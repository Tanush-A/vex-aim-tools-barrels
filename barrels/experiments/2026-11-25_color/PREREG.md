# Pre-registration: the color step across the ordinary conditions (2026-11-25 experiment)

Written 2026-11-25 (machine date 2026-11-23), **before `test.py` existed and before any candidate below was run
leave-one-place-out**. Committed on `wip/color` before the test. Nothing is adopted by this experiment: the default
model stays `eb863d84` (`worldmap_bridge.DEFAULT_MODEL` is not touched); a passing candidate is proposed as a model
file, and the switch is Tanush's call after the walkthrough.

## What was looked at before this was written (honesty)

All on TRAIN frames only (no test frame was opened, scored or listed):
- `gates.md` (step 1): which barrel pixels no slider setting can paint. Warm lamp on the bathroom floor: the blue paint
  reads gray-olive (hue 26-44, S 44), blocked by the slider's hue limit; the dark ottoman: the V gate blocks 8-27 % of
  its blue; the horizon row and the tie rule block nothing on free-standing barrels.
- `sweep.md`, `relation.md` (step 2, step 3 part 1): one-at-a-time working ranges around Tanush's 45 slider labels,
  the joint check, the non-monotone cases; no constant inside every place's range; no histogram feature predicts the
  ranges convincingly leave one place out.
- **Exploration on all ordinary train frames, in-sample** (`explore.py`, `grid.py`, `diff.py`, renders): fixed
  211 of 307 found, 13 false, 2 boxes on empty frames; orange hysteresis (+20 found but +8 false, and drops on pale
  wood, cool glass, cool bathroom); per-frame orange peak placement (fails: the peak is the bathroom floor or the
  clutter, 0 of 32 on the ABP white table); orange constants (best ones 1..15-16, S >= 160: +17 to +20 found, empty
  frames 2 -> 0, but bumpy: neighbouring grid points drop pale wood or glass); the blue floor following the light's
  warmth (white patch, ramp 0.10 -> 0.25 to S 40 and hue 92: +21 found, +5 false, no condition down, a flat plateau
  over its parameters); orange constant plus warm blue (about 251-254 found, 23-28 false, 0 on empty frames,
  in-sample). These in-sample numbers chose the candidate FAMILIES below; the leave-one-place-out test is what guards
  against having chosen on the same frames. The parameter values themselves are chosen inside each fold by the rule
  below, never by hand.

## Data

Every TRAIN frame with a box label in the **ordinary** conditions, 8 places (place = table and room,
`data/conditions.json`): home white table (`window_light`, 16 frames), campus study room (`campus_light`, 21), ABP gray
(`both_abpgray`, 8), ABP white occlusion set (`window_abpwhite`, 17), UC pale wood (`overheaddim_palewood`, 7), home
ottoman (`lamp{cool6,mid6,warm6}_ottoman`, 21), home glass (`lamp{warm6,mid6,cool6,mid3}_glass`, `window_glass`, 36),
home bathroom tile (`lamp{warm6,mid6,cool6,mid3}_bathtile`, 28): 154 frames, 307 barrels. Report-only (extreme):
`lampmid3_ottoman`, `window_black`, the wood lamp ladder. Excluded: lamp brightness 1. Test frames are refused before
any image is read (`common.load`).

Scoring: today's detector (`DetConfig()`), camera `AIM_4A8B6118_BOXFIT`, the v2 rule against the hand boxes
(`eval_det.evaluate_frame`), the condition score = `report.summarize(...).score` (mean of the orange and blue F1). Every
candidate is run through `pipeline.segment` with a `pipeline.Model` (no second implementation). Home is scored with
the candidate applied as it is (the adopted model is the "fixed" arm there too); the never-regress gate (A4) adds the
home leave-one-scene-out protocol.

## The candidates (three families, each a set of settings; the setting is chosen inside each fold)

- **C1, a re-centred constant.** The six numbers, the same for every frame: orange hue low in {0, 1, 2, 3}, hue high in
  {13, 14, 15, 16, 17}, S floor in {140, 150, 160, 170}; blue hue low in {100, 103}, blue hue high 119, blue S floor in
  {100, 113, 125} (480 settings; the adopted values are one of them).
- **C2, the blue box follows the light** (`pipeline.Config.hs_light`, `lightcolor.py`). Orange as adopted. Per frame,
  the light's warmth w = median (R - B) / (R + G + B + 1) of the brightest 5 % of the frame's pixels; the blue S floor
  and the blue hue low end move from 113 / 103 toward s_warm / h_warm by the share clip((w - w0) / (w1 - w0), 0, 1); only
  ever lowered. Grid: w0 in {0.06, 0.08, 0.10, 0.12}, w1 in {0.20, 0.25, 0.30}, s_warm in {30, 40, 50}, h_warm in {92, 98}
  (72 settings).
- **C3, both.** Orange from C1's orange grid (80), blue constants adopted, plus the light rule with w0 in {0.08, 0.10},
  w1 in {0.22, 0.25}, s_warm 40, h_warm 92 (320 settings).

