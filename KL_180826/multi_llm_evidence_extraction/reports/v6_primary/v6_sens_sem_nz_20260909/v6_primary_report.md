# V6 semantic-nonzero sensitivity evaluation

- Run: `v6_sens_sem_nz_20260909`
- Protocol: `v6_technical_primary_v1`
- Protocol SHA256: `62b255260d1f29d1a84f9a143d4b8f0259a4a177c0a0a3fcb2962479835403e2`
- Claim level: `v6_sensitivity_semantic_nonzero_retrain`
- Row filter: `semantic_nonzero`
- Fast: `False`
- Eligible rows used: `5656`
- Predictions: `29916`
- Folds: `3`

Primary family is H1 (B vs A) and H2 (C vs A) RandomForest balanced_accuracy.
BH is applied only to that two-test family. S_kw_sem and LogisticRegression are not jointly adjusted.
SENSITIVITY ONLY: retrain/eval on panel_eligible rows with at least one non-zero semantic predictor (coverage columns excluded). This does not replace the V6 full-panel primary.

## Fold audit

| fold_id | train_start | train_end | train_target_exit_max | test_start | test_end | purge_method | n_train | n_test | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2022-01-06 00:00:00 | 2023-01-27 00:00:00 | 2023-02-24 00:00:00 | 2023-03-06 00:00:00 | 2024-03-29 00:00:00 | target_exit_date_before_test_start | 660 | 820 | ok |
| 2 | 2022-01-06 00:00:00 | 2024-03-01 00:00:00 | 2024-03-29 00:00:00 | 2024-04-01 00:00:00 | 2025-04-29 00:00:00 | target_exit_date_before_test_start | 1446 | 1285 | ok |
| 3 | 2022-01-06 00:00:00 | 2025-03-31 00:00:00 | 2025-04-29 00:00:00 | 2025-05-05 00:00:00 | 2026-06-01 00:00:00 | target_exit_date_before_test_start | 2595 | 2881 | ok |

## Inference

| hypothesis | role | baseline_config | comparison_config | model | metric | raw_delta | improvement_delta | bootstrap_ci_low | bootstrap_ci_high | p_value | n_paired_dates | n_folds | status | primary_family_member | p_value_bh |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | auc | 0.05320778194253804 | 0.05320778194253804 | -0.010234997074402554 | 0.12304750129048912 | 0.12838716128387162 | 410 | 3 | ok | False | nan |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | balanced_accuracy | -0.0050044873825361635 | -0.0050044873825361635 | -0.04360787205680498 | 0.03680806101080491 | 0.8123187681231877 | 410 | 3 | ok | True | 0.8123187681231877 |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | brier | -0.004193635123872459 | 0.004193635123872459 | -0.006196852009796684 | 0.010745298100937734 | 0.3808619138086191 | 807 | 3 | ok | False | nan |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | f1 | -0.08911963526520365 | -0.08911963526520365 | -0.14741185742922192 | -0.05634935463711636 | 0.0004999500049995 | 807 | 3 | ok | False | nan |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | log_loss | -0.009500170440364187 | 0.009500170440364187 | -0.01223276589170595 | 0.022848032033073288 | 0.33586641335866413 | 807 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | auc | 0.12507804819390184 | 0.12507804819390184 | 0.013108894879397929 | 0.192477195004634 | 0.0184981501849815 | 410 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | balanced_accuracy | 0.08877256889452012 | 0.08877256889452012 | 0.013819789796923944 | 0.135826369091613 | 0.0115988401159884 | 410 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | brier | 0.0940277423413046 | -0.0940277423413046 | -0.141762568348316 | -0.06311421345959022 | 0.0006999300069993001 | 807 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | f1 | 0.004100161365632606 | 0.004100161365632606 | -0.08797636023499789 | 0.06890901562356291 | 0.926007399260074 | 807 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | log_loss | 3.629053917858937 | -3.629053917858937 | -4.6268895353594415 | -2.975162826938511 | 9.999000099990002e-05 | 807 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | auc | 0.0185943772803529 | 0.0185943772803529 | -0.052715735424805545 | 0.06940884520290007 | 0.5734426557344265 | 410 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | balanced_accuracy | -0.0289125136381234 | -0.0289125136381234 | -0.06905327007003836 | 0.010836803355858222 | 0.13988601139886012 | 410 | 3 | ok | True | 0.27977202279772023 |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | brier | 0.004160829174734061 | -0.004160829174734061 | -0.012714298949655149 | 0.003531008495878642 | 0.36526347365263473 | 807 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | f1 | -0.03449290967878329 | -0.03449290967878329 | -0.08789923822219362 | 0.0283775155382962 | 0.31616838316168383 | 807 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | log_loss | 0.00974866876366247 | -0.00974866876366247 | -0.027618315095849232 | 0.005868186100922268 | 0.30356964303569645 | 807 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | auc | 0.03766467374089325 | 0.03766467374089325 | -0.007744189352878378 | 0.07332220154506741 | 0.1396860313968603 | 410 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | balanced_accuracy | -0.0024644088973357274 | -0.0024644088973357274 | -0.04753318573364305 | 0.026811361656636043 | 0.9028097190280971 | 410 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | brier | 0.06468021116489377 | -0.06468021116489377 | -0.09885567387255638 | -0.027213824897092204 | 0.0007999200079992001 | 807 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | f1 | 0.024772961931282513 | 0.024772961931282513 | -0.04486452114937245 | 0.08717230285730172 | 0.45965403459654036 | 807 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | log_loss | 0.6649336163313987 | -0.6649336163313987 | -0.8417919396192841 | -0.44946183086120367 | 9.999000099990002e-05 | 807 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | auc | -0.034613404662185154 | -0.034613404662185154 | -0.12391909637900492 | 0.032715407339949966 | 0.41605839416058393 | 410 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | balanced_accuracy | -0.023908026255587238 | -0.023908026255587238 | -0.08460272256537502 | 0.03315361916200328 | 0.42925707429257076 | 410 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | brier | 0.008354464298606519 | -0.008354464298606519 | -0.01801086517676216 | 0.005354610398911955 | 0.20507949205079493 | 807 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | f1 | 0.05462672558642036 | 0.05462672558642036 | -0.0011741792025738334 | 0.13871642452962152 | 0.1897810218978102 | 807 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | log_loss | 0.019248839204026657 | -0.019248839204026657 | -0.03915599051063903 | 0.008863900885924479 | 0.1548845115488451 | 807 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | auc | -0.0874133744530086 | -0.0874133744530086 | -0.16016856159592438 | 0.0178992415810251 | 0.08159184081591841 | 410 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | balanced_accuracy | -0.09123697779185587 | -0.09123697779185587 | -0.13903917001020658 | -0.027475827526132424 | 0.0046995300469953 | 410 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | brier | -0.029347531176410823 | 0.029347531176410823 | -0.0071264678801228306 | 0.0872955295067015 | 0.29387061293870614 | 807 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | f1 | 0.0206728005656499 | 0.0206728005656499 | -0.05918341612647867 | 0.11288698565650233 | 0.6567343265673433 | 807 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | log_loss | -2.9641203015275384 | 2.9641203015275384 | 2.325791697704241 | 4.000992718887838 | 9.999000099990002e-05 | 807 | 3 | ok | False | nan |

## Allowed claims

Sensitivity paired OOS deltas only. Not V6 primary evidence; no alpha/causal/live-trading claims.
