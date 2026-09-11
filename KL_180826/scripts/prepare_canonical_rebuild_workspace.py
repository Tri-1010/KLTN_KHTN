#!/usr/bin/env python
"""Create a clean workspace for a new canonical-comparison rerun.

The frozen canonical_150_v7 artifacts in the portable bundle are never modified.
This helper copies only the processed inputs and source needed to start a new run.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COPY_DIRS = (
    "pipeline",
    "config",
    "scripts",
    "multi_llm_evidence_extraction/config",
    "multi_llm_evidence_extraction/data",
    "multi_llm_evidence_extraction/prompts",
    "multi_llm_evidence_extraction/schemas",
    "multi_llm_evidence_extraction/scripts",
)
COPY_FILES = (
    "requirements-reproduction.txt",
    "data/prices/all_vn30_prices.csv",
    "data/prices_extended/VNINDEX.csv",
    "data/features/technical_features.csv",
    "multi_llm_evidence_extraction/outputs/pseudo_labels_consensus.csv",
    "multi_llm_evidence_extraction/outputs/pseudo_labels_consensus.jsonl",
    "multi_llm_evidence_extraction/outputs/annotation_manifest_index.json",
)


def ignored(_: str, names: list[str]) -> set[str]:
    return {name for name in names if name in {"__pycache__", ".pytest_cache", "outputs", "reports"} or name.endswith(".pyc")}


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a separate workspace for a new canonical-comparison rerun.")
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    if workspace == ROOT or ROOT in workspace.parents:
        raise ValueError("workspace must be outside the frozen portable bundle")
    if workspace.exists() and any(workspace.iterdir()):
        raise FileExistsError("workspace must be empty")
    workspace.mkdir(parents=True, exist_ok=True)
    for relative in COPY_DIRS:
        source = ROOT / relative
        if not source.is_dir():
            raise FileNotFoundError(source)
        shutil.copytree(source, workspace / relative, ignore=ignored, dirs_exist_ok=True)
    for relative in COPY_FILES:
        source = ROOT / relative
        if not source.is_file():
            raise FileNotFoundError(source)
        target = workspace / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    print("Workspace prepared:", workspace)
    print("Use a NEW --run-id under multi_llm_evidence_extraction/outputs/harmonized/.")
    print("Do not copy or overwrite canonical_150_v7. Compare a new run against the frozen bundle afterward.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
