# Pre-registration: side occlusion, and the misses left when the segmentation is good (TODO A2 + A3)

Written 2026-11-18 (the folder carries the date of the run, 2026-11-19), after the baseline run and **before any
fix was coded or evaluated**. The designs below come from the baseline's reason log, its pictures and the census
of partly seen stripes (`census.py`) only. Test: the one of `experiments/2026-11-18_det_given_seg` (its scripts
are loaded by path, `run.py`, `recordings.py`).

## Baseline (`results/2026-11-19_det_side/step1_baseline/`, git 6503924, detector as on `barrels`)

`base` = today's defaults (`stripe_join` and `cap_behind` on, `stripe_w_min` 0.4, `occl_body_side` off).
`old_side` = the 2026-11-11 fix (`stripe_w_min` 0.25 + `occl_body_side`), report only. Found / barrels (false
boxes), v2 rule, train frames only.

| level | scenario | base | old_side |
|---|---|---|---|
| 1 | perfect masks, HOME (16 frames) | 28 / 29 (0) | 28 / 29 (0) |
| 2 | light damage (5 seeds) | 141 / 145 (0) | 141 (0) |
| 2 | medium damage | 64 / 145 (22) | 99 (7) |
| 2 | heavy damage | 13 / 145 (2) | 20 (0) |
| 3a | CAMPUS, adopted color model | 34 / 35 (0) | 35 (0) |
| 3b | BLACK, thresholds from the frame's labels | 19 / 26 (2) | 19 (2) |
| 3c | wood, cool lamp, label thresholds (report only) | 25 / 42 (7) | 28 (8) |

One kind of damage at a time (report only), base: top highlight 0.5 × 0.3: 141 (0); 0.7 × 0.4: 127 (5); stripe
highlight 0.15: 117 (16); 0.3: 90 (38); stripe breaks 2 × 0.08: 93 (25); edges 1 px: 140 (0); edges 2 px: 95 (0);
dropout 10 %: 140 (0); speckle 30: 140 (0).

Eval table (`never_regress.md`; found / missed / false): HOME 27 / 2 / 0; CAMPUS 34 / 1 / 0; BLACK 3 / 23 / 1;
wood brightness 3 and 6: 7 / 119 / 4; wood brightness 1: 0 / 63 / 0; Dave 12 / 22 / 2. No box on any negative
frame. Recordings (337 unlabeled frames): `base` draws 499 boxes; `old_side` adds 8 and removes none: 4 right on
the campus clips (barrels entering at the right frame edge), 3 on the black clip (`frame_008`, `frame_037`: a
box a barrel wide, half off the orange barrel to its left; `frame_038` right), 1 wrong on the wood clip.

## What the reason log and the pictures say

1. **Campus `occl_02`** (the blue barrel behind the marker stand; `probe.py occl_02 --set CAMPUS`). The barrel's
   left edge is in view: the upper body, the stripe and the lower body all start at column 277 or 278. On the
   right the three end at different columns (upper body 294, stripe 294 to 297, lower body 311): the occluder's
   edge slants. The stripe is 16 px where the barrel is 53.6 wide (0.30); the finder asks 0.4. With the floor
   lowered, the present side rule centres the box on the stripe (IoU 0.51).
2. **The boxes half off the barrel on the black clip** (`frame_008`, `frame_037`). The stripe is painted on its
   left part only (glare), 0.36 to 0.40 of a barrel; the orange body is painted in a few columns at the left.
   The present rule "the hidden side is where a barrel-colored pixel touches the stripe at its middle row" finds
   such a pixel on the left: it is the stripe's own, one column outside the sandwiched part. So the box is
   widened to the left, onto empty table. Here too the left edge is the barrel's own: stripe and body start
   within one column of each other; on the right the body stops 11 px short of the stripe.
