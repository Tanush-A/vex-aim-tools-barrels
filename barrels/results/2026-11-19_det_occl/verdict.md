# Verdict against the pre-registered rule (round 2; round 1 is in `round1/` and in the PREREG addendum)

Rule: `experiments/2026-11-19_det_occl/PREREG.md` and its addendum. Numbers: `scorecard.md`, `scorecard_check.md`,
`summary.md`, `cells.csv`, `real.md`, `levels/summary.md`, `levels/never_regress.md`, `recordings.md`, `by_eye.md`.
`base` = the defaults of `wip/detector-bottom`. Found / barrels (false boxes).

| | base | slice | slice+cover | two | edge | cap | **edge+cap** | all | all-cover |
|---|---|---|---|---|---|---|---|---|---|
| scorecard, found of 3888 scenes | 2401 | 3068 | 3068 | 2471 | 2412 | 2406 | **2417** | 3155 | 3155 |
| scorecard, box in the right place | 2521 | 3231 | 3232 | 2588 | 2521 | 2532 | **2532** | 3312 | 3311 |
| scorecard, boxes where no barrel is | 63 | 82 | 82 | 66 | 45 | 63 | **45** | 58 | 58 |
| scorecard, cells with found lower / right place lower | | 0 / 1 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | **0 / 0** | 0 / 0 | 0 / 0 |
| 1 perfect HOME masks | 28 / 29 (0) | same | same | same | same | same | **same** | same | same |
| 2 light, of 145 | 143 (0) | same | same | same | same | same | **same** | same | same |
| 2 medium, of 145 | 99 (1) | 124 (4) | 124 (4) | 99 (1) | 99 (1) | 99 (1) | **99 (1)** | 124 (4) | 124 (4) |
| 2 heavy, of 145 | 21 (0) | 24 (0) | 24 (0) | 21 (0) | 21 (0) | 21 (0) | **21 (0)** | 24 (0) | 24 (0) |
| 3a CAMPUS | 35 / 35 (0) | same | same | same | same | same | **same** | same | same |
| 3b BLACK, label thresholds | 19 / 26 (2) | same | same | same | same | same | **same** | same | same |
| eval table HOME, found / missed / false | 28 / 1 / 0 | same | same | same | same | same | **same** | same | same |
| eval table CAMPUS | 35 / 0 / 0 | same | same | same | same | same | **same** | same | same |
| eval table BLACK (report only) | 5 / 21 / 1 | 7 / 19 / 1 | 7 / 19 / 1 | same | same | same | same | 7 / 19 / 1 | 7 / 19 / 1 |
| eval table Dave (indicative) | 12 / 22 / 2 | same | same | same | same | 12 / 22 / 3 | 12 / 22 / 3 | 12 / 22 / 3 | 12 / 22 / 3 |
| campus clips: boxes appearing / of them wrong; disappearing | | 1 / 0; 0 | 1 / 0; 0 | 0 | 0 | 0 | **0** | 1 / 0; 0 | 1 / 0; 0 |
| black clip (report only): appearing | | 24 | 24 | 0 | 0 | 0 | 0 | 24 | 24 |

