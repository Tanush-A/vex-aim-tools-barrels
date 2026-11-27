# Guard values of painted candidates, in-sample (mode=add,strength_min=1.0; ordinary train frames; exploration, not a verdict)

75 painted candidates on a labelled barrel's stripe (73 ended in a new box); 24 not on one (17 ended in a new box). Candidates inside a box today's detector already drew are left alone and are not listed.

share, strength: the finder's two numbers. d: the feature distance between the body's and the stripe's own colors. orange_part: the red-against-blue value of the part that should be orange. alike_rel, alike_feat: how much the two body bands differ (red-blue channel, relative; color and brightness, in units of d). above, below, left, right: how far what is around the predicted box is from the body color, in units of d.

## Not on a barrel

| frame | color | x, row | on | new box | share | strength | d | orange_part | alike_rel | alike_feat | above | below | left | right |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| both_abpgray_clutter_01 | O | 458, 135 | nothing | yes | 1.00 | 1.10 | 0.92 | 1.40 | 0.11 | 0.12 | 1.29 | 1.19 | 0.95 | 0.76 |
| both_abpgray_neg_02 | B | 459, 123 | nothing | yes | 1.00 | 1.14 | 1.07 | 1.47 | 0.00 | 0.37 | 0.29 | 0.68 | 0.17 | 0.10 |
| campus_light_neg_05 | B | 440, 141 | nothing | yes | 0.76 | 1.12 | 1.35 | 1.67 | 0.52 | 0.50 | 0.13 | 0.21 | 0.25 | 0.27 |
| lampcool6_glass_clutter_01 | O | 124, 196 | nothing | yes | 1.00 | 1.05 | 1.09 | -0.33 | 0.04 | 0.15 | 0.16 | 0.16 | 0.15 | 1.03 |
| lampcool6_glass_neg_02 | O | 126, 196 | nothing | yes | 1.00 | 1.06 | 1.11 | -0.33 | 0.04 | 0.15 | 0.19 | 0.14 | 0.13 | 0.07 |
| lampmid3_bathtile_clutter_01 | O | 528, 119 | nothing | yes | 1.00 | 1.15 | 1.11 | 1.39 | 0.30 | 0.31 | 0.29 | 0.22 | 0.20 | 0.21 |
| lampmid3_bathtile_neg_02 | O | 525, 118 | nothing | yes | 1.00 | 1.09 | 1.03 | 1.49 | 0.19 | 0.48 | 0.28 | 0.09 | 0.30 | 0.32 |
| lampmid3_bathtile_occl_02 | O | 528, 118 | nothing | yes | 1.00 | 1.00 | 0.98 | 1.37 | 0.17 | 0.61 | 0.33 | 0.31 | 0.30 | 0.33 |
| overheaddim_palewood_neg_02 | O | 228, 160 | nothing | yes | 1.00 | 1.61 | 1.81 | 0.24 | 0.23 | 0.23 | 0.15 | 0.05 | 0.07 | 0.04 |
| overheaddim_palewood_neg_02 | B | 159, 123 | nothing | yes | 0.96 | 1.43 | 1.49 | 0.03 | 0.11 | 0.12 | 0.09 | 1.20 | 0.45 | 0.93 |
| overheaddim_palewood_occl_02 | B | 476, 128 | nothing | yes | 0.93 | 1.38 | 1.40 | -0.01 | 0.01 | 0.04 | 0.47 | 1.14 | 0.55 | 0.32 |
| window_abpwhite_occlx_15 | B | 434, 150 | nothing | yes | 0.95 | 0.95 | 0.94 | 1.14 | 0.29 | 0.67 | 0.09 | 0.30 | 0.55 | 0.32 |
| window_glass_clutter_01 | O | 124, 196 | nothing | yes | 1.00 | 1.13 | 1.15 | -0.34 | 0.05 | 0.13 | 0.15 | 0.14 | 0.12 | 0.98 |
| window_glass_neg_02 | O | 128, 197 | nothing | yes | 1.00 | 1.20 | 1.25 | -0.38 | 0.06 | 0.14 | 0.16 | 0.12 | 0.08 | 0.09 |
| window_glass_occlx_16 | B | 408, 127 | nothing | yes | 0.83 | 1.37 | 1.91 | 0.69 | 0.51 | 0.61 | 0.44 | 0.21 | 0.47 | 0.88 |
| window_glass_occlx_16 | B | 246, 171 | nothing | yes | 0.83 | 1.29 | 1.59 | 1.58 | 0.62 | 0.48 | 0.05 | 0.19 | 0.14 | 0.18 |
| window_glass_occlx_16 | B | 356, 122 | nothing | yes | 1.00 | 1.10 | 0.99 | 1.04 | 0.22 | 0.25 | 0.26 | 0.80 | 0.31 | 0.61 |
| lampcool6_glass_neg_02 | O | 578, 146 | nothing | no | 1.00 | 1.09 | 0.90 | 0.33 | 0.12 | 0.09 | 0.56 | 0.48 | 0.35 | 0.87 |
| lampcool6_glass_occl_02 | B | 574, 129 | nothing | no | 1.00 | 1.07 | 1.14 | 1.29 | 1.16 | 0.89 | 0.79 | 0.44 | 0.36 | 0.65 |
| lampmid6_glass_occl_02 | O | 580, 146 | nothing | no | 1.00 | 1.01 | 0.81 | 0.67 | 0.32 | 0.13 | 0.72 | 0.56 | 0.46 | 1.15 |
| lampwarm6_glass_occl_02 | B | 574, 128 | nothing | no | 1.00 | 0.97 | 1.12 | 1.70 | 1.08 | 0.69 | 0.45 | 0.38 | 0.38 | 0.40 |
| window_glass_neg_02 | O | 579, 146 | nothing | no | 1.00 | 1.08 | 0.89 | 0.18 | 0.16 | 0.18 | 0.30 | 0.51 | 0.44 | 1.03 |
| window_glass_occl_02 | O | 578, 146 | nothing | no | 1.00 | 1.24 | 1.09 | 0.14 | 0.06 | 0.13 | 0.19 | 0.44 | 0.38 | 1.17 |
| window_glass_occlx_16 | O | 580, 146 | nothing | no | 1.00 | 1.27 | 1.16 | 0.24 | 0.19 | 0.12 | 0.28 | 0.44 | 0.45 | 1.26 |

