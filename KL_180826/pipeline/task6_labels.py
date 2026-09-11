"""
TASK 6: Label_Builder
Build binary classification labels from quarterly price changes.

This module:
1. Computes label_basic: 1 if next_avg_close > avg_close, else 0 (Req 6.1)
2. Computes label_threshold with ±2% threshold (Req 6.2)
3. Saves master_with_labels.csv (Req 6.3)
4. Analyzes label distribution by year and sector (Req 6.4, 6.5)
5. Generates label distribution bar chart (Req 6.6)
"""

import os
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless environments
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pipeline.logging_config import setup_logger

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
MASTER_DATASET_PATH = "data/aggregated/master_dataset.csv"
MASTER_WITH_LABELS_PATH = "data/aggregated/master_with_labels.csv"
LABEL_DISTRIBUTION_PATH = "reports/label_distribution.png"

# ---------------------------------------------------------------------------
# Sector mapping (Req 6.4)
# ---------------------------------------------------------------------------
SECTOR_MAPPING = {
    "Banking": [
        "ACB", "BID", "CTG", "HDB", "MBB", "SHB", "SSB",
        "STB", "TCB", "TPB", "VCB", "VIB", "VPB",
    ],
    "Real Estate": ["BCM", "VHM", "VIC", "VRE"],
    "Energy/Resources": ["GAS", "GVR", "PLX", "POW"],
    "Consumer/Food": ["MWG", "SAB", "VNM"],
    "Industrial": ["HPG"],
    "Finance/Insurance": ["BVH", "SSI"],
    "Tech/Telecom": ["FPT"],
}

# Reverse mapping: ticker → sector
TICKER_TO_SECTOR = {}
for sector, tickers in SECTOR_MAPPING.items():
    for ticker in tickers:
        TICKER_TO_SECTOR[ticker] = sector


# ---------------------------------------------------------------------------
# Label computation (Req 6.1, 6.2)
# ---------------------------------------------------------------------------

def build_label_basic(
    avg_close: float,
    next_avg_close: float,
) -> Optional[int]:
    """Compute the basic binary label.

    Args:
        avg_close: Average closing price in the current quarter.
        next_avg_close: Average closing price in the next quarter.

    Returns:
        1 if next_avg_close > avg_close, 0 otherwise.
        None if either value is NaN.
    """
    if pd.isna(avg_close) or pd.isna(next_avg_close):
        return None
    return 1 if next_avg_close > avg_close else 0


def build_label_threshold(
    avg_close: float,
    next_avg_close: float,
    threshold: float = 0.02,
) -> Optional[float]:
    """Compute the threshold-based label.

    Computes return = (next_avg_close - avg_close) / avg_close, then:
    - 1 if return > +threshold
    - 0 if return < -threshold
    - NaN if |return| <= threshold

    Args:
        avg_close: Average closing price in the current quarter.
        next_avg_close: Average closing price in the next quarter.
        threshold: Threshold for label assignment (default 0.02 = ±2%).

    Returns:
        1.0, 0.0, or NaN. None if inputs are invalid.
    """
    if pd.isna(avg_close) or pd.isna(next_avg_close) or avg_close == 0:
        return None
    ret = (next_avg_close - avg_close) / avg_close
    if ret > threshold:
        return 1.0
    elif ret < -threshold:
        return 0.0
    else:
        return np.nan


def compute_return(
    avg_close: float,
    next_avg_close: float,
) -> Optional[float]:
    """Compute quarter-over-quarter return.

    Args:
        avg_close: Average closing price in the current quarter.
        next_avg_close: Average closing price in the next quarter.

    Returns:
        (next_avg_close - avg_close) / avg_close, or None if invalid.
    """
    if pd.isna(avg_close) or pd.isna(next_avg_close) or avg_close == 0:
        return None
    return (next_avg_close - avg_close) / avg_close


