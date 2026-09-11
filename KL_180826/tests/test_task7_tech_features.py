"""
Unit tests for TASK 7: Tech_Feature_Extractor module.

Tests cover:
- RSI computation bounds (0-100) with period=14 (Req 7.1)
- MACD computation with parameters (12,26,9) (Req 7.1)
- Bollinger Bands ordering (upper > middle > lower) with parameters (20,2) (Req 7.1)
- Quarterly aggregation calculations per named group (Req 7.2)
- Lag feature generation (Req 7.2, 7.3)
- Correlation check warnings (Req 7.5)
"""

import math

import numpy as np
import pandas as pd
import pytest

from pipeline.task7_tech_features import (
    compute_daily_indicators,
    aggregate_quarter_features,
    compute_quarterly_features,
    check_correlations,
    _find_column,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_daily_prices(
    ticker: str = "VNM",
    n_days: int = 120,
    start_date: str = "2022-01-03",
    base_price: float = 100.0,
) -> pd.DataFrame:
    """Generate synthetic daily OHLCV data for testing.

    Creates a price series with realistic-looking random walk behaviour
    so that technical indicators produce meaningful values.
    """
    rng = np.random.RandomState(42)
    dates = pd.bdate_range(start=start_date, periods=n_days)
    returns = rng.normal(0.001, 0.02, size=n_days)
    close = base_price * np.cumprod(1 + returns)

    df = pd.DataFrame({
        "ticker": ticker,
        "date": dates,
        "open": close * (1 + rng.uniform(-0.01, 0.01, n_days)),
        "high": close * (1 + rng.uniform(0.005, 0.02, n_days)),
        "low": close * (1 - rng.uniform(0.005, 0.02, n_days)),
        "close": close,
        "volume": rng.randint(500_000, 5_000_000, size=n_days),
    })
    return df


@pytest.fixture
def daily_prices_vnm():
    """120 business days of synthetic VNM prices starting 2022-01-03."""
    return _make_daily_prices("VNM", n_days=120)


@pytest.fixture
def daily_prices_multi():
    """Multi-ticker daily prices spanning multiple quarters."""
    vnm = _make_daily_prices("VNM", n_days=250, start_date="2022-01-03")
    fpt = _make_daily_prices("FPT", n_days=250, start_date="2022-01-03",
                             base_price=80.0)
    return pd.concat([vnm, fpt], ignore_index=True)


# ---------------------------------------------------------------------------
# Daily indicator tests (Req 7.1)
# ---------------------------------------------------------------------------


class TestComputeDailyIndicators:
    """Test daily indicator computation using pandas-ta."""

    def test_rsi_bounds(self, daily_prices_vnm):
        """RSI values must be between 0 and 100 (Req 7.1)."""
        result = compute_daily_indicators(daily_prices_vnm)
        rsi = result["RSI_14"].dropna()
        assert len(rsi) > 0, "RSI should have non-NaN values"
        assert rsi.min() >= 0, f"RSI min {rsi.min()} < 0"
        assert rsi.max() <= 100, f"RSI max {rsi.max()} > 100"

    def test_macd_columns_present(self, daily_prices_vnm):
        """MACD(12,26,9) should produce MACD line, signal, and histogram."""
        result = compute_daily_indicators(daily_prices_vnm)
        macd_cols = [c for c in result.columns if c.startswith("MACD")]
        assert len(macd_cols) >= 3, (
            f"Expected at least 3 MACD columns, got {macd_cols}"
        )

    def test_macd_histogram_is_difference(self, daily_prices_vnm):
        """MACD histogram = MACD line - signal line."""
        result = compute_daily_indicators(daily_prices_vnm)
        macd_col = _find_column(result, "MACD_")
        signal_col = _find_column(result, "MACDs_")
        hist_col = _find_column(result, "MACDh_")
        assert macd_col and signal_col and hist_col

        valid = result[[macd_col, signal_col, hist_col]].dropna()
        diff = valid[macd_col] - valid[signal_col]
        np.testing.assert_allclose(
            valid[hist_col].values, diff.values, atol=1e-6,
            err_msg="MACD histogram should equal MACD - signal"
        )

    def test_bollinger_bands_ordering(self, daily_prices_vnm):
        """Bollinger Bands: upper > middle > lower (Req 7.1)."""
        result = compute_daily_indicators(daily_prices_vnm)
        bbu_col = _find_column(result, "BBU_")
        bbm_col = _find_column(result, "BBM_")
        bbl_col = _find_column(result, "BBL_")
        assert bbu_col and bbm_col and bbl_col

        valid = result[[bbu_col, bbm_col, bbl_col]].dropna()
        assert len(valid) > 0, "BB should have non-NaN values"
        assert (valid[bbu_col] >= valid[bbm_col]).all(), "BBU should >= BBM"
        assert (valid[bbm_col] >= valid[bbl_col]).all(), "BBM should >= BBL"

    def test_sma_columns_present(self, daily_prices_vnm):
        """SMA(20) and SMA(50) columns should be present."""
        result = compute_daily_indicators(daily_prices_vnm)
        assert "SMA_20" in result.columns
        assert "SMA_50" in result.columns

    def test_ema_column_present(self, daily_prices_vnm):
        """EMA(20) column should be present."""
        result = compute_daily_indicators(daily_prices_vnm)
        assert "EMA_20" in result.columns

    def test_daily_return_computed(self, daily_prices_vnm):
        """daily_return column should be present and first value NaN."""
        result = compute_daily_indicators(daily_prices_vnm)
        assert "daily_return" in result.columns
        assert pd.isna(result["daily_return"].iloc[0])
        # Second value should be a valid return
        expected = (
            result["close"].iloc[1] - result["close"].iloc[0]
        ) / result["close"].iloc[0]
        assert abs(result["daily_return"].iloc[1] - expected) < 1e-9


# ---------------------------------------------------------------------------
# Quarterly aggregation tests (Req 7.2)
# ---------------------------------------------------------------------------


class TestAggregateQuarterFeatures:
    """Test quarterly feature aggregation per named group."""

    def test_returns_group(self, daily_prices_vnm):
        """Returns group: return_q, return_mean_daily, return_std_daily."""
        result = compute_daily_indicators(daily_prices_vnm)
        # Take first ~60 days as a quarter
        q_data = result.iloc[:60]
        feats = aggregate_quarter_features(q_data)

        assert "return_q" in feats
        assert "return_mean_daily" in feats
        assert "return_std_daily" in feats

        # return_q should be (last - first) / first
        expected_return = (
            (q_data["close"].iloc[-1] - q_data["close"].iloc[0])
            / q_data["close"].iloc[0]
        )
        assert abs(feats["return_q"] - expected_return) < 1e-9

    def test_volatility_group(self, daily_prices_vnm):
        """Volatility group: volatility_q, price_range_q."""
        result = compute_daily_indicators(daily_prices_vnm)
        q_data = result.iloc[:60]
        feats = aggregate_quarter_features(q_data)

        assert "volatility_q" in feats
        assert "price_range_q" in feats

        # volatility_q = return_std_daily * sqrt(trading_days)
        expected_vol = feats["return_std_daily"] * math.sqrt(60)
        assert abs(feats["volatility_q"] - expected_vol) < 1e-9

    def test_liquidity_group(self, daily_prices_vnm):
        """Liquidity group: volume_mean_q present."""
        result = compute_daily_indicators(daily_prices_vnm)
        q_data = result.iloc[:60]
        feats = aggregate_quarter_features(q_data)

        assert "volume_mean_q" in feats
        assert feats["volume_mean_q"] > 0

    def test_trend_group(self, daily_prices_vnm):
        """Trend group: sma20_end, ema20_end, price_vs_sma20."""
        result = compute_daily_indicators(daily_prices_vnm)
        q_data = result.iloc[:60]
        feats = aggregate_quarter_features(q_data)

        assert "sma20_end" in feats
        assert "ema20_end" in feats
        assert "price_vs_sma20" in feats

    def test_indicator_group(self, daily_prices_vnm):
        """Indicator group: rsi_mean_q, rsi_end_q, macd_hist_mean_q, bb_position_q."""
        result = compute_daily_indicators(daily_prices_vnm)
        q_data = result.iloc[:60]
        feats = aggregate_quarter_features(q_data)

        assert "rsi_mean_q" in feats
        assert "rsi_end_q" in feats
        assert "macd_hist_mean_q" in feats
        assert "bb_position_q" in feats

    def test_rsi_mean_within_bounds(self, daily_prices_vnm):
        """rsi_mean_q should be between 0 and 100."""
        result = compute_daily_indicators(daily_prices_vnm)
        q_data = result.iloc[:60]
        feats = aggregate_quarter_features(q_data)

        if pd.notna(feats["rsi_mean_q"]):
            assert 0 <= feats["rsi_mean_q"] <= 100

    def test_bb_position_reasonable(self, daily_prices_vnm):
        """bb_position_q should typically be between 0 and 1."""
        result = compute_daily_indicators(daily_prices_vnm)
        q_data = result.iloc[:60]
        feats = aggregate_quarter_features(q_data)

        if pd.notna(feats["bb_position_q"]):
            # Mean BB position should be roughly around 0.5
            assert -0.5 <= feats["bb_position_q"] <= 1.5

    def test_momentum_group_nan_for_first_quarter(self, daily_prices_vnm):
        """Momentum group: return_prev_q and return_2q_ago should be NaN
        when no previous quarter data is provided."""
        result = compute_daily_indicators(daily_prices_vnm)
        q_data = result.iloc[:60]
        feats = aggregate_quarter_features(q_data)

        assert feats["return_prev_q"] is None
        assert feats["return_2q_ago"] is None

    def test_empty_dataframe(self):
        """aggregate_quarter_features should return empty dict for empty input."""
        empty_df = pd.DataFrame()
        feats = aggregate_quarter_features(empty_df)
        assert feats == {}


# ---------------------------------------------------------------------------
# Full quarterly pipeline tests (Req 7.2, 7.3)
# ---------------------------------------------------------------------------


class TestComputeQuarterlyFeatures:
    """Test the full compute_quarterly_features pipeline."""

    def test_output_columns(self, daily_prices_multi):
        """Output should have ticker, quarter_id, and all feature columns."""
        result = compute_quarterly_features(daily_prices_multi)
        assert "ticker" in result.columns
        assert "quarter_id" in result.columns

        expected_features = [
            "return_q", "return_mean_daily", "return_std_daily",
            "volatility_q", "price_range_q",
            "volume_mean_q", "volume_change_q",
            "sma20_end", "ema20_end", "price_vs_sma20",
            "rsi_mean_q", "rsi_end_q", "macd_hist_mean_q", "bb_position_q",
            "return_prev_q", "return_2q_ago",
        ]
        for col in expected_features:
            assert col in result.columns, f"Missing feature column: {col}"

    def test_multiple_tickers(self, daily_prices_multi):
        """Should produce features for both VNM and FPT."""
        result = compute_quarterly_features(daily_prices_multi)
        tickers = result["ticker"].unique()
        assert "VNM" in tickers
        assert "FPT" in tickers

    def test_lag_features_nan_first_quarters(self, daily_prices_multi):
        """Lag features should be NaN for the first 1-2 quarters (Req 7.3)."""
        result = compute_quarterly_features(daily_prices_multi)

        for ticker in result["ticker"].unique():
            ticker_data = result[result["ticker"] == ticker].sort_values(
                "quarter_id"
            )
            # First quarter: return_prev_q should be NaN
            assert pd.isna(ticker_data["return_prev_q"].iloc[0]), (
                f"{ticker} first quarter return_prev_q should be NaN"
            )
            # First two quarters: return_2q_ago should be NaN
            if len(ticker_data) >= 2:
                assert pd.isna(ticker_data["return_2q_ago"].iloc[0]), (
                    f"{ticker} first quarter return_2q_ago should be NaN"
                )
                assert pd.isna(ticker_data["return_2q_ago"].iloc[1]), (
                    f"{ticker} second quarter return_2q_ago should be NaN"
                )

    def test_volume_change_q_first_quarter_nan(self, daily_prices_multi):
        """volume_change_q should be NaN for the first quarter of each ticker."""
        result = compute_quarterly_features(daily_prices_multi)

        for ticker in result["ticker"].unique():
            ticker_data = result[result["ticker"] == ticker].sort_values(
                "quarter_id"
            )
            assert pd.isna(ticker_data["volume_change_q"].iloc[0])

    def test_quarter_id_format(self, daily_prices_multi):
        """quarter_id should follow YYYYQN format."""
        result = compute_quarterly_features(daily_prices_multi)
        for qid in result["quarter_id"]:
            assert len(qid) == 6, f"quarter_id '{qid}' should be 6 chars"
            assert qid[4] == "Q", f"quarter_id '{qid}' should have Q at pos 4"
            assert qid[5] in "1234", f"quarter_id '{qid}' quarter must be 1-4"


# ---------------------------------------------------------------------------
# Correlation check tests (Req 7.5)
# ---------------------------------------------------------------------------


class TestCheckCorrelations:
    """Test correlation matrix computation and warnings."""

    def test_returns_correlation_matrix(self, daily_prices_multi):
        """check_correlations should return a correlation matrix."""
        features = compute_quarterly_features(daily_prices_multi)
        corr = check_correlations(features)
        assert isinstance(corr, pd.DataFrame)
        assert corr.shape[0] == corr.shape[1]  # Square matrix

    def test_warns_high_correlation(self, capsys):
        """Should print warning for feature pairs with |corr| > 0.95."""
        # Create data with perfectly correlated features
        df = pd.DataFrame({
            "ticker": ["A"] * 10,
            "quarter_id": [f"2022Q{i % 4 + 1}" for i in range(10)],
            "feat_a": range(10),
            "feat_b": range(10),  # Perfectly correlated with feat_a
            "feat_c": list(range(5)) + list(range(5, 0, -1)),
        })
        check_correlations(df, threshold=0.95)
        captured = capsys.readouterr()
        assert "feat_a" in captured.out and "feat_b" in captured.out

    def test_no_warning_low_correlation(self, capsys):
        """Should not warn for uncorrelated features."""
        rng = np.random.RandomState(123)
        df = pd.DataFrame({
            "ticker": ["A"] * 50,
            "quarter_id": [f"2022Q{i % 4 + 1}" for i in range(50)],
            "feat_a": rng.randn(50),
            "feat_b": rng.randn(50),
        })
        check_correlations(df, threshold=0.95)
        captured = capsys.readouterr()
        assert "High correlation" not in captured.out


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------


class TestFindColumn:
    """Test the _find_column helper."""

    def test_finds_matching_column(self):
        df = pd.DataFrame({"MACDh_12_26_9": [1], "other": [2]})
        assert _find_column(df, "MACDh_") == "MACDh_12_26_9"

    def test_returns_none_when_no_match(self):
        df = pd.DataFrame({"other": [1]})
        assert _find_column(df, "MACDh_") is None
