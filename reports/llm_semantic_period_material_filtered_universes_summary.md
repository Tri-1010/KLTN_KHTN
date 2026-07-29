# Period-level material hybrid — cache total universes

- annotation_source: `data/experiments/llm_semantic/article_semantics_cache.csv`
- universes: VN30, HOSE80/liquid universe
- units: 1week, 2week, month, 2month, quarter
- relevance_variants: direct, direct_indirect, any_relevance, indirect_only
- threshold: next_period_return > 2.00%

## Best deltas

```text
       universe relevance_variant    unit               model  n_test   ba_a  ba_hybrid  delta_hybrid_minus_a   b   c  n_discordant  p_mid
liquid100_mat10     any_relevance  2month             XGBoost     140 0.5714     0.6602                0.0888   3  15            18 0.0044
 liquid200_mat5   direct_indirect quarter            LightGBM      78 0.7019     0.7596                0.0577   3   6             9 0.3437
  liquid50_mat5     any_relevance   month Logistic_Regression     616 0.6125     0.6680                0.0554  40  67           107 0.0091
liquid100_mat10     any_relevance quarter             XGBoost      84 0.5952     0.6429                0.0476   5   9            14 0.3018
liquid100_mat10   direct_indirect  2month             XGBoost     140 0.5714     0.6186                0.0471   6  12            18 0.1671
liquid100_mat10            direct  2month             XGBoost     140 0.5714     0.6065                0.0351   6  10            16 0.3323
liquid100_mat10            direct  2month       Random_Forest     140 0.6575     0.6926                0.0351   3   7            10 0.2266
liquid100_mat10   direct_indirect   month             XGBoost     308 0.6724     0.7056                0.0331   8  17            25 0.0755
 liquid200_mat5            direct  2month Logistic_Regression     130 0.5481     0.5794                0.0312   3   6             9 0.3437
 liquid100_mat5            direct quarter            LightGBM     126 0.6758     0.7060                0.0302   2   6             8 0.1797
 liquid100_mat5     any_relevance  2month       Random_Forest     210 0.6798     0.7091                0.0293   2   8            10 0.0654
 liquid200_mat5   direct_indirect quarter       Random_Forest      78 0.6731     0.7019                0.0288   4   6            10 0.5488
  liquid50_mat5            direct quarter             XGBoost     168 0.6411     0.6699                0.0288   6  10            16 0.3323
 liquid200_mat5   direct_indirect  2month            LightGBM     130 0.7227     0.7510                0.0283   1   4             5 0.2188
 liquid200_mat5     any_relevance   month            LightGBM     286 0.6434     0.6713                0.0279  16  20            36 0.5114
 liquid200_mat5     any_relevance  2month Logistic_Regression     130 0.5481     0.5758                0.0277   4   6            10 0.5488
  liquid50_mat5            direct quarter Logistic_Regression     168 0.6435     0.6705                0.0270   1   6             7 0.0703
 liquid100_mat5   direct_indirect   2week             XGBoost    1008 0.6700     0.6964                0.0264  56  67           123 0.3232
 liquid100_mat5   direct_indirect  2month       Random_Forest     210 0.6798     0.7059                0.0262   3   9            12 0.0923
 liquid200_mat5            direct   1week             XGBoost    1248 0.6774     0.7031                0.0258  57  71           128 0.2176
  liquid50_mat5   direct_indirect quarter             XGBoost     168 0.6411     0.6657                0.0246   6   9            15 0.4545
liquid100_mat10            direct   month       Random_Forest     308 0.7149     0.7388                0.0239   5  12            17 0.0963
liquid100_mat10     any_relevance   2week             XGBoost     672 0.6482     0.6695                0.0214  31  40            71 0.2888
  liquid50_mat5            direct   2week            LightGBM    1344 0.6834     0.7046                0.0212  59  77           136 0.1238
  liquid50_mat5   direct_indirect quarter Logistic_Regression     168 0.6435     0.6645                0.0210   3   8            11 0.1460
liquid100_mat10     any_relevance  2month       Random_Forest     140 0.6575     0.6783                0.0208   3   6             9 0.3437
 liquid200_mat5            direct   2week            LightGBM     624 0.6923     0.7127                0.0204  16  25            41 0.1641
  liquid50_mat5   direct_indirect   2week            LightGBM    1344 0.6834     0.7035                0.0201  44  64           108 0.0549
 liquid200_mat5            direct  2month       Random_Forest     130 0.6691     0.6886                0.0195   3   6             9 0.3437
 liquid200_mat5            direct quarter            LightGBM      78 0.7019     0.7212                0.0192   5   5            10 0.7539
 liquid200_mat5     any_relevance quarter            LightGBM      78 0.7019     0.7212                0.0192   5   5            10 0.7539
 liquid200_mat5     any_relevance quarter Logistic_Regression      78 0.5865     0.6058                0.0192   0   1             1 0.5000
liquid100_mat10     any_relevance   2week       Random_Forest     672 0.6556     0.6742                0.0186  18  30            48 0.0854
 liquid100_mat5     any_relevance   month            LightGBM     462 0.6651     0.6836                0.0184  22  29            51 0.3317
 liquid200_mat5            direct   2week       Random_Forest     624 0.6673     0.6854                0.0180  13  20            33 0.2295
  liquid50_mat5   direct_indirect   1week Logistic_Regression    2744 0.6846     0.7018                0.0173  78 132           210 0.0002
liquid100_mat10   direct_indirect   2week       Random_Forest     672 0.6556     0.6723                0.0167  19  32            51 0.0704
 liquid100_mat5   direct_indirect  2month             XGBoost     210 0.6665     0.6829                0.0164   4   8            12 0.2668
 liquid100_mat5            direct  2month       Random_Forest     210 0.6798     0.6962                0.0164   4   8            12 0.2668
 liquid100_mat5     any_relevance   month       Random_Forest     462 0.6977     0.7137                0.0160  12  16            28 0.4583
 liquid200_mat5     any_relevance  2month             XGBoost     130 0.7351     0.7510                0.0159   3   5             8 0.5078
liquid100_mat10   direct_indirect quarter Logistic_Regression      84 0.5873     0.6032                0.0159   0   2             2 0.2500
 liquid100_mat5     any_relevance   2week       Random_Forest    1008 0.6734     0.6893                0.0158  31  35            66 0.6254
 liquid100_mat5            direct   2week       Random_Forest    1008 0.6734     0.6890                0.0156  32  37            69 0.5504
 liquid100_mat5   direct_indirect   month             XGBoost     462 0.6694     0.6847                0.0152  19  28            47 0.1934
liquid100_mat10            direct   2week             XGBoost     672 0.6482     0.6632                0.0150  37  47            84 0.2780
liquid100_mat10            direct   2week       Random_Forest     672 0.6556     0.6702                0.0145  21  32            53 0.1337
 liquid100_mat5            direct   month       Random_Forest     462 0.6977     0.7111                0.0134   9  13            22 0.4049
  liquid50_mat5   direct_indirect   month             XGBoost     616 0.6572     0.6700                0.0128  37  42            79 0.5764
  liquid50_mat5     any_relevance quarter             XGBoost     168 0.6411     0.6537                0.0126   3   6             9 0.3437
liquid100_mat10   direct_indirect  2month       Random_Forest     140 0.6575     0.6695                0.0120   2   4             6 0.4531
  liquid50_mat5            direct  2month             XGBoost     280 0.6864     0.6979                0.0115   8   9            17 0.8145
 liquid100_mat5            direct quarter Logistic_Regression     126 0.6023     0.6136                0.0114   0   2             2 0.2500
 liquid100_mat5   direct_indirect quarter Logistic_Regression     126 0.6023     0.6136                0.0114   0   2             2 0.2500
 liquid100_mat5     any_relevance   2week            LightGBM    1008 0.6812     0.6924                0.0113  32  40            72 0.3492
 liquid200_mat5     any_relevance   2week            LightGBM     624 0.6923     0.7026                0.0102  16  26            42 0.1263
  liquid50_mat5     any_relevance  2month             XGBoost     280 0.6864     0.6962                0.0098   9  10            19 0.8238
liquid100_mat10   direct_indirect   month       Random_Forest     308 0.7149     0.7245                0.0096   5   8            13 0.4240
 liquid200_mat5   direct_indirect  2month Logistic_Regression     130 0.5481     0.5576                0.0094   0   1             1 0.5000
 liquid200_mat5   direct_indirect   2week       Random_Forest     624 0.6673     0.6767                0.0094  16  18            34 0.7359
 liquid200_mat5     any_relevance   1week       Random_Forest    1248 0.6518     0.6609                0.0091  22  32            54 0.1770
 liquid100_mat5     any_relevance   1week             XGBoost    2016 0.6756     0.6846                0.0089 126 129           255 0.8513
liquid100_mat10            direct   month             XGBoost     308 0.6724     0.6813                0.0089  13  14            27 0.8506
  liquid50_mat5   direct_indirect quarter            LightGBM     168 0.6555     0.6639                0.0084   6   8            14 0.6072
 liquid200_mat5   direct_indirect   2week            LightGBM     624 0.6923     0.7005                0.0081  20  27            47 0.3123
  liquid50_mat5   direct_indirect  2month             XGBoost     280 0.6864     0.6944                0.0081   7   8            15 0.8036
liquid100_mat10            direct quarter             XGBoost      84 0.5952     0.6032                0.0079   2   1             3 0.6250
 liquid200_mat5     any_relevance   2week       Random_Forest     624 0.6673     0.6748                0.0075  17  21            38 0.5224
 liquid100_mat5     any_relevance quarter Logistic_Regression     126 0.6023     0.6097                0.0075   1   1             2 0.5000
 liquid200_mat5            direct   1week            LightGBM    1248 0.6970     0.7042                0.0072  35  48            83 0.1557
 liquid100_mat5     any_relevance   1week       Random_Forest    2016 0.6359     0.6427                0.0068  52  62           114 0.3511
 liquid100_mat5   direct_indirect   2week            LightGBM    1008 0.6812     0.6879                0.0067  40  39            79 0.9111
  liquid50_mat5     any_relevance   2week            LightGBM    1344 0.6834     0.6901                0.0067  52  55           107 0.7730
 liquid100_mat5            direct  2month             XGBoost     210 0.6665     0.6732                0.0066   4   6            10 0.5488
liquid100_mat10   direct_indirect   1week Logistic_Regression    1344 0.6757     0.6823                0.0065  21  34            55 0.0814
 liquid200_mat5   direct_indirect  2month       Random_Forest     130 0.6691     0.6756                0.0065   4   5             9 0.7539
 liquid200_mat5   direct_indirect   1week Logistic_Regression    1248 0.6701     0.6762                0.0061  16  32            48 0.0213
 liquid200_mat5     any_relevance   1week             XGBoost    1248 0.6774     0.6834                0.0061  68  66           134 0.8634
 liquid200_mat5     any_relevance   month       Random_Forest     286 0.6686     0.6744                0.0058  10   9            19 0.8238
 liquid200_mat5   direct_indirect   month       Random_Forest     286 0.6686     0.6744                0.0058  10   9            19 0.8238
```

