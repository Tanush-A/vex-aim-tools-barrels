## 2026-11-27 — "Bluer than the light", with the false boxes taken away by geometry (branch `wip/exp-bluer-geom`)

Ready to paste into `docs/EXPERIMENTS.md`. Plan: `experiments/2026-11-27_bluer_geom/PREREG.md`, committed (3094b20)
before any judged run. One round. Nothing that runs by default was changed. `detector.py` was not edited.

#### Hypothesis

Yesterday's B4 ("bluer than the light") finds the warm bathroom's barrels but fails on boxes on clutter. Tanush: the
clutter was placed as near-barrel traps, and only the detector's geometry can tell them apart. So: keep B4's colors,
and remove the traps by shape, with checks each built on a measured kind of false box.

#### Method

- **A. Reproduction.** B4 leave one place out on this branch (the collapsed detector): 145.72 placements, 257 per
  frame, boxes not on their barrel 6.68, FAIL. Equal to the light experiment, number for number, same picks per fold.
- **B. Every false box measured.** B4 draws 283 boxes on the 154 ordinary frames: 259 on a real barrel, 24 not. Each
  measured against what its row predicts (15 measurements, `stages.measure`) and compared with all 259 real barrels.
  Contact sheets of all of them were looked at.
- **What the 24 are.** 12 on the red jar with the teal label (bathroom; two on the glass table, drawn by the fixed
  colors too). 4 on the blue tin. 2 on the small figure. The rest: a cap over a real barrel, two wrong colors on real
  barrels, one box beside a real barrel, the pale-wood close-up.
- **What separates.** Two things. *Speckle*: a barrel is painted as one solid shape; the tin, the figure and the jar
  under the warm lamp are speckle (solidity 0.17-0.39; real barrels 0.40 and up). *A label, not a stripe*: the jar's
  label is 1.3-1.65 times the stripe its row predicts, and the jar around it holds little body color (0.14-0.53;
  real barrels with a stripe that tall: 0.72-0.80, except one on the dark ottoman at 0.23).
- **What does not separate.** Width and height for the row, the top and bottom edges, the bulge (the mask is too
  ragged to read a curve), aspect, the body bands' likeness, color around the box.
- **The checks** (`checks.py`, a post-filter in the callable; `stages.found` draws the same boxes as `detect`:
  IDENTICAL BOXES ON EVERY INPUT, 5435 masks). K1 speckle: solidity under 0.30 / 0.35 / 0.40. K2 label: stripe over
  1.5 / 1.35 / 1.25 x the row's AND body fill under 0.45 / 0.6. 28 sets with "off". The folds choose the color step
  and the checks together, by the light experiment's rule. The grid values were read off the in-sample table.

#### Data

Train frames only. 154 ordinary frames, 17 conditions, 8 places, 172 placements. Extreme conditions printed, never
judged. No test frame was loaded, viewed, scored or listed.

#### Results (leave one place out; baseline 133.8 of 172, 211 of 307 per frame, boxes 1.93)

| candidate | verdict | found, placements | per frame | gained / lost | boxes not on their barrel (per frame) | empty with clutter | places that moved |
|---|---|---|---|---|---|---|---|
| B4, reproduced | FAIL | 145.72 (+11.92) | 257 | 46 / 0 | 6.68 (24) | 1.25 | bathroom 4 → 14.25; ottoman 3 → 4.67 |
| **G1 B4 + checks (primary)** | **PASS** | **147.05 (+13.25)** | 261 | 50 / 0 | **3.23 (13)** | 0.75 | bathroom 4 → 14.25; ottoman 3 → 6 |
| G1a B4 + K1 only | PASS | 145.80 (+12.00) | 257 | 47 / 1 | 2.48 (10) | 0.25 | bathroom 4 → 14; ottoman 3 → 5 |
| G1b B4 + K2 only | FAIL | 145.72 (+11.92) | 257 | 46 / 0 | 6.23 (22) | 1.25 | as B4 |
| G2 fixed colors + checks | NO CLEAR DIFFERENCE | 133.80 (0) | 211 | 0 / 0 | 1.93 (5) | 0 | none |
| C1 (contrast), reproduced | PASS | 155.30 (+21.50) | 275 | 64 / 0 | 2.83 (9) | 0 | gray table 10 → 15; bathroom 4 → 13.5; ottoman 3 → 10 |
| G3 C1 + checks | PASS | 155.30 (+21.50) | 275 | 64 / 0 | 2.23 (6) | 0 | as C1 |
| delta 0.30, no checks | PASS | 141.97 (+8.17) | 242 | 31 / 0 | 3.68 (12) | 0 | bathroom 4 → 10.5; ottoman 3 → 4.67 |
| delta 0.30 + checks | PASS | 141.97 (+8.17) | 242 | 31 / 0 | 1.73 (7) | 0 | as above |
| delta 0.25, no checks | PASS | 144.72 (+10.92) | 253 | 42 / 0 | 2.93 (9) | 0 | bathroom 4 → 13.25; ottoman 3 → 4.67 |
| delta 0.25 + checks | PASS | 144.72 (+10.92) | 253 | 42 / 0 | 2.23 (6) | 0 | as above |
| delta 0.20, no checks | FAIL | 143.80 (+10.00) | 251 | 40 / 0 | 3.93 (13) | 0.75 | bathroom 4 → 14 |
| **delta 0.20 + checks** | **PASS** | **145.80 (+12.00)** | 257 | 46 / 0 | **1.98 (8)** | 0.25 | bathroom 4 → 14; ottoman 3 → 5 |
| delta 0.15, no checks | FAIL | 144.05 (+10.25) | 252 | 41 / 0 | 6.68 (24) | 1.25 | bathroom 4 → 14.25 |
| delta 0.15 + checks | PASS | 147.05 (+13.25) | 261 | 50 / 0 | 3.23 (13) | 0.75 | same as G1 |

