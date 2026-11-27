# Pre-registration: "bluer than the light", with the false boxes taken away by geometry (2026-11-27)

Written 2026-11-27 on branch `wip/exp-bluer-geom`, **after part A (the reproduction) and part B (the measurements,
in-sample) and before any candidate below was judged**. Committed before `run.py` and `run_contrast.py` are first
run. Nothing that runs by default changes: `detector.py` is not touched. The checks are a post-filter inside the
experiment's own callable (`checks.py`); `stages.found` is the ten lines of `detector.detect` with the `Found` objects
kept, and it draws the same boxes on every input of the proof harness (`check_same.py`, below).

## The question

Yesterday's light experiment (branch `wip/exp-light`) found that "bluer than the light" (B4) paints the warm
bathroom's gray-olive blue: 145.72 placements held out (+11.92), 46 barrels gained, none lost. It failed only on boxes
not on their barrel (1.93 -> 6.68) and on cluttered empty frames (1.25 per arrangement). The owner's view (Tanush,
2026-11-27): the segmentation is better on the barrels; things colored like a barrel can be told apart only by the
detector's geometry; the clutter was put there on purpose as near-barrel traps. So:

1. Which geometry tells B4's false boxes from real barrels, measured box by box?
2. With checks built on that, does B4 pass the standard rule, leave one place out?
3. Do the same checks cost real barrels with the fixed colors, and do they help the contrast winner too?
4. Where does the best trade sit among the less aggressive margins (delta 0.30 / 0.25 / 0.20 / 0.15)?

## What was looked at before this was written (honesty)

Train frames only. No test frame was loaded, viewed, scored or listed.

- **Part A, the reproduction** (`repro.py`, `results/2026-11-27_bluer_geom/judge_A_B4_repro/`, `repro.json`). The
  light experiment's B4 fit run leave one place out on this branch (the collapsed detector), with a fresh cache:
  133.8 -> **145.72** placements, 211 -> **257** per frame, boxes not on their barrel 1.93 -> 6.68, FAIL. The same as
  `results/2026-11-26_light/chosen.json`, number for number, with the same setting picked in every fold (delta 0.25,
  ramp 0.08 -> 0.18, S to 30, hue low to 96; with the bathroom held out: delta 0.15, ramp 0.11 -> 0.30, S to 60).
- **Part B, the measurements** (`measure.py`, `analyze.py`, `stages.measure`; `results/.../boxes.csv`,
  `false_boxes.md`). Every box B4 draws on the 154 ordinary frames, each place under its own fold's setting: 283
  boxes, 259 on a real barrel (found or box off), **24 not on their barrel**. Measured: width and height over the
  row's W and H, the widest seen run over W, fill, body fill, the seen top and bottom against the row's, stripe height
  over the row's stripe height, stripe over body, the body bands above and below and their likeness, the bulge (width
  at the upper and lower quarter over the width at the stripe), aspect, the stripe's width over W, barrel color in a
  ring around the box, and the solidity of the paint. The same for the fixed colors (218 boxes, 5 not on a barrel).
- **Contact sheets, looked at** (`sheets.py`; `results/.../sheets/false_01.png`, `real_01..06.png`): all 24 false
  boxes and all 259 real barrels. What they show: 12 of the 24 sit on the **red jar with the teal label and the gold
  lid** (bathroom mid 3, mid 6, warm 6; and two on the glass table next to a real barrel, also drawn by the fixed
  colors); 4 on the **blue tin** ("Vaseline"; warm 6); 2 on the **small figure** (warm 6); the rest are a cap over a
  real barrel (second box), two wrong-colored boxes on real barrels (bathroom warm clutter, warm ottoman touch), one
  box beside a real barrel (warm core), and the pale wood close-up box that the fixed colors draw too.
