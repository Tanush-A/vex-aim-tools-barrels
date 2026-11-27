# B4's boxes that are not on their barrel, measured (in-sample, all eight places; never a verdict)

B4 = the light experiment's candidate, each place under the setting its own fold picked. 283 boxes on the 154 ordinary train frames: 259 on a real barrel (found or box off), 24 not on their barrel. Measurements: `stages.measure` (definitions in `stages.py`).

## The real barrels: the spread of each measurement

| measurement | n | min | 1 % | 5 % | median | 95 % | 99 % | max |
|---|---|---|---|---|---|---|---|---|
| w_ratio | 259 | 0.29 | 0.46 | 0.62 | 0.99 | 1.17 | 1.20 | 1.21 |
| h_ratio | 259 | 0.30 | 0.53 | 0.82 | 0.99 | 1.10 | 1.14 | 1.17 |
| seen_w_ratio | 254 | 0.00 | 0.26 | 0.39 | 0.95 | 1.35 | 1.53 | 1.58 |
| fill | 259 | 0.25 | 0.30 | 0.37 | 0.77 | 0.86 | 0.90 | 0.94 |
| body_fill | 259 | 0.17 | 0.23 | 0.32 | 0.76 | 0.86 | 0.88 | 0.88 |
| top_err | 259 | -0.33 | -0.31 | -0.30 | 0.04 | 0.12 | 0.14 | 0.65 |
| bot_err | 259 | -0.70 | -0.69 | -0.23 | 0.02 | 0.10 | 0.29 | 0.30 |
| stripe_h_ratio | 235 | 0.25 | 0.41 | 0.52 | 0.79 | 1.15 | 1.74 | 1.92 |
| stripe_over_body | 235 | 0.06 | 0.09 | 0.12 | 0.19 | 0.28 | 0.42 | 0.51 |
| up_share | 259 | 0.00 | 0.03 | 0.26 | 0.77 | 0.90 | 0.97 | 0.99 |
| low_share | 242 | 0.00 | 0.00 | 0.20 | 0.83 | 0.95 | 0.98 | 0.99 |
| bands_alike | 242 | 0.00 | 0.00 | 0.10 | 0.91 | 0.99 | 1.00 | 1.00 |
| bulge_top | 253 | 0.00 | 0.07 | 0.21 | 0.95 | 1.93 | 4.09 | 11.25 |
| bulge_bot | 253 | 0.02 | 0.09 | 0.39 | 0.95 | 2.12 | 5.01 | 9.25 |
| aspect | 259 | 0.29 | 0.41 | 0.59 | 1.05 | 1.47 | 2.40 | 2.94 |
| stripe_w_ratio | 235 | 0.24 | 0.31 | 0.42 | 0.88 | 1.01 | 1.12 | 1.32 |
| ring_left | 248 | 0.00 | 0.00 | 0.00 | 0.02 | 0.71 | 0.85 | 0.87 |
| ring_right | 256 | 0.00 | 0.00 | 0.00 | 0.01 | 0.70 | 0.79 | 0.86 |
| ring_lr_min | 259 | 0.00 | 0.00 | 0.00 | 0.00 | 0.39 | 0.61 | 0.68 |
| ring_top | 259 | 0.00 | 0.00 | 0.00 | 0.00 | 0.41 | 0.71 | 1.00 |
| solid | 259 | 0.40 | 0.48 | 0.61 | 0.81 | 0.96 | 0.98 | 0.99 |

Real barrels by the rule that drew them: whole_stripe 159, hidden_side 34, body_span 33, closeup 16, centred 7, cap 5, half_stripe 2, closeup_stripe 1, outline 1, thin_frame 1

## Every box not on its barrel

