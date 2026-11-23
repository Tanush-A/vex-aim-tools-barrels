# The sweep: how wide the working ranges are, where they sit, and the non-monotone cases (2026-11-25, step 2)

`python barrels/experiments/2026-11-25_color/sweep.py` then `analyse_sweep.py`. The 45 slider-labelled train frames (15 conditions, 5 places with slider labels). Working = every barrel found at his values still found, no more false boxes, outside paint at most max(150 px, 10 %) more (the 2026-11-24 PREREG definition); one threshold at a time, the others at his values; blue hue now swept over 0-179, orange high up to 90, the V gate 0-150, the horizon row 0-150.

## 1. Ranges per place (ordinary conditions; intersection over the place's labelled frames)

| threshold | fixed | abp_gray | home_bathtile | home_glass | home_ottoman | uc_palewood | fixed inside (frames) |
|---|---:|---|---|---|---|---|---:|
| orange_h_lo | 3 | -5..0 (w 15) | **empty** (9>7) (w 6) | **empty** (6>-4) (w 26) | -1..8 (w 43) | -3..6 (w 12) | 31 of 42 |
| orange_h_hi | 13 | 17..90 (w 89) | **empty** (11>10) (w 6) | **empty** (12>10) (w 7) | 18..90 (w 75) | **empty** (13>11) (w 14) | 22 of 42 |
| orange_s_lo | 140 | **empty** (180>171) (w 66) | **empty** (201>174) (w 44) | 153..180 (w 90) | **empty** (180>153) (w 42) | 168..198 (w 54) | 19 of 42 |
| blue_h_lo | 103 | 23..111 (w 90) | **empty** (89>68) (w 54) | 105..106 (w 86) | 86..101 (w 70) | 105..108 (w 34) | 31 of 42 |
| blue_h_hi | 119 | **empty** (120>118) (w 10) | **empty** (138>111) (w 29) | **empty** (112>111) (w 4) | 110..111 (w 46) | 111..122 (w 56) | 21 of 42 |
| blue_s_lo | 113 | **empty** (171>144) (w 75) | **empty** (54>12) (w 62) | **empty** (204>183) (w 72) | **empty** (98>18) (w 81) | 42..132 (w 195) | 18 of 42 |
| v_min | 40 | 35..75 (w 85) | 40..45 (w 52) | 35..50 (w 115) | 40..40 (w 30) | 0..60 (w 115) | 42 of 42 |
| horizon_row | 50 | 0..120 (w 130) | 0..110 (w 120) | 0..100 (w 120) | 0..100 (w 130) | 0..90 (w 120) | 42 of 42 |

Cell = the values that work on every labelled frame of the place (intersection), and the median width of the frames' own ranges. An empty intersection = the place's frames want different values for this threshold (usually clutter against no clutter).

**Why each end stopped** (ordinary frames):

| threshold | low end | high end |
|---|---|---|
| orange_h_lo | outside paint 21, open 21 | barrel lost 37, open 4, false box 1 |
| orange_h_hi | barrel lost 35, false box 4, open 3 | outside paint 20, open 18, barrel lost 2, false box 2 |
| orange_s_lo | outside paint 38, open 2, false box 2 | barrel lost 36, false box 3, open 3 |
| blue_h_lo | outside paint 26, false box 7, open 7, barrel lost 2 | barrel lost 38, open 3, false box 1 |
| blue_h_hi | barrel lost 38, open 3, false box 1 | outside paint 27, open 10, barrel lost 3, false box 2 |
| blue_s_lo | outside paint 20, open 15, barrel lost 4, false box 3 | barrel lost 36, false box 3, open 3 |
| v_min | outside paint 20, open 20, barrel lost 1, false box 1 | barrel lost 36, open 5, false box 1 |
| horizon_row | open 42 | barrel lost 33, open 6, false box 3 |

