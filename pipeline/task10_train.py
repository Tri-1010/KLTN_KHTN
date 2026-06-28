"""
TASK 10: Model_Trainer
Train and evaluate ML classifiers under three feature configurations.

Merges technical_features.csv, keyword_features.csv, and master_with_labels.csv
on (ticker, quarter_id), applies median imputation, trains 4 ML algorithms +
2 baselines across Config_A / Config_B / Config_C, evaluates with multiple
metrics, and saves the best model to models/best_model.pkl.

Requirements: 10.1 – 10.9
"""

from __future__ import annotations

import json
import os
import warnings
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.impute import SimpleImputer

from pipeline.logging_config import setup_logger

logger = setup_logger("TASK_10")

# Suppress convergence / user warnings during training
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

TECH_FEATURES_PATH = "data/features/technical_features.csv"
KW_FEATURES_PATH = "data/features/keyword_features.csv"
LABELS_PATH = "data/aggregated/master_with_labels.csv"
MODEL_COMPARISON_PATH = "reports/model_comparison.csv"
BEST_MODEL_PATH = "models/best_model.pkl"

# ---------------------------------------------------------------------------
# 16.1 — Data preparation  (Req 10.1)
# ---------------------------------------------------------------------------


def load_and_merge_data(
    tech_path: str = TECH_FEATURES_PATH,
    kw_path: str = KW_FEATURES_PATH,
    labels_path: str = LABELS_PATH,
) -> pd.DataFrame:
    """Load and merge the three feature/label CSVs on (ticker, quarter_id).

    Returns a single DataFrame with all features and the ``label_basic``
    target column.  Rows with NaN labels are dropped.
    """
    tech = pd.read_csv(tech_path)
    kw = pd.read_csv(kw_path)
    labels = pd.read_csv(labels_path)

    # Keep only the columns we need from labels
    label_cols = ["ticker", "quarter_id", "label_basic"]
    labels_subset = labels[label_cols].copy()

    # Merge technical + labels
    merged = tech.merge(labels_subset, on=["ticker", "quarter_id"], how="inner")

    # Merge keyword features
    merged = merged.merge(kw, on=["ticker", "quarter_id"], how="inner")

    # Drop rows where label is NaN
    merged = merged.dropna(subset=["label_basic"])

    logger.info(
        "Merged dataset: %d rows, %d columns", len(merged), len(merged.columns)
    )
    return merged


def identify_feature_columns(
    df: pd.DataFrame,
) -> Tuple[List[str], List[str]]:
    """Identify technical and keyword feature column names.

    Technical features are those that are NOT prefixed with ``kw_``,
    ``kw_norm_``, ``tfidf_``, and are not metadata/label columns.

    Returns:
        (tech_feature_cols, kw_feature_cols)
    """
    meta_cols = {"ticker", "quarter_id", "label_basic"}
    kw_prefixes = ("kw_", "kw_norm_", "tfidf_")
    kw_exact = {
        "pos_score",
        "neg_score",
        "sentiment_ratio",
        "news_count",
        "news_count_log",
        "has_min_news",
        "combined_text",
    }

    tech_cols: List[str] = []
    kw_cols: List[str] = []

    for col in df.columns:
        if col in meta_cols:
            continue
        if col in kw_exact or any(col.startswith(p) for p in kw_prefixes):
            kw_cols.append(col)
        else:
            tech_cols.append(col)

    return tech_cols, kw_cols


def prepare_features(
    df: pd.DataFrame,
    feature_cols: List[str],
    imputer: Optional[SimpleImputer] = None,
) -> Tuple[pd.DataFrame, pd.Series]:
    """Extract feature matrix and target, apply median imputation.

    Args:
        df: Merged DataFrame with features and label_basic.
        feature_cols: Columns to use as features.
        imputer: Optional pre-fitted SimpleImputer. If provided, it is used
            to ``transform`` the features (no refit) — this is how the test
            set is imputed using statistics learned from the training set,
            preventing test-set leakage. If ``None``, a new median imputer is
            fitted on *df* (used for the training set).

    Returns:
        (X, y) where X has been median-imputed and y is the binary target.
    """
    X = df[feature_cols].copy()

    # Drop any non-numeric columns (e.g. combined_text)
    non_numeric = X.select_dtypes(exclude=[np.number]).columns.tolist()
    if non_numeric:
        X = X.drop(columns=non_numeric)

    y = df["label_basic"].astype(int)

    # Median imputation: fit on training data only, transform elsewhere.
    if imputer is None:
        imputer = SimpleImputer(strategy="median")
        imputed = imputer.fit_transform(X)
    else:
        imputed = imputer.transform(X)

    X_imputed = pd.DataFrame(imputed, columns=X.columns, index=X.index)

    return X_imputed, y


