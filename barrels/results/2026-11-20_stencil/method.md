# The stencil detector: the method, in the order the data flows

A second opinion on the class mask. It is not the detector: `detector.py` is untouched and nothing here runs in the
live view. Code: `src/barrels/stencil.py` (one file). What it is worth: `verdict.md`.

## The idea in one sentence

For every place a barrel could stand, cut out a paper barrel of the right size with a stripe band across it, lay it
on the mask, and count how much of it the painted pixels agree with; keep the places where enough agrees, best first,
and never use a painted pixel twice.

## 0. What goes in

The class mask the color model makes: every pixel is orange (1), blue (2) or nothing (0). Same input as the rule
detector. The photo itself is never looked at.

## 1. The stencils (`make_stencil`, `stencils`)

The camera is fixed, so a barrel's distance fixes two things at once: **how big it is and which rows it is on.**
A barrel 20 cm away is 51 px wide and sits on rows 119 to 174, wherever it stands left to right.

So there is one stencil per size: 66 of them, each 5 % bigger than the one before, from 16 px wide (60 cm away) to
401 px (touching the bumper). For each, `geometry.barrel_rows` gives the top row, the stripe's two rows and the
bottom row. A stencil is then:

```
        . . . . . . . . . .        ring (5 px above the top)
      +---------------------+
      |  /  upper body   \  |      band U: should be the BODY color
      | |                 | |
      |=====================|      (seam: 1 px not looked at)
      |       stripe        |      band S: should be the OTHER color
      |=====================|
      | |   lower body    | |      band L: should be the BODY color
      |  \               /  |
      +---------------------+
        . . . . . . . . . .        ring below; and a ring left and right
```

