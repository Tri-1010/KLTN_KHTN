# Đánh giá tính thỏa đáng của dữ liệu & statistical power

> Trả lời hai câu hỏi: (1) dữ liệu đã đủ chưa? (2) kiểm định nào dùng quá ít dữ liệu,
> ý nghĩa thống kê thấp? Số liệu lấy trực tiếp từ dữ liệu thô (script
> `experiments/assess_data_adequacy.py`).

---

## Kết luận nhanh

| Loại kiểm định | Quy mô dữ liệu | Đủ power? |
|---|---|---|
| So sánh mô hình **toàn cục** (Δ C−A, McNemar) | Train 948 / **Test 400**, cân bằng ~53/47 | **ĐỦ** |
| Ý nghĩa từ khóa **toàn cục** (BH-FDR) | 106 từ khóa, nhưng 33 có <10 lần xuất hiện | **Một phần** — nhiều từ khóa yếu |
| Ý nghĩa từ khóa **theo phân khúc** | 1060 dòng, 58,7% bị loại, 334/438 có <10 occ | **KHÔNG đủ** |
| Δ(C−A) **theo phân khúc nhỏ** (Transport, Technology) | Test 15–25 mẫu | **KHÔNG đủ** |

Tóm lại: **dữ liệu đủ cho kết luận chính (toàn cục), nhưng KHÔNG đủ cho các kiểm định
chi tiết theo phân khúc và cho phần lớn kiểm định từng-từ-khóa.** Điều quan trọng: điều
này **không làm suy yếu kết luận âm** — vì kết luận âm dựa trên phép so sánh toàn cục
(đủ power), còn các phân khúc thiếu power chỉ được dùng để *loại trừ* giả thuyết tín hiệu
có điều kiện, không phải để *khẳng định* điều gì.

---

## 1. Dữ liệu tổng thể — ĐỦ cho kết luận chính

- Tổng mẫu: **1.348** (ticker × quý), 80 ticker, 17 quý (2022Q1–2026Q1).
- Chia thời gian tại 2025Q1: **train 948 / test 400**.
- Cân bằng nhãn tập test: 210 giảm / 190 tăng (~53/47) — cân bằng tốt, không lệch lớp.

**Đánh giá:** Test set 400 mẫu cân bằng là **đủ** để so sánh balanced accuracy giữa các
cấu hình và chạy McNemar một cách đáng tin cậy. Đây là nền tảng cho kết luận chính của
luận văn (Δ C−A toàn cục ≈ 0, McNemar không ý nghĩa). Kết luận này **vững**.

Lưu ý về chiều thời gian: 17 quý là chuỗi tương đối ngắn cho phân tích chuỗi thời gian.
Điều này không ảnh hưởng phép so sánh cross-sectional hiện tại, nhưng nên nêu trong phần
hạn chế.

## 2. Kiểm định ý nghĩa từ khóa toàn cục — power không đồng đều

Trong 106 từ khóa được xét:

| Số lần xuất hiện | Số từ khóa | Đánh giá power |
|---|---|---|
| = 0 (bị loại) | 35 | Không kiểm định được |
| 1–4 | 24 | Gần như vô hiệu |
| 5–9 | 9 | Rất thấp |
| 10–29 | 19 | Trung bình |
| ≥ 30 | 19 | Đủ để tin cậy |

**Đánh giá:** Chỉ ~19/106 từ khóa (18%) có đủ số lần xuất hiện (≥30) để kiểm định đáng
tin. 33 từ khóa có <10 lần xuất hiện — với các từ này, kiểm định chi-square/Fisher gần
như không có khả năng phát hiện hiệu ứng dù nó tồn tại.

**Hàm ý:** Kết quả "0/71 từ khóa có ý nghĩa" cần được diễn giải cẩn thận: một phần là do
văn bản thật sự không có tín hiệu, nhưng một phần là do nhiều từ khóa quá hiếm để kiểm
định. Nên trình bày kèm phân bố tần suất này để trung thực về power.

## 3. Kiểm định từ khóa theo phân khúc — KHÔNG đủ power (điểm yếu rõ nhất)

