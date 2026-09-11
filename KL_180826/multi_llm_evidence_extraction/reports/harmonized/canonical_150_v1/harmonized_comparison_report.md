# Harmonized keyword–semantic comparison

- Run: `canonical_150_v1`
- Mode: `pilot`
- Protocol SHA256: `be96a76960d08314e68e2d4db0f63f9540881eb36916a74c273366ea449255bc`
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
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | auc | 0.007498585374525228 | 0.007498585374525228 | -0.05545351033678101 | 0.07458147045101925 | 0.8124187581241876 | 665 | 3 | ok | 0.9696030396960303 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | balanced_accuracy | 0.008579976831856531 | 0.008579976831856531 | -0.032601336946261765 | 0.04799131079864161 | 0.6653334666533347 | 665 | 3 | ok | 0.9696030396960303 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | brier | 0.03794678712676241 | -0.03794678712676241 | -0.06898786070304747 | -0.000978942617033778 | 0.0428957104289571 | 807 | 3 | ok | 0.2001799820017998 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | f1 | 0.09369556453872865 | 0.09369556453872865 | 0.04945146361701773 | 0.1480079015997364 | 0.006099390060993901 | 807 | 3 | ok | 0.042695730426957304 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | log_loss | 0.38900900948630457 | -0.38900900948630457 | -0.5702515536886523 | -0.1566874915457269 | 0.0008999100089991 | 807 | 3 | ok | 0.0125987401259874 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | precision_at_10 | -0.0011152416356877322 | -0.0011152416356877322 | -0.006567534076827756 | 0.0037174721189591068 | 0.7476252374762524 | 807 | 3 | ok | 0.9696030396960303 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | rank_ic | 0.09040266763987292 | 0.09040266763987292 | -0.03936357707082331 | 0.18770522120482586 | 0.17448255174482552 | 683 | 3 | ok | 0.4071259540712595 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | auc | -0.03621033943778304 | -0.03621033943778304 | -0.09616078696261965 | 0.015185490844090457 | 0.21507849215078492 | 665 | 3 | ok | 0.43015698430156984 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | balanced_accuracy | 0.0019604476559363783 | 0.0019604476559363783 | -0.04956194327810869 | 0.05391333176013626 | 0.9435056494350565 | 665 | 3 | ok | 0.9696030396960303 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | brier | 0.011571993980596378 | -0.011571993980596378 | -0.024096833204133236 | 0.004431969244556559 | 0.1421857814218578 | 807 | 3 | ok | 0.39812018798120186 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | f1 | -0.041382752501504444 | -0.041382752501504444 | -0.10867122287408837 | 0.036964550698035 | 0.27107289271072893 | 807 | 3 | ok | 0.47437756224377564 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | log_loss | 0.026692916062676455 | -0.026692916062676455 | -0.053433299680515335 | 0.007375450329861578 | 0.11038896110388961 | 807 | 3 | ok | 0.38636136386361364 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | precision_at_10 | -0.00012391573729863704 | -0.00012391573729863704 | -0.004213135068153656 | 0.0038413878562577443 | 0.9696030396960303 | 807 | 3 | ok | 0.9696030396960303 | True | True | False |
| P1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | rank_ic | 0.004340293012006788 | 0.004340293012006788 | -0.11430823728574688 | 0.06635899570230604 | 0.9363063693630637 | 683 | 3 | ok | 0.9696030396960303 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | auc | 0.009511480304713386 | 0.009511480304713386 | -0.042133662800580104 | 0.057068897883653526 | 0.7243275672432756 | 665 | 3 | ok | 0.8195641974264112 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | balanced_accuracy | -0.01971388678155596 | -0.01971388678155596 | -0.059095213944368084 | 0.025718057318621205 | 0.39176082391760825 | 665 | 3 | ok | 0.720927907209279 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | brier | 0.0400382332943889 | -0.0400382332943889 | -0.07358891589037261 | -0.009492169666972835 | 0.017598240175982403 | 807 | 3 | ok | 0.09855014498550145 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | f1 | 0.0027017128119709672 | 0.0027017128119709672 | -0.04184948457921543 | 0.052280651284256505 | 0.9281071892810719 | 807 | 3 | ok | 0.9624815296248154 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | log_loss | 0.4159637825541732 | -0.4159637825541732 | -0.6290091245059075 | -0.24061892518099404 | 9.999000099990002e-05 | 807 | 3 | ok | 0.0009332400093324001 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | precision_at_10 | -0.00012391573729863658 | -0.00012391573729863658 | -0.0022304832713754635 | 0.0027292441140024347 | 0.9911008899110089 | 807 | 3 | ok | 0.9911008899110089 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | LogisticRegression | rank_ic | -0.0323787254751377 | -0.0323787254751377 | -0.11734066037663528 | 0.07062965888412764 | 0.5214478552144786 | 683 | 3 | ok | 0.811141108111411 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | auc | -0.013278621754185658 | -0.013278621754185658 | -0.07100198969785435 | 0.03507911161694051 | 0.6744325567443256 | 665 | 3 | ok | 0.8195641974264112 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | balanced_accuracy | -0.04109404797374722 | -0.04109404797374722 | -0.10248674367612336 | 0.009601786632331735 | 0.17398260173982602 | 665 | 3 | ok | 0.45425457454254575 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | brier | -0.0019220953550146882 | 0.0019220953550146882 | -0.012178586247085496 | 0.011942754493067182 | 0.7552244775522448 | 807 | 3 | ok | 0.8195641974264112 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | f1 | -0.008436445327464698 | -0.008436445327464698 | -0.07073217461678193 | 0.027510675639898067 | 0.761023897610239 | 807 | 3 | ok | 0.8195641974264112 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | log_loss | -0.005378259843203539 | 0.005378259843203539 | -0.024653032350634905 | 0.02642124613764151 | 0.6782321767823217 | 807 | 3 | ok | 0.8195641974264112 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | precision_at_10 | -0.0021065675340768276 | -0.0021065675340768276 | -0.007930607187112764 | 0.0022304832713754648 | 0.49955004499550043 | 807 | 3 | ok | 0.811141108111411 | True | True | False |
| S1 | E_technical_coverage | B_technical_coverage_keyword | RandomForest | rank_ic | -0.06898986417523402 | -0.06898986417523402 | -0.14946340002683 | 0.03470430913104938 | 0.17368263173682633 | 683 | 3 | ok | 0.45425457454254575 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | auc | 0.017010065679238615 | 0.017010065679238615 | -0.04919924532095584 | 0.08416750787502666 | 0.6191380861913809 | 665 | 3 | ok | 0.8195641974264112 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | balanced_accuracy | -0.011133909949699426 | -0.011133909949699426 | -0.06465108460879138 | 0.045156721933037686 | 0.7134286571342866 | 665 | 3 | ok | 0.8195641974264112 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | brier | 0.07798502042115131 | -0.07798502042115131 | -0.10999906776166828 | -0.04359783084120162 | 9.999000099990002e-05 | 807 | 3 | ok | 0.0009332400093324001 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | f1 | 0.0963972773506996 | 0.0963972773506996 | 0.04208776447815373 | 0.16748691350025552 | 0.0040995900409959 | 807 | 3 | ok | 0.028697130286971302 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | log_loss | 0.8049727920404776 | -0.8049727920404776 | -1.0103075538536141 | -0.5908067609354423 | 9.999000099990002e-05 | 807 | 3 | ok | 0.0009332400093324001 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | precision_at_10 | -0.0012391573729863688 | -0.0012391573729863688 | -0.006939281288723668 | 0.003717472118959109 | 0.7470252974702529 | 807 | 3 | ok | 0.8195641974264112 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | LogisticRegression | rank_ic | 0.05802394216473522 | 0.05802394216473522 | -0.07733210240574896 | 0.16972942542011132 | 0.411958804119588 | 683 | 3 | ok | 0.720927907209279 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | auc | -0.04948896119196871 | -0.04948896119196871 | -0.11698768565394506 | 0.000457877287012633 | 0.1272872712728727 | 665 | 3 | ok | 0.45425457454254575 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | balanced_accuracy | -0.039133600317810845 | -0.039133600317810845 | -0.08982026426998231 | -0.0004038932037052461 | 0.19468053194680532 | 665 | 3 | ok | 0.45425457454254575 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | brier | 0.00964989862558169 | -0.00964989862558169 | -0.022843329830241375 | 0.003286039987410897 | 0.18498150184981502 | 807 | 3 | ok | 0.45425457454254575 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | f1 | -0.049819197828969125 | -0.049819197828969125 | -0.12178695252534692 | 0.010693348188413561 | 0.17678232176782321 | 807 | 3 | ok | 0.45425457454254575 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | log_loss | 0.021314656219472913 | -0.021314656219472913 | -0.049238719041755495 | 0.006017773363049279 | 0.16478352164783522 | 807 | 3 | ok | 0.45425457454254575 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | precision_at_10 | -0.002230483271375465 | -0.002230483271375465 | -0.007558859975216852 | 0.0028500619578686486 | 0.39576042395760425 | 807 | 3 | ok | 0.720927907209279 | True | True | False |
| S1 | E_technical_coverage | C_technical_coverage_semantic | RandomForest | rank_ic | -0.06464957116322723 | -0.06464957116322723 | -0.1735481089200177 | 0.012640154871392167 | 0.2206779322067793 | 683 | 3 | ok | 0.4753063155222939 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | auc | -0.001159583663343063 | -0.001159583663343063 | -0.03465111294650768 | 0.03759598421106878 | 0.9605039496050395 | 665 | 3 | ok | 0.9605039496050395 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | balanced_accuracy | 0.010482103527216307 | 0.010482103527216307 | -0.037750476705833855 | 0.04519251727804358 | 0.6358364163583642 | 665 | 3 | ok | 0.9082291770822917 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | brier | -0.0005943924449596173 | 0.0005943924449596173 | -0.0059936215438497085 | 0.01048446531852609 | 0.8881111888811118 | 807 | 3 | ok | 0.9564274341796589 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | f1 | 0.021466275465723023 | 0.021466275465723023 | -0.024616807418715355 | 0.065673605392414 | 0.3544645535446455 | 807 | 3 | ok | 0.9082291770822917 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | log_loss | 0.0020846381554013946 | -0.0020846381554013946 | -0.01749944983299088 | 0.022468103582759646 | 0.8367163283671633 | 807 | 3 | ok | 0.9564274341796589 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | precision_at_10 | -0.0024783147459727386 | -0.0024783147459727386 | -0.0055762081784386614 | -0.00037174721189591083 | 0.18688131186881313 | 807 | 3 | ok | 0.9082291770822917 | True | True | False |
| S2 | A_technical | E_technical_coverage | LogisticRegression | rank_ic | 0.008308945481237593 | 0.008308945481237593 | -0.044353503409745566 | 0.06058660404313231 | 0.7784221577842215 | 683 | 3 | ok | 0.9564274341796589 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | auc | -0.012628338523075362 | -0.012628338523075362 | -0.06788814421967615 | 0.02667137509176981 | 0.6487351264873512 | 665 | 3 | ok | 0.9082291770822917 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | balanced_accuracy | 0.009192922783148344 | 0.009192922783148344 | -0.00918398675259578 | 0.037809359708795745 | 0.4851514848515148 | 665 | 3 | ok | 0.9082291770822917 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | brier | 0.0022228670847979385 | -0.0022228670847979385 | -0.009442854245407063 | 0.006531870402146542 | 0.5805419458054195 | 807 | 3 | ok | 0.9082291770822917 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | f1 | 0.022867483894162224 | 0.022867483894162224 | -0.017318931028476186 | 0.08835920275511353 | 0.45645435456454353 | 807 | 3 | ok | 0.9082291770822917 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | log_loss | 0.006017561513524492 | -0.006017561513524492 | -0.021199690904103487 | 0.011795111147786858 | 0.48135186481351866 | 807 | 3 | ok | 0.9082291770822917 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | precision_at_10 | 0.0014869888475836429 | 0.0014869888475836429 | -0.001982651796778191 | 0.004708798017348202 | 0.4443555644435556 | 807 | 3 | ok | 0.9082291770822917 | True | True | False |
| S2 | A_technical | E_technical_coverage | RandomForest | rank_ic | -0.026609779675338452 | -0.026609779675338452 | -0.08712156054361178 | 0.05048998077043494 | 0.537946205379462 | 683 | 3 | ok | 0.9082291770822917 | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | top5_net_return | 0.004954797552042227 | 0.004954797552042227 | 0.004954797552042227 | 0.004954797552042227 | 1.0 | 22 | 3 | ok | 1.0 | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | top5_net_excess_return | 0.004954797552042225 | 0.004954797552042225 | 0.004954797552042225 | 0.004954797552042225 | 0.5101489851014899 | 22 | 3 | ok | 1.0 | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | top10_net_return | -0.0053360837275767525 | -0.0053360837275767525 | -0.0053360837275767525 | -0.0053360837275767525 | 1.0 | 9 | 1 | ok | 1.0 | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | LogisticRegression | top10_net_excess_return | -0.00533608372757674 | -0.00533608372757674 | -0.00533608372757674 | -0.00533608372757674 | 1.0 | 9 | 1 | ok | 1.0 | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | top5_net_return | -0.0066885101530232164 | -0.0066885101530232164 | -0.0066885101530232164 | -0.0066885101530232164 | 0.7426257374262574 | 22 | 3 | ok | 1.0 | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | top5_net_excess_return | -0.0066885101530232164 | -0.0066885101530232164 | -0.0066885101530232164 | -0.0066885101530232164 | 0.7426257374262574 | 22 | 3 | ok | 1.0 | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | top10_net_return | 0.00029975034853111277 | 0.00029975034853111277 | 0.00029975034853111277 | 0.00029975034853111277 | 1.0 | 9 | 1 | ok | 1.0 | True | True | False |
| T1 | B_technical_coverage_keyword | C_technical_coverage_semantic | RandomForest | top10_net_excess_return | 0.00029975034853111835 | 0.00029975034853111835 | 0.00029975034853111835 | 0.00029975034853111835 | 1.0 | 9 | 1 | ok | 1.0 | True | True | False |

## Matched Top-K T1

| family | model | k | periods | status | drop_reason |
| --- | --- | --- | --- | --- | --- |
| T1 | LogisticRegression | 5 | 22 | ok |  |
| T1 | LogisticRegression | 10 | 9 | ok |  |
| T1 | RandomForest | 5 | 22 | ok |  |
| T1 | RandomForest | 10 | 9 | ok |  |

## Selection and provenance limitation

Pilot sample was stratified using keyword-derived buckets. Canonical annotation manifests are legacy-reconstructed and represent three runs from two model families; this limits provenance and blocks full-corpus or superiority claims.

## Allowed claims

Only out-of-sample deltas on common stratified article spine. Pilot/sample500 cannot support full-corpus superiority, alpha, ground-truth, or causal claims.

## Replication requirement

Independent larger and full-corpus replication with same preregistered protocol is required.
