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
| a | deepseek | deepseek-chat | deepseek-v4-flash | deepseek | native | legacy_reconstructed | semantic_news_materiality_v1 | semantic_news_annotation_v1 | True | 68534c7c70e4284f5e49799ca2702e528c619475a37e2adfac5f1053154f9b6e |
| b | deepseek | deepseek-chat | deepseek-v4-flash | deepseek | native | legacy_reconstructed | semantic_news_materiality_v1 | semantic_news_annotation_v1 | True | 6ce4996daa89a8befae87d8d35da277755f35dc1fd378b1d3bd94061e5a87d45 |
| c | anthropic | cx/gpt-5.4-mini | gpt-5.4-mini | openai | gateway_or_proxy | legacy_reconstructed | semantic_news_materiality_v1 | semantic_news_annotation_v1 | True | 08d2de8c56d41e5373256b59f5f90fac304fd369b672745eb657921be0f66ba7 |

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
| consensus | outputs/pseudo_labels_consensus.csv | pseudo_label_consensus_v2 | 6342f27827e3327b78099fc1e1bbf13d4340c598764379dff0b14ac5f357da54 | 2026-07-30T11:51:56+00:00 | 2026-07-30T11:51:48+00:00 | fresh |
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

## Harmonized keyword–semantic comparison

Available=True; status=primary_gate_failed; mode=pilot; run=canonical_150_v7; claim level=common_stratified_article_spine_only; same-row primary gate pass=False. Pilot and sample500 runs remain validation-sample evidence and cannot produce full-corpus claims.

This section reads structured per-run inference and manifest artifacts only; missing or stale runs remain unavailable rather than being parsed from Markdown.

## Point-in-time ML experiment

Prediction rows=685704; unique folds=3; purge trading days=[20]; purged OOS verification=True; status=verified_from_fold_metadata; configs=A_technical, B_technical_keyword, C_technical_semantic, D_all; models=LogisticRegression, RandomForest.

| fold | train start | train end | test start | test end | purge trading days |
| --- | --- | --- | --- | --- | --- |
| 1 | 2021-10-14 | 2022-01-06 | 2022-02-11 | 2023-07-14 | 20 |
| 2 | 2021-10-14 | 2023-06-16 | 2023-07-17 | 2024-12-16 | 20 |
| 3 | 2021-10-14 | 2024-11-18 | 2024-12-17 | 2026-06-01 | 20 |

