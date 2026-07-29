"""Spillover_Builder — B4: lan tỏa tin tức chéo ngành (Req 12).

Thí nghiệm B4 (tùy chọn) kiểm tra giả thuyết **lan tỏa (spillover) trong ngành**:
tâm lý (sentiment) và cường độ tin tức của *các ticker khác* trong cùng một ngành,
trong cùng một kỳ, có mang giá trị dự báo cho một ticker hay không. Ý tưởng là một
làn sóng tin tích cực/tiêu cực toàn ngành có thể tác động tới từng cổ phiếu, kể cả
khi bản thân cổ phiếu đó chưa có tin riêng.

Với mỗi ``(ticker t thuộc ngành S, quarter_id q)`` (Req 12.1, 12.2):

.. code-block:: text

    sector_news_count[t, q] = Σ_{u ∈ S, u ≠ t}  news_count[u, q]
    sector_pos_score[t, q]  = mean_{u ∈ S, u ≠ t}  pos_score[u, q]

Hai ràng buộc cốt lõi:

- **Leave-one-out trong ngành (Req 12.1):** điểm được gán ngược cho ticker ``t``
  KHÔNG bao giờ dùng chính tin của ``t`` — chỉ tổng hợp trên các ticker *khác*
  cùng ngành. Nhờ vậy đặc trưng không rò rỉ tín hiệu của chính ticker đó.
- **Chỉ dùng tin cùng kỳ (Req 12.2):** mọi tổng hợp chỉ lấy tin thuộc đúng
  ``Period_q`` — không dùng bất kỳ kỳ nào khác (no temporal leakage).

``pos_score`` là tín hiệu sentiment v0 theo ``(ticker, quarter)`` do
:func:`pipeline.task9_kw_features.compute_sentiment_scores` sinh ra (tổng các
``kw_norm_`` của từ khóa tích cực). Ta chọn ``pos_score`` (không phải
``sentiment_ratio``) để khớp đúng tên cột đầu ra ``sector_pos_score``.

**Quy ước ngành chỉ có một ticker trong kỳ (singleton):** khi không tồn tại
ticker "khác" nào trong ngành ``S`` tại kỳ ``q``, ``sector_news_count = 0`` và
``sector_pos_score = NaN`` (giữ NaN, không impute) — nhất quán với error-handling
của thiết kế; imputer fit-trên-train của pipeline sẽ xử lý sau.

``compute_spillover_features`` là hàm thuần (pure) tính hai cột B4 keyed trên
``(ticker, quarter_id)`` với ánh xạ ``sector_of`` được tiêm vào (nên test không
phụ thuộc cấu hình). ``build_b4_features`` là entrypoint zero-arg đọc
``data/aggregated/news_by_quarter.csv``, dùng
:func:`experiments.common.segments.assign_segments` để lấy ánh xạ ngành thật,
gộp hai cột B4 lên khung đặc trưng v0 base, và ghi
``data/features/keyword_features_B4.csv`` (Req 12.1, 12.2, 2.1). Tệp v0 gốc
``data/features/keyword_features.csv`` không bị sửa đổi (Req 2.3).

Báo cáo so sánh với Baseline_v0 do CLI
``experiments/run_experiment.py::run_experiment("B4")`` tự sinh qua
Comparison_Reporter — module này chỉ cần tạo tệp đặc trưng hợp lệ, mergeable.

_Requirements: 12.1, 12.2, 2.1, 2.3_
"""

from __future__ import annotations

import logging
import os
from typing import Callable, Dict, List, Mapping, Optional, Union

import numpy as np
import pandas as pd

from experiments.common.segments import assign_segments
from pipeline.task8_keywords import get_curated_keywords
from pipeline.task9_kw_features import (
    add_coverage_features,
    compute_keyword_counts,
    compute_sentiment_scores,
    compute_tfidf_features,
)

logger = logging.getLogger(__name__)

__all__ = [
    "B4_FEATURE_COLUMNS",
    "compute_spillover_features",
    "build_b4_features",
]

# ---------------------------------------------------------------------------
# Đường dẫn artifact của B4 (Req 12.1, 12.2, 2.1, 2.3)
# ---------------------------------------------------------------------------

NEWS_BY_QUARTER_PATH = "data/aggregated/news_by_quarter.csv"
#: Tệp đặc trưng version hóa của B4 — KHÔNG ghi đè v0 (Req 2.1, 2.3).
OUTPUT_PATH = "data/features/keyword_features_B4.csv"

#: Cột khóa mergeable trên (ticker, quarter_id).
META_COLS = ["ticker", "quarter_id"]

