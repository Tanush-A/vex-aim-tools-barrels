# Thresholds as ranges: the range version does NOT hold; R2 FAIL — 2026-11-23, git 999b73a

One command: `python barrels/experiments/2026-11-24_adaptive_range/run.py` (plan: `PREREG.md`). Train frames only; the 60 test frames are refused before any image is opened. Nothing is adopted; the default model is unchanged (`eb863d84`).

**Data.** 18 slider-labelled frames in 6 conditions; ordinary: 5 conditions at **3 places** (abp_gray, home_ottoman, uc_palewood). Labels saved from the slider proposal: 0 (0 saved without moving a slider).

**In plain words.** A frame has a run of values for each threshold that work as well as Tanush's; the runs hold when all six move together on 10 of 18 frames (confirmed box at least half the size). Constrained thresholds: orange_h_lo, orange_h_hi, orange_s_lo, blue_h_lo, blue_h_hi, blue_s_lo. R2 lands inside the held-out ranges more often than the fixed value for: orange_s_lo. R2's detection test fails C2, C5, C6.

Verdict parts (PREREG): (a) ranges hold jointly: no; (b) R2 beats fixed on a constrained threshold: yes; (c) R2 passes C2-C6: no. C1 (5 places) is separate: not met.

## 1. How wide the ranges are (detector version, one threshold at a time, around his values)

| threshold | fixed | median width (min-max) | without clutter | with clutter | low end stopped by | high end stopped by | fixed inside the condition range | constrained |
|---|---|---|---|---|---|---|---|---|
| orange_h_lo | 3 | 42 (3-53) | 42 (8-53) | 27 (3-53) | open 11, outside paint 7 | barrel lost 14, other end 4 | 4 of 5 | **yes** |
| orange_h_hi | 13 | 45 (9-61) | 46 (9-61) | 44 (42-56) | barrel lost 11, other end 4, false box 3 | open 16, outside paint 2 | 1 of 5 | **yes** |
| orange_s_lo | 140 | 54 (8-156) | 62 (8-156) | 38 (16-117) | outside paint 18 | barrel lost 12, open 4, false box 2 | 1 of 5 | **yes** |
| blue_h_lo | 103 | 46 (6-56) | 48 (33-56) | 35 (6-52) | open 14, outside paint 4 | barrel lost 13, other end 4, false box 1 | 2 of 5 | **yes** |
| blue_h_hi | 119 | 38 (5-55) | 40 (7-55) | 10 (5-55) | barrel lost 13, other end 4, false box 1 | outside paint 9, open 8, barrel lost 1 | 2 of 5 | **yes** |
| blue_s_lo | 113 | 98 (8-255) | 105 (18-255) | 75 (8-255) | outside paint 9, open 8, false box 1 | barrel lost 11, open 4, false box 3 | 2 of 5 | **yes** |

Hue in OpenCV units, S in 0-255. 'open' = the slider's end was reached still working. Ends closed one step from his value: 18 of 216 (a lone failure next to his value is possible detector noise). Pixel-version widths are in `ranges.csv`.

**Joint check:** the box of the six ranges works at all its corners on 0 of 18 frames; median share of random points inside it that work 0.79; the confirmed box (shrunk toward his values until it holds) is full size on 0, at least half size on 10, his values alone on 1 frames.

## 2. Does anything land inside the held-out ranges? (leave one PLACE out)

Mean over places of the share of a place's conditions whose range holds the prediction. Best feature = the best of the nine histogram features (line through home, or interval fit), named.

| threshold | fixed | mean of other places | best feature | its rate | features beating both fixed and the mean |
|---|---|---|---|---|---|
| orange_h_lo | 0.67 | 0.89 | ref_hue_shift (line) | 0.67 | none |
| orange_h_hi | 0.33 | 0.67 | blue_peak_h (line) | 0.67 | none |
| orange_s_lo | 0.11 | 0.78 | blue_s_p90 (line) | 0.67 | none |
| blue_h_lo | 0.44 | 0.67 | v_mean (interval) | 1.00 | v_mean (interval) |
| blue_h_hi | 0.44 | 0.11 | s_share100 (interval) | 0.78 | s_share100 (interval), ref_s_scale (line), ref_s_scale (interval) |
| blue_s_lo | 0.67 | 0.33 | orange_s_p90 (interval) | 0.78 | orange_s_p90 (interval) |

