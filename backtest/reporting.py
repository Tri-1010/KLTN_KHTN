"""Backtest_Reporter (`backtest/reporting.py`) — báo cáo tổng hợp cho luận văn (Req 9).

Module này gộp toàn bộ artifact do các thành phần backtest sinh ra thành một báo
cáo Markdown duy nhất, đưa thẳng vào chương kết quả của luận văn:

- ``reports/backtest_performance.csv`` — bảng chỉ số hiệu quả của chiến lược mô
  hình cạnh mọi Benchmark_Strategy (Req 9.1);
- ``reports/walk_forward_results.csv`` — kết quả walk-forward + nhận xét ổn định
  (Req 9.2);
- ``reports/technical_feature_importance.csv`` — bảng xếp hạng tầm quan trọng đặc
  trưng kỹ thuật (Req 9.3);
- ``reports/leakage_audit.md`` — tóm tắt/nhúng kết quả kiểm toán rò rỉ (Req 9.3);
- nhận xét tường minh mô hình có/không tạo giá trị vượt benchmark kèm giả định thị
  trường cơ sở VN và giới hạn (Req 9.4);
- ghi kết quả ra ``reports/technical_ml_backtest_report.md`` (Req 9.5).

Thiết kế chịu lỗi: nếu một artifact đầu vào còn thiếu (chạy báo cáo trước khi có đủ
kết quả), báo cáo vẫn được sinh ra với ghi chú "(chưa có dữ liệu — chạy bước tương
ứng)" thay vì làm sập toàn bộ.
"""

from __future__ import annotations

import os
from typing import Optional

import pandas as pd

from backtest.strategy import VN_MARKET_ASSUMPTIONS

# Đường dẫn artifact mặc định (tương đối thư mục reports/).
PERFORMANCE_CSV = "backtest_performance.csv"
WALK_FORWARD_CSV = "walk_forward_results.csv"
FEATURE_IMPORTANCE_CSV = "technical_feature_importance.csv"
LEAKAGE_AUDIT_MD = "leakage_audit.md"

_MISSING_NOTE = "*(chưa có dữ liệu — chạy bước tương ứng)*"


def _df_to_markdown(df: pd.DataFrame) -> str:
    """Render một DataFrame thành bảng Markdown.

    Dùng :meth:`DataFrame.to_markdown` khi thư viện ``tabulate`` khả dụng; nếu
    không, dựng bảng Markdown thủ công để module không phụ thuộc cứng vào
    ``tabulate``.
    """
    try:
        import tabulate  # noqa: F401

        return df.to_markdown(index=False)
    except Exception:
        return _manual_markdown_table(df)


def _fmt_cell(value: object) -> str:
    """Định dạng một ô: số thực gọn 6 chữ số ý nghĩa, còn lại ép chuỗi."""
    if isinstance(value, float):
        if pd.isna(value):
            return ""
        return f"{value:.6g}"
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value)


def _manual_markdown_table(df: pd.DataFrame) -> str:
    """Dựng bảng Markdown thủ công (fallback khi thiếu ``tabulate``)."""
    columns = [str(c) for c in df.columns]
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    rows = []
    for _, row in df.iterrows():
        cells = [_fmt_cell(row[c]) for c in df.columns]
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, separator, *rows])


def _read_csv(path: str) -> Optional[pd.DataFrame]:
    """Đọc CSV nếu tồn tại, ngược lại trả ``None`` (chịu lỗi khi thiếu artifact)."""
    if not os.path.exists(path):
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def _section_performance(df: Optional[pd.DataFrame]) -> str:
    """Mục 1 — bảng chỉ số hiệu quả mọi chiến lược (Req 9.1)."""
    lines = ["## 1. Chỉ số hiệu quả đầu tư (Req 9.1)", ""]
    if df is None or df.empty:
        lines.append(
            f"Chưa có `{PERFORMANCE_CSV}`. {_MISSING_NOTE} "
            "(chạy Performance_Evaluator: `evaluate_all`)."
        )
        return "\n".join(lines)
    lines.append(
        "Bảng dưới liệt kê chỉ số của chiến lược mô hình cạnh các benchmark "
        "(buy-and-hold, equal-weight tái cân bằng), ở cả hai kịch bản gross/net."
    )
    lines.append("")
    lines.append(_df_to_markdown(df))
    return "\n".join(lines)


