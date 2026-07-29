"""Velocity_Feature_Builder — A3: đặc trưng tốc độ và độ mới của tin tức (Req 7).

Thí nghiệm A3 bổ sung một tầng đặc trưng **động theo thời gian** lên trên tần
suất từ khóa tĩnh của baseline v0, để kiểm tra liệu thông tin *mới* có giá trị
dự báo cao hơn tần suất tĩnh không. Với mỗi ``(ticker, quarter_id)``, A3 tính
(Req 7.1–7.4):

.. code-block:: text

    news_velocity[q] = (news_count[q] − news_count[q−1]) / (news_count[q−1] + 1)
    pos_neg_shift[q] = sentiment_ratio[q] − sentiment_ratio[q−1]
    kw_novelty[q]    = # từ khóa lần đầu xuất hiện ở q của ticker
    kw_entropy[q]    = entropy Shannon của phân phối tần suất từ khóa trong q

Ràng buộc chống rò rỉ dữ liệu tương lai (Req 7.5, 4.3–4.5): mọi đặc trưng tại
kỳ ``q`` chỉ dùng dữ liệu của kỳ ``≤ q``.

- ``news_velocity`` / ``pos_neg_shift`` dùng ``groupby("ticker").shift(1)`` trên
  chuỗi kỳ đã sắp tăng dần, nên ``q−1`` luôn là quá khứ.
- ``kw_novelty`` tại ``q`` dùng **tập hợp mở rộng (expanding set)** các từ khóa
  đã từng xuất hiện ở các kỳ **trước** ``q`` (loại trừ chính ``q``).
- ``kw_entropy`` tại ``q`` chỉ phụ thuộc phân phối tần suất từ khóa của riêng
  kỳ ``q``.

**Quy ước kỳ đầu tiên của một ticker (không có ``q−1``):** ``news_velocity`` và
``pos_neg_shift`` được giữ ``NaN`` (không impute) — nhất quán với error-handling
của thiết kế ("keep NaN, not imputed"); imputer fit-trên-train của pipeline
huấn luyện sẽ xử lý các giá trị này. ``kw_novelty`` tại kỳ đầu bằng số từ khóa
xuất hiện ở kỳ đó (mọi từ khóa đều "mới"), và ``kw_entropy`` được tính bình
thường (entropy = 0 nếu không có từ khóa nào).

``build_velocity_features`` là hàm thuần (pure) tính bốn cột A3 keyed trên
``(ticker, quarter_id)``. ``build_a3_features`` là entrypoint zero-arg đọc
``data/aggregated/news_by_quarter.csv``, gộp bốn cột A3 lên khung đặc trưng v0
base, và ghi ``data/features/keyword_features_A3.csv`` (Req 7.6). Tệp v0 gốc
``data/features/keyword_features.csv`` không bị sửa đổi (Req 2.3).

_Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 2.1, 2.3_
"""

from __future__ import annotations

import logging
import os
from typing import Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

from pipeline.task8_keywords import (
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
    "A3_FEATURE_COLUMNS",
    "shannon_entropy",
    "compute_a3_features",
    "build_velocity_features",
    "build_a3_features",
]

# ---------------------------------------------------------------------------
# Đường dẫn artifact của A3 (Req 7.6, 2.1, 2.3)
# ---------------------------------------------------------------------------

NEWS_BY_QUARTER_PATH = "data/aggregated/news_by_quarter.csv"
#: Tệp đặc trưng version hóa của A3 — KHÔNG ghi đè v0 (Req 2.1, 2.3).
OUTPUT_PATH = "data/features/keyword_features_A3.csv"

#: Cột khóa mergeable trên (ticker, quarter_id).
META_COLS = ["ticker", "quarter_id"]

#: Bốn cột đặc trưng đặc thù của A3 (thứ tự ổn định).
A3_FEATURE_COLUMNS: List[str] = [
    "news_velocity",
    "kw_novelty",
    "kw_entropy",
    "pos_neg_shift",
]


# ---------------------------------------------------------------------------
# Thuật toán then chốt: entropy Shannon của phân phối tần suất từ khóa (Req 7.3)
# ---------------------------------------------------------------------------


