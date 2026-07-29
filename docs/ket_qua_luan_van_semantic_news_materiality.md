# Kết quả luận văn: Semantic News Materiality Study

> Bản cập nhật sau khi bổ sung annotator C bằng ChatGPT qua router Claude (`cx/gpt-5.4-mini`). Nội dung dùng cho Chương 4 và phần thảo luận Chương 5. Kết quả phục vụ nghiên cứu học thuật, không phải khuyến nghị đầu tư.

---

## 4.1. Mục tiêu thực nghiệm

Các thí nghiệm keyword/news-count trước đây cho thấy tin tức dạng tần suất từ khóa không cải thiện dự báo giá ổn định so với technical-only baseline. Nhánh Semantic News Materiality Study được bổ sung để kiểm tra giả thuyết khác: vấn đề không nằm ở việc tin tức vô dụng, mà nằm ở cách biểu diễn tin tức quá thô.

Thay vì chỉ đếm keyword, nghiên cứu gán nhãn tin theo các trục:

- `ticker_relevance`: tin liên quan trực tiếp/gián tiếp/thị trường chung/không liên quan;
- `materiality`: mức độ trọng yếu tài chính;
- `direction`: support/risk/neutral/mixed;
- `event_type`: loại sự kiện;
- `time_horizon`: horizon tác động;
- `evidence_span`: đoạn bằng chứng trong bài báo.

Mục tiêu chính không phải chứng minh LLM tạo alpha, mà là xây dựng framework audit tin tức có kiểm soát: pseudo-labeling, agreement, rule comparison, event-window audit, evidence card và outcome review.

---

## 4.2. Dữ liệu annotation

Tập mẫu annotation gồm 150 bài lấy từ `data/news/enriched/all_news_enriched.csv`. Trước khi chọn mẫu, corpus được lọc trùng theo URL, content hash và title.

| Bước | Số dòng |
|---|---:|
| Trước dedup | 52.790 |
| Sau URL dedup | 45.968 |
| Sau content hash dedup | 44.462 |
| Sau title dedup | 43.198 |
| Mẫu annotation | 150 |

Mẫu được stratified theo 7 nhóm:

| Nhóm tin | Số bài |
|---|---:|
| Debt/legal/governance risk | 25 |
| Earnings/business result | 25 |
| Market/sector/macro | 25 |
| Dividend/capital | 20 |
| Generic/company announcement | 20 |
| Project/business expansion | 20 |
| Noisy/low-confidence match | 15 |

Nguồn tin gồm CafeF, Vietstock, Kinh Tế Chứng Khoán, VietnamBiz, VnExpress và TNCK. Mẫu có đủ các trường chính như ticker, date, source, title, description, full_text, url và match_confidence.

---

## 4.3. Annotation protocol và 3 annotators

Protocol annotation có các nguyên tắc:

- không đưa future return, target label, prediction hoặc outcome vào prompt;
- LLM chỉ dùng article payload được cung cấp;
- output phải hợp JSON schema;
- `evidence_span` phải khớp chính xác với text;
- pseudo-label không phải ground truth;
- case disagreement/score outlier được đưa vào human review queue.

Đã chạy 3 annotators:

| Annotator | Provider/model | Valid labels | Errors |
|---|---|---:|---:|
| A | DeepSeek `deepseek-chat` | 150 | 0 |
| B | DeepSeek `deepseek-chat` | 150 | 0 |
| C | ChatGPT router `cx/gpt-5.4-mini` | 150 | 0 |

Điểm nâng cấp quan trọng: annotator C khác provider/model với A/B. Điều này làm kết quả mạnh hơn vì không chỉ dựa vào 2 annotators cùng DeepSeek.

---

## 4.4. Agreement giữa annotators

Pairwise agreement sau khi thêm ChatGPT C:

| Field | Pair | Agreement | Cohen Kappa |
|---|---|---:|---:|
| ticker_relevance | A-B | 0,9867 | 0,9408 |
| ticker_relevance | A-C | 0,9000 | 0,6325 |
| ticker_relevance | B-C | 0,8867 | 0,5917 |
| materiality | A-B | 0,9467 | 0,9183 |
| materiality | A-C | 0,7267 | 0,5772 |
| materiality | B-C | 0,7200 | 0,5669 |
| direction | A-B | 0,9667 | 0,9518 |
| direction | A-C | 0,7800 | 0,6811 |
| direction | B-C | 0,7600 | 0,6532 |
| event_type | A-B | 0,9733 | 0,9695 |
| event_type | A-C | 0,8467 | 0,8252 |
| event_type | B-C | 0,8400 | 0,8176 |
| time_horizon | A-B | 0,9267 | 0,8868 |
| time_horizon | A-C | 0,6867 | 0,5332 |
| time_horizon | B-C | 0,6533 | 0,4845 |

