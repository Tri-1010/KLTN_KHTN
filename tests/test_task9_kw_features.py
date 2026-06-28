"""
Unit tests for TASK 9: Keyword_Feature_Extractor module.

Tests cover:
- Raw count extraction (Req 9.1)
- Normalized count calculation (Req 9.1)
- Sentiment score aggregation (Req 9.2)
- TF-IDF computation (Req 9.3)
- Coverage features (Req 9.4)
- Sparsity rate calculation (Req 9.8)
"""

import math
import os
import tempfile

import numpy as np
import pandas as pd
import pytest

from pipeline.task9_kw_features import (
    add_coverage_features,
    compute_keyword_counts,
    compute_raw_counts,
    compute_sentiment_scores,
    compute_sparsity_rate,
    compute_tfidf_features,
    extract_keyword_features,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_keywords_by_direction():
    """Small keyword set for testing."""
    return {
        "positive": ["lợi nhuận tăng", "doanh thu tăng"],
        "negative": ["nợ xấu", "thua lỗ"],
        "neutral": ["đại hội cổ đông"],
    }


@pytest.fixture
def all_keywords(sample_keywords_by_direction):
    """Flat list of all test keywords."""
    kw = sample_keywords_by_direction
    return kw["positive"] + kw["negative"] + kw["neutral"]


@pytest.fixture
def sample_df():
    """Sample news_by_quarter DataFrame for testing."""
    return pd.DataFrame({
        "ticker": ["VNM", "VNM", "VCB", "VCB"],
        "quarter_id": ["2022Q1", "2022Q2", "2022Q1", "2022Q2"],
        "news_count": [10, 5, 8, 3],
        "combined_text": [
            "lợi nhuận tăng mạnh doanh thu tăng lợi nhuận tăng kỷ lục",
            "nợ xấu tăng thua lỗ nặng nợ xấu cao",
            "đại hội cổ đông thường niên lợi nhuận tăng",
            "doanh thu tăng mạnh đại hội cổ đông",
        ],
    })


# ---------------------------------------------------------------------------
# Raw count tests (Req 9.1)
# ---------------------------------------------------------------------------


class TestRawCounts:
    """Test raw keyword count extraction."""

    def test_single_occurrence(self, all_keywords):
        """Should count a keyword that appears once."""
        text = "lợi nhuận tăng mạnh trong quý"
        counts = compute_raw_counts(text, all_keywords)
        assert counts["lợi nhuận tăng"] == 1

    def test_multiple_occurrences(self, all_keywords):
        """Should count a keyword that appears multiple times."""
        text = "nợ xấu tăng cao nợ xấu vẫn lớn nợ xấu"
        counts = compute_raw_counts(text, all_keywords)
        assert counts["nợ xấu"] == 3

    def test_zero_count_for_absent_keyword(self, all_keywords):
        """Keywords not in text should have count 0."""
        text = "thị trường chứng khoán biến động"
        counts = compute_raw_counts(text, all_keywords)
        assert counts["lợi nhuận tăng"] == 0
        assert counts["nợ xấu"] == 0

    def test_empty_text(self, all_keywords):
        """Empty text should yield all zeros."""
        counts = compute_raw_counts("", all_keywords)
        assert all(v == 0 for v in counts.values())

    def test_none_text(self, all_keywords):
        """None text should yield all zeros."""
        counts = compute_raw_counts(None, all_keywords)
        assert all(v == 0 for v in counts.values())

    def test_case_insensitive(self, all_keywords):
        """Counting should be case-insensitive."""
        text = "Lợi Nhuận Tăng mạnh"
        counts = compute_raw_counts(text, all_keywords)
        assert counts["lợi nhuận tăng"] == 1


# ---------------------------------------------------------------------------
# Normalized count tests (Req 9.1)
# ---------------------------------------------------------------------------


class TestNormalizedCounts:
    """Test normalized keyword count calculation."""

    def test_normalized_equals_raw_div_news_count(self, sample_df, all_keywords):
        """kw_norm_{k} should equal kw_{k} / news_count."""
        result = compute_keyword_counts(sample_df, all_keywords)

        for kw in all_keywords:
            raw_col = f"kw_{kw}"
            norm_col = f"kw_norm_{kw}"
            for idx in result.index:
                raw = result.loc[idx, raw_col]
                nc = result.loc[idx, "news_count"]
                expected = raw / nc if nc > 0 else np.nan
                actual = result.loc[idx, norm_col]
                if np.isnan(expected):
                    assert np.isnan(actual)
                else:
                    assert abs(actual - expected) < 1e-9

    def test_zero_news_count_gives_nan(self, all_keywords):
        """When news_count is 0, normalized count should be NaN."""
        df = pd.DataFrame({
            "ticker": ["VNM"],
            "quarter_id": ["2022Q1"],
            "news_count": [0],
            "combined_text": [""],
        })
        result = compute_keyword_counts(df, all_keywords)
        for kw in all_keywords:
            assert np.isnan(result[f"kw_norm_{kw}"].iloc[0])

    def test_raw_columns_present(self, sample_df, all_keywords):
        """All kw_{k} columns should be present."""
        result = compute_keyword_counts(sample_df, all_keywords)
        for kw in all_keywords:
            assert f"kw_{kw}" in result.columns

    def test_norm_columns_present(self, sample_df, all_keywords):
        """All kw_norm_{k} columns should be present."""
        result = compute_keyword_counts(sample_df, all_keywords)
        for kw in all_keywords:
            assert f"kw_norm_{kw}" in result.columns


# ---------------------------------------------------------------------------
# Sentiment score tests (Req 9.2)
# ---------------------------------------------------------------------------


class TestSentimentScores:
    """Test aggregate sentiment score computation."""

    def test_pos_score_is_sum_of_positive_norms(
        self, sample_df, all_keywords, sample_keywords_by_direction
    ):
        """pos_score should be sum of kw_norm for positive keywords."""
        df = compute_keyword_counts(sample_df, all_keywords)
        result = compute_sentiment_scores(df, sample_keywords_by_direction)

        pos_kws = sample_keywords_by_direction["positive"]
        for idx in result.index:
            expected = sum(
                result.loc[idx, f"kw_norm_{kw}"]
                for kw in pos_kws
                if not np.isnan(result.loc[idx, f"kw_norm_{kw}"])
            )
            assert abs(result.loc[idx, "pos_score"] - expected) < 1e-9

    def test_neg_score_is_sum_of_negative_norms(
        self, sample_df, all_keywords, sample_keywords_by_direction
    ):
        """neg_score should be sum of kw_norm for negative keywords."""
        df = compute_keyword_counts(sample_df, all_keywords)
        result = compute_sentiment_scores(df, sample_keywords_by_direction)

        neg_kws = sample_keywords_by_direction["negative"]
        for idx in result.index:
            expected = sum(
                result.loc[idx, f"kw_norm_{kw}"]
                for kw in neg_kws
                if not np.isnan(result.loc[idx, f"kw_norm_{kw}"])
            )
            assert abs(result.loc[idx, "neg_score"] - expected) < 1e-9

    def test_sentiment_ratio_formula(
        self, sample_df, all_keywords, sample_keywords_by_direction
    ):
        """sentiment_ratio = (pos - neg) / (pos + neg + 1e-6)."""
        df = compute_keyword_counts(sample_df, all_keywords)
        result = compute_sentiment_scores(df, sample_keywords_by_direction)

        for idx in result.index:
            pos = result.loc[idx, "pos_score"]
            neg = result.loc[idx, "neg_score"]
            expected = (pos - neg) / (pos + neg + 1e-6)
            assert abs(result.loc[idx, "sentiment_ratio"] - expected) < 1e-9

    def test_sentiment_ratio_positive_when_pos_dominates(self):
        """sentiment_ratio should be positive when pos_score > neg_score."""
        df = pd.DataFrame({
            "ticker": ["VNM"],
            "quarter_id": ["2022Q1"],
            "news_count": [10],
            "combined_text": ["lợi nhuận tăng doanh thu tăng"],
        })
        kw_dir = {
            "positive": ["lợi nhuận tăng", "doanh thu tăng"],
            "negative": ["nợ xấu"],
            "neutral": [],
        }
        all_kw = kw_dir["positive"] + kw_dir["negative"]
        df = compute_keyword_counts(df, all_kw)
        result = compute_sentiment_scores(df, kw_dir)
        assert result["sentiment_ratio"].iloc[0] > 0

    def test_sentiment_ratio_negative_when_neg_dominates(self):
        """sentiment_ratio should be negative when neg_score > pos_score."""
        df = pd.DataFrame({
            "ticker": ["VNM"],
            "quarter_id": ["2022Q1"],
            "news_count": [10],
            "combined_text": ["nợ xấu tăng nợ xấu cao thua lỗ"],
        })
        kw_dir = {
            "positive": ["lợi nhuận tăng"],
            "negative": ["nợ xấu", "thua lỗ"],
            "neutral": [],
        }
        all_kw = kw_dir["positive"] + kw_dir["negative"]
        df = compute_keyword_counts(df, all_kw)
        result = compute_sentiment_scores(df, kw_dir)
        assert result["sentiment_ratio"].iloc[0] < 0


# ---------------------------------------------------------------------------
# TF-IDF tests (Req 9.3)
# ---------------------------------------------------------------------------


class TestTfidfFeatures:
    """Test TF-IDF feature computation."""

    def test_tfidf_columns_present(self, sample_df, all_keywords):
        """All tfidf_{k} columns should be present."""
        df = compute_keyword_counts(sample_df, all_keywords)
        result = compute_tfidf_features(df, all_keywords)
        for kw in all_keywords:
            assert f"tfidf_{kw}" in result.columns

    def test_tfidf_non_negative(self, sample_df, all_keywords):
        """TF-IDF values should be non-negative."""
        df = compute_keyword_counts(sample_df, all_keywords)
        result = compute_tfidf_features(df, all_keywords)
        for kw in all_keywords:
            col = f"tfidf_{kw}"
            assert (result[col] >= 0).all(), f"Negative TF-IDF for {kw}"

    def test_tfidf_zero_for_absent_keyword(self, all_keywords):
        """Keywords absent from all documents should have tfidf = 0."""
        df = pd.DataFrame({
            "ticker": ["VNM", "VCB"],
            "quarter_id": ["2022Q1", "2022Q1"],
            "news_count": [5, 5],
            "combined_text": [
                "thị trường biến động mạnh",
                "giá cổ phiếu tăng nhẹ",
            ],
        })
        df = compute_keyword_counts(df, all_keywords)
        result = compute_tfidf_features(df, all_keywords)
        for kw in all_keywords:
            assert (result[f"tfidf_{kw}"] == 0).all()

    def test_tfidf_min_df_filter(self):
        """Keywords appearing in only 1 document should get tfidf = 0 (min_df=2)."""
        keywords = ["lợi nhuận tăng"]
        df = pd.DataFrame({
            "ticker": ["VNM", "VCB", "FPT"],
            "quarter_id": ["2022Q1", "2022Q1", "2022Q1"],
            "news_count": [5, 5, 5],
            "combined_text": [
                "lợi nhuận tăng mạnh",
                "thị trường ổn định",
                "giá cổ phiếu giảm",
            ],
        })
        df = compute_keyword_counts(df, keywords)
        result = compute_tfidf_features(df, keywords)
        # "lợi nhuận tăng" appears in only 1 doc → min_df=2 → tfidf = 0
        assert (result["tfidf_lợi nhuận tăng"] == 0).all()

    def test_tfidf_positive_for_frequent_keyword(self):
        """Keywords appearing in >= 2 docs should have positive tfidf."""
        keywords = ["lợi nhuận tăng"]
        df = pd.DataFrame({
            "ticker": ["VNM", "VCB", "FPT"],
            "quarter_id": ["2022Q1", "2022Q1", "2022Q1"],
            "news_count": [5, 5, 5],
            "combined_text": [
                "lợi nhuận tăng mạnh",
                "lợi nhuận tăng nhẹ",
                "giá cổ phiếu giảm",
            ],
        })
        df = compute_keyword_counts(df, keywords)
        result = compute_tfidf_features(df, keywords)
        # Appears in 2 docs → should have positive tfidf for those rows
        assert result["tfidf_lợi nhuận tăng"].iloc[0] > 0
        assert result["tfidf_lợi nhuận tăng"].iloc[1] > 0
        assert result["tfidf_lợi nhuận tăng"].iloc[2] == 0  # not in this doc


# ---------------------------------------------------------------------------
# Coverage feature tests (Req 9.4)
# ---------------------------------------------------------------------------


class TestCoverageFeatures:
    """Test coverage feature computation."""

    def test_news_count_log(self):
        """news_count_log should equal log(news_count + 1)."""
        df = pd.DataFrame({"news_count": [0, 1, 5, 10, 100]})
        result = add_coverage_features(df)
        for idx in result.index:
            nc = result.loc[idx, "news_count"]
            expected = math.log(nc + 1)
            assert abs(result.loc[idx, "news_count_log"] - expected) < 1e-9

    def test_has_min_news_threshold(self):
        """has_min_news should be 1 if news_count >= 5, else 0."""
        df = pd.DataFrame({"news_count": [0, 4, 5, 6, 100]})
        result = add_coverage_features(df)
        expected = [0, 0, 1, 1, 1]
        assert result["has_min_news"].tolist() == expected


# ---------------------------------------------------------------------------
# Sparsity rate tests (Req 9.8)
# ---------------------------------------------------------------------------


class TestSparsityRate:
    """Test sparsity rate calculation."""

    def test_all_zeros_gives_100_percent(self):
        """All-zero keyword columns should give 100% sparsity."""
        keywords = ["kw_a", "kw_b"]
        # Note: compute_sparsity_rate looks for columns named kw_{keyword}
        # so we use the keyword names directly
        kw_names = ["a", "b"]
        df = pd.DataFrame({
            "kw_a": [0, 0, 0],
            "kw_b": [0, 0, 0],
        })
        overall, per_kw = compute_sparsity_rate(df, kw_names)
        assert abs(overall - 1.0) < 1e-9
        assert abs(per_kw["a"] - 1.0) < 1e-9
        assert abs(per_kw["b"] - 1.0) < 1e-9

    def test_no_zeros_gives_0_percent(self):
        """No zero values should give 0% sparsity."""
        kw_names = ["a", "b"]
        df = pd.DataFrame({
            "kw_a": [1, 2, 3],
            "kw_b": [4, 5, 6],
        })
        overall, per_kw = compute_sparsity_rate(df, kw_names)
        assert abs(overall - 0.0) < 1e-9
        assert abs(per_kw["a"] - 0.0) < 1e-9

    def test_mixed_sparsity(self):
        """Mixed values should give correct sparsity."""
        kw_names = ["a", "b"]
        df = pd.DataFrame({
            "kw_a": [0, 1, 0, 1],  # 50% sparse
            "kw_b": [0, 0, 0, 1],  # 75% sparse
        })
        overall, per_kw = compute_sparsity_rate(df, kw_names)
        # Total: 5 zeros out of 8 cells = 62.5%
        assert abs(overall - 5 / 8) < 1e-9
        assert abs(per_kw["a"] - 0.5) < 1e-9
        assert abs(per_kw["b"] - 0.75) < 1e-9

    def test_empty_dataframe(self):
        """Empty DataFrame should return 0 sparsity."""
        kw_names = ["a"]
        df = pd.DataFrame({"kw_a": pd.Series([], dtype=float)})
        overall, per_kw = compute_sparsity_rate(df, kw_names)
        assert overall == 0.0


# ---------------------------------------------------------------------------
# Integration test — extract_keyword_features
# ---------------------------------------------------------------------------


class TestExtractKeywordFeatures:
    """Test the main extract_keyword_features function end-to-end."""

    def test_returns_dataframe_with_expected_columns(
        self, sample_df, sample_keywords_by_direction
    ):
        """Output should have ticker, quarter_id, and all feature columns."""
        result = extract_keyword_features(sample_df, sample_keywords_by_direction)
        assert "ticker" in result.columns
        assert "quarter_id" in result.columns
        assert "pos_score" in result.columns
        assert "neg_score" in result.columns
        assert "sentiment_ratio" in result.columns
        assert "news_count" in result.columns
        assert "news_count_log" in result.columns
        assert "has_min_news" in result.columns

    def test_combined_text_dropped(self, sample_df, sample_keywords_by_direction):
        """combined_text should not be in the output."""
        result = extract_keyword_features(sample_df, sample_keywords_by_direction)
        assert "combined_text" not in result.columns

    def test_row_count_preserved(self, sample_df, sample_keywords_by_direction):
        """Number of rows should match input."""
        result = extract_keyword_features(sample_df, sample_keywords_by_direction)
        assert len(result) == len(sample_df)

    def test_sparse_values_kept_as_is(self, sample_keywords_by_direction):
        """Zero values should remain zero, not imputed (Req 9.8)."""
        df = pd.DataFrame({
            "ticker": ["VNM"],
            "quarter_id": ["2022Q1"],
            "news_count": [5],
            "combined_text": ["thị trường biến động"],
        })
        result = extract_keyword_features(df, sample_keywords_by_direction)
        # All keywords absent → raw counts should be 0
        for kw in (
            sample_keywords_by_direction["positive"]
            + sample_keywords_by_direction["negative"]
            + sample_keywords_by_direction["neutral"]
        ):
            assert result[f"kw_{kw}"].iloc[0] == 0
