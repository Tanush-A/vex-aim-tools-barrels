# The detector given good segmentation

git be63ff2; v2 rule; train frames only; camera AIM_4A8B6118_BOXFIT. Cells: found / barrels (false boxes). Level 2 rows add up 5 seeds of the 16 HOME frames (29 barrels each).

| level | scenario | in the rule | rules | stencil | union | veto | veto+union | union1 |
|---|---|---|---|---|---|---|---|---|
| 1 | perfect masks (HOME) | yes | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) |
| 2 | light | yes | 143 / 145 (0) | 135 / 145 (0) | 143 / 145 (0) | 143 / 145 (0) | 143 / 145 (0) | 143 / 145 (0) |
| 2 | medium | yes | 99 / 145 (1) | 37 / 145 (0) | 99 / 145 (2) | 97 / 145 (1) | 97 / 145 (2) | 99 / 145 (2) |
| 2 | heavy | yes | 21 / 145 (0) | 4 / 145 (0) | 21 / 145 (0) | 16 / 145 (0) | 16 / 145 (0) | 21 / 145 (0) |
| 2s | top highlight 0.5 x 0.3 | report only | 141 / 145 (0) | 124 / 145 (4) | 142 / 145 (0) | 141 / 145 (0) | 142 / 145 (0) | 142 / 145 (0) |
| 2s | top highlight 0.7 x 0.4 | report only | 132 / 145 (7) | 38 / 145 (0) | 132 / 145 (7) | 132 / 145 (7) | 132 / 145 (7) | 132 / 145 (7) |
| 2s | stripe highlight 0.15 | report only | 132 / 145 (3) | 138 / 145 (0) | 140 / 145 (3) | 132 / 145 (3) | 140 / 145 (3) | 140 / 145 (3) |
| 2s | stripe highlight 0.3 | report only | 136 / 145 (0) | 138 / 145 (0) | 140 / 145 (0) | 136 / 145 (0) | 140 / 145 (0) | 140 / 145 (0) |
| 2s | stripe breaks 2 x 0.08 | report only | 133 / 145 (1) | 141 / 145 (0) | 142 / 145 (2) | 133 / 145 (1) | 142 / 145 (2) | 142 / 145 (2) |
| 2s | edges 1 px | report only | 145 / 145 (0) | 140 / 145 (0) | 145 / 145 (0) | 145 / 145 (0) | 145 / 145 (0) | 145 / 145 (0) |
| 2s | edges 2 px | report only | 110 / 145 (0) | 130 / 145 (0) | 125 / 145 (0) | 110 / 145 (0) | 125 / 145 (0) | 125 / 145 (0) |
| 2s | dropout 10 % | report only | 140 / 145 (0) | 140 / 145 (0) | 140 / 145 (0) | 140 / 145 (0) | 140 / 145 (0) | 140 / 145 (0) |
| 2s | speckle 30 | report only | 140 / 145 (0) | 140 / 145 (0) | 140 / 145 (0) | 140 / 145 (0) | 140 / 145 (0) | 140 / 145 (0) |
| 3a | CAMPUS, adopted color model | yes | 35 / 35 (0) | 31 / 35 (1) | 35 / 35 (0) | 35 / 35 (0) | 35 / 35 (0) | 35 / 35 (0) |
| 3b | BLACK, thresholds from the frame's labels | yes | 19 / 26 (2) | 17 / 26 (0) | 19 / 26 (2) | 19 / 26 (2) | 19 / 26 (2) | 19 / 26 (2) |
| 3c | wood cool lamp, thresholds from the frame's labels | report only | 27 / 42 (2) | 17 / 42 (2) | 28 / 42 (2) | 27 / 42 (2) | 28 / 42 (2) | 28 / 42 (2) |

## What each damage level is (fractions of the barrel's box, W wide and H tall)

