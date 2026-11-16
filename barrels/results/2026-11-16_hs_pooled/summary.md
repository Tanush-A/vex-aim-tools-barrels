# The hs color model fit on all train tables

git bb65914; v2 rule; train frames only; new arms scored leave-one-scene-tag-out. Rule: `experiments/2026-11-16_hs_pooled/PREREG.md`.

## The ranges (each arm fit on all its fit frames)

- `base`: orange hue 3 to 13, S >= 140; blue hue 103 to 119, S >= 113
- `all`: orange hue 4 to 18, S >= 126; blue hue 95 to 113, S >= 65
- `nowood`: orange hue 4 to 17, S >= 140; blue hue 97 to 115, S >= 131
- `blue`: orange hue 3 to 13, S >= 140; blue hue 95 to 113, S >= 65

## Found / barrels (false boxes), score

| set | base | all | nowood | blue |
|---|---|---|---|---|
| HOME | 25 / 29 (0), 0.93 | 20 / 29 (12), 0.66 | 24 / 29 (1), 0.89 | 21 / 29 (12), 0.68 |
| CAMPUS | 34 / 35 (0), 0.99 | 33 / 35 (2), 0.94 | 32 / 35 (2), 0.93 | 33 / 35 (1), 0.96 |
| BLACK | 2 / 26 (0), 0.12 | 10 / 26 (3), 0.46 | 4 / 26 (3), 0.23 | 2 / 26 (0), 0.12 |
| WOOD bright | 7 / 126 (3), 0.10 | 18 / 126 (13), 0.23 | 10 / 126 (4), 0.14 | 19 / 126 (6), 0.25 |
| WOOD dark | 0 / 63 (0), 0.00 | 0 / 63 (0), 0.00 | 0 / 63 (0), 0.00 | 0 / 63 (0), 0.00 |
| DAVE* | 11 / 34 (2), 0.47 | 8 / 34 (3), 0.37 | 8 / 34 (1), 0.40 | 8 / 34 (3), 0.37 |
|   wood cool1 | 0 / 21 (0), 0.00 | 0 / 21 (0), 0.00 | 0 / 21 (0), 0.00 | 0 / 21 (0), 0.00 |
|   wood cool3 | 2 / 21 (0), 0.17 | 4 / 21 (1), 0.30 | 2 / 21 (0), 0.15 | 3 / 21 (1), 0.21 |
|   wood cool6 | 2 / 21 (2), 0.16 | 11 / 21 (3), 0.63 | 4 / 21 (1), 0.31 | 11 / 21 (1), 0.67 |
|   wood mid1 | 0 / 21 (0), 0.00 | 0 / 21 (0), 0.00 | 0 / 21 (0), 0.00 | 0 / 21 (0), 0.00 |
|   wood mid3 | 1 / 21 (0), 0.08 | 2 / 21 (4), 0.15 | 1 / 21 (1), 0.08 | 3 / 21 (1), 0.24 |
|   wood mid6 | 1 / 21 (0), 0.08 | 1 / 21 (4), 0.08 | 2 / 21 (0), 0.15 | 1 / 21 (2), 0.08 |
|   wood warm1 | 0 / 21 (0), 0.00 | 0 / 21 (0), 0.00 | 0 / 21 (0), 0.00 | 0 / 21 (0), 0.00 |
|   wood warm3 | 1 / 21 (0), 0.08 | 0 / 21 (0), 0.00 | 1 / 21 (1), 0.08 | 1 / 21 (0), 0.08 |
|   wood warm6 | 0 / 21 (1), 0.00 | 0 / 21 (1), 0.00 | 0 / 21 (1), 0.00 | 0 / 21 (1), 0.00 |

## Black + bright wood, by scene tag: found / barrels (false)

| scene | base | all | nowood | blue |
|---|---|---|---|---|
| close | 6 / 9 (1) | 3 / 9 (2) | 6 / 9 (1) | 5 / 9 (1) |
| cluster | 0 / 28 (0) | 3 / 28 (0) | 0 / 28 (0) | 1 / 28 (0) |
| clutter | 0 / 28 (0) | 4 / 28 (0) | 0 / 28 (1) | 3 / 28 (0) |
| core | 0 / 24 (0) | 3 / 24 (3) | 0 / 24 (1) | 3 / 24 (0) |
| far | 0 / 4 (0) | 2 / 4 (1) | 1 / 4 (1) | 0 / 4 (0) |
| held | 1 / 9 (0) | 5 / 9 (2) | 4 / 9 (0) | 5 / 9 (0) |
| neg | 0 / 0 (0) | 0 / 0 (0) | 0 / 0 (0) | 0 / 0 (0) |
| occl | 2 / 36 (2) | 3 / 36 (8) | 2 / 36 (3) | 2 / 36 (4) |
| touch | 0 / 14 (0) | 5 / 14 (0) | 1 / 14 (0) | 2 / 14 (1) |

## Acceptance

- `all`: 1 home >= 0.91 and campus >= 0.97: FAIL; 2 no box on a clean negative: pass; 3 found on black + bright wood: 28 of 152 (base 9)
- `nowood`: 1 home >= 0.91 and campus >= 0.97: FAIL; 2 no box on a clean negative: pass; 3 found on black + bright wood: 14 of 152 (base 9)
- `blue`: 1 home >= 0.91 and campus >= 0.97: FAIL; 2 no box on a clean negative: pass; 3 found on black + bright wood: 21 of 152 (base 9)

**By conditions 1 to 3: no arm passes.** Condition 4 (by eye on the sheets) is recorded in `by_eye.md`.
