# Annotation agreement report

## Annotator provenance

| annotator | api_provider | requested_model | response_model | model_vendor | route_mode | provenance_status | run_id |
| --- | --- | --- | --- | --- | --- | --- | --- |
| a | deepseek | deepseek-chat | deepseek-v4-flash | deepseek | native | legacy_reconstructed | legacy-reconstructed-a |
| b | deepseek | deepseek-chat | deepseek-v4-flash | deepseek | native | legacy_reconstructed | legacy-reconstructed-b |
| c | anthropic | cx/gpt-5.4-mini | gpt-5.4-mini | openai | gateway_or_proxy | legacy_reconstructed | legacy-reconstructed-c |

## Annotator valid-label counts

| index | value |
| --- | --- |
| a | 150 |
| b | 150 |
| c | 150 |

## Invalid/error counts

| index | value |
| --- | --- |
| a | 0 |
| b | 0 |
| c | 0 |

## Pairwise agreement

| field | pair | agree | total | agreement | cohen_kappa |
| --- | --- | --- | --- | --- | --- |
| ticker_relevance | a-b | 148 | 150 | 0.9867 | 0.9408 |
| ticker_relevance | a-c | 135 | 150 | 0.9 | 0.6325 |
| ticker_relevance | b-c | 133 | 150 | 0.8867 | 0.5917 |
| materiality | a-b | 142 | 150 | 0.9467 | 0.9183 |
| materiality | a-c | 109 | 150 | 0.7267 | 0.5772 |
| materiality | b-c | 108 | 150 | 0.72 | 0.5669 |
| direction | a-b | 145 | 150 | 0.9667 | 0.9518 |
| direction | a-c | 117 | 150 | 0.78 | 0.6811 |
| direction | b-c | 114 | 150 | 0.76 | 0.6532 |
| event_type | a-b | 146 | 150 | 0.9733 | 0.9695 |
| event_type | a-c | 127 | 150 | 0.8467 | 0.8252 |
| event_type | b-c | 126 | 150 | 0.84 | 0.8176 |
| time_horizon | a-b | 139 | 150 | 0.9267 | 0.8868 |
| time_horizon | a-c | 103 | 150 | 0.6867 | 0.5332 |
| time_horizon | b-c | 98 | 150 | 0.6533 | 0.4845 |

## Consensus summary

- Consensus rows: 150
- majority_vote: 106
- unanimous: 40
- disagreement: 4
- Analysis eligible: 122/150
- Evidence span missing rate: 8.67%

## Example rows

