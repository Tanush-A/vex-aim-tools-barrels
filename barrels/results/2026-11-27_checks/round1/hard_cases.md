# The hard cases: what the checks remove, by kind (question 3)

From `harness_removed.csv` (every box removed in the proof harness). 'on a barrel' = found or box off before; 'not' = wrong color, second box, on nothing; 'unscored' = no truth for that mask. Expected width W from the box's top row.

## S: solid paint only, solidity under 0.40 dropped (P) — 46 boxes removed

| group | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| damage | 32 | 0 | 0 |
| real | 2 | 2 | 0 |
| scene | 10 | 0 | 0 |

| reason | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| speckle | 44 | 2 | 0 |

| rule that drew it | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| body_span | 24 | 0 | 0 |
| cap | 1 | 0 | 0 |
| centred | 4 | 0 | 0 |
| closeup | 2 | 1 | 0 |
| half_stripe | 1 | 0 | 0 |
| hidden_side | 6 | 0 | 0 |
| pair | 1 | 0 | 0 |
| thin_frame | 1 | 0 | 0 |
| thin_span | 2 | 0 | 0 |
| whole_stripe | 2 | 1 | 0 |

| scene kind (amount hidden) | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (not a scene) | 34 | 2 | 0 |
| both 0.5 | 1 | 0 | 0 |
| edge 0.25 | 1 | 0 | 0 |
| frame 0.25 | 1 | 0 | 0 |
| frame 0.5 | 1 | 0 | 0 |
| frame 0.75 | 1 | 0 | 0 |
| post 0.5 | 1 | 0 | 0 |
| post 0.75 | 1 | 0 | 0 |
| slant 0.25 | 2 | 0 | 0 |
| top 0.5 | 1 | 0 | 0 |

| expected width | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| 25-60 px | 20 | 1 | 0 |
| close, W >= 60 px | 24 | 1 | 0 |

| place of the frame | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (scene) | 10 | 0 | 0 |
| campus_study | 21 | 0 | 0 |
| home_bathtile | 1 | 0 | 0 |
| home_glass | 0 | 1 | 0 |
| home_white | 11 | 0 | 0 |
| home_wooddesk | 1 | 0 | 0 |
| uc_palewood | 0 | 1 | 0 |

## L: label only, stripe over 1.25 x a stripe height with body under 0.6 dropped (P) — 79 boxes removed

| group | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| damage | 10 | 7 | 0 |
| real | 2 | 4 | 0 |
| real_dilate | 1 | 5 | 0 |
| real_erode | 0 | 2 | 0 |
| scene | 41 | 7 | 0 |

| reason | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| label | 54 | 25 | 0 |

| rule that drew it | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| body_span | 7 | 2 | 0 |
| centred | 10 | 7 | 0 |
| hidden_side | 14 | 1 | 0 |
| thin_span | 1 | 0 | 0 |
| whole_stripe | 22 | 15 | 0 |

| scene kind (amount hidden) | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (not a scene) | 13 | 18 | 0 |
| barrel_front/same 0.25 | 0 | 2 | 0 |
| barrel_front/same 0.5 | 0 | 2 | 0 |
| barrel_front/same 0.75 | 0 | 1 | 0 |
| barrel_low/other 0.25 | 3 | 0 | 0 |
| barrel_low/other 0.5 | 3 | 0 | 0 |
| barrel_low/other 0.75 | 6 | 0 | 0 |
| barrel_low/same 0.5 | 1 | 0 | 0 |
| barrel_side/other 0.25 | 2 | 0 | 0 |
| barrel_side/other 0.5 | 13 | 1 | 0 |
| barrel_side/other 0.75 | 11 | 0 | 0 |
| barrel_side/same 0.5 | 1 | 0 | 0 |
| barrel_side/same 0.75 | 1 | 1 | 0 |

| expected width | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| 25-60 px | 45 | 24 | 0 |
| close, W >= 60 px | 9 | 1 | 0 |

| place of the frame | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (scene) | 41 | 7 | 0 |
| campus_study | 0 | 8 | 0 |
| home_glass | 0 | 8 | 0 |
| home_white | 10 | 0 | 0 |
| home_wooddesk | 3 | 1 | 0 |
| uc_palewood | 0 | 1 | 0 |

