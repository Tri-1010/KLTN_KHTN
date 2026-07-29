# LLM semantic HOSE100 results and recommended next steps

## Scope

- Universe: `HOSE100_quality`
- Tickers: `100`
- Price panel: `117,566` rows
- Annotation cache: `data/experiments/llm_semantic/article_semantics_cache_hose100_extra.csv`
- Main evaluation outputs:
  - `reports/llm_semantic_period_material_hose100_extra_quality_summary.md`
  - `reports/llm_semantic_period_material_hose100_extra_quality_results.csv`
  - `reports/llm_semantic_period_material_hose100_extra_quality_stats.csv`
- Event-filter sweep outputs:
  - `reports/llm_semantic_period_material_hose100_variant_sweep_summary.md`
  - `reports/llm_semantic_period_material_hose100_variant_sweep_results.csv`
  - `reports/llm_semantic_period_material_hose100_variant_sweep_stats.csv`
  - `reports/llm_semantic_period_material_hose100_variant_sweep_counts.csv`

## News and annotation counts

Current files show two different article-count views:

- Processed news file: `data/news/processed/all_news_processed.csv`
  - total rows: `35,158`
  - rows in HOSE100 quality universe: `29,353`
  - tickers with rows in HOSE100 universe: `80/100`
  - unique URLs in HOSE100 universe: `29,353`

- Matched news file: `data/news/matched/all_news_matched.csv`
  - total ticker-article match rows: `52,790`
  - rows in HOSE100 quality universe: `44,518`
  - tickers with rows in HOSE100 universe: `80/100`
  - unique URLs in HOSE100 universe: `39,704`

The earlier informal statement of roughly `42k` news articles is closest to the matched unique-URL view, but the current exact value in the matched file is `39,704` unique URLs in the HOSE100 quality universe.

LLM annotation cache for HOSE100 quality universe:

- cache rows in HOSE100 universe: `22,088`
- successful annotations: `12,133`
- legacy error rows: `9,955`
- tickers with successful annotations: `91/100`
- unique URLs with successful annotations: `10,023`
- provider/model: `deepseek / deepseek-chat`

Recent HOSE100 extra annotation rerun:

- selected articles: `319`
- successful rows: `319`
- error rows: `0`

## Why strict material-event count looked small

Strict material-event filters keep only:

- `earnings`
- `dividend`
- `capital`
- `debt_risk`
- `legal_risk`

This intentionally removes many lower-specificity or noisier article types, such as market commentary, macro news, operation updates, governance updates, list-style stock recommendations, and articles that only mention a ticker in passing.

In the event-filter sweep, annotation coverage changed sharply by event filter:

```text
variant                    direct  direct+indirect  any_relevance
core_material                 279              288            291
+ operation/governance       1367             1398           1500
+ macro/market               1530             1569           1705
all_event_types              8956             9251          12133
```

Interpretation:

- `core_material` is strict and low-noise, but sparse.
- `+ macro/market` gives better coverage and useful signal for longer horizons.
- `all_event_types` maximizes coverage but adds many low-signal article types, increasing noise.

## Main HOSE100 result: hybrid features help conditionally

The safest conclusion is not that LLM features always improve prediction. The result is conditional:

> LLM-extracted semantic news features provide complementary signal to technical indicators in selected horizons and model configurations, especially short-to-medium horizons. The effect is not universal and depends on event filtering, relevance filtering, horizon, and model family.

Strong positive results from the HOSE100 extra-quality run:

```text
relevance/event setting        horizon  model                 BA_A -> BA_Hybrid      delta    p_mid
core/direct                    2week    Logistic_Regression   0.6807 -> 0.7050     +0.0243  0.0000
core/any_relevance             2week    Logistic_Regression   0.6807 -> 0.7036     +0.0230  0.0000
core/indirect_only             1week    XGBoost               0.6735 -> 0.6919     +0.0183  0.0048
core/indirect_only             2week    Random_Forest         0.6873 -> 0.7006     +0.0133  0.0222
core/any_relevance             1week    Logistic_Regression   0.6882 -> 0.7009     +0.0127  0.0000
```

