# Đề cương chi tiết: Đặc trưng tin tức có xét độ liên quan/trọng yếu và outcome review cho hỗ trợ phân tích cổ phiếu Việt Nam

## 0. Định vị hướng nghiên cứu

Hướng này **không phải stock recommender**, **không phải project LLM summary**, và **không claim LLM tạo alpha**.

Trọng tâm luận văn là:

> Đánh giá cách biểu diễn tin tức chứng khoán Việt Nam bằng các đặc trưng có ngữ cảnh như độ liên quan, mức độ trọng yếu, loại sự kiện, chiều tác động và đoạn bằng chứng; sau đó kiểm tra các đặc trưng này trong một pipeline hỗ trợ phân tích có ML signal, evidence card và outcome review.

Nói ngắn:

```text
ML signal yếu/ban đầu
        ↓
Decision candidate
        ↓
News retrieval trước decision_date
        ↓
LLM/Rule extract:
  - relevance
  - materiality
  - event type
  - direction
  - evidence span
        ↓
Evidence Card / Claim Ledger
        ↓
Decision Card
        ↓
Outcome Review:
  - decision đúng/sai
  - evidence nào hữu ích
  - evidence nào nhiễu
```

LLM/AI chỉ là **công cụ annotation/extraction tạm thời** để giải quyết bài toán chưa có human labels. Nội dung chính vẫn là luận văn về **tin tức, đặc trưng semantic, ML signal audit, và decision-support evaluation**.

---

## 1. Tên đề tài đề xuất

### Tên khuyến nghị

**Đánh giá đặc trưng tin tức có xét độ liên quan và trọng yếu trong hỗ trợ phân tích cổ phiếu Việt Nam**

### Tên cân bằng ML + news + support

**Hệ thống hỗ trợ phân tích cổ phiếu Việt Nam dựa trên tín hiệu học máy và đặc trưng tin tức có xét độ liên quan, trọng yếu**

### Tên nhấn hướng nghiên cứu mới

**Từ đặc trưng từ khóa đến đặc trưng trọng yếu: đánh giá vai trò của tin tức trong hỗ trợ phân tích cổ phiếu Việt Nam**

### Tên tiếng Anh tham khảo

**Evaluating Relevance- and Materiality-Aware News Features for Vietnamese Stock Analysis and Decision Support**

---

## 2. Vì sao cần hướng này?

Các hướng phổ biến đã có nhiều:

1. Dự báo giá/tăng giảm bằng technical indicators.
2. Thêm keyword/sentiment/news count vào ML model.
3. Dùng FinBERT/BERT/LLM để phân loại sentiment.
4. Dùng LLM/RAG để tóm tắt tin tức.
5. Làm dashboard lọc cổ phiếu + tin tức + chỉ báo kỹ thuật.

Nếu chỉ làm:

> ML lọc cổ phiếu + tin tức + LLM tóm tắt

thì dễ trùng với project có sẵn trên GitHub và khó chứng minh tính mới.

Kết quả hiện tại của dự án cũng cho thấy: keyword/news/sentiment/LLM sentiment chưa cải thiện dự báo ổn định. Nhưng điều này không chứng minh tin tức vô dụng. Nó chỉ ra rằng **cách biểu diễn tin tức dạng keyword/sentiment/count thiếu ngữ cảnh**.

Do đó, hướng mới đặt câu hỏi:

> Tin tức thất bại khi làm feature dự báo vì thiếu những thuộc tính nào? Relevance, materiality, event type, direction và evidence span có giúp phân tích tin tức tốt hơn keyword/sentiment không? Các đặc trưng này có tạo tín hiệu outcome hợp lý hơn không?

---

## 3. Tính mới và khác biệt so với hướng phổ biến

### 3.1. Không claim “chưa ai làm”

Luận văn không cần claim phát minh thuật toán LLM mới. Tính mới nằm ở **tổ hợp nghiên cứu phù hợp bối cảnh Việt Nam**:

1. Dữ liệu tin tức chứng khoán tiếng Việt, nhiều nguồn, full-text.
2. Negative findings có hệ thống về keyword/news-as-feature.
3. Schema semantic-news gồm relevance, materiality, event type, direction, uncertainty, novelty, evidence span.
4. AI-assisted pseudo-labeling có agreement/disagreement, không xem là ground truth.
5. So sánh keyword/rule baseline với semantic pseudo labels.
6. ML target được nâng từ up/down tuyệt đối sang **market-adjusted outperform T+20**.
7. Đánh giá lọc cổ phiếu bằng ranking, Precision@K, Top-K simulation và transaction cost.
8. Semantic signal audit bằng outcome windows T+1/T+5/T+20.
9. Evidence card/claim ledger có point-in-time cutoff, evidence ID, data-quality flags.
10. Outcome review framework để hậu kiểm claim, ML signal và evidence.

### 3.2. Bảng định vị novelty

| Nhóm hướng phổ biến | Thường làm | Hạn chế | Luận văn này bổ sung |
|---|---|---|---|
| Technical stock prediction | OHLCV, indicators, classifier/regressor | Thường dự báo up/down tuyệt đối, ít phân tích tin tức | Dùng market-adjusted outperform target, ranking/Top-K simulation, rồi kiểm tra semantic news features |
| News sentiment prediction | Positive/negative sentiment | Sentiment không đồng nghĩa materiality | Thêm relevance, materiality, event type, direction |
| Keyword/news-count features | Đếm tin, đếm keyword | False positive, ticker mismatch, thiếu ngữ cảnh | Phân tích noise bằng semantic labels |
| FinBERT/LLM sentiment | Phân loại sentiment tài chính | Vẫn xoay quanh tone/polarity | Tập trung vào evidence span và trọng yếu |
| LLM summarization/RAG | Tóm tắt tin, hỏi đáp | Khó kiểm định, dễ giống demo | Schema hóa thành labels + evidence ID + agreement |
| Event extraction | Nhận diện loại sự kiện | Chưa chắc đo relevance/materiality theo ticker | Gắn event với ticker relevance và decision context |
| Dashboard/recommender | Hiển thị tín hiệu/mua bán | Dễ overclaim decision | Evidence card + outcome review, không khuyến nghị mua/bán |

### 3.3. Điểm khác cụ thể

Hướng này khác project phổ biến vì:

- không chỉ sentiment;
- không chỉ summary;
- không chỉ stock prediction;
- có point-in-time cutoff;
- có evidence IDs;
- có materiality/relevance;
- có claim-vs-evidence audit;
- có outcome review;
- có phân tích error taxonomy của news-as-feature.

---

## 4. Vai trò của ML trong luận văn

Đóng góp chính là **semantic representation và khả năng truy vết bằng chứng** cho tin tức chứng khoán Việt Nam. ML chỉ là phân tích secondary/exploratory để kiểm tra xem cách biểu diễn này có tạo chênh lệch lọc/xếp hạng so với keyword/news-count trong mẫu lịch sử hay không; kết quả không chứng minh alpha, chiến lược giao dịch hoặc quan hệ nhân quả.

### 4.1. Phân tích ML secondary: market-adjusted outperform classification

Không nên chỉ dùng label tăng/giảm tuyệt đối:

```text
label = 1 nếu stock_return_T+20 > 0
label = 0 nếu stock_return_T+20 <= 0
```

Label này dễ bị thị trường chung chi phối. Đề xuất dùng label chính:

```text
excess_return_T20 = stock_return_T20 - VNINDEX_return_T20
label_outperform_T20 = 1 nếu excess_return_T20 > 0
label_outperform_T20 = 0 nếu excess_return_T20 <= 0
```

Ý nghĩa:

