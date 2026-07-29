# Task chi tiết: Semantic News Materiality Study

File này chuyển đề cương thành checklist triển khai. Nguyên tắc chính: **tận dụng tối đa dữ liệu/module đã có trong repo**, chỉ viết mới phần còn thiếu cho hướng semantic materiality / evidence / outcome review.

---

## 0. Tài sản đã có trong repo cần tận dụng

### 0.1. Dữ liệu giá

- [x] `data/prices/*.csv` — giá từng mã.
- [x] `data/prices/all_vn30_prices.csv` — giá VN30 hợp nhất.
- [x] `pipeline/task1_prices.py` — module tải/cập nhật giá.
- [x] `pipeline/task7_tech_features.py` — technical indicators.
- [x] `data/features/technical_features.csv` — technical features đã sinh.

Cách dùng:

- Không crawl/tải lại giá nếu file hiện có đủ giai đoạn nghiên cứu.
- Chỉ chạy lại `task1_prices.py` nếu cần cập nhật ngày mới hoặc sửa lỗi dữ liệu.
- Dùng technical features làm baseline ML chính.

### 0.2. Dữ liệu tin tức đã crawl + full text

- [x] `data/news/cafef/`
- [x] `data/news/vietstock/`
- [x] `data/news/tnck/tnck_raw.csv`
- [x] `data/news/vietnambiz/vietnambiz_raw.csv`
- [x] `data/news/vnexpress/vnexpress_raw.csv`
- [x] `data/news/kinhtechungkhoan/kinhtechungkhoan_raw.csv`
- [x] `data/news/matched/all_news_matched.csv`
- [x] `data/news/processed/all_news_processed.csv`
- [x] `data/news/enriched/all_news_enriched.csv` nếu tồn tại trong checkout hiện tại.
- [x] `.kiro/specs/news-source-expansion/tasks.md` ghi rõ full-text coverage gần như đủ.

Cách dùng:

- Không scrape lại từ đầu trừ khi cần mở rộng thời gian hoặc sửa source cụ thể.
- Dùng `all_news_processed.csv` cho annotation sample.
- Nếu cần full text tốt hơn, ưu tiên `all_news_enriched.csv` hoặc các cột `full_text`, `lead`, `article_summary`, `key_facts_json` đã được TASK 2B tạo.

### 0.3. Matching, preprocess, aggregate đã có

- [x] `config/entity_aliases.json`
- [x] `pipeline/task3_matching.py`
- [x] `pipeline/task4_preprocess.py`
- [x] `pipeline/task5_aggregate.py`

Cách dùng:

- Không viết lại entity matching từ đầu.
- Chỉ thêm data quality flags nếu cần cho semantic pipeline.
- Tận dụng `match_confidence`, `ticker`, `source`, `date`, `url`, `title`, `description`, `full_text`.

### 0.4. Keyword/news baseline đã có

- [x] `config/keywords_finance.json`
- [x] `config/keywords_by_group.json`
- [x] `data/features/keyword_features.csv`
- [x] `docs/keyword_features_note.md`
- [x] `pipeline/task8_keywords.py`
- [x] `pipeline/task9_kw_features.py`
- [x] `reports/H1_experiment_report.md`
- [x] `reports/H2_H3_validation_report.md`
- [x] `reports/experiment_A6_report.md`
- [x] `reports/experiment_B1_report.md`

Cách dùng:

- Giữ keyword làm baseline đối chứng.
- Không claim keyword vô dụng; claim đúng: keyword/frequency thiếu relevance/materiality/context.
- Dùng báo cáo cũ làm evidence cho Chương 1/4.

### 0.5. Annotation/LLM semantic đã có một phần

- [x] `data/news/annotated/llm_scorecard*.csv`
- [x] `data/news/annotated/a7_pilot_500_articles.csv`
- [x] `data/experiments/llm_semantic/article_semantics_cache.csv`
- [x] `data/experiments/llm_semantic/*annotations*.csv`
- [x] `pipeline/experiment_llm_semantic_features.py`
- [x] `scripts/annotate_hose100_extra_material.py`
- [x] `reports/llm_semantic_*summary.md`

Cách dùng:

- Tận dụng cache/annotation cũ để khảo sát nhanh.
- Nếu schema cũ thiếu `evidence_span`, `ticker_relevance`, `materiality`, `direction`, thì chạy lại annotation sample theo schema mới.
- Không bỏ kết quả cũ; dùng làm baseline/negative finding hoặc tiền đề.

### 0.6. Decision-support artifacts đã có

