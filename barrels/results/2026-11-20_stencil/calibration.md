# Calibration of the stencil's score (PREREG.md, "The three score numbers")

git 53f4aa1. Masks: A1 16, A2 16, A3 80, A4 10, B 80. Barrels: A1 29, A2 29, A3 145, B 145. The rule detector draws 1 false boxes on B.

## The grid (from the boxes stored with accept 0.10)

T0 = the smallest accept with no false box in A1 to A4 and no more in B than the rule detector. accept = T0 + 0.05. Found = A1 + A2 + A3 + B (348 barrels).

| band_full | absent_cost | outside_cost | false boxes at 0.10 (A1 / A2 / A3 / A4 / B) | T0 | accept | found at 0.10 | at T0 | at accept |
|---|---|---|---|---|---|---|---|---|
| 1.0 | 0.1 | 0.25 | 0 / 2 / 0 / 0 / 0 | 0.18 | 0.23 | 280 | 241 | 205 |
| 1.0 | 0.1 | 0.5 | 0 / 2 / 0 / 0 / 0 | 0.15 | 0.2 **chosen** | 280 | 261 | 224 |
| 1.0 | 0.1 | 1.0 | 0 / 2 / 0 / 0 / 0 | 0.13 | 0.18 | 273 | 265 | 223 |
| 1.0 | 0.25 | 0.25 | 0 / 1 / 0 / 0 / 1 | 0.17 | 0.22 | 239 | 202 | 174 |
| 1.0 | 0.25 | 0.5 | 0 / 2 / 0 / 0 / 2 | 0.14 | 0.19 | 238 | 217 | 195 |
| 1.0 | 0.25 | 1.0 | 0 / 1 / 0 / 0 / 0 | 0.11 | 0.16 | 238 | 234 | 195 |
| 1.0 | 0.5 | 0.25 | 0 / 1 / 0 / 0 / 0 | 0.16 | 0.21 | 187 | 156 | 140 |
| 1.0 | 0.5 | 0.5 | 0 / 1 / 0 / 0 / 0 | 0.13 | 0.18 | 187 | 176 | 148 |
| 1.0 | 0.5 | 1.0 | 0 / 0 / 0 / 0 / 0 | 0.1 | 0.15 | 178 | 178 | 149 |
| 0.5 | 0.1 | 0.25 | 8 / 10 / 2 / 0 / 2 | None | None | 286 | None | None |
| 0.5 | 0.1 | 0.5 | 3 / 3 / 2 / 0 / 1 | None | None | 299 | None | None |
| 0.5 | 0.1 | 1.0 | 2 / 3 / 6 / 0 / 2 | 0.7 | 0.75 | 288 | 93 | None |
| 0.5 | 0.25 | 0.25 | 9 / 12 / 2 / 0 / 4 | None | None | 265 | None | None |
| 0.5 | 0.25 | 0.5 | 4 / 5 / 2 / 0 / 1 | None | None | 277 | None | None |
| 0.5 | 0.25 | 1.0 | 2 / 3 / 4 / 0 / 3 | 0.69 | 0.74 | 277 | 91 | None |
| 0.5 | 0.5 | 0.25 | 9 / 13 / 2 / 0 / 5 | None | None | 234 | None | None |
| 0.5 | 0.5 | 0.5 | 4 / 7 / 2 / 0 / 3 | None | None | 244 | None | None |
| 0.5 | 0.5 | 1.0 | 3 / 3 / 2 / 0 / 2 | 0.7 | 0.75 | 249 | 60 | None |
| 0.25 | 0.1 | 0.25 | 11 / 14 / 10 / 0 / 6 | None | None | 290 | None | None |
| 0.25 | 0.1 | 0.5 | 5 / 8 / 12 / 0 / 9 | None | None | 298 | None | None |
| 0.25 | 0.1 | 1.0 | 2 / 4 / 6 / 0 / 5 | None | None | 316 | None | None |
| 0.25 | 0.25 | 0.25 | 10 / 17 / 6 / 0 / 3 | None | None | 281 | None | None |
| 0.25 | 0.25 | 0.5 | 6 / 8 / 5 / 0 / 3 | None | None | 292 | None | None |
| 0.25 | 0.25 | 1.0 | 2 / 3 / 10 / 0 / 2 | None | None | 294 | None | None |
| 0.25 | 0.5 | 0.25 | 14 / 17 / 11 / 0 / 5 | None | None | 249 | None | None |
| 0.25 | 0.5 | 0.5 | 7 / 10 / 5 / 0 / 4 | None | None | 267 | None | None |
| 0.25 | 0.5 | 1.0 | 3 / 3 / 9 / 0 / 4 | None | None | 267 | None | None |

## The direct run with the chosen numbers

band_full 1.0, absent_cost 0.1, outside_cost 0.5, accept 0.2.

| masks | barrels | stencil found | stencil false | rules found | rules false |
|---|---|---|---|---|---|
| A1 HOME hand masks | 29 | 28 | 0 | 28 | 0 |
| A2 HOME color model, leave one scene out | 29 | 27 | 0 | 28 | 0 |
| A3 light damage, seeds 10 to 14 | 145 | 132 | 0 | 144 | 0 |
| A4 negatives of the other tables | 0 | 0 | 0 | 0 | 0 |
| B medium damage, seeds 10 to 14 | 145 | 38 | 0 | 92 | 1 |

What the tolerance means: a barrel hidden by a thing that is not painted, showing the share v of its width, scores about v - 0.1 x (1 - v). It passes accept 0.2 from v = 0.27 up (with a perfect mask). At T0 = 0.15 that would be 0.23; at the floor 0.10, 0.18.

## Leaving one HOME scene out (does the tolerance transfer?)

T0 from the masks of the other scenes (and the negatives); the left-out scene's masks (hand, color model, light, medium) at that T0 + 0.05.

| scene left out | T0 without it | accept | found on it | false on it |
|---|---|---|---|---|
| close | 0.15 | 0.2 | 23 of 24 | 0 |
| cluster | 0.15 | 0.2 | 50 of 96 | 0 |
| core | 0.13 | 0.18 | 46 of 60 | 0 |
| edge | 0.15 | 0.2 | 7 of 12 | 0 |
| far | 0.15 | 0.2 | 23 of 48 | 0 |
| neg | 0.15 | 0.2 | 0 of 0 | 0 |
| occl | 0.15 | 0.2 | 31 of 48 | 0 |
| top | 0.15 | 0.2 | 7 of 12 | 0 |
| topstripe | 0.15 | 0.2 | 11 of 12 | 0 |
| touch | 0.15 | 0.2 | 27 of 36 | 0 |

## The veto level

The lowest stencil score at the place of a right rule box in A1, A2, A3 is 0.043; veto = that - 0.05 = **-0.01**. The eight lowest:

- 0.043  A3|4A8B_window_light_cluster_01|seed11  [357, 111, 399, 162]
- 0.045  A3|4A8B_window_light_cluster_01|seed12  [357, 111, 399, 162]
- 0.045  A3|4A8B_window_light_cluster_01|seed13  [357, 111, 399, 162]
- 0.047  A3|4A8B_window_light_cluster_01|seed10  [357, 111, 399, 162]
- 0.130  A3|4A8B_window_light_cluster_01|seed12  [315, 118, 366, 162]
- 0.136  A3|4A8B_window_light_occl_02|seed10  [399, 117, 439, 161]
- 0.136  A3|4A8B_window_light_occl_01|seed10  [388, 116, 429, 158]
- 0.136  A3|4A8B_window_light_occl_02|seed11  [399, 117, 439, 161]
