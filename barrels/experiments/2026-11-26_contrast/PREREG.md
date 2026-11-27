# PREREG: the stripe by color difference, then the barrel's own colors (C4, part of C6)

Written 2026-11-26 on branch `wip/exp-contrast`, and committed before any judged run. "Judged run" = `run.py` of this
folder, or any call of `judge.judge` / `judge.compare` with leave one place out. Train frames only. Nothing that runs
by default is changed. `detector.py` is not edited.

## The question

The fixed color step asks of each pixel "is this the home orange, is this the home blue". Under another light one of
a barrel's two colors fails that test, and the detector, which needs both, drops the barrel (57 of 63 clean misses).

Can the barrel be found from a color DIFFERENCE instead: a band that is bluer (or redder) than what is right above it
and right below it, by a margin, at the size its row predicts? And once it is found, can that barrel's own two
colors, read from the photo at that place, paint it well enough for today's detector to box it?

Known before this experiment (review of 2026-11-26, at KNOWN barrel locations): the sign of the difference with a
margin of 0.3 holds for 220 of 220 ordinary barrels; 0.63 % of random triplets pass. Nobody had run it as a detector.

## The method (code: `src/barrels/contrast.py`, unit-tested, imported by nothing that runs)

1. **The channel.** `log((R + 8) / (B + 8))` per pixel. Pixels darker than 25 or with a channel at 250 or more are
   left out of every mean. No pixel is changed.
2. **What the row predicts.** For each row taken as a stripe's middle, the camera model gives the stripe's rows, the
   barrel's top, bottom and width. The stripe band is the middle 60 % of the stripe's rows. The two body bands start a
   quarter of a stripe height beyond the stripe and are 0.9 stripe heights tall, never leaving the barrel.
3. **The sandwich, per pixel.** The smaller of (upper minus stripe) and (lower minus stripe) when both have one
   sign. Positive: an orange barrel's blue stripe. Negative: a blue barrel's orange stripe.
4. **A candidate.** At least half of the columns of a window 0.8 barrels wide pass a margin of 0.5 with one sign, and
   the mean size of the score over the window (the *strength*) is at least a floor. The strongest first; a weaker
   point inside a stronger one's predicted box is dropped. The point is moved to the middle of its stripe.
5. **The barrel's own colors.** Body = the two body bands, stripe = the stripe band, read in (log R/G, log B/G,
   half of log brightness), over the middle 60 % of the predicted width. Also read: what is left of, right of, above
   and below the predicted box.
6. **The guards**, each on or off (the folds choose):
   - *own colors apart*: body and stripe at least 1.1 apart in that space;
   - *absolute check*: the part that should be orange (an orange barrel's body, a blue barrel's stripe) reads at
     least 0.8 in the red-against-blue channel. Orange is the stable paint (review: 1.26 to 2.23 in the ordinary
     conditions);
   - *one body*: the upper and the lower body band differ by at most 0.42 of the body-stripe distance;
   - *extent*: what is right above the predicted top and right below the predicted bottom each differ from the body
     by at least 0.15 of the body-stripe distance.
7. **The paint.** Inside the predicted box grown by 8 %, and only where the fixed model painted nothing: a pixel is
   body when body is the nearest of (body color, stripe color, the distinct things around the box) and nearer than
   0.6 of the body-stripe distance. Stripe likewise, within 0.75 stripe heights of the predicted stripe rows.
8. **The boxes** always come from `detector.detect(mask)` with `DetConfig()`. Three ways to use the paint:
   - **add**: today's boxes are kept as they are. Candidates inside one of them are left alone. The rest are painted
     into the fixed mask, the detector runs again, and a box of the second run is added when it is on none of
     today's boxes. A barrel found today cannot be lost.
   - **merge**: every candidate is painted into the fixed mask; the detector's answer on that mask is the answer.
   - **alone**: fixed colors off; the mask holds the contrast path's paint only.

Fixed, not chosen in any fold: everything in 1 to 5 and 7 (channel, offset 8, margin 0.5, share 0.5, the band
layout, the paint numbers), and the four guard thresholds (1.1, 0.8, 0.42, 0.15).

## The candidates (families: `table.py`)

Chosen inside each fold: the strength floor and which guards are on.

