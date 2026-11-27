# Pre-registration: a barrel hidden at the side by a thing that is not a barrel (2026-11-26, TODO E7, map B9)

Written 2026-11-26 on branch `wip/exp-sidecut` (from `barrels` at `337f04c`), and committed **before any judged run**.
Train frames only. No test frame is loaded, viewed, scored or listed: every frame goes through `judge.load_frame` /
`judge.require_train`. No image pixel is changed. Nothing is learned.

## The question

A barrel 50 to 75 % hidden at the side by a box or a book. Today there is a cliff: simulated on our tables, a
straight edge hiding half leaves 96 of 104 found, hiding 60 % leaves 64, and at 75 % far fewer. The two real frames of
this kind (`occlx_02`, `occlx_03`, about 60 % hidden) are both missed. Tanush: "I feel like we can still work with
60 %, especially if we see the stripe and the bulge and the top or bottom edge."

Can one rule place such a barrel from its own side, with no cliff, without drawing a box on anything that is not a
barrel?

## Why today fails (the diagnosis, given)

A stripe narrower than 0.8 W goes down the "partly seen" branch. A side counts as hidden only for a reason: the frame
edge, a found nearer barrel, or the body and the stripe ending more than 15 % of W apart. A thing that is not a barrel
is "other" in the mask, like bare table, so it is never a reason. Then the outline may place the box. If not, a stripe
at least 0.4 W wide gets a box centred on what is seen (a guess, a quarter of a width off when half is hidden), and a
narrower one gets nothing.

## The rule

A barrel is widest at mid-height (25.5 mm) and narrower at the lid and the base (18 mm). So its own side **bulges**.
A side cut by a box is straight, upright or leaning.

For a partly seen stripe that no reason and no outline places, and whose top **and** bottom are seen where its row
predicts them:

1. Per row of the seen part, take its left edge and its right edge (the first and the last barrel-colored pixel,
   either color, inside the seen columns).
2. Split the rows by height: the top sixth, the bottom sixth, the middle between them.
3. For each edge: lay a ruler from its place in the top rows to its place in the bottom rows (the median column of
   each). The **bulge** is how far its median column in the middle rows sticks out past the ruler. A lean of the edge
   moves both ends of the ruler and cancels.
4. The same measure is taken on the barrel's outline (`Outline`, at the stripe's distance, stretched from the seen top
   to the seen bottom), in the same rows. That is the outline's bulge.
5. A side is **the barrel's own** when its bulge is at least a quarter of the outline's bulge, and at least 1 pixel.
6. Exactly one side is the barrel's own: the box is W wide from that side's seen end (rule `own_side`; for a thin
   piece of stripe `thin_own_side`).
7. Both sides are: all of the barrel is seen and its paint is narrow. The box is W wide, centred on what is seen,
   as today, and only for a stripe at least 0.4 W wide (rule `two_sides`).
8. Neither is, or it cannot be measured (an edge of the barrel is not seen, fewer than 8 rows, fewer than 2 rows in a
   band): **no box**. The centred guess is gone.

Like the outline, the rule never takes the place of a box that is already there. The top and the bottom of the box are
read as today. The checks after it (`holds_body`, duplicates, the verify stages) are as today.

It works when the stripe stops before the cut, because it reads the body and the stripe together.

**One flag**, `DetConfig.side_cut`, off by default:

| value | what it does |
|---|---|
| `centred` | today, box for box (the default) |
| `own_side` | **the candidate**: steps 1 to 8 |
| `own_side+centred` | the comparison arm: steps 1 to 6, then today's centred guess for a stripe at least 0.4 W wide |

The two arms differ only in "should the centred guess stay". On adoption the chosen value becomes plain code and the
flag goes.

The detector still takes only the mask. The photo is looked at in a separate analysis (P below), not by the rule.

## How every number is chosen

| number | value | how |
|---|---|---|
| the bands | top sixth, bottom sixth | Three splits were tried on the development pools: a sixth, a quarter, a third. A sixth separates own sides from cut sides best (see "What I looked at") |
| the share | 0.25 of the outline's bulge | A straight cut bulges 0. A barrel's own side in a real mask bulges about half of the outline's (median 0.45 to 0.62 on the development pools): the lid's top rows are often not painted and the table's reflection widens the base. 0.25 is halfway between |
| the floor | 1 pixel | the picture's resolution. Not tuned |
| rows needed | 8 in all, 2 per band | so that a median is a median. Not tuned |
| the outline's grid | 201 columns | precision only |
| `stripe_w_min` for `two_sides` | 0.4 | today's number for the centred box, unchanged |