def build_labels(
    df: pd.DataFrame,
    threshold: float = 0.02,
) -> pd.DataFrame:
    """Add label columns to the master dataset.

    Adds:
    - ``return``: quarter-over-quarter return
    - ``label_basic``: 1 if next_avg_close > avg_close, else 0
    - ``label_threshold``: 1 if return > +threshold, 0 if < -threshold, NaN otherwise

    Args:
        df: Master dataset with columns [avg_close, next_avg_close].
        threshold: Threshold for label_threshold (default 0.02).

    Returns:
        DataFrame with additional label columns.
    """
    df = df.copy()
    df["return"] = df.apply(
        lambda row: compute_return(row["avg_close"], row["next_avg_close"]),
        axis=1,
    )
    df["label_basic"] = df.apply(
        lambda row: build_label_basic(row["avg_close"], row["next_avg_close"]),
        axis=1,
    )
    df["label_threshold"] = df.apply(
        lambda row: build_label_threshold(
            row["avg_close"], row["next_avg_close"], threshold
        ),
        axis=1,
    )
    return df


# ---------------------------------------------------------------------------
# Label distribution analysis (Req 6.4, 6.5)
# ---------------------------------------------------------------------------

def analyze_label_distribution(
    df: pd.DataFrame,
    logger,
) -> None:
    """Analyze and report label distribution.

    Reports:
    - Overall ratio of label=1 to label=0
    - Ratio by year
    - Ratio by sector
    - Class imbalance warning if minority class < 35%

    Args:
        df: DataFrame with label_basic column.
        logger: Logger instance.
    """
    logger.info("=" * 60)
    logger.info("LABEL DISTRIBUTION ANALYSIS")
    logger.info("=" * 60)

    # Filter rows with valid labels
    valid = df[df["label_basic"].notna()].copy()
    if valid.empty:
        logger.warning("No valid labels found for analysis.")
        return

    # --- Overall ratio ---
    total = len(valid)
    count_1 = int((valid["label_basic"] == 1).sum())
    count_0 = int((valid["label_basic"] == 0).sum())
    ratio_1 = count_1 / total if total > 0 else 0
    ratio_0 = count_0 / total if total > 0 else 0
    minority_ratio = min(ratio_1, ratio_0)

    logger.info("Overall: label=1: %d (%.1f%%), label=0: %d (%.1f%%)",
                count_1, ratio_1 * 100, count_0, ratio_0 * 100)

    # --- By year ---
    valid["year"] = valid["quarter_id"].str[:4]
    logger.info("Distribution by year:")
    for year, group in valid.groupby("year"):
        y_total = len(group)
        y_count_1 = int((group["label_basic"] == 1).sum())
        y_count_0 = int((group["label_basic"] == 0).sum())
        logger.info(
            "  %s: label=1: %d (%.1f%%), label=0: %d (%.1f%%)",
            year,
            y_count_1,
            y_count_1 / y_total * 100 if y_total > 0 else 0,
            y_count_0,
            y_count_0 / y_total * 100 if y_total > 0 else 0,
        )

    # --- By sector ---
    valid["sector"] = valid["ticker"].map(TICKER_TO_SECTOR).fillna("Other")
    logger.info("Distribution by sector:")
    for sector, group in valid.groupby("sector"):
        s_total = len(group)
        s_count_1 = int((group["label_basic"] == 1).sum())
        s_count_0 = int((group["label_basic"] == 0).sum())
        logger.info(
            "  %s: label=1: %d (%.1f%%), label=0: %d (%.1f%%)",
            sector,
            s_count_1,
            s_count_1 / s_total * 100 if s_total > 0 else 0,
            s_count_0,
            s_count_0 / s_total * 100 if s_total > 0 else 0,
        )

    # --- Class imbalance warning (Req 6.5) ---
    if minority_ratio < 0.35:
        logger.warning(
            "CLASS IMBALANCE WARNING: Minority class ratio = %.1f%% (< 35%%). "
            "Consider using class_weight='balanced' or adjusting the label "
            "threshold during model training.",
            minority_ratio * 100,
        )

    logger.info("=" * 60)


# ---------------------------------------------------------------------------
# Label distribution visualization (Req 6.6)
# ---------------------------------------------------------------------------

