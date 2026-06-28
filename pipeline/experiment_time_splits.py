"""
Experiment: does the keyword contribution (H1) change under different
time-series train/test split points?

This is an ad-hoc research script (not part of the 12-task pipeline). It reuses
TASK 10's data-prep / split / training functions to evaluate Config_A
(technical only) vs Config_C (technical + keyword) across several train cutoffs,
so we can see whether combining keyword features helps in any time window.

Usage:
    python -m pipeline.experiment_time_splits
"""

from __future__ import annotations

import sys

# Ensure UTF-8 output on Windows (vnstock/banner safety; harmless elsewhere).
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

from typing import Any, Dict, List

import numpy as np
import pandas as pd

from pipeline.task10_train import (
    NaiveMomentumBaseline,
    build_ml_models,
    evaluate_model,
    fit_imputer,
    get_feature_configs,
    identify_feature_columns,
    load_and_merge_data,
    prepare_features,
    time_series_split,
)

# Cutoffs to try. Each is the first quarter that belongs to the TEST set;
# everything strictly before it is training data.
CANDIDATE_CUTOFFS = [
    "2024Q1",
    "2024Q3",
    "2025Q1",
    "2025Q3",
    "2026Q1",
]

CONFIGS_TO_RUN = ("Config_A", "Config_C")


def _evaluate_cutoff(
    merged: pd.DataFrame,
    tech_cols: List[str],
    kw_cols: List[str],
    cutoff: str,
) -> List[Dict[str, Any]]:
    """Train the 4 ML models on Config_A and Config_C for one cutoff."""
    configs = get_feature_configs(tech_cols, kw_cols)
    train_df, test_df = time_series_split(merged, cutoff=cutoff)

    n_train_q = train_df["quarter_id"].nunique()
    n_test_q = test_df["quarter_id"].nunique()

    rows: List[Dict[str, Any]] = []
    for config_name in CONFIGS_TO_RUN:
        feature_cols = configs[config_name]
        available = [c for c in feature_cols if c in train_df.columns]

        imputer, _ = fit_imputer(train_df, available)
        X_train, y_train = prepare_features(train_df, available, imputer=imputer)
        X_test, y_test = prepare_features(test_df, available, imputer=imputer)
        common = [c for c in X_train.columns if c in X_test.columns]
        X_train, X_test = X_train[common], X_test[common]

        # Skip degenerate splits (one class in train or test).
        if y_train.nunique() < 2 or y_test.nunique() < 2:
            continue

        models = build_ml_models(y_train)
        for mname, mmodel in models.items():
            mmodel.fit(X_train, y_train)
            res = evaluate_model(mmodel, X_test, y_test, mname, config_name)
            res["cutoff"] = cutoff
            res["train_quarters"] = n_train_q
            res["test_quarters"] = n_test_q
            res["test_samples"] = len(X_test)
            rows.append(res)
    return rows


def run_experiment() -> pd.DataFrame:
    merged = load_and_merge_data()
    tech_cols, kw_cols = identify_feature_columns(merged)

    all_rows: List[Dict[str, Any]] = []
    for cutoff in CANDIDATE_CUTOFFS:
        all_rows.extend(_evaluate_cutoff(merged, tech_cols, kw_cols, cutoff))

    df = pd.DataFrame(all_rows)
    if df.empty:
        print("No valid splits produced results.")
        return df

    # Build a per-(cutoff, model) comparison of Config_A vs Config_C.
    pivot = df.pivot_table(
        index=["cutoff", "test_quarters", "test_samples", "model"],
        columns="config",
        values="balanced_accuracy",
    ).reset_index()
    pivot["delta_C_minus_A"] = pivot["Config_C"] - pivot["Config_A"]

    auc_pivot = df.pivot_table(
        index=["cutoff", "model"],
        columns="config",
        values="auc_roc",
    ).reset_index()
    auc_pivot = auc_pivot.rename(
        columns={"Config_A": "auc_A", "Config_C": "auc_C"}
    )
    pivot = pivot.merge(auc_pivot, on=["cutoff", "model"], how="left")
    pivot["auc_delta_C_minus_A"] = pivot["auc_C"] - pivot["auc_A"]

    out_path = "reports/time_split_experiment.csv"
    pivot.to_csv(out_path, index=False)

    # Console summary
    pd.set_option("display.width", 140)
    pd.set_option("display.max_columns", 20)
    print("\n" + "=" * 70)
    print("TIME-SPLIT EXPERIMENT — Config_A vs Config_C (Balanced Accuracy)")
    print("=" * 70)
    show_cols = [
        "cutoff",
        "test_quarters",
        "test_samples",
        "model",
        "Config_A",
        "Config_C",
        "delta_C_minus_A",
    ]
    print(pivot[show_cols].round(4).to_string(index=False))

    print("\n--- Mean delta (Config_C − Config_A) by cutoff ---")
    by_cut = (
        pivot.groupby("cutoff")["delta_C_minus_A"].mean().round(4)
    )
    print(by_cut.to_string())

    n_better = int((pivot["delta_C_minus_A"] > 0).sum())
    total = len(pivot)
    print(
        f"\nConfig_C beat Config_A in {n_better}/{total} "
        f"(cutoff × model) combinations."
    )
    print(f"Overall mean delta: {pivot['delta_C_minus_A'].mean():.4f}")
    print(f"Saved detailed results to {out_path}")
    return pivot


if __name__ == "__main__":
    run_experiment()
