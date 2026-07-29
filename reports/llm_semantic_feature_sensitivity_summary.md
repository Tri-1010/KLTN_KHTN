# LLM semantic feature sensitivity summary

- selected_articles: 2000
- ok_annotations: 1991
- direct_annotations: 1685
- material_annotations: 137
- direct_material_annotations: 121

## Best hybrid deltas

```text
                variant horizon               model  Config_A  Config_Hybrid  Config_LLM  delta_hybrid_minus_A
   material_events_only     20d       Random_Forest    0.5025         0.5343      0.4922                0.0318
   direct_material_only     10d       Random_Forest    0.4905         0.5216      0.5147                0.0310
   material_events_only      5d       Random_Forest    0.5149         0.5408      0.5222                0.0259
   material_events_only     10d       Random_Forest    0.4905         0.5159      0.5108                0.0254
   material_events_only      1d Logistic_Regression    0.5150         0.5381      0.5087                0.0230
   direct_material_only     20d       Random_Forest    0.5025         0.5238      0.4914                0.0212
   direct_material_only      1d       Random_Forest    0.5100         0.5296      0.4859                0.0196
          material_lag1      1d       Random_Forest    0.5100         0.5280      0.5000                0.0180
   material_events_only      1d       Random_Forest    0.5100         0.5257      0.4915                0.0157
   direct_material_only     10d Logistic_Regression    0.4527         0.4681      0.4931                0.0154
          material_lag1     10d Logistic_Regression    0.4527         0.4679      0.5157                0.0152
   direct_material_only      1d Logistic_Regression    0.5150         0.5302      0.4883                0.0151
   direct_material_lag1     10d Logistic_Regression    0.4527         0.4678      0.4737                0.0150
          relevant_lag1      1d       Random_Forest    0.5100         0.5246      0.4808                0.0147
          material_lag1      1d Logistic_Regression    0.5150         0.5290      0.5121                0.0139
            direct_only      1d Logistic_Regression    0.5150         0.5257      0.4915                0.0106
   material_events_only     10d Logistic_Regression    0.4527         0.4633      0.5263                0.0105
            direct_lag1     20d       Random_Forest    0.5025         0.5129      0.4642                0.0104
relevant_non_irrelevant      1d       Random_Forest    0.5100         0.5192      0.4839                0.0092
   direct_material_lag1     10d       Random_Forest    0.4905         0.4989      0.4899                0.0083
```

## Worst hybrid deltas

```text
                variant horizon               model  Config_A  Config_Hybrid  Config_LLM  delta_hybrid_minus_A
          relevant_lag1     10d       Random_Forest    0.4905         0.4739      0.4916               -0.0167
          relevant_lag1      5d       Random_Forest    0.5149         0.4977      0.4865               -0.0172
relevant_non_irrelevant      5d       Random_Forest    0.5149         0.4972      0.5023               -0.0177
relevant_non_irrelevant      5d Logistic_Regression    0.4853         0.4643      0.4890               -0.0210
            direct_only     10d       Random_Forest    0.4905         0.4694      0.4846               -0.0211
          relevant_lag1      1d Logistic_Regression    0.5150         0.4929      0.5061               -0.0222
relevant_non_irrelevant     10d       Random_Forest    0.4905         0.4681      0.4961               -0.0225
          material_lag1      5d Logistic_Regression    0.4853         0.4599      0.5178               -0.0254
   direct_material_only     20d Logistic_Regression    0.5096         0.4834      0.5520               -0.0262
            direct_only      5d       Random_Forest    0.5149         0.4879      0.4673               -0.0270
   material_events_only      5d Logistic_Regression    0.4853         0.4582      0.5186               -0.0271
   direct_material_only      5d Logistic_Regression    0.4853         0.4579      0.4967               -0.0275
            direct_only      5d Logistic_Regression    0.4853         0.4562      0.4717               -0.0291
            direct_lag1     10d       Random_Forest    0.4905         0.4613      0.4627               -0.0293
   direct_material_lag1     20d Logistic_Regression    0.5096         0.4708      0.5500               -0.0388
            direct_lag1      5d       Random_Forest    0.5149         0.4746      0.4760               -0.0403
            direct_only     20d Logistic_Regression    0.5096         0.4648      0.4490               -0.0449
            direct_lag1     20d Logistic_Regression    0.5096         0.4619      0.4525               -0.0477
relevant_non_irrelevant     20d Logistic_Regression    0.5096         0.4562      0.4560               -0.0534
          relevant_lag1     20d Logistic_Regression    0.5096         0.4553      0.4435               -0.0544
```

## Best per-ticker hybrid deltas

```text
                           variant ticker horizon               model  Config_A  Config_Hybrid  Config_LLM  delta_hybrid_minus_A
          material_lag1_per_ticker    SSI     10d       Random_Forest    0.4369         0.5997      0.4738                0.1628
   direct_material_lag1_per_ticker    SSI     10d       Random_Forest    0.4369         0.5997      0.4738                0.1628
   material_events_only_per_ticker    SSI     10d       Random_Forest    0.4369         0.5979      0.5223                0.1610
   direct_material_only_per_ticker    SSI     10d       Random_Forest    0.4369         0.5979      0.5223                0.1610
            direct_only_per_ticker    SSI     10d       Random_Forest    0.4369         0.5318      0.5232                0.0949
            direct_only_per_ticker    FPT      1d       Random_Forest    0.5072         0.5957      0.5218                0.0885
relevant_non_irrelevant_per_ticker    SSI     10d       Random_Forest    0.4369         0.5190      0.5232                0.0821
          relevant_lag1_per_ticker    SSI     10d       Random_Forest    0.4369         0.5155      0.5182                0.0786
            direct_lag1_per_ticker    SSI     20d Logistic_Regression    0.5436         0.6214      0.5405                0.0778
relevant_non_irrelevant_per_ticker    SSI     20d Logistic_Regression    0.5436         0.6163      0.5285                0.0728
   direct_material_lag1_per_ticker    VCB     10d Logistic_Regression    0.5322         0.6042      0.6183                0.0720
            direct_lag1_per_ticker    SSI     10d       Random_Forest    0.4369         0.5080      0.5057                0.0711
            direct_only_per_ticker    SSI     20d       Random_Forest    0.4935         0.5605      0.4794                0.0670
          relevant_lag1_per_ticker    SSI     20d Logistic_Regression    0.5436         0.6104      0.5446                0.0668
   direct_material_lag1_per_ticker    VCB     10d       Random_Forest    0.5248         0.5910      0.5873                0.0662
relevant_non_irrelevant_per_ticker    HPG      5d Logistic_Regression    0.5000         0.5652      0.4922                0.0652
          material_lag1_per_ticker    HPG     10d       Random_Forest    0.5190         0.5828      0.5058                0.0637
   direct_material_only_per_ticker    VCB     10d       Random_Forest    0.5248         0.5885      0.6002                0.0637
   material_events_only_per_ticker    HPG      5d       Random_Forest    0.5572         0.6175      0.5576                0.0603
relevant_non_irrelevant_per_ticker    VCB     10d Logistic_Regression    0.5322         0.5922      0.5460                0.0600
```