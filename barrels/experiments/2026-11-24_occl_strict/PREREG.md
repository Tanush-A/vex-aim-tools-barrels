# Pre-registration: a logical audit of the rules that make boxes, and one verify step (occl_strict)

Written 2026-11-24 on branch `wip/occl-strict` (from `origin/barrels` 08b3f71, merged with `origin/barrels` b72ed6f: glass,
bathroom tile, the glass occlusion set). **Committed before any detector change is committed.** At the time of writing the
two checks below exist in the working copy of `detector.py` behind switches that are OFF (`verify_front`,
`verify_readings`), and were run only as census arms (no default changed). Train frames only; no test frame opened.

The request (Tanush): the occlusion logic may be too lenient; strengthen it everywhere against random boxes without
breaking the real cases, by logic, not by trial and error.

## 1. The facts every real barrel obeys (whatever is hidden)

- **F1 layout.** Top to bottom: body, stripe, body; the stripe is 6 of 24 mm at mid-height; the bands are level.
- **F2 one distance.** Every seen dimension (width, top, stripe row, stripe height, bottom) agrees with ONE distance.
  The "one idea" of the occlusion work: a reading, a second reading that agrees, a place.
- **F3 explained edges.** A seen edge is the barrel's outline, or ends against a cause: the frame, a nearer found
  barrel, a painted occluder, or an unpainted region where an occluder could be.
- **F4 extent.** No body color continuing past where the barrel must end, unless another barrel explains it.
- **F5 occlusion order.** A barrel is not seen through a nearer barrel: inside the nearer one's outline every pixel is
  the nearer one's picture (its own layout).
- **F6 on the table.** The bottom is below the horizon; a box above a found barrel is farther, so higher AND smaller.

## 2. Inventory: each rule that can CREATE a box

| rule | evidence it accepts as "a barrel" | facts it does not check |
|---|---|---|
| stripe step, whole stripe | a component of the other color with body right above and below it (pixel sandwich), 0.45-1.6 stripe heights, >= 0.8 W; seen edges used if they agree | F5 (is the "stripe" a nearer barrel's body?), F4, F2 when both edges are inferred (only edge_check (a): top against the other color) |
| `stripe_join` / `stripe_bridge` | pieces at the same rows within 1.2 W (bridge: body over the gap) are one stripe | F5; F1 levelness only to half a stripe height |
| `seam_height` | a too-thin whole-width stripe re-read with the body gap | F5 |
| `stripe_wide` | a stripe > 1.2 W with body above and below is k barrels, each W from its outer edge | F3 at the cut, F5 |
| `side_hidden` | a stripe < 0.8 W: W wide from the seen edge opposite a side with a reason (frame, nearer found barrel, body and stripe ending apart) | **F5** (the reason "a nearer barrel is beside it" never asks whether the stripe lies inside that barrel); **F2** (top and bottom may both be inferred: the distance then rests on the stripe row alone) |
| `pin_outline` | no side reason: exactly one end of the seen part follows the outline's corners | F5 |
| `pin_thin`, `thin_span`, `thin_frame` | a thin full slice (top and bottom seen) with one own end / the whole width in its body / cut by the frame | F5 (thin_frame: F3 at the far end) |
| `cap_behind`, `cap_same`, `cap_low` (+ `cap_seen_bottom`, placement) | a piece barrel-wide for its top row, upper-body tall, half its predicted box behind found nearer boxes | F1 (no stripe), F5 for the other color (rule 1 only asks the own color's boxes) |
| `post_pair` | two narrow full slices at the same rows, outer edges 0.8-1.2 W apart | F3 at the inner ends, F5 |
| `half_stripe`, `half_thin` | a band with body on one side only, far edge where the seam predicts it | F1's reverse reading (only "thinner than the body" separates it), F5 |
| stripeless close-up (`det1`, `closeup_stripe`, `closeup_side`) | barrel-colored, 0.4-1.6 W for its top row, reaching the frame bottom (seen or inferred) | F3 (a seen bottom far above the frame bottom against the table), F4 (body resuming above its "top"), solidity |
| stripeless far piece (`det1`) | barrel-wide and barrel-tall, expected stripe under 4 px | F1 (cannot be seen), F5 |
| `edge_check` | (refuses and places only) | – |

## 3. The census (no detector change; `census_facts.py`, `boxes.py`, `diff.py`)

Test beds: every train frame of every set (HOME, CAMPUS and all new sets; wood and black report only), the 3888
scorecard scenes, the damage levels (16 HOME hand masks, perfect and 7 levels, 20 seeds). Each box judged against the
labels; for each candidate check, the boxes it would remove.

FILLED IN BELOW (section 5) from `results/2026-11-24_occl_strict/`.

## 4. The checks, the rule for adopting them

One verify step at the end of `detect`, applied to every rule's box (and, for `verify_front`, once also after the
stripe step and the stripeless pieces, so that caps, pairs and half stripes lean only on boxes that passed it). Each a
switch.

- **`verify_front` (F5).** Boxes are taken nearest first (lowest bottom edge). A box's evidence (the stripe, cap piece,
  band, slices or piece it was read from, from the reason log) is split into pixels a KEPT nearer barrel explains
  (inside its outline, between its seen top and bottom, and of the color its own layout puts there; within half a
  stripe height of a seam either color) and the rest. Fewer than `min_area_px` (20) own pixels: dropped. No new number.
