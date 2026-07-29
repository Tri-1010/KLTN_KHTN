# ĐỀ CƯƠNG CHI TIẾT LUẬN VĂN / KHÓA LUẬN

## Tên đề tài đề xuất

**Hệ thống hỗ trợ quyết định đầu tư cổ phiếu Việt Nam dựa trên tín hiệu học máy và LLM tạo luận điểm từ bằng chứng tin tức**

Tên tiếng Anh:

**An ML-Led Investment Decision Support System for Vietnamese Stocks with LLM-Generated Evidence-Grounded Decision Cards**

---

## 0. Định vị cuối cùng của đề tài

Đề tài không định vị là hệ thống dự báo giá cổ phiếu bằng LLM. Đề tài định vị là một hệ thống hỗ trợ quyết định đầu tư, trong đó:

- **ML kỹ thuật** là lõi định lượng, tạo xác suất tăng/giảm, rank và danh sách ứng viên.
- **Tin tức** không được ép làm predictor chính vì kết quả keyword/frequency/sentiment không cải thiện forecast ổn định.
- **LLM** được dùng để tạo decision card/evidence-grounded investment thesis, không dự báo giá trực tiếp.
- **Monitoring và outcome review** giúp theo dõi, cập nhật và hậu kiểm vòng đời quyết định.

Câu chốt:

> Luận văn không chứng minh LLM hay tin tức tạo alpha ổn định. Luận văn chứng minh một thiết kế thực tế hơn: ML tạo tín hiệu định lượng, tin tức cung cấp bằng chứng, LLM tạo luận điểm có kiểm soát, monitoring và outcome review giúp quản trị vòng đời quyết định đầu tư.

---

## 1. Lý do chọn đề tài

### 1.1. Bối cảnh thực tiễn

Thị trường chứng khoán Việt Nam tạo ra lượng lớn dữ liệu từ nhiều nguồn:

- dữ liệu giá và khối lượng giao dịch;
- chỉ báo kỹ thuật;
- tin tức tài chính;
- công bố doanh nghiệp;
- thông tin ngành và vĩ mô.

Nhà đầu tư không chỉ cần biết cổ phiếu nào có khả năng tăng, mà còn cần hiểu:

- vì sao cổ phiếu được mô hình chọn;
- tín hiệu kỹ thuật nào đóng góp chính;
- tin tức nào ủng hộ hoặc làm suy yếu luận điểm;
- rủi ro cần theo dõi là gì;
- khi nào cần review quyết định;
- sau kỳ nắm giữ, quyết định đúng/sai vì nguyên nhân nào.

Vì vậy, khoảng cách nghiên cứu nằm ở bước chuyển từ **model output** sang **decision record có thể giải thích, theo dõi và hậu kiểm**.

### 1.2. Bối cảnh học thuật

Các nghiên cứu truyền thống về dự báo cổ phiếu thường dùng:

- technical indicators;
- TF-IDF/Bag-of-Words;
- sentiment dictionary;
- event extraction;
- BERT/FinBERT/PhoBERT;
- gần đây là LLM.

Research ngoài cho thấy hướng semantic/event extraction có cơ sở:

- Ding et al. (2015) cho thấy event-driven stock prediction vượt bag-of-words baseline.
- Xu & Cohen (2018) cho thấy joint text-price model phù hợp hơn price-only/text-only.
- FinBERT (Araci, 2019) cho thấy ngôn ngữ tài chính cần domain adaptation.
- Lopez-Lira & Tang (2023) cho thấy GPT-4 có thể trích xuất tín hiệu từ financial headlines, nhưng cần kiểm soát tradability/leakage.
- Nghiên cứu Việt Nam Le et al. (2022) mới dùng SVM bag-of-words cho VN-Index, đạt 60.1% accuracy; chưa có hướng LLM/evidence-grounded decision support.

### 1.3. Bài học từ kết quả hiện có

Kết quả local cho thấy:

- Technical ML có tín hiệu mạnh nhất: BA khoảng 0.76, AUC khoảng 0.83, backtest net return khoảng 60.3% so với benchmark 25.4%, Sharpe khoảng 1.05.
- Keyword/frequency/sentiment/distant supervision không cải thiện forecast ổn định.
- LLM semantic features có vài cấu hình dương nhưng mixed, mean effect gần 0, rủi ro multiple testing.
- Decision-support artifacts đã có: evidence packs, decision cards, monitoring events, outcome reviews, LLM full-evidence cards và rubric.