> Mô hình không chỉ hỏi cổ phiếu có tăng không, mà hỏi cổ phiếu có tốt hơn VNINDEX trong T+20 ngày giao dịch không.

Đây là target phù hợp hơn cho mục tiêu lọc/xếp hạng cổ phiếu.

### 4.2. Horizon dự báo

Horizon chính:

- `T+20` trading days: xấp xỉ 1 tháng, phù hợp hơn cho stock selection.

Horizon phụ:

- `T+5` trading days: phản ứng ngắn hạn với tin tức.
- `T+60` trading days: chỉ dùng cho event có `time_horizon = medium_term` nếu đủ dữ liệu.

### 4.3. Feature sets cần so sánh

Luận văn nên có các nhóm feature sau:

| Model | Feature set | Mục đích |
|---|---|---|
| A | Technical-only | baseline định lượng |
| B | Technical + keyword/news-count/sentiment | baseline tin tức truyền thống |
| C | Technical + semantic pseudo-label features | kiểm tra relevance/materiality/event/direction |
| D | Technical + keyword + semantic | kiểm tra bổ sung nếu cần |

Technical features gồm RSI, MACD, SMA/EMA, Bollinger, return lag, volatility, volume change, price-vs-SMA.

Semantic features gồm:

- `direct_news_count`
- `high_materiality_count`
- `support_count`
- `risk_count`
- `mixed_direction_count`
- `avg_materiality_score`
- `avg_uncertainty_score`
- `avg_novelty_score`
- `high_disagreement_ratio`
- `days_since_high_materiality_news`
- `event_earnings_count`
- `event_debt_legal_count`
- `low_relevance_ratio`

### 4.4. Model đề xuất

Model baseline:

- Logistic Regression.

Model tree-based:

- Random Forest.
- LightGBM hoặc XGBoost.
- CatBoost nếu cần xử lý categorical/robustness.

Nếu làm regression phụ:

- Ridge/Linear Regression baseline.
- LightGBM Regressor hoặc XGBoost Regressor.

### 4.5. Regression/ranking phụ: excess return

Ngoài classification 0/1, có thể thêm target phụ:

```text
excess_return_T20 = stock_return_T20 - VNINDEX_return_T20
```

Mục tiêu không phải dự báo return chính xác tuyệt đối, mà kiểm tra khả năng **xếp hạng**.

Metric phụ:

- MAE/RMSE: báo cáo nhưng không đặt nặng.
- Spearman rank correlation.
- Information Coefficient.
- average excess return theo probability/score decile.
- top quantile return.

### 4.6. Top-K stock filtering simulation

Để đáp ứng mục tiêu “lọc cổ phiếu”, cần thêm mô phỏng Top-K đơn giản.

Quy trình:

```text
Mỗi rebalance date:
  1. Tính feature tại thời điểm t0.
  2. Model dự báo probability outperform hoặc expected excess return.
  3. Rank cổ phiếu trong universe.
  4. Chọn Top-K.
  5. Equal-weight portfolio.
  6. Giữ T+20 ngày giao dịch hoặc đến kỳ rebalance sau.
  7. Trừ transaction cost.
  8. So sánh benchmark.
```

K đề xuất:

- Top-5.
- Top-10.

Benchmark:

- VNINDEX.
- Equal-weight universe.
- Random Top-K.
- Technical-only Top-K.
- Keyword/news-count Top-K.

Transaction cost tối thiểu:

- 0.15%–0.25% mỗi chiều; hoặc
- 0.30%–0.50% round-trip.

Nên dùng một mức chính, ví dụ:

```text
round_trip_cost = 0.50%
```

Metric portfolio:

- cumulative return;
- excess return vs VNINDEX;
- Sharpe;
- max drawdown;
- hit rate by rebalance period;
- turnover;
- average return per trade/period.

### 4.7. ML signal làm decision candidate

Output từ mô hình:

```text
ticker + date/period + pred_proba_outperform + rank + feature group
```

Dùng để tạo:

- `Analysis Candidate`;
- `Review Candidate`;
- `Decision Candidate`.

Không dùng “Buy Candidate” nếu muốn tránh overclaim.

### 4.8. Semantic signal audit trong ML/outcome setting

Ngoài model classification, cần kiểm tra trực tiếp:

1. Tin `direct` và `high materiality` có phản ứng giá/khối lượng rõ hơn tin `market_wide` hoặc `low materiality` không?
2. Nhãn `direction` có liên hệ với biến động sau tin trong T+1/T+5/T+20 không?
3. Semantic aggregate features có giảm noise so với keyword/news-count baseline không?

Metric:

- event-window raw return;
- market-adjusted return;
- abnormal volume;
- realized volatility;
- hit-rate theo direction;
- lift của nhóm direct/high-materiality so với low-relevance/low-materiality;
- Spearman/rank IC giữa materiality/direction score và return;
- ΔAUC/ΔF1 giữa Model B và Model C.

### 4.9. Cách diễn giải kết quả ML

Nếu Model C hoặc semantic Top-K tốt hơn keyword baseline:

> Semantic news features có dấu hiệu biểu diễn tin tức tốt hơn keyword/news-count trong setting mô phỏng lịch sử, nhưng chưa đủ để claim alpha do pseudo-label chưa phải ground truth và backtest còn đơn giản.

Nếu Model C không cải thiện:

> Semantic labels giúp phân tích chất lượng tin tức và phát hiện noise, nhưng chưa tạo predictive gain ổn định. Đây vẫn là negative finding có giá trị cho bài toán news-as-feature trên dữ liệu Việt Nam.

Luận văn không claim:

- mô hình giao dịch thật;
- lợi nhuận tương lai;
- khuyến nghị mua/bán;
- LLM tạo alpha.

---

## 5. Vai trò của LLM/AI

LLM/AI không phải nội dung chính. Nó chỉ giải quyết bài toán thiếu nhãn.

### 5.1. LLM dùng để làm gì?

1. Đọc title/summary/full-text.
2. Gán nhãn tạm cho semantic fields:
   - relevance;
   - materiality;
   - event type;
   - direction;
   - evidence span;
   - confidence.
3. Tạo weak reference labels/pseudo labels.
4. So sánh với keyword/rule baseline.
5. Hỗ trợ sinh evidence card minh họa.

### 5.2. LLM không dùng để làm gì?

- Không dự báo giá.
- Không đưa khuyến nghị mua/bán.
- Không thay human ground truth.
- Không chứng minh alpha.
- Không là nhân vật chính của luận văn.

### 5.3. Cách gọi đúng

Nên gọi:

- AI-assisted pseudo-labeling;
- LLM-assisted annotation;
- weak reference labels;
- AI annotator agreement.

Không gọi:

- ground truth;
- nhãn chuẩn;
- hệ thống multi-LLM là đóng góp chính.

---

## 6. Bối cảnh dữ liệu và module hiện có

### 6.1. Dữ liệu giá

Dự án đã có:

- OHLCV;
- technical indicators;
- pipeline giá;
- output ML/backtest từ các nghiên cứu trước.

Dùng cho:

- baseline;
- chọn decision candidates;
- semantic signal audit;
- outcome review.

### 6.2. Dữ liệu tin tức

Dự án đã có:

- tin tức tiếng Việt từ nhiều nguồn;
- full article/full-text ở nhiều bài;
- title, description, article summary;
- ticker matching;
- keyword/risk/event flags ở một số pipeline.

Dùng cho:

- annotation mẫu;
- semantic extraction;
- rule baseline;
- evidence card;
- outcome review.

### 6.3. File specification hiện có

File:

`LLM_News_Feature_Extraction_Specification.md`

Spec cũ tập trung vào:

> LLM chuyển bài báo thành semantic features để đưa vào ML model.

Field sẵn có:

- `is_stock_relevant`
- `sentiment`
- `importance_score`
- `expected_impact_score`
- `uncertainty_score`
- `novelty_score`
- `time_horizon`
- `reasoning_confidence`
- `summary`
- `reason`

Hướng mới kế thừa các field này, nhưng mở rộng và đặt lại mục tiêu:

> Dùng semantic features để đánh giá chất lượng thông tin và hỗ trợ phân tích/outcome review, không đặt kỳ vọng chính là cải thiện prediction.

---

## 7. Vấn đề nghiên cứu

### 7.1. Vấn đề thực tế

Tin tức chứng khoán có nhiều nhiễu:

- bài nhắc ticker nhưng không liên quan trực tiếp;
- tin thị trường chung bị gán cho mã;
- tin thủ tục nhiều nhưng ít trọng yếu;
- tin sentiment tích cực nhưng materiality thấp;
- tin keyword tiêu cực nhưng ngữ cảnh là đã xử lý rủi ro;
- full-text có boilerplate/menu/sidebar;
- tin trùng lặp nhiều nguồn;
- aggregation theo ngày/quý làm mất timing.

### 7.2. Vấn đề khoa học

Keyword/sentiment/count không trả lời đủ:

1. Tin có liên quan trực tiếp tới ticker không?
2. Tin có đủ trọng yếu không?
3. Tin thuộc loại sự kiện nào?
4. Tin hỗ trợ, rủi ro, trung tính hay hỗn hợp?
5. Đâu là câu/đoạn bằng chứng?
6. Tin có cần human review không?
7. Tin có phản ứng outcome sau đó không?

### 7.3. Vấn đề luận văn cần giải quyết

> Xây dựng và đánh giá schema đặc trưng tin tức có ngữ cảnh cho dữ liệu chứng khoán Việt Nam; dùng AI-assisted pseudo-labeling để tạo nhãn tham chiếu tạm; so sánh với keyword/rule baseline; kiểm tra semantic signal bằng outcome windows; minh họa decision support bằng evidence card và outcome review.

---

## 8. Mục tiêu nghiên cứu

### 8.1. Mục tiêu tổng quát

Đánh giá cách biểu diễn tin tức tài chính tiếng Việt bằng các đặc trưng có ngữ cảnh như relevance, materiality, event type, direction và evidence span, nhằm hỗ trợ phân tích cổ phiếu Việt Nam trong một pipeline có ML signal và outcome review.

### 8.2. Mục tiêu cụ thể

1. Tổng hợp kết quả cũ về technical ML, keyword/news features, sentiment/LLM sentiment, distant supervision.
2. Chỉ ra hạn chế của keyword/sentiment/count.
3. Đề xuất schema semantic-news annotation.
4. Tạo tập mẫu 100–200 bài báo từ dữ liệu full-text đã có.
5. Dùng AI-assisted pseudo-labeling để gán nhãn tạm.
6. Đo agreement/disagreement giữa AI annotators.
7. So sánh keyword/rule baseline với pseudo labels.
8. Phân tích lỗi: low relevance, low materiality, mixed direction, ticker mismatch, boilerplate.
9. Kiểm tra exploratory semantic signal bằng outcome windows T+1/T+5/T+20.
10. Tạo evidence card/claim ledger và outcome review framework để minh họa decision support.

---

## 9. Câu hỏi nghiên cứu

Dùng namespace `RQ-SM*` để không trùng câu hỏi/giả thuyết legacy trong các report cũ.

### RQ-SM1. Keyword/rule representation bỏ sót ngữ cảnh nào?

Đánh giá low relevance/materiality, mixed/unclear direction, ticker mismatch, boilerplate/duplicate và sai khác accuracy/macro-F1/coverage so với pseudo-label reference.

### RQ-SM2. Schema semantic-news và protocol pseudo-label có tạo biểu diễn ổn định, truy vết được không?

Đánh giá label distribution, agreement/disagreement, evidence span, provenance và manual sanity sample. Ba annotation runs chỉ thuộc hai model families, không phải ba hệ độc lập.

### RQ-SM3. Semantic labels có liên hệ với outcome windows khác baseline không?

Đánh giá exploratory association qua T+1/T+5/T+20 return, market-adjusted return, volume, volatility, direct/high-or-medium materiality versus low materiality, support versus risk, event groups và placebo pre-event. Thiết kế quan sát này không nhận dạng tác động nhân quả.

### RQ-SM4. Semantic features có chênh lệch predictive/ranking so với technical và keyword baselines không?

Đánh giá secondary bằng purged OOS balanced accuracy/AUC/F1/Precision@K/rank IC cùng paired/bootstrap deltas. Near-random hoặc unstable deltas là null finding hợp lệ.

### RQ-SM5. Top-K exploratory có khác random null và còn tồn tại sau transaction cost không?

Đánh giá non-overlap simulation, random-null comparison và cost sensitivity. Câu hỏi không nhằm chứng minh alpha hoặc chiến lược giao dịch.

### RQ-SM6. Evidence card, lineage và outcome review có cung cấp technical traceability không?

Đánh giá khả năng truy ngược claim về evidence/artifact/hash và ghi retrospective outcome status. Không suy diễn rằng card cải thiện chất lượng hoặc hiệu quả quyết định của con người.

---

## 10. Giả thuyết nghiên cứu

Các giả thuyết dưới đây là giả thuyết associational/descriptive, không phải causal hypotheses.

### H-SM1. Keyword/rule representation có sai khác tập trung ở relevance, materiality và direction

Sai khác được đo với controlled pseudo-label reference, không phải human ground truth.

### H-SM2. Schema semantic-news tạo artifact có khả năng audit tốt hơn count/sentiment đơn giản

Khả năng audit thể hiện qua evidence span, provenance, disagreement và manual quality-control sample; không đồng nghĩa nhãn đúng ở cấp population.

### H-SM3. Nhóm semantic có outcome distribution khác nhau trong mẫu quan sát

Direct/high-or-medium materiality và support/risk có thể khác nhóm đối chứng sau correction, nhưng pre-event placebo/confounding có thể bác bỏ diễn giải event-specific; không claim causality.

### H-SM4. Semantic features có predictive delta khác keyword baseline trong purged OOS evaluation

Delta có thể dương, bằng không hoặc âm. Near-random metrics và CI/delta không ổn định được giữ như negative finding.

### H-SM5. Top-K performance không được xem là khác random hoặc bền với chi phí nếu null/cost gates không qua

Passing accounting checks chỉ xác nhận implementation; không xác nhận alpha.

### H-SM6. Evidence card và lineage tăng technical traceability

Mỗi claim có thể truy về evidence ID, structured artifact và hash. Hypothesis không bao gồm decision quality, user utility hoặc investment suitability.

---

## 11. Đóng góp dự kiến

### Đóng góp 1: Benchmark và negative findings về news-as-feature

Tổng hợp có hệ thống các kết quả cũ:

- keyword/news không cải thiện forecast ổn định;
- keyword significance yếu;
- sentiment/LLM sentiment không tạo gain rõ;
- distant supervision có tín hiệu article-level nhưng aggregate yếu.

### Đóng góp 2: Schema semantic-news cho tin chứng khoán Việt Nam

Schema gồm:

- ticker relevance;
- materiality;
- event type;
- direction;
- uncertainty;
- novelty;
- time horizon;
- evidence span;
- confidence;
- data quality flags.

### Đóng góp 3: AI-assisted pseudo-labeling protocol

Quy trình tạo nhãn tạm có kiểm soát:

- prompt/schema cố định;
- raw output lưu lại;
- agreement/disagreement;
- evidence span bắt buộc;
- không gọi là ground truth.