def shannon_entropy(counts: Iterable[float]) -> float:
    """Entropy Shannon (log tự nhiên) của một phân phối tần suất từ khóa.

    Cho một vector số đếm từ khóa không âm, entropy được tính trên phân phối
    xác suất chuẩn hóa ``p_k = count_k / Σ count`` (chỉ trên các từ khóa có mặt,
    tức ``count_k > 0``):

    .. code-block:: text

        H = − Σ_{k: count_k > 0} p_k · ln(p_k)

    Tính chất (Req 7.3):

    - ``H = 0`` khi toàn bộ khối lượng tập trung ở đúng một từ khóa.
    - ``H`` đạt cực đại ``ln(n)`` khi phân phối đều trên ``n`` từ khóa có mặt.
    - ``H ≥ 0`` với mọi phân phối.
    - Trường hợp không có từ khóa nào (tổng bằng 0) → ``H = 0`` theo quy ước.

    Args:
        counts: Iterable các số đếm từ khóa (không âm) trong một kỳ.

    Returns:
        Giá trị entropy (float, không âm). Dùng log tự nhiên nhất quán.

    Validates: Requirements 7.3.
    """
    arr = np.asarray(list(counts), dtype=float)
    if arr.size == 0:
        return 0.0
    total = float(arr.sum())
    if total <= 0.0:
        # Không có từ khóa nào trong kỳ → entropy 0 theo quy ước.
        return 0.0
    probs = arr[arr > 0] / total
    # Bảo vệ chống underflow: một số đếm dương rất nhỏ so với tổng có thể bị làm
    # tròn xuống 0.0 sau khi chuẩn hóa. Vì p·ln(p) → 0 khi p → 0, ta loại các
    # xác suất đã underflow để tránh ln(0) = −inf và 0·(−inf) = NaN.
    probs = probs[probs > 0]
    if probs.size == 0:
        return 0.0
    return float(-np.sum(probs * np.log(probs)))


# ---------------------------------------------------------------------------
# Thuật toán then chốt: bốn đặc trưng A3 keyed trên (ticker, quarter_id)
# ---------------------------------------------------------------------------


