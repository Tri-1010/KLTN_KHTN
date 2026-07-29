"""Anomaly_Detector — B5: phát hiện đột biến khối lượng tin (Req 12.3).

Thí nghiệm B5 (tùy chọn) kiểm tra giả thuyết rằng **những kỳ có khối lượng tin
bất thường cao** (news spike) mang giá trị dự báo. Với mỗi ``(ticker, quarter_id)``
ta gán một đặc trưng nhị phân ``news_spike`` bằng một khi số lượng tin của kỳ đó
vượt quá ngưỡng thống kê ``mean + 2·std`` (Req 12.3):

.. code-block:: text

    threshold          = mean(news_count trên TRAIN) + 2 · std(news_count trên TRAIN)
    news_spike[q]      = 1  nếu  news_count[q] > threshold
                       = 0  ngược lại

**Chống rò rỉ (leakage guard, Req 4.1, 4.2):** trung bình và độ lệch chuẩn CHỈ
được ước lượng trên tập **train** — tức các hàng có ``quarter_id < cutoff``
(``Train_Cutoff`` mặc định ``"2025Q1"``). Ngưỡng dẫn xuất từ train sau đó được
áp dụng cho **mọi** hàng (train + test). Nhờ vậy các hàng thuộc kỳ test không bao
giờ ảnh hưởng tới ngưỡng — không có rò rỉ thông tin tương lai vào đặc trưng.

**Các quyết định thiết kế (được ghi rõ):**

- **Ngưỡng toàn cục trên train:** ``mean``/``std`` tính gộp trên toàn bộ hàng
  train của mọi ticker (đơn giản nhất, khớp đúng phát biểu "tính trên tập
  train" của Req 12.3), không tách theo từng ticker.
- **Độ lệch chuẩn quần thể (``ddof=0``):** dùng ``numpy.std`` mặc định
  (population std) để ngưỡng ổn định và tái lập được; ghi rõ để test khẳng định.
- **Guard biên (empty/zero-variance train):** nếu tập train rỗng, hoặc độ lệch
  chuẩn bằng 0 (mọi giá trị train bằng nhau — gồm cả trường hợp chỉ có một hàng
  train), ngưỡng được đặt thành ``+inf`` → **không** hàng nào bị gán spike. Điều
  này tránh các spike giả (spurious spikes) khi không có đủ biến thiên để định
  nghĩa "bất thường".
- **So sánh cutoff bằng chuỗi:** chuỗi ``quarter_id`` dạng ``"YYYYQn"`` sắp xếp
  từ điển trùng với thứ tự thời gian, nên ``df["quarter_id"] < cutoff`` cho đúng
  mặt nạ train — nhất quán với quy ước của
  :func:`pipeline.task10_train.time_series_split`.

``compute_spike_threshold`` (thuần) trả về ngưỡng train; ``compute_news_spike``
(thuần) trả khung ``[ticker, quarter_id, news_spike]`` keyed mergeable trên
``(ticker, quarter_id)``. ``build_b5_features`` là entrypoint zero-arg đọc
``data/aggregated/news_by_quarter.csv``, gộp cột ``news_spike`` lên khung đặc
trưng v0 base, và ghi ``data/features/keyword_features_B5.csv`` (Req 12.3, 2.1).
Tệp v0 gốc ``data/features/keyword_features.csv`` không bị sửa đổi (Req 2.3).

Báo cáo so sánh với Baseline_v0 do CLI
``experiments/run_experiment.py::run_experiment("B5")`` tự sinh qua
Comparison_Reporter — module này chỉ cần tạo tệp đặc trưng hợp lệ, mergeable.

_Requirements: 12.3, 4.1, 2.1, 2.3_
"""

from __future__ import annotations

import logging
import math
import os
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from pipeline.task8_keywords import get_curated_keywords
from pipeline.task9_kw_features import (
    add_coverage_features,
    compute_keyword_counts,
    compute_sentiment_scores,
    compute_tfidf_features,
)

logger = logging.getLogger(__name__)

__all__ = [
    "compute_spike_threshold",
    "compute_news_spike",
    "build_b5_features",
]

# ---------------------------------------------------------------------------
# Đường dẫn artifact & hằng số của B5 (Req 12.3, 4.1, 2.1, 2.3)
# ---------------------------------------------------------------------------

NEWS_BY_QUARTER_PATH = "data/aggregated/news_by_quarter.csv"
#: Tệp đặc trưng version hóa của B5 — KHÔNG ghi đè v0 (Req 2.1, 2.3).
OUTPUT_PATH = "data/features/keyword_features_B5.csv"

#: Cột khóa mergeable trên (ticker, quarter_id).
META_COLS = ["ticker", "quarter_id"]

#: Train_Cutoff theo thời gian mặc định (Req 4.1). Hàng train: quarter_id < cutoff.
DEFAULT_CUTOFF = "2025Q1"


# ---------------------------------------------------------------------------
# Thuật toán then chốt: ngưỡng train-only (Req 12.3 + leakage guard 4.1)
# ---------------------------------------------------------------------------


