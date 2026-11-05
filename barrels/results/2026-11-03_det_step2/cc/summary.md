# cc on train (16 frames, boxfit camera, rule v1)

Detection metrics (EVAL.md). Rule **v1**: greedy class-aware matching (confidence order) at IoU ≥ 0.5; GT flagged occluded, truncated, top_only is ignored; any false detection on a negative frame disqualifies. Loose = projected ground position within 15 mm (not part of the v2 score). Errors are over matched pairs (|·| median / p90); bottom err seen · est. splits them by the GT box's bottom_estimated flag; count err = n_pred − n_gt per frame.

| condition | frames (neg, clean) | neg false det (on clean) | orange n / P / R / F1 | blue n / P / R / F1 | loose P/R o · b | mean IoU | bottom err px | bottom err seen · est. px (n) | bottom err frac | count err mean (abs) | ground proj mm | ground meas mm (n) | color conf |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 16 (2, 2) | 0 (0) | 16 / 0.233 / 0.875 / 0.368 | 13 / 0.474 / 0.818 / 0.600 | 0.276/1.000 · 0.611/1.000 | 0.734 | 1.000 / 5.000 | 1.000 (16) · 0.000 (2) | 0.014 | 1.375 (1.625) | 2.250 / 22.405 | 2.250 (18) | 0 |
| window_light_close | 2 (0, 0) | 0 (0) | 1 / 0.500 / 1.000 / 0.667 | 1 / 1.000 / 1.000 / 1.000 | 0.500/1.000 · 1.000/1.000 | 0.718 | 1.500 / 1.900 | 1.500 (2) · — (0) | 0.016 | 0.500 (0.500) | 1.284 / 1.571 | 1.284 (2) | 0 |
| window_light_cluster | 2 (0, 0) | 0 (0) | 4 / 0.000 / 0.000 / 0.000 | 4 / 0.250 / 0.500 / 0.333 | 0.250/1.000 · 0.500/1.000 | 0.808 | 0.500 / 0.900 | 0.500 (2) · — (0) | 0.009 | 2.500 (2.500) | 3.690 / 5.073 | 3.690 (2) | 0 |
| window_light_core | 3 (0, 0) | 0 (0) | 3 / 0.333 / 1.000 / 0.500 | 2 / 1.000 / 1.000 / 1.000 | 0.333/1.000 · 1.000/1.000 | 0.794 | 1.000 / 16.800 | 1.000 (5) · — (0) | 0.019 | 2.000 (2.000) | 2.274 / 70.021 | 2.274 (5) | 0 |
| window_light_edge | 1 (0, 0) | 0 (0) | 0 / 0.000 / — / 0.000 | 1 / 0.000 / — / 0.000 | 0.000/— · 0.000/— | — | — / — | — (0) · — (0) | — | 2.000 (2.000) | — / — | — (0) | 0 |
| window_light_far | 1 (0, 0) | 0 (0) | 2 / 0.111 / 1.000 / 0.200 | 2 / 1.000 / 1.000 / 1.000 | 0.111/1.000 · 1.000/1.000 | 0.568 | 1.000 / 1.000 | 1.000 (3) · — (0) | 0.026 | 7.000 (7.000) | 6.907 / 7.621 | 6.907 (3) | 0 |
| window_light_neg | 2 (2, 2) | 0 (0) | 0 / — / — / — | 0 / — / — / — | —/— · —/— | — | — / — | — (0) · — (0) | — | 0.000 (0.000) | — / — | — (0) | 0 |
| window_light_occl | 2 (0, 0) | 0 (0) | 2 / 0.500 / 1.000 / 0.667 | 2 / 0.500 / 1.000 / 0.667 | 0.500/1.000 · 0.500/1.000 | 0.639 | 1.000 / 1.000 | 1.000 (2) · — (0) | 0.011 | 0.000 (1.000) | 0.890 / 0.906 | 0.890 (2) | 0 |
| window_light_top | 1 (0, 0) | 0 (0) | 1 / — / — / — | 0 / — / — / — | —/— · —/— | 0.902 | 0.000 / 0.000 | — (0) · 0.000 (1) | 0.000 | 0.000 (0.000) | 2.009 / 2.009 | 2.009 (1) | 0 |
| window_light_topstripe | 1 (0, 0) | 0 (0) | 1 / 0.000 / — / 0.000 | 0 / 0.000 / — / 0.000 | 0.000/— · 0.000/— | 0.805 | 0.000 / 0.000 | — (0) · 0.000 (1) | 0.000 | 2.000 (2.000) | 3.884 / 3.884 | 3.884 (1) | 0 |
| window_light_touch | 1 (0, 0) | 0 (0) | 2 / 1.000 / 1.000 / 1.000 | 1 / 1.000 / 1.000 / 1.000 | 1.000/1.000 · 1.000/1.000 | 0.750 | 0.500 / 0.900 | 0.500 (2) · — (0) | 0.010 | -1.000 (1.000) | 6.096 / 9.286 | 6.096 (2) | 0 |

Per-image counts: `per_image.csv`; every match/miss/false: `per_barrel.csv`.
