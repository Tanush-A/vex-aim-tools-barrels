# Pre-registration: occlusion (the scorecard, then the fixes)

Written 2026-11-19, after the baseline scorecard, the three censuses and the baseline of the earlier tests, and
**before any fix was coded or evaluated**. Every design below comes from the baseline's numbers, its pictures and
its reason logs only. Scripts: `run.py` (the scorecard), `levels.py` (the earlier tests, loaded by path),
`recordings.py`, `look.py` (a viewing aid), `outline_census.py`, `edge_census.py`.

## What was asked (Tanush, 2026-11-19)

"Improve side occlusion a lot; there are a lot of missing cases: both sides cut (there is probably still enough
visible to draw an estimate for a bounding box, where you go over rather than under); a vertical cut of course; cut
by another barrel with the same colors or where the colors overlap so that it looks really off; more cases. I want
occlusion to be fixed. Either fix them or not, but let me know how good the occlusion fix actually is after."

## Baseline (`results/2026-11-19_det_occl/step1_baseline/`, git 5361d83 = `wip/detector-bottom`)

`base` = `stripe_join`, `cap_behind`, `side_hidden`, `seam_height`, `cap_seen_bottom` on.

**The scorecard** (`scorecard.md`, `summary.md`): 50 unhidden barrels of the train frames (12 HOME hand masks, 12 HOME
color model, 26 CAMPUS color model; none left out), each alone on an empty mask, hidden by one thing at a time;
3888 scenes. Found under the v2 rule against the barrel's FULL box, of n scenes:

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 of 100 | 99 of 100 | 3 of 100 |
| a straight upright edge, one side | 100 of 100 | 82 of 100 | 0 of 100 |
| a slanted edge, one side | 200 of 200 | 154 of 200 | 0 of 200 |
| both sides cut | 50 of 50 | 49 of 50 | 0 of 50 |
| hidden from above | 50 of 50 | 2 of 50 | 0 of 50 |
| hidden from below (a low thing in front) | 49 of 50 | 1 of 50 | 1 of 50 |
| a post across the middle | 49 of 50 | 9 of 50 | 0 of 50 |
| a barrel of the OTHER color, beside it | 99 of 100 | 94 of 100 | 49 of 100 |
| a barrel of the OTHER color, beside it and lower | 98 of 100 | 92 of 100 | 77 of 100 |
| a barrel of the OTHER color, straight in front | 29 of 47 | 37 of 48 | 17 of 49 |
| a barrel of the SAME color, beside it | 81 of 100 | 36 of 100 | 16 of 100 |
| a barrel of the SAME color, beside it and lower | 91 of 100 | 85 of 100 | 26 of 100 |
| a barrel of the SAME color, straight in front | 44 of 47 | 25 of 48 | 1 of 49 |
| a plain block of the barrel's body color | 100 of 100 | 99 of 100 | 5 of 100 |
| a plain block of the barrel's stripe color | 100 of 100 | 99 of 100 | 3 of 100 |

All scenes: found 2401 of 3888; a box in the right place 2521; boxes where no barrel is 63; right-place boxes too
small / about right / too big 305 / 2114 / 102. The real occluded barrels (`real.md`): HOME 9 of 10, CAMPUS 3 of 3,
BLACK 2 of 12, WOOD 7 of 63.

**The earlier tests** (`step1_baseline/levels/`): perfect HOME masks 28 / 29 (0); light / medium / heavy damage 143 (0)
/ 99 (1) / 21 (0) of 145; CAMPUS 35 / 35 (0); BLACK with label thresholds 19 / 26 (2). Eval table: HOME 28 / 1 / 0,
CAMPUS 35 / 0 / 0, BLACK 5 / 21 / 1; no box on any negative frame. Recordings: 506 boxes on 337 frames.

## What the baseline shows (reason logs, pictures, censuses)

1. **At 75 % hidden from the side nothing is tried.** What shows of the stripe is a piece about a quarter of a
   barrel wide, which is as wide as a stripe is tall: the finder's floor ("at least one stripe height wide, not
   taller than wide") refuses 94 of 100 (`stripe_refused:width`), also where the reason for the hidden side is
   known (frame edge, a block of barrel color).
2. **A straight cut gives no reason.** At 50 % hidden by a straight or slanted edge, 58 of 300 are refused as
   `side_unexplained` (stripe under 0.4 of a barrel, body and stripe ending together on both sides); the rest are
   centred on what is seen (mean overlap 0.59 for the straight edge).
