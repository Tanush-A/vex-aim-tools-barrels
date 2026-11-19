# Pre-registration: a stencil-matching detector as a second opinion

Written 2026-11-19/20 on branch `wip/stencil` (from `wip/detector-occl`, git 085c99d), **before the calibration was
run and before the scorecard, the CAMPUS frames or the recordings were looked at with this method**. What had been
run when this was written: the stencil code with guessed numbers (accept 0.30, absent cost 0.25, outside cost 0.5,
no row correction) on the 16 HOME hand masks, to see that it runs (27 of 29 found, no false box, 100 ms per pass),
and the shape fit (`fit_stencil.py`). Nothing else.

## What was asked

The rule detector finds 2417 of the 3888 scenes of the occlusion scorecard, and every new case has needed a new
rule. Question: does ONE idea, a stencil of the barrel scored against the class mask, cover the occlusion cases
without their special rules and without false boxes? It is a second opinion. `detector.py` is not touched and
nothing becomes the default on this branch.

## The method (fixed now; `src/barrels/stencil.py`)

1. **Stencils.** One per barrel size, 5 % apart, from 16 px wide (60 cm) to 420 px (touching the bumper). The camera
   model gives the rows of a barrel of that size (top, stripe top, stripe bottom, bottom); the top and bottom rows
   get a small correction fit on the HOME hand masks. A stencil has three bands (upper body, stripe, lower body),
   rounded corners (the outer columns have shorter body bands), a seam at every band edge that is not looked at,
   and a ring just outside the outline.
