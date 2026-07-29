"""Leakage_Auditor (`backtest/leakage_audit.py`) — kiểm toán rò rỉ thời gian (Req 8).

Module này thực hiện kiểm tra **tĩnh + thống kê** (không huấn luyện lại mô hình)
để chứng minh đặc trưng kỹ thuật của kỳ ``q`` không rò rỉ thông tin của kỳ tương
lai — điểm hội đồng dễ vặn vì balanced accuracy ≈ 0,76 khá cao.

Ba lớp kiểm tra:

- **(a) Phân loại cửa sổ thời gian** (Req 8.1): mỗi đặc trưng kỹ thuật được gán
  nhãn ``"in-period"`` (tính trong kỳ ``q``: ``return_q``, ``volatility_q``,
  ``rsi_end_q``, ``sma20_end``, ...) hoặc ``"past"`` (dùng dữ liệu kỳ trước:
  ``return_prev_q``, ``return_2q_ago``). KHÔNG đặc trưng nào được phép mang cửa
  sổ ``"future"``; nếu tên cột khớp mẫu tương lai (``next_``, ``_next``,
  ``future``, ...) → cờ đỏ.
- **(b) Nhãn không nằm trong feature set** (Req 8.2): xác nhận các cột
  nhãn/return tương lai (``return``, ``next_quarter_id``, ``next_avg_close``,
  ``label_basic``, ``label_threshold``) KHÔNG xuất hiện trong tập đặc trưng kỹ
  thuật.
- **(c) Tương quan đặc trưng–nhãn** (Req 8.3): với mỗi đặc trưng số, tính
  ``|corr|`` Pearson với nhãn ``label_basic``; nếu vượt ``corr_threshold`` →
  đánh dấu cờ đỏ để rà soát thủ công (tương quan bất thường có thể là dấu hiệu
  rò rỉ).

Kết quả được ghi ra ``reports/leakage_audit.md`` (Req 8.5) và trả về dưới dạng
:class:`AuditResult`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from pipeline.logging_config import setup_logger
from pipeline.task10_train import LABELS_PATH, TECH_FEATURES_PATH

logger = setup_logger("BACKTEST_LEAKAGE_AUDIT")

# Đường dẫn báo cáo mặc định (Req 8.5).
DEFAULT_OUTPUT_PATH = "reports/leakage_audit.md"

# Khóa nối kỹ thuật ↔ nhãn; KHÔNG phải đặc trưng.
KEY_COLUMNS: Tuple[str, ...] = ("ticker", "quarter_id")

# Cột nhãn tương lai — dùng làm nhãn để tính tương quan (c).
LABEL_COLUMN = "label_basic"

# Các cột nhãn/return tương lai KHÔNG được phép nằm trong feature set (Req 8.2).
FUTURE_LABEL_COLUMNS: Tuple[str, ...] = (
    "return",
    "next_quarter_id",
    "next_avg_close",
    "label_basic",
    "label_threshold",
)

# Mẫu tên gợi ý đặc trưng dùng dữ liệu TƯƠNG LAI (cấm) — nếu khớp → cờ đỏ.
FUTURE_NAME_PATTERNS: Tuple[str, ...] = (
    r"next[_-]",
    r"[_-]next",
    r"future",
    r"forward",
    r"ahead",
    r"lead",
)

# Mẫu tên gợi ý đặc trưng dùng dữ liệu QUÁ KHỨ (kỳ < q) — hợp lệ.
PAST_NAME_PATTERNS: Tuple[str, ...] = (
    r"prev",
    r"_ago",
    r"ago$",
    r"lag",
    r"_prior",
)


@dataclass
class AuditResult:
    """Kết quả kiểm toán rò rỉ thời gian (Req 8).

    Attributes:
        feature_windows: ánh xạ ``feature -> "in-period" | "past" | "future"``
            phân loại cửa sổ thời gian của mỗi đặc trưng kỹ thuật (a).
        label_not_in_features: ``True`` khi không cột nhãn/return tương lai nào
            xuất hiện trong tập đặc trưng (b).
        high_corr_flags: danh sách ``(feature, |corr|)`` có tương quan tuyệt đối
            với nhãn vượt ``corr_threshold`` (c) — cần rà soát thủ công.
        passed: ``True`` khi không đặc trưng nào bị phân loại ``"future"``,
            ``label_not_in_features`` là ``True``, và ``high_corr_flags`` rỗng.
    """

    feature_windows: Dict[str, str] = field(default_factory=dict)
    label_not_in_features: bool = True
    high_corr_flags: List[Tuple[str, float]] = field(default_factory=list)
    passed: bool = False


def _match_any(name: str, patterns: Tuple[str, ...]) -> bool:
    """Trả ``True`` nếu *name* (lowercase) khớp bất kỳ regex nào trong *patterns*."""
    lowered = name.lower()
    return any(re.search(p, lowered) for p in patterns)


def classify_feature_window(feature: str) -> str:
    """Phân loại cửa sổ thời gian của một tên đặc trưng kỹ thuật (Req 8.1).

    Quy tắc (theo thứ tự ưu tiên):

    1. Tên khớp mẫu tương lai (``next_``, ``future``, ``ahead``, ...) →
       ``"future"`` (CẤM — sẽ khiến audit fail).
    2. Tên khớp mẫu quá khứ (``prev``, ``_ago``, ``lag``, ...) → ``"past"``
       (hợp lệ — dùng dữ liệu kỳ trước ``q``).
    3. Còn lại → ``"in-period"`` (tính trong kỳ ``q``, hợp lệ). Đây là mặc định
       cho các đặc trưng như ``return_q``, ``volatility_q``, ``rsi_end_q``,
       ``sma20_end``, ``macd_hist_mean_q``...

    Args:
        feature: tên cột đặc trưng.

    Returns:
        Một trong ``"in-period"``, ``"past"``, ``"future"``.
    """
    if _match_any(feature, FUTURE_NAME_PATTERNS):
        return "future"
    if _match_any(feature, PAST_NAME_PATTERNS):
        return "past"
    return "in-period"


def _abs_corr_with_label(
    feature_values: pd.Series,
    label_values: pd.Series,
) -> float:
    """Tính ``|corr|`` Pearson giữa một đặc trưng và nhãn, an toàn với NaN/hằng.

    Loại theo cặp các hàng có NaN ở một trong hai chuỗi. Nếu sau khi loại còn
    < 2 điểm, hoặc một trong hai chuỗi là hằng (std = 0) → tương quan không xác
    định, trả ``0.0`` (bỏ qua thay vì gắn cờ nhầm).
    """
    pair = pd.DataFrame({"f": feature_values, "y": label_values}).dropna()
    if len(pair) < 2:
        return 0.0
    f = pair["f"].to_numpy(dtype=float)
    y = pair["y"].to_numpy(dtype=float)
    if np.std(f) == 0.0 or np.std(y) == 0.0:
        return 0.0
    corr = np.corrcoef(f, y)[0, 1]
    if np.isnan(corr):
        return 0.0
    return float(abs(corr))


def _write_report(
    result: AuditResult,
    output_path: str,
    tech_path: str,
    labels_path: str,
    cutoff: str,
    corr_threshold: float,
    n_features: int,
    n_merged_rows: int,
) -> None:
    """Ghi báo cáo Markdown human-readable (Req 8.5)."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    overall = "✅ PASS" if result.passed else "❌ FAIL — CẦN RÀ SOÁT"

    lines: List[str] = []
    lines.append("# Kiểm toán rò rỉ dữ liệu thời gian (Leakage Audit)")
    lines.append("")
    lines.append(f"**Kết luận tổng thể:** {overall}")
    lines.append("")
    lines.append("## Tham số kiểm toán")
    lines.append("")
    lines.append(f"- Tệp đặc trưng kỹ thuật: `{tech_path}`")
    lines.append(f"- Tệp nhãn: `{labels_path}`")
    lines.append(f"- Train_Cutoff: `{cutoff}`")
    lines.append(f"- Ngưỡng tương quan (corr_threshold): `{corr_threshold}`")
    lines.append(f"- Số đặc trưng kỹ thuật kiểm tra: **{n_features}**")
    lines.append(f"- Số hàng dùng tính tương quan (sau merge): **{n_merged_rows}**")
    lines.append("")

    # (a) Phân loại cửa sổ thời gian.
    lines.append("## (a) Phân loại cửa sổ thời gian của đặc trưng (Req 8.1)")
    lines.append("")
    lines.append(
        "Quy tắc: tên khớp mẫu `next_`/`future`/`ahead` → **future** (cấm); "
        "khớp `prev`/`_ago`/`lag` → **past** (dùng kỳ < q, hợp lệ); còn lại → "
        "**in-period** (tính trong kỳ q, hợp lệ)."
    )
    lines.append("")
    lines.append("| Đặc trưng | Cửa sổ thời gian |")
    lines.append("|---|---|")
    for feat, window in result.feature_windows.items():
        marker = " ⚠️" if window == "future" else ""
        lines.append(f"| `{feat}` | {window}{marker} |")
    lines.append("")
    n_future = sum(1 for w in result.feature_windows.values() if w == "future")
    n_past = sum(1 for w in result.feature_windows.values() if w == "past")
    n_in = sum(1 for w in result.feature_windows.values() if w == "in-period")
    lines.append(
        f"Tổng hợp: **{n_in}** in-period, **{n_past}** past, "
        f"**{n_future}** future."
    )
    if n_future == 0:
        lines.append("")
        lines.append(
            "→ Không đặc trưng nào dùng dữ liệu tương lai (> q). Đặc trưng "
            "`return_q`/`volatility_q` là *trong kỳ* (dùng để dự báo kỳ *kế "
            "tiếp*), KHÔNG phải nhãn tương lai."
        )
    else:
        lines.append("")
        lines.append("→ ⚠️ Phát hiện đặc trưng phân loại **future** — cần rà soát.")
    lines.append("")

    # (b) Nhãn không nằm trong feature set.
    lines.append("## (b) Cột nhãn/return tương lai không nằm trong feature set (Req 8.2)")
    lines.append("")
    lines.append(
        "Các cột kiểm tra: "
        + ", ".join(f"`{c}`" for c in FUTURE_LABEL_COLUMNS)
        + "."
    )
    lines.append("")
    if result.label_not_in_features:
        lines.append(
            "→ ✅ Không cột nhãn/return tương lai nào xuất hiện trong tập đặc "
            "trưng kỹ thuật."
        )
    else:
        lines.append(
            "→ ❌ Có cột nhãn/return tương lai xuất hiện trong tập đặc trưng — "
            "RÒ RỈ TRỰC TIẾP."
        )
    lines.append("")

    # (c) Tương quan đặc trưng–nhãn.
    lines.append("## (c) Tương quan đặc trưng–nhãn (Req 8.3)")
    lines.append("")
    lines.append(
        f"Tính `|corr|` Pearson giữa mỗi đặc trưng và nhãn `{LABEL_COLUMN}`; "
        f"vượt `{corr_threshold}` → cờ đỏ rà soát thủ công."
    )
    lines.append("")
    if result.high_corr_flags:
        lines.append("| Đặc trưng | \\|corr\\| |")
        lines.append("|---|---|")
        for feat, corr in result.high_corr_flags:
            lines.append(f"| `{feat}` | {corr:.4f} |")
        lines.append("")
        lines.append(
            "→ ⚠️ Có đặc trưng tương quan bất thường với nhãn — rà soát thủ công."
        )
    else:
        lines.append(
            f"→ ✅ Không đặc trưng nào có `|corr|` với `{LABEL_COLUMN}` vượt "
            f"ngưỡng `{corr_threshold}`."
        )
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Đã ghi báo cáo kiểm toán rò rỉ → %s", output_path)


