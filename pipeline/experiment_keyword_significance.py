"""
Góc 1 — Kiểm định H2 từng từ khóa: Statistical significance testing
of keyword–label associations.

Giả thuyết H2: "Một số từ khóa tài chính có mối liên hệ thống kê với
xu hướng tăng/giảm giá cổ phiếu VN30."

Ba kiểm định được thực hiện cho mỗi từ khóa:
1. Chi-square hoặc Fisher exact (tuỳ kỳ vọng) — giữa Keyword_Occurrence và nhãn
2. Mann-Whitney U — so sánh phân phối tần suất chuẩn hóa giữa nhóm Up và Not_Up
3. Logistic regression đơn biến — ước lượng hệ số và khoảng tin cậy

Hiệu chỉnh đa kiểm định: Benjamini-Hochberg FDR áp dụng riêng cho từng loại
kiểm định.

Sử dụng toàn bộ dataset (không chỉ test set) vì đây là phân tích
correlation/association, không phải đánh giá dự báo out-of-sample.
Ghi rõ giả định này trong output.

Output: reports/keyword_significance.csv

Usage:
    python -m pipeline.experiment_keyword_significance
"""

from __future__ import annotations

import sys

# ---------------------------------------------------------------------------
# UTF-8 reconfigure — hiển thị đúng tiếng Việt trên Windows (Req 7.4)
# ---------------------------------------------------------------------------
for _stream in (sys.stdout, sys.stderr):
    _rc = getattr(_stream, "reconfigure", None)
    if _rc is not None:
        try:
            _rc(encoding="utf-8", errors="replace")
        except Exception:
            pass

import os
import warnings
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu
from statsmodels.stats.multitest import multipletests

from pipeline.task8_keywords import get_curated_keywords
from pipeline.task10_train import load_and_merge_data


# ---------------------------------------------------------------------------
# Output path
# ---------------------------------------------------------------------------

REPORTS_DIR = "reports"
OUTPUT_PATH = os.path.join(REPORTS_DIR, "keyword_significance.csv")


# ---------------------------------------------------------------------------
# Sub-task 1.1 — BH-FDR correction (Req 1.5, 6.1)
# ---------------------------------------------------------------------------


def apply_bh_correction(
    p_values: np.ndarray,
    alpha: float = 0.05,
) -> np.ndarray:
    """Apply Benjamini-Hochberg FDR correction to an array of raw p-values.

    Uses ``statsmodels.stats.multitest.multipletests(method='fdr_bh')``.
    NaN entries are passed through as NaN (excluded from the correction).

    Args:
        p_values: 1-D array of raw p-values (values in [0, 1]).
                  May contain NaN for tests that could not be run.
        alpha: Family-wise significance level (default 0.05).

    Returns:
        Array of adjusted p-values with the same length and same NaN pattern.

    Method note (Req 6.7):
        BH controls the expected proportion of false discoveries among all
        rejected hypotheses.  Less conservative than Bonferroni, which
        controls the probability of any false positive — appropriate for
        exploratory research with 100+ keywords.
    """
    p_values = np.asarray(p_values, dtype=float)
    adj = np.full_like(p_values, np.nan)

    # Only correct non-NaN entries
    valid_mask = ~np.isnan(p_values)
    if valid_mask.sum() == 0:
        return adj

    _, adj_valid, _, _ = multipletests(
        p_values[valid_mask],
        alpha=alpha,
        method="fdr_bh",
    )
    adj[valid_mask] = adj_valid
    return adj


# ---------------------------------------------------------------------------
# Sub-task 1.2 — Chi-square or Fisher exact (Req 1.2, 1.9)
# ---------------------------------------------------------------------------


