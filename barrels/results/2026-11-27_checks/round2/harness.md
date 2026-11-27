# The proof harness with the paint checks on (yardstick H)

`harness.py`: 5435 masks. Before = today's boxes (`before.json`). Scored where the truth is known: masks made from a train frame against its hand boxes (261 of 261 frames have box labels), the 3888 simulated scenes against their own true boxes. A check only takes boxes away. Removed boxes by what they were before: F = on its barrel and found, O = on its barrel with the box off, W = wrong color on a barrel, S = a second box on a barrel, N = on nothing; unscored = a mask with no truth.

## S: solid paint only, solidity under 0.40 dropped (P)

| group | inputs changed | boxes removed | removed by what they were: F / O / W / S / N / unscored | barrels found (strict) before → after | found → box off | lost (no box left on it) | boxes not on their barrel before → after |
|---|---|---|---|---|---|---|---|
| damage | 0 / 666 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 803 → 803 of 1152 | 0 | 0 | 7 → 7 |
| hand | 0 / 45 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 115 → 115 of 135 | 0 | 0 | 1 → 1 |
| pool | 0 / 53 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 91 → 91 of 93 | 0 | 0 | 0 → 0 |
| real | 0 / 261 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 224 → 224 of 537 | 0 | 0 | 9 → 9 |
| real_dilate | 0 / 261 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 234 → 234 of 537 | 0 | 0 | 18 → 18 |
| real_erode | 0 / 261 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 181 → 181 of 537 | 0 | 0 | 2 → 2 |
| scene | 0 / 3888 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 4177 → 4177 of 5376 | 0 | 0 | 21 → 21 |
| **all** | 0 / 5435 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 5825 → 5825 of 8367 | 0 | 0 | 58 → 58 |

## L: label only, stripe over 1.25 x a stripe height with body under 0.6 dropped (P)

| group | inputs changed | boxes removed | removed by what they were: F / O / W / S / N / unscored | barrels found (strict) before → after | found → box off | lost (no box left on it) | boxes not on their barrel before → after |
|---|---|---|---|---|---|---|---|
| damage | 7 / 666 | 7 | 0 / 0 / 7 / 0 / 0 / 0 | 803 → 803 of 1152 | 0 | 0 | 7 → 0 |
| hand | 0 / 45 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 115 → 115 of 135 | 0 | 0 | 1 → 1 |
| pool | 0 / 53 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 91 → 91 of 93 | 0 | 0 | 0 → 0 |
| real | 2 / 261 | 2 | 0 / 0 / 1 / 0 / 1 / 0 | 224 → 224 of 537 | 0 | 0 | 9 → 7 |
| real_dilate | 2 / 261 | 2 | 0 / 0 / 0 / 0 / 2 / 0 | 234 → 234 of 537 | 0 | 0 | 18 → 16 |
| real_erode | 2 / 261 | 2 | 0 / 0 / 2 / 0 / 0 / 0 | 181 → 181 of 537 | 0 | 0 | 2 → 0 |
| scene | 12 / 3888 | 12 | 3 / 4 / 4 / 1 / 0 / 0 | 4177 → 4174 of 5376 | 0 | 7 | 21 → 16 |
| **all** | 25 / 5435 | 25 | 3 / 4 / 14 / 1 / 3 / 0 | 5825 → 5822 of 8367 | 0 | 7 | 58 → 40 |

Every box removed (all groups):

