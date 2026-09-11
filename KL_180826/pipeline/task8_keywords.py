"""
TASK 8: Keyword_Builder
Build curated Vietnamese financial keyword list with sentiment direction.

Steps:
    1. Extract keyword candidates from corpus using CountVectorizer (top 500 unigrams, top 300 bigrams)
    2. Define curated keyword list organized into 6 thematic groups (A-F)
    3. Assign sentiment direction (positive / negative / neutral) to each keyword
    4. Save keyword lists to config/keywords_finance.json and config/keywords_by_group.json
    5. Print corpus frequency of each keyword for validation

Outputs:
    config/keyword_candidates.csv   (for manual review)
    config/keywords_finance.json    (flat: positive / negative / neutral)
    config/keywords_by_group.json   (grouped: A-F with direction)
"""

import json
import os
from collections import Counter
from typing import Any, Dict, List, Optional, Set

import pandas as pd

from pipeline.logging_config import setup_logger

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INPUT_PATH = "data/news/processed/all_news_processed.csv"
STOPWORDS_PATH = "config/stopwords_finance.txt"
CANDIDATES_PATH = "config/keyword_candidates.csv"
KEYWORDS_FINANCE_PATH = "config/keywords_finance.json"
KEYWORDS_BY_GROUP_PATH = "config/keywords_by_group.json"

# ---------------------------------------------------------------------------
# Curated keyword list — 6 thematic groups (Req 8.2)
# ---------------------------------------------------------------------------

KEYWORD_GROUPS: Dict[str, Dict[str, Any]] = {
    "A": {
        "name": "Kết quả kinh doanh",
        "positive": [
            "lợi nhuận tăng",
            "doanh thu tăng",
            "tăng trưởng mạnh",
            "vượt kế hoạch",
            "kỷ lục",
            "tăng trưởng",
            "lãi ròng",
            "lợi nhuận sau thuế tăng",
            "kết quả tích cực",
            "lãi khủng",
            "lãi lớn",
            "lãi đậm",
            "báo lãi",
            "lợi nhuận kỷ lục",
            "doanh thu kỷ lục",
            "lãi kỷ lục",
            "bứt phá",
            "tăng vọt",
            "tăng mạnh",
            "khởi sắc",
            "phục hồi",
            "lập đỉnh",
            "hoàn thành kế hoạch",
            "lợi nhuận cải thiện",
        ],
        "negative": [
            "lợi nhuận giảm",
            "doanh thu giảm",
            "lợi nhuận âm",
            "thua lỗ",
            "lỗ ròng",
            "dưới kế hoạch",
            "sụt giảm",
            "kết quả tiêu cực",
            "lợi nhuận thấp hơn",
            "báo lỗ",
            "lỗ nặng",
            "lỗ lớn",
            "lỗ kỷ lục",
            "lỗ lũy kế",
            "lao dốc",
            "giảm sâu",
            "giảm mạnh",
            "tụt dốc",
            "kinh doanh sa sút",
            "âm vốn chủ sở hữu",
            "lợi nhuận không tăng",
            "doanh thu không tăng",
            "không tăng trưởng",
            "tăng trưởng chậm lại",
            "không hoàn thành kế hoạch",
            "không đạt kế hoạch",
            "chưa có lãi",
        ],
    },
    "B": {
        "name": "Chính sách cổ đông",
        "positive": [
            "chia cổ tức",
            "cổ tức cao",
            "mua lại cổ phiếu",
            "phát hành thưởng",
            "tăng vốn điều lệ",
            "cổ tức tiền mặt",
        ],
        "negative": [
            "không chia cổ tức",
            "hủy cổ tức",
            "giảm cổ tức",
            "phát hành pha loãng",
            "chào bán giá thấp",
        ],
    },
    "C": {
        "name": "Tài chính doanh nghiệp",
        "positive": [
            "giảm nợ",
            "trả nợ",
            "cải thiện tài chính",
            "hệ số an toàn vốn",
            "dòng tiền dương",
            "tiền mặt dồi dào",
        ],
        "negative": [
            "nợ xấu",
            "nợ vay tăng",
            "áp lực tài chính",
            "nợ quá hạn",
            "hệ số nợ cao",
            "thiếu thanh khoản",
            "dòng tiền âm",
        ],
    },
    "D": {
        "name": "Hoạt động kinh doanh",
        "positive": [
            "ký kết hợp đồng",
            "mở rộng thị trường",
            "dự án mới",
            "đầu tư mới",
            "hợp tác chiến lược",
            "thắng thầu",
            "xuất khẩu tăng",
        ],
        "negative": [
            "hủy hợp đồng",
            "dự án trì hoãn",
            "thu hẹp hoạt động",
            "đóng cửa",
            "dừng dự án",
        ],
    },
    "E": {
        "name": "Rủi ro và pháp lý",
        "negative": [
            "bị phạt",
            "vi phạm",
            "bị thanh tra",
            "bị kiểm toán từ chối",
            "cảnh báo",
            "đình chỉ",
            "khởi tố",
            "điều tra",
            "tranh chấp pháp lý",
            "bị kiện",
        ],
    },
    "F": {
        "name": "Sự kiện doanh nghiệp trung tính",
        "neutral": [
            "đại hội cổ đông",
            "họp HĐQT",
            "thay đổi lãnh đạo",
            "thay CEO",
            "sáp nhập",
            "mua lại",
            "phát hành cổ phiếu mới",
            "niêm yết thêm",
            "thoái vốn",
        ],
    },
}