def chi_square_or_fisher(
    occurrence: np.ndarray,
    labels: np.ndarray,
) -> Tuple[float, float, str]:
    """Chi-square or Fisher exact test for keyword occurrence vs trend label.

    Builds a 2×2 contingency table:

        |           | label=0 | label=1 |
        |-----------|---------|---------|
        | occur=0   |  n00    |  n01    |
        | occur=1   |  n10    |  n11    |

    Decision rule (Req 1.9):
        If ANY expected cell frequency < 5 → Fisher exact test.
        Otherwise → chi-square with Yates' continuity correction.

    Args:
        occurrence: Binary array (0/1) — keyword occurred in the period.
        labels: Binary array (0/1) — up-trend label.

    Returns:
        (statistic, p_value, test_used) where test_used is one of
        "chi_square" or "fisher_exact".

    Assumptions (Req 6.7):
        Chi-square assumes expected cell counts ≥ 5.  Fisher exact makes no
        such assumption and is used when the chi-square assumption is violated.
    """
    occurrence = np.asarray(occurrence, dtype=int)
    labels = np.asarray(labels, dtype=int)

    # Build 2×2 contingency table
    n00 = int(np.sum((occurrence == 0) & (labels == 0)))
    n01 = int(np.sum((occurrence == 0) & (labels == 1)))
    n10 = int(np.sum((occurrence == 1) & (labels == 0)))
    n11 = int(np.sum((occurrence == 1) & (labels == 1)))

    table = np.array([[n00, n01], [n10, n11]], dtype=float)

    # Guard: degenerate table (all zeros in a row or column)
    if table.sum() == 0:
        return (np.nan, np.nan, "fisher_exact")

    # Compute expected frequencies for chi-square assumption check
    row_sums = table.sum(axis=1, keepdims=True)
    col_sums = table.sum(axis=0, keepdims=True)
    total = table.sum()
    if total == 0:
        return (np.nan, np.nan, "fisher_exact")

    expected = row_sums * col_sums / total

    if (expected < 5).any():
        # Use Fisher exact test (Req 1.9)
        # scipy.stats.fisher_exact takes an integer 2×2 array
        int_table = np.array([[n00, n01], [n10, n11]], dtype=int)
        stat, pval = fisher_exact(int_table, alternative="two-sided")
        return (float(stat), float(pval), "fisher_exact")
    else:
        # Chi-square with Yates' continuity correction
        stat, pval, _dof, _exp = chi2_contingency(table, correction=True)
        return (float(stat), float(pval), "chi_square")


# ---------------------------------------------------------------------------
# Sub-task 1.3 — Mann-Whitney U test (Req 1.3)
# ---------------------------------------------------------------------------


def mann_whitney_test(
    norm_freq_up: np.ndarray,
    norm_freq_not_up: np.ndarray,
) -> Tuple[float, float]:
    """Mann-Whitney U test on normalized keyword frequencies.

    Compares the distribution of ``kw_norm_{k}`` between:
    - Group 1 (Up_Label = 1): periods where the stock went up next quarter.
    - Group 2 (Not_Up_Label = 0): periods where it did not go up.

    Uses ``scipy.stats.mannwhitneyu(alternative='two-sided')``.

    Safe handling:
        - If either group is empty → returns (nan, nan).
        - If either group has only identical values (zero variance) the test
          still runs; scipy handles this gracefully.

    Args:
        norm_freq_up: Normalized frequencies for the Up_Label group.
        norm_freq_not_up: Normalized frequencies for the Not_Up_Label group.

    Returns:
        (statistic, p_value)

    Assumptions (Req 6.7):
        Mann-Whitney U assumes independence of observations; it does not
        assume normality, making it appropriate for the typically sparse
        and zero-heavy normalized keyword frequency distributions.
    """
    norm_freq_up = np.asarray(norm_freq_up, dtype=float)
    norm_freq_not_up = np.asarray(norm_freq_not_up, dtype=float)

    # Safe handling when a group is empty (Req 1.3)
    if len(norm_freq_up) == 0 or len(norm_freq_not_up) == 0:
        return (np.nan, np.nan)

    # Replace NaN with 0 (no news → normalized frequency = 0)
    norm_freq_up = np.nan_to_num(norm_freq_up, nan=0.0)
    norm_freq_not_up = np.nan_to_num(norm_freq_not_up, nan=0.0)

    stat, pval = mannwhitneyu(norm_freq_up, norm_freq_not_up, alternative="two-sided")
    return (float(stat), float(pval))


