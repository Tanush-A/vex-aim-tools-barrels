# Detector hardening: old (bands) vs new (cores, no dark gaps, body color) vs new+dark

git 9563b50; camera AIM_4A8B6118_BOXFIT; v2 rule where labels exist. Front ends: v1 = frozen afd85483; hs = hue sector + S floor (probe 2026-11-07, hs_p10h5, fit on the home train masks).

| front end | detector | home train v2 (F1 o / b) | neg FD | Dave 12 v2 (F1 o / b) | neg FD | campus: right count | campus negatives: boxes | campus frames with extra boxes |
|---|---|---|---|---|---|---|---|---|
| v1 | old | **0.91** (0.87 / 0.96) | 0 | **0.00** (0.00 / 0.00) | 0 | 7 / 21 | 0 | 0 |
| v1 | new | **0.93** (0.90 / 0.96) | 0 | **0.00** (0.00 / 0.00) | 0 | 8 / 21 | 0 | 0 |
| v1 | new+dark | **0.93** (0.93 / 0.92) | 0 | **0.00** (0.00 / 0.00) | 0 | 8 / 21 | 0 | 1 |
| hs | old | **0.57** (0.81 / 0.33) | 0 | **0.31** (0.30 / 0.32) | 0 | 12 / 21 | 0 | 5 |
| hs | new | **0.78** (0.93 / 0.63) | 0 | **0.40** (0.31 / 0.50) | 0 | 15 / 21 | 0 | 1 |
| hs | new+dark | **0.67** (0.90 / 0.44) | 0 | **0.37** (0.31 / 0.42) | 0 | 10 / 21 | 1 | 8 |

## Campus train frames, boxes orange/blue (expected in brackets where wrong)

| frame | v1/old | v1/new | v1/new+dark | hs/old | hs/new | hs/new+dark |
|---|---|---|---|---|---|---|
| close_01 | 0/0 (exp 1/0) | 0/0 (exp 1/0) | 0/0 (exp 1/0) | 0/1 (exp 1/0) | 1/0 | 1/0 |
| cluster_02 | 0/0 (exp 2/2) | 0/0 (exp 2/2) | 2/0 (exp 2/2) | 2/1 (exp 2/2) | 2/1 (exp 2/2) | 2/3 (exp 2/2) |
| clutter_02 | 0/0 (exp 1/2) | 0/0 (exp 1/2) | 0/0 (exp 1/2) | 1/1 (exp 1/2) | 1/1 (exp 1/2) | 1/1 (exp 1/2) |
| core_01 | 2/0 (exp 2/2) | 1/0 (exp 2/2) | 1/1 (exp 2/2) | 0/3 (exp 2/2) | 0/3 (exp 2/2) | 0/5 (exp 2/2) |
| edge_01 | 0/0 (exp 1/0) | 0/0 (exp 1/0) | 0/0 (exp 1/0) | 0/0 (exp 1/0) | 0/0 (exp 1/0) | 0/0 (exp 1/0) |
| far_01 | 2/1 (exp 2/2) | 1/1 (exp 2/2) | 3/1 (exp 2/2) | 3/2 (exp 2/2) | 2/2 | 3/2 (exp 2/2) |
| hand_02 | 1/1 | 1/1 | 1/1 | 1/2 (exp 1/1) | 1/1 | 1/2 (exp 1/1) |
| held_01 | 0/0 (exp 0/1) | 0/0 (exp 0/1) | 0/0 (exp 0/1) | 0/1 | 0/1 | 0/1 |
| neg_02 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| neg_03 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| neg_04 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 |
| neg_05 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0/1 (exp 0/0) |
| occl_02 | 0/0 (exp 0/1) | 0/0 (exp 0/1) | 0/0 (exp 0/1) | 0/0 (exp 0/1) | 0/0 (exp 0/1) | 0/0 (exp 0/1) |
| plain_01 | 1/0 (exp 1/1) | 1/1 | 1/1 | 2/0 (exp 1/1) | 1/1 | 2/1 (exp 1/1) |
| plain_02 | 1/0 (exp 1/1) | 1/0 (exp 1/1) | 1/0 (exp 1/1) | 1/1 | 1/1 | 1/1 |
| room_01 | 0/0 (exp 1/1) | 0/0 (exp 1/1) | 0/0 (exp 1/1) | 1/1 | 1/0 (exp 1/1) | 1/1 |
| room_03 | 0/0 (exp 1/1) | 0/0 (exp 1/1) | 0/0 (exp 1/1) | 1/1 | 1/1 | 1/2 (exp 1/1) |
| top_01 | 1/0 | 1/0 | 1/0 | 1/0 | 1/0 | 1/0 |
| topstripe_01 | 1/0 | 1/0 | 1/0 | 1/0 | 1/0 | 1/0 |
| touch_02 | 0/0 (exp 0/2) | 0/0 (exp 0/2) | 0/0 (exp 0/2) | 0/2 | 0/2 | 0/3 (exp 0/2) |
| window_01 | 0/0 (exp 1/1) | 0/0 (exp 1/1) | 1/0 (exp 1/1) | 1/1 | 1/1 | 1/1 |