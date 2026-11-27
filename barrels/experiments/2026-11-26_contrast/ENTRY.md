## 2026-11-26 — The stripe by color difference, then the barrel's own colors (branch `wip/exp-contrast`)

Branch `wip/exp-contrast`. TODO item C4 and part of C6. Ready to paste into `docs/EXPERIMENTS.md`.
Plan: `experiments/2026-11-26_contrast/PREREG.md`, committed (66a747d) before any judged run. One round was run.
Nothing that runs by default was changed. `detector.py` was not edited.

### Hypothesis

1. A barrel's stripe can be found without knowing its color: it is a band that is bluer (or redder) than what is
   right above it AND right below it, by a margin, at the size its row predicts.
2. Once it is found, that barrel's own two colors, read at that place, can paint it well enough for today's
   detector to box it.
3. Added to today's boxes, this finds the barrels the fixed colors miss, by more than the noise, on places the
   numbers were not chosen on, without drawing boxes on clutter.

### Method

- **The finder** (`src/barrels/contrast.py`, 22 unit tests, called by nothing that runs). The channel is
  `log((R + 8) / (B + 8))`. For each row taken as a stripe's middle, the camera model gives the stripe band and the
  two body bands. Per pixel: the smaller of (upper minus stripe) and (lower minus stripe) when both have one sign.
  A candidate is a place where half of the predicted width passes a margin of 0.5, and the mean difference over the
  width (the *strength*) is above a floor. The sign gives the barrel's color. No pixel is changed.
- **From candidate to box.** The barrel's body color and stripe color are read from its own bands. Inside the box
  the geometry predicts (grown 8 %), a pixel is painted body or stripe when that is the nearest of (body, stripe,
  what is around the box). Only where the fixed model painted nothing. Then `detector.detect` runs on the mask.
- **Guards**, each on or off: the part that should be orange reads reddish at all (the absolute check); what is
  above the top and below the bottom differs from the body (extent); body and stripe are far apart (own colors
  apart); the two body bands are one color (one body).
- **Three ways to use it.** *Add*: today's boxes stay, candidates inside them are left alone, new boxes are added.
  *Merge*: everything is painted into the fixed mask and the detector runs once. *Alone*: fixed colors off.
- **How the numbers are chosen.** Inside each fold, on the other seven places: every setting is run and counted;
  a setting the pass rule calls FAIL there is out; the highest (found minus boxes not on their barrel) wins; a tie
  goes to the most cautious. The folds choose the strength floor (1.0, 1.15, 1.3) and which guards are on.
- **Said plainly:** the four guard thresholds (1.1, 0.8, 0.42, 0.15) and the three floors were read off an
  in-sample table of all eight places. The folds choose which guards are on, not where their thresholds sit.

### Data

Train frames only. 154 ordinary frames, 17 conditions, 8 places, 172 placements. 77 extreme frames are printed,
never judged. The finder was also measured on the 30 frames at lamp brightness 1. No test frame was loaded, viewed,
scored or listed.

### Results

#### A. The finder against the hand boxes (no detector; `results/2026-11-26_contrast/finder.md`)

Margin 0.5, half the width, no guard, at most 20 candidates a frame. A barrel counts when a candidate of its color
sits on its stripe.

| frames | clean barrels with a candidate: among the 3 strongest | among the 5 | among the 20 | of | of those the fixed colors miss | partly hidden, among the 20 | candidates on no barrel, per frame |
|---|---|---|---|---|---|---|---|
| ordinary, 154 | 196 | 211 | 211 | 211 | 63 of 63 | 60 of 88 | 1.03 (2.8 per empty frame) |
| extreme, 77 | 85 | 98 | 98 | 108 | 95 of 105 | 16 of 44 | 0.68 |
| lamp brightness 1, 30 | 0 | 0 | 0 | 42 | 0 of 42 | 0 of 15 | 0.90 |

- Every clean barrel in every ordinary condition has a candidate, among the 5 strongest of its frame.
- The predicted box fits the hand box: overlap median 0.87; 210 of 211 at 0.5 or more.
- **Where it breaks.** The very dark ottoman: 1 of 10 (the pixels are under the brightness floor). Lamp brightness
  1: none. Close-ups whose stripe is below the frame: none of 14 (no stripe, no candidate). Barrels hidden from
  below or behind another barrel: 28 of 88 have no candidate. The black table: 13 of 14.
- Far barrels were not a problem here: the smallest clean barrels (29 px tall, stripe about 5 px) are found. Rows where
  the stripe would be under 4 px are not searched.
- The channel hardly matters: log ratio with offset 1, 8 or 16 and (R - B)/(R + G + B) all keep 211 of 211
  (`finder_grid.md`). A higher margin cuts the candidates on nothing and costs hidden barrels.

#### D. The judged candidates (leave one place out; baseline 133.8 of 172 placements, 211 of 307 per frame)