# ---------------------------------------------------------------------------
# Sub-task 1.4 — Logistic regression univariate (Req 1.4)
# ---------------------------------------------------------------------------


def logistic_univariate(
    occurrence: np.ndarray,
    labels: np.ndarray,
) -> Tuple[float, float, float, float]:
    """Univariate logistic regression: keyword occurrence → trend label.

    Uses ``statsmodels.api.Logit`` to fit a model with a single binary
    predictor (Keyword_Occurrence) and a constant intercept.

    Error handling:
        - ``PerfectSeparationError``: the keyword perfectly predicts the label
          (e.g. always present when label=1, never when label=0). The MLE
          does not exist in finite samples. Returns (nan, nan, nan, nan).
        - ``ConvergenceWarning``: the optimizer did not converge. Returns
          (nan, nan, nan, nan) to avoid reporting unreliable estimates.
        - Any other exception: Returns (nan, nan, nan, nan) and logs the error.

    Args:
        occurrence: Binary array (0/1) — keyword occurred in the period.
        labels: Binary array (0/1) — up-trend label.

    Returns:
        (coef, ci_lower, ci_upper, p_value) for the keyword coefficient.
        Returns (nan, nan, nan, nan) when estimation fails.

    Assumptions (Req 6.7):
        Logistic regression assumes independence of observations and that
        the log-odds are linearly related to the predictor. The univariate
        form is used here for interpretability; the coefficient can be
        interpreted as the change in log-odds of an up-trend when the
        keyword is present.
    """
    import statsmodels.api as sm
    from statsmodels.tools.sm_exceptions import PerfectSeparationError

    occurrence = np.asarray(occurrence, dtype=float)
    labels = np.asarray(labels, dtype=float)

    # Need at least 2 classes in labels and some variation in occurrence
    if len(np.unique(labels)) < 2 or len(np.unique(occurrence)) < 2:
        return (np.nan, np.nan, np.nan, np.nan)

    X = sm.add_constant(occurrence, has_constant="add")

    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("error", category=UserWarning)
            model = sm.Logit(labels, X)
            result = model.fit(disp=False, maxiter=100)

        coef = float(result.params[1])
        ci = result.conf_int(alpha=0.05)
        ci_lower = float(ci.iloc[1, 0])
        ci_upper = float(ci.iloc[1, 1])
        pval = float(result.pvalues[1])
        return (coef, ci_lower, ci_upper, pval)

    except PerfectSeparationError:
        warnings.warn(
            "Logistic regression: PerfectSeparationError — returning (nan, nan, nan, nan)",
            stacklevel=2,
        )
        return (np.nan, np.nan, np.nan, np.nan)

    except Exception as e:
        # Catches ConvergenceWarning (raised as error above) and other issues
        warnings.warn(
            f"Logistic regression failed: {type(e).__name__}: {e} — "
            "returning (nan, nan, nan, nan)",
            stacklevel=2,
        )
        return (np.nan, np.nan, np.nan, np.nan)


# ---------------------------------------------------------------------------
# Sub-task 1.5 — Build keyword-label dataset (Req 1.1, 1.8)
# ---------------------------------------------------------------------------


