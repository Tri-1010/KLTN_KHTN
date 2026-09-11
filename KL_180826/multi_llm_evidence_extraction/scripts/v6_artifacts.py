"""Fail-closed artifact, provenance, and claim-gate helpers for V6 runs.

The helpers in this module deliberately keep the prospective V6 lane separate from
frozen historical artifacts.  A completed V6 release is immutable; retrospective
checks write a sibling attestation and never modify the historical run directory.
"""

from __future__ import annotations

import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from common import sha256_file, utc_now, validate_safe_identifier


INTENT_MANIFEST = "v6_intent_manifest.json"
BUILD_MANIFEST = "v6_build_manifest.json"
RUN_MANIFEST = "v6_run_manifest.json"
RELEASE_MANIFEST = "v6_release_manifest.json"
TARGET_MANIFEST = "v6_target_manifest.json"
V6_MANIFEST_NAMES = (INTENT_MANIFEST, BUILD_MANIFEST, RUN_MANIFEST, RELEASE_MANIFEST)
DEFAULT_FROZEN_V6_RUN_IDS = frozenset({"v6_primary_20260909"})
_DRIVE_PATH = re.compile(r"^[A-Za-z]:")


class V6ArtifactError(ValueError):
    """Raised when a V6 source, manifest, or claim contract is invalid."""


class V6RunImmutableError(FileExistsError):
    """Raised when a V6 run directory is already reserved or completed."""


