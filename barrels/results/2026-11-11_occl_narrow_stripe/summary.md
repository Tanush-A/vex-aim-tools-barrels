# A barrel hidden at the side: lower stripe-width floor, hidden side from the body

git 194bc1c; adopted color model; v2 rule; train frames only. Rule and hypothesis: `experiments/2026-11-11_occl_narrow_stripe/PREREG.md`.

## Labeled frames

| config | HOME v2 (found / false / missed) | CAMPUS v2 (found / false / missed) | Dave v2 | barrels lost vs base | barrels gained vs base | mean IoU of found barrels, HOME / CAMPUS | `occl_02` barrel (IoU) |
|---|---|---|---|---|---|---|---|
| base | 0.91 (25 / 1 / 4) | 0.99 (34 / 0 / 1) | 0.47 (11 / 2 / 23) | 0 | 0 | 0.878 / 0.865 | missed (0.00) |
| w25 | 0.91 (25 / 1 / 4) | 1.00 (35 / 0 / 0) | 0.49 (12 / 2 / 22) | 0 | 1 | 0.878 / 0.855 | found (0.51) |
| w25h | 0.91 (25 / 1 / 4) | 1.00 (35 / 0 / 0) | 0.49 (12 / 2 / 22) | 0 | 1 | 0.888 / 0.859 | found (0.68) |
| h | 0.91 (25 / 1 / 4) | 0.99 (34 / 0 / 1) | 0.47 (11 / 2 / 23) | 0 | 0 | 0.888 / 0.864 | missed (0.00) |
| w35 (report only) | 0.91 (25 / 1 / 4) | 0.99 (34 / 0 / 1) | 0.49 (12 / 2 / 22) | 0 | 0 | 0.878 / 0.865 | missed (0.00) |
| w30 (report only) | 0.91 (25 / 1 / 4) | 0.99 (34 / 0 / 1) | 0.49 (12 / 2 / 22) | 0 | 0 | 0.878 / 0.865 | missed (0.00) |
| w20 (report only) | 0.89 (25 / 2 / 4) | 1.00 (35 / 0 / 0) | 0.49 (12 / 2 / 22) | 0 | 1 | 0.879 / 0.855 | found (0.51) |

HOME here uses the adopted model on all 16 home frames (the model was fit on them), so it is not the leave-one-scene-out headline number; it is only for comparing detector configs.

## Unlabeled frames: boxes against `base`

| config | set | frames | boxes | added | removed | moved | largest edge shift of a moved box (median / max px) |
|---|---|---|---|---|---|---|---|
| base | WOOD (unlabeled) | 25 | 61 | 0 | 0 | 0 |  |
| base | REC (unlabeled) | 238 | 462 | 0 | 0 | 0 |  |
| base | LIVE (unlabeled) | 1 | 2 | 0 | 0 | 0 |  |
| w25 | WOOD (unlabeled) | 25 | 63 | 2 | 0 | 0 |  |
| w25 | REC (unlabeled) | 238 | 466 | 4 | 0 | 0 |  |
| w25 | LIVE (unlabeled) | 1 | 2 | 0 | 0 | 0 |  |
| w25h | WOOD (unlabeled) | 25 | 63 | 2 | 0 | 18 | 8 / 38 |
| w25h | REC (unlabeled) | 238 | 466 | 4 | 0 | 72 | 2 / 12 |
| w25h | LIVE (unlabeled) | 1 | 2 | 0 | 0 | 0 |  |
| h | WOOD (unlabeled) | 25 | 61 | 0 | 0 | 18 | 8 / 38 |
| h | REC (unlabeled) | 238 | 462 | 0 | 0 | 72 | 2 / 12 |
| h | LIVE (unlabeled) | 1 | 2 | 0 | 0 | 0 |  |
| w35 (report only) | WOOD (unlabeled) | 25 | 61 | 0 | 0 | 0 |  |
| w35 (report only) | REC (unlabeled) | 238 | 462 | 0 | 0 | 0 |  |
| w35 (report only) | LIVE (unlabeled) | 1 | 2 | 0 | 0 | 0 |  |
| w30 (report only) | WOOD (unlabeled) | 25 | 63 | 2 | 0 | 0 |  |
| w30 (report only) | REC (unlabeled) | 238 | 463 | 1 | 0 | 0 |  |
| w30 (report only) | LIVE (unlabeled) | 1 | 2 | 0 | 0 | 0 |  |
| w20 (report only) | WOOD (unlabeled) | 25 | 63 | 2 | 0 | 0 |  |
| w20 (report only) | REC (unlabeled) | 238 | 469 | 7 | 0 | 0 |  |
| w20 (report only) | LIVE (unlabeled) | 1 | 2 | 0 | 0 | 0 |  |

## Acceptance (conditions 1, 2, 3, 5 by the script; 4 by eye)

- **w25h**: 1 no found barrel lost (HOME, CAMPUS): pass; 2 no false box added (HOME, CAMPUS): pass; 3 Dave score not lower: pass; 4 boxes added on unlabeled frames are real (BY EYE, see sheets): by eye; 5 occl_02 barrel found: pass
- **w25**: 1 no found barrel lost (HOME, CAMPUS): pass; 2 no false box added (HOME, CAMPUS): pass; 3 Dave score not lower: pass; 4 boxes added on unlabeled frames are real (BY EYE, see sheets): by eye; 5 occl_02 barrel found: pass
