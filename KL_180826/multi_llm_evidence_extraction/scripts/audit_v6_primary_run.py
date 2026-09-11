"""Create a read-only retrospective attestation for a locked V6 primary run.

This script never writes into the run it examines.  It records the current hashes,
checks the locked summary against the inference record, and emits explicit claim
states in a separate audit directory.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_v6_primary_panel import SPEC_PATH, load_v6_spec
from common import STUDY_DIR, sha256_file, validate_safe_identifier
from v6_artifacts import (
    DEFAULT_FROZEN_V6_RUN_IDS,
    V6ArtifactError,
    artifact_ledger,
    atomic_write_json,
    primary_claims,
)


def _run_directory(run_id: str) -> Path:
    return (STUDY_DIR / "outputs" / "v6_primary" / run_id).resolve()


def _report_directory(run_id: str) -> Path:
    return (STUDY_DIR / "reports" / "v6_primary" / run_id).resolve()


def _audit_directory(run_id: str) -> Path:
    return (STUDY_DIR / "audits" / run_id).resolve()


def _summary_primary(summary: dict[str, Any], hypothesis: str) -> dict[str, Any]:
    matches = [item for item in summary.get("primary", []) if isinstance(item, dict) and item.get("hypothesis") == hypothesis]
    if len(matches) != 1:
        raise V6ArtifactError(f"locked V6 summary must contain exactly one primary {hypothesis} record")
    return matches[0]


def audit_locked_v6_run(
    run_id: str,
    *,
    workspace_root: Path | None = None,
    audit_dir: Path | None = None,
) -> dict[str, Any]:
    """Attest a frozen V6 run without mutating the run or report directory."""
    spec = load_v6_spec()
    safe = validate_safe_identifier(run_id, "run_id")
    frozen = set(DEFAULT_FROZEN_V6_RUN_IDS) | set(spec.get("frozen_v6_run_ids", []))
    if safe not in frozen:
        raise V6ArtifactError(f"retrospective audit accepts frozen V6 runs only: {safe}")

    workspace = (workspace_root or STUDY_DIR.parents[1]).resolve()
    run_dir = _run_directory(safe)
    report_dir = _report_directory(safe)
    if not run_dir.is_dir():
        raise FileNotFoundError(run_dir)
    if not report_dir.is_dir():
        raise FileNotFoundError(report_dir)

    destination = (audit_dir or _audit_directory(safe)).resolve()
    audit_root = (STUDY_DIR / "audits" / safe).resolve()
    if audit_dir is None:
        destination = audit_root
    try:
        destination.relative_to(audit_root.parent)
    except ValueError as exc:
        raise V6ArtifactError("V6 audit destination must be contained in the run-scoped audits root") from exc
    if destination != audit_root:
        raise V6ArtifactError("V6 audit destination must equal audits/<frozen-run-id>")
    if destination == run_dir or destination == report_dir or run_dir in destination.parents or report_dir in destination.parents:
        raise V6ArtifactError("V6 audit destination must be outside locked output/report directories")
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"V6 retrospective audit directory is immutable/nonempty: {destination}")

    summary_path = run_dir / "v6_run_summary.json"
    inference_path = run_dir / "v6_inference.csv"
    build_summary_path = run_dir / "v6_build_summary.json"
    for required in (summary_path, inference_path, build_summary_path):
        if not required.is_file():
            raise FileNotFoundError(required)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    build_summary = json.loads(build_summary_path.read_text(encoding="utf-8"))
    inference = pd.read_csv(inference_path, encoding="utf-8-sig")

    protocol_hash_matches = summary.get("protocol_sha256") == sha256_file(SPEC_PATH)
    build_protocol_hash_matches = build_summary.get("protocol_sha256") == sha256_file(SPEC_PATH)
    expected_count = int(summary.get("n_predictions", -1))
    prediction_path = run_dir / "v6_predictions.csv"
    prediction_count_matches = prediction_path.is_file() and len(pd.read_csv(prediction_path, encoding="utf-8-sig")) == expected_count
    summary_reconciliation: dict[str, bool] = {}
    for hypothesis in ("H1", "H2"):
        row = inference[
            inference["hypothesis"].eq(hypothesis)
            & inference["role"].eq("primary")
            & inference["model"].eq(spec["primary"]["model"])
            & inference["metric"].eq(spec["primary"]["metric"])
        ]
        if len(row) != 1:
            raise V6ArtifactError(f"locked V6 inference must contain exactly one primary record for {hypothesis}")
        summary_row = _summary_primary(summary, hypothesis)
        record = row.iloc[0].to_dict()
        keys = ("status", "improvement_delta", "bootstrap_ci_low", "bootstrap_ci_high", "p_value", "p_value_bh", "n_paired_dates", "n_folds")
        equal = True
        for key in keys:
            left, right = summary_row.get(key), record.get(key)
            if isinstance(left, (int, float)) or isinstance(right, (int, float)):
                try:
                    equal = equal and abs(float(left) - float(right)) < 1e-12
                except (TypeError, ValueError):
                    equal = False
            else:
                equal = equal and left == right
        summary_reconciliation[hypothesis] = bool(equal)

    audit_pass = protocol_hash_matches and build_protocol_hash_matches and prediction_count_matches and all(summary_reconciliation.values())
    claims = primary_claims(
        inference.to_dict("records"),
        spec,
        audit_pass=audit_pass,
        manifest_pass=False,
    )
    destination.mkdir(parents=True, exist_ok=False)
    artifacts = [*sorted(path for path in run_dir.iterdir() if path.is_file()), *sorted(path for path in report_dir.iterdir() if path.is_file())]
    payload = {
        "artifact_schema_version": "v6_retrospective_attestation_v1",
        "status": "completed",
        "audited_run_id": safe,
        "immutable_source": True,
        "source_run_directory": run_dir.relative_to(workspace).as_posix(),
        "source_report_directory": report_dir.relative_to(workspace).as_posix(),
        "protocol": {
            "path": SPEC_PATH.relative_to(workspace).as_posix(),
            "sha256": sha256_file(SPEC_PATH),
            "summary_hash_matches_current_protocol": protocol_hash_matches,
            "build_summary_hash_matches_current_protocol": build_protocol_hash_matches,
        },
        "reconciliation": {
            "prediction_count_matches": bool(prediction_count_matches),
            "summary_primary_matches_inference": summary_reconciliation,
            "audit_pass": bool(audit_pass),
            "manifest_validation": "not_available_for_historical_locked_run",
        },
        "claims": claims,
        "locked_artifacts": artifact_ledger(workspace, artifacts),
        "limitations": [
            "retrospective_attestation_does_not_rewrite_locked_artifacts",
            "historical_locked_run_has_no_fail_closed_runtime_input_manifest",
            "historical_claim_state_requires_manifest_validation_for_supported_status",
        ],
    }
    manifest_path = destination / "v6_retrospective_attestation.json"
    atomic_write_json(manifest_path, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a separate read-only attestation for a frozen V6 run.")
    parser.add_argument("--run-id", default="v6_primary_20260909")
    parser.add_argument("--audit-dir", type=Path, default=None)
    args = parser.parse_args()
    result = audit_locked_v6_run(args.run_id, audit_dir=args.audit_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
