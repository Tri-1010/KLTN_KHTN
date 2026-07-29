# Period-level material hybrid — HOSE100 quality universe

- annotation_source: `data/experiments/llm_semantic/article_semantics_cache_hose100_extra.csv`
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
HOSE100_quality     indirect_only quarter Logistic_Regression     388 0.6047     0.6380                0.0333  48  62           110 0.1837
HOSE100_quality            direct   2week Logistic_Regression    2400 0.6807     0.7050                0.0243 112 185           297 0.0000
HOSE100_quality     any_relevance   month             XGBoost    1088 0.6674     0.6916                0.0241  67  91           158 0.0567
HOSE100_quality   direct_indirect  2month             XGBoost     488 0.6576     0.6816                0.0240  30  38            68 0.3356
HOSE100_quality     any_relevance   2week Logistic_Regression    2400 0.6807     0.7036                0.0230 114 184           298 0.0000
HOSE100_quality     any_relevance  2month             XGBoost     488 0.6576     0.6768                0.0192  27  36            63 0.2604
HOSE100_quality     indirect_only   1week             XGBoost    4888 0.6735     0.6919                0.0183 203 264           467 0.0048
HOSE100_quality   direct_indirect quarter       Random_Forest     388 0.6962     0.7132                0.0170  13  18            31 0.3771
HOSE100_quality            direct   1week             XGBoost    4888 0.6735     0.6888                0.0153 358 369           727 0.6835
HOSE100_quality     any_relevance   1week             XGBoost    4888 0.6735     0.6881                0.0146 363 379           742 0.5572
HOSE100_quality     any_relevance   month            LightGBM    1088 0.6826     0.6970                0.0145  49  49            98 0.9196
HOSE100_quality            direct   2week       Random_Forest    2400 0.6873     0.7007                0.0135  62  80           142 0.1320
HOSE100_quality     indirect_only   2week       Random_Forest    2400 0.6873     0.7006                0.0133  56  83           139 0.0222
HOSE100_quality     any_relevance   1week Logistic_Regression    4888 0.6882     0.7009                0.0127 144 229           373 0.0000
HOSE100_quality   direct_indirect  2month            LightGBM     488 0.6818     0.6936                0.0118  18  19            37 0.8714
HOSE100_quality            direct quarter Logistic_Regression     388 0.6047     0.6164                0.0117   2   7             9 0.1094
HOSE100_quality            direct   month             XGBoost    1088 0.6674     0.6790                0.0116  61  70           131 0.4335
HOSE100_quality            direct  2month             XGBoost     488 0.6576     0.6690                0.0114  30  35            65 0.5386
HOSE100_quality   direct_indirect quarter Logistic_Regression     388 0.6047     0.6146                0.0099   2   6             8 0.1797
HOSE100_quality     any_relevance quarter Logistic_Regression     388 0.6047     0.6146                0.0099   2   6             8 0.1797
HOSE100_quality     any_relevance   2week       Random_Forest    2400 0.6873     0.6964                0.0091  71  85           156 0.2638
HOSE100_quality            direct   month            LightGBM    1088 0.6826     0.6909                0.0084  48  49            97 0.9196
HOSE100_quality   direct_indirect   2week       Random_Forest    2400 0.6873     0.6953                0.0080  64  79           143 0.2112
HOSE100_quality            direct   1week            LightGBM    4888 0.7109     0.7179                0.0069 158 179           337 0.2533
HOSE100_quality   direct_indirect   2week             XGBoost    2400 0.6956     0.7023                0.0067 147 151           298 0.8171
HOSE100_quality     indirect_only  2month             XGBoost     488 0.6576     0.6634                0.0058  21  25            46 0.5601
HOSE100_quality     any_relevance quarter       Random_Forest     388 0.6962     0.7016                0.0054  14  17            31 0.5966
HOSE100_quality   direct_indirect   1week             XGBoost    4888 0.6735     0.6776                0.0040 368 362           730 0.8244
HOSE100_quality   direct_indirect   1week            LightGBM    4888 0.7109     0.7149                0.0040 153 194           347 0.0278
HOSE100_quality     indirect_only  2month       Random_Forest     488 0.6908     0.6935                0.0027  13  12            25 0.8450
HOSE100_quality     any_relevance   1week            LightGBM    4888 0.7109     0.7133                0.0023 157 162           319 0.7799
HOSE100_quality   direct_indirect   month            LightGBM    1088 0.6826     0.6845                0.0019  47  50            97 0.7620
HOSE100_quality   direct_indirect   2week            LightGBM    2400 0.7155     0.7173                0.0018  63  74           137 0.3491
HOSE100_quality            direct  2month            LightGBM     488 0.6818     0.6831                0.0013  15  13            28 0.7111
HOSE100_quality            direct   1week Logistic_Regression    4888 0.6882     0.6884                0.0001   2   3             5 0.6875
HOSE100_quality   direct_indirect   1week Logistic_Regression    4888 0.6882     0.6884                0.0001   2   3             5 0.6875
HOSE100_quality     indirect_only quarter             XGBoost     388 0.6953     0.6953                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only  2month            LightGBM     488 0.6818     0.6818                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only  2month Logistic_Regression     488 0.6263     0.6263                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only   2week            LightGBM    2400 0.7155     0.7155                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only   2week Logistic_Regression    2400 0.6807     0.6807                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only   1week            LightGBM    4888 0.7109     0.7109                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only   2week             XGBoost    2400 0.6956     0.6956                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only   month            LightGBM    1088 0.6826     0.6826                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only quarter            LightGBM     388 0.7009     0.7009                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only   month             XGBoost    1088 0.6674     0.6674                0.0000   0   0             0 1.0000
HOSE100_quality     indirect_only   1week Logistic_Regression    4888 0.6882     0.6881               -0.0001   1   0             1 0.5000
HOSE100_quality   direct_indirect   2week Logistic_Regression    2400 0.6807     0.6804               -0.0003   2   1             3 0.6250
HOSE100_quality            direct quarter       Random_Forest     388 0.6962     0.6955               -0.0007  15  19            34 0.4996
HOSE100_quality     any_relevance  2month            LightGBM     488 0.6818     0.6810               -0.0008  16  14            30 0.7201
HOSE100_quality            direct   month       Random_Forest    1088 0.7028     0.7019               -0.0010  44  44            88 0.9152
HOSE100_quality     any_relevance   2week            LightGBM    2400 0.7155     0.7141               -0.0014  83  86           169 0.8181
HOSE100_quality     indirect_only   1week       Random_Forest    4888 0.6499     0.6483               -0.0016 118 120           238 0.8971
HOSE100_quality   direct_indirect  2month       Random_Forest     488 0.6908     0.6881               -0.0027  15  16            31 0.8601
HOSE100_quality            direct   1week       Random_Forest    4888 0.6499     0.6465               -0.0034 112 117           229 0.7417
HOSE100_quality            direct  2month Logistic_Regression     488 0.6263     0.6228               -0.0035   6   5            11 0.7744
HOSE100_quality     indirect_only   month       Random_Forest    1088 0.7028     0.6987               -0.0042  35  39            74 0.6445
HOSE100_quality   direct_indirect   1week       Random_Forest    4888 0.6499     0.6454               -0.0045 119 120           239 0.9486
HOSE100_quality            direct   2week            LightGBM    2400 0.7155     0.7105               -0.0050  63  63           126 0.9291
HOSE100_quality     any_relevance   month       Random_Forest    1088 0.7028     0.6974               -0.0055  41  37            78 0.6530
HOSE100_quality            direct   2week             XGBoost    2400 0.6956     0.6900               -0.0056 147 134           281 0.4389
HOSE100_quality            direct quarter            LightGBM     388 0.7009     0.6946               -0.0063  15  13            28 0.7111
HOSE100_quality     any_relevance   1week       Random_Forest    4888 0.6499     0.6432               -0.0066 118 101           219 0.2517
HOSE100_quality   direct_indirect  2month Logistic_Regression     488 0.6263     0.6193               -0.0070   7   5            12 0.5811
HOSE100_quality     any_relevance  2month       Random_Forest     488 0.6908     0.6838               -0.0070  15  13            28 0.7111
HOSE100_quality     indirect_only quarter       Random_Forest     388 0.6962     0.6881               -0.0081  17  14            31 0.5966
HOSE100_quality     any_relevance   2week             XGBoost    2400 0.6956     0.6867               -0.0089 157 134           291 0.1782
HOSE100_quality   direct_indirect   month             XGBoost    1088 0.6674     0.6572               -0.0103  80  70           150 0.4159
HOSE100_quality   direct_indirect   month       Random_Forest    1088 0.7028     0.6925               -0.0103  48  35            83 0.1557
HOSE100_quality   direct_indirect quarter             XGBoost     388 0.6953     0.6847               -0.0106  19  19            38 0.8714
HOSE100_quality            direct  2month       Random_Forest     488 0.6908     0.6732               -0.0176  15  10            25 0.3269
HOSE100_quality            direct quarter             XGBoost     388 0.6953     0.6758               -0.0195  17  15            32 0.7283
HOSE100_quality     any_relevance  2month Logistic_Regression     488 0.6263     0.6045               -0.0218  25  30            55 0.5044
HOSE100_quality     indirect_only   month Logistic_Regression    1088 0.7218     0.6996               -0.0222  70  49           119 0.0548
HOSE100_quality   direct_indirect quarter            LightGBM     388 0.7009     0.6783               -0.0226  24  13            37 0.0730
HOSE100_quality     any_relevance quarter            LightGBM     388 0.7009     0.6747               -0.0262  26  13            39 0.0385
HOSE100_quality   direct_indirect   month Logistic_Regression    1088 0.7218     0.6919               -0.0299  78  48           126 0.0075
HOSE100_quality     any_relevance quarter             XGBoost     388 0.6953     0.6550               -0.0403  20   8            28 0.0241
HOSE100_quality            direct   month Logistic_Regression    1088 0.7218     0.6404               -0.0814 173  75           248 0.0000
HOSE100_quality     any_relevance   month Logistic_Regression    1088 0.7218     0.6404               -0.0814 173  75           248 0.0000
```

## Balanced accuracy

```text
       universe relevance_variant    unit               model  Config_A  Config_Hybrid  Config_LLM  delta_hybrid_minus_A