## SL: both, at P (0.40; 1.25 / 0.6) — 124 boxes removed

| group | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| damage | 42 | 7 | 0 |
| real | 4 | 5 | 0 |
| real_dilate | 1 | 5 | 0 |
| real_erode | 0 | 2 | 0 |
| scene | 51 | 7 | 0 |

| reason | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| label | 54 | 24 | 0 |
| speckle | 44 | 2 | 0 |

| rule that drew it | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| body_span | 31 | 2 | 0 |
| cap | 1 | 0 | 0 |
| centred | 14 | 7 | 0 |
| closeup | 2 | 1 | 0 |
| half_stripe | 1 | 0 | 0 |
| hidden_side | 20 | 1 | 0 |
| pair | 1 | 0 | 0 |
| thin_frame | 1 | 0 | 0 |
| thin_span | 3 | 0 | 0 |
| whole_stripe | 24 | 15 | 0 |

| scene kind (amount hidden) | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (not a scene) | 47 | 19 | 0 |
| barrel_front/same 0.25 | 0 | 2 | 0 |
| barrel_front/same 0.5 | 0 | 2 | 0 |
| barrel_front/same 0.75 | 0 | 1 | 0 |
| barrel_low/other 0.25 | 3 | 0 | 0 |
| barrel_low/other 0.5 | 3 | 0 | 0 |
| barrel_low/other 0.75 | 6 | 0 | 0 |
| barrel_low/same 0.5 | 1 | 0 | 0 |
| barrel_side/other 0.25 | 2 | 0 | 0 |
| barrel_side/other 0.5 | 13 | 1 | 0 |
| barrel_side/other 0.75 | 11 | 0 | 0 |
| barrel_side/same 0.5 | 1 | 0 | 0 |
| barrel_side/same 0.75 | 1 | 1 | 0 |
| both 0.5 | 1 | 0 | 0 |
| edge 0.25 | 1 | 0 | 0 |
| frame 0.25 | 1 | 0 | 0 |
| frame 0.5 | 1 | 0 | 0 |
| frame 0.75 | 1 | 0 | 0 |
| post 0.5 | 1 | 0 | 0 |
| post 0.75 | 1 | 0 | 0 |
| slant 0.25 | 2 | 0 | 0 |
| top 0.5 | 1 | 0 | 0 |

| expected width | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| 25-60 px | 65 | 24 | 0 |
| close, W >= 60 px | 33 | 2 | 0 |

| place of the frame | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (scene) | 51 | 7 | 0 |
| campus_study | 21 | 8 | 0 |
| home_bathtile | 1 | 0 | 0 |
| home_glass | 0 | 8 | 0 |
| home_white | 21 | 0 | 0 |
| home_wooddesk | 4 | 1 | 0 |
| uc_palewood | 0 | 2 | 0 |

## Sm: solid paint only, under 0.35 (M) — 18 boxes removed

| group | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| damage | 11 | 0 | 0 |
| real | 1 | 1 | 0 |
| scene | 5 | 0 | 0 |

| reason | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| speckle | 17 | 1 | 0 |

| rule that drew it | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| body_span | 8 | 0 | 0 |
| cap | 1 | 0 | 0 |
| centred | 3 | 0 | 0 |
| closeup | 0 | 1 | 0 |
| hidden_side | 4 | 0 | 0 |
| thin_frame | 1 | 0 | 0 |

| scene kind (amount hidden) | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (not a scene) | 12 | 1 | 0 |
| edge 0.25 | 1 | 0 | 0 |
| frame 0.5 | 1 | 0 | 0 |
| frame 0.75 | 1 | 0 | 0 |
| slant 0.25 | 2 | 0 | 0 |

| expected width | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| 25-60 px | 8 | 0 | 0 |
| close, W >= 60 px | 9 | 1 | 0 |

| place of the frame | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (scene) | 5 | 0 | 0 |
| campus_study | 9 | 0 | 0 |
| home_white | 2 | 0 | 0 |
| home_wooddesk | 1 | 0 | 0 |
| uc_palewood | 0 | 1 | 0 |