def get_curated_keywords() -> Dict[str, List[str]]:
    """Return the flat curated keyword list grouped by sentiment direction.

    Returns:
        Dictionary with keys ``"positive"``, ``"negative"``, ``"neutral"``,
        each mapping to a list of keyword strings.
    """
    result: Dict[str, List[str]] = {"positive": [], "negative": [], "neutral": []}
    for group_data in KEYWORD_GROUPS.values():
        for direction in ("positive", "negative", "neutral"):
            result[direction].extend(group_data.get(direction, []))
    return result


def get_all_keywords_flat() -> List[str]:
    """Return a flat list of all curated keywords (all directions)."""
    kw = get_curated_keywords()
    return kw["positive"] + kw["negative"] + kw["neutral"]


# ---------------------------------------------------------------------------
# Stopword loading (reuse from task4)
# ---------------------------------------------------------------------------


def _load_stopwords(path: str = STOPWORDS_PATH) -> Set[str]:
    """Load stopwords from text file. Lines starting with ``#`` are comments."""
    stopwords: Set[str] = set()
    if not os.path.isfile(path):
        return stopwords
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            stopwords.add(line.lower())
    return stopwords


# ---------------------------------------------------------------------------
# Task 13.1 — Keyword candidate extraction (Req 8.1)
# ---------------------------------------------------------------------------


def extract_candidates(
    corpus: List[str],
    stopwords: Optional[Set[str]] = None,
    top_unigrams: int = 500,
    top_bigrams: int = 300,
) -> pd.DataFrame:
    """Extract top unigrams and bigrams from the corpus using CountVectorizer.

    Args:
        corpus: List of tokenized text strings (one per document).
        stopwords: Optional set of stopwords to exclude.
        top_unigrams: Number of top unigrams to keep.
        top_bigrams: Number of top bigrams to keep.

    Returns:
        DataFrame with columns ``[term, ngram, count]`` sorted by count descending.
    """
    from sklearn.feature_extraction.text import CountVectorizer

    stop_list = list(stopwords) if stopwords else None

    # --- Unigrams ---
    vec_uni = CountVectorizer(
        ngram_range=(1, 1),
        stop_words=stop_list,
        max_features=top_unigrams,
        token_pattern=r"(?u)\b\w[\w_]+\b",
    )
    X_uni = vec_uni.fit_transform(corpus)
    uni_counts = X_uni.sum(axis=0).A1  # dense 1-D array
    uni_terms = vec_uni.get_feature_names_out()
    df_uni = pd.DataFrame({"term": uni_terms, "ngram": "unigram", "count": uni_counts})

    # --- Bigrams ---
    vec_bi = CountVectorizer(
        ngram_range=(2, 2),
        stop_words=stop_list,
        max_features=top_bigrams,
        token_pattern=r"(?u)\b\w[\w_]+\b",
    )
    X_bi = vec_bi.fit_transform(corpus)
    bi_counts = X_bi.sum(axis=0).A1
    bi_terms = vec_bi.get_feature_names_out()
    df_bi = pd.DataFrame({"term": bi_terms, "ngram": "bigram", "count": bi_counts})

    candidates = pd.concat([df_uni, df_bi], ignore_index=True)
    candidates = candidates.sort_values("count", ascending=False).reset_index(drop=True)
    return candidates


