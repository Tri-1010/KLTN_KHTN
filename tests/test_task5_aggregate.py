"""
Unit tests for TASK 5: Data_Aggregator module.

Tests cover:
- Quarter_id assignment for edge dates (Req 5.1)
- Price aggregation calculations (Req 5.3)
- News concatenation (Req 5.2)
- Next_quarter_id derivation (Req 5.4)
"""

import os

import pandas as pd
import pytest

from pipeline.task5_aggregate import (
    add_quarter_id,
    aggregate_news,
    aggregate_prices,
    assign_quarter_id,
    build_master_dataset,
    generate_coverage_heatmap,
    _next_quarter,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_prices():
    """Create a small daily price DataFrame for two tickers across Q1 and Q2."""
    rows = []
    # VNM: 3 trading days in Q1, 2 in Q2
    for date, close, volume in [
        ("2022-01-10", 100.0, 1000),
        ("2022-02-15", 110.0, 1200),
        ("2022-03-20", 120.0, 1100),
        ("2022-04-10", 130.0, 1500),
        ("2022-05-15", 125.0, 1400),
    ]:
        rows.append({
            "ticker": "VNM",
            "date": date,
            "open": close - 1,
            "high": close + 2,
            "low": close - 2,
            "close": close,
            "volume": volume,
        })
    # FPT: 2 trading days in Q1
    for date, close, volume in [
        ("2022-01-05", 50.0, 2000),
        ("2022-03-28", 55.0, 2500),
    ]:
        rows.append({
            "ticker": "FPT",
            "date": date,
            "open": close - 1,
            "high": close + 2,
            "low": close - 2,
            "close": close,
            "volume": volume,
        })
    return pd.DataFrame(rows)


@pytest.fixture
def sample_news():
    """Create a small news DataFrame for two tickers."""
    return pd.DataFrame({
        "date": [
            "2022-01-15",
            "2022-02-20",
            "2022-03-10",
            "2022-04-05",
            "2022-01-20",
        ],
        "ticker": ["VNM", "VNM", "VNM", "VNM", "FPT"],
        "title": ["Title A", "Title B", "Title C", "Title D", "Title E"],
        "text_tokenized": [
            "lợi_nhuận tăng mạnh",
            "doanh_thu quý tốt",
            "cổ_phiếu vnm tăng_giá",
            "kết_quả kinh_doanh quý 2",
            "fpt công_nghệ phát_triển",
        ],
    })


# ---------------------------------------------------------------------------
# Quarter ID assignment tests (Req 5.1)
# ---------------------------------------------------------------------------


class TestAssignQuarterId:
    """Test quarter_id assignment for various dates."""

    def test_january_is_q1(self):
        assert assign_quarter_id(pd.Timestamp("2022-01-01")) == "2022Q1"

    def test_march_is_q1(self):
        assert assign_quarter_id(pd.Timestamp("2022-03-31")) == "2022Q1"

    def test_april_is_q2(self):
        assert assign_quarter_id(pd.Timestamp("2022-04-01")) == "2022Q2"

    def test_june_is_q2(self):
        assert assign_quarter_id(pd.Timestamp("2022-06-30")) == "2022Q2"

    def test_july_is_q3(self):
        assert assign_quarter_id(pd.Timestamp("2022-07-01")) == "2022Q3"

    def test_september_is_q3(self):
        assert assign_quarter_id(pd.Timestamp("2022-09-30")) == "2022Q3"

    def test_october_is_q4(self):
        assert assign_quarter_id(pd.Timestamp("2022-10-01")) == "2022Q4"

    def test_december_is_q4(self):
        assert assign_quarter_id(pd.Timestamp("2022-12-31")) == "2022Q4"

    def test_edge_date_feb_28(self):
        """Feb 28 should still be Q1."""
        assert assign_quarter_id(pd.Timestamp("2024-02-28")) == "2024Q1"

    def test_edge_date_feb_29_leap_year(self):
        """Feb 29 in a leap year should be Q1."""
        assert assign_quarter_id(pd.Timestamp("2024-02-29")) == "2024Q1"

    def test_new_years_day(self):
        """Jan 1 should be Q1."""
        assert assign_quarter_id(pd.Timestamp("2023-01-01")) == "2023Q1"

    def test_year_end(self):
        """Dec 31 should be Q4."""
        assert assign_quarter_id(pd.Timestamp("2023-12-31")) == "2023Q4"


class TestAddQuarterId:
    """Test adding quarter_id column to a DataFrame."""

    def test_adds_quarter_id_column(self, sample_prices):
        result = add_quarter_id(sample_prices, date_col="date")
        assert "quarter_id" in result.columns

    def test_correct_quarter_values(self, sample_prices):
        result = add_quarter_id(sample_prices, date_col="date")
        # VNM Jan → Q1
        vnm_jan = result[
            (result["ticker"] == "VNM")
            & (result["date"] == pd.Timestamp("2022-01-10"))
        ]
        assert vnm_jan["quarter_id"].iloc[0] == "2022Q1"

    def test_does_not_modify_original(self, sample_prices):
        original_cols = set(sample_prices.columns)
        add_quarter_id(sample_prices, date_col="date")
        assert set(sample_prices.columns) == original_cols


# ---------------------------------------------------------------------------
# Price aggregation tests (Req 5.3)
# ---------------------------------------------------------------------------


class TestAggregatePrice:
    """Test price aggregation calculations."""

    def test_avg_close(self, sample_prices):
        result = aggregate_prices(sample_prices)
        vnm_q1 = result[
            (result["ticker"] == "VNM") & (result["quarter_id"] == "2022Q1")
        ]
        expected_avg = (100.0 + 110.0 + 120.0) / 3
        assert abs(vnm_q1["avg_close"].iloc[0] - expected_avg) < 1e-6

    def test_avg_volume(self, sample_prices):
        result = aggregate_prices(sample_prices)
        vnm_q1 = result[
            (result["ticker"] == "VNM") & (result["quarter_id"] == "2022Q1")
        ]
        expected_vol = (1000 + 1200 + 1100) / 3
        assert abs(vnm_q1["avg_volume"].iloc[0] - expected_vol) < 1e-6

    def test_return_intra(self, sample_prices):
        result = aggregate_prices(sample_prices)
        vnm_q1 = result[
            (result["ticker"] == "VNM") & (result["quarter_id"] == "2022Q1")
        ]
        # (120 - 100) / 100 = 0.2
        assert abs(vnm_q1["return_intra"].iloc[0] - 0.2) < 1e-6

    def test_trading_days(self, sample_prices):
        result = aggregate_prices(sample_prices)
        vnm_q1 = result[
            (result["ticker"] == "VNM") & (result["quarter_id"] == "2022Q1")
        ]
        assert vnm_q1["trading_days"].iloc[0] == 3

    def test_multiple_tickers(self, sample_prices):
        result = aggregate_prices(sample_prices)
        tickers = result["ticker"].unique()
        assert "VNM" in tickers
        assert "FPT" in tickers

    def test_fpt_q1_return_intra(self, sample_prices):
        result = aggregate_prices(sample_prices)
        fpt_q1 = result[
            (result["ticker"] == "FPT") & (result["quarter_id"] == "2022Q1")
        ]
        # (55 - 50) / 50 = 0.1
        assert abs(fpt_q1["return_intra"].iloc[0] - 0.1) < 1e-6

    def test_output_columns(self, sample_prices):
        result = aggregate_prices(sample_prices)
        expected_cols = {
            "ticker", "quarter_id", "avg_close", "avg_volume",
            "return_intra", "trading_days",
        }
        assert expected_cols.issubset(set(result.columns))


# ---------------------------------------------------------------------------
# News aggregation tests (Req 5.2)
# ---------------------------------------------------------------------------


class TestAggregateNews:
    """Test news aggregation by (ticker, quarter_id)."""

    def test_news_count(self, sample_news):
        result = aggregate_news(sample_news)
        vnm_q1 = result[
            (result["ticker"] == "VNM") & (result["quarter_id"] == "2022Q1")
        ]
        assert vnm_q1["news_count"].iloc[0] == 3

    def test_combined_text_contains_all_tokens(self, sample_news):
        result = aggregate_news(sample_news)
        vnm_q1 = result[
            (result["ticker"] == "VNM") & (result["quarter_id"] == "2022Q1")
        ]
        combined = vnm_q1["combined_text"].iloc[0]
        assert "lợi_nhuận" in combined
        assert "doanh_thu" in combined
        assert "cổ_phiếu" in combined

    def test_single_article_quarter(self, sample_news):
        result = aggregate_news(sample_news)
        fpt_q1 = result[
            (result["ticker"] == "FPT") & (result["quarter_id"] == "2022Q1")
        ]
        assert fpt_q1["news_count"].iloc[0] == 1
        assert "fpt" in fpt_q1["combined_text"].iloc[0]

    def test_output_columns(self, sample_news):
        result = aggregate_news(sample_news)
        expected_cols = {"ticker", "quarter_id", "news_count", "combined_text"}
        assert expected_cols.issubset(set(result.columns))


# ---------------------------------------------------------------------------
# Next quarter derivation tests (Req 5.4)
# ---------------------------------------------------------------------------


class TestNextQuarter:
    """Test next_quarter_id derivation."""

    def test_q1_to_q2(self):
        assert _next_quarter("2022Q1") == "2022Q2"

    def test_q2_to_q3(self):
        assert _next_quarter("2022Q2") == "2022Q3"

    def test_q3_to_q4(self):
        assert _next_quarter("2022Q3") == "2022Q4"

    def test_q4_to_next_year_q1(self):
        assert _next_quarter("2022Q4") == "2023Q1"

    def test_year_boundary(self):
        assert _next_quarter("2024Q4") == "2025Q1"


class TestBuildMasterDataset:
    """Test master dataset construction."""

    def test_inner_merge_only_matching_rows(self, sample_prices, sample_news):
        price_agg = aggregate_prices(sample_prices)
        news_agg = aggregate_news(sample_news)
        master = build_master_dataset(news_agg, price_agg)
        # Only (ticker, quarter) pairs present in BOTH should appear
        for _, row in master.iterrows():
            ticker, qid = row["ticker"], row["quarter_id"]
            assert len(price_agg[
                (price_agg["ticker"] == ticker)
                & (price_agg["quarter_id"] == qid)
            ]) > 0
            assert len(news_agg[
                (news_agg["ticker"] == ticker)
                & (news_agg["quarter_id"] == qid)
            ]) > 0

    def test_has_next_quarter_id(self, sample_prices, sample_news):
        price_agg = aggregate_prices(sample_prices)
        news_agg = aggregate_news(sample_news)
        master = build_master_dataset(news_agg, price_agg)
        assert "next_quarter_id" in master.columns

    def test_next_quarter_id_values(self, sample_prices, sample_news):
        price_agg = aggregate_prices(sample_prices)
        news_agg = aggregate_news(sample_news)
        master = build_master_dataset(news_agg, price_agg)
        vnm_q1 = master[
            (master["ticker"] == "VNM") & (master["quarter_id"] == "2022Q1")
        ]
        if not vnm_q1.empty:
            assert vnm_q1["next_quarter_id"].iloc[0] == "2022Q2"

    def test_next_avg_close_populated(self, sample_prices, sample_news):
        """next_avg_close should be populated when the next quarter exists."""
        price_agg = aggregate_prices(sample_prices)
        news_agg = aggregate_news(sample_news)
        master = build_master_dataset(news_agg, price_agg)
        vnm_q1 = master[
            (master["ticker"] == "VNM") & (master["quarter_id"] == "2022Q1")
        ]
        if not vnm_q1.empty:
            # VNM has Q2 price data, so next_avg_close should be set
            assert pd.notna(vnm_q1["next_avg_close"].iloc[0])
            expected_q2_avg = (130.0 + 125.0) / 2
            assert abs(vnm_q1["next_avg_close"].iloc[0] - expected_q2_avg) < 1e-6

    def test_next_avg_close_nan_when_missing(self, sample_prices, sample_news):
        """next_avg_close should be NaN when the next quarter has no data."""
        price_agg = aggregate_prices(sample_prices)
        news_agg = aggregate_news(sample_news)
        master = build_master_dataset(news_agg, price_agg)
        # FPT only has Q1 data, so next_avg_close for Q1 should be NaN
        # (no Q2 price data for FPT)
        fpt_q1 = master[
            (master["ticker"] == "FPT") & (master["quarter_id"] == "2022Q1")
        ]
        if not fpt_q1.empty:
            assert pd.isna(fpt_q1["next_avg_close"].iloc[0])

    def test_master_has_both_price_and_news_columns(
        self, sample_prices, sample_news
    ):
        price_agg = aggregate_prices(sample_prices)
        news_agg = aggregate_news(sample_news)
        master = build_master_dataset(news_agg, price_agg)
        for col in [
            "avg_close", "avg_volume", "return_intra", "trading_days",
            "news_count", "combined_text",
            "next_quarter_id", "next_avg_close",
        ]:
            assert col in master.columns, f"Missing column: {col}"


# ---------------------------------------------------------------------------
# Heatmap generation test
# ---------------------------------------------------------------------------


class TestCoverageHeatmap:
    """Test heatmap generation."""

    def test_heatmap_file_created(self, sample_prices, sample_news, tmp_path):
        price_agg = aggregate_prices(sample_prices)
        news_agg = aggregate_news(sample_news)
        master = build_master_dataset(news_agg, price_agg)
        output_path = str(tmp_path / "heatmap.png")
        generate_coverage_heatmap(master, output_path=output_path)
        assert os.path.isfile(output_path)
