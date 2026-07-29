# Bổ sung luận văn: Hiệu quả đầu tư (backtest) và giả định kết hợp từ khóa

> Tài liệu tổng hợp phục vụ **Chương 4 (Kết quả thí nghiệm)** và **Chương 5 (Kết
> luận)**. Mọi con số được trích trực tiếp từ các artifact backtest và thí nghiệm
> văn bản trong `reports/` (không làm tròn tùy tiện). Tài liệu này là bản ghi độc
> lập — KHÔNG bị ghi đè khi chạy lại `python -m backtest.run_backtest --all`.

Nguồn số liệu:
- `reports/backtest_performance.csv` — chỉ số hiệu quả đầu tư (cutoff 2025Q1)
- `reports/walk_forward_results.csv` — độ ổn định qua nhiều cutoff
- `reports/technical_feature_importance.csv` — SHAP + permutation (Config_A)
- `reports/model_comparison_B1.csv`, `reports/baseline_v0/model_comparison.csv` — so sánh Config_A/B/C
- `reports/mcnemar_month_rf.txt`, `reports/mcnemar_2month_rf.txt`, `reports/experiment_B1_report.md` — kiểm định McNemar
- `reports/shap_configc_keyword_ranking.csv` — SHAP của đặc trưng từ khóa trong Config_C

---

## Phần A — Hiệu quả đầu tư của mô hình kỹ thuật (trụ đóng góp dương)

### A.1. Từ "độ chính xác" sang "giá trị đầu tư"

Luận văn trước đây mới dừng ở mức đo *độ chính xác dự báo* (balanced accuracy ≈
0,76; AUC ≈ 0,82 với LightGBM, Config_A — chỉ đặc trưng kỹ thuật). Phần backtest
này chuyển kết quả đó thành *giá trị đầu tư thực tế* bằng cách mô phỏng một chiến
lược **long-only** đúng đặc thù thị trường cơ sở Việt Nam, đo lợi nhuận sau chi
phí và so với các benchmark.

### A.2. Kết quả trên tập test chính (cutoff 2025Q1, 5 quý, 80 mã HOSE)

| Chiến lược | Kịch bản | Lợi nhuận tích lũy | LN kỳ TB | Độ lệch chuẩn kỳ | Sharpe | Max Drawdown | Hit rate | Tổng chi phí |
|---|---|---|---|---|---|---|---|---|
| **Mô hình** | gross | **0,6207** | 0,1046 | 0,0969 | **1,0795** | 0,0000 | 1,00 | 0,0000 |
| **Mô hình** | net | **0,6030** | 0,1023 | 0,0972 | **1,0517** | −0,0010 | 0,80 | 0,0120 |
| Buy-and-hold đều | net | 0,2535 | 0,0507 | 0,1138 | 0,4461 | −0,0200 | 0,60 | 0,0000 |
| Equal-weight tái cân bằng | net | 0,2535 | 0,0507 | 0,1138 | 0,4461 | −0,0200 | 0,60 | 0,0000 |

**Diễn giải chính:**

- **Lợi nhuận:** sau chi phí giao dịch, chiến lược mô hình đạt lợi nhuận tích lũy
  **60,3%** trên 5 quý, gấp **~2,4 lần** benchmark (25,4%). Chênh lệch tuyệt đối
  ~35 điểm phần trăm.
- **Rủi ro–lợi nhuận:** Sharpe **1,05 (net)** so với 0,45 của benchmark — mô hình
  không chỉ lời nhiều hơn mà còn hiệu quả hơn trên mỗi đơn vị rủi ro. Độ lệch chuẩn
  kỳ của mô hình (0,097) còn *thấp hơn* benchmark (0,114).
- **Kiểm soát sụt giảm:** Max Drawdown của mô hình gần như bằng 0 (−0,10% net),
  trong khi benchmark −2,00%. Mô hình chủ động giữ tiền mặt/chọn lọc mã "tăng" nên
  đường vốn mượt hơn.
- **Tính nhất quán:** hit rate net 0,80 (4/5 quý dương) so với 0,60 của benchmark.
- **Chi phí:** tổng chi phí giao dịch tích lũy chỉ ~1,2% NAV; khoảng cách gross↔net
  hẹp (62,1% → 60,3%), cho thấy kết luận không bị chi phí giao dịch VN xóa bỏ.