**One value for all places?** Per threshold, the values inside the intersection of EVERY ordinary place (empty = no constant fits every place's labelled frames one at a time):

- orange_h_lo: all frames 9..-4 (empty); inside the most frames' ranges: 7..7 (32 of 42 frames); fixed 3 inside 31.
- orange_h_hi: all frames 18..10 (empty); inside the most frames' ranges: 10..10 (27 of 42 frames); fixed 13 inside 22.
- orange_s_lo: all frames 201..153 (empty); inside the most frames' ranges: 180..180 (33 of 42 frames); fixed 140 inside 19.
- blue_h_lo: all frames 105..68 (empty); inside the most frames' ranges: 89..90 (35 of 42 frames); fixed 103 inside 31.
- blue_h_hi: all frames 138..111 (empty); inside the most frames' ranges: 111..111 (34 of 42 frames); fixed 119 inside 21.
- blue_s_lo: all frames 204..12 (empty); inside the most frames' ranges: 102..105 (21 of 42 frames); fixed 113 inside 18.
- v_min: all frames 40..40; inside the most frames' ranges: 40..40 (42 of 42 frames); fixed 40 inside 42.
- horizon_row: all frames 0..90; inside the most frames' ranges: 0..90 (42 of 42 frames); fixed 50 inside 42.

## 2. Do the ranges hold together?

150 random settings inside each frame's box of one-at-a-time ranges, all eight numbers moved at once: median share working 0.76 (min 0.38, max 0.99) over 42 ordinary frames; at least 0.9 on 4, under 0.7 on 15 (lampcool6_bathtile_occl_02, lampcool6_glass_core_01, lampcool6_glass_occl_02, lampcool6_ottoman_clutter_01, lampcool6_ottoman_core_01, lampmid3_bathtile_clutter_01, lampmid3_bathtile_occl_02, lampmid3_glass_clutter_01, lampmid6_bathtile_core_01, lampmid6_bathtile_occl_02, lampwarm6_bathtile_core_01, lampwarm6_glass_clutter_01, overheaddim_palewood_occl_02, window_glass_clutter_01, window_glass_occl_02).

## 3. Non-monotone cases: more paint, a barrel lost

138 events on 35 frames (a barrel found at one value and lost one step looser; each value of each threshold and gate, from strict to loose). 90 of them added at most 150 px of paint outside the boxes: the barrel was lost from its OWN extra paint, not from the table gluing on.

**By kind and the detector check behind it:**

| kind | check | events | of which outside paint <= 150 px | params |
|---|---|---:|---:|---|
| box moved | bottom edge (bottom edge) | 65 | 41 | blue_s_lo 21, orange_s_lo 19, v_min 12, blue_h_hi 4 |
| box gone | stripe:height | 16 | 14 | orange_s_lo 11, blue_s_lo 3, blue_h_hi 1, blue_h_lo 1 |
| box moved | bottom edge (left edge) | 10 | 4 | orange_s_lo 3, orange_h_hi 3, blue_s_lo 2, v_min 1 |
| box gone | half:height | 7 | 6 | v_min 2, blue_s_lo 2, orange_h_hi 1, blue_h_lo 1 |
| box gone | barrel:side_unexplained | 7 | 4 | blue_s_lo 4, orange_h_hi 1, orange_s_lo 1, blue_h_lo 1 |
| box gone | half:width | 6 | 5 | orange_h_hi 3, horizon_row 2, orange_s_lo 1 |
| box gone | stripe:area | 6 | 6 | blue_h_hi 2, blue_s_lo 2, blue_h_lo 2 |
| box moved | IoU (left edge) | 5 | 3 | orange_s_lo 2, orange_h_lo 1, blue_h_hi 1, v_min 1 |
| color flip | cap:width | 4 | 2 | orange_h_lo 1, orange_s_lo 1, blue_h_lo 1, horizon_row 1 |
| box gone | half:thicker_than_body | 3 | 2 | v_min 2, orange_h_lo 1 |
| box moved | IoU (right edge) | 3 | 0 | blue_s_lo 2, blue_h_lo 1 |
| box gone | barrel:slice_not_full | 1 | 1 | blue_s_lo 1 |
| box moved | bottom edge (top edge) | 1 | 0 | orange_h_hi 1 |
| box moved | bottom edge (right edge) | 1 | 1 | orange_h_hi 1 |
| box moved | IoU (top edge) | 1 | 0 | orange_s_lo 1 |
| box gone | barrel:outline_unknown | 1 | 1 | horizon_row 1 |
| color flip | barrel:slice_not_full | 1 | 0 | orange_s_lo 1 |

The part of the detector that made the box at the stricter value: barrel 113, half 20, cap 5.

**The list for the detector work** (events with at most 150 px more outside paint, i.e. the barrel's own extra paint lost it; all in `events.csv`):

| frame | barrel | param from -> to | kind | check | box change | IoU / bottom err (tol) | core gain |
|---|---|---|---|---|---|---|---:|
| lampwarm6_ottoman_clutter_01 | #2 blue (occluded) | horizon_row 120 -> 110 | box gone | barrel:outline_unknown |  | 0.0 /  () | +0.000 |
| lampcool6_bathtile_clutter_01 | #4 orange | blue_s_lo 177 -> 174 | box gone | barrel:side_unexplained |  | 0.0 /  () | +0.016 |
| lampcool6_ottoman_clutter_01 | #2 blue (occluded) | blue_s_lo 174 -> 171 | box gone | barrel:side_unexplained |  | 0.0 /  () | +0.025 |
| overheaddim_palewood_occl_02 | #1 orange (occluded) | orange_s_lo 189 -> 186 | box gone | barrel:side_unexplained |  | 0.0 /  () | +0.006 |
| overheaddim_palewood_occl_02 | #1 orange (occluded) | blue_h_lo 113 -> 111 | box gone | barrel:side_unexplained |  | 0.0 /  () | +0.000 |
| both_abpgray_clutter_01 | #4 orange | blue_s_lo 246 -> 243 | box gone | barrel:slice_not_full |  | 0.0 /  () | +0.026 |
| both_abpgray_clutter_01 | #3 blue | v_min 135 -> 130 | box gone | half:height |  | 0.0 /  () | +0.036 |
| lampcool6_bathtile_clutter_01 | #1 blue | blue_s_lo 195 -> 192 | box gone | half:height |  | 0.0 /  () | +0.024 |
| lampcool6_ottoman_clutter_01 | #1 blue | v_min 135 -> 130 | box gone | half:height |  | 0.0 /  () | +0.078 |
| lampmid6_bathtile_clutter_01 | #1 blue | blue_s_lo 99 -> 96 | box gone | half:height |  | 0.0 /  () | +0.017 |
| lampwarm6_bathtile_clutter_01 | #1 blue | blue_h_lo 50 -> 48 | box gone | half:height |  | 0.0 /  () | +0.027 |
| lampwarm6_bathtile_clutter_01 | #1 blue | blue_h_hi 168 -> 170 | box gone | half:height |  | 0.0 /  () | +0.003 |
| both_abpgray_clutter_01 | #2 orange (occluded) | orange_h_lo 6 -> 5 | box gone | half:thicker_than_body |  | 0.0 /  () | +0.106 |
| lampwarm6_ottoman_core_01 | #3 blue | v_min 65 -> 60 | box gone | half:thicker_than_body |  | 0.0 /  () | +0.048 |
| both_abpgray_core_01 | #1 orange | orange_h_hi -1 -> 0 | box gone | half:width |  | 0.0 /  () | +0.126 |
| lampmid3_glass_clutter_01 | #4 orange | horizon_row 150 -> 140 | box gone | half:width |  | 0.0 /  () | +0.003 |
| lampmid6_ottoman_core_01 | #2 orange | orange_h_hi 11 -> 12 | box gone | half:width |  | 0.0 /  () | +0.025 |
| overheaddim_palewood_clutter_01 | #4 orange (truncated) | orange_h_hi 5 -> 6 | box gone | half:width |  | 0.0 /  () | +0.069 |
| window_glass_clutter_01 | #4 orange | horizon_row 150 -> 140 | box gone | half:width |  | 0.0 /  () | +0.003 |
| lampmid3_bathtile_clutter_01 | #3 orange | blue_h_hi 106 -> 108 | box gone | stripe:area |  | 0.0 /  () | +0.032 |
| lampmid3_glass_clutter_01 | #4 orange | blue_s_lo 243 -> 240 | box gone | stripe:area |  | 0.0 /  () | +0.008 |
| lampmid6_ottoman_clutter_01 | #4 orange (occluded,bottom_estimated) | blue_h_lo 107 -> 105 | box gone | stripe:area |  | 0.0 /  () | +0.248 |
| lampwarm6_bathtile_core_01 | #1 orange | blue_h_lo 58 -> 56 | box gone | stripe:area |  | 0.0 /  () | +0.006 |
| lampwarm6_bathtile_core_01 | #1 orange | blue_h_hi 156 -> 158 | box gone | stripe:area |  | 0.0 /  () | +0.000 |
| lampwarm6_ottoman_clutter_01 | #3 orange | blue_s_lo 69 -> 66 | box gone | stripe:area |  | 0.0 /  () | +0.030 |
| lampcool6_bathtile_clutter_01 | #3 orange | blue_s_lo 129 -> 126 | box gone | stripe:height |  | 0.0 /  () | +0.006 |
| lampmid3_bathtile_core_01 | #2 orange | orange_s_lo 42 -> 39 | box gone | stripe:height |  | 0.0 /  () | +0.003 |
| lampmid3_bathtile_core_01 | #1 orange | blue_s_lo 66 -> 63 | box gone | stripe:height |  | 0.0 /  () | +0.017 |
| lampmid3_bathtile_occl_02 | #1 orange (occluded) | blue_h_hi 128 -> 130 | box gone | stripe:height |  | 0.0 /  () | +0.000 |
| lampmid3_bathtile_occl_02 | #1 orange (occluded) | blue_s_lo 25 -> 24 | box gone | stripe:height |  | 0.0 /  () | +0.000 |
| lampmid3_glass_clutter_01 | #2 blue (occluded) | orange_s_lo 207 -> 204 | box gone | stripe:height |  | 0.0 /  () | +0.032 |
| lampmid3_glass_core_01 | #1 orange (occluded) | orange_s_lo 51 -> 48 | box gone | stripe:height |  | 0.12 /  () | +0.000 |
| lampmid6_bathtile_core_01 | #4 blue | orange_s_lo 225 -> 222 | box gone | stripe:height |  | 0.0 /  () | +0.154 |
| lampmid6_bathtile_core_01 | #2 orange | blue_h_lo 102 -> 100 | box gone | stripe:height |  | 0.0 /  () | +0.108 |
| lampmid6_ottoman_core_01 | #3 blue | orange_s_lo 222 -> 219 | box gone | stripe:height |  | 0.0 /  () | +0.030 |
| lampwarm6_glass_clutter_01 | #3 orange | orange_s_lo 207 -> 204 | box gone | stripe:height |  | 0.0 /  () | +0.019 |
| lampwarm6_glass_core_01 | #4 blue | orange_s_lo 222 -> 219 | box gone | stripe:height |  | 0.0 /  () | +0.066 |
| overheaddim_palewood_core_01 | #2 blue | orange_s_lo 228 -> 225 | box gone | stripe:height |  | 0.0 /  () | +0.088 |
| window_glass_clutter_01 | #2 blue (occluded) | orange_s_lo 204 -> 201 | box gone | stripe:height |  | 0.0 /  () | +0.027 |
| lampcool6_bathtile_clutter_01 | #3 orange | orange_h_lo 15 -> 14 | box moved |  IoU | left +6 px | 0.42 / 1 (3.3) | +0.030 |
| lampmid6_ottoman_clutter_01 | #2 blue (occluded) | blue_h_hi 117 -> 119 | box moved |  IoU | left +23 px | 0.47 / -1 (4.7) | +0.004 |
| lampwarm6_glass_core_01 | #4 blue | v_min 140 -> 135 | box moved |  IoU | left +9 px | 0.35 / -1 (4.0) | +0.042 |
| both_abpgray_clutter_01 | #1 blue (occluded) | v_min 145 -> 140 | box moved | bottom edge | bottom -6 px | 0.77 / -11 (7.1) | +0.028 |
| both_abpgray_clutter_01 | #3 blue | v_min 115 -> 110 | box moved | bottom edge | bottom -9 px | 0.7 / -11 (5.9) | +0.023 |
| both_abpgray_core_01 | #3 blue | blue_h_hi 132 -> 134 | box moved | bottom edge | bottom +2 px | 0.84 / 5 (3.8) | +0.003 |
| both_abpgray_core_01 | #2 blue | v_min 125 -> 120 | box moved | bottom edge | bottom -15 px | 0.75 / -27 (13.4) | +0.022 |
| lampcool6_bathtile_clutter_01 | #2 blue | v_min 90 -> 85 | box moved | bottom edge | left +6 px | 0.65 / -5 (4.1) | +0.067 |
| lampcool6_glass_clutter_01 | #3 orange | orange_s_lo 57 -> 54 | box moved | bottom edge | bottom +2 px | 0.66 / 5 (3) | +0.000 |
| lampcool6_glass_clutter_01 | #2 blue (occluded) | blue_s_lo 111 -> 108 | box moved | bottom edge | bottom +2 px | 0.75 / 5 (4.9) | +0.000 |
| lampcool6_glass_core_01 | #4 blue | blue_s_lo 93 -> 90 | box moved | bottom edge | left -1 px | 0.78 / 5 (4.0) | +0.000 |
| lampcool6_glass_core_01 | #2 blue | blue_s_lo 81 -> 78 | box moved | bottom edge | bottom +3 px | 0.79 / 7 (6.2) | +0.000 |
| lampcool6_glass_occl_02 | #1 blue (occluded) | blue_s_lo 105 -> 102 | box moved | bottom edge | bottom +1 px | 0.8 / 5 (4.9) | +0.000 |
| lampcool6_ottoman_clutter_01 | #4 orange (occluded,bottom_estimated) | orange_s_lo 186 -> 183 | box moved | bottom edge | bottom -10 px | 0.72 / -17 (7.3) | +0.028 |
| lampcool6_ottoman_clutter_01 | #4 orange (occluded,bottom_estimated) | blue_s_lo 150 -> 147 | box moved | bottom edge | bottom -11 px | 0.63 / -16 (7.3) | +0.015 |
| lampcool6_ottoman_clutter_01 | #4 orange (occluded,bottom_estimated) | blue_s_lo 132 -> 129 | box moved | bottom edge | bottom -11 px | 0.65 / -16 (7.3) | +0.005 |
| lampcool6_ottoman_clutter_01 | #2 blue (occluded) | v_min 40 -> 35 | box moved | bottom edge | bottom +5 px | 0.71 / 5 (4.7) | +0.001 |
| lampcool6_ottoman_core_01 | #1 blue | orange_s_lo 219 -> 216 | box moved | bottom edge | left +9 px | 0.69 / -11 (7.5) | +0.035 |
| lampcool6_ottoman_core_01 | #1 blue | v_min 110 -> 105 | box moved | bottom edge | bottom -11 px | 0.65 / -16 (7.5) | +0.066 |
| lampmid3_bathtile_clutter_01 | #2 blue | blue_s_lo 63 -> 60 | box moved | bottom edge | bottom -6 px | 0.76 / -5 (4.1) | +0.011 |
| lampmid3_bathtile_clutter_01 | #1 blue | blue_s_lo 45 -> 42 | box moved | bottom edge | bottom -12 px | 0.73 / -14 (7.6) | +0.025 |
| lampmid3_glass_clutter_01 | #3 orange | orange_s_lo 69 -> 66 | box moved | bottom edge | bottom +2 px | 0.62 / 5 (3) | +0.000 |
| lampmid3_glass_clutter_01 | #4 orange | orange_s_lo 54 -> 51 | box moved | bottom edge | bottom +1 px | 0.64 / 6 (5.1) | +0.000 |
| lampmid3_glass_clutter_01 | #2 blue (occluded) | blue_s_lo 99 -> 96 | box moved | bottom edge | bottom +2 px | 0.85 / 5 (4.9) | +0.000 |
| lampmid3_glass_core_01 | #4 blue | blue_s_lo 75 -> 72 | box moved | bottom edge | left -1 px | 0.76 / 5 (4.0) | +0.000 |
| lampmid3_glass_core_01 | #2 blue | blue_s_lo 63 -> 60 | box moved | bottom edge | bottom +3 px | 0.81 / 7 (6.2) | +0.000 |
| lampmid3_glass_occl_02 | #1 blue (occluded) | blue_s_lo 90 -> 87 | box moved | bottom edge | bottom +1 px | 0.85 / 5 (4.9) | +0.000 |
| lampmid6_bathtile_clutter_01 | #1 blue | blue_s_lo 81 -> 78 | box moved | bottom edge | bottom -12 px | 0.75 / -15 (7.6) | +0.012 |
| lampmid6_glass_clutter_01 | #4 orange | orange_s_lo 84 -> 81 | box moved | bottom edge | bottom +3 px | 0.75 / 7 (5.1) | +0.000 |
| lampmid6_glass_clutter_01 | #3 orange | orange_s_lo 81 -> 78 | box moved | bottom edge | bottom +1 px | 0.7 / 4 (3) | +0.000 |
| lampmid6_glass_clutter_01 | #2 blue (occluded) | blue_s_lo 84 -> 81 | box moved | bottom edge | bottom +2 px | 0.84 / 5 (4.9) | +0.000 |
| lampmid6_glass_core_01 | #4 blue | blue_s_lo 51 -> 48 | box moved | bottom edge | bottom +1 px | 0.79 / 5 (4.0) | +0.000 |
| lampmid6_ottoman_clutter_01 | #4 orange (occluded,bottom_estimated) | orange_h_hi 16 -> 17 | box moved | bottom edge | right +15 px | 0.7 / -16 (7.3) | +0.064 |
| lampmid6_ottoman_clutter_01 | #4 orange (occluded,bottom_estimated) | orange_s_lo 192 -> 189 | box moved | bottom edge | bottom -10 px | 0.74 / -16 (7.3) | +0.014 |
| lampmid6_ottoman_clutter_01 | #4 orange (occluded,bottom_estimated) | blue_s_lo 108 -> 105 | box moved | bottom edge | bottom -11 px | 0.63 / -16 (7.3) | +0.015 |
| lampmid6_ottoman_clutter_01 | #1 blue | v_min 110 -> 105 | box moved | bottom edge | bottom -8 px | 0.68 / -17 (9.5) | +0.048 |
| lampmid6_ottoman_clutter_01 | #2 blue (occluded) | v_min 70 -> 65 | box moved | bottom edge | bottom -7 px | 0.69 / -6 (4.7) | +0.014 |
| lampmid6_ottoman_core_01 | #1 blue | v_min 100 -> 95 | box moved | bottom edge | bottom -10 px | 0.65 / -15 (7.5) | +0.044 |
| lampmid6_ottoman_core_01 | #3 blue | v_min 85 -> 80 | box moved | bottom edge | bottom -6 px | 0.66 / -7 (4.7) | +0.043 |
| lampwarm6_bathtile_clutter_01 | #1 blue | blue_s_lo 39 -> 36 | box moved | bottom edge | bottom -1 px | 0.85 / -8 (7.6) | +0.028 |
| lampwarm6_bathtile_core_01 | #3 blue | blue_h_lo 36 -> 34 | box moved | bottom edge | bottom -10 px | 0.71 / -14 (8.6) | +0.052 |
| lampwarm6_glass_clutter_01 | #4 orange | orange_s_lo 96 -> 93 | box moved | bottom edge | bottom +1 px | 0.65 / 6 (5.1) | +0.000 |
| lampwarm6_glass_core_01 | #4 blue | blue_s_lo 33 -> 30 | box moved | bottom edge | bottom +1 px | 0.79 / 5 (4.0) | +0.000 |
| lampwarm6_glass_core_01 | #1 orange (occluded) | v_min 145 -> 140 | box moved | bottom edge | bottom +7 px | 0.68 / 6 (4.0) | +0.056 |
| lampwarm6_ottoman_core_01 | #3 blue | orange_h_lo 14 -> 13 | box moved | bottom edge | bottom -7 px | 0.79 / -8 (4.7) | +0.059 |
| lampwarm6_ottoman_core_01 | #2 orange | blue_h_hi 100 -> 102 | box moved | bottom edge | bottom -21 px | 0.77 / -22 (14.5) | +0.037 |
| overheaddim_palewood_core_01 | #1 orange | blue_s_lo 240 -> 237 | box moved | bottom edge | bottom -8 px | 0.79 / -9 (8.6) | +0.034 |
| window_glass_core_01 | #3 orange | orange_s_lo 42 -> 39 | box moved | bottom edge | bottom +1 px | 0.91 / 8 (7.8) | +0.000 |
| window_glass_occl_02 | #1 blue (occluded) | blue_s_lo 120 -> 117 | box moved | bottom edge | bottom +1 px | 0.75 / 5 (4.9) | +0.000 |
| overheaddim_palewood_clutter_01 | #1 blue (occluded,bottom_estimated) | orange_s_lo 225 -> 222 | color flip | cap:width |  | 0.27 /  () | +0.089 |
| overheaddim_palewood_clutter_01 | #1 blue (occluded,bottom_estimated) | blue_h_lo 109 -> 107 | color flip | cap:width |  | 0.0 /  () | +0.185 |
