# Semantic news materiality study report

## Data and current artifact counts

| artifact | rows |
| --- | --- |
| annotation_sample | 150 |
| consensus_labels | 150 |
| rule_labels | 150 |
| semantic_daily | 93824 |
| event_windows | 456 |
| event_tests | 8 |
| ml_predictions | 685704 |
| topk_rows | 2592 |
| case_candidates | 5 |
| outcome_reviews | 114 |

## RQ–hypothesis–evidence matrix

| Research question | Hypothesis | Evidence focus | Allowed interpretation |
| --- | --- | --- | --- |
| RQ-SM1 | H-SM1 | Rule/keyword representation limits | Descriptive/associational |
| RQ-SM2 | H-SM2 | Schema, agreement, manual sanity | Descriptive; pseudo-labels |
| RQ-SM3 | H-SM3 | Event-window association and placebo | Exploratory; not causal |
| RQ-SM4 | H-SM4 | Purged OOS ML metrics and deltas | Secondary exploratory |
| RQ-SM5 | H-SM5 | Top-K null and cost sensitivity | Secondary; no alpha |
| RQ-SM6 | H-SM6 | Evidence/lineage traceability | Technical traceability only |

## Semantic annotation schema

Semantic annotation schema separates ticker relevance, materiality, direction, event type, uncertainty, novelty, and exact evidence span. This representation and its auditable evaluation are primary contribution; ML, ranking, and Top-K are secondary exploratory analyses.

## Pseudo-label protocol and consensus

Consensus rows=150; analysis-eligible=122; ineligible=28; schema=pseudo_label_consensus_v2.

| consensus method | rows |
| --- | --- |
| disagreement | 4 |
| majority_vote | 106 |
| unanimous | 40 |

Offline prompt packs are pending annotations, not synthetic labels. Future/outcome fields are blocked from annotation prompts. Consensus labels remain pseudo-labels, not ground truth.

## Annotator provenance

| annotator | API provider | requested model | response model | vendor | route | status | prompt version | schema version | label hash match | manifest SHA256 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a | deepseek | deepseek-chat | deepseek-v4-flash | deepseek | native | legacy_reconstructed | semantic_news_materiality_v1 | semantic_news_annotation_v1 | True | ef73ed36d5d7ec540247617ba4138abb0b2a1451ba5eedb8c0acf263694fb9e6 |
| b | deepseek | deepseek-chat | deepseek-v4-flash | deepseek | native | legacy_reconstructed | semantic_news_materiality_v1 | semantic_news_annotation_v1 | True | e9ffc93410bf5a3f17f70e7e7d10bb7a5e3dc9ebd63ac6d915e97329666231e5 |
| c | anthropic | cx/gpt-5.4-mini | gpt-5.4-mini | openai | gateway_or_proxy | legacy_reconstructed | semantic_news_materiality_v1 | semantic_news_annotation_v1 | True | b1958ee94d822811e7da2bed95143598dfd34830a18325fc0786c30799589456 |

Provider and model vendor are separate fields. A routed response keeps its actual vendor and is not relabeled as a native provider model.

## Annotation agreement

Available=True; valid labels={'a': 150, 'b': 150, 'c': 150}; error rows={'a': 0, 'b': 0, 'c': 0}; mean pairwise agreement=0.8400.

| field | pair | agree | total | agreement | Cohen kappa |
| --- | --- | --- | --- | --- | --- |
| ticker_relevance | a-b | 148 | 150 | 0.9867 | 0.9408 |
| materiality | a-b | 142 | 150 | 0.9467 | 0.9183 |
| direction | a-b | 145 | 150 | 0.9667 | 0.9518 |
| event_type | a-b | 146 | 150 | 0.9733 | 0.9695 |
| time_horizon | a-b | 139 | 150 | 0.9267 | 0.8868 |
| ticker_relevance | a-c | 135 | 150 | 0.9000 | 0.6325 |
| materiality | a-c | 109 | 150 | 0.7267 | 0.5772 |
| direction | a-c | 117 | 150 | 0.7800 | 0.6811 |
| event_type | a-c | 127 | 150 | 0.8467 | 0.8252 |
| time_horizon | a-c | 103 | 150 | 0.6867 | 0.5332 |
| ticker_relevance | b-c | 133 | 150 | 0.8867 | 0.5917 |
| materiality | b-c | 108 | 150 | 0.7200 | 0.5669 |
| direction | b-c | 114 | 150 | 0.7600 | 0.6532 |
| event_type | b-c | 126 | 150 | 0.8400 | 0.8176 |
| time_horizon | b-c | 98 | 150 | 0.6533 | 0.4845 |

