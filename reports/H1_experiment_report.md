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
|---|---:|---:|---:|---:|---:|
| 1 tuần | 10.788 | 232 | 0,6709 | 0,6641 | −0,0068 |
| 2 tuần | 7.090 | 117 | 0,7024 | 0,6954 | −0,0071 |
| 1 tháng | 3.815 | 53 | 0,6938 | 0,6906 | −0,0032 |
| 2 tháng | 2.042 | 26 | 0,6898 | 0,6786 | −0,0112 |
| Quý | 1.348 | 17 | 0,6304 | 0,6398 | +0,0094 |

Sau full-text enrichment, không còn "đỉnh" cải thiện ổn định ở 1 tháng/2 tháng. Delta trung bình âm ở 4/5 đơn vị thời gian; riêng quý dương nhỏ nhưng không nhất quán theo thuật toán.

### Không còn "hình chuông" sau full-text enrichment

```
Quý (3 tháng):  +0.0094   ~ nhỏ, không nhất quán
2 tháng:        -0.0112   ❌ giảm
1 tháng:        -0.0032   ~ gần 0
2 tuần:         -0.0071   ~ giảm nhẹ
1 tuần:         -0.0068   ~ giảm nhẹ
```

Sau full-text enrichment, đóng góp của từ khóa **không có dạng hình chuông** nữa. Bốn đơn vị ngắn hơn quý đều âm nhẹ; riêng quý dương nhỏ nhưng không ổn định theo thuật toán. Điều này làm kết luận H1 âm rõ hơn so với các lần chạy metadata/keyword trước.

### 5a-bis. Kết quả ở granularity 1 tuần (bổ sung)

Để trả lời trực tiếp câu hỏi "tín hiệu văn bản có xuất hiện ở khung thời gian ngắn hơn không",
đã bổ sung đơn vị **1 tuần** (7 ngày lịch, ~5 phiên giao dịch) với cỡ mẫu rất lớn:

| Đơn vị | n_samples | n_test | Δ(C−A) TB | Nhận xét |
|---|---:|---:|---:|---|
| **1 tuần** | **10.788** | **2.764** | **−0,0068** | Giảm nhẹ, n lớn → ước lượng tin cậy |
| 2 tuần | 7.090 | 1.660 | −0,0071 | Giảm nhẹ |
| 1 tháng | 3.815 | 785 | −0,0032 | ≈ 0 |
| 2 tháng | 2.042 | 400 | −0,0112 | Giảm nhẹ |
| Quý | 1.348 | 240 | +0,0094 | Dương nhỏ, không nhất quán |

Chi tiết 1 tuần theo thuật toán:

| Thuật toán | Config_A | Config_C | Δ(C−A) |
|---|---:|---:|---:|
| LightGBM | 0,6723 | 0,6662 | −0,0061 |
| Logistic Regression | 0,6819 | 0,6851 | +0,0031 |
| Random Forest | 0,6666 | 0,6590 | −0,0077 |
| XGBoost | 0,6628 | 0,6460 | −0,0168 |

**Diễn giải:**
- Với **2.764 mẫu test** (cỡ mẫu lớn nhất trong toàn bộ thí nghiệm), Δ(C−A) = −0,0068 gần như bằng 0 nhưng theo chiều bất lợi cho Config_C.
- 3/4 thuật toán ở cấp tuần âm; Logistic Regression dương rất nhỏ (+0,0031), không đủ tạo kết luận cải thiện.
- Corpus ở cấp tuần không còn là lý do chính để nghi ngờ: cỡ mẫu lớn giúp ước lượng ổn định hơn, nhưng Config_C vẫn không thắng Config_A.
- **Kết luận mạnh hơn:** tin tức tài chính tiếng Việt dưới dạng tần suất từ khóa không mang thêm giá trị dự báo ổn định ở bất kỳ khung thời gian nào đã kiểm tra (tuần, 2 tuần, tháng, 2 tháng, quý). Kết quả nhất quán với giả thuyết thị trường hiệu quả dạng vừa (Semi-strong EMH).