- `light`: top_highlight (0.3, 0.2), erode_px 1, dropout 0.02, speckle 5
- `medium`: top_highlight (0.5, 0.3), stripe_highlight 0.15, stripe_breaks (1, 0.06), erode_px 1, dropout 0.05, speckle 15
- `heavy`: top_highlight (0.7, 0.4), stripe_highlight 0.3, stripe_breaks (2, 0.08), erode_px 2, dropout 0.1, speckle 30
- `top highlight 0.5 x 0.3`: top_highlight (0.5, 0.3)
- `top highlight 0.7 x 0.4`: top_highlight (0.7, 0.4)
- `stripe highlight 0.15`: stripe_highlight 0.15
- `stripe highlight 0.3`: stripe_highlight 0.3
- `stripe breaks 2 x 0.08`: stripe_breaks (2, 0.08)
- `edges 1 px`: erode_px 1
- `edges 2 px`: erode_px 2
- `dropout 10 %`: dropout 0.1
- `speckle 30`: speckle 30

## Which test refused the missed barrels (the detector's reason log)

### `rules`

- 1 perfect masks (HOME): stripe_refused:height 1
- 2 light: stripe_refused:height 2
- 2 medium: stripe_refused:width 33, stripe_refused:area 5, stripe_refused:height 4, stripe_refused:side_unexplained 2, misplaced 2
- 2 heavy: stripe_refused:width 44, stripe_not_sandwiched 32, stripe_refused:area 26, stripe_hidden 14, stripe_refused:height 7, not_segmented 1
- 2s top highlight 0.5 x 0.3: stripe_refused:height 3, stripe_refused:side_unexplained 1
- 2s top highlight 0.7 x 0.4: stripe_refused:width 5, stripe_refused:side_unexplained 5, misplaced 3
- 2s stripe highlight 0.15: stripe_refused:height 6, misplaced 3, stripe_refused:side_unexplained 2, stripe_refused:width 2
- 2s stripe highlight 0.3: stripe_refused:height 5, stripe_refused:side_unexplained 2, stripe_refused:width 2
- 2s stripe breaks 2 x 0.08: stripe_refused:width 6, stripe_refused:height 3, stripe_refused:side_unexplained 2, misplaced 1
- 2s edges 2 px: stripe_refused:height 30, stripe_refused:side_unexplained 5
- 2s dropout 10 %: stripe_refused:height 5
- 2s speckle 30: stripe_refused:height 5
- 3b BLACK, thresholds from the frame's labels: stripe_refused:width 2, stripe_refused:height 2, misplaced 2, stripe_not_sandwiched 1, (of the misses and false boxes: right barrel, bottom differs from the hand estimate) 1
- 3c wood cool lamp, thresholds from the frame's labels: stripe_not_sandwiched 4, stripe_refused:height 4, stripe_refused:width 3, stripe_refused:side_unexplained 2, misplaced 2

### `stencil`

- 1 perfect masks (HOME): stripe_not_sandwiched 1
- 2 light: stripe_not_sandwiched 10
- 2 medium: stripe_not_sandwiched 108
- 2 heavy: stripe_not_sandwiched 123, stripe_hidden 17, not_segmented 1
- 2s top highlight 0.5 x 0.3: stripe_not_sandwiched 17, misplaced 4, (of the misses and false boxes: right barrel, bottom differs from the hand estimate) 4
- 2s top highlight 0.7 x 0.4: stripe_not_sandwiched 107
- 2s stripe highlight 0.15: stripe_not_sandwiched 7
- 2s stripe highlight 0.3: stripe_not_sandwiched 7
- 2s stripe breaks 2 x 0.08: stripe_not_sandwiched 4
- 2s edges 1 px: stripe_not_sandwiched 5
- 2s edges 2 px: stripe_not_sandwiched 15
- 2s dropout 10 %: stripe_not_sandwiched 5
- 2s speckle 30: stripe_not_sandwiched 5
- 3a CAMPUS, adopted color model: misplaced 2, stripe_hidden 1, stripe_not_sandwiched 1
- 3b BLACK, thresholds from the frame's labels: stripe_not_sandwiched 8, stripe_hidden 1
- 3c wood cool lamp, thresholds from the frame's labels: stripe_not_sandwiched 23, misplaced 2

### `union`

