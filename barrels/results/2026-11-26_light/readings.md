# The readings compared (part A of the 2026-11-26 light experiment)

`python barrels/experiments/2026-11-26_light/measure.py` then `table.py`. Train frames only (the ordinary conditions: 154 frames, 17 conditions, 8 places). In-sample unless a column says leave one place out. A reading is a set of pixels picked without knowing where a barrel is; its number is the median of (R - B) / (R + G + B) over them: 0 = neutral light, positive = yellow. The truth it is compared with is the labelled paint inside the hand boxes (body and stripe bands).

## The one table

| reading | frames it speaks on | r / rho with the blue paint's S (17 conditions) | r / rho with the blue paint's hue | r / rho with the orange paint's hue | leave one place out, blue S: skill (error against the baseline, S units) | leave one place out, blue hue: skill | leave one place out, orange hue: skill | spread inside a condition / between conditions (ratio) | close-up / clutter / empty frame: mean shift from the condition's median | warm-needing frames against the others: AUC | other frames at least as warm as the 10th percentile of the needing ones |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `whole_frame`: the brightest 5 % of the whole frame (the existing rule) | 154 of 154 | -0.95 / -0.91 | -0.68 / -0.83 | 0.54 / 0.73 | 0.70 (36 against 65) | -0.30 | 0.08 | 0.066 / 0.139 (2.1) | 0.102 / 0.024 / 0.011 | 0.979 | 3 of 119 |
| `above_gate`: the brightest 5 % of rows 0-49 (above the horizon gate) | 154 of 154 | -0.95 / -0.87 | -0.75 / -0.78 | 0.38 / 0.63 | 0.83 (27 against 65) | 0.10 | -0.13 | 0.024 / 0.125 (5.3) | -0.007 / 0.000 / 0.013 | 0.997 | 1 of 119 |
| `above_gate20`: the brightest 20 % of rows 0-49 (round 2 of 2026-11-25) | 154 of 154 | -0.96 / -0.89 | -0.71 / -0.78 | 0.44 / 0.66 | 0.83 (27 against 65) | 0.03 | -0.07 | 0.019 / 0.126 (6.7) | -0.007 / -0.004 / 0.007 | 1.000 | 0 of 119 |
| `above_all`: every pixel of rows 0-49 that is not dark | 154 of 154 | -0.86 / -0.86 | -0.72 / -0.82 | 0.28 / 0.58 | 0.70 (35 against 65) | 0.16 | -0.16 | 0.020 / 0.137 (6.9) | -0.004 / -0.005 / 0.002 | 0.972 | 13 of 119 |
| `without_barrels`: the brightest 5 % after taking out what the fixed model paints, grown 15 px | 154 of 154 | -0.96 / -0.90 | -0.74 / -0.83 | 0.47 / 0.73 | 0.90 (21 against 65) | 0.13 | -0.25 | 0.036 / 0.129 (3.6) | 0.037 / -0.006 / 0.010 | 0.993 | 1 of 119 |
| `without_loose`: the brightest 5 % after taking out anything barrel-like under a loose model, grown 15 px | 154 of 154 | -0.96 / -0.88 | -0.73 / -0.79 | 0.42 / 0.67 | 0.89 (21 against 65) | 0.07 | -0.17 | 0.009 / 0.119 (12.5) | -0.005 / -0.002 / 0.001 | 1.000 | 0 of 119 |
| `neutral`: pixels with almost no color (S < 40), middle brightness | 143 of 154 | -0.35 / -0.61 | -0.07 / -0.44 | 0.48 / 0.61 | -0.04 (67 against 66) | -0.00 | -0.06 | 0.011 / 0.022 (1.9) | 0.003 / -0.007 / 0.005 | 0.682 | 90 of 117 |
| `least_colored`: the least colored 10 % of the middle-bright pixels | 154 of 154 | -0.88 / -0.87 | -0.82 / -0.80 | 0.19 / 0.67 | 0.65 (38 against 65) | 0.30 | -1.07 | 0.015 / 0.101 (6.6) | -0.003 / -0.006 / 0.001 | 0.961 | 7 of 119 |
| `highlights`: nearly clipped pixels (brightest channel 225-249) | 116 of 154 | -0.58 / -0.62 | -0.45 / -0.71 | 0.31 / 0.40 | -0.18 (71 against 65) | -0.08 | 0.10 | 0.072 / 0.155 (2.1) | 0.085 / -0.007 / 0.001 | 0.906 | 20 of 92 |
| `near_strip`: the bottom 80 rows (the table nearest the robot) | 153 of 154 | -0.70 / -0.60 | -0.71 / -0.52 | 0.01 / 0.38 | -0.41 (78 against 66) | -0.39 | -0.11 | 0.052 / 0.131 (2.5) | 0.016 / -0.002 / 0.006 | 0.818 | 64 of 118 |
| `gray_world`: every pixel below the gate that is not dark | 154 of 154 | -0.84 / -0.74 | -0.74 / -0.60 | 0.18 / 0.48 | 0.20 (58 against 65) | -0.15 | 0.01 | 0.018 / 0.129 (7.2) | -0.000 / -0.004 / -0.001 | 0.965 | 14 of 119 |
| `max_rgb`: the 99th percentile of each channel | 154 of 154 | -0.96 / -0.85 | -0.76 / -0.84 | 0.41 / 0.68 | 0.90 (21 against 65) | 0.09 | -0.24 | 0.027 / 0.108 (4.0) | 0.011 / 0.013 / 0.011 | 0.992 | 3 of 119 |
| `tiles`: the lower quartile over 4 x 4 tiles of each bright tile's brightest 20 % | 148 of 154 | -0.94 / -0.83 | -0.76 / -0.70 | 0.31 / 0.55 | 0.76 (32 against 65) | 0.02 | -0.09 | 0.017 / 0.126 (7.3) | 0.003 / -0.010 / -0.005 | 0.998 | 0 of 117 |

