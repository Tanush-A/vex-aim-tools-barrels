# Pre-registration: where is a cut barrel, sideways? (occlusion, direction "pin")

Written 2026-11-19 on branch `wip/occl-pin` (from `wip/detector-occl`, git 085c99d), after the censuses and the
baseline below, and **before any detector code was written**. Scripts in this folder: `shape_census.py`,
`thin_census.py`, `look_sources.py` (measurements); `pin_arms.py`, `run.py` (the occlusion scorecard of
`2026-11-19_det_occl`, loaded by path), `levels.py`, `recordings.py` (the earlier tests, loaded by path),
`check.py`. Results: `results/2026-11-20_occl_pin/`.

## What was asked

The occlusion round of 2026-11-19 ended with a part that finds far more (3155 of 3888 scenes against 2417) by
drawing a "cover box" up to 1.78 barrels wide where nothing says which side of a cut barrel is hidden. Tanush
(2026-11-19): that part stays off; keep trying new methods; he does not like false positives at all, and a box
where no barrel is, a box half off the barrel and a box nearly two barrels wide all count against a method.

This direction: the distance, hence the full size, is known from the stripe's row. What is missing for a barrel
cut at the side is its sideways position. Find what in the seen part says where the barrel is, measure each cue
before building on it, and draw a box **one barrel wide**, placed by the cue, **only when the cue knows**;
otherwise nothing new is drawn.

## Baseline (`step1_baseline/`, git 085c99d, the defaults of `wip/detector-occl`)

`base` = `stripe_join`, `cap_behind`, `side_hidden`, `seam_height`, `cap_seen_bottom`, `edge_check`, `cap_same` on;
`slice_box`, `cover_unpinned`, `stripe_two` off (spelled out in `pin_arms.py`).

- Scorecard (3888 scenes, 50 source barrels): found 2417; a box in the right place 2532; boxes where no barrel is
  45; right-place boxes too small / about right / too big 299 / 2129 / 104 (too big: 4.11 %).
- The targeted cells, found of n:

| what hides the barrel | 50 % hidden | 75 % hidden |
|---|---|---|
| a straight upright edge, one side | 82 of 100 | 0 of 100 |
| a slanted edge, one side | 154 of 200 | 0 of 200 |
| both sides cut | 49 of 50 | 0 of 50 |
| cut by the frame edge | 99 of 100 | 3 of 100 |
| a plain block of the body color | 99 of 100 | 5 of 100 |
| a plain block of the stripe color | 99 of 100 | 3 of 100 |

  Together: 593 of 1300.
- Earlier levels: perfect HOME masks 28 / 29 (0 false); light / medium / heavy damage 143 (0) / 99 (1) / 21 (0) of
  145; CAMPUS 35 / 35 (0); BLACK with label thresholds 19 / 26 (2).
- Eval table: HOME 28 / 1 / 0, CAMPUS 35 / 0 / 0, no box on any negative frame of any set.
- Recordings: 506 boxes on 337 frames.

Why the targeted cells fail today (the 2026-11-19 reason logs): at 50 % hidden by a straight edge the stripe
piece has no reason for either side, so the box is centred on what is seen (a quarter barrel off; overlap 0.59) or,
under 0.4 of a barrel, refused; at 75 % the piece is about as wide as a stripe is tall and the finder's floor refuses it.

## The censuses (`results/2026-11-20_occl_pin/shape_census.md`, `thin_census.md`)

Source barrels: the 50 unhidden train barrels of the scorecard; "hand masks" = the 12 HOME hand masks, "color
model" = the same 12 as the color model segments them + 26 of CAMPUS. W = the barrel width the stripe's row gives.

**A. The outline has a shape the camera model predicts.** Seen from 43 mm up, looking 22 degrees down: the top
edge is the far rim of the lid (18 of 25.5 mm = 0.71 W across), nearly flat, and then a shoulder runs down to the
full width at mid-height; the bottom edge is the near rim of the base, with a corner running up; the stripe is an
arc, lowest at the centre. Measured, in W (median), against the model:

| | top rise at 0.3 W | shoulder at 0.46 W | stripe sag | base rise at 0.3 W | base corner at 0.46 W |
|---|---|---|---|---|---|
| seen, 45 to 70 px wide, hand masks | 0.019 | 0.184 | 0.024 | 0.028 | 0.233 |
| seen, 45 to 70 px wide, color model | 0.015 | 0.236 | 0.035 | 0.038 | 0.315 |
| model, straight side from lid to middle | 0.017 | 0.397 | 0.035 | 0.038 | 0.424 |
| model, curved side (radius falls off with the square of the height above the middle) | 0.017 | 0.273 | 0.035 | 0.038 | 0.306 |

The arcs are real but small: the top rises 1 px across a 55 px barrel and the stripe sags 1 to 2 px (4 to 7 px on
a barrel over 100 px wide). **The corners are large**: in the last 8 % before a barrel's own side the top is 10 to
13 px lower and the bottom 13 to 17 px higher than in the middle (55 px barrel). A straight side predicted the
shoulder twice as deep as it is seen; the curved side fits and is the one used below.

**B. The centre column from each cue** (a straight edge cuts the barrel so that 75 / 50 / 25 % of the width
shows; error in barrel widths, median / 90th percentile; color model; one side cut):

| seen | centred (today) | top apex | top line fit | stripe arc fit | bottom line fit | all three lines |
|---|---|---|---|---|---|---|
| 75 % | 0.11 / 0.12 | 0.12 / 0.25 | 0.03 / 0.10 | 0.06 / 0.13 | 0.03 / 0.06 | 0.02 / 0.05 |
| 50 % | 0.24 / 0.25 | 0.14 / 0.27 | 0.03 / 0.22 | 0.06 / 0.19 | 0.03 / 0.07 | 0.03 / 0.05 |
| 25 % | 0.36 / 0.38 | 0.29 / 0.36 | 0.04 / 0.23 | 0.07 / 0.35 | 0.05 / 0.13 | 0.03 / 0.07 |

"Fit" = the predicted line slid sideways to where it lies closest to the seen one. The apex of the top edge is
useless (the top is flat). The stripe's arc alone is weak (90th percentile 0.19 to 0.35). The top and the bottom
lines locate the centre to 0.03 to 0.05 W in the median **when a corner is in view**, and the three lines
together to 0.02 to 0.03 W, 90th percentile 0.05 to 0.07, on hand masks and on real segmentation alike.

With both sides cut by different amounts the best fit is right at 75 and 50 % seen (0.02 / 0.05 and 0.02 / 0.09)
and poor at 25 % (0.06 / 0.17): a quarter from the middle of a barrel is flat and fits at many positions.

**C. When does the outline know?** The positions whose cost (mean distance in rows between seen and predicted
lines) is within `near` x H of the best one's "fit". With near = 0.01 H, the outline "knows" when every fitting
position is within 0.15 W of their middle and the best cost is at most 0.05 H. Scenes where it knows / of those
wrong by more than 0.15 W / the largest error (both groups, 100 + 100 + 50 scenes per column):

| | 75 % seen | 50 % seen | 25 % seen |
|---|---|---|---|
| one side cut | 92 / 0 / 0.08 | 85 / 0 / 0.13 | 80 / 0 / 0.11 |
| both sides, unequal | 94 / 0 / 0.06 | 42 / 0 / 0.10 | 4 / 0 / 0.07 |
| both sides, equal | 47 / 0 / 0.06 | 17 / 0 / 0.13 | 0 / 0 / - |

No scene of the 461 where it knows is wrong by more than 0.15 W. With the best cost limited to 0.03 H instead:
86 / 77 / 57 one side cut, also none wrong. **For a quarter seen from the middle of a barrel the outline knows in
4 of 150 scenes: nothing in the mask says where such a barrel is.**

