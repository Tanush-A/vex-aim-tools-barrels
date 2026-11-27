# Fusion: `F3` held out, beside F0 (contrast alone) and today

Made by `analysis.py`. Every box is the held-out one (leave one place out). Train frames only.

## 1. Every box not on its barrel, `F3` (ordinary frames, per frame: 5; F0: 9)

| frame | color | box | kind | F0 draws it | today draws it |
|---|---|---|---|---|---|
| 4A8B_lampmid3_bathtile_core_01 | orange | (218, 104, 256, 145) | second | yes | no |
| 4A8B_lampmid6_ottoman_core_01 | blue | (120, 139, 186, 203) | second | **no (new)** | no |
| 4A8B_lampwarm6_bathtile_core_01 | orange | (465, 104, 495, 134) | wrong_color | yes | no |
| 4A8B_lampwarm6_ottoman_core_01 | orange | (166, 248, 282, 480) | nothing | yes | yes |
| 4A8B_overheaddim_palewood_core_01 | orange | (235, 273, 576, 480) | nothing | yes | yes |

F0's boxes not on their barrel that `F3` does not draw: 5

| frame | color | box | kind |
|---|---|---|---|
| 4A8B_lampmid3_glass_occl_02 | orange | (577, 117, 636, 167) | nothing |
| 4A8B_lampmid6_glass_clutter_01 | orange | (554, 117, 604, 171) | nothing |
| 4A8B_lampwarm6_glass_clutter_01 | orange | (555, 117, 605, 172) | nothing |
| 4A8B_lampwarm6_glass_occl_02 | orange | (566, 101, 595, 133) | nothing |
| 4A8B_lampwarm6_glass_occl_02 | orange | (572, 94, 594, 118) | nothing |

## 2. Barrels whose state differs from F0 (37)

| frame | # | color | label box | F0 | F3 |  |
|---|---|---|---|---|---|---|
| 4A8B_lampcool6_ottoman_occl_02 | 0 | orange | (225, 125, 286, 192) | missed | found | judged |
| 4A8B_lampcool6_ottoman_touch_01 | 0 | blue | (198, 129, 262, 198) | missed | found | judged |
| 4A8B_lampmid6_bathtile_edge_01 | 0 | blue | (0, 127, 31, 196) | missed | off | judged |
| 4A8B_lampmid6_bathtile_occl_02 | 0 | orange | (346, 107, 376, 137) | missed | found | judged |
| 4A8B_lampmid6_ottoman_clutter_01 | 3 | orange | (541, 129, 613, 202) | missed | found | judged |
| 4A8B_lampmid6_ottoman_core_01 | 1 | orange | (155, 166, 280, 311) | found | off | judged |
| 4A8B_lampmid6_ottoman_edge_01 | 0 | blue | (0, 141, 43, 229) | found | off | judged |
| 4A8B_lampmid6_ottoman_occl_02 | 0 | orange | (225, 125, 286, 192) | missed | found | judged |
| 4A8B_lampmid6_ottoman_touch_01 | 0 | blue | (198, 129, 262, 198) | missed | found | judged |
| 4A8B_lampwarm6_ottoman_core_01 | 1 | orange | (155, 166, 280, 311) | missed | found | judged |
| 4A8B_lampwarm6_ottoman_touch_01 | 1 | blue | (262, 129, 325, 198) | missed | off | judged |
| 4A8B_window_glass_occl_02 | 0 | blue | (254, 114, 300, 163) | off | found | judged |
| 4A8B_lampcool3_wood_clutter_01 | 2 | blue | (377, 111, 410, 146) | missed | found | report only |
| 4A8B_lampcool3_wood_occl_04 | 0 | orange | (181, 128, 238, 186) | found | missed | report only |
| 4A8B_lampcool3_wood_occl_04 | 1 | blue | (186, 150, 272, 243) | missed | found | report only |
| 4A8B_lampcool6_wood_clutter_01 | 1 | orange | (236, 118, 280, 166) | missed | found | report only |
| 4A8B_lampcool6_wood_occl_02 | 1 | blue | (182, 148, 267, 244) | missed | found | report only |
| 4A8B_lampcool6_wood_occl_04 | 0 | orange | (182, 130, 241, 186) | off | missed | report only |
| 4A8B_lampcool6_wood_occl_04 | 1 | blue | (186, 150, 271, 243) | missed | found | report only |
| 4A8B_lampmid3_wood_clutter_01 | 3 | blue | (529, 123, 594, 184) | missed | found | report only |
| 4A8B_lampmid3_wood_core_01 | 3 | blue | (334, 109, 368, 144) | missed | found | report only |
| 4A8B_lampmid3_wood_touch_02 | 0 | orange | (170, 129, 232, 196) | off | found | report only |
| 4A8B_lampmid6_wood_touch_02 | 0 | orange | (170, 129, 232, 196) | off | found | report only |
| 4A8B_lampwarm3_wood_cluster_01 | 1 | orange | (151, 129, 213, 194) | missed | off | report only |
| 4A8B_lampwarm3_wood_clutter_01 | 2 | blue | (377, 111, 410, 146) | missed | found | report only |
| 4A8B_lampwarm3_wood_clutter_01 | 3 | blue | (529, 123, 594, 184) | missed | found | report only |
| 4A8B_lampwarm3_wood_touch_02 | 1 | orange | (230, 129, 289, 194) | off | found | report only |
| 4A8B_lampwarm6_wood_cluster_01 | 3 | orange | (270, 125, 322, 183) | off | found | report only |
| 4A8B_lampwarm6_wood_occl_02 | 0 | orange | (175, 117, 218, 162) | off | found | report only |
| 4A8B_window_black_close_02 | 0 | orange | (0, 132, 51, 207) | missed | found | report only |
| 4A8B_window_black_cluster_01 | 2 | orange | (350, 128, 418, 199) | missed | found | report only |
| 4A8B_window_black_clutter_02 | 0 | blue | (0, 135, 73, 212) | missed | found | report only |
| 4A8B_window_black_far_01 | 1 | orange | (279, 112, 323, 157) | missed | off | report only |
| 4A8B_window_black_far_01 | 2 | orange | (366, 114, 412, 158) | off | found | report only |
| 4A8B_window_black_far_01 | 3 | blue | (508, 116, 565, 166) | missed | found | report only |
| 4A8B_window_black_held_01 | 0 | orange | (0, 132, 48, 208) | missed | found | report only |
| 4A8B_window_black_touch_02 | 1 | orange | (304, 136, 384, 219) | missed | found | report only |

