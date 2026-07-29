"""LLM_Annotator — A6: gán nhãn sentiment zero-shot bằng Gemini Flash (Req 8).

Thí nghiệm A6 dùng một mô hình ngôn ngữ lớn (Gemini Flash) như một **công cụ
gán nhãn sentiment nội dung** cho từng bài viết tin tức, rồi lưu kết quả cố
định vào cache để đảm bảo tái lập. Đây là tầng biểu diễn văn bản "cao nhất"
trong Hướng A: thay vì đếm từ khóa, ta hỏi trực tiếp mô hình về polarity nội
dung của bài (Req 8.1).

Nguyên tắc thiết kế then chốt của module này:

- **Prompt chỉ hỏi polarity nội dung, CẤM dự đoán giá** (Req 8.2): mô hình chỉ
  được đánh giá sắc thái nội dung bài viết là ``positive`` / ``negative`` /
  ``neutral`` kèm mức tin cậy, tuyệt đối không được suy đoán diễn biến giá cổ
  phiếu.
- **temperature = 0** (Req 8.3): mọi lời gọi mô hình dùng ``TEMPERATURE = 0.0``
  và giá trị này được ghi vào cache để truy vết.
- **Cache cố định** (Req 8.4, 8.5): mỗi bài được khóa bằng ``content_hash`` =
  SHA-256 của ``title + "\n" + description`` đã chuẩn hóa. Kết quả được ghi vào
  ``data/news/annotated/llm_sentiment.csv`` kèm ``model_version``,
  ``temperature``, ``annotated_at``. Bài đã có trong cache được **dùng lại**,
  không gọi lại mô hình.
- **Client injectable** (để test): lời gọi API được trừu tượng hóa qua giao
  thức :class:`SentimentClient`. Trong test, ta truyền một client giả (mock)
  nên KHÔNG gọi API thật. Client Gemini thật chỉ được **khởi tạo lười (lazy)**
  khi thực sự có bài cần gán nhãn, nên import module hay chạy test mà không có
  API key vẫn không lỗi.
- **Chịu lỗi API** (Req 8.8): mỗi lời gọi bọc trong try/except; bài lỗi được
  ghi log kèm ``content_hash`` và bỏ qua, quá trình tiếp tục với các bài còn
  lại. Nhờ cache, lần chạy sau chỉ xử lý các bài còn thiếu.

Hàm :func:`aggregate_llm_features` gộp nhãn theo ``(ticker, quarter_id)`` thành
``llm_pos_ratio`` / ``llm_neg_ratio`` / ``llm_net_sentiment`` (Req 8.6), và
:func:`build_a6_features` là entrypoint zero-arg nạp bài viết đã tiền xử lý,
gọi :func:`annotate_articles` (dùng lại cache), gộp đặc trưng rồi ghi
``data/features/keyword_features_A6.csv`` (Req 8.7), giữ khung khóa
``(ticker, quarter_id)`` mergeable với ``technical_features.csv`` (Req 2.1).

_Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 2.1_
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, List, Optional, Protocol

import pandas as pd

from experiments.common.periods import quarter_id_from_date

logger = logging.getLogger(__name__)

__all__ = [
    "TEMPERATURE",
    "CACHE_COLUMNS",
    "VALID_SENTIMENTS",
    "A6_OUTPUT_PATH",
    "LLM_FEATURE_COLS",
    "META_COLS",
    "SentimentAnnotation",
    "SentimentClient",
    "build_sentiment_prompt",
    "content_hash",
    "annotate_articles",
    "aggregate_llm_features",
    "build_a6_features",
]

# ---------------------------------------------------------------------------
# Đường dẫn & hằng số cấu hình (Req 8.3, 8.4)
# ---------------------------------------------------------------------------

#: Nguồn bài viết đã tiền xử lý (title, description, ticker, date, ...).
PROCESSED_NEWS_PATH = "data/news/processed/all_news_processed.csv"
#: Khung khóa (ticker, quarter_id) để left-join cho mergeability (Req 2.1).
NEWS_BY_QUARTER_PATH = "data/aggregated/news_by_quarter.csv"
#: Cache nhãn sentiment cố định, được commit vào repo (Req 8.4, 15.2).
CACHE_PATH = "data/news/annotated/llm_sentiment.csv"
#: Tệp đặc trưng version hóa của A6 (Req 8.7, 2.1).
A6_OUTPUT_PATH = "data/features/keyword_features_A6.csv"
#: Mô hình mặc định.
DEFAULT_MODEL = "gemini-2.0-flash"
#: temperature luôn bằng 0 (Req 8.3).
TEMPERATURE = 0.0

#: Ba nhãn hợp lệ (Req 8.1).
VALID_SENTIMENTS = ("positive", "negative", "neutral")

#: Cột khóa mergeable trên (ticker, quarter_id) — Req 2.1.
META_COLS: List[str] = ["ticker", "quarter_id"]
#: Ba đặc trưng LLM tổng hợp (Req 8.6).
LLM_FEATURE_COLS: List[str] = ["llm_pos_ratio", "llm_neg_ratio", "llm_net_sentiment"]

#: Schema cache — thứ tự cột cố định (Req 8.4, xem Data Models trong design).
CACHE_COLUMNS: List[str] = [
    "content_hash",
    "ticker",
    "date",
    "title",
    "sentiment",
    "confidence",
    "model_version",
    "temperature",
    "annotated_at",
]


# ---------------------------------------------------------------------------
# Kết quả gán nhãn & giao thức client injectable (Req 8.1, test dùng mock)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SentimentAnnotation:
    """Kết quả gán nhãn sentiment cho một bài viết.

    Attributes:
        sentiment: Một trong ``positive`` / ``negative`` / ``neutral`` (Req 8.1).
        confidence: Mức tin cậy trong ``[0, 1]`` do mô hình trả về (Req 8.1).
        model_version: Phiên bản mô hình cụ thể (ví dụ ``gemini-2.0-flash-001``)
            để truy vết (Req 8.4).
    """

    sentiment: str
    confidence: float
    model_version: str


class SentimentClient(Protocol):
    """Giao thức trừu tượng hóa lời gọi mô hình để test dùng được mock.

    Bất kỳ đối tượng nào có phương thức ``annotate(title, description)`` trả về
    một :class:`SentimentAnnotation` đều dùng được. Nhờ đó test có thể truyền
    một client giả (mock) mà KHÔNG gọi API thật, còn code sản xuất dùng
    :class:`GeminiSentimentClient` khởi tạo lười.
    """

    def annotate(self, title: str, description: str) -> SentimentAnnotation:
        """Trả về nhãn sentiment nội dung cho một bài viết."""
        ...


#: Kiểu factory tạo client mặc định (khởi tạo lười — Req 8.8 / an toàn import).
ClientFactory = Callable[[str], SentimentClient]


# ---------------------------------------------------------------------------
# Prompt: chỉ hỏi polarity nội dung, CẤM dự đoán giá (Req 8.2)
# ---------------------------------------------------------------------------


def build_sentiment_prompt(title: str, description: str) -> str:
    """Dựng prompt chỉ yêu cầu đánh giá polarity nội dung, cấm dự đoán giá.

    Prompt được thiết kế theo Req 8.2: mô hình chỉ đánh giá sắc thái *nội dung*
    của bài viết (tích cực / tiêu cực / trung tính) kèm mức tin cậy, và bị
    **cấm tường minh** suy đoán diễn biến giá cổ phiếu.

    Args:
        title: Tiêu đề bài viết.
        description: Mô tả bài viết (có thể rỗng).

    Returns:
        Chuỗi prompt hoàn chỉnh gửi tới mô hình.
    """
    title = (title or "").strip()
    description = (description or "").strip()

    return (
        "Bạn là công cụ phân tích sắc thái NỘI DUNG của tin tức tài chính "
        "tiếng Việt.\n"
        "Nhiệm vụ: đánh giá sắc thái (polarity) của NỘI DUNG bài viết dưới đây "
        "là một trong ba giá trị: positive, negative, neutral, kèm mức độ tin "
        "cậy (confidence) trong khoảng [0, 1].\n"
        "\n"
        "RÀNG BUỘC BẮT BUỘC:\n"
        "- CHỈ đánh giá sắc thái nội dung của chính bài viết.\n"
        "- TUYỆT ĐỐI KHÔNG dự đoán, suy luận hay bình luận về diễn biến giá cổ "
        "phiếu, xu hướng thị trường, hay khuyến nghị mua/bán.\n"
        "- Không thêm giải thích ngoài JSON.\n"
        "\n"
        "Trả về DUY NHẤT một đối tượng JSON theo đúng định dạng:\n"
        '{"sentiment": "positive|negative|neutral", "confidence": <số thực 0..1>}\n'
        "\n"
        f"Tiêu đề: {title}\n"
        f"Mô tả: {description}\n"
    )


# ---------------------------------------------------------------------------
# Khóa cache: content_hash (Req 8.4, 8.5)
# ---------------------------------------------------------------------------


def _normalize_text(text: str) -> str:
    """Chuẩn hóa văn bản trước khi băm: về str, strip, gộp khoảng trắng."""
    if text is None or (isinstance(text, float) and pd.isna(text)):
        text = ""
    text = str(text).strip().lower()
    # Gộp mọi chuỗi khoảng trắng (kể cả xuống dòng, tab) thành một dấu cách.
    return re.sub(r"\s+", " ", text)


def content_hash(title: str, description: str) -> str:
    """Tính SHA-256 của ``title + "\\n" + description`` đã chuẩn hóa (Req 8.4).

    Args:
        title: Tiêu đề bài viết.
        description: Mô tả bài viết (có thể là ``NaN``/rỗng).

    Returns:
        Chuỗi hex SHA-256 dùng làm khóa cache ổn định cho một bài viết.
    """
    normalized = _normalize_text(title) + "\n" + _normalize_text(description)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Client Gemini thật — khởi tạo LƯỜI (chỉ khi có bài cần gọi API)
# ---------------------------------------------------------------------------


class GeminiSentimentClient:
    """Client gọi Gemini Flash thật; import SDK được hoãn tới lúc gọi.

    SDK ``google-generativeai`` KHÔNG được import ở cấp module để việc import
    :mod:`experiments.a6_llm_sentiment` và chạy test (dùng mock client) không
    yêu cầu cài đặt SDK hay có API key.
    """

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model
        self._genai = None
        self._model_obj = None

    def _ensure_model(self):
        """Import SDK và khởi tạo model một lần (lazy)."""
        if self._model_obj is not None:
            return
        try:  # import hoãn — chỉ khi thực sự cần gọi API.
            import google.generativeai as genai
        except ImportError as exc:  # pragma: no cover - phụ thuộc môi trường
            raise RuntimeError(
                "Cần cài đặt 'google-generativeai' để gọi Gemini Flash thật. "
                "Trong test hãy truyền tham số client=<mock>."
            ) from exc

        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        self._genai = genai
        self._model_obj = genai.GenerativeModel(self.model)

    def annotate(self, title: str, description: str) -> SentimentAnnotation:  # pragma: no cover - gọi API thật
        """Gọi Gemini Flash (temperature=0) và phân tích kết quả JSON."""
        import json

        self._ensure_model()
        prompt = build_sentiment_prompt(title, description)
        response = self._model_obj.generate_content(
            prompt,
            generation_config={"temperature": TEMPERATURE},
        )
        raw = (getattr(response, "text", None) or "").strip()
        # Bóc khối JSON đầu tiên xuất hiện trong phản hồi.
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError(f"Phản hồi không chứa JSON hợp lệ: {raw!r}")
        payload = json.loads(match.group(0))

        sentiment = str(payload.get("sentiment", "")).strip().lower()
        if sentiment not in VALID_SENTIMENTS:
            raise ValueError(f"Sentiment không hợp lệ: {sentiment!r}")
        confidence = float(payload.get("confidence", 0.0))
        model_version = getattr(self, "model", DEFAULT_MODEL)
        return SentimentAnnotation(sentiment, confidence, model_version)


def _default_client_factory(model: str) -> SentimentClient:
    """Factory mặc định tạo client Gemini thật (khởi tạo lười).

    Chỉ được gọi khi có ít nhất một bài chưa nằm trong cache, nên môi trường
    test/không có API key vẫn an toàn.
    """
    return GeminiSentimentClient(model)


# ---------------------------------------------------------------------------
# Nạp cache hiện có (Req 8.5)
# ---------------------------------------------------------------------------


def _load_cache(cache_path: str) -> pd.DataFrame:
    """Nạp cache nếu tồn tại; trả DataFrame rỗng (đúng schema) nếu chưa có."""
    if not os.path.isfile(cache_path):
        return pd.DataFrame(columns=CACHE_COLUMNS)

    df = pd.read_csv(cache_path, encoding="utf-8", dtype={"content_hash": str})
    # Bổ sung cột thiếu để tương thích ngược nếu cache cũ thiếu cột nào đó.
    for col in CACHE_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    logger.info("Đã nạp %d nhãn từ cache %s.", len(df), cache_path)
    return df[CACHE_COLUMNS]


# ---------------------------------------------------------------------------
# Entrypoint chính: annotate_articles (Req 8.1–8.5, 8.8)
# ---------------------------------------------------------------------------


def annotate_articles(
    articles: pd.DataFrame,
    cache_path: str = CACHE_PATH,
    model: str = DEFAULT_MODEL,
    client: Optional[SentimentClient] = None,
    client_factory: ClientFactory = _default_client_factory,
) -> pd.DataFrame:
    """Gán nhãn sentiment nội dung cho từng bài viết, dùng cache cố định.

    Với mỗi bài viết:

    - Nếu ``content_hash`` đã có trong cache → **dùng lại** kết quả cũ, không
      gọi mô hình (Req 8.5).
    - Nếu chưa có → gọi ``client.annotate(title, description)`` (Gemini Flash,
      ``temperature = 0``, prompt cấm dự đoán giá — Req 8.1, 8.2, 8.3), ghi kết
      quả vào cache kèm ``content_hash``, ``model_version``, ``temperature``,
      ``annotated_at`` (Req 8.4).
    - Nếu lời gọi mô hình lỗi → ghi log bài lỗi và **tiếp tục** với bài kế
      (Req 8.8).

    Args:
        articles: DataFrame bài viết, tối thiểu có cột ``title`` (và tùy chọn
            ``description``, ``ticker``, ``date``). ``description`` có thể rỗng
            hoặc ``NaN`` — được xử lý an toàn.
        cache_path: Đường dẫn cache ``llm_sentiment.csv``.
        model: Tên mô hình dùng khi phải khởi tạo client mặc định.
        client: Client injectable. Nếu ``None``, client thật được **khởi tạo
            lười** qua ``client_factory`` chỉ khi có bài cần gọi API — nên test
            truyền mock sẽ không bao giờ chạm API thật.
        client_factory: Factory tạo client mặc định (mặc định là Gemini thật).

    Returns:
        DataFrame nhãn cho các bài viết đầu vào (đúng schema :data:`CACHE_COLUMNS`),
        gồm cả bài lấy lại từ cache lẫn bài mới gán. Bài bị lỗi API bị loại khỏi
        kết quả nhưng không làm dừng quá trình.
    """
    cache = _load_cache(cache_path)
    cached_by_hash = {
        str(row["content_hash"]): row for _, row in cache.iterrows()
    }

    if articles is None or articles.empty:
        logger.warning("Không có bài viết nào để gán nhãn.")
        return pd.DataFrame(columns=CACHE_COLUMNS)

    if "title" not in articles.columns:
        logger.error("DataFrame bài viết thiếu cột bắt buộc 'title'.")
        return pd.DataFrame(columns=CACHE_COLUMNS)

    result_rows: List[dict] = []
    new_rows: List[dict] = []
    seen_hashes: set = set()
    error_count = 0
    active_client: Optional[SentimentClient] = client

    for _, article in articles.iterrows():
        title = article.get("title", "")
        description = article.get("description", "")
        ticker = article.get("ticker", "")
        date = article.get("date", "")

        chash = content_hash(title, description)

        # Đã xử lý trong lượt chạy này (trùng lặp trong đầu vào) → bỏ qua.
        if chash in seen_hashes:
            continue

        # (Req 8.5) Đã có trong cache → dùng lại, KHÔNG gọi mô hình.
        if chash in cached_by_hash:
            cached_row = cached_by_hash[chash]
            result_rows.append({col: cached_row[col] for col in CACHE_COLUMNS})
            seen_hashes.add(chash)
            continue

        # Cần gọi mô hình → khởi tạo client lười nếu chưa có (Req 8.8 an toàn).
        if active_client is None:
            active_client = client_factory(model)

        try:
            annotation = active_client.annotate(str(title or ""), str(description or ""))
        except Exception as exc:  # noqa: BLE001 - Req 8.8: log + tiếp tục
            error_count += 1
            logger.warning(
                "Lỗi gọi mô hình cho bài (content_hash=%s, ticker=%s): %s. "
                "Bỏ qua bài này và tiếp tục.",
                chash,
                ticker,
                exc,
            )
            continue

        row = {
            "content_hash": chash,
            "ticker": ticker,
            "date": date,
            "title": title,
            "sentiment": annotation.sentiment,
            "confidence": annotation.confidence,
            "model_version": annotation.model_version,
            "temperature": TEMPERATURE,
            "annotated_at": datetime.now(timezone.utc).isoformat(),
        }
        new_rows.append(row)
        result_rows.append(row)
        seen_hashes.add(chash)

    # (Req 8.4) Ghi các nhãn mới vào cache (append vào cache hiện có).
    if new_rows:
        new_df = pd.DataFrame(new_rows, columns=CACHE_COLUMNS)
        # Tránh FutureWarning khi cache rỗng: chỉ concat khi cache có dữ liệu.
        updated_cache = (
            new_df if cache.empty else pd.concat([cache, new_df], ignore_index=True)
        )
        os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
        updated_cache.to_csv(cache_path, index=False, encoding="utf-8")
        logger.info(
            "Đã gán nhãn %d bài mới (tổng cache %d), ghi vào %s.",
            len(new_rows),
            len(updated_cache),
            cache_path,
        )
    else:
        logger.info("Không có bài mới cần gán nhãn (toàn bộ đã có trong cache).")

    if error_count:
        logger.warning("Có %d bài bị lỗi API và đã bị bỏ qua.", error_count)

    return pd.DataFrame(result_rows, columns=CACHE_COLUMNS)


# ---------------------------------------------------------------------------
# Gộp nhãn theo (ticker, quarter_id) → đặc trưng LLM (Req 8.6, 8.7, 2.1)
# ---------------------------------------------------------------------------


def aggregate_llm_features(
    annotations: pd.DataFrame,
    news_by_quarter_keys: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Gộp nhãn LLM theo ``(ticker, quarter_id)`` thành ba đặc trưng tổng hợp.

    Với mỗi nhóm ``(ticker, quarter_id)`` (Req 8.6):

    .. code-block:: text

        llm_pos_ratio     = count(sentiment == "positive") / n_bài_trong_nhóm
        llm_neg_ratio     = count(sentiment == "negative") / n_bài_trong_nhóm
        llm_net_sentiment = llm_pos_ratio − llm_neg_ratio

    ``quarter_id`` được suy ra từ cột ``date`` của mỗi nhãn qua
    :func:`experiments.common.periods.quarter_id_from_date`. Vì
    ``pos + neg + neutral`` tỷ lệ luôn cộng bằng 1 và
    ``net = pos − neg`` theo đúng công thức, kết quả thỏa Property 10.

    Args:
        annotations: DataFrame nhãn (schema :data:`CACHE_COLUMNS`), tối thiểu có
            ``ticker``, ``date``, ``sentiment``.
        news_by_quarter_keys: (tùy chọn) khung khóa ``(ticker, quarter_id)``. Nếu
            được cung cấp, kết quả được left-join lên khung này để mọi khóa có
            mặt trong ``news_by_quarter`` đều xuất hiện; nhóm không có nhãn được
            điền 0 cho cả ba tỷ lệ (đảm bảo mergeable — Req 2.1).

    Returns:
        DataFrame keyed trên ``(ticker, quarter_id)`` với các cột
        :data:`LLM_FEATURE_COLS`.
    """
    empty = pd.DataFrame(columns=META_COLS + LLM_FEATURE_COLS)

    if annotations is None or annotations.empty:
        logger.warning("Không có nhãn LLM nào để gộp.")
        agg = empty
    else:
        required = {"ticker", "date", "sentiment"}
        missing = required - set(annotations.columns)
        if missing:
            logger.error("DataFrame nhãn thiếu cột bắt buộc: %s", missing)
            return empty

        work = annotations[["ticker", "date", "sentiment"]].copy()
        # Suy ra quarter_id từ date; bỏ qua các hàng có date không hợp lệ.
        def _safe_qid(d):
            try:
                return quarter_id_from_date(d)
            except (ValueError, TypeError):
                return None

        work["quarter_id"] = work["date"].map(_safe_qid)
        invalid = work["quarter_id"].isna().sum()
        if invalid:
            logger.warning("Bỏ qua %d nhãn có 'date' không hợp lệ.", invalid)
            work = work[work["quarter_id"].notna()]

        if work.empty:
            agg = empty
        else:
            work["sentiment"] = work["sentiment"].astype(str).str.strip().str.lower()

            grouped = work.groupby(META_COLS, sort=True)
            total = grouped.size()
            pos = grouped["sentiment"].apply(lambda s: (s == "positive").sum())
            neg = grouped["sentiment"].apply(lambda s: (s == "negative").sum())

            agg = pd.DataFrame(
                {
                    "llm_pos_ratio": pos / total,
                    "llm_neg_ratio": neg / total,
                }
            )
            agg["llm_net_sentiment"] = agg["llm_pos_ratio"] - agg["llm_neg_ratio"]
            agg = agg.reset_index()

    # (Req 2.1) Left-join lên khung khóa news_by_quarter nếu có, để mọi
    # (ticker, quarter_id) đều xuất hiện; nhóm thiếu nhãn điền 0.
    if news_by_quarter_keys is not None and not news_by_quarter_keys.empty:
        keys = news_by_quarter_keys[
            [c for c in META_COLS if c in news_by_quarter_keys.columns]
        ].drop_duplicates()
        if set(META_COLS).issubset(keys.columns):
            merged = keys.merge(agg, on=META_COLS, how="left")
            merged[LLM_FEATURE_COLS] = merged[LLM_FEATURE_COLS].fillna(0.0)
            return merged[META_COLS + LLM_FEATURE_COLS].reset_index(drop=True)
        logger.warning(
            "news_by_quarter_keys thiếu cột khóa %s; bỏ qua bước left-join.",
            META_COLS,
        )

    return agg[META_COLS + LLM_FEATURE_COLS].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Entrypoint ghi tệp: build_a6_features (Req 8.7, 2.1) — zero-arg như A1/A2
