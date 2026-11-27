# The bottom edge: every candidate, judged two ways (1ccdbaf)

`python barrels/experiments/2026-11-26_bottom/run.py` (plan: `../../experiments/2026-11-26_bottom/PREREG.md`; the yardstick alone: `yardstick.md`). 154 ordinary train frames (172 placements, 307 barrels); 77 extreme frames reported, never judged. Test frames never opened. Every verdict is `judge.compare` with the stored margins (found better above +4.0 placements, worse below -10.9; boxes not on their barrel worse above +1.85).

The candidates (all off by default):

- `low`: `--cand-det bottom_rule=low`
- `both`: `--cand-det bottom_rule=both`
- `predicted`: `--cand-det bottom_rule=predicted`
- `rows`: `--cand-det bottom_rows=0.5`
- `rows+low`: `--cand-det bottom_rows=0.5,bottom_rule=low`
- `low_uncut`: `--cand-det bottom_rule=low_uncut`

The color steps:

- `fixed`: the fixed color model (what runs today)
- `s20`: both saturation floors lowered by 20 (orange 140 -> 120, blue 113 -> 93)
- `s40`: both saturation floors lowered by 40 (orange 100, blue 73)
- `hue3`: both hue ranges widened by 3 at each end (orange 0-16, blue 100-122)
- `dil1`: the fixed model's mask with one pixel added around each color (3 x 3 dilation)
- `hand`: Tanush's hand thresholds: per condition the median of its slider labels (others keep the fixed model)

## 1. Every candidate at every color step, against today's detector on the same masks

