# The finder at the reference setting (logrb o=8 margin=0.5 share=0.5; no guard, at most 20 candidates a frame)

`python barrels/experiments/2026-11-26_contrast/finder.py`. A measurement at known barrel locations: a barrel counts when a candidate of its color has its stripe point on the barrel's stripe (the middle 70 % of the hand box's columns, rows 0.35 to 0.80 of its height). Clean = upright, whole, in view. Hidden = flagged occluded or truncated. 'On no barrel' = the stripe point is in no hand box.

| condition | class | frames | clean: top 3 | top 5 | top 10 | top 20 | of | missed by the fixed colors, with a candidate | hidden: top 20 | of | predicted box IoU, median | IoU >= 0.5 | on no barrel per frame | empty frames: candidates |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| window_light | ordinary | 16 | 19 | 19 | 19 | 19 | 19 | 0 of 0 | 5 | 8 | 0.884 | 19 | 0.00 | 0, 0 |
| campus_light | ordinary | 21 | 25 | 27 | 27 | 27 | 27 | 0 of 0 | 3 | 3 | 0.862 | 26 | 0.38 | 0, 0, 3, 2 |
| both_abpgray | ordinary | 8 | 9 | 10 | 10 | 10 | 10 | 5 of 5 | 4 | 5 | 0.919 | 10 | 1.38 | 3 |
| lampcool6_bathtile | ordinary | 7 | 10 | 12 | 12 | 12 | 12 | 1 of 1 | 2 | 3 | 0.904 | 12 | 2.00 | 5 |
| lampcool6_glass | ordinary | 7 | 10 | 10 | 10 | 10 | 10 | 0 of 0 | 4 | 5 | 0.917 | 10 | 1.29 | 3 |
| lampcool6_ottoman | ordinary | 7 | 9 | 10 | 10 | 10 | 10 | 7 of 7 | 4 | 5 | 0.762 | 10 | 0.57 | 2 |
| lampmid3_bathtile | ordinary | 7 | 10 | 12 | 12 | 12 | 12 | 12 of 12 | 2 | 3 | 0.873 | 12 | 1.14 | 3 |
| lampmid3_glass | ordinary | 7 | 10 | 10 | 10 | 10 | 10 | 0 of 0 | 4 | 5 | 0.913 | 10 | 1.71 | 4 |
| lampmid6_bathtile | ordinary | 7 | 10 | 12 | 12 | 12 | 12 | 12 of 12 | 2 | 3 | 0.873 | 12 | 1.71 | 4 |
| lampmid6_glass | ordinary | 7 | 10 | 10 | 10 | 10 | 10 | 0 of 0 | 4 | 5 | 0.905 | 10 | 1.29 | 3 |
| lampmid6_ottoman | ordinary | 7 | 9 | 10 | 10 | 10 | 10 | 4 of 4 | 4 | 5 | 0.741 | 10 | 0.29 | 2 |
| lampwarm6_bathtile | ordinary | 7 | 10 | 12 | 12 | 12 | 12 | 12 of 12 | 2 | 3 | 0.896 | 12 | 2.86 | 4 |
| lampwarm6_glass | ordinary | 7 | 10 | 10 | 10 | 10 | 10 | 0 of 0 | 4 | 5 | 0.898 | 10 | 1.43 | 3 |
| lampwarm6_ottoman | ordinary | 7 | 9 | 10 | 10 | 10 | 10 | 10 of 10 | 4 | 5 | 0.701 | 10 | 0.57 | 2 |
| overheaddim_palewood | ordinary | 7 | 9 | 10 | 10 | 10 | 10 | 0 of 0 | 2 | 5 | 0.892 | 10 | 1.29 | 3 |
| window_abpwhite | ordinary | 17 | 17 | 17 | 17 | 17 | 17 | 0 of 0 | 6 | 15 | 0.883 | 17 | 0.59 | 7 |
| window_glass | ordinary | 8 | 10 | 10 | 10 | 10 | 10 | 0 of 0 | 4 | 5 | 0.917 | 10 | 2.00 | 3, 6 |
| lampcool3_wood | extreme | 10 | 12 | 14 | 14 | 14 | 14 | 14 of 14 | 2 | 5 | 0.866 | 14 | 0.30 | 1 |
| lampcool6_wood | extreme | 10 | 12 | 14 | 14 | 14 | 14 | 14 of 14 | 2 | 5 | 0.86 | 14 | 0.60 | 2 |
| lampmid3_ottoman | extreme | 7 | 1 | 1 | 1 | 1 | 10 | 1 of 10 | 0 | 5 | 0.568 | 1 | 0.14 | 1 |
| lampmid3_wood | extreme | 10 | 12 | 14 | 14 | 14 | 14 | 14 of 14 | 2 | 5 | 0.867 | 14 | 0.30 | 1 |
| lampmid6_wood | extreme | 10 | 12 | 14 | 14 | 14 | 14 | 14 of 14 | 2 | 5 | 0.867 | 14 | 0.70 | 2 |
| lampwarm3_wood | extreme | 10 | 12 | 14 | 14 | 14 | 14 | 14 of 14 | 2 | 5 | 0.863 | 14 | 1.30 | 5 |
| lampwarm6_wood | extreme | 10 | 12 | 14 | 14 | 14 | 14 | 14 of 14 | 2 | 5 | 0.864 | 14 | 1.90 | 5 |
| window_black | extreme | 10 | 12 | 13 | 13 | 13 | 14 | 10 of 11 | 4 | 9 | 0.745 | 11 | 0.00 | 0 |
| lampcool1_wood | excluded | 10 | 0 | 0 | 0 | 0 | 14 | 0 of 14 | 0 | 5 |  | 0 | 0.90 | 1 |
| lampmid1_wood | excluded | 10 | 0 | 0 | 0 | 0 | 14 | 0 of 14 | 0 | 5 |  | 0 | 0.90 | 1 |
| lampwarm1_wood | excluded | 10 | 0 | 0 | 0 | 0 | 14 | 0 of 14 | 0 | 5 |  | 0 | 0.90 | 1 |
| **all ordinary** | ordinary | 154 | 196 | 211 | 211 | 211 | 211 | 63 of 63 | 60 | 88 | 0.873 | 210 | 1.03 | 0, 0, 0, 0, 3, 2, 3, 5, 3, 2, 3, 4, 4, 3, 2, 4, 3, 2, 3, 7, 3, 6 |
| **all extreme** | extreme | 77 | 85 | 98 | 98 | 98 | 108 | 95 of 105 | 16 | 44 | 0.861 | 96 | 0.68 | 1, 2, 1, 1, 2, 5, 5, 0 |
| **all excluded** | excluded | 30 | 0 | 0 | 0 | 0 | 42 | 0 of 42 | 0 | 15 |  | 0 | 0.90 | 1, 1, 1 |

