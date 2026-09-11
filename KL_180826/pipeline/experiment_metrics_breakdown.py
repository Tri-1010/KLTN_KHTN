"""
Góc 2 — Phân rã thước đo đánh giá: Config_A vs Config_C theo từng lớp.

So sánh Config_A (đặc trưng kỹ thuật) và Config_C (kỹ thuật + từ khóa) trên
Precision/Recall/F1 theo từng lớp (lớp 0 = "không tăng", lớp 1 = "tăng"),
cùng Balanced Accuracy và AUC-ROC, cho mỗi trong 4 thuật toán ML.

Thêm các dòng delta (config="delta_C_minus_A") để thể hiện đóng góp thực sự
của đặc trưng từ khóa — bao gồm cả đánh đổi (trade-off) giữa recall và precision.

Trả lời: thêm từ khóa có làm recall lớp "tăng" tốt hơn không, và đánh đổi là gì?

Sử dụng Time_Series_Split nhất quán với pipeline sản xuất (task10_train).
Random seed cố định = 42. Không ghi đè Production_Pipeline_Outputs.

Output: reports/metrics_breakdown.csv

Usage:
    python -m pipeline.experiment_metrics_breakdown
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
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.metrics import (
    balanced_accuracy_score,
    precision_recall_fscore_support,
    roc_auc_score,
)

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
OUTPUT_PATH = os.path.join(REPORTS_DIR, "metrics_breakdown.csv")


# ---------------------------------------------------------------------------
# Sub-task 3.1 — Per-class metrics (Req 2.2)
# ---------------------------------------------------------------------------


def compute_per_class_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: Optional[np.ndarray],
) -> Dict[str, float]:
    """Compute per-class Precision, Recall, F1 plus Balanced Accuracy and AUC-ROC.

    Uses:
        - ``sklearn.metrics.precision_recall_fscore_support(labels=[0, 1], zero_division=0)``
        - ``sklearn.metrics.balanced_accuracy_score``
        - ``sklearn.metrics.roc_auc_score`` (only when y_proba is not None)

    Args:
        y_true: True binary labels (0 or 1).
        y_pred: Predicted binary labels (0 or 1).
        y_proba: Predicted probabilities for class 1, shape (n_samples,).
                 Pass ``None`` to skip AUC-ROC computation.

    Returns:
        Dict with keys:
            precision_class0, recall_class0, f1_class0,
            precision_class1, recall_class1, f1_class1,
            balanced_accuracy, auc_roc.
        ``auc_roc`` is ``np.nan`` when y_proba is None or computation fails.

    Notes:
        ``zero_division=0`` ensures graceful handling of classes absent from
        predictions (e.g. a model that never predicts class 1 will get
        precision_class1=0.0 rather than raising a warning).
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)

    # Precision, Recall, F1 per class — labels=[0,1] fixes the order
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=[0, 1],
        zero_division=0,
    )

    bal_acc = balanced_accuracy_score(y_true, y_pred)

    if y_proba is not None:
        try:
            y_proba = np.asarray(y_proba, dtype=float)
            auc = float(roc_auc_score(y_true, y_proba))
        except ValueError:
            # roc_auc_score raises ValueError when only one class is present
            auc = np.nan
    else:
        auc = np.nan

    return {
        "precision_class0": float(precision[0]),
        "recall_class0": float(recall[0]),
        "f1_class0": float(f1[0]),
        "precision_class1": float(precision[1]),
        "recall_class1": float(recall[1]),
        "f1_class1": float(f1[1]),
        "balanced_accuracy": float(bal_acc),
        "auc_roc": float(auc),
    }


# ---------------------------------------------------------------------------
# Sub-task 3.2 — Main runner (Req 2.1–2.7, 6.3, 6.4)
# ---------------------------------------------------------------------------


