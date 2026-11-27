# Near-miss colors next to strong evidence: every judged candidate (2026-11-26)

Made by `experiments/2026-11-26_nearmiss/run.py --summary` from the judge's pages in the folders beside this file. Train frames only; every candidate against today's default; candidates with a chosen number judged leave one place out. Found = the strict rule. Margins: found better above +4.0, worse below -10.92 placements; boxes not on their barrel worse above +1.85; any new box on a clean empty frame fails. A PASS less than 2 placements above the gain margin is marked WEAK.

Baseline (the fixed model): 133.8 of 172 placements, 211 of 307 per frame, 1.9 boxes not on their barrel, 0 on clean empty frames.

| candidate | setting | verdict | found, placements | per frame | gained / lost | boxes not on their barrel | empty frames: clean, with clutter | places that moved |
|---|---|---|---|---|---|---|---|---|
| A_hyst1 | hyst:1 | **FAIL** | 143.7 (+9.8) | 234 (+23) | +30 / -7 | 6.7 (+4.8) | 0, 1.6 | home_white -2.0; abp_gray +5.0; home_bathtile +0.2; home_glass -0.4; home_ottoman +7.0; uc_palewood -1.0; abp_white +1.0 |
| A_hyst2 | hyst:2 | **FAIL** | 138.1 (+4.3) | 219 (+8) | +30 / -22 | 14.5 (+12.6) | 1, 3.6 | home_white -2.0; campus_study -1.0; abp_gray +6.0; home_bathtile -0.5; home_glass -2.2; home_ottoman +7.0; uc_palewood -2.0; abp_white -1.0 |
| A_hyst3 | hyst:3 | **FAIL** | 133.2 (-0.6) | 210 (-1) | +32 / -33 | 23.4 (+21.5) | 1, 7.6 | home_white -6.0; campus_study -1.0; abp_gray +6.0; home_glass -3.6; home_ottoman +7.0; uc_palewood -1.0; abp_white -2.0 |
| A_hyst_fit | chosen in each fold | **FAIL** | 131.8 (-2.0) | 209 (-2) | +0 / -2 | 4.9 (+3.0) | 0, 0.0 | home_white -2.0 |
| A_hyst_guard_fit | chosen in each fold | **FAIL** | 131.8 (-2.0) | 209 (-2) | +0 / -2 | 5.9 (+4.0) | 0, 0.0 | home_white -2.0 |
| B_partner_fit | chosen in each fold | **PASS** | 147.5 (+13.7) | 249 (+38) | +38 / -0 | 3.6 (+1.6) | 0, 0.4 | abp_gray +2.0; home_bathtile +5.0; home_ottoman +4.7; abp_white +2.0 |
| D_partner_free_fit | chosen in each fold | **FAIL** | 132.2 (-1.6) | 214 (+3) | +13 / -10 | 2.7 (+0.7) | 0, 0.2 | home_white -1.0; campus_study -4.0; abp_gray +2.0; home_bathtile +0.5; home_glass -0.4; home_ottoman +2.3; abp_white -1.0 |
| C_wide_fit | chosen in each fold | **PASS** | 147.5 (+13.7) | 249 (+38) | +38 / -0 | 3.6 (+1.6) | 0, 0.4 | abp_gray +2.0; home_bathtile +5.0; home_ottoman +4.7; abp_white +2.0 |
| C_stripe1 | pc:1,0,strict | **NO CLEAR DIFFERENCE** | 137.3 (+3.5) | 218 (+7) | +7 / -0 | 1.9 (+0.0) | 0, 0.0 | abp_gray +2.0; home_bathtile +0.5; home_ottoman +1.0 |
| C_stripe2 | pc:2,0,strict | **PASS (WEAK)** | 139.0 (+5.2) | 224 (+13) | +13 / -0 | 2.2 (+0.2) | 0, 0.0 | abp_gray +2.0; home_bathtile +1.5; home_ottoman +1.7 |
| C_stripe3 | pc:3,0,strict | **PASS (WEAK)** | 139.7 (+5.9) | 227 (+16) | +16 / -0 | 2.2 (+0.2) | 0, 0.0 | abp_gray +2.0; home_bathtile +2.2; home_ottoman +1.7 |
| C_stripe4 | pc:4,0,strict | **PASS** | 140.2 (+6.4) | 229 (+18) | +18 / -0 | 2.2 (+0.2) | 0, 0.0 | abp_gray +2.0; home_bathtile +2.8; home_ottoman +1.7 |
| C_stripe5 | pc:5,0,strict | **PASS** | 141.0 (+7.2) | 232 (+21) | +21 / -0 | 2.2 (+0.2) | 0, 0.0 | abp_gray +2.0; home_bathtile +3.5; home_ottoman +1.7 |
| C_stripe6 | pc:6,0,strict | **FAIL** | 144.1 (+10.3) | 243 (+32) | +33 / -1 | 5.1 (+3.2) | 0, 0.2 | abp_gray +2.0; home_bathtile +5.5; home_glass -0.2; home_ottoman +3.0 |
| C_body1 | pc:0,1,pred | **PASS (WEAK)** | 138.5 (+4.7) | 219 (+8) | +10 / -2 | 1.9 (+0.0) | 0, 0.0 | abp_gray +3.0; home_ottoman +1.7 |
| C_body2 | pc:0,2,pred | **PASS** | 141.0 (+7.2) | 227 (+16) | +16 / -0 | 2.2 (+0.2) | 0, 0.0 | abp_gray +3.0; home_bathtile +0.5; home_ottoman +3.7 |
| C_body3 | pc:0,3,pred | **PASS** | 143.9 (+10.1) | 232 (+21) | +21 / -0 | 1.9 (+0.0) | 0, 0.0 | abp_gray +4.0; home_bathtile +0.8; home_ottoman +4.3; abp_white +1.0 |
| C_body4 | pc:0,4,pred | **PASS** | 146.2 (+12.4) | 238 (+27) | +27 / -0 | 2.3 (+0.4) | 0, 0.2 | abp_gray +4.0; home_bathtile +1.8; home_ottoman +4.7; abp_white +2.0 |
| C_body5 | pc:0,5,pred | **PASS** | 147.3 (+13.5) | 239 (+28) | +28 / -0 | 3.3 (+1.4) | 0, 0.4 | abp_gray +5.0; home_bathtile +1.5; home_ottoman +5.0; abp_white +2.0 |
| C_body6 | pc:0,6,pred | **FAIL** | 148.7 (+14.9) | 245 (+34) | +34 / -0 | 5.6 (+3.7) | 0, 1.6 | abp_gray +5.0; home_bathtile +3.2; home_ottoman +4.7; abp_white +2.0 |
| C_body7 | pc:0,7,pred | **FAIL** | 142.3 (+8.5) | 242 (+31) | +38 / -7 | 45.9 (+44.0) | 3, 14.3 | home_white -2.0; campus_study -1.0; abp_gray +4.0; home_bathtile +3.5; home_ottoman +6.0; uc_palewood -1.0; abp_white -1.0 |
| C_both1_1 | pc:1,1,pred | **PASS** | 142.0 (+8.2) | 226 (+15) | +16 / -1 | 1.9 (+0.0) | 0, 0.0 | abp_gray +5.0; home_bathtile +0.5; home_ottoman +2.7 |
| C_both2_2 | pc:2,2,pred | **PASS** | 144.8 (+11.0) | 236 (+25) | +25 / -0 | 2.5 (+0.6) | 0, 0.0 | abp_gray +5.0; home_bathtile +2.0; home_ottoman +4.0 |
| C_both3_3 | pc:3,3,pred | **PASS** | 148.1 (+14.3) | 243 (+32) | +32 / -0 | 2.9 (+0.9) | 0, 0.0 | abp_gray +6.0; home_bathtile +3.0; home_ottoman +4.3; abp_white +1.0 |
| C_both4_4 | pc:4,4,pred | **PASS** | 151.0 (+17.2) | 251 (+40) | +40 / -0 | 2.9 (+1.0) | 0, 0.2 | abp_gray +6.0; home_bathtile +4.5; home_ottoman +4.7; abp_white +2.0 |
| C_both5_5 | pc:5,5,pred | **PASS** | 152.8 (+19.0) | 257 (+46) | +46 / -0 | 3.2 (+1.3) | 0, 0.4 | abp_gray +6.0; home_bathtile +5.0; home_ottoman +6.0; abp_white +2.0 |
| C_both6_6 | pc:6,6,pred | **FAIL** | 156.4 (+22.6) | 271 (+60) | +61 / -1 | 8.5 (+6.6) | 0, 1.9 | abp_gray +6.0; home_bathtile +8.5; home_glass -0.2; home_ottoman +6.3; abp_white +2.0 |
| C_both6_7 | pc:6,7,pred | **FAIL** | 151.0 (+17.2) | 269 (+58) | +66 / -8 | 50.0 (+48.1) | 3, 14.8 | home_white -2.0; campus_study -1.0; abp_gray +6.0; home_bathtile +8.8; home_glass -0.2; home_ottoman +7.7; uc_palewood -1.0; abp_white -1.0 |

