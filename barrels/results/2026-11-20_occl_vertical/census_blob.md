# Census 2: a post, a joined stripe, the cap's height floor, a slice beside a found barrel

Measurements made before any rule was built (`experiments/2026-11-20_occl_vertical/census_blob.py`). Train frames only.

## P. A post across the middle

| hidden | scenes | narrow pieces on the barrel (median per scene) | piece width / stripe height | piece area, px | pieces of 20 px or more that are full slices | found today or boxed (v2) by a pair of full slices (boxes where no barrel is) | the same, slices not checked |
|---|---|---|---|---|---|---|---|
| 25 % | 50 | 2 | 1.23 (0.02 to 1.57; 10th to 90th pct 0.97 to 1.41) | 170 (3 to 1386; 10th to 90th pct 53 to 478) | 94 of 97 | 49 (0) | 49 (0) |
| 50 % | 50 | 2 | 0.76 (0.02 to 1.13; 10th to 90th pct 0.52 to 0.93) | 101 (3 to 814; 10th to 90th pct 28 to 287) | 91 of 97 | 42 (0) | 46 (0) |
| 75 % | 50 | 2 | 0.29 (0.02 to 0.54; 10th to 90th pct 0.10 to 0.40) | 36 (3 to 264; 10th to 90th pct 6 to 103) | 37 of 60 | 9 (0) | 16 (0) |

## W. How wide a stripe is, against three references

`row` = the barrel width the stripe's row gives. `tall` = the larger of that and the width of a barrel as tall as the body seen above and below the stripe (`stripe_two`, 2026-11-19). `own` = the width of a barrel whose stripe is as tall as this one. Median (min to max; 10th to 90th percentile).

