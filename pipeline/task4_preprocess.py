"""
TASK 4: Text_Preprocessor
Clean, tokenize, and deduplicate Vietnamese news text.

Steps:
    1. Clean text: lowercase, remove HTML/URLs/special chars, preserve numeric tokens
    2. Tokenize using underthesea (with whitespace fallback)
    3. Remove stopwords (standard Vietnamese + custom financial)
    4. Deduplicate by URL and fuzzy title similarity
    5. Exclude short articles (<5 tokens)
    6. Save processed output and generate report

Outputs:
    data/news/processed/all_news_processed.csv
"""

import logging
import math
import os
import re
import unicodedata
from collections import Counter
from multiprocessing import Pool, cpu_count
from typing import List, Optional, Set, Tuple

import pandas as pd
from rapidfuzz import fuzz

from pipeline.logging_config import setup_logger

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INPUT_PATH = "data/news/matched/all_news_matched.csv"
OUTPUT_PATH = "data/news/processed/all_news_processed.csv"
STOPWORDS_PATH = "config/stopwords_finance.txt"

# Threshold for multiprocessing (Req 4.5)
MULTIPROCESSING_THRESHOLD = 10_000

# Fuzzy similarity threshold for deduplication (Req 4.6)
FUZZY_SIMILARITY_THRESHOLD = 90

# Minimum token count to keep an article (Req 4.9)
MIN_TOKEN_COUNT = 5

# ---------------------------------------------------------------------------
# Stopword loading
# ---------------------------------------------------------------------------


def load_stopwords(path: str = STOPWORDS_PATH) -> Set[str]:
    """Load stopwords from a text file.

    Each line is one stopword. Lines starting with ``#`` are comments.
    Blank lines are ignored.

    Args:
        path: Path to the stopwords file.

    Returns:
        Set of stopword strings (lowercased).
    """
    stopwords: Set[str] = set()
    if not os.path.isfile(path):
        return stopwords

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            stopwords.add(line.lower())
    return stopwords


# ---------------------------------------------------------------------------
# Text cleaning (Req 4.1, 4.2)
# ---------------------------------------------------------------------------

