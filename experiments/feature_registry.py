"""Feature Registry — nguồn chân lý duy nhất cho các cột đặc trưng văn bản mới.

Module này khai báo các tiền tố, tên chính xác, và hậu tố phủ định của các cột
đặc trưng văn bản (keyword) do các thí nghiệm Hướng A/B sinh ra, và cung cấp
``is_keyword_column`` để mở rộng ``identify_feature_columns()`` trong
``pipeline/task10_train.py``.

Bất biến cốt lõi (Req 3.6, 3.7): mọi cột không khớp bất kỳ quy tắc keyword nào và
không phải cột siêu dữ liệu đều rơi vào nhóm technical — do đó 16 đặc trưng kỹ
thuật của Config_A luôn ổn định giữa mọi thí nghiệm.

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Đăng ký các nhóm cột đặc trưng văn bản mới
# ---------------------------------------------------------------------------

# Các tiền tố của cột keyword mới (bổ sung cho kw_, kw_norm_, tfidf_ đã có sẵn
# trong ``identify_feature_columns``).
NEW_KW_PREFIXES = (
    "sent_",     # A1: sentiment nhóm — sent_A, sent_B, ...
    "llm_",      # A6/A7: LLM sentiment and scorecard aggregate features
    "ds_",       # B1: ds_pos_prob_mean, ds_net_sentiment
    "sector_",   # B4: sector_pos_score, sector_news_count
    "emb_",      # A5: embedding dims
    "tfidfx_",   # A4: cross-ticker tfidf
)

# Các cột keyword mới nhận diện bằng tên chính xác.
NEW_KW_EXACT = {
    "news_velocity",   # A3
    "kw_novelty",      # A3
    "kw_entropy",      # A3
    "pos_neg_shift",   # A3
    "news_spike",      # B5
}

# Hậu tố phủ định của A2: một cột kw gốc + "_NEG" (ví dụ kw_nợ xấu_NEG).
NEG_SUFFIX = "_NEG"


def is_keyword_column(col: str) -> bool:
    """True nếu ``col`` là một cột đặc trưng văn bản mới đã đăng ký.

    Một cột được coi là keyword khi nó thuộc bất kỳ nhóm nào dưới đây:

    - khớp một trong các tiền tố ở ``NEW_KW_PREFIXES``
      (``sent_``, ``llm_``, ``ds_``, ``sector_``, ``emb_``, ``tfidfx_``);
    - có tên chính xác thuộc ``NEW_KW_EXACT``
      (``news_velocity``, ``kw_novelty``, ``kw_entropy``, ``pos_neg_shift``,
      ``news_spike``);
    - là cột phủ định A2: kết thúc bằng ``NEG_SUFFIX`` (``_NEG``) VÀ bắt đầu
      bằng ``kw_`` (ví dụ ``kw_{keyword}_NEG``).

    Args:
        col: Tên cột cần kiểm tra.

    Returns:
        ``True`` nếu ``col`` là cột đặc trưng văn bản mới, ngược lại ``False``.
    """
    if not isinstance(col, str):
        return False

    if col in NEW_KW_EXACT:
        return True

    if any(col.startswith(prefix) for prefix in NEW_KW_PREFIXES):
        return True

    # Cột phủ định A2: kw_{keyword}_NEG
    if col.endswith(NEG_SUFFIX) and col.startswith("kw_"):
        return True

    return False
