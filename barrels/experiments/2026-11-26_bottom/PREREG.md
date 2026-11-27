# Pre-registration: the bottom edge ("more paint, box disappears"; map B8, TODO D1 and K2)

Written 2026-11-26 on branch `wip/exp-bottom` (from `barrels` at `337f04c`). Written **after** the yardstick
(step A: today's detector only) and **before any candidate rule was run on any frame**. Train frames only: every
frame is read through `judge.load_frame`, which refuses a test frame. No test frame was opened, scored or listed.

## The question

When the color step paints more of the picture, shadow and reflection under a barrel get the barrel's color. The
detector keeps a seen bottom that is within 15 % of the height (at least 4 px) of the predicted one. The scorer
allows 10 % (at least 3 px) from the true one. So a box that is on its barrel is counted as a miss plus a false
box, and the distance read off its bottom is wrong.

**Is there a rule for the bottom edge alone that brings these boxes back, without losing barrels under today's
colors and without making the bottom edge worse where it is right today?**

## What was seen before this was written (honesty)

1. The docs and the code named in the task: `DETECTOR-MAP.md`, `HOW-IT-WORKS-SHORT.md`, the sections of `EVAL.md`,
   `TODO.md`, the audit's 4a to 4c, the report's 3.3; `detector.py`, `geometry.py`, `eval_det.py`, `judge.py`,
   `counting.py` in full.
2. From the task text: `bottom_tol` 0.10 everywhere gains 3 and loses 5 barrels; 0.12 gains 1 and loses 1. The
   audit's and the main session's counts (8 of 10; 65 of 138).
3. **The yardstick** (`yardstick.py`, `results/2026-11-26_bottom/yardstick.md`; today's detector under six color
   steps on the 154 ordinary train frames, 307 barrels, 172 placements). Every number of it. The ones that matter:

   | color step | found, placements | found, per frame | box off | the bottom edge is the cause: low / high |
   |---|---|---|---|---|
   | `fixed` | 133.8 | 211 | 2 | 1 / 1 |
   | `s20` (saturation floors -20) | 133.6 | 209 | 8 | 4 / 3 |
   | `s40` (saturation floors -40) | 125.4 | 204 | 14 | 8 / 5 |
   | `hue3` (hue ranges +-3) | 142.1 | 230 | 4 | 2 / 2 |
   | `dil1` (mask dilated 1 px) | 136.6 | 217 | 8 | 2 / 5 |
   | `hand` (hand thresholds) | 156.8 | 281 | 4 | 1 / 3 |

   So on the ordinary train frames the flaw is real and **small**: 2 to 13 boxes per color step, 37 in all, and
   only half of them (18) end too LOW. The other 19 end too HIGH.
4. **The contact sheets** of those 37 boxes (`results/2026-11-26_bottom/sheets/yardstick_*.png`), all six looked at.
   What they show:
   - *Too low, 18:* a painted reflection on the glass table or a painted shadow on a white or gray table. The seen
     bottom is 10 to 14 % of the height below the bottom the stripe's row predicts. In every one the predicted
     bottom is within the scorer's tolerance of the true one. In some the extra paint is a narrow tail, in others it
     is as wide as the barrel.
   - *Too high, a seen bottom, 10:* the lower body is only partly painted (gloss on the gray table, a dark lower face
     on the ottoman, a barrel at the frame edge). In 8 of them the seen bottom is 10 to 15 % above the predicted one,
     so it is kept today. The predicted bottom would pass the scorer in 9 of the 10.
   - *Too high, the predicted bottom drawn, 9:* (a) the barrel cut by the left frame edge on the glass table, very
     near (true box 92 px tall): its reflection carries the seen bottom past 15 %, the predicted bottom is drawn,
     and the prediction is 10 px too high for this near barrel (6 of the 9, one placement under several lights);
     (b) two half stripes on the bathroom floor whose bottom comes from the seam, 8 and 19 px high; (c) one other.
     **No rule below can fix these**: the paint is refused today already, and the prediction is what is wrong.
5. **Five readings of the bottom, against the labels** (yardstick, section 7; stripe boxes with a seen top):

   | reading | outside the scorer's tolerance, near barrels (lowest and highest of the six color steps) | far barrels |
   |---|---|---|
   | the seen bottom (raw, before the 15 % test) | 7.8 % ... 21.7 % | 0 % ... 29 % |
   | the bottom the stripe's row predicts | 1.8 % ... 3.9 % | 0 % at every step |
   | the seen top + the predicted height | 6 % ... 12 % | 17 % ... 56 % |
   | the seen top and the stripe's row, by the barrel's proportions | 14 % ... 16 % | 7 % ... 24 % |
   | the seen top + the height of a barrel as wide as the box | 17 % ... 20 % | 25 % ... 43 % |

   The stripe's row is by far the steadiest reading, and paint does not move it. Its weak point: for near barrels it
   is a median 2 px too high (3.8 % of the height), for far ones 1 px too low. The seen bottom is better at the
   median (1 px, no bias) and has the long tail. Every reading that leans on the seen top or on the box's width is
   worse than both. This is why no candidate below uses the top or the width.
6. The new code (`drawn_bottom`, `rows_with_body` in `detector.py`) was written before this file. It had been run on
   nothing but the proof harness at the defaults and unit tests. **No candidate setting was run on a frame, a mask
   of a frame, or the judge.**

Not seen: any count, verdict or picture for any candidate.

## The candidates

All of them change the bottom edge only. All use two rows the detector already has: `seen` (one past the last row of
the body's color under the barrel) and `predicted` (the bottom the rule's own reading predicts).

| # | name | setting (`--cand-det`) | the rule |
|---|---|---|---|
| 1 | `low` | `bottom_rule=low` | A seen bottom that agrees (15 %) but lies **below** the predicted one by more than the scorer's tolerance (10 % of the height, at least 3 px): the predicted row is drawn. Above stays as today. *Shadow and reflection only ever extend a barrel downward.* |
| 2 | `both` | `bottom_rule=both` | The same, in both directions: a seen bottom further than the scorer's tolerance from the predicted one, above or below: the predicted row is drawn. *The detector and the scorer agree (B8 as written).* |
| 3 | `predicted` | `bottom_rule=predicted` | The predicted row is always drawn. *The paint says that the bottom is there, not where.* |
| 4 | `rows` | `bottom_rows=0.5` | What counts as "seen" changes: a row under the body is the barrel's only when the body's color fills at least half of the columns walked (today: one pixel in any column). *Paint under a barrel that is narrower than the barrel is not its bottom.* |
| 5 | `rows+low` | `bottom_rows=0.5,bottom_rule=low` | 4 and 1 together. |

**Where each applies** (every place the map says a bottom is decided):

| site | function | `predicted` comes from | rules 1 to 3 | rule 4 |
|---|---|---|---|---|
| stage 1, a piece | `resolve_bottom` | the top row | the drawn row | the piece's last row filled to half its width |
| stage 3, a stripe's box | `read_edges` | the stripe's row | the drawn row | the walk down (`_body_extent`) |
| stage 6, a cap, checks 6 and 7 | `_cap_box` | the width, or the top row | the drawn row | the cap's columns |
| stage 7, a pair's slices | `_full_slice` | the stripe piece's row | the drawn row | the walk down |
| stage 8, a half stripe hidden from above | `half_stripes` | the seam | the drawn row | the walk down |

**What rules 1 to 3 do not touch.** They decide the *drawn* row only. Whether an edge was *seen* is answered as
today (15 %, at least 4 px) wherever a rule asks it: the flag `bottom_inferred`, a thin slice seen from top to
bottom, a full slice, the far edge of a half stripe, the second reading of `drop_single_reading`. A shadow 12 % low
still says "the body is seen down to about the predicted bottom". Only its row is not believed. (If a rule were to
also change those answers, boxes would be refused that are drawn today; that would be a second change.)

**Not candidates, and why.**
- *The bottom from the box's width, or from the seen top:* item 5 above. They are outside the scorer's tolerance 3
  to 20 times as often as the stripe's row.
- *"Mirrored paint is not the barrel":* on the sheets a reflection on glass is a smear of the body's color, not a
  mirrored stripe; there is nothing mirrored to test for. Rule 4 is the nearest testable form.
- *One global `bottom_tol`:* already probed by the main session (no clear difference), and it moves tops and a
  sideways test as well.

## How every number is chosen

- **10 % of the height, at least 3 px** (rules 1, 2, 5): the scorer's own tolerance (`eval_det.BOTTOM_TOL_FRAC`,
  `BOTTOM_TOL_MIN_PX`). Not fitted, not swept. A unit test keeps the detector's copy equal to the scorer's.