- 1 perfect masks (HOME): stripe_refused:height 1
- 2 light: stripe_refused:height 2
- 2 medium: stripe_refused:width 33, stripe_refused:area 5, stripe_refused:height 4, stripe_refused:side_unexplained 2, misplaced 2
- 2 heavy: stripe_refused:width 44, stripe_not_sandwiched 32, stripe_refused:area 26, stripe_hidden 14, stripe_refused:height 7, not_segmented 1
- 2s top highlight 0.5 x 0.3: stripe_refused:height 3
- 2s top highlight 0.7 x 0.4: stripe_refused:width 5, stripe_refused:side_unexplained 5, misplaced 3
- 2s stripe highlight 0.15: stripe_refused:height 5
- 2s stripe highlight 0.3: stripe_refused:height 5
- 2s stripe breaks 2 x 0.08: stripe_refused:height 2, stripe_refused:width 1
- 2s edges 2 px: stripe_refused:height 15, stripe_refused:side_unexplained 5
- 2s dropout 10 %: stripe_refused:height 5
- 2s speckle 30: stripe_refused:height 5
- 3b BLACK, thresholds from the frame's labels: stripe_refused:width 2, stripe_refused:height 2, misplaced 2, stripe_not_sandwiched 1, (of the misses and false boxes: right barrel, bottom differs from the hand estimate) 1
- 3c wood cool lamp, thresholds from the frame's labels: stripe_refused:height 4, stripe_refused:width 3, stripe_not_sandwiched 3, stripe_refused:side_unexplained 2, misplaced 2

### `veto`

- 1 perfect masks (HOME): stripe_refused:height 1
- 2 light: stripe_refused:height 2
- 2 medium: stripe_refused:width 33, stripe_refused:area 7, stripe_refused:height 4, stripe_refused:side_unexplained 2, misplaced 2
- 2 heavy: stripe_refused:width 47, stripe_not_sandwiched 34, stripe_refused:area 26, stripe_hidden 14, stripe_refused:height 7, not_segmented 1
- 2s top highlight 0.5 x 0.3: stripe_refused:height 3, stripe_refused:side_unexplained 1
- 2s top highlight 0.7 x 0.4: stripe_refused:width 5, stripe_refused:side_unexplained 5, misplaced 3
- 2s stripe highlight 0.15: stripe_refused:height 6, misplaced 3, stripe_refused:side_unexplained 2, stripe_refused:width 2
- 2s stripe highlight 0.3: stripe_refused:height 5, stripe_refused:side_unexplained 2, stripe_refused:width 2
- 2s stripe breaks 2 x 0.08: stripe_refused:width 6, stripe_refused:height 3, stripe_refused:side_unexplained 2, misplaced 1
- 2s edges 2 px: stripe_refused:height 30, stripe_refused:side_unexplained 5
- 2s dropout 10 %: stripe_refused:height 5
- 2s speckle 30: stripe_refused:height 5
- 3b BLACK, thresholds from the frame's labels: stripe_refused:width 2, stripe_refused:height 2, misplaced 2, stripe_not_sandwiched 1, (of the misses and false boxes: right barrel, bottom differs from the hand estimate) 1
- 3c wood cool lamp, thresholds from the frame's labels: stripe_not_sandwiched 4, stripe_refused:height 4, stripe_refused:width 3, stripe_refused:side_unexplained 2, misplaced 2

### `veto+union`

