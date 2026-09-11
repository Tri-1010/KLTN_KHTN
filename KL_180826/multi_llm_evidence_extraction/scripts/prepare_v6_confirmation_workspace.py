"""Create an isolated, immutable-input workspace for V6 H2 confirmation.

The helper copies only code/configuration and creates a snapshot manifest. It does
not collect data, call a provider, or mutate the portable thesis bundle.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(SCRIPT_DIR))

from common import ROOT, sha256_file, utc_now
from v6_artifacts import V6ArtifactError, atomic_write_json, portable_path, resolve_workspace_path

COPY_DIRECTORIES = (
    "KL_180826/multi_llm_evidence_extraction/config",
    "KL_180826/multi_llm_evidence_extraction/schemas",
    "KL_180826/multi_llm_evidence_extraction/scripts",
    "KL_180826/pipeline",
    "KL_180826/scripts",
)
COPY_FILES = (
    "KL_180826/requirements-reproduction.txt",
    "KL_180826/requirements-runtime.txt",
    "KL_180826/requirements.txt",
)
SNAPSHOT_INPUTS = (
    "KL_180826/data/prices/all_vn30_prices.csv",
    "KL_180826/data/prices_extended/VNINDEX.csv",
    "KL_180826/data/features/technical_features.csv",
    "data/features/keyword_features.csv",
    "multi_llm_evidence_extraction/outputs/semantic_features_daily.csv",
    "KL_180826/multi_llm_evidence_extraction/outputs/pseudo_labels_consensus.csv",
    "KL_180826/data/news/matched/all_news_matched.csv",
    "KL_180826/data/news/processed/all_news_processed.csv",
)


def _ensure_empty_external_workspace(workspace: Path, bundle_root: Path) -> Path:
    target = workspace.resolve()
    bundle = bundle_root.resolve()
    if target == bundle or bundle in target.parents or target in bundle.parents:
        raise V6ArtifactError("confirmation workspace must be outside KL_180826 bundle")
    if target.exists() and any(target.iterdir()):
        raise FileExistsError(f"confirmation workspace must be empty: {target}")
    if target.exists() and target.is_symlink():
        raise V6ArtifactError("confirmation workspace must not be a symlink/junction")
    target.mkdir(parents=True, exist_ok=True)
    return target


def _copy_code(source_root: Path, workspace: Path) -> list[Path]:
    copied: list[Path] = []
    for relative in COPY_DIRECTORIES:
        source = resolve_workspace_path(source_root, relative, field="workspace source", require_file=False)
        if not source.is_dir():
            raise FileNotFoundError(f"confirmation workspace source directory is missing: {source}")
        destination = workspace / relative
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "outputs", "reports"), dirs_exist_ok=False)
        copied.extend(path for path in destination.rglob("*") if path.is_file())
    for relative in COPY_FILES:
        source = resolve_workspace_path(source_root, relative, field="workspace source")
        destination = workspace / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append(destination)
    return copied


def _snapshot_inputs(source_root: Path, workspace: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for relative in SNAPSHOT_INPUTS:
        source = resolve_workspace_path(source_root, relative, field="confirmation snapshot input")
        # Preserve the protocol-relative path directly under the new workspace so
        # copied V6 scripts cannot resolve back into the source repository.
        destination = workspace / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        rows.append({
            "source_path": portable_path(source_root, source),
            "source_sha256": sha256_file(source),
            "snapshot_path": destination.relative_to(workspace).as_posix(),
            "snapshot_sha256": sha256_file(destination),
            "size_bytes": destination.stat().st_size,
        })
    return rows


def prepare_confirmation_workspace(workspace: Path, source_root: Path) -> dict[str, Any]:
    source = source_root.resolve()
    if not (source / "KL_180826").is_dir():
        raise FileNotFoundError(f"source root lacks KL_180826: {source}")
    target = _ensure_empty_external_workspace(workspace, source / "KL_180826")
    try:
        copied = _copy_code(source, target)
        snapshot = _snapshot_inputs(source, target)
        manifest = {
            "artifact_schema_version": "v6_confirmation_workspace_v1",
            "status": "prepared",
            "created_at_utc": utc_now(),
            "workspace_root": ".",
            "source_root": "not_persisted",
            "code_file_count": len(copied),
            "snapshot_inputs": snapshot,
            "locked_run_ids": ["v6_primary_20260909"],
            "network_execution": "not_run",
            "write_policy": "all future collection, annotation, features, and confirmation artifacts remain under this workspace",
        }
        atomic_write_json(target / "confirmation_workspace_manifest.json", manifest)
        return manifest
    except Exception:
        shutil.rmtree(target, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a clean isolated V6 H2 confirmation workspace.")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, default=ROOT.parent)
    args = parser.parse_args()
    result = prepare_confirmation_workspace(args.workspace, args.source_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
