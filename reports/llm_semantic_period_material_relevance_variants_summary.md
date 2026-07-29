# Period-level LLM material-event hybrid experiment

- universe: original VN30 (30 tickers)
- units: 1week, 2week, month, 2month, quarter
- threshold: next_period_return > 2.00%
- annotation_source: `data/experiments/llm_semantic/focused_material_expanded_annotations_deepseek.csv`
- Config_A: technical indicators only
- Config_LLM: period-aggregated LLM material-event features only
- Config_Hybrid: technical + LLM material-event features

## Hybrid vs Technical deltas

```text
relevance_variant    unit               model  n_test   ba_a  ba_hybrid  delta_hybrid_minus_a   b  c  n_discordant  p_mid
    any_relevance  2month Logistic_Regression     150 0.5290     0.5722                0.0432   5 11            16 0.1435
  direct_indirect  2month Logistic_Regression     150 0.5290     0.5722                0.0432   5 11            16 0.1435
    indirect_only   month Logistic_Regression     330 0.6052     0.6343                0.0292  33 36            69 0.7202
    any_relevance  2month            LightGBM     150 0.6990     0.7250                0.0260   3  6             9 0.3437
  direct_indirect  2month            LightGBM     150 0.6990     0.7250                0.0260   3  6             9 0.3437
           direct   1week             XGBoost    1440 0.6673     0.6868                0.0195  72 96           168 0.0646
           direct   month             XGBoost     330 0.6206     0.6390                0.0184  13 18            31 0.3771
           direct   2week             XGBoost     720 0.6954     0.7121                0.0168  32 39            71 0.4096
    indirect_only   1week       Random_Forest    1440 0.6298     0.6460                0.0161  21 38            59 0.0273
           direct   2week            LightGBM     720 0.7067     0.7214                0.0147  16 27            43 0.0961
           direct  2month            LightGBM     150 0.6990     0.7126                0.0137   2  4             6 0.4531
  direct_indirect   2week            LightGBM     720 0.7067     0.7174                0.0107  14 21            35 0.2430
    any_relevance   2week            LightGBM     720 0.7067     0.7174                0.0107  14 21            35 0.2430
           direct   1week       Random_Forest    1440 0.6298     0.6389                0.0091  30 44            74 0.1053
    any_relevance quarter             XGBoost      90 0.6853     0.6938                0.0085   2  3             5 0.6875
  direct_indirect quarter             XGBoost      90 0.6853     0.6938                0.0085   2  3             5 0.6875
           direct quarter             XGBoost      90 0.6853     0.6938                0.0085   2  3             5 0.6875
    indirect_only  2month       Random_Forest     150 0.7162     0.7241                0.0079   4  5             9 0.7539
  direct_indirect quarter            LightGBM      90 0.7048     0.7124                0.0077   3  3             6 0.6875
           direct quarter            LightGBM      90 0.7048     0.7124                0.0077   3  3             6 0.6875
    any_relevance quarter            LightGBM      90 0.7048     0.7124                0.0077   3  3             6 0.6875
  direct_indirect   month            LightGBM     330 0.6528     0.6599                0.0071  13 14            27 0.8506
    any_relevance   month            LightGBM     330 0.6528     0.6599                0.0071  13 14            27 0.8506
           direct   month            LightGBM     330 0.6528     0.6599                0.0071  13 14            27 0.8506
           direct  2month Logistic_Regression     150 0.5290     0.5348                0.0057   1  2             3 0.6250
    any_relevance   1week       Random_Forest    1440 0.6298     0.6354                0.0056  28 38            66 0.2215
  direct_indirect   1week       Random_Forest    1440 0.6298     0.6354                0.0056  28 38            66 0.2215
           direct   1week Logistic_Regression    1440 0.6756     0.6783                0.0027   1  5             6 0.1250
    any_relevance   month             XGBoost     330 0.6206     0.6221                0.0016  14 14            28 0.8506
  direct_indirect   month             XGBoost     330 0.6206     0.6221                0.0016  14 14            28 0.8506
  direct_indirect   1week Logistic_Regression    1440 0.6756     0.6770                0.0014   2  5             7 0.2891
    any_relevance   1week Logistic_Regression    1440 0.6756     0.6770                0.0014   2  5             7 0.2891
           direct   2week Logistic_Regression     720 0.6976     0.6988                0.0012   1  1             2 0.5000
    any_relevance   2week Logistic_Regression     720 0.6976     0.6988                0.0012   1  1             2 0.5000
  direct_indirect   2week Logistic_Regression     720 0.6976     0.6988                0.0012   1  1             2 0.5000
    indirect_only   1week Logistic_Regression    1440 0.6756     0.6756                0.0000   0  0             0 1.0000
    indirect_only   1week             XGBoost    1440 0.6673     0.6673                0.0000   0  0             0 1.0000
    indirect_only  2month Logistic_Regression     150 0.5290     0.5290                0.0000   0  0             0 1.0000
    indirect_only  2month            LightGBM     150 0.6990     0.6990                0.0000   0  0             0 1.0000
  direct_indirect   month Logistic_Regression     330 0.6052     0.6052                0.0000   1  1             2 0.5000
    indirect_only quarter             XGBoost      90 0.6853     0.6853                0.0000   0  0             0 1.0000
           direct quarter Logistic_Regression      90 0.6394     0.6394                0.0000   0  0             0 1.0000
           direct   month Logistic_Regression     330 0.6052     0.6052                0.0000   1  1             2 0.5000
    indirect_only   1week            LightGBM    1440 0.6962     0.6962                0.0000   0  0             0 1.0000
    indirect_only   2week            LightGBM     720 0.7067     0.7067                0.0000   0  0             0 1.0000
    indirect_only quarter Logistic_Regression      90 0.6394     0.6394                0.0000   0  0             0 1.0000
    indirect_only   2week Logistic_Regression     720 0.6976     0.6976                0.0000   0  0             0 1.0000
    indirect_only   2week             XGBoost     720 0.6954     0.6954                0.0000   0  0             0 1.0000
    indirect_only   month            LightGBM     330 0.6528     0.6528                0.0000   0  0             0 1.0000
    indirect_only  2month             XGBoost     150 0.7206     0.7206                0.0000   0  0             0 1.0000
    indirect_only quarter            LightGBM      90 0.7048     0.7048                0.0000   0  0             0 1.0000
    any_relevance   month Logistic_Regression     330 0.6052     0.6052                0.0000   1  1             2 0.5000
    indirect_only   month             XGBoost     330 0.6206     0.6206                0.0000   0  0             0 1.0000
    any_relevance   2week       Random_Forest     720 0.6923     0.6907               -0.0016  28 24            52 0.5831
  direct_indirect   2week       Random_Forest     720 0.6923     0.6907               -0.0016  28 24            52 0.5831
           direct   2week       Random_Forest     720 0.6923     0.6891               -0.0032  24 22            46 0.7709
    any_relevance  2month       Random_Forest     150 0.7162     0.7118               -0.0044   4  4             8 0.7266
  direct_indirect  2month       Random_Forest     150 0.7162     0.7118               -0.0044   4  4             8 0.7266
    any_relevance quarter Logistic_Regression      90 0.6394     0.6318               -0.0077   1  1             2 0.5000
  direct_indirect quarter Logistic_Regression      90 0.6394     0.6318               -0.0077   1  1             2 0.5000
    any_relevance   1week            LightGBM    1440 0.6962     0.6876               -0.0086  69 51           120 0.1014
  direct_indirect   1week            LightGBM    1440 0.6962     0.6876               -0.0086  69 51           120 0.1014
  direct_indirect   2week             XGBoost     720 0.6954     0.6851               -0.0103  55 40            95 0.1253
    any_relevance   2week             XGBoost     720 0.6954     0.6851               -0.0103  55 40            95 0.1253
    indirect_only   month       Random_Forest     330 0.6753     0.6647               -0.0106  12  7            19 0.2632
           direct   1week            LightGBM    1440 0.6962     0.6852               -0.0110  61 48           109 0.2150
  direct_indirect  2month             XGBoost     150 0.7206     0.7091               -0.0115   5  3             8 0.5078
    any_relevance  2month             XGBoost     150 0.7206     0.7091               -0.0115   5  3             8 0.5078
  direct_indirect   1week             XGBoost    1440 0.6673     0.6552               -0.0121 104 92           196 0.3926
    any_relevance   1week             XGBoost    1440 0.6673     0.6552               -0.0121 104 92           196 0.3926
    any_relevance   month       Random_Forest     330 0.6753     0.6616               -0.0138  11  6            17 0.2379
  direct_indirect   month       Random_Forest     330 0.6753     0.6616               -0.0138  11  6            17 0.2379
           direct   month       Random_Forest     330 0.6753     0.6591               -0.0162  11  5            16 0.1435
    indirect_only   2week       Random_Forest     720 0.6923     0.6756               -0.0168  31 18            49 0.0649
           direct  2month       Random_Forest     150 0.7162     0.6981               -0.0181   5  3             8 0.5078
           direct  2month             XGBoost     150 0.7206     0.6875               -0.0331   8  3            11 0.1460
           direct quarter       Random_Forest      90 0.7531     0.7132               -0.0399   7  5            12 0.5811
    any_relevance quarter       Random_Forest      90 0.7531     0.7124               -0.0407   8  5            13 0.4240
  direct_indirect quarter       Random_Forest      90 0.7531     0.7124               -0.0407   8  5            13 0.4240
    indirect_only quarter       Random_Forest      90 0.7531     0.6946               -0.0585   8  2            10 0.0654
```

