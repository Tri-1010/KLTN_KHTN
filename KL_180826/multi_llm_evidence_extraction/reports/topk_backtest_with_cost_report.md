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

## Deterministic random-null distribution

| artifact_schema_version | config | model | top_k | draws | periods | model_cumulative_net_return | null_cumulative_net_return_mean | null_cumulative_net_return_std | null_cumulative_net_return_p05 | null_cumulative_net_return_p50 | null_cumulative_net_return_p95 | model_percentile_vs_null | one_sided_null_p_value | null_mean_net_return_mean | null_mean_net_return_std | null_mean_net_excess_return_mean | null_mean_net_excess_return_std | round_trip_cost_rate | holding_period_days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| topk_random_null_summary_v1 | A_technical | LogisticRegression | 5 | 200 | 54 | -0.1432 | 0.0565 | 0.2994 | -0.3442 | 0.0098 | 0.5226 | 0.28 | 0.7214 | 0.0033 | 0.0051 | -0.0018 | 0.0051 | 0.005 | 20 |
| topk_random_null_summary_v1 | A_technical | LogisticRegression | 10 | 200 | 54 | 0.3267 | 0.0393 | 0.201 | -0.2441 | 0.0245 | 0.3737 | 0.905 | 0.0995 | 0.003 | 0.0035 | -0.0021 | 0.0035 | 0.005 | 20 |
| topk_random_null_summary_v1 | A_technical | RandomForest | 5 | 200 | 54 | 0.4249 | 0.0565 | 0.2994 | -0.3442 | 0.0098 | 0.5226 | 0.87 | 0.1343 | 0.0033 | 0.0051 | -0.0018 | 0.0051 | 0.005 | 20 |
| topk_random_null_summary_v1 | A_technical | RandomForest | 10 | 200 | 54 | 0.431 | 0.0393 | 0.201 | -0.2441 | 0.0245 | 0.3737 | 0.965 | 0.0398 | 0.003 | 0.0035 | -0.0021 | 0.0035 | 0.005 | 20 |
| topk_random_null_summary_v1 | B_technical_keyword | LogisticRegression | 5 | 200 | 54 | 0.1966 | 0.0565 | 0.2994 | -0.3442 | 0.0098 | 0.5226 | 0.68 | 0.3234 | 0.0033 | 0.0051 | -0.0018 | 0.0051 | 0.005 | 20 |
| topk_random_null_summary_v1 | B_technical_keyword | LogisticRegression | 10 | 200 | 54 | 0.5847 | 0.0393 | 0.201 | -0.2441 | 0.0245 | 0.3737 | 0.995 | 0.01 | 0.003 | 0.0035 | -0.0021 | 0.0035 | 0.005 | 20 |
| topk_random_null_summary_v1 | B_technical_keyword | RandomForest | 5 | 200 | 54 | -0.0175 | 0.0565 | 0.2994 | -0.3442 | 0.0098 | 0.5226 | 0.455 | 0.5473 | 0.0033 | 0.0051 | -0.0018 | 0.0051 | 0.005 | 20 |
| topk_random_null_summary_v1 | B_technical_keyword | RandomForest | 10 | 200 | 54 | 0.3737 | 0.0393 | 0.201 | -0.2441 | 0.0245 | 0.3737 | 0.95 | 0.0547 | 0.003 | 0.0035 | -0.0021 | 0.0035 | 0.005 | 20 |
| topk_random_null_summary_v1 | C_technical_semantic | LogisticRegression | 5 | 200 | 54 | 0.125 | 0.0565 | 0.2994 | -0.3442 | 0.0098 | 0.5226 | 0.63 | 0.3731 | 0.0033 | 0.0051 | -0.0018 | 0.0051 | 0.005 | 20 |
| topk_random_null_summary_v1 | C_technical_semantic | LogisticRegression | 10 | 200 | 54 | 0.3156 | 0.0393 | 0.201 | -0.2441 | 0.0245 | 0.3737 | 0.9 | 0.1045 | 0.003 | 0.0035 | -0.0021 | 0.0035 | 0.005 | 20 |
| topk_random_null_summary_v1 | C_technical_semantic | RandomForest | 5 | 200 | 54 | 0.1354 | 0.0565 | 0.2994 | -0.3442 | 0.0098 | 0.5226 | 0.64 | 0.3632 | 0.0033 | 0.0051 | -0.0018 | 0.0051 | 0.005 | 20 |
| topk_random_null_summary_v1 | C_technical_semantic | RandomForest | 10 | 200 | 54 | 0.2201 | 0.0393 | 0.201 | -0.2441 | 0.0245 | 0.3737 | 0.825 | 0.1791 | 0.003 | 0.0035 | -0.0021 | 0.0035 | 0.005 | 20 |
| topk_random_null_summary_v1 | D_all | LogisticRegression | 5 | 200 | 54 | 0.394 | 0.0565 | 0.2994 | -0.3442 | 0.0098 | 0.5226 | 0.845 | 0.1592 | 0.0033 | 0.0051 | -0.0018 | 0.0051 | 0.005 | 20 |
| topk_random_null_summary_v1 | D_all | LogisticRegression | 10 | 200 | 54 | 0.7613 | 0.0393 | 0.201 | -0.2441 | 0.0245 | 0.3737 | 0.995 | 0.01 | 0.003 | 0.0035 | -0.0021 | 0.0035 | 0.005 | 20 |
| topk_random_null_summary_v1 | D_all | RandomForest | 5 | 200 | 54 | 0.3253 | 0.0565 | 0.2994 | -0.3442 | 0.0098 | 0.5226 | 0.815 | 0.1891 | 0.0033 | 0.0051 | -0.0018 | 0.0051 | 0.005 | 20 |
| topk_random_null_summary_v1 | D_all | RandomForest | 10 | 200 | 54 | 0.3134 | 0.0393 | 0.201 | -0.2441 | 0.0245 | 0.3737 | 0.9 | 0.1045 | 0.003 | 0.0035 | -0.0021 | 0.0035 | 0.005 | 20 |

