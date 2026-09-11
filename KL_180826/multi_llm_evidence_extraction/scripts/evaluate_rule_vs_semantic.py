from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import OUTPUT_DIR, REPORT_DIR, ensure_dirs

RULE = OUTPUT_DIR / "rule_labels.csv"
CONS = OUTPUT_DIR / "pseudo_labels_consensus.csv"
MATRIX = OUTPUT_DIR / "rule_vs_semantic_confusion_matrices.csv"
REPORT = REPORT_DIR / "rule_vs_semantic_labels_report.md"
PAIRS = [
    ("rule_direction", "consensus_direction"),
    ("rule_event_type", "consensus_event_type"),
    ("rule_materiality", "consensus_materiality"),
    ("rule_relevance", "consensus_ticker_relevance"),
]


def main() -> int:
    ensure_dirs()
    lines = ["# Rule vs semantic labels report", ""]
    if not RULE.exists() or not CONS.exists() or pd.read_csv(CONS, encoding="utf-8-sig").empty:
        lines.append("Rule or consensus labels unavailable. Run rule baseline and live annotation consensus first.")
        REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        pd.DataFrame().to_csv(MATRIX, index=False, encoding="utf-8-sig")
        print(f"saved pending {REPORT}")
        return 0
    rule = pd.read_csv(RULE, encoding="utf-8-sig")
    cons = pd.read_csv(CONS, encoding="utf-8-sig")
    if "analysis_eligible" not in cons:
        lines.append("Comparison unavailable: consensus artifact lacks required `analysis_eligible`; no implicit all-row fallback is allowed.")
        REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        pd.DataFrame().to_csv(MATRIX, index=False, encoding="utf-8-sig")
        print(f"saved pending {REPORT}")
        return 0
    eligible = cons["analysis_eligible"].astype(str).str.strip().str.lower().isin(["true", "1", "yes"])
    eligible_cons = cons[eligible].copy()
    df = rule.merge(eligible_cons, on=["news_id", "ticker"], how="inner")
    eligible_keys = eligible_cons[["news_id", "ticker"]].drop_duplicates()
    compared_keys = df[["news_id", "ticker"]].drop_duplicates()
    coverage = len(compared_keys) / len(eligible_keys) if len(eligible_keys) else 0.0
    lines.append("Semantic labels are controlled pseudo-label references, not human ground truth.")
    lines.append(f"- Eligible consensus rows: {len(eligible_cons)} ({len(eligible_keys)} unique news-ticker keys)")
    lines.append(f"- Compared rows (analysis eligible): {len(df)} ({len(compared_keys)} unique keys)")
    lines.append(f"- Unique-key merge coverage over eligible consensus: {coverage:.4f}")
    rows = []
    for rcol, ccol in PAIRS:
        if rcol not in df or ccol not in df:
            continue
        work = df[[rcol, ccol]].dropna()
        excluded = work[ccol].astype(str).isin(["disagreement", "unclear"])
        unclear_rate = float(excluded.mean()) if len(work) else 0.0
        work = work[~excluded]
        if work.empty:
            lines.append(f"- {rcol} vs {ccol}: no scorable rows; unclear/disagreement rate={unclear_rate:.4f}")
            continue
        acc = accuracy_score(work[ccol], work[rcol])
        f1 = f1_score(work[ccol], work[rcol], average="macro", zero_division=0)
        lines.append(f"- {rcol} vs {ccol}: accuracy={acc:.4f}, macro_f1={f1:.4f}, n={len(work)}, unclear/disagreement rate={unclear_rate:.4f}")
        labels = sorted(set(work[rcol].astype(str)) | set(work[ccol].astype(str)))
        cm = confusion_matrix(work[ccol], work[rcol], labels=labels)
        for i, actual in enumerate(labels):
            for j, pred in enumerate(labels):
                rows.append({"field": ccol, "actual": actual, "predicted_rule": pred, "count": int(cm[i, j])})
    pd.DataFrame(rows).to_csv(MATRIX, index=False, encoding="utf-8-sig")
    lines += ["", "## Error taxonomy", "", "- keyword thiếu ngữ cảnh", "- keyword không đo materiality", "- ticker relevance sai", "- market-wide bị đếm như direct", "- boilerplate/full-text noise", "- mixed direction", "- event type overlap"]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