def compute_spike_threshold(
    df: pd.DataFrame,
    cutoff: str = DEFAULT_CUTOFF,
) -> float:
    """Tính ngưỡng ``mean + 2·std`` của ``news_count`` CHỈ trên tập train (Req 12.3).

    Tập train là các hàng có ``quarter_id < cutoff`` (so sánh chuỗi, nhất quán
    với :func:`pipeline.task10_train.time_series_split`). Trung bình và độ lệch
    chuẩn dùng độ lệch chuẩn quần thể ``ddof=0`` (numpy mặc định). Hàng thuộc kỳ
    test (``quarter_id >= cutoff``) KHÔNG tham gia tính ngưỡng — chống rò rỉ
    (Req 4.1, 4.2).

    Guard biên: nếu tập train rỗng hoặc độ lệch chuẩn bằng 0 (mọi giá trị train
    bằng nhau, gồm cả trường hợp một hàng train), trả về ``+inf`` để không hàng
    nào bị gán spike (tránh spike giả).

    Args:
        df: DataFrame có cột ``quarter_id`` và ``news_count``.
        cutoff: Train_Cutoff theo thời gian (mặc định ``"2025Q1"``).

    Returns:
        Ngưỡng ``mean + 2·std`` (float); ``+inf`` khi train rỗng hoặc std == 0.
    """
    train_mask = df["quarter_id"] < cutoff
    values = df.loc[train_mask, "news_count"].astype(float).to_numpy()

    if values.size == 0:
        # Không có hàng train → không thể định nghĩa "bất thường" → không spike.
        return math.inf

    std = float(np.std(values, ddof=0))
    if std == 0.0 or not np.isfinite(std):
        # Zero-variance (mọi giá trị train bằng nhau) → không có spike giả.
        return math.inf

    mean = float(np.mean(values))
    return mean + 2.0 * std


def compute_news_spike(
    df: pd.DataFrame,
    cutoff: str = DEFAULT_CUTOFF,
) -> pd.DataFrame:
    """Tính đặc trưng nhị phân ``news_spike`` keyed trên ``(ticker, quarter_id)``.

    Hàm thuần trung tâm dùng chung cho :func:`build_b5_features` và cho test.
    Ngưỡng được ước lượng CHỈ trên train (:func:`compute_spike_threshold`) rồi áp
    dụng cho MỌI hàng (train + test) — chống rò rỉ (Req 4.1):

    .. code-block:: text

        news_spike[q] = 1  nếu  news_count[q] > threshold
                      = 0  ngược lại

    Đầu vào phải chứa ``ticker``, ``quarter_id`` (khóa) và ``news_count``.

    Args:
        df: DataFrame đầu vào (xem các cột bắt buộc ở trên).
        cutoff: Train_Cutoff theo thời gian (mặc định ``"2025Q1"``).

    Returns:
        DataFrame gồm ``[ticker, quarter_id, news_spike]`` với ``news_spike`` là
        số nguyên nhị phân (0/1).
    """
    threshold = compute_spike_threshold(df, cutoff)
    news_count = df["news_count"].astype(float).to_numpy()

    spike = (news_count > threshold).astype(int)

    return pd.DataFrame(
        {
            "ticker": df["ticker"].to_numpy(),
            "quarter_id": df["quarter_id"].to_numpy(),
            "news_spike": spike,
        }
    )


# ---------------------------------------------------------------------------
# Xây dựng khung đặc trưng v0 base + B5 (Req 12.3, 2.1)
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

    Tái dùng nguyên các hàm của v0 (giống ``b4_spillover._prepare_v0_frame``):
    raw/normalized counts → sentiment scores → TF-IDF → coverage. Bỏ cột
    ``combined_text`` ở cuối để khung sẵn sàng ghi ra tệp đặc trưng. Khung này
    còn giữ ``news_count`` cần cho :func:`compute_news_spike`.

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


def build_b5_features(
    news_path: str = NEWS_BY_QUARTER_PATH,
    output_path: str = OUTPUT_PATH,
    cutoff: str = DEFAULT_CUTOFF,
) -> pd.DataFrame:
    """Đọc news-by-quarter, tính B5 và ghi ``keyword_features_B5.csv`` (Req 12.3).

    Gộp đặc trưng B5 (``news_spike``) lên khung đặc trưng v0 base, giữ khung khóa
    ``(ticker, quarter_id)`` mergeable với ``technical_features.csv`` (Req 2.1).
    Ngưỡng đột biến ước lượng CHỈ trên train (``quarter_id < cutoff``) rồi áp cho
    mọi hàng — chống rò rỉ (Req 4.1). KHÔNG sửa tệp v0
    ``data/features/keyword_features.csv`` (Req 2.3).

    Args:
        news_path: Đường dẫn ``news_by_quarter.csv`` đầu vào.
        output_path: Đường dẫn ghi tệp đặc trưng B5.
        cutoff: Train_Cutoff theo thời gian (mặc định ``"2025Q1"``).

    Returns:
        DataFrame đặc trưng B5 đã ghi (rỗng nếu đầu vào lỗi).
    """
    df = _load_news(news_path)
    if df.empty:
        return pd.DataFrame()

    keywords_by_direction = get_curated_keywords()

    # Khung v0 base (đã có kw_*, kw_norm_*, tfidf_*, sentiment, coverage, news_count).
    v0 = _prepare_v0_frame(df, keywords_by_direction)

    # Đặc trưng B5, tính trực tiếp trên khung v0 (đủ cột news_count + khóa).
    b5 = compute_news_spike(v0, cutoff)

    # Gộp cột news_spike lên v0 base theo khóa (ticker, quarter_id).
    features = v0.merge(b5, on=META_COLS, how="left")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    features.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(
        "Đã ghi đặc trưng B5 (%d hàng, %d cột) vào %s.",
        len(features),
        len(features.columns),
        output_path,
    )
    return features


if __name__ == "__main__":  # pragma: no cover - entrypoint
    logging.basicConfig(level=logging.INFO)
    build_b5_features()