def build_keyword_label_dataset(
    merged_df: pd.DataFrame,
    keywords: List[str],
) -> Tuple[pd.DataFrame, List[str]]:
    """Extract occurrence and normalized-frequency columns for each keyword.

    For each keyword k:
      - ``kw_{k}``       must already exist in merged_df (raw count)
      - ``kw_norm_{k}``  must already exist in merged_df (normalized by news_count)
      - ``occurrence_{k}`` = 1 if kw_{k} > 0 else 0

    Keywords whose total raw count across all rows is 0 are excluded from
    statistical testing and recorded in the excluded list (Req 1.8).

    Args:
        merged_df: Full merged DataFrame from load_and_merge_data().
        keywords: Flat list of all curated keyword strings.

    Returns:
        (dataset_df, excluded_keywords)

        dataset_df has columns:
            label_basic, occurrence_{k}, kw_norm_{k}  for each included keyword.
        excluded_keywords: list of keyword strings excluded (zero occurrences).
    """
    excluded: List[str] = []
    included_cols = ["label_basic"]

    for kw in keywords:
        col_raw = f"kw_{kw}"
        col_norm = f"kw_norm_{kw}"

        # Check that column exists and has at least one non-zero value
        if col_raw not in merged_df.columns:
            excluded.append(kw)
            continue

        total = merged_df[col_raw].fillna(0).sum()
        if total == 0:
            excluded.append(kw)  # Req 1.8
            continue

        occ_col = f"occurrence_{kw}"
        merged_df = merged_df.copy()  # avoid SettingWithCopyWarning
        merged_df[occ_col] = (merged_df[col_raw] > 0).astype(int)

        included_cols.append(occ_col)
        if col_norm in merged_df.columns:
            included_cols.append(col_norm)

    dataset_df = merged_df[included_cols].copy()
    return dataset_df, excluded


# ---------------------------------------------------------------------------
# Sub-task 1.6 — Main runner (Req 1.1–1.10, 6.2–6.5, 7.1–7.5)
# ---------------------------------------------------------------------------