Limitation: deterministic hash draws are a reproducible empirical null, not independent market realizations; overlapping names and limited OOS periods reduce inferential strength. Draw-level results are intentionally not stored.

## Cost sensitivity

| artifact_schema_version | config | model | top_k | strategy | round_trip_cost_rate | periods | cumulative_net_return | mean_net_return | mean_net_excess_return | annualized_sharpe | annualization_factor | max_drawdown | hit_rate | avg_turnover | holding_period_days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| topk_cost_sensitivity_v1 | A_technical | LogisticRegression | 5 | model_topk | 0.0 | 54 | -0.0646 | 0.0018 | -0.0033 | 0.0815 | 3.5496 | -0.3877 | 0.5 | 0.3185 | 20 |
| topk_cost_sensitivity_v1 | A_technical | LogisticRegression | 10 | model_topk | 0.0 | 54 | 0.4395 | 0.0088 | 0.0037 | 0.4847 | 3.5496 | -0.2633 | 0.537 | 0.3 | 20 |
| topk_cost_sensitivity_v1 | A_technical | RandomForest | 5 | model_topk | 0.0 | 54 | 0.5547 | 0.0103 | 0.0052 | 0.5589 | 3.5496 | -0.3279 | 0.6481 | 0.3185 | 20 |
| topk_cost_sensitivity_v1 | A_technical | RandomForest | 10 | model_topk | 0.0 | 54 | 0.5478 | 0.01 | 0.0049 | 0.5746 | 3.5496 | -0.3236 | 0.5926 | 0.2889 | 20 |
| topk_cost_sensitivity_v1 | B_technical_keyword | LogisticRegression | 5 | model_topk | 0.0 | 54 | 0.2989 | 0.0078 | 0.0027 | 0.3608 | 3.5496 | -0.3877 | 0.5926 | 0.3 | 20 |
| topk_cost_sensitivity_v1 | B_technical_keyword | LogisticRegression | 10 | model_topk | 0.0 | 54 | 0.7042 | 0.0121 | 0.007 | 0.6468 | 3.5496 | -0.2633 | 0.5741 | 0.2685 | 20 |
| topk_cost_sensitivity_v1 | B_technical_keyword | RandomForest | 5 | model_topk | 0.0 | 54 | 0.0714 | 0.0031 | -0.002 | 0.1819 | 3.5496 | -0.3279 | 0.5556 | 0.3148 | 20 |
| topk_cost_sensitivity_v1 | B_technical_keyword | RandomForest | 10 | model_topk | 0.0 | 54 | 0.485 | 0.0093 | 0.0043 | 0.5209 | 3.5496 | -0.3236 | 0.5741 | 0.2852 | 20 |
| topk_cost_sensitivity_v1 | C_technical_semantic | LogisticRegression | 5 | model_topk | 0.0 | 54 | 0.2582 | 0.007 | 0.0019 | 0.3331 | 3.5496 | -0.3445 | 0.5926 | 0.4111 | 20 |
| topk_cost_sensitivity_v1 | C_technical_semantic | LogisticRegression | 10 | model_topk | 0.0 | 54 | 0.448 | 0.0087 | 0.0036 | 0.5033 | 3.5496 | -0.2306 | 0.537 | 0.3537 | 20 |
| topk_cost_sensitivity_v1 | C_technical_semantic | RandomForest | 5 | model_topk | 0.0 | 54 | 0.2785 | 0.0066 | 0.0015 | 0.3611 | 3.5496 | -0.2583 | 0.5926 | 0.4407 | 20 |
| topk_cost_sensitivity_v1 | C_technical_semantic | RandomForest | 10 | model_topk | 0.0 | 54 | 0.3419 | 0.0073 | 0.0023 | 0.4211 | 3.5496 | -0.3129 | 0.5185 | 0.3519 | 20 |
| topk_cost_sensitivity_v1 | D_all | LogisticRegression | 5 | model_topk | 0.0 | 54 | 0.5309 | 0.0107 | 0.0056 | 0.5057 | 3.5496 | -0.3445 | 0.6296 | 0.3444 | 20 |
| topk_cost_sensitivity_v1 | D_all | LogisticRegression | 10 | model_topk | 0.0 | 54 | 0.8984 | 0.0142 | 0.0091 | 0.7409 | 3.5496 | -0.2306 | 0.5926 | 0.2778 | 20 |
| topk_cost_sensitivity_v1 | D_all | RandomForest | 5 | model_topk | 0.0 | 54 | 0.4644 | 0.009 | 0.0039 | 0.5082 | 3.5496 | -0.2583 | 0.5741 | 0.3667 | 20 |
| topk_cost_sensitivity_v1 | D_all | RandomForest | 10 | model_topk | 0.0 | 54 | 0.4296 | 0.0086 | 0.0035 | 0.4785 | 3.5496 | -0.3129 | 0.5556 | 0.3111 | 20 |
| topk_cost_sensitivity_v1 | A_technical | LogisticRegression | 5 | model_topk | 0.0025 | 54 | -0.1047 | 0.001 | -0.0041 | 0.0457 | 3.5496 | -0.393 | 0.5 | 0.3185 | 20 |
| topk_cost_sensitivity_v1 | A_technical | LogisticRegression | 10 | model_topk | 0.0025 | 54 | 0.382 | 0.008 | 0.0029 | 0.4426 | 3.5496 | -0.2682 | 0.537 | 0.3 | 20 |
| topk_cost_sensitivity_v1 | A_technical | RandomForest | 5 | model_topk | 0.0025 | 54 | 0.4884 | 0.0095 | 0.0044 | 0.5139 | 3.5496 | -0.3327 | 0.6481 | 0.3185 | 20 |
| topk_cost_sensitivity_v1 | A_technical | RandomForest | 10 | model_topk | 0.0025 | 54 | 0.4884 | 0.0093 | 0.0042 | 0.5319 | 3.5496 | -0.3272 | 0.5926 | 0.2889 | 20 |
| topk_cost_sensitivity_v1 | B_technical_keyword | LogisticRegression | 5 | model_topk | 0.0025 | 54 | 0.2468 | 0.007 | 0.0019 | 0.3255 | 3.5496 | -0.393 | 0.5926 | 0.3 | 20 |
| topk_cost_sensitivity_v1 | B_technical_keyword | LogisticRegression | 10 | model_topk | 0.0025 | 54 | 0.6434 | 0.0114 | 0.0063 | 0.61 | 3.5496 | -0.2682 | 0.5741 | 0.2685 | 20 |
| topk_cost_sensitivity_v1 | B_technical_keyword | RandomForest | 5 | model_topk | 0.0025 | 54 | 0.026 | 0.0023 | -0.0028 | 0.1347 | 3.5496 | -0.3327 | 0.5556 | 0.3148 | 20 |
| topk_cost_sensitivity_v1 | B_technical_keyword | RandomForest | 10 | model_topk | 0.0025 | 54 | 0.4283 | 0.0086 | 0.0035 | 0.4799 | 3.5496 | -0.3272 | 0.5741 | 0.2852 | 20 |
| topk_cost_sensitivity_v1 | C_technical_semantic | LogisticRegression | 5 | model_topk | 0.0025 | 54 | 0.1898 | 0.006 | 0.0009 | 0.2839 | 3.5496 | -0.3508 | 0.5741 | 0.4111 | 20 |
| topk_cost_sensitivity_v1 | C_technical_semantic | LogisticRegression | 10 | model_topk | 0.0025 | 54 | 0.3803 | 0.0078 | 0.0028 | 0.4515 | 3.5496 | -0.2361 | 0.5185 | 0.3537 | 20 |
| topk_cost_sensitivity_v1 | C_technical_semantic | RandomForest | 5 | model_topk | 0.0025 | 54 | 0.2049 | 0.0055 | 0.0004 | 0.3011 | 3.5496 | -0.2633 | 0.5556 | 0.4407 | 20 |
| topk_cost_sensitivity_v1 | C_technical_semantic | RandomForest | 10 | model_topk | 0.0025 | 54 | 0.2796 | 0.0065 | 0.0014 | 0.3704 | 3.5496 | -0.3174 | 0.5185 | 0.3519 | 20 |
| topk_cost_sensitivity_v1 | D_all | LogisticRegression | 5 | model_topk | 0.0025 | 54 | 0.4609 | 0.0098 | 0.0048 | 0.4644 | 3.5496 | -0.3508 | 0.6296 | 0.3444 | 20 |
| topk_cost_sensitivity_v1 | D_all | LogisticRegression | 10 | model_topk | 0.0025 | 54 | 0.8286 | 0.0135 | 0.0084 | 0.7039 | 3.5496 | -0.2361 | 0.5926 | 0.2778 | 20 |
| topk_cost_sensitivity_v1 | D_all | RandomForest | 5 | model_topk | 0.0025 | 54 | 0.3932 | 0.0081 | 0.003 | 0.4552 | 3.5496 | -0.2633 | 0.5556 | 0.3667 | 20 |
| topk_cost_sensitivity_v1 | D_all | RandomForest | 10 | model_topk | 0.0025 | 54 | 0.3703 | 0.0079 | 0.0028 | 0.4345 | 3.5496 | -0.3174 | 0.5556 | 0.3111 | 20 |
| topk_cost_sensitivity_v1 | A_technical | LogisticRegression | 5 | model_topk | 0.005 | 54 | -0.1432 | 0.0002 | -0.0049 | 0.0099 | 3.5496 | -0.3984 | 0.4815 | 0.3185 | 20 |
| topk_cost_sensitivity_v1 | A_technical | LogisticRegression | 10 | model_topk | 0.005 | 54 | 0.3267 | 0.0073 | 0.0022 | 0.4005 | 3.5496 | -0.2731 | 0.537 | 0.3 | 20 |
| topk_cost_sensitivity_v1 | A_technical | RandomForest | 5 | model_topk | 0.005 | 54 | 0.4249 | 0.0087 | 0.0036 | 0.469 | 3.5496 | -0.3374 | 0.6296 | 0.3185 | 20 |
| topk_cost_sensitivity_v1 | A_technical | RandomForest | 10 | model_topk | 0.005 | 54 | 0.431 | 0.0085 | 0.0034 | 0.4893 | 3.5496 | -0.3307 | 0.5926 | 0.2889 | 20 |
| topk_cost_sensitivity_v1 | B_technical_keyword | LogisticRegression | 5 | model_topk | 0.005 | 54 | 0.1966 | 0.0063 | 0.0012 | 0.2903 | 3.5496 | -0.3984 | 0.5926 | 0.3 | 20 |
| topk_cost_sensitivity_v1 | B_technical_keyword | LogisticRegression | 10 | model_topk | 0.005 | 54 | 0.5847 | 0.0107 | 0.0056 | 0.5732 | 3.5496 | -0.2731 | 0.5741 | 0.2685 | 20 |
| topk_cost_sensitivity_v1 | B_technical_keyword | RandomForest | 5 | model_topk | 0.005 | 54 | -0.0175 | 0.0015 | -0.0036 | 0.0878 | 3.5496 | -0.3374 | 0.5556 | 0.3148 | 20 |
| topk_cost_sensitivity_v1 | B_technical_keyword | RandomForest | 10 | model_topk | 0.005 | 54 | 0.3737 | 0.0079 | 0.0028 | 0.439 | 3.5496 | -0.3307 | 0.5741 | 0.2852 | 20 |
| topk_cost_sensitivity_v1 | C_technical_semantic | LogisticRegression | 5 | model_topk | 0.005 | 54 | 0.125 | 0.005 | -0.0001 | 0.2347 | 3.5496 | -0.3571 | 0.5741 | 0.4111 | 20 |
| topk_cost_sensitivity_v1 | C_technical_semantic | LogisticRegression | 10 | model_topk | 0.005 | 54 | 0.3156 | 0.007 | 0.0019 | 0.3999 | 3.5496 | -0.2416 | 0.5185 | 0.3537 | 20 |
| topk_cost_sensitivity_v1 | C_technical_semantic | RandomForest | 5 | model_topk | 0.005 | 54 | 0.1354 | 0.0044 | -0.0007 | 0.241 | 3.5496 | -0.2686 | 0.537 | 0.4407 | 20 |
| topk_cost_sensitivity_v1 | C_technical_semantic | RandomForest | 10 | model_topk | 0.005 | 54 | 0.2201 | 0.0056 | 0.0005 | 0.3197 | 3.5496 | -0.3218 | 0.5185 | 0.3519 | 20 |
| topk_cost_sensitivity_v1 | D_all | LogisticRegression | 5 | model_topk | 0.005 | 54 | 0.394 | 0.009 | 0.0039 | 0.4231 | 3.5496 | -0.3571 | 0.6296 | 0.3444 | 20 |
| topk_cost_sensitivity_v1 | D_all | LogisticRegression | 10 | model_topk | 0.005 | 54 | 0.7613 | 0.0128 | 0.0077 | 0.6669 | 3.5496 | -0.2416 | 0.5926 | 0.2778 | 20 |
| topk_cost_sensitivity_v1 | D_all | RandomForest | 5 | model_topk | 0.005 | 54 | 0.3253 | 0.0072 | 0.0021 | 0.4024 | 3.5496 | -0.2686 | 0.5556 | 0.3667 | 20 |
| topk_cost_sensitivity_v1 | D_all | RandomForest | 10 | model_topk | 0.005 | 54 | 0.3134 | 0.0071 | 0.002 | 0.3906 | 3.5496 | -0.3218 | 0.537 | 0.3111 | 20 |
| topk_cost_sensitivity_v1 | A_technical | LogisticRegression | 5 | model_topk | 0.01 | 54 | -0.2155 | -0.0014 | -0.0065 | -0.0613 | 3.5496 | -0.4204 | 0.4444 | 0.3185 | 20 |
| topk_cost_sensitivity_v1 | A_technical | LogisticRegression | 10 | model_topk | 0.01 | 54 | 0.2223 | 0.0058 | 0.0007 | 0.3166 | 3.5496 | -0.2828 | 0.5185 | 0.3 | 20 |
| topk_cost_sensitivity_v1 | A_technical | RandomForest | 5 | model_topk | 0.01 | 54 | 0.3055 | 0.0071 | 0.002 | 0.3799 | 3.5496 | -0.3468 | 0.6296 | 0.3185 | 20 |
| topk_cost_sensitivity_v1 | A_technical | RandomForest | 10 | model_topk | 0.01 | 54 | 0.3226 | 0.0071 | 0.002 | 0.4043 | 3.5496 | -0.3377 | 0.5926 | 0.2889 | 20 |
| topk_cost_sensitivity_v1 | B_technical_keyword | LogisticRegression | 5 | model_topk | 0.01 | 54 | 0.102 | 0.0048 | -0.0003 | 0.2199 | 3.5496 | -0.4089 | 0.5556 | 0.3 | 20 |
| topk_cost_sensitivity_v1 | B_technical_keyword | LogisticRegression | 10 | model_topk | 0.01 | 54 | 0.4731 | 0.0094 | 0.0043 | 0.4996 | 3.5496 | -0.2828 | 0.5741 | 0.2685 | 20 |
| topk_cost_sensitivity_v1 | B_technical_keyword | RandomForest | 5 | model_topk | 0.01 | 54 | -0.0995 | -0.0001 | -0.0052 | -0.0049 | 3.5496 | -0.3468 | 0.5556 | 0.3148 | 20 |
| topk_cost_sensitivity_v1 | B_technical_keyword | RandomForest | 10 | model_topk | 0.01 | 54 | 0.2704 | 0.0065 | 0.0014 | 0.3577 | 3.5496 | -0.3377 | 0.5741 | 0.2852 | 20 |
| topk_cost_sensitivity_v1 | C_technical_semantic | LogisticRegression | 5 | model_topk | 0.01 | 54 | 0.0055 | 0.0029 | -0.0022 | 0.1368 | 3.5496 | -0.3695 | 0.537 | 0.4111 | 20 |
| topk_cost_sensitivity_v1 | C_technical_semantic | LogisticRegression | 10 | model_topk | 0.01 | 54 | 0.1949 | 0.0052 | 0.0001 | 0.297 | 3.5496 | -0.2525 | 0.5185 | 0.3537 | 20 |
| topk_cost_sensitivity_v1 | C_technical_semantic | RandomForest | 5 | model_topk | 0.01 | 54 | 0.0078 | 0.0022 | -0.0029 | 0.1206 | 3.5496 | -0.2791 | 0.5185 | 0.4407 | 20 |
| topk_cost_sensitivity_v1 | C_technical_semantic | RandomForest | 10 | model_topk | 0.01 | 54 | 0.1089 | 0.0038 | -0.0013 | 0.2184 | 3.5496 | -0.3307 | 0.5 | 0.3519 | 20 |
| topk_cost_sensitivity_v1 | D_all | LogisticRegression | 5 | model_topk | 0.01 | 54 | 0.2688 | 0.0073 | 0.0022 | 0.3408 | 3.5496 | -0.3695 | 0.6111 | 0.3444 | 20 |
| topk_cost_sensitivity_v1 | D_all | LogisticRegression | 10 | model_topk | 0.01 | 54 | 0.6337 | 0.0114 | 0.0063 | 0.5929 | 3.5496 | -0.2525 | 0.5926 | 0.2778 | 20 |
| topk_cost_sensitivity_v1 | D_all | RandomForest | 5 | model_topk | 0.01 | 54 | 0.1989 | 0.0053 | 0.0003 | 0.2976 | 3.5496 | -0.2791 | 0.537 | 0.3667 | 20 |
| topk_cost_sensitivity_v1 | D_all | RandomForest | 10 | model_topk | 0.01 | 54 | 0.2063 | 0.0055 | 0.0004 | 0.3031 | 3.5496 | -0.3307 | 0.537 | 0.3111 | 20 |

Limitation: fixed proportional round-trip rates omit market impact, spread variation, taxes, liquidity constraints, and execution timing; gross returns and turnover are held unchanged across rates.