3. **Can a barrel's own side be told from a cut side by its outline?** (`outline_census.md`) At its own side a barrel's
   body ends further inward at the top and at the bottom than next to the stripe: by a median 0.04 of its width (2 px
   for a barrel 54 px wide), and with the color model it is zero or negative for more than one side in twenty. A
   synthetic straight cut gives exactly 0, but a real edge is not straight to 2 px. **The data does not support an
   outline test; it is not built.**
4. **Two barrels of one color whose stripes run together are one box.** The joined stripe of two same-colored
   barrels overlapping by half is about 1.4 to 1.5 barrels wide; the finder cuts a stripe in two only above 1.4 and
   then into round(width / barrel) parts, which is 1 below 1.5. One box as wide as it may be (1.2) is drawn over
   both; the hidden barrel has none (36 of 100 found at 50 %, 28 right-place boxes too big).
5. **A barrel of the other color straight in front makes a box of the wrong color.** What shows of the back
   barrel's lower body lies between its own stripe above and the front barrel's upper body below: a band of one
   color between the other color above and below, of a stripe's height. It is boxed as a barrel of the FRONT color (21
   false boxes at 25 % hidden). `edge_census.md`: of all boxes drawn from a stripe, "neither the top nor the bottom
   seen where the stripe's row predicts it, and the seen top ends against the other barrel color" holds for 18 wrong
   boxes and 1 right one on the scorecard, and for no box on HOME, CAMPUS, the damaged masks or the recordings.
6. **A bottom that ends against another barrel is taken as the barrel's bottom** when it is within the 15 %
   tolerance: a median 5 px short for a barrel of the other color straight in front, where the bottom the stripe's row
   predicts is 1.4 px short. Beside a barrel it is the other way round (seen 0 to 2 px short, predicted 2 to 7).
   The lower of the two is the better one in all three arrangements. No such bottom on HOME or CAMPUS.
7. **A barrel behind one of its own color, straight in front:** its top is one blob with the front barrel, and
   `cap_behind` skips a piece with half its pixels inside found boxes of its color (25 of 48 at 50 %, 1 of 49 at 75 %).
8. **No stripe, no barrel:** hidden from above or from below by half or more, what shows has no band with body color
   above AND below (`stripe_not_sandwiched`, `stripe_hidden`).

## The one idea

**What is seen fixes the distance; the distance fixes the size; the box is the full barrel, placed where the seen
part allows; where nothing pins it, the box covers every place the barrel can be.**

- *Distance:* the stripe's row. A second reading must agree with it: the top or the bottom of the body seen where
  that row predicts it.
- *Size:* the camera model at that distance (width W, height H).
- *Placement, sideways:* a side with a reason to be hidden (frame edge, a found nearer barrel, body and stripe
  ending apart) lets the box extend there; the other side's seen edge then pins it: W from that edge (today's rule).
  With no reason on either side, or one on both, nothing pins it: the barrel holds the seen part, so it lies
  between (seen right end - W) and (seen left end + W). **That span is the box** ("the cover box"). It always holds
  the whole barrel; with v = the seen share of the width, its overlap with the true box is 1 / (2 - v) in width: at
  least 0.5, whatever side is hidden (centring gives (1 + v) / (3 - v) in the worst case, which is never better and is
  under 0.5 below v = 1/3).
- *Placement, up and down:* an edge is seen only where the body ends against something that is not a barrel.

## The changes (each a `DetConfig` switch, off until it passes)

### 1. `slice_box`: a narrow slice of a barrel is a barrel; unpinned, it gets the cover box (findings 1, 2)

With the switch on (and `side_hidden` on):

- (a) *The finder's floor:* a stripe piece must be at least `stripe_h_min` (0.45) x the stripe height wide
  (before: one stripe height, and not taller than wide). 0.45 is the floor the stripe's height already has.
- (b) *Exactly one side hidden for a reason:* W from the seen edge of the other side, as today, now down to the new floor.
- (c) *Both sides hidden for a reason:* the cover box (before: centred if the stripe is 0.4 wide, else no box).
- (d) *No reason on either side, stripe under `stripe_w_min` (0.4) x W:* a box only when the slice is seen from top
  to bottom: the body above and below the stripe ends where the stripe's row predicts the top AND the bottom (the
  usual 15 % / 4 px; i.e. neither edge is inferred). Then the cover box. Otherwise no box, as today.
