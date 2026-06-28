"""
Tests for TASK 1: Price_Collector (pipeline/task1_prices.py).

Tests cover:
- VN30 ticker list validation
- Date range resolution
- CSV output format and column presence
- Retry logic with exponential backoff
- Config loading
- Error handling and logging (Req 1.3)
- Summary report output (Req 1.6)
- Data completeness validation (Req 1.7)
"""

import logging
import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from pipeline.task1_prices import (
    VN30_TICKERS,
    BACKOFF_DELAYS,
    MAX_RETRIES,
    _compute_expected_trading_days,
    _fetch_ticker_data,
    _load_config,
    _print_summary,
    _resolve_end_date,
    collect_prices,
    validate_tickers,
)


# ---------------------------------------------------------------------------
# VN30 ticker list validation
# ---------------------------------------------------------------------------

class TestVN30TickerList:
    """Tests for the canonical VN30 ticker list."""

    def test_vn30_has_30_tickers(self):
        """VN30_TICKERS must contain exactly 30 symbols."""
        assert len(VN30_TICKERS) == 30

    def test_vn30_canonical_members(self):
        """VN30_TICKERS must match the canonical list from the spec."""
        expected = sorted([
            "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR",
            "HDB", "HPG", "MBB", "MSN", "MWG", "PLX", "POW", "SAB",
            "SHB", "SSB", "SSI", "STB", "TCB", "TPB", "VCB", "VHM",
            "VIB", "VIC", "VJC", "VNM", "VPB", "VRE",
        ])
        assert sorted(VN30_TICKERS) == expected

    def test_vn30_no_duplicates(self):
        """VN30_TICKERS must not contain duplicates."""
        assert len(VN30_TICKERS) == len(set(VN30_TICKERS))


# ---------------------------------------------------------------------------
# validate_tickers
# ---------------------------------------------------------------------------

class TestValidateTickers:
    """Tests for validate_tickers()."""

    def test_valid_tickers_pass(self):
        """All valid VN30 tickers should be returned unchanged."""
        result = validate_tickers(["VNM", "VCB", "FPT"])
        assert result == ["VNM", "VCB", "FPT"]

    def test_invalid_tickers_filtered(self):
        """Invalid tickers should be filtered out with a warning."""
        result = validate_tickers(["VNM", "INVALID", "FPT"])
        assert result == ["VNM", "FPT"]

    def test_all_invalid_raises(self):
        """All-invalid ticker list should raise ValueError."""
        with pytest.raises(ValueError, match="No valid VN30 tickers"):
            validate_tickers(["INVALID1", "INVALID2"])

    def test_empty_list_raises(self):
        """Empty ticker list should raise ValueError."""
        with pytest.raises(ValueError, match="No valid VN30 tickers"):
            validate_tickers([])

    def test_full_vn30_list(self):
        """Full VN30 list should pass validation unchanged."""
        result = validate_tickers(VN30_TICKERS)
        assert result == VN30_TICKERS


# ---------------------------------------------------------------------------
# Date range resolution
# ---------------------------------------------------------------------------

class TestDateResolution:
    """Tests for _resolve_end_date()."""

    def test_auto_resolves_to_today(self):
        """'auto' should resolve to today's date."""
        result = _resolve_end_date("auto")
        today = datetime.now().strftime("%Y-%m-%d")
        assert result == today

    def test_explicit_date_unchanged(self):
        """Explicit date string should be returned as-is."""
        assert _resolve_end_date("2024-06-30") == "2024-06-30"


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

class TestConfigLoading:
    """Tests for _load_config()."""

    def test_loads_pipeline_config(self):
        """Config should load with expected keys."""
        config = _load_config()
        assert "tickers" in config
        assert "start_date" in config
        assert "end_date" in config
        assert len(config["tickers"]) == 30

    def test_start_date_is_2022(self):
        """start_date should be 2022-01-01 per spec."""
        config = _load_config()
        assert config["start_date"] == "2022-01-01"


# ---------------------------------------------------------------------------
# Retry logic
# ---------------------------------------------------------------------------

