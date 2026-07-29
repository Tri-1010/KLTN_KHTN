from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_consensus_labels import load_annotation_rows, vote
from common import CATEGORICAL_FIELDS, OUTPUT_DIR, REPORT_DIR, ensure_dirs, markdown_table, write_csv

LABEL_FILES = [OUTPUT_DIR / f"labels_annotator_{x}.jsonl" for x in ("a", "b", "c")]
CANONICAL_CONSENSUS = OUTPUT_DIR / "pseudo_labels_consensus.csv"
DETAIL_OUT = OUTPUT_DIR / "consensus_family_sensitivity_detail.csv"
SUMMARY_OUT = OUTPUT_DIR / "consensus_family_sensitivity_summary.csv"
REPORT_OUT = REPORT_DIR / "consensus_family_sensitivity_report.md"
UNKNOWN_VENDORS = {"", "unknown", "missing", "mixed", "none", "nan"}
DETAIL_SCHEMA_VERSION = "consensus_family_sensitivity_detail_v1"
SUMMARY_SCHEMA_VERSION = "consensus_family_sensitivity_summary_v1"


def annotator_name(row: dict[str, Any]) -> str:
    return str(row.get("annotator") or "").strip()


def load_annotator_manifests(annotators: list[str], output_dir: Path = OUTPUT_DIR) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for annotator in sorted(set(annotators)):
        path = output_dir / f"annotation_manifest_{annotator}.json"
        status = "ok"
        vendor = "unknown"
        if not path.exists():
            status = "missing_manifest"
        else:
            try:
                manifest = json.loads(path.read_text(encoding="utf-8"))
                vendor = str(manifest.get("model_vendor") or "unknown").strip().lower()
                if vendor in UNKNOWN_VENDORS:
                    vendor = "unknown"
                    status = "missing_vendor"
            except (json.JSONDecodeError, OSError, AttributeError):
                status = "invalid_manifest"
        result[annotator] = {"model_vendor": vendor, "manifest_status": status}
    return result


def collapse_family_votes(
    rows: list[dict[str, Any]], field: str, manifests: dict[str, dict[str, str]]
) -> tuple[dict[str, str], dict[str, str], list[str]]:
    grouped: dict[str, list[Any]] = defaultdict(list)
    excluded: list[str] = []
    for row in sorted(rows, key=lambda item: annotator_name(item)):
        annotator = annotator_name(row)
        metadata = manifests.get(annotator, {"model_vendor": "unknown", "manifest_status": "missing_manifest"})
        vendor = metadata["model_vendor"]
        if metadata["manifest_status"] != "ok" or vendor in UNKNOWN_VENDORS:
            excluded.append(f"{annotator}:{metadata['manifest_status']}")
            continue
        grouped[vendor].append(row.get(field))

    family_labels: dict[str, str] = {}
    family_statuses: dict[str, str] = {}
    for vendor in sorted(grouped):
        values = [value for value in grouped[vendor] if value is not None and str(value).strip()]
        if len(values) == 1:
            family_statuses[vendor] = "single_family_member"
            family_labels[vendor] = str(values[0])
            continue
        result = vote(values)
        family_statuses[vendor] = result["status"]
        if result["status"] not in {"disagreement", "insufficient"}:
            family_labels[vendor] = str(result["label"])
    return family_labels, family_statuses, sorted(excluded)


def family_balanced_consensus(family_labels: dict[str, str]) -> dict[str, Any]:
    result = vote([family_labels[vendor] for vendor in sorted(family_labels)])
    return {
        "label": result["label"],
        "status": result["status"],
        "support": result["support"],
        "family_count": result["total"],
    }


