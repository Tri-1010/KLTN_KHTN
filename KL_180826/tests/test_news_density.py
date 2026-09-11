"""
Unit tests for pipeline/experiment_news_density.py

Tests cover:
- split_by_news_density: correct grouping on has_min_news (Req 3.1)
- check_group_reliability: low samples, single class, sufficient samples (Req 3.5)
- Edge cases: all-dense, all-sparse, reliable groups
"""

import numpy as np
import pandas as pd
import pytest

from pipeline.experiment_news_density import (
    check_group_reliability,
    split_by_news_density,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_test_df(n_dense: int, n_sparse: int, seed: int = 0) -> pd.DataFrame:
    """Build a synthetic test DataFrame with has_min_news and label_basic."""
    rng = np.random.RandomState(seed)
    total = n_dense + n_sparse
    has_min_news = [1] * n_dense + [0] * n_sparse
    label_basic = rng.randint(0, 2, size=total).tolist()
    return pd.DataFrame({
        "has_min_news": has_min_news,
        "label_basic": label_basic,
        "feature_a": rng.randn(total),
    })


def _make_group_df(
    n: int,
    n_classes: int = 2,
    seed: int = 0,
) -> pd.DataFrame:
    """Build a group DataFrame with a specified number of label classes."""
    rng = np.random.RandomState(seed)
    if n_classes == 1:
        labels = [0] * n  # only class 0
    else:
        # Alternate 0 and 1 to ensure both classes present
        labels = [i % 2 for i in range(n)]
    return pd.DataFrame({
        "label_basic": labels,
        "feature_a": rng.randn(n),
    })


# ---------------------------------------------------------------------------
# 4.1 — test_split_by_news_density
# ---------------------------------------------------------------------------


class TestSplitByNewsDensity:
    """Verify split_by_news_density partitions test_df correctly."""

    def test_split_by_density_correct_groups(self):
        """has_min_news=1 rows go to dense; has_min_news=0 rows go to sparse."""
        df = _make_test_df(n_dense=15, n_sparse=10)
        dense_df, sparse_df = split_by_news_density(df)

        assert (dense_df["has_min_news"] == 1).all(), (
            "Dense group must contain only rows with has_min_news=1"
        )
        assert (sparse_df["has_min_news"] == 0).all(), (
            "Sparse group must contain only rows with has_min_news=0"
        )

    def test_split_correct_sizes(self):
        """Resulting groups have the expected row counts."""
        df = _make_test_df(n_dense=12, n_sparse=8)
        dense_df, sparse_df = split_by_news_density(df)

        assert len(dense_df) == 12, f"Expected 12 dense rows, got {len(dense_df)}"
        assert len(sparse_df) == 8, f"Expected 8 sparse rows, got {len(sparse_df)}"

    def test_split_union_equals_original(self):
        """dense + sparse must cover all original rows (no rows lost or duplicated)."""
        df = _make_test_df(n_dense=10, n_sparse=10)
        dense_df, sparse_df = split_by_news_density(df)

        assert len(dense_df) + len(sparse_df) == len(df), (
            "Total rows after split must equal original DataFrame length"
        )

    def test_split_handles_all_dense(self):
        """When all rows have has_min_news=1, sparse_df must be empty."""
        df = _make_test_df(n_dense=20, n_sparse=0)
        dense_df, sparse_df = split_by_news_density(df)

        assert len(dense_df) == 20
        assert len(sparse_df) == 0, "sparse_df must be empty when all rows are dense"

    def test_split_handles_all_sparse(self):
        """When all rows have has_min_news=0, dense_df must be empty."""
        df = _make_test_df(n_dense=0, n_sparse=20)
        dense_df, sparse_df = split_by_news_density(df)

        assert len(dense_df) == 0, "dense_df must be empty when all rows are sparse"
        assert len(sparse_df) == 20

    def test_split_preserves_other_columns(self):
        """Other columns (e.g. label_basic) must be preserved in split groups."""
        df = _make_test_df(n_dense=5, n_sparse=5)
        dense_df, sparse_df = split_by_news_density(df)

        assert "label_basic" in dense_df.columns
        assert "label_basic" in sparse_df.columns
        assert "feature_a" in dense_df.columns
        assert "feature_a" in sparse_df.columns

    def test_split_returns_copies_not_views(self):
        """Modifying returned DataFrames must not affect original."""
        df = _make_test_df(n_dense=5, n_sparse=5)
        dense_df, sparse_df = split_by_news_density(df)

        # Modifying the dense_df should not raise any warnings or change df
        dense_df["new_col"] = 99
        assert "new_col" not in df.columns


# ---------------------------------------------------------------------------
# 4.2 — test_check_group_reliability
# ---------------------------------------------------------------------------


class TestCheckGroupReliability:
    """Verify check_group_reliability returns correct reliability status."""

    def test_check_reliability_low_samples(self):
        """< 20 samples → returns (False, non-empty warning)."""
        group_df = _make_group_df(n=10, n_classes=2)
        is_reliable, warning_msg = check_group_reliability(group_df, min_samples=20)

        assert is_reliable is False, "Group with 10 samples should be unreliable"
        assert len(warning_msg) > 0, "Warning message must not be empty"

    def test_check_reliability_low_samples_warning_contains_n(self):
        """Warning for low samples must mention the actual sample count."""
        group_df = _make_group_df(n=5, n_classes=2)
        _, warning_msg = check_group_reliability(group_df, min_samples=20)

        assert "5" in warning_msg, (
            f"Warning '{warning_msg}' should mention the sample count N=5"
        )

    def test_check_reliability_low_samples_warning_contains_min(self):
        """Warning for low samples must mention the minimum threshold."""
        group_df = _make_group_df(n=10, n_classes=2)
        _, warning_msg = check_group_reliability(group_df, min_samples=20)

        assert "20" in warning_msg, (
            f"Warning '{warning_msg}' should mention the minimum threshold 20"
        )

    def test_check_reliability_single_class(self):
        """Only 1 unique label class → returns (False, non-empty warning)."""
        group_df = _make_group_df(n=30, n_classes=1)
        is_reliable, warning_msg = check_group_reliability(group_df, min_samples=20)

        assert is_reliable is False, (
            "Group with only 1 label class should be unreliable"
        )
        assert len(warning_msg) > 0, "Warning message must not be empty"

    def test_check_reliability_single_class_warning_mentions_class(self):
        """Warning for single class must mention the class issue."""
        group_df = _make_group_df(n=30, n_classes=1)
        _, warning_msg = check_group_reliability(group_df, min_samples=20)

        assert "lớp" in warning_msg.lower() or "class" in warning_msg.lower(), (
            f"Warning '{warning_msg}' should mention the label class issue"
        )

    def test_check_reliability_both_conditions_fail(self):
        """Both < 20 samples AND single class → warning mentions both conditions."""
        group_df = _make_group_df(n=5, n_classes=1)
        is_reliable, warning_msg = check_group_reliability(group_df, min_samples=20)

        assert is_reliable is False
        # Should mention both issues
        assert "5" in warning_msg, "Should mention sample count"
        # Should have some content about class
        assert len(warning_msg) > 10, "Warning should be descriptive for both failures"

    def test_check_reliability_sufficient_samples(self):
        """≥ 20 samples and both classes → returns (True, '')."""
        group_df = _make_group_df(n=25, n_classes=2)
        is_reliable, warning_msg = check_group_reliability(group_df, min_samples=20)

        assert is_reliable is True, (
            "Group with 25 samples and 2 classes should be reliable"
        )
        assert warning_msg == "", (
            f"Expected empty warning for reliable group, got: '{warning_msg}'"
        )

    def test_check_reliability_returns_true(self):
        """Reliable group returns exactly (True, '')."""
        group_df = _make_group_df(n=50, n_classes=2)
        result = check_group_reliability(group_df, min_samples=20)

        assert result == (True, ""), (
            f"Expected (True, ''), got {result}"
        )

    def test_check_reliability_exactly_at_threshold(self):
        """Exactly min_samples rows (not below) with 2 classes → reliable."""
        group_df = _make_group_df(n=20, n_classes=2)
        is_reliable, _ = check_group_reliability(group_df, min_samples=20)

        assert is_reliable is True, (
            "Group with exactly min_samples=20 rows should be reliable"
        )

    def test_check_reliability_one_below_threshold(self):
        """Exactly min_samples - 1 rows → not reliable."""
        group_df = _make_group_df(n=19, n_classes=2)
        is_reliable, _ = check_group_reliability(group_df, min_samples=20)

        assert is_reliable is False, (
            "Group with 19 rows (< 20 min) should be unreliable"
        )

    def test_check_reliability_custom_min_samples(self):
        """Custom min_samples parameter is respected."""
        group_df = _make_group_df(n=10, n_classes=2)
        # With min_samples=5, a group of 10 should be reliable
        is_reliable, _ = check_group_reliability(group_df, min_samples=5)

        assert is_reliable is True, (
            "Group with 10 samples should be reliable when min_samples=5"
        )

    def test_check_reliability_empty_group(self):
        """Empty DataFrame → not reliable (0 < min_samples)."""
        group_df = pd.DataFrame({"label_basic": [], "feature_a": []})
        is_reliable, warning_msg = check_group_reliability(group_df, min_samples=20)

        assert is_reliable is False
        assert len(warning_msg) > 0

    def test_check_reliability_warning_is_string(self):
        """Warning message must always be a string (never None)."""
        group_df_ok = _make_group_df(n=30, n_classes=2)
        group_df_bad = _make_group_df(n=5, n_classes=1)

        _, msg_ok = check_group_reliability(group_df_ok)
        _, msg_bad = check_group_reliability(group_df_bad)

        assert isinstance(msg_ok, str), "Warning must be a string for reliable group"
        assert isinstance(msg_bad, str), "Warning must be a string for unreliable group"
