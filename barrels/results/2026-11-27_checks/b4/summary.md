# Does the adopted stage 11 still catch B4's traps? (addendum 2)

Leave one place out, the standard rule. Today's default = fixed colors, stage 11 off (with stage 11: the same boxes on every train frame: True).
(i) = folds pick on the detector before stage 11, as bluer_geom did; (ii) = folds pick with stage 11 in the detector.

| baseline | candidate | verdict | found, placements | per frame | gained / lost | boxes not on their barrel (per frame) | empty: clean / cluttered | places that moved |
|---|---|---|---|---|---|---|---|---|
| today | B4_i_off | **FAIL** | 133.80 → 145.72 | 211 → 257 | 46 / 0 | 1.93 → 6.68 (5 → 24) | 0 → 0 / 0.00 → 1.25 | home_bathtile 4 → 14.25; home_ottoman 3 → 4.66667 |
| today | B4_i_on | **FAIL** | 133.80 → 145.72 | 211 → 257 | 46 / 0 | 1.93 → 6.18 (5 → 22) | 0 → 0 / 0.00 → 0.75 | home_bathtile 4 → 14.25; home_ottoman 3 → 4.66667 |
| today | B4_ii_on | **FAIL** | 133.80 → 145.72 | 211 → 257 | 46 / 0 | 1.93 → 6.18 (5 → 22) | 0 → 0 / 0.00 → 0.75 | home_bathtile 4 → 14.25; home_ottoman 3 → 4.66667 |
| B4_i_off | B4_i_on | **NO CLEAR DIFFERENCE** | 145.72 → 145.72 | 257 → 257 | 0 / 0 | 6.68 → 6.18 (24 → 22) | 0 → 0 / 1.25 → 0.75 |  |
| today | D0.20_i_off | **FAIL** | 133.80 → 143.80 | 211 → 251 | 40 / 0 | 1.93 → 3.93 (5 → 13) | 0 → 0 / 0.00 → 0.75 | home_bathtile 4 → 14 |
| today | D0.20_i_on | **PASS** | 133.80 → 143.80 | 211 → 251 | 40 / 0 | 1.93 → 3.43 (5 → 11) | 0 → 0 / 0.00 → 0.25 | home_bathtile 4 → 14 |
| today | D0.20_ii_on | **PASS** | 133.80 → 145.80 | 211 → 257 | 46 / 0 | 1.93 → 3.43 (5 → 11) | 0 → 0 / 0.00 → 0.25 | home_bathtile 4 → 14; home_ottoman 3 → 5 |
| D0.20_i_off | D0.20_i_on | **NO CLEAR DIFFERENCE** | 143.80 → 143.80 | 251 → 251 | 0 / 0 | 3.93 → 3.43 (13 → 11) | 0 → 0 / 0.75 → 0.25 |  |

## Every box not on its barrel drawn by (i) without stage 11 (ordinary frames)

