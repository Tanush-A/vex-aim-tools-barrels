# Pre-registration: the barrel as its own color reference (2026-11-26, TODO E6, first idea)

Written 2026-11-26 on branch `wip/exp-selfcal`, **before any run through the judge**. Train frames only. No test frame
is opened, scored or listed. Nothing that runs by default is changed: the method is a new module
(`src/barrels/selfcal.py`) that nothing calls, and the candidates are functions in this folder.

## The question

The fixed colors find 211 of 307 barrels on the ordinary train frames (133.8 of 172 placements). Hand-set ranges per
condition find 281, so a range per place is enough; the problem is knowing it. Whole-frame statistics cannot tell,
because barrels are 4 % of the pixels.

**Can a barrel that is already found, or half found, tell us this frame's colors, per frame, with nothing carried
between frames and no pixel changed? Does that find more barrels without drawing more boxes where no barrel is?**

## The method (fixed here; `src/barrels/selfcal.py` at this commit)

1. **First pass.** Today's detector: the fixed colors, the mask, the boxes.
2. **Seeds.** Three kinds, each a box.
   - `found`: a box of the first pass with no flag (not partly hidden, not cut by the frame, no edge guessed).
   - `body`: one strict color with a gap in it. The gap has that color above and below in every column, and the
     thickness and width of a stripe. The stripe is there but not painted.
   - `stripe`: a band of one strict color with the thickness and width of a stripe. The body is there but not painted.
   - Size. The band's row gives the width a barrel must have there. The band must be 0.55 to 1.25 of it. The box is
     then as wide as the band, and its top and bottom come from the camera geometry at that scale.
3. **The photo check** (the guard against a seed that is not a barrel). Three bands are read from the photo: upper
   body, stripe, lower body, in the centre columns. For a `found` seed they sit at fixed shares of the box. For a
   half-found seed they sit around the seen stripe or gap. A seed is kept only if:
   - the part that made it a seed is painted on at least half of its band;
   - both body bands differ from the stripe band in log(R/B) by `rel_margin`, with the sign of the seed's color;
   - a part that had to be read (painted on under 0.8 of its band) does not look like what is around the box. Its read
     range (hue, saturation, brightness: 5th to 95th percentile, plus a margin) may match at most one side of the
     surround. Stripe: left and right. Body: left, right, above, below.
4. **What a kept seed changes.**
   - `local`: its read part is painted inside its own box with the range read on it. This cannot flood.
   - `frame`: its two readings widen the frame's ranges for the two colors. Bounds: a range only widens; a hue end
     moves at most `hue_move_max`; the saturation floor never goes under 60; a reading counts only if it is one color
     (at least half its pixels at S >= 60, at least 20 such pixels, hue spread at most 12); several readings must agree
     (median hues within 6 of their median, else the odd ones are left out, and if fewer than half agree none is
     used); a widened range that newly paints more than `flood_max` of the frame, not counting paint inside the kept
     seeds' boxes, is taken back.
5. **Second pass.** The frame's ranges give a new mask, the local paint is added, the same detector runs. A second-pass
   box of the other color on a kept seed's box is dropped. Then the boxes are combined: **every first-pass box stays
   as it is**; a second-pass box is added only where no first-pass box is (less than half of the smaller box inside
   the other).

Nothing is carried from one frame to the next. Pixels are never changed. No learned model.

## The candidates

| name | seeds | what a seed changes | numbers chosen per fold |
|---|---|---|---|
| `A_found` (idea A) | found boxes | frame ranges | `found_flags` none / any, `hue_move_max` 6 / 10, `flood_max` 0.01 / 0.03 (8 settings) |
| `B_local` (idea B, on the seed only) | body gaps, stripe bands | local paint | `rel_margin` 1.0 / 0.5 (2 settings) |
| `B_frame` (idea B, as written in the brief) | body gaps, stripe bands | frame ranges | `rel_margin` 1.0 / 0.5, `hue_move_max` 6 / 10, `flood_max` 0.01 / 0.03 (8 settings) |
| `AB` (**the main candidate**) | all three | local paint and frame ranges | the same 8 settings |
| `AB_noguard` (idea C, the guards switched off) | all three, shape only | both | none: photo check, surround, agreement, one-color rule, flood limit and seed color rule are all off |

Code: `candidates.py` (`fit_A_found`, `fit_B_local`, `fit_B_frame`, `fit_AB`, `detect_noguard`). Run: `run.py`.

## How every number is chosen

