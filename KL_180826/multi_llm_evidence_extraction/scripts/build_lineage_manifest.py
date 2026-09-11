from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
STUDY_DIR = SCRIPT_DIR.parent
REPO_ROOT = STUDY_DIR.parent
DEFAULT_OUTPUT = STUDY_DIR / "outputs" / "report_lineage_manifest.json"
HARMONIZED_CONFIG = STUDY_DIR / "config" / "harmonized_comparison_v5.json"

DEFAULT_PATHS = [
    STUDY_DIR / "outputs" / "pseudo_labels_consensus.csv",
    STUDY_DIR / "outputs" / "rule_labels.csv",
    STUDY_DIR / "outputs" / "event_window_stat_tests.csv",
    STUDY_DIR / "outputs" / "placebo_pre_event_stat_tests.csv",
    STUDY_DIR / "outputs" / "ml_predictions_outperform.csv",
    STUDY_DIR / "outputs" / "ml_paired_daily_metrics_outperform.csv",
    STUDY_DIR / "outputs" / "ml_bootstrap_delta_outperform.csv",
    STUDY_DIR / "outputs" / "topk_portfolio_simulation.csv",
    STUDY_DIR / "outputs" / "topk_random_null_summary.csv",
    STUDY_DIR / "outputs" / "topk_cost_sensitivity_summary.csv",
    STUDY_DIR / "outputs" / "consensus_family_sensitivity_summary.csv",
    STUDY_DIR / "data" / "manual_sanity_check_sample.csv",
    STUDY_DIR / "outputs" / "outcome_review_labels.csv",
]


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def display_path(path: Path, root: Path = REPO_ROOT) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def lineage_record(path: Path, root: Path = REPO_ROOT) -> dict[str, Any]:
    exists = path.is_file()
    stat = path.stat() if exists else None
    return {
        "path": display_path(path, root),
        "status": "available" if exists else "missing_optional",
        "size_bytes": stat.st_size if stat else None,
        "modified_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(timespec="seconds") if stat else None,
        "sha256": sha256_file(path),
    }


def build_manifest(paths: Iterable[Path], root: Path = REPO_ROOT) -> dict[str, Any]:
    records = [lineage_record(Path(path), root) for path in paths]
    return {
        "manifest_schema_version": "semantic_report_lineage_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root": str(root.resolve()),
        "artifacts": records,
        "available_count": sum(row["status"] == "available" for row in records),
        "missing_optional_count": sum(row["status"] == "missing_optional" for row in records),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build byte-level lineage manifest for semantic-news report inputs.")
    parser.add_argument("paths", nargs="*", type=Path, help="Optional artifact paths; defaults to canonical report inputs.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    return parser.parse_args()


def discover_harmonized_artifacts() -> list[Path]:
    paths = [HARMONIZED_CONFIG]
    for root in (STUDY_DIR / "outputs" / "harmonized", STUDY_DIR / "reports" / "harmonized"):
        if root.exists():
            paths.extend(path for path in root.rglob("*") if path.is_file())
    return sorted(set(paths))


def main() -> int:
    args = parse_args()
    paths = args.paths or [*DEFAULT_PATHS, *discover_harmonized_artifacts()]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build_manifest(paths, args.root), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
