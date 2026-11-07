# Segmentation probe: (hue, HSV-saturation) boxes, no top-row stages

git 091a616; boxes fit on the 16 home train frames' masks; detector DetConfig(), camera AIM_4A8B6118_BOXFIT; v2 rule.

- `hs` boxes (H 0–179, S 0–255): orange {'lo': [2.0, 84.0], 'hi': [168.0, 239.0]}, blue {'lo': [5.0, 23.0], 'hi': [170.0, 255.0]}; V >= 40, horizon 50
- `hs_tight` boxes (H 0–179, S 0–255): orange {'lo': [3.0, 103.0], 'hi': [17.0, 234.0]}, blue {'lo': [10.0, 34.0], 'hi': [156.0, 255.0]}; V >= 40, horizon 50

| arm | home train v2 (F1 o / b) | neg FD | Dave 12 v2 (F1 o / b) | neg FD | campus train: frames with the right count | boxes on the 4 campus negatives |
|---|---|---|---|---|---|---|
| v1 | **0.91** (0.87 / 0.96) | 0 | **0.00** (0.00 / 0.00) | 0 | 7 / 21 | 0 |
| hs | **0.52** (0.77 / 0.27) | 0 | **0.10** (0.18 / 0.03) | 0 | 1 / 21 | 22 |
| hs_tight | **0.36** (0.69 / 0.03) | 16 | **0.18** (0.28 / 0.09) | 0 | 4 / 21 | 17 |

## Campus train frames: boxes orange/blue per arm (expected in brackets where wrong)

| frame | v1 | hs | hs_tight |
|---|---|---|---|
| close_01 | 0/0 (exp 1/0) | 1/6 (exp 1/0) | 1/2 (exp 1/0) |
| cluster_02 | 0/0 (exp 2/2) | 2/4 (exp 2/2) | 2/1 (exp 2/2) |
| clutter_02 | 0/0 (exp 1/2) | 1/1 (exp 1/2) | 2/7 (exp 1/2) |
| core_01 | 2/0 (exp 2/2) | 2/4 (exp 2/2) | 2/4 (exp 2/2) |
| edge_01 | 0/0 (exp 1/0) | 0/6 (exp 1/0) | 1/0 |
| far_01 | 2/1 (exp 2/2) | 2/9 (exp 2/2) | 2/5 (exp 2/2) |
| hand_02 | 1/1 | 1/2 (exp 1/1) | 3/5 (exp 1/1) |
| held_01 | 0/0 (exp 0/1) | 2/6 (exp 0/1) | 1/5 (exp 0/1) |
| neg_02 | 0/0 | 0/3 (exp 0/0) | 0/2 (exp 0/0) |
| neg_03 | 0/0 | 0/3 (exp 0/0) | 0/6 (exp 0/0) |
| neg_04 | 0/0 | 1/7 (exp 0/0) | 2/4 (exp 0/0) |
| neg_05 | 0/0 | 1/7 (exp 0/0) | 0/3 (exp 0/0) |
| occl_02 | 0/0 (exp 0/1) | 0/3 (exp 0/1) | 0/1 |
| plain_01 | 1/0 (exp 1/1) | 0/2 (exp 1/1) | 1/1 |
| plain_02 | 1/0 (exp 1/1) | 1/2 (exp 1/1) | 1/2 (exp 1/1) |
| room_01 | 0/0 (exp 1/1) | 1/1 | 1/5 (exp 1/1) |
| room_03 | 0/0 (exp 1/1) | 1/3 (exp 1/1) | 1/5 (exp 1/1) |
| top_01 | 1/0 | 0/12 (exp 1/0) | 1/2 (exp 1/0) |
| topstripe_01 | 1/0 | 0/6 (exp 1/0) | 0/5 (exp 1/0) |
| touch_02 | 0/0 (exp 0/2) | 0/4 (exp 0/2) | 0/2 |
| window_01 | 0/0 (exp 1/1) | 1/3 (exp 1/1) | 1/2 (exp 1/1) |