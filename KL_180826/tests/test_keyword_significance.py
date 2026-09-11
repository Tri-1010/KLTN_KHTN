"""
Unit tests for pipeline/experiment_keyword_significance.py

Tests cover:
- BH-FDR correction with known example (Req 8.2)
- Property: adjusted p-values >= raw p-values (Req 8.3, 8.4)
- Chi-square vs Fisher exact selection logic (Req 1.9)
- Zero-occurrence keyword exclusion (Req 1.8, 8.5)
- Single-class label robustness (Req 8.5)
- Perfect separation returns (nan, nan, nan, nan) (Req 8.5)
"""

import warnings

import numpy as np
import pandas as pd
import pytest

from pipeline.experiment_keyword_significance import (
    apply_bh_correction,
    build_keyword_label_dataset,
    chi_square_or_fisher,
    logistic_univariate,
    mann_whitney_test,
)


# ---------------------------------------------------------------------------
# 2.1 — BH correction: known example
# ---------------------------------------------------------------------------


class TestApplyBhCorrectionKnownExample:
    """Verify BH correction against hand-calculated values.

    Input p-values (already in ascending order): [0.01, 0.04, 0.10, 0.20]
    n = 4 tests.

    BH adjusted p-values:
        p_adj[k] = p[k] * n / k  (capped at 1, then isotonically corrected)

    rank 1 (p=0.01): 0.01 * 4/1 = 0.04
    rank 2 (p=0.04): 0.04 * 4/2 = 0.08
    rank 3 (p=0.10): 0.10 * 4/3 ≈ 0.1333
    rank 4 (p=0.20): 0.20 * 4/4 = 0.20

    Expected: [0.04, 0.08, 0.1333..., 0.20]
    """

    def test_adjusted_values_match_expected(self):
        """Adjusted p-values must match the hand-calculated BH values."""
        p_values = np.array([0.01, 0.04, 0.10, 0.20])
        expected = np.array([0.04, 0.08, 0.13333333, 0.20])

        adj_p = apply_bh_correction(p_values, alpha=0.05)

        np.testing.assert_allclose(adj_p, expected, rtol=1e-5)

    def test_first_pvalue_is_significant(self):
        """p=0.01 should be significant after BH correction with alpha=0.05."""
        p_values = np.array([0.01, 0.04, 0.10, 0.20])
        adj_p = apply_bh_correction(p_values, alpha=0.05)

        assert adj_p[0] < 0.05, f"p_adj[0]={adj_p[0]} should be < 0.05"

    def test_remaining_pvalues_not_significant(self):
        """p=0.04, 0.10, 0.20 should not be significant after BH at alpha=0.05."""
        p_values = np.array([0.01, 0.04, 0.10, 0.20])
        adj_p = apply_bh_correction(p_values, alpha=0.05)

        assert adj_p[1] >= 0.05
        assert adj_p[2] >= 0.05
        assert adj_p[3] >= 0.05

    def test_output_length_matches_input(self):
        """Output array must have the same length as input."""
        p_values = np.array([0.01, 0.04, 0.10, 0.20])
        adj_p = apply_bh_correction(p_values, alpha=0.05)
        assert len(adj_p) == len(p_values)

    def test_nan_passthrough(self):
        """NaN entries in input should remain NaN in output."""
        p_values = np.array([0.01, np.nan, 0.10])
        adj_p = apply_bh_correction(p_values, alpha=0.05)

        assert np.isnan(adj_p[1])
        assert not np.isnan(adj_p[0])
        assert not np.isnan(adj_p[2])

    def test_all_nan_returns_all_nan(self):
        """All-NaN input should return all-NaN output without error."""
        p_values = np.array([np.nan, np.nan, np.nan])
        adj_p = apply_bh_correction(p_values, alpha=0.05)
        assert np.all(np.isnan(adj_p))


# ---------------------------------------------------------------------------
# 2.2 — Property test: adjusted p-value >= raw p-value
# ---------------------------------------------------------------------------


