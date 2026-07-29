# Chương bổ sung: Semantic News Materiality Study

> Bản tích hợp kết quả từ `multi_llm_evidence_extraction/`. Mục tiêu: cập nhật phạm vi luận văn từ keyword/news-count thuần túy sang phân tích tin tức có ngữ cảnh: relevance, materiality, direction, event type, evidence span và outcome review. Nội dung phục vụ nghiên cứu, không phải khuyến nghị đầu tư.

---

## 1. Điều chỉnh phạm vi nghiên cứu

Các thí nghiệm trước cho thấy đặc trưng keyword/news-count chưa cải thiện dự báo ổn định so với technical-only baseline. Kết quả này không chứng minh tin tức vô dụng, mà chỉ ra biểu diễn keyword-frequency thiếu ngữ cảnh: một bài có từ khóa tích cực chưa chắc liên quan trực tiếp tới ticker; một bài có sentiment mạnh chưa chắc trọng yếu; một tin thị trường chung có thể bị gán nhầm thành tín hiệu riêng cho cổ phiếu.

Vì vậy, luận văn bổ sung hướng **Semantic News Materiality Study**:

- thiết kế schema semantic-news cho tin chứng khoán Việt Nam;
- tạo pseudo-label bằng AI-assisted annotation;
- đo agreement giữa annotators;
- so sánh keyword/rule baseline với semantic labels;
- tạo semantic aggregate features;
- kiểm tra exploratory bằng event-window audit, target outperform T+20 và Top-K simulation;
- sinh evidence cards và outcome review để minh họa audit trail.

LLM/AI chỉ đóng vai trò công cụ annotation/extraction tạm thời. Pseudo-label không được xem là ground truth.

---

## 2. Dữ liệu và annotation protocol

Tập annotation gồm 150 bài tin được chọn stratified từ corpus tin tức đã crawl/full-text. Mẫu bao phủ bảy nhóm: earnings/business result, dividend/capital, debt/legal/governance risk, project/business expansion, market/sector/macro, generic/company announcement và noisy/low-confidence match.

Schema annotation gồm các trường chính:

- `ticker_relevance`: direct, indirect, market_wide, irrelevant, unclear;
- `materiality`: high, medium, low, unclear;
- `direction`: support, risk, neutral, mixed, unclear;
- `event_type`: earnings, dividend, capital, debt, legal, governance, project, product, ma, analyst, market, macro, sector, other, unclear;
- `materiality_score`, `expected_impact_score`, `uncertainty_score`, `novelty_score`;
- `time_horizon`, `evidence_span`, `reasoning_confidence`, `requires_human_review`, `data_quality_flags`.

Prompt annotation chặn future/outcome leakage: không đưa future return, target label, prediction, outcome review hoặc excess return vào input. `evidence_span` phải là đoạn trích chính xác từ bài báo; nếu không có bằng chứng rõ, giá trị là `null` và mẫu bị gắn `requires_human_review=true`.

---

## 3. Kết quả pseudo-labeling và agreement

Đã chạy live annotation bằng DeepSeek cho 2 annotators:

| Annotator | Provider | Model | Rows OK | Errors |
|---|---|---|---:|---:|
| A | DeepSeek | `deepseek-chat` | 150 | 0 |
| B | DeepSeek | `deepseek-chat` | 150 | 0 |

Annotator C được thử chạy nhưng provider trả lỗi `DeepSeek API error 402: Insufficient Balance`, nên không dùng cho consensus. Theo protocol, không sinh fake labels; consensus dùng 2 annotators A/B.

Agreement A-B cao ở các field chính:

| Field | Agreement | Cohen Kappa |
|---|---:|---:|
| ticker_relevance | 0.9867 | 0.9408 |
| materiality | 0.9467 | 0.9183 |
| direction | 0.9667 | 0.9518 |
| event_type | 0.9733 | 0.9695 |
| time_horizon | 0.9267 | 0.8868 |

Consensus sinh 150 rows. Có 48/150 rows cần human review. Missing evidence span rate là 2.67%.

Diễn giải: agreement cao cho thấy schema/prompt ổn định trên sample này, nhưng vì annotators đều là AI và cùng provider, kết quả vẫn chỉ là pseudo-label chất lượng tham chiếu, chưa phải human ground truth.

---

## 4. Manual sanity check

Manual sanity check chọn 21 bài từ các nhóm: high disagreement, high materiality, mixed/unclear direction, low match confidence và random control. Đây là kiểm tra chất lượng nhỏ, không phải gán nhãn chuẩn.

Kết quả sheet đã điền các cột:

- `human_relevance_ok`;
- `human_materiality_ok`;
- `human_direction_ok`;
- `human_event_type_ok`;
- `human_evidence_span_ok`;
- `human_error_notes`.

Các lỗi chính cần chú ý:

- evidence span thiếu/không khớp ở vài mẫu;
- disagreement về event type hoặc time horizon;
- direction mixed/unclear cần giữ trong human review queue;
- một số tin market-wide hoặc UNKNOWN ticker cần kiểm tra relevance khi đưa vào downstream analysis.

---

## 5. Keyword/rule baseline vs semantic pseudo labels

Rule baseline được sinh từ keyword groups hiện có và `compute_raw_counts()` với longest-first masking. Các nhãn rule gồm:

- `rule_sentiment`;
- `rule_direction`;
- `rule_event_type`;
- `rule_materiality`;
- `rule_relevance`.

So sánh với semantic pseudo labels cho thấy keyword/rule phù hợp cho nhận diện event đơn giản nhưng yếu ở materiality và direction. Nguyên nhân chính:

1. keyword thiếu ngữ cảnh phủ định hoặc quy mô sự kiện;
2. keyword không đo được materiality tài chính;
3. tin market-wide dễ bị hiểu thành direct signal;
4. bài thủ tục/boilerplate có ticker nhưng impact thấp;
5. direction mixed khó biểu diễn bằng rule một chiều.

Kết quả này củng cố negative finding cũ: news không nên chỉ được biểu diễn bằng frequency/sentiment thô.

---

## 6. Semantic features, event-window audit và ML outperform

Semantic labels được aggregate thành features theo ticker/date và ticker/period:

- `direct_news_count`;
- `high_materiality_count`;
- `medium_materiality_count`;
- `low_relevance_ratio`;
- `support_count`, `risk_count`, `mixed_direction_count`;
- `avg_materiality_score`, `avg_uncertainty_score`, `avg_novelty_score`;
- `event_earnings_count`, `event_debt_legal_count`;
- `high_disagreement_ratio`;
- `days_since_high_materiality_news`.

Generated artifacts:

| Artifact | Rows |
|---|---:|
| `semantic_features_daily.csv` | 93,824 |
| `semantic_features_period.csv` | 1,521 |
| `event_window_outcomes.csv` | 600 |
| `outperform_targets.csv` | 93,824 |
| `ml_panel_outperform.csv` | generated |
| `ml_predictions_outperform.csv` | generated |

Target mới:

```text
excess_return_T20 = stock_return_T20 - VNINDEX_return_T20
label_outperform_T20 = 1 nếu excess_return_T20 > 0, ngược lại 0
```

ML experiment dùng temporal split, không random split. Feature sets:

- A: technical-only;
- B: technical + keyword/news-count;
- C: technical + semantic pseudo-label features;
- D: technical + keyword + semantic.

Kết quả được diễn giải exploratory. Nếu semantic không cải thiện rõ, đây vẫn là negative finding: semantic labels hữu ích để phân tích noise và audit evidence, nhưng chưa đủ chứng minh predictive gain ổn định.

---

## 7. Top-K simulation có benchmark

Top-K simulation dùng `round_trip_cost = 0.50%`, Top-5 và Top-10 theo probability outperform. Benchmark đã bổ sung:

- VNINDEX;
- equal-weight universe;
- deterministic random Top-K;
- technical-only Top-K;
- keyword/news-count Top-K.

Metrics báo cáo:

- cumulative net return;
- mean net return;
- mean net excess return;
- Sharpe;
- max drawdown;
- hit rate;
- average turnover.

Top-K là secondary/optional analysis, không dùng làm claim chính và không được viết như chiến lược giao dịch thực tế.

---

## 8. Evidence cards và outcome review

Đã chọn 5 case study candidates và sinh evidence cards. Mỗi card gồm ticker/date, case pattern, relevance/materiality/direction, evidence span, claim, data-quality flags và limitation. Outcome review hậu kiểm theo T+20 raw return, gắn nhãn:

- confirmed;
- contradicted;
- unresolved;
- confounded;
- not_price_relevant.

Outcome review là post-hoc, không dùng trong prompt annotation và không được đưa vào evidence card ban đầu. Mục tiêu là audit claim/evidence, không chứng minh dự báo chắc chắn.

---

## 9. Cập nhật đóng góp luận văn

Sau Semantic News Materiality Study, đóng góp luận văn có thể viết lại thành:

1. Xây dựng corpus tin tức chứng khoán Việt Nam nhiều nguồn và pipeline matching/full-text.
2. Chứng minh keyword/news-count/sentiment thô có giới hạn khi dùng làm predictor trực tiếp.
3. Đề xuất schema semantic-news gồm relevance, materiality, event type, direction và evidence span.
4. Thiết kế AI-assisted pseudo-labeling protocol có schema validation, agreement, consensus và human review flags.
5. So sánh keyword/rule baseline với semantic pseudo labels để chỉ ra lỗi materiality/relevance/direction.
6. Kiểm tra exploratory semantic signal bằng event windows, outperform target và Top-K simulation có cost.
7. Minh họa evidence card/outcome review để tăng tính truy vết và giảm overclaim trong phân tích tin tức tài chính.

---

## 10. Hạn chế và hướng phát triển

Hạn chế:

- Pseudo labels không phải ground truth.
- Annotator C không hoàn tất do provider insufficient balance; consensus hiện dựa trên 2 annotators.
- Manual sanity check nhỏ, chưa thay thế human-labeled benchmark.
- Semantic features mới sinh từ sample/pseudo-label pipeline, cần mở rộng corpus/human validation để tăng độ tin cậy.
- Top-K simulation là mô phỏng lịch sử, chưa mô phỏng đầy đủ slippage, liquidity, corporate actions và market impact.

Hướng phát triển:

- mở rộng human-labeled semantic dataset;
- thêm annotator/model khác provider để giảm correlated error;
- active learning cho các row disagreement/high review;
- event ontology chi tiết hơn theo ngành;
- rolling evaluation nhiều giai đoạn;
- dashboard evidence audit cho analyst, không phải recommender.

---

## 11. Kết luận ngắn để đưa vào Chương 5

Kết quả bổ sung cho thấy chuyển từ keyword-frequency sang semantic materiality giúp phân tích chất lượng tin tức rõ hơn: biết tin nào liên quan trực tiếp, tin nào trọng yếu, direction nào không chắc chắn và evidence nào cần review. Tuy semantic labels chưa được xem là ground truth và chưa được claim tạo alpha, pipeline này tạo đóng góp phương pháp rõ ràng cho bài toán tin tức chứng khoán Việt Nam: controlled pseudo-labeling, agreement analysis, rule baseline comparison, outcome audit và evidence-card traceability.
