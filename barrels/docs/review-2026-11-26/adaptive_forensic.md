# Adaptive thresholds: what was tried and why it failed (forensic review)

Reviewer's report on the snapshot `final/barrels` plus `docs/REPORT-2026-11-25.md`. Train frames only; no test frame was loaded or viewed. My own scripts and outputs are in `scratchpad/work_adaptive/` (`a_`…`p_*.py`, `*.out`, `perturb_res.json`, `decomp_res.json`, `band_warmth.csv`).

## The verdict in five lines

1. **The representation was not the limit in the ordinary places.** Tanush's own per-condition thresholds, run through the detector, find **281 of 307** barrels with 7 false boxes (fixed: 211, 7). On the 243 barrels with vendor files that is **218 against the vendor's 177** (fixed 148). A rectangle per condition beats the vendor. The failure is in *predicting* the rectangle from the frame.
2. **The prediction problem was unlearnable as posed:** 3 to 5 independent places (only 2 with warm light), a target that is mostly arbitrary, and features that measure the room rather than the barrels.
3. **The pass rules could not be passed.** The hand-labelled thresholds themselves, the target of the whole exercise, fail clauses A1, A2 and A3. So do 10 of 12 one-step neighbours of the fixed model (hue ±1, S ±3).
4. **One idea has real support and was killed by the rules, not by the data:** the blue saturation floor following the light. In-sample the light reading tracks the barrels' real blue saturation at r = −0.96 over 17 conditions, and round 1 gained 22 barrels and lost none.
5. **Mostly bad logic, some bad luck.** Bad logic: the target, the features, the model form, the validation unit, the pass rules. Bad luck: only two warm places, and one lamp-lit white cloth on one empty glass frame.

Caveat on my re-scoring: the snapshot's detector includes the verify step, so my false-box counts are lower than in the 2026-11-25 summaries (fixed: 211 found in both; 7 false here, 13 there). The hand-threshold ceiling is in-sample and optimistic (see 2e).

---

## 1. What was tried, one row per attempt

