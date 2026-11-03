# step1 on train (16 frames, 4A8B boxfit camera)

Detection metrics (EVAL.md): greedy class-aware matching at IoU ≥ 0.5; GT flagged occluded, truncated, top_only is ignored; loose = projected ground position within 15 mm. Errors are over matched pairs (|·| median / p90).

| condition | frames (neg) | neg false det | orange n / P / R / F1 | blue n / P / R / F1 | loose P/R o · b | mean IoU | bottom err px | ground proj mm | ground meas mm (n) | color conf |
|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 16 (2) | 0 | 14 / 0.833 / 0.833 / 0.833 | 14 / 0.889 / 0.615 / 0.727 | 0.583/0.583 · 1.000/0.692 | 0.866 | 1.000 / 6.100 | 2.309 / 32.533 | 2.309 (20) | 0 |
| window_light_close | 2 (0) | 0 | 1 / 1.000 / 1.000 / 1.000 | 1 / 1.000 / 1.000 / 1.000 | 1.000/1.000 · 1.000/1.000 | 0.912 | 1.500 / 1.900 | 1.214 / 1.519 | 1.214 (2) | 0 |
| window_light_cluster | 2 (0) | 0 | 3 / 1.000 / 0.667 / 0.800 | 5 / 1.000 / 0.800 / 0.889 | 1.000/0.667 · 1.000/0.800 | 0.864 | 1.000 / 1.500 | 2.932 / 3.941 | 2.932 (6) | 0 |
| window_light_core | 3 (0) | 0 | 3 / 0.750 / 1.000 / 0.857 | 2 / 1.000 / 1.000 / 1.000 | 0.500/0.667 · 1.000/1.000 | 0.892 | 1.000 / 6.400 | 2.227 / 29.347 | 2.227 (5) | 0 |
| window_light_edge | 1 (0) | 0 | 0 / — / — / — | 1 / — / — / — | —/— · —/— | — | — / — | — / — | — (0) | 0 |
| window_light_far | 1 (0) | 0 | 2 / 0.667 / 1.000 / 0.800 | 2 / 1.000 / 0.500 / 0.667 | 0.000/0.000 · 1.000/0.500 | 0.766 | 6.000 / 6.800 | 32.291 / 34.226 | 32.291 (3) | 0 |
| window_light_neg | 2 (2) | 0 | 0 / — / — / — | 0 / — / — / — | —/— · —/— | — | — / — | — / — | — (0) | 0 |
| window_light_occl | 2 (0) | 0 | 1 / — / 0.000 / 0.000 | 2 / — / 0.000 / 0.000 | —/0.000 · —/0.000 | — | — / — | — / — | — (0) | 0 |
| window_light_top | 1 (0) | 0 | 1 / — / — / — | 0 / — / — / — | —/— · —/— | 0.902 | 0.000 / 0.000 | 2.009 / 2.009 | 2.009 (1) | 0 |
| window_light_topstripe | 1 (0) | 0 | 1 / — / — / — | 0 / — / — / — | —/— · —/— | 0.805 | 0.000 / 0.000 | 3.884 / 3.884 | 3.884 (1) | 0 |
| window_light_touch | 1 (0) | 0 | 2 / 1.000 / 1.000 / 1.000 | 1 / 0.000 / 0.000 / 0.000 | 1.000/1.000 · 1.000/1.000 | 0.924 | 1.000 / 1.000 | 2.096 / 2.106 | 2.096 (2) | 0 |

Per-image counts: `per_image.csv`; every match/miss/false: `per_barrel.csv`.