## Balanced accuracy table

```text
relevance_variant    unit               model  Config_A  Config_Hybrid  Config_LLM  delta_hybrid_minus_A
    any_relevance  2month Logistic_Regression    0.5290         0.5722      0.4423                0.0432
  direct_indirect  2month Logistic_Regression    0.5290         0.5722      0.4502                0.0432
    indirect_only   month Logistic_Regression    0.6052         0.6343      0.4894                0.0292
    any_relevance  2month            LightGBM    0.6990         0.7250      0.4119                0.0260
  direct_indirect  2month            LightGBM    0.6990         0.7250      0.4198                0.0260
           direct   1week             XGBoost    0.6673         0.6868      0.5101                0.0195
           direct   month             XGBoost    0.6206         0.6390      0.4900                0.0184
           direct   2week             XGBoost    0.6954         0.7121      0.4937                0.0168
    indirect_only   1week       Random_Forest    0.6298         0.6460      0.5015                0.0161
           direct   2week            LightGBM    0.7067         0.7214      0.4941                0.0147
           direct  2month            LightGBM    0.6990         0.7126      0.4242                0.0137
  direct_indirect   2week            LightGBM    0.7067         0.7174      0.5010                0.0107
    any_relevance   2week            LightGBM    0.7067         0.7174      0.4988                0.0107
           direct   1week       Random_Forest    0.6298         0.6389      0.5058                0.0091
    any_relevance quarter             XGBoost    0.6853         0.6938      0.4792                0.0085
  direct_indirect quarter             XGBoost    0.6853         0.6938      0.4954                0.0085
           direct quarter             XGBoost    0.6853         0.6938      0.4877                0.0085
    indirect_only  2month       Random_Forest    0.7162         0.7241      0.4718                0.0079
  direct_indirect quarter            LightGBM    0.7048         0.7124      0.5599                0.0077
           direct quarter            LightGBM    0.7048         0.7124      0.5200                0.0077
    any_relevance quarter            LightGBM    0.7048         0.7124      0.5437                0.0077
  direct_indirect   month            LightGBM    0.6528         0.6599      0.4991                0.0071
    any_relevance   month            LightGBM    0.6528         0.6599      0.4991                0.0071
           direct   month            LightGBM    0.6528         0.6599      0.5080                0.0071
           direct  2month Logistic_Regression    0.5290         0.5348      0.4740                0.0057
    any_relevance   1week       Random_Forest    0.6298         0.6354      0.5010                0.0056
  direct_indirect   1week       Random_Forest    0.6298         0.6354      0.5031                0.0056
           direct   1week Logistic_Regression    0.6756         0.6783      0.5052                0.0027
    any_relevance   month             XGBoost    0.6206         0.6221      0.4866                0.0016
  direct_indirect   month             XGBoost    0.6206         0.6221      0.4866                0.0016
  direct_indirect   1week Logistic_Regression    0.6756         0.6770      0.5033                0.0014
    any_relevance   1week Logistic_Regression    0.6756         0.6770      0.5030                0.0014
           direct   2week Logistic_Regression    0.6976         0.6988      0.5032                0.0012
    any_relevance   2week Logistic_Regression    0.6976         0.6988      0.5020                0.0012
  direct_indirect   2week Logistic_Regression    0.6976         0.6988      0.5032                0.0012
    indirect_only   1week Logistic_Regression    0.6756         0.6756      0.5015                0.0000
    indirect_only   1week             XGBoost    0.6673         0.6673      0.5000                0.0000
    indirect_only  2month Logistic_Regression    0.5290         0.5290      0.4655                0.0000
    indirect_only  2month            LightGBM    0.6990         0.6990      0.5000                0.0000
  direct_indirect   month Logistic_Regression    0.6052         0.6052      0.4991                0.0000
    indirect_only quarter             XGBoost    0.6853         0.6853      0.5000                0.0000
           direct quarter Logistic_Regression    0.6394         0.6394      0.5446                0.0000
           direct   month Logistic_Regression    0.6052         0.6052      0.5169                0.0000
    indirect_only   1week            LightGBM    0.6962         0.6962      0.5000                0.0000
    indirect_only   2week            LightGBM    0.7067         0.7067      0.5000                0.0000
    indirect_only quarter Logistic_Regression    0.6394         0.6394      0.4984                0.0000
    indirect_only   2week Logistic_Regression    0.6976         0.6976      0.4838                0.0000
    indirect_only   2week             XGBoost    0.6954         0.6954      0.5000                0.0000
    indirect_only   month            LightGBM    0.6528         0.6528      0.5000                0.0000
    indirect_only  2month             XGBoost    0.7206         0.7206      0.5000                0.0000
    indirect_only quarter            LightGBM    0.7048         0.7048      0.5000                0.0000
    any_relevance   month Logistic_Regression    0.6052         0.6052      0.4951                0.0000
    indirect_only   month             XGBoost    0.6206         0.6206      0.5000                0.0000
    any_relevance   2week       Random_Forest    0.6923         0.6907      0.4889               -0.0016
  direct_indirect   2week       Random_Forest    0.6923         0.6907      0.4889               -0.0016
           direct   2week       Random_Forest    0.6923         0.6891      0.4891               -0.0032
    any_relevance  2month       Random_Forest    0.7162         0.7118      0.4595               -0.0044
  direct_indirect  2month       Random_Forest    0.7162         0.7118      0.4674               -0.0044
    any_relevance quarter Logistic_Regression    0.6394         0.6318      0.5446               -0.0077
  direct_indirect quarter Logistic_Regression    0.6394         0.6318      0.5446               -0.0077
    any_relevance   1week            LightGBM    0.6962         0.6876      0.5012               -0.0086
  direct_indirect   1week            LightGBM    0.6962         0.6876      0.5033               -0.0086
  direct_indirect   2week             XGBoost    0.6954         0.6851      0.4937               -0.0103
    any_relevance   2week             XGBoost    0.6954         0.6851      0.4937               -0.0103
    indirect_only   month       Random_Forest    0.6753         0.6647      0.4938               -0.0106
           direct   1week            LightGBM    0.6962         0.6852      0.5056               -0.0110
  direct_indirect  2month             XGBoost    0.7206         0.7091      0.4833               -0.0115
    any_relevance  2month             XGBoost    0.7206         0.7091      0.4754               -0.0115
  direct_indirect   1week             XGBoost    0.6673         0.6552      0.5061               -0.0121
    any_relevance   1week             XGBoost    0.6673         0.6552      0.5036               -0.0121
    any_relevance   month       Random_Forest    0.6753         0.6616      0.4891               -0.0138
  direct_indirect   month       Random_Forest    0.6753         0.6616      0.4891               -0.0138
           direct   month       Random_Forest    0.6753         0.6591      0.4900               -0.0162
    indirect_only   2week       Random_Forest    0.6923         0.6756      0.5000               -0.0168
           direct  2month       Random_Forest    0.7162         0.6981      0.4811               -0.0181
           direct  2month             XGBoost    0.7206         0.6875      0.5085               -0.0331
           direct quarter       Random_Forest    0.7531         0.7132      0.5361               -0.0399
    any_relevance quarter       Random_Forest    0.7531         0.7124      0.5361               -0.0407
  direct_indirect quarter       Random_Forest    0.7531         0.7124      0.5522               -0.0407
    indirect_only quarter       Random_Forest    0.7531         0.6946      0.4822               -0.0585
```