## Paint, bottom edges, extreme conditions (report only)

Paint outside / inside the hand boxes: the candidate's painted pixels over the fixed model's, ordinary frames, boxes grown by 4 px. Bottoms moved: of the barrels the fixed model finds, how many get a box with another bottom row; lost: how many are no longer a strict hit (box still on the barrel but off / no box on it). Extreme: the parked conditions, found per frame and boxes not on their barrel, never judged.

| candidate | paint outside | paint inside | bottoms moved | lost: box off / missed | extreme: found per frame | extreme: boxes not on their barrel |
|---|---|---|---|---|---|---|
| A_hyst1 | x 2.58 | x 1.15 | 99 of 211 | 4 / 3 | 13 -> 29 of 167 | 4.0 -> 5.0 |
| A_hyst2 | x 6.03 | x 1.28 | 151 of 211 | 9 / 13 | 13 -> 33 of 167 | 4.0 -> 5.0 |
| A_hyst3 | x 15.27 | x 1.40 | 159 of 211 | 14 / 19 | 13 -> 32 of 167 | 4.0 -> 10.0 |
| A_hyst_fit | x 1.21 | x 1.00 | 15 of 211 | 0 / 2 | 13 -> 13 of 167 | 4.0 -> 4.0 |
| A_hyst_guard_fit | x 1.19 | x 1.00 | 0 of 211 | 0 / 2 | 13 -> 13 of 167 | 4.0 -> 4.0 |
| B_partner_fit | x 1.04 | x 1.15 | 19 of 211 | 0 / 0 | 13 -> 58 of 167 | 4.0 -> 4.0 |
| D_partner_free_fit | x 1.06 | x 1.08 | 99 of 211 | 8 / 2 | 13 -> 47 of 167 | 4.0 -> 4.0 |
| C_wide_fit | x 1.04 | x 1.15 | 19 of 211 | 0 / 0 | 13 -> 58 of 167 | 4.0 -> 4.0 |
| C_stripe1 | x 1.00 | x 1.00 | 2 of 211 | 0 / 0 | 13 -> 15 of 167 | 4.0 -> 4.0 |
| C_stripe2 | x 1.00 | x 1.01 | 2 of 211 | 0 / 0 | 13 -> 18 of 167 | 4.0 -> 4.0 |
| C_stripe3 | x 1.00 | x 1.01 | 1 of 211 | 0 / 0 | 13 -> 20 of 167 | 4.0 -> 5.0 |
| C_stripe4 | x 1.00 | x 1.01 | 2 of 211 | 0 / 0 | 13 -> 26 of 167 | 4.0 -> 5.0 |
| C_stripe5 | x 1.00 | x 1.01 | 3 of 211 | 0 / 0 | 13 -> 30 of 167 | 4.0 -> 5.0 |
| C_stripe6 | x 1.00 | x 1.02 | 3 of 211 | 0 / 1 | 13 -> 41 of 167 | 4.0 -> 7.0 |
| C_body1 | x 1.00 | x 1.03 | 6 of 211 | 0 / 2 | 13 -> 15 of 167 | 4.0 -> 2.0 |
| C_body2 | x 1.01 | x 1.09 | 13 of 211 | 0 / 0 | 13 -> 19 of 167 | 4.0 -> 2.0 |
| C_body3 | x 1.02 | x 1.11 | 16 of 211 | 0 / 0 | 13 -> 24 of 167 | 4.0 -> 2.0 |
| C_body4 | x 1.03 | x 1.12 | 16 of 211 | 0 / 0 | 13 -> 32 of 167 | 4.0 -> 3.0 |
| C_body5 | x 1.05 | x 1.15 | 17 of 211 | 0 / 0 | 13 -> 45 of 167 | 4.0 -> 3.0 |
| C_body6 | x 1.09 | x 1.15 | 20 of 211 | 0 / 0 | 13 -> 70 of 167 | 4.0 -> 4.0 |
| C_body7 | x 1.18 | x 1.18 | 17 of 211 | 0 / 7 | 13 -> 72 of 167 | 4.0 -> 33.0 |
| C_both1_1 | x 1.00 | x 1.03 | 8 of 211 | 0 / 1 | 13 -> 17 of 167 | 4.0 -> 2.0 |
| C_both2_2 | x 1.01 | x 1.09 | 14 of 211 | 0 / 0 | 13 -> 23 of 167 | 4.0 -> 2.0 |
| C_both3_3 | x 1.02 | x 1.12 | 17 of 211 | 0 / 0 | 13 -> 30 of 167 | 4.0 -> 3.0 |
| C_both4_4 | x 1.03 | x 1.14 | 17 of 211 | 0 / 0 | 13 -> 42 of 167 | 4.0 -> 4.0 |
| C_both5_5 | x 1.05 | x 1.16 | 19 of 211 | 0 / 0 | 13 -> 58 of 167 | 4.0 -> 4.0 |
| C_both6_6 | x 1.09 | x 1.17 | 20 of 211 | 0 / 1 | 13 -> 86 of 167 | 4.0 -> 7.0 |
| C_both6_7 | x 1.19 | x 1.19 | 19 of 211 | 0 / 8 | 13 -> 88 of 167 | 4.0 -> 36.0 |

