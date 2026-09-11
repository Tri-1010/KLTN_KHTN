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
KEY_COLUMNS = ["news_id", "ticker"]
HUMAN_COLUMNS = [
    "reviewer_id", "reviewed_at", "review_source", "review_status",
    "human_relevance_label", "human_materiality_label", "human_direction_label",
    "human_event_type_label", "human_time_horizon_label", "human_evidence_span_label",
    "human_error_category", "human_review_notes",
    "human_relevance_ok", "human_materiality_ok", "human_direction_ok",
    "human_event_type_ok", "human_evidence_span_ok", "human_error_notes",
]


def _nonempty(value: object) -> bool:
    return pd.notna(value) and str(value).strip() != ""


def preserve_human_values(selected: pd.DataFrame, previous: pd.DataFrame) -> pd.DataFrame:
    out = selected.copy()
    for column in HUMAN_COLUMNS:
        if column not in out:
            out[column] = ""
    if previous.empty or not set(KEY_COLUMNS).issubset(previous.columns):
        return out
    normalized_previous = previous.copy()
    normalized_out = out.copy()
    for column in KEY_COLUMNS:
        normalized_previous[column] = normalized_previous[column].astype(str)
        normalized_out[column] = normalized_out[column].astype(str)
    old = normalized_previous.drop_duplicates(KEY_COLUMNS, keep="last").set_index(KEY_COLUMNS)
    for index, row in normalized_out.iterrows():
        key = tuple(row[column] for column in KEY_COLUMNS)
        if key not in old.index:
            continue
        prior = old.loc[key]
        if isinstance(prior, pd.DataFrame):
            prior = prior.iloc[-1]
        for column in HUMAN_COLUMNS:
            if column in prior and _nonempty(prior[column]):
                out.at[index, column] = prior[column]
    return out


def select_rows(consensus: pd.DataFrame, sample: pd.DataFrame, n: int) -> pd.DataFrame:
    frame = consensus.merge(sample, on=KEY_COLUMNS, how="left", suffixes=("", "_sample"))
    picks = []
    masks = [
        frame.get("requires_human_review", pd.Series(False, index=frame.index)).astype(str).str.lower().isin(["true", "1"]),
        frame.get("consensus_materiality", pd.Series("", index=frame.index)).eq("high"),
        frame.get("consensus_direction", pd.Series("", index=frame.index)).isin(["mixed", "unclear", "disagreement"]),
    ]
    for mask in masks:
        part = frame[mask]
        if not part.empty:
            picks.append(part.head(max(1, n // 4)))
    if not frame.empty:
        picks.append(frame.sample(n=min(max(1, n // 4), len(frame)), random_state=42))
    if not picks:
        return frame.head(0)
    return pd.concat(picks, ignore_index=True).drop_duplicates(KEY_COLUMNS).head(n)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build manual sanity-check sheet without overwriting human work.")
    parser.add_argument("--n", type=int, default=30)
    args = parser.parse_args()
    ensure_dirs()
    previous = pd.DataFrame()
    if OUT.exists():
        try:
            previous = pd.read_csv(OUT, encoding="utf-8-sig")
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            previous = pd.DataFrame()
    if not CONSENSUS.exists():
        TEMPLATE.write_text("# Manual sanity check template\n\nConsensus labels unavailable.\n", encoding="utf-8")
        if not OUT.exists():
            pd.DataFrame(columns=HUMAN_COLUMNS).to_csv(OUT, index=False, encoding="utf-8-sig")
        return 0
    consensus = pd.read_csv(CONSENSUS, encoding="utf-8-sig")
    if consensus.empty:
        return 0
    sample = pd.read_csv(SAMPLE, encoding="utf-8-sig") if SAMPLE.exists() else pd.DataFrame(columns=KEY_COLUMNS)
    selected = select_rows(consensus, sample, args.n)
    out = preserve_human_values(selected, previous)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")
    TEMPLATE.write_text(
        "# Manual validation template\n\n"
        "Human-authored QC only; not full ground truth. Fill reviewer metadata, categorical labels, legacy ok/not-ok checks, and notes in `data/manual_sanity_check_sample.csv`. Regeneration preserves non-empty human fields by `(news_id, ticker)`.\n",
        encoding="utf-8",
    )
    print(f"saved {OUT} rows={len(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
