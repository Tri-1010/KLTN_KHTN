# V6 horizon T+5 sensitivity evaluation

- Run: `v6_sens_h5_20260909`
- Protocol: `v6_technical_primary_v1`
- Protocol SHA256: `62b255260d1f29d1a84f9a143d4b8f0259a4a177c0a0a3fcb2962479835403e2`
- Claim level: `v6_sensitivity_horizon_T5`
- Row filter: `primary`
- Horizon (benchmark sessions): `5`
- Fast: `False`
- Eligible rows used: `88782`
- Predictions: `417228`
- Folds: `3`

Primary family is H1 (B vs A) and H2 (C vs A) RandomForest balanced_accuracy.
BH is applied only to that two-test family. S_kw_sem and LogisticRegression are not jointly adjusted.
SENSITIVITY ONLY: full eligible panel with outperform label horizon T+5 benchmark sessions. Locked primary remains T+20.

## Fold audit

| fold_id | train_start | train_end | train_target_exit_max | test_start | test_end | purge_method | n_train | n_test | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2021-10-14 00:00:00 | 2022-12-12 00:00:00 | 2022-12-19 00:00:00 | 2022-12-20 00:00:00 | 2024-02-21 00:00:00 | target_exit_date_before_test_start | 18844 | 23200 | ok |
| 2 | 2021-10-14 00:00:00 | 2024-02-07 00:00:00 | 2024-02-21 00:00:00 | 2024-02-22 00:00:00 | 2025-04-21 00:00:00 | target_exit_date_before_test_start | 42044 | 23189 | ok |
| 3 | 2021-10-14 00:00:00 | 2025-04-14 00:00:00 | 2025-04-21 00:00:00 | 2025-04-22 00:00:00 | 2026-06-22 00:00:00 | target_exit_date_before_test_start | 65233 | 23149 | ok |

## Inference

