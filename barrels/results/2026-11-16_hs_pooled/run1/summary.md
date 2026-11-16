# The hs color model fit on all train tables

git bb65914; v2 rule; train frames only; new arms scored leave-one-scene-tag-out. Rule: `experiments/2026-11-16_hs_pooled/PREREG.md`.

## The ranges (each arm fit on all its fit frames)

- `base`: orange hue 3 to 13, S >= 140; blue hue 103 to 119, S >= 113
- `all`: orange hue 4 to 18, S >= 126; blue hue 12 to 113, S >= 67
- `nowood`: orange hue 4 to 17, S >= 140; blue hue 97 to 115, S >= 131
- `blue`: orange hue 3 to 13, S >= 140; blue hue 12 to 113, S >= 67

## Found / barrels (false boxes), score

| set | base | all | nowood | blue |
|---|---|---|---|---|
| HOME | 25 / 29 (0), 0.93 | 21 / 29 (14), 0.67 | 24 / 29 (1), 0.89 | 22 / 29 (15), 0.68 |
| CAMPUS | 34 / 35 (0), 0.99 | 33 / 35 (6), 0.90 | 32 / 35 (2), 0.93 | 33 / 35 (4), 0.92 |
| BLACK | 2 / 26 (0), 0.12 | 6 / 26 (3), 0.33 | 4 / 26 (3), 0.23 | 0 / 26 (3), 0.00 |
| WOOD bright | 7 / 126 (3), 0.10 | 21 / 126 (204), 0.12 | 10 / 126 (4), 0.14 | 21 / 126 (134), 0.15 |
| WOOD dark | 0 / 63 (0), 0.00 | 0 / 63 (10), 0.00 | 0 / 63 (0), 0.00 | 0 / 63 (13), 0.00 |
| DAVE* | 11 / 34 (2), 0.47 | 7 / 34 (6), 0.33 | 8 / 34 (1), 0.40 | 8 / 34 (4), 0.37 |
|   wood cool1 | 0 / 21 (0), 0.00 | 0 / 21 (3), 0.00 | 0 / 21 (0), 0.00 | 0 / 21 (2), 0.00 |
|   wood cool3 | 2 / 21 (0), 0.17 | 5 / 21 (16), 0.22 | 2 / 21 (0), 0.15 | 3 / 21 (19), 0.10 |
|   wood cool6 | 2 / 21 (2), 0.16 | 10 / 21 (17), 0.43 | 4 / 21 (1), 0.31 | 7 / 21 (16), 0.38 |
|   wood mid1 | 0 / 21 (0), 0.00 | 0 / 21 (2), 0.00 | 0 / 21 (0), 0.00 | 0 / 21 (7), 0.00 |
|   wood mid3 | 1 / 21 (0), 0.08 | 3 / 21 (38), 0.10 | 1 / 21 (1), 0.08 | 4 / 21 (16), 0.19 |
|   wood mid6 | 1 / 21 (0), 0.08 | 1 / 21 (42), 0.03 | 2 / 21 (0), 0.15 | 3 / 21 (23), 0.09 |
|   wood warm1 | 0 / 21 (0), 0.00 | 0 / 21 (5), 0.00 | 0 / 21 (0), 0.00 | 0 / 21 (4), 0.00 |
|   wood warm3 | 1 / 21 (0), 0.08 | 2 / 21 (34), 0.07 | 1 / 21 (1), 0.08 | 2 / 21 (24), 0.06 |
|   wood warm6 | 0 / 21 (1), 0.00 | 0 / 21 (57), 0.00 | 0 / 21 (1), 0.00 | 2 / 21 (36), 0.05 |

## Black + bright wood, by scene tag: found / barrels (false)

| scene | base | all | nowood | blue |
|---|---|---|---|---|
| close | 6 / 9 (1) | 1 / 9 (9) | 6 / 9 (1) | 0 / 9 (33) |
| cluster | 0 / 28 (0) | 3 / 28 (0) | 0 / 28 (0) | 1 / 28 (0) |
| clutter | 0 / 28 (0) | 9 / 28 (49) | 0 / 28 (1) | 8 / 28 (41) |
| core | 0 / 24 (0) | 6 / 24 (28) | 0 / 24 (1) | 8 / 24 (20) |
| far | 0 / 4 (0) | 1 / 4 (0) | 1 / 4 (1) | 0 / 4 (0) |
| held | 1 / 9 (0) | 1 / 9 (38) | 4 / 9 (0) | 0 / 9 (3) |
| neg | 0 / 0 (0) | 0 / 0 (43) | 0 / 0 (0) | 0 / 0 (12) |
| occl | 2 / 36 (2) | 3 / 36 (8) | 2 / 36 (3) | 2 / 36 (4) |
| touch | 0 / 14 (0) | 3 / 14 (32) | 1 / 14 (0) | 2 / 14 (24) |

## Acceptance

- `all`: 1 home >= 0.91 and campus >= 0.97: FAIL; 2 no box on a clean negative: pass; 3 found on black + bright wood: 27 of 152 (base 9)
- `nowood`: 1 home >= 0.91 and campus >= 0.97: FAIL; 2 no box on a clean negative: pass; 3 found on black + bright wood: 14 of 152 (base 9)
- `blue`: 1 home >= 0.91 and campus >= 0.97: FAIL; 2 no box on a clean negative: pass; 3 found on black + bright wood: 21 of 152 (base 9)

**By conditions 1 to 3: no arm passes.** Condition 4 (by eye on the sheets) is recorded in `by_eye.md`.