Warm-needing conditions (the blue paint's 10th percentile of S is under the fixed floor of 113): lampmid3_bathtile, lampmid6_bathtile, lampmid6_ottoman, lampwarm6_bathtile, lampwarm6_ottoman.

## Per condition: the paint, and each reading's mean

| condition | blue S median / 10th pct | blue hue median / 2nd pct | blue brightness, share under the gate | orange hue median / 98th pct | orange S 10th pct | `whole_frame` | `above_gate` | `above_gate20` | `above_all` | `without_barrels` | `without_loose` | `neutral` | `least_colored` | `highlights` | `near_strip` | `gray_world` | `max_rgb` | `tiles` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| both_abpgray | 234 / 221 | 111 / 107 | 141, 0.00 | 1.8 / 5.5 | 220 | -0.01 | 0.00 | -0.01 | -0.01 | -0.01 | -0.01 | -0.00 | -0.00 | -0.01 | 0.05 | 0.06 | -0.00 | -0.01 |
| window_abpwhite | 229 / 212 | 108 / 105 | 178, 0.00 | 8.0 / 25.0 | 183 | 0.02 | -0.03 | -0.04 | -0.01 | 0.02 | 0.02 | 0.01 | -0.00 | 0.09 | 0.07 | 0.04 | 0.01 | -0.01 |
| campus_light | 206 / 150 | 107 / 86 | 97, 0.00 | 7.9 / 27.6 | 177 | -0.01 | -0.01 | -0.02 | -0.01 | -0.01 | -0.01 | -0.00 | -0.00 | 0.00 | -0.03 | -0.00 | -0.00 | -0.01 |
| lampcool6_bathtile | 196 / 160 | 102 / 93 | 77, 0.00 | 9.8 / 13.0 | 211 | 0.15 | 0.08 | 0.07 | 0.19 | 0.08 | 0.08 | 0.01 | 0.08 | 0.40 | 0.11 | 0.12 | 0.11 | 0.08 |
| lampmid3_bathtile (needs) | 48 / 17 | 100 / 3 | 52, 0.06 | 10.0 / 13.0 | 211 | 0.27 | 0.21 | 0.20 | 0.23 | 0.22 | 0.20 | 0.01 | 0.18 | 0.42 | 0.24 | 0.24 | 0.21 | 0.22 |
| lampmid6_bathtile (needs) | 82 / 47 | 100 / 45 | 62, 0.00 | 9.0 / 11.5 | 214 | 0.29 | 0.23 | 0.22 | 0.32 | 0.25 | 0.23 | 0.01 | 0.22 | 0.32 | 0.27 | 0.27 | 0.24 | 0.25 |
| lampwarm6_bathtile (needs) | 44 / 26 | 38 / 6 | 53, 0.00 | 8.0 / 10.5 | 216 | 0.39 | 0.36 | 0.34 | 0.41 | 0.39 | 0.35 | -0.00 | 0.33 | 0.39 | 0.40 | 0.41 | 0.35 | 0.38 |
| lampcool6_glass | 229 / 215 | 109 / 106 | 135, 0.00 | 7.5 / 10.5 | 183 | -0.04 | -0.06 | -0.06 | -0.03 | -0.06 | -0.06 | -0.05 | -0.05 | 0.28 | -0.08 | -0.07 | -0.00 | -0.07 |
| lampmid3_glass | 229 / 209 | 109 / 106 | 139, 0.00 | 7.2 / 9.5 | 183 | -0.01 | -0.05 | -0.04 | 0.00 | -0.03 | -0.04 | -0.04 | -0.03 | 0.26 | -0.05 | -0.04 | 0.01 | -0.04 |
| lampmid6_glass | 226 / 199 | 109 / 106 | 128, 0.00 | 7.5 / 10.0 | 192 | 0.05 | -0.01 | -0.01 | 0.07 | 0.01 | -0.00 | -0.00 | -0.00 | 0.29 | -0.00 | -0.00 | 0.03 | -0.01 |
| lampwarm6_glass | 216 / 182 | 109 / 107 | 124, 0.00 | 7.2 / 9.8 | 196 | 0.05 | 0.01 | 0.03 | 0.15 | 0.04 | 0.04 | 0.03 | 0.02 | 0.31 | 0.04 | 0.04 | 0.05 | 0.03 |
| window_glass | 231 / 216 | 110 / 106 | 150, 0.00 | 6.5 / 9.2 | 174 | -0.05 | -0.06 | -0.07 | -0.05 | -0.05 | -0.06 | -0.03 | -0.05 | -0.03 | -0.10 | -0.08 | -0.02 | -0.08 |
| lampcool6_ottoman | 192 / 153 | 104 / 79 | 98, 0.13 | 16.0 / 20.5 | 177 | 0.13 | 0.02 | 0.03 | 0.03 | 0.08 | 0.03 | 0.02 | 0.01 | 0.19 | 0.00 | 0.02 | 0.06 | -0.01 |
| lampmid6_ottoman (needs) | 140 / 98 | 105 / 79 | 83, 0.19 | 15.2 / 22.2 | 196 | 0.23 | 0.12 | 0.15 | 0.12 | 0.18 | 0.14 | 0.03 | 0.06 | 0.19 | 0.02 | 0.09 | 0.14 | 0.11 |
| lampwarm6_ottoman (needs) | 63 / 34 | 102 / 48 | 54, 0.34 | 14.8 / 22.5 | 201 | 0.31 | 0.22 | 0.25 | 0.20 | 0.28 | 0.26 | 0.01 | 0.07 | 0.24 | 0.05 | 0.17 | 0.22 | 0.22 |
| window_light | 229 / 208 | 110 / 106 | 135, 0.00 | 7.3 / 19.1 | 206 | -0.01 | -0.10 | -0.10 | -0.11 | -0.01 | -0.01 | 0.00 | -0.00 | -0.00 | 0.05 | 0.00 | -0.00 | -0.02 |
| overheaddim_palewood | 224 / 191 | 109 / 105 | 140, 0.01 | 7.5 / 11.2 | 201 | -0.01 | -0.01 | -0.01 | 0.00 | -0.01 | -0.01 | -0.01 | -0.01 | -0.01 | 0.21 | 0.18 | -0.00 | 0.06 |

Extreme conditions (report only; not in any number above):

| condition | blue S median | blue hue median | orange hue median | `whole_frame` | `above_gate` | `above_gate20` | `above_all` | `without_barrels` | `without_loose` | `neutral` | `least_colored` | `highlights` | `near_strip` | `gray_world` | `max_rgb` | `tiles` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lampcool3_wood | 67 | 104 | 13 | 0.04 | 0.04 | 0.04 | 0.05 | 0.05 | 0.04 | 0.03 | 0.05 | n/a | 0.17 | 0.21 | 0.06 | 0.11 |
| lampcool6_wood | 114 | 104 | 12 | 0.07 | 0.04 | 0.05 | 0.05 | 0.05 | 0.04 | 0.03 | 0.05 | 0.12 | 0.19 | 0.24 | 0.05 | 0.13 |
| lampmid3_ottoman | 54 | 52 | 13 | 0.20 | 0.10 | 0.07 | 0.11 | 0.07 | 0.05 | 0.03 | 0.13 | n/a | 0.38 | 0.31 | 0.16 | 0.43 |
| lampmid3_wood | 36 | 106 | 12 | 0.16 | 0.11 | 0.11 | 0.11 | 0.11 | 0.11 | 0.02 | 0.09 | 0.28 | 0.24 | 0.27 | 0.12 | 0.18 |
| lampmid6_wood | 47 | 104 | 10 | 0.22 | 0.13 | 0.14 | 0.15 | 0.21 | 0.13 | 0.01 | 0.14 | 0.22 | 0.32 | 0.36 | 0.13 | 0.24 |
| lampwarm3_wood | 22 | 58 | 13 | 0.22 | 0.16 | 0.16 | 0.16 | 0.17 | 0.16 | 0.01 | 0.12 | 0.33 | 0.33 | 0.34 | 0.17 | 0.23 |
| lampwarm6_wood | 33 | 54 | 10 | 0.30 | 0.22 | 0.23 | 0.24 | 0.30 | 0.22 | 0.01 | 0.19 | 0.32 | 0.38 | 0.42 | 0.22 | 0.33 |
| window_black | 150 | 99 | 23 | 0.00 | 0.01 | 0.01 | 0.01 | 0.00 | 0.00 | 0.02 | 0.00 | 0.00 | 0.10 | 0.01 | 0.00 | -0.01 |

## Where each reading is furthest off (the three frames furthest from their condition's median)

- `whole_frame`: lampcool6_bathtile_close_01 reads 0.50 (its condition 0.09); lampcool6_ottoman_core_01 reads 0.40 (its condition 0.03); lampcool6_ottoman_close_01 reads 0.38 (its condition 0.03)
- `above_gate`: lampwarm6_glass_neg_02 reads 0.20 (its condition -0.02); lampmid6_glass_neg_02 reads 0.07 (its condition -0.03); campus_light_hand_02 reads -0.07 (its condition 0.00)
- `above_gate20`: lampwarm6_glass_neg_02 reads 0.13 (its condition 0.00); campus_light_hand_02 reads -0.08 (its condition 0.00); campus_light_plain_01 reads -0.07 (its condition 0.00)
- `above_all`: window_abpwhite_occlx_01 reads 0.06 (its condition -0.02); window_abpwhite_occlx_02 reads 0.06 (its condition -0.02); campus_light_hand_02 reads -0.07 (its condition 0.00)
- `without_barrels`: lampcool6_ottoman_close_01 reads 0.38 (its condition 0.03); lampmid6_ottoman_close_01 reads 0.38 (its condition 0.16); lampwarm6_ottoman_close_01 reads 0.40 (its condition 0.26)
- `without_loose`: lampwarm6_ottoman_close_01 reads 0.21 (its condition 0.26); window_abpwhite_occlx_19 reads -0.01 (its condition 0.02); campus_light_hand_02 reads -0.03 (its condition -0.00)
- `neutral`: lampmid6_ottoman_edge_01 reads 0.00 (its condition 0.04); lampwarm6_ottoman_touch_01 reads -0.03 (its condition 0.01); lampwarm6_ottoman_close_01 reads 0.04 (its condition 0.01)
- `least_colored`: lampwarm6_ottoman_touch_01 reads -0.03 (its condition 0.08); lampwarm6_ottoman_edge_01 reads 0.18 (its condition 0.08); lampmid6_ottoman_edge_01 reads 0.12 (its condition 0.04)
- `highlights`: window_abpwhite_occlx_18 reads -0.33 (its condition 0.11); lampmid6_ottoman_close_01 reads 0.39 (its condition 0.10); window_abpwhite_occlx_05 reads 0.37 (its condition 0.11)
- `near_strip`: both_abpgray_held_01 reads -0.34 (its condition 0.10); campus_light_held_01 reads -0.42 (its condition -0.01); campus_light_top_01 reads 0.15 (its condition -0.01)
- `gray_world`: lampwarm6_ottoman_edge_01 reads 0.25 (its condition 0.15); lampwarm6_ottoman_touch_01 reads 0.25 (its condition 0.15); lampmid6_ottoman_edge_01 reads 0.14 (its condition 0.07)
- `max_rgb`: lampcool6_ottoman_close_01 reads 0.16 (its condition 0.03); lampwarm6_ottoman_neg_02 reads 0.14 (its condition 0.23); lampcool6_ottoman_core_01 reads 0.13 (its condition 0.03)
- `tiles`: lampcool6_ottoman_clutter_01 reads -0.11 (its condition 0.00); overheaddim_palewood_neg_02 reads 0.01 (its condition 0.07); lampwarm6_ottoman_core_01 reads 0.26 (its condition 0.21)

## Largest shift on a close-up, a clutter and an empty frame (absolute, any condition)

| reading | close-up | clutter | empty |
|---|---|---|---|
| `whole_frame` | 0.42 | 0.10 | 0.08 |
| `above_gate` | 0.03 | 0.01 | 0.22 |
| `above_gate20` | 0.05 | 0.03 | 0.13 |
| `above_all` | 0.05 | 0.04 | 0.05 |
| `without_barrels` | 0.35 | 0.02 | 0.08 |
| `without_loose` | 0.05 | 0.02 | 0.02 |
| `neutral` | 0.03 | 0.03 | 0.03 |
| `least_colored` | 0.02 | 0.02 | 0.01 |
| `highlights` | 0.29 | 0.04 | 0.19 |
| `near_strip` | 0.06 | 0.03 | 0.03 |
| `gray_world` | 0.04 | 0.03 | 0.03 |
| `max_rgb` | 0.12 | 0.07 | 0.10 |
| `tiles` | 0.03 | 0.11 | 0.06 |
