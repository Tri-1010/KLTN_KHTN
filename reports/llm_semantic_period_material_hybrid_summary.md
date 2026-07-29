# Period-level LLM material-event hybrid experiment

- universe: original VN30 (30 tickers)
- units: month, 2month, quarter
- threshold: next_period_return > 2.00%
- annotation_source: `data/experiments/llm_semantic/focused_material_expanded_annotations_deepseek.csv`
- Config_A: technical indicators only
- Config_LLM: period-aggregated LLM material-event features only
- Config_Hybrid: technical + LLM material-event features

## Hybrid vs Technical deltas

```text
   unit               model  n_test   ba_a  ba_hybrid  delta_hybrid_minus_a  b  c  n_discordant  p_mid
 2month Logistic_Regression     150 0.5290     0.5722                0.0432  5 11            16 0.1435
 2month            LightGBM     150 0.6990     0.7250                0.0260  3  6             9 0.3437
quarter             XGBoost      90 0.6853     0.6938                0.0085  2  3             5 0.6875
quarter            LightGBM      90 0.7048     0.7124                0.0077  3  3             6 0.6875
  month            LightGBM     330 0.6528     0.6599                0.0071 13 14            27 0.8506
  month             XGBoost     330 0.6206     0.6221                0.0016 14 14            28 0.8506
  month Logistic_Regression     330 0.6052     0.6052                0.0000  1  1             2 0.5000
 2month       Random_Forest     150 0.7162     0.7118               -0.0044  4  4             8 0.7266
quarter Logistic_Regression      90 0.6394     0.6318               -0.0077  1  1             2 0.5000
 2month             XGBoost     150 0.7206     0.7091               -0.0115  5  3             8 0.5078
  month       Random_Forest     330 0.6753     0.6616               -0.0138 11  6            17 0.2379
quarter       Random_Forest      90 0.7531     0.7124               -0.0407  8  5            13 0.4240
```

## Balanced accuracy table

```text
   unit               model  Config_A  Config_Hybrid  Config_LLM  delta_hybrid_minus_A
 2month Logistic_Regression    0.5290         0.5722      0.4502                0.0432
 2month            LightGBM    0.6990         0.7250      0.4198                0.0260
quarter             XGBoost    0.6853         0.6938      0.4954                0.0085
quarter            LightGBM    0.7048         0.7124      0.5599                0.0077
  month            LightGBM    0.6528         0.6599      0.4991                0.0071
  month             XGBoost    0.6206         0.6221      0.4866                0.0016
  month Logistic_Regression    0.6052         0.6052      0.4991                0.0000
 2month       Random_Forest    0.7162         0.7118      0.4674               -0.0044
quarter Logistic_Regression    0.6394         0.6318      0.5446               -0.0077
 2month             XGBoost    0.7206         0.7091      0.4833               -0.0115
  month       Random_Forest    0.6753         0.6616      0.4891               -0.0138
quarter       Random_Forest    0.7531         0.7124      0.5522               -0.0407
```

## Dataset coverage

```text
   unit  n_samples  n_periods  test_samples  positive_rate_test  llm_nonzero_rows  annotations
 2month        840         28           150              0.4200               208          288
  month       1680         56           330              0.3788               238          288
quarter        540         18            90              0.3444               175          288
```
