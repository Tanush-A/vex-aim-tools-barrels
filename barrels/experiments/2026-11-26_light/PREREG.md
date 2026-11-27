# Pre-registration: what the light can be read from, and whether a threshold that follows it passes (2026-11-26)

Written 2026-11-26 on branch `wip/exp-light`, **after the in-sample exploration listed below and before any candidate
was run leave one place out or through the judge**. Committed before `run.py` was first run. TODO items C3 and the
light part of E6. Nothing here changes what runs by default: `detector.py` is not touched, the default color model and
`Config.hs_light` stay as they are, and the new module `src/barrels/lightread.py` is imported by nothing in the package.

## The question

1. What in one frame can the color of the light be read from, without knowing where a barrel is?
2. If the blue thresholds follow that reading, does the detector get better by more than the noise, judged on places
   the numbers were not chosen on?
3. Does any reading predict the orange hue the ottoman needs without painting the bathroom floor?

## What was looked at before this was written (honesty)

Train frames only. No test frame was loaded, viewed, scored or listed.

- **Docs and earlier results:** `docs/EVAL.md` (the standard pass rule and its sanity checks, including "blue follows
  the light" at +5.9 placements, PASS, weak, and +3.2 for the reading above the gate), `review-2026-11-26/` (REVIEW,
  adaptive_forensic, color_physics), `experiments/2026-11-25_color/` (PREREG, rules, features, test),
  `results/2026-11-26_judge/summary.md` and `chosen.json` (the settings that experiment's folds picked: mostly w0 0.08,
  w1 0.2, S to 40, hue low to 92).
- **Part A, the readings** (`measure.py`, `table.py`; `results/2026-11-26_light/readings.md`): thirteen readings on all
  154 ordinary and 77 extreme train frames next to the labelled paint. In-sample correlations, and a leave-one-place-out
  LINE fit of the paint's S and hue on each reading (a statistic, not a detector run). What it showed: `without_loose`
  r -0.96 with the blue paint's S, line-fit skill 0.89, spread between conditions 12.5 times the spread inside one, the
  warm-needing frames apart from all others (AUC 1.000); `above_gate20` -0.96, 0.83, 6.7, AUC 1.000; `whole_frame`
  -0.95, 0.70, 2.1, AUC 0.979 (three other frames as warm as the needing ones; a close orange barrel moves it by up to
  0.42); `neutral` fails (r -0.35: under a yellow lamp nothing white is under a fixed S limit); `highlights` speaks on
  116 of 154 frames and reads orange lids; `near_strip` and `gray_world` read the table's own color (pale wood 0.21 and
  0.18 under neutral light). No reading predicts the orange hue (line-fit skill between -1.07 and +0.10).
- **Pictures** (`look_readings.py`): three sheets, 18 frames, of the pixels each reading reads.
- **Blue rules at pixel level** (`explore_blue.py`, in-sample, no detector): the share of the labelled blue paint and of
  the background that fixed boxes, lowered boxes and "bluer than the light" rules paint, per condition. What it showed:
  under the warm bathroom lamp no blue hue range reaches the paint (hue 92..119 with S >= 30 paints 3 % of it), "bluer
  than the light by 0.20" paints 96 % with 0.27 % of the background; on the dark ottoman the same rule paints 9 % of the
  background (the black lid is neutral, so it is "bluer than the light"), and comparing with the lower of the light and
  the scene brings that to 0.67 %. A local-surround version (a 151 px window) did about the same and was not taken
  (one more number).
- **Orange at pixel level** (`explore_orange.py`, in-sample): the orange paint's hue per condition next to the readings,
  the darkness of the scene and the share of the frame in the band the ottoman needs; and what orange ranges up to hue
  16, 19, 22 paint. What it showed: the ottoman needs hue up to 19..22 (painted 16-36 % by the fixed range, 86-96 % at
  19..22); the same ranges paint 4-96 % of the bathroom background under the mid and warm lamp; the scene's darkness
  separates the ottoman (median brightness 31-37 below the gate) from every other ordinary place (141-204), which is one
  place against seven.
