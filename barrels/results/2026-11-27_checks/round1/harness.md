# The proof harness with the paint checks on (yardstick H)

`harness.py`: 5435 masks. Before = today's boxes (`before.json`). Scored where the truth is known: masks made from a train frame against its hand boxes (261 of 261 frames have box labels), the 3888 simulated scenes against their own true boxes. A check only takes boxes away. Removed boxes by what they were before: F = on its barrel and found, O = on its barrel with the box off, W = wrong color on a barrel, S = a second box on a barrel, N = on nothing; unscored = a mask with no truth.

Same as the experiment's own post-filter (ref/checks.py + ref/stages.py) at the same numbers, arms SL and SLm: **yes, on every input**.

## S: solid paint only, solidity under 0.40 dropped (P)

| group | inputs changed | boxes removed | removed by what they were: F / O / W / S / N / unscored | barrels found (strict) before → after | found → box off | lost (no box left on it) | boxes not on their barrel before → after |
|---|---|---|---|---|---|---|---|
| damage | 28 / 666 | 32 | 29 / 3 / 0 / 0 / 0 / 0 | 803 → 774 of 1152 | 0 | 32 | 7 → 7 |
| hand | 0 / 45 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 115 → 115 of 135 | 0 | 0 | 1 → 1 |
| pool | 0 / 53 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 91 → 91 of 93 | 0 | 0 | 0 → 0 |
| real | 4 / 261 | 4 | 2 / 0 / 0 / 0 / 2 / 0 | 224 → 222 of 537 | 1 | 1 | 9 → 6 |
| real_dilate | 0 / 261 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 234 → 234 of 537 | 0 | 0 | 18 → 18 |
| real_erode | 0 / 261 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 181 → 181 of 537 | 0 | 0 | 2 → 2 |
| scene | 10 / 3888 | 10 | 9 / 1 / 0 / 0 / 0 / 0 | 4177 → 4168 of 5376 | 0 | 10 | 21 → 21 |
| **all** | 42 / 5435 | 46 | 40 / 4 / 0 / 0 / 2 / 0 | 5825 → 5785 of 8367 | 1 | 43 | 58 → 55 |

Every box removed (all groups):

| group | input | why | rule | color | box | before | solid | stripe h | body share | scene |
|---|---|---|---|---|---|---|---|---|---|---|
| damage | `heavy/0/CAMPUS color model/4A8B_campus_light_close_01` | speckle | body_span | orange | 262 184 392 356 | found | 0.3639 | 0.7693 | 0.3004 |  |
| damage | `heavy/0/CAMPUS color model/4A8B_campus_light_core_01` | speckle | body_span | blue | 98 159 200 281 | found | 0.3068 | 0.8436 | 0.2244 |  |
| damage | `heavy/0/CAMPUS color model/4A8B_campus_light_core_01` | speckle | hidden_side | orange | 402 128 467 195 | found | 0.2744 | 0.5518 | 0.1464 |  |
| damage | `heavy/0/CAMPUS color model/4A8B_campus_light_topstripe_01` | speckle | closeup | orange | 240 249 461 480 | found | 0.3943 | nan | 0.3673 |  |
| damage | `heavy/0/HOME hand masks/4A8B_window_light_close_01` | speckle | body_span | orange | 311 142 387 233 | found | 0.3515 | 0.7513 | 0.2922 |  |
| damage | `heavy/0/HOME hand masks/4A8B_window_light_close_02` | speckle | body_span | blue | 315 140 389 231 | found | 0.3645 | 0.6486 | 0.2964 |  |
| damage | `heavy/0/HOME hand masks/4A8B_window_light_occl_01` | speckle | body_span | orange | 345 139 421 227 | found | 0.3769 | 0.7801 | 0.2881 |  |
| damage | `heavy/0/HOME hand masks/4A8B_window_light_occl_02` | speckle | body_span | blue | 401 140 476 228 | found | 0.2946 | 0.6535 | 0.2806 |  |
| damage | `heavy/1/CAMPUS color model/4A8B_campus_light_close_01` | speckle | body_span | orange | 262 185 391 356 | found | 0.3601 | 0.7377 | 0.2795 |  |
| damage | `heavy/1/CAMPUS color model/4A8B_campus_light_core_01` | speckle | body_span | blue | 98 160 200 278 | found | 0.3114 | 0.7085 | 0.2059 |  |
| damage | `heavy/1/CAMPUS color model/4A8B_campus_light_plain_01` | speckle | body_span | blue | 80 148 160 248 | found | 0.3533 | 0.6114 | 0.2125 |  |
| damage | `heavy/1/CAMPUS color model/4A8B_campus_light_plain_01` | speckle | thin_span | orange | 502 151 585 231 | off | 0.3702 | 0.6885 | 0.3125 |  |
| damage | `heavy/1/HOME hand masks/4A8B_window_light_close_01` | speckle | body_span | orange | 311 142 387 231 | found | 0.3745 | 0.7123 | 0.2615 |  |
| damage | `heavy/1/HOME hand masks/4A8B_window_light_close_02` | speckle | body_span | blue | 315 141 388 231 | found | 0.3656 | 0.6833 | 0.289 |  |
| damage | `heavy/1/HOME hand masks/4A8B_window_light_occl_01` | speckle | body_span | orange | 346 139 421 227 | found | 0.346 | 0.6991 | 0.2672 |  |
| damage | `heavy/2/CAMPUS color model/4A8B_campus_light_close_01` | speckle | body_span | orange | 258 189 392 355 | found | 0.346 | 0.7666 | 0.301 |  |
| damage | `heavy/2/CAMPUS color model/4A8B_campus_light_core_01` | speckle | hidden_side | blue | 90 165 200 281 | found | 0.3234 | 0.8392 | 0.215 |  |
| damage | `heavy/2/CAMPUS color model/4A8B_campus_light_plain_01` | speckle | body_span | blue | 67 148 160 247 | found | 0.2795 | 0.651 | 0.206 |  |
| damage | `heavy/2/CAMPUS color model/4A8B_campus_light_topstripe_01` | speckle | closeup | orange | 232 252 461 480 | found | 0.397 | nan | 0.3334 |  |
| damage | `heavy/2/HOME hand masks/4A8B_window_light_occl_01` | speckle | body_span | orange | 344 136 421 227 | found | 0.3691 | 0.7832 | 0.2909 |  |
| damage | `medium/0/CAMPUS color model/4A8B_campus_light_touch_02` | speckle | whole_stripe | blue | 244 125 307 176 | off | 0.3608 | 0.6052 | 0.3279 |  |
| damage | `medium/0/HOME hand masks/4A8B_window_light_cluster_02` | speckle | body_span | orange | 393 117 430 160 | found | 0.3921 | 1.2134 | 0.5083 |  |
| damage | `medium/0/HOME hand masks/4A8B_window_light_far_02` | speckle | hidden_side | orange | 335 107 367 136 | found | 0.3858 | 0.68 | 0.3466 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_cluster_02` | speckle | body_span | blue | 345 121 397 167 | found | 0.3657 | 0.5293 | 0.3345 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_clutter_02` | speckle | whole_stripe | blue | 442 123 494 178 | found | 0.3903 | 0.7146 | 0.3596 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_clutter_02` | speckle | cap | blue | 460 124 519 168 | off | 0.2765 | nan | 0.1292 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_room_01` | speckle | body_span | blue | 66 121 121 181 | found | 0.3227 | 0.47 | 0.2248 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_room_01` | speckle | body_span | orange | 343 123 386 174 | found | 0.3728 | 0.5598 | 0.3848 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_touch_02` | speckle | body_span | blue | 226 125 271 176 | found | 0.3417 | 0.6052 | 0.3978 |  |
| damage | `medium/1/HOME hand masks/4A8B_window_light_far_02` | speckle | thin_span | blue | 221 112 251 142 | found | 0.3795 | 0.6227 | 0.4406 |  |
| damage | `medium/2/CAMPUS color model/4A8B_campus_light_clutter_02` | speckle | body_span | blue | 442 124 505 178 | found | 0.397 | 0.7233 | 0.3379 |  |
| damage | `medium/2/CAMPUS color model/4A8B_campus_light_core_01` | speckle | body_span | blue | 337 133 392 197 | found | 0.3916 | 0.6989 | 0.3738 |  |
| real | `4A8B_lampcool6_bathtile_clutter_01` | speckle | body_span | blue | 296 110 343 150 | found | 0.3992 | 0.7923 | 0.3355 |  |
| real | `4A8B_lampcool6_wood_occl_02` | speckle | hidden_side | orange | 179 112 225 164 | found | 0.266 | 0.4882 | 0.1652 |  |
| real | `4A8B_lampmid3_glass_occl_02` | speckle | whole_stripe | orange | 577 117 636 167 | nothing | 0.3918 | 1.651 | 0.1893 |  |
| real | `4A8B_overheaddim_palewood_core_01` | speckle | closeup | orange | 235 273 564 480 | nothing | 0.3418 | nan | 0.2792 |  |
| scene | `CAMPUS color model/00307/frame/0.25/R` | speckle | hidden_side | orange | 616 110 640 144 | found | 0.3941 | 0.527 | 0.4077 | frame 0.25 (hidden 0.319) |
| scene | `CAMPUS color model/00309/frame/0.5/R` | speckle | hidden_side | orange | 624 110 640 144 | found | 0.1802 | 0.527 | 0.2522 | frame 0.5 (hidden 0.686) |
| scene | `CAMPUS color model/00313/edge/0.25/R` | speckle | centred | orange | 241 110 277 144 | found | 0.3351 | 0.527 | 0.2718 | edge 0.25 (hidden 0.319) |
| scene | `CAMPUS color model/00320/slant/0.25/R+` | speckle | centred | orange | 242 110 279 144 | found | 0.3236 | 0.527 | 0.2654 | slant 0.25 (hidden 0.312) |
| scene | `CAMPUS color model/00321/slant/0.25/R-` | speckle | centred | orange | 243 110 279 144 | found | 0.3444 | 0.527 | 0.2887 | slant 0.25 (hidden 0.285) |
| scene | `CAMPUS color model/00331/both/0.5/` | speckle | centred | orange | 245 110 281 144 | found | 0.3905 | 0.4427 | 0.227 | both 0.5 (hidden 0.425) |
| scene | `CAMPUS color model/00334/top/0.5/` | speckle | half_stripe | orange | 249 107 278 144 | found | 0.3887 | nan | 0.212 | top 0.5 (hidden 0.516) |
| scene | `CAMPUS color model/01480/frame/0.75/L` | speckle | thin_frame | blue | 0 114 7 151 | found | 0.3451 | 0.4058 | 0.5312 | frame 0.75 (hidden 0.849) |
| scene | `CAMPUS color model/01510/post/0.5/` | speckle | body_span | blue | 180 112 214 151 | found | 0.3973 | 0.5604 | 0.273 | post 0.5 (hidden 0.607) |
| scene | `HOME color model/00425/post/0.75/` | speckle | pair | orange | 293 125 340 170 | off | 0.3525 | nan | 0.073 | post 0.75 (hidden 0.875) |

## L: label only, stripe over 1.25 x a stripe height with body under 0.6 dropped (P)

