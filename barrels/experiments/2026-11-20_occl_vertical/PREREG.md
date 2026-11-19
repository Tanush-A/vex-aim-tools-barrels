# Pre-registration: the occlusion rows nothing handles (from above, from below, a post, same color in front or beside)

Written 2026-11-19 on branch `wip/occl-vertical` (from `wip/detector-occl`, git 085c99d), after the reason-log
attribution and two censuses, and **before any detector code was written**. Every design below comes from those
measurements only. Scripts in this folder: `attribution.py`, `census_half.py`, `census_blob.py` (measurements; they
load the scorecard harness of `experiments/2026-11-19_det_occl` by path), `vert_arms.py` (the arms), `run.py`,
`levels.py`, `recordings.py`, `check.py`, `amounts.py` (the experiment). Results: `results/2026-11-20_occl_vertical/`.

## What was asked

Tanush, 2026-11-19: keep iterating on new methods; it should work in as many cases as possible ("2 of 100 sucks");
**no false positives**. This experiment takes the seven rows of the occlusion scorecard that no switch handles.

## Baseline (`base` = the defaults of `wip/detector-occl`: `edge_check`, `cap_same` on; `slice_box`, `cover_unpinned`, `stripe_two` off)

Found under the v2 rule against the barrel's FULL box, of n scenes (re-run here, `attribution_base.md`; identical to
`results/2026-11-19_det_occl/scorecard.md`):

| what hides the barrel | 25 % | 50 % | 75 % |
|---|---|---|---|
| hidden from above (of 50) | 50 | 2 | 0 |
| hidden from below (of 50) | 49 | 1 | 1 |
| a post across the middle (of 50) | 49 | 9 | 0 |
| a barrel of the OTHER color straight in front (of 47 / 48 / 49) | 39 | 38 | 17 |
| a barrel of the SAME color straight in front (of 47 / 48 / 49) | 44 | 29 | 2 |
| a barrel of the SAME color beside it (of 100) | 81 | 36 | 16 |
| a barrel of the SAME color beside it and lower (of 100) | 91 | 85 | 26 |

Whole scorecard: 2417 of 3888 found, 45 boxes where no barrel is. Eval table: HOME 28 / 1 / 0, CAMPUS 35 / 0 / 0, no
box on any negative frame. Damaged masks, light / medium / heavy: 143 (0) / 99 (1) / 21 (0) of 145. Recordings: 506
boxes on 337 frames.

## What the measurements show

### Which test refuses the barrel (`attribution_base.md`: the reason log, every stage)

- **From above, 50 %:** what shows is the stripe and the lower body. No stripe candidate exists (no body color above
  it); the only thing tried is the stripe itself as a top of the OTHER color (44 x `cap:height`). **75 %:** only the
  lower body shows; tried as a top, refused for its width or height (37 + 12).
- **From below, 50 %:** the upper body and a line of stripe 2 to 6 rows thin. Tried as a top behind a barrel: 38 x
  `cap:not_hidden` (no found barrel is in front of it), 9 x `cap:narrow`. **75 %:** half an upper body: 32 x `cap:height`.
- **A post, 50 %:** two slices; each stripe piece is about 0.75 of a stripe height wide (median) and taller than wide:
  41 x `stripe:width` (the finder's floor: one stripe height wide, not taller than wide). **75 %:** two slivers, stripe
  pieces 0.29 of a stripe height wide (about 3 px), 36 px in the median: `stripe:width` 36, `stripe:area` 23.
- **Other color straight in front, 75 %** (17 of 49): 16 x `cap:height`: the top that shows is 0.40 of an upper body
  in the median (0.18 to 0.50), under the floor of 0.5; 11 x a box in the right place that fails the v2 rule (bottom).
  **A threshold at its edge, not a gap:** a quarter of the height is 0.55 of an upper body before the seam pixels are lost.
- **Same color straight in front, 75 %** (2 of 49): 23 x nothing tried. The back barrel's top is within the front
  barrel's top tolerance (15 % of its height) and the front barrel's box swallows it; 7 x `cap:height` as above.
  **50 %** (29 of 48): 8 of the 19 misses have a box on the hidden barrel whose bottom is 4 to 17 px off (the allowed 3
  to 7); 11 have none (the front barrel's box starts above its own top and takes part of the back barrel's).
- **Same color beside, 50 %** (36 of 100): one box over both barrels; the joined stripe is 1.34 barrels wide in the
  median (10th to 90th percentile 0.87 to 1.48), cut today only above 1.4 and then into round(width / W) parts.
  **75 %** (16): the joined stripe is 1.10 wide (0.87 to 1.23).
- **Same color beside and lower, 75 %** (26 of 100): the hidden barrel's stripe is a piece narrower than a stripe is
  tall, next to the front barrel's upper body: 39 x `stripe:width`.

### Census 1: a stripe with body color on ONE side only (`census_half.md`)

*On 50 free-standing barrels, what one seam of the stripe says about the rest:* from the stripe's TOP seam (stripe top =
15 mm above the table at the bulge) the top row is predicted to +1.9 px in the median (10th to 90th percentile -1.0 to
+2.8), inside the usual edge tolerance (15 % of the height, 4 px at least) for 50 of 50; the bottom row to +1.2 px (-2.8
to +3.9), inside the v2 bottom tolerance for 43 of 50. From the BOTTOM seam (9 mm) the bottom row is predicted to +2.1 px
(-0.2 to +5.8), inside the edge tolerance for 50 of 50; the top row to -3.2 px (-4.4 to -1.8). For comparison the bottom
from the TOP ROW alone is +5.5 px off and inside the v2 tolerance for 25 of 50: **a seam is a far better reading than
the top row.**