Do đó, đề tài nên pivot từ “LLM/news forecast” sang “ML-led decision support”.

---

## 2. Vấn đề nghiên cứu

### 2.1. Vấn đề chính

Mô hình ML có thể tạo tín hiệu tăng/giảm hoặc ranking cổ phiếu, nhưng tín hiệu đó chưa đủ để sử dụng trong quy trình đầu tư vì thiếu:

1. giải thích có cấu trúc;
2. bằng chứng định tính từ tin tức;
3. rủi ro và điều kiện theo dõi;
4. cơ chế cập nhật khi bối cảnh thay đổi;
5. outcome review để tránh hindsight bias.

### 2.2. Vấn đề phụ

1. Tin tức dạng keyword/frequency không cải thiện forecast ổn định.
2. LLM semantic labels chưa đủ robust nếu không có human validation.
3. LLM có rủi ro hallucination nếu không ràng buộc evidence.
4. Backtest dễ overclaim nếu không nói rõ giả định.
5. Up/down classification quá đơn giản nếu không gắn với probability/ranking/backtest/monitoring.

### 2.3. Khoảng trống nghiên cứu

Ở thị trường Việt Nam, các nghiên cứu NLP-finance còn ít, chủ yếu dùng text mining/Bag-of-Words/SVM. Chưa thấy nghiên cứu đầy đủ về:

- ML signal + evidence pack point-in-time;
- LLM-generated decision cards có guardrails;
- monitoring và outcome review sau khuyến nghị;
- phân biệt rõ news-as-predictor và news-as-evidence.

---

## 3. Mục tiêu nghiên cứu

### 3.1. Mục tiêu tổng quát

Xây dựng và đánh giá prototype hệ thống hỗ trợ quyết định đầu tư cổ phiếu Việt Nam kết hợp ML signal, tin tức công khai và LLM-generated decision cards theo vòng đời:

**select → explain → monitor → update → review**

### 3.2. Mục tiêu cụ thể

1. Đóng gói ML technical signal engine để dự báo xu hướng tăng/giảm và xếp hạng cổ phiếu.
2. Đánh giá ML signal bằng classification metrics, backtest, walk-forward và robustness.
3. Tổng hợp kết quả âm của keyword/news features để xác định đúng vai trò của news.
4. Thiết kế evidence pack point-in-time gồm ML signal, technical drivers, news evidence, data quality flags.
5. Dùng LLM tạo decision cards từ evidence pack, theo schema và guardrails.
6. Đánh giá decision cards bằng rubric: faithfulness, hallucination control, ML explanation, risk awareness, monitoring usefulness, clarity.
7. Thiết kế monitoring events và outcome reviews để hậu kiểm quyết định.
8. Trình bày hạn chế: leakage, multiple testing, LLM pseudo-label, backtest assumptions, data quality.

---

## 4. Câu hỏi nghiên cứu

### RQ1. ML technical signal có tạo tín hiệu hữu ích cho lựa chọn cổ phiếu Việt Nam không?

Đánh giá bằng:

- Balanced Accuracy;
- AUC-ROC;
- F1-macro;
- Precision/Recall;
- robustness trên universe mở rộng;
- leakage audit.

Kỳ vọng trả lời: Có, trong phạm vi dữ liệu và giả định nghiên cứu.

### RQ2. Chiến lược Top-K long-only dựa trên ML signal có vượt benchmark không?

Đánh giá bằng:

- cumulative return;
- Sharpe ratio;
- max drawdown;
- hit rate;
- walk-forward;
- benchmark buy-hold/equal-weight/VNINDEX.

Kỳ vọng trả lời: Có trong backtest hiện tại, nhưng không claim triển khai thực tế.

### RQ3. News features dạng keyword/frequency/sentiment/semantic có cải thiện forecast không?

Đánh giá bằng:

- Config_A technical-only;
- Config_B news-only;
- Config_C technical + news;
- McNemar/p-value;
- BH-FDR;
- sensitivity across horizons/sources/universe.

Kỳ vọng trả lời: Keyword/frequency/sentiment không cải thiện ổn định; LLM semantic chỉ có tín hiệu cục bộ/exploratory.

### RQ4. Nếu news không tạo alpha ổn định, news có thể dùng làm evidence layer cho decision-support không?

Đánh giá bằng:

- evidence coverage;
- data quality flags;
- case studies;
- decision-card usefulness;
- monitoring and outcome review.