# ---------------------------------------------------------------------------
# Task 13.3 — Save keyword lists & frequency report (Req 8.3, 8.4, 8.5)
# ---------------------------------------------------------------------------


def save_keywords_finance(keywords: Dict[str, List[str]], path: str = KEYWORDS_FINANCE_PATH) -> None:
    """Save flat keyword list to JSON (positive / negative / neutral).

    Args:
        keywords: Dict with keys ``"positive"``, ``"negative"``, ``"neutral"``.
        path: Output file path.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(keywords, fh, ensure_ascii=False, indent=2)


def save_keywords_by_group(groups: Dict[str, Dict[str, Any]], path: str = KEYWORDS_BY_GROUP_PATH) -> None:
    """Save group-level keyword breakdown to JSON (groups A-F).

    Args:
        groups: The ``KEYWORD_GROUPS`` dictionary.
        path: Output file path.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(groups, fh, ensure_ascii=False, indent=2)


def compute_corpus_frequency(
    corpus: List[str],
    keywords: List[str],
) -> Dict[str, int]:
    """Count how many times each keyword appears across the entire corpus.

    For multi-word keywords the search is a simple substring match on each
    document (case-insensitive).  For single-word keywords the search counts
    token-level occurrences.

    Args:
        corpus: List of tokenized text strings.
        keywords: Flat list of all keywords.

    Returns:
        Dict mapping keyword → total corpus count.
    """
    freq: Dict[str, int] = {kw: 0 for kw in keywords}
    for doc in corpus:
        doc_lower = doc.lower()
        for kw in keywords:
            freq[kw] += doc_lower.count(kw.lower())
    return freq