Diễn giải:

- DeepSeek A/B agreement rất cao, cho thấy prompt/schema ổn định trong cùng provider.
- ChatGPT C vẫn đồng thuận khá tốt ở `ticker_relevance` và `event_type`.
- `materiality` và `time_horizon` khó hơn, agreement thấp hơn rõ rệt.
- Kết quả này làm luận văn mạnh hơn vì chỉ ra field nào ổn định, field nào cần human review.

---

## 4.5. Consensus 3 annotators

Consensus sau khi thêm annotator C vẫn gồm 150 dòng.

| Chỉ số | Giá trị |
|---|---:|
| Consensus rows | 150 |
| Unanimous consensus (tất cả categorical fields và stock relevance 3/3) | 40 |
| Majority vote (ít nhất một field 2/3, không có categorical disagreement) | 106 |
| Disagreement consensus | 4 |
| Analysis eligible | 122 |
| Requires human review | 82 |
| Evidence span missing/disputed | 13 |

Consensus đã sửa semantics: chỉ 3/3 trên mọi categorical field và stock relevance mới gọi là `unanimous`; 2/3 là `majority_vote`. `analysis_eligible` loại rows có provenance conflict, categorical consensus không khả dụng, relevance/materiality/direction không đủ rõ, hoặc evidence span thiếu/tranh chấp. Human-review queue vẫn chỉ là kiểm soát chất lượng, không biến pseudo-label thành ground truth.

Phân phối consensus chính:

### Ticker relevance

| Label | Số bài |
|---|---:|
| direct | 132 |
| market_wide | 9 |
| irrelevant | 8 |
| indirect | 1 |

### Materiality

| Label | Số bài |
|---|---:|
| low | 69 |
| medium | 46 |
| high | 32 |
| unclear | 2 |
| disagreement | 1 |

### Direction

| Label | Số bài |
|---|---:|
| neutral | 63 |
| support | 48 |
| risk | 18 |
| mixed | 12 |
| unclear | 7 |
| disagreement | 2 |

### Event type

| Event type | Số bài |
|---|---:|
| capital | 27 |
| governance | 25 |
| earnings | 19 |
| debt | 18 |
| dividend | 17 |
| other | 16 |
| market | 13 |
| legal | 4 |
| macro | 4 |
| project | 3 |
| ma | 1 |
| analyst | 1 |
| sector | 1 |
| disagreement | 1 |

Kết quả này cho thấy phần lớn sample là tin direct nhưng không phải tất cả đều high materiality. Nhóm low/neutral vẫn lớn, xác nhận rằng news-count/keyword-count dễ phóng đại tín hiệu nếu không xét materiality.

---

## 4.6. Manual sanity check

Manual sanity check được cập nhật sau consensus 3 annotators. Tổng cộng 24 bài được kiểm tra.

| Field kiểm tra | OK | Not OK |
|---|---:|---:|
| Relevance | 23 | 1 |
| Materiality | 21 | 3 |
| Direction | 23 | 1 |
| Event type | 24 | 0 |
| Evidence span | 23 | 1 |

Kết quả cho thấy event type, relevance, direction và evidence span nhìn chung ổn. Materiality vẫn là field khó nhất, phù hợp với agreement thấp hơn giữa DeepSeek và ChatGPT. Đây là limitation quan trọng nhưng cũng là insight có giá trị: materiality cần rubric chặt hơn hoặc human validation lớn hơn.

---

## 4.7. Rule baseline vs semantic pseudo-labels

So sánh rule/keyword baseline với consensus mới:

| So sánh | Accuracy | Macro-F1 | N |
|---|---:|---:|---:|
| rule_direction vs consensus_direction | 0,3770 | 0,2282 | 122 |
| rule_event_type vs consensus_event_type | 0,1475 | 0,0865 | 122 |
| rule_materiality vs consensus_materiality | 0,2213 | 0,1595 | 122 |
| rule_relevance vs consensus_ticker_relevance | 0,6885 | 0,2090 | 122 |

So sánh này chỉ dùng 122 rows `analysis_eligible`; các row consensus/evidence chưa đủ tin cậy không tham gia metric.

Kết quả gần như không thay đổi sau khi thêm ChatGPT C: keyword/rule baseline vẫn yếu rõ ở direction, event type và materiality. Điều này củng cố claim chính của luận văn: keyword frequency thiếu ngữ cảnh và không đủ để biểu diễn chất lượng tin tức.

Lỗi chính:

1. Keyword thiếu ngữ cảnh phủ định/trung tính.
2. Keyword không đo được materiality.
3. Market-wide news bị đếm như direct ticker signal.
4. Tin thủ tục/boilerplate có ticker nhưng impact thấp.
5. Direction mixed không thể biểu diễn bằng rule một chiều.
6. Event type overlap.