- [x] `scripts/generate_decision_support_artifacts.py`
- [x] `scripts/generate_llm_decision_cards.py`
- [x] `scripts/score_decision_cards.py`
- [x] `scripts/monitor_news_events.py`
- [x] `reports/decision_support/evidence_pack_schema.md`
- [x] `reports/decision_support/decision_card_schema.md`
- [x] `reports/decision_support/generated/evidence_packs.jsonl`
- [x] `reports/decision_support/generated/decision_cards.md`
- [x] `reports/decision_support/generated/outcome_reviews.md`
- [x] `reports/decision_support/generated/llm_rubric_summary.md`

Cách dùng:

- Tận dụng format evidence pack / decision card.
- Chỉnh lại framing: artifact hỗ trợ phân tích, không phải recommender.
- Outcome review cũ dùng làm mẫu, nhưng cần rubric mới rõ hơn.

---

## 1. Scope cuối cùng cho luận văn

### Core scope bắt buộc

- [x] 1.1. Chốt schema semantic news mới.
- [x] 1.2. Chọn annotation sample 100–200 bài từ dữ liệu đã crawl.
- [x] 1.3. Tạo pseudo labels bằng 2–3 AI annotators/model/config.
- [x] 1.4. Tính agreement/disagreement.
- [x] 1.5. Manual sanity check 20–30 bài.
- [x] 1.6. So sánh keyword/rule baseline với semantic pseudo labels.
- [x] 1.7. Phân tích error taxonomy: relevance, materiality, direction, event type, boilerplate, ticker mismatch.
- [x] 1.8. Làm 3–5 evidence card + outcome review case studies.

### Extended scope nếu đủ thời gian

- [x] 1.9. Aggregate semantic features theo ticker/date hoặc ticker/period.
- [x] 1.10. ML outperform classification/ranking T+20.
- [x] 1.11. Semantic signal audit với event-window return/volume/volatility.
- [x] 1.12. Top-K simulation có transaction cost.

---

## 2. Phase A — Chuẩn hóa folder và schema

### A1. Tạo cấu trúc file trong `multi_llm_evidence_extraction/`

- [x] A1.1. Tạo `README.md`.
- [x] A1.2. Tạo `de_cuong_chi_tiet_multi_llm_evidence_extraction.md`.
- [x] A1.3. Tạo `tasks.md` này.
- [x] A1.4. Tạo `schemas/semantic_news_annotation_schema.json`.
- [x] A1.5. Tạo `schemas/pseudo_label_consensus_schema.json`.
- [x] A1.6. Tạo `schemas/outcome_review_schema.json`.
- [x] A1.7. Tạo `prompts/annotation_prompt.md`.
- [x] A1.8. Tạo `prompts/consensus_prompt_or_rules.md` nếu cần.
- [x] A1.9. Tạo `prompts/evidence_card_prompt.md` nếu dùng LLM sinh card.

### A2. Schema semantic annotation

- [x] A2.1. Định nghĩa field bắt buộc:
  - `news_id`
  - `ticker`
  - `company_name`
  - `article_date`
  - `source`
  - `title`
  - `url`
  - `ticker_relevance`
  - `is_stock_relevant`
  - `event_type`
  - `event_subtype`
  - `direction`
  - `sentiment`
  - `materiality`
  - `materiality_score`
  - `expected_impact_score`
  - `uncertainty_score`
  - `novelty_score`
  - `time_horizon`
  - `evidence_span`
  - `summary`
  - `reason`
  - `reasoning_confidence`
  - `requires_human_review`
  - `data_quality_flags`
- [x] A2.2. Allowed values cho `ticker_relevance`:
  - `direct`
  - `indirect`
  - `market_wide`
  - `irrelevant`
  - `unclear`
- [x] A2.3. Allowed values cho `materiality`:
  - `high`
  - `medium`
  - `low`
  - `unclear`
- [x] A2.4. Allowed values cho `direction`:
  - `support`
  - `risk`
  - `neutral`
  - `mixed`
  - `unclear`
- [x] A2.5. Allowed values cho `event_type`:
  - `earnings`, `dividend`, `capital`, `debt`, `legal`, `governance`, `project`, `product`, `ma`, `analyst`, `market`, `macro`, `sector`, `other`, `unclear`
- [x] A2.6. Bắt buộc `evidence_span` hoặc `null`; không cho model bịa evidence.
- [x] A2.7. Thêm JSON schema validation.

Tận dụng:

- Có thể lấy logic validation từ `pipeline/experiment_llm_semantic_features.py`.
- Có thể lấy prompt style và provider call từ `scripts/annotate_hose100_extra_material.py`.

---

## 3. Phase B — Chọn mẫu annotation từ dữ liệu đã có

### B1. Xác định nguồn dữ liệu đầu vào