| group | input | why | rule | color | box | before | solid | stripe h | body share | scene |
|---|---|---|---|---|---|---|---|---|---|---|
| damage | `light/1/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.5477 | 1.3543 | 0.408 |  |
| damage | `white tables, bad day/0/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 220 101 248 136 | wrong_color | 0.6033 | 1.3698 | 0.419 |  |
| damage | `white tables, bad day/1/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 101 247 136 | wrong_color | 0.5732 | 1.3698 | 0.421 |  |
| damage | `white tables, bad day/2/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 222 101 248 136 | wrong_color | 0.6229 | 1.3698 | 0.419 |  |
| damage | `white tables, typical/0/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.671 | 1.3392 | 0.414 |  |
| damage | `white tables, typical/1/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.671 | 1.3392 | 0.414 |  |
| damage | `white tables, typical/2/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.671 | 1.3392 | 0.414 |  |
| real | `4A8B_lampcool6_wood_occl_02` | label | body_span | orange | 186 131 261 215 | wrong_color | 0.8094 | 1.3092 | 0.4845 |  |
| real | `4A8B_lampmid3_glass_occl_02` | label | whole_stripe | orange | 577 117 636 167 | nothing | 0.4976 | 1.2737 | 0.1955 |  |
| real_dilate | `4A8B_lampmid3_glass_occl_02` | label | whole_stripe | orange | 559 122 609 167 | nothing | 0.7631 | 1.4781 | 0.5339 |  |
| real_dilate | `4A8B_lampmid6_glass_occl_02` | label | centred | orange | 558 119 611 176 | nothing | 0.7156 | 1.4794 | 0.4253 |  |
| real_erode | `4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.671 | 1.3392 | 0.414 |  |
| real_erode | `4A8B_overheaddim_palewood_core_01` | label | whole_stripe | orange | 438 107 476 150 | wrong_color | 0.8174 | 1.4545 | 0.3146 |  |
| scene | `CAMPUS color model/00353/barrel_low/other/0.75/R` | label | body_span | orange | 248 110 279 148 | found | 0.8078 | 1.4285 | 0.4638 | barrel_low/other 0.75 (hidden 0.584) |
| scene | `CAMPUS color model/00503/barrel_side/other/0.75/R` | label | whole_stripe | orange | 397 133 460 199 | found | 0.9534 | 1.3566 | 0.5815 | barrel_side/other 0.75 (hidden 0.59) |
| scene | `CAMPUS color model/00682/barrel_front/same/0.5/` | label | centred | orange | 233 113 278 163 | wrong_color | 0.9402 | 1.4728 | 0.4251 | barrel_front/same 0.5 (hidden 0.456) |
| scene | `CAMPUS color model/01438/barrel_side/other/0.75/L` | label | body_span | orange | 345 113 384 163 | off | 0.8975 | 1.5651 | 0.5424 | barrel_side/other 0.75 (hidden 0.681) |
| scene | `HOME color model/00507/barrel_side/other/0.5/R` | label | centred | orange | 384 111 425 157 | second | 0.9479 | 1.5151 | 0.4711 | barrel_side/other 0.5 (hidden 0.411) |
| scene | `HOME color model/00584/barrel_side/other/0.5/L` | label | hidden_side | blue | 404 117 449 163 | off | 0.8703 | 1.3149 | 0.5808 | barrel_side/other 0.5 (hidden 0.457) |
| scene | `HOME color model/00586/barrel_side/other/0.75/L` | label | body_span | blue | 423 117 474 163 | off | 0.8599 | 1.3832 | 0.5769 | barrel_side/other 0.75 (hidden 0.71) |
| scene | `HOME color model/00687/barrel_front/same/0.25/` | label | whole_stripe | blue | 314 112 349 159 | wrong_color | 0.8665 | 1.4281 | 0.4754 | barrel_front/same 0.25 (hidden 0.258) |
| scene | `HOME color model/00749/barrel_low/other/0.75/R` | label | whole_stripe | orange | 335 102 360 135 | found | 0.7627 | 1.3392 | 0.5011 | barrel_low/other 0.75 (hidden 0.733) |
| scene | `HOME color model/00843/barrel_front/same/0.25/` | label | whole_stripe | orange | 419 117 471 170 | wrong_color | 0.8955 | 1.673 | 0.5918 | barrel_front/same 0.25 (hidden 0.348) |
| scene | `HOME color model/00845/barrel_front/same/0.75/` | label | hidden_side | orange | 444 104 477 141 | wrong_color | 0.8124 | 1.4786 | 0.4714 | barrel_front/same 0.75 (hidden 0.867) |
| scene | `HOME color model/00898/barrel_side/other/0.75/L` | label | whole_stripe | orange | 244 114 287 164 | off | 0.834 | 1.3636 | 0.4138 | barrel_side/other 0.75 (hidden 0.812) |