| group | inputs changed | boxes removed | removed by what they were: F / O / W / S / N / unscored | barrels found (strict) before → after | found → box off | lost (no box left on it) | boxes not on their barrel before → after |
|---|---|---|---|---|---|---|---|
| damage | 16 / 666 | 17 | 10 / 0 / 7 / 0 / 0 / 0 | 803 → 793 of 1152 | 0 | 10 | 7 → 0 |
| hand | 0 / 45 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 115 → 115 of 135 | 0 | 0 | 1 → 1 |
| pool | 0 / 53 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 91 → 91 of 93 | 0 | 0 | 0 → 0 |
| real | 6 / 261 | 6 | 1 / 1 / 1 / 0 / 3 / 0 | 224 → 223 of 537 | 0 | 2 | 9 → 5 |
| real_dilate | 6 / 261 | 6 | 1 / 0 / 0 / 0 / 5 / 0 | 234 → 233 of 537 | 0 | 1 | 18 → 13 |
| real_erode | 2 / 261 | 2 | 0 / 0 / 2 / 0 / 0 / 0 | 181 → 181 of 537 | 0 | 0 | 2 → 0 |
| scene | 48 / 3888 | 48 | 35 / 6 / 6 / 1 / 0 / 0 | 4177 → 4142 of 5376 | 0 | 41 | 21 → 14 |
| **all** | 78 / 5435 | 79 | 47 / 7 / 16 / 1 / 8 / 0 | 5825 → 5778 of 8367 | 0 | 54 | 58 → 33 |

Every box removed (all groups):

| group | input | why | rule | color | box | before | solid | stripe h | body share | scene |
|---|---|---|---|---|---|---|---|---|---|---|
| damage | `light/0/HOME hand masks/4A8B_window_light_cluster_01` | label | hidden_side | orange | 315 118 359 163 | found | 0.6125 | 1.8464 | 0.4821 |  |
| damage | `light/0/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 358 118 401 162 | found | 0.5863 | 1.8308 | 0.4468 |  |
| damage | `light/1/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.4085 | 1.4565 | 0.3741 |  |
| damage | `light/1/HOME hand masks/4A8B_window_light_cluster_01` | label | hidden_side | orange | 315 118 359 163 | found | 0.6059 | 1.8464 | 0.4797 |  |
| damage | `light/2/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.5668 | 1.8892 | 0.3278 |  |
| damage | `white tables, bad day/0/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 220 101 248 136 | wrong_color | 0.5044 | 1.4731 | 0.3912 |  |
| damage | `white tables, bad day/0/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.6785 | 1.8892 | 0.326 |  |
| damage | `white tables, bad day/1/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 101 247 136 | wrong_color | 0.5077 | 1.4731 | 0.3946 |  |
| damage | `white tables, bad day/1/HOME hand masks/4A8B_window_light_cluster_01` | label | hidden_side | orange | 315 118 358 163 | found | 0.6757 | 1.8744 | 0.4933 |  |
| damage | `white tables, bad day/2/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 222 101 248 136 | wrong_color | 0.4966 | 1.4731 | 0.4066 |  |
| damage | `white tables, typical/0/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.5886 | 1.4403 | 0.3793 |  |
| damage | `white tables, typical/0/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.7313 | 1.8892 | 0.3425 |  |
| damage | `white tables, typical/1/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.5886 | 1.4403 | 0.3793 |  |
| damage | `white tables, typical/1/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.7313 | 1.8892 | 0.3425 |  |
| damage | `white tables, typical/2/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.5886 | 1.4403 | 0.3793 |  |
| damage | `white tables, typical/2/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.7313 | 1.8892 | 0.3425 |  |
| damage | `white tables, worst seen/1/HOME hand masks/4A8B_window_light_cluster_02` | label | thin_span | orange | 393 117 430 160 | found | 0.5698 | 1.2507 | 0.5333 |  |
| real | `4A8B_lampcool3_wood_occl_04` | label | whole_stripe | orange | 186 126 239 185 | found | 0.4836 | 1.5218 | 0.1849 |  |
| real | `4A8B_lampcool6_wood_occl_02` | label | body_span | orange | 186 131 261 215 | wrong_color | 0.7168 | 1.6337 | 0.422 |  |
| real | `4A8B_lampcool6_wood_occl_04` | label | body_span | orange | 186 141 266 214 | off | 0.6686 | 1.789 | 0.5811 |  |
| real | `4A8B_lampmid3_glass_occl_02` | label | whole_stripe | orange | 577 117 636 167 | nothing | 0.3918 | 1.651 | 0.1893 |  |
| real | `4A8B_lampmid6_glass_clutter_01` | label | centred | orange | 554 117 604 171 | nothing | 0.6853 | 1.5253 | 0.5133 |  |
| real | `4A8B_lampwarm6_glass_clutter_01` | label | centred | orange | 555 117 605 172 | nothing | 0.7056 | 1.5253 | 0.5277 |  |
| real_dilate | `4A8B_lampcool3_wood_occl_04` | label | whole_stripe | orange | 186 135 240 186 | found | 0.6904 | 1.6636 | 0.4969 |  |
| real_dilate | `4A8B_lampmid3_glass_neg_02` | label | whole_stripe | orange | 559 122 609 166 | nothing | 0.6645 | 1.8397 | 0.588 |  |
| real_dilate | `4A8B_lampmid3_glass_occl_02` | label | whole_stripe | orange | 559 122 609 167 | nothing | 0.6578 | 1.7139 | 0.5467 |  |
| real_dilate | `4A8B_lampmid6_glass_clutter_01` | label | whole_stripe | orange | 560 117 609 172 | nothing | 0.8251 | 1.673 | 0.5834 |  |
| real_dilate | `4A8B_lampmid6_glass_occl_02` | label | centred | orange | 558 119 611 176 | nothing | 0.6431 | 1.569 | 0.3877 |  |
| real_dilate | `4A8B_window_glass_clutter_01` | label | body_span | orange | 561 118 609 171 | nothing | 0.7855 | 1.7139 | 0.4944 |  |
| real_erode | `4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.5886 | 1.4403 | 0.3793 |  |
| real_erode | `4A8B_overheaddim_palewood_core_01` | label | whole_stripe | orange | 438 107 476 150 | wrong_color | 0.7777 | 1.5388 | 0.3126 |  |
| scene | `CAMPUS color model/00043/barrel_low/other/0.25/R` | label | whole_stripe | blue | 368 204 550 424 | found | 0.9314 | 1.2628 | 0.541 | barrel_low/other 0.25 (hidden 0.044) |
| scene | `CAMPUS color model/00129/barrel_side/same/0.75/L` | label | centred | blue | 249 108 288 151 | wrong_color | 0.6012 | 1.5391 | 0.2682 | barrel_side/same 0.75 (hidden 0.788) |
| scene | `CAMPUS color model/00343/barrel_side/other/0.25/R` | label | whole_stripe | orange | 250 110 278 144 | found | 0.4241 | 1.5098 | 0.4706 | barrel_side/other 0.25 (hidden 0.265) |
| scene | `CAMPUS color model/00348/barrel_low/other/0.25/L` | label | whole_stripe | orange | 247 110 279 144 | found | 0.4849 | 1.2859 | 0.5658 | barrel_low/other 0.25 (hidden 0.042) |
| scene | `CAMPUS color model/00349/barrel_low/other/0.25/R` | label | body_span | orange | 248 110 279 146 | found | 0.4933 | 1.4285 | 0.4856 | barrel_low/other 0.25 (hidden 0.102) |
| scene | `CAMPUS color model/00351/barrel_low/other/0.5/R` | label | body_span | orange | 248 110 279 147 | found | 0.5337 | 1.5113 | 0.4295 | barrel_low/other 0.5 (hidden 0.367) |
| scene | `CAMPUS color model/00352/barrel_low/other/0.75/L` | label | centred | orange | 249 110 286 146 | found | 0.6397 | 1.5388 | 0.4565 | barrel_low/other 0.75 (hidden 0.438) |
| scene | `CAMPUS color model/00353/barrel_low/other/0.75/R` | label | body_span | orange | 248 110 279 148 | found | 0.6319 | 1.5113 | 0.4452 | barrel_low/other 0.75 (hidden 0.584) |
| scene | `CAMPUS color model/00422/barrel_side/other/0.5/L` | label | hidden_side | blue | 329 132 392 198 | found | 0.8474 | 2.0341 | 0.5604 | barrel_side/other 0.5 (hidden 0.428) |
| scene | `CAMPUS color model/00501/barrel_side/other/0.5/R` | label | whole_stripe | orange | 397 133 460 200 | found | 0.7665 | 1.6465 | 0.5905 | barrel_side/other 0.5 (hidden 0.378) |
| scene | `CAMPUS color model/00502/barrel_side/other/0.75/L` | label | whole_stripe | orange | 400 133 460 200 | found | 0.8293 | 1.6811 | 0.5952 | barrel_side/other 0.75 (hidden 0.572) |
| scene | `CAMPUS color model/00503/barrel_side/other/0.75/R` | label | whole_stripe | orange | 397 133 460 199 | found | 0.8217 | 1.5936 | 0.5745 | barrel_side/other 0.75 (hidden 0.59) |
| scene | `CAMPUS color model/00657/barrel_side/other/0.5/R` | label | hidden_side | blue | 240 110 276 146 | found | 0.7292 | 1.5675 | 0.5077 | barrel_side/other 0.5 (hidden 0.327) |
| scene | `CAMPUS color model/00682/barrel_front/same/0.5/` | label | centred | orange | 233 113 278 163 | wrong_color | 0.8105 | 1.5421 | 0.3825 | barrel_front/same 0.5 (hidden 0.456) |
| scene | `CAMPUS color model/00743/barrel_low/other/0.75/R` | label | hidden_side | blue | 315 111 355 153 | found | 0.7106 | 1.488 | 0.5989 | barrel_low/other 0.75 (hidden 0.579) |
| scene | `CAMPUS color model/00975/barrel_low/other/0.5/R` | label | whole_stripe | orange | 395 121 448 184 | found | 0.8011 | 1.7062 | 0.5927 | barrel_low/other 0.5 (hidden 0.494) |
| scene | `CAMPUS color model/01358/barrel_side/other/0.5/L` | label | hidden_side | blue | 64 125 119 176 | found | 0.7624 | 1.2675 | 0.3981 | barrel_side/other 0.5 (hidden 0.461) |
| scene | `CAMPUS color model/01438/barrel_side/other/0.75/L` | label | body_span | orange | 345 113 384 163 | off | 0.8095 | 1.7058 | 0.4892 | barrel_side/other 0.75 (hidden 0.681) |
| scene | `CAMPUS color model/01513/barrel_side/other/0.25/R` | label | hidden_side | blue | 181 112 220 152 | found | 0.667 | 1.3559 | 0.592 | barrel_side/other 0.25 (hidden 0.064) |
| scene | `CAMPUS color model/01514/barrel_side/other/0.5/L` | label | whole_stripe | blue | 181 112 214 151 | found | 0.6622 | 1.6769 | 0.5662 | barrel_side/other 0.5 (hidden 0.408) |
| scene | `CAMPUS color model/01515/barrel_side/other/0.5/R` | label | whole_stripe | blue | 181 112 212 152 | found | 0.6561 | 1.5391 | 0.596 | barrel_side/other 0.5 (hidden 0.292) |
| scene | `CAMPUS color model/01593/barrel_side/other/0.5/R` | label | hidden_side | orange | 220 111 258 150 | found | 0.7 | 1.6474 | 0.5332 | barrel_side/other 0.5 (hidden 0.349) |
| scene | `CAMPUS color model/01595/barrel_side/other/0.75/R` | label | centred | orange | 211 111 247 150 | found | 0.6319 | 1.6534 | 0.3347 | barrel_side/other 0.75 (hidden 0.697) |
| scene | `CAMPUS color model/01598/barrel_low/other/0.5/L` | label | hidden_side | orange | 210 112 249 154 | found | 0.7696 | 1.9061 | 0.5883 | barrel_low/other 0.5 (hidden 0.329) |
| scene | `CAMPUS color model/01743/barrel_side/other/0.5/R` | label | whole_stripe | blue | 225 120 277 177 | found | 0.8102 | 1.4863 | 0.5851 | barrel_side/other 0.5 (hidden 0.313) |
| scene | `CAMPUS color model/01745/barrel_side/other/0.75/R` | label | whole_stripe | blue | 225 120 277 177 | found | 0.7879 | 1.4818 | 0.509 | barrel_side/other 0.75 (hidden 0.531) |
| scene | `CAMPUS color model/01751/barrel_low/other/0.75/R` | label | whole_stripe | blue | 226 120 269 177 | found | 0.7928 | 1.6297 | 0.5961 | barrel_low/other 0.75 (hidden 0.613) |
| scene | `HOME color model/00275/barrel_side/other/0.75/R` | label | hidden_side | blue | 440 119 491 178 | found | 0.7986 | 1.517 | 0.3059 | barrel_side/other 0.75 (hidden 0.752) |
| scene | `HOME color model/00287/barrel_side/same/0.5/L` | label | body_span | blue | 455 120 503 185 | off | 0.7778 | 1.8589 | 0.4817 | barrel_side/same 0.5 (hidden 0.547) |
| scene | `HOME color model/00289/barrel_side/same/0.75/L` | label | whole_stripe | blue | 430 120 497 187 | found | 0.788 | 1.7952 | 0.5053 | barrel_side/same 0.75 (hidden 0.841) |
| scene | `HOME color model/00507/barrel_side/other/0.5/R` | label | centred | orange | 384 111 425 157 | second | 0.815 | 1.5899 | 0.3639 | barrel_side/other 0.5 (hidden 0.411) |
| scene | `HOME color model/00584/barrel_side/other/0.5/L` | label | hidden_side | blue | 404 117 449 163 | off | 0.7977 | 1.3832 | 0.5026 | barrel_side/other 0.5 (hidden 0.457) |
| scene | `HOME color model/00585/barrel_side/other/0.5/R` | label | whole_stripe | blue | 420 117 474 175 | found | 0.7753 | 1.631 | 0.5847 | barrel_side/other 0.5 (hidden 0.433) |
| scene | `HOME color model/00586/barrel_side/other/0.75/L` | label | body_span | blue | 423 117 474 163 | off | 0.7685 | 1.3832 | 0.5845 | barrel_side/other 0.75 (hidden 0.71) |
| scene | `HOME color model/00587/barrel_side/other/0.75/R` | label | whole_stripe | blue | 421 117 476 164 | off | 0.7422 | 1.7003 | 0.5554 | barrel_side/other 0.75 (hidden 0.68) |
| scene | `HOME color model/00663/barrel_side/other/0.5/R` | label | hidden_side | orange | 318 107 349 136 | found | 0.6541 | 1.2822 | 0.5585 | barrel_side/other 0.5 (hidden 0.434) |
| scene | `HOME color model/00665/barrel_side/other/0.75/R` | label | whole_stripe | orange | 318 102 342 136 | found | 0.5842 | 1.4403 | 0.3396 | barrel_side/other 0.75 (hidden 0.733) |
| scene | `HOME color model/00670/barrel_low/other/0.75/L` | label | whole_stripe | orange | 319 107 344 136 | found | 0.6087 | 1.3101 | 0.58 | barrel_low/other 0.75 (hidden 0.807) |
| scene | `HOME color model/00683/barrel_low/same/0.5/L` | label | hidden_side | orange | 312 107 344 136 | found | 0.733 | 1.9189 | 0.559 | barrel_low/same 0.5 (hidden 0.463) |
| scene | `HOME color model/00687/barrel_front/same/0.25/` | label | whole_stripe | blue | 314 112 349 159 | wrong_color | 0.7682 | 1.5888 | 0.4754 | barrel_front/same 0.25 (hidden 0.258) |
| scene | `HOME color model/00749/barrel_low/other/0.75/R` | label | whole_stripe | orange | 335 102 360 135 | found | 0.6062 | 1.4403 | 0.5011 | barrel_low/other 0.75 (hidden 0.733) |
| scene | `HOME color model/00843/barrel_front/same/0.25/` | label | whole_stripe | orange | 419 117 471 170 | wrong_color | 0.839 | 1.673 | 0.5662 | barrel_front/same 0.25 (hidden 0.348) |
| scene | `HOME color model/00845/barrel_front/same/0.75/` | label | hidden_side | orange | 444 104 477 141 | wrong_color | 0.7919 | 1.5696 | 0.4152 | barrel_front/same 0.75 (hidden 0.867) |
| scene | `HOME color model/00898/barrel_side/other/0.75/L` | label | whole_stripe | orange | 244 114 287 164 | off | 0.7476 | 1.4309 | 0.4138 | barrel_side/other 0.75 (hidden 0.812) |
| scene | `HOME color model/00899/barrel_side/other/0.75/R` | label | whole_stripe | orange | 241 122 283 174 | found | 0.7179 | 1.588 | 0.4651 | barrel_side/other 0.75 (hidden 0.709) |
| scene | `HOME hand masks/00818/barrel_side/other/0.5/L` | label | centred | blue | 439 108 473 139 | found | 0.8657 | 1.4498 | 0.4078 | barrel_side/other 0.5 (hidden 0.511) |
| scene | `HOME hand masks/00819/barrel_side/other/0.5/R` | label | centred | blue | 428 108 462 139 | found | 0.866 | 1.5391 | 0.479 | barrel_side/other 0.5 (hidden 0.433) |
| scene | `HOME hand masks/00844/barrel_front/same/0.5/` | label | centred | orange | 429 112 471 160 | wrong_color | 0.969 | 1.5408 | 0.5741 | barrel_front/same 0.5 (hidden 0.357) |