## Balanced accuracy

```text
       universe relevance_variant    unit               model  Config_A  Config_Hybrid  Config_LLM  delta_hybrid_minus_A
liquid100_mat10     any_relevance  2month             XGBoost    0.5714         0.6602      0.4735                0.0888
 liquid200_mat5   direct_indirect quarter            LightGBM    0.7019         0.7596      0.4904                0.0577
  liquid50_mat5     any_relevance   month Logistic_Regression    0.6125         0.6680      0.5008                0.0554
liquid100_mat10     any_relevance quarter             XGBoost    0.5952         0.6429      0.3571                0.0476
liquid100_mat10   direct_indirect  2month             XGBoost    0.5714         0.6186      0.4915                0.0471
liquid100_mat10            direct  2month             XGBoost    0.5714         0.6065      0.4674                0.0351
liquid100_mat10            direct  2month       Random_Forest    0.6575         0.6926      0.5337                0.0351
liquid100_mat10   direct_indirect   month             XGBoost    0.6724         0.7056      0.5053                0.0331
 liquid200_mat5            direct  2month Logistic_Regression    0.5481         0.5794      0.5387                0.0312
 liquid100_mat5            direct quarter            LightGBM    0.6758         0.7060      0.4755                0.0302
 liquid100_mat5     any_relevance  2month       Random_Forest    0.6798         0.7091      0.5193                0.0293
 liquid200_mat5   direct_indirect quarter       Random_Forest    0.6731         0.7019      0.4712                0.0288
  liquid50_mat5            direct quarter             XGBoost    0.6411         0.6699      0.4970                0.0288
 liquid200_mat5   direct_indirect  2month            LightGBM    0.7227         0.7510      0.5403                0.0283
 liquid200_mat5     any_relevance   month            LightGBM    0.6434         0.6713      0.4832                0.0279
 liquid200_mat5     any_relevance  2month Logistic_Regression    0.5481         0.5758      0.5127                0.0277
  liquid50_mat5            direct quarter Logistic_Regression    0.6435         0.6705      0.5696                0.0270
 liquid100_mat5   direct_indirect   2week             XGBoost    0.6700         0.6964      0.5142                0.0264
 liquid100_mat5   direct_indirect  2month       Random_Forest    0.6798         0.7059      0.5054                0.0262
 liquid200_mat5            direct   1week             XGBoost    0.6774         0.7031      0.5053                0.0258
  liquid50_mat5   direct_indirect quarter             XGBoost    0.6411         0.6657      0.4886                0.0246
liquid100_mat10            direct   month       Random_Forest    0.7149         0.7388      0.5178                0.0239
liquid100_mat10     any_relevance   2week             XGBoost    0.6482         0.6695      0.5011                0.0214
  liquid50_mat5            direct   2week            LightGBM    0.6834         0.7046      0.4982                0.0212
  liquid50_mat5   direct_indirect quarter Logistic_Regression    0.6435         0.6645      0.5612                0.0210
liquid100_mat10     any_relevance  2month       Random_Forest    0.6575         0.6783      0.5754                0.0208
 liquid200_mat5            direct   2week            LightGBM    0.6923         0.7127      0.4865                0.0204
  liquid50_mat5   direct_indirect   2week            LightGBM    0.6834         0.7035      0.4950                0.0201
 liquid200_mat5            direct  2month       Random_Forest    0.6691         0.6886      0.4697                0.0195
 liquid200_mat5            direct quarter            LightGBM    0.7019         0.7212      0.4231                0.0192
 liquid200_mat5     any_relevance quarter            LightGBM    0.7019         0.7212      0.4231                0.0192
 liquid200_mat5     any_relevance quarter Logistic_Regression    0.5865         0.6058      0.4615                0.0192
liquid100_mat10     any_relevance   2week       Random_Forest    0.6556         0.6742      0.5113                0.0186
 liquid100_mat5     any_relevance   month            LightGBM    0.6651         0.6836      0.5016                0.0184
 liquid200_mat5            direct   2week       Random_Forest    0.6673         0.6854      0.5012                0.0180
  liquid50_mat5   direct_indirect   1week Logistic_Regression    0.6846         0.7018      0.5041                0.0173
liquid100_mat10   direct_indirect   2week       Random_Forest    0.6556         0.6723      0.5064                0.0167
 liquid100_mat5   direct_indirect  2month             XGBoost    0.6665         0.6829      0.4575                0.0164
 liquid100_mat5            direct  2month       Random_Forest    0.6798         0.6962      0.4710                0.0164
 liquid100_mat5     any_relevance   month       Random_Forest    0.6977         0.7137      0.4738                0.0160
 liquid200_mat5     any_relevance  2month             XGBoost    0.7351         0.7510      0.5140                0.0159
liquid100_mat10   direct_indirect quarter Logistic_Regression    0.5873         0.6032      0.4365                0.0159
 liquid100_mat5     any_relevance   2week       Random_Forest    0.6734         0.6893      0.4984                0.0158
 liquid100_mat5            direct   2week       Random_Forest    0.6734         0.6890      0.5010                0.0156
 liquid100_mat5   direct_indirect   month             XGBoost    0.6694         0.6847      0.4774                0.0152
liquid100_mat10            direct   2week             XGBoost    0.6482         0.6632      0.5018                0.0150
liquid100_mat10            direct   2week       Random_Forest    0.6556         0.6702      0.5147                0.0145
 liquid100_mat5            direct   month       Random_Forest    0.6977         0.7111      0.4894                0.0134
  liquid50_mat5   direct_indirect   month             XGBoost    0.6572         0.6700      0.4789                0.0128
  liquid50_mat5     any_relevance quarter             XGBoost    0.6411         0.6537      0.4778                0.0126
liquid100_mat10   direct_indirect  2month       Random_Forest    0.6575         0.6695      0.5545                0.0120
  liquid50_mat5            direct  2month             XGBoost    0.6864         0.6979      0.4823                0.0115
 liquid100_mat5            direct quarter Logistic_Regression    0.6023         0.6136      0.5206                0.0114
 liquid100_mat5   direct_indirect quarter Logistic_Regression    0.6023         0.6136      0.5111                0.0114
 liquid100_mat5     any_relevance   2week            LightGBM    0.6812         0.6924      0.5094                0.0113
 liquid200_mat5     any_relevance   2week            LightGBM    0.6923         0.7026      0.5087                0.0102
  liquid50_mat5     any_relevance  2month             XGBoost    0.6864         0.6962      0.4848                0.0098
liquid100_mat10   direct_indirect   month       Random_Forest    0.7149         0.7245      0.5220                0.0096
 liquid200_mat5   direct_indirect  2month Logistic_Regression    0.5481         0.5576      0.5322                0.0094
 liquid200_mat5   direct_indirect   2week       Random_Forest    0.6673         0.6767      0.4960                0.0094
 liquid200_mat5     any_relevance   1week       Random_Forest    0.6518         0.6609      0.4957                0.0091
 liquid100_mat5     any_relevance   1week             XGBoost    0.6756         0.6846      0.5026                0.0089
liquid100_mat10            direct   month             XGBoost    0.6724         0.6813      0.5302                0.0089
  liquid50_mat5   direct_indirect quarter            LightGBM    0.6555         0.6639      0.5156                0.0084
 liquid200_mat5   direct_indirect   2week            LightGBM    0.6923         0.7005      0.4928                0.0081
  liquid50_mat5   direct_indirect  2month             XGBoost    0.6864         0.6944      0.4737                0.0081
liquid100_mat10            direct quarter             XGBoost    0.5952         0.6032      0.3730                0.0079
 liquid200_mat5     any_relevance   2week       Random_Forest    0.6673         0.6748      0.4981                0.0075
 liquid100_mat5     any_relevance quarter Logistic_Regression    0.6023         0.6097      0.5338                0.0075
 liquid200_mat5            direct   1week            LightGBM    0.6970         0.7042      0.5110                0.0072
 liquid100_mat5     any_relevance   1week       Random_Forest    0.6359         0.6427      0.5087                0.0068
 liquid100_mat5   direct_indirect   2week            LightGBM    0.6812         0.6879      0.4996                0.0067
  liquid50_mat5     any_relevance   2week            LightGBM    0.6834         0.6901      0.4955                0.0067
 liquid100_mat5            direct  2month             XGBoost    0.6665         0.6732      0.4462                0.0066
liquid100_mat10   direct_indirect   1week Logistic_Regression    0.6757         0.6823      0.5227                0.0065
 liquid200_mat5   direct_indirect  2month       Random_Forest    0.6691         0.6756      0.4922                0.0065
 liquid200_mat5   direct_indirect   1week Logistic_Regression    0.6701         0.6762      0.5145                0.0061
 liquid200_mat5     any_relevance   1week             XGBoost    0.6774         0.6834      0.5085                0.0061
 liquid200_mat5     any_relevance   month       Random_Forest    0.6686         0.6744      0.4766                0.0058
 liquid200_mat5   direct_indirect   month       Random_Forest    0.6686         0.6744      0.4845                0.0058
liquid100_mat10     any_relevance   1week Logistic_Regression    0.6757         0.6813      0.5077                0.0055
 liquid200_mat5     any_relevance   month             XGBoost    0.6480         0.6534      0.5172                0.0055
  liquid50_mat5     any_relevance   2week       Random_Forest    0.6761         0.6813      0.4918                0.0053
  liquid50_mat5   direct_indirect  2month Logistic_Regression    0.6359         0.6411      0.5283                0.0053
 liquid200_mat5   direct_indirect   1week            LightGBM    0.6970         0.7019      0.5107                0.0049
 liquid200_mat5   direct_indirect   1week             XGBoost    0.6774         0.6819      0.5052                0.0046
  liquid50_mat5     any_relevance   1week       Random_Forest    0.6419         0.6463      0.5010                0.0043
  liquid50_mat5   direct_indirect   1week       Random_Forest    0.6419         0.6460      0.5030                0.0040
 liquid200_mat5   direct_indirect   month Logistic_Regression    0.5879         0.5915      0.4968                0.0036
 liquid200_mat5            direct   month       Random_Forest    0.6686         0.6723      0.4887                0.0036
 liquid100_mat5   direct_indirect   month       Random_Forest    0.6977         0.7013      0.4897                0.0036
 liquid200_mat5   direct_indirect  2month             XGBoost    0.7351         0.7387      0.5315                0.0036
 liquid200_mat5            direct  2month             XGBoost    0.7351         0.7387      0.4837                0.0036
 liquid100_mat5            direct   1week       Random_Forest    0.6359         0.6390      0.5103                0.0031
 liquid200_mat5            direct  2month            LightGBM    0.7227         0.7257      0.5439                0.0029
 liquid200_mat5     any_relevance  2month       Random_Forest    0.6691         0.6720      0.5240                0.0029
liquid100_mat10   direct_indirect   2week             XGBoost    0.6482         0.6511      0.5008                0.0029
 liquid100_mat5     any_relevance   2week             XGBoost    0.6700         0.6727      0.5034                0.0028
  liquid50_mat5   direct_indirect   2week       Random_Forest    0.6761         0.6787      0.4912                0.0026
 liquid100_mat5     any_relevance   2week Logistic_Regression    0.6665         0.6691      0.4802                0.0026
```