def compute_a3_features(
    df: pd.DataFrame,
    keyword_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Tính bốn đặc trưng A3 keyed trên ``(ticker, quarter_id)`` (Req 7.1–7.5).

    Đây là hàm thuần trung tâm dùng chung cho ``build_velocity_features`` và cho
    property tests. Đầu vào phải chứa các cột:

    - ``ticker``, ``quarter_id`` — khóa;
    - ``news_count`` — số lượng tin của kỳ (cho ``news_velocity``);
    - ``sentiment_ratio`` — tỷ số sentiment của kỳ (cho ``pos_neg_shift``);
    - các cột trong ``keyword_cols`` — số đếm thô ``kw_{k}`` của mỗi từ khóa
      (cho ``kw_novelty`` và ``kw_entropy``).

    Toàn bộ tính toán tôn trọng ràng buộc nhân quả theo kỳ (Req 7.5): sắp theo
    ``(ticker, quarter_id)`` tăng dần rồi chỉ nhìn lùi về quá khứ.

    - ``news_velocity`` / ``pos_neg_shift`` dùng ``groupby("ticker").shift(1)``.
      Kỳ đầu tiên của một ticker (không có ``q−1``) → ``NaN`` (không impute).
    - ``kw_novelty`` dùng tập hợp mở rộng các từ khóa đã xuất hiện ở các kỳ
      **trước** ``q`` (loại trừ ``q``): số từ khóa có ``kw_{k} > 0`` tại ``q``
      mà chưa từng dương ở bất kỳ kỳ nào sớm hơn của ticker đó.
    - ``kw_entropy`` là entropy Shannon của số đếm ``kw_{k}`` tại riêng ``q``.

    Args:
        df: DataFrame đầu vào (xem các cột bắt buộc ở trên).
        keyword_cols: Danh sách tên cột số đếm từ khóa thô (``kw_{k}``); mặc
            định ``None`` → suy ra mọi cột bắt đầu bằng ``kw_`` nhưng không phải
            ``kw_norm_`` (để chỉ lấy số đếm thô, không lấy bản chuẩn hóa).

    Returns:
        DataFrame gồm ``[ticker, quarter_id, news_velocity, kw_novelty,
        kw_entropy, pos_neg_shift]``, đã sắp theo ``(ticker, quarter_id)``.
    """
    if keyword_cols is None:
        keyword_cols = [
            c
            for c in df.columns
            if c.startswith("kw_") and not c.startswith("kw_norm_")
        ]
    else:
        keyword_cols = [c for c in keyword_cols if c in df.columns]

    # Sắp ổn định theo (ticker, quarter_id) tăng dần. quarter_id dạng "YYYYQn"
    # sắp theo lexical trùng với thứ tự thời gian.
    result = df.sort_values(
        list(META_COLS), kind="mergesort"
    ).reset_index(drop=True)

    grouped = result.groupby("ticker", sort=False)

    # news_velocity = (nc[q] − nc[q−1]) / (nc[q−1] + 1); kỳ đầu → NaN (Req 7.1).
    prev_news_count = grouped["news_count"].shift(1)
    news_velocity = (result["news_count"] - prev_news_count) / (prev_news_count + 1)

    # pos_neg_shift = sentiment_ratio[q] − sentiment_ratio[q−1]; kỳ đầu → NaN (Req 7.4).
    prev_sentiment = grouped["sentiment_ratio"].shift(1)
    pos_neg_shift = result["sentiment_ratio"] - prev_sentiment

    # kw_entropy: entropy Shannon của số đếm kw tại từng kỳ (Req 7.3).
    if keyword_cols:
        counts_matrix = result[keyword_cols].to_numpy(dtype=float)
        kw_entropy = np.array(
            [shannon_entropy(row) for row in counts_matrix], dtype=float
        )
    else:
        kw_entropy = np.zeros(len(result), dtype=float)

    # kw_novelty: số từ khóa lần đầu xuất hiện ở q (expanding set các kỳ trước,
    # loại trừ q) (Req 7.2, 7.5).
    novelty = np.zeros(len(result), dtype=int)
    if keyword_cols:
        counts_matrix = result[keyword_cols].to_numpy(dtype=float)
        # Nhóm theo ticker giữ thứ tự đã sắp; tính expanding set trên vị trí hàng.
        for _ticker, positions in grouped.indices.items():
            seen = np.zeros(len(keyword_cols), dtype=bool)
            for pos in positions:  # positions đã theo thứ tự thời gian tăng dần
                present = counts_matrix[pos] > 0
                # Từ khóa mới = có mặt ở q nhưng chưa từng thấy ở các kỳ trước.
                novelty[pos] = int(np.count_nonzero(present & ~seen))
                seen |= present

    out = pd.DataFrame(
        {
            "ticker": result["ticker"].to_numpy(),
            "quarter_id": result["quarter_id"].to_numpy(),
            "news_velocity": news_velocity.to_numpy(),
            "kw_novelty": novelty,
            "kw_entropy": kw_entropy,
            "pos_neg_shift": pos_neg_shift.to_numpy(),
        }
    )
    return out


def build_velocity_features(
    news_by_quarter: pd.DataFrame,
    keywords_by_direction: Optional[Dict[str, List[str]]] = None,
) -> pd.DataFrame:
    """Tính bốn đặc trưng A3 từ khung ``news_by_quarter`` (Req 7.1–7.5).

    Chuẩn bị dữ liệu cần thiết rồi ủy quyền cho :func:`compute_a3_features`:

    1. ``compute_keyword_counts`` → số đếm thô ``kw_{k}`` (cho entropy/novelty).
    2. ``compute_sentiment_scores`` → ``sentiment_ratio`` (cho ``pos_neg_shift``).
       Lưu ý ``sentiment_ratio`` KHÔNG có sẵn trong ``news_by_quarter.csv`` mà
       được tính lại đúng như v0 (``(pos − neg)/(pos + neg + 1e-6)``).

    Args:
        news_by_quarter: DataFrame ``[ticker, quarter_id, news_count,
            combined_text]``.
        keywords_by_direction: Dict positive/negative/neutral; mặc định lấy từ
            :func:`get_curated_keywords`.

    Returns:
        DataFrame ``[ticker, quarter_id, news_velocity, kw_novelty, kw_entropy,
        pos_neg_shift]`` keyed mergeable trên ``(ticker, quarter_id)``.
    """
    if keywords_by_direction is None:
        keywords_by_direction = get_curated_keywords()

    all_keywords = (
        keywords_by_direction.get("positive", [])
        + keywords_by_direction.get("negative", [])
        + keywords_by_direction.get("neutral", [])
    )

    # Bước 1: số đếm thô + chuẩn hóa (cho entropy/novelty dùng kw_{k} thô).
    base = compute_keyword_counts(news_by_quarter, all_keywords)
    # Bước 2: điểm sentiment tổng hợp (cho sentiment_ratio).
    base = compute_sentiment_scores(base, keywords_by_direction)

    keyword_cols = [f"kw_{kw}" for kw in all_keywords]
    return compute_a3_features(base, keyword_cols)


# ---------------------------------------------------------------------------
# Xây dựng khung đặc trưng v0 base + A3 (Req 7.6, 2.1)
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

    Tái dùng nguyên các hàm của v0 (giống ``a1_group_sentiment._prepare_v0_frame``):
    raw/normalized counts → sentiment scores → TF-IDF → coverage. Bỏ cột
    ``combined_text`` ở cuối để khung sẵn sàng ghi ra tệp đặc trưng.

    Args:
        df: DataFrame ``[ticker, quarter_id, news_count, combined_text]``.
        keywords_by_direction: Dict positive/negative/neutral; mặc định curated.

    Returns:
        DataFrame v0 đầy đủ (đã bỏ ``combined_text``), còn ``kw_*`` và
        ``sentiment_ratio`` cần cho :func:`compute_a3_features`.
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


def build_a3_features(
    news_path: str = NEWS_BY_QUARTER_PATH,
    output_path: str = OUTPUT_PATH,
) -> pd.DataFrame:
    """Đọc news-by-quarter, tính A3 và ghi ``keyword_features_A3.csv`` (Req 7.6).

    Gộp bốn đặc trưng A3 (``news_velocity``, ``kw_novelty``, ``kw_entropy``,
    ``pos_neg_shift``) lên khung đặc trưng v0 base, giữ khung khóa
    ``(ticker, quarter_id)`` mergeable với ``technical_features.csv`` (Req 2.1).
    KHÔNG sửa tệp v0 ``data/features/keyword_features.csv`` (Req 2.3).

    Args:
        news_path: Đường dẫn ``news_by_quarter.csv`` đầu vào.
        output_path: Đường dẫn ghi tệp đặc trưng A3.

    Returns:
        DataFrame đặc trưng A3 đã ghi (rỗng nếu đầu vào lỗi).
    """
    df = _load_news(news_path)
    if df.empty:
        return pd.DataFrame()

    keywords_by_direction = get_curated_keywords()
    all_keywords = get_all_keywords_flat()

    # Khung v0 base (đã có kw_*, sentiment_ratio, news_count, coverage, tfidf_*).
    v0 = _prepare_v0_frame(df, keywords_by_direction)

    # Bốn đặc trưng A3, tính trực tiếp trên khung v0 (đủ cột đầu vào cần thiết).
    keyword_cols = [f"kw_{kw}" for kw in all_keywords]
    a3 = compute_a3_features(v0, keyword_cols)

    # Gộp bốn cột A3 lên v0 base theo khóa (ticker, quarter_id).
    features = v0.merge(a3, on=META_COLS, how="left")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    features.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(
        "Đã ghi đặc trưng A3 (%d hàng, %d cột) vào %s.",
        len(features),
        len(features.columns),
        output_path,
    )
    return features


if __name__ == "__main__":  # pragma: no cover - entrypoint
    logging.basicConfig(level=logging.INFO)
    build_a3_features()