# Regex patterns compiled once for performance
_RE_HTML_TAGS = re.compile(r"<[^>]+>")
_RE_URLS = re.compile(r"https?://\S+|www\.\S+")
# Remove special characters but preserve: letters, digits, whitespace,
# Vietnamese diacritics, percent sign (for "20%"), period and comma (for numbers)
_RE_SPECIAL_CHARS = re.compile(r"[^\w\s%.,àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]", re.UNICODE)
# Collapse multiple spaces
_RE_MULTI_SPACE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Clean a single text string for Vietnamese NLP processing.

    Steps:
        1. Convert to lowercase
        2. Remove HTML tags
        3. Remove URLs
        4. Remove special characters (preserving numeric tokens like "20%", "500 tỷ")
        5. Normalize Vietnamese diacritics (NFC normalization)
        6. Collapse whitespace

    Args:
        text: Raw text string.

    Returns:
        Cleaned text string.
    """
    if not text or not isinstance(text, str):
        return ""

    # Lowercase
    text = text.lower()

    # Remove HTML tags
    text = _RE_HTML_TAGS.sub(" ", text)

    # Remove URLs
    text = _RE_URLS.sub(" ", text)

    # Remove special characters (preserve letters, digits, whitespace, %, ., ,)
    text = _RE_SPECIAL_CHARS.sub(" ", text)

    # Normalize Vietnamese diacritics to NFC form
    text = unicodedata.normalize("NFC", text)

    # Collapse whitespace
    text = _RE_MULTI_SPACE.sub(" ", text).strip()

    return text


def prepare_text_clean(title: str, description: str) -> str:
    """Concatenate title and description, then clean.

    Requirement 4.2: Concatenate title + description into single text_clean field.

    Args:
        title: Article title.
        description: Article description/summary.

    Returns:
        Cleaned concatenated text.
    """
    title = str(title) if pd.notna(title) else ""
    description = str(description) if pd.notna(description) else ""
    combined = f"{title} {description}".strip()
    return clean_text(combined)


# ---------------------------------------------------------------------------
# Vietnamese tokenization (Req 4.3, 4.5)
# ---------------------------------------------------------------------------


def tokenize_vi(text: str, logger: Optional[logging.Logger] = None) -> str:
    """Tokenize Vietnamese text using underthesea with whitespace fallback.

    Uses ``underthesea.word_tokenize(text, format="text")`` for proper
    Vietnamese word segmentation. Falls back to simple whitespace splitting
    if underthesea fails for a specific article.

    Args:
        text: Cleaned text to tokenize.
        logger: Optional logger for fallback events.

    Returns:
        Tokenized text (space-separated tokens).
    """
    if not text or not isinstance(text, str):
        return ""

    try:
        from underthesea import word_tokenize
        result = word_tokenize(text, format="text")
        return result if result else ""
    except Exception as exc:
        if logger:
            logger.warning("underthesea tokenization failed, using whitespace fallback: %s", exc)
        # Fallback: simple whitespace splitting
        return " ".join(text.split())


def _tokenize_single(text: str) -> str:
    """Wrapper for multiprocessing — tokenize without logger."""
    return tokenize_vi(text, logger=None)


def tokenize_batch(
    texts: List[str],
    logger: Optional[logging.Logger] = None,
) -> List[str]:
    """Tokenize a batch of texts, using multiprocessing for large batches.

    Requirement 4.5: Use multiprocessing for batches >10,000 articles.

    Args:
        texts: List of cleaned text strings.
        logger: Optional logger.

    Returns:
        List of tokenized text strings.
    """
    if len(texts) > MULTIPROCESSING_THRESHOLD:
        if logger:
            logger.info(
                "Using multiprocessing for %d articles (threshold=%d).",
                len(texts),
                MULTIPROCESSING_THRESHOLD,
            )
        n_workers = max(1, cpu_count() - 1)
        with Pool(processes=n_workers) as pool:
            results = pool.map(_tokenize_single, texts)
        return results
    else:
        return [tokenize_vi(t, logger=logger) for t in texts]


# ---------------------------------------------------------------------------
# Stopword removal (Req 4.4)
# ---------------------------------------------------------------------------


def remove_stopwords(text: str, stopwords: Set[str]) -> str:
    """Remove stopwords from tokenized Vietnamese text.

    Handles both single-word and multi-word stopwords. Multi-word stopwords
    (containing underscores from underthesea tokenization) are matched first,
    then single-word stopwords are removed.

    Args:
        text: Tokenized text (space-separated tokens, may contain underscores
              for compound words from underthesea).
        stopwords: Set of stopword strings.

    Returns:
        Text with stopwords removed.
    """
    if not text or not stopwords:
        return text

    # Separate multi-word and single-word stopwords
    # underthesea uses underscores for compound words: "công_ty", "doanh_nghiệp"
    multi_word_stopwords = set()
    single_word_stopwords = set()

    for sw in stopwords:
        # Convert space-separated stopword to underscore form (underthesea format)
        underscore_form = sw.replace(" ", "_")
        if "_" in underscore_form:
            multi_word_stopwords.add(underscore_form)
        single_word_stopwords.add(sw)
        # Also add the underscore form as a single token to match
        if underscore_form != sw:
            single_word_stopwords.add(underscore_form)

    tokens = text.split()
    filtered = [t for t in tokens if t.lower() not in single_word_stopwords]

    return " ".join(filtered)


# ---------------------------------------------------------------------------
# Deduplication (Req 4.6)
# ---------------------------------------------------------------------------


def deduplicate_by_url(df: pd.DataFrame, logger: Optional[logging.Logger] = None) -> pd.DataFrame:
    """Remove articles with identical URLs.

    Keeps the first occurrence (earliest in the DataFrame).

    Args:
        df: DataFrame with a ``url`` column.
        logger: Optional logger.

    Returns:
        Deduplicated DataFrame.
    """
    before = len(df)
    df = df.drop_duplicates(subset=["url"], keep="first").reset_index(drop=True)
    after = len(df)
    if logger and before != after:
        logger.info("URL deduplication: %d → %d (removed %d duplicates).", before, after, before - after)
    return df


def deduplicate_by_fuzzy_title(
    df: pd.DataFrame,
    threshold: int = FUZZY_SIMILARITY_THRESHOLD,
    logger: Optional[logging.Logger] = None,
) -> pd.DataFrame:
    """Flag and remove articles with >threshold% fuzzy title similarity.

    Retains the article with the earliest publication date among similar pairs.
    Uses rapidfuzz for fast fuzzy matching.

    Args:
        df: DataFrame with ``title`` and ``date`` columns.
        threshold: Similarity threshold (0-100). Default 90.
        logger: Optional logger.

    Returns:
        DataFrame with near-duplicate titles removed.
    """
    if df.empty or len(df) < 2:
        return df

    # Ensure date is parsed for comparison
    df = df.copy()
    df["_date_parsed"] = pd.to_datetime(df["date"], errors="coerce")

    # Sort by date so earliest comes first
    df = df.sort_values("_date_parsed", na_position="last").reset_index(drop=True)

    titles = df["title"].fillna("").tolist()
    to_remove: set = set()

    # Compare each pair — O(n²) but necessary for fuzzy matching
    # For large datasets, we only compare within reasonable windows
    n = len(titles)
    for i in range(n):
        if i in to_remove:
            continue
        for j in range(i + 1, min(i + 500, n)):  # Limit comparison window
            if j in to_remove:
                continue
            if not titles[i] or not titles[j]:
                continue
            similarity = fuzz.ratio(titles[i], titles[j])
            if similarity > threshold:
                # Remove the later one (j), keep earlier (i)
                to_remove.add(j)
                if logger:
                    logger.debug(
                        "Fuzzy duplicate (%.0f%%): '%s' ≈ '%s'",
                        similarity,
                        titles[i][:60],
                        titles[j][:60],
                    )

    before = len(df)
    df = df.drop(index=list(to_remove)).reset_index(drop=True)
    df = df.drop(columns=["_date_parsed"], errors="ignore")
    after = len(df)

    if logger:
        logger.info(
            "Fuzzy title deduplication: %d → %d (removed %d near-duplicates, threshold=%d%%).",
            before, after, before - after, threshold,
        )

    return df


# ---------------------------------------------------------------------------
# Preprocessing report (Req 4.8)
# ---------------------------------------------------------------------------


def generate_preprocessing_report(
    count_before_dedup: int,
    count_after_dedup: int,
    df: pd.DataFrame,
    logger: logging.Logger,
) -> None:
    """Generate and log the preprocessing report.

    Reports:
        - Article count before/after deduplication
        - Average token count per article
        - Top 50 frequent tokens after stopword removal
        - Warning for articles with <5 tokens

    Args:
        count_before_dedup: Article count before deduplication.
        count_after_dedup: Article count after deduplication.
        df: Final processed DataFrame with ``text_tokenized`` column.
        logger: Logger instance.
    """
    logger.info("=" * 60)
    logger.info("TEXT PREPROCESSING REPORT")
    logger.info("=" * 60)
    logger.info("Articles before deduplication : %d", count_before_dedup)
    logger.info("Articles after deduplication  : %d", count_after_dedup)
    logger.info("Articles in final output      : %d", len(df))

    if df.empty or "text_tokenized" not in df.columns:
        logger.info("No articles to analyze.")
        logger.info("=" * 60)
        return

    # Average token count
    token_counts = df["text_tokenized"].fillna("").apply(lambda x: len(x.split()) if x else 0)
    avg_tokens = token_counts.mean()
    logger.info("Average token count per article: %.1f", avg_tokens)

    # Warn for articles with <5 tokens
    short_articles = token_counts[token_counts < MIN_TOKEN_COUNT]
    if len(short_articles) > 0:
        logger.warning(
            "%d articles have fewer than %d tokens.",
            len(short_articles),
            MIN_TOKEN_COUNT,
        )

    # Top 50 frequent tokens
    all_tokens: Counter = Counter()
    for text in df["text_tokenized"].fillna(""):
        if text:
            all_tokens.update(text.split())

    logger.info("\nTop 50 most frequent tokens:")
    for token, count in all_tokens.most_common(50):
        logger.info("  %-30s %d", token, count)

    logger.info("=" * 60)


# ---------------------------------------------------------------------------
# Main preprocessing pipeline
# ---------------------------------------------------------------------------


def preprocess_text(
    title: str,
    description: str,
    stopwords: Set[str],
    logger: Optional[logging.Logger] = None,
) -> Tuple[str, str]:
    """Clean and tokenize a single article's text.

    Steps: concatenate → clean → tokenize → remove stopwords.

    Args:
        title: Article title.
        description: Article description.
        stopwords: Set of stopwords to remove.
        logger: Optional logger for fallback events.

    Returns:
        Tuple of (text_clean, text_tokenized).
    """
    text_clean = prepare_text_clean(title, description)
    text_tokenized = tokenize_vi(text_clean, logger=logger)
    text_tokenized = remove_stopwords(text_tokenized, stopwords)
    return text_clean, text_tokenized


def run_preprocessing() -> pd.DataFrame:
    """Execute the full text preprocessing pipeline.

    1. Load matched news articles
    2. Clean text (concatenate title + description)
    3. Tokenize using underthesea (with fallback)
    4. Remove stopwords
    5. Deduplicate by URL and fuzzy title similarity
    6. Exclude articles with <5 tokens
    7. Save processed output
    8. Generate report

    Returns:
        The processed DataFrame.
    """
    logger = setup_logger("TASK_4")
    logger.info("Starting Text Preprocessing (TASK 4)...")

    # Load input
    if not os.path.isfile(INPUT_PATH):
        logger.error("Input file not found: %s", INPUT_PATH)
        return pd.DataFrame()

    df = pd.read_csv(INPUT_PATH, encoding="utf-8")
    logger.info("Loaded %d articles from %s.", len(df), INPUT_PATH)
    count_before_dedup = len(df)

    if df.empty:
        logger.warning("No articles to preprocess. Saving empty output with full schema.")
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        # Ensure downstream schema is consistent even with no articles:
        # always include the text_clean / text_tokenized columns.
        for col in ("text_clean", "text_tokenized"):
            if col not in df.columns:
                df[col] = pd.Series(dtype="object")
        df.to_csv(OUTPUT_PATH, index=False)
        return df

    # Load stopwords
    stopwords = load_stopwords(STOPWORDS_PATH)
    logger.info("Loaded %d stopwords from %s.", len(stopwords), STOPWORDS_PATH)

    # Step 1: Deduplicate by URL (Req 4.6)
    df = deduplicate_by_url(df, logger=logger)

    # Step 2: Fuzzy title deduplication (Req 4.6)
    df = deduplicate_by_fuzzy_title(df, logger=logger)
    count_after_dedup = len(df)

    # Step 3: Clean text — concatenate title + description (Req 4.1, 4.2)
    logger.info("Cleaning text...")
    df["text_clean"] = df.apply(
        lambda row: prepare_text_clean(row.get("title", ""), row.get("description", "")),
        axis=1,
    )

    # Step 4: Tokenize (Req 4.3, 4.5)
    logger.info("Tokenizing %d articles...", len(df))
    texts_to_tokenize = df["text_clean"].tolist()
    tokenized = tokenize_batch(texts_to_tokenize, logger=logger)
    df["text_tokenized"] = tokenized

    # Step 5: Remove stopwords (Req 4.4)
    logger.info("Removing stopwords...")
    df["text_tokenized"] = df["text_tokenized"].apply(
        lambda t: remove_stopwords(t, stopwords)
    )

    # Step 6: Exclude articles with <5 tokens (Req 4.9)
    token_counts = df["text_tokenized"].fillna("").apply(lambda x: len(x.split()) if x else 0)
    short_mask = token_counts < MIN_TOKEN_COUNT
    short_articles = df[short_mask]
    if not short_articles.empty:
        logger.warning(
            "Excluding %d articles with <%d tokens:",
            len(short_articles),
            MIN_TOKEN_COUNT,
        )
        for _, row in short_articles.iterrows():
            logger.warning("  URL: %s", row.get("url", "N/A"))
        df = df[~short_mask].reset_index(drop=True)

    # Step 7: Save output (Req 4.7)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    logger.info("Saved %d processed articles to %s.", len(df), OUTPUT_PATH)

    # Step 8: Generate report (Req 4.8)
    generate_preprocessing_report(count_before_dedup, count_after_dedup, df, logger)

    return df


if __name__ == "__main__":
    run_preprocessing()