- (e) *A piece of a found barrel's stripe is not another barrel:* a partly seen stripe that shares rows with the
  stripe of a found barrel of its body color (half the height of the shorter, as in `stripe_join`) and whose middle
  column is inside that barrel's box is skipped. (The cover box is wide; the overlap test alone would let a second
  box through.)

`cover_unpinned` (a second switch, only with `slice_box`): *no reason on either side, stripe 0.4 x W or wider:* the
cover box too (before, and with `slice_box` alone: W wide, centred on what is seen).

Expected: frame edge, straight edge, slanted edge, both sides and the two blocks found at 75 %; straight and slanted
edge at 50 % near 100; a post at 50 % found (one piece gives the box, the other is its duplicate by (e)). Risks,
written now: (i) more stripe candidates everywhere (the floor is lower): a sliver of stripe color with body color
above and below, and a full-height slice by accident, is boxed 1.6 to 1.9 barrels wide; the negatives, `clutter`,
the hand clip and the damaged masks are where it would show. (ii) `cover_unpinned` widens boxes that are centred
today: found barrels can drop under 0.5 overlap when their top or bottom is off as well (medium and heavy damage).

### 2. `stripe_two`: a stripe wider than a barrel is two barrels (finding 4)

A stripe region wider than `body_width` (1.2) x W is the joined stripes of same-colored barrels, cut into max(2,
round(width / W)) equal parts (before: only above `stripe_merge` 1.4, into round(width / W) parts). Each part of a
pair is a partly seen stripe; where it was cut the body runs on (reason (c) of `side_hidden`), at the outer end
body and stripe end together: W from the outer edge. Two parts cut from one stripe are two barrels: they are never
each other's duplicate (today two same-colored boxes overlapping by more than half are one). No new number.

