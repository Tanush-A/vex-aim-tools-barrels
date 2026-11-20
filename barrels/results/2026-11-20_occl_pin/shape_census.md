# Where is a cut barrel, sideways? (a census; no acceptance number)

Source barrels: the 50 unhidden train barrels of the occlusion scorecard. W = the barrel width the stripe's row gives. `hand masks` = the 12 HOME hand masks; `color model` = the same 12 as the color model segments them + the 26 of CAMPUS.

## A. How curved is the outline of an unhidden barrel?

In barrel widths W; median (10th to 90th percentile; n). `seen` is measured on the mask, `model` is what the camera model predicts for the barrel's distance. *top rise*: how much lower the top edge is at 0.25 to 0.35 W from the centre than at the centre. *shoulder*: the same at 0.42 to 0.5 W (the last 8 % before the side). *stripe sag*: how much lower the stripe's middle is at the centre than at 0.35 to 0.45 W. *base rise*, *base corner*: how much higher the bottom edge is at 0.25 to 0.35 W / at 0.42 to 0.5 W than at the centre.

### hand masks

| barrel width | | top rise | shoulder | stripe sag | base rise | base corner |
|---|---|---|---|---|---|---|
| under 45 px (n 3) | seen | +0.000 (+0.000 to +0.012; n 3) | +0.187 (+0.181 to +0.187; n 3) | +0.030 (+0.006 to +0.043; n 3) | +0.016 (+0.003 to +0.039; n 3) | +0.299 (+0.210 to +0.309; n 3) |
| | model | +0.011 | +0.270 | +0.022 | +0.024 | +0.291 |
| 45 to 70 px (n 7) | seen | +0.019 (-0.004 to +0.027; n 7) | +0.184 (+0.130 to +0.241; n 7) | +0.024 (+0.010 to +0.035; n 7) | +0.028 (+0.010 to +0.047; n 7) | +0.233 (+0.152 to +0.306; n 7) |
| | model | +0.017 | +0.273 | +0.034 | +0.037 | +0.305 |
| over 70 px (n 2) | seen | +0.031 (+0.025 to +0.036; n 2) | +0.238 (+0.221 to +0.255; n 2) | +0.047 (+0.043 to +0.052; n 2) | +0.061 (+0.061 to +0.062; n 2) | +0.330 (+0.324 to +0.337; n 2) |
| | model | +0.025 | +0.277 | +0.053 | +0.054 | +0.325 |

### color model

| barrel width | | top rise | shoulder | stripe sag | base rise | base corner |
|---|---|---|---|---|---|---|
| under 45 px (n 10) | seen | +0.000 (-0.033 to +0.046; n 10) | +0.202 (+0.046 to +0.307; n 9) | +0.015 (+0.007 to +0.039; n 10) | +0.028 (+0.022 to +0.063; n 10) | +0.333 (+0.249 to +0.365; n 9) |
| | model | +0.013 | +0.271 | +0.026 | +0.028 | +0.295 |
| 45 to 70 px (n 21) | seen | +0.015 (-0.026 to +0.038; n 21) | +0.236 (+0.086 to +0.416; n 21) | +0.035 (+0.021 to +0.059; n 21) | +0.038 (+0.019 to +0.054; n 21) | +0.315 (+0.220 to +0.351; n 21) |
| | model | +0.017 | +0.273 | +0.035 | +0.038 | +0.306 |
| over 70 px (n 6) | seen | +0.034 (+0.024 to +0.130; n 6) | +0.356 (+0.240 to +0.496; n 6) | +0.074 (+0.057 to +0.089; n 6) | +0.087 (+0.055 to +0.119; n 6) | +0.299 (+0.292 to +0.337; n 6) |
| | model | +0.026 | +0.277 | +0.057 | +0.058 | +0.329 |

## B. The centre column from each cue, when only part of the width shows

