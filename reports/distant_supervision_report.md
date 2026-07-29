# Báo cáo Distant Supervision (B1)

## 1. Phân phối nhãn nhiễu (noisy label)

Nhãn nhiễu suy ra từ suất sinh lời cửa sổ [d+1, d+3] ngày giao dịch, cắt tại ranh giới kỳ chứa ngày đăng bài (ngưỡng ±2%).

| Nhãn | Số bài | Tỷ lệ |
|---|---|---|
| negative | 6789 | 23.8% |
| neutral | 14495 | 50.8% |
| positive | 7235 | 25.4% |
| **tổng** | **28519** | 100% |

Số bài dùng huấn luyện classifier (kỳ < cutoff): **14016**. Số bài bị loại (thiếu giá / cuối kỳ không còn ngày giao dịch): **6447**.

## 2. Chất lượng bộ phân loại cấp bài viết

AUC macro one-vs-rest trên nhãn nhiễu cấp bài viết: **0.6797**.

## 3. Granularity analysis

B1 kiểm tra giả thuyết rằng tín hiệu văn bản tồn tại ở cấp độ từng bài viết nhưng bị *tổng hợp theo quý làm mờ*. Bộ phân loại được huấn luyện trên nhãn nhiễu cấp bài (distant supervision từ suất sinh lời ngắn hạn); xác suất dự đoán sau đó được gộp theo quý thành ``ds_pos_prob_mean`` và ``ds_net_sentiment``. Nếu AUC cấp bài cao hơn đáng kể so với giá trị dự báo của đặc trưng gộp theo quý (Δ(C−A) ở báo cáo so sánh B1), điều đó ủng hộ giả thuyết mất mát thông tin do tổng hợp theo kỳ (within-period absorption). Ngược lại, nếu ngay cả tín hiệu cấp bài cũng yếu, kết quả củng cố thêm kết luận âm của Hướng A.
