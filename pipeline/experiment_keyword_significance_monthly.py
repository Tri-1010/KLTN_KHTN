"""
Góc 1 (monthly) — Kiểm định H2 theo từng từ khóa với đơn vị thời gian THÁNG.

Tái sử dụng toàn bộ hàm thống kê từ experiment_keyword_significance.py.
Chỉ thay thế nguồn dữ liệu: thay vì đọc keyword_features.csv (quý),
script này rebuild features theo tháng từ raw data (giống experiment_period.py).

Output: reports/keyword_significance_monthly.csv

Usage:
    python -m pipeline.experiment_keyword_significance_monthly
"""

from __future__ import annotations

import sys

for _stream in (sys.stdout, sys.stderr):
    _rc = getattr(_stream, "reconfigure", None)
    if _rc is not None:
        try:
            _rc(encoding="utf-8", errors="replace")
        except Exception:
            pass

import os
import numpy as np
import pandas as pd

from pipeline.task8_keywords import get_curated_keywords, get_all_keywords_flat
from pipeline.experiment_period import (
    build_period_technical,
    build_period_news,
    build_period_keyword_features,
    build_labels,
    make_period_funcs,
)
from pipeline.experiment_keyword_significance import (
    apply_bh_correction,
    chi_square_or_fisher,
    mann_whitney_test,
    logistic_univariate,
    build_keyword_label_dataset,
    _print_summary,
)

PRICES_PATH = "data/prices/all_vn30_prices.csv"
NEWS_PATH = "data/news/processed/all_news_processed.csv"
REPORTS_DIR = "reports"
OUTPUT_PATH = os.path.join(REPORTS_DIR, "keyword_significance_monthly.csv")


def build_monthly_merged() -> pd.DataFrame:
    """Build merged (ticker, month) dataset with keyword features and labels.

    Mirrors run_for_unit('month') in experiment_period.py but returns the
    full merged DataFrame instead of model metrics.
    """
    assign_fn, next_fn = make_period_funcs("month")

    prices = pd.read_csv(PRICES_PATH, encoding="utf-8")
    news = pd.read_csv(NEWS_PATH, encoding="utf-8")

    print("Building monthly technical features...")
    tech = build_period_technical(prices, assign_fn)

    print("Aggregating monthly news...")
    news_agg = build_period_news(news, assign_fn)

    print("Computing monthly keyword features...")
    kw = build_period_keyword_features(news_agg)

    print("Building monthly labels...")
    labels = build_labels(tech, next_fn)

    # Merge: tech + labels (inner) → keyword (inner)
    merged = tech.merge(labels, on=["ticker", "period_id"], how="inner")
    merged = merged.merge(kw, on=["ticker", "period_id"], how="inner")
    merged = merged.dropna(subset=["label_basic"])

    # Rename period_id → quarter_id so downstream functions work unchanged
    merged = merged.rename(columns={"period_id": "quarter_id"})

    print(f"Monthly dataset: {len(merged)} rows ({merged['quarter_id'].nunique()} periods, "
          f"{merged['ticker'].nunique()} tickers)")
    return merged