**Per fold, never on the place that is judged** (`candidates.py`, `choose`). For each held-out place, every setting of
the family's grid and the fixed detector are counted on the frames of the other seven places, the way the judge counts.
A setting is out if, against the fixed detector on those frames, it breaks one of the judge's box clauses: boxes that
are not on their barrel up by more than 1.85, any more box on a clean empty frame, or boxes on cluttered empty frames
up by more than 1.0. Of the rest, the setting that finds the most placements wins. A tie keeps the more careful one
(the grids are ordered careful first: higher `rel_margin`, smaller move, smaller flood limit). If no setting finds more
than the fixed detector, the fold uses the fixed detector.

Why these grid values. `rel_margin`: the review's table Q3 puts 99.5 % of ordinary barrels and 0.3 % of random
patches above 0.5, and 98.2 % and 0.05 % above 1.0. `hue_move_max`: the largest shift of a condition's median hue in
the review's table Q1 is about 7 (orange 14 to 15 on the ottoman, 1 on the gray table, against 7 at home). `flood_max`:
barrels cover a median 4 % of a frame.

**Copied from elsewhere, not tuned here.** The band positions in a box (review, color physics, step 0). The stripe
thickness window 0.45 to 1.6, the smallest piece 20 px, the smallest barrel width 16 px, the reach of three stripe
heights, the 3 x 3 closing (all `DetConfig`). "On a box" = half of the smaller box inside the other (`counting.py`).
The side wall is 9 mm above and below a 6 mm stripe (`geometry.py`).

**Set once by me and never varied.** Painted on half of the band to be a seed; under 0.8 to be read. Percentiles 5 and
95. Margins: hue 3, saturation 20, brightness 15. A side "looks like" at half its pixels; at most one side. Saturation
floor bound 60. Agreement 6 hue units. Hue spread 12. At least 20 colorful pixels. A band holds a pixel in 0.85 of its
columns.

**Decided while looking at all eight places (in-sample; NOT held out).** These are design choices, each made after a
picture or an in-sample count showed a failure. The leave-one-place-out fit does not protect them.

1. The width window went from 0.8 to 1.25 down to 0.55 to 1.25, with the box sized by the band. Reason: on the soft
   ottoman every barrel is 0.6 to 0.7 of the size its row predicts.
2. Thickness is the median over columns, not the band's row range, and the "fills 0.6 of its box" test became "holds a
   pixel in 0.85 of its columns". Reason: a near barrel's stripe is curved.
3. The bands of a half-found seed sit around the seen stripe, not at fixed shares of the box. Reason: on a near barrel
   the stripe sits lower in the box.
4. A second-pass box of the other color on a kept seed is dropped. Reason: under the warm bathroom lamp the door
   paints orange, and a blue body painted under it read as an orange barrel.
5. A reading must be one color to move a frame range. Reason: a noisy reading widened orange to hue 23 and a yellow
   note got a box.
6. The flood limit does not count paint on the kept seeds, and went from 0.10 of the frame to the grid 0.01 / 0.03.
   Reason: a near barrel is 4 to 5 % of the frame by itself, and at 0.10 the bathroom door and tiles got a box.
7. Tried and dropped: a second round of seeds on the second-pass mask (found fewer); keeping the second-pass boxes
   and adding the first-pass ones (same found, more boxes off their barrel, one barrel lost).

## What counts as success

- **Main:** `AB` is PASS under the standard pass rule (`docs/EVAL.md`), leave one place out. A PASS less than 2
  placements above the gain margin (under +6.0) is WEAK and is called so.
- **Guards:** under each fold's chosen setting, no kept seed on an empty frame of an ordinary condition, and `AB` draws
  no more boxes on empty frames than the fixed detector. Every kept seed that is not on a hand box is listed.
- Every candidate is reported with its verdict, also the ones that lose.

**Predictions, written before the runs.** `AB`: PASS, +12 to +15 placements, most of it on the bathroom floor, the
ottoman and the gray table; nothing on the warm ottoman. `B_local`: PASS, a little under `AB`. `B_frame`: PASS, under
`B_local`. `A_found`: at the margin (NO CLEAR DIFFERENCE or a weak PASS), because a sure found barrel exists mostly
where the colors are already right. `AB_noguard`: more boxes that are not on a barrel, and boxes on empty frames;
it may FAIL.

## Reported, never judged