> **Lưu ý minh bạch:** trên tập test này, hai benchmark buy-and-hold và
> equal-weight tái cân bằng cho **kết quả trùng khớp** vì đủ 80 mã đều có dữ liệu ở
> cả 5 quý (không có mã rời/mới), nên tái cân bằng đều mỗi quý ≈ nắm giữ đều. Đây là
> đặc điểm của bộ dữ liệu cân đối, cần nêu rõ để tránh hiểu nhầm hai benchmark là
> hai phép đo độc lập cho ra cùng số một cách ngẫu nhiên.

### A.3. Độ ổn định theo thời gian (walk-forward)

| Cutoff | Số mẫu test | Balanced Accuracy | AUC | LN tích lũy mô hình (net) | LN tích lũy buy-and-hold |
|---|---|---|---|---|---|
| 2024Q3 | 556 | 0,7229 | 0,7970 | 0,6563 | 0,2818 |
| 2025Q1 | 400 | 0,7599 | 0,8235 | 0,6030 | 0,2535 |
| 2025Q3 | 240 | 0,6400 | 0,7098 | 0,1182 | 0,0072 |

- Balanced accuracy trung bình **0,7076**, dao động [0,6400 – 0,7599], độ lệch chuẩn
  **0,0501** — ổn định vừa phải, không phụ thuộc một điểm chia duy nhất.
- Chiến lược mô hình **vượt buy-and-hold ở 3/3 cutoff** và **lợi nhuận net dương ở
  3/3 cutoff** (trung bình 0,4592).
- Cutoff gần nhất (2025Q3) yếu hơn hẳn (BA 0,64; lợi nhuận 0,118) do tập test ngắn
  (chỉ 240 mẫu ≈ 3 quý) và có thể vướng chế độ thị trường bất lợi — đây là cảnh báo
  quan trọng: **ưu thế của mô hình co lại khi cửa sổ test thu hẹp/điều kiện thị
  trường thay đổi.**

### A.4. Đặc trưng kỹ thuật quan trọng nhất (diễn giải mô hình)

| Hạng | Đặc trưng | mean\|SHAP\| | Permutation importance |
|---|---|---|---|
| 1 | `rsi_end_q` (RSI cuối kỳ) | 1,6729 | 0,1860 |
| 2 | `macd_hist_mean_q` | 0,5088 | 0,0192 |
| 3 | `price_vs_sma20` | 0,4462 | 0,0030 |
| 4 | `return_2q_ago` | 0,4134 | 0,0048 |
| 5 | `return_q` | 0,3220 | 0,0128 |

- **`rsi_end_q` áp đảo**: mức SHAP gấp ~3,3 lần đặc trưng hạng 2 và permutation
  importance gấp ~10 lần — RSI cuối quý là tín hiệu động lượng/quá mua–quá bán chi
  phối dự báo. Nhóm động lượng (RSI, MACD, vị thế giá so với SMA20) và lợi nhuận quá
  khứ chiếm phần lớn giá trị dự báo, nhất quán với cơ chế momentum/mean-reversion.

### A.5. Bảo vệ độ tin cậy — kiểm toán rò rỉ

Kiểm toán rò rỉ thời gian (`reports/leakage_audit.md`) **PASS**: 16 đặc trưng kỹ
thuật, trong đó 14 in-period + 2 past (`return_prev_q`, `return_2q_ago`), **0 đặc
trưng future**; không cột nhãn/return tương lai lọt vào feature set; không đặc trưng
nào có |corr| với nhãn vượt 0,95. Đây là bằng chứng tường minh rằng con số BA ≈ 0,76
**không** đến từ rò rỉ dữ liệu — điểm hội đồng dễ chất vấn nhất.

---

## Phần B — Giả định và kết quả kết hợp đặc trưng từ khóa (trụ khám phá)

### B.1. Cấu hình đặc trưng và giả định kết hợp

Ba cấu hình đặc trưng được so sánh trên **cùng một tập test, cùng quy trình chia
thời gian, cùng imputer** để đảm bảo so sánh công bằng:

- **Config_A** — chỉ 16 đặc trưng **kỹ thuật** (giá/khối lượng).
- **Config_B** — chỉ đặc trưng **từ khóa** (đếm/tần suất từ khóa tài chính trích từ
  tin tức CafeF theo (ticker, quý)).