- [x] B1.1. Kiểm tra cột trong `data/news/processed/all_news_processed.csv`.
- [x] B1.2. Nếu cần full text tốt hơn, kiểm tra `data/news/enriched/all_news_enriched.csv`.
- [x] B1.3. Ưu tiên giữ các trường:
  - `ticker`
  - `date` hoặc `published_at`
  - `source`
  - `title`
  - `description`
  - `full_text`
  - `article_summary`
  - `key_facts_json`
  - `url`
  - `match_confidence`
  - `content_hash`

### B2. Tạo sample 100–200 bài

- [x] B2.1. Viết script `multi_llm_evidence_extraction/scripts/build_annotation_sample.py`.
- [x] B2.2. Input mặc định: `data/news/processed/all_news_processed.csv`.
- [x] B2.3. Output: `multi_llm_evidence_extraction/data/sample_news_for_annotation.csv`.
- [x] B2.4. Tạo `news_id` ổn định, ví dụ hash từ `ticker + date + url + title`.
- [x] B2.5. Stratified sample theo:
  - source;
  - ticker;
  - event keyword group nếu có;
  - match_confidence;
  - high/low news length;
  - market-wide vs direct candidates.
- [x] B2.6. Gợi ý phân bổ 150 bài:
  - earnings/business result: 25
  - dividend/capital issuance: 20
  - debt/legal/governance risk: 25
  - project/business expansion: 20
  - market-wide/sector: 25
  - generic/company announcement: 20
  - noisy/low-confidence match: 15
- [x] B2.7. Dedup theo URL/content hash/title similarity trước khi sample.
- [x] B2.8. Xuất summary `multi_llm_evidence_extraction/reports/sample_selection_summary.md`.

Tận dụng:

- Dedup logic từ `pipeline/task4_preprocess.py`.
- Source/match metadata từ `data/news/matched/all_news_matched.csv` hoặc processed file.
- Keyword groups từ `config/keywords_by_group.json` nếu cần stratification.

---

## 4. Phase C — Annotation / pseudo-labeling

### C1. Viết annotator runner

- [x] C1.1. Tạo `multi_llm_evidence_extraction/scripts/run_semantic_annotation.py`.
- [x] C1.2. Tái dùng `scripts/llm_provider.py` để gọi model.
- [x] C1.3. Hỗ trợ 2 mode:
  - offline prompt pack mode;
  - live API mode.
- [x] C1.4. Input: `data/sample_news_for_annotation.csv`.
- [x] C1.5. Output mỗi annotator:
  - `outputs/labels_annotator_a.jsonl`
  - `outputs/labels_annotator_b.jsonl`
  - `outputs/labels_annotator_c.jsonl`
- [x] C1.6. Lưu raw prompt/output:
  - `outputs/raw_responses_annotator_a.jsonl`
  - `outputs/raw_responses_annotator_b.jsonl`
  - `outputs/raw_responses_annotator_c.jsonl`
- [x] C1.7. Lưu manifest:
  - model/provider;
  - prompt version;
  - schema version;
  - run timestamp;
  - input hash;
  - output hash.
- [x] C1.8. Không đưa future return/outcome vào prompt.
- [x] C1.9. Nếu chưa có API key/model live, xuất prompt packs để chạy ngoài.

Tận dụng:

- `pipeline/experiment_llm_semantic_features.py` có:
  - prompt pack writing;
  - schema validation;
  - cache key;
  - forbidden input token guard.
- `scripts/annotate_hose100_extra_material.py` có material-event prompt gần hướng mới hơn.
- `data/experiments/llm_semantic/article_semantics_cache.csv` có cache cũ để tham khảo.

### C2. Chạy annotation

- [x] C2.1. Chạy annotator A.
- [x] C2.2. Chạy annotator B.
- [x] C2.3. Thử chạy annotator C; DeepSeek trả `402 Insufficient Balance`, nên không dùng cho consensus và không tạo nhãn giả.
- [x] C2.4. Validate JSON output.
- [x] C2.5. Không có lỗi format cần retry; lỗi annotator C là provider balance, không retry format.
- [x] C2.6. Nếu nội dung thiếu evidence span, đánh dấu `requires_human_review = true`.
- [x] C2.7. Không overwrite cache cũ; lưu version mới riêng.

Command gợi ý sau khi viết script:

```bash
python multi_llm_evidence_extraction/scripts/run_semantic_annotation.py --input multi_llm_evidence_extraction/data/sample_news_for_annotation.csv --annotator a --offline
```

---

## 5. Phase D — Consensus và agreement

### D1. Tạo consensus labels

- [x] D1.1. Tạo `multi_llm_evidence_extraction/scripts/build_consensus_labels.py`.
- [x] D1.2. Input:
  - `outputs/labels_annotator_a.jsonl`
  - `outputs/labels_annotator_b.jsonl`
  - `outputs/labels_annotator_c.jsonl`