## Dataset coverage

```text
relevance_variant    unit  n_samples  n_periods  test_samples  positive_rate_test  llm_nonzero_rows  annotations
    any_relevance   1week       7320        244          1440              0.2715               275          291
    any_relevance  2month        840         28           150              0.4200               209          291
    any_relevance   2week       3690        123           720              0.3125               268          291
    any_relevance   month       1680         56           330              0.3788               239          291
    any_relevance quarter        540         18            90              0.3444               175          291
           direct   1week       7320        244          1440              0.2715               263          279
           direct  2month        840         28           150              0.4200               205          279
           direct   2week       3690        123           720              0.3125               257          279
           direct   month       1680         56           330              0.3788               232          279
           direct quarter        540         18            90              0.3444               174          279
  direct_indirect   1week       7320        244          1440              0.2715               272          288
  direct_indirect  2month        840         28           150              0.4200               208          288
  direct_indirect   2week       3690        123           720              0.3125               266          288
  direct_indirect   month       1680         56           330              0.3788               238          288
  direct_indirect quarter        540         18            90              0.3444               175          288
    indirect_only   1week       7320        244          1440              0.2715                 9            9
    indirect_only  2month        840         28           150              0.4200                 8            9
    indirect_only   2week       3690        123           720              0.3125                 9            9
    indirect_only   month       1680         56           330              0.3788                 9            9
    indirect_only quarter        540         18            90              0.3444                 7            9
```
