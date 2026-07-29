"""Embedding_Builder — A5: đặc trưng nhúng ngữ nghĩa bằng PhoBERT (Req 9).

Thí nghiệm A5 (tùy chọn) thay cách biểu diễn văn bản dạng túi-từ-khóa (bag of
keywords) của baseline v0 bằng **vector nhúng ngữ nghĩa dày** (dense semantic
embedding) sinh từ mô hình ngôn ngữ tiếng Việt **PhoBERT** (``vinai/phobert-base``).
Với mỗi cặp ``(ticker, quarter_id)``, corpus gộp ``combined_text`` của kỳ được
mã hóa thành một vector ``d`` chiều bằng **mean-pooling** trạng thái ẩn cuối
cùng của PhoBERT, tạo ra các cột đặc trưng ``emb_0, emb_1, ..., emb_{d-1}``
(Req 9.2).

``compute_embedding_features`` là hàm thuần (pure) nhận một *encoder* có thể
tiêm vào (injectable) và sinh các cột ``emb_*`` keyed trên ``(ticker,
quarter_id)``. ``build_a5_features`` là entrypoint zero-arg đọc
``data/aggregated/news_by_quarter.csv``, gộp các cột ``emb_*`` lên khung đặc
trưng v0 base, và ghi ``data/features/keyword_features_A5.csv`` (Req 9.2). Tệp
v0 gốc ``data/features/keyword_features.csv`` không bị sửa đổi (Req 2.3).

**Encoder có thể tiêm vào (dependency injection).** PhoBERT kéo theo phụ thuộc
nặng (``transformers`` + ``torch``) có thể không được cài trong môi trường test.
Do đó module này KHÔNG import ``transformers``/``torch`` ở cấp module:

- ``compute_embedding_features(df, encoder)`` và ``build_a5_features(...,
  encoder=None)`` nhận một *encoder* — một callable nhận ``list[str]`` các văn
  bản và trả về ``numpy.ndarray`` hình ``(n_texts, d)``.
- :class:`PhoBERTEncoder` chỉ import ``transformers``/``torch`` **bên trong**
  (lazy, ở ``_load()``), nên ``import experiments.a5_embeddings`` luôn thành
  công dù ``transformers``/``torch`` chưa được cài.
- Khi ``encoder=None``, ``build_a5_features`` mặc định dựng một
  :class:`PhoBERTEncoder` (lazy) — nhưng test có thể truyền encoder giả để
  tránh tải mô hình thật.

Báo cáo so sánh với Baseline_v0 (Req 9.3) do CLI
``experiments/run_experiment.py::run_experiment("A5")`` tự sinh qua
Comparison_Reporter — module này chỉ cần tạo tệp đặc trưng hợp lệ, mergeable.

_Requirements: 9.2, 9.3, 2.1, 2.3_
"""

from __future__ import annotations

import logging
import os
from typing import Callable, Dict, List, Optional, Sequence

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
    "EMBEDDING_DIM",
    "Encoder",
    "PhoBERTEncoder",
    "compute_embedding_features",
    "build_a5_features",
]

# ---------------------------------------------------------------------------
# Đường dẫn artifact của A5 (Req 9.2, 2.1, 2.3)
# ---------------------------------------------------------------------------

NEWS_BY_QUARTER_PATH = "data/aggregated/news_by_quarter.csv"
#: Tệp đặc trưng version hóa của A5 — KHÔNG ghi đè v0 (Req 2.1, 2.3).
OUTPUT_PATH = "data/features/keyword_features_A5.csv"

#: Cột khóa mergeable trên (ticker, quarter_id).
META_COLS = ["ticker", "quarter_id"]

#: Số chiều vector nhúng của PhoBERT-base (hidden size mặc định).
EMBEDDING_DIM = 768

#: Tên mô hình PhoBERT dùng để nhúng văn bản tiếng Việt.
PHOBERT_MODEL_NAME = "vinai/phobert-base"

#: Kiểu của một *encoder*: callable nhận list văn bản → ndarray (n_texts, d).
Encoder = Callable[[Sequence[str]], np.ndarray]


# ---------------------------------------------------------------------------
# PhoBERT encoder — import nặng lazy, KHÔNG ở cấp module (Req 9.2)
# ---------------------------------------------------------------------------