Given by the task, not chosen: the amounts 0.5, 0.6, 0.65, 0.75; the "real-like" variant (stripe ends 6 px before the
cut); "placed" = centre within 10 % of the width.

## Development material and held-out material

- **Development** (looked at with the new rule before this was written): source barrels of the **HOME** and **ABP
  white** train frames and simulated edge and slant cuts on them; the five real frames with a black box at the side,
  `occlx_01` to `occlx_05`; the 16 real HOME train frames.
- **Held out** (the new rule was never run on them before this commit): the **CAMPUS** source barrels; every
  simulated scene of another kind; `occlx_06` to `occlx_19` and the glass `occlx_16`; every real frame of the other
  six places; the judge; the damaged masks; the proof harness with the flag on.

## What I looked at before writing this (honesty)

1. The diagnosis in the task, and the docs it names.
2. Today's detector on all 18 train `occlx` frames: its boxes, the labels, the reason logs. A sheet of the 18 photos.
   The mask around the hidden barrel of `occlx_01` to `04`, printed as text.
3. The bulge, measured on development material (`explore_dev.py`). Own sides of unhidden barrels, as a share of the
   outline's bulge, with bands of a sixth: HOME min 0.17, median 0.49; ABP white min 0.43, median 0.62. Cut sides of
   simulated cuts: at most 0.11 of the outline's bulge, at most 1.0 px. The five real frames: own sides 2.9 to 8.5 px,
   cut sides −2.8 to +0.1 px.
4. **A first version that I changed.** It took a side as own at half of the outline's bulge and said "cannot tell"
   when that half was under 1 px. Most real own sides bulge less than half of the outline's, so it missed most. I
   changed the share to a quarter, the floor to "at least 1 px", and the ruler to use the rows' own heights. I tried
   a grid of shares (0.15 to 0.5) on the development pools: no share put a box on the wrong side; 0.25 with a sixth
   gave the most right answers.
5. The simulated side cuts on the development pools with all three values of the flag (`results/…/dev/sidecut.md`).
   Plain cuts, edge and slant together, found of 156: today 150, 93, 72, 18 at 50, 60, 65, 75 %; `own_side` 152, 151,
   150, 122. Real-like: today 136, 98, 60, 7; `own_side` 153, 146, 134, 68. 13 boxes of `own_side` at 75 % are on the
   barrel but fail the strict rule: the slanted cut hides a bottom corner, the seen bottom is 6 to 9 px high, inside
   the detector's 15 % and outside the scorer's 10 % (map B8). One scene found today by the centred guess is lost by
   `own_side`.
6. The three values on `occlx_01` to `05`: `occlx_02` and `occlx_03` are found by `own_side`
   (boxes (91,122,140,171) and (101,120,151,171) against labels (92,119,143,170) and (99,120,152,172)); 01, 04, 05
   keep their boxes.
7. The three values on the 16 real HOME frames: one box changes. `far_02`: a small unhidden orange barrel (30 px
   wide) is found today by the centred guess; `own_side` draws no box there (neither side bulges by 1 px);
   `own_side+centred` keeps it. So I expect `own_side` to lose a few real barrels whose paint is narrow.
8. Synthetic barrels for the unit tests.

Not looked at: anything in "held out" above.

## Yardsticks

**(a) Simulated scenes** (`sim.py`; masks only, as the occlusion scorecard makes them).

