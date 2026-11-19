# Pre-registration: hidden bottoms that come from the top row (TODO A5)

Written 2026-11-19, after the baseline run and the census below, and **before the change was coded or evaluated**.
Small and time-boxed: one change, one round. If it fails, it is reported and left off; there is no second round.
Test: the one of `experiments/2026-11-19_det_side` (which loads `2026-11-18_det_given_seg`), loaded by path
(`run.py`, `recordings.py`); `census.py` is new and only measures.

## The finding this acts on

With the camera in use (`AIM_4A8B6118_BOXFIT`), the bottom predicted from a barrel's **top row** is 4 to 7 px too
low for far and mid barrels and about right for near ones (`size_check.md`). "Top row + the height of a barrel as
wide as the box" is right to 1 to 2 px, because a width does not depend on the camera tilt.

## Where the detector takes a bottom (or a size) from the top row today

| where (`detector.py`) | what is taken from the top row | is the barrel's whole width seen there? |
|---|---|---|
| `resolve_bottom` (step 1 pieces) | the bottom, when the seen bottom is further than 15 % of the height (min 4 px) from it | usually yes (the piece passed 0.4 to 1.6 widths), but a piece only becomes a box when it reaches the frame bottom (nothing is inferred) or is too far to show a stripe (under about 17 px wide) |
| `expected_width_px` (step 1) | the expected width, only when the bottom is below the frame | yes; near barrels, where the bias is about 0 |
| `caps_behind`, the size tests | the expected width, height and upper-body height of the cap | not needed: these are gates with wide margins (0.4 to 1.2, 0.5 to 1 + 15 %) |
| `caps_behind`, a cap seen whole (at least 0.8 of a barrel wide) | nothing: the bottom is top + the height of a barrel as wide as the cap | yes, and it is used |
| `caps_behind`, a **narrow** cap (one side hidden by a found barrel or the frame) | **the bottom**; a seen end of its own color replaces it only within 15 % of the height (min 4 px) of it | **no** |
| `caps_behind`, "what hides the rest is a barrel" | compares that bottom with the front barrel's bottom | follows the row above |

Not from the top row: a stripe barrel's top and bottom (`barrel_from_stripe`) come from the **stripe's** row when the
seen edge disagrees, and the "stands nearer" test of `side_hidden` uses that same stripe-row bottom.

## Baseline (`results/2026-11-19_det_bottom/step1_baseline/`, git 6e027a5, the defaults of `wip/detector-side`)

`base` = `stripe_join`, `cap_behind`, `side_hidden`, `seam_height` on. Found / barrels (false boxes), v2 rule, train
frames only.

| level | scenario | base |
|---|---|---|
| 1 | perfect masks, HOME | 28 / 29 (0) |
| 2 | light / medium / heavy damage (5 seeds) | 141 / 145 (0); 99 (1); 21 (0) |
| 3a | CAMPUS, adopted color model | 35 / 35 (0) |
| 3b | BLACK, thresholds from the frame's labels | 19 / 26 (2) |
| 3c | wood, cool lamp, label thresholds (report only) | 27 / 42 (7) |

Eval table (found / missed / false): HOME 27 / 2 / 0; CAMPUS 35 / 0 / 0; BLACK 5 / 21 / 1; Dave 12 / 22 / 2; no box
on any negative frame.

**The census** (`census.py`, `step1_baseline/bottom_edges.md`): of the 62 boxes the baseline draws on HOME and
CAMPUS, 55 have a **seen** bottom, 5 end at the frame edge, 2 are caps seen whole (one bottom from the width, one
seen). **No box's bottom comes from the top row, and none from the stripe row.** All 62 are inside the v2 bottom
tolerance; median distance from the hand-drawn bottom 1 px (HOME) and 2 px (CAMPUS). On the same boxes, had the
bottom been worked out from the top row, the median distance would be 7.0 px (HOME) and 5.8 px (CAMPUS).

So the top-row bottom is in no box that is drawn today. It acts in one place only: as the reference a narrow
cap's seen bottom is compared with, and in the "stands nearer" comparison after it.

## The known case: HOME `cluster_01`, the left orange barrel (eval-table segmentation)