## Clean barrels without a candidate on their stripe (top 20)

- lampmid3_ottoman_clutter_01 #1 blue [79, 146, 177, 241] (h 95, bottom 241); fixed colors: off
- lampmid3_ottoman_core_01 #1 blue [77, 133, 155, 208] (h 75, bottom 208); fixed colors: missed
- lampmid3_ottoman_core_01 #2 orange [155, 166, 280, 311] (h 145, bottom 311); fixed colors: missed
- lampmid3_ottoman_core_01 #3 blue [273, 113, 316, 160] (h 47, bottom 160); fixed colors: missed
- lampmid3_ottoman_core_01 #4 orange [413, 126, 479, 190] (h 64, bottom 190); fixed colors: missed
- lampmid3_ottoman_edge_01 #2 orange [267, 139, 351, 231] (h 92, bottom 231); fixed colors: missed
- lampmid3_ottoman_touch_01 #1 blue [198, 129, 262, 198] (h 69, bottom 198); fixed colors: missed
- lampmid3_ottoman_touch_01 #2 blue [262, 129, 325, 198] (h 69, bottom 198); fixed colors: missed
- lampmid3_ottoman_touch_01 #3 orange [324, 128, 389, 199] (h 71, bottom 199); fixed colors: missed
- window_black_clutter_02 #2 orange [246, 108, 276, 140] (h 32, bottom 140); fixed colors: missed
- lampcool1_wood_cluster_01 #1 blue [93, 125, 145, 176] (h 51, bottom 176); fixed colors: missed
- lampcool1_wood_cluster_01 #2 orange [151, 129, 213, 194] (h 65, bottom 194); fixed colors: missed
- lampcool1_wood_cluster_01 #3 blue [218, 125, 271, 182] (h 57, bottom 182); fixed colors: missed
- lampcool1_wood_cluster_01 #4 orange [270, 125, 322, 183] (h 58, bottom 183); fixed colors: missed
- lampcool1_wood_clutter_01 #1 orange [35, 154, 144, 259] (h 105, bottom 259); fixed colors: missed
- lampcool1_wood_clutter_01 #3 blue [377, 111, 410, 146] (h 35, bottom 146); fixed colors: missed
- lampcool1_wood_clutter_01 #4 blue [529, 123, 594, 184] (h 61, bottom 184); fixed colors: missed
- lampcool1_wood_core_01 #2 blue [180, 130, 239, 195] (h 65, bottom 195); fixed colors: missed
- lampcool1_wood_core_01 #3 orange [237, 130, 295, 192] (h 62, bottom 192); fixed colors: missed
- lampcool1_wood_core_01 #4 blue [334, 109, 368, 144] (h 35, bottom 144); fixed colors: missed
- lampcool1_wood_occl_02 #2 blue [182, 148, 267, 244] (h 96, bottom 244); fixed colors: missed
- lampcool1_wood_occl_04 #2 blue [180, 150, 267, 243] (h 93, bottom 243); fixed colors: missed
- lampcool1_wood_touch_02 #1 orange [170, 129, 232, 196] (h 67, bottom 196); fixed colors: missed
- lampcool1_wood_touch_02 #2 orange [230, 129, 289, 194] (h 65, bottom 194); fixed colors: missed
- lampmid1_wood_cluster_01 #1 blue [93, 125, 145, 176] (h 51, bottom 176); fixed colors: missed
- lampmid1_wood_cluster_01 #2 orange [151, 129, 213, 194] (h 65, bottom 194); fixed colors: missed
- lampmid1_wood_cluster_01 #3 blue [218, 125, 271, 182] (h 57, bottom 182); fixed colors: missed
- lampmid1_wood_cluster_01 #4 orange [270, 125, 322, 183] (h 58, bottom 183); fixed colors: missed
- lampmid1_wood_clutter_01 #1 orange [35, 154, 144, 259] (h 105, bottom 259); fixed colors: missed
- lampmid1_wood_clutter_01 #3 blue [377, 111, 410, 146] (h 35, bottom 146); fixed colors: missed
- lampmid1_wood_clutter_01 #4 blue [529, 123, 594, 184] (h 61, bottom 184); fixed colors: missed
- lampmid1_wood_core_01 #2 blue [180, 130, 239, 195] (h 65, bottom 195); fixed colors: missed
- lampmid1_wood_core_01 #3 orange [237, 130, 295, 192] (h 62, bottom 192); fixed colors: missed
- lampmid1_wood_core_01 #4 blue [334, 109, 368, 144] (h 35, bottom 144); fixed colors: missed
- lampmid1_wood_occl_02 #2 blue [182, 148, 267, 244] (h 96, bottom 244); fixed colors: missed
- lampmid1_wood_occl_04 #2 blue [180, 150, 267, 243] (h 93, bottom 243); fixed colors: missed
- lampmid1_wood_touch_02 #1 orange [170, 129, 232, 196] (h 67, bottom 196); fixed colors: missed
- lampmid1_wood_touch_02 #2 orange [230, 129, 289, 194] (h 65, bottom 194); fixed colors: missed
- lampwarm1_wood_cluster_01 #1 blue [93, 125, 145, 176] (h 51, bottom 176); fixed colors: missed
- lampwarm1_wood_cluster_01 #2 orange [151, 129, 213, 194] (h 65, bottom 194); fixed colors: missed
- lampwarm1_wood_cluster_01 #3 blue [218, 125, 271, 182] (h 57, bottom 182); fixed colors: missed
- lampwarm1_wood_cluster_01 #4 orange [270, 125, 322, 183] (h 58, bottom 183); fixed colors: missed
- lampwarm1_wood_clutter_01 #1 orange [35, 154, 144, 259] (h 105, bottom 259); fixed colors: missed
- lampwarm1_wood_clutter_01 #3 blue [377, 111, 410, 146] (h 35, bottom 146); fixed colors: missed
- lampwarm1_wood_clutter_01 #4 blue [529, 123, 594, 184] (h 61, bottom 184); fixed colors: missed
- lampwarm1_wood_core_01 #2 blue [180, 130, 239, 195] (h 65, bottom 195); fixed colors: missed
- lampwarm1_wood_core_01 #3 orange [237, 130, 295, 192] (h 62, bottom 192); fixed colors: missed
- lampwarm1_wood_core_01 #4 blue [334, 109, 368, 144] (h 35, bottom 144); fixed colors: missed
- lampwarm1_wood_occl_02 #2 blue [182, 148, 267, 244] (h 96, bottom 244); fixed colors: missed
- lampwarm1_wood_occl_04 #2 blue [180, 150, 267, 243] (h 93, bottom 243); fixed colors: missed
- lampwarm1_wood_touch_02 #1 orange [170, 129, 232, 196] (h 67, bottom 196); fixed colors: missed
- lampwarm1_wood_touch_02 #2 orange [230, 129, 289, 194] (h 65, bottom 194); fixed colors: missed

