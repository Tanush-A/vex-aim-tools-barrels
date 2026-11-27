# Addendum 3: the stage-11 variants on everything

Harness: 'none' reproduces before.json on every input: True.

## The proof harness (5435 masks): real barrels lost / boxes not on a barrel removed, against no stage 11

| variant | damage | hand | pool | real | real_dilate | real_erode | scene | all |
|---|---|---|---|---|---|---|---|---|
| none | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | **0** / 0 |
| V0_adopted | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 2 | **1** / 2 |
| V1_fusion_mild | 20 / 0 | 0 / 0 | 0 / 0 | 3 / 5 | 1 / 5 | 0 / 1 | 30 / 7 | **54** / 18 |
| V2_row_label_excl | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 4 | 1 / 5 | 0 / 0 | 2 / 0 | **5** / 9 |
| V3_col_label_125_excl | 0 / 7 | 0 / 0 | 0 / 0 | 0 / 2 | 0 / 2 | 0 / 1 | 0 / 1 | **0** / 13 |
| V4_raw_speckle_025 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 2 | **1** / 2 |
| V5_V2_plus_V4 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 4 | 1 / 5 | 0 / 0 | 2 / 0 | **5** / 9 |

## The train frames: each color step with the variant against itself without (ordinary judged; extreme report only)

| color step | variant | verdict | found, placements | gained / lost (ordinary) | boxes not on their barrel (per frame) | extreme: lost | cluttered empty |
|---|---|---|---|---|---|---|---|
| fixed | V0_adopted | NO CLEAR DIFFERENCE | 133.80 → 133.80 | 0 / 0 | 1.93 → 1.93 (5 → 5) | 0 | 0.00 → 0.00 |
| fixed | V1_fusion_mild | PASS | 133.80 → 133.80 | 0 / 0 | 1.93 → 0.33 (5 → 1) | 2 | 0.00 → 0.00 |
| fixed | V2_row_label_excl | NO CLEAR DIFFERENCE | 133.80 → 133.80 | 0 / 0 | 1.93 → 1.33 (5 → 2) | 1 | 0.00 → 0.00 |
| fixed | V3_col_label_125_excl | NO CLEAR DIFFERENCE | 133.80 → 133.80 | 0 / 0 | 1.93 → 1.73 (5 → 4) | 0 | 0.00 → 0.00 |
| fixed | V4_raw_speckle_025 | NO CLEAR DIFFERENCE | 133.80 → 133.80 | 0 / 0 | 1.93 → 1.93 (5 → 5) | 0 | 0.00 → 0.00 |
| fixed | V5_V2_plus_V4 | NO CLEAR DIFFERENCE | 133.80 → 133.80 | 0 / 0 | 1.93 → 1.33 (5 → 2) | 1 | 0.00 → 0.00 |
| contrast | V0_adopted | NO CLEAR DIFFERENCE | 155.30 → 155.30 | 0 / 0 | 2.83 → 2.63 (9 → 8) | 0 | 0.00 → 0.00 |
| contrast | V1_fusion_mild | PASS | 155.30 → 155.30 | 0 / 0 | 2.83 → 1.43 (9 → 6) | 2 | 0.00 → 0.00 |
| contrast | V2_row_label_excl | NO CLEAR DIFFERENCE | 155.30 → 155.30 | 0 / 0 | 2.83 → 2.63 (9 → 8) | 1 | 0.00 → 0.00 |
| contrast | V3_col_label_125_excl | NO CLEAR DIFFERENCE | 155.30 → 155.30 | 0 / 0 | 2.83 → 2.43 (9 → 7) | 0 | 0.00 → 0.00 |
| contrast | V4_raw_speckle_025 | NO CLEAR DIFFERENCE | 155.30 → 155.30 | 0 / 0 | 2.83 → 2.63 (9 → 8) | 0 | 0.00 → 0.00 |
| contrast | V5_V2_plus_V4 | NO CLEAR DIFFERENCE | 155.30 → 155.30 | 0 / 0 | 2.83 → 2.63 (9 → 8) | 1 | 0.00 → 0.00 |
| B4 | V0_adopted | NO CLEAR DIFFERENCE | 145.72 → 145.72 | 0 / 0 | 6.68 → 6.18 (24 → 22) | 0 | 1.25 → 0.75 |
| B4 | V1_fusion_mild | PASS | 145.72 → 145.72 | 0 / 0 | 6.68 → 2.83 (24 → 11) | 2 | 1.25 → 0.75 |
| B4 | V2_row_label_excl | PASS | 145.72 → 145.72 | 0 / 0 | 6.68 → 5.33 (24 → 18) | 1 | 1.25 → 0.75 |
| B4 | V3_col_label_125_excl | NO CLEAR DIFFERENCE | 145.72 → 145.72 | 0 / 0 | 6.68 → 5.73 (24 → 20) | 0 | 1.25 → 0.50 |
| B4 | V4_raw_speckle_025 | PASS | 145.72 → 145.72 | 0 / 0 | 6.68 → 4.93 (24 → 17) | 0 | 1.25 → 0.75 |
| B4 | V5_V2_plus_V4 | PASS | 145.72 → 145.72 | 0 / 0 | 6.68 → 4.33 (24 → 14) | 1 | 1.25 → 0.75 |
| D0.20 | V0_adopted | NO CLEAR DIFFERENCE | 143.80 → 143.80 | 0 / 0 | 3.93 → 3.43 (13 → 11) | 0 | 0.75 → 0.25 |
| D0.20 | V1_fusion_mild | PASS | 143.80 → 143.80 | 0 / 0 | 3.93 → 1.58 (13 → 6) | 2 | 0.75 → 0.25 |
| D0.20 | V2_row_label_excl | PASS | 143.80 → 143.80 | 0 / 0 | 3.93 → 2.83 (13 → 8) | 1 | 0.75 → 0.25 |
| D0.20 | V3_col_label_125_excl | NO CLEAR DIFFERENCE | 143.80 → 143.80 | 0 / 0 | 3.93 → 3.23 (13 → 10) | 0 | 0.75 → 0.25 |
| D0.20 | V4_raw_speckle_025 | NO CLEAR DIFFERENCE | 143.80 → 143.80 | 0 / 0 | 3.93 → 3.18 (13 → 10) | 0 | 0.75 → 0.25 |
| D0.20 | V5_V2_plus_V4 | PASS | 143.80 → 143.80 | 0 / 0 | 3.93 → 2.58 (13 → 7) | 1 | 0.75 → 0.25 |

