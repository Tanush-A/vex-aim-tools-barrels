# One setting per place, without sliders: results (2026-11-26, git 8b81375)

`python barrels/experiments/2026-11-26_place_ceiling/run.py all` (plan: `../../experiments/2026-11-26_place_ceiling/PREREG.md`). Train frames only; no test frame opened. 154 ordinary train frames, 17 conditions at 8 places: 172 placements, 307 barrels when every light is counted. Baseline everywhere: today's default (the fixed colors). Margins: found better above +4.00 placements, worse below -10.92; boxes not on their barrel worse above +1.85; found at one place worse below its own margin (1.0 at campus, home, pale wood, ABP white and glass).

## Round 1: every judged candidate

| candidate | kind | found, placements | per frame | found either way | boxes not on their barrel | on empty frames: clean / with clutter | gained / lost (per frame) | verdict |
|---|---|---|---|---|---|---|---|---|
| `hand` | in-sample | 133.8 → 156.8 (+23.0) | 211 → 281 | 158.8 | 1.9 → 1.5 (5 → 3) | 0 / 0.5 | 71 / 1 | **PASS** |
| `relabel` | in-sample | 133.8 → 158.3 (+24.5) | 211 → 287 | 160.2 | 1.9 → 1.2 (5 → 2) | 0 / 0.0 | 77 / 1 | **PASS** |
| `relabel_blue` | in-sample | 133.8 → 158.6 (+24.8) | 211 → 288 | 160.5 | 1.9 → 1.2 (5 → 2) | 0 / 0.0 | 78 / 1 | **PASS** |
| `cal_core_mid` | held out | 133.8 → 141.8 (+8.0) | 211 → 269 | 147.0 | 1.9 → 1.2 (5 → 2) | 0 / 0.0 | 78 / 20 | **FAIL** |
| `cal_core_net` | held out | 133.8 → 140.9 (+7.1) | 211 → 266 | 144.5 | 1.9 → 2.2 (5 → 3) | 0 / 0.0 | 74 / 19 | **FAIL** |
| `cal_core_tool` | held out | 133.8 → 150.8 (+17.0) | 211 → 272 | 156.0 | 1.9 → 7.3 (5 → 12) | 1 / 4.2 | 70 / 9 | **FAIL** |
| `cal_rot1_mid` | held out | 133.8 → 138.1 (+4.3) | 211 → 263 | 144.5 | 1.9 → 2.7 (5 → 5) | 1 / 0.2 | 73 / 21 | **FAIL** |
| `cal_rot2_mid` | held out | 133.8 → 139.6 (+5.8) | 211 → 267 | 144.2 | 1.9 → 1.2 (5 → 2) | 0 / 0.0 | 78 / 22 | **FAIL** |
| `cal_rot3_mid` | held out | 133.8 → 130.9 (-2.9) | 211 → 256 | 136.1 | 1.9 → 0.2 (5 → 1) | 0 / 0.0 | 74 / 29 | **FAIL** |
| `cal_rot4_mid` | held out | 133.8 → 141.1 (+7.3) | 211 → 269 | 146.2 | 1.9 → 2.5 (5 → 4) | 0 / 0.0 | 78 / 20 | **FAIL** |
| `cal_otherlight_mid` | held out | 133.8 → 148.9 (+15.1) | 211 → 263 | 151.5 | 1.9 → 1.2 (5 → 2) | 0 / 0.0 | 54 / 2 | **PASS** |
| `cal_otherplace_mid` | control | 133.8 → 81.0 (-52.9) | 211 → 142 | 86.2 | 1.9 → 6.8 (5 → 22) | 0 / 3.0 | 1 / 70 | **FAIL** |
| `cal_all_net` | in-sample | 133.8 → 141.0 (+7.2) | 211 → 261 | 146.8 | 1.9 → 0.5 (5 → 2) | 0 / 0.0 | 67 / 17 | **FAIL** |
| `oracle` | in-sample | 133.8 → 163.2 (+29.4) | 211 → 294 | 163.8 | 1.9 → 0.0 (5 → 0) | 0 / 0.0 | 83 / 0 | **PASS** |

What each candidate is:

- `hand`: Tanush's hand thresholds: per condition the median of its slider labels.
- `relabel`: the hand thresholds, the four bathroom conditions replaced by the median of the proposals (full hue range).
- `relabel_blue`: the hand thresholds; in the bathroom his orange numbers with the proposals' blue numbers.
- `cal_core_mid`: ONE frame sets the condition (mid): the calibration frame (core_01), applied to the other frames; the calibration frame itself is scored with the backup frame's setting.
- `cal_core_net`: ONE frame sets the condition (net): the calibration frame (core_01), applied to the other frames; the calibration frame itself is scored with the backup frame's setting.
- `cal_core_tool`: ONE frame sets the condition (tool): the calibration frame (core_01), applied to the other frames; the calibration frame itself is scored with the backup frame's setting.
- `cal_rot1_mid`: each frame in turn, rotation 1 (mid): every frame is scored with the setting of another frame of its condition.
- `cal_rot2_mid`: each frame in turn, rotation 2 (mid): every frame is scored with the setting of another frame of its condition.
- `cal_rot3_mid`: each frame in turn, rotation 3 (mid): every frame is scored with the setting of another frame of its condition.
- `cal_rot4_mid`: each frame in turn, rotation 4 (mid): every frame is scored with the setting of another frame of its condition.
- `cal_otherlight_mid`: the setting of ANOTHER light of the same place (the next light by name; places with one light keep the fixed model).
- `cal_otherplace_mid`: CONTROL: the setting of the calibration frame of ANOTHER place (the next place by name, its first condition).
- `cal_all_net`: every frame of the condition at once: the net setting of its pooled barrel pixels (no sliders, no detector).
- `oracle`: the best rectangle pair per condition found by search on its own frames.

