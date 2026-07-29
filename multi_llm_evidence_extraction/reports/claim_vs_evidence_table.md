# Claim vs evidence table

| Claim luận văn | Evidence artifact | Corrected result | Claim level |
| --- | --- | --- | --- |
| Keyword/news-count thiếu ngữ cảnh | reports/rule_vs_semantic_labels_report.md | Rule baseline versus semantic pseudo-labels; not human ground truth | Supported exploratory |
| Annotation provenance | outputs/annotation_manifest_*.json | manifest runs=3; provider, routed model vendor, and hashes below | Descriptive limitation |
| Consensus categorical labels | outputs/pseudo_labels_consensus.csv | rows=150; disagreement=4, majority_vote=106, unanimous=40; eligible=122/150 | Descriptive |
| Semantic event-window association | outputs/event_window_stat_tests.csv | joint positive gate=1/8; FDR rows=1; positive-CI rows=2; flag mismatches=0 | Supported exploratory association |
| Point-in-time ML ranking | outputs/ml_predictions_outperform.csv | rows=685704; folds=3; purge=[20]; status=verified_from_fold_metadata; near-random metrics and paired deltas reported when available | Exploratory |
| Top-K simulation | outputs/topk_portfolio_simulation.csv | rows=2592; periods=54; non-overlap=True; turnover-cost=True; net equations=True; random-null and cost sensitivity are required for performance interpretation | Null/weak exploratory result |
| Evidence cards and outcome review | outputs/evidence_cards.*, outputs/outcome_review_labels.csv | outcome-review rows=114; retrospective structured review only | Technical traceability; not decision quality or ground truth |

## RQ–hypothesis–evidence matrix

| Research question | Hypothesis | Focus | Evidence | Allowed interpretation |
| --- | --- | --- | --- | --- |
| RQ-SM1 | H-SM1 | Representation limits | rule comparison + error taxonomy | Associational/descriptive |
| RQ-SM2 | H-SM2 | Semantic schema and pseudo-label stability | consensus + agreement + manual sanity | Descriptive; 3 runs, 2 model families |
| RQ-SM3 | H-SM3 | Outcome association | event tests + placebo | Exploratory association, not causal |
| RQ-SM4 | H-SM4 | ML/ranking increment | purged OOS metrics + paired/bootstrap deltas | Secondary exploratory |
| RQ-SM5 | H-SM5 | Top-K filtering | random null + cost sensitivity | Secondary exploratory; no alpha claim |
| RQ-SM6 | H-SM6 | Evidence traceability | cards + lineage + outcome review | Technical traceability only |

## Corrected event claim gate

Rule: `p_value_bh <= 0.05 AND diff_ci_low > 0 under Benjamini-Hochberg correction`. Available=True; pass=True; joint-positive fraction=1/8.

## Annotator provenance

| annotator | API provider | requested | response | vendor | route | status | schema | label hash match | input SHA256 | schema SHA256 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a | deepseek | deepseek-chat | deepseek-v4-flash | deepseek | native | legacy_reconstructed | semantic_news_annotation_v1 | True | a03ec8cbbb4cbbc8a0d9e3427c29771bb8c38698ec494ef83451b3f38a652c73 | cbb930cb4f3ed7b02f113aa4a76da9634ba17a84359d2dc1c4b7ca6a42ad60ba |
| b | deepseek | deepseek-chat | deepseek-v4-flash | deepseek | native | legacy_reconstructed | semantic_news_annotation_v1 | True | a03ec8cbbb4cbbc8a0d9e3427c29771bb8c38698ec494ef83451b3f38a652c73 | cbb930cb4f3ed7b02f113aa4a76da9634ba17a84359d2dc1c4b7ca6a42ad60ba |
| c | anthropic | cx/gpt-5.4-mini | gpt-5.4-mini | openai | gateway_or_proxy | legacy_reconstructed | semantic_news_annotation_v1 | True | a03ec8cbbb4cbbc8a0d9e3427c29771bb8c38698ec494ef83451b3f38a652c73 | cbb930cb4f3ed7b02f113aa4a76da9634ba17a84359d2dc1c4b7ca6a42ad60ba |

## Artifact integrity and freshness

