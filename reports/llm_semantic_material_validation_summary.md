# LLM semantic material-event validation

- selected_articles: 2000
- ok_annotations: 1991
- material_annotations_any_relevance: 137
- direct_material_annotations: 121

## Pooled Hybrid vs Technical — best deltas

```text
             variant ticker horizon               model  n_test   ba_a  ba_hybrid  delta_hybrid_minus_a  delta_ci_low  delta_ci_high  p_mid   b   c
material_events_only    ALL     20d       Random_Forest    1150 0.5025     0.5343                0.0318        0.0094         0.0555 0.0109  77 112
direct_material_only    ALL     10d       Random_Forest    1160 0.4905     0.5216                0.0310        0.0020         0.0579 0.0211 110 147
material_events_only    ALL      5d       Random_Forest    1165 0.5149     0.5408                0.0259       -0.0046         0.0568 0.1504 150 176
material_events_only    ALL     10d       Random_Forest    1160 0.4905     0.5159                0.0254        0.0008         0.0523 0.0488 108 139
material_events_only    ALL      1d Logistic_Regression    1170 0.5150     0.5381                0.0230        0.0014         0.0463 0.3853  89 101
direct_material_only    ALL     20d       Random_Forest    1150 0.5025     0.5238                0.0212       -0.0008         0.0442 0.0739  71  94
direct_material_only    ALL      1d       Random_Forest    1170 0.5100     0.5296                0.0196       -0.0125         0.0492 0.5780 156 166
       material_lag1    ALL      1d       Random_Forest    1170 0.5100     0.5280                0.0180       -0.0133         0.0471 0.5309 148 159
material_events_only    ALL      1d       Random_Forest    1170 0.5100     0.5257                0.0157       -0.0162         0.0467 0.7460 168 174
direct_material_only    ALL     10d Logistic_Regression    1160 0.4527     0.4681                0.0154       -0.0102         0.0414 0.9498 126 126
       material_lag1    ALL     10d Logistic_Regression    1160 0.4527     0.4679                0.0152       -0.0125         0.0447 0.6947 162 155
direct_material_only    ALL      1d Logistic_Regression    1170 0.5150     0.5302                0.0151       -0.0057         0.0368 0.7064  85  90
direct_material_lag1    ALL     10d Logistic_Regression    1160 0.4527     0.4678                0.0150       -0.0085         0.0415 0.9498 126 126
       material_lag1    ALL      1d Logistic_Regression    1170 0.5150     0.5290                0.0139       -0.0091         0.0366 0.7676  89  93
material_events_only    ALL     10d Logistic_Regression    1160 0.4527     0.4633                0.0105       -0.0149         0.0386 0.5169 149 138
direct_material_lag1    ALL     10d       Random_Forest    1160 0.4905     0.4989                0.0083       -0.0173         0.0342 0.4664 108 119
direct_material_lag1    ALL      1d Logistic_Regression    1170 0.5150     0.5232                0.0081       -0.0124         0.0294 0.9370  80  80
       material_lag1    ALL      5d       Random_Forest    1165 0.5149     0.5230                0.0081       -0.0230         0.0373 0.6522 153 161
direct_material_lag1    ALL      1d       Random_Forest    1170 0.5100     0.5166                0.0066       -0.0234         0.0353 0.9086 152 150
direct_material_only    ALL      5d       Random_Forest    1165 0.5149     0.5195                0.0046       -0.0218         0.0315 0.9037 135 137
```

## Per-ticker Hybrid vs Technical — best deltas