- **Config_C** — **kết hợp** kỹ thuật + từ khóa (nối vector đặc trưng).

**Các giả định của cách kết hợp từ khóa (cần ghi rõ trong luận văn):**

1. **Giả định tổng hợp theo quý (aggregation):** đặc trưng từ khóa của một mã trong
   một quý được tổng hợp (đếm/tần suất) từ toàn bộ bài tin trong quý đó. Giả định
   này làm mờ thông tin *thời điểm trong quý* — một tin tốt đầu quý và cuối quý được
   coi như nhau.
2. **Giả định biểu diễn túi-từ-khóa (bag-of-keywords):** tín hiệu văn bản được rút
   gọn về tần suất xuất hiện của một danh sách từ khóa tài chính định trước, không
   mô hình hóa ngữ cảnh/phủ định đầy đủ ở tầng cơ bản (các biến thể tinh vi hơn được
   thử ở A2/A6).
3. **Giả định ranh giới thời gian:** đặc trưng từ khóa của quý q chỉ dùng tin đến
   hết quý q, khớp cùng ranh giới với đặc trưng kỹ thuật — nên phép so sánh
   Config_C vs Config_A là "thêm thông tin văn bản" thuần túy, không rò rỉ.
4. **Giả định kết hợp cộng tính (concatenation):** kết hợp = nối đặc trưng, để mô
   hình tự học trọng số. Không áp đặt tương tác kỹ thuật×văn bản thủ công.

### B.2. Ba giả thuyết kiểm chứng

- **H1 — Đặc trưng văn bản cải thiện dự báo:** kỳ vọng Δ(C−A) > 0 đáng kể.
- **H2 — Đặc trưng văn bản bổ sung thông tin ngoài giá:** kỳ vọng Config_B mang tín
  hiệu dự báo phi ngẫu nhiên.
- **H3 — Tín hiệu văn bản có điều kiện theo phân khúc/độ chi tiết:** kỳ vọng giá trị
  văn bản chỉ lộ ra ở độ chi tiết cao hơn quý hoặc ở phân khúc nhiều tin.

### B.3. Kết quả — từ khóa gần như không thêm giá trị dự báo

**(a) Từ khóa đơn lẻ (Config_B) gần mức ngẫu nhiên.** Balanced accuracy của
Config_B (chỉ từ khóa) trên 4 thuật toán chỉ quanh **0,49–0,52** — tức xấp xỉ đoán
ngẫu nhiên (0,50):

| Thuật toán | BA Config_B |
|---|---|
| Logistic Regression | 0,4756 |
| Random Forest | 0,5048 |
| XGBoost | 0,4935 |
| LightGBM | 0,4926 |

→ **Bác bỏ H2** ở cấp độ quý: đặc trưng từ khóa một mình không tách được lớp
"tăng"/"không tăng".

**(b) Kết hợp (Config_C) không nâng — thậm chí có xu hướng giảm.** So sánh
Δ(C−A) = BA(Config_C) − BA(Config_A):

| Thuật toán | BA Config_A | BA Config_C | Δ(C−A) |
|---|---|---|---|
| LightGBM | 0,7599 | 0,7485 | **−0,0114** |
| Random Forest | 0,7351 | 0,7380 | +0,0029 |
| XGBoost | 0,7293 | 0,7480 | +0,0187 |
| Logistic Regression | 0,7269 | 0,7274 | +0,0005 |
| **Trung bình** | — | — | **+0,0027 ≈ 0** |

→ Δ(C−A) trung bình **+0,0027** (gần như bằng 0). Với LightGBM (mô hình mạnh nhất),
kết hợp từ khóa còn *làm giảm* BA. **Không ủng hộ H1.**

**(c) Khác biệt không có ý nghĩa thống kê (McNemar).** Kiểm định McNemar giữa
Config_A và Config_C trên cùng tập test:

| Kiểm định | Δ(C−A) | p-value | Kết luận (α = 0,05) |
|---|---|---|---|
| Random Forest, độ chi tiết tháng (297 mẫu) | −0,0303 | 0,1742 | Không có ý nghĩa |
| Random Forest, độ chi tiết 2 tháng (150 mẫu) | −0,0325 | 0,1797 | Không có ý nghĩa |
| Config_C mới vs Config_C baseline (400 mẫu) | — | 0,5601 | Không có ý nghĩa |