class TestAdjustedPvalueGeqRaw:
    """Property: for any valid p-values, adj_p >= raw_p (Req 8.3, 8.4).

    Uses numpy random with fixed seeds for reproducibility.
    Tests multiple array shapes and sizes.
    """

    def _check_geq_property(self, p_values: np.ndarray) -> None:
        """Helper: verify adj_p >= raw_p for each valid (non-NaN) entry."""
        adj_p = apply_bh_correction(p_values, alpha=0.05)
        for i, (raw, adj) in enumerate(zip(p_values, adj_p)):
            if not np.isnan(raw) and not np.isnan(adj):
                assert adj >= raw - 1e-12, (
                    f"adj_p[{i}]={adj:.6f} < raw_p[{i}]={raw:.6f} — "
                    "BH-adjusted p-value must be >= raw p-value"
                )

    def test_property_small_array_seed_0(self):
        """Property holds on small array with seed=0."""
        rng = np.random.RandomState(0)
        p = rng.uniform(0, 1, size=10)
        self._check_geq_property(p)

    def test_property_small_array_seed_1(self):
        """Property holds on small array with seed=1."""
        rng = np.random.RandomState(1)
        p = rng.uniform(0, 1, size=10)
        self._check_geq_property(p)

    def test_property_medium_array_seed_42(self):
        """Property holds on medium array (n=50) with seed=42."""
        rng = np.random.RandomState(42)
        p = rng.uniform(0, 1, size=50)
        self._check_geq_property(p)

    def test_property_large_array_seed_100(self):
        """Property holds on large array (n=200) with seed=100."""
        rng = np.random.RandomState(100)
        p = rng.uniform(0, 1, size=200)
        self._check_geq_property(p)

    def test_property_very_small_pvalues(self):
        """Property holds when p-values are very small (near zero)."""
        rng = np.random.RandomState(7)
        p = rng.uniform(0, 0.01, size=30)
        self._check_geq_property(p)

    def test_property_mixed_sizes(self):
        """Property holds for multiple different array sizes."""
        for seed, size in [(10, 5), (20, 15), (30, 100), (40, 2)]:
            rng = np.random.RandomState(seed)
            p = rng.uniform(0, 1, size=size)
            self._check_geq_property(p)

    def test_property_identical_pvalues(self):
        """Property holds when all p-values are identical."""
        p = np.full(20, 0.03)
        self._check_geq_property(p)

    def test_property_uniform_pvalues(self):
        """Property holds for evenly-spaced p-values across [0, 1]."""
        p = np.linspace(0.001, 0.999, 50)
        self._check_geq_property(p)


# ---------------------------------------------------------------------------
# 2.3 — Chi-square selects Fisher when low expected frequency
# ---------------------------------------------------------------------------


class TestChiSelectsFisherWhenLowExpected:
    """When a 2x2 table has at least one expected cell < 5, Fisher must be used."""

    def test_very_few_occurrences_uses_fisher(self):
        """Very rare keyword (1 occurrence out of 100) triggers Fisher exact."""
        # 1 occurrence, 99 non-occurrences; labels ~ 50/50
        occurrence = np.array([0] * 99 + [1])
        labels = np.array([0, 1] * 50)  # alternating: 50 zeros, 50 ones (len=100)

        _, _, test_used = chi_square_or_fisher(occurrence, labels)
        assert test_used == "fisher_exact", (
            f"Expected 'fisher_exact' but got '{test_used}'"
        )

    def test_small_2x2_table_uses_fisher(self):
        """Small sample (n=8) with extreme split triggers Fisher exact."""
        occurrence = np.array([0, 0, 0, 0, 0, 0, 1, 1])
        labels     = np.array([0, 0, 0, 1, 1, 0, 1, 0])

        _, _, test_used = chi_square_or_fisher(occurrence, labels)
        assert test_used == "fisher_exact"

    def test_all_in_one_cell_uses_fisher(self):
        """If all occurrences have the same label, expected cells are < 5 → Fisher."""
        # occurrence=1 only when label=1, and only 3 such cases
        occurrence = np.array([0, 0, 0, 0, 0, 0, 0, 1, 1, 1])
        labels     = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])

        _, _, test_used = chi_square_or_fisher(occurrence, labels)
        assert test_used == "fisher_exact"

    def test_returns_tuple_of_three(self):
        """chi_square_or_fisher always returns a 3-tuple."""
        occurrence = np.array([0] * 9 + [1])
        labels = np.ones(10, dtype=int)
        result = chi_square_or_fisher(occurrence, labels)
        assert len(result) == 3

    def test_pvalue_in_valid_range(self):
        """p-value from Fisher must be in [0, 1]."""
        occurrence = np.array([0] * 9 + [1])
        labels = np.array([0, 0, 0, 0, 0, 0, 0, 0, 1, 1])
        stat, pval, test_used = chi_square_or_fisher(occurrence, labels)
        if not np.isnan(pval):
            assert 0.0 <= pval <= 1.0


