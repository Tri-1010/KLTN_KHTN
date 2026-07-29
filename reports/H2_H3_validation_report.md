# Báo cáo Kiểm định H2 và H3

_Cập nhật lần cuối: 2026-06-30 — tích hợp kết quả HOSE-80 (80 cổ phiếu, 1.348 mẫu)_

---

## 1. Bối cảnh và Tiền đề

### 1.1 Kết luận H1 (tiền đề đã chốt)

> **H1 KHÔNG được ủng hộ** — Đã được kiểm chứng triệt để qua nhiều ngưỡng thời gian, 4 đơn vị thời gian, 5 lần mở rộng corpus (9.7k → 28k bài), 6 nguồn cân bằng và cải tiến cách đếm từ (phủ định + đồng nghĩa). Đây là kết luận đã chốt, KHÔNG làm lại trong spec này.

Mặc dù H1 không được ủng hộ, đây không phải là thất bại của đề tài. Đề cương đã xác định từ đầu rằng kết quả âm là kết quả hợp lệ và có ý nghĩa khoa học.

### 1.2 Giới thiệu H2 và H3

**Giả thuyết H2:** *Một số từ khóa/cụm từ khóa tài chính có thể có mối liên hệ thống kê với xu hướng tăng/giảm của giá cổ phiếu trong kỳ dự báo tiếp theo.*

Phương pháp kiểm định: chi-square/Fisher exact test, Mann-Whitney U test, logistic regression đơn biến — tất cả áp dụng hiệu chỉnh đa kiểm định Benjamini-Hochberg (BH-FDR).

**Giả thuyết H3:** *Các phương pháp giải thích mô hình có thể hỗ trợ xác định nhóm từ khóa/cụm từ khóa có mức đóng góp đáng kể trong mô hình dự báo.*

Phương pháp kiểm định: SHAP values + permutation importance bắt buộc trên Random_Forest Config_C.

---

## 2. Góc 1 — Kiểm định H2: Mối liên hệ thống kê từng từ khóa

### 2.1 Phương pháp

- **Chi-square / Fisher exact test:** kiểm tra tính độc lập giữa sự xuất hiện từ khóa (nhị phân) và nhãn xu hướng. Khi ô kỳ vọng < 5 → dùng Fisher exact.
- **Mann-Whitney U test:** so sánh phân phối tần suất từ khóa chuẩn hóa giữa nhóm "tăng" và "không tăng".
- **Logistic regression đơn biến:** ước lượng hệ số và khoảng tin cậy 95%.
- **Hiệu chỉnh BH-FDR:** áp dụng riêng biệt cho mỗi loại kiểm định.
- Phân tích in-sample (toàn bộ dữ liệu), không kết luận về khả năng dự báo out-of-sample.
- Thực nghiệm được lặp lại trên **ba cấu hình dataset** để đánh giá robustness.

### 2.2 Các thực nghiệm và kết quả

#### Thực nghiệm 1 — VN30, đơn vị quý (baseline)

| Chỉ số | Giá trị |
|---|---|
| Dataset | 30 tickers × ~17 quý = **510 rows** |
| Từ khóa kiểm định | 62 / 106 |
| Significant sau BH-FDR (bất kỳ test) | **0 / 62** |

Top 5 raw p-value thấp nhất:

| Từ khóa | Hướng | chi p-raw | mw p-raw |
|---|---|---|---|
| chia cổ tức | positive | 0.0043 | 0.0035 |
| nợ xấu | negative | 0.0242 | 0.0167 |
| hợp tác chiến lược | positive | 0.0201 | 0.0186 |
| mua lại cổ phiếu | positive | 0.0598 | 0.0312 |
| đóng cửa | negative | 0.0682 | 0.0338 |

#### Thực nghiệm 2 — VN30, đơn vị tháng (sensitivity test)

| Chỉ số | Giá trị |
|---|---|
| Dataset | 30 tickers × ~53 tháng = **1.541 rows** |
| Từ khóa kiểm định | 64 / 106 |
| Significant sau BH-FDR | **0 / 64** |
| chi p-raw < 0.05 | 0 / 64 (vs 3/62 ở quý) |

Kết quả: đơn vị tháng **không cải thiện** tín hiệu, thậm chí yếu hơn quý. Nhất quán với chu kỳ công bố tài chính theo quý.