def clean_canonical(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return None if text.lower() in {"", "nan"} else text


def build_detail_rows(
    annotation_rows: list[dict[str, Any]],
    manifests: dict[str, dict[str, str]],
    canonical: pd.DataFrame,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in annotation_rows:
        grouped[str(row.get("news_id"))].append(row)
    canonical_by_id = canonical.set_index(canonical["news_id"].astype(str), drop=False) if "news_id" in canonical else pd.DataFrame()

    detail: list[dict[str, Any]] = []
    for news_id in sorted(grouped):
        for field in CATEGORICAL_FIELDS:
            family_labels, family_statuses, excluded = collapse_family_votes(grouped[news_id], field, manifests)
            result = family_balanced_consensus(family_labels)
            canonical_label = None
            if not canonical_by_id.empty and news_id in canonical_by_id.index:
                canonical_row = canonical_by_id.loc[news_id]
                if isinstance(canonical_row, pd.DataFrame):
                    canonical_row = canonical_row.iloc[0]
                canonical_label = clean_canonical(canonical_row.get(f"consensus_{field}"))
            available = result["status"] not in {"disagreement", "insufficient"}
            comparable = available and canonical_label is not None
            detail.append({
                "news_id": news_id,
                "field": field,
                "family_consensus": result["label"],
                "family_consensus_status": result["status"],
                "family_support": result["support"],
                "eligible_family_count": result["family_count"],
                "family_labels": json.dumps(family_labels, ensure_ascii=False, sort_keys=True),
                "family_vote_statuses": json.dumps(family_statuses, ensure_ascii=False, sort_keys=True),
                "excluded_annotators": json.dumps(excluded, ensure_ascii=False),
                "canonical_consensus": canonical_label or "",
                "canonical_comparable": comparable,
                "matches_canonical": comparable and result["label"] == canonical_label,
                "artifact_schema_version": DETAIL_SCHEMA_VERSION,
            })
    return detail


def build_summary_rows(detail_rows: list[dict[str, Any]], canonical_available: bool = True) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for field in CATEGORICAL_FIELDS:
        rows = [row for row in detail_rows if row["field"] == field]
        comparable = [row for row in rows if row["canonical_comparable"]]
        matches = sum(bool(row["matches_canonical"]) for row in comparable)
        summary.append({
            "field": field,
            "total_rows": len(rows),
            "available_family_consensus": sum(row["family_consensus_status"] not in {"disagreement", "insufficient"} for row in rows),
            "family_disagreement": sum(row["family_consensus_status"] == "disagreement" for row in rows),
            "family_insufficient": sum(row["family_consensus_status"] == "insufficient" for row in rows),
            "canonical_comparable": len(comparable),
            "canonical_matches": matches,
            "canonical_mismatches": len(comparable) - matches,
            "canonical_match_rate": round(matches / len(comparable), 4) if comparable else None,
            "canonical_available": canonical_available,
            "canonical_status": "available" if canonical_available else "missing",
            "artifact_schema_version": SUMMARY_SCHEMA_VERSION,
        })
    return summary


def write_report(
    path: Path,
    summary_rows: list[dict[str, Any]],
    manifests: dict[str, dict[str, str]],
    detail_path: Path,
    summary_path: Path,
) -> None:
    provenance = [
        {"annotator": annotator, **manifests[annotator]}
        for annotator in sorted(manifests)
    ]
    lines = [
        "# Consensus family sensitivity report",
        "",
        "## Method",
        "",
        "- Annotators are grouped only when manifests provide a known `model_vendor`.",
        "- Votes within each vendor family use canonical categorical voting semantics.",
        "- Each family contributes at most one resolved vote per news item and field.",
        "- Tied family votes produce `disagreement`; fewer than two resolved family votes produce `insufficient`.",
        "- Missing, invalid, mixed, or unknown vendor metadata is excluded rather than treated as one family.",
        "- News IDs, fields, vendors, and annotators use deterministic sorted ordering.",
        "- Canonical consensus artifacts are read for comparison and never modified.",
        "",
        "## Annotator family metadata",
        "",
        markdown_table(pd.DataFrame(provenance)),
        "",
        "## Canonical comparison",
        "",
        markdown_table(pd.DataFrame(summary_rows)),
        "",
        "## Artifacts",
        "",
        f"- Detail CSV: `{detail_path}`",
        f"- Summary CSV: `{summary_path}`",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_analysis(
    label_paths: list[Path],
    canonical_path: Path,
    output_dir: Path,
    report_dir: Path,
) -> tuple[Path, Path, Path]:
    rows = load_annotation_rows(label_paths)
    annotators = sorted({annotator_name(row) for row in rows if annotator_name(row)})
    manifests = load_annotator_manifests(annotators, output_dir)
    canonical = pd.read_csv(canonical_path, encoding="utf-8-sig") if canonical_path.exists() else pd.DataFrame()
    detail_rows = build_detail_rows(rows, manifests, canonical)
    summary_rows = build_summary_rows(detail_rows, canonical_path.exists())
    detail_path = output_dir / DETAIL_OUT.name
    summary_path = output_dir / SUMMARY_OUT.name
    report_path = report_dir / REPORT_OUT.name
    write_csv(detail_path, detail_rows, [
        "news_id", "field", "family_consensus", "family_consensus_status", "family_support",
        "eligible_family_count", "family_labels", "family_vote_statuses", "excluded_annotators",
        "canonical_consensus", "canonical_comparable", "matches_canonical", "artifact_schema_version",
    ])
    write_csv(summary_path, summary_rows)
    write_report(report_path, summary_rows, manifests, detail_path, summary_path)
    return detail_path, summary_path, report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare family-balanced categorical consensus with canonical consensus.")
    parser.add_argument("--inputs", nargs="*", default=[str(path) for path in LABEL_FILES])
    parser.add_argument("--canonical", default=str(CANONICAL_CONSENSUS))
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    parser.add_argument("--report-dir", default=str(REPORT_DIR))
    args = parser.parse_args()
    ensure_dirs()
    paths = run_analysis(
        [Path(path) for path in args.inputs], Path(args.canonical), Path(args.output_dir), Path(args.report_dir)
    )
    for path in paths:
        print(f"saved {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