- 1 perfect masks (HOME): stripe_refused:height 1
- 2 light: stripe_refused:height 2
- 2 medium: stripe_refused:width 33, stripe_refused:area 7, stripe_refused:height 4, stripe_refused:side_unexplained 2, misplaced 2
- 2 heavy: stripe_refused:width 47, stripe_not_sandwiched 34, stripe_refused:area 26, stripe_hidden 14, stripe_refused:height 7, not_segmented 1
- 2s top highlight 0.5 x 0.3: stripe_refused:height 3
- 2s top highlight 0.7 x 0.4: stripe_refused:width 5, stripe_refused:side_unexplained 5, misplaced 3
- 2s stripe highlight 0.15: stripe_refused:height 5
- 2s stripe highlight 0.3: stripe_refused:height 5
- 2s stripe breaks 2 x 0.08: stripe_refused:height 2, stripe_refused:width 1
- 2s edges 2 px: stripe_refused:height 15, stripe_refused:side_unexplained 5
- 2s dropout 10 %: stripe_refused:height 5
- 2s speckle 30: stripe_refused:height 5
- 3b BLACK, thresholds from the frame's labels: stripe_refused:width 2, stripe_refused:height 2, misplaced 2, stripe_not_sandwiched 1, (of the misses and false boxes: right barrel, bottom differs from the hand estimate) 1
- 3c wood cool lamp, thresholds from the frame's labels: stripe_refused:height 4, stripe_refused:width 3, stripe_not_sandwiched 3, stripe_refused:side_unexplained 2, misplaced 2

### `union1`

- 1 perfect masks (HOME): stripe_refused:height 1
- 2 light: stripe_refused:height 2
- 2 medium: stripe_refused:width 33, stripe_refused:area 5, stripe_refused:height 4, stripe_refused:side_unexplained 2, misplaced 2
- 2 heavy: stripe_refused:width 44, stripe_not_sandwiched 32, stripe_refused:area 26, stripe_hidden 14, stripe_refused:height 7, not_segmented 1
- 2s top highlight 0.5 x 0.3: stripe_refused:height 3
- 2s top highlight 0.7 x 0.4: stripe_refused:width 5, stripe_refused:side_unexplained 5, misplaced 3
- 2s stripe highlight 0.15: stripe_refused:height 5
- 2s stripe highlight 0.3: stripe_refused:height 5
- 2s stripe breaks 2 x 0.08: stripe_refused:height 2, stripe_refused:width 1
- 2s edges 2 px: stripe_refused:height 15, stripe_refused:side_unexplained 5
- 2s dropout 10 %: stripe_refused:height 5
- 2s speckle 30: stripe_refused:height 5
- 3b BLACK, thresholds from the frame's labels: stripe_refused:width 2, stripe_refused:height 2, misplaced 2, stripe_not_sandwiched 1, (of the misses and false boxes: right barrel, bottom differs from the hand estimate) 1
- 3c wood cool lamp, thresholds from the frame's labels: stripe_refused:height 4, stripe_refused:width 3, stripe_not_sandwiched 3, stripe_refused:side_unexplained 2, misplaced 2

## Level 1 and level 3: every missed barrel and every false box

### `rules`

| scenario | frame | what | box | flags | cause | detail |
|---|---|---|---|---|---|---|
| 1 perfect masks (HOME) | window_light_cluster_01 | missed orange | [361, 117, 400, 163] | bottom_estimated+occluded | stripe_refused:height | stripe (361, 120, 396, 147) {'core_h': 19.0, 'expected_stripe_h': 10.69} |
| 3b BLACK | window_black_close_02 | missed orange | [0, 132, 51, 207] | truncated | stripe_refused:width | stripe (32, 163, 35, 176) {'core_h': 11.0, 'expected_w': 64.7} |
| 3b BLACK | window_black_close_02 | missed blue | [5, 127, 74, 186] | occluded | stripe_refused:width | stripe (64, 154, 69, 162) {'core_h': 7.6, 'expected_w': 57.06} |
| 3b BLACK | window_black_clutter_02 | missed orange | [246, 108, 276, 140] |  | stripe_refused:height | stripe (250, 122, 273, 126) {'core_h': 3.0, 'expected_stripe_h': 8.62} |
| 3b BLACK | window_black_far_01 | missed orange | [279, 112, 323, 157] |  | misplaced | box (278, 112, 329, 164) iou 0.75 flags ['top_inferred'] |
| 3b BLACK | window_black_far_01 | false orange | [278, 112, 329, 164] | top_inferred | false_box | det2 |
| 3b BLACK | window_black_held_01 | missed orange | [0, 132, 48, 208] | truncated | stripe_not_sandwiched | 418 stripe px in the box but no candidate with body above and below |
| 3b BLACK | window_black_held_01 | missed blue | [3, 127, 73, 189] | occluded | stripe_refused:height | stripe (64, 154, 67, 162) {'core_h': 6.0, 'expected_stripe_h': 14.37} |
| 3b BLACK | window_black_occl_04 | missed orange | [267, 129, 334, 193] | bottom_estimated+occluded | misplaced | box (268, 128, 335, 200) iou 0.86 flags ['bottom_inferred', 'occluded'] |
| 3b BLACK | window_black_occl_04 | false orange | [268, 128, 335, 200] | bottom_inferred+occluded | right_barrel_bottom_differs_from_hand_estimate | det3; label bottom 193, box bottom 200 |

