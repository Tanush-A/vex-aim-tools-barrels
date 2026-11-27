# 2026-11-26_slack — the detector has no slack. Pre-registration

Written and committed before any judged run. Branch `wip/exp-slack`. Train frames only.

## The question

A plain barrel must pass about seventeen yes-or-no tests in a row. None can make up for another. Shaving one pixel
off the edge of every painted region loses 12 of the 63 barrels found on the two white tables, 148 → 121 on the
new conditions, 115 → 86 with hand-set colors (the audit, section 4b). Real changes in light and focus move the
mask by more than a pixel.

**Can a rule stop the detector from losing found barrels to a one-pixel change, without one new false box?**

The aim is narrow. It is not to find more barrels on the masks as they are. It is to keep the ones already found
when the mask moves by a pixel or two.

## What I looked at before writing this (the honest list)

1. The task's numbers from the audit: where the erosion kills (the stripe's height 31, its area floor 15, a bottom
   then off 5, caps 6, the stripe's width 3, the second-reading verify 3, others 9), the three cliffs, the
   single-score probe.
2. The docs named in the task, `detector.py`, `geometry.py`, `degrade.py`, `judge.py`, the plan of
   `2026-11-19_det_side` (why the second height reading is asked only of a stripe seen whole: two boxes under a
   hand in a campus clip, a blue sliver between two fingers, thin and short).
