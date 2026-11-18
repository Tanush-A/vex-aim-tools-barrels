# Histogram against thresholds: is there a relation? (TODO F)

> **DRY RUN. 2 ordinary condition(s); under 8 no conclusion about a relation can be drawn.** Every table below shows that the pipeline runs and gives a first look. None of it is a finding.

Run 2026-11-18, git aa0fd0a. Plan and criteria: `experiments/2026-11-18_hs_relation/PREREG.md`. Train frames only (the 47 test frames are refused before any image is opened). Nothing is adopted.

- **Ordinary conditions (2):** CAMPUS `campus_light` (21 frames), HOME `window_light` (16 frames)
- **Extreme conditions (7; parked, not targets):** wood cool3 (10), wood cool6 (10), wood mid3 (10), wood mid6 (10), wood warm3 (10), wood warm6 (10), BLACK (10)
- **Excluded (lamp brightness 1):** lampcool1_wood (10), lampmid1_wood (10), lampwarm1_wood (10)
- **Hand labels (`_hs.json`):** none yet; every number below uses the **box-derived** target

Targets: **box** = thresholds read from the hand-drawn boxes per frame (the ceiling-check recipe), median per condition; **hand** = Tanush's slider labels, median per condition. Hue in OpenCV units (a negative hue is below the red wrap: -3 = 177).

## 1. The targets: six thresholds per condition

| condition | class | target | orange h lo | orange h hi | orange s lo | blue h lo | blue h hi | blue s lo | frames with a reading (orange / blue) |
|---|---|---|---|---|---|---|---|---|---|
| adopted model | | fixed | 3 | 13 | 140 | 103 | 119 | 113 | |
| CAMPUS | ordinary | box | 3 | 12 | 136 | 103 | 112 | 169 | 16 / 15 of 21 |
| HOME | ordinary | box | 0 | 13 | 101 | 104 | 116 | 162 | 14 / 12 of 16 |
| wood cool3 | extreme | box | 8 | 18 | 71 | 97 | 112 | 36 | 8 / 8 of 10 |
| wood cool6 | extreme | box | 6 | 20 | 95 | 96 | 110 | 58 | 8 / 8 of 10 |
| wood mid3 | extreme | box | 4 | 18 | 31 | 97 | 112 | 24 | 8 / 8 of 10 |
| wood mid6 | extreme | box | 6 | 20 | 46 | 96 | 114 | 36 | 8 / 8 of 10 |
| wood warm3 | extreme | box | 7 | 18 | 30 | 87 | 110 | 23 | 8 / 6 of 10 |
| wood warm6 | extreme | box | 5 | 20 | 32 | 76 | 100 | 29 | 8 / 5 of 10 |
| BLACK | extreme | box | 11 | 29 | 44 | 94 | 108 | 84 | 9 / 7 of 10 |

Is there anything to predict at condition level? Spread of the box-derived thresholds between conditions (max − min of the condition medians) against the spread inside a condition (median over conditions of the per-frame interquartile range):

| | orange h lo | orange h hi | orange s lo | blue h lo | blue h hi | blue s lo |
|---|---|---|---|---|---|---|
| between, ordinary (n = 2) | 3 | 1 | 35 | 1 | 4 | 6 |
| between, ordinary + extreme (n = 9) | 11 | 17 | 106 | 28 | 16 | 146 |
| inside a condition | 4 | 2 | 24 | 4 | 5 | 27 |

## 2. The features: from the frame alone, mean per condition

