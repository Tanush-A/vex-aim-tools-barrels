# Verdict: the stencil detector as a second opinion

Rule and method: `experiments/2026-11-20_stencil/PREREG.md` (with addenda A and B). Method in plain English:
`method.md`. Numbers: `tables.md`, `never_regress.md`, `scorecard.md`, `levels/summary.md`, `by_eye.md`,
`recordings.md`, `timing.md`, `calibration.md`, `fit.md`, `veto_curve.md`. Train frames only; no test frame was opened.

## The answer in three lines

1. **One stencil idea does not cover the occlusion cases.** Alone it finds 2233 of the 3888 scorecard scenes
   against the rules' 2417, loses barrels on HOME and CAMPUS, and is weak on damaged masks. It is not a replacement.
2. **It is the more careful of the two:** 10 boxes where no barrel is on the scorecard against 45, no box on any
   negative frame, no new box on any recording, tighter boxes. What it draws is nearly always a barrel.
3. **Behind the rules it adds a little, safely:** the rule detector's boxes plus what the stencil still finds
   (`union1`) is 2512 of 3888, no cell lower, HOME and CAMPUS and all 337 recorded frames unchanged. The gain is
   in "half hidden" rows. Three quarters hidden stays at zero.

## The arms

| arm | what it is |
|---|---|
| `rules` | the rule detector as it is on this branch |
| `stencil` | the stencil alone (accept 0.20, absent cost 0.1, outside cost 0.5) |
| `union` | rule boxes + what the stencil finds with those boxes claimed |
| `union1` | round 2: `union`, but an added box on a rule box of its color at the same depth is not drawn |
| `veto` | rule boxes whose stencil score at their place is at least -0.01 |
| `veto+union` | both |

## The project's rule

No HOME or CAMPUS scenario row loses a found barrel or gains a false box; no box on any negative frame; no new wrong
box on the campus clips (and a box that disappears must have been wrong).

| | `stencil` | `union` | `union1` | `veto` | `veto+union` |
|---|---|---|---|---|---|
| eval table (found / missed / false): HOME 28 / 1 / 0 | 27 / 2 / 0 | same | same | same | same |
| CAMPUS 35 / 0 / 0 | 31 / 4 / 1 | same | same | same | same |
| boxes on negative frames, every set | 0 | 0 | 0 | 0 | 0 |
| campus clips: boxes appearing | 0 | 0 | 0 | 0 | 0 |
| campus clips: boxes disappearing (right ones among them) | 16 (5) | 0 | 0 | 3 (0) | 3 (0) |
| **passes** | **no** | yes | yes | yes | yes |

By the registered pick (most scorecard scenes among the combined arms that pass) the best combined arm is `union`
(2514); `union1` is its round-2 correction (2512, and no extra box where no barrel is).

## Eval table, set by set (found / missed / false; median width ratio; median bottom error px)

| set | barrels | `rules` | `stencil` | `union1` |
|---|---|---|---|---|
| HOME (leave one scene out) | 29 | 28 / 1 / 0; 0.95; 1.0 | 27 / 2 / 0; 0.96; 2.0 | 28 / 1 / 0; 0.95; 1.0 |
| CAMPUS | 35 | 35 / 0 / 0; 0.94; 2.0 | 31 / 4 / 1; 0.98; 3.0 | 35 / 0 / 0; 0.94; 2.0 |
| BLACK (report only) | 26 | 5 / 21 / 1 | 0 / 26 / 0 | 5 / 21 / 1 |
| wood, 9 lamp settings (report only) | 189 | 7 / 182 / 4 | 3 / 186 / 0 | 7 / 182 / 4 |
| Dave (indicative) | 34 | 12 / 22 / 3 | 3 / 31 / 0 | 13 / 21 / 3 |

Scenario by scenario: `tables.md`. `union` equals `union1` in every row. The stencil's misses on HOME and CAMPUS:
HOME `topstripe_01` (close-up, stripe at the frame bottom) and the wedge of `cluster_01` (also missed by the rules);
CAMPUS `held_01` (no stripe in view: the score cannot pass 0.25), `occl_02` (behind the marker stand: too little
seen), `clutter_02` (box a third off), `cluster_02` (box at overlap 0.50, bottom off: one miss and one false box).
On the extreme sets the stencil draws no false box at all and finds almost nothing: the barrels are half painted.

## Damaged masks (found of 145 (false boxes); seeds 0 to 4, not the calibration's)

