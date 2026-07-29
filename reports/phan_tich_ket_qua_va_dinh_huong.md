# Phân tích kết quả thí nghiệm & định hướng luận văn

> Tài liệu tổng hợp phân tích sâu toàn bộ thí nghiệm `text-feature-experiments`
> (Hướng A và Hướng B), đánh giá tính vững của các tín hiệu, và khuyến nghị về
> giá trị/định hướng luận văn. Dùng làm nguồn viết Chương 4 (Kết quả) và Chương 5
> (Kết luận).

---

## 1. Tóm tắt điều hành (Executive Summary)

Toàn bộ thí nghiệm mở rộng đặc trưng văn bản **không tạo ra cải thiện dự báo** so
với baseline chỉ dùng đặc trưng kỹ thuật. Tuy nhiên, chúng **làm kết luận âm của
luận văn vững hơn đáng kể** bằng cách loại trừ các lời giải thích thay thế (đo lường
yếu, tín hiệu bị pha loãng khi gộp toàn thị trường).

Kết luận khoa học cuối cùng:

> Ở độ chi tiết theo quý, đặc trưng trích xuất từ tin tức tài chính tiếng Việt **không
> mang thêm giá trị dự báo** cho xu hướng giá cổ phiếu HOSE-80 vượt trên đặc trưng
> kỹ thuật. Kết quả này **không phải** do phương pháp đo lường văn bản yếu (đã thử tới
> LLM zero-shot và distant supervision cấp bài viết) và **không phải** do tín hiệu bị
> pha loãng khi gộp toàn thị trường (đã kiểm định theo từng phân khúc). Kết quả nhất
> quán với giả thuyết thị trường hiệu quả dạng vừa (Semi-strong EMH).

---

## 2. Kết quả Hướng A — Củng cố kết quả âm

**Mục tiêu:** Chứng minh kết quả âm không phải do biểu diễn văn bản thô sơ, bằng cách
thử các tầng biểu diễn tinh vi hơn tần suất từ khóa.

**Thước đo chính:** Δ(C−A) = balanced accuracy(Config_C: kỹ thuật + văn bản) − balanced
accuracy(Config_A: chỉ kỹ thuật). Δ > 0 nghĩa là văn bản giúp ích.

| Tầng biểu diễn | Δ(C−A) trung bình (4 thuật toán) | McNemar p (vs v0) | Kết luận |
|---|---|---|---|
| v0 — tần suất từ khóa thô | ≈ −0.019 | (mốc gốc) | Âm |
| A6 — LLM sentiment (Gemini Flash) | **−0.0061** | 0.6177 (không ý nghĩa) | Vẫn ≈ 0 |
| B1 — distant supervision cấp bài viết | **+0.0027** | 0.5601 (không ý nghĩa) | Vẫn ≈ 0 |

**Diễn giải:**

- Càng dùng biểu diễn văn bản tinh vi hơn, Δ(C−A) càng tiến về 0 nhưng **không bao giờ
  vượt qua ngưỡng có ý nghĩa**. LLM — tầng biểu diễn cao cấp nhất — vẫn cho Δ ≈ 0.
- McNemar cho cả A6 và B1 đều **không có ý nghĩa thống kê** (p ≫ 0.05): mô hình có văn
  bản không khác biệt thật sự so với baseline trên cùng tập test.
- Điều này bịt lập luận phản biện phổ biến nhất: "kết quả âm vì bạn đo lường văn bản
  kém". Không phải — kể cả LLM cũng không cứu được.

---

## 3. Kết quả Hướng B — Tìm tín hiệu có điều kiện (B3 Segmentation)

**Mục tiêu:** Kiểm tra liệu tín hiệu văn bản có mạnh hơn ở một ngành/nhóm vốn hóa cụ
thể không (giả thuyết H3 — tín hiệu có điều kiện).

### 3.1 Bảng tổng hợp Δ(C−A) theo phân khúc