#### Thực nghiệm 3 — HOSE-80, đơn vị quý (mở rộng chính)

Dataset mở rộng từ VN30 (30 tickers) lên **HOSE-80 (80 tickers)** theo tiêu chí:
- HOSE only; vốn hóa ≥ 2.000 tỷ VND; GTGD bình quân ≥ 50 tỷ VND/ngày; niêm yết từ trước 2022.
- Thêm 50 tickers từ 8 ngành: ngân hàng tầm trung, chứng khoán, bất động sản, công nghiệp, năng lượng, tiêu dùng, công nghệ, vận tải.

| Chỉ số | VN30 | HOSE-80 | Thay đổi |
|---|---|---|---|
| Tickers | 30 | **80** | +167% |
| Rows (ticker × quý) | 510 | **1.348** | +164% |
| Từ khóa kiểm định | 62 | **71** | +9 từ khóa |
| Từ khóa bị loại (zero) | 44 | **35** | −9 từ khóa |
| Significant sau BH-FDR | **0** | **0** | Không đổi |

Top 5 raw p-value thấp nhất trên HOSE-80:

| Từ khóa | Hướng | chi p-raw | chi p-adj | mw p-raw |
|---|---|---|---|---|
| chia cổ tức | positive | 0.0089 | 0.333 | 0.0076 |
| giảm mạnh | negative | 0.0094 | 0.333 | 0.0056 |
| nợ xấu | negative | 0.0448 | 0.862 | 0.0337 |
| đại hội cổ đông | neutral | 0.0486 | 0.862 | 0.0339 |
| không chia cổ tức | negative | 0.0670 | 0.951 | 0.0551 |

### 2.3 So sánh tổng hợp ba thực nghiệm

| Thực nghiệm | Rows | KW tested | chi p<0.05 (raw) | Significant (BH) |
|---|---|---|---|---|
| VN30 — quý | 510 | 62 | 3 | 0 |
| VN30 — tháng | 1.541 | 64 | 0 | 0 |
| HOSE-80 — quý | 1.348 | 71 | **5** | **0** |

### 2.4 Kết luận H2

**H2 KHÔNG được ủng hộ** ở cả ba thực nghiệm sau hiệu chỉnh BH-FDR.

Tuy nhiên, tín hiệu raw trước BH có tính nhất quán đáng chú ý: **chia cổ tức** và **nợ xấu** luôn xuất hiện trong top 3 raw p-value thấp nhất ở cả VN30 lẫn HOSE-80. Điều này gợi ý hai từ khóa này có tín hiệu tiềm năng nhưng chưa đủ mạnh để vượt ngưỡng sau khi hiệu chỉnh cho 62–71 kiểm định đồng thời.

Kết quả không thay đổi khi tăng dataset 2.6 lần (510 → 1.348 rows) cho thấy đây là kết luận **robust**: tín hiệu thực sự yếu, không phải do thiếu dữ liệu.

---

## 3. Góc 2 — Phân rã thước đo: Recall lớp "tăng"

### 3.1 Phương pháp

- So sánh Config_A (chỉ kỹ thuật) vs Config_C (kỹ thuật + từ khóa) trên 4 thuật toán ML.
- Time_Series_Split (cutoff 2025Q1), tái sử dụng `pipeline.task10_train`.
- Tính Precision, Recall, F1 theo từng lớp + AUC + Balanced Accuracy.
- Thêm hàng delta = Config_C − Config_A.

### 3.2 Kết quả (VN30 baseline, đơn vị quý)

**Delta Config_C − Config_A:**

| Model | Δ recall_class1 | Δ precision_class1 | Δ f1_class1 | Δ bal_acc |
|---|---|---|---|---|
| Logistic Regression | +0.013 | −0.044 | −0.010 | −0.022 |
| Random Forest | **+0.076** | −0.058 | +0.014 | −0.011 |
| XGBoost | +0.051 | −0.044 | +0.011 | −0.010 |
| LightGBM | +0.025 | −0.036 | −0.002 | −0.016 |

### 3.3 Nhận xét

Tất cả 4 thuật toán cho thấy **pattern đánh đổi nhất quán**: từ khóa tăng recall lớp "tăng" (+1.3% đến +7.6%) nhưng giảm precision (−3.6% đến −5.8%). Balanced accuracy tổng thể giảm nhẹ ở cả 4.