#: Hai cột đặc trưng đặc thù của B4 (thứ tự ổn định).
B4_FEATURE_COLUMNS: List[str] = [
    "sector_pos_score",
    "sector_news_count",
]

#: Kiểu ánh xạ ticker -> sector: dict hoặc callable.
SectorOf = Union[Mapping[str, str], Callable[[str], Optional[str]]]


# ---------------------------------------------------------------------------
# Thuật toán then chốt: tổng hợp ngành leave-one-out, cùng kỳ (Req 12.1, 12.2)
# ---------------------------------------------------------------------------


def _resolve_sector(sector_of: SectorOf, ticker: str) -> Optional[str]:
    """Tra cứu ngành của ``ticker`` từ dict hoặc callable ``sector_of``."""
    if callable(sector_of):
        return sector_of(ticker)
    return sector_of.get(ticker)


def compute_spillover_features(
    df: pd.DataFrame,
    sector_of: SectorOf,
) -> pd.DataFrame:
    """Tính hai đặc trưng B4 keyed trên ``(ticker, quarter_id)`` (Req 12.1, 12.2).

    Đây là hàm thuần trung tâm dùng chung cho :func:`build_b4_features` và cho
    test (ánh xạ ``sector_of`` được tiêm vào nên không phụ thuộc cấu hình). Đầu
    vào phải chứa các cột:

    - ``ticker``, ``quarter_id`` — khóa;
    - ``news_count`` — số lượng tin của kỳ (cho ``sector_news_count``);
    - ``pos_score`` — điểm sentiment tích cực v0 của kỳ (cho ``sector_pos_score``).

    Với mỗi ``(ticker t thuộc ngành S, quarter q)`` (leave-one-out, cùng kỳ):

    .. code-block:: text

        sector_news_count[t, q] = Σ_{u ∈ S, u ≠ t}  news_count[u, q]
        sector_pos_score[t, q]  = mean_{u ∈ S, u ≠ t}  pos_score[u, q]

    Ràng buộc:

    - Loại trừ chính tin của ticker ``t`` (Req 12.1).
    - Chỉ tổng hợp trên tin cùng kỳ ``q`` (Req 12.2).
    - Ngành chỉ có một ticker trong kỳ (không có "ticker khác") →
      ``sector_news_count = 0`` và ``sector_pos_score = NaN`` (giữ NaN, không
      impute).

    Ticker không có ánh xạ ngành (``sector_of`` trả về ``None``) được xử lý như
    một ngành riêng biệt của chính nó → luôn là singleton (không có láng giềng).

    Args:
        df: DataFrame đầu vào (xem các cột bắt buộc ở trên).
        sector_of: Ánh xạ ``ticker -> sector`` (dict hoặc callable).

    Returns:
        DataFrame gồm ``[ticker, quarter_id, sector_pos_score,
        sector_news_count]`` keyed mergeable trên ``(ticker, quarter_id)``.
    """
    tickers = df["ticker"].to_numpy()
    quarters = df["quarter_id"].to_numpy()
    news_count = df["news_count"].astype(float).to_numpy()
    pos_score = df["pos_score"].astype(float).to_numpy()

    n = len(df)

    # Gán mỗi hàng vào một khóa ngành. Ticker không có ánh xạ → khóa riêng biệt
    # (sentinel gắn với ticker) để nó luôn là singleton, không rò rỉ chéo ngành.
    sector_keys: List[object] = []
    for t in tickers:
        sec = _resolve_sector(sector_of, t)
        if sec is None:
            sector_keys.append(("__unmapped__", t))
        else:
            sector_keys.append(sec)

    # Tổng hợp theo (sector, quarter): tổng news_count, tổng pos_score, số ticker.
    group_news_sum: Dict[tuple, float] = {}
    group_pos_sum: Dict[tuple, float] = {}
    group_size: Dict[tuple, int] = {}
    for i in range(n):
        key = (sector_keys[i], quarters[i])
        group_news_sum[key] = group_news_sum.get(key, 0.0) + news_count[i]
        group_pos_sum[key] = group_pos_sum.get(key, 0.0) + pos_score[i]
        group_size[key] = group_size.get(key, 0) + 1

    sector_news = np.zeros(n, dtype=float)
    sector_pos = np.empty(n, dtype=float)

    for i in range(n):
        key = (sector_keys[i], quarters[i])
        others = group_size[key] - 1
        if others <= 0:
            # Singleton trong kỳ: không có ticker khác cùng ngành (Req 12.1).
            sector_news[i] = 0.0
            sector_pos[i] = np.nan
        else:
            # Leave-one-out: trừ đóng góp của chính ticker t (Req 12.1),
            # chỉ trên tin cùng kỳ q (Req 12.2).
            sector_news[i] = group_news_sum[key] - news_count[i]
            sector_pos[i] = (group_pos_sum[key] - pos_score[i]) / others

    return pd.DataFrame(
        {
            "ticker": tickers,
            "quarter_id": quarters,
            "sector_pos_score": sector_pos,
            "sector_news_count": sector_news,
        }
    )


