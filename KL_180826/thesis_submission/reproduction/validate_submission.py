from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "thesis_submission"
STUDY = ROOT / "multi_llm_evidence_extraction"

MANDATORY = (
    "README.md",
    "proposal/de_cuong.md",
    "thesis/luan_van.md",
    "canonical_results/canonical_summary.json",
    "canonical_results/evaluation_manifest.json",
    "canonical_results/run_manifest.json",
    "canonical_results/manifests/harmonized_article_spine.csv",
    "canonical_results/manifests/harmonized_row_manifest.csv",
    "canonical_results/manifests/harmonized_fold_manifest.csv",
    "canonical_results/manifests/harmonized_fold_feature_manifest.csv",
    "canonical_results/tables/harmonized_paired_daily_deltas.csv",
    "governance/claim_evidence_matrix.md",
    "governance/data_dictionary.md",
    "governance/limitations.md",
    "governance/legacy_artifact_registry.md",
    "governance/checksums.sha256",
    "reproduction/README.md",
    "reproduction/build_submission.py",
    "reproduction/generate_figures.py",
    "reproduction/validate_submission.py",
    "artifacts/figures/primary_delta_ci.png",
    "artifacts/figures/canonical_attrition.png",
    "artifacts/figure_data/primary_delta_ci.csv",
    "artifacts/figure_data/canonical_attrition.csv",
)
PLACEHOLDER = re.compile(r"\b(TODO|TBD|FIXME|XX+)\b", re.IGNORECASE)
ABSOLUTE_PATH = re.compile(r"[A-Za-z]:\\(?:Users|Program Files|Windows)\\")
SECRET = re.compile(r"(?:sk-ant-|AIza[0-9A-Za-z_-]{20,}|GEMINI_API_KEY\s*=|ANTHROPIC_API_KEY\s*=)")
EVIDENCE_PATH = re.compile(r"`((?:canonical_results|artifacts)/[^`]+)`")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bundle_file_set() -> set[str]:
    return {
        path.relative_to(BUNDLE).as_posix()
        for path in BUNDLE.rglob("*")
        if path.is_file()
        and path.name != "checksums.sha256"
        and path.suffix != ".pyc"
        and "__pycache__" not in path.parts
    }


