from __future__ import annotations

import argparse
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (
    CATEGORICAL_FIELDS,
    CONSENSUS_SCHEMA_VERSION,
    NUMERIC_FIELDS,
    OUTPUT_DIR,
    boolish,
    ensure_dirs,
    load_schema,
    read_jsonl,
    validate_json,
    write_csv,
    write_jsonl,
)

LABEL_FILES = [OUTPUT_DIR / f"labels_annotator_{x}.jsonl" for x in ("a", "b", "c")]
JSONL_OUT = OUTPUT_DIR / "pseudo_labels_consensus.jsonl"
CSV_OUT = OUTPUT_DIR / "pseudo_labels_consensus.csv"


def load_annotation_rows(paths: list[Path]) -> list[dict[str, Any]]:
    deduped: dict[tuple[str, str], dict[str, Any]] = {}
    for path in paths:
        for row in read_jsonl(path):
            if row.get("status") != "ok":
                continue
            key = (str(row.get("news_id")), str(row.get("annotator") or path.stem))
            deduped[key] = row
    return list(deduped.values())


def vote(values: list[Any]) -> dict[str, Any]:
    clean = [value for value in values if value not in (None, "", "nan")]
    if not clean:
        return {"label": "disagreement", "status": "insufficient", "support": 0, "total": 0}
    counts = Counter(clean)
    label, support = counts.most_common(1)[0]
    total = len(clean)
    if total >= 3 and support == total:
        status = "unanimous"
    elif total >= 3 and support >= 2:
        status = "majority"
    elif total == 2 and support == 2:
        status = "agreement_2"
    elif total < 2:
        status = "insufficient"
        label = "disagreement"
    else:
        status = "disagreement"
        label = "disagreement"
    return {"label": label, "status": status, "support": support, "total": total}


def median_int(values: list[Any]) -> tuple[int | None, bool]:
    nums = []
    for value in values:
        try:
            nums.append(int(round(float(value))))
        except Exception:
            pass
    if not nums:
        return None, True
    return int(round(statistics.median(nums))), max(nums) - min(nums) >= 2


def provenance_conflicts(rows: list[dict[str, Any]]) -> list[str]:
    conflicts = []
    for field in ("input_sha256", "prompt_sha256", "schema_sha256"):
        values = {str(row.get(field)) for row in rows if row.get(field)}
        if len(values) > 1:
            conflicts.append(field)
    return conflicts


def consensus_evidence_span(rows: list[dict[str, Any]]) -> tuple[str | None, bool]:
    spans = [str(row.get("evidence_span") or "").strip() for row in rows]
    spans = [span for span in spans if span]
    if not spans:
        return None, False
    span, support = Counter(spans).most_common(1)[0]
    required = 2 if len(rows) >= 2 else 1
    return (span, True) if support >= required else (None, False)


