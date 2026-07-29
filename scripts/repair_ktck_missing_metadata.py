"""Repair only missing Kinhtechungkhoan enriched rows using listing metadata.

This preserves all existing rows, including CafeF full-text rows and existing KTCK
full-body rows. Only KTCK rows without full_text_available are updated.
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

from pipeline import task2b_enrich_articles as t2b

ENRICHED = ROOT / "data" / "news" / "enriched" / "all_news_enriched.csv"
REPORT = ROOT / "reports" / "decision_support" / "generated" / "ktck_missing_metadata_repair_summary.json"


def _ok_mask(df: pd.DataFrame) -> pd.Series:
    return df["full_text_available"].astype(str).str.lower().isin(["true", "1"])


def _coverage(df: pd.DataFrame) -> dict:
    unique = df.drop_duplicates("url")
    ok = _ok_mask(unique)
    by_source = (
        unique.assign(_ok=ok)
        .groupby("source")
        .agg(total=("url", "count"), full_text=("_ok", "sum"))
        .reset_index()
    )
    by_source["coverage_pct"] = (by_source["full_text"] / by_source["total"] * 100).round(2)
    return {
        "unique_urls": int(len(unique)),
        "full_text_unique": int(ok.sum()),
        "coverage_pct": round(float(ok.mean() * 100), 2),
        "by_source": by_source.to_dict("records"),
        "status_counts": {str(k): int(v) for k, v in unique["extraction_status"].fillna("").value_counts().to_dict().items()},
    }


def main() -> None:
    df = pd.read_csv(ENRICHED, low_memory=False)
    before = _coverage(df)

    unique = df.drop_duplicates("url", keep="first")
    ok = _ok_mask(unique)
    kt_missing_urls = set(
        unique.loc[
            unique["source"].astype(str).str.lower().eq("kinhtechungkhoan") & ~ok,
            "url",
        ].astype(str)
    )

    backup = ENRICHED.with_name(
        f"all_news_enriched.pre_ktck_metadata_repair_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    shutil.copy2(ENRICHED, backup)

    cfg = {
        "max_text_chars": 12000,
        "summary_max_chars": 1200,
        "store_full_text": True,
        "extractor_version": t2b.EXTRACTOR_VERSION,
    }
    limiter = t2b.RateLimiter(default_delay=0.0)

    repaired_by_url = {}
    for _, row in unique[unique["url"].astype(str).isin(kt_missing_urls)].iterrows():
        enriched = t2b.enrich_single_article(row, limiter, cfg)
        repaired_by_url[str(row["url"])] = enriched

    out = df.copy()
    repair_cols = [col for col in t2b.ENRICHED_COLUMNS if col not in t2b.BASE_COLUMNS]
    for idx, row in out.iterrows():
        repaired = repaired_by_url.get(str(row.get("url", "")))
        if repaired:
            for col in repair_cols:
                if col in out.columns:
                    out.at[idx, col] = repaired.get(col, "")

    stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    temp_path = ENRICHED.with_name(f"{ENRICHED.name}.{stamp}.tmp")
    out.to_csv(temp_path, index=False, encoding="utf-8")
    temp_path.replace(ENRICHED)

    after = _coverage(out)
    result = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "backup": str(backup),
        "repaired_unique_urls": len(repaired_by_url),
        "before": before,
        "after": after,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