| # | frame | state | also with fixed colors | color | rule | box | w_ratio | h_ratio | seen_w_ratio | fill | body_fill | top_err | bot_err | stripe_h_ratio | stripe_over_body | up_share | low_share | bands_alike | bulge_top | bulge_bot | aspect | stripe_w_ratio | ring_left | ring_right | ring_lr_min | ring_top | solid |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | lampmid3_bathtile_clutter_01 | nothing | False | orange | whole_stripe | 516,102 35x32 | 1.17 | 0.98 | 0.27 | 0.21 | 0.21 | -0.05 | 0.26 | 0.53 | 0.10 | 0.08 | 0.36 | 0.22 | 1.00 | 10.75 | 1.05 | 1.17 | 0.30 | 0.12 | 0.12 | 0.04 | 0.28 |
| 2 | lampmid3_bathtile_clutter_01 | nothing | False | orange | cap | 529,100 28x27 | 1.01 | 0.89 | 0.22 | 0.20 | 0.23 | -0.00 | -0.11 |  |  | 0.10 | 0.34 | 0.31 |  |  | 1.42 |  | 0.26 | 0.15 | 0.15 | 0.00 | 0.32 |
| 3 | lampmid3_bathtile_core_01 | second | False | orange | cap | 218,104 38x41 | 1.16 | 1.15 | 1.22 | 0.65 | 0.47 | 0.00 | 0.43 |  |  | 0.42 | 0.71 | 0.60 | 0.43 | 0.53 | 0.94 |  | 0.03 | 0.59 | 0.03 | 0.00 | 0.74 |
| 4 | lampmid3_bathtile_neg_02 | nothing | False | blue | whole_stripe | 529,105 40x37 | 1.17 | 0.99 | 1.67 | 0.25 | 0.17 | 0.70 | 0.18 | 0.47 | 0.23 | 0.05 | 0.38 | 0.12 | 0.56 | 0.17 | 2.91 | 0.91 | 0.53 | 0.09 | 0.09 | 0.04 | 0.33 |
| 5 | lampmid3_bathtile_occl_02 | nothing | False | orange | centred | 529,113 45x44 | 1.01 | 0.91 | 0.54 | 0.36 | 0.23 | -0.21 | -0.12 | 1.33 | 0.29 | 0.16 | 0.16 | 0.97 | 0.00 | 0.47 | 1.04 | 0.70 | 0.65 | 0.03 | 0.03 | 0.03 | 0.39 |
| 6 | lampmid3_glass_occl_02 | nothing | True | orange | whole_stripe | 577,117 59x50 | 1.19 | 0.93 | 0.42 | 0.31 | 0.19 | 0.24 | -0.09 | 1.65 | 0.58 | 0.09 | 0.15 | 0.59 | 0.58 | 0.83 | 1.98 | 1.05 | 0.33 | 0.41 | 0.33 | 0.00 | 0.39 |
| 7 | lampmid6_bathtile_neg_02 | nothing | False | orange | whole_stripe | 527,117 51x43 | 1.14 | 0.89 | 0.85 | 0.49 | 0.36 | -0.21 | -0.14 | 1.40 | 0.31 | 0.24 | 0.23 | 0.96 | 0.00 | 0.44 | 1.29 | 0.81 | 0.75 | 0.00 | 0.00 | 0.01 | 0.47 |
| 8 | lampmid6_bathtile_occl_02 | nothing | False | orange | cap | 369,102 30x30 | 0.99 | 0.91 | 0.56 | 0.28 | 0.28 | -0.18 | -0.24 |  |  | 0.31 | 0.22 | 0.72 | 0.00 | 0.33 | 1.30 |  | 0.80 | 0.00 | 0.00 | 0.06 | 0.42 |
| 9 | lampmid6_bathtile_occl_02 | nothing | False | orange | whole_stripe | 526,112 53x48 | 1.21 | 1.01 | 0.87 | 0.43 | 0.27 | 0.15 | -0.01 | 1.42 | 0.41 | 0.23 | 0.21 | 0.89 | 0.59 | 0.34 | 1.52 | 0.84 | 0.65 | 0.00 | 0.00 | 0.00 | 0.48 |
| 10 | lampmid6_glass_clutter_01 | nothing | True | orange | centred | 554,117 50x54 | 1.01 | 1.01 | 0.95 | 0.59 | 0.51 | 0.06 | -0.09 | 1.53 | 0.42 | 0.45 | 0.25 | 0.55 | 1.00 | 0.83 | 1.47 | 0.77 | 0.90 | 0.41 | 0.41 | 0.05 | 0.69 |
| 11 | lampwarm6_bathtile_clutter_01 | wrong_color | False | orange | centred | 294,117 46x49 | 0.99 | 0.97 | 0.86 | 0.48 | 0.24 | -0.22 | -0.15 | 0.75 | 0.17 | 0.44 | 0.05 | 0.11 | 0.20 | 0.16 | 1.18 | 0.56 | 0.13 | 0.10 | 0.10 | 0.64 | 0.72 |
| 12 | lampwarm6_bathtile_core_01 | nothing | False | orange | body_span | 465,101 30x33 | 1.03 | 1.03 | 0.85 | 0.44 | 0.36 | 0.18 | 0.03 | 1.27 | 0.36 | 0.08 | 0.90 | 0.09 | 0.00 | 1.26 | 1.50 | 0.58 | 0.09 | 0.65 | 0.09 | 0.00 | 0.71 |
| 13 | lampwarm6_bathtile_neg_02 | nothing | False | blue | whole_stripe | 305,95 27x26 | 1.23 | 1.08 | 0.64 | 0.65 | 0.71 | -0.34 | 0.07 | 1.13 | 0.19 | 0.80 | 0.68 | 0.85 | 1.53 | 1.47 | 1.04 | 0.96 | 0.64 | 0.48 | 0.48 | 0.62 | 0.39 |
| 14 | lampwarm6_bathtile_neg_02 | nothing | False | orange | whole_stripe | 527,111 54x49 | 1.19 | 1.00 | 0.57 | 0.37 | 0.37 | -0.26 | -0.12 | 1.31 | 0.28 | 0.29 | 0.30 | 0.97 | 0.73 | 1.03 | 1.28 | 0.84 | 0.74 | 0.02 | 0.02 | 0.16 | 0.39 |
| 15 | lampwarm6_bathtile_neg_02 | nothing | False | orange | cap | 544,100 32x35 | 1.15 | 1.16 | 0.36 | 0.27 | 0.26 | -0.13 | -0.08 |  |  | 0.20 | 0.46 | 0.44 | 1.00 | 6.38 | 1.32 |  | 0.28 | 0.16 | 0.16 | 0.05 | 0.23 |
| 16 | lampwarm6_bathtile_occl_02 | nothing | False | blue | cap | 165,91 17x16 | 1.01 | 0.87 | 0.41 | 0.56 | 0.25 | 0.16 | -0.19 |  |  | 0.24 | 0.20 | 0.83 | 1.25 | 1.25 | 1.98 |  | 0.52 | 0.48 | 0.48 | 0.62 | 0.20 |
| 17 | lampwarm6_bathtile_occl_02 | nothing | False | orange | whole_stripe | 172,95 23x23 | 1.08 | 0.99 | 0.56 | 0.47 | 0.41 | -0.29 | 0.26 | 1.44 | 0.23 | 0.55 | 0.33 | 0.59 | 0.86 | 1.14 | 0.88 | 0.99 | 0.70 | 0.39 | 0.39 | 0.57 | 0.18 |
| 18 | lampwarm6_bathtile_occl_02 | nothing | False | orange | centred | 298,105 29x28 | 0.99 | 0.88 | 0.72 | 0.38 | 0.12 | 0.12 | 0.28 | 0.96 | 0.20 | 0.17 | 0.02 | 0.14 | 0.78 | 0.44 | 1.06 | 0.51 | 0.31 | 0.36 | 0.31 | 0.71 | 0.19 |
| 19 | lampwarm6_bathtile_occl_02 | nothing | False | blue | whole_stripe | 299,96 22x25 | 0.96 | 0.99 | 0.61 | 0.67 | 0.63 | -0.32 | -0.01 | 0.95 | 0.18 | 0.64 | 0.56 | 0.87 | 1.92 | 0.92 | 0.93 | 0.83 | 0.69 | 0.61 | 0.61 | 0.70 | 0.24 |
| 20 | lampwarm6_bathtile_occl_02 | nothing | False | orange | hidden_side | 310,98 26x28 | 0.98 | 0.97 | 0.49 | 0.49 | 0.14 | 0.00 | -0.17 | 1.62 | 0.47 | 0.15 | 0.12 | 0.83 | 0.26 | 0.21 | 1.52 | 0.49 | 0.66 | 0.28 | 0.28 | 0.77 | 0.17 |
| 21 | lampwarm6_bathtile_occl_02 | nothing | False | orange | whole_stripe | 527,111 53x50 | 1.19 | 1.03 | 0.63 | 0.43 | 0.41 | -0.36 | -0.02 | 1.33 | 0.24 | 0.35 | 0.45 | 0.79 | 0.47 | 1.27 | 1.05 | 0.83 | 0.71 | 0.01 | 0.01 | 0.11 | 0.42 |
| 22 | lampwarm6_glass_clutter_01 | nothing | True | orange | centred | 555,117 50x55 | 1.01 | 1.03 | 1.15 | 0.61 | 0.53 | -0.32 | -0.07 | 1.53 | 0.29 | 0.44 | 0.32 | 0.72 | 0.21 | 0.83 | 1.01 | 0.77 | 0.90 | 0.57 | 0.57 | 0.19 | 0.71 |
| 23 | lampwarm6_ottoman_touch_01 | wrong_color | False | blue | hidden_side | 298,131 59x53 | 1.00 | 0.83 | 0.41 | 0.45 | 0.29 | 0.10 | -0.07 | 0.65 | 0.18 | 0.80 | 0.27 | 0.34 | 3.30 | 0.90 | 1.51 | 0.30 | 0.69 | 0.28 | 0.28 | 0.03 | 0.71 |
| 24 | overheaddim_palewood_core_01 | nothing | True | orange | closeup | 235,273 329x207 | 0.94 | 0.61 |  | 0.28 | 0.28 | 0.06 | -0.42 |  |  | 0.28 |  |  |  |  | 2.31 |  | 0.10 | 0.07 | 0.07 | 0.07 | 0.34 |

