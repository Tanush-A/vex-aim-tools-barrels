# Experiment-log entry: what the light can be read from, and a threshold that follows it (2026-11-26)

Branch `wip/exp-light`. TODO items C3 and the light part of E6. Ready to paste into `docs/EXPERIMENTS.md`.
Plan: `experiments/2026-11-26_light/PREREG.md`, committed before any judged run. One round was run. No second round.
Nothing that runs by default was changed.

## Hypothesis

1. The color of the light can be read from one frame without knowing where a barrel is, and some places in the frame
   are better to read it from than others.
2. If the blue thresholds follow that reading, the detector finds more barrels under warm light, by more than the
   noise, on places the numbers were not chosen on.
3. The review's expectation for orange: no reading of the light predicts the orange hue the ottoman needs.

## Method

- **Part A, the readings.** Thirteen ways to pick pixels (`src/barrels/lightread.py`, unit-tested, imported by nothing
  that runs). Each gives the warmth of its pixels: the median of (R - B) / (R + G + B). Compared with the labelled
  paint inside the hand boxes (body and stripe bands of free-standing barrels). `measure.py`, `table.py`, `extra.py`.
- **Part B, blue follows the light.** The blue S floor (113) and the low end of the blue hue range (103) go down
  along a ramp as the reading goes from w0 to w1. Four numbers, a grid of 54 settings, the same grid for three
  readings (B1, B2, B3). B4 adds "bluer than the light": where the light reads warm, a pixel under the S floor is also
  blue when its own warmth is at least delta below the lower of the light and the scene. One more number.
- **Part C, orange.** The high end of the orange hue range (13) widens to 16, 19 or 22: with the light (O1), with how
  dark the scene is (O2), or everywhere it does not flood the frame (O3).
- **How the numbers are chosen.** Inside each fold, on the other seven places: every setting is run through the
  detector and the judge's counting; a setting the pass rule calls FAIL there is out; the highest (found minus boxes
  not on their barrel) wins; a tie goes to the most cautious; no gain means the fixed model.
- **The judge.** The standard pass rule, leave one place out, against today's default. `run.py`.

## Data

Train frames only. 154 ordinary frames, 17 conditions, 8 places, 172 placements. The 77 extreme frames are printed,
never judged. No test frame was loaded, viewed, scored or listed. Only two places have warm light: the bathroom floor
and the ottoman.

## Results

### A. The readings (in-sample unless it says leave one place out; the full table is `results/2026-11-26_light/readings.md`)

| reading | frames it speaks on | r with the blue paint's S | leave one place out, a line: skill | spread between conditions / inside one | largest shift on a close-up | other frames as warm as the warm ones | what fools it |
|---|---|---|---|---|---|---|---|
| `without_loose`: brightest 5 % after taking out anything barrel-like, 15 px margin | 154 | -0.96 | 0.89 | 12.5 | 0.05 | 0 of 119 | nothing in the ordinary set. On the dark ottoman it has only the wall behind to read. |
| `above_gate20`: brightest 20 % of rows 0-49 | 154 | -0.96 | 0.83 | 6.7 | 0.05 | 0 of 119 | what stands behind the table. A lamp-lit yellow note on an empty glass frame reads 0.13. The home wall reads -0.10. |
| `above_gate`: brightest 5 % of rows 0-49 | 154 | -0.95 | 0.83 | 5.3 | 0.03 | 1 of 119 | the same note reads 0.20. |
| `whole_frame`: brightest 5 % (the existing rule) | 154 | -0.95 | 0.70 | 2.1 | 0.42 | 3 of 119 | a close orange barrel (0.50 under the cool lamp), barrels on the black ottoman (0.40), the yellow note. |
| `without_barrels`: the same after taking out what the fixed model paints | 154 | -0.96 | 0.90 | 3.6 | 0.35 | 1 of 119 | the ottoman's orange, which the fixed model does not paint, so it is not taken out (0.38). |
| `max_rgb`: 99th percentile of each channel | 154 | -0.96 | 0.90 | 4.0 | 0.12 | 3 of 119 | close orange barrels, less than `whole_frame`. |
| `tiles`: lower quartile over 4 x 4 tiles | 148 | -0.94 | 0.76 | 7.3 | 0.03 | 0 of 117 | a colored table (pale wood 0.06). Says nothing on 6 dark frames. |
| `least_colored`: least colored 10 % | 154 | -0.88 | 0.65 | 6.6 | 0.02 | 7 of 119 | under a warm lamp it picks the blue barrels themselves. Reads 0.07 on the warm ottoman. |
| `gray_world`: everything below the gate | 154 | -0.84 | 0.20 | 7.2 | 0.04 | 14 of 119 | the table's own color: pale wood reads 0.18 under neutral light. |
| `above_all`: all of rows 0-49 | 154 | -0.86 | 0.70 | 6.9 | 0.05 | 13 of 119 | room content. |
| `near_strip`: bottom 80 rows | 153 | -0.70 | -0.41 | 2.5 | 0.06 | 64 of 118 | the table's own color (pale wood 0.21, black ottoman 0.00 to 0.05 under the warm lamp), a hand. |
| `highlights`: nearly clipped pixels | 116 | -0.58 | -0.18 | 2.1 | 0.29 | 20 of 92 | orange lids and the yellow note are the highlights. Nothing on the ottoman. |
| `neutral`: pixels with S under 40 | 143 | -0.35 | -0.04 | 1.9 | 0.03 | 90 of 117 | everything. Under a yellow lamp nothing white is colorless. It reads 0.01 everywhere. |