## SL: both, at P (0.40; 1.25 / 0.6)

| group | inputs changed | boxes removed | removed by what they were: F / O / W / S / N / unscored | barrels found (strict) before → after | found → box off | lost (no box left on it) | boxes not on their barrel before → after |
|---|---|---|---|---|---|---|---|
| damage | 44 / 666 | 49 | 39 / 3 / 7 / 0 / 0 / 0 | 803 → 764 of 1152 | 0 | 42 | 7 → 0 |
| hand | 0 / 45 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 115 → 115 of 135 | 0 | 0 | 1 → 1 |
| pool | 0 / 53 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 91 → 91 of 93 | 0 | 0 | 0 → 0 |
| real | 8 / 261 | 9 | 3 / 1 / 1 / 0 / 4 / 0 | 224 → 221 of 537 | 0 | 4 | 9 → 4 |
| real_dilate | 6 / 261 | 6 | 1 / 0 / 0 / 0 / 5 / 0 | 234 → 233 of 537 | 0 | 1 | 18 → 13 |
| real_erode | 2 / 261 | 2 | 0 / 0 / 2 / 0 / 0 / 0 | 181 → 181 of 537 | 0 | 0 | 2 → 0 |
| scene | 58 / 3888 | 58 | 44 / 7 / 6 / 1 / 0 / 0 | 4177 → 4133 of 5376 | 0 | 51 | 21 → 14 |
| **all** | 118 / 5435 | 124 | 87 / 11 / 16 / 1 / 9 / 0 | 5825 → 5738 of 8367 | 0 | 98 | 58 → 32 |

Every box removed (all groups):