- Three bands. The seam rows between them are skipped (mixed pixels: on the hand masks the painted stripe is 0.80 to
  0.97 of the model's height).
- Rounded corners: in the outer fifth of the width on each side ("rim columns") the upper body starts a little lower
  and the lower body ends a third earlier.
- A ring just outside, a tenth of the width thick.

**Fit on the HOME hand masks** (`fit.md`; 12 free-standing barrels, the rule for each number written before the
numbers): the model's top row is 2.0 px too high (corrected by +2.0), its bottom row is 1.8 px too low for a far barrel
and 2.8 px too high for a near one (corrected by -4.62 + 0.0887 x width; fit between 32 and 84 px wide and extended
beyond that range, which is unchecked), seam 0.10, rim 0.208 / 0.125 / 0.333. The model's width is used as it is
(hand boxes are 0.91 to 1.06 of it).

Example: the stencil 49 px wide has upper body rows 120 to 139, stripe 142 to 151, lower body 154 to 168.

## 2. Every place (`score_map`)

A stencil's rows are fixed, so only its column is free. Each stencil is slid along its rows one column at a time,
from "one column still in the frame on the left" to the same on the right. Because the camera's rows are a few
pixels off, it is also tried up to 8 % of its width higher and lower (for the 49 px stencil: 4 rows each way, 9
tries). Everything twice: as an orange barrel (blue stripe) and as a blue one.

That is every place a barrel can be: 66 sizes x up to 9 row offsets x about 700 columns x 2 colors.

## 3. The score of one place (`score_at` is this, pixel by pixel; `score_map` is the same numbers, fast)

Go through the stencil's columns, left to right. For one column:

1. For each of its three bands: **what share of the band's pixels has the predicted color?**
2. **The column is worth its WORST band** (q, between 0 and 1). A column showing body, stripe, body is worth 1. A
   column with a stripe and nothing above it is worth 0. This is the heart of it: an orange block, a blue bar, or a
   blue thing lying on an orange thing never shows all three in one column.
3. **A band that is known to be hidden is not asked for.** Known means: outside the frame, or inside the box of a
   barrel already accepted that stands nearer (its bottom row is lower). Then the column counts only for the bands
   that were checked: the stripe is half of a column's weight, each body part a quarter.

Then three numbers for the place:

- `seen` = the average over the columns of weight x q: the share of the barrel that is seen and right.
- `missing` = the average of weight x (1 - q): checked, and not there, with nothing to explain it.
- `outside` = the share of the ring painted as if the barrel went on (body color above, below or beside the body;
  stripe color beside the stripe). It says: the thing here is bigger than this stencil. This is what picks the right
  size, because a smaller stencil inside a barrel also sees body, stripe, body everywhere.

**score = seen - 0.1 x missing - 0.5 x outside.**

Worked example, HOME `core_01` (hand mask), the orange barrel, hand-drawn box (292, 121, 342, 176). Best place:
the 49 px stencil, 4 rows down, left column 292, box (292, 123, 341, 174). seen 0.91, missing 0.09, outside 0.06:
score 0.91 - 0.009 - 0.03 = **0.87**.

## 4. Which places are barrels (`detect`)

1. Take the best-scoring place in the picture. If its score is at least **0.20** (`accept`), it is a barrel.
2. **Claim its box.** From now on those pixels are evidence for no other place. For a place standing **further
   away** they count as hidden (not asked for); for any other place they count as missing.
3. Score again and take the next best. Stop when nothing reaches 0.20.

(To save time several places are accepted in one round as long as they do not touch each other; a place touching an
accepted box waits for the next round, when its score is up to date. Same answer.)

**Where several columns fit equally well** (within 0.02 of the best) the box goes in the middle of them. That
happens when a slice of a barrel shows and nothing says which side of it is hidden.

Worked example, HOME `occl_01`: a blue barrel behind an orange one.
- The orange front barrel scores 0.86 and is accepted first.
- The blue barrel behind it, **before** the orange one is accepted: seen 0.21, missing 0.79, score **0.12**. Not a barrel.
- **After** the orange box is claimed, the part of the blue barrel behind it is "hidden", not "missing": score
  **0.72**, box (387, 116, 429, 159) against the hand-drawn (386, 115, 430, 161).

That is the whole occlusion handling. There is no rule for "a barrel behind a barrel".

More examples from the HOME hand masks: `edge_01`, the barrel half out of the frame on the left: 0.40, box
(0, 132, 35, 195). `top_01`, the close-up whose stripe is below the frame: only the upper body can be checked, a
quarter of the weight: 0.23, just over the line. `cluster_01`, the barrel that shows only a wedge between two others:
no place reaches 0.20.

## 5. The numbers, and where each came from

| number | value | from |
|---|---|---|
| `accept` | 0.20 | calibration: the smallest value with no false box on the calibration masks was 0.15; plus a margin of 0.05 |
| `absent_cost` | 0.1 | calibration grid {0.1, 0.25, 0.5} |
| `outside_cost` | 0.5 | calibration grid {0.25, 0.5, 1.0} |
| `band_full` | 1.0 | calibration grid {1.0, 0.5, 0.25}: 1.0 means "the painted share itself" (step 3.1 as written) |
| stripe weight 0.5, "checked" from half a band open, ring 0.10 of the width, size step 5 %, rows searched 8 % | chosen, not tuned | |
| top / bottom correction, seam, rim | fit on 12 barrels of the HOME hand masks | `fit.md` |

**The calibration** (`calibration.md`; rule in `PREREG.md`, written first). Masks: the 16 HOME hand masks; the same
frames through the color model (leave one scene out); the hand masks with light damage and with medium damage (seeds
10 to 14); the 10 train negatives of the wood and black tables (orange and blue clutter). For each of 27 combinations:
find the smallest `accept` with no false box, add 0.05, count the barrels found; take the combination that finds
most. Leaving one HOME scene out at a time gives the same `accept` (0.18 to 0.20) and no false box on the left-out
scene.

**What `accept` means.** A thing that is not a barrel is unpainted in the mask, like the table. So for a barrel
behind a book, "hidden" and "absent" look the same, and such a barrel gets only what is seen of it: showing the share
v of its width it scores about v - 0.1 x (1 - v). With accept 0.20 it passes from **v = 0.27** up, on a perfect mask.
At 0.15 (no margin) it would pass from 0.23. Lower than that, false boxes appear on the calibration masks.

## 6. What the method cannot do, by construction

- **Hidden from above or below by something that is not a barrel, by half or more.** No column shows body, stripe,
  body. Score near 0. Deliberate: "stripe with body on one side" is what clutter looks like.
- **A hole inside a seen barrel is scored like a missing part.** A highlight that removes the upper body in a column
  makes that column worth nothing. Tried before the evaluation (PREREG addendum A): letting a band count as "there"
  from half or a quarter painted finds more damaged barrels, but then stencils of slightly wrong size and place fit
  as well as the right one and wrong boxes appear that no `accept` removes. The calibration rule kept the strict form.
- **A slice with nothing saying which side is hidden** gets a box centred on the slice. If three quarters are hidden
  on one side that box is off by 3/8 of a width: under half overlap with the true box.
- **No stripe to check** (stripe below the frame, or behind a nearer barrel): at most 0.25. A full upper body just passes.

## 7. How to run it

```python
from barrels import stencil
barrels = stencil.detect(mask)                    # list of Barrel, like detector.detect
stencil.score_at(mask, st, color, u, dy)          # one place, pixel by pixel: score, seen, missing, explained, outside
label_image, origin = stencil.render(st)          # the stencil as a picture
```

Repeat everything: `fit_stencil.py`, `calibrate.py`, then `run_levels.py`, `run_scorecard.py <arm>`, `scorecard.py`,
`run_recordings.py --rec <recordings>`, `timing.py`, `tables.py`, all in `experiments/2026-11-20_stencil/`.
Tests: `tests/test_stencil.py` (19: the picture of a stencil, the score, the fast scorer against pixel counting, the
arbitration).