### Giải thích (cập nhật)

Ba lực đối nghịch:
- **Rút ngắn kỳ → có lợi (lý thuyết):** tin tức "tươi" hơn, gần thời điểm phản ứng giá.
- **Rút ngắn kỳ → có hại (thực tế):** mỗi (mã, kỳ) có quá ít bài tin → tín hiệu từ khóa
  thưa và nhiễu, đóng góp tan biến.
- **EMH:** kể cả ở khung ngắn, nếu thị trường đã phản ánh tin tức vào giá trước khi bài
  báo xuất bản (hoặc ngay lúc xuất bản), thì đặc trưng từ khóa trích xuất *sau* khi bài
  đăng không còn giá trị dự báo.

Kết quả thực nghiệm ủng hộ lực thứ hai và thứ ba: **không tồn tại khung thời gian nào** mà
đặc trưng tần suất từ khóa tạo ra cải thiện dự báo vượt trên đặc trưng kỹ thuật.

---

## 5b. Kiểm định ý nghĩa thống kê (McNemar) — Random Forest, đơn vị tháng (corpus ban đầu ~7.5k bài)

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

## 5c. Mở rộng nguồn tin tức — VietnamBiz (kiểm chứng giả thuyết "thiếu dữ liệu")

Giả thuyết đặt ra: cải thiện ở đơn vị tháng chưa significant **vì thiếu dữ liệu** (chỉ 34 ca bất
đồng). Để kiểm chứng, đã bổ sung nguồn thứ tư **VietnamBiz** (3.598 bài, giai đoạn 2024-08 → 2026),
nâng corpus tin đã xử lý từ **7.492 → 11.087 bài (+48%)**.

Phân bố nguồn sau mở rộng: CafeF 6.072, VietnamBiz 3.515, TNCK 1.114, Vietstock 386.

**Kết quả delta (Config_C − Config_A) trước vs sau khi thêm VietnamBiz:**

| Đơn vị | Delta trước | Delta sau |
|---|---|---|
| 2 tuần | +0.0005 | −0.0006 |
| **1 tháng** | **+0.0109** | **−0.0245** |
| 2 tháng | −0.0028 | −0.0316 |
| Quý | −0.0156 | −0.0194 |

**McNemar (Random Forest, đơn vị tháng) sau mở rộng:** số ca bất đồng tăng 34 → **45**, nhưng
delta về gần 0 (−0.003) và **p-value = 1.000** — hoàn toàn không có ý nghĩa thống kê.

### Diễn giải (quan trọng)

Việc thêm dữ liệu **không** củng cố H1 — ngược lại, "lợi thế" của từ khóa ở đơn vị tháng (+1.1
điểm trước đây) **biến mất** khi có thêm dữ liệu. Điều này cho thấy:

- Mức +3.6 điểm của Random Forest ở thí nghiệm trước **đúng là dao động ngẫu nhiên** (đúng như
  McNemar p=0.121 đã cảnh báo), không phải tín hiệu thật. Khi tăng dữ liệu, nó hồi quy về 0.
- Kết luận H1 **"không được ủng hộ"** giờ **vững hơn**: với corpus lớn hơn và đa dạng nguồn hơn,
  đặc trưng từ khóa vẫn không cải thiện dự báo ở mọi đơn vị thời gian.
- Đây là minh hoạ điển hình của **regression to the mean**: cải thiện nhỏ trên mẫu ít thường tan
  biến khi có thêm dữ liệu — một bài học phương pháp luận giá trị cho luận văn.

> Lưu ý: VietnamBiz chỉ phủ 2024-08 trở đi (trang web giới hạn phân trang sâu), nên phần làm dày
> dữ liệu tập trung vào giai đoạn gần. Dù vậy kết luận về dấu của delta không đổi.

---