The barrel is cut by straight upright edges so that a window of 75, 50 or 25 % of its width shows: `one side cut` (the window starts at the barrel's left side, or ends at its right side: 2 scenes per barrel), `both sides, equal` (the window is in the middle), `both sides, unequal` (a quarter of what is hidden is on one side and three quarters on the other: 2 scenes per barrel). Each cell: **median error / 90th-percentile error / scenes with the centre right to 0.15 W, of all scenes** (error in barrel widths; a scene where no stripe piece is seen counts as not right). A W-wide box whose centre is 0.15 W off overlaps the true box by 0.74.

### hand masks, one side cut

| seen | centred | top apex | top fit | stripe fit | bottom fit | all fit |
|---|---|---|---|---|---|---|
| 75 % | 0.12 / 0.12 / 24 of 24 | 0.03 / 0.09 / 24 of 24 | 0.02 / 0.05 / 24 of 24 | 0.05 / 0.18 / 21 of 24 | 0.02 / 0.05 / 24 of 24 | 0.02 / 0.04 / 24 of 24 |
| 50 % | 0.24 / 0.25 / 0 of 24 | 0.13 / 0.19 / 16 of 24 | 0.02 / 0.05 / 24 of 24 | 0.07 / 0.26 / 15 of 24 | 0.02 / 0.06 / 23 of 24 | 0.02 / 0.04 / 24 of 24 |
| 25 % | 0.37 / 0.38 / 0 of 24 | 0.28 / 0.33 / 0 of 24 | 0.02 / 0.05 / 24 of 24 | 0.16 / 0.37 / 12 of 24 | 0.02 / 0.07 / 24 of 24 | 0.03 / 0.05 / 24 of 24 |

### hand masks, both sides, equal

| seen | centred | top apex | top fit | stripe fit | bottom fit | all fit |
|---|---|---|---|---|---|---|
| 75 % | 0.00 / 0.00 / 12 of 12 | 0.02 / 0.07 / 12 of 12 | 0.00 / 0.01 / 12 of 12 | 0.07 / 0.14 / 11 of 12 | 0.01 / 0.02 / 12 of 12 | 0.01 / 0.02 / 12 of 12 |
| 50 % | 0.00 / 0.00 / 12 of 12 | 0.02 / 0.05 / 12 of 12 | 0.02 / 0.09 / 12 of 12 | 0.06 / 0.12 / 11 of 12 | 0.05 / 0.08 / 12 of 12 | 0.03 / 0.07 / 12 of 12 |
| 25 % | 0.00 / 0.00 / 12 of 12 | 0.00 / 0.10 / 12 of 12 | 0.00 / 0.10 / 11 of 12 | 0.01 / 0.18 / 10 of 12 | 0.02 / 0.14 / 11 of 12 | 0.02 / 0.08 / 12 of 12 |

### hand masks, both sides, unequal

| seen | centred | top apex | top fit | stripe fit | bottom fit | all fit |
|---|---|---|---|---|---|---|
| 75 % | 0.06 / 0.07 / 24 of 24 | 0.02 / 0.06 / 24 of 24 | 0.02 / 0.04 / 24 of 24 | 0.06 / 0.15 / 21 of 24 | 0.02 / 0.05 / 24 of 24 | 0.02 / 0.04 / 24 of 24 |
| 50 % | 0.13 / 0.13 / 24 of 24 | 0.07 / 0.15 / 21 of 24 | 0.02 / 0.12 / 23 of 24 | 0.07 / 0.20 / 19 of 24 | 0.02 / 0.11 / 24 of 24 | 0.02 / 0.11 / 23 of 24 |
| 25 % | 0.19 / 0.19 / 0 of 24 | 0.16 / 0.19 / 10 of 24 | 0.12 / 0.19 / 13 of 24 | 0.14 / 0.28 / 13 of 24 | 0.03 / 0.19 / 17 of 24 | 0.03 / 0.19 / 17 of 24 |

### color model, one side cut

| seen | centred | top apex | top fit | stripe fit | bottom fit | all fit |
|---|---|---|---|---|---|---|
| 75 % | 0.11 / 0.12 / 74 of 76 | 0.12 / 0.25 / 43 of 76 | 0.03 / 0.10 / 70 of 76 | 0.06 / 0.13 / 69 of 76 | 0.03 / 0.06 / 73 of 76 | 0.02 / 0.05 / 74 of 76 |
| 50 % | 0.24 / 0.25 / 0 of 76 | 0.14 / 0.27 / 41 of 76 | 0.03 / 0.22 / 65 of 76 | 0.06 / 0.19 / 62 of 76 | 0.03 / 0.07 / 72 of 76 | 0.03 / 0.05 / 74 of 76 |
| 25 % | 0.36 / 0.38 / 0 of 76 | 0.29 / 0.36 / 0 of 76 | 0.04 / 0.23 / 61 of 76 | 0.07 / 0.35 / 53 of 76 | 0.05 / 0.13 / 64 of 76 | 0.03 / 0.07 / 66 of 76 |

### color model, both sides, equal

| seen | centred | top apex | top fit | stripe fit | bottom fit | all fit |
|---|---|---|---|---|---|---|
| 75 % | 0.00 / 0.00 / 37 of 38 | 0.12 / 0.26 / 23 of 38 | 0.01 / 0.08 / 35 of 38 | 0.07 / 0.11 / 34 of 38 | 0.02 / 0.05 / 36 of 38 | 0.02 / 0.05 / 36 of 38 |
| 50 % | 0.00 / 0.00 / 37 of 38 | 0.09 / 0.23 / 23 of 38 | 0.05 / 0.13 / 34 of 38 | 0.07 / 0.14 / 34 of 38 | 0.04 / 0.10 / 36 of 38 | 0.04 / 0.09 / 36 of 38 |
| 25 % | 0.00 / 0.00 / 37 of 38 | 0.01 / 0.08 / 37 of 38 | 0.00 / 0.25 / 28 of 38 | 0.08 / 0.25 / 25 of 38 | 0.00 / 0.13 / 34 of 38 | 0.01 / 0.08 / 36 of 38 |

### color model, both sides, unequal

| seen | centred | top apex | top fit | stripe fit | bottom fit | all fit |
|---|---|---|---|---|---|---|
| 75 % | 0.06 / 0.07 / 74 of 76 | 0.12 / 0.26 / 44 of 76 | 0.03 / 0.10 / 69 of 76 | 0.06 / 0.12 / 71 of 76 | 0.03 / 0.06 / 72 of 76 | 0.02 / 0.05 / 73 of 76 |
| 50 % | 0.12 / 0.13 / 74 of 76 | 0.09 / 0.24 / 58 of 76 | 0.04 / 0.22 / 61 of 76 | 0.07 / 0.15 / 66 of 76 | 0.03 / 0.07 / 73 of 76 | 0.02 / 0.09 / 74 of 76 |
| 25 % | 0.19 / 0.19 / 0 of 76 | 0.17 / 0.24 / 33 of 76 | 0.17 / 0.42 / 34 of 76 | 0.11 / 0.25 / 46 of 76 | 0.06 / 0.19 / 61 of 76 | 0.06 / 0.17 / 60 of 76 |

### `all fit` by barrel size (both groups, all windows)

| barrel width | 75 % seen | 50 % seen | 25 % seen |
|---|---|---|---|
| under 45 px | 0.03 / 0.07 / 63 of 65 | 0.03 / 0.09 / 64 of 65 | 0.04 / 0.18 / 49 of 65 |
| 45 to 70 px | 0.02 / 0.04 / 135 of 135 | 0.03 / 0.07 / 134 of 135 | 0.03 / 0.14 / 123 of 135 |
| over 70 px | 0.02 / 0.04 / 45 of 50 | 0.02 / 0.05 / 45 of 50 | 0.03 / 0.09 / 43 of 50 |

## C. When does the outline know where the barrel is?

The best position is not enough: a flat piece from the middle of a barrel fits the outline at many positions. The cost of a position = the mean distance in rows between the seen lines and the predicted ones. A position *fits* when its cost is within `near` x H of the best position's (H = the barrel's height). The outline *knows* when the fitting positions span at most `span` x W and the best cost is at most `good` x H; the centre is then the middle of the fitting positions. Each cell: **scenes where it knows / of those, the centre wrong by more than 0.15 W / the largest error among them** (both groups together: 100 scenes one side, 100 both sides unequal, 50 both sides equal).

