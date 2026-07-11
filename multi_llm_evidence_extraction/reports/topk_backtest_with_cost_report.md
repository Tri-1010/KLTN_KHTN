# Top-K backtest with turnover cost

Secondary exploratory simulation using non-overlapping OOS T+20 periods; not investment recommendation.

## Summary

| config | model | top_k | strategy | periods | cumulative_net_return | mean_net_return | mean_net_excess_return | annualized_sharpe | annualization_factor | max_drawdown | hit_rate | avg_turnover | holding_period_days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A_technical | LogisticRegression | 5 | equal_weight_universe | 54 | 0.3115 | 0.0073 | 0.0022 | 0.3847 | 3.5496 | -0.391 | 0.5926 | 0.019 | 20 |
| A_technical | LogisticRegression | 5 | model_topk | 54 | -0.1432 | 0.0002 | -0.0049 | 0.0099 | 3.5496 | -0.3984 | 0.4815 | 0.3185 | 20 |
| A_technical | LogisticRegression | 5 | random_topk_deterministic | 54 | -0.4022 | -0.007 | -0.0121 | -0.3601 | 3.5496 | -0.5156 | 0.5185 | 0.9296 | 20 |
| A_technical | LogisticRegression | 10 | equal_weight_universe | 54 | 0.3115 | 0.0073 | 0.0022 | 0.3847 | 3.5496 | -0.391 | 0.5926 | 0.019 | 20 |
| A_technical | LogisticRegression | 10 | model_topk | 54 | 0.3267 | 0.0073 | 0.0022 | 0.4005 | 3.5496 | -0.2731 | 0.537 | 0.3 | 20 |
| A_technical | LogisticRegression | 10 | random_topk_deterministic | 54 | 0.2148 | 0.0063 | 0.0012 | 0.3065 | 3.5496 | -0.4152 | 0.5556 | 0.8852 | 20 |
| A_technical | RandomForest | 5 | equal_weight_universe | 54 | 0.3115 | 0.0073 | 0.0022 | 0.3847 | 3.5496 | -0.391 | 0.5926 | 0.019 | 20 |
| A_technical | RandomForest | 5 | model_topk | 54 | 0.4249 | 0.0087 | 0.0036 | 0.469 | 3.5496 | -0.3374 | 0.6296 | 0.3185 | 20 |
| A_technical | RandomForest | 5 | random_topk_deterministic | 54 | -0.4022 | -0.007 | -0.0121 | -0.3601 | 3.5496 | -0.5156 | 0.5185 | 0.9296 | 20 |
| A_technical | RandomForest | 10 | equal_weight_universe | 54 | 0.3115 | 0.0073 | 0.0022 | 0.3847 | 3.5496 | -0.391 | 0.5926 | 0.019 | 20 |
| A_technical | RandomForest | 10 | model_topk | 54 | 0.431 | 0.0085 | 0.0034 | 0.4893 | 3.5496 | -0.3307 | 0.5926 | 0.2889 | 20 |
| A_technical | RandomForest | 10 | random_topk_deterministic | 54 | 0.2148 | 0.0063 | 0.0012 | 0.3065 | 3.5496 | -0.4152 | 0.5556 | 0.8852 | 20 |
| B_technical_keyword | LogisticRegression | 5 | equal_weight_universe | 54 | 0.3115 | 0.0073 | 0.0022 | 0.3847 | 3.5496 | -0.391 | 0.5926 | 0.019 | 20 |
| B_technical_keyword | LogisticRegression | 5 | model_topk | 54 | 0.1966 | 0.0063 | 0.0012 | 0.2903 | 3.5496 | -0.3984 | 0.5926 | 0.3 | 20 |
| B_technical_keyword | LogisticRegression | 5 | random_topk_deterministic | 54 | -0.4022 | -0.007 | -0.0121 | -0.3601 | 3.5496 | -0.5156 | 0.5185 | 0.9296 | 20 |
| B_technical_keyword | LogisticRegression | 10 | equal_weight_universe | 54 | 0.3115 | 0.0073 | 0.0022 | 0.3847 | 3.5496 | -0.391 | 0.5926 | 0.019 | 20 |
| B_technical_keyword | LogisticRegression | 10 | model_topk | 54 | 0.5847 | 0.0107 | 0.0056 | 0.5732 | 3.5496 | -0.2731 | 0.5741 | 0.2685 | 20 |
| B_technical_keyword | LogisticRegression | 10 | random_topk_deterministic | 54 | 0.2148 | 0.0063 | 0.0012 | 0.3065 | 3.5496 | -0.4152 | 0.5556 | 0.8852 | 20 |
| B_technical_keyword | RandomForest | 5 | equal_weight_universe | 54 | 0.3115 | 0.0073 | 0.0022 | 0.3847 | 3.5496 | -0.391 | 0.5926 | 0.019 | 20 |
| B_technical_keyword | RandomForest | 5 | model_topk | 54 | -0.0175 | 0.0015 | -0.0036 | 0.0878 | 3.5496 | -0.3374 | 0.5556 | 0.3148 | 20 |
| B_technical_keyword | RandomForest | 5 | random_topk_deterministic | 54 | -0.4022 | -0.007 | -0.0121 | -0.3601 | 3.5496 | -0.5156 | 0.5185 | 0.9296 | 20 |
| B_technical_keyword | RandomForest | 10 | equal_weight_universe | 54 | 0.3115 | 0.0073 | 0.0022 | 0.3847 | 3.5496 | -0.391 | 0.5926 | 0.019 | 20 |
| B_technical_keyword | RandomForest | 10 | model_topk | 54 | 0.3737 | 0.0079 | 0.0028 | 0.439 | 3.5496 | -0.3307 | 0.5741 | 0.2852 | 20 |
| B_technical_keyword | RandomForest | 10 | random_topk_deterministic | 54 | 0.2148 | 0.0063 | 0.0012 | 0.3065 | 3.5496 | -0.4152 | 0.5556 | 0.8852 | 20 |
| C_technical_semantic | LogisticRegression | 5 | equal_weight_universe | 54 | 0.3115 | 0.0073 | 0.0022 | 0.3847 | 3.5496 | -0.391 | 0.5926 | 0.019 | 20 |
| C_technical_semantic | LogisticRegression | 5 | model_topk | 54 | 0.125 | 0.005 | -0.0001 | 0.2347 | 3.5496 | -0.3571 | 0.5741 | 0.4111 | 20 |
| C_technical_semantic | LogisticRegression | 5 | random_topk_deterministic | 54 | -0.4022 | -0.007 | -0.0121 | -0.3601 | 3.5496 | -0.5156 | 0.5185 | 0.9296 | 20 |
| C_technical_semantic | LogisticRegression | 10 | equal_weight_universe | 54 | 0.3115 | 0.0073 | 0.0022 | 0.3847 | 3.5496 | -0.391 | 0.5926 | 0.019 | 20 |
| C_technical_semantic | LogisticRegression | 10 | model_topk | 54 | 0.3156 | 0.007 | 0.0019 | 0.3999 | 3.5496 | -0.2416 | 0.5185 | 0.3537 | 20 |
| C_technical_semantic | LogisticRegression | 10 | random_topk_deterministic | 54 | 0.2148 | 0.0063 | 0.0012 | 0.3065 | 3.5496 | -0.4152 | 0.5556 | 0.8852 | 20 |
| C_technical_semantic | RandomForest | 5 | equal_weight_universe | 54 | 0.3115 | 0.0073 | 0.0022 | 0.3847 | 3.5496 | -0.391 | 0.5926 | 0.019 | 20 |
| C_technical_semantic | RandomForest | 5 | model_topk | 54 | 0.1354 | 0.0044 | -0.0007 | 0.241 | 3.5496 | -0.2686 | 0.537 | 0.4407 | 20 |
| C_technical_semantic | RandomForest | 5 | random_topk_deterministic | 54 | -0.4022 | -0.007 | -0.0121 | -0.3601 | 3.5496 | -0.5156 | 0.5185 | 0.9296 | 20 |
| C_technical_semantic | RandomForest | 10 | equal_weight_universe | 54 | 0.3115 | 0.0073 | 0.0022 | 0.3847 | 3.5496 | -0.391 | 0.5926 | 0.019 | 20 |
| C_technical_semantic | RandomForest | 10 | model_topk | 54 | 0.2201 | 0.0056 | 0.0005 | 0.3197 | 3.5496 | -0.3218 | 0.5185 | 0.3519 | 20 |
| C_technical_semantic | RandomForest | 10 | random_topk_deterministic | 54 | 0.2148 | 0.0063 | 0.0012 | 0.3065 | 3.5496 | -0.4152 | 0.5556 | 0.8852 | 20 |
| D_all | LogisticRegression | 5 | equal_weight_universe | 54 | 0.3115 | 0.0073 | 0.0022 | 0.3847 | 3.5496 | -0.391 | 0.5926 | 0.019 | 20 |
| D_all | LogisticRegression | 5 | model_topk | 54 | 0.394 | 0.009 | 0.0039 | 0.4231 | 3.5496 | -0.3571 | 0.6296 | 0.3444 | 20 |
| D_all | LogisticRegression | 5 | random_topk_deterministic | 54 | -0.4022 | -0.007 | -0.0121 | -0.3601 | 3.5496 | -0.5156 | 0.5185 | 0.9296 | 20 |
| D_all | LogisticRegression | 10 | equal_weight_universe | 54 | 0.3115 | 0.0073 | 0.0022 | 0.3847 | 3.5496 | -0.391 | 0.5926 | 0.019 | 20 |
| D_all | LogisticRegression | 10 | model_topk | 54 | 0.7613 | 0.0128 | 0.0077 | 0.6669 | 3.5496 | -0.2416 | 0.5926 | 0.2778 | 20 |
| D_all | LogisticRegression | 10 | random_topk_deterministic | 54 | 0.2148 | 0.0063 | 0.0012 | 0.3065 | 3.5496 | -0.4152 | 0.5556 | 0.8852 | 20 |
| D_all | RandomForest | 5 | equal_weight_universe | 54 | 0.3115 | 0.0073 | 0.0022 | 0.3847 | 3.5496 | -0.391 | 0.5926 | 0.019 | 20 |
| D_all | RandomForest | 5 | model_topk | 54 | 0.3253 | 0.0072 | 0.0021 | 0.4024 | 3.5496 | -0.2686 | 0.5556 | 0.3667 | 20 |
| D_all | RandomForest | 5 | random_topk_deterministic | 54 | -0.4022 | -0.007 | -0.0121 | -0.3601 | 3.5496 | -0.5156 | 0.5185 | 0.9296 | 20 |
| D_all | RandomForest | 10 | equal_weight_universe | 54 | 0.3115 | 0.0073 | 0.0022 | 0.3847 | 3.5496 | -0.391 | 0.5926 | 0.019 | 20 |
| D_all | RandomForest | 10 | model_topk | 54 | 0.3134 | 0.0071 | 0.002 | 0.3906 | 3.5496 | -0.3218 | 0.537 | 0.3111 | 20 |
| D_all | RandomForest | 10 | random_topk_deterministic | 54 | 0.2148 | 0.0063 | 0.0012 | 0.3065 | 3.5496 | -0.4152 | 0.5556 | 0.8852 | 20 |

