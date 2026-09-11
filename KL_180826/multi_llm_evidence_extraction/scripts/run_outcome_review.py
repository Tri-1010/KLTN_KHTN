from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import OUTPUT_DIR, REPORT_DIR, ensure_dirs, load_schema, markdown_table, validate_json, write_csv

CARDS = OUTPUT_DIR / "evidence_cards.jsonl"
AUDIT = OUTPUT_DIR / "event_window_outcomes.csv"
OUT = OUTPUT_DIR / "outcome_review_labels.csv"
REPORT = REPORT_DIR / "outcome_review_report.md"
CASE_REPORT = REPORT_DIR / "case_studies.md"

DIRECTION_FLAT_BAND = 0.0
SALIENCE_ABSOLUTE_RETURN = 0.05
THRESHOLD_METADATA = {
    "direction_flat_band": DIRECTION_FLAT_BAND,
    "salience_absolute_return": SALIENCE_ABSOLUTE_RETURN,
    "return_unit": "decimal_return",
}
VERSION_METADATA = {
    "schema_version": "outcome_review_v2",
    "label_rule_version": "legacy_outcome_label_v1",
}


def label(direction: str, ret: float | None) -> str:
    """Preserve legacy outcome_label behavior."""
    if ret is None or pd.isna(ret):
        return "unresolved"
    if direction == "support" and ret > 0:
        return "confirmed"
    if direction == "risk" and ret < 0:
        return "confirmed"
    if direction in {"support", "risk"}:
        return "contradicted"
    if direction in {"neutral", "mixed", "unclear"}:
        return "not_price_relevant"
    return "unresolved"


def outcome_direction(direction: str, ret: float | None) -> str:
    if ret is None or pd.isna(ret):
        return "unavailable"
    if abs(ret) <= DIRECTION_FLAT_BAND:
        return "flat"
    if direction == "support":
        return "aligned" if ret > 0 else "opposed"
    if direction == "risk":
        return "aligned" if ret < 0 else "opposed"
    return "unavailable"


def outcome_salience(ret: float | None) -> str:
    if ret is None or pd.isna(ret):
        return "unavailable"
    return "salient" if abs(ret) >= SALIENCE_ABSOLUTE_RETURN else "not_salient"


def main() -> int:
    ensure_dirs()
    if not AUDIT.exists():
        pd.DataFrame().to_csv(OUT, index=False, encoding="utf-8-sig")
        REPORT.write_text("# Outcome review report\n\nEvent-window outcomes unavailable; outcome review pending.\n", encoding="utf-8")
        CASE_REPORT.write_text("# Case studies\n\nPending semantic labels and event-window outcomes.\n", encoding="utf-8")
        print("wrote pending outcome review")
        return 0
    try:
        audit = pd.read_csv(AUDIT, encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        audit = pd.DataFrame()
    if audit.empty:
        pd.DataFrame().to_csv(OUT, index=False, encoding="utf-8-sig")
        REPORT.write_text("# Outcome review report\n\nEvent-window outcomes unavailable; outcome review pending.\n", encoding="utf-8")
        CASE_REPORT.write_text("# Case studies\n\nPending semantic labels and event-window outcomes.\n", encoding="utf-8")
        print("wrote pending outcome review")
        return 0
    if "window" not in audit:
        t20 = pd.DataFrame()
    else:
        t20 = audit[audit["window"].eq("T+20")].copy()
    rows = []
    for _, r in t20.iterrows():
        adjusted = r.get("market_adjusted_return")
        direction = str(r.get("direction"))
        rows.append({
            "news_id": r.get("news_id"),
            "ticker": r.get("ticker"),
            "event_date": r.get("event_date"),
            "claim_id": f"{r.get('news_id')}_T20",
            "claim_text": f"Semantic direction={direction} for event {r.get('event_type')}",
            "claim_direction": direction,
            "review_window": "T+20",
            "raw_return": r.get("raw_return"),
            "benchmark_return": r.get("benchmark_return"),
            "excess_return": adjusted,
            "abnormal_volume": r.get("abnormal_volume"),
            "volatility": r.get("volatility"),
            "max_adverse_move": r.get("max_adverse_move"),
            "outcome_direction": outcome_direction(direction, adjusted),
            "outcome_salience": outcome_salience(adjusted),
            "attribution_status": "unassessed",
            "outcome_label": label(direction, adjusted),
            "threshold_metadata": THRESHOLD_METADATA.copy(),
            "version_metadata": VERSION_METADATA.copy(),
            "confounders": ["residual_market_or_company_events_not_modeled"],
            "review_reason": "Rule-based post-hoc label from T+20 VNINDEX-adjusted return; residual confounding remains unmeasured.",
            "requires_follow_up": True,
        })
    schema = load_schema("outcome_review_schema.json")
    for row in rows:
        validate_json(row, schema)
    write_csv(OUT, rows)
    df = pd.DataFrame(rows)
    lines = [
        "# Outcome review report", "",
        "Post-hoc external-consistency audit only. Not used in annotation prompts and not semantic ground truth.", "",
        "`outcome_label` is retained for legacy compatibility; interpretation uses direction alignment, salience, and unassessed attribution separately.", "",
    ]
    if not df.empty:
        lines += [
            "## Direction alignment", "", markdown_table(df["outcome_direction"].value_counts()), "",
            "## Market-response salience", "", markdown_table(df["outcome_salience"].value_counts()), "",
            "## Attribution status", "", markdown_table(df["attribution_status"].value_counts()), "",
            "## Legacy outcome labels", "", markdown_table(df["outcome_label"].value_counts()), "",
        ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    CASE_REPORT.write_text("# Case studies\n\nSee `outputs/evidence_cards.md` and `outputs/outcome_review_labels.csv` for selected cases and post-hoc labels.\n", encoding="utf-8")
    print(f"saved {OUT} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
