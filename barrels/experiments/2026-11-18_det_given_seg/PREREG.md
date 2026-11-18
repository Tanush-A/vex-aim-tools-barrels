# Pre-registration: the detector given good segmentation (TODO item A), written 2026-11-18

Written and committed after the baseline run (step 1) and **before any fix was coded or evaluated**. The
designs below come from the baseline's reason log and pictures only.

## The principle under test

"If the segmentation is good, the detector finds the barrel." Today that is false in known cases.

## Baseline (step 1; `results/2026-11-18_det_given_seg/step1_baseline/`, git 2b6ca83, detector as on `barrels`)

Found / barrels (false boxes), v2 rule, train frames only.

| level | scenario | base |
|---|---|---|
| 1 | perfect masks, HOME (16 frames) | 25 / 29 (0) |
| 2 | light damage (5 seeds) | 131 / 145 (0) |
| 2 | medium damage (5 seeds) | 36 / 145 (24) |
| 2 | heavy damage (5 seeds) | 12 / 145 (2) |
| 3a | CAMPUS, adopted color model | 34 / 35 (0) |
| 3b | BLACK, thresholds from the frame's labels | 17 / 26 (1) |
| 3c | wood, cool lamp, thresholds from the labels (report only) | 24 / 42 (7) |

One kind of damage at a time (report only; undamaged = 125 / 145): top highlight 0.5 × 0.3: 130 (0); top
highlight 0.7 × 0.4: 112 (5); stripe highlight 0.15: 85 (35); stripe highlight 0.3: 57 (53); stripe breaks
2 × 0.08: 61 (32); edges 1 px: 130 (0); edges 2 px: 95 (0); dropout 10 %: 125 (0); speckle 30: 125 (0).

Eval table (`tools/report.py --base-model default`): HOME 25 found / 4 missed / 0 false (0.93); CAMPUS 34 / 1 / 0
(0.99); BLACK 2 / 24 / 0; wood bright (6 lamp settings) 7 / 119 / 3; wood brightness 1: 0 / 63 / 0; Dave 11 / 23 / 2
(0.47). No box on any negative frame.

What the reason log and the pictures say:

1. **A barrel behind a barrel of the other color** is never found: 4 of 4 misses on the perfect masks (HOME
   `occl_01`, `occl_02`, two in `cluster_01`) and 3 of the 9 misses on the black table (`occl_02`, `occl_03`,
   `occl_04`). The back barrel shows its upper body (a "cap") above the front barrel. Its stripe has the front
   barrel's body color, the two join, and the patch is refused as too tall for a stripe (`height`: 19 to 37 px
   against 11 to 19 expected). In `cluster_01` one back barrel shows no stripe at all, only the cap between two
   front barrels.
2. **A stripe in pieces** is refused piece by piece: one pale patch 0.15 of a barrel wide across the stripe takes
   125 → 85 found and adds 35 false boxes (each piece is under the 0.4 width floor, or one piece passes alone as
   a "partly hidden" stripe and its box is drawn in the wrong place). A wide highlight on the upper body
   (0.7 × 0.4) does the same from above: the stripe pixels under it have no body color above them, so the stripe
   survives only at its two ends.
3. **Side occlusion** (CAMPUS `occl_02`): the stripe shows 0.30 of a barrel, the floor is 0.4.
4. Not addressed here (said so now): edges eaten by 2 px (125 → 95; a far stripe 6 px tall loses 4 px and is
   under the height floor); the two far barrels cut by the left frame edge in black `close_02` / `held_01`
   (glare, almost nothing painted); black `clutter_02` (stripe 3 px tall); black `far_01` (the orange reflection
   on the glossy table is painted as body, the box bottom is 7 px low).

**Expected size check** (`size_check.md`): the hand-drawn boxes agree with the camera model's size at their
bottom row: median width ratio 0.95 to 1.03, height ratio 0.96 to 0.99 per set. No set is systematically off, so
size does not explain refusals. One bias exists: the bottom row predicted **from the top row** is 4 to 7 px too
low at mid and far range (HOME +4.4, CAMPUS +5.4, wood +7.1; near barrels about 0). On the same boxes, "top row
+ the height of a barrel as wide as the box" is off by a median 0.6 to 2.1 px and lands within the v2 bottom
tolerance on 162 of 191 boxes against 105 of 191. This matters for change 1 below.

## The changes (each a `DetConfig` switch, off by default until it passes)

### 1. `cap_behind`: a barrel standing behind a found barrel

After the stripe barrels and the stripeless pieces are found: take each color's pixels, without the boxes of the
stripes already used. A connected piece of one color is the **cap** of a hidden barrel when all of these hold:

- it is not a found barrel's own body: fewer than half of its pixels lie inside found boxes of its own color;
- its top row gives the distance (as in step 3), the distance gives the expected width W, height H and the
  height of the upper body (top row to the top of the stripe);
- it is barrel-wide: between `width_min` (0.4) and `body_width` (1.2) × W; and the barrel is on the table
  (W ≥ `min_width_px`);
