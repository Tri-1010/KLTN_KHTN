# HOSE100 material event variant sweep

- cache: `data/experiments/llm_semantic/article_semantics_cache_hose100_extra.csv`
- universe: HOSE100_quality
- tested relevance: direct, direct_indirect, any_relevance
- units: 1week, 2week, month, 2month, quarter

## Annotation coverage

```text
                  variant relevance_variant  annotations  tickers
            core_material            direct          279       30
            core_material   direct_indirect          288       30
            core_material     any_relevance          291       30
            core_material     indirect_only            9        7
plus_operation_governance            direct         1367       91
plus_operation_governance   direct_indirect         1398       91
plus_operation_governance     any_relevance         1500       91
plus_operation_governance     indirect_only           31       13
        plus_macro_market            direct         1530       91
        plus_macro_market   direct_indirect         1569       91
        plus_macro_market     any_relevance         1705       91
        plus_macro_market     indirect_only           39       16
          all_event_types            direct         8956       91
          all_event_types   direct_indirect         9251       91
          all_event_types     any_relevance        12133       91
          all_event_types     indirect_only          295       54
```

## Best positive deltas

```text
            event_variant                                  universe relevance_variant    unit               model  n_test   ba_a  ba_hybrid  delta_hybrid_minus_a   b   c  n_discordant  p_mid
        plus_macro_market         HOSE100_quality_plus_macro_market     any_relevance  2month             XGBoost     488 0.6576     0.6961                0.0385  24  42            66 0.0271
plus_operation_governance HOSE100_quality_plus_operation_governance     any_relevance quarter Logistic_Regression     388 0.6047     0.6381                0.0334  44  61           105 0.0982
          all_event_types           HOSE100_quality_all_event_types            direct  2month             XGBoost     488 0.6576     0.6905                0.0330  34  41            75 0.4222
        plus_macro_market         HOSE100_quality_plus_macro_market   direct_indirect quarter       Random_Forest     388 0.6962     0.7277                0.0315  12  25            37 0.0336
          all_event_types           HOSE100_quality_all_event_types   direct_indirect  2month             XGBoost     488 0.6576     0.6885                0.0309  36  43            79 0.4340
          all_event_types           HOSE100_quality_all_event_types     any_relevance   month             XGBoost    1088 0.6674     0.6977                0.0302  88  99           187 0.4225
        plus_macro_market         HOSE100_quality_plus_macro_market            direct  2month             XGBoost     488 0.6576     0.6874                0.0298  27  39            66 0.1421
          all_event_types           HOSE100_quality_all_event_types     any_relevance  2month             XGBoost     488 0.6576     0.6870                0.0294  34  40            74 0.4887
plus_operation_governance HOSE100_quality_plus_operation_governance            direct  2month             XGBoost     488 0.6576     0.6858                0.0282  28  36            64 0.3211
          all_event_types           HOSE100_quality_all_event_types            direct  2month            LightGBM     488 0.6818     0.7100                0.0282  17  25            42 0.2221
          all_event_types           HOSE100_quality_all_event_types     any_relevance quarter             XGBoost     388 0.6953     0.7230                0.0276  18  23            41 0.4408
        plus_macro_market         HOSE100_quality_plus_macro_market     any_relevance   month             XGBoost    1088 0.6674     0.6941                0.0267  65  90           155 0.0450
            core_material             HOSE100_quality_core_material            direct   2week Logistic_Regression    2400 0.6807     0.7050                0.0243 112 185           297 0.0000
            core_material             HOSE100_quality_core_material     any_relevance   month             XGBoost    1088 0.6674     0.6916                0.0241  67  91           158 0.0567
            core_material             HOSE100_quality_core_material   direct_indirect  2month             XGBoost     488 0.6576     0.6816                0.0240  30  38            68 0.3356
plus_operation_governance HOSE100_quality_plus_operation_governance     any_relevance   month             XGBoost    1088 0.6674     0.6909                0.0235  65  85           150 0.1033
            core_material             HOSE100_quality_core_material     any_relevance   2week Logistic_Regression    2400 0.6807     0.7036                0.0230 114 184           298 0.0000
          all_event_types           HOSE100_quality_all_event_types   direct_indirect  2month       Random_Forest     488 0.6908     0.7132                0.0224  20  24            44 0.5515
plus_operation_governance HOSE100_quality_plus_operation_governance     any_relevance  2month             XGBoost     488 0.6576     0.6797                0.0221  23  34            57 0.1480
plus_operation_governance HOSE100_quality_plus_operation_governance   direct_indirect   month             XGBoost    1088 0.6674     0.6893                0.0219  68  87           155 0.1279
          all_event_types           HOSE100_quality_all_event_types   direct_indirect   month             XGBoost    1088 0.6674     0.6890                0.0215  96  95           191 0.9425
plus_operation_governance HOSE100_quality_plus_operation_governance     any_relevance   1week             XGBoost    4888 0.6735     0.6948                0.0213 323 392           715 0.0099
          all_event_types           HOSE100_quality_all_event_types            direct   1week             XGBoost    4888 0.6735     0.6946                0.0210 334 399           733 0.0164
          all_event_types           HOSE100_quality_all_event_types   direct_indirect   1week             XGBoost    4888 0.6735     0.6945                0.0210 329 384           713 0.0395
          all_event_types           HOSE100_quality_all_event_types     any_relevance  2month       Random_Forest     488 0.6908     0.7103                0.0195  21  23            44 0.7660
            core_material             HOSE100_quality_core_material     any_relevance  2month             XGBoost     488 0.6576     0.6768                0.0192  27  36            63 0.2604
          all_event_types           HOSE100_quality_all_event_types     any_relevance   1week             XGBoost    4888 0.6735     0.6921                0.0186 357 406           763 0.0762
          all_event_types           HOSE100_quality_all_event_types     any_relevance  2month            LightGBM     488 0.6818     0.7000                0.0182  22  26            48 0.5682
          all_event_types           HOSE100_quality_all_event_types   direct_indirect   month            LightGBM    1088 0.6826     0.7006                0.0180  80  63           143 0.1563
plus_operation_governance HOSE100_quality_plus_operation_governance   direct_indirect quarter Logistic_Regression     388 0.6047     0.6227                0.0180   8  15            23 0.1516
plus_operation_governance HOSE100_quality_plus_operation_governance     any_relevance   month            LightGBM    1088 0.6826     0.7002                0.0177  46  57           103 0.2807
          all_event_types           HOSE100_quality_all_event_types            direct   month       Random_Forest    1088 0.7028     0.7205                0.0177  54  53           107 0.9234
plus_operation_governance HOSE100_quality_plus_operation_governance            direct   month             XGBoost    1088 0.6674     0.6848                0.0174  60  78           138 0.1265
        plus_macro_market         HOSE100_quality_plus_macro_market   direct_indirect   1week             XGBoost    4888 0.6735     0.6909                0.0173 347 381           728 0.2079
            core_material             HOSE100_quality_core_material   direct_indirect quarter       Random_Forest     388 0.6962     0.7132                0.0170  13  18            31 0.3771
plus_operation_governance HOSE100_quality_plus_operation_governance            direct   month            LightGBM    1088 0.6826     0.6993                0.0167  41  52            93 0.2564
          all_event_types           HOSE100_quality_all_event_types   direct_indirect  2month            LightGBM     488 0.6818     0.6984                0.0166  26  26            52 0.8899
plus_operation_governance HOSE100_quality_plus_operation_governance     any_relevance  2month       Random_Forest     488 0.6908     0.7065                0.0157  10  18            28 0.1360
            core_material             HOSE100_quality_core_material            direct   1week             XGBoost    4888 0.6735     0.6888                0.0153 358 369           727 0.6835
        plus_macro_market         HOSE100_quality_plus_macro_market            direct quarter Logistic_Regression     388 0.6047     0.6199                0.0152   8  12            20 0.3833
        plus_macro_market         HOSE100_quality_plus_macro_market   direct_indirect   month             XGBoost    1088 0.6674     0.6826                0.0151  68  84           152 0.1957
            core_material             HOSE100_quality_core_material     any_relevance   1week             XGBoost    4888 0.6735     0.6881                0.0146 363 379           742 0.5572
            core_material             HOSE100_quality_core_material     any_relevance   month            LightGBM    1088 0.6826     0.6970                0.0145  49  49            98 0.9196
        plus_macro_market         HOSE100_quality_plus_macro_market   direct_indirect  2month             XGBoost     488 0.6576     0.6719                0.0143  29  36            65 0.3891
plus_operation_governance HOSE100_quality_plus_operation_governance            direct   1week Logistic_Regression    4888 0.6882     0.7018                0.0135 137 224           361 0.0000
            core_material             HOSE100_quality_core_material            direct   2week       Random_Forest    2400 0.6873     0.7007                0.0135  62  80           142 0.1320
plus_operation_governance HOSE100_quality_plus_operation_governance   direct_indirect  2month             XGBoost     488 0.6576     0.6706                0.0130  29  38            67 0.2750
          all_event_types           HOSE100_quality_all_event_types   direct_indirect quarter       Random_Forest     388 0.6962     0.7090                0.0129  31  22            53 0.2203
        plus_macro_market         HOSE100_quality_plus_macro_market     any_relevance  2month       Random_Forest     488 0.6908     0.7037                0.0128  15  21            36 0.3240
            core_material             HOSE100_quality_core_material     any_relevance   1week Logistic_Regression    4888 0.6882     0.7009                0.0127 144 229           373 0.0000
        plus_macro_market         HOSE100_quality_plus_macro_market            direct  2month            LightGBM     488 0.6818     0.6944                0.0126  15  18            33 0.6076
          all_event_types           HOSE100_quality_all_event_types   direct_indirect quarter Logistic_Regression     388 0.6047     0.6170                0.0123  18  16            34 0.7359
plus_operation_governance HOSE100_quality_plus_operation_governance   direct_indirect   month            LightGBM    1088 0.6826     0.6948                0.0122  50  60           110 0.3426
          all_event_types           HOSE100_quality_all_event_types            direct   month            LightGBM    1088 0.6826     0.6948                0.0122  79  62           141 0.1534
plus_operation_governance HOSE100_quality_plus_operation_governance            direct   1week             XGBoost    4888 0.6735     0.6854                0.0119 344 370           714 0.3309
        plus_macro_market         HOSE100_quality_plus_macro_market   direct_indirect   month            LightGBM    1088 0.6826     0.6945                0.0119  47  55           102 0.4307
        plus_macro_market         HOSE100_quality_plus_macro_market     any_relevance   month            LightGBM    1088 0.6826     0.6945                0.0119  47  55           102 0.4307
            core_material             HOSE100_quality_core_material   direct_indirect  2month            LightGBM     488 0.6818     0.6936                0.0118  18  19            37 0.8714
            core_material             HOSE100_quality_core_material            direct quarter Logistic_Regression     388 0.6047     0.6164                0.0117   2   7             9 0.1094
            core_material             HOSE100_quality_core_material            direct   month             XGBoost    1088 0.6674     0.6790                0.0116  61  70           131 0.4335
```

