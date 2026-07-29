# Period-level material hybrid — cache total universes

- annotation_source: `data/experiments/llm_semantic/article_semantics_cache.csv`
- universes: VN30, HOSE80/liquid universe
- units: 1week, 2week, month, 2month, quarter
- relevance_variants: direct, direct_indirect, any_relevance, indirect_only
- threshold: next_period_return > 2.00%

## Best deltas

```text
universe relevance_variant    unit               model  n_test   ba_a  ba_hybrid  delta_hybrid_minus_a   b   c  n_discordant  p_mid
    VN30     indirect_only  2month Logistic_Regression     150 0.5290     0.6437                0.1147  20  35            55 0.0440
  HOSE80     indirect_only quarter Logistic_Regression     240 0.6159     0.6916                0.0756  33  50            83 0.0630
    VN30   direct_indirect   month             XGBoost     330 0.6206     0.6714                0.0508  12  29            41 0.0079
  HOSE80     any_relevance   month Logistic_Regression     880 0.6291     0.6794                0.0504  56  94           150 0.0019
  HOSE80            direct quarter Logistic_Regression     240 0.6159     0.6453                0.0294   5  18            23 0.0066
    VN30     any_relevance  2month Logistic_Regression     150 0.5290     0.5564                0.0274   5   9            14 0.3018
  HOSE80   direct_indirect quarter Logistic_Regression     240 0.6159     0.6424                0.0264   5  17            22 0.0106
  HOSE80   direct_indirect   2week Logistic_Regression    1920 0.6857     0.7115                0.0258  95 145           240 0.0012
    VN30   direct_indirect  2month Logistic_Regression     150 0.5290     0.5506                0.0216   5   8            13 0.4240
  HOSE80     indirect_only  2month       Random_Forest     400 0.6834     0.7035                0.0201   5  15            20 0.0266
    VN30     any_relevance   2week       Random_Forest     720 0.6923     0.7105                0.0182  18  30            48 0.0854
    VN30   direct_indirect  2month            LightGBM     150 0.6990     0.7170                0.0181   4   6            10 0.5488
    VN30            direct  2month Logistic_Regression     150 0.5290     0.5449                0.0159   0   2             2 0.2500
    VN30     any_relevance   2week            LightGBM     720 0.7067     0.7222                0.0156  19  26            45 0.3020
  HOSE80     indirect_only quarter       Random_Forest     240 0.6509     0.6654                0.0145   9  11            20 0.6636
  HOSE80            direct   month             XGBoost     880 0.6687     0.6830                0.0143  51  62           113 0.3029
    VN30   direct_indirect   2week            LightGBM     720 0.7067     0.7208                0.0141  21  29            50 0.2624
  HOSE80     any_relevance   month             XGBoost     880 0.6687     0.6824                0.0137  48  62           110 0.1837
  HOSE80     any_relevance   2week             XGBoost    1920 0.6923     0.7060                0.0137 100 130           230 0.0482
  HOSE80   direct_indirect   2week             XGBoost    1920 0.6923     0.7058                0.0135  98 126           224 0.0617
    VN30   direct_indirect   1week             XGBoost    1440 0.6673     0.6806                0.0132  79  95           174 0.2264
    VN30     any_relevance  2month            LightGBM     150 0.6990     0.7113                0.0123   3   4             7 0.7266
  HOSE80            direct   2week             XGBoost    1920 0.6923     0.7041                0.0118  97 116           213 0.1939
  HOSE80            direct   month       Random_Forest     880 0.6844     0.6962                0.0118  29  38            67 0.2750
    VN30            direct   2week            LightGBM     720 0.7067     0.7184                0.0117  19  27            46 0.2430
    VN30            direct  2month            LightGBM     150 0.6990     0.7091                0.0101   4   5             9 0.7539
    VN30            direct   2week Logistic_Regression     720 0.6976     0.7071                0.0095  36  43            79 0.4340
  HOSE80     any_relevance  2month       Random_Forest     400 0.6834     0.6928                0.0093  14  18            32 0.4869
  HOSE80   direct_indirect   month             XGBoost     880 0.6687     0.6780                0.0093  50  58           108 0.4437
  HOSE80     any_relevance quarter Logistic_Regression     240 0.6159     0.6248                0.0089  31  37            68 0.4704
  HOSE80     indirect_only   2week       Random_Forest    1920 0.6959     0.7047                0.0088  46  54           100 0.4262
  HOSE80            direct   2week       Random_Forest    1920 0.6959     0.7042                0.0083  63  68           131 0.6636
  HOSE80   direct_indirect  2month       Random_Forest     400 0.6834     0.6916                0.0081  14  20            34 0.3105
  HOSE80   direct_indirect   month       Random_Forest     880 0.6844     0.6925                0.0081  30  32            62 0.8013
    VN30   direct_indirect  2month             XGBoost     150 0.7206     0.7285                0.0079   4   5             9 0.7539
  HOSE80   direct_indirect   1week             XGBoost    3920 0.6960     0.7036                0.0076 237 261           498 0.2826
  HOSE80     indirect_only   month       Random_Forest     880 0.6844     0.6919                0.0074  26  30            56 0.5966
    VN30            direct   1week       Random_Forest    1440 0.6298     0.6372                0.0073  29  36            65 0.3891
    VN30   direct_indirect   1week       Random_Forest    1440 0.6298     0.6370                0.0071  26  41            67 0.0681
    VN30            direct   1week             XGBoost    1440 0.6673     0.6736                0.0062  91  94           185 0.8260
    VN30            direct   1week Logistic_Regression    1440 0.6756     0.6812                0.0056   2  12            14 0.0074
  HOSE80            direct  2month       Random_Forest     400 0.6834     0.6889                0.0054  11  15            26 0.4421
    VN30     any_relevance   1week            LightGBM    1440 0.6962     0.7016                0.0054  51  59           110 0.4478
  HOSE80   direct_indirect   2week            LightGBM    1920 0.7251     0.7304                0.0054  63  63           126 0.9291
  HOSE80     any_relevance   2week Logistic_Regression    1920 0.6857     0.6907                0.0050  39  63           102 0.0176
    VN30     any_relevance   1week Logistic_Regression    1440 0.6756     0.6799                0.0043   3  12            15 0.0213
    VN30   direct_indirect   1week Logistic_Regression    1440 0.6756     0.6799                0.0043   4  13            17 0.0309
    VN30            direct   month             XGBoost     330 0.6206     0.6244                0.0038  17  16            33 0.8642
    VN30   direct_indirect   month       Random_Forest     330 0.6753     0.6784                0.0031   8   8            16 0.8036
  HOSE80     any_relevance quarter            LightGBM     240 0.6612     0.6640                0.0028   9   7            16 0.6291
    VN30     indirect_only   1week       Random_Forest    1440 0.6298     0.6324                0.0025  30  37            67 0.3961
  HOSE80     any_relevance   2week            LightGBM    1920 0.7251     0.7276                0.0025  49  50            99 0.9204
    VN30     any_relevance   2week             XGBoost     720 0.6954     0.6976                0.0022  40  35            75 0.5666
  HOSE80            direct   month            LightGBM     880 0.6822     0.6842                0.0019  38  43            81 0.5811
    VN30            direct   2week       Random_Forest     720 0.6923     0.6939                0.0016  24  22            46 0.7709
  HOSE80            direct quarter       Random_Forest     240 0.6509     0.6523                0.0014   8   7            15 0.8036
  HOSE80            direct   1week Logistic_Regression    3920 0.6814     0.6828                0.0014   1   9            10 0.0117
  HOSE80   direct_indirect   1week Logistic_Regression    3920 0.6814     0.6828                0.0014   1   9            10 0.0117
    VN30     any_relevance   1week       Random_Forest    1440 0.6298     0.6311                0.0013  26  32            58 0.4350
  HOSE80     any_relevance   1week Logistic_Regression    3920 0.6814     0.6826                0.0012   2   9            11 0.0386
  HOSE80   direct_indirect   month            LightGBM     880 0.6822     0.6832                0.0010  32  35            67 0.7163
    VN30     any_relevance   month             XGBoost     330 0.6206     0.6215                0.0009  17  18            35 0.8679
    VN30   direct_indirect   2week             XGBoost     720 0.6954     0.6956                0.0002  44  37            81 0.4397
    VN30     indirect_only   1week Logistic_Regression    1440 0.6756     0.6756                0.0000   0   0             0 1.0000
    VN30     indirect_only quarter Logistic_Regression      90 0.6394     0.6394                0.0000   0   0             0 1.0000
    VN30     indirect_only quarter            LightGBM      90 0.7048     0.7048                0.0000   0   0             0 1.0000
    VN30     indirect_only   month             XGBoost     330 0.6206     0.6206                0.0000   0   0             0 1.0000
    VN30     indirect_only   month Logistic_Regression     330 0.6052     0.6052                0.0000   0   0             0 1.0000
    VN30     indirect_only   month            LightGBM     330 0.6528     0.6528                0.0000   0   0             0 1.0000
    VN30     any_relevance  2month       Random_Forest     150 0.7162     0.7162                0.0000   5   5            10 0.7539
    VN30     indirect_only   2week             XGBoost     720 0.6954     0.6954                0.0000   0   0             0 1.0000
    VN30            direct quarter Logistic_Regression      90 0.6394     0.6394                0.0000   0   0             0 1.0000
    VN30     indirect_only   1week             XGBoost    1440 0.6673     0.6673                0.0000   0   0             0 1.0000
    VN30     indirect_only   2week Logistic_Regression     720 0.6976     0.6976                0.0000   0   0             0 1.0000
    VN30     any_relevance quarter Logistic_Regression      90 0.6394     0.6394                0.0000   0   0             0 1.0000
    VN30     indirect_only   2week            LightGBM     720 0.7067     0.7067                0.0000   0   0             0 1.0000
    VN30   direct_indirect quarter Logistic_Regression      90 0.6394     0.6394                0.0000   0   0             0 1.0000
    VN30     indirect_only  2month             XGBoost     150 0.7206     0.7206                0.0000   0   0             0 1.0000
    VN30     indirect_only   1week            LightGBM    1440 0.6962     0.6962                0.0000   0   0             0 1.0000
    VN30     indirect_only  2month            LightGBM     150 0.6990     0.6990                0.0000   0   0             0 1.0000
```