| candidate | verdict | found, placements | found, per frame | boxes not on their barrel, per arrangement (per frame) | boxes on empty frames: clean / with clutter | places that moved | barrels gained / lost |
|---|---|---|---|---|---|---|---|
| **C1** today's boxes plus the contrast path, guards chosen in the fold (primary) | **PASS** | 155.3 (+21.5) | 275 | 1.93 → 2.83 (5 → 9) | 0 / 0.0 | gray table 10 → 15 of 16; bathroom 4.0 → 13.5 of 15; ottoman 3.0 → 10.0 of 15 | 64 / 0 |
| **C2** painted into the fixed mask, one detector run | **FAIL** | 142.3 (+8.5) | 248 | 1.93 → 4.83 (5 → 15) | 0 / 0.0 | bathroom 4.0 → 13.5; pale wood 13 → 12 | 38 / 1 |
| **C3** as C1 with no guard | **FAIL** | 152.1 (+18.3) | 262 | 1.93 → 5.18 (5 → 9) | 0 / 2.0 | gray table 10 → 15; bathroom 4.0 → 12.2; ottoman 3.0 → 7.0; ABP white 26 → 27 | 51 / 0 |
| **C4** as C1 without the absolute check | **FAIL** | 155.6 (+21.8) | 276 | 1.93 → 4.93 (5 → 11) | 0 / 1.0 | gray table 10 → 15; bathroom 4.0 → 13.8; ottoman 3.0 → 10.0 | 65 / 0 |
| **C5** the contrast path alone, fixed colors off (report only) | FAIL | 138.2 (+4.4) | 253 | 1.93 → 4.20 (5 → 9) | 0 / 0.0 | home 28 → 24; campus 35 → 31; gray table 10 → 14; bathroom 4.0 → 12.5; glass 14.8 → 14.0; ottoman 3.0 → 10.7; pale wood 13 → 11; ABP white 26 → 21 | 68 / 26 |

Margins: found better above +4.00, boxes worse above +1.85, cluttered empty frames worse above +1.00, a box on a
clean empty frame fails. C1's gain is 17.5 placements above the margin: not a weak pass.

**C1, place by place** (found per placement; per frame; boxes not on their barrel per frame):

| place | found | per frame | boxes |
|---|---|---|---|
| home white | 28 → 28 of 29 | 28 → 28 | 0 → 0 |
| campus | 35 → 35 of 35 | 35 → 35 | 0 → 0 |
| ABP gray table | 10 → 15 of 16 | 10 → 15 | 0 → 0 |
| bathroom floor | 4.0 → 13.5 of 15 | 16 → 54 of 60 | 0 → 2 |
| glass | 14.8 → 14.8 of 15 | 74 → 74 of 75 | 3 → 5 |
| ottoman | 3.0 → 10.0 of 15 | 9 → 30 of 45 | 1 → 1 |
| pale wood | 13 → 13 of 15 | 13 → 13 | 1 → 1 |
| ABP white | 26 → 26 of 32 | 26 → 26 | 0 → 0 |

- By light at the bathroom: cool 13 → 15, mid 1 → 13, dim 1 → 13, warm 1 → 13 of 15. At the ottoman: cool 3 → 12,
  mid 6 → 10, warm 0 → 8 of 15.
- Of the 64 barrels gained, 58 are clean and 6 are partly hidden.
- **The named traps.** No box on any of them, for any of the five candidates: `lampmid3_bathtile_neg_02`,
  `lampmid6_bathtile_neg_02`, `lampwarm6_bathtile_neg_02`, `lampwarm6_glass_neg_02`, `lampmid6_glass_neg_02`.
  The red jar with the teal label has a candidate of strength 1.09; the floor of 1.15 stops it. The blue tin has an
  "orange body" that is not reddish; the absolute check stops it.
- **C1's four new boxes that are not on their barrel** (seen on the sheets): a second, smaller box on an orange
  barrel (`lampmid3_bathtile_core_01`); an orange box on a far blue barrel beside its right blue box
  (`lampwarm6_bathtile_core_01`); two boxes on the jar with the orange lid and the blue label on glass under the
  warm lamp (`lampwarm6_glass_occl_02`). The jar is orange above and below a blue band, at the size of a barrel
  for its row. Nothing here tells it from a barrel.
- **What the folds picked.** Five of eight: floor 1.15, the absolute check, the extent guard. The other three add
  "own colors apart" (two of them with floor 1.0, one with "one body" too). The absolute check and the extent guard
  were picked in every fold.
- **The extreme conditions, C1, report only.** Orange wood under the lamp: 7 → 79 of 126 found per frame, boxes
  not on their barrel 4 → 6. The very dark ottoman 1 → 1 of 15. The black table 5 → 5 of 26.

#### One guard at a time (in-sample, all eight places, not a verdict; `insample.md`)

Around the setting the rule picks on all eight places (floor 1.15, absolute check, extent):

