from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import DATA_DIR, REPORT_DIR, ensure_dirs

INPUT = DATA_DIR / "manual_sanity_check_sample.csv"
REPORT = REPORT_DIR / "manual_sanity_check_report.md"
CHECK_COLS = ["human_relevance_ok", "human_materiality_ok", "human_direction_ok", "human_event_type_ok", "human_evidence_span_ok"]


def main() -> int:
    ensure_dirs()
    lines = ["# Manual sanity check report", "", "This is a small quality-control check, not full human ground truth.", ""]
    if not INPUT.exists():
        lines.append("Manual review sheet is empty or unavailable. Fill it after consensus labels exist.")
        REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"saved {REPORT}")
        return 0
    try:
        df = pd.read_csv(INPUT, encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        df = pd.DataFrame()
    if df.empty:
        lines.append("Manual review sheet is empty or unavailable. Fill it after consensus labels exist.")
        REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"saved {REPORT}")
        return 0
    filled = df[CHECK_COLS].replace("", pd.NA).notna().any(axis=1) if all(c in df for c in CHECK_COLS) else pd.Series(False, index=df.index)
    lines.append(f"- Rows in sheet: {len(df)}")
    lines.append(f"- Rows with any manual check filled: {int(filled.sum())}")
    for col in CHECK_COLS:
        if col in df:
            yes = df[col].astype(str).str.lower().isin(["1", "true", "yes", "y", "ok", "đúng", "dung"]).sum()
            no = df[col].astype(str).str.lower().isin(["0", "false", "no", "n", "sai"]).sum()
            lines.append(f"- {col}: ok={int(yes)}, not_ok={int(no)}")
    if "human_error_notes" in df:
        notes = df["human_error_notes"].dropna().astype(str)
        notes = notes[notes.str.strip().ne("")].head(20)
        if not notes.empty:
            lines += ["", "## Error notes", ""] + [f"- {n}" for n in notes]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
