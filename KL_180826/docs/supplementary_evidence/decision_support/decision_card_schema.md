# Decision Card Schema

## 1. Mục đích

Decision card là bản ghi quyết định có cấu trúc, được LLM tạo từ evidence pack. Card giúp người dùng hiểu tín hiệu ML, luận điểm đầu tư, rủi ro và điều kiện cần theo dõi.

Decision card không phải khuyến nghị đầu tư chắc chắn. Đây là tài liệu hỗ trợ ra quyết định và phục vụ hậu kiểm.

## 2. Nguyên tắc

1. Chỉ dùng evidence pack.
2. Không thêm dữ kiện ngoài evidence.
3. Không dự báo giá tuyệt đối.
4. Không cam kết lợi nhuận.
5. Mọi luận điểm chính cần dẫn evidence ID.
6. Nếu evidence thiếu hoặc yếu, phải ghi rõ.
7. Tách decision card ban đầu khỏi outcome review.

## 3. Schema markdown

```markdown
# Decision Card: {ticker} — {decision_date}

## 1. Tóm tắt tín hiệu

- Trạng thái: {Buy Candidate / Watchlist / Avoid / Review Required}
- Xác suất tăng theo ML: {pred_proba_up}
- Rank trong kỳ: {rank_in_period}
- Kỳ nắm giữ dự kiến: {holding_horizon}
- Mức tin cậy dữ liệu: {data_quality_summary}

## 2. Luận điểm đầu tư chính

{1-2 đoạn, chỉ dựa trên ML signal + technical drivers + news evidence.}

Evidence: {N001, D001, ...}

## 3. Yếu tố hỗ trợ

1. {supporting_factor_1} — Evidence: {id}
2. {supporting_factor_2} — Evidence: {id}
3. {supporting_factor_3} — Evidence: {id}

## 4. Yếu tố cần lưu ý / rủi ro

1. {risk_1} — Evidence: {id hoặc data_quality_flag}
2. {risk_2} — Evidence: {id hoặc data_quality_flag}
3. {risk_3} — Evidence: {id hoặc data_quality_flag}

## 5. Trigger theo dõi

- ML probability giảm dưới {threshold}.
- Rank rơi khỏi Top-K.
- `pred_label` chuyển sang 0.
- Chỉ báo kỹ thuật đảo chiều: {technical_trigger}.
- Xuất hiện tin mới trái chiều: {news_trigger}.
- Drawdown vượt {drawdown_threshold}.

## 6. Thời điểm review

- Review định kỳ: {review_date_or_period}
- Review sớm nếu bất kỳ trigger nào được kích hoạt.

## 7. Kết luận hỗ trợ quyết định

{Nên trình bày thận trọng: “có thể đưa vào danh sách xem xét”, “cần theo dõi thêm”, “không đủ evidence”.}

## 8. Disclaimer

Decision card này phục vụ mục tiêu học thuật và hỗ trợ phân tích, không phải khuyến nghị đầu tư. Nhà đầu tư tự chịu trách nhiệm với quyết định cuối cùng.
```

## 4. Schema JSON

```json
{
  "decision_id": "2025Q1_FPT_001",
  "ticker": "FPT",
  "decision_date": "2025-03-31",
  "status": "Buy Candidate",
  "ml_summary": {
    "pred_proba_up": 0.73,
    "rank_in_period": 3,
    "signal_class": "Buy Candidate"
  },
  "investment_thesis": {
    "text": "...",
    "evidence_refs": ["D001", "N001"]
  },
  "supporting_factors": [
    {
      "factor": "Động lượng kỹ thuật tích cực",
      "evidence_refs": ["D001", "D002"]
    }
  ],
  "risks": [
    {
      "risk": "Tin tức gần đây chưa đủ dày để xác nhận bối cảnh định tính",
      "evidence_refs": ["Q001"]
    }
  ],
  "monitoring_triggers": [
    "pred_proba_up < 0.55",
    "rank_in_period > 10",
    "drawdown > 8%",
    "negative_news_event appears"
  ],
  "review_plan": {
    "scheduled_review": "next_quarter_end",
    "early_review_if_triggered": true
  },
  "decision_support_summary": "Có thể đưa vào danh sách xem xét, nhưng cần theo dõi trigger kỹ thuật và tin tức mới.",
  "limitations": [
    "Không phải khuyến nghị đầu tư",
    "LLM chỉ dùng evidence pack",
    "Không chứa outcome tương lai"
  ]
}
```

## 5. Trường bắt buộc

| Trường | Bắt buộc | Ghi chú |
|---|---:|---|
| ticker | Có | Mã cổ phiếu |
| decision_date | Có | Ranh giới point-in-time |
| status | Có | Buy Candidate / Watchlist / Avoid / Review Required |
| ml_summary | Có | Probability, rank, signal |
| investment_thesis | Có | Phải có evidence refs |
| supporting_factors | Có | Có thể rỗng nếu evidence yếu |
| risks | Có | Luôn phải có ít nhất 1 rủi ro |
| monitoring_triggers | Có | Điều kiện xem xét lại |
| review_plan | Có | Review date/horizon |
| disclaimer | Có | Không phải khuyến nghị đầu tư |

## 6. Outcome review schema riêng

Outcome review không được nhập vào decision card ban đầu. Sau holding period, tạo record riêng:

```json
{
  "decision_id": "2025Q1_FPT_001",
  "review_date": "2025-06-30",
  "realized_return": 0.08,
  "benchmark_return": 0.04,
  "excess_return": 0.04,
  "outcome": "positive",
  "thesis_assessment": "partially_supported",
  "monitoring_events": [
    {
      "date": "2025-05-10",
      "trigger": "new_positive_news",
      "action": "keep"
    }
  ],
  "lessons": [
    "ML technical signal aligned with subsequent return.",
    "News evidence helped explain thesis but was not used as predictor."
  ]
}
```

## 7. Chất lượng card cần đạt

Decision card tốt phải:

- cụ thể, không chung chung;
- không thêm thông tin ngoài evidence;
- phân biệt rõ tín hiệu định lượng và bằng chứng định tính;
- nêu rủi ro thật, không chỉ liệt kê hình thức;
- có trigger đo được;
- có thể hậu kiểm sau kỳ nắm giữ.