## 5d. Mở rộng nguồn lần 2 — đào sâu Vietstock (corpus 4 nguồn cân bằng)

Để khắc phục rủi ro phụ thuộc một nguồn (CafeF chiếm 83%), đã **đào sâu Vietstock** qua endpoint
phân trang nội bộ `/View/PagingNewsContent` (phát hiện từ JS của trang tin), thay cho cách cũ chỉ
lấy ~20 bài mới nhất/mã. Kết quả: Vietstock từ **534 → 5.008 bài** (gấp ~9 lần).

**Phân bố nguồn sau khi cân bằng (17.787 bài unique):**

| Nguồn | Trước | Sau | Tỷ lệ sau |
|---|---|---|---|
| CafeF | 8.020 (83%) | 8.020 | **45%** |
| Vietstock | 534 (5%) | 5.008 | 28% |
| VietnamBiz | 0 | 3.598 | 20% |
| TNCK | 1.161 | 1.161 | 7% |

CafeF không còn áp đảo (83% → 45%); corpus tin đã xử lý lên ~13.351 news_count (mật độ mã-quý dày
hơn rõ rệt). Đây là cơ sở dữ liệu khách quan hơn nhiều cho luận văn.

**Kết quả delta trung bình (Config_C − Config_A) qua 3 lần mở rộng corpus:**

| Đơn vị | Lần 1 (~7.5k) | Lần 2 (+VietnamBiz, 11k) | Lần 3 (+Vietstock, 13k, 4 nguồn) |
|---|---|---|---|
| 2 tuần | +0.0005 | −0.0006 | −0.0009 |
| 1 tháng | **+0.0109** | −0.0245 | −0.0028 |
| 2 tháng | −0.0028 | −0.0316 | −0.0273 |
| Quý | −0.0156 | −0.0194 | −0.0224 |

**McNemar (Random Forest, tháng) sau cùng:** 44 ca bất đồng, delta −0.0045, **p = 0.880** — không
có ý nghĩa thống kê.

### Kết luận sau 3 lần mở rộng

Bất chấp việc tăng corpus gần **gấp đôi** (9.7k → 17.8k bài) và **cân bằng 4 nguồn** (CafeF không
còn áp đảo), đặc trưng từ khóa **vẫn không cải thiện** dự báo ở mọi đơn vị thời gian. Delta dao
động quanh 0 hoặc âm; mọi kiểm định McNemar đều không significant (p từ 0.12 đến 1.0).

Đây là bằng chứng **rất mạnh và khách quan** cho kết luận: với cách biểu diễn tin tức bằng tần suất
từ khóa và bài toán phân loại theo kỳ, **H1 không được ủng hộ** — kết luận bền vững qua nhiều ngưỡng
thời gian, nhiều đơn vị thời gian, và **ba quy mô/cấu trúc corpus khác nhau**. Rủi ro "kết quả chỉ
do thiên lệch một nguồn CafeF" đã được loại trừ.

---

## 5e. Mở rộng nguồn lần 3 — thêm VnExpress (5 nguồn, corpus ~19.5k)

Tiếp tục đa dạng hóa, đã khảo sát ~10 nguồn uy tín và thêm **VnExpress** (báo điện tử lớn nhất VN) —
3 chuyên mục kinh doanh (chứng khoán, doanh nghiệp, vĩ mô). Tối ưu: trích ngày từ URL ảnh thumbnail
(`/YYYY/MM/DD/`) nên không cần fetch từng bài. Thu được **1.762 bài** (2025-07 → 2026).

Các nguồn khác đã khảo sát nhưng loại: VnEconomy/nguoiquansat/kinhtechungkhoan (phân trang JS),
tbtaichinh/cafebiz/vietnamfinance (404/redirect), ndh.vn (đã đóng cửa).

**Phân bố nguồn cuối (5 nguồn, 19.549 bài unique):**