class TestRetryLogic:
    """Tests for retry configuration and _fetch_ticker_data retry behavior."""

    def test_retry_constants(self):
        """Retry config should match spec: 3 attempts, delays 1s/2s/4s."""
        assert MAX_RETRIES == 3
        assert BACKOFF_DELAYS == [1, 2, 4]

    @patch("pipeline.task1_prices.time.sleep")
    @patch("pipeline.task1_prices.Quote")
    def test_retries_on_exception(self, mock_quote_cls, mock_sleep):
        """_fetch_ticker_data should retry up to MAX_RETRIES on exceptions."""
        mock_instance = MagicMock()
        mock_instance.history.side_effect = ConnectionError("API down")
        mock_quote_cls.return_value = mock_instance

        result = _fetch_ticker_data("VNM", "2024-01-01", "2024-01-10")

        assert result is None
        assert mock_instance.history.call_count == MAX_RETRIES
        # Should have slept with backoff delays (except after last attempt)
        assert mock_sleep.call_count == MAX_RETRIES - 1
        mock_sleep.assert_any_call(1)
        mock_sleep.assert_any_call(2)

    @patch("pipeline.task1_prices.time.sleep")
    @patch("pipeline.task1_prices.Quote")
    def test_returns_data_on_success(self, mock_quote_cls, mock_sleep):
        """_fetch_ticker_data should return DataFrame on successful fetch."""
        mock_df = pd.DataFrame({
            "time": pd.to_datetime(["2024-01-02", "2024-01-03"]),
            "open": [50.0, 51.0],
            "high": [52.0, 53.0],
            "low": [49.0, 50.0],
            "close": [51.0, 52.0],
            "volume": [1000000, 1100000],
        })
        mock_instance = MagicMock()
        mock_instance.history.return_value = mock_df
        mock_quote_cls.return_value = mock_instance

        result = _fetch_ticker_data("VNM", "2024-01-01", "2024-01-10")

        assert result is not None
        assert len(result) == 2
        assert "date" in result.columns  # 'time' renamed to 'date'
        assert "time" not in result.columns
        assert list(result.columns) == ["date", "open", "high", "low", "close", "volume"]

    @patch("pipeline.task1_prices.time.sleep")
    @patch("pipeline.task1_prices.Quote")
    def test_retries_on_empty_then_succeeds(self, mock_quote_cls, mock_sleep):
        """Should retry on empty DataFrame and succeed on next attempt."""
        good_df = pd.DataFrame({
            "time": pd.to_datetime(["2024-01-02"]),
            "open": [50.0],
            "high": [52.0],
            "low": [49.0],
            "close": [51.0],
            "volume": [1000000],
        })
        mock_instance = MagicMock()
        mock_instance.history.side_effect = [pd.DataFrame(), good_df]
        mock_quote_cls.return_value = mock_instance

        result = _fetch_ticker_data("VNM", "2024-01-01", "2024-01-10")

        assert result is not None
        assert len(result) == 1


# ---------------------------------------------------------------------------
# CSV output format
# ---------------------------------------------------------------------------

