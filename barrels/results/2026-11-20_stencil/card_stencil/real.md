# The real occluded barrels of the train frames, one by one

Every hand-drawn box flagged `occluded` or `truncated` (cut by the frame). HOME = segmented as in the eval table; BLACK and WOOD are the extreme sets (adopted color model, report only). found = v2 rule; place = a box of the right color centred within half a barrel width.

| set | frame | barrel | flags | `rules` | `stencil` |
|---|---|---|---|---|---|
| HOME hand masks | cluster_01 | orange [313, 115, 356, 164] | occluded | found, overlap 0.81, width 1.14 | found, overlap 0.86, width 1.05 |
| HOME hand masks | cluster_01 | orange [361, 117, 400, 163] | bottom_estimated+occluded | no box (stripe_refused:height) | no box (stripe_not_sandwiched) |
| HOME hand masks | cluster_02 | orange [390, 116, 432, 163] | occluded | found, overlap 0.89, width 0.93 | found, overlap 0.91, width 1.0 |
| HOME hand masks | edge_01 | blue [0, 133, 34, 198] | truncated | found, overlap 1.0, width 1.0 | found, overlap 0.91, width 1.03 |
| HOME hand masks | far_02 | orange [244, 105, 273, 135] | occluded | found, overlap 0.88, width 1.07 | found, overlap 0.94, width 1.03 |
| HOME hand masks | occl_01 | blue [386, 115, 430, 161] | bottom_estimated+occluded | found, overlap 0.98, width 1.0 | found, overlap 0.89, width 0.95 |
| HOME hand masks | occl_02 | orange [395, 114, 441, 158] | bottom_estimated+occluded | found, overlap 0.83, width 0.91 | found, overlap 0.85, width 0.91 |
| HOME hand masks | top_01 | orange [163, 259, 452, 480] | bottom_estimated+no_stripe+truncated | found, overlap 1.0, width 1.0 | found, overlap 0.97, width 0.99 |
| HOME hand masks | topstripe_01 | orange [173, 240, 426, 480] | bottom_estimated+truncated | found, overlap 1.0, width 1.0 | found, overlap 0.87, width 1.13 |
| HOME hand masks | touch_02 | orange [148, 121, 192, 176] | occluded | found, overlap 0.94, width 0.95 | found, overlap 0.84, width 1.11 |
| HOME | cluster_01 | orange [313, 115, 356, 164] | occluded | found, overlap 0.71, width 1.19 | found, overlap 0.86, width 0.98 |
| HOME | cluster_01 | orange [361, 117, 400, 163] | bottom_estimated+occluded | no box (stripe_refused:width) | no box (stripe_not_sandwiched) |
| HOME | cluster_02 | orange [390, 116, 432, 163] | occluded | found, overlap 0.8, width 0.86 | found, overlap 0.83, width 1.0 |
| HOME | edge_01 | blue [0, 133, 34, 198] | truncated | found, overlap 0.91, width 0.94 | found, overlap 0.75, width 0.79 |
| HOME | far_02 | orange [244, 105, 273, 135] | occluded | found, overlap 0.79, width 1.07 | found, overlap 0.94, width 1.03 |
| HOME | occl_01 | blue [386, 115, 430, 161] | bottom_estimated+occluded | found, overlap 0.82, width 1.02 | found, overlap 0.89, width 0.95 |
| HOME | occl_02 | orange [395, 114, 441, 158] | bottom_estimated+occluded | found, overlap 0.76, width 0.87 | found, overlap 0.82, width 0.91 |
| HOME | top_01 | orange [163, 259, 452, 480] | bottom_estimated+no_stripe+truncated | found, overlap 0.98, width 0.99 | found, overlap 0.91, width 0.94 |
| HOME | topstripe_01 | orange [173, 240, 426, 480] | bottom_estimated+truncated | found, overlap 0.97, width 0.98 | no box (stripe_not_sandwiched) |
| HOME | touch_02 | orange [148, 121, 192, 176] | occluded | found, overlap 0.89, width 0.95 | found, overlap 0.84, width 1.11 |
| CAMPUS | cluster_02 | blue [379, 117, 419, 163] | occluded | found, overlap 0.71, width 1.15 | found, overlap 0.78, width 1.12 |
| CAMPUS | clutter_02 | blue [475, 122, 522, 174] | occluded | found, overlap 0.84, width 1.09 | no box (misplaced) |
| CAMPUS | occl_02 | blue [275, 123, 328, 180] | occluded | found, overlap 0.82, width 1.02 | no box (stripe_not_sandwiched) |
| BLACK (extreme) | close_02 | orange [0, 132, 51, 207] | truncated | no box (stripe_not_sandwiched) | no box (stripe_not_sandwiched) |
| BLACK (extreme) | close_02 | blue [5, 127, 74, 186] | occluded | no box (stripe_refused:area) | no box (stripe_hidden) |
| BLACK (extreme) | close_02 | orange [154, 245, 426, 480] | truncated | found, overlap 0.72, width 0.76 | no box (stripe_not_sandwiched) |
| BLACK (extreme) | cluster_01 | orange [256, 119, 305, 173] | occluded | no box (stripe_refused:width) | no box (stripe_not_sandwiched) |
| BLACK (extreme) | clutter_02 | blue [0, 135, 73, 212] | truncated | no box (stripe_refused:area) | no box (stripe_hidden) |
| BLACK (extreme) | clutter_02 | orange [530, 144, 640, 247] | truncated | right place, not v2, overlap 0.8, width 0.92 (misplaced) | no box (stripe_not_sandwiched) |
| BLACK (extreme) | held_01 | orange [0, 132, 48, 208] | truncated | no box (stripe_refused:area) | no box (stripe_not_sandwiched) |
| BLACK (extreme) | held_01 | blue [3, 127, 73, 189] | occluded | no box (stripe_refused:area) | no box (stripe_hidden) |
| BLACK (extreme) | held_01 | orange [90, 327, 521, 480] | held+truncated | found, overlap 0.69, width 0.73 | no box (stripe_hidden) |
| BLACK (extreme) | occl_02 | orange [271, 122, 327, 178] | bottom_estimated+occluded | no box (stripe_refused:width) | no box (stripe_not_sandwiched) |
| BLACK (extreme) | occl_03 | orange [283, 121, 338, 178] | bottom_estimated+occluded | no box (not_segmented) | no box (not_segmented) |
| BLACK (extreme) | occl_04 | orange [267, 129, 334, 193] | bottom_estimated+occluded | no box (stripe_refused:width) | no box (not_segmented) |

Totals (found under v2 / box in the right place / barrels):

| set | `rules` | `stencil` |
|---|---|---|
| HOME hand masks | 9 / 9 / 10 | 9 / 9 / 10 |
| HOME | 9 / 9 / 10 | 8 / 8 / 10 |
| CAMPUS | 3 / 3 / 3 | 1 / 1 / 3 |
| BLACK (extreme) | 2 / 3 / 12 | 0 / 0 / 12 |
| WOOD (extreme) | 7 / 8 / 63 | 3 / 3 / 63 |
