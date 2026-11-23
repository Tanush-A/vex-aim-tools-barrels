# Pre-registration: the adaptive color rule, and TODO F updated (2026-11-24 experiment)

Written 2026-11-23, evening, **before any test of the rule**. Committed on `wip/adaptive` before the rule's
code ran on a single frame. Script: `run.py` in this folder (one command, no arguments, re-run tomorrow on
whatever conditions exist). Nothing is adopted by this experiment: the default color model stays `eb863d84`;
the rule lives behind a switch (`pipeline.Config.hs_adapt`, empty = off) and adoption is Tanush's decision after
the walkthrough.

## What was looked at before this was written (so the reader can judge the forking paths)

1. The 2026-11-18 relation script (`2026-11-18_hs_relation/run.py`) re-run on today's data: 9 ordinary
   conditions, 6 with slider labels (3 frames each). Its leave-one-condition-out (LOCO) picks `v_mean` for the
   orange hue ends and beats the fixed values; that is the four ottoman conditions (one table, one lamp,
   one room, the only dark place) vouching for each other.
2. The same with **leave one place out** (LOPO; places in `data/conditions.json`): with the hand target there are
   3 places (ottoman, pale wood, ABP gray), too few for a nested choice of feature (it falls back to the mean
   of the others, worse than the fixed values on every threshold). With the box target, 6 places: the nested
   one-feature rule beats the fixed values only for `orange_s_lo` (16.7 vs 23.3 S units, the feature changing
   between folds) and `blue_h_hi` (2.3 vs 5.4, which the mean of the other places also does: an offset between
   the box recipe and the adopted value, not a relation).
3. An ablation on the hand-labelled conditions: the adopted model with ONE threshold replaced by the hand value.
   The thresholds that change what is found: `orange_h_lo` (ABP gray 10 → 16 of 16), `orange_h_hi` (ottoman
   cool6 3 → 13 of 15, mid6 6 → 9), `blue_s_lo` (ottoman warm6 0 → 5). The other three change nothing found.
4. The hand labels and the box-derived thresholds differ by a median of 4.5 / 1.0 / 30 (orange lo, hi, S) and
   3.5 / 3.8 / 46 (blue): more than the 2026-11-18 PREREG allows (3 hue, 20 S) for box to stand in for hand.

The rule below was written after 1–4. It is fit on those same hand labels, so tonight's test of it is
in-sample for the choice of thresholds and features; **the honest test is tomorrow's new places**, and part C
below scores a copy of the rule frozen tonight on exactly those.

## Conditions, places, light kinds, classes

- **Condition** = `{light}_{surface}`; **place** = the table and the room; **light** = window / overhead / lamp /
  mixed; both from `data/conditions.json` (one entry per condition; how to extend it is written in the file; a
  missing condition is guessed from its tags and flagged in the summary).
