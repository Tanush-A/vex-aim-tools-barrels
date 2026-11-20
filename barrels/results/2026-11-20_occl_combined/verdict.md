# Verdict: the occlusion work combined, against the pre-registered rule

Rule: `experiments/2026-11-20_occl_combined/PREREG.md` and its addendum. Numbers: `round2/` (`check.md`, `scorecard.md`,
`summary.md`, `cells.csv`, `levels.md`, `eval.md`, `real.md`, `interactions.md`), `round1/`, `sanity/`, `alone/`,
`by_eye.md`, `verify*/`, `census_slice.md`. The one page: `scorecard.md`. The logic: `walkthrough.md`.
Train frames only; no test frame was opened. Found / missed / false, or found (false boxes).

## The result

**On by default on `wip/occl-combined`:** everything `wip/detector-occl` had on (`side_hidden`, `seam_height`,
`cap_seen_bottom`, `edge_check`, `cap_same`), plus `half_stripe`, `half_thin`, `post_pair`, `stripe_wide`, `cap_low`
(occl-vertical), `pin_outline` and **`pin_thin`** (occl-pin). This is the arm `reduced+thin`; the code's defaults are
exactly that arm (checked).

**Off:** `slice_behind` (failed clause (c) by one box; below), `slice_box`, `cover_unpinned`, `stripe_two` (Tanush's
decision of 2026-11-19; they also fail (b) and (c)), and the stencil verifier (fails its rule; below).

| | `before` (`barrels` today) | `stack` (`wip/detector-occl`) | **`reduced+thin` (the default)** | `combined+thin` (with `slice_behind`) | `combined+cover` (report only) |
|---|---|---|---|---|---|
| scorecard, found of 3888 | 2153 | 2417 | **2737** | 2825 | 3261 |
| scorecard, box in the right place | 2318 | 2532 | **2854** | 2944 | 3419 |
| scorecard, boxes where no barrel is | 88 | 45 | **45** | 45 | 58 |
| scorecard, cells lower than `stack` (of 45) | 24 | | **0** | 0 | 0 |
| right-place boxes too small / right / too big | 157 / 1998 / 163 | 299 / 2129 / 104 | **324 / 2445 / 85** | 347 / 2507 / 90 | 362 / 2421 / 636 |
| eval table HOME | 27 / 2 / 0 | 28 / 1 / 0 | **28 / 1 / 0** | same | same |
| eval table CAMPUS | 34 / 1 / 0 | 35 / 0 / 0 | **35 / 0 / 0** | same | same |
| boxes on negative frames, any set | 0 | 0 | **0** | 0 | 0 |
| black table (report only) | 3 / 23 / 1 | 5 / 21 / 1 | 5 / 21 / 1 | same | 7 / 19 / 1 |
| wood, 9 lamp settings, 189 barrels (report only): found, false | 7, 4 | 7, 4 | 7, 5 | 7, 5 | 7, 5 |
| Dave's frames (indicative) | 12 / 22 / 2 | 12 / 22 / 3 | 12 / 22 / 4 | same | 12 / 22 / 3 |
| perfect HOME masks, of 29 | 28 (0) | 28 (0) | **28 (0)** | 28 (0) | 28 (0) |
| typical, of 145 / of 580 | 140 (0) / 560 (0) | 145 (0) / 579 (0) | **145 (0) / 579 (0)** | same | same |
| bad day without the stripe patch | 140 (1) / 563 (4) | 144 (0) / 577 (0) | **144 (0) / 577 (0)** | same | same |
| light | 141 (0) / 564 (5) | 143 (0) / 574 (0) | **143 (0) / 574 (0)** | same | 143 (0) / 572 (2) |
| bad day (reported; limit double) | 115 (15) / 454 (75) | 135 (3) / 547 (5) | **135 (3) / 547 (5)** | 136 (3) / 555 (6) | 139 (4) / 560 (17) |
| medium (reported; limit double) | 64 (22) / 242 (87) | 99 (1) / 388 (3) | **102 (1) / 400 (3)** | 115 (1) / 444 (**7**) | 125 (4) / 481 (21) |
| heavy (report only) | 13 (2) / 47 (5) | 21 (0) / 89 (0) | 21 (0) / 89 (0) | same | 24 (0) / 98 (0) |
| worst seen (report only) | 41 (21) / 154 (72) | 84 (2) / 337 (6) | 95 (2) / 378 (6) | 105 (2) / 419 (10) | 115 (6) / 463 (17) |
| real occluded or cut barrels: HOME, CAMPUS (of 10, 3) | 8, 2 | 9, 3 | **9, 3** | same | same |
| campus clips against `stack`: boxes appearing (wrong); disappearing | | | **0; 0** | 1 (0); 0 | 1 (0); 0 |