## Significant p_mid < 0.05

```text
            event_variant                                  universe relevance_variant    unit               model  n_test   ba_a  ba_hybrid  delta_hybrid_minus_a   b   c  n_discordant  p_mid
        plus_macro_market         HOSE100_quality_plus_macro_market     any_relevance  2month             XGBoost     488 0.6576     0.6961                0.0385  24  42            66 0.0271
        plus_macro_market         HOSE100_quality_plus_macro_market   direct_indirect quarter       Random_Forest     388 0.6962     0.7277                0.0315  12  25            37 0.0336
        plus_macro_market         HOSE100_quality_plus_macro_market     any_relevance   month             XGBoost    1088 0.6674     0.6941                0.0267  65  90           155 0.0450
            core_material             HOSE100_quality_core_material            direct   2week Logistic_Regression    2400 0.6807     0.7050                0.0243 112 185           297 0.0000
            core_material             HOSE100_quality_core_material     any_relevance   2week Logistic_Regression    2400 0.6807     0.7036                0.0230 114 184           298 0.0000
plus_operation_governance HOSE100_quality_plus_operation_governance     any_relevance   1week             XGBoost    4888 0.6735     0.6948                0.0213 323 392           715 0.0099
          all_event_types           HOSE100_quality_all_event_types            direct   1week             XGBoost    4888 0.6735     0.6946                0.0210 334 399           733 0.0164
          all_event_types           HOSE100_quality_all_event_types   direct_indirect   1week             XGBoost    4888 0.6735     0.6945                0.0210 329 384           713 0.0395
plus_operation_governance HOSE100_quality_plus_operation_governance            direct   1week Logistic_Regression    4888 0.6882     0.7018                0.0135 137 224           361 0.0000
            core_material             HOSE100_quality_core_material     any_relevance   1week Logistic_Regression    4888 0.6882     0.7009                0.0127 144 229           373 0.0000
plus_operation_governance HOSE100_quality_plus_operation_governance   direct_indirect  2month Logistic_Regression     488 0.6263     0.6318                0.0055  54  88           142 0.0043
        plus_macro_market         HOSE100_quality_plus_macro_market   direct_indirect   1week Logistic_Regression    4888 0.6882     0.6937                0.0055  73 135           208 0.0000
        plus_macro_market         HOSE100_quality_plus_macro_market     any_relevance   1week Logistic_Regression    4888 0.6882     0.6937                0.0055  75 137           212 0.0000
plus_operation_governance HOSE100_quality_plus_operation_governance   direct_indirect   1week Logistic_Regression    4888 0.6882     0.6933                0.0051  78 141           219 0.0000
        plus_macro_market         HOSE100_quality_plus_macro_market   direct_indirect   2week Logistic_Regression    2400 0.6807     0.6849                0.0042  47  87           134 0.0005
            core_material             HOSE100_quality_core_material   direct_indirect   1week            LightGBM    4888 0.7109     0.7149                0.0040 153 194           347 0.0278
        plus_macro_market         HOSE100_quality_plus_macro_market            direct   1week Logistic_Regression    4888 0.6882     0.6917                0.0035  95 172           267 0.0000
        plus_macro_market         HOSE100_quality_plus_macro_market   direct_indirect  2month Logistic_Regression     488 0.6263     0.6287                0.0024  56  95           151 0.0015
          all_event_types           HOSE100_quality_all_event_types   direct_indirect   1week Logistic_Regression    4888 0.6882     0.6906                0.0024  27  66            93 0.0000
          all_event_types           HOSE100_quality_all_event_types     any_relevance   1week Logistic_Regression    4888 0.6882     0.6899                0.0017  32  70           102 0.0002
          all_event_types           HOSE100_quality_all_event_types            direct   1week Logistic_Regression    4888 0.6882     0.6894                0.0011  26  52            78 0.0032
          all_event_types           HOSE100_quality_all_event_types     any_relevance quarter       Random_Forest     388 0.6962     0.6911               -0.0051  37  21            58 0.0363
          all_event_types           HOSE100_quality_all_event_types     any_relevance quarter Logistic_Regression     388 0.6047     0.5892               -0.0155  14   4            18 0.0192
          all_event_types           HOSE100_quality_all_event_types            direct quarter Logistic_Regression     388 0.6047     0.5872               -0.0175  28  11            39 0.0064
          all_event_types           HOSE100_quality_all_event_types   direct_indirect  2month Logistic_Regression     488 0.6263     0.6046               -0.0217  34  19            53 0.0402
            core_material             HOSE100_quality_core_material     any_relevance quarter            LightGBM     388 0.7009     0.6747               -0.0262  26  13            39 0.0385
            core_material             HOSE100_quality_core_material   direct_indirect   month Logistic_Regression    1088 0.7218     0.6919               -0.0299  78  48           126 0.0075
          all_event_types           HOSE100_quality_all_event_types            direct  2month Logistic_Regression     488 0.6263     0.5864               -0.0399  41  22            63 0.0169
            core_material             HOSE100_quality_core_material     any_relevance quarter             XGBoost     388 0.6953     0.6550               -0.0403  20   8            28 0.0241
          all_event_types           HOSE100_quality_all_event_types     any_relevance  2month Logistic_Regression     488 0.6263     0.5634               -0.0630  63  18            81 0.0000
          all_event_types           HOSE100_quality_all_event_types            direct   month Logistic_Regression    1088 0.7218     0.6584               -0.0634 152  76           228 0.0000
            core_material             HOSE100_quality_core_material            direct   month Logistic_Regression    1088 0.7218     0.6404               -0.0814 173  75           248 0.0000
            core_material             HOSE100_quality_core_material     any_relevance   month Logistic_Regression    1088 0.7218     0.6404               -0.0814 173  75           248 0.0000
        plus_macro_market         HOSE100_quality_plus_macro_market            direct   month Logistic_Regression    1088 0.7218     0.6398               -0.0820 173  74           247 0.0000
plus_operation_governance HOSE100_quality_plus_operation_governance     any_relevance   month Logistic_Regression    1088 0.7218     0.6398               -0.0820 173  74           247 0.0000
plus_operation_governance HOSE100_quality_plus_operation_governance            direct   month Logistic_Regression    1088 0.7218     0.6398               -0.0820 173  74           247 0.0000
        plus_macro_market         HOSE100_quality_plus_macro_market     any_relevance   month Logistic_Regression    1088 0.7218     0.6382               -0.0836 174  74           248 0.0000
        plus_macro_market         HOSE100_quality_plus_macro_market   direct_indirect   month Logistic_Regression    1088 0.7218     0.6333               -0.0885 195  74           269 0.0000
plus_operation_governance HOSE100_quality_plus_operation_governance   direct_indirect   month Logistic_Regression    1088 0.7218     0.6330               -0.0888 192  72           264 0.0000
          all_event_types           HOSE100_quality_all_event_types     any_relevance   month Logistic_Regression    1088 0.7218     0.6327               -0.0891 195  76           271 0.0000
          all_event_types           HOSE100_quality_all_event_types   direct_indirect   month Logistic_Regression    1088 0.7218     0.6127               -0.1091 211  64           275 0.0000
```

