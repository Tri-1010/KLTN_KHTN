"""
TASK 11: SHAP_Analyzer
Analyze feature importance using SHAP values, permutation importance,
and tree-based importance for the best Config_C model.

Steps:
    1. Tree-based feature importance (gain-based) — Req 11.1
    2. Permutation importance on test set — Req 11.2
    3. SHAP values (beeswarm + bar plots) — Req 11.3
    4. Top keyword analysis with direction verification — Req 11.4, 11.5
    5. Group contribution analysis (technical vs keyword) — Req 11.6
    6. SHAP case studies (waterfall plots) — Req 11.7

Inputs:
    models/best_model.pkl
    data/features/technical_features.csv
    data/features/keyword_features.csv
    data/aggregated/master_with_labels.csv
    reports/model_comparison.csv

Outputs:
    reports/feature_importance.png
    reports/permutation_importance.png
    reports/shap_summary.png
    reports/shap_bar.png
    reports/top_keywords_analysis.csv
    reports/shap_case_study_{ticker}_{quarter}.png
"""

from __future__ import annotations

import json
import os
import warnings
from typing import Any, Dict, List, Optional, Tuple

import joblib
import matplotlib
matplotlib.use("Agg")  # Headless backend — must be set before importing pyplot
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.inspection import permutation_importance

from pipeline.logging_config import setup_logger
from pipeline.task10_train import (
    BEST_MODEL_PATH,
    LABELS_PATH,
    KW_FEATURES_PATH,
    MODEL_COMPARISON_PATH,
    TECH_FEATURES_PATH,
    identify_feature_columns,
    load_and_merge_data,
    prepare_features,
    fit_imputer,
    time_series_split,
    get_feature_configs,
    build_ml_models,
    build_baselines,
    evaluate_model,
)
from pipeline.task8_keywords import get_curated_keywords

logger = setup_logger("TASK_11")

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPORTS_DIR = "reports"
FEATURE_IMPORTANCE_PATH = os.path.join(REPORTS_DIR, "feature_importance.png")
PERMUTATION_IMPORTANCE_PATH = os.path.join(REPORTS_DIR, "permutation_importance.png")
SHAP_SUMMARY_PATH = os.path.join(REPORTS_DIR, "shap_summary.png")
SHAP_BAR_PATH = os.path.join(REPORTS_DIR, "shap_bar.png")
TOP_KEYWORDS_PATH = os.path.join(REPORTS_DIR, "top_keywords_analysis.csv")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

KW_PREFIXES = ("kw_", "kw_norm_", "tfidf_")
KW_EXACT_COLS = {
    "pos_score",
    "neg_score",
    "sentiment_ratio",
    "news_count",
    "news_count_log",
    "has_min_news",
}


def _is_keyword_feature(col: str) -> bool:
    """Return True if *col* is a keyword-derived feature."""
    return col in KW_EXACT_COLS or any(col.startswith(p) for p in KW_PREFIXES)


def _feature_color(col: str) -> str:
    """Return a colour hex string: blue for technical, orange for keyword."""
    return "#E07020" if _is_keyword_feature(col) else "#2070C0"


def _ensure_reports_dir() -> None:
    os.makedirs(REPORTS_DIR, exist_ok=True)


def _keyword_direction_map() -> Dict[str, str]:
    """Build keyword → direction mapping from the curated list."""
    kw_by_dir = get_curated_keywords()
    mapping: Dict[str, str] = {}
    for direction, keywords in kw_by_dir.items():
        for kw in keywords:
            mapping[kw] = direction
    return mapping


def _extract_keyword_name(col: str) -> Optional[str]:
    """Extract the raw keyword string from a feature column name.

    E.g. ``"kw_norm_lợi nhuận tăng"`` → ``"lợi nhuận tăng"``.
    Returns ``None`` if the column is not a per-keyword feature.
    """
    for prefix in ("kw_norm_", "tfidf_", "kw_"):
        if col.startswith(prefix):
            return col[len(prefix):]
    return None


# ---------------------------------------------------------------------------
# Data loading (shared across sub-tasks)
# ---------------------------------------------------------------------------


