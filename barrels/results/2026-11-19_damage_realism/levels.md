# The occlusion arms on realistic damage

git cdd0ce1; v2 rule; train frames only; the 16 HOME hand masks (29 barrels). Cells: found / barrels (false boxes). `base` = the defaults before the occlusion round; `edge+cap` = today's default on `wip/detector-occl`; `all` = with the three held-back switches (`slice_box`, `cover_unpinned`, `stripe_two`).

## 5 seeds, as in the earlier test (light / medium / heavy must match `results/2026-11-19_det_occl/verdict.md`)

| level | `base` | `edge+cap` | `all` |
|---|---|---|---|
| perfect masks (HOME) | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) |
| white tables, typical | 145 / 145 (0) | 145 / 145 (0) | 145 / 145 (0) |
| white tables, bad day | 135 / 145 (3) | 135 / 145 (3) | 139 / 145 (4) |
| white tables, worst seen | 84 / 145 (2) | 84 / 145 (2) | 113 / 145 (6) |
| light | 143 / 145 (0) | 143 / 145 (0) | 143 / 145 (0) |
| medium | 99 / 145 (1) | 99 / 145 (1) | 124 / 145 (4) |
| heavy | 21 / 145 (0) | 21 / 145 (0) | 24 / 145 (0) |
| real: HOME, leave-one-scene-out | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) |
| real: HOME, stored model | 28 / 29 (1) | 28 / 29 (1) | 28 / 29 (1) |
| real: CAMPUS | 35 / 35 (0) | 35 / 35 (0) | 35 / 35 (0) |

## 20 seeds (the simulated levels only): the false-box counts on four times as many masks

| level | `base` | `edge+cap` | `all` |
|---|---|---|---|
| white tables, typical | 579 / 580 (0) | 579 / 580 (0) | 579 / 580 (0) |
| white tables, bad day | 547 / 580 (5) | 547 / 580 (5) | 560 / 580 (17) |
| white tables, worst seen | 337 / 580 (6) | 337 / 580 (6) | 457 / 580 (17) |
| light | 574 / 580 (0) | 574 / 580 (0) | 572 / 580 (2) |
| medium | 388 / 580 (3) | 388 / 580 (3) | 477 / 580 (20) |
| heavy | 89 / 580 (0) | 89 / 580 (0) | 98 / 580 (0) |

## What each level is

- `white tables, typical`: erode_px 1, speckle 6
- `white tables, bad day`: top_highlight (0.16, 0.09), stripe_highlight 0.06, erode_px 1, dropout 0.005, speckle 20
- `white tables, worst seen`: top_highlight (0.41, 0.3), stripe_highlight 0.4, stripe_breaks (1, 0.03), erode_px 1, dropout 0.014, speckle 37
- `light`: top_highlight (0.3, 0.2), erode_px 1, dropout 0.02, speckle 5
- `medium`: top_highlight (0.5, 0.3), stripe_highlight 0.15, stripe_breaks (1, 0.06), erode_px 1, dropout 0.05, speckle 15
- `heavy`: top_highlight (0.7, 0.4), stripe_highlight 0.3, stripe_breaks (2, 0.08), erode_px 2, dropout 0.1, speckle 30

## One measured kind at a time, at its 90th-percentile amount (`white tables, bad day`), and that level without one kind

5 seeds:

| level | `base` | `edge+cap` | `all` |
|---|---|---|---|
| only top_highlight | 140 / 145 (0) | 140 / 145 (0) | 140 / 145 (0) |
| only stripe_highlight | 134 / 145 (5) | 134 / 145 (5) | 139 / 145 (8) |
| only erode_px | 145 / 145 (0) | 145 / 145 (0) | 145 / 145 (0) |
| only dropout | 140 / 145 (0) | 140 / 145 (0) | 140 / 145 (0) |
| only speckle | 140 / 145 (0) | 140 / 145 (0) | 140 / 145 (0) |
| bad day without top_highlight | 134 / 145 (2) | 134 / 145 (2) | 141 / 145 (1) |
| bad day without stripe_highlight | 144 / 145 (0) | 144 / 145 (0) | 144 / 145 (0) |
| bad day without erode_px | 135 / 145 (3) | 135 / 145 (3) | 139 / 145 (11) |
| bad day without dropout | 135 / 145 (3) | 135 / 145 (3) | 139 / 145 (4) |
| bad day without speckle | 135 / 145 (3) | 135 / 145 (3) | 139 / 145 (4) |

