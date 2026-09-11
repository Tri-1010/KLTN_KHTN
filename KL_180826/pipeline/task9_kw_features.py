"""
TASK 9: Keyword_Feature_Extractor
Extract keyword frequency features (raw, normalized, TF-IDF, sentiment).

Steps:
    1. For each (ticker, quarter_id) and keyword k: compute raw count kw_{k}
       and normalized count kw_norm_{k} = raw_count / news_count  (Req 9.1)
    2. Compute aggregate sentiment scores: pos_score, neg_score,
       sentiment_ratio  (Req 9.2)
    3. Compute TF-IDF features using TfidfVectorizer(vocabulary=..., min_df=2)
       fitted on the full corpus  (Req 9.3)
    4. Add coverage features: news_count, news_count_log, has_min_news  (Req 9.4)
    5. Save to data/features/keyword_features.csv  (Req 9.5)
    6. Generate keyword feature report: total features, top 20 keywords,
       sparsity rate, pos/neg score distributions  (Req 9.6)
    7. Log keywords with sparsity > 95% as removal candidates  (Req 9.7)
    8. Keep sparse features as-is (not imputed)  (Req 9.8)

Inputs:
    data/aggregated/news_by_quarter.csv
    config/keywords_finance.json  (or imported from task8_keywords)

Output:
    data/features/keyword_features.csv
"""

import math
import os
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from pipeline.logging_config import setup_logger
from pipeline.task8_keywords import get_all_keywords_flat, get_curated_keywords

# ---------------------------------------------------------------------------
# Constants / Paths
# ---------------------------------------------------------------------------

NEWS_BY_QUARTER_PATH = "data/aggregated/news_by_quarter.csv"
OUTPUT_PATH = "data/features/keyword_features.csv"


# ---------------------------------------------------------------------------
# 14.1 — Raw and normalized keyword counts (Req 9.1)
# ---------------------------------------------------------------------------


def _normalize_for_matching(text: str) -> str:
    """Normalize text for keyword substring matching.

    underthesea joins compound words with underscores (e.g. "lợi_nhuận"),
    and it does so inconsistently across multi-word phrases. The curated
    keywords are stored in space-separated form (e.g. "lợi nhuận tăng").

    To match reliably regardless of how underthesea segmented the text,
    we replace underscores with spaces and collapse repeated whitespace on
    both the text and the keyword before comparison.

    Args:
        text: Any text or keyword string.

    Returns:
        Lowercased, underscore-normalized, whitespace-collapsed string.
    """
    if not isinstance(text, str):
        return ""
    normalized = text.lower().replace("_", " ")
    return " ".join(normalized.split())


#: Sentinel character used to mask matched keyword spans. It never appears
#: in normalized financial text (which is lowercased Vietnamese words and
#: spaces), so masked regions can never be re-matched by shorter keywords.
_MASK_CHAR = "\x00"


def compute_raw_counts(
    combined_text: str,
    keywords: List[str],
) -> Dict[str, int]:
    """Count occurrences of each keyword in *combined_text* with longest-first masking.

    Uses case-insensitive substring matching after normalizing underscores
    to spaces, so that multi-word keywords match text tokenized by
    underthesea (which joins some compound words with underscores).

    **Longest-first masking** prevents double-counting when one keyword is a
    substring of another with the *opposite* sentiment. For example the
    negative phrase ``"không tăng trưởng"`` ("no growth") contains the
    positive phrase ``"tăng trưởng"`` ("growth"). A naive substring count
    would credit both the negative and the positive keyword for the same
    span of text, cancelling out or even flipping the true signal.

    To avoid this we:

    1. Sort keywords by normalized length, longest first.
    2. Count occurrences of each keyword in the (progressively masked) text.
    3. Blank out every matched span with a sentinel character so that
       shorter keywords contained inside it can no longer match.

    Thus ``"lợi nhuận không tăng"`` counts only the negative keyword
    ``"lợi nhuận không tăng"`` (or ``"không tăng"``) and never the positive
    ``"tăng"``-based phrases hidden inside it.

    Args:
        combined_text: Concatenated tokenized text for a (ticker, quarter).
        keywords: Flat list of all curated keywords.

    Returns:
        Dict mapping keyword → raw count.
    """
    counts: Dict[str, int] = {kw: 0 for kw in keywords}

    text_norm = _normalize_for_matching(combined_text)
    if not text_norm:
        return counts

    # Pre-normalize every keyword once.
    norm_map = {kw: _normalize_for_matching(kw) for kw in keywords}

    # Process longest keywords first so that a longer phrase claims (and
    # masks) its span before any shorter substring keyword can match it.
    ordered = sorted(
        (kw for kw in keywords if norm_map[kw]),
        key=lambda k: len(norm_map[k]),
        reverse=True,
    )

    masked = text_norm
    for kw in ordered:
        pattern = norm_map[kw]
        occurrences = masked.count(pattern)
        if occurrences:
            counts[kw] = occurrences
            # Mask each matched span so shorter keywords inside it cannot
            # re-match. ``str.replace`` replaces the same non-overlapping
            # occurrences that ``str.count`` reported.
            masked = masked.replace(pattern, _MASK_CHAR * len(pattern))

    return counts


