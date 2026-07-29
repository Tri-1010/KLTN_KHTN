# Period-level material hybrid — HOSE100 quality universe

- annotation_source: `data/experiments/llm_semantic/article_semantics_cache.csv`
- price_source: `data/prices/hose100_quality_prices.csv`
- universe: HOSE100 quality (100 tickers)
- selection: original HOSE80 + 20 liquid HOSE tickers from `data/prices_extended`
- units: 1week, 2week, month, 2month, quarter
- relevance_variants: direct, direct_indirect, any_relevance, indirect_only
- threshold: next_period_return > 2.00%
- price_rows: 117566

## Tickers

```text
ACB,BCM,BID,BVH,CTG,FPT,GAS,GVR,HDB,HPG,MBB,MSN,MWG,PLX,POW,SAB,SHB,SSB,SSI,STB,TCB,TPB,VCB,VHM,VIB,VIC,VJC,VNM,VPB,VRE,EIB,LPB,MSB,NAB,OCB,PGB,VBB,BVB,ABB,KLB,BAB,VCI,HCM,VND,MBS,BSI,KDH,NVL,DXG,PDR,NLG,DIG,HDG,VCG,SCR,HSG,NKG,VGC,PHR,CSV,DPM,DCM,BMP,REE,NT2,PPC,GEX,EVF,PNJ,DGW,FRT,MCH,VHC,ANV,CMG,ELC,GMD,VSC,PVT,HAH,CII,PC1,TCH,KBC,VPI,IJC,LCG,VOS,TCM,AAA,PAN,SZC,CTD,FCN,DPG,SBT,IDI,HT1,KDC,MSH
```

## Best deltas