Kỳ vọng trả lời: Có thể, nếu ràng buộc point-in-time và kiểm soát quality.

### RQ5. LLM full-evidence decision card có tốt hơn rule-based/ML-only card theo rubric chất lượng không?

Đánh giá bằng:

- 25 rule-based baseline cards;
- 25 LLM ML-only cards;
- 25 LLM full-evidence cards;
- rubric scores.

Kỳ vọng trả lời: Full-evidence LLM cards đạt điểm cao hơn về decision-card quality, không phải return.

---

## 5. Phạm vi nghiên cứu

| Hạng mục | Phạm vi |
|---|---|
| Thị trường | Cổ phiếu Việt Nam |
| Universe chính | HOSE-80 |
| Robustness | 125 mã HOSE+HNX |
| Giai đoạn dữ liệu | 2022–2026 theo dữ liệu hiện có |
| Dữ liệu giá | OHLCV, technical features |
| Dữ liệu news | CafeF, Vietstock, TNCK, VnExpress, Kinh tế chứng khoán, nguồn đã crawl |
| Bài toán ML | Direction classification + Top-K ranking |
| LLM | Decision-card generation, not price forecasting |
| Đánh giá đầu tư | Long-only backtest, không short, không robo-advisor |
| Hệ thống | Prototype nghiên cứu |

---

## 6. Giả thuyết / kỳ vọng nghiên cứu

Không nên đặt hypothesis quá mạnh kiểu “LLM tạo alpha”. Dùng các giả thuyết mềm:

### H1. Technical ML signal hữu ích

Mô hình kỹ thuật vượt baseline phân loại và tạo portfolio return tốt hơn benchmark trong backtest.

### H2. News-as-predictor yếu

Đặc trưng keyword/frequency/sentiment không cải thiện forecast ổn định so với technical-only.

### H3. LLM semantic feature chỉ bổ sung có điều kiện

LLM semantic features có thể tạo tín hiệu cục bộ trong một số cấu hình material-event/horizon, nhưng chưa đủ robust để làm main claim.

### H4. News-as-evidence hữu ích hơn news-as-predictor

Tin tức phù hợp hơn cho giải thích, risk awareness, monitoring và outcome review.

### H5. LLM full-evidence cards cải thiện chất lượng trình bày quyết định

Full-evidence LLM cards đạt điểm rubric cao hơn rule-based baseline và ML-only card ở faithfulness/risk/clarity/monitoring, nhưng không chứng minh return.

---

## 7. Đóng góp dự kiến

### 7.1. Đóng góp học thuật

1. Cung cấp kết quả thực nghiệm rõ ràng rằng keyword/news features không cải thiện forecast ổn định trong bối cảnh dữ liệu Việt Nam.
2. Đề xuất framing chuyển từ news-as-predictor sang news-as-evidence.
3. Đưa LLM vào vai trò controlled explanation layer thay vì forecasting oracle.
4. Kết hợp ML signal, evidence pack, decision card, monitoring và outcome review thành vòng đời quyết định.

### 7.2. Đóng góp kỹ thuật

1. ML Signal Engine với technical features.
2. Evidence Pack Builder point-in-time.
3. Rule-based baseline decision cards.
4. Gemini Pro full-evidence LLM decision cards.
5. Rubric scoring 75 cards.
6. Monitoring timeline và outcome reviews.
7. Leakage guardrails cho cả ML và LLM.

### 7.3. Đóng góp thực tiễn

1. Giảm khoảng cách giữa model score và investment memo.
2. Tạo audit trail cho quyết định đầu tư.
3. Hỗ trợ nhà phân tích kiểm tra lại thesis ban đầu.
4. Giảm overconfidence bằng cách buộc nêu rủi ro và data quality flags.

---

## 8. Tổng quan tài liệu cần viết

### 8.1. ML trong dự báo cổ phiếu

Nội dung cần có:

- Efficient Market Hypothesis và giới hạn dự báo.
- Direction classification vs return regression vs ranking.
- Technical indicators trong ML.
- Tree-based models: Random Forest, XGBoost, LightGBM.
- Time-series split, walk-forward, backtest.

Nguồn gợi ý:

- Fama (1970), Efficient Capital Markets.
- Breiman (2001), Random Forests.
- Chen & Guestrin (2016), XGBoost.
- Ke et al. (2017), LightGBM.

### 8.2. NLP/news trong tài chính