## Hidden barrels without a candidate (top 20)

- window_light_cluster_01 #3 orange [361, 117, 400, 163] ['occluded', 'bottom_estimated']; fixed colors: missed
- window_light_occl_01 #2 blue [386, 115, 430, 161] ['occluded', 'bottom_estimated']; fixed colors: found
- window_light_occl_02 #2 orange [395, 114, 441, 158] ['occluded', 'bottom_estimated']; fixed colors: found
- both_abpgray_close_01 #1 orange [189, 250, 467, 480] ['truncated']; fixed colors: found
- lampcool6_bathtile_close_01 #1 orange [122, 242, 395, 480] ['truncated']; fixed colors: found
- lampcool6_glass_close_01 #1 orange [164, 249, 438, 480] ['truncated']; fixed colors: found
- lampcool6_ottoman_close_01 #1 orange [218, 232, 470, 480] ['truncated']; fixed colors: missed
- lampmid3_bathtile_close_01 #1 orange [122, 242, 395, 480] ['truncated']; fixed colors: found
- lampmid3_glass_close_01 #1 orange [164, 249, 438, 480] ['truncated']; fixed colors: found
- lampmid6_bathtile_close_01 #1 orange [122, 242, 395, 480] ['truncated']; fixed colors: found
- lampmid6_glass_close_01 #1 orange [164, 249, 438, 480] ['truncated']; fixed colors: found
- lampmid6_ottoman_close_01 #1 orange [218, 232, 470, 480] ['truncated']; fixed colors: missed
- lampwarm6_bathtile_close_01 #1 orange [122, 242, 395, 480] ['truncated']; fixed colors: found
- lampwarm6_glass_close_01 #1 orange [164, 249, 438, 480] ['truncated']; fixed colors: found
- lampwarm6_ottoman_close_01 #1 orange [218, 232, 470, 480] ['truncated']; fixed colors: missed
- overheaddim_palewood_close_01 #1 orange [291, 243, 566, 480] ['truncated']; fixed colors: found
- overheaddim_palewood_clutter_01 #1 blue [136, 118, 187, 169] ['occluded', 'bottom_estimated']; fixed colors: found
- overheaddim_palewood_edge_01 #1 blue [0, 131, 35, 199] ['truncated']; fixed colors: missed
- window_abpwhite_occlx_02 #1 orange [92, 119, 143, 170] ['occluded']; fixed colors: missed
- window_abpwhite_occlx_03 #1 orange [99, 120, 152, 172] ['occluded']; fixed colors: missed
- window_abpwhite_occlx_04 #1 orange [98, 119, 151, 174] ['occluded']; fixed colors: found
- window_abpwhite_occlx_07 #1 orange [108, 116, 159, 166] ['occluded', 'bottom_estimated']; fixed colors: found
- window_abpwhite_occlx_08 #1 orange [111, 114, 160, 164] ['occluded']; fixed colors: found
- window_abpwhite_occlx_10 #1 orange [99, 118, 148, 168] ['occluded', 'bottom_estimated']; fixed colors: missed
- window_abpwhite_occlx_11 #2 orange [99, 117, 147, 169] ['occluded', 'bottom_estimated']; fixed colors: found
- window_abpwhite_occlx_17 #1 blue [0, 124, 19, 183] ['truncated']; fixed colors: found
- window_abpwhite_occlx_19 #2 orange [232, 121, 288, 181] ['occluded', 'bottom_estimated']; fixed colors: missed
- window_glass_close_01 #1 orange [164, 249, 438, 480] ['truncated']; fixed colors: found

