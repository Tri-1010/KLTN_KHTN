from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import DATA_DIR, OUTPUT_DIR, REPORT_DIR, ensure_dirs

CONSENSUS = OUTPUT_DIR / "pseudo_labels_consensus.csv"
SAMPLE = DATA_DIR / "sample_news_for_annotation.csv"
OUT = DATA_DIR / "manual_sanity_check_sample.csv"
TEMPLATE = REPORT_DIR / "manual_sanity_check_template.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build manual sanity check sheet.")
    parser.add_argument("--n", type=int, default=30)
    args = parser.parse_args()
    ensure_dirs()
    if not CONSENSUS.exists() or pd.read_csv(CONSENSUS, encoding="utf-8-sig").empty:
        TEMPLATE.write_text("# Manual sanity check template\n\nConsensus labels not available yet. Run live annotation and consensus first.\n", encoding="utf-8")
        pd.DataFrame().to_csv(OUT, index=False, encoding="utf-8-sig")
        print("Consensus labels unavailable; wrote pending template.")
        return 0
    cons = pd.read_csv(CONSENSUS, encoding="utf-8-sig")
    sample = pd.read_csv(SAMPLE, encoding="utf-8-sig") if SAMPLE.exists() else pd.DataFrame()
    df = cons.merge(sample, on=["news_id", "ticker"], how="left", suffixes=("", "_sample"))
    picks = []
    for mask in [
        df.get("requires_human_review", pd.Series(False, index=df.index)).astype(str).str.lower().isin(["true", "1"]),
        df.get("consensus_materiality", pd.Series("", index=df.index)).eq("high"),
        df.get("consensus_direction", pd.Series("", index=df.index)).isin(["mixed", "unclear", "disagreement"]),
    ]:
        part = df[mask]
        if not part.empty:
            picks.append(part.head(max(1, args.n // 4)))
    picks.append(df.sample(n=min(max(1, args.n // 4), len(df)), random_state=42))
    out = pd.concat(picks, ignore_index=True).drop_duplicates("news_id").head(args.n)
    for col in ["human_relevance_ok", "human_materiality_ok", "human_direction_ok", "human_event_type_ok", "human_evidence_span_ok", "human_error_notes"]:
        out[col] = ""
    out.to_csv(OUT, index=False, encoding="utf-8-sig")
    TEMPLATE.write_text(
        "# Manual sanity check template\n\n"
        "This is small quality-control check, not full human ground truth. Fill columns in `data/manual_sanity_check_sample.csv`: relevance/materiality/direction/event_type/evidence_span ok plus notes.\n",
        encoding="utf-8",
    )
    print(f"saved {OUT} rows={len(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
