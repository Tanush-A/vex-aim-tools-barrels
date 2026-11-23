# Ours (candidate color model) against ours (fixed) and the vendor, per condition (2026-11-25, step 4)

`python barrels/experiments/2026-11-25_color/vendor.py --model results/2026-11-25_color/config_c2_round1_not_passing.json`. Train frames with a vendor file (124); test frames never opened. Cells: strict found / barrels (v2 rule), false boxes, and in brackets the place count (a box of the right color centred on the barrel). Better = more found (strict) unless it brings as many more false boxes.

| condition | class | barrels | fixed | candidate | vendor | candidate vs vendor |
|---|---|---:|---|---|---|---|
| both_abpgray | ordinary | 16 | 10 f2 (11) | 10 f2 (11) | 16 f0 (16) | vendor (-6 found, +2 false) |
| window_abpwhite | ordinary | 32 | 26 f1 (26) | 26 f1 (26) | 24 f4 (27) | ours (+2 found, -3 false) |
| lampcool6_bathtile | ordinary | 15 | 13 f0 (13) | 14 f0 (14) | 11 f2 (13) | ours (+3 found, -2 false) |
| lampmid3_bathtile | ordinary | 15 | 1 f0 (1) | 7 f3 (8) | 9 f0 (9) | vendor (-2 found, +3 false) |
| lampmid6_bathtile | ordinary | 15 | 1 f0 (1) | 14 f0 (14) | 8 f1 (9) | ours (+6 found, -1 false) |
| lampwarm6_bathtile | ordinary | 15 | 1 f0 (1) | 1 f1 (1) | 0 f0 (0) | mixed (+1 found, +1 false) |
| lampcool6_glass | ordinary | 15 | 15 f0 (15) | 15 f0 (15) | 12 f4 (15) | ours (+3 found, -4 false) |
| lampmid3_glass | ordinary | 15 | 15 f2 (15) | 15 f2 (15) | 12 f4 (15) | ours (+3 found, -2 false) |
| lampmid6_glass | ordinary | 15 | 15 f2 (15) | 15 f2 (15) | 12 f4 (15) | ours (+3 found, -2 false) |
| lampwarm6_glass | ordinary | 15 | 15 f1 (15) | 15 f1 (15) | 12 f2 (14) | ours (+3 found, -1 false) |
| window_glass | ordinary | 15 | 14 f2 (15) | 14 f2 (15) | 12 f6 (15) | ours (+2 found, -4 false) |
| lampcool6_ottoman | ordinary | 15 | 3 f0 (3) | 3 f0 (3) | 13 f1 (14) | vendor (-10 found, -1 false) |
| lampmid6_ottoman | ordinary | 15 | 6 f0 (6) | 6 f0 (6) | 13 f1 (14) | vendor (-7 found, -1 false) |
| lampwarm6_ottoman | ordinary | 15 | 0 f1 (0) | 5 f1 (5) | 11 f0 (11) | vendor (-6 found, +1 false) |
| overheaddim_palewood | ordinary | 15 | 13 f1 (13) | 13 f1 (13) | 12 f1 (13) | ours (+1 found, +0 false) |
| lampmid3_ottoman | extreme | 15 | 1 f1 (2) | 1 f1 (2) | 10 f1 (11) | vendor (-9 found, +0 false) |
| **all ordinary** | | 243 | **148 f12 (150)** | **173 f16 (176)** | **177 f30 (200)** | |

## By place (ordinary)

| place | barrels | fixed | candidate | vendor |
|---|---:|---|---|---|
| abp_gray | 16 | 10 f2 (11) | 10 f2 (11) | 16 f0 (16) |
| abp_white | 32 | 26 f1 (26) | 26 f1 (26) | 24 f4 (27) |
| home_bathtile | 60 | 16 f0 (16) | 36 f4 (37) | 28 f3 (31) |
| home_glass | 75 | 74 f7 (75) | 74 f7 (75) | 60 f20 (74) |
| home_ottoman | 45 | 9 f1 (9) | 14 f1 (14) | 37 f2 (39) |
| uc_palewood | 15 | 13 f1 (13) | 13 f1 (13) | 12 f1 (13) |

Barrels (strict) the vendor finds and the candidate misses, per condition: lampcool6_ottoman 10, lampmid6_ottoman 7, both_abpgray 6, lampwarm6_ottoman 6, lampmid3_bathtile 2, overheaddim_palewood 2. The other way: lampmid6_bathtile 6, lampcool6_bathtile 3, lampcool6_glass 3, lampmid3_glass 3, lampmid6_glass 3, lampwarm6_glass 3, overheaddim_palewood 3, window_abpwhite 2, window_glass 2, lampwarm6_bathtile 1.