| Phân khúc | n_samples | n_tickers | mean Δ(C−A) | Đánh giá |
|---|---|---|---|---|
| sector: Banking | 425 | 25 | −0.0447 | Âm |
| sector: Consumer | 170 | 10 | −0.0400 | Âm |
| sector: Energy | 131 | 8 | −0.0250 | Âm |
| sector: Industrial | 168 | 10 | −0.0848 | Âm |
| sector: RealEstate | 220 | 13 | +0.0063 | ~0, không vững |
| sector: Securities | 101 | 6 | −0.0250 | Âm |
| sector: Technology | 51 | 3 | −0.0208 | Nhiễu (n rất nhỏ) |
| sector: Transport | 82 | 5 | +0.0414 | Nhiễu (n nhỏ) |
| **cap_group: large_cap** | **510** | **30** | **−0.0217** | **Âm (power cao)** |
| **cap_group: mid_cap** | **838** | **50** | **−0.0187** | **Âm (power cao)** |

### 3.2 Ba bằng chứng khẳng định tín hiệu dương chỉ là NHIỄU, không phải tín hiệu thật

**Bằng chứng 1 — Không nhất quán giữa các thuật toán.**
Tín hiệu thật phải nhất quán trên cả 4 mô hình. Thực tế ngược lại:

- **Transport** (mean +0.0414): XGBoost **+0.1364**, RF +0.0455, LogReg +0.0552,
  nhưng LightGBM **−0.0714**. Cùng dữ liệu mà XGBoost nói "+13.6%" còn LightGBM nói
  "−7.1%" → các mô hình đang fit nhiễu theo các hướng khác nhau.
- **Technology** (n=51): LogReg **+0.1667**, RF **−0.25**, LightGBM/XGBoost 0.0.
  Biên độ dao động ±0.25 trên cùng dữ liệu = dấu hiệu overfit mẫu nhỏ điển hình.

**Bằng chứng 2 — Cỡ mẫu quá nhỏ, không đủ statistical power.**
Các phân khúc "dương" chính là các phân khúc có tập test nhỏ nhất (đã tính chính xác,
xem `reports/segment_test_sizes.csv`):

| Phân khúc | n_test (mẫu test) | mean Δ(C−A) | Độ tin cậy |
|---|---|---|---|
| Technology | **15** | −0.0208 (dao động ±0.25 giữa model) | Cực thấp |
| Transport | **25** | +0.0414 | Rất thấp |
| Securities | 30 | −0.0250 | Rất thấp |
| large_cap | **150** | −0.0217 | Cao |
| mid_cap | **250** | −0.0187 | Cao |

Với 15–25 mẫu test, chỉ cần dự đoán đúng/sai khác đi 1–2 mẫu là Δ(C−A) nhảy vài điểm
phần trăm. Ngược lại, hai phân khúc có power cao nhất (large_cap n_test=150, mid_cap
n_test=250) **đều âm** — đây mới là kết quả đáng tin, nhất quán với kết quả âm toàn cục.

**Bằng chứng 3 — Không một từ khóa nào đạt ý nghĩa thống kê ở BẤT KỲ phân khúc nào.**
Quét toàn bộ 1062 dòng kiểm định từ khóa trong `segmentation_keyword_sig.csv` (chi-square,
Mann-Whitney, logistic — cả p thô lẫn p sau hiệu chỉnh BH-FDR): **không có một dòng nào
`significant_any = True`**. Kể cả trước khi hiệu chỉnh đa kiểm định, không có keyword nào
vượt ngưỡng ở bất kỳ ngành nào. Nếu Transport thật sự có tín hiệu, phải thấy ít nhất vài
từ khóa nổi lên — không có gì cả.

### 3.3 Diễn giải H3 đúng theo bằng chứng

> **CẢNH BÁO:** Báo cáo tự động `experiment_B3_report.md` hiện diễn giải H3 hơi lạc quan
> ("H3 được ủng hộ"). Theo bằng chứng ở trên, cách diễn giải này **không chính xác** và
> là điểm yếu nếu để nguyên trong luận văn.

Cách trình bày đúng và mạnh hơn:

