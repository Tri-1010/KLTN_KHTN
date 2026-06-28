"""
TASK 5: Data_Aggregator
Aggregate news and price data by (ticker, quarter_id).

This module:
1. Assigns quarter_id labels ("YYYYQn") to price and news datasets (Req 5.1)
2. Aggregates news per (ticker, quarter_id): news_count, combined_text (Req 5.2)
3. Aggregates prices per (ticker, quarter_id): avg_close, avg_volume,
   return_intra, trading_days (Req 5.3)
4. Merges news + price aggregations, adds next_quarter_id and
   next_avg_close (Req 5.4, 5.5)
5. Generates aggregation report and coverage heatmap (Req 5.6, 5.7)
"""

import os
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless environments
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from pipeline.logging_config import setup_logger

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PRICES_PATH = "data/prices/all_vn30_prices.csv"
NEWS_PATH = "data/news/processed/all_news_processed.csv"
NEWS_BY_QUARTER_PATH = "data/aggregated/news_by_quarter.csv"
PRICES_BY_QUARTER_PATH = "data/aggregated/prices_by_quarter.csv"
MASTER_DATASET_PATH = "data/aggregated/master_dataset.csv"
HEATMAP_PATH = "reports/coverage_heatmap.png"


# ---------------------------------------------------------------------------
# Quarter assignment (Req 5.1)
# ---------------------------------------------------------------------------

def assign_quarter_id(date_val: pd.Timestamp) -> str:
    """Map a date to its quarter identifier in 'YYYYQn' format.

    Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec.

    Args:
        date_val: A pandas Timestamp or datetime-like value.

    Returns:
        Quarter string, e.g. '2022Q1'.
    """
    quarter = (date_val.month - 1) // 3 + 1
    return f"{date_val.year}Q{quarter}"


