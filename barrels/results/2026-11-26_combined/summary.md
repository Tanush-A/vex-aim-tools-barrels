# The two winners together: every judged candidate (2026-11-26, TODO E8)

Made by `experiments/2026-11-26_combined/run.py`. Train frames only (154 ordinary frames, 8 places, 172 placements; 307 barrels counted per frame). Every candidate is fitted leave one place out: in each fold each step's setting is picked by that step's own rule on the other places. Found = the strict rule. Boxes = boxes that are not on their barrel, counted once per arrangement. Margins: found better above +4.0, worse below -10.92; boxes worse above +1.85; any new box on a clean empty frame fails; no place may drop by more than its margin.

Today's detector (the fixed colors): 133.8 of 172 placements, 211 of 307 per frame, 1.93 boxes not on their barrel, 0 on clean empty frames.

## Against today's detector

| candidate | verdict | found, placements | per frame | gained / lost | boxes not on their barrel | per frame: on nothing, second, wrong color | empty frames: clean, with clutter | ms per frame |
|---|---|---|---|---|---|---|---|---|
| `nearmiss` | **PASS, boxes at the margin (+1.63 of +1.85)** | 147.5 (+13.7) | 249 (+38) | +38 / -0 | 3.57 (+1.63) | 9, 2, 1 (today 5, 0, 0) | 0, 0.40 | 83 |
| `selfcal` | **PASS** | 147.6 (+13.8) | 248 (+37) | +37 / -0 | 2.18 (+0.25) | 5, 1, 0 (today 5, 0, 0) | 0, 0.00 | 88 |
| `nm_then_sc` | **FAIL** | 151.9 (+18.1) | 260 (+49) | +49 / -0 | 4.57 (+2.63) | 10, 2, 1 (today 5, 0, 0) | 0, 0.40 | 162 |
| `sc_then_nm` | **FAIL** | 153.1 (+19.3) | 262 (+51) | +51 / -0 | 4.32 (+2.38) | 10, 2, 0 (today 5, 0, 0) | 0, 0.40 | 161 |
| `mask_union` | **PASS, boxes at the margin (+1.38 of +1.85)** | 152.8 (+19.0) | 261 (+50) | +50 / -0 | 3.32 (+1.38) | 9, 2, 0 (today 5, 0, 0) | 0, 0.40 | 138 |
| `box_union` | **PASS, boxes at the margin (+1.63 of +1.85)** | 152.8 (+19.0) | 261 (+50) | +50 / -0 | 3.57 (+1.63) | 9, 2, 1 (today 5, 0, 0) | 0, 0.40 | 160 |
| `box_agree` | **PASS** | 143.2 (+9.4) | 237 (+26) | +26 / -0 | 2.18 (+0.25) | 5, 1, 0 (today 5, 0, 0) | 0, 0.00 | 160 |

Today's detector alone: 47 ms per frame. Times: fixed numbers, one process, nothing cached (`timing.json`).

## Each combination against each winner alone (the same judge, the winner as the baseline)

| combination | against `nearmiss`: verdict | found | gained / lost | boxes | against `selfcal`: verdict | found | gained / lost | boxes |
|---|---|---|---|---|---|---|---|---|
| `nm_then_sc` | PASS | 151.9 (+4.4) | +11 / -0 | 4.57 (+1.00) | FAIL | 151.9 (+4.3) | +14 / -2 | 4.57 (+2.38) |
| `sc_then_nm` | PASS | 153.1 (+5.7) | +13 / -0 | 4.32 (+0.75) | FAIL | 153.1 (+5.6) | +14 / -0 | 4.32 (+2.13) |
| `mask_union` | PASS | 152.8 (+5.3) | +12 / -0 | 3.32 (-0.25) | PASS | 152.8 (+5.2) | +13 / -0 | 3.32 (+1.13) |
| `box_union` | PASS | 152.8 (+5.3) | +12 / -0 | 3.57 (+0.00) | PASS | 152.8 (+5.2) | +13 / -0 | 3.57 (+1.38) |
| `box_agree` | FAIL | 143.2 (-4.2) | +1 / -13 | 2.18 (-1.38) | FAIL | 143.2 (-4.3) | +0 / -11 | 2.18 (+0.00) |

The two winners against each other (`nearmiss` with `selfcal` as the baseline): NO CLEAR DIFFERENCE; found 147.5 (-0.1); `nearmiss` finds 13 barrels that `selfcal` does not and misses 12 that `selfcal` finds (per frame); boxes 3.57 (+1.38).

## By place: found, placements (per frame in brackets)

