# Ceiling check: per-frame thresholds set from the frame's own labels

git 74484ba; v2 rule; train frames only; today's detector. Not a method: the thresholds read the answer.

## Found / barrels (false boxes), score

| set | base | hue | hue+sat | hue+sat+stripes |
|---|---|---|---|---|
| HOME | 25 / 29 (1), 0.91 | 25 / 29 (1), 0.91 | 25 / 29 (5), 0.86 | 25 / 29 (5), 0.86 |
| CAMPUS | 34 / 35 (0), 0.99 | 33 / 35 (0), 0.97 | 27 / 35 (0), 0.86 | 30 / 35 (1), 0.91 |
| BLACK | 2 / 26 (0), 0.12 | 6 / 26 (5), 0.29 | 14 / 26 (1), 0.69 | 17 / 26 (1), 0.78 |
| WOOD bright | 7 / 126 (3), 0.10 | 9 / 126 (3), 0.12 | 29 / 126 (21), 0.33 | 36 / 126 (31), 0.37 |
| WOOD dark | 0 / 63 (0), 0.00 | 0 / 63 (0), 0.00 | 0 / 63 (0), 0.00 | 0 / 63 (0), 0.00 |
|   wood cool3 | 2 / 21 (0), 0.17 | 3 / 21 (0), 0.24 | 7 / 21 (1), 0.47 | 9 / 21 (3), 0.53 |
|   wood cool6 | 2 / 21 (2), 0.16 | 2 / 21 (2), 0.15 | 13 / 21 (3), 0.69 | 15 / 21 (4), 0.75 |
|   wood mid3 | 1 / 21 (0), 0.08 | 1 / 21 (0), 0.08 | 3 / 21 (3), 0.21 | 5 / 21 (6), 0.33 |
|   wood mid6 | 1 / 21 (0), 0.08 | 2 / 21 (0), 0.15 | 3 / 21 (6), 0.20 | 5 / 21 (6), 0.28 |
|   wood warm3 | 1 / 21 (0), 0.08 | 1 / 21 (0), 0.08 | 2 / 21 (2), 0.15 | 2 / 21 (6), 0.14 |
|   wood warm6 | 0 / 21 (1), 0.00 | 0 / 21 (1), 0.00 | 1 / 21 (6), 0.08 | 0 / 21 (6), 0.00 |

## Black + bright wood, by scene tag

| scene | base | hue | hue+sat | hue+sat+stripes |
|---|---|---|---|---|
| close | 6 / 9 (1), 0.67 | 6 / 9 (1), 0.67 | 6 / 9 (1), 0.67 | 2 / 9 (1), 0.38 |
| cluster | 0 / 28 (0), 0.00 | 1 / 28 (0), 0.07 | 6 / 28 (0), 0.35 | 12 / 28 (1), 0.57 |
| clutter | 0 / 28 (0), 0.00 | 1 / 28 (3), 0.06 | 11 / 28 (8), 0.48 | 13 / 28 (8), 0.55 |
| core | 0 / 24 (0), 0.00 | 0 / 24 (0), 0.00 | 5 / 24 (9), 0.29 | 7 / 24 (13), 0.36 |
| far | 0 / 4 (0), 0.00 | 1 / 4 (2), 0.33 | 3 / 4 (1), 0.75 | 3 / 4 (1), 0.75 |
| held | 1 / 9 (0), 0.33 | 4 / 9 (0), 0.63 | 7 / 9 (0), 0.79 | 2 / 9 (0), 0.46 |
| neg | 0 / 0 (0), - | 0 / 0 (0), - | 0 / 0 (0), - | 0 / 0 (0), - |
| occl | 2 / 36 (2), 0.11 | 1 / 36 (1), 0.06 | 3 / 36 (3), 0.14 | 7 / 36 (7), 0.27 |
| touch | 0 / 14 (0), 0.00 | 1 / 14 (1), 0.12 | 2 / 14 (0), 0.25 | 7 / 14 (1), 0.64 |

## Why the remaining barrels on black + bright wood are missed (the detector's reason log)

- `base`: stripe_hidden 45, not_segmented 39, stripe_not_sandwiched 19, stripe_refused:width 16, stripe_refused:area 14, stripe_refused:height 9, misplaced 1
- `hue`: stripe_hidden 42, not_segmented 35, stripe_not_sandwiched 19, stripe_refused:width 18, stripe_refused:area 10, stripe_refused:height 7, misplaced 6
- `hue+sat`: stripe_refused:width 37, stripe_refused:area 22, stripe_hidden 15, stripe_refused:height 14, not_segmented 9, stripe_not_sandwiched 8, misplaced 4
- `hue+sat+stripes`: stripe_refused:width 31, stripe_refused:height 16, stripe_not_sandwiched 13, stripe_hidden 11, stripe_refused:area 10, misplaced 9, not_segmented 8, stripe_refused:body_min 1