- **A smoke test of the rule code through the detector** (`look_rules.py`, in-sample): 12 frames (6 bathroom, 4
  ottoman, 2 empty glass) with four hand-picked settings (fixed; ramp 0.08 / 0.20 / 40 / 92 on `without_loose`; the
  same plus bluer-than-the-light by 0.20 and by 0.30). Printed found and extra boxes per frame, and two sheets of masks
  and boxes. What it showed: warm bathroom `core_01` 0 of 4 found by the fixed model and by the ramp, 3 of 4 with the
  relative rule; `lampwarm6_bathtile_neg_02` (empty, with clutter) gets 2 boxes at 0.20 and none at 0.30; mid 6
  `core_01` 0 -> 4 of 4 with the ramp alone; warm ottoman `core_01` 0 -> 2 of 4; the two empty glass frames read
  0.03 and -0.01 and nothing changes on them.
- **Not seen:** any candidate of this plan run on all frames; any leave-one-place-out detector result; any verdict.
  The grids below were written without a run of them.

## Data

The ordinary train conditions: 154 frames, 17 conditions, 8 places, 172 placements (`data/conditions.json`,
`judge.train_frames`). Extreme conditions are run and printed by the judge, never judged. Only two places have warm
light (the bathroom floor, the ottoman).

## Part A: how the readings are compared, and which one part B uses

Already measured (above); the table is `results/2026-11-26_light/readings.md` and is reported as it is: in-sample
unless a column says leave one place out. The reading for part B was picked by this criterion, before any detector
run: the highest leave-one-place-out line-fit skill for the blue paint's S among the readings that (a) speak on every
frame, (b) keep every warm-needing frame apart from the others (no other frame as warm as the 10th percentile of the
needing ones) and (c) move by at most 0.05 on a close-up. That is `without_loose` (skill 0.89): the brightest 5 % of the
frame after taking out, with a 15 px margin, everything barrel-like under a loose model (orange hue -10..25 with
S >= 120, blue hue 90..125 with S >= 60, below the gate). Its loose model's numbers were written once and not tuned.
`without_barrels` and `max_rgb` have skill 0.90 and fail (c) or (b). The second reading is `above_gate20` (Tanush's
question about the rows above the horizon); the reference is `whole_frame` (the reading of 2026-11-25).

## The candidates (families of settings; code: `rules.py`, `candidates.py`)

**Blue follows the light.** The light's warmth w is read by the family's reading. The share t = clip((w - w0) /
(w1 - w0), 0, 1). The blue S floor goes from 113 toward `s_warm` and the low end of the blue hue range from 103 toward
`h_warm` by t. Orange and the pixels are untouched. One grid for every reading: w0 in {0.05, 0.08, 0.11}, w1 in
{0.18, 0.24, 0.30}, s_warm in {30, 45, 60}, h_warm in {88, 96}: 54 settings.

- **B1** (primary): reading `without_loose`.
- **B2**: reading `above_gate20`. The same grid and the same rule of choice, so B1, B2 and B3 differ in the reading only
  (the comparison of 2026-11-25 also changed a parameter).
- **B3**: reading `whole_frame`.
- **B4** = B1's 54 settings plus each of them with **"bluer than the light"**: where the light reads warm (w > w0), a
  pixel the moved boxes left unpainted, with S under the adopted floor (113), is also blue when its own warmth
  (R - B) / (R + G + B + 1) is at least `delta` below the lower of the light's warmth and the scene's warmth below the
  gate. delta in {0.30, 0.25, 0.20, 0.15}: 54 + 216 = 270 settings. This is the test of "reaching the gray-olive blue
  needs more than the two numbers". Note for Tanush and Dave: no pixel is changed, but comparing a pixel with the
  light's color is the same arithmetic as correcting the pixel and then thresholding it. Whether that is inside the
  "no image correction" rule is their call; it is flagged in the entry either way.

**Orange** (part C). The high end of the orange hue range goes from 13 toward `o_hi` in {16, 19, 22}.

- **O1**, it follows the light (`without_loose`): from warmth x0 to x1 in {(0.10, 0.25), (0.05, 0.20), (0.0, 0.15)}: 9
  settings. The direct test of "does a light reading predict the orange hue".
- **O2**, it follows the scene's darkness (median brightness below the gate): from x0 down to x1 in {(60, 40), (90, 45),
  (120, 60)}: 9 settings.
- **O3**, wide everywhere, with a flood guard: the range is widened on every frame unless the pixels it would add are
  more than `guard` of the gated frame, guard in {0.02, 0.05, 0.10, 0.20}: 12 settings. Barrels cover a few percent
  of a frame; a band that holds more is the table.

Not candidates: the other ten readings as detector inputs (compared in part A only); the local-surround version of
the relative rule; an orange S floor that moves; blue and orange together (TODO E8, after the single ideas).