## Lm: label only, over 1.5 x with body under 0.6 (M) — 54 boxes removed

| group | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| damage | 9 | 0 | 0 |
| real | 2 | 4 | 0 |
| real_dilate | 1 | 5 | 0 |
| real_erode | 0 | 1 | 0 |
| scene | 25 | 7 | 0 |

| reason | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| label | 37 | 17 | 0 |

| rule that drew it | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| body_span | 5 | 2 | 0 |
| centred | 9 | 7 | 0 |
| hidden_side | 9 | 1 | 0 |
| whole_stripe | 14 | 7 | 0 |

| scene kind (amount hidden) | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (not a scene) | 12 | 10 | 0 |
| barrel_front/same 0.25 | 0 | 2 | 0 |
| barrel_front/same 0.5 | 0 | 2 | 0 |
| barrel_front/same 0.75 | 0 | 1 | 0 |
| barrel_low/other 0.5 | 3 | 0 | 0 |
| barrel_low/other 0.75 | 3 | 0 | 0 |
| barrel_low/same 0.5 | 1 | 0 | 0 |
| barrel_side/other 0.25 | 1 | 0 | 0 |
| barrel_side/other 0.5 | 8 | 1 | 0 |
| barrel_side/other 0.75 | 7 | 0 | 0 |
| barrel_side/same 0.5 | 1 | 0 | 0 |
| barrel_side/same 0.75 | 1 | 1 | 0 |

| expected width | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| 25-60 px | 30 | 16 | 0 |
| close, W >= 60 px | 7 | 1 | 0 |

| place of the frame | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (scene) | 25 | 7 | 0 |
| home_glass | 0 | 8 | 0 |
| home_white | 9 | 0 | 0 |
| home_wooddesk | 3 | 1 | 0 |
| uc_palewood | 0 | 1 | 0 |

## SLm: both, at M (0.35; 1.5 / 0.6) — 72 boxes removed

| group | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| damage | 20 | 0 | 0 |
| real | 3 | 5 | 0 |
| real_dilate | 1 | 5 | 0 |
| real_erode | 0 | 1 | 0 |
| scene | 30 | 7 | 0 |

| reason | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| label | 37 | 17 | 0 |
| speckle | 17 | 1 | 0 |

| rule that drew it | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| body_span | 13 | 2 | 0 |
| cap | 1 | 0 | 0 |
| centred | 12 | 7 | 0 |
| closeup | 0 | 1 | 0 |
| hidden_side | 13 | 1 | 0 |
| thin_frame | 1 | 0 | 0 |
| whole_stripe | 14 | 7 | 0 |

| scene kind (amount hidden) | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (not a scene) | 24 | 11 | 0 |
| barrel_front/same 0.25 | 0 | 2 | 0 |
| barrel_front/same 0.5 | 0 | 2 | 0 |
| barrel_front/same 0.75 | 0 | 1 | 0 |
| barrel_low/other 0.5 | 3 | 0 | 0 |
| barrel_low/other 0.75 | 3 | 0 | 0 |
| barrel_low/same 0.5 | 1 | 0 | 0 |
| barrel_side/other 0.25 | 1 | 0 | 0 |
| barrel_side/other 0.5 | 8 | 1 | 0 |
| barrel_side/other 0.75 | 7 | 0 | 0 |
| barrel_side/same 0.5 | 1 | 0 | 0 |
| barrel_side/same 0.75 | 1 | 1 | 0 |
| edge 0.25 | 1 | 0 | 0 |
| frame 0.5 | 1 | 0 | 0 |
| frame 0.75 | 1 | 0 | 0 |
| slant 0.25 | 2 | 0 | 0 |

| expected width | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| 25-60 px | 38 | 16 | 0 |
| close, W >= 60 px | 16 | 2 | 0 |

| place of the frame | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (scene) | 30 | 7 | 0 |
| campus_study | 9 | 0 | 0 |
| home_glass | 0 | 8 | 0 |
| home_white | 11 | 0 | 0 |
| home_wooddesk | 4 | 1 | 0 |
| uc_palewood | 0 | 2 | 0 |

