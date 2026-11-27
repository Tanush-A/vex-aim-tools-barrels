# Fusion: `F1a` held out, beside F0 (contrast alone) and today

Made by `analysis.py`. Every box is the held-out one (leave one place out). Train frames only.

## 1. Every box not on its barrel, `F1a` (ordinary frames, per frame: 3; F0: 9)

| frame | color | box | kind | F0 draws it | today draws it |
|---|---|---|---|---|---|
| 4A8B_lampmid3_bathtile_core_01 | orange | (218, 104, 256, 145) | second | yes | no |
| 4A8B_lampwarm6_bathtile_core_01 | orange | (465, 104, 495, 134) | wrong_color | yes | no |
| 4A8B_lampwarm6_ottoman_core_01 | orange | (166, 248, 282, 480) | nothing | yes | yes |

F0's boxes not on their barrel that `F1a` does not draw: 6

| frame | color | box | kind |
|---|---|---|---|
| 4A8B_lampmid3_glass_occl_02 | orange | (577, 117, 636, 167) | nothing |
| 4A8B_lampmid6_glass_clutter_01 | orange | (554, 117, 604, 171) | nothing |
| 4A8B_lampwarm6_glass_clutter_01 | orange | (555, 117, 605, 172) | nothing |
| 4A8B_lampwarm6_glass_occl_02 | orange | (566, 101, 595, 133) | nothing |
| 4A8B_lampwarm6_glass_occl_02 | orange | (572, 94, 594, 118) | nothing |
| 4A8B_overheaddim_palewood_core_01 | orange | (235, 273, 564, 480) | nothing |

## 2. Barrels whose state differs from F0 (3)

| frame | # | color | label box | F0 | F1a |  |
|---|---|---|---|---|---|---|
| 4A8B_lampcool3_wood_occl_04 | 0 | orange | (181, 128, 238, 186) | found | missed | report only |
| 4A8B_lampcool6_wood_occl_02 | 0 | orange | (175, 117, 218, 162) | found | missed | report only |
| 4A8B_lampcool6_wood_occl_04 | 0 | orange | (182, 130, 241, 186) | off | missed | report only |

## 3. The extreme conditions (report only; found per frame, boxes not on their barrel in brackets)

| condition | barrels per frame | today | F0 | F1a |
|---|---|---|---|---|
| lampcool3_wood | 21 | 2 (0) | 15 (0) | 14 (0) |
| lampcool6_wood | 21 | 2 (2) | 11 (2) | 10 (1) |
| lampmid3_ottoman | 15 | 1 (0) | 1 (0) | 1 (0) |
| lampmid3_wood | 21 | 1 (1) | 12 (1) | 12 (1) |
| lampmid6_wood | 21 | 1 (0) | 16 (1) | 16 (1) |
| lampwarm3_wood | 21 | 1 (0) | 12 (0) | 12 (0) |
| lampwarm6_wood | 21 | 0 (1) | 13 (2) | 13 (2) |
| window_black | 26 | 5 (0) | 5 (0) | 5 (0) |
| **all extreme** | 167 | 13 (4) | 85 (6) | 83 (5) |

| extreme frames by place | placements (per frame) | today | F0 | F1a |
|---|---|---|---|---|
| home_wooddesk | 21 (126) | 1.2 (7); 4 off | 13.2 (79); 6 off | 12.8 (77); 5 off |
| home_ottoman | 15 (15) | 1.0 (1); 0 off | 1.0 (1); 0 off | 1.0 (1); 0 off |
| home_black | 26 (26) | 5.0 (5); 0 off | 5.0 (5); 0 off | 5.0 (5); 0 off |

## 4. Against the vendor (the six places with vendor files; found per placement (per frame); boxes not on their barrel per arrangement)

Train frames: our methods were shaped on them; the vendor's was not.

| place | placements (per frame) | today | F0 | F1a | vendor |
|---|---|---|---|---|---|
| abp_gray | 16 (16) | 10.0 (10); 0.00 | 15.0 (15); 0.00 | 15.0 (15); 0.00 | 16.0 (16); 0.00 |
| home_bathtile | 15 (60) | 4.0 (16); 0.00 | 13.5 (54); 0.50 | 13.5 (54); 0.50 | 7.0 (28); 0.00 |
| home_glass | 15 (75) | 14.8 (74); 0.60 | 14.8 (74); 1.00 | 14.8 (74); 0.00 | 12.0 (60); 2.00 |
| home_ottoman | 15 (45) | 3.0 (9); 0.33 | 10.0 (30); 0.33 | 10.0 (30); 0.33 | 12.3 (37); 0.00 |
| uc_palewood | 15 (15) | 13.0 (13); 1.00 | 13.0 (13); 1.00 | 13.0 (13); 0.00 | 12.0 (12); 0.00 |
| abp_white | 32 (32) | 26.0 (26); 0.00 | 26.0 (26); 0.00 | 26.0 (26); 0.00 | 24.0 (24); 1.00 |
| **six places** | 108 (243) | 70.8 (148); 1.93 | 92.3 (212); 2.83 | 92.3 (212); 0.83 | 83.3 (177); 3.00 |