def _load_best_model_meta() -> Dict[str, Any]:
    """Load the best-model metadata written by TASK 10.

    Returns a dict with keys ``config_name``, ``feature_cols``, ``model_name``.
    Falls back to an empty dict (caller defaults to Config_C) if the metadata
    file is missing or unreadable.
    """
    meta_path = BEST_MODEL_PATH + ".meta.json"
    if not os.path.isfile(meta_path):
        logger.warning(
            "Best model metadata not found at %s; assuming Config_C.", meta_path
        )
        return {}
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Could not read best model metadata: %s", exc)
        return {}


def load_shap_data(
    cutoff: str = "2025Q1",
) -> Tuple[Any, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, List[str], List[str]]:
    """Load best model and prepare the train/test data it was trained on.

    The feature configuration is read from the best-model metadata written by
    TASK 10 (``best_model.pkl.meta.json``). This ensures the SHAP/feature
    matrix matches the saved model even when the best model is not Config_C.

    Returns:
        (model, X_train, y_train, X_test, y_test, tech_cols, kw_cols)
    """
    model = joblib.load(BEST_MODEL_PATH)
    logger.info("Loaded best model from %s", BEST_MODEL_PATH)

    meta = _load_best_model_meta()

    merged = load_and_merge_data()
    tech_cols, kw_cols = identify_feature_columns(merged)
    configs = get_feature_configs(tech_cols, kw_cols)

    best_config = meta.get("config_name") or "Config_C"
    selected_cols = meta.get("feature_cols") or configs.get(best_config, configs["Config_C"])
    logger.info(
        "SHAP analysis using %s (%d features) per best-model metadata.",
        best_config, len(selected_cols),
    )

    train_df, test_df = time_series_split(merged, cutoff=cutoff)

    train_imputer, _ = fit_imputer(train_df, selected_cols)
    X_train, y_train = prepare_features(train_df, selected_cols, imputer=train_imputer)
    X_test, y_test = prepare_features(test_df, selected_cols, imputer=train_imputer)

    # Align columns
    common = [c for c in X_train.columns if c in X_test.columns]
    X_train = X_train[common]
    X_test = X_test[common]

    logger.info(
        "Config_C data — train: %d samples, test: %d samples, features: %d",
        len(X_train), len(X_test), len(common),
    )
    return model, X_train, y_train, X_test, y_test, tech_cols, kw_cols


# ---------------------------------------------------------------------------
# 17.1 — Tree-based feature importance  (Req 11.1)
# ---------------------------------------------------------------------------


def plot_tree_importance(
    model: Any,
    feature_names: List[str],
    top_n: int = 30,
    save_path: str = FEATURE_IMPORTANCE_PATH,
) -> pd.Series:
    """Extract gain-based feature importances and plot top *top_n*.

    Uses ``model.feature_importances_`` which is available on
    XGBoost, LightGBM, and RandomForest.

    Returns:
        Sorted Series of all feature importances.
    """
    _ensure_reports_dir()

    importances = pd.Series(model.feature_importances_, index=feature_names)
    importances = importances.sort_values(ascending=False)

    top = importances.head(top_n)
    colors = [_feature_color(c) for c in top.index]

    fig, ax = plt.subplots(figsize=(10, 8))
    top.iloc[::-1].plot.barh(ax=ax, color=colors[::-1])
    ax.set_xlabel("Feature Importance (Gain)")
    ax.set_title(f"Top {top_n} Features — Tree-Based Importance")

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#2070C0", label="Technical"),
        Patch(facecolor="#E07020", label="Keyword"),
    ]
    ax.legend(handles=legend_elements, loc="lower right")

    plt.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    logger.info("Saved tree-based feature importance plot to %s", save_path)

    return importances


# ---------------------------------------------------------------------------
# 17.2 — Permutation importance  (Req 11.2)
# ---------------------------------------------------------------------------