*As a candidate, counted everywhere* (the funnel in `census_half.md`): bands of one barrel color with the other color
on one side only exist by the hundred (HOME 85, CAMPUS 61, the four campus clips 718). After the tests below
(not taller than a stripe; whole width; the body's far edge where the seam predicts it; the body a barrel wide; the
open side clear; the body's far edge not against barrel color) **none is left on anything that is not a barrel**:
0 on HOME, CAMPUS, BLACK, the damaged masks and all six recordings; 2 on WOOD, both on labeled barrels missed today.
The test that removes the last ones is "the body's far edge not against barrel color": without it 41 candidates in
clip r2 and 37 in the hand clip r4 remain, all inside found boxes. They are an ordinary barrel's upper body and stripe
read as "stripe and lower body" of a smaller barrel of the other color.

*Forecast on the scorecard's scenes at more amounts* (found today → today or a candidate whose band is at least 0.45
of a stripe tall → any band of 20 px or more):

| hidden | from above | from below |
|---|---|---|
| 35 % | 49 → 49 → 49 | 10 → 44 → 44 |
| 40 % | 38 → 47 → 47 | 1 → 46 → 47 |
| 45 % | 9 → 46 → 46 | 1 → 15 → 45 |
| 50 % | 2 → 40 → 45 | 1 → 2 → 40 |
| 55 % | 0 → 13 → 38 | 1 → 1 → 8 |
| 60 % | 0 → 1 → 17 | 1 → 1 → 1 |
| 75 % | 0 → 0 → 0 | 1 → 1 → 1 |

At 35 % from below 15 scenes get two boxes on one barrel: today's detector boxes a narrow sandwiched corner of the
same stripe as "partly seen". Change 1 (9) below is for that.

### Census 1, part C: a top alone, a base alone (no stripe at all)

A one-color piece, a barrel wide for its top row and no taller than an upper body ("top alone"), or a barrel wide for
its bottom row and no taller than a lower body ("base alone"), outside the boxes found today: **on things that are not
barrels: HOME 1 + 1 (a hand; a blue thing at the table edge), CAMPUS 2 (the blue cloth of `neg_04` and `neg_05`: two
NEGATIVE frames), the hand clip r4 27 (fingers, the printed box), r3 68, r2 9, r1 6.** A class mask shows a thing that
is not barrel-colored as nothing, so a lone top or base with nothing around it is the same picture as a short thing
of that color and width. Not built (below).

### Census 2 (`census_blob.md`)

- **A post.** "Two pieces of one body color, each under 0.4 of a barrel wide, at the same rows, each a full slice (its
  body ends where its row predicts the top and the bottom), outer edges 0.8 to 1.2 barrels apart": found today or
  boxed 42 of 50 at 50 % hidden (today 9), 9 of 50 at 75 %; no box where no barrel is. Everywhere else (train frames,
  damaged masks, recordings): 3 such pairs, all on labeled barrels missed today (medium damage). Without the
  full-slice test: 46 and 16, but 3 pairs on barrels found today, 1 on a non-barrel (wood) and 9 unjudged in the black
  and wood clips. At 75 % only 37 of 60 pieces are full slices: a sliver at the bulge does not reach the barrel's top
  and bottom rows.
- **A joined stripe.** A barrel standing alone has a stripe 0.88 of the width its row gives (10th to 90th percentile
  0.80 to 0.96, largest 1.04). "Wider than 1.2 x the larger of the row's width and the width of a barrel as tall as the
  body seen above and below, asked only where body IS seen right above and right below the stripe": on the scorecard
  80 scenes of "same color beside" at 25 %, 77 at 50 %, 2 at 75 %, 21 of "beside and lower"; **every one lies on two true
  barrels, none on one.** Everywhere else: one such stripe (CAMPUS), on two labeled barrels. **Why `stripe_two` made
  3 false boxes:** all three are the barrel PASTED in front (a scaled copy of CAMPUS `plain_01`'s near barrel, cut by the
  frame edge): its stripe is 183 px wide where its row gives a barrel 145 px wide, and no body color lies within 3
  rows above or below the stripe (the unlabeled seam of the source, magnified 1.9 x by the paste), so the "barrel as
  tall as the seen body" reference fell back to the row. The guard "body seen right above and below" removes all three.
