# Part A in full: TODO F updated — 2026-11-23, git 6ace4f5

Conditions (class, place, light, frames, hand-labelled frames, ceiling found / barrels):

| condition | class | place | light | frames | hand | ceiling |
|---|---|---|---|---|---|---|
| both_abpgray | ordinary | abp_gray | mixed | 8 | 3 | 16 / 16 |
| CAMPUS | ordinary | campus_study | overhead | 21 | 0 | 33 / 35 |
| lampcool6_ottoman | ordinary | home_ottoman | lamp | 7 | 3 | 15 / 15 |
| lampmid3_ottoman | extreme (ceiling) | home_ottoman | lamp | 7 | 3 | 0 / 15 |
| lampmid6_ottoman | ordinary | home_ottoman | lamp | 7 | 3 | 13 / 15 |
| lampwarm6_ottoman | ordinary | home_ottoman | lamp | 7 | 3 | 12 / 15 |
| overheaddim_palewood | ordinary | uc_palewood | overhead | 7 | 3 | 11 / 15 |
| window_abpwhite | ordinary | abp_white | window | 17 | 0 | 24 / 32 |
| HOME | ordinary | home_white | window | 16 | 0 | 28 / 29 |
| lampcool3_wood | extreme | home_wooddesk | lamp | 10 | 0 | - / - |
| lampcool6_wood | extreme | home_wooddesk | lamp | 10 | 0 | - / - |
| lampmid3_wood | extreme | home_wooddesk | lamp | 10 | 0 | - / - |
| lampmid6_wood | extreme | home_wooddesk | lamp | 10 | 0 | - / - |
| lampwarm3_wood | extreme | home_wooddesk | lamp | 10 | 0 | - / - |
| lampwarm6_wood | extreme | home_wooddesk | lamp | 10 | 0 | - / - |
| BLACK | extreme | home_black | window | 10 | 0 | - / - |

## Targets per ordinary condition (hand, box, hand − box)

| condition | target | orange_h_lo | orange_h_hi | orange_s_lo | blue_h_lo | blue_h_hi | blue_s_lo |
|---|---|---|---|---|---|---|---|
| adopted | fixed | 3 | 13 | 140 | 103 | 119 | 113 |
| both_abpgray | box | -4 | 7 | 194 | 105 | 119 | 217 |
| | hand | -2 | 6 | 167 | 102 | 121 | 113 |
| | hand − box | 2 | -1 | -26 | -3 | 2 | -104 |
| CAMPUS | box | 3 | 12 | 136 | 103 | 112 | 169 |
| lampcool6_ottoman | box | 9 | 22 | 120 | 99 | 110 | 144 |
| | hand | 4 | 23 | 105 | 97 | 112 | 98 |
| | hand − box | -5 | 1 | -15 | -2 | 2 | -46 |
| lampmid6_ottoman | box | 8 | 23 | 134 | 99 | 112 | 94 |
| | hand | 4 | 23 | 171 | 95 | 115 | 48 |
| | hand − box | -4 | 0 | 37 | -4 | 3 | -46 |
| lampwarm6_ottoman | box | 8 | 23 | 127 | 92 | 112 | 40 |
| | hand | 5 | 25 | 166 | 80 | 135 | 10 |
| | hand − box | -3 | 2 | 39 | -12 | 23 | -30 |
| overheaddim_palewood | box | 2 | 13 | 170 | 104 | 114 | 186 |
| | hand | -3 | 14 | 166 | 104 | 132 | 131 |
| | hand − box | -5 | 1 | -4 | 0 | 18 | -56 |
| window_abpwhite | box | 2 | 13 | 135 | 104 | 112 | 214 |
| HOME | box | 0 | 13 | 101 | 104 | 116 | 162 |

## Prediction, hand target: leave one place out (lead) and leave one condition out

| threshold | conditions / places | fixed | mean of other places | nested line, LOPO | LOCO (flatters) | LOPO prediction better than fixed in (places) | place-level Spearman, primary feature |
|---|---|---|---|---|---|---|---|
| orange_h_lo | 5 / 3 | 4.1 | 5.7 | 5.7 (fallback: too few places) | 2.3 | 2 of 3 | orange_peak_h: 0.50 (p 1.00, n 3) |
| orange_h_hi | 5 / 3 | 6.2 | 11.4 | 11.4 (fallback: too few places) | 1.4 | 0 of 3 | orange_peak_h: 1.00 (p 0.33, n 3) |
| orange_s_lo | 5 / 3 | 27.9 | 17.0 | 17.0 (fallback: too few places) | 32.3 | 3 of 3 | orange_s_p90: -1.00 (p 0.33, n 3) |
| blue_h_lo | 5 / 3 | 4.8 | 10.3 | 10.3 (fallback: too few places) | 11.8 | 0 of 3 | blue_peak_h: -0.50 (p 1.00, n 3) |
| blue_h_hi | 5 / 3 | 8.0 | 8.4 | 8.4 (fallback: too few places) | 7.4 | 1 of 3 | blue_peak_h: -0.50 (p 1.00, n 3) |
| blue_s_lo | 5 / 3 | 26.3 | 58.3 | 58.3 (fallback: too few places) | 13.7 | 0 of 3 | blue_s_p90: 0.50 (p 1.00, n 3) |