| what | n | stripe / `row` | stripe / `tall` | stripe / `own` | body joined to the stripe / `row` |
|---|---|---|---|---|---|
| a barrel standing alone | 50 | 0.88 (0.01 to 1.04; 10th to 90th pct 0.80 to 0.96) | 0.87 (0.01 to 1.02; 10th to 90th pct 0.79 to 0.93) | 1.26 (0.01 to 1.62; 10th to 90th pct 1.09 to 1.40) | 0.94 (0.01 to 1.21; 10th to 90th pct 0.84 to 1.05) |
| a barrel of the SAME color, beside it, 25 % hidden: the widest stripe on the hidden barrel | 100 | 1.58 (0.72 to 1.81; 10th to 90th pct 0.84 to 1.74) | 1.51 (0.72 to 1.74; 10th to 90th pct 0.84 to 1.64) | 1.78 (1.06 to 2.37; 10th to 90th pct 1.29 to 2.18) | 1.67 (0.87 to 2.22; 10th to 90th pct 1.51 to 1.83) |
| a barrel of the SAME color, beside it, 50 % hidden: the widest stripe on the hidden barrel | 100 | 1.34 (0.45 to 1.63; 10th to 90th pct 0.87 to 1.48) | 1.29 (0.45 to 1.45; 10th to 90th pct 0.87 to 1.39) | 1.55 (0.69 to 2.04; 10th to 90th pct 1.23 to 1.91) | 1.44 (1.03 to 1.90; 10th to 90th pct 1.29 to 1.60) |
| a barrel of the SAME color, beside it, 75 % hidden: the widest stripe on the hidden barrel | 100 | 1.10 (0.20 to 1.47; 10th to 90th pct 0.87 to 1.23) | 1.06 (0.20 to 1.20; 10th to 90th pct 0.86 to 1.15) | 1.42 (0.33 to 2.02; 10th to 90th pct 1.11 to 1.65) | 1.19 (0.96 to 1.58; 10th to 90th pct 1.05 to 1.32) |
| a barrel of the SAME color, beside it and lower, 25 % hidden: the widest stripe on the hidden barrel | 100 | 0.91 (0.71 to 1.80; 10th to 90th pct 0.74 to 1.50) | 0.83 (0.69 to 1.56; 10th to 90th pct 0.73 to 1.19) | 1.25 (0.81 to 1.58; 10th to 90th pct 1.07 to 1.45) | 1.59 (0.84 to 2.16; 10th to 90th pct 1.42 to 1.80) |
| a barrel of the SAME color, beside it and lower, 50 % hidden: the widest stripe on the hidden barrel | 100 | 0.92 (0.54 to 1.57; 10th to 90th pct 0.74 to 1.46) | 0.83 (0.49 to 1.35; 10th to 90th pct 0.71 to 1.20) | 1.22 (0.67 to 1.58; 10th to 90th pct 1.03 to 1.45) | 1.39 (0.84 to 1.90; 10th to 90th pct 1.23 to 1.58) |
| a barrel of the SAME color, beside it and lower, 75 % hidden: the widest stripe on the hidden barrel | 100 | 0.91 (0.30 to 1.44; 10th to 90th pct 0.74 to 1.20) | 0.81 (0.27 to 1.17; 10th to 90th pct 0.70 to 1.01) | 1.25 (0.48 to 1.63; 10th to 90th pct 1.05 to 1.45) | 1.17 (0.84 to 1.63; 10th to 90th pct 1.04 to 1.33) |
| a barrel of the SAME color, straight in front, 25 % hidden: the widest stripe on the hidden barrel | 45 | 0.92 (0.80 to 1.07; 10th to 90th pct 0.83 to 1.02) | 0.55 (0.48 to 0.95; 10th to 90th pct 0.49 to 0.72) | 1.34 (0.80 to 4.46; 10th to 90th pct 1.12 to 1.59) | 2.00 (0.86 to 3.06; 10th to 90th pct 1.46 to 2.65) |
| a barrel of the SAME color, straight in front, 50 % hidden: the widest stripe on the hidden barrel | 42 | 0.86 (0.05 to 1.08; 10th to 90th pct 0.21 to 0.98) | 0.66 (0.04 to 0.95; 10th to 90th pct 0.17 to 0.80) | 1.57 (0.46 to 3.22; 10th to 90th pct 0.76 to 2.58) | 1.64 (0.95 to 2.73; 10th to 90th pct 1.27 to 2.15) |
| a barrel of the SAME color, straight in front, 75 % hidden: the widest stripe on the hidden barrel | 49 | 0.86 (0.15 to 1.19; 10th to 90th pct 0.76 to 1.02) | 0.77 (0.10 to 1.19; 10th to 90th pct 0.69 to 0.84) | 1.22 (0.55 to 1.60; 10th to 90th pct 1.09 to 1.38) | 0.97 (0.79 to 2.09; 10th to 90th pct 0.84 to 1.16) |
| a barrel of the OTHER color, straight in front, 25 % hidden: the widest stripe on the hidden barrel | 44 | 0.66 (0.31 to 0.99; 10th to 90th pct 0.56 to 0.90) | 0.66 (0.31 to 0.99; 10th to 90th pct 0.55 to 0.90) | 0.37 (0.16 to 1.62; 10th to 90th pct 0.31 to 1.25) | 1.22 (0.31 to 1.56; 10th to 90th pct 0.91 to 1.49) |
| a barrel of the OTHER color, straight in front, 50 % hidden: the widest stripe on the hidden barrel | 48 | 0.73 (0.29 to 1.20; 10th to 90th pct 0.66 to 0.86) | 0.70 (0.29 to 1.20; 10th to 90th pct 0.63 to 0.86) | 0.40 (0.33 to 0.81; 10th to 90th pct 0.36 to 0.48) | 1.23 (0.65 to 1.54; 10th to 90th pct 0.82 to 1.46) |
| a barrel of the OTHER color, straight in front, 75 % hidden: the widest stripe on the hidden barrel | 49 | 0.88 (0.43 to 1.22; 10th to 90th pct 0.76 to 1.01) | 0.83 (0.43 to 1.22; 10th to 90th pct 0.74 to 0.93) | 0.50 (0.27 to 0.70; 10th to 90th pct 0.41 to 0.60) | 1.23 (0.43 to 1.54; 10th to 90th pct 1.00 to 1.43) |

- every unflagged labeled barrel of HOME hand masks (19; touching neighbours included): stripe / `row` 0.91 (0.84 to 0.99; 10th to 90th pct 0.86 to 0.98); / `tall` 0.91 (0.84 to 0.97; 10th to 90th pct 0.85 to 0.95); / `own` 1.16 (1.02 to 1.32; 10th to 90th pct 1.03 to 1.26)
- every unflagged labeled barrel of HOME as in the eval table (19; touching neighbours included): stripe / `row` 0.89 (0.80 to 0.98; 10th to 90th pct 0.81 to 0.95); / `tall` 0.86 (0.67 to 0.94; 10th to 90th pct 0.73 to 0.91); / `own` 1.23 (1.06 to 1.49; 10th to 90th pct 1.18 to 1.37)
- every unflagged labeled barrel of CAMPUS (30; touching neighbours included): stripe / `row` 0.85 (0.01 to 1.50; 10th to 90th pct 0.75 to 0.95); / `tall` 0.84 (0.01 to 1.38; 10th to 90th pct 0.52 to 0.94); / `own` 1.30 (0.01 to 1.67; 10th to 90th pct 1.07 to 1.45)