def run_keyword_significance(
    cutoff: str = "2025Q1",
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Run statistical significance testing for H2 — keyword × trend label.

    Workflow:
    1. Load and merge feature/label data (entire dataset, not just test set).
    2. Build keyword-label dataset; exclude zero-frequency keywords.
    3. For each included keyword run:
       a. Chi-square or Fisher exact test (occurrence vs label)
       b. Mann-Whitney U test (norm_freq: up vs not-up groups)
       c. Univariate logistic regression (occurrence → label)
    4. Apply BH-FDR correction to each test type separately (Req 1.5, 6.1).
    5. Build output DataFrame with all design columns.
    6. Save to reports/keyword_significance.csv (Req 1.7, 7.1).
    7. Print summary of significant keywords (Req 1.10).

    Note on in-sample analysis (Req 6.7):
        This analysis uses the entire dataset, not only the test split, because
        H2 is a correlation/association question, not a prediction question.
        Findings should NOT be interpreted as evidence of out-of-sample
        predictive power. The cutoff parameter is accepted for API consistency
        but is not used to split the data here.

    Args:
        cutoff: Accepted for API consistency; not used to split data.
        alpha: Significance level for BH-FDR (default 0.05).

    Returns:
        DataFrame saved to reports/keyword_significance.csv.
    """
    print("=" * 70)
    print("Góc 1 — Kiểm định H2: mối liên hệ thống kê từng từ khóa")
    print(f"Alpha = {alpha}, BH-FDR correction")
    print(f"Ghi chú: sử dụng toàn bộ dataset (in-sample, cutoff '{cutoff}' không được dùng để chia)")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Step 1: Load data
    # ------------------------------------------------------------------
    merged = load_and_merge_data()
    print(f"Dataset: {len(merged)} rows, {len(merged.columns)} columns")

    # ------------------------------------------------------------------
    # Step 2: Build keyword-label dataset
    # ------------------------------------------------------------------
    kw_by_dir = get_curated_keywords()
    all_keywords = (
        kw_by_dir["positive"] + kw_by_dir["negative"] + kw_by_dir["neutral"]
    )

    dataset_df, excluded_kws = build_keyword_label_dataset(merged, all_keywords)

    if excluded_kws:
        print(f"\nTừ khóa bị loại (zero occurrences): {len(excluded_kws)}")
        for ek in excluded_kws:
            print(f"  - {ek}")

    # Direction lookup: keyword → direction string
    direction_map: Dict[str, str] = {}
    for kw in kw_by_dir["positive"]:
        direction_map[kw] = "positive"
    for kw in kw_by_dir["negative"]:
        direction_map[kw] = "negative"
    for kw in kw_by_dir["neutral"]:
        direction_map[kw] = "neutral"

    # Determine which keywords were actually included
    included_keywords = [
        kw for kw in all_keywords if kw not in excluded_kws
        and f"occurrence_{kw}" in dataset_df.columns
    ]

    labels = dataset_df["label_basic"].values.astype(int)

    # ------------------------------------------------------------------
    # Step 3: Run tests for each keyword
    # ------------------------------------------------------------------
    rows = []
    print(f"\nChạy kiểm định cho {len(included_keywords)} từ khóa...")

    for kw in included_keywords:
        occ_col = f"occurrence_{kw}"
        norm_col = f"kw_norm_{kw}"

        occurrence = dataset_df[occ_col].values.astype(int)

        # Raw occurrence count
        n_occ = int(occurrence.sum())

        # Normalized frequency groups
        if norm_col in dataset_df.columns:
            norm_freq = dataset_df[norm_col].values.astype(float)
        else:
            norm_freq = np.zeros(len(occurrence), dtype=float)

        norm_up = norm_freq[labels == 1]
        norm_not_up = norm_freq[labels == 0]

        # 3a. Chi-square or Fisher
        chi_stat, chi_p_raw, chi_test_used = chi_square_or_fisher(occurrence, labels)

        # 3b. Mann-Whitney
        mw_stat, mw_p_raw = mann_whitney_test(norm_up, norm_not_up)

        # 3c. Logistic regression
        logit_coef, logit_ci_lower, logit_ci_upper, logit_p_raw = logistic_univariate(
            occurrence, labels
        )

        rows.append({
            "keyword": kw,
            "direction": direction_map.get(kw, "unknown"),
            "n_occurrences": n_occ,
            "n_excluded": 0,  # 0 = included
            "chi_statistic": chi_stat,
            "chi_p_raw": chi_p_raw,
            "chi_p_adj": np.nan,       # filled after BH
            "chi_test_used": chi_test_used,
            "mw_statistic": mw_stat,
            "mw_p_raw": mw_p_raw,
            "mw_p_adj": np.nan,        # filled after BH
            "logit_coef": logit_coef,
            "logit_ci_lower": logit_ci_lower,
            "logit_ci_upper": logit_ci_upper,
            "logit_p_raw": logit_p_raw,
            "logit_p_adj": np.nan,     # filled after BH
            "significant_chi": False,
            "significant_mw": False,
            "significant_logit": False,
            "significant_any": False,
        })

    # Append excluded keywords as informational rows (Req 1.8, 6.6)
    for ek in excluded_kws:
        rows.append({
            "keyword": ek,
            "direction": direction_map.get(ek, "unknown"),
            "n_occurrences": 0,
            "n_excluded": 1,
            "chi_statistic": np.nan,
            "chi_p_raw": np.nan,
            "chi_p_adj": np.nan,
            "chi_test_used": "excluded",
            "mw_statistic": np.nan,
            "mw_p_raw": np.nan,
            "mw_p_adj": np.nan,
            "logit_coef": np.nan,
            "logit_ci_lower": np.nan,
            "logit_ci_upper": np.nan,
            "logit_p_raw": np.nan,
            "logit_p_adj": np.nan,
            "significant_chi": False,
            "significant_mw": False,
            "significant_logit": False,
            "significant_any": False,
        })

    result_df = pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # Step 4: Apply BH-FDR correction per test type (Req 1.5, 6.1)
    # ------------------------------------------------------------------
    included_mask = result_df["n_excluded"] == 0

    for raw_col, adj_col in [
        ("chi_p_raw", "chi_p_adj"),
        ("mw_p_raw", "mw_p_adj"),
        ("logit_p_raw", "logit_p_adj"),
    ]:
        p_raw_included = result_df.loc[included_mask, raw_col].values
        p_adj_included = apply_bh_correction(p_raw_included, alpha=alpha)
        result_df.loc[included_mask, adj_col] = p_adj_included

    # ------------------------------------------------------------------
    # Step 5: Mark significant keywords (Req 1.6)
    # ------------------------------------------------------------------
    result_df["significant_chi"] = result_df["chi_p_adj"] < alpha
    result_df["significant_mw"] = result_df["mw_p_adj"] < alpha
    result_df["significant_logit"] = result_df["logit_p_adj"] < alpha
    result_df["significant_any"] = (
        result_df["significant_chi"]
        | result_df["significant_mw"]
        | result_df["significant_logit"]
    )

    # ------------------------------------------------------------------
    # Step 6: Save output (Req 1.7, 7.1)
    # ------------------------------------------------------------------
    os.makedirs(REPORTS_DIR, exist_ok=True)
    result_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"\nKết quả đã lưu vào: {OUTPUT_PATH}")

    # ------------------------------------------------------------------
    # Step 7: Print summary (Req 1.10)
    # ------------------------------------------------------------------
    _print_summary(result_df, alpha)

    return result_df


# ---------------------------------------------------------------------------
# Helper — print summary
# ---------------------------------------------------------------------------


def _print_summary(result_df: pd.DataFrame, alpha: float) -> None:
    """Print a summary of significant keywords sorted by adjusted p-value."""
    included = result_df[result_df["n_excluded"] == 0]

    n_chi = included["significant_chi"].sum()
    n_mw = included["significant_mw"].sum()
    n_logit = included["significant_logit"].sum()
    n_any = included["significant_any"].sum()
    n_total = len(included)

    print("\n" + "=" * 70)
    print(f"TÓM TẮT KẾT QUẢ — alpha = {alpha} (BH-FDR adjusted)")
    print("=" * 70)
    print(f"Tổng từ khóa được kiểm định : {n_total}")
    print(f"  Significant (chi/Fisher)  : {n_chi} / {n_total}")
    print(f"  Significant (Mann-Whitney): {n_mw} / {n_total}")
    print(f"  Significant (logistic)    : {n_logit} / {n_total}")
    print(f"  Significant (bất kỳ test) : {n_any} / {n_total}")

    if n_any > 0:
        sig = included[included["significant_any"]].copy()
        # Sort by best (minimum) adjusted p-value across the three tests
        sig["_min_adj_p"] = sig[["chi_p_adj", "mw_p_adj", "logit_p_adj"]].min(axis=1)
        sig = sig.sort_values("_min_adj_p")

        print(f"\nDanh sách từ khóa significant (sorted by min adj p-value):")
        print(f"{'Từ khóa':<40} {'Hướng':<10} {'Chi adj_p':>10} {'MW adj_p':>10} {'Logit adj_p':>12}")
        print("-" * 85)
        for _, row in sig.iterrows():
            chi_p = f"{row['chi_p_adj']:.4f}" if pd.notna(row["chi_p_adj"]) else "  NaN"
            mw_p = f"{row['mw_p_adj']:.4f}" if pd.notna(row["mw_p_adj"]) else "  NaN"
            logit_p = f"{row['logit_p_adj']:.4f}" if pd.notna(row["logit_p_adj"]) else "  NaN"
            print(f"{row['keyword']:<40} {row['direction']:<10} {chi_p:>10} {mw_p:>10} {logit_p:>12}")
    else:
        print("\nKhông có từ khóa nào đạt ý nghĩa thống kê sau BH-FDR correction.")
        print("Kết quả này là hợp lệ và sẽ được báo cáo trung thực.")
    print("=" * 70)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_keyword_significance()