Agreement measures annotator consistency; it does not turn pseudo-labels into human ground truth. Three annotation runs represent only two model families, so they are not three independent systems or three independent evidence sources.

## Manual sanity check

Rows=24; rows with any check filled=24; status=available; missing columns=[].

| field | ok | not ok | reviewed | ok rate |
| --- | --- | --- | --- | --- |
| human_relevance_ok | 23 | 1 | 24 | 0.9583 |
| human_materiality_ok | 21 | 3 | 24 | 0.8750 |
| human_direction_ok | 23 | 1 | 24 | 0.9583 |
| human_event_type_ok | 24 | 0 | 24 | 1.0000 |
| human_evidence_span_ok | 23 | 1 | 24 | 0.9583 |

This is a small, non-blinded quality-control sample, not full human ground truth; it cannot estimate population-level annotation accuracy.

## Keyword/rule baseline versus semantic pseudo-labels

Analysis-eligible merged rows=122; available=True.

| rule field | consensus field | n | accuracy | macro-F1 |
| --- | --- | --- | --- | --- |
| rule_direction | consensus_direction | 122 | 0.3770 | 0.2282 |
| rule_event_type | consensus_event_type | 122 | 0.1475 | 0.0865 |
| rule_materiality | consensus_materiality | 122 | 0.2213 | 0.1595 |
| rule_relevance | consensus_ticker_relevance | 122 | 0.6885 | 0.2090 |

Error taxonomy includes missing context/materiality, ticker mismatch, market-wide versus direct confusion, boilerplate noise, mixed direction, and overlapping event types. Semantic labels remain a controlled pseudo-label reference, not ground truth.

## Artifact schema, hash, and freshness

| artifact | path | schema version | SHA256 | modified UTC | latest upstream UTC | freshness |
| --- | --- | --- | --- | --- | --- | --- |
| consensus | outputs/pseudo_labels_consensus.csv | pseudo_label_consensus_v2 | 658e6b8b827f7bc5b76f6cf72f5c100abd77dba0be95be563bec94d1b31715ba | 2026-07-10T09:43:10+00:00 | 2026-07-10T08:39:31+00:00 | fresh |
| event_tests | outputs/event_window_stat_tests.csv | event_window_tests_v3 | 0ef12ace27fec1c809b24a2b93f077258c51840f5bab656e23752d7975721c7f | 2026-07-10T14:23:42+00:00 | 2026-07-10T14:20:01+00:00 | fresh |
| ml_predictions | outputs/ml_predictions_outperform.csv | outperform_ml_predictions_v2 | 8ac3ddf5fcb328e9713b2311321e8d810a97f0c03f06d90923b90257aff03da9 | 2026-07-12T00:56:48+00:00 | 2026-07-12T00:54:15+00:00 | fresh |
| topk | outputs/topk_portfolio_simulation.csv | topk_nonoverlap_v2 | f9c9becda04e72dff11f89ae7da777e0842ba21ea1c45a34a27d3ffd93d6f280 | 2026-07-12T01:02:23+00:00 | 2026-07-12T00:56:48+00:00 | fresh |
| placebo | outputs/placebo_pre_event_stat_tests.csv | unavailable | ca33bd20fedd3b18ca19f2e6bd4648c1b787dd725f6f3912f83fe36514e8a709 | 2026-07-12T00:53:47+00:00 | unavailable | no_upstream_reference |
| ml_paired | outputs/ml_paired_daily_metrics_outperform.csv | unavailable | ac180fa8c86a559d76a80397490a0e7b24b3bdb1f2d2ba72019936b214d02a40 | 2026-07-12T01:01:30+00:00 | unavailable | no_upstream_reference |
| ml_bootstrap | outputs/ml_bootstrap_delta_outperform.csv | unavailable | 3bcab88907c668030354035080a6f31138d950f85db3b3d8b296a63c4681bc81 | 2026-07-12T01:01:30+00:00 | unavailable | no_upstream_reference |
| topk_null | outputs/topk_random_null_summary.csv | unavailable | 47fe353387e3bb42de63afc6e97d88c1967ee0a4c322be04c0e554730bd01af7 | 2026-07-12T01:11:18+00:00 | unavailable | no_upstream_reference |
| topk_cost | outputs/topk_cost_sensitivity_summary.csv | unavailable | f11bba86218faf4e93fcdab805b6bfa25813b993f221751607e60cf228541d2d | 2026-07-12T01:11:18+00:00 | unavailable | no_upstream_reference |
| family_sensitivity | outputs/consensus_family_sensitivity_summary.csv | unavailable | afa707757773638b68c6ac32b843d997e8b5a5c69a0aaa87f3966df77f6bbe7d | 2026-07-12T00:53:40+00:00 | unavailable | no_upstream_reference |

