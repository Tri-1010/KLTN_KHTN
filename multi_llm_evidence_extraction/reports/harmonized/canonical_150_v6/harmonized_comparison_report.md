# Harmonized keyword–semantic comparison

- Run: `canonical_150_v6`
- Mode: `pilot`
- Protocol SHA256: `718dd5e5828eaf1df991492091b3d96dec478096070767bf25e4ae93b4ce5a1a`
- Run tier: `canonical`
- Claim level: `common_stratified_article_spine_only`
- Coverage audit pass: `True`
- Fold audit pass: `True`

## Sample selection and spine attrition

| index | value |
| --- | --- |
| sampled_articles | 150 |
| joined_articles | 150 |
| eligible_articles | 122 |
| mapped_eligible_articles | 114 |
| analytic_spine_articles | 114 |
| panel_target_available_rows | 92080 |
| panel_eligible_rows | 5656 |

## Target exit and fold audit

| fold_id | train_start | train_end | train_target_exit_max | test_start | test_end | n_train | n_test | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2022-01-06 | 2023-01-27 | 2023-02-24 | 2023-03-06 | 2024-03-29 | 660 | 820 | ok |
| 2 | 2022-01-06 | 2024-03-01 | 2024-03-29 | 2024-04-01 | 2025-04-29 | 1446 | 1285 | ok |
| 3 | 2022-01-06 | 2025-03-31 | 2025-04-29 | 2025-05-05 | 2026-06-01 | 2595 | 2881 | ok |

## Coverage equality audit

| ticker | rows | panel_eligible | common_60d | coverage_feature_count | coverage_equal_B_C |
| --- | --- | --- | --- | --- | --- |
| ABB | 1173 | 60 | 60.0 | 9 | True |
| ACB | 1172 | 180 | 196.0 | 9 | True |
| ANV | 1173 | 60 | 60.0 | 9 | True |
| BAB | 1173 | 0 | 0.0 | 9 | True |
| BCM | 1172 | 60 | 60.0 | 9 | True |
| BID | 1172 | 214 | 236.0 | 9 | True |
| BMP | 1173 | 120 | 120.0 | 9 | True |
| BSI | 1173 | 60 | 83.0 | 9 | True |
| BVB | 1173 | 0 | 0.0 | 9 | True |
| BVH | 1172 | 0 | 0.0 | 9 | True |
| CMG | 1174 | 60 | 60.0 | 9 | True |
| CSV | 1173 | 38 | 58.0 | 9 | True |
| CTG | 1172 | 97 | 117.0 | 9 | True |
| DCM | 1173 | 0 | 0.0 | 9 | True |
| DGW | 1174 | 60 | 60.0 | 9 | True |
| DIG | 1173 | 0 | 0.0 | 9 | True |
| DPM | 1173 | 120 | 120.0 | 9 | True |
| DXG | 1173 | 0 | 0.0 | 9 | True |
| EIB | 1173 | 0 | 0.0 | 9 | True |
| ELC | 1173 | 0 | 0.0 | 9 | True |
| EVF | 1174 | 0 | 0.0 | 9 | True |
| FPT | 1172 | 60 | 60.0 | 9 | True |
| FRT | 1174 | 60 | 60.0 | 9 | True |
| GAS | 1172 | 60 | 60.0 | 9 | True |
| GEX | 1174 | 60 | 60.0 | 9 | True |
| GMD | 1174 | 0 | 0.0 | 9 | True |
| GVR | 1172 | 0 | 0.0 | 9 | True |
| HAH | 1174 | 60 | 60.0 | 9 | True |
| HCM | 1173 | 60 | 70.0 | 9 | True |
| HDB | 1172 | 67 | 120.0 | 9 | True |
| HDG | 1173 | 132 | 180.0 | 9 | True |
| HPG | 1172 | 216 | 340.0 | 9 | True |
| HSG | 1173 | 120 | 120.0 | 9 | True |
| KDH | 1173 | 146 | 210.0 | 9 | True |
| KLB | 1173 | 60 | 60.0 | 9 | True |
| LPB | 1173 | 199 | 300.0 | 9 | True |
| MBB | 1172 | 120 | 120.0 | 9 | True |
| MBS | 1173 | 95 | 120.0 | 9 | True |
| MCH | 1174 | 0 | 0.0 | 9 | True |
| MSB | 1173 | 60 | 60.0 | 9 | True |
| MSN | 1172 | 60 | 60.0 | 9 | True |
| MWG | 1172 | 180 | 180.0 | 9 | True |
| NAB | 1173 | 60 | 60.0 | 9 | True |
| NKG | 1173 | 0 | 0.0 | 9 | True |
| NLG | 1173 | 120 | 120.0 | 9 | True |
| NT2 | 1174 | 0 | 0.0 | 9 | True |
| NVL | 1173 | 199 | 219.0 | 9 | True |
| OCB | 1173 | 144 | 180.0 | 9 | True |
| PDR | 1173 | 60 | 60.0 | 9 | True |
| PGB | 1173 | 60 | 60.0 | 9 | True |
| PHR | 1173 | 0 | 0.0 | 9 | True |
| PLX | 1172 | 0 | 0.0 | 9 | True |
| PNJ | 1174 | 67 | 87.0 | 9 | True |
| POW | 1172 | 0 | 0.0 | 9 | True |
| PPC | 1173 | 120 | 120.0 | 9 | True |
| PVT | 1174 | 0 | 0.0 | 9 | True |
| REE | 1174 | 120 | 120.0 | 9 | True |
| SAB | 1172 | 60 | 60.0 | 9 | True |
| SCR | 1173 | 0 | 0.0 | 9 | True |
| SHB | 1172 | 60 | 60.0 | 9 | True |
| SSB | 1172 | 0 | 0.0 | 9 | True |
| SSI | 1172 | 180 | 180.0 | 9 | True |
| STB | 1172 | 60 | 60.0 | 9 | True |
| TCB | 1172 | 180 | 185.0 | 9 | True |
| TPB | 1172 | 60 | 71.0 | 9 | True |
| VBB | 1173 | 60 | 60.0 | 9 | True |
| VCB | 1172 | 180 | 180.0 | 9 | True |
| VCG | 1173 | 120 | 120.0 | 9 | True |
| VCI | 1173 | 98 | 118.0 | 9 | True |
| VGC | 1173 | 0 | 0.0 | 9 | True |
| VHC | 1174 | 0 | 0.0 | 9 | True |
| VHM | 1172 | 60 | 60.0 | 9 | True |
| VIB | 1172 | 120 | 120.0 | 9 | True |
| VIC | 1172 | 180 | 180.0 | 9 | True |
| VJC | 1172 | 60 | 60.0 | 9 | True |
| VND | 1173 | 120 | 120.0 | 9 | True |
| VNM | 1172 | 142 | 162.0 | 9 | True |
| VPB | 1172 | 22 | 42.0 | 9 | True |
| VRE | 1172 | 0 | 0.0 | 9 | True |
| VSC | 1174 | 0 | 0.0 | 9 | True |