def _section_walk_forward(df: Optional[pd.DataFrame]) -> str:
    """Mục 2 — kết quả walk-forward + nhận xét ổn định (Req 9.2)."""
    lines = ["## 2. Độ ổn định theo thời gian — walk-forward (Req 9.2)", ""]
    if df is None or df.empty:
        lines.append(
            f"Chưa có `{WALK_FORWARD_CSV}`. {_MISSING_NOTE} "
            "(chạy Walk_Forward_Evaluator: `run_walk_forward`)."
        )
        return "\n".join(lines)
    lines.append(_df_to_markdown(df))
    lines.append("")
    lines.append("**Nhận xét về độ ổn định:**")
    lines.append("")
    lines.append(_walk_forward_commentary(df))
    return "\n".join(lines)


def _walk_forward_commentary(df: pd.DataFrame) -> str:
    """Sinh nhận xét ổn định dựa trên phân tán BA/return giữa các cutoff (Req 9.2)."""
    notes = []
    if "balanced_accuracy" in df.columns:
        ba = pd.to_numeric(df["balanced_accuracy"], errors="coerce").dropna()
        if len(ba) > 0:
            notes.append(
                f"Balanced accuracy qua {len(ba)} cutoff: trung bình "
                f"{ba.mean():.4f}, dao động [{ba.min():.4f}, {ba.max():.4f}] "
                f"(độ lệch chuẩn {ba.std(ddof=0):.4f})."
            )
    ret_col = "strategy_cumulative_return_net"
    if ret_col in df.columns:
        ret = pd.to_numeric(df[ret_col], errors="coerce").dropna()
        if len(ret) > 0:
            positive = int((ret > 0).sum())
            notes.append(
                f"Lợi nhuận tích lũy (net) của chiến lược mô hình dương ở "
                f"{positive}/{len(ret)} cutoff; trung bình {ret.mean():.4f}."
            )
    if "buy_hold_cumulative_return" in df.columns and ret_col in df.columns:
        ret = pd.to_numeric(df[ret_col], errors="coerce")
        bh = pd.to_numeric(df["buy_hold_cumulative_return"], errors="coerce")
        pair = pd.concat([ret, bh], axis=1).dropna()
        if len(pair) > 0:
            beat = int((pair.iloc[:, 0] > pair.iloc[:, 1]).sum())
            notes.append(
                f"Chiến lược mô hình vượt buy-and-hold ở {beat}/{len(pair)} cutoff."
            )
    if not notes:
        notes.append(
            "Không đủ cột số liệu để nhận xét định lượng; xem bảng walk-forward ở trên."
        )
    return "\n\n".join(notes)


def _section_feature_importance(df: Optional[pd.DataFrame]) -> str:
    """Mục 3a — bảng xếp hạng tầm quan trọng đặc trưng kỹ thuật (Req 9.3)."""
    lines = ["## 3. Diễn giải mô hình & kiểm toán rò rỉ (Req 9.3)", ""]
    lines.append("### 3.1. Tầm quan trọng đặc trưng kỹ thuật")
    lines.append("")
    if df is None or df.empty:
        lines.append(
            f"Chưa có `{FEATURE_IMPORTANCE_CSV}`. {_MISSING_NOTE} "
            "(chạy Model_Interpreter: `interpret_technical_model`)."
        )
        return "\n".join(lines)
    lines.append(_df_to_markdown(df))
    return "\n".join(lines)