→ Mọi khác biệt nằm trong biến động ngẫu nhiên của tập test.

**(d) SHAP xác nhận từ khóa đóng góp không đáng kể trong Config_C.** Trong Config_C,
đặc trưng từ khóa có mean|SHAP| cao nhất chỉ khoảng **0,007** (các từ như "tăng
trưởng", "nợ xấu", "báo lãi", "chia cổ tức", "tăng vốn điều lệ"), trong khi đặc
trưng kỹ thuật dẫn đầu `rsi_end_q` đạt **1,67** — chênh **~240 lần**. Rất nhiều từ
khóa có SHAP = 0 (không bao giờ kích hoạt do thưa/hiếm xuất hiện). Các từ khóa có
đóng góp cao nhất mang đúng chiều kinh tế trực giác (tăng trưởng/báo lãi/cổ tức →
positive; nợ xấu/sụt giảm/lao dốc → negative), nhưng độ lớn quá nhỏ để dịch chuyển
quyết định của mô hình.

### B.4. Ba giải thích lý thuyết cho kết quả âm

1. **Thị trường hiệu quả dạng vừa (semi-strong EMH):** tin công khai được phản ánh
   nhanh vào giá, nên đặc trưng trích từ tin khó thêm thông tin vượt trên đặc trưng
   kỹ thuật — nhất quán với Δ(C−A) ≈ 0.
2. **Hấp thụ trong kỳ (within-period absorption):** ở độ chi tiết quý, phản ứng giá
   với tin thường xảy ra và tan biến ngay trong kỳ; tổng hợp theo quý làm mờ tín
   hiệu ngắn hạn.
3. **Giới hạn biểu diễn tần suất từ khóa:** sau full-text enrichment, phản biện corpus quá ngắn yếu hơn; giới hạn chính còn lại là keyword frequency không nắm đủ ngữ cảnh, cường độ, novelty và thời điểm tác động, làm tăng nhiễu và kéo Δ(C−A) về 0.

### B.5. H3 và định hướng

Kết quả toàn cục **bác bỏ H1, H2** ở cấp độ quý. H3 (tín hiệu văn bản có điều kiện)
**chưa bị bác bỏ**: cần các phân tích ở độ chi tiết cao hơn (cấp bài viết B1, các
period nhỏ hơn) và theo phân khúc (mật độ tin, ngành) để trả lời trực tiếp. Đây là
định hướng nghiên cứu tương lai — không phải kết luận đóng.

---

## Phần C — Thông điệp tổng hợp cho hội đồng

1. **Trụ đóng góp dương (kỹ thuật):** mô hình ML trên đặc trưng kỹ thuật không chỉ
   dự báo chính xác (BA ≈ 0,76; AUC ≈ 0,82) mà còn **tạo giá trị đầu tư thực**: lợi
   nhuận net 60,3% so với 25,4% của benchmark, Sharpe 1,05 vs 0,45, drawdown gần 0,
   ổn định qua 3 cutoff, và **đã được kiểm toán chống rò rỉ**.
2. **Trụ khám phá (văn bản/từ khóa):** kết hợp từ khóa **không** cải thiện dự báo ở
   cấp độ quý (Δ trung bình +0,003, không có ý nghĩa thống kê; từ khóa đơn lẻ ~ngẫu
   nhiên; SHAP từ khóa nhỏ hơn kỹ thuật ~240 lần). Đây là một **kết quả âm có giá
   trị khoa học**, được giải thích bằng EMH dạng vừa / hấp thụ trong kỳ / giới hạn
   corpus, và mở ra hướng nghiên cứu ở độ chi tiết cao hơn.
3. **Giới hạn cần nêu:** backtest theo quý (T+2/biên độ ±7%/lô 100 chỉ là giả định
   nền), bỏ qua trượt giá; kết quả phụ thuộc 80 mã HOSE và khoảng test; ưu thế mô
   hình co lại ở cutoff 2025Q3. Lợi nhuận quá khứ không đảm bảo tương lai — báo cáo
   phục vụ mục tiêu học thuật, không phải khuyến nghị đầu tư.