### Đóng góp 4: So sánh keyword/rule với semantic pseudo labels

Chỉ ra keyword/rule sai ở đâu:

- relevance;
- materiality;
- direction;
- ticker mismatch;
- boilerplate/duplicate noise.

### Đóng góp 5: ML filtering/ranking với target outperform benchmark

Nâng bài toán ML từ up/down tuyệt đối sang target:

```text
label_outperform_T20 = 1 nếu stock_return_T20 > VNINDEX_return_T20
```

Đánh giá không chỉ bằng accuracy/AUC mà còn bằng:

- Precision@K;
- ranking quality;
- Top-K portfolio simulation;
- transaction cost;
- benchmark VNINDEX/equal-weight/random/technical-only.

### Đóng góp 6: Semantic signal audit gắn với ML/outcome

Kiểm tra exploratory xem semantic labels có phản ánh outcome tốt hơn keyword/news-count không qua:

- event-window returns;
- abnormal volume;
- volatility;
- lift theo direct/high-materiality.

### Đóng góp 7: Evidence card và outcome review framework

Mỗi claim có:

- evidence ID;
- evidence span;
- relevance/materiality;
- direction;
- confidence;
- data quality flags;
- outcome review label.

---

## 12. Phạm vi nghiên cứu

### Trong phạm vi

- Tin tức chứng khoán tiếng Việt đã crawl.
- Full-text article nếu có.
- Dữ liệu giá/technical features đã có để làm baseline/outcome.
- Keyword/rule baseline.
- Semantic-news schema.
- AI-assisted pseudo-labeling.
- Agreement/disagreement analysis.
- Rule-vs-pseudo-label comparison.
- Semantic signal audit.
- Evidence card/outcome review.

### Ngoài phạm vi

- Không xây stock recommender hoàn chỉnh.
- Không chứng minh LLM tạo alpha.
- Không claim AI labels là ground truth.
- Không cần fine-tune LLM.
- Không cần hệ thống multi-agent phức tạp.
- Không claim semantic features chắc chắn cải thiện return.

---

## 13. Phạm vi core và extended để tránh scope creep

Để luận văn không bị quá rộng, chia rõ phần bắt buộc và phần mở rộng.

### 13.1. Core scope bắt buộc

Đây là phần cần hoàn thành để luận văn có đóng góp rõ:

1. **Semantic-news schema**: relevance, materiality, event type, direction, evidence span, uncertainty, novelty, confidence.
2. **AI-assisted pseudo-labeling protocol**: 2–3 annotators/model, raw output, agreement/disagreement, JSON validation.
3. **Keyword/rule vs semantic pseudo labels**: so sánh định lượng và phân tích lỗi.
4. **Materiality/relevance error taxonomy**: low relevance, low materiality, mixed direction, ticker mismatch, boilerplate/duplicate.
5. **Manual sanity check nhỏ**: 20–30 bài kiểm tra thủ công để neo chất lượng pseudo labels.
6. **Outcome review case studies**: 3–5 case có evidence card và hậu kiểm.

### 13.2. Extended scope nếu đủ dữ liệu/thời gian

Phần này làm đề tài mạnh hơn nhưng không nên là điều kiện sống còn:

1. Pseudo-label trên tập tin lớn/toàn corpus để tạo semantic aggregate features.
2. ML outperform classification/ranking với target T+20.
3. Top-K simulation có transaction cost.
4. Regression/ranking excess return.
5. Mở rộng event ontology hoặc human-labeled dataset lớn hơn.

### 13.3. Nguyên tắc diễn giải

- Nếu chỉ hoàn thành core scope: luận văn vẫn có đóng góp về semantic representation và evidence audit.
- Nếu hoàn thành thêm ML/Top-K: xem là kiểm tra exploratory/secondary, không claim trading strategy.
- Top-K simulation là sanity check cho filtering/ranking, không phải bằng chứng lợi nhuận tương lai.

---

## 14. Dữ liệu dùng trong luận văn

### 14.1. Dữ liệu giá

Dùng để:

- tổng hợp kết quả technical ML trước đó;
- chọn decision candidates;
- tính event-window outcome;
- outcome review;
- tạo semantic aggregate features thử nghiệm nếu cần.

### 14.2. Dữ liệu tin tức

Dùng các trường:

- `ticker`;
- `date` hoặc `published_at`;
- `source`;
- `title`;
- `description`;
- `article_summary` nếu có;
- `full_text`;
- `url`;
- `match_confidence`;
- keyword/risk/event flags nếu có.

### 14.3. Tập mẫu annotation

MVP:

- 100 bài.

Tốt hơn:

- 200 bài.

Cách chọn mẫu:

- có nhiều event type;
- có direct company news;
- có market-wide/sector news;
- có tin thủ tục;
- có tin risk/legal/debt;
- có tin earnings/dividend/capital;
- có match confidence khác nhau;
- có cả tin dễ và tin mơ hồ.

Gợi ý phân bổ 150 bài:

| Nhóm tin | Số bài gợi ý |
|---|---:|
| Earnings/business result | 25 |
| Dividend/capital issuance | 20 |
| Debt/legal/governance risk | 25 |
| Project/business expansion | 20 |
| Market-wide/sector news | 25 |
| Generic/company announcement | 20 |
| Noisy/low-confidence match | 15 |

---

## 15. Schema annotation đề xuất

```json
{
  "news_id": "N0001",
  "ticker": "HPG",
  "company_name": "Hoa Phat Group",
  "article_date": "2026-07-07",
  "source": "cafef",
  "title": "...",

  "ticker_relevance": "direct",
  "is_stock_relevant": true,

  "event_type": "earnings",
  "event_subtype": "quarterly_result",

  "direction": "support",
  "sentiment": "positive",

  "materiality": "high",
  "materiality_score": 4,
  "expected_impact_score": 3,

  "uncertainty_score": 2,
  "novelty_score": 4,
  "time_horizon": "short_term",

  "evidence_span": "...",
  "summary": "...",
  "reason": "...",

  "reasoning_confidence": 4,
  "requires_human_review": false,
  "data_quality_flags": []
}
```

### 15.1. `ticker_relevance`

Allowed values:

| Label | Quy tắc gán nhãn |
|---|---|
| `direct` | Tin nói trực tiếp về công ty/ticker, kết quả kinh doanh, vốn, cổ tức, pháp lý, dự án, lãnh đạo hoặc tài sản của công ty. |
| `indirect` | Tin liên quan qua ngành, công ty mẹ/con, đối tác lớn, hàng hóa đầu vào/đầu ra hoặc chính sách ảnh hưởng đáng kể tới công ty. |
| `market_wide` | Tin thị trường chung, vĩ mô, lãi suất, tỷ giá, index, tâm lý thị trường; có thể ảnh hưởng nhiều mã nhưng không riêng ticker. |
| `irrelevant` | Ticker bị nhắc phụ, nhắc trong danh sách, sidebar, bảng giá, tin liên quan, hoặc không có quan hệ kinh tế rõ. |
| `unclear` | Không đủ dữ liệu để xác định liên quan. |

Quy tắc ưu tiên:

1. Nếu bài vừa có tin công ty vừa có thị trường chung, chọn `direct` nếu phần công ty là nội dung chính.
2. Nếu ticker chỉ xuất hiện trong danh sách nhiều mã, không có claim riêng, chọn `market_wide` hoặc `irrelevant` tùy ngữ cảnh.
3. Nếu match confidence thấp, thêm `requires_human_review = true`.

### 15.2. `materiality`

Allowed values:

| Label | Quy tắc gán nhãn |
|---|---|
| `high` | Tin có thể thay đổi kỳ vọng về doanh thu, lợi nhuận, tài sản, nợ, dòng tiền, vốn, pháp lý lớn, dự án lớn, M&A, audit opinion, default risk hoặc sự kiện có số liệu/giá trị đáng kể. |
| `medium` | Tin có liên quan rõ nhưng quy mô/tác động chưa đủ lớn hoặc chưa đủ dữ liệu định lượng; có thể đáng theo dõi nhưng chưa chắc đổi thesis đầu tư. |
| `low` | Tin thủ tục, PR, lịch họp, nhắc lại thông tin cũ, thay đổi nhỏ, tin chung chung, không có tác động tài chính rõ. |
| `unclear` | Bài thiếu thông tin, evidence span yếu, hoặc annotators không đủ căn cứ đánh trọng yếu. |

Rubric ngắn:

- Có số liệu tài chính, quy mô dự án, tỷ lệ vốn, mức phạt, nợ, lợi nhuận, doanh thu, guidance hoặc audit/legal event lớn → ưu tiên `high`/`medium`.
- Chỉ có keyword tích cực/tiêu cực nhưng không rõ quy mô → không tự động gán `high`.
- Tin đúng về doanh nghiệp nhưng không kỳ vọng phản ứng giá ngắn hạn → có thể `low` hoặc `not_price_relevant` ở outcome review.
- Nếu không chỉ được evidence span hỗ trợ materiality → giảm một bậc hoặc gắn `unclear`.

### 15.3. `event_type`

Allowed values:

- `earnings`
- `dividend`
- `capital`
- `debt`
- `legal`
- `governance`
- `project`
- `product`
- `ma`
- `analyst`
- `market`
- `macro`
- `sector`
- `other`
- `unclear`

### 15.4. `direction`

Allowed values:

- `support`: hỗ trợ thesis tích cực.
- `risk`: tạo rủi ro/áp lực.
- `neutral`: trung tính.
- `mixed`: vừa có hỗ trợ vừa có rủi ro.
- `unclear`: không đủ thông tin.

### 15.5. `evidence_span`

Một đoạn ngắn trong bài làm căn cứ cho label.

Quy tắc:

- không tự bịa;
- nếu không có căn cứ rõ, ghi `null`;
- ưu tiên title/lead/body chính;
- không lấy boilerplate/menu/footer.

### 15.6. `requires_human_review`

True nếu:

- relevance unclear;
- materiality high nhưng evidence yếu;
- direction mixed/unclear;
- confidence thấp;
- ticker matching yếu;
- nghi ngờ boilerplate;
- annotators disagreement cao.

---

## 16. AI-assisted pseudo-labeling protocol

### 16.1. Mục đích

Tạo nhãn tham chiếu tạm cho 100–200 bài khi chưa có human labels.

### 16.2. Cách làm

- Chạy 2–3 AI model hoặc 2–3 cấu hình annotator độc lập nếu có điều kiện.
- Cố định prompt, schema, instruction và version model.
- Ưu tiên structured JSON output theo schema.
- Nếu provider hỗ trợ sampling parameter thì dùng temperature thấp; nếu không hỗ trợ thì kiểm soát bằng prompt/schema/validation.
- Không cho annotator xem nhãn của nhau.
- Không đưa future return/outcome vào input.
- Lưu raw input, raw output, parsed output, model name, model version, timestamp.
- Bắt buộc evidence span hoặc `null` nếu không có căn cứ.
- Validate output bằng JSON schema; output lỗi được retry hoặc đánh dấu invalid.

### 16.3. Consensus rule

Nếu dùng 3 model:

- field categorical: majority vote 2/3;
- nếu không có majority: `disagreement`;
- nếu majority là `unclear`: `unclear`;
- field numeric: median;
- score range >= 2: đánh dấu high disagreement.

Nếu chỉ dùng 2 model:

- nếu đồng ý: lấy label;
- nếu khác: gắn disagreement và dùng model thứ ba hoặc manual audit nếu cần.

### 16.4. Manual sanity check

Để tránh phụ thuộc hoàn toàn vào AI labels, cần kiểm tra thủ công một mẫu nhỏ.

Cỡ mẫu tối thiểu:

- 20–30 bài nếu thời gian hạn chế.
- Ưu tiên bài có disagreement, high materiality, mixed/unclear direction, match confidence thấp.

Cách kiểm tra:

1. Đọc title + full text chính, bỏ boilerplate/menu/footer.
2. So nhãn consensus với rubric `ticker_relevance`, `materiality`, `event_type`, `direction`.
3. Ghi lỗi theo taxonomy:
   - wrong relevance;
   - wrong materiality;
   - wrong direction;
   - wrong event type;
   - missing/invalid evidence span;
   - boilerplate contamination;
   - ticker mismatch.
4. Báo cáo tỷ lệ lỗi, ví dụ `x/30` bài cần sửa.

Diễn giải:

> Manual sanity check không biến pseudo labels thành ground truth. Nó chỉ giúp phát hiện lỗi hệ thống và chứng minh quy trình có kiểm soát.

### 16.5. Phân biệt annotation sample và ML corpus

Cần tách rõ hai tầng dữ liệu:

| Tầng | Quy mô | Vai trò | Claim được phép |
|---|---:|---|---|
| Annotation sample | 100–200 bài | đánh giá schema, agreement, keyword-vs-semantic, lỗi materiality/relevance | claim về chất lượng nhãn và noise của tin tức |
| ML/outcome corpus | nhiều ticker/date hơn nếu đủ thời gian | tạo aggregate semantic features, kiểm tra T+20 outperform/ranking | claim exploratory, không claim trading alpha |
| Case-study set | 3–5 case | evidence card và outcome review | minh họa audit trail và decision-support logic |

Nếu không kịp mở rộng corpus ML, luận văn vẫn giữ được core contribution bằng annotation sample + error taxonomy + outcome case studies.

### 16.6. Limitation phải ghi rõ

> Pseudo labels không phải ground truth. Kết quả chỉ dùng để phân tích tương đối và định hướng xây dựng human-labeled dataset sau này.

---

## 17. Keyword/rule baseline

### 17.1. Mục tiêu

Dùng baseline hiện có/đơn giản để so sánh với semantic pseudo labels.

### 17.2. Baseline có thể gồm

- keyword sentiment positive/negative/neutral;
- keyword event groups;
- news count;
- ticker mention/match confidence;
- rule materiality theo event type;
- rule relevance theo ticker/source/match confidence.

### 17.3. Câu hỏi so sánh

1. Keyword có bắt đúng event type không?
2. Keyword sentiment có khớp với semantic direction không?
3. Match confidence có khớp với semantic relevance không?
4. Event/risk keyword có phản ánh materiality không?
5. Tin bị keyword đếm nhưng pseudo label đánh low relevance/low materiality là bao nhiêu?

### 17.4. Metrics

- accuracy vs pseudo labels;
- macro-F1 vs pseudo labels;
- confusion matrix;
- coverage;
- unclear/disagreement rate;
- qualitative error examples.

---

## 18. Semantic aggregate features và ML signal audit

Phần này giúp đề tài không chỉ dừng ở annotation. Nhưng vẫn diễn giải thận trọng.

### 18.1. Semantic features theo ticker/date hoặc ticker/quarter

- `direct_news_count`
- `high_materiality_count`
- `medium_materiality_count`
- `low_relevance_ratio`
- `support_count`
- `risk_count`
- `mixed_direction_count`
- `avg_materiality_score`
- `avg_uncertainty_score`
- `avg_novelty_score`
- `event_earnings_count`
- `event_debt_legal_count`
- `high_disagreement_ratio`
- `days_since_high_materiality_news`

### 18.2. Feature sets so sánh

1. Technical-only.
2. Technical + keyword/news-count/sentiment baseline.
3. Technical + semantic pseudo-label features.