### `stencil`

| scenario | frame | what | box | flags | cause | detail |
|---|---|---|---|---|---|---|
| 1 perfect masks (HOME) | window_light_cluster_01 | missed orange | [361, 117, 400, 163] | bottom_estimated+occluded | stripe_not_sandwiched | 893 stripe px in the box but no candidate with body above and below |
| 3a CAMPUS | campus_light_cluster_02 | missed blue | [342, 120, 391, 171] |  | misplaced | box (328, 120, 375, 168) iou 0.50 flags ['occluded'] |
| 3a CAMPUS | campus_light_cluster_02 | false blue | [328, 120, 375, 168] | occluded | false_box | stencil |
| 3a CAMPUS | campus_light_clutter_02 | missed blue | [475, 122, 522, 174] | occluded | misplaced | box (440, 125, 492, 179) iou 0.19 flags [] |
| 3a CAMPUS | campus_light_held_01 | missed blue | [97, 332, 512, 479] |  | stripe_hidden | 0 stripe px in the box; body piece: none |
| 3a CAMPUS | campus_light_occl_02 | missed blue | [275, 123, 328, 180] | occluded | stripe_not_sandwiched | 163 stripe px in the box but no candidate with body above and below |
| 3b BLACK | window_black_close_02 | missed orange | [0, 132, 51, 207] | truncated | stripe_not_sandwiched | 468 stripe px in the box but no candidate with body above and below |
| 3b BLACK | window_black_close_02 | missed blue | [5, 127, 74, 186] | occluded | stripe_not_sandwiched | 142 stripe px in the box but no candidate with body above and below |
| 3b BLACK | window_black_close_02 | missed orange | [154, 245, 426, 480] | truncated | stripe_not_sandwiched | 855 stripe px in the box but no candidate with body above and below |
| 3b BLACK | window_black_clutter_02 | missed orange | [246, 108, 276, 140] |  | stripe_not_sandwiched | 59 stripe px in the box but no candidate with body above and below |
| 3b BLACK | window_black_held_01 | missed orange | [0, 132, 48, 208] | truncated | stripe_not_sandwiched | 418 stripe px in the box but no candidate with body above and below |
| 3b BLACK | window_black_held_01 | missed blue | [3, 127, 73, 189] | occluded | stripe_not_sandwiched | 86 stripe px in the box but no candidate with body above and below |
| 3b BLACK | window_black_held_01 | missed orange | [90, 327, 521, 480] | held+truncated | stripe_hidden | 0 stripe px in the box; body piece: none |
| 3b BLACK | window_black_occl_03 | missed orange | [283, 121, 338, 178] | bottom_estimated+occluded | stripe_not_sandwiched | 1370 stripe px in the box but no candidate with body above and below |
| 3b BLACK | window_black_occl_04 | missed orange | [267, 129, 334, 193] | bottom_estimated+occluded | stripe_not_sandwiched | 1797 stripe px in the box but no candidate with body above and below |

### `union`

