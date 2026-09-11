"""Unit tests for the Technical_Model interpreter (Req 7.1, 7.3).

Covers :func:`backtest.interpret.interpret_technical_model` on tiny deterministic
synthetic data with 16 named features (``f0``..``f15``):

- Tree model path (:class:`sklearn.ensemble.RandomForestClassifier`, which always
  exposes ``feature_importances_``). Uses SHAP (``TreeExplainer``) when ``shap`` is
  importable, otherwise transparently falls back to permutation importance for the
  ``mean_abs_shap`` column. Assertions hold for BOTH paths — we only check the
  ranking-table contract (features, columns, ranks) and that the CSV + PNG are
  written, never SHAP-specific internals.
- Fallback path (:class:`sklearn.linear_model.LogisticRegression`, no
  ``feature_importances_``) — always uses the permutation fallback.
- ``y_test=None`` raises :class:`ValueError`.

Output is directed to pytest's ``tmp_path`` so tests never touch the real
``reports/`` directory.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from backtest.interpret import (
    CSV_FILENAME,
    IMPORTANCE_COLUMNS,
    interpret_technical_model,
)

N_FEATURES = 16
FEATURE_NAMES = [f"f{i}" for i in range(N_FEATURES)]


def _make_synthetic_data(n_rows: int = 80, seed: int = 42):
    """Deterministic synthetic dataset with 16 named features and both classes.

    The label depends on a couple of features so a fitted model has non-trivial
    importances, and both classes are guaranteed to be present.
    """
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n_rows, N_FEATURES))
    X_df = pd.DataFrame(X, columns=FEATURE_NAMES)

    # Label driven by a few features so importances are meaningful.
    logits = 1.5 * X[:, 0] - 1.0 * X[:, 3] + 0.5 * X[:, 7]
    y = (logits > np.median(logits)).astype(int)

    # Guarantee BOTH classes present (median split already does, but be safe).
    assert set(np.unique(y)) == {0, 1}
    return X_df, pd.Series(y, name="target")


def test_tree_model_path_ranking_table(tmp_path):
    """RandomForest (tree) path returns full 16-feature ranking + writes files."""
    X_df, y = _make_synthetic_data()
    model = RandomForestClassifier(n_estimators=25, random_state=42)
    model.fit(X_df, y)

    df = interpret_technical_model(
        model,
        X_df,
        FEATURE_NAMES,
        y_test=y,
        output_dir=str(tmp_path),
        n_repeats=3,
        random_state=42,
    )

    # All 16 features present (set equality — order is by rank).
    assert set(df["feature"]) == set(FEATURE_NAMES)
    assert len(df) == N_FEATURES

    # Required columns exist.
    for col in ("feature", "mean_abs_shap", "permutation_importance", "rank"):
        assert col in df.columns
    assert list(df.columns) == IMPORTANCE_COLUMNS

    # rank is exactly 1..16, unique.
    assert sorted(df["rank"].tolist()) == list(range(1, N_FEATURES + 1))
    assert df["rank"].nunique() == N_FEATURES

    # rank 1 has the max mean_abs_shap.
    top = df.loc[df["rank"] == 1, "mean_abs_shap"].iloc[0]
    assert top == pytest.approx(df["mean_abs_shap"].max())

    # CSV and a PNG were written into tmp_path.
    csv_path = tmp_path / CSV_FILENAME
    assert csv_path.exists()
    png_files = list(tmp_path.glob("*.png"))
    assert len(png_files) >= 1


def test_logistic_regression_fallback_path(tmp_path):
    """LogisticRegression (no feature_importances_) uses permutation fallback."""
    X_df, y = _make_synthetic_data()
    model = LogisticRegression(max_iter=1000)
    model.fit(X_df, y)

    df = interpret_technical_model(
        model,
        X_df,
        FEATURE_NAMES,
        y_test=y,
        output_dir=str(tmp_path),
        n_repeats=3,
        random_state=42,
    )

    # All 16 features and required columns present.
    assert set(df["feature"]) == set(FEATURE_NAMES)
    assert len(df) == N_FEATURES
    assert list(df.columns) == IMPORTANCE_COLUMNS

    # mean_abs_shap must be non-null (fallback reuses permutation importance).
    assert df["mean_abs_shap"].notna().all()

    # rank remains a full 1..16 ordering.
    assert sorted(df["rank"].tolist()) == list(range(1, N_FEATURES + 1))


def test_missing_y_test_raises_value_error(tmp_path):
    """y_test is required — passing None raises ValueError."""
    X_df, y = _make_synthetic_data()
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_df, y)

    with pytest.raises(ValueError):
        interpret_technical_model(
            model,
            X_df,
            FEATURE_NAMES,
            y_test=None,
            output_dir=str(tmp_path),
            n_repeats=3,
        )