## The rule, clause by clause (`round2/check.md`)

| clause | `reduced` | **`reduced+thin`** | `combined`, `combined+thin` | `combined+cover` |
|---|---|---|---|---|
| (a) no HOME or CAMPUS row loses a barrel or gains a false box; no box on a negative frame | pass | **pass** | pass | pass |
| (b) scorecard: boxes where no barrel is not above 45; no cell lower than `stack` | pass (2649; 45) | **pass (2737; 45)** | pass (2764, 2825; 45) | **no** (58) |
| (c) false boxes not above `stack` on perfect, typical, bad day without the stripe patch, light (5 and 20 seeds) | pass | **pass** | pass | **no** (light, 20 seeds: 2) |
| (c) bad day and medium: not more than double `stack` (5 and 20 seeds) | pass | **pass** | **no: medium, 20 seeds, 7 against 3** | **no** |
| (c) campus clips: no new wrong box against `stack` | pass (no frame changes) | **pass (no frame changes)** | pass (1 box, on a barrel) | pass |
| `pin_thin` on top: no cell lower than without it; false boxes not higher at any judged level | | **pass** (2649 → 2737) | | |

## Why `slice_behind` is off, and exactly what stands between it and a pass

`combined` (round 1) passed everything except one count: **medium damage with 20 seeds, 7 false boxes against
`stack`'s 3; the limit is 6.** With 5 seeds, the protocol of every earlier test and of occl-vertical's own verdict, it
is 1 against 1. All four extra boxes, the one extra at bad day (6 against 5, inside the limit) and the four at "worst
seen" are drawn by `slices_behind`; occl-vertical's arm alone draws the same boxes, so this is the rule itself and not
an interaction. By the rule as written the switch is taken out.

What it costs to leave it off (`reduced+thin` → `combined+thin`): 2737 → 2825 scenes; the frame edge at three quarters
29 → 87 of 100; same color beside and lower at three quarters 29 → 44; other color beside 50 → 60; medium damage found
400 → 444 of 580; one right box on the campus clips (`r3_enter_leave` 013, a barrel entering at the frame edge).

A lead, measured and not built (`census_slice.md`, report only): of the 219 boxes `slices_behind` draws on the scorecard
and on 1920 damaged masks, 9 are wrong, and **all 9 lean on "a found barrel standing nearer"; of the 129 that lean on
the frame edge none is wrong.** A `slice_behind` that takes only the frame edge as its reason would keep the frame-edge
cell and the campus box. That is a change to a rule chosen after seeing these numbers, so it needs its own
pre-registered run.

**This hinges on a choice made in this experiment's PREREG: judging the damaged masks with 20 seeds as well as 5.**
Tanush's rule said "not more than double `stack`'s" without a seed count. If he reads it with 5 seeds, `combined+thin`
passes every clause and `slice_behind` goes on (one line in `DetConfig`).

## Interactions (the task's question 1)

- **The six of occl-vertical + `pin_outline`: none.** `combined` finds exactly the scenes that either branch finds
  alone (2738 and 2445 alone, 2764 by either, 2764 together): 0 scenes lost, 0 with an extra box. Same on the damage
  levels (`alone/levels.md`), the eval table and the recordings. Three of the four interactions predicted from reading
  the code did not happen.
- **`pin_thin` × `slice_behind` (predicted): real, fixed.** Round 1: 87 scenes lost (2738 found against 2825 by either
  alone), medium damage 115 → 103, one campus box gone; no wrong box added. Cause: `pin_thin` lowers the finder's width
  floor, so the narrow pieces `slices_behind` is given ("refused for their width") became thin stripes instead and were
  dropped. Fix (`detector.py`, two lines; tests in `tests/test_detector_combined.py`): the finder hands a piece under
  the old floor to the left-over rules whether or not the lower floor also lets it into the stripe step, and a thin
  stripe left without a box is not handed over twice. Round 2: `combined+thin` 2825 = by either alone, 0 lost, 0 extra.
  With `slice_behind` off the fix changes no default number; it is there so the two can be on together.