def plot_permutation_importance(
    model: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    top_n: int = 30,
    save_path: str = PERMUTATION_IMPORTANCE_PATH,
    n_repeats: int = 10,
    random_state: int = 42,
) -> pd.Series:
    """Compute and plot permutation importance on the test set.

    Returns:
        Sorted Series of mean permutation importances.
    """
    _ensure_reports_dir()

    result = permutation_importance(
        model,
        X_test,
        y_test,
        n_repeats=n_repeats,
        random_state=random_state,
        n_jobs=-1,
        scoring="balanced_accuracy",
    )

    perm_imp = pd.Series(result.importances_mean, index=X_test.columns)
    perm_imp = perm_imp.sort_values(ascending=False)

    top = perm_imp.head(top_n)
    colors = [_feature_color(c) for c in top.index]

    fig, ax = plt.subplots(figsize=(10, 8))
    top.iloc[::-1].plot.barh(ax=ax, color=colors[::-1])
    ax.set_xlabel("Mean Decrease in Balanced Accuracy")
    ax.set_title(f"Top {top_n} Features — Permutation Importance")

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#2070C0", label="Technical"),
        Patch(facecolor="#E07020", label="Keyword"),
    ]
    ax.legend(handles=legend_elements, loc="lower right")

    plt.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    logger.info("Saved permutation importance plot to %s", save_path)

    return perm_imp


# ---------------------------------------------------------------------------
# 17.3 — SHAP values  (Req 11.3)
# ---------------------------------------------------------------------------


def compute_shap_values(
    model: Any,
    X_test: pd.DataFrame,
    X_train: Optional[pd.DataFrame] = None,
) -> shap.Explanation:
    """Compute SHAP values, choosing an explainer appropriate to the model.

    - Tree models (XGBoost, LightGBM, RandomForest) → ``shap.TreeExplainer``
    - Linear models (LogisticRegression) → ``shap.LinearExplainer``
    - Anything else → model-agnostic ``shap.Explainer`` (falls back to a
      permutation/kernel explainer)

    Args:
        model: The trained best model.
        X_test: Test feature matrix to explain.
        X_train: Optional training matrix used as the background/masker for
            non-tree explainers. Falls back to X_test if not provided.

    Returns:
        shap.Explanation object.
    """
    background = X_train if X_train is not None else X_test
    model_type = type(model).__name__

    has_tree_importance = hasattr(model, "feature_importances_")

    try:
        if has_tree_importance:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer(X_test)
        elif hasattr(model, "coef_"):
            # Linear model (e.g. LogisticRegression)
            explainer = shap.LinearExplainer(model, background)
            shap_values = explainer(X_test)
        else:
            # Model-agnostic fallback
            predict_fn = (
                model.predict_proba if hasattr(model, "predict_proba")
                else model.predict
            )
            explainer = shap.Explainer(predict_fn, background)
            shap_values = explainer(X_test)
    except Exception as exc:
        # Last-resort fallback: model-agnostic explainer on probabilities.
        logger.warning(
            "Primary SHAP explainer failed for %s (%s); "
            "falling back to model-agnostic explainer.",
            model_type, exc,
        )
        predict_fn = (
            model.predict_proba if hasattr(model, "predict_proba")
            else model.predict
        )
        explainer = shap.Explainer(predict_fn, background)
        shap_values = explainer(X_test)

    # For binary classifiers, shap_values.values may have shape
    # (n_samples, n_features, 2). We take the class-1 slice.
    if shap_values.values.ndim == 3:
        shap_values = shap_values[..., 1]

    logger.info(
        "Computed SHAP values with %s: shape=%s",
        model_type, shap_values.values.shape,
    )
    return shap_values


def plot_shap_summary(
    shap_values: shap.Explanation,
    save_path: str = SHAP_SUMMARY_PATH,
) -> None:
    """Generate beeswarm summary plot."""
    _ensure_reports_dir()

    fig, ax = plt.subplots(figsize=(12, 10))
    shap.summary_plot(
        shap_values.values,
        features=shap_values.data,
        feature_names=shap_values.feature_names,
        show=False,
        max_display=30,
    )
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close("all")
    logger.info("Saved SHAP beeswarm summary to %s", save_path)


def plot_shap_bar(
    shap_values: shap.Explanation,
    save_path: str = SHAP_BAR_PATH,
) -> None:
    """Generate mean |SHAP| bar plot."""
    _ensure_reports_dir()

    fig, ax = plt.subplots(figsize=(12, 10))
    shap.plots.bar(shap_values, show=False, max_display=30)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close("all")
    logger.info("Saved SHAP bar plot to %s", save_path)