| name | what | settings |
|---|---|---|
| **C1** (primary) | add; strength floor 1.3 / 1.15 / 1.0; each of the four guards on or off | 48 |
| **C2** | merge; the same grid | 48 |
| **C3** | add; no guard at all; strength floor 1.5 / 1.3 / 1.15 / 1.0. Shows what the size for the row and the difference give alone | 4 |
| **C4** | add; the grid of C1 without the absolute check. C1 against C4 says whether the absolute check helps or hurts | 24 |
| **C5** (report only) | alone: the numbers C1's fold picked, fixed colors off. Shows how far relative color goes by itself. Its verdict is printed and is not a result | (C1's) |

## How every number is chosen

Leave one place out, by the judge (`judge.leave_one_place_out`). For each of the 8 places, on the ordinary train
frames of the other 7 (the rule of the 2026-11-26 light experiment, unchanged; `table.choose`):

1. Every setting of the family and today's detector are run on every training frame and counted with the judge's own
   counting.
2. A setting is *allowed* when the standard pass rule does not call it FAIL against today's detector on those places.
3. The allowed setting with the highest gain wins. Gain = found (per placement) minus boxes that are not on their
   barrel (per arrangement), both as differences from today.
4. A tie goes to the setting that comes first in the family (the most cautious: a guard on before off, a high floor
   before a low one). No allowed setting with a gain above zero: today's detector, unchanged.

The held-out place is then scored by that setting. The extreme conditions are printed, never judged; a parked place
of its own is scored by the pick on all eight ordinary places.

## What counts as success

- **The verdict of the standard pass rule** (`docs/EVAL.md`) for C1, leave one place out, against today's default.
  PASS = found up by more than 4.0 placements, boxes that are not on their barrel not up by more than 1.85, no place
  down by more than its margin, no box on a clean empty frame, boxes on empty frames with clutter not up by more
  than 1.0. A PASS under +6.0 placements is WEAK and is called that.
- Reported for every candidate, pass or fail: found per placement and per frame; boxes that are not on their barrel;
  boxes on empty frames; the per-place table; the bathroom floor, the ottoman and the gray table by name; every
  barrel gained and lost; the five named trap frames (`lampmid3_bathtile_neg_02`, `lampmid6_bathtile_neg_02`,
  `lampwarm6_bathtile_neg_02`, `lampwarm6_glass_neg_02`, `lampmid6_glass_neg_02`) with the boxes on them; the extreme
  conditions; the time per frame.
- What I expect, written before the run: C1 gains at the bathroom, the ottoman and the gray table and loses nothing
  (it cannot, by construction). The open question is the false boxes: whether a guard set picked on seven places
  keeps the eighth's clutter out. C3 should fail on boxes. C2 may lose a barrel at a white table. C5 should find more
  than today in the warm places and less at home.
- One round. A second round needs a dated addendum in this file, committed before it runs.

## What I looked at before writing this (all in-sample, all train frames)

Nothing below is a verdict. All of it shaped the method, so the judged run is not blind to these frames.

1. **The docs** named in the task, the code of `geometry.py`, `pipeline.py`, `judge.py`, `counting.py`, the sister
   experiment's entry and its `candidates.py` (the fold rule is copied from it).
2. **The finder against the hand boxes** (`finder.py`, all 261 train frames, ordinary, extreme and brightness 1; run
   three times, before and after two fixes to the finder). At the reference setting (margin 0.5, share 0.5, no
   guard, at most 20 candidates a frame): 211 of 211 clean ordinary barrels have a candidate on their stripe among
   the 5 strongest; all 63 that the fixed colors miss have one; 60 of 88 partly hidden ones; 98 of 108 on the extreme
   conditions (1 of 10 on the very dark ottoman); 0 of 42 at lamp brightness 1. About 1.0 candidate on no barrel per
   frame, 2.8 per empty frame. `results/2026-11-26_contrast/finder.md`.
3. **The finder grid** (`finder.py --grid`): four channels (log ratio with offset 1, 8, 16; the opponent
   (R - B)/(R + G + B)), four margins, three shares. Every setting with share 0.4 or 0.5 keeps 211 of 211. I took
   log ratio, offset 8, margin 0.5, share 0.5 from this table. `finder_grid.md`.