| group | input | why | rule | color | box | before | solid | stripe h | body share | scene |
|---|---|---|---|---|---|---|---|---|---|---|
| damage | `heavy/0/CAMPUS color model/4A8B_campus_light_close_01` | speckle | body_span | orange | 262 184 392 356 | found | 0.3639 | 0.7693 | 0.3004 |  |
| damage | `heavy/0/CAMPUS color model/4A8B_campus_light_core_01` | speckle | body_span | blue | 98 159 200 281 | found | 0.3068 | 0.8436 | 0.2244 |  |
| damage | `heavy/0/CAMPUS color model/4A8B_campus_light_core_01` | speckle | hidden_side | orange | 402 128 467 195 | found | 0.2744 | 0.5518 | 0.1464 |  |
| damage | `heavy/0/CAMPUS color model/4A8B_campus_light_topstripe_01` | speckle | closeup | orange | 240 249 461 480 | found | 0.3943 | nan | 0.3673 |  |
| damage | `heavy/0/HOME hand masks/4A8B_window_light_close_01` | speckle | body_span | orange | 311 142 387 233 | found | 0.3515 | 0.7513 | 0.2922 |  |
| damage | `heavy/0/HOME hand masks/4A8B_window_light_close_02` | speckle | body_span | blue | 315 140 389 231 | found | 0.3645 | 0.6486 | 0.2964 |  |
| damage | `heavy/0/HOME hand masks/4A8B_window_light_occl_01` | speckle | body_span | orange | 345 139 421 227 | found | 0.3769 | 0.7801 | 0.2881 |  |
| damage | `heavy/0/HOME hand masks/4A8B_window_light_occl_02` | speckle | body_span | blue | 401 140 476 228 | found | 0.2946 | 0.6535 | 0.2806 |  |
| damage | `heavy/1/CAMPUS color model/4A8B_campus_light_close_01` | speckle | body_span | orange | 262 185 391 356 | found | 0.3601 | 0.7377 | 0.2795 |  |
| damage | `heavy/1/CAMPUS color model/4A8B_campus_light_core_01` | speckle | body_span | blue | 98 160 200 278 | found | 0.3114 | 0.7085 | 0.2059 |  |
| damage | `heavy/1/CAMPUS color model/4A8B_campus_light_plain_01` | speckle | body_span | blue | 80 148 160 248 | found | 0.3533 | 0.6114 | 0.2125 |  |
| damage | `heavy/1/CAMPUS color model/4A8B_campus_light_plain_01` | speckle | thin_span | orange | 502 151 585 231 | off | 0.3702 | 0.6885 | 0.3125 |  |
| damage | `heavy/1/HOME hand masks/4A8B_window_light_close_01` | speckle | body_span | orange | 311 142 387 231 | found | 0.3745 | 0.7123 | 0.2615 |  |
| damage | `heavy/1/HOME hand masks/4A8B_window_light_close_02` | speckle | body_span | blue | 315 141 388 231 | found | 0.3656 | 0.6833 | 0.289 |  |
| damage | `heavy/1/HOME hand masks/4A8B_window_light_occl_01` | speckle | body_span | orange | 346 139 421 227 | found | 0.346 | 0.6991 | 0.2672 |  |
| damage | `heavy/2/CAMPUS color model/4A8B_campus_light_close_01` | speckle | body_span | orange | 258 189 392 355 | found | 0.346 | 0.7666 | 0.301 |  |
| damage | `heavy/2/CAMPUS color model/4A8B_campus_light_core_01` | speckle | hidden_side | blue | 90 165 200 281 | found | 0.3234 | 0.8392 | 0.215 |  |
| damage | `heavy/2/CAMPUS color model/4A8B_campus_light_plain_01` | speckle | body_span | blue | 67 148 160 247 | found | 0.2795 | 0.651 | 0.206 |  |
| damage | `heavy/2/CAMPUS color model/4A8B_campus_light_topstripe_01` | speckle | closeup | orange | 232 252 461 480 | found | 0.397 | nan | 0.3334 |  |
| damage | `heavy/2/HOME hand masks/4A8B_window_light_occl_01` | speckle | body_span | orange | 344 136 421 227 | found | 0.3691 | 0.7832 | 0.2909 |  |
| damage | `light/0/HOME hand masks/4A8B_window_light_cluster_01` | label | hidden_side | orange | 315 118 359 163 | found | 0.6125 | 1.8464 | 0.4821 |  |
| damage | `light/0/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 358 118 401 162 | found | 0.5863 | 1.8308 | 0.4468 |  |
| damage | `light/1/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.4085 | 1.4565 | 0.3741 |  |
| damage | `light/1/HOME hand masks/4A8B_window_light_cluster_01` | label | hidden_side | orange | 315 118 359 163 | found | 0.6059 | 1.8464 | 0.4797 |  |
| damage | `light/2/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.5668 | 1.8892 | 0.3278 |  |
| damage | `medium/0/CAMPUS color model/4A8B_campus_light_touch_02` | speckle | whole_stripe | blue | 244 125 307 176 | off | 0.3608 | 0.6052 | 0.3279 |  |
| damage | `medium/0/HOME hand masks/4A8B_window_light_cluster_02` | speckle | body_span | orange | 393 117 430 160 | found | 0.3921 | 1.2134 | 0.5083 |  |
| damage | `medium/0/HOME hand masks/4A8B_window_light_far_02` | speckle | hidden_side | orange | 335 107 367 136 | found | 0.3858 | 0.68 | 0.3466 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_cluster_02` | speckle | body_span | blue | 345 121 397 167 | found | 0.3657 | 0.5293 | 0.3345 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_clutter_02` | speckle | whole_stripe | blue | 442 123 494 178 | found | 0.3903 | 0.7146 | 0.3596 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_clutter_02` | speckle | cap | blue | 460 124 519 168 | off | 0.2765 | nan | 0.1292 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_room_01` | speckle | body_span | blue | 66 121 121 181 | found | 0.3227 | 0.47 | 0.2248 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_room_01` | speckle | body_span | orange | 343 123 386 174 | found | 0.3728 | 0.5598 | 0.3848 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_touch_02` | speckle | body_span | blue | 226 125 271 176 | found | 0.3417 | 0.6052 | 0.3978 |  |
| damage | `medium/1/HOME hand masks/4A8B_window_light_far_02` | speckle | thin_span | blue | 221 112 251 142 | found | 0.3795 | 0.6227 | 0.4406 |  |
| damage | `medium/2/CAMPUS color model/4A8B_campus_light_clutter_02` | speckle | body_span | blue | 442 124 505 178 | found | 0.397 | 0.7233 | 0.3379 |  |
| damage | `medium/2/CAMPUS color model/4A8B_campus_light_core_01` | speckle | body_span | blue | 337 133 392 197 | found | 0.3916 | 0.6989 | 0.3738 |  |
| damage | `white tables, bad day/0/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 220 101 248 136 | wrong_color | 0.5044 | 1.4731 | 0.3912 |  |
| damage | `white tables, bad day/0/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.6785 | 1.8892 | 0.326 |  |
| damage | `white tables, bad day/1/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 101 247 136 | wrong_color | 0.5077 | 1.4731 | 0.3946 |  |
| damage | `white tables, bad day/1/HOME hand masks/4A8B_window_light_cluster_01` | label | hidden_side | orange | 315 118 358 163 | found | 0.6757 | 1.8744 | 0.4933 |  |
| damage | `white tables, bad day/2/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 222 101 248 136 | wrong_color | 0.4966 | 1.4731 | 0.4066 |  |
| damage | `white tables, typical/0/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.5886 | 1.4403 | 0.3793 |  |
| damage | `white tables, typical/0/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.7313 | 1.8892 | 0.3425 |  |
| damage | `white tables, typical/1/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.5886 | 1.4403 | 0.3793 |  |
| damage | `white tables, typical/1/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.7313 | 1.8892 | 0.3425 |  |
| damage | `white tables, typical/2/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.5886 | 1.4403 | 0.3793 |  |
| damage | `white tables, typical/2/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.7313 | 1.8892 | 0.3425 |  |
| damage | `white tables, worst seen/1/HOME hand masks/4A8B_window_light_cluster_02` | label | thin_span | orange | 393 117 430 160 | found | 0.5698 | 1.2507 | 0.5333 |  |
| real | `4A8B_lampcool3_wood_occl_04` | label | whole_stripe | orange | 186 126 239 185 | found | 0.4836 | 1.5218 | 0.1849 |  |
| real | `4A8B_lampcool6_bathtile_clutter_01` | speckle | body_span | blue | 296 110 343 150 | found | 0.3992 | 0.7923 | 0.3355 |  |
| real | `4A8B_lampcool6_wood_occl_02` | speckle | hidden_side | orange | 179 112 225 164 | found | 0.266 | 0.4882 | 0.1652 |  |
| real | `4A8B_lampcool6_wood_occl_02` | label | body_span | orange | 186 131 261 215 | wrong_color | 0.7168 | 1.6337 | 0.422 |  |
| real | `4A8B_lampcool6_wood_occl_04` | label | body_span | orange | 186 141 266 214 | off | 0.6686 | 1.789 | 0.5811 |  |
| real | `4A8B_lampmid3_glass_occl_02` | speckle | whole_stripe | orange | 577 117 636 167 | nothing | 0.3918 | 1.651 | 0.1893 |  |
| real | `4A8B_lampmid6_glass_clutter_01` | label | centred | orange | 554 117 604 171 | nothing | 0.6853 | 1.5253 | 0.5133 |  |
| real | `4A8B_lampwarm6_glass_clutter_01` | label | centred | orange | 555 117 605 172 | nothing | 0.7056 | 1.5253 | 0.5277 |  |
| real | `4A8B_overheaddim_palewood_core_01` | speckle | closeup | orange | 235 273 564 480 | nothing | 0.3418 | nan | 0.2792 |  |
| real_dilate | `4A8B_lampcool3_wood_occl_04` | label | whole_stripe | orange | 186 135 240 186 | found | 0.6904 | 1.6636 | 0.4969 |  |
| real_dilate | `4A8B_lampmid3_glass_neg_02` | label | whole_stripe | orange | 559 122 609 166 | nothing | 0.6645 | 1.8397 | 0.588 |  |
| real_dilate | `4A8B_lampmid3_glass_occl_02` | label | whole_stripe | orange | 559 122 609 167 | nothing | 0.6578 | 1.7139 | 0.5467 |  |
| real_dilate | `4A8B_lampmid6_glass_clutter_01` | label | whole_stripe | orange | 560 117 609 172 | nothing | 0.8251 | 1.673 | 0.5834 |  |
| real_dilate | `4A8B_lampmid6_glass_occl_02` | label | centred | orange | 558 119 611 176 | nothing | 0.6431 | 1.569 | 0.3877 |  |
| real_dilate | `4A8B_window_glass_clutter_01` | label | body_span | orange | 561 118 609 171 | nothing | 0.7855 | 1.7139 | 0.4944 |  |
| real_erode | `4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.5886 | 1.4403 | 0.3793 |  |
| real_erode | `4A8B_overheaddim_palewood_core_01` | label | whole_stripe | orange | 438 107 476 150 | wrong_color | 0.7777 | 1.5388 | 0.3126 |  |
| scene | `CAMPUS color model/00043/barrel_low/other/0.25/R` | label | whole_stripe | blue | 368 204 550 424 | found | 0.9314 | 1.2628 | 0.541 | barrel_low/other 0.25 (hidden 0.044) |
| scene | `CAMPUS color model/00129/barrel_side/same/0.75/L` | label | centred | blue | 249 108 288 151 | wrong_color | 0.6012 | 1.5391 | 0.2682 | barrel_side/same 0.75 (hidden 0.788) |
| scene | `CAMPUS color model/00307/frame/0.25/R` | speckle | hidden_side | orange | 616 110 640 144 | found | 0.3941 | 0.527 | 0.4077 | frame 0.25 (hidden 0.319) |
| scene | `CAMPUS color model/00309/frame/0.5/R` | speckle | hidden_side | orange | 624 110 640 144 | found | 0.1802 | 0.527 | 0.2522 | frame 0.5 (hidden 0.686) |
| scene | `CAMPUS color model/00313/edge/0.25/R` | speckle | centred | orange | 241 110 277 144 | found | 0.3351 | 0.527 | 0.2718 | edge 0.25 (hidden 0.319) |
| scene | `CAMPUS color model/00320/slant/0.25/R+` | speckle | centred | orange | 242 110 279 144 | found | 0.3236 | 0.527 | 0.2654 | slant 0.25 (hidden 0.312) |
| scene | `CAMPUS color model/00321/slant/0.25/R-` | speckle | centred | orange | 243 110 279 144 | found | 0.3444 | 0.527 | 0.2887 | slant 0.25 (hidden 0.285) |
| scene | `CAMPUS color model/00331/both/0.5/` | speckle | centred | orange | 245 110 281 144 | found | 0.3905 | 0.4427 | 0.227 | both 0.5 (hidden 0.425) |
| scene | `CAMPUS color model/00334/top/0.5/` | speckle | half_stripe | orange | 249 107 278 144 | found | 0.3887 | nan | 0.212 | top 0.5 (hidden 0.516) |
| scene | `CAMPUS color model/00343/barrel_side/other/0.25/R` | label | whole_stripe | orange | 250 110 278 144 | found | 0.4241 | 1.5098 | 0.4706 | barrel_side/other 0.25 (hidden 0.265) |
| scene | `CAMPUS color model/00348/barrel_low/other/0.25/L` | label | whole_stripe | orange | 247 110 279 144 | found | 0.4849 | 1.2859 | 0.5658 | barrel_low/other 0.25 (hidden 0.042) |
| scene | `CAMPUS color model/00349/barrel_low/other/0.25/R` | label | body_span | orange | 248 110 279 146 | found | 0.4933 | 1.4285 | 0.4856 | barrel_low/other 0.25 (hidden 0.102) |
| scene | `CAMPUS color model/00351/barrel_low/other/0.5/R` | label | body_span | orange | 248 110 279 147 | found | 0.5337 | 1.5113 | 0.4295 | barrel_low/other 0.5 (hidden 0.367) |
| scene | `CAMPUS color model/00352/barrel_low/other/0.75/L` | label | centred | orange | 249 110 286 146 | found | 0.6397 | 1.5388 | 0.4565 | barrel_low/other 0.75 (hidden 0.438) |
| scene | `CAMPUS color model/00353/barrel_low/other/0.75/R` | label | body_span | orange | 248 110 279 148 | found | 0.6319 | 1.5113 | 0.4452 | barrel_low/other 0.75 (hidden 0.584) |
| scene | `CAMPUS color model/00422/barrel_side/other/0.5/L` | label | hidden_side | blue | 329 132 392 198 | found | 0.8474 | 2.0341 | 0.5604 | barrel_side/other 0.5 (hidden 0.428) |
| scene | `CAMPUS color model/00501/barrel_side/other/0.5/R` | label | whole_stripe | orange | 397 133 460 200 | found | 0.7665 | 1.6465 | 0.5905 | barrel_side/other 0.5 (hidden 0.378) |
| scene | `CAMPUS color model/00502/barrel_side/other/0.75/L` | label | whole_stripe | orange | 400 133 460 200 | found | 0.8293 | 1.6811 | 0.5952 | barrel_side/other 0.75 (hidden 0.572) |
| scene | `CAMPUS color model/00503/barrel_side/other/0.75/R` | label | whole_stripe | orange | 397 133 460 199 | found | 0.8217 | 1.5936 | 0.5745 | barrel_side/other 0.75 (hidden 0.59) |
| scene | `CAMPUS color model/00657/barrel_side/other/0.5/R` | label | hidden_side | blue | 240 110 276 146 | found | 0.7292 | 1.5675 | 0.5077 | barrel_side/other 0.5 (hidden 0.327) |
| scene | `CAMPUS color model/00682/barrel_front/same/0.5/` | label | centred | orange | 233 113 278 163 | wrong_color | 0.8105 | 1.5421 | 0.3825 | barrel_front/same 0.5 (hidden 0.456) |
| scene | `CAMPUS color model/00743/barrel_low/other/0.75/R` | label | hidden_side | blue | 315 111 355 153 | found | 0.7106 | 1.488 | 0.5989 | barrel_low/other 0.75 (hidden 0.579) |
| scene | `CAMPUS color model/00975/barrel_low/other/0.5/R` | label | whole_stripe | orange | 395 121 448 184 | found | 0.8011 | 1.7062 | 0.5927 | barrel_low/other 0.5 (hidden 0.494) |
| scene | `CAMPUS color model/01358/barrel_side/other/0.5/L` | label | hidden_side | blue | 64 125 119 176 | found | 0.7624 | 1.2675 | 0.3981 | barrel_side/other 0.5 (hidden 0.461) |
| scene | `CAMPUS color model/01438/barrel_side/other/0.75/L` | label | body_span | orange | 345 113 384 163 | off | 0.8095 | 1.7058 | 0.4892 | barrel_side/other 0.75 (hidden 0.681) |
| scene | `CAMPUS color model/01480/frame/0.75/L` | speckle | thin_frame | blue | 0 114 7 151 | found | 0.3451 | 0.4058 | 0.5312 | frame 0.75 (hidden 0.849) |
| scene | `CAMPUS color model/01510/post/0.5/` | speckle | body_span | blue | 180 112 214 151 | found | 0.3973 | 0.5604 | 0.273 | post 0.5 (hidden 0.607) |
| scene | `CAMPUS color model/01513/barrel_side/other/0.25/R` | label | hidden_side | blue | 181 112 220 152 | found | 0.667 | 1.3559 | 0.592 | barrel_side/other 0.25 (hidden 0.064) |
| scene | `CAMPUS color model/01514/barrel_side/other/0.5/L` | label | whole_stripe | blue | 181 112 214 151 | found | 0.6622 | 1.6769 | 0.5662 | barrel_side/other 0.5 (hidden 0.408) |
| scene | `CAMPUS color model/01515/barrel_side/other/0.5/R` | label | whole_stripe | blue | 181 112 212 152 | found | 0.6561 | 1.5391 | 0.596 | barrel_side/other 0.5 (hidden 0.292) |
| scene | `CAMPUS color model/01593/barrel_side/other/0.5/R` | label | hidden_side | orange | 220 111 258 150 | found | 0.7 | 1.6474 | 0.5332 | barrel_side/other 0.5 (hidden 0.349) |
| scene | `CAMPUS color model/01595/barrel_side/other/0.75/R` | label | centred | orange | 211 111 247 150 | found | 0.6319 | 1.6534 | 0.3347 | barrel_side/other 0.75 (hidden 0.697) |
| scene | `CAMPUS color model/01598/barrel_low/other/0.5/L` | label | hidden_side | orange | 210 112 249 154 | found | 0.7696 | 1.9061 | 0.5883 | barrel_low/other 0.5 (hidden 0.329) |
| scene | `CAMPUS color model/01743/barrel_side/other/0.5/R` | label | whole_stripe | blue | 225 120 277 177 | found | 0.8102 | 1.4863 | 0.5851 | barrel_side/other 0.5 (hidden 0.313) |
| scene | `CAMPUS color model/01745/barrel_side/other/0.75/R` | label | whole_stripe | blue | 225 120 277 177 | found | 0.7879 | 1.4818 | 0.509 | barrel_side/other 0.75 (hidden 0.531) |
| scene | `CAMPUS color model/01751/barrel_low/other/0.75/R` | label | whole_stripe | blue | 226 120 269 177 | found | 0.7928 | 1.6297 | 0.5961 | barrel_low/other 0.75 (hidden 0.613) |
| scene | `HOME color model/00275/barrel_side/other/0.75/R` | label | hidden_side | blue | 440 119 491 178 | found | 0.7986 | 1.517 | 0.3059 | barrel_side/other 0.75 (hidden 0.752) |
| scene | `HOME color model/00287/barrel_side/same/0.5/L` | label | body_span | blue | 455 120 503 185 | off | 0.7778 | 1.8589 | 0.4817 | barrel_side/same 0.5 (hidden 0.547) |
| scene | `HOME color model/00289/barrel_side/same/0.75/L` | label | whole_stripe | blue | 430 120 497 187 | found | 0.788 | 1.7952 | 0.5053 | barrel_side/same 0.75 (hidden 0.841) |
| scene | `HOME color model/00425/post/0.75/` | speckle | pair | orange | 293 125 340 170 | off | 0.3525 | nan | 0.073 | post 0.75 (hidden 0.875) |
| scene | `HOME color model/00507/barrel_side/other/0.5/R` | label | centred | orange | 384 111 425 157 | second | 0.815 | 1.5899 | 0.3639 | barrel_side/other 0.5 (hidden 0.411) |
| scene | `HOME color model/00584/barrel_side/other/0.5/L` | label | hidden_side | blue | 404 117 449 163 | off | 0.7977 | 1.3832 | 0.5026 | barrel_side/other 0.5 (hidden 0.457) |
| scene | `HOME color model/00585/barrel_side/other/0.5/R` | label | whole_stripe | blue | 420 117 474 175 | found | 0.7753 | 1.631 | 0.5847 | barrel_side/other 0.5 (hidden 0.433) |
| scene | `HOME color model/00586/barrel_side/other/0.75/L` | label | body_span | blue | 423 117 474 163 | off | 0.7685 | 1.3832 | 0.5845 | barrel_side/other 0.75 (hidden 0.71) |
| scene | `HOME color model/00587/barrel_side/other/0.75/R` | label | whole_stripe | blue | 421 117 476 164 | off | 0.7422 | 1.7003 | 0.5554 | barrel_side/other 0.75 (hidden 0.68) |
| scene | `HOME color model/00663/barrel_side/other/0.5/R` | label | hidden_side | orange | 318 107 349 136 | found | 0.6541 | 1.2822 | 0.5585 | barrel_side/other 0.5 (hidden 0.434) |
| scene | `HOME color model/00665/barrel_side/other/0.75/R` | label | whole_stripe | orange | 318 102 342 136 | found | 0.5842 | 1.4403 | 0.3396 | barrel_side/other 0.75 (hidden 0.733) |
| scene | `HOME color model/00670/barrel_low/other/0.75/L` | label | whole_stripe | orange | 319 107 344 136 | found | 0.6087 | 1.3101 | 0.58 | barrel_low/other 0.75 (hidden 0.807) |
| scene | `HOME color model/00683/barrel_low/same/0.5/L` | label | hidden_side | orange | 312 107 344 136 | found | 0.733 | 1.9189 | 0.559 | barrel_low/same 0.5 (hidden 0.463) |
| scene | `HOME color model/00687/barrel_front/same/0.25/` | label | whole_stripe | blue | 314 112 349 159 | wrong_color | 0.7682 | 1.5888 | 0.4754 | barrel_front/same 0.25 (hidden 0.258) |
| scene | `HOME color model/00749/barrel_low/other/0.75/R` | label | whole_stripe | orange | 335 102 360 135 | found | 0.6062 | 1.4403 | 0.5011 | barrel_low/other 0.75 (hidden 0.733) |
| scene | `HOME color model/00843/barrel_front/same/0.25/` | label | whole_stripe | orange | 419 117 471 170 | wrong_color | 0.839 | 1.673 | 0.5662 | barrel_front/same 0.25 (hidden 0.348) |
| scene | `HOME color model/00845/barrel_front/same/0.75/` | label | hidden_side | orange | 444 104 477 141 | wrong_color | 0.7919 | 1.5696 | 0.4152 | barrel_front/same 0.75 (hidden 0.867) |
| scene | `HOME color model/00898/barrel_side/other/0.75/L` | label | whole_stripe | orange | 244 114 287 164 | off | 0.7476 | 1.4309 | 0.4138 | barrel_side/other 0.75 (hidden 0.812) |
| scene | `HOME color model/00899/barrel_side/other/0.75/R` | label | whole_stripe | orange | 241 122 283 174 | found | 0.7179 | 1.588 | 0.4651 | barrel_side/other 0.75 (hidden 0.709) |
| scene | `HOME hand masks/00818/barrel_side/other/0.5/L` | label | centred | blue | 439 108 473 139 | found | 0.8657 | 1.4498 | 0.4078 | barrel_side/other 0.5 (hidden 0.511) |
| scene | `HOME hand masks/00819/barrel_side/other/0.5/R` | label | centred | blue | 428 108 462 139 | found | 0.866 | 1.5391 | 0.479 | barrel_side/other 0.5 (hidden 0.433) |
| scene | `HOME hand masks/00844/barrel_front/same/0.5/` | label | centred | orange | 429 112 471 160 | wrong_color | 0.969 | 1.5408 | 0.5741 | barrel_front/same 0.5 (hidden 0.357) |