## Balanced accuracy

```text
universe relevance_variant    unit               model  Config_A  Config_Hybrid  Config_LLM  delta_hybrid_minus_A
    VN30     indirect_only  2month Logistic_Regression    0.5290         0.6437      0.4765                0.1147
  HOSE80     indirect_only quarter Logistic_Regression    0.6159         0.6916      0.4969                0.0756
    VN30   direct_indirect   month             XGBoost    0.6206         0.6714      0.4967                0.0508
  HOSE80     any_relevance   month Logistic_Regression    0.6291         0.6794      0.5064                0.0504
  HOSE80            direct quarter Logistic_Regression    0.6159         0.6453      0.4964                0.0294
    VN30     any_relevance  2month Logistic_Regression    0.5290         0.5564      0.4871                0.0274
  HOSE80   direct_indirect quarter Logistic_Regression    0.6159         0.6424      0.4797                0.0264
  HOSE80   direct_indirect   2week Logistic_Regression    0.6857         0.7115      0.5166                0.0258
    VN30   direct_indirect  2month Logistic_Regression    0.5290         0.5506      0.4951                0.0216
  HOSE80     indirect_only  2month       Random_Forest    0.6834         0.7035      0.4935                0.0201
    VN30     any_relevance   2week       Random_Forest    0.6923         0.7105      0.4879                0.0182
    VN30   direct_indirect  2month            LightGBM    0.6990         0.7170      0.5014                0.0181
    VN30            direct  2month Logistic_Regression    0.5290         0.5449      0.5088                0.0159
    VN30     any_relevance   2week            LightGBM    0.7067         0.7222      0.5081                0.0156
  HOSE80     indirect_only quarter       Random_Forest    0.6509         0.6654      0.4969                0.0145
  HOSE80            direct   month             XGBoost    0.6687         0.6830      0.4863                0.0143
    VN30   direct_indirect   2week            LightGBM    0.7067         0.7208      0.5010                0.0141
  HOSE80     any_relevance   month             XGBoost    0.6687         0.6824      0.4901                0.0137
  HOSE80     any_relevance   2week             XGBoost    0.6923         0.7060      0.5003                0.0137
  HOSE80   direct_indirect   2week             XGBoost    0.6923         0.7058      0.5049                0.0135
    VN30   direct_indirect   1week             XGBoost    0.6673         0.6806      0.5158                0.0132
    VN30     any_relevance  2month            LightGBM    0.6990         0.7113      0.5208                0.0123
  HOSE80            direct   2week             XGBoost    0.6923         0.7041      0.5034                0.0118
  HOSE80            direct   month       Random_Forest    0.6844         0.6962      0.4962                0.0118
    VN30            direct   2week            LightGBM    0.7067         0.7184      0.5026                0.0117
    VN30            direct  2month            LightGBM    0.6990         0.7091      0.4546                0.0101
    VN30            direct   2week Logistic_Regression    0.6976         0.7071      0.4929                0.0095
  HOSE80     any_relevance  2month       Random_Forest    0.6834         0.6928      0.5212                0.0093
  HOSE80   direct_indirect   month             XGBoost    0.6687         0.6780      0.4941                0.0093
  HOSE80     any_relevance quarter Logistic_Regression    0.6159         0.6248      0.4914                0.0089
  HOSE80     indirect_only   2week       Random_Forest    0.6959         0.7047      0.4963                0.0088
  HOSE80            direct   2week       Random_Forest    0.6959         0.7042      0.5089                0.0083
  HOSE80   direct_indirect  2month       Random_Forest    0.6834         0.6916      0.4950                0.0081
  HOSE80   direct_indirect   month       Random_Forest    0.6844         0.6925      0.5039                0.0081
    VN30   direct_indirect  2month             XGBoost    0.7206         0.7285      0.4869                0.0079
  HOSE80   direct_indirect   1week             XGBoost    0.6960         0.7036      0.5025                0.0076
  HOSE80     indirect_only   month       Random_Forest    0.6844         0.6919      0.5003                0.0074
    VN30            direct   1week       Random_Forest    0.6298         0.6372      0.5160                0.0073
    VN30   direct_indirect   1week       Random_Forest    0.6298         0.6370      0.5156                0.0071
    VN30            direct   1week             XGBoost    0.6673         0.6736      0.5161                0.0062
    VN30            direct   1week Logistic_Regression    0.6756         0.6812      0.5077                0.0056
  HOSE80            direct  2month       Random_Forest    0.6834         0.6889      0.5049                0.0054
    VN30     any_relevance   1week            LightGBM    0.6962         0.7016      0.5131                0.0054
  HOSE80   direct_indirect   2week            LightGBM    0.7251         0.7304      0.5033                0.0054
  HOSE80     any_relevance   2week Logistic_Regression    0.6857         0.6907      0.5128                0.0050
    VN30     any_relevance   1week Logistic_Regression    0.6756         0.6799      0.5089                0.0043
    VN30   direct_indirect   1week Logistic_Regression    0.6756         0.6799      0.5083                0.0043
    VN30            direct   month             XGBoost    0.6206         0.6244      0.4909                0.0038
    VN30   direct_indirect   month       Random_Forest    0.6753         0.6784      0.4796                0.0031
  HOSE80     any_relevance quarter            LightGBM    0.6612         0.6640      0.4476                0.0028
    VN30     indirect_only   1week       Random_Forest    0.6298         0.6324      0.5000                0.0025
  HOSE80     any_relevance   2week            LightGBM    0.7251         0.7276      0.5147                0.0025
    VN30     any_relevance   2week             XGBoost    0.6954         0.6976      0.5057                0.0022
  HOSE80            direct   month            LightGBM    0.6822         0.6842      0.4963                0.0019
    VN30            direct   2week       Random_Forest    0.6923         0.6939      0.4966                0.0016
  HOSE80            direct quarter       Random_Forest    0.6509         0.6523      0.4744                0.0014
  HOSE80            direct   1week Logistic_Regression    0.6814         0.6828      0.4989                0.0014
  HOSE80   direct_indirect   1week Logistic_Regression    0.6814         0.6828      0.4972                0.0014
    VN30     any_relevance   1week       Random_Forest    0.6298         0.6311      0.5135                0.0013
  HOSE80     any_relevance   1week Logistic_Regression    0.6814         0.6826      0.5007                0.0012
  HOSE80   direct_indirect   month            LightGBM    0.6822         0.6832      0.5018                0.0010
    VN30     any_relevance   month             XGBoost    0.6206         0.6215      0.5083                0.0009
    VN30   direct_indirect   2week             XGBoost    0.6954         0.6956      0.4947                0.0002
    VN30     indirect_only   1week Logistic_Regression    0.6756         0.6756      0.5007                0.0000
    VN30     indirect_only quarter Logistic_Regression    0.6394         0.6394      0.4721                0.0000
    VN30     indirect_only quarter            LightGBM    0.7048         0.7048      0.5000                0.0000
    VN30     indirect_only   month             XGBoost    0.6206         0.6206      0.4940                0.0000
    VN30     indirect_only   month Logistic_Regression    0.6052         0.6052      0.4940                0.0000
    VN30     indirect_only   month            LightGBM    0.6528         0.6528      0.5000                0.0000
    VN30     any_relevance  2month       Random_Forest    0.7162         0.7162      0.4896                0.0000
    VN30     indirect_only   2week             XGBoost    0.6954         0.6954      0.4905                0.0000
    VN30            direct quarter Logistic_Regression    0.6394         0.6394      0.5437                0.0000
    VN30     indirect_only   1week             XGBoost    0.6673         0.6673      0.4990                0.0000
    VN30     indirect_only   2week Logistic_Regression    0.6976         0.6976      0.4905                0.0000
    VN30     any_relevance quarter Logistic_Regression    0.6394         0.6394      0.5115                0.0000
    VN30     indirect_only   2week            LightGBM    0.7067         0.7067      0.5000                0.0000
    VN30   direct_indirect quarter Logistic_Regression    0.6394         0.6394      0.5224                0.0000
    VN30     indirect_only  2month             XGBoost    0.7206         0.7206      0.4844                0.0000
    VN30     indirect_only   1week            LightGBM    0.6962         0.6962      0.5000                0.0000
    VN30     indirect_only  2month            LightGBM    0.6990         0.6990      0.5000                0.0000
    VN30     indirect_only quarter             XGBoost    0.6853         0.6853      0.4636                0.0000
  HOSE80     indirect_only quarter             XGBoost    0.6496         0.6496      0.4969                0.0000
  HOSE80     indirect_only   2week Logistic_Regression    0.6857         0.6857      0.4954                0.0000
  HOSE80     indirect_only   1week Logistic_Regression    0.6814         0.6814      0.5000                0.0000
  HOSE80     indirect_only   1week            LightGBM    0.7131         0.7131      0.5000                0.0000
  HOSE80     indirect_only  2month             XGBoost    0.7045         0.7045      0.4882                0.0000
  HOSE80     indirect_only quarter            LightGBM    0.6612         0.6612      0.5000                0.0000
  HOSE80     indirect_only  2month            LightGBM    0.6966         0.6966      0.5000                0.0000
  HOSE80     indirect_only   2week            LightGBM    0.7251         0.7251      0.5000                0.0000
  HOSE80     indirect_only   2week             XGBoost    0.6923         0.6923      0.4972                0.0000
  HOSE80     indirect_only   month            LightGBM    0.6822         0.6822      0.5000                0.0000
  HOSE80     indirect_only   month Logistic_Regression    0.6291         0.6291      0.4961                0.0000
  HOSE80     indirect_only   month             XGBoost    0.6687         0.6687      0.5014                0.0000
  HOSE80     indirect_only   1week             XGBoost    0.6960         0.6960      0.4993                0.0000
  HOSE80            direct   1week       Random_Forest    0.6515         0.6515      0.5015               -0.0000
  HOSE80            direct   2week Logistic_Regression    0.6857         0.6855      0.5174               -0.0002
  HOSE80   direct_indirect   1week            LightGBM    0.7131         0.7127      0.4993               -0.0004
    VN30            direct quarter            LightGBM    0.7048         0.7039      0.4470               -0.0008
  HOSE80     any_relevance   1week             XGBoost    0.6960         0.6951      0.4971               -0.0009
    VN30   direct_indirect   2week Logistic_Regression    0.6976         0.6966      0.4956               -0.0010
```