Cap: columns 315 to 347 (32 px), rows 118 to 136. Top row 118 gives a barrel 50.7 px wide and 55.0 tall, bottom
173.0. The cap is 0.63 of a barrel wide; the found blue barrel (326, 120, 383, 173) hides its right side. Its own
orange is seen to the left of the blue barrel's box (columns 316 to 331), ending at row 162 (bottom 163). 173 - 163
= 10 px, tolerance 0.15 × 55 = 8.25 px: refused, the bottom stays 173; the blue barrel's bottom (173) is not lower
than 173, so "nothing stands in front of it" and the cap is dropped. Hand-drawn box: (313, 115, 356, 164).

What honest information exists for this barrel's bottom:

1. **The seen end of its own color beside the front barrel** (row 162 or 163). It is a measurement, 1 to 2 px from
   the hand-drawn 164. It is refused today only because it is compared with a reference that is itself 9 px low.
2. **The width that is seen**: the barrel is at least 32 px wide, so at least as tall as a barrel 32 px wide: 34.9
   px, bottom not above row 152.9. A lower bound that does not depend on the tilt.
3. **The front barrel**: a barrel standing behind another has its bottom above the front one's (173). An upper
   bound, and one the top-row estimate already touches.

The whole width is not seen, so "height from width" gives a bound (2), not the bottom. A simple rule uses 1 inside
the bounds 2 and the top-row estimate.

## The change (one rule, a `DetConfig` switch `cap_seen_bottom`, off until it passes)

**For a narrow cap whose seen end today's test does not accept: if its own color, read in the cap's columns that
lie outside the boxes of found barrels standing nearer, is seen ending between the bottom of a barrel only as wide
as the seen cap and the top-row bottom plus the usual tolerance, that seen end is its bottom.**

- "Narrow cap", "found barrel standing nearer", "seen ending" (no pixel of the color in the 3 rows below) and the
  tolerance (15 % of the height, min 4 px) are today's, unchanged. The lower limit is the tilt-free bound 2 above.
  No new number.
- Only columns beside the front barrel are read, because inside its box that color is the front barrel's stripe.
- Today's test runs first and is unchanged, so the rule acts only where today the bottom comes from the top row.
  A cap seen whole is not touched.
- Everything after it is unchanged ("at least half of the box below the cap inside nearer found barrels", the
  duplicate test).

Expected: HOME `cluster_01` left orange found with a bottom at about row 162 (HOME 27 → 28 of 29). Nothing else
moves on HOME or CAMPUS (the census: no other box depends on the top row). Risks, written now: (i) the seen end is
where something that is not a barrel hides the lower body, so the box is drawn short; (ii) a narrow cap that was
rightly dropped as "not hidden" now passes with a shorter box: a new wrong box would show on the damaged masks, the
black table or the recordings.

Not changed, with the reason: a narrow cap with **no** seen end keeps the top-row bottom (nothing better is seen;
clamping it above the front barrel's bottom would draw a bottom up to 8 px low, a miss and a false box under the v2
rule). Step 1's `resolve_bottom` is left as it is: no box drawn on HOME or CAMPUS takes its bottom from it.

## Arms

`base`; `bottom` (`cap_seen_bottom` on).

## Acceptance rule (fixed now)

`bottom` passes when all of these hold against `base`:

- **(a) Never regress.** `python barrels/tools/report.py --cand-det <bottom> --base-model default` (written by
  `run.py` as `never_regress.md`): no scenario row of HOME (leave-one-scene-out) or CAMPUS loses a found barrel or
  gains a false box; no box on any negative frame of any set. The black table, the orange wood table and Dave's
  set are reported rows and decide nothing.
- **(b) Levels.** Perfect masks, light, medium and heavy damage, campus (3a), black with label thresholds (3b):
  found not lower, false boxes not higher, at each.
- **(c) Recordings** (`recordings.py --rec <data/recordings>`): every box that appears or disappears on the campus
  clips is looked at on a contact sheet; no new box on something that is not a barrel or half off its barrel, and
  a box that disappears must have been wrong. The black and wood clips are described, not judged.
- **(d) Reported, decides nothing:** median distance of the bottom edge from the hand-drawn one and the number of
  boxes inside the v2 bottom tolerance, HOME and CAMPUS, `base` against `bottom` (`census.py`).

If it passes: `cap_seen_bottom` on by default on `wip/detector-bottom`. If not: off, and the report says so. The
rule is not re-picked after the results. No second round. The test frames are never opened.
