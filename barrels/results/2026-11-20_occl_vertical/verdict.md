# Verdict against the pre-registered rule (round 2; round 1 is in `round1/` and in the PREREG addendum)

Rule: `experiments/2026-11-20_occl_vertical/PREREG.md` and its addendum. Numbers: `scorecard.md`, `scorecard_check.md`,
`summary.md`, `cells.csv`, `real.md`, `amounts.md`, `levels/summary.md`, `levels/never_regress.md`, `recordings.md`,
`by_eye.md`. `base` = the defaults of `wip/detector-occl` (git 085c99d). Found / barrels (false boxes).

| | base | half | half+thin | post | wide | behind | caplow | **all** |
|---|---|---|---|---|---|---|---|---|
| scorecard, found of 3888 scenes | 2417 | 2457 | 2500 | 2458 | 2487 | 2532 | 2429 | **2738** |
| scorecard, box in the right place | 2532 | 2572 | 2615 | 2575 | 2599 | 2649 | 2547 | **2857** |
| scorecard, boxes where no barrel is | 45 | 45 | 45 | 45 | 45 | 45 | 45 | **45** |
| scorecard, cells with found lower / right place lower | | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | **0 / 0** |
| perfect HOME masks | 28 / 29 (0) | same | same | same | same | same | same | **same** |
| light damage, of 145 | 143 (0) | same | same | same | same | same | same | **same** |
| medium damage, of 145 | 99 (1) | 99 (1) | 99 (1) | 102 (1) | 99 (1) | 114 (1) | 99 (1) | **115 (1)** |
| heavy damage, of 145 | 21 (0) | same | same | same | same | same | same | **same** |
| CAMPUS | 35 / 35 (0) | same | same | same | same | same | same | **same** |
| BLACK, label thresholds (report only) | 19 / 26 (2) | same | same | same | same | same | same | same |
| eval table HOME, found / missed / false | 28 / 1 / 0 | same | same | same | same | same | same | **same** |
| eval table CAMPUS | 35 / 0 / 0 | same | same | same | same | same | same | **same** |
| boxes on negative frames, any set | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** |
| eval table wood, 90 frames (report only): false | 4 | 5 | 5 | 4 | 4 | 4 | 4 | 5 |
| eval table Dave (indicative) | 12 / 22 / 3 | same | same | same | same | same | 12 / 22 / 4 | 12 / 22 / 4 |
| campus clips: boxes appearing / of them wrong; disappearing | | 0 | 0 | 0 | 0 | 1 / 0; 0 | 0 | **1 / 0; 0** |
| black clip, wood clip (report only) | | no change | no change | no change | no change | no change | no change | no change |

| rule | every arm |
|---|---|
| 1 eval table: no HOME or CAMPUS scenario row loses a barrel or gains a false box; no box on a negative frame | pass |
| 2 damaged masks: false boxes not above 0 / 1 / 0; found not lower at any level | pass |
| 3 scorecard: boxes where no barrel is not above 45; no cell lower; the target cells higher | pass |
| 4 campus clips by eye: no new wrong box | pass |

**`all` passes. By the adoption order, `half_stripe`, `half_thin`, `post_pair`, `stripe_wide`, `slice_behind` and `cap_low`
are on by default on `wip/occl-vertical`.** Nothing stays off from this experiment.

## The seven rows (found at 25 / 50 / 75 % hidden, before → now)

| what hides the barrel | before | now | by | verdict |
|---|---|---|---|---|
| from above (of 50) | 50 / 2 / 0 | 50 / 45 / 0 | `half_stripe`, `half_thin` | handled until about 0.55 of the height is hidden; a base alone (75 %) is not measurable |
| from below (of 50) | 49 / 1 / 1 | 49 / 40 / 1 | `half_stripe`, `half_thin` | handled until about half is hidden (a line of stripe must show); a top alone (75 %) is not measurable |
| a post across the middle (of 50) | 49 / 9 / 0 | 49 / 41 / 9 | `post_pair` | handled while the slices reach the top and the bottom (to about 0.6 of the width; 9 of 50 at 0.75) |
| OTHER color straight in front (of 47 / 48 / 49) | 39 / 38 / 17 | 40 / 38 / 22 | `cap_low` | 75 %: a threshold at its edge; 5 more; the rest have a box whose hidden bottom is off, or a top under 0.4 of an upper body |
| SAME color straight in front (of 47 / 48 / 49) | 44 / 29 / 2 | 44 / 29 / 8 | `cap_low` | 50 % unchanged (hidden bottoms 4 to 17 px off; front box takes the back barrel's top); 75 %: 0.19 of a height above a top whose tolerance is 0.15: not measurable |
| SAME color beside (of 100) | 81 / 36 / 16 | 96 / 88 / 18 | `stripe_wide` | handled at a quarter and a half; at 75 % the joined stripe is 1.10 barrels wide and one barrel reaches 1.04: not measurable |
| SAME color beside and lower (of 100) | 91 / 85 / 26 | 91 / 87 / 42 | `slice_behind` | 75 %: 16 more; the rest are slices that are not full or have no found barrel beside them |

## What round 2 changed against round 1

`post` 46 → 45 and `behind` 51 → 45 boxes where no barrel is; `behind` at medium damage 2 → 1 false boxes; the wrong-color
boxes of `half` in the report-only table (6 at 35 % hidden from below, 1 at 30 %) are gone and the right ones are drawn
(35 %: 10 → 44 of 50); one of the two wrong-color boxes on wood is gone. Cost: `post` at 50 % 42 → 41, `behind` at 75 % 42 → 41.

## What is still wrong, plainly

- One wrong-color box on the 90 wood train frames (`lampcool6_wood_cluster_01`, report only), and one more box on
  Dave's frames that lies on barrels but not on one hand-drawn box (`by_eye.md`).
- A barrel seen through a slot (upper body cut down to the stripe's height, nothing under the stripe) can be read
  as a barrel of the other color. No frame has it; no test covers it.
- The scorecard hides barrels on the mask. A real book or hand in front also throws a shadow and bleeds color at the
  seam; the seam is exactly what `half_stripe` reads. No real frame of a barrel hidden from above or below by a
  non-barrel thing exists in the train sets, so that rule is unverified on real pixels (shots asked for in the report).
- The real occluded barrels (`real.md`): unchanged, HOME 9 of 10, CAMPUS 3 of 3, BLACK 2 of 12, WOOD 7 of 63.