Đây là "giá trị bổ sung có điều kiện": từ khóa giúp mô hình nhận diện được nhiều trường hợp tăng giá hơn, nhưng đổi lại tăng tỷ lệ báo động giả. Trong ứng dụng thực tế, lựa chọn Config_A hay Config_C phụ thuộc vào ngưỡng chấp nhận rủi ro.

---

## 4. Góc 3 — Đóng góp từ khóa theo mật độ tin

### 4.1 Phương pháp

- Phân chia tập test thành nhóm tin dày (`has_min_news = 1`, `news_count ≥ 5`) và tin thưa.
- Huấn luyện Config_A và Config_C trên toàn tập train; đánh giá riêng từng nhóm.
- Nhóm < 20 mẫu hoặc 1 lớp nhãn → đánh dấu "not reliable".

### 4.2 Kết quả

**Delta Config_C − Config_A theo mật độ tin:**

| Model | Nhóm | Δ bal_acc | Δ recall_1 | n | Đáng tin |
|---|---|---|---|---|---|
| Random Forest | dense | −0.010 | **+0.078** | 148 | ✓ |
| Logistic Regression | dense | −0.022 | +0.013 | 148 | ✓ |
| XGBoost | dense | −0.009 | +0.052 | 148 | ✓ |
| LightGBM | dense | −0.015 | +0.026 | 148 | ✓ |
| Tất cả | sparse | ±0.000 | ±0.000 | 2 | ✗ |

**Cảnh báo:** Nhóm "sparse" chỉ có 2 mẫu — không đáng tin cậy, không thể kết luận.

### 4.3 Nhận xét

Pattern delta trong nhóm tin dày nhất quán với Góc 2. Không thể kiểm tra giả thuyết "mật độ tin là yếu tố thể hiện" do nhóm sparse quá nhỏ trong tập test.

---

## 5. Góc 4 — Kiểm định H3: Từ khóa đóng góp trong Config_C (SHAP)

### 5.1 Phương pháp

- Huấn luyện bắt buộc Random_Forest trên Config_C (không phụ thuộc best model toàn cục).
- SHAP values (TreeExplainer) + permutation importance (Balanced Accuracy, n=10).
- Xếp hạng từ khóa theo mean(|SHAP|); kiểm tra tính nhất quán hướng.

### 5.2 Kết quả

- Tổng đặc trưng từ khóa xếp hạng: **318**
- Nhất quán về hướng (direction_consistent): **80 / 318** (25.2%)
- Tỷ lệ đóng góp: **kỹ thuật ~68.1%, từ khóa ~31.9%**

**Top 10 từ khóa theo mean|SHAP|:**

| Từ khóa | Hướng | mean\|SHAP\| | Nhất quán hướng |
|---|---|---|---|
| tăng trưởng | positive | 0.00685 | ✓ |
| nợ xấu | negative | 0.00659 | ✗ |
| tăng trưởng | positive | 0.00637 | ✓ |
| nợ xấu | negative | 0.00580 | ✗ |
| báo lãi | positive | 0.00359 | ✓ |
| chia cổ tức | positive | 0.00357 | ✓ |
| nợ xấu | negative | 0.00332 | ✓ |
| tăng vốn điều lệ | positive | 0.00305 | ✓ |
| tăng trưởng | positive | 0.00276 | ✓ |
| chia cổ tức | positive | 0.00266 | ✓ |

### 5.3 Kết luận H3

**H3 ĐƯỢC ỦNG HỘ MỘT PHẦN.**

Từ khóa chiếm ~32% SHAP importance trong Config_C. Các từ khóa top — **tăng trưởng, chia cổ tức, báo lãi** — có ý nghĩa tài chính rõ ràng. Tuy nhiên chỉ 25% direction_consistent cho thấy mô hình sử dụng từ khóa theo pattern phức tạp hơn hướng gán nhãn đơn giản — có thể phản ánh ngữ cảnh (ví dụ "tăng trưởng" xuất hiện cả trong tin tích cực lẫn phân tích rủi ro).

---

## 6. Kết luận tổng hợp