**D. The corners alone** (share of body color in the corner squares of the seen part's end) separate a barrel's
own side from a straight cut less well: with a limit that calls 88 % of own sides "own", 7 % of straight cuts and
18 % of slanted cuts are called "own" too (color model). The line fit uses the same evidence with the size known,
and is what is built.

**E. Real partly hidden barrels** (the 10 flagged `occluded` on HOME and CAMPUS, nearly all hidden by another
barrel): most show 0.8 W or more, where the detector takes the seen width as the box and the outline is not
asked. Where less shows (HOME `cluster_01` 0.38, CAMPUS `clutter_02` 0.47, `occl_02` 0.64) the outline does not
know (the lines are mixed with the neighbour's), and the box stays what it is today. **There is no real train
frame of a barrel cut at the side by a straight edge that is not a barrel with the corner of the barrel clean; the
census cannot validate the cue on real occlusion (shots are listed in the report).**

**Thin pieces on real frames (`thin_census.md`).** If the finder's floor is lowered, 124 thin stripe pieces appear
on the 137 train frames and 337 recording frames; 28 are full slices (top and bottom where the row predicts
them); the outline knows for 2 of them, and both are barrels with no box today (campus clip `r3_enter_leave` 013,
the orange barrel entering at the frame edge; black clip 032, the blue barrel). With the best cost limited to
0.03 H: none.

**Negative evidence, plainly.** The detector sees a class mask: orange, blue, nothing. A thing that hides a
barrel and is not barrel-colored is "nothing", exactly like the table. So "there is empty table here, the barrel
cannot be hidden here" cannot be read from the mask; only a barrel-colored occluder is visible in it (and is
already used: a found nearer barrel, a body running on past the stripe). In the image an occluder usually is
visible (an edge, a different color); using it would mean a second input to the detector. Not built; noted as a
lead that needs real frames.

## The idea, one sentence

**The barrel's outline is known once its distance is known; slide it sideways over the seen part; if it fits in
one place only, the barrel is there.**

## The changes (each a `DetConfig` switch, off until it passes)

### 1. `pin_outline`: a partly seen stripe that no side reason places is placed by the outline

Where: `_partly_seen`, step 5 (the stripe is narrower than 0.8 W, what is seen of the barrel too, and either no
side or both sides have a reason to be hidden). Today: centred on what is seen if the stripe is 0.4 W or wider,
else no box. With the switch, first:

1. *The predicted outline* for the distance the stripe's row gives, as three lines over the columns: the top (the
   lid's far rim, an arc 0.71 W wide, then the curved shoulder down to the full width at mid-height), the
   stripe's middle (an arc over the full width), the bottom (the base's near rim, then the corner up). Every
   number is the camera model's and the barrel's (24 mm tall, 18 and 25.5 mm across, 6 mm stripe).
2. *The seen lines*, per column of the seen part: the top of the body color joined to the stripe from above,
   the end of the body below it, the middle row of the stripe's pixels.
3. *Slide*: for every centre column a barrel holding the seen part can have (and 0.15 W more), the cost = the
   mean distance in rows between each seen line and the predicted one, after taking out that line's own up-down
   offset (its median), averaged over the three lines.
4. *Knows*: the best cost is at most `pin_good` (0.05) x H, and every position whose cost is within `pin_near`
   (0.01) x H of the best lies within `bottom_tol` (0.15, the existing edge tolerance) x W of the middle of those
   positions.
5. *The box*: W wide, centred on that middle. If the outline does not know: exactly as today.

New numbers: `pin_near` 0.01 and `pin_good` 0.05, both shares of the barrel's height, read off census C.

### 2. `pin_thin` (only with `pin_outline`): a thin piece of stripe is a barrel when the outline places it

- The finder's width floor for a stripe piece becomes `stripe_h_min` (0.45, the floor the stripe's height already
  has) x the stripe height, and a piece may be taller than wide (today: one stripe height, not taller than wide).
  A piece under today's floor is "thin".
- A thin piece gives a box only when (a) it is a full slice: the body above and below it ends where its row
  predicts the top AND the bottom (the usual tolerance), and (b) the outline knows; the box is where the outline
  puts it, W wide. Otherwise no box, whatever reasons its sides have. This is stricter than the full slice
  alone of 2026-11-19, and there is no cover box.
- A thin piece that shares rows with the stripe of a found barrel of its body color, inside that barrel's box,
  is a second piece of that stripe (the 2026-11-19 `_piece_of_found`), not another barrel.
- Thin pieces never change another barrel's box (they do not count among the "other stripes" whose columns a
  barrel's body may not take).

### Not built, with the reason

- **A quarter of a barrel seen with both sides cut:** the census finds no cue (4 of 150). No box, as today.
- **The cover box, or any box wider than a barrel.**
- **The corner squares, the top's apex, the stripe's arc alone:** weaker than the line fit (census B, D).
- **The gray image** (shading across the body, a visible occluder): a second input; no evidence yet that the
  mask is not enough for the one-side cuts, and no real frames to test it on.

