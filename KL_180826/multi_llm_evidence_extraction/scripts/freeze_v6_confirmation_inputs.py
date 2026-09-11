"""Freeze workspace-local inputs before a V6 H2 confirmation analysis.

The confirmation runner consumes only this immutable hash manifest, never arbitrary
prediction/panel paths. A reader obtains verified bytes from this module, ensuring
analysis parses the exact bytes whose digests appear in its frozen provenance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import sha256_file, utc_now, validate_safe_identifier
from v6_artifacts import V6ArtifactError, atomic_write_json, portable_path, resolve_workspace_path

INPUT_MANIFEST_SCHEMA_VERSION = "v6_confirmation_input_manifest_v1"
REQUIRED_ANALYSIS_ARTIFACTS = ("predictions", "panel", "robustness")
REQUIRED_PREFLIGHT_SOURCE_PATHS = frozenset(
    {
        "KL_180826/data/prices/all_vn30_prices.csv",
        "KL_180826/data/prices_extended/VNINDEX.csv",
        "KL_180826/data/news/matched/all_news_matched.csv",
        "KL_180826/data/news/processed/all_news_processed.csv",
    }
)


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _read_json_bytes(content: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise V6ArtifactError(f"invalid {label}") from exc
    if not isinstance(value, dict):
        raise V6ArtifactError(f"{label} must be a JSON object")
    return value


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        return _read_json_bytes(path.read_bytes(), label)
    except OSError as exc:
        raise V6ArtifactError(f"cannot read {label}: {path}") from exc


def _read_verified_bytes(
    workspace: Path,
    relative_path: str,
    expected_sha256: str,
    field: str,
) -> tuple[Path, bytes]:
    """Read once and verify the digest of exactly the bytes returned."""
    path = resolve_workspace_path(workspace, relative_path, field=field)
    try:
        content = path.read_bytes()
    except OSError as exc:
        raise V6ArtifactError(f"cannot read {field}: {path}") from exc
    if _sha256_bytes(content) != expected_sha256:
        raise V6ArtifactError(f"{field} hash mismatch: {relative_path}")
    return path, content


def _preflight_path(workspace: Path) -> Path:
    return resolve_workspace_path(workspace, "preflight/v6_confirmation_preflight.json", field="confirmation preflight")


def _protocol_path(workspace: Path) -> Path:
    return resolve_workspace_path(
        workspace,
        "KL_180826/multi_llm_evidence_extraction/config/v6_h2_confirmation_20260602_20260810_v1.json",
        field="confirmation protocol",
    )


def _validate_preflight_sources(workspace: Path, preflight: dict[str, Any]) -> list[dict[str, str]]:
    if preflight.get("status") != "ready":
        raise V6ArtifactError("confirmation preflight is not ready")
    entries = preflight.get("input_hashes")
    if not isinstance(entries, list) or not entries:
        raise V6ArtifactError("confirmation preflight has no frozen source hashes")
    paths: set[str] = set()
    result: list[dict[str, str]] = []
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not isinstance(entry.get("sha256"), str):
            raise V6ArtifactError("confirmation preflight source entry is invalid")
        path = resolve_workspace_path(workspace, entry["path"], field="preflight source")
        portable = portable_path(workspace, path)
        if portable in paths:
            raise V6ArtifactError("confirmation preflight source hash entries must be unique")
        if sha256_file(path) != entry["sha256"]:
            raise V6ArtifactError(f"confirmation preflight source hash mismatch: {entry['path']}")
        paths.add(portable)
        result.append({"path": portable, "sha256": entry["sha256"]})
    if paths != REQUIRED_PREFLIGHT_SOURCE_PATHS:
        raise V6ArtifactError("confirmation preflight source hash membership is incomplete or unexpected")
    return result


def _analysis_artifact(workspace: Path, name: str, relative_path: str) -> dict[str, str]:
    path = resolve_workspace_path(workspace, relative_path, field=f"confirmation {name}")
    return {"name": name, "path": portable_path(workspace, path), "sha256": sha256_file(path)}


def _default_manifest_path(workspace: Path, input_set_id: str) -> Path:
    return resolve_workspace_path(
        workspace,
        f"KL_180826/multi_llm_evidence_extraction/outputs/v6_h2_confirmation_inputs/{input_set_id}/v6_confirmation_input_manifest.json",
        field="confirmation input manifest",
        require_file=False,
    )


def _annotation_consensus_from_file(workspace: Path, relative_path: str) -> dict[str, Any]:
    """Bind a root-contained completed strict A/B/C consensus provenance file."""
    path = resolve_workspace_path(workspace, relative_path, field="annotation consensus provenance")
    content = path.read_bytes()
    payload = _read_json_bytes(content, "annotation consensus provenance")
    if payload.get("artifact_schema_version") != "v6_confirmation_annotation_consensus_v1":
        raise V6ArtifactError("confirmation annotation consensus has an unexpected schema version")
    if payload.get("annotators") != ["a", "b", "c"]:
        raise V6ArtifactError("confirmation annotation consensus must declare annotators A/B/C")
    if payload.get("strict_expansion") is not True or payload.get("status") != "completed":
        raise V6ArtifactError("confirmation annotation consensus must be completed strict expansion")
    expected_sample = payload.get("expected_sample")
    inputs = payload.get("inputs")
    consensus_csv = payload.get("consensus_csv")
    if not isinstance(expected_sample, dict) or not isinstance(inputs, list) or not isinstance(consensus_csv, dict):
        raise V6ArtifactError("confirmation annotation consensus lacks strict-expansion provenance")
    if len(inputs) != 3:
        raise V6ArtifactError("confirmation annotation consensus must bind exactly three annotator inputs")
    verified_paths: set[str] = set()
    for label, entry in [("expected sample", expected_sample), ("consensus CSV", consensus_csv), *[("annotator input", item) for item in inputs]]:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not isinstance(entry.get("sha256"), str):
            raise V6ArtifactError(f"confirmation annotation consensus has invalid {label} provenance")
        referenced = resolve_workspace_path(workspace, entry["path"], field=f"annotation consensus {label}")
        if sha256_file(referenced) != entry["sha256"]:
            raise V6ArtifactError(f"confirmation annotation consensus {label} hash mismatch")
        if label == "annotator input":
            portable = portable_path(workspace, referenced)
            if portable in verified_paths:
                raise V6ArtifactError("confirmation annotation consensus annotator inputs must be unique")
            verified_paths.add(portable)
    return {
        "path": portable_path(workspace, path),
        "sha256": _sha256_bytes(content),
        "status": "completed",
        "strict_expansion": True,
        "annotators": ["a", "b", "c"],
    }


def _verify_annotation_consensus_snapshot(workspace: Path, value: Any, required: bool) -> dict[str, Any] | None:
    if value is None:
        if required:
            raise V6ArtifactError("frozen confirmation inputs lack three-annotator consensus provenance")
        return None
    if not isinstance(value, dict):
        raise V6ArtifactError("frozen annotation consensus provenance is invalid")
    if value.get("annotators") != ["a", "b", "c"]:
        raise V6ArtifactError("frozen confirmation annotation consensus does not contain A/B/C")
    if value.get("strict_expansion") is not True or value.get("status") != "completed":
        raise V6ArtifactError("frozen confirmation annotation consensus is not completed strict expansion")
    path, content = _read_verified_bytes(
        workspace,
        str(value.get("path", "")),
        str(value.get("sha256", "")),
        "frozen annotation consensus provenance",
    )
    _annotation_consensus_from_file(workspace, portable_path(workspace, path))
    return {"path": portable_path(workspace, path), "sha256": _sha256_bytes(content), "bytes": content}


def freeze_confirmation_inputs(
    workspace: Path,
    input_set_id: str,
    *,
    predictions_relative: str,
    panel_relative: str,
    robustness_relative: str,
    annotation_consensus_relative: str,
) -> dict[str, Any]:
    """Write exactly one immutable manifest for a confirmation input set."""
    root = workspace.resolve()
    safe_id = validate_safe_identifier(input_set_id, "input_set_id")
    preflight_path = _preflight_path(root)
    preflight = _read_json(preflight_path, "confirmation preflight")
    protocol_path = _protocol_path(root)
    protocol = _read_json(protocol_path, "confirmation protocol")
    preflight_protocol = preflight.get("protocol")
    if not isinstance(preflight_protocol, dict) or preflight_protocol.get("sha256") != sha256_file(protocol_path):
        raise V6ArtifactError("confirmation preflight protocol hash does not match the frozen protocol")
    preflight_sources = _validate_preflight_sources(root, preflight)
    annotation = _annotation_consensus_from_file(root, annotation_consensus_relative)
    artifacts = [
        _analysis_artifact(root, "predictions", predictions_relative),
        _analysis_artifact(root, "panel", panel_relative),
        _analysis_artifact(root, "robustness", robustness_relative),
    ]
    manifest_path = _default_manifest_path(root, safe_id)
    if manifest_path.exists():
        raise FileExistsError(f"confirmation input manifest already exists: {manifest_path}")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "artifact_schema_version": INPUT_MANIFEST_SCHEMA_VERSION,
        "status": "frozen",
        "generated_at_utc": utc_now(),
        "input_set_id": safe_id,
        "preflight": {
            "path": portable_path(root, preflight_path),
            "sha256": sha256_file(preflight_path),
            "source_inputs": preflight_sources,
        },
        "protocol": {
            "path": portable_path(root, protocol_path),
            "sha256": sha256_file(protocol_path),
            "protocol_id": protocol.get("protocol_id"),
        },
        "annotation_consensus": annotation,
        "analysis_artifacts": artifacts,
    }
    atomic_write_json(manifest_path, payload)
    return payload


def load_frozen_confirmation_snapshot(workspace: Path, relative_path: str) -> dict[str, Any]:
    """Return immutable verified bytes for every input used by confirmation.

    Callers must parse these bytes directly rather than reopening live paths after
    validation, preventing a replace-after-check race from changing the analysis.
    """
    root = workspace.resolve()
    manifest_path = resolve_workspace_path(root, relative_path, field="confirmation input manifest")
    manifest_bytes = manifest_path.read_bytes()
    manifest = _read_json_bytes(manifest_bytes, "confirmation input manifest")
    if manifest.get("artifact_schema_version") != INPUT_MANIFEST_SCHEMA_VERSION or manifest.get("status") != "frozen":
        raise V6ArtifactError("confirmation input manifest is not frozen")
    protocol_entry = manifest.get("protocol")
    preflight_entry = manifest.get("preflight")
    artifact_entries = manifest.get("analysis_artifacts")
    if not isinstance(protocol_entry, dict) or not isinstance(preflight_entry, dict) or not isinstance(artifact_entries, list):
        raise V6ArtifactError("confirmation input manifest has invalid required sections")

    protocol_path, protocol_bytes = _read_verified_bytes(
        root, str(protocol_entry.get("path", "")), str(protocol_entry.get("sha256", "")), "frozen confirmation protocol"
    )
    if portable_path(root, protocol_path) != portable_path(root, _protocol_path(root)):
        raise V6ArtifactError("frozen confirmation protocol path is not canonical")
    protocol = _read_json_bytes(protocol_bytes, "frozen confirmation protocol")
    if protocol.get("protocol_id") != protocol_entry.get("protocol_id"):
        raise V6ArtifactError("frozen confirmation protocol ID does not match its manifest entry")
    preflight_path, preflight_bytes = _read_verified_bytes(
        root, str(preflight_entry.get("path", "")), str(preflight_entry.get("sha256", "")), "frozen confirmation preflight"
    )
    preflight = _read_json_bytes(preflight_bytes, "frozen confirmation preflight")
    if preflight.get("status") != "ready":
        raise V6ArtifactError("frozen confirmation preflight is not ready")
    preflight_protocol = preflight.get("protocol")
    if not isinstance(preflight_protocol, dict) or preflight_protocol.get("sha256") != _sha256_bytes(protocol_bytes):
        raise V6ArtifactError("frozen confirmation preflight does not bind the verified protocol")

    source_entries = preflight_entry.get("source_inputs")
    if not isinstance(source_entries, list) or not source_entries:
        raise V6ArtifactError("frozen confirmation input manifest has no source inputs")
    source_paths: set[str] = set()
    sources: list[dict[str, Any]] = []
    for entry in source_entries:
        if not isinstance(entry, dict):
            raise V6ArtifactError("frozen confirmation source input is invalid")
        path, content = _read_verified_bytes(
            root, str(entry.get("path", "")), str(entry.get("sha256", "")), "frozen confirmation source input"
        )
        portable = portable_path(root, path)
        source_paths.add(portable)
        sources.append({"path": portable, "sha256": _sha256_bytes(content), "bytes": content})
    if source_paths != REQUIRED_PREFLIGHT_SOURCE_PATHS:
        raise V6ArtifactError("frozen confirmation source membership is incomplete or unexpected")
    preflight_hashes = preflight.get("input_hashes")
    if not isinstance(preflight_hashes, list):
        raise V6ArtifactError("frozen confirmation preflight has invalid source hashes")
    preflight_map: dict[str, str] = {}
    for entry in preflight_hashes:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not isinstance(entry.get("sha256"), str):
            raise V6ArtifactError("frozen confirmation preflight source hash entry is invalid")
        if entry["path"] in preflight_map:
            raise V6ArtifactError("frozen confirmation preflight source hash entries must be unique")
        preflight_map[entry["path"]] = entry["sha256"]
    source_map = {item["path"]: item["sha256"] for item in sources}
    if preflight_map != source_map:
        raise V6ArtifactError("frozen confirmation source hashes do not match the verified preflight")

    annotation = _verify_annotation_consensus_snapshot(
        root,
        manifest.get("annotation_consensus"),
        required=bool(protocol.get("gates", {}).get("require_three_annotator_consensus", False)),
    )

    artifacts: dict[str, dict[str, Any]] = {}
    for entry in artifact_entries:
        if not isinstance(entry, dict):
            raise V6ArtifactError("frozen confirmation analysis artifact is invalid")
        name = str(entry.get("name", ""))
        if name not in REQUIRED_ANALYSIS_ARTIFACTS or name in artifacts:
            raise V6ArtifactError("frozen confirmation analysis artifact membership is invalid")
        path, content = _read_verified_bytes(
            root, str(entry.get("path", "")), str(entry.get("sha256", "")), f"frozen {name}"
        )
        artifacts[name] = {"path": portable_path(root, path), "sha256": _sha256_bytes(content), "bytes": content}
    if set(artifacts) != set(REQUIRED_ANALYSIS_ARTIFACTS):
        raise V6ArtifactError("frozen confirmation analysis artifact membership is incomplete")

    return {
        "manifest": manifest,
        "manifest_path": portable_path(root, manifest_path),
        "manifest_sha256": _sha256_bytes(manifest_bytes),
        "protocol": {"path": portable_path(root, protocol_path), "sha256": _sha256_bytes(protocol_bytes), "bytes": protocol_bytes, "payload": protocol},
        "preflight": {"path": portable_path(root, preflight_path), "sha256": _sha256_bytes(preflight_bytes), "bytes": preflight_bytes, "payload": preflight},
        "sources": sources,
        "annotation_consensus": annotation,
        "analysis_artifacts": artifacts,
    }


def load_frozen_confirmation_inputs(workspace: Path, relative_path: str) -> tuple[dict[str, Any], Path]:
    """Backward-compatible validator returning the manifest/path only."""
    snapshot = load_frozen_confirmation_snapshot(workspace, relative_path)
    return snapshot["manifest"], resolve_workspace_path(workspace.resolve(), snapshot["manifest_path"], field="confirmation input manifest")


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze workspace-local V6 H2 confirmation inputs.")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--input-set-id", required=True)
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--panel", required=True)
    parser.add_argument("--robustness", required=True)
    parser.add_argument("--annotation-consensus", required=True, help="root-contained strict A/B/C consensus provenance JSON")
    args = parser.parse_args()
    result = freeze_confirmation_inputs(
        args.workspace,
        args.input_set_id,
        predictions_relative=args.predictions,
        panel_relative=args.panel,
        robustness_relative=args.robustness,
        annotation_consensus_relative=args.annotation_consensus,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