## How far each measurement separates (in-sample)

For each measurement: the false boxes outside the real barrels' range (min..max), and outside 1 %..99 %.

| measurement | false boxes below real min / above real max | below 1 % / above 99 % |
|---|---|---|
| w_ratio | 0 / 1 | 0 / 2 |
| h_ratio | 0 / 0 | 0 / 2 |
| seen_w_ratio | 0 / 1 | 1 / 1 |
| fill | 3 / 0 | 6 / 0 |
| body_fill | 2 / 0 | 6 / 0 |
| top_err | 2 / 1 | 4 / 5 |
| bot_err | 0 / 1 | 0 / 1 |
| stripe_h_ratio | 0 / 0 | 0 / 0 |
| stripe_over_body | 0 / 1 | 0 / 3 |
| up_share | 0 / 0 | 0 / 0 |
| low_share | 0 / 0 | 0 / 0 |
| bands_alike | 0 / 0 | 0 / 0 |
| bulge_top | 0 / 0 | 4 / 0 |
| bulge_bot | 0 / 1 | 0 / 2 |
| aspect | 0 / 0 | 0 / 1 |
| stripe_w_ratio | 0 / 0 | 1 / 1 |
| ring_left | 0 / 2 | 0 / 2 |
| ring_right | 0 / 0 | 0 / 0 |
| ring_lr_min | 0 / 0 | 0 / 1 |
| ring_top | 0 / 0 | 0 / 1 |
| solid | 14 / 0 | 18 / 0 |