| scenario | frame | what | box | flags | cause | detail |
|---|---|---|---|---|---|---|
| 1 perfect masks (HOME) | window_light_cluster_01 | missed orange | [361, 117, 400, 163] | bottom_estimated+occluded | stripe_refused:height | stripe (361, 120, 396, 147) {'core_h': 19.0, 'expected_stripe_h': 10.69} |
| 3b BLACK | window_black_close_02 | missed orange | [0, 132, 51, 207] | truncated | stripe_refused:width | stripe (32, 163, 35, 176) {'core_h': 11.0, 'expected_w': 64.7} |
| 3b BLACK | window_black_close_02 | missed blue | [5, 127, 74, 186] | occluded | stripe_refused:width | stripe (64, 154, 69, 162) {'core_h': 7.6, 'expected_w': 57.06} |
| 3b BLACK | window_black_clutter_02 | missed orange | [246, 108, 276, 140] |  | stripe_refused:height | stripe (250, 122, 273, 126) {'core_h': 3.0, 'expected_stripe_h': 8.62} |
| 3b BLACK | window_black_far_01 | missed orange | [279, 112, 323, 157] |  | misplaced | box (278, 112, 329, 164) iou 0.75 flags ['top_inferred'] |
| 3b BLACK | window_black_far_01 | false orange | [278, 112, 329, 164] | top_inferred | false_box | det2 |
| 3b BLACK | window_black_held_01 | missed orange | [0, 132, 48, 208] | truncated | stripe_not_sandwiched | 418 stripe px in the box but no candidate with body above and below |
| 3b BLACK | window_black_held_01 | missed blue | [3, 127, 73, 189] | occluded | stripe_refused:height | stripe (64, 154, 67, 162) {'core_h': 6.0, 'expected_stripe_h': 14.37} |
| 3b BLACK | window_black_occl_04 | missed orange | [267, 129, 334, 193] | bottom_estimated+occluded | misplaced | box (268, 128, 335, 200) iou 0.86 flags ['bottom_inferred', 'occluded'] |
| 3b BLACK | window_black_occl_04 | false orange | [268, 128, 335, 200] | bottom_inferred+occluded | right_barrel_bottom_differs_from_hand_estimate | det3; label bottom 193, box bottom 200 |

### `veto`

| scenario | frame | what | box | flags | cause | detail |
|---|---|---|---|---|---|---|
| 1 perfect masks (HOME) | window_light_cluster_01 | missed orange | [361, 117, 400, 163] | bottom_estimated+occluded | stripe_refused:height | stripe (361, 120, 396, 147) {'core_h': 19.0, 'expected_stripe_h': 10.69} |
| 3b BLACK | window_black_close_02 | missed orange | [0, 132, 51, 207] | truncated | stripe_refused:width | stripe (32, 163, 35, 176) {'core_h': 11.0, 'expected_w': 64.7} |
| 3b BLACK | window_black_close_02 | missed blue | [5, 127, 74, 186] | occluded | stripe_refused:width | stripe (64, 154, 69, 162) {'core_h': 7.6, 'expected_w': 57.06} |
| 3b BLACK | window_black_clutter_02 | missed orange | [246, 108, 276, 140] |  | stripe_refused:height | stripe (250, 122, 273, 126) {'core_h': 3.0, 'expected_stripe_h': 8.62} |
| 3b BLACK | window_black_far_01 | missed orange | [279, 112, 323, 157] |  | misplaced | box (278, 112, 329, 164) iou 0.75 flags ['top_inferred'] |
| 3b BLACK | window_black_far_01 | false orange | [278, 112, 329, 164] | top_inferred | false_box | det2 |
| 3b BLACK | window_black_held_01 | missed orange | [0, 132, 48, 208] | truncated | stripe_not_sandwiched | 418 stripe px in the box but no candidate with body above and below |
| 3b BLACK | window_black_held_01 | missed blue | [3, 127, 73, 189] | occluded | stripe_refused:height | stripe (64, 154, 67, 162) {'core_h': 6.0, 'expected_stripe_h': 14.37} |
| 3b BLACK | window_black_occl_04 | missed orange | [267, 129, 334, 193] | bottom_estimated+occluded | misplaced | box (268, 128, 335, 200) iou 0.86 flags ['bottom_inferred', 'occluded'] |
| 3b BLACK | window_black_occl_04 | false orange | [268, 128, 335, 200] | bottom_inferred+occluded | right_barrel_bottom_differs_from_hand_estimate | det3; label bottom 193, box bottom 200 |

