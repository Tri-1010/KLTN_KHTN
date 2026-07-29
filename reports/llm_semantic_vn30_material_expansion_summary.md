# VN30 material-event semantic expansion

- universe: original VN30 (30 tickers)
- source annotations: `data/experiments/llm_semantic/focused_material_expanded_annotations_deepseek.csv`
- checkpoint_dir: `data/experiments/llm_semantic/vn30_material_eval/checkpoints`
- workers: 4
- horizons: 1d,5d,10d,20d,60d (20d ≈ 1 month, 60d ≈ 3 months)
- run_per_ticker: False
- ok_annotations_vn30: 2967
- material_annotations_vn30: 288
- direct_material_annotations_vn30: 279
- material_tickers: 30
- direct_material_tickers: 30

## Pooled original VN30 — best Hybrid vs Technical deltas

```text
                  variant horizon               model  n_test   ba_a  ba_hybrid  delta_hybrid_minus_a  delta_ci_low  delta_ci_high  p_mid    b    c
vn30_direct_material_lag1     60d       Random_Forest    6660 0.4924     0.5217                0.0293        0.0181         0.0408 0.0000  633  832
            vn30_material     60d       Random_Forest    6660 0.4924     0.5215                0.0291        0.0180         0.0401 0.0000  609  807
     vn30_direct_material     60d       Random_Forest    6660 0.4924     0.5202                0.0278        0.0175         0.0389 0.0000  642  830
       vn30_material_lag1     60d       Random_Forest    6660 0.4924     0.5193                0.0269        0.0152         0.0378 0.0000  631  811
vn30_direct_material_lag1      1d             XGBoost    7020 0.5056     0.5237                0.0182        0.0044         0.0318 0.0032 1184 1332
vn30_direct_material_lag1     10d Logistic_Regression    6960 0.4946     0.5114                0.0168        0.0081         0.0264 0.0002  472  592
            vn30_material     10d Logistic_Regression    6960 0.4946     0.5102                0.0156        0.0063         0.0243 0.0004  450  562
     vn30_direct_material     20d            LightGBM    6900 0.4981     0.5132                0.0151        0.0037         0.0269 0.0134  832  936
       vn30_material_lag1     10d             XGBoost    6960 0.5097     0.5245                0.0147        0.0020         0.0277 0.0231  995 1099
       vn30_material_lag1      1d             XGBoost    7020 0.5056     0.5193                0.0137       -0.0010         0.0269 0.0304 1190 1298
     vn30_direct_material     10d       Random_Forest    6960 0.5117     0.5251                0.0134        0.0025         0.0255 0.0230  773  865
vn30_direct_material_lag1     20d       Random_Forest    6900 0.5044     0.5166                0.0122        0.0006         0.0240 0.0373  790  875
     vn30_direct_material     10d Logistic_Regression    6960 0.4946     0.5067                0.0120        0.0026         0.0208 0.0058  454  541
     vn30_direct_material     20d       Random_Forest    6900 0.5044     0.5164                0.0119        0.0007         0.0237 0.0442  809  892
     vn30_direct_material      1d             XGBoost    7020 0.5056     0.5175                0.0119       -0.0018         0.0247 0.0672 1190 1281
vn30_direct_material_lag1     60d Logistic_Regression    6660 0.5112     0.5225                0.0113        0.0040         0.0185 0.0003  260  350
vn30_direct_material_lag1     10d       Random_Forest    6960 0.5117     0.5224                0.0107        0.0002         0.0223 0.0651  789  864
            vn30_material     60d Logistic_Regression    6660 0.5112     0.5213                0.0101        0.0024         0.0176 0.0013  275  356
vn30_direct_material_lag1     10d             XGBoost    6960 0.5097     0.5194                0.0097       -0.0030         0.0222 0.1475 1005 1071
     vn30_direct_material     60d Logistic_Regression    6660 0.5112     0.5206                0.0094        0.0018         0.0165 0.0019  263  339
       vn30_material_lag1     10d Logistic_Regression    6960 0.4946     0.5039                0.0093       -0.0006         0.0192 0.0429  514  581
       vn30_material_lag1     10d       Random_Forest    6960 0.5117     0.5203                0.0086       -0.0019         0.0206 0.1514  844  904
       vn30_material_lag1     60d Logistic_Regression    6660 0.5112     0.5196                0.0084        0.0014         0.0159 0.0031  261  333
            vn30_material     10d       Random_Forest    6960 0.5117     0.5201                0.0084       -0.0020         0.0208 0.1547  801  859
     vn30_direct_material      1d Logistic_Regression    7020 0.5157     0.5238                0.0080       -0.0016         0.0177 0.0054  512  605
       vn30_material_lag1     20d       Random_Forest    6900 0.5044     0.5118                0.0074       -0.0042         0.0202 0.2169  827  878
            vn30_material      1d Logistic_Regression    7020 0.5157     0.5228                0.0071       -0.0022         0.0168 0.0307  549  623
            vn30_material     10d            LightGBM    6960 0.5131     0.5201                0.0070       -0.0051         0.0192 0.2468  870  919
     vn30_direct_material     10d             XGBoost    6960 0.5097     0.5168                0.0070       -0.0059         0.0198 0.2740 1019 1069
     vn30_direct_material     60d             XGBoost    6660 0.5069     0.5138                0.0069       -0.0057         0.0193 0.1266  900  966
```

