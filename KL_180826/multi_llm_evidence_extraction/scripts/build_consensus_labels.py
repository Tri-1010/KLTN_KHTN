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
    sha256_file,
    utc_now,
    validate_json,
    write_csv,
    write_json,
    write_jsonl,
)

LABEL_FILES = [OUTPUT_DIR / f"labels_annotator_{name}.jsonl" for name in ("a", "b", "c")]
JSONL_OUT = OUTPUT_DIR / "pseudo_labels_consensus.jsonl"
CSV_OUT = OUTPUT_DIR / "pseudo_labels_consensus.csv"


def validate_strict_expansion_rows(paths: list[Path], expected_sample_path: Path, expected_annotators: tuple[str, ...] = ("a", "b", "c")) -> list[dict[str, Any]]:
    rows = [row for path in paths for row in read_jsonl(path)]
    if not rows:
        raise ValueError("strict expansion consensus requires annotation rows")
    sample = pd.read_csv(expected_sample_path, encoding="utf-8-sig")
    if not {"news_id", "ticker"}.issubset(sample.columns):
        raise ValueError("strict expansion expected sample missing news_id/ticker")
    sample = sample[["news_id", "ticker"]].copy()
    sample["news_id"] = sample["news_id"].fillna("").astype(str).str.strip()
    sample["ticker"] = sample["ticker"].fillna("").astype(str).str.upper().str.strip()
    if sample.eq("").any().any() or sample.duplicated(["news_id", "ticker"]).any():
        raise ValueError("strict expansion expected sample keys must be unique and nonempty")
    expected_keys = set(map(tuple, sample[["news_id", "ticker"]].to_numpy()))
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row.get("news_id", "")).strip(), str(row.get("ticker", "")).upper().strip())].append(row)
    if set(grouped) != expected_keys:
        raise ValueError(f"strict expansion sample coverage mismatch: missing={len(expected_keys - set(grouped))} unexpected={len(set(grouped) - expected_keys)}")
    required = {"input_sha256", "content_hash", "prompt_sha256", "schema_sha256", "requested_model", "provider"}
    expected_set = set(expected_annotators)
    for key, group in grouped.items():
        annotators = [str(row.get("annotator", "")) for row in group]
        if set(annotators) != expected_set or len(annotators) != len(expected_set):
            raise ValueError(f"strict expansion annotator coverage failed for {key}: {annotators}")
        for row in group:
            if row.get("status") != "ok" or row.get("terminal") is not True:
                raise ValueError(f"strict expansion terminal successful coverage failed for {key}")
            missing = sorted(field for field in required if not str(row.get(field, "")).strip())
            if missing:
                raise ValueError(f"strict expansion provenance incomplete for {key}: {missing}")
        if provenance_conflicts(group):
            raise ValueError(f"strict expansion provenance conflict for {key}")
    return rows


def load_annotation_rows(paths: list[Path]) -> list[dict[str, Any]]:
    deduped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for path in paths:
        for row in read_jsonl(path):
            if row.get("status") == "ok":
                deduped[(str(row.get("news_id")), str(row.get("ticker", "")).upper(), str(row.get("annotator") or path.stem))] = row
    return list(deduped.values())


def vote(values: list[Any]) -> dict[str, Any]:
    clean = [value for value in values if value not in (None, "", "nan")]
    if not clean:
        return {"label": "disagreement", "status": "insufficient", "support": 0, "total": 0}
    label, support = Counter(clean).most_common(1)[0]
    total = len(clean)
    if total >= 3 and support == total:
        status = "unanimous"
    elif total >= 3 and support >= 2:
        status = "majority"
    elif total == 2 and support == 2:
        status = "agreement_2"
    elif total < 2:
        status, label = "insufficient", "disagreement"
    else:
        status, label = "disagreement", "disagreement"
    return {"label": label, "status": status, "support": support, "total": total}


def median_int(values: list[Any]) -> tuple[int | None, bool]:
    numbers = []
    for value in values:
        try:
            numbers.append(int(round(float(value))))
        except Exception:
            pass
    if not numbers:
        return None, True
    return int(round(statistics.median(numbers))), max(numbers) - min(numbers) >= 2


def provenance_conflicts(rows: list[dict[str, Any]]) -> list[str]:
    return [field for field in ("input_sha256", "content_hash", "prompt_sha256", "schema_sha256") if len({str(row.get(field)) for row in rows if row.get(field)}) > 1]


