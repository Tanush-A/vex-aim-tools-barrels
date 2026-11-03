# det_step1_boxes_step1 on train (16 frames, cam 4a8b)

Detection metrics (EVAL.md): greedy class-aware matching at IoU ≥ 0.5; GT flagged occluded, truncated, top_only is ignored; loose = projected ground position within 15 mm. Errors are over matched pairs (|·| median / p90).

| condition | frames (neg) | neg false det | orange n / P / R / F1 | blue n / P / R / F1 | loose P/R o · b | mean IoU | bottom err px | ground proj mm | ground meas mm (n) | color conf |
|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 16 (2) | 0 | 16 / 0.778 / 0.875 / 0.824 | 13 / 1.000 / 0.818 / 0.900 | 0.500/0.625 · 1.000/0.818 | 0.857 | 1.000 / 6.000 | 1.912 / 24.530 | 1.912 (21) | 0 |
| window_light_close | 2 (0) | 0 | 1 / 1.000 / 1.000 / 1.000 | 1 / 1.000 / 1.000 / 1.000 | 1.000/1.000 · 1.000/1.000 | 0.923 | 1.500 / 1.900 | 1.141 / 1.382 | 1.141 (2) | 0 |
| window_light_cluster | 2 (0) | 0 | 4 / 1.000 / 1.000 / 1.000 | 4 / 1.000 / 1.000 / 1.000 | 1.000/1.000 · 1.000/1.000 | 0.840 | 1.000 / 1.000 | 2.020 / 3.951 | 2.020 (6) | 0 |
| window_light_core | 3 (0) | 0 | 3 / 0.750 / 1.000 / 0.857 | 2 / 1.000 / 1.000 / 1.000 | 0.500/0.667 · 1.000/1.000 | 0.892 | 1.000 / 6.400 | 1.861 / 22.498 | 1.861 (5) | 0 |
| window_light_edge | 1 (0) | 0 | 0 / — / — / — | 1 / — / — / — | —/— · —/— | — | — / — | — / — | — (0) | 0 |
| window_light_far | 1 (0) | 0 | 2 / 0.500 / 1.000 / 0.667 | 2 / 1.000 / 0.500 / 0.667 | 0.000/0.000 · 1.000/0.500 | 0.756 | 6.000 / 6.800 | 24.530 / 26.007 | 24.530 (3) | 0 |
| window_light_neg | 2 (2) | 0 | 0 / — / — / — | 0 / — / — / — | —/— · —/— | — | — / — | — / — | — (0) | 0 |
| window_light_occl | 2 (0) | 0 | 2 / — / 0.000 / 0.000 | 2 / — / 0.000 / 0.000 | —/0.000 · —/0.000 | — | — / — | — / — | — (0) | 0 |
| window_light_top | 1 (0) | 0 | 1 / — / — / — | 0 / — / — / — | —/— · —/— | 0.902 | 0.000 / 0.000 | 1.978 / 1.978 | 1.978 (1) | 0 |
| window_light_topstripe | 1 (0) | 0 | 1 / — / — / — | 0 / — / — / — | —/— · —/— | 0.805 | 0.000 / 0.000 | 3.825 / 3.825 | 3.825 (1) | 0 |
| window_light_touch | 1 (0) | 0 | 2 / 1.000 / 1.000 / 1.000 | 1 / 1.000 / 1.000 / 1.000 | 1.000/1.000 · 1.000/1.000 | 0.895 | 1.000 / 1.000 | 1.748 / 1.766 | 1.748 (3) | 0 |

Per-image counts: `per_image.csv`; every match/miss/false: `per_barrel.csv`.
