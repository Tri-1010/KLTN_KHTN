# V6 densified-semantic sensitivity evaluation (`densified_cache_semantic`)

- Run: `v6_sens_sem_feat_20260909`
- Protocol: `v6_technical_primary_v1`
- Protocol SHA256: `62b255260d1f29d1a84f9a143d4b8f0259a4a177c0a0a3fcb2962479835403e2`
- Claim level: `v6_sensitivity_densified_cache_semantic`
- Row filter: `primary`
- Horizon (benchmark sessions): `20`
- Fast: `False`
- Eligible rows used: `87577`
- Predictions: `410496`
- Folds: `3`

Primary family is H1 (B vs A) and H2 (C vs A) RandomForest balanced_accuracy.
BH is applied only to that two-test family. S_kw_sem and LogisticRegression are not jointly adjusted.
SENSITIVITY ONLY: densified single-model cache semantic features on the full eligible panel. This is not multi-LLM consensus and does not replace the locked V6 primary.

## Fold audit

| fold_id | train_start | train_end | train_target_exit_max | test_start | test_end | purge_method | n_train | n_test | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-10-14 00:00:00 | 2022-11-18 00:00:00 | 2022-12-16 00:00:00 | 2022-12-19 00:00:00 | 2024-02-07 00:00:00 | target_exit_date_before_test_start | 17561 | 22874 | ok |
| 2 | 2021-10-14 00:00:00 | 2024-01-10 00:00:00 | 2024-02-07 00:00:00 | 2024-02-15 00:00:00 | 2025-04-04 00:00:00 | target_exit_date_before_test_start | 40441 | 22794 | ok |
| 3 | 2021-10-14 00:00:00 | 2025-03-07 00:00:00 | 2025-04-04 00:00:00 | 2025-04-08 00:00:00 | 2026-06-01 00:00:00 | target_exit_date_before_test_start | 63229 | 22748 | ok |

## Inference

| hypothesis | role | baseline_config | comparison_config | model | metric | raw_delta | improvement_delta | bootstrap_ci_low | bootstrap_ci_high | p_value | n_paired_dates | n_folds | status | primary_family_member | p_value_bh |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | auc | -0.00621319269721484 | -0.00621319269721484 | -0.01982373716452061 | 0.008311376063182933 | 0.38166183381661833 | 856 | 3 | ok | False | nan |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | balanced_accuracy | -0.010240973025000802 | -0.010240973025000802 | -0.02130337612994644 | 0.0003147027325150499 | 0.09759024097590241 | 856 | 3 | ok | True | 0.17218278172182783 |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | brier | -0.0021112347825401672 | 0.0021112347825401672 | 0.001300352182256006 | 0.003279034138202858 | 0.00029997000299970003 | 856 | 3 | ok | False | nan |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | f1 | -0.005930928835793079 | -0.005930928835793079 | -0.02089016820177174 | 0.012295794040018576 | 0.5236476352364764 | 856 | 3 | ok | False | nan |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | log_loss | -0.004364092418139651 | 0.004364092418139651 | 0.0027079327627096412 | 0.006752965003525523 | 0.00029997000299970003 | 856 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | auc | 0.01315624730516579 | 0.01315624730516579 | -0.014748464253673982 | 0.03632878115737532 | 0.36606339366063395 | 856 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | balanced_accuracy | -0.0005696924955734288 | -0.0005696924955734288 | -0.021533953023162487 | 0.017504815633967358 | 0.9562043795620438 | 856 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | brier | 0.06338082700999216 | -0.06338082700999216 | -0.07310900338610549 | -0.05565932421700014 | 9.999000099990002e-05 | 856 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | f1 | 0.02621794699332217 | 0.02621794699332217 | -0.006947244757045379 | 0.05314261637787168 | 0.10378962103789621 | 856 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | log_loss | 0.6460101918218986 | -0.6460101918218986 | -0.738728152103031 | -0.5740513883660092 | 9.999000099990002e-05 | 856 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | auc | -0.015795516231941375 | -0.015795516231941375 | -0.026360634369192847 | -0.003192435269249109 | 0.0096990300969903 | 856 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | balanced_accuracy | -0.00756692982105108 | -0.00756692982105108 | -0.017130717234564285 | 0.0034867199734372584 | 0.17218278172182783 | 856 | 3 | ok | True | 0.17218278172182783 |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | brier | 0.0003174900248740065 | -0.0003174900248740065 | -0.0012923665892376668 | 0.0009250473345783127 | 0.6368363163683631 | 856 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | f1 | 0.014437795903955686 | 0.014437795903955686 | 0.0010152746078019948 | 0.028619649886016094 | 0.17798220177982202 | 856 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | log_loss | 0.0005530586430367631 | -0.0005530586430367631 | -0.0025361072230206485 | 0.001982468231860851 | 0.6864313568643136 | 856 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | auc | 0.0027276696167183832 | 0.0027276696167183832 | -0.007262785610581722 | 0.015459492310827105 | 0.6718328167183282 | 856 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | balanced_accuracy | -0.0061475560769513 | -0.0061475560769513 | -0.01655292849956569 | 0.006065520189535458 | 0.3321667833216678 | 856 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | brier | 0.005175515424766909 | -0.005175515424766909 | -0.006865890668494735 | -0.003272052893111934 | 9.999000099990002e-05 | 856 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | f1 | 0.00990922279295019 | 0.00990922279295019 | -0.01119454951784614 | 0.02821807926935029 | 0.3628637136286371 | 856 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | log_loss | 0.011574720582124642 | -0.011574720582124642 | -0.015073258427073105 | -0.007452233048546274 | 9.999000099990002e-05 | 856 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | auc | -0.009582323534726532 | -0.009582323534726532 | -0.021710143804998652 | 0.0038903292175569786 | 0.15348465153484653 | 856 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | balanced_accuracy | 0.0026740432039497218 | 0.0026740432039497218 | -0.008014168496617402 | 0.014659454919957966 | 0.6974302569743026 | 856 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | brier | 0.002428724807414174 | -0.002428724807414174 | -0.0034092597200238405 | -0.0015254868947187348 | 9.999000099990002e-05 | 856 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | f1 | 0.020368724739748767 | 0.020368724739748767 | 0.0066660726512521055 | 0.03231237714551638 | 0.045495450454954504 | 856 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | log_loss | 0.004917151061176413 | -0.004917151061176413 | -0.006901609138846543 | -0.0030854029591767637 | 9.999000099990002e-05 | 856 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | auc | -0.010428577688447405 | -0.010428577688447405 | -0.027273639779681325 | 0.01320717470702447 | 0.37206279372062795 | 856 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | balanced_accuracy | -0.005577863581377871 | -0.005577863581377871 | -0.017350293205875795 | 0.01060145112419891 | 0.46455354464553544 | 856 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | brier | -0.058205311585225246 | 0.058205311585225246 | 0.05057206442197502 | 0.06825342685024498 | 9.999000099990002e-05 | 856 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | f1 | -0.01630872420037198 | -0.01630872420037198 | -0.033567500618717765 | 0.004354060293750704 | 0.14288571142885712 | 856 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | log_loss | -0.6344354712397738 | 0.6344354712397738 | 0.5627299114581057 | 0.7279876348890378 | 9.999000099990002e-05 | 856 | 3 | ok | False | nan |

## Allowed claims

Sensitivity paired OOS deltas only. Not V6 primary evidence; no alpha/causal/live-trading claims.