## Every box not on its barrel drawn with no stage 11 (ordinary frames): which variants remove it

| color step | frame | state | color | box | V0_adopted | V1_fusion_mild | V2_row_label_excl | V3_col_label_125_excl | V4_raw_speckle_025 | V5_V2_plus_V4 |
|---|---|---|---|---|---|---|---|---|---|---|
| fixed | lampmid3_glass_occl_02 | nothing | orange | 577 117 636 167 | no | **yes** | **yes** | **yes** | no | **yes** |
| fixed | lampmid6_glass_clutter_01 | nothing | orange | 554 117 604 171 | no | **yes** | **yes** | no | no | **yes** |
| fixed | lampwarm6_glass_clutter_01 | nothing | orange | 555 117 605 172 | no | **yes** | **yes** | no | no | **yes** |
| fixed | lampwarm6_ottoman_core_01 | nothing | orange | 166 248 282 480 | no | no | no | no | no | no |
| fixed | overheaddim_palewood_core_01 | nothing | orange | 235 273 564 480 | no | **yes** | no | no | no | no |
| contrast | lampmid3_bathtile_core_01 | second | orange | 218 104 256 145 | no | no | no | no | no | no |
| contrast | lampmid3_glass_occl_02 | nothing | orange | 577 117 636 167 | no | **yes** | **yes** | **yes** | no | **yes** |
| contrast | lampmid6_glass_clutter_01 | nothing | orange | 554 117 604 171 | no | **yes** | **yes** | no | no | **yes** |
| contrast | lampwarm6_bathtile_core_01 | wrong_color | orange | 465 104 495 134 | no | no | no | no | no | no |
| contrast | lampwarm6_glass_clutter_01 | nothing | orange | 555 117 605 172 | no | no | no | no | no | no |
| contrast | lampwarm6_glass_occl_02 | nothing | orange | 566 101 595 133 | no | **yes** | no | no | no | no |
| contrast | lampwarm6_glass_occl_02 | nothing | orange | 572 94 594 118 | **yes** | **yes** | **yes** | **yes** | **yes** | **yes** |
| contrast | lampwarm6_ottoman_core_01 | nothing | orange | 166 248 282 480 | no | no | no | no | no | no |
| contrast | overheaddim_palewood_core_01 | nothing | orange | 235 273 564 480 | no | **yes** | no | no | no | no |
| B4 | lampmid3_bathtile_clutter_01 | nothing | orange | 516 102 551 134 | no | **yes** | no | no | no | no |
| B4 | lampmid3_bathtile_clutter_01 | nothing | orange | 529 100 557 127 | no | **yes** | no | no | no | no |
| B4 | lampmid3_bathtile_core_01 | second | orange | 218 104 256 145 | no | no | no | no | no | no |
| B4 | lampmid3_bathtile_neg_02 | nothing | blue | 529 105 569 142 | **yes** | **yes** | **yes** | **yes** | **yes** | **yes** |
| B4 | lampmid3_bathtile_occl_02 | nothing | orange | 529 113 574 157 | no | no | no | no | no | no |
| B4 | lampmid3_glass_occl_02 | nothing | orange | 577 117 636 167 | no | **yes** | **yes** | **yes** | no | **yes** |
| B4 | lampmid6_bathtile_neg_02 | nothing | orange | 527 117 578 160 | no | no | no | **yes** | no | no |
| B4 | lampmid6_bathtile_occl_02 | nothing | orange | 369 102 399 132 | no | no | no | no | no | no |
| B4 | lampmid6_bathtile_occl_02 | nothing | orange | 526 112 579 160 | no | no | no | no | no | no |
| B4 | lampmid6_glass_clutter_01 | nothing | orange | 554 117 604 171 | no | **yes** | **yes** | no | no | **yes** |
| B4 | lampwarm6_bathtile_clutter_01 | wrong_color | orange | 294 117 340 166 | no | no | no | no | no | no |
| B4 | lampwarm6_bathtile_core_01 | nothing | orange | 465 101 495 134 | no | no | no | no | no | no |
| B4 | lampwarm6_bathtile_neg_02 | nothing | blue | 305 95 332 121 | no | no | no | no | no | no |
| B4 | lampwarm6_bathtile_neg_02 | nothing | orange | 527 111 581 160 | no | no | no | no | no | no |
| B4 | lampwarm6_bathtile_neg_02 | nothing | orange | 544 100 576 135 | **yes** | **yes** | **yes** | **yes** | **yes** | **yes** |
| B4 | lampwarm6_bathtile_occl_02 | nothing | blue | 165 91 182 107 | no | **yes** | no | no | **yes** | **yes** |
| B4 | lampwarm6_bathtile_occl_02 | nothing | orange | 172 95 195 118 | no | **yes** | no | no | **yes** | **yes** |
| B4 | lampwarm6_bathtile_occl_02 | nothing | orange | 298 105 327 133 | no | **yes** | no | no | **yes** | **yes** |
| B4 | lampwarm6_bathtile_occl_02 | nothing | blue | 299 96 321 121 | no | **yes** | no | no | **yes** | **yes** |
| B4 | lampwarm6_bathtile_occl_02 | nothing | orange | 310 98 336 126 | no | **yes** | **yes** | no | **yes** | **yes** |
| B4 | lampwarm6_bathtile_occl_02 | nothing | orange | 527 111 580 161 | no | no | no | no | no | no |
| B4 | lampwarm6_glass_clutter_01 | nothing | orange | 555 117 605 172 | no | **yes** | **yes** | no | no | **yes** |
| B4 | lampwarm6_ottoman_touch_01 | wrong_color | blue | 298 131 357 184 | no | no | no | no | no | no |
| B4 | overheaddim_palewood_core_01 | nothing | orange | 235 273 564 480 | no | **yes** | no | no | no | no |
| D0.20 | lampmid3_bathtile_core_01 | second | orange | 218 104 256 145 | no | no | no | no | no | no |
| D0.20 | lampmid3_glass_occl_02 | nothing | orange | 577 117 636 167 | no | **yes** | **yes** | **yes** | no | **yes** |
| D0.20 | lampmid6_bathtile_neg_02 | nothing | orange | 529 117 578 158 | **yes** | **yes** | **yes** | **yes** | **yes** | **yes** |
| D0.20 | lampmid6_bathtile_occl_02 | nothing | orange | 369 102 399 132 | no | no | no | no | no | no |
| D0.20 | lampmid6_glass_clutter_01 | nothing | orange | 554 117 604 171 | no | **yes** | **yes** | no | no | **yes** |
| D0.20 | lampwarm6_bathtile_clutter_01 | wrong_color | orange | 294 117 340 166 | no | no | no | no | no | no |
| D0.20 | lampwarm6_bathtile_neg_02 | nothing | orange | 528 111 571 160 | no | no | no | no | no | no |
| D0.20 | lampwarm6_bathtile_neg_02 | nothing | orange | 544 100 576 135 | **yes** | **yes** | **yes** | **yes** | **yes** | **yes** |
| D0.20 | lampwarm6_bathtile_occl_02 | nothing | blue | 301 96 320 121 | no | **yes** | no | no | **yes** | **yes** |
| D0.20 | lampwarm6_bathtile_occl_02 | nothing | orange | 531 111 577 163 | no | no | no | no | no | no |
| D0.20 | lampwarm6_glass_clutter_01 | nothing | orange | 555 117 605 172 | no | **yes** | **yes** | no | no | **yes** |
| D0.20 | lampwarm6_ottoman_core_01 | nothing | orange | 166 248 282 480 | no | no | no | no | no | no |
| D0.20 | overheaddim_palewood_core_01 | nothing | orange | 235 273 564 480 | no | **yes** | no | no | no | no |