### `veto+union`

| scenario | frame | what | box | flags | cause | detail |
|---|---|---|---|---|---|---|
| 1 perfect masks (HOME) | window_light_cluster_01 | missed orange | [361, 117, 400, 163] | bottom_estimated+occluded | stripe_refused:height | stripe (361, 120, 396, 147) {'core_h': 19.0, 'expected_stripe_h': 10.69} |
| 3b BLACK | window_black_close_02 | missed orange | [0, 132, 51, 207] | truncated | stripe_refused:width | stripe (32, 163, 35, 176) {'core_h': 11.0, 'expected_w': 64.7} |
| 3b BLACK | window_black_close_02 | missed blue | [5, 127, 74, 186] | occluded | stripe_refused:width | stripe (64, 154, 69, 162) {'core_h': 7.6, 'expected_w': 57.06} |
| 3b BLACK | window_black_clutter_02 | missed orange | [246, 108, 276, 140] |  | stripe_refused:height | stripe (250, 122, 273, 126) {'core_h': 3.0, 'expected_stripe_h': 8.62} |
| 3b BLACK | window_black_far_01 | missed orange | [279, 112, 323, 157] |  | misplaced | box (278, 112, 329, 164) iou 0.75 flags ['top_inferred'] |
| 3b BLACK | window_black_far_01 | false orange | [278, 112, 329, 164] | top_inferred | false_box | det2 |
| 3b BLACK | window_black_held_01 | missed orange | [0, 132, 48, 208] | truncated | stripe_not_sandwiched | 418 stripe px in the box but no candidate with body above and below |
| 3b BLACK | window_black_held_01 | missed blue | [3, 127, 73, 189] | occluded | stripe_refused:height | stripe (64, 154, 67, 162) {'core_h': 6.0, 'expected_stripe_h': 14.37} |
| 3b BLACK | window_black_occl_04 | missed orange | [267, 129, 334, 193] | bottom_estimated+occluded | misplaced | box (268, 128, 335, 200) iou 0.86 flags ['bottom_inferred', 'occluded'] |
| 3b BLACK | window_black_occl_04 | false orange | [268, 128, 335, 200] | bottom_inferred+occluded | right_barrel_bottom_differs_from_hand_estimate | det3; label bottom 193, box bottom 200 |

### `union1`

| scenario | frame | what | box | flags | cause | detail |
|---|---|---|---|---|---|---|
| 1 perfect masks (HOME) | window_light_cluster_01 | missed orange | [361, 117, 400, 163] | bottom_estimated+occluded | stripe_refused:height | stripe (361, 120, 396, 147) {'core_h': 19.0, 'expected_stripe_h': 10.69} |
| 3b BLACK | window_black_close_02 | missed orange | [0, 132, 51, 207] | truncated | stripe_refused:width | stripe (32, 163, 35, 176) {'core_h': 11.0, 'expected_w': 64.7} |
| 3b BLACK | window_black_close_02 | missed blue | [5, 127, 74, 186] | occluded | stripe_refused:width | stripe (64, 154, 69, 162) {'core_h': 7.6, 'expected_w': 57.06} |
| 3b BLACK | window_black_clutter_02 | missed orange | [246, 108, 276, 140] |  | stripe_refused:height | stripe (250, 122, 273, 126) {'core_h': 3.0, 'expected_stripe_h': 8.62} |
| 3b BLACK | window_black_far_01 | missed orange | [279, 112, 323, 157] |  | misplaced | box (278, 112, 329, 164) iou 0.75 flags ['top_inferred'] |
| 3b BLACK | window_black_far_01 | false orange | [278, 112, 329, 164] | top_inferred | false_box | det2 |
| 3b BLACK | window_black_held_01 | missed orange | [0, 132, 48, 208] | truncated | stripe_not_sandwiched | 418 stripe px in the box but no candidate with body above and below |
| 3b BLACK | window_black_held_01 | missed blue | [3, 127, 73, 189] | occluded | stripe_refused:height | stripe (64, 154, 67, 162) {'core_h': 6.0, 'expected_stripe_h': 14.37} |
| 3b BLACK | window_black_occl_04 | missed orange | [267, 129, 334, 193] | bottom_estimated+occluded | misplaced | box (268, 128, 335, 200) iou 0.86 flags ['bottom_inferred', 'occluded'] |
| 3b BLACK | window_black_occl_04 | false orange | [268, 128, 335, 200] | bottom_inferred+occluded | right_barrel_bottom_differs_from_hand_estimate | det3; label bottom 193, box bottom 200 |

