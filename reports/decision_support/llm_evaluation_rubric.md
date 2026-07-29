# Rubric đánh giá LLM Decision Card

## 1. Mục đích

Rubric này dùng để đánh giá chất lượng decision card do LLM tạo từ evidence pack. Mục tiêu không phải đo LLM có dự báo đúng giá hay không, mà đo LLM có hỗ trợ quyết định tốt hơn bằng cách diễn giải dữ liệu, nêu rủi ro và tạo trigger theo dõi hay không.

## 2. Thang điểm chung

| Điểm | Ý nghĩa |
|---:|---|
| 1 | Rất kém, sai hoặc không đáp ứng tiêu chí |
| 2 | Yếu, có nhiều thiếu sót |
| 3 | Đạt mức cơ bản, còn thiếu chi tiết |
| 4 | Tốt, chỉ còn lỗi nhỏ |
| 5 | Rất tốt, đầy đủ, rõ ràng, bám evidence |

## 3. Tiêu chí

### 3.1. Faithfulness — Bám sát evidence

| Điểm | Mô tả |
|---:|---|
| 1 | Nhiều luận điểm không có trong evidence pack |
| 2 | Có vài luận điểm dựa trên suy đoán |
| 3 | Phần lớn bám evidence nhưng thiếu reference hoặc diễn giải hơi rộng |
| 4 | Bám evidence tốt, có reference cho luận điểm chính |
| 5 | Tất cả luận điểm chính đều bám evidence và dẫn evidence rõ |

### 3.2. Hallucination control — Không thêm dữ kiện ngoài evidence

| Điểm | Mô tả |
|---:|---|
| 1 | Thêm dữ kiện tài chính/tin tức/outcome không có trong input |
| 2 | Có dữ kiện ngoài input nhưng không quá nhiều |
| 3 | Không có hallucination lớn nhưng có câu diễn giải quá mức |
| 4 | Không thấy hallucination đáng kể |
| 5 | Rất chặt, ghi rõ khi evidence thiếu |

### 3.3. ML explanation — Giải thích tín hiệu ML

| Điểm | Mô tả |
|---:|---|
| 1 | Chỉ nói “mô hình dự báo tăng”, không giải thích |
| 2 | Nhắc probability/rank nhưng không nêu driver |
| 3 | Có nêu probability/rank và vài driver nhưng còn chung chung |
| 4 | Giải thích rõ ML score, rank, technical drivers |
| 5 | Liên kết tốt giữa signal class, drivers, giới hạn mô hình và mức tin cậy |

### 3.4. Risk awareness — Nhận diện rủi ro

| Điểm | Mô tả |
|---:|---|
| 1 | Không nêu rủi ro hoặc chỉ nêu hình thức |
| 2 | Rủi ro chung chung, không liên quan evidence |
| 3 | Có rủi ro liên quan nhưng thiếu cụ thể |
| 4 | Rủi ro cụ thể, bám evidence/data quality |
| 5 | Rủi ro đầy đủ, phân biệt rủi ro kỹ thuật, tin tức và dữ liệu |

### 3.5. Monitoring usefulness — Trigger theo dõi

| Điểm | Mô tả |
|---:|---|
| 1 | Không có trigger |
| 2 | Trigger mơ hồ, không đo được |
| 3 | Có trigger đo được nhưng chưa đủ nhóm tín hiệu |
| 4 | Trigger rõ cho ML/rank/technical/news/drawdown |
| 5 | Trigger cụ thể, có ngưỡng, có hành động review rõ |

### 3.6. Clarity/usefulness — Rõ ràng và hữu ích

| Điểm | Mô tả |
|---:|---|
| 1 | Khó hiểu, không dùng được |
| 2 | Dài hoặc rối, thiếu cấu trúc |
| 3 | Có cấu trúc cơ bản nhưng còn chung chung |
| 4 | Rõ, dễ đọc, hữu ích cho người phân tích |
| 5 | Rất rõ, cân bằng giữa định lượng và định tính, dễ hậu kiểm |

## 4. Tổng hợp điểm

Có thể báo cáo:

- Điểm trung bình từng tiêu chí.
- Điểm trung bình toàn card.
- Tỷ lệ hallucination lớn.
- Tỷ lệ luận điểm có evidence reference.
- Tỷ lệ card có đủ trigger theo dõi.

Công thức gợi ý:

```text
overall_score = mean(
  faithfulness,
  hallucination_control,
  ml_explanation,
  risk_awareness,
  monitoring_usefulness,
  clarity_usefulness
)
```

## 5. So sánh baseline

Nên chấm ba loại card:

1. **Template rule-based**: không LLM, điền thông tin theo mẫu cố định.
2. **LLM ML-only**: LLM chỉ có probability/rank/technical drivers.
3. **LLM full evidence**: LLM có ML + technical + news evidence + data quality flags.

Kỳ vọng hợp lý:

- Template có hallucination thấp nhưng thesis nghèo.
- LLM ML-only giải thích kỹ thuật tốt hơn nhưng thiếu bối cảnh.
- LLM full evidence có thể hữu ích nhất nếu hallucination được kiểm soát.

## 6. Cảnh báo diễn giải

Không được kết luận “LLM cải thiện lợi nhuận đầu tư” chỉ từ rubric. Rubric chỉ đánh giá chất lượng hỗ trợ quyết định. Nếu muốn kết luận về return, cần backtest riêng với rule rõ ràng và tránh leakage.

## 7. Biểu mẫu chấm

| decision_id | card_type | faithfulness | hallucination_control | ml_explanation | risk_awareness | monitoring_usefulness | clarity_usefulness | overall | major_issue |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2025Q1_FPT_001 | LLM full evidence | 4 | 5 | 4 | 4 | 4 | 5 | 4.33 | None |
