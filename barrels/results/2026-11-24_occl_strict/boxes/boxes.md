# Every box on every train frame, arm `start`

kind: hit = v2 match; loose = same color IoU >= 0.5, bottom off; part = same color IoU 0.1-0.5; wrongcolor = on a
labeled barrel of the other color; false = no labeled barrel there. knockout = the creating switches whose being off
alone removes the box.

## Totals per set

| set | boxes | hit | loose | part | wrongcolor | false |
|---|---|---|---|---|---|---|
| HOME | 28 | 28 | 0 | 0 | 0 | 0 |
| CAMPUS | 35 | 35 | 0 | 0 | 0 | 0 |
| 4A8B_both_abpgray | 12 | 10 | 1 | 0 | 1 | 0 |
| 4A8B_lampcool3_wood (extreme) | 2 | 2 | 0 | 0 | 0 | 0 |
| 4A8B_lampcool6_bathtile | 13 | 13 | 0 | 0 | 0 | 0 |
| 4A8B_lampcool6_glass | 15 | 15 | 0 | 0 | 0 | 0 |
| 4A8B_lampcool6_ottoman | 3 | 3 | 0 | 0 | 0 | 0 |
| 4A8B_lampcool6_wood (extreme) | 6 | 2 | 0 | 3 | 1 | 0 |
| 4A8B_lampmid3_bathtile | 1 | 1 | 0 | 0 | 0 | 0 |
| 4A8B_lampmid3_glass | 17 | 15 | 0 | 0 | 0 | 2 |
| 4A8B_lampmid3_ottoman | 2 | 1 | 1 | 0 | 0 | 0 |
| 4A8B_lampmid3_wood (extreme) | 2 | 1 | 0 | 0 | 1 | 0 |
| 4A8B_lampmid6_bathtile | 1 | 1 | 0 | 0 | 0 | 0 |
| 4A8B_lampmid6_glass | 17 | 15 | 0 | 1 | 0 | 1 |
| 4A8B_lampmid6_ottoman | 6 | 6 | 0 | 0 | 0 | 0 |
| 4A8B_lampmid6_wood (extreme) | 1 | 1 | 0 | 0 | 0 | 0 |
| 4A8B_lampwarm3_wood (extreme) | 1 | 1 | 0 | 0 | 0 | 0 |
| 4A8B_lampwarm6_bathtile | 1 | 1 | 0 | 0 | 0 | 0 |
| 4A8B_lampwarm6_glass | 16 | 15 | 0 | 1 | 0 | 0 |
| 4A8B_lampwarm6_ottoman | 1 | 0 | 0 | 1 | 0 | 0 |
| 4A8B_lampwarm6_wood (extreme) | 1 | 0 | 0 | 0 | 1 | 0 |
| 4A8B_overheaddim_palewood | 14 | 13 | 0 | 0 | 0 | 1 |
| 4A8B_window_abpwhite | 27 | 26 | 0 | 0 | 0 | 1 |
| 4A8B_window_black (extreme) | 6 | 5 | 1 | 0 | 0 | 0 |
| 4A8B_window_glass | 16 | 14 | 1 | 0 | 0 | 1 |
| DAVE* | 17 | 13 | 1 | 3 | 0 | 0 |

## Every box that is not a hit