def canonical_json(value: Any) -> str:
    """Return a stable UTF-8-safe JSON representation for digests/manifests."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Write a JSON artifact atomically, avoiding partially published manifests."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, default=str))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_json_object(path: Path, label: str = "manifest") -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise V6ArtifactError(f"invalid V6 {label}: {path}") from exc
    if not isinstance(value, dict):
        raise V6ArtifactError(f"V6 {label} must be a JSON object: {path}")
    return value


def strict_relative_path(value: str | Path, field: str = "path") -> str:
    """Validate a portable path relative to a declared workspace root."""
    text = str(value).strip().replace("\\", "/")
    if not text or text in {".", ".."}:
        raise V6ArtifactError(f"V6 {field} must be a nonempty relative path")
    if text.startswith("/") or text.startswith("//") or _DRIVE_PATH.match(text):
        raise V6ArtifactError(f"V6 {field} must be relative to workspace root: {value!r}")
    parts = PurePosixPath(text).parts
    if any(part in {"", ".", ".."} for part in parts):
        raise V6ArtifactError(f"V6 {field} escapes workspace root: {value!r}")
    return PurePosixPath(*parts).as_posix()


def resolve_workspace_path(
    workspace_root: Path,
    relative_path: str | Path,
    *,
    field: str = "path",
    require_file: bool = True,
) -> Path:
    """Resolve one input below the explicit workspace root or fail closed."""
    root = Path(workspace_root).resolve()
    relative = strict_relative_path(relative_path, field)
    candidate = (root / PurePosixPath(relative)).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise V6ArtifactError(f"V6 {field} escapes workspace root: {relative_path!r}") from exc
    if require_file and not candidate.is_file():
        raise FileNotFoundError(f"V6 {field} is missing: {candidate}")
    return candidate


def portable_path(workspace_root: Path, path: Path) -> str:
    root = Path(workspace_root).resolve()
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise V6ArtifactError(f"V6 artifact path escapes workspace root: {resolved}") from exc


def frozen_v6_run_ids(spec: Mapping[str, Any]) -> set[str]:
    """Return runtime-protected IDs without mutating the locked protocol bytes."""
    declared = spec.get("frozen_v6_run_ids", [])
    if declared is None:
        declared = []
    if not isinstance(declared, list) or not all(isinstance(item, str) for item in declared):
        raise V6ArtifactError("frozen_v6_run_ids must be a list of run identifiers when present")
    return set(DEFAULT_FROZEN_V6_RUN_IDS) | set(declared)


def _run_has_any_content(directory: Path) -> bool:
    """Return whether a directory has artifacts without following a missing path."""
    return directory.is_dir() and any(directory.iterdir())


def _expected_output_paths(workspace_root: Path, run_id: str) -> tuple[Path, Path]:
    root = Path(workspace_root).resolve()
    study = root / "KL_180826" / "multi_llm_evidence_extraction"
    return study / "outputs" / "v6_primary" / run_id, study / "reports" / "v6_primary" / run_id


def _assert_v6_run_destination(workspace_root: Path, output_dir: Path, report_dir: Path, run_id: str) -> None:
    expected_output, expected_report = _expected_output_paths(workspace_root, run_id)
    if Path(output_dir).resolve() != expected_output.resolve() or Path(report_dir).resolve() != expected_report.resolve():
        raise V6ArtifactError("V6 output/report directories must equal the run-scoped workspace paths")


def prepare_v6_run(
    run_id: str,
    spec: Mapping[str, Any],
    output_dir: Path,
    report_dir: Path,
    workspace_root: Path,
    input_ledger: Mapping[str, Any],
    *,
    protocol_path: Path,
    horizon: int,
    row_filter: str = "primary",
    sensitivity_tag: str | None = None,
) -> Path:
    """Atomically reserve a fresh V6 run and write its intent manifest.

    No output directory is created until all destination, protocol, and input
    constraints have been validated by the caller.  If report directory creation
    fails, the empty output directory is removed to avoid a half-reserved run.
    """
    safe = assert_new_v6_run_available(run_id, spec, output_dir, report_dir)
    _assert_v6_run_destination(workspace_root, output_dir, report_dir, safe)
    root = Path(workspace_root).resolve()
    output, report = Path(output_dir).resolve(), Path(report_dir).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir(exist_ok=False)
    try:
        report.mkdir(exist_ok=False)
        payload = {
            "artifact_schema_version": "v6_intent_manifest_v1",
            "status": "prepared",
            "generated_at_utc": utc_now(),
            "run_id": safe,
            "protocol_version": spec.get("protocol_version"),
            "protocol_path": portable_path(root, protocol_path),
            "protocol_sha256": sha256_file(protocol_path),
            "workspace_root": ".",
            "output_dir": portable_path(root, output),
            "report_dir": portable_path(root, report),
            "horizon_benchmark_sessions": int(horizon),
            "row_filter": row_filter,
            "sensitivity_tag": sensitivity_tag,
            "inputs": dict(input_ledger),
        }
        return write_manifest_once(output, INTENT_MANIFEST, payload)
    except Exception:
        import shutil
        if output.is_dir():
            shutil.rmtree(output)
        if report.is_dir():
            shutil.rmtree(report)
        raise


def ensure_v6_run_reserved(
    run_id: str,
    spec: Mapping[str, Any],
    output_dir: Path,
    report_dir: Path,
    workspace_root: Path,
    input_ledger: Mapping[str, Any],
    *,
    protocol_path: Path,
    horizon: int,
    row_filter: str = "primary",
    sensitivity_tag: str | None = None,
) -> Path:
    """Return an existing matching intent or reserve a new clean V6 run."""
    intent_path = _manifest_path(output_dir, INTENT_MANIFEST)
    if intent_path.is_file():
        intent = load_json_object(intent_path, "intent manifest")
        if intent.get("run_id") != run_id or intent.get("protocol_sha256") != sha256_file(protocol_path):
            raise V6RunImmutableError(f"V6 run intent does not match requested contract: {output_dir}")
        return intent_path
    return prepare_v6_run(
        run_id, spec, output_dir, report_dir, workspace_root, input_ledger,
        protocol_path=protocol_path, horizon=horizon, row_filter=row_filter, sensitivity_tag=sensitivity_tag,
    )


def abort_uncompleted_v6_run(
    output_dir: Path,
    report_dir: Path,
    *,
    workspace_root: Path | None = None,
    run_id: str | None = None,
    spec: Mapping[str, Any] | None = None,
) -> None:
    """Remove only a run that has no completed build/run/release manifest.

    Used by the caller after a build exception so partial data never becomes a
    reusable run.  It intentionally refuses to touch a completed or frozen lane.
    """
    output, report = Path(output_dir).resolve(), Path(report_dir).resolve()
    if run_id is not None:
        safe = validate_safe_identifier(run_id, "run_id")
        if safe in frozen_v6_run_ids(spec or {}):
            raise V6ArtifactError(f"refusing to abort frozen V6 run: {safe}")
        if workspace_root is not None:
            expected_output, expected_report = _expected_output_paths(workspace_root, safe)
            if output != expected_output.resolve() or report != expected_report.resolve():
                raise V6ArtifactError("abort target must equal the run-scoped workspace paths")
        intent = _manifest_path(output, INTENT_MANIFEST)
        if not intent.is_file():
            raise V6ArtifactError("refusing to abort a V6 run without a matching intent manifest")
        intent_payload = load_json_object(intent, "intent manifest")
        if intent_payload.get("run_id") != safe:
            raise V6ArtifactError("refusing to abort a V6 run whose intent does not match run_id")
    if any(_manifest_path(output, name).exists() for name in (BUILD_MANIFEST, RUN_MANIFEST, RELEASE_MANIFEST)):
        return
    import shutil
    if output.exists():
        shutil.rmtree(output)
    if report.exists():
        shutil.rmtree(report)


def write_v6_failure_manifest(
    output_dir: Path,
    run_id: str,
    stage: str,
    error: Exception,
) -> Path:
    """Persist a bounded failure record without calling it a completed run."""
    payload = {
        "artifact_schema_version": "v6_failure_manifest_v1",
        "status": "failed",
        "generated_at_utc": utc_now(),
        "run_id": run_id,
        "stage": stage,
        "error_type": type(error).__name__,
        "error": str(error)[:1000],
    }
    path = _manifest_path(output_dir, "v6_failure_manifest.json")
    if not path.exists():
        atomic_write_json(path, payload)
    return path


def validate_v6_run_id(run_id: str, spec: Mapping[str, Any]) -> str:
    safe = validate_safe_identifier(run_id, "run_id")
    frozen_canonical = str(spec.get("frozen_canonical_run_id", "canonical_150_v7"))
    if safe in frozen_v6_run_ids(spec):
        raise V6ArtifactError(f"refusing frozen V6 run id: {safe}")
    if safe == frozen_canonical or safe.startswith("canonical_150_"):
        raise V6ArtifactError(f"refusing frozen canonical run id: {safe}")
    return safe


def validate_declared_inputs(spec: Mapping[str, Any], workspace_root: Path) -> dict[str, dict[str, str]]:
    """Validate every preregistered V6 input against its declared hash."""
    paths = spec.get("input_paths")
    expected_hashes = spec.get("input_sha256")
    if not isinstance(paths, dict) or not isinstance(expected_hashes, dict):
        raise V6ArtifactError("V6 protocol must define input_paths and input_sha256 objects")
    if set(paths) != set(expected_hashes):
        raise V6ArtifactError("V6 protocol input path/hash membership mismatch")

    ledger: dict[str, dict[str, str]] = {}
    for name in sorted(paths):
        raw_path = paths[name]
        expected = expected_hashes[name]
        if not isinstance(raw_path, str) or not isinstance(expected, str) or len(expected) != 64:
            raise V6ArtifactError(f"V6 protocol input contract is invalid for {name}")
        path = resolve_workspace_path(workspace_root, raw_path, field=f"input_paths.{name}")
        actual = sha256_file(path)
        if actual != expected:
            raise V6ArtifactError(f"preregistered V6 input hash mismatch: {name}")
        ledger[name] = {
            "path": portable_path(workspace_root, path),
            "sha256": actual,
        }
    return ledger


def validate_input_ledger(ledger: Mapping[str, Any], workspace_root: Path) -> None:
    """Re-hash a persisted input ledger before consuming prior build artifacts."""
    if not isinstance(ledger, Mapping) or not ledger:
        raise V6ArtifactError("V6 input ledger is missing")
    for name, entry in ledger.items():
        if not isinstance(entry, Mapping):
            raise V6ArtifactError(f"V6 input ledger entry is invalid: {name}")
        path = resolve_workspace_path(workspace_root, str(entry.get("path", "")), field=f"ledger.{name}")
        expected = str(entry.get("sha256", ""))
        if sha256_file(path) != expected:
            raise V6ArtifactError(f"V6 input ledger hash mismatch: {name}")


def artifact_ledger(workspace_root: Path, paths: Iterable[Path]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in sorted((Path(item) for item in paths), key=lambda item: str(item)):
        if not path.is_file():
            raise FileNotFoundError(f"V6 artifact missing for manifest: {path}")
        entries.append(
            {
                "path": portable_path(workspace_root, path),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    return entries


def validate_artifact_ledger(entries: Iterable[Mapping[str, Any]], workspace_root: Path) -> None:
    for entry in entries:
        path = resolve_workspace_path(workspace_root, str(entry.get("path", "")), field="artifact.path")
        expected = str(entry.get("sha256", ""))
        if sha256_file(path) != expected:
            raise V6ArtifactError(f"V6 artifact hash mismatch: {entry.get('path')}")


def code_provenance(workspace_root: Path, code_paths: Iterable[Path]) -> dict[str, Any]:
    root = Path(workspace_root).resolve()
    git_commit = "unknown"
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            git_commit = result.stdout.strip()
    except OSError:
        pass
    requirements = []
    for candidate in ("KL_180826/requirements-reproduction.txt", "KL_180826/requirements-runtime.txt", "KL_180826/requirements.txt"):
        path = (root / candidate).resolve()
        if path.is_file():
            requirements.append({"path": portable_path(root, path), "sha256": sha256_file(path)})
    return {
        "git_commit": git_commit,
        "python_version": sys.version,
        "platform": platform.platform(),
        "implementation": platform.python_implementation(),
        "requirements": requirements,
        "code": artifact_ledger(root, code_paths),
    }


def _manifest_path(output_dir: Path, name: str) -> Path:
    return Path(output_dir).resolve() / name


def assert_new_v6_run_available(run_id: str, spec: Mapping[str, Any], output_dir: Path, report_dir: Path) -> str:
    """Refuse frozen, staged, completed, or otherwise nonempty new run targets."""
    safe = validate_v6_run_id(run_id, spec)
    for directory in (Path(output_dir), Path(report_dir)):
        if any(_manifest_path(directory, name).exists() for name in V6_MANIFEST_NAMES):
            raise V6RunImmutableError(f"V6 run already has immutable manifest: {directory}")
        if directory.exists() and any(directory.iterdir()):
            raise V6RunImmutableError(f"V6 run directory is not empty: {directory}")
    return safe


def assert_v6_stage_available(output_dir: Path, stage_manifest: str) -> None:
    path = _manifest_path(output_dir, stage_manifest)
    if path.exists():
        raise V6RunImmutableError(f"V6 manifest already exists: {path}")
    if stage_manifest != RELEASE_MANIFEST and _manifest_path(output_dir, RELEASE_MANIFEST).exists():
        raise V6RunImmutableError(f"V6 release is immutable: {output_dir}")


def write_manifest_once(output_dir: Path, name: str, payload: Mapping[str, Any]) -> Path:
    assert_v6_stage_available(output_dir, name)
    path = _manifest_path(output_dir, name)
    atomic_write_json(path, dict(payload))
    return path


def load_required_manifest(output_dir: Path, name: str) -> dict[str, Any]:
    path = _manifest_path(output_dir, name)
    if not path.is_file():
        raise FileNotFoundError(f"required V6 manifest is missing: {path}")
    return load_json_object(path, name)


def write_v6_build_manifest(
    output_dir: Path,
    run_id: str,
    spec: Mapping[str, Any],
    workspace_root: Path,
    input_ledger: Mapping[str, Any],
    artifact_paths: Iterable[Path],
    code_paths: Iterable[Path],
    *,
    target_manifest: Path | None = None,
    extra: Mapping[str, Any] | None = None,
) -> Path:
    intent = load_required_manifest(output_dir, INTENT_MANIFEST)
    if intent.get("run_id") != run_id:
        raise V6ArtifactError("V6 intent run id mismatch")
    payload: dict[str, Any] = {
        "artifact_schema_version": "v6_build_manifest_v1",
        "status": "completed",
        "generated_at_utc": utc_now(),
        "run_id": run_id,
        "protocol_version": spec.get("protocol_version"),
        "protocol_sha256": intent.get("protocol_sha256"),
        "intent_manifest_sha256": sha256_file(_manifest_path(output_dir, INTENT_MANIFEST)),
        "inputs": dict(input_ledger),
        "artifacts": artifact_ledger(workspace_root, artifact_paths),
        "code_provenance": code_provenance(workspace_root, code_paths),
    }
    if target_manifest is not None:
        payload["target_manifest"] = {
            "path": portable_path(workspace_root, target_manifest),
            "sha256": sha256_file(target_manifest),
        }
    if extra:
        payload.update(dict(extra))
    return write_manifest_once(output_dir, BUILD_MANIFEST, payload)


def load_and_validate_build_manifest(output_dir: Path, workspace_root: Path, run_id: str) -> dict[str, Any]:
    manifest = load_required_manifest(output_dir, BUILD_MANIFEST)
    if manifest.get("status") != "completed" or manifest.get("run_id") != run_id:
        raise V6ArtifactError("V6 build manifest run/status mismatch")
    validate_input_ledger(manifest.get("inputs", {}), workspace_root)
    validate_artifact_ledger(manifest.get("artifacts", []), workspace_root)
    return manifest


def write_v6_run_manifest(
    output_dir: Path,
    run_id: str,
    spec: Mapping[str, Any],
    workspace_root: Path,
    artifact_paths: Iterable[Path],
    code_paths: Iterable[Path],
    *,
    extra: Mapping[str, Any] | None = None,
) -> Path:
    build = load_and_validate_build_manifest(output_dir, workspace_root, run_id)
    payload: dict[str, Any] = {
        "artifact_schema_version": "v6_run_manifest_v1",
        "status": "completed",
        "generated_at_utc": utc_now(),
        "run_id": run_id,
        "protocol_version": spec.get("protocol_version"),
        "protocol_sha256": build.get("protocol_sha256"),
        "build_manifest_sha256": sha256_file(_manifest_path(output_dir, BUILD_MANIFEST)),
        "inputs": build.get("inputs", {}),
        "artifacts": artifact_ledger(workspace_root, artifact_paths),
        "code_provenance": code_provenance(workspace_root, code_paths),
    }
    if extra:
        payload.update(dict(extra))
    return write_manifest_once(output_dir, RUN_MANIFEST, payload)


def write_v6_release_manifest(
    output_dir: Path,
    run_id: str,
    spec: Mapping[str, Any],
    workspace_root: Path,
    public_artifacts: Iterable[Path],
    claims: Iterable[Mapping[str, Any]],
    *,
    limitations: Iterable[str],
    extra: Mapping[str, Any] | None = None,
) -> Path:
    run = load_required_manifest(output_dir, RUN_MANIFEST)
    if run.get("status") != "completed" or run.get("run_id") != run_id:
        raise V6ArtifactError("V6 run manifest run/status mismatch")
    validate_artifact_ledger(run.get("artifacts", []), workspace_root)
    payload: dict[str, Any] = {
        "artifact_schema_version": "v6_release_manifest_v1",
        "status": "completed",
        "generated_at_utc": utc_now(),
        "run_id": run_id,
        "protocol_version": spec.get("protocol_version"),
        "protocol_sha256": run.get("protocol_sha256"),
        "run_manifest_sha256": sha256_file(_manifest_path(output_dir, RUN_MANIFEST)),
        "public_artifacts": artifact_ledger(workspace_root, public_artifacts),
        "claims": [dict(claim) for claim in claims],
        "limitations": sorted({str(item) for item in limitations}),
    }
    if extra:
        payload.update(dict(extra))
    return write_manifest_once(output_dir, RELEASE_MANIFEST, payload)


def write_target_manifest(
    target_path: Path,
    workspace_root: Path,
    input_ledger: Mapping[str, Mapping[str, str]],
    code_path: Path,
    horizon: int,
) -> Path:
    required = {"prices", "benchmark"}
    if not required.issubset(input_ledger):
        raise V6ArtifactError("V6 target manifest requires prices and benchmark input hashes")
    path = Path(target_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    payload = {
        "artifact_schema_version": "v6_target_manifest_v1",
        "status": "completed",
        "generated_at_utc": utc_now(),
        "horizon_benchmark_sessions": int(horizon),
        "sources": {name: dict(input_ledger[name]) for name in sorted(required)},
        "target": {
            "path": portable_path(workspace_root, path),
            "sha256": sha256_file(path),
        },
        "target_builder": {
            "path": portable_path(workspace_root, code_path),
            "sha256": sha256_file(code_path),
        },
    }
    manifest_path = path.with_name(TARGET_MANIFEST)
    if manifest_path.exists():
        raise V6RunImmutableError(f"V6 target manifest already exists: {manifest_path}")
    atomic_write_json(manifest_path, payload)
    return manifest_path


def validate_target_manifest(
    target_path: Path,
    workspace_root: Path,
    input_ledger: Mapping[str, Mapping[str, str]],
    code_path: Path,
    horizon: int,
) -> Path:
    manifest_path = Path(target_path).with_name(TARGET_MANIFEST)
    if not manifest_path.is_file():
        raise V6ArtifactError(f"cached V6 targets lack provenance manifest: {target_path}")
    manifest = load_json_object(manifest_path, "target manifest")
    if manifest.get("status") != "completed" or int(manifest.get("horizon_benchmark_sessions", -1)) != int(horizon):
        raise V6ArtifactError("cached V6 target manifest status/horizon mismatch")
    if manifest.get("target", {}).get("path") != portable_path(workspace_root, target_path):
        raise V6ArtifactError("cached V6 target path mismatch")
    if manifest.get("target", {}).get("sha256") != sha256_file(target_path):
        raise V6ArtifactError("cached V6 target hash mismatch")
    if manifest.get("target_builder", {}).get("sha256") != sha256_file(code_path):
        raise V6ArtifactError("cached V6 target-builder code hash mismatch")
    for name in ("prices", "benchmark"):
        if manifest.get("sources", {}).get(name) != dict(input_ledger[name]):
            raise V6ArtifactError(f"cached V6 target source mismatch: {name}")
    return manifest_path


def claim_gate(
    record: Mapping[str, Any],
    *,
    alpha: float,
    expected_baseline: str,
    expected_comparison: str,
    expected_model: str,
    expected_metric: str,
    audit_pass: bool = True,
    manifest_pass: bool = True,
) -> dict[str, Any]:
    """Return an explicit claim state; estimability is never claim support."""
    status = str(record.get("status", ""))
    contract_match = (
        str(record.get("baseline_config", "")) == expected_baseline
        and str(record.get("comparison_config", "")) == expected_comparison
        and str(record.get("model", "")) == expected_model
        and str(record.get("metric", "")) == expected_metric
    )

    def number(name: str) -> float | None:
        value = record.get(name)
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return None
        return parsed if parsed == parsed else None

    effect = number("improvement_delta")
    ci_low = number("bootstrap_ci_low")
    adjusted_p = number("p_value_bh")
    gates = {
        "estimable": status == "ok",
        "comparison_contract": contract_match,
        "positive_effect": effect is not None and effect > 0,
        "ci_lower_bound_positive": ci_low is not None and ci_low > 0,
        "bh_alpha": adjusted_p is not None and adjusted_p <= float(alpha),
        "audit_pass": bool(audit_pass),
        "manifest_pass": bool(manifest_pass),
    }
    if not gates["estimable"] or not gates["comparison_contract"]:
        state = "not_estimable"
    elif all(gates.values()):
        state = "supported"
    else:
        state = "unsupported"
    return {"claim_state": state, "claim_gate_pass": state == "supported", "claim_gates": gates}


def primary_claims(
    rows: Iterable[Mapping[str, Any]],
    spec: Mapping[str, Any],
    *,
    audit_pass: bool = True,
    manifest_pass: bool = True,
) -> list[dict[str, Any]]:
    primary = spec.get("primary", {})
    family = spec.get("hypothesis_families", {}).get("V6_H1_H2", {})
    hypotheses = family.get("hypotheses", []) if isinstance(family, Mapping) else []
    by_id = {str(item.get("id")): item for item in hypotheses if isinstance(item, Mapping)}
    result: list[dict[str, Any]] = []
    for row in rows:
        hypothesis = str(row.get("hypothesis", ""))
        contract = by_id.get(hypothesis)
        if not contract or str(row.get("role", "")) != "primary":
            continue
        if str(row.get("model", "")) != str(primary.get("model", "RandomForest")):
            continue
        if str(row.get("metric", "")) != str(primary.get("metric", "balanced_accuracy")):
            continue
        gate = claim_gate(
            row,
            alpha=float(spec.get("inference", {}).get("alpha", 0.05)),
            expected_baseline=str(contract.get("baseline_config")),
            expected_comparison=str(contract.get("comparison_config")),
            expected_model=str(primary.get("model")),
            expected_metric=str(primary.get("metric")),
            audit_pass=audit_pass,
            manifest_pass=manifest_pass,
        )
        result.append(
            {
                "claim_id": hypothesis,
                "baseline_config": row.get("baseline_config"),
                "comparison_config": row.get("comparison_config"),
                "model": row.get("model"),
                "metric": row.get("metric"),
                "improvement_delta": row.get("improvement_delta"),
                "bootstrap_ci_low": row.get("bootstrap_ci_low"),
                "bootstrap_ci_high": row.get("bootstrap_ci_high"),
                "p_value": row.get("p_value"),
                "p_value_bh": row.get("p_value_bh"),
                "status": row.get("status"),
                **gate,
            }
        )
    return result