The three scenes where `stripe_two` (2026-11-19) cut one barrel in two (CAMPUS `plain_01`, the near barrel [498, 145, 603, 243]):

- barrel_front/other at 50 %: stripe / `row` 0.65, / `tall` 0.65, / `own` 0.76; boxes today [(461, 181, 636, 334), (592, 146, 640, 242)]; with `stripe_two` [(452, 181, 598, 335), (522, 180, 640, 332), (592, 146, 640, 242)]; the front barrel is (441, 160, 640, 398)
- barrel_front/same at 25 %: stripe / `row` nan, / `tall` nan, / `own` nan; boxes today [(415, 203, 638, 375), (505, 147, 600, 249)]; with `stripe_two` [(404, 203, 591, 375), (490, 203, 640, 397), (505, 147, 600, 249)]; the front barrel is (395, 164, 640, 480)
- barrel_front/same at 50 %: stripe / `row` nan, / `tall` nan, / `own` nan; boxes today [(459, 180, 632, 330)]; with `stripe_two` [(448, 180, 591, 330), (521, 180, 640, 331)]; the front barrel is (441, 156, 640, 398)

## K. The cap rule's height floor (today: half an upper body)

For each scene with a barrel straight in front: the tallest piece the cap rule refuses for its height on the hidden barrel, as a share of the upper body its top row predicts; then how many hidden barrels are found (v2) with the floor at 0.5 (today), 0.4, 0.3, 0.25.

| scenes | n | refused top / upper body | found at 0.5 | 0.4 | 0.3 | 0.25 | boxes where no barrel is at 0.5 / 0.4 / 0.3 / 0.25 |
|---|---|---|---|---|---|---|---|
| a barrel of the OTHER color, straight in front, 25 % | 47 | 0.28 (0.28 to 0.28; 10th to 90th pct 0.28 to 0.28) (n 1) | 39 | 39 | 39 | 39 | 3 / 3 / 3 / 3 |
| a barrel of the OTHER color, straight in front, 50 % | 48 | 0.29 (0.16 to 0.41; 10th to 90th pct 0.19 to 0.38) (n 2) | 38 | 38 | 38 | 38 | 3 / 3 / 3 / 3 |
| a barrel of the OTHER color, straight in front, 75 % | 49 | 0.40 (0.18 to 0.50; 10th to 90th pct 0.27 to 0.49) (n 16) | 17 | 22 | 22 | 22 | 1 / 1 / 1 / 1 |
| a barrel of the SAME color, straight in front, 25 % | 47 | 0.16 (0.16 to 0.16; 10th to 90th pct 0.16 to 0.16) (n 1) | 44 | 44 | 44 | 44 | 4 / 4 / 4 / 4 |
| a barrel of the SAME color, straight in front, 50 % | 48 | 0.30 (0.30 to 0.30; 10th to 90th pct 0.30 to 0.30) (n 1) | 29 | 29 | 30 | 30 | 6 / 6 / 6 / 6 |
| a barrel of the SAME color, straight in front, 75 % | 49 | 0.43 (0.15 to 0.48; 10th to 90th pct 0.23 to 0.46) (n 10) | 2 | 8 | 8 | 8 | 2 / 2 / 2 / 2 |

The same change everywhere else: boxes that appear with the lower floor, by what they lie on.

| data | floor 0.4 | floor 0.3 | floor 0.25 |
|---|---|---|---|
| HOME hand masks | 0 | 0 | 0 |
| HOME as in the eval table | 0 | 0 | 0 |
| CAMPUS | 0 | 0 | 0 |
| BLACK (report only) | 0 | 0 | 0 |
| WOOD (report only) | 0 | 0 | 0 |
| HOME hand masks, medium damage, 5 seeds | 0 | 0 | 0 |
| HOME hand masks, heavy damage, 5 seeds | 0 | 0 | 0 |
| recording 2026-11-07_campus/r1_static | 0 | 0 | 0 |
| recording 2026-11-07_campus/r2_pan | 0 | 0 | 0 |
| recording 2026-11-07_campus/r3_enter_leave | 0 | 0 | 0 |
| recording 2026-11-07_campus/r4_hand_occlusion | 0 | 0 | 0 |
| recording 2026-11-16_black/rec_2026-11-16_131933 | 0 | 0 | 0 |
| recording 2026-11-16_wood/rec_2026-11-16_121306 | 0 | 0 | 0 |