---

## 4.8. Semantic signal audit và kiểm định thống kê

Event-window audit gồm 456 outcome rows từ 122 rows `analysis_eligible`, cho T+1, T+5, T+20 và T+60. Tin thiếu giờ xuất bản map sang phiên giao dịch kế tiếp; metric chính là `market_adjusted_return = stock_return - VNINDEX_return`.

### Mean VNINDEX-adjusted return theo materiality

| Window | High | Medium | Low |
|---|---:|---:|---:|
| T+1 | 0,0051 | 0,0018 | 0,0012 |
| T+5 | 0,0092 | 0,0147 | -0,0108 |
| T+20 | 0,0118 | 0,0203 | -0,0213 |
| T+60 | 0,0086 | -0,0084 | -0,0425 |

Nhóm low materiality thấp hơn high/medium ở các cửa sổ dài hơn, nhưng đây vẫn là mô tả event sample, không phải quan hệ nhân quả.

### Mean VNINDEX-adjusted return theo direction

| Window | Support | Risk | Neutral |
|---|---:|---:|---:|
| T+1 | 0,0052 | -0,0028 | 0,0008 |
| T+5 | 0,0124 | 0,0043 | -0,0089 |
| T+20 | 0,0228 | -0,0014 | -0,0201 |
| T+60 | 0,0042 | -0,0152 | -0,0409 |

Pattern support thường dương hơn risk/neutral, nhưng uncertainty lớn và không đồng nhất giữa cửa sổ.

### Statistical tests exploratory đã hiệu chỉnh

Primary sample loại event overlap theo ticker/window. Mann–Whitney dùng tie correction; toàn bộ tám hypotheses dùng Benjamini–Hochberg; 95% CI dùng deterministic cluster bootstrap theo ticker.

| Comparison | Window | Diff mean | BH p-value | 95% CI | Robust gate |
|---|---|---:|---:|---:|---|
| support vs risk | T+1 | 0,0080 | 0,3069 | [-0,0013; 0,0175] | Không |
| high+medium vs low | T+1 | 0,0020 | 0,6278 | [-0,0046; 0,0089] | Không |
| support vs risk | T+5 | 0,0081 | 0,3069 | [-0,0245; 0,0338] | Không |
| high+medium vs low | T+5 | 0,0223 | 0,0457 | [0,0091; 0,0366] | Có |
| support vs risk | T+20 | 0,0249 | 0,3972 | [-0,0318; 0,0783] | Không |
| high+medium vs low | T+20 | 0,0397 | 0,1301 | [0,0065; 0,0735] | Không |
| support vs risk | T+60 | 0,0205 | 0,9722 | [-0,0533; 0,1023] | Không |
| high+medium vs low | T+60 | 0,0399 | 0,2306 | [-0,0117; 0,0914] | Không |

Chỉ comparison materiality T+5 vượt đồng thời BH-FDR 5% và CI dương. Direction comparisons không vượt claim gate. Kết quả vẫn exploratory/non-causal do pseudo-label, sample chọn lọc và residual confounding.

---

## 4.9. ML outperform experiment

Target chính:

```text
excess_return_T20 = stock_return_T20 - VNINDEX_return_T20
label_outperform_T20 = 1 nếu excess_return_T20 > 0
```

Experiment dùng ba expanding walk-forward folds, purge 20 phiên cho target T+20; imputer/scaler/model fit riêng từng fold. Predictions chỉ chứa OOS rows. Bảng dưới dùng fold-mean classification accuracy để tóm tắt trực tiếp artifact prediction:

| Config | Model | Fold mean accuracy | Fold std | Delta vs cùng model technical-only |
|---|---|---:|---:|---:|
| A Technical | Logistic Regression | 0,4957 | 0,0161 | 0,0000 |
| A Technical | Random Forest | 0,5026 | 0,0164 | 0,0000 |
| B Technical+Keyword | Logistic Regression | 0,4892 | 0,0090 | -0,0066 |
| B Technical+Keyword | Random Forest | 0,4983 | 0,0201 | -0,0043 |
| C Technical+Semantic | Logistic Regression | 0,4918 | 0,0046 | -0,0040 |
| C Technical+Semantic | Random Forest | 0,5102 | 0,0162 | +0,0076 |
| D All | Logistic Regression | 0,4909 | 0,0150 | -0,0048 |
| D All | Random Forest | 0,5099 | 0,0069 | +0,0072 |

Semantic Random Forest có delta dương nhỏ so technical-only, nhưng Logistic Regression không cải thiện. Chênh lệch nhỏ và không có uncertainty test xác nhận superiority; claim ML giữ ở mức exploratory/không ổn định, không phải predictive alpha.

---

## 4.10. Top-K simulation

