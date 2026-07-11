# Claim vs evidence table

| Claim luận văn | Evidence artifact | Corrected result | Claim level |
| --- | --- | --- | --- |
| Keyword/news-count thiếu ngữ cảnh | reports/rule_vs_semantic_labels_report.md | Rule baseline versus semantic pseudo-labels; not human ground truth | Supported exploratory |
| Annotation provenance | outputs/annotation_manifest_*.json | manifest runs=3; provider, routed model vendor, and hashes below | Descriptive limitation |
| Consensus categorical labels | outputs/pseudo_labels_consensus.csv | rows=150; disagreement=4, majority_vote=106, unanimous=40; eligible=122/150 | Descriptive |
| Semantic event-window signal | outputs/event_window_stat_tests.csv | tests=8; FDR=1; positive-CI=2; joint gate=1; flag mismatches=0 | Supported exploratory |
| Point-in-time ML ranking | outputs/ml_predictions_outperform.csv | rows=685704; folds=3; purge=[20]; status=verified_from_fold_metadata | Exploratory |
| Top-K simulation | outputs/topk_portfolio_simulation.csv | rows=2592; periods=54; non-overlap=True; turnover-cost=True; net equations=True; status=verified_nonoverlap_turnover_cost | Weak / exploratory |
| Evidence cards and outcome review | outputs/evidence_cards.*, outputs/outcome_review_labels.csv | outcome-review rows=114 | Descriptive |

## Corrected event claim gate

Rule: `p_value_bh <= 0.05 AND diff_ci_low > 0 under Benjamini-Hochberg correction`. Available=True; pass=True.

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
| ml_predictions | outperform_ml_predictions_v2 | 8ac3ddf5fcb328e9713b2311321e8d810a97f0c03f06d90923b90257aff03da9 | 2026-07-10T14:34:21+00:00 | 2026-07-10T14:31:23+00:00 | fresh |
| topk | topk_nonoverlap_v2 | 1cfed60e59255449343cc27862c5b65ece936979133354d7331cfa4aa89f7a72 | 2026-07-10T14:35:04+00:00 | 2026-07-10T14:34:21+00:00 | fresh |

## Purged OOS fold metadata

| fold | train start | train end | test start | test end | purge trading days |
| --- | --- | --- | --- | --- | --- |
| 1 | 2021-10-14 | 2022-01-06 | 2022-02-11 | 2023-07-14 | 20 |
| 2 | 2021-10-14 | 2023-06-16 | 2023-07-17 | 2024-12-16 | 20 |
| 3 | 2021-10-14 | 2024-11-18 | 2024-12-17 | 2026-06-01 | 20 |

## Safe interpretation

Consensus labels are pseudo-labels, not ground truth. Event-study, ML, and Top-K results remain exploratory and are not alpha or investment claims.