```text
       universe relevance_variant    unit               model  n_test   ba_a  ba_hybrid  delta_hybrid_minus_a   b   c  n_discordant  p_mid
HOSE100_quality     any_relevance quarter Logistic_Regression     388 0.6047     0.6365                0.0318  43  62           105 0.0645
HOSE100_quality            direct quarter       Random_Forest     388 0.6962     0.7259                0.0297   8  20            28 0.0241
HOSE100_quality            direct  2month             XGBoost     488 0.6576     0.6831                0.0255  29  38            67 0.2750
HOSE100_quality     indirect_only   2week Logistic_Regression    2400 0.6807     0.7059                0.0252 105 186           291 0.0000
HOSE100_quality   direct_indirect quarter       Random_Forest     388 0.6962     0.7204                0.0243  10  19            29 0.0987
HOSE100_quality   direct_indirect  2month             XGBoost     488 0.6576     0.6810                0.0234  29  38            67 0.2750
HOSE100_quality            direct quarter Logistic_Regression     388 0.6047     0.6274                0.0227   8  22            30 0.0107
HOSE100_quality   direct_indirect   1week             XGBoost    4888 0.6735     0.6959                0.0224 322 377           699 0.0376
HOSE100_quality            direct   1week             XGBoost    4888 0.6735     0.6940                0.0205 320 385           705 0.0144
HOSE100_quality     any_relevance   month            LightGBM    1088 0.6826     0.7022                0.0196  45  53            98 0.4215
HOSE100_quality     any_relevance  2month             XGBoost     488 0.6576     0.6768                0.0192  24  33            57 0.2370
HOSE100_quality     any_relevance   1week             XGBoost    4888 0.6735     0.6920                0.0185 332 398           730 0.0146
HOSE100_quality     indirect_only   1week             XGBoost    4888 0.6735     0.6919                0.0183 203 264           467 0.0048
HOSE100_quality            direct   month             XGBoost    1088 0.6674     0.6835                0.0161  63  88           151 0.0422
HOSE100_quality            direct   month            LightGBM    1088 0.6826     0.6980                0.0154  42  57            99 0.1332
HOSE100_quality   direct_indirect quarter Logistic_Regression     388 0.6047     0.6193                0.0146   7  18            25 0.0290
HOSE100_quality            direct  2month            LightGBM     488 0.6818     0.6959                0.0141  14  18            32 0.4869
HOSE100_quality     any_relevance  2month            LightGBM     488 0.6818     0.6951                0.0133  15  17            32 0.7283
HOSE100_quality   direct_indirect   month             XGBoost    1088 0.6674     0.6806                0.0132  69  79           148 0.4127
HOSE100_quality     indirect_only   1week Logistic_Regression    4888 0.6882     0.7001                0.0119 117 188           305 0.0000
HOSE100_quality     any_relevance   month             XGBoost    1088 0.6674     0.6774                0.0100  65  70           135 0.6683
HOSE100_quality     any_relevance   1week            LightGBM    4888 0.7109     0.7209                0.0099 136 177           313 0.0205
HOSE100_quality   direct_indirect  2month            LightGBM     488 0.6818     0.6915                0.0097  21  22            43 0.8804
HOSE100_quality            direct   1week            LightGBM    4888 0.7109     0.7205                0.0095 135 173           308 0.0305
HOSE100_quality   direct_indirect   2week            LightGBM    2400 0.7155     0.7246                0.0091  57  82           139 0.0342
HOSE100_quality            direct   2week             XGBoost    2400 0.6956     0.7046                0.0090 135 144           279 0.5908
HOSE100_quality   direct_indirect   1week            LightGBM    4888 0.7109     0.7184                0.0075 151 188           339 0.0446
HOSE100_quality   direct_indirect   2week       Random_Forest    2400 0.6873     0.6947                0.0074  72  77           149 0.6832
HOSE100_quality            direct   2week Logistic_Regression    2400 0.6807     0.6874                0.0068  71  96           167 0.0534
HOSE100_quality            direct quarter             XGBoost     388 0.6953     0.7017                0.0064  18  23            41 0.4408
HOSE100_quality     indirect_only quarter       Random_Forest     388 0.6962     0.7024                0.0063  12  14            26 0.7011
HOSE100_quality            direct   month       Random_Forest    1088 0.7028     0.7090                0.0061  35  43            78 0.3682
HOSE100_quality     any_relevance   2week       Random_Forest    2400 0.6873     0.6922                0.0049  73  79           152 0.6278
HOSE100_quality     indirect_only quarter Logistic_Regression     388 0.6047     0.6091                0.0045   0   1             1 0.5000
HOSE100_quality   direct_indirect   month            LightGBM    1088 0.6826     0.6867                0.0042  47  46            93 0.9179
HOSE100_quality   direct_indirect   1week Logistic_Regression    4888 0.6882     0.6922                0.0040  84 137           221 0.0004
HOSE100_quality     indirect_only   2week       Random_Forest    2400 0.6873     0.6904                0.0031  73  79           152 0.6278
HOSE100_quality     indirect_only   month       Random_Forest    1088 0.7028     0.7038                0.0010  33  36            69 0.7202
HOSE100_quality     indirect_only  2month       Random_Forest     488 0.6908     0.6916                0.0008  14  16            30 0.7201
HOSE100_quality            direct  2month       Random_Forest     488 0.6908     0.6916                0.0008  16  18            34 0.7359
HOSE100_quality     any_relevance   1week Logistic_Regression    4888 0.6882     0.6889                0.0007   2   5             7 0.2891
HOSE100_quality            direct   1week Logistic_Regression    4888 0.6882     0.6884                0.0001   2   3             5 0.6875
HOSE100_quality     any_relevance   2week            LightGBM    2400 0.7155     0.7156                0.0001  75  80           155 0.6891
HOSE100_quality     indirect_only   2week             XGBoost    2400 0.6956     0.6956                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only   month            LightGBM    1088 0.6826     0.6826                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only   2week            LightGBM    2400 0.7155     0.7155                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only  2month             XGBoost     488 0.6576     0.6576                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only   month             XGBoost    1088 0.6674     0.6674                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only  2month Logistic_Regression     488 0.6263     0.6263                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only  2month            LightGBM     488 0.6818     0.6818                0.0000   0   0             0 1.0000
HOSE100_quality     any_relevance  2month Logistic_Regression     488 0.6263     0.6263                0.0000   5   5            10 0.7539
HOSE100_quality     indirect_only   1week            LightGBM    4888 0.7109     0.7109                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only quarter            LightGBM     388 0.7009     0.7009                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only quarter             XGBoost     388 0.6953     0.6953                0.0000   0   0             0 1.0000
HOSE100_quality     any_relevance   2week             XGBoost    2400 0.6956     0.6955               -0.0001 146 144           290 0.9067
HOSE100_quality     any_relevance   2week Logistic_Regression    2400 0.6807     0.6804               -0.0003   2   1             3 0.6250
HOSE100_quality   direct_indirect   2week Logistic_Regression    2400 0.6807     0.6804               -0.0003   2   1             3 0.6250
HOSE100_quality            direct   1week       Random_Forest    4888 0.6499     0.6485               -0.0013 120 122           242 0.8979
HOSE100_quality            direct   2week            LightGBM    2400 0.7155     0.7141               -0.0014  71  66           137 0.6705
HOSE100_quality     any_relevance quarter       Random_Forest     388 0.6962     0.6925               -0.0036  17  15            32 0.7283
HOSE100_quality            direct  2month Logistic_Regression     488 0.6263     0.6223               -0.0040  55  91           146 0.0029
HOSE100_quality   direct_indirect   month       Random_Forest    1088 0.7028     0.6987               -0.0042  45  43            88 0.8323
HOSE100_quality   direct_indirect   2week             XGBoost    2400 0.6956     0.6912               -0.0044 170 161           331 0.6214
HOSE100_quality            direct   2week       Random_Forest    2400 0.6873     0.6827               -0.0046  77  69           146 0.5095
HOSE100_quality     indirect_only   1week       Random_Forest    4888 0.6499     0.6450               -0.0049 123 113           236 0.5161
HOSE100_quality     any_relevance   1week       Random_Forest    4888 0.6499     0.6445               -0.0054 116 122           238 0.6980
HOSE100_quality     any_relevance  2month       Random_Forest     488 0.6908     0.6852               -0.0056  16  15            31 0.8601
HOSE100_quality   direct_indirect  2month       Random_Forest     488 0.6908     0.6844               -0.0064  16  13            29 0.5847
HOSE100_quality   direct_indirect  2month Logistic_Regression     488 0.6263     0.6196               -0.0067  57  94           151 0.0026
HOSE100_quality   direct_indirect   1week       Random_Forest    4888 0.6499     0.6420               -0.0079 121 111           232 0.5125
HOSE100_quality     any_relevance   month       Random_Forest    1088 0.7028     0.6929               -0.0100  47  39            86 0.3912
HOSE100_quality   direct_indirect quarter            LightGBM     388 0.7009     0.6864               -0.0145  20  12            32 0.1628
HOSE100_quality            direct quarter            LightGBM     388 0.7009     0.6819               -0.0190  23  14            37 0.1433
HOSE100_quality     any_relevance quarter             XGBoost     388 0.6953     0.6757               -0.0197  20  15            35 0.4050
HOSE100_quality     indirect_only   month Logistic_Regression    1088 0.7218     0.7002               -0.0215  69  49           118 0.0663
HOSE100_quality   direct_indirect quarter             XGBoost     388 0.6953     0.6631               -0.0322  26  17            43 0.1742
HOSE100_quality     any_relevance quarter            LightGBM     388 0.7009     0.6595               -0.0414  28  11            39 0.0064
HOSE100_quality            direct   month Logistic_Regression    1088 0.7218     0.6404               -0.0814 173  75           248 0.0000
HOSE100_quality     any_relevance   month Logistic_Regression    1088 0.7218     0.6404               -0.0814 173  75           248 0.0000
HOSE100_quality   direct_indirect   month Logistic_Regression    1088 0.7218     0.6404               -0.0814 173  75           248 0.0000
```

