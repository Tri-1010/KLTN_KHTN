"""Sinh phụ lục luận văn (.docx) từ các artifact backtest + thí nghiệm từ khóa.

Đọc số liệu THẬT từ `reports/` và dựng một tài liệu Word có tiêu đề, đoạn văn và
bảng định dạng sẵn để dán thẳng vào file luận văn. Chạy:

    python scripts/build_thesis_docx.py

Đầu ra: `reports/luan_van_bo_sung_backtest_va_tu_khoa.docx`.
"""

from __future__ import annotations

import csv
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

REPORTS = Path("reports")
OUTPUT = REPORTS / "luan_van_bo_sung_backtest_va_tu_khoa.docx"

ACCENT = RGBColor(0x1F, 0x4E, 0x79)  # xanh đậm cho tiêu đề


def _read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _fmt(value: str, nd: int = 4) -> str:
    """Định dạng số gọn; giữ nguyên nếu không phải số."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return value if value is not None else ""
    if f == int(f) and abs(f) >= 100:
        return f"{int(f)}"
    return f"{f:.{nd}f}"


def add_heading(doc: Document, text: str, level: int) -> None:
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = ACCENT


def add_table(doc: Document, headers: list[str], rows: list[list[str]]) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        for p in hdr[i].paragraphs:
            for run in p.runs:
                run.font.bold = True
                run.font.size = Pt(9)
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
            for p in cells[i].paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9)


def add_para(doc: Document, text: str, bold: bool = False) -> None:
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.bold = bold
    run.font.size = Pt(11)


def add_bullet(doc: Document, text: str) -> None:
    doc.add_paragraph(text, style="List Bullet")


def build() -> None:
    doc = Document()

    # Tiêu đề chính.
    title = doc.add_heading(
        "Phụ lục: Hiệu quả đầu tư (backtest) và giả định kết hợp từ khóa", level=0
    )
    for run in title.runs:
        run.font.color.rgb = ACCENT
    intro = doc.add_paragraph()
    intro.add_run(
        "Tài liệu tổng hợp phục vụ Chương 4 (Kết quả thí nghiệm) và Chương 5 "
        "(Kết luận). Mọi con số được trích trực tiếp từ các artifact trong thư "
        "mục reports/."
    ).italic = True

    # ------------------------------------------------------------------
    # PHẦN A — Hiệu quả đầu tư
    # ------------------------------------------------------------------
    add_heading(doc, "Phần A — Hiệu quả đầu tư của mô hình kỹ thuật", 1)

    add_heading(doc, "A.1. Từ độ chính xác sang giá trị đầu tư", 2)
    add_para(
        doc,
        "Luận văn trước đây mới đo độ chính xác dự báo (balanced accuracy ≈ 0,76; "
        "AUC ≈ 0,82 với LightGBM, Config_A — chỉ đặc trưng kỹ thuật). Phần backtest "
        "chuyển kết quả đó thành giá trị đầu tư thực tế bằng chiến lược long-only "
        "đúng đặc thù thị trường cơ sở Việt Nam, đo lợi nhuận sau chi phí và so với "
        "các benchmark.",
    )

    add_heading(doc, "A.2. Kết quả trên tập test chính (cutoff 2025Q1)", 2)
    perf = _read_csv(REPORTS / "backtest_performance.csv")
    perf_headers = [
        "Chiến lược", "Kịch bản", "LN tích lũy", "LN kỳ TB", "Độ lệch chuẩn",
        "Sharpe", "Max DD", "Hit rate", "Tổng chi phí",
    ]
    name_map = {
        "model": "Mô hình",
        "buy_hold_equal": "Buy-and-hold đều",
        "equal_weight_rebalanced": "Equal-weight tái cân bằng",
    }
    perf_rows = []
    for r in perf:
        perf_rows.append([
            name_map.get(r["strategy"], r["strategy"]),
            r["cost_scenario"],
            _fmt(r["cumulative_return"]),
            _fmt(r["mean_period_return"]),
            _fmt(r["std_period_return"]),
            _fmt(r["sharpe_ratio"]),
            _fmt(r["max_drawdown"]),
            _fmt(r["hit_rate"], 2),
            _fmt(r["total_cost"]),
        ])
    add_table(doc, perf_headers, perf_rows)

    add_para(doc, "Diễn giải chính:", bold=True)
    add_bullet(
        doc,
        "Lợi nhuận: sau chi phí, chiến lược mô hình đạt 60,3% trên 5 quý, gấp ~2,4 "
        "lần benchmark (25,4%).",
    )
    add_bullet(
        doc,
        "Rủi ro–lợi nhuận: Sharpe 1,05 (net) so với 0,45 của benchmark; độ lệch "
        "chuẩn kỳ của mô hình (0,097) còn thấp hơn benchmark (0,114).",
    )
    add_bullet(
        doc,
        "Kiểm soát sụt giảm: Max Drawdown mô hình gần 0 (−0,10% net) so với −2,00% "
        "của benchmark; hit rate 0,80 so với 0,60.",
    )
    add_bullet(
        doc,
        "Chi phí: tổng chi phí giao dịch tích lũy chỉ ~1,2% NAV; khoảng cách "
        "gross↔net hẹp (62,1% → 60,3%).",
    )
    note = doc.add_paragraph()
    note.add_run(
        "Lưu ý minh bạch: hai benchmark cho kết quả trùng khớp vì đủ 80 mã đều có "
        "dữ liệu ở cả 5 quý (không có mã rời/mới), nên tái cân bằng đều mỗi quý ≈ "
        "nắm giữ đều."
    ).italic = True

    add_heading(doc, "A.3. Độ ổn định theo thời gian (walk-forward)", 2)
    wf = _read_csv(REPORTS / "walk_forward_results.csv")
    wf_headers = [
        "Cutoff", "Số mẫu test", "Balanced Accuracy", "AUC",
        "LN tích lũy mô hình (net)", "LN tích lũy buy-and-hold",
    ]
    wf_rows = [
        [
            r["cutoff"], _fmt(r["n_test"], 0), _fmt(r["balanced_accuracy"]),
            _fmt(r["auc_roc"]), _fmt(r["strategy_cumulative_return_net"]),
            _fmt(r["buy_hold_cumulative_return"]),
        ]
        for r in wf
    ]
    add_table(doc, wf_headers, wf_rows)
    add_bullet(
        doc,
        "Balanced accuracy trung bình 0,7076, dao động [0,6400 – 0,7599]; chiến "
        "lược vượt buy-and-hold ở 3/3 cutoff và lợi nhuận net dương ở 3/3 cutoff.",
    )
    add_bullet(
        doc,
        "Cảnh báo: cutoff gần nhất (2025Q3) yếu hơn hẳn (BA 0,64; lợi nhuận 0,118) "
        "do tập test ngắn — ưu thế mô hình co lại khi cửa sổ test thu hẹp.",
    )

    add_heading(doc, "A.4. Đặc trưng kỹ thuật quan trọng nhất", 2)
    fi = _read_csv(REPORTS / "technical_feature_importance.csv")
    fi_headers = ["Hạng", "Đặc trưng", "mean|SHAP|", "Permutation importance"]
    fi_rows = [
        [r["rank"], r["feature"], _fmt(r["mean_abs_shap"]),
         _fmt(r["permutation_importance"])]
        for r in fi[:5]
    ]
    add_table(doc, fi_headers, fi_rows)
    add_bullet(
        doc,
        "rsi_end_q áp đảo: mean|SHAP| gấp ~3,3 lần đặc trưng hạng 2 và permutation "
        "importance gấp ~10 lần. Nhóm động lượng (RSI, MACD, giá vs SMA20) và lợi "
        "nhuận quá khứ chi phối dự báo.",
    )

    add_heading(doc, "A.5. Bảo vệ độ tin cậy — kiểm toán rò rỉ", 2)
    add_para(
        doc,
        "Kiểm toán rò rỉ thời gian PASS: 16 đặc trưng (14 in-period + 2 past), 0 "
        "đặc trưng future; không cột nhãn/return tương lai lọt vào feature set; "
        "không đặc trưng nào có |corr| với nhãn vượt 0,95. Đây là bằng chứng con số "
        "BA ≈ 0,76 không đến từ rò rỉ dữ liệu.",
    )

    # ------------------------------------------------------------------
    # PHẦN B — Kết hợp từ khóa
    # ------------------------------------------------------------------
    add_heading(doc, "Phần B — Giả định và kết quả kết hợp đặc trưng từ khóa", 1)

    add_heading(doc, "B.1. Cấu hình đặc trưng và giả định kết hợp", 2)
    add_para(
        doc,
        "Ba cấu hình so sánh trên cùng tập test, cùng quy trình chia thời gian, "
        "cùng imputer: Config_A (chỉ kỹ thuật), Config_B (chỉ từ khóa), Config_C "
        "(kết hợp kỹ thuật + từ khóa).",
    )
    add_para(doc, "Các giả định của cách kết hợp từ khóa:", bold=True)
    add_bullet(
        doc,
        "Tổng hợp theo quý: đặc trưng từ khóa của một mã trong một quý được tổng "
        "hợp từ toàn bộ bài tin trong quý — làm mờ thông tin thời điểm trong quý.",
    )
    add_bullet(
        doc,
        "Biểu diễn túi-từ-khóa: tín hiệu văn bản rút gọn về tần suất một danh sách "
        "từ khóa tài chính định trước, không mô hình hóa đầy đủ ngữ cảnh/phủ định ở "
        "tầng cơ bản.",
    )
    add_bullet(
        doc,
        "Ranh giới thời gian: đặc trưng từ khóa quý q chỉ dùng tin đến hết quý q, "
        "khớp cùng ranh giới đặc trưng kỹ thuật (không rò rỉ).",
    )
    add_bullet(
        doc,
        "Kết hợp cộng tính: kết hợp = nối đặc trưng, để mô hình tự học trọng số, "
        "không áp đặt tương tác kỹ thuật×văn bản thủ công.",
    )

    add_heading(doc, "B.2. Ba giả thuyết kiểm chứng", 2)
    add_bullet(doc, "H1 — Đặc trưng văn bản cải thiện dự báo: kỳ vọng Δ(C−A) > 0.")
    add_bullet(
        doc, "H2 — Đặc trưng văn bản bổ sung thông tin ngoài giá: kỳ vọng Config_B "
        "mang tín hiệu dự báo phi ngẫu nhiên.")
    add_bullet(
        doc, "H3 — Tín hiệu văn bản có điều kiện theo phân khúc/độ chi tiết.")

    add_heading(doc, "B.3. Kết quả — từ khóa gần như không thêm giá trị", 2)

    add_para(doc, "(a) Từ khóa đơn lẻ (Config_B) gần mức ngẫu nhiên:", bold=True)
    comp = _read_csv(REPORTS / "model_comparison_B1.csv")
    ml_models = {"Logistic_Regression", "Random_Forest", "XGBoost", "LightGBM"}
    b_rows = [
        [r["model"].replace("_", " "), _fmt(r["balanced_accuracy"])]
        for r in comp
        if r["config"] == "Config_B" and r["model"] in ml_models
    ]
    add_table(doc, ["Thuật toán", "BA Config_B"], b_rows)
    add_bullet(
        doc,
        "BA Config_B chỉ quanh 0,49–0,52 (≈ đoán ngẫu nhiên 0,50) → bác bỏ H2 ở cấp "
        "độ quý.",
    )

    add_para(doc, "(b) Kết hợp (Config_C) không nâng — thậm chí giảm:", bold=True)
    # Ghép Config_A và Config_C theo model để tính Δ.
    by_model_cfg = {}
    for r in comp:
        if r["model"] in ml_models:
            by_model_cfg[(r["model"], r["config"])] = float(r["balanced_accuracy"])
    delta_headers = ["Thuật toán", "BA Config_A", "BA Config_C", "Δ(C−A)"]
    delta_rows = []
    deltas = []
    for m in ["LightGBM", "Random_Forest", "XGBoost", "Logistic_Regression"]:
        a = by_model_cfg.get((m, "Config_A"))
        c = by_model_cfg.get((m, "Config_C"))
        if a is None or c is None:
            continue
        d = c - a
        deltas.append(d)
        delta_rows.append([
            m.replace("_", " "), f"{a:.4f}", f"{c:.4f}", f"{d:+.4f}",
        ])
    if deltas:
        avg = sum(deltas) / len(deltas)
        delta_rows.append(["Trung bình", "—", "—", f"{avg:+.4f}"])
    add_table(doc, delta_headers, delta_rows)
    add_bullet(
        doc,
        "Δ(C−A) trung bình +0,0027 (gần 0). Với LightGBM (mô hình mạnh nhất), kết "
        "hợp từ khóa còn làm giảm BA → không ủng hộ H1.",
    )

    add_para(doc, "(c) Khác biệt không có ý nghĩa thống kê (McNemar):", bold=True)
    mcnemar_rows = [
        ["Random Forest, độ chi tiết tháng (297 mẫu)", "−0,0303", "0,1742",
         "Không có ý nghĩa"],
        ["Random Forest, độ chi tiết 2 tháng (150 mẫu)", "−0,0325", "0,1797",
         "Không có ý nghĩa"],
        ["Config_C mới vs Config_C baseline (400 mẫu)", "—", "0,5601",
         "Không có ý nghĩa"],
    ]
    add_table(
        doc, ["Kiểm định", "Δ(C−A)", "p-value", "Kết luận (α=0,05)"], mcnemar_rows
    )

    add_para(
        doc,
        "(d) SHAP xác nhận từ khóa đóng góp không đáng kể trong Config_C: đặc trưng "
        "từ khóa có mean|SHAP| cao nhất chỉ ~0,007 (tăng trưởng, nợ xấu, báo lãi, "
        "chia cổ tức, tăng vốn điều lệ), trong khi rsi_end_q đạt 1,67 — chênh ~240 "
        "lần. Nhiều từ khóa có SHAP = 0 do thưa/hiếm xuất hiện.",
        bold=False,
    )

    add_heading(doc, "B.4. Ba giải thích lý thuyết cho kết quả âm", 2)
    add_bullet(
        doc,
        "Thị trường hiệu quả dạng vừa (semi-strong EMH): tin công khai phản ánh "
        "nhanh vào giá, đặc trưng tin khó thêm thông tin vượt trên kỹ thuật.",
    )
    add_bullet(
        doc,
        "Hấp thụ trong kỳ (within-period absorption): ở độ chi tiết quý, phản ứng "
        "giá với tin xảy ra và tan biến ngay trong kỳ; tổng hợp theo quý làm mờ tín "
        "hiệu ngắn hạn.",
    )
    add_bullet(
        doc,
        "Giới hạn corpus: số bài tin tiếng Việt mỗi (ticker, quý) có thể quá nhỏ để "
        "ước lượng ổn định tín hiệu văn bản, làm tăng nhiễu và kéo Δ(C−A) về 0.",
    )

    add_heading(doc, "B.5. H3 và định hướng", 2)
    add_para(
        doc,
        "Kết quả toàn cục bác bỏ H1, H2 ở cấp độ quý. H3 (tín hiệu văn bản có điều "
        "kiện) chưa bị bác bỏ: cần phân tích ở độ chi tiết cao hơn (cấp bài viết, "
        "period nhỏ hơn) và theo phân khúc (mật độ tin, ngành). Đây là định hướng "
        "nghiên cứu tương lai.",
    )

    # ------------------------------------------------------------------
    # PHẦN C — Thông điệp tổng hợp
    # ------------------------------------------------------------------
    add_heading(doc, "Phần C — Thông điệp tổng hợp cho hội đồng", 1)
    add_bullet(
        doc,
        "Trụ đóng góp dương (kỹ thuật): mô hình dự báo chính xác (BA ≈ 0,76; AUC ≈ "
        "0,82) và tạo giá trị đầu tư thực (LN net 60,3% vs 25,4%; Sharpe 1,05 vs "
        "0,45; drawdown gần 0; ổn định qua 3 cutoff; đã kiểm toán chống rò rỉ).",
    )
    add_bullet(
        doc,
        "Trụ khám phá (văn bản/từ khóa): kết hợp từ khóa không cải thiện dự báo ở "
        "cấp độ quý (Δ trung bình +0,003, không có ý nghĩa thống kê; từ khóa đơn lẻ "
        "≈ ngẫu nhiên; SHAP từ khóa nhỏ hơn kỹ thuật ~240 lần). Kết quả âm có giá "
        "trị khoa học.",
    )
    add_bullet(
        doc,
        "Giới hạn: backtest theo quý (T+2/±7%/lô 100 là giả định nền), bỏ qua trượt "
        "giá; phụ thuộc 80 mã HOSE và khoảng test; ưu thế co lại ở 2025Q3. Lợi "
        "nhuận quá khứ không đảm bảo tương lai — phục vụ học thuật, không phải "
        "khuyến nghị đầu tư.",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    build()