## Arms

`base`; `pin` (1); `pin+thin` (1 and 2).

## Expected, written now

- `pin`: straight edge at 50 %: 82 → 90 or more of 100, the boxes no longer a quarter barrel off; slanted edge
  at 50 %: 154 → 175 or more of 200. Both sides at 50 % stays 49 or 50 (centring is right there by symmetry).
- `pin+thin`: at 75 %: straight edge 0 → 50 or more of 100; slanted edge 0 → 60 or more of 200; frame edge 3 →
  50 or more; block of the body color 5 → 50 or more. Block of the stripe color at 75 %: not sure (the block
  hides the lower body in the columns where the top still shows). **Both sides at 75 %: stays 0.** A post at 50 %
  (not targeted) should rise: each half shows a corner.
- Risks: (i) a box moved by `pin` from "centred, overlap 0.6" to a wrong place when the outline is wrong: the
  scorecard's right-place counts and the recordings would show it; (ii) thin pieces between touching barrels
  that are full slices by accident and fit the outline by accident: damaged masks, clutter, the hand clip;
  (iii) near barrels are up to 1.28 x the width their row predicts: the outline is then too small and should
  not fit (no box) rather than fit in the wrong place.

## Acceptance rule (fixed now; the coordinator's clauses, with two readings made explicit)

An arm passes when all of these hold against `base`:

1. **No false positive added anywhere.**
   (a) Eval table (`levels.py` writes `never_regress.md`; the same as `python barrels/tools/report.py --cand-det
   <arm> --base-model default`): no scenario row of HOME (leave-one-scene-out) or CAMPUS loses a found barrel or
   gains a false box (HOME 28 / 1 / 0, CAMPUS 35 / 0 / 0); no box on any negative frame of any set.
   (b) Scorecard: boxes where no barrel is not above 45.
   (c) Damage: false boxes at light / medium / heavy not above 0 / 1 / 0. Stricter, mine: found not lower at any
   level (perfect masks, light, medium, heavy, CAMPUS, BLACK with label thresholds) and false boxes not higher
   at perfect masks (0), CAMPUS (0) and BLACK with label thresholds (2).
   (d) Scorecard: the share of right-place boxes that are too big not above the baseline's (104 of 2532, 4.11 %).
2. **Recordings** (`recordings.py`): every box that appears or disappears on the campus clips (r1 to r4) is
   looked at on a contact sheet. No new box on something that is not a barrel or half off its barrel. A box that
   disappears must have been wrong, or be replaced in the same frame by a box that sits better on the same
   barrel. The black and wood clips are described, not judged.
3. **The scorecard's targeted cells** (straight edge, slanted edge, both sides, frame edge, the two plain
   blocks, at 50 and 75 % hidden: 12 cells, 593 of 1300 today). Reading, fixed now: five of these cells are at 98
   or 99 % and cannot rise by more than a scene, and for one (both sides, 75 %) the census found no cue. So the
   clause is: **the 12 cells together are higher; no cell of the whole scorecard is lower, in found or in
   right-place boxes; and the cells the arm commits to are each higher**: `pin`: straight and slanted edge at 50 %;
   `pin+thin`: those two, and straight edge, slanted edge, frame edge and block of the body color at 75 %. If both
   sides at 75 % stays 0, the report says so in its first lines; it is not hidden behind the sum.

Adopted on `wip/occl-pin`: `pin+thin` if it passes; else `pin` if it passes; else nothing is switched on. What
does not pass stays behind its switch, off, and the report names it. The rule is not re-picked after the
results. At most two rounds: if round 1 fails, a dated addendum is written below before any corrected code. One
correction is named in advance: if the failure is a false box of clause 1 or 2 drawn where the outline "knew",
round 2 lowers `pin_good` to 0.03 (census C: 86 / 77 / 57 of 100 one-side scenes instead of 92 / 85 / 80).
The test frames are never opened; no camera constant changes; the image is never corrected.

## What this cannot show

The cuts are made on the mask with a straight edge. A real edge throws a shadow on the barrel, is not straight to
a pixel, and bleeds at the seam; the corner the method needs is on the side away from the edge, but a shadow or a
highlight on that corner would make the outline not know (a miss, not a wrong box). Real frames are needed to say
how often.
