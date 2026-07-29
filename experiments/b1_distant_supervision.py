"""Distant_Supervision_Module — B1: nhãn nhiễu từ suất sinh lời ngắn hạn (Req 11).

Thí nghiệm B1 kiểm tra giả thuyết rằng tín hiệu văn bản tồn tại ở **cấp độ từng
bài viết** nhưng bị *tổng hợp theo quý làm mờ đi*. Ý tưởng "distant supervision":
thay vì gán nhãn sentiment thủ công, ta suy ra một **nhãn nhiễu (noisy label)**
cho mỗi bài viết từ suất sinh lời ngắn hạn của cổ phiếu ngay sau ngày đăng bài,
rồi huấn luyện một bộ phân loại sentiment cấp bài viết (TF-IDF + Logistic
Regression) trên các nhãn nhiễu đó. Cuối cùng, xác suất dự đoán của bộ phân loại
được tổng hợp theo ``(ticker, quarter_id)`` thành hai đặc trưng ``ds_pos_prob_mean``
và ``ds_net_sentiment`` để đưa qua cùng pipeline huấn luyện của baseline v0.

Ba lớp bảo vệ chống rò rỉ dữ liệu thời gian (Req 11.5, 11.6, 11.7):

1. **Nhãn nhiễu** dùng suất sinh lời trong cửa sổ ``[d+1, d+3]`` ngày giao dịch,
   nhưng **cắt tại ranh giới của kỳ (quý) chứa ngày d** — nếu d gần cuối kỳ, cửa
   sổ chỉ tính tới ngày giao dịch cuối cùng của kỳ đó (Req 11.1, 11.5). Việc cắt
   dùng :func:`experiments.common.periods.clip_return_window`.
2. **Bộ phân loại** chỉ được fit trên các bài đăng trong các kỳ ``< Train_Cutoff``
   (Req 11.6), thực thi qua :func:`select_training_articles`.
3. **Đặc trưng cho kỳ q** chỉ tổng hợp xác suất của các bài đăng trong kỳ q
   (Req 11.7), thực thi qua :func:`aggregate_ds_features`.

Quy ước tính suất sinh lời (được kiểm thử bằng property test P13):

- **Giá gốc (base)**: giá đóng cửa (``close``) của ngày giao dịch gần nhất **tại
  hoặc trước** ngày đăng bài d. Với bài đăng đúng vào một ngày giao dịch, đây
  chính là ``close`` của ngày d; với bài đăng vào ngày không giao dịch (cuối
  tuần/nghỉ lễ), đây là ``close`` của phiên giao dịch liền trước.
- **Giá cuối (end)**: giá đóng cửa của **ngày giao dịch cuối cùng** trong cửa sổ
  ``[d+1, d+3]`` đã bị cắt tại ranh giới kỳ.
- ``return = (end − base) / base``. Nhãn được gán bởi :func:`classify_return`:
  ``positive`` nếu ``return >= +threshold``, ``negative`` nếu
  ``return <= −threshold``, ``neutral`` nếu ở giữa (ngưỡng ±2% mặc định, biên
  bao hàm — Req 11.2–11.4).

Xử lý lỗi (theo mục "Distant_Supervision" của thiết kế): ticker thiếu dữ liệu
giá, hoặc cửa sổ ``[d+1, d+3]`` rơi vào cuối kỳ không còn ngày giao dịch nào →
bài đó **không sinh được nhãn nhiễu** và bị loại (ghi log số bài bị loại), không
ném exception. Khi một kỳ không có bài nào, đặc trưng ``ds_*`` cho kỳ đó là
``NaN`` (giữ nguyên, không impute — imputer của pipeline xử lý sau).

_Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 2.1_
"""

from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline

from experiments.common.periods import (
    clip_return_window,
    quarter_bounds,
    quarter_id_from_date,
)

logger = logging.getLogger(__name__)

__all__ = [
    "DEFAULT_THRESHOLD",
    "RETURN_HORIZON_TRADING_DAYS",
    "DEFAULT_CUTOFF",
    "NOISY_LABELS",
    "DS_FEATURE_COLS",
    "META_COLS",
    "B1_OUTPUT_PATH",
    "DISTANT_SUPERVISION_REPORT_PATH",
    "classify_return",
    "load_prices",
    "select_return_trading_days",
    "compute_clipped_return",
    "build_noisy_labels",
    "select_training_articles",
    "train_article_classifier",
    "predict_article_probs",
    "aggregate_ds_features",
    "build_b1_features",
]

# ---------------------------------------------------------------------------
# Đường dẫn & hằng số cấu hình (Req 11.1–11.8, 2.1)
# ---------------------------------------------------------------------------