- No reading predicts the orange hue: leave-one-place-out skill between -1.07 and +0.10.
- With the parked places counted as well (wood desk, black table, very dark ottoman), `without_loose` drops to
  r -0.78 and skill 0.55. On the wood desk under the cool lamp the light reads 0.04 (neutral) and the blue paint is
  washed out anyway (S 67 to 114). `readings_extra.md`.
- The blue paint under the warm bathroom lamp: median hue 38, S 44. Under the mid lamp: hue 100, S 48 to 82.

### B and C. The judged candidates (leave one place out; baseline 133.8 of 172 placements, 211 of 307 per frame)

| candidate | verdict | found, placements | found, per frame | boxes not on their barrel, per arrangement (per frame) | boxes on empty frames: clean / with clutter | bathroom (of 15) | ottoman (of 15) | barrels gained / lost |
|---|---|---|---|---|---|---|---|---|
| **B1** blue ramp, `without_loose` (primary) | **NO CLEAR DIFFERENCE** | 137.72 (+3.92) | 225 | 1.93 → 2.68 (5 → 8) | 0 / 0.0 | 4.0 → 6.25 | 3.0 → 4.67 | 14 / 0 |
| **B2** blue ramp, `above_gate20` | **NO CLEAR DIFFERENCE** | 136.22 (+2.42) | 219 | 1.93 → 2.63 (5 → 8) | 0 / 0.2 | 4.0 → 4.75 | 3.0 → 4.67 | 8 / 0 |
| **B3** blue ramp, `whole_frame` | **NO CLEAR DIFFERENCE** | 136.97 (+3.17) | 222 | 1.93 → 2.18 (5 → 6) | 0 / 0.0 | 4.0 → 5.5 | 3.0 → 4.67 | 11 / 0 |
| **B4** = B1 plus "bluer than the light" | **FAIL** | 145.72 (+11.92) | 257 | 1.93 → 6.68 (5 → 24) | 0 / 1.25 | 4.0 → 14.25 | 3.0 → 4.67 | 46 / 0 |
| **O1** orange follows the light | **FAIL** | 133.30 (-0.50) | 209 | 1.93 → 3.93 (5 → 13) | 0 / 0.25 | 4.0 → 3.5 | 3.0 → 3.0 | 0 / 2 |
| **O2** orange follows the scene's darkness | **NO CLEAR DIFFERENCE** | 133.80 (0) | 211 | 1.93 → 1.93 | 0 / 0.0 | no change | no change | 0 / 0 |
| **O3** wide orange with a flood guard | **NO CLEAR DIFFERENCE** | 133.80 (0) | 211 | 1.93 → 3.43 (5 → 8) | 0 / 0.0 | no change | no change | 0 / 0 |

The six places without warm light did not move in found for any candidate. No candidate put a box on a clean empty
frame. Margins: found better above +4.00, boxes worse above +1.85, cluttered empty frames worse above +1.00.

- **B1 misses the gain margin by 0.08 placements.** It is "at the margin". Per frame: bathroom mid 3 lamp 1 → 3 of 15,
  mid 6 1 → 8, warm ottoman 0 → 5. The warm bathroom stays at 1 of 15.
- **B4 finds nearly every bathroom barrel** (mid 3 1 → 15 of 15, mid 6 1 → 15, warm 6 1 → 14) and fails on boxes: 16
  more boxes on nothing, and new boxes on all three cluttered empty bathroom frames.

**Traps, by name.**
- Clean empty frames: no box, any candidate.
- Empty frames with clutter: B4 boxes `lampmid3_`, `lampmid6_` and `lampwarm6_bathtile_neg_02`. O1 boxes
  `lampmid3_bathtile_neg_02`. B1 and B3: none.
- Warm-lit white objects: B2 (the reading above the gate) boxes `lampwarm6_glass_neg_02`, the frame the 2026-11-25
  round failed on. The yellow note stands above the gate and reads 0.13. B1 and B3 read 0.03 and 0.09 there and draw
  nothing. `lampmid6_glass_neg_02`: no box, any candidate.
- The glass table's reflections: found 14.8 → 14.8 and boxes 0.6 → 0.6 for every candidate but B2 (0.6 → 0.8, the
  frame above).

**What the contact sheets show** (`results/2026-11-26_light/sheets/`, every gained and lost barrel and every new box
looked at).
- B1, B2, B3 gained: real barrels. The blue stripe of an orange barrel gets painted, or the body of a blue one.
- Their new boxes are small second boxes on real barrels (a cap boxed apart from its body; a box across two touching
  barrels). None is on the floor or on clutter.
