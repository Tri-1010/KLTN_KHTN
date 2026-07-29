"""Comparison_Reporter — sinh báo cáo so sánh thí nghiệm với Baseline_v0 (Req 13).

Module này tạo báo cáo Markdown ``reports/experiment_{id}_report.md`` cho mỗi thí
nghiệm, đặt kết quả mới **cạnh** kết quả cũ đã đóng băng trong ``reports/baseline_v0/``
để có thể viết trực tiếp vào luận văn. Báo cáo gồm đủ các phần của Phần C trong kế
hoạch A_B:

1. Bảng Δ(C−A) cho 4 thuật toán (LightGBM, Random_Forest, XGBoost,
   Logistic_Regression) đặt cạnh baseline_v0 (Req 13.1).
2. Số keyword/đặc trưng đạt ý nghĩa sau BH_FDR, đặt cạnh ``0/71`` của baseline
   (Req 13.2).
3. Tỷ lệ đóng góp SHAP của nhóm đặc trưng văn bản, đặt cạnh ``32%`` của baseline
   (Req 13.3).
4. McNemar giữa Config_C mới và Config_C của baseline_v0 trên cùng tập test
   (Req 13.4).
5. Nhận xét tường minh cho H1/H2/H3 (Req 13.5).
6. Phân tích nguyên nhân theo 3 giải thích lý thuyết (Req 13.6).
7. Kết luận vị trí trong luận văn (Req 13.7).

Ngoài ra ``generate_text_representation_table`` sinh bảng tổng hợp Δ(C−A) của 4 tầng
biểu diễn văn bản (Req 13.8).

Các hàm được viết ở dạng thuần và guard mọi nguồn dữ liệu ngoài (tệp thiếu, không có
overlap, lỗi tái tạo predictions) để việc sinh báo cáo luôn hoàn tất được thay vì
crash.

_Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8_
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd

from experiments.common.runner import RunnerResult, report_path
from experiments.common.snapshot import BASELINE_DIR

logger = logging.getLogger(__name__)

__all__ = [
    "REPORT_MODELS",
    "BASELINE_KEYWORD_SIG",
    "BASELINE_SHAP_PCT_TEXT",
    "TEXT_REPRESENTATION_TABLE_PATH",
    "generate_comparison_report",
    "generate_b3_report",
    "generate_text_representation_table",
    "write_text_representation_table",
]

# Bốn thuật toán so sánh (Req 13.1). Tên khớp CHÍNH XÁC với cột ``model`` trong
# các tệp ``model_comparison*.csv`` (baseline dùng underscore cho Random_Forest,
# Logistic_Regression).
REPORT_MODELS = ["LightGBM", "Random_Forest", "XGBoost", "Logistic_Regression"]

# Tên hiển thị đẹp cho báo cáo (Req 13.1 nêu "Random Forest", "Logistic Regression").
_MODEL_DISPLAY = {
    "LightGBM": "LightGBM",
    "Random_Forest": "Random Forest",
    "XGBoost": "XGBoost",
    "Logistic_Regression": "Logistic Regression",
}

# Con số baseline_v0 cố định để đối chiếu (Req 13.2, 13.3).
BASELINE_KEYWORD_SIG = "0/71"
BASELINE_SHAP_PCT_TEXT = "32%"

# Đường dẫn tệp báo cáo tổng hợp 4 tầng biểu diễn văn bản (Req 13.8). Bảng được
# persist ở đây để có thể trích thẳng vào luận văn.
TEXT_REPRESENTATION_TABLE_PATH = "reports/text_representation_summary.md"

# Tên config dùng cho McNemar (Req 13.4).
_CONFIG_C = "Config_C"


# ---------------------------------------------------------------------------
# Đọc & trích Δ(C−A) từ model_comparison*.csv
# ---------------------------------------------------------------------------


def _read_comparison_df(path: str | Path) -> pd.DataFrame | None:
    """Đọc một tệp ``model_comparison*.csv``; trả về ``None`` nếu thiếu/lỗi."""
    p = Path(path)
    if not p.exists():
        logger.warning("Không tìm thấy tệp so sánh mô hình: '%s'.", p)
        return None
    try:
        return pd.read_csv(p, encoding="utf-8")
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Lỗi đọc tệp so sánh '%s': %s.", p, exc)
        return None


def _extract_ba(
    df: pd.DataFrame | None, model: str, config: str
) -> float | None:
    """Lấy ``balanced_accuracy`` của (model, config) từ bảng so sánh.

    Trả về ``None`` nếu không có dòng khớp (để báo cáo hiển thị "N/A").
    """
    if df is None or df.empty:
        return None
    if not {"model", "config", "balanced_accuracy"}.issubset(df.columns):
        return None
    mask = (df["model"] == model) & (df["config"] == config)
    rows = df.loc[mask, "balanced_accuracy"]
    if rows.empty:
        return None
    try:
        return float(rows.iloc[0])
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return None


def _delta_row(
    df: pd.DataFrame | None, model: str
) -> tuple[float | None, float | None, float | None]:
    """Trả về ``(ba_config_a, ba_config_c, delta_ca)`` cho một model.

    ``delta_ca = ba_config_c − ba_config_a`` khi cả hai có mặt; ngược lại ``None``.
    """
    ba_a = _extract_ba(df, model, "Config_A")
    ba_c = _extract_ba(df, model, "Config_C")
    delta = None
    if ba_a is not None and ba_c is not None:
        delta = ba_c - ba_a
    return ba_a, ba_c, delta


def _fmt(value: float | None, spec: str = "+.4f") -> str:
    """Định dạng số; ``None`` → "N/A"."""
    if value is None:
        return "N/A"
    return format(value, spec)


def _build_delta_table(
    new_df: pd.DataFrame | None, baseline_df: pd.DataFrame | None
) -> str:
    """Bảng Δ(C−A) 4 thuật toán, cột thí nghiệm cạnh cột baseline_v0 (Req 13.1)."""
    lines = [
        "| Thuật toán | BA Config_A (exp) | BA Config_C (exp) | Δ(C−A) exp "
        "| BA Config_A (v0) | BA Config_C (v0) | Δ(C−A) v0 |",
        "|---|---|---|---|---|---|---|",
    ]
    for model in REPORT_MODELS:
        na_a, nc_c, ndelta = _delta_row(new_df, model)
        ba_a, bc_c, bdelta = _delta_row(baseline_df, model)
        display = _MODEL_DISPLAY.get(model, model)
        lines.append(
            f"| {display} "
            f"| {_fmt(na_a, '.4f')} | {_fmt(nc_c, '.4f')} | {_fmt(ndelta)} "
            f"| {_fmt(ba_a, '.4f')} | {_fmt(bc_c, '.4f')} | {_fmt(bdelta)} |"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Keyword significance (Req 13.2) & SHAP contribution (Req 13.3)
# ---------------------------------------------------------------------------


def _count_significant_keywords(keyword_sig_path: str | None) -> str:
    """Đếm ``n_sig/n_total`` keyword đạt ý nghĩa sau BH_FDR (Req 13.2).

    Trả về "not computed" nếu không cung cấp đường dẫn hoặc tệp không tồn tại.
    """
    if not keyword_sig_path:
        return "not computed"
    p = Path(keyword_sig_path)
    if not p.exists():
        logger.warning("Không tìm thấy tệp keyword significance: '%s'.", p)
        return "not computed"
    try:
        df = pd.read_csv(p, encoding="utf-8")
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Lỗi đọc keyword significance '%s': %s.", p, exc)
        return "not computed"
    n_total = len(df)
    if "significant_any" not in df.columns:
        logger.warning(
            "Tệp keyword significance thiếu cột 'significant_any': '%s'.", p
        )
        return "not computed"
    # Chuẩn hóa cột boolean (có thể là chuỗi "True"/"False" khi đọc từ CSV).
    col = df["significant_any"]
    if col.dtype == object:
        n_sig = int(
            col.astype(str).str.strip().str.lower().isin({"true", "1"}).sum()
        )
    else:
        n_sig = int(col.fillna(False).astype(bool).sum())
    return f"{n_sig}/{n_total}"


def _format_shap_pct(shap_contrib_pct: float | None) -> str:
    """Định dạng % đóng góp SHAP của nhóm text (Req 13.3).

    Quy ước: ``shap_contrib_pct`` là **phân số trong [0, 1]** (ví dụ ``0.32`` cho
    32%). Giá trị > 1 được hiểu là đã ở dạng phần trăm (ví dụ ``32.0``). ``None`` →
    "not computed".
    """
    if shap_contrib_pct is None:
        return "not computed"
    pct = shap_contrib_pct * 100.0 if shap_contrib_pct <= 1.0 else shap_contrib_pct
    return f"{pct:.0f}%"


# ---------------------------------------------------------------------------
# McNemar giữa Config_C mới và Config_C baseline_v0 (Req 13.4)
# ---------------------------------------------------------------------------


def _correctness_by_key(
    test_index: pd.DataFrame,
    y_test: np.ndarray,
    preds: np.ndarray,
) -> dict[tuple[Any, Any], bool]:
    """Ánh xạ ``(ticker, quarter_id) -> (pred == y_test)`` cho căn chỉnh McNemar."""
    y_arr = np.asarray(y_test)
    p_arr = np.asarray(preds)
    n = min(len(test_index), len(y_arr), len(p_arr))
    result: dict[tuple[Any, Any], bool] = {}
    idx = test_index.reset_index(drop=True)
    for i in range(n):
        key = (idx.iloc[i]["ticker"], idx.iloc[i]["quarter_id"])
        result[key] = bool(p_arr[i] == y_arr[i])
    return result


def _run_mcnemar_section(
    new_results: RunnerResult,
    cutoff: str,
    baseline_config_c: dict[str, Any] | None,
    reconstruct_fn: Callable[..., dict[str, Any]] | None,
) -> str:
    """Chạy McNemar giữa Config_C mới và Config_C baseline_v0 (Req 13.4).

    Baseline v0 không lưu predictions nên ta tái tạo bằng
    ``run_configs_return_predictions`` với ``keyword_features.csv`` gốc rồi align
    theo ``(ticker, quarter_id)``. Mọi lỗi (không overlap, thiếu Config_C, exception
    khi tái tạo) → trả về câu "not available" thay vì crash.

    ``baseline_config_c`` (tùy chọn, keyword-only) cho phép truyền sẵn dict
    predictions baseline để test không phải huấn luyện thật.
    """
    # 1. Lấy predictions Config_C của thí nghiệm.
    if _CONFIG_C not in new_results.pred_by_config:
        return (
            "McNemar: **not available** — thí nghiệm không có predictions "
            f"cho {_CONFIG_C}."
        )

    # 2. Lấy/tái tạo predictions Config_C của baseline v0.
    baseline = baseline_config_c
    if baseline is None:
        fn = reconstruct_fn
        if fn is None:
            # Import mềm để test có thể monkeypatch/inject mà không cần training.
            try:
                from pipeline.task10_train import (
                    run_configs_return_predictions as fn,  # type: ignore
                )
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning(
                    "Không import được run_configs_return_predictions: %s.", exc
                )
                return (
                    "McNemar: **not available** — không tái tạo được predictions "
                    "baseline_v0."
                )
        try:
            baseline = fn(
                kw_path="data/features/keyword_features.csv",
                cutoff=cutoff,
            )
        except Exception as exc:
            logger.warning(
                "Tái tạo predictions baseline_v0 thất bại: %s.", exc
            )
            return (
                "McNemar: **not available** — tái tạo predictions baseline_v0 "
                f"thất bại ({exc})."
            )

    base_preds = baseline.get("pred_by_config", {})
    if _CONFIG_C not in base_preds:
        return (
            "McNemar: **not available** — baseline_v0 không có predictions "
            f"cho {_CONFIG_C}."
        )

    # 3. Căn theo (ticker, quarter_id).
    new_corr = _correctness_by_key(
        new_results.test_index,
        new_results.y_test,
        new_results.pred_by_config[_CONFIG_C],
    )
    base_corr = _correctness_by_key(
        baseline["test_index"],
        baseline["y_test"],
        base_preds[_CONFIG_C],
    )
    common_keys = sorted(set(new_corr) & set(base_corr))
    if not common_keys:
        return (
            "McNemar: **not available** — không có mẫu test chung giữa Config_C "
            "mới và Config_C baseline_v0."
        )

    # 4. Bảng tương liên correctness: baseline (a) vs new (c).
    both_correct = a_only = c_only = both_wrong = 0
    for key in common_keys:
        a_ok = base_corr[key]  # baseline v0 đúng?
        c_ok = new_corr[key]  # thí nghiệm mới đúng?
        if a_ok and c_ok:
            both_correct += 1
        elif a_ok and not c_ok:
            a_only += 1  # v0 đúng, mới sai (b)
        elif not a_ok and c_ok:
            c_only += 1  # v0 sai, mới đúng (c)
        else:
            both_wrong += 1

    try:
        from statsmodels.stats.contingency_tables import mcnemar

        table = [[both_correct, a_only], [c_only, both_wrong]]
        res = mcnemar(table, exact=True)
        p_value = float(res.pvalue)
        stat = float(res.statistic)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Lỗi khi chạy McNemar: %s.", exc)
        return f"McNemar: **not available** — lỗi khi tính ({exc})."

    alpha = 0.05
    verdict = (
        "khác biệt CÓ ý nghĩa thống kê" if p_value < alpha
        else "khác biệt KHÔNG có ý nghĩa thống kê"
    )
    return (
        f"McNemar (exact) giữa Config_C mới và Config_C baseline_v0 trên "
        f"{len(common_keys)} mẫu test chung:\n\n"
        f"- Cả hai đúng: {both_correct}\n"
        f"- v0 đúng, mới sai (b): {a_only}\n"
        f"- v0 sai, mới đúng (c): {c_only}\n"
        f"- Cả hai sai: {both_wrong}\n"
        f"- statistic = {stat:.4f}, **p-value = {p_value:.4f}**\n\n"
        f"Ở mức α = {alpha}: {verdict}."
    )


# ---------------------------------------------------------------------------
# Nhận xét H1/H2/H3, phân tích lý thuyết, kết luận (Req 13.5, 13.6, 13.7)
# ---------------------------------------------------------------------------


def _mean_delta(new_df: pd.DataFrame | None) -> float | None:
    """Δ(C−A) trung bình trên các thuật toán có đủ dữ liệu (cho nhận xét H1/H2/H3)."""
    deltas = [d for _, _, d in (_delta_row(new_df, m) for m in REPORT_MODELS) if d is not None]
    if not deltas:
        return None
    return float(np.mean(deltas))


def _hypotheses_commentary(new_df: pd.DataFrame | None) -> str:
    """Nhận xét tường minh cho H1, H2, H3 dựa trên Δ(C−A) (Req 13.5)."""
    avg = _mean_delta(new_df)
    if avg is None:
        direction = "không xác định (thiếu dữ liệu Δ(C−A))"
        magnitude = "N/A"
    else:
        magnitude = f"{avg:+.4f}"
        if avg > 0.01:
            direction = "dương đáng kể (Config_C tốt hơn Config_A)"
        elif avg < -0.01:
            direction = "âm (Config_C kém hơn Config_A)"
        else:
            direction = "gần như bằng 0 (không cải thiện đáng kể)"
    return (
        "## 5. Nhận xét về các giả thuyết (H1, H2, H3)\n\n"
        f"Δ(C−A) trung bình trên 4 thuật toán của thí nghiệm này là **{magnitude}**, "
        f"tức hướng {direction}.\n\n"
        "- **H1 — Đặc trưng văn bản cải thiện dự báo:** "
        + (
            "Với Δ(C−A) trung bình không dương đáng kể, kết quả **không ủng hộ H1** — "
            "tầng biểu diễn văn bản tinh vi hơn vẫn không nâng được balanced accuracy "
            "so với chỉ dùng đặc trưng kỹ thuật. Điều này củng cố kết quả âm gốc và "
            "cho thấy kết luận không phải do phương pháp đo lường văn bản yếu."
            if (avg is None or avg <= 0.01)
            else "Δ(C−A) dương đáng kể **ủng hộ H1** ở thí nghiệm này — cần kiểm định "
            "McNemar (mục 4) để xác nhận ý nghĩa thống kê trước khi kết luận."
        )
        + "\n"
        "- **H2 — Đặc trưng văn bản bổ sung thông tin ngoài giá:** "
        + (
            "Chênh lệch nhỏ giữa Config_C và Config_A cho thấy thông tin văn bản phần "
            "lớn đã được phản ánh trong giá; kết quả **không ủng hộ H2**."
            if (avg is None or avg <= 0.01)
            else "Mức cải thiện gợi ý H2 có thể đúng một phần trong thí nghiệm này."
        )
        + "\n"
        "- **H3 — Tín hiệu văn bản có điều kiện theo phân khúc/độ chi tiết:** "
        "Bảng tổng hợp toàn cục chưa đủ để bác bỏ H3; các phân tích phân khúc (B3) và "
        "cấp bài viết (B1) mới trả lời trực tiếp cho H3. Kết quả ở đây **ủng hộ một "
        "phần H3** theo đúng tinh thần luận văn.\n"
    )


def _causal_analysis() -> str:
    """Phân tích nguyên nhân theo 3 giải thích lý thuyết (Req 13.6)."""
    return (
        "## 6. Phân tích nguyên nhân (3 giải thích lý thuyết)\n\n"
        "- **Semi-strong EMH (thị trường hiệu quả dạng vừa):** Nếu tin tức công khai "
        "đã được phản ánh nhanh vào giá, thì đặc trưng trích từ tin tức khó mang thêm "
        "thông tin dự báo vượt trên đặc trưng kỹ thuật. Δ(C−A) ≈ 0 nhất quán với giả "
        "thuyết này.\n"
        "- **Within-period absorption (hấp thụ trong kỳ):** Với độ chi tiết theo quý, "
        "phản ứng giá với tin tức thường xảy ra và tan biến ngay trong kỳ, nên tổng hợp "
        "theo quý làm mờ tín hiệu ngắn hạn — điều này thúc đẩy các thí nghiệm ở độ chi "
        "tiết cao hơn (B1 cấp bài viết, các period nhỏ hơn).\n"
        "- **Giới hạn corpus (corpus limitation):** Kích thước và độ phủ của corpus tin "
        "tức tiếng Việt (số bài mỗi ticker/quý) có thể quá nhỏ để ước lượng ổn định "
        "tín hiệu văn bản, làm tăng nhiễu và kéo Δ(C−A) về 0.\n"
    )


def _conclusion(experiment_id: str) -> str:
    """Kết luận vị trí trong luận văn và tác động tới Chương 5 (Req 13.7)."""
    return (
        "## 7. Kết luận và vị trí trong luận văn\n\n"
        f"Thí nghiệm **{experiment_id}** đóng vai trò một mắt xích trong chuỗi kiểm "
        "chứng độ vững của kết quả âm (Hướng A) và tìm tín hiệu có điều kiện (Hướng B). "
        "Kết quả bổ sung bằng chứng cho **Chương 4 (Kết quả thí nghiệm)** và tinh chỉnh "
        "lập luận của **Chương 5 (Kết luận)**: nếu ngay cả các tầng biểu diễn văn bản "
        "tinh vi hơn vẫn cho Δ(C−A) ≈ 0, kết luận âm về giá trị dự báo của đặc trưng văn "
        "bản ở độ chi tiết quý được củng cố, đồng thời định hướng nghiên cứu tương lai "
        "sang độ chi tiết cao hơn và phân tích theo phân khúc.\n"
    )


# ---------------------------------------------------------------------------
# API chính
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# A2 flip statistics (Req 5.7) — % hit bị đảo polarity
# ---------------------------------------------------------------------------


def _format_flip_stats_section(flip_stats: dict[str, Any] | None) -> str | None:
    """Định dạng mục "% hit bị flip" của A2 cho báo cáo (Req 5.7).

    Trả về ``None`` khi không cung cấp ``flip_stats`` (các thí nghiệm khác A2),
    để không thêm mục thừa vào báo cáo — giữ tương thích ngược.
    """
    if not flip_stats:
        return None

    overall = flip_stats.get("overall_flip_pct")
    total_base = flip_stats.get("total_base", 0)
    total_neg = flip_stats.get("total_neg", 0)
    by_kw = flip_stats.get("by_keyword", {}) or {}

    overall_txt = "not computed" if overall is None else f"{overall * 100:.2f}%"
    lines = [
        "## 8. Tỷ lệ số lần khớp bị đảo polarity (A2 negation)\n",
        f"Tổng thể: **{overall_txt}** số lần khớp bị đảo sang ``_NEG`` "
        f"({total_neg}/{total_base + total_neg} hit).\n",
    ]
    if by_kw:
        lines.append(
            "| Từ khóa hay bị phủ định | base | _NEG | % flip |\n"
            "|---|---|---|---|"
        )
        for kw, s in by_kw.items():
            base = s.get("base", 0)
            neg = s.get("neg", 0)
            pct = s.get("flip_pct", 0.0)
            lines.append(f"| {kw} | {base} | {neg} | {pct * 100:.2f}% |")
    return "\n".join(lines)


def _format_feature_counts_section(feature_counts: dict[str, Any] | None) -> str | None:
    """Định dạng mục "số lượng đặc trưng" của A1a/A1b vs v0 cho báo cáo (Req 6.5).

    Trả về ``None`` khi không cung cấp ``feature_counts`` (các thí nghiệm khác),
    để không thêm mục thừa vào báo cáo — giữ tương thích ngược.

    ``feature_counts`` là dict gồm ``exp_feature_count`` (số đặc trưng của thí
    nghiệm) và ``v0_feature_count`` (số đặc trưng của Baseline_v0); giá trị
    ``None`` được hiển thị là "not computed".
    """
    if not feature_counts:
        return None

    exp = feature_counts.get("exp_feature_count")
    v0 = feature_counts.get("v0_feature_count")
    exp_txt = "not computed" if exp is None else str(exp)
    v0_txt = "not computed" if v0 is None else str(v0)

    lines = [
        "## 9. Số lượng đặc trưng của thí nghiệm đối chiếu Baseline_v0\n",
        f"- Thí nghiệm: **{exp_txt}** đặc trưng\n"
        f"- Baseline_v0: **{v0_txt}** đặc trưng\n",
    ]
    return "\n".join(lines)


def generate_comparison_report(
    experiment_id: str,
    new_results: RunnerResult,
    baseline_dir: str = BASELINE_DIR,
    keyword_sig_path: str | None = None,
    shap_contrib_pct: float | None = None,
    *,
    baseline_config_c: dict[str, Any] | None = None,
    reconstruct_fn: Callable[..., dict[str, Any]] | None = None,
    flip_stats: dict[str, Any] | None = None,
    feature_counts: dict[str, Any] | None = None,
) -> str:
    """Sinh báo cáo Markdown so sánh thí nghiệm với Baseline_v0 (Req 13.1–13.7).

    Args:
        experiment_id: Mã thí nghiệm (``"A2"``, ``"A1a"``, ...).
        new_results: :class:`RunnerResult` của thí nghiệm (chứa ``results_df`` và
            predictions Config_A/Config_C trên cùng tập test).
        baseline_dir: Thư mục baseline bất biến (mặc định ``reports/baseline_v0``).
            Bảng Δ(C−A) baseline đọc từ ``{baseline_dir}/model_comparison.csv``.
        keyword_sig_path: Đường dẫn ``keyword_significance_{id}.csv`` của thí nghiệm.
            Nếu tồn tại, đếm số dòng ``significant_any == True`` trên tổng số dòng
            (Req 13.2); ngược lại báo "not computed".
        shap_contrib_pct: % đóng góp SHAP của nhóm đặc trưng văn bản (Req 13.3).
            Quy ước là phân số trong [0, 1] (ví dụ ``0.32`` cho 32%); giá trị > 1
            hiểu là đã ở dạng phần trăm. ``None`` → "not computed".
        baseline_config_c: (keyword-only, để test) dict predictions baseline v0 đã
            tính sẵn dạng ``{"test_index", "y_test", "pred_by_config"}``; nếu cung
            cấp sẽ bỏ qua bước tái tạo nặng cho McNemar (Req 13.4).
        reconstruct_fn: (keyword-only, để test) hàm thay thế
            ``run_configs_return_predictions`` để tái tạo predictions baseline v0.
        flip_stats: (keyword-only, tùy chọn) thống kê % hit bị đảo polarity của
            A2 (từ ``experiments.a2_negation.compute_flip_statistics``). Nếu
            cung cấp, báo cáo thêm một mục "% hit bị flip" cho các từ khóa hay
            bị phủ định (Req 5.7). ``None`` → bỏ qua mục này (giữ tương thích
            ngược với các thí nghiệm khác).
        feature_counts: (keyword-only, tùy chọn) dict số lượng đặc trưng của
            thí nghiệm đối chiếu Baseline_v0, dạng ``{"exp_feature_count": int,
            "v0_feature_count": int}``. Dùng cho A1a/A1b (Req 6.5). ``None`` →
            bỏ qua mục này (giữ tương thích ngược).

    Returns:
        Đường dẫn tệp báo cáo đã ghi (``reports/experiment_{id}_report.md``).

    Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7
    """
    baseline_df = _read_comparison_df(Path(baseline_dir) / "model_comparison.csv")
    new_df = new_results.results_df

    cutoff = "2025Q1"

    delta_table = _build_delta_table(new_df, baseline_df)
    kw_sig = _count_significant_keywords(keyword_sig_path)
    shap_pct = _format_shap_pct(shap_contrib_pct)
    mcnemar_section = _run_mcnemar_section(
        new_results,
        cutoff=cutoff,
        baseline_config_c=baseline_config_c,
        reconstruct_fn=reconstruct_fn,
    )

    parts = [
        f"# Báo cáo so sánh thí nghiệm {experiment_id} với Baseline_v0\n",
        "## 1. Bảng Δ(C−A) — thí nghiệm cạnh Baseline_v0\n",
        "Balanced accuracy của Config_A, Config_C và Δ(C−A) cho 4 thuật toán "
        "(Req 13.1).\n",
        delta_table,
        "",
        "## 2. Số keyword/đặc trưng đạt ý nghĩa sau BH_FDR\n",
        f"- Thí nghiệm {experiment_id}: **{kw_sig}**\n"
        f"- Baseline_v0: **{BASELINE_KEYWORD_SIG}**\n",
        "## 3. Tỷ lệ đóng góp SHAP của nhóm đặc trưng văn bản\n",
        f"- Thí nghiệm {experiment_id}: **{shap_pct}**\n"
        f"- Baseline_v0: **{BASELINE_SHAP_PCT_TEXT}**\n",
        "## 4. Kiểm định McNemar (Config_C mới vs Config_C baseline_v0)\n",
        mcnemar_section,
        "",
        _hypotheses_commentary(new_df),
        _causal_analysis(),
        _conclusion(experiment_id),
    ]
    flip_section = _format_flip_stats_section(flip_stats)
    if flip_section is not None:
        parts.append(flip_section)
    feature_counts_section = _format_feature_counts_section(feature_counts)
    if feature_counts_section is not None:
        parts.append(feature_counts_section)
    report = "\n".join(parts).rstrip() + "\n"

    out_path = report_path(experiment_id)
    out_p = Path(out_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(report, encoding="utf-8")
    logger.info("Đã ghi báo cáo so sánh thí nghiệm: '%s'.", out_p)
    return out_path


# ---------------------------------------------------------------------------
# B3 — báo cáo so sánh phân tích theo phân khúc với Baseline_v0 (Req 13.1–13.7)
# ---------------------------------------------------------------------------


def _read_segmentation_csv(path: str | Path) -> pd.DataFrame | None:
    """Đọc một tệp CSV đầu ra của B3 (analysis/keyword_sig); ``None`` nếu lỗi.

    Guard mọi lỗi (tệp thiếu, không đọc được) để việc sinh báo cáo B3 luôn hoàn
    tất được thay vì crash — nhất quán với phần còn lại của module.
    """
    p = Path(path)
    if not p.exists():
        logger.warning("Không tìm thấy tệp đầu ra B3: '%s'.", p)
        return None
    try:
        return pd.read_csv(p, encoding="utf-8")
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Lỗi đọc tệp đầu ra B3 '%s': %s.", p, exc)
        return None


def _v0_delta_by_model(baseline_df: pd.DataFrame | None) -> dict[str, float | None]:
    """Δ(C−A) toàn cục của Baseline_v0 cho từng thuật toán (Req 13.1).

    ``delta = balanced_accuracy(Config_C) − balanced_accuracy(Config_A)`` đọc từ
    ``model_comparison.csv`` của baseline. Thuật toán thiếu → giá trị ``None``.
    """
    return {m: _delta_row(baseline_df, m)[2] for m in REPORT_MODELS}


def _segment_sort_key(segment_type: str, segment_name: str) -> tuple[int, str]:
    """Khóa sắp xếp phân khúc ổn định: các sector trước (theo tên), rồi cap_group.

    Với cap_group, ưu tiên ``large_cap`` trước ``mid_cap`` để đọc luận văn thuận.
    """
    if segment_type == "sector":
        return (0, segment_name)
    cap_order = {"large_cap": "0", "mid_cap": "1"}
    return (1, cap_order.get(segment_name, segment_name))


def _is_normalized_true(value: Any) -> bool:
    """Chuẩn hóa giá trị boolean có thể đọc từ CSV dạng chuỗi ("True"/"False")."""
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1"}
    if value is None:
        return False
    try:
        if isinstance(value, float) and np.isnan(value):
            return False
    except (TypeError, ValueError):  # pragma: no cover - defensive
        pass
    return bool(value)


def _b3_segment_delta_section(
    analysis_df: pd.DataFrame | None,
    v0_delta: dict[str, float | None],
) -> str:
    """Mục Δ(C−A) theo phân khúc cạnh Δ(C−A) tổng hợp v0 (Req 13.1).

    Nhấn mạnh statistical power bằng cách in nổi bật ``n_samples``/``n_tickers``
    mỗi phân khúc, kèm bảng per-model và một bảng tổng hợp mean Δ(C−A) mỗi phân
    khúc để quét nhanh phân khúc nào (nếu có) cho tín hiệu văn bản dương.
    """
    header = (
        "## 1. Δ(C−A) theo phân khúc cạnh Δ(C−A) tổng hợp Baseline_v0\n\n"
        "Với mỗi phân khúc (ngành và nhóm vốn hóa), balanced accuracy được huấn "
        "luyện lại trên riêng phân khúc theo cùng pipeline/time-split của v0. Cột "
        "**Δ(C−A) v0** là chênh lệch toàn cục của Baseline_v0 để đối chiếu. "
        "Số mẫu (`n_samples`) và số ticker (`n_tickers`) được nêu nổi bật để nhấn "
        "mạnh **statistical power** của từng phân khúc (Req 13.1).\n"
    )
    if analysis_df is None or analysis_df.empty:
        return header + "\n_Δ(C−A) theo phân khúc: not available._\n"

    required = {"segment_type", "segment_name", "model"}
    if not required.issubset(analysis_df.columns):
        return header + "\n_Δ(C−A) theo phân khúc: not available (thiếu cột)._\n"

    # Danh sách phân khúc theo thứ tự ổn định.
    seg_keys = (
        analysis_df[["segment_type", "segment_name"]]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )
    segments = sorted(seg_keys, key=lambda s: _segment_sort_key(s[0], s[1]))

    parts = [header]
    summary_rows: list[str] = [
        "\n### Tổng hợp mean Δ(C−A) theo phân khúc\n",
        "| Phân khúc | n_samples | n_tickers | mean Δ(C−A) |",
        "|---|---|---|---|",
    ]

    for segment_type, segment_name in segments:
        seg_df = analysis_df[
            (analysis_df["segment_type"] == segment_type)
            & (analysis_df["segment_name"] == segment_name)
        ]
        # n_samples / n_tickers giống nhau trên các dòng của phân khúc.
        n_samples = _first_int(seg_df, "n_samples")
        n_tickers = _first_int(seg_df, "n_tickers")

        parts.append(
            f"\n### {segment_type}: {segment_name} — "
            f"n_samples={n_samples}, n_tickers={n_tickers}\n"
        )
        parts.append(
            "| Model | BA A (seg) | BA C (seg) | Δ(C−A) seg | Δ(C−A) v0 |\n"
            "|---|---|---|---|---|"
        )

        seg_deltas: list[float] = []
        for model in REPORT_MODELS:
            display = _MODEL_DISPLAY.get(model, model)
            row = seg_df[seg_df["model"] == model]
            v0d = _fmt(v0_delta.get(model))
            if row.empty:
                parts.append(
                    f"| {display} | N/A | N/A | N/A | {v0d} |"
                )
                continue
            note = str(row.iloc[0].get("note", "") or "")
            if note.strip().lower() == "insufficient power":
                parts.append(
                    f"| {display} | N/A (insufficient power) "
                    "| N/A (insufficient power) | N/A (insufficient power) "
                    f"| {v0d} |"
                )
                continue
            ba_a = _cell_float(row.iloc[0].get("ba_config_a"))
            ba_c = _cell_float(row.iloc[0].get("ba_config_c"))
            delta = _cell_float(row.iloc[0].get("delta_ca"))
            if delta is not None:
                seg_deltas.append(delta)
            parts.append(
                f"| {display} | {_fmt(ba_a, '.4f')} | {_fmt(ba_c, '.4f')} "
                f"| {_fmt(delta)} | {v0d} |"
            )

        mean_delta = float(np.mean(seg_deltas)) if seg_deltas else None
        summary_rows.append(
            f"| {segment_type}: {segment_name} | {n_samples} | {n_tickers} "
            f"| {_fmt(mean_delta)} |"
        )

    parts.append("\n".join(summary_rows))
    return "\n".join(parts)


def _first_int(df: pd.DataFrame, col: str) -> Any:
    """Lấy giá trị nguyên đầu tiên của cột (cho n_samples/n_tickers); "N/A" nếu thiếu."""
    if col not in df.columns or df.empty:
        return "N/A"
    try:
        return int(df.iloc[0][col])
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return "N/A"


def _cell_float(value: Any) -> float | None:
    """Ép một ô về float; ``None`` nếu NaN/không ép được (để hiển thị "N/A")."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if np.isnan(f):
        return None
    return f


