"""TFIDF_CrossTicker_Builder — A4: trọng số TF-IDF cross-ticker (Req 9).

Thí nghiệm A4 (tùy chọn) thay cách tính TF-IDF **theo từng tài liệu
``(ticker, quarter_id)``** của baseline v0 bằng một biến thể **cross-ticker**:
tần suất tài liệu (document frequency) của mỗi từ khóa được tính trên **chiều
ticker** thay vì trên từng cặp ``(ticker, quarter_id)``. Nhờ đó, một từ khóa
xuất hiện dày đặc ở một ticker nhưng hiếm gặp trên toàn vũ trụ ticker sẽ nhận
trọng số IDF cao (mang tính phân biệt), còn từ khóa phổ biến ở mọi ticker nhận
trọng số ~0 (ít giá trị phân biệt).

Với mỗi từ khóa ``k`` và mỗi hàng ``(ticker, quarter_id)`` (Req 9.1):

.. code-block:: text

    idf_x[k]          = ln( n_tickers / ticker_df[k] )          nếu ticker_df[k] > 0
                      = 0                                        nếu ticker_df[k] = 0
    tf[k, ticker, q]  = kw_{k}[ticker, q] / doc_length[ticker, q]
    tfidfx_{k}        = tf[k, ticker, q] · idf_x[k]

Trong đó:

- ``n_tickers`` là số ticker phân biệt trong tập dữ liệu.
- ``ticker_df[k]`` là số ticker mà **corpus gộp của ticker đó** (tổng ``kw_{k}``
  qua mọi kỳ của ticker) có chứa từ khóa ``k`` (tổng > 0). Đây chính là điểm
  khác biệt cốt lõi với v0: IDF tính trên chiều ticker, không phải trên chiều
  ``(ticker, quarter_id)``.
- ``doc_length`` là số token của ``combined_text`` tại kỳ đó (tối thiểu 1), dùng
  để chuẩn hóa TF giống v0 (:func:`pipeline.task9_kw_features.compute_tfidf_features`).

Dùng công thức IDF cổ điển ``ln(n/df)`` (không làm mượt) để tính chất phân biệt
cross-ticker được thể hiện rõ: từ khóa có mặt ở **mọi** ticker
(``ticker_df = n_tickers``) → ``idf_x = ln(1) = 0`` → mọi ``tfidfx_{k} = 0``; từ
khóa chỉ xuất hiện ở **một** ticker → ``idf_x = ln(n_tickers)`` (lớn nhất).

``compute_crossticker_tfidf`` là hàm thuần (pure) tính các cột ``tfidfx_{k}``
keyed trên ``(ticker, quarter_id)``. ``build_a4_features`` là entrypoint zero-arg
đọc ``data/aggregated/news_by_quarter.csv``, gộp các cột ``tfidfx_*`` lên khung
đặc trưng v0 base, và ghi ``data/features/keyword_features_A4.csv`` (Req 9.1).
Tệp v0 gốc ``data/features/keyword_features.csv`` không bị sửa đổi (Req 2.3).

Báo cáo so sánh với Baseline_v0 (Req 9.3) do CLI
``experiments/run_experiment.py::run_experiment("A4")`` tự sinh qua
Comparison_Reporter — module này chỉ cần tạo tệp đặc trưng hợp lệ, mergeable.

_Requirements: 9.1, 9.3, 2.1, 2.3_
"""

from __future__ import annotations

import logging
import math
import os
from typing import Dict, List, Optional

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
    "compute_crossticker_idf",
    "compute_crossticker_tfidf",
    "build_a4_features",
]

# ---------------------------------------------------------------------------
# Đường dẫn artifact của A4 (Req 9.1, 2.1, 2.3)
# ---------------------------------------------------------------------------

NEWS_BY_QUARTER_PATH = "data/aggregated/news_by_quarter.csv"
#: Tệp đặc trưng version hóa của A4 — KHÔNG ghi đè v0 (Req 2.1, 2.3).
OUTPUT_PATH = "data/features/keyword_features_A4.csv"