## P1/S1/S2 paired inference

| family | baseline_config | comparison_config | model | metric | raw_delta | improvement_delta | bootstrap_ci_low | bootstrap_ci_high | p_value | n_paired_dates | n_folds | status | p_value_bh | coverage_audit_pass | fold_audit_pass | primary_gate_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | auc | 0.005466907753493111 | 0.005466907753493111 | -0.06635931333515176 | 0.06817752796548528 | 0.8691130886911309 | 410 | 3 | ok | 0.9239076092390761 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | balanced_accuracy | 0.020972794143525843 | 0.020972794143525843 | -0.035740836060958014 | 0.07182773950304439 | 0.44515548445155484 | 410 | 3 | ok | 0.6924640869246408 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | brier | 0.03794678712676241 | -0.03794678712676241 | -0.0677351862820494 | -0.0009067433514971303 | 0.025797420257974202 | 807 | 3 | ok | 0.12038796120387961 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | f1 | 0.09369556453872865 | 0.09369556453872865 | 0.05133183332473072 | 0.1483087249536344 | 0.006399360063993601 | 807 | 3 | ok | 0.044795520447955206 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | log_loss | 0.38900900948630457 | -0.38900900948630457 | -0.5622128375607987 | -0.16271448888493614 | 0.00029997000299970003 | 807 | 3 | ok | 0.004199580041995801 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | precision_at_10 | -0.004945054945054946 | -0.004945054945054946 | nan | nan | nan | 182 | 2 | not_estimable | nan | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | precision_at_5 | 0.010643015521064303 | 0.010643015521064303 | -0.03503325942350333 | 0.05633037694013288 | 0.6578342165783422 | 451 | 3 | ok | 0.8372435483724355 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | rank_ic | 0.09040266763987292 | 0.09040266763987292 | -0.03339372389698521 | 0.18640231121237658 | 0.14058594140585942 | 683 | 3 | ok | 0.33270006332700064 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | auc | -0.025138107263107258 | -0.025138107263107258 | -0.08415962213599408 | 0.006760056099614023 | 0.32926707329267074 | 410 | 3 | ok | 0.5762173782621738 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | balanced_accuracy | -0.0066099144757681355 | -0.0066099144757681355 | -0.05436679292929294 | 0.0242987991852321 | 0.7456254374562544 | 410 | 3 | ok | 0.8698963436989634 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | brier | 0.011571993980596386 | -0.011571993980596386 | -0.023546653321133038 | 0.004444300283347218 | 0.14258574142585742 | 807 | 3 | ok | 0.33270006332700064 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | f1 | -0.041382752501504444 | -0.041382752501504444 | -0.10533998160360562 | 0.035758717993776154 | 0.29027097290270976 | 807 | 3 | ok | 0.5762173782621738 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | log_loss | 0.026692916062676472 | -0.026692916062676472 | -0.052256515214892926 | 0.007233817844308378 | 0.10938906109389061 | 807 | 3 | ok | 0.33270006332700064 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | precision_at_10 | -0.0005494505494505505 | -0.0005494505494505505 | nan | nan | nan | 182 | 2 | not_estimable | nan | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | precision_at_5 | -0.005764966740576497 | -0.005764966740576497 | -0.029711751662971173 | 0.011086474501108652 | 0.6322367763223677 | 451 | 3 | ok | 0.8372435483724355 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | rank_ic | 0.004340293012006788 | 0.004340293012006788 | -0.1038749897964466 | 0.06951895445107652 | 0.9239076092390761 | 683 | 3 | ok | 0.9239076092390761 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | auc | 0.02127257182744988 | 0.02127257182744988 | -0.02449781548058987 | 0.07407400493025493 | 0.48255174482551744 | 410 | 3 | ok | 0.8679132086791321 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | balanced_accuracy | -0.012226577622919088 | -0.012226577622919088 | -0.0562584952310562 | 0.02118608999401681 | 0.5327467253274673 | 410 | 3 | ok | 0.8774651946570049 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | brier | 0.0400382332943889 | -0.0400382332943889 | -0.07335730362581046 | -0.010481024603763673 | 0.017198280171982803 | 807 | 3 | ok | 0.0963103689631037 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | f1 | 0.0027017128119709672 | 0.0027017128119709672 | -0.04320451109514778 | 0.05038620522696103 | 0.9231076892310769 | 807 | 3 | ok | 0.9667329563339961 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | log_loss | 0.4159637825541732 | -0.4159637825541732 | -0.6284024180992815 | -0.24765955397223824 | 9.999000099990002e-05 | 807 | 3 | ok | 0.0009332400093324001 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | precision_at_10 | -0.0005494505494505479 | -0.0005494505494505479 | nan | nan | nan | 182 | 2 | not_estimable | nan | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | precision_at_5 | -0.016407982261640797 | -0.016407982261640797 | -0.040354767184035474 | 0.0022172949002217295 | 0.2278772122787721 | 451 | 3 | ok | 0.5317134953171349 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | rank_ic | -0.0323787254751377 | -0.0323787254751377 | -0.10835703465642872 | 0.0657714629608365 | 0.49595040495950404 | 683 | 3 | ok | 0.8679132086791321 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | auc | 0.03649745275050153 | 0.03649745275050153 | -0.007718600420582128 | 0.08786174319413649 | 0.20667933206679331 | 410 | 3 | ok | 0.5317134953171349 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | balanced_accuracy | 0.0043376711364516264 | 0.0043376711364516264 | -0.03898793576003941 | 0.04947649733396684 | 0.8669133086691331 | 410 | 3 | ok | 0.9667329563339961 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | brier | -0.001922095355014697 | 0.001922095355014697 | -0.011779773071347643 | 0.011687536889639003 | 0.7768223177682232 | 807 | 3 | ok | 0.9456967346743587 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | f1 | -0.008436445327464698 | -0.008436445327464698 | -0.06863760431020922 | 0.02715539434911291 | 0.7612238776122388 | 807 | 3 | ok | 0.9456967346743587 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | log_loss | -0.005378259843203556 | 0.005378259843203556 | -0.023725399269491656 | 0.025732897994245142 | 0.708929107089291 | 807 | 3 | ok | 0.9456967346743587 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | precision_at_10 | -0.009340659340659339 | -0.009340659340659339 | nan | nan | nan | 182 | 2 | not_estimable | nan | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | precision_at_5 | -9.846767402440413e-19 | -9.846767402440413e-19 | -0.02039911308203991 | 0.01862527716186253 | 0.9892010798920108 | 451 | 3 | ok | 0.9892010798920108 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | rank_ic | -0.06898986417523402 | -0.06898986417523402 | -0.15764478288865444 | 0.03328991307017525 | 0.19138086191380863 | 683 | 3 | ok | 0.5317134953171349 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | auc | 0.02673947958094299 | 0.02673947958094299 | -0.042634943145156555 | 0.09919912738007249 | 0.49135086491350866 | 410 | 3 | ok | 0.8679132086791321 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | balanced_accuracy | 0.008746216520606767 | 0.008746216520606767 | -0.05279371788441911 | 0.05373436565128637 | 0.7591240875912408 | 410 | 3 | ok | 0.9456967346743587 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | brier | 0.07798502042115131 | -0.07798502042115131 | -0.10871989116802824 | -0.0445235045193722 | 9.999000099990002e-05 | 807 | 3 | ok | 0.0009332400093324001 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | f1 | 0.0963972773506996 | 0.0963972773506996 | 0.04245034498459205 | 0.16507017007065922 | 0.003999600039996 | 807 | 3 | ok | 0.027997200279972004 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | log_loss | 0.8049727920404776 | -0.8049727920404776 | -1.0051847319237157 | -0.5957738431148694 | 9.999000099990002e-05 | 807 | 3 | ok | 0.0009332400093324001 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | precision_at_10 | -0.005494505494505492 | -0.005494505494505492 | nan | nan | nan | 182 | 2 | not_estimable | nan | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | precision_at_5 | -0.005764966740576492 | -0.005764966740576492 | -0.05631929046563192 | 0.04035476718403548 | 0.8308169183081692 | 451 | 3 | ok | 0.9667329563339961 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | rank_ic | 0.05802394216473522 | 0.05802394216473522 | -0.06500973129162463 | 0.1733911520668689 | 0.36596340365963403 | 683 | 3 | ok | 0.7882288694207502 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | auc | 0.011359345487394278 | 0.011359345487394278 | -0.04930682775050152 | 0.05708421764831824 | 0.7281271872812719 | 410 | 3 | ok | 0.9456967346743587 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | balanced_accuracy | -0.002272243339316509 | -0.002272243339316509 | -0.058955497923485735 | 0.04099572048886073 | 0.9322067793220677 | 410 | 3 | ok | 0.9667329563339961 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | brier | 0.009649898625581688 | -0.009649898625581688 | -0.022810546779453426 | 0.0027864475379550105 | 0.19658034196580343 | 807 | 3 | ok | 0.5317134953171349 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | f1 | -0.049819197828969125 | -0.049819197828969125 | -0.11882485942223732 | 0.010750892412972172 | 0.15528447155284472 | 807 | 3 | ok | 0.5317134953171349 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | log_loss | 0.02131465621947292 | -0.02131465621947292 | -0.049566307428841105 | 0.0050800291148219425 | 0.1810818918108189 | 807 | 3 | ok | 0.5317134953171349 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | precision_at_10 | -0.009890109890109891 | -0.009890109890109891 | nan | nan | nan | 182 | 2 | not_estimable | nan | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | precision_at_5 | -0.005764966740576496 | -0.005764966740576496 | -0.02971175166297118 | 0.012416851441241685 | 0.684031596840316 | 451 | 3 | ok | 0.9456967346743587 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | rank_ic | -0.06464957116322723 | -0.06464957116322723 | -0.16908479254261286 | 0.014875701104654202 | 0.21397860213978603 | 683 | 3 | ok | 0.5317134953171349 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | auc | 0.012244260256455374 | 0.012244260256455374 | -0.02162157760092212 | 0.03256326582462253 | 0.4383561643835616 | 410 | 3 | ok | 0.88996100389961 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | balanced_accuracy | 0.021944092492872977 | 0.021944092492872977 | -0.006651173098581638 | 0.049755284772815246 | 0.15348465153484653 | 410 | 3 | ok | 0.88996100389961 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | brier | -0.0005943924449596173 | 0.0005943924449596173 | -0.005439606860202177 | 0.010133742185577192 | 0.8847115288471152 | 807 | 3 | ok | 0.9511048895110489 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | f1 | 0.021466275465723023 | 0.021466275465723023 | -0.021837963617214257 | 0.064178774623447 | 0.36706329367063295 | 807 | 3 | ok | 0.88996100389961 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | log_loss | 0.0020846381554013946 | -0.0020846381554013946 | -0.016590946476481478 | 0.021702305496548568 | 0.8485151484851515 | 807 | 3 | ok | 0.9511048895110489 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | precision_at_10 | -0.01098901098901099 | -0.01098901098901099 | nan | nan | nan | 182 | 2 | not_estimable | nan | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | precision_at_5 | -0.012416851441241685 | -0.012416851441241685 | -0.03636363636363636 | -0.0008869179600886916 | 0.31456854314568544 | 451 | 3 | ok | 0.88996100389961 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | rank_ic | 0.008308945481237593 | 0.008308945481237593 | -0.046242420996428606 | 0.060176832058615105 | 0.7804219578042195 | 683 | 3 | ok | 0.9511048895110489 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | auc | 0.0016556447166203257 | 0.0016556447166203257 | -0.043451236339879636 | 0.04652011938490597 | 0.9511048895110489 | 410 | 3 | ok | 0.9511048895110489 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | balanced_accuracy | 0.003721931862175764 | 0.003721931862175764 | -0.02108741047231901 | 0.03141470673635306 | 0.7887211278872113 | 410 | 3 | ok | 0.9511048895110489 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | brier | 0.0022228670847979403 | -0.0022228670847979403 | -0.00920297230279527 | 0.006237898754089972 | 0.6123387661233877 | 807 | 3 | ok | 0.9511048895110489 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | f1 | 0.022867483894162224 | 0.022867483894162224 | -0.0156556726402834 | 0.0861891209973705 | 0.4353564643535646 | 807 | 3 | ok | 0.88996100389961 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | log_loss | 0.006017561513524482 | -0.006017561513524482 | -0.020653452109143353 | 0.011260813095110624 | 0.5085491450854914 | 807 | 3 | ok | 0.88996100389961 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | precision_at_10 | 0.006593406593406592 | 0.006593406593406592 | nan | nan | nan | 182 | 2 | not_estimable | nan | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | precision_at_5 | 0.02483370288248337 | 0.02483370288248337 | -0.003104212860310422 | 0.052782705099778116 | 0.12458754124587541 | 451 | 3 | ok | 0.88996100389961 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | rank_ic | -0.026609779675338452 | -0.026609779675338452 | -0.08571054414472268 | 0.05000028277837249 | 0.5003499650034996 | 683 | 3 | ok | 0.88996100389961 | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | top5_net_return | 0.004954797552042227 | 0.004954797552042227 | -0.0062492272847909985 | 0.018779369464036175 | 0.7496250374962504 | 22 | 3 | ok | 0.7496250374962504 | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | top5_net_excess_return | 0.004954797552042225 | 0.004954797552042225 | -0.006249227284790995 | 0.018779369464036164 | 0.6268373162683731 | 22 | 3 | ok | 0.7496250374962504 | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | top10_net_return | -0.0053360837275767525 | -0.0053360837275767525 | nan | nan | nan | 9 | 1 | not_estimable_in_pilot | nan | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | top10_net_excess_return | -0.00533608372757674 | -0.00533608372757674 | nan | nan | nan | 9 | 1 | not_estimable_in_pilot | nan | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | top5_net_return | -0.0066885101530232164 | -0.0066885101530232164 | -0.012778567349418497 | -0.001764010048756473 | 0.24637536246375363 | 22 | 3 | ok | 0.49275072492750727 | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | top5_net_excess_return | -0.0066885101530232164 | -0.0066885101530232164 | -0.012778567349418495 | -0.0017640100487564707 | 0.24637536246375363 | 22 | 3 | ok | 0.49275072492750727 | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | top10_net_return | 0.00029975034853111277 | 0.00029975034853111277 | nan | nan | nan | 9 | 1 | not_estimable_in_pilot | nan | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | top10_net_excess_return | 0.00029975034853111835 | 0.00029975034853111835 | nan | nan | nan | 9 | 1 | not_estimable_in_pilot | nan | True | True | False |

## Matched Top-K T1

| family | model | k | periods | folds | status | drop_reason |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | LogisticRegression | 5 | 22 | 3 | ok |  |
| T1 | LogisticRegression | 10 | 9 | 1 | not_estimable_in_pilot | universe_below_k |
| T1 | RandomForest | 5 | 22 | 3 | ok |  |
| T1 | RandomForest | 10 | 9 | 1 | not_estimable_in_pilot | universe_below_k |

## Selection and provenance limitation

Pilot sample was stratified using keyword-derived buckets. Canonical annotation manifests are legacy-reconstructed and represent three runs from two model families; this limits provenance and blocks full-corpus or superiority claims.

## Allowed claims

Only out-of-sample deltas on common stratified article spine. Pilot/sample500 cannot support full-corpus superiority, alpha, ground-truth, or causal claims.

## Replication requirement

Independent larger and full-corpus replication with same preregistered protocol is required.
