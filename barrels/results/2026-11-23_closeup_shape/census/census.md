# Census of the frame-bottom step-1 pieces (arm `start`; train frames; all rows in census.csv)

| what the detector does | real barrel | not a barrel | on an empty frame |
|---|---|---|---|
| BOX | 23 | 5 | 1 |
| covered | 1 | 0 | 0 |
| refused | 0 | 905 | 92 |

## Every piece kept or covered (the refused ones fail the size test and are untouched)

| set | stem | color | x0 | y0 | x1 | seen_y1 | status | real | iou | cut_l | cut_r | ratio | st_pred | upper | reach | rule_pass | cost_l | cost_r | fill_box | row_fill | top_flat | body | other |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HOME | 4A8B_window_light_top_01 | orange | 164 | 260 | 449 | 480 | BOX | 1 | 0.98 | 0 | 0 | 0.91 | 499.2 | 220 | 1.0 | 1 | 0.022 | 0.019 | 0.87 | 1.0 | 0.71 | 1.0 | 0.0 |
| HOME | 4A8B_window_light_topstripe_01 | orange | 176 | 242 | 423 | 465 | BOX | 1 | 0.97 | 0 | 0 | 0.92 | 437.4 | 195.4 | 1.14 | 1 | 0.023 | 0.02 | 0.76 | 1.0 | 0.74 | 1.0 | 0.0 |
| CAMPUS | 4A8B_campus_light_held_01 | blue | 98 | 334 | 505 | 480 | BOX | 1 | 0.96 | 0 | 0 | 0.73 | 848.4 | 146 | 1.0 | 1 | 0.03 | 0.033 | 0.73 | 1.0 | 0.67 | 1.0 | 0.0 |
| CAMPUS | 4A8B_campus_light_top_01 | orange | 167 | 281 | 479 | 480 | BOX | 1 | 0.92 | 0 | 0 | 0.84 | 580.7 | 199 | 1.0 | 1 | 0.024 | 0.031 | 0.85 | 1.0 | 0.71 | 1.0 | 0.0 |
| CAMPUS | 4A8B_campus_light_topstripe_01 | orange | 230 | 241 | 463 | 456 | BOX | 1 | 0.92 | 0 | 0 | 0.87 | 434.2 | 193.2 | 1.11 | 1 | 0.034 | 0.031 | 0.75 | 1.0 | 0.78 | 1.0 | 0.0 |
| 4A8B_both_abpgray | 4A8B_both_abpgray_close_01 | orange | 188 | 250 | 466 | 480 | BOX | 1 | 0.99 | 0 | 0 | 0.96 | 464.1 | 214.1 | 1.07 | 1 | 0.02 | 0.02 | 0.84 | 1.0 | 0.7 | 0.99 | 0.0 |
| 4A8B_both_abpgray | 4A8B_both_abpgray_held_01 | blue | 95 | 331 | 518 | 480 | BOX | 1 | 0.98 | 0 | 0 | 0.78 | 830.2 | 149 | 1.0 | 1 | 0.028 | 0.028 | 0.71 | 1.0 | 0.64 | 1.0 | 0.0 |
| 4A8B_lampcool3_wood | 4A8B_lampcool3_wood_close_01 | blue | 118 | 240 | 355 | 434 | BOX | 1 | 0.95 | 0 | 0 | 0.9 | 431.0 | 191.0 | 1.02 | 1 | 0.035 | 0.026 | 0.61 | 0.92 | 0.76 | 0.97 | 0.0 |
| 4A8B_lampcool6_wood | 4A8B_lampcool6_wood_close_01 | blue | 114 | 270 | 355 | 460 | BOX | 1 | 0.84 | 0 | 0 | 0.71 | 536.7 | 210 | 0.9 | 1 | 0.123 | 0.129 | 0.52 | 0.99 | 0.12 | 0.99 | 0.0 |
| 4A8B_lampmid3_ottoman | 4A8B_lampmid3_ottoman_close_01 | orange | 229 | 272 | 428 | 453 | BOX | 1 | 0.66 | 0 | 0 | 0.58 | 544.4 | 208 | 0.87 | 1 | 0.136 | 0.028 | 0.33 | 0.97 | 0.15 | 0.98 | 0.0 |
| 4A8B_lampmid3_wood | 4A8B_lampmid3_wood_close_01 | blue | 121 | 243 | 347 | 390 | BOX | 1 | 0.89 | 0 | 0 | 0.83 | 440.7 | 197.7 | 0.74 | 1 | 0.04 | 0.046 | 0.46 | 0.96 | 0.81 | 0.97 | 0.0 |
| 4A8B_lampmid6_wood | 4A8B_lampmid6_wood_close_01 | blue | 120 | 242 | 352 | 453 | BOX | 1 | 0.92 | 0 | 0 | 0.86 | 437.4 | 195.4 | 1.08 | 1 | 0.038 | 0.03 | 0.52 | 0.8 | 0.77 | 0.97 | 0.0 |
| 4A8B_lampwarm3_wood | 4A8B_lampwarm3_wood_close_01 | blue | 124 | 248 | 338 | 357 | BOX | 1 | 0.83 | 0 | 0 | 0.76 | 457.3 | 209.3 | 0.52 | 1 | 0.05 | 0.081 | 0.3 | 0.84 | 0.85 | 0.96 | 0.0 |
| 4A8B_lampwarm6_ottoman | 4A8B_lampwarm6_ottoman_core_01 | orange | 166 | 248 | 282 | 310 | BOX | 0 | 0.19 | 0 | 0 | 0.41 | 457.3 | 209.3 | 0.3 | 1 | 0.107 | 0.083 | 0.1 | 0.96 | 0.67 | 0.98 | 0.0 |
| 4A8B_lampwarm6_wood | 4A8B_lampwarm6_wood_close_01 | orange | 102 | 265 | 512 | 480 | BOX | 0 | 0.0 | 0 | 0 | 1.26 | 517.6 | 215 | 1.0 | 1 | 0.133 | 0.055 | 0.14 | 0.36 | 0.2 | 0.96 | 0.0 |
| 4A8B_lampwarm6_wood | 4A8B_lampwarm6_wood_close_01 | blue | 124 | 247 | 338 | 387 | covered | 1 | 0.83 | 0 | 0 | 0.76 | 453.9 | 206.9 | 0.68 | 1 | 0.047 | 0.088 | 0.37 | 0.85 | 0.85 | 0.97 | 0.0 |
| 4A8B_overheaddim_palewood | 4A8B_overheaddim_palewood_core_01 | orange | 235 | 273 | 564 | 477 | BOX | 0 | 0.0 | 0 | 0 | 0.94 | 548.4 | 207 | 0.99 | 1 | 0.049 | 0.041 | 0.25 | 0.46 | 0.52 | 0.87 | 0.0 |
| 4A8B_window_abpwhite | 4A8B_window_abpwhite_occlx_15 | orange | 465 | 286 | 640 | 368 | BOX | 0 | 0.0 | 0 | 1 | 0.45 | 601.8 | 194 | 0.42 | 0 | 0.083 | 0.075 | 0.28 | 0.96 | 1.0 | 0.99 | 0.0 |
| 4A8B_window_black | 4A8B_window_black_close_02 | orange | 159 | 258 | 366 | 480 | BOX | 1 | 0.72 | 0 | 0 | 0.67 | 492.0 | 222 | 1.0 | 1 | 0.084 | 0.033 | 0.55 | 0.85 | 0.22 | 0.97 | 0.0 |
| 4A8B_window_black | 4A8B_window_black_held_01 | orange | 102 | 335 | 416 | 480 | BOX | 1 | 0.69 | 0 | 0 | 0.56 | 854.6 | 145 | 1.0 | 1 | 0.037 | 0.046 | 0.35 | 0.56 | 0.64 | 0.96 | 0.0 |
| DAVE* | DAVE_office_speckle_snap_03 | blue | 192 | 246 | 357 | 325 | BOX | 0 | 0.11 | 0 | 0 | 0.59 | 450.6 | 204.6 | 0.39 | 1 | 0.078 | 0.041 | 0.17 | 0.94 | 0.66 | 0.98 | 0.0 |
| DAVE* | DAVE_office_speckle_snap_04 | orange | 400 | 240 | 561 | 291 | BOX | 0 | 0.14 | 0 | 0 | 0.61 | 431.0 | 191.0 | 0.27 | 1 | 0.091 | 0.078 | 0.08 | 0.77 | 1.0 | 0.97 | 0.0 |
| DAVE* | DAVE_office_speckle_snap_06 | orange | 146 | 349 | 542 | 480 | BOX | 1 | 0.91 | 0 | 0 | 0.64 | 946.5 | 131 | 1.0 | 1 | 0.048 | 0.043 | 0.7 | 0.99 | 0.7 | 0.99 | 0.0 |
| DAVE* | DAVE_office_speckle_snap_07 | orange | 136 | 346 | 544 | 480 | BOX | 1 | 0.95 | 0 | 0 | 0.67 | 925.9 | 134 | 1.0 | 1 | 0.041 | 0.04 | 0.72 | 1.0 | 0.7 | 1.0 | 0.0 |
| DAVE* | DAVE_office_speckle_snap_08 | orange | 61 | 273 | 341 | 480 | BOX | 1 | 0.9 | 0 | 0 | 0.8 | 548.4 | 207 | 1.0 | 1 | 0.026 | 0.058 | 0.78 | 0.97 | 0.67 | 0.99 | 0.0 |
| DAVE* | DAVE_office_speckle_snap_08 | blue | 385 | 292 | 640 | 480 | BOX | 1 | 0.93 | 0 | 1 | 0.63 | 628.2 | 188 | 1.0 | 1 | 0.046 | 0.069 | 0.88 | 1.0 | 0.9 | 1.0 | 0.0 |
| DAVE* | DAVE_office_speckle_snap_09 | orange | 15 | 279 | 315 | 480 | BOX | 1 | 0.9 | 0 | 0 | 0.82 | 572.5 | 201 | 1.0 | 1 | 0.063 | 0.046 | 0.71 | 0.94 | 0.54 | 0.99 | 0.0 |
| DAVE* | DAVE_office_speckle_snap_09 | blue | 350 | 253 | 597 | 467 | BOX | 1 | 0.89 | 0 | 0 | 0.84 | 474.4 | 221.4 | 0.97 | 1 | 0.042 | 0.033 | 0.76 | 1.0 | 0.76 | 1.0 | 0.0 |
| DAVE* | DAVE_office_speckle_snap_10 | blue | 270 | 338 | 640 | 480 | BOX | 1 | 0.92 | 0 | 1 | 0.65 | 873.4 | 142 | 1.0 | 1 | 0.055 | 0.046 | 0.78 | 1.0 | 0.74 | 1.0 | 0.0 |
| DAVE* | DAVE_office_speckle_snap_11 | blue | 0 | 339 | 382 | 480 | BOX | 1 | 0.93 | 1 | 0 | 0.66 | 879.8 | 141 | 1.0 | 1 | 0.043 | 0.052 | 0.75 | 1.0 | 0.71 | 1.0 | 0.0 |

