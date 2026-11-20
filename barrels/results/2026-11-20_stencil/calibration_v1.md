# Calibration of the stencil's score (PREREG.md, "The three score numbers")

git 6b159cb. Masks: A1 16, A2 16, A3 80, A4 10, B 80. Barrels: A1 29, A2 29, A3 145, B 145. The rule detector draws 1 false boxes on B.

## The grid (from the boxes stored with accept 0.10)

T0 = the smallest accept with no false box in A1 to A4 and no more in B than the rule detector. accept = T0 + 0.05. Found = A1 + A2 + A3 + B (348 barrels).

| absent_cost | outside_cost | false boxes at 0.10 (A1 / A2 / A3 / A4 / B) | T0 | accept | found at 0.10 | at T0 | at accept |
|---|---|---|---|---|---|---|---|
| 0.1 | 0.25 | 0 / 2 / 1 / 0 / 0 | 0.18 | 0.23 | 279 | 239 | 205 |
| 0.1 | 0.5 | 0 / 2 / 0 / 0 / 0 | 0.16 | 0.21 | 280 | 251 | 222 |
| 0.1 | 1.0 | 0 / 2 / 0 / 0 / 0 | 0.13 | 0.18 **chosen** | 273 | 265 | 226 |
| 0.25 | 0.25 | 0 / 1 / 0 / 0 / 1 | 0.18 | 0.23 | 239 | 197 | 170 |
| 0.25 | 0.5 | 0 / 2 / 0 / 0 / 2 | 0.14 | 0.19 | 238 | 217 | 195 |
| 0.25 | 1.0 | 1 / 1 / 0 / 0 / 0 | 0.11 | 0.16 | 237 | 233 | 195 |
| 0.5 | 0.25 | 0 / 1 / 0 / 0 / 0 | 0.16 | 0.21 | 187 | 156 | 140 |
| 0.5 | 0.5 | 0 / 1 / 0 / 0 / 0 | 0.13 | 0.18 | 187 | 176 | 148 |
| 0.5 | 1.0 | 0 / 0 / 0 / 0 / 0 | 0.1 | 0.15 | 179 | 179 | 149 |

## The direct run with the chosen numbers

absent_cost 0.1, outside_cost 1.0, accept 0.18.

| masks | barrels | stencil found | stencil false | rules found | rules false |
|---|---|---|---|---|---|
| A1 HOME hand masks | 29 | 28 | 0 | 28 | 0 |
| A2 HOME color model, leave one scene out | 29 | 27 | 0 | 28 | 0 |
| A3 light damage, seeds 10 to 14 | 145 | 129 | 0 | 144 | 0 |
| A4 negatives of the other tables | 0 | 0 | 0 | 0 | 0 |
| B medium damage, seeds 10 to 14 | 145 | 44 | 0 | 92 | 1 |

What the tolerance means: a barrel hidden by a thing that is not painted, showing the share v of its width, scores about v - 0.1 x (1 - v). It passes accept 0.18 from v = 0.25 up (with a perfect mask). At T0 = 0.13 that would be 0.21; at the floor 0.10, 0.18.

## Leaving one HOME scene out (does the tolerance transfer?)

T0 from the masks of the other scenes (and the negatives); the left-out scene's masks (hand, color model, light, medium) at that T0 + 0.05.

| scene left out | T0 without it | accept | found on it | false on it |
|---|---|---|---|---|
| close | 0.13 | 0.18 | 24 of 24 | 0 |
| cluster | 0.12 | 0.17 | 56 of 96 | 0 |
| core | 0.13 | 0.18 | 46 of 60 | 0 |
| edge | 0.13 | 0.18 | 7 of 12 | 0 |
| far | 0.13 | 0.18 | 28 of 48 | 0 |
| neg | 0.13 | 0.18 | 0 of 0 | 0 |
| occl | 0.13 | 0.18 | 23 of 48 | 0 |
| top | 0.13 | 0.18 | 7 of 12 | 0 |
| topstripe | 0.13 | 0.18 | 11 of 12 | 0 |
| touch | 0.13 | 0.18 | 27 of 36 | 0 |

## The veto level

The lowest stencil score at the place of a right rule box in A1, A2, A3 is 0.043; veto = that - 0.05 = **-0.01**. The eight lowest:

- 0.043  A3|4A8B_window_light_cluster_01|seed11  [357, 111, 399, 162]
- 0.045  A3|4A8B_window_light_cluster_01|seed12  [357, 111, 399, 162]
- 0.045  A3|4A8B_window_light_cluster_01|seed13  [357, 111, 399, 162]
- 0.047  A3|4A8B_window_light_cluster_01|seed10  [357, 111, 399, 162]
- 0.128  A3|4A8B_window_light_cluster_01|seed12  [315, 118, 366, 162]
- 0.136  A3|4A8B_window_light_occl_02|seed10  [399, 117, 439, 161]
- 0.136  A3|4A8B_window_light_occl_01|seed10  [388, 116, 429, 158]
- 0.136  A3|4A8B_window_light_occl_02|seed11  [399, 117, 439, 161]