- *Side cuts.* Source barrels cut from the HOME, CAMPUS and ABP white train frames (no flag, 3 px inside the frame,
  not overlapping another box, found by today's detector alone and unhidden). Kinds `edge` and `slant` (both leans),
  both sides, amounts 0.5, 0.6, 0.65, 0.75. Each scene plain and real-like. Scored against the full box twice:
  **found** (the strict rule) and **placed** (found, and the box's centre within 10 % of the width of the true
  centre). Reported for all pools, for the development pools, for CAMPUS alone, and per pool.
- *Every other kind* of the occlusion scorecard (15 kinds, 25, 50, 75 %) on the same source barrels: found before and
  after per kind, the number of scenes whose boxes differ from today, boxes on no barrel.

**(b) The real occlusion set** (`real.py`): the 18 train `occlx` frames, barrel by barrel, before and after. And every
box the rule adds, moves or removes on **any** real train frame (261 masks), each on a contact sheet that I look at.

**(c) The standard judge** on the ordinary train conditions, for both arms:
`python barrels/tools/judge.py --cand-det side_cut=own_side` and `…=own_side+centred`. And the proof harness's
masks with the flag on (`harness_on.py`): the 666 damaged masks, the 522 real masks with one pixel taken off or
added, the 45 hand-threshold masks, each box given its state by `counting.classify_frame` against the labels.

**(P) The photo at the cut: an analysis, not a rule** (`photo_cue.py`). For every labelled barrel of the train frames
that has a stripe in the mask, and for each of its two sides: the largest difference, over blue, green and red, between
the median color of the strip just beside the seen end (max(3, 12 % of W) columns, the stripe's rows) and the median
color of the table just below the barrel (the same number of rows under the seen bottom, the seen columns). A side is
"hidden by a thing" when the label is flagged occluded, the seen end is more than 15 % of W inside the label's box
there, no other barrel's box covers the hidden part and the box does not touch the frame. A side of an unflagged
barrel is "free". Reported: the two distributions, per place, and how many free sides lie above the smallest value of
a hidden side. No threshold is set. It answers: could the photo be an extra reason for a hidden side, and what would
it add to what the mask rule finds. A rule from it would be a second round.

## What counts as success

For an arm (`own_side`, and separately `own_side+centred`), **all** of:

- **R0.** At the default, the proof harness prints `IDENTICAL BOXES ON EVERY INPUT` and the test suite passes.
- **R1. No cliff.** Side cuts, edge and slant together: found at 60 % hidden is at least 90 % of found at 50 % hidden.
  Asked four times: all pools and CAMPUS alone, plain and real-like. (Today on the development pools: 62 % and 72 %.)
- **R2. Not worse than today on side cuts.** At every amount (edge and slant together, all pools; plain and real-like
  each): found is not lower than today's by more than 2 % of the scenes, and placed is not lower than today's by more
  than 2 % of the scenes.
- **R3. No box off the barrel in side cuts.** Boxes that do not touch the true box at all: not more than today.
  (Boxes on the barrel that fail the strict rule are counted and reported; they are not a failure.)
- **R4. Nothing else worse.** For each of the 13 other kinds of scene (all amounts and pools together): found is not
  lower than today's by more than 2 % of its scenes (at least 1 scene). Boxes on no barrel, all 13 kinds together: not
  more than today.
- **R5. The real occlusion set.** Every barrel found today is still found. No new box in the states `nothing`,
  `second` or `wrong_color`.
- **R6. The judge** does not say FAIL, and the boxes that are not on their barrel (on nothing, second, wrong color;
  counted per frame on the ordinary conditions) are not more than the baseline's.
- **R7. Damaged masks.** On the 666 damaged masks, the 522 one-pixel masks and the 45 hand-threshold masks: boxes in
  the states `nothing`, `second` and `wrong_color` are, in each group, not more than today's.

**The decision, fixed now.** Recommend `own_side` if it meets R0 to R7. Else recommend `own_side+centred` if that
meets R0 to R7. Else recommend neither, and say which clause failed.

What I expect: `own_side` to fail R4 on the kind `both` (both sides cut by the same amount: today's centred guess is
exactly right there, by the symmetry of the simulation), and to lose a few real barrels with narrow paint (point 7
above). `own_side+centred` to meet R4. I do not know what the judge will say.

`occlx_02` and `occlx_03` being found is **not** a test: I saw it during development.

## What would make me distrust the result

- A box of the new rule on the wrong side of a barrel in the held-out pool (none on the development pools).
- A new box on a real frame that is not on a barrel. One is enough to stop.
- CAMPUS much worse than the development pools: then the numbers were fitted to two tables.
- Two real frames are still two real frames. The simulated cuts are ruler-straight; real cuts are ragged.

## Outputs

`results/2026-11-26_sidecut/`: `dev/sidecut.md` (development, already there); `sidecut.md`, `scorecard.md` and their
`.csv` (a); `real.md`, `real_changes.md`, `sheets/` (b); `judge_own_side/`, `judge_own_side_centred/`, `harness_on.md`
(c); `photo_cue.md` (P); `summary.md`. `ENTRY.md` here: the text for `EXPERIMENTS.md`, with the map change the rule
would need.

A second round needs a dated addendum, committed before it runs.