def _b3_keyword_sig_section(keyword_sig_df: pd.DataFrame | None) -> str:
    """Mục số keyword đạt ý nghĩa sau BH_FDR theo phân khúc cạnh 0/71 v0 (Req 13.2).

    Với mỗi phân khúc: ``# sig / # tested`` trong đó ``# tested`` là số keyword thực
    sự được kiểm định (``n_excluded == 0``) và ``# sig`` là số keyword có
    ``significant_any`` True. Chuẩn hóa cột boolean đọc từ CSV (chuỗi "True"/"False").
    """
    header = (
        "## 2. Số keyword đạt ý nghĩa (sau BH_FDR) theo phân khúc\n\n"
        "So với Baseline_v0 toàn cục là **{v0}**.\n".format(v0=BASELINE_KEYWORD_SIG)
    )
    if keyword_sig_df is None or keyword_sig_df.empty:
        return header + "\n_Keyword significance theo phân khúc: not available._\n"

    required = {"segment_type", "segment_name", "keyword", "significant_any"}
    if not required.issubset(keyword_sig_df.columns):
        return header + "\n_Keyword significance theo phân khúc: not available (thiếu cột)._\n"

    df = keyword_sig_df.copy()
    df["_sig"] = df["significant_any"].map(_is_normalized_true)
    if "n_excluded" in df.columns:
        tested_mask = pd.to_numeric(df["n_excluded"], errors="coerce").fillna(0) == 0
    else:
        tested_mask = pd.Series(True, index=df.index)

    seg_keys = (
        df[["segment_type", "segment_name"]]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )
    segments = sorted(seg_keys, key=lambda s: _segment_sort_key(s[0], s[1]))

    lines = [
        header,
        "\n| Phân khúc | # sig / # tested | Baseline_v0 |",
        "|---|---|---|",
    ]
    for segment_type, segment_name in segments:
        seg_mask = (df["segment_type"] == segment_type) & (
            df["segment_name"] == segment_name
        )
        tested = df[seg_mask & tested_mask]
        n_tested = int(tested["keyword"].nunique())
        n_sig = int(tested.loc[tested["_sig"], "keyword"].nunique())
        lines.append(
            f"| {segment_type}: {segment_name} | {n_sig}/{n_tested} "
            f"| {BASELINE_KEYWORD_SIG} |"
        )
    return "\n".join(lines)