- **What separated, in-sample** (all eight places, never a verdict):
  - *Solidity* (of the barrel-colored pixels in the box, the share whose 3 x 3 neighbourhood is all barrel color). Real
    barrels: lowest 0.40, 0.47, 0.48. False boxes: 14 of 24 under 0.40 (the tin 0.19-0.39, the figure 0.18-0.20, the jar
    under the warm lamp 0.28-0.39). Under 0.30: 7 false, 0 real; under 0.35: 10 false, 0 real; under 0.40: 14 false,
    1 real (`lampcool6_bathtile_clutter_01`, 0.399). Fixed colors: under 0.35 removes 1 false (the pale wood close-up),
    0 real.
  - *Stripe taller than the row's stripe, and thin body*. The jar's label reads 1.27-1.65 x the row's stripe height,
    with body fill 0.14-0.53. Real barrels over 1.2 x: nine, eight of them with body fill 0.72-0.80 (glass-table
    reflections and close bathroom barrels) and one on the dark ottoman (`lampmid6_ottoman_core_01`, 1.29 x, body fill
    0.23). Stripe over 1.35 x and body fill under 0.6: 7 false, 0 real; over 1.25 x and under 0.6: 11 false, 1 real
    (that ottoman barrel). Fixed colors: 3 false (the glass-table jar), 0 real.
  - *What did not separate*: width and height for the row (the jar is boxed at the 1.2 W cap, but so are real
    barrels), the seen top and bottom, the bulge (real barrels 5 %-95 %: 0.21-1.93 at the top; the mask is too ragged
    to read a curve), aspect, the bands' likeness, the ring around the box (real barrels in a row of touching barrels
    have both sides colored). Each was looked at and none is a candidate.
- **A smoke test** of the table code on two frames (`lampwarm6_bathtile_neg_02`, `campus_light_core_01`): it runs,
  and how many distinct counts it gives. No count was read.
- **Not seen**: any candidate below run leave one place out; any verdict; the contrast path with the checks on any frame.

## The checks (code: `checks.py`; each removes a measured kind of false box)

- **K1, speckle**: a box whose barrel-colored pixels are under `solid_min` solid is removed. A barrel's paint is one
  solid shape; the tin, the figure and the jar under the warm lamp are speckle. Grid: off, 0.30, 0.35, 0.40.
- **K2, a label, not a stripe**: a box whose stripe is taller than `label_sh` x the stripe its row predicts AND
  whose body color outside the stripe's rows is under `label_bf` of the box is removed. The jar's teal label is taller
  than a barrel's stripe and the jar around it is thin in body color. A box with no stripe is not asked. Grid
  (`label_sh`, `label_bf`): off, (1.5, 0.45), (1.5, 0.6), (1.35, 0.45), (1.35, 0.6), (1.25, 0.45), (1.25, 0.6).
- Together: 4 x 7 = 28 sets of checks, `checks.GRID`. Both apply to every box (fixed-color boxes too): a check is a
  property of the detector, not of the color step.
- Said plainly: the grid values were read off the in-sample table above (all eight places). The folds choose which
  checks are on and at which grid value, not the grid.

## The candidates (code: `fitgeo.py`, `run.py`, `run_contrast.py`)

A member = (a color step of the light experiment, a set of checks). Families list the color step outer and the
checks inner, each from the most cautious (for the checks: off first, then the milder value first).

| name | color steps | checks | role |
|---|---|---|---|
| **G1** | B4's 270 (54 ramps; each also with delta 0.30, 0.25, 0.20, 0.15) | the 28 | **primary**: question 2 |
| G1a | B4's 270 | K1 only (4) | which check does what |
| G1b | B4's 270 | K2 only (7) | which check does what |
| **G2** | the fixed colors | the 28 | question 3: do the checks cost real barrels? |
| **G3** | C1 of the contrast experiment, the setting its own fold picked for that place (`results/2026-11-26_contrast/chosen.json`) | the 28 | question 3: do they help another color step? |
| D0.30 ... D0.15, with checks | the 54 ramps with that delta | the 28 | question 4 |
| D0.30 ... D0.15, no checks | the 54 ramps with that delta | none | question 4, the reference |
| B4 (no checks) | B4's 270 | none | the reproduction through this code; the reference for G1 |
| C1 (no checks) | as G3 | none | the reproduction of C1 on this branch; the reference for G3 |

## How every number is chosen (inside each fold, never on the place it is judged on)

The rule of the light experiment, word for word (`fitgeo.choose`; `run_contrast.choose` for G3):

1. Every member and the fixed model are run on every training frame and counted with the judge's counting.
2. A member is allowed when the standard pass rule (`judge.decide`, the stored margins) does not call it FAIL against
   the fixed model (no checks) on the training places.
