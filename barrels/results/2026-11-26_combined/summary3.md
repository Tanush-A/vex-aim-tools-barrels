# Addendum 2026-11-27: the third winner (contrast) with the other two

Made by `experiments/2026-11-26_combined/run3.py`. Train frames only; every candidate leave one place out, each component's setting picked by that component's own rule on the other places. `nearmiss`, `selfcal` and `mask_union` are the held-out boxes of the first judged run (`summary.md`). Margins: found better above +4.0, worse below -10.92; boxes worse above +1.85.

## Against today's detector (133.8 of 172 placements, 211 of 307 per frame, 1.93 boxes not on their barrel)

| candidate | verdict | found, placements | per frame | gained / lost | boxes not on their barrel | per frame: on nothing, second, wrong | empty frames: clean, with clutter | ms per frame |
|---|---|---|---|---|---|---|---|---|
| `cn_alone` | **PASS, boxes at the margin (+0.90 of +1.85)** | 155.3 (+21.5) | 275 (+64) | +64 / -0 | 2.83 (+0.90) | 7, 1, 1 | 0, 0.00 | 89.8 |
| `nearmiss` | **PASS, boxes at the margin (+1.63 of +1.85)** | 147.5 (+13.7) | 249 (+38) | +38 / -0 | 3.57 (+1.63) | 9, 2, 1 | 0, 0.40 | 82.6 |
| `selfcal` | **PASS** | 147.6 (+13.8) | 248 (+37) | +37 / -0 | 2.18 (+0.25) | 5, 1, 0 | 0, 0.00 | 87.6 |
| `mask_union` | **PASS, boxes at the margin (+1.38 of +1.85)** | 152.8 (+19.0) | 261 (+50) | +50 / -0 | 3.32 (+1.38) | 9, 2, 0 | 0, 0.40 | 138.3 |
| `cn_on_nm` | **FAIL** | 157.0 (+23.2) | 278 (+67) | +67 / -0 | 4.22 (+2.28) | 11, 2, 2 | 0, 0.40 | 154.7 |
| `cn_on_sc` | **PASS, boxes at the margin (+1.65 of +1.85)** | 155.5 (+21.7) | 275 (+64) | +64 / -0 | 3.58 (+1.65) | 9, 1, 2 | 0, 0.00 | 130.9 |
| `cn_on_all` | **FAIL** | 157.7 (+23.9) | 278 (+67) | +67 / -0 | 4.72 (+2.78) | 13, 2, 2 | 0, 0.40 | 179.8 |
| `cn_box_nm` | **FAIL** | 156.6 (+22.8) | 277 (+66) | +66 / -0 | 4.22 (+2.28) | 11, 2, 2 | 0, 0.40 | 205.3 |
| `cn_box_sc` | **PASS, boxes at the margin (+0.90 of +1.85)** | 155.7 (+21.9) | 276 (+65) | +65 / -0 | 2.83 (+0.90) | 7, 1, 1 | 0, 0.00 | 177.0 |
| `cn_box_all` | **FAIL** | 158.0 (+24.2) | 279 (+68) | +68 / -0 | 3.97 (+2.03) | 11, 2, 1 | 0, 0.40 | 228.9 |

Today's detector alone: 45.9 ms per frame.

## Against CONTRAST ALONE (the same judge, contrast alone as the baseline): is anything worth adding to it?

| candidate | verdict | found, placements | per frame | gained / lost (per frame) | boxes not on their barrel |
|---|---|---|---|---|---|
| `cn_on_nm` | NO CLEAR DIFFERENCE | 157.0 (+1.7) | 278 (+3) | +6 / -3 | 4.22 (+1.38) |
| `cn_on_sc` | NO CLEAR DIFFERENCE | 155.5 (+0.2) | 275 (+0) | +2 / -2 | 3.58 (+0.75) |
| `cn_on_all` | FAIL | 157.7 (+2.4) | 278 (+3) | +6 / -3 | 4.72 (+1.88) |
| `cn_box_nm` | NO CLEAR DIFFERENCE | 156.6 (+1.3) | 277 (+2) | +5 / -3 | 4.22 (+1.38) |
| `cn_box_sc` | NO CLEAR DIFFERENCE | 155.7 (+0.4) | 276 (+1) | +2 / -1 | 2.83 (+0.00) |
| `cn_box_all` | NO CLEAR DIFFERENCE | 158.0 (+2.7) | 279 (+4) | +6 / -2 | 3.97 (+1.13) |
| `nearmiss` | FAIL | 147.5 (-7.8) | 249 (-26) | +5 / -31 | 3.57 (+0.73) |
| `selfcal` | FAIL | 147.6 (-7.8) | 248 (-27) | +2 / -29 | 2.18 (-0.65) |
| `mask_union` | FAIL | 152.8 (-2.5) | 261 (-14) | +6 / -20 | 3.32 (+0.48) |

## By place: found, placements (per frame)

| place | placements | today | `cn_alone` | `nearmiss` | `selfcal` | `mask_union` | `cn_on_nm` | `cn_on_sc` | `cn_on_all` | `cn_box_nm` | `cn_box_sc` | `cn_box_all` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| home_white | 29 | 28.0 | 28.0 (28) | 28.0 (28) | 28.0 (28) | 28.0 (28) | 28.0 (28) | 28.0 (28) | 28.0 (28) | 28.0 (28) | 28.0 (28) | 28.0 (28) |
| campus_study | 35 | 35.0 | 35.0 (35) | 35.0 (35) | 35.0 (35) | 35.0 (35) | 35.0 (35) | 35.0 (35) | 35.0 (35) | 35.0 (35) | 35.0 (35) | 35.0 (35) |
| abp_gray | 16 | 10.0 | 15.0 (15) | 12.0 (12) | 15.0 (15) | 15.0 (15) | 14.0 (14) | 15.0 (15) | 15.0 (15) | 14.0 (14) | 15.0 (15) | 15.0 (15) |
| home_bathtile | 15 | 4.0 | 13.5 (54) | 9.0 (36) | 9.8 (39) | 11.0 (44) | 13.5 (54) | 13.0 (52) | 13.2 (53) | 13.5 (54) | 13.2 (53) | 13.5 (54) |
| home_glass | 15 | 14.8 | 14.8 (74) | 14.8 (74) | 14.8 (74) | 14.8 (74) | 14.8 (74) | 14.8 (74) | 14.8 (74) | 14.8 (74) | 14.8 (74) | 14.8 (74) |
| home_ottoman | 15 | 3.0 | 10.0 (30) | 7.7 (23) | 6.0 (18) | 8.0 (24) | 10.7 (32) | 10.7 (32) | 10.7 (32) | 10.3 (31) | 10.7 (32) | 10.7 (32) |
| uc_palewood | 15 | 13.0 | 13.0 (13) | 13.0 (13) | 13.0 (13) | 13.0 (13) | 13.0 (13) | 13.0 (13) | 13.0 (13) | 13.0 (13) | 13.0 (13) | 13.0 (13) |
| abp_white | 32 | 26.0 | 26.0 (26) | 28.0 (28) | 26.0 (26) | 28.0 (28) | 28.0 (28) | 26.0 (26) | 28.0 (28) | 28.0 (28) | 26.0 (26) | 28.0 (28) |

## Checks

- mask_union run again gives the boxes of the first run: 231 of 231 frames identical
- contrast alone from barrels.combined gives contrast's own judged pages: 0 difference(s)

## The pick (the addendum's rule)

- Combinations that are PASS against today's detector AND against contrast alone: none.
- The answer: `cn_alone` (no combination is PASS against contrast alone).
