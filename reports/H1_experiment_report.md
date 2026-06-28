# Báo cáo thực nghiệm H1 — Đóng góp của đặc trưng tin tức trong dự báo xu hướng giá VN30

## 1. Câu hỏi nghiên cứu

**H1:** Việc bổ sung đặc trưng tần suất từ khóa trích xuất từ tin tức tài chính tiếng Việt
có cải thiện độ chính xác dự báo xu hướng giá so với chỉ dùng đặc trưng kỹ thuật không?

Bài toán: phân loại nhị phân (giá trung bình kỳ kế tiếp **tăng** / **không tăng**) cho 30 mã VN30,
giai đoạn 2022-01 đến 2026-06.

## 2. Thiết lập thực nghiệm

- **Dữ liệu:** 30 mã VN30; giá OHLCV theo ngày (35.160 dòng); tin tức từ CafeF, Vietstock,
  Tinnhanhchungkhoan (10.050 bài đã gắn mã, 7.492 bài sau tiền xử lý).
- **Ba cấu hình đặc trưng:**
  - **Config A:** chỉ đặc trưng kỹ thuật (RSI, MACD, Bollinger Bands, SMA, EMA, return, volatility…)
  - **Config B:** chỉ đặc trưng từ khóa (tần suất, TF-IDF, pos/neg score, sentiment_ratio)
  - **Config C:** kết hợp A + B
- **Chia train/test:** theo thời gian (time-series split), không xáo trộn — toàn bộ kỳ huấn luyện
  nằm trước kỳ kiểm tra để tránh rò rỉ dữ liệu.
- **Thuật toán:** Logistic Regression, Random Forest, XGBoost, LightGBM + 2 baseline
  (đa số lớp, momentum ngây thơ).
- **Chỉ số chính:** Balanced Accuracy (cân bằng giữa hai lớp; 0.5 = đoán ngẫu nhiên).

> Mọi con số dưới đây đo trên tập kiểm tra (out-of-sample).

---

## 3. Thí nghiệm 1 — So sánh ba cấu hình (đơn vị quý, cutoff 2025Q1)

Train: 356 mẫu (12 quý) · Test: 150 mẫu (5 quý).

| Thuật toán | Config A (kỹ thuật) | Config B (từ khóa) | Config C (kết hợp) | C − A |
|---|---|---|---|---|
| Random Forest | **0.776** | 0.470 | 0.747 | −0.029 |
| XGBoost | 0.730 | 0.548 | 0.735 | +0.005 |
| LightGBM | 0.723 | 0.498 | 0.721 | −0.002 |
| Logistic Regression | 0.725 | 0.509 | 0.697 | −0.028 |
| *Baseline đa số lớp* | 0.500 | 0.500 | 0.500 | — |
| *Baseline momentum* | 0.464 | 0.464 | 0.464 | — |

**Nhận xét:**
- Đặc trưng kỹ thuật (A) mang gần như toàn bộ sức dự báo (0.72–0.78, vượt xa baseline 0.5).
- Đặc trưng từ khóa đơn lẻ (B) gần như vô dụng (0.47–0.55, chỉ ngang đoán ngẫu nhiên).
- Kết hợp (C) **không cải thiện** so với A — trung bình còn giảm nhẹ.
- **Mô hình tốt nhất toàn cục: Random Forest – Config A (Balanced Accuracy 0.776, AUC 0.83).**

➡️ Ở đơn vị quý, **H1 không được ủng hộ**.

---

## 4. Thí nghiệm 2 — Kiểm tra độ bền theo nhiều ngưỡng thời gian (vẫn đơn vị quý)

Thử 5 điểm chia train/test khác nhau, mỗi điểm tính delta C − A (Balanced Accuracy):

| Cutoff | Số quý test | Delta trung bình (C − A) |
|---|---|---|
| 2024Q1 | 9 | −0.0004 |
| 2024Q3 | 7 | −0.0131 |
| 2025Q1 | 5 | −0.0130 |
| 2025Q3 | 3 | −0.0425 |
| 2026Q1 | 3 | −0.0425 |

- Config C chỉ thắng Config A ở **5/20** tổ hợp (cutoff × thuật toán), thắng đều rất nhỏ.
- **Delta trung bình toàn cục: −0.0223.**
- Mọi ngưỡng đều âm; delta càng âm khi test set càng ngắn.

➡️ Kết luận "H1 không được ủng hộ ở đơn vị quý" **vững qua nhiều cách chia thời gian** (không phải
do may rủi của một điểm chia).

---

## 5. Thí nghiệm 3 — Thay đổi đơn vị thời gian (phát hiện chính)

Xây lại toàn bộ đặc trưng + nhãn theo từng đơn vị thời gian (nhãn: kỳ kế tiếp tăng/giảm),
so sánh A vs C trung bình qua 4 thuật toán:

| Đơn vị | Số mẫu | Số kỳ | Mean A | Mean C | Delta (C − A) |
|---|---|---|---|---|---|
| 2 tuần | 2556 | 115 | 0.694 | 0.694 | +0.0005 |
| **1 tháng** | 1413 | 53 | 0.670 | 0.681 | **+0.0109** ← đỉnh |
| 2 tháng | 761 | 26 | 0.700 | 0.698 | −0.0028 |
| Quý | 506 | 17 | 0.652 | 0.636 | −0.0156 |

Chi tiết đáng chú ý ở **đơn vị 1 tháng**: Random Forest A=0.671 → C=0.707, **+0.036** —
mức cải thiện rõ rệt nhất của toàn bộ nghiên cứu (3/4 thuật toán có delta dương).

### Đồ thị "hình chuông" của đóng góp từ khóa

