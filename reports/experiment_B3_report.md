# Báo cáo so sánh thí nghiệm B3 với Baseline_v0

Thí nghiệm **B3** phân tích giá trị dự báo của đặc trưng văn bản theo từng **phân khúc** (ngành và nhóm vốn hóa large_cap/mid_cap), đối chiếu với kết quả toàn cục đã đóng băng trong **Baseline_v0**. Trọng tâm là kiểm tra tín hiệu văn bản **có điều kiện** (H3) và nhấn mạnh **statistical power** của từng phân khúc (số mẫu n mỗi nhóm).

## 1. Δ(C−A) theo phân khúc cạnh Δ(C−A) tổng hợp Baseline_v0

Với mỗi phân khúc (ngành và nhóm vốn hóa), balanced accuracy được huấn luyện lại trên riêng phân khúc theo cùng pipeline/time-split của v0. Cột **Δ(C−A) v0** là chênh lệch toàn cục của Baseline_v0 để đối chiếu. Số mẫu (`n_samples`) và số ticker (`n_tickers`) được nêu nổi bật để nhấn mạnh **statistical power** của từng phân khúc (Req 13.1).


### sector: Banking — n_samples=425, n_tickers=25

| Model | BA A (seg) | BA C (seg) | Δ(C−A) seg | Δ(C−A) v0 |
|---|---|---|---|---|
| LightGBM | 0.6723 | 0.6476 | -0.0247 | -0.0231 |
| Random Forest | 0.7359 | 0.6307 | -0.1052 | -0.0187 |
| XGBoost | 0.6482 | 0.6158 | -0.0324 | -0.0033 |
| Logistic Regression | 0.6480 | 0.6313 | -0.0166 | -0.0303 |

### sector: Consumer — n_samples=170, n_tickers=10

| Model | BA A (seg) | BA C (seg) | Δ(C−A) seg | Δ(C−A) v0 |
|---|---|---|---|---|
| LightGBM | 0.7800 | 0.7200 | -0.0600 | -0.0231 |
| Random Forest | 0.7800 | 0.7800 | +0.0000 | -0.0187 |
| XGBoost | 0.7800 | 0.7200 | -0.0600 | -0.0033 |
| Logistic Regression | 0.8200 | 0.7800 | -0.0400 | -0.0303 |

### sector: Energy — n_samples=131, n_tickers=8

| Model | BA A (seg) | BA C (seg) | Δ(C−A) seg | Δ(C−A) v0 |
|---|---|---|---|---|
| LightGBM | 0.8000 | 0.7750 | -0.0250 | -0.0231 |
| Random Forest | 0.8000 | 0.7500 | -0.0500 | -0.0187 |
| XGBoost | 0.7750 | 0.7750 | +0.0000 | -0.0033 |
| Logistic Regression | 0.7750 | 0.7500 | -0.0250 | -0.0303 |

### sector: Industrial — n_samples=168, n_tickers=10

| Model | BA A (seg) | BA C (seg) | Δ(C−A) seg | Δ(C−A) v0 |
|---|---|---|---|---|
| LightGBM | 0.6913 | 0.7085 | +0.0172 | -0.0231 |
| Random Forest | 0.7800 | 0.5920 | -0.1880 | -0.0187 |
| XGBoost | 0.7258 | 0.7085 | -0.0172 | -0.0033 |
| Logistic Regression | 0.8054 | 0.6544 | -0.1511 | -0.0303 |

### sector: RealEstate — n_samples=220, n_tickers=13

| Model | BA A (seg) | BA C (seg) | Δ(C−A) seg | Δ(C−A) v0 |
|---|---|---|---|---|
| LightGBM | 0.7799 | 0.7623 | -0.0176 | -0.0231 |
| Random Forest | 0.7827 | 0.8283 | +0.0455 | -0.0187 |
| XGBoost | 0.7799 | 0.7476 | -0.0323 | -0.0033 |
| Logistic Regression | 0.6461 | 0.6755 | +0.0294 | -0.0303 |

### sector: Securities — n_samples=101, n_tickers=6