## The named traps: candidates on the cluttered empty frames

- lampmid3_bathtile_neg_02: 3 candidates: orange at (525, 118) share 1.00 strength 1.09; orange at (552, 118) share 1.00 strength 0.78; orange at (388, 104) share 0.53 strength 0.54
- lampmid6_bathtile_neg_02: 4 candidates: orange at (555, 140) share 1.00 strength 0.78; blue at (316, 108) share 0.68 strength 0.57; blue at (248, 160) share 0.64 strength 0.55; blue at (337, 100) share 0.53 strength 0.52
- lampwarm6_bathtile_neg_02: 4 candidates: orange at (555, 139) share 1.00 strength 0.73; blue at (342, 99) share 0.54 strength 0.68; blue at (313, 108) share 0.63 strength 0.61; orange at (600, 107) share 0.84 strength 0.55
- lampwarm6_glass_neg_02: 3 candidates: orange at (618, 119) share 1.00 strength 0.93; blue at (573, 127) share 0.69 strength 0.86; orange at (116, 195) share 0.67 strength 0.70
- lampmid6_glass_neg_02: 3 candidates: orange at (579, 147) share 0.95 strength 0.96; orange at (122, 196) share 0.87 strength 0.88; orange at (624, 119) share 1.00 strength 0.74