## SL: both, at P (0.40; 1.25 / 0.6)

| group | inputs changed | boxes removed | removed by what they were: F / O / W / S / N / unscored | barrels found (strict) before → after | found → box off | lost (no box left on it) | boxes not on their barrel before → after |
|---|---|---|---|---|---|---|---|
| damage | 7 / 666 | 7 | 0 / 0 / 7 / 0 / 0 / 0 | 803 → 803 of 1152 | 0 | 0 | 7 → 0 |
| hand | 0 / 45 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 115 → 115 of 135 | 0 | 0 | 1 → 1 |
| pool | 0 / 53 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 91 → 91 of 93 | 0 | 0 | 0 → 0 |
| real | 2 / 261 | 2 | 0 / 0 / 1 / 0 / 1 / 0 | 224 → 224 of 537 | 0 | 0 | 9 → 7 |
| real_dilate | 2 / 261 | 2 | 0 / 0 / 0 / 0 / 2 / 0 | 234 → 234 of 537 | 0 | 0 | 18 → 16 |
| real_erode | 2 / 261 | 2 | 0 / 0 / 2 / 0 / 0 / 0 | 181 → 181 of 537 | 0 | 0 | 2 → 0 |
| scene | 12 / 3888 | 12 | 3 / 4 / 4 / 1 / 0 / 0 | 4177 → 4174 of 5376 | 0 | 7 | 21 → 16 |
| **all** | 25 / 5435 | 25 | 3 / 4 / 14 / 1 / 3 / 0 | 5825 → 5822 of 8367 | 0 | 7 | 58 → 40 |

Every box removed (all groups):

