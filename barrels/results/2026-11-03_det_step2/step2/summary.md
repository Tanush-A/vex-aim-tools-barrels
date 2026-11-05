# step2 on train (16 frames, boxfit camera, rule v1)

Detection metrics (EVAL.md). Rule **v1**: greedy class-aware matching (confidence order) at IoU ≥ 0.5; GT flagged occluded, truncated, top_only is ignored; any false detection on a negative frame disqualifies. Loose = projected ground position within 15 mm (not part of the v2 score). Errors are over matched pairs (|·| median / p90); bottom err seen · est. splits them by the GT box's bottom_estimated flag; count err = n_pred − n_gt per frame.

| condition | frames (neg, clean) | neg false det (on clean) | orange n / P / R / F1 | blue n / P / R / F1 | loose P/R o · b | mean IoU | bottom err px | bottom err seen · est. px (n) | bottom err frac | count err mean (abs) | ground proj mm | ground meas mm (n) | color conf |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 16 (2, 2) | 0 (0) | 16 / 0.889 / 1.000 / 0.941 | 13 / 1.000 / 1.000 / 1.000 | 0.889/1.000 · 1.000/1.000 | 0.829 | 1.000 / 1.000 | 1.000 (23) · 0.000 (2) | 0.018 | -0.188 (0.188) | 2.115 / 5.598 | 2.115 (25) | 0 |
| window_light_close | 2 (0, 0) | 0 (0) | 1 / 1.000 / 1.000 / 1.000 | 1 / 1.000 / 1.000 / 1.000 | 1.000/1.000 · 1.000/1.000 | 0.867 | 1.500 / 1.900 | 1.500 (2) · — (0) | 0.016 | 0.000 (0.000) | 1.423 / 1.599 | 1.423 (2) | 0 |
| window_light_cluster | 2 (0, 0) | 0 (0) | 4 / 0.500 / 1.000 / 0.667 | 4 / 1.000 / 1.000 / 1.000 | 0.500/1.000 · 1.000/1.000 | 0.825 | 1.000 / 1.000 | 1.000 (6) · — (0) | 0.018 | -0.500 (0.500) | 2.231 / 4.340 | 2.231 (6) | 0 |
| window_light_core | 3 (0, 0) | 0 (0) | 3 / 1.000 / 1.000 / 1.000 | 2 / 1.000 / 1.000 / 1.000 | 1.000/1.000 · 1.000/1.000 | 0.893 | 1.000 / 1.000 | 1.000 (5) · — (0) | 0.018 | 0.000 (0.000) | 2.115 / 4.251 | 2.115 (5) | 0 |
| window_light_edge | 1 (0, 0) | 0 (0) | 0 / — / — / — | 1 / — / — / — | —/— · —/— | 0.548 | 0.000 / 0.000 | 0.000 (1) · — (0) | 0.000 | 0.000 (0.000) | 5.570 / 5.570 | 5.570 (1) | 0 |
| window_light_far | 1 (0, 0) | 0 (0) | 2 / 1.000 / 1.000 / 1.000 | 2 / 1.000 / 1.000 / 1.000 | 1.000/1.000 · 1.000/1.000 | 0.796 | 1.000 / 1.000 | 1.000 (4) · — (0) | 0.029 | 0.000 (0.000) | 5.107 / 5.905 | 5.107 (4) | 0 |
| window_light_neg | 2 (2, 2) | 0 (0) | 0 / — / — / — | 0 / — / — / — | —/— · —/— | — | — / — | — (0) · — (0) | — | 0.000 (0.000) | — / — | — (0) | 0 |
| window_light_occl | 2 (0, 0) | 0 (0) | 2 / 1.000 / 1.000 / 1.000 | 2 / 1.000 / 1.000 / 1.000 | 1.000/1.000 · 1.000/1.000 | 0.829 | 1.000 / 1.000 | 1.000 (2) · — (0) | 0.011 | -1.000 (1.000) | 0.891 / 0.905 | 0.891 (2) | 0 |
| window_light_top | 1 (0, 0) | 0 (0) | 1 / — / — / — | 0 / — / — / — | —/— · —/— | 0.902 | 0.000 / 0.000 | — (0) · 0.000 (1) | 0.000 | 0.000 (0.000) | 2.009 / 2.009 | 2.009 (1) | 0 |
| window_light_topstripe | 1 (0, 0) | 0 (0) | 1 / — / — / — | 0 / — / — / — | —/— · —/— | 0.805 | 0.000 / 0.000 | — (0) · 0.000 (1) | 0.000 | 0.000 (0.000) | 3.884 / 3.884 | 3.884 (1) | 0 |
| window_light_touch | 1 (0, 0) | 0 (0) | 2 / 1.000 / 1.000 / 1.000 | 1 / 1.000 / 1.000 / 1.000 | 1.000/1.000 · 1.000/1.000 | 0.828 | 1.000 / 1.000 | 1.000 (3) · — (0) | 0.018 | 0.000 (0.000) | 2.125 / 3.346 | 2.125 (3) | 0 |

Per-image counts: `per_image.csv`; every match/miss/false: `per_barrel.csv`.