## Labeled barrels at the frame bottom (or close / held / no_stripe)

| set | stem | color | box | flags | best_iou | by | box_found |
|---|---|---|---|---|---|---|---|
| HOME | 4A8B_window_light_top_01 | orange | 163 259 452 480 | bottom_estimated no_stripe truncated | 0.98 | det1 | 164 260 449 480 |
| HOME | 4A8B_window_light_topstripe_01 | orange | 173 240 426 480 | bottom_estimated truncated | 0.97 | det1 | 176 242 423 480 |
| CAMPUS | 4A8B_campus_light_held_01 | blue | 97 332 512 479 |  | 0.96 | det1 | 98 334 505 480 |
| CAMPUS | 4A8B_campus_light_top_01 | orange | 160 280 493 478 |  | 0.92 | det1 | 167 281 479 480 |
| 4A8B_both_abpgray | 4A8B_both_abpgray_close_01 | orange | 189 250 467 480 | truncated | 0.99 | det1 | 188 250 466 480 |
| 4A8B_both_abpgray | 4A8B_both_abpgray_held_01 | blue | 97 330 514 480 | held no_stripe truncated | 0.98 | det1 | 95 331 518 480 |
| 4A8B_lampcool1_wood | 4A8B_lampcool1_wood_close_01 | blue | 109 239 358 480 | truncated | 0.0 |  |  |
| 4A8B_lampcool1_wood | 4A8B_lampcool1_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0.0 |  |  |
| 4A8B_lampcool1_wood | 4A8B_lampcool1_wood_occl_04 | orange | 178 128 238 186 | bottom_estimated no_stripe occluded | 0.0 |  |  |
| 4A8B_lampcool3_wood | 4A8B_lampcool3_wood_close_01 | blue | 109 239 358 480 | truncated | 0.95 | det1 | 118 240 355 480 |
| 4A8B_lampcool3_wood | 4A8B_lampcool3_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0.0 |  |  |
| 4A8B_lampcool3_wood | 4A8B_lampcool3_wood_occl_04 | orange | 181 128 238 186 | bottom_estimated no_stripe occluded | 0.85 | barrel | 186 126 239 185 |
| 4A8B_lampcool6_ottoman | 4A8B_lampcool6_ottoman_close_01 | orange | 218 232 470 480 | truncated | 0.0 |  |  |
| 4A8B_lampcool6_wood | 4A8B_lampcool6_wood_close_01 | blue | 109 239 358 480 | truncated | 0.84 | det1 | 114 270 355 480 |
| 4A8B_lampcool6_wood | 4A8B_lampcool6_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0.0 |  |  |
| 4A8B_lampcool6_wood | 4A8B_lampcool6_wood_occl_04 | orange | 182 130 241 186 | bottom_estimated no_stripe occluded | 0.37 | barrel | 186 141 266 214 |
| 4A8B_lampmid1_wood | 4A8B_lampmid1_wood_close_01 | blue | 109 239 358 480 | truncated | 0.0 |  |  |
| 4A8B_lampmid1_wood | 4A8B_lampmid1_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0.0 |  |  |
| 4A8B_lampmid1_wood | 4A8B_lampmid1_wood_occl_04 | orange | 178 128 238 186 | bottom_estimated no_stripe occluded | 0.0 |  |  |
| 4A8B_lampmid3_ottoman | 4A8B_lampmid3_ottoman_close_01 | orange | 218 232 470 480 | truncated | 0.66 | det1 | 229 272 428 480 |
| 4A8B_lampmid3_wood | 4A8B_lampmid3_wood_close_01 | blue | 109 239 358 480 | truncated | 0.89 | det1 | 121 243 347 480 |
| 4A8B_lampmid3_wood | 4A8B_lampmid3_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0.0 |  |  |
| 4A8B_lampmid3_wood | 4A8B_lampmid3_wood_occl_04 | orange | 178 128 238 186 | bottom_estimated no_stripe occluded | 0.0 |  |  |
| 4A8B_lampmid6_ottoman | 4A8B_lampmid6_ottoman_close_01 | orange | 218 232 470 480 | truncated | 0.0 |  |  |
| 4A8B_lampmid6_wood | 4A8B_lampmid6_wood_close_01 | blue | 109 239 358 480 | truncated | 0.92 | det1 | 120 242 352 480 |
| 4A8B_lampmid6_wood | 4A8B_lampmid6_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0.0 |  |  |
| 4A8B_lampmid6_wood | 4A8B_lampmid6_wood_occl_04 | orange | 178 128 238 186 | bottom_estimated no_stripe occluded | 0.0 |  |  |
| 4A8B_lampwarm1_wood | 4A8B_lampwarm1_wood_close_01 | blue | 109 239 358 480 | truncated | 0.0 |  |  |
| 4A8B_lampwarm1_wood | 4A8B_lampwarm1_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0.0 |  |  |
| 4A8B_lampwarm1_wood | 4A8B_lampwarm1_wood_occl_04 | orange | 178 128 238 186 | bottom_estimated no_stripe occluded | 0.0 |  |  |
| 4A8B_lampwarm3_wood | 4A8B_lampwarm3_wood_close_01 | blue | 109 239 358 480 | truncated | 0.83 | det1 | 124 248 338 480 |
| 4A8B_lampwarm3_wood | 4A8B_lampwarm3_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0.0 |  |  |
| 4A8B_lampwarm3_wood | 4A8B_lampwarm3_wood_occl_04 | orange | 178 128 238 186 | bottom_estimated no_stripe occluded | 0.0 |  |  |
| 4A8B_lampwarm6_ottoman | 4A8B_lampwarm6_ottoman_close_01 | orange | 218 232 470 480 | truncated | 0.0 |  |  |
| 4A8B_lampwarm6_wood | 4A8B_lampwarm6_wood_close_01 | blue | 109 239 358 480 | truncated | 0.0 |  |  |
| 4A8B_lampwarm6_wood | 4A8B_lampwarm6_wood_held_01 | blue | 97 335 514 480 | held no_stripe truncated | 0.0 |  |  |
| 4A8B_lampwarm6_wood | 4A8B_lampwarm6_wood_occl_04 | orange | 178 128 238 186 | bottom_estimated no_stripe occluded | 0.0 |  |  |
| 4A8B_overheaddim_palewood | 4A8B_overheaddim_palewood_close_01 | orange | 291 243 566 480 | truncated | 0.0 |  |  |
| 4A8B_window_black | 4A8B_window_black_close_02 | orange | 154 245 426 480 | truncated | 0.72 | det1 | 159 258 366 480 |
| 4A8B_window_black | 4A8B_window_black_held_01 | orange | 90 327 521 480 | held truncated | 0.69 | det1 | 102 335 416 480 |
| DAVE* | DAVE_office_speckle_snap_06 | orange | 133 341 543 480 | truncated | 0.91 | det1 | 146 349 542 480 |
| DAVE* | DAVE_office_speckle_snap_07 | orange | 133 341 543 480 | truncated | 0.95 | det1 | 136 346 544 480 |
| DAVE* | DAVE_office_speckle_snap_08 | orange | 54 266 354 479 |  | 0.9 | det1 | 61 273 341 480 |
| DAVE* | DAVE_office_speckle_snap_08 | blue | 373 287 640 480 | truncated | 0.93 | det1 | 385 292 640 480 |
| DAVE* | DAVE_office_speckle_snap_09 | orange | 7 271 325 479 |  | 0.9 | det1 | 15 279 315 480 |
| DAVE* | DAVE_office_speckle_snap_09 | blue | 335 248 605 479 |  | 0.89 | det1 | 350 253 597 480 |
| DAVE* | DAVE_office_speckle_snap_10 | blue | 259 331 639 479 |  | 0.92 | det1 | 270 338 640 480 |
| DAVE* | DAVE_office_speckle_snap_11 | blue | 0 333 387 478 | truncated | 0.93 | det1 | 0 339 382 480 |

## Pieces refused as stripeless whose predicted stripe runs past the frame bottom

| set | stem | color | box | stripe_top | stripe_bottom | real | iou | negative |
|---|---|---|---|---|---|---|---|---|
| 4A8B_overheaddim_palewood | 4A8B_overheaddim_palewood_close_01 | orange | 292 241 568 477 | 434.2 | 482.8 | 1 | 0.97 | 0 |