| artifact | schema version | SHA256 | modified UTC | latest upstream UTC | freshness |
| --- | --- | --- | --- | --- | --- |
| consensus | pseudo_label_consensus_v2 | 658e6b8b827f7bc5b76f6cf72f5c100abd77dba0be95be563bec94d1b31715ba | 2026-07-10T09:43:10+00:00 | 2026-07-10T08:39:31+00:00 | fresh |
| event_tests | event_window_tests_v3 | 0ef12ace27fec1c809b24a2b93f077258c51840f5bab656e23752d7975721c7f | 2026-07-10T14:23:42+00:00 | 2026-07-10T14:20:01+00:00 | fresh |
| ml_predictions | outperform_ml_predictions_v2 | 8ac3ddf5fcb328e9713b2311321e8d810a97f0c03f06d90923b90257aff03da9 | 2026-07-12T00:56:48+00:00 | 2026-07-12T00:54:15+00:00 | fresh |
| topk | topk_nonoverlap_v2 | f9c9becda04e72dff11f89ae7da777e0842ba21ea1c45a34a27d3ffd93d6f280 | 2026-07-12T01:02:23+00:00 | 2026-07-12T00:56:48+00:00 | fresh |
| placebo | placebo_pre_event_tests_v1 | ca33bd20fedd3b18ca19f2e6bd4648c1b787dd725f6f3912f83fe36514e8a709 | 2026-07-12T00:53:47+00:00 | unavailable | no_upstream_reference |
| ml_paired | outperform_ml_paired_daily_v1 | ac180fa8c86a559d76a80397490a0e7b24b3bdb1f2d2ba72019936b214d02a40 | 2026-07-12T01:01:30+00:00 | unavailable | no_upstream_reference |
| ml_bootstrap | outperform_ml_bootstrap_delta_v1 | 3bcab88907c668030354035080a6f31138d950f85db3b3d8b296a63c4681bc81 | 2026-07-12T01:01:30+00:00 | unavailable | no_upstream_reference |
| topk_null | topk_random_null_summary_v1 | 47fe353387e3bb42de63afc6e97d88c1967ee0a4c322be04c0e554730bd01af7 | 2026-07-12T01:11:18+00:00 | unavailable | no_upstream_reference |
| topk_cost | topk_cost_sensitivity_v1 | f11bba86218faf4e93fcdab805b6bfa25813b993f221751607e60cf228541d2d | 2026-07-12T01:11:18+00:00 | unavailable | no_upstream_reference |
| family_sensitivity | consensus_family_sensitivity_summary_v1 | afa707757773638b68c6ac32b843d997e8b5a5c69a0aaa87f3966df77f6bbe7d | 2026-07-12T00:53:40+00:00 | unavailable | no_upstream_reference |

## Purged OOS fold metadata

| fold | train start | train end | test start | test end | purge trading days |
| --- | --- | --- | --- | --- | --- |
| 1 | 2021-10-14 | 2022-01-06 | 2022-02-11 | 2023-07-14 | 20 |
| 2 | 2021-10-14 | 2023-06-16 | 2023-07-17 | 2024-12-16 | 20 |
| 3 | 2021-10-14 | 2024-11-18 | 2024-12-17 | 2026-06-01 | 20 |

## Optional robustness readers

Available={'placebo': True, 'ml_paired': True, 'ml_bootstrap': True, 'topk_null': True, 'topk_cost': True, 'family_sensitivity': True}; placebo robust-positive=0/4; ML metrics/deltas={'auc': {'rows': 10720, 'baseline_mean': 0.4987859851841035, 'comparison_mean': 0.5077274414618087, 'delta_mean': 0.008941456277705222}, 'balanced_accuracy': {'rows': 10720, 'baseline_mean': 0.4962194204808665, 'comparison_mean': 0.5017280469501291, 'delta_mean': 0.005508626469262693}, 'daily_rank_ic': {'rows': 10720, 'baseline_mean': -0.00208379320853634, 'comparison_mean': 0.013083896667428457, 'delta_mean': 0.015167689875964797}, 'f1': {'rows': 10720, 'baseline_mean': 0.43072887299074886, 'comparison_mean': 0.4534448712644368, 'delta_mean': 0.02271599827368796}, 'precision_at_10_by_date': {'rows': 10720, 'baseline_mean': 0.4662220149253731, 'comparison_mean': 0.47141791044776116, 'delta_mean': 0.005195895522388059}}; ML bootstrap rows=50; Top-K null significant=3/16; cost rows=64 at rates=[0.0, 0.0025, 0.005, 0.01]; family-sensitivity rows=5.

Missing optional files remain unavailable and do not block core report generation.

## Safe interpretation

Consensus labels are pseudo-labels, not ground truth. Three annotation runs represent only two model families, not three independent systems. Manual review is a small quality-control sample. Outcome review is retrospective structured review, not semantic ground truth or decision-quality validation. Event-study reports associations, not causal effects. ML and Top-K results remain exploratory; near-random metrics, null comparisons, and transaction costs preclude alpha or investment claims.