| Model | BA A (seg) | BA C (seg) | Δ(C−A) seg | Δ(C−A) v0 |
|---|---|---|---|---|
| LightGBM | 0.6250 | 0.6000 | -0.0250 | -0.0231 |
| Random Forest | 0.6750 | 0.6000 | -0.0750 | -0.0187 |
| XGBoost | 0.6250 | 0.6000 | -0.0250 | -0.0033 |
| Logistic Regression | 0.7250 | 0.7500 | +0.0250 | -0.0303 |

### sector: Technology — n_samples=51, n_tickers=3

| Model | BA A (seg) | BA C (seg) | Δ(C−A) seg | Δ(C−A) v0 |
|---|---|---|---|---|
| LightGBM | 0.5000 | 0.5000 | +0.0000 | -0.0231 |
| Random Forest | 0.8333 | 0.5833 | -0.2500 | -0.0187 |
| XGBoost | 0.8750 | 0.8750 | +0.0000 | -0.0033 |
| Logistic Regression | 0.7917 | 0.9583 | +0.1667 | -0.0303 |

### sector: Transport — n_samples=82, n_tickers=5

| Model | BA A (seg) | BA C (seg) | Δ(C−A) seg | Δ(C−A) v0 |
|---|---|---|---|---|
| LightGBM | 0.5584 | 0.4870 | -0.0714 | -0.0231 |
| Random Forest | 0.5942 | 0.6396 | +0.0455 | -0.0187 |
| XGBoost | 0.5390 | 0.6753 | +0.1364 | -0.0033 |
| Logistic Regression | 0.6136 | 0.6688 | +0.0552 | -0.0303 |

### cap_group: large_cap — n_samples=510, n_tickers=30

| Model | BA A (seg) | BA C (seg) | Δ(C−A) seg | Δ(C−A) v0 |
|---|---|---|---|---|
| LightGBM | 0.7235 | 0.7305 | +0.0070 | -0.0231 |
| Random Forest | 0.7636 | 0.7220 | -0.0416 | -0.0187 |
| XGBoost | 0.7249 | 0.7150 | -0.0099 | -0.0033 |
| Logistic Regression | 0.7249 | 0.6826 | -0.0423 | -0.0303 |

### cap_group: mid_cap — n_samples=838, n_tickers=50

| Model | BA A (seg) | BA C (seg) | Δ(C−A) seg | Δ(C−A) v0 |
|---|---|---|---|---|
| LightGBM | 0.7147 | 0.7210 | +0.0063 | -0.0231 |
| Random Forest | 0.7300 | 0.6707 | -0.0594 | -0.0187 |
| XGBoost | 0.7246 | 0.7318 | +0.0072 | -0.0033 |
| Logistic Regression | 0.7048 | 0.6760 | -0.0288 | -0.0303 |

### Kích thước tập test theo phân khúc (statistical power)

Số mẫu (ticker × quý) rơi vào tập test (quý ≥ cutoff 2025Q1) theo cùng quy tắc chia
thời gian của pipeline. Cột `n_test` là cơ sở đánh giá độ tin cậy của Δ(C−A): n_test
càng nhỏ, Δ(C−A) càng dễ dao động do phương sai lấy mẫu.

| Phân khúc | n_tickers | n_train | n_test | Ghi chú power |
|---|---|---|---|---|
| cap_group: mid_cap | 50 | 588 | **250** | Cao — đáng tin |
| cap_group: large_cap | 30 | 360 | **150** | Cao — đáng tin |
| sector: Banking | 25 | 300 | 125 | Khá |
| sector: RealEstate | 13 | 155 | 65 | Trung bình |
| sector: Consumer | 10 | 120 | 50 | Thấp |
| sector: Industrial | 10 | 118 | 50 | Thấp |
| sector: Energy | 8 | 91 | 40 | Thấp |
| sector: Securities | 6 | 71 | 30 | Rất thấp |
| sector: Transport | 5 | 57 | **25** | Rất thấp — Δ không tin cậy |
| sector: Technology | 3 | 36 | **15** | Cực thấp — Δ không tin cậy |

