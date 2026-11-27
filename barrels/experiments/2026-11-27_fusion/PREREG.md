# PREREG — Fusion: the passing color methods combined by what each is good at (2026-11-27, branch `wip/exp-fusion`)

Written and committed before any judged run. One round. A second round needs a dated addendum committed first.

## Question

Tanush: "Surely we can combine contrast with peaks or with bluer-than-the-light in a valid, seamless way ... so long as
false barrels don't come up." Yesterday's crude stacks (`wip/exp-combined`) added 0.2 to 2.7 placements to contrast
alone and several failed on boxes not on their barrel. **Does a careful fusion (one method proposes, the others are
asked only about that box, shape checks reject traps) beat contrast alone (C1, 155.3 of 172 held out) by more than the
noise, without more boxes not on their barrel?** And: what do the non-color fixes (the seams rule, the bottom-edge
rule, the two shape checks) add on top of contrast?

## The methods (each brought in unchanged; each at the setting ITS OWN fold rule picked for that held-out place)

| name | what it is | where its per-fold pick comes from |
|---|---|---|
| FX | the fixed colors (today) | none |
| C1 | contrast: stripe by color difference, added to today's boxes (`wip/exp-contrast`) | `results/2026-11-26_contrast/chosen.json`, family C1 |
| P2 | histogram peaks, the stripe-pair finder: this frame's color ranges (`wip/exp-peaks`) | `results/2026-11-27_peaks/chosen.json`, "P2 without <place>" |
| SC | self-calibration AB: a found barrel sets the frame's colors (`wip/exp-selfcal`) | `results/2026-11-26_combined/chosen.json`, "sc" |
| NM | near-miss colors next to strong evidence (`wip/exp-nearmiss`) | the same file, "nm" |
| B4 | bluer than the light (light experiment's B4, as in `wip/exp-bluer-geom`) | `results/2026-11-27_bluer_geom/chosen.json`, G1's color step |

The stored picks were each made by that method's own rule on the other places (or, for a place with extreme frames
only, on all eight). They are read, not re-chosen. The reproduction step checks that C1 gives its judged 155.30.

Non-color fixes, ported to `detector.py` behind off-by-default flags (proof harness: IDENTICAL BOXES ON EVERY INPUT at
defaults, 5435 masks, run before this file was written):
- `DetConfig(seams=True)`: rule D of 2026-11-26_slack, the code of `wip/adopt-slack`.
- `DetConfig(bottom_rule="low_uncut")`: 2026-11-26_bottom.
- The shape checks K1 (paint solidity) and K2 (a "stripe" that is a label) of `wip/exp-bluer-geom` (`checks.py`,
  `stages.measure`), a post-filter on boxes.

Every fusion candidate (F1 onward) runs EVERY method's detector with `DetConfig(seams=True, bottom_rule="low_uncut")`.

## The candidates

- **F0 contrast alone** (the baseline of this experiment): C1 exactly as judged on `wip/exp-contrast` (default
  detector, no checks). Reproduced first.
- **F1 the non-color stack**: C1 + seams + bottom rule + shape checks. The checks are chosen in the fold among three:
  off; mild (K1 solid < 0.35; K2 stripe > 1.5 x the row's and body fill < 0.6); strong (K1 < 0.40; K2 > 1.25 x and
  < 0.6). Report-only ablations at F1's picks: F1a = C1 + checks, default detector; F1b = C1 + seams + bottom, no checks.
- **F2 propose, then ask the others (votes among the other methods).** F1's boxes stand. Every box drawn by P2, SC, NM
  or B4 that is on no F1 box (on = half of the smaller box inside the other, any color) is a proposal. Proposals of
  the same color on each other (on) are one cluster. A cluster's votes = how many of the four methods drew it. It is
  added when votes >= k AND its box passes F1's fold-chosen shape checks. The box drawn is that of the first method in
  the order SC, P2, NM, B4 (by their own boxes not on their barrel when judged alone, lowest first: 2.18, 3.45, 3.57,
  6.68). Clusters are added most votes first; a cluster on an already added box is not added. k is chosen in the fold
  among: off (= F1), 4, 3, 2 (most cautious first).