Expected: same color beside, 50 % hidden, well above 36 of 100, the too-big boxes gone. At 75 % the joined stripe is
about 1.15 to 1.25 W: only part of the cell. Risk: a single near barrel whose stripe is over 1.2 x the expected
width gets two boxes (the eval table's `close` rows).

### 3. `edge_check`: an edge is seen only against something that is not a barrel (findings 5, 6)

- (a) *Not a barrel:* a stripe candidate with neither the top nor the bottom seen where its row predicts them, whose
  body color above the stripe ends against the OTHER barrel color (in at least half of the stripe's columns, within
  the 3-row gap the body walk allows plus one row), is refused. A top can be cut short by a highlight (nothing
  painted above it) or by a thing in front; a barrel-colored thing right above it and inside its own box stands
  behind it and cannot hide it. With a seen bottom the candidate is kept (a hand over the top of a barrel).
- (b) *The bottom:* when the seen bottom is kept and the other barrel color lies right under it (same test, below),
  the bottom is the lower of the seen one and the one the stripe's row predicts.

Expected: the 18 wrong-color boxes gone; other color straight in front at 25 % from 29 toward 40 of 47. Risk: (b)
moves a bottom that was within the v2 tolerance out of it where the prediction is poor (beside a barrel the
prediction is 2 to 7 px short, but then it is not the lower one).

### 4. `cap_same`: a top showing above a found barrel of its own color (finding 7)

In `caps_behind`, the boxes of the found barrels of a color are taken out of that color's pixels before the pieces
are formed (before: a piece with half its pixels inside found boxes of its color was skipped whole). What is left
above a found barrel goes through the same cap tests (barrel-wide and upper-body tall for its row; a narrow one
hidden on exactly one side; at least half of what is missing behind found nearer barrels). No new number.

Expected: same color straight in front at 50 % above 25 of 48. Risks: the paint of a found barrel outside its own
box (a rim a few px wide) is now a piece (the size tests must refuse it); an orange thing above an orange barrel
(a hand) can pass as a cap, as it already can above a blue one.

### Not built, with the reason

- **An outline test for a straight cut** (finding 3): 2 px of signal.
- **Hidden from above or from below by half or more; a post hiding three quarters:** no band with body color above
  and below is left. A top alone is boxed only behind a found barrel (`cap_behind`); a top or a bottom alone behind
  something that is not a barrel looks like any orange or blue thing. Named in the report, not attempted.
- **Two same-colored barrels whose joined stripe is under 1.2 barrels wide** (one hides three quarters of the
  other, stripes at the same rows): nothing separates them. Named.
- **The wedge of home `cluster_01`:** unchanged, no box on purpose.

## Arms

`base`; `slice` (1); `slice+cover` (1 with `cover_unpinned`); `two` (2); `edge` (3); `cap` (4); `all` (1 with
`cover_unpinned`, 2, 3, 4); `all-cover` (1 without `cover_unpinned`, 2, 3, 4).

## Acceptance rule (fixed now)

An arm passes when all of these hold against `base`:

1. **Never regress.** The eval table (`levels.py` writes `never_regress.md`; the same as `python
   barrels/tools/report.py --cand-det <arm> --base-model default`): no scenario row of HOME (leave-one-scene-out) or
   CAMPUS loses a found barrel or gains a false box (HOME 28 / 1 / 0, CAMPUS 35 / 0 / 0); no box on any negative
   frame of any set. BLACK, the wood table and Dave's rows are report only.
2. **The earlier levels.** Perfect masks, light, medium and heavy damage, CAMPUS (3a), BLACK with label thresholds
   (3b): found not lower and false boxes not higher at each.
3. **Recordings** (`recordings.py --rec <data/recordings>`): every box that appears or disappears on the campus clips
   (r1 to r4) is looked at on a contact sheet; no new box on something that is not a barrel or half off its barrel
   (a cover box that holds the whole barrel is not "half off"; it is counted and described); a box that disappears
   must have been wrong. The black and wood clips are described, not judged.
4. **The scorecard.** In no cell (kind x amount, the three pools together) is found (v2) lower or the number of
   right-place boxes lower; the false boxes of the whole card are not more (63); and found is higher in the cells the
   arm targets (`slice`: the 75 % cells of the frame edge, straight edge, slanted edge, both sides and the two
   blocks, and the 50 % cells of the straight and slanted edge; `two`: same color beside at 50 %; `edge`: other color
   straight in front at 25 %; `cap`: same color straight in front at 50 %).

Adopted on `wip/detector-occl`: `all` if it passes. Else `all-cover` if it passes. Else every switch is judged
alone; the switches that pass alone are combined, and that combination is adopted if it passes; else the single
passing arm with the largest gain on the scorecard. What does not pass stays behind its switch, off, and the
report names it. The rule is not re-picked after the results. If round 1 fails, at most one corrected round, with
a dated addendum below written before the corrected code; no third round. The test frames are never opened.

---

# Addendum, 2026-11-19: round 1, and round 2, written before round 2 was coded or run

## Round 1 result (`results/2026-11-19_det_occl/round1/`; code: the five switches as designed above, git of this commit)

| | base | slice | slice+cover | two | edge | cap | all | all-cover |
|---|---|---|---|---|---|---|---|---|
| scorecard, found of 3888 | 2401 | 3086 | 3087 | 2485 | 2412 | 2404 | 3186 | 3185 |
| scorecard, box in the right place | 2521 | 3251 | 3253 | 2615 | 2521 | 2528 | 3356 | 3354 |
| scorecard, boxes where no barrel is | 63 | 315 | 315 | 70 | 45 | 61 | 300 | 300 |
| scorecard, cells with found lower / right place lower | | 1 / 2 | 1 / 2 | 0 / 0 | 0 / 0 | 1 / 1 | 1 / 1 | 1 / 1 |
| 1 perfect masks, found / 29 (false) | 28 (0) | 28 (2) | 28 (2) | 28 (0) | 28 (0) | 28 (0) | 28 (2) | 28 (2) |
| 2 light / medium / heavy, of 145 | 143 (0) / 99 (1) / 21 (0) | 143 (5) / 132 (13) / 43 (0) | same as slice | as base | as base | as base | as slice | as slice |
| 3a CAMPUS / 3b BLACK | 35 (0) / 19 (2) | 35 (1) / 19 (2) | same | as base | as base | as base | as slice | as slice |
| eval table HOME, found / missed / false | 28 / 1 / 0 | 28 / 1 / 3 | 28 / 1 / 3 | 28 / 1 / 0 | 28 / 1 / 0 | 28 / 1 / 0 | 28 / 1 / 3 | 28 / 1 / 3 |
| eval table CAMPUS | 35 / 0 / 0 | 35 / 0 / 1 | 35 / 0 / 1 | 35 / 0 / 0 | 35 / 0 / 0 | 35 / 0 / 0 | 35 / 0 / 1 | 35 / 0 / 1 |
| campus clips: boxes appearing / disappearing | | 21 / 0 | 21 / 0 | 0 / 0 | 0 / 0 | 1 / 0 | 22 / 0 | 22 / 0 |

**Verdict of round 1.** `edge` passes all four rules (18 false boxes gone, other color straight in front at 25 %: 29 →
39 of 47; no frame of the recordings changes). Nothing else passes:

- `slice`, `slice+cover`, `all`, `all-cover` **fail rules 1, 2, 3 and 4**: false boxes on HOME (3) and CAMPUS (1), on
  the perfect and the damaged masks, 20 wrong boxes on the campus clips (`round1/by_eye.md`), 252 more false boxes on
  the scorecard. They also find the most: 75 % hidden by an edge, the frame or a block goes from 0 to 5 of 100 to 58 to
  97 of 100; medium damage 99 → 132.
- `two` **fails rule 4**: 7 more false boxes on the scorecard (found 2401 → 2485, no cell lower).
- `cap` **fails rule 4**: one cell lower (same color beside and lower, 75 %: 26 → 25); and **rule 3**: one orange cap
  box on the hand in campus clip r4, frame 020, above an orange box `base` already draws on a pen under the hand.
  This is the risk written above ("an orange thing above an orange barrel"). Correction C below does not address
  it: if that box is still drawn in round 2, `cap_same` stays off.

## What was wrong (from the round-1 reason logs and pictures)

`slice_box`. Of its 248 new false boxes on the scorecard, 219 come from a piece the old floor refused (narrower than
a stripe is tall, or taller than wide) **with a top or a bottom that is not where the piece's row predicts it**: 229
such boxes are false and 35 right, against 20 false and 671 right when both edges are seen. The six false boxes on
HOME and CAMPUS and the 20 on the campus clips are all of this kind: an upright sliver of one color between two
barrels, or the top of a barrel's stripe under its lid, with a found barrel beside it as the "reason". I had asked
for the full slice only when no side has a reason (PREREG 1 (d)); a reason for a side says where a barrel would
be, not that there is one. 12 more come from the cover box drawn for a narrow stripe with a reason on both sides,
again with an inferred edge.

`stripe_two`. All 7 new false boxes are one barrel cut in two: the near barrel of campus `plain_01` (and
`topstripe_01`), whose stripe is more than 1.2 x the width its row predicts. The width from the row is too small
there (near barrels are up to 1.28 x the predicted width, `size_check.md`); the barrel is also taller than predicted
by as much.

`cap_same`. Taking the found boxes out before the pieces are formed also trims the caps that were found before (a
cap less than half inside a found box): 4 right boxes are lost for 12 gained.

## Round 2: three corrections (same switches, same rule)

**A. `slice_box`: what the switch adds is drawn only for a full slice.** (i) A piece the old floor refused is a barrel
only when neither its top nor its bottom is inferred, with or without a reason for a side. (ii) The cover box for a
stripe under 0.4 x W is drawn only for a full slice, also when both sides have a reason. A piece that passes the old
floor with exactly one reason is treated as before the switch. No new number.

**B. `stripe_two`: the barrel width a stripe is compared with is the larger of two readings**: the width its row
gives, and the width of a barrel as tall as the body seen above and below it (seen height x W / H). Two barrels side
by side are not taller than one; a single barrel that is wider than predicted is also taller. No new number.

**C. `cap_same`: nothing found before is trimmed.** The pieces are formed as before. A piece that was skipped as
"half inside found boxes of its color" is not skipped: the parts of it that lie outside those boxes are tested as
caps. A piece that was tested before is tested as before.

`edge_check` is unchanged.

**Acceptance and adoption in round 2.** The rule above, unchanged, against `base`. Adopted, in this order: `all` if it
passes; else `all-cover`; else the switches that pass alone, combined, if the combination passes (round 1's `edge`
passed and is not changed, so it is adopted in any case); what does not pass stays off behind its switch and is
named. Known before the run: with A, about 17 of `slice_box`'s new false boxes on the scorecard remain (full slices
by accident, most of them an orange box where a hand touches the top of a far blue barrel in the source frame), so
`slice` alone will probably still fail the false-box count of rule 4 and `all` will be near it. This is a second
attempt made after seeing round 1 on the train frames and the recordings; the test frames are untouched and remain
the only unbiased check. There will be no round 3.