| near | span | good | one side: 75 % seen | 50 % | 25 % | both, unequal: 75 % | 50 % | 25 % | both, equal: 75 % | 50 % | 25 % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.005 H | 0.15 W | 0.03 H | 81 / 0 / 0.07 | 79 / 0 / 0.09 | 61 / 0 / 0.10 | 77 / 0 / 0.06 | 18 / 0 / 0.06 | 3 / 0 / 0.02 | 37 / 0 / 0.03 | 1 / 0 / 0.00 | 0 / 0 / 0.00 |
| 0.005 H | 0.15 W | 0.05 H | 85 / 0 / 0.07 | 88 / 0 / 0.09 | 83 / 0 / 0.10 | 81 / 0 / 0.06 | 19 / 0 / 0.06 | 3 / 0 / 0.02 | 39 / 0 / 0.03 | 2 / 1 / 0.15 | 0 / 0 / 0.00 |
| 0.005 H | 0.15 W | any | 89 / 0 / 0.07 | 90 / 0 / 0.09 | 85 / 0 / 0.10 | 84 / 1 / 0.21 | 20 / 0 / 0.13 | 4 / 1 / 0.16 | 41 / 1 / 0.17 | 2 / 1 / 0.15 | 0 / 0 / 0.00 |
| 0.005 H | 0.3 W | 0.03 H | 87 / 0 / 0.07 | 83 / 0 / 0.09 | 62 / 0 / 0.15 | 86 / 0 / 0.06 | 76 / 0 / 0.12 | 14 / 0 / 0.09 | 43 / 0 / 0.03 | 42 / 0 / 0.06 | 3 / 0 / 0.04 |
| 0.005 H | 0.3 W | 0.05 H | 92 / 0 / 0.07 | 92 / 0 / 0.09 | 86 / 1 / 0.17 | 94 / 0 / 0.06 | 80 / 0 / 0.13 | 15 / 0 / 0.09 | 47 / 0 / 0.06 | 43 / 1 / 0.15 | 3 / 0 / 0.04 |
| 0.005 H | 0.3 W | any | 98 / 0 / 0.07 | 96 / 0 / 0.09 | 89 / 1 / 0.17 | 98 / 1 / 0.21 | 83 / 0 / 0.13 | 16 / 1 / 0.16 | 49 / 1 / 0.17 | 44 / 1 / 0.15 | 3 / 0 / 0.04 |
| 0.01 H | 0.15 W | 0.03 H | 54 / 0 / 0.06 | 63 / 0 / 0.10 | 57 / 0 / 0.11 | 45 / 0 / 0.04 | 2 / 0 / 0.00 | 0 / 0 / 0.00 | 21 / 0 / 0.03 | 0 / 0 / 0.00 | 0 / 0 / 0.00 |
| 0.01 H | 0.15 W | 0.05 H | 56 / 0 / 0.06 | 68 / 0 / 0.10 | 77 / 0 / 0.11 | 47 / 0 / 0.04 | 2 / 0 / 0.00 | 0 / 0 / 0.00 | 21 / 0 / 0.03 | 0 / 0 / 0.00 | 0 / 0 / 0.00 |
| 0.01 H | 0.15 W | any | 57 / 0 / 0.06 | 68 / 0 / 0.10 | 78 / 0 / 0.11 | 48 / 0 / 0.04 | 2 / 0 / 0.00 | 1 / 1 / 0.15 | 22 / 0 / 0.03 | 0 / 0 / 0.00 | 0 / 0 / 0.00 |
| 0.01 H | 0.3 W | 0.03 H | 87 / 0 / 0.08 | 77 / 0 / 0.13 | 58 / 0 / 0.11 | 86 / 0 / 0.06 | 40 / 0 / 0.10 | 4 / 0 / 0.07 | 43 / 0 / 0.03 | 16 / 0 / 0.04 | 0 / 0 / 0.00 |
| 0.01 H | 0.3 W | 0.05 H | 92 / 0 / 0.08 | 85 / 0 / 0.13 | 80 / 0 / 0.11 | 94 / 0 / 0.06 | 42 / 0 / 0.10 | 4 / 0 / 0.07 | 47 / 0 / 0.06 | 17 / 0 / 0.13 | 0 / 0 / 0.00 |
| 0.01 H | 0.3 W | any | 97 / 0 / 0.08 | 87 / 0 / 0.13 | 83 / 0 / 0.11 | 97 / 0 / 0.14 | 43 / 0 / 0.11 | 5 / 1 / 0.15 | 48 / 0 / 0.06 | 17 / 0 / 0.13 | 0 / 0 / 0.00 |
| 0.02 H | 0.15 W | 0.03 H | 4 / 0 / 0.04 | 10 / 0 / 0.05 | 29 / 0 / 0.07 | 2 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 1 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 |
| 0.02 H | 0.15 W | 0.05 H | 4 / 0 / 0.04 | 10 / 0 / 0.05 | 30 / 0 / 0.07 | 2 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 1 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 |
| 0.02 H | 0.15 W | any | 4 / 0 / 0.04 | 10 / 0 / 0.05 | 30 / 0 / 0.07 | 2 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 1 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 |
| 0.02 H | 0.3 W | 0.03 H | 79 / 0 / 0.09 | 46 / 0 / 0.12 | 50 / 0 / 0.12 | 85 / 0 / 0.06 | 5 / 0 / 0.08 | 0 / 0 / 0.00 | 42 / 0 / 0.02 | 2 / 0 / 0.02 | 0 / 0 / 0.00 |
| 0.02 H | 0.3 W | 0.05 H | 83 / 0 / 0.10 | 50 / 0 / 0.12 | 68 / 0 / 0.12 | 92 / 0 / 0.08 | 5 / 0 / 0.08 | 0 / 0 / 0.00 | 44 / 0 / 0.03 | 2 / 0 / 0.02 | 0 / 0 / 0.00 |
| 0.02 H | 0.3 W | any | 86 / 0 / 0.10 | 51 / 0 / 0.12 | 68 / 0 / 0.12 | 94 / 0 / 0.08 | 5 / 0 / 0.08 | 0 / 0 / 0.00 | 45 / 0 / 0.03 | 2 / 0 / 0.02 | 0 / 0 / 0.00 |