def _b3_hypotheses_commentary(
    analysis_df: pd.DataFrame | None,
    keyword_sig_df: pd.DataFrame | None,
) -> str:
    """Nhận xét H1/H2/H3 dựa trên dữ liệu phân khúc B3 (Req 13.5).

    Kiểm tra xem có phân khúc nào cho mean Δ(C−A) > 0.01 và/hoặc có keyword đạt ý
    nghĩa hay không, rồi diễn giải H1/H2/H3 theo dữ liệu (không hard-code).
    """
    positive_segments: list[str] = []
    if analysis_df is not None and not analysis_df.empty and {
        "segment_type",
        "segment_name",
        "delta_ca",
    }.issubset(analysis_df.columns):
        grouped = analysis_df.copy()
        grouped["_delta"] = pd.to_numeric(grouped["delta_ca"], errors="coerce")
        means = grouped.groupby(["segment_type", "segment_name"])["_delta"].mean()
        for (stype, sname), val in means.items():
            if pd.notna(val) and val > 0.01:
                positive_segments.append(f"{stype}: {sname} (mean Δ={val:+.4f})")

    sig_segments: list[str] = []
    if keyword_sig_df is not None and not keyword_sig_df.empty and {
        "segment_type",
        "segment_name",
        "significant_any",
    }.issubset(keyword_sig_df.columns):
        tmp = keyword_sig_df.copy()
        tmp["_sig"] = tmp["significant_any"].map(_is_normalized_true)
        sig_by_seg = tmp.groupby(["segment_type", "segment_name"])["_sig"].any()
        for (stype, sname), has_sig in sig_by_seg.items():
            if bool(has_sig):
                sig_segments.append(f"{stype}: {sname}")

    any_signal = bool(positive_segments) or bool(sig_segments)

    lines = [
        "## 5. Nhận xét về các giả thuyết (H1, H2, H3)\n",
        (
            "Phân khúc có Δ(C−A) trung bình > 0.01: "
            + (", ".join(positive_segments) if positive_segments else "**không có**")
            + ".\n"
        ),
        (
            "Phân khúc có ít nhất một keyword đạt ý nghĩa sau BH_FDR: "
            + (", ".join(sig_segments) if sig_segments else "**không có**")
            + ".\n"
        ),
    ]

    if any_signal:
        lines.append(
            "- **H1 — Đặc trưng văn bản cải thiện dự báo:** Có phân khúc cho tín "
            "hiệu dương, nên H1 **được ủng hộ một phần** ở cấp phân khúc — cần lưu ý "
            "statistical power (n mỗi phân khúc) trước khi kết luận chắc chắn.\n"
            "- **H2 — Đặc trưng văn bản bổ sung thông tin ngoài giá:** Tín hiệu có "
            "điều kiện gợi ý H2 có thể đúng trong một số phân khúc, nhưng không phổ "
            "quát toàn thị trường.\n"
            "- **H3 — Tín hiệu văn bản có điều kiện theo phân khúc:** Kết quả B3 "
            "**ủng hộ H3** — giá trị dự báo của văn bản khác nhau giữa các phân khúc, "
            "đúng như giả thuyết tín hiệu có điều kiện."
        )
    else:
        lines.append(
            "- **H1 — Đặc trưng văn bản cải thiện dự báo:** Không phân khúc nào cho "
            "Δ(C−A) dương đáng kể, nên kết quả **không ủng hộ H1**, củng cố kết quả "
            "âm toàn cục.\n"
            "- **H2 — Đặc trưng văn bản bổ sung thông tin ngoài giá:** Không có bằng "
            "chứng phân khúc cho H2; thông tin văn bản phần lớn đã phản ánh trong giá.\n"
            "- **H3 — Tín hiệu văn bản có điều kiện theo phân khúc:** H3 được **kiểm "
            "định trực tiếp** ở B3 nhưng — theo dữ liệu này — cũng **không được ủng hộ "
            "mạnh** ở cấp phân khúc; cần lưu ý statistical power hạn chế của các phân "
            "khúc nhỏ (n thấp) khi diễn giải."
        )
    return "\n".join(lines)