## W on the scorecard: stripes wider than a barrel can be (1.2 x the taller reference, body seen right above and below)

Per cell: scenes with such a stripe; of those stripes, how many lie on two true barrels of that color (the hidden one and the one pasted in front) / on one only (it would be cut in two wrongly).

| scenes | n | scenes with a wide stripe | on two barrels | on one only |
|---|---|---|---|---|
| hidden from above, 25 % | 50 | 0 | 0 | 0 |
| hidden from above, 50 % | 50 | 0 | 0 | 0 |
| hidden from above, 75 % | 50 | 0 | 0 | 0 |
| hidden from below (a low thing in front), 25 % | 50 | 0 | 0 | 0 |
| hidden from below (a low thing in front), 50 % | 50 | 0 | 0 | 0 |
| hidden from below (a low thing in front), 75 % | 50 | 0 | 0 | 0 |
| a post across the middle, 25 % | 50 | 0 | 0 | 0 |
| a post across the middle, 50 % | 50 | 0 | 0 | 0 |
| a post across the middle, 75 % | 50 | 0 | 0 | 0 |
| a barrel of the OTHER color, straight in front, 25 % | 47 | 0 | 0 | 0 |
| a barrel of the OTHER color, straight in front, 50 % | 48 | 0 | 0 | 0 |
| a barrel of the OTHER color, straight in front, 75 % | 49 | 0 | 0 | 0 |
| a barrel of the SAME color, straight in front, 25 % | 47 | 0 | 0 | 0 |
| a barrel of the SAME color, straight in front, 50 % | 48 | 0 | 0 | 0 |
| a barrel of the SAME color, straight in front, 75 % | 49 | 0 | 0 | 0 |
| a barrel of the SAME color, beside it, 25 % | 100 | 80 | 80 | 0 |
| a barrel of the SAME color, beside it, 50 % | 100 | 77 | 77 | 0 |
| a barrel of the SAME color, beside it, 75 % | 100 | 2 | 2 | 0 |
| a barrel of the SAME color, beside it and lower, 25 % | 100 | 10 | 10 | 0 |
| a barrel of the SAME color, beside it and lower, 50 % | 100 | 11 | 11 | 0 |
| a barrel of the SAME color, beside it and lower, 75 % | 100 | 0 | 0 | 0 |

## W, everywhere: stripes wider than a barrel can be

| data | lies on | candidates |
|---|---|---|
| CAMPUS | two or more labeled barrels | 1 |

## P, everywhere, slices not checked: pairs of narrow pieces at the same rows one barrel apart, not already boxed

| data | lies on | candidates |
|---|---|---|
| BLACK (report only) | a labeled barrel found today | 2 |
| HOME hand masks, heavy damage, 5 seeds | a labeled barrel missed today | 12 |
| HOME hand masks, medium damage, 5 seeds | a labeled barrel found today | 3 |
| HOME hand masks, medium damage, 5 seeds | a labeled barrel missed today | 8 |
| WOOD (report only) | NOT a barrel | 1 |
| WOOD (report only) | a labeled barrel missed today | 1 |
| recording 2026-11-16_black/rec_2026-11-16_131933 | not known (unlabeled) | 7 |
| recording 2026-11-16_wood/rec_2026-11-16_121306 | not known (unlabeled) | 2 |

## P, everywhere: pairs of full slices one barrel apart, not already boxed

| data | lies on | candidates |
|---|---|---|
| HOME hand masks, medium damage, 5 seeds | a labeled barrel missed today | 3 |

## S, everywhere: a narrow full slice with exactly one side next to a found nearer barrel or the frame edge, not already boxed

| data | lies on | candidates |
|---|---|---|
| HOME hand masks, medium damage, 5 seeds | a labeled barrel found today | 1 |
| HOME hand masks, medium damage, 5 seeds | a labeled barrel missed today | 17 |
| recording 2026-11-07_campus/r3_enter_leave | not known (unlabeled) | 1 |

## S. A narrow piece beside a found nearer barrel, on the scorecard

| scenes | n | found today | found with the slice rule | boxes where no barrel is: today / with it |
|---|---|---|---|---|
| a barrel of the SAME color, beside it and lower, 25 % | 100 | 91 | 91 | 0 / 0 |
| a barrel of the SAME color, beside it and lower, 50 % | 100 | 85 | 85 | 0 / 0 |
| a barrel of the SAME color, beside it and lower, 75 % | 100 | 26 | 42 | 0 / 1 |
| a barrel of the SAME color, beside it, 25 % | 100 | 81 | 81 | 2 / 2 |
| a barrel of the SAME color, beside it, 50 % | 100 | 68 | 68 | 2 / 2 |
| a barrel of the SAME color, beside it, 75 % | 100 | 63 | 63 | 4 / 5 |