## Sm: solid paint only, under 0.35 (M)

| group | inputs changed | boxes removed | removed by what they were: F / O / W / S / N / unscored | barrels found (strict) before → after | found → box off | lost (no box left on it) | boxes not on their barrel before → after |
|---|---|---|---|---|---|---|---|
| damage | 10 / 666 | 11 | 10 / 1 / 0 / 0 / 0 / 0 | 803 → 793 of 1152 | 0 | 11 | 7 → 7 |
| hand | 0 / 45 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 115 → 115 of 135 | 0 | 0 | 1 → 1 |
| pool | 0 / 53 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 91 → 91 of 93 | 0 | 0 | 0 → 0 |
| real | 2 / 261 | 2 | 1 / 0 / 0 / 0 / 1 / 0 | 224 → 223 of 537 | 1 | 0 | 9 → 7 |
| real_dilate | 0 / 261 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 234 → 234 of 537 | 0 | 0 | 18 → 18 |
| real_erode | 0 / 261 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 181 → 181 of 537 | 0 | 0 | 2 → 2 |
| scene | 5 / 3888 | 5 | 5 / 0 / 0 / 0 / 0 / 0 | 4177 → 4172 of 5376 | 0 | 5 | 21 → 21 |
| **all** | 17 / 5435 | 18 | 16 / 1 / 0 / 0 / 1 / 0 | 5825 → 5809 of 8367 | 1 | 16 | 58 → 56 |

