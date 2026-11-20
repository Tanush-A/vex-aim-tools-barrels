# Verdict: a stripe cut through, and a sliver with stripe and body in view (A8)

Rule: `experiments/2026-11-20_occl_sliver/PREREG.md` and its addendum (two rounds, the last one is final). Numbers:
`round2/` (scorecard, levels, recordings, real), `round2_stripe/` (one kind of stripe damage at a time), `round2/cells75.md`,
`by_eye.md`, the censuses (`census_pairs.md`, `census_ends.md`, `census_ends_damaged.md`), round 1 in `round1*/`.
Train frames only; no test frame was opened. `start` = the defaults of `barrels` before this experiment.

## Outcome

- **On by default: `thin_span`** (a thin slice whose body shows the barrel's whole width gets that width). A block of the
  stripe color hiding 75 %: 3 → 77 of 100; no false box anywhere; scorecard 2737 → 2811, boxes where no barrel is 45 → 45.
- **Off, each failing one clause by a few boxes:** `stripe_bridge` (Part 1; +3 scorecard boxes where no barrel is, +1
  false box at medium damage), `thin_frame` (frame edge 29 → 88 of 100, but "too big" 3 → 8 by 2–3 px), `own_close`
  (straight edge 28 → 57, slanted 0 → 62, but bad day +1 false box, 3 scorecard scenes lost).
- Three quarters hidden on both sides, from above or from below: the mask cannot say which way the barrel extends (0 of 49
  ends closed); no box, by design.

## Clause by clause (round 2)

| clause | `bridge` | `frame` | `close` | **`span`** | `sliver` (all) |
|---|---|---|---|---|---|
| gate: HOME, CAMPUS rows, negatives | pass | pass | pass | **pass** | pass |
| scorecard boxes where no barrel is ≤ 45 | **48** | 45 | 45 | **45** | **48** |
| no scorecard cell lower (found or right place) | pass | pass | **no**: same color beside 50 % 88 → 87; 2 scenes at 75 % lost | **pass** | no |
| false boxes not higher: perfect, typical, bad day w/o patch, light, heavy (20 seeds) | pass (0 = 0) | pass | pass | **pass** | pass |
| false boxes not higher: bad day (20 seeds) | pass (5 → 0) | pass (5) | **no (5 → 6)** | **pass (5)** | pass (0) |
| false boxes not higher: medium (20 seeds) | **no (3 → 4)** | pass | pass (3) | **pass (3)** | **no (4)** |
| campus clips: no new wrong box | pass | pass (1 right box) | pass | **pass** | pass |
| Part 1: bad day and medium find more, no more false | bad day yes; **medium no** | | | | |
| Part 1: patch, one and two breaks better at every width | **yes** (below) | | | | |
| Part 2 cells: found and right place up, too big and false not up | (no Part 2 cell) | **no: frame 75 % too big 3 → 8** | **no: frame 75 % too big 3 → 4; same color beside and lower 75 % 2 → 3** | **yes: stripe-color block 75 %, the only cell it changes** | no |

## Part 1: a stripe cut through

**Why it cost barrels and made false boxes** (reason log, `stripe_before/stripe.md`): `stripe_join` joins pieces only
if each is stripe-shaped (not taller than wide, box not taller than 1.6 stripe heights). A patch or a slit cutting a stripe
near its end leaves an end piece narrower than it is tall, and a piece touching a neighbour picks up a sliver of that
neighbour's body: the pieces stay apart. The larger piece alone is "partly seen"; the side where the patch cut it has a
reason ("body and stripe end apart") and the box is drawn a barrel wide toward the wrong side: one miss and one false
box ("misplaced box of a missed barrel" drew 7 to 15 of the 9 to 18 false boxes at each width). The rest are pieces left
without any box (`side_unexplained`, `outline_unknown`). 20 misses per level are the wedge of `cluster_01` (missed on
perfect masks too).

**The rule (`stripe_bridge`, off):** two pieces of stripe color at the same rows (box middles within half a stripe
height) that fit in one barrel's width are one stripe, gap included, when each is no taller than a stripe by the finder's
own height measure, body color is right above and right below in every column of the gap, and the gap is at most half
the joined span. "Strong enough sense" was set by `census_pairs.md`: with body over the whole gap, 0 of 59 two-barrel
pairs (patch) and 0 of 55 (breaks) are bridged, against 556 and 548 pairs on one barrel; the gap's size alone would
bridge 49 of 59 two-barrel pairs.

Found / 580 (false boxes), 20 seeds, HOME hand masks, one kind of damage at a time (`round2_stripe/stripe.md`):

| damage | 0.03 W | 0.06 W | 0.1 W | 0.15 W | 0.2 W | 0.3 W |
|---|---|---|---|---|---|---|
| stripe patch, `start` | 545 (12) | 544 (13) | 543 (13) | 538 (15) | 543 (9) | 547 (5) |
| stripe patch, `bridge` | 554 (8) | 555 (8) | 555 (8) | 555 (8) | 562 (1) | 557 (4) |
| one break, `start` | 560 (0) | 553 (9) | 536 (18) | 539 (11) | 545 (2) | 535 (3) |
| one break, `bridge` | 560 (0) | 555 (8) | 556 (7) | 559 (3) | 560 (0) | 553 (2) |
| two breaks, `start` | 560 (1) | 553 (13) | 541 (10) | 535 (2) | 530 (2) | 465 (4) |
| two breaks, `bridge` | 560 (0) | 559 (5) | 559 (5) | 558 (2) | 557 (0) | 481 (3) |

| level (20 seeds, of 580) | `start` | `bridge` |
|---|---|---|
| bad day | 547 (5) | **563 (0)** |
| medium | 400 (3) | 413 (**4**) |

Round 1's bridge (without the same-rows test) was better still at every width (e.g. patch 0.06 W 562 (0), one break 0.1 W
563 (0)) but drew 9 scorecard boxes where no barrel is; round 2's same-rows test removed 6 of the 9 and gave back part of
the gain (it refuses pairs where one piece holds a sliver of a neighbour's body, `examples.md`).

**What still fails, exactly:** 3 scorecard boxes, all on one CAMPUS source barrel (`cluster_02`, orange, a same-colored
barrel pasted beside it, at 25 / 50 / 75 %): the pasted barrel's body joins a speck of the other color; and 1 medium box
(`touch_02`, seed 0): one barrel's stripe ends as two bridged groups (a gap column without body) and the second group's box
is shifted by half a barrel. **Off by the rule.** On the real frames and recordings it changes only right boxes (2 on the
black clip) and removes one wrong box (wood).

## Part 2: a sliver with stripe and body in view

Every 75 % cell, found (v2) / right place / too big (`round2/cells75.md`; n = 100 unless said):

| what hides the barrel | `start` | `thin_frame` | `own_close` | **`thin_span` (on)** | all four |
|---|---|---|---|---|---|
| the frame edge | 29 / 29 / 3 | 88 / 89 / 8 | 58 / 59 / 4 | 29 / 29 / 3 | 88 / 89 / 8 |
| a straight upright edge | 28 / 28 / 0 | 28 / 28 / 0 | 57 / 58 / 0 | 28 / 28 / 0 | 57 / 58 / 0 |
| a slanted edge (200) | 0 / 0 / 0 | 0 / 0 / 0 | 62 / 71 / 0 | 0 / 0 / 0 | 62 / 71 / 0 |
| both sides cut (50) | 0 / 0 / 0 | 0 | 0 | 0 | 0 |
| hidden from above / below (50 each) | 0, 1 | same | same | same | same |
| a post across the middle (50) | 11 / 13 / 0 | same | same | same | same |
| other color, beside | 50 / 61 / 3 | 50 / 61 / 3 | 58 / 68 / 3 | 50 / 61 / 3 | 61 / 68 / 3 |
| other color, beside and lower | 77 / 90 / 8 | 77 / 90 / 8 | 82 / 95 / 8 | 77 / 90 / 8 | 85 / 95 / 8 |
| other color, straight in front (49) | 22 / 35 / 5 | same | same | same | same |
| same color, beside | 17 / 33 / 29 | 17 / 33 / 29 | 19 / 35 / 29 | 17 / 33 / 29 | 19 / 36 / 30 |
| same color, beside and lower | 29 / 35 / 2 | 29 / 35 / 2 | 43 / 49 / 3 | 29 / 35 / 2 | 43 / 49 / 3 |
| same color, straight in front (49) | 8 / 14 / 0 | same | same | same | same |
| a block of the body color | 36 / 36 / 2 | 36 / 36 / 2 | 63 / 64 / 2 | 36 / 36 / 2 | 63 / 64 / 2 |
| a block of the stripe color | 3 / 4 / 0 | 3 / 4 / 0 | 14 / 15 / 0 | **77 / 80 / 0** | 79 / 82 / 0 |

(`start+behind`, report only: frame 87 / 88 / 8, same color beside and lower 44 / 51 / 2.)

- **The frame edge (`thin_frame`, off).** Why 29: a thin piece was placed by the outline only, so the frame edge, a
  hidden side that is known, was never asked (60 of the 71 misses were `outline_unknown`). The rule: a thin full slice
  touching the frame on exactly one side is W wide from its other end. 29 → 88 of 100, no box where no barrel is, nothing
  else on the scorecard moves, no false box at any damage level, one right box on the campus clips. **It fails one clause
  by the letter:** too big 3 → 8. The five: truth boxes 10 to 14 px wide (the hand box clipped at the frame); our boxes
  2 to 3 px wider, because the painted barrel reaches 2 to 3 px past the hand-drawn box at the barrel's own side. Example
  `examples.md`: HOME `cluster_02`, orange, frame 75 %: no box → (0, 120, 11, 169), overlap 0.96. *Tanush's call:* the
  frame-edge half of `slice_behind` (`start+behind`, off) gives the same cell (87) with the same 8.
- **The barrel's own side (`own_close`, off).** `census_ends.md` + `census_ends_damaged.md`: "both the top and the bottom
  have come in by 0.15 H over the last 0.05 W" at one end and "at most 0.1 H" at the other was right in all 1330 scorecard
  calls and all 177 calls on real and damaged masks, **when asked of full slices only** (8 wrong of 183 otherwise; the
  looser 0.15 line: 4 wrong). On the scorecard it is right too (straight edge 28 → 57, slanted 0 → 62, body block 36 → 63)
  but a barrel standing in front is round as well: a back barrel's end cut by it closes like a corner. Round 2 asked that
  the own end not be against barrel color; still bad day 5 → 6 (two boxes on the right barrel, overlap 0.71 and 0.77,
  bottom more than a tenth off) and 3 scorecard scenes with a same-colored barrel beside are lost. **Off.**
- **A painted block in front.** Stripe color (`thin_span`, **on**): the barrel's upper body shows its whole width above
  the block, only the stripe is hidden; a thin piece was placed by the outline "whatever its span". 3 → 77 of 100, right
  place 4 → 80, too big 0 → 0. Body color: the block joins the body; round 1's `thin_span` took it into the box (too big
  85 → 121), round 2 refuses a span where the body crosses the stripe's rows, so the body-block cell stays 36 (only
  `own_close` raises it, to 63).