## Balanced accuracy

```text
       universe relevance_variant    unit               model  Config_A  Config_Hybrid  Config_LLM  delta_hybrid_minus_A
HOSE100_quality     any_relevance quarter Logistic_Regression    0.6047         0.6365      0.5000                0.0318
HOSE100_quality            direct quarter       Random_Forest    0.6962         0.7259      0.4678                0.0297
HOSE100_quality            direct  2month             XGBoost    0.6576         0.6831      0.4502                0.0255
HOSE100_quality     indirect_only   2week Logistic_Regression    0.6807         0.7059      0.4959                0.0252
HOSE100_quality   direct_indirect quarter       Random_Forest    0.6962         0.7204      0.4785                0.0243
HOSE100_quality   direct_indirect  2month             XGBoost    0.6576         0.6810      0.4667                0.0234
HOSE100_quality            direct quarter Logistic_Regression    0.6047         0.6274      0.4955                0.0227
HOSE100_quality   direct_indirect   1week             XGBoost    0.6735         0.6959      0.5023                0.0224
HOSE100_quality            direct   1week             XGBoost    0.6735         0.6940      0.4999                0.0205
HOSE100_quality     any_relevance   month            LightGBM    0.6826         0.7022      0.5057                0.0196
HOSE100_quality     any_relevance  2month             XGBoost    0.6576         0.6768      0.4527                0.0192
HOSE100_quality     any_relevance   1week             XGBoost    0.6735         0.6920      0.4966                0.0185
HOSE100_quality     indirect_only   1week             XGBoost    0.6735         0.6919      0.4997                0.0183
HOSE100_quality            direct   month             XGBoost    0.6674         0.6835      0.5006                0.0161
HOSE100_quality            direct   month            LightGBM    0.6826         0.6980      0.5083                0.0154
HOSE100_quality   direct_indirect quarter Logistic_Regression    0.6047         0.6193      0.4891                0.0146
HOSE100_quality            direct  2month            LightGBM    0.6818         0.6959      0.4558                0.0141
HOSE100_quality     any_relevance  2month            LightGBM    0.6818         0.6951      0.4573                0.0133
HOSE100_quality   direct_indirect   month             XGBoost    0.6674         0.6806      0.5089                0.0132
HOSE100_quality     indirect_only   1week Logistic_Regression    0.6882         0.7001      0.5000                0.0119
HOSE100_quality     any_relevance   month             XGBoost    0.6674         0.6774      0.4983                0.0100
HOSE100_quality     any_relevance   1week            LightGBM    0.7109         0.7209      0.4959                0.0099
HOSE100_quality   direct_indirect  2month            LightGBM    0.6818         0.6915      0.4537                0.0097
HOSE100_quality            direct   1week            LightGBM    0.7109         0.7205      0.4998                0.0095
HOSE100_quality   direct_indirect   2week            LightGBM    0.7155         0.7246      0.5086                0.0091
HOSE100_quality            direct   2week             XGBoost    0.6956         0.7046      0.5051                0.0090
HOSE100_quality   direct_indirect   1week            LightGBM    0.7109         0.7184      0.5002                0.0075
HOSE100_quality   direct_indirect   2week       Random_Forest    0.6873         0.6947      0.5113                0.0074
HOSE100_quality            direct   2week Logistic_Regression    0.6807         0.6874      0.5211                0.0068
HOSE100_quality            direct quarter             XGBoost    0.6953         0.7017      0.4988                0.0064
HOSE100_quality     indirect_only quarter       Random_Forest    0.6962         0.7024      0.5034                0.0063
HOSE100_quality            direct   month       Random_Forest    0.7028         0.7090      0.5093                0.0061
HOSE100_quality     any_relevance   2week       Random_Forest    0.6873         0.6922      0.5103                0.0049
HOSE100_quality     indirect_only quarter Logistic_Regression    0.6047         0.6091      0.5007                0.0045
HOSE100_quality   direct_indirect   month            LightGBM    0.6826         0.6867      0.5073                0.0042
HOSE100_quality   direct_indirect   1week Logistic_Regression    0.6882         0.6922      0.4982                0.0040
HOSE100_quality     indirect_only   2week       Random_Forest    0.6873         0.6904      0.4967                0.0031
HOSE100_quality     indirect_only   month       Random_Forest    0.7028         0.7038      0.5000                0.0010
HOSE100_quality     indirect_only  2month       Random_Forest    0.6908         0.6916      0.4949                0.0008
HOSE100_quality            direct  2month       Random_Forest    0.6908         0.6916      0.4767                0.0008
HOSE100_quality     any_relevance   1week Logistic_Regression    0.6882         0.6889      0.4967                0.0007
HOSE100_quality            direct   1week Logistic_Regression    0.6882         0.6884      0.4983                0.0001
HOSE100_quality     any_relevance   2week            LightGBM    0.7155         0.7156      0.5083                0.0001
HOSE100_quality     indirect_only   2week             XGBoost    0.6956         0.6956      0.4974                0.0000
HOSE100_quality     indirect_only   month            LightGBM    0.6826         0.6826      0.5000                0.0000
HOSE100_quality     indirect_only   2week            LightGBM    0.7155         0.7155      0.5000                0.0000
HOSE100_quality     indirect_only  2month             XGBoost    0.6576         0.6576      0.4946                0.0000
HOSE100_quality     indirect_only   month             XGBoost    0.6674         0.6674      0.4987                0.0000
HOSE100_quality     indirect_only  2month Logistic_Regression    0.6263         0.6263      0.5010                0.0000
HOSE100_quality     indirect_only  2month            LightGBM    0.6818         0.6818      0.5000                0.0000
HOSE100_quality     any_relevance  2month Logistic_Regression    0.6263         0.6263      0.4694                0.0000
HOSE100_quality     indirect_only   1week            LightGBM    0.7109         0.7109      0.5000                0.0000
HOSE100_quality     indirect_only quarter            LightGBM    0.7009         0.7009      0.5000                0.0000
HOSE100_quality     indirect_only quarter             XGBoost    0.6953         0.6953      0.4989                0.0000
HOSE100_quality     any_relevance   2week             XGBoost    0.6956         0.6955      0.5068               -0.0001
HOSE100_quality     any_relevance   2week Logistic_Regression    0.6807         0.6804      0.5174               -0.0003
HOSE100_quality   direct_indirect   2week Logistic_Regression    0.6807         0.6804      0.5208               -0.0003
HOSE100_quality            direct   1week       Random_Forest    0.6499         0.6485      0.4986               -0.0013
HOSE100_quality            direct   2week            LightGBM    0.7155         0.7141      0.5081               -0.0014
HOSE100_quality     any_relevance quarter       Random_Forest    0.6962         0.6925      0.4733               -0.0036
HOSE100_quality            direct  2month Logistic_Regression    0.6263         0.6223      0.4776               -0.0040
HOSE100_quality   direct_indirect   month       Random_Forest    0.7028         0.6987      0.5064               -0.0042
HOSE100_quality   direct_indirect   2week             XGBoost    0.6956         0.6912      0.5069               -0.0044
HOSE100_quality            direct   2week       Random_Forest    0.6873         0.6827      0.5100               -0.0046
HOSE100_quality     indirect_only   1week       Random_Forest    0.6499         0.6450      0.4999               -0.0049
HOSE100_quality     any_relevance   1week       Random_Forest    0.6499         0.6445      0.4977               -0.0054
HOSE100_quality     any_relevance  2month       Random_Forest    0.6908         0.6852      0.4994               -0.0056
HOSE100_quality   direct_indirect  2month       Random_Forest    0.6908         0.6844      0.4796               -0.0064
HOSE100_quality   direct_indirect  2month Logistic_Regression    0.6263         0.6196      0.4742               -0.0067
HOSE100_quality   direct_indirect   1week       Random_Forest    0.6499         0.6420      0.4979               -0.0079
HOSE100_quality     any_relevance   month       Random_Forest    0.7028         0.6929      0.4967               -0.0100
HOSE100_quality   direct_indirect quarter            LightGBM    0.7009         0.6864      0.4827               -0.0145
HOSE100_quality            direct quarter            LightGBM    0.7009         0.6819      0.4746               -0.0190
HOSE100_quality     any_relevance quarter             XGBoost    0.6953         0.6757      0.4675               -0.0197
HOSE100_quality     indirect_only   month Logistic_Regression    0.7218         0.7002      0.4997               -0.0215
HOSE100_quality   direct_indirect quarter             XGBoost    0.6953         0.6631      0.4971               -0.0322
HOSE100_quality     any_relevance quarter            LightGBM    0.7009         0.6595      0.4748               -0.0414
HOSE100_quality            direct   month Logistic_Regression    0.7218         0.6404      0.5234               -0.0814
HOSE100_quality     any_relevance   month Logistic_Regression    0.7218         0.6404      0.5118               -0.0814
HOSE100_quality   direct_indirect   month Logistic_Regression    0.7218         0.6404      0.5205               -0.0814
```

