from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "thesis_submission"
STUDY = ROOT / "multi_llm_evidence_extraction"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_Không khả dụng._"
    columns = [str(column) for column in frame.columns]
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(str(row[column]).replace("|", "\\|") for column in frame.columns) + " |")
    return "\n".join(lines)


def build_primary_table(summary: dict[str, Any]) -> pd.DataFrame:
    primary = summary["primary"]
    return pd.DataFrame([{
        "Run": summary["run_id"],
        "Baseline": primary["baseline_config"],
        "Comparison": primary["comparison_config"],
        "Model": primary["model"],
        "Metric": primary["metric"],
        "Delta": primary["improvement_delta"],
        "CI low": primary["bootstrap_ci_low"],
        "CI high": primary["bootstrap_ci_high"],
        "p BH": primary["p_value_bh"],
        "Folds": primary["n_folds"],
        "Gate": primary["gate_pass"],
    }])


def copy_artifact(source: Path, target: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def repo_relative_manifest(value: Any) -> Any:
    if isinstance(value, dict):
        output = {key: repo_relative_manifest(item) for key, item in value.items()}
        path = output.get("path")
        if isinstance(path, str):
            candidate = Path(path)
            if candidate.is_absolute():
                try:
                    output["path"] = candidate.resolve().relative_to(ROOT.resolve()).as_posix()
                except ValueError:
                    output["path"] = candidate.name
        return output
    if isinstance(value, list):
        return [repo_relative_manifest(item) for item in value]
    return value


def write_portable_manifest(source: Path, target: Path) -> None:
    manifest = json.loads(source.read_text(encoding="utf-8"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(repo_relative_manifest(manifest), ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="canonical_150_v7")
    args = parser.parse_args()
    if args.run_id != "canonical_150_v7":
        raise ValueError("submission requires canonical_150_v7")
    run_dir = STUDY / "outputs" / "harmonized" / args.run_id
    summary_path = run_dir / "canonical_summary.json"
    manifest_path = run_dir / "harmonized_comparison_manifest.json"
    if not summary_path.exists() or not manifest_path.exists():
        raise FileNotFoundError("completed canonical summary/manifest required")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("run_id") != "canonical_150_v7":
        raise ValueError("submission requires canonical_150_v7")
    if summary.get("mode") != "pilot" or summary.get("run_tier") != "canonical":
        raise ValueError("only preregistered canonical pilot output can build thesis submission")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("preregistered_input_match") is not True:
        raise ValueError("submission requires preregistered input match")

    canonical = BUNDLE / "canonical_results"
    shutil.rmtree(BUNDLE / "reproduction" / "__pycache__", ignore_errors=True)
    copy_artifact(summary_path, canonical / "canonical_summary.json")
    write_portable_manifest(manifest_path, canonical / "run_manifest.json")
    copy_artifact(STUDY / "config" / "harmonized_comparison_v5.json", canonical / "evaluation_manifest.json")

    artifact_map = {
        "harmonized_article_spine.csv": canonical / "manifests" / "harmonized_article_spine.csv",
        "harmonized_row_manifest.csv": canonical / "manifests" / "harmonized_row_manifest.csv",
        "harmonized_fold_manifest.csv": canonical / "manifests" / "harmonized_fold_manifest.csv",
        "harmonized_fold_feature_manifest.csv": canonical / "manifests" / "harmonized_fold_feature_manifest.csv",
        "harmonized_paired_daily_deltas.csv": canonical / "tables" / "harmonized_paired_daily_deltas.csv",
        "harmonized_inference.csv": canonical / "tables" / "harmonized_inference.csv",
        "harmonized_fold_metrics.csv": canonical / "tables" / "harmonized_fold_metrics.csv",
        "harmonized_calibration.csv": canonical / "tables" / "harmonized_calibration.csv",
        "harmonized_predictions.csv": canonical / "predictions" / "harmonized_predictions.csv",
        "harmonized_topk_matched_deltas.csv": canonical / "backtest" / "harmonized_topk_matched_deltas.csv",
    }
    for name, target in artifact_map.items():
        copy_artifact(run_dir / name, target)

    primary = build_primary_table(summary)
    primary_csv = BUNDLE / "artifacts" / "figure_data" / "primary_comparison.csv"
    primary_csv.parent.mkdir(parents=True, exist_ok=True)
    primary.to_csv(primary_csv, index=False, encoding="utf-8-sig")
    (BUNDLE / "artifacts" / "tables").mkdir(parents=True, exist_ok=True)
    (BUNDLE / "artifacts" / "tables" / "primary_comparison.md").write_text(
        "# Primary same-sample comparison\n\n" + markdown_table(primary) + "\n",
        encoding="utf-8",
    )

    subprocess.run(
        [sys.executable, str(BUNDLE / "reproduction" / "generate_figures.py"), "--run-id", args.run_id],
        cwd=ROOT,
        check=True,
    )

    generated = BUNDLE / "artifacts" / "tables" / "canonical_results_generated.md"
    generated.write_text(
        "# Canonical results generated from structured artifacts\n\n"
        + f"- Run: `{summary['run_id']}`\n"
        + f"- Protocol SHA256: `{summary['protocol_sha256']}`\n"
        + f"- Claim level: `{summary['claim_level']}`\n\n"
        + "## Primary comparison\n\n"
        + markdown_table(primary)
        + "\n\n## Attrition\n\n"
        + markdown_table(pd.DataFrame([summary["attrition"]]))
        + "\n\n## Top-K status\n\n"
        + markdown_table(pd.DataFrame(summary.get("topk", [])))
        + "\n",
        encoding="utf-8",
    )

    shutil.rmtree(BUNDLE / "reproduction" / "__pycache__", ignore_errors=True)
    for checksum in (BUNDLE / "governance" / "checksums.sha256",):
        checksum.unlink(missing_ok=True)
    checksums = []
    for path in sorted(
        item
        for item in BUNDLE.rglob("*")
        if item.is_file()
        and item.name != "checksums.sha256"
        and item.suffix != ".pyc"
        and "__pycache__" not in item.parts
    ):
        checksums.append(f"{sha256(path)}  {path.relative_to(BUNDLE).as_posix()}")
    checksum_path = BUNDLE / "governance" / "checksums.sha256"
    checksum_path.write_text("\n".join(checksums) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": args.run_id, "files_hashed": len(checksums), "bundle": str(BUNDLE)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
