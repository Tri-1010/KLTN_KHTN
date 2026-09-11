"""
Góc 4 — Kiểm định H3 / diễn giải: SHAP + permutation importance
bắt buộc trên mô hình Config_C.

Mục tiêu: xác định và xếp hạng các từ khóa đóng góp nhiều nhất vào
dự báo của mô hình Config_C, trả lời giả thuyết H3 một cách trực tiếp.

Lý do: task11_shap chỉ chạy trên best model (thường là Config_A/Config_B).
Script này BẮT BUỘC chạy SHAP và permutation importance trên Config_C
bất kể best model toàn cục là cấu hình nào (Req 4.1).

Tái sử dụng:
  - pipeline.task10_train: build_ml_models, fit_imputer, prepare_features,
      time_series_split, get_feature_configs, identify_feature_columns,
      load_and_merge_data
  - pipeline.task11_shap: compute_shap_values, plot_shap_summary,
      group_contribution_analysis, _extract_keyword_name, _is_keyword_feature
  - pipeline.task8_keywords: get_curated_keywords

Output files (tên tệp phân biệt với Production_Pipeline_Outputs của task11):
  - reports/shap_configc_keyword_ranking.csv   (Req 4.4)
  - reports/configc_shap_summary.png           (Req 4.7 — KHÔNG phải shap_summary.png)
  - reports/configc_permutation_importance.png (Req 4.7 — KHÔNG phải permutation_importance.png)

Random seed = 42 (Req 6.3). Time_Series_Split (Req 6.4). Không ghi đè
Production_Pipeline_Outputs (Req 7.1, 7.2).

Usage:
    python -m pipeline.experiment_shap_configc
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
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")  # headless backend — must be set before pyplot import
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance as sklearn_permutation_importance

import pipeline.task11_shap as task11_shap
from pipeline.task10_train import (
    build_ml_models,
    fit_imputer,
    get_feature_configs,
    identify_feature_columns,
    load_and_merge_data,
    prepare_features,
    time_series_split,
)
from pipeline.task8_keywords import get_curated_keywords

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# Output paths — NEVER overwrite task11 Production_Pipeline_Outputs
# ---------------------------------------------------------------------------

REPORTS_DIR = "reports"
SHAP_SUMMARY_PATH = os.path.join(REPORTS_DIR, "configc_shap_summary.png")
PERM_IMPORTANCE_PATH = os.path.join(REPORTS_DIR, "configc_permutation_importance.png")
KW_RANKING_PATH = os.path.join(REPORTS_DIR, "shap_configc_keyword_ranking.csv")

# Paths that must NEVER be written by this script
_FORBIDDEN_PATHS = {
    os.path.join(REPORTS_DIR, "shap_summary.png"),
    os.path.join(REPORTS_DIR, "permutation_importance.png"),
}

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _ensure_reports_dir() -> None:
    os.makedirs(REPORTS_DIR, exist_ok=True)


def _build_keywords_by_dir() -> Dict[str, str]:
    """Build a flat keyword → direction mapping from get_curated_keywords().

    Returns:
        Dict mapping each keyword string to its direction
        ("positive", "negative", or "neutral").
    """
    kw_by_dir = get_curated_keywords()
    mapping: Dict[str, str] = {}
    for direction, keywords in kw_by_dir.items():
        for kw in keywords:
            mapping[kw] = direction
    return mapping


def _extract_shap_array(shap_values: Any) -> np.ndarray:
    """Extract a 2-D (n_samples, n_features) array from shap_values.

    Handles both:
      - shap.Explanation objects  → shap_values.values
      - plain numpy ndarrays      → used directly if already 2-D

    For binary classifiers the SHAP explanation may have shape
    (n_samples, n_features, 2); task11_shap.compute_shap_values already
    slices the class-1 slice before returning, but we guard here anyway.
    """
    if hasattr(shap_values, "values"):
        arr = shap_values.values
    else:
        arr = np.asarray(shap_values)

    if arr.ndim == 3:
        # Binary classifier — take class-1 slice
        arr = arr[..., 1]

    return arr


# ---------------------------------------------------------------------------
# Sub-task 5.1 — train_configc_model (Req 4.1, 6.3)
# ---------------------------------------------------------------------------


def train_configc_model(
    merged_df: pd.DataFrame,
    tech_cols: List[str],
    kw_cols: List[str],
    cutoff: str = "2025Q1",
    model_name: str = "Random_Forest",
    random_state: int = 42,
) -> Tuple[Any, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """Train a model on Config_C (technical + keyword features).

    Workflow:
    1. Call ``time_series_split(merged_df, cutoff=cutoff)`` for train/test.
    2. Build Config_C column list: tech_cols + kw_cols.
    3. Call ``fit_imputer(train_df, config_c_cols)`` → (imputer, numeric_cols).
    4. Call ``prepare_features(train_df, config_c_cols)`` and
       ``prepare_features(test_df, config_c_cols, imputer=imputer)``
       → X_train, y_train, X_test, y_test.
    5. Retrieve the model from ``build_ml_models(y_train)`` using *model_name*.
    6. Train: ``model.fit(X_train[numeric_cols], y_train)``.
    7. Return ``(model, X_train[numeric_cols], y_train,
                  X_test[numeric_cols], y_test)``.

    Args:
        merged_df: Merged feature/label DataFrame from ``load_and_merge_data()``.
        tech_cols: Technical feature column names (Config_A subset).
        kw_cols: Keyword feature column names.
        cutoff: Quarter string for Time_Series_Split (default "2025Q1").
        model_name: Key in ``build_ml_models()`` dict (default "Random_Forest").
        random_state: Random seed — fixed to 42 for reproducibility (Req 6.3).
            Note: the random seed is set within ``build_ml_models()``; this
            parameter is accepted for API clarity and future-proofing.

    Returns:
        (model, X_train, y_train, X_test, y_test)

    Notes:
        - Config_C = tech_cols + kw_cols (Req 4.1).
        - ``fit_imputer`` is called on the training set only — no leakage (Req 6.4).
        - The model is selected from ``build_ml_models()`` so that random seeds
          and hyperparameters are identical to the production pipeline (Req 6.3).
    """
    # Step 1: Time-series split — no shuffling (Req 6.4)
    train_df, test_df = time_series_split(merged_df, cutoff=cutoff)

    # Step 2: Config_C columns
    config_c_cols = list(tech_cols) + list(kw_cols)

    # Step 3: Fit imputer on training set only (no data leakage)
    imputer, numeric_cols = fit_imputer(train_df, config_c_cols)

    # Step 4: Prepare feature matrices
    X_train_full, y_train = prepare_features(train_df, config_c_cols, imputer=None)
    X_test_full, y_test = prepare_features(test_df, config_c_cols, imputer=imputer)

    # Align to numeric_cols (same order/columns as the imputer was fitted on)
    X_train = X_train_full[numeric_cols]
    X_test = X_test_full[numeric_cols]

    # Step 5: Build model from production factory (random_state=42 inside build_ml_models)
    ml_models = build_ml_models(y_train)
    if model_name not in ml_models:
        available = list(ml_models.keys())
        raise ValueError(
            f"model_name '{model_name}' not found in build_ml_models(). "
            f"Available: {available}"
        )
    model = ml_models[model_name]

    # Step 6: Train on Config_C
    model.fit(X_train, y_train)

    print(
        f"  Trained {model_name} on Config_C: "
        f"{len(numeric_cols)} features, "
        f"train={len(X_train)}, test={len(X_test)}"
    )

    # Step 7: Return
    return model, X_train, y_train, X_test, y_test


# ---------------------------------------------------------------------------
# Sub-task 5.2 — rank_keyword_features_by_shap (Req 4.4, 4.6)
# ---------------------------------------------------------------------------


def rank_keyword_features_by_shap(
    shap_values: Any,
    feature_names: List[str],
    keywords_by_dir: Dict[str, str],
) -> pd.DataFrame:
    """Rank keyword features by mean absolute SHAP value.

    For each feature that ``task11_shap._is_keyword_feature()`` identifies as
    a keyword feature:
      - Extract the keyword name via ``task11_shap._extract_keyword_name()``.
      - Compute ``mean_shap`` = average signed SHAP value across test samples.
      - Compute ``mean_abs_shap`` = average of |SHAP| values across test samples.
      - Look up ``direction`` from *keywords_by_dir* dict
        (positive / negative / neutral / unknown).
      - Determine ``shap_direction``: "positive" if mean_shap > 0 else "negative".
      - Determine ``direction_consistent``:
          * True if direction="positive" AND mean_shap > 0
          * True if direction="negative" AND mean_shap < 0
          * False otherwise (including "neutral" and "unknown")

    Results are sorted by ``mean_abs_shap`` descending and saved to
    ``reports/shap_configc_keyword_ranking.csv``.

    Args:
        shap_values: shap.Explanation object (or ndarray) — output of
            ``task11_shap.compute_shap_values()``.  Handles both
            shap.Explanation and plain ndarray shapes.
        feature_names: List of feature column names aligned with shap_values.
        keywords_by_dir: Flat dict mapping keyword string → direction string.
            Built from ``get_curated_keywords()`` via ``_build_keywords_by_dir()``.

    Returns:
        DataFrame with columns: keyword, direction, mean_shap, mean_abs_shap,
        shap_direction, direction_consistent.
        Also saved to ``reports/shap_configc_keyword_ranking.csv``.

    Notes (Req 4.6):
        ``direction_consistent`` records whether the keyword's intended
        sentiment direction aligns with the sign of its SHAP value in the
        Config_C model, enabling a direct test of H3.
    """
    _ensure_reports_dir()

    # Extract (n_samples, n_features) float array
    vals = _extract_shap_array(shap_values)  # shape: (n_samples, n_features)

    mean_shap_arr = vals.mean(axis=0)          # signed mean
    mean_abs_shap_arr = np.abs(vals).mean(axis=0)  # mean absolute

    records: List[Dict] = []

    for i, col in enumerate(feature_names):
        # Only process keyword-derived features
        if not task11_shap._is_keyword_feature(col):
            continue

        # Extract raw keyword name (e.g. "kw_tang_truong" → "tang_truong",
        # or "kw_loi nhuan tang" → "loi nhuan tang")
        kw_name = task11_shap._extract_keyword_name(col)
        if kw_name is None:
            # _is_keyword_feature returned True but _extract_keyword_name
            # returned None — this covers exact cols like "pos_score"; skip.
            continue

        mean_shap_val = float(mean_shap_arr[i])
        mean_abs_shap_val = float(mean_abs_shap_arr[i])

        # Direction from curated keyword list
        direction = keywords_by_dir.get(kw_name, "unknown")

        # Actual SHAP direction
        shap_direction = "positive" if mean_shap_val > 0 else "negative"

        # Direction consistency check (Req 4.6)
        if direction == "positive" and mean_shap_val > 0:
            direction_consistent = True
        elif direction == "negative" and mean_shap_val < 0:
            direction_consistent = True
        else:
            direction_consistent = False

        records.append(
            {
                "keyword": kw_name,
                "direction": direction,
                "mean_shap": mean_shap_val,
                "mean_abs_shap": mean_abs_shap_val,
                "shap_direction": shap_direction,
                "direction_consistent": direction_consistent,
            }
        )

    if not records:
        print("  Cảnh báo: Không tìm thấy đặc trưng từ khóa nào trong SHAP values.")
        df = pd.DataFrame(
            columns=[
                "keyword", "direction", "mean_shap", "mean_abs_shap",
                "shap_direction", "direction_consistent",
            ]
        )
        df.to_csv(KW_RANKING_PATH, index=False, encoding="utf-8")
        return df

    df = pd.DataFrame(records)
    df = df.sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)

    # Save ranking
    df.to_csv(KW_RANKING_PATH, index=False, encoding="utf-8")
    print(f"  Đã lưu xếp hạng {len(df)} từ khóa vào: {KW_RANKING_PATH}")

    return df


# ---------------------------------------------------------------------------
# Internal helper — permutation importance plot (Req 4.3)
# ---------------------------------------------------------------------------


def _plot_permutation_importance(
    model: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    save_path: str = PERM_IMPORTANCE_PATH,
    n_repeats: int = 10,
    random_state: int = 42,
    top_n: int = 20,
) -> pd.Series:
    """Compute and save a permutation importance bar chart for Config_C.

    Uses ``sklearn.inspection.permutation_importance`` with
    ``scoring="balanced_accuracy"`` and ``random_state=42`` (Req 6.3).

    Saves a horizontal bar chart with top *top_n* features to *save_path*.
    Does NOT write to ``reports/permutation_importance.png`` (Req 4.7, 7.1).

    Args:
        model: Trained Config_C model.
        X_test: Test feature matrix (n_samples × n_features).
        y_test: True labels for test set.
        save_path: Where to save the PNG (must NOT be permutation_importance.png).
        n_repeats: Number of permutation repeats (default 10).
        random_state: Random seed (default 42, Req 6.3).
        top_n: Maximum number of features to display (default 20).

    Returns:
        Series of mean permutation importances (all features), sorted descending.
    """
    # Guard: never overwrite task11 output
    abs_save = os.path.abspath(save_path)
    for forbidden in _FORBIDDEN_PATHS:
        if abs_save == os.path.abspath(forbidden):
            raise ValueError(
                f"Refused to write to forbidden Production_Pipeline_Output: {forbidden}"
            )

    _ensure_reports_dir()

    result = sklearn_permutation_importance(
        model,
        X_test,
        y_test,
        n_repeats=n_repeats,
        random_state=random_state,
        scoring="balanced_accuracy",
    )

    perm_imp = pd.Series(result.importances_mean, index=X_test.columns)
    perm_imp = perm_imp.sort_values(ascending=False)

    # Plot top_n features as a horizontal bar chart
    top = perm_imp.head(top_n)

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = [
        "#E07020" if task11_shap._is_keyword_feature(c) else "#2070C0"
        for c in top.index
    ]
    top.iloc[::-1].plot.barh(ax=ax, color=colors[::-1])
    ax.set_xlabel("Mean Decrease in Balanced Accuracy")
    ax.set_title(f"Config_C — Top {min(top_n, len(top))} Features\nPermutation Importance")
    ax.axvline(x=0, color="gray", linestyle="--", linewidth=0.8)

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#2070C0", label="Technical"),
        Patch(facecolor="#E07020", label="Keyword"),
    ]
    ax.legend(handles=legend_elements, loc="lower right")

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight", dpi=150)
    plt.close()

    print(f"  Đã lưu biểu đồ permutation importance vào: {save_path}")
    return perm_imp


# ---------------------------------------------------------------------------
# Sub-task 5.3 — run_shap_configc (Req 4.1–4.7, 6.3, 6.4)
# ---------------------------------------------------------------------------


def run_shap_configc(
    cutoff: str = "2025Q1",
    model_name: str = "Random_Forest",
) -> pd.DataFrame:
    """Main entry point — SHAP + permutation importance forced on Config_C.

    Workflow:
    (1) Load data via ``load_and_merge_data()``; identify feature columns via
        ``identify_feature_columns()``; get feature configs via
        ``get_feature_configs()`` to determine tech_cols and kw_cols.
    (2) Call ``train_configc_model(merged_df, tech_cols, kw_cols, cutoff,
        model_name)`` → (model, X_train, y_train, X_test, y_test).
    (3) Call ``task11_shap.compute_shap_values(model, X_test, X_train)``
        → shap_values.
    (4) Save beeswarm SHAP summary to ``reports/configc_shap_summary.png``
        via ``task11_shap.plot_shap_summary(shap_values, save_path=...)``.
        Does NOT write to ``reports/shap_summary.png`` (Req 4.7).
    (5) Compute permutation importance and save to
        ``reports/configc_permutation_importance.png`` (Req 4.3, 4.7).
        Does NOT write to ``reports/permutation_importance.png``.
    (6) Call ``rank_keyword_features_by_shap(shap_values, ...)`` and save
        keyword ranking to ``reports/shap_configc_keyword_ranking.csv`` (Req 4.4).
    (7) Call ``task11_shap.group_contribution_analysis(shap_values, ...)``
        and print % keyword vs technical contribution (Req 4.5).

    Args:
        cutoff: Quarter string for Time_Series_Split (default "2025Q1"). Req 6.4.
        model_name: ML algorithm key in ``build_ml_models()`` (default
            "Random_Forest"). Req 4.1 — consistent with best model default.

    Returns:
        Keyword ranking DataFrame (also saved to
        ``reports/shap_configc_keyword_ranking.csv``).

    Notes:
        - Random seed = 42 everywhere (Req 6.3).
        - NEVER writes to ``reports/shap_summary.png`` or
          ``reports/permutation_importance.png`` (Req 4.7, 7.1, 7.2).
    """
    print("=" * 70)
    print("Góc 4 — SHAP + Permutation Importance bắt buộc trên Config_C")
    print(f"Cutoff: {cutoff} | Model: {model_name} | Random seed: 42")
    print("=" * 70)

    # ------------------------------------------------------------------
    # (1) Load data and identify feature columns
    # ------------------------------------------------------------------
    print("\n[1/7] Tải dữ liệu và xác định cột đặc trưng...")
    merged_df = load_and_merge_data()
    print(f"  Dataset: {len(merged_df)} hàng, {len(merged_df.columns)} cột")

    tech_cols, kw_cols = identify_feature_columns(merged_df)
    configs = get_feature_configs(tech_cols, kw_cols)

    print(f"  Config_C: {len(tech_cols)} tech + {len(kw_cols)} keyword "
          f"= {len(configs['Config_C'])} đặc trưng")

    # ------------------------------------------------------------------
    # (2) Train Config_C model
    # ------------------------------------------------------------------
    print(f"\n[2/7] Huấn luyện mô hình Config_C ({model_name})...")
    model, X_train, y_train, X_test, y_test = train_configc_model(
        merged_df=merged_df,
        tech_cols=tech_cols,
        kw_cols=kw_cols,
        cutoff=cutoff,
        model_name=model_name,
        random_state=42,
    )
    feature_names = X_test.columns.tolist()

    # ------------------------------------------------------------------
    # (3) Compute SHAP values
    # ------------------------------------------------------------------
    print("\n[3/7] Tính SHAP values cho Config_C...")
    shap_values = task11_shap.compute_shap_values(model, X_test, X_train=X_train)
    print(f"  SHAP shape: {_extract_shap_array(shap_values).shape}")

    # ------------------------------------------------------------------
    # (4) SHAP beeswarm plot — save to configc_shap_summary.png (NOT shap_summary.png)
    # ------------------------------------------------------------------
    print(f"\n[4/7] Lưu beeswarm SHAP plot → {SHAP_SUMMARY_PATH}")
    task11_shap.plot_shap_summary(shap_values, save_path=SHAP_SUMMARY_PATH)
    print(f"  Đã lưu: {SHAP_SUMMARY_PATH}")

    # ------------------------------------------------------------------
    # (5) Permutation importance — save to configc_permutation_importance.png
    #     (NOT permutation_importance.png)
    # ------------------------------------------------------------------
    print(f"\n[5/7] Tính và lưu permutation importance → {PERM_IMPORTANCE_PATH}")
    perm_imp = _plot_permutation_importance(
        model=model,
        X_test=X_test,
        y_test=y_test,
        save_path=PERM_IMPORTANCE_PATH,
        n_repeats=10,
        random_state=42,
        top_n=20,
    )

    # ------------------------------------------------------------------
    # (6) Rank keyword features by SHAP
    # ------------------------------------------------------------------
    print(f"\n[6/7] Xếp hạng đặc trưng từ khóa theo SHAP → {KW_RANKING_PATH}")
    keywords_by_dir = _build_keywords_by_dir()
    kw_ranking_df = rank_keyword_features_by_shap(
        shap_values=shap_values,
        feature_names=feature_names,
        keywords_by_dir=keywords_by_dir,
    )

    # ------------------------------------------------------------------
    # (7) Group contribution analysis: keyword % vs technical %
    # ------------------------------------------------------------------
    print("\n[7/7] Phân tích tỷ lệ đóng góp nhóm đặc trưng...")
    group_contrib = task11_shap.group_contribution_analysis(shap_values, feature_names)

    print("\n" + "=" * 70)
    print("KẾT QUẢ GROUP CONTRIBUTION (Config_C):")
    print(
        f"  Technical features: mean|SHAP| = {group_contrib['technical_mean_abs']:.6f} "
        f"({group_contrib['technical_share']:.1f}%)"
    )
    print(
        f"  Keyword   features: mean|SHAP| = {group_contrib['keyword_mean_abs']:.6f} "
        f"({group_contrib['keyword_share']:.1f}%)"
    )

    # ------------------------------------------------------------------
    # Print keyword ranking summary
    # ------------------------------------------------------------------
    if not kw_ranking_df.empty:
        print("\n" + "=" * 70)
        print(f"TOP TỪ KHÓA THEO SHAP (Config_C) — {len(kw_ranking_df)} từ khóa:")
        top_10 = kw_ranking_df.head(10)
        print(
            f"  {'Từ khóa':<35} {'Hướng':<10} "
            f"{'mean|SHAP|':>12} {'Nhất quán':>10}"
        )
        print("  " + "-" * 70)
        for _, row in top_10.iterrows():
            consistent_mark = "✓" if row["direction_consistent"] else "✗"
            print(
                f"  {row['keyword']:<35} {row['direction']:<10} "
                f"{row['mean_abs_shap']:>12.6f} {consistent_mark:>10}"
            )

        n_consistent = kw_ranking_df["direction_consistent"].sum()
        pct_consistent = (
            100.0 * n_consistent / len(kw_ranking_df) if len(kw_ranking_df) > 0 else 0
        )
        print(
            f"\n  Số từ khóa nhất quán về hướng: "
            f"{n_consistent}/{len(kw_ranking_df)} ({pct_consistent:.1f}%)"
        )

    print("\n" + "=" * 70)
    print("Output files:")
    print(f"  {SHAP_SUMMARY_PATH}")
    print(f"  {PERM_IMPORTANCE_PATH}")
    print(f"  {KW_RANKING_PATH}")
    print("=" * 70)

    return kw_ranking_df


# ---------------------------------------------------------------------------
# Sub-task 5.4 — Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_shap_configc()
