"""
Góc 1 (sub-group: news_count >= 15) — Kiểm định H2 trên nhóm cổ phiếu tin dày.

Lý do lý thuyết cho sub-group này:
    Khi số bài báo đủ dày (>= 15 bài/quý), tần suất từ khóa phản ánh thực sự
    hoạt động doanh nghiệp thay vì nhiễu ngẫu nhiên. Đây là điều kiện cần thiết
    để đặc trưng từ khóa có ý nghĩa thống kê.

    Ngưỡng 15 bài/quý tương đương ~5 bài/tháng — mức tối thiểu để corpus đủ đại
    diện cho tin tức doanh nghiệp trong kỳ. So sánh: has_min_news hiện tại dùng
    ngưỡng 5 bài/quý, thấp hơn 3x.

Sub-group: 636 rows, 74 tickers (47.2% của HOSE-80 dataset).

Output: reports/keyword_significance_highnews.csv
"""

from __future__ import annotations
import sys
for _s in (sys.stdout, sys.stderr):
    _rc = getattr(_s, "reconfigure", None)
    if _rc:
        try: _rc(encoding="utf-8", errors="replace")
        except: pass

import os
import numpy as np
import pandas as pd

from pipeline.task8_keywords import get_curated_keywords, get_all_keywords_flat
from pipeline.task10_train import load_and_merge_data
from pipeline.experiment_keyword_significance import (
    apply_bh_correction,
    chi_square_or_fisher,
    mann_whitney_test,
    logistic_univariate,
    build_keyword_label_dataset,
    _print_summary,
)

REPORTS_DIR = "reports"
OUTPUT_PATH = os.path.join(REPORTS_DIR, "keyword_significance_highnews.csv")
MIN_NEWS = 15


def run_keyword_significance_highnews(
    min_news: int = MIN_NEWS,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Kiểm định H2 trên sub-group có news_count >= min_news.

    Sub-group lý do: khi tin đủ dày, tần suất từ khóa phản ánh thực sự
    hoạt động doanh nghiệp, không bị nhiễu do thưa tin.

    Args:
        min_news: Ngưỡng số bài tối thiểu/quý (default 15).
        alpha: Significance level cho BH-FDR (default 0.05).
    """
    print("=" * 70)
    print(f"Góc 1 (SUB-GROUP: news_count >= {min_news}) — Kiểm định H2")
    print(f"Alpha = {alpha}, BH-FDR correction")
    print(f"Lý do: tin đủ dày mới phản ánh thực sự hoạt động doanh nghiệp")
    print("=" * 70)

    merged = load_and_merge_data()
    print(f"Full dataset: {len(merged)} rows")

    # Apply sub-group filter
    if 'news_count' not in merged.columns:
        raise ValueError("news_count column not found in merged dataset")

    sub = merged[merged['news_count'] >= min_news].copy()
    print(f"Sub-group (news_count >= {min_news}): {len(sub)} rows, "
          f"{sub['ticker'].nunique()} tickers")
    print(f"Label: {sub['label_basic'].value_counts().to_dict()}")

    kw_by_dir = get_curated_keywords()
    all_kws = kw_by_dir["positive"] + kw_by_dir["negative"] + kw_by_dir["neutral"]

    direction_map = {}
    for kw in kw_by_dir["positive"]: direction_map[kw] = "positive"
    for kw in kw_by_dir["negative"]: direction_map[kw] = "negative"
    for kw in kw_by_dir["neutral"]:  direction_map[kw] = "neutral"

    dataset_df, excluded = build_keyword_label_dataset(sub, all_kws)
    included = [kw for kw in all_kws
                if kw not in excluded and f"occurrence_{kw}" in dataset_df.columns]
    labels = dataset_df["label_basic"].values.astype(int)

    if excluded:
        print(f"\nTừ khóa bị loại (zero occurrences): {len(excluded)}")

    print(f"\nChạy kiểm định cho {len(included)} từ khóa...")
    rows = []

    for kw in included:
        occ = dataset_df[f"occurrence_{kw}"].values.astype(int)
        n_occ = int(occ.sum())
        norm_col = f"kw_norm_{kw}"
        norm = (dataset_df[norm_col].values.astype(float)
                if norm_col in dataset_df.columns
                else np.zeros(len(occ)))

        chi_stat, chi_p, chi_test = chi_square_or_fisher(occ, labels)
        mw_stat, mw_p = mann_whitney_test(norm[labels==1], norm[labels==0])
        lc, ll, lu, lp = logistic_univariate(occ, labels)

        rows.append({
            "keyword": kw, "direction": direction_map.get(kw, "unknown"),
            "n_occurrences": n_occ, "n_excluded": 0,
            "chi_statistic": chi_stat, "chi_p_raw": chi_p, "chi_p_adj": np.nan,
            "chi_test_used": chi_test,
            "mw_statistic": mw_stat, "mw_p_raw": mw_p, "mw_p_adj": np.nan,
            "logit_coef": lc, "logit_ci_lower": ll,
            "logit_ci_upper": lu, "logit_p_raw": lp, "logit_p_adj": np.nan,
            "significant_chi": False, "significant_mw": False,
            "significant_logit": False, "significant_any": False,
        })

    for ek in excluded:
        rows.append({
            "keyword": ek, "direction": direction_map.get(ek, "unknown"),
            "n_occurrences": 0, "n_excluded": 1,
            "chi_statistic": np.nan, "chi_p_raw": np.nan, "chi_p_adj": np.nan,
            "chi_test_used": "excluded",
            "mw_statistic": np.nan, "mw_p_raw": np.nan, "mw_p_adj": np.nan,
            "logit_coef": np.nan, "logit_ci_lower": np.nan,
            "logit_ci_upper": np.nan, "logit_p_raw": np.nan, "logit_p_adj": np.nan,
            "significant_chi": False, "significant_mw": False,
            "significant_logit": False, "significant_any": False,
        })

    result_df = pd.DataFrame(rows)
    inc_mask = result_df["n_excluded"] == 0

    for raw_col, adj_col in [
        ("chi_p_raw", "chi_p_adj"),
        ("mw_p_raw", "mw_p_adj"),
        ("logit_p_raw", "logit_p_adj"),
    ]:
        p_raw = result_df.loc[inc_mask, raw_col].values
        result_df.loc[inc_mask, adj_col] = apply_bh_correction(p_raw, alpha=alpha)

    result_df["significant_chi"]   = result_df["chi_p_adj"] < alpha
    result_df["significant_mw"]    = result_df["mw_p_adj"] < alpha
    result_df["significant_logit"] = result_df["logit_p_adj"] < alpha
    result_df["significant_any"]   = (result_df["significant_chi"]
                                       | result_df["significant_mw"]
                                       | result_df["significant_logit"])

    # Add sub-group metadata
    result_df["subgroup"] = f"news_count>={min_news}"
    result_df["subgroup_n"] = len(sub)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    result_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"\nKết quả đã lưu vào: {OUTPUT_PATH}")

    _print_summary(result_df, alpha)
    return result_df


if __name__ == "__main__":
    run_keyword_significance_highnews()
