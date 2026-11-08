# Segmentation probe: hue sector + HSV-saturation floor per class, no top-row stages

git 9563b50; boxes fit on the 16 home train frames' masks; detector DetConfig(), camera AIM_4A8B6118_BOXFIT; v2 rule.

- `hs_p5`: orange hue 3–12 (OpenCV 0–179, unshifted), S >= 140; blue hue 11–150, S >= 64; V >= 40, horizon 50
- `hs_p10`: orange hue 4–11 (OpenCV 0–179, unshifted), S >= 163; blue hue 12–140, S >= 92; V >= 40, horizon 50
- `hs_p10h5`: orange hue 5–10 (OpenCV 0–179, unshifted), S >= 163; blue hue 104–118, S >= 92; V >= 40, horizon 50

| arm | home train v2 (F1 o / b) | neg FD | Dave 12 v2 (F1 o / b) | neg FD | campus train: frames with the right count | boxes on the 4 campus negatives |
|---|---|---|---|---|---|---|
| v1 | **0.91** (0.87 / 0.96) | 0 | **0.00** (0.00 / 0.00) | 0 | 7 / 21 | 0 |
| hs_p5 | **0.42** (0.83 / 0.01) | 25 | **0.28** (0.44 / 0.12) | 0 | 10 / 21 | 12 |
| hs_p10 | **0.50** (0.86 / 0.14) | 4 | **0.24** (0.27 / 0.22) | 0 | 10 / 21 | 2 |
| hs_p10h5 | **0.57** (0.81 / 0.33) | 0 | **0.31** (0.30 / 0.32) | 0 | 12 / 21 | 0 |

## Campus train frames: boxes orange/blue per arm (expected in brackets where wrong)

| frame | v1 | hs_p5 | hs_p10 | hs_p10h5 |
|---|---|---|---|---|
| close_01 | 0/0 (exp 1/0) | 1/0 | 1/0 | 0/1 (exp 1/0) |
| cluster_02 | 0/0 (exp 2/2) | 2/3 (exp 2/2) | 2/1 (exp 2/2) | 2/1 (exp 2/2) |
| clutter_02 | 0/0 (exp 1/2) | 4/0 (exp 1/2) | 1/0 (exp 1/2) | 1/1 (exp 1/2) |
| core_01 | 2/0 (exp 2/2) | 2/2 | 0/4 (exp 2/2) | 0/3 (exp 2/2) |
| edge_01 | 0/0 (exp 1/0) | 1/0 | 0/0 (exp 1/0) | 0/0 (exp 1/0) |
| far_01 | 2/1 (exp 2/2) | 2/2 | 2/3 (exp 2/2) | 3/2 (exp 2/2) |
| hand_02 | 1/1 | 2/2 (exp 1/1) | 1/2 (exp 1/1) | 1/2 (exp 1/1) |
| held_01 | 0/0 (exp 0/1) | 0/1 | 0/1 | 0/1 |
| neg_02 | 0/0 | 0/2 (exp 0/0) | 0/0 | 0/0 |
| neg_03 | 0/0 | 0/1 (exp 0/0) | 0/0 | 0/0 |
| neg_04 | 0/0 | 3/2 (exp 0/0) | 0/0 | 0/0 |
| neg_05 | 0/0 | 3/1 (exp 0/0) | 2/0 (exp 0/0) | 0/0 |
| occl_02 | 0/0 (exp 0/1) | 0/1 | 0/1 | 0/0 (exp 0/1) |
| plain_01 | 1/0 (exp 1/1) | 1/5 (exp 1/1) | 1/0 (exp 1/1) | 2/0 (exp 1/1) |
| plain_02 | 1/0 (exp 1/1) | 1/3 (exp 1/1) | 1/1 | 1/1 |
| room_01 | 0/0 (exp 1/1) | 1/0 (exp 1/1) | 1/2 (exp 1/1) | 1/1 |
| room_03 | 0/0 (exp 1/1) | 1/1 | 1/2 (exp 1/1) | 1/1 |
| top_01 | 1/0 | 1/0 | 1/0 | 1/0 |
| topstripe_01 | 1/0 | 1/0 | 1/0 | 1/0 |
| touch_02 | 0/0 (exp 0/2) | 0/1 (exp 0/2) | 0/3 (exp 0/2) | 0/2 |
| window_01 | 0/0 (exp 1/1) | 1/1 | 1/1 | 1/1 |