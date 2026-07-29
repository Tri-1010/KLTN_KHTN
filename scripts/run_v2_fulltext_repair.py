"""Run v2 full-text repair and print coverage.

This script preserves existing successful full_text rows and repairs low-coverage
sources using the current TASK_2B configuration in config/pipeline_config.yaml.
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(r"C:\Users\User\KLTN_KHTN")
sys.path.insert(0, str(ROOT))

from pipeline.task2b_enrich_articles import run_enrichment
ENRICHED = ROOT / "data" / "news" / "enriched" / "all_news_enriched.csv"
REPORT = ROOT / "reports" / "decision_support" / "generated" / "v2_fulltext_repair_summary.json"


def coverage() -> dict:
    df = pd.read_csv(ENRICHED, low_memory=False).drop_duplicates("url")
    ok = df["full_text_available"].astype(str).str.lower().isin(["true", "1"])
    status_counts = df["extraction_status"].fillna("").value_counts().to_dict()
    by_source = (
        df.assign(_ok=ok)
        .groupby("source")
        .agg(total=("url", "count"), full_text=("_ok", "sum"))
        .reset_index()
    )
    by_source["coverage_pct"] = (by_source["full_text"] / by_source["total"] * 100).round(2)
    return {
        "unique_urls": int(len(df)),
        "full_text_unique": int(ok.sum()),
        "coverage_pct": round(float(ok.mean() * 100), 2),
        "status_counts": {str(k): int(v) for k, v in status_counts.items()},
        "by_source": by_source.to_dict("records"),
    }


def main() -> None:
    before = coverage()
    backup = ENRICHED.with_name(
        f"all_news_enriched.pre_v2_repair_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    shutil.copy2(ENRICHED, backup)
    print(json.dumps({"phase": "before", "backup": str(backup), **before}, ensure_ascii=False, indent=2))

    run_enrichment(force=False)

    after = coverage()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "backup": str(backup),
        "before": before,
        "after": after,
        "target_80_percent_met": after["coverage_pct"] >= 80.0,
        "target_full_text_unique": int(after["unique_urls"] * 0.8 + 0.9999),
    }
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"phase": "after", **after, "report": str(REPORT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