| hypothesis | role | baseline_config | comparison_config | model | metric | raw_delta | improvement_delta | bootstrap_ci_low | bootstrap_ci_high | p_value | n_paired_dates | n_folds | status | primary_family_member | p_value_bh |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | auc | -0.0024374188285862792 | -0.0024374188285862792 | -0.010172756222637847 | 0.004433557995899523 | 0.5026497350264973 | 870 | 3 | ok | False | nan |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | balanced_accuracy | -0.0014118714922704263 | -0.0014118714922704263 | -0.009186213276409711 | 0.004862830274750983 | 0.6935306469353064 | 870 | 3 | ok | True | 0.6935306469353064 |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | brier | -0.0007531047770442623 | 0.0007531047770442623 | 0.0003117718784990016 | 0.001301912376471132 | 0.0071992800719928 | 870 | 3 | ok | False | nan |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | f1 | -0.002425230489325357 | -0.002425230489325357 | -0.020747720617622402 | 0.01260571817541652 | 0.7863213678632137 | 870 | 3 | ok | False | nan |
| H1 | primary | A_technical | B_technical_keyword | RandomForest | log_loss | -0.0015108929338783844 | 0.0015108929338783844 | 0.0006300455284914687 | 0.002618396744883995 | 0.007099290070992901 | 870 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | auc | 0.008402516639241008 | 0.008402516639241008 | -0.007292524502267664 | 0.021152013516396583 | 0.23977602239776022 | 870 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | balanced_accuracy | 0.0015647765064350162 | 0.0015647765064350162 | -0.007784616306644182 | 0.00948113705649919 | 0.7144285571442855 | 870 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | brier | 0.031814585304849714 | -0.031814585304849714 | -0.035714343346736024 | -0.028951066574934438 | 9.999000099990002e-05 | 870 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | f1 | 0.04780983843147992 | 0.04780983843147992 | 0.01830948103792959 | 0.07419703929887662 | 0.0057994200579942 | 870 | 3 | ok | False | nan |
| H1 | robustness | A_technical | B_technical_keyword | LogisticRegression | log_loss | 0.21070109793979466 | -0.21070109793979466 | -0.2478027661410054 | -0.18575233724036858 | 9.999000099990002e-05 | 870 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | auc | -0.004345075673892757 | -0.004345075673892757 | -0.00890787672771574 | -0.0014104796244031779 | 0.012598740125987402 | 870 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | balanced_accuracy | -0.004193506795531739 | -0.004193506795531739 | -0.008391972084947014 | -0.0008554654118108145 | 0.05849415058494151 | 870 | 3 | ok | True | 0.11698830116988301 |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | brier | -0.00024188037383301097 | 0.00024188037383301097 | -7.753918193804884e-06 | 0.00047529728585940663 | 0.08199180081991801 | 870 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | f1 | 0.014018067369546219 | 0.014018067369546219 | 0.005495812647319633 | 0.02121129878507058 | 0.0029997000299970002 | 870 | 3 | ok | False | nan |
| H2 | primary | A_technical | C_technical_semantic | RandomForest | log_loss | -0.00048515396467442015 | 0.00048515396467442015 | -1.4333890101964972e-05 | 0.0009568699793814007 | 0.08299170082991701 | 870 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | auc | 0.0009996137312676694 | 0.0009996137312676694 | -0.0041138557943392546 | 0.004733942373891164 | 0.6663333666633336 | 870 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | balanced_accuracy | 0.0011071102420209564 | 0.0011071102420209564 | -0.002803557277096586 | 0.0054977681520896144 | 0.6145385461453855 | 870 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | brier | 0.00341606845557889 | -0.00341606845557889 | -0.004492527646404191 | -0.0025882343249990997 | 9.999000099990002e-05 | 870 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | f1 | 0.007123763452690348 | 0.007123763452690348 | -0.003905331005953766 | 0.01823503984286849 | 0.2628737126287371 | 870 | 3 | ok | False | nan |
| H2 | robustness | A_technical | C_technical_semantic | LogisticRegression | log_loss | 0.017203667531828438 | -0.017203667531828438 | -0.022519728525234442 | -0.012914833508046196 | 9.999000099990002e-05 | 870 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | auc | -0.001907656845306477 | -0.001907656845306477 | -0.009151088464703586 | 0.0050423556463048535 | 0.6076392360763924 | 870 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | balanced_accuracy | -0.002781635303261314 | -0.002781635303261314 | -0.00946225372616734 | 0.004504885649720615 | 0.47755224477552244 | 870 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | brier | 0.0005112244032112512 | -0.0005112244032112512 | -0.0008947931902181628 | -0.00024053991587166126 | 0.006799320067993201 | 870 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | f1 | 0.016443297858871574 | 0.016443297858871574 | 0.0018096090851443842 | 0.03298605086885774 | 0.061193880611938804 | 870 | 3 | ok | False | nan |
| S_kw_sem | supplemental | B_technical_keyword | C_technical_semantic | RandomForest | log_loss | 0.001025738969203964 | -0.001025738969203964 | -0.0017981971245281557 | -0.0004838428845516315 | 0.0066993300669933005 | 870 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | auc | -0.007402902907973341 | -0.007402902907973341 | -0.020759891344396878 | 0.007155479400484243 | 0.2882711728827117 | 870 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | balanced_accuracy | -0.0004576662644140604 | -0.0004576662644140604 | -0.008285573267143801 | 0.009493459277610323 | 0.9203079692030797 | 870 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | brier | -0.028398516849270826 | 0.028398516849270826 | 0.02522633607738599 | 0.03243083548237278 | 9.999000099990002e-05 | 870 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | f1 | -0.04068607497878958 | -0.04068607497878958 | -0.06351708957021172 | -0.014065945579431072 | 0.004199580041995801 | 870 | 3 | ok | False | nan |
| S_kw_sem | robustness | B_technical_keyword | C_technical_semantic | LogisticRegression | log_loss | -0.19349743040796621 | 0.19349743040796621 | 0.1671793511524681 | 0.2305214659059117 | 9.999000099990002e-05 | 870 | 3 | ok | False | nan |

## Allowed claims

Sensitivity paired OOS deltas only. Not V6 primary evidence; no alpha/causal/live-trading claims.