- **The order at the end of `detect`** stays stripe step (with the outline) → stripeless pieces → caps → pairs →
  (slices behind) → half stripes: each rule after what it leans on; the left-over rules last, each adding a box only
  where no box of that color is.

## The stencil as a verifier: OFF

Limit by the registered rule (HOME hand masks, HOME leave one scene out, the 10 clutter negatives; lowest right box
0.182, margin 0.02): **0.16** for `combined`, `reduced` and `reduced+thin` alike (`verify_calibration*.md`).

| against its base | `combined+verify` | `combined+verify2` (boxes of `half_stripes` not checked) | on `reduced+thin` |
|---|---|---|---|
| removes wrong boxes | yes: scorecard 45 → 8; wood 5 → 0 or 1; Dave 4 → 0; black 1 → 0; medium (20 seeds) 7 → 1; 11 wrong boxes on the campus clips | the same | see `verify_reduced+thin/` |
| HOME | 28 / 1 / 0, unchanged | unchanged | unchanged |
| **CAMPUS** | **35 → 33 found** (`clutter_02` blue, score 0.111; `occl_02` blue, score 0.065) | the same | **35 → 33** |
| campus clips, right boxes lost | 3 | 3 | 2 |
| perfect masks, typical | nothing lost | nothing lost | |
| light / medium found (of 580) | 574 → 516 / 444 → 209 | the same | |
| scorecard found; cells that drop by more than 1 | 2764 → 2419; 23 cells | 2764 → 2501; 22 cells | |

It fails three clauses of its rule (right boxes lost on CAMPUS and on the campus clips; scorecard cells). It is the
only thing measured here that removes the standing wrong boxes (the 11 on the campus clips, every wrong box on wood
and on Dave's frames, 37 of the 45 on the scorecard), and it does so by also removing every barrel that is seen a
third or less: the stencil scores what is painted, and a partly hidden barrel and a wrong box both have little
painted. Report only (`verify/verify_curve.md`, not used for anything): no limit separates them; at 0.05 a verifier
drops 27 of the 45 scorecard boxes where no barrel is and no right box on HOME or CAMPUS, but 133 right scorecard
boxes (82 of them every box `half_stripes` draws); the lowest right CAMPUS box scores 0.065.

## What is still not handled

| case | found now | can the painted pixels decide? |
|---|---|---|
| three quarters hidden from above, or from below | 0, 1 of 50 | no: a top or a base alone is one row and a width; the thing in front is unpainted, like the table |
| both sides cut, three quarters hidden | 0 of 50 | no: no end of what is seen is the barrel's own |
| a slanted edge, three quarters | 0 of 200 | no with this cue: the cut goes through the corner the outline rule reads |
| a block of the stripe color, three quarters | 3 of 100 | unclear: the block hides the lower body where the top still shows |
| a straight edge, the frame edge or a block of body color, three quarters | 28, 29, 36 of 100 | partly: only with a clean own corner; the frame-edge case is 87 with `slice_behind` |
| a post, three quarters | 11 of 50 | partly: the slices must reach the barrel's top and bottom |
| same color straight in front, half / three quarters | 29 of 48 / 8 of 49 | perhaps: one blob, one stripe; the back top is 0.19 H above the front one against a tolerance of 0.15 |
| same color beside at the same rows, three quarters | 17 of 100 | no: the joined stripe is 1.10 barrels wide and one barrel alone reaches 1.04 |
| the wedge barrel of HOME `cluster_01` | no box, on purpose | no: nothing of it can be measured |
| wrong boxes on a hand or a chair behind a barrel (11 in the campus clips, before and after) | | not by these rules; the verifier removes them and fails elsewhere |

One cell is lower than before the occlusion work: same color straight in front at a quarter, 45 → 44 of 47; it came
with `stack` (2026-11-19) and is unchanged here.

## Could not be verified

- Every scorecard number is simulated on the mask. No real train frame exists of a barrel hidden from above or below
  by a thing that is not a barrel, behind a post, behind a straight upright edge, or beside a barrel of its own
  color: `half_stripe`, `post_pair`, `stripe_wide`, `pin_outline` and `pin_thin` change **no box on any real frame or
  recording** (HOME, CAMPUS, black, the 337 recorded frames), so on real pixels they are untested, not confirmed.
- The recordings were judged by one look at contact sheets; `r4` 020 is a judgment call.
- The damage levels are seeded simulations on 16 hand masks; "typical" and "bad day" were measured on 12 barrels.
- Time per frame: `timing.md`.
