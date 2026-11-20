# Verdict against the pre-registered rule (round 2; round 1 is in `round1/` and in the PREREG addendum)

Rule: `experiments/2026-11-20_occl_pin/PREREG.md` and its addendum. Numbers: `scorecard.md`, `scorecard_check.md`,
`summary.md`, `cells.csv`, `real.md`, `levels/summary.md`, `levels/never_regress.md`, `recordings.md`, `by_eye.md`.
`base` = the defaults of `wip/detector-occl` (git 085c99d). Found / barrels (false boxes).

| | base | **pin** | pin+thin |
|---|---|---|---|
| scorecard, found of 3888 scenes | 2417 | **2445** | 2556 |
| scorecard, box in the right place | 2532 | **2560** | 2671 |
| scorecard, boxes where no barrel is | 45 | **45** | 45 |
| scorecard, too big, of the right-place boxes | 104 (4.11 %) | **102 (3.98 %)** | 104 (3.89 %) |
| scorecard, cells with found lower / right place lower | | **0 / 0** | 0 / 0 |
| the 12 targeted cells together, of 1300 | 593 | **619** | 702 |
| 1 perfect HOME masks | 28 / 29 (0) | **same** | same |
| 2 light / medium / heavy, of 145 | 143 (0) / 99 (1) / 21 (0) | **same** | same |
| 3a CAMPUS / 3b BLACK, label thresholds | 35 / 35 (0); 19 / 26 (2) | **same** | same |
| eval table HOME, CAMPUS (found / missed / false) | 28 / 1 / 0; 35 / 0 / 0 | **same** | same |
| eval table BLACK, wood, Dave (report only) | 5 / 21 / 1; ...; 12 / 22 / 3 | same | same |
| boxes on negative frames, any set | 0 | **0** | 0 |
| recordings (337 frames, 506 boxes): appearing / disappearing | | **0 / 0** | 0 / 0 |

The targeted cells, found of n:

| what hides the barrel | hidden | n | base | pin | pin+thin |
|---|---|---|---|---|---|
| a straight upright edge | 50 % | 100 | 82 | **90** | 90 |
| a straight upright edge | 75 % | 100 | 0 | 2 | 28 |
| a slanted edge | 50 % | 200 | 154 | **170** | 170 |
| a slanted edge | 75 % | 200 | 0 | 0 | **0** |
| both sides | 50 % | 50 | 49 | 49 | 49 |
| both sides | 75 % | 50 | **0** | **0** | **0** |
| the frame edge | 50 % | 100 | 99 | 99 | 99 |
| the frame edge | 75 % | 100 | 3 | 3 | 29 |
| a block of the body color | 50 % | 100 | 99 | 99 | 99 |
| a block of the body color | 75 % | 100 | 5 | 5 | 36 |
| a block of the stripe color | 50 % | 100 | 99 | 99 | 99 |
| a block of the stripe color | 75 % | 100 | 3 | 3 | 3 |

Other cells that move: a post at 50 %: 9 → 11 → 31 of 50, at 75 %: 0 → 0 → 5; other color beside, 75 %: 49 → 49 → 50;
same color beside and lower, 75 %: 26 → 26 → 28.

| clause | pin | pin+thin |
|---|---|---|
| 1 (a) eval table: no HOME or CAMPUS row loses a barrel or gains a false box; nothing on a negative frame | pass | pass |
| 1 (b) scorecard: boxes where no barrel is not above 45 | pass (45) | pass (45) |
| 1 (c) damage: false boxes not above 0 / 1 / 0; found not lower at any level | pass | pass |
| 1 (d) scorecard: share of too-big boxes not above 4.11 % | pass (3.98 %) | pass (3.89 %) |
| 2 recordings by eye | pass (no frame changes) | pass (no frame changes) |
| 3 the 12 targeted cells together higher; no cell of the card lower | pass (593 → 619) | pass (593 → 702) |
| 3 the committed cells each higher | pass (82 → 90, 154 → 170) | **no: slanted edge at 75 % stays 0** |

**`pin` passes: `pin_outline` is on by default on `wip/occl-pin`. `pin+thin` fails one part of clause 3 by the
letter (a cell I committed to and should not have): `pin_thin` stays off behind its switch.**

## Said first, as promised: what did not improve

- **Both sides cut, 75 % hidden: 0 of 50, unchanged, with either switch.** The census found no cue for a piece
  from the middle of a barrel (the outline knew in 4 of 150 scenes in round 1's census, and the end rule never
  speaks there). Both sides at 50 %: 49 of 50, the centred box, right only because the benchmark cuts both sides
  equally.
- **A slanted edge at 75 %: 0 of 200.** The slant cuts into the corner itself.
- **A block of the stripe color at 75 %: 3 of 100.** The block hides the lower body in the columns where the
  barrel's top still shows above it: the seen part is not a barrel's outline.
- At 75 % hidden by a straight edge, the frame or a block of the body color, `pin_thin` finds 28 to 36 of 100: the
  barrel's own corner follows the outline to 0.05 of its height in about a third of the scenes. The rest are
  misses, not wrong boxes.

## What is on, and what it does

`pin_outline`: a partly seen stripe that no side reason places (before: centred on what is seen, or no box under
0.4 of a barrel) gets a box one barrel wide from the end of the seen part that follows the barrel's outline, when
exactly one end does. On the scorecard it changes the box in the straight-edge and slanted-edge cells at 25 and
50 % hidden: found 2417 → 2445, and the boxes it places sit on the barrel's own side (HOME `core_02`: overlap 0.59
→ 0.98). It changes no box on HOME, CAMPUS, BLACK, wood, Dave's frames, the damaged masks or the 337 recorded
frames: on real frames today no partly seen stripe without a side reason has a clean corner.

## What is off, and exactly what stands between it and a pass

`pin_thin` finds 111 more scenes (2445 → 2556) with no box where no barrel is added, no cell lower, a smaller share
of too-big boxes, and no change on any real frame or damaged mask. It fails because the PREREG committed it to
raising the slanted edge at 75 %, which the end census (run before round 2) already showed it would not. Nothing
measured speaks against switching it on; the rule as written does.

Round 1's version of both switches (the outline slid over the seen part, the mean of the three lines) found more
(2699 with both) and was fooled by slanted cuts (6 barrels lost, 3 false boxes): `round1/`, `slant_census.md`.

## Two rounds, honestly

Round 2 is a different way of asking the same outline, designed after seeing round 1 on the train scorecard. The
limit `pin_good` (0.05) was kept from the PREREG; the window (half a lid's width) and "the largest of the three
lines" were chosen from `end_census.md` on the same 50 barrels the scorecard uses. The test frames are untouched.