| | `rules` | `stencil` | `union` = `union1` | `veto` |
|---|---|---|---|---|
| perfect HOME masks, of 29 | 28 (0) | 28 (0) | 28 (0) | 28 (0) |
| light | 143 (0) | 135 (0) | 143 (0) | 143 (0) |
| medium | 99 (1) | **37 (0)** | 99 (**2**) | 97 (1) |
| heavy | 21 (0) | 4 (0) | 21 (0) | 16 (0) |
| one kind: top highlight 0.7 x 0.4 | 132 (7) | 38 (0) | 132 (7) | 132 (7) |
| one kind: stripe highlight 0.15 | 132 (3) | 138 (0) | 140 (3) | 132 (3) |
| one kind: stripe breaks | 133 (1) | 141 (0) | 142 (2) | 133 (1) |
| one kind: edges eaten 2 px | 110 (0) | 130 (0) | 125 (0) | 110 (0) |

- The stencil is **better than the rules when the stripe is damaged** (highlight on it, breaks, eaten edges) and
  **much worse when the upper body has a hole**: a column is worth its worst band, so a highlight on the lid makes
  every column under it worth nothing. That one kind of damage is the whole medium / heavy gap.
- `union` and `union1` have one more false box at medium damage (and the same frame under "stripe breaks"): HOME
  `close_02`, seed 3. The rule box (334, 141, 417, 232) sits 26 px to the right of the barrel (308, 141, 392, 231);
  the stencil adds (306, 145, 382, 227) on the uncovered strip. Two boxes on one barrel. Round 2's rule does not
  catch it, because the added box's bottom is 5 rows higher and so it counts as "standing behind". No round 3.

## Occlusion scorecard (3888 scenes; `scorecard.md` has every cell for every arm)

Found, `rules` → `stencil` → `union1`:

| what hides the barrel | 25 % | 50 % | 75 % |
|---|---|---|---|
| the frame edge | 100 → 99 → 100 of 100 | 99 → 97 → 100 | 3 → 4 → 6 |
| a straight upright edge | 100 → 99 → 100 of 100 | 82 → 86 → 91 | 0 → 0 → 0 |
| a slanted edge | 200 → 198 → 200 of 200 | 154 → 142 → 175 | 0 → 0 → 0 |
| both sides | 50 → 50 → 50 of 50 | 49 → 49 → 49 | 0 → 7 → 7 |
| from above | 50 → 46 → 50 of 50 | 2 → 0 → 2 | 0 → 0 → 0 |
| from below | 49 → **8** → 49 of 50 | 1 → 0 → 1 | 1 → 0 → 1 |
| a post across the middle | 49 → 49 → 50 of 50 | 9 → **27** → 32 | 0 → 0 → 0 |
| other color, beside | 99 → 99 → 100 of 100 | 94 → 93 → 97 | 49 → **11** → 50 |
| other color, beside and lower | 98 → 99 → 100 of 100 | 92 → 91 → 98 | 77 → **13** → 77 |
| other color, straight in front | 39 → 44 → 43 of 47 | 38 → 28 → 40 of 48 | 17 → 9 → 20 of 49 |
| same color, beside | 81 → **99** → 81 of 100 | 36 → **83** → 36 | 16 → 8 → 16 |
| same color, beside and lower | 91 → 99 → 92 of 100 | 85 → 96 → 87 | 26 → 18 → 26 |
| same color, straight in front | 44 → 45 → 44 of 47 | 29 → 28 → 32 of 48 | 2 → 13 → 4 of 49 |
| a block of the body color | 100 → 96 → 100 of 100 | 99 → **19** → 99 | 5 → 2 → 5 |
| a block of the stripe color | 100 → 98 → 100 of 100 | 99 → 81 → 99 | 3 → 0 → 3 |

| all 3888 scenes | `rules` | `stencil` | `union` | `union1` | `veto` | `veto+union` |
|---|---|---|---|---|---|---|
| found | 2417 | 2233 | 2514 | 2512 | 2408 | 2507 |
| box in the right place | 2532 | 2421 | 2644 | 2644 | 2520 | 2634 |
| **boxes where no barrel is** | 45 | **10** | 47 | 45 | 42 | 44 |
| right-place boxes too small / right / too big | 299 / 2129 / 104 | 96 / 2298 / 27 | 308 / 2230 / 106 | 309 / 2229 / 106 | 292 / 2124 / 104 | 301 / 2227 / 106 |
| cells with more found / fewer found than `rules` | | 12 / 25 | 19 / 0 | 19 / 0 | 0 / 6 | 21 / 6 |

Why the stencil alone loses its worst cells (looked at on `card_stencil/sheets/` and with scores):

- **From below, a quarter hidden: 49 → 8.** It boxes the barrel (score 0.36 to 0.41) but with a smaller stencil that
  fits what is painted, so the bottom is 7 to 8 px too high. Nothing tells it the bottom is hidden.
- **A block of body color hiding half: 99 → 19.** The block paints the ring, the box is pushed away from it and
  lands a third of a width off the barrel.
- **Another barrel hiding three quarters: 49 → 11, 77 → 13.** The front barrel is found and the hidden part does
  count as explained, but a quarter of a barrel seen scores 0.08 to 0.16, under accept 0.20. The rules know the
  reason for the missing side and box it.