#: Nguồn bài viết đã tiền xử lý (title, description, ticker, date, text_tokenized).
PROCESSED_NEWS_PATH = "data/news/processed/all_news_processed.csv"
#: Khung khóa (ticker, quarter_id) để left-join cho mergeability (Req 2.1).
NEWS_BY_QUARTER_PATH = "data/aggregated/news_by_quarter.csv"
#: Thư mục chứa giá theo từng ticker: data/prices/<TICKER>.csv.
PRICES_DIR = "data/prices"
#: Tệp đặc trưng version hóa của B1 (Req 11.8, 2.1).
B1_OUTPUT_PATH = "data/features/keyword_features_B1.csv"
#: Báo cáo distant supervision (Req 11.8).
DISTANT_SUPERVISION_REPORT_PATH = "reports/distant_supervision_report.md"

#: Ngưỡng ±2% cho việc gán nhãn nhiễu (Req 11.2–11.4).
DEFAULT_THRESHOLD = 0.02
#: Cửa sổ suất sinh lời: 3 ngày giao dịch [d+1, d+3] (Req 11.1).
RETURN_HORIZON_TRADING_DAYS = 3
#: Train_Cutoff theo thời gian (Req 11.6, 4.1).
DEFAULT_CUTOFF = "2025Q1"

#: Ba nhãn nhiễu hợp lệ, thứ tự ổn định cho ma trận xác suất/AUC.
NOISY_LABELS = ("negative", "neutral", "positive")

#: Cột khóa mergeable trên (ticker, quarter_id) — Req 2.1.
META_COLS: List[str] = ["ticker", "quarter_id"]
#: Hai đặc trưng B1 tổng hợp (Req 11.7). Tiền tố ``ds_`` đã đăng ký là keyword.
DS_FEATURE_COLS: List[str] = ["ds_pos_prob_mean", "ds_net_sentiment"]


# ---------------------------------------------------------------------------
# Thuật toán thuần: phân loại nhãn theo ngưỡng ±threshold (Req 11.2–11.4)
# ---------------------------------------------------------------------------


def classify_return(ret: float, threshold: float = DEFAULT_THRESHOLD) -> str:
    """Gán nhãn nhiễu cho một giá trị suất sinh lời theo ngưỡng ±``threshold``.

    Quy tắc (biên bao hàm tại ±threshold — Req 11.2, 11.3, 11.4):

    .. code-block:: text

        return >= +threshold  → "positive"
        return <= −threshold  → "negative"
        ngược lại             → "neutral"

    Args:
        ret: Suất sinh lời (phân số, ví dụ ``0.02`` cho +2%).
        threshold: Ngưỡng dương (mặc định ``0.02``). Phải ``>= 0``.

    Returns:
        Một trong ``"positive"`` / ``"negative"`` / ``"neutral"``.

    Validates: Requirements 11.2, 11.3, 11.4.
    """
    if ret >= threshold:
        return "positive"
    if ret <= -threshold:
        return "negative"
    return "neutral"


# ---------------------------------------------------------------------------
# Nạp giá theo ticker
# ---------------------------------------------------------------------------


