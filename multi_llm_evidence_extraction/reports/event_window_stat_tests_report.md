# Event-window statistical tests

Primary metric: VNINDEX-adjusted return. Non-overlapping event sample, tie-corrected Mann–Whitney, BH-FDR, deterministic bootstrap CI. Exploratory only; no causal claim.

## Results

| window | comparison | metric | n_a | n_b | mean_a | mean_b | diff_mean | mann_whitney_u | z_score | tie_corrected_variance | p_value_raw | cliffs_delta | diff_ci_low | diff_ci_high | cliffs_delta_ci_low | cliffs_delta_ci_high | p_value_bh | reject_fdr_05 | robust_positive_effect | robust_negative_effect | correction_method | artifact_schema_version |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T+1 | direction=support vs direction=risk | market_adjusted_return | 41 | 16 | 0.0052 | -0.0028 | 0.008 | 402.0 | 1.3053 | 3170.6667 | 0.1918 | 0.2256 | -0.0013 | 0.0175 | -0.1189 | 0.5518 | 0.3069 | False | False | False | Benjamini-Hochberg | event_window_tests_v3 |
| T+1 | materiality=high+medium vs materiality=low | market_adjusted_return | 60 | 54 | 0.0032 | 0.0012 | 0.002 | 1514.0 | -0.5987 | 31050.0 | 0.5494 | -0.0654 | -0.0046 | 0.0089 | -0.2803 | 0.1469 | 0.6278 | False | False | False | Benjamini-Hochberg | event_window_tests_v3 |
| T+5 | direction=support vs direction=risk | market_adjusted_return | 40 | 16 | 0.0124 | 0.0043 | 0.0081 | 395.0 | 1.3512 | 3040.0 | 0.1766 | 0.2344 | -0.0245 | 0.0338 | -0.1439 | 0.572 | 0.3069 | False | False | False | Benjamini-Hochberg | event_window_tests_v3 |
| T+5 | materiality=high+medium vs materiality=low | market_adjusted_return | 59 | 50 | 0.0124 | -0.0099 | 0.0223 | 1930.0 | 2.7639 | 27041.6667 | 0.0057 | 0.3085 | 0.0091 | 0.0366 | 0.0956 | 0.5132 | 0.0457 | True | True | False | Benjamini-Hochberg | event_window_tests_v3 |
| T+20 | direction=support vs direction=risk | market_adjusted_return | 36 | 16 | 0.0235 | -0.0014 | 0.0249 | 341.0 | 1.0409 | 2544.0 | 0.2979 | 0.184 | -0.0318 | 0.0783 | -0.2014 | 0.5174 | 0.3972 | False | False | False | Benjamini-Hochberg | event_window_tests_v3 |
| T+20 | materiality=high+medium vs materiality=low | market_adjusted_return | 55 | 46 | 0.017 | -0.0227 | 0.0397 | 1579.0 | 2.1378 | 21505.0 | 0.0325 | 0.2482 | 0.0065 | 0.0735 | 0.0245 | 0.4609 | 0.1301 | False | False | False | Benjamini-Hochberg | event_window_tests_v3 |
| T+60 | direction=support vs direction=risk | market_adjusted_return | 33 | 14 | 0.0054 | -0.0152 | 0.0205 | 229.0 | -0.0349 | 1848.0 | 0.9722 | -0.0087 | -0.0533 | 0.1023 | -0.3681 | 0.3463 | 0.9722 | False | False | False | Benjamini-Hochberg | event_window_tests_v3 |
| T+60 | materiality=high+medium vs materiality=low | market_adjusted_return | 50 | 38 | -0.0011 | -0.041 | 0.0399 | 1154.0 | 1.7143 | 14091.6667 | 0.0865 | 0.2147 | -0.0117 | 0.0914 | -0.0211 | 0.4379 | 0.2306 | False | False | False | Benjamini-Hochberg | event_window_tests_v3 |

