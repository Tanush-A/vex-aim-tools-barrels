# Part D: what correction gains that the ideas which change no pixel do not

Barrels counted per frame, judged ordinary frames, from each candidate's `changes.csv` (the others read from their branches with `git show`). *None of the three* = not gained by contrast C1, near-miss or self-calibration AB.

| candidate | gained | also by contrast C1 | also by near-miss | also by self-cal AB | also by blue-follows-light B1 | by none of the three | lost |
|---|---|---|---|---|---|---|---|
| F1_gray_world | 39 | 32 | 23 | 21 | 9 | 4 | 11 |
| F2_white_patch | 34 | 29 | 22 | 19 | 9 | 4 | 17 |
| F3_without_loose | 50 | 41 | 24 | 26 | 10 | 7 | 7 |
| F4_gray_above | 46 | 38 | 22 | 24 | 9 | 6 | 11 |
| F5_shades_of_gray | 32 | 26 | 20 | 18 | 9 | 5 | 11 |
| P1_gray_world_partial | 38 | 33 | 15 | 18 | 12 | 4 | 6 |
| P2_white_patch_partial | 7 | 5 | 3 | 1 | 0 | 1 | 10 |
| P3_without_loose_partial | 6 | 6 | 5 | 2 | 3 | 0 | 2 |
| P4_gray_above_partial | 30 | 26 | 16 | 15 | 10 | 3 | 7 |
| P5_shades_of_gray_partial | 3 | 2 | 0 | 0 | 2 | 1 | 6 |
| U3_without_loose_added | 7 | 6 | 5 | 3 | 3 | 0 | 1 |

## P1_gray_world_partial: gained by none of the three (4)

- both_abpgray_clutter_01 barrel 2
- lampmid6_bathtile_occl_02 barrel 1
- lampwarm6_bathtile_edge_01 barrel 1
- window_glass_occl_02 barrel 1

## F3_without_loose: gained by none of the three (7)

- lampcool6_ottoman_occl_02 barrel 1
- lampmid3_bathtile_edge_01 barrel 1
- lampmid3_bathtile_occl_02 barrel 1
- lampmid6_bathtile_occl_02 barrel 1
- lampwarm6_ottoman_occl_02 barrel 1
- lampwarm6_ottoman_touch_01 barrel 1
- window_glass_occl_02 barrel 1

## The others, for scale

| idea | gained | lost |
|---|---|---|
| stripe by contrast (C1, +21.5) | 64 | 0 |
| near-miss (B_partner_fit, +13.7) | 38 | 0 |
| self-calibration (AB, +13.8) | 37 | 0 |
| blue follows the light (B1, +3.9) | 14 | 0 |

Union of contrast C1, near-miss and self-calibration AB: 70 barrels gained.