HOSE100_quality     indirect_only quarter Logistic_Regression    0.6047         0.6380      0.5007                0.0333
HOSE100_quality            direct   2week Logistic_Regression    0.6807         0.7050      0.5196                0.0243
HOSE100_quality     any_relevance   month             XGBoost    0.6674         0.6916      0.4903                0.0241
HOSE100_quality   direct_indirect  2month             XGBoost    0.6576         0.6816      0.4468                0.0240
HOSE100_quality     any_relevance   2week Logistic_Regression    0.6807         0.7036      0.5173                0.0230
HOSE100_quality     any_relevance  2month             XGBoost    0.6576         0.6768      0.4530                0.0192
HOSE100_quality     indirect_only   1week             XGBoost    0.6735         0.6919      0.4997                0.0183
HOSE100_quality   direct_indirect quarter       Random_Forest    0.6962         0.7132      0.4809                0.0170
HOSE100_quality            direct   1week             XGBoost    0.6735         0.6888      0.5001                0.0153
HOSE100_quality     any_relevance   1week             XGBoost    0.6735         0.6881      0.4973                0.0146
HOSE100_quality     any_relevance   month            LightGBM    0.6826         0.6970      0.5080                0.0145
HOSE100_quality            direct   2week       Random_Forest    0.6873         0.7007      0.5138                0.0135
HOSE100_quality     indirect_only   2week       Random_Forest    0.6873         0.7006      0.4967                0.0133
HOSE100_quality     any_relevance   1week Logistic_Regression    0.6882         0.7009      0.4973                0.0127
HOSE100_quality   direct_indirect  2month            LightGBM    0.6818         0.6936      0.4309                0.0118
HOSE100_quality            direct quarter Logistic_Regression    0.6047         0.6164      0.4788                0.0117
HOSE100_quality            direct   month             XGBoost    0.6674         0.6790      0.5048                0.0116
HOSE100_quality            direct  2month             XGBoost    0.6576         0.6690      0.4607                0.0114
HOSE100_quality   direct_indirect quarter Logistic_Regression    0.6047         0.6146      0.4818                0.0099
HOSE100_quality     any_relevance quarter Logistic_Regression    0.6047         0.6146      0.4944                0.0099
HOSE100_quality     any_relevance   2week       Random_Forest    0.6873         0.6964      0.5131                0.0091
HOSE100_quality            direct   month            LightGBM    0.6826         0.6909      0.5067                0.0084
HOSE100_quality   direct_indirect   2week       Random_Forest    0.6873         0.6953      0.5110                0.0080
HOSE100_quality            direct   1week            LightGBM    0.7109         0.7179      0.5007                0.0069
HOSE100_quality   direct_indirect   2week             XGBoost    0.6956         0.7023      0.5099                0.0067
HOSE100_quality     indirect_only  2month             XGBoost    0.6576         0.6634      0.4911                0.0058
HOSE100_quality     any_relevance quarter       Random_Forest    0.6962         0.7016      0.4918                0.0054
HOSE100_quality   direct_indirect   1week             XGBoost    0.6735         0.6776      0.5015                0.0040
HOSE100_quality   direct_indirect   1week            LightGBM    0.7109         0.7149      0.5007                0.0040
HOSE100_quality     indirect_only  2month       Random_Forest    0.6908         0.6935      0.4913                0.0027
HOSE100_quality     any_relevance   1week            LightGBM    0.7109         0.7133      0.4984                0.0023
HOSE100_quality   direct_indirect   month            LightGBM    0.6826         0.6845      0.5099                0.0019
HOSE100_quality   direct_indirect   2week            LightGBM    0.7155         0.7173      0.5151                0.0018
HOSE100_quality            direct  2month            LightGBM    0.6818         0.6831      0.4518                0.0013
HOSE100_quality            direct   1week Logistic_Regression    0.6882         0.6884      0.4982                0.0001
HOSE100_quality   direct_indirect   1week Logistic_Regression    0.6882         0.6884      0.4991                0.0001
HOSE100_quality     indirect_only quarter             XGBoost    0.6953         0.6953      0.4989                0.0000
HOSE100_quality     indirect_only  2month            LightGBM    0.6818         0.6818      0.5000                0.0000
HOSE100_quality     indirect_only  2month Logistic_Regression    0.6263         0.6263      0.4933                0.0000
HOSE100_quality     indirect_only   2week            LightGBM    0.7155         0.7155      0.5000                0.0000
HOSE100_quality     indirect_only   2week Logistic_Regression    0.6807         0.6807      0.4959                0.0000
HOSE100_quality     indirect_only   1week            LightGBM    0.7109         0.7109      0.5000                0.0000
HOSE100_quality     indirect_only   2week             XGBoost    0.6956         0.6956      0.4959                0.0000
HOSE100_quality     indirect_only   month            LightGBM    0.6826         0.6826      0.5000                0.0000
HOSE100_quality     indirect_only quarter            LightGBM    0.7009         0.7009      0.5000                0.0000
HOSE100_quality     indirect_only   month             XGBoost    0.6674         0.6674      0.4994                0.0000
HOSE100_quality     indirect_only   1week Logistic_Regression    0.6882         0.6881      0.5000               -0.0001
HOSE100_quality   direct_indirect   2week Logistic_Regression    0.6807         0.6804      0.5161               -0.0003
HOSE100_quality            direct quarter       Random_Forest    0.6962         0.6955      0.4756               -0.0007
HOSE100_quality     any_relevance  2month            LightGBM    0.6818         0.6810      0.4522               -0.0008
HOSE100_quality            direct   month       Random_Forest    0.7028         0.7019      0.5112               -0.0010
HOSE100_quality     any_relevance   2week            LightGBM    0.7155         0.7141      0.5142               -0.0014
HOSE100_quality     indirect_only   1week       Random_Forest    0.6499         0.6483      0.4999               -0.0016
HOSE100_quality   direct_indirect  2month       Random_Forest    0.6908         0.6881      0.4593               -0.0027
HOSE100_quality            direct   1week       Random_Forest    0.6499         0.6465      0.4988               -0.0034
HOSE100_quality            direct  2month Logistic_Regression    0.6263         0.6228      0.4630               -0.0035
HOSE100_quality     indirect_only   month       Random_Forest    0.7028         0.6987      0.5010               -0.0042
HOSE100_quality   direct_indirect   1week       Random_Forest    0.6499         0.6454      0.4970               -0.0045
HOSE100_quality            direct   2week            LightGBM    0.7155         0.7105      0.5145               -0.0050
HOSE100_quality     any_relevance   month       Random_Forest    0.7028         0.6974      0.5060               -0.0055
HOSE100_quality            direct   2week             XGBoost    0.6956         0.6900      0.5137               -0.0056
HOSE100_quality            direct quarter            LightGBM    0.7009         0.6946      0.4827               -0.0063
HOSE100_quality     any_relevance   1week       Random_Forest    0.6499         0.6432      0.4972               -0.0066
HOSE100_quality   direct_indirect  2month Logistic_Regression    0.6263         0.6193      0.4610               -0.0070
HOSE100_quality     any_relevance  2month       Random_Forest    0.6908         0.6838      0.4766               -0.0070
HOSE100_quality     indirect_only quarter       Random_Forest    0.6962         0.6881      0.4989               -0.0081
HOSE100_quality     any_relevance   2week             XGBoost    0.6956         0.6867      0.5125               -0.0089
HOSE100_quality   direct_indirect   month             XGBoost    0.6674         0.6572      0.4957               -0.0103
HOSE100_quality   direct_indirect   month       Random_Forest    0.7028         0.6925      0.5048               -0.0103
HOSE100_quality   direct_indirect quarter             XGBoost    0.6953         0.6847      0.4779               -0.0106
HOSE100_quality            direct  2month       Random_Forest    0.6908         0.6732      0.4783               -0.0176
HOSE100_quality            direct quarter             XGBoost    0.6953         0.6758      0.4715               -0.0195
HOSE100_quality     any_relevance  2month Logistic_Regression    0.6263         0.6045      0.4620               -0.0218
HOSE100_quality     indirect_only   month Logistic_Regression    0.7218         0.6996      0.4997               -0.0222
HOSE100_quality   direct_indirect quarter            LightGBM    0.7009         0.6783      0.4493               -0.0226
HOSE100_quality     any_relevance quarter            LightGBM    0.7009         0.6747      0.4928               -0.0262
HOSE100_quality   direct_indirect   month Logistic_Regression    0.7218         0.6919      0.5137               -0.0299
HOSE100_quality     any_relevance quarter             XGBoost    0.6953         0.6550      0.4825               -0.0403
HOSE100_quality            direct   month Logistic_Regression    0.7218         0.6404      0.5124               -0.0814
HOSE100_quality     any_relevance   month Logistic_Regression    0.7218         0.6404      0.5073               -0.0814
```

## Coverage

```text
       universe relevance_variant    unit  n_samples  n_periods  test_samples  positive_rate_test  llm_nonzero_rows  annotations