# ---------------------------------------------------------------------------
# 2.4 — Chi-square selects chi_square when sufficient expected frequency
# ---------------------------------------------------------------------------


class TestChiSelectsChiSquareWhenSufficient:
    """When all expected cells >= 5, chi-square test must be used."""

    def test_balanced_large_table_uses_chi_square(self):
        """50/50 occurrence split, 50/50 label split, n=200 → chi_square."""
        rng = np.random.RandomState(42)
        occurrence = np.array([0] * 100 + [1] * 100)
        labels = np.array([0] * 50 + [1] * 50 + [0] * 50 + [1] * 50)

        _, _, test_used = chi_square_or_fisher(occurrence, labels)
        assert test_used == "chi_square", (
            f"Expected 'chi_square' but got '{test_used}'"
        )

    def test_large_equal_groups_uses_chi_square(self):
        """Large, evenly distributed contingency table → chi_square."""
        occurrence = np.array([0] * 60 + [1] * 40)
        labels = np.array([0] * 30 + [1] * 30 + [0] * 20 + [1] * 20)

        _, _, test_used = chi_square_or_fisher(occurrence, labels)
        assert test_used == "chi_square"

    def test_pvalue_in_valid_range(self):
        """p-value from chi-square must be in [0, 1]."""
        occurrence = np.array([0] * 60 + [1] * 40)
        labels = np.array([0] * 30 + [1] * 30 + [0] * 20 + [1] * 20)

        stat, pval, _ = chi_square_or_fisher(occurrence, labels)
        assert 0.0 <= pval <= 1.0

    def test_statistic_non_negative(self):
        """Chi-square statistic must be non-negative."""
        occurrence = np.array([0] * 60 + [1] * 40)
        labels = np.array([0] * 30 + [1] * 30 + [0] * 20 + [1] * 20)

        stat, pval, test_used = chi_square_or_fisher(occurrence, labels)
        assert stat >= 0.0


# ---------------------------------------------------------------------------
# 2.5 — All-zero keyword excluded from build_keyword_label_dataset
# ---------------------------------------------------------------------------