| family | # | frame | state | color | rule | box | round 1: solid / stripe / body → removes at P | round 2: solid / stripe / body | stage 11 removes |
|---|---|---|---|---|---|---|---|---|---|
| B4 | 1 | lampmid3_bathtile_clutter_01 | nothing | orange | whole_stripe | 516 102 551 134 | 0.2827 / 0.5306 / 0.2074 → yes | 0.4167 / 0.1769 / 0.2074 | no |
| B4 | 2 | lampmid3_bathtile_clutter_01 | nothing | orange | cap | 529 100 557 127 | 0.3203 / nan / 0.2304 → yes | 0.5521 / nan / 0.2304 | no |
| B4 | 3 | lampmid3_bathtile_core_01 | second | orange | cap | 218 104 256 145 | 0.7408 / nan / 0.4655 → no | 0.8554 / nan / 0.4655 | no |
| B4 | 4 | lampmid3_bathtile_neg_02 | nothing | blue | whole_stripe | 529 105 569 142 | 0.327 / 0.4684 / 0.1742 → yes | 0.3894 / 0.29 / 0.2077 | **yes** |
| B4 | 5 | lampmid3_bathtile_occl_02 | nothing | orange | centred | 529 113 574 157 | 0.3904 / 1.3342 / 0.2347 → yes | 0.5547 / 1.1263 / 0.2258 | no |
| B4 | 6 | lampmid3_glass_occl_02 | nothing | orange | whole_stripe | 577 117 636 167 | 0.3918 / 1.651 / 0.1893 → yes | 0.4976 / 1.2737 / 0.1955 | no |
| B4 | 7 | lampmid6_bathtile_neg_02 | nothing | orange | whole_stripe | 527 117 578 160 | 0.4663 / 1.4035 / 0.3572 → yes | 0.6495 / 1.2995 / 0.3611 | no |
| B4 | 8 | lampmid6_bathtile_occl_02 | nothing | orange | cap | 369 102 399 132 | 0.4219 / nan / 0.2848 → no | 0.5524 / nan / 0.2848 | no |
| B4 | 9 | lampmid6_bathtile_occl_02 | nothing | orange | whole_stripe | 526 112 579 160 | 0.4811 / 1.4244 / 0.2749 → yes | 0.6687 / 1.1782 / 0.2847 | no |
| B4 | 10 | lampmid6_glass_clutter_01 | nothing | orange | centred | 554 117 604 171 | 0.6853 / 1.5253 / 0.5133 → yes | 0.8098 / 0.7076 / 0.4921 | no |
| B4 | 11 | lampwarm6_bathtile_clutter_01 | wrong_color | orange | centred | 294 117 340 166 | 0.7181 / 0.747 / 0.242 → no | 0.865 / 0.6806 / 0.2874 | no |
| B4 | 12 | lampwarm6_bathtile_core_01 | nothing | orange | body_span | 465 101 495 134 | 0.7136 / 1.2664 / 0.3635 → yes | 0.7438 / 1.2664 / 0.5182 | no |
| B4 | 13 | lampwarm6_bathtile_neg_02 | nothing | blue | whole_stripe | 305 95 332 121 | 0.386 / 1.1251 / 0.7119 → yes | 0.829 / 0.4432 / 0.7381 | no |
| B4 | 14 | lampwarm6_bathtile_neg_02 | nothing | orange | whole_stripe | 527 111 581 160 | 0.3909 / 1.3149 / 0.3654 → yes | 0.4665 / 1.0246 / 0.3754 | no |
| B4 | 15 | lampwarm6_bathtile_neg_02 | nothing | orange | cap | 544 100 576 135 | 0.2341 / nan / 0.26 → yes | 0.361 / nan / 0.26 | **yes** |
| B4 | 16 | lampwarm6_bathtile_occl_02 | nothing | blue | cap | 165 91 182 107 | 0.1961 / nan / 0.2513 → yes | 0.7725 / nan / 0.2513 | no |
| B4 | 17 | lampwarm6_bathtile_occl_02 | nothing | orange | whole_stripe | 172 95 195 118 | 0.184 / 1.4422 / 0.408 → yes | 0.5861 / 0.4573 / 0.3956 | no |
| B4 | 18 | lampwarm6_bathtile_occl_02 | nothing | orange | centred | 298 105 327 133 | 0.1934 / 0.9563 / 0.1198 → yes | 0.7809 / 0.9563 / 0.1333 | no |
| B4 | 19 | lampwarm6_bathtile_occl_02 | nothing | blue | whole_stripe | 299 96 321 121 | 0.2358 / 0.9453 / 0.6313 → yes | 0.9538 / 0.4237 / 0.617 | no |
| B4 | 20 | lampwarm6_bathtile_occl_02 | nothing | orange | hidden_side | 310 98 336 126 | 0.1704 / 1.6217 / 0.1374 → yes | 0.7455 / 1.195 / 0.2143 | no |
| B4 | 21 | lampwarm6_bathtile_occl_02 | nothing | orange | whole_stripe | 527 111 580 161 | 0.421 / 1.3342 / 0.4096 → yes | 0.6013 / 1.1263 / 0.4551 | no |
| B4 | 22 | lampwarm6_glass_clutter_01 | nothing | orange | centred | 555 117 605 172 | 0.7056 / 1.5253 / 0.5277 → yes | 0.817 / 0.7076 / 0.5153 | no |
| B4 | 23 | lampwarm6_ottoman_touch_01 | wrong_color | blue | hidden_side | 298 131 357 184 | 0.7093 / 0.6523 / 0.2932 → no | 0.7697 / 0.1198 / 0.7319 | no |
| B4 | 24 | overheaddim_palewood_core_01 | nothing | orange | closeup | 235 273 564 480 | 0.3418 / nan / 0.2792 → yes | 0.5066 / nan / 0.2792 | no |
| D0.20 | 25 | lampmid3_bathtile_core_01 | second | orange | cap | 218 104 256 145 | 0.7091 / nan / 0.4655 → no | 0.8308 / nan / 0.4655 | no |
| D0.20 | 26 | lampmid3_glass_occl_02 | nothing | orange | whole_stripe | 577 117 636 167 | 0.3918 / 1.651 / 0.1893 → yes | 0.4976 / 1.2737 / 0.1955 | no |
| D0.20 | 27 | lampmid6_bathtile_neg_02 | nothing | orange | whole_stripe | 529 117 578 158 | 0.246 / 1.3233 / 0.3398 → yes | 0.374 / 0.9607 / 0.3568 | **yes** |
| D0.20 | 28 | lampmid6_bathtile_occl_02 | nothing | orange | cap | 369 102 399 132 | 0.42 / nan / 0.2848 → no | 0.5583 / nan / 0.2848 | no |
| D0.20 | 29 | lampmid6_glass_clutter_01 | nothing | orange | centred | 554 117 604 171 | 0.6853 / 1.5253 / 0.5133 → yes | 0.8098 / 0.7076 / 0.4921 | no |
| D0.20 | 30 | lampwarm6_bathtile_clutter_01 | wrong_color | orange | centred | 294 117 340 166 | 0.6927 / 0.6806 / 0.2363 → no | 0.8495 / 0.6142 / 0.2801 | no |
| D0.20 | 31 | lampwarm6_bathtile_neg_02 | nothing | orange | centred | 528 111 571 160 | 0.3789 / 1.143 / 0.3763 → yes | 0.4691 / 0.932 / 0.372 | no |
| D0.20 | 32 | lampwarm6_bathtile_neg_02 | nothing | orange | cap | 544 100 576 135 | 0.2574 / nan / 0.26 → yes | 0.3484 / nan / 0.26 | **yes** |
| D0.20 | 33 | lampwarm6_bathtile_occl_02 | nothing | blue | body_span | 301 96 320 121 | 0.2362 / 1.0757 / 0.5851 → yes | 0.8723 / 0.5541 / 0.6353 | no |
| D0.20 | 34 | lampwarm6_bathtile_occl_02 | nothing | orange | centred | 531 111 577 163 | 0.3711 / 1.1783 / 0.3752 → yes | 0.5306 / 0.4611 / 0.4071 | no |
| D0.20 | 35 | lampwarm6_glass_clutter_01 | nothing | orange | centred | 555 117 605 172 | 0.7056 / 1.5253 / 0.5277 → yes | 0.817 / 0.7076 / 0.5153 | no |
| D0.20 | 36 | lampwarm6_ottoman_core_01 | nothing | orange | closeup | 166 248 282 480 | 0.7852 / nan / 0.1111 → no | 0.8131 / nan / 0.1111 | no |
| D0.20 | 37 | overheaddim_palewood_core_01 | nothing | orange | closeup | 235 273 564 480 | 0.3418 / nan / 0.2792 → yes | 0.5066 / nan / 0.2792 | no |
