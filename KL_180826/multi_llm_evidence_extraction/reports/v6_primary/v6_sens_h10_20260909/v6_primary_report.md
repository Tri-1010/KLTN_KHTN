# V6 horizon T+10 sensitivity evaluation

- Run: `v6_sens_h10_20260909`
- Protocol: `v6_technical_primary_v1`
- Protocol SHA256: `62b255260d1f29d1a84f9a143d4b8f0259a4a177c0a0a3fcb2962479835403e2`
- Claim level: `v6_sensitivity_horizon_T10`
- Row filter: `primary`
- Horizon (benchmark sessions): `10`
- Fast: `False`
- Eligible rows used: `88377`
- Predictions: `414336`
- Folds: `3`

Primary family is H1 (B vs A) and H2 (C vs A) RandomForest balanced_accuracy.
BH is applied only to that two-test family. S_kw_sem and LogisticRegression are not jointly adjusted.
SENSITIVITY ONLY: full eligible panel with outperform label horizon T+10 benchmark sessions. Locked primary remains T+20.

## Fold audit

| fold_id | train_start | train_end | train_target_exit_max | test_start | test_end | purge_method | n_train | n_test | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-10-14 00:00:00 | 2022-12-06 00:00:00 | 2022-12-20 00:00:00 | 2022-12-21 00:00:00 | 2024-02-20 00:00:00 | target_exit_date_before_test_start | 18521 | 23036 | ok |
| 2 | 2021-10-14 00:00:00 | 2024-01-30 00:00:00 | 2024-02-20 00:00:00 | 2024-02-21 00:00:00 | 2025-04-16 00:00:00 | target_exit_date_before_test_start | 41561 | 23032 | ok |
| 3 | 2021-10-14 00:00:00 | 2025-04-01 00:00:00 | 2025-04-16 00:00:00 | 2025-04-17 00:00:00 | 2026-06-15 00:00:00 | target_exit_date_before_test_start | 64589 | 22988 | ok |

## Inference

| hypothesis | role | baseline_config | comparison_config | model | metric | raw_delta | improvement_delta | bootstrap_ci_low | bootstrap_ci_high | p_value | n_paired_dates | n_folds | status | primary_family_member | p_value_bh |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | auc | -0.0016799442108559157 | -0.0016799442108559157 | -0.009234002567505202 | 0.008541495445480652 | 0.7212278772122788 | 864 | 3 | ok | False | nan |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | balanced_accuracy | -0.003233770604832961 | -0.003233770604832961 | -0.00999581923722004 | 0.004191050245520951 | 0.4196580341965803 | 864 | 3 | ok | True | 0.4196580341965803 |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | brier | -0.0013751736154520874 | 0.0013751736154520874 | 0.0008976451966980314 | 0.002191292473328678 | 9.999000099990002e-05 | 864 | 3 | ok | False | nan |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | f1 | 0.008617162273223272 | 0.008617162273223272 | -0.006714605694348207 | 0.024551369323271423 | 0.34966503349665035 | 864 | 3 | ok | False | nan |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | log_loss | -0.0027891233080015237 | 0.0027891233080015237 | 0.0018252079893634964 | 0.0044482190481183155 | 9.999000099990002e-05 | 864 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | auc | 0.010790488789720665 | 0.010790488789720665 | -0.01280609252408826 | 0.027970596407687873 | 0.3588641135886411 | 864 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | balanced_accuracy | 0.009102624358632534 | 0.009102624358632534 | -0.008052159240628912 | 0.022032661179323173 | 0.2910708929107089 | 864 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | brier | 0.04509451239586224 | -0.04509451239586224 | -0.05155137453334878 | -0.04062099585109161 | 9.999000099990002e-05 | 864 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | f1 | 0.03962876645084309 | 0.03962876645084309 | 0.00737269550026704 | 0.06690649228363862 | 0.013598640135986401 | 864 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | log_loss | 0.42781113248260033 | -0.42781113248260033 | -0.4967229781048687 | -0.3803520173557929 | 9.999000099990002e-05 | 864 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | auc | -0.006682223252915014 | -0.006682223252915014 | -0.012018311533663555 | -0.0013482627636743532 | 0.0168983101689831 | 864 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | balanced_accuracy | -0.007011110818047889 | -0.007011110818047889 | -0.0131294369533887 | -0.0023857678704032074 | 0.016298370162983702 | 864 | 3 | ok | True | 0.032596740325967405 |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | brier | -0.0004014506280169181 | 0.0004014506280169181 | 0.00014622514481767482 | 0.0008395868619503937 | 0.045995400459954004 | 864 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | f1 | 0.008965132950601697 | 0.008965132950601697 | 0.0009992831702949178 | 0.01697326722303636 | 0.0648935106489351 | 864 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | log_loss | -0.0008144991850954116 | 0.0008144991850954116 | 0.00029395813756232756 | 0.0017140445894006193 | 0.04609539046095391 | 864 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | auc | 0.0007017004105040942 | 0.0007017004105040942 | -0.005107343473927436 | 0.005917887074851875 | 0.8164183581641836 | 864 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | balanced_accuracy | -0.002401852614887326 | -0.002401852614887326 | -0.007512269925236214 | 0.0025291474477201208 | 0.3594640535946405 | 864 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | brier | 0.004694086501715822 | -0.004694086501715822 | -0.006136197884951065 | -0.0032879287498485685 | 9.999000099990002e-05 | 864 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | f1 | 0.007348599568451579 | 0.007348599568451579 | -0.0002116688640388706 | 0.014514054668111637 | 0.0668933106689331 | 864 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | log_loss | 0.030797344882203485 | -0.030797344882203485 | -0.040068529902836963 | -0.022164541559558406 | 9.999000099990002e-05 | 864 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | auc | -0.005002279042059098 | -0.005002279042059098 | -0.01494591340518223 | 0.00254942896711637 | 0.28187181281871815 | 864 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | balanced_accuracy | -0.0037773402132149276 | -0.0037773402132149276 | -0.01260454666949619 | 0.003223367991459491 | 0.3825617438256174 | 864 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | brier | 0.0009737229874351695 | -0.0009737229874351695 | -0.0014884657421331902 | -0.0006179866636571244 | 9.999000099990002e-05 | 864 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | f1 | 0.0003479706773784259 | 0.0003479706773784259 | -0.01651292679409296 | 0.016086564090396372 | 0.972002799720028 | 864 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | log_loss | 0.0019746241229061127 | -0.0019746241229061127 | -0.003018380984368139 | -0.0012568151413636882 | 9.999000099990002e-05 | 864 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | auc | -0.010088788379216571 | -0.010088788379216571 | -0.02552611430708453 | 0.011253419175881109 | 0.3428657134286571 | 864 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | balanced_accuracy | -0.011504476973519862 | -0.011504476973519862 | -0.023260800587843855 | 0.0048756817398977895 | 0.1474852514748525 | 864 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | brier | -0.04040042589414643 | 0.04040042589414643 | 0.035665637781911085 | 0.04706249836807874 | 9.999000099990002e-05 | 864 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | f1 | -0.032280166882391506 | -0.032280166882391506 | -0.058045537162254426 | -0.0014264975485972773 | 0.029397060293970604 | 864 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | log_loss | -0.39701378760039685 | 0.39701378760039685 | 0.3482391394746647 | 0.46592664839531034 | 9.999000099990002e-05 | 864 | 3 | ok | False | nan |

## Allowed claims

Sensitivity paired OOS deltas only. Not V6 primary evidence; no alpha/causal/live-trading claims.