| metric | paired rows | baseline mean | comparison mean | mean delta |
| --- | --- | --- | --- | --- |
| A_technical\|B_technical_keyword\|LogisticRegression\|auc | 1072 | 0.4892192622732334 | 0.49871582711216 | 0.009496564838926564 |
| A_technical\|B_technical_keyword\|LogisticRegression\|balanced_accuracy | 1072 | 0.49086079352008377 | 0.492598739479063 | 0.001737945958979242 |
| A_technical\|B_technical_keyword\|LogisticRegression\|daily_rank_ic | 1072 | -0.028471310997488185 | 0.006882311345767966 | 0.035353622343256154 |
| A_technical\|B_technical_keyword\|LogisticRegression\|f1 | 1072 | 0.3744445606136091 | 0.45333969642875116 | 0.07889513581514213 |
| A_technical\|B_technical_keyword\|LogisticRegression\|precision_at_10_by_date | 1072 | 0.45597014925373136 | 0.475839552238806 | 0.019869402985074624 |
| A_technical\|B_technical_keyword\|RandomForest\|auc | 1072 | 0.5047542829179611 | 0.5042537810215659 | -0.0005005018963951668 |
| A_technical\|B_technical_keyword\|RandomForest\|balanced_accuracy | 1072 | 0.5011096489143645 | 0.5005426992735967 | -0.0005669496407677372 |
| A_technical\|B_technical_keyword\|RandomForest\|daily_rank_ic | 1072 | 0.008941615922818745 | 0.011993265223554475 | 0.0030516493007357254 |
| A_technical\|B_technical_keyword\|RandomForest\|f1 | 1072 | 0.44863352693683034 | 0.4656875371993339 | 0.0170540102625036 |
| A_technical\|B_technical_keyword\|RandomForest\|precision_at_10_by_date | 1072 | 0.46539179104477607 | 0.47322761194029844 | 0.007835820895522387 |
| A_technical\|C_technical_semantic\|LogisticRegression\|auc | 1072 | 0.4892192622732334 | 0.5001217884007518 | 0.010902526127518478 |
| A_technical\|C_technical_semantic\|LogisticRegression\|balanced_accuracy | 1072 | 0.49086079352008377 | 0.49185629484319476 | 0.000995501323110934 |
| A_technical\|C_technical_semantic\|LogisticRegression\|daily_rank_ic | 1072 | -0.028471310997488185 | -0.010689209997820866 | 0.017782100999667306 |
| A_technical\|C_technical_semantic\|LogisticRegression\|f1 | 1072 | 0.3744445606136091 | 0.40059298658378856 | 0.026148425970179495 |
| A_technical\|C_technical_semantic\|LogisticRegression\|precision_at_10_by_date | 1072 | 0.45597014925373136 | 0.45764925373134324 | 0.0016791044776119422 |
| A_technical\|C_technical_semantic\|RandomForest\|auc | 1072 | 0.5047542829179611 | 0.5132390679343315 | 0.008484785016370403 |
| A_technical\|C_technical_semantic\|RandomForest\|balanced_accuracy | 1072 | 0.5011096489143645 | 0.5091600318028571 | 0.008050382888492604 |
| A_technical\|C_technical_semantic\|RandomForest\|daily_rank_ic | 1072 | 0.008941615922818745 | 0.01924339018949507 | 0.010301774266676323 |
| A_technical\|C_technical_semantic\|RandomForest\|f1 | 1072 | 0.44863352693683034 | 0.4650782666914725 | 0.01644473975464217 |
| A_technical\|C_technical_semantic\|RandomForest\|precision_at_10_by_date | 1072 | 0.46539179104477607 | 0.46875 | 0.003358208955223875 |
| A_technical\|D_all\|LogisticRegression\|auc | 1072 | 0.4892192622732334 | 0.5109244203173087 | 0.02170515804407522 |
| A_technical\|D_all\|LogisticRegression\|balanced_accuracy | 1072 | 0.49086079352008377 | 0.49980124964221995 | 0.00894045612213623 |
| A_technical\|D_all\|LogisticRegression\|daily_rank_ic | 1072 | -0.028471310997488185 | 0.02282705964658473 | 0.05129837064407291 |
| A_technical\|D_all\|LogisticRegression\|f1 | 1072 | 0.3744445606136091 | 0.45498966593271034 | 0.0805451053191012 |
| A_technical\|D_all\|LogisticRegression\|precision_at_10_by_date | 1072 | 0.45597014925373136 | 0.47472014925373135 | 0.018750000000000003 |
| A_technical\|D_all\|RandomForest\|auc | 1072 | 0.5047542829179611 | 0.5128671265897887 | 0.008112843671827713 |
| A_technical\|D_all\|RandomForest\|balanced_accuracy | 1072 | 0.5011096489143645 | 0.5112519390860439 | 0.010142290171679454 |
| A_technical\|D_all\|RandomForest\|daily_rank_ic | 1072 | 0.008941615922818745 | 0.024600455214222126 | 0.015658839291403374 |
| A_technical\|D_all\|RandomForest\|f1 | 1072 | 0.44863352693683034 | 0.48704982030017013 | 0.03841629336333977 |
| A_technical\|D_all\|RandomForest\|precision_at_10_by_date | 1072 | 0.46539179104477607 | 0.48143656716417915 | 0.01604477611940298 |
| B_technical_keyword\|C_technical_semantic\|LogisticRegression\|auc | 1072 | 0.49871582711216 | 0.5001217884007518 | 0.0014059612885919156 |
| B_technical_keyword\|C_technical_semantic\|LogisticRegression\|balanced_accuracy | 1072 | 0.492598739479063 | 0.49185629484319476 | -0.00074244463586831 |
| B_technical_keyword\|C_technical_semantic\|LogisticRegression\|daily_rank_ic | 1072 | 0.006882311345767966 | -0.010689209997820866 | -0.01757152134358884 |
| B_technical_keyword\|C_technical_semantic\|LogisticRegression\|f1 | 1072 | 0.45333969642875116 | 0.40059298658378856 | -0.0527467098449626 |
| B_technical_keyword\|C_technical_semantic\|LogisticRegression\|precision_at_10_by_date | 1072 | 0.475839552238806 | 0.45764925373134324 | -0.018190298507462684 |
| B_technical_keyword\|C_technical_semantic\|RandomForest\|auc | 1072 | 0.5042537810215659 | 0.5132390679343315 | 0.00898528691276557 |
| B_technical_keyword\|C_technical_semantic\|RandomForest\|balanced_accuracy | 1072 | 0.5005426992735967 | 0.5091600318028571 | 0.008617332529260346 |
| B_technical_keyword\|C_technical_semantic\|RandomForest\|daily_rank_ic | 1072 | 0.011993265223554475 | 0.01924339018949507 | 0.007250124965940599 |
| B_technical_keyword\|C_technical_semantic\|RandomForest\|f1 | 1072 | 0.4656875371993339 | 0.4650782666914725 | -0.0006092705078614238 |
| B_technical_keyword\|C_technical_semantic\|RandomForest\|precision_at_10_by_date | 1072 | 0.47322761194029844 | 0.46875 | -0.004477611940298509 |
| B_technical_keyword\|D_all\|LogisticRegression\|auc | 1072 | 0.49871582711216 | 0.5109244203173087 | 0.01220859320514865 |
| B_technical_keyword\|D_all\|LogisticRegression\|balanced_accuracy | 1072 | 0.492598739479063 | 0.49980124964221995 | 0.007202510163156985 |
| B_technical_keyword\|D_all\|LogisticRegression\|daily_rank_ic | 1072 | 0.006882311345767966 | 0.02282705964658473 | 0.015944748300816755 |
| B_technical_keyword\|D_all\|LogisticRegression\|f1 | 1072 | 0.45333969642875116 | 0.45498966593271034 | 0.0016499695039590774 |
| B_technical_keyword\|D_all\|LogisticRegression\|precision_at_10_by_date | 1072 | 0.475839552238806 | 0.47472014925373135 | -0.0011194029850746237 |
| B_technical_keyword\|D_all\|RandomForest\|auc | 1072 | 0.5042537810215659 | 0.5128671265897887 | 0.008613345568222878 |
| B_technical_keyword\|D_all\|RandomForest\|balanced_accuracy | 1072 | 0.5005426992735967 | 0.5112519390860439 | 0.010709239812447195 |
| B_technical_keyword\|D_all\|RandomForest\|daily_rank_ic | 1072 | 0.011993265223554475 | 0.024600455214222126 | 0.012607189990667652 |
| B_technical_keyword\|D_all\|RandomForest\|f1 | 1072 | 0.4656875371993339 | 0.48704982030017013 | 0.02136228310083618 |
| B_technical_keyword\|D_all\|RandomForest\|precision_at_10_by_date | 1072 | 0.47322761194029844 | 0.48143656716417915 | 0.008208955223880595 |

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
