# Monitoring & Outcome Review Cases

## 1. Mục đích

Tài liệu này mô tả cách chọn và trình bày các case study cho module monitoring và outcome review. Đây là phần giúp luận văn chứng minh hệ thống không dừng ở bước tạo khuyến nghị, mà có khả năng theo dõi và hậu kiểm vòng đời quyết định.

## 2. Monitoring rules đề xuất

| Nhóm trigger | Điều kiện ví dụ | Trạng thái |
|---|---|---|
| ML probability | `pred_proba_up < 0.55` hoặc giảm > 0.15 so với lúc decision | Review Required |
| Rank | Rơi khỏi Top-K hoặc rank giảm > 10 bậc | Watch / Review Required |
| Label | `pred_label` chuyển từ 1 sang 0 | Review Required |
| Technical | MACD histogram chuyển âm, price_vs_sma20 < 0, RSI suy yếu mạnh | Watch / Review Required |
| Drawdown | Giá giảm > 8–10% từ decision price | Review Required |
| News | Tin mới có event type tiêu cực hoặc trái với thesis | Watch / Review Required |
| Data quality | Ticker matching nghi ngờ hoặc coverage quá thấp | Watch |
| Time | Đến cuối holding period | Outcome Review |

## 3. Outcome review schema

```markdown
# Outcome Review: {decision_id}

## 1. Decision ban đầu

- Ticker: {ticker}
- Decision date: {decision_date}
- Trạng thái ban đầu: {status}
- ML probability/rank: {ml_signal}
- Thesis tóm tắt: {thesis_summary}

## 2. Kết quả sau holding period

- Realized return: {realized_return}
- Benchmark return: {benchmark_return}
- Excess return: {excess_return}
- Outcome: Positive / Neutral / Negative

## 3. Monitoring events

| Date | Trigger | Evidence | Action |
|---|---|---|---|
| ... | ... | ... | Keep / Watch / Review Required |

## 4. Thesis assessment

- Điểm đúng:
- Điểm sai hoặc thiếu:
- Evidence ban đầu hữu ích:
- Evidence ban đầu gây nhiễu:

## 5. Bài học

- Về ML signal:
- Về news evidence:
- Về LLM card:
- Về monitoring rules:
```

## 4. Case study đề xuất

### Case A — ML đúng, thesis được hỗ trợ

Mục tiêu: minh họa hệ thống tạo decision card tốt khi ML signal, technical drivers và news evidence cùng chiều.

Điều kiện chọn:

- `pred_label = 1`.
- `pred_proba_up` cao hoặc Top-K.
- realized return sau holding period dương.
- Có tin tức hỗ trợ trước decision date.

Điểm cần trình bày:

- Thesis ban đầu dựa trên technical drivers và evidence tin tức.
- Monitoring không kích hoạt cảnh báo tiêu cực lớn.
- Outcome review xác nhận decision có excess return dương.

### Case B — ML sai, monitoring cảnh báo được

Mục tiêu: minh họa giá trị của monitoring.

Điều kiện chọn:

- Decision ban đầu là Buy Candidate.
- realized return âm hoặc thấp hơn benchmark.
- Trong kỳ có trigger: rank giảm, technical đảo chiều, drawdown hoặc tin tiêu cực.

Điểm cần trình bày:

- Thesis ban đầu có căn cứ tại thời điểm decision.
- Monitoring phát hiện tín hiệu suy yếu.
- Outcome review phân tích warning có đến sớm hơn outcome xấu hay không.

### Case C — ML đúng nhưng news evidence nghèo

Mục tiêu: minh họa hệ thống không overclaim khi evidence định tính yếu.

Điều kiện chọn:

- ML signal tích cực.
- realized return dương.
- `news_coverage = low` hoặc không có tin gần decision.

Điểm cần trình bày:

- Decision card chỉ nên gọi là technical candidate.
- LLM phải ghi rõ thiếu evidence tin tức.
- Outcome tốt không đồng nghĩa news layer hữu ích.

### Case D — News trái chiều với ML

Mục tiêu: minh họa vai trò cân bằng rủi ro của evidence layer.

Điều kiện chọn:

- ML signal tích cực.
- Có tin tiêu cực trước hoặc ngay sau decision.
- Outcome có thể dương hoặc âm.

Điểm cần trình bày:

- Decision card không nên bỏ qua risk evidence.
- Monitoring nên tăng trạng thái Watch/Review.
- Outcome review đánh giá tin trái chiều có thực sự dự báo rủi ro không.

### Case E — Tín hiệu đảo chiều sau khuyến nghị

Mục tiêu: minh họa vòng đời update.

Điều kiện chọn:

- Ban đầu Top-K.
- Lần cập nhật sau rơi khỏi Top-K hoặc `pred_label` đổi sang 0.

Điểm cần trình bày:

- Update prompt tạo trạng thái Review Required.
- So sánh decision nếu không monitoring và nếu có monitoring.
- Hậu kiểm xem trigger có giảm rủi ro không.

## 5. Bảng tổng hợp case studies

| Case | Ticker | Decision period | Initial status | Trigger occurred | Outcome | Lesson |
|---|---|---|---|---|---|---|
| A | STB (`2025Q2_STB_01`) | 2025Q2 | Buy Candidate | Không có major negative flag trong card baseline; có earnings-related news trước decision date | Positive, realized return 0.2763 | ML signal mạnh và evidence tin tức có thể hỗ trợ thesis |
| B | DPM (`2026Q1_DPM_03`) | 2026Q1 | Buy Candidate | `price_vs_sma20` âm; nhiều news tag `legal_risk` quanh BCTC kiểm toán | Negative/neutral, realized return -0.0276 | Monitoring flags giúp yêu cầu review dù ML probability cao |
| C | KDH (`2025Q3_KDH_04`) | 2025Q3 | Buy Candidate | Technical drivers mixed: RSI weak/neutral, `price_vs_sma20` âm; news thiên về giao dịch/quỹ | Positive, realized return 0.0461 | Outcome dương không đồng nghĩa thesis định tính mạnh; cần tránh overclaim |
| D | VND (`2025Q2_VND_05`) | 2025Q2 | Buy Candidate | News tag `debt_risk`/`capital` liên quan phát hành trái phiếu; MACD âm | Positive, realized return 0.4522 | Evidence layer giúp nêu rủi ro trái chiều ngay cả khi outcome tốt |
| E | VBB (`2025Q4_VBB_05`) | 2025Q4 | Buy Candidate | RSI weak/neutral, MACD âm, current return âm; realized return âm | Negative/neutral, realized return -0.0526 | Cần update/review required khi nhiều technical flags yếu xuất hiện |

## 6. Cách chọn case từ dữ liệu hiện có

Nguồn dữ liệu:

- `reports/signals.csv`: ticker, quarter_id, pred_label, pred_proba_up, period_return.
- `data/features/technical_features.csv`: technical snapshot theo kỳ.
- `data/news/matched/all_news_matched.csv`: news evidence.
- `reports/backtest_performance.csv`: benchmark/strategy performance.
- `reports/walk_forward_results.csv`: stability.

Quy trình:

1. Chọn từng kỳ test.
2. Sort theo `pred_proba_up` để lấy Top-K.
3. Join với period return để phân loại outcome.
4. Join với technical features cùng kỳ.
5. Lọc news có `published_at <= decision_date`.
6. Tạo evidence pack.
7. Tạo decision card.
8. Sau holding period, tạo outcome review.

## 7. Cảnh báo leakage

- Không dùng tin sau `decision_date` trong decision card ban đầu.
- Không dùng `period_return` trong prompt tạo thesis ban đầu.
- Monitoring events sau decision phải tách riêng khỏi initial evidence.
- Outcome review phải ghi rõ đây là bước hậu kiểm sau khi đã biết kết quả.

## 8. Cách viết vào luận văn

Trong chương 4, không cần trình bày quá nhiều case. Nên chọn 3–5 case tiêu biểu:

1. Một case thành công.
2. Một case thất bại có warning.
3. Một case thiếu news coverage.
4. Một case news trái chiều.
5. Một case update/review required.

Mỗi case nên có:

- bảng evidence pack rút gọn;
- decision card tóm tắt;
- monitoring timeline;
- outcome review;
- bài học.