- [x] D1.3. Output:
  - `outputs/pseudo_labels_consensus.jsonl`
  - `outputs/pseudo_labels_consensus.csv`
- [x] D1.4. Rule categorical:
  - 3 annotators: majority vote 2/3.
  - no majority: `disagreement`.
  - 2 annotators: nếu khác nhau thì `disagreement` hoặc cần annotator thứ 3/manual.
- [x] D1.5. Rule numeric:
  - median.
  - nếu range >= 2 thì flag `high_disagreement`.
- [x] D1.6. `evidence_span`:
  - giữ span từ annotator consensus nếu giống nhau;
  - nếu khác, chọn span ngắn/rõ nhất hoặc flag manual review.
- [x] D1.7. `requires_human_review = true` nếu:
  - no majority;
  - materiality high nhưng confidence thấp;
  - direction mixed/unclear;
  - relevance unclear;
  - evidence span null;
  - data quality flag có boilerplate/ticker mismatch.

### D2. Agreement report

- [x] D2.1. Tạo `multi_llm_evidence_extraction/scripts/analyze_annotation_agreement.py`.
- [x] D2.2. Output: `reports/annotation_agreement_report.md`.
- [x] D2.3. Metrics:
  - consensus rate by field;
  - pairwise agreement;
  - Cohen/Fleiss Kappa nếu phù hợp;
  - disagreement rate;
  - invalid JSON rate;
  - evidence_span missing rate.
- [x] D2.4. Bảng theo field:
  - `ticker_relevance`
  - `materiality`
  - `event_type`
  - `direction`
  - `time_horizon`
- [x] D2.5. Lưu examples:
  - 10 case agreement cao;
  - 10 case disagreement cao;
  - 10 case cần human review.

---

## 6. Phase E — Manual sanity check

### E1. Tạo file review thủ công

- [x] E1.1. Tạo `multi_llm_evidence_extraction/scripts/build_manual_review_sheet.py`.
- [x] E1.2. Chọn 20–30 bài từ:
  - high disagreement;
  - high materiality;
  - mixed/unclear direction;
  - low match confidence;
  - suspected boilerplate;
  - random control.
- [x] E1.3. Output:
  - `data/manual_sanity_check_sample.csv`
  - `reports/manual_sanity_check_template.md`

### E2. Điền và tổng hợp sanity check

- [x] E2.1. Manual review các field:
  - relevance đúng/sai;
  - materiality đúng/sai;
  - direction đúng/sai;
  - event type đúng/sai;
  - evidence span hợp lệ/không;
  - lỗi boilerplate/ticker mismatch.
- [x] E2.2. Tạo `reports/manual_sanity_check_report.md`.
- [x] E2.3. Báo cáo:
  - số bài check;
  - số bài đồng ý consensus;
  - lỗi chính;
  - ví dụ lỗi;
  - điều chỉnh prompt/schema nếu cần.

Lưu ý diễn giải:

- Không gọi manual sanity check là human ground truth đầy đủ.
- Chỉ gọi là kiểm tra chất lượng nhỏ để phát hiện lỗi hệ thống.

---

## 7. Phase F — Keyword/rule baseline vs semantic labels

### F1. Tạo rule baseline

- [x] F1.1. Tạo `multi_llm_evidence_extraction/scripts/build_rule_baseline_labels.py`.
- [x] F1.2. Tận dụng keyword hiện có:
  - `config/keywords_finance.json`
  - `config/keywords_by_group.json`
  - `docs/keyword_features_note.md`
- [x] F1.3. Rule labels cần sinh:
  - `rule_sentiment`
  - `rule_direction`
  - `rule_event_type`
  - `rule_materiality`
  - `rule_relevance`
- [x] F1.4. Output:
  - `outputs/rule_labels.jsonl`
  - `outputs/rule_labels.csv`

### F2. So sánh rule vs pseudo labels

- [x] F2.1. Tạo `multi_llm_evidence_extraction/scripts/evaluate_rule_vs_semantic.py`.
- [x] F2.2. Input:
  - `outputs/rule_labels.csv`
  - `outputs/pseudo_labels_consensus.csv`
- [x] F2.3. Output:
  - `reports/rule_vs_semantic_labels_report.md`
  - `outputs/rule_vs_semantic_confusion_matrices.csv`
- [x] F2.4. Metrics:
  - accuracy;
  - macro-F1;
  - confusion matrix;
  - coverage;
  - unclear/disagreement rate.
- [x] F2.5. Error taxonomy:
  - keyword thiếu ngữ cảnh;
  - keyword không đo materiality;
  - ticker relevance sai;
  - market-wide bị đếm như direct;
  - boilerplate/full-text noise;
  - mixed direction;
  - event type overlap.

Tận dụng:

- `docs/keyword_features_note.md` đã có danh sách keyword và điểm yếu.
- `reports/H1_experiment_report.md`, `reports/H2_H3_validation_report.md`, `reports/experiment_A6_report.md`, `reports/experiment_B1_report.md` làm evidence cho negative findings.

---

## 8. Phase G — Semantic aggregate features và outcome audit

### G1. Aggregate semantic features

- [x] G1.1. Tạo `multi_llm_evidence_extraction/scripts/build_semantic_features.py`.
- [x] G1.2. Input:
  - `outputs/pseudo_labels_consensus.csv`
  - `data/prices/all_vn30_prices.csv`
- [x] G1.3. Output:
  - `outputs/semantic_features_daily.csv`
  - `outputs/semantic_features_period.csv`
- [x] G1.4. Features:
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
- [x] G1.5. Map article date sang trading date:
  - nếu thiếu publication hour, dùng next trading day;
  - không dùng future news.

Tận dụng:

- `pipeline/experiment_llm_semantic_features.py` có `aggregate_daily_semantics()` và `_map_article_to_trading_date()`.
- Có thể copy/adapt thay vì viết từ đầu.

### G2. Event-window outcome audit

- [x] G2.1. Tạo `multi_llm_evidence_extraction/scripts/run_semantic_signal_audit.py`.
- [x] G2.2. Input:
  - consensus labels;
  - prices.
- [x] G2.3. Output:
  - `reports/semantic_signal_audit_report.md`
  - `outputs/event_window_outcomes.csv`
- [x] G2.4. Windows:
  - T+1;
  - T+5;
  - T+20;
  - T+60 nếu medium-term.
- [x] G2.5. Metrics:
  - raw return;
  - market-adjusted return vs VNINDEX;
  - abnormal volume;
  - volatility;
  - drawdown/max adverse move.
- [x] G2.6. Comparisons:
  - direct/high materiality vs low materiality;
  - support vs risk;
  - event type groups;
  - semantic labels vs keyword/news-count.

---

## 9. Phase H — ML outperform classification/ranking

### H1. Chuẩn bị target mới

- [x] H1.1. Tạo `multi_llm_evidence_extraction/scripts/build_outperform_targets.py` hoặc mở rộng script experiment hiện có.
- [x] H1.2. Target chính:

```text
excess_return_T20 = stock_return_T20 - VNINDEX_return_T20
label_outperform_T20 = 1 nếu excess_return_T20 > 0
label_outperform_T20 = 0 nếu excess_return_T20 <= 0
```

- [x] H1.3. Output:
  - `outputs/outperform_targets.csv`
- [x] H1.4. Kiểm tra anti-leakage:
  - target chỉ dùng để train/evaluate;
  - không đưa target vào annotation prompt;
  - temporal split.

Tận dụng:

- `pipeline/task6_labels.py` có logic label cũ.
- `pipeline/experiment_llm_semantic_features.py` có forward return logic nhưng đang là up/down absolute; cần nâng thành outperform vs VNINDEX.

### H2. Build ML panel

- [x] H2.1. Tạo `outputs/ml_panel_outperform.csv`.
- [x] H2.2. Feature sets:
  - A: technical-only;
  - B: technical + keyword/news-count/sentiment;
  - C: technical + semantic pseudo-label features;
  - D: technical + keyword + semantic.
- [x] H2.3. Dùng temporal split.
- [x] H2.4. Không random split.
- [x] H2.5. Không tune threshold trên test period.

Tận dụng:

- `pipeline/task10_train.py` có model train/evaluate.
- `data/features/technical_features.csv` và `data/features/keyword_features.csv` có feature sẵn.
- `pipeline/experiment_time_splits.py` có logic time split.

### H3. Train/evaluate ML

- [x] H3.1. Tạo `multi_llm_evidence_extraction/scripts/run_ml_outperform_experiment.py`.
- [x] H3.2. Models:
  - Logistic Regression;
  - Random Forest;
  - LightGBM/XGBoost nếu setup ổn.
- [x] H3.3. Metrics classification:
  - Balanced Accuracy;
  - AUC;
  - F1;
  - Precision@K;
  - confusion matrix.
- [x] H3.4. Metrics ranking/regression:
  - Spearman rank correlation;
  - Information Coefficient;
  - average excess return by score decile;
  - top quantile return.
- [x] H3.5. Output:
  - `outputs/ml_predictions_outperform.csv`
  - `reports/ml_outperform_experiment_report.md`

Diễn giải bắt buộc:

- Nếu performance vẫn 40–50%: không claim model lọc cổ phiếu tốt.
- Nếu semantic features không cải thiện: coi là negative finding hợp lệ.
- Nếu cải thiện nhẹ: claim exploratory, không claim alpha.

---

## 10. Phase I — Top-K simulation có cost — optional