| change | found, placements | boxes not on their barrel | on empty frames with clutter |
|---|---|---|---|
| the pick | +23.17 | +0.50 | 0.0 |
| no absolute check | +23.17 | +2.50 | 1.0 |
| no extent guard | +23.17 | +1.50 | 1.0 |
| no guard at all | +23.17 | +5.70 | 4.2 |
| floor 1.0 instead of 1.15 | +24.42 | +5.65 | 3.0 |
| floor 1.3 | +21.25 | +0.50 | 0.0 |
| plus own colors apart | +22.50 | +0.50 | 0.0 |
| plus one body | +22.17 | +0.50 | 0.0 |
| the pick, merged into the fixed mask | +23.17 | +3.17 | 0.0 |
| the pick, alone | +6.03 | +2.07 | 0.0 |

- **The absolute check helps.** It costs no barrel and removes 2 boxes per arrangement. Judged blind, C4 (without
  it) fails on boxes where C1 passes.
- The strength floor is the sharpest number: 1.0 to 1.15 costs 1.25 placements and removes 5 boxes.
- "Own colors apart" and "one body" cost barrels and remove nothing more here.

#### Time per frame (`timing.md`, one thread, 26 frames)

Today's path: 82 ms median (fixed colors 23, detector 58). With the contrast path added: 139 ms median, 165 mean,
355 at most. The response map is 47 ms; candidates, own colors and paint are 10 ms together. The second detector
run is needed only when a candidate was painted: 4 of 26 frames.

### Takeaway

- **Relative color works as a finder.** Every clean barrel of the ordinary conditions has a candidate on its
  stripe, including all 63 the fixed colors miss.
- **Added to today's detector it passes the standard rule, leave one place out**, by a wide margin: +21.5
  placements, 64 barrels gained, none lost, 4 more boxes that are not on their barrel, none on an empty frame.
  The bathroom goes from 4 to 13.5 of 15, the ottoman from 3 to 10 of 15, the gray table from 10 to 15 of 16.
- **It needs its guards.** Without any, it draws boxes on clutter (C3). The absolute check and the extent guard
  carry that weight.
- **It must be added, not merged.** Painting into barrels that are already found adds second boxes and boxes on
  the glass table's jar (C2).
- **By itself it is not a detector.** With the fixed colors off it finds 253 per frame against 211, but loses 26
  barrels that have no visible stripe: close-ups, tipped barrels, barrels hidden from below.
- **What it cannot do.** A barrel with no visible stripe. Very dark scenes. A thing that really is orange with a
  blue band at barrel size (the jar). A barrel inside a wrong box of today's detector is left alone (the large
  orange barrel on the ottoman).
- **Caveats.** The guard thresholds saw all eight places. Two places have warm light. The gain sits at three
  places; five did not move.

### What surprised me

- A barrel's own body bands are sandwiches of the other sign (table, body, stripe). The finder needs the rule
  "the stronger candidate owns its box".
- The first version put every candidate about 3 rows too high: the response is flat over a few rows and the first
  of them was taken. Fixed before the plan was written.
- On orange wood, parked as extreme, the path finds 79 of 126 where today finds 7.
- The same paint that passes when added fails when merged.

### What next

1. **A place with warm light that the thresholds have never seen.** That is the blind test this run could not be.
2. **Use the response inside the detector's own stripe test** as soft evidence, in place of paint and a second
   run. It would also let a found stripe ask for its body.
3. **Grow the body from the stripe** by likeness to the barrel's own color, stopping at the predicted size. The
   box paint fills dark table on the ottoman.
4. **Let a candidate replace a wrong box of today's detector**, not only add where there is none.
5. **A guard for the jar**: nothing in two colors and one size separates it. The outline (a jar has a neck) or
   the side profile of the stripe might.
6. If this is adopted: the walkthrough for Tanush first, then the noise floor measured again.

### Not done

- No second round. The margin itself (0.5) and the share of the width (0.5) were fixed after the finder table;
  the folds varied the strength floor instead.
- The opponent channel was compared in the finder only, not judged.
- The side-flank guard was measured (`explore_guards.md`) and left out of the families: touching barrels and the
  dark ottoman fail it.
- `docs/ARCHITECTURE.md`: a row for the new module was added (same commit as this entry).

### Files

- Code: `src/barrels/contrast.py`, `tests/test_contrast.py`.
- Experiment: `experiments/2026-11-26_contrast/` (`PREREG.md`, `finder.py`, `explore_guards.py`, `candidate.py`,
  `table.py`, `run.py`, `insample.py`, `timing.py`, `sheets.py`).
- Results: `results/2026-11-26_contrast/` (`summary.md`, `chosen.json`, `judge_C1_add_guards/` and four more,
  `finder.md`, `finder_grid.md`, `explore_guards.md`, `insample.md`, `timing.md`).
- To judge it again: `python barrels/tools/judge.py --cand-fit barrels/experiments/2026-11-26_contrast/table.py:fit`
  (leave one place out, the judged candidate) or `--cand-callable .../candidate.py:detect_frame` (one setting,
  in-sample: found +23.2 placements, 278 per frame, boxes +0.5).
