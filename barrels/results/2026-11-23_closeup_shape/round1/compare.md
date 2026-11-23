# Every box that changes against `start`, every close-up / held / edge / top barrel, every box on an empty frame

Train frames of every set, segmented as the report does (HOME leave one scene out). `on_barrel` = the box finds a
labeled barrel under the v2 rule.

## Boxes that appear or disappear

| arm | set | frame | what | box | source | on a barrel |
|---|---|---|---|---|---|---|
| stripe | 4A8B_overheaddim_palewood | 4A8B_overheaddim_palewood_close_01 | added | 292 241 568 477 | det1 | yes |
| shape | 4A8B_overheaddim_palewood | 4A8B_overheaddim_palewood_close_01 | added | 292 241 568 477 | det1 | yes |
| side | 4A8B_window_abpwhite | 4A8B_window_abpwhite_occlx_15 | removed | 465 286 640 480 | det1 | no |
| shape | 4A8B_window_abpwhite | 4A8B_window_abpwhite_occlx_15 | removed | 465 286 640 480 | det1 | no |

## Close-up / held / edge / top barrels (and any labeled barrel at the frame bottom): found (1) or not (0)

| set | frame | color | label box | flags | start | side | stripe | shape |
|---|---|---|---|---|---|---|---|---|
| HOME | 4A8B_window_light_close_01 | orange | 302 143 390 235 |  | 1 | 1 | 1 | 1 |
| HOME | 4A8B_window_light_close_02 | blue | 308 141 392 231 |  | 1 | 1 | 1 | 1 |
| HOME | 4A8B_window_light_edge_01 | blue | 0 133 34 198 | truncated | 1 | 1 | 1 | 1 |
| HOME | 4A8B_window_light_top_01 | orange | 163 259 452 480 | bottom_estimated no_stripe truncated | 1 | 1 | 1 | 1 |
| HOME | 4A8B_window_light_topstripe_01 | orange | 173 240 426 480 | bottom_estimated truncated | 1 | 1 | 1 | 1 |
| CAMPUS | 4A8B_campus_light_close_01 | orange | 252 182 400 357 |  | 1 | 1 | 1 | 1 |
| CAMPUS | 4A8B_campus_light_edge_01 | orange | 602 143 638 228 |  | 1 | 1 | 1 | 1 |
| CAMPUS | 4A8B_campus_light_held_01 | blue | 97 332 512 479 |  | 1 | 1 | 1 | 1 |
| CAMPUS | 4A8B_campus_light_top_01 | orange | 160 280 493 478 |  | 1 | 1 | 1 | 1 |
| CAMPUS | 4A8B_campus_light_topstripe_01 | orange | 221 238 468 477 |  | 1 | 1 | 1 | 1 |
| 4A8B_both_abpgray | 4A8B_both_abpgray_close_01 | orange | 189 250 467 480 | truncated | 1 | 1 | 1 | 1 |
| 4A8B_both_abpgray | 4A8B_both_abpgray_edge_01 | orange | 291 127 356 197 |  | 0 | 0 | 0 | 0 |
| 4A8B_both_abpgray | 4A8B_both_abpgray_edge_01 | blue | 588 150 640 260 | truncated | 1 | 1 | 1 | 1 |
| 4A8B_both_abpgray | 4A8B_both_abpgray_held_01 | blue | 97 330 514 480 | held no_stripe truncated | 1 | 1 | 1 | 1 |
| 4A8B_lampcool1_wood | 4A8B_lampcool1_wood_close_01 | blue | 109 239 358 480 | truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampcool1_wood | 4A8B_lampcool1_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampcool3_wood | 4A8B_lampcool3_wood_close_01 | blue | 109 239 358 480 | truncated | 1 | 1 | 1 | 1 |
| 4A8B_lampcool3_wood | 4A8B_lampcool3_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampcool6_ottoman | 4A8B_lampcool6_ottoman_close_01 | orange | 218 232 470 480 | truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampcool6_ottoman | 4A8B_lampcool6_ottoman_edge_01 | blue | 0 141 43 229 | truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampcool6_ottoman | 4A8B_lampcool6_ottoman_edge_01 | orange | 267 139 351 231 |  | 0 | 0 | 0 | 0 |
| 4A8B_lampcool6_wood | 4A8B_lampcool6_wood_close_01 | blue | 109 239 358 480 | truncated | 1 | 1 | 1 | 1 |
| 4A8B_lampcool6_wood | 4A8B_lampcool6_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampmid1_wood | 4A8B_lampmid1_wood_close_01 | blue | 109 239 358 480 | truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampmid1_wood | 4A8B_lampmid1_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampmid3_ottoman | 4A8B_lampmid3_ottoman_close_01 | orange | 218 232 470 480 | truncated | 1 | 1 | 1 | 1 |
| 4A8B_lampmid3_ottoman | 4A8B_lampmid3_ottoman_edge_01 | blue | 0 141 43 229 | truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampmid3_ottoman | 4A8B_lampmid3_ottoman_edge_01 | orange | 267 139 351 231 |  | 0 | 0 | 0 | 0 |
| 4A8B_lampmid3_wood | 4A8B_lampmid3_wood_close_01 | blue | 109 239 358 480 | truncated | 1 | 1 | 1 | 1 |
| 4A8B_lampmid3_wood | 4A8B_lampmid3_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampmid6_ottoman | 4A8B_lampmid6_ottoman_close_01 | orange | 218 232 470 480 | truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampmid6_ottoman | 4A8B_lampmid6_ottoman_edge_01 | blue | 0 141 43 229 | truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampmid6_ottoman | 4A8B_lampmid6_ottoman_edge_01 | orange | 267 139 351 231 |  | 1 | 1 | 1 | 1 |
| 4A8B_lampmid6_wood | 4A8B_lampmid6_wood_close_01 | blue | 109 239 358 480 | truncated | 1 | 1 | 1 | 1 |
| 4A8B_lampmid6_wood | 4A8B_lampmid6_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampwarm1_wood | 4A8B_lampwarm1_wood_close_01 | blue | 109 239 358 480 | truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampwarm1_wood | 4A8B_lampwarm1_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampwarm3_wood | 4A8B_lampwarm3_wood_close_01 | blue | 109 239 358 480 | truncated | 1 | 1 | 1 | 1 |
| 4A8B_lampwarm3_wood | 4A8B_lampwarm3_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampwarm6_ottoman | 4A8B_lampwarm6_ottoman_close_01 | orange | 218 232 470 480 | truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampwarm6_ottoman | 4A8B_lampwarm6_ottoman_edge_01 | blue | 0 141 43 229 | truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampwarm6_ottoman | 4A8B_lampwarm6_ottoman_edge_01 | orange | 267 139 351 231 |  | 0 | 0 | 0 | 0 |
| 4A8B_lampwarm6_wood | 4A8B_lampwarm6_wood_close_01 | blue | 109 239 358 480 | truncated | 0 | 0 | 0 | 0 |
| 4A8B_lampwarm6_wood | 4A8B_lampwarm6_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0 | 0 | 0 | 0 |
| 4A8B_overheaddim_palewood | 4A8B_overheaddim_palewood_close_01 | orange | 291 243 566 480 | truncated | 0 | 0 | 1 | 1 |
| 4A8B_overheaddim_palewood | 4A8B_overheaddim_palewood_edge_01 | blue | 0 131 35 199 | truncated | 0 | 0 | 0 | 0 |
| 4A8B_overheaddim_palewood | 4A8B_overheaddim_palewood_edge_01 | orange | 313 125 375 191 |  | 1 | 1 | 1 | 1 |
| 4A8B_window_black | 4A8B_window_black_close_02 | orange | 0 132 51 207 | truncated | 0 | 0 | 0 | 0 |
| 4A8B_window_black | 4A8B_window_black_close_02 | blue | 5 127 74 186 | occluded | 0 | 0 | 0 | 0 |
| 4A8B_window_black | 4A8B_window_black_close_02 | orange | 154 245 426 480 | truncated | 1 | 1 | 1 | 1 |
| 4A8B_window_black | 4A8B_window_black_held_01 | orange | 0 132 48 208 | truncated | 0 | 0 | 0 | 0 |
| 4A8B_window_black | 4A8B_window_black_held_01 | blue | 3 127 73 189 | occluded | 0 | 0 | 0 | 0 |
| 4A8B_window_black | 4A8B_window_black_held_01 | orange | 90 327 521 480 | held truncated | 1 | 1 | 1 | 1 |
| DAVE* | DAVE_office_speckle_snap_06 | orange | 133 341 543 480 | truncated | 1 | 1 | 1 | 1 |
| DAVE* | DAVE_office_speckle_snap_07 | orange | 133 341 543 480 | truncated | 1 | 1 | 1 | 1 |
| DAVE* | DAVE_office_speckle_snap_08 | orange | 54 266 354 479 |  | 1 | 1 | 1 | 1 |
| DAVE* | DAVE_office_speckle_snap_08 | blue | 373 287 640 480 | truncated | 1 | 1 | 1 | 1 |
| DAVE* | DAVE_office_speckle_snap_09 | orange | 7 271 325 479 |  | 1 | 1 | 1 | 1 |
| DAVE* | DAVE_office_speckle_snap_09 | blue | 335 248 605 479 |  | 1 | 1 | 1 | 1 |
| DAVE* | DAVE_office_speckle_snap_10 | blue | 259 331 639 479 |  | 1 | 1 | 1 | 1 |
| DAVE* | DAVE_office_speckle_snap_11 | blue | 0 333 387 478 | truncated | 1 | 1 | 1 | 1 |

| arm | found of 61 |
|---|---|
| start | 31 |
| side | 31 |
| stripe | 32 |
| shape | 32 |

## Boxes on empty frames

| arm | set | frame | boxes |
|---|---|---|---|
| start | 4A8B_window_abpwhite | 4A8B_window_abpwhite_occlx_15 | (465, 286, 640, 480) |
| stripe | 4A8B_window_abpwhite | 4A8B_window_abpwhite_occlx_15 | (465, 286, 640, 480) |