No candidate put a box on a clean empty frame. Margins: found better above +4.00, boxes worse above +1.85, cluttered
empty frames worse above +1.00. Full pages: `results/2026-11-27_bluer_geom/summary.md`, `judge_*/`, `vs_own_*/`.

- **G1 passes.** Boxes not on their barrel fall from 6.68 to 3.23, at +1.30 inside the 1.85 margin. Found rises
  slightly against B4, because with the checks the folds can take a looser color step (the ottoman 4.67 → 6).
- **The bathroom fold is the weak point, as expected.** With the bathroom held out, the checks are taught by the
  glass table's jar and one pale-wood close-up only, so the fold takes milder checks (speckle under 0.35, label
  over 1.5 x). Left on the bathroom: the jar under the mid lamps (label 1.40-1.42 x) and one tin box (solidity
  0.386). Every other fold takes 0.40 and 1.25 x.
- **Do the checks cost real barrels?** On the ordinary frames: no barrel lost in G1, G2, G3 or any delta with checks.
  G1a (speckle only) loses one, a blue barrel under the cool bathroom lamp painted in stripes (solidity 0.399). On
  the parked wood desk under the cool lamp (report only), the label check costs one barrel at each of lamp 3 and 6
  (with C1: 15 → 14 and 11 → 10 of 21).
- **With the fixed colors the checks change nothing held out.** The two false boxes they would remove are each the
  only example at their place (the jar on the glass table, the pale-wood close-up). With that place held out, no
  other place teaches the check. In-sample they remove 1.6 boxes and no barrel.
- **On the contrast winner** the checks take boxes not on their barrel from 2.83 to 2.23 (9 → 6 per frame) and lose
  nothing. Under the pass rule this is NO CLEAR DIFFERENCE against C1 itself.
- **Which margin is best.** The best trade is **delta 0.20 with the checks**: +12.00 placements, 46 gained, 0 lost,
  boxes 1.98, about where today is (1.93). Delta 0.15 with the checks finds 1.25 more and draws 1.25 more boxes.
  Delta 0.30 and 0.25 draw fewer boxes than today but find 3.8 and 1.1 fewer. Without the checks, 0.20 and 0.15
  fail; with them, every delta passes.

**What the contact sheets show** (`results/2026-11-27_bluer_geom/sheets/`, looked at).
- G1 and delta 0.20 gained: real bathroom barrels, painted solid, and some ottoman barrels.
- G1's 14 boxes on frames where they rose: 5 on the jar and 1 on the tin, all in the bathroom fold (the milder
  checks); 4 on or beside real bathroom barrels (a cap, boxes beside a barrel); one on the ottoman; three on the
  parked wood desk (report only).
- Delta 0.20 plus the checks: the jar on the warm empty frame and one tin box remain.

#### Takeaway

- **Tanush's view holds on these frames.** The color step is better on the barrels, and two shape checks remove
  most of the traps it reveals. B4 with the checks passes: +13.25 placements, no barrel lost.
- The traps are told apart by **how solid the paint is** and by **a label taller than a barrel's stripe**. Width,
  height and outline do not tell them apart in a mask this ragged.
- The checks help every color step tried: B4 6.68 → 3.23 boxes, C1 2.83 → 2.23, delta 0.30 3.68 → 1.73. With the
  fixed colors they need a second place with the same trap to be learned held out.
- Weak point: the traps sit at one place, the bathroom. Its fold learns the checks from the glass table's jar alone.
  A new trap shape (a solid blue tin, a label as tall as a stripe) would pass both checks.

#### What next

1. Tanush: whether the two checks go into `detector.py` behind a flag (as a last stage, after verify), and which delta.
   The best trade measured is delta 0.20 with the checks.
2. Put the jar and the tin under a second lamp or place, so the bathroom fold is not taught by one glass-table jar.
3. Try the checks on the near-miss and self-calibration color steps (not done here).

#### Not done

- No second round. The checks as a `DetConfig` flag (they are a post-filter in the callable).
- The ring, bulge and edge measurements were measured and not used.
- `sheets.py` was renamed to `bgsheets.py` after the plan was committed (a module-name clash with the light
  experiment's `sheets.py`). Nothing else changed.
- `TODO.md`, `STATUS.md`, `EXPERIMENTS.md`, `DECISIONS.md` were not edited.