def load_prices(ticker: str, prices_dir: str = PRICES_DIR) -> Optional[pd.DataFrame]:
    """Nạp chuỗi giá ngày của một ``ticker`` từ ``data/prices/<TICKER>.csv``.

    Tệp giá có các cột ``date,open,high,low,close,volume`` (ngày giao dịch, sắp
    tăng dần; ngày không giao dịch đơn giản là không có dòng). Hàm chỉ trả về
    cột ``date`` (đã ép ``Timestamp``) và ``close``, đã sắp tăng dần.

    Args:
        ticker: Mã cổ phiếu.
        prices_dir: Thư mục chứa các tệp giá.

    Returns:
        DataFrame ``[date, close]`` đã sắp tăng dần, hoặc ``None`` nếu thiếu tệp
        giá cho ticker (Req error handling: ticker thiếu dữ liệu giá).
    """
    path = os.path.join(prices_dir, f"{ticker}.csv")
    if not os.path.isfile(path):
        return None
    df = pd.read_csv(path, encoding="utf-8", usecols=["date", "close"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date", kind="mergesort")
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Chọn ngày giao dịch của cửa sổ return, cắt tại ranh giới kỳ (Req 11.1, 11.5)
# ---------------------------------------------------------------------------


def select_return_trading_days(
    price_dates: pd.Series,
    d,
    quarter_id: Optional[str] = None,
    horizon: int = RETURN_HORIZON_TRADING_DAYS,
) -> List[pd.Timestamp]:
    """Chọn tối đa ``horizon`` ngày giao dịch của cửa sổ ``[d+1, d+3]``, đã cắt kỳ.

    Các ngày giao dịch được chọn là những ngày **sau** d (strictly greater), và
    bị **cắt tại ranh giới cuối của kỳ chứa d** qua
    :func:`experiments.common.periods.clip_return_window`, nên toàn bộ tập ngày
    trả về luôn nằm trong ``quarter_bounds(quarter_id)`` (Req 11.5, Property 13).

    Args:
        price_dates: ``Series`` các ngày giao dịch (``Timestamp``), sắp tăng dần.
        d: Ngày đăng bài (sẽ ép ``Timestamp``).
        quarter_id: Kỳ chứa d dạng ``"YYYYQn"``; mặc định suy từ d.
        horizon: Số ngày giao dịch tối đa của cửa sổ (mặc định 3).

    Returns:
        Danh sách tối đa ``horizon`` ``Timestamp`` (có thể rỗng nếu không còn
        ngày giao dịch nào trong kỳ sau d).
    """
    ts = pd.Timestamp(d)
    if quarter_id is None:
        quarter_id = quarter_id_from_date(ts)

    dates = pd.to_datetime(pd.Series(price_dates)).sort_values()

    # Các ngày giao dịch strictly sau d.
    future = dates[dates > ts]
    if future.empty:
        return []

    # Cửa sổ danh nghĩa bao trọn tối đa ``horizon`` ngày giao dịch đầu tiên sau d;
    # điểm cuối được cắt tại ranh giới kỳ chứa d bằng clip_return_window.
    nominal_end = future.iloc[min(horizon, len(future)) - 1]
    horizon_days = int((nominal_end - ts).days)
    _, window_end = clip_return_window(ts, horizon_days, quarter_id)

    selected = future[future <= window_end].head(horizon)
    return list(selected)


def compute_clipped_return(
    prices: pd.DataFrame,
    d,
    quarter_id: Optional[str] = None,
    horizon: int = RETURN_HORIZON_TRADING_DAYS,
) -> Optional[float]:
    """Tính suất sinh lời ``[d+1, d+3]`` đã cắt kỳ cho một bài viết (Req 11.1, 11.5).

    - **base** = ``close`` của ngày giao dịch gần nhất tại hoặc trước d.
    - **end** = ``close`` của ngày giao dịch cuối cùng trong cửa sổ đã cắt kỳ.
    - ``return = (end − base) / base``.

    Args:
        prices: DataFrame giá của ticker (``[date, close]`` sắp tăng dần).
        d: Ngày đăng bài.
        quarter_id: Kỳ chứa d; mặc định suy từ d.
        horizon: Số ngày giao dịch tối đa của cửa sổ.

    Returns:
        Suất sinh lời (float), hoặc ``None`` nếu không tính được (không có giá
        gốc tại/trước d, hoặc không còn ngày giao dịch nào trong kỳ sau d, hoặc
        giá gốc bằng 0).
    """
    if prices is None or prices.empty:
        return None

    ts = pd.Timestamp(d)
    dates = pd.to_datetime(prices["date"])

    # Giá gốc: close của ngày giao dịch gần nhất tại hoặc trước d.
    base_mask = dates <= ts
    if not base_mask.any():
        return None
    base_close = float(prices.loc[base_mask, "close"].iloc[-1])
    if base_close == 0.0:
        return None

    selected = select_return_trading_days(dates, ts, quarter_id, horizon)
    if not selected:
        return None

    end_date = selected[-1]
    end_close = float(prices.loc[dates == end_date, "close"].iloc[-1])
    return (end_close - base_close) / base_close


# ---------------------------------------------------------------------------
# Gán nhãn nhiễu cho toàn bộ bài viết (Req 11.1–11.5)
# ---------------------------------------------------------------------------


def build_noisy_labels(
    articles: pd.DataFrame,
    prices: Union[Dict[str, pd.DataFrame], pd.DataFrame],
    threshold: float = DEFAULT_THRESHOLD,
    horizon: int = RETURN_HORIZON_TRADING_DAYS,
) -> pd.DataFrame:
    """Gán nhãn nhiễu cho từng bài viết từ suất sinh lời ngắn hạn (Req 11.1–11.5).

    Với mỗi bài viết ``(ticker t, ngày d)``: tính suất sinh lời trong cửa sổ
    ``[d+1, d+3]`` ngày giao dịch, **cắt tại ranh giới kỳ chứa d**
    (:func:`compute_clipped_return`), rồi gán nhãn ``positive``/``negative``/
    ``neutral`` qua :func:`classify_return`.

    Bài viết bị **loại** (không sinh nhãn) khi: ticker thiếu dữ liệu giá, hoặc
    cửa sổ không còn ngày giao dịch nào trong kỳ (cuối kỳ). Số bài bị loại được
    ghi log, không ném exception.

    Args:
        articles: DataFrame bài viết, tối thiểu có ``ticker`` và ``date`` (và
            tùy chọn ``text_tokenized`` được giữ lại để huấn luyện classifier).
        prices: Nguồn giá — hoặc ``dict[ticker -> DataFrame(date, close)]``,
            hoặc một DataFrame dài duy nhất có cột ``ticker`` (được nhóm nội
            bộ). Dạng dict là được khuyến nghị vì rõ ràng và dễ kiểm thử nhất.
        threshold: Ngưỡng ±% gán nhãn (mặc định ``0.02``).
        horizon: Số ngày giao dịch của cửa sổ (mặc định 3).

    Returns:
        DataFrame các bài **có nhãn**, gồm ``[ticker, date, quarter_id,
        text_tokenized, noisy_return, noisy_label]``. Có thể rỗng nếu không bài
        nào sinh được nhãn.
    """
    empty = pd.DataFrame(
        columns=[
            "ticker",
            "date",
            "quarter_id",
            "text_tokenized",
            "noisy_return",
            "noisy_label",
        ]
    )
    if articles is None or articles.empty:
        logger.warning("Không có bài viết nào để gán nhãn nhiễu.")
        return empty

    required = {"ticker", "date"}
    missing = required - set(articles.columns)
    if missing:
        logger.error("DataFrame bài viết thiếu cột bắt buộc: %s", missing)
        return empty

    # Chuẩn hóa nguồn giá về dict[ticker -> DataFrame(date, close)].
    if isinstance(prices, dict):
        prices_by_ticker = prices
    elif isinstance(prices, pd.DataFrame) and "ticker" in prices.columns:
        prices_by_ticker = {
            t: g[["date", "close"]].copy() for t, g in prices.groupby("ticker")
        }
    else:
        logger.error(
            "Tham số 'prices' phải là dict[ticker->DataFrame] hoặc DataFrame "
            "dài có cột 'ticker'."
        )
        return empty

    rows: List[Dict[str, object]] = []
    n_excluded_no_price = 0
    n_excluded_no_window = 0

    for _, art in articles.iterrows():
        ticker = art["ticker"]
        raw_date = art["date"]
        ts = pd.Timestamp(raw_date) if not pd.isna(raw_date) else pd.NaT
        if pd.isna(ts):
            n_excluded_no_window += 1
            continue

        tk_prices = prices_by_ticker.get(ticker)
        if tk_prices is None or len(tk_prices) == 0:
            n_excluded_no_price += 1
            continue
        # Bảo đảm cột date là Timestamp và đã sắp xếp.
        if not np.issubdtype(tk_prices["date"].dtype, np.datetime64):
            tk_prices = tk_prices.copy()
            tk_prices["date"] = pd.to_datetime(tk_prices["date"], errors="coerce")
            tk_prices = tk_prices.dropna(subset=["date"]).sort_values("date")

        quarter_id = quarter_id_from_date(ts)
        ret = compute_clipped_return(tk_prices, ts, quarter_id, horizon)
        if ret is None:
            n_excluded_no_window += 1
            continue

        rows.append(
            {
                "ticker": ticker,
                "date": ts,
                "quarter_id": quarter_id,
                "text_tokenized": art.get("text_tokenized", ""),
                "noisy_return": ret,
                "noisy_label": classify_return(ret, threshold),
            }
        )

    n_excluded = n_excluded_no_price + n_excluded_no_window
    if n_excluded:
        logger.info(
            "Đã loại %d bài khi gán nhãn nhiễu (%d thiếu giá, %d không còn "
            "ngày giao dịch trong kỳ).",
            n_excluded,
            n_excluded_no_price,
            n_excluded_no_window,
        )

    if not rows:
        return empty
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Lọc bài huấn luyện theo kỳ < cutoff (Req 11.6) — hàm thuần để test P14
# ---------------------------------------------------------------------------


def select_training_articles(
    labeled_articles: pd.DataFrame,
    cutoff: str = DEFAULT_CUTOFF,
) -> pd.DataFrame:
    """Chọn tập bài huấn luyện: chỉ bài thuộc kỳ ``< cutoff`` (Req 11.6).

    Vì ``quarter_id`` dạng ``"YYYYQn"`` có thứ tự lexical trùng thứ tự thời gian,
    điều kiện "kỳ nhỏ hơn cutoff" được kiểm bằng so sánh chuỗi thuần
    ``quarter_id < cutoff``. Đây là hàm thuần được :func:`train_article_classifier`
    ủy quyền tới, và được property test P14 kiểm trực tiếp.

    Args:
        labeled_articles: DataFrame có ít nhất cột ``quarter_id`` (thường là kết
            quả của :func:`build_noisy_labels`).
        cutoff: Train_Cutoff dạng ``"YYYYQn"`` (mặc định ``"2025Q1"``).

    Returns:
        DataFrame con chỉ gồm các bài có ``quarter_id < cutoff`` (giữ nguyên thứ
        tự và các cột đầu vào).

    Validates: Requirements 11.6.
    """
    if labeled_articles is None or labeled_articles.empty:
        return labeled_articles
    if "quarter_id" not in labeled_articles.columns:
        raise ValueError("labeled_articles thiếu cột 'quarter_id'.")
    mask = labeled_articles["quarter_id"].astype(str) < str(cutoff)
    return labeled_articles[mask].copy()


# ---------------------------------------------------------------------------
# Bộ phân loại sentiment cấp bài viết: TF-IDF + Logistic Regression (Req 11.6)
# ---------------------------------------------------------------------------


def train_article_classifier(
    labeled_articles: pd.DataFrame,
    cutoff: str = DEFAULT_CUTOFF,
    text_col: str = "text_tokenized",
    label_col: str = "noisy_label",
) -> Pipeline:
    """Huấn luyện bộ phân loại sentiment cấp bài viết trên nhãn nhiễu (Req 11.6).

    Lọc bài về các kỳ ``< cutoff`` qua :func:`select_training_articles` **trước
    khi** fit (chống rò rỉ thời gian — Req 11.6), rồi fit một
    :class:`sklearn.pipeline.Pipeline` gồm :class:`TfidfVectorizer` +
    :class:`LogisticRegression` (đa lớp, ``class_weight="balanced"``,
    ``max_iter=1000``, ``random_state=42``) trên cột ``text_tokenized``.

    Xử lý ca thoái hóa: nếu sau khi lọc còn **ít hơn 2 lớp nhãn** khác nhau (hoặc
    tập rỗng), không thể fit một bộ phân loại đa lớp có ý nghĩa → ném
    :class:`ValueError` với thông báo rõ ràng để nơi gọi (``build_b1_features``)
    xử lý mềm.

    Args:
        labeled_articles: DataFrame nhãn nhiễu (từ :func:`build_noisy_labels`),
            có ``text_tokenized``, ``noisy_label`` và ``quarter_id``.
        cutoff: Train_Cutoff dạng ``"YYYYQn"``; bài kỳ ``>= cutoff`` bị loại
            khỏi tập fit.
        text_col: Tên cột văn bản đã token hóa.
        label_col: Tên cột nhãn nhiễu.

    Returns:
        Pipeline đã fit; thuộc tính ``classes_`` của bước ``clf`` cho biết thứ
        tự lớp của ``predict_proba``.

    Raises:
        ValueError: nếu tập huấn luyện (sau lọc) rỗng hoặc có < 2 lớp nhãn.

    Validates: Requirements 11.6.
    """
    train_df = select_training_articles(labeled_articles, cutoff)
    if train_df is None or train_df.empty:
        raise ValueError(
            f"Không có bài huấn luyện nào thuộc kỳ < {cutoff} để fit classifier."
        )

    n_classes = train_df[label_col].nunique()
    if n_classes < 2:
        raise ValueError(
            "Cần ít nhất 2 lớp nhãn khác nhau để huấn luyện bộ phân loại đa lớp; "
            f"tập train (kỳ < {cutoff}) chỉ có {n_classes} lớp."
        )

    texts = train_df[text_col].fillna("").astype(str)
    labels = train_df[label_col].astype(str)

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(min_df=1)),
            (
                "clf",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ]
    )
    pipeline.fit(texts, labels)
    logger.info(
        "Đã fit article classifier trên %d bài (kỳ < %s), %d lớp: %s.",
        len(train_df),
        cutoff,
        n_classes,
        list(pipeline.named_steps["clf"].classes_),
    )
    return pipeline