### I1. Chỉ làm nếu Phase H có đủ dữ liệu

- [x] I1.1. Điều kiện chạy:
  - có predictions T+20 đủ nhiều dates;
  - có universe đủ mã mỗi rebalance date;
  - có VNINDEX benchmark hoặc proxy rõ;
  - transaction cost cố định trước.
- [x] I1.2. Nếu không đủ, ghi vào limitation và bỏ phase này.

### I2. Top-K backtest đơn giản

- [x] I2.1. Tạo `multi_llm_evidence_extraction/scripts/run_topk_simulation.py`.
- [x] I2.2. Input:
  - `outputs/ml_predictions_outperform.csv`
  - price data.
- [x] I2.3. Quy trình:
  - mỗi rebalance date;
  - rank cổ phiếu theo probability outperform hoặc expected excess return;
  - chọn Top-5 hoặc Top-10;
  - equal-weight;
  - giữ T+20 hoặc đến rebalance sau;
  - trừ `round_trip_cost = 0.50%`;
  - so sánh benchmark.
- [x] I2.4. Benchmarks:
  - VNINDEX;
  - equal-weight universe;
  - random Top-K;
  - technical-only Top-K;
  - keyword/news-count Top-K.
- [x] I2.5. Output:
  - `outputs/topk_portfolio_simulation.csv`
  - `reports/topk_backtest_with_cost_report.md`
- [x] I2.6. Metrics:
  - cumulative return;
  - excess return vs VNINDEX;
  - Sharpe;
  - max drawdown;
  - hit rate by rebalance period;
  - turnover;
  - average return per period.

Diễn giải bắt buộc:

- Đây là secondary/optional.
- Không dùng làm claim chính.
- Không viết “khuyến nghị mua/bán”.

---

## 11. Phase J — Evidence card và outcome review case studies

### J1. Chọn case studies

- [x] J1.1. Tạo `multi_llm_evidence_extraction/scripts/select_case_studies.py`.
- [x] J1.2. Chọn 3–5 case:
  - keyword tích cực nhưng semantic low materiality;
  - keyword bỏ sót event quan trọng;
  - direct/high materiality nhưng direction mixed;
  - ML đúng nhưng evidence yếu;
  - ML sai nhưng evidence card cảnh báo rủi ro.
- [x] J1.3. Output:
  - `outputs/case_study_candidates.csv`.

Tận dụng:

- `reports/decision_support/generated/evidence_packs.jsonl`
- `reports/decision_support/generated/decision_cards.md`
- `reports/decision_support/generated/outcome_reviews.md`
- `scripts/generate_decision_support_artifacts.py`

### J2. Sinh evidence cards

- [x] J2.1. Tạo/adapt `multi_llm_evidence_extraction/scripts/generate_evidence_cards.py`.
- [x] J2.2. Mỗi card gồm:
  - ticker/date;
  - ML signal context nếu có;
  - evidence summary;
  - relevance/materiality/direction;
  - evidence span;
  - data quality flags;
  - claim table;
  - warning/limitation.
- [x] J2.3. Output:
  - `outputs/evidence_cards.md`
  - `outputs/evidence_cards.jsonl`

### J3. Outcome review

- [x] J3.1. Tạo/adapt `multi_llm_evidence_extraction/scripts/run_outcome_review.py`.
- [x] J3.2. Review unit:

```text
(news_id, ticker, event_date, claim_id)
```

- [x] J3.3. Outcome labels:
  - `confirmed`
  - `contradicted`
  - `unresolved`
  - `confounded`
  - `not_price_relevant`
- [x] J3.4. Rule vận hành:
  - `confirmed support`: excess return/volume tích cực, không confounder lớn;
  - `confirmed risk`: excess return/drawdown tiêu cực, không confounder lớn;
  - `contradicted`: outcome ngược direction, không confounder;
  - `confounded`: có event khác/market shock;
  - `not_price_relevant`: tin thủ tục/low materiality.
- [x] J3.5. Output:
  - `reports/outcome_review_report.md`
  - `reports/case_studies.md`
  - `outputs/outcome_review_labels.csv`

---

## 12. Phase K — Tổng hợp kết quả vào luận văn

### K1. Tổng hợp negative findings cũ

- [x] K1.1. Tạo `reports/news_feature_negative_findings_summary.md` trong folder mới.
- [x] K1.2. Tận dụng:
  - `reports/H1_experiment_report.md`
  - `reports/H2_H3_validation_report.md`
  - `reports/experiment_A6_report.md`
  - `reports/experiment_B1_report.md`
  - `docs/keyword_features_note.md`
- [x] K1.3. Viết rõ:
  - keyword/news không cải thiện ổn định;
  - sentiment/PhoBERT/LLM sentiment cũ không đủ mạnh;
  - vấn đề nằm ở representation, không kết luận news vô dụng.