> Phân tích phân khúc **không tìm thấy** phân khúc nào có tín hiệu văn bản vững. Các
> Δ(C−A) dương quan sát được (Transport, một phần RealEstate) không nhất quán giữa các
> thuật toán, chỉ xuất hiện ở các phân khúc n nhỏ nhất (n = 51–82, test set ~12–24 mẫu),
> và không kèm theo bất kỳ từ khóa nào đạt ý nghĩa thống kê. Chúng phù hợp với dao động
> do phương sai lấy mẫu hơn là tín hiệu thật. Ngược lại, hai phân khúc có power cao nhất
> (large_cap, mid_cap) đều cho Δ(C−A) âm.

**Hệ quả:** B3 **không** "cứu" H3 theo nghĩa tìm ra tín hiệu có điều kiện. Nhưng nó vẫn
là đóng góp học thuật giá trị — nó **loại trừ** giả thuyết "tín hiệu bị pha loãng khi gộp
toàn thị trường", làm kết luận âm càng khó phản biện hơn.

---

## 4. Kết quả B1 — Granularity cấp bài viết

- Nhãn nhiễu (distant supervision từ suất sinh lời [d+1, d+3], ngưỡng ±2%): 25.4%
  positive, 23.8% negative, 50.8% neutral trên 28.519 bài.
- AUC macro one-vs-rest của bộ phân loại cấp bài viết trên nhãn nhiễu: **0.6797** — có
  tín hiệu yếu ở cấp bài viết.
- Nhưng khi gộp xác suất dự đoán theo quý (`ds_pos_prob_mean`, `ds_net_sentiment`), Δ(C−A)
  vẫn ≈ 0 (mean +0.0027).

**Diễn giải:** Có một chút tín hiệu ở cấp bài viết (AUC 0.68 > 0.5), nhưng nó **tan biến
khi tổng hợp theo quý**. Điều này ủng hộ giả thuyết *within-period absorption* (phản ứng
giá xảy ra và tan biến ngay trong kỳ) và là **định hướng nghiên cứu tương lai** mạnh nhất:
thử độ chi tiết cao hơn (ngày/tuần/tháng) thay vì quý.

## 4b. Kết quả bổ sung — Full-text enrichment và granularity 1 tuần

Để kiểm chứng trực tiếp giả thuyết "tín hiệu văn bản tồn tại ở granularity cao hơn" và phản biện "kết quả âm do chỉ dùng tiêu đề/mô tả", pipeline đã được chạy lại sau full-text enrichment gần đầy đủ (**45.949/45.968 unique URLs có `full_text`, 99,96% coverage**). Kết quả:

| Đơn vị | n_samples | n_test | Δ(C−A) TB 4 mô hình | Nhận xét |
|---|---:|---:|---:|---|
| **1 tuần** | **10.788** | **2.764** | **−0,0068** | Giảm nhẹ, n lớn → ước lượng tin cậy |
| 2 tuần | 7.090 | 1.660 | −0,0071 | Giảm nhẹ |
| 1 tháng | 3.815 | 785 | −0,0032 | ≈ 0 |
| 2 tháng | 2.042 | 400 | −0,0112 | Giảm nhẹ |
| Quý | 1.348 | 240 | +0,0094 | Dương nhỏ, không nhất quán |

**Kết luận bổ sung:** Kể cả ở khung thời gian ngắn nhất mà corpus cho phép (1 tuần), đặc trưng từ khóa **vẫn không cải thiện** dự báo. Full text cũng loại trừ phản biện quan trọng rằng kết quả âm do nội dung văn bản nghèo. Khi gần như toàn bộ bài báo được đưa vào TASK 4, Config_C vẫn không thắng Config_A ổn định; ở production split theo quý, Config_C còn kém Config_A ở cả 4 thuật toán. Do đó kết luận âm phản ánh **giới hạn của cách biểu diễn tin tức bằng tần suất từ khóa trong bài toán dự báo theo kỳ**, không phải do thiếu toàn văn hay chỉ do granularity.

---

## 5. Ba giải thích lý thuyết cho kết quả âm (dùng cho Chương 5)