#: Cột khóa mergeable trên (ticker, quarter_id).
META_COLS = ["ticker", "quarter_id"]

#: Tên cột chứa độ dài tài liệu (số token) dùng chuẩn hóa TF.
DOC_LENGTH_COL = "doc_length"


# ---------------------------------------------------------------------------
# Thuật toán then chốt: IDF cross-ticker (Req 9.1)
# ---------------------------------------------------------------------------


def compute_crossticker_idf(
    df: pd.DataFrame,
    keywords: List[str],
) -> Dict[str, float]:
    """Tính IDF cross-ticker cho mỗi từ khóa (Req 9.1).

    Tần suất tài liệu được tính trên **chiều ticker**: ``ticker_df[k]`` là số
    ticker mà corpus gộp của ticker đó (tổng ``kw_{k}`` qua mọi kỳ) chứa từ khóa
    ``k``. IDF dùng công thức cổ điển không làm mượt:

    .. code-block:: text

        idf_x[k] = ln( n_tickers / ticker_df[k] )   nếu ticker_df[k] > 0
                 = 0                                  nếu ticker_df[k] = 0

    Tính chất (Req 9.1):

    - Từ khóa có mặt ở **mọi** ticker → ``idf_x = ln(1) = 0`` (ít phân biệt).
    - Từ khóa chỉ ở **một** ticker → ``idf_x = ln(n_tickers)`` (phân biệt cao).
    - Từ khóa không xuất hiện ở ticker nào → ``idf_x = 0`` (an toàn, tránh ln(0)).

    Args:
        df: DataFrame có cột ``ticker`` và các cột số đếm thô ``kw_{k}``.
        keywords: Danh sách từ khóa cần tính IDF.

    Returns:
        Dict ánh xạ từ khóa → giá trị IDF cross-ticker (không âm).
    """
    n_tickers = int(df["ticker"].nunique())
    idf: Dict[str, float] = {}

    if n_tickers == 0:
        return {kw: 0.0 for kw in keywords}

    kw_cols = [f"kw_{kw}" for kw in keywords]
    existing = [c for c in kw_cols if c in df.columns]

    # Tổng số đếm mỗi từ khóa theo từng ticker → có mặt (>0) hay không.
    if existing:
        ticker_totals = df.groupby("ticker")[existing].sum()
    else:
        ticker_totals = pd.DataFrame(index=df["ticker"].unique())

    for kw in keywords:
        col = f"kw_{kw}"
        if col in ticker_totals.columns:
            ticker_df = int((ticker_totals[col] > 0).sum())
        else:
            ticker_df = 0
        idf[kw] = math.log(n_tickers / ticker_df) if ticker_df > 0 else 0.0

    return idf


# ---------------------------------------------------------------------------
# Thuật toán then chốt: TF-IDF cross-ticker keyed trên (ticker, quarter_id)
# ---------------------------------------------------------------------------