Features chosen inside the loop (LOPO / LOCO), per threshold:

- orange_h_lo: LOPO fallback ×5; LOCO v_mean ×3, orange_s_p90 ×2
- orange_h_hi: LOPO fallback ×5; LOCO orange_s_p90 ×5
- orange_s_lo: LOPO fallback ×5; LOCO s_median ×2, ref_hue_shift ×2, ref_s_scale ×1
- blue_h_lo: LOPO fallback ×5; LOCO blue_s_p90 ×3, v_mean ×1, s_share100 ×1
- blue_h_hi: LOPO fallback ×5; LOCO s_median ×4, s_share100 ×1
- blue_s_lo: LOPO fallback ×5; LOCO blue_s_p90 ×5

Spearman, primary pairs, hand target (condition level, then place level; permutation p):

| threshold | feature | rho cond (n) | p | rho place (n) | p |
|---|---|---|---|---|---|
| orange_h_lo | orange_peak_h | 0.56 (5) | 0.367 | 0.50 (3) | 1.000 |
| orange_h_lo | ref_hue_shift | 0.67 (5) | 0.267 | 1.00 (3) | 0.333 |
| orange_h_hi | orange_peak_h | 0.67 (5) | 0.267 | 1.00 (3) | 0.333 |
| orange_h_hi | ref_hue_shift | 0.56 (5) | 0.367 | 0.50 (3) | 1.000 |
| orange_s_lo | orange_s_p90 | -0.62 (5) | 0.300 | -1.00 (3) | 0.333 |
| orange_s_lo | ref_s_scale | -0.87 (5) | 0.067 | -0.50 (3) | 1.000 |
| blue_h_lo | blue_peak_h | -0.30 (5) | 0.683 | -0.50 (3) | 1.000 |
| blue_h_lo | ref_hue_shift | -0.60 (5) | 0.350 | -1.00 (3) | 0.333 |
| blue_h_hi | blue_peak_h | -0.10 (5) | 0.950 | -0.50 (3) | 1.000 |
| blue_h_hi | ref_hue_shift | -0.70 (5) | 0.233 | -1.00 (3) | 0.333 |
| blue_s_lo | blue_s_p90 | 0.90 (5) | 0.083 | 0.50 (3) | 1.000 |
| blue_s_lo | ref_s_scale | 0.10 (5) | 0.950 | 0.50 (3) | 1.000 |

## Prediction, box target: leave one place out (lead) and leave one condition out

| threshold | conditions / places | fixed | mean of other places | nested line, LOPO | LOCO (flatters) | LOPO prediction better than fixed in (places) | place-level Spearman, primary feature |
|---|---|---|---|---|---|---|---|
| orange_h_lo | 8 / 6 | 2.8 | 4.0 | 6.1 | 2.1 | 1 of 6 | orange_peak_h: 0.17 (p 0.76, n 6) |
| orange_h_hi | 8 / 6 | 2.8 | 5.8 | 7.1 | 1.8 | 1 of 6 | orange_peak_h: 0.58 (p 0.28, n 6) |
| orange_s_lo | 8 / 6 | 24.1 | 28.3 | 20.4 | 18.1 | 3 of 6 | orange_s_p90: -0.49 (p 0.36, n 6) |
| blue_h_lo | 8 / 6 | 1.8 | 3.8 | 4.5 | 5.0 | 2 of 6 | blue_peak_h: 0.31 (p 0.56, n 6) |
| blue_h_hi | 8 / 6 | 4.8 | 3.0 | 2.4 | 2.0 | 4 of 6 | blue_peak_h: 0.20 (p 0.71, n 6) |
| blue_s_lo | 8 / 6 | 70.9 | 51.0 | 54.1 | 58.8 | 4 of 6 | blue_s_p90: 0.89 (p 0.03, n 6) |

Features chosen inside the loop (LOPO / LOCO), per threshold:

- orange_h_lo: LOPO orange_s_p90 ×5, ref_s_scale ×2, blue_s_p90 ×1; LOCO v_mean ×8
- orange_h_hi: LOPO v_mean ×3, orange_peak_h ×3, orange_s_p90 ×1, blue_s_p90 ×1; LOCO v_mean ×8
- orange_s_lo: LOPO orange_peak_h ×7, orange_s_p90 ×1; LOCO orange_peak_h ×6, orange_s_p90 ×2
- blue_h_lo: LOPO v_mean ×3, orange_s_p90 ×3, ref_s_scale ×1, blue_s_p90 ×1; LOCO v_mean ×6, s_share100 ×1, blue_s_p90 ×1
- blue_h_hi: LOPO orange_s_p90 ×7, orange_peak_h ×1; LOCO orange_s_p90 ×7, orange_peak_h ×1
- blue_s_lo: LOPO v_mean ×4, blue_peak_h ×3, blue_s_p90 ×1; LOCO v_mean ×5, orange_s_p90 ×2, blue_s_p90 ×1

