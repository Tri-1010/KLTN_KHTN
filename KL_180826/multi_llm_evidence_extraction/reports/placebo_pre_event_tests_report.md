# Placebo pre-event tests

Negative-control windows end before event effective date. Primary metric: VNINDEX-adjusted return. Non-overlapping samples, tie-corrected Mann–Whitney, BH-FDR, deterministic bootstrap CI. Exploratory only; no causal claim.

## Results

| artifact_schema_version | placebo_window | pre_window_start_offset | pre_window_end_offset | comparison | metric | n_a | n_b | mean_a | mean_b | diff_mean | mann_whitney_u | z_score | tie_corrected_variance | p_value_raw | cliffs_delta | diff_ci_low | diff_ci_high | cliffs_delta_ci_low | cliffs_delta_ci_high | p_value_bh | reject_fdr_05 | robust_positive_effect | robust_negative_effect | correction_method |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| placebo_pre_event_tests_v1 | T-20:T-1 | -20 | -1 | direction=support vs direction=risk | market_adjusted_return | 39 | 16 | 0.0192 | -0.0145 | 0.0337 | 401.0 | 1.64 | 2912.0 | 0.101 | 0.2853 | -0.0413 | 0.1011 | -0.0866 | 0.6378 | 0.404 | False | False | False | Benjamini-Hochberg |
| placebo_pre_event_tests_v1 | T-20:T-1 | -20 | -1 | materiality=high+medium vs materiality=low | market_adjusted_return | 58 | 49 | 0.0159 | 0.0019 | 0.014 | 1422.0 | 0.0031 | 25578.0 | 0.9975 | 0.0007 | -0.0216 | 0.0473 | -0.2295 | 0.2104 | 0.9975 | False | False | False | Benjamini-Hochberg |
| placebo_pre_event_tests_v1 | T-60:T-21 | -60 | -21 | direction=support vs direction=risk | market_adjusted_return | 38 | 15 | -0.0037 | -0.0312 | 0.0275 | 326.0 | 0.7997 | 2565.0 | 0.4239 | 0.1439 | -0.021 | 0.077 | -0.1896 | 0.4982 | 0.5652 | False | False | False | Benjamini-Hochberg |
| placebo_pre_event_tests_v1 | T-60:T-21 | -60 | -21 | materiality=high+medium vs materiality=low | market_adjusted_return | 57 | 45 | -0.0201 | 0.0108 | -0.0309 | 1125.0 | -1.0581 | 22016.25 | 0.29 | -0.1228 | -0.078 | 0.0133 | -0.3435 | 0.1096 | 0.5652 | False | False | False | Benjamini-Hochberg |

No pre-event comparison survives BH-FDR 5% with bootstrap CI excluding zero; this does not prove absence of pre-trends.