- **`verify_readings` (F2).** A partly seen stripe-step box (`occluded`) whose top AND bottom are both inferred and whose
  seen span (stripe + joined body, as `_partly_seen` measures it) is under `stripe_full` W has no second reading: the
  distance rests on the stripe's row alone and the place on a guessed side. Dropped. No new number.

Rejected by the census before any arm (section 5): "at least one own edge" for every box, "no body joined above the
horizon", "no body resuming beyond a seen edge" (above / below), "body span not wider than 1.2 W", "the stripe-colored
region is not taller than a stripe", "over-extended at both ends", "evidence share inside a nearer barrel > 1/2".

Acceptance (against `origin/barrels`, on the latest data, stricter allowed):
1. `python barrels/tools/report.py --gate --cand-det <the checks on>` passes.
2. No real barrel lost on any real train frame of any ordinary set (every change listed by frame).
3. False boxes on the real train frames go down.
4. Scorecard: boxes where no barrel is not up; found not down by more than 15 of 3888 (every lost scene named).
5. Damage levels: false boxes not up at any level.
6. Campus recordings: every box that appears or disappears judged by eye.
At most two rounds; a dated addendum before any corrected code.

## 5. Census numbers (latest data, b72ed6f; `results/2026-11-24_occl_strict/`)

Boxes today on the real train frames (`boxes/boxes.md`): 261, of which 237 hits, 5 loose (real barrel, bottom off), 9
part (on a real barrel, wrong place), 4 wrong color, **6 false (no barrel there)**: abpwhite `occlx_17` (orange, stripe
step / `side_hidden`), palewood `core_01` (wood grain, stripeless close-up), glass `lampmid3_glass_neg_02`,
`lampmid3_glass_occl_02`, `lampmid6_glass_occl_02` (the tin with an orange lid and a blue label, stripe step /
`side_hidden`, `stripe_join`, `stripe_bridge`), `window_glass_occlx_16` (blue tin under an orange sticky note, stripe step /
`stripe_join`, `side_hidden`). Two of them are on empty frames (the gate fails on them today).

Candidate checks as measures on the real frames (`census/census_real.csv`; real hits it would remove on ordinary sets):

| check (fact) | removes not-hits | removes real hits, ordinary sets | verdict |
|---|---|---|---|
| at least one own edge, top or bottom (F2/F3) | 7 | **3** (ottoman `lampmid6` clutter_01, core_01; palewood clutter_01) + 1 black | rejected |
| no body joined above the horizon (F4) | 3 | **9** (campus far_01, every glass clutter_01, tile clutter_01, ...) | rejected: clutter behind a barrel touches it |
| body resumes within 1.6 stripe heights above a seen top (F4) | 7 | **3** (campus plain_01, tile and ottoman close_01) | rejected |
| ... below a seen bottom (F4) | 0 | 0 (+1 black) | rejected: removes nothing false |
| body span <= 1.2 W after other boxes (F4, sides) | 11 | **42** | rejected |
| stripe-colored region not taller than a stripe (F1) | 8 at 1.0, 0 at 1.6 | 2 at 1.0 (HOME far_02, glass clutter_01) | rejected |
| over-extended past both inferred edges (F4) | 2 | **1** (palewood clutter_01) | rejected |
| evidence share inside a nearer barrel's layout > 1/2 (F5, first form) | 2 | 0 here, but 154 right scorecard boxes and 15 damaged-mask hits | replaced by the own-pixel form |
| **`verify_front`**, own evidence < 20 px (F5) | 2 (abpgray clutter_01 wrong color; abpwhite `occlx_17`) | **0** | candidate |
| **`verify_readings`** (F2) | 3 (the three glass tin / note boxes, two of them on empty frames) | **0** | candidate |

As arms against `start` (`diff_front_r2.md`, `diff_readings.md`):

| | real frames removed | scorecard (3888) removed | damage levels (20 seeds) |
|---|---|---|---|
| `verify_front` | 2 not-hits, 0 hits | 16 boxes where no barrel is, 12 right-place boxes (3 others appear: caps that the dropped stripe box had blocked) | medium: 3 hits lost, 1 part removed; worst seen: 3 hits lost, 1 found by `post_pair`; perfect, typical, bad day, light: none |
| `verify_readings` | 3 not-hits, 0 hits | 14 boxes where no barrel is, 5 right-place boxes | 2 part boxes (medium, worst seen) |

Every right-place scorecard box `verify_front` removes was read from the front barrel's picture (looked at:
`look_r1.png`): its evidence has 0 to 16 pixels of its own; the barrel is there, the reading is not. The damaged-mask
losses are at "medium" and "worst seen", the levels the earlier experiments only report.