HOSE100_quality     any_relevance   1week      24489        247          4888              0.2514              1115         1234
HOSE100_quality     any_relevance  2month       2888         29           488              0.2910               791         1234
HOSE100_quality     any_relevance   2week      12304        124          2400              0.2788              1048         1234
HOSE100_quality     any_relevance   month       5689         58          1088              0.2858               927         1234
HOSE100_quality     any_relevance quarter       1889         20           388              0.2887               690         1234
HOSE100_quality            direct   1week      24489        247          4888              0.2514              1036         1132
HOSE100_quality            direct  2month       2888         29           488              0.2910               767         1132
HOSE100_quality            direct   2week      12304        124          2400              0.2788               985         1132
HOSE100_quality            direct   month       5689         58          1088              0.2858               889         1132
HOSE100_quality            direct quarter       1889         20           388              0.2887               673         1132
HOSE100_quality   direct_indirect   1week      24489        247          4888              0.2514              1058         1155
HOSE100_quality   direct_indirect  2month       2888         29           488              0.2910               773         1155
HOSE100_quality   direct_indirect   2week      12304        124          2400              0.2788              1003         1155
HOSE100_quality   direct_indirect   month       5689         58          1088              0.2858               901         1155
HOSE100_quality   direct_indirect quarter       1889         20           388              0.2887               678         1155
HOSE100_quality     indirect_only   1week      24489        247          4888              0.2514                23           23
HOSE100_quality     indirect_only  2month       2888         29           488              0.2910                19           23
HOSE100_quality     indirect_only   2week      12304        124          2400              0.2788                22           23
HOSE100_quality     indirect_only   month       5689         58          1088              0.2858                21           23
HOSE100_quality     indirect_only quarter       1889         20           388              0.2887                18           23
```