Nội dung cần có:

- Bag-of-Words/TF-IDF/sentiment dictionary.
- Event extraction.
- Domain-specific financial language.
- Tại sao keyword thô yếu.

Nguồn gợi ý:

- Tetlock (2007), media pessimism and stock market.
- Schumaker & Chen (2009), textual analysis for stock prediction.
- Ding et al. (2015), event-driven stock prediction.
- Loughran & McDonald or survey on textual analysis.

### 8.3. LLM trong tài chính

Nội dung cần có:

- FinBERT/domain adaptation.
- GPT-4 headline sentiment evidence.
- FinGPT data-centric financial LLM.
- LLM agents/decision support.
- Hallucination and RAG/evidence-grounded generation.

Nguồn gợi ý:

- Araci (2019), FinBERT.
- Lopez-Lira & Tang (2023), Can ChatGPT Forecast Stock Price Movements?
- Yang et al. (2023), FinGPT.
- FinMem/FinAgent as broader context, dùng cẩn thận vì trading-agent claims dễ tranh cãi.

### 8.4. Nghiên cứu tại Việt Nam

Nội dung cần có:

- Le et al. (2022): Vietnamese financial news, 70,000 articles, SVM bag-of-words, VN-Index next-day direction, 60.1% accuracy.
- Khoảng trống: chưa có evidence-grounded LLM decision-support cho cổ phiếu Việt Nam.

---

## 9. Dữ liệu và pipeline

### 9.1. Dữ liệu giá

- OHLCV ngày.
- Aggregation theo quarter/period.
- Tạo labels cho kỳ tiếp theo.
- Universe HOSE-80 và HOSE+HNX-125.

### 9.2. Dữ liệu news

- Raw news từ nhiều nguồn.
- Matching ticker.
- Preprocessing.
- Enrichment: article summary, key facts, risk flags.
- Evidence filtering theo `published_at <= decision_date`.

### 9.3. Pipeline tổng thể

```text
OHLCV ──> Technical Features ──> ML Signal Engine ──> Top-K Candidates
                                                        │
News ──> Matching/Enrichment ──> News Evidence ─────────┤
                                                        ▼
                                                Evidence Pack
                                                        ▼
                                    Rule-based / LLM Decision Card
                                                        ▼
                                         Monitoring + Outcome Review
```

---

## 10. Thiết kế thực nghiệm

### 10.1. Experiment A: Technical ML baseline

Mục tiêu: kiểm tra ML technical signal.

Models:

- Logistic Regression;
- Random Forest;
- XGBoost;
- LightGBM.

Metrics:

- BA;
- AUC;
- F1 Macro;
- Precision/Recall;
- calibration nếu kịp.

Expected evidence:

- BA khoảng 0.76;
- AUC khoảng 0.83;
- robustness trên 125 mã.

### 10.2. Experiment B: News-as-predictor negative result

Mục tiêu: chứng minh keyword/news thô không cải thiện ổn định.

Configs:

- Config_A: technical-only;
- Config_B: keyword/news-only;
- Config_C: technical + keyword/news.

Evidence:

- Config_C không vượt Config_A;
- H2: 0 keyword qua BH-FDR;
- A6/B1/A7 không significant.

### 10.3. Experiment C: LLM semantic features exploratory

Mục tiêu: trình bày có kiểm soát, không overclaim.

Nội dung:

- material event features;
- direct materiality;
- horizon sensitivity;
- HOSE100 variant sweep;
- p-values và multiple-testing caution.

Kết luận an toàn:

> LLM semantic features có tín hiệu cục bộ nhưng chưa robust toàn cục; phù hợp làm hướng mở rộng hoặc evidence enrichment hơn là main alpha source.

### 10.4. Experiment D: Decision-support artifacts

Mục tiêu: đánh giá hệ thống hỗ trợ quyết định.

Artifacts:

- 25 evidence packs;
- 25 rule-based cards;
- 25 LLM ML-only cards;
- 25 LLM full-evidence cards;
- 75 rubric scores;
- 3,838 monitoring events;
- 25 outcome reviews.

Metrics:

- rubric score;
- hallucination count;
- missing references;
- data quality flags;
- case studies.

### 10.5. Experiment E: Case studies

Chọn 3–5 case sạch:

1. ML đúng và evidence hỗ trợ.
2. ML sai nhưng monitoring cảnh báo.
3. News trái chiều với ML.
4. Evidence yếu/data quality warning.
5. LLM full-evidence card tốt hơn ML-only.

