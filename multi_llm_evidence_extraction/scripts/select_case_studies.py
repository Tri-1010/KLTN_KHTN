from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import OUTPUT_DIR, ensure_dirs

CONS = OUTPUT_DIR / "pseudo_labels_consensus.csv"
RULE = OUTPUT_DIR / "rule_labels.csv"
AUDIT = OUTPUT_DIR / "event_window_outcomes.csv"
OUT = OUTPUT_DIR / "case_study_candidates.csv"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError, UnicodeDecodeError):
        return pd.DataFrame()


def main() -> int:
    ensure_dirs()
    cons = read_csv(CONS)
    if cons.empty:
        pd.DataFrame().to_csv(OUT, index=False, encoding="utf-8-sig")
        print("Consensus unavailable; wrote empty case candidates.")
        return 0
    if "analysis_eligible" in cons:
        eligible = cons["analysis_eligible"].astype(str).str.lower().isin(["true", "1"])
        cons = cons[eligible].copy()
    rule = read_csv(RULE)
    df = cons.merge(rule, on=["news_id", "ticker"], how="left") if not rule.empty else cons
    audit = read_csv(AUDIT)
    if not audit.empty and {"news_id", "ticker", "window", "market_adjusted_return"}.issubset(audit.columns):
        columns = ["news_id", "ticker", "market_adjusted_return"]
        if "effective_date" in audit:
            columns.append("effective_date")
        t20 = audit[audit["window"].eq("T+20")][columns].drop_duplicates(["news_id", "ticker"])
        t20["market_adjusted_return"] = pd.to_numeric(t20["market_adjusted_return"], errors="coerce")
        df = df.merge(t20, on=["news_id", "ticker"], how="left")
    candidates = []
    rule_direction = df["rule_direction"] if "rule_direction" in df else pd.Series("", index=df.index)
    rule_total_hits = pd.to_numeric(df["rule_total_hits"], errors="coerce") if "rule_total_hits" in df else pd.Series(0, index=df.index)
    materiality = df["consensus_materiality"] if "consensus_materiality" in df else pd.Series("", index=df.index)
    direction = df["consensus_direction"] if "consensus_direction" in df else pd.Series("", index=df.index)
    adjusted = pd.to_numeric(df["market_adjusted_return"], errors="coerce") if "market_adjusted_return" in df else pd.Series(float("nan"), index=df.index)
    patterns = [
        ("keyword_positive_semantic_low", rule_direction.eq("support") & materiality.eq("low")),
        ("keyword_missed_high_materiality", rule_total_hits.fillna(0).eq(0) & materiality.eq("high")),
        ("support_outcome_contradicted", direction.eq("support") & adjusted.lt(0)),
        ("risk_outcome_confirmed", direction.eq("risk") & adjusted.lt(0)),
    ]
    for name, mask in patterns:
        part = df[mask].copy()
        if "market_adjusted_return" in part:
            part = part.assign(_magnitude=part["market_adjusted_return"].abs()).sort_values("_magnitude", ascending=False).drop(columns="_magnitude")
        part = part.head(2)
        part["case_pattern"] = name
        candidates.append(part)
    out = pd.concat(candidates, ignore_index=True).drop_duplicates("news_id").head(5) if candidates else pd.DataFrame()
    out.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"saved {OUT} rows={len(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