def audit_leakage(
    tech_path: str = TECH_FEATURES_PATH,
    labels_path: str = LABELS_PATH,
    cutoff: str = "2025Q1",
    corr_threshold: float = 0.95,
    output_path: str = DEFAULT_OUTPUT_PATH,
) -> AuditResult:
    """Kiểm toán rò rỉ dữ liệu thời gian trong đặc trưng kỹ thuật (Req 8).

    (a) Phân loại cửa sổ thời gian mỗi đặc trưng (``return_prev_q``,
    ``return_2q_ago`` là *past*; ``return_q``, ``volatility_q`` là *in-period*,
    hợp lệ) và xác nhận không đặc trưng nào dùng dữ liệu ``> q`` (Req 8.1);
    (b) Xác nhận cột nhãn/return tương lai KHÔNG nằm trong feature set (Req 8.2);
    (c) Tính ``|corr|`` đặc trưng–nhãn; vượt *corr_threshold* → cờ đỏ rà soát thủ
    công (Req 8.3). Ghi ``leakage_audit.md`` (Req 8.5).

    Args:
        tech_path: đường dẫn tệp đặc trưng kỹ thuật.
        labels_path: đường dẫn ``master_with_labels.csv`` (nguồn nhãn).
        cutoff: Train_Cutoff — chỉ dùng để ghi vào báo cáo (kiểm tra này là tĩnh,
            áp dụng cho toàn bộ đặc trưng nên không phụ thuộc split).
        corr_threshold: ngưỡng ``|corr|`` để gắn cờ đỏ (mặc định ``0.95``).
        output_path: đường dẫn tệp Markdown đầu ra (mặc định
            ``reports/leakage_audit.md``).

    Returns:
        :class:`AuditResult`.

    Raises:
        FileNotFoundError: nếu thiếu tệp đặc trưng hoặc tệp nhãn.
        KeyError: nếu tệp nhãn thiếu cột nhãn ``label_basic`` hoặc khóa nối.
    """
    tech_file = Path(tech_path)
    labels_file = Path(labels_path)
    if not tech_file.exists():
        raise FileNotFoundError(f"Không tìm thấy tệp đặc trưng kỹ thuật: {tech_path}")
    if not labels_file.exists():
        raise FileNotFoundError(f"Không tìm thấy tệp nhãn: {labels_path}")

    tech = pd.read_csv(tech_path)
    labels = pd.read_csv(labels_path)

    # Đặc trưng kỹ thuật = mọi cột trừ khóa nối.
    feature_cols = [c for c in tech.columns if c not in KEY_COLUMNS]

    # (a) Phân loại cửa sổ thời gian.
    feature_windows: Dict[str, str] = {
        feat: classify_feature_window(feat) for feat in feature_cols
    }
    no_future_features = not any(w == "future" for w in feature_windows.values())

    # (b) Nhãn/return tương lai không nằm trong feature set.
    feature_set = set(feature_cols)
    leaked_label_cols = [c for c in FUTURE_LABEL_COLUMNS if c in feature_set]
    label_not_in_features = len(leaked_label_cols) == 0
    if leaked_label_cols:
        logger.warning(
            "Rò rỉ trực tiếp: cột nhãn/return tương lai nằm trong feature set: %s",
            leaked_label_cols,
        )

    # (c) Tương quan đặc trưng–nhãn.
    for key in KEY_COLUMNS:
        if key not in labels.columns:
            raise KeyError(f"master_with_labels.csv thiếu cột khóa bắt buộc: {key!r}")
    if LABEL_COLUMN not in labels.columns:
        raise KeyError(
            f"master_with_labels.csv thiếu cột nhãn bắt buộc: {LABEL_COLUMN!r}"
        )

    # Đổi tên nhãn sang tên nội bộ dành riêng trước khi merge để tránh va chạm
    # tên cột: một đặc trưng kỹ thuật có thể trùng tên cột nhãn (`label_basic`),
    # khi đó merge sẽ sinh hậu tố `_x`/`_y` và tra cứu `merged[LABEL_COLUMN]` sẽ
    # lỗi KeyError. Tên nội bộ `__label__` không lọt ra báo cáo (report chỉ dùng
    # LABEL_COLUMN cho phần hiển thị).
    INTERNAL_LABEL = "__label__"
    label_frame = labels[[*KEY_COLUMNS, LABEL_COLUMN]].rename(
        columns={LABEL_COLUMN: INTERNAL_LABEL}
    )
    merged = tech.merge(label_frame, on=list(KEY_COLUMNS), how="inner")
    n_merged_rows = len(merged)

    high_corr_flags: List[Tuple[str, float]] = []
    if n_merged_rows >= 2:
        label_series = merged[INTERNAL_LABEL]
        for feat in feature_cols:
            # Chỉ tính tương quan trên cột số.
            col = pd.to_numeric(merged[feat], errors="coerce")
            abs_corr = _abs_corr_with_label(col, label_series)
            if abs_corr > corr_threshold:
                high_corr_flags.append((feat, abs_corr))
                logger.warning(
                    "Cờ đỏ: |corr(%s, %s)| = %.4f > %.2f",
                    feat,
                    LABEL_COLUMN,
                    abs_corr,
                    corr_threshold,
                )
    else:
        logger.warning(
            "Chỉ %d hàng sau merge — bỏ qua kiểm tra tương quan (c).",
            n_merged_rows,
        )

    passed = (
        no_future_features and label_not_in_features and not high_corr_flags
    )

    result = AuditResult(
        feature_windows=feature_windows,
        label_not_in_features=label_not_in_features,
        high_corr_flags=high_corr_flags,
        passed=passed,
    )

    _write_report(
        result=result,
        output_path=output_path,
        tech_path=tech_path,
        labels_path=labels_path,
        cutoff=cutoff,
        corr_threshold=corr_threshold,
        n_features=len(feature_cols),
        n_merged_rows=n_merged_rows,
    )

    logger.info(
        "Kiểm toán rò rỉ hoàn tất: passed=%s (future=%d, label_ok=%s, flags=%d).",
        passed,
        sum(1 for w in feature_windows.values() if w == "future"),
        label_not_in_features,
        len(high_corr_flags),
    )

    return result
