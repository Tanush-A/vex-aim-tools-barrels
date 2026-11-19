# Census: a stripe with body color on one side only; a top or a base alone

Measurements made before any rule was built (`experiments/2026-11-20_occl_vertical/census_half.py`). Camera AIM_4A8B6118_BOXFIT; train frames only.

## A. What one seam of the stripe says about the rest of the barrel (50 free-standing barrels)

Errors in px, median (10th to 90th percentile; worst). + = lower in the picture / larger.

| reading | value |
|---|---|
| stripe's TOP seam alone → the top row: seen top minus predicted | +1.9 (-1.0 to +2.8; worst -6.6) |
| ... inside the usual edge tolerance (15 % of the height, 4 px at least) | 50 of 50 |
| stripe's TOP seam alone → the bottom row: predicted minus hand-drawn | +1.2 (-2.8 to +3.9; worst +51.4) |
| ... inside the v2 bottom tolerance (10 % of the height, 3 px at least) | 43 of 50 |
| upper body's width / the width that seam predicts | 0.92 (0.77 to 1.17) |
| upper body's height / predicted | 0.93 (0.73 to 1.08) |
| stripe's BOTTOM seam alone → the bottom row: seen bottom minus predicted | +2.1 (-0.2 to +5.8; worst -25.4) |
| ... inside the usual edge tolerance | 50 of 50 |
| stripe's BOTTOM seam alone → the top row: predicted minus hand-drawn | -3.2 (-4.4 to -1.8; worst -5.4) |
| lower body's width / the width that seam predicts | 0.91 (0.00 to 1.07) |
| lower body's height / predicted | 1.11 (0.00 to 1.52) |
| for comparison, the stripe's MIDDLE row (today's reading) → the bottom row: predicted minus hand-drawn | -1.4 (-4.5 to +1.4; worst +38.9) |
| ... inside the v2 bottom tolerance | 49 of 50 |
| for comparison, the TOP ROW → the bottom row: predicted minus hand-drawn | +5.5 (-2.6 to +9.0; worst +30.9) |
| ... inside the v2 bottom tolerance | 25 of 50 |
| stripe's height / predicted from its middle row | 0.76 (0.48 to 0.99) |

## B. A band with body color on one side only, counted everywhere

`top hidden` = body color under the band only (the stripe and the lower body show). `bottom hidden` = body color above the band only (the upper body and the stripe show). The distance comes from the seam between band and body. Each column = how many candidates are left after that test and all before it (a band is any connected piece of 20 px or more). The last two: all tests, by what the candidate lies on; and the same when the band must also be at least 0.45 of a stripe tall.

| data | kind | one side only | not taller than a stripe | whole width (0.8 to 1.2 W) | body's far edge where the seam predicts | body a barrel wide (0.8 to 1.2 W) | open side clear of barrel color | body's far edge not against barrel color | not inside a found box | all tests, and 0.45 of a stripe tall | all tests, any band of 20 px |
|---|---|---|---|---|---|---|---|---|---|---|---|
| HOME hand masks | top hidden | 19 | 7 | 6 | 5 | 3 | 3 | 0 | 0 | 0 | 0 |
| HOME hand masks | bottom hidden | 23 | 23 | 8 | 2 | 1 | 1 | 1 | 0 | 0 | 0 |
| HOME as in the eval table | top hidden | 17 | 10 | 8 | 6 | 4 | 4 | 0 | 0 | 0 | 0 |
| HOME as in the eval table | bottom hidden | 26 | 26 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| CAMPUS | top hidden | 28 | 12 | 8 | 4 | 4 | 4 | 0 | 0 | 0 | 0 |
| CAMPUS | bottom hidden | 33 | 33 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| BLACK (report only) | top hidden | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| BLACK (report only) | bottom hidden | 6 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| WOOD (report only) | top hidden | 52 | 50 | 8 | 4 | 2 | 2 | 2 | 2 | 2 on a labeled barrel missed today | 2 on a labeled barrel missed today |
| WOOD (report only) | bottom hidden | 34 | 34 | 8 | 3 | 3 | 3 | 2 | 0 | 0 | 0 |
| HOME hand masks, medium damage, 5 seeds | top hidden | 118 | 94 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| HOME hand masks, medium damage, 5 seeds | bottom hidden | 50 | 50 | 15 | 6 | 6 | 6 | 5 | 0 | 0 | 0 |
| HOME hand masks, heavy damage, 5 seeds | top hidden | 115 | 108 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| HOME hand masks, heavy damage, 5 seeds | bottom hidden | 13 | 13 | 5 | 5 | 5 | 5 | 5 | 0 | 0 | 0 |
| recording 2026-11-07_campus/r1_static | top hidden | 108 | 54 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| recording 2026-11-07_campus/r1_static | bottom hidden | 162 | 162 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| recording 2026-11-07_campus/r2_pan | top hidden | 102 | 74 | 43 | 43 | 41 | 41 | 0 | 0 | 0 | 0 |
| recording 2026-11-07_campus/r2_pan | bottom hidden | 167 | 167 | 22 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| recording 2026-11-07_campus/r3_enter_leave | top hidden | 34 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| recording 2026-11-07_campus/r3_enter_leave | bottom hidden | 34 | 33 | 22 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| recording 2026-11-07_campus/r4_hand_occlusion | top hidden | 54 | 43 | 37 | 37 | 37 | 37 | 0 | 0 | 0 | 0 |
| recording 2026-11-07_campus/r4_hand_occlusion | bottom hidden | 57 | 57 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| recording 2026-11-16_black/rec_2026-11-16_131933 | top hidden | 46 | 46 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| recording 2026-11-16_black/rec_2026-11-16_131933 | bottom hidden | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| recording 2026-11-16_wood/rec_2026-11-16_121306 | top hidden | 26 | 23 | 12 | 11 | 1 | 1 | 1 | 0 | 0 | 0 |
| recording 2026-11-16_wood/rec_2026-11-16_121306 | bottom hidden | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Every candidate that passes all tests (without the height floor) is listed in `census_half.csv`.

