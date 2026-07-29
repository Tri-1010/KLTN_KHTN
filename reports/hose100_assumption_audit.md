# HOSE100 assumption audit — LLM material hybrid

## Research objective

Test whether period-aggregated LLM material-event features add predictive value beyond technical indicators.

- H0: Technical indicators alone are sufficient.
- H1: Technical + LLM material-event features improve prediction vs technical-only.
- Main comparison: `Config_Hybrid - Config_A` on balanced accuracy.

## Universe and data checks

- Universe: `HOSE100_quality`
- Selection: original HOSE80 + 20 added liquid HOSE tickers.
- Price source: `data/prices/hose100_quality_prices.csv`
- Price tickers: 100
- Price rows: 117,566
- Annotation source: `data/experiments/llm_semantic/article_semantics_cache.csv`
- OK annotations: 11,913 rows across 80 tickers
- Added 20 tickers have 0 annotations, so their LLM features are zero/no-news.

Added tickers:

```text
CII, PC1, TCH, KBC, VPI, IJC, LCG, VOS, TCM, AAA,
PAN, SZC, CTD, FCN, DPG, SBT, IDI, HT1, KDC, MSH
```

## Coverage

Direct-indirect coverage:

| unit | n_samples | test_samples | llm_nonzero_rows | annotations |
|---|---:|---:|---:|---:|
| 1week | 24,489 | 4,888 | 1,019 | 1,112 |
| 2week | 12,304 | 2,400 | 966 | 1,112 |
| month | 5,689 | 1,088 | 866 | 1,112 |
| 2month | 2,888 | 488 | 741 | 1,112 |
| quarter | 1,889 | 388 | 646 | 1,112 |

## Aggregate result

Across 80 HOSE100 config/model/unit/relevance combinations:

- Mean delta: +0.0007
- Median delta: +0.0007
- Positive delta rate: 53.8%
- Max delta: +0.0318
- Min delta: -0.0814

By unit:

| unit | mean delta | positive rate | max | min |
|---|---:|---:|---:|---:|
| 1week | +0.0065 | 68.8% | +0.0224 | -0.0079 |
| 2week | +0.0034 | 50.0% | +0.0252 | -0.0046 |
| 2month | +0.0053 | 50.0% | +0.0255 | -0.0067 |
| quarter | +0.0006 | 50.0% | +0.0318 | -0.0414 |
| month | -0.0121 | 50.0% | +0.0196 | -0.0814 |

By relevance:

| relevance | mean delta | positive rate | max | min |
|---|---:|---:|---:|---:|
| direct | +0.0035 | 70.0% | +0.0297 | -0.0814 |
| indirect_only | +0.0022 | 40.0% | +0.0252 | -0.0215 |
| direct_indirect | -0.0009 | 55.0% | +0.0243 | -0.0814 |
| any_relevance | -0.0020 | 50.0% | +0.0318 | -0.0814 |

## Best positive deltas

| relevance | unit | model | Config_A | Config_Hybrid | delta | p_mid |
|---|---|---|---:|---:|---:|---:|
| any_relevance | quarter | Logistic Regression | 0.6047 | 0.6365 | +0.0318 | 0.0645 |
| direct | quarter | Random Forest | 0.6962 | 0.7259 | +0.0297 | 0.0241 |
| direct | 2month | XGBoost | 0.6576 | 0.6831 | +0.0255 | 0.2750 |
| indirect_only | 2week | Logistic Regression | 0.6807 | 0.7059 | +0.0252 | 0.0000 |
| direct_indirect | quarter | Random Forest | 0.6962 | 0.7204 | +0.0243 | 0.0987 |
| direct_indirect | 1week | XGBoost | 0.6735 | 0.6959 | +0.0224 | 0.0376 |
| direct | 1week | XGBoost | 0.6735 | 0.6940 | +0.0205 | 0.0144 |
| any_relevance | month | LightGBM | 0.6826 | 0.7022 | +0.0196 | 0.4215 |

## Significance check

Uncorrected mid-p McNemar:

- p_mid < 0.05: 21 / 80 combinations
- positive delta and p_mid < 0.05: 15 / 80 combinations

Benjamini-Hochberg FDR 5%:

- BH pass: 9 / 80 combinations
- positive delta and BH pass: 4 / 80 combinations

Positive BH-surviving effects:

| relevance | unit | model | delta | p_mid | q_bh |
|---|---|---|---:|---:|---:|
| indirect_only | 2week | Logistic Regression | +0.0252 | 0.0000 | 0.0000 |
| indirect_only | 1week | Logistic Regression | +0.0119 | 0.0000 | 0.0007 |
| direct_indirect | 1week | Logistic Regression | +0.0040 | 0.0004 | 0.0047 |
| indirect_only | 1week | XGBoost | +0.0183 | 0.0048 | 0.0423 |

Negative BH-surviving effects also exist, especially Logistic Regression at month/2month. So evidence is mixed, not uniformly positive.

## Assumption review

1. Price data assumption: valid for HOSE100; all 100 selected tickers have price rows.
2. Annotation assumption: not valid for all 100. Existing LLM annotation cache covers 80 old tickers only; the 20 added tickers have zero annotations.
3. No-new-LLM assumption: satisfied. No additional LLM calls needed; new tickers enter with zero/no-news LLM features.
4. Feature timing assumption: period-level LLM features from current period predict next-period return, so no direct future-label leakage.
5. Statistical power assumption: improved. HOSE100 increases samples vs HOSE80, e.g. direct_indirect 1week n_samples 19,521 -> 24,489 and test_samples 3,920 -> 4,888.
6. Dilution risk: high. Because the 20 added tickers have no annotations, hybrid signal can be diluted. HOSE100 tests robustness of adding no-news tickers more than it tests LLM value on those new tickers.

## Verdict

HOSE100 improves sample size and shows some positive LLM-hybrid effects, especially at 1week/2week/quarter and in direct/indirect variants. However, average improvement is near zero and negative significant cases exist.

Conclusion for thesis/report:

> Expanding to HOSE100 increases statistical power and preserves several positive Config_Hybrid improvements over Config_A, but evidence remains configuration-dependent. Since the 20 newly added tickers have no LLM annotations, HOSE100 mainly tests robustness under larger no-news coverage rather than full semantic coverage. Stronger evidence requires annotating the additional tickers or selecting a larger universe with comparable annotation coverage.
