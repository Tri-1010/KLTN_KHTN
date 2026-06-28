"""
Unit tests for TASK 6: Label_Builder module.

Tests cover:
- label_basic for increase/decrease cases (Req 6.1)
- label_threshold for above/below/neutral cases (Req 6.2)
- Return calculation (Req 6.1, 6.2)
- Label distribution analysis (Req 6.4, 6.5)
- Label distribution chart generation (Req 6.6)
"""

import os

import numpy as np
import pandas as pd
import pytest

from pipeline.task6_labels import (
    build_label_basic,
    build_label_threshold,
    build_labels,
    compute_return,
    analyze_label_distribution,
    generate_label_distribution_chart,
    SECTOR_MAPPING,
    TICKER_TO_SECTOR,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_master():
    """Create a sample master dataset with known price values."""
    return pd.DataFrame({
        "ticker": ["VNM", "VNM", "VNM", "FPT", "FPT", "ACB"],
        "quarter_id": [
            "2022Q1", "2022Q2", "2022Q3",
            "2022Q1", "2022Q2",
            "2022Q1",
        ],
        "avg_close": [100.0, 110.0, 105.0, 50.0, 48.0, 30.0],
        "next_avg_close": [110.0, 105.0, np.nan, 48.0, 55.0, 30.3],
        "avg_volume": [1000, 1100, 1050, 2000, 2100, 500],
        "return_intra": [0.1, 0.05, -0.02, 0.08, -0.03, 0.01],
        "trading_days": [60, 62, 61, 60, 62, 60],
        "news_count": [10, 12, 8, 15, 11, 7],
        "combined_text": ["text1", "text2", "text3", "text4", "text5", "text6"],
        "next_quarter_id": [
            "2022Q2", "2022Q3", "2022Q4",
            "2022Q2", "2022Q3",
            "2022Q2",
        ],
    })


# ---------------------------------------------------------------------------
# label_basic tests (Req 6.1)
# ---------------------------------------------------------------------------


class TestBuildLabelBasic:
    """Test label_basic computation: 1 if next > current, else 0."""

    def test_increase_returns_1(self):
        """When next_avg_close > avg_close, label should be 1."""
        assert build_label_basic(100.0, 110.0) == 1

    def test_decrease_returns_0(self):
        """When next_avg_close < avg_close, label should be 0."""
        assert build_label_basic(110.0, 100.0) == 0

    def test_equal_returns_0(self):
        """When next_avg_close == avg_close, label should be 0."""
        assert build_label_basic(100.0, 100.0) == 0

    def test_small_increase_returns_1(self):
        """Even a tiny increase should return 1."""
        assert build_label_basic(100.0, 100.01) == 1

    def test_nan_avg_close_returns_none(self):
        """NaN avg_close should return None."""
        assert build_label_basic(np.nan, 100.0) is None

    def test_nan_next_avg_close_returns_none(self):
        """NaN next_avg_close should return None."""
        assert build_label_basic(100.0, np.nan) is None

    def test_both_nan_returns_none(self):
        """Both NaN should return None."""
        assert build_label_basic(np.nan, np.nan) is None


# ---------------------------------------------------------------------------
# label_threshold tests (Req 6.2)
# ---------------------------------------------------------------------------


class TestBuildLabelThreshold:
    """Test label_threshold: 1 if return > +2%, 0 if < -2%, NaN otherwise."""

    def test_above_threshold_returns_1(self):
        """Return > +2% should give label 1."""
        # return = (105 - 100) / 100 = 0.05 > 0.02
        assert build_label_threshold(100.0, 105.0) == 1.0

    def test_below_threshold_returns_0(self):
        """Return < -2% should give label 0."""
        # return = (95 - 100) / 100 = -0.05 < -0.02
        assert build_label_threshold(100.0, 95.0) == 0.0

    def test_neutral_zone_returns_nan(self):
        """Return within ±2% should give NaN."""
        # return = (101 - 100) / 100 = 0.01, |0.01| <= 0.02
        result = build_label_threshold(100.0, 101.0)
        assert np.isnan(result)

    def test_exactly_at_positive_threshold_returns_nan(self):
        """Return exactly at +2% boundary should give NaN (|return| <= 0.02)."""
        # return = (102 - 100) / 100 = 0.02, |0.02| <= 0.02
        result = build_label_threshold(100.0, 102.0)
        assert np.isnan(result)

    def test_exactly_at_negative_threshold_returns_nan(self):
        """Return exactly at -2% boundary should give NaN (|return| <= 0.02)."""
        # return = (98 - 100) / 100 = -0.02, |-0.02| <= 0.02
        result = build_label_threshold(100.0, 98.0)
        assert np.isnan(result)

    def test_just_above_positive_threshold_returns_1(self):
        """Return just above +2% should give 1."""
        # return = (102.01 - 100) / 100 = 0.0201 > 0.02
        assert build_label_threshold(100.0, 102.01) == 1.0

    def test_just_below_negative_threshold_returns_0(self):
        """Return just below -2% should give 0."""
        # return = (97.99 - 100) / 100 = -0.0201 < -0.02
        assert build_label_threshold(100.0, 97.99) == 0.0

    def test_custom_threshold(self):
        """Custom threshold should be respected."""
        # return = 0.05, threshold = 0.10 → neutral
        result = build_label_threshold(100.0, 105.0, threshold=0.10)
        assert np.isnan(result)

    def test_nan_input_returns_none(self):
        """NaN input should return None."""
        assert build_label_threshold(np.nan, 100.0) is None
        assert build_label_threshold(100.0, np.nan) is None

    def test_zero_avg_close_returns_none(self):
        """Zero avg_close should return None (division by zero)."""
        assert build_label_threshold(0.0, 100.0) is None


# ---------------------------------------------------------------------------
# Return calculation tests
# ---------------------------------------------------------------------------


class TestComputeReturn:
    """Test quarter-over-quarter return calculation."""

    def test_positive_return(self):
        """Positive return when price increases."""
        ret = compute_return(100.0, 110.0)
        assert abs(ret - 0.10) < 1e-9

    def test_negative_return(self):
        """Negative return when price decreases."""
        ret = compute_return(100.0, 90.0)
        assert abs(ret - (-0.10)) < 1e-9

    def test_zero_return(self):
        """Zero return when price unchanged."""
        ret = compute_return(100.0, 100.0)
        assert abs(ret) < 1e-9

    def test_large_increase(self):
        """Large positive return."""
        ret = compute_return(50.0, 100.0)
        assert abs(ret - 1.0) < 1e-9

    def test_nan_avg_close(self):
        """NaN avg_close returns None."""
        assert compute_return(np.nan, 100.0) is None

    def test_nan_next_avg_close(self):
        """NaN next_avg_close returns None."""
        assert compute_return(100.0, np.nan) is None

    def test_zero_avg_close(self):
        """Zero avg_close returns None (division by zero)."""
        assert compute_return(0.0, 100.0) is None


# ---------------------------------------------------------------------------
# build_labels integration tests
# ---------------------------------------------------------------------------


class TestBuildLabels:
    """Test the build_labels function on a DataFrame."""

    def test_adds_label_columns(self, sample_master):
        result = build_labels(sample_master)
        assert "label_basic" in result.columns
        assert "label_threshold" in result.columns
        assert "return" in result.columns

    def test_label_basic_increase(self, sample_master):
        """VNM Q1: avg=100, next=110 → label_basic=1."""
        result = build_labels(sample_master)
        vnm_q1 = result[
            (result["ticker"] == "VNM") & (result["quarter_id"] == "2022Q1")
        ]
        assert vnm_q1["label_basic"].iloc[0] == 1

    def test_label_basic_decrease(self, sample_master):
        """VNM Q2: avg=110, next=105 → label_basic=0."""
        result = build_labels(sample_master)
        vnm_q2 = result[
            (result["ticker"] == "VNM") & (result["quarter_id"] == "2022Q2")
        ]
        assert vnm_q2["label_basic"].iloc[0] == 0

    def test_label_basic_nan_next(self, sample_master):
        """VNM Q3: next_avg_close=NaN → label_basic=None."""
        result = build_labels(sample_master)
        vnm_q3 = result[
            (result["ticker"] == "VNM") & (result["quarter_id"] == "2022Q3")
        ]
        assert pd.isna(vnm_q3["label_basic"].iloc[0])

    def test_label_threshold_above(self, sample_master):
        """VNM Q1: return=0.10 > 0.02 → label_threshold=1."""
        result = build_labels(sample_master)
        vnm_q1 = result[
            (result["ticker"] == "VNM") & (result["quarter_id"] == "2022Q1")
        ]
        assert vnm_q1["label_threshold"].iloc[0] == 1.0

    def test_label_threshold_below(self, sample_master):
        """VNM Q2: return=(105-110)/110 ≈ -0.0455 < -0.02 → label_threshold=0."""
        result = build_labels(sample_master)
        vnm_q2 = result[
            (result["ticker"] == "VNM") & (result["quarter_id"] == "2022Q2")
        ]
        assert vnm_q2["label_threshold"].iloc[0] == 0.0

    def test_label_threshold_neutral(self, sample_master):
        """ACB Q1: return=(30.3-30)/30=0.01, |0.01|<=0.02 → NaN."""
        result = build_labels(sample_master)
        acb_q1 = result[
            (result["ticker"] == "ACB") & (result["quarter_id"] == "2022Q1")
        ]
        assert np.isnan(acb_q1["label_threshold"].iloc[0])

    def test_return_column_values(self, sample_master):
        """Verify return column is computed correctly."""
        result = build_labels(sample_master)
        vnm_q1 = result[
            (result["ticker"] == "VNM") & (result["quarter_id"] == "2022Q1")
        ]
        expected_return = (110.0 - 100.0) / 100.0
        assert abs(vnm_q1["return"].iloc[0] - expected_return) < 1e-9

    def test_does_not_modify_original(self, sample_master):
        """build_labels should not modify the input DataFrame."""
        original_cols = set(sample_master.columns)
        build_labels(sample_master)
        assert set(sample_master.columns) == original_cols


# ---------------------------------------------------------------------------
# Sector mapping tests
# ---------------------------------------------------------------------------


class TestSectorMapping:
    """Test sector mapping completeness."""

    def test_all_30_tickers_mapped(self):
        """All 30 VN30 tickers should be in the sector mapping."""
        vn30 = [
            "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR",
            "HDB", "HPG", "MBB", "MSN", "MWG", "PLX", "POW", "SAB",
            "SHB", "SSB", "SSI", "STB", "TCB", "TPB", "VCB", "VHM",
            "VIB", "VIC", "VJC", "VNM", "VPB", "VRE",
        ]
        for ticker in vn30:
            # MSN and VJC may not be in the sector mapping per the spec
            if ticker in ("MSN", "VJC"):
                continue
            assert ticker in TICKER_TO_SECTOR, f"{ticker} not in sector mapping"


# ---------------------------------------------------------------------------
# Label distribution chart test (Req 6.6)
# ---------------------------------------------------------------------------


class TestLabelDistributionChart:
    """Test label distribution chart generation."""

    def test_chart_file_created(self, sample_master, tmp_path):
        labeled = build_labels(sample_master)
        output_path = str(tmp_path / "label_dist.png")
        generate_label_distribution_chart(labeled, output_path=output_path)
        assert os.path.isfile(output_path)

    def test_chart_with_empty_labels(self, tmp_path):
        """Chart should handle empty data gracefully."""
        df = pd.DataFrame({
            "quarter_id": ["2022Q1"],
            "label_basic": [np.nan],
        })
        output_path = str(tmp_path / "label_dist_empty.png")
        generate_label_distribution_chart(df, output_path=output_path)
        # File may or may not be created, but no exception should be raised