| Nguồn | Bài | Tỷ lệ |
|---|---|---|
| CafeF | 8.020 | 41% |
| Vietstock | 5.008 | 26% |
| VietnamBiz | 3.598 | 18% |
| VnExpress | 1.762 | 9% |
| TNCK | 1.161 | 6% |

CafeF từ 83% → **41%**. Corpus gấp đôi ban đầu (9.7k → 19.5k); news_count theo kỳ ~15.151.

**Delta trung bình (Config_C − Config_A) qua 4 lần mở rộng:**

| Đơn vị | Lần 1 (7.5k) | Lần 2 (11k) | Lần 3 (17.8k) | Lần 4 (19.5k, 5 nguồn) |
|---|---|---|---|---|
| 2 tuần | +0.0005 | −0.0006 | −0.0009 | −0.0049 |
| 1 tháng | +0.0109 | −0.0245 | −0.0028 | −0.0268 |
| 2 tháng | −0.0028 | −0.0316 | −0.0273 | −0.0292 |
| Quý | −0.0156 | −0.0194 | −0.0224 | −0.0244 |

**McNemar (RF, tháng) lần cuối:** 41 ca bất đồng, delta −0.025, **p = 0.211** — không significant.

### Kết luận cuối cùng (rất vững)

Qua **4 lần mở rộng corpus** (gấp đôi dữ liệu) và **5 nguồn cân bằng** (không nguồn nào quá 41%),
đặc trưng từ khóa tin tức **nhất quán không cải thiện** dự báo ở mọi đơn vị thời gian. Mọi delta đều
quanh 0 hoặc âm; mọi McNemar đều không significant. Rủi ro thiên lệch nguồn đã được loại trừ triệt
để. **H1 không được ủng hộ** là kết luận khoa học vững chắc, đa chiều và khách quan.

---

## 5f. Mở rộng nguồn lần 4 — kinhtechungkhoan qua sitemap (6 nguồn, corpus ~28k)

Tiếp tục theo yêu cầu khảo sát thêm 6 nguồn (VnEconomy, VietnamFinance, Kinh Tế Chứng Khoán,
Stockbiz, TNCK, 24hmoney). Kết quả khảo sát sâu:

| Nguồn | Kết quả |
|---|---|
| **Kinh Tế Chứng Khoán** | ✅ Thêm — phát hiện **sitemap theo ngày** (`sitemap-article-YYYY-MM-DD.xml`) phủ 2010-2026, kèm `<lastmod>` (ngày chính xác). Lọc slug chứa mã/tên VN30 (~7%), lấy **8.513 bài** không cần JS. |
| 24hmoney | ⚠️ Trang render 49 bài + ngày chuẩn, nhưng phân trang sâu cần API ẩn không tìm được. Bỏ. |
| Stockbiz | ❌ Chỉ ~9 bài, phân trang lặp trang 1. Bỏ. |
| VnEconomy, VietnamFinance | ❌ Phân trang JS / 404 (như khảo sát trước). Bỏ. |
| TNCK | Đã có sẵn (qua search). |

**Phân bố nguồn cuối (6 nguồn, 28.062 bài unique):**

| Nguồn | Bài | Tỷ lệ |
|---|---|---|
| Kinh Tế Chứng Khoán | 8.513 | 30% |
| CafeF | 8.020 | 29% |
| Vietstock | 5.008 | 18% |
| VietnamBiz | 3.598 | 13% |
| VnExpress | 1.762 | 6% |
| TNCK | 1.161 | 4% |

CafeF từ **83% → 29%**. Corpus gần **gấp 3 lần** ban đầu (9.7k → 28k); news_count theo kỳ ~22.697.

**McNemar (RF, tháng) cuối:** 40 ca bất đồng, delta −0.016, **p = 0.430** — không significant.

### Kết luận sau 5 lần mở rộng (kết luận tối hậu)