## C. A top alone, a base alone (no stripe): one-color pieces of the right size, outside the boxes found today

| data | kind | lies on | pieces |
|---|---|---|---|
| BLACK (report only) | base alone | NOT a barrel | 1 |
| BLACK (report only) | base alone | a labeled barrel missed today | 7 |
| BLACK (report only) | top alone | NOT a barrel | 1 |
| CAMPUS | base alone | NOT a barrel | 2 |
| HOME as in the eval table | base alone | NOT a barrel | 1 |
| HOME as in the eval table | top alone | NOT a barrel | 1 |
| HOME hand masks, heavy damage, 5 seeds | base alone | a labeled barrel missed today | 50 |
| HOME hand masks, medium damage, 5 seeds | base alone | a labeled barrel missed today | 10 |
| WOOD (report only) | base alone | NOT a barrel | 18 |
| WOOD (report only) | base alone | a labeled barrel found today | 1 |
| WOOD (report only) | base alone | a labeled barrel missed today | 65 |
| WOOD (report only) | top alone | NOT a barrel | 16 |
| WOOD (report only) | top alone | a labeled barrel missed today | 16 |
| recording 2026-11-07_campus/r1_static | base alone | not known (unlabeled) | 6 |
| recording 2026-11-07_campus/r2_pan | base alone | not known (unlabeled) | 9 |
| recording 2026-11-07_campus/r3_enter_leave | base alone | not known (unlabeled) | 68 |
| recording 2026-11-07_campus/r4_hand_occlusion | base alone | not known (unlabeled) | 21 |
| recording 2026-11-07_campus/r4_hand_occlusion | top alone | not known (unlabeled) | 6 |
| recording 2026-11-16_black/rec_2026-11-16_131933 | base alone | not known (unlabeled) | 4 |
| recording 2026-11-16_black/rec_2026-11-16_131933 | top alone | not known (unlabeled) | 7 |
| recording 2026-11-16_wood/rec_2026-11-16_121306 | base alone | not known (unlabeled) | 19 |
| recording 2026-11-16_wood/rec_2026-11-16_121306 | top alone | not known (unlabeled) | 5 |

## What the candidates would give on the scorecard's scenes (a forecast, not the experiment)

Each of the free-standing barrels hidden from above or from below by the stated share of its height; 'boxed' = a candidate passes all tests and its box is a hit under the v2 rule against the full box. Each cell: found today → found today or boxed by a candidate at least 0.45 of a stripe tall → the same with any band of 20 px; then (boxes of the wrong color or place with any band).

| hidden | from above | from below | n |
|---|---|---|---|
| 25 % | 50 → 50 → 50 (0) | 49 → 49 → 49 (0) | 50 |
| 30 % | 50 → 50 → 50 (0) | 45 → 46 → 46 (1) | 50 |
| 35 % | 49 → 49 → 49 (0) | 10 → 44 → 44 (15) | 50 |
| 40 % | 38 → 47 → 47 (0) | 1 → 46 → 47 (6) | 50 |
| 45 % | 9 → 46 → 46 (0) | 1 → 15 → 45 (0) | 50 |
| 50 % | 2 → 40 → 45 (0) | 1 → 2 → 40 (0) | 50 |
| 55 % | 0 → 13 → 38 (0) | 1 → 1 → 8 (0) | 50 |
| 60 % | 0 → 1 → 17 (1) | 1 → 1 → 1 (0) | 50 |
| 75 % | 0 → 0 → 0 (0) | 1 → 1 → 1 (0) | 50 |