| condition | class | v_mean | s_median | s_share100 | blue_peak_h | blue_s_p90 | orange_peak_h | orange_s_p90 | ref_hue_shift | ref_s_scale |
|---|---|---|---|---|---|---|---|---|---|---|
| CAMPUS | ordinary | 155 | 20 | 0.062 | 102.7 | 179 | 9.7 | 205 | -1.6 | 1.19 |
| HOME | ordinary | 140 | 33 | 0.066 | 102.9 | 105 | 21.2 | 173 | 0.2 | 0.99 |
| wood cool3 | extreme | 126 | 129 | 0.725 | 102.5 | 132 | 20.5 | 163 | -3.8 | 1.77 |
| wood cool6 | extreme | 173 | 143 | 0.760 | 103.4 | 158 | 20.7 | 176 | -3.5 | 1.94 |
| wood mid3 | extreme | 143 | 150 | 0.800 | 103.8 | 97 | 18.4 | 179 | -5.4 | 2.00 |
| wood mid6 | extreme | 189 | 184 | 0.919 | 102.4 | 120 | 18.5 | 205 | -5.4 | 2.53 |
| wood warm3 | extreme | 146 | 178 | 0.903 | 102.0 | 78 | 17.9 | 202 | -5.9 | 2.53 |
| wood warm6 | extreme | 194 | 201 | 0.930 | 96.6 | 94 | 17.2 | 213 | -6.7 | 2.87 |
| BLACK | extreme | 109 | 17 | 0.103 | 102.9 | 182 | 18.4 | 163 | -5.6 | 1.59 |

`ref_hue_shift` and `ref_s_scale` compare each frame with the pooled HOME histogram, so HOME reads about 0 and 1 by construction.

## 3. Is there a relation? Spearman correlation at condition level

### Target: box. ORDINARY conditions only. n = 2 conditions

n = 2: a rank correlation needs at least 3 conditions. Nothing to report.

### Target: box. ordinary + EXTREME conditions (optimistic: the wood lamps are one table). n = 9 conditions

54 pairs tested (12 primary). At p < 0.05 about **2.7 of them (0.6 of the primary) would look significant by chance alone**; hence the Holm-corrected column. Smallest p this n can produce: 5e-05; after Holm over the primary family a pair needs p < 0.0042.

Primary pairs (named in the PREREG):

| threshold | feature | n | rho | p | p, Holm over the primary |
|---|---|---|---|---|---|
| orange_h_lo | orange_peak_h | 9 | 0.05 | 0.906 | 1.000 |
| orange_h_lo | ref_hue_shift | 9 | -0.49 | 0.189 | 0.945 |
| orange_h_hi | orange_peak_h | 9 | 0.10 | 0.795 | 1.000 |
| orange_h_hi | ref_hue_shift | 9 | -0.58 | 0.103 | 0.697 |
| orange_s_lo | orange_s_p90 | 9 | -0.12 | 0.775 | 1.000 |
| orange_s_lo | ref_s_scale | 9 | -0.77 | 0.020 | 0.203 |
| blue_h_lo | blue_peak_h | 9 | 0.59 | 0.100 | 0.697 |
| blue_h_lo | ref_hue_shift | 9 | 0.91 | 0.001 | 0.016 |
| blue_h_hi | blue_peak_h | 9 | 0.27 | 0.490 | 1.000 |
| blue_h_hi | ref_hue_shift | 9 | 0.76 | 0.022 | 0.203 |
| blue_s_lo | blue_s_p90 | 9 | 0.77 | 0.021 | 0.203 |
| blue_s_lo | ref_s_scale | 9 | -0.83 | 0.008 | 0.085 |

The six strongest of the other pairs (exploratory: leads, not findings):

| threshold | feature | n | rho | p | p, Holm over all pairs |
|---|---|---|---|---|---|
| orange_s_lo | ref_hue_shift | 9 | 0.88 | 0.004 | 0.199 |
| blue_h_lo | ref_s_scale | 9 | -0.79 | 0.014 | 0.722 |
| blue_s_lo | s_share100 | 9 | -0.78 | 0.017 | 0.875 |
| blue_h_lo | s_share100 | 9 | -0.73 | 0.029 | 1.000 |
| blue_s_lo | s_median | 9 | -0.73 | 0.030 | 1.000 |
| blue_s_lo | ref_hue_shift | 9 | 0.71 | 0.038 | 1.000 |

After correction: 1 primary pair(s) and 0 of all pairs below 0.05: blue_h_lo ~ ref_hue_shift.

## 4. Does it predict? Leave one condition out

