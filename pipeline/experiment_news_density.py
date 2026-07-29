"""
Góc 3 — Phân tích đóng góp từ khóa theo mật độ tin tức.

So sánh đóng góp của đặc trưng từ khóa (Config_C − Config_A) giữa nhóm
(mã, kỳ) có tin dày (`has_min_news == 1`, tức news_count >= 5) và nhóm
tin thưa (`has_min_news == 0`), cho mỗi trong 4 thuật toán ML.

Mục tiêu: kiểm tra giả thuyết rằng tin tức không đủ dày là nguyên nhân
làm từ khóa kém hiệu quả trong toàn bộ tập test.

Sử dụng Time_Series_Split nhất quán với pipeline sản xuất (task10_train).
Random seed cố định = 42. Không ghi đè Production_Pipeline_Outputs.

Output: reports/news_density_analysis.csv

Usage:
    python -m pipeline.experiment_news_density
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

import copy
import os
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from pipeline.experiment_metrics_breakdown import compute_per_class_metrics
from pipeline.task10_train import (
    build_ml_models,
    fit_imputer,
    get_feature_configs,
    identify_feature_columns,
    load_and_merge_data,
    prepare_features,
    time_series_split,
)


# ---------------------------------------------------------------------------
# Output path
# ---------------------------------------------------------------------------

REPORTS_DIR = "reports"
OUTPUT_PATH = os.path.join(REPORTS_DIR, "news_density_analysis.csv")


# ---------------------------------------------------------------------------
# Sub-task 4.1 — split_by_news_density (Req 3.1)
# ---------------------------------------------------------------------------


def split_by_news_density(
    test_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split test_df into dense and sparse news groups.

    Uses the ``has_min_news`` column already present in the merged data:
      - ``has_min_news == 1`` → dense group (news_count >= 5)
      - ``has_min_news == 0`` → sparse group

    Args:
        test_df: Test-split DataFrame from ``time_series_split()``.
                 Must contain a ``has_min_news`` column.

    Returns:
        (dense_df, sparse_df) where:
          - dense_df  contains rows with has_min_news == 1
          - sparse_df contains rows with has_min_news == 0

    Notes:
        Either returned DataFrame may be empty if all rows belong to one
        group.  Callers should handle this via ``check_group_reliability()``.
    """
    dense_df = test_df[test_df["has_min_news"] == 1].copy()
    sparse_df = test_df[test_df["has_min_news"] == 0].copy()
    return dense_df, sparse_df


# ---------------------------------------------------------------------------
# Sub-task 4.2 — check_group_reliability (Req 3.5)
# ---------------------------------------------------------------------------


def check_group_reliability(
    group_df: pd.DataFrame,
    min_samples: int = 20,
) -> Tuple[bool, str]:
    """Check whether a density group has enough samples and label diversity.

    A group is considered NOT reliable if:
      1. ``len(group_df) < min_samples``  → "Không đủ mẫu: N={n} < {min_samples}"
      2. Only 1 unique label class in ``group_df['label_basic']``
         → "Chỉ có 1 lớp nhãn"
      3. Both conditions fail → both messages combined

    Args:
        group_df: Sub-DataFrame representing one density group (dense or sparse).
        min_samples: Minimum required samples for reliability (default 20).

    Returns:
        (is_reliable, warning_message) where:
          - is_reliable is True only when both criteria pass
          - warning_message is "" when reliable, or a descriptive warning

    Notes (Req 6.7):
        Groups with fewer than ``min_samples`` rows or only one label class
        produce statistically unreliable metric estimates.  We still compute
        metrics for completeness (Req 6.6) but flag them with a warning.
    """
    n = len(group_df)
    warnings_parts: List[str] = []

    # Condition 1: insufficient samples
    if n < min_samples:
        warnings_parts.append(f"Không đủ mẫu: N={n} < {min_samples}")

    # Condition 2: only one label class
    if "label_basic" in group_df.columns:
        n_classes = group_df["label_basic"].nunique()
        if n_classes < 2:
            warnings_parts.append("Chỉ có 1 lớp nhãn")

    if warnings_parts:
        return (False, "; ".join(warnings_parts))

    return (True, "")


# ---------------------------------------------------------------------------
# Sub-task 4.3 — run_news_density_analysis (Req 3.1–3.6)
# ---------------------------------------------------------------------------