def compute_keyword_counts(
    df: pd.DataFrame,
    keywords: List[str],
) -> pd.DataFrame:
    """Add raw count and normalized count columns for every keyword.

    For each row (ticker, quarter_id):
        - ``kw_{k}``      = raw count of keyword *k* in combined_text
        - ``kw_norm_{k}``  = kw_{k} / news_count

    Args:
        df: DataFrame with columns [ticker, quarter_id, news_count, combined_text].
        keywords: Flat list of all curated keywords.

    Returns:
        DataFrame with original columns plus kw_* and kw_norm_* columns.
    """
    result = df.copy()

    # Pre-compute raw counts for every row
    raw_records: List[Dict[str, int]] = []
    for _, row in result.iterrows():
        raw_records.append(compute_raw_counts(row.get("combined_text", ""), keywords))

    # Build raw-count frame. When there are no rows, construct an empty
    # frame that still has all keyword columns so downstream column access
    # (raw_df[kw]) does not raise KeyError on an empty corpus.
    if raw_records:
        raw_df = pd.DataFrame(raw_records, index=result.index)
    else:
        raw_df = pd.DataFrame(columns=keywords, index=result.index)

    # Add kw_{k} columns
    for kw in keywords:
        col_raw = f"kw_{kw}"
        result[col_raw] = raw_df[kw]

    # Add kw_norm_{k} columns (raw / news_count)
    for kw in keywords:
        col_raw = f"kw_{kw}"
        col_norm = f"kw_norm_{kw}"
        result[col_norm] = result[col_raw] / result["news_count"].replace(0, np.nan)
        # If news_count is 0, normalized count stays NaN — that's fine (Req 9.8)

    return result


# ---------------------------------------------------------------------------
# 14.2 — Aggregate sentiment scores (Req 9.2)
# ---------------------------------------------------------------------------


def compute_sentiment_scores(
    df: pd.DataFrame,
    keywords_by_direction: Dict[str, List[str]],
) -> pd.DataFrame:
    """Add pos_score, neg_score, and sentiment_ratio columns.

    - ``pos_score``  = sum of kw_norm_{k} for all positive keywords
    - ``neg_score``  = sum of kw_norm_{k} for all negative keywords
    - ``sentiment_ratio`` = (pos - neg) / (pos + neg + 1e-6)

    Args:
        df: DataFrame already containing kw_norm_* columns.
        keywords_by_direction: Dict with keys "positive", "negative", "neutral".

    Returns:
        DataFrame with three new columns appended.
    """
    result = df.copy()

    pos_cols = [f"kw_norm_{kw}" for kw in keywords_by_direction.get("positive", [])]
    neg_cols = [f"kw_norm_{kw}" for kw in keywords_by_direction.get("negative", [])]

    # Use fillna(0) so that NaN normalized values don't propagate
    result["pos_score"] = result[pos_cols].fillna(0).sum(axis=1)
    result["neg_score"] = result[neg_cols].fillna(0).sum(axis=1)
    result["sentiment_ratio"] = (
        (result["pos_score"] - result["neg_score"])
        / (result["pos_score"] + result["neg_score"] + 1e-6)
    )

    return result