class TestCSVOutput:
    """Tests for CSV output format and column presence."""

    @patch("pipeline.task1_prices._fetch_ticker_data")
    def test_collect_prices_output_columns(self, mock_fetch, tmp_path):
        """Consolidated output must have [ticker, date, open, high, low, close, volume]."""
        mock_df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-02", "2024-01-03"]),
            "open": [50.0, 51.0],
            "high": [52.0, 53.0],
            "low": [49.0, 50.0],
            "close": [51.0, 52.0],
            "volume": [1000000, 1100000],
        })
        mock_fetch.return_value = mock_df

        output_dir = str(tmp_path / "prices")
        result = collect_prices(
            tickers=["VNM"],
            start_date="2024-01-01",
            end_date="2024-01-10",
            output_dir=output_dir,
        )

        expected_cols = ["ticker", "date", "open", "high", "low", "close", "volume"]
        assert list(result.columns) == expected_cols

    @patch("pipeline.task1_prices._fetch_ticker_data")
    def test_individual_ticker_csv_saved(self, mock_fetch, tmp_path):
        """Individual ticker CSV files should be saved to output_dir."""
        mock_df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-02"]),
            "open": [50.0],
            "high": [52.0],
            "low": [49.0],
            "close": [51.0],
            "volume": [1000000],
        })
        mock_fetch.return_value = mock_df

        output_dir = str(tmp_path / "prices")
        collect_prices(
            tickers=["VNM", "FPT"],
            start_date="2024-01-01",
            end_date="2024-01-10",
            output_dir=output_dir,
        )

        assert os.path.isfile(os.path.join(output_dir, "VNM.csv"))
        assert os.path.isfile(os.path.join(output_dir, "FPT.csv"))
        assert os.path.isfile(os.path.join(output_dir, "all_vn30_prices.csv"))

    @patch("pipeline.task1_prices._fetch_ticker_data")
    def test_consolidated_csv_has_ticker_column(self, mock_fetch, tmp_path):
        """Consolidated CSV should include a ticker column."""
        mock_df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-02"]),
            "open": [50.0],
            "high": [52.0],
            "low": [49.0],
            "close": [51.0],
            "volume": [1000000],
        })
        mock_fetch.return_value = mock_df

        output_dir = str(tmp_path / "prices")
        collect_prices(
            tickers=["VNM", "FPT"],
            start_date="2024-01-01",
            end_date="2024-01-10",
            output_dir=output_dir,
        )

        consolidated = pd.read_csv(os.path.join(output_dir, "all_vn30_prices.csv"))
        assert "ticker" in consolidated.columns
        assert set(consolidated["ticker"].unique()) == {"VNM", "FPT"}

    @patch("pipeline.task1_prices._fetch_ticker_data")
    def test_all_tickers_fail_raises(self, mock_fetch, tmp_path):
        """Should raise ValueError when all tickers fail."""
        mock_fetch.return_value = None

        output_dir = str(tmp_path / "prices")
        with pytest.raises(ValueError, match="failed for ALL"):
            collect_prices(
                tickers=["VNM"],
                start_date="2024-01-01",
                end_date="2024-01-10",
                output_dir=output_dir,
            )

    @patch("pipeline.task1_prices._fetch_ticker_data")
    def test_partial_failure_continues(self, mock_fetch, tmp_path):
        """Should continue collecting when some tickers fail."""
        good_df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-02"]),
            "open": [50.0],
            "high": [52.0],
            "low": [49.0],
            "close": [51.0],
            "volume": [1000000],
        })
        # VNM succeeds, FPT fails
        mock_fetch.side_effect = [good_df, None]

        output_dir = str(tmp_path / "prices")
        result = collect_prices(
            tickers=["VNM", "FPT"],
            start_date="2024-01-01",
            end_date="2024-01-10",
            output_dir=output_dir,
        )

        assert len(result) == 1
        assert result["ticker"].iloc[0] == "VNM"


# ---------------------------------------------------------------------------
# Error handling and logging (Req 1.3)
# ---------------------------------------------------------------------------