| rule | slice, slice+cover | two | edge | cap | **edge+cap** | all, all-cover |
|---|---|---|---|---|---|---|
| 1 never regress (every HOME and CAMPUS scenario row; no box on any negative frame of any set) | pass | pass | pass | pass | **pass** | pass |
| 2 earlier levels: found not lower, false boxes not higher, at each | **no** (medium: false 1 → 4) | pass | pass | pass | **pass** | **no** (medium: false 1 → 4) |
| 3 campus clips by eye | pass | pass | pass | pass | **pass** | pass |
| 4 scorecard: no cell lower, false boxes not more, targets higher | **no** (false 63 → 82; one cell's right-place count 30 → 29) | **no** (false 63 → 66) | pass | pass | **pass** | pass |

**`edge+cap` passes. By the adoption order of the addendum (`all` fails, `all-cover` fails, then the switches that
pass alone, combined), `edge_check` and `cap_same` are on by default on `wip/detector-occl`. `slice_box`,
`cover_unpinned` and `stripe_two` stay off behind their switches.**

## What is on, and what it does

- `edge_check`: 18 boxes of the wrong color gone from the scorecard (a barrel of the other color straight in front,
  a quarter hidden: boxes where no barrel is 21 → 3) and that cell goes from 29 to 39 of 47 found (the bottom is no
  longer cut short where it ends against the front barrel). Nothing changes on HOME, CAMPUS, the damaged masks or the
  recordings.
- `cap_same`: a barrel of the same color straight in front, half hidden: 25 → 29 of 48 found, 30 → 37 in the right
  place. Nothing else moves; one more wrong box on Dave's frames (indicative, report only).
- Together: found 2401 → 2417 of 3888, boxes where no barrel is 63 → 45.

## What is off, and exactly what stands between it and a pass

`all` (every switch) finds 3155 of 3888 against 2401, with fewer boxes where no barrel is (58 against 63), no cell of
the scorecard lower, no HOME or CAMPUS row changed, and one new box on the campus clips, which is right. It fails
one clause of one rule:

- **Rule 2, medium damage: false boxes 1 → 4** (found 99 → 124 of 145). The three new ones are on barrels that are
  not hidden at all, where the damage left a piece of stripe with the body gone beside it: HOME `cluster_02` seed 4
  (307, 121, 387, 168) and `touch_02` seed 3 (236, 123, 323, 172) are cover boxes 1.8 barrels wide; `cluster_02` seed 2
  (328, 120, 377, 169) is a barrel wide and half a barrel off. Each overlaps the hand-drawn box by less than half, so
  it counts as a miss and a false box. This is the risk written in the PREREG: erring large turns a damaged barrel
  into a wrong box.

Alone, the two parts fail differently:

- `slice_box` alone: the scorecard's boxes where no barrel is go 63 → 82. 19 are new: slices that are full by accident.
  12 of them are on the two far barrels of HOME `far_02` as the color model segments them (fingers touch the barrels
  in that frame), 3 on `cluster_02`, 4 on three other barrels. Together with `edge_check` the count is under 63.
  Also one cell's right-place count goes 30 → 29 (same color straight in front, half hidden).
- `stripe_two` alone: 63 → 66. All three are the near barrel of campus `plain_01` behind or beside a pasted barrel,
  cut in two. It finds 70 more barrels (same color beside, half hidden: 36 → 88 of 100 with everything on).

`cover_unpinned` (the cover box for a stripe 0.4 wide or wider with no reason on either side, instead of the centred
box) widens the box in 438 of the 3888 scenes and changes a count in 3 of them. It decides nothing here; it stays off
with `slice_box`.

How large the boxes are with everything on: of the right-place boxes on the scorecard, too small / about right / too
big goes from 305 / 2114 / 102 (`base`) to 357 / 2062 / 893. Three quarters hidden by a straight edge: 88 boxes in the
right place, median width 1.78 x the true width, mean overlap 0.53. The boxes hold the barrel and are wide, as
designed.

## Not handled by any arm

- **Hidden from above or from below by half or more** (2 and 1 of 50): no band with body color above and below is
  left. A top alone is boxed only behind a found barrel.
- **A post hiding three quarters** (1 of 50): two slivers a few pixels wide.
- **A barrel of the other color straight in front, three quarters hidden** (17 of 49): the back barrel's top is
  shorter than half an upper body, or its stripe has run into the front barrel's body.
- **A barrel of the same color straight in front, half or more hidden** (29 of 48, 2 of 49), and **beside it with
  the stripes at the same rows, three quarters hidden** (24 of 100 with everything on): one blob, one joined stripe
  under 1.2 barrels wide.
- **Real frames:** nothing changes on the 25 occluded or cut barrels of HOME, CAMPUS and BLACK (`real.md`): HOME 9 of
  10 (the wedge of `cluster_01` has no box, on purpose), CAMPUS 3 of 3, BLACK 2 of 12 (glare: the barrels are not
  painted).