4. **Guard values** of candidates on barrels and of candidates on nothing: first as percentiles from `finder.json`,
   then per painted candidate (`explore_guards.py`, the 154 ordinary frames, add mode, strength floor 1.0, no
   guard; run three times). 75 painted candidates were on a barrel (73 got a box), 24 were not (17 got a box).
   **The four guard thresholds and the three strength floors were read off this table**: 1.1 (barrels 1.06 and up,
   seven false ones under it), 0.8 (barrels 0.92 and up, eight false ones under it), 0.42 (barrels up to 0.52, two
   hidden ones above it), 0.15 (barrels 0.19 and up). So the thresholds have seen every place, the held-out one
   included. What the folds choose blind is only which guards are on and the strength floor. `explore_guards.md`.
5. **Three runs through the judge's counting, in-sample, no leave one place out, no guard** (margin 0.5, share 0.5,
   strength floor 1.0, before the two finder fixes), on the 154 ordinary frames:
   - add: found 133.8 → 158.8 placements (211 → 284 per frame), boxes not on their barrel 1.93 → 16.83 (5 → 30),
     one box on a clean empty frame (`campus_light_neg_05`), 8.65 on empty frames with clutter. Bathroom 4 → 14 of
     15, ottoman 3 → 12 of 15, gray table 10 → 15 of 16.
   - merge: 157.5 (284 per frame), boxes 19.30 (35); campus -1, pale wood -1.
   - alone: 140.7 (261 per frame), boxes 18.15; home white -4, campus -5, ABP white -4.
   The printed verdict was FAIL for all three, on boxes. This is why the guards exist.
6. **Sheets I looked at** (`sheets.py`; photo, response, fixed mask, the mask the detector saw, boxes): four barrel
   frames (`lampwarm6_bathtile_core_01`, `lampwarm6_ottoman_core_01`, `lampmid6_bathtile_touch_01`,
   `both_abpgray_core_01`), the five named trap frames, and eight frames with a false box (`campus_light_neg_05`,
   `campus_light_clutter_02`, `both_abpgray_neg_02`, `lampwarm6_glass_occl_02`, `window_glass_occlx_16`,
   `window_abpwhite_occlx_15`, `overheaddim_palewood_neg_02`, `lampmid3_bathtile_neg_02`). What I saw: the false
   boxes are a jar with a red lid and a teal label, a glue stick, a blue tin with a white label, orange things with
   a blue band between them, an orange box between a blue tin and a dark book. On several the "body" was two
   different things (table above, object below) and the paint filled the whole box: that is where the *one body*
   and *extent* guards come from.
7. **Changes made after looking**: the strength floor, the *own colors apart* guard and the *one body* guard were
   added; the body bands were kept inside the barrel (they left it for close barrels); the candidate point is moved
   to the middle of its stripe (it sat about 3 rows high). A smoke test of `table.py` on three white-table frames.

## Addendum, 2026-11-26, after the judged round (written before the run it describes)

The judged round was run once (`run.py`, git 66a747d). No second round and no new candidate. After it I ran, and
none of these is a verdict: `timing.py`; `insample.py` (the cached table, all eight places); `sheets.py` on the
changes of C1 and on the named traps.

One more run through the judge, for a mechanical reason only: `candidate.py:detect_frame` is the callable another
session can import. It holds ONE setting, the one the fold rule picks on all eight places (strength floor 1.15, the
absolute check, the extent guard). I run it once through `tools/judge.py --cand-callable` to check that the callable
gives what `insample.md` says for that setting (found +23.17 placements, 278 per frame, boxes +0.50). That number is
in-sample. The result of this experiment stays C1 as judged leave one place out.

## What this cannot show

- 8 places, 2 with warm light. A guard set that holds on seven places and fails on the eighth is the likely way to
  lose, and two warm places cannot say whether a third would behave.
- The thresholds of the guards were set in-sample (item 4). The honest claim is "which guards and how strong,
  chosen blind", not "the whole method chosen blind".
- A hidden stripe gives no candidate: close-ups whose stripe is below the frame and barrels hidden from below stay
  with today's rules.
- The judge sees gains above 4 placements only.