- B4 gained: bathroom barrels painted solid. Its new boxes sit on three clutter things: the red jar with a teal
  label (orange with a blue band, which is what a barrel is to the detector), the blue tin, the small figure.
- O1: the wider orange paints the whole bathroom floor. Two close-up barrels drown in it. Boxes on floor patches.
- O3: a box on the pale wood table and on the cool bathroom floor.

### Why the folds failed where the idea works (in-sample, `insample.md`; never a verdict)

| setting | found, all places | bathroom | boxes |
|---|---|---|---|
| B1's ramp picked on all eight places (0.08 → 0.18, S to 30, hue low to 88) | +7.42 | +5.75 | +0.75 |
| B1's ramp picked without the bathroom (0.11 → 0.30, S to 45) | +3.92 | +2.25 | +0.42 |
| B4 picked on all eight places (delta 0.25) | +11.42 | +9.75 | +1.00 |
| B4 picked without the bathroom (delta 0.15) | +13.25 | +10.25 | +4.75 |

- Without the bathroom, the only warm place left to learn from is the ottoman. Its blue fades more slowly, so it
  teaches a slow ramp. Its black lid has no clutter that looks blue, so it teaches the loosest delta.
- All 54 ramp settings gain in-sample (+0.92 to +6.67). All three readings give the same best in-sample result
  (+7.42). The reading is not what limits the rule. The warm end of the ramp is.
- In-sample, delta 0.30 and 0.25 pass and 0.20 and 0.15 fail on boxes.

## Takeaway

- **What to read the light from:** the bright pixels that are not barrel-like, or the rows above the gate. Both
  separate every warm frame from every other frame. The whole frame is fooled by close orange barrels. Colorless
  pixels do not work.
- **"Blue follows the light" did not pass.** +3.92 placements against a margin of +4.00, no barrel lost, no box on any
  empty frame. With the 2026-11-25 version (+5.9, weak pass), every variant lands between +2.4 and +5.9. The gain is
  real at barrel level and too small for this judge to call.
- **The gray-olive blue needs more than the two numbers, and one more number reaches it.** "Bluer than the light"
  finds 14.25 of 15 bathroom placements held out. It fails because the margin was chosen on the ottoman alone.
- **Orange: no.** The light does not predict the ottoman's orange. Following it floods the bathroom floor (FAIL).
  Darkness of the scene tells the two apart, but one dark place cannot teach itself. One hint from a place never
  trained on: on the parked black table the darkness rule picked on the ottoman finds 5 → 8 of 26, with no new box on
  nothing.
- **The limit is the data, not the idea.** Two warm places that need different numbers.

## Open point for Tanush and Dave

"Bluer than the light" changes no pixel. But comparing a pixel with the light's color is the same arithmetic as
correcting the pixel and then thresholding it. Whether that is inside "no image correction" is their call.

## What next

1. Shoot a third warm-light place before any further round (below).
2. Then one more round of B4 with the margin chosen on two warm places.
3. The same idea made local is C4 (the stripe by contrast): bluer than what is above and below it, not than the light.
4. For orange: O2 again once a second dark place exists.

## Not done

- No second round. The addendum would have had to fix the margin after seeing which one works at the bathroom.
- The local-surround form of the relative rule; blue and orange together (E8); choosing the ramp from the paint
  instead of from the detector's count; the other ten readings as detector inputs.
- No walkthrough with Tanush yet. `TODO.md`, `STATUS.md`, `EXPERIMENTS.md`, `DECISIONS.md` were not edited.

## For Tanush, in plain words

**What is the best thing to read the light from, and why?** The bright things in the picture that are not
barrel-colored. Bright things are mostly white or pale, so they show the lamp's color. Leaving out anything orange or
blue stops a close barrel from being mistaken for the lamp. Your idea, the rows above the horizon, works about as
well and is simpler. Its weak point is that it reads whatever stands behind the table: a yellow note under the lamp
made it draw a box on an empty glass frame. At the detector the three readings ended within 1.5 placements of each
other, which is inside the noise.

**What can a light-following rule fix?** Blue paint that has lost its strength under a yellow lamp but still looks
bluish (the bathroom under the mid lamp, the ottoman under the warm lamp). With one more rule, "bluer than the light",
also the blue that has gone gray-olive under the warm bathroom lamp.

**What can it not fix?** Orange on the dark ottoman: that follows the surface, not the lamp. Blue that is washed out
while the light reads white (the wood desk under the cool lamp). A scene with nothing pale in it: on the ottoman the
reading has only the wall behind. Clutter that is orange with a blue band: once blue is loosened, the jar is a barrel.

**What data would settle it?** One or two more places, three frames each (`core_01`, `neg_01`, then `clutter_01`
last):
1. **The warm lamp on a pale table or floor that is not the bathroom**, lamp at warm and at mid. This is the one that
   matters most. It gives a third warm place, so the ramp's end and the margin are no longer taught by one place. Put
   the blue tin and the red jar in the clutter frame: they are where the false boxes were.
2. **A dark table or a dark cloth under ordinary white light** (window or ceiling). It says whether the orange shift
   comes with a dark surface. Today only the ottoman says so, and the parked black table hints at it.
