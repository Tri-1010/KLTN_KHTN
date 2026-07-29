# VN30 material-event expansion runbook

## Goal

Evaluate whether LLM material-event semantic features improve VN30 direction prediction beyond technical indicators.

Main claim tested:

```text
delta = Config_Hybrid - Config_A
```

where:

- `Config_A`: technical indicators only.
- `Config_LLM`: LLM semantic features only.
- `Config_Hybrid`: technical indicators + LLM semantic features.

## Universe

Original VN30 only, 30 tickers:

```text
ACB BCM BID BVH CTG FPT GAS GVR HDB HPG
MBB MSN MWG PLX POW SAB SHB SSB SSI STB
TCB TPB VCB VHM VIB VIC VJC VNM VPB VRE
```

Do not mix HOSE80 expansion into primary VN30 claim.

## Input annotation file

```text
data/experiments/llm_semantic/focused_material_expanded_annotations_deepseek.csv
```

Current annotation status at time of this run:

- expanded candidates: 7,624
- DeepSeek OK annotations: 7,624
- missing: 0
- error: 0
- original VN30 OK annotations: about 2,967
- VN30 material-event annotations: about 291
- VN30 direct material annotations: about 279
- material/direct material coverage: 30/30 VN30 tickers

## Material-event definition

Material events used in primary variants:

```text
earnings
dividend
capital
debt_risk
legal_risk
```

These are events most defensible in finance: earnings, payout, financing/capital structure, debt risk, legal/regulatory risk.

## Variants

### `vn30_material`

Uses material events with non-irrelevant relevance:

```text
event_type in {earnings, dividend, capital, debt_risk, legal_risk}
relevance_to_ticker != irrelevant
```

Includes direct + indirect material information.

### `vn30_direct_material`

Uses only direct material events:

```text
event_type in {earnings, dividend, capital, debt_risk, legal_risk}
relevance_to_ticker == direct
```

This is cleaner for thesis defense.

### `vn30_material_lag1`

Same as `vn30_material`, but all `llm_*` features are shifted by one trading day per ticker.

Purpose: reduce same-day look-ahead risk.

### `vn30_direct_material_lag1`

Same as `vn30_direct_material`, but shifted by one trading day.

This is strictest variant: material + direct + lagged.

## Horizons

Run horizons in trading days:

```text
1,5,10,20,60
```

Interpretation:

- `1d`: next trading day
- `5d`: about 1 trading week
- `10d`: about 2 trading weeks
- `20d`: about 1 trading month
- `60d`: about 3 trading months

## Models

Use all ML models from `pipeline.task10_train.build_ml_models()`:

- Logistic Regression
- Random Forest
- XGBoost
- LightGBM

No model filter in final run.

## Checkpointing

Each small evaluation step writes two checkpoint files:

```text
data/experiments/llm_semantic/vn30_material_eval/checkpoints/results__<variant>__<scope>__<horizon>d.csv
data/experiments/llm_semantic/vn30_material_eval/checkpoints/predictions__<variant>__<scope>__<horizon>d.csv
```

Example:

```text
results__vn30_direct_material_lag1__ALL__60d.csv
predictions__vn30_direct_material_lag1__ALL__60d.csv
```

If run crashes, rerun same command without `--force`; completed checkpoint files are skipped.

Use `--force` only when intentionally recomputing everything.

## Parallelism

Script parallelizes by variant using `ProcessPoolExecutor`.

Default:

```text
--workers 4
```

Each worker uses single-threaded model internals where possible to avoid CPU oversubscription.

## Commands

### Static check

```powershell
python -m py_compile .\scripts\evaluate_vn30_material_expansion.py
```

### Smoke test

```powershell
python .\scripts\evaluate_vn30_material_expansion.py --horizons 1 --workers 1 --checkpoint-dir data/experiments/llm_semantic/vn30_material_eval/checkpoints_smoke --force
```

### Main pooled VN30 run

```powershell
python .\scripts\evaluate_vn30_material_expansion.py --horizons 1,5,10,20,60 --workers 4
```

This evaluates pooled VN30 only. This is recommended primary thesis result because it uses all 30 tickers and has much larger test sample than per-ticker fits.

### Optional per-ticker appendix run

```powershell
python .\scripts\evaluate_vn30_material_expansion.py --horizons 1,5,10,20,60 --workers 4 --run-per-ticker
```

Use as appendix/case study only. Per-ticker test samples are smaller and more volatile.

## Outputs