Not candidates (looked at, not taken): orange hysteresis, per-frame orange peak placement, a V gate that adapts (the
sweep shows no ordinary frame that needs a V gate other than 40), a line on a histogram feature (step 3 part 1: none
predicts the ranges).

## The selection rule (inside each fold; on the training places only)

For a family and a set of training places:
1. A setting is **eligible** when, on the training places: no training condition's score is more than 0.02 below the
   fixed model's; and it puts no box on an empty frame where the fixed model puts none, and not more boxes on empty
   frames in total than the fixed model.
2. Among the eligible settings, take the one with the highest **J = sum over the training places of
   (found - 2 x false) / barrels** of that place (every place weighted the same).
3. Ties (equal J): the setting closest to the adopted values (sum of |difference|, hue units x 1, S units x 0.1, and
   +1 when the light rule is on), then the first in grid order.
4. No eligible setting: the fixed model.

**Leave one place out:** for each of the 8 places, the rule is applied on the other 7 and the chosen setting is scored
on the held-out place's frames. **The final model** of a family: the rule applied on all 8 places.

**Choice among the families:** the family whose leave-one-place-out result passes A1-A3 with the highest total
held-out J; ties to the simpler (C1, then C2, then C3). If none passes, the one with the highest held-out J is
reported as "best, not passing", and nothing is proposed.

## Acceptance (the chosen family, leave-one-place-out numbers against the fixed model on the same frames)

- **A1** (better across the ordinary conditions): summed over the ordinary conditions, (found - 2 x false) improves by
  at least 20 (about 6.5 % of the 307 barrels); per place, (found - 2 x false) improves in at least 4 of the 8 places
  and drops in none.
- **A2** (empty frames): no box on an empty frame where the fixed model has none; the total on empty frames not above
  the fixed model's.
- **A3** (no condition gets worse): no ordinary condition's score drops by more than 0.02. No exception.
- **A4** (never regress home / campus), on the final model: `python barrels/tools/report.py --gate --cand-model
  <model>` passes; and home and campus scored with the model as it is lose no barrel and gain no false box against the
  fixed model.
- Extreme sets: printed, not judged.

A pass is proposed, not adopted. A fail is reported as a fail; a second round is allowed only after a dated addendum
below, and at most two rounds in all.

## What would make me distrust a pass

A gain carried by one place (printed per place); a chosen setting that changes from fold to fold a lot (printed per
fold); a pass that rests on the bottom-edge tolerance (the per-barrel lists are written); the light rule moving the blue
box on frames whose light is plainly white (the warmth per condition is printed).

## Outputs

`results/2026-11-25_color/test/`: `summary.md` (per condition fixed vs each family leave-one-place-out; per place; the
acceptance clauses; the chosen settings per fold), `per_frame.csv`, `chosen.json`; the final model file
`results/2026-11-25_color/config.json` when a family passes (else `config_best_not_passing.json`), `gate.txt`.

## Addendum, round 2 (dated 2026-11-25, written after round 1 and before round 2 ran)

**Round 1 (results in `results/2026-11-25_color/test_round1/`): no family passes.** C1 +5 net (the ottoman's orange
shift is not learnable from the other places); C2 +22 found but +6 false, a new box on `lampmid6_glass_neg_02`, and
`lampmid6_glass` -0.023, better in 2 of 8 places; C3 -1 net.

**What was wrong with C2, found by reading the warmth per frame (no further look at scores):** the white patch was
taken from the whole frame, so wherever an orange barrel is among the brightest things in view (a close-up; a barrel
on the black ottoman) or yellow clutter is, the "light" reads warm under white light: `lampcool6_bathtile close_01`
0.50, `lampcool6_ottoman core_01` 0.40, `lampmid6_glass close_01` 0.18, `neg_02` 0.08. The light estimate was
contaminated by the very objects it is meant to help find.

**The one change for round 2:** the light's warmth is read from the rows ABOVE the horizon gate (rows 0-49), where no
barrel can ever be (the band v1 used for its background prior), as the median (R - B) / (R + G + B + 1) of the brightest
20 % of those rows' pixels. Within a condition this reads 0.18-0.23 (bathroom mid), 0.13-0.17 (ottoman mid 6), 0.33-0.35
(bathroom warm), at most 0.07 on every white-light condition except the empty `lampwarm6_glass neg_02` (0.13).
`Config.hs_light` takes it as two more numbers, (w0, w1, s_warm, h_warm, rows, top) = (..., 50, 20); the four-number
form keeps round 1's whole-frame 5 % reading.

**Round 2 families:** C2b = C2's grid with the band reading; C3b = C3's grid with the band reading. C1 is not re-run
(its round-1 result stands). Same selection rule, same acceptance A1-A4 (unchanged, although A1's "better in 4 of 8
places" is hard for a rule that by design changes nothing under white light: stated now, not relaxed), same choice
among the families, C1 entering with its round-1 numbers. This is the last round.