| Giả thuyết | Kết quả |
|---|---|
| H1 (tiền đề, đã chốt) | **Không được ủng hộ** |
| H2 — VN30/quý (510 rows) | Không ủng hộ; 3/62 raw p<0.05 |
| H2 — VN30/tháng (1.541 rows) | Không ủng hộ; 0/64 raw p<0.05 |
| H2 — HOSE-80/quý (1.348 rows) | **Không ủng hộ; 5/71 raw p<0.05** |
| H3 — SHAP Config_C | **Được ủng hộ một phần** (~32% SHAP) |
| Góc 2 — Đánh đổi recall/precision | Pattern nhất quán qua 4 thuật toán |
| Góc 3 — Mật độ tin | Nhóm sparse không đủ mẫu |

### Ý nghĩa đối với luận văn

1. **Bằng chứng âm có hệ thống và robust:** H2 được kiểm định trên 3 cấu hình dataset khác nhau (30→80 tickers, quý→tháng), kết quả nhất quán. Đây là bằng chứng khoa học thuyết phục, không phải thất bại.

2. **Tín hiệu tiềm năng chưa đủ mạnh:** "chia cổ tức" và "nợ xấu" liên tục xuất hiện trong top raw p-value nhưng không vượt ngưỡng BH-FDR. Điều này gợi ý hướng nghiên cứu tương lai: kiểm định riêng biệt cho hai từ khóa này với dataset lớn hơn hoặc phương pháp khác.

3. **H3 ủng hộ một phần:** Từ khóa được mô hình sử dụng (~32% SHAP) nhưng không đủ để cải thiện balanced accuracy tổng thể (H1). Điều này gợi ý rằng tín hiệu từ khóa bị nhiễu hoặc không ổn định theo thời gian.

4. **Giá trị bổ sung có điều kiện:** Config_C tăng recall lớp "tăng" (+7.6% với Random Forest) nhưng đánh đổi precision. Kết quả này có ứng dụng thực tế cho chiến lược đầu tư chấp nhận rủi ro cao.

---

## 7. Giả định và Giới hạn

### Góc 1 (Kiểm định H2)
- **In-sample analysis:** Kết quả phản ánh mối liên hệ *đã quan sát*, không kết luận về dự báo out-of-sample.
- **BH-FDR:** Ít bảo thủ hơn Bonferroni, phù hợp với nghiên cứu khám phá. Tuy nhiên với 71 kiểm định đồng thời, ngưỡng effective thấp (~0.001 cho raw p).
- **Corpus thiếu từ khóa tiêu cực:** 35/106 từ khóa bị loại do zero occurrences — chủ yếu là từ khóa tiêu cực phức tạp. Corpus báo tài chính Việt Nam có xu hướng đưa tin tích cực nhiều hơn.

### Góc 2 (Phân rã thước đo)
- Một time_series_split duy nhất (cutoff 2025Q1); không cross-validated.

### Góc 3 (Mật độ tin)
- Nhóm sparse trong tập test chỉ có 2 mẫu — không thể kết luận.
- Ngưỡng `has_min_news` (≥5 bài/quý) là tùy ý.

### Góc 4 (SHAP Config_C)
- Chỉ Random_Forest; kết quả phụ thuộc loại mô hình.
- SHAP là post-hoc explanation, không chứng minh nhân quả.

---

## 8. Tệp kết quả

| Góc | Tệp | Mô tả |
|---|---|---|
| Góc 1 (quý, HOSE-80) | `reports/keyword_significance.csv` | Kiểm định H2 — 1.348 rows |
| Góc 1 (tháng) | `reports/keyword_significance_monthly.csv` | Kiểm định H2 — 1.541 rows |
| Góc 2 | `reports/metrics_breakdown.csv` | Precision/Recall/F1/AUC + delta |
| Góc 3 | `reports/news_density_analysis.csv` | Delta theo mật độ tin |
| Góc 4 | `reports/shap_configc_keyword_ranking.csv` | Xếp hạng từ khóa theo SHAP |
| Góc 4 | `reports/configc_shap_summary.png` | Beeswarm SHAP — Config_C |
| Góc 4 | `reports/configc_permutation_importance.png` | Permutation importance — Config_C |
| So sánh đơn vị | `reports/period_experiment.csv` | H1 theo 4 đơn vị thời gian |
| Tiêu chí cổ phiếu | `docs/stock_selection_criteria.md` | Tiêu chí mở rộng HOSE-80 |