# ---------------------------------------------------------------------------
# 14.3 — TF-IDF features (Req 9.3)
# ---------------------------------------------------------------------------


def compute_tfidf_features(
    df: pd.DataFrame,
    keywords: List[str],
) -> pd.DataFrame:
    """Compute TF-IDF weights for each keyword using the full corpus.

    Uses ``TfidfVectorizer(vocabulary=keywords, min_df=2)`` fitted on the
    ``combined_text`` column.  Resulting columns are named ``tfidf_{k}``.

    Args:
        df: DataFrame with a ``combined_text`` column.
        keywords: Flat list of all curated keywords.

    Returns:
        DataFrame with tfidf_* columns appended.
    """
    result = df.copy()

    corpus = result["combined_text"].fillna("").tolist()

    # Build vocabulary mapping (keyword → index)
    vocab = {kw: i for i, kw in enumerate(keywords)}

    vectorizer = TfidfVectorizer(
        vocabulary=vocab,
        min_df=2,
        token_pattern=r"(?u)\b\w[\w ]+\b",  # allow spaces inside tokens
        lowercase=True,
    )

    # TfidfVectorizer with a fixed vocabulary and multi-word terms:
    # The default tokenizer splits on whitespace, so multi-word keywords
    # won't match.  We work around this by using the raw TF-IDF on the
    # combined_text directly.  For multi-word keywords we compute TF-IDF
    # manually using the raw counts already available.
    #
    # Strategy: compute TF-IDF from raw counts + IDF from corpus.
    # IDF_k = log((1 + n) / (1 + df_k)) + 1  (sklearn default smooth_idf)
    # where df_k = number of documents containing keyword k.

    n_docs = len(corpus)

    # Document frequency for each keyword (underscore-normalized matching)
    norm_corpus = [_normalize_for_matching(doc) for doc in corpus]
    doc_freq: Dict[str, int] = {kw: 0 for kw in keywords}
    for doc_norm in norm_corpus:
        for kw in keywords:
            if _normalize_for_matching(kw) in doc_norm:
                doc_freq[kw] += 1

    # IDF (sklearn smooth formula)
    idf: Dict[str, float] = {}
    for kw in keywords:
        df_k = doc_freq[kw]
        idf[kw] = math.log((1 + n_docs) / (1 + df_k)) + 1

    # For each row, compute TF-IDF = (raw_count / doc_length) * IDF
    # Apply min_df=2 filter: if df_k < 2, set tfidf to 0
    for kw in keywords:
        col_raw = f"kw_{kw}"
        col_tfidf = f"tfidf_{kw}"

        if doc_freq[kw] < 2:
            result[col_tfidf] = 0.0
        else:
            # Term frequency = raw count / total tokens in document
            doc_lengths = result["combined_text"].fillna("").apply(
                lambda t: max(len(t.split()), 1)
            )
            result[col_tfidf] = (result[col_raw] / doc_lengths) * idf[kw]

    return result


# ---------------------------------------------------------------------------
# 14.4 — Coverage features (Req 9.4)
# ---------------------------------------------------------------------------


