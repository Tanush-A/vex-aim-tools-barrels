# dave_snaps_step1 on test (12 frames, cam 4a8b)

Detection metrics (EVAL.md): greedy class-aware matching at IoU ≥ 0.5; GT flagged occluded, truncated, top_only is ignored; loose = projected ground position within 15 mm. Errors are over matched pairs (|·| median / p90).

| condition | frames (neg) | neg false det | orange n / P / R / F1 | blue n / P / R / F1 | loose P/R o · b | mean IoU | bottom err px | ground proj mm | ground meas mm (n) | color conf |
|---|---|---|---|---|---|---|---|---|---|---|
| ALL | 12 (0) | 0 | 22 / — / 0.000 / 0.000 | 12 / — / 0.000 / 0.000 | —/0.000 · —/0.000 | — | — / — | — / — | — (0) | 0 |
| office_speckle_snap | 12 (0) | 0 | 22 / — / 0.000 / 0.000 | 12 / — / 0.000 / 0.000 | —/0.000 · —/0.000 | — | — / — | — / — | — (0) | 0 |

Per-image counts: `per_image.csv`; every match/miss/false: `per_barrel.csv`.