| # | attempt (doc date) | target predicted / optimized | inputs | model form, free parameters | independent data | validation | pass rule | result | stated reason |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Ceiling check (11-16) | barrels found, with thresholds re-fit from each frame's own labelled pixels | the labels (an oracle) | home recipe re-run per frame; 6 numbers per frame, 3 arms | 4 places; 137 frames; 152 target barrels (black + bright wood) | none (in-sample by design) | hypothesis: "well over half of 152" | 53 of 152, 32 false boxes | orange range that fits the barrels paints the wood table; stripes come out in pieces |
| 2 | Pooled fit (11-16) | detection score | labelled pixels pooled over tables | one fixed rectangle pair; 6 numbers; 3 arms × 2 runs | same 4 places | leave one *scene tag* out (every place always in training) | home ≥ 0.91 and campus ≥ 0.97; no box on a clean negative; then most found | no arm passes; home 0.66–0.89; best 28 of 152 | wide ranges paint the wood table and the home wall; tight ones miss the barrels |
| 3 | Histogram relation, dry run (11-18) | thresholds read from the boxes (no hand labels yet) | 9 global histogram features | Spearman on 54 pairs (12 primary, Holm); nested one- and two-feature line | 2 ordinary conditions (+7 extreme, of which 6 are one table) | leave one condition out | A (Holm p < 0.05), B (error below both baselines), C (detection); only at n ≥ 8 | not evaluable; rules fit mostly on wood find 36 of 64 on home + campus against 59 fixed | too few conditions |
| 4 | Relation, re-run (in the 11-24 analysis) | hand slider thresholds | same 9 features | same | hand: 5 conditions, **3 places**, 15 frames; box: 8 conditions, 6 places | leave one *place* out | same | no threshold beats the fixed value; with 3 places the nested fit falls back to the mean | too few places; hand and box targets disagree (median 4 / 1 / 26.5 and 3 / 3 / 46) |
| 5 | Adaptive line rule (11-24) | hand thresholds, 3 of the 6 | `orange_peak_h`, `blue_s_p90` | `fixed + b·(feature − home's feature)`, clipped; **3 slopes** | slopes fit on 3 places (2 per fold); tested on 8 conditions, 6 places, 90 frames, 172 barrels | leave one place out; gate; a frozen copy for new places | C1–C7 (≥ 5 labelled places; ≥ +3 barrels in ≥ 2 places; ≤ +2 false; no new empty-frame box; no condition −0.02) | 121 against 120; gray 10 → 16, ottoman 9 → 4; fails C1, C2, C4, C5; two slopes flip sign between folds | too few places; the ottoman's orange peak sits below home's |
| 6 | Adaptive range, R2 (11-24) | the per-frame "working range" of each threshold | one primary feature per threshold | up to 6 lines (5 kept), slope chosen to land in the most ranges | 18 frames, 6 conditions, 3 places | as row 5 | ranges hold jointly on ≥ 2/3 of frames; beats fixed on one threshold; C2–C6 | ranges hold on 10 of 18; 112 against 121; breaks campus and home | ranges are wide but shifted between places; one-at-a-time ranges overstate the freedom |
| 7 | Relation on ranges (11-25 step 3) | working ranges | 11 features × 2 fits | line or interval fit | 14 conditions, **5 places**, 42 frames | leave one place out | none ("description, not proof") | some feature "beats" both baselines on 5 of 6 thresholds, a different one each time | 22 tries per threshold, a chance winner is expected |
| 8 | C1, re-centred constant (11-25) | J = Σ over places of (found − 2·false) / barrels, under eligibility limits | none | one constant; **480-setting grid**, 5 free numbers | 8 places, 17 conditions, 154 frames, 307 barrels | leave one place out | A1 (net ≥ +20; better in ≥ 4 of 8 places, worse in none), A2 (empty frames), A3 (no condition −0.02), A4 (gate) | 212 against 211, net +5; ottoman mid 6 −0.237 | the ottoman's orange shift is not learnable from the other places |
| 9 | C2, blue follows the light, whole frame (11-25 round 1) | same J | warmth of the brightest 5 % of the frame | ramp on the blue S floor and blue hue low end; **72 settings**, 4 numbers | same; only **2 places** have a warm condition | same | same | **+22 found, 0 lost**, +6 false, net +10; fails A1 (2 of 8 places), A2 (one box on `lampmid6_glass_neg_02`), A3 (−0.023) | the white patch is contaminated by orange barrels and yellow clutter |
| 10 | C2b, light read from rows 0–49 (round 2) | same | warmth of the brightest 20 % of rows 0–49 | same grid | same | same | same | +11 found, +9 false, net −7; fails all three | the floor lands at 55–65, the blue body is painted in pieces |
| 11 | C3 / C3b, both (rounds 1 and 2) | same | as C1 + C2 | **320 settings**, 5 numbers | same | same | same | net −1 / −2; fails A1, A3 | as C1 |

No recorded acceptance test in this line of work was passed.

---

## 2. Root causes, weighed

### a. Ill-posed target (predicting a human's slider values): **ACCEPT, a primary cause**

- **The labelled point is mostly arbitrary inside a wide range.** Median width of the range of values that work as well as his, against the between-condition SD of his values (42 ordinary frames, `ranges.csv`):

| threshold | working-range width (median) | between-condition SD of his value | ratio |
|---|---:|---:|---:|
| orange hue low | 22 | 4.9 | 4.4 |
| orange hue high | 9 | 5.4 | 1.7 |
| orange S floor | 63 | 22.1 | 2.8 |
| blue hue low | 75 | 18.0 | 4.2 |
| blue hue high | 15 | 8.6 | 1.7 |
| blue S floor | 75 | 74.8 | 1.0 |