Top-K simulation chỉ dùng OOS predictions, Top-5/Top-10, holding T+20 trên 54 cửa sổ không overlap. Chi phí mỗi kỳ bằng `0,50% × turnover`, với turnover equal-weight `0.5 × Σ|w_t − w_{t-1}|`. Sharpe annualize bằng `sqrt(252/20)`.

Tóm tắt `model_topk` Top-5:

| Config | Model | Periods | Mean net return | Mean net excess return |
|---|---|---:|---:|---:|
| A Technical | Logistic Regression | 54 | 0,0002 | -0,0049 |
| A Technical | Random Forest | 54 | 0,0087 | 0,0036 |
| B Technical+Keyword | Logistic Regression | 54 | 0,0063 | 0,0012 |
| B Technical+Keyword | Random Forest | 54 | 0,0015 | -0,0036 |
| C Technical+Semantic | Logistic Regression | 54 | 0,0050 | -0,0001 |
| C Technical+Semantic | Random Forest | 54 | 0,0044 | -0,0007 |
| D All | Logistic Regression | 54 | 0,0090 | 0,0039 |
| D All | Random Forest | 54 | 0,0072 | 0,0021 |

Top-5 semantic-only augmentation không vượt technical-only Random Forest theo mean net excess return. Một số `D_all`/Top-10 cấu hình dương hơn baseline, nhưng model ordering thiếu ổn định và chưa có paired uncertainty đủ mạnh. Top-K là secondary exploratory simulation, không phải bằng chứng alpha hoặc chiến lược giao dịch.

---

## 4.11. Evidence cards và outcome review

Evidence cards gồm 5 case patterns đại diện:

- keyword positive nhưng semantic low;
- keyword positive nhưng irrelevant;
- keyword missed high materiality;
- direct high materiality risk;
- direct high materiality mixed direction.

Outcome review có 150 rows:

| Outcome label | Số case |
|---|---:|
| not_price_relevant | 68 |
| confirmed | 31 |
| contradicted | 26 |
| unresolved | 25 |

Tỷ lệ `not_price_relevant` cao phù hợp với kết quả materiality: nhiều bài có thông tin đúng nhưng không kỳ vọng phản ứng giá rõ. Outcome review là post-hoc và không được dùng làm nhãn ground truth.

---

## 4.12. Claim-vs-evidence summary

Bảng claim-vs-evidence được lưu tại `multi_llm_evidence_extraction/reports/claim_vs_evidence_table.md`. Tóm tắt:

| Claim | Mức độ |
|---|---|
| Keyword/news-count thiếu ngữ cảnh | Mạnh |
| DeepSeek A/B schema agreement cao | Mạnh |
| ChatGPT C cross-model check chỉ ra field khó | Mạnh cho robustness/limitation |
| 3-annotator consensus ổn định, nhưng human review queue lớn hơn | Mạnh |
| Manual sanity check ủng hộ nhãn | Vừa |
| Event-window direction/materiality có tín hiệu hợp lý | Vừa / exploratory |
| ML/Top-K có tiềm năng ranking | Yếu / exploratory |
| Evidence card/outcome review tăng truy vết | Vừa |

---

## 4.13. Kết luận kết quả

Sau khi bổ sung ChatGPT annotator C, chất lượng luận văn tăng rõ ở phần robustness. Trước đây A/B DeepSeek agreement rất cao, nhưng có thể bị nghi ngờ correlated error do cùng provider. Kết quả mới cho thấy khi thêm model khác provider, các label dễ như event type và relevance vẫn tương đối ổn, trong khi materiality và time horizon bộc lộ khó khăn hơn. Đây là kết quả tốt cho luận văn vì vừa tăng độ tin cậy vừa giúp xác định limitation thật.

Kết quả rule baseline tiếp tục yếu so với semantic consensus trên sample `analysis_eligible`, ủng hộ nhận định keyword/news-count thiếu ngữ cảnh tài chính. Event-window audit chỉ có comparison materiality T+5 vượt BH-FDR và CI gate; direction chưa robust. ML cho delta nhỏ, phụ thuộc model; Top-K semantic Top-5 không vượt technical-only Random Forest. Các kết quả định lượng phụ vẫn exploratory và không hỗ trợ claim alpha.

Kết luận an toàn:

> Tin tức tài chính tiếng Việt không nên chỉ được biểu diễn bằng tần suất keyword. Semantic representation theo relevance, materiality, direction, event type và evidence span giúp audit chất lượng tin tức tốt hơn, chỉ ra nguồn nhiễu của keyword baseline, tạo claim có thể truy vết và hỗ trợ outcome review. Giá trị chính của nghiên cứu nằm ở framework kiểm soát và minh bạch hóa news-as-feature, không phải ở việc chứng minh LLM hoặc semantic features tạo lợi nhuận đầu tư ổn định.