Qua **5 lần mở rộng corpus** (9.7k → 28k bài, gần gấp 3) và **6 nguồn cân bằng** (không nguồn nào
quá 30%), đặc trưng từ khóa tin tức **nhất quán không cải thiện** dự báo. Mọi delta trung bình quanh
0 hoặc âm; mọi McNemar đều không significant (p từ 0.12 đến 1.0). Đây là bằng chứng **rất mạnh và
khách quan**: kết luận **H1 không được ủng hộ** đã được kiểm chứng triệt để, loại trừ hoàn toàn nghi
vấn thiên lệch hoặc thiếu dữ liệu nguồn.

---

## 5g. Cải tiến phương pháp đếm từ khóa — xử lý phủ định + từ đồng nghĩa (Option 3)

Theo định hướng giữ nguyên khung "đếm tần suất từ khóa" của đề cương (không dùng sentiment/embedding),
đã cải tiến **chính bản thân cách đếm** để khắc phục hai điểm yếu cốt lõi:

1. **Phủ định phá vỡ cụm từ.** Trước đây "lợi nhuận không tăng" vẫn bị tính là tín hiệu tích cực vì
   chứa chuỗi con "tăng". Đã bổ sung các **cụm phủ định** vào danh sách tiêu cực: "lợi nhuận không
   tăng", "doanh thu không tăng", "không tăng trưởng", "tăng trưởng chậm lại", "không hoàn thành kế
   hoạch", "không đạt kế hoạch", "chưa có lãi"…