Confirmed-box version and per-place hits: `prediction.csv`.

## 3. The rule R2 and its test

R2 (PREREG part 3): a threshold stays fixed when the fixed value is inside every training condition's range; otherwise it moves with its primary feature along a line through home, slope chosen to land inside the most training ranges, kept only if that beats fixed. Fit on all places now: `orange_h_lo` <- `orange_peak_h` b = +0.214; `orange_h_hi` <- `orange_peak_h` b = -7.880; `orange_s_lo` <- `orange_s_p90` b = -1.645; `blue_h_lo` <- `blue_peak_h` b = -1.498; `blue_h_hi` <- `blue_peak_h` b = -0.550.

Per threshold on the range target, leave one place out (share of held-out places' conditions inside their range): orange_h_lo fixed 0.67 / R2 0.67 / 2026-11-24 rule 0.67; orange_h_hi fixed 0.33 / R2 0.00 / 2026-11-24 rule 0.67; orange_s_lo fixed 0.11 / R2 0.33 / 2026-11-24 rule 0.11; blue_h_lo fixed 0.44 / R2 0.33 / 2026-11-24 rule 0.44; blue_h_hi fixed 0.44 / R2 0.11 / 2026-11-24 rule 0.44; blue_s_lo fixed 0.67 / R2 0.33 / 2026-11-24 rule 0.33.

Leave one place out, per condition: found / barrels (false boxes; boxes on empty frames).

| condition | place | light | fixed | R2 |
|---|---|---|---|---|
| both_abpgray | abp_gray | mixed | 10 / 16 (2; 0) | 3 / 16 (1; 0) |
| CAMPUS | campus_study | overhead | 35 / 35 (0; 0) | 30 / 35 (1; 0) |
| lampcool6_ottoman | home_ottoman | lamp | 3 / 15 (0; 0) | 6 / 15 (0; 0) |
| lampmid6_ottoman | home_ottoman | lamp | 6 / 15 (0; 0) | 5 / 15 (1; 0) |
| lampwarm6_ottoman | home_ottoman | lamp | 0 / 15 (1; 0) | 0 / 15 (1; 0) |
| overheaddim_palewood | uc_palewood | overhead | 13 / 15 (1; 0) | 13 / 15 (1; 0) |
| window_abpwhite | abp_white | window | 26 / 32 (1; 0) | 28 / 32 (2; 0) |
| HOME | home_white | window | 28 / 29 (1; 0) | 27 / 29 (1; 0) |
| **total** | | | 121 / 172 (6; 0) | 112 / 172 (8; 0) |

**Acceptance (the 2026-11-24 clauses, R2 in place of that rule):**

- C1: **FAIL** — 3 places with slider labels (abp_gray, home_ottoman, uc_palewood); 5 needed
- C2: **FAIL** — found 112 vs 121 fixed (-9; +3 needed), more in 2 places (2 needed)
- C3: pass — false boxes 8 vs 6 fixed (at most +2)
- C4: pass — no new box on an empty frame
- C5: **FAIL** — score drops by more than 0.02 in both_abpgray, CAMPUS, lampmid6_ottoman
- C6: **FAIL** — R2 adds failing gate rows: 4A8B_campus_light|cluster, 4A8B_campus_light|edge, 4A8B_campus_light|occl, 4A8B_campus_light|room, 4A8B_window_light|core
- C7: pass — not applicable: no place new since the frozen R2

**R2 verdict: FAIL — the default stays the fixed model.**

Files: `ranges.csv`, `joint.csv`, `prediction.csv`, `detection.csv`, `rule.json`, `model_r2.json`, `gate.txt`, `config.json`.