def consensus_evidence_span(rows: list[dict[str, Any]]) -> tuple[str | None, bool]:
    spans = [str(row.get("evidence_span") or "").strip() for row in rows]
    spans = [span for span in spans if span]
    if not spans:
        return None, False
    span, support = Counter(spans).most_common(1)[0]
    return (span, True) if support >= (2 if len(rows) >= 2 else 1) else (None, False)


def consensus_for(news_id: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    rows = sorted(rows, key=lambda row: str(row.get("annotator", "")))
    disagreement, high_disagreement, unanimous, majority, flags = [], [], [], [], []
    conflicts = provenance_conflicts(rows)
    if conflicts:
        flags.append("provenance_conflict")
    content_hashes = {str(row.get("content_hash", "")).strip() for row in rows if str(row.get("content_hash", "")).strip()}
    if len(content_hashes) != 1:
        raise ValueError(f"consensus content_hash provenance conflict for {news_id}")
    out: dict[str, Any] = {"artifact_schema_version": CONSENSUS_SCHEMA_VERSION, "news_id": news_id, "ticker": rows[0].get("ticker", ""), "article_date": rows[0].get("article_date", ""), "content_hash": next(iter(content_hashes)), "annotator_count": len({str(row.get("annotator", "")) for row in rows})}
    vote_statuses = []
    for field in CATEGORICAL_FIELDS:
        result = vote([row.get(field) for row in rows])
        out[f"consensus_{field}"] = result["label"]
        vote_statuses.append(result["status"])
        if result["status"] == "unanimous": unanimous.append(field)
        elif result["status"] in {"majority", "agreement_2"}: majority.append(field)
        else: disagreement.append(field)
    stock = vote([boolish(row.get("is_stock_relevant")) for row in rows])
    out["consensus_is_stock_relevant"] = bool(stock["label"]) if stock["status"] not in {"disagreement", "insufficient"} else None
    vote_statuses.append(stock["status"])
    if stock["status"] == "unanimous": unanimous.append("is_stock_relevant")
    elif stock["status"] in {"majority", "agreement_2"}: majority.append("is_stock_relevant")
    else: disagreement.append("is_stock_relevant")
    for field in NUMERIC_FIELDS:
        value, high = median_int([row.get(field) for row in rows])
        out[f"consensus_{field}"] = value
        if high: high_disagreement.append(field)
    span, agreed = consensus_evidence_span(rows)
    out["evidence_span"] = span
    if not agreed: flags.append("missing_or_disputed_evidence")
    if out["annotator_count"] < 2: method = "insufficient_annotations"
    elif disagreement: method = "disagreement"
    elif out["annotator_count"] >= 3 and all(status == "unanimous" for status in vote_statuses): method = "unanimous"
    elif out["annotator_count"] >= 3: method = "majority_vote"
    else: method = "two_annotator_agreement"
    if disagreement: flags.append("categorical_disagreement")
    if high_disagreement: flags.append("numeric_score_outlier")
    if out.get("consensus_direction") in {"mixed", "unclear", "disagreement"}: flags.append("unclear_direction")
    if out.get("consensus_ticker_relevance") in {"unclear", "irrelevant", "disagreement"}: flags.append("unclear_relevance")
    inherited = {str(flag) for row in rows for flag in (row.get("data_quality_flags") or []) if isinstance(row.get("data_quality_flags") or [], list)}
    if inherited & {"ticker_mismatch", "boilerplate_or_listing", "ambiguous_entity", "insufficient_evidence", "evidence_span_not_found"}: flags.append("data_quality_issue")
    exclusion = []
    if conflicts: exclusion.append("provenance_conflict")
    if method in {"disagreement", "insufficient_annotations"}: exclusion.append("categorical_consensus_unavailable")
    if out.get("consensus_is_stock_relevant") is not True: exclusion.append("not_directly_stock_relevant")
    if out.get("consensus_ticker_relevance") in {"unclear", "irrelevant", "disagreement"}: exclusion.append("relevance_unclear_or_irrelevant")
    if out.get("consensus_materiality") in {"unclear", "disagreement"}: exclusion.append("materiality_unclear")
    if out.get("consensus_direction") in {"unclear", "disagreement"}: exclusion.append("direction_unclear")
    if span is None: exclusion.append("evidence_unavailable")
    out.update({"disagreement_fields": sorted(set(disagreement)), "high_disagreement_fields": sorted(set(high_disagreement)), "unanimous_fields": sorted(set(unanimous)), "majority_fields": sorted(set(majority)), "consensus_method": method, "agreement_level": "high" if method == "unanimous" else "medium" if method in {"majority_vote", "two_annotator_agreement"} else "low", "analysis_eligible": not exclusion, "exclusion_reasons": sorted(set(exclusion)), "quality_flags": sorted(set(flags)) or ["none"], "requires_human_review": bool(flags), "review_flags": sorted(set(flags)) or ["none"], "reason": "Deterministic pseudo-label consensus; eligibility excludes unresolved, irrelevant, missing-evidence, and provenance-conflict rows."})
    return out


def _strict_consensus_provenance(inputs: list[Path], expected_sample: Path, output_csv: Path, annotators: list[str]) -> dict[str, Any]:
    return {"artifact_schema_version": "v6_confirmation_annotation_consensus_v1", "status": "completed", "generated_at_utc": utc_now(), "strict_expansion": True, "annotators": list(annotators), "expected_sample": {"path": str(expected_sample), "sha256": sha256_file(expected_sample)}, "inputs": [{"path": str(path), "sha256": sha256_file(path)} for path in inputs], "consensus_csv": {"path": str(output_csv), "sha256": sha256_file(output_csv)}}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build consensus pseudo labels from annotator outputs.")
    parser.add_argument("--inputs", nargs="*", default=[str(path) for path in LABEL_FILES])
    parser.add_argument("--jsonl-output", type=Path, default=JSONL_OUT)
    parser.add_argument("--csv-output", type=Path, default=CSV_OUT)
    parser.add_argument("--strict-expansion", action="store_true")
    parser.add_argument("--expected-sample", type=Path)
    parser.add_argument("--expected-annotators", nargs="+", default=["a", "b", "c"])
    parser.add_argument("--confirmation-provenance-output", type=Path, default=None)
    args = parser.parse_args()
    ensure_dirs()
    input_paths = [Path(path) for path in args.inputs]
    if args.strict_expansion:
        if args.expected_sample is None:
            parser.error("--strict-expansion requires --expected-sample")
        rows = [row for row in validate_strict_expansion_rows(input_paths, args.expected_sample, tuple(args.expected_annotators)) if row.get("status") == "ok"]
    else:
        if args.confirmation_provenance_output is not None:
            parser.error("--confirmation-provenance-output requires --strict-expansion")
        rows = load_annotation_rows(input_paths)
    if args.confirmation_provenance_output is not None:
        provenance = args.confirmation_provenance_output
        destinations = [args.jsonl_output, args.csv_output, provenance]
        existing = [str(path) for path in destinations if path.exists()]
        if existing:
            raise FileExistsError(f"confirmation consensus destinations already exist: {existing}")
    if not rows:
        write_jsonl(args.jsonl_output, [])
        write_csv(args.csv_output, [], list(load_schema("pseudo_label_consensus_schema.json").get("required", [])))
        if args.confirmation_provenance_output is not None:
            write_json(
                args.confirmation_provenance_output,
                _strict_consensus_provenance(input_paths, args.expected_sample, args.csv_output, args.expected_annotators),
            )
            print(f"saved {args.confirmation_provenance_output}")
        print("No valid annotator labels found; wrote empty consensus outputs.")
        return 0
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row.get("news_id", "")), str(row.get("ticker", "")).upper())].append(row)
    schema = load_schema("pseudo_label_consensus_schema.json")
    output = []
    for (news_id, _ticker), group in sorted(grouped.items()):
        item = consensus_for(news_id, group)
        validate_json(item, schema)
        output.append(item)
    write_jsonl(args.jsonl_output, output)
    write_csv(args.csv_output, output)
    if args.confirmation_provenance_output is not None:
        provenance = args.confirmation_provenance_output
        write_json(provenance, _strict_consensus_provenance(input_paths, args.expected_sample, args.csv_output, args.expected_annotators))
        print(f"saved {provenance}")
    print(f"saved {args.jsonl_output} rows={len(output)}")
    print(f"saved {args.csv_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