3. `results/2026-11-26_collapse/rule_counts.md` (how often each check says no, per group of masks, at defaults).
4. **The two white tables with one pixel shaved off, barrel by barrel** (`look_white.py`,
   `look_white_detail.py`; HOME and CAMPUS, 37 train frames, the fixed model's mask). With the stored model I
   count 63 → 52 (the audit counts 51 with HOME segmented leave one scene out). For each of the 11 lost barrels
   I printed the reason log and these numbers: the stripe's own height, the gap between the two body parts, the
   expected sizes, the stripe's and the body's width as shares of W, the seen top and bottom against the predicted
   ones. **The gate of candidate B was shaped by these 11 barrels.** They are a design set. What they say:
   - 8 of the 11 are refused as "height". The stripe is 3 to 4 rows tall where the floor is 3.6 to 4.7.
   - The second reading that exists would pass all 8 (6.5 to 8.0 against an expected 8.1 to 10.3). It is not
     asked: after the pixel the stripe is 0.65 to 0.73 W wide, under the 0.8 W it needs. Before the pixel these
     stripes were 0.74 to 0.82 W.
   - The pixel moves every reading at once, not one. The seam between stripe and body opens from about 1.5 to
     about 3.5 rows on each side, so the body walk (it allows 3 empty rows) no longer reaches the body. The seen
     top moves down a row; on HOME it was already 3.5 to 4 rows under the predicted top with a tolerance of 5.
   - The other 3: two caps (behind a barrel), one barrel cut at the side ("slice_not_full"). Not aimed at here.
5. The full test suite at the start of the branch: 952 pass.

**Not looked at before this was committed:** any barrel-by-barrel output for the other places, for hand-set
colors, for two pixels, for dilation, for the damage levels, for the simulated scenes; any result of any
candidate. No test frame, ever. The campus recordings are not train frames and are not opened.

## The candidates

One experiment flag in `DetConfig`: `slack`, a string of letters, default `""` (today's detector, box for box).
`A`, `B`, `C` switch one candidate on; letters combine. On adoption the chosen rule becomes plain code and the
flag goes. Everything is in stage 2 (`find_stripes`), one extra question in stage 3 (C) and one in the verify
step (the floor a small stripe was admitted with).

### A. The stripe's area floor scales with the barrel

Today a stripe needs 20 px whatever the distance. As a share of the stripe the row predicts (W × the stripe
height): 1.7 % at 15 cm, 3 % at 20 cm, 6.6 % at 30 cm, 11.6 % at 40 cm, 18 % at 50 cm, 26 % at 60 cm, 29 % at the
far end (64 cm, 69 px predicted).

With A the floor is `min(min_area_px, stripe_h_min × stripe_w_min × W × Hs)`: the smallest stripe that passes
the height floor (0.45 of a stripe height) and is wide enough for the detector to place it alone (0.4 W), and
never more than today's 20 px. **No new number.** 0.45 × 0.4 = 18 % of the predicted stripe. It equals 20 px at
50 cm and is 14 px at 60 cm and 12.4 px at the far end. Nearer than 50 cm nothing changes. The verify step's
"20 pixels of its own" uses the same floor for a box read from a stripe. Not scaled: the blob floor and the cap
and band floors (they are asked before any row is known), `min_width_px`, `min_stripe_px`.

### B. A second reading for the stripe's height, area and width, from the seams

The seams say how many pixels the color step took off this barrel's edges. With the stripe's own height `h` and
the gap `g` between the body above and below it: each color lost `e = (g − h) / 4` pixels per edge (not below 0;
at most 3, the three empty rows the body walk already allows between a stripe and its body).

- **Height** (exists today): `h + 2e`, the mean of `h` and `g`.
- **Area** (new): the stripe's pixels × `(h + 2e) / h`. Asked of a stripe under the area floor.
- **Width, "seen whole"** (new): today the second height reading is asked only of a stripe at least 0.8 W wide by
  its own pixels. With B a thin (or small) stripe is read a second time when the barrel is seen whole by either
  of two readings:
  1. the stripe's own width with the eaten pixels given back: `width + 2e ≥ 0.8 W`; or
  2. the rest of the barrel: the body walked up and down from the seams ends where the stripe's row predicts the
     top and the bottom (the usual edge tolerance; each edge may agree as seen or with `e` given back), neither
     end lies against the other barrel color, and on at least one side the stripe and the body end together
     (the usual sideways tolerance: that side is the barrel's own edge).
- A stripe accepted by the second reading is, from then on, the band between its two bodies (its box's rows run
  from body to body). So the body walk of stage 3 starts at the body, not 4 empty rows away from it.
- In the verify step such a stripe needs all of its pixels to be its own, in place of 20.

The second reading must still land in 0.45 to 1.6 stripe heights. Nothing else is loosened: the upper limits,
`on_the_table`, the sandwich, every test of stage 3 and of the verify step stay as they are.

The known false box this gate was written against (the sliver between two fingers: 30 px where the barrel is 48,
and 18 where it is 44) fails reading 1 by its numbers (30 + 2 × 1 = 32 < 38). Reading 2 asks for skin that is
exactly one barrel tall at that row and for the sliver to end with the skin on one side. I cannot check the clip
(not a train frame). A synthetic test of that shape goes into the suite.

### C. One marginal test is made up by the others

Three size floors of a stripe may be forgiven: its area, its height floor (the thin side), its least width. A
stripe that fails **exactly one** of them by at most **one pixel on each edge** (height + 2, width + 2, area + a
ring one pixel wide around its box) goes on, marked marginal. Its box is kept only if the rest fits well:

1. top and bottom both seen where its row predicts them (neither edge inferred);
2. body color above and below the stripe in at least 0.8 (`stripe_full`) of the stripe's columns;
3. the box well filled: in the stripe's columns, between the seen top and bottom, at least half of the pixels
   are barrel-colored (0.5: under the 5th percentile of the found clean barrels of the white tables, 0.49 body +
   0.085 stripe, the audit section 3.3).

Never forgiven: the row gives no distance, `on_the_table` (`min_width_px` and `min_stripe_px` are cliffs on the
false-box side), the stripe's upper height limit, wider than one barrel, every test of stage 3 (the box holds
the body color, "top against a barrel", duplicates, a thin slice seen from top to bottom) and both verify
checks. C does not use the seams.

### What is judged

Five arms against today's detector on the same mask: `A`, `B`, `C`, `AB`, `ABC`. No number of any candidate is
fitted or swept. If a number turns out wrong, that is a second round with a dated addendum, committed first.

## The yardsticks (all required)

Scoring is the standard judge (`judge.run_many`, `judge.compare`: found = the strict rule; a box on its barrel
with the bottom off counts once; boxes not on their barrel = on nothing, a second box, the wrong color).
Per-frame counts are given beside the placement counts.

- **(a) Erosion, real train frames, fixed colors.** Both arms get the same mask: the fixed model's mask with one
  pixel shaved off every painted region (`degrade.damage(mask, [], Damage(erode_px=1))`); also two pixels. On the
  ordinary conditions (154 frames), split into the two white tables (HOME, CAMPUS) and the other places.
  The headline: of the barrels found on the unharmed mask and lost to the erosion by today's detector, how many
  the arm finds on the eroded mask. The cost: barrels the arm loses on the eroded mask, boxes not on their
  barrel, boxes on empty frames.
- **(b) Realistic damage.** The two `REALISTIC` levels of `degrade.py` (seeds 0, 1, 2), on the white-table frames
  (HOME, CAMPUS, ABP white), applied to the fixed model's mask around the hand boxes. Same counts.
- **(c) Unharmed masks.** `python barrels/tools/judge.py --cand-det slack=<arm>` must not FAIL, and the boxes not
  on their barrel must not rise.
- **(d) False boxes.** Every empty train frame (all conditions, the extreme and excluded ones too), on the
  unharmed mask, one and two pixels eroded, one pixel dilated: boxes with the arm against boxes today. And the
  proof harness of `2026-11-26_collapse` (5435 masks) with the flag on: the inputs whose boxes change, per group,
  boxes added and removed. For the groups made from train frames (`real`, `real_erode`, `real_dilate`, `hand`)
  every changed box is scored against the hand boxes. For the simulated scenes the truth is rebuilt from the
  tagged code if that works; if not, the changed scenes are counted and a contact sheet of them is looked at.
- **(e) Hand-set colors.** (a) and (c) again with the mask of the hand thresholds (`data/labels/*_hs.json`, the
  median per condition, as `experiments/2026-11-26_judge` builds it; a condition without labels keeps the fixed
  model).
- **Contact sheets** of every box that appears or disappears on a real frame (unharmed and eroded), looked at
  one by one. Each new box is called right or wrong in the report.
- **The cliffs** (report only): which thresholds an arm moves. `min_width_px`, `min_stripe_px` and `height_max`
  are not touched by any arm; I report what happens to the boxes not on their barrel when each is moved by 20 %
  with and without the recommended arm (or that the code refuses the value).

## What counts as success

**Hard limits. An arm that breaks one is not recommended:**

1. (c) is FAIL, or the boxes not on their barrel rise on the unharmed masks (fixed or hand colors).
2. A new box on any empty train frame, on any of the four masks of (d).
3. In (a), (b), (e): more boxes not on their barrel than today's detector draws on the same masks.
4. Any box that appears on a real frame and, looked at, is on something that is not a barrel, or is a second box
   on a barrel that has one. This holds whatever the counts say.
5. The default is not the same: the harness must print IDENTICAL BOXES ON EVERY INPUT with the flag off.

**Success:** of the found barrels that one pixel of erosion loses on the ordinary frames with fixed colors
(about 40 by the audit), at least **one in three** comes back, and no hard limit is broken. One in two is a
strong result. One in three because about a third of the losses go through caps, the bottom edge and side
occlusion, which no arm touches, and a stripe 2 to 3 rows tall at the far end is simply gone after one pixel.

**Which arm is recommended** (fixed now): among the arms that break no hard limit, the one that brings back the
most barrels in (a) at one pixel on the ordinary frames. Arms within 2 barrels of each other: the one with fewer
letters. If no arm passes the hard limits: say so, and say which limit and which box.

**Predictions, written now.** A alone: little (it changes nothing nearer than 50 cm). B: most of the
"height" losses come back, 8 of the 11 on the white tables (that is the design set, so it proves nothing), and
it should hold at two pixels where today's detector falls further. C alone: few, because the pixel fails several
tests at once (the height, the body walk, the edge tolerance), and C forgives exactly one. Risk for B: on the
unharmed masks it also admits real barrels whose stripe is weakly painted (a thin line in a stripe-sized gap),
and a box on such a barrel may be drawn with the bottom off; and things that are not barrels but have a thin
line of one color between two blocks of the other, one barrel tall.

## Not done here, on purpose

The bottom edge (another experiment owns it), caps, the partly seen branch, the color step. No image pixel is
changed. No learned model.

## Outputs

`results/2026-11-26_slack/`: `summary.md` (one table, every arm on every yardstick), `changes.csv` (every barrel
and box that changed, per yardstick), the judge pages of (c), the contact sheets, `harness.md`. `ENTRY.md` in
this folder is the experiment-log entry.