3. **The false boxes under damage are the same mistake.** At medium damage 21 of the 22 false boxes are
   "partly hidden" stripe boxes (seed 0 looked at one by one: HOME `close_01`, `core_01`, `cluster_01`,
   `cluster_02`; with the stripe highlight alone `touch_02`, `far_02`, `cluster_02`, `occl_02`). A highlight or a
   slit leaves a stripe piece 0.4 to 0.8 of a barrel wide; the pixel next to it is the barrel's own stripe (not
   sandwiched where the upper body is washed out) and the box is drawn a full barrel wide toward it, half off
   the barrel. In every one of these the body above and below the stripe is there and shows the barrel's real
   width (`close_01`: stripe piece 48 px, body 84 px, barrel 88).
4. **The census** (`census.py --floor 0.2`, 158 stripes narrower than 0.8 of a barrel, recordings included): on
   HOME (eval-table masks) and CAMPUS, 16 such stripes; the pixel beside the stripe is barrel-colored on both
   sides, or on neither, in 13 of the 16, so today's box is centred; the body joined to the stripe spans 0.8 to
   1.2 of a barrel in about 7 of the 16. In the campus clips nearly every narrow stripe is a barrel cut by the
   right frame edge.
5. **Stripes eaten at far range** (edges 2 px: 95 of 145; 40 refused for `height`, 10 for `width`). A stripe
   8 to 9 px tall loses 2 px at each seam and is 3 to 4 px tall, under the floor of 0.45 × the expected height.
   The body loses the same 2 px on its side of the seam, so the gap between the upper and the lower body is
   that much taller than the stripe (HOME `far_02`: stripe rows 120 to 123, gap rows 116 to 126, expected 8.3).
6. **`cluster_01`** (HOME; `probe.py cluster_01 --set HOME --level mask` and `--level loso`).
   - The middle orange barrel shows a wedge of its top between two blue barrels: `cap` refused `both_sides`.
   - With the real segmentation (eval table) the second miss is the **left orange barrel**, found from its cap on
     the hand mask. Its cap is 0.65 of a barrel wide with the right side hidden by the found blue barrel, so its
     bottom comes from its top row: predicted 173. The orange lower body seen beside the blue barrel ends at
     row 163, 10 px higher, outside the 8 px tolerance (on the hand mask: top row 117, predicted 170.5, seen
     164, inside). With the bottom at 173 the blue barrel (bottom 173) no longer "stands nearer", and the cap is
     dropped (`not_hidden`). The cause is the known bias of the bottom predicted from the top row (4 to 7 px
     low at this range, `size_check.md`), plus one row of difference in the segmentation.

## The changes (each a `DetConfig` switch, off until it passes)

### 1. `side_hidden`: a side counts as hidden only where there is a reason (A2, and finding 3)

For a stripe narrower than `stripe_full` (0.8) × the barrel width W at its row ("partly seen"). With the switch on:

0. **The finder's width floor** for a stripe is the height a stripe has at that row (about 0.24 W: a stripe piece
   at least as wide as a stripe is tall) instead of `stripe_w_min` (0.4) × W. `stripe_w_min` keeps a meaning in
   step 5. "Not taller than wide" is unchanged.
1. **What is seen of the barrel** = the stripe's columns joined with the columns of body color above and below
   it (the walk hardening (f) already uses; columns under another found stripe never count). A body span wider
   than `body_width` (1.2) × W holds a same-colored neighbour: it is not trusted and only the stripe counts.
2. **Seen span ≥ 0.8 W: the box's sides are the seen span.** The barrel is all there; only its stripe was cut.
3. **Otherwise, which side is hidden?** A side counts as hidden only for one of three reasons:
   - (a) the seen span touches the **frame edge** there;
   - (b) a **found barrel standing nearer** is there: its box holds one of the `close_px` (3) pixels beside the
     seen span at the stripe's middle row, and its bottom edge is lower than this barrel's predicted bottom.
     For this the barrels with a whole stripe are made first, then the partly seen ones, nearest first;
   - (c) **the outline is cut there**: the body (when trusted) and the stripe end at different columns, further
     apart than the edge tolerance the detector already uses (`bottom_tol` 15 % of W, at least 4 px). At a
     barrel's own edge the stripe and the body end together, because the stripe goes round the barrel; where
     something hides the barrel, or the paint is washed out, they end apart unless the hiding edge is straight
     and upright.
