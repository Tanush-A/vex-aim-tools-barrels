# Adaptive color rule: FAIL — 2026-11-23, git 6ace4f5

One command: `python barrels/experiments/2026-11-24_adaptive/run.py` (plan and acceptance: `PREREG.md`). Train frames only; the 60 test frames are refused before any image is opened. Nothing is adopted; the default model is unchanged (`eb863d84`).

**Data.** 8 ordinary conditions at 6 places; slider labels on 5 conditions at **3 independent places** (abp_gray, home_ottoman, uc_palewood). Extreme (ceiling: under half the barrels even with its own best thresholds): lampmid3_ottoman. Parked extreme: the wood lamp ladder, the black table.

## 1. Does a relation show? (leave one PLACE out; the honest test)

**hand target**: **no threshold** is predicted from the frame's histogram better than by the fixed value (or the mean of the other places).
**box target**: a frame-histogram line beats the fixed value and the mean of the other places, in two thirds of the places, for: **blue_h_hi**.

| threshold | conditions / places | fixed | mean of other places | nested line, leave one place out | leave one condition out (flatters) | LOPO prediction better than fixed in (places) | place-level Spearman, primary feature |
|---|---|---|---|---|---|---|---|
| orange_h_lo | 5 / 3 | 4.1 | 5.7 | 5.7 (fallback: too few places) | 2.3 | 2 of 3 | orange_peak_h: 0.50 (p 1.00, n 3) |
| orange_h_hi | 5 / 3 | 6.2 | 11.4 | 11.4 (fallback: too few places) | 1.4 | 0 of 3 | orange_peak_h: 1.00 (p 0.33, n 3) |
| orange_s_lo | 5 / 3 | 27.9 | 17.0 | 17.0 (fallback: too few places) | 32.3 | 3 of 3 | orange_s_p90: -1.00 (p 0.33, n 3) |
| blue_h_lo | 5 / 3 | 4.8 | 10.3 | 10.3 (fallback: too few places) | 11.8 | 0 of 3 | blue_peak_h: -0.50 (p 1.00, n 3) |
| blue_h_hi | 5 / 3 | 8.0 | 8.4 | 8.4 (fallback: too few places) | 7.4 | 1 of 3 | blue_peak_h: -0.50 (p 1.00, n 3) |
| blue_s_lo | 5 / 3 | 26.3 | 58.3 | 58.3 (fallback: too few places) | 13.7 | 0 of 3 | blue_s_p90: 0.50 (p 1.00, n 3) |

Hand target above (mean |error| per place, then over places; hue or S units). With fewer than 4 hand-labelled places no feature can be chosen inside the loop and the line falls back to the mean of the others. The box-target version of this table is in `analysis.md`.

## 2. Hand labels against box-derived thresholds

Median |hand − box| over 5 conditions: orange_h_lo 4.0; orange_h_hi 1.0; orange_s_lo 26.5; blue_h_lo 3.0; blue_h_hi 3.0; blue_s_lo 46.0. The 2026-11-18 PREREG lets box stand in for hand at ≤ 3 hue and ≤ 20 S units: **it cannot**; box is a cross-check only.

## 3. Mixed light

Mixed-light ordinary conditions: 1. Residual (hand − rule's threshold, leave one place out), mean |r| / mean r (n) by light kind:

| threshold | mixed (n) | overhead (n) | lamp (n) | window (n) |
|---|---|---|---|---|
| orange_h_lo | 5.0 / 5.0 (1) | 4.0 / -4.0 (1) | 2.8 / 2.8 (3) | - |
| orange_h_hi | 17.0 / -17.0 (1) | 3.2 / 3.2 (1) | 11.9 / 11.9 (3) | - |
| blue_s_lo | 11.3 / -11.3 (1) | 22.9 / 22.9 (1) | 64.4 / -64.4 (3) | - |

Not judged: 1 mixed condition(s); 2 needed. The fixed model's residuals and the box-target nested line are in `analysis.md`.

## 4. The rule and its test

Rule (PREREG part B): `threshold = fixed + b · (feature − home's feature)`, clipped, per frame from its own histogram; fit with every place weighted equally. Fit on all hand-labelled places now: `orange_h_lo` ← `orange_peak_h`: b = +0.216 (home 21.2, clip ±10); `orange_h_hi` ← `orange_peak_h`: b = +0.142 (home 21.2, clip ±10); `blue_s_lo` ← `blue_s_p90`: b = +0.042 (home 105.1, clip ±60). Slope across the leave-one-place-out folds: orange_h_lo +0.165 to +0.388; orange_h_hi -0.355 to +0.198 (**the sign flips**); blue_s_lo -0.039 to +0.082 (**the sign flips**).

Leave one place out, per condition: found / barrels (false boxes; boxes on empty frames).

| condition | place | light | fixed | adaptive | hand labels (ceiling, not a method) |
|---|---|---|---|---|---|
| both_abpgray | abp_gray | mixed | 10 / 16 (2; 0) | 16 / 16 (2; 1) | 15 |
| CAMPUS | campus_study | overhead | 35 / 35 (0; 0) | 35 / 35 (0; 0) | - |
| lampcool6_ottoman | home_ottoman | lamp | 3 / 15 (0; 0) | 2 / 15 (0; 0) | 15 |
| lampmid6_ottoman | home_ottoman | lamp | 6 / 15 (0; 0) | 2 / 15 (1; 0) | 13 |
| lampwarm6_ottoman | home_ottoman | lamp | 0 / 15 (1; 0) | 0 / 15 (0; 0) | 12 |
| overheaddim_palewood | uc_palewood | overhead | 12 / 15 (1; 0) | 12 / 15 (1; 0) | 11 |
| window_abpwhite | abp_white | window | 26 / 32 (2; 1) | 26 / 32 (2; 1) | - |
| HOME | home_white | window | 28 / 29 (1; 0) | 28 / 29 (0; 0) | - |
| **total** | | | 120 / 172 (7; 1) | 121 / 172 (6; 2) | |

**Acceptance (PREREG part C):**

- C1: **FAIL** — 3 places with slider labels (abp_gray, home_ottoman, uc_palewood); 5 needed
- C2: **FAIL** — found 121 vs 120 fixed (+1; 3 needed), more in 1 places (2 needed)
- C3: pass — false boxes 6 vs 7 fixed (at most +2)
- C4: **FAIL** — new box(es) on an empty frame in both_abpgray
- C5: **FAIL** — score drops by more than 0.02 in lampcool6_ottoman, lampmid6_ottoman
- C6: pass — the rule adds no failing gate row (the fixed model's own: 4A8B_window_abpwhite|occlx)
- C7: pass — not applicable: no place new since the frozen rule

**Verdict: FAIL — the default stays the fixed model.**

Files: `analysis.md` (part A in full), `detection.csv`, `per_condition.csv`, `rule.json`, `model_adaptive.json` (`tools/report.py --gate --cand-model` takes it), `gate.txt`, `config.json`.