def predict_article_probs(
    classifier: Pipeline,
    articles: pd.DataFrame,
    text_col: str = "text_tokenized",
) -> pd.DataFrame:
    """Dự đoán xác suất pos/neg cho từng bài rồi trả khung để aggregate.

    Ánh xạ ``predict_proba`` về hai cột ``pos_prob`` và ``neg_prob`` bằng cách
    tra chỉ số lớp trong ``classifier.classes_`` (không giả định thứ tự lớp cố
    định — an toàn với mọi thứ tự sklearn sinh ra). Lớp không có mặt (ví dụ tập
    train thiếu ``positive``) → xác suất tương ứng bằng 0.

    Args:
        classifier: Pipeline đã fit từ :func:`train_article_classifier`.
        articles: DataFrame bài viết có ``ticker``, ``quarter_id`` và ``text``.
        text_col: Tên cột văn bản.

    Returns:
        DataFrame ``[ticker, quarter_id, pos_prob, neg_prob]`` (một dòng/bài).
    """
    out_cols = ["ticker", "quarter_id", "pos_prob", "neg_prob"]
    if articles is None or articles.empty:
        return pd.DataFrame(columns=out_cols)

    texts = articles[text_col].fillna("").astype(str)
    proba = classifier.predict_proba(texts)
    classes = list(classifier.named_steps["clf"].classes_)

    pos_idx = classes.index("positive") if "positive" in classes else None
    neg_idx = classes.index("negative") if "negative" in classes else None

    n = len(articles)
    pos_prob = proba[:, pos_idx] if pos_idx is not None else np.zeros(n)
    neg_prob = proba[:, neg_idx] if neg_idx is not None else np.zeros(n)

    return pd.DataFrame(
        {
            "ticker": articles["ticker"].to_numpy(),
            "quarter_id": articles["quarter_id"].to_numpy(),
            "pos_prob": pos_prob,
            "neg_prob": neg_prob,
        }
    )