Mean |prediction − target| over the held-out conditions, in hue units (S units for the floors). `fixed` = the adopted value; `mean of others` = the mean target of the other conditions; `one feature` = a line on one feature, **the feature chosen inside the loop** from the other conditions only; `two features` = the same with at most two. `optimistic` = the feature chosen once on all conditions: the held-out condition then helped pick its own predictor, so this number reads too low. It is printed to show the size of that mistake and is never the result.

### Target: box. ORDINARY conditions only. n = 2 conditions

**n = 2 is too small for a nested fit (4 conditions needed for one feature, 5 for two): `one feature` and `two features` are the mean of the others here, not a rule.**

| threshold | n | fixed | mean of others | one feature (nested) | features chosen | two features (nested) | optimistic (not a result) |
|---|---|---|---|---|---|---|---|
| orange_h_lo | 2 | 1.5 | 3.0 | 3.0 | none (fallback) ×2 | 3.0 (2 fallback) | 3.0 (none) |
| orange_h_hi | 2 | 0.5 | 1.0 | 1.0 | none (fallback) ×2 | 1.0 (2 fallback) | 1.0 (none) |
| orange_s_lo | 2 | 21.4 | 34.9 | 34.9 | none (fallback) ×2 | 34.9 (2 fallback) | 34.9 (none) |
| blue_h_lo | 2 | 0.5 | 1.0 | 1.0 | none (fallback) ×2 | 1.0 (2 fallback) | 1.0 (none) |
| blue_h_hi | 2 | 4.8 | 4.5 | 4.5 | none (fallback) ×2 | 4.5 (2 fallback) | 4.5 (none) |
| blue_s_lo | 2 | 52.8 | 6.5 | 6.5 | none (fallback) ×2 | 6.5 (2 fallback) | 6.5 (none) |

### Target: box. ordinary + EXTREME conditions (optimistic: the wood lamps are one table). n = 9 conditions

| threshold | n | fixed | mean of others | one feature (nested) | features chosen | two features (nested) | optimistic (not a result) |
|---|---|---|---|---|---|---|---|
| orange_h_lo | 9 | 3.1 | 2.6 | 3.9 | ref_hue_shift ×6, blue_s_p90 ×1, orange_peak_h ×1, s_share100 ×1 | 3.7 | 2.5 (ref_hue_shift) |
| orange_h_hi | 9 | 5.7 | 3.5 | 4.7 | ref_hue_shift ×6, blue_peak_h ×2, s_share100 ×1 | 9.3 | 3.2 (ref_hue_shift) |
| orange_s_lo | 9 | 74.9 | 35.6 | 51.9 | ref_hue_shift ×7, orange_peak_h ×1, s_median ×1 | 60.7 | 19.7 (ref_hue_shift) |
| blue_h_lo | 9 | 8.7 | 6.7 | 5.9 | blue_peak_h ×4, ref_s_scale ×4, ref_hue_shift ×1 | 5.4 | 4.2 (blue_peak_h) |
| blue_h_hi | 9 | 8.5 | 3.4 | 3.6 | ref_hue_shift ×8, blue_peak_h ×1 | 4.3 | 3.1 (ref_hue_shift) |
| blue_s_lo | 9 | 67.2 | 52.0 | 25.4 | s_share100 ×9 | 44.0 | 25.4 (s_share100) |

## 5. Does it detect? Today's detector with each set of thresholds

Each cell: found / barrels (false boxes), score; `DQ` = a box on a clean empty frame. v2 rule, `DetConfig()` defaults. `fixed` = the adopted model as stored (also at home: not the leave-one-scene-out home number). `pred1` / `pred2` = the six thresholds predicted for the held-out condition by the nested one- / two-feature rule (with the fallback of section 4 they are the mean of the other conditions). `box median` = the box target used as one model per condition. `box per frame` = thresholds read from each frame's own labels (the ceiling check; not a method).

### Predictions from the box target. ORDINARY conditions only. n = 2 conditions