Freshness compares each artifact mtime with newest available upstream reference; SHA256 identifies exact bytes used by this report run.

## Semantic signal audit and corrected event-window tests

Gate rule: `p_value_bh <= 0.05 AND diff_ci_low > 0 under Benjamini-Hochberg correction`. Tests=8; BH-FDR significant=1; positive-CI=2; joint robust-positive fraction=1/8; claim gate pass=True. Interpretation: exploratory positive association present.

Planned comparisons are direct/high-or-medium materiality versus low materiality, support versus risk, event-type groups, and semantic versus keyword/news-count baselines. Counts above refer to corrected test rows, not fraction of articles; event-level denominators remain in structured event artifacts.

Consistency checks: FDR flag mismatches=0; robust-positive flag mismatches=0. Negative robust effects are not counted as support for a positive claim.

## Optional robustness checks

Available={'placebo': True, 'ml_paired': True, 'ml_bootstrap': True, 'topk_null': True, 'topk_cost': True, 'family_sensitivity': True}; placebo joint-positive=0/4; family-sensitivity rows=5. Missing optional artifacts remain unavailable and do not block report generation.

## Point-in-time ML experiment

Prediction rows=685704; unique folds=3; purge trading days=[20]; purged OOS verification=True; status=verified_from_fold_metadata; configs=A_technical, B_technical_keyword, C_technical_semantic, D_all; models=LogisticRegression, RandomForest.

| fold | train start | train end | test start | test end | purge trading days |
| --- | --- | --- | --- | --- | --- |
| 1 | 2021-10-14 | 2022-01-06 | 2022-02-11 | 2023-07-14 | 20 |
| 2 | 2021-10-14 | 2023-06-16 | 2023-07-17 | 2024-12-16 | 20 |
| 3 | 2021-10-14 | 2024-11-18 | 2024-12-17 | 2026-06-01 | 20 |

| metric | paired rows | baseline mean | comparison mean | mean delta |
| --- | --- | --- | --- | --- |
| auc | 10720 | 0.4987859851841035 | 0.5077274414618087 | 0.008941456277705222 |
| balanced_accuracy | 10720 | 0.4962194204808665 | 0.5017280469501291 | 0.005508626469262693 |
| daily_rank_ic | 10720 | -0.00208379320853634 | 0.013083896667428457 | 0.015167689875964797 |
| f1 | 10720 | 0.43072887299074886 | 0.4534448712644368 | 0.02271599827368796 |
| precision_at_10_by_date | 10720 | 0.4662220149253731 | 0.47141791044776116 | 0.005195895522388059 |

Bootstrap delta rows=50. Balanced accuracy/AUC near 0.5, weak F1/Precision@K, near-zero rank IC, or small/unstable deltas must be reported as near-random or null predictive evidence, not useful stock filtering.

## Non-overlap turnover-cost Top-K simulation

Rows=2592; entry periods=54; top-K=[5, 10]; strategies=equal_weight_universe, model_topk, random_topk_deterministic; holding days=[20]; cost rates=[0.005].

Non-overlap=True; turnover-cost equation=True; net-return equations=True; overall status=verified_nonoverlap_turnover_cost (verified).

Random-null rows=16; one-sided null p<=0.05 rows=3; cost-sensitivity rows=64; tested cost rates=[0.0, 0.0025, 0.005, 0.01]. Passing accounting checks does not establish performance. Null-comparable results or gains erased by cost are null findings, not alpha.

## Evidence cards and outcome review

Case candidates=5; outcome-review labels=114. These are retrospective, selected-case structured reviews: not trading recommendations, semantic ground truth, causal validation, representative outcome accuracy, or evidence that cards improve human decisions.

## Claim-vs-evidence summary

Consensus eligible=122/150; robust-positive event tests=1; purged OOS verified=True; Top-K methodology status=verified_nonoverlap_turnover_cost; outcome-review rows=114.

## Interpretation rules and limitations

- LLM consensus labels are pseudo-labels, not ground truth; three runs cover only two model families.
- Event results are associations. They require BH-FDR significance and a strictly positive bootstrap CI before supporting a positive exploratory claim; they never establish causality.
- ML claims require fold metadata to verify purged, out-of-sample predictions.
- Top-K claims require non-overlap plus turnover-scaled cost and net-return equation checks.
- Weak or failed gates remain valid negative findings.
- No artifact establishes causal impact, persistent alpha, or investment suitability.

## Conclusion

Structured semantic annotation improves auditability of relevance, materiality, direction, and evidence compared with keyword counts. Statistical, ML, and portfolio results remain exploratory and must be interpreted through recorded claim gates and limitations.