def print_frequency_report(
    freq: Dict[str, int],
    keywords_by_direction: Dict[str, List[str]],
    logger,
) -> None:
    """Print corpus frequency of each keyword grouped by direction.

    Args:
        freq: Keyword → corpus count mapping.
        keywords_by_direction: Dict with keys positive / negative / neutral.
        logger: Logger instance.
    """
    logger.info("=" * 70)
    logger.info("KEYWORD CORPUS FREQUENCY REPORT")
    logger.info("=" * 70)

    for direction in ("positive", "negative", "neutral"):
        kws = keywords_by_direction.get(direction, [])
        if not kws:
            continue
        logger.info("\n--- %s keywords (%d) ---", direction.upper(), len(kws))
        for kw in sorted(kws, key=lambda k: freq.get(k, 0), reverse=True):
            logger.info("  %-40s %d", kw, freq.get(kw, 0))

    total = sum(freq.values())
    logger.info("\nTotal keyword occurrences in corpus: %d", total)
    zero_count = sum(1 for v in freq.values() if v == 0)
    logger.info("Keywords with zero occurrences: %d / %d", zero_count, len(freq))
    logger.info("=" * 70)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def build_keyword_list(corpus: Optional[List[str]] = None) -> Dict[str, List[str]]:
    """Build and save the curated financial keyword list.

    This is the main function for TASK 8.  It:

    1. Extracts keyword candidates from the corpus (if provided) using
       CountVectorizer — top 500 unigrams and top 300 bigrams — and saves
       them to ``config/keyword_candidates.csv`` for manual review (Req 8.1).
    2. Builds the curated keyword list from the hardcoded ``KEYWORD_GROUPS``
       constant, organized into 6 thematic groups A-F (Req 8.2).
    3. Saves the flat keyword list to ``config/keywords_finance.json``
       (Req 8.3) and the group-level breakdown to
       ``config/keywords_by_group.json`` (Req 8.4).
    4. Prints the corpus frequency of each keyword for validation (Req 8.5).

    Args:
        corpus: Optional list of tokenized text strings.  When ``None`` the
                function still saves the curated keyword lists but skips
                candidate extraction and frequency reporting.

    Returns:
        Dict ``{"positive": [...], "negative": [...], "neutral": [...]}``.
    """
    logger = setup_logger("TASK_8")
    logger.info("Starting Keyword Builder (TASK 8)...")

    # Load stopwords for candidate extraction
    stopwords = _load_stopwords(STOPWORDS_PATH)
    logger.info("Loaded %d stopwords.", len(stopwords))

    # ------------------------------------------------------------------
    # Step 1: Candidate extraction (Req 8.1) — only when corpus provided
    # ------------------------------------------------------------------
    if corpus is not None and len(corpus) > 0:
        logger.info("Extracting keyword candidates from %d documents...", len(corpus))
        candidates = extract_candidates(
            corpus,
            stopwords=stopwords,
            top_unigrams=500,
            top_bigrams=300,
        )
        os.makedirs(os.path.dirname(CANDIDATES_PATH), exist_ok=True)
        candidates.to_csv(CANDIDATES_PATH, index=False, encoding="utf-8")
        logger.info(
            "Saved %d keyword candidates to %s (unigrams: %d, bigrams: %d).",
            len(candidates),
            CANDIDATES_PATH,
            len(candidates[candidates["ngram"] == "unigram"]),
            len(candidates[candidates["ngram"] == "bigram"]),
        )
    else:
        logger.info("No corpus provided — skipping candidate extraction.")

    # ------------------------------------------------------------------
    # Step 2: Build curated keyword list (Req 8.2)
    # ------------------------------------------------------------------
    keywords = get_curated_keywords()
    all_keywords = get_all_keywords_flat()
    logger.info(
        "Curated keyword list: %d positive, %d negative, %d neutral (total: %d).",
        len(keywords["positive"]),
        len(keywords["negative"]),
        len(keywords["neutral"]),
        len(all_keywords),
    )

    # ------------------------------------------------------------------
    # Step 3: Save keyword lists (Req 8.3, 8.4)
    # ------------------------------------------------------------------
    save_keywords_finance(keywords, KEYWORDS_FINANCE_PATH)
    logger.info("Saved flat keyword list to %s.", KEYWORDS_FINANCE_PATH)

    save_keywords_by_group(KEYWORD_GROUPS, KEYWORDS_BY_GROUP_PATH)
    logger.info("Saved group-level keyword breakdown to %s.", KEYWORDS_BY_GROUP_PATH)

    # ------------------------------------------------------------------
    # Step 4: Corpus frequency report (Req 8.5)
    # ------------------------------------------------------------------
    if corpus is not None and len(corpus) > 0:
        freq = compute_corpus_frequency(corpus, all_keywords)
        print_frequency_report(freq, keywords, logger)
    else:
        logger.info("No corpus provided — skipping frequency report.")

    logger.info("Keyword Builder (TASK 8) complete.")
    return keywords


def run_keyword_builder() -> Dict[str, List[str]]:
    """Execute TASK 8 by loading the processed news corpus and building keywords.

    Loads ``data/news/processed/all_news_processed.csv``, extracts the
    ``text_tokenized`` column as the corpus, and delegates to
    :func:`build_keyword_list`.

    Returns:
        The curated keyword dictionary.
    """
    logger = setup_logger("TASK_8")

    corpus: Optional[List[str]] = None
    if os.path.isfile(INPUT_PATH):
        df = pd.read_csv(INPUT_PATH, encoding="utf-8")
        logger.info("Loaded %d articles from %s.", len(df), INPUT_PATH)
        if "text_tokenized" in df.columns:
            corpus = df["text_tokenized"].fillna("").tolist()
        else:
            logger.warning("Column 'text_tokenized' not found in %s.", INPUT_PATH)
    else:
        logger.warning("Input file not found: %s. Building keywords without corpus.", INPUT_PATH)

    return build_keyword_list(corpus)


if __name__ == "__main__":
    run_keyword_builder()