# ---------------------------------------------------------------------------
# Tổng hợp đặc trưng theo (ticker, quarter_id) (Req 11.7) — hàm thuần để test P4
# ---------------------------------------------------------------------------


def aggregate_ds_features(
    article_probs_df: pd.DataFrame,
    news_by_quarter_keys: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Gộp xác suất cấp bài theo ``(ticker, quarter_id)`` thành đặc trưng B1.

    Với mỗi nhóm ``(ticker, quarter_id)`` — **chỉ gồm các bài đăng trong kỳ đó**
    (Req 11.7):

    .. code-block:: text

        ds_pos_prob_mean  = mean(pos_prob)
        ds_net_sentiment  = mean(pos_prob) − mean(neg_prob)

    Vì mỗi bài đã mang sẵn ``quarter_id`` của kỳ đăng bài, việc nhóm theo
    ``(ticker, quarter_id)`` đảm bảo đặc trưng của kỳ q chỉ phụ thuộc các bài
    của kỳ q — nên thay đổi dữ liệu bài của kỳ ``q' > q`` không thể ảnh hưởng
    đặc trưng tại q (Property 4 / Req 11.7, đây là hàm thuần được P4 kiểm).

    Args:
        article_probs_df: DataFrame ``[ticker, quarter_id, pos_prob, neg_prob]``
            (một dòng mỗi bài). Nếu chứa cột ``date`` thay vì ``quarter_id``,
            ``quarter_id`` được suy ra từ ``date``.
        news_by_quarter_keys: (tùy chọn) khung khóa ``(ticker, quarter_id)``.
            Nếu cung cấp, kết quả được left-join lên khung này để mọi khóa của
            ``news_by_quarter`` đều xuất hiện; kỳ không có bài → ``NaN`` (giữ
            nguyên, không impute — Req 2.1 mergeable + design "keep NaN").

    Returns:
        DataFrame keyed trên ``(ticker, quarter_id)`` với các cột
        :data:`DS_FEATURE_COLS`.
    """
    empty = pd.DataFrame(columns=META_COLS + DS_FEATURE_COLS)

    if article_probs_df is None or article_probs_df.empty:
        agg = empty
    else:
        work = article_probs_df.copy()
        if "quarter_id" not in work.columns:
            if "date" not in work.columns:
                raise ValueError(
                    "article_probs_df cần cột 'quarter_id' hoặc 'date'."
                )
            work["quarter_id"] = work["date"].map(quarter_id_from_date)

        grouped = work.groupby(META_COLS, sort=True)
        pos_mean = grouped["pos_prob"].mean()
        neg_mean = grouped["neg_prob"].mean()

        agg = pd.DataFrame(
            {
                "ds_pos_prob_mean": pos_mean,
                "ds_net_sentiment": pos_mean - neg_mean,
            }
        ).reset_index()

    # Left-join lên khung khóa news_by_quarter nếu có; kỳ thiếu bài → NaN.
    if news_by_quarter_keys is not None and not news_by_quarter_keys.empty:
        keys = news_by_quarter_keys[
            [c for c in META_COLS if c in news_by_quarter_keys.columns]
        ].drop_duplicates()
        if set(META_COLS).issubset(keys.columns):
            merged = keys.merge(agg, on=META_COLS, how="left")
            return merged[META_COLS + DS_FEATURE_COLS].reset_index(drop=True)
        logger.warning(
            "news_by_quarter_keys thiếu cột khóa %s; bỏ qua bước left-join.",
            META_COLS,
        )

    return agg[META_COLS + DS_FEATURE_COLS].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Báo cáo distant supervision (Req 11.8)
# ---------------------------------------------------------------------------


def _macro_ovr_auc(
    classifier: Pipeline,
    labeled_articles: pd.DataFrame,
    text_col: str = "text_tokenized",
    label_col: str = "noisy_label",
) -> Optional[float]:
    """AUC macro one-vs-rest của classifier trên nhãn nhiễu cấp bài (Req 11.8).

    Tính trên toàn bộ ``labeled_articles`` (nhãn nhiễu cấp bài viết). Trả về
    ``None`` nếu không tính được (một lớp nhãn, thiếu dữ liệu).
    """
    if labeled_articles is None or labeled_articles.empty:
        return None
    y_true = labeled_articles[label_col].astype(str)
    if y_true.nunique() < 2:
        return None
    texts = labeled_articles[text_col].fillna("").astype(str)
    try:
        proba = classifier.predict_proba(texts)
        classes = list(classifier.named_steps["clf"].classes_)
        return float(
            roc_auc_score(
                y_true,
                proba,
                labels=classes,
                multi_class="ovr",
                average="macro",
            )
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Không tính được macro-OvR AUC: %s.", exc)
        return None


def _write_distant_supervision_report(
    labeled_articles: pd.DataFrame,
    auc: Optional[float],
    n_train: int,
    n_excluded: int,
    report_path: str = DISTANT_SUPERVISION_REPORT_PATH,
) -> str:
    """Ghi ``reports/distant_supervision_report.md`` (Req 11.8).

    Gồm: (a) phân phối nhãn nhiễu pos/neg/neutral; (b) AUC macro-OvR của
    classifier trên nhãn nhiễu cấp bài; (c) một mục granularity analysis ngắn.
    """
    dist = (
        labeled_articles["noisy_label"].value_counts().to_dict()
        if labeled_articles is not None and not labeled_articles.empty
        else {}
    )
    total = int(sum(dist.values()))
    auc_txt = "not computed" if auc is None else f"{auc:.4f}"

    lines = [
        "# Báo cáo Distant Supervision (B1)\n",
        "## 1. Phân phối nhãn nhiễu (noisy label)\n",
        "Nhãn nhiễu suy ra từ suất sinh lời cửa sổ [d+1, d+3] ngày giao dịch, "
        "cắt tại ranh giới kỳ chứa ngày đăng bài (ngưỡng ±2%).\n",
        "| Nhãn | Số bài | Tỷ lệ |",
        "|---|---|---|",
    ]
    for lab in NOISY_LABELS:
        cnt = int(dist.get(lab, 0))
        pct = (cnt / total * 100.0) if total else 0.0
        lines.append(f"| {lab} | {cnt} | {pct:.1f}% |")
    lines.append(f"| **tổng** | **{total}** | 100% |")
    lines.append("")
    lines.append(
        f"Số bài dùng huấn luyện classifier (kỳ < cutoff): **{n_train}**. "
        f"Số bài bị loại (thiếu giá / cuối kỳ không còn ngày giao dịch): "
        f"**{n_excluded}**.\n"
    )

    lines.append("## 2. Chất lượng bộ phân loại cấp bài viết\n")
    lines.append(
        f"AUC macro one-vs-rest trên nhãn nhiễu cấp bài viết: **{auc_txt}**.\n"
    )

    lines.append("## 3. Granularity analysis\n")
    lines.append(
        "B1 kiểm tra giả thuyết rằng tín hiệu văn bản tồn tại ở cấp độ từng bài "
        "viết nhưng bị *tổng hợp theo quý làm mờ*. Bộ phân loại được huấn luyện "
        "trên nhãn nhiễu cấp bài (distant supervision từ suất sinh lời ngắn "
        "hạn); xác suất dự đoán sau đó được gộp theo quý thành "
        "``ds_pos_prob_mean`` và ``ds_net_sentiment``. Nếu AUC cấp bài cao hơn "
        "đáng kể so với giá trị dự báo của đặc trưng gộp theo quý (Δ(C−A) ở báo "
        "cáo so sánh B1), điều đó ủng hộ giả thuyết mất mát thông tin do tổng "
        "hợp theo kỳ (within-period absorption). Ngược lại, nếu ngay cả tín "
        "hiệu cấp bài cũng yếu, kết quả củng cố thêm kết luận âm của Hướng A.\n"
    )

    report = "\n".join(lines).rstrip() + "\n"
    os.makedirs(os.path.dirname(report_path) or ".", exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(report)
    logger.info("Đã ghi báo cáo distant supervision: %s.", report_path)
    return report_path


# ---------------------------------------------------------------------------
# Entrypoint ghi tệp: build_b1_features (Req 11.7, 11.8, 2.1) — zero-arg
# ---------------------------------------------------------------------------


def _load_news_by_quarter_keys(news_path: str) -> Optional[pd.DataFrame]:
    """Nạp khung khóa ``(ticker, quarter_id)`` từ ``news_by_quarter.csv``.

    Trả về ``None`` nếu tệp không tồn tại hoặc thiếu cột khóa.
    """
    if not os.path.isfile(news_path):
        logger.warning(
            "Không tìm thấy %s; B1 chỉ phát ra khóa có bài.", news_path
        )
        return None
    df = pd.read_csv(news_path, encoding="utf-8")
    if not set(META_COLS).issubset(df.columns):
        logger.warning("%s thiếu cột khóa %s; bỏ qua khung khóa.", news_path, META_COLS)
        return None
    return df[META_COLS].drop_duplicates()


def _load_all_prices(tickers, prices_dir: str = PRICES_DIR) -> Dict[str, pd.DataFrame]:
    """Nạp giá cho tập ``tickers`` thành dict; ticker thiếu tệp bị bỏ qua."""
    prices: Dict[str, pd.DataFrame] = {}
    n_missing = 0
    for t in sorted(set(tickers)):
        df = load_prices(t, prices_dir)
        if df is None or df.empty:
            n_missing += 1
            continue
        prices[t] = df
    if n_missing:
        logger.info("Thiếu dữ liệu giá cho %d ticker.", n_missing)
    return prices


def build_b1_features(
    processed_news_path: str = PROCESSED_NEWS_PATH,
    news_by_quarter_path: str = NEWS_BY_QUARTER_PATH,
    prices_dir: str = PRICES_DIR,
    output_path: str = B1_OUTPUT_PATH,
    cutoff: str = DEFAULT_CUTOFF,
    threshold: float = DEFAULT_THRESHOLD,
    report_path: str = DISTANT_SUPERVISION_REPORT_PATH,
) -> pd.DataFrame:
    """Xây dựng đặc trưng B1 và ghi ``keyword_features_B1.csv`` (Req 11.7, 11.8).

    Luồng end-to-end:

    1. Nạp bài viết đã tiền xử lý và giá theo từng ticker.
    2. Gán nhãn nhiễu cho từng bài (:func:`build_noisy_labels`, Req 11.1–11.5).
    3. Huấn luyện article classifier CHỈ trên bài kỳ ``< cutoff``
       (:func:`train_article_classifier`, Req 11.6).
    4. Dự đoán xác suất pos/neg cho **mọi** bài có nhãn, rồi tổng hợp theo
       ``(ticker, quarter_id)`` thành ``ds_pos_prob_mean`` / ``ds_net_sentiment``
       (:func:`aggregate_ds_features`, Req 11.7), left-join lên khung khóa
       ``news_by_quarter`` để mergeable với ``technical_features.csv`` (Req 2.1);
       kỳ thiếu bài → ``NaN``.
    5. Ghi ``keyword_features_B1.csv`` và ``distant_supervision_report.md``
       (phân phối nhãn + AUC + granularity — Req 11.8).

    Đầu vào thiếu/rỗng được xử lý mềm: log lỗi và trả DataFrame rỗng (giống các
    builder khác). Nếu không đủ lớp nhãn để fit classifier, cũng trả rỗng mềm.

    Args:
        processed_news_path: Đường dẫn bài viết đã tiền xử lý.
        news_by_quarter_path: Đường dẫn khung khóa ``(ticker, quarter_id)``.
        prices_dir: Thư mục giá theo ticker.
        output_path: Đường dẫn ghi tệp đặc trưng B1.
        cutoff: Train_Cutoff dạng ``"YYYYQn"``.
        threshold: Ngưỡng ±% gán nhãn nhiễu.
        report_path: Đường dẫn ghi báo cáo distant supervision.

    Returns:
        DataFrame đặc trưng B1 đã ghi (rỗng nếu đầu vào lỗi/không đủ nhãn).
    """
    empty = pd.DataFrame(columns=META_COLS + DS_FEATURE_COLS)

    if not os.path.isfile(processed_news_path):
        logger.error("Không tìm thấy tệp bài viết: %s", processed_news_path)
        return empty

    articles = pd.read_csv(processed_news_path, encoding="utf-8")
    logger.info("Đã nạp %d bài viết từ %s.", len(articles), processed_news_path)

    required = {"ticker", "date"}
    if not required.issubset(articles.columns):
        logger.error("Tệp bài viết thiếu cột bắt buộc %s.", required)
        return empty

    # Nạp giá cho các ticker xuất hiện trong bài viết.
    prices = _load_all_prices(articles["ticker"].dropna().unique(), prices_dir)
    if not prices:
        logger.error("Không nạp được dữ liệu giá cho bất kỳ ticker nào.")
        return empty

    n_articles_in = len(articles)
    labeled = build_noisy_labels(articles, prices, threshold=threshold)
    n_excluded = n_articles_in - len(labeled)
    if labeled.empty:
        logger.error("Không gán được nhãn nhiễu cho bài nào; bỏ qua B1.")
        return empty

    # Huấn luyện classifier chỉ trên kỳ < cutoff (Req 11.6).
    try:
        classifier = train_article_classifier(labeled, cutoff=cutoff)
    except ValueError as exc:
        logger.error("Không huấn luyện được article classifier: %s", exc)
        return empty

    n_train = len(select_training_articles(labeled, cutoff))

    # Dự đoán xác suất cho mọi bài có nhãn, tổng hợp theo (ticker, quarter_id).
    article_probs = predict_article_probs(classifier, labeled)
    news_keys = _load_news_by_quarter_keys(news_by_quarter_path)
    features = aggregate_ds_features(article_probs, news_by_quarter_keys=news_keys)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    features.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(
        "Đã ghi đặc trưng B1 (%d hàng, %d cột) vào %s.",
        len(features),
        len(features.columns),
        output_path,
    )

    # Báo cáo distant supervision (Req 11.8).
    auc = _macro_ovr_auc(classifier, labeled)
    try:
        _write_distant_supervision_report(
            labeled, auc, n_train, n_excluded, report_path=report_path
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Không ghi được báo cáo distant supervision: %s.", exc)

    return features


if __name__ == "__main__":  # pragma: no cover - entrypoint
    logging.basicConfig(level=logging.INFO)
    build_b1_features()