2. **Every place.** Each stencil is slid along its rows, one column at a time, and also a few rows up and down
   (8 % of its width, because the model's rows are a few px off), once as an orange barrel and once as a blue one.
3. **One score per place**, column by column of the stencil:
   - a column is worth its worst band: q = the smallest, over its bands, of (pixels painted the predicted color /
     pixels of the band). A column shows the whole pattern or it does not count;
   - a band known to be hidden is not asked for: outside the frame, or inside the box of an accepted barrel that
     stands nearer. The column then counts for the checked bands only (stripe half the weight, each body part a
     quarter);
   - `seen` = mean of weight x q; `missing` = mean of weight x (1 - q); `outside` = the share of the ring painted
     as if the barrel went on;
   - **score = seen - absent_cost x missing - outside_cost x outside.**
4. **Accept** a place when score >= `accept`. Best first; an accepted box is claimed: its pixels are evidence for
   no other place, and hidden (not missing) for places further away. Scores are computed again; repeat until
   nothing reaches `accept`. Columns that fit within 0.02 of the best are "equally good": the box goes in their middle.

What follows from the design, stated before measuring:

- A thing that is not a barrel and hides a barrel is unpainted, like the table. The mask cannot tell hidden from
  absent. So a barrel hidden by such a thing, showing the share v of its width, scores about
  v - absent_cost x (1 - v), and is found only if that reaches `accept`. **`accept` is the tolerance for
  unexplained absence, and it is where false boxes come from.** With accept T and absent cost m the smallest share
  that passes is (T + m) / (1 + m).
- Hidden from above or below by a non-barrel thing by half or more: no column shows the whole pattern, the score
  is near 0. Not found, by design: a stripe with body on one side only is not told apart from clutter in the mask.
- A barrel with its stripe outside the frame or behind an accepted barrel can score at most the body's weight
  (0.25 for a full upper body). Whether such barrels pass depends on where `accept` lands.

## The stencil's shape: fit on the HOME hand masks (`fit_stencil.py` -> `results/2026-11-20_stencil/fit.md`)

12 barrels (no flag, box overlapping no other box). Rules, fixed before the numbers:

- `top_fit`, `bottom_fit` (px added to the model's top / bottom row, as a + b x width): the straight line if,
  leaving one scene out at a time, it predicts the left-out barrels better than the median by more than 10 %; else
  the median.
- `seam` = (1 - 10th percentile of [stripe height in the mask / model]) / 2.
- `rim`, `rim_top`, `rim_bottom`: read off the mean barrel (cells under half painted), as written in the script.
- The model's width is used as it is. `halo` 0.10 of the width, `stripe_weight` 0.5, `min_checked` 0.5, the
  5 % size step and the 8 % / 2 % row search are chosen, not fit, and are not tuned.

## The three score numbers: calibration (`calibrate.py` -> `calibration.md`)

Masks used (HOME train frames and negative frames only; no CAMPUS frame, no scorecard scene, no recording):

- **A1** the 16 HOME hand masks; **A2** the same frames segmented by the color model, leave one scene out (as in
  the eval table); **A3** the hand masks with `light` damage, seeds 10 to 14 (not the seeds 0 to 4 the reported
  level uses); **A4** the train negative frames of the other tables (9 wood `neg_02` with orange and blue clutter,
  1 black `neg_01`), adopted color model. HOME's own two negatives are in A1 / A2.
- **B** the hand masks with `medium` damage, seeds 10 to 14.

Grid: absent_cost in {0.1, 0.25, 0.5} x outside_cost in {0.25, 0.5, 1.0}. Each pair is run once with accept 0.10
and every box is stored with its score; "the boxes at T" = the stored boxes with score >= T.

1. For each pair: **T0 = the smallest T (steps of 0.01) at which there is no false box in A1 to A4** (a box that is
   not right under the v2 rule; any box on a negative frame) **and no more false boxes in B than the rule detector
   draws on the same masks.**
2. **accept = T0 + 0.05** (the margin).
3. **The pair chosen: the most barrels found (v2) in A1 + A2 + A3 + B at its accept.** Ties: lower accept, then
   lower absent_cost, then lower outside_cost.
4. One direct run with the chosen numbers (the stored boxes are an approximation: with a higher accept fewer boxes
   are claimed). If it shows a false box in A1 to A4, accept goes up by 0.01 until it does not; this is reported.
5. Reported with it: leaving one HOME scene out at a time, T0 from the other scenes, and the false boxes and found
   barrels on the left-out scene (does the tolerance transfer); and what the margin and T0 cost: barrels found at
   0.10, at T0 and at accept, and the smallest visible share that passes.

## Combinations (fixed now)

- `rules`: `detector.detect`, today's default on this branch (edge_check and cap_same on).
- `stencil`: `stencil.detect` alone.
- `union`: the rule detector's boxes, plus the boxes the stencil finds when the rule boxes are given to it as
  already accepted (claimed, and hiding what stands behind them). Same `accept`.
- `veto`: the rule detector's boxes whose stencil score at their place (`box_score`: best place overlapping the box
  by half or more) is at least `veto`. **veto = (the lowest such score among the rule boxes that are right in A1,
  A2, A3) - 0.05.** No right box of the calibration masks is lost by construction; the question is what it removes
  elsewhere.
- `veto+union`: `veto`, then the stencil's additions with the kept boxes given.

"The best combined" = among `union`, `veto`, `veto+union`: the one that passes rules 1 to 3 below with the most
scorecard scenes found; ties: fewer boxes where no barrel is; if none passes, the one that fails least, named as failing.

## What is measured, and the rule

For `rules`, `stencil`, and the combined arms:

1. **Never regress** (the eval table, `report.py` machinery): no scenario row of HOME (leave one scene out) or
   CAMPUS loses a found barrel or gains a false box against `rules` (HOME 28 / 1 / 0, CAMPUS 35 / 0 / 0); no box on
   any negative frame of any set. BLACK, wood and Dave's rows are report only.
2. **The levels** (harness of `2026-11-18_det_given_seg`): perfect HOME masks, light / medium / heavy damage (seeds
   0 to 4), CAMPUS, BLACK with label thresholds: found and false, against `rules`.
3. **Recordings**: every box that differs from `rules` on the campus clips is looked at on a sheet; no new box on
   something that is not a barrel or half off its barrel; a box that disappears must have been wrong. Black and
   wood clips are described.
4. **The scorecard**: all 15 rows x 3 amounts, right place, boxes where no barrel is, too small / right / too big.
5. **Time per frame** on the HOME and CAMPUS train frames.

An arm **passes the project's rule** when 1 and 3 hold. 2 and 4 are reported in full and compared; the verdict
says where each arm is better and worse than `rules`. If the stencil is clearly worse, that is the result.

At most two rounds. If round 1 shows a mistake in the method, a dated addendum goes below this line before any
corrected code, and the corrected run is round 2; no third round. No threshold is re-picked after the scorecard
or the CAMPUS numbers are seen, except through such an addendum, with the reason. Test frames are never opened.

## Not built

- Reading the gray or color image to see a non-barrel occluder (so that "hidden" could be told from "absent").
  If the numbers say this is the missing piece, it is reported as a lead with the evidence.
- Anything over several frames. Any change to the camera constants or to the color model.