# ---------------------------------------------------------------------------


def _load_news_by_quarter_keys(news_path: str) -> Optional[pd.DataFrame]:
    """Nạp khung khóa ``(ticker, quarter_id)`` từ ``news_by_quarter.csv``.

    Trả về ``None`` nếu tệp không tồn tại hoặc thiếu cột khóa (khi đó
    :func:`aggregate_llm_features` chỉ phát ra các khóa có nhãn).
    """
    if not os.path.isfile(news_path):
        logger.warning(
            "Không tìm thấy %s; A6 chỉ phát ra khóa có nhãn LLM.", news_path
        )
        return None
    df = pd.read_csv(news_path, encoding="utf-8")
    if not set(META_COLS).issubset(df.columns):
        logger.warning("%s thiếu cột khóa %s; bỏ qua khung khóa.", news_path, META_COLS)
        return None
    return df[META_COLS].drop_duplicates()


def build_a6_features(
    processed_news_path: str = PROCESSED_NEWS_PATH,
    news_by_quarter_path: str = NEWS_BY_QUARTER_PATH,
    output_path: str = A6_OUTPUT_PATH,
    cache_path: str = CACHE_PATH,
    model: str = DEFAULT_MODEL,
    client: Optional[SentimentClient] = None,
    client_factory: ClientFactory = _default_client_factory,
) -> pd.DataFrame:
    """Nạp bài viết, gán nhãn (dùng cache), gộp và ghi ``keyword_features_A6.csv``.

    Luồng (Req 8.7, 2.1):

    1. Nạp bài viết đã tiền xử lý từ ``processed_news_path``.
    2. Gọi :func:`annotate_articles` để lấy/dùng lại nhãn từ cache (Req 8.5). Có
       thể tiêm ``client`` để test; mặc định client thật khởi tạo lười chỉ khi
       có bài cần gọi API.
    3. Gộp qua :func:`aggregate_llm_features`, left-join lên khung khóa
       ``news_by_quarter`` để mergeable với ``technical_features.csv`` (Req 2.1).
    4. Ghi tệp đặc trưng keyed trên ``(ticker, quarter_id)``.

    Đầu vào thiếu/rỗng được xử lý mềm: log lỗi và trả DataFrame rỗng (giống các
    builder khác).

    Args:
        processed_news_path: Đường dẫn bài viết đã tiền xử lý.
        news_by_quarter_path: Đường dẫn khung khóa ``(ticker, quarter_id)``.
        output_path: Đường dẫn ghi tệp đặc trưng A6.
        cache_path: Đường dẫn cache nhãn LLM.
        model: Tên mô hình dùng khi phải khởi tạo client mặc định.
        client: Client injectable (test truyền mock).
        client_factory: Factory tạo client mặc định.

    Returns:
        DataFrame đặc trưng A6 đã ghi (rỗng nếu đầu vào lỗi).
    """
    if not os.path.isfile(processed_news_path):
        logger.error("Không tìm thấy tệp bài viết: %s", processed_news_path)
        return pd.DataFrame(columns=META_COLS + LLM_FEATURE_COLS)

    articles = pd.read_csv(processed_news_path, encoding="utf-8")
    logger.info("Đã nạp %d bài viết từ %s.", len(articles), processed_news_path)

    annotations = annotate_articles(
        articles,
        cache_path=cache_path,
        model=model,
        client=client,
        client_factory=client_factory,
    )

    news_keys = _load_news_by_quarter_keys(news_by_quarter_path)
    features = aggregate_llm_features(annotations, news_by_quarter_keys=news_keys)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    features.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(
        "Đã ghi đặc trưng A6 (%d hàng, %d cột) vào %s.",
        len(features),
        len(features.columns),
        output_path,
    )
    return features


if __name__ == "__main__":  # pragma: no cover - entrypoint
    logging.basicConfig(level=logging.INFO)
    build_a6_features()