- **F3 as F2, with the contrast response as one more voter.** A cluster gets one more vote when a contrast candidate
  of its color (`contrast.find`, margin 0.5, share 0.5, strength >= 1.0, and the absolute check, orange part >= 0.8;
  numbers from contrast's own grid, nothing new) has its stripe point inside the cluster's box. k among off, 5, 4, 3, 2.
- **F4 division of labor: contrast says where, the others say the colors.** For each C1 contrast candidate (C1's fold
  setting and its guards) whose stripe point lies in no F1 box: inside its predicted box (grown 8 %, contrast's own
  `box_slack`), the pixels that P2's, SC's or NM's mask paints and the fixed mask leaves empty are painted onto the
  fixed mask (in that order of trust: SC, P2, NM); the detector runs once more on that mask; a new box on no F1 box is
  added when it passes F1's checks. No new number.
- **F5 = F4, then F3's votes** over the proposals that are on no F4 box. k chosen in the fold as in F3.
- **F6 = F5 + tidy**: two rules with no new number, against the kinds of false box contrast was seen to draw
  (`EXPERIMENTS.md`, the winners together, D): (a) one box per barrel: a box that is not from the fixed detector and
  lies at least 0.8 inside a larger box of the same color is removed; (b) a box that is not from the fixed detector,
  on (half inside) a box of the other color that is from the fixed detector, is removed. k chosen in the fold as in F3.

## How every number is chosen (inside each fold, never on the place judged)

For held-out place P: every method runs at ITS fold-P pick on the frames of the other seven places, and the fusion's
own choice (F1: the checks; F2, F3, F5, F6: k, with F1's checks of that fold fixed) is picked there by the rule of the
contrast and light experiments: a choice is allowed when the standard pass rule (`judge.decide`, stored margins) calls
it neither FAIL against today's detector NOR FAIL against F0 on those places; the highest gain (found per placement
minus boxes not on their barrel per arrangement, as differences from today) wins; a tie goes to the most cautious (the
order written above). F2-F6 with no allowed k above the gain of k = off: k = off. A place with extreme frames only is
scored with the picks on all eight places (the judge's rule).

Free numbers of this experiment: the checks choice (3 options) and k (4 or 5 options). Nothing else.

## Judging and success line

- Every candidate is judged leave one place out, by `jg.judge(fit=...)` against today's detector AND against F0
  (`jg.judge(candidate, baseline=F0)`, both as held-out detectors). Every one is reported, losers included.
- **Success line**: a fusion PASSES against F0 (found up by more than +4.0 placements, boxes not on their barrel not up
  by more than +1.85, no box on a clean empty frame, no place down by more than its margin). A PASS under +6 is WEAK.
  Anything less: contrast alone stays the answer for color, and the non-color fixes are reported by what they do.
- Expected, written now: what is left after contrast is mostly hidden and frame-cut barrels (15.0 of 16.7), so a
  color fusion can reach at most about 2-3 placements more. A PASS against F0 on found is unlikely; the more likely
  gain is fewer boxes not on their barrel.
- For the best fusion: every box not on its barrel, by frame and object, with whether F0 draws it; contact sheets of
  gained, lost and new false boxes; the extreme conditions (wood desk, black table, very dark ottoman) and the vendor
  comparison on the six measured places for the best fusion, F0 and the vendor.

## Said plainly

All methods, their guards and the shape checks were shaped on these eight places (by their authors, with in-sample
tables). Only the settings inside the folds are held out. The fusion rules (F2-F6) were designed after reading every
2026-11-26/27 entry, including the lists of each method's false boxes (the jar, the tin, the figure, a second box on
an orange barrel, an orange box on a blue barrel). The tidy rules of F6 were written against those boxes. A new place,
or the test frames, is the clean check.

## What I looked at before writing this

`docs/REPORT-2026-11-27.md`; every `EXPERIMENTS.md` entry of 2026-11-26/27 (results tables, the "who finds what"
overlap, the lists of false boxes, what is left after contrast); the code of contrast, peaks, bluer-geom checks and
combined; the stored fold picks of each method (settings only, no per-frame result). No frame, no contact sheet and no
per-frame count was looked at for this plan. The golden harness was run with the two new flags at their defaults only.

## Addendum 1 (2026-11-27, written after round 1, before round 2 ran)

Round 1 (committed in f92a43f, `results/2026-11-27_fusion/`): every fusion is NO CLEAR DIFFERENCE against F0; the best
on found is F3 (157.08 against 155.30; boxes not on their barrel 2.17 against 2.83). F1a (contrast + checks) PASSES
against F0 on boxes (2.83 -> 0.83, found equal). Looking at F3's boxes not on their barrel: the pale-wood close-up box
(a box of today's detector, on wood grain) is removed by F1's checks and then comes back, because the other methods
draw the same fixed-color box and their votes carry it; measured in their masks, it passes the checks.

Round 2, one rule and two report-only ablations, nothing else changed:

- **F3r, F5r, F6r** = F3, F5, F6 with one rule: a proposal on (half inside) a box that F1's checks removed is not a
  proposal. A box the checks call a trap stays a trap, whichever method draws it again. k chosen in the fold exactly
  as before (the same options, the same rule). This rule was written after seeing round 1's false boxes. Said plainly.
- Report only, to tell the two detector flags apart: **F1s** = C1 + checks + seams only; **F1u** = C1 + checks +
  bottom rule only (both at F1's checks pick).

Each judged against today and against F0, as in round 1. Round 1's numbers stand as they are.