- it is as tall as an upper body, not more: between `height_min` (0.5) × the upper-body height and the
  upper-body height plus the usual edge tolerance (`bottom_tol` 15 % of H, at least 4 px). Body color running on
  below where the stripe must start is not a barrel top;
- what hides the rest is a barrel: at least half of the predicted box below the cap lies inside boxes of found
  barrels whose bottom edge is lower than the cap's (they stand nearer).

The box: top = the cap's top row. Left and right = the cap's columns; a cap narrower than `stripe_full` (0.8) × W
is partly hidden at a side and is widened to W toward the side where barrel color or the frame edge borders it
(the rule the partly hidden stripe already uses). Bottom = top + the height of a barrel as wide as the cap when
the whole width shows, else the bottom the top row predicts (`predicted_bottom`). Flags `occluded`,
`bottom_inferred`. A box that overlaps a found box of the same color by IoU > 0.5 is dropped.

No new number: every threshold is one the detector already has. Reason for the design: the stripe cannot be the
anchor here (it has melted into the front barrel, or is hidden), so the evidence is the other half of what makes a
barrel recognisable: a body-colored top of the right width and height for its row, cut off by a barrel we have
already found. The earlier written idea (TODO step 9 of 2026-11-11: "a stripeless body piece directly above a
found barrel of the same color, barrel-sized for its row, is a barrel") is this, corrected in two places seen in
the pictures: the piece must be found per color (in a mixed pair the blob holds both barrels), and it is
cap-sized, not barrel-sized. Why height from width: the size check above.

### 2. `stripe_join`: a stripe in pieces is one stripe

Today each connected piece of sandwiched stripe color is tested alone. With the switch on, pieces of the same
body color that share rows (they overlap by at least half the height of the shorter one) and that together span
no more than one barrel (`body_width` 1.2 × W) are one stripe, whatever lies between them (a highlight, a shadow
line, stripe pixels whose body color above was washed out). The joined stripe then passes the same tests as
before (area, height 0.45 to 1.6, width at least 0.4, merged-stripe cut). Pieces are taken left to right.

Reason: two different barrels cannot both have their stripe inside one barrel's width at the same rows, so
pieces that fit inside one barrel's width are the same barrel's. Touching same-color barrels are unaffected: their
pieces together span two barrels, so nothing is joined that was not joined before. One new number: "half" for
sharing rows.

### 3. Side occlusion, re-evaluated: `stripe_w_min` 0.4 → 0.25 with `occl_body_side` on

Unchanged from `experiments/2026-11-11_occl_narrow_stripe/PREREG.md` (0.25 = the point where "not taller than
wide" takes over from the width floor). It failed there only on two frames of the orange wood table, which is now
report-only.

## Arms

`base`; `cap` (1 alone); `join` (2 alone); `cap+join`; `cap+join+side` (1 + 2 + 3); `side` (3 alone, report
only).

## Acceptance rule (fixed now)

An arm passes when all of these hold against `base`:

1. **Never regress.** `python barrels/tools/report.py --cand-det <arm> --base-model default`: in every scenario
   row of HOME (leave-one-scene-out) and of CAMPUS, found is not lower and false is not higher; and no box on a
   clean negative frame of any set. The black, wood and Dave rows are reported, not judged.
2. **Level 1:** every barrel found, or each remaining miss explained and argued to be undetectable from a perfect
   mask.
3. **Level 2:** strictly more barrels found at each of the three severities, and no more false boxes at any of
   them.
4. **Level 3:** 3a (CAMPUS) not lower, 3b (BLACK) strictly higher, false boxes not higher in either. (Reading
   note, written now: "level 3 strictly better" is taken as 3b strictly and 3a not lower, because 3a's single
   miss is the side-occlusion barrel that only change 3 addresses. Whether 3a itself improved is reported per
   arm.)
5. **Unlabeled recordings** (`data/recordings/`, local): every box that appears or disappears against `base` is
   looked at on a contact sheet; appearing boxes must be on real barrels and disappearing boxes must have been
   wrong, with at most the exceptions written in `by_eye.md` and argued there. A new box on something that is
   not a barrel fails the arm.

Adopted as the default on `wip/detector-given-seg`: `cap+join+side` if it passes; else `cap+join`; else `cap`
or `join` alone if one passes (both reported). Anything that does not pass stays behind its switch, off. The
rule is not re-picked after the results. A flaw in the test itself may be corrected in an addendum below, with
the reason, keeping both runs.

**A known weak point of the test, written now.** The seven hidden barrels that change 1 is for all carry the
label flag `bottom_estimated`: their bottom edge was guessed by hand, and three of the labels are no taller
than wide (HOME `occl_02` 46 × 44, black `occl_04` 67 × 64, black `occl_02` 56 × 56), which a barrel rarely is
(unoccluded boxes: median height / width 1.05 to 1.07 in every set, 10th percentile 0.90 to 1.00). Under the v2 rule a box on the right barrel whose bottom differs
from such a label by more than a tenth of the height counts as one miss **and** one false box. The rule above is
kept as it is; boxes of this kind (same color, IoU ≥ 0.5 with a `bottom_estimated` label, bottom outside the
tolerance) are also counted separately in the summary as "right barrel, bottom differs from the hand estimate",
so the reader can see why an arm failed if it fails for this.

---

# Addendum, 2026-11-18: round 1 failed; round 2, written before round 2 was coded or run

## Round 1 result (`results/2026-11-18_det_given_seg/round1/`; nothing adopted)

Found / barrels (false boxes).

| | base | cap | join | cap+join | cap+join+side | side |
|---|---|---|---|---|---|---|
| 1 perfect masks | 25 / 29 (0) | 27 / 29 (2) | 25 / 29 (0) | 27 / 29 (2) | 27 / 29 (2) | 25 / 29 (0) |
| 2 light | 131 / 145 (0) | 141 (0) | 131 (0) | 141 (0) | 141 (0) | 131 (0) |
| 2 medium | 36 / 145 (24) | 36 (27) | 114 (6) | 115 (11) | 122 (10) | 92 (16) |
| 2 heavy | 12 / 145 (2) | 12 (2) | 30 (2) | 30 (2) | 33 (0) | 20 (1) |
| 3a CAMPUS | 34 / 35 (0) | 34 (0) | 34 (0) | 34 (0) | 35 (0) | 35 (0) |
| 3b BLACK | 17 / 26 (1) | 19 (2) | 17 (2) | 19 (3) | 19 (3) | 17 (1) |
| eval table HOME, found / false | 25 / 0 | 27 / 0 | 25 / **4** | 27 / **4** | 27 / **4** | 25 / 0 |
| eval table CAMPUS | 34 / 0 | 34 / 0 | 34 / 0 | 34 / 0 | 35 / 0 | 35 / 0 |
| recordings, boxes appearing / wrong ones | | 3 / 3 | 13 / 10 | | | 5 / 0 |

Every arm fails: `join` and the arms that hold it fail rule 1 (4 false boxes at HOME) and rule 5; `cap` fails
rule 5 (3 wrong boxes), rule 3 (medium: not more found, 3 more false) and rule 4 (3b: one more false box).
By the rule, nothing is adopted from round 1. `side` alone does what it did on 2026-11-11 (campus `occl_02`
found, 5 real barrels in the recordings, nothing false at HOME or CAMPUS) but does not address level 1.

## What was wrong with the two changes (from the round-1 reason logs and pictures)

`cap_behind`:
- The 3 wrong boxes in the recordings are all caps **narrower than a barrel with nothing hiding their sides**
  (a 15 px patch above a barrel under a hand; table color above a barrel on wood). Round 1 widened any narrow cap
  to a full barrel, "centred" when no side was bordered.
- In `cluster_01` both hidden barrels are boxed (IoU 0.71, 0.68) but 7 to 8 px too low: a cap hidden at a side
  gets its bottom from its top row, the estimate the size check found biased by +4 to +7 px. For the left one the
  barrel's own bottom is in fact visible beside the front barrel and was not used.
- Black `occl_04`: boxed with IoU 0.86, bottom 200 against a hand-estimated 193 (the label is 67 × 64). This is
  the weak point declared above; it is not changed.

`stripe_join`:
- All 4 false boxes at HOME and the 3 in campus `r2_pan` are joined pieces that are **each taller than a stripe
  or taller than wide**: slivers of a barrel's own upper body (3 × 10 px, 10 × 21 px) between specks. Alone each
  fails "not taller than wide"; joined, the group is wide enough.
- The black-table boxes drawn half off the barrel are a half-visible stripe widened to the wrong side: the
  existing rule for a partly hidden stripe, which switch (h) `occl_body_side` replaces.

## Round 2: the changes to the two designs (same switches, same rule, same arms)

`cap_behind`, two changes:
1. **A narrow cap must be explained.** A cap that shows less than `stripe_full` (0.8) of the expected width is
   kept only when exactly one of its sides is hidden by a found barrel standing nearer (that barrel's box holds
   the pixel next to the cap at the cap's middle row) or by the frame edge; the box is widened to W toward that
   side. Hidden at neither side: not a cap (its narrowness has no cause). Hidden at both sides (a wedge between
   two front barrels): no box, because neither its width nor its place can be measured; this stays a miss and is
   reported as one.
2. **The seen bottom is used when it agrees.** As in step 3: if the cap's own color appears in the cap's columns
   near the estimated bottom (within the usual tolerance, 15 % of the height, at least 4 px) and ends there, that
   seen bottom is the box bottom. Otherwise the estimate stays (height from width when the whole width shows,
   from the top row when a side is hidden).

`stripe_join`, one change: **a piece joins only if it has a shape a stripe can have**: not taller than
`stripe_h_max` (1.6) × the expected stripe height, and not taller than wide. Small is allowed (that is what a
cut stripe leaves); the minimum area, height and width are still asked of the joined whole. Known cost, accepted
now: the two end slivers left by a wide highlight on the upper body are taller than wide and will not join.

Arms, acceptance rule, adoption order: unchanged from above. This is a second attempt at the same rule, made
after seeing round 1 on the train frames and the recordings; the test frames are untouched and remain the only
unbiased check. Round 1's outputs are kept in `round1/`. There will be no round 3 in this experiment.