def run_news_density_analysis(
    cutoff: str = "2025Q1",
) -> pd.DataFrame:
    """Train Config_A and Config_C; evaluate per news-density group.

    Workflow:
    1. Load and merge feature/label data via ``load_and_merge_data()``.
    2. Split data using ``time_series_split(merged_df, cutoff=cutoff)`` — no shuffling.
    3. Identify technical and keyword feature columns; build feature configs.
    4. For each of the 4 ML algorithms from ``build_ml_models()``:
       a. Train Config_A (tech features only) and Config_C (tech + keyword).
       b. Split TEST set into dense/sparse via ``split_by_news_density()``.
       c. For each density group:
          - Call ``check_group_reliability()`` — compute metrics regardless,
            but mark ``reliable=False`` and populate ``warning`` if not reliable.
          - Compute per-class metrics via ``compute_per_class_metrics()``.
          - Append rows for Config_A, Config_C, and delta (Config_C - Config_A).
    5. Collect columns: model, density_group, config, n_samples, reliable,
       warning, balanced_accuracy, recall_class1, precision_class1.
    6. Save to ``reports/news_density_analysis.csv``.
    7. Return DataFrame.

    Args:
        cutoff: Quarter string for time-series split (default "2025Q1"). Req 6.4.

    Returns:
        DataFrame saved to reports/news_density_analysis.csv.

    Notes:
        - Random seed is fixed at 42 for all ML models (Req 6.3).
        - Time_Series_Split is used — data is NOT shuffled (Req 6.4).
        - Config_A = technical features only.
        - Config_C = technical + keyword features.
        - Delta rows (config="delta_C_minus_A") show incremental effect of keywords.
        - Unreliable groups are still included in output with reliable=False (Req 6.6).
    """
    print("=" * 70)
    print("Góc 3 — Phân tích theo mật độ tin: Config_A vs Config_C")
    print(f"Cutoff: {cutoff}, Random seed: 42")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Step 1: Load data
    # ------------------------------------------------------------------
    merged = load_and_merge_data()
    print(f"Dataset: {len(merged)} rows, {len(merged.columns)} columns")

    # ------------------------------------------------------------------
    # Step 2: Time-series split (Req 6.4 — no shuffling)
    # ------------------------------------------------------------------
    train_df, test_df = time_series_split(merged, cutoff=cutoff)
    print(f"Train: {len(train_df)} rows | Test: {len(test_df)} rows")

    # ------------------------------------------------------------------
    # Step 3: Identify feature columns
    # ------------------------------------------------------------------
    tech_cols, kw_cols = identify_feature_columns(merged)
    feature_configs = get_feature_configs(tech_cols, kw_cols)

    config_a_cols = feature_configs["Config_A"]
    config_c_cols = feature_configs["Config_C"]

    print(f"Config_A features: {len(config_a_cols)} technical columns")
    print(f"Config_C features: {len(config_c_cols)} total columns "
          f"({len(tech_cols)} tech + {len(kw_cols)} keyword)")

    # ------------------------------------------------------------------
    # Step 4: Split test set into density groups
    # ------------------------------------------------------------------
    dense_df, sparse_df = split_by_news_density(test_df)
    print(f"\nTest split — dense: {len(dense_df)} rows | sparse: {len(sparse_df)} rows")

    density_groups = [
        ("dense", dense_df),
        ("sparse", sparse_df),
    ]

    # ------------------------------------------------------------------
    # Step 5: Build models (need y_train for scale_pos_weight)
    # ------------------------------------------------------------------
    _, y_train_base = prepare_features(train_df, config_a_cols)
    ml_models = build_ml_models(y_train_base)

    rows: List[Dict] = []

    # ------------------------------------------------------------------
    # Step 6: Train and evaluate each (model, density_group, config) combo
    # ------------------------------------------------------------------
    for model_name, model_template in ml_models.items():
        print(f"\n  Model: {model_name}")

        # Train Config_A and Config_C on FULL training set (not split by density)
        trained: Dict[str, object] = {}
        test_preds: Dict[str, Dict] = {}  # config_name -> {y_pred, y_proba}

        for config_name, feat_cols in [("Config_A", config_a_cols),
                                       ("Config_C", config_c_cols)]:
            # Fit imputer on training features (no leakage)
            imputer, numeric_cols = fit_imputer(train_df, feat_cols)

            # Prepare train
            X_train, y_train = prepare_features(train_df, feat_cols, imputer=None)
            X_train = X_train[numeric_cols]

            # Clone model to avoid state leakage between configs
            model = copy.deepcopy(model_template)
            model.fit(X_train, y_train)

            trained[config_name] = {
                "model": model,
                "imputer": imputer,
                "numeric_cols": numeric_cols,
                "feat_cols": feat_cols,
            }

        # For each density group, evaluate Config_A and Config_C
        for group_name, group_df in density_groups:
            print(f"    Group: {group_name} (n={len(group_df)})")

            # Check group reliability
            is_reliable, warning_msg = check_group_reliability(group_df)

            if not is_reliable:
                print(f"      Warning: {warning_msg}")

            # Skip empty groups entirely (can't compute metrics)
            if len(group_df) == 0:
                print(f"      Skipping empty group: {group_name}")
                continue

            # Collect metrics per config for this density group
            metrics_per_config: Dict[str, Dict[str, float]] = {}

            for config_name in ("Config_A", "Config_C"):
                info = trained[config_name]
                model = info["model"]
                imputer = info["imputer"]
                numeric_cols = info["numeric_cols"]
                feat_cols = info["feat_cols"]

                # Prepare group features using training imputer
                X_group, y_group = prepare_features(
                    group_df, feat_cols, imputer=imputer
                )
                X_group = X_group[numeric_cols]

                # Predict
                y_pred = model.predict(X_group)

                # Probabilities
                try:
                    y_proba = model.predict_proba(X_group)[:, 1]
                except AttributeError:
                    y_proba = None

                # Compute metrics — always compute even if not reliable (Req 6.6)
                metrics = compute_per_class_metrics(
                    y_true=y_group.values,
                    y_pred=y_pred,
                    y_proba=y_proba,
                )
                metrics_per_config[config_name] = metrics

                print(
                    f"      {config_name}: bal_acc={metrics['balanced_accuracy']:.4f}, "
                    f"recall_class1={metrics['recall_class1']:.4f}, "
                    f"precision_class1={metrics['precision_class1']:.4f}"
                )

                rows.append({
                    "model": model_name,
                    "density_group": group_name,
                    "config": config_name,
                    "n_samples": len(group_df),
                    "reliable": is_reliable,
                    "warning": warning_msg,
                    "balanced_accuracy": metrics["balanced_accuracy"],
                    "recall_class1": metrics["recall_class1"],
                    "precision_class1": metrics["precision_class1"],
                })

            # Delta row: Config_C − Config_A
            if "Config_A" in metrics_per_config and "Config_C" in metrics_per_config:
                delta_metrics = {
                    "balanced_accuracy": (
                        metrics_per_config["Config_C"]["balanced_accuracy"]
                        - metrics_per_config["Config_A"]["balanced_accuracy"]
                    ),
                    "recall_class1": (
                        metrics_per_config["Config_C"]["recall_class1"]
                        - metrics_per_config["Config_A"]["recall_class1"]
                    ),
                    "precision_class1": (
                        metrics_per_config["Config_C"]["precision_class1"]
                        - metrics_per_config["Config_A"]["precision_class1"]
                    ),
                }

                rows.append({
                    "model": model_name,
                    "density_group": group_name,
                    "config": "delta_C_minus_A",
                    "n_samples": len(group_df),
                    "reliable": is_reliable,
                    "warning": warning_msg,
                    "balanced_accuracy": delta_metrics["balanced_accuracy"],
                    "recall_class1": delta_metrics["recall_class1"],
                    "precision_class1": delta_metrics["precision_class1"],
                })

                print(
                    f"      delta recall_class1 = {delta_metrics['recall_class1']:+.4f}, "
                    f"delta precision_class1 = {delta_metrics['precision_class1']:+.4f}"
                )

    # ------------------------------------------------------------------
    # Step 7: Build DataFrame and save
    # ------------------------------------------------------------------
    result_df = pd.DataFrame(rows)

    if result_df.empty:
        print("\nCảnh báo: Không có kết quả nào để lưu (tất cả các nhóm đều rỗng).")
        result_df = pd.DataFrame(columns=[
            "model", "density_group", "config", "n_samples",
            "reliable", "warning", "balanced_accuracy",
            "recall_class1", "precision_class1",
        ])
    else:
        # Ensure column order matches design spec
        col_order = [
            "model", "density_group", "config", "n_samples",
            "reliable", "warning", "balanced_accuracy",
            "recall_class1", "precision_class1",
        ]
        result_df = result_df[col_order]

    os.makedirs(REPORTS_DIR, exist_ok=True)
    result_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"\nKết quả đã lưu vào: {OUTPUT_PATH}")

    # ------------------------------------------------------------------
    # Step 8: Print summary
    # ------------------------------------------------------------------
    _print_summary(result_df)

    return result_df


# ---------------------------------------------------------------------------
# Helper — print summary
# ---------------------------------------------------------------------------


def _print_summary(result_df: pd.DataFrame) -> None:
    """Print a compact summary of delta rows for quick interpretation."""
    if result_df.empty:
        return

    delta_df = result_df[result_df["config"] == "delta_C_minus_A"].copy()
    if delta_df.empty:
        return

    print("\n" + "=" * 70)
    print("TÓM TẮT DELTA — Config_C minus Config_A theo nhóm mật độ tin")
    header = (
        f"{'Model':<25} {'Nhóm':<8} {'Đáng tin':>9} "
        f"{'Δ recall_1':>12} {'Δ precision_1':>14} {'Δ bal_acc':>10}"
    )
    print(header)
    print("-" * 80)
    for _, row in delta_df.iterrows():
        reliable_flag = "Có" if row["reliable"] else "Không"
        print(
            f"{row['model']:<25} {row['density_group']:<8} {reliable_flag:>9} "
            f"{row['recall_class1']:>+12.4f} "
            f"{row['precision_class1']:>+14.4f} "
            f"{row['balanced_accuracy']:>+10.4f}"
        )
    print("=" * 70)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_news_density_analysis()