---

## 11. Kết quả hiện có cần đưa vào luận văn

### 11.1. ML metrics

| Chỉ số | Giá trị chính |
|---|---:|
| BA technical ML | ~0.76 |
| AUC technical ML | ~0.83 |
| Robustness BA 125 mã | 0.7607 |
| Robustness AUC 125 mã | 0.8307 |
| Backtest net return | 0.602964 |
| Benchmark return | 0.253502 |
| Net Sharpe | 1.05171 |
| Walk-forward wins | 3/3 |

### 11.2. News negative findings

| Nhóm | Kết luận |
|---|---|
| Keyword frequency | Không cải thiện forecast ổn định |
| H2 keyword significance | 0 keyword qua BH-FDR |
| LLM sentiment A6 | Δ âm, p không significant |
| Distant supervision B1 | Δ nhỏ, p không significant |
| LLM semantic | Cục bộ có tín hiệu, toàn sweep mixed |

### 11.3. Decision support artifacts

| Artifact | Số lượng |
|---|---:|
| Evidence packs | 25 |
| ML-only packs | 25 |
| Rule-based cards | 25 |
| LLM ML-only cards | 25 |
| LLM full-evidence cards | 25 |
| Rubric scores | 75 |
| Monitoring news events | 3,838 |
| Positive realized returns | 19 |
| Negative/neutral realized returns | 6 |

### 11.4. Rubric results

| Card type | n | Overall | Major hallucinations | Missing refs |
|---|---:|---:|---:|---:|
| LLM full-evidence | 25 | 5.00 | 0 | 0 |
| Rule-based baseline | 25 | 4.32 | 2 | 15 |
| LLM ML-only | 25 | 1.16 | 43 | 114 |

Diễn giải đúng:

> Kết quả này đo quality của decision card, không đo lợi nhuận và không chứng minh LLM tạo alpha.

---

## 12. Threats to validity bắt buộc viết

### 12.1. Internal validity

- Look-ahead leakage.
- Outcome leakage into LLM prompts.
- Content-level leakage từ crawler/sidebar/future dates.
- Data preprocessing fit trên toàn bộ dữ liệu.

### 12.2. Statistical validity

- Multiple testing trong LLM semantic sweeps.
- p-value không correction.
- Small sample segments.
- Non-independent `(ticker, period)` observations.
- Backtest overfitting.

### 12.3. Construct validity

- Up/down labels không phản ánh magnitude/risk.
- Rubric score không phải investment return.
- LLM pseudo-label không phải human truth.
- News sentiment không đồng nghĩa expected return.

### 12.4. External validity

- Giai đoạn 2022–2026 có thể không đại diện tương lai.
- Universe chọn lọc.
- Thị trường Việt Nam có liquidity/limit/T+2.
- News coverage không đều.

### 12.5. LLM-specific risks

- Hallucination.
- Prompt sensitivity.
- Provider/model drift.
- Self-evaluation bias nếu LLM chấm LLM.
- Vietnamese financial language ambiguity.

---

## 13. Cấu trúc luận văn đề xuất

### Chương 1. Giới thiệu

1.1. Bối cảnh thị trường và bài toán

1.2. Khoảng cách giữa model output và decision support

1.3. Bài học từ news-as-predictor thất bại

1.4. Mục tiêu nghiên cứu

1.5. Câu hỏi nghiên cứu

1.6. Phạm vi và giới hạn

1.7. Đóng góp

1.8. Cấu trúc luận văn

### Chương 2. Cơ sở lý thuyết và nghiên cứu liên quan

2.1. ML trong stock direction prediction

2.2. Technical indicators và tabular ML

2.3. Financial news NLP: keyword, sentiment, event extraction

2.4. LLM/FinBERT/FinGPT trong tài chính

2.5. Explainable AI và SHAP

2.6. Decision support systems

2.7. Leakage, backtest overfitting và multiple testing

2.8. Khoảng trống nghiên cứu tại Việt Nam

### Chương 3. Dữ liệu và phương pháp

3.1. Tổng quan hệ thống

3.2. Dữ liệu giá và universe

3.3. News collection, matching, enrichment

3.4. Technical feature engineering

3.5. ML Signal Engine

3.6. News-as-predictor experiments

3.7. Evidence Pack Builder

3.8. LLM Decision Card Generator

3.9. Monitoring và Outcome Review

