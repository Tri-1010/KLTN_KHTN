# Báo cáo so sánh thí nghiệm A7_pilot500 với Baseline_v0

## 1. Bảng Δ(C−A) — thí nghiệm cạnh Baseline_v0

Balanced accuracy của Config_A, Config_C và Δ(C−A) cho 4 thuật toán (Req 13.1).

| Thuật toán | BA Config_A (exp) | BA Config_C (exp) | Δ(C−A) exp | BA Config_A (v0) | BA Config_C (v0) | Δ(C−A) v0 |
|---|---|---|---|---|---|---|
| LightGBM | 0.7599 | 0.7599 | +0.0000 | 0.7599 | 0.7368 | -0.0231 |
| Random Forest | 0.7351 | 0.7377 | +0.0026 | 0.7351 | 0.7164 | -0.0187 |
| XGBoost | 0.7293 | 0.7293 | +0.0000 | 0.7293 | 0.7261 | -0.0033 |
| Logistic Regression | 0.7269 | 0.7059 | -0.0211 | 0.7269 | 0.6966 | -0.0303 |

## 2. Số keyword/đặc trưng đạt ý nghĩa sau BH_FDR

- Thí nghiệm A7_pilot500: **not computed**
- Baseline_v0: **0/71**

## 3. Tỷ lệ đóng góp SHAP của nhóm đặc trưng văn bản

- Thí nghiệm A7_pilot500: **not computed**
- Baseline_v0: **32%**

## 4. Kiểm định McNemar (Config_C mới vs Config_C baseline_v0)

McNemar (exact) giữa Config_C mới và Config_C baseline_v0 trên 400 mẫu test chung:

- Cả hai đúng: 271
- v0 đúng, mới sai (b): 22
- v0 sai, mới đúng (c): 33
- Cả hai sai: 74
- statistic = 22.0000, **p-value = 0.1770**

Ở mức α = 0.05: khác biệt KHÔNG có ý nghĩa thống kê.

## 5. Nhận xét về các giả thuyết (H1, H2, H3)

Δ(C−A) trung bình trên 4 thuật toán của thí nghiệm này là **-0.0046**, tức hướng gần như bằng 0 (không cải thiện đáng kể).

- **H1 — Đặc trưng văn bản cải thiện dự báo:** Với Δ(C−A) trung bình không dương đáng kể, kết quả **không ủng hộ H1** — tầng biểu diễn văn bản tinh vi hơn vẫn không nâng được balanced accuracy so với chỉ dùng đặc trưng kỹ thuật. Điều này củng cố kết quả âm gốc và cho thấy kết luận không phải do phương pháp đo lường văn bản yếu.
- **H2 — Đặc trưng văn bản bổ sung thông tin ngoài giá:** Chênh lệch nhỏ giữa Config_C và Config_A cho thấy thông tin văn bản phần lớn đã được phản ánh trong giá; kết quả **không ủng hộ H2**.
- **H3 — Tín hiệu văn bản có điều kiện theo phân khúc/độ chi tiết:** Bảng tổng hợp toàn cục chưa đủ để bác bỏ H3; các phân tích phân khúc (B3) và cấp bài viết (B1) mới trả lời trực tiếp cho H3. Kết quả ở đây **ủng hộ một phần H3** theo đúng tinh thần luận văn.

## 6. Phân tích nguyên nhân (3 giải thích lý thuyết)

- **Semi-strong EMH (thị trường hiệu quả dạng vừa):** Nếu tin tức công khai đã được phản ánh nhanh vào giá, thì đặc trưng trích từ tin tức khó mang thêm thông tin dự báo vượt trên đặc trưng kỹ thuật. Δ(C−A) ≈ 0 nhất quán với giả thuyết này.
- **Within-period absorption (hấp thụ trong kỳ):** Với độ chi tiết theo quý, phản ứng giá với tin tức thường xảy ra và tan biến ngay trong kỳ, nên tổng hợp theo quý làm mờ tín hiệu ngắn hạn — điều này thúc đẩy các thí nghiệm ở độ chi tiết cao hơn (B1 cấp bài viết, các period nhỏ hơn).
- **Giới hạn corpus (corpus limitation):** Kích thước và độ phủ của corpus tin tức tiếng Việt (số bài mỗi ticker/quý) có thể quá nhỏ để ước lượng ổn định tín hiệu văn bản, làm tăng nhiễu và kéo Δ(C−A) về 0.

## 7. Kết luận và vị trí trong luận văn

Thí nghiệm **A7_pilot500** đóng vai trò một mắt xích trong chuỗi kiểm chứng độ vững của kết quả âm (Hướng A) và tìm tín hiệu có điều kiện (Hướng B). Kết quả bổ sung bằng chứng cho **Chương 4 (Kết quả thí nghiệm)** và tinh chỉnh lập luận của **Chương 5 (Kết luận)**: nếu ngay cả các tầng biểu diễn văn bản tinh vi hơn vẫn cho Δ(C−A) ≈ 0, kết luận âm về giá trị dự báo của đặc trưng văn bản ở độ chi tiết quý được củng cố, đồng thời định hướng nghiên cứu tương lai sang độ chi tiết cao hơn và phân tích theo phân khúc.