### 18.3. Outcome windows

Với mỗi tin tại `t0`, xem:

- T+1 ngày giao dịch;
- T+5 ngày giao dịch;
- T+20 ngày giao dịch;
- T+60 nếu `time_horizon = medium_term`.

Outcome gồm:

- raw return;
- market-adjusted return;
- abnormal volume;
- realized volatility;
- max adverse move/drawdown nếu cần.

### 18.4. Temporal validation và anti-leakage

Quy tắc bắt buộc:

- Dùng temporal split, không dùng random split.
- Feature tại `t0` chỉ dùng giá và tin xuất hiện trước hoặc tại `t0`.
- Nếu bài báo thiếu giờ công bố, xem bài có hiệu lực từ ngày giao dịch kế tiếp.
- Không đưa return T+1/T+5/T+20 vào prompt annotation.
- Không tune threshold/model dựa trên test period.
- Deduplicate tin trước khi aggregate để tránh một sự kiện bị đếm nhiều lần.
- Tách train/validation/test theo thời gian trước khi chọn model chính.

### 18.5. Universe và backtest rule

Nếu chạy ML/ranking/Top-K, cần ghi rõ:

- universe gồm các mã có đủ dữ liệu giá và tin tức trong giai đoạn nghiên cứu;
- loại mã thiếu dữ liệu quá nhiều hoặc thanh khoản quá thấp nếu có tiêu chí thanh khoản;
- dùng giá đã điều chỉnh nếu có dữ liệu corporate action;
- nếu chưa có dữ liệu adjusted price đầy đủ, ghi limitation rõ;
- dùng close-to-close return hoặc next-open-to-close nhất quán;
- benchmark chính là VNINDEX, benchmark phụ là equal-weight universe;
- transaction cost chính: `round_trip_cost = 0.50%`;
- rebalance và holding window phải cố định trước khi xem kết quả.

### 18.6. Cách diễn giải

Nếu semantic features cải thiện nhẹ:

> Semantic labels có tín hiệu định lượng tốt hơn keyword baseline trong setting exploratory, nhưng chưa đủ để claim alpha do sample nhỏ và pseudo-label chưa phải ground truth.

Nếu không cải thiện:

> Semantic labels hữu ích cho phân tích chất lượng tin tức và phát hiện noise, nhưng chưa tạo predictive gain ổn định. Đây vẫn là negative finding có giá trị.

---

## 19. Decision-support pipeline dựa trên evidence

Evidence card không chỉ là phần trình bày đẹp. Nó là artifact giúp truy vết từ tin tức → nhãn semantic → claim → outcome review.

### 19.1. Pipeline đề xuất

```text
Raw news
  -> ticker matching / deduplication / data quality flags
  -> AI-assisted semantic annotation
  -> agreement / disagreement detection
  -> pseudo-label consensus
  -> semantic feature aggregation by ticker/date
  -> ML signal / decision candidate context
  -> evidence card / claim ledger
  -> human review queue
  -> outcome review after T+1/T+5/T+20
  -> schema/prompt/error taxonomy update
```

### 19.2. Vai trò từng bước

| Bước | Output | Mục đích |
|---|---|---|
| Ticker matching | ticker, match confidence | giảm lỗi gán nhầm mã |
| Semantic annotation | relevance, materiality, event, direction, evidence span | biểu diễn tin theo ngữ cảnh |
| Agreement check | consensus/disagreement flags | biết nhãn nào ổn định, nhãn nào cần review |
| Semantic aggregation | features by ticker/date | nối với ML/outcome setting |
| ML signal context | decision candidate | chọn case phân tích, không khuyến nghị mua |
| Evidence card | claim + evidence + warning | hỗ trợ analyst đọc nhanh nhưng có truy vết |
| Outcome review | confirmed/contradicted/unresolved/confounded | hậu kiểm chất lượng claim/evidence |

### 19.3. Human review queue

Các tin/claim sau cần review:

- `materiality = high` nhưng confidence thấp;
- `direction = mixed` hoặc `unclear`;
- disagreement cao giữa annotators;
- ticker matching yếu;
- evidence span ngắn/mơ hồ/nghi boilerplate;
- outcome sau này trái direction ban đầu.

---

## 20. Evidence card / claim ledger

### 20.1. Mục tiêu

Evidence card giúp người đọc thấy:

- tin nào thật sự liên quan;
- tin nào material;
- tin nào hỗ trợ/rủi ro;
- tin nào nhiễu;
- claim dựa trên evidence nào;
- cần hậu kiểm gì sau đó.

### 20.2. Cấu trúc card

```text
1. Ticker / date / decision context
2. ML signal context nếu có
3. News evidence summary
4. Evidence quality
5. Claims table
6. Risks / contradictory evidence
7. Data quality flags
8. Outcome review status
```

### 20.3. Claim table mẫu

| Claim | Evidence ID | Relevance | Materiality | Direction | Confidence | Note |
|---|---|---|---|---|---|---|
| Tin dự án có thể hỗ trợ kỳ vọng trung hạn | N002 | direct | medium | support | medium | cần theo dõi tiến độ |
| Tin BCTC có rủi ro kiểm toán | N001 | direct | medium | risk | medium | risk flag audit_issue |
| Tin thị trường chung không đủ trực tiếp | N004 | market_wide | low | neutral | low | không dùng làm thesis chính |

---

## 21. Outcome review framework

Outcome review là điểm giúp hướng này khác dashboard/tóm tắt thông thường.

### 21.1. Mục tiêu

Hậu kiểm evidence card sau một khoảng thời gian. Không dùng để khẳng định dự báo chắc chắn. Mục tiêu là đánh giá liệu nhãn `materiality` và `direction` ban đầu có tạo nhận định hợp lý trong bối cảnh sau đó không.

### 21.2. Đơn vị review

Mỗi đơn vị review:

```text
(news_id, ticker, event_date, claim_id)
```

Mỗi claim được freeze tại `t0`, trước khi biết outcome.

### 21.3. Cửa sổ outcome

- T+1: phản ứng ngắn hạn.
- T+5: phản ứng tuần.
- T+20: phản ứng tháng.
- T+60: trung hạn nếu event có `time_horizon = medium_term`.

### 21.4. Outcome labels

| Label | Ý nghĩa | Quy tắc vận hành |
|---|---|---|
| `confirmed` | Diễn biến sau đó phù hợp với direction/materiality ban đầu | `support` đi cùng excess return/volume tích cực, hoặc `risk` đi cùng excess return/volume tiêu cực trong cửa sổ review; không có confounder lớn. |
| `contradicted` | Diễn biến trái với direction/materiality ban đầu | Outcome ngược direction ban đầu và không có sự kiện khác giải thích rõ. |
| `unresolved` | Chưa đủ dữ liệu để kết luận | Window quá ngắn, thiếu giá/tin follow-up, hoặc tín hiệu outcome quá yếu. |
| `confounded` | Có sự kiện khác lớn hơn làm nhiễu outcome | Có tin khác, shock ngành/thị trường, kết quả kinh doanh, cổ tức, pháp lý hoặc biến động index mạnh trong cùng cửa sổ. |
| `not_price_relevant` | Tin có giá trị thông tin nhưng không thể hiện rõ qua giá | Tin thủ tục/PR/low materiality; hợp lệ về thông tin nhưng không kỳ vọng phản ứng giá rõ. |

Ngưỡng outcome nên cố định trước khi chạy review. Ví dụ:

- `confirmed support`: excess return T+20 > 0 và/hoặc abnormal volume dương, không có confounder lớn.
- `confirmed risk`: excess return T+20 < 0 và/hoặc drawdown tăng, không có confounder lớn.
- Nếu return gần 0 hoặc trái chiều nhưng có tin lớn khác, không ép thành đúng/sai; dùng `unresolved` hoặc `confounded`.