### K2. Viết report chính cho hướng mới

- [x] K2.1. Tạo canonical report `reports/ket_qua_luan_van_semantic_news_materiality.md` bằng `scripts/write_final_reports.py`.
- [x] K2.2. Sections:
  - data;
  - schema;
  - pseudo-label protocol;
  - agreement;
  - manual sanity check;
  - keyword/rule comparison;
  - semantic signal audit;
  - ML outperform experiment nếu có;
  - evidence card/outcome review;
  - limitations.
- [x] K2.3. Dùng structured artifacts làm source-of-truth; không parse generated Markdown.
- [x] K2.4. Canonical report ghi đúng snapshot hiện tại: 150 consensus rows, 122 analysis-eligible, 24 manual-review rows, 114 outcome-review labels.
- [x] K2.5. Report generation idempotent cho canonical report, negative-findings summary và advisor pitch.

### K4. Review và hardening report pipeline

- [x] K4.1. Codex review qua 9router model `cx/gpt-5.5`; lưu raw review và consolidated report trong `reports/`.
- [x] K4.2. Agreement dùng key `(news_id, ticker)`, bỏ blank labels và trả Cohen kappa unavailable cho single-class case.
- [x] K4.3. Rule comparison bắt buộc `analysis_eligible`; thiếu eligibility thì comparison unavailable.
- [x] K4.4. Manual sanity summary báo `available` / `partial` / `unavailable` và các cột thiếu.
- [x] K4.5. Event claim gate yêu cầu BH-FDR và bootstrap CI dương trên cùng test row.
- [x] K4.6. ML fold verification reject fold ID thiếu và kiểm tra business-day purge gap theo metadata.
- [x] K4.7. Top-K verification reject overlap, reversed period, sai cost/net equations và negative turnover/cost.
- [x] K4.8. Targeted verification: `tests/test_multi_llm_backtest_reports.py` — 12 passed.
- [x] K4.9. Lưu tổng hợp tại `reports/codex_review_consolidated.md`.

### K3. Update thesis draft/outline

- [x] K3.1. Update đề cương nếu kết quả thực nghiệm thay đổi scope.
- [x] K3.2. Update draft thesis hoặc tạo chương mới:
  - Chương 3: Dữ liệu và phương pháp.
  - Chương 4: Kết quả.
  - Chương 5: Thảo luận.
  - Output: `docs/luan_van_semantic_news_materiality_chuong_3_4_5.md`.
- [x] K3.3. Chuẩn bị advisor pitch 1 trang.

---

## 13. Phase L — Framing, report, robustness và lineage

Quy ước: `AUTO` là kiểm tra/sinh artifact bằng script; `HUMAN` là xác nhận nội dung học thuật không thể tự động suy ra.

### L1. Framing và hypothesis namespace

- [x] L1.1. `[AUTO]` Hạ causal claim thành association; cấm suy diễn nhân quả từ event/outcome quan sát.
- [x] L1.2. `[AUTO]` Xác định semantic representation + auditability là primary contribution.
- [x] L1.3. `[AUTO]` Đặt ML, ranking, Top-K thành secondary exploratory analyses; không claim alpha/strategy.
- [x] L1.4. `[AUTO]` Giới hạn evidence card ở technical traceability; không claim cải thiện decision quality.
- [x] L1.5. `[AUTO]` Gọi outcome review là retrospective structured review, không phải ground truth.
- [x] L1.6. `[AUTO]` Namespace RQ/hypothesis thành `RQ-SM1`–`RQ-SM6` và `H-SM1`–`H-SM6`, tách legacy `H1`–`H3`.
- [x] L1.7. `[AUTO]` Ghi rõ 3 annotation runs chỉ thuộc 2 model families.
- [ ] L1.8. `[HUMAN]` Advisor xác nhận wording đóng góp chính, secondary scope và hypothesis namespace.

### L2. Report evidence matrix và null-result language

- [x] L2.1. `[AUTO]` Thêm RQ–hypothesis–evidence matrix vào claim table và canonical report.
- [x] L2.2. `[AUTO]` Báo số và fraction event tests qua joint BH-FDR + positive-CI gate; liệt kê comparisons.
- [x] L2.3. `[AUTO]` Đọc optional placebo/family-sensitivity artifacts; thiếu file vẫn render `unavailable`.
- [x] L2.4. `[AUTO]` Báo near-random ML metrics và paired/bootstrap deltas khi artifact tồn tại.
- [x] L2.5. `[AUTO]` Báo Top-K random-null và cost sensitivity; passing accounting checks không đồng nghĩa performance.
- [x] L2.6. `[AUTO]` Ghi limitation manual sample và selected retrospective outcome reviews.
- [ ] L2.7. `[HUMAN]` Kiểm tra mọi con số/narrative trong report regenerated khớp structured artifacts.