With the limits taken (near 0.01 H, span 0.3 W, good 0.05 H), by group and by barrel size (scenes where it knows / wrong / largest error; of the scenes of that kind):

| | one side: 75 % seen | 50 % | 25 % | both, unequal: 75 % | 50 % | 25 % | both, equal: 75 % | 50 % | 25 % |
|---|---|---|---|---|---|---|---|---|---|
| hand masks | 24 / 0 / 0.07, of 24 | 22 / 0 / 0.13, of 24 | 24 / 0 / 0.07, of 24 | 24 / 0 / 0.06, of 24 | 11 / 0 / 0.08, of 24 | 0 / 0 / 0.00, of 24 | 12 / 0 / 0.01, of 12 | 4 / 0 / 0.03, of 12 | 0 / 0 / 0.00, of 12 |
| color model | 68 / 0 / 0.08, of 76 | 63 / 0 / 0.12, of 76 | 56 / 0 / 0.11, of 76 | 70 / 0 / 0.06, of 76 | 31 / 0 / 0.10, of 76 | 4 / 0 / 0.07, of 76 | 35 / 0 / 0.06, of 38 | 13 / 0 / 0.13, of 38 | 0 / 0 / 0.00, of 38 |
| under 45 px | 24 / 0 / 0.07, of 26 | 19 / 0 / 0.07, of 26 | 19 / 0 / 0.06, of 26 | 24 / 0 / 0.05, of 26 | 4 / 0 / 0.08, of 26 | 0 / 0 / 0.00, of 26 | 12 / 0 / 0.03, of 13 | 0 / 0 / 0.00, of 13 | 0 / 0 / 0.00, of 13 |
| 45 to 70 px | 51 / 0 / 0.08, of 54 | 49 / 0 / 0.13, of 54 | 48 / 0 / 0.07, of 54 | 52 / 0 / 0.06, of 54 | 22 / 0 / 0.10, of 54 | 0 / 0 / 0.00, of 54 | 26 / 0 / 0.04, of 27 | 10 / 0 / 0.13, of 27 | 0 / 0 / 0.00, of 27 |
| over 70 px | 17 / 0 / 0.06, of 20 | 17 / 0 / 0.10, of 20 | 13 / 0 / 0.11, of 20 | 18 / 0 / 0.06, of 20 | 16 / 0 / 0.09, of 20 | 4 / 0 / 0.07, of 20 | 9 / 0 / 0.06, of 10 | 7 / 0 / 0.02, of 10 | 0 / 0 / 0.00, of 10 |

