# V6 technical primary evaluation

- Run: `v6_primary_20260909`
- Protocol: `v6_technical_primary_v1`
- Protocol SHA256: `62b255260d1f29d1a84f9a143d4b8f0259a4a177c0a0a3fcb2962479835403e2`
- Fast: `False`
- Predictions: `410496`
- Folds: `3`

Primary family is H1 (B vs A) and H2 (C vs A) RandomForest balanced_accuracy.
BH is applied only to that two-test family. S_kw_sem and LogisticRegression are not jointly adjusted.
Eligibility is target_status==ok plus lagged technical availability; no-news rows are zero-filled.

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
| H1 | primary | A_technical | B_technical_keyword | RandomForest | balanced_accuracy | -0.010240973025000802 | -0.010240973025000802 | -0.02130337612994644 | 0.0003147027325150499 | 0.09759024097590241 | 856 | 3 | ok | True | 0.19518048195180482 |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | brier | -0.0021112347825401664 | 0.0021112347825401664 | 0.0013003521822560066 | 0.003279034138202853 | 0.00029997000299970003 | 856 | 3 | ok | False | nan |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | f1 | -0.005930928835793079 | -0.005930928835793079 | -0.02089016820177174 | 0.012295794040018576 | 0.5236476352364764 | 856 | 3 | ok | False | nan |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | log_loss | -0.004364092418139639 | 0.004364092418139639 | 0.002707932762709628 | 0.006752965003525507 | 0.00029997000299970003 | 856 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | auc | 0.01315624730516579 | 0.01315624730516579 | -0.014748464253673982 | 0.03632878115737532 | 0.36606339366063395 | 856 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | balanced_accuracy | -0.0005696924955734288 | -0.0005696924955734288 | -0.021533953023162487 | 0.017504815633967358 | 0.9562043795620438 | 856 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | brier | 0.06338082700999216 | -0.06338082700999216 | -0.07310900338610549 | -0.05565932421700014 | 9.999000099990002e-05 | 856 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | f1 | 0.02621794699332217 | 0.02621794699332217 | -0.006947244757045379 | 0.05314261637787168 | 0.10378962103789621 | 856 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | log_loss | 0.6460101918218986 | -0.6460101918218986 | -0.738728152103031 | -0.5740513883660092 | 9.999000099990002e-05 | 856 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | auc | -0.007454846757091191 | -0.007454846757091191 | -0.01564057441309709 | 0.00025277629928544367 | 0.0932906709329067 | 856 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | balanced_accuracy | -0.004248607815284229 | -0.004248607815284229 | -0.011200577414621025 | 0.0018953157694729088 | 0.22997700229977003 | 856 | 3 | ok | True | 0.22997700229977003 |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | brier | -0.0006363924023673683 | 0.0006363924023673683 | 3.869392238645771e-05 | 0.0013488257383418771 | 0.11788821117888211 | 856 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | f1 | 0.012306251653193495 | 0.012306251653193495 | 0.005224223972354276 | 0.018505260699373315 | 0.016698330166983303 | 856 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | log_loss | -0.001344971772246094 | 0.001344971772246094 | 0.00011826187504454858 | 0.002801328557987062 | 0.10728927107289271 | 856 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | auc | -0.0009624477227472691 | -0.0009624477227472691 | -0.006688164623999328 | 0.0040171529020342454 | 0.7414258574142586 | 856 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | balanced_accuracy | 0.0019225922239327548 | 0.0019225922239327548 | -0.0038461940216159194 | 0.007732831283206392 | 0.561943805619438 | 856 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | brier | 0.0060002971144967766 | -0.0060002971144967766 | -0.007666253510934506 | -0.00449421849530755 | 9.999000099990002e-05 | 856 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | f1 | 0.006026025760862438 | 0.006026025760862438 | -0.00159764150905555 | 0.012451353435063369 | 0.13338666133386662 | 856 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | log_loss | 0.041229827526058326 | -0.041229827526058326 | -0.05051255459858523 | -0.028988372156855714 | 9.999000099990002e-05 | 856 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | auc | -0.0012416540598763491 | -0.0012416540598763491 | -0.013813936418625496 | 0.010454287807241436 | 0.8524147585241476 | 856 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | balanced_accuracy | 0.005992365209716572 | 0.005992365209716572 | -0.005798580795986371 | 0.017182502464173032 | 0.38506149385061494 | 856 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | brier | 0.0014748423801727983 | -0.0014748423801727983 | -0.002243798539287025 | -0.0009097805229583808 | 9.999000099990002e-05 | 856 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | f1 | 0.018237180488986572 | 0.018237180488986572 | 0.0002172420903200581 | 0.031949936375031296 | 0.0653934606539346 | 856 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | log_loss | 0.0030191206458935445 | -0.0030191206458935445 | -0.004591512517390768 | -0.0018783854508381708 | 9.999000099990002e-05 | 856 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | auc | -0.014118695027913056 | -0.014118695027913056 | -0.03799520847356832 | 0.013138895394360578 | 0.32166783321667836 | 856 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | balanced_accuracy | 0.0024922847195061847 | 0.0024922847195061847 | -0.016176007318880765 | 0.02402872494655544 | 0.8172182781721827 | 856 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | brier | -0.057380529895495386 | 0.057380529895495386 | 0.049213354670195546 | 0.0674228983476112 | 9.999000099990002e-05 | 856 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | f1 | -0.020191921232459737 | -0.020191921232459737 | -0.046991209067336 | 0.011912475205537322 | 0.20657934206579343 | 856 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | log_loss | -0.6047803642958403 | 0.6047803642958403 | 0.5330086957112089 | 0.6997904688659479 | 9.999000099990002e-05 | 856 | 3 | ok | False | nan |

## Allowed claims

Only out-of-sample paired deltas on the V6 full price panel. This run does not support alpha, causal, or live-trading claims.