1. **Semi-strong EMH (thị trường hiệu quả dạng vừa):** Tin tức công khai được phản ánh
   nhanh vào giá, nên đặc trưng trích từ tin tức khó mang thêm thông tin vượt trên đặc
   trưng kỹ thuật (vốn đã chứa dấu vết của phản ứng giá). Δ(C−A) ≈ 0 nhất quán với giả
   thuyết này.
2. **Within-period absorption (hấp thụ trong kỳ):** Ở độ chi tiết quý, phản ứng giá với
   tin tức xảy ra và tan biến ngay trong kỳ → tổng hợp theo quý làm mờ tín hiệu ngắn hạn.
   Bằng chứng: AUC cấp bài 0.68 nhưng Δ(C−A) sau khi gộp quý ≈ 0.
3. **Giới hạn biểu diễn tần suất từ khóa:** Full-text enrichment đã làm yếu phản biện "corpus quá ngắn". Giới hạn còn lại nằm ở cách biểu diễn: keyword frequency không phân biệt đủ ngữ cảnh, cường độ, novelty và thời điểm tác động, nên dễ đưa nhiễu vào Config_C.

---

## 6. Đánh giá: Luận văn có đáng làm tiếp không?

**Khuyến nghị: NÊN tiếp tục. Không nên đổi đề tài.**

### 6.1 Vì sao kết quả âm vẫn là luận văn tốt

- **Kết quả âm là kết quả khoa học hợp lệ** khi được chứng minh chặt chẽ. Luận văn của
  bạn không "chạy không ra" — nó *trả lời* một câu hỏi nghiên cứu rõ ràng bằng bằng chứng.
- **Đã bịt các đường phản biện dễ nhất:** thử tới LLM và distant supervision (không phải
  do đo lường yếu); kiểm định theo phân khúc (không phải do gộp toàn thị trường).
- **Nhất quán với lý thuyết kinh tế** (EMH) — một phát hiện có nền tảng, không phải lỗi
  kỹ thuật.
- **Độ nghiêm ngặt phương pháp cao:** chống rò rỉ thời gian, property-based testing, cùng
  pipeline so sánh công bằng, hiệu chỉnh đa kiểm định. Một kết quả âm được kiểm chứng kỹ
  **đáng tin hơn** một kết quả dương mong manh do overfit.
- **Đổi đề tài = vứt toàn bộ công sức và bắt đầu lại với rủi ro tương tự.**

### 6.2 Rủi ro cần lưu ý (thành thật)

- Kết quả âm đòi hỏi **framing tốt** và người hướng dẫn/hội đồng **cởi mở** với dạng kết
  quả này. Nếu chương trình cứng nhắc yêu cầu "phải cải thiện mô hình mới đạt", đó là rủi
  ro thật → **nên xác nhận sớm với GVHD**.
- Cần chỉnh phần diễn giải H3 trong báo cáo B3 cho khớp bằng chứng (mục 3.3) để tránh bị
  vặn về statistical power.

### 6.3 Việc nên làm để luận văn vững hơn (không đổi đề tài)

1. Sửa diễn giải H3 trong `experiment_B3_report.md` theo mục 3.3.
2. Thêm cột kích thước test set cho từng phân khúc để định lượng độ tin cậy (power).
3. Bổ sung phần "hạn chế nghiên cứu" và "hướng phát triển" nhấn vào granularity cao hơn
   (từ B1) — biến điểm yếu thành đề xuất tương lai.
4. Đóng khung toàn bộ luận văn quanh câu hỏi: *"Đặc trưng văn bản có cải thiện dự báo
   không, và nếu không thì vì sao?"* — kết quả âm trở thành câu trả lời trọn vẹn.

---

## 7. Nguồn dữ liệu tham chiếu

- `reports/experiment_A6_report.md` — LLM sentiment
- `reports/experiment_B1_report.md` — distant supervision
- `reports/experiment_B3_report.md` — segmentation
- `reports/distant_supervision_report.md` — chi tiết B1
- `reports/segmentation_analysis.csv` — Δ(C−A) theo phân khúc (dữ liệu thô)
- `reports/segmentation_keyword_sig.csv` — kiểm định ý nghĩa từ khóa (1062 dòng, 0 significant)
- `reports/baseline_v0/` — kết quả gốc đóng băng
