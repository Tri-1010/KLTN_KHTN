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
LABEL_COLS = ["human_relevance_label", "human_materiality_label", "human_direction_label", "human_event_type_label", "human_time_horizon_label", "human_evidence_span_label"]
REVIEWER_COLS = ["reviewer_id", "reviewed_at", "review_source", "review_status"]
TRUTHY = {"1", "true", "yes", "y", "ok", "đúng", "dung"}
FALSEY = {"0", "false", "no", "n", "sai"}


def _text(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    available = [column for column in columns if column in frame]
    if not available:
        return pd.DataFrame(index=frame.index)
    return frame[available].fillna("").astype(str).apply(lambda col: col.str.strip())


def summarize(frame: pd.DataFrame) -> dict[str, object]:
    checks = _text(frame, CHECK_COLS).apply(lambda col: col.str.lower())
    labels = _text(frame, LABEL_COLS)
    reviewers = _text(frame, REVIEWER_COLS)
    reviewed = pd.Series(False, index=frame.index)
    if not checks.empty:
        reviewed |= checks.isin(TRUTHY | FALSEY).any(axis=1)
    if not labels.empty:
        reviewed |= labels.ne("").any(axis=1)
    if "reviewer_id" in reviewers:
        reviewer_backed = reviewers["reviewer_id"].ne("")
    else:
        reviewer_backed = pd.Series(False, index=frame.index)
    reviewed_count = int(reviewed.sum())
    if reviewed_count == 0:
        status = "pending"
    elif reviewed_count < len(frame):
        status = "partial"
    else:
        status = "complete_small_qc"
    check_summary = {}
    for column in CHECK_COLS:
        if column not in checks:
            continue
        values = checks[column]
        ok = int(values.isin(TRUTHY).sum())
        not_ok = int(values.isin(FALSEY).sum())
        check_summary[column] = {"ok": ok, "not_ok": not_ok, "reviewed": ok + not_ok}
    label_summary = {
        column: {str(key): int(value) for key, value in labels[column][labels[column].ne("")].value_counts().items()}
        for column in LABEL_COLS if column in labels
    }
    return {
        "rows": len(frame), "reviewed_rows": reviewed_count, "status": status,
        "reviewer_backed_rows": int((reviewed & reviewer_backed).sum()),
        "checks": check_summary, "labels": label_summary,
    }


def main() -> int:
    ensure_dirs()
    lines = ["# Manual sanity check report", "", "Small human-authored quality-control bridge; not full ground truth.", ""]
    try:
        frame = pd.read_csv(INPUT, encoding="utf-8-sig") if INPUT.exists() else pd.DataFrame()
    except pd.errors.EmptyDataError:
        frame = pd.DataFrame()
    summary = summarize(frame)
    lines += [
        f"- Rows in sheet: {summary['rows']}",
        f"- Rows with any manual label/check: {summary['reviewed_rows']}",
        f"- Reviewer-backed rows: {summary['reviewer_backed_rows']}",
        f"- QC status: {summary['status']}",
    ]
    for column, values in summary["checks"].items():
        lines.append(f"- {column}: ok={values['ok']}, not_ok={values['not_ok']}, reviewed={values['reviewed']}")
    if summary["labels"]:
        lines += ["", "## Human categorical labels", ""]
        for column, counts in summary["labels"].items():
            lines.append(f"- {column}: {counts}")
    note_column = "human_review_notes" if "human_review_notes" in frame else "human_error_notes"
    if note_column in frame:
        notes = frame[note_column].dropna().astype(str)
        notes = notes[notes.str.strip().ne("")].head(20)
        if not notes.empty:
            lines += ["", "## Review notes", ""] + [f"- {note}" for note in notes]
    if summary["reviewed_rows"] and not summary["reviewer_backed_rows"]:
        lines += ["", "Warning: existing checks lack reviewer provenance; treat as pilot QC, not validated human reference."]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