- Tổng dòng kiểm định: **1.060**.
- **622 dòng (58,7%) bị loại** vì từ khóa không xuất hiện lần nào trong phân khúc.
- Trong 438 dòng thực sự kiểm định: **334 dòng (76%) có <10 lần xuất hiện**, 242 dòng có
  <5 lần.
- Số đạt ý nghĩa: **0**.

**Đánh giá:** Đây là loại kiểm định yếu nhất trong toàn luận văn. Khi chia nhỏ theo ngành,
mỗi từ khóa chỉ còn vài lần xuất hiện, khiến kiểm định gần như chắc chắn không thể đạt ý
nghĩa bất kể tín hiệu có tồn tại hay không. "0 kết quả có ý nghĩa" ở đây **không chứng minh
được** là không có tín hiệu — nó chỉ phản ánh thiếu power.

**Khuyến nghị trình bày:** Không dùng kết quả phân khúc để khẳng định "không có tín hiệu ở
ngành X". Chỉ dùng nó theo hướng: "phân tích phân khúc bị giới hạn power nghiêm trọng, và
trong giới hạn đó không phát hiện tín hiệu vững" — như một hạn chế, đồng thời củng cố
(chứ không thay thế) kết luận toàn cục.

## 4. Δ(C−A) theo phân khúc — các phân khúc nhỏ không tin cậy

| Phân khúc | n_test | Đánh giá |
|---|---|---|
| mid_cap | 250 | Đáng tin |
| large_cap | 150 | Đáng tin |
| Banking | 125 | Đáng tin |
| RealEstate | 65 | Chấp nhận được |
| Consumer / Industrial | 50 | Nhỏ |
| Energy | 40 | Nhỏ |
| Securities | 30 | Rất nhỏ |
| Transport | 25 | **Quá nhỏ — không tin cậy** |
| Technology | 15 | **Quá nhỏ — không tin cậy** |

**Đánh giá:** Đúng như nghi ngờ, hai phân khúc cho Δ(C−A) dương (Transport, Technology) là
hai phân khúc có test set nhỏ nhất (25 và 15 mẫu). Với cỡ này, một khoảng tin cậy 95% cho
độ chính xác rộng khoảng ±20 điểm phần trăm — nghĩa là Δ(C−A) ±0,04 hoàn toàn nằm trong
biên nhiễu. Các phân khúc đáng tin (n_test ≥ 150) đều cho kết quả âm.

---

## Trả lời trực tiếp câu hỏi

**"Dữ liệu đã đủ chưa?"**
Đủ cho kết luận trung tâm (so sánh mô hình toàn cục, test 400 mẫu cân bằng). Không đủ cho
các phân tích chia nhỏ (phân khúc ngành, kiểm định từng từ khóa hiếm).

**"Có kiểm định nào dùng quá ít dữ liệu, ý nghĩa thấp không?"**
Có, ba nhóm:
1. **Kiểm định từ khóa theo phân khúc** — yếu nhất (76% dựa trên <10 lần xuất hiện, 58,7%
   bị loại hoàn toàn).
2. **Δ(C−A) cho phân khúc Technology (n=15), Transport (n=25), Securities (n=30)** — không
   tin cậy, chính là nguồn của các "tín hiệu dương" giả.
3. **~33/106 từ khóa toàn cục có <10 lần xuất hiện** — power thấp ngay ở cấp toàn cục.

**Hàm ý cho luận văn:** Không cần thu thêm dữ liệu để bảo vệ kết luận chính — nó đã đủ vững.
Nhưng nên (a) trình bày minh bạch giới hạn power của các phân tích chi tiết, (b) diễn giải
các phân khúc thiếu power như hạn chế chứ không như bằng chứng, (c) nếu muốn phân tích phân
khúc mạnh hơn thì cần mở rộng corpus/thời gian hoặc gộp phân khúc lớn hơn thay vì chia nhỏ.

---

## Nguồn
- `experiments/assess_data_adequacy.py` — script tái lập số liệu này
- `data/aggregated/master_with_labels.csv`, `reports/keyword_significance.csv`,
  `reports/segmentation_keyword_sig.csv`, `reports/segment_test_sizes.csv`