3.10. Evaluation design

3.11. Leakage guardrails

### Chương 4. Kết quả và thảo luận

4.1. ML technical baseline

4.2. Backtest và walk-forward

4.3. Robustness trên universe mở rộng

4.4. Negative result của keyword/news features

4.5. LLM semantic features: exploratory evidence

4.6. Evidence packs và decision cards

4.7. LLM full-evidence vs rule-based vs ML-only rubric

4.8. Monitoring và outcome review case studies

4.9. Tổng hợp: vì sao decision-support là hướng đúng

### Chương 5. Kết luận và hướng phát triển

5.1. Trả lời câu hỏi nghiên cứu

5.2. Đóng góp chính

5.3. Hạn chế

5.4. Threats to validity

5.5. Hướng phát triển

5.6. Kết luận cuối

---

## 14. Checklist phát triển tiếp

### Cần làm trước bản nộp

- [ ] Đổi title/narrative toàn bộ file sang ML-led decision support.
- [ ] Thêm bảng claim/evidence/limitation.
- [ ] Dọn 3–5 case study sạch.
- [ ] Audit content-level leakage trong selected cards.
- [ ] Viết mục Threats to Validity đầy đủ.
- [ ] Tách rõ result đã có và result exploratory/pending.
- [ ] Không để câu nào claim LLM alpha hoặc news forecast improvement.

### Nên làm nếu còn thời gian

- [ ] Random Top-K benchmark.
- [ ] Momentum/RSI/MACD rule benchmark.
- [ ] Probability calibration: Brier score/reliability curve.
- [ ] Human audit 100–300 news annotations.
- [ ] Cross-provider LLM stability test trên 50–100 bài.
- [ ] Content-level leakage scanner: future date/entity mismatch/boilerplate ratio.

### Có thể đưa vào hướng phát triển

- [ ] Event-time graph thay quarter aggregation.
- [ ] Human-in-the-loop annotation benchmark cho tin tài chính tiếng Việt.
- [ ] RAG/evidence-span citation thay summary-only.
- [ ] Daily mark-to-market backtest với slippage/liquidity/T+2.
- [ ] Paper-trading dashboard.

---

## 15. Câu trả lời hội đồng nên chuẩn bị

### Q1. Nếu news không cải thiện forecast, sao vẫn dùng news?

Vì forecast và decision support là hai bài toán khác nhau. News không ổn định khi ép thành predictor, nhưng hữu ích để giải thích bối cảnh, nêu rủi ro, tạo monitoring triggers và hậu kiểm thesis.

### Q2. LLM có đóng góp gì nếu không forecast?

LLM chuyển evidence pack thành decision card có cấu trúc, dễ đọc, có citations, có rủi ro và trigger. LLM không tạo signal định lượng.

### Q3. Up/down có quá đơn giản không?

Up/down chỉ là formulation cho ML signal. Hệ thống dùng probability, Top-K ranking, backtest, monitoring và outcome review. Không claim binary label đủ cho đầu tư.

### Q4. Backtest 60% có tin được không?

Tin trong phạm vi historical simulation. Đã kiểm temporal split và leakage audit, nhưng chưa mô phỏng đầy đủ slippage/liquidity/daily execution. Không claim triển khai thật.

### Q5. LLM decision card có được đánh giá khách quan không?

Có rubric cho faithfulness/hallucination/ML explanation/risk/monitoring/clarity, đã chấm 75 cards. Nhưng rubric đo card quality, không đo return; nếu triển khai thực tế cần thêm human evaluation.

### Q6. LLM semantic labels đúng không?

Hiện không claim semantic labels là ground truth. Nếu dùng làm predictive features, cần human-labeled benchmark. Trong luận văn, LLM chủ yếu dùng làm evidence-card generator có guardrails.

---

## 16. Kết luận đề cương

Hướng luận văn nên giữ là **ML-led investment decision support**, không phải **LLM semantic forecasting**. Đây là hướng có khả năng bảo vệ cao nhất vì:

1. khớp với kết quả định lượng mạnh của technical ML;
2. biến kết quả âm của keyword/news thành đóng góp khoa học;
3. dùng LLM ở vai trò an toàn hơn: explanation/evidence card;
4. có artifact thật để trình bày: packs, cards, rubric, monitoring, outcome reviews;
5. có ý nghĩa thực tiễn với nhà đầu tư/analyst nhưng không overclaim thành robo-advisor.