## Coverage

```text
       universe relevance_variant    unit  n_samples  n_periods  test_samples  positive_rate_test  llm_nonzero_rows  annotations
liquid100_mat10     any_relevance   1week       6832        244          1344              0.2612               493          572
liquid100_mat10     any_relevance  2month        784         28           140              0.4071               304          572
liquid100_mat10     any_relevance   2week       3444        123           672              0.2932               456          572
liquid100_mat10     any_relevance   month       1568         56           308              0.3506               380          572
liquid100_mat10     any_relevance quarter        504         18            84              0.2500               257          572
liquid100_mat10            direct   1week       6832        244          1344              0.2612               432          487
liquid100_mat10            direct  2month        784         28           140              0.4071               291          487
liquid100_mat10            direct   2week       3444        123           672              0.2932               409          487
liquid100_mat10            direct   month       1568         56           308              0.3506               356          487
liquid100_mat10            direct quarter        504         18            84              0.2500               248          487
liquid100_mat10   direct_indirect   1week       6832        244          1344              0.2612               451          507
liquid100_mat10   direct_indirect  2month        784         28           140              0.4071               296          507
liquid100_mat10   direct_indirect   2week       3444        123           672              0.2932               424          507
liquid100_mat10   direct_indirect   month       1568         56           308              0.3506               366          507
liquid100_mat10   direct_indirect quarter        504         18            84              0.2500               251          507
 liquid100_mat5     any_relevance   1week      10248        244          2016              0.2733               604          688
 liquid100_mat5     any_relevance  2month       1176         28           210              0.4190               393          688
 liquid100_mat5     any_relevance   2week       5166        123          1008              0.3026               566          688
 liquid100_mat5     any_relevance   month       2352         56           462              0.3593               480          688
 liquid100_mat5     any_relevance quarter        756         18           126              0.3016               332          688
 liquid100_mat5            direct   1week      10248        244          2016              0.2733               531          591
 liquid100_mat5            direct  2month       1176         28           210              0.4190               372          591
 liquid100_mat5            direct   2week       5166        123          1008              0.3026               507          591
 liquid100_mat5            direct   month       2352         56           462              0.3593               446          591
 liquid100_mat5            direct quarter        756         18           126              0.3016               317          591
 liquid100_mat5   direct_indirect   1week      10248        244          2016              0.2733               552          613
 liquid100_mat5   direct_indirect  2month       1176         28           210              0.4190               377          613
 liquid100_mat5   direct_indirect   2week       5166        123          1008              0.3026               524          613
 liquid100_mat5   direct_indirect   month       2352         56           462              0.3593               457          613
 liquid100_mat5   direct_indirect quarter        756         18           126              0.3016               320          613
 liquid200_mat5     any_relevance   1week       6344        244          1248              0.2756               401          463
 liquid200_mat5     any_relevance  2month        728         28           130              0.4077               244          463
 liquid200_mat5     any_relevance   2week       3198        123           624              0.3109               370          463
 liquid200_mat5     any_relevance   month       1456         56           286              0.3601               307          463
 liquid200_mat5     any_relevance quarter        468         18            78              0.3333               203          463
 liquid200_mat5            direct   1week       6344        244          1248              0.2756               331          369
 liquid200_mat5            direct  2month        728         28           130              0.4077               224          369
 liquid200_mat5            direct   2week       3198        123           624              0.3109               314          369
 liquid200_mat5            direct   month       1456         56           286              0.3601               275          369
 liquid200_mat5            direct quarter        468         18            78              0.3333               189          369
 liquid200_mat5   direct_indirect   1week       6344        244          1248              0.2756               351          390
 liquid200_mat5   direct_indirect  2month        728         28           130              0.4077               228          390
 liquid200_mat5   direct_indirect   2week       3198        123           624              0.3109               330          390
 liquid200_mat5   direct_indirect   month       1456         56           286              0.3601               285          390
 liquid200_mat5   direct_indirect quarter        468         18            78              0.3333               191          390
  liquid50_mat5     any_relevance   1week      13664        246          2744              0.2748               791          899
  liquid50_mat5     any_relevance  2month       1568         28           280              0.3857               526          899
  liquid50_mat5     any_relevance   2week       6889        124          1344              0.2954               744          899
  liquid50_mat5     any_relevance   month       3137         57           616              0.3474               634          899
  liquid50_mat5     any_relevance quarter       1009         19           168              0.2917               440          899
  liquid50_mat5            direct   1week      13664        246          2744              0.2748               716          800
  liquid50_mat5            direct  2month       1568         28           280              0.3857               505          800
  liquid50_mat5            direct   2week       6889        124          1344              0.2954               683          800
  liquid50_mat5            direct   month       3137         57           616              0.3474               599          800
  liquid50_mat5            direct quarter       1009         19           168              0.2917               425          800
  liquid50_mat5   direct_indirect   1week      13664        246          2744              0.2748               737          822
  liquid50_mat5   direct_indirect  2month       1568         28           280              0.3857               510          822
  liquid50_mat5   direct_indirect   2week       6889        124          1344              0.2954               700          822
  liquid50_mat5   direct_indirect   month       3137         57           616              0.3474               610          822
  liquid50_mat5   direct_indirect quarter       1009         19           168              0.2917               428          822
```
