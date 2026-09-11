"""
Unit tests for TASK 11: SHAP_Analyzer.

Tests cover the helper functions and core logic without requiring
real trained models or data files on disk.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from pipeline.task11_shap import (
    _extract_keyword_name,
    _feature_color,
    _is_keyword_feature,
    _keyword_direction_map,
    analyze_top_keywords,
    group_contribution_analysis,
    plot_tree_importance,
    plot_permutation_importance,
)


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------


class TestIsKeywordFeature:
    """Tests for _is_keyword_feature."""

    def test_kw_prefix(self):
        assert _is_keyword_feature("kw_lợi nhuận tăng") is True

    def test_kw_norm_prefix(self):
        assert _is_keyword_feature("kw_norm_lợi nhuận tăng") is True

    def test_tfidf_prefix(self):
        assert _is_keyword_feature("tfidf_lợi nhuận tăng") is True

    def test_pos_score(self):
        assert _is_keyword_feature("pos_score") is True

    def test_neg_score(self):
        assert _is_keyword_feature("neg_score") is True

    def test_sentiment_ratio(self):
        assert _is_keyword_feature("sentiment_ratio") is True

    def test_news_count(self):
        assert _is_keyword_feature("news_count") is True

    def test_technical_feature(self):
        assert _is_keyword_feature("rsi_mean_q") is False

    def test_return_q(self):
        assert _is_keyword_feature("return_q") is False


class TestFeatureColor:
    """Tests for _feature_color."""

    def test_technical_is_blue(self):
        assert _feature_color("rsi_mean_q") == "#2070C0"

    def test_keyword_is_orange(self):
        assert _feature_color("kw_norm_lợi nhuận tăng") == "#E07020"

    def test_pos_score_is_orange(self):
        assert _feature_color("pos_score") == "#E07020"


class TestExtractKeywordName:
    """Tests for _extract_keyword_name."""

    def test_kw_prefix(self):
        assert _extract_keyword_name("kw_lợi nhuận tăng") == "lợi nhuận tăng"

    def test_kw_norm_prefix(self):
        assert _extract_keyword_name("kw_norm_lợi nhuận tăng") == "lợi nhuận tăng"

    def test_tfidf_prefix(self):
        assert _extract_keyword_name("tfidf_lợi nhuận tăng") == "lợi nhuận tăng"

    def test_non_keyword_returns_none(self):
        assert _extract_keyword_name("rsi_mean_q") is None

    def test_aggregate_col_returns_none(self):
        assert _extract_keyword_name("pos_score") is None


class TestKeywordDirectionMap:
    """Tests for _keyword_direction_map."""

    def test_returns_dict(self):
        mapping = _keyword_direction_map()
        assert isinstance(mapping, dict)

    def test_positive_keyword_mapped(self):
        mapping = _keyword_direction_map()
        assert mapping.get("lợi nhuận tăng") == "positive"

    def test_negative_keyword_mapped(self):
        mapping = _keyword_direction_map()
        assert mapping.get("thua lỗ") == "negative"

    def test_neutral_keyword_mapped(self):
        mapping = _keyword_direction_map()
        assert mapping.get("đại hội cổ đông") == "neutral"


# ---------------------------------------------------------------------------
# Tree-based importance tests
# ---------------------------------------------------------------------------


class TestPlotTreeImportance:
    """Tests for plot_tree_importance."""

    def test_returns_sorted_series(self, tmp_path):
        model = MagicMock()
        model.feature_importances_ = np.array([0.1, 0.3, 0.2, 0.05, 0.35])
        features = ["rsi_mean_q", "kw_norm_lợi nhuận tăng", "return_q", "pos_score", "volatility_q"]

        save_path = str(tmp_path / "feat_imp.png")
        result = plot_tree_importance(model, features, top_n=5, save_path=save_path)

        assert isinstance(result, pd.Series)
        assert result.iloc[0] >= result.iloc[1]  # sorted descending
        assert os.path.isfile(save_path)

    def test_top_n_limits_output(self, tmp_path):
        model = MagicMock()
        model.feature_importances_ = np.random.rand(50)
        features = [f"feat_{i}" for i in range(50)]

        save_path = str(tmp_path / "feat_imp.png")
        result = plot_tree_importance(model, features, top_n=10, save_path=save_path)

        assert len(result) == 50  # full series returned
        assert os.path.isfile(save_path)


# ---------------------------------------------------------------------------
# Permutation importance tests
# ---------------------------------------------------------------------------


class TestPlotPermutationImportance:
    """Tests for plot_permutation_importance."""

    def test_returns_sorted_series(self, tmp_path):
        # Create a simple model that can be evaluated
        from sklearn.ensemble import RandomForestClassifier

        np.random.seed(42)
        X = pd.DataFrame(np.random.rand(50, 5), columns=["a", "b", "c", "d", "e"])
        y = pd.Series(np.random.randint(0, 2, 50))

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)

        save_path = str(tmp_path / "perm_imp.png")
        result = plot_permutation_importance(
            model, X, y, top_n=5, save_path=save_path, n_repeats=3
        )

        assert isinstance(result, pd.Series)
        assert len(result) == 5
        assert os.path.isfile(save_path)


# ---------------------------------------------------------------------------
# Top keyword analysis tests
# ---------------------------------------------------------------------------


class TestAnalyzeTopKeywords:
    """Tests for analyze_top_keywords."""

    def _make_shap_explanation(self, n_samples=20, feature_names=None):
        """Create a mock shap.Explanation-like object."""
        if feature_names is None:
            feature_names = [
                "rsi_mean_q",
                "kw_norm_lợi nhuận tăng",
                "kw_norm_thua lỗ",
                "kw_norm_đại hội cổ đông",
                "return_q",
            ]
        n_features = len(feature_names)
        values = np.random.randn(n_samples, n_features) * 0.1
        # Make "lợi nhuận tăng" have positive mean SHAP
        values[:, 1] = np.abs(values[:, 1]) + 0.05
        # Make "thua lỗ" have negative mean SHAP
        values[:, 2] = -np.abs(values[:, 2]) - 0.05

        explanation = MagicMock()
        explanation.values = values
        explanation.feature_names = feature_names
        return explanation

    def test_returns_dataframe(self, tmp_path):
        shap_vals = self._make_shap_explanation()
        save_path = str(tmp_path / "top_kw.csv")
        result = analyze_top_keywords(
            shap_vals,
            shap_vals.feature_names,
            top_n=5,
            save_path=save_path,
        )
        assert isinstance(result, pd.DataFrame)
        assert os.path.isfile(save_path)

    def test_only_keyword_features_included(self, tmp_path):
        shap_vals = self._make_shap_explanation()
        save_path = str(tmp_path / "top_kw.csv")
        result = analyze_top_keywords(
            shap_vals,
            shap_vals.feature_names,
            top_n=10,
            save_path=save_path,
        )
        # Should only have keyword features, not rsi_mean_q or return_q
        assert all(
            row["feature_column"].startswith(("kw_", "kw_norm_", "tfidf_"))
            for _, row in result.iterrows()
        )

    def test_direction_labels_present(self, tmp_path):
        shap_vals = self._make_shap_explanation()
        save_path = str(tmp_path / "top_kw.csv")
        result = analyze_top_keywords(
            shap_vals,
            shap_vals.feature_names,
            top_n=10,
            save_path=save_path,
        )
        assert "direction_label" in result.columns
        assert "mean_shap" in result.columns
        assert "aligned" in result.columns


# ---------------------------------------------------------------------------
# Group contribution analysis tests
# ---------------------------------------------------------------------------


class TestGroupContributionAnalysis:
    """Tests for group_contribution_analysis."""

    def test_returns_shares_summing_to_100(self):
        feature_names = [
            "rsi_mean_q",
            "return_q",
            "kw_norm_lợi nhuận tăng",
            "pos_score",
        ]
        values = np.array([
            [0.1, 0.2, 0.05, 0.03],
            [0.15, 0.1, 0.08, 0.02],
        ])
        explanation = MagicMock()
        explanation.values = values
        explanation.feature_names = feature_names

        result = group_contribution_analysis(explanation, feature_names)

        assert "technical_share" in result
        assert "keyword_share" in result
        assert abs(result["technical_share"] + result["keyword_share"] - 100.0) < 0.01

    def test_all_technical_gives_100_percent(self):
        feature_names = ["rsi_mean_q", "return_q"]
        values = np.array([[0.1, 0.2], [0.15, 0.1]])
        explanation = MagicMock()
        explanation.values = values

        result = group_contribution_analysis(explanation, feature_names)
        assert result["technical_share"] == pytest.approx(100.0, abs=0.01)
        assert result["keyword_share"] == pytest.approx(0.0, abs=0.01)

    def test_all_keyword_gives_100_percent(self):
        feature_names = ["kw_norm_test", "pos_score"]
        values = np.array([[0.1, 0.2], [0.15, 0.1]])
        explanation = MagicMock()
        explanation.values = values

        result = group_contribution_analysis(explanation, feature_names)
        assert result["keyword_share"] == pytest.approx(100.0, abs=0.01)
        assert result["technical_share"] == pytest.approx(0.0, abs=0.01)