Final aggregated files:

```text
reports/llm_semantic_vn30_material_expansion_summary.md
reports/llm_semantic_vn30_material_expansion_results.csv
reports/llm_semantic_vn30_material_expansion_predictions.csv
reports/llm_semantic_vn30_material_expansion_stats.csv
reports/llm_semantic_vn30_material_expansion_counts.csv
```

Checkpoint files remain under:

```text
data/experiments/llm_semantic/vn30_material_eval/checkpoints/
```

## How to read results

Primary table: `Pooled original VN30 — best Hybrid vs Technical deltas`.

Important columns:

- `ba_a`: balanced accuracy of technical-only model.
- `ba_hybrid`: balanced accuracy of technical + LLM features.
- `delta_hybrid_minus_a`: improvement from LLM semantic features.
- `delta_ci_low`, `delta_ci_high`: bootstrap CI for delta.
- `p_mid`: mid-p McNemar-style paired prediction test.
- `b`: cases where Config_A correct and Config_Hybrid wrong.
- `c`: cases where Config_A wrong and Config_Hybrid correct.

Strongest thesis evidence if:

```text
delta_hybrid_minus_a > 0
and delta_ci_low > 0
and p_mid < 0.05
```

Most defensible positive variant:

```text
vn30_direct_material_lag1
```

because it is direct, material, and lagged.

## Thesis design note — ML + LLM research idea

Original thesis direction from user:

> Use Machine Learning to generate prediction signals from technical indicators, then use LLM-extracted news features as additional inputs to test whether they improve ML predictive probability/performance. LLM also supports investors by summarizing and structuring relevant news information.

This means the thesis should not present the LLM as a standalone stock predictor. The intended architecture is:

```text
Technical indicators ─┐
                      ├─> ML model ─> stock direction signal / probability
LLM news features ────┘
```

Main empirical question:

```text
Does adding LLM-derived news features improve the ML model compared with technical indicators alone?
```

Operational comparison:

```text
Config_A      = technical indicators only
Config_LLM    = LLM news features only, diagnostic
Config_Hybrid = technical indicators + LLM news features

Delta = Config_Hybrid - Config_A
```

## Three possible prediction designs

### 1. Period-level smoothed trend prediction

Sample unit:

```text
(ticker, period)
```

Example periods:

```text
1 week, 2 weeks, 1 month, 2 months, quarter
```

Label currently used in `pipeline/experiment_period.py`:

```text
label = 1 if avg_close(next_period) > avg_close(current_period)
label = 0 otherwise
```

Example:

```text
avg_close(HPG, April) > avg_close(HPG, March) => March label = 1
```

Strengths:

- aligns with existing ML part where technical indicators achieved better balanced accuracy (~0.67–0.76 in earlier reports);
- smoother label because it compares average prices, not one noisy closing price;
- easier to defend as a trend-prediction task;
- best way to integrate ML and LLM into one consistent framework.

Weaknesses / user concern:

- label is still simple up/down;
- any tiny increase counts as `up`, even if economically meaningless;
- should consider thresholded label or return-regression variant if thesis needs more economic meaning.

Possible stronger labels:

```text
label = 1 if return_next_period > +threshold
label = 0 if return_next_period <= +threshold
```

or three-class:

```text
up      if return_next_period > +2%
neutral if -2% <= return_next_period <= +2%
down    if return_next_period < -2%
```

For binary thesis setup, recommended improvement:

```text
label = 1 if next_period_return > 0.02
label = 0 otherwise
```

This avoids treating +0.01% as meaningful increase.

### 2. Daily point-horizon prediction

Sample unit:

```text
(ticker, trading_date)
```

Label used in current LLM material-event daily experiment:

```text
label_up_h = 1 if close(t+h) > close(t)
label_up_h = 0 otherwise
```

Examples:

```text
1d  = close after 1 trading day > close today
20d = close after 20 trading days > close today, about 1 month
60d = close after 60 trading days > close today, about 3 months
```

Important clarification:

- this is not only from event dates;
- dataset has every trading day for every ticker;
- if no event/news exists on a day, LLM features are zero or based on rolling past windows;
- model learns whether days with material-event signals improve future direction prediction.

Strengths:

- higher sample size;
- directly tests rolling 1d/5d/10d/20d/60d horizons;
- LLM material-event signals showed positive 60d results on VN30.

Weaknesses:

- technical-only baseline can look near random (~0.49–0.52 balanced accuracy) because task is noisier;
- not directly comparable with period-level ML results;
- uses point-to-point close prices, which are more volatile than period averages;
- should be presented as an LLM extension experiment, not as replacement for main ML benchmark.

### 3. Event-study / event-date prediction

Sample unit:

```text
(ticker, event_date)
```

Label:

```text
label_h = 1 if close(event_date + h) > close(event_date)
label_h = 0 otherwise
```

or better:

```text
abnormal_return_h = stock_return_h - market_return_h
```

This matches user intuition: start counting from the day an event article appears.

Strengths:

- directly asks whether a material news event is followed by price movement;
- easier to explain for investor-support use case;
- aligns with LLM role: identify relevant event, summarize it, and assess its possible importance.

Weaknesses:

- fewer samples because only event dates are included;
- may require market-adjusted returns/VNIndex benchmark for stronger finance interpretation;
- should be treated as event-study extension, not the main ML-period benchmark unless enough events exist.

## Recommended thesis framing

Decision as of current discussion:

```text
Main direction = period-level thresholded ML + LLM material-event hybrid
Support direction = daily rolling-horizon material-event result
Optional appendix = event-study from event dates
```

Why main direction is best:

- it matches the original thesis idea most directly: ML technical signals first, LLM news features added second;
- it keeps the stronger ML baseline from period-level experiments instead of relying on the noisier daily point-horizon baseline;
- it compares `Config_A_period` vs `Config_Hybrid_period` in the same framework, so the improvement is easier to defend;
- thresholded returns make the target more economically meaningful than simple `avg_close(next_period) > avg_close(current_period)`;
- investor-support role remains clear: LLM structures and explains news, while ML produces predictive signal/probability.

Planned main experiment:

```text
Sample unit: (ticker, period)
Periods: month, 2month, quarter
Label: next_period_return > 2%
Config_A: technical indicators only
Config_LLM: LLM material-event features only
Config_Hybrid: technical indicators + LLM material-event features
Models: Logistic Regression, Random Forest, XGBoost, LightGBM
Metric: balanced accuracy, AUC, F1
Split: time-series split, last 20% periods as test
```

LLM material features aggregated per period:

```text
llm_material_count
llm_direct_material_count
llm_earnings_count
llm_dividend_count
llm_capital_count
llm_debt_risk_count
llm_legal_risk_count
llm_positive_ratio
llm_negative_ratio
llm_importance_mean / max
llm_magnitude_mean / max
llm_uncertainty_mean
llm_novelty_mean
llm_confidence_mean
llm_direct_ratio
llm_material_count_lag1
llm_direct_material_count_lag1
```

Run target:

```text
reports/llm_semantic_period_material_hybrid_summary.md
reports/llm_semantic_period_material_hybrid_results.csv
reports/llm_semantic_period_material_hybrid_stats.csv
```

Use two linked components:

### Main ML component

Use period-level ML as the main predictive framework because this is where technical indicators are already strong and defensible.

Recommended next step:

```text
Add LLM material-event features into the same period-level framework.
```

That produces the cleanest thesis result:

```text
Config_A_period      = technical indicators only
Config_Hybrid_period = technical indicators + LLM material-event features
```

This directly answers the original thesis question: whether LLM features increase an already-working ML model.

### LLM component

Use LLM for two roles:

1. Feature creation for ML:
   - material event count;
   - direct material count;
   - sentiment;
   - importance score;
   - information magnitude / expected impact;
   - uncertainty;
   - novelty;
   - time horizon;
   - event type.

2. Investor support:
   - summarize relevant news;
   - explain why event is material;
   - identify whether event directly relates to ticker;
   - support interpretation, not issue buy/sell/hold recommendation.

## Current interpretation caution

Current daily LLM material-event result is useful but should be described carefully:

```text
In a daily rolling-horizon setup, LLM material-event features improve hybrid prediction at 60d for Random Forest on pooled VN30.
```

Do not write:

```text
LLM always improves stock prediction.
```

Better wording:

```text
LLM-derived material-event features provide incremental predictive information in selected medium-horizon settings, especially 60 trading days, while keyword-count features do not provide stable improvement.
```

## Most important unresolved design decision

The binary up/down label may be too simple because a tiny positive return is treated as success.

For stronger economic meaning, future runs should consider:

```text
next_return > 2%
```

or market-adjusted returns:

```text
stock_return_h - VNIndex_return_h > threshold
```

This would make the thesis claim more meaningful for investors, because it avoids treating noise-level gains as useful predictions.
