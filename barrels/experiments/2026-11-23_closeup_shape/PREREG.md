# Pre-registration: the stripeless close-up piece (TODO A9)

Written 2026-11-23 on branch `wip/closeup-shape` (= `origin/barrels` at `e0d01e0`), **before any detector code is
changed**. What had been run when this was written: the census (`census.py`, results in
`results/2026-11-23_closeup_shape/census/`), the reason log of single frames (`why.py`), the never-regress check on the
starting defaults (FAIL: one new box on an empty frame, `4A8B_window_abpwhite_occlx_15`), and the occlusion scorecard
of the starting defaults (`battery.py card --arms start`). No arm with a new rule has been run: the rules below do not
exist in code yet.

## The problem

`4A8B_window_abpwhite_occlx_15` is a train frame with no barrel (label `negative: true`, `clean: false`: striped-looking
clutter on purpose). The detector draws an orange box (465, 286, 640, 480) on a printed orange fruit on a snack bag at
the frame's bottom-right corner. Source `det1`, the step-1 rule of 2026-11-03: "a barrel-colored piece that reaches the
frame bottom is a close barrel whose stripe is below the frame". The piece's own pixels end at row 368; the box reaches
the frame bottom only because the top row 286 predicts a base at row 653 and the seen bottom (368) disagrees with it by
more than the tolerance, so the predicted bottom is drawn and clipped to the frame.

## The census (`results/2026-11-23_closeup_shape/census/census.md`; train frames of every set; the report's segmentation)

Step-1 pieces whose resolved box reaches the frame bottom, 1027 in all:

| what the detector does today | real barrel | not a barrel | on an empty frame |
|---|---|---|---|
| box (`det1`) | 23 | 5 | 1 (the fruit) |
| covered by another box | 1 | 0 | 0 |
| refused by the size test | 0 | 905 | 92 |

The refused ones are slivers (wood grain, clutter) and are not touched by anything below.

