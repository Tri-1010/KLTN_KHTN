"""
TASK 3: Entity_Matcher
Map news articles to VN30 tickers using company name aliases.

Loads alias dictionary from config/entity_aliases.json and matches each
article's title + description against known company names.  Special priority
rules disambiguate the Vingroup family (VHM, VRE, VIC).

Outputs:
    data/news/matched/all_news_matched.csv
    logs/unmatched_articles.log
"""

import json
import logging
import os
from typing import Dict, List, Tuple

import pandas as pd

from pipeline.logging_config import setup_logger

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALIASES_PATH = "config/entity_aliases.json"
OUTPUT_PATH = "data/news/matched/all_news_matched.csv"
UNMATCHED_LOG_PATH = "logs/unmatched_articles.log"

OUTPUT_COLUMNS = [
    "date",
    "title",
    "description",
    "url",
    "source",
    "ticker",
    "match_confidence",
]

# News source directories / files
NEWS_SOURCES = {
    "cafef": "data/news/cafef",
    "vietstock": "data/news/vietstock",
    "tnck": "data/news/tnck/tnck_raw.csv",
    "vietnambiz": "data/news/vietnambiz/vietnambiz_raw.csv",
    "vnexpress": "data/news/vnexpress/vnexpress_raw.csv",
}

# ---------------------------------------------------------------------------
# Alias loading
# ---------------------------------------------------------------------------


