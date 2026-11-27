# Group 3 (report only): the very dark ottoman

Per labelled barrel (not tipped, stripe inside the frame): V = the brightest channel (median); under 25 / 40 = share of the pixels under the contrast floor / the color gate; diff = median red-against-blue of the body minus the stripe's, at offset o; noise = the spread (median absolute deviation x 1.48) of the body band in the same channel; z = diff / noise.

| frame | color | body V | stripe V | body under 25 / 40 | stripe under 25 / 40 | diff o=2 (z) | diff o=8 (z) | diff o=16 (z) |
|---|---|---|---|---|---|---|---|---|
| lampmid3_ottoman_core_01 | blue | 30 | 56 | 0.22 / 0.96 | 0.01 / 0.10 | -1.81 (10.4) | -1.45 (9.6) | -1.16 (9.2) |
| lampmid3_ottoman_core_01 | orange | 62 | 18 | 0.00 / 0.05 | 0.89 / 0.93 | +1.68 (11.4) | +1.36 (11.0) | +1.10 (13.7) |
| lampmid3_ottoman_core_01 | blue | 29 | 52 | 0.38 / 0.96 | 0.09 / 0.25 | -1.47 (11.5) | -1.22 (12.3) | -0.99 (14.2) |
| lampmid3_ottoman_core_01 | orange | 56 | 14 | 0.07 / 0.21 | 0.94 / 1.00 | +1.39 (5.0) | +1.15 (5.3) | +0.94 (5.7) |
| lampmid3_ottoman_edge_01 | blue | 22 | 41 | 0.81 / 0.93 | 0.18 / 0.46 | -1.24 (1241713.1) | -0.99 (990319.2) | -0.79 (785079.0) |
| lampmid3_ottoman_edge_01 | orange | 55 | 14 | 0.02 / 0.11 | 0.98 / 1.00 | +1.62 (5.8) | +1.28 (6.3) | +1.04 (7.0) |
| lampmid3_ottoman_touch_01 | blue | 20 | 46 | 0.81 / 1.00 | 0.14 / 0.36 | -1.49 (1491654.9) | -1.15 (1149905.6) | -0.92 (923670.8) |
| lampmid3_ottoman_touch_01 | blue | 20 | 42 | 0.88 / 1.00 | 0.15 / 0.38 | -1.39 (1386294.4) | -1.08 (1078809.7) | -0.84 (844432.5) |
| lampmid3_ottoman_touch_01 | orange | 52 | 14 | 0.02 / 0.16 | 1.00 / 1.00 | +1.44 (5.2) | +1.15 (6.2) | +0.92 (7.7) |
| lampmid3_ottoman_clutter_01 | blue | 46 | 60 | 0.12 / 0.36 | 0.00 / 0.04 | -2.25 (16.5) | -1.85 (15.8) | -1.53 (17.5) |
| lampmid3_ottoman_clutter_01 | blue | 41 | 56 | 0.14 / 0.46 | 0.08 / 0.22 | -1.81 (7.3) | -1.54 (7.7) | -1.28 (7.9) |
| lampmid3_ottoman_clutter_01 | orange | 65 | 18 | 0.01 / 0.03 | 0.92 / 1.00 | +1.58 (9.4) | +1.30 (10.2) | +1.09 (12.8) |
| lampmid3_ottoman_clutter_01 | orange | 52 | 21 | 0.06 / 0.16 | 0.73 / 0.97 | +1.30 (3.4) | +1.08 (4.1) | +0.89 (4.6) |
| lampmid3_ottoman_close_01 | orange | 125 | 103 | 0.00 / 0.00 | 0.00 / 0.04 | +0.17 (1.4) | +0.16 (1.6) | +0.15 (1.8) |
| lampmid3_ottoman_occl_02 | orange | 74 | 26 | 0.00 / 0.00 | 0.47 / 0.69 | +1.48 (3.1) | +1.26 (3.9) | +1.07 (4.5) |
| lampmid6_ottoman_core_01 | blue | 114 | 155 | 0.00 / 0.00 | 0.00 / 0.00 | -2.34 (17.0) | -2.15 (18.3) | -1.94 (20.0) |
| lampmid6_ottoman_core_01 | orange | 166 | 80 | 0.00 / 0.00 | 0.01 / 0.11 | +2.41 (22.5) | +2.19 (25.8) | +1.96 (29.5) |
| lampmid6_ottoman_core_01 | blue | 110 | 150 | 0.00 / 0.00 | 0.00 / 0.00 | -2.36 (9.6) | -2.15 (9.9) | -1.92 (10.2) |
| lampmid6_ottoman_core_01 | orange | 152 | 45 | 0.00 / 0.00 | 0.27 / 0.44 | +2.01 (13.3) | +1.80 (14.9) | +1.58 (15.5) |
| lampmid6_ottoman_edge_01 | blue | 85 | 122 | 0.00 / 0.00 | 0.00 / 0.00 | -2.22 (16.4) | -2.00 (16.7) | -1.78 (16.9) |
| lampmid6_ottoman_edge_01 | orange | 140 | 65 | 0.00 / 0.00 | 0.14 / 0.28 | +2.47 (13.7) | +2.21 (16.4) | +1.94 (18.7) |
| lampmid6_ottoman_touch_01 | blue | 89 | 126 | 0.00 / 0.00 | 0.00 / 0.00 | -2.46 (21.4) | -2.19 (22.4) | -1.92 (23.0) |
| lampmid6_ottoman_touch_01 | blue | 86 | 122 | 0.00 / 0.00 | 0.00 / 0.00 | -2.38 (16.1) | -2.12 (17.4) | -1.86 (18.9) |
| lampmid6_ottoman_touch_01 | orange | 136 | 56 | 0.00 / 0.00 | 0.17 / 0.34 | +2.38 (13.9) | +2.11 (14.6) | +1.86 (16.7) |
| lampmid6_ottoman_clutter_01 | blue | 124 | 169 | 0.00 / 0.00 | 0.00 / 0.00 | -2.39 (13.2) | -2.21 (14.1) | -2.00 (15.1) |
| lampmid6_ottoman_clutter_01 | blue | 122 | 163 | 0.00 / 0.00 | 0.00 / 0.00 | -2.35 (10.8) | -2.16 (11.2) | -1.94 (11.4) |
| lampmid6_ottoman_clutter_01 | orange | 177 | 73 | 0.00 / 0.00 | 0.15 / 0.28 | +2.42 (19.2) | +2.20 (21.9) | +1.97 (26.1) |
| lampmid6_ottoman_clutter_01 | orange | 152 | 75 | 0.00 / 0.00 | 0.00 / 0.12 | +1.64 (9.5) | +1.50 (11.5) | +1.34 (14.0) |
| lampmid6_ottoman_close_01 | orange | 230 | 204 | 0.00 / 0.00 | 0.00 / 0.00 | +0.13 (1.1) | +0.12 (1.2) | +0.12 (1.3) |
| lampmid6_ottoman_occl_02 | orange | 212 | 108 | 0.00 / 0.00 | 0.00 / 0.02 | +2.05 (5.4) | +1.91 (5.9) | +1.75 (6.5) |

| light | barrels | median body V | median stripe V | median diff at o=8 | median z o=2 | median z o=8 | median z o=16 |
|---|---|---|---|---|---|---|---|
| lampmid3 | 15 | 52 | 41 | 1.22 | 9.4 | 9.6 | 9.2 |
| lampmid6 | 15 | 136 | 122 | 2.15 | 13.7 | 14.9 | 16.7 |

## The finder on the lamp-mid-3 ottoman frames at report-only settings

Candidates whose stripe point is on a labelled barrel's stripe (middle 70 % of columns, rows 0.35-0.80 of the box) / on nothing. Today: offset 8, brightness floor 25, margin 0.5, strength 1.15.

| setting | barrels with a candidate on their stripe | candidates on nothing |
|---|---|---|
| today | 0 of 15 | 0 |
| floor V 10 | 2 of 15 | 0 |
| offset 2 | 0 of 15 | 0 |
| offset 2, floor V 10 | 2 of 15 | 0 |
| floor V 10, margin 0.3, strength 0.8 | 5 of 15 | 0 |