def compute_crossticker_tfidf(
    df: pd.DataFrame,
    keywords: List[str],
) -> pd.DataFrame:
    """Tính các cột ``tfidfx_{k}`` cross-ticker keyed trên ``(ticker, quarter_id)``.

    Hàm thuần trung tâm dùng chung cho :func:`build_a4_features` và cho các test.
    Đầu vào phải chứa:

    - ``ticker``, ``quarter_id`` — khóa;
    - các cột số đếm thô ``kw_{k}`` của mỗi từ khóa;
    - ``doc_length`` — số token của tài liệu tại kỳ (tối thiểu 1) để chuẩn hóa TF.
      Nếu thiếu, TF được chuẩn hóa bằng tổng số đếm từ khóa của hàng (tối thiểu 1).

    Với mỗi từ khóa ``k`` (Req 9.1):

    .. code-block:: text

        tf[k]       = kw_{k} / doc_length
        tfidfx_{k}  = tf[k] · idf_x[k]

    trong đó ``idf_x[k]`` là IDF cross-ticker từ :func:`compute_crossticker_idf`.

    Args:
        df: DataFrame đầu vào (xem các cột bắt buộc ở trên).
        keywords: Danh sách từ khóa cần tính ``tfidfx_``.

    Returns:
        DataFrame gồm ``[ticker, quarter_id]`` + các cột ``tfidfx_{k}``.
    """
    idf = compute_crossticker_idf(df, keywords)

    # Độ dài tài liệu để chuẩn hóa TF. Nếu không có sẵn, dùng tổng số đếm từ khóa.
    if DOC_LENGTH_COL in df.columns:
        doc_length = df[DOC_LENGTH_COL].astype(float).replace(0, np.nan)
    else:
        kw_cols = [f"kw_{kw}" for kw in keywords if f"kw_{kw}" in df.columns]
        if kw_cols:
            doc_length = df[kw_cols].sum(axis=1).astype(float).replace(0, np.nan)
        else:
            doc_length = pd.Series(np.nan, index=df.index)

    out_cols: Dict[str, pd.Series] = {}
    for kw in keywords:
        col_raw = f"kw_{kw}"
        col_tfx = f"tfidfx_{kw}"
        if col_raw in df.columns:
            tf = df[col_raw].astype(float) / doc_length
            # doc_length == 0 → NaN → coi như 0 (không có token nào).
            out_cols[col_tfx] = (tf.fillna(0.0) * idf[kw]).astype(float)
        else:
            out_cols[col_tfx] = pd.Series(0.0, index=df.index)

    result = pd.DataFrame(
        {
            "ticker": df["ticker"].to_numpy(),
            "quarter_id": df["quarter_id"].to_numpy(),
        }
    )
    tfx_df = pd.DataFrame(out_cols, index=df.index).reset_index(drop=True)
    return pd.concat([result, tfx_df], axis=1)


# ---------------------------------------------------------------------------
# Xây dựng khung đặc trưng v0 base + A4 (Req 9.1, 2.1)
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
    ``combined_text`` ở cuối để khung sẵn sàng ghi ra tệp đặc trưng.

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


def build_a4_features(
    news_path: str = NEWS_BY_QUARTER_PATH,
    output_path: str = OUTPUT_PATH,
) -> pd.DataFrame:
    """Đọc news-by-quarter, tính A4 và ghi ``keyword_features_A4.csv`` (Req 9.1).

    Gộp các cột ``tfidfx_{k}`` (TF-IDF cross-ticker) lên khung đặc trưng v0 base,
    giữ khung khóa ``(ticker, quarter_id)`` mergeable với
    ``technical_features.csv`` (Req 2.1). KHÔNG sửa tệp v0
    ``data/features/keyword_features.csv`` (Req 2.3).

    Args:
        news_path: Đường dẫn ``news_by_quarter.csv`` đầu vào.
        output_path: Đường dẫn ghi tệp đặc trưng A4.

    Returns:
        DataFrame đặc trưng A4 đã ghi (rỗng nếu đầu vào lỗi).
    """
    df = _load_news(news_path)
    if df.empty:
        return pd.DataFrame()

    keywords_by_direction = get_curated_keywords()
    all_keywords = get_all_keywords_flat()

    # Khung v0 base (đã có kw_*, kw_norm_*, tfidf_*, sentiment, coverage).
    v0 = _prepare_v0_frame(df, keywords_by_direction)

    # Khung số đếm thô + độ dài tài liệu (còn combined_text) cho TF-IDF cross-ticker.
    base = compute_keyword_counts(df, all_keywords)
    base[DOC_LENGTH_COL] = (
        base["combined_text"].fillna("").apply(lambda t: max(len(t.split()), 1))
    )

    tfx = compute_crossticker_tfidf(base, all_keywords)

    # Gộp các cột tfidfx_ lên v0 base theo khóa (ticker, quarter_id).
    features = v0.merge(tfx, on=META_COLS, how="left")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    features.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(
        "Đã ghi đặc trưng A4 (%d hàng, %d cột) vào %s.",
        len(features),
        len(features.columns),
        output_path,
    )
    return features


if __name__ == "__main__":  # pragma: no cover - entrypoint
    logging.basicConfig(level=logging.INFO)
    build_a4_features()