```text
             variant ticker horizon               model  n_test   ba_a  ba_hybrid  delta_hybrid_minus_a  delta_ci_low  delta_ci_high  p_mid  b  c
       material_lag1    SSI     10d       Random_Forest     232 0.4369     0.5997                0.1628        0.0968         0.2292 0.0000 18 55
direct_material_lag1    SSI     10d       Random_Forest     232 0.4369     0.5997                0.1628        0.0968         0.2292 0.0000 18 55
direct_material_only    SSI     10d       Random_Forest     232 0.4369     0.5979                0.1610        0.0907         0.2328 0.0000 22 59
material_events_only    SSI     10d       Random_Forest     232 0.4369     0.5979                0.1610        0.0907         0.2328 0.0000 22 59
direct_material_lag1    VCB     10d Logistic_Regression     232 0.5322     0.6042                0.0720        0.0152         0.1300 0.1524 19 29
direct_material_lag1    VCB     10d       Random_Forest     232 0.5248     0.5910                0.0662        0.0143         0.1201 0.0288 11 24
       material_lag1    HPG     10d       Random_Forest     232 0.5190     0.5828                0.0637        0.0156         0.1115 0.0351 10 22
direct_material_only    VCB     10d       Random_Forest     232 0.5248     0.5885                0.0637        0.0107         0.1166 0.0237 12 26
material_events_only    HPG      5d       Random_Forest     233 0.5572     0.6175                0.0603       -0.0074         0.1289 0.1619 25 36
direct_material_only    VCB     10d Logistic_Regression     232 0.5322     0.5885                0.0564       -0.0021         0.1128 0.3020 19 26
direct_material_lag1    VCB     20d       Random_Forest     230 0.6452     0.6992                0.0540        0.0181         0.0952 0.0266  5 15
direct_material_lag1    HPG     10d       Random_Forest     232 0.5190     0.5724                0.0534        0.0061         0.0989 0.0614  9 19
material_events_only    HPG     20d       Random_Forest     230 0.5478     0.6000                0.0522        0.0043         0.0970 0.0294  9 21
material_events_only    HPG     10d       Random_Forest     232 0.5190     0.5691                0.0501        0.0106         0.0927 0.0266  5 15
direct_material_lag1    VCB     20d Logistic_Regression     230 0.6483     0.6964                0.0481       -0.0020         0.1035 0.1214 12 21
       material_lag1    VCB     10d       Random_Forest     232 0.5248     0.5714                0.0466        0.0029         0.0928 0.0357  8 19
direct_material_only    HPG     10d       Random_Forest     232 0.5190     0.5644                0.0453        0.0066         0.0846 0.0414  5 14
material_events_only    HPG     10d Logistic_Regression     232 0.5000     0.5451                0.0451       -0.0015         0.1015 0.3817 20 26
direct_material_only    VCB     20d       Random_Forest     230 0.6452     0.6884                0.0432        0.0083         0.0825 0.0636  5 13
material_events_only    VCB     10d       Random_Forest     232 0.5248     0.5653                0.0404       -0.0006         0.0852 0.0428  9 20
direct_material_only    HPG     20d       Random_Forest     230 0.5478     0.5870                0.0391       -0.0087         0.0833 0.0872  9 18
material_events_only    SSI     20d       Random_Forest     230 0.4935     0.5312                0.0376        0.0108         0.0656 0.0129  2 11
direct_material_only    SSI     20d       Random_Forest     230 0.4935     0.5312                0.0376        0.0108         0.0656 0.0129  2 11
direct_material_only    VNM      1d       Random_Forest     234 0.5095     0.5462                0.0367       -0.0251         0.1010 0.2288 23 32
material_events_only    VNM      1d       Random_Forest     234 0.5095     0.5462                0.0367       -0.0251         0.1010 0.2288 23 32
       material_lag1    HPG      5d       Random_Forest     233 0.5572     0.5906                0.0334       -0.0260         0.0989 0.4270 25 31
direct_material_lag1    FPT      1d       Random_Forest     234 0.5072     0.5399                0.0327       -0.0354         0.1010 0.6570 38 42
direct_material_only    HPG      5d       Random_Forest     233 0.5572     0.5869                0.0297       -0.0353         0.0920 0.4966 24 29
direct_material_lag1    VCB      5d       Random_Forest     233 0.5909     0.6182                0.0272       -0.0196         0.0724 0.2649 11 17
       material_lag1    FPT      1d       Random_Forest     234 0.5072     0.5334                0.0262       -0.0501         0.1016 0.9122 40 41
```

## Annotation counts by ticker/event

```text
             variant ticker event_type  n_articles
direct_material_lag1    FPT    capital          16
direct_material_lag1    FPT   dividend           6
direct_material_lag1    FPT   earnings           5
direct_material_lag1    FPT legal_risk           1
direct_material_lag1    HPG    capital           6
direct_material_lag1    HPG   dividend           2
direct_material_lag1    HPG   earnings           4
direct_material_lag1    HPG legal_risk           4
direct_material_lag1    SSI    capital          27
direct_material_lag1    SSI   dividend           2
direct_material_lag1    SSI   earnings           1
direct_material_lag1    SSI legal_risk           2
direct_material_lag1    VCB    capital          19
direct_material_lag1    VCB   earnings           3
direct_material_lag1    VCB legal_risk           5
direct_material_lag1    VNM    capital           3
direct_material_lag1    VNM   dividend          11
direct_material_lag1    VNM   earnings           3
direct_material_lag1    VNM legal_risk           1
direct_material_only    FPT    capital          16
direct_material_only    FPT   dividend           6
direct_material_only    FPT   earnings           5
direct_material_only    FPT legal_risk           1
direct_material_only    HPG    capital           6
direct_material_only    HPG   dividend           2
direct_material_only    HPG   earnings           4
direct_material_only    HPG legal_risk           4
direct_material_only    SSI    capital          27
direct_material_only    SSI   dividend           2
direct_material_only    SSI   earnings           1
direct_material_only    SSI legal_risk           2
direct_material_only    VCB    capital          19
direct_material_only    VCB   earnings           3
direct_material_only    VCB legal_risk           5
direct_material_only    VNM    capital           3
direct_material_only    VNM   dividend          11
direct_material_only    VNM   earnings           3
direct_material_only    VNM legal_risk           1
material_events_only    FPT    capital          22
material_events_only    FPT  debt_risk           1
material_events_only    FPT   dividend           6
material_events_only    FPT   earnings           5
material_events_only    FPT legal_risk           1
material_events_only    HPG    capital           7
material_events_only    HPG   dividend           2
material_events_only    HPG   earnings           4
material_events_only    HPG legal_risk           4
material_events_only    SSI    capital          27
material_events_only    SSI   dividend           2
material_events_only    SSI   earnings           1
material_events_only    SSI legal_risk           2
material_events_only    VCB    capital          26
material_events_only    VCB   earnings           3
material_events_only    VCB legal_risk           6
material_events_only    VNM    capital           3
material_events_only    VNM   dividend          11
material_events_only    VNM   earnings           3
material_events_only    VNM legal_risk           1
       material_lag1    FPT    capital          22
       material_lag1    FPT  debt_risk           1
       material_lag1    FPT   dividend           6
       material_lag1    FPT   earnings           5
       material_lag1    FPT legal_risk           1
       material_lag1    HPG    capital           7
       material_lag1    HPG   dividend           2
       material_lag1    HPG   earnings           4
       material_lag1    HPG legal_risk           4
       material_lag1    SSI    capital          27
       material_lag1    SSI   dividend           2
       material_lag1    SSI   earnings           1
       material_lag1    SSI legal_risk           2
       material_lag1    VCB    capital          26
       material_lag1    VCB   earnings           3
       material_lag1    VCB legal_risk           6
       material_lag1    VNM    capital           3
       material_lag1    VNM   dividend          11
       material_lag1    VNM   earnings           3
       material_lag1    VNM legal_risk           1
```