def consensus_for(news_id: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    rows = sorted(rows, key=lambda row: str(row.get("annotator", "")))
    disagreement_fields: list[str] = []
    high_disagreement_fields: list[str] = []
    unanimous_fields: list[str] = []
    majority_fields: list[str] = []
    quality_flags: list[str] = []
    conflicts = provenance_conflicts(rows)
    if conflicts:
        quality_flags.append("provenance_conflict")

    out: dict[str, Any] = {
        "artifact_schema_version": CONSENSUS_SCHEMA_VERSION,
        "news_id": news_id,
        "ticker": rows[0].get("ticker", ""),
        "article_date": rows[0].get("article_date", ""),
        "annotator_count": len({str(row.get("annotator", "")) for row in rows}),
    }

    vote_statuses: list[str] = []
    for field in CATEGORICAL_FIELDS:
        result = vote([row.get(field) for row in rows])
        out[f"consensus_{field}"] = result["label"]
        vote_statuses.append(result["status"])
        if result["status"] == "unanimous":
            unanimous_fields.append(field)
        elif result["status"] in {"majority", "agreement_2"}:
            majority_fields.append(field)
        else:
            disagreement_fields.append(field)

    stock = vote([boolish(row.get("is_stock_relevant")) for row in rows])
    out["consensus_is_stock_relevant"] = bool(stock["label"]) if stock["status"] not in {"disagreement", "insufficient"} else None
    vote_statuses.append(stock["status"])
    if stock["status"] == "unanimous":
        unanimous_fields.append("is_stock_relevant")
    elif stock["status"] in {"majority", "agreement_2"}:
        majority_fields.append("is_stock_relevant")
    else:
        disagreement_fields.append("is_stock_relevant")

    for field in NUMERIC_FIELDS:
        value, high = median_int([row.get(field) for row in rows])
        out[f"consensus_{field}"] = value
        if high:
            high_disagreement_fields.append(field)

    span, span_agreed = consensus_evidence_span(rows)
    out["evidence_span"] = span
    if not span_agreed:
        quality_flags.append("missing_or_disputed_evidence")

    if out["annotator_count"] < 2:
        method = "insufficient_annotations"
    elif disagreement_fields:
        method = "disagreement"
    elif out["annotator_count"] >= 3 and all(status == "unanimous" for status in vote_statuses):
        method = "unanimous"
    elif out["annotator_count"] >= 3:
        method = "majority_vote"
    else:
        method = "two_annotator_agreement"

    if disagreement_fields:
        quality_flags.append("categorical_disagreement")
    if high_disagreement_fields:
        quality_flags.append("numeric_score_outlier")
    if out.get("consensus_direction") in {"mixed", "unclear", "disagreement"}:
        quality_flags.append("unclear_direction")
    if out.get("consensus_ticker_relevance") in {"unclear", "irrelevant", "disagreement"}:
        quality_flags.append("unclear_relevance")

    inherited_flags = set()
    for row in rows:
        flags = row.get("data_quality_flags") or []
        if isinstance(flags, list):
            inherited_flags.update(str(flag) for flag in flags)
    if inherited_flags & {"ticker_mismatch", "boilerplate_or_listing", "ambiguous_entity", "insufficient_evidence", "evidence_span_not_found"}:
        quality_flags.append("data_quality_issue")

    exclusion_reasons = []
    if conflicts:
        exclusion_reasons.append("provenance_conflict")
    if method in {"disagreement", "insufficient_annotations"}:
        exclusion_reasons.append("categorical_consensus_unavailable")
    if out.get("consensus_is_stock_relevant") is not True:
        exclusion_reasons.append("not_directly_stock_relevant")
    if out.get("consensus_ticker_relevance") in {"unclear", "irrelevant", "disagreement"}:
        exclusion_reasons.append("relevance_unclear_or_irrelevant")
    if out.get("consensus_materiality") in {"unclear", "disagreement"}:
        exclusion_reasons.append("materiality_unclear")
    if out.get("consensus_direction") in {"unclear", "disagreement"}:
        exclusion_reasons.append("direction_unclear")
    if span is None:
        exclusion_reasons.append("evidence_unavailable")

    out.update({
        "disagreement_fields": sorted(set(disagreement_fields)),
        "high_disagreement_fields": sorted(set(high_disagreement_fields)),
        "unanimous_fields": sorted(set(unanimous_fields)),
        "majority_fields": sorted(set(majority_fields)),
        "consensus_method": method,
        "agreement_level": "high" if method == "unanimous" else ("medium" if method in {"majority_vote", "two_annotator_agreement"} else "low"),
        "analysis_eligible": not exclusion_reasons,
        "exclusion_reasons": sorted(set(exclusion_reasons)),
        "quality_flags": sorted(set(quality_flags)) or ["none"],
        "requires_human_review": bool(quality_flags),
        "review_flags": sorted(set(quality_flags)) or ["none"],
        "reason": "Deterministic pseudo-label consensus; eligibility excludes unresolved, irrelevant, missing-evidence, and provenance-conflict rows.",
    })
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Build consensus pseudo labels from annotator outputs.")
    parser.add_argument("--inputs", nargs="*", default=[str(path) for path in LABEL_FILES])
    args = parser.parse_args()
    ensure_dirs()
    rows = load_annotation_rows([Path(path) for path in args.inputs])
    if not rows:
        write_jsonl(JSONL_OUT, [])
        schema = load_schema("pseudo_label_consensus_schema.json")
        write_csv(CSV_OUT, [], list(schema.get("required", [])))
        print("No valid annotator labels found; wrote empty consensus outputs.")
        return 0
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("news_id"))].append(row)
    schema = load_schema("pseudo_label_consensus_schema.json")
    output = []
    for news_id, group in sorted(grouped.items()):
        item = consensus_for(news_id, group)
        validate_json(item, schema)
        output.append(item)
    write_jsonl(JSONL_OUT, output)
    write_csv(CSV_OUT, output)
    print(f"saved {JSONL_OUT} rows={len(output)}")
    print(f"saved {CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