### 21.5. Metric outcome

- price return;
- market-adjusted return;
- abnormal volume;
- volatility change;
- follow-up news;
- drawdown/max adverse move.

### 21.6. Bảng outcome review mẫu

| Claim ID | News ID | Ticker | Initial direction | Materiality | Window | Outcome label | Evidence after review |
|---|---|---|---|---|---|---|---|
| C001 | N001 | HPG | support | high | T+20 | confirmed | giá tăng vượt benchmark, volume tăng, follow-up tích cực |
| C002 | N004 | VNM | risk | medium | T+5 | confounded | cùng kỳ có tin thị trường chung ảnh hưởng toàn ngành |
| C003 | N010 | SSI | support | low | T+20 | not_price_relevant | tin thủ tục, không có phản ứng đáng kể |

### 21.7. Nguyên tắc chống leakage

- Không đưa return tương lai vào prompt annotation.
- Freeze evidence card tại `t0`.
- Outcome review chạy sau annotation.
- Nếu nhiều tin trong cùng cửa sổ, đánh dấu `confounded`.
- Không xem outcome label là ground truth cho nhãn semantic; chỉ là hậu kiểm ứng dụng.

---

## 22. Thực nghiệm đề xuất

### Experiment 1: Tổng hợp kết quả cũ về news-as-feature

Mục tiêu:

> Chứng minh vì sao cần schema mới.

Dùng các kết quả:

- H1 keyword/news không cải thiện;
- H2 keyword significance không qua BH-FDR;
- H3 SHAP chỉ partial;
- A6 LLM sentiment không cải thiện;
- B1 distant supervision aggregate yếu.

Output:

- bảng claim-vs-evidence;
- narrative negative finding.

### Experiment 2: Semantic label distribution

Input:

- 100–200 bài báo.

Output:

- phân phối relevance/materiality/event/direction.

Bảng mẫu:

| Field | Label | Ratio |
|---|---|---:|
| relevance | direct | x% |
| relevance | market_wide | x% |
| materiality | high | x% |
| materiality | low | x% |
| direction | mixed/unclear | x% |

### Experiment 3: AI annotator agreement

Mục tiêu:

> Đánh giá pseudo labels có ổn định không.

Metric:

- consensus rate;
- agreement by field;
- Cohen/Fleiss Kappa nếu phù hợp;
- disagreement examples.

### Experiment 4: Keyword/rule vs semantic pseudo labels

Mục tiêu:

> Chỉ ra keyword/rule sai ở đâu.

Bảng mẫu:

| Field | Keyword/rule Accuracy | Macro-F1 | Lỗi chính |
|---|---:|---:|---|
| event_type | x | x | keyword overlap |
| direction | x | x | thiếu ngữ cảnh |
| materiality | x | x | keyword không đo trọng yếu |
| relevance | x | x | ticker matching/mixed news |

### Experiment 5: Semantic signal audit

Mục tiêu:

> Kiểm tra semantic labels có liên hệ outcome tốt hơn keyword/news-count không.

So sánh:

- direct/high materiality vs market-wide/low materiality;
- support vs risk direction;
- event types khác nhau;
- keyword baseline vs semantic labels.

Metric:

- T+1/T+5/T+20 returns;
- market-adjusted returns;
- abnormal volume;
- volatility;
- hit-rate/lift.

### Experiment 6: ML classification/ranking với target outperform

Target chính:

```text
label_outperform_T20 = 1 nếu stock_return_T20 > VNINDEX_return_T20
label_outperform_T20 = 0 nếu stock_return_T20 <= VNINDEX_return_T20
```

Target phụ:

```text
excess_return_T20 = stock_return_T20 - VNINDEX_return_T20
```

Feature sets:

1. Technical-only.
2. Technical + keyword/news-count/sentiment.
3. Technical + semantic pseudo-label features.
4. Technical + keyword + semantic nếu cần.

Models:

- Logistic Regression baseline.
- Random Forest.
- LightGBM/XGBoost.
- Optional: regression/ranking model cho `excess_return_T20`.

Metrics classification:

- Balanced Accuracy;
- AUC;
- F1;
- Precision@K;
- confusion matrix.

Metrics ranking/regression:

- Spearman rank correlation;
- Information Coefficient;
- average excess return by score decile;
- top quantile return;
- MAE/RMSE chỉ báo cáo phụ nếu chạy regression.

### Experiment 6b: Top-K filtering simulation có chi phí

Mức ưu tiên: **secondary/optional**. Chỉ chạy nếu semantic aggregate features và ML corpus đủ lớn. Không dùng làm claim chính của luận văn.

Mục tiêu:

> Kiểm tra mô hình có hỗ trợ lọc/xếp hạng cổ phiếu trong mô phỏng lịch sử không.

Quy trình:

```text
Mỗi rebalance date:
  1. Dự báo probability outperform hoặc expected excess return.
  2. Rank cổ phiếu trong universe.
  3. Chọn Top-5 hoặc Top-10.
  4. Equal-weight portfolio.
  5. Giữ T+20 ngày hoặc đến kỳ rebalance sau.
  6. Trừ transaction cost.
  7. So sánh benchmark.
```

Benchmark:

- VNINDEX;
- equal-weight universe;
- random Top-K;
- technical-only Top-K;
- keyword/news-count Top-K.

Transaction cost:

```text
round_trip_cost = 0.50%
```

Metrics:

- cumulative return;
- excess return vs VNINDEX;
- Sharpe;
- max drawdown;
- hit rate by rebalance period;
- turnover;
- average return per period.

Cách diễn giải:

- Nếu semantic Top-K tốt hơn keyword baseline: semantic news features có giá trị lọc/xếp hạng exploratory.
- Nếu không tốt hơn: kết quả âm cho thấy semantic labels hữu ích cho phân tích/evidence nhưng chưa đủ chuyển thành stock selection signal ổn định.

### Experiment 7: Evidence card và outcome review case studies

Chọn 3–5 case:

1. Keyword tích cực nhưng pseudo label low materiality.
2. Keyword bỏ sót event quan trọng.
3. Tin direct/high materiality nhưng direction mixed.
4. Case ML đúng nhưng evidence yếu.
5. Case ML sai và evidence card đã cảnh báo rủi ro.

---

## 23. Cấu trúc luận văn đề xuất

### Chương 1. Giới thiệu

- Bài toán phân tích cổ phiếu bằng giá và tin tức.
- Hạn chế của stock prediction/news sentiment phổ biến.
- Kết quả ban đầu cho thấy news-as-feature chưa hiệu quả.
- Đặt vấn đề: cần đánh giá relevance/materiality/context của tin tức.
- Mục tiêu và đóng góp.

### Chương 2. Cơ sở lý thuyết và công trình liên quan

- ML stock prediction.
- Technical indicators.
- Financial news sentiment.
- Event extraction trong tài chính.
- Materiality/relevance trong thông tin tài chính.
- Weak supervision/pseudo-labeling.
- LLM như công cụ annotation/extraction.
- Decision support/evidence card và outcome review.
- Định vị novelty so với stock-prediction/sentiment/RAG/dashboard.

### Chương 3. Dữ liệu và phương pháp

- Dữ liệu giá.
- Dữ liệu tin tức full-text.
- Keyword/sentiment baseline.
- Schema semantic annotation.
- AI-assisted pseudo-labeling protocol.
- Keyword/rule baseline.
- Semantic aggregate features.
- ML target: market-adjusted outperform T+20.
- Classification/ranking/Top-K simulation.
- Transaction cost và benchmark design.
- ML signal audit.
- Outcome review framework.