- **Three quarters hidden by a thing that is not a barrel: 0 everywhere**, for both. By design here (seen share
  under 0.27).

Where it wins alone: **a same-colored barrel beside (36 → 83 at half hidden)**: two tight boxes where the rules draw
one wide one; a post; a same-colored barrel straight in front at three quarters (2 → 13). In `union1` most of the
same-color gain is lost again, because the rules' one wide box claims both barrels.

The 25 real occluded or cut barrels of the train frames (`card_*/real.md`): `union1` the same as `rules` everywhere
(HOME 9 of 10, CAMPUS 3 of 3, BLACK 2 of 12); `stencil` HOME 8, CAMPUS 1, BLACK 0.

## Recordings (337 frames, by eye: `by_eye.md`)

| | `stencil` | `union`, `union1` | `veto`, `veto+union` |
|---|---|---|---|
| boxes that appear, any clip | 0 | 0 | 0 |
| campus clips, boxes that disappear | 16: 11 wrong rule boxes, **5 right ones** | 0 | 3, all wrong |
| black clip | 1 right box lost | 0 | 1 right box lost |
| wood clip (extreme) | 37 half-barrel boxes gone | 0 | 29 half-barrel boxes gone |

## Time per frame (37 HOME and CAMPUS frames, one core; detection only; segmentation is 26 ms more)

| | median | 90th percentile | slowest frame |
|---|---|---|---|
| `rules` | 19 ms | 33 | 41 |
| `stencil` | 89 ms | 154 | 266 |
| `union`, `union1` | 70 ms | 90 | 126 |
| `veto` | 78 ms | 160 | 167 |
| `veto+union` | 127 ms | 209 | 264 |

Fine for a live view once a second; about four times the rule detector.

## The veto, and a lead

The registered veto level (-0.01) is nearly a no-op by construction: the lowest stencil score at a RIGHT rule box
on the calibration masks is 0.04 (a cap behind two barrels). Report only, chosen by nothing (`veto_curve.md`): at
0.05 a veto would remove 27 of the rules' 45 scorecard boxes where no barrel is, for 35 of 3701 right boxes, and no
right box on HOME (28) or CAMPUS (35). At 0.10: 32 of 45 for 67, and one right CAMPUS box. This is the stencil's
most useful side and it was not what was pre-registered; it needs its own run (levels, recordings by eye).

## Does one idea cover the cases? What the numbers say

No, and the reason is the one written in the pre-registration: **in the mask a thing that hides a barrel looks
like bare table.** The stencil can only count what is seen. The calibration put the line at 0.20 (below 0.15 false
boxes appear on HOME's own masks), which is "a little more than a quarter of the barrel, seen whole top to bottom".
So half hidden is found, three quarters is not, and hidden from above or below is not (no column shows all three
bands). The rules get further on the scorecard only where they know a reason (a found barrel, the frame edge).
Softer scoring was tried on the calibration masks before any evaluation (addendum A): it finds more damaged
barrels and draws wrong boxes that no threshold removes.

**Lead, not built:** to go below a quarter seen, or to box a barrel hidden from above or below, something has to say
"there IS a thing in front here". The class mask cannot. The gray image can in principle: an occluder's edge and
its texture are in the picture. Evidence that this is the missing piece: every 75 % row with a non-barrel occluder
is 0 for every arm, while the same amount hidden by a barrel (which the mask does show) is 50 and 77 of 100.

## Recommendation

- **Stencil as the detector: drop.** It fails the project's rule and is brittle to a highlight on the lid.
- **Stencil as an adder behind the rules (`union1`): a candidate, not urgent.** +95 scenes of 3888, nothing lost
  anywhere measured, 50 ms more per frame. One known flaw: a second box on a barrel whose rule box is displaced
  (once in 80 damaged frames). The gain is modest because the rules already cover "half hidden".
- **Stencil as a verifier: the part worth pursuing**, as its own pre-registered test at a level near 0.05. It is
  where "no false positives" would actually move: 45 → about 18 boxes where no barrel is on the scorecard, 11 of
  the 16 boxes the stencil declines on the campus clips are wrong rule boxes.
- Either way the method is one page and one formula, and can be explained (`method.md`).

## What could not be verified

- Everything about occlusion is simulated on the mask. The open shot request R1 (10 real occlusion frames) is the
  real check; no real frame exists for: a low thing hiding a barrel's lower quarter, a same-colored barrel beside,
  a post, a block of barrel color beside a barrel.
- The bottom-row correction is fit on 12 barrels 32 to 84 px wide and extended to all sizes.
- `accept` rests on 10 negative frames with clutter (wood and black tables) plus HOME's masks. No frame with a
  striped orange-and-blue object that is not a barrel exists.
- The recordings were judged by one look at contact sheets; `r4` frame 020 (a barrel between the fingers of a hand)
  is a judgment call counted as a right box lost.