2. **Từ đồng nghĩa ngoài danh sách.** Đã mở rộng nhóm A với các biến thể thực tế: tích cực ("lãi
   khủng", "lãi lớn", "báo lãi", "lợi nhuận kỷ lục", "bứt phá", "tăng vọt", "khởi sắc", "phục hồi",
   "lập đỉnh"…); tiêu cực ("báo lỗ", "lỗ nặng", "lỗ kỷ lục", "lao dốc", "giảm sâu", "tụt dốc", "kinh
   doanh sa sút"…). Nhóm A: 9→24 tích cực, 9→27 tiêu cực.

### Kỹ thuật then chốt — đếm theo "cụm dài trước, che vùng đã khớp" (longest-first masking)

Nếu chỉ thêm "không tăng trưởng" (tiêu cực) mà vẫn đếm bằng `.count()` ngây thơ thì code **vẫn đếm
cả "tăng trưởng" (tích cực)** nằm bên trong → đếm trùng cả hai chiều, làm hỏng tín hiệu. Đã sửa
`compute_raw_counts` trong `pipeline/task9_kw_features.py`:

1. Sắp xếp từ khóa theo độ dài giảm dần (cụm dài khớp trước).
2. Đếm từng cụm trên văn bản đã được che dần.
3. **Che (mask)** mọi vùng đã khớp bằng ký tự sentinel để cụm ngắn hơn nằm trong không bị đếm lại.

Nhờ vậy "lợi nhuận không tăng" chỉ tính cụm tiêu cực, **không** còn cộng nhầm cho "tăng". Đã bổ sung
5 unit test cho hành vi này (tổng test 535 → 540, tất cả pass).

### Kết quả (corpus 6 nguồn ~28k, sau cải tiến)

**Đơn vị quý (cutoff 2025Q1), Balanced Accuracy:**

| Thuật toán | Config A | Config C | C − A |
|---|---|---|---|
| Random Forest | 0.764 | 0.752 | −0.011 |
| XGBoost | 0.725 | 0.715 | −0.010 |
| LightGBM | 0.724 | 0.708 | −0.016 |
| Logistic Regression | 0.725 | 0.703 | −0.022 |

**Delta trung bình (Config_C − Config_A) — trước vs sau cải tiến đếm từ:**

| Đơn vị | Trước cải tiến (6 nguồn) | Sau cải tiến (phủ định + đồng nghĩa) |
|---|---|---|
| 2 tuần | −0.0049* | −0.0143 |
| 1 tháng | −0.0268 | −0.0087 |
| 2 tháng | −0.0292 | **+0.0047** |
| Quý | −0.0244 | −0.0381 |

(*giá trị tham chiếu lần mở rộng 5 nguồn; mốc 6 nguồn không chạy lại period trước cải tiến.)

Cải tiến giúp delta ở **1 tháng** bớt âm rõ rệt (−0.027 → −0.009) và ở **2 tháng** lần đầu **dương
nhẹ** (+0.005). Tuy nhiên phần dương này đến từ **Logistic Regression** (A=0.600 → C=0.689, +0.089),
còn các mô hình cây mạnh nhất (Random Forest, XGBoost, LightGBM) vẫn âm.

**McNemar (Random Forest, 2 tháng):** delta −0.0325; chỉ 9 ca bất đồng; exact p = 0.180 — **không có
ý nghĩa thống kê**.

### Diễn giải

Việc xử lý phủ định và bổ sung từ đồng nghĩa **cải thiện chất lượng tín hiệu từ khóa** (delta dịch
lên ở 1-2 tháng, một mô hình tuyến tính được hưởng lợi rõ), chứng tỏ hướng cải tiến là **đúng về
nguyên lý**. Nhưng mức cải thiện vẫn **nhỏ, không nhất quán giữa các thuật toán, và không đạt ý nghĩa
thống kê**. Các mô hình cây — vốn cho độ chính xác cao nhất — vẫn không được lợi từ đặc trưng từ khóa.

➡️ Kết luận **H1 không được ủng hộ** vẫn giữ nguyên, kể cả khi đã khắc phục hai điểm yếu lớn nhất của
phương pháp đếm từ. Điều này củng cố nhận định: **giới hạn nằm ở chính cách biểu diễn tin tức bằng
tần suất từ khóa**, chứ không phải do danh sách từ chưa đủ tốt hay thiếu dữ liệu.

---

## 5h. Kiểm chứng sau khi dùng toàn văn bài báo — full-text enrichment 99.96%

Sau khi đã enrich toàn văn gần như đầy đủ (`45.949/45.968` unique URLs có `full_text`, **99,96% coverage**), pipeline được chạy lại từ điểm văn bản được sử dụng: TASK 4 tiền xử lý full text → TASK 5/6 tổng hợp và nhãn → TASK 8/9 keyword features → TASK 10/11 train và SHAP.

**Thay đổi dữ liệu sau full text:**

| Chỉ tiêu | Giá trị |
|---|---:|
| Bài enriched input | 52.790 dòng |
| Unique URL sau dedup | 45.968 |
| Bài sau fuzzy-title dedup | 35.158 |
| Average token/article | 714,8 |
| Ticker-period pairs (`news_by_quarter`) | 1.450 |
| Merged train/test samples | 1.348 |
| Keyword features | 324 |

Average token/article tăng lên rất mạnh, xác nhận TASK 4 đang thật sự dùng nội dung toàn văn chứ không còn chỉ dùng tiêu đề/mô tả.

**Kết quả quý, cutoff 2025Q1 (TASK 10 production split):**

| Thuật toán | Config A | Config B | Config C | C − A |
|---|---:|---:|---:|---:|
| LightGBM | **0,7599** | 0,4510 | 0,7357 | −0,0242 |
| Logistic Regression | 0,7269 | 0,4999 | 0,7132 | −0,0138 |
| Random Forest | 0,7351 | 0,5053 | 0,6679 | −0,0672 |
| XGBoost | 0,7293 | 0,4792 | 0,7238 | −0,0055 |

Best model vẫn là **LightGBM Config_A**. Config_B gần mức ngẫu nhiên; Config_C không cải thiện so với Config_A ở cả 4 thuật toán. Vì best model là Config_A, SHAP chạy trên 16 đặc trưng kỹ thuật và keyword contribution = **0%**.

**Granularity sau full text (`reports/period_experiment.csv`):**

| Đơn vị | n_samples | n_test | Mean Δ(C−A) |
|---|---:|---:|---:|
| 1 tuần | 10.788 | 2.764 | −0,0068 |
| 2 tuần | 7.090 | 1.660 | −0,0071 |
| 1 tháng | 3.815 | 785 | −0,0032 |
| 2 tháng | 2.042 | 400 | −0,0112 |
| Quý | 1.348 | 240 | +0,0094 |

Sau full text, delta trung bình âm ở 4/5 đơn vị thời gian. Dấu dương nhỏ ở quý không ổn định theo thuật toán (LightGBM/Logistic Regression/XGBoost dương, Random Forest âm) và không đủ đảo kết luận H1.

**McNemar sau full text:**

- Random Forest, **1 tháng**: Config_A 0,6998 vs Config_C 0,6796; Δ = **−0,0202**, exact p = **0,0227**. Khác biệt có ý nghĩa thống kê nhưng theo chiều **Config_C tệ hơn Config_A**.
- Random Forest, **2 tháng**: Config_A 0,7002 vs Config_C 0,6978; Δ = **−0,0024**, exact p = **0,4638**. Không có ý nghĩa thống kê.

### Diễn giải

Full text đã loại trừ phản biện quan trọng nhất còn lại: kết quả âm không phải do pipeline chỉ dùng title/description quá nghèo thông tin. Khi đưa gần như toàn văn corpus vào chuỗi xử lý, đặc trưng tần suất từ khóa vẫn không cải thiện dự báo; ở split production theo quý, Config_C còn kém Config_A rõ rệt. Điều này củng cố kết luận rằng giới hạn nằm ở cách biểu diễn tin tức bằng tần suất từ khóa trong bài toán dự báo theo kỳ, không phải do thiếu nội dung bài báo.

➡️ **H1 tiếp tục không được ủng hộ, với bằng chứng mạnh hơn sau full-text enrichment.**

---

## 6. Kết luận tổng hợp

1. **Đặc trưng kỹ thuật là nền tảng dự báo chính** (Balanced Accuracy ~0.65–0.78); đặc trưng từ
   khóa đơn lẻ gần như không có sức dự báo.
2. **Ở đơn vị quý, H1 không được ủng hộ** — kết hợp từ khóa không cải thiện, kết luận này bền qua
   nhiều ngưỡng thời gian.
3. **Tín hiệu "đỉnh ở 1 tháng" (+3.6 điểm) trong corpus cũ là dao động ngẫu nhiên, không phải tín hiệu thật.**
   McNemar đã cảnh báo (p=0.121); khi mở rộng corpus và sau đó dùng full text, mức cải thiện này biến
   mất. Với full text, mean Δ(C−A) ở 1 tháng là −0,0032 và Random Forest 1 tháng còn cho Config_C kém Config_A có ý nghĩa thống kê (p=0,0227).
4. **Kết luận cuối: H1 không được ủng hộ** — kiểm chứng qua nhiều ngưỡng thời gian, nhiều đơn vị
   thời gian, và **năm lần mở rộng corpus** (9.7k → 28k bài, gần gấp 3) với **6 nguồn cân bằng**
   (Kinh Tế Chứng Khoán 30%, CafeF 29%, Vietstock 18%, VietnamBiz 13%, VnExpress 6%, TNCK 4% —
   không nguồn nào áp đảo). Đặc trưng tần suất từ khóa tin tức (theo cách biểu diễn hiện tại) không
   cải thiện dự báo xu hướng giá VN30. Rủi ro thiên lệch/thiếu nguồn dữ liệu đã được loại trừ triệt để.

### Hướng nghiên cứu tiếp theo (gợi ý)
- Biểu diễn tin tức tinh vi hơn tần suất từ khóa (embedding / mô hình ngôn ngữ), xử lý phủ định.
- Mô hình hóa độ trễ tác động của tin (event-time) thay vì gộp cố định theo lịch.
- Bổ sung nguồn tin phủ giai đoạn 2022-2024 để cân bằng dữ liệu theo thời gian.

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