- How often a usable seed exists, per condition: frames with barrels, frames with a kept seed, seeds by kind.
- What the guards did with seed candidates that are not on a barrel, on empty frames, clutter frames and plain frames.
- Painted pixels outside the hand boxes (grown 4 px), first pass against second pass, per condition.
- The extreme conditions (wood under the lamp, black table, dark ottoman).
- **The colors carried across the frames of one condition** (one table under one light): every frame also gets the
  readings of the kept seeds of the other frames of its condition. This is what a robot working in one room for a
  session could do. It uses other frames, so it is not a per-frame candidate and gets no verdict.

## What I looked at before writing this (honesty)

Everything below is in-sample: all eight ordinary places and the extreme conditions, train frames only.

- `explore0.py`: the first pass on every frame: which barrels are found and with which flags. A sure (unflagged)
  found box exists in 65 of 132 ordinary frames with barrels, and in none on the bathroom floor under the mid and warm
  lamp or on the ottoman under the cool and warm lamp.
- `explore1.py`: hue, saturation and brightness of the body and stripe bands at every unflagged hand box, per
  condition, and the share of each band the fixed ranges paint.
- `explore2.py`, four times, as the method changed (the design list above). Found on the ordinary frames, counted
  per frame of 307 and per placement of 172, in-sample, fixed numbers on all places:

  | version | A, found boxes | B local | B frame | AB | AB, rel 1.0 |
  |---|---|---|---|---|---|
  | 1 (first build) | 218 (138.7); any flag: 227 (142.4) | 237 (143.4) | 228 (142.9) | 246 (146.8), boxes off barrels 3.3 | |
  | 2 (design 1, 2, 4, 5) | 217 (138.4); any flag: 226 (142.1) | 244 (145.5) | 231 (144.2) | 250 (148.3), 2.9 | 250 (148.3), 2.6 |
  | 3 (design 3) | | 243 (146.0) | 235 (144.6) | 250 (148.3), 2.4 | 250 (148.3), 2.2 |
  | 4 (design 6, as registered) | 217 (138.4) | 243 (146.0) at rel 1.0 | 236 (144.8) | 251 (148.6), 2.4 | 251 (148.6), 2.2, no box on an empty frame |

  The fixed detector: 211 (133.8), boxes off barrels 1.9. So I know roughly what the main candidate scores in-sample
  (+14.8 placements), per condition, and which frames get a new box. I have not seen any verdict, any
  leave-one-place-out number, or any run of `AB_noguard`.
- Kept seeds that were not on a hand box, seen in-sample: a red and orange toy on an empty bathroom frame
  (`lampcool6_bathtile_neg_02`, rel 0.53 to 0.59), a blue thing on `window_abpwhite_occlx_13` (0.90 to 0.95), a blue
  thing behind the glass table (`window_glass_core_01`, 1.0, gone after design 3), and one on an extreme empty frame
  (`lampmid3_ottoman_neg_02`, 0.87). So I know that `rel_margin` 1.0 removes all of them in-sample. The lowest value
  on a real barrel was 1.07 at that setting.
- Pictures (photo, first-pass mask, second-pass mask, boxes) of: `lampwarm6_bathtile_core_01`,
  `lampmid6_bathtile_touch_01`, `lampmid3_bathtile_core_01`, `lampmid3_bathtile_clutter_01`,
  `lampcool6_bathtile_neg_02`, `lampcool6_ottoman_core_01`, `lampcool6_ottoman_clutter_01`,
  `lampmid6_ottoman_core_01`, `lampmid6_ottoman_touch_01`, `lampwarm6_ottoman_core_01`, `both_abpgray_touch_01`,
  `both_abpgray_core_01`, `window_glass_core_01`, `lampcool6_glass_clutter_01`.
- From the review (read, not re-measured): 49 of 63 clean missed barrels have one color at full strength; the
  relative-color test passes 220 of 220 ordinary barrels at 0.3.
- Not seen: any judge verdict for any candidate; any held-out number; any test frame.

## What would make me distrust the result

- The gain sits at one place only (the judge prints it by place).
- A PASS within 2 placements of the margin.
- The folds pick different settings and the result depends on which.
- The honest limit of this design: the method was shaped on all eight places. Only three numbers are held out. The
  held-out verdict is therefore optimistic by an amount I cannot measure here; a new place or the test frames are the
  only clean check.

## Outputs

`results/2026-11-26_selfcal/`: one folder per candidate (`judge.md`, `judge.json`, `changes.csv`), `summary.md`,
`summary.json`, and `sheets/` (contact sheets of every barrel gained or lost and every new box off its barrel; images
are not committed). `ENTRY.md` in this folder: the experiment-log entry.

A second round, if any, gets a dated addendum to this file, committed before it runs.