- **What the mask cannot decide.** Both sides cut at 75 %: in 0 of the 49 scenes with a piece is either end closed
  (`census_ends.md`: both ends cut in 39 of 49 at the 0.05 line, 49 of 49 at 0.1); the only honest box holding the barrel
  wherever it is is the cover box, up to 1.75 W wide (off by Tanush's decision; the combined experiment measured it at 58
  boxes where no barrel is, 21 false at medium). A centred box is half off the barrel in half the cases. No box.
  Hidden from above or below at 75 %: a top or a base alone; no stripe is seen (`stripe_hidden` 49 of 50); out of this
  experiment's scope (it needs a stripe).

## False boxes everywhere (the default after this experiment = `start` + `thin_span`)

| where | `start` | default now |
|---|---|---|
| gate (HOME 28 of 29, CAMPUS 35 of 35, false, negatives) | pass | pass (no row changes) |
| scorecard boxes where no barrel is | 45 | 45 |
| perfect / typical / bad day w/o patch / light (20 seeds) | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| bad day / medium / heavy (20 seeds) | 5 / 3 / 0 | 5 / 3 / 0 |
| worst seen (report only) | 6 | 6 |
| campus clips | — | 0 boxes change |
| black clip (report only) | — | +17, all right |
| wood clip, wood frames, Dave's, black frames (report only) | — | no change |

Found at the damage levels (20 seeds, `start` → default): medium 400 → 421, heavy 89 → 99, worst seen 378 → 411; others
equal. Earlier experiments' arms are pinned (their `*_arms.py` pin the four switches off): `before` 2153 / 88, `stack`
2417 / 45, `reduced+thin` 2737 / 45 re-run on the final code (`check_pinned/`).