def _section_leakage(md_content: Optional[str]) -> str:
    """Mục 3b — tóm tắt/nhúng kết quả kiểm toán rò rỉ (Req 9.3)."""
    lines = ["### 3.2. Tóm tắt kiểm toán rò rỉ dữ liệu", ""]
    if md_content is None:
        lines.append(
            f"Chưa có `{LEAKAGE_AUDIT_MD}`. {_MISSING_NOTE} "
            "(chạy Leakage_Auditor: `audit_leakage`)."
        )
        return "\n".join(lines)
    lines.append(f"Nội dung đầy đủ: xem `reports/{LEAKAGE_AUDIT_MD}`.")
    lines.append("")
    # Nhúng nguyên văn nội dung audit, hạ bậc heading một cấp để không phá cấu trúc.
    demoted = "\n".join(
        ("#" + line) if line.startswith("#") else line
        for line in md_content.splitlines()
    )
    lines.append("> Trích kết quả kiểm toán:")
    lines.append("")
    lines.append(demoted)
    return "\n".join(lines)


def _model_row(df: pd.DataFrame, scenario: str) -> Optional[pd.Series]:
    """Lấy hàng chiến lược ``model`` theo kịch bản (gross/net) nếu có."""
    if "strategy" not in df.columns:
        return None
    subset = df[df["strategy"] == "model"]
    if "cost_scenario" in df.columns:
        scen = subset[subset["cost_scenario"] == scenario]
        if not scen.empty:
            return scen.iloc[0]
    if not subset.empty:
        return subset.iloc[0]
    return None


def _commentary(perf: Optional[pd.DataFrame]) -> str:
    """Mục 4 — nhận xét mô hình có/không tạo giá trị vượt benchmark (Req 9.4).

    Nhận xét được suy ra từ dữ liệu khi có: so sánh ``cumulative_return`` và
    ``sharpe_ratio`` của chiến lược ``model`` (kịch bản net) với các benchmark.
    Luôn kèm giả định thị trường cơ sở VN và cảnh báo giới hạn.
    """
    lines = ["## 4. Nhận xét: mô hình có tạo giá trị vượt benchmark? (Req 9.4)", ""]

    verdict_written = False
    if perf is not None and not perf.empty and "strategy" in perf.columns:
        scenario = "net" if "cost_scenario" in perf.columns else "net"
        model_net = _model_row(perf, "net")
        if model_net is not None and "cumulative_return" in perf.columns:
            benchmarks = perf[perf["strategy"] != "model"]
            if "cost_scenario" in perf.columns:
                # Ưu tiên so sánh benchmark cùng kịch bản net, fallback mọi hàng.
                bench_net = benchmarks[benchmarks["cost_scenario"] == "net"]
                if not bench_net.empty:
                    benchmarks = bench_net

            m_ret = pd.to_numeric(
                pd.Series([model_net.get("cumulative_return")]), errors="coerce"
            ).iloc[0]

            comparisons = []
            beats_all = True
            for _, brow in benchmarks.iterrows():
                b_ret = pd.to_numeric(
                    pd.Series([brow.get("cumulative_return")]), errors="coerce"
                ).iloc[0]
                if pd.isna(b_ret) or pd.isna(m_ret):
                    continue
                verb = "vượt" if m_ret > b_ret else ("bằng" if m_ret == b_ret else "thấp hơn")
                if m_ret <= b_ret:
                    beats_all = False
                comparisons.append(
                    f"- So với **{brow.get('strategy')}**: lợi nhuận tích lũy mô hình "
                    f"{m_ret:.4f} {verb} {b_ret:.4f}."
                )

            if comparisons:
                verdict_written = True
                if beats_all:
                    lines.append(
                        "**Kết luận (dựa trên số liệu net):** mô hình TẠO giá trị đầu "
                        "tư vượt toàn bộ benchmark về lợi nhuận tích lũy trên khoảng "
                        "test hiện tại."
                    )
                else:
                    lines.append(
                        "**Kết luận (dựa trên số liệu net):** mô hình CHƯA vượt được "
                        "toàn bộ benchmark về lợi nhuận tích lũy; cần thận trọng khi "
                        "khẳng định giá trị đầu tư."
                    )
                lines.append("")
                lines.extend(comparisons)

                if "sharpe_ratio" in perf.columns:
                    m_sharpe = pd.to_numeric(
                        pd.Series([model_net.get("sharpe_ratio")]), errors="coerce"
                    ).iloc[0]
                    if not pd.isna(m_sharpe):
                        lines.append("")
                        lines.append(
                            f"- Sharpe ratio (net) của mô hình: {m_sharpe:.4f}."
                        )

    if not verdict_written:
        lines.append(
            "Chưa đủ số liệu hiệu quả (`backtest_performance.csv`) để kết luận định "
            f"lượng. {_MISSING_NOTE}"
        )

    # Giả định thị trường cơ sở VN (Req 2.8, 9.4).
    lines.append("")
    lines.append("### 4.1. Giả định thị trường chứng khoán cơ sở Việt Nam")
    lines.append("")
    lines.append(
        "Mọi kết quả trên chỉ có hiệu lực trong phạm vi các giả định sau (Req 2.8):"
    )
    lines.append("")
    for key, value in VN_MARKET_ASSUMPTIONS.items():
        lines.append(f"- **{key}**: {value}.")

    # Cảnh báo giới hạn (Req 9.4).
    lines.append("")
    lines.append("### 4.2. Giới hạn và cảnh báo")
    lines.append("")
    lines.append(
        "- Backtest theo đơn vị **quý** và dùng suất sinh lời kỳ, không mô phỏng "
        "khớp lệnh từng phiên; T+2/biên độ ±7%/lô 100 chỉ là giả định nền."
    )
    lines.append(
        "- Chỉ tính chi phí tường minh (brokerage + sell_tax), **bỏ qua trượt giá** "
        "và tác động thị trường; chi phí thực tế có thể cao hơn."
    )
    lines.append(
        "- Kết quả phụ thuộc khoảng thời gian test và tập 80 mã HOSE; walk-forward "
        "chỉ giảm nhẹ rủi ro phụ thuộc một cutoff, không đảm bảo hiệu lực tương lai."
    )
    lines.append(
        "- Lợi nhuận quá khứ **không đảm bảo** lợi nhuận tương lai; báo cáo phục vụ "
        "mục tiêu học thuật, không phải khuyến nghị đầu tư."
    )
    return "\n".join(lines)