## All pooled deltas

```text
                  variant horizon               model  Config_A  Config_Hybrid  Config_LLM  delta_hybrid_minus_A
vn30_direct_material_lag1     60d       Random_Forest    0.4924         0.5217      0.5255                0.0293
            vn30_material     60d       Random_Forest    0.4924         0.5215      0.5233                0.0291
     vn30_direct_material     60d       Random_Forest    0.4924         0.5202      0.5263                0.0278
       vn30_material_lag1     60d       Random_Forest    0.4924         0.5193      0.5244                0.0269
vn30_direct_material_lag1      1d             XGBoost    0.5056         0.5237      0.5088                0.0182
vn30_direct_material_lag1     10d Logistic_Regression    0.4946         0.5114      0.4966                0.0168
            vn30_material     10d Logistic_Regression    0.4946         0.5102      0.4913                0.0156
     vn30_direct_material     20d            LightGBM    0.4981         0.5132      0.4934                0.0151
       vn30_material_lag1     10d             XGBoost    0.5097         0.5245      0.5026                0.0147
       vn30_material_lag1      1d             XGBoost    0.5056         0.5193      0.5137                0.0137
     vn30_direct_material     10d       Random_Forest    0.5117         0.5251      0.5086                0.0134
vn30_direct_material_lag1     20d       Random_Forest    0.5044         0.5166      0.4886                0.0122
     vn30_direct_material     10d Logistic_Regression    0.4946         0.5067      0.4969                0.0120
     vn30_direct_material     20d       Random_Forest    0.5044         0.5164      0.4881                0.0119
     vn30_direct_material      1d             XGBoost    0.5056         0.5175      0.5095                0.0119
vn30_direct_material_lag1     60d Logistic_Regression    0.5112         0.5225      0.4879                0.0113
vn30_direct_material_lag1     10d       Random_Forest    0.5117         0.5224      0.5142                0.0107
            vn30_material     60d Logistic_Regression    0.5112         0.5213      0.4953                0.0101
vn30_direct_material_lag1     10d             XGBoost    0.5097         0.5194      0.5137                0.0097
     vn30_direct_material     60d Logistic_Regression    0.5112         0.5206      0.4879                0.0094
       vn30_material_lag1     10d Logistic_Regression    0.4946         0.5039      0.4958                0.0093
       vn30_material_lag1     10d       Random_Forest    0.5117         0.5203      0.5116                0.0086
       vn30_material_lag1     60d Logistic_Regression    0.5112         0.5196      0.4940                0.0084
            vn30_material     10d       Random_Forest    0.5117         0.5201      0.5047                0.0084
     vn30_direct_material      1d Logistic_Regression    0.5157         0.5238      0.5038                0.0080
       vn30_material_lag1     20d       Random_Forest    0.5044         0.5118      0.4854                0.0074
            vn30_material      1d Logistic_Regression    0.5157         0.5228      0.5021                0.0071
            vn30_material     10d            LightGBM    0.5131         0.5201      0.5063                0.0070
     vn30_direct_material     10d             XGBoost    0.5097         0.5168      0.5090                0.0070
     vn30_direct_material     60d             XGBoost    0.5069         0.5138      0.5302                0.0069
       vn30_material_lag1      1d            LightGBM    0.5209         0.5275      0.5131                0.0066
     vn30_direct_material      1d            LightGBM    0.5209         0.5275      0.5047                0.0066
vn30_direct_material_lag1     60d             XGBoost    0.5069         0.5132      0.5187                0.0063
vn30_direct_material_lag1      5d       Random_Forest    0.5170         0.5218      0.4987                0.0048
       vn30_material_lag1     20d            LightGBM    0.4981         0.5026      0.4920                0.0045
       vn30_material_lag1      1d Logistic_Regression    0.5157         0.5202      0.5002                0.0044
vn30_direct_material_lag1     10d            LightGBM    0.5131         0.5175      0.5146                0.0044
            vn30_material     20d            LightGBM    0.4981         0.5024      0.4976                0.0043
vn30_direct_material_lag1      1d Logistic_Regression    0.5157         0.5200      0.5011                0.0042
vn30_direct_material_lag1     20d            LightGBM    0.4981         0.5022      0.4931                0.0042
     vn30_direct_material     20d Logistic_Regression    0.4906         0.4945      0.4994                0.0039
       vn30_material_lag1      5d             XGBoost    0.5214         0.5249      0.4945                0.0034
       vn30_material_lag1      1d       Random_Forest    0.5209         0.5239      0.5154                0.0030
            vn30_material     20d       Random_Forest    0.5044         0.5071      0.4840                0.0027
       vn30_material_lag1      5d            LightGBM    0.5204         0.5225      0.4966                0.0022
            vn30_material      1d             XGBoost    0.5056         0.5075      0.5104                0.0020
     vn30_direct_material      5d       Random_Forest    0.5170         0.5188      0.5018                0.0019
vn30_direct_material_lag1      1d            LightGBM    0.5209         0.5226      0.5071                0.0017
       vn30_material_lag1      5d       Random_Forest    0.5170         0.5185      0.4975                0.0016
            vn30_material      5d       Random_Forest    0.5170         0.5182      0.4988                0.0013
            vn30_material     20d Logistic_Regression    0.4906         0.4914      0.4943                0.0008
       vn30_material_lag1     60d             XGBoost    0.5069         0.5077      0.5169                0.0008
            vn30_material     60d             XGBoost    0.5069         0.5075      0.5258                0.0006
            vn30_material      1d            LightGBM    0.5209         0.5214      0.5048                0.0006
            vn30_material      5d            LightGBM    0.5204         0.5208      0.4971                0.0004
       vn30_material_lag1     20d Logistic_Regression    0.4906         0.4907      0.4988                0.0001
vn30_direct_material_lag1     20d Logistic_Regression    0.4906         0.4906      0.4889                0.0000
       vn30_material_lag1     10d            LightGBM    0.5131         0.5126      0.5109               -0.0005
     vn30_direct_material      1d       Random_Forest    0.5209         0.5178      0.5094               -0.0031
vn30_direct_material_lag1      5d            LightGBM    0.5204         0.5172      0.4928               -0.0032
            vn30_material     10d             XGBoost    0.5097         0.5062      0.5039               -0.0035
       vn30_material_lag1     60d            LightGBM    0.5219         0.5178      0.5190               -0.0041
vn30_direct_material_lag1      5d             XGBoost    0.5214         0.5171      0.4988               -0.0043
     vn30_direct_material      5d            LightGBM    0.5204         0.5148      0.4965               -0.0056
     vn30_direct_material     10d            LightGBM    0.5131         0.5067      0.5074               -0.0064
     vn30_direct_material      5d Logistic_Regression    0.5067         0.5001      0.4898               -0.0066
            vn30_material     20d             XGBoost    0.5118         0.5051      0.4980               -0.0067
     vn30_direct_material     20d             XGBoost    0.5118         0.5051      0.4999               -0.0067
vn30_direct_material_lag1      1d       Random_Forest    0.5209         0.5134      0.5112               -0.0075
            vn30_material      5d             XGBoost    0.5214         0.5137      0.4988               -0.0077
            vn30_material      5d Logistic_Regression    0.5067         0.4979      0.4928               -0.0088
       vn30_material_lag1      5d Logistic_Regression    0.5067         0.4977      0.4925               -0.0090
vn30_direct_material_lag1      5d Logistic_Regression    0.5067         0.4971      0.4894               -0.0096
     vn30_direct_material     60d            LightGBM    0.5219         0.5113      0.5212               -0.0106
     vn30_direct_material      5d             XGBoost    0.5214         0.5105      0.5010               -0.0110
       vn30_material_lag1     20d             XGBoost    0.5118         0.4999      0.4858               -0.0119
            vn30_material      1d       Random_Forest    0.5209         0.5077      0.5086               -0.0132
vn30_direct_material_lag1     20d             XGBoost    0.5118         0.4979      0.4866               -0.0139
vn30_direct_material_lag1     60d            LightGBM    0.5219         0.5072      0.5207               -0.0147
            vn30_material     60d            LightGBM    0.5219         0.5048      0.5216               -0.0171
```
