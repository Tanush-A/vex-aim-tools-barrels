# Interactions: the combination against each branch alone, scene by scene

3888 scenes. `vertical_all` = `stack` + the six switches of occl-vertical; `pin`, `pin+thin` = `stack` + those of occl-pin (`sanity/scenes.csv`). Found = the v2 rule against the full box; a box where no barrel is = a box in the right place of no true barrel.

## `combined` against `vertical_all` and `pin`

Found: `vertical_all` 2738, `pin` 2445, by either alone 2764, `combined` 2764. Boxes where no barrel is: 45, 45, `combined` 45.

- **lost** (found by a branch alone, not by the combination): 0 scenes
- **extra** (more boxes where no barrel is than either alone): 0 scenes
- gained (found by the combination only): 0 scenes

## `combined+thin` against `vertical_all` and `pin+thin`

Found: `vertical_all` 2738, `pin+thin` 2556, by either alone 2825, `combined+thin` 2738. Boxes where no barrel is: 45, 45, `combined+thin` 45.

- **lost** (found by a branch alone, not by the combination): 87 scenes
- **extra** (more boxes where no barrel is than either alone): 0 scenes
- gained (found by the combination only): 0 scenes

`lost`, by cell: barrel_low/other at 75 %: 4; barrel_low/same at 75 %: 15; barrel_side/other at 75 %: 10; barrel_side/same at 75 %: 1; frame at 75 %: 57