def generate_label_distribution_chart(
    df: pd.DataFrame,
    output_path: str = LABEL_DISTRIBUTION_PATH,
    logger=None,
) -> None:
    """Generate a bar chart of label distribution by year × quarter.

    Args:
        df: DataFrame with columns [quarter_id, label_basic].
        output_path: File path for the saved PNG.
        logger: Optional logger.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    valid = df[df["label_basic"].notna()].copy()
    if valid.empty:
        if logger:
            logger.warning("No valid labels to plot.")
        return

    # Build counts by quarter_id
    counts = (
        valid.groupby(["quarter_id", "label_basic"])
        .size()
        .unstack(fill_value=0)
    )
    # Ensure both columns exist
    for col in [0, 1]:
        if col not in counts.columns:
            counts[col] = 0
    counts = counts[[0, 1]]
    counts.columns = ["label=0", "label=1"]
    counts = counts.sort_index()

    # Plot
    fig, ax = plt.subplots(figsize=(max(10, len(counts) * 0.8), 6))
    x = range(len(counts))
    width = 0.35

    bars_0 = ax.bar(
        [i - width / 2 for i in x],
        counts["label=0"],
        width,
        label="label=0 (decrease/no-increase)",
        color="#e74c3c",
        alpha=0.8,
    )
    bars_1 = ax.bar(
        [i + width / 2 for i in x],
        counts["label=1"],
        width,
        label="label=1 (increase)",
        color="#2ecc71",
        alpha=0.8,
    )

    ax.set_xlabel("Quarter")
    ax.set_ylabel("Count")
    ax.set_title("Label Distribution by Year × Quarter")
    ax.set_xticks(list(x))
    ax.set_xticklabels(counts.index, rotation=45, ha="right")
    ax.legend()

    # Add value labels on bars
    for bar in bars_0:
        height = bar.get_height()
        if height > 0:
            ax.annotate(
                f"{int(height)}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )
    for bar in bars_1:
        height = bar.get_height()
        if height > 0:
            ax.annotate(
                f"{int(height)}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    plt.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    if logger:
        logger.info("Label distribution chart saved to %s", output_path)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_label_builder() -> pd.DataFrame:
    """Execute the full label building pipeline (TASK 6).

    Steps:
    1. Load master_dataset.csv
    2. Compute labels (label_basic, label_threshold, return)
    3. Save master_with_labels.csv
    4. Analyze label distribution
    5. Generate label distribution chart

    Returns:
        The master dataset with labels DataFrame.
    """
    logger = setup_logger("TASK_6")
    logger.info("Starting Label Builder (TASK 6)...")

    # ------------------------------------------------------------------
    # Load input
    # ------------------------------------------------------------------
    if not os.path.isfile(MASTER_DATASET_PATH):
        logger.error("Master dataset not found: %s", MASTER_DATASET_PATH)
        return pd.DataFrame()

    master = pd.read_csv(MASTER_DATASET_PATH, encoding="utf-8")
    logger.info("Loaded master dataset: %d rows from %s", len(master), MASTER_DATASET_PATH)

    # ------------------------------------------------------------------
    # Build labels (Req 6.1, 6.2, 6.3)
    # ------------------------------------------------------------------
    master = build_labels(master, threshold=0.02)

    # Save output
    os.makedirs(os.path.dirname(MASTER_WITH_LABELS_PATH), exist_ok=True)
    master.to_csv(MASTER_WITH_LABELS_PATH, index=False)
    logger.info(
        "Saved master with labels: %d rows → %s",
        len(master),
        MASTER_WITH_LABELS_PATH,
    )

    # ------------------------------------------------------------------
    # Analyze distribution (Req 6.4, 6.5)
    # ------------------------------------------------------------------
    analyze_label_distribution(master, logger)

    # ------------------------------------------------------------------
    # Generate visualization (Req 6.6)
    # ------------------------------------------------------------------
    generate_label_distribution_chart(master, LABEL_DISTRIBUTION_PATH, logger)

    logger.info("TASK 6 complete.")
    return master


if __name__ == "__main__":
    run_label_builder()
