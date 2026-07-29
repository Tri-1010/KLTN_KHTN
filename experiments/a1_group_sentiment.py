"""Sentiment_Aggregator — A1: điểm sentiment có dấu theo nhóm chủ đề (Req 6).

Thí nghiệm A1 thay các đặc trưng tần suất từ khóa rời rạc của baseline v0 bằng
một điểm **sentiment có dấu** tổng hợp cho mỗi nhóm chủ đề G ∈ ``KEYWORD_GROUPS``
(các nhóm "A".."F" định nghĩa trong :mod:`pipeline.task8_keywords`).

Với mỗi nhóm G và mỗi ``(ticker, quarter_id)`` (Req 6.1, 6.2):

.. code-block:: text

    sent_{G} = Σ kw_norm(positive ∈ G) − Σ kw_norm(negative ∈ G)

Trong đó ``kw_norm_{k} = kw_{k} / news_count`` đã được
:func:`pipeline.task9_kw_features.compute_keyword_counts` tính sẵn, nên
``sent_{G}`` **tự nhiên đã được chuẩn hóa theo ``news_count``** (Req 6.2) — không
cần chia thêm. Các nhóm chỉ có từ khóa trung tính (ví dụ nhóm F "Sự kiện doanh
nghiệp trung tính") không có từ khóa positive/negative nên ``sent_F = 0``; cột
vẫn được phát ra để giữ schema nhất quán.

Hai biến thể tập đặc trưng:

- **A1a** (Req 6.3): chỉ ``sent_A..F`` + đặc trưng coverage (news_count,
  news_count_log, has_min_news), ghi ``data/features/keyword_features_A1a.csv``.
- **A1b** (Req 6.4): toàn bộ đặc trưng tần suất gốc của v0 (``kw_*``,
  ``kw_norm_*``, ``tfidf_*`` + sentiment scores + coverage) CỘNG ``sent_A..F``,
  ghi ``data/features/keyword_features_A1b.csv``.

Cả hai giữ khung khóa ``(ticker, quarter_id)`` mergeable với
``technical_features.csv`` (Req 2.1) và KHÔNG sửa tệp v0
``data/features/keyword_features.csv`` (Req 2.3).

_Requirements: 6.1, 6.2, 6.3, 6.4, 2.1_
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import pandas as pd

from pipeline.task8_keywords import (
    KEYWORD_GROUPS,
    get_all_keywords_flat,
    get_curated_keywords,
)
from pipeline.task9_kw_features import (
    add_coverage_features,
    compute_keyword_counts,
    compute_sentiment_scores,
    compute_tfidf_features,
)

logger = logging.getLogger(__name__)

__all__ = [
    "GROUP_NAMES",
    "compute_group_sentiment",
    "extract_a1a_features",
    "extract_a1b_features",
    "build_a1a_features",
    "build_a1b_features",
]

# ---------------------------------------------------------------------------
# Đường dẫn artifact của A1 (Req 6.3, 6.4, 2.1, 2.3)
# ---------------------------------------------------------------------------

NEWS_BY_QUARTER_PATH = "data/aggregated/news_by_quarter.csv"
#: Tệp đặc trưng version hóa của A1a — chỉ sent_* + coverage (Req 6.3).
A1A_OUTPUT_PATH = "data/features/keyword_features_A1a.csv"
#: Tệp đặc trưng version hóa của A1b — v0 base + sent_* (Req 6.4).
A1B_OUTPUT_PATH = "data/features/keyword_features_A1b.csv"

#: Các cột coverage của v0 giữ lại trong A1a (Req 6.3).
COVERAGE_COLS = ["news_count", "news_count_log", "has_min_news"]
#: Cột khóa mergeable trên (ticker, quarter_id).
META_COLS = ["ticker", "quarter_id"]

#: Tên nhóm chủ đề (khóa của KEYWORD_GROUPS), sắp thứ tự ổn định "A".."F".
GROUP_NAMES: List[str] = sorted(KEYWORD_GROUPS.keys())


# ---------------------------------------------------------------------------
# Thuật toán then chốt: điểm sentiment có dấu theo nhóm (Req 6.1, 6.2)
# ---------------------------------------------------------------------------


def compute_group_sentiment(
    df: pd.DataFrame,
    keyword_groups: Dict[str, Dict[str, Any]] = KEYWORD_GROUPS,
) -> pd.DataFrame:
    """Thêm cột ``sent_{G}`` cho mỗi nhóm chủ đề G vào DataFrame.

    Với mỗi nhóm G và mỗi hàng ``(ticker, quarter_id)`` (Req 6.1):

    .. code-block:: text

        sent_{G} = Σ kw_norm_{k} (k ∈ positive của G)
                 − Σ kw_norm_{k} (k ∈ negative của G)

    ``kw_norm_{k}`` (= ``kw_{k} / news_count``) do
    :func:`pipeline.task9_kw_features.compute_keyword_counts` tính sẵn, nên điểm
    này đã chuẩn hóa theo ``news_count`` (Req 6.2). Giá trị ``NaN`` của
    ``kw_norm`` (khi ``news_count == 0``) được coi là 0 trong tổng.

    Nhóm chỉ có từ khóa trung tính (không có positive/negative) → ``sent_{G} = 0``
    nhưng cột vẫn được phát ra để giữ schema nhất quán (ví dụ nhóm F).

    Args:
        df: DataFrame đã chứa các cột ``kw_norm_{k}`` (đầu ra của
            :func:`compute_keyword_counts`).
        keyword_groups: Cấu trúc nhóm chủ đề; mặc định
            :data:`pipeline.task8_keywords.KEYWORD_GROUPS`.

    Returns:
        DataFrame gốc kèm các cột ``sent_{G}`` cho mọi nhóm G (thứ tự "A".."F").
    """
    result = df.copy()

    sent_cols: Dict[str, pd.Series] = {}
    for group in sorted(keyword_groups.keys()):
        group_data = keyword_groups[group]

        pos_cols = [
            f"kw_norm_{kw}"
            for kw in group_data.get("positive", [])
            if f"kw_norm_{kw}" in result.columns
        ]
        neg_cols = [
            f"kw_norm_{kw}"
            for kw in group_data.get("negative", [])
            if f"kw_norm_{kw}" in result.columns
        ]

        pos_sum = (
            result[pos_cols].fillna(0).sum(axis=1)
            if pos_cols
            else pd.Series(0.0, index=result.index)
        )
        neg_sum = (
            result[neg_cols].fillna(0).sum(axis=1)
            if neg_cols
            else pd.Series(0.0, index=result.index)
        )

        sent_cols[f"sent_{group}"] = pos_sum - neg_sum

    # Gộp một lần để tránh phân mảnh DataFrame (PerformanceWarning).
    sent_df = pd.DataFrame(sent_cols, index=result.index)
    return pd.concat([result, sent_df], axis=1)


# ---------------------------------------------------------------------------
# Xây dựng khung đặc trưng A1a / A1b (Req 6.3, 6.4)
# ---------------------------------------------------------------------------


def _prepare_v0_frame(
    df: pd.DataFrame,
    keywords_by_direction: Optional[Dict[str, List[str]]] = None,
) -> pd.DataFrame:
    """Tính khung đặc trưng v0 đầy đủ + cột ``kw_norm_*`` cần cho sentiment nhóm.

    Tái dùng nguyên các hàm của v0 (Req 6.1 yêu cầu tái dùng
    ``compute_keyword_counts``): raw/normalized counts → sentiment scores →
    TF-IDF → coverage. Trả về khung có cả ``combined_text`` (chưa drop) để bước
    gọi có thể chọn lọc cột.

    Args:
        df: DataFrame ``[ticker, quarter_id, news_count, combined_text]``.
        keywords_by_direction: Dict positive/negative/neutral; mặc định
            :func:`get_curated_keywords`.

    Returns:
        DataFrame v0 đầy đủ (kèm ``kw_*``, ``kw_norm_*``, ``tfidf_*``, sentiment
        scores, coverage) và còn cột ``combined_text``.
    """
    if keywords_by_direction is None:
        keywords_by_direction = get_curated_keywords()

    all_keywords = (
        keywords_by_direction.get("positive", [])
        + keywords_by_direction.get("negative", [])
        + keywords_by_direction.get("neutral", [])
    )

    # Bước 1: raw + normalized counts (tái dùng — cho kw_norm_*).
    result = compute_keyword_counts(df, all_keywords)
    # Bước 2: điểm sentiment tổng hợp của v0.
    result = compute_sentiment_scores(result, keywords_by_direction)
    # Bước 3: TF-IDF.
    result = compute_tfidf_features(result, all_keywords)
    # Bước 4: coverage.
    result = add_coverage_features(result)
    return result


def extract_a1a_features(
    df: pd.DataFrame,
    keywords_by_direction: Optional[Dict[str, List[str]]] = None,
) -> pd.DataFrame:
    """Tính đặc trưng A1a: chỉ ``sent_A..F`` + coverage + khóa (Req 6.3).

    Args:
        df: DataFrame ``[ticker, quarter_id, news_count, combined_text]``.
        keywords_by_direction: Dict positive/negative/neutral; mặc định curated.

    Returns:
        DataFrame gồm ``[ticker, quarter_id]`` + coverage + ``sent_{G}``.
        Không chứa ``kw_*``/``tfidf_*`` (đó là điểm khác biệt của biến thể A1a).
    """
    v0 = _prepare_v0_frame(df, keywords_by_direction)
    with_sent = compute_group_sentiment(v0)

    keep = [c for c in META_COLS if c in with_sent.columns]
    keep += [c for c in COVERAGE_COLS if c in with_sent.columns]
    keep += [f"sent_{g}" for g in GROUP_NAMES]

    return with_sent[keep].copy()


def extract_a1b_features(
    df: pd.DataFrame,
    keywords_by_direction: Optional[Dict[str, List[str]]] = None,
) -> pd.DataFrame:
    """Tính đặc trưng A1b: toàn bộ đặc trưng v0 CỘNG ``sent_A..F`` (Req 6.4).

    Args:
        df: DataFrame ``[ticker, quarter_id, news_count, combined_text]``.
        keywords_by_direction: Dict positive/negative/neutral; mặc định curated.

    Returns:
        DataFrame gồm mọi đặc trưng v0 (``kw_*``, ``kw_norm_*``, ``tfidf_*``,
        sentiment scores, coverage) + ``sent_{G}``; đã bỏ ``combined_text``.
    """
    v0 = _prepare_v0_frame(df, keywords_by_direction)
    with_sent = compute_group_sentiment(v0)

    if "combined_text" in with_sent.columns:
        with_sent = with_sent.drop(columns=["combined_text"])

    return with_sent


# ---------------------------------------------------------------------------
# Entrypoints ghi tệp (builders zero-arg, giống build_a2_features) — Req 6.3, 6.4
# ---------------------------------------------------------------------------


def _load_news(news_path: str) -> pd.DataFrame:
    """Nạp và kiểm tra ``news_by_quarter.csv``; trả DataFrame rỗng nếu lỗi."""
    if not os.path.isfile(news_path):
        logger.error("Không tìm thấy tệp đầu vào: %s", news_path)
        return pd.DataFrame()

    df = pd.read_csv(news_path, encoding="utf-8")
    logger.info("Đã nạp %d hàng (ticker, quarter) từ %s.", len(df), news_path)

    required = {"ticker", "quarter_id", "news_count", "combined_text"}
    missing = required - set(df.columns)
    if missing:
        logger.error("Thiếu cột bắt buộc: %s", missing)
        return pd.DataFrame()
    return df


def build_a1a_features(
    news_path: str = NEWS_BY_QUARTER_PATH,
    output_path: str = A1A_OUTPUT_PATH,
) -> pd.DataFrame:
    """Đọc news-by-quarter, tính A1a và ghi ``keyword_features_A1a.csv`` (Req 6.3).

    Chỉ gồm ``sent_A..F`` + đặc trưng coverage, keyed trên
    ``(ticker, quarter_id)`` để mergeable với ``technical_features.csv`` (Req 2.1).
    KHÔNG sửa tệp v0 (Req 2.3).

    Args:
        news_path: Đường dẫn ``news_by_quarter.csv`` đầu vào.
        output_path: Đường dẫn ghi tệp đặc trưng A1a.

    Returns:
        DataFrame đặc trưng A1a đã ghi (rỗng nếu đầu vào lỗi).
    """
    df = _load_news(news_path)
    if df.empty:
        return pd.DataFrame()

    features = extract_a1a_features(df, get_curated_keywords())

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    features.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(
        "Đã ghi đặc trưng A1a (%d hàng, %d cột) vào %s.",
        len(features),
        len(features.columns),
        output_path,
    )
    return features


def build_a1b_features(
    news_path: str = NEWS_BY_QUARTER_PATH,
    output_path: str = A1B_OUTPUT_PATH,
) -> pd.DataFrame:
    """Đọc news-by-quarter, tính A1b và ghi ``keyword_features_A1b.csv`` (Req 6.4).

    Gồm toàn bộ đặc trưng tần suất gốc của v0 CỘNG ``sent_A..F``, keyed trên
    ``(ticker, quarter_id)`` để mergeable với ``technical_features.csv`` (Req 2.1).
    KHÔNG sửa tệp v0 (Req 2.3).

    Args:
        news_path: Đường dẫn ``news_by_quarter.csv`` đầu vào.
        output_path: Đường dẫn ghi tệp đặc trưng A1b.

    Returns:
        DataFrame đặc trưng A1b đã ghi (rỗng nếu đầu vào lỗi).
    """
    df = _load_news(news_path)
    if df.empty:
        return pd.DataFrame()

    features = extract_a1b_features(df, get_curated_keywords())

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    features.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(
        "Đã ghi đặc trưng A1b (%d hàng, %d cột) vào %s.",
        len(features),
        len(features.columns),
        output_path,
    )
    return features


if __name__ == "__main__":  # pragma: no cover - entrypoint
    logging.basicConfig(level=logging.INFO)
    build_a1a_features()
    build_a1b_features()
