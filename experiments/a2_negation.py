"""Negation_Matcher — A2: khớp từ khóa có nhận biết phủ định (Req 5).

Thí nghiệm A2 mở rộng bước đếm từ khóa thô của baseline v0
(``pipeline/task9_kw_features.py::compute_raw_counts``) bằng một bước **nhận
biết phủ định**: khi một từ khóa khớp trong văn bản, ta kiểm tra một cửa sổ
±``NEGATION_WINDOW`` từ quanh vị trí khớp; nếu có một dấu hiệu phủ định tiếng
Việt trong cửa sổ đó VÀ từ khóa chưa mang sẵn nghĩa phủ định, lần khớp được
đếm vào đặc trưng đảo polarity ``kw_{keyword}_NEG`` thay vì ``kw_{keyword}``
gốc (Req 5.2, 5.3, 5.5).

Nguyên tắc cốt lõi (tái dùng longest-first masking của v0 — Req 5.4):

- Giữ nguyên **longest-first masking**: sắp từ khóa theo độ dài chuẩn hóa giảm
  dần, mỗi span đã khớp bị "mask" bằng ký tự sentinel để từ khóa con (substring)
  đối nghịch không đếm lại. Nhờ đó tổng ``kw_{k}`` + ``kw_{k}_NEG`` luôn bằng
  đúng số span mà ``compute_raw_counts`` gốc tạo ra cho ``k`` (bảo toàn số đếm).
- Việc kiểm tra phủ định chạy **sau khi** span khớp đã được xác định bởi
  longest-first masking (Req 5.4).
- Cửa sổ phủ định được tính trên chuỗi token của văn bản gốc (đã chuẩn hóa),
  còn vị trí từng lần khớp được lấy bằng ``re.finditer`` trên bản masked hiện
  thời (Req 5.2).

``build_a2_features`` áp dụng matcher trên ``news_by_quarter.csv`` và ghi ra
``data/features/keyword_features_A2.csv`` với đầy đủ schema v0 (kw_*, kw_norm_*,
tfidf_*, sentiment scores, coverage) CỘNG các cột ``kw_{keyword}_NEG`` mới
(Req 5.6). Tệp v0 gốc ``data/features/keyword_features.csv`` không bị sửa đổi
(Req 2.3).

_Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 2.1, 2.3_
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from pipeline.task8_keywords import (
    get_all_keywords_flat,
    get_curated_keywords,
)
from pipeline.task9_kw_features import (
    _MASK_CHAR,
    _normalize_for_matching,
    add_coverage_features,
    compute_raw_counts,
    compute_sentiment_scores,
    compute_tfidf_features,
)

logger = logging.getLogger(__name__)

__all__ = [
    "NEGATION_CUES",
    "NEGATION_WINDOW",
    "compute_raw_counts_negation_aware",
    "compute_flip_statistics",
    "extract_a2_features",
    "build_a2_features",
]

# ---------------------------------------------------------------------------
# Hằng số cấu hình phủ định (Req 5.1, 5.2)
# ---------------------------------------------------------------------------

#: Danh sách dấu hiệu phủ định tiếng Việt được khai báo tường minh (Req 5.1).
#: Lưu ý theo caveat của design: ``giảm``/``hạ`` KHÔNG phải cue phủ định — chúng
#: là từ chỉ hướng và đã được xử lý qua các cụm keyword trong ``KEYWORD_GROUPS``.
NEGATION_CUES: List[str] = [
    "không",
    "chưa",
    "chẳng",
    "chả",
    "không còn",
    "không thể",
    "khó",
    "thiếu",
    "mất",
]

#: Kích thước cửa sổ phủ định: ±3 từ quanh vị trí khớp (Req 5.2).
NEGATION_WINDOW: int = 3

# ---------------------------------------------------------------------------
# Đường dẫn artifact của A2 (Req 5.6, 2.1, 2.3)
# ---------------------------------------------------------------------------

NEWS_BY_QUARTER_PATH = "data/aggregated/news_by_quarter.csv"
#: Tệp đặc trưng version hóa của A2 — KHÔNG ghi đè v0 (Req 2.1, 2.3).
OUTPUT_PATH = "data/features/keyword_features_A2.csv"
#: Sidecar thống kê % hit bị flip, để Comparison_Reporter đưa vào báo cáo (Req 5.7).
FLIP_STATS_PATH = "reports/experiment_A2_flip_stats.json"

#: Các từ khóa hay bị phủ định nhất — dùng để nêu bật trong thống kê báo cáo (Req 5.7).
FREQUENTLY_NEGATED_KEYWORDS: List[str] = [
    "nợ xấu",
    "tăng trưởng",
    "chia cổ tức",
    "lãi ròng",
    "phục hồi",
    "hoàn thành kế hoạch",
]


# ---------------------------------------------------------------------------
# Nghĩa phủ định sẵn có (Req 5.5) — chống double-flip
# ---------------------------------------------------------------------------

# Tập từ khóa (đã chuẩn hóa) thuộc hướng ``negative`` của KEYWORD_GROUPS.
_NEGATIVE_KEYWORDS_NORM = {
    _normalize_for_matching(kw) for kw in get_curated_keywords().get("negative", [])
}

# Danh sách cue đã chuẩn hóa (loại bỏ chuỗi rỗng).
_NEGATION_CUES_NORM = [
    c for c in (_normalize_for_matching(cue) for cue in NEGATION_CUES) if c
]


def _already_negative(kw: str) -> bool:
    """True nếu ``kw`` đã mang sẵn nghĩa phủ định — không đảo polarity lần nữa.

    Một từ khóa được coi là đã phủ định nếu (Req 5.5):

    - nó thuộc hướng ``negative`` của ``KEYWORD_GROUPS`` (ví dụ ``nợ xấu``,
      ``thua lỗ``); HOẶC
    - dạng chuẩn hóa của nó đã chứa sẵn một dấu hiệu phủ định
      (ví dụ ``không chia cổ tức``, ``lợi nhuận không tăng``).

    Các từ khóa này được đếm theo polarity gốc (``kw_{keyword}``) mà không bị
    đảo thêm một lần nữa.

    Args:
        kw: Từ khóa (dạng gốc, chưa chuẩn hóa).

    Returns:
        ``True`` nếu từ khóa đã mang nghĩa phủ định; ngược lại ``False``.
    """
    kw_norm = _normalize_for_matching(kw)
    if not kw_norm:
        return False
    if kw_norm in _NEGATIVE_KEYWORDS_NORM:
        return True
    # Đã chứa sẵn cue phủ định (so khớp theo ranh giới token).
    padded = f" {kw_norm} "
    for cue in _NEGATION_CUES_NORM:
        if f" {cue} " in padded:
            return True
    return False


# ---------------------------------------------------------------------------
# Ánh xạ span ký tự → chỉ số từ (cho cửa sổ ±window)
# ---------------------------------------------------------------------------


def _word_char_spans(text_norm: str) -> List[Tuple[int, int]]:
    """Trả về danh sách ``(start_char, end_char)`` cho mỗi từ trong văn bản.

    Văn bản đầu vào đã được ``_normalize_for_matching`` chuẩn hóa (một dấu cách
    giữa các từ), nên vị trí ký tự của từng token là xác định.

    Args:
        text_norm: Văn bản đã chuẩn hóa (space-normalized).

    Returns:
        Danh sách cặp ``(start, end)`` (nửa mở) của mỗi token theo thứ tự.
    """
    spans: List[Tuple[int, int]] = []
    pos = 0
    for word in text_norm.split(" "):
        start = pos
        end = pos + len(word)
        spans.append((start, end))
        pos = end + 1  # bỏ qua đúng một dấu cách phân tách
    return spans


def _words_overlapping(
    word_spans: List[Tuple[int, int]], start_char: int, end_char: int
) -> Tuple[Optional[int], Optional[int]]:
    """Chỉ số từ đầu/cuối mà span ký tự ``[start_char, end_char)`` chạm tới.

    Args:
        word_spans: Danh sách span ký tự của mỗi từ (từ :func:`_word_char_spans`).
        start_char: Vị trí ký tự bắt đầu của span khớp (bao gồm).
        end_char: Vị trí ký tự kết thúc của span khớp (không bao gồm).

    Returns:
        Cặp ``(word_lo, word_hi)`` — chỉ số từ đầu tiên và cuối cùng giao với
        span; ``(None, None)`` nếu không có từ nào giao (không xảy ra trong
        thực tế nhưng được guard để an toàn).
    """
    lo: Optional[int] = None
    hi: Optional[int] = None
    for i, (ws, we) in enumerate(word_spans):
        if ws < end_char and we > start_char:  # có giao nhau
            if lo is None:
                lo = i
            hi = i
    return lo, hi


# ---------------------------------------------------------------------------
# Thuật toán then chốt: khớp từ khóa có nhận biết phủ định (Req 5.2–5.5)
# ---------------------------------------------------------------------------


def compute_raw_counts_negation_aware(
    combined_text: str,
    keywords: List[str],
    negation_cues: List[str] = NEGATION_CUES,
    window: int = NEGATION_WINDOW,
) -> Dict[str, int]:
    """Đếm số lần khớp từ khóa, tách theo có/không có phủ định trong cửa sổ.

    Giống :func:`pipeline.task9_kw_features.compute_raw_counts` (longest-first
    masking) nhưng khi một từ khóa khớp, kiểm tra cửa sổ ±``window`` từ quanh
    span khớp; nếu có dấu hiệu phủ định trong cửa sổ VÀ từ khóa chưa mang sẵn
    nghĩa phủ định (:func:`_already_negative` là ``False``) → đếm vào
    ``kw_{keyword}_NEG``; ngược lại đếm vào ``kw_{keyword}`` (Req 5.2, 5.3, 5.5).

    Thuật toán (theo design "A2 — Negation-aware masking"):

    1. Chuẩn hóa văn bản; tách token để đánh chỉ số từ cho cửa sổ.
    2. Sắp từ khóa theo độ dài chuẩn hóa giảm dần (longest-first).
    3. Với mỗi từ khóa, dùng ``re.finditer`` trên bản masked hiện thời để lấy
       span ký tự của TỪNG lần khớp (không chồng lấn, đồng nhất với ``str.count``
       của bản gốc).
    4. Ánh xạ span ký tự → chỉ số từ bao quanh; lấy cửa sổ token
       ``[word_lo - window, word_hi + window]``; nếu có cue phủ định trong cửa
       sổ và từ khóa chưa phủ định → ``_NEG``, ngược lại → gốc.
    5. Mask span bằng sentinel để từ khóa con không đếm lại (bảo toàn số đếm,
       Req 5.4).

    Quy ước khởi tạo: từ điển trả về khởi tạo **cả hai** khóa ``kw_{keyword}``
    và ``kw_{keyword}_NEG`` cho **mọi** từ khóa (kể cả khi giá trị bằng 0), để
    schema cột nhất quán giữa mọi hàng/lần gọi.

    Args:
        combined_text: Văn bản đã ghép của một ``(ticker, quarter)``.
        keywords: Danh sách phẳng các từ khóa curated.
        negation_cues: Danh sách dấu hiệu phủ định (mặc định :data:`NEGATION_CUES`).
        window: Bán kính cửa sổ theo số từ (mặc định :data:`NEGATION_WINDOW`).

    Returns:
        Dict ánh xạ ``kw_{keyword}`` → số đếm gốc và ``kw_{keyword}_NEG`` → số
        đếm bị đảo polarity.
    """
    # Khởi tạo cả hai khóa cho mọi từ khóa (schema nhất quán).
    counts: Dict[str, int] = {}
    for kw in keywords:
        counts[f"kw_{kw}"] = 0
        counts[f"kw_{kw}_NEG"] = 0

    text_norm = _normalize_for_matching(combined_text)
    if not text_norm:
        return counts

    tokens = text_norm.split(" ")
    word_spans = _word_char_spans(text_norm)

    norm_map = {kw: _normalize_for_matching(kw) for kw in keywords}
    norm_cues = [
        c for c in (_normalize_for_matching(cue) for cue in negation_cues) if c
    ]

    # Longest-first: từ khóa dài hơn "chiếm" (và mask) span trước.
    ordered = sorted(
        (kw for kw in keywords if norm_map[kw]),
        key=lambda k: len(norm_map[k]),
        reverse=True,
    )

    masked = text_norm
    for kw in ordered:
        pattern = norm_map[kw]
        matches = list(re.finditer(re.escape(pattern), masked))
        if not matches:
            continue

        already_neg = _already_negative(kw)
        spans_to_mask: List[Tuple[int, int]] = []

        for m in matches:
            start_char, end_char = m.start(), m.end()
            lo, hi = _words_overlapping(word_spans, start_char, end_char)

            if lo is None or hi is None:
                # Guard phòng thủ: không ánh xạ được → đếm vào gốc.
                counts[f"kw_{kw}"] += 1
                spans_to_mask.append((start_char, end_char))
                continue

            w_start = max(0, lo - window)
            w_end = min(len(tokens), hi + window + 1)
            window_tokens = tokens[w_start:w_end]
            # Ghép cửa sổ + đệm khoảng trắng để so khớp cue theo ranh giới token
            # (đúng cho cả cue một từ lẫn nhiều từ như "không còn").
            window_text = " " + " ".join(window_tokens) + " "
            negated = any(f" {cue} " in window_text for cue in norm_cues)

            if negated and not already_neg:
                counts[f"kw_{kw}_NEG"] += 1
            else:
                counts[f"kw_{kw}"] += 1
            spans_to_mask.append((start_char, end_char))

        # Mask toàn bộ span đã khớp (giữ chống double-count như bản gốc).
        masked_chars = list(masked)
        for s, e in spans_to_mask:
            for i in range(s, e):
                masked_chars[i] = _MASK_CHAR
        masked = "".join(masked_chars)

    return counts


# ---------------------------------------------------------------------------
# Xây dựng khung đặc trưng A2 (Req 5.6, 2.1)
# ---------------------------------------------------------------------------


def _compute_negation_aware_counts(
    df: pd.DataFrame,
    keywords: List[str],
) -> pd.DataFrame:
    """Thêm cột ``kw_{k}``, ``kw_{k}_NEG`` và ``kw_norm_{k}`` cho mỗi hàng.

    Bước đếm thô là **negation-aware** (thay cho ``compute_keyword_counts`` của
    v0), nhưng ``kw_norm_{k}`` giữ nguyên ngữ nghĩa v0 (chuẩn hóa theo
    ``news_count``) trên số đếm gốc ``kw_{k}`` để pos/neg score tương thích.

    Args:
        df: DataFrame có ``[ticker, quarter_id, news_count, combined_text]``.
        keywords: Danh sách phẳng các từ khóa curated.

    Returns:
        DataFrame gốc kèm các cột ``kw_*``, ``kw_*_NEG`` và ``kw_norm_*``.
    """
    result = df.copy()

    records: List[Dict[str, int]] = []
    for _, row in result.iterrows():
        records.append(
            compute_raw_counts_negation_aware(row.get("combined_text", ""), keywords)
        )

    base_cols = [f"kw_{kw}" for kw in keywords]
    neg_cols = [f"kw_{kw}_NEG" for kw in keywords]
    all_count_cols = base_cols + neg_cols

    if records:
        counts_df = pd.DataFrame(records, index=result.index).reindex(
            columns=all_count_cols, fill_value=0
        )
    else:
        counts_df = pd.DataFrame(0, columns=all_count_cols, index=result.index)

    # Cột chuẩn hóa (raw gốc / news_count) — giữ ngữ nghĩa v0.
    news_count_safe = result["news_count"].replace(0, np.nan)
    norm_df = pd.DataFrame(
        {
            f"kw_norm_{kw}": counts_df[f"kw_{kw}"] / news_count_safe
            for kw in keywords
        },
        index=result.index,
    )

    # Gộp một lần để tránh phân mảnh DataFrame (PerformanceWarning).
    return pd.concat([result, counts_df, norm_df], axis=1)


def extract_a2_features(
    df: pd.DataFrame,
    keywords_by_direction: Optional[Dict[str, List[str]]] = None,
) -> pd.DataFrame:
    """Tính toàn bộ đặc trưng A2 cho dữ liệu news-by-quarter.

    Phản chiếu schema của v0 (:func:`pipeline.task9_kw_features.extract_keyword_features`):
    ``kw_*``, ``kw_norm_*``, ``pos_score``/``neg_score``/``sentiment_ratio``,
    ``tfidf_*``, ``news_count_log``/``has_min_news`` — CỘNG các cột
    ``kw_{keyword}_NEG`` mới của A2. Chỉ bước đếm thô đổi sang negation-aware.

    Args:
        df: DataFrame ``[ticker, quarter_id, news_count, combined_text]``.
        keywords_by_direction: Dict ``positive/negative/neutral``; mặc định lấy
            từ :func:`get_curated_keywords`.

    Returns:
        DataFrame đặc trưng, đã bỏ cột ``combined_text``.
    """
    if keywords_by_direction is None:
        keywords_by_direction = get_curated_keywords()

    all_keywords = (
        keywords_by_direction.get("positive", [])
        + keywords_by_direction.get("negative", [])
        + keywords_by_direction.get("neutral", [])
    )

    # Bước 1: đếm thô có nhận biết phủ định + chuẩn hóa (thay bước v0).
    result = _compute_negation_aware_counts(df, all_keywords)

    # Bước 2: điểm sentiment (tái dùng nguyên hàm v0).
    result = compute_sentiment_scores(result, keywords_by_direction)

    # Bước 3: TF-IDF (tái dùng nguyên hàm v0; dựa trên kw_{k} gốc).
    result = compute_tfidf_features(result, all_keywords)

    # Bước 4: đặc trưng coverage (tái dùng nguyên hàm v0).
    result = add_coverage_features(result)

    if "combined_text" in result.columns:
        result = result.drop(columns=["combined_text"])

    return result


def compute_flip_statistics(
    features_df: pd.DataFrame,
    keywords: List[str],
    highlight: Optional[List[str]] = None,
) -> Dict[str, object]:
    """Tính % số lần khớp bị đảo polarity (flip) cho báo cáo (Req 5.7).

    Với mỗi từ khóa ``k``: ``flip_pct = Σ kw_{k}_NEG / (Σ kw_{k} + Σ kw_{k}_NEG)``
    trên toàn bộ các hàng. Trả về thống kê tổng thể cùng bảng chi tiết cho các
    từ khóa hay bị phủ định nhất (``highlight``).

    Args:
        features_df: Khung đặc trưng A2 (có ``kw_{k}`` và ``kw_{k}_NEG``).
        keywords: Danh sách phẳng các từ khóa curated.
        highlight: Các từ khóa cần nêu bật; mặc định
            :data:`FREQUENTLY_NEGATED_KEYWORDS`.

    Returns:
        Dict gồm: ``overall_flip_pct`` (float), ``total_base``/``total_neg``
        (int), và ``by_keyword`` (dict keyword → {base, neg, flip_pct}) cho các
        từ khóa nêu bật.
    """
    if highlight is None:
        highlight = FREQUENTLY_NEGATED_KEYWORDS

    total_base = 0
    total_neg = 0
    for kw in keywords:
        base_col = f"kw_{kw}"
        neg_col = f"kw_{kw}_NEG"
        if base_col in features_df.columns:
            total_base += int(features_df[base_col].sum())
        if neg_col in features_df.columns:
            total_neg += int(features_df[neg_col].sum())

    denom_all = total_base + total_neg
    overall = (total_neg / denom_all) if denom_all > 0 else 0.0

    by_keyword: Dict[str, Dict[str, float]] = {}
    for kw in highlight:
        base_col = f"kw_{kw}"
        neg_col = f"kw_{kw}_NEG"
        base = int(features_df[base_col].sum()) if base_col in features_df.columns else 0
        neg = int(features_df[neg_col].sum()) if neg_col in features_df.columns else 0
        denom = base + neg
        by_keyword[kw] = {
            "base": base,
            "neg": neg,
            "flip_pct": (neg / denom) if denom > 0 else 0.0,
        }

    return {
        "overall_flip_pct": overall,
        "total_base": total_base,
        "total_neg": total_neg,
        "by_keyword": by_keyword,
    }


def build_a2_features(
    news_path: str = NEWS_BY_QUARTER_PATH,
    output_path: str = OUTPUT_PATH,
    flip_stats_path: Optional[str] = FLIP_STATS_PATH,
) -> pd.DataFrame:
    """Đọc news-by-quarter, áp dụng matcher A2 và ghi ``keyword_features_A2.csv``.

    Giữ khung khóa ``(ticker, quarter_id)`` mergeable với
    ``technical_features.csv`` / ``master_with_labels.csv`` (Req 2.1). Không sửa
    tệp v0 ``data/features/keyword_features.csv`` (Req 2.3). Ghi kèm sidecar
    thống kê % hit bị flip cho các từ khóa hay bị phủ định (Req 5.7).

    Args:
        news_path: Đường dẫn ``news_by_quarter.csv`` đầu vào.
        output_path: Đường dẫn ghi tệp đặc trưng A2.
        flip_stats_path: Đường dẫn ghi sidecar thống kê flip (JSON); ``None`` để
            bỏ qua việc ghi sidecar.

    Returns:
        DataFrame đặc trưng A2 đã ghi (kèm thuộc tính thống kê được log).
    """
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

    keywords_by_direction = get_curated_keywords()
    all_keywords = get_all_keywords_flat()

    features = extract_a2_features(df, keywords_by_direction)

    # Ghi tệp đặc trưng version hóa (Req 5.6, 2.1) — KHÔNG đụng v0 (Req 2.3).
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    features.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(
        "Đã ghi đặc trưng A2 (%d hàng, %d cột) vào %s.",
        len(features),
        len(features.columns),
        output_path,
    )

    # Thống kê % hit bị flip (Req 5.7).
    stats = compute_flip_statistics(features, all_keywords)
    logger.info(
        "A2 flip tổng thể: %.2f%% (%d/%d hit bị đảo polarity).",
        stats["overall_flip_pct"] * 100.0,
        stats["total_neg"],
        stats["total_base"] + stats["total_neg"],
    )
    for kw, s in stats["by_keyword"].items():
        logger.info(
            "  %-24s flip=%.2f%% (neg=%d, base=%d).",
            kw,
            s["flip_pct"] * 100.0,
            s["neg"],
            s["base"],
        )

    if flip_stats_path:
        os.makedirs(os.path.dirname(flip_stats_path), exist_ok=True)
        with open(flip_stats_path, "w", encoding="utf-8") as fh:
            json.dump(stats, fh, ensure_ascii=False, indent=2)
        logger.info("Đã ghi sidecar thống kê flip vào %s.", flip_stats_path)

    return features


if __name__ == "__main__":  # pragma: no cover - entrypoint
    logging.basicConfig(level=logging.INFO)
    build_a2_features()
