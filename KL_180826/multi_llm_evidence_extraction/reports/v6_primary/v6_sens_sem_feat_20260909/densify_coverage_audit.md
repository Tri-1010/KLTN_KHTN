# Densified-cache semantic coverage audit

Claim level: `v6_sensitivity_densified_cache_semantic`  
Run id: `v6_sens_sem_feat_20260909`

## Inputs

- `data/experiments/llm_semantic/article_semantics_cache.csv`
- `data/experiments/llm_semantic/focused_material_expanded_annotations_deepseek.csv`
- Adapted labels: `outputs/cache_dense_pseudo_labels.csv` (8,989 rows / 80 tickers after OK+relevant filter and content_hash dedupe)
- Dense daily: `outputs/semantic_features_daily_cache_dense.csv`

## Coverage lift vs locked consensus daily

| Metric | Consensus locked daily | Densified cache daily |
| --- | --- | --- |
| Grid rows | 93,824 | 93,824 |
| Nonzero `semantic_news_count` day-rate | ~0.12% | ~8.08% |
| Nonzero `semantic_news_count_roll_60d` day-rate | ~6% | ~86.6% |
| Panel `n_no_news_semantic` (eligible build) | high (sparse present) | 0 |

Direction mix after score-threshold adapter (`sentiment_score` ±0.25; categorical sentiment is all `neutral` in cache): support 4059, neutral 2629, mixed 1361, risk 940.

## Integrity

- Locked `semantic_features_daily.csv` sha256 unchanged: `3755fbbef05c608db80c65d2f525215169a0bdd535d3ee634aacf23ee41b25f0`
- Locked primary `v6_primary_20260909` untouched
- This lane is exploratory sensitivity only; single-model cache ≠ multi-LLM consensus; not a V6 primary gate

## Sensitivity H1/H2 readout (RF balanced_accuracy)

| Hypothesis | Locked primary Δ | Densified-cache Δ | Densified p_BH | Densified 95% CI |
| --- | ---: | ---: | ---: | --- |
| H1 (B−A) | −0.0102 | −0.0102 | 0.172 | [−0.0213, +0.0003] |
| H2 (C−A) | −0.0042 | −0.0076 | 0.172 | [−0.0171, +0.0035] |

H1 unchanged is expected (keyword path untouched). Densified H2 remains negative and does not reverse the locked primary null/negative conclusion. Coverage lift alone was not sufficient for Tech+Sem to beat Tech on the V6 primary metric.

## Limitations

- Adapter approximates consensus materiality/direction schema
- Densification may concentrate on liquid names already present in the cache
- Even a positive densified H2 would **not** replace the locked null/negative primary H2; here H2 stayed negative