`fixed` is judgement 1 of the PREREG (the candidate against today's default). The five others are judgement 2. yardstick = boxes that are on their barrel and fail the strict rule with the bottom edge as the cause, per frame (too low / too high). Found per placement, with the change; per frame in brackets.

| color step | arm | found, placements | found, per frame | box off | **yardstick** (low / high) | boxes not on their barrel, per arrangement | on clean empty frames | gained / lost | verdict |
|---|---|---|---|---|---|---|---|---|---|
| `fixed` | `today` | 133.8 | 211 | 2 | **2** (1 / 1) | 1.9 (5) | 0 |  |  |
| `fixed` | `low` | 132.7 (-1.1) | 210 | 3 | **3** (0 / 3) | 1.9 (5) | 0 | 1 / 2 | **NO CLEAR DIFFERENCE** |
| `fixed` | `both` | 132.0 (-1.8) | 208 | 4 | **4** (2 / 2) | 1.9 (5) | 0 | 2 / 5 | **NO CLEAR DIFFERENCE** |
| `fixed` | `predicted` | 131.0 (-2.8) | 207 | 5 | **5** (2 / 3) | 1.9 (5) | 0 | 2 / 6 | **NO CLEAR DIFFERENCE** |
| `fixed` | `rows` | 126.7 (-7.0) | 202 | 10 | **10** (2 / 8) | 1.9 (5) | 0 | 2 / 11 | **FAIL** |
| `fixed` | `rows+low` | 127.7 (-6.0) | 203 | 9 | **9** (1 / 8) | 1.9 (5) | 0 | 2 / 10 | **NO CLEAR DIFFERENCE** |
| `fixed` | `low_uncut` | 133.7 (-0.1) | 211 | 2 | **2** (0 / 2) | 1.9 (5) | 0 | 1 / 1 | **NO CLEAR DIFFERENCE** |
| `s20` | `today` | 133.6 | 209 | 8 | **7** (4 / 3) | 7.3 (16) | 0 |  |  |
| `s20` | `low` | 133.0 (-0.6) | 210 | 7 | **6** (1 / 5) | 7.3 (16) | 0 | 3 / 2 | **NO CLEAR DIFFERENCE** |
| `s20` | `both` | 132.6 (-0.9) | 209 | 7 | **6** (2 / 4) | 7.3 (16) | 0 | 4 / 4 | **NO CLEAR DIFFERENCE** |
| `s20` | `predicted` | 132.6 (-0.9) | 209 | 7 | **6** (1 / 5) | 7.3 (16) | 0 | 5 / 5 | **NO CLEAR DIFFERENCE** |
| `s20` | `rows` | 129.2 (-4.4) | 204 | 11 | **11** (4 / 7) | 7.3 (16) | 0 | 4 / 9 | **FAIL** |
| `s20` | `rows+low` | 129.4 (-4.2) | 205 | 10 | **10** (1 / 9) | 7.3 (16) | 0 | 5 / 9 | **FAIL** |
| `s20` | `low_uncut` | 134.2 (+0.6) | 212 | 5 | **4** (1 / 3) | 7.3 (16) | 0 | 3 / 0 | **NO CLEAR DIFFERENCE** |
| `s40` | `today` | 125.4 | 204 | 14 | **13** (8 / 5) | 12.8 (27) | 0 |  |  |
| `s40` | `low` | 127.8 (+2.5) | 209 | 9 | **8** (1 / 7) | 12.8 (27) | 0 | 7 / 2 | **NO CLEAR DIFFERENCE** |
| `s40` | `both` | 128.2 (+2.8) | 208 | 10 | **9** (3 / 6) | 12.8 (27) | 0 | 8 / 4 | **NO CLEAR DIFFERENCE** |
| `s40` | `predicted` | 127.8 (+2.5) | 207 | 10 | **9** (2 / 7) | 12.5 (26) | 0 | 9 / 6 | **NO CLEAR DIFFERENCE** |
| `s40` | `rows` | 124.2 (-1.2) | 201 | 17 | **17** (6 / 11) | 11.6 (25) | 0 | 10 / 13 | **NO CLEAR DIFFERENCE** |
| `s40` | `rows+low` | 126.6 (+1.2) | 205 | 13 | **13** (2 / 11) | 11.6 (25) | 0 | 11 / 10 | **PASS** |
| `s40` | `low_uncut` | 128.8 (+3.5) | 210 | 8 | **7** (1 / 6) | 12.8 (27) | 0 | 7 / 1 | **NO CLEAR DIFFERENCE** |
| `hue3` | `today` | 142.1 | 230 | 4 | **4** (2 / 2) | 4.1 (11) | 0 |  |  |
| `hue3` | `low` | 143.3 (+1.2) | 232 | 2 | **2** (0 / 2) | 4.5 (12) | 0 | 2 / 0 | **NO CLEAR DIFFERENCE** |
| `hue3` | `both` | 143.7 (+1.5) | 235 | 0 | **0** (0 / 0) | 4.5 (12) | 0 | 6 / 1 | **NO CLEAR DIFFERENCE** |
| `hue3` | `predicted` | 141.3 (-0.8) | 232 | 3 | **3** (0 / 3) | 4.5 (12) | 0 | 6 / 4 | **NO CLEAR DIFFERENCE** |
| `hue3` | `rows` | 139.1 (-3.1) | 227 | 9 | **9** (1 / 8) | 4.7 (13) | 0 | 5 / 8 | **NO CLEAR DIFFERENCE** |
| `hue3` | `rows+low` | 140.1 (-2.1) | 228 | 8 | **8** (0 / 8) | 4.7 (13) | 0 | 5 / 7 | **NO CLEAR DIFFERENCE** |
| `hue3` | `low_uncut` | 143.3 (+1.2) | 232 | 2 | **2** (0 / 2) | 4.5 (12) | 0 | 2 / 0 | **NO CLEAR DIFFERENCE** |
| `dil1` | `today` | 136.6 | 217 | 8 | **7** (2 / 5) | 7.3 (16) | 0 |  |  |
| `dil1` | `low` | 134.4 (-2.1) | 215 | 10 | **9** (1 / 8) | 6.3 (15) | 0 | 1 / 3 | **NO CLEAR DIFFERENCE** |
| `dil1` | `both` | 133.8 (-2.8) | 215 | 10 | **9** (2 / 7) | 6.3 (15) | 0 | 2 / 4 | **NO CLEAR DIFFERENCE** |
| `dil1` | `predicted` | 135.8 (-0.8) | 217 | 7 | **6** (0 / 6) | 6.3 (15) | 0 | 4 / 4 | **NO CLEAR DIFFERENCE** |
| `dil1` | `rows` | 131.1 (-5.5) | 211 | 11 | **10** (1 / 9) | 5.9 (13) | 0 | 5 / 11 | **FAIL** |
| `dil1` | `rows+low` | 131.8 (-4.7) | 211 | 11 | **10** (0 / 10) | 5.9 (13) | 0 | 3 / 9 | **NO CLEAR DIFFERENCE** |
| `dil1` | `low_uncut` | 136.4 (-0.1) | 217 | 8 | **7** (1 / 6) | 6.3 (15) | 0 | 1 / 1 | **NO CLEAR DIFFERENCE** |
| `hand` | `today` | 156.8 | 281 | 4 | **4** (1 / 3) | 1.5 (3) | 0 |  |  |
| `hand` | `low` | 157.6 (+0.8) | 281 | 4 | **4** (0 / 4) | 1.5 (3) | 0 | 1 / 1 | **NO CLEAR DIFFERENCE** |
| `hand` | `both` | 157.6 (+0.8) | 283 | 3 | **3** (0 / 3) | 1.2 (2) | 0 | 4 / 2 | **NO CLEAR DIFFERENCE** |
| `hand` | `predicted` | 155.2 (-1.7) | 280 | 6 | **6** (0 / 6) | 1.2 (2) | 0 | 5 / 6 | **NO CLEAR DIFFERENCE** |
| `hand` | `rows` | 153.8 (-3.1) | 275 | 12 | **12** (0 / 12) | 1.2 (2) | 0 | 4 / 10 | **NO CLEAR DIFFERENCE** |
| `hand` | `rows+low` | 153.8 (-3.1) | 275 | 12 | **12** (0 / 12) | 1.2 (2) | 0 | 4 / 10 | **NO CLEAR DIFFERENCE** |
| `hand` | `low_uncut` | 157.6 (+0.8) | 281 | 4 | **4** (0 / 4) | 1.5 (3) | 0 | 1 / 1 | **NO CLEAR DIFFERENCE** |

## 2. The five conditions of the PREREG

Today: the yardstick summed over the five "more paint" steps = 35; found summed over them = 694.5 placements.

| candidate | (a) fixed colors not FAIL | (b) no FAIL on the five steps | (c) yardstick sum lower | (d) found sum higher | (e) fixed colors: median bottom error, near / far, today -> candidate | works |
|---|---|---|---|---|---|---|
| `low` | yes (NO CLEAR DIFFERENCE) | yes | yes (29 against 35) | yes (696.2 against 694.5, +1.7) | yes (1.0 -> 1.0 px / 1.0 -> 1.0 px) | **yes** |
| `both` | yes (NO CLEAR DIFFERENCE) | yes | yes (27 against 35) | yes (695.8 against 694.5, +1.4) | yes (1.0 -> 1.0 px / 1.0 -> 1.0 px) | **yes** |
| `predicted` | yes (NO CLEAR DIFFERENCE) | yes | yes (30 against 35) | **no** (692.7 against 694.5, -1.7) | **no** (1.0 -> 2.0 px / 1.0 -> 1.0 px) | no |
| `rows` | **no** (FAIL) | **no** | **no** (59 against 35) | **no** (677.2 against 694.5, -17.2) | **no** (1.0 -> 2.0 px / 1.0 -> 1.0 px) | no |
| `rows+low` | yes (NO CLEAR DIFFERENCE) | **no** | **no** (53 against 35) | **no** (681.6 against 694.5, -12.8) | **no** (1.0 -> 2.0 px / 1.0 -> 1.0 px) | no |
| `low_uncut` | yes (NO CLEAR DIFFERENCE) | yes | yes (24 against 35) | yes (700.4 against 694.5, +5.9) | yes (1.0 -> 1.0 px / 1.0 -> 1.0 px) | **yes** |

**Recommended by the PREREG's rule: `low_uncut` (`--cand-det bottom_rule=low_uncut`).**

## 3. The bottom-edge error against the labels, before and after

The box's bottom row minus the true one, on the barrels that have a box on them in BOTH arms and a measurable true bottom (inside the frame, not flagged `bottom_estimated`). near = a true box at least 40 px tall. Each cell: median / 90th percentile of the absolute error in px, the same in % of the true height, and the share outside the scorer's tolerance. "moved" = boxes whose bottom row differs between the two arms.

| color step | candidate | barrels (moved) | near: today | near: candidate | far: today | far: candidate |
|---|---|---|---|---|---|---|
| `fixed` | `low` | 194 (9) | 1.0 / 3.0 px, 1.9 / 5.4 %, 1.1 % out | 1.0 / 3.0 px, 2.0 / 5.8 %, 1.7 % out | 1.0 / 1.3 px, 2.9 / 4.0 %, 0.0 % out | 1.0 / 1.3 px, 2.9 / 4.0 %, 0.0 % out |
| `fixed` | `both` | 193 (12) | 1.0 / 3.0 px, 1.9 / 5.4 %, 1.1 % out | 1.0 / 3.0 px, 2.0 / 5.9 %, 2.3 % out | 1.0 / 1.3 px, 2.9 / 4.0 %, 0.0 % out | 1.0 / 1.3 px, 2.9 / 4.0 %, 0.0 % out |
| `fixed` | `predicted` | 193 (150) | 1.0 / 3.0 px, 1.9 / 5.4 %, 1.1 % out | 2.0 / 5.6 px, 3.8 / 7.4 %, 2.9 % out | 1.0 / 1.3 px, 2.9 / 4.0 %, 0.0 % out | 1.0 / 1.0 px, 3.1 / 3.4 %, 0.0 % out |
| `fixed` | `rows` | 193 (154) | 1.0 / 3.0 px, 1.9 / 5.4 %, 1.1 % out | 2.0 / 4.0 px, 2.8 / 6.3 %, 5.1 % out | 1.0 / 1.3 px, 2.9 / 4.0 %, 0.0 % out | 1.0 / 2.0 px, 3.4 / 5.9 %, 5.6 % out |
| `fixed` | `rows+low` | 193 (152) | 1.0 / 3.0 px, 1.9 / 5.4 %, 1.1 % out | 2.0 / 4.6 px, 2.8 / 6.3 %, 5.1 % out | 1.0 / 1.3 px, 2.9 / 4.0 %, 0.0 % out | 1.0 / 2.0 px, 3.1 / 5.5 %, 0.0 % out |
| `fixed` | `low_uncut` | 194 (4) | 1.0 / 3.0 px, 1.9 / 5.4 %, 1.1 % out | 1.0 / 3.0 px, 2.0 / 5.4 %, 1.1 % out | 1.0 / 1.3 px, 2.9 / 4.0 %, 0.0 % out | 1.0 / 1.3 px, 2.9 / 4.0 %, 0.0 % out |
| `s20` | `low` | 197 (15) | 1.0 / 4.0 px, 2.1 / 6.1 %, 3.9 % out | 1.0 / 4.0 px, 2.2 / 5.9 %, 3.4 % out | 1.0 / 2.0 px, 3.3 / 6.1 %, 0.0 % out | 1.0 / 2.0 px, 3.3 / 6.1 %, 0.0 % out |
| `s20` | `both` | 196 (17) | 1.0 / 4.0 px, 2.1 / 6.1 %, 4.0 % out | 1.0 / 4.0 px, 2.2 / 5.9 %, 3.4 % out | 1.0 / 2.0 px, 3.3 / 6.1 %, 0.0 % out | 1.0 / 2.0 px, 3.3 / 6.1 %, 0.0 % out |
| `s20` | `predicted` | 196 (153) | 1.0 / 4.0 px, 2.1 / 6.1 %, 4.0 % out | 2.0 / 5.0 px, 3.8 / 7.4 %, 3.4 % out | 1.0 / 2.0 px, 3.3 / 6.1 %, 0.0 % out | 1.0 / 1.2 px, 3.0 / 3.8 %, 0.0 % out |
| `s20` | `rows` | 196 (146) | 1.0 / 4.0 px, 2.1 / 6.1 %, 4.0 % out | 2.0 / 5.0 px, 2.9 / 7.3 %, 6.2 % out | 1.0 / 2.0 px, 3.3 / 6.1 %, 0.0 % out | 1.0 / 2.0 px, 3.3 / 5.3 %, 0.0 % out |
| `s20` | `rows+low` | 196 (147) | 1.0 / 4.0 px, 2.1 / 6.1 %, 4.0 % out | 2.0 / 5.0 px, 2.7 / 7.2 %, 5.6 % out | 1.0 / 2.0 px, 3.3 / 6.1 %, 0.0 % out | 1.0 / 2.0 px, 3.3 / 5.3 %, 0.0 % out |
| `s20` | `low_uncut` | 197 (10) | 1.0 / 4.0 px, 2.1 / 6.1 %, 3.9 % out | 1.0 / 3.0 px, 2.1 / 5.9 %, 2.2 % out | 1.0 / 2.0 px, 3.3 / 6.1 %, 0.0 % out | 1.0 / 2.0 px, 3.3 / 6.1 %, 0.0 % out |
| `s40` | `low` | 201 (24) | 2.0 / 5.0 px, 2.5 / 7.7 %, 6.0 % out | 2.0 / 5.0 px, 2.5 / 7.1 %, 4.4 % out | 1.0 / 3.6 px, 3.4 / 11.8 %, 11.1 % out | 1.0 / 2.3 px, 3.1 / 7.2 %, 0.0 % out |
| `s40` | `both` | 201 (28) | 2.0 / 5.0 px, 2.5 / 7.7 %, 6.0 % out | 2.0 / 5.0 px, 2.5 / 7.7 %, 4.9 % out | 1.0 / 3.6 px, 3.4 / 11.8 %, 11.1 % out | 1.0 / 2.3 px, 3.1 / 7.2 %, 0.0 % out |
| `s40` | `predicted` | 200 (146) | 1.5 / 5.0 px, 2.5 / 7.8 %, 6.0 % out | 2.0 / 6.0 px, 3.9 / 8.1 %, 4.9 % out | 1.0 / 3.6 px, 3.4 / 11.8 %, 11.1 % out | 1.0 / 1.3 px, 3.1 / 4.0 %, 0.0 % out |
| `s40` | `rows` | 199 (154) | 2.0 / 5.0 px, 2.5 / 7.8 %, 6.1 % out | 2.0 / 6.0 px, 3.3 / 9.6 %, 8.8 % out | 1.0 / 3.6 px, 3.4 / 11.8 %, 11.1 % out | 1.0 / 2.3 px, 3.4 / 6.9 %, 5.6 % out |
| `s40` | `rows+low` | 199 (149) | 2.0 / 5.0 px, 2.5 / 7.8 %, 6.1 % out | 2.0 / 5.0 px, 3.3 / 8.0 %, 7.2 % out | 1.0 / 3.6 px, 3.4 / 11.8 %, 11.1 % out | 1.0 / 2.0 px, 3.3 / 5.6 %, 0.0 % out |
| `s40` | `low_uncut` | 201 (22) | 2.0 / 5.0 px, 2.5 / 7.7 %, 6.0 % out | 1.0 / 5.0 px, 2.5 / 7.1 %, 3.8 % out | 1.0 / 3.6 px, 3.4 / 11.8 %, 11.1 % out | 1.0 / 2.3 px, 3.1 / 7.2 %, 0.0 % out |
| `hue3` | `low` | 213 (8) | 1.0 / 3.0 px, 1.9 / 5.6 %, 1.0 % out | 1.0 / 3.0 px, 1.9 / 5.8 %, 0.0 % out | 1.0 / 1.0 px, 3.1 / 3.4 %, 0.0 % out | 1.0 / 1.0 px, 3.1 / 3.4 %, 0.0 % out |
| `hue3` | `both` | 212 (8) | 1.0 / 3.0 px, 1.9 / 5.6 %, 1.0 % out | 1.0 / 3.0 px, 1.9 / 5.8 %, 0.0 % out | 1.0 / 1.0 px, 3.1 / 3.4 %, 0.0 % out | 1.0 / 1.0 px, 3.1 / 3.4 %, 0.0 % out |
| `hue3` | `predicted` | 212 (174) | 1.0 / 3.0 px, 1.9 / 5.6 %, 1.0 % out | 2.0 / 5.7 px, 3.6 / 6.7 %, 1.5 % out | 1.0 / 1.0 px, 3.1 / 3.4 %, 0.0 % out | 1.0 / 1.0 px, 2.9 / 3.4 %, 0.0 % out |
| `hue3` | `rows` | 213 (180) | 1.0 / 3.0 px, 1.9 / 5.6 %, 1.0 % out | 2.0 / 5.0 px, 3.3 / 6.4 %, 3.6 % out | 1.0 / 1.0 px, 3.1 / 3.4 %, 0.0 % out | 1.0 / 3.0 px, 3.4 / 8.0 %, 5.6 % out |
| `hue3` | `rows+low` | 213 (178) | 1.0 / 3.0 px, 1.9 / 5.6 %, 1.0 % out | 2.0 / 5.0 px, 3.3 / 6.4 %, 3.6 % out | 1.0 / 1.0 px, 3.1 / 3.4 %, 0.0 % out | 1.0 / 2.3 px, 3.4 / 6.9 %, 0.0 % out |
| `hue3` | `low_uncut` | 213 (4) | 1.0 / 3.0 px, 1.9 / 5.6 %, 1.0 % out | 1.0 / 3.0 px, 1.8 / 5.4 %, 0.0 % out | 1.0 / 1.0 px, 3.1 / 3.4 %, 0.0 % out | 1.0 / 1.0 px, 3.1 / 3.4 %, 0.0 % out |
| `dil1` | `low` | 204 (10) | 1.0 / 3.7 px, 1.9 / 6.1 %, 3.8 % out | 1.0 / 4.7 px, 2.1 / 8.1 %, 4.9 % out | 1.0 / 2.0 px, 3.1 / 6.9 %, 0.0 % out | 1.0 / 2.0 px, 3.1 / 6.9 %, 0.0 % out |
| `dil1` | `both` | 204 (13) | 1.0 / 3.7 px, 1.9 / 6.1 %, 3.8 % out | 1.0 / 4.7 px, 2.1 / 8.1 %, 4.9 % out | 1.0 / 2.0 px, 3.1 / 6.9 %, 0.0 % out | 1.0 / 2.0 px, 3.1 / 6.9 %, 0.0 % out |
| `dil1` | `predicted` | 203 (167) | 1.0 / 3.8 px, 1.9 / 6.1 %, 3.8 % out | 2.0 / 5.0 px, 3.8 / 7.2 %, 3.3 % out | 1.0 / 2.0 px, 3.1 / 6.9 %, 0.0 % out | 1.0 / 1.0 px, 3.0 / 3.4 %, 0.0 % out |
| `dil1` | `rows` | 202 (150) | 1.0 / 3.0 px, 1.9 / 6.1 %, 3.3 % out | 1.0 / 4.9 px, 2.2 / 6.4 %, 4.9 % out | 1.0 / 2.0 px, 3.1 / 6.9 %, 0.0 % out | 1.0 / 2.0 px, 3.1 / 6.9 %, 5.0 % out |
| `dil1` | `rows+low` | 202 (147) | 1.0 / 3.0 px, 1.9 / 6.1 %, 3.3 % out | 1.0 / 5.0 px, 2.3 / 7.2 %, 5.5 % out | 1.0 / 2.0 px, 3.1 / 6.9 %, 0.0 % out | 1.0 / 2.0 px, 3.0 / 6.9 %, 0.0 % out |
| `dil1` | `low_uncut` | 204 (5) | 1.0 / 3.7 px, 1.9 / 6.1 %, 3.8 % out | 1.0 / 4.0 px, 1.9 / 6.1 %, 3.8 % out | 1.0 / 2.0 px, 3.1 / 6.9 %, 0.0 % out | 1.0 / 2.0 px, 3.1 / 6.9 %, 0.0 % out |
| `hand` | `low` | 263 (6) | 1.0 / 3.0 px, 2.0 / 5.4 %, 1.3 % out | 1.0 / 3.0 px, 2.0 / 5.6 %, 1.3 % out | 1.0 / 2.0 px, 3.0 / 5.7 %, 0.0 % out | 1.0 / 2.0 px, 3.0 / 5.7 %, 0.0 % out |
| `hand` | `both` | 262 (7) | 1.0 / 3.0 px, 1.9 / 5.4 %, 1.3 % out | 1.0 / 3.0 px, 2.0 / 5.4 %, 1.3 % out | 1.0 / 2.0 px, 3.0 / 5.7 %, 0.0 % out | 1.0 / 2.0 px, 3.0 / 5.7 %, 0.0 % out |
| `hand` | `predicted` | 262 (209) | 1.0 / 3.0 px, 1.9 / 5.4 %, 1.3 % out | 2.0 / 6.0 px, 3.6 / 7.2 %, 2.6 % out | 1.0 / 2.0 px, 3.0 / 5.7 %, 0.0 % out | 1.0 / 1.0 px, 3.0 / 3.4 %, 0.0 % out |
| `hand` | `rows` | 263 (220) | 1.0 / 3.0 px, 2.0 / 5.4 %, 1.3 % out | 2.0 / 6.0 px, 3.6 / 7.3 %, 4.3 % out | 1.0 / 2.0 px, 3.0 / 5.7 %, 0.0 % out | 1.0 / 3.0 px, 3.3 / 8.0 %, 3.6 % out |
| `hand` | `rows+low` | 263 (219) | 1.0 / 3.0 px, 2.0 / 5.4 %, 1.3 % out | 2.0 / 6.0 px, 3.6 / 7.2 %, 4.3 % out | 1.0 / 2.0 px, 3.0 / 5.7 %, 0.0 % out | 1.0 / 3.0 px, 3.3 / 8.0 %, 3.6 % out |
| `hand` | `low_uncut` | 263 (6) | 1.0 / 3.0 px, 2.0 / 5.4 %, 1.3 % out | 1.0 / 3.0 px, 2.0 / 5.6 %, 1.3 % out | 1.0 / 2.0 px, 3.0 / 5.7 %, 0.0 % out | 1.0 / 2.0 px, 3.0 / 5.7 %, 0.0 % out |

Each arm on its own boxes (every box that is on a barrel with a measurable bottom; the sets differ a little between arms):

| color step | arm | near: boxes, error | far: boxes, error |
|---|---|---|---|
| `fixed` | `today` | 176: 1.0 / 3.0 px, 1.9 / 5.4 %, 1.1 % out | 18: 1.0 / 1.3 px, 2.9 / 4.0 %, 0.0 % out |
| `fixed` | `low` | 176: 1.0 / 3.0 px, 2.0 / 5.8 %, 1.7 % out | 18: 1.0 / 1.3 px, 2.9 / 4.0 %, 0.0 % out |
| `fixed` | `both` | 175: 1.0 / 3.0 px, 2.0 / 5.9 %, 2.3 % out | 18: 1.0 / 1.3 px, 2.9 / 4.0 %, 0.0 % out |
| `fixed` | `predicted` | 175: 2.0 / 5.6 px, 3.8 / 7.4 %, 2.9 % out | 18: 1.0 / 1.0 px, 3.1 / 3.4 %, 0.0 % out |
| `fixed` | `rows` | 175: 2.0 / 4.0 px, 2.8 / 6.3 %, 5.1 % out | 18: 1.0 / 2.0 px, 3.4 / 5.9 %, 5.6 % out |
| `fixed` | `rows+low` | 175: 2.0 / 4.6 px, 2.8 / 6.3 %, 5.1 % out | 18: 1.0 / 2.0 px, 3.1 / 5.5 %, 0.0 % out |
| `fixed` | `low_uncut` | 176: 1.0 / 3.0 px, 2.0 / 5.4 %, 1.1 % out | 18: 1.0 / 1.3 px, 2.9 / 4.0 %, 0.0 % out |
| `s20` | `today` | 178: 1.0 / 4.0 px, 2.1 / 6.1 %, 3.9 % out | 19: 1.0 / 2.0 px, 3.3 / 6.1 %, 0.0 % out |
| `s20` | `low` | 178: 1.0 / 4.0 px, 2.2 / 5.9 %, 3.4 % out | 19: 1.0 / 2.0 px, 3.3 / 6.1 %, 0.0 % out |
| `s20` | `both` | 177: 1.0 / 4.0 px, 2.2 / 5.9 %, 3.4 % out | 19: 1.0 / 2.0 px, 3.3 / 6.1 %, 0.0 % out |
| `s20` | `predicted` | 177: 2.0 / 5.0 px, 3.8 / 7.4 %, 3.4 % out | 19: 1.0 / 1.2 px, 3.0 / 3.8 %, 0.0 % out |
| `s20` | `rows` | 177: 2.0 / 5.0 px, 2.9 / 7.3 %, 6.2 % out | 19: 1.0 / 2.0 px, 3.3 / 5.3 %, 0.0 % out |
| `s20` | `rows+low` | 177: 2.0 / 5.0 px, 2.7 / 7.2 %, 5.6 % out | 19: 1.0 / 2.0 px, 3.3 / 5.3 %, 0.0 % out |
| `s20` | `low_uncut` | 178: 1.0 / 3.0 px, 2.1 / 5.9 %, 2.2 % out | 19: 1.0 / 2.0 px, 3.3 / 6.1 %, 0.0 % out |
| `s40` | `today` | 183: 2.0 / 5.0 px, 2.5 / 7.7 %, 6.0 % out | 18: 1.0 / 3.6 px, 3.4 / 11.8 %, 11.1 % out |
| `s40` | `low` | 183: 2.0 / 5.0 px, 2.5 / 7.1 %, 4.4 % out | 18: 1.0 / 2.3 px, 3.1 / 7.2 %, 0.0 % out |
| `s40` | `both` | 183: 2.0 / 5.0 px, 2.5 / 7.7 %, 4.9 % out | 18: 1.0 / 2.3 px, 3.1 / 7.2 %, 0.0 % out |
| `s40` | `predicted` | 182: 2.0 / 6.0 px, 3.9 / 8.1 %, 4.9 % out | 18: 1.0 / 1.3 px, 3.1 / 4.0 %, 0.0 % out |
| `s40` | `rows` | 182: 2.0 / 5.9 px, 3.3 / 9.5 %, 8.8 % out | 19: 1.0 / 2.2 px, 3.3 / 6.7 %, 5.3 % out |
| `s40` | `rows+low` | 182: 2.0 / 5.0 px, 3.3 / 8.0 %, 7.1 % out | 19: 1.0 / 2.0 px, 3.3 / 5.5 %, 0.0 % out |
| `s40` | `low_uncut` | 183: 1.0 / 5.0 px, 2.5 / 7.1 %, 3.8 % out | 18: 1.0 / 2.3 px, 3.1 / 7.2 %, 0.0 % out |
| `hue3` | `today` | 195: 1.0 / 3.0 px, 1.9 / 5.6 %, 1.0 % out | 18: 1.0 / 1.0 px, 3.1 / 3.4 %, 0.0 % out |
| `hue3` | `low` | 195: 1.0 / 3.0 px, 1.9 / 5.8 %, 0.0 % out | 18: 1.0 / 1.0 px, 3.1 / 3.4 %, 0.0 % out |
| `hue3` | `both` | 194: 1.0 / 3.0 px, 1.9 / 5.8 %, 0.0 % out | 18: 1.0 / 1.0 px, 3.1 / 3.4 %, 0.0 % out |
| `hue3` | `predicted` | 194: 2.0 / 5.7 px, 3.6 / 6.7 %, 1.5 % out | 18: 1.0 / 1.0 px, 2.9 / 3.4 %, 0.0 % out |
| `hue3` | `rows` | 195: 2.0 / 5.0 px, 3.3 / 6.4 %, 3.6 % out | 18: 1.0 / 3.0 px, 3.4 / 8.0 %, 5.6 % out |
| `hue3` | `rows+low` | 195: 2.0 / 5.0 px, 3.3 / 6.4 %, 3.6 % out | 18: 1.0 / 2.3 px, 3.4 / 6.9 %, 0.0 % out |
| `hue3` | `low_uncut` | 195: 1.0 / 3.0 px, 1.8 / 5.4 %, 0.0 % out | 18: 1.0 / 1.0 px, 3.1 / 3.4 %, 0.0 % out |
| `dil1` | `today` | 184: 1.0 / 3.7 px, 1.9 / 6.1 %, 3.8 % out | 20: 1.0 / 2.0 px, 3.1 / 6.9 %, 0.0 % out |
| `dil1` | `low` | 184: 1.0 / 4.7 px, 2.1 / 8.1 %, 4.9 % out | 20: 1.0 / 2.0 px, 3.1 / 6.9 %, 0.0 % out |
| `dil1` | `both` | 184: 1.0 / 4.7 px, 2.1 / 8.1 %, 4.9 % out | 20: 1.0 / 2.0 px, 3.1 / 6.9 %, 0.0 % out |
| `dil1` | `predicted` | 183: 2.0 / 5.0 px, 3.8 / 7.2 %, 3.3 % out | 20: 1.0 / 1.0 px, 3.0 / 3.4 %, 0.0 % out |
| `dil1` | `rows` | 182: 1.0 / 4.9 px, 2.2 / 6.4 %, 4.9 % out | 20: 1.0 / 2.0 px, 3.1 / 6.9 %, 5.0 % out |
| `dil1` | `rows+low` | 182: 1.0 / 5.0 px, 2.3 / 7.2 %, 5.5 % out | 20: 1.0 / 2.0 px, 3.0 / 6.9 %, 0.0 % out |
| `dil1` | `low_uncut` | 184: 1.0 / 4.0 px, 1.9 / 6.1 %, 3.8 % out | 20: 1.0 / 2.0 px, 3.1 / 6.9 %, 0.0 % out |
| `hand` | `today` | 235: 1.0 / 3.0 px, 2.0 / 5.4 %, 1.3 % out | 28: 1.0 / 2.0 px, 3.0 / 5.7 %, 0.0 % out |
| `hand` | `low` | 235: 1.0 / 3.0 px, 2.0 / 5.6 %, 1.3 % out | 28: 1.0 / 2.0 px, 3.0 / 5.7 %, 0.0 % out |
| `hand` | `both` | 234: 1.0 / 3.0 px, 2.0 / 5.4 %, 1.3 % out | 28: 1.0 / 2.0 px, 3.0 / 5.7 %, 0.0 % out |
| `hand` | `predicted` | 234: 2.0 / 6.0 px, 3.6 / 7.2 %, 2.6 % out | 28: 1.0 / 1.0 px, 3.0 / 3.4 %, 0.0 % out |
| `hand` | `rows` | 235: 2.0 / 6.0 px, 3.6 / 7.3 %, 4.3 % out | 28: 1.0 / 3.0 px, 3.3 / 8.0 %, 3.6 % out |
| `hand` | `rows+low` | 235: 2.0 / 6.0 px, 3.6 / 7.2 %, 4.3 % out | 28: 1.0 / 3.0 px, 3.3 / 8.0 %, 3.6 % out |
| `hand` | `low_uncut` | 235: 1.0 / 3.0 px, 2.0 / 5.6 %, 1.3 % out | 28: 1.0 / 2.0 px, 3.0 / 5.7 %, 0.0 % out |

## 4. The extreme conditions (report only, never judged)

| color step | arm | found, placements | found, per frame | box off | yardstick (low / high) | boxes not on their barrel |
|---|---|---|---|---|---|---|
| `fixed` | `today` | 7.2 of 62 | 13 of 167 | 4 | 3 (1 / 2) | 4 |
| `fixed` | `low` | 7.2 of 62 | 13 of 167 | 4 | 3 (1 / 2) | 4 |
| `fixed` | `both` | 7.0 of 62 | 12 of 167 | 5 | 4 (2 / 2) | 4 |
| `fixed` | `predicted` | 6.0 of 62 | 11 of 167 | 5 | 4 (2 / 2) | 4 |
| `fixed` | `rows` | 6.2 of 62 | 12 of 167 | 4 | 3 (1 / 2) | 4 |
| `fixed` | `rows+low` | 6.2 of 62 | 12 of 167 | 4 | 3 (1 / 2) | 4 |
| `fixed` | `low_uncut` | 7.2 of 62 | 13 of 167 | 4 | 3 (1 / 2) | 4 |
| `s20` | `today` | 12.7 of 62 | 21 of 167 | 7 | 7 (5 / 2) | 6 |
| `s20` | `low` | 11.7 of 62 | 20 of 167 | 8 | 8 (5 / 3) | 6 |
| `s20` | `both` | 11.7 of 62 | 20 of 167 | 8 | 8 (5 / 3) | 6 |
| `s20` | `predicted` | 11.7 of 62 | 20 of 167 | 8 | 8 (5 / 3) | 6 |
| `s20` | `rows` | 12.7 of 62 | 21 of 167 | 7 | 7 (5 / 2) | 5 |
| `s20` | `rows+low` | 12.7 of 62 | 21 of 167 | 7 | 7 (5 / 2) | 5 |
| `s20` | `low_uncut` | 11.7 of 62 | 20 of 167 | 8 | 8 (5 / 3) | 6 |
| `s40` | `today` | 13.0 of 62 | 23 of 167 | 10 | 10 (5 / 5) | 6 |
| `s40` | `low` | 13.0 of 62 | 23 of 167 | 10 | 10 (5 / 5) | 6 |
| `s40` | `both` | 12.8 of 62 | 22 of 167 | 11 | 11 (6 / 5) | 6 |
| `s40` | `predicted` | 12.8 of 62 | 22 of 167 | 11 | 11 (6 / 5) | 6 |
| `s40` | `rows` | 14.0 of 62 | 24 of 167 | 10 | 10 (5 / 5) | 5 |
| `s40` | `rows+low` | 14.0 of 62 | 24 of 167 | 10 | 10 (5 / 5) | 5 |
| `s40` | `low_uncut` | 13.0 of 62 | 23 of 167 | 10 | 10 (5 / 5) | 6 |
| `hue3` | `today` | 14.0 of 62 | 24 of 167 | 6 | 4 (2 / 2) | 5 |
| `hue3` | `low` | 13.8 of 62 | 23 of 167 | 6 | 4 (1 / 3) | 5 |
| `hue3` | `both` | 14.8 of 62 | 24 of 167 | 6 | 4 (1 / 3) | 5 |
| `hue3` | `predicted` | 14.8 of 62 | 24 of 167 | 6 | 4 (0 / 4) | 5 |
| `hue3` | `rows` | 15.0 of 62 | 25 of 167 | 4 | 2 (0 / 2) | 4 |
| `hue3` | `rows+low` | 15.0 of 62 | 25 of 167 | 4 | 2 (0 / 2) | 4 |
| `hue3` | `low_uncut` | 13.8 of 62 | 23 of 167 | 6 | 4 (1 / 3) | 5 |
| `dil1` | `today` | 10.3 of 62 | 17 of 167 | 7 | 5 (3 / 2) | 2 |
| `dil1` | `low` | 11.3 of 62 | 18 of 167 | 6 | 4 (2 / 2) | 2 |
| `dil1` | `both` | 11.3 of 62 | 18 of 167 | 6 | 4 (2 / 2) | 2 |
| `dil1` | `predicted` | 11.0 of 62 | 16 of 167 | 8 | 6 (2 / 4) | 2 |
| `dil1` | `rows` | 10.2 of 62 | 16 of 167 | 7 | 5 (1 / 4) | 2 |
| `dil1` | `rows+low` | 10.2 of 62 | 16 of 167 | 7 | 5 (1 / 4) | 2 |
| `dil1` | `low_uncut` | 11.3 of 62 | 18 of 167 | 6 | 4 (2 / 2) | 2 |
| `hand` | `today` | 6.2 of 62 | 12 of 167 | 4 | 3 (1 / 2) | 4 |
| `hand` | `low` | 6.2 of 62 | 12 of 167 | 4 | 3 (1 / 2) | 4 |
| `hand` | `both` | 7.0 of 62 | 12 of 167 | 5 | 4 (2 / 2) | 4 |
| `hand` | `predicted` | 6.0 of 62 | 11 of 167 | 5 | 4 (2 / 2) | 4 |
| `hand` | `rows` | 6.2 of 62 | 12 of 167 | 4 | 3 (1 / 2) | 4 |
| `hand` | `rows+low` | 6.2 of 62 | 12 of 167 | 4 | 3 (1 / 2) | 4 |
| `hand` | `low_uncut` | 6.2 of 62 | 12 of 167 | 4 | 3 (1 / 2) | 4 |

## 5. Every barrel that changed (ordinary frames)

### `low`

- `fixed`: + 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off
- `s20`: + 4A8B_lampcool6_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_lampmid3_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_window_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampcool6_glass_edge_01 #1 blue at [0, 145, 40, 237]: found -> off
- `s40`: + 4A8B_window_light_far_02 #2 orange at [244, 105, 273, 135]: off -> found; + 4A8B_window_light_far_02 #4 blue at [433, 106, 468, 139]: off -> found; + 4A8B_lampcool6_glass_core_01 #2 blue at [176, 123, 233, 185]: off -> found; + 4A8B_lampmid3_glass_core_01 #4 blue at [371, 111, 412, 151]: off -> found; + 4A8B_lampmid6_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_lampmid6_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found; + 4A8B_window_abpwhite_occlx_09 #1 blue at [106, 114, 152, 164]: off -> found; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampwarm6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off
- `hue3`: + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: off -> found; + 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found
- `dil1`: + 4A8B_window_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; - 4A8B_campus_light_edge_01 #1 orange at [602, 143, 638, 228]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off
- `hand`: + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: off -> found; - 4A8B_lampwarm6_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: found -> off

### `both`

- `fixed`: + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found; + 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found; - 4A8B_window_light_cluster_01 #1 orange at [313, 115, 356, 164]: found -> missed; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampcool6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off; - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off; - 4A8B_lampmid6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off
- `s20`: + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found; + 4A8B_lampcool6_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_lampmid3_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_window_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; - 4A8B_window_light_cluster_01 #1 orange at [313, 115, 356, 164]: found -> missed; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampcool6_glass_edge_01 #1 blue at [0, 145, 40, 237]: found -> off; - 4A8B_lampcool6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off
- `s40`: + 4A8B_window_light_far_02 #2 orange at [244, 105, 273, 135]: off -> found; + 4A8B_window_light_far_02 #4 blue at [433, 106, 468, 139]: off -> found; + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found; + 4A8B_lampcool6_glass_core_01 #2 blue at [176, 123, 233, 185]: off -> found; + 4A8B_lampmid3_glass_core_01 #4 blue at [371, 111, 412, 151]: off -> found; + 4A8B_lampmid6_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_lampmid6_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found; + 4A8B_window_abpwhite_occlx_09 #1 blue at [106, 114, 152, 164]: off -> found; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampcool6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off; - 4A8B_lampmid6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off; - 4A8B_lampwarm6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off
- `hue3`: + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: off -> found; + 4A8B_lampcool6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: off -> found; + 4A8B_lampmid6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found; + 4A8B_lampmid6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: off -> found; + 4A8B_lampwarm6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found; + 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found; - 4A8B_window_light_cluster_01 #1 orange at [313, 115, 356, 164]: found -> missed
- `dil1`: + 4A8B_lampcool6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: off -> found; + 4A8B_window_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; - 4A8B_window_light_cluster_01 #1 orange at [313, 115, 356, 164]: found -> off; - 4A8B_campus_light_edge_01 #1 orange at [602, 143, 638, 228]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off
- `hand`: + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: off -> found; + 4A8B_lampmid6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found; + 4A8B_lampmid6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: off -> found; + 4A8B_lampwarm6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found; - 4A8B_window_light_cluster_01 #1 orange at [313, 115, 356, 164]: found -> missed; - 4A8B_lampwarm6_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: found -> off

### `predicted`

- `fixed`: + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found; + 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found; - 4A8B_window_light_cluster_01 #1 orange at [313, 115, 356, 164]: found -> missed; - 4A8B_campus_light_edge_01 #1 orange at [602, 143, 638, 228]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampcool6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off; - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off; - 4A8B_lampmid6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off
- `s20`: + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found; + 4A8B_lampcool6_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_lampmid3_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_window_abpwhite_occlx_08 #1 orange at [111, 114, 160, 164]: off -> found; + 4A8B_window_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; - 4A8B_window_light_cluster_01 #1 orange at [313, 115, 356, 164]: found -> missed; - 4A8B_campus_light_edge_01 #1 orange at [602, 143, 638, 228]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampcool6_glass_edge_01 #1 blue at [0, 145, 40, 237]: found -> off; - 4A8B_lampcool6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off
- `s40`: + 4A8B_window_light_far_02 #2 orange at [244, 105, 273, 135]: off -> found; + 4A8B_window_light_far_02 #4 blue at [433, 106, 468, 139]: off -> found; + 4A8B_campus_light_cluster_02 #4 blue at [379, 117, 419, 163]: off -> found; + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found; + 4A8B_lampcool6_glass_core_01 #2 blue at [176, 123, 233, 185]: off -> found; + 4A8B_lampmid3_glass_core_01 #4 blue at [371, 111, 412, 151]: off -> found; + 4A8B_lampmid6_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_lampmid6_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found; + 4A8B_window_abpwhite_occlx_09 #1 blue at [106, 114, 152, 164]: off -> found; - 4A8B_campus_light_edge_01 #1 orange at [602, 143, 638, 228]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampcool6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> missed; - 4A8B_lampcool6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off; - 4A8B_lampmid6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off; - 4A8B_lampwarm6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off
- `hue3`: + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: off -> found; + 4A8B_lampcool6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: off -> found; + 4A8B_lampmid6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found; + 4A8B_lampmid6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: off -> found; + 4A8B_lampwarm6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found; + 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found; - 4A8B_window_light_cluster_01 #1 orange at [313, 115, 356, 164]: found -> missed; - 4A8B_campus_light_edge_01 #1 orange at [602, 143, 638, 228]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampcool6_ottoman_edge_01 #1 blue at [0, 141, 43, 229]: found -> off
- `dil1`: + 4A8B_campus_light_cluster_02 #4 blue at [379, 117, 419, 163]: off -> found; + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found; + 4A8B_lampcool6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: off -> found; + 4A8B_window_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; - 4A8B_window_light_cluster_01 #1 orange at [313, 115, 356, 164]: found -> missed; - 4A8B_campus_light_edge_01 #1 orange at [602, 143, 638, 228]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off
- `hand`: + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: off -> found; + 4A8B_lampmid3_bathtile_edge_01 #1 blue at [0, 127, 31, 196]: off -> found; + 4A8B_lampmid6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found; + 4A8B_lampmid6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: off -> found; + 4A8B_lampwarm6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found; - 4A8B_window_light_cluster_01 #1 orange at [313, 115, 356, 164]: found -> missed; - 4A8B_campus_light_edge_01 #1 orange at [602, 143, 638, 228]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampcool6_ottoman_edge_01 #1 blue at [0, 141, 43, 229]: found -> off; - 4A8B_lampmid6_ottoman_edge_01 #1 blue at [0, 141, 43, 229]: found -> off; - 4A8B_lampwarm6_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: found -> off

### `rows`

- `fixed`: + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found; + 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found; - 4A8B_campus_light_room_01 #1 blue at [64, 123, 125, 181]: found -> off; - 4A8B_both_abpgray_clutter_01 #1 blue at [34, 132, 110, 203]: found -> off; - 4A8B_both_abpgray_clutter_01 #4 orange at [506, 124, 579, 190]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_both_abpgray_occl_02 #1 blue at [366, 123, 422, 181]: found -> off; - 4A8B_lampcool6_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: found -> off; - 4A8B_lampcool6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off; - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off; - 4A8B_lampmid6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> missed; - 4A8B_overheaddim_palewood_core_01 #1 orange at [125, 137, 207, 223]: found -> off; - 4A8B_overheaddim_palewood_core_01 #3 orange at [364, 105, 396, 138]: found -> off
- `s20`: + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found; + 4A8B_lampmid3_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_lampmid3_glass_edge_01 #1 blue at [0, 145, 40, 237]: off -> found; + 4A8B_window_abpwhite_occlx_08 #1 orange at [111, 114, 160, 164]: off -> found; - 4A8B_both_abpgray_clutter_01 #1 blue at [34, 132, 110, 203]: found -> off; - 4A8B_both_abpgray_clutter_01 #4 orange at [506, 124, 579, 190]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_both_abpgray_occl_02 #1 blue at [366, 123, 422, 181]: found -> off; - 4A8B_lampcool6_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: found -> off; - 4A8B_lampcool6_glass_occl_02 #1 blue at [254, 114, 300, 163]: found -> off; - 4A8B_lampcool6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off; - 4A8B_overheaddim_palewood_close_01 #1 orange at [291, 243, 566, 480]: found -> missed; - 4A8B_overheaddim_palewood_core_01 #1 orange at [125, 137, 207, 223]: found -> off; ~ 4A8B_lampmid6_ottoman_occl_02 #1 orange at [225, 125, 286, 192]: off -> missed
- `s40`: + 4A8B_window_light_far_02 #2 orange at [244, 105, 273, 135]: off -> found; + 4A8B_campus_light_cluster_02 #4 blue at [379, 117, 419, 163]: off -> found; + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found; + 4A8B_lampcool6_glass_core_01 #2 blue at [176, 123, 233, 185]: off -> found; + 4A8B_lampmid3_glass_core_01 #4 blue at [371, 111, 412, 151]: off -> found; + 4A8B_lampmid6_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_lampmid6_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found; + 4A8B_overheaddim_palewood_core_01 #2 blue at [246, 111, 282, 148]: missed -> found; + 4A8B_window_abpwhite_occlx_09 #1 blue at [106, 114, 152, 164]: off -> found; + 4A8B_window_abpwhite_occlx_17 #1 blue at [0, 124, 19, 183]: missed -> found; - 4A8B_both_abpgray_clutter_01 #1 blue at [34, 132, 110, 203]: found -> off; - 4A8B_both_abpgray_clutter_01 #4 orange at [506, 124, 579, 190]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_both_abpgray_occl_02 #1 blue at [366, 123, 422, 181]: found -> off; - 4A8B_lampcool6_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: found -> off; - 4A8B_lampcool6_glass_core_01 #4 blue at [371, 111, 412, 151]: found -> off; - 4A8B_lampcool6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> missed; - 4A8B_lampcool6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off; - 4A8B_lampmid3_glass_clutter_01 #2 blue at [254, 114, 300, 163]: found -> off; - 4A8B_lampmid6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off; - 4A8B_lampwarm6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off; - 4A8B_overheaddim_palewood_core_01 #1 orange at [125, 137, 207, 223]: found -> off; - 4A8B_window_abpwhite_occlx_18 #1 orange at [102, 118, 153, 166]: found -> off; ~ 4A8B_lampmid6_ottoman_occl_02 #1 orange at [225, 125, 286, 192]: off -> missed
- `hue3`: + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: off -> found; + 4A8B_lampcool6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: off -> found; + 4A8B_lampmid6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found; + 4A8B_lampwarm6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found; + 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found; - 4A8B_campus_light_room_01 #1 blue at [64, 123, 125, 181]: found -> off; - 4A8B_both_abpgray_clutter_01 #1 blue at [34, 132, 110, 203]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampcool6_bathtile_edge_01 #1 blue at [0, 127, 31, 196]: found -> off; - 4A8B_lampmid6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: found -> off; - 4A8B_lampmid6_ottoman_edge_01 #1 blue at [0, 141, 43, 229]: found -> off; - 4A8B_lampmid6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off; - 4A8B_overheaddim_palewood_core_01 #3 orange at [364, 105, 396, 138]: found -> off; ~ 4A8B_window_light_cluster_01 #3 orange at [361, 117, 400, 163]: missed -> off; ~ 4A8B_lampmid6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: off -> missed
- `dil1`: + 4A8B_campus_light_cluster_02 #4 blue at [379, 117, 419, 163]: off -> found; + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found; + 4A8B_lampcool6_glass_edge_01 #1 blue at [0, 145, 40, 237]: off -> found; + 4A8B_window_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_window_glass_edge_01 #1 blue at [0, 145, 40, 237]: off -> found; - 4A8B_campus_light_room_01 #1 blue at [64, 123, 125, 181]: found -> off; - 4A8B_both_abpgray_clutter_01 #1 blue at [34, 132, 110, 203]: found -> off; - 4A8B_both_abpgray_clutter_01 #4 orange at [506, 124, 579, 190]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_both_abpgray_occl_02 #1 blue at [366, 123, 422, 181]: found -> off; - 4A8B_lampcool6_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: found -> off; - 4A8B_lampmid6_ottoman_clutter_01 #3 orange at [313, 141, 401, 236]: found -> missed; - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off; - 4A8B_overheaddim_palewood_close_01 #1 orange at [291, 243, 566, 480]: found -> missed; - 4A8B_overheaddim_palewood_core_01 #3 orange at [364, 105, 396, 138]: found -> off; - 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: found -> off; ~ 4A8B_lampcool6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: off -> missed
- `hand`: + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: off -> found; + 4A8B_lampmid6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found; + 4A8B_lampmid6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: off -> found; + 4A8B_lampwarm6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found; - 4A8B_campus_light_room_01 #1 blue at [64, 123, 125, 181]: found -> off; - 4A8B_both_abpgray_clutter_01 #1 blue at [34, 132, 110, 203]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampcool6_ottoman_clutter_01 #2 blue at [288, 116, 333, 163]: found -> off; - 4A8B_lampcool6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: found -> off; - 4A8B_lampmid3_bathtile_core_01 #3 blue at [374, 140, 457, 226]: found -> off; - 4A8B_lampmid3_bathtile_core_01 #4 blue at [475, 110, 513, 147]: found -> off; - 4A8B_lampmid6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: found -> off; - 4A8B_lampwarm6_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: found -> off; - 4A8B_lampwarm6_ottoman_core_01 #1 blue at [79, 133, 155, 209]: found -> off

### `rows+low`

- `fixed`: + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found; + 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found; - 4A8B_campus_light_room_01 #1 blue at [64, 123, 125, 181]: found -> off; - 4A8B_both_abpgray_clutter_01 #1 blue at [34, 132, 110, 203]: found -> off; - 4A8B_both_abpgray_clutter_01 #4 orange at [506, 124, 579, 190]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_both_abpgray_occl_02 #1 blue at [366, 123, 422, 181]: found -> off; - 4A8B_lampcool6_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: found -> off; - 4A8B_lampcool6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off; - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off; - 4A8B_lampmid6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> missed; - 4A8B_overheaddim_palewood_core_01 #1 orange at [125, 137, 207, 223]: found -> off
- `s20`: + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found; + 4A8B_lampcool6_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_lampmid3_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_window_abpwhite_occlx_08 #1 orange at [111, 114, 160, 164]: off -> found; + 4A8B_window_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; - 4A8B_both_abpgray_clutter_01 #1 blue at [34, 132, 110, 203]: found -> off; - 4A8B_both_abpgray_clutter_01 #4 orange at [506, 124, 579, 190]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_both_abpgray_occl_02 #1 blue at [366, 123, 422, 181]: found -> off; - 4A8B_lampcool6_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: found -> off; - 4A8B_lampcool6_glass_edge_01 #1 blue at [0, 145, 40, 237]: found -> off; - 4A8B_lampcool6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off; - 4A8B_overheaddim_palewood_close_01 #1 orange at [291, 243, 566, 480]: found -> missed; - 4A8B_overheaddim_palewood_core_01 #1 orange at [125, 137, 207, 223]: found -> off; ~ 4A8B_lampmid6_ottoman_occl_02 #1 orange at [225, 125, 286, 192]: off -> missed
- `s40`: + 4A8B_window_light_far_02 #2 orange at [244, 105, 273, 135]: off -> found; + 4A8B_window_light_far_02 #4 blue at [433, 106, 468, 139]: off -> found; + 4A8B_campus_light_cluster_02 #4 blue at [379, 117, 419, 163]: off -> found; + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found; + 4A8B_lampcool6_glass_core_01 #2 blue at [176, 123, 233, 185]: off -> found; + 4A8B_lampmid3_glass_core_01 #4 blue at [371, 111, 412, 151]: off -> found; + 4A8B_lampmid6_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_lampmid6_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found; + 4A8B_overheaddim_palewood_core_01 #2 blue at [246, 111, 282, 148]: missed -> found; + 4A8B_window_abpwhite_occlx_09 #1 blue at [106, 114, 152, 164]: off -> found; + 4A8B_window_abpwhite_occlx_17 #1 blue at [0, 124, 19, 183]: missed -> found; - 4A8B_both_abpgray_clutter_01 #1 blue at [34, 132, 110, 203]: found -> off; - 4A8B_both_abpgray_clutter_01 #4 orange at [506, 124, 579, 190]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_both_abpgray_occl_02 #1 blue at [366, 123, 422, 181]: found -> off; - 4A8B_lampcool6_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: found -> off; - 4A8B_lampcool6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> missed; - 4A8B_lampcool6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off; - 4A8B_lampmid6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off; - 4A8B_lampwarm6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off; - 4A8B_overheaddim_palewood_core_01 #1 orange at [125, 137, 207, 223]: found -> off; ~ 4A8B_lampmid6_ottoman_occl_02 #1 orange at [225, 125, 286, 192]: off -> missed
- `hue3`: + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: off -> found; + 4A8B_lampcool6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: off -> found; + 4A8B_lampmid6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found; + 4A8B_lampwarm6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found; + 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found; - 4A8B_campus_light_room_01 #1 blue at [64, 123, 125, 181]: found -> off; - 4A8B_both_abpgray_clutter_01 #1 blue at [34, 132, 110, 203]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampcool6_bathtile_edge_01 #1 blue at [0, 127, 31, 196]: found -> off; - 4A8B_lampmid6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: found -> off; - 4A8B_lampmid6_ottoman_edge_01 #1 blue at [0, 141, 43, 229]: found -> off; - 4A8B_lampmid6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off; ~ 4A8B_window_light_cluster_01 #3 orange at [361, 117, 400, 163]: missed -> off; ~ 4A8B_lampmid6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: off -> missed
- `dil1`: + 4A8B_campus_light_cluster_02 #4 blue at [379, 117, 419, 163]: off -> found; + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found; + 4A8B_window_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; - 4A8B_campus_light_room_01 #1 blue at [64, 123, 125, 181]: found -> off; - 4A8B_both_abpgray_clutter_01 #1 blue at [34, 132, 110, 203]: found -> off; - 4A8B_both_abpgray_clutter_01 #4 orange at [506, 124, 579, 190]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_both_abpgray_occl_02 #1 blue at [366, 123, 422, 181]: found -> off; - 4A8B_lampcool6_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: found -> off; - 4A8B_lampmid6_ottoman_clutter_01 #3 orange at [313, 141, 401, 236]: found -> missed; - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off; - 4A8B_overheaddim_palewood_close_01 #1 orange at [291, 243, 566, 480]: found -> missed; ~ 4A8B_lampcool6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: off -> missed
- `hand`: + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: off -> found; + 4A8B_lampmid6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found; + 4A8B_lampmid6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: off -> found; + 4A8B_lampwarm6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found; - 4A8B_campus_light_room_01 #1 blue at [64, 123, 125, 181]: found -> off; - 4A8B_both_abpgray_clutter_01 #1 blue at [34, 132, 110, 203]: found -> off; - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off; - 4A8B_lampcool6_ottoman_clutter_01 #2 blue at [288, 116, 333, 163]: found -> off; - 4A8B_lampcool6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: found -> off; - 4A8B_lampmid3_bathtile_core_01 #3 blue at [374, 140, 457, 226]: found -> off; - 4A8B_lampmid3_bathtile_core_01 #4 blue at [475, 110, 513, 147]: found -> off; - 4A8B_lampmid6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: found -> off; - 4A8B_lampwarm6_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: found -> off; - 4A8B_lampwarm6_ottoman_core_01 #1 blue at [79, 133, 155, 209]: found -> off

### `low_uncut`

- `fixed`: + 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found; - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off
- `s20`: + 4A8B_lampcool6_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_lampmid3_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_window_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found
- `s40`: + 4A8B_window_light_far_02 #2 orange at [244, 105, 273, 135]: off -> found; + 4A8B_window_light_far_02 #4 blue at [433, 106, 468, 139]: off -> found; + 4A8B_lampcool6_glass_core_01 #2 blue at [176, 123, 233, 185]: off -> found; + 4A8B_lampmid3_glass_core_01 #4 blue at [371, 111, 412, 151]: off -> found; + 4A8B_lampmid6_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; + 4A8B_lampmid6_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found; + 4A8B_window_abpwhite_occlx_09 #1 blue at [106, 114, 152, 164]: off -> found; - 4A8B_lampwarm6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off
- `hue3`: + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: off -> found; + 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found
- `dil1`: + 4A8B_window_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found; - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off
- `hand`: + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: off -> found; - 4A8B_lampwarm6_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: found -> off

Files: `summary.json` (every number), `judge/<step>_<candidate>/judge.md` (the full judgement of each comparison), `sheets/changed_<candidate>.png` (every barrel whose state changed: white = the true box, red = today's box, green = the candidate's).