# ---------------------------------------------------------------------------
# 17.4 — Top keyword analysis  (Req 11.4, 11.5)
# ---------------------------------------------------------------------------


def analyze_top_keywords(
    shap_values: shap.Explanation,
    feature_names: List[str],
    top_n: int = 20,
    save_path: str = TOP_KEYWORDS_PATH,
) -> pd.DataFrame:
    """Identify top keywords by mean |SHAP| and verify direction alignment.

    For each keyword feature, records:
    - keyword name
    - feature column name
    - direction label (positive / negative / neutral)
    - mean SHAP value (signed)
    - mean |SHAP| value
    - actual SHAP direction ("positive" if mean SHAP > 0 else "negative")
    - aligned (True if direction label matches actual SHAP direction)

    Logs mismatches as anomalies (Req 11.5).

    Returns:
        DataFrame saved to *save_path*.
    """
    _ensure_reports_dir()

    direction_map = _keyword_direction_map()

    vals = shap_values.values  # (n_samples, n_features)
    mean_shap = vals.mean(axis=0)
    mean_abs_shap = np.abs(vals).mean(axis=0)

    records: List[Dict[str, Any]] = []
    for i, col in enumerate(feature_names):
        kw_name = _extract_keyword_name(col)
        if kw_name is None:
            continue  # not a per-keyword feature
        direction = direction_map.get(kw_name, "unknown")
        actual_dir = "positive" if mean_shap[i] > 0 else "negative"
        aligned = True
        if direction == "positive" and actual_dir != "positive":
            aligned = False
        elif direction == "negative" and actual_dir != "negative":
            aligned = False
        # neutral keywords: alignment check not applicable
        records.append({
            "keyword": kw_name,
            "feature_column": col,
            "direction_label": direction,
            "mean_shap": float(mean_shap[i]),
            "mean_abs_shap": float(mean_abs_shap[i]),
            "actual_shap_direction": actual_dir,
            "aligned": aligned,
        })

    df = pd.DataFrame(records)
    if df.empty:
        logger.warning("No keyword features found in SHAP values.")
        return df

    df = df.sort_values("mean_abs_shap", ascending=False)
    top_df = df.head(top_n).copy()

    # Log mismatches (Req 11.5)
    mismatches = top_df[
        (top_df["direction_label"].isin(["positive", "negative"]))
        & (~top_df["aligned"])
    ]
    if not mismatches.empty:
        logger.warning(
            "ANOMALY: %d keyword(s) have SHAP direction mismatching their label:",
            len(mismatches),
        )
        for _, row in mismatches.iterrows():
            logger.warning(
                "  %s — label=%s, actual SHAP direction=%s (mean SHAP=%.6f)",
                row["keyword"],
                row["direction_label"],
                row["actual_shap_direction"],
                row["mean_shap"],
            )
    else:
        logger.info(
            "All top %d keyword directions are aligned with their labels.", top_n
        )

    # Verify positive-direction keywords have positive mean SHAP values
    pos_kws = top_df[top_df["direction_label"] == "positive"]
    if not pos_kws.empty:
        pos_with_neg_shap = pos_kws[pos_kws["mean_shap"] < 0]
        if not pos_with_neg_shap.empty:
            logger.warning(
                "ANOMALY: %d positive-direction keyword(s) have negative mean SHAP:",
                len(pos_with_neg_shap),
            )
            for _, row in pos_with_neg_shap.iterrows():
                logger.warning("  %s: mean_shap=%.6f", row["keyword"], row["mean_shap"])

    top_df.to_csv(save_path, index=False, encoding="utf-8")
    logger.info("Saved top %d keyword analysis to %s", top_n, save_path)

    return top_df


# ---------------------------------------------------------------------------
# 17.5 — Group contribution analysis  (Req 11.6)
# ---------------------------------------------------------------------------


