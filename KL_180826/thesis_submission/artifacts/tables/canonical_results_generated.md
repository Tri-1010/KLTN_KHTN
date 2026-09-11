# Canonical results generated from structured artifacts

- Run: `canonical_150_v7`
- Protocol SHA256: `ae4fd6ec0cf095b4608d09ecfbdeb5c1663b742c80a1bbd1cac02567c259f3ae`
- Claim level: `common_stratified_article_spine_only`

## Primary comparison

| Run | Baseline | Comparison | Model | Metric | Delta | CI low | CI high | p BH | Folds | Gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| canonical_150_v7 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | balanced_accuracy | -0.0066099144757681355 | -0.05436679292929294 | 0.0242987991852321 | 0.8698963436989634 | 3 | False |

## Attrition

| sampled_articles | joined_articles | eligible_articles | mapped_eligible_articles | analytic_spine_articles | panel_target_available_rows | panel_eligible_rows |
| --- | --- | --- | --- | --- | --- | --- |
| 150 | 150 | 122 | 114 | 114 | 92080 | 5656 |

## Top-K status

| family | model | k | periods | folds | status | drop_reason |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | LogisticRegression | 5 | 22 | 3 | ok |  |
| T1 | LogisticRegression | 10 | 9 | 1 | not_estimable_in_pilot | universe_below_k |
| T1 | RandomForest | 5 | 22 | 3 | ok |  |
| T1 | RandomForest | 10 | 9 | 1 | not_estimable_in_pilot | universe_below_k |