class TestErrorHandling:
    """Tests for error handling: log errors with ticker name and timestamp,
    continue with remaining tickers (Req 1.3)."""

    @patch("pipeline.task1_prices.time.sleep")
    @patch("pipeline.task1_prices.Quote")
    def test_error_log_includes_ticker_name(self, mock_quote_cls, mock_sleep, caplog):
        """Error log message should include the ticker name."""
        mock_instance = MagicMock()
        mock_instance.history.side_effect = ConnectionError("API down")
        mock_quote_cls.return_value = mock_instance

        with caplog.at_level(logging.WARNING, logger="TASK_1"):
            _fetch_ticker_data("VNM", "2024-01-01", "2024-01-10")

        # Check that at least one log message mentions the ticker
        ticker_mentioned = any("VNM" in record.message for record in caplog.records)
        assert ticker_mentioned, "Error log should include ticker name 'VNM'"

    @patch("pipeline.task1_prices.time.sleep")
    @patch("pipeline.task1_prices.Quote")
    def test_error_log_includes_timestamp(self, mock_quote_cls, mock_sleep, caplog):
        """Error log message should include an explicit timestamp."""
        mock_instance = MagicMock()
        mock_instance.history.side_effect = ConnectionError("API down")
        mock_quote_cls.return_value = mock_instance

        with caplog.at_level(logging.WARNING, logger="TASK_1"):
            _fetch_ticker_data("VNM", "2024-01-01", "2024-01-10")

        # Check that error/warning messages contain a timestamp pattern [YYYY-MM-DD HH:MM:SS]
        import re
        timestamp_pattern = re.compile(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]")
        has_timestamp = any(
            timestamp_pattern.search(record.message)
            for record in caplog.records
        )
        assert has_timestamp, "Error log should include explicit timestamp"

    @patch("pipeline.task1_prices._fetch_ticker_data")
    def test_continues_after_ticker_failure(self, mock_fetch, tmp_path):
        """Pipeline should continue processing remaining tickers after one fails (Req 1.3)."""
        good_df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-02", "2024-01-03"]),
            "open": [50.0, 51.0],
            "high": [52.0, 53.0],
            "low": [49.0, 50.0],
            "close": [51.0, 52.0],
            "volume": [1000000, 1100000],
        })
        # First ticker fails, second and third succeed
        mock_fetch.side_effect = [None, good_df, good_df]

        output_dir = str(tmp_path / "prices")
        result = collect_prices(
            tickers=["VNM", "VCB", "FPT"],
            start_date="2024-01-01",
            end_date="2024-01-10",
            output_dir=output_dir,
        )

        # Should have data for VCB and FPT despite VNM failure
        assert set(result["ticker"].unique()) == {"VCB", "FPT"}
        assert len(result) == 4  # 2 rows each for VCB and FPT

    @patch("pipeline.task1_prices._fetch_ticker_data")
    def test_failed_ticker_logged_in_summary(self, mock_fetch, tmp_path, caplog):
        """Failed tickers should appear in the summary report."""
        good_df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-02"]),
            "open": [50.0],
            "high": [52.0],
            "low": [49.0],
            "close": [51.0],
            "volume": [1000000],
        })
        mock_fetch.side_effect = [good_df, None]

        output_dir = str(tmp_path / "prices")
        with caplog.at_level(logging.WARNING, logger="TASK_1"):
            collect_prices(
                tickers=["VNM", "FPT"],
                start_date="2024-01-01",
                end_date="2024-01-10",
                output_dir=output_dir,
            )

        # Check that FPT appears in a "Failed tickers" warning
        failed_msg = any(
            "Failed tickers" in record.message and "FPT" in record.message
            for record in caplog.records
        )
        assert failed_msg, "Summary should warn about failed ticker FPT"


# ---------------------------------------------------------------------------
# Expected trading days computation
# ---------------------------------------------------------------------------

class TestExpectedTradingDays:
    """Tests for _compute_expected_trading_days()."""

    def test_known_date_range(self):
        """Business days for a known week should be 5 (Mon-Fri)."""
        # 2024-01-01 (Mon) to 2024-01-05 (Fri) = 5 business days
        result = _compute_expected_trading_days("2024-01-01", "2024-01-05")
        assert result == 5

    def test_weekend_excluded(self):
        """Weekends should not count as trading days."""
        # 2024-01-06 (Sat) to 2024-01-07 (Sun) = 0 business days
        result = _compute_expected_trading_days("2024-01-06", "2024-01-07")
        assert result == 0

    def test_full_year_reasonable(self):
        """A full year should have ~250-262 business days."""
        result = _compute_expected_trading_days("2024-01-01", "2024-12-31")
        assert 250 <= result <= 262


# ---------------------------------------------------------------------------
# Summary report (Req 1.6) and data completeness (Req 1.7)
# ---------------------------------------------------------------------------