class PhoBERTEncoder:
    """Encoder nhúng văn bản bằng PhoBERT với mean-pooling trạng thái ẩn cuối.

    Phụ thuộc nặng (``transformers`` + ``torch``) chỉ được import **bên trong**
    :meth:`_load` (lazy), nên việc ``import experiments.a5_embeddings`` không bao
    giờ thất bại khi các thư viện này chưa được cài. Mô hình được nạp một lần
    (memoized) ở lần gọi đầu tiên.

    Cách nhúng (Req 9.2):

    - Tokenize từng văn bản (cắt/pad tới ``max_length``).
    - Chạy PhoBERT ở chế độ ``eval`` trong ``torch.no_grad()``.
    - Lấy **mean-pooling** của ``last_hidden_state`` có tính tới attention mask
      (chỉ trung bình trên các token thực, bỏ qua padding) → vector ``d`` chiều.

    Args:
        model_name: Tên/đường dẫn mô hình PhoBERT (mặc định ``vinai/phobert-base``).
        max_length: Độ dài token tối đa mỗi văn bản khi tokenize.
        batch_size: Số văn bản mỗi batch khi mã hóa.
    """

    def __init__(
        self,
        model_name: str = PHOBERT_MODEL_NAME,
        max_length: int = 256,
        batch_size: int = 16,
    ) -> None:
        self.model_name = model_name
        self.max_length = max_length
        self.batch_size = batch_size
        self._tokenizer = None
        self._model = None
        self._torch = None

    def _load(self) -> None:
        """Nạp tokenizer + model PhoBERT lazily (import nặng nằm ở đây)."""
        if self._model is not None:
            return
        # Import nặng CỐ Ý đặt trong hàm để module-level import không cần torch.
        import torch  # noqa: WPS433 (import cục bộ có chủ đích)
        from transformers import AutoModel, AutoTokenizer  # noqa: WPS433

        logger.info("Đang nạp PhoBERT '%s' (lazy)...", self.model_name)
        self._torch = torch
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self._model = AutoModel.from_pretrained(self.model_name)
        self._model.eval()

    def __call__(self, texts: Sequence[str]) -> np.ndarray:
        """Mã hóa danh sách văn bản thành ma trận nhúng ``(n_texts, d)``.

        Args:
            texts: Danh sách văn bản cần nhúng.

        Returns:
            ``numpy.ndarray`` hình ``(len(texts), hidden_size)``.
        """
        self._load()
        torch = self._torch

        cleaned = ["" if t is None else str(t) for t in texts]
        vectors: List[np.ndarray] = []

        with torch.no_grad():
            for start in range(0, len(cleaned), self.batch_size):
                batch = cleaned[start : start + self.batch_size]
                enc = self._tokenizer(
                    batch,
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors="pt",
                )
                out = self._model(**enc)
                last_hidden = out.last_hidden_state  # (b, seq, d)
                mask = enc["attention_mask"].unsqueeze(-1).type_as(last_hidden)
                # Mean-pooling có tính attention mask (bỏ qua padding).
                summed = (last_hidden * mask).sum(dim=1)
                counts = mask.sum(dim=1).clamp(min=1e-9)
                pooled = summed / counts
                vectors.append(pooled.cpu().numpy())

        if not vectors:
            return np.zeros((0, EMBEDDING_DIM), dtype=float)
        return np.vstack(vectors).astype(float)


# ---------------------------------------------------------------------------
# Thuật toán then chốt: cột nhúng emb_* keyed trên (ticker, quarter_id) (Req 9.2)
# ---------------------------------------------------------------------------


