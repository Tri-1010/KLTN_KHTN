# Claim–Evidence–Limitation Matrix

| Claim | Evidence source | Gate | Allowed interpretation | Limitation |
|---|---|---|---|---|
| Keyword và semantic được so sánh công bằng | `canonical_results/manifests/harmonized_article_spine.csv`, `canonical_results/manifests/harmonized_row_manifest.csv`, `canonical_results/manifests/harmonized_fold_manifest.csv`, prediction alignment checks | Exact keys, targets, folds và candidate universe bằng nhau | So sánh paired OOS trong canonical sample | Chỉ common stratified article spine |
| Semantic tốt hơn keyword ở primary setting | `canonical_results/tables/harmonized_inference.csv`, `canonical_results/canonical_summary.json` | Đúng P1 / B→C / RandomForest / balanced_accuracy; 3 folds; audits pass; BH ≤ 0,05; CI low > 0 | Conditional improvement trong contract khai báo | Không suy rộng full corpus hoặc mọi model/horizon; không có timestamp preregistration độc lập |
| Keyword không tăng giá trị ổn định | H1 reports và canonical B so với E | Kết quả phải gắn đúng protocol | Negative empirical finding trong setting đã kiểm tra | Không chứng minh tin tức vô ích |
| Semantic schema giàu hơn rule/keyword | Consensus, rule-vs-semantic report, evidence-span audit | Ghi rõ pseudo-label | Representation/error-taxonomy evidence | Không phải human ground truth |
| Materiality liên hệ adjusted return T+5 | Event test artifact | BH ≤ 0,05 và positive CI | Exploratory association | Không causal; nhiều confounders |
| Full-evidence card tốt hơn ML-only trong rubric | Same-run card scores | Chỉ so trong cùng judge condition | Card quality/faithfulness evidence | Automated judge, không đo return/human quality |
| EvidenceTrace duy trì truy vết | Bundle/schema/hash/tests/case audit | Initial/monitor/review separation pass | Prototype traceability | Chưa production deployment |
| Top-K keyword và semantic khác nhau | `canonical_results/backtest/harmonized_topk_matched_deltas.csv`, `canonical_results/tables/harmonized_inference.csv` | Cùng dates/universe/K/cost; đủ periods và đủ 3 folds | Exploratory economic simulation | Không alpha; liquidity/impact chưa đầy đủ |

## Non-claims

- Không tuyên bố LLM luôn cải thiện dự báo.
- Không tuyên bố semantic tạo alpha ổn định.
- Không gọi pseudo-label là nhãn chuẩn con người.
- Không diễn giải event association thành tác động nhân quả.
- Không gọi automated rubric là human evaluation.
- Không đưa khuyến nghị đầu tư hoặc cam kết lợi nhuận.