Harness losses, by variant (first 30):

- V0_adopted: 1: scene/CAMPUS color model/01438/barrel_side/other/0.75/L #1
- V1_fusion_mild: 54: damage/heavy/0/CAMPUS color model/4A8B_campus_light_core_01 #1; damage/heavy/0/CAMPUS color model/4A8B_campus_light_core_01 #4; damage/heavy/0/HOME hand masks/4A8B_window_light_occl_02 #1; damage/heavy/1/CAMPUS color model/4A8B_campus_light_core_01 #1; damage/heavy/1/HOME hand masks/4A8B_window_light_occl_01 #1; damage/heavy/2/CAMPUS color model/4A8B_campus_light_close_01 #1; damage/heavy/2/CAMPUS color model/4A8B_campus_light_core_01 #1; damage/heavy/2/CAMPUS color model/4A8B_campus_light_plain_01 #1; damage/light/0/HOME hand masks/4A8B_window_light_cluster_01 #1; damage/light/0/HOME hand masks/4A8B_window_light_cluster_01 #3; damage/light/1/HOME hand masks/4A8B_window_light_cluster_01 #1; damage/light/2/HOME hand masks/4A8B_window_light_cluster_01 #3; damage/medium/1/CAMPUS color model/4A8B_campus_light_clutter_02 #3; damage/medium/1/CAMPUS color model/4A8B_campus_light_room_01 #1; damage/medium/1/CAMPUS color model/4A8B_campus_light_touch_02 #1; damage/white tables, bad day/0/HOME hand masks/4A8B_window_light_cluster_01 #3; damage/white tables, bad day/1/HOME hand masks/4A8B_window_light_cluster_01 #1; damage/white tables, typical/0/HOME hand masks/4A8B_window_light_cluster_01 #3; damage/white tables, typical/1/HOME hand masks/4A8B_window_light_cluster_01 #3; damage/white tables, typical/2/HOME hand masks/4A8B_window_light_cluster_01 #3; real/4A8B_lampcool3_wood_occl_04 #1; real/4A8B_lampcool6_wood_occl_02 #1; real/4A8B_lampcool6_wood_occl_04 #1; real_dilate/4A8B_lampcool3_wood_occl_04 #1; scene/CAMPUS color model/00309/frame/0.5/R #1; scene/CAMPUS color model/00313/edge/0.25/R #1; scene/CAMPUS color model/00320/slant/0.25/R+ #1; scene/CAMPUS color model/00321/slant/0.25/R- #1; scene/CAMPUS color model/00343/barrel_side/other/0.25/R #1; scene/CAMPUS color model/00351/barrel_low/other/0.5/R #1
- V2_row_label_excl: 5: real/4A8B_lampcool3_wood_occl_04 #1; real/4A8B_lampcool6_wood_occl_04 #1; real_dilate/4A8B_lampcool3_wood_occl_04 #1; scene/HOME color model/00287/barrel_side/same/0.5/L #1; scene/HOME color model/00289/barrel_side/same/0.75/L #2
- V3_col_label_125_excl: 0: 
- V4_raw_speckle_025: 1: scene/CAMPUS color model/01438/barrel_side/other/0.75/L #1
- V5_V2_plus_V4: 5: real/4A8B_lampcool3_wood_occl_04 #1; real/4A8B_lampcool6_wood_occl_04 #1; real_dilate/4A8B_lampcool3_wood_occl_04 #1; scene/HOME color model/00287/barrel_side/same/0.5/L #1; scene/HOME color model/00289/barrel_side/same/0.75/L #2