def load_aliases(path: str = ALIASES_PATH) -> Dict[str, List[str]]:
    """Load ticker → alias list mapping from JSON config file.

    Args:
        path: Path to entity_aliases.json.

    Returns:
        Dictionary mapping ticker symbols to lists of alias strings.

    Raises:
        FileNotFoundError: If the alias file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    with open(path, "r", encoding="utf-8") as f:
        aliases: Dict[str, List[str]] = json.load(f)
    return aliases


# ---------------------------------------------------------------------------
# Vingroup family priority matching
# ---------------------------------------------------------------------------

# Ordered list of (pattern, ticker, confidence) for Vingroup disambiguation.
# Checked first, in order, so more-specific patterns take priority.
_VINGROUP_PRIORITY: List[Tuple[str, str, str]] = [
    ("vinhomes", "VHM", "exact"),
    ("vincom retail", "VRE", "exact"),
    ("trung tâm thương mại vincom", "VRE", "exact"),
    ("ctcp vinhomes", "VHM", "exact"),
    ("ctcp vincom retail", "VRE", "exact"),
]

# Patterns that map to VIC only when no VHM/VRE pattern matched first.
_VINGROUP_GENERIC: List[Tuple[str, str, str]] = [
    ("vingroup", "VIC", "exact"),
    ("tập đoàn vingroup", "VIC", "exact"),
    ("vin group", "VIC", "exact"),
]


def _match_vingroup(text_lower: str) -> List[Tuple[str, str]]:
    """Return Vingroup-family matches with priority disambiguation.

    "Vinhomes" → VHM, "Vincom Retail" / "trung tâm thương mại Vincom" → VRE,
    "Vingroup" / "tập đoàn Vingroup" → VIC.

    Returns:
        List of (ticker, confidence) tuples.  May contain 0, 1, or more
        entries if the text mentions multiple Vingroup entities.
    """
    matches: List[Tuple[str, str]] = []
    matched_tickers: set = set()

    # Check specific patterns first
    for pattern, ticker, confidence in _VINGROUP_PRIORITY:
        if pattern in text_lower and ticker not in matched_tickers:
            matches.append((ticker, confidence))
            matched_tickers.add(ticker)

    # Check generic Vingroup patterns only if VIC not already matched
    for pattern, ticker, confidence in _VINGROUP_GENERIC:
        if pattern in text_lower and ticker not in matched_tickers:
            matches.append((ticker, confidence))
            matched_tickers.add(ticker)

    return matches


# ---------------------------------------------------------------------------
# General matching
# ---------------------------------------------------------------------------

# Tickers whose aliases should NOT be used for general substring matching
# because they are handled by the Vingroup priority logic above.
_VINGROUP_TICKERS = {"VHM", "VIC", "VRE"}


def _build_alias_index(
    aliases: Dict[str, List[str]],
) -> List[Tuple[str, str, str]]:
    """Build a flat list of (alias_lower, ticker, confidence) sorted longest-first.

    Longer aliases are checked first so that e.g. "Ngân hàng Ngoại thương"
    matches before the 3-letter ticker code that might appear inside other words.

    Vingroup-family tickers are excluded here — they are handled separately.
    """
    index: List[Tuple[str, str, str]] = []
    for ticker, names in aliases.items():
        if ticker in _VINGROUP_TICKERS:
            continue
        for name in names:
            name_lower = name.lower().strip()
            if not name_lower:
                continue
            # Ticker codes (<=4 chars uppercase) are "exact"; longer names are "partial"
            confidence = "exact" if name.strip().isupper() and len(name.strip()) <= 4 else "partial"
            index.append((name_lower, ticker, confidence))

    # Sort longest first to prefer more-specific matches
    index.sort(key=lambda x: -len(x[0]))
    return index


def match_single_article(
    text: str,
    alias_index: List[Tuple[str, str, str]],
) -> List[Tuple[str, str]]:
    """Match a single article text against all aliases.

    Args:
        text: Combined title + description (will be lowercased internally).
        alias_index: Pre-built alias index from ``_build_alias_index``.

    Returns:
        List of (ticker, match_confidence) tuples.  Empty if no match.
    """
    text_lower = text.lower()
    matches: List[Tuple[str, str]] = []
    matched_tickers: set = set()

    # 1. Vingroup family — priority rules
    vin_matches = _match_vingroup(text_lower)
    for ticker, confidence in vin_matches:
        if ticker not in matched_tickers:
            matches.append((ticker, confidence))
            matched_tickers.add(ticker)

    # 2. General alias matching (non-Vingroup)
    for alias_lower, ticker, confidence in alias_index:
        if ticker in matched_tickers:
            continue
        if alias_lower in text_lower:
            matches.append((ticker, confidence))
            matched_tickers.add(ticker)

    return matches


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def match_entities(
    articles: pd.DataFrame,
    aliases: Dict[str, List[str]],
    logger: logging.Logger | None = None,
) -> pd.DataFrame:
    """Map articles to VN30 tickers using company name aliases.

    For each article the title and description are concatenated and matched
    case-insensitively against the alias dictionary.  Articles matching
    multiple tickers produce one output row per ticker.  Unmatched articles
    receive ticker="UNKNOWN" and are logged.

    Args:
        articles: DataFrame with at least ``title`` and ``description`` columns.
        aliases: Loaded from ``config/entity_aliases.json``.
        logger: Optional logger instance.

    Returns:
        DataFrame with columns defined by ``OUTPUT_COLUMNS``.
    """
    if logger is None:
        logger = setup_logger("TASK_3")

    alias_index = _build_alias_index(aliases)

    rows: list = []
    unmatched_urls: list = []

    for _, row in articles.iterrows():
        title = str(row.get("title", "") or "")
        description = str(row.get("description", "") or "")
        combined = f"{title} {description}"

        matches = match_single_article(combined, alias_index)

        if matches:
            # One output row per matched ticker (Req 3.4)
            for ticker, confidence in matches:
                rows.append(
                    {
                        "date": row.get("date", ""),
                        "title": title,
                        "description": description,
                        "url": row.get("url", ""),
                        "source": row.get("source", ""),
                        "ticker": ticker,
                        "match_confidence": confidence,
                    }
                )
        else:
            # No match → UNKNOWN (Req 3.5)
            rows.append(
                {
                    "date": row.get("date", ""),
                    "title": title,
                    "description": description,
                    "url": row.get("url", ""),
                    "source": row.get("source", ""),
                    "ticker": "UNKNOWN",
                    "match_confidence": "none",
                }
            )
            unmatched_urls.append(row.get("url", ""))

    # Log unmatched articles to separate file (Req 3.5)
    if unmatched_urls:
        os.makedirs(os.path.dirname(UNMATCHED_LOG_PATH), exist_ok=True)
        with open(UNMATCHED_LOG_PATH, "w", encoding="utf-8") as f:
            f.write("# Unmatched article URLs\n")
            for url in unmatched_urls:
                f.write(f"{url}\n")
        logger.info(
            "Logged %d unmatched article URLs to %s",
            len(unmatched_urls),
            UNMATCHED_LOG_PATH,
        )

    matched_df = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    return matched_df


# ---------------------------------------------------------------------------
# Collect all raw news into a single DataFrame
# ---------------------------------------------------------------------------


def _load_all_news(logger: logging.Logger) -> pd.DataFrame:
    """Load and concatenate all raw news CSVs from the three sources."""
    frames: list = []

    # CafeF: one CSV per ticker
    cafef_dir = NEWS_SOURCES["cafef"]
    if os.path.isdir(cafef_dir):
        for fname in sorted(os.listdir(cafef_dir)):
            if fname.endswith("_cafef.csv"):
                path = os.path.join(cafef_dir, fname)
                try:
                    df = pd.read_csv(path, encoding="utf-8")
                    if not df.empty:
                        frames.append(df)
                except Exception as exc:
                    logger.warning("Failed to read %s: %s", path, exc)

    # Vietstock: one CSV per ticker
    vs_dir = NEWS_SOURCES["vietstock"]
    if os.path.isdir(vs_dir):
        for fname in sorted(os.listdir(vs_dir)):
            if fname.endswith("_vietstock.csv"):
                path = os.path.join(vs_dir, fname)
                try:
                    df = pd.read_csv(path, encoding="utf-8")
                    if not df.empty:
                        frames.append(df)
                except Exception as exc:
                    logger.warning("Failed to read %s: %s", path, exc)

    # TNCK: single file
    tnck_path = NEWS_SOURCES["tnck"]
    if os.path.isfile(tnck_path):
        try:
            df = pd.read_csv(tnck_path, encoding="utf-8")
            if not df.empty:
                frames.append(df)
        except Exception as exc:
            logger.warning("Failed to read %s: %s", tnck_path, exc)

    # VietnamBiz: single file (broad scrape, like TNCK)
    vnbiz_path = NEWS_SOURCES.get("vietnambiz")
    if vnbiz_path and os.path.isfile(vnbiz_path):
        try:
            df = pd.read_csv(vnbiz_path, encoding="utf-8")
            if not df.empty:
                frames.append(df)
        except Exception as exc:
            logger.warning("Failed to read %s: %s", vnbiz_path, exc)

    # VnExpress: single file (broad scrape, like TNCK)
    vne_path = NEWS_SOURCES.get("vnexpress")
    if vne_path and os.path.isfile(vne_path):
        try:
            df = pd.read_csv(vne_path, encoding="utf-8")
            if not df.empty:
                frames.append(df)
        except Exception as exc:
            logger.warning("Failed to read %s: %s", vne_path, exc)

    if not frames:
        logger.warning("No news files found in any source directory.")
        return pd.DataFrame(columns=["date", "title", "description", "url", "source"])

    combined = pd.concat(frames, ignore_index=True)
    logger.info("Loaded %d total articles from all sources.", len(combined))
    return combined


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def generate_matching_report(
    total_before: int,
    matched_df: pd.DataFrame,
    logger: logging.Logger,
) -> None:
    """Print matching summary report (Req 3.7).

    Reports:
        - Total articles before and after matching
        - UNKNOWN rate
        - Articles per ticker per source
        - Warning for any ticker with <20 articles per year
    """
    total_after = len(matched_df)
    unknown_count = int((matched_df["ticker"] == "UNKNOWN").sum())
    unknown_rate = unknown_count / total_after * 100 if total_after > 0 else 0.0

    logger.info("=" * 60)
    logger.info("ENTITY MATCHING REPORT")
    logger.info("=" * 60)
    logger.info("Total articles before matching : %d", total_before)
    logger.info("Total rows after matching      : %d", total_after)
    logger.info("UNKNOWN articles               : %d (%.1f%%)", unknown_count, unknown_rate)

    # Articles per ticker per source
    if not matched_df.empty:
        pivot = (
            matched_df.groupby(["ticker", "source"])
            .size()
            .unstack(fill_value=0)
        )
        logger.info("\nArticles per ticker per source:")
        logger.info("\n%s", pivot.to_string())

    # Warning for tickers with <20 articles per year (Req 3.7)
    if not matched_df.empty and "date" in matched_df.columns:
        df_known = matched_df[matched_df["ticker"] != "UNKNOWN"].copy()
        if not df_known.empty:
            df_known["year"] = pd.to_datetime(
                df_known["date"], errors="coerce"
            ).dt.year
            yearly = df_known.groupby(["ticker", "year"]).size().reset_index(name="count")
            low = yearly[yearly["count"] < 20]
            if not low.empty:
                logger.warning(
                    "\nTickers with <20 articles in a year:"
                )
                for _, r in low.iterrows():
                    logger.warning(
                        "  %s in %d: %d articles", r["ticker"], int(r["year"]), r["count"]
                    )

    logger.info("=" * 60)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def run_matching() -> pd.DataFrame:
    """Execute the full entity matching pipeline.

    1. Load aliases from config/entity_aliases.json
    2. Load all raw news articles
    3. Match entities
    4. Save matched output
    5. Generate report

    Returns:
        The matched DataFrame.
    """
    logger = setup_logger("TASK_3")
    logger.info("Starting Entity Matching (TASK 3)...")

    # Load aliases
    aliases = load_aliases()
    logger.info("Loaded aliases for %d tickers.", len(aliases))

    # Load all news
    articles = _load_all_news(logger)
    total_before = len(articles)

    if articles.empty:
        logger.warning("No articles to match. Saving empty output.")
        empty = pd.DataFrame(columns=OUTPUT_COLUMNS)
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        empty.to_csv(OUTPUT_PATH, index=False)
        return empty

    # Match
    matched = match_entities(articles, aliases, logger=logger)

    # Save (Req 3.6)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    matched.to_csv(OUTPUT_PATH, index=False)
    logger.info("Saved matched output to %s (%d rows).", OUTPUT_PATH, len(matched))

    # Report (Req 3.7)
    generate_matching_report(total_before, matched, logger)

    return matched


if __name__ == "__main__":
    run_matching()