def group_contribution_analysis(
    shap_values: shap.Explanation,
    feature_names: List[str],
) -> Dict[str, float]:
    """Calculate total mean |SHAP| for technical vs keyword feature groups.

    Reports percentage share as empirical evidence for H1.

    Returns:
        Dict with keys ``"technical_share"``, ``"keyword_share"``,
        ``"technical_mean_abs"``, ``"keyword_mean_abs"``.
    """
    vals = shap_values.values  # (n_samples, n_features)
    mean_abs = np.abs(vals).mean(axis=0)

    tech_total = 0.0
    kw_total = 0.0

    for i, col in enumerate(feature_names):
        if _is_keyword_feature(col):
            kw_total += mean_abs[i]
        else:
            tech_total += mean_abs[i]

    grand_total = tech_total + kw_total
    if grand_total == 0:
        tech_share = 0.0
        kw_share = 0.0
    else:
        tech_share = tech_total / grand_total * 100
        kw_share = kw_total / grand_total * 100

    logger.info("=" * 60)
    logger.info("GROUP CONTRIBUTION ANALYSIS (H1 Evidence)")
    logger.info("=" * 60)
    logger.info(
        "Technical features: mean|SHAP| = %.6f  (%.1f%%)",
        tech_total, tech_share,
    )
    logger.info(
        "Keyword features:   mean|SHAP| = %.6f  (%.1f%%)",
        kw_total, kw_share,
    )
    logger.info("=" * 60)

    if kw_share > 0:
        logger.info(
            "Keyword features contribute %.1f%% of total SHAP importance, "
            "providing empirical evidence for H1.",
            kw_share,
        )
    else:
        logger.info(
            "Keyword features contribute 0%% of total SHAP importance. "
            "This suggests keywords may not add predictive value (H1 not supported)."
        )

    return {
        "technical_mean_abs": tech_total,
        "keyword_mean_abs": kw_total,
        "technical_share": tech_share,
        "keyword_share": kw_share,
    }


# ---------------------------------------------------------------------------
# 17.6 — SHAP case studies  (Req 11.7)
# ---------------------------------------------------------------------------


