"""Run a frozen V6 H2 confirmation from one immutable input manifest only."""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import sha256_file, utc_now
from freeze_v6_confirmation_inputs import load_frozen_confirmation_snapshot
from v6_artifacts import V6ArtifactError, atomic_write_json, portable_path, validate_safe_identifier
from v6_subgroup_analysis import (
    analyze_materiality_interaction,
    build_prior_materiality_exposure,
    frozen_t20_exit_dates,
    validate_confirmation_prediction_targets,
)


REQUIRED_PREFLIGHT_SOURCE_PATHS = frozenset(
    {
        "KL_180826/data/prices/all_vn30_prices.csv",
        "KL_180826/data/prices_extended/VNINDEX.csv",
        "KL_180826/data/news/matched/all_news_matched.csv",
        "KL_180826/data/news/processed/all_news_processed.csv",
    }
)
ROBUSTNESS_SCHEMA_VERSION = "v6_h2_confirmation_robustness_v1"


def _read_json_bytes(content: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise V6ArtifactError(f"invalid {label}") from exc
    if not isinstance(value, dict):
        raise V6ArtifactError(f"{label} must be a JSON object")
    return value


def _validate_panel_status(panel: pd.DataFrame) -> None:
    if "semantic_source_status" not in panel:
        raise V6ArtifactError("frozen confirmation panel lacks semantic_source_status")
    permitted = {"valid_source_event", "no_valid_news"}
    invalid = ~panel["semantic_source_status"].astype(str).isin(permitted)
    if invalid.any():
        counts = panel.loc[invalid, "semantic_source_status"].astype(str).value_counts().to_dict()
        raise V6ArtifactError(f"frozen confirmation panel has unresolved source statuses: {counts}")


def _robustness_alignment(value: dict[str, Any], protocol: dict[str, Any]) -> bool:
    """Accept only a separately declared robustness result with this exact contract."""
    required = {
        "artifact_schema_version",
        "status",
        "protocol_id",
        "confirmation_oos",
        "comparison",
        "exposure",
        "metric",
        "inference",
        "correction_family",
        "improvement_delta",
        "bootstrap_ci_low",
        "p_value_bh",
    }
    if not required.issubset(value):
        return False
    try:
        return (
            value["artifact_schema_version"] == ROBUSTNESS_SCHEMA_VERSION
            and value["status"] == "ok"
            and value["protocol_id"] == protocol.get("protocol_id")
            and value["confirmation_oos"] == protocol.get("confirmation_oos")
            and value["comparison"] == protocol.get("comparison")
            and value["exposure"] == protocol.get("exposure")
            and value["metric"] == protocol.get("estimand", {}).get("metric")
            and value["inference"] == protocol.get("inference")
            and value["correction_family"] == protocol.get("inference", {}).get("correction_family")
            and float(value["improvement_delta"]) > 0
            and float(value["bootstrap_ci_low"]) > 0
            and float(value["p_value_bh"]) <= float(protocol.get("inference", {}).get("alpha", 0.05))
        )
    except (TypeError, ValueError):
        return False


def _verified_preflight_source_bytes(snapshot: dict[str, Any]) -> dict[str, bytes]:
    """Bind runner inputs to the exact sources that were covered by preflight."""
    preflight = snapshot["preflight"]["payload"]
    protocol = snapshot["protocol"]
    declared_protocol = preflight.get("protocol")
    if not isinstance(declared_protocol, dict) or declared_protocol.get("sha256") != protocol["sha256"]:
        raise V6ArtifactError("frozen confirmation preflight does not bind the verified protocol")
    entries = preflight.get("input_hashes")
    if not isinstance(entries, list):
        raise V6ArtifactError("frozen confirmation preflight has invalid source hashes")
    preflight_sources: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not isinstance(entry.get("sha256"), str):
            raise V6ArtifactError("frozen confirmation preflight source hash entry is invalid")
        path = str(entry["path"])
        if path in preflight_sources:
            raise V6ArtifactError("frozen confirmation preflight source hash entries must be unique")
        preflight_sources[path] = str(entry["sha256"])
    source_bytes = {source["path"]: source["bytes"] for source in snapshot["sources"]}
    if set(preflight_sources) != REQUIRED_PREFLIGHT_SOURCE_PATHS or set(source_bytes) != REQUIRED_PREFLIGHT_SOURCE_PATHS:
        raise V6ArtifactError("frozen confirmation preflight source membership is incomplete or unexpected")
    import hashlib

    for path, content in source_bytes.items():
        if hashlib.sha256(content).hexdigest() != preflight_sources[path]:
            raise V6ArtifactError(f"frozen confirmation source differs from verified preflight: {path}")
    return source_bytes


def _relative_result_path(workspace: Path, value: str) -> Path:
    path = (workspace / value).resolve()
    try:
        path.relative_to(workspace)
    except ValueError as exc:
        raise V6ArtifactError("frozen result path escapes confirmation workspace") from exc
    return path


def run_confirmation(workspace: Path, run_id: str, *, input_manifest_relative: str) -> dict[str, Any]:
    root = workspace.resolve()
    safe_run = validate_safe_identifier(run_id, "run_id")
    output_root = root / "KL_180826" / "multi_llm_evidence_extraction" / "outputs" / "v6_h2_confirmation" / safe_run
    report_root = root / "KL_180826" / "multi_llm_evidence_extraction" / "reports" / "v6_h2_confirmation" / safe_run
    if output_root.exists() or report_root.exists():
        raise FileExistsError("confirmation run ID already has an immutable output or report directory")
    output_root.mkdir(parents=True)
    report_root.mkdir(parents=True)
    preflight_status = "not_checked"
    try:
        snapshot = load_frozen_confirmation_snapshot(root, input_manifest_relative)
        protocol = snapshot["protocol"]["payload"]
        preflight_status = str(snapshot["preflight"]["payload"].get("status", "not_checked"))
        if preflight_status != "ready":
            raise V6ArtifactError("frozen confirmation preflight is not ready")
        source_bytes = _verified_preflight_source_bytes(snapshot)
        predictions_entry = snapshot["analysis_artifacts"]["predictions"]
        panel_entry = snapshot["analysis_artifacts"]["panel"]
        robustness_entry = snapshot["analysis_artifacts"]["robustness"]
        predictions = pd.read_csv(io.BytesIO(predictions_entry["bytes"]), encoding="utf-8-sig")
        panel = pd.read_csv(io.BytesIO(panel_entry["bytes"]), encoding="utf-8-sig")
        _validate_panel_status(panel)
        robustness = _read_json_bytes(robustness_entry["bytes"], "frozen confirmation robustness")
        prices = pd.read_csv(io.BytesIO(source_bytes["KL_180826/data/prices/all_vn30_prices.csv"]), encoding="utf-8-sig")
        benchmark = pd.read_csv(io.BytesIO(source_bytes["KL_180826/data/prices_extended/VNINDEX.csv"]), encoding="utf-8-sig")
        validate_confirmation_prediction_targets(predictions, prices, benchmark, protocol)
        target_exit_dates = frozen_t20_exit_dates(prices, benchmark, protocol)
        exposure = build_prior_materiality_exposure(panel)
        exposure_path = output_root / "v6_confirmation_exposure.csv"
        exposure.to_csv(exposure_path, index=False, encoding="utf-8-sig")
        interaction, result = analyze_materiality_interaction(
            predictions,
            exposure,
            protocol,
            robustness_aligned=_robustness_alignment(robustness, protocol),
            target_exit_dates=target_exit_dates,
        )
        interaction_path = output_root / "v6_confirmation_interaction_dates.csv"
        interaction.to_csv(interaction_path, index=False, encoding="utf-8-sig")
        result.update(
            {
                "run_id": safe_run,
                "frozen_input_manifest": {
                    "path": snapshot["manifest_path"],
                    "sha256": snapshot["manifest_sha256"],
                },
                "preflight_sha256": snapshot["preflight"]["sha256"],
                "inputs": [
                    {"name": "predictions", "path": predictions_entry["path"], "sha256": predictions_entry["sha256"]},
                    {"name": "panel", "path": panel_entry["path"], "sha256": panel_entry["sha256"]},
                    {"name": "robustness", "path": robustness_entry["path"], "sha256": robustness_entry["sha256"]},
                    {"name": "protocol", "path": snapshot["protocol"]["path"], "sha256": snapshot["protocol"]["sha256"]},
                ],
                "outputs": [
                    {"name": "exposure", "path": _relative_result_path(root, exposure_path.relative_to(root).as_posix()).relative_to(root).as_posix(), "sha256": sha256_file(exposure_path)},
                    {"name": "interaction", "path": _relative_result_path(root, interaction_path.relative_to(root).as_posix()).relative_to(root).as_posix(), "sha256": sha256_file(interaction_path)},
                ],
                "generated_at_utc": utc_now(),
            }
        )
        result_path = output_root / "v6_h2_confirmation_result.json"
        atomic_write_json(result_path, result)
        report = [
            "# V6 H2 materiality confirmation",
            "",
            f"- Run: `{safe_run}`",
            f"- State: `{result['state']}`",
            f"- Status: `{result['status']}`",
            f"- Interaction: `{result['improvement_delta']}`",
            f"- CI: `[{result['bootstrap_ci_low']}, {result['bootstrap_ci_high']}]`",
            f"- BH p: `{result['p_value_bh']}`",
            "",
            "This result does not replace the locked all-observation V6 primary H2 conclusion.",
        ]
        (report_root / "v6_h2_confirmation_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
        return result
    except Exception as exc:
        atomic_write_json(
            output_root / "v6_h2_confirmation_failure.json",
            {
                "artifact_schema_version": "v6_h2_confirmation_failure_v1",
                "status": "blocked",
                "run_id": safe_run,
                "generated_at_utc": utc_now(),
                "error_type": type(exc).__name__,
                "error": str(exc)[:1000],
                "preflight_status": preflight_status,
            },
        )
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V6 H2 confirmation from one frozen workspace input manifest.")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--input-manifest", required=True)
    args = parser.parse_args()
    result = run_confirmation(args.workspace, args.run_id, input_manifest_relative=args.input_manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["state"] in {"confirmed", "unsupported", "not_estimable"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
