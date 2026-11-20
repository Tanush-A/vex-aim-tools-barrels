# The boxes of `slices_behind`: what the wrong ones have in common (REPORT ONLY, a lead)

Arm `combined`. Scorecard: 3888 scenes, a box is right when it is in the right place of a true barrel. Damaged masks: the 16 HOME hand masks at typical, bad day, bad day without the stripe patch, light, medium and worst seen, seeds 0 to 19 (1920 masks); a box is right when it matches a hand-drawn box (v2). Nothing here was used to decide anything.

| boxes of `slices_behind` | scorecard: right | scorecard: wrong | damaged masks: right | damaged masks: wrong |
|---|---|---|---|---|
| all | 117 | 0 | 93 | 9 |
| hidden side = the frame edge | 85 | 0 | 44 | 0 |
| hidden side = a found barrel | 32 | 0 | 49 | 9 |
| ... whose bottom is 0 to 0.05 H below the slice's predicted bottom | 4 | 0 | 4 | 1 |
| ... whose bottom is 0.05 to 0.1 H below the slice's predicted bottom | 2 | 0 | 7 | 4 |
| ... whose bottom is 0.1 to 0.15 H below the slice's predicted bottom | 5 | 0 | 5 | 1 |
| ... whose bottom is 0.15 to 0.25 H below the slice's predicted bottom | 1 | 0 | 16 | 3 |
| ... whose bottom is 0.25 to 0.5 H below the slice's predicted bottom | 19 | 0 | 0 | 0 |
| ... whose bottom is 0.5 to 9 H below the slice's predicted bottom | 1 | 0 | 17 | 0 |

Damaged masks, by level (right / wrong): white tables, bad day: 8 / 1; medium: 44 / 4; white tables, worst seen: 41 / 4.

Every wrong box on the damaged masks:

| level | color | box | hidden side | slice width / W | the hiding barrel's bottom below the predicted one (px; share of H) |
|---|---|---|---|---|---|
| white tables, bad day | orange | [379, 118, 424, 162] | found barrel | 0.25 | 6.6; 0.136 |
| medium | blue | [317, 120, 364, 166] | found barrel | 0.24 | 3.4; 0.068 |
| medium | orange | [359, 117, 401, 160] | found barrel | 0.19 | 8.1; 0.176 |
| medium | orange | [385, 118, 430, 157] | found barrel | 1.19 | 3.0; 0.061 |
| medium | blue | [313, 121, 359, 164] | found barrel | 0.13 | 4.7; 0.094 |
| white tables, worst seen | blue | [314, 121, 360, 164] | found barrel | 0.15 | 4.7; 0.094 |
| white tables, worst seen | orange | [358, 117, 399, 159] | found barrel | 0.15 | 10.7; 0.239 |
| white tables, worst seen | orange | [359, 117, 401, 160] | found barrel | 0.19 | 8.1; 0.176 |
| white tables, worst seen | blue | [386, 121, 435, 164] | found barrel | 0.97 | 0.3; 0.006 |

Scorecard, right boxes hidden by a found barrel: its bottom is below the predicted one by a median 0.39 H (10th percentile 0.05, lowest 0.03).
