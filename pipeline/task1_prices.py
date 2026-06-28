"""
TASK 1: Price_Collector
Collect daily OHLCV data for VN30 tickers using vnstock.

Uses the vnstock VCI Quote API to retrieve daily price data for all 30 VN30
constituents. Implements retry logic with exponential backoff, validates
tickers against the canonical VN30 list, and saves both individual and
consolidated CSV files.

Includes error handling (Req 1.3), summary reporting (Req 1.6), and data
completeness validation against expected business-day calendar (Req 1.7).
"""

import os
import time
from datetime import datetime
from typing import List, Optional

import numpy as np
import pandas as pd
import yaml
from vnstock.explorer.vci.quote import Quote

from pipeline.logging_config import setup_logger

# Canonical VN30 ticker list
VN30_TICKERS = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE",
]

# Retry configuration
MAX_RETRIES = 3
BACKOFF_DELAYS = [1, 2, 4]  # seconds

logger = setup_logger("TASK_1")


def _load_config(config_path: str = "config/pipeline_config.yaml") -> dict:
    """Load pipeline configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _resolve_end_date(end_date: str) -> str:
    """Resolve 'auto' end_date to current date string YYYY-MM-DD."""
    if end_date == "auto":
        return datetime.now().strftime("%Y-%m-%d")
    return end_date


def validate_tickers(tickers: List[str]) -> List[str]:
    """
    Validate tickers against the canonical VN30 list.

    Args:
        tickers: List of ticker symbols to validate.

    Returns:
        List of valid VN30 tickers.

    Raises:
        ValueError: If no valid tickers are found.
    """
    valid = [t for t in tickers if t in VN30_TICKERS]
    invalid = [t for t in tickers if t not in VN30_TICKERS]

    if invalid:
        logger.warning(
            "Invalid tickers (not in VN30): %s — these will be skipped.",
            ", ".join(invalid),
        )

    if not valid:
        raise ValueError(
            "No valid VN30 tickers provided. "
            f"Expected tickers from: {VN30_TICKERS}"
        )

    logger.info("Validated %d/%d tickers against VN30 list.", len(valid), len(tickers))
    return valid


def _fetch_ticker_data(
    ticker: str,
    start_date: str,
    end_date: str,
) -> Optional[pd.DataFrame]:
    """
    Fetch OHLCV data for a single ticker with retry logic.

    Uses exponential backoff: delays of 1s, 2s, 4s across 3 attempts.

    Args:
        ticker: Stock ticker symbol.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        DataFrame with columns [date, open, high, low, close, volume]
        or None if all retries fail.
    """
    for attempt in range(MAX_RETRIES):
        try:
            quote = Quote(ticker)
            df = quote.history(start=start_date, end=end_date, interval="1D")

            if df is None or df.empty:
                logger.warning(
                    "Empty data returned for %s (attempt %d/%d).",
                    ticker, attempt + 1, MAX_RETRIES,
                )
                if attempt < MAX_RETRIES - 1:
                    delay = BACKOFF_DELAYS[attempt]
                    logger.info("Retrying in %ds...", delay)
                    time.sleep(delay)
                continue

            # Rename 'time' column to 'date' for consistency
            if "time" in df.columns:
                df = df.rename(columns={"time": "date"})

            # Ensure date column is datetime type
            df["date"] = pd.to_datetime(df["date"])

            # Keep only required OHLCV columns
            required_cols = ["date", "open", "high", "low", "close", "volume"]
            available = [c for c in required_cols if c in df.columns]
            df = df[available].copy()

            # Sort by date ascending
            df = df.sort_values("date").reset_index(drop=True)

            logger.info(
                "Fetched %d rows for %s (%s to %s).",
                len(df), ticker,
                df["date"].min().strftime("%Y-%m-%d"),
                df["date"].max().strftime("%Y-%m-%d"),
            )
            return df

        except Exception as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.warning(
                "[%s] Error fetching %s (attempt %d/%d): %s",
                timestamp, ticker, attempt + 1, MAX_RETRIES, str(e),
            )
            if attempt < MAX_RETRIES - 1:
                delay = BACKOFF_DELAYS[attempt]
                logger.info("Retrying in %ds...", delay)
                time.sleep(delay)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.error(
        "[%s] Failed to fetch data for %s after %d attempts.",
        timestamp, ticker, MAX_RETRIES,
    )
    return None


def collect_prices(
    tickers: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    config_path: str = "config/pipeline_config.yaml",
    output_dir: str = "data/prices",
) -> pd.DataFrame:
    """
    Collect OHLCV data for specified VN30 tickers.

    Retrieves daily price data from vnstock for each ticker, saves individual
    CSV files per ticker and a consolidated file with all tickers.

    Args:
        tickers: List of ticker symbols. Defaults to config file tickers.
        start_date: Start date (YYYY-MM-DD). Defaults to config value.
        end_date: End date (YYYY-MM-DD) or "auto". Defaults to config value.
        config_path: Path to pipeline_config.yaml.
        output_dir: Directory to save CSV files.

    Returns:
        DataFrame with columns [ticker, date, open, high, low, close, volume].

    Raises:
        ValueError: If vnstock API fails for ALL tickers.
    """
    # Load config
    config = _load_config(config_path)

    if tickers is None:
        tickers = config.get("tickers", VN30_TICKERS)
    if start_date is None:
        start_date = config.get("start_date", "2022-01-01")
    if end_date is None:
        end_date = config.get("end_date", "auto")

    end_date = _resolve_end_date(end_date)

    logger.info("=" * 60)
    logger.info("TASK 1: Price Collection Started")
    logger.info("Tickers: %d | Date range: %s to %s", len(tickers), start_date, end_date)
    logger.info("=" * 60)

    # Validate tickers against canonical VN30 list
    valid_tickers = validate_tickers(tickers)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    all_frames = []
    failed_tickers = []
    success_count = 0

    for i, ticker in enumerate(valid_tickers, 1):
        logger.info("Processing %s (%d/%d)...", ticker, i, len(valid_tickers))

        df = _fetch_ticker_data(ticker, start_date, end_date)

        if df is not None and not df.empty:
            # Save individual ticker CSV
            ticker_path = os.path.join(output_dir, f"{ticker}.csv")
            df.to_csv(ticker_path, index=False)
            logger.info("Saved %s → %s (%d rows)", ticker, ticker_path, len(df))

            # Add ticker column for consolidated file
            df_with_ticker = df.copy()
            df_with_ticker.insert(0, "ticker", ticker)
            all_frames.append(df_with_ticker)
            success_count += 1
        else:
            failed_tickers.append(ticker)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.error(
                "[%s] FAILED: %s — no data collected. "
                "Continuing with remaining tickers.",
                timestamp, ticker,
            )

        # Small delay between tickers to be respectful to the API
        if i < len(valid_tickers):
            time.sleep(0.5)

    # Check if we got any data at all
    if not all_frames:
        raise ValueError(
            f"vnstock API failed for ALL {len(valid_tickers)} tickers. "
            "No price data collected."
        )

    # Consolidate all ticker data
    consolidated = pd.concat(all_frames, ignore_index=True)
    consolidated = consolidated.sort_values(["ticker", "date"]).reset_index(drop=True)

    # Save consolidated file
    consolidated_path = os.path.join(output_dir, "all_vn30_prices.csv")
    consolidated.to_csv(consolidated_path, index=False)
    logger.info(
        "Saved consolidated file → %s (%d rows, %d tickers)",
        consolidated_path, len(consolidated), success_count,
    )

    # Print summary report
    _print_summary(consolidated, failed_tickers, start_date, end_date)

    return consolidated


def _compute_expected_trading_days(start_date: str, end_date: str) -> int:
    """
    Compute the expected number of trading days between two dates.

    Uses the pandas business-day calendar (Mon-Fri) as a proxy for the
    Vietnamese stock exchange calendar. The actual HOSE calendar may differ
    slightly due to Vietnamese public holidays, but business days provide a
    reasonable upper-bound estimate.

    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        Number of business days in the date range (inclusive).
    """
    bdays = pd.bdate_range(start=start_date, end=end_date)
    return len(bdays)


def _print_summary(
    df: pd.DataFrame,
    failed_tickers: List[str],
    start_date: str,
    end_date: str,
) -> None:
    """
    Print a summary report of the collected price data.

    Reports trading days, date range per ticker (Req 1.6), and warns about
    missing data or failed tickers. Validates data completeness against the
    expected business-day calendar (Req 1.7).
    """
    logger.info("=" * 60)
    logger.info("PRICE COLLECTION SUMMARY")
    logger.info("=" * 60)

    tickers_in_data = sorted(df["ticker"].unique())
    logger.info("Successfully collected: %d tickers", len(tickers_in_data))

    if failed_tickers:
        logger.warning("Failed tickers: %s", ", ".join(failed_tickers))

    # Compute expected trading days from business-day calendar
    expected_trading_days = _compute_expected_trading_days(start_date, end_date)
    logger.info(
        "Expected trading days (business-day calendar): %d",
        expected_trading_days,
    )

    # Per-ticker summary
    logger.info("-" * 60)
    logger.info("%-6s  %10s  %10s  %6s", "Ticker", "Earliest", "Latest", "Days")
    logger.info("-" * 60)

    for ticker in tickers_in_data:
        ticker_data = df[df["ticker"] == ticker]
        n_days = len(ticker_data)
        earliest = ticker_data["date"].min()
        latest = ticker_data["date"].max()

        # Format dates
        earliest_str = pd.Timestamp(earliest).strftime("%Y-%m-%d")
        latest_str = pd.Timestamp(latest).strftime("%Y-%m-%d")

        logger.info("%-6s  %10s  %10s  %6d", ticker, earliest_str, latest_str, n_days)

        # Warn if >5% missing trading days compared to expected calendar (Req 1.7)
        if expected_trading_days > 0:
            missing_pct = (1 - n_days / expected_trading_days) * 100
            if missing_pct > 5:
                logger.warning(
                    "⚠ %s has %.1f%% fewer trading days than expected "
                    "(%d vs %d expected). Check for missing data.",
                    ticker, missing_pct, n_days, expected_trading_days,
                )

    logger.info("-" * 60)
    logger.info(
        "Total rows: %d | Date range: %s to %s",
        len(df), start_date, end_date,
    )
    logger.info("=" * 60)


if __name__ == "__main__":
    collect_prices()
