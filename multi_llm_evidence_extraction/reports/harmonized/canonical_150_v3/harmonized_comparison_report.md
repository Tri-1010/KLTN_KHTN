# Harmonized keyword–semantic comparison

- Run: `canonical_150_v3`
- Mode: `pilot`
- Protocol SHA256: `15c2f01f39850a524af24a37931f885e8bf0434a52400732f76f24dde4298a31`
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
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | auc | 0.005466907753493111 | 0.005466907753493111 | -0.07395695536960782 | 0.06850298051654757 | 0.8922107789221078 | 410 | 3 | ok | 0.9696030396960303 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | balanced_accuracy | 0.020972794143525843 | 0.020972794143525843 | -0.039221179565691766 | 0.06872227281526058 | 0.4928507149285071 | 410 | 3 | ok | 0.7666566676665666 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | brier | 0.03794678712676241 | -0.03794678712676241 | -0.06898786070304747 | -0.000978942617033778 | 0.0428957104289571 | 807 | 3 | ok | 0.2001799820017998 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | f1 | 0.09369556453872865 | 0.09369556453872865 | 0.04945146361701773 | 0.1480079015997364 | 0.006099390060993901 | 807 | 3 | ok | 0.042695730426957304 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | log_loss | 0.38900900948630457 | -0.38900900948630457 | -0.5702515536886523 | -0.1566874915457269 | 0.0008999100089991 | 807 | 3 | ok | 0.0125987401259874 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | precision_at_10 | -0.0011152416356877322 | -0.0011152416356877322 | -0.006567534076827756 | 0.0037174721189591068 | 0.7476252374762524 | 807 | 3 | ok | 0.9696030396960303 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | rank_ic | 0.09040266763987292 | 0.09040266763987292 | -0.03936357707082331 | 0.18770522120482586 | 0.17448255174482552 | 683 | 3 | ok | 0.4071259540712595 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | auc | -0.025138107263107258 | -0.025138107263107258 | -0.08908286633759192 | -0.0005159478789051996 | 0.43255674432556745 | 410 | 3 | ok | 0.7569743025697431 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | balanced_accuracy | -0.0066099144757681355 | -0.0066099144757681355 | -0.057307059048674905 | 0.022603066818005828 | 0.8066193380661933 | 410 | 3 | ok | 0.9696030396960303 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | brier | 0.011571993980596383 | -0.011571993980596383 | -0.024096833204133247 | 0.004431969244556557 | 0.1421857814218578 | 807 | 3 | ok | 0.39812018798120186 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | f1 | -0.041382752501504444 | -0.041382752501504444 | -0.10867122287408837 | 0.036964550698035 | 0.27107289271072893 | 807 | 3 | ok | 0.5421457854214579 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | log_loss | 0.026692916062676465 | -0.026692916062676465 | -0.05343329968051535 | 0.007375450329861553 | 0.11038896110388961 | 807 | 3 | ok | 0.38636136386361364 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | precision_at_10 | -0.00012391573729863704 | -0.00012391573729863704 | -0.004213135068153656 | 0.0038413878562577443 | 0.9696030396960303 | 807 | 3 | ok | 0.9696030396960303 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | rank_ic | 0.004340293012006788 | 0.004340293012006788 | -0.11430823728574688 | 0.06635899570230604 | 0.9363063693630637 | 683 | 3 | ok | 0.9696030396960303 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | auc | 0.02127257182744988 | 0.02127257182744988 | -0.02623477127547248 | 0.08236740385856238 | 0.5322467753224678 | 410 | 3 | ok | 0.8812896488128964 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | balanced_accuracy | -0.012226577622919088 | -0.012226577622919088 | -0.052057111841410625 | 0.02130616377186498 | 0.5622437756224378 | 410 | 3 | ok | 0.8812896488128964 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | brier | 0.0400382332943889 | -0.0400382332943889 | -0.07358891589037261 | -0.009492169666972835 | 0.017598240175982403 | 807 | 3 | ok | 0.09855014498550145 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | f1 | 0.0027017128119709672 | 0.0027017128119709672 | -0.04184948457921543 | 0.052280651284256505 | 0.9281071892810719 | 807 | 3 | ok | 0.9820795698207957 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | log_loss | 0.4159637825541732 | -0.4159637825541732 | -0.6290091245059075 | -0.24061892518099404 | 9.999000099990002e-05 | 807 | 3 | ok | 0.0009332400093324001 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | precision_at_10 | -0.00012391573729863658 | -0.00012391573729863658 | -0.0022304832713754635 | 0.0027292441140024347 | 0.9911008899110089 | 807 | 3 | ok | 0.9911008899110089 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | rank_ic | -0.0323787254751377 | -0.0323787254751377 | -0.11734066037663528 | 0.07062965888412764 | 0.5214478552144786 | 683 | 3 | ok | 0.8812896488128964 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | auc | 0.03649745275050153 | 0.03649745275050153 | -0.0006471505120895321 | 0.08924945110219498 | 0.18938106189381063 | 410 | 3 | ok | 0.5302669733026698 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | balanced_accuracy | 0.0043376711364516264 | 0.0043376711364516264 | -0.04003711219336219 | 0.055607399121880806 | 0.8744125587441256 | 410 | 3 | ok | 0.9793420657934206 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | brier | -0.0019220953550146923 | 0.0019220953550146923 | -0.012178586247085486 | 0.011942754493067188 | 0.7552244775522448 | 807 | 3 | ok | 0.895677098956771 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | f1 | -0.008436445327464698 | -0.008436445327464698 | -0.07073217461678193 | 0.027510675639898067 | 0.761023897610239 | 807 | 3 | ok | 0.895677098956771 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | log_loss | -0.005378259843203548 | 0.005378259843203548 | -0.0246530323506349 | 0.02642124613764154 | 0.6782321767823217 | 807 | 3 | ok | 0.895677098956771 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | precision_at_10 | -0.0021065675340768276 | -0.0021065675340768276 | -0.007930607187112764 | 0.0022304832713754648 | 0.49955004499550043 | 807 | 3 | ok | 0.8812896488128964 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | rank_ic | -0.06898986417523402 | -0.06898986417523402 | -0.14946340002683 | 0.03470430913104938 | 0.17368263173682633 | 683 | 3 | ok | 0.5302669733026698 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | auc | 0.02673947958094299 | 0.02673947958094299 | -0.045485150796583725 | 0.10309045928946838 | 0.5665433456654334 | 410 | 3 | ok | 0.8812896488128964 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | balanced_accuracy | 0.008746216520606767 | 0.008746216520606767 | -0.05751373820962236 | 0.05476198835040297 | 0.7677232276772322 | 410 | 3 | ok | 0.895677098956771 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | brier | 0.07798502042115131 | -0.07798502042115131 | -0.10999906776166828 | -0.04359783084120162 | 9.999000099990002e-05 | 807 | 3 | ok | 0.0009332400093324001 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | f1 | 0.0963972773506996 | 0.0963972773506996 | 0.04208776447815373 | 0.16748691350025552 | 0.0040995900409959 | 807 | 3 | ok | 0.028697130286971302 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | log_loss | 0.8049727920404776 | -0.8049727920404776 | -1.0103075538536141 | -0.5908067609354423 | 9.999000099990002e-05 | 807 | 3 | ok | 0.0009332400093324001 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | precision_at_10 | -0.0012391573729863688 | -0.0012391573729863688 | -0.006939281288723668 | 0.003717472118959109 | 0.7470252974702529 | 807 | 3 | ok | 0.895677098956771 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | rank_ic | 0.05802394216473522 | 0.05802394216473522 | -0.07733210240574896 | 0.16972942542011132 | 0.411958804119588 | 683 | 3 | ok | 0.8812896488128964 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | auc | 0.011359345487394278 | 0.011359345487394278 | -0.05296462494427433 | 0.05805984639513601 | 0.7618238176182381 | 410 | 3 | ok | 0.895677098956771 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | balanced_accuracy | -0.002272243339316509 | -0.002272243339316509 | -0.06217619905501003 | 0.045285581204026266 | 0.947005299470053 | 410 | 3 | ok | 0.9820795698207957 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | brier | 0.009649898625581686 | -0.009649898625581686 | -0.02284332983024138 | 0.0032860399874108936 | 0.18498150184981502 | 807 | 3 | ok | 0.5302669733026698 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | f1 | -0.049819197828969125 | -0.049819197828969125 | -0.12178695252534692 | 0.010693348188413561 | 0.17678232176782321 | 807 | 3 | ok | 0.5302669733026698 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | log_loss | 0.021314656219472917 | -0.021314656219472917 | -0.049238719041755516 | 0.006017773363049282 | 0.16478352164783522 | 807 | 3 | ok | 0.5302669733026698 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | precision_at_10 | -0.002230483271375465 | -0.002230483271375465 | -0.007558859975216852 | 0.0028500619578686486 | 0.39576042395760425 | 807 | 3 | ok | 0.8812896488128964 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | rank_ic | -0.06464957116322723 | -0.06464957116322723 | -0.1735481089200177 | 0.012640154871392167 | 0.2206779322067793 | 683 | 3 | ok | 0.5617256456172565 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | auc | 0.012244260256455374 | 0.012244260256455374 | -0.024272490585295462 | 0.02907059253979986 | 0.47965203479652035 | 410 | 3 | ok | 0.9030652490306524 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | balanced_accuracy | 0.021944092492872977 | 0.021944092492872977 | -0.0091523785327139 | 0.04307581036849328 | 0.23967603239676033 | 410 | 3 | ok | 0.9030652490306524 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | brier | -0.0005943924449596173 | 0.0005943924449596173 | -0.0059936215438497085 | 0.01048446531852609 | 0.8881111888811118 | 807 | 3 | ok | 0.9564274341796589 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | f1 | 0.021466275465723023 | 0.021466275465723023 | -0.024616807418715355 | 0.065673605392414 | 0.3544645535446455 | 807 | 3 | ok | 0.9030652490306524 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | log_loss | 0.0020846381554013946 | -0.0020846381554013946 | -0.01749944983299088 | 0.022468103582759646 | 0.8367163283671633 | 807 | 3 | ok | 0.9564274341796589 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | precision_at_10 | -0.0024783147459727386 | -0.0024783147459727386 | -0.0055762081784386614 | -0.00037174721189591083 | 0.18688131186881313 | 807 | 3 | ok | 0.9030652490306524 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | rank_ic | 0.008308945481237593 | 0.008308945481237593 | -0.044353503409745566 | 0.06058660404313231 | 0.7784221577842215 | 683 | 3 | ok | 0.9564274341796589 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | auc | 0.0016556447166203257 | 0.0016556447166203257 | -0.04685927777337839 | 0.04275131992837784 | 0.9612038796120388 | 410 | 3 | ok | 0.9612038796120388 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | balanced_accuracy | 0.003721931862175764 | 0.003721931862175764 | -0.019706821041424703 | 0.03326622386759581 | 0.835016498350165 | 410 | 3 | ok | 0.9564274341796589 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | brier | 0.0022228670847979385 | -0.0022228670847979385 | -0.009442854245407056 | 0.00653187040214654 | 0.5805419458054195 | 807 | 3 | ok | 0.9030652490306524 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | f1 | 0.022867483894162224 | 0.022867483894162224 | -0.017318931028476186 | 0.08835920275511353 | 0.45645435456454353 | 807 | 3 | ok | 0.9030652490306524 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | log_loss | 0.006017561513524484 | -0.006017561513524484 | -0.021199690904103487 | 0.011795111147786877 | 0.48135186481351866 | 807 | 3 | ok | 0.9030652490306524 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | precision_at_10 | 0.0014869888475836429 | 0.0014869888475836429 | -0.001982651796778191 | 0.004708798017348202 | 0.4443555644435556 | 807 | 3 | ok | 0.9030652490306524 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | rank_ic | -0.026609779675338452 | -0.026609779675338452 | -0.08712156054361178 | 0.05048998077043494 | 0.537946205379462 | 683 | 3 | ok | 0.9030652490306524 | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | top5_net_return | 0.004954797552042227 | 0.004954797552042227 | nan | nan | nan | 22 | 3 | not_estimable_degenerate_bootstrap | nan | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | top5_net_excess_return | 0.004954797552042225 | 0.004954797552042225 | nan | nan | nan | 22 | 3 | not_estimable_degenerate_bootstrap | nan | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | top10_net_return | -0.0053360837275767525 | -0.0053360837275767525 | nan | nan | nan | 9 | 1 | not_estimable_in_pilot | nan | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | top10_net_excess_return | -0.00533608372757674 | -0.00533608372757674 | nan | nan | nan | 9 | 1 | not_estimable_in_pilot | nan | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | top5_net_return | -0.0066885101530232164 | -0.0066885101530232164 | nan | nan | nan | 22 | 3 | not_estimable_degenerate_bootstrap | nan | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | top5_net_excess_return | -0.0066885101530232164 | -0.0066885101530232164 | nan | nan | nan | 22 | 3 | not_estimable_degenerate_bootstrap | nan | True | True | False |
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