def generate_backtest_report(
    reports_dir: str = "reports",
    output_path: str = "reports/technical_ml_backtest_report.md",
) -> str:
    """Sinh báo cáo tổng hợp backtest ML kỹ thuật (Req 9.1–9.5, 2.8).

    Gộp các artifact trong *reports_dir* thành một báo cáo Markdown và ghi ra
    *output_path*. Nếu một artifact còn thiếu, mục tương ứng vẫn được sinh với
    ghi chú "(chưa có dữ liệu)" thay vì làm sập báo cáo.

    Args:
        reports_dir: Thư mục chứa các artifact đầu vào và cũng là nơi ghi báo cáo.
        output_path: Đường dẫn tệp Markdown đầu ra.

    Returns:
        Chuỗi Markdown của báo cáo (đã đồng thời ghi ra *output_path*).
    """
    perf = _read_csv(os.path.join(reports_dir, PERFORMANCE_CSV))
    wf = _read_csv(os.path.join(reports_dir, WALK_FORWARD_CSV))
    fi = _read_csv(os.path.join(reports_dir, FEATURE_IMPORTANCE_CSV))

    leakage_path = os.path.join(reports_dir, LEAKAGE_AUDIT_MD)
    leakage_content: Optional[str] = None
    if os.path.exists(leakage_path):
        try:
            with open(leakage_path, "r", encoding="utf-8") as fh:
                leakage_content = fh.read()
        except Exception:
            leakage_content = None

    parts = [
        "# Báo cáo tổng hợp: Backtest ML trên đặc trưng kỹ thuật (HOSE-80)",
        "",
        "Báo cáo này tổng hợp kết quả đánh giá *giá trị đầu tư* của mô hình dự báo "
        "xu hướng giá dựa trên đặc trưng kỹ thuật (Config_A), theo đúng đặc thù thị "
        "trường chứng khoán cơ sở Việt Nam (long-only).",
        "",
        _section_performance(perf),
        "",
        _section_walk_forward(wf),
        "",
        _section_feature_importance(fi),
        "",
        _section_leakage(leakage_content),
        "",
        _commentary(perf),
        "",
    ]
    report = "\n".join(parts)

    os.makedirs(reports_dir, exist_ok=True)
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(report)

    return report