3. Among the allowed: the highest (found, per placement) minus (boxes not on their barrel, per arrangement), each as
   the difference from the fixed model.
4. A tie goes to the first in the family order. No allowed member with a gain above zero: the fixed model.

Leave one place out is the judge's (`judge.leave_one_place_out`): for each of the 8 places the rule runs on the frames
of the other 7 and the picked member is run on the held-out place only. G3: the C1 setting is the one C1's own fold
picked for that place (picked on the other places); the checks are then picked by the rule above with it fixed.
Also printed, in-sample and never a verdict: the member each rule picks on all eight places.

## What counts as success

The only pass rule is the standard judge (`docs/EVAL.md`), held out, **against today's default**: PASS, FAIL or NO
CLEAR DIFFERENCE. A PASS with found up by less than 6.0 placements is WEAK.

- **Question 2 is answered by G1.** Success = G1 PASSES. G1a and G1b say which check carries it.
- **Question 3, the cost**: G2 against today's default (the verdict), and every family with checks against the same
  family without them (printed beside, not a verdict: `vs_own_*`). The checks "cost real barrels" if any barrel is
  lost in those comparisons; each lost barrel is named and shown. G3 against today's default, and against C1
  reproduced.
- **Question 4**: the four D families with and without checks, side by side; the best trade is the one with the most
  found among those that do not FAIL; it is named, with its found and its boxes.
- Reported for every candidate, pass or fail: found per placement and per frame, gained / lost, boxes not on their
  barrel, boxes on clean empty frames and on empty frames with clutter, the places that moved, the extreme conditions
  (report only), the member each fold picked. **Traps by name**: the three cluttered empty bathroom frames
  (`lampmid3_`, `lampmid6_`, `lampwarm6_bathtile_neg_02`), the warm-lit glass empties, the clean empty frames.
- Contact sheets of every gained and lost barrel and every new box not on its barrel are made and looked at before
  the entry is written.

## Proof that nothing else moved

`check_same.py <inputs.pkl>`: on all 5435 masks of the proof harness, `stages.found` draws exactly the boxes of
`detector.detect`, and `checks.apply` with every check off returns them unchanged. It must say IDENTICAL BOXES ON
EVERY INPUT before the judged run (result in `results/2026-11-27_bluer_geom/check_same.md`).

## What I expect (written before the run)

- G1: most of the 16 extra boxes on clutter go (the jar by K2 and by K1 under the warm lamp, the tin and the figure by
  K1). Boxes not on their barrel about 3, under the margin; found about +11 (the ottoman barrel at 1.29 x may be lost
  in a fold that picks K2 at 1.25). A PASS. The bathroom fold is the risk: there, the checks are taught by the jar on
  the glass table and the pale-wood close-up only, so it may pick milder checks than the bathroom needs.
- G2: NO CLEAR DIFFERENCE or a PASS on clause 3 (the glass-table jar and the pale-wood close-up go), with no barrel lost.
- G3: about C1, a little fewer boxes. The contrast path's paint is solid; the jar's label may still be read as a stripe.
- D: the looser the delta, the more found and the more boxes; with the checks the trade moves toward 0.20 or 0.15.

## What this cannot show

Only two places have warm light, and the traps sit at one of them (the bathroom) and on the glass table. Leave one
place out teaches the checks for the bathroom from the glass table's jar and one pale-wood close-up. A pass says "the
traps on the glass table teach enough to remove those in the bathroom", not that the checks remove any clutter. The
checks were designed by looking at these very boxes; the grid values are in-sample. A new near-barrel object (a
different label shape, a solid blue tin) may pass both checks. The test frames are not looked at.

## Rounds

One round. A second round needs a dated addendum here, committed before it runs.

## Outputs

`results/2026-11-27_bluer_geom/`: `repro.json`, `judge_A_B4_repro/` (part A); `boxes.csv`, `false_boxes.md` (part B);
`check_same.md`; `chosen.json`, `chosen_contrast.json`, `judge_<family>/`, `vs_own_<family>/`, `summary.md` (part C,
D); `sheets/` (images, not committed). `ENTRY.md` in this folder.