4. **Exactly one side hidden:** the box is W wide from the seen edge of the other side, toward the hidden side.
5. **No side or both sides:** nothing says where the rest of the barrel is. A stripe at least `stripe_w_min`
   (0.4) × W wide is centred on what is seen, as today (so this step drops nothing that is found today). A
   narrower one gives no box (log: `side_unexplained`).

The rule "a barrel-colored pixel touches the stripe" is not used when the switch is on. `occl_body_side` (h) is
contained in steps 1 and 2 and stays off. No new number: 0.8, 1.2, 0.4, 15 % / 4 px and 3 px are the detector's.

Expected: campus `occl_02` found with its box starting at the seen left edge; the black-clip boxes on the barrel
or absent; medium damage at least as good as `old_side` with fewer false boxes.
Risks, written now: (i) a barrel-sized thing of one barrel color with a patch of the other color at least a
stripe-height wide now passes steps 0 to 2 (today the patch must be 0.4 W wide): the negatives and the
recordings are where this would show. (ii) An occluder with a straight upright edge gives no reason (c): such a
barrel with under 0.4 of its stripe showing stays missed. (iii) Boxes of stripes 0.4 to 0.8 wide move from
"a barrel wide, centred" to "as wide as the body": a few px narrower.

### 2. `seam_height`: the stripe's height is read at the seams too (A3, finding 5)

