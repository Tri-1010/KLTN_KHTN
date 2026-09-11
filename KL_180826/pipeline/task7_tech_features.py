"""
TASK 7: Tech_Feature_Extractor
Compute technical indicators from daily OHLCV data and aggregate by quarter.

This module:
1. Computes daily indicators using pandas-ta: RSI(14), MACD(12,26,9),
   Bollinger Bands(20,2), SMA(20,50), EMA(20) (Req 7.1)
2. Aggregates daily indicators into quarterly features per (ticker, quarter_id)
   organized into named groups: Returns, Volatility, Liquidity, Trend,
   Indicator, Momentum (Req 7.2, 7.3)
3. Saves quarterly technical features to data/features/technical_features.csv
   (Req 7.4)
4. Computes correlation matrix and warns for |corr| > 0.95 (Req 7.5)
"""

import math
import os
from typing import Optional

import numpy as np
import pandas as pd
import pandas_ta as ta

from pipeline.logging_config import setup_logger
from pipeline.task5_aggregate import assign_quarter_id

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PRICES_PATH = "data/prices/all_vn30_prices.csv"
FEATURES_OUTPUT_PATH = "data/features/technical_features.csv"
CORRELATION_THRESHOLD = 0.95


# ---------------------------------------------------------------------------
# Daily indicator computation (Req 7.1)
# ---------------------------------------------------------------------------


