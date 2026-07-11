from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import OUTPUT_DIR, ROOT, boolish, ensure_dirs, parse_string_list, write_jsonl

CASES = OUTPUT_DIR / "case_study_candidates.csv"
SAMPLE = ROOT / "multi_llm_evidence_extraction" / "data" / "sample_news_for_annotation.csv"
MD_OUT = OUTPUT_DIR / "evidence_cards.md"
JSONL_OUT = OUTPUT_DIR / "evidence_cards.jsonl"


def main() -> int:
    ensure_dirs()
    try:
        cases = pd.read_csv(CASES, encoding="utf-8-sig") if CASES.exists() else pd.DataFrame()
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError, UnicodeDecodeError):
        cases = pd.DataFrame()
    if cases.empty:
        MD_OUT.write_text("# Evidence cards\n\nCase studies unavailable until eligible consensus/case selection exists.\n", encoding="utf-8")
        write_jsonl(JSONL_OUT, [])
        print("wrote pending evidence cards")
        return 0
    sample = pd.read_csv(SAMPLE, encoding="utf-8-sig") if SAMPLE.exists() else pd.DataFrame()
    df = cases.merge(sample, on=["news_id", "ticker"], how="left", suffixes=("", "_sample")) if not sample.empty else cases
    rows = []
    lines = ["# Evidence cards", "", "> Research support only. Not buy/sell recommendation.", ""]
    for index, row in df.iterrows():
        claim_id = f"C{index + 1:03d}"
        evidence = row.get("evidence_span")
        if pd.isna(evidence) or not str(evidence).strip():
            evidence = None
        quality_flags = parse_string_list(row.get("quality_flags", row.get("review_flags", "")))
        exclusion_reasons = parse_string_list(row.get("exclusion_reasons", ""))
        adjusted = pd.to_numeric(pd.Series([row.get("market_adjusted_return")]), errors="coerce").iloc[0]
        card = {
            "news_id": row.get("news_id"),
            "ticker": row.get("ticker"),
            "article_date": row.get("article_date", row.get("date", "")),
            "effective_date": row.get("effective_date", None),
            "case_pattern": row.get("case_pattern", ""),
            "claim_id": claim_id,
            "claim_text": row.get("reason", "Deterministic semantic consensus case."),
            "relevance": row.get("consensus_ticker_relevance", ""),
            "materiality": row.get("consensus_materiality", ""),
            "direction": row.get("consensus_direction", ""),
            "evidence_span": evidence,
            "analysis_eligible": boolish(row.get("analysis_eligible")),
            "quality_flags": quality_flags,
            "exclusion_reasons": exclusion_reasons,
            "market_adjusted_return_T20": None if pd.isna(adjusted) else float(adjusted),
            "limitation": "Pseudo-label evidence card with post-hoc adjusted outcome; requires human interpretation and is not investment advice.",
        }
        rows.append(card)
        lines += [
            f"## {claim_id} — {card['ticker']} {card['article_date']}",
            "",
            f"- Case pattern: `{card['case_pattern']}`",
            f"- Relevance/materiality/direction: `{card['relevance']}` / `{card['materiality']}` / `{card['direction']}`",
            f"- Evidence span: {card['evidence_span'] or 'MISSING — requires review'}",
            f"- T+20 VNINDEX-adjusted return: {card['market_adjusted_return_T20'] if card['market_adjusted_return_T20'] is not None else 'unavailable'}",
            f"- Claim: {card['claim_text']}",
            f"- Quality flags: {', '.join(card['quality_flags']) or 'none'}",
            f"- Exclusion reasons: {', '.join(card['exclusion_reasons']) or 'none'}",
            "- Limitation: post-hoc research support only, not recommendation.",
            "",
        ]
    write_jsonl(JSONL_OUT, rows)
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"saved {MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
