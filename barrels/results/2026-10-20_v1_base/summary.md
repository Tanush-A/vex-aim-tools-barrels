# v1_base: LOSO CV on 16 pool frames

Config `5f1a692b` (see config.json); git 34fb11f; 16 pool frames predicted once each; 1.5 s.

## Score (EVAL.md / DECISIONS.md 2026-10-19 rule)

- **primary** (mean of pooled orange/blue IoU, in-scope positives): **0.775**
- orange: IoU 0.766, P 0.866, R 0.868; fold IoU 0.724 ± 0.175
- blue: IoU 0.785, P 0.989, R 0.792; fold IoU 0.775 ± 0.049
- negative frames: FP rate orange 0.000, blue 0.000
- out-of-scope (top/topstripe): IoU orange 0.000, blue 0.000
- prior guard trips: 0

## Folds

| held-out scene | n | orange IoU | blue IoU | neg FP o | neg FP b | guard trips |
|---|---|---|---|---|---|---|
| close | 2 | 0.890 | 0.826 | — | — | 0 |
| cluster | 2 | 0.735 | 0.796 | — | — | 0 |
| core | 3 | 0.743 | 0.676 | — | — | 0 |
| edge | 1 | 0.651 | 0.797 | — | — | 0 |
| far | 1 | 0.344 | 0.746 | — | — | 0 |
| neg | 2 | — | — | 0.000 | 0.000 | 0 |
| occl | 2 | 0.898 | 0.826 | — | — | 0 |
| top | 1 | — | — | — | — | 0 |
| topstripe | 1 | — | — | — | — | 0 |
| touch | 1 | 0.807 | 0.758 | — | — | 0 |

## Box bounds across folds (min … max per channel)

- orange: lo [60, 10, 3] … [71, 18, 5], hi [208, 119, 109] … [212, 127, 116]; fullness(8) 0.25–0.30
- blue: lo [0, 9, 30] … [0, 12, 36], hi [122, 111, 179] … [130, 114, 187]; fullness(8) 0.21–0.24

Per-image numbers: `per_image.csv`; per-condition table: `summary.csv`.