## D. The corners alone: a barrel's own side against a cut side

`fill` = the share of body color in the square of side 0.147 W (how far in the lid ends from the side) at the top corner and at the bottom corner of the seen part's end. A square corner is full (1.0); a barrel's own corner is rounded off. Median (10th to 90th percentile; n). `the fuller of the two` = max(top, bottom): low only when BOTH corners are rounded off. (Scenes of the scorecard: an edge, a slanted edge, both sides.)

| group | end | top corner | bottom corner | the fuller of the two |
|---|---|---|---|---|
| hand masks | own | +0.43 (+0.20 to +0.66; n 238) | +0.30 (+0.03 to +0.52; n 238) | +0.48 (+0.24 to +0.69; n 238) |
| hand masks | cut straight | +0.95 (+0.80 to +1.00; n 144) | +0.92 (+0.65 to +1.00; n 144) | +1.00 (+0.83 to +1.00; n 144) |
| hand masks | cut slanted | +0.02 (+0.00 to +0.93; n 142) | +0.59 (+0.00 to +0.94; n 142) | +0.89 (+0.74 to +0.96; n 142) |
| color model | own | +0.42 (+0.13 to +0.71; n 695) | +0.27 (+0.00 to +0.52; n 695) | +0.47 (+0.27 to +0.71; n 695) |
| color model | cut straight | +0.89 (+0.56 to +1.00; n 439) | +0.89 (+0.56 to +1.00; n 439) | +0.95 (+0.74 to +1.00; n 439) |
| color model | cut slanted | +0.00 (+0.00 to +0.92; n 404) | +0.28 (+0.00 to +0.94; n 404) | +0.87 (+0.57 to +0.95; n 404) |