def add_coverage_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add news coverage features.

    - ``news_count``     — already present, kept as-is
    - ``news_count_log`` — log(news_count + 1)
    - ``has_min_news``   — 1 if news_count >= 5 else 0

    Args:
        df: DataFrame with a ``news_count`` column.

    Returns:
        DataFrame with coverage columns added.
    """
    result = df.copy()
    result["news_count_log"] = np.log(result["news_count"] + 1)
    result["has_min_news"] = (result["news_count"] >= 5).astype(int)
    return result


# ---------------------------------------------------------------------------
# 14.5 — Report and sparsity handling (Req 9.6, 9.7, 9.8)
# ---------------------------------------------------------------------------


def compute_sparsity_rate(
    df: pd.DataFrame,
    keywords: List[str],
) -> Tuple[float, Dict[str, float]]:
    """Compute overall and per-keyword sparsity rates.

    Sparsity = percentage of zero-valued cells among all kw_{k} columns.

    Args:
        df: DataFrame with kw_* columns.
        keywords: Flat keyword list.

    Returns:
        (overall_sparsity, per_keyword_sparsity) where per_keyword_sparsity
        maps keyword → fraction of rows with kw_{k} == 0.
    """
    kw_cols = [f"kw_{kw}" for kw in keywords]
    kw_data = df[kw_cols]

    total_cells = kw_data.size
    zero_cells = (kw_data == 0).sum().sum()
    overall = zero_cells / total_cells if total_cells > 0 else 0.0

    per_kw: Dict[str, float] = {}
    n_rows = len(df)
    for kw in keywords:
        col = f"kw_{kw}"
        if n_rows > 0:
            per_kw[kw] = (df[col] == 0).sum() / n_rows
        else:
            per_kw[kw] = 0.0

    return overall, per_kw


def generate_keyword_feature_report(
    df: pd.DataFrame,
    keywords: List[str],
    keywords_by_direction: Dict[str, List[str]],
    logger,
) -> None:
    """Print keyword feature extraction report (Req 9.6, 9.7).

    Reports:
    - Total features generated
    - Top 20 keywords by corpus frequency (sum of kw_{k})
    - Overall sparsity rate
    - pos_score and neg_score distribution statistics
    - Keywords with sparsity > 95% (removal candidates)

    Args:
        df: Final feature DataFrame.
        keywords: Flat keyword list.
        keywords_by_direction: Dict with positive/negative/neutral lists.
        logger: Logger instance.
    """
    logger.info("=" * 70)
    logger.info("KEYWORD FEATURE REPORT")
    logger.info("=" * 70)

    # --- Total features ---
    feature_cols = [
        c for c in df.columns if c not in ("ticker", "quarter_id", "combined_text")
    ]
    logger.info("Total features generated: %d", len(feature_cols))

    # --- Top 20 keywords by frequency ---
    kw_sums: Dict[str, float] = {}
    for kw in keywords:
        col = f"kw_{kw}"
        if col in df.columns:
            kw_sums[kw] = df[col].sum()
    top20 = sorted(kw_sums.items(), key=lambda x: x[1], reverse=True)[:20]
    logger.info("\nTop 20 keywords by corpus frequency:")
    for rank, (kw, total) in enumerate(top20, 1):
        logger.info("  %2d. %-40s  %.0f", rank, kw, total)

    # --- Sparsity ---
    overall_sparsity, per_kw_sparsity = compute_sparsity_rate(df, keywords)
    logger.info("\nOverall sparsity rate: %.2f%%", overall_sparsity * 100)

    # Keywords with sparsity > 95% (Req 9.7)
    high_sparsity = {
        kw: sp for kw, sp in per_kw_sparsity.items() if sp > 0.95
    }
    if high_sparsity:
        logger.info(
            "\nKeywords with sparsity > 95%% (%d candidates for removal):",
            len(high_sparsity),
        )
        for kw, sp in sorted(high_sparsity.items(), key=lambda x: x[1], reverse=True):
            logger.info("  %-40s  %.1f%%", kw, sp * 100)
    else:
        logger.info("\nNo keywords with sparsity > 95%%.")

    # --- pos_score / neg_score distributions ---
    if "pos_score" in df.columns:
        logger.info("\npos_score distribution:")
        logger.info("  mean=%.4f  std=%.4f  min=%.4f  max=%.4f",
                     df["pos_score"].mean(), df["pos_score"].std(),
                     df["pos_score"].min(), df["pos_score"].max())
    if "neg_score" in df.columns:
        logger.info("neg_score distribution:")
        logger.info("  mean=%.4f  std=%.4f  min=%.4f  max=%.4f",
                     df["neg_score"].mean(), df["neg_score"].std(),
                     df["neg_score"].min(), df["neg_score"].max())

    logger.info("=" * 70)


# ---------------------------------------------------------------------------
# Main extraction function
# ---------------------------------------------------------------------------


def extract_keyword_features(
    df: pd.DataFrame,
    keywords_by_direction: Optional[Dict[str, List[str]]] = None,
) -> pd.DataFrame:
    """Compute all keyword features for the given news-by-quarter data.

    This is the core function for TASK 9.  It:

    1. Computes raw and normalized keyword counts (Req 9.1)
    2. Computes aggregate sentiment scores (Req 9.2)
    3. Computes TF-IDF features (Req 9.3)
    4. Adds coverage features (Req 9.4)

    Args:
        df: DataFrame with columns [ticker, quarter_id, news_count, combined_text].
        keywords_by_direction: Optional dict with keys "positive", "negative",
            "neutral".  If ``None``, loaded from :func:`get_curated_keywords`.

    Returns:
        DataFrame with columns: ticker, quarter_id, all feature columns.
        The ``combined_text`` column is dropped from the output.
    """
    if keywords_by_direction is None:
        keywords_by_direction = get_curated_keywords()

    all_keywords = (
        keywords_by_direction.get("positive", [])
        + keywords_by_direction.get("negative", [])
        + keywords_by_direction.get("neutral", [])
    )

    # Step 1: Raw + normalized counts (Req 9.1)
    result = compute_keyword_counts(df, all_keywords)

    # Step 2: Sentiment scores (Req 9.2)
    result = compute_sentiment_scores(result, keywords_by_direction)

    # Step 3: TF-IDF (Req 9.3)
    result = compute_tfidf_features(result, all_keywords)

    # Step 4: Coverage features (Req 9.4)
    result = add_coverage_features(result)

    # Drop combined_text from output (not a feature)
    if "combined_text" in result.columns:
        result = result.drop(columns=["combined_text"])

    return result


# ---------------------------------------------------------------------------
# Pipeline entry point
# ---------------------------------------------------------------------------


def run_keyword_feature_extraction() -> pd.DataFrame:
    """Execute TASK 9: Keyword Feature Extraction.

    Loads ``data/aggregated/news_by_quarter.csv``, computes all keyword
    features, saves to ``data/features/keyword_features.csv``, and prints
    the feature report.

    Returns:
        The keyword features DataFrame.
    """
    logger = setup_logger("TASK_9")
    logger.info("Starting Keyword Feature Extraction (TASK 9)...")

    # ------------------------------------------------------------------
    # Load input
    # ------------------------------------------------------------------
    if not os.path.isfile(NEWS_BY_QUARTER_PATH):
        logger.error("Input file not found: %s", NEWS_BY_QUARTER_PATH)
        return pd.DataFrame()

    df = pd.read_csv(NEWS_BY_QUARTER_PATH, encoding="utf-8")
    logger.info("Loaded %d (ticker, quarter) rows from %s.", len(df), NEWS_BY_QUARTER_PATH)

    # Ensure required columns
    required = {"ticker", "quarter_id", "news_count", "combined_text"}
    missing = required - set(df.columns)
    if missing:
        logger.error("Missing required columns: %s", missing)
        return pd.DataFrame()

    # ------------------------------------------------------------------
    # Load keywords
    # ------------------------------------------------------------------
    keywords_by_direction = get_curated_keywords()
    all_keywords = get_all_keywords_flat()
    logger.info(
        "Using %d keywords (%d pos, %d neg, %d neutral).",
        len(all_keywords),
        len(keywords_by_direction["positive"]),
        len(keywords_by_direction["negative"]),
        len(keywords_by_direction["neutral"]),
    )

    # ------------------------------------------------------------------
    # Extract features
    # ------------------------------------------------------------------
    result = extract_keyword_features(df, keywords_by_direction)

    # ------------------------------------------------------------------
    # Save output (Req 9.5)
    # ------------------------------------------------------------------
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    result.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    logger.info("Saved keyword features (%d rows, %d cols) to %s.",
                len(result), len(result.columns), OUTPUT_PATH)

    # ------------------------------------------------------------------
    # Report (Req 9.6, 9.7, 9.8)
    # ------------------------------------------------------------------
    generate_keyword_feature_report(result, all_keywords, keywords_by_direction, logger)

    logger.info("TASK 9 complete.")
    return result


if __name__ == "__main__":
    run_keyword_feature_extraction()