| condition | class | frames | fixed | pred1 | pred2 | box median | box per frame |
|---|---|---|---|---|---|---|---|
| CAMPUS | ordinary | 21 | 34 / 35 (0), 0.99 | 29 / 35 (0), 0.91 | 29 / 35 (0), 0.91 | 29 / 35 (0), 0.91 | 30 / 35 (1), 0.91 |
| HOME | ordinary | 16 | 25 / 29 (1), 0.91 | 24 / 29 (1), 0.89 | 24 / 29 (1), 0.89 | 24 / 29 (2), 0.88 | 25 / 29 (5), 0.86 |
| **ordinary, total** | | 37 | 59 / 64 (1) | 53 / 64 (1) | 53 / 64 (1) | 53 / 64 (2) | 55 / 64 (6) |

### Predictions from the box target. ordinary + EXTREME conditions (optimistic: the wood lamps are one table). n = 9 conditions

| condition | class | frames | fixed | pred1 | pred2 | box median | box per frame |
|---|---|---|---|---|---|---|---|
| CAMPUS | ordinary | 21 | 34 / 35 (0), 0.99 | 18 / 35 (7), 0.58 | 10 / 35 (8), 0.38 | 29 / 35 (0), 0.91 | 30 / 35 (1), 0.91 |
| HOME | ordinary | 16 | 25 / 29 (1), 0.91 | 18 / 29 (1), 0.75 | 24 / 29 (7), 0.80 | 24 / 29 (2), 0.88 | 25 / 29 (5), 0.86 |
| wood cool3 | extreme | 10 | 2 / 21 (0), 0.17 | 4 / 21 (4), 0.28 | 4 / 21 (1), 0.31 | 11 / 21 (4), 0.60 | 9 / 21 (3), 0.53 |
| wood cool6 | extreme | 10 | 2 / 21 (2), 0.16 | 15 / 21 (5), 0.73 | 14 / 21 (7), 0.67 | 11 / 21 (5), 0.58 | 15 / 21 (4), 0.75 |
| wood mid3 | extreme | 10 | 1 / 21 (0), 0.08 | 1 / 21 (7), 0.06 | 0 / 21 (7), 0.00 | 3 / 21 (4), 0.21 | 5 / 21 (6), 0.33 |
| wood mid6 | extreme | 10 | 1 / 21 (0), 0.08 | 2 / 21 (8), 0.14 | 2 / 21 (5), 0.15 | 0 / 21 (6), 0.00 | 5 / 21 (6), 0.28 |
| wood warm3 | extreme | 10 | 1 / 21 (0), 0.08 | 0 / 21 (8), 0.00 | 0 / 21 (7), 0.00 | 0 / 21 (7), 0.00 | 2 / 21 (6), 0.14 |
| wood warm6 | extreme | 10 | 0 / 21 (1), 0.00 | 0 / 21 (7), 0.00 | 0 / 21 (6), 0.00 | 1 / 21 (4), 0.07 | 0 / 21 (6), 0.00 |
| BLACK | extreme | 10 | 2 / 26 (0), 0.12 | 1 / 26 (1), 0.06 | 0 / 26 (0), 0.00 | 17 / 26 (4), 0.73 | 17 / 26 (1), 0.78 |
| **ordinary, total** | | 37 | 59 / 64 (1) | 36 / 64 (8) | 34 / 64 (15) | 53 / 64 (2) | 55 / 64 (6) |
| **extreme, total** | | 70 | 9 / 152 (3) | 23 / 152 (40) | 20 / 152 (33) | 43 / 152 (34) | 53 / 152 (32) |

Kept the adopted box (no usable range): pred2 on HOME: orange.

## 6. Against the pre-registered criteria

**Not evaluated: 2 ordinary condition(s), 8 needed (aim: 10).** Criteria A (a primary pair with Holm p < 0.05), B (nested one-feature error below both baselines, better than fixed in two thirds of the conditions) and C (more barrels found, at most 2 more false boxes, no clean-negative box, no condition losing more than 0.02) are in the PREREG and are checked on the ordinary conditions only.

## Files

`per_condition.csv` (features, targets, detection per condition), `pairs.csv` (every pair, both scopes), `predictions.csv` (every held-out prediction), `detection.csv`, `per_frame.csv`, `config.json`; figures `fig_<target>_<threshold>.png` (6, not in git). A copy of this run is under `runs/`.