20 seeds:

| level | `base` | `edge+cap` | `all` |
|---|---|---|---|
| only top_highlight | 560 / 580 (0) | 560 / 580 (0) | 560 / 580 (0) |
| only stripe_highlight | 540 / 580 (16) | 540 / 580 (17) | 555 / 580 (31) |
| only erode_px | 580 / 580 (0) | 580 / 580 (0) | 580 / 580 (0) |
| only dropout | 560 / 580 (0) | 560 / 580 (0) | 560 / 580 (0) |
| only speckle | 560 / 580 (0) | 560 / 580 (0) | 560 / 580 (0) |
| bad day without top_highlight | 549 / 580 (6) | 549 / 580 (6) | 567 / 580 (12) |
| bad day without stripe_highlight | 577 / 580 (0) | 577 / 580 (0) | 577 / 580 (0) |
| bad day without erode_px | 540 / 580 (10) | 542 / 580 (11) | 549 / 580 (36) |
| bad day without dropout | 546 / 580 (5) | 546 / 580 (5) | 559 / 580 (18) |
| bad day without speckle | 547 / 580 (5) | 547 / 580 (5) | 560 / 580 (17) |

## Which test refused the missed barrels (5 seeds; the detector's reason log)

- white tables, bad day, `edge+cap`: stripe_refused:height 5, misplaced 3, stripe_refused:side_unexplained 1, stripe_refused:width 1
- white tables, bad day, `all`: stripe_refused:height 5, misplaced 1
- white tables, worst seen, `edge+cap`: stripe_refused:width 49, stripe_refused:area 5, stripe_refused:height 3, misplaced 3, stripe_refused:side_unexplained 1
- white tables, worst seen, `all`: stripe_refused:slice_not_full 16, stripe_refused:width 6, stripe_refused:area 5, misplaced 4, stripe_refused:height 1
- only top_highlight, `edge+cap`: stripe_refused:height 5
- only top_highlight, `all`: stripe_refused:height 5
- only stripe_highlight, `edge+cap`: stripe_refused:height 5, misplaced 3, stripe_refused:width 2, stripe_refused:side_unexplained 1
- only stripe_highlight, `all`: stripe_refused:height 5, misplaced 1
- only dropout, `edge+cap`: stripe_refused:height 5
- only dropout, `all`: stripe_refused:height 5
- only speckle, `edge+cap`: stripe_refused:height 5
- only speckle, `all`: stripe_refused:height 5
- bad day without top_highlight, `edge+cap`: stripe_refused:side_unexplained 3, stripe_refused:height 3, stripe_refused:width 3, misplaced 2
- bad day without top_highlight, `all`: stripe_refused:height 3, stripe_refused:slice_not_full 1
- bad day without stripe_highlight, `edge+cap`: stripe_refused:height 1
- bad day without stripe_highlight, `all`: stripe_refused:height 1
- bad day without erode_px, `edge+cap`: stripe_refused:height 6, misplaced 3, stripe_refused:width 1
- bad day without erode_px, `all`: stripe_refused:height 4, misplaced 2
- bad day without dropout, `edge+cap`: stripe_refused:height 5, misplaced 3, stripe_refused:side_unexplained 1, stripe_refused:width 1
- bad day without dropout, `all`: stripe_refused:height 5, misplaced 1
- bad day without speckle, `edge+cap`: stripe_refused:height 5, misplaced 3, stripe_refused:side_unexplained 1, stripe_refused:width 1
- bad day without speckle, `all`: stripe_refused:height 5, misplaced 1