### Chương 4. Kết quả thực nghiệm

- Tổng hợp negative findings cũ.
- Distribution semantic labels.
- Agreement/disagreement giữa AI annotators.
- Keyword/rule vs pseudo labels.
- Semantic signal audit.
- ML outperform classification/ranking.
- Top-K simulation có transaction cost.
- Evidence card/outcome review case studies.

### Chương 5. Thảo luận

- Vì sao keyword/sentiment yếu.
- Relevance/materiality giúp hiểu dữ liệu thế nào.
- Field nào dễ/khó annotate.
- Hạn chế của pseudo labels.
- Hạn chế outcome review.
- Khả năng phát triển human-labeled dataset.

### Chương 6. Kết luận

- Tóm tắt đóng góp.
- Không claim alpha/prediction chắc chắn.
- Future work: human labels, active learning, better event ontology, materiality scoring, dashboard/evidence audit.

---

## 24. Kế hoạch MVP

### Giai đoạn 1: Chọn mẫu tin

Output:

`data/sample_news_for_annotation.csv`

Fields:

```text
news_id,ticker,date,source,title,summary,article_text,url,match_confidence
```

Số lượng:

- 100 bài trước.
- Nếu ổn, mở rộng 200 bài.

### Giai đoạn 2: Viết schema + prompt annotation

Output:

- `schemas/semantic_news_annotation_schema.json`
- `prompts/annotation_prompt.md`

### Giai đoạn 3: Chạy AI-assisted pseudo-labeling

Output:

- `outputs/labels_model_a.jsonl`
- `outputs/labels_model_b.jsonl`
- `outputs/labels_model_c.jsonl`
- `outputs/pseudo_labels_consensus.jsonl`

### Giai đoạn 4: Đánh giá agreement

Output:

- `reports/annotation_agreement_report.md`

### Giai đoạn 5: So sánh keyword/rule

Output:

- `outputs/rule_labels.jsonl`
- `reports/rule_vs_semantic_labels_report.md`

### Giai đoạn 6: Semantic signal audit

Output:

- `reports/semantic_signal_audit_report.md`
- event-window return/volume/volatility tables.

### Giai đoạn 7: ML outperform classification/ranking + Top-K simulation

Output:

- `outputs/ml_predictions_outperform.csv`
- `outputs/topk_portfolio_simulation.csv`
- `reports/ml_outperform_experiment_report.md`
- `reports/topk_backtest_with_cost_report.md`

Nội dung:

- target `label_outperform_T20`;
- feature sets A/B/C/D;
- classification metrics;
- ranking metrics;
- Top-5/Top-10 simulation;
- transaction cost `round_trip_cost = 0.50%`;
- benchmark VNINDEX/equal-weight/random/technical-only/keyword.

### Giai đoạn 8: Evidence card + outcome review

Output:

- `outputs/evidence_cards.md`
- `reports/outcome_review_report.md`
- `reports/case_studies.md`

### Giai đoạn 9: Tích hợp vào luận văn

Output:

- chương phương pháp;
- chương kết quả;
- claim-vs-evidence table;
- limitations.

---

## 25. Folder structure đề xuất sau chỉnh

```text
multi_llm_evidence_extraction/
  README.md
  de_cuong_chi_tiet_multi_llm_evidence_extraction.md
  prompts/
    annotation_prompt.md
    evidence_card_prompt.md
  schemas/
    semantic_news_annotation_schema.json
    pseudo_label_consensus_schema.json
    outcome_review_schema.json
  data/
    sample_news_for_annotation.csv
  outputs/
    labels_model_a.jsonl
    labels_model_b.jsonl
    labels_model_c.jsonl
    pseudo_labels_consensus.jsonl
    rule_labels.jsonl
    semantic_features.csv
    evidence_cards.md
  reports/
    annotation_agreement_report.md
    rule_vs_semantic_labels_report.md
    semantic_news_analysis_report.md
    semantic_signal_audit_report.md
    outcome_review_report.md
    case_studies.md
    limitations.md
```

---

## 26. Rủi ro và cách phòng thủ

### Rủi ro 1: Không có human ground truth

Phòng thủ:

> Luận văn dùng pseudo labels như nhãn tham chiếu tạm, không phải ground truth. Mục tiêu là phân tích tương đối và thiết kế schema, không công bố benchmark NLP chuẩn.

### Rủi ro 2: AI annotators cùng sai

Phòng thủ:

- bắt buộc evidence span;
- đo disagreement;
- manual sanity check 20 mẫu nếu có thể;
- ghi limitation rõ.

### Rủi ro 3: Chủ đề bị hiểu là LLM project

Phòng thủ:

> LLM chỉ là annotation tool. Nội dung chính là đánh giá đặc trưng tin tức có ngữ cảnh, ML signal audit và outcome review cho cổ phiếu Việt Nam.

### Rủi ro 4: Không cải thiện prediction

Phòng thủ:

> Prediction không phải claim chính. Nếu thử semantic features mà không cải thiện, kết quả vẫn có giá trị giải thích giới hạn của news-as-feature.

### Rủi ro 5: Outcome bị confounded

Phòng thủ:

- dùng outcome label `confounded`;
- không xem outcome là ground truth tuyệt đối;
- dùng market-adjusted return và follow-up events;
- phân tích case thay vì overclaim thống kê mạnh.

### Rủi ro 6: Tin tức noisy/full-text lỗi

Phòng thủ:

- data quality flags;
- relevance label;
- materiality label;
- boilerplate/noise analysis;
- ticker matching analysis.

---

## 27. Câu nói với giảng viên

> Em không muốn biến luận văn thành một project LLM summary hay stock recommender vì hướng đó dễ trùng và kết quả prediction hiện chưa mạnh. Trọng tâm em muốn làm là đánh giá cách biểu diễn tin tức cho cổ phiếu Việt Nam. Các kết quả trước cho thấy keyword/sentiment không cải thiện ổn định, nên em đề xuất phân tích sâu hơn bằng các đặc trưng semantic như relevance, materiality, event type, direction và evidence span. Vì chưa có human labels, em dùng AI như công cụ gán nhãn tạm và đo agreement, sau đó so sánh với keyword/rule baseline. ML signal vẫn được dùng để chọn decision candidate và kiểm tra exploratory bằng outcome windows. Phần evidence card/outcome review giúp hậu kiểm claim: tin nào hữu ích, tin nào nhiễu, và vì sao một tín hiệu đúng/sai. Luận văn không claim LLM tạo alpha hay khuyến nghị mua/bán.

---

## 28. Kết luận đề cương

Hướng sau chỉnh hợp lý vì:

1. Trọng tâm là luận văn về **đặc trưng tin tức và chất lượng thông tin**, không phải nhiều LLM.
2. ML vẫn có vai trò rõ: baseline, decision candidate, semantic signal audit, outcome review.
3. LLM/AI chỉ giải quyết vấn đề thiếu label.
4. Dùng được dữ liệu giá và tin tức full-text đã có.
5. Kế thừa được kết quả âm của keyword/sentiment/news-as-feature.
6. Có tính mới hơn generic GitHub nhờ relevance/materiality/event/direction/evidence span.
7. Có point-in-time evidence, claim ledger, outcome review.
8. Có evaluation rõ dù chưa có human labels đầy đủ.

Định vị cuối:

> Luận văn nghiên cứu **semantic representation của tin tức chứng khoán Việt Nam trong pipeline hỗ trợ phân tích có ML signal và outcome review**, với LLM đóng vai trò công cụ annotation/extraction tạm thời, nhằm giải thích và cải thiện cách dùng tin tức trong phân tích cổ phiếu.