# Expected barrel size against the hand-drawn boxes

Camera `AIM_4A8B6118_BOXFIT` (f 400, tilt 22.25, horizon row 76). Train frames only. Boxes flagged occluded, truncated, held or bottom_estimated, and boxes touching the frame, are left out.
Ratio = hand-drawn size / the size the camera model expects for a barrel whose bottom edge is at the box's bottom row (what `g` in the box tool draws). Median (10th to 90th percentile).
`bottom from top` = the bottom row the detector predicts from the box's top row, minus the drawn bottom row, in px (+ = predicted lower).

| set | boxes | width ratio | height ratio | bottom from top, px |
|---|---|---|---|---|
| HOME | 19 | 0.99 (0.93 to 1.03) | 0.97 (0.93 to 1.00) | 4.40 (-0.60 to 8.44) |
| CAMPUS | 32 | 0.98 (0.92 to 1.10) | 0.97 (0.89 to 1.01) | 5.35 (-3.05 to 11.54) |
| BLACK | 14 | 1.03 (0.96 to 1.17) | 0.99 (0.95 to 1.02) | 1.10 (-4.92 to 5.58) |
| WOOD bright | 84 | 0.95 (0.93 to 1.09) | 0.96 (0.90 to 0.99) | 7.05 (3.30 to 10.20) |
| WOOD dark | 42 | 0.96 (0.93 to 1.09) | 0.96 (0.90 to 0.99) | 7.05 (3.30 to 10.20) |
| wood, all 9 lamp settings | 126 | 0.95 (0.93 to 1.09) | 0.96 (0.90 to 0.99) | 7.05 (3.30 to 10.20) |

By distance (expected width: far under 35 px, mid 35 to 60, near over 60):

| set | range | boxes | width ratio | height ratio | bottom from top, px |
|---|---|---|---|---|---|
| HOME | far | 3 | 0.96 (0.93 to 1.06) | 0.91 (0.86 to 0.93) | 7.40 (5.80 to 11.16) |
| HOME | mid | 12 | 0.99 (0.92 to 1.03) | 0.97 (0.94 to 0.98) | 4.50 (2.82 to 8.27) |
| HOME | near | 4 | 1.02 (1.01 to 1.03) | 1.00 (1.00 to 1.02) | -0.90 (-3.50 to -0.40) |
| CAMPUS | mid | 17 | 0.95 (0.91 to 1.04) | 0.95 (0.90 to 0.98) | 6.60 (2.22 to 9.98) |
| CAMPUS | near | 15 | 1.02 (0.94 to 1.28) | 1.00 (0.87 to 1.02) | 0.70 (-5.10 to 101.68) |
| BLACK | far | 1 | 0.91 (0.91 to 0.91) | 0.89 (0.89 to 0.89) | 9.10 (9.10 to 9.10) |
| BLACK | mid | 6 | 1.06 (1.03 to 1.21) | 0.98 (0.95 to 0.99) | 3.25 (1.10 to 5.50) |
| BLACK | near | 7 | 1.00 (0.97 to 1.05) | 1.01 (1.00 to 1.02) | -3.30 (-5.10 to -0.38) |
| WOOD | mid | 54 | 0.96 (0.92 to 1.15) | 0.93 (0.89 to 0.99) | 7.65 (1.10 to 13.90) |
| WOOD | near | 72 | 0.95 (0.94 to 1.09) | 0.96 (0.94 to 0.99) | 5.70 (3.30 to 10.20) |