| artifact_schema_version | news_id | ticker | article_date | annotator_count | consensus_ticker_relevance | consensus_materiality | consensus_direction | consensus_event_type | consensus_time_horizon | consensus_is_stock_relevant | consensus_materiality_score | consensus_expected_impact_score | consensus_uncertainty_score | consensus_novelty_score | consensus_reasoning_confidence | evidence_span | disagreement_fields | high_disagreement_fields | unanimous_fields | majority_fields | consensus_method | agreement_level | analysis_eligible | exclusion_reasons | quality_flags | requires_human_review | review_flags | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pseudo_label_consensus_v2 | 031ef1d479fa02d5 | HDG | 2025-06-26 | 3 | direct | low | neutral | governance | unclear | True | 1 | 1 | 1 | 1 | 5 | HDG: Thông báo ký kết hợp đồng kiểm toán BCTC 2025 | [] | ['materiality_score', 'novelty_score', 'reasoning_confidence', 'uncertainty_score'] | ['direction', 'event_type', 'is_stock_relevant', 'materiality', 'ticker_relevance', 'time_horizon'] | [] | unanimous | high | True | [] | ['numeric_score_outlier'] | True | ['numeric_score_outlier'] | Deterministic pseudo-label consensus; eligibility excludes unresolved, irrelevant, missing-evidence, and provenance-conflict rows. |
| pseudo_label_consensus_v2 | 0332db9674ce5215 | MSB | 2025-02-03 | 3 | direct | low | neutral | other | short_term | True | 1 | 1 | 1 | 1 | 5 | MSB: CBTT hoàn thành nghĩa vụ thuế Ngân hàng Thương mại Cổ phần Hàng Hải Việt Nam thông báo hoàn thành nghĩa vụ thuế | [] | ['materiality_score', 'novelty_score', 'reasoning_confidence', 'uncertainty_score'] | ['direction', 'event_type', 'is_stock_relevant', 'materiality', 'ticker_relevance', 'time_horizon'] | [] | unanimous | high | True | [] | ['numeric_score_outlier'] | True | ['numeric_score_outlier'] | Deterministic pseudo-label consensus; eligibility excludes unresolved, irrelevant, missing-evidence, and provenance-conflict rows. |
| pseudo_label_consensus_v2 | 0524672d9cbb31a1 | MBB | 2025-11-14 | 3 | direct | high | risk | debt | short_term | True | 4 | 4 | 2 | 3 | 4 | Thông báo về việc tạm ngừng giao dịch đối với trái phiếu MBB12348 của NGÂN HÀNG TMCP QUÂN ĐỘI | [] | ['expected_impact_score'] | ['event_type', 'is_stock_relevant', 'ticker_relevance'] | ['direction', 'materiality', 'time_horizon'] | majority_vote | medium | True | [] | ['numeric_score_outlier'] | True | ['numeric_score_outlier'] | Deterministic pseudo-label consensus; eligibility excludes unresolved, irrelevant, missing-evidence, and provenance-conflict rows. |
| pseudo_label_consensus_v2 | 08dbe74f075e78c1 | VNM | 2025-10-06 | 3 | direct | medium | support | earnings | medium_term | True | 3 | 3 | 2 | 2 | 4 | Lũy kế 6 tháng đầu năm 2025, Vinamilk đạt tổng doanh thu hợp nhất là 29.710 tỷ đồng, hoàn thành 46,1% kế hoạch năm; với doanh thu thuần trong nước và nước ngoài đạt lần lượt 23.624 tỷ đồng và 6.035 tỷ đồng. | [] | [] | ['direction', 'event_type', 'is_stock_relevant', 'materiality', 'ticker_relevance', 'time_horizon'] | [] | unanimous | high | True | [] | ['none'] | False | ['none'] | Deterministic pseudo-label consensus; eligibility excludes unresolved, irrelevant, missing-evidence, and provenance-conflict rows. |
| pseudo_label_consensus_v2 | 09d75de8414ae409 | UNKNOWN | 2025-07-14 | 3 | irrelevant | low | neutral | market | short_term | False | 1 | 1 | 3 | 3 | 5 | bitcoin đã vượt mốc 120.000 USD lần đầu tiên trong lịch sử | [] | ['expected_impact_score', 'materiality_score', 'reasoning_confidence'] | ['event_type', 'time_horizon'] | ['direction', 'is_stock_relevant', 'materiality', 'ticker_relevance'] | majority_vote | medium | False | ['not_directly_stock_relevant', 'relevance_unclear_or_irrelevant'] | ['numeric_score_outlier', 'unclear_relevance'] | True | ['numeric_score_outlier', 'unclear_relevance'] | Deterministic pseudo-label consensus; eligibility excludes unresolved, irrelevant, missing-evidence, and provenance-conflict rows. |
| pseudo_label_consensus_v2 | 0d0a280f83b376c3 | VIC | 2023-02-17 | 3 | direct | low | neutral | capital | unclear | True | 1 | 1 | 4 | 1 | 3 | VIC: Nhận chuyển nhượng cổ phần tại pháp nhânCTCP Đầu tư và Phát triển Làng Vân | [] | ['materiality_score', 'novelty_score'] | ['direction', 'is_stock_relevant', 'materiality', 'ticker_relevance'] | ['event_type', 'time_horizon'] | majority_vote | medium | True | [] | ['numeric_score_outlier'] | True | ['numeric_score_outlier'] | Deterministic pseudo-label consensus; eligibility excludes unresolved, irrelevant, missing-evidence, and provenance-conflict rows. |
| pseudo_label_consensus_v2 | 0d54ea881ed2c26e | VND | 2023-09-19 | 3 | direct | low | risk | capital | short_term | True | 2 | 2 | 2 | 3 | 4 | nan | [] | [] | ['direction', 'event_type', 'is_stock_relevant', 'ticker_relevance', 'time_horizon'] | ['materiality'] | majority_vote | medium | False | ['evidence_unavailable'] | ['missing_or_disputed_evidence'] | True | ['missing_or_disputed_evidence'] | Deterministic pseudo-label consensus; eligibility excludes unresolved, irrelevant, missing-evidence, and provenance-conflict rows. |
| pseudo_label_consensus_v2 | 0d633b4bd75f7972 | VSC | 2024-10-04 | 3 | direct | low | neutral | other | disagreement | True | 2 | 1 | 2 | 2 | 4 | Công ty CP Chứng khoán Bảo Việt (BVSC) vừa phát đi thông báo về việc chuẩn hóa dữ liệu nhà đầu tư trước ngày 01/01/2025. | ['time_horizon'] | ['materiality_score', 'novelty_score', 'reasoning_confidence', 'uncertainty_score'] | ['direction', 'materiality'] | ['event_type', 'is_stock_relevant', 'ticker_relevance'] | disagreement | low | False | ['categorical_consensus_unavailable'] | ['categorical_disagreement', 'numeric_score_outlier'] | True | ['categorical_disagreement', 'numeric_score_outlier'] | Deterministic pseudo-label consensus; eligibility excludes unresolved, irrelevant, missing-evidence, and provenance-conflict rows. |
| pseudo_label_consensus_v2 | 0dc6d1da109b4aaf | UNKNOWN | 2026-06-23 | 3 | market_wide | medium | neutral | market | long_term | True | 3 | 3 | 3 | 3 | 4 | Việt Nam vẫn ở nhóm thị trường cận biên (Frontier Market) | [] | [] | ['event_type', 'is_stock_relevant', 'materiality', 'ticker_relevance'] | ['direction', 'time_horizon'] | majority_vote | medium | True | [] | ['none'] | False | ['none'] | Deterministic pseudo-label consensus; eligibility excludes unresolved, irrelevant, missing-evidence, and provenance-conflict rows. |
| pseudo_label_consensus_v2 | 0f37c4ecb1cd0f71 | TPB | 2026-06-11 | 3 | direct | medium | support | other | medium_term | True | 3 | 3 | 3 | 3 | 4 | Ở TPBank, trong hai năm qua, chúng tôi đã tăng năng suất lao động tới 64%, tức là tạo ra được lợi nhuận trên mỗi đầu nhân viên. | [] | [] | ['direction', 'event_type', 'is_stock_relevant', 'materiality', 'ticker_relevance'] | ['time_horizon'] | majority_vote | medium | True | [] | ['data_quality_issue'] | True | ['data_quality_issue'] | Deterministic pseudo-label consensus; eligibility excludes unresolved, irrelevant, missing-evidence, and provenance-conflict rows. |