**Nhận xét:** Hai phân khúc "dương" (Transport n_test=25, Technology n_test=15) là hai
phân khúc có tập test **nhỏ nhất**. Với 15–25 mẫu, chỉ cần dự đoán đúng/sai khác đi 1–2
mẫu là Δ(C−A) thay đổi vài điểm phần trăm. Ngược lại, hai phân khúc đáng tin nhất
(mid_cap n_test=250, large_cap n_test=150) đều cho Δ(C−A) âm.

### Tổng hợp mean Δ(C−A) theo phân khúc

| Phân khúc | n_samples | n_tickers | mean Δ(C−A) |
|---|---|---|---|
| sector: Banking | 425 | 25 | -0.0447 |
| sector: Consumer | 170 | 10 | -0.0400 |
| sector: Energy | 131 | 8 | -0.0250 |
| sector: Industrial | 168 | 10 | -0.0848 |
| sector: RealEstate | 220 | 13 | +0.0063 |
| sector: Securities | 101 | 6 | -0.0250 |
| sector: Technology | 51 | 3 | -0.0208 |
| sector: Transport | 82 | 5 | +0.0414 |
| cap_group: large_cap | 510 | 30 | -0.0217 |
| cap_group: mid_cap | 838 | 50 | -0.0187 |

## 2. Số keyword đạt ý nghĩa (sau BH_FDR) theo phân khúc

So với Baseline_v0 toàn cục là **0/71**.


| Phân khúc | # sig / # tested | Baseline_v0 |
|---|---|---|
| sector: Banking | 0/42 | 0/71 |
| sector: Consumer | 0/52 | 0/71 |
| sector: Energy | 0/42 | 0/71 |
| sector: Industrial | 0/45 | 0/71 |
| sector: RealEstate | 0/52 | 0/71 |
| sector: Securities | 0/33 | 0/71 |
| sector: Technology | 0/26 | 0/71 |
| sector: Transport | 0/26 | 0/71 |
| cap_group: large_cap | 0/60 | 0/71 |
| cap_group: mid_cap | 0/60 | 0/71 |

## 3. Tỷ lệ đóng góp SHAP của nhóm đặc trưng văn bản

B3 không tính lại SHAP riêng cho từng phân khúc (mỗi phân khúc là một lần huấn luyện lại độc lập).

- Thí nghiệm B3: **not computed per segment**
- Baseline_v0: **32%**

## 4. Kiểm định McNemar

McNemar: **not applicable** cho B3 ở mức tổng hợp — B3 không tạo một tập dự đoán Config_C toàn cục duy nhất để so trực tiếp với Baseline_v0 (mỗi phân khúc là một lần huấn luyện lại riêng). Việc huấn luyện lại theo phân khúc dùng **cùng pipeline và cùng quy trình chia thời gian** như v0, nên các so sánh Δ(C−A) trong từng phân khúc vẫn là apples-to-apples (Req 13.4).

## 5. Nhận xét về các giả thuyết (H1, H2, H3)

> **Đính chính diễn giải (bản sửa):** Diễn giải tự động ban đầu ("H3 được ủng hộ") đã
> được xem xét lại dựa trên phân tích tính vững của tín hiệu. Các Δ(C−A) dương quan sát
> được **không đại diện cho tín hiệu văn bản thật**, vì ba lý do độc lập dưới đây.

Phân khúc có Δ(C−A) trung bình > 0.01: chỉ sector: Transport (mean Δ=+0.0414) và
RealEstate (mean Δ=+0.0063, gần như 0).

Phân khúc có ít nhất một keyword đạt ý nghĩa sau BH_FDR: **không có phân khúc nào**
(0/1062 dòng kiểm định trên toàn bộ ngành và nhóm vốn hóa — kể cả trước hiệu chỉnh
đa kiểm định).

### Vì sao các Δ(C−A) dương chỉ là nhiễu, không phải tín hiệu