## How every number is chosen (inside each fold, never on the place it is judged on)

The same rule for every family (`candidates.choose`):

1. Every setting and the fixed model are run on every training frame: the color step, today's detector
   (`DetConfig()`), the judge's counting (`counting.classify_frame`).
2. A setting is *allowed* when the standard pass rule (`judge.decide`, the stored margins) does not call it FAIL
   against the fixed model on the training places.
3. Among the allowed settings: the highest gain, where gain = (found, per placement) minus (boxes that are not on
   their barrel, per arrangement), each as the difference from the fixed model on the training places.
4. A tie goes to the first setting in the family's order, the most cautious first (blue: higher w0, then higher w1,
   higher s_warm, higher h_warm, no relative rule before a larger delta before a smaller one; orange: lower o_hi, then
   a smaller guard, then a later start). No allowed setting with a gain above zero: the fixed model.

**Leave one place out** is the judge's (`judge.leave_one_place_out`): for each of the 8 places the rule runs on the
frames of the other 7 and the picked setting is run on the held-out place only. Also printed, **in-sample and never a
verdict**: the setting the rule picks on all 8 places.

## What counts as success

The only pass rule is the standard judge (`docs/EVAL.md`, "The standard pass rule"), on held-out results: PASS, FAIL
or NO CLEAR DIFFERENCE. A PASS with found up by less than 6.0 placements (2 above the gain margin of 4.0) is reported
as WEAK.

- **Question 2 is answered by B1.** B2 and B3 are the comparison of readings; B4 is the test of the extra rule. Seven
  candidates are judged; one of 12 changes that mean nothing passed this rule, so a single PASS near the margin among
  seven is weak evidence and is said to be.
- **Question 3 is answered "no" unless** O1 passes, or O1 gains at the ottoman without losing at the bathroom.
- Reported for every candidate, pass or fail: found per placement and per frame, boxes not on their barrel, boxes on
  clean empty frames and on empty frames with clutter, every place, every barrel gained and lost, the setting each fold
  picked. **Traps reported by name:** the clean empty frames; the empty frames with clutter (the bathroom's and the
  ottoman's `neg_02` above all); warm-lit white objects (`lampwarm6_glass_neg_02` and `lampmid6_glass_neg_02`, where
  the 2026-11-25 rounds drew a box); the glass table's reflections (found and boxes at `home_glass`).
- Contact sheets of every gained barrel, every lost barrel and every new box that is not on its barrel are made and
  looked at before the entry is written.

## What I expect (written before the run)

- B1: a gain of the size of 2026-11-25 (+4 to +8 placements), nearly all at the bathroom, a little at the ottoman
  (orange limits it there); nothing moves at the six places without warm light, because the reading is under w0 there.
- B2 about the same as B1; B3 lower or with more boxes (close-ups read warm).
- B4: more at the bathroom under the warm lamp than B1, and new boxes on the bathroom's cluttered empty frames.
- O1: no gain, or a loss at the bathroom. O2: **no change at all, by construction**: with the ottoman held out no
  training frame is dark, so nothing can be learned; with any other place held out the rule never acts there. It is run
  to show that, not to test it. O3: no gain at the ottoman for the same reason (the other seven places do not ask for
  a wider orange), possibly new boxes elsewhere.

## What this cannot show

Only two places have warm light. Leave one place out therefore fits the warm end of every ramp on ONE place and tests
it on the other. A pass says "what the bathroom teaches works on the ottoman and the other way round", not "it works
under warm light in general". A warm-colored wall or table in daylight is not in the data, and neither is a second
dark surface. In-sample numbers are marked as such and are never the verdict.

## What would make me distrust a pass

A gain carried by one place (printed per place). A setting that changes a lot from fold to fold (printed). A gain
that rests on the bottom-edge tolerance (the per-barrel lists). The light rule acting on a frame whose light is plainly
white (the reading per frame is in `per_frame.csv`; any place without warm light that moves is named).

## Rounds

One round. A second round needs a dated addendum here, committed before it runs, and at most two rounds in all.

## Outputs

`results/2026-11-26_light/`: `readings.md`, `readings.json`, `per_frame.csv` (part A); `explore_blue_without_loose.md`,
`explore_orange.md` (the exploration); `summary.md`, `chosen.json`, `judge_<family>/` (`judge.md`, `judge.json`,
`changes.csv`) for each judged candidate; `sheets/` (images, not committed). `ENTRY.md` in this folder: the
experiment-log entry.