## Every false box at the realistic levels and on the real segmentations (20 seeds; sheets in `false_sheets/`)

| level | arm | frame | seed | color | box | width / a barrel's | flags | best overlap with a true box of its color | that barrel | also missed |
|---|---|---|---|---|---|---|---|---|---|---|
| white tables, bad day | base | cluster_02 | 0 | orange | [368, 117, 411, 160] | 0.99 | occluded | 0.31 | [390, 116, 432, 163] occluded | yes |
| white tables, bad day | base | touch_02 | 1 | orange | [172, 123, 223, 175] | 0.98 | occluded | 0.26 | [148, 121, 192, 176] occluded | yes |
| white tables, bad day | base | cluster_02 | 4 | orange | [370, 117, 413, 160] | 0.99 | occluded | 0.35 | [390, 116, 432, 163] occluded | yes |
| white tables, bad day | base | touch_02 | 11 | orange | [170, 123, 221, 175] | 0.98 | occluded | 0.29 | [148, 121, 192, 176] occluded | yes |
| white tables, bad day | base | cluster_02 | 15 | orange | [371, 117, 414, 160] | 0.99 | occluded | 0.37 | [390, 116, 432, 163] occluded | yes |
| white tables, bad day | edge+cap | cluster_02 | 0 | orange | [368, 117, 411, 160] | 0.99 | occluded | 0.31 | [390, 116, 432, 163] occluded | yes |
| white tables, bad day | edge+cap | touch_02 | 1 | orange | [172, 123, 223, 175] | 0.98 | occluded | 0.26 | [148, 121, 192, 176] occluded | yes |
| white tables, bad day | edge+cap | cluster_02 | 4 | orange | [370, 117, 413, 160] | 0.99 | occluded | 0.35 | [390, 116, 432, 163] occluded | yes |
| white tables, bad day | edge+cap | touch_02 | 11 | orange | [170, 123, 221, 175] | 0.98 | occluded | 0.29 | [148, 121, 192, 176] occluded | yes |
| white tables, bad day | edge+cap | cluster_02 | 15 | orange | [371, 117, 414, 160] | 0.99 | occluded | 0.37 | [390, 116, 432, 163] occluded | yes |
| white tables, bad day | all | cluster_02 | 1 | blue | [346, 121, 427, 164] | 1.77 | occluded | 0.54 | [351, 119, 398, 167]  | no |
| white tables, bad day | all | cluster_02 | 3 | blue | [346, 121, 428, 164] | 1.79 | occluded | 0.54 | [351, 119, 398, 167]  | no |
| white tables, bad day | all | touch_02 | 3 | orange | [112, 124, 200, 170] | 1.79 | occluded | 0.46 | [148, 121, 192, 176] occluded | yes |
| white tables, bad day | all | touch_02 | 4 | orange | [203, 124, 254, 173] | 1.01 | occluded | 0.16 | [240, 122, 289, 174]  | no |
| white tables, bad day | all | touch_02 | 5 | orange | [236, 124, 326, 171] | 1.81 | occluded | 0.51 | [240, 122, 289, 174]  | no |
| white tables, bad day | all | edge_01 | 6 | blue | [0, 135, 16, 197] | 0.25 | occluded+truncated | 0.45 | [0, 133, 34, 198] truncated | no |
| white tables, bad day | all | cluster_01 | 7 | orange | [377, 118, 422, 162] | 1.01 | occluded | 0.37 | [361, 117, 400, 163] bottom_estimated+occluded | yes |
| white tables, bad day | all | touch_02 | 7 | orange | [236, 124, 326, 171] | 1.81 | occluded | 0.51 | [240, 122, 289, 174]  | no |
| white tables, bad day | all | cluster_01 | 8 | blue | [301, 121, 384, 169] | 1.71 | occluded | 0.58 | [331, 119, 382, 171]  | no |
| white tables, bad day | all | touch_02 | 8 | orange | [236, 123, 323, 172] | 1.74 | occluded | 0.54 | [240, 122, 289, 174]  | no |
| white tables, bad day | all | touch_02 | 10 | orange | [114, 124, 200, 171] | 1.73 | occluded | 0.47 | [148, 121, 192, 176] occluded | yes |
| white tables, bad day | all | edge_01 | 12 | blue | [0, 135, 17, 197] | 0.27 | occluded+truncated | 0.48 | [0, 133, 34, 198] truncated | no |
| white tables, bad day | all | edge_01 | 13 | blue | [0, 135, 16, 197] | 0.25 | occluded+truncated | 0.45 | [0, 133, 34, 198] truncated | no |
| white tables, bad day | all | edge_01 | 15 | blue | [0, 135, 15, 197] | 0.23 | occluded+truncated | 0.42 | [0, 133, 34, 198] truncated | no |
| white tables, bad day | all | cluster_01 | 18 | blue | [386, 121, 472, 164] | 1.88 | occluded | 0.51 | [388, 118, 437, 170]  | yes |
| white tables, bad day | all | touch_02 | 18 | orange | [114, 124, 200, 171] | 1.73 | occluded | 0.47 | [148, 121, 192, 176] occluded | yes |
| white tables, bad day | all | cluster_02 | 19 | blue | [346, 121, 429, 164] | 1.81 | occluded | 0.53 | [351, 119, 398, 167]  | no |
| white tables, worst seen | base | cluster_01 | 3 | blue | [360, 120, 418, 171] | 1.17 |  | 0.37 | [388, 118, 437, 170]  | yes |
| white tables, worst seen | base | touch_02 | 3 | orange | [168, 123, 225, 175] | 1.1 | bottom_inferred+occluded | 0.3 | [148, 121, 192, 176] occluded | yes |
| white tables, worst seen | base | occl_01 | 11 | blue | [369, 125, 429, 190] | 1.0 | bottom_inferred+occluded+top_inferred | 0.35 | [386, 115, 430, 161] bottom_estimated+occluded | yes |
| white tables, worst seen | base | cluster_01 | 13 | blue | [351, 120, 409, 171] | 1.17 |  | 0.39 | [331, 119, 382, 171]  | yes |
| white tables, worst seen | base | occl_01 | 14 | orange | [371, 135, 452, 228] | 0.99 | occluded | 0.45 | [340, 139, 423, 229]  | no |
| white tables, worst seen | base | cluster_01 | 18 | blue | [354, 120, 412, 171] | 1.17 |  | 0.34 | [331, 119, 382, 171]  | yes |
| white tables, worst seen | edge+cap | cluster_01 | 3 | blue | [360, 120, 418, 171] | 1.17 |  | 0.37 | [388, 118, 437, 170]  | yes |
| white tables, worst seen | edge+cap | touch_02 | 3 | orange | [168, 123, 225, 175] | 1.1 | bottom_inferred+occluded | 0.3 | [148, 121, 192, 176] occluded | yes |
| white tables, worst seen | edge+cap | occl_01 | 11 | blue | [369, 125, 429, 190] | 1.0 | bottom_inferred+occluded+top_inferred | 0.35 | [386, 115, 430, 161] bottom_estimated+occluded | yes |
| white tables, worst seen | edge+cap | cluster_01 | 13 | blue | [351, 120, 409, 171] | 1.17 |  | 0.39 | [331, 119, 382, 171]  | yes |
| white tables, worst seen | edge+cap | occl_01 | 14 | orange | [371, 135, 452, 228] | 0.99 | occluded | 0.45 | [340, 139, 423, 229]  | no |
| white tables, worst seen | edge+cap | cluster_01 | 18 | blue | [354, 120, 412, 171] | 1.17 |  | 0.34 | [331, 119, 382, 171]  | yes |
| white tables, worst seen | all | close_01 | 2 | orange | [306, 150, 386, 225] | 1.0 | occluded | 0.74 | [302, 143, 390, 235]  | yes |
| white tables, worst seen | all | touch_02 | 2 | blue | [186, 126, 278, 175] | 1.78 | occluded | 0.53 | [187, 122, 240, 178]  | no |
| white tables, worst seen | all | cluster_01 | 3 | blue | [360, 120, 418, 171] | 1.17 |  | 0.37 | [388, 118, 437, 170]  | yes |
| white tables, worst seen | all | cluster_02 | 3 | orange | [384, 118, 430, 158] | 1.08 | occluded | 0.72 | [390, 116, 432, 163] occluded | yes |
| white tables, worst seen | all | touch_02 | 3 | orange | [236, 123, 325, 172] | 1.78 | occluded | 0.53 | [240, 122, 289, 174]  | no |
| white tables, worst seen | all | cluster_02 | 4 | orange | [307, 121, 388, 168] | 1.69 | occluded | 0.51 | [306, 119, 351, 170]  | no |
| white tables, worst seen | all | cluster_01 | 5 | blue | [360, 120, 407, 168] | 0.98 | occluded | 0.27 | [331, 119, 382, 171]  | no |
| white tables, worst seen | all | far_02 | 7 | blue | [194, 112, 256, 142] | 1.83 | occluded | 0.45 | [218, 106, 250, 144]  | yes |
| white tables, worst seen | all | touch_02 | 9 | orange | [178, 124, 229, 174] | 1.0 | occluded | 0.16 | [148, 121, 192, 176] occluded | yes |
| white tables, worst seen | all | cluster_02 | 11 | orange | [304, 121, 389, 168] | 1.77 | occluded | 0.51 | [306, 119, 351, 170]  | no |
| white tables, worst seen | all | occl_01 | 11 | orange | [389, 136, 470, 228] | 0.99 | occluded | 0.25 | [340, 139, 423, 229]  | no |
| white tables, worst seen | all | cluster_01 | 13 | blue | [351, 120, 409, 171] | 1.17 |  | 0.39 | [331, 119, 382, 171]  | yes |
| white tables, worst seen | all | touch_02 | 13 | orange | [207, 123, 258, 173] | 1.01 | occluded | 0.21 | [240, 122, 289, 174]  | no |
| white tables, worst seen | all | cluster_01 | 15 | orange | [279, 118, 360, 161] | 1.83 | occluded | 0.49 | [313, 115, 356, 164] occluded | yes |
| white tables, worst seen | all | occl_02 | 17 | orange | [362, 118, 442, 152] | 2.04 | occluded | 0.49 | [395, 114, 441, 158] bottom_estimated+occluded | yes |
| white tables, worst seen | all | cluster_01 | 18 | blue | [354, 120, 412, 171] | 1.17 |  | 0.34 | [331, 119, 382, 171]  | yes |
| white tables, worst seen | all | cluster_01 | 18 | blue | [386, 121, 435, 164] | 1.07 | occluded | 0.77 | [388, 118, 437, 170]  | yes |
| real: HOME, stored model | base | cluster_01 |  | orange | [358, 109, 396, 153] | 0.95 | occluded+top_inferred | 0.57 | [361, 117, 400, 163] bottom_estimated+occluded | yes |
| real: HOME, stored model | edge+cap | cluster_01 |  | orange | [358, 109, 396, 153] | 0.95 | occluded+top_inferred | 0.57 | [361, 117, 400, 163] bottom_estimated+occluded | yes |
| real: HOME, stored model | all | cluster_01 |  | orange | [353, 109, 401, 153] | 1.2 | occluded+top_inferred | 0.56 | [361, 117, 400, 163] bottom_estimated+occluded | yes |