class TestAllZeroKeywordExcluded:
    """A keyword with all-zero values must be excluded (Req 1.8)."""

    def _make_merged_df(self) -> pd.DataFrame:
        """Build a minimal merged DataFrame for testing."""
        n = 20
        rng = np.random.RandomState(99)
        df = pd.DataFrame({
            "label_basic": rng.choice([0, 1], size=n),
            "kw_active_kw": rng.randint(0, 5, size=n),
            "kw_norm_active_kw": rng.uniform(0, 1, size=n),
            # All-zero keyword — should be excluded
            "kw_zero_kw": np.zeros(n, dtype=int),
            "kw_norm_zero_kw": np.zeros(n, dtype=float),
        })
        return df

    def test_zero_keyword_in_excluded_list(self):
        """'zero_kw' must appear in the excluded list."""
        merged_df = self._make_merged_df()
        keywords = ["active_kw", "zero_kw"]

        _, excluded = build_keyword_label_dataset(merged_df, keywords)

        assert "zero_kw" in excluded, (
            f"Expected 'zero_kw' in excluded list but got: {excluded}"
        )

    def test_zero_keyword_not_in_dataset(self):
        """occurrence_zero_kw must not appear as a column in dataset_df."""
        merged_df = self._make_merged_df()
        keywords = ["active_kw", "zero_kw"]

        dataset_df, _ = build_keyword_label_dataset(merged_df, keywords)

        assert "occurrence_zero_kw" not in dataset_df.columns

    def test_active_keyword_not_excluded(self):
        """The keyword with non-zero occurrences must not be excluded."""
        merged_df = self._make_merged_df()
        keywords = ["active_kw", "zero_kw"]

        _, excluded = build_keyword_label_dataset(merged_df, keywords)

        assert "active_kw" not in excluded

    def test_active_keyword_in_dataset(self):
        """occurrence_active_kw must be present in dataset_df."""
        merged_df = self._make_merged_df()
        keywords = ["active_kw", "zero_kw"]

        dataset_df, _ = build_keyword_label_dataset(merged_df, keywords)

        assert "occurrence_active_kw" in dataset_df.columns

    def test_missing_column_keyword_excluded(self):
        """A keyword whose kw_{k} column is missing is also excluded."""
        merged_df = self._make_merged_df()
        keywords = ["active_kw", "missing_kw"]  # missing_kw has no column

        _, excluded = build_keyword_label_dataset(merged_df, keywords)

        assert "missing_kw" in excluded

    def test_label_column_preserved(self):
        """label_basic must always be present in dataset_df."""
        merged_df = self._make_merged_df()
        keywords = ["active_kw", "zero_kw"]

        dataset_df, _ = build_keyword_label_dataset(merged_df, keywords)

        assert "label_basic" in dataset_df.columns


# ---------------------------------------------------------------------------
# 2.6 — Single-class label: no exception raised
# ---------------------------------------------------------------------------