Why each FAIL fails (the judge's clause):

- `cal_core_mid`: worse than the baseline by more than the noise in: found at campus_study.
- `cal_core_net`: worse than the baseline by more than the noise in: found at campus_study, abp_white, home_white.
- `cal_core_tool`: worse than the baseline by more than the noise in: found at campus_study, home_white; boxes that are not on their barrel; boxes on empty frames.
- `cal_rot1_mid`: worse than the baseline by more than the noise in: found at campus_study, abp_white, home_white; boxes on empty frames.
- `cal_rot2_mid`: worse than the baseline by more than the noise in: found at campus_study, abp_white, home_white.
- `cal_rot3_mid`: worse than the baseline by more than the noise in: found at campus_study, home_white.
- `cal_rot4_mid`: worse than the baseline by more than the noise in: found at campus_study, abp_white, home_white.
- `cal_otherplace_mid`: worse than the baseline by more than the noise in: found over all places; found at abp_gray, campus_study, home_glass, home_ottoman, uc_palewood, abp_white, home_white; boxes that are not on their barrel; boxes on empty frames.
- `cal_all_net`: worse than the baseline by more than the noise in: found at campus_study, abp_white, home_white.

Each frame in turn, the 4 rotations together: found 137.4 placements on average (lowest 130.9, highest 141.1); per frame 263.8 (256 to 269); boxes not on their barrel 1.6 (0.2 to 2.7); verdicts: FAIL, FAIL, FAIL, FAIL. (In a condition with four frames that can calibrate, rotation 4 gives a frame that can calibrate the same partner as rotation 1.)

## D. By place: found placements (found per frame) / boxes not on their barrel, once per arrangement

| place | placements (barrels, lights) | fixed | one frame, core_01 (held out) | one frame, each in turn (held out, mean) | round 2: one frame, keep rule (core_01) | hand thresholds | relabelled hand | oracle | vendor |
|---|---|---|---|---|---|---|---|---|---|
| abp_gray | 16 (16, 1) | 10.0 (10) / 0.0 | 15.0 (15) / 0.0 | 11.8 (11.8) / 0.2 | 15.0 (15) / 0.0 | 15.0 (15) / 0.0 | 15.0 (15) / 0.0 | 16.0 (16) / 0.0 | 16.0 (16) / 0.0 |
| campus_study | 35 (35, 1) | 35.0 (35) / 0.0 | 21.0 (21) / 0.0 | 23.0 (23.0) / 0.2 | 35.0 (35) / 0.0 | 35.0 (35) / 0.0 | 35.0 (35) / 0.0 | 35.0 (35) / 0.0 | 35.0* (35*) |
| home_bathtile | 15 (60, 4) | 4.0 (16) / 0.0 | 14.0 (56) / 0.0 | 13.9 (55.5) / 0.2 | 13.5 (54) / 0.0 | 12.5 (50) / 0.5 | 14.0 (56) / 0.2 | 14.5 (58) / 0.0 | 7.0 (28) / 0.0 |
| home_glass | 15 (75, 5) | 14.8 (74) / 0.6 | 14.8 (74) / 0.2 | 14.8 (74.0) / 0.2 | 14.8 (74) / 0.6 | 15.0 (75) / 0.0 | 15.0 (75) / 0.0 | 15.0 (75) / 0.0 | 12.0 (60) / 2.0 |
| home_ottoman | 15 (45, 3) | 3.0 (9) / 0.3 | 13.0 (39) / 0.0 | 12.7 (38.2) / 0.0 | 12.3 (37) / 0.0 | 13.3 (40) / 0.0 | 13.3 (40) / 0.0 | 13.7 (41) / 0.0 | 12.3 (37) / 0.0 |
| uc_palewood | 15 (15, 1) | 13.0 (13) / 1.0 | 12.0 (12) / 1.0 | 12.8 (12.8) / 0.8 | 12.0 (12) / 2.0 | 12.0 (12) / 1.0 | 12.0 (12) / 1.0 | 14.0 (14) / 0.0 | 12.0 (12) / 0.0 |
| abp_white | 32 (32, 1) | 26.0 (26) / 0.0 | 25.0 (25) / 0.0 | 24.0 (24.0) / 0.0 | 26.0 (26) / 0.0 | 26.0 (26) / 0.0 | 26.0 (26) / 0.0 | 27.0 (27) / 0.0 | 24.0 (24) / 1.0 |
| home_white | 29 (29, 1) | 28.0 (28) / 0.0 | 27.0 (27) / 0.0 | 24.5 (24.5) / 0.0 | 28.0 (28) / 0.0 | 28.0 (28) / 0.0 | 28.0 (28) / 0.0 | 28.0 (28) / 0.0 | 29.0* (29*) |
| **the six places with vendor files** | 108 (243, 15) | **70.8 (148) / 1.9** | **93.8 (221) / 1.2** | **89.9 (216.2) / 1.4** | **93.6 (218) / 2.6** | **93.8 (218) / 1.5** | **95.3 (224) / 1.2** | **100.2 (231) / 0.0** | **83.3 (177) / 3.0** |
| **all eight places** | 172 (307, 17) | **133.8 (211) / 1.9** | **141.8 (269) / 1.2** | **137.4 (263.8) / 1.6** | **156.6 (281) / 2.6** | **156.8 (281) / 1.5** | **158.3 (287) / 1.2** | **163.2 (294) / 0.0** | **147.3* (241*)** |

\* = the vendor is ASSUMED to find every barrel on the two white tables without vendor files (home, campus; Tanush 2026-11-26); a starred total holds assumed frames. The vendor's row for the six measured places is measured.

### The gap to the vendor on the six measured places

Fixed colors 70.8, the vendor 83.3 of 108 placements: a gap of 12.5.

| arm | found, placements | gap to the vendor closed | found either way | boxes not on their barrel |
|---|---|---|---|---|
| fixed | 70.8 | 0 % | 72.0 | 1.9 |
| one frame, core_01 (held out) | 93.8 | 184 % | 96.0 | 1.2 |
| one frame, each in turn (held out, mean) | 89.9 | 153 % | 92.3 | 1.4 |
| round 2: one frame, keep rule (core_01) | 93.6 | 182 % | 96.0 | 2.6 |
| hand thresholds | 93.8 | 184 % | 95.8 | 1.5 |
| relabelled hand | 95.3 | 196 % | 97.2 | 1.2 |
| oracle | 100.2 | 234 % | 100.8 | 0.0 |
| vendor | 83.3 | 100 % | 91.5 | 3.0 |

## A. The bathroom, by lamp: found per frame

| condition | barrels | fixed | hand | relabelled | relabelled, blue only | one frame, core_01 | oracle | vendor |
|---|---|---|---|---|---|---|---|---|
| lampcool6_bathtile | 15 | 13 | 15 | 15 | 15 | 15 | 15 | 11 |
| lampmid3_bathtile | 15 | 1 | 14 | 12 | 13 | 14 | 14 | 9 |
| lampmid6_bathtile | 15 | 1 | 15 | 15 | 15 | 14 | 15 | 8 |
| lampwarm6_bathtile | 15 | 1 | 6 | 14 | 14 | 13 | 14 | 0 |

The numbers used (orange hue low / high / S floor, blue hue low / high / S floor):

| condition | hand (median of his labels) | relabelled (median of the proposals) | one frame, core_01 | oracle |
|---|---|---|---|---|
| lampcool6_bathtile | o 7/15/155  b 88/115/57 | o 9/14/198  b 89/106/120 | o 6/14/195  b 71/110/121 | o 9/14/198  b 89/106/120 |
| lampmid3_bathtile | o 7/16/185  b 60/126/9 | o 9/13/205  b 66/112/14 | o 7/14/195  b 62/140/9 | o 7/16/185  b 60/126/9 |
| lampmid6_bathtile | o 8/13/191  b 60/110/10 | o 8/13/213  b 66/112/10 | o 7/13/206  b 64/125/9 | o 8/13/213  b 66/112/10 |
| lampwarm6_bathtile | o 4/10/185  b 60/131/7 | o 7/10/215  b 26/103/8 | o 5/10/198  b 29/174/8 | o 5/10/198  b 29/174/8 |

## Every condition: found per frame

| place / condition | barrels | fixed | one frame, core_01 | each in turn (mean of 4) | another light | another place | all frames pooled | hand | relabelled | oracle | vendor |
|---|---|---|---|---|---|---|---|---|---|---|---|
| abp_gray / both_abpgray | 16 | 10 | 15 | 11.8 | 10 | 2 | 11 | 15 | 15 | 16 | 16 |
| campus_study / campus_light | 35 | 35 | 21 | 23.0 | 35 | 30 | 30 | 35 | 35 | 35 | 35* |
| home_bathtile / lampcool6_bathtile | 15 | 13 | 15 | 14.8 | 15 | 9 | 15 | 15 | 15 | 15 | 11 |
| home_glass / lampcool6_glass | 15 | 15 | 15 | 15.0 | 15 | 13 | 15 | 15 | 15 | 15 | 12 |
| home_ottoman / lampcool6_ottoman | 15 | 3 | 15 | 14.8 | 12 | 0 | 12 | 15 | 15 | 15 | 13 |
| home_bathtile / lampmid3_bathtile | 15 | 1 | 14 | 13.5 | 13 | 0 | 10 | 14 | 12 | 14 | 9 |
| home_glass / lampmid3_glass | 15 | 15 | 15 | 15.0 | 15 | 12 | 14 | 15 | 15 | 15 | 12 |
| home_bathtile / lampmid6_bathtile | 15 | 1 | 14 | 14.0 | 14 | 1 | 14 | 15 | 15 | 15 | 8 |
| home_glass / lampmid6_glass | 15 | 15 | 15 | 15.0 | 15 | 15 | 15 | 15 | 15 | 15 | 12 |
| home_ottoman / lampmid6_ottoman | 15 | 6 | 14 | 13.5 | 13 | 0 | 14 | 13 | 13 | 14 | 13 |
| home_bathtile / lampwarm6_bathtile | 15 | 1 | 13 | 13.2 | 1 | 1 | 12 | 6 | 14 | 14 | 0 |
| home_glass / lampwarm6_glass | 15 | 15 | 14 | 14.2 | 14 | 12 | 14 | 15 | 15 | 15 | 12 |
| home_ottoman / lampwarm6_ottoman | 15 | 0 | 10 | 10.0 | 9 | 0 | 9 | 12 | 12 | 12 | 11 |
| uc_palewood / overheaddim_palewood | 15 | 13 | 12 | 12.8 | 13 | 8 | 12 | 12 | 12 | 14 | 12 |
| abp_white / window_abpwhite | 32 | 26 | 25 | 24.0 | 26 | 1 | 23 | 26 | 26 | 27 | 24 |
| home_glass / window_glass | 15 | 14 | 15 | 14.8 | 15 | 14 | 15 | 15 | 15 | 15 | 12 |
| home_white / window_light | 29 | 28 | 27 | 24.5 | 28 | 24 | 26 | 28 | 28 | 28 | 29* |

The setting each condition got (orange hue low / high / S floor, blue hue low / high / S floor):

| condition | calibration frame | its setting (mid) | its net setting | the tool's proposal | hand | oracle (seed, moves) |
|---|---|---|---|---|---|---|
| both_abpgray | core_01 | o -12/14/200  b 104/121/225 | o -12/14/183  b 104/121/222 | o -29/8/201  b 104/120/217 | o -2/6/167  b 102/121/113 | o -12/14/200  b 104/121/225 (mid of core_01, 0) |
| campus_light | core_01 | o 1/17/117  b 67/106/92 | o 1/17/124  b 100/107/90 | o -7/18/112  b 100/108/90 | - | o 3/13/140  b 103/119/113 (fixed, 0) |
| lampcool6_bathtile | core_01 | o 6/14/195  b 71/110/121 | o 6/15/198  b 89/110/121 | o -28/11/0  b 68/145/9 | o 7/15/155  b 88/115/57 | o 9/14/198  b 89/106/120 (relabelled, 0) |
| lampcool6_glass | core_01 | o 2/11/171  b 103/112/157 | o 2/11/171  b 103/112/198 | o -30/14/116  b 103/148/157 | o 3/12/140  b 103/113/182 | o 3/13/140  b 103/119/113 (fixed, 0) |
| lampcool6_ottoman | core_01 | o -16/25/136  b 92/120/22 | o -16/25/95  b 97/120/22 | o -16/18/128  b 94/150/13 | o 4/23/105  b 97/112/98 | o 4/23/105  b 97/112/98 (hand thresholds, 0) |
| lampmid3_bathtile | core_01 | o 7/14/195  b 62/140/9 | o 7/14/202  b 46/140/9 | o 6/12/190  b 60/140/9 | o 7/16/185  b 60/126/9 | o 7/16/185  b 60/126/9 (hand thresholds, 0) |
| lampmid3_glass | core_01 | o 3/10/123  b 103/113/152 | o 3/10/169  b 103/113/183 | o -30/9/133  b 105/150/152 | o 2/13/140  b 105/113/186 | o 2/13/140  b 105/113/186 (hand thresholds, 0) |
| lampmid6_bathtile | core_01 | o 7/13/206  b 64/125/9 | o 7/14/204  b 66/125/9 | o 4/10/180  b 60/146/8 | o 8/13/191  b 60/110/10 | o 8/13/213  b 66/112/10 (relabelled, 0) |
| lampmid6_glass | core_01 | o 5/11/140  b 104/111/128 | o 5/11/178  b 104/111/168 | o -30/12/141  b 102/150/134 | o 3/12/158  b 103/112/179 | o 3/12/158  b 103/112/179 (hand thresholds, 0) |
| lampmid6_ottoman | core_01 | o 4/26/186  b 71/142/20 | o 4/26/180  b 97/125/20 | o 4/27/183  b 87/150/13 | o 4/23/171  b 95/115/48 | o 4/25/194  b 92/113/51 (pooled net setting, 0) |
| lampwarm6_bathtile | core_01 | o 5/10/198  b 29/174/8 | o 5/10/213  b 26/174/8 | o 5/9/185  b 60/150/9 | o 4/10/185  b 60/131/7 | o 5/10/198  b 29/174/8 (mid of core_01, 0) |
| lampwarm6_glass | core_01 | o 5/11/159  b 101/115/129 | o 5/11/181  b 101/115/146 | o 3/13/164  b 103/119/129 | o 3/12/164  b 105/114/147 | o 3/12/164  b 105/114/147 (hand thresholds, 0) |
| lampwarm6_ottoman | core_01 | o 7/25/194  b 70/137/5 | o 7/24/202  b 80/132/8 | o 5/25/176  b 66/150/6 | o 5/25/166  b 80/135/10 | o 5/25/166  b 80/135/10 (hand thresholds, 0) |
| overheaddim_palewood | core_01 | o 3/11/213  b 66/137/118 | o 2/11/210  b 103/116/127 | o 4/10/210  b 103/147/135 | o -3/14/166  b 104/132/131 | o 4/14/189  b 64/136/114 (mid of touch_01, 0) |
| window_abpwhite | occlx_01 | o 7/10/166  b 64/111/127 | o 8/9/171  b 104/111/198 | o 1/9/149  b 102/149/138 | - | o 7/10/167  b 68/113/124 (mid of occlx_07, 0) |
| window_glass | core_01 | o 1/10/137  b 104/113/197 | o 1/10/137  b 104/113/189 | o -30/15/116  b 103/117/193 | o -11/12/153  b 104/113/207 | o -11/12/153  b 104/113/207 (hand thresholds, 0) |
| window_light | core_01 | o 5/11/190  b 105/111/173 | o 5/11/190  b 105/111/211 | o -29/12/128  b 106/137/172 | - | o 3/13/140  b 103/119/113 (fixed, 0) |

## How narrow a setting is: hue units from the low end to the high end (median; smallest to largest)

| setting | how many | orange hue range | blue hue range | orange S floor | blue S floor |
|---|---|---|---|---|---|
| fixed | 1 | 10 (10 to 10) | 16 (16 to 16) | 140 (140 to 140) | 113 (113 to 113) |
| one frame, mid (all 99 frames that can calibrate) | 99 | 7 (1 to 41) | 28 (0 to 145) | 171 (106 to 214) | 137 (5 to 227) |
| one frame, net | 99 | 7 (1 to 41) | 9 (0 to 148) | 186 (94 to 215) | 183 (5 to 236) |
| one frame, the tool's proposal | 99 | 18 (1 to 60) | 42 (2 to 90) | 155 (0 to 214) | 138 (5 to 223) |
| all frames of a condition pooled, net | 17 | 6 (2 to 21) | 10 (4 to 73) | 194 (138 to 215) | 163 (7 to 221) |
| hand (median per condition) | 14 | 9 (5 to 23) | 20 (8 to 71) | 165 (105 to 191) | 106 (7 to 207) |
| oracle | 17 | 10 (3 to 26) | 17 (8 to 145) | 166 (105 to 213) | 113 (8 to 225) |

## B. Which frame calibrates: each frame in turn (found per frame on the OTHER frames of its condition)

| condition | frames that can calibrate | fixed, mean | calibrated, mean | worst calibration frame | best calibration frame |
|---|---|---|---|---|---|
| both_abpgray | 4 | 8.2 of 12.8 | 9.5 | clutter_01: 5 of 12 | core_01: 12 of 12 |
| campus_light | 16 | 32.9 of 32.9 | 22.6 | top_01: 1 of 34 | window_01: 32 of 33 |
| lampcool6_bathtile | 4 | 10.0 of 11.8 | 11.5 | edge_01: 12 of 13 | clutter_01: 11 of 11 |
| lampcool6_glass | 4 | 11.8 of 11.8 | 11.8 | clutter_01: 11 of 11 | clutter_01: 11 of 11 |
| lampcool6_ottoman | 4 | 2.2 of 11.8 | 11.5 | edge_01: 12 of 13 | clutter_01: 11 of 11 |
| lampmid3_bathtile | 4 | 1.0 of 11.8 | 10.5 | clutter_01: 9 of 11 | edge_01: 12 of 13 |
| lampmid3_glass | 4 | 11.8 of 11.8 | 11.8 | clutter_01: 11 of 11 | clutter_01: 11 of 11 |
| lampmid6_bathtile | 4 | 1.0 of 11.8 | 11.0 | clutter_01: 9 of 11 | edge_01: 13 of 13 |
| lampmid6_glass | 4 | 11.8 of 11.8 | 11.8 | clutter_01: 11 of 11 | clutter_01: 11 of 11 |
| lampmid6_ottoman | 4 | 4.5 of 11.8 | 10.2 | touch_01: 10 of 12 | clutter_01: 10 of 11 |
| lampwarm6_bathtile | 4 | 1.0 of 11.8 | 10.2 | clutter_01: 9 of 11 | touch_01: 11 of 12 |
| lampwarm6_glass | 4 | 11.8 of 11.8 | 11.2 | edge_01: 11 of 13 | clutter_01: 11 of 11 |
| lampwarm6_ottoman | 4 | 0.0 of 11.8 | 7.5 | core_01: 6 of 11 | edge_01: 10 of 13 |
| overheaddim_palewood | 4 | 10.0 of 11.8 | 9.8 | core_01: 8 of 11 | touch_01: 11 of 12 |
| window_abpwhite | 16 | 24.4 of 30.0 | 22.4 | occlx_13: 10 of 30 | occlx_10: 26 of 30 |
| window_glass | 4 | 10.8 of 11.8 | 11.5 | clutter_01: 10 of 11 | core_01: 11 of 11 |
| window_light | 11 | 25.7 of 26.6 | 23.0 | core_03: 14 of 28 | occl_01: 26 of 27 |

By the kind of shot that calibrates (all conditions together; found on the other frames of the same condition):

| calibration shot | times used | fixed | calibrated | share found | boxes not on their barrel |
|---|---|---|---|---|---|
| core | 18 | 199 of 268 | 226 of 268 | 84 % (fixed 74 %) | 2 |
| touch | 16 | 154 of 228 | 209 of 228 | 92 % (fixed 68 %) | 2 |
| occlx | 16 | 390 of 480 | 359 of 480 | 75 % (fixed 81 %) | 0 |
| clutter | 15 | 123 of 187 | 149 of 187 | 80 % (fixed 66 %) | 2 |
| edge | 15 | 141 of 217 | 174 of 217 | 80 % (fixed 65 %) | 2 |
| close | 3 | 88 of 90 | 77 of 90 | 86 % (fixed 98 %) | 2 |
| cluster | 3 | 80 of 81 | 73 of 81 | 90 % (fixed 99 %) | 0 |
| far | 2 | 55 of 56 | 53 of 56 | 95 % (fixed 98 %) | 0 |
| plain | 2 | 66 of 66 | 58 of 66 | 88 % (fixed 100 %) | 0 |
| room | 2 | 66 of 66 | 58 of 66 | 88 % (fixed 100 %) | 0 |
| occl | 2 | 52 of 54 | 50 of 54 | 93 % (fixed 96 %) | 0 |
| hand | 1 | 33 of 33 | 23 of 33 | 70 % (fixed 100 %) | 0 |
| held | 1 | 34 of 34 | 30 of 34 | 88 % (fixed 100 %) | 0 |
| top | 1 | 34 of 34 | 1 of 34 | 3 % (fixed 100 %) | 0 |
| topstripe | 1 | 34 of 34 | 1 of 34 | 3 % (fixed 100 %) | 0 |
| window | 1 | 33 of 33 | 32 of 33 | 97 % (fixed 100 %) | 0 |

## B. One light of a place applied to the other lights (found per frame; rows = the light whose core_01 set the numbers; the same light: its other frames only)

**home_bathtile**

| setting from \ applied to | lampcool6_bathtile | lampmid3_bathtile | lampmid6_bathtile | lampwarm6_bathtile |
|---|---|---|---|---|
| (fixed colors) | 13 of 15 | 1 of 15 | 1 of 15 | 1 of 15 |
| lampcool6_bathtile | **11 of 11** | 1 of 15 | 1 of 15 | 1 of 15 |
| lampmid3_bathtile | 15 of 15 | **10 of 11** | 15 of 15 | 3 of 15 |
| lampmid6_bathtile | 15 of 15 | 13 of 15 | **10 of 11** | 3 of 15 |
| lampwarm6_bathtile | 9 of 15 | 13 of 15 | 14 of 15 | **10 of 11** |

**home_glass**

| setting from \ applied to | lampcool6_glass | lampmid3_glass | lampmid6_glass | lampwarm6_glass | window_glass |
|---|---|---|---|---|---|
| (fixed colors) | 15 of 15 | 15 of 15 | 15 of 15 | 15 of 15 | 14 of 15 |
| lampcool6_glass | **11 of 11** | 15 of 15 | 15 of 15 | 15 of 15 | 15 of 15 |
| lampmid3_glass | 15 of 15 | **11 of 11** | 15 of 15 | 15 of 15 | 15 of 15 |
| lampmid6_glass | 15 of 15 | 15 of 15 | **11 of 11** | 15 of 15 | 15 of 15 |
| lampwarm6_glass | 15 of 15 | 15 of 15 | 15 of 15 | **11 of 11** | 15 of 15 |
| window_glass | 15 of 15 | 15 of 15 | 15 of 15 | 14 of 15 | **11 of 11** |

**home_ottoman**

| setting from \ applied to | lampcool6_ottoman | lampmid6_ottoman | lampwarm6_ottoman |
|---|---|---|---|
| (fixed colors) | 3 of 15 | 6 of 15 | 0 of 15 |
| lampcool6_ottoman | **11 of 11** | 14 of 15 | 9 of 15 |
| lampmid6_ottoman | 12 of 15 | **10 of 11** | 8 of 15 |
| lampwarm6_ottoman | 12 of 15 | 13 of 15 | **6 of 11** |

## B. Where the calibration frame comes from (every pair of conditions; found per frame)

| the setting comes from | found | share | fixed colors on the same frames |
|---|---|---|---|
| the same condition (its other frames) | 212 of 243 | 87.2 % | 170 of 243 (70.0 %) |
| another light of the same place | 470 of 570 | 82.5 % | 362 of 570 (63.5 %) |
| another place | 2322 of 4342 | 53.5 % | 3014 of 4342 (69.4 %) |

## Round 2: a calibration that keeps the fixed colors where they work

Designed AFTER round 1 was seen (PREREG addendum). No tuned number, but the rule was chosen with these frames in view: a hypothesis for the next places, not a held-out result.

| candidate | kind | found, placements | per frame | found either way | boxes not on their barrel | on empty frames: clean / with clutter | gained / lost (per frame) | verdict |
|---|---|---|---|---|---|---|---|---|
| `cal_core_keep` | held out, round 2 | 133.8 → 156.6 (+22.8) | 211 → 281 | 159.0 | 1.9 → 2.6 (5 → 5) | 0 / 0.0 | 71 / 1 | **PASS** |
| `cal_rot1_keep` | held out, round 2 | 133.8 → 154.4 (+20.6) | 211 → 278 | 158.0 | 1.9 → 3.1 (5 → 7) | 0 / 0.2 | 68 / 1 | **PASS** |
| `cal_rot2_keep` | held out, round 2 | 133.8 → 156.2 (+22.4) | 211 → 280 | 157.7 | 1.9 → 1.6 (5 → 4) | 0 / 0.0 | 70 / 1 | **PASS** |
| `cal_rot3_keep` | held out, round 2 | 133.8 → 154.0 (+20.2) | 211 → 277 | 155.4 | 1.9 → 1.6 (5 → 4) | 0 / 0.0 | 68 / 2 | **PASS** |
| `cal_rot4_keep` | held out, round 2 | 133.8 → 153.0 (+19.2) | 211 → 278 | 156.2 | 1.9 → 3.9 (5 → 7) | 0 / 0.0 | 70 / 3 | **FAIL** |
| `cal_core_wide` | held out, round 2 | 133.8 → 158.5 (+24.7) | 211 → 287 | 159.8 | 1.9 → 7.4 (5 → 21) | 0 / 1.3 | 78 / 2 | **FAIL** |

What each candidate is:

- `cal_core_keep`: ROUND 2. The calibration frame (core_01) first tests the fixed colors: if they find every free-standing box of it and draw no box that is not on its barrel, the fixed colors stay; otherwise its mid setting. The calibration frame itself: the same with the backup frame.
- `cal_rot1_keep`: ROUND 2. The same keep rule, each frame in turn, rotation 1.
- `cal_rot2_keep`: ROUND 2. The same keep rule, each frame in turn, rotation 2.
- `cal_rot3_keep`: ROUND 2. The same keep rule, each frame in turn, rotation 3.
- `cal_rot4_keep`: ROUND 2. The same keep rule, each frame in turn, rotation 4.
- `cal_core_wide`: ROUND 2. The calibration may only widen: per color the lower hue low, the higher hue high and the lower S floor of the fixed colors and the calibration frame's mid setting.

Why each FAIL fails (the judge's clause):

- `cal_rot4_keep`: worse than the baseline by more than the noise in: boxes that are not on their barrel.
- `cal_core_wide`: worse than the baseline by more than the noise in: found at uc_palewood; boxes that are not on their barrel; boxes on empty frames.

The keep rule, each frame in turn: found 154.4 placements on average (lowest 153.0, highest 156.2); per frame 278.2 (277 to 280); verdicts: PASS, PASS, PASS, FAIL.

With core_01 as the calibration frame, the fixed colors are kept at 9 of 17 conditions: campus_light, lampcool6_bathtile, lampcool6_glass, lampmid3_glass, lampmid6_glass, lampwarm6_glass, window_abpwhite, window_glass, window_light. Over all 99 frames that can calibrate, the fixed colors pass the test on 69.

| place | placements | fixed | round 1: one frame (core_01) | round 2: keep rule (core_01) | round 2: keep rule, each in turn (mean) | round 2: only widen (core_01) | hand |
|---|---|---|---|---|---|---|---|
| abp_gray | 16 | 10.0 (10) / 0.0 | 15.0 (15) / 0.0 | 15.0 (15) / 0.0 | 12.2 (12.2) / 0.2 | 16.0 (16) / 2.0 | 15.0 (15) / 0.0 |
| campus_study | 35 | 35.0 (35) / 0.0 | 21.0 (21) / 0.0 | 35.0 (35) / 0.0 | 35.0 (35.0) / 0.0 | 35.0 (35) / 0.0 | 35.0 (35) / 0.0 |
| home_bathtile | 15 | 4.0 (16) / 0.0 | 14.0 (56) / 0.0 | 13.5 (54) / 0.0 | 13.5 (54.0) / 0.2 | 14.0 (56) / 3.5 | 12.5 (50) / 0.5 |
| home_glass | 15 | 14.8 (74) / 0.6 | 14.8 (74) / 0.2 | 14.8 (74) / 0.6 | 14.8 (74.0) / 0.6 | 14.8 (74) / 0.6 | 15.0 (75) / 0.0 |
| home_ottoman | 15 | 3.0 (9) / 0.3 | 13.0 (39) / 0.0 | 12.3 (37) / 0.0 | 12.1 (36.2) / 0.0 | 13.7 (41) / 0.3 | 13.3 (40) / 0.0 |
| uc_palewood | 15 | 13.0 (13) / 1.0 | 12.0 (12) / 1.0 | 12.0 (12) / 2.0 | 12.8 (12.8) / 1.5 | 11.0 (11) / 1.0 | 12.0 (12) / 1.0 |
| abp_white | 32 | 26.0 (26) / 0.0 | 25.0 (25) / 0.0 | 26.0 (26) / 0.0 | 26.0 (26.0) / 0.0 | 26.0 (26) / 0.0 | 26.0 (26) / 0.0 |
| home_white | 29 | 28.0 (28) / 0.0 | 27.0 (27) / 0.0 | 28.0 (28) / 0.0 | 28.0 (28.0) / 0.0 | 28.0 (28) / 0.0 | 28.0 (28) / 0.0 |
| **the six places with vendor files** | 108 | **70.8 (148) / 1.9** | **93.8 (221) / 1.2** | **93.6 (218) / 2.6** | **91.4 (215.2) / 2.5** | **95.5 (224) / 7.4** | **93.8 (218) / 1.5** |
| **all eight places** | 172 | **133.8 (211) / 1.9** | **141.8 (269) / 1.2** | **156.6 (281) / 2.6** | **154.4 (278.2) / 2.5** | **158.5 (287) / 7.4** | **156.8 (281) / 1.5** |

Files: `settings.json` (the setting of every frame that can calibrate), `oracle.json`, `judged.json` and `judged2.json` (every tally), `cross.json`, `thresholds.json`, `judge/<candidate>/judge.md` (the judge's page: tables, every barrel gained and lost, the clauses), `sheets/` (contact sheets, not committed).