- **0.5** (rules 4, 5): "half of the columns", the share the detector already uses for "an edge lies against
  something" (`ends_against`). What it costs on a clean barrel, from the geometry: the base is 0.71 of the barrel's
  width and its near rim is an arc 4 px deep at 20 cm and 1 px at 40 cm; half of a whole stripe's columns are
  covered down to about 1 px above the arc's lowest point at 20 cm. Not fitted, not swept.
- No number is chosen from the frames. No value other than these is run in this round.

## How it is judged

`run.py` runs today's detector and the five candidates on the same masks: the six color steps of every ordinary
train frame (the extreme conditions are run and reported, never judged). Every comparison is made by
`judge.compare`, the standard pass rule with the stored margins (`results/baseline/margins.json`).

1. **With the fixed colors, against today's default.** This is `python barrels/tools/judge.py --cand-det <setting>`;
   the recommended rule is also run through that command, and the two must agree.
2. **With each of the five "more paint" color steps: the rule against today's detector on the same masks.**

Reported for every candidate at every color step: the verdict and its clauses; found per placement and per frame;
box off; boxes not on their barrel; **the yardstick** (boxes on their barrel that fail the strict rule with the
bottom edge as the cause, per frame, low and high; `lib.why_off`); every barrel gained and lost; the bottom-edge
error against the labels (median and 90th percentile of the absolute error, in px and in % of the true height, near
and far apart; near = a true box at least 40 px tall; only true bottoms inside the frame and not flagged
`bottom_estimated`), on the barrels that have a box on them in both arms, and on each arm's own.
Contact sheets of every barrel whose state changes; they are looked at.

