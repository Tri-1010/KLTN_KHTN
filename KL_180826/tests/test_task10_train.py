"""
Unit tests for TASK 10: Model_Trainer module.

Tests cover:
- Time-series split ensures no future leakage (Req 10.2)
- Config_A uses only technical features (Req 10.3)
- Config_B uses only keyword features (Req 10.3)
- Config_C uses combined features (Req 10.3)
- Class weight computation (Req 10.5)
"""

import numpy as np
import pandas as pd
import pytest

from pipeline.task10_train import (
    build_ml_models,
    get_feature_configs,
    identify_feature_columns,
    load_and_merge_data,
    prepare_features,
    time_series_split,
    evaluate_model,
    find_best_model,
    NaiveMomentumBaseline,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_merged_df(n_tickers: int = 3, n_quarters: int = 8) -> pd.DataFrame:
    """Build a synthetic merged DataFrame that mimics the real pipeline output."""
    tickers = [f"T{i}" for i in range(n_tickers)]
    quarters = [f"202{y}Q{q}" for y in range(2, 5) for q in range(1, 5)][:n_quarters]

    rows = []
    rng = np.random.RandomState(42)
    for t in tickers:
        for q in quarters:
            row = {
                "ticker": t,
                "quarter_id": q,
                # Technical features
                "return_q": rng.randn(),
                "volatility_q": abs(rng.randn()),
                "rsi_mean_q": rng.uniform(30, 70),
                "macd_hist_mean_q": rng.randn() * 0.1,
                "bb_position_q": rng.uniform(0, 1),
                "sma20_end": rng.uniform(80, 120),
                "ema20_end": rng.uniform(80, 120),
                "return_prev_q": rng.randn() * 0.05,
                # Keyword features
                "kw_lợi nhuận tăng": rng.randint(0, 5),
                "kw_norm_lợi nhuận tăng": rng.uniform(0, 1),
                "tfidf_lợi nhuận tăng": rng.uniform(0, 0.5),
                "kw_nợ xấu": rng.randint(0, 3),
                "kw_norm_nợ xấu": rng.uniform(0, 0.5),
                "tfidf_nợ xấu": rng.uniform(0, 0.3),
                "pos_score": rng.uniform(0, 2),
                "neg_score": rng.uniform(0, 1),
                "sentiment_ratio": rng.uniform(-1, 1),
                "news_count": rng.randint(5, 30),
                "news_count_log": rng.uniform(1, 3),
                "has_min_news": 1,
                # Label
                "label_basic": rng.choice([0, 1]),
            }
            rows.append(row)

    return pd.DataFrame(rows)


@pytest.fixture
def merged_df():
    return _make_merged_df()


@pytest.fixture
def large_merged_df():
    """Larger dataset for model training tests."""
    return _make_merged_df(n_tickers=10, n_quarters=12)


# ---------------------------------------------------------------------------
# 16.2 — Time-series split: no future leakage (Req 10.2)
# ---------------------------------------------------------------------------


class TestTimeSeriesSplit:
    """Verify that the time-series split prevents data leakage."""

    def test_no_future_data_in_train(self, merged_df):
        """All training quarter_ids must be strictly before all test quarter_ids."""
        train_df, test_df = time_series_split(merged_df, cutoff="2023Q1")

        train_max = train_df["quarter_id"].max()
        test_min = test_df["quarter_id"].min()

        assert train_max < test_min, (
            f"Future leakage: train max quarter {train_max} >= "
            f"test min quarter {test_min}"
        )

    def test_no_overlap_between_train_and_test(self, merged_df):
        """Train and test sets must have disjoint quarter_ids."""
        train_df, test_df = time_series_split(merged_df, cutoff="2023Q1")

        train_quarters = set(train_df["quarter_id"].unique())
        test_quarters = set(test_df["quarter_id"].unique())

        assert train_quarters.isdisjoint(test_quarters), (
            f"Overlap found: {train_quarters & test_quarters}"
        )

    def test_all_rows_assigned(self, merged_df):
        """Every row in the original df must appear in either train or test."""
        train_df, test_df = time_series_split(merged_df, cutoff="2023Q1")
        assert len(train_df) + len(test_df) == len(merged_df)

    def test_no_shuffling(self, merged_df):
        """Rows within train and test must remain sorted by quarter_id."""
        train_df, test_df = time_series_split(merged_df, cutoff="2023Q1")

        assert train_df["quarter_id"].is_monotonic_increasing
        assert test_df["quarter_id"].is_monotonic_increasing

    def test_fallback_when_few_test_quarters(self):
        """When cutoff yields < 4 test quarters, fall back to last 20%."""
        # Create data with only 2 quarters after a late cutoff
        df = _make_merged_df(n_tickers=3, n_quarters=8)
        # All quarters are 2022Q1..2024Q4; cutoff at 2024Q4 leaves ≤1 quarter
        train_df, test_df = time_series_split(df, cutoff="2024Q4")

        # Should still have a non-empty test set via fallback
        assert len(test_df) > 0
        # No leakage even with fallback
        assert train_df["quarter_id"].max() < test_df["quarter_id"].min()


# ---------------------------------------------------------------------------
# 16.3 — Feature configurations (Req 10.3)
# ---------------------------------------------------------------------------


class TestFeatureConfigs:
    """Verify Config_A / Config_B / Config_C feature sets."""

    def test_config_a_technical_only(self, merged_df):
        """Config_A must contain only technical features (no kw_/tfidf_ prefixes)."""
        tech_cols, kw_cols = identify_feature_columns(merged_df)
        configs = get_feature_configs(tech_cols, kw_cols)

        for col in configs["Config_A"]:
            assert not col.startswith("kw_"), f"Keyword col in Config_A: {col}"
            assert not col.startswith("tfidf_"), f"TF-IDF col in Config_A: {col}"
            assert col not in {
                "pos_score", "neg_score", "sentiment_ratio",
                "news_count", "news_count_log", "has_min_news",
            }, f"Keyword-derived col in Config_A: {col}"

    def test_config_b_keyword_only(self, merged_df):
        """Config_B must contain only keyword features (no technical indicators)."""
        tech_cols, kw_cols = identify_feature_columns(merged_df)
        configs = get_feature_configs(tech_cols, kw_cols)

        tech_set = set(tech_cols)
        for col in configs["Config_B"]:
            assert col not in tech_set, f"Technical col in Config_B: {col}"

    def test_config_c_is_union(self, merged_df):
        """Config_C must be the union of Config_A and Config_B."""
        tech_cols, kw_cols = identify_feature_columns(merged_df)
        configs = get_feature_configs(tech_cols, kw_cols)

        assert set(configs["Config_C"]) == (
            set(configs["Config_A"]) | set(configs["Config_B"])
        )

    def test_configs_are_non_empty(self, merged_df):
        """All three configs must have at least one feature."""
        tech_cols, kw_cols = identify_feature_columns(merged_df)
        configs = get_feature_configs(tech_cols, kw_cols)

        for name, cols in configs.items():
            assert len(cols) > 0, f"{name} has no features"

    def test_config_a_contains_expected_technical_features(self, merged_df):
        """Config_A should include known technical feature names."""
        tech_cols, kw_cols = identify_feature_columns(merged_df)
        configs = get_feature_configs(tech_cols, kw_cols)

        expected = {"return_q", "rsi_mean_q", "macd_hist_mean_q"}
        assert expected.issubset(set(configs["Config_A"]))


# ---------------------------------------------------------------------------
# 16.5 — Class weight computation (Req 10.5)
# ---------------------------------------------------------------------------


class TestClassWeights:
    """Verify class weight / imbalance handling in ML models."""

    def test_xgboost_scale_pos_weight(self):
        """XGBoost scale_pos_weight should equal neg_count / pos_count."""
        y_train = pd.Series([0, 0, 0, 1, 1])  # 3 neg, 2 pos
        models = build_ml_models(y_train)

        xgb_model = models["XGBoost"]
        expected_spw = 3 / 2  # 1.5
        assert abs(xgb_model.scale_pos_weight - expected_spw) < 1e-6

    def test_logistic_regression_balanced(self):
        """Logistic Regression should use class_weight='balanced'."""
        y_train = pd.Series([0, 1])
        models = build_ml_models(y_train)
        lr = models["Logistic_Regression"]
        assert lr.class_weight == "balanced"

    def test_random_forest_balanced(self):
        """Random Forest should use class_weight='balanced'."""
        y_train = pd.Series([0, 1])
        models = build_ml_models(y_train)
        rf = models["Random_Forest"]
        assert rf.class_weight == "balanced"

    def test_lightgbm_is_unbalance(self):
        """LightGBM should have is_unbalance=True."""
        y_train = pd.Series([0, 1])
        models = build_ml_models(y_train)
        lgbm = models["LightGBM"]
        assert lgbm.is_unbalance is True


# ---------------------------------------------------------------------------
# Additional unit tests
# ---------------------------------------------------------------------------


class TestPrepareFeatures:
    """Test median imputation and feature preparation."""

    def test_median_imputation_fills_nan(self):
        """NaN values should be replaced with column medians."""
        df = pd.DataFrame({
            "ticker": ["A", "B", "C"],
            "quarter_id": ["2022Q1", "2022Q1", "2022Q1"],
            "feat1": [1.0, np.nan, 3.0],
            "feat2": [10.0, 20.0, np.nan],
            "label_basic": [1, 0, 1],
        })
        X, y = prepare_features(df, ["feat1", "feat2"])
        assert not X.isna().any().any(), "NaN values remain after imputation"

    def test_non_numeric_columns_dropped(self):
        """Non-numeric columns (e.g. combined_text) should be dropped."""
        df = pd.DataFrame({
            "ticker": ["A"],
            "quarter_id": ["2022Q1"],
            "feat1": [1.0],
            "combined_text": ["some text"],
            "label_basic": [1],
        })
        X, y = prepare_features(df, ["feat1", "combined_text"])
        assert "combined_text" not in X.columns


class TestEvaluation:
    """Test evaluation metric computation."""

    def test_evaluate_returns_all_metrics(self, merged_df):
        """evaluate_model should return all required metric keys."""
        from sklearn.dummy import DummyClassifier

        train_df, test_df = time_series_split(merged_df, cutoff="2023Q1")
        X_train, y_train = prepare_features(
            train_df, ["return_q", "volatility_q"]
        )
        X_test, y_test = prepare_features(
            test_df, ["return_q", "volatility_q"]
        )

        model = DummyClassifier(strategy="most_frequent")
        model.fit(X_train, y_train)

        result = evaluate_model(model, X_test, y_test, "Dummy", "Config_A")

        expected_keys = {
            "model", "config", "accuracy", "precision", "recall",
            "f1_macro", "auc_roc", "balanced_accuracy",
        }
        assert expected_keys == set(result.keys())

    def test_find_best_model(self):
        """find_best_model should return the row with highest balanced_accuracy."""
        results_df = pd.DataFrame([
            {"model": "A", "config": "Config_A", "balanced_accuracy": 0.5},
            {"model": "B", "config": "Config_C", "balanced_accuracy": 0.7},
            {"model": "C", "config": "Config_B", "balanced_accuracy": 0.6},
        ])
        name, config, ba = find_best_model(results_df)
        assert name == "B"
        assert config == "Config_C"
        assert ba == 0.7


class TestNaiveMomentumBaseline:
    """Test the naive momentum baseline model."""

    def test_predicts_majority_class(self):
        """Should predict the majority class from training data."""
        X_train = pd.DataFrame({"f": [1, 2, 3, 4, 5]})
        y_train = pd.Series([0, 0, 0, 1, 1])

        model = NaiveMomentumBaseline()
        model.fit(X_train, y_train)

        X_test = pd.DataFrame({"f": [10, 20]})
        preds = model.predict(X_test)

        assert all(p == 0 for p in preds)  # majority is 0

    def test_predict_proba_shape(self):
        """predict_proba should return (n_samples, 2) array."""
        model = NaiveMomentumBaseline()
        model.fit(pd.DataFrame({"f": [1]}), pd.Series([1]))

        proba = model.predict_proba(pd.DataFrame({"f": [1, 2, 3]}))
        assert proba.shape == (3, 2)