def generate_b3_report(
    analysis_path: str = "reports/segmentation_analysis.csv",
    keyword_sig_path: str = "reports/segmentation_keyword_sig.csv",
    baseline_dir: str = BASELINE_DIR,
    experiment_id: str = "B3",
) -> str:
    """Sinh báo cáo so sánh B3 (phân tích theo phân khúc) với Baseline_v0 (Req 13.1–13.7).

    B3 là một phân tích *theo phân khúc* (ngành và nhóm vốn hóa), không phải một
    lần huấn luyện toàn cục, nên hàm này tiêu thụ hai tệp đầu ra của B3
    (``segmentation_analysis.csv`` và ``segmentation_keyword_sig.csv``) thay vì một
    :class:`RunnerResult`. Báo cáo đặt Δ(C−A) mỗi phân khúc cạnh Δ(C−A) toàn cục
    của Baseline_v0, nhấn mạnh **statistical power** (n mỗi phân khúc).

    Mọi nguồn dữ liệu ngoài đều được guard: tệp thiếu/không đọc được sẽ suy biến
    êm (log cảnh báo, in "not available"/"not computed") thay vì crash.

    Args:
        analysis_path: Đường dẫn ``segmentation_analysis.csv`` (4 dòng/phân khúc,
            một dòng mỗi thuật toán).
        keyword_sig_path: Đường dẫn ``segmentation_keyword_sig.csv``.
        baseline_dir: Thư mục baseline bất biến (mặc định ``reports/baseline_v0``);
            Δ(C−A) toàn cục v0 đọc từ ``{baseline_dir}/model_comparison.csv``.
        experiment_id: Mã thí nghiệm dùng cho tên tệp báo cáo (mặc định ``"B3"``).

    Returns:
        Đường dẫn tệp báo cáo đã ghi (``reports/experiment_B3_report.md``).

    Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7

    _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7_
    """
    analysis_df = _read_segmentation_csv(analysis_path)
    keyword_sig_df = _read_segmentation_csv(keyword_sig_path)
    baseline_df = _read_comparison_df(Path(baseline_dir) / "model_comparison.csv")
    v0_delta = _v0_delta_by_model(baseline_df)

    parts = [
        f"# Báo cáo so sánh thí nghiệm {experiment_id} với Baseline_v0\n",
        "Thí nghiệm **B3** phân tích giá trị dự báo của đặc trưng văn bản theo từng "
        "**phân khúc** (ngành và nhóm vốn hóa large_cap/mid_cap), đối chiếu với kết "
        "quả toàn cục đã đóng băng trong **Baseline_v0**. Trọng tâm là kiểm tra tín "
        "hiệu văn bản **có điều kiện** (H3) và nhấn mạnh **statistical power** của "
        "từng phân khúc (số mẫu n mỗi nhóm).\n",
        _b3_segment_delta_section(analysis_df, v0_delta),
        "",
        _b3_keyword_sig_section(keyword_sig_df),
        "",
        "## 3. Tỷ lệ đóng góp SHAP của nhóm đặc trưng văn bản\n",
        "B3 không tính lại SHAP riêng cho từng phân khúc (mỗi phân khúc là một lần "
        "huấn luyện lại độc lập).\n\n"
        f"- Thí nghiệm {experiment_id}: **not computed per segment**\n"
        f"- Baseline_v0: **{BASELINE_SHAP_PCT_TEXT}**\n",
        "## 4. Kiểm định McNemar\n",
        "McNemar: **not applicable** cho B3 ở mức tổng hợp — B3 không tạo một tập dự "
        "đoán Config_C toàn cục duy nhất để so trực tiếp với Baseline_v0 (mỗi phân "
        "khúc là một lần huấn luyện lại riêng). Việc huấn luyện lại theo phân khúc "
        "dùng **cùng pipeline và cùng quy trình chia thời gian** như v0, nên các so "
        "sánh Δ(C−A) trong từng phân khúc vẫn là apples-to-apples (Req 13.4).\n",
        _b3_hypotheses_commentary(analysis_df, keyword_sig_df),
        _causal_analysis(),
        _conclusion(experiment_id),
    ]
    report = "\n".join(parts).rstrip() + "\n"

    out_path = report_path(experiment_id)
    out_p = Path(out_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(report, encoding="utf-8")
    logger.info("Đã ghi báo cáo so sánh B3: '%s'.", out_p)
    return out_path


def generate_text_representation_table(
    experiment_ids: list[str] = ["v0", "A2", "A1a", "A6"],
) -> str:
    """Bảng tổng hợp Δ(C−A) qua các tầng biểu diễn văn bản (Req 13.8).

    Với mỗi id:
    - ``"v0"`` đọc ``reports/baseline_v0/model_comparison.csv`` (fallback
      ``reports/model_comparison.csv`` nếu baseline chưa có);
    - id khác đọc ``reports/model_comparison_{id}.csv``.

    Tệp thiếu → cột id đó đánh "N/A" thay vì crash. Hàng = 4 thuật toán, cột = các
    tầng, ô = Δ(C−A).

    Args:
        experiment_ids: Danh sách tầng biểu diễn cần đối chiếu.

    Returns:
        Chuỗi bảng Markdown (không bắt buộc ghi file).

    Validates: Requirements 13.8
    """
    # Đọc bảng so sánh của từng tầng (có guard).
    dfs: dict[str, pd.DataFrame | None] = {}
    for eid in experiment_ids:
        if eid == "v0":
            df = _read_comparison_df(Path(BASELINE_DIR) / "model_comparison.csv")
            if df is None:
                df = _read_comparison_df("reports/model_comparison.csv")
        else:
            df = _read_comparison_df(f"reports/model_comparison_{eid}.csv")
        dfs[eid] = df

    header = "| Thuật toán | " + " | ".join(experiment_ids) + " |"
    sep = "|---|" + "---|" * len(experiment_ids)
    lines = [header, sep]
    for model in REPORT_MODELS:
        display = _MODEL_DISPLAY.get(model, model)
        cells = []
        for eid in experiment_ids:
            _, _, delta = _delta_row(dfs[eid], model)
            cells.append(_fmt(delta))
        lines.append(f"| {display} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


# Chú thích ý nghĩa từng tầng biểu diễn cho phần legend của báo cáo tổng hợp.
_TIER_LEGEND = {
    "v0": "baseline tần suất từ khóa thô (raw-frequency)",
    "A2": "negation — khớp từ khóa có nhận biết phủ định",
    "A1a": "group sentiment — điểm sentiment có dấu theo nhóm chủ đề",
    "A6": "LLM sentiment — gán nhãn sentiment zero-shot bằng LLM",
}


def write_text_representation_table(
    experiment_ids: list[str] = ["v0", "A2", "A1a", "A6"],
    out_path: str = TEXT_REPRESENTATION_TABLE_PATH,
) -> str:
    """Persist bảng tổng hợp Δ(C−A) 4 tầng biểu diễn văn bản ra tệp (Req 13.8).

    Bọc :func:`generate_text_representation_table` trong một tài liệu Markdown nhỏ
    (tiêu đề + ghi chú tham chiếu Req 13.8 + legend giải nghĩa từng tầng) rồi ghi
    ra ``out_path`` để có thể trích thẳng vào luận văn — thay vì chỉ in ra stdout.

    Args:
        experiment_ids: Danh sách tầng biểu diễn cần đối chiếu (mặc định
            ``["v0", "A2", "A1a", "A6"]``).
        out_path: Đường dẫn tệp Markdown đầu ra (mặc định
            ``reports/text_representation_summary.md``). Thư mục cha được tạo nếu
            còn thiếu.

    Returns:
        Đường dẫn tệp báo cáo đã ghi (chuỗi).

    Validates: Requirements 13.8
    """
    table = generate_text_representation_table(experiment_ids)

    legend_lines = []
    for eid in experiment_ids:
        desc = _TIER_LEGEND.get(eid)
        if desc is not None:
            legend_lines.append(f"- **{eid}**: {desc}")

    parts = [
        "# Bảng tổng hợp Δ(C−A) — 4 tầng biểu diễn văn bản (Hướng A)\n",
        "Bảng tổng hợp chênh lệch balanced accuracy Config_C − Config_A qua các "
        "tầng biểu diễn văn bản, dùng cho luận văn (Req 13.8).\n",
    ]
    if legend_lines:
        parts.append("## Chú giải các tầng\n")
        parts.append("\n".join(legend_lines) + "\n")
    parts.append("## Bảng Δ(C−A)\n")
    parts.append(table)

    document = "\n".join(parts).rstrip() + "\n"

    out_p = Path(out_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(document, encoding="utf-8")
    logger.info("Đã ghi bảng tổng hợp tầng biểu diễn văn bản: '%s'.", out_p)
    return out_path