Today the stripe's height is the rows its own pixels occupy (10th to 90th percentile) and must be 0.45 to 1.6 ×
the expected stripe height. With the switch on, a stripe refused as too thin gets a second reading: the mean of
that height and of the gap between the body above and the body below it (median over the stripe's columns).
Mixed pixels at the two seams belong to neither color: they make the stripe thinner and the gap taller by the
same amount, so the middle of the two readings is the stripe's height whatever was eaten. The second reading
must pass the same 0.45 to 1.6. A stripe that passes today is not re-read (shadow glued to a stripe makes the
gap too tall; hardening (b)), so the switch can only add stripes. No new number.

Expected: edges 2 px well above 95; medium and heavy higher. Risk, written now: a thin line of the other color
inside a gap between two body-colored things 1 to 3 stripe heights apart now has a stripe's height; it must
still be wide enough, sandwiched, and its box must hold body color.

### Not changed, with the reason (A3, `cluster_01`)

- **The wedge barrel: no box.** What is seen of it is the top row and a wedge 35 px wide where the barrel is 49:
  no stripe, no side, no bottom. Its presence is seen; its box is not measured. The only size cue is the top
  row, and the bottom the top row predicts is 4 to 7 px low with the provisional camera (round 1 of 2026-11-18
  drew it 8 px low). The label's own bottom is a hand estimate. Accepted as not measurable today; with the
  ruler calibration (A4) a rule "top between two found nearer barrels → a box of the expected size, centred on
  the wedge" becomes testable, and that is said in the report, not coded here.
- **The left orange barrel on the real segmentation:** explained above (finding 6). It is the calibration's
  miss, not a missing rule; the report says what a better calibration would change (`probe.py --tilt`, report
  only). No change here.

## Arms

`base`; `side` (1); `seam` (2); `side+seam`; `old_side` (report only).

## Acceptance rule (fixed now)

An arm passes when all of these hold against `base`:

1. **Never regress.** `python barrels/tools/report.py --cand-det <arm> --base-model default` (written by
   `run.py` as `never_regress.md`): no scenario row of HOME (leave-one-scene-out) or CAMPUS loses a found barrel
   or gains a false box; no box on any negative frame of any set. The black table, the orange wood table and
   Dave's set are reported rows and decide nothing (Tanush, 2026-11-18).
2. **Levels.** Level 1 not lower. Level 2 not lower at any of the three severities and no more false boxes at
   any. Level 3a and 3b not lower and no more false boxes. Campus `occl_02` found (asked of the arms that hold
   `side`; `seam` alone cannot and is judged without it).
3. **Recordings** (`recordings.py --rec <data/recordings>`): every box that appears or disappears against `base`
   on the campus clips (r1 to r4) is looked at on a contact sheet. No new box on something that is not a barrel
   or half off its barrel; a box that disappears must have been wrong. The black and wood clips are described,
   not judged.

Made the default on `wip/detector-side`: `side+seam` if it passes; else `side` if it passes; else `seam` if it
passes. What does not pass stays behind its switch, off, and the report says so. The rule is not re-picked after
the results. If round 1 fails, at most one corrected round, with a dated addendum below written before the
corrected code; no third round. The test frames are never opened.

---

# Addendum, 2026-11-18: round 1, and round 2, written before round 2 was coded or run

## Round 1 result (`results/2026-11-19_det_side/round1/`; code: the two switches as designed above)

Found / barrels (false boxes).

| | base | side | seam | side+seam | old_side (report only) |
|---|---|---|---|---|---|
| 1 perfect masks | 28 / 29 (0) | 28 (0) | 28 (0) | 28 (0) | 28 (0) |
| 2 light | 141 / 145 (0) | 141 (0) | 141 (0) | 141 (0) | 141 (0) |
| 2 medium | 64 / 145 (22) | 99 (1) | 64 (22) | 99 (1) | 99 (7) |
| 2 heavy | 13 / 145 (2) | 21 (0) | 13 (2) | 22 (0) | 20 (0) |
| 3a CAMPUS | 34 / 35 (0) | 35 (0) | 34 (0) | 35 (0) | 35 (0) |
| 3b BLACK, label thresholds | 19 / 26 (2) | 19 (2) | 20 (2) | 20 (2) | 19 (2) |
| 3c wood cool (report only) | 25 / 42 (7) | 27 (7) | 27 (10) | 28 (10) | 28 (8) |
| edges 2 px alone (report only) | 95 / 145 (0) | 100 (0) | 125 (0) | 130 (0) | 100 (5) |
| stripe highlight 0.15 alone (report only) | 117 / 145 (16) | 132 (3) | 117 (16) | 132 (3) | 134 (7) |
| top highlight 0.7 × 0.4 alone (report only) | 127 / 145 (5) | 131 (11) | 127 (5) | 131 (12) | 140 (12) |
| eval table HOME, found / missed / false | 27 / 2 / 0 | 27 / 2 / 0 | 27 / 2 / 0 | 27 / 2 / 0 | 27 / 2 / 0 |
| eval table CAMPUS | 34 / 1 / 0 | 35 / 0 / 0 | 34 / 1 / 0 | 35 / 0 / 0 | 35 / 0 / 0 |
| eval table BLACK (report only) | 3 / 23 / 1 | 5 / 21 / 1 | 3 / 23 / 1 | 5 / 21 / 1 | 5 / 21 / 1 |
| eval table Dave (indicative) | 12 / 22 / 2 | 12 / 22 / 2 | 18 / 16 / 4 | 18 / 16 / 6 | 12 / 22 / 2 |
| campus clips: boxes appearing / of them wrong; disappearing | | 4 / 0; 0 | 2 / 2; 0 | 6 / 2; 0 | 4 / 0; 0 |

No scenario row of HOME or CAMPUS loses a barrel or gains a false box in any arm; no box on any negative frame.

**Verdict of round 1.** `side` passes rules 1, 2 and 3: campus `occl_02` is found with the box (277, 127, 331, 178)
against the hand-drawn (275, 123, 328, 180); the four boxes it adds on the campus clips are barrels entering at the
frame edge; the two boxes `old_side` drew half off the barrel on the black clip are not drawn. `seam` and
`side+seam` pass rules 1 and 2 and **fail rule 3**: two boxes under the hand in campus clip r4 (`round1/by_eye.md`).
By the adoption order, round 1 alone makes `side` the default and leaves `seam_height` off.

## What was wrong (from the round-1 reason logs and pictures)

`seam_height`: the two wrong boxes are the risk written above, in its plainest form. Between two fingers a slit
of the scene shows; skin is painted orange; a blue sliver 4 rows tall in the slit (the blue barrel's body in frame
019, the orange barrel's stripe in 021) is too thin for a stripe by its own rows, and the gap between the skin
above and below gives it a stripe's height at the second reading. Both slivers are also **short**: 30 px where the
barrel is 48 wide (0.63) and 18 px where it is 44 (0.41). The stripes the switch is for (eaten at both seams at
far range) are thin but whole: erosion takes 2 px off each end of a stripe 25 to 35 px long.

`side_hidden`, in a row that does not decide (a wide highlight on the upper body alone: 11 false boxes against 5):
six new wrong boxes in HOME `cluster_01`, `cluster_02`, `far_02`. In every one the body joined to the stripe runs
on into a touching neighbour's **stripe** of the same color (an orange barrel's body beside a blue barrel's orange
stripe), so the body is wider than 1.2 barrels. Round 1 then drops the body altogether: reason (c) is not asked,
and reason (b), the found neighbour, decides alone, while the stripe is in fact cut on the other side, where the
body visibly runs past the end of the stripe (`far_02` seed 3: stripe ends at column 259, orange body below it to
271, the box is drawn from 228 to 259 where the barrel is 244 to 273).

## Round 2: two corrections (same switches, same rule)

**A. `seam_height`: the second reading is asked only of a stripe seen whole**, i.e. at least `stripe_full` (0.8) ×
the barrel width at its row. Reason: a stripe may be thin because its seams were eaten, or short because it is
partly hidden; a piece that is both thin and short is too little to call a stripe. No new number. Known cost,
accepted now: the three right boxes round 1 added on the black clip from an orange patch 22 px long are lost.

**B. `side_hidden`: reason (c) is asked of every body, trusted or not.** A body wider than `body_width` (1.2) × W
still cannot give the box (step 2) and its far end is not this barrel's edge; but where it runs past the end of
the stripe by more than the tolerance, the stripe does not end at the barrel's own edge there, whatever the body
belongs to: that side is cut. And where it ends with the stripe, that is this barrel's edge. So in step 3, (c) no
longer asks for a trusted body; with an untrusted body the seen edge of a side is the body's end where body and
stripe end together, else the stripe's end. Steps 0, 1, 2, 4 and 5 are unchanged. No new number.

Round 2 is run in two parts so that each correction is measured: first A alone on round 1's `side_hidden`
(arms `seam`, `side+seam`), then B added (arms `side`, `side+seam`). Outputs: `round2a/` and the results folder
itself.

**Acceptance and adoption in round 2.** The rule above, unchanged, against `base`; and, stricter, an arm of
round 2 must not be worse than round 1's `side` on any row the rule judges (found not lower, false boxes not
higher on levels 1, 2, 3a, 3b and on every HOME and CAMPUS scenario row; campus clips: no wrong box, no right box
of round-1 `side` lost). Made the default, in this order: `side+seam` with A and B if it passes; else `side+seam`
with A and round 1's `side_hidden` if it passes; else `side` with B if it passes; else round 1's `side` as it is
(it passed), `seam_height` off. This is a second attempt made after seeing round 1 on the train frames and the
recordings; the test frames are untouched and remain the only unbiased check. There will be no round 3.