| group | input | why | rule | color | box | before | solid | stripe h | body share | scene |
|---|---|---|---|---|---|---|---|---|---|---|
| damage | `light/1/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.5477 | 1.3543 | 0.408 |  |
| damage | `white tables, bad day/0/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 220 101 248 136 | wrong_color | 0.6033 | 1.3698 | 0.419 |  |
| damage | `white tables, bad day/1/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 101 247 136 | wrong_color | 0.5732 | 1.3698 | 0.421 |  |
| damage | `white tables, bad day/2/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 222 101 248 136 | wrong_color | 0.6229 | 1.3698 | 0.419 |  |
| damage | `white tables, typical/0/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.671 | 1.3392 | 0.414 |  |
| damage | `white tables, typical/1/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.671 | 1.3392 | 0.414 |  |
| damage | `white tables, typical/2/CAMPUS color model/4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.671 | 1.3392 | 0.414 |  |
| real | `4A8B_lampcool6_wood_occl_02` | label | body_span | orange | 186 131 261 215 | wrong_color | 0.8094 | 1.3092 | 0.4845 |  |
| real | `4A8B_lampmid3_glass_occl_02` | label | whole_stripe | orange | 577 117 636 167 | nothing | 0.4976 | 1.2737 | 0.1955 |  |
| real_dilate | `4A8B_lampmid3_glass_occl_02` | label | whole_stripe | orange | 559 122 609 167 | nothing | 0.7631 | 1.4781 | 0.5339 |  |
| real_dilate | `4A8B_lampmid6_glass_occl_02` | label | centred | orange | 558 119 611 176 | nothing | 0.7156 | 1.4794 | 0.4253 |  |
| real_erode | `4A8B_campus_light_room_03` | label | whole_stripe | blue | 219 102 248 136 | wrong_color | 0.671 | 1.3392 | 0.414 |  |
| real_erode | `4A8B_overheaddim_palewood_core_01` | label | whole_stripe | orange | 438 107 476 150 | wrong_color | 0.8174 | 1.4545 | 0.3146 |  |
| scene | `CAMPUS color model/00353/barrel_low/other/0.75/R` | label | body_span | orange | 248 110 279 148 | found | 0.8078 | 1.4285 | 0.4638 | barrel_low/other 0.75 (hidden 0.584) |
| scene | `CAMPUS color model/00503/barrel_side/other/0.75/R` | label | whole_stripe | orange | 397 133 460 199 | found | 0.9534 | 1.3566 | 0.5815 | barrel_side/other 0.75 (hidden 0.59) |
| scene | `CAMPUS color model/00682/barrel_front/same/0.5/` | label | centred | orange | 233 113 278 163 | wrong_color | 0.9402 | 1.4728 | 0.4251 | barrel_front/same 0.5 (hidden 0.456) |
| scene | `CAMPUS color model/01438/barrel_side/other/0.75/L` | label | body_span | orange | 345 113 384 163 | off | 0.8975 | 1.5651 | 0.5424 | barrel_side/other 0.75 (hidden 0.681) |
| scene | `HOME color model/00507/barrel_side/other/0.5/R` | label | centred | orange | 384 111 425 157 | second | 0.9479 | 1.5151 | 0.4711 | barrel_side/other 0.5 (hidden 0.411) |
| scene | `HOME color model/00584/barrel_side/other/0.5/L` | label | hidden_side | blue | 404 117 449 163 | off | 0.8703 | 1.3149 | 0.5808 | barrel_side/other 0.5 (hidden 0.457) |
| scene | `HOME color model/00586/barrel_side/other/0.75/L` | label | body_span | blue | 423 117 474 163 | off | 0.8599 | 1.3832 | 0.5769 | barrel_side/other 0.75 (hidden 0.71) |
| scene | `HOME color model/00687/barrel_front/same/0.25/` | label | whole_stripe | blue | 314 112 349 159 | wrong_color | 0.8665 | 1.4281 | 0.4754 | barrel_front/same 0.25 (hidden 0.258) |
| scene | `HOME color model/00749/barrel_low/other/0.75/R` | label | whole_stripe | orange | 335 102 360 135 | found | 0.7627 | 1.3392 | 0.5011 | barrel_low/other 0.75 (hidden 0.733) |
| scene | `HOME color model/00843/barrel_front/same/0.25/` | label | whole_stripe | orange | 419 117 471 170 | wrong_color | 0.8955 | 1.673 | 0.5918 | barrel_front/same 0.25 (hidden 0.348) |
| scene | `HOME color model/00845/barrel_front/same/0.75/` | label | hidden_side | orange | 444 104 477 141 | wrong_color | 0.8124 | 1.4786 | 0.4714 | barrel_front/same 0.75 (hidden 0.867) |
| scene | `HOME color model/00898/barrel_side/other/0.75/L` | label | whole_stripe | orange | 244 114 287 164 | off | 0.834 | 1.3636 | 0.4138 | barrel_side/other 0.75 (hidden 0.812) |

## Sm: solid paint only, under 0.35 (M)

| group | inputs changed | boxes removed | removed by what they were: F / O / W / S / N / unscored | barrels found (strict) before → after | found → box off | lost (no box left on it) | boxes not on their barrel before → after |
|---|---|---|---|---|---|---|---|
| damage | 0 / 666 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 803 → 803 of 1152 | 0 | 0 | 7 → 7 |
| hand | 0 / 45 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 115 → 115 of 135 | 0 | 0 | 1 → 1 |
| pool | 0 / 53 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 91 → 91 of 93 | 0 | 0 | 0 → 0 |
| real | 0 / 261 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 224 → 224 of 537 | 0 | 0 | 9 → 9 |
| real_dilate | 0 / 261 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 234 → 234 of 537 | 0 | 0 | 18 → 18 |
| real_erode | 0 / 261 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 181 → 181 of 537 | 0 | 0 | 2 → 2 |
| scene | 0 / 3888 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 4177 → 4177 of 5376 | 0 | 0 | 21 → 21 |
| **all** | 0 / 5435 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 5825 → 5825 of 8367 | 0 | 0 | 58 → 58 |

## Lm: label only, over 1.5 x with body under 0.6 (M)

| group | inputs changed | boxes removed | removed by what they were: F / O / W / S / N / unscored | barrels found (strict) before → after | found → box off | lost (no box left on it) | boxes not on their barrel before → after |
|---|---|---|---|---|---|---|---|
| damage | 0 / 666 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 803 → 803 of 1152 | 0 | 0 | 7 → 7 |
| hand | 0 / 45 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 115 → 115 of 135 | 0 | 0 | 1 → 1 |
| pool | 0 / 53 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 91 → 91 of 93 | 0 | 0 | 0 → 0 |
| real | 0 / 261 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 224 → 224 of 537 | 0 | 0 | 9 → 9 |
| real_dilate | 0 / 261 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 234 → 234 of 537 | 0 | 0 | 18 → 18 |
| real_erode | 0 / 261 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 181 → 181 of 537 | 0 | 0 | 2 → 2 |
| scene | 3 / 3888 | 3 | 0 / 1 / 1 / 1 / 0 / 0 | 4177 → 4177 of 5376 | 0 | 1 | 21 → 19 |
| **all** | 3 / 5435 | 3 | 0 / 1 / 1 / 1 / 0 / 0 | 5825 → 5825 of 8367 | 0 | 1 | 58 → 56 |

Every box removed (all groups):

| group | input | why | rule | color | box | before | solid | stripe h | body share | scene |
|---|---|---|---|---|---|---|---|---|---|---|
| scene | `CAMPUS color model/01438/barrel_side/other/0.75/L` | label | body_span | orange | 345 113 384 163 | off | 0.8975 | 1.5651 | 0.5424 | barrel_side/other 0.75 (hidden 0.681) |
| scene | `HOME color model/00507/barrel_side/other/0.5/R` | label | centred | orange | 384 111 425 157 | second | 0.9479 | 1.5151 | 0.4711 | barrel_side/other 0.5 (hidden 0.411) |
| scene | `HOME color model/00843/barrel_front/same/0.25/` | label | whole_stripe | orange | 419 117 471 170 | wrong_color | 0.8955 | 1.673 | 0.5918 | barrel_front/same 0.25 (hidden 0.348) |

## SLm: both, at M (0.35; 1.5 / 0.6)

| group | inputs changed | boxes removed | removed by what they were: F / O / W / S / N / unscored | barrels found (strict) before → after | found → box off | lost (no box left on it) | boxes not on their barrel before → after |
|---|---|---|---|---|---|---|---|
| damage | 0 / 666 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 803 → 803 of 1152 | 0 | 0 | 7 → 7 |
| hand | 0 / 45 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 115 → 115 of 135 | 0 | 0 | 1 → 1 |
| pool | 0 / 53 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 91 → 91 of 93 | 0 | 0 | 0 → 0 |
| real | 0 / 261 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 224 → 224 of 537 | 0 | 0 | 9 → 9 |
| real_dilate | 0 / 261 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 234 → 234 of 537 | 0 | 0 | 18 → 18 |
| real_erode | 0 / 261 | 0 | 0 / 0 / 0 / 0 / 0 / 0 | 181 → 181 of 537 | 0 | 0 | 2 → 2 |
| scene | 3 / 3888 | 3 | 0 / 1 / 1 / 1 / 0 / 0 | 4177 → 4177 of 5376 | 0 | 1 | 21 → 19 |
| **all** | 3 / 5435 | 3 | 0 / 1 / 1 / 1 / 0 / 0 | 5825 → 5825 of 8367 | 0 | 1 | 58 → 56 |

Every box removed (all groups):

| group | input | why | rule | color | box | before | solid | stripe h | body share | scene |
|---|---|---|---|---|---|---|---|---|---|---|
| scene | `CAMPUS color model/01438/barrel_side/other/0.75/L` | label | body_span | orange | 345 113 384 163 | off | 0.8975 | 1.5651 | 0.5424 | barrel_side/other 0.75 (hidden 0.681) |
| scene | `HOME color model/00507/barrel_side/other/0.5/R` | label | centred | orange | 384 111 425 157 | second | 0.9479 | 1.5151 | 0.4711 | barrel_side/other 0.5 (hidden 0.411) |
| scene | `HOME color model/00843/barrel_front/same/0.25/` | label | whole_stripe | orange | 419 117 471 170 | wrong_color | 0.8955 | 1.673 | 0.5918 | barrel_front/same 0.25 (hidden 0.348) |