## Coverage

```text
       universe relevance_variant    unit  n_samples  n_periods  test_samples  positive_rate_test  llm_nonzero_rows  annotations
HOSE100_quality     any_relevance   1week      24489        247          4888              0.2514              1076         1191
HOSE100_quality     any_relevance  2month       2888         29           488              0.2910               759         1191
HOSE100_quality     any_relevance   2week      12304        124          2400              0.2788              1011         1191
HOSE100_quality     any_relevance   month       5689         58          1088              0.2858               892         1191
HOSE100_quality     any_relevance quarter       1889         20           388              0.2887               658         1191
HOSE100_quality            direct   1week      24489        247          4888              0.2514               998         1090
HOSE100_quality            direct  2month       2888         29           488              0.2910               736         1090
HOSE100_quality            direct   2week      12304        124          2400              0.2788               949         1090
HOSE100_quality            direct   month       5689         58          1088              0.2858               855         1090
HOSE100_quality            direct quarter       1889         20           388              0.2887               642         1090
HOSE100_quality   direct_indirect   1week      24489        247          4888              0.2514              1019         1112
HOSE100_quality   direct_indirect  2month       2888         29           488              0.2910               741         1112
HOSE100_quality   direct_indirect   2week      12304        124          2400              0.2788               966         1112
HOSE100_quality   direct_indirect   month       5689         58          1088              0.2858               866         1112
HOSE100_quality   direct_indirect quarter       1889         20           388              0.2887               646         1112
HOSE100_quality     indirect_only   1week      24489        247          4888              0.2514                22           22
HOSE100_quality     indirect_only  2month       2888         29           488              0.2910                18           22
HOSE100_quality     indirect_only   2week      12304        124          2400              0.2788                21           22
HOSE100_quality     indirect_only   month       5689         58          1088              0.2858                20           22
HOSE100_quality     indirect_only quarter       1889         20           388              0.2887                17           22
```