- **Class.** Parked as extreme (logged 2026-11-18, unchanged): the wood lamp ladder and `window_black`; brightness
  1 excluded. **New, mechanical, for every other condition, today's and tomorrow's: a condition is
  `extreme (ceiling)` when even its own best thresholds find fewer than half its barrels** (the larger of `box per
  frame` and `hand median`, today's detector): no color threshold can fix it, so it is not a target of a color
  rule. Otherwise ordinary. Applied today: the ottoman under `lampwarm6`, `lampmid6`, `lampcool6` is ordinary
  (the fixed model finds 0–6 of 15, hand thresholds 12–15: exactly what a rule should fix); `lampmid3_ottoman`
  (mean V 63, nothing finds more than 1 of 15) is extreme (ceiling); ABP gray, pale wood and ABP white are
  ordinary. The black ottoman lid is not the black table: it has no glare and its hand thresholds work.
- **The unit of evidence is the place.** Every leave-out test leads with leave one place out; leave one
  condition out is printed beside it, marked as flattering when a place has more than one condition.

## Part A — TODO F, updated (analysis; not the rule's test)

Unchanged from the 2026-11-18 PREREG (features, targets, primary pairs, Holm), plus:
- the hand − box difference per threshold and condition (hand is the target wherever it exists; box is the
  cross-check);
- Spearman at **place level** (place means), next to the condition level, with n = places;
- the nested one-feature prediction (feature chosen inside the loop) **leave one place out**, next to leave one
  condition out, against the fixed value and the mean of the other places;
- **residuals by light kind**: for each threshold, the LOPO residual (target − prediction) of each condition,
  mean and mean |·| per light kind, for the nested one-feature prediction and for the rule below. If the rule
  reads what the light did to the frame, mixed-light conditions should sit on the line like the others.
  **Report-only.** Flag: "light kind matters" when the mixed conditions' mean |residual| is more than twice the
  others' on a threshold, with at least 2 mixed conditions (with 1 it is printed, not judged).

## Part B — the rule

**Which thresholds adapt** (from the ablation, item 3): `orange_h_lo`, `orange_h_hi`, `blue_s_lo`. The other three
(`orange_s_lo`, `blue_h_lo`, `blue_h_hi`) stay at the adopted values: nothing found depends on them today.

**Feature per threshold, fixed in advance, one each** (the 2026-11-18 primary features that need no reference
histogram, from the frame alone: the pixels below row 50 with V ≥ 40):
- `orange_h_lo`, `orange_h_hi` ← `orange_peak_h`: the tallest hue in −10..30 among pixels with S ≥ 40.
- `blue_s_lo` ← `blue_s_p90`: the 90th percentile of S in hue 85..125 (S ≥ 40).
A frame whose window holds fewer than 200 pixels has no reading: the threshold stays fixed for that frame.

**Formula: a line through the home point.**
`threshold(frame) = fixed + b · (feature(frame) − f_home)`, clipped to `fixed ± 10` hue units (`± 60` S units).
`fixed` = the model's own value (the adopted `eb863d84`, or the leave-one-scene-out re-fit at home);
`f_home` = the mean feature of the home train frames (the frames the adopted model was fit on). So at home the
rule gives the adopted model, by construction; elsewhere it moves the threshold in proportion to how far the
frame's own histogram is from home's. Only the slope `b` is fit. An orange range that comes out empty
(lo ≥ hi) keeps the fixed range for that frame. Pixels are never changed; nothing is carried between frames.

**Fit.** `b` per threshold by least squares through the home point, on the ordinary conditions with slider
labels (condition-mean feature, median hand threshold), **each place weighted equally** (a place with four
conditions does not count four times). Home enters only as the anchor (its "label" is the adopted model, fit on
its hand-painted masks). Box-derived thresholds are not used for the fit (part A, item 4).

**Switch.** `pipeline.Config.hs_adapt`: a tuple of terms `(threshold, feature, b, f_home, max_delta)`; empty (the
default) = off, and the field is left out of the config hash when empty, so `eb863d84` is unchanged. A model
file with the switch on is written to `results/2026-11-24_adaptive/model_adaptive.json` (rule fit on all places),
which `tools/report.py --gate --cand-model <that file>` also accepts.

## Part C — the test, and what must be true (all on train frames; test frames are never opened)

Scored with today's detector (`DetConfig()`), v2 rule (`report.score_frame`).

1. **Leave one place out, detection.** For each place: `b` fit on the other places' hand labels (+ the home
   anchor), the rule applied to every frame of the held-out place. Per condition: found / missed / false and
   boxes on empty frames, fixed against adaptive. A fold whose training places have no hand label gives `b = 0`
   (the fixed model) and is flagged.
2. **The never-regress gate with the rule ON** (fit on all places): `report.make_report` + `gate.compare`
   against `results/baseline/baseline.json`, HOME leave-one-scene-out as always. The fixed model fails the gate
   today on one known box (`4A8B_window_abpwhite_occlx_15`, the striped-clutter trap, TODO A9); so the clause is:
   **the rule adds no failing row to the fixed model's failing rows.**
3. **Frozen tonight.** `rule_frozen_2026-11-23.json` (written by tonight's run, committed with it) applied
   unchanged to the places that have no hand label in it: found / false against fixed. Tonight: none.

**Acceptance (exit 0 only if every line holds).** Over the ordinary conditions, LOPO:

| # | clause |
|---|---|
| C1 | at least **5 independent places with slider labels** (today 3); fewer → "not enough places", fail |
| C2 | the rule finds **at least 3 more barrels** than the fixed model in total, and more in at least 2 places |
| C3 | at most **2 more false boxes** in total than the fixed model |
| C4 | **no new box on an empty frame** in any condition (boxes on `neg` frames ≤ the fixed model's, per condition), and none on a clean empty frame |
| C5 | no ordinary condition's score drops by more than 0.02 |
| C6 | the gate with the rule ON adds no failing row to the fixed model's (HOME and CAMPUS never regress) |
| C7 | when places new since tonight exist: the frozen rule finds at least as many barrels there as fixed, with at most 1 more false box; none: not applicable |

A pass is **proposed, not adopted**: it goes to Tanush with a walkthrough; the default changes only on his word.
A fail says which clause failed. Either way the run also prints, per threshold, whether its line beats the
fixed value at LOPO (mean |error| over places, and in how many places), which is what would justify keeping or
dropping each of the three terms in a later, newly registered rule.

## What would make me distrust a pass

A gain carried by one place; a slope whose sign flips between LOPO folds; a gain that comes from the ottoman
only (one room, one lamp); mixed-light conditions sitting off the line; the frozen rule failing on the new
places while the re-fit one passes (then the rule only works when it has seen the place).

## Outputs

`results/2026-11-24_adaptive/`: `summary.md` (one page, plain English), `analysis.md` (part A in full),
`detection.csv`, `per_condition.csv`, `rule.json` (the rule fit on all places tonight / tomorrow),
`model_adaptive.json`, `gate.txt`, `config.json`; every run copied to `runs/<nn>_<date>_<git>/`.
