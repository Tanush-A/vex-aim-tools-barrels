# The judged round (PREREG.md), against today's default (fixed colors, detector, stripe by contrast)

154 ordinary train frames, 172 placements, 8 places. Margins `results/baseline/margins.json` (re-measured 2026-11-27 with contrast in the
default): found better above +1.0, worse below -2.8; boxes not on their barrel worse above +2.1. A PASS under +6 is WEAK.

| candidate | verdict | found, placements (per frame) | gained / lost | boxes not on their barrel | empty frames (clean) | places that moved |
|---|---|---|---|---|---|---|
| `cut` (in-sample) | PASS, WEAK | 156.6 -> 158.0, +1.3 (277 -> 279) | 2 / 0 | 2.4 -> 2.4 | 0 -> 0 | home_ottoman +0.3, abp_white +1.0 |
| `cut+bulge` (in-sample) | NO CLEAR DIFFERENCE | 156.6 -> 157.6, +1.0 (277 -> 278) | 1 / 0 | 2.4 -> 2.4 | 0 -> 0 | abp_white +1.0 |
| `slack` (in-sample) | PASS, WEAK | 156.6 -> 159.0, +2.3 (277 -> 280) | 3 / 0 | 2.4 -> 2.4 | 0 -> 0 | home_ottoman +0.3, abp_white +2.0 |
| `loose` (in-sample) | PASS, WEAK | 156.6 -> 159.0, +2.3 (277 -> 280); report-only +1 (window_black) | 3 / 0 | 2.4 -> 2.4 | 0 -> 0 | home_ottoman +0.3, abp_white +2.0 |
| `fit` (leave one place out) | PASS, WEAK | 156.6 -> 158.0, +1.3 (277 -> 279) | 2 / 0 | 2.4 -> 2.4 | 0 -> 0 | home_ottoman +0.3, abp_white +1.0 |

`fit` chose `slack` in 8 of 9 folds and `cut` when abp_white was held out (the only place where `slack` gains over `cut` is
abp_white itself, `occlx_03`), so held out `occlx_03` is not found.

Gained barrels (all arms that gain them): `lampcool6_ottoman_occl_02` #1 (all but `cut+bulge`), `window_abpwhite_occlx_02` #1 (all),
`window_abpwhite_occlx_03` #1 (`slack`, `loose` in-sample only). Every judgement: `judge_<name>/judge.md`, `judge.json`, `changes.csv`.