| place | placements | today | `nearmiss` | `selfcal` | `nm_then_sc` | `sc_then_nm` | `mask_union` | `box_union` | `box_agree` |
|---|---|---|---|---|---|---|---|---|---|
| home_white | 29 | 28.0 (28) | 28.0 (28) | 28.0 (28) | 28.0 (28) | 28.0 (28) | 28.0 (28) | 28.0 (28) | 28.0 (28) |
| campus_study | 35 | 35.0 (35) | 35.0 (35) | 35.0 (35) | 35.0 (35) | 35.0 (35) | 35.0 (35) | 35.0 (35) | 35.0 (35) |
| abp_gray | 16 | 10.0 (10) | 12.0 (12) | 15.0 (15) | 14.0 (14) | 15.0 (15) | 15.0 (15) | 15.0 (15) | 13.0 (13) |
| home_bathtile | 15 | 4.0 (16) | 9.0 (36) | 9.8 (39) | 10.8 (43) | 11.0 (44) | 11.0 (44) | 11.0 (44) | 7.8 (31) |
| home_glass | 15 | 14.8 (74) | 14.8 (74) | 14.8 (74) | 14.8 (74) | 14.8 (74) | 14.8 (74) | 14.8 (74) | 14.8 (74) |
| home_ottoman | 15 | 3.0 (9) | 7.7 (23) | 6.0 (18) | 8.3 (25) | 8.3 (25) | 8.0 (24) | 8.0 (24) | 5.7 (17) |
| uc_palewood | 15 | 13.0 (13) | 13.0 (13) | 13.0 (13) | 13.0 (13) | 13.0 (13) | 13.0 (13) | 13.0 (13) | 13.0 (13) |
| abp_white | 32 | 26.0 (26) | 28.0 (28) | 26.0 (26) | 28.0 (28) | 28.0 (28) | 28.0 (28) | 28.0 (28) | 26.0 (26) |
| **all** | 172 | **133.8 (211)** | **147.5 (249)** | **147.6 (248)** | **151.9 (260)** | **153.1 (262)** | **152.8 (261)** | **152.8 (261)** | **143.2 (237)** |

The place clause of the judge, per candidate:

- `nearmiss`: [within the noise] found, place by place: abp_gray +2.0 of 16 (margin 6.0); home_bathtile +5.0 of 15 (margin 1.2); home_ottoman +4.7 of 15 (margin 2.3); abp_white +2.0 of 32 (margin 1.0).
- `selfcal`: [within the noise] found, place by place: abp_gray +5.0 of 16 (margin 6.0); home_bathtile +5.8 of 15 (margin 1.2); home_ottoman +3.0 of 15 (margin 2.3).
- `nm_then_sc`: [within the noise] found, place by place: abp_gray +4.0 of 16 (margin 6.0); home_bathtile +6.8 of 15 (margin 1.2); home_ottoman +5.3 of 15 (margin 2.3); abp_white +2.0 of 32 (margin 1.0).
- `sc_then_nm`: [within the noise] found, place by place: abp_gray +5.0 of 16 (margin 6.0); home_bathtile +7.0 of 15 (margin 1.2); home_ottoman +5.3 of 15 (margin 2.3); abp_white +2.0 of 32 (margin 1.0).
- `mask_union`: [within the noise] found, place by place: abp_gray +5.0 of 16 (margin 6.0); home_bathtile +7.0 of 15 (margin 1.2); home_ottoman +5.0 of 15 (margin 2.3); abp_white +2.0 of 32 (margin 1.0).
- `box_union`: [within the noise] found, place by place: abp_gray +5.0 of 16 (margin 6.0); home_bathtile +7.0 of 15 (margin 1.2); home_ottoman +5.0 of 15 (margin 2.3); abp_white +2.0 of 32 (margin 1.0).
- `box_agree`: [within the noise] found, place by place: abp_gray +3.0 of 16 (margin 6.0); home_bathtile +3.8 of 15 (margin 1.2); home_ottoman +2.7 of 15 (margin 2.3).

## What each winner's rule picked in each fold

| held-out place | near-miss | self-calibration |
|---|---|---|
| home_white | `pc:5,5,pred` | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| campus_study | `pc:5,5,pred` | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| abp_gray | `pc:5,5,strict` | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| home_bathtile | `pc:5,5,pred` | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| home_glass | `pc:5,5,pred` | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| home_ottoman | `pc:5,4,pred` | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.01} |
| uc_palewood | `pc:5,5,pred` | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| abp_white | `pc:5,5,pred` | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| home_wooddesk | `pc:5,5,pred` | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| home_black | `pc:5,5,pred` | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |
| (any place that is not an ordinary one) | `pc:5,5,pred` | {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03} |

## Checks

- `nearmiss` alone, built from `barrels.combined`'s building blocks, gives the winner's own boxes on 231 of 231 frames.
- `selfcal` alone, built from `barrels.combined`'s building blocks, gives the winner's own boxes on 231 of 231 frames.

## The pick (the rule is in PREREG.md)

- Ways the judge calls PASS against today's detector: `mask_union`, `box_union`, `box_agree`.
- The best combination by the rule: `mask_union`.
- Is it worth having both? Against each winner alone: `nearmiss` PASS, `selfcal` PASS. So: yes.