## Mean deltas by variant

```text
                             mean  median     max     min
event_variant                                            
all_event_types            0.0003  0.0036  0.0330 -0.1091
core_material             -0.0019  0.0001  0.0243 -0.0814
plus_macro_market          0.0005  0.0025  0.0385 -0.0885
plus_operation_governance -0.0012  0.0003  0.0334 -0.0888
```

## Mean deltas by variant/unit

```text
                                                  mean               median                  max                  min
                                  delta_hybrid_minus_a delta_hybrid_minus_a delta_hybrid_minus_a delta_hybrid_minus_a
event_variant             unit                                                                                       
all_event_types           1week                 0.0044               0.0020               0.0210              -0.0138
                          2month                0.0059               0.0189               0.0330              -0.0630
                          2week                 0.0011              -0.0001               0.0106              -0.0040
                          month                -0.0115               0.0108               0.0302              -0.1091
                          quarter               0.0016               0.0055               0.0276              -0.0175
core_material             1week                 0.0038               0.0031               0.0153              -0.0066
                          2month                0.0006              -0.0018               0.0240              -0.0218
                          2week                 0.0054               0.0042               0.0243              -0.0089
                          month                -0.0133              -0.0032               0.0241              -0.0814
                          quarter              -0.0060              -0.0035               0.0170              -0.0403
plus_macro_market         1week                 0.0034               0.0028               0.0173              -0.0057
                          2month                0.0092               0.0086               0.0385              -0.0097
                          2week                 0.0013               0.0008               0.0083              -0.0062
                          month                -0.0124               0.0092               0.0267              -0.0885
                          quarter               0.0009               0.0014               0.0315              -0.0305
plus_operation_governance 1week                 0.0041               0.0027               0.0213              -0.0092
                          2month                0.0048               0.0053               0.0282              -0.0281
                          2week                -0.0010              -0.0006               0.0085              -0.0083
                          month                -0.0120               0.0095               0.0235              -0.0888
                          quarter              -0.0023              -0.0054               0.0334              -0.0234
```