## Coverage

```text
universe relevance_variant    unit  n_samples  n_periods  test_samples  positive_rate_test  llm_nonzero_rows  annotations
  HOSE80     any_relevance   1week      19521        246          3920              0.2612              1071         1191
  HOSE80     any_relevance  2month       2240         28           400              0.3775               722         1191
  HOSE80     any_relevance   2week       9844        124          1920              0.2880              1011         1191
  HOSE80     any_relevance   month       4481         57           880              0.3420               865         1191
  HOSE80     any_relevance quarter       1441         19           240              0.2875               614         1191
  HOSE80            direct   1week      19521        246          3920              0.2612               994         1090
  HOSE80            direct  2month       2240         28           400              0.3775               701         1090
  HOSE80            direct   2week       9844        124          1920              0.2880               949         1090
  HOSE80            direct   month       4481         57           880              0.3420               830         1090
  HOSE80            direct quarter       1441         19           240              0.2875               599         1090
  HOSE80   direct_indirect   1week      19521        246          3920              0.2612              1015         1112
  HOSE80   direct_indirect  2month       2240         28           400              0.3775               706         1112
  HOSE80   direct_indirect   2week       9844        124          1920              0.2880               966         1112
  HOSE80   direct_indirect   month       4481         57           880              0.3420               841         1112
  HOSE80   direct_indirect quarter       1441         19           240              0.2875               602         1112
  HOSE80     indirect_only   1week      19521        246          3920              0.2612                22           22
  HOSE80     indirect_only  2month       2240         28           400              0.3775                16           22
  HOSE80     indirect_only   2week       9844        124          1920              0.2880                21           22
  HOSE80     indirect_only   month       4481         57           880              0.3420                20           22
  HOSE80     indirect_only quarter       1441         19           240              0.2875                14           22
    VN30     any_relevance   1week       7320        244          1440              0.2715               420          488
    VN30     any_relevance  2month        840         28           150              0.4200               260          488
    VN30     any_relevance   2week       3690        123           720              0.3125               387          488
    VN30     any_relevance   month       1680         56           330              0.3788               320          488
    VN30     any_relevance quarter        540         18            90              0.3444               211          488
    VN30            direct   1week       7320        244          1440              0.2715               361          405
    VN30            direct  2month        840         28           150              0.4200               249          405
    VN30            direct   2week       3690        123           720              0.3125               342          405
    VN30            direct   month       1680         56           330              0.3788               298          405
    VN30            direct quarter        540         18            90              0.3444               204          405
    VN30   direct_indirect   1week       7320        244          1440              0.2715               381          426
    VN30   direct_indirect  2month        840         28           150              0.4200               253          426
    VN30   direct_indirect   2week       3690        123           720              0.3125               358          426
    VN30   direct_indirect   month       1680         56           330              0.3788               308          426
    VN30   direct_indirect quarter        540         18            90              0.3444               206          426
    VN30     indirect_only   1week       7320        244          1440              0.2715                21           21
    VN30     indirect_only  2month        840         28           150              0.4200                15           21
    VN30     indirect_only   2week       3690        123           720              0.3125                20           21
    VN30     indirect_only   month       1680         56           330              0.3788                19           21
    VN30     indirect_only quarter        540         18            90              0.3444                13           21
```