## F. Same color straight in front, half hidden: the scenes not found, one by one

| barrel | full box | front barrel | boxes drawn (color, box, how) | best overlap with the full box | bottom off by / allowed |
|---|---|---|---|---|---|
| HOME core_03 | [317, 108, 346, 137] | [310, 123, 353, 166] | orange [311, 108, 352, 166] det2; blue [312, 108, 351, 150] det2; orange [318, 108, 345, 141] det2 | 0.83 | 4 / 3.0 |
| HOME close_01 | [302, 143, 390, 235] | [258, 187, 434, 372] | orange [262, 181, 432, 335] det2 | 0.16 | 100 / 9.2 |
| HOME close_02 | [308, 141, 392, 231] | [266, 188, 434, 366] | blue [270, 180, 436, 330] det2 | 0.15 | 99 / 9.0 |
| HOME cluster_02 | [443, 122, 500, 179] | [422, 143, 521, 250] | blue [424, 144, 523, 237] det2 | 0.19 | 58 / 5.7 |
| HOME core_02 | [368, 120, 418, 173] | [350, 146, 436, 238] | orange [353, 147, 434, 238] det2; orange [370, 121, 417, 167] det2 | 0.82 | -6 / 5.3 |
| HOME core_02 | [419, 120, 471, 175] | [399, 148, 491, 244] | blue [402, 143, 496, 246] det2 | 0.15 | 71 / 5.5 |
| HOME core_03 | [317, 108, 346, 137] | [310, 123, 353, 166] | blue [305, 108, 343, 149] det2; orange [308, 107, 344, 147] det3; orange [311, 115, 350, 165] det2 | 0.52 | 10 / 3.0 |
| HOME far_02 | [333, 106, 363, 137] | [324, 120, 372, 170] | orange [326, 117, 375, 172] det2 | 0.20 | 35 / 3.1 |
| HOME far_02 | [433, 106, 468, 139] | [422, 123, 479, 176] | orange [414, 110, 454, 156] det2; blue [422, 125, 477, 178] det2; blue [433, 107, 467, 135] det2 | 0.82 | -4 / 3.3 |
| CAMPUS core_01 | [90, 161, 208, 286] | [6, 233, 292, 480] | blue [8, 219, 270, 417] det2 | 0.13 | 131 / 12.5 |
| CAMPUS core_01 | [333, 131, 397, 200] | [307, 165, 423, 290] | blue [314, 166, 417, 284] det2; blue [330, 132, 389, 188] det2 | 0.68 | -12 / 6.9 |
| CAMPUS far_01 | [240, 112, 273, 147] | [231, 127, 282, 184] | orange [233, 113, 278, 163] det2; blue [234, 129, 280, 180] det2 | 0.20 | 33 / 3.5 |
| CAMPUS far_01 | [379, 113, 414, 150] | [369, 129, 424, 189] | orange [370, 124, 421, 187] det2; orange [379, 112, 414, 155] det3 | 0.86 | 5 / 3.7 |
| CAMPUS hand_02 | [393, 124, 451, 185] | [370, 155, 474, 264] | orange [365, 150, 479, 262] det2 | 0.14 | 77 / 6.1 |
| CAMPUS plain_01 | [62, 149, 166, 255] | [1, 165, 227, 433] | blue [6, 200, 220, 387] det2 | 0.13 | 132 / 10.6 |
| CAMPUS plain_01 | [498, 145, 603, 243] | [441, 156, 640, 398] | orange [459, 180, 632, 330] det2 | 0.22 | 87 / 9.8 |
| CAMPUS plain_02 | [82, 131, 153, 204] | [51, 159, 184, 304] | blue [54, 160, 185, 277] det2; blue [80, 131, 150, 217] det3 | 0.80 | 13 / 7.3 |
| CAMPUS room_01 | [64, 123, 125, 181] | [41, 140, 148, 254] | blue [46, 147, 142, 254] det2; blue [65, 125, 128, 198] det3 | 0.70 | 17 / 5.8 |
| CAMPUS room_03 | [215, 112, 252, 152] | [203, 131, 264, 197] | orange [204, 132, 265, 196] det2 | 0.16 | 44 / 4.0 |