The 29 boxed pieces and the cues measured on each (`reach` = how much of the upper body is seen: from the top row down
to the row where that top row puts the stripe's top, or to the frame bottom when the stripe is below the frame;
`ratio` = seen width / the width the top row predicts; `cut` = the frame's left / right side cuts the piece):

| piece | real | cut | ratio | reach | outline cost of the uncut end | row fill |
|---|---|---|---|---|---|---|
| HOME top_01, topstripe_01 | yes | – | 0.91, 0.92 | 1.00, 1.14 | 0.02 | 1.00 |
| CAMPUS held_01, top_01, topstripe_01 | yes | – | 0.73–0.87 | 1.00–1.11 | 0.02–0.03 | 1.00 |
| abpgray close_01, held_01 | yes | – | 0.96, 0.78 | 1.07, 1.00 | 0.02–0.03 | 1.00 |
| wood (cool3, cool6, mid3, mid6, warm3) close_01 | yes | – | 0.71–0.90 | **0.52**–1.08 | 0.03–0.13 | 0.80–0.99 |
| ottoman mid3 close_01 | yes | – | 0.58 | 0.87 | 0.03 | 0.97 |
| black close_02, held_01 | yes | – | 0.67, 0.56 | 1.00, 1.00 | 0.03–0.05 | 0.85, 0.56 |
| DAVE snap_06, 07, 08 o, 09 o, 09 b | yes | – | 0.64–0.84 | 0.97–1.00 | 0.03–0.06 | 0.94–1.00 |
| **DAVE snap_08 b, snap_10, snap_11** | yes | **right, right, left** | 0.63–0.66 | **1.00** | 0.046, 0.055, 0.052 | 1.00 |
| **abpwhite occlx_15 (the fruit, empty frame)** | **no** | **right** | 0.45 | **0.42** | 0.083 | 0.96 |
| ottoman warm6 core_01 | no | – | 0.41 | 0.30 | 0.08–0.11 | 0.96 |
| wood warm6 close_01 (orange wood grain) | no | – | 1.26 | 1.00 | 0.06–0.13 | 0.36 |
| palewood core_01 (wood grain) | no | – | 0.94 | 0.99 | 0.04–0.05 | 0.46 |
| DAVE snap_03, snap_04 | no | – | 0.59, 0.61 | 0.39, 0.27 | 0.04–0.09 | 0.94, 0.77 |

(The real wood warm6 close_01 blue barrel is the one piece "covered": by the false orange wood-grain box beside it.)

What separates, and what does not:
- **Cut by the frame's side + reach.** A piece cut by the frame side has no width to check: the seen width is only a
  lower bound. Real side-cut close-ups (3, all Dave's) are seen down to the frame bottom: reach 1.00. The fruit: 0.42.
  The margin is the whole range from 0.42 to 1.00; the tolerance below puts the line at 0.85.
- Reach alone, for every piece: real down to 0.52 (wood warm3 close_01: under the warm lamp only the lit lid is blue,
  the body is too dark), false up to 0.42 (the fruit) — no margin worth the name, and three false pieces reach 1.00.
- Width ratio alone: real 0.56–0.96, false 0.41–1.26: overlaps.
- The outline of the top at the uncut end (`pin_outline`'s measure on the top line, `pin_good` = 0.05): real side-cut
  ones are 0.046–0.055, two of them above 0.05; the fruit 0.083. Too thin a margin and two real ones fail.
- Rounded or flat top (share of columns whose top is within 0.1 H of the top row): the lit lid of a real barrel is as
  flat as the fruit (0.85 vs 1.00). No margin.
- Body color filling the piece (row fill): real down to 0.56 (black held_01), the fruit 0.96. The fruit is filled; its
  yellow part is simply not orange in the mask. Does not separate the fruit (it would separate the two wood-grain boxes,
  0.36 and 0.46, but with a 0.10 margin to 0.56; not proposed).
- The other barrel color inside the piece: 0.00 on every piece, real or not. Does not separate.
- The top row against the horizon: every piece's top is 160–270 rows below it. Does not separate.

### The "specific position" lead (same census, third table)

Pieces refused as stripeless (they pass the size test, show no stripe, and do not reach the frame bottom) whose top row
puts the stripe's bottom row past the frame bottom: **one, and it is real** — `4A8B_overheaddim_palewood_close_01`, the
orange barrel (292, 241, 568, 477), label (291, 243, 566, 480), missed today. Its top row 241 puts the stripe at rows
434–483 and the base at 508: the frame bottom cuts the stripe, so the stripe finder never sees body below it; and the
piece's seen bottom 477 agrees with the predicted 508 within the tolerance (40 px), so the piece is not "reaching the
frame bottom" and is refused as a barrel that should have shown a stripe. A barrel a little nearer (stripe below the
frame) and a little farther (body below the stripe in view) are both found. No false piece of any train frame is in
this table.

## The rules (two switches, `DetConfig`, both only in step 1's stripeless pieces of `detect`)

**A. `closeup_side`.** A stripeless piece kept because it reaches the frame bottom, and that the frame's left or right
side also cuts (x0 = 0 or x1 = 640), shows neither its width nor its stripe; it is a close barrel only when its body is
seen from its top row down to where that top row puts the stripe's top (or down to the frame bottom when that is lower),
within the existing tolerance `max(bottom_tol_min_px, bottom_tol × that height)` (15 %, at least 4 px). Otherwise no box.

Worked example (the fruit): top row 286 → axis distance 26.4 mm → stripe top at row 602, below the frame → it must be
seen down to row 480 − 0.15 × (480 − 286) = 451; it ends at 368 → no box.

**B. `closeup_stripe`.** A stripeless piece is also a close barrel (kept as today's frame-bottom pieces are, with rule A
applying to it) when the stripe its top row predicts runs past the frame bottom (predicted stripe bottom row ≥ 480): then
no stripe can be seen with body below it, exactly as when the piece reaches the frame bottom. Its box is the piece's box
as step 1 resolved it (a seen bottom that agrees with the predicted one is kept).

Every number is an existing parameter (`bottom_tol`, `bottom_tol_min_px`) or a barrel proportion from the camera
model (the stripe's top and bottom rows for the distance the top row gives).

## Arms (`closeup.py`; every field pinned from the starting defaults, so later default changes do not move them)

`start` (both off: `origin/barrels` e0d01e0), `side` (A), `stripe` (B), `shape` (A + B, the candidate default).

## Acceptance (each against `start`, on the same code)

1. The box on `occlx_15` is gone, and no empty frame of any set gets a box (eval table, every set).
2. `report.py --gate --cand-det <the switches>`: PASS.
3. No real close-up / held / edge / top barrel that is found today is lost, on any set (listed by name, before / after);
   any newly found ones are listed.
4. The eval table: HOME 28 / 1 / 0 and CAMPUS 35 / 0 / 0 (found / missed / false), unchanged.
5. The occlusion scorecard (`2026-11-20_occl_combined` harness, by path): found not lower in any cell; boxes where no
   barrel is not above `start`'s.
6. The damaged masks (levels): false boxes not higher at any level.
7. The campus recordings (`data/recordings`, read only): every box that appears or disappears judged by eye on contact
   sheets; no appearing box on something that is not a barrel, no disappearing box on a barrel (the clips with barrels
   entering at the frame edge and with a hand are checked one by one).

A switch that passes all seven is on by default on this branch; one that fails any is off, with the reason. B is
judged on its own (`stripe` against `start`) and together (`shape` against `side`). At most two rounds; a second round
gets a dated addendum here before the code is corrected.