How many ends fall under a limit on the fuller of the two (an end under the limit would be called the barrel's own side):

| group | end | under 0.6 | under 0.7 | under 0.8 | under 0.9 | n |
|---|---|---|---|---|---|---|
| hand masks | own | 187 | 214 | 238 | 238 | 238 |
| hand masks | cut straight | 0 | 0 | 12 | 40 | 144 |
| hand masks | cut slanted | 2 | 7 | 26 | 77 | 142 |
| color model | own | 500 | 615 | 666 | 677 | 695 |
| color model | cut straight | 14 | 31 | 66 | 147 | 439 |
| color model | cut slanted | 43 | 72 | 139 | 263 | 404 |

## E. The real partly hidden barrels of the HOME and CAMPUS train frames

Every hand-drawn box flagged `occluded` (most are hidden by another barrel, and most show 0.8 of their width or more, where the detector takes the seen width as the box and the outline is not asked). `seen` = the width of the seen part (stripe + the body joined to it) / the box's width; errors in box widths; best cost in barrel heights; `span` = how wide the fitting positions are, in W; the last column is the verdict with the limits taken.

| set | frame | barrel | seen | centred: error | outline: error | best cost | span | |
|---|---|---|---|---|---|---|---|---|
| HOME hand masks | cluster_01 | orange [313, 115, 356, 164] |  |  |  |  |  | no stripe piece of it |
| HOME hand masks | cluster_01 | orange [361, 117, 400, 163] |  |  |  |  |  | no stripe piece of it |
| HOME hand masks | cluster_02 | orange [390, 116, 432, 163] | 0.9 | -0.024 | -0.021 | 0.023 | 0.11 | knows |
| HOME hand masks | far_02 | orange [244, 105, 273, 135] | 0.86 | 0.034 | 0.017 | 0.017 | 0.15 | knows |
| HOME hand masks | occl_01 | blue [386, 115, 430, 161] |  |  |  |  |  | no stripe piece of it |
| HOME hand masks | occl_02 | orange [395, 114, 441, 158] |  |  |  |  |  | no stripe piece of it |
| HOME hand masks | touch_02 | orange [148, 121, 192, 176] | 0.95 | 0.023 | 0.052 | 0.022 | 0.15 | knows |
| HOME | cluster_01 | orange [313, 115, 356, 164] |  |  |  |  |  | no stripe piece of it |
| HOME | cluster_01 | orange [361, 117, 400, 163] | 0.38 | -0.256 | -0.288 | 0.019 | 0.47 | does not know |
| HOME | cluster_02 | orange [390, 116, 432, 163] | 0.86 | 0.024 | 0.194 | 0.045 | 0.17 | knows |
| HOME | far_02 | orange [244, 105, 273, 135] | 0.79 | 0.034 | 0.041 | 0.018 | 0.22 | knows |
| HOME | occl_01 | blue [386, 115, 430, 161] | 1.02 | 0.034 | 0.034 | 0.056 | 0.13 | does not know |
| HOME | occl_02 | orange [395, 114, 441, 158] |  |  |  |  |  | no stripe piece of it |
| HOME | touch_02 | orange [148, 121, 192, 176] | 0.8 | 0.011 | -0.005 | 0.017 | 0.25 | knows |
| CAMPUS | cluster_02 | blue [379, 117, 419, 163] | 0.88 | -0.037 | -0.09 | 0.031 | 0.15 | knows |
| CAMPUS | clutter_02 | blue [475, 122, 522, 174] | 0.47 | 0.138 | 0.08 | 0.038 | 0.44 | does not know |
| CAMPUS | occl_02 | blue [275, 123, 328, 180] | 0.64 | -0.142 | -0.157 | 0.067 | 0.38 | does not know |