## 3. The extreme conditions (report only; found per frame, boxes not on their barrel in brackets)

| condition | barrels per frame | today | F0 | F3 |
|---|---|---|---|---|
| lampcool3_wood | 21 | 2 (0) | 15 (0) | 16 (1) |
| lampcool6_wood | 21 | 2 (2) | 11 (2) | 14 (1) |
| lampmid3_ottoman | 15 | 1 (0) | 1 (0) | 1 (0) |
| lampmid3_wood | 21 | 1 (1) | 12 (1) | 15 (1) |
| lampmid6_wood | 21 | 1 (0) | 16 (1) | 17 (2) |
| lampwarm3_wood | 21 | 1 (0) | 12 (0) | 15 (0) |
| lampwarm6_wood | 21 | 0 (1) | 13 (2) | 15 (2) |
| window_black | 26 | 5 (0) | 5 (0) | 12 (0) |
| **all extreme** | 167 | 13 (4) | 85 (6) | 105 (7) |

| extreme frames by place | placements (per frame) | today | F0 | F3 |
|---|---|---|---|---|
| home_wooddesk | 21 (126) | 1.2 (7); 4 off | 13.2 (79); 6 off | 15.3 (92); 7 off |
| home_ottoman | 15 (15) | 1.0 (1); 0 off | 1.0 (1); 0 off | 1.0 (1); 0 off |
| home_black | 26 (26) | 5.0 (5); 0 off | 5.0 (5); 0 off | 12.0 (12); 0 off |

## 4. Against the vendor (the six places with vendor files; found per placement (per frame); boxes not on their barrel per arrangement)

Train frames: our methods were shaped on them; the vendor's was not.

| place | placements (per frame) | today | F0 | F3 | vendor |
|---|---|---|---|---|---|
| abp_gray | 16 (16) | 10.0 (10); 0.00 | 15.0 (15); 0.00 | 15.0 (15); 0.00 | 16.0 (16); 0.00 |
| home_bathtile | 15 (60) | 4.0 (16); 0.00 | 13.5 (54); 0.50 | 13.8 (55); 0.50 | 7.0 (28); 0.00 |
| home_glass | 15 (75) | 14.8 (74); 0.60 | 14.8 (74); 1.00 | 15.0 (75); 0.00 | 12.0 (60); 2.00 |
| home_ottoman | 15 (45) | 3.0 (9); 0.33 | 10.0 (30); 0.33 | 11.3 (34); 0.67 | 12.3 (37); 0.00 |
| uc_palewood | 15 (15) | 13.0 (13); 1.00 | 13.0 (13); 1.00 | 13.0 (13); 1.00 | 12.0 (12); 0.00 |
| abp_white | 32 (32) | 26.0 (26); 0.00 | 26.0 (26); 0.00 | 26.0 (26); 0.00 | 24.0 (24); 1.00 |
| **six places** | 108 (243) | 70.8 (148); 1.93 | 92.3 (212); 2.83 | 94.1 (218); 2.17 | 83.3 (177); 3.00 |