def run_metrics_breakdown(
    cutoff: str = "2025Q1",
    unit: str = "quarter",
) -> pd.DataFrame:
    """Train Config_A and Config_C on all 4 ML algorithms; compute per-class metrics.

    Workflow:
    1. Load and merge feature/label data via ``load_and_merge_data()``.
    2. Split data using ``time_series_split(merged_df, cutoff=cutoff)`` — no shuffling.
    3. Identify technical and keyword feature columns via ``identify_feature_columns()``.
    4. For each of the 4 ML algorithms from ``build_ml_models()``:
       a. Train Config_A (tech features only) and Config_C (tech + keyword features).
       b. Fit imputer on training set; transform test set (no leakage).
       c. Compute per-class metrics via ``compute_per_class_metrics()``.
       d. Add delta row: config="delta_C_minus_A", values = Config_C − Config_A.
    5. Append ``unit`` and ``cutoff`` columns to all rows.
    6. Save to ``reports/metrics_breakdown.csv``.
    7. Return the DataFrame.

    Args:
        cutoff: Quarter string for time-series split (default "2025Q1"). Req 6.4.
        unit: Time unit label written to the output CSV (default "quarter"). Req 2.7.

    Returns:
        DataFrame saved to reports/metrics_breakdown.csv.

    Notes:
        - Random seed is fixed at 42 for all ML models (Req 6.3).
        - Time_Series_Split is used — data is NOT shuffled (Req 6.4).
        - Config_A = technical features only (no keyword features).
        - Config_C = technical + keyword features.
        - Delta rows (config="delta_C_minus_A") show the incremental effect
          of adding keyword features.
    """
    print("=" * 70)
    print("Góc 2 — Phân rã thước đo: Config_A vs Config_C")
    print(f"Cutoff: {cutoff}, Unit: {unit}, Random seed: 42")
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
    # Step 4: Get target for building models (need y_train for scale_pos_weight)
    # ------------------------------------------------------------------
    _, y_train_base = prepare_features(train_df, config_a_cols)

    # Build model instances — random_state=42 is set inside build_ml_models (Req 6.3)
    ml_models = build_ml_models(y_train_base)

    rows: List[Dict] = []

    # ------------------------------------------------------------------
    # Step 5: Train and evaluate each (model, config) pair
    # ------------------------------------------------------------------
    for model_name, model_template in ml_models.items():
        print(f"\n  Model: {model_name}")
        metrics_per_config: Dict[str, Dict[str, float]] = {}

        for config_name, feat_cols in [("Config_A", config_a_cols),
                                       ("Config_C", config_c_cols)]:
            # Fit imputer on training features (no leakage)
            imputer, numeric_cols = fit_imputer(train_df, feat_cols)

            # Prepare train and test
            X_train, y_train = prepare_features(train_df, feat_cols, imputer=None)
            X_test, y_test = prepare_features(test_df, feat_cols, imputer=imputer)

            # Align columns (remove non-numeric cols that imputer handled)
            X_train = X_train[numeric_cols]
            X_test = X_test[numeric_cols]

            # Clone model to avoid state leakage between configs
            import copy
            model = copy.deepcopy(model_template)

            # Train
            model.fit(X_train, y_train)

            # Predict
            y_pred = model.predict(X_test)

            # Probabilities (for AUC-ROC)
            try:
                y_proba = model.predict_proba(X_test)[:, 1]
            except AttributeError:
                y_proba = None

            # Compute metrics
            metrics = compute_per_class_metrics(
                y_true=y_test.values,
                y_pred=y_pred,
                y_proba=y_proba,
            )
            metrics_per_config[config_name] = metrics

            print(f"    {config_name}: bal_acc={metrics['balanced_accuracy']:.4f}, "
                  f"recall_class1={metrics['recall_class1']:.4f}, "
                  f"auc={metrics['auc_roc']:.4f}")

            row = {
                "model": model_name,
                "config": config_name,
                **metrics,
                "unit": unit,
                "cutoff": cutoff,
            }
            rows.append(row)

        # ------------------------------------------------------------------
        # Step 6: Compute delta row (Config_C − Config_A)
        # ------------------------------------------------------------------
        metric_keys = [
            "precision_class0", "recall_class0", "f1_class0",
            "precision_class1", "recall_class1", "f1_class1",
            "balanced_accuracy", "auc_roc",
        ]
        delta_metrics = {
            k: metrics_per_config["Config_C"][k] - metrics_per_config["Config_A"][k]
            for k in metric_keys
        }
        delta_row = {
            "model": model_name,
            "config": "delta_C_minus_A",
            **delta_metrics,
            "unit": unit,
            "cutoff": cutoff,
        }
        rows.append(delta_row)

        print(f"    delta recall_class1 = {delta_metrics['recall_class1']:+.4f}, "
              f"delta precision_class1 = {delta_metrics['precision_class1']:+.4f}")

    # ------------------------------------------------------------------
    # Step 7: Build DataFrame and save
    # ------------------------------------------------------------------
    result_df = pd.DataFrame(rows)

    # Ensure column order matches design spec
    col_order = [
        "model", "config",
        "precision_class0", "recall_class0", "f1_class0",
        "precision_class1", "recall_class1", "f1_class1",
        "balanced_accuracy", "auc_roc",
        "unit", "cutoff",
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
    delta_df = result_df[result_df["config"] == "delta_C_minus_A"].copy()

    print("\n" + "=" * 70)
    print("TÓM TẮT DELTA — Config_C minus Config_A")
    print(f"{'Model':<25} {'Δ recall_1':>12} {'Δ precision_1':>14} {'Δ bal_acc':>10} {'Δ AUC':>8}")
    print("-" * 70)
    for _, row in delta_df.iterrows():
        print(
            f"{row['model']:<25} "
            f"{row['recall_class1']:>+12.4f} "
            f"{row['precision_class1']:>+14.4f} "
            f"{row['balanced_accuracy']:>+10.4f} "
            f"{row['auc_roc']:>+8.4f}"
        )
    print("=" * 70)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_metrics_breakdown()