### L3. Lineage và reproducibility

- [x] L3.1. `[AUTO]` Tạo `scripts/build_lineage_manifest.py` với path, status, bytes, mtime UTC và SHA256.
- [x] L3.2. `[AUTO]` Ghi missing optional artifacts thay vì fail report pipeline.
- [x] L3.3. `[AUTO]` README phân biệt đề cương, canonical result report, claim ledger và lineage manifest.
- [x] L3.4. `[AUTO]` Giữ public report helper contracts, pure renderers và canonical filename.
- [ ] L3.5. `[HUMAN]` Archive/freeze manifest cùng bản report dùng để nộp hoặc bảo vệ.

### L4. Verification

- [x] L4.1. `[AUTO]` Thêm focused tests cho optional fallbacks, RQ-H matrix, wording và lineage.
- [x] L4.2. `[AUTO]` Focused verification: Python compile pass; `tests/test_multi_llm_backtest_reports.py` — 15 passed; lineage + pure-render smoke pass.
- [ ] L4.3. `[HUMAN]` Đọc proof cuối: causal language, alpha language, family independence, manual/outcome limitations.

---

## 14. Thứ tự triển khai khuyến nghị

### Sprint 1 — Hoàn thành core data + schema

1. A1/A2 — schema + prompt.
2. B1/B2 — sample 100–200 bài.
3. C1 — annotator runner offline/live.

Deliverables:

- `schemas/semantic_news_annotation_schema.json`
- `prompts/annotation_prompt.md`
- `data/sample_news_for_annotation.csv`
- `reports/sample_selection_summary.md`

### Sprint 2 — Pseudo labels + agreement

1. C2 — chạy annotation.
2. D1 — consensus.
3. D2 — agreement report.
4. E1/E2 — manual sanity check.

Deliverables:

- `outputs/labels_annotator_*.jsonl`
- `outputs/pseudo_labels_consensus.csv`
- `reports/annotation_agreement_report.md`
- `reports/manual_sanity_check_report.md`

### Sprint 3 — Keyword/rule comparison

1. F1 — rule baseline.
2. F2 — evaluate rule vs semantic.
3. K1 — negative findings summary.

Deliverables:

- `outputs/rule_labels.csv`
- `reports/rule_vs_semantic_labels_report.md`
- `reports/news_feature_negative_findings_summary.md`

### Sprint 4 — Outcome/evidence core

1. G2 — semantic signal audit.
2. J1/J2/J3 — case studies + evidence card + outcome review.

Deliverables:

- `reports/semantic_signal_audit_report.md`
- `outputs/evidence_cards.md`
- `reports/outcome_review_report.md`
- `reports/case_studies.md`

### Sprint 5 — ML extended

1. G1 — aggregate semantic features.
2. H1/H2/H3 — outperform ML.
3. I1/I2 — Top-K optional nếu đủ.

Deliverables:

- `outputs/semantic_features_daily.csv`
- `outputs/ml_panel_outperform.csv`
- `reports/ml_outperform_experiment_report.md`
- `reports/topk_backtest_with_cost_report.md` nếu chạy.

---

## 15. Definition of Done

### Bản tối thiểu đủ trao đổi/bảo vệ hướng

- [x] Schema semantic rõ và có rubric.
- [x] 100–200 bài annotation sample.
- [x] 2–3 annotator outputs hoặc ít nhất 2 annotators + manual sanity check.
- [x] Consensus labels.
- [x] Agreement report.
- [x] Manual sanity check 20–30 bài.
- [x] Keyword/rule baseline comparison.
- [x] Error taxonomy.
- [x] 3–5 evidence card/outcome review case studies.
- [x] Report tổng hợp kết quả.

### Bản mạnh hơn

- [x] Semantic signal audit T+1/T+5/T+20.
- [x] ML outperform classification/ranking T+20.
- [x] Top-K simulation có transaction cost.
- [x] Kết nối kết quả với thesis draft.

---

## 16. Nguyên tắc diễn giải khi viết luận văn

- Không claim LLM labels là ground truth.
- Không claim semantic features chắc chắn tạo alpha.
- Không gọi evidence card là khuyến nghị mua/bán.
- Không dùng random split cho dữ liệu thời gian.
- Không đưa future return/outcome vào prompt.
- Không overfit threshold/model trên test period.
- Nếu kết quả ML yếu, vẫn dùng làm negative finding và giải thích giới hạn của news-as-feature.
- Giá trị chính của luận văn: schema semantic + materiality/relevance + controlled pseudo-labeling + evidence/outcome audit cho tin chứng khoán Việt Nam.