Spearman, primary pairs, box target (condition level, then place level; permutation p):

| threshold | feature | rho cond (n) | p | rho place (n) | p |
|---|---|---|---|---|---|
| orange_h_lo | orange_peak_h | 0.30 (8) | 0.469 | 0.17 (6) | 0.756 |
| orange_h_lo | ref_hue_shift | 0.35 (8) | 0.389 | 0.06 (6) | 0.939 |
| orange_h_hi | orange_peak_h | 0.45 (8) | 0.265 | 0.58 (6) | 0.283 |
| orange_h_hi | ref_hue_shift | 0.11 (8) | 0.799 | 0.03 (6) | 1.000 |
| orange_s_lo | orange_s_p90 | -0.40 (8) | 0.327 | -0.49 (6) | 0.356 |
| orange_s_lo | ref_s_scale | -0.07 (8) | 0.882 | 0.26 (6) | 0.658 |
| blue_h_lo | blue_peak_h | 0.01 (8) | 0.990 | 0.31 (6) | 0.564 |
| blue_h_lo | ref_hue_shift | -0.22 (8) | 0.610 | -0.14 (6) | 0.803 |
| blue_h_hi | blue_peak_h | 0.11 (8) | 0.794 | 0.20 (6) | 0.711 |
| blue_h_hi | ref_hue_shift | -0.51 (8) | 0.206 | -0.12 (6) | 0.839 |
| blue_s_lo | blue_s_p90 | 0.86 (8) | 0.011 | 0.89 (6) | 0.033 |
| blue_s_lo | ref_s_scale | -0.45 (8) | 0.267 | -0.20 (6) | 0.714 |

## Residuals by light kind

Hand − the FIXED value (mean |r| / mean r (n)):

| threshold | mixed (n) | overhead (n) | lamp (n) | window (n) |
|---|---|---|---|---|
| orange_h_lo | 5.0 / -5.0 (1) | 6.0 / -6.0 (1) | 1.3 / 1.3 (3) | - |
| orange_h_hi | 7.0 / -7.0 (1) | 1.0 / 1.0 (1) | 10.7 / 10.7 (3) | - |
| blue_s_lo | 0.0 / 0.0 (1) | 18.0 / 18.0 (1) | 61.0 / -61.0 (3) | - |

Box target − the nested line, leave one place out:

| threshold | mixed (n) | overhead (n) | lamp (n) | window (n) |
|---|---|---|---|---|
| orange_h_lo | 6.5 / -6.5 (1) | 6.6 / -6.6 (2) | 6.0 / 6.0 (3) | 5.6 / -5.6 (2) |
| orange_h_hi | 5.8 / -5.8 (1) | 7.6 / -4.2 (2) | 9.7 / 9.7 (3) | 6.1 / -4.4 (2) |
| orange_s_lo | 15.5 / -15.5 (1) | 18.9 / 4.0 (2) | 2.7 / -2.1 (3) | 33.0 / -15.2 (2) |
| blue_h_lo | 1.4 / 1.4 (1) | 4.6 / 3.1 (2) | 6.7 / -6.7 (3) | 5.0 / 4.6 (2) |
| blue_h_hi | 1.4 / 1.4 (1) | 1.8 / 0.3 (2) | 1.5 / -1.5 (3) | 3.8 / 2.5 (2) |
| blue_s_lo | 33.4 / 33.4 (1) | 25.9 / -25.9 (2) | 102.8 / -102.8 (3) | 68.3 / 68.3 (2) |

## The rule's leave-one-place-out folds

| held-out place | training places with hand labels | b per term |
|---|---|---|
| abp_gray | home_ottoman, uc_palewood | orange_h_lo +0.388; orange_h_hi -0.355; blue_s_lo +0.082 |
| campus_study | abp_gray, home_ottoman, uc_palewood | orange_h_lo +0.216; orange_h_hi +0.142; blue_s_lo +0.042 |
| home_ottoman | abp_gray, uc_palewood | orange_h_lo +0.229; orange_h_hi +0.198; blue_s_lo +0.072 |
| uc_palewood | abp_gray, home_ottoman | orange_h_lo +0.165; orange_h_hi +0.183; blue_s_lo -0.039 |
| abp_white | abp_gray, home_ottoman, uc_palewood | orange_h_lo +0.216; orange_h_hi +0.142; blue_s_lo +0.042 |
| home_white | abp_gray, home_ottoman, uc_palewood | orange_h_lo +0.216; orange_h_hi +0.142; blue_s_lo +0.042 |