## The named clutter traps (empty frames with clutter that has an orange part and a blue band)

Boxes drawn, fixed model -> candidate.

| candidate | lampmid3_bathtile_neg_02 | lampmid6_bathtile_neg_02 | lampwarm6_bathtile_neg_02 |
|---|---|---|---|
| A_hyst1 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| A_hyst2 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| A_hyst3 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| A_hyst_fit | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| A_hyst_guard_fit | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| B_partner_fit | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| D_partner_free_fit | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_wide_fit | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_stripe1 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_stripe2 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_stripe3 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_stripe4 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_stripe5 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_stripe6 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_body1 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_body2 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_body3 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_body4 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_body5 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_body6 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_body7 | 0 -> 0 | 0 -> 1 | 0 -> 0 |
| C_both1_1 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_both2_2 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_both3_3 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_both4_4 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_both5_5 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_both6_6 | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| C_both6_7 | 0 -> 0 | 0 -> 1 | 0 -> 0 |

## What each fold chose (the setting used on the held-out place)

| candidate | home_white | campus_study | abp_gray | home_bathtile | home_glass | home_ottoman | uc_palewood | abp_white | home_wooddesk | home_black |
|---|---|---|---|---|---|---|---|---|---|---|
| A_hyst_fit | hyst:1 | fixed | fixed | fixed | fixed | fixed | fixed | fixed | fixed | fixed |
| A_hyst_guard_fit | hystg:1 | fixed | fixed | fixed | fixed | fixed | fixed | fixed | fixed | fixed |
| B_partner_fit | pc:5,5,pred | pc:5,5,pred | pc:5,5,strict | pc:5,5,pred | pc:5,5,pred | pc:5,4,pred | pc:5,5,pred | pc:5,5,pred | pc:5,5,pred | pc:5,5,pred |
| D_partner_free_fit | pc:5,4,free | pc:2,5,free | pc:5,0,strict | pc:1,1,free | pc:5,4,free | pc:5,1,free | pc:5,4,free | pc:5,4,free | pc:5,4,free | pc:5,4,free |
| C_wide_fit | pc:5,5,pred | pc:5,5,pred | pc:5,5,strict | pc:5,5,pred | pc:5,5,pred | pc:5,4,pred | pc:5,5,pred | pc:5,5,pred | pc:5,5,pred | pc:5,5,pred |

A place that is not an ordinary one (the black table, the wood desk) is report only; its setting was chosen on all the ordinary frames.