| set | frame | color | box | kind | stage | flags | knockout |
|---|---|---|---|---|---|---|---|
| 4A8B_both_abpgray | 4A8B_both_abpgray_clutter_01 | orange | 207 117 244 152 | loose | stripe |  |  |
| 4A8B_both_abpgray | 4A8B_both_abpgray_clutter_01 | blue | 512 113 556 168 | wrongcolor | stripe | occluded top_inferred |  |
| 4A8B_lampcool6_wood | 4A8B_lampcool6_wood_cluster_01 | orange | 220 115 268 163 | wrongcolor | half_stripe | occluded top_inferred | half_stripe |
| 4A8B_lampcool6_wood | 4A8B_lampcool6_wood_occl_02 | orange | 186 131 261 215 | part | stripe | occluded top_inferred | side_hidden |
| 4A8B_lampcool6_wood | 4A8B_lampcool6_wood_occl_04 | orange | 186 141 266 214 | part | stripe | occluded | side_hidden |
| 4A8B_lampcool6_wood | 4A8B_lampcool6_wood_touch_02 | orange | 194 126 269 196 | part | stripe | top_inferred | stripe_join stripe_bridge |
| 4A8B_lampmid3_glass | 4A8B_lampmid3_glass_neg_02 | orange | 556 118 606 172 | false | stripe | bottom_inferred occluded top_inferred | side_hidden |
| 4A8B_lampmid3_glass | 4A8B_lampmid3_glass_occl_02 | orange | 577 117 636 167 | false | stripe | top_inferred | stripe_join stripe_bridge side_hidden |
| 4A8B_lampmid3_ottoman | 4A8B_lampmid3_ottoman_clutter_01 | blue | 95 150 175 229 | loose | half_stripe | bottom_inferred occluded | half_stripe |
| 4A8B_lampmid3_wood | 4A8B_lampmid3_wood_close_01 | orange | 214 231 458 469 | wrongcolor | cap | bottom_inferred occluded | cap_behind |
| 4A8B_lampmid6_glass | 4A8B_lampmid6_glass_clutter_01 | orange | 554 117 604 171 | part | stripe | occluded top_inferred | stripe_wide side_hidden |
| 4A8B_lampmid6_glass | 4A8B_lampmid6_glass_occl_02 | orange | 559 119 610 174 | false | stripe | bottom_inferred occluded top_inferred | stripe_join stripe_bridge |
| 4A8B_lampwarm6_glass | 4A8B_lampwarm6_glass_clutter_01 | orange | 555 117 605 172 | part | stripe | occluded | stripe_wide side_hidden |
| 4A8B_lampwarm6_ottoman | 4A8B_lampwarm6_ottoman_core_01 | orange | 166 248 282 480 | part | piece | bottom_inferred truncated |  |
| 4A8B_lampwarm6_wood | 4A8B_lampwarm6_wood_close_01 | orange | 102 265 512 480 | wrongcolor | piece | truncated |  |
| 4A8B_overheaddim_palewood | 4A8B_overheaddim_palewood_core_01 | orange | 235 273 564 480 | false | piece | bottom_inferred truncated |  |
| 4A8B_window_abpwhite | 4A8B_window_abpwhite_occlx_17 | orange | 161 105 196 143 | false | stripe | occluded top_inferred | side_hidden |
| 4A8B_window_black | 4A8B_window_black_clutter_02 | orange | 539 143 640 235 | loose | stripe | bottom_inferred top_inferred truncated | stripe_join |
| 4A8B_window_glass | 4A8B_window_glass_occl_02 | blue | 268 115 307 168 | loose | stripe | occluded | side_hidden |
| 4A8B_window_glass | 4A8B_window_glass_occlx_16 | blue | 395 107 431 146 | false | stripe | bottom_inferred occluded top_inferred | stripe_join side_hidden |
| DAVE* | DAVE_office_speckle_snap_01 | orange | 392 160 503 272 | loose | cap | bottom_inferred occluded | stripe_join cap_behind cap_same |
| DAVE* | DAVE_office_speckle_snap_02 | orange | 396 168 520 258 | part | cap | bottom_inferred occluded | side_hidden cap_behind cap_same cap_low cap_seen_bottom |
| DAVE* | DAVE_office_speckle_snap_03 | blue | 192 246 357 480 | part | piece | bottom_inferred truncated |  |
| DAVE* | DAVE_office_speckle_snap_04 | orange | 400 240 561 480 | part | piece | bottom_inferred truncated |  |
