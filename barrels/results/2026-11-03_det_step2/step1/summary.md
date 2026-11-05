# step1 on train (16 frames, boxfit camera, rule v1)

Detection metrics (EVAL.md). Rule **v1**: greedy class-aware matching (confidence order) at IoU ≥ 0.5; GT flagged occluded, truncated, top_only is ignored; any false detection on a negative frame disqualifies. Loose = projected ground position within 15 mm (not part of the v2 score). Errors are over matched pairs (|·| median / p90); bottom err seen · est. splits them by the GT box's bottom_estimated flag; count err = n_pred − n_gt per frame.

| condition | frames (neg, clean) | neg false det (on clean) | orange n / P / R / F1 | blue n / P / R / F1 | loose P/R o · b | mean IoU | bottom err px | bottom err seen · est. px (n) | bottom err frac | count err mean (abs) | ground proj mm | ground meas mm (n) | color conf |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 16 (2, 2) | 0 (0) | 16 / 0.778 / 0.875 / 0.824 | 13 / 1.000 / 0.818 / 0.900 | 0.500/0.625 · 1.000/0.818 | 0.857 | 1.000 / 6.000 | 1.000 (19) · 0.000 (2) | 0.018 | -0.375 (0.500) | 2.227 / 32.622 | 2.227 (21) | 0 |
| window_light_close | 2 (0, 0) | 0 (0) | 1 / 1.000 / 1.000 / 1.000 | 1 / 1.000 / 1.000 / 1.000 | 1.000/1.000 · 1.000/1.000 | 0.923 | 1.500 / 1.900 | 1.500 (2) · — (0) | 0.016 | 0.000 (0.000) | 1.259 / 1.527 | 1.259 (2) | 0 |
| window_light_cluster | 2 (0, 0) | 0 (0) | 4 / 1.000 / 1.000 / 1.000 | 4 / 1.000 / 1.000 / 1.000 | 1.000/1.000 · 1.000/1.000 | 0.840 | 1.000 / 1.000 | 1.000 (6) · — (0) | 0.018 | -1.000 (1.000) | 2.439 / 4.389 | 2.439 (6) | 0 |
| window_light_core | 3 (0, 0) | 0 (0) | 3 / 0.750 / 1.000 / 0.857 | 2 / 1.000 / 1.000 / 1.000 | 0.500/0.667 · 1.000/1.000 | 0.892 | 1.000 / 6.400 | 1.000 (5) · — (0) | 0.018 | 0.333 (0.333) | 2.227 / 29.347 | 2.227 (5) | 0 |
| window_light_edge | 1 (0, 0) | 0 (0) | 0 / — / — / — | 1 / — / — / — | —/— · —/— | — | — / — | — (0) · — (0) | — | -1.000 (1.000) | — / — | — (0) | 0 |
| window_light_far | 1 (0, 0) | 0 (0) | 2 / 0.500 / 1.000 / 0.667 | 2 / 1.000 / 0.500 / 0.667 | 0.000/0.000 · 1.000/0.500 | 0.756 | 6.000 / 6.800 | 6.000 (3) · — (0) | 0.200 | 0.000 (0.000) | 32.622 / 34.292 | 32.622 (3) | 0 |
| window_light_neg | 2 (2, 2) | 0 (0) | 0 / — / — / — | 0 / — / — / — | —/— · —/— | — | — / — | — (0) · — (0) | — | 0.000 (0.000) | — / — | — (0) | 0 |
| window_light_occl | 2 (0, 0) | 0 (0) | 2 / — / 0.000 / 0.000 | 2 / — / 0.000 / 0.000 | —/0.000 · —/0.000 | — | — / — | — (0) · — (0) | — | -2.000 (2.000) | — / — | — (0) | 0 |
| window_light_top | 1 (0, 0) | 0 (0) | 1 / — / — / — | 0 / — / — / — | —/— · —/— | 0.902 | 0.000 / 0.000 | — (0) · 0.000 (1) | 0.000 | 0.000 (0.000) | 2.009 / 2.009 | 2.009 (1) | 0 |
| window_light_topstripe | 1 (0, 0) | 0 (0) | 1 / — / — / — | 0 / — / — / — | —/— · —/— | 0.805 | 0.000 / 0.000 | — (0) · 0.000 (1) | 0.000 | 0.000 (0.000) | 3.884 / 3.884 | 3.884 (1) | 0 |
| window_light_touch | 1 (0, 0) | 0 (0) | 2 / 1.000 / 1.000 / 1.000 | 1 / 1.000 / 1.000 / 1.000 | 1.000/1.000 · 1.000/1.000 | 0.895 | 1.000 / 1.000 | 1.000 (3) · — (0) | 0.018 | 0.000 (0.000) | 2.082 / 2.103 | 2.082 (3) | 0 |

Per-image counts: `per_image.csv`; every match/miss/false: `per_barrel.csv`.