def fit_imputer(
    df: pd.DataFrame,
    feature_cols: List[str],
) -> Tuple[SimpleImputer, List[str]]:
    """Fit a median imputer on the given (training) features.

    Returns the fitted imputer along with the numeric column order it was
    fitted on, so the same columns can be passed to :func:`prepare_features`
    for the test set.
    """
    X = df[feature_cols].copy()
    non_numeric = X.select_dtypes(exclude=[np.number]).columns.tolist()
    if non_numeric:
        X = X.drop(columns=non_numeric)
    imputer = SimpleImputer(strategy="median")
    imputer.fit(X)
    return imputer, list(X.columns)


# ---------------------------------------------------------------------------
# 16.2 — Time-series split  (Req 10.2)
# ---------------------------------------------------------------------------


def time_series_split(
    df: pd.DataFrame,
    cutoff: str = "2025Q1",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split data by quarter_id into train / test sets.

    Train: all rows with quarter_id < *cutoff*.
    Test:  all rows with quarter_id >= *cutoff*.

    If the test set has fewer than 4 unique quarters, fall back to the last
    20 % of sorted quarters.

    No random shuffling — order is preserved.

    Args:
        df: DataFrame with a ``quarter_id`` column.
        cutoff: Quarter string like ``"2025Q1"``.

    Returns:
        (train_df, test_df)
    """
    df = df.sort_values("quarter_id").reset_index(drop=True)

    train_mask = df["quarter_id"] < cutoff
    test_mask = df["quarter_id"] >= cutoff

    test_quarters = df.loc[test_mask, "quarter_id"].nunique()

    if test_quarters < 4:
        # Fallback: last 20 % of unique quarters
        unique_quarters = sorted(df["quarter_id"].unique())
        n_test = max(1, int(len(unique_quarters) * 0.2))
        test_quarter_set = set(unique_quarters[-n_test:])
        train_mask = ~df["quarter_id"].isin(test_quarter_set)
        test_mask = df["quarter_id"].isin(test_quarter_set)
        logger.warning(
            "Fewer than 4 test quarters with cutoff %s; "
            "falling back to last 20%% of quarters (%d test quarters).",
            cutoff,
            n_test,
        )

    train_df = df.loc[train_mask].copy()
    test_df = df.loc[test_mask].copy()

    logger.info(
        "Time-series split — train: %d rows (%d quarters), test: %d rows (%d quarters)",
        len(train_df),
        train_df["quarter_id"].nunique(),
        len(test_df),
        test_df["quarter_id"].nunique(),
    )
    return train_df, test_df


# ---------------------------------------------------------------------------
# 16.3 — Feature configurations  (Req 10.3)
# ---------------------------------------------------------------------------


def get_feature_configs(
    tech_cols: List[str],
    kw_cols: List[str],
) -> Dict[str, List[str]]:
    """Return the three feature configurations.

    - Config_A: technical features only
    - Config_B: keyword features only
    - Config_C: combined (technical + keyword)
    """
    return {
        "Config_A": list(tech_cols),
        "Config_B": list(kw_cols),
        "Config_C": list(tech_cols) + list(kw_cols),
    }


# ---------------------------------------------------------------------------
# 16.4 — Baseline models  (Req 10.4)
# ---------------------------------------------------------------------------


class NaiveMomentumBaseline:
    """Predict next-quarter label = current-quarter label (momentum).

    Each sample is a (ticker, quarter) row whose label answers "did the price
    rise next quarter". The naive momentum heuristic predicts the trend
    persists: a row's prediction is the *previous* quarter's label for the
    same ticker. When no previous-quarter label is available (first quarter of
    a ticker, or no context supplied), it falls back to the training majority
    class.

    Context is supplied via :meth:`set_context` with the merged frame (indexed
    identically to the X passed to fit/predict). Without context the model
    degrades gracefully to a majority-class predictor.
    """

    def __init__(self) -> None:
        self.majority_label: int = 0
        # (ticker, quarter_id) -> label_basic
        self._label_lookup: Dict[Tuple[str, str], int] = {}
        # row index -> (ticker, quarter_id)
        self._index_meta: Dict[Any, Tuple[str, str]] = {}

    def set_context(self, merged: pd.DataFrame) -> "NaiveMomentumBaseline":
        """Provide the merged frame so momentum lookups can be performed."""
        self._label_lookup = {}
        self._index_meta = {}
        for idx, row in merged.iterrows():
            ticker = row.get("ticker")
            quarter = row.get("quarter_id")
            label = row.get("label_basic")
            if pd.notna(label):
                self._label_lookup[(ticker, quarter)] = int(label)
            self._index_meta[idx] = (ticker, quarter)
        return self

    @staticmethod
    def _prev_quarter(quarter_id: str) -> Optional[str]:
        """Return the quarter_id immediately preceding *quarter_id*."""
        try:
            year = int(quarter_id[:4])
            q = int(quarter_id[-1])
        except (ValueError, IndexError, TypeError):
            return None
        if q == 1:
            return f"{year - 1}Q4"
        return f"{year}Q{q - 1}"

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "NaiveMomentumBaseline":
        self.majority_label = int(y.mode().iloc[0])
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        # If no context was supplied, fall back to majority class.
        if not self._index_meta:
            return np.full(len(X), self.majority_label)

        preds = []
        for idx in X.index:
            meta = self._index_meta.get(idx)
            pred = self.majority_label
            if meta is not None:
                ticker, quarter = meta
                prev_q = self._prev_quarter(quarter)
                if prev_q is not None:
                    prev_label = self._label_lookup.get((ticker, prev_q))
                    if prev_label is not None:
                        pred = prev_label
            preds.append(pred)
        return np.array(preds)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        preds = self.predict(X)
        proba = np.zeros((len(X), 2))
        for i, p in enumerate(preds):
            proba[i, int(p)] = 1.0
        return proba


def build_baselines() -> Dict[str, Any]:
    """Return baseline model instances."""
    return {
        "Majority_Class": DummyClassifier(strategy="most_frequent"),
        "Naive_Momentum": NaiveMomentumBaseline(),
    }


# ---------------------------------------------------------------------------
# 16.5 — ML algorithms  (Req 10.5)
# ---------------------------------------------------------------------------


def build_ml_models(
    y_train: pd.Series,
) -> Dict[str, Any]:
    """Return ML model instances with specified hyperparameters.

    XGBoost ``scale_pos_weight`` is computed from the training labels.
    """
    # Lazy imports so the module loads even if xgboost/lightgbm are missing
    from xgboost import XGBClassifier
    from lightgbm import LGBMClassifier

    neg_count = int((y_train == 0).sum())
    pos_count = int((y_train == 1).sum())
    scale_pos = neg_count / max(pos_count, 1)

    return {
        "Logistic_Regression": LogisticRegression(
            C=1.0,
            class_weight="balanced",
            max_iter=1000,
            solver="lbfgs",
            random_state=42,
        ),
        "Random_Forest": RandomForestClassifier(
            n_estimators=100,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
        "XGBoost": XGBClassifier(
            scale_pos_weight=scale_pos,
            eval_metric="logloss",
            random_state=42,
            verbosity=0,
        ),
        "LightGBM": LGBMClassifier(
            is_unbalance=True,
            random_state=42,
            verbose=-1,
        ),
    }


# ---------------------------------------------------------------------------
# 16.6 — Evaluation  (Req 10.6, 10.7)
# ---------------------------------------------------------------------------


def evaluate_model(
    model: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    model_name: str,
    config_name: str,
) -> Dict[str, Any]:
    """Compute all evaluation metrics for a trained model.

    Returns a dict with keys: model, config, accuracy, precision, recall,
    f1_macro, auc_roc, balanced_accuracy.
    """
    y_pred = model.predict(X_test)

    # AUC-ROC needs probability estimates
    try:
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_test)[:, 1]
        else:
            y_proba = y_pred.astype(float)
        auc = roc_auc_score(y_test, y_proba)
    except (ValueError, IndexError):
        auc = np.nan

    cm = confusion_matrix(y_test, y_pred)
    logger.info(
        "Confusion matrix for %s - %s:\n%s", model_name, config_name, cm
    )

    return {
        "model": model_name,
        "config": config_name,
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1_macro": f1_score(y_test, y_pred, average="macro", zero_division=0),
        "auc_roc": auc,
        "balanced_accuracy": balanced_accuracy_score(y_test, y_pred),
    }


def save_results(
    results: List[Dict[str, Any]],
    path: str = MODEL_COMPARISON_PATH,
) -> pd.DataFrame:
    """Save consolidated comparison table to CSV."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv(path, index=False)
    logger.info("Saved model comparison to %s (%d rows)", path, len(df))
    return df


# ---------------------------------------------------------------------------
# 16.7 — Best model & Config comparison  (Req 10.8, 10.9)
# ---------------------------------------------------------------------------


def find_best_model(
    results_df: pd.DataFrame,
) -> Tuple[str, str, float]:
    """Identify the best model by Balanced Accuracy.

    Returns:
        (model_name, config_name, balanced_accuracy)
    """
    best_idx = results_df["balanced_accuracy"].idxmax()
    best_row = results_df.loc[best_idx]
    return (
        best_row["model"],
        best_row["config"],
        best_row["balanced_accuracy"],
    )


def report_config_comparison(results_df: pd.DataFrame) -> None:
    """Log performance delta between Config_A and Config_C per algorithm."""
    models = results_df["model"].unique()
    for model_name in models:
        subset = results_df[results_df["model"] == model_name]
        a_row = subset[subset["config"] == "Config_A"]
        c_row = subset[subset["config"] == "Config_C"]
        if a_row.empty or c_row.empty:
            continue
        ba_a = a_row["balanced_accuracy"].values[0]
        ba_c = c_row["balanced_accuracy"].values[0]
        delta = ba_c - ba_a
        direction = "improves" if delta > 0 else "does not improve"
        logger.info(
            "%s: Config_C %s over Config_A by %.4f "
            "(BA: %.4f → %.4f)",
            model_name,
            direction,
            abs(delta),
            ba_a,
            ba_c,
        )
        if delta <= 0:
            logger.info(
                "Note: Config_C does not improve over Config_A for %s. "
                "This is still a valid research finding.",
                model_name,
            )


def save_best_model(
    model: Any,
    path: str = BEST_MODEL_PATH,
    config_name: Optional[str] = None,
    feature_cols: Optional[List[str]] = None,
    model_name: Optional[str] = None,
) -> None:
    """Serialize the best model to disk using joblib.

    Also writes a companion metadata JSON (``<path>.meta.json``) recording the
    feature configuration, the exact feature columns the model was trained on,
    and the model/algorithm name. Downstream analysis (TASK 11) relies on this
    metadata to align its feature matrix with the saved model, avoiding
    column-count mismatches when the best model is not Config_C.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    logger.info("Saved best model to %s", path)

    meta = {
        "config_name": config_name,
        "feature_cols": list(feature_cols) if feature_cols is not None else None,
        "model_name": model_name,
    }
    meta_path = path + ".meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    logger.info("Saved best model metadata to %s", meta_path)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def run_model_training(
    tech_path: str = TECH_FEATURES_PATH,
    kw_path: str = KW_FEATURES_PATH,
    labels_path: str = LABELS_PATH,
    cutoff: str = "2025Q1",
) -> pd.DataFrame:
    """Execute the full TASK 10 workflow.

    1. Load & merge data
    2. Identify feature columns
    3. Time-series split
    4. For each config (A/B/C):
       a. Prepare features (impute)
       b. Train baselines + ML models
       c. Evaluate
    5. Save comparison table
    6. Highlight best model, save to disk

    Returns:
        DataFrame with model comparison results.
    """
    # 1. Load & merge
    merged = load_and_merge_data(tech_path, kw_path, labels_path)

    # Guard: model training requires a non-empty merged dataset with both
    # classes present. When upstream news scraping produced no usable data
    # (so the keyword/label merge is empty), fail fast with a clear,
    # actionable message instead of an opaque sklearn error.
    if merged.empty:
        msg = (
            "No training samples after merging technical/keyword/label data. "
            "This usually means upstream tasks produced empty outputs "
            "(e.g. news scraping in TASK 2 collected no articles, so labels "
            "or keyword features are empty). Cannot train a model without "
            "data — fix the upstream data collection and rerun."
        )
        logger.error(msg)
        raise ValueError(msg)

    if merged["label_basic"].nunique() < 2:
        msg = (
            "Training data has only one label class "
            f"({merged['label_basic'].unique().tolist()}). At least two "
            "classes are required to train a classifier. This usually "
            "indicates insufficient upstream data."
        )
        logger.error(msg)
        raise ValueError(msg)

    # 2. Identify columns
    tech_cols, kw_cols = identify_feature_columns(merged)
    logger.info(
        "Feature columns — technical: %d, keyword: %d",
        len(tech_cols),
        len(kw_cols),
    )

    configs = get_feature_configs(tech_cols, kw_cols)

    # 3. Time-series split (on the merged df, before feature selection)
    train_df, test_df = time_series_split(merged, cutoff=cutoff)

    all_results: List[Dict[str, Any]] = []
    trained_models: Dict[str, Any] = {}  # key = "model - config"
    # Record the exact feature columns each config was trained on, so the
    # best model can be saved with metadata that downstream tasks can use.
    config_feature_cols: Dict[str, List[str]] = {}

    for config_name, feature_cols in configs.items():
        logger.info("=== %s (%d features) ===", config_name, len(feature_cols))

        # Filter to numeric feature cols that actually exist
        available_cols = [c for c in feature_cols if c in train_df.columns]

        # 4a. Prepare features — fit imputer on train, reuse for test
        # to prevent test-set leakage.
        train_imputer, _ = fit_imputer(train_df, available_cols)
        X_train, y_train = prepare_features(train_df, available_cols, imputer=train_imputer)
        X_test, y_test = prepare_features(test_df, available_cols, imputer=train_imputer)

        # Ensure columns match after dropping non-numeric
        common_cols = [c for c in X_train.columns if c in X_test.columns]
        X_train = X_train[common_cols]
        X_test = X_test[common_cols]
        config_feature_cols[config_name] = list(common_cols)

        logger.info(
            "  Train: %d samples, Test: %d samples, Features: %d",
            len(X_train),
            len(X_test),
            len(common_cols),
        )

        # 4b. Baselines
        baselines = build_baselines()
        for bname, bmodel in baselines.items():
            # Provide (ticker, quarter) context so the momentum baseline can
            # look up the previous quarter's label per ticker.
            if isinstance(bmodel, NaiveMomentumBaseline):
                bmodel.set_context(merged)
            bmodel.fit(X_train, y_train)
            result = evaluate_model(bmodel, X_test, y_test, bname, config_name)
            all_results.append(result)
            trained_models[f"{bname} - {config_name}"] = bmodel

        # 4c. ML models
        ml_models = build_ml_models(y_train)
        for mname, mmodel in ml_models.items():
            logger.info("  Training %s …", mname)
            mmodel.fit(X_train, y_train)
            result = evaluate_model(mmodel, X_test, y_test, mname, config_name)
            all_results.append(result)
            trained_models[f"{mname} - {config_name}"] = mmodel

    # 5. Save comparison table
    results_df = save_results(all_results)

    # 6. Best model
    best_model_name, best_config, best_ba = find_best_model(results_df)
    logger.info(
        "Best model: %s (%s) — Balanced Accuracy = %.4f",
        best_model_name,
        best_config,
        best_ba,
    )

    report_config_comparison(results_df)

    best_key = f"{best_model_name} - {best_config}"
    save_best_model(
        trained_models[best_key],
        config_name=best_config,
        feature_cols=config_feature_cols.get(best_config),
        model_name=best_model_name,
    )

    return results_df