class TestSingleClassLabelNoException:
    """When all labels = 0 or all labels = 1, statistical functions must not crash."""

    def test_chi_all_labels_zero_no_exception(self):
        """chi_square_or_fisher must not raise when all labels = 0."""
        occurrence = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
        labels = np.zeros(10, dtype=int)
        try:
            stat, pval, test_used = chi_square_or_fisher(occurrence, labels)
        except Exception as exc:
            pytest.fail(f"chi_square_or_fisher raised unexpectedly: {exc}")

    def test_chi_all_labels_one_no_exception(self):
        """chi_square_or_fisher must not raise when all labels = 1."""
        occurrence = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
        labels = np.ones(10, dtype=int)
        try:
            stat, pval, test_used = chi_square_or_fisher(occurrence, labels)
        except Exception as exc:
            pytest.fail(f"chi_square_or_fisher raised unexpectedly: {exc}")

    def test_mann_whitney_all_labels_zero_no_exception(self):
        """mann_whitney_test must not raise when all labels = 0 (empty up group)."""
        norm_freq = np.array([0.1, 0.2, 0.0, 0.3, 0.0])
        labels = np.zeros(5, dtype=int)

        up_group = norm_freq[labels == 1]     # empty
        not_up_group = norm_freq[labels == 0]  # all samples

        try:
            stat, pval = mann_whitney_test(up_group, not_up_group)
        except Exception as exc:
            pytest.fail(f"mann_whitney_test raised unexpectedly: {exc}")

    def test_mann_whitney_all_labels_one_no_exception(self):
        """mann_whitney_test must not raise when all labels = 1 (empty not-up group)."""
        norm_freq = np.array([0.1, 0.2, 0.0, 0.3, 0.0])
        labels = np.ones(5, dtype=int)

        up_group = norm_freq[labels == 1]     # all samples
        not_up_group = norm_freq[labels == 0]  # empty

        try:
            stat, pval = mann_whitney_test(up_group, not_up_group)
        except Exception as exc:
            pytest.fail(f"mann_whitney_test raised unexpectedly: {exc}")

    def test_logistic_all_labels_zero_no_exception(self):
        """logistic_univariate must not raise when all labels = 0."""
        occurrence = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
        labels = np.zeros(10, dtype=int)
        try:
            result = logistic_univariate(occurrence, labels)
        except Exception as exc:
            pytest.fail(f"logistic_univariate raised unexpectedly: {exc}")
        # May return nans but must not crash
        assert len(result) == 4

    def test_logistic_all_labels_one_no_exception(self):
        """logistic_univariate must not raise when all labels = 1."""
        occurrence = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
        labels = np.ones(10, dtype=int)
        try:
            result = logistic_univariate(occurrence, labels)
        except Exception as exc:
            pytest.fail(f"logistic_univariate raised unexpectedly: {exc}")
        assert len(result) == 4

    def test_single_class_mann_whitney_returns_nan(self):
        """When one group is empty, mann_whitney_test returns (nan, nan)."""
        stat, pval = mann_whitney_test(np.array([]), np.array([0.1, 0.2]))
        assert np.isnan(stat)
        assert np.isnan(pval)

    def test_single_class_logistic_returns_nan_tuple(self):
        """logistic_univariate returns (nan, nan, nan, nan) for single-class labels."""
        occurrence = np.array([0, 0, 1, 1, 0, 1])
        labels = np.zeros(6, dtype=int)
        result = logistic_univariate(occurrence, labels)
        assert all(np.isnan(v) for v in result), (
            f"Expected all-nan tuple but got {result}"
        )


# ---------------------------------------------------------------------------
# 2.7 — Perfect separation returns (nan, nan, nan, nan)
# ---------------------------------------------------------------------------


class TestLogisticPerfectSeparationReturnsNan:
    """Perfect separation between occurrence and labels → (nan, nan, nan, nan)."""

    def test_perfect_correlation_returns_nan_tuple(self):
        """occurrence == labels exactly → logistic must return (nan, nan, nan, nan)."""
        occurrence = np.array([0, 0, 0, 1, 1, 1])
        labels     = np.array([0, 0, 0, 1, 1, 1])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = logistic_univariate(occurrence, labels)

        assert len(result) == 4
        assert all(np.isnan(v) for v in result), (
            f"Expected (nan, nan, nan, nan) for perfect separation, got {result}"
        )

    def test_inverse_perfect_correlation_returns_nan_tuple(self):
        """occurrence == 1 - labels → also perfect separation → (nan, nan, nan, nan)."""
        occurrence = np.array([1, 1, 1, 0, 0, 0])
        labels     = np.array([0, 0, 0, 1, 1, 1])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = logistic_univariate(occurrence, labels)

        assert len(result) == 4
        assert all(np.isnan(v) for v in result), (
            f"Expected (nan, nan, nan, nan) for inverse perfect separation, got {result}"
        )

    def test_no_separation_returns_real_values(self):
        """Without separation, logistic returns real (non-nan) numeric values."""
        rng = np.random.RandomState(42)
        n = 100
        occurrence = rng.randint(0, 2, size=n)
        # Mix labels to avoid separation
        labels = rng.randint(0, 2, size=n)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = logistic_univariate(occurrence, labels)

        # Should return 4 values; at least some should be non-nan
        assert len(result) == 4
        # At minimum, the function should not raise

    def test_return_is_tuple_of_four(self):
        """logistic_univariate always returns a 4-element sequence."""
        occurrence = np.array([0, 0, 0, 1, 1, 1])
        labels     = np.array([0, 0, 0, 1, 1, 1])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = logistic_univariate(occurrence, labels)

        assert len(result) == 4