1. **Không nhất quán giữa các thuật toán.** Transport: XGBoost +0.1364 nhưng LightGBM
   **−0.0714** trên cùng dữ liệu. Technology: LogReg +0.1667 nhưng Random Forest **−0.25**.
   Tín hiệu thật phải nhất quán trên các mô hình; dao động trái chiều biên độ lớn là dấu
   hiệu overfit nhiễu.
2. **Cỡ mẫu quá nhỏ.** Các phân khúc "dương" chính là các phân khúc nhỏ nhất (Transport
   n=82, Technology n=51). Balanced accuracy 0.9583 của Technology ≈ 23/24 cho thấy test
   set chỉ ~24 mẫu — chỉ cần đúng thêm 1–2 mẫu do may mắn là Δ(C−A) nhảy vài điểm phần trăm.
3. **Không có ý nghĩa thống kê từ khóa.** Không một từ khóa nào đạt ngưỡng ở bất kỳ phân
   khúc nào.

Ngược lại, hai phân khúc có statistical power cao nhất — **large_cap (n=510, mean Δ=−0.0217)**
và **mid_cap (n=838, mean Δ=−0.0187)** — đều cho kết quả **âm**, nhất quán với kết quả âm
toàn cục. Đây mới là các ước lượng đáng tin cậy.

- **H1 — Đặc trưng văn bản cải thiện dự báo:** **Không được ủng hộ** ở cấp phân khúc. Không
  phân khúc nào cho tín hiệu dương vững; các Δ dương đều thuộc phân khúc n nhỏ và không nhất
  quán giữa các mô hình.
- **H2 — Đặc trưng văn bản bổ sung thông tin ngoài giá:** **Không được ủng hộ** — không có
  bằng chứng phân khúc nào cho thấy văn bản bổ sung thông tin vượt trên giá một cách vững.
- **H3 — Tín hiệu văn bản có điều kiện theo phân khúc:** **Không được ủng hộ.** B3 **không**
  tìm thấy phân khúc nào có tín hiệu văn bản thật. Tuy nhiên B3 vẫn có giá trị học thuật: nó
  **loại trừ** giả thuyết "tín hiệu bị pha loãng do gộp toàn thị trường", qua đó củng cố kết
  luận âm chung thay vì làm suy yếu nó.
## 6. Phân tích nguyên nhân (3 giải thích lý thuyết)

- **Semi-strong EMH (thị trường hiệu quả dạng vừa):** Nếu tin tức công khai đã được phản ánh nhanh vào giá, thì đặc trưng trích từ tin tức khó mang thêm thông tin dự báo vượt trên đặc trưng kỹ thuật. Δ(C−A) ≈ 0 nhất quán với giả thuyết này.
- **Within-period absorption (hấp thụ trong kỳ):** Với độ chi tiết theo quý, phản ứng giá với tin tức thường xảy ra và tan biến ngay trong kỳ, nên tổng hợp theo quý làm mờ tín hiệu ngắn hạn — điều này thúc đẩy các thí nghiệm ở độ chi tiết cao hơn (B1 cấp bài viết, các period nhỏ hơn).
- **Giới hạn biểu diễn văn bản:** Sau full-text enrichment, phản biện "corpus quá ngắn" yếu hơn. Giới hạn chính còn lại là cách biểu diễn/aggregate văn bản chưa nắm đủ ngữ cảnh, cường độ, novelty và thời điểm tác động, làm tín hiệu dễ bị nhiễu khi đưa vào Config_C.

## 7. Kết luận và vị trí trong luận văn

Thí nghiệm **B3** đóng vai trò một mắt xích trong chuỗi kiểm chứng độ vững của kết quả âm (Hướng A) và tìm tín hiệu có điều kiện (Hướng B). Kết quả bổ sung bằng chứng cho **Chương 4 (Kết quả thí nghiệm)** và tinh chỉnh lập luận của **Chương 5 (Kết luận)**: nếu ngay cả các tầng biểu diễn văn bản tinh vi hơn vẫn cho Δ(C−A) ≈ 0, kết luận âm về giá trị dự báo của đặc trưng văn bản ở độ chi tiết quý được củng cố, đồng thời định hướng nghiên cứu tương lai sang độ chi tiết cao hơn và phân tích theo phân khúc.