Every box removed (all groups):

| group | input | why | rule | color | box | before | solid | stripe h | body share | scene |
|---|---|---|---|---|---|---|---|---|---|---|
| damage | `heavy/0/CAMPUS color model/4A8B_campus_light_core_01` | speckle | body_span | blue | 98 159 200 281 | found | 0.3068 | 0.8436 | 0.2244 |  |
| damage | `heavy/0/CAMPUS color model/4A8B_campus_light_core_01` | speckle | hidden_side | orange | 402 128 467 195 | found | 0.2744 | 0.5518 | 0.1464 |  |
| damage | `heavy/0/HOME hand masks/4A8B_window_light_occl_02` | speckle | body_span | blue | 401 140 476 228 | found | 0.2946 | 0.6535 | 0.2806 |  |
| damage | `heavy/1/CAMPUS color model/4A8B_campus_light_core_01` | speckle | body_span | blue | 98 160 200 278 | found | 0.3114 | 0.7085 | 0.2059 |  |
| damage | `heavy/1/HOME hand masks/4A8B_window_light_occl_01` | speckle | body_span | orange | 346 139 421 227 | found | 0.346 | 0.6991 | 0.2672 |  |
| damage | `heavy/2/CAMPUS color model/4A8B_campus_light_close_01` | speckle | body_span | orange | 258 189 392 355 | found | 0.346 | 0.7666 | 0.301 |  |
| damage | `heavy/2/CAMPUS color model/4A8B_campus_light_core_01` | speckle | hidden_side | blue | 90 165 200 281 | found | 0.3234 | 0.8392 | 0.215 |  |
| damage | `heavy/2/CAMPUS color model/4A8B_campus_light_plain_01` | speckle | body_span | blue | 67 148 160 247 | found | 0.2795 | 0.651 | 0.206 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_clutter_02` | speckle | cap | blue | 460 124 519 168 | off | 0.2765 | nan | 0.1292 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_room_01` | speckle | body_span | blue | 66 121 121 181 | found | 0.3227 | 0.47 | 0.2248 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_touch_02` | speckle | body_span | blue | 226 125 271 176 | found | 0.3417 | 0.6052 | 0.3978 |  |
| real | `4A8B_lampcool6_wood_occl_02` | speckle | hidden_side | orange | 179 112 225 164 | found | 0.266 | 0.4882 | 0.1652 |  |
| real | `4A8B_overheaddim_palewood_core_01` | speckle | closeup | orange | 235 273 564 480 | nothing | 0.3418 | nan | 0.2792 |  |
| scene | `CAMPUS color model/00309/frame/0.5/R` | speckle | hidden_side | orange | 624 110 640 144 | found | 0.1802 | 0.527 | 0.2522 | frame 0.5 (hidden 0.686) |
| scene | `CAMPUS color model/00313/edge/0.25/R` | speckle | centred | orange | 241 110 277 144 | found | 0.3351 | 0.527 | 0.2718 | edge 0.25 (hidden 0.319) |
| scene | `CAMPUS color model/00320/slant/0.25/R+` | speckle | centred | orange | 242 110 279 144 | found | 0.3236 | 0.527 | 0.2654 | slant 0.25 (hidden 0.312) |
| scene | `CAMPUS color model/00321/slant/0.25/R-` | speckle | centred | orange | 243 110 279 144 | found | 0.3444 | 0.527 | 0.2887 | slant 0.25 (hidden 0.285) |
| scene | `CAMPUS color model/01480/frame/0.75/L` | speckle | thin_frame | blue | 0 114 7 151 | found | 0.3451 | 0.4058 | 0.5312 | frame 0.75 (hidden 0.849) |

## Lm: label only, over 1.5 x with body under 0.6 (M)

| group | inputs changed | boxes removed | removed by what they were: F / O / W / S / N / unscored | barrels found (strict) before → after | found → box off | lost (no box left on it) | boxes not on their barrel before → after |
|---|---|---|---|---|---|---|---|
| damage | 8 / 666 | 9 | 9 / 0 / 0 / 0 / 0 / 0 | 803 → 794 of 1152 | 0 | 9 | 7 → 7 |
| hand | 0 / 45 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 115 → 115 of 135 | 0 | 0 | 1 → 1 |
| pool | 0 / 53 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 91 → 91 of 93 | 0 | 0 | 0 → 0 |
| real | 6 / 261 | 6 | 1 / 1 / 1 / 0 / 3 / 0 | 224 → 223 of 537 | 0 | 2 | 9 → 5 |
| real_dilate | 6 / 261 | 6 | 1 / 0 / 0 / 0 / 5 / 0 | 234 → 233 of 537 | 0 | 1 | 18 → 13 |
| real_erode | 1 / 261 | 1 | 0 / 0 / 1 / 0 / 0 / 0 | 181 → 181 of 537 | 0 | 0 | 2 → 1 |
| scene | 32 / 3888 | 32 | 22 / 3 / 6 / 1 / 0 / 0 | 4177 → 4155 of 5376 | 0 | 25 | 21 → 14 |
| **all** | 53 / 5435 | 54 | 33 / 4 / 8 / 1 / 8 / 0 | 5825 → 5792 of 8367 | 0 | 37 | 58 → 41 |

Every box removed (all groups):

| group | input | why | rule | color | box | before | solid | stripe h | body share | scene |
|---|---|---|---|---|---|---|---|---|---|---|
| damage | `light/0/HOME hand masks/4A8B_window_light_cluster_01` | label | hidden_side | orange | 315 118 359 163 | found | 0.6125 | 1.8464 | 0.4821 |  |
| damage | `light/0/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 358 118 401 162 | found | 0.5863 | 1.8308 | 0.4468 |  |
| damage | `light/1/HOME hand masks/4A8B_window_light_cluster_01` | label | hidden_side | orange | 315 118 359 163 | found | 0.6059 | 1.8464 | 0.4797 |  |
| damage | `light/2/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.5668 | 1.8892 | 0.3278 |  |
| damage | `white tables, bad day/0/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.6785 | 1.8892 | 0.326 |  |
| damage | `white tables, bad day/1/HOME hand masks/4A8B_window_light_cluster_01` | label | hidden_side | orange | 315 118 358 163 | found | 0.6757 | 1.8744 | 0.4933 |  |
| damage | `white tables, typical/0/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.7313 | 1.8892 | 0.3425 |  |
| damage | `white tables, typical/1/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.7313 | 1.8892 | 0.3425 |  |
| damage | `white tables, typical/2/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.7313 | 1.8892 | 0.3425 |  |
| real | `4A8B_lampcool3_wood_occl_04` | label | whole_stripe | orange | 186 126 239 185 | found | 0.4836 | 1.5218 | 0.1849 |  |
| real | `4A8B_lampcool6_wood_occl_02` | label | body_span | orange | 186 131 261 215 | wrong_color | 0.7168 | 1.6337 | 0.422 |  |
| real | `4A8B_lampcool6_wood_occl_04` | label | body_span | orange | 186 141 266 214 | off | 0.6686 | 1.789 | 0.5811 |  |
| real | `4A8B_lampmid3_glass_occl_02` | label | whole_stripe | orange | 577 117 636 167 | nothing | 0.3918 | 1.651 | 0.1893 |  |
| real | `4A8B_lampmid6_glass_clutter_01` | label | centred | orange | 554 117 604 171 | nothing | 0.6853 | 1.5253 | 0.5133 |  |
| real | `4A8B_lampwarm6_glass_clutter_01` | label | centred | orange | 555 117 605 172 | nothing | 0.7056 | 1.5253 | 0.5277 |  |
| real_dilate | `4A8B_lampcool3_wood_occl_04` | label | whole_stripe | orange | 186 135 240 186 | found | 0.6904 | 1.6636 | 0.4969 |  |
| real_dilate | `4A8B_lampmid3_glass_neg_02` | label | whole_stripe | orange | 559 122 609 166 | nothing | 0.6645 | 1.8397 | 0.588 |  |
| real_dilate | `4A8B_lampmid3_glass_occl_02` | label | whole_stripe | orange | 559 122 609 167 | nothing | 0.6578 | 1.7139 | 0.5467 |  |
| real_dilate | `4A8B_lampmid6_glass_clutter_01` | label | whole_stripe | orange | 560 117 609 172 | nothing | 0.8251 | 1.673 | 0.5834 |  |
| real_dilate | `4A8B_lampmid6_glass_occl_02` | label | centred | orange | 558 119 611 176 | nothing | 0.6431 | 1.569 | 0.3877 |  |
| real_dilate | `4A8B_window_glass_clutter_01` | label | body_span | orange | 561 118 609 171 | nothing | 0.7855 | 1.7139 | 0.4944 |  |
| real_erode | `4A8B_overheaddim_palewood_core_01` | label | whole_stripe | orange | 438 107 476 150 | wrong_color | 0.7777 | 1.5388 | 0.3126 |  |
| scene | `CAMPUS color model/00129/barrel_side/same/0.75/L` | label | centred | blue | 249 108 288 151 | wrong_color | 0.6012 | 1.5391 | 0.2682 | barrel_side/same 0.75 (hidden 0.788) |
| scene | `CAMPUS color model/00343/barrel_side/other/0.25/R` | label | whole_stripe | orange | 250 110 278 144 | found | 0.4241 | 1.5098 | 0.4706 | barrel_side/other 0.25 (hidden 0.265) |
| scene | `CAMPUS color model/00351/barrel_low/other/0.5/R` | label | body_span | orange | 248 110 279 147 | found | 0.5337 | 1.5113 | 0.4295 | barrel_low/other 0.5 (hidden 0.367) |
| scene | `CAMPUS color model/00352/barrel_low/other/0.75/L` | label | centred | orange | 249 110 286 146 | found | 0.6397 | 1.5388 | 0.4565 | barrel_low/other 0.75 (hidden 0.438) |
| scene | `CAMPUS color model/00353/barrel_low/other/0.75/R` | label | body_span | orange | 248 110 279 148 | found | 0.6319 | 1.5113 | 0.4452 | barrel_low/other 0.75 (hidden 0.584) |
| scene | `CAMPUS color model/00422/barrel_side/other/0.5/L` | label | hidden_side | blue | 329 132 392 198 | found | 0.8474 | 2.0341 | 0.5604 | barrel_side/other 0.5 (hidden 0.428) |
| scene | `CAMPUS color model/00501/barrel_side/other/0.5/R` | label | whole_stripe | orange | 397 133 460 200 | found | 0.7665 | 1.6465 | 0.5905 | barrel_side/other 0.5 (hidden 0.378) |
| scene | `CAMPUS color model/00502/barrel_side/other/0.75/L` | label | whole_stripe | orange | 400 133 460 200 | found | 0.8293 | 1.6811 | 0.5952 | barrel_side/other 0.75 (hidden 0.572) |
| scene | `CAMPUS color model/00503/barrel_side/other/0.75/R` | label | whole_stripe | orange | 397 133 460 199 | found | 0.8217 | 1.5936 | 0.5745 | barrel_side/other 0.75 (hidden 0.59) |
| scene | `CAMPUS color model/00657/barrel_side/other/0.5/R` | label | hidden_side | blue | 240 110 276 146 | found | 0.7292 | 1.5675 | 0.5077 | barrel_side/other 0.5 (hidden 0.327) |
| scene | `CAMPUS color model/00682/barrel_front/same/0.5/` | label | centred | orange | 233 113 278 163 | wrong_color | 0.8105 | 1.5421 | 0.3825 | barrel_front/same 0.5 (hidden 0.456) |
| scene | `CAMPUS color model/00975/barrel_low/other/0.5/R` | label | whole_stripe | orange | 395 121 448 184 | found | 0.8011 | 1.7062 | 0.5927 | barrel_low/other 0.5 (hidden 0.494) |
| scene | `CAMPUS color model/01438/barrel_side/other/0.75/L` | label | body_span | orange | 345 113 384 163 | off | 0.8095 | 1.7058 | 0.4892 | barrel_side/other 0.75 (hidden 0.681) |
| scene | `CAMPUS color model/01514/barrel_side/other/0.5/L` | label | whole_stripe | blue | 181 112 214 151 | found | 0.6622 | 1.6769 | 0.5662 | barrel_side/other 0.5 (hidden 0.408) |
| scene | `CAMPUS color model/01515/barrel_side/other/0.5/R` | label | whole_stripe | blue | 181 112 212 152 | found | 0.6561 | 1.5391 | 0.596 | barrel_side/other 0.5 (hidden 0.292) |
| scene | `CAMPUS color model/01593/barrel_side/other/0.5/R` | label | hidden_side | orange | 220 111 258 150 | found | 0.7 | 1.6474 | 0.5332 | barrel_side/other 0.5 (hidden 0.349) |
| scene | `CAMPUS color model/01595/barrel_side/other/0.75/R` | label | centred | orange | 211 111 247 150 | found | 0.6319 | 1.6534 | 0.3347 | barrel_side/other 0.75 (hidden 0.697) |
| scene | `CAMPUS color model/01598/barrel_low/other/0.5/L` | label | hidden_side | orange | 210 112 249 154 | found | 0.7696 | 1.9061 | 0.5883 | barrel_low/other 0.5 (hidden 0.329) |
| scene | `CAMPUS color model/01751/barrel_low/other/0.75/R` | label | whole_stripe | blue | 226 120 269 177 | found | 0.7928 | 1.6297 | 0.5961 | barrel_low/other 0.75 (hidden 0.613) |
| scene | `HOME color model/00275/barrel_side/other/0.75/R` | label | hidden_side | blue | 440 119 491 178 | found | 0.7986 | 1.517 | 0.3059 | barrel_side/other 0.75 (hidden 0.752) |
| scene | `HOME color model/00287/barrel_side/same/0.5/L` | label | body_span | blue | 455 120 503 185 | off | 0.7778 | 1.8589 | 0.4817 | barrel_side/same 0.5 (hidden 0.547) |
| scene | `HOME color model/00289/barrel_side/same/0.75/L` | label | whole_stripe | blue | 430 120 497 187 | found | 0.788 | 1.7952 | 0.5053 | barrel_side/same 0.75 (hidden 0.841) |
| scene | `HOME color model/00507/barrel_side/other/0.5/R` | label | centred | orange | 384 111 425 157 | second | 0.815 | 1.5899 | 0.3639 | barrel_side/other 0.5 (hidden 0.411) |
| scene | `HOME color model/00585/barrel_side/other/0.5/R` | label | whole_stripe | blue | 420 117 474 175 | found | 0.7753 | 1.631 | 0.5847 | barrel_side/other 0.5 (hidden 0.433) |
| scene | `HOME color model/00587/barrel_side/other/0.75/R` | label | whole_stripe | blue | 421 117 476 164 | off | 0.7422 | 1.7003 | 0.5554 | barrel_side/other 0.75 (hidden 0.68) |
| scene | `HOME color model/00683/barrel_low/same/0.5/L` | label | hidden_side | orange | 312 107 344 136 | found | 0.733 | 1.9189 | 0.559 | barrel_low/same 0.5 (hidden 0.463) |
| scene | `HOME color model/00687/barrel_front/same/0.25/` | label | whole_stripe | blue | 314 112 349 159 | wrong_color | 0.7682 | 1.5888 | 0.4754 | barrel_front/same 0.25 (hidden 0.258) |
| scene | `HOME color model/00843/barrel_front/same/0.25/` | label | whole_stripe | orange | 419 117 471 170 | wrong_color | 0.839 | 1.673 | 0.5662 | barrel_front/same 0.25 (hidden 0.348) |
| scene | `HOME color model/00845/barrel_front/same/0.75/` | label | hidden_side | orange | 444 104 477 141 | wrong_color | 0.7919 | 1.5696 | 0.4152 | barrel_front/same 0.75 (hidden 0.867) |
| scene | `HOME color model/00899/barrel_side/other/0.75/R` | label | whole_stripe | orange | 241 122 283 174 | found | 0.7179 | 1.588 | 0.4651 | barrel_side/other 0.75 (hidden 0.709) |
| scene | `HOME hand masks/00819/barrel_side/other/0.5/R` | label | centred | blue | 428 108 462 139 | found | 0.866 | 1.5391 | 0.479 | barrel_side/other 0.5 (hidden 0.433) |
| scene | `HOME hand masks/00844/barrel_front/same/0.5/` | label | centred | orange | 429 112 471 160 | wrong_color | 0.969 | 1.5408 | 0.5741 | barrel_front/same 0.5 (hidden 0.357) |

## SLm: both, at M (0.35; 1.5 / 0.6)

| group | inputs changed | boxes removed | removed by what they were: F / O / W / S / N / unscored | barrels found (strict) before → after | found → box off | lost (no box left on it) | boxes not on their barrel before → after |
|---|---|---|---|---|---|---|---|
| damage | 18 / 666 | 20 | 19 / 1 / 0 / 0 / 0 / 0 | 803 → 784 of 1152 | 0 | 20 | 7 → 7 |
| hand | 0 / 45 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 115 → 115 of 135 | 0 | 0 | 1 → 1 |
| pool | 0 / 53 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 91 → 91 of 93 | 0 | 0 | 0 → 0 |
| real | 7 / 261 | 8 | 2 / 1 / 1 / 0 / 4 / 0 | 224 → 222 of 537 | 0 | 3 | 9 → 4 |
| real_dilate | 6 / 261 | 6 | 1 / 0 / 0 / 0 / 5 / 0 | 234 → 233 of 537 | 0 | 1 | 18 → 13 |
| real_erode | 1 / 261 | 1 | 0 / 0 / 1 / 0 / 0 / 0 | 181 → 181 of 537 | 0 | 0 | 2 → 1 |
| scene | 37 / 3888 | 37 | 27 / 3 / 6 / 1 / 0 / 0 | 4177 → 4150 of 5376 | 0 | 30 | 21 → 14 |
| **all** | 69 / 5435 | 72 | 49 / 5 / 8 / 1 / 9 / 0 | 5825 → 5776 of 8367 | 0 | 54 | 58 → 40 |

Every box removed (all groups):

| group | input | why | rule | color | box | before | solid | stripe h | body share | scene |
|---|---|---|---|---|---|---|---|---|---|---|
| damage | `heavy/0/CAMPUS color model/4A8B_campus_light_core_01` | speckle | body_span | blue | 98 159 200 281 | found | 0.3068 | 0.8436 | 0.2244 |  |
| damage | `heavy/0/CAMPUS color model/4A8B_campus_light_core_01` | speckle | hidden_side | orange | 402 128 467 195 | found | 0.2744 | 0.5518 | 0.1464 |  |
| damage | `heavy/0/HOME hand masks/4A8B_window_light_occl_02` | speckle | body_span | blue | 401 140 476 228 | found | 0.2946 | 0.6535 | 0.2806 |  |
| damage | `heavy/1/CAMPUS color model/4A8B_campus_light_core_01` | speckle | body_span | blue | 98 160 200 278 | found | 0.3114 | 0.7085 | 0.2059 |  |
| damage | `heavy/1/HOME hand masks/4A8B_window_light_occl_01` | speckle | body_span | orange | 346 139 421 227 | found | 0.346 | 0.6991 | 0.2672 |  |
| damage | `heavy/2/CAMPUS color model/4A8B_campus_light_close_01` | speckle | body_span | orange | 258 189 392 355 | found | 0.346 | 0.7666 | 0.301 |  |
| damage | `heavy/2/CAMPUS color model/4A8B_campus_light_core_01` | speckle | hidden_side | blue | 90 165 200 281 | found | 0.3234 | 0.8392 | 0.215 |  |
| damage | `heavy/2/CAMPUS color model/4A8B_campus_light_plain_01` | speckle | body_span | blue | 67 148 160 247 | found | 0.2795 | 0.651 | 0.206 |  |
| damage | `light/0/HOME hand masks/4A8B_window_light_cluster_01` | label | hidden_side | orange | 315 118 359 163 | found | 0.6125 | 1.8464 | 0.4821 |  |
| damage | `light/0/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 358 118 401 162 | found | 0.5863 | 1.8308 | 0.4468 |  |
| damage | `light/1/HOME hand masks/4A8B_window_light_cluster_01` | label | hidden_side | orange | 315 118 359 163 | found | 0.6059 | 1.8464 | 0.4797 |  |
| damage | `light/2/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.5668 | 1.8892 | 0.3278 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_clutter_02` | speckle | cap | blue | 460 124 519 168 | off | 0.2765 | nan | 0.1292 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_room_01` | speckle | body_span | blue | 66 121 121 181 | found | 0.3227 | 0.47 | 0.2248 |  |
| damage | `medium/1/CAMPUS color model/4A8B_campus_light_touch_02` | speckle | body_span | blue | 226 125 271 176 | found | 0.3417 | 0.6052 | 0.3978 |  |
| damage | `white tables, bad day/0/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.6785 | 1.8892 | 0.326 |  |
| damage | `white tables, bad day/1/HOME hand masks/4A8B_window_light_cluster_01` | label | hidden_side | orange | 315 118 358 163 | found | 0.6757 | 1.8744 | 0.4933 |  |
| damage | `white tables, typical/0/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.7313 | 1.8892 | 0.3425 |  |
| damage | `white tables, typical/1/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.7313 | 1.8892 | 0.3425 |  |
| damage | `white tables, typical/2/HOME hand masks/4A8B_window_light_cluster_01` | label | centred | orange | 357 111 399 162 | found | 0.7313 | 1.8892 | 0.3425 |  |
| real | `4A8B_lampcool3_wood_occl_04` | label | whole_stripe | orange | 186 126 239 185 | found | 0.4836 | 1.5218 | 0.1849 |  |
| real | `4A8B_lampcool6_wood_occl_02` | speckle | hidden_side | orange | 179 112 225 164 | found | 0.266 | 0.4882 | 0.1652 |  |
| real | `4A8B_lampcool6_wood_occl_02` | label | body_span | orange | 186 131 261 215 | wrong_color | 0.7168 | 1.6337 | 0.422 |  |
| real | `4A8B_lampcool6_wood_occl_04` | label | body_span | orange | 186 141 266 214 | off | 0.6686 | 1.789 | 0.5811 |  |
| real | `4A8B_lampmid3_glass_occl_02` | label | whole_stripe | orange | 577 117 636 167 | nothing | 0.3918 | 1.651 | 0.1893 |  |
| real | `4A8B_lampmid6_glass_clutter_01` | label | centred | orange | 554 117 604 171 | nothing | 0.6853 | 1.5253 | 0.5133 |  |
| real | `4A8B_lampwarm6_glass_clutter_01` | label | centred | orange | 555 117 605 172 | nothing | 0.7056 | 1.5253 | 0.5277 |  |
| real | `4A8B_overheaddim_palewood_core_01` | speckle | closeup | orange | 235 273 564 480 | nothing | 0.3418 | nan | 0.2792 |  |
| real_dilate | `4A8B_lampcool3_wood_occl_04` | label | whole_stripe | orange | 186 135 240 186 | found | 0.6904 | 1.6636 | 0.4969 |  |
| real_dilate | `4A8B_lampmid3_glass_neg_02` | label | whole_stripe | orange | 559 122 609 166 | nothing | 0.6645 | 1.8397 | 0.588 |  |
| real_dilate | `4A8B_lampmid3_glass_occl_02` | label | whole_stripe | orange | 559 122 609 167 | nothing | 0.6578 | 1.7139 | 0.5467 |  |
| real_dilate | `4A8B_lampmid6_glass_clutter_01` | label | whole_stripe | orange | 560 117 609 172 | nothing | 0.8251 | 1.673 | 0.5834 |  |
| real_dilate | `4A8B_lampmid6_glass_occl_02` | label | centred | orange | 558 119 611 176 | nothing | 0.6431 | 1.569 | 0.3877 |  |
| real_dilate | `4A8B_window_glass_clutter_01` | label | body_span | orange | 561 118 609 171 | nothing | 0.7855 | 1.7139 | 0.4944 |  |
| real_erode | `4A8B_overheaddim_palewood_core_01` | label | whole_stripe | orange | 438 107 476 150 | wrong_color | 0.7777 | 1.5388 | 0.3126 |  |
| scene | `CAMPUS color model/00129/barrel_side/same/0.75/L` | label | centred | blue | 249 108 288 151 | wrong_color | 0.6012 | 1.5391 | 0.2682 | barrel_side/same 0.75 (hidden 0.788) |
| scene | `CAMPUS color model/00309/frame/0.5/R` | speckle | hidden_side | orange | 624 110 640 144 | found | 0.1802 | 0.527 | 0.2522 | frame 0.5 (hidden 0.686) |
| scene | `CAMPUS color model/00313/edge/0.25/R` | speckle | centred | orange | 241 110 277 144 | found | 0.3351 | 0.527 | 0.2718 | edge 0.25 (hidden 0.319) |
| scene | `CAMPUS color model/00320/slant/0.25/R+` | speckle | centred | orange | 242 110 279 144 | found | 0.3236 | 0.527 | 0.2654 | slant 0.25 (hidden 0.312) |
| scene | `CAMPUS color model/00321/slant/0.25/R-` | speckle | centred | orange | 243 110 279 144 | found | 0.3444 | 0.527 | 0.2887 | slant 0.25 (hidden 0.285) |
| scene | `CAMPUS color model/00343/barrel_side/other/0.25/R` | label | whole_stripe | orange | 250 110 278 144 | found | 0.4241 | 1.5098 | 0.4706 | barrel_side/other 0.25 (hidden 0.265) |
| scene | `CAMPUS color model/00351/barrel_low/other/0.5/R` | label | body_span | orange | 248 110 279 147 | found | 0.5337 | 1.5113 | 0.4295 | barrel_low/other 0.5 (hidden 0.367) |
| scene | `CAMPUS color model/00352/barrel_low/other/0.75/L` | label | centred | orange | 249 110 286 146 | found | 0.6397 | 1.5388 | 0.4565 | barrel_low/other 0.75 (hidden 0.438) |
| scene | `CAMPUS color model/00353/barrel_low/other/0.75/R` | label | body_span | orange | 248 110 279 148 | found | 0.6319 | 1.5113 | 0.4452 | barrel_low/other 0.75 (hidden 0.584) |
| scene | `CAMPUS color model/00422/barrel_side/other/0.5/L` | label | hidden_side | blue | 329 132 392 198 | found | 0.8474 | 2.0341 | 0.5604 | barrel_side/other 0.5 (hidden 0.428) |
| scene | `CAMPUS color model/00501/barrel_side/other/0.5/R` | label | whole_stripe | orange | 397 133 460 200 | found | 0.7665 | 1.6465 | 0.5905 | barrel_side/other 0.5 (hidden 0.378) |
| scene | `CAMPUS color model/00502/barrel_side/other/0.75/L` | label | whole_stripe | orange | 400 133 460 200 | found | 0.8293 | 1.6811 | 0.5952 | barrel_side/other 0.75 (hidden 0.572) |
| scene | `CAMPUS color model/00503/barrel_side/other/0.75/R` | label | whole_stripe | orange | 397 133 460 199 | found | 0.8217 | 1.5936 | 0.5745 | barrel_side/other 0.75 (hidden 0.59) |
| scene | `CAMPUS color model/00657/barrel_side/other/0.5/R` | label | hidden_side | blue | 240 110 276 146 | found | 0.7292 | 1.5675 | 0.5077 | barrel_side/other 0.5 (hidden 0.327) |
| scene | `CAMPUS color model/00682/barrel_front/same/0.5/` | label | centred | orange | 233 113 278 163 | wrong_color | 0.8105 | 1.5421 | 0.3825 | barrel_front/same 0.5 (hidden 0.456) |
| scene | `CAMPUS color model/00975/barrel_low/other/0.5/R` | label | whole_stripe | orange | 395 121 448 184 | found | 0.8011 | 1.7062 | 0.5927 | barrel_low/other 0.5 (hidden 0.494) |
| scene | `CAMPUS color model/01438/barrel_side/other/0.75/L` | label | body_span | orange | 345 113 384 163 | off | 0.8095 | 1.7058 | 0.4892 | barrel_side/other 0.75 (hidden 0.681) |
| scene | `CAMPUS color model/01480/frame/0.75/L` | speckle | thin_frame | blue | 0 114 7 151 | found | 0.3451 | 0.4058 | 0.5312 | frame 0.75 (hidden 0.849) |
| scene | `CAMPUS color model/01514/barrel_side/other/0.5/L` | label | whole_stripe | blue | 181 112 214 151 | found | 0.6622 | 1.6769 | 0.5662 | barrel_side/other 0.5 (hidden 0.408) |
| scene | `CAMPUS color model/01515/barrel_side/other/0.5/R` | label | whole_stripe | blue | 181 112 212 152 | found | 0.6561 | 1.5391 | 0.596 | barrel_side/other 0.5 (hidden 0.292) |
| scene | `CAMPUS color model/01593/barrel_side/other/0.5/R` | label | hidden_side | orange | 220 111 258 150 | found | 0.7 | 1.6474 | 0.5332 | barrel_side/other 0.5 (hidden 0.349) |
| scene | `CAMPUS color model/01595/barrel_side/other/0.75/R` | label | centred | orange | 211 111 247 150 | found | 0.6319 | 1.6534 | 0.3347 | barrel_side/other 0.75 (hidden 0.697) |
| scene | `CAMPUS color model/01598/barrel_low/other/0.5/L` | label | hidden_side | orange | 210 112 249 154 | found | 0.7696 | 1.9061 | 0.5883 | barrel_low/other 0.5 (hidden 0.329) |
| scene | `CAMPUS color model/01751/barrel_low/other/0.75/R` | label | whole_stripe | blue | 226 120 269 177 | found | 0.7928 | 1.6297 | 0.5961 | barrel_low/other 0.75 (hidden 0.613) |
| scene | `HOME color model/00275/barrel_side/other/0.75/R` | label | hidden_side | blue | 440 119 491 178 | found | 0.7986 | 1.517 | 0.3059 | barrel_side/other 0.75 (hidden 0.752) |
| scene | `HOME color model/00287/barrel_side/same/0.5/L` | label | body_span | blue | 455 120 503 185 | off | 0.7778 | 1.8589 | 0.4817 | barrel_side/same 0.5 (hidden 0.547) |
| scene | `HOME color model/00289/barrel_side/same/0.75/L` | label | whole_stripe | blue | 430 120 497 187 | found | 0.788 | 1.7952 | 0.5053 | barrel_side/same 0.75 (hidden 0.841) |
| scene | `HOME color model/00507/barrel_side/other/0.5/R` | label | centred | orange | 384 111 425 157 | second | 0.815 | 1.5899 | 0.3639 | barrel_side/other 0.5 (hidden 0.411) |
| scene | `HOME color model/00585/barrel_side/other/0.5/R` | label | whole_stripe | blue | 420 117 474 175 | found | 0.7753 | 1.631 | 0.5847 | barrel_side/other 0.5 (hidden 0.433) |
| scene | `HOME color model/00587/barrel_side/other/0.75/R` | label | whole_stripe | blue | 421 117 476 164 | off | 0.7422 | 1.7003 | 0.5554 | barrel_side/other 0.75 (hidden 0.68) |
| scene | `HOME color model/00683/barrel_low/same/0.5/L` | label | hidden_side | orange | 312 107 344 136 | found | 0.733 | 1.9189 | 0.559 | barrel_low/same 0.5 (hidden 0.463) |
| scene | `HOME color model/00687/barrel_front/same/0.25/` | label | whole_stripe | blue | 314 112 349 159 | wrong_color | 0.7682 | 1.5888 | 0.4754 | barrel_front/same 0.25 (hidden 0.258) |
| scene | `HOME color model/00843/barrel_front/same/0.25/` | label | whole_stripe | orange | 419 117 471 170 | wrong_color | 0.839 | 1.673 | 0.5662 | barrel_front/same 0.25 (hidden 0.348) |
| scene | `HOME color model/00845/barrel_front/same/0.75/` | label | hidden_side | orange | 444 104 477 141 | wrong_color | 0.7919 | 1.5696 | 0.4152 | barrel_front/same 0.75 (hidden 0.867) |
| scene | `HOME color model/00899/barrel_side/other/0.75/R` | label | whole_stripe | orange | 241 122 283 174 | found | 0.7179 | 1.588 | 0.4651 | barrel_side/other 0.75 (hidden 0.709) |
| scene | `HOME hand masks/00819/barrel_side/other/0.5/R` | label | centred | blue | 428 108 462 139 | found | 0.866 | 1.5391 | 0.479 | barrel_side/other 0.5 (hidden 0.433) |
| scene | `HOME hand masks/00844/barrel_front/same/0.5/` | label | centred | orange | 429 112 471 160 | wrong_color | 0.969 | 1.5408 | 0.5741 | barrel_front/same 0.5 (hidden 0.357) |