def validate_checksums(path: Path) -> list[str]:
    errors = []
    listed: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError:
            errors.append("invalid checksum line")
            continue
        if relative in listed:
            errors.append(f"duplicate checksum target: {relative}")
            continue
        listed.add(relative)
        target = BUNDLE / relative
        try:
            target.resolve().relative_to(BUNDLE.resolve())
        except ValueError:
            errors.append(f"checksum target escapes bundle: {relative}")
            continue
        if not target.exists():
            errors.append(f"checksum target missing: {relative}")
        elif sha256(target) != digest:
            errors.append(f"checksum mismatch: {relative}")
    actual = bundle_file_set()
    for relative in sorted(actual - listed):
        errors.append(f"unlisted bundle file: {relative}")
    for relative in sorted(listed - actual):
        if not (BUNDLE / relative).exists():
            continue
        errors.append(f"checksum target excluded from bundle set: {relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="canonical_150_v7")
    args = parser.parse_args()
    errors = []
    for relative in MANDATORY:
        if not (BUNDLE / relative).exists():
            errors.append(f"mandatory file missing: {relative}")
    cache_files = [path.relative_to(BUNDLE).as_posix() for path in BUNDLE.rglob("*") if path.is_file() and (path.suffix == ".pyc" or "__pycache__" in path.parts)]
    for relative in cache_files:
        errors.append(f"cache file present in bundle: {relative}")

    run_dir = STUDY / "outputs" / "harmonized" / args.run_id
    source_summary = run_dir / "canonical_summary.json"
    bundled_summary = BUNDLE / "canonical_results" / "canonical_summary.json"
    if not source_summary.exists():
        errors.append("source canonical_summary missing")
    elif bundled_summary.exists() and sha256(source_summary) != sha256(bundled_summary):
        errors.append("bundled canonical_summary differs from run artifact")

    artifact_map = {
        "harmonized_article_spine.csv": "manifests/harmonized_article_spine.csv",
        "harmonized_row_manifest.csv": "manifests/harmonized_row_manifest.csv",
        "harmonized_fold_manifest.csv": "manifests/harmonized_fold_manifest.csv",
        "harmonized_fold_feature_manifest.csv": "manifests/harmonized_fold_feature_manifest.csv",
        "harmonized_paired_daily_deltas.csv": "tables/harmonized_paired_daily_deltas.csv",
        "harmonized_inference.csv": "tables/harmonized_inference.csv",
        "harmonized_fold_metrics.csv": "tables/harmonized_fold_metrics.csv",
        "harmonized_calibration.csv": "tables/harmonized_calibration.csv",
        "harmonized_predictions.csv": "predictions/harmonized_predictions.csv",
        "harmonized_topk_matched_deltas.csv": "backtest/harmonized_topk_matched_deltas.csv",
    }
    manifest_path = run_dir / "harmonized_comparison_manifest.json"
    if not manifest_path.exists():
        errors.append("source run manifest missing")
    else:
        run_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        protocol_source = STUDY / "config" / "harmonized_comparison_v5.json"
        bundled_protocol = BUNDLE / "canonical_results" / "evaluation_manifest.json"
        declared_protocol_hash = run_manifest.get("protocol_sha256")
        if not declared_protocol_hash or not protocol_source.exists() or sha256(protocol_source) != declared_protocol_hash:
            errors.append("source protocol hash mismatch")
        elif not bundled_protocol.exists() or sha256(bundled_protocol) != declared_protocol_hash:
            errors.append("bundled protocol hash mismatch")
        manifest_entries = [*run_manifest.get("inputs", []), *run_manifest.get("outputs", [])]
        build_manifest_path = run_dir / "harmonized_build_manifest.json"
        if build_manifest_path.exists():
            build_manifest = json.loads(build_manifest_path.read_text(encoding="utf-8"))
            manifest_entries.extend(build_manifest.get("artifacts", []))
        else:
            errors.append("source build manifest missing")
        artifact_hashes = {Path(str(item.get("path", ""))).name: item.get("sha256") for item in manifest_entries}
        for source_name, bundle_relative in artifact_map.items():
            source = run_dir / source_name
            bundled = BUNDLE / "canonical_results" / bundle_relative
            expected_hash = artifact_hashes.get(source_name)
            if not expected_hash:
                errors.append(f"run manifest hash missing: {source_name}")
            elif not source.exists() or sha256(source) != expected_hash:
                errors.append(f"source run artifact hash mismatch: {source_name}")
            elif not bundled.exists() or sha256(bundled) != expected_hash:
                errors.append(f"bundled run artifact hash mismatch: {bundle_relative}")

    if bundled_summary.exists():
        summary = json.loads(bundled_summary.read_text(encoding="utf-8"))
        if summary.get("run_id") != args.run_id:
            errors.append("canonical summary run_id mismatch")
        if summary.get("run_tier") != "canonical":
            errors.append("smoke output present in canonical bundle")
        primary = summary.get("primary", {})
        expected = {
            "family": "P1",
            "baseline_config": "B_technical_coverage_keyword",
            "comparison_config": "C_technical_coverage_semantic",
            "model": "RandomForest",
            "metric": "balanced_accuracy",
            "topk": 10,
        }
        for key, value in expected.items():
            if primary.get(key) != value:
                errors.append(f"primary contract mismatch: {key}")

    for path in BUNDLE.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".py", ".json", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        relative = path.relative_to(BUNDLE).as_posix()
        scan_text = text
        if relative == "reproduction/validate_submission.py":
            scan_text = "\n".join(
                line for line in text.splitlines()
                if not line.startswith(("PLACEHOLDER =", "ABSOLUTE_PATH =", "SECRET ="))
            )
        if PLACEHOLDER.search(scan_text):
            errors.append(f"placeholder found: {relative}")
        if ABSOLUTE_PATH.search(scan_text):
            errors.append(f"absolute local path found: {relative}")
        if SECRET.search(scan_text):
            errors.append(f"possible secret found: {relative}")

    matrix_path = BUNDLE / "governance" / "claim_evidence_matrix.md"
    if matrix_path.exists():
        matrix = matrix_path.read_text(encoding="utf-8")
        for evidence_path in EVIDENCE_PATH.findall(matrix):
            if not (BUNDLE / evidence_path).exists():
                errors.append(f"claim evidence missing: {evidence_path}")

    checksum_path = BUNDLE / "governance" / "checksums.sha256"
    if checksum_path.exists():
        errors.extend(validate_checksums(checksum_path))

    if errors:
        print(json.dumps({"status": "failed", "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"status": "passed", "run_id": args.run_id}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