## What counts as success

A candidate **works** when all five hold:

- (a) judgement 1 (fixed colors) is not FAIL;
- (b) none of the five judgements 2 is FAIL;
- (c) the yardstick, summed over the five "more paint" steps, is lower than today's (today: 7 + 13 + 4 + 7 + 4 = 35);
- (d) found per placement, summed over the five "more paint" steps, is higher than today's (today: 133.6 + 125.4 +
  142.1 + 136.6 + 156.8 = 694.5);
- (e) the bottom edge is not made worse where it is right today: with the fixed colors, on the barrels that have a
  box in both arms, the median absolute bottom error is not higher than today's by more than 0.5 px, for near and
  for far barrels (today 1.0 px and 1.0 px).

**The recommendation:** among the candidates that work, the one with the lowest yardstick sum of (c); a tie goes to
the higher sum of (d); a tie there to the earlier candidate in the list. If none works, none is recommended.

Reported and not required ("ideally"): found with the fixed colors does not drop (today 133.8 placements, 211
barrels).

**What this experiment cannot show.** The pass rule calls a gain only above +4.0 placements. The whole yardstick
is 2 to 13 boxes per color step, and a placement under five lights is five boxes. So the expected verdict of every
judgement is NO CLEAR DIFFERENCE, and (a) and (b) are a check against harm, not a proof of a gain. The gain is
measured by (c) and (d) and by the bottom-edge error.

## What I expect (written before running)

- `low`: the 18 low boxes mostly go. One known risk: the barrel at the left edge of the glass table (`edge_01`),
  where the prediction is 10 px too high. A correct seen bottom is then more than 10 % below the predicted one and
  would be replaced by a bad one. That would cost up to one placement at the glass table with the fixed colors.
- `both`: the same, plus up to 8 of the 10 "too high, seen" boxes.
- `predicted`: the steadiest tail and a worse median for near barrels (2 px against 1); I expect it to fail (e).
- `rows`: I do not know. It may keep more true seen bottoms when a narrow tail hangs under them.

## A second round

Needs a dated addendum in this file, committed before it runs.

## Outputs

`results/2026-11-26_bottom/`: `yardstick.md` (step A), `summary.md` (step C), `summary.json`, one folder per
judgement under `judge/`, `sheets/`. `ENTRY.md` in this folder: the entry for `EXPERIMENTS.md`.