| lost: pool | row | hidden | variant | frame | color | true box | found alone by | the combination's box | why not found |
|---|---|---|---|---|---|---|---|---|---|
| CAMPUS color model | barrel_low/other | 75 % | L | campus_light_plain_02 | orange | [419, 129, 486, 199] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | barrel_low/same | 75 % | L | campus_light_core_01 | blue | [90, 161, 208, 286] | vertical | none | misplaced |
| CAMPUS color model | barrel_low/same | 75 % | L | campus_light_hand_02 | blue | [127, 124, 188, 187] | vertical | none | misplaced |
| CAMPUS color model | barrel_low/same | 75 % | L | campus_light_plain_02 | orange | [419, 129, 486, 199] | vertical | none | misplaced |
| CAMPUS color model | barrel_low/same | 75 % | L | campus_light_window_01 | blue | [155, 132, 224, 202] | vertical | none | misplaced |
| CAMPUS color model | barrel_low/same | 75 % | L | campus_light_window_01 | orange | [367, 130, 435, 203] | vertical | none | misplaced |
| CAMPUS color model | barrel_low/same | 75 % | R | campus_light_core_01 | blue | [333, 131, 397, 200] | vertical | none | misplaced |
| CAMPUS color model | barrel_low/same | 75 % | R | campus_light_hand_02 | blue | [127, 124, 188, 187] | vertical | none | misplaced |
| CAMPUS color model | barrel_low/same | 75 % | R | campus_light_window_01 | blue | [155, 132, 224, 202] | vertical | none | misplaced |
| CAMPUS color model | barrel_side/other | 75 % | L | campus_light_far_01 | blue | [318, 114, 357, 154] | vertical | none | stripe_refused:height |
| CAMPUS color model | barrel_side/other | 75 % | L | campus_light_far_01 | orange | [379, 113, 414, 150] | vertical | none | stripe_refused:height |
| CAMPUS color model | barrel_side/other | 75 % | L | campus_light_window_01 | orange | [367, 130, 435, 203] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | barrel_side/other | 75 % | R | campus_light_hand_02 | blue | [127, 124, 188, 187] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | barrel_side/same | 75 % | L | campus_light_window_01 | orange | [367, 130, 435, 203] | vertical | none | misplaced |
| CAMPUS color model | frame | 75 % | L | campus_light_close_01 | orange | [0, 182, 37, 357] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | L | campus_light_core_01 | blue | [0, 131, 16, 200] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | L | campus_light_core_01 | blue | [0, 161, 30, 286] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | L | campus_light_core_01 | orange | [0, 131, 16, 202] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | L | campus_light_far_01 | blue | [0, 112, 8, 147] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | L | campus_light_far_01 | blue | [0, 114, 10, 154] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | L | campus_light_far_01 | orange | [0, 113, 9, 150] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | L | campus_light_far_01 | orange | [0, 116, 10, 161] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | L | campus_light_hand_02 | blue | [0, 124, 15, 187] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | L | campus_light_hand_02 | orange | [0, 124, 14, 185] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | L | campus_light_plain_01 | orange | [0, 145, 26, 243] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | L | campus_light_plain_02 | blue | [0, 131, 18, 204] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | L | campus_light_plain_02 | orange | [0, 129, 17, 199] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | L | campus_light_room_01 | orange | [0, 120, 12, 176] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | L | campus_light_room_03 | blue | [0, 112, 9, 153] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | L | campus_light_room_03 | orange | [0, 112, 9, 152] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | L | campus_light_window_01 | orange | [0, 130, 17, 203] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | R | campus_light_close_01 | orange | [603, 182, 640, 357] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | R | campus_light_cluster_02 | orange | [629, 118, 640, 167] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | R | campus_light_clutter_02 | orange | [627, 126, 640, 186] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | R | campus_light_core_01 | blue | [610, 161, 640, 286] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | R | campus_light_core_01 | blue | [624, 131, 640, 200] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | R | campus_light_far_01 | blue | [630, 114, 640, 154] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | R | campus_light_far_01 | blue | [632, 112, 640, 147] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | R | campus_light_far_01 | orange | [630, 116, 640, 161] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | R | campus_light_far_01 | orange | [631, 113, 640, 150] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | R | campus_light_hand_02 | blue | [625, 124, 640, 187] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | R | campus_light_room_01 | blue | [625, 123, 640, 181] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | R | campus_light_room_03 | blue | [631, 112, 640, 153] | vertical | none | stripe_refused:outline_unknown |
| CAMPUS color model | frame | 75 % | R | campus_light_touch_02 | blue | [627, 123, 640, 178] | vertical | none | stripe_refused:outline_unknown |
| HOME color model | barrel_low/other | 75 % | R | window_light_cluster_02 | blue | [443, 122, 500, 179] | vertical | none | stripe_refused:height |
| HOME color model | barrel_low/same | 75 % | L | window_light_cluster_02 | blue | [443, 122, 500, 179] | vertical | none | misplaced |
| HOME color model | barrel_low/same | 75 % | L | window_light_far_02 | blue | [433, 106, 468, 139] | vertical | none | misplaced |
| HOME color model | barrel_low/same | 75 % | R | window_light_close_02 | blue | [308, 141, 392, 231] | vertical | none | misplaced |
| HOME color model | barrel_low/same | 75 % | R | window_light_core_01 | orange | [292, 121, 342, 176] | vertical | none | misplaced |
| HOME color model | barrel_low/same | 75 % | R | window_light_core_03 | orange | [317, 108, 346, 137] | vertical | none | misplaced |
| HOME color model | barrel_side/other | 75 % | L | window_light_cluster_02 | blue | [443, 122, 500, 179] | vertical | none | stripe_refused:height |
| HOME color model | barrel_side/other | 75 % | L | window_light_far_02 | blue | [433, 106, 468, 139] | vertical | none | stripe_refused:top_against_barrel |
| HOME color model | barrel_side/other | 75 % | R | window_light_close_01 | orange | [302, 143, 390, 235] | vertical | none | stripe_refused:outline_unknown |
| HOME color model | frame | 75 % | L | window_light_close_01 | orange | [0, 143, 22, 235] | vertical | none | stripe_refused:outline_unknown |
| HOME color model | frame | 75 % | L | window_light_close_02 | blue | [0, 141, 21, 231] | vertical | none | stripe_refused:outline_unknown |
| HOME color model | frame | 75 % | L | window_light_cluster_02 | blue | [0, 122, 14, 179] | vertical | none | stripe_refused:outline_unknown |
| HOME color model | frame | 75 % | L | window_light_cluster_02 | orange | [0, 119, 11, 170] | vertical | none | stripe_refused:outline_unknown |
| HOME color model | frame | 75 % | L | window_light_core_01 | orange | [0, 121, 12, 176] | vertical | none | stripe_refused:outline_unknown |
| HOME color model | frame | 75 % | L | window_light_core_02 | blue | [0, 120, 13, 175] | vertical | none | stripe_refused:outline_unknown |
| HOME color model | frame | 75 % | L | window_light_core_02 | orange | [0, 120, 12, 173] | vertical | none | stripe_refused:outline_unknown |