## On a barrel

| frame | color | x, row | on | new box | share | strength | d | orange_part | alike_rel | alike_feat | above | below | left | right |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| both_abpgray_core_01 | B | 292, 248 | barrel (clean) | yes | 1.00 | 3.95 | 3.08 | 2.09 | 0.01 | 0.39 | 0.52 | 0.52 | 0.56 | 0.50 |
| both_abpgray_core_01 | O | 440, 161 | barrel (clean) | yes | 1.00 | 3.82 | 2.98 | 2.02 | 0.04 | 0.22 | 0.60 | 0.34 | 0.52 | 0.56 |
| both_abpgray_edge_01 | O | 323, 167 | barrel (clean) | yes | 1.00 | 3.97 | 3.10 | 2.05 | 0.02 | 0.06 | 0.61 | 0.37 | 0.57 | 0.64 |
| both_abpgray_touch_01 | O | 220, 155 | barrel (clean) | yes | 1.00 | 3.95 | 3.16 | 2.02 | 0.06 | 0.17 | 0.55 | 0.30 | 0.52 | 0.91 |
| both_abpgray_touch_01 | B | 274, 155 | barrel (clean) | yes | 1.00 | 3.87 | 3.16 | 2.00 | 0.03 | 0.18 | 0.51 | 0.51 | 0.88 | 0.18 |
| lampcool6_bathtile_clutter_01 | O | 426, 125 | barrel (clean) | yes | 1.00 | 2.17 | 1.63 | 1.62 | 0.01 | 0.07 | 0.45 | 0.52 | 0.36 | 0.45 |
| lampcool6_bathtile_occl_02 | O | 368, 122 | barrel (hidden) | yes | 0.67 | 1.16 | 1.45 | 1.52 | 0.11 | 0.12 | 0.47 | 0.49 | 0.64 | 0.35 |
| lampcool6_ottoman_clutter_01 | B | 137, 199 | barrel (clean) | yes | 1.00 | 2.41 | 1.97 | 1.54 | 0.13 | 0.16 | nan | 0.50 | 0.48 | 0.49 |
| lampcool6_ottoman_clutter_01 | O | 365, 195 | barrel (clean) | yes | 0.93 | 2.17 | 1.94 | 1.46 | 0.03 | 0.12 | 0.69 | 0.62 | 0.61 | 0.61 |
| lampcool6_ottoman_clutter_01 | O | 576, 165 | barrel (hidden) | yes | 1.00 | 1.29 | 1.14 | 1.09 | 0.26 | 0.40 | 0.80 | 0.43 | 0.76 | 0.76 |
| lampcool6_ottoman_clutter_01 | B | 314, 141 | barrel (hidden) | yes | 0.59 | 1.09 | 1.64 | 1.44 | 0.23 | 0.30 | 0.25 | 0.56 | 0.32 | 0.39 |
| lampcool6_ottoman_core_01 | O | 226, 253 | barrel (clean) | yes | 1.00 | 2.47 | 1.98 | 1.50 | 0.01 | 0.12 | 0.62 | 0.62 | 0.61 | 0.63 |
| lampcool6_ottoman_core_01 | B | 124, 172 | barrel (clean) | yes | 1.00 | 2.22 | 1.81 | 1.53 | 0.04 | 0.12 | nan | 0.44 | 0.43 | 0.45 |
| lampcool6_ottoman_core_01 | O | 458, 161 | barrel (clean) | yes | 0.90 | 1.56 | 1.62 | 1.31 | 0.07 | 0.16 | nan | 0.67 | 0.66 | 0.66 |
| lampcool6_ottoman_edge_01 | O | 316, 191 | barrel (clean) | yes | 0.92 | 2.20 | 1.92 | 1.43 | 0.02 | 0.12 | nan | nan | 0.60 | 0.60 |
| lampcool6_ottoman_edge_01 | B | 20, 186 | barrel (hidden) | yes | 0.67 | 1.41 | 1.64 | 1.39 | 0.06 | 0.11 | nan | 0.43 | nan | 0.45 |
| lampcool6_ottoman_occl_02 | O | 246, 162 | barrel (hidden) | yes | 0.61 | 1.14 | 1.55 | 1.18 | 0.16 | 0.32 | 0.62 | 0.57 | 0.59 | 0.73 |
| lampcool6_ottoman_touch_01 | B | 236, 166 | barrel (clean) | no | 0.71 | 1.70 | 1.90 | 1.47 | 0.12 | 0.17 | nan | 0.50 | 0.50 | 0.15 |
| lampmid3_bathtile_clutter_01 | B | 114, 175 | barrel (clean) | yes | 1.00 | 1.77 | 1.41 | 1.73 | 0.21 | 0.18 | 0.28 | 0.63 | 0.62 | 0.58 |
| lampmid3_bathtile_clutter_01 | O | 529, 161 | barrel (clean) | yes | 1.00 | 1.65 | 1.21 | 1.61 | 0.02 | 0.06 | 0.47 | 0.57 | 0.50 | 0.53 |
| lampmid3_bathtile_clutter_01 | B | 310, 132 | barrel (clean) | yes | 1.00 | 1.61 | 1.30 | 1.62 | 0.11 | 0.14 | 0.19 | 0.68 | 0.73 | 0.57 |
| lampmid3_bathtile_clutter_01 | O | 426, 125 | barrel (clean) | yes | 1.00 | 1.54 | 1.17 | 1.60 | 0.08 | 0.11 | 0.62 | 0.45 | 0.43 | 0.60 |
| lampmid3_bathtile_core_01 | O | 245, 143 | barrel (clean) | yes | 1.00 | 1.76 | 1.35 | 1.74 | 0.02 | 0.15 | 0.57 | 0.48 | 0.43 | 0.42 |
| lampmid3_bathtile_core_01 | B | 416, 188 | barrel (clean) | yes | 1.00 | 1.72 | 1.33 | 1.73 | 0.10 | 0.13 | 0.77 | 0.65 | 0.67 | 0.66 |
| lampmid3_bathtile_core_01 | B | 494, 129 | barrel (clean) | yes | 1.00 | 1.62 | 1.29 | 1.67 | 0.06 | 0.11 | 0.49 | 0.67 | 0.75 | 0.69 |
| lampmid3_bathtile_core_01 | O | 343, 123 | barrel (clean) | yes | 1.00 | 1.48 | 1.24 | 1.73 | 0.06 | 0.12 | 0.58 | 0.45 | 0.44 | 0.41 |
| lampmid3_bathtile_edge_01 | O | 306, 152 | barrel (clean) | yes | 1.00 | 1.81 | 1.36 | 1.73 | 0.00 | 0.08 | 0.62 | 0.51 | 0.40 | 0.41 |
| lampmid3_bathtile_touch_01 | O | 309, 153 | barrel (clean) | yes | 1.00 | 1.72 | 1.33 | 1.71 | 0.00 | 0.10 | 0.55 | 0.52 | 0.41 | 0.89 |
| lampmid3_bathtile_touch_01 | B | 367, 154 | barrel (clean) | yes | 1.00 | 1.64 | 1.30 | 1.70 | 0.14 | 0.15 | 0.43 | 0.67 | 0.89 | 0.07 |
| lampmid3_bathtile_touch_01 | B | 416, 155 | barrel (clean) | yes | 1.00 | 1.71 | 1.31 | 1.68 | 0.08 | 0.09 | 0.59 | 0.67 | 0.10 | 0.72 |
| lampmid6_bathtile_clutter_01 | B | 114, 175 | barrel (clean) | yes | 1.00 | 1.92 | 1.54 | 1.77 | 0.19 | 0.18 | 0.29 | 0.67 | 0.30 | 0.62 |
| lampmid6_bathtile_clutter_01 | O | 530, 161 | barrel (clean) | yes | 1.00 | 1.83 | 1.36 | 1.70 | 0.01 | 0.04 | 0.37 | 0.50 | 0.47 | 0.50 |
| lampmid6_bathtile_clutter_01 | O | 426, 125 | barrel (clean) | yes | 1.00 | 1.79 | 1.38 | 1.76 | 0.02 | 0.09 | 0.57 | 0.45 | 0.46 | 0.59 |
| lampmid6_bathtile_clutter_01 | B | 310, 133 | barrel (clean) | yes | 1.00 | 1.72 | 1.51 | 1.74 | 0.18 | 0.16 | 0.26 | 0.67 | 0.69 | 0.57 |
| lampmid6_bathtile_core_01 | O | 246, 142 | barrel (clean) | yes | 1.00 | 2.06 | 1.51 | 1.81 | 0.02 | 0.09 | 0.39 | 0.44 | 0.41 | 0.40 |
| lampmid6_bathtile_core_01 | B | 416, 188 | barrel (clean) | yes | 1.00 | 1.81 | 1.39 | 1.66 | 0.09 | 0.10 | 0.74 | 0.67 | 0.70 | 0.69 |
| lampmid6_bathtile_core_01 | O | 343, 123 | barrel (clean) | yes | 1.00 | 1.69 | 1.37 | 1.75 | 0.00 | 0.07 | 0.42 | 0.45 | 0.43 | 0.43 |
| lampmid6_bathtile_core_01 | B | 493, 129 | barrel (clean) | yes | 1.00 | 1.75 | 1.41 | 1.74 | 0.11 | 0.11 | 0.61 | 0.62 | 0.67 | 0.65 |
| lampmid6_bathtile_edge_01 | O | 306, 152 | barrel (clean) | yes | 1.00 | 2.02 | 1.48 | 1.77 | 0.01 | 0.06 | 0.37 | 0.49 | 0.39 | 0.40 |
| lampmid6_bathtile_edge_01 | B | 14, 163 | barrel (hidden) | yes | 0.61 | 1.08 | 1.40 | 1.65 | 0.15 | 0.14 | 0.58 | 0.67 | nan | 0.69 |
| lampmid6_bathtile_occl_02 | O | 368, 122 | barrel (hidden) | yes | 0.67 | 1.02 | 1.17 | 1.59 | 0.18 | 0.19 | 0.40 | 0.41 | 0.55 | 0.36 |
| lampmid6_bathtile_touch_01 | O | 310, 152 | barrel (clean) | yes | 1.00 | 1.93 | 1.45 | 1.76 | 0.02 | 0.08 | 0.42 | 0.50 | 0.42 | 0.92 |
| lampmid6_bathtile_touch_01 | B | 416, 155 | barrel (clean) | yes | 1.00 | 1.93 | 1.47 | 1.73 | 0.12 | 0.12 | 0.70 | 0.65 | 0.08 | 0.69 |
| lampmid6_bathtile_touch_01 | B | 366, 154 | barrel (clean) | yes | 1.00 | 1.82 | 1.44 | 1.69 | 0.14 | 0.15 | 0.62 | 0.67 | 0.95 | 0.07 |
| lampmid6_ottoman_clutter_01 | B | 139, 199 | barrel (clean) | yes | 0.97 | 1.93 | 1.62 | 1.54 | 0.06 | 0.15 | 0.41 | 0.36 | 0.42 | 0.41 |
| lampmid6_ottoman_clutter_01 | O | 576, 165 | barrel (hidden) | yes | 1.00 | 1.33 | 1.09 | 1.35 | 0.20 | 0.35 | 1.02 | 0.45 | 0.94 | 0.97 |
| lampmid6_ottoman_core_01 | B | 124, 171 | barrel (clean) | yes | 1.00 | 1.94 | 1.61 | 1.57 | 0.03 | 0.14 | 0.39 | 0.39 | 0.37 | 0.49 |
| lampmid6_ottoman_core_01 | B | 300, 137 | barrel (clean) | yes | 0.80 | 1.55 | 1.55 | 1.57 | 0.03 | 0.18 | 0.36 | 0.34 | 0.34 | 0.34 |
| lampmid6_ottoman_edge_01 | B | 22, 185 | barrel (hidden) | yes | 0.74 | 1.32 | 1.42 | 1.46 | 0.04 | 0.11 | nan | 0.36 | nan | 0.29 |
| lampmid6_ottoman_occl_02 | O | 247, 162 | barrel (hidden) | yes | 0.59 | 1.07 | 1.38 | 1.56 | 0.01 | 0.30 | 0.80 | 0.67 | 0.78 | 0.87 |
| lampmid6_ottoman_touch_01 | B | 236, 166 | barrel (clean) | no | 0.67 | 1.37 | 1.64 | 1.57 | 0.03 | 0.16 | nan | 0.35 | 0.33 | 0.13 |
| lampwarm6_bathtile_clutter_01 | B | 116, 175 | barrel (clean) | yes | 1.00 | 1.55 | 1.26 | 1.81 | 0.20 | 0.20 | 0.23 | 0.95 | 0.25 | 0.88 |
| lampwarm6_bathtile_clutter_01 | O | 530, 162 | barrel (clean) | yes | 1.00 | 1.54 | 1.19 | 1.75 | 0.01 | 0.04 | 0.38 | 0.57 | 0.49 | 0.51 |
| lampwarm6_bathtile_clutter_01 | B | 310, 132 | barrel (clean) | yes | 1.00 | 1.39 | 1.18 | 1.77 | 0.10 | 0.13 | 0.25 | 0.97 | 0.99 | 0.77 |
| lampwarm6_bathtile_clutter_01 | O | 426, 125 | barrel (clean) | yes | 0.97 | 1.38 | 1.13 | 1.72 | 0.04 | 0.09 | 0.77 | 0.56 | 0.58 | 0.74 |
| lampwarm6_bathtile_core_01 | O | 246, 143 | barrel (clean) | yes | 1.00 | 1.59 | 1.22 | 1.80 | 0.01 | 0.13 | 0.42 | 0.55 | 0.51 | 0.50 |
| lampwarm6_bathtile_core_01 | B | 414, 188 | barrel (clean) | yes | 1.00 | 1.53 | 1.22 | 1.76 | 0.10 | 0.12 | 0.92 | 0.93 | 0.95 | 0.95 |
| lampwarm6_bathtile_core_01 | O | 344, 123 | barrel (clean) | yes | 1.00 | 1.37 | 1.15 | 1.86 | 0.05 | 0.08 | 0.42 | 0.49 | 0.44 | 0.45 |
| lampwarm6_bathtile_core_01 | B | 493, 129 | barrel (clean) | yes | 1.00 | 1.34 | 1.18 | 1.76 | 0.11 | 0.10 | 0.76 | 0.90 | 0.91 | 0.88 |
| lampwarm6_bathtile_edge_01 | O | 306, 152 | barrel (clean) | yes | 1.00 | 1.62 | 1.22 | 1.78 | 0.00 | 0.07 | 0.43 | 0.58 | 0.50 | 0.50 |
| lampwarm6_bathtile_touch_01 | O | 310, 152 | barrel (clean) | yes | 1.00 | 1.61 | 1.23 | 1.82 | 0.02 | 0.10 | 0.42 | 0.57 | 0.49 | 0.93 |
| lampwarm6_bathtile_touch_01 | B | 363, 154 | barrel (clean) | yes | 1.00 | 1.56 | 1.20 | 1.77 | 0.08 | 0.09 | 0.70 | 0.98 | 0.94 | 0.05 |
| lampwarm6_bathtile_touch_01 | B | 418, 155 | barrel (clean) | yes | 1.00 | 1.51 | 1.19 | 1.73 | 0.13 | 0.14 | 0.79 | 0.98 | 0.08 | 0.94 |
| lampwarm6_ottoman_clutter_01 | B | 139, 199 | barrel (clean) | yes | 0.94 | 1.56 | 1.38 | 1.58 | 0.03 | 0.19 | 0.30 | 0.28 | 0.37 | 0.31 |
| lampwarm6_ottoman_clutter_01 | O | 366, 195 | barrel (clean) | yes | 0.84 | 1.41 | 1.33 | 1.59 | 0.01 | 0.27 | 0.74 | 0.97 | 0.95 | 0.96 |
| lampwarm6_ottoman_clutter_01 | O | 580, 165 | barrel (hidden) | yes | 1.00 | 1.24 | 1.06 | 1.43 | 0.10 | 0.26 | 1.10 | 0.33 | 0.89 | 0.97 |
| lampwarm6_ottoman_core_01 | B | 126, 171 | barrel (clean) | yes | 1.00 | 1.58 | 1.30 | 1.55 | 0.07 | 0.17 | 0.31 | 0.29 | 0.29 | 0.42 |
| lampwarm6_ottoman_core_01 | B | 301, 137 | barrel (clean) | yes | 0.77 | 1.24 | 1.26 | 1.57 | 0.12 | 0.26 | 0.24 | 0.20 | 0.21 | 0.20 |
| lampwarm6_ottoman_core_01 | O | 457, 161 | barrel (clean) | yes | 0.71 | 1.13 | 1.21 | 1.51 | 0.02 | 0.22 | 1.01 | 0.99 | 0.99 | 0.99 |
| lampwarm6_ottoman_edge_01 | O | 320, 190 | barrel (clean) | yes | 0.82 | 1.35 | 1.31 | 1.54 | 0.03 | 0.25 | nan | 0.94 | 0.93 | 0.94 |
| lampwarm6_ottoman_edge_01 | B | 23, 185 | barrel (hidden) | yes | 0.77 | 1.16 | 1.22 | 1.51 | 0.07 | 0.15 | nan | 0.32 | nan | 0.23 |
| lampwarm6_ottoman_touch_01 | O | 365, 166 | barrel (clean) | yes | 0.76 | 1.23 | 1.28 | 1.51 | 0.04 | 0.24 | nan | nan | 0.88 | 0.93 |
| lampwarm6_ottoman_touch_01 | B | 304, 165 | barrel (clean) | yes | 0.61 | 0.97 | 1.26 | 1.56 | 0.14 | 0.24 | nan | nan | 0.07 | 0.91 |
| window_abpwhite_occlx_06 | O | 157, 141 | barrel (hidden) | yes | 1.00 | 2.12 | 2.09 | 0.92 | 0.59 | 0.52 | 0.20 | 0.34 | 0.37 | 0.33 |
| window_abpwhite_occlx_14 | O | 21, 151 | barrel (hidden) | yes | 1.00 | 2.03 | 2.11 | 1.08 | 0.60 | 0.45 | 0.23 | 0.27 | nan | 0.36 |