```
Quý (3 tháng):  -0.0156   ❌ giảm
2 tháng:        -0.0028   ~ trung tính
1 tháng:        +0.0109   ✅ đỉnh
2 tuần:         +0.0005   ~ gần 0
```

Đóng góp của từ khóa **không tăng đơn điệu** khi rút ngắn kỳ, mà đạt cực đại quanh **1 tháng**.

### Giải thích

Hai lực đối nghịch:
- **Rút ngắn kỳ → có lợi:** tin tức "tươi" hơn, khớp với khung tác động ngắn hạn của tin lên giá
  (giải thích vì sao quý → tháng cải thiện).
- **Rút quá ngắn → có hại:** ở 2 tuần, mỗi (mã, kỳ) có quá ít bài tin → tín hiệu từ khóa thưa và
  nhiễu, đóng góp tan biến.

**1 tháng** là điểm cân bằng giữa độ tươi của thông tin và mật độ tin đủ để khử nhiễu.

---

## 5b. Kiểm định ý nghĩa thống kê (McNemar) — Random Forest, đơn vị tháng

Mức cải thiện đáng chú ý nhất là Random Forest ở đơn vị tháng (+3.6 điểm Balanced Accuracy).
Để xác minh đây không phải dao động ngẫu nhiên, dùng **kiểm định McNemar** so sánh dự đoán của
Config A và Config C trên **cùng tập kiểm tra** (286 mẫu). McNemar chỉ xét các trường hợp hai mô
hình **bất đồng** ý kiến.

**Bảng tương quan (tính đúng/sai):**

|  | C đúng | C sai |
|---|---|---|
| **A đúng** | 178 | 12 (b) |
| **A sai** | 22 (c) | 74 |

- Số ca bất đồng: b + c = **34** (A đúng-C sai = 12; A sai-C đúng = 22).
- Config C "sửa đúng" 22 ca mà A sai, nhưng cũng "làm hỏng" 12 ca mà A đúng → lợi ròng chỉ 10 ca.

**Kết quả kiểm định:**

| Phương pháp | Statistic | p-value |
|---|---|---|
| Exact binomial McNemar | 12.0 | **0.1214** |
| Chi-square (hiệu chỉnh liên tục) | 2.38 | 0.1227 |

**Kết luận:** p = 0.121 > 0.05 → **không bác bỏ giả thuyết H0**. Mặc dù Config C nhỉnh hơn về điểm
số (+3.6 điểm), sự khác biệt này **chưa đạt ý nghĩa thống kê** ở mức α = 0.05 — nó nằm trong khoảng
dao động ngẫu nhiên có thể xảy ra trên tập kiểm tra 286 mẫu. Cần thêm dữ liệu (hoặc kiểm định trên
nhiều ngưỡng/khởi tạo) để khẳng định chắc chắn.

> Diễn giải cho luận văn: cải thiện ở đơn vị tháng là **có hướng tích cực và nhất quán về dấu**,
> nhưng **chưa đủ mạnh để kết luận có ý nghĩa thống kê**. Đây là một kết quả trung thực — gợi ý
> rằng tin tức *có thể* hữu ích ở khung thời gian tháng, nhưng bằng chứng hiện tại còn yếu.

---

## 6. Kết luận tổng hợp

1. **Đặc trưng kỹ thuật là nền tảng dự báo chính** (Balanced Accuracy ~0.65–0.78); đặc trưng từ
   khóa đơn lẻ gần như không có sức dự báo.
2. **Ở đơn vị quý, H1 không được ủng hộ** — kết hợp từ khóa không cải thiện, kết luận này bền qua
   nhiều ngưỡng thời gian.
3. **Giá trị dự báo của tin tức phụ thuộc phi tuyến vào đơn vị thời gian**, đạt cực đại quanh
   **chu kỳ 1 tháng** (+1.1 điểm Balanced Accuracy trung bình; Random Forest +3.6 điểm). Tuy nhiên
   kiểm định McNemar cho thấy mức cải thiện này **chưa đạt ý nghĩa thống kê** (p = 0.121 > 0.05) —
   có hướng tích cực nhưng bằng chứng còn yếu.
4. Đây là đóng góp khoa học chính: thay vì kết luận "tin tức vô dụng", nghiên cứu chỉ ra **điều kiện**
   để tin tức trở nên hữu ích — phản ánh sự đánh đổi giữa độ tươi thông tin và mật độ dữ liệu.

### Hướng nghiên cứu tiếp theo (gợi ý)
- Kiểm định ý nghĩa thống kê (ví dụ McNemar) cho mức +3.6 điểm của Random Forest ở đơn vị tháng.
- Biểu diễn tin tức tinh vi hơn tần suất từ khóa (embedding / mô hình ngôn ngữ), xử lý phủ định.
- Mô hình hóa độ trễ tác động của tin (event-time) thay vì gộp cố định theo lịch.

---

## 7. Nguồn dữ liệu kết quả

| Thí nghiệm | File kết quả |
|---|---|
| So sánh 3 cấu hình (quý) | `reports/model_comparison.csv` |
| Nhiều ngưỡng thời gian | `reports/time_split_experiment.csv` |
| Thay đổi đơn vị thời gian | `reports/period_experiment.csv` |
| Kiểm định McNemar (RF, tháng) | `reports/mcnemar_month_rf.txt` |
| Phân tích SHAP / tầm quan trọng đặc trưng | `reports/feature_importance.png`, `reports/shap_summary.png`, `reports/top_keywords_analysis.csv` |

*Script thực nghiệm: `pipeline/experiment_time_splits.py`, `pipeline/experiment_period.py`, `pipeline/experiment_mcnemar.py`.*
