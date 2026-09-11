# Claim–Evidence–Limitation Matrix

## Protocol layers

- **V6 prospective primary:** `multi_llm_evidence_extraction/outputs/v6_primary/<run_id>/` and matching report directory. H1 is B→A and H2 is C→A on the full target/technical-eligible price panel, including no-news rows. BH is applied jointly to H1/H2; C→B is supplemental.
- **Frozen canonical:** `canonical_results/` and `multi_llm_evidence_extraction/outputs/harmonized/canonical_150_v7/`. This is the historical same-spine B→C contract and must not be overwritten or presented as V6 H1/H2.
- **Legacy quarterly:** `pipeline/`. Its `label_basic`, news-filtered sample and Config A/B/C definitions are exploratory and cannot support V6 claims.

| Claim | Evidence source | Gate | Allowed interpretation | Limitation |
|---|---|---|---|---|
| V6 từ khóa tạo khác biệt so với kỹ thuật (H1) | `multi_llm_evidence_extraction/outputs/v6_primary/<run_id>/v6_primary_inference.csv`, `v6_primary_summary.json`, row/fold/prediction alignment manifests | Đúng H1 / B→A / RandomForest / balanced_accuracy; đủ 3 folds; same-row and purge audits pass; H1/H2 BH reported | Paired OOS difference within the completed V6 full-price-panel run | Không mặc định là cải thiện; không alpha hoặc causal claim |
| V6 ngữ nghĩa tạo khác biệt so với kỹ thuật (H2) | `multi_llm_evidence_extraction/outputs/v6_primary/<run_id>/v6_primary_inference.csv`, `v6_primary_summary.json`, row/fold/prediction alignment manifests | Đúng H2 / C→A / RandomForest / balanced_accuracy; đủ 3 folds; same-row and purge audits pass; H1/H2 BH reported | Paired OOS difference within the completed V6 full-price-panel run | Semantic coverage sparse; pseudo-label không phải human gold |
| Keyword và semantic được so sánh công bằng trong frozen canonical | `canonical_results/manifests/harmonized_article_spine.csv`, `canonical_results/manifests/harmonized_row_manifest.csv`, `canonical_results/manifests/harmonized_fold_manifest.csv`, prediction alignment checks | Exact keys, targets, folds và candidate universe bằng nhau | So sánh paired OOS trong canonical sample | Chỉ common stratified article spine; không phải V6 H1/H2 |
| Semantic tốt hơn keyword ở frozen canonical primary setting | `canonical_results/tables/harmonized_inference.csv`, `canonical_results/canonical_summary.json` | Đúng P1 / B→C / RandomForest / balanced_accuracy; 3 folds; audits pass; BH ≤ 0,05; CI low > 0 | Conditional improvement trong contract khai báo | Gate thực tế không đạt; không suy rộng full corpus hoặc mọi model/horizon; không có timestamp preregistration độc lập |
| Keyword không tăng giá trị ổn định | Kết quả H1 phải trỏ đúng V6 run; bằng chứng canonical/legacy phải ghi đúng layer | Kết quả phải gắn đúng protocol | Negative empirical finding trong setting đã kiểm tra | Không chứng minh tin tức vô ích |
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