class TestSummaryReport:
    """Tests for _print_summary() — Req 1.6 and Req 1.7."""

    def test_summary_reports_per_ticker_stats(self, caplog):
        """Summary should report trading days, earliest date, latest date per ticker (Req 1.6)."""
        df = pd.DataFrame({
            "ticker": ["VNM"] * 3 + ["FPT"] * 2,
            "date": pd.to_datetime([
                "2024-01-02", "2024-01-03", "2024-01-04",
                "2024-01-02", "2024-01-03",
            ]),
            "open": [50.0] * 5,
            "high": [52.0] * 5,
            "low": [49.0] * 5,
            "close": [51.0] * 5,
            "volume": [1000000] * 5,
        })

        with caplog.at_level(logging.INFO, logger="TASK_1"):
            _print_summary(df, [], "2024-01-02", "2024-01-04")

        messages = " ".join(record.message for record in caplog.records)
        # Should mention both tickers
        assert "FPT" in messages
        assert "VNM" in messages
        # Should mention dates
        assert "2024-01-02" in messages
        assert "2024-01-04" in messages

    def test_summary_warns_missing_trading_days(self, caplog):
        """Summary should warn when a ticker has >5% missing trading days (Req 1.7)."""
        # Create data where FPT has significantly fewer days than expected
        # Date range 2024-01-02 to 2024-03-29 has ~63 business days
        # VNM has 60 days, FPT has only 30 days (~52% missing)
        vnm_dates = pd.bdate_range("2024-01-02", periods=60)
        fpt_dates = pd.bdate_range("2024-01-02", periods=30)

        vnm_df = pd.DataFrame({
            "ticker": "VNM",
            "date": vnm_dates,
            "open": 50.0, "high": 52.0, "low": 49.0, "close": 51.0,
            "volume": 1000000,
        })
        fpt_df = pd.DataFrame({
            "ticker": "FPT",
            "date": fpt_dates,
            "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0,
            "volume": 2000000,
        })
        df = pd.concat([vnm_df, fpt_df], ignore_index=True)

        with caplog.at_level(logging.WARNING, logger="TASK_1"):
            _print_summary(df, [], "2024-01-02", "2024-03-29")

        # Should warn about FPT having fewer trading days
        warning_msgs = [r.message for r in caplog.records if r.levelno >= logging.WARNING]
        fpt_warning = any("FPT" in msg and "fewer trading days" in msg for msg in warning_msgs)
        assert fpt_warning, "Should warn about FPT having >5% missing trading days"

    def test_summary_no_warning_when_complete(self, caplog):
        """No missing-data warning when all tickers have sufficient data (Req 1.7)."""
        # Both tickers have the same number of days, matching expected calendar
        dates = pd.bdate_range("2024-01-02", "2024-01-05")  # 4 business days

        vnm_df = pd.DataFrame({
            "ticker": "VNM",
            "date": dates,
            "open": 50.0, "high": 52.0, "low": 49.0, "close": 51.0,
            "volume": 1000000,
        })
        fpt_df = pd.DataFrame({
            "ticker": "FPT",
            "date": dates,
            "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0,
            "volume": 2000000,
        })
        df = pd.concat([vnm_df, fpt_df], ignore_index=True)

        with caplog.at_level(logging.WARNING, logger="TASK_1"):
            _print_summary(df, [], "2024-01-02", "2024-01-05")

        warning_msgs = [r.message for r in caplog.records if r.levelno >= logging.WARNING]
        missing_warnings = [m for m in warning_msgs if "fewer trading days" in m]
        assert len(missing_warnings) == 0, "No missing-data warnings expected"

    def test_summary_reports_failed_tickers(self, caplog):
        """Summary should list failed tickers when present."""
        df = pd.DataFrame({
            "ticker": ["VNM"],
            "date": pd.to_datetime(["2024-01-02"]),
            "open": [50.0], "high": [52.0], "low": [49.0],
            "close": [51.0], "volume": [1000000],
        })

        with caplog.at_level(logging.WARNING, logger="TASK_1"):
            _print_summary(df, ["FPT", "VCB"], "2024-01-02", "2024-01-02")

        warning_msgs = " ".join(r.message for r in caplog.records if r.levelno >= logging.WARNING)
        assert "FPT" in warning_msgs
        assert "VCB" in warning_msgs

    def test_summary_reports_expected_trading_days(self, caplog):
        """Summary should report the expected trading days from business-day calendar."""
        df = pd.DataFrame({
            "ticker": ["VNM"],
            "date": pd.to_datetime(["2024-01-02"]),
            "open": [50.0], "high": [52.0], "low": [49.0],
            "close": [51.0], "volume": [1000000],
        })

        with caplog.at_level(logging.INFO, logger="TASK_1"):
            _print_summary(df, [], "2024-01-02", "2024-01-05")

        messages = " ".join(record.message for record in caplog.records)
        assert "Expected trading days" in messages