def add_quarter_id(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Add a ``quarter_id`` column to *df* based on *date_col*.

    The date column is coerced to datetime first.

    Args:
        df: DataFrame containing a date column.
        date_col: Name of the date column.

    Returns:
        DataFrame with an additional ``quarter_id`` column.
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df["quarter_id"] = df[date_col].apply(assign_quarter_id)
    return df


# ---------------------------------------------------------------------------
# News aggregation (Req 5.2)
# ---------------------------------------------------------------------------

def aggregate_news(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate news articles by (ticker, quarter_id).

    For each group:
    - ``news_count``: number of articles
    - ``combined_text``: all ``text_tokenized`` values concatenated with a space

    Args:
        df: Processed news DataFrame with columns
            [ticker, date, text_tokenized, ...].

    Returns:
        Aggregated DataFrame with columns
        [ticker, quarter_id, news_count, combined_text].
    """
    # Guard against empty input or missing required columns so the pipeline
    # degrades gracefully (e.g. when news scraping yielded no articles)
    # instead of raising a cryptic KeyError downstream.
    required_cols = {"ticker", "date", "text_tokenized"}
    if df.empty or not required_cols.issubset(df.columns):
        return pd.DataFrame(
            columns=["ticker", "quarter_id", "news_count", "combined_text"]
        )

    df = add_quarter_id(df, date_col="date")

    agg = (
        df.groupby(["ticker", "quarter_id"])
        .agg(
            news_count=("text_tokenized", "size"),
            combined_text=("text_tokenized", lambda texts: " ".join(
                str(t) for t in texts if pd.notna(t)
            )),
        )
        .reset_index()
    )
    return agg


# ---------------------------------------------------------------------------
# Price aggregation (Req 5.3)
# ---------------------------------------------------------------------------

def aggregate_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate daily prices by (ticker, quarter_id).

    Computes:
    - ``avg_close``: mean closing price
    - ``avg_volume``: mean daily volume
    - ``return_intra``: (close_last - close_first) / close_first
    - ``trading_days``: count of trading days

    Args:
        df: Daily price DataFrame with columns
            [ticker, date, open, high, low, close, volume].

    Returns:
        Aggregated DataFrame with columns
        [ticker, quarter_id, avg_close, avg_volume, return_intra, trading_days].
    """
    df = add_quarter_id(df, date_col="date")
    df = df.sort_values(["ticker", "date"])

    def _agg_group(g: pd.DataFrame) -> pd.Series:
        close_first = g["close"].iloc[0]
        close_last = g["close"].iloc[-1]
        return_intra = (
            (close_last - close_first) / close_first
            if close_first != 0
            else 0.0
        )
        return pd.Series({
            "avg_close": g["close"].mean(),
            "avg_volume": g["volume"].mean(),
            "return_intra": return_intra,
            "trading_days": len(g),
        })

    agg = (
        df.groupby(["ticker", "quarter_id"])
        .apply(_agg_group, include_groups=False)
        .reset_index()
    )
    return agg


# ---------------------------------------------------------------------------
# Next-quarter helpers (Req 5.4)
# ---------------------------------------------------------------------------

def _next_quarter(quarter_id: str) -> str:
    """Return the quarter_id immediately following *quarter_id*.

    Example: '2022Q4' → '2023Q1', '2023Q1' → '2023Q2'.
    """
    year = int(quarter_id[:4])
    q = int(quarter_id[-1])
    if q == 4:
        return f"{year + 1}Q1"
    return f"{year}Q{q + 1}"


def build_master_dataset(
    news_agg: pd.DataFrame,
    price_agg: pd.DataFrame,
) -> pd.DataFrame:
    """Merge news and price aggregations and add next-quarter columns.

    Only rows that have **both** price and news data are retained.

    Adds:
    - ``next_quarter_id``: the following quarter
    - ``next_avg_close``: avg_close of the following quarter for the same
      ticker (NaN if not available)

    Args:
        news_agg: Output of :func:`aggregate_news`.
        price_agg: Output of :func:`aggregate_prices`.

    Returns:
        Master dataset DataFrame.
    """
    # Inner merge keeps only rows present in both
    master = pd.merge(
        price_agg,
        news_agg,
        on=["ticker", "quarter_id"],
        how="inner",
    )

    # Add next_quarter_id
    master["next_quarter_id"] = master["quarter_id"].apply(_next_quarter)

    # Build a lookup for avg_close by (ticker, quarter_id)
    close_lookup = price_agg.set_index(["ticker", "quarter_id"])["avg_close"]

    # Map next_avg_close
    master["next_avg_close"] = master.apply(
        lambda row: close_lookup.get((row["ticker"], row["next_quarter_id"]), None),
        axis=1,
    )

    return master


# ---------------------------------------------------------------------------
# Reporting (Req 5.6, 5.7)
# ---------------------------------------------------------------------------

def generate_aggregation_report(
    master: pd.DataFrame,
    logger,
) -> None:
    """Print aggregation summary and warnings.

    Reports:
    - Number of (ticker, quarter) pairs per year
    - Warns for pairs with news_count < 5
    - Warns if total samples < 300

    Args:
        master: Master dataset DataFrame.
        logger: Logger instance.
    """
    logger.info("=" * 60)
    logger.info("AGGREGATION REPORT")
    logger.info("=" * 60)

    total = len(master)
    logger.info("Total (ticker, quarter) pairs: %d", total)

    # Pairs per year
    master_copy = master.copy()
    master_copy["year"] = master_copy["quarter_id"].str[:4]
    pairs_per_year = master_copy.groupby("year").size()
    for year, count in pairs_per_year.items():
        logger.info("  Year %s: %d pairs", year, count)

    # Warn for low news coverage
    low_news = master[master["news_count"] < 5]
    if not low_news.empty:
        logger.warning(
            "%d (ticker, quarter) pairs have news_count < 5:",
            len(low_news),
        )
        for _, row in low_news.iterrows():
            logger.warning(
                "  %s %s — news_count=%d",
                row["ticker"],
                row["quarter_id"],
                row["news_count"],
            )

    # Warn if total samples < 300
    if total < 300:
        logger.warning(
            "Total samples (%d) is below the recommended minimum of 300.",
            total,
        )

    logger.info("=" * 60)


def generate_coverage_heatmap(
    master: pd.DataFrame,
    output_path: str = HEATMAP_PATH,
    logger=None,
) -> None:
    """Generate and save a coverage heatmap (ticker × quarter, color = news_count).

    Args:
        master: Master dataset with columns [ticker, quarter_id, news_count].
        output_path: File path for the saved PNG.
        logger: Optional logger.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    pivot = master.pivot_table(
        index="ticker",
        columns="quarter_id",
        values="news_count",
        fill_value=0,
    )

    # Sort columns chronologically
    pivot = pivot.reindex(sorted(pivot.columns), axis=1)

    fig_width = max(12, len(pivot.columns) * 0.8)
    fig_height = max(8, len(pivot.index) * 0.35)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Ensure integer values for annotation formatting
    pivot = pivot.astype(int)

    sns.heatmap(
        pivot,
        annot=True,
        fmt="d",
        cmap="YlOrRd",
        linewidths=0.5,
        ax=ax,
    )
    ax.set_title("News Coverage Heatmap (ticker × quarter)", fontsize=14)
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Ticker")
    plt.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    if logger:
        logger.info("Coverage heatmap saved to %s", output_path)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_aggregation() -> pd.DataFrame:
    """Execute the full data aggregation pipeline (TASK 5).

    Steps:
    1. Load price and news data
    2. Aggregate news by (ticker, quarter_id)
    3. Aggregate prices by (ticker, quarter_id)
    4. Merge into master dataset with next-quarter columns
    5. Generate report and heatmap

    Returns:
        The master dataset DataFrame.
    """
    logger = setup_logger("TASK_5")
    logger.info("Starting Data Aggregation (TASK 5)...")

    # ------------------------------------------------------------------
    # Load inputs
    # ------------------------------------------------------------------
    if not os.path.isfile(PRICES_PATH):
        logger.error("Price data not found: %s", PRICES_PATH)
        return pd.DataFrame()

    if not os.path.isfile(NEWS_PATH):
        logger.error("Processed news data not found: %s", NEWS_PATH)
        return pd.DataFrame()

    prices_df = pd.read_csv(PRICES_PATH, encoding="utf-8")
    news_df = pd.read_csv(NEWS_PATH, encoding="utf-8")
    logger.info(
        "Loaded %d price rows and %d news articles.",
        len(prices_df),
        len(news_df),
    )

    # ------------------------------------------------------------------
    # Aggregate news (Req 5.2)
    # ------------------------------------------------------------------
    news_agg = aggregate_news(news_df)
    os.makedirs(os.path.dirname(NEWS_BY_QUARTER_PATH), exist_ok=True)
    news_agg.to_csv(NEWS_BY_QUARTER_PATH, index=False)
    logger.info(
        "News aggregation: %d (ticker, quarter) pairs → %s",
        len(news_agg),
        NEWS_BY_QUARTER_PATH,
    )

    if news_agg.empty:
        logger.error(
            "No usable news rows after preprocessing (0 aggregated pairs). "
            "This usually means TASK 2 scraping collected no valid articles "
            "(check selectors / network) — downstream tasks need news data. "
            "Writing empty master dataset and stopping aggregation early."
        )
        empty_master = pd.DataFrame(
            columns=[
                "ticker", "quarter_id", "avg_close", "avg_volume",
                "return_intra", "trading_days", "news_count", "combined_text",
                "next_quarter_id", "next_avg_close",
            ]
        )
        empty_master.to_csv(MASTER_DATASET_PATH, index=False)
        return empty_master

    # ------------------------------------------------------------------
    # Aggregate prices (Req 5.3)
    # ------------------------------------------------------------------
    price_agg = aggregate_prices(prices_df)
    price_agg.to_csv(PRICES_BY_QUARTER_PATH, index=False)
    logger.info(
        "Price aggregation: %d (ticker, quarter) pairs → %s",
        len(price_agg),
        PRICES_BY_QUARTER_PATH,
    )

    # ------------------------------------------------------------------
    # Build master dataset (Req 5.4, 5.5)
    # ------------------------------------------------------------------
    master = build_master_dataset(news_agg, price_agg)
    master.to_csv(MASTER_DATASET_PATH, index=False)
    logger.info(
        "Master dataset: %d rows → %s",
        len(master),
        MASTER_DATASET_PATH,
    )

    # ------------------------------------------------------------------
    # Report & heatmap (Req 5.6, 5.7)
    # ------------------------------------------------------------------
    generate_aggregation_report(master, logger)
    generate_coverage_heatmap(master, HEATMAP_PATH, logger)

    logger.info("TASK 5 complete.")
    return master


if __name__ == "__main__":
    run_aggregation()