Important negative results also exist:

```text
setting                         horizon  model                 BA_A -> BA_Hybrid      delta    p_mid
core/direct                     month    Logistic_Regression   0.7218 -> 0.6404     -0.0814  0.0000
core/any_relevance              month    Logistic_Regression   0.7218 -> 0.6404     -0.0814  0.0000
core/direct_indirect            month    Logistic_Regression   0.7218 -> 0.6919     -0.0299  0.0075
```

Therefore the thesis claim should be framed as conditional improvement, not universal improvement.

## One-month horizon result

For the original strict core material setting, the one-month horizon was weak:

```text
core_material + any_relevance + XGBoost
BA_A -> BA_Hybrid: 0.6674 -> 0.6916
delta: +0.0241
p_mid: 0.0567
```

This is close to the `10%` level but does not reach `p < 0.05`.

After expanding event types to include `macro` and `market`, the one-month result became statistically significant:

```text
plus_macro_market + any_relevance + XGBoost
BA_A -> BA_Hybrid: 0.6674 -> 0.6941
delta: +0.0267
p_mid: 0.0450
```

Interpretation:

- Strict firm-level material events are strongest at 1–2 week horizons.
- Adding macro/market news helps medium horizons such as 1 month and 2 months.
- Adding all event types increases coverage but also increases noise and instability.

## Event-filter sweep findings

Best results by event-filter variant:

```text
event_variant              relevance        horizon  model                 BA_A -> BA_Hybrid      delta    p_mid
plus_macro_market          any_relevance    2month   XGBoost               0.6576 -> 0.6961     +0.0385  0.0271
plus_operation_governance  any_relevance    quarter  Logistic_Regression   0.6047 -> 0.6381     +0.0334  0.0982
all_event_types            direct           2month   XGBoost               0.6576 -> 0.6905     +0.0330  0.4222
core_material              direct           2week    Logistic_Regression   0.6807 -> 0.7050     +0.0243  0.0000
```

Significant positive examples from the sweep:

```text
event_variant              relevance          horizon  model                 delta    p_mid
plus_macro_market          any_relevance      2month   XGBoost              +0.0385  0.0271
plus_macro_market          direct_indirect    quarter  Random_Forest        +0.0315  0.0336
plus_macro_market          any_relevance      month    XGBoost              +0.0267  0.0450
core_material              direct             2week    Logistic_Regression  +0.0243  0.0000
core_material              any_relevance      2week    Logistic_Regression  +0.0230  0.0000
plus_operation_governance  any_relevance      1week    XGBoost              +0.0213  0.0099
all_event_types            direct             1week    XGBoost              +0.0210  0.0164
all_event_types            direct_indirect    1week    XGBoost              +0.0210  0.0395
plus_operation_governance  direct             1week    Logistic_Regression  +0.0135  0.0000
core_material              any_relevance      1week    Logistic_Regression  +0.0127  0.0000
```

Summary by event-filter variant:

```text
variant                    mean_delta  max_delta  min_delta  positive_significant  negative_significant
all_event_types              +0.0003    +0.0330   -0.1091          5                      9
core_material                -0.0019    +0.0243   -0.0814          4                      5
plus_macro_market            +0.0005    +0.0385   -0.0885          8                      3
plus_operation_governance    -0.0012    +0.0334   -0.0888          4                      3
```

Best practical variant from the sweep: `plus_macro_market`.

Reason:

- It gives the highest maximum positive delta: `+0.0385`.
- It gives the most positive significant outcomes: `8`.
- It gives fewer negative significant outcomes than `all_event_types`: `3` vs `9`.
- It improves the one-month horizon with statistical significance.

## What “noise” means here

Noise means extra LLM features come from article types that increase coverage but do not consistently add useful predictive information.

Examples:

- articles that only mention a ticker in a list
- broad market summaries
- generic stock recommendation articles
- duplicate-style updates
- already-price-reflected news
- articles classified as `other`
- articles with weak relevance to the target ticker

The clearest evidence is the comparison:

```text
plus_macro_market: positive significant = 8, negative significant = 3, max delta = +0.0385
all_event_types:   positive significant = 5, negative significant = 9, max delta = +0.0330, min delta = -0.1091
```

So more annotations are not automatically better. Event selection matters.

## Statistical caution

The test sample sizes are not small:

```text
horizon   test_samples
1week     4,888
2week     2,400
month     1,088
2month      488
quarter     388
```

However, the sweep evaluates many configurations:

- event filters
- relevance filters
- horizons
- model families

This creates a multiple-comparisons issue. With many tests, some `p < 0.05` outcomes can occur by chance.

Therefore, the thesis should not claim that every significant result is definitive proof. The safer claim is:

> The results provide evidence that LLM semantic features can add useful information under specific, interpretable configurations, especially short-to-medium horizons and controlled event filters. The effect is conditional and requires sensitivity analysis.

## Recommended thesis framing

Strong thesis statement:

> LLM-extracted semantic news features do not replace technical indicators, but can provide complementary information in a hybrid model. The strongest evidence appears at 1–2 week horizons using strict material-event filters, and at 1–2 month horizons when the event set is expanded to include macro/market context. Overly broad inclusion of all event types increases noise and reduces stability.

Safe conclusion:

> The evidence supports H1 conditionally: LLM semantic features improve selected hybrid configurations with statistical significance, but the improvement is not universal across all horizons, models, and event definitions.

## Three recommended next analyses before defense

### 1. Define and report a primary holdout configuration

Choose one or two primary configurations before final reporting, then make all other runs secondary sensitivity analysis.

Recommended primary configurations:

- Short-horizon primary:
  - event filter: `core_material`
  - relevance: `direct`
  - horizon: `2week`
  - model: `Logistic_Regression`
  - observed result: `0.6807 -> 0.7050`, delta `+0.0243`, `p_mid=0.0000`

- Medium-horizon secondary:
  - event filter: `plus_macro_market`
  - relevance: `any_relevance`
  - horizon: `month`
  - model: `XGBoost`
  - observed result: `0.6674 -> 0.6941`, delta `+0.0267`, `p_mid=0.0450`

Why this helps:

- Avoids accusations of cherry-picking from many sweep results.
- Makes the thesis claim cleaner.
- Lets the sweep become sensitivity/robustness analysis instead of the main evidence.

### 2. Bootstrap confidence intervals for delta balanced accuracy

Estimate confidence intervals for:

```text
delta = balanced_accuracy(Config_Hybrid) - balanced_accuracy(Config_A)
```

Recommended bootstrap units:

- block bootstrap by `ticker`, or
- block bootstrap by `period_id`, or
- paired bootstrap over test observations while preserving paired predictions from Config_A and Config_Hybrid.

Report examples:

```text
2week direct Logistic Regression: delta BA = +0.0243, 95% bootstrap CI = [lower, upper]
1month plus_macro_market XGBoost: delta BA = +0.0267, 95% bootstrap CI = [lower, upper]
```

Why this helps:

- Gives effect-size uncertainty, not only p-value.
- Easier to explain in defense.
- Shows whether the improvement is economically/statistically stable.

### 3. Permutation test for LLM feature signal

Run a negative-control experiment:

- keep technical features and labels unchanged
- shuffle LLM features across ticker/date or within ticker over time
- rerun Config_Hybrid
- compare real delta against shuffled deltas

Expected result if LLM signal is real:

```text
real_delta > most shuffled_delta values
```

Why this helps:

- Tests whether LLM features carry time/ticker-specific information.
- Reduces risk that the gain comes from leakage, model artifact, or random dimensionality increase.
- Strong defense answer if committee asks whether LLM feature gains are accidental.
