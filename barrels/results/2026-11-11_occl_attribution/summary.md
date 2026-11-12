# Occlusion attribution — detector overrides: none (the detector as it stands)

Train frames only, v2 rule. `occl` = truth barrels flagged `occluded`.

| set | frames | barrels | found | missed | false | occl barrels | occl found |
|---|---|---|---|---|---|---|---|
| CAMPUS | 21 | 35 | 34 | 1 | 0 | 3 | 2 |
| HOME | 16 | 29 | 25 | 4 | 1 | 7 | 3 |

## Every occluded barrel, every miss, every false box

| frame | barrel | flags | found | cause | detail | body px / stripe px in its box |
|---|---|---|---|---|---|---|
| campus_light_cluster_02 | blue [379, 117, 419, 163] | occluded | yes | found |  | 942 / 316 |
| campus_light_clutter_02 | blue [475, 122, 522, 174] | occluded | yes | found |  | 1209 / 471 |
| campus_light_occl_02 | blue [275, 123, 328, 180] | occluded | NO | stripe_refused:width | stripe (278, 148, 294, 160) {'core_h': 9.0, 'expected_w': 53.58} | 636 / 163 |
| window_light_cluster_01 | orange [313, 115, 356, 164] | occluded | NO | misplaced | box (339, 109, 378, 153) iou 0.20 flags ['occluded', 'top_inferred'] | 784 / 771 |
| window_light_cluster_01 | orange [361, 117, 400, 163] | bottom_estimated+occluded | NO | misplaced | box (339, 109, 378, 153) iou 0.21 flags ['occluded', 'top_inferred'] | 403 / 646 |
| window_light_cluster_01 | orange [339, 109, 378, 153] | occluded+top_inferred | NO | false_box | det2 | 0 / 0 |
| window_light_cluster_02 | orange [390, 116, 432, 163] | occluded | yes | found |  | 885 / 330 |
| window_light_far_02 | orange [244, 105, 273, 135] | occluded | yes | found |  | 434 / 169 |
| window_light_occl_01 | blue [386, 115, 430, 161] | bottom_estimated+occluded | NO | stripe_refused:height | stripe (388, 145, 421, 182) {'core_h': 29.0, 'expected_stripe_h': 15.35} | 784 / 894 |
| window_light_occl_02 | orange [395, 114, 441, 158] | bottom_estimated+occluded | NO | stripe_refused:height | stripe (398, 143, 439, 182) {'core_h': 28.0, 'expected_stripe_h': 15.35} | 652 / 880 |
| window_light_touch_02 | orange [148, 121, 192, 176] | occluded | yes | found |  | 1275 / 327 |