def compute_embedding_features(
    df: pd.DataFrame,
    encoder: Encoder,
) -> pd.DataFrame:
    """Tính các cột nhúng ``emb_{i}`` keyed trên ``(ticker, quarter_id)`` (Req 9.2).

    Hàm thuần trung tâm dùng chung cho :func:`build_a5_features` và cho các test.
    Đầu vào phải chứa:

    - ``ticker``, ``quarter_id`` — khóa;
    - ``combined_text`` — corpus gộp của kỳ để nhúng.

    Corpus của mỗi hàng được đưa qua ``encoder`` (một callable nhận
    ``list[str]`` và trả ndarray ``(n_texts, d)``). Số chiều ``d`` được suy ra
    trực tiếp từ đầu ra của encoder, nên các cột kết quả là
    ``emb_0, emb_1, ..., emb_{d-1}``.

    Args:
        df: DataFrame đầu vào (xem các cột bắt buộc ở trên).
        encoder: Callable mã hóa văn bản → ma trận nhúng ``(n_texts, d)``.

    Returns:
        DataFrame gồm ``[ticker, quarter_id]`` + các cột ``emb_0..emb_{d-1}``,
        một hàng cho mỗi ``(ticker, quarter_id)``.
    """
    texts = df["combined_text"].fillna("").astype(str).tolist()

    if texts:
        matrix = np.asarray(encoder(texts), dtype=float)
        if matrix.ndim == 1:
            matrix = matrix.reshape(len(texts), -1)
        dim = matrix.shape[1] if matrix.size else EMBEDDING_DIM
    else:
        # Corpus rỗng: không có hàng nào, giữ EMBEDDING_DIM cột theo quy ước.
        dim = EMBEDDING_DIM
        matrix = np.zeros((0, dim), dtype=float)

    emb_cols = {f"emb_{i}": matrix[:, i] for i in range(dim)}

    result = pd.DataFrame(
        {
            "ticker": df["ticker"].to_numpy(),
            "quarter_id": df["quarter_id"].to_numpy(),
        }
    )
    emb_df = pd.DataFrame(emb_cols, index=df.index).reset_index(drop=True)
    return pd.concat([result, emb_df], axis=1)


# ---------------------------------------------------------------------------
# Xây dựng khung đặc trưng v0 base + A5 (Req 9.2, 2.1)
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

    Tái dùng nguyên các hàm của v0 (giống ``a4_tfidf_crossticker._prepare_v0_frame``):
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


def build_a5_features(
    news_path: str = NEWS_BY_QUARTER_PATH,
    output_path: str = OUTPUT_PATH,
    encoder: Optional[Encoder] = None,
) -> pd.DataFrame:
    """Đọc news-by-quarter, tính A5 và ghi ``keyword_features_A5.csv`` (Req 9.2).

    Gộp các cột nhúng ``emb_{i}`` (PhoBERT mean-pooling) lên khung đặc trưng v0
    base, giữ khung khóa ``(ticker, quarter_id)`` mergeable với
    ``technical_features.csv`` (Req 2.1). KHÔNG sửa tệp v0
    ``data/features/keyword_features.csv`` (Req 2.3).

    Args:
        news_path: Đường dẫn ``news_by_quarter.csv`` đầu vào.
        output_path: Đường dẫn ghi tệp đặc trưng A5.
        encoder: Encoder tùy chọn (callable ``list[str] -> ndarray``). Nếu
            ``None``, mặc định dựng :class:`PhoBERTEncoder` (lazy — chỉ tải mô
            hình khi thực sự mã hóa). Test có thể truyền encoder giả để tránh
            tải PhoBERT thật.

    Returns:
        DataFrame đặc trưng A5 đã ghi (rỗng nếu đầu vào lỗi).
    """
    df = _load_news(news_path)
    if df.empty:
        return pd.DataFrame()

    if encoder is None:
        encoder = PhoBERTEncoder()

    keywords_by_direction = get_curated_keywords()
    # get_all_keywords_flat() giữ tương thích với các builder anh em (không dùng
    # trực tiếp ở đây vì v0 frame tự lấy curated keywords).
    _ = get_all_keywords_flat

    # Khung v0 base (đã có kw_*, kw_norm_*, tfidf_*, sentiment, coverage).
    v0 = _prepare_v0_frame(df, keywords_by_direction)

    # Các cột nhúng emb_* keyed trên (ticker, quarter_id).
    emb = compute_embedding_features(df, encoder)

    # Gộp các cột emb_ lên v0 base theo khóa (ticker, quarter_id).
    features = v0.merge(emb, on=META_COLS, how="left")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    features.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(
        "Đã ghi đặc trưng A5 (%d hàng, %d cột) vào %s.",
        len(features),
        len(features.columns),
        output_path,
    )
    return features


if __name__ == "__main__":  # pragma: no cover - entrypoint
    logging.basicConfig(level=logging.INFO)
    build_a5_features()