- **Labels inside one condition do not agree.** Median spread over a condition's 3 frames: 4 / 3.5 / 31.5 / 3 / 8 / 42 (same order). Worst: 34 hue units and 129 S units (`lampcool6_bathtile`), 100 S units (gray table). Clutter against no clutter moves the S floors by 20–27 units on average.
- **Only two thresholds carry a place signal.** Share of label variance explained by place: orange hue high 0.78, blue S floor 0.79, blue hue low 0.55; the other three 0.13–0.20. Those two are the two real physical effects (2d). The other four were noise being regressed.
- **The labels are not independent hand measurements.**
  - Ottoman: orange hue high is 23 on 9 of 9 frames and 25 on 3 of 3 (the tool's "copy previous frame" key).
  - Bathroom: blue hue low is exactly 60 on 8 of 12 frames, the slider's lower limit at the time (censored).
  - Glass and bathroom: 25 of 27 labels started from a *computed* proposal built from the frame and the hand boxes (`proposed_by: computed`); 2 more were left at the adopted values.
- **The range version did not rescue it.** The six one-at-a-time ranges work together at all corners on 0 of 18 frames; the fixed values sit inside all six ranges on 5 of 42 frames.
- **The fall-back target (thresholds from boxes) differs from the hand target** by more than the project's own limit, and its one "lead" (blue S floor against `blue_s_p90`, rho 0.89, n = 6) is near-circular: both are read off the same blue pixels.

### b. Sample size: **ACCEPT, a primary cause**

- **Units of evidence:** 3 labelled places (11-24), 5 (11-25), 8 for detection. For the light rule the effective n is **2**: only the bathroom and the ottoman have a warm condition. Leaving one out fits the ramp on the other alone.
- **Choices against that:** 54 feature-threshold pairs on 3 places; 22 tries per threshold on 5 places; 3 slopes on 2 places per fold; grids of 480, 72 and 320 settings on 7 places.
- **The relation test could not be passed with the data in hand.** Smallest possible permutation p: 0.33 at n = 3, 0.017 at n = 5. Holm over 12 pairs needs p < 0.0042, impossible below n = 6. At n = 8 it needs |rho| ≥ 0.905; power is 7 % for a true correlation of 0.7 and 30 % for 0.9. About 12 places are needed for 80 % power at r = 0.9, more than 20 at r = 0.7 (`j_power.py`).
- **No positive result was ever distinguishable from noise at place level.** C2 round 1 is real at barrel level (22 gained, 0 lost) but is 2 places up, 1 down. Even the hand-threshold oracle is 4 places up, 1 down: sign test p = 0.375.
- **Instability shows it:** the line rule's orange-high slope ranges from −0.355 to +0.198 across folds. R2's fitted slopes are −7.88, −1.65, −1.50 against a ±10 clip, which is a two-state switch, not a line.

### c. Features measure the scene, not the barrel or the light: **ACCEPT, a primary cause**

- **Barrels are a few percent of the pixels.** Hand boxes cover a median 4.2 % of the gated region (quartiles 2.9–7.1 %).
- **The orange peak is usually not the barrel.** It sits ≥ 5 hue units from the barrels' own hue on 37 of 99 frames (S ≥ 150 version; 48 of 99 at S ≥ 100):
  - ABP white: 16 of 16 frames, peak 19–22 against barrel 8.
  - Bathroom: 15 of 16, peak 20–21 against barrel 9. The floor is 88–91 % of the gated pixels in the orange window.
  - Glass: 3 of 20, peak 23.
- **The home anchor of the line rule is the home background.** Home's `orange_peak_h` is 21.25 while home barrels are hue 7; home's `blue_s_p90` is 105 while home blue barrels are S 232 (it reads the bluish wall). So "distance from home" compares a wall at home with a barrel elsewhere.
  - Ottoman: the peak (15–20) is the barrel, because the lid is black. It reads *below* home's 21, so the rule narrowed orange where the labels widen it: 9 → 4 of 45.
  - Gray table: the one win (10 → 16) came from a peak at hue −7, which is not the barrels either (hue 1–2), pushing the range to the clip, plus the one new empty-frame box.
- **Whole-frame white patch (round 1): contaminated, as the addendum says.** Under white light it reads 0.50 on `lampcool6_bathtile close_01`, up to 0.40 on the cool ottoman, 0.18 on a glass close-up.
- **Rows 0–49 (round 2): a measurement of whatever stands behind the table, after the camera's own white balance** (`band_strips.png`):
  - Bathroom: a brown wood cabinet front with a pale strip at the right (band median S 116–193).
  - Ottoman: curtain, speaker grille, wood.
  - Glass: dark shelves and a white cloth. The empty frame `lampwarm6_glass_neg_02` reads 0.13 and is where the round-2 false box appeared; the lamp-lit cloth is the likely source (I did not isolate it).
  - Home: a blue-gray wall, reading −0.10.
  - ABP gray: windows, 14 % of pixels clipped.
- **Yet the band reading works in-sample:** against the barrels' real blue S, Spearman −0.91, Pearson −0.96 over 17 conditions (`n_floor.out`). That is carried by two lamp-only rooms. A warm-colored wall in daylight would read as a warm light; no such place is in the data. Can't tell if it generalizes.

### d. Model form: **ACCEPT that the form was wrong; REJECT "one global shift" as the fix**

There are two separate effects, and neither is a shift of all colors together (medians from `gates.md`, gains against home, `g_physics.py`):

| condition | orange body RGB (hue) | blue body RGB (hue, S) | orange gain R, G, B | blue gain R, G, B |
|---|---|---|---|---|
| home | 178, 64, 25 (8) | 12, 54, 134 (110, 232) | 1, 1, 1 | 1, 1, 1 |
| bathroom mid 6 | 184, 70, 24 (9) | 42, 56, 62 (99, 82) | 1.03, 1.09, 0.96 | 3.5, 1.04, 0.46 |
| bathroom warm 6 | 191, 66, 24 (8) | 50, 50, 43 (30, 36) | 1.07, 1.03, 0.96 | 4.2, 0.93, 0.32 |
| ottoman cool 6 | 122, 74, 24 (15) | 26, 64, 100 (105, 189) | 0.69, 1.16, 0.96 | 2.2, 1.19, 0.75 |
| ottoman warm 6 | 136, 73, 22 (13) | 45, 52, 58 (104, 57) | 0.76, 1.14, 0.88 | 3.8, 0.96, 0.43 |

- **Effect 1, blue fades to gray under warm or dim light; orange does not move.** In the bathroom orange keeps its gains near 1 while blue's red channel rises 3.5–4.2× and its blue channel falls to 0.32–0.46. A per-channel gain cannot do both. The blue body ends at a chroma (max − min) of 6–20 gray levels at V ≈ 50–60. HSV saturation is a ratio, so at that signal level a small additive offset collapses it. At the same light reading, dim (mid 3) gives S 46 and bright (mid 6) gives S 79: brightness matters as well as light color.
- **Effect 2, orange hue moves with the surface, not with the lamp color.** On the ottoman orange is hue 14–16 under the cool, mid and warm lamp alike (G/R 0.54–0.61 against 0.35 at home). The gray table goes the other way (hue 1–3). This looks like the camera's exposure or white balance reacting to the scene. Untested; the question of locking them is still open in `STATUS.md`.
- **So:** six edges on independent lines through a home point is wrong, and "the illuminant moves everything" is wrong too. Hue / saturation is not a space where either effect is a simple shift. The only pairing with support is light warmth → blue S floor.

### e. The representational ceiling: **REJECT as a cause in the ordinary places**

Per-condition hand thresholds (median of the 3 labels, applied to all of the condition's train frames; `k_analyse.out`), against fixed and vendor:

| place | barrels | fixed | hand thresholds | vendor |
|---|---:|---:|---:|---:|
| gray table | 16 | 10 | 15 | 16 |
| ABP white (no slider labels) | 32 | 26 | 26 | 24 |
| bathroom (4 lamps) | 60 | 16 | **50** | 28 |
| glass (5 lights) | 75 | 74 | 75 | 60 |
| ottoman (3 lamps) | 45 | 9 | **40** | 37 |
| pale wood | 15 | 13 | 12 | 12 |
| **all with vendor files** | 243 | 148 | **218** | 177 |
| false boxes | | 7 | 7 | 30 |

- The vendor gap is 29 barrels; a per-condition rectangle closes it and adds 41 more. Contrast black + wood on 11-16: 53 of 152 with perfect thresholds.
- **By color** (`m_decomp.out`): hand blue alone gives 186 of 243, already above the vendor; hand orange alone 167; both 218. The gap is mostly blue under warm light (bathroom 16 → 47), then orange on the ottoman, which needs both (9 → 24 with orange, 15 with blue, 40 with both).
- **Optimistic:** 3 of each condition's 7 frames are the labelled ones, and the glass and bathroom labels were seeded from the boxes. On the fixed model's own test look glass fell from 74 of 75 (train) to 6 of 10, so train ceilings overstate.
- Even with hand thresholds the warm bathroom is 6 of 15 (vendor 0): blue reads hue 26–44 there.

### f. Conflicts no threshold can solve: **ACCEPT, but it is narrow**

Documented, and checked where I could:

- **Ottoman orange against the warm bathroom floor (real).** Ottoman barrels need orange up to hue 21–23 at S ≥ 160–185. The bathroom floor at hue 14–18 with S ≥ 185 covers 4.7 % of the frame under mid 6 and 20 % under warm 6. Six constant orange ranges with a high S floor (to hue 17–23, S ≥ 170–200) plus hand blue find 252–267 of 307 but draw 14–25 false boxes, 9–18 of them in the bathroom (hand thresholds: 281 and 7).
- **Blue S floor.** Warm light needs S ≥ 10–50; the home wall (S ≤ 110) and the glass table need ≥ 113.
- **Warm bathroom blue** is outside any blue range (hue 26–44, S 44).
- **Ottoman dark blue.** 8–41 % of blue body and stripe pixels are under the V ≥ 40 gate.
- **Pale wood and the wood ladder.** The table itself is orange (wood ceiling 66–91 %).
- **Pooled fit.** Blue S ≥ 65 brings back the home wall (12 false boxes at home).

Not a general impossibility: outside the bathroom and the ottoman, non-barrel pixels at hue 14–25 with S ≥ 185 are at most 0.16 % of the frame in every condition except ABP white (2.2 %).

### g. Evaluation coupling: **ACCEPT as real; REJECT as the main cause**

- **Non-monotone detector:** 138 "more paint, barrel lost" events on 35 of the 45 slider frames; in 94 the lost barrel's own core gained paint; 90 added ≤ 150 px outside.
- **At candidate level it is small.** C1 lost 5 barrels while gaining 6; C3 lost 5; C2, a pure loosening of blue, lost none. My six looser one-step neighbours got worse on 11 of 774 painted-more frames (1.4 %).
- **The bigger coupling: every barrel needs both colors.** In the bathroom the orange bodies sit inside the fixed range (hue 7–13, S ≥ 209 at the 5th percentile, against 3–13 and ≥ 140), and the fixed model still finds 1 of 8 orange barrels under each of the mid 3, mid 6 and warm 6 lamps, because their blue stripe is not painted. A barrel is hostage to the worse of the two colors.
- **No pixel-level metric on the new conditions.** No masks exist there. The paint share inside box cores and the outside paint exist (`hsrange`) but were never an acceptance criterion.
- **Results depend on the detector version:** the same fixed model has 13 false boxes in the 11-25 test and 7 with the verify step.

### h. Acceptance rules against noise: **ACCEPT, a primary cause of "every round failed"**

- **One box decides a clause.** A new condition is 7 frames, 15 barrels, 1 empty frame. One lost barrel is −0.033 of score at ceiling and up to −0.06 mid-range; one false box is −0.029. So "no condition drops more than 0.02" means "no single box worse in any of 17 conditions". "No new box on an empty frame" is one box on 22 frames.
- **The fixed model fails against itself.** Of 12 one-step neighbours (hue ±1, S ±3), 10 fail the 0.02 clause and 1 fails the empty-frame clause. Judged the other way, the fixed model fails against 9 of 12 neighbours. Example cliffs: orange hue low 3 → 4 costs the gray table −0.36; blue hue low 103 → 104 costs the cool bathroom −0.27.
- **The target itself fails.** Hand thresholds: +70 barrels, same false boxes, yet A1 FAIL (pale wood −1), A2 FAIL (two empty bathroom frames), A3 FAIL (pale wood −0.055) (`p_oracle_verdict.out`).
- **Some clauses could not be met by construction.**
  - C2's A1 needs improvement in ≥ 4 of 8 places; the rule acts only under warm light, which exists in 2. The addendum says so and keeps the clause.
  - Rows 5 and 6 needed ≥ 5 labelled places with 3 in hand.
  - C1 was tested after the sweep had already shown no constant fits every place.
- **Earlier rules were too loose, and were bent the other way.** 11-08: the pre-registered rule picked the config with home 0.69 because it "ignored the home score". 11-18 and 11-23: detector switches that failed a clause by a box or two (`cap_behind`, `stripe_join`, `stripe_bridge`, `thin_frame`) were merged on Tanush's word. Color candidates failing by one box were not.

### i. Forking paths: **ACCEPT as a fact; it does not explain the failures**

- **What was chosen in-sample before each "pre-registered" test:** which 3 thresholds adapt (an ablation on the same labels); which conditions are "ordinary" (a ceiling rule written after looking); the three C families and their grids (exploration on all 154 frames; its outputs are not in the results folder).
- **The registration is commit order within minutes, by one session:** PREREG 16:43:01, `test.py` 16:44:29, round 1 result 16:56:32, round-2 addendum 16:57:31, round 2 result 17:01:26. Line rule: PREREG 01:35, FAIL 01:44.
- **Dates:** every commit carries machine date 2026-11-23, while the docs say 11-24 and 11-25 ("Written 2026-11-25 (machine date 2026-11-23)"). The line rule, the range rule and both color rounds ran inside about 15.5 hours of one machine day.
- **The promised honest test was never run.** The rule "frozen tonight" for "tomorrow's places" has only run 01 on every branch. I ran it on the glass and bathroom train frames: the line rule finds 89 against 90 (fails C7 by one barrel); R2 finds 75 against 90 with 11 false against 4.
- **Evidential value:** forking inflates positives, and everything failed, so the failures stand. It lowers the worth of the leads. Example: the report's "16 → 36 of 60, beating the vendor's 28" is the in-sample final model; held out it is 33, and the last permitted round scored net −7.

### j. Search space: **ACCEPT; the search stayed inside "move the edges of an H / S rectangle"**

- **Tried:**
  - fixed HSV (10-07);
  - gray-world white balance, diagnostic only, ruled out by decision;
  - RGB box with a per-image S floor (v1);
  - YUV chroma box (tie, one light);
  - barrel-referenced re-fit (one light: tie to −0.07; the only thing that helped under *synthetic* casts, 0.44 → 0.57; "back on the table once a second light is labelled", never re-run);
  - the hs rectangle; pooled fit; per-frame oracle;
  - an H × S lookup, as a ceiling only, never as a method;
  - histogram line; range interval fit; constants grid;
  - orange hysteresis (in-sample only: +20 found, +8 false; dropped, no outputs kept);
  - orange peak placement (in-sample: 0 of 32 on ABP white);
  - blue floor from frame warmth, from light warmth, and from the frame's strongest blue (in `rules.py`, unreported).
- **Never tried:**
  - the stripe as a *relative* color (the band inside an orange body that is not orange), which needs no absolute blue threshold;
  - shape or edges first;
  - a two-pass re-fit from confident barrels on the multi-light data;
  - a per-pixel classifier or lookup trained across conditions;
  - chromaticity spaces on the new data (Lab a* separated orange from wood on 10-07: 50 against 15–20);
  - locking the camera's exposure and white balance;
  - a one-off calibration per place.

---

## 3. The real reasons, ranked

1. **They tried to learn a rule from three to five rooms.** A rule that maps "what the picture looks like" to "six numbers" needs many different rooms to learn from. There were 3, then 5, and only 2 with yellow light. The project's own significance test could not be passed below 6 places, and at 8 it had a 30 % chance of seeing even a near-perfect relation. *Evidence:* `results/2026-11-24_adaptive/summary.md` (every threshold "fallback: too few places"); `j_power.py`.
2. **The thing being predicted was mostly arbitrary.** For four of the six numbers, the range that works on one frame is 1.7 to 4.4 times wider than the difference between rooms, and Tanush's three labels in one room differ by up to 34 hue and 129 saturation units. Some were copied, pinned at the slider's end, or started from a computed proposal. *Evidence:* `results/2026-11-25_color/ranges.csv`, `data/labels/*_hs.json` (`a_labels2.py`, `b_ranges.py`).
3. **The measurements looked at the room, not the barrels.** Barrels are about 4 % of the picture. The "orange peak" was the floor or the furniture on 37 of 99 frames, and at home it read 21 while home barrels are 7, so the rule's reference point was a wall. *Evidence:* `results/2026-11-25_color/features.csv` (`c_features.py`); `rule_frozen_2026-11-23.json` (`f_home` 21.25).
4. **The pass rules failed anything that changed a single box.** The fixed model fails them against 10 of 12 of its own nearest neighbours, and Tanush's hand thresholds (+70 barrels) fail all three clauses. The light rule could not pass "better in 4 of 8 places" when only 2 places have yellow light. *Evidence:* `k_analyse.out`, `p_oracle_verdict.out`; PREREG addendum of `2026-11-25_color`.
5. **Two different problems were treated as one "shift".** Yellow or dim light turns blue paint gray while orange stays put; a dark or gray surface moves orange's hue whatever the lamp. And the detector needs both colors on every barrel, so one bad color loses all of them. *Evidence:* `results/2026-11-25_color/gates.md` (bathroom blue 42, 56, 62 against orange 184, 70, 24; ottoman orange hue 14–16 under all three lamps).

What did **not** cause it: the rectangle itself (hand rectangles find 218 of 243, vendor 177), and the detector's non-monotone behaviour (real, but about 1 % of frames at candidate level).

---

## 4. What the existing results already support

- **A threshold set per place works.** 281 of 307 on train frames with 7 false boxes, from 3 labelled frames per condition. The robot works in one place per session, so a short calibration per place is supported by the data. Any automatic version has to reach these numbers, not Tanush's slider positions.
- **Blue is the bigger half, and one cue predicts it.** Hand blue alone lifts 148 → 186 of 243. The light reading tracks real blue saturation at r = −0.96 over 17 conditions, and C2 round 1 gained 22 and lost 0. This is the one adaptive idea with evidence. It needs:
  - places with warm light beyond two before any leave-one-place-out claim;
  - parameters set from the physics rather than chosen on the one remaining warm place (round 2 failed on `w1` = 0.3 picked from the ottoman alone, which left the bathroom floor at S ≈ 64);
  - a trap for bright warm-lit white objects.
- **The bathroom's orange barrels are already painted by the fixed model and still lost** (1 of 8). The evidence points at removing the dependence on an absolutely-colored blue stripe, not at more orange tuning.
- **Orange on the ottoman is a camera or surface effect, not a light-color effect** (hue 14–16 under cool, mid and warm). The light rule cannot fix it, and it conflicts with the warm bathroom floor at pixel level. The open question about locking exposure and white balance is the cheapest test of its cause.
- **The pass rules need a noise floor.** One-step neighbours of the fixed model move single conditions by up to 0.36. A clause tighter than what the fixed model does against its own neighbours cannot separate a good candidate from a bad one.
- **Use the boxes, not the sliders, as the color target.** There are 228 boxed train frames with barrels against 45 slider labels. Barrel-pixel paint share and outside paint are already computed in `hsrange` and do not go through the detector.
