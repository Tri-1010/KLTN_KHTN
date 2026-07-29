# Focused material-event expansion

- tickers: SSI, VCB, HPG
- selected_candidates: 1193
- before_status: {'ok': 938, 'missing': 254, 'error': 1}
- returned_annotations: 1190
- ok_annotations: 1190
- material_annotations: 96
- direct_material_annotations: 83
- after_status: {'ok': 1191, 'error': 2}

## Best deltas

```text
                     variant horizon               model  Config_A  Config_Hybrid  Config_LLM  delta_hybrid_minus_A
            focused_material     10d Logistic_Regression    0.4486         0.5358      0.5311                0.0872
     focused_direct_material     10d Logistic_Regression    0.4486         0.5166      0.5120                0.0680
focused_direct_material_lag1     20d       Random_Forest    0.5233         0.5813      0.4379                0.0580
     focused_direct_material     20d       Random_Forest    0.5233         0.5804      0.4412                0.0571
       focused_material_lag1     10d Logistic_Regression    0.4486         0.4931      0.5153                0.0445
            focused_material     20d       Random_Forest    0.5233         0.5653      0.4619                0.0420
       focused_material_lag1     20d       Random_Forest    0.5233         0.5634      0.4613                0.0400
focused_direct_material_lag1     10d Logistic_Regression    0.4486         0.4862      0.4984                0.0376
            focused_material     10d       Random_Forest    0.5222         0.5504      0.5343                0.0282
       focused_material_lag1     10d       Random_Forest    0.5222         0.5435      0.5141                0.0213
     focused_direct_material     10d       Random_Forest    0.5222         0.5431      0.5270                0.0209
            focused_material      5d Logistic_Regression    0.5025         0.5215      0.5273                0.0189
focused_direct_material_lag1     10d       Random_Forest    0.5222         0.5391      0.5154                0.0169
       focused_material_lag1     20d Logistic_Regression    0.4979         0.5061      0.4850                0.0082
     focused_direct_material      5d Logistic_Regression    0.5025         0.5093      0.5191                0.0068
            focused_material     20d Logistic_Regression    0.4979         0.5006      0.4822                0.0027
       focused_material_lag1      5d Logistic_Regression    0.5025         0.5044      0.5287                0.0018
            focused_material      5d       Random_Forest    0.5366         0.5378      0.5077                0.0012
focused_direct_material_lag1      5d Logistic_Regression    0.5025         0.5020      0.5169               -0.0005
focused_direct_material_lag1      1d       Random_Forest    0.5254         0.5245      0.5039               -0.0009
```

## Material counts

```text
ticker event_type relevance_to_ticker  n_articles
   HPG    capital              direct          10
   HPG    capital            indirect           1
   HPG   dividend              direct           2
   HPG   earnings              direct           4
   HPG legal_risk              direct           9
   SSI    capital              direct          25
   SSI   dividend              direct           3
   SSI   earnings              direct           2
   SSI legal_risk              direct           2
   SSI legal_risk            indirect           1
   VCB    capital              direct          15
   VCB    capital            indirect           6
   VCB    capital          irrelevant           4
   VCB   dividend              direct           1
   VCB   earnings              direct           7
   VCB legal_risk              direct           3
   VCB legal_risk            indirect           1
```