- **The cap's floor.** With 0.4 of an upper body instead of 0.5: other color straight in front at 75 % 17 → 22, same
  color 2 → 8; no further gain down to 0.25. Everywhere else, at 0.4, 0.3 and 0.25: **no box appears** on any train
  frame, damaged mask or recording.
- **A narrow piece beside a found nearer barrel.** "A piece under the finder's floor that is a full slice, with exactly
  one side next to a found nearer barrel or the frame edge: a barrel wide from the seen edge of the other side":
  same color beside and lower at 75 %: 26 → 42 of 100, 1 more box where no barrel is (1 more at "beside", 75 %).
  Everywhere else: 18 on the medium-damage masks (17 on barrels missed today, 1 on a barrel found today) and 1 in
  campus clip r3 (the barrel entering at the frame edge).

## The idea, unchanged from 2026-11-19, applied up and down

**What is seen fixes the distance; the distance fixes the size; the box is the full barrel placed where the seen part
allows.** New here: a distance reading needs a second reading that agrees with it, and a hidden part is inferred
only in the direction where nothing is seen. Every box below shows the barrel's whole width, so no side is guessed.

## The changes (each a `DetConfig` switch, off until it passes)

### 1. `half_stripe`: a stripe with body on one side only, seen in its whole width

After the stripe barrels and the stripeless pieces: every connected band of one barrel color (20 px or more) that has
the other color (the body) right above it in at least 0.8 of its columns and right below it in at most 0.2 ("bottom
hidden": the upper body and the stripe show), or the reverse ("top hidden": the stripe and the lower body show). "Right
above / below" = within 3 stripe heights, as for a stripe. The seam between band and body gives the distance (the
stripe's top edge is 15 mm above the table, its bottom edge 9 mm, at the bulge). The band is a barrel's stripe when:

1. it is not taller than a stripe (`stripe_h_max` 1.6 x the stripe height the seam predicts) and at least
   `stripe_h_min` (0.45) of it tall;
2. the whole width shows: the band is `stripe_full` (0.8) to `body_width` (1.2) x the barrel width W;
3. **the second reading:** the body's far edge (its top for "bottom hidden", its bottom for "top hidden") is where the
   seam predicts it, within the usual edge tolerance (15 % of the height, 4 px at least), and inside the frame;
4. the body joined to the band is 0.8 to 1.2 x W wide;
5. the open side is clear: barrel color in the 4 rows beyond the band in fewer than half of its columns (as `edge_check`);
6. the body's far edge is a seen edge: not against barrel color (the same test beyond that edge);
7. the band is not a found barrel's (fewer than half of its pixels inside found boxes), and its box is not a found
   barrel's (same color, overlap above 0.5).

Box: the sides are the seen body and band; the seen far edge; the hidden edge where the seam's distance predicts it
(flags `occluded` and `bottom_inferred` or `top_inferred`).

8. (from the forecast) A box made earlier from a narrow, partly seen piece of the same band (its stripe lies inside
   the band's box) is replaced by this one: the band shows the whole width, the piece was a corner of it. Such a box
   does not count as "found" in test 7.

`half_thin` (a second switch, only with `half_stripe`): test 1 without the 0.45 floor: any band of 20 px that passes
2 to 7 counts. Half hidden from below leaves 2 to 6 rows of stripe; tests 2 to 6 are unchanged.

No new number. Risks, written now: (i) a barrel hidden from above AND from below (seen through a slot), showing a
short upper body over its stripe, is read as a smaller barrel of the other color hidden from above; nothing in the
mask can tell the two apart; (ii) `half_thin` leans on a line of color a few rows thin.

### 2. `post_pair`: two slices of one barrel

Stripe pieces that give no box alone (under the finder's floor, or refused as `side_unexplained`), each under
`stripe_w_min` (0.4) x W wide: two of one body color that share rows (half the height of the shorter, as
`stripe_join`), are each a full slice (the body above and below ends where the piece's row predicts the top and the
bottom), and whose outer body edges are `stripe_full` to `body_width` x W apart, are one barrel: the box is from outer
edge to outer edge, top and bottom as seen. Two barrels at one distance cannot have their outer edges within 1.2 W.
No new number. Risk: none seen in the census (3 pairs outside the scorecard, all on barrels).

### 3. `stripe_wide`: a stripe wider than a barrel is two barrels (`stripe_two` with a guard)

`stripe_two` of 2026-11-19 (a stripe region wider than `body_width` x W is max(2, round(width / W)) barrels, each part
hidden where it was cut, each with its own row; W = the larger of the row's width and the width of a barrel as tall as
the body seen above and below), asked only where body color is seen right above AND right below the stripe (the body
walk finds some within its 3-row gap on both sides). `stripe_two` itself stays as it was, off.

### 4. `slice_behind`: a narrow slice next to a found nearer barrel

A stripe piece under the finder's floor (narrower than a stripe is tall, or taller than wide) that is a full slice and
has exactly one side hidden by a found barrel standing nearer (reason (b) of `side_hidden`) or by the frame edge: a
barrel wide from the seen edge of the other side. This is `slice_box` (a) + (b) without the cover box and without the
"body and stripe end apart" reason. No new number. The sideways position of a barrel cut by something that is NOT a
barrel belongs to another branch and is not touched. Risk: 2 more boxes where no barrel is on the scorecard and one
on a found barrel at medium damage in the census.

### 5. `cap_low`: the cap's height floor is 0.4 of an upper body

In `caps_behind` the floor "at least `height_min` (0.5) x an upper body tall" becomes `width_min` (0.4): the number
that already says "narrower than this is a sliver", used for the height of a top. Nothing else changes.

### Not built, with the reason

- **A top alone or a base alone (three quarters hidden from above or from below, by something that is not a
  barrel).** No stripe, so one reading only (the width against the top or bottom row), and the census finds such
  pieces on two negative frames, on hands and on a printed box. Named "not measurable from a class mask".
- **Same color straight in front, three quarters hidden.** What shows is 0.19 of the front barrel's height above its
  top; the top tolerance is 0.15, and a top is predicted to within about 3 px. `cap_low` takes the cases just above.
- **Same color beside, stripes at the same rows, three quarters hidden.** The joined stripe is 1.10 barrels wide;
  one barrel alone reaches 1.04. Nothing separates them.
- **A post hiding three quarters,** beyond the pairs of full slices.
- **The bottoms of hidden barrels that are 4 to 17 px off** (same color straight in front, half hidden): a hidden
  bottom is an estimate; not touched here.

## Arms

`base`; `half` (1); `half+thin` (1 with `half_thin`); `post` (2); `wide` (3); `behind` (4); `caplow` (5); `all` (1 with
`half_thin`, 2, 3, 4, 5).

## Acceptance rule (fixed now; the coordinator's, made stricter where marked)

An arm passes when all of these hold against `base`:

1. **Eval table** (`levels.py` writes `never_regress.md`; the same as `python barrels/tools/report.py --cand-det <arm>
   --base-model default`): no scenario row of HOME or CAMPUS loses a found barrel or gains a false box (HOME 28 / 1 / 0,
   CAMPUS 35 / 0 / 0); no box on any negative frame of any set.
2. **Damaged masks:** false boxes at light / medium / heavy not above 0 / 1 / 0; (stricter) found not lower at any of
   the perfect masks, the three damage levels and CAMPUS; BLACK with label thresholds and the wood rows report only.
3. **Scorecard:** boxes where no barrel is, whole card, not above 45; (stricter) in no cell is found (v2) or the
   right-place count lower; found is higher in the cells the arm targets (`half`: from above 50 %; `half+thin`: from
   above 50 % and from below 50 %; `post`: a post 50 %; `wide`: same color beside 25 % and 50 %; `behind`: same color
   beside and lower 75 %; `caplow`: other color straight in front 75 % and same color straight in front 75 %).
4. **Recordings** (`recordings.py --rec <data/recordings>`): every box that appears or disappears on the campus clips
   r1 to r4 is looked at on a contact sheet; no new box on something that is not a barrel (the hand over the barrel in
   r4 is the trap); a box that disappears must have been wrong. The black and wood clips are described, not judged.

**Adoption** on `wip/occl-vertical`: `all` if it passes. Else every switch is judged alone (`half+thin` counts for
`half_thin`); the switches that pass alone are combined in the order 1 to 5, a switch staying in only if the
combination still passes; that combination is adopted. What does not pass stays off behind its switch and is named.
The rule is not re-picked after the results. At most one corrected round, with a dated addendum below written before
the corrected code; no third round. The test frames are never opened; no camera constant is changed; the image is
never corrected; nothing uses more than one frame.

Also reported, not part of the rule: the scorecard's rows "from above", "from below" and "a post" at 30 to 60 % hidden
in steps of 5 (`amounts.py`), because rule 1 works in a window of amounts that the three columns do not show.