def run_keyword_significance_monthly(alpha: float = 0.05) -> pd.DataFrame:
    """Run H2 keyword significance testing on monthly data.

    Same methodology as run_keyword_significance() but uses monthly
    (ticker, month) aggregation instead of quarterly.

    Args:
        alpha: Significance level for BH-FDR (default 0.05).

    Returns:
        DataFrame saved to reports/keyword_significance_monthly.csv.
    """
    print("=" * 70)
    print("Góc 1 (THÁNG) — Kiểm định H2: mối liên hệ thống kê từng từ khóa")
    print(f"Alpha = {alpha}, BH-FDR correction, đơn vị: tháng")
    print("=" * 70)

    # Build monthly merged dataset
    merged = build_monthly_merged()

    # Get keyword list and direction map
    kw_by_dir = get_curated_keywords()
    all_keywords = (
        kw_by_dir["positive"] + kw_by_dir["negative"] + kw_by_dir["neutral"]
    )

    direction_map = {}
    for kw in kw_by_dir["positive"]:
        direction_map[kw] = "positive"
    for kw in kw_by_dir["negative"]:
        direction_map[kw] = "negative"
    for kw in kw_by_dir["neutral"]:
        direction_map[kw] = "neutral"

    # Build keyword-label dataset
    dataset_df, excluded_kws = build_keyword_label_dataset(merged, all_keywords)

    if excluded_kws:
        print(f"\nTừ khóa bị loại (zero occurrences): {len(excluded_kws)}")

    included_keywords = [
        kw for kw in all_keywords
        if kw not in excluded_kws and f"occurrence_{kw}" in dataset_df.columns
    ]

    labels = dataset_df["label_basic"].values.astype(int)

    # Run tests
    print(f"\nChạy kiểm định cho {len(included_keywords)} từ khóa (monthly)...")
    rows = []

    for kw in included_keywords:
        occ_col = f"occurrence_{kw}"
        norm_col = f"kw_norm_{kw}"

        occurrence = dataset_df[occ_col].values.astype(int)
        n_occ = int(occurrence.sum())

        norm_freq = (
            dataset_df[norm_col].values.astype(float)
            if norm_col in dataset_df.columns
            else np.zeros(len(occurrence), dtype=float)
        )
        norm_up = norm_freq[labels == 1]
        norm_not_up = norm_freq[labels == 0]

        chi_stat, chi_p_raw, chi_test_used = chi_square_or_fisher(occurrence, labels)
        mw_stat, mw_p_raw = mann_whitney_test(norm_up, norm_not_up)
        logit_coef, logit_ci_lower, logit_ci_upper, logit_p_raw = logistic_univariate(
            occurrence, labels
        )

        rows.append({
            "keyword": kw,
            "direction": direction_map.get(kw, "unknown"),
            "n_occurrences": n_occ,
            "n_excluded": 0,
            "chi_statistic": chi_stat,
            "chi_p_raw": chi_p_raw,
            "chi_p_adj": np.nan,
            "chi_test_used": chi_test_used,
            "mw_statistic": mw_stat,
            "mw_p_raw": mw_p_raw,
            "mw_p_adj": np.nan,
            "logit_coef": logit_coef,
            "logit_ci_lower": logit_ci_lower,
            "logit_ci_upper": logit_ci_upper,
            "logit_p_raw": logit_p_raw,
            "logit_p_adj": np.nan,
            "significant_chi": False,
            "significant_mw": False,
            "significant_logit": False,
            "significant_any": False,
        })

    # Excluded keyword rows
    for ek in excluded_kws:
        rows.append({
            "keyword": ek,
            "direction": direction_map.get(ek, "unknown"),
            "n_occurrences": 0,
            "n_excluded": 1,
            "chi_statistic": np.nan, "chi_p_raw": np.nan, "chi_p_adj": np.nan,
            "chi_test_used": "excluded",
            "mw_statistic": np.nan, "mw_p_raw": np.nan, "mw_p_adj": np.nan,
            "logit_coef": np.nan, "logit_ci_lower": np.nan,
            "logit_ci_upper": np.nan, "logit_p_raw": np.nan, "logit_p_adj": np.nan,
            "significant_chi": False, "significant_mw": False,
            "significant_logit": False, "significant_any": False,
        })

    result_df = pd.DataFrame(rows)

    # BH-FDR correction per test type
    included_mask = result_df["n_excluded"] == 0
    for raw_col, adj_col in [
        ("chi_p_raw", "chi_p_adj"),
        ("mw_p_raw", "mw_p_adj"),
        ("logit_p_raw", "logit_p_adj"),
    ]:
        p_raw = result_df.loc[included_mask, raw_col].values
        result_df.loc[included_mask, adj_col] = apply_bh_correction(p_raw, alpha=alpha)

    # Mark significant
    result_df["significant_chi"] = result_df["chi_p_adj"] < alpha
    result_df["significant_mw"] = result_df["mw_p_adj"] < alpha
    result_df["significant_logit"] = result_df["logit_p_adj"] < alpha
    result_df["significant_any"] = (
        result_df["significant_chi"]
        | result_df["significant_mw"]
        | result_df["significant_logit"]
    )

    # Save
    os.makedirs(REPORTS_DIR, exist_ok=True)
    result_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"\nKết quả đã lưu vào: {OUTPUT_PATH}")

    # Print summary
    _print_summary(result_df, alpha)

    return result_df


if __name__ == "__main__":
    run_keyword_significance_monthly()
