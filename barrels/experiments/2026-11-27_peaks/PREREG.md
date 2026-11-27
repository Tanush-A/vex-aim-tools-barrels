# PREREG — the barrels' colors as peaks of the frame's own histogram (2026-11-27, branch `wip/exp-peaks`)

Written and committed before any judged run. Nothing here changes what runs by default; `detector.py` is not touched.

## Question

Tanush (2026-11-27): "read the peaks from histograms; barrels show up as peaks; maybe that's useful". The naive version
is known to fail: the whole-frame orange peak sat 5 or more hue units from the barrels on 37 of 99 frames
(`docs/review-2026-11-26/adaptive_forensic.md` 2c), because barrels are about 4 % of the pixels.

1. (A, descriptive) Do the barrels make a separate local peak in the frame's hue x S histogram, and how often is it
   the largest one in its hue region?
2. (B, descriptive) Which peak finder picks the barrels' peak and not the floor or the wall?
3. (C, judged) Does setting this frame's color ranges from the best finder's peak find more barrels, by the standard
   pass rule, leave one place out?

## What was looked at first (honest list)

- Parts A and B were run, in-sample, on all train frames (ordinary 154, extreme 77): `measure.py`,
  `results/2026-11-27_peaks/measure.md` / `.csv`. No detector was run, nothing was scored with boxes.
  - In the plain histogram the barrels' own peak exists as a separate local peak in 96 of 97 ordinary orange frames
    and 87 of 92 blue frames, but it is the largest in its hue region in only 28 of 97 (orange) and 53 of 92 (blue).
  - Finders with structure find it: F6_pair_small within 3 hue units on 89 of 97 orange and 88 of 92 blue frames
    (fooled, 5 or more units away: 4 and 3); F5_pair 82/11 and 88/4; F1_sat 75/21 and 83/9; F0_naive 38/56 and 68/22.
  - The fooled frames of F6 (orange) are close-ups and lid views (no stripe pattern in view; few or no pixels kept),
    a campus top view (a low-S peak at hue 17), and one glass close-up. The fooled blue frames are two warm-lamp
    bathroom frames where the blue barrel is not blue any more (true S about 40, hue 54-80) and one held frame.
- **F6_pair_small was chosen as the primary finder after seeing these tables.** So its choice is in-sample; only the
  setting below is chosen held out.
- The finders' own constants (hue regions, broad S floors 60 / 40, 2 stripe heights, the barrel-size limits 1.6 W
  and 1.3 H, the 8-unit window, (S/255)^3) were set when the code was written, before measure.py was run, and not
  changed after.
- The grid below and the rule for turning a peak into a range were written before any detector run on a peak range.
  One smoke test ran the code on one frame (`4A8B_window_light_close_01`) to time it; its boxes were not scored.
- The other experiments of 2026-11-26 (contrast, near-miss, selfcal) and their pictures were read before; the S floor
  "never under 60" is borrowed from selfcal.

## Candidates (all judged; all reported, losers included)

Each finder gives, per frame and color, the largest local peak among the pixels it keeps (`peaks.py`):

| candidate | finder | what it is |
|---|---|---|
| **P1 (primary)** | F6_pair_small | pixels in a stripe pattern with the other color AND in a barrel-sized connected region |
| P2 | F5_pair | stripe pattern only |
| P3 | F1_sat | every gated pixel weighted by (S/255)^3; no structure |
| P0 | F0_naive | every gated pixel: the known failure, for comparison |
| P5 | F6_pair_small | P1's frame ranges as the first pass of selfcal AB (copied from `wip/exp-selfcal` 690ae91, its defaults rel_margin 1.0, hue_move_max 6, flood_max 0.03, which its own folds chose), then selfcal |
| S0 (report) | none | selfcal AB with its defaults on the fixed ranges: the comparison for P5. Its numbers were chosen by its own folds on 2026-11-26, so this row is not a clean held-out number |

**From peak to ranges** (`candidates.py: frame_thresholds`), per color, from the fixed range [lo, hi] (orange 3-13
S >= 140; blue 103-119 S >= 113):

- Use the peak only if it exists, the finder kept at least `n_min` pixels of that color, and its hue lies within
  `cap` of the fixed range (lo - cap <= hue <= hi + cap). Else the fixed range.
- `shift`: the range moved so its middle sits on the peak, half-width the fixed one plus `pad`. `union`: the hull of
  the fixed range and that moved range.
- Blue only, `s_follow`: when the blue peak is used, the floor becomes 0.6 x the peak's S, never under 60, never above
  113. Orange's floor never moves.
- Per frame only; no pixel changed; nothing carried across frames.

**The grid** (32 settings; the careful one first): cap {4, 8} x n_min {200, 50} x pad {0, 2} x s_follow {off, on} x
mode {union, shift}.

**How the setting is chosen** (inside each fold, on the other seven places only; `candidates.py: choose`): every
setting and the fixed ranges are counted as the judge counts. A setting is out if, against the fixed ranges on those
frames, boxes not on their barrel rise by more than 1.85, any box is added on a clean empty frame, boxes on cluttered
empty frames rise by more than 1.0, or found at any training place drops by more than that place's margin. Of the
rest, most placements found wins; a tie keeps the earlier one; if none beats the fixed ranges, the fold uses them.
P5 takes P1's choice in each fold.

## The judge

`barrels.judge.judge(fit=...)`, leave one place out, baseline = today's default (fixed ranges, `DetConfig()`),
154 ordinary train frames, 172 placements. Extreme conditions printed, never judged. Train frames only.

## Success line

- P1 **PASS** by the standard pass rule = the peak idea works. A PASS under +6 placements is WEAK.
- P1 NO CLEAR DIFFERENCE or FAIL = it does not, as built.
- Part D (the comparison with selfcal +13.8, contrast +21.5, near-miss +13.7) is read off the same judge; those
  numbers come from their own branches and are not re-run here, except S0.
- A second round needs a dated addendum committed first.