# ---------------------------------------------------------------------------
# Xây dựng khung đặc trưng v0 base + B4 (Req 12.1, 12.2, 2.1)
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


def _prepare_v0_frame(
    df: pd.DataFrame,
    keywords_by_direction: Optional[Dict[str, List[str]]] = None,
) -> pd.DataFrame:
    """Tính khung đặc trưng v0 đầy đủ (kw_*, kw_norm_*, tfidf_*, sentiment, coverage).

    Tái dùng nguyên các hàm của v0 (giống ``a3_velocity._prepare_v0_frame``):
    raw/normalized counts → sentiment scores → TF-IDF → coverage. Bỏ cột
    ``combined_text`` ở cuối để khung sẵn sàng ghi ra tệp đặc trưng. Khung này
    còn giữ ``pos_score`` và ``news_count`` cần cho :func:`compute_spillover_features`.

    Args:
        df: DataFrame ``[ticker, quarter_id, news_count, combined_text]``.
        keywords_by_direction: Dict positive/negative/neutral; mặc định curated.

    Returns:
        DataFrame v0 đầy đủ (đã bỏ ``combined_text``).
    """
    if keywords_by_direction is None:
        keywords_by_direction = get_curated_keywords()

    all_keywords = (
        keywords_by_direction.get("positive", [])
        + keywords_by_direction.get("negative", [])
        + keywords_by_direction.get("neutral", [])
    )

    result = compute_keyword_counts(df, all_keywords)
    result = compute_sentiment_scores(result, keywords_by_direction)
    result = compute_tfidf_features(result, all_keywords)
    result = add_coverage_features(result)

    if "combined_text" in result.columns:
        result = result.drop(columns=["combined_text"])
    return result


def build_b4_features(
    news_path: str = NEWS_BY_QUARTER_PATH,
    output_path: str = OUTPUT_PATH,
) -> pd.DataFrame:
    """Đọc news-by-quarter, tính B4 và ghi ``keyword_features_B4.csv`` (Req 12).

    Gộp hai đặc trưng B4 (``sector_pos_score``, ``sector_news_count``) lên khung
    đặc trưng v0 base, giữ khung khóa ``(ticker, quarter_id)`` mergeable với
    ``technical_features.csv`` (Req 2.1). Ánh xạ ngành lấy từ
    :func:`experiments.common.segments.assign_segments` (nguồn chân lý ticker ->
    sector cho toàn vũ trụ HOSE-80). KHÔNG sửa tệp v0
    ``data/features/keyword_features.csv`` (Req 2.3).

    Args:
        news_path: Đường dẫn ``news_by_quarter.csv`` đầu vào.
        output_path: Đường dẫn ghi tệp đặc trưng B4.

    Returns:
        DataFrame đặc trưng B4 đã ghi (rỗng nếu đầu vào lỗi).
    """
    df = _load_news(news_path)
    if df.empty:
        return pd.DataFrame()

    keywords_by_direction = get_curated_keywords()

    # Khung v0 base (đã có kw_*, pos_score, news_count, sentiment, coverage, tfidf_*).
    v0 = _prepare_v0_frame(df, keywords_by_direction)

    # Ánh xạ ticker -> sector thật từ Segment_Mapper (B3).
    segments = assign_segments()
    sector_of = {ticker: info.sector for ticker, info in segments.items()}

    # Hai đặc trưng B4, tính trực tiếp trên khung v0 (đủ cột đầu vào cần thiết).
    b4 = compute_spillover_features(v0, sector_of)

    # Gộp hai cột B4 lên v0 base theo khóa (ticker, quarter_id).
    features = v0.merge(b4, on=META_COLS, how="left")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    features.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(
        "Đã ghi đặc trưng B4 (%d hàng, %d cột) vào %s.",
        len(features),
        len(features.columns),
        output_path,
    )
    return features


if __name__ == "__main__":  # pragma: no cover - entrypoint
    logging.basicConfig(level=logging.INFO)
    build_b4_features()