def compute_daily_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Compute daily technical indicators for a single ticker's price data.

    Adds the following columns using pandas-ta with explicit parameters:
    - RSI_14: Relative Strength Index with period 14
    - MACD_12_26_9, MACDs_12_26_9, MACDh_12_26_9: MACD line, signal, histogram
    - BBU_20_2.0, BBM_20_2.0, BBL_20_2.0: Bollinger upper, middle, lower
    - SMA_20, SMA_50: Simple Moving Averages
    - EMA_20: Exponential Moving Average
    - daily_return: (close - prev_close) / prev_close

    Args:
        df: DataFrame with columns [date, open, high, low, close, volume]
            for a single ticker, sorted by date ascending.

    Returns:
        DataFrame with all original columns plus indicator columns.
    """
    df = df.copy()
    df = df.sort_values("date").reset_index(drop=True)

    # Daily return
    df["daily_return"] = df["close"].pct_change()

    # RSI with period 14
    df["RSI_14"] = ta.rsi(df["close"], length=14)

    # MACD with parameters (fast=12, slow=26, signal=9)
    macd_result = ta.macd(df["close"], fast=12, slow=26, signal=9)
    if macd_result is not None and not macd_result.empty:
        df = pd.concat([df, macd_result], axis=1)

    # Bollinger Bands with parameters (period=20, std=2)
    bb_result = ta.bbands(df["close"], length=20, std=2)
    if bb_result is not None and not bb_result.empty:
        df = pd.concat([df, bb_result], axis=1)

    # SMA with periods 20 and 50
    df["SMA_20"] = ta.sma(df["close"], length=20)
    df["SMA_50"] = ta.sma(df["close"], length=50)

    # EMA with period 20
    df["EMA_20"] = ta.ema(df["close"], length=20)

    return df


# ---------------------------------------------------------------------------
# Quarterly aggregation (Req 7.2, 7.3)
# ---------------------------------------------------------------------------


def _find_column(df: pd.DataFrame, prefix: str) -> Optional[str]:
    """Find a column name that starts with the given prefix.

    pandas-ta may name columns slightly differently across versions,
    so we search by prefix to be robust.
    """
    matches = [c for c in df.columns if c.startswith(prefix)]
    return matches[0] if matches else None


def aggregate_quarter_features(
    daily_df: pd.DataFrame,
    prev_quarter_return: Optional[float] = None,
    two_q_ago_return: Optional[float] = None,
) -> dict:
    """Aggregate daily indicator data for one (ticker, quarter) into features.

    Args:
        daily_df: Daily data for a single (ticker, quarter) with indicator
            columns already computed. Must be sorted by date ascending.
        prev_quarter_return: Cumulative return of the previous quarter (lag 1).
        two_q_ago_return: Cumulative return of 2 quarters ago (lag 2).

    Returns:
        Dictionary of feature name → value.
    """
    if daily_df.empty:
        return {}

    features = {}

    close = daily_df["close"]
    high = daily_df["high"]
    low = daily_df["low"]
    volume = daily_df["volume"]
    daily_return = daily_df["daily_return"]

    close_first = close.iloc[0]
    close_last = close.iloc[-1]
    trading_days = len(daily_df)

    # --- Returns group ---
    features["return_q"] = (
        (close_last - close_first) / close_first if close_first != 0 else 0.0
    )
    features["return_mean_daily"] = daily_return.mean()
    features["return_std_daily"] = daily_return.std()

    # --- Volatility group ---
    features["volatility_q"] = (
        features["return_std_daily"] * math.sqrt(trading_days)
        if pd.notna(features["return_std_daily"])
        else np.nan
    )
    avg_close = close.mean()
    features["price_range_q"] = (
        (high.max() - low.min()) / avg_close if avg_close != 0 else 0.0
    )

    # --- Liquidity group ---
    features["volume_mean_q"] = volume.mean()
    # volume_change_q is computed later at the ticker level (vs previous quarter)
    features["volume_change_q"] = np.nan  # placeholder

    # --- Trend group (end-of-quarter values) ---
    sma20_col = "SMA_20"
    ema20_col = "EMA_20"

    sma20_end = (
        daily_df[sma20_col].iloc[-1]
        if sma20_col in daily_df.columns
        else np.nan
    )
    ema20_end = (
        daily_df[ema20_col].iloc[-1]
        if ema20_col in daily_df.columns
        else np.nan
    )
    features["sma20_end"] = sma20_end
    features["ema20_end"] = ema20_end
    features["price_vs_sma20"] = (
        (close_last - sma20_end) / sma20_end
        if pd.notna(sma20_end) and sma20_end != 0
        else np.nan
    )

    # --- Indicator group (quarterly means) ---
    rsi_col = "RSI_14"
    if rsi_col in daily_df.columns:
        features["rsi_mean_q"] = daily_df[rsi_col].mean()
        features["rsi_end_q"] = daily_df[rsi_col].iloc[-1]
    else:
        features["rsi_mean_q"] = np.nan
        features["rsi_end_q"] = np.nan

    macd_hist_col = _find_column(daily_df, "MACDh_")
    if macd_hist_col and macd_hist_col in daily_df.columns:
        features["macd_hist_mean_q"] = daily_df[macd_hist_col].mean()
    else:
        features["macd_hist_mean_q"] = np.nan

    # bb_position_q: (close - BB_lower) / (BB_upper - BB_lower)
    bbl_col = _find_column(daily_df, "BBL_")
    bbu_col = _find_column(daily_df, "BBU_")
    if bbl_col and bbu_col and bbl_col in daily_df.columns and bbu_col in daily_df.columns:
        bb_lower = daily_df[bbl_col]
        bb_upper = daily_df[bbu_col]
        bb_range = bb_upper - bb_lower
        bb_position = (close - bb_lower) / bb_range.replace(0, np.nan)
        features["bb_position_q"] = bb_position.mean()
    else:
        features["bb_position_q"] = np.nan

    # --- Momentum group (lagged values) ---
    features["return_prev_q"] = prev_quarter_return
    features["return_2q_ago"] = two_q_ago_return

    return features


def compute_quarterly_features(prices_df: pd.DataFrame) -> pd.DataFrame:
    """Compute quarterly technical features for all tickers.

    For each ticker:
    1. Compute daily indicators
    2. Assign quarter_id
    3. Aggregate into quarterly features per named group
    4. Compute volume_change_q and lag features across quarters

    Args:
        prices_df: Daily price DataFrame with columns
            [ticker, date, open, high, low, close, volume].

    Returns:
        DataFrame with columns [ticker, quarter_id, <feature columns>].
    """
    prices_df = prices_df.copy()
    prices_df["date"] = pd.to_datetime(prices_df["date"], errors="coerce")
    prices_df = prices_df.sort_values(["ticker", "date"])

    all_rows = []
    tickers = prices_df["ticker"].unique()

    for ticker in tickers:
        ticker_df = prices_df[prices_df["ticker"] == ticker].copy()

        # Step 1: Compute daily indicators
        ticker_df = compute_daily_indicators(ticker_df)

        # Step 2: Assign quarter_id
        ticker_df["quarter_id"] = ticker_df["date"].apply(assign_quarter_id)

        # Step 3: Group by quarter and aggregate
        quarters = sorted(ticker_df["quarter_id"].unique())
        quarter_features = []

        for qid in quarters:
            q_data = ticker_df[ticker_df["quarter_id"] == qid]
            feats = aggregate_quarter_features(q_data)
            feats["ticker"] = ticker
            feats["quarter_id"] = qid
            quarter_features.append(feats)

        if not quarter_features:
            continue

        qf_df = pd.DataFrame(quarter_features)

        # Step 4: Compute volume_change_q (vs previous quarter)
        qf_df = qf_df.sort_values("quarter_id").reset_index(drop=True)
        vol_prev = qf_df["volume_mean_q"].shift(1)
        qf_df["volume_change_q"] = (
            (qf_df["volume_mean_q"] - vol_prev) / vol_prev.replace(0, np.nan)
        )

        # Step 5: Compute lag features
        qf_df["return_prev_q"] = qf_df["return_q"].shift(1)
        qf_df["return_2q_ago"] = qf_df["return_q"].shift(2)

        all_rows.append(qf_df)

    if not all_rows:
        return pd.DataFrame()

    result = pd.concat(all_rows, ignore_index=True)

    # Reorder columns: ticker, quarter_id first, then features
    feature_cols = [
        "return_q", "return_mean_daily", "return_std_daily",
        "volatility_q", "price_range_q",
        "volume_mean_q", "volume_change_q",
        "sma20_end", "ema20_end", "price_vs_sma20",
        "rsi_mean_q", "rsi_end_q", "macd_hist_mean_q", "bb_position_q",
        "return_prev_q", "return_2q_ago",
    ]
    ordered_cols = ["ticker", "quarter_id"] + [
        c for c in feature_cols if c in result.columns
    ]
    result = result[ordered_cols]

    return result


# ---------------------------------------------------------------------------
# Correlation check (Req 7.5)
# ---------------------------------------------------------------------------


def check_correlations(
    df: pd.DataFrame,
    threshold: float = CORRELATION_THRESHOLD,
    logger=None,
) -> pd.DataFrame:
    """Compute correlation matrix and warn for highly correlated feature pairs.

    Args:
        df: Technical features DataFrame (numeric columns only).
        threshold: Absolute correlation threshold for warnings.
        logger: Optional logger instance.

    Returns:
        Correlation matrix as a DataFrame.
    """
    feature_cols = [
        c for c in df.columns if c not in ("ticker", "quarter_id")
    ]
    corr_matrix = df[feature_cols].corr()

    # Find pairs with |correlation| > threshold
    warned_pairs = set()
    for i, col_i in enumerate(feature_cols):
        for j, col_j in enumerate(feature_cols):
            if i >= j:
                continue
            corr_val = corr_matrix.loc[col_i, col_j]
            if pd.notna(corr_val) and abs(corr_val) > threshold:
                pair = tuple(sorted([col_i, col_j]))
                if pair not in warned_pairs:
                    warned_pairs.add(pair)
                    msg = (
                        f"High correlation ({corr_val:.3f}) between "
                        f"'{col_i}' and '{col_j}'"
                    )
                    if logger:
                        logger.warning(msg)
                    else:
                        print(f"WARNING: {msg}")

    return corr_matrix


# ---------------------------------------------------------------------------
# Save features (Req 7.4)
# ---------------------------------------------------------------------------


def save_features(
    df: pd.DataFrame,
    output_path: str = FEATURES_OUTPUT_PATH,
    logger=None,
) -> None:
    """Save technical features to CSV.

    Args:
        df: Technical features DataFrame.
        output_path: File path for the output CSV.
        logger: Optional logger instance.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    if logger:
        logger.info("Saved %d rows to %s", len(df), output_path)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def run_tech_features() -> pd.DataFrame:
    """Execute the full technical feature extraction pipeline (TASK 7).

    Steps:
    1. Load daily price data
    2. Compute daily indicators per ticker
    3. Aggregate into quarterly features
    4. Save to data/features/technical_features.csv
    5. Check correlations and warn for |corr| > 0.95

    Returns:
        The quarterly technical features DataFrame.
    """
    logger = setup_logger("TASK_7")
    logger.info("Starting Technical Feature Extraction (TASK 7)...")

    # Load prices
    if not os.path.isfile(PRICES_PATH):
        logger.error("Price data not found: %s", PRICES_PATH)
        return pd.DataFrame()

    prices_df = pd.read_csv(PRICES_PATH, encoding="utf-8")
    logger.info("Loaded %d daily price rows.", len(prices_df))

    # Compute quarterly features
    features_df = compute_quarterly_features(prices_df)
    logger.info(
        "Computed %d quarterly feature rows for %d tickers.",
        len(features_df),
        features_df["ticker"].nunique() if not features_df.empty else 0,
    )

    # Save features
    save_features(features_df, FEATURES_OUTPUT_PATH, logger)

    # Check correlations
    if not features_df.empty:
        logger.info("Computing correlation matrix...")
        check_correlations(features_df, CORRELATION_THRESHOLD, logger)

    logger.info("TASK 7 complete.")
    return features_df


if __name__ == "__main__":
    run_tech_features()