def generate_case_studies(
    shap_values: shap.Explanation,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    test_df: pd.DataFrame,
    cutoff: str = "2025Q1",
    max_cases: int = 3,
) -> List[str]:
    """Identify cases correctly predicted by Config_C but not Config_A.

    Generates SHAP waterfall plots for up to *max_cases* such pairs.

    Args:
        shap_values: SHAP Explanation for Config_C test set.
        X_test: Config_C test features (aligned with shap_values).
        y_test: True labels for test set.
        test_df: Original test DataFrame with ticker and quarter_id columns.
        cutoff: Time-series split cutoff.
        max_cases: Maximum number of case studies to generate.

    Returns:
        List of saved file paths.
    """
    _ensure_reports_dir()

    # We need Config_A predictions on the same test set.
    # Re-load data and train Config_A model to get predictions.
    merged = load_and_merge_data()
    tech_cols, kw_cols = identify_feature_columns(merged)
    configs = get_feature_configs(tech_cols, kw_cols)

    train_df_full, test_df_full = time_series_split(merged, cutoff=cutoff)

    # Config_A: technical features only
    config_a_cols = configs["Config_A"]
    a_imputer, _ = fit_imputer(train_df_full, config_a_cols)
    X_train_a, y_train_a = prepare_features(train_df_full, config_a_cols, imputer=a_imputer)
    X_test_a, y_test_a = prepare_features(test_df_full, config_a_cols, imputer=a_imputer)
    common_a = [c for c in X_train_a.columns if c in X_test_a.columns]
    X_train_a = X_train_a[common_a]
    X_test_a = X_test_a[common_a]

    # Train a Config_A model (same type as best model)
    model_c = joblib.load(BEST_MODEL_PATH)
    model_type = type(model_c).__name__

    # Build the same model type for Config_A
    ml_models = build_ml_models(y_train_a)
    model_a = None
    for name, m in ml_models.items():
        if type(m).__name__ == model_type:
            model_a = m
            break

    if model_a is None:
        # Fallback: use the first available tree model
        for name, m in ml_models.items():
            if hasattr(m, "feature_importances_"):
                model_a = m
                break

    if model_a is None:
        logger.warning("Could not build Config_A model for case studies. Skipping.")
        return []

    model_a.fit(X_train_a, y_train_a)
    preds_a = model_a.predict(X_test_a)

    # Config_C predictions
    preds_c = model_c.predict(X_test)

    # Align indices
    y_true = y_test.values
    tickers = test_df_full["ticker"].values
    quarters = test_df_full["quarter_id"].values

    # Find cases: Config_C correct AND Config_A wrong
    case_indices = []
    for i in range(len(y_true)):
        if i < len(preds_a) and i < len(preds_c):
            c_correct = preds_c[i] == y_true[i]
            a_wrong = preds_a[i] != y_true[i]
            if c_correct and a_wrong:
                case_indices.append(i)

    if not case_indices:
        logger.info(
            "No (ticker, quarter) pairs found where Config_C is correct "
            "but Config_A is wrong. Skipping case studies."
        )
        return []

    # Take up to max_cases
    selected = case_indices[:max_cases]
    logger.info(
        "Found %d case study candidates; generating %d waterfall plots.",
        len(case_indices), len(selected),
    )

    saved_paths: List[str] = []
    for idx in selected:
        ticker = tickers[idx] if idx < len(tickers) else f"idx{idx}"
        quarter = quarters[idx] if idx < len(quarters) else f"q{idx}"
        safe_quarter = str(quarter).replace("/", "_")

        save_path = os.path.join(
            REPORTS_DIR,
            f"shap_case_study_{ticker}_{safe_quarter}.png",
        )

        fig, ax = plt.subplots(figsize=(12, 8))
        shap.plots.waterfall(shap_values[idx], show=False, max_display=15)
        plt.title(f"SHAP Waterfall — {ticker} {quarter}")
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close("all")

        logger.info(
            "  Case study: %s %s — true=%d, Config_C=%d, Config_A=%d → %s",
            ticker, quarter, y_true[idx], preds_c[idx], preds_a[idx], save_path,
        )
        saved_paths.append(save_path)

    return saved_paths


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def run_shap_analysis(
    cutoff: str = "2025Q1",
) -> None:
    """Execute the full TASK 11 workflow.

    1. Load best model and Config_C data
    2. Tree-based feature importance (Req 11.1)
    3. Permutation importance (Req 11.2)
    4. SHAP values + plots (Req 11.3)
    5. Top keyword analysis (Req 11.4, 11.5)
    6. Group contribution analysis (Req 11.6)
    7. SHAP case studies (Req 11.7)
    """
    logger.info("Starting SHAP Analysis (TASK 11)...")

    # 1. Load data
    model, X_train, y_train, X_test, y_test, tech_cols, kw_cols = load_shap_data(
        cutoff=cutoff
    )
    feature_names = list(X_test.columns)

    # 2. Tree-based importance (Req 11.1)
    logger.info("--- 17.1: Tree-based feature importance ---")
    if hasattr(model, "feature_importances_"):
        tree_imp = plot_tree_importance(model, feature_names)
    else:
        logger.warning(
            "Best model (%s) does not have feature_importances_. "
            "Skipping tree-based importance.",
            type(model).__name__,
        )
        tree_imp = pd.Series(dtype=float)

    # 3. Permutation importance (Req 11.2)
    logger.info("--- 17.2: Permutation importance ---")
    perm_imp = plot_permutation_importance(model, X_test, y_test)

    # 4. SHAP values (Req 11.3)
    logger.info("--- 17.3: SHAP values ---")
    shap_vals = compute_shap_values(model, X_test, X_train=X_train)
    plot_shap_summary(shap_vals)
    plot_shap_bar(shap_vals)

    # 5. Top keyword analysis (Req 11.4, 11.5)
    logger.info("--- 17.4: Top keyword analysis ---")
    top_kw_df = analyze_top_keywords(shap_vals, feature_names)

    # 6. Group contribution (Req 11.6)
    logger.info("--- 17.5: Group contribution analysis ---")
    group_contrib = group_contribution_analysis(shap_vals, feature_names)

    # 7. Case studies (Req 11.7)
    logger.info("--- 17.6: SHAP case studies ---")
    merged = load_and_merge_data()
    _, test_df = time_series_split(merged, cutoff=cutoff)
    case_paths = generate_case_studies(
        shap_vals, X_test, y_test, test_df, cutoff=cutoff
    )

    logger.info("TASK 11 complete.")


if __name__ == "__main__":
    run_shap_analysis()
