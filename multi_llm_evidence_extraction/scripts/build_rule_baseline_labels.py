from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import OUTPUT_DIR, ROOT, ensure_dirs, write_csv, write_jsonl
from pipeline.task9_kw_features import compute_raw_counts

SAMPLE = ROOT / "multi_llm_evidence_extraction" / "data" / "sample_news_for_annotation.csv"
KW_GROUPS = ROOT / "config" / "keywords_by_group.json"
JSONL_OUT = OUTPUT_DIR / "rule_labels.jsonl"
CSV_OUT = OUTPUT_DIR / "rule_labels.csv"

EVENT_MAP = {
    "A": "earnings",
    "B": "dividend",
    "C": "debt",
    "D": "project",
    "E": "legal",
    "F": "other",
}
MARKET_TERMS = ["vn-index", "vnindex", "thị trường", "lãi suất", "vĩ mô", "ngành", "vốn hóa", "thanh khoản"]


def load_groups() -> dict[str, Any]:
    return json.loads(KW_GROUPS.read_text(encoding="utf-8")) if KW_GROUPS.exists() else {}


def text(row: dict[str, Any]) -> str:
    return " ".join(str(row.get(c, "")) for c in ["title", "description", "article_summary", "full_text"]).lower()


def label_row(row: dict[str, Any], groups: dict[str, Any]) -> dict[str, Any]:
    t = text(row)
    hits: dict[str, int] = {}
    pos = neg = neu = 0
    for gid, spec in groups.items():
        kws = []
        for direction in ("positive", "negative", "neutral"):
            vals = spec.get(direction) or [] if isinstance(spec, dict) else []
            count = sum(compute_raw_counts(t, [kw]).get(kw, 0) for kw in vals)
            if direction == "positive":
                pos += count
            elif direction == "negative":
                neg += count
            else:
                neu += count
            kws.extend(vals)
        group_count = sum(compute_raw_counts(t, kws).values()) if kws else 0
        if group_count:
            hits[gid] = group_count
    if pos > neg:
        sentiment, direction = "positive", "support"
    elif neg > pos:
        sentiment, direction = "negative", "risk"
    elif neu or hits:
        sentiment, direction = "neutral", "neutral"
    else:
        sentiment, direction = "unclear", "unclear"
    event_type = "unclear"
    if hits:
        event_type = EVENT_MAP.get(max(hits, key=hits.get), "other")
    market = any(term in t for term in MARKET_TERMS)
    match_conf = str(row.get("match_confidence", "")).lower()
    if match_conf in {"none", "low"} or str(row.get("ticker", "")).upper() in {"", "UNKNOWN", "NAN"}:
        relevance = "unclear"
    elif market and not hits:
        relevance = "market_wide"
    else:
        relevance = "direct" if hits else "unclear"
    total_hits = pos + neg + neu + sum(hits.values())
    if total_hits >= 4 and relevance == "direct" and event_type in {"earnings", "dividend", "debt", "legal", "capital"}:
        materiality = "high"
    elif total_hits >= 2:
        materiality = "medium"
    elif total_hits >= 1:
        materiality = "low"
    else:
        materiality = "unclear"
    return {
        "news_id": row.get("news_id", ""),
        "ticker": row.get("ticker", ""),
        "article_date": str(row.get("date", ""))[:10],
        "rule_sentiment": sentiment,
        "rule_direction": direction,
        "rule_event_type": event_type,
        "rule_materiality": materiality,
        "rule_relevance": relevance,
        "rule_positive_hits": pos,
        "rule_negative_hits": neg,
        "rule_neutral_hits": neu,
        "rule_total_hits": total_hits,
        "rule_matched_groups": ";".join(sorted(hits)),
    }


def main() -> int:
    ensure_dirs()
    if not SAMPLE.exists():
        raise FileNotFoundError(f"Missing sample: {SAMPLE}")
    df = pd.read_csv(SAMPLE, encoding="utf-8-sig")
    groups = load_groups()
    rows = [label_row(dict(r), groups) for _, r in df.iterrows()]
    write_jsonl(JSONL_OUT, rows)
    write_csv(CSV_OUT, rows)
    print(f"saved {CSV_OUT} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
