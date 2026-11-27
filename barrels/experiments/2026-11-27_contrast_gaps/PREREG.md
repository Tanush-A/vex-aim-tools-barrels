# PREREG — the frames where the vendor still beats the stripe by contrast (2026-11-27)

Branch `wip/exp-contrast-gaps` (from `barrels` at 125aed7, where the stripe by contrast is the default, with
`wip/exp-contrast` merged in: its module kept as `contrast_c4.py`, the default `contrast.py` untouched). Code:
`gaps.py` (the additions), `run.py` (the judged round), `explore.py`, `other.py` (exploration and the count of group 5).

## Question

On the train frames with a vendor file, the vendor puts a box on 211 of 258 barrels and today's default (fixed colors,
detector, stripe by contrast) on 221, but the vendor finds more on 16 frames. Which of those losses can a small,
per-frame addition after today's default recover, without a box on an empty frame, without more boxes that are not on
their barrel, and without a box on the near-barrel traps?

## What I looked at first (honest list)

1. The page `results/2026-11-27_vs_vendor/index.html` (main checkout) and the 16 frames where the vendor finds more.
2. A diagnosis of every barrel today's default misses on the ordinary and extreme train frames (25 ordinary, 68
   extreme): the contrast candidates near it, their reasons, the detector's boxes (scratch script, not committed).
   Findings: (a) the three ottoman close-ups: the lower body band is below the frame, so no row is searched; (b) a
   barrel cut by the side of the frame: share 0.6 to 0.8 and strength 0.86 to 1.08 because the window counts the part
   outside the frame as "does not agree" (bathroom edge, wood core, black table); (c) touching blue barrels on the
   ottoman (cool and mid lamp): the contrast candidate on the left barrel IS painted, but the detector's run on the
   painted mask gives a box that is "on" the fixed colors' box of the middle barrel, which is 78 to 81 px wide (1.2 to
   1.3 barrels), so it is not added. The "one body" guard of the experiment is not in the adopted stage and is not
   the cause. (d) touching blue barrels under the warm lamp: both candidates have strength 0.92 and 0.97, under 1.15.
3. Probes of the four additions on the target frames, then `explore.py` once at the loosest setting of each (edge
   0.4, half 1.0, split 1.1, beside 0.8) on all ordinary and extreme train frames, in-sample: 15 boxes added or
   changed, 14 on a labelled barrel, 1 not (a `beside` box on `campus_light_clutter_02`), none on an empty frame,
   2 boxes replaced (the two wide boxes). `results/2026-11-27_contrast_gaps/explore.json`.
4. Group 5 (the coordinator's addition): `other.py` counted, in-sample, on every train frame and Dave's 12 office
   frames, what three versions of the rule would drop. A drop-only rule against boxes the detector drew on the fixed
   colors finds nothing: in both named cases BOTH boxes were added by contrast. Resolving by "a painted candidate of
   its color inside it" and by "the sandwich at the box's stripe row" each dropped the real orange barrel on Dave's
   snap 07 (the wrong blue box reads its orange top as a stripe between a purple sign and the real blue stripe, and
   its sandwich is as strong); the mask share alone fails one way on Dave's frame (contrast painted the orange body
   blue) and the other way on the warm bathroom (the fixed colors miss the blue). The rule kept (below) was shaped on
   these 7 pairs, 6 of them on extreme frames or Dave's: its two numbers (1.25 and 0.25) are in-sample and are NOT
   chosen in the fold. Only one pair is on an ordinary frame (`lampwarm6_bathtile_core_01`), so the judge can say
   little about it.

## The candidates (each on top of today's default; off = exactly today's boxes, `check.py`)

| name | what | settings chosen in the fold (most cautious first) |
|---|---|---|
| **E** edge | a candidate whose counting window the side of the frame cuts is counted on the part inside the frame, when at least `edge` of the window is inside | edge 0.6 / 0.5 / 0.4 |
| **H** half | rows whose lower body band the BOTTOM of the frame cuts: the stripe band against the body band above it alone, strength floor `half` | half 1.5 / 1.3 / 1.15 / 1.0 |
| **S** split | a fixed-colors box wider than `split` x the width its top row predicts, with two or more boxes of its color on it in the run on the painted mask, is replaced by them | split 1.25 / 1.2 / 1.15 / 1.1 |
| **B** beside | a candidate under today's strength floor but at least `beside`, on the stripe row of a found barrel and right beside it (chained) | beside 1.0 / 0.9 / 0.8 |
| **O** other | two boxes of different colors, overlap over `other` of the smaller, heights within 1.25x, one of them added by contrast: the added one is dropped when the sandwich at its stripe row is weaker by 0.25 or more (on a near tie: when the fixed colors support it less) | other 0.5 / 0.4 |
| **ALL** (primary) | E + H + S + B + O, each number the pick of its own family on the same training places | per family |

The extra candidates of E, H and B are skipped when their stripe point lies in a box of today's answer or in the
predicted box of one of today's candidates; they are measured and painted exactly as today's candidates (the two
checks, the barrel's own colors, only where nothing is painted yet), and the detector's box on that mask is added
when it is on no box of today's answer.

## How every number is chosen

Leave one place out, by the judge (`judge.judge(fit=...)`). Inside each fold, on the ordinary train frames of the
other 7 places, the rule of the 2026-11-26 contrast experiment, word for word (`run.choose`, copied from
`2026-11-26_contrast/table.choose`): a setting is allowed when the standard pass rule does not call it FAIL against
today's default on those places; the allowed setting with the highest gain wins (gain = found per placement minus
boxes not on their barrel per arrangement, as differences from today); a tie goes to the most cautious; no allowed
setting with a gain above zero: the addition stays off. ALL uses each family's own pick. SAME_SIZE 1.25 and TIE 0.25
of O are fixed (item 4 above).

## Success line, said before the run

- The judge's verdict, as it comes (PASS / NO CLEAR DIFFERENCE / FAIL). A PASS needs more than +4.0 placements. The
  ceiling of the named groups on ordinary frames is about +4.1 (close-ups 1.0, bathroom edge 0.75, touching ottoman
  1.33, pale-wood edge 1.0 if anything reaches it), so I expect NO CLEAR DIFFERENCE at best and say so now.
- Hard limits, each a failure of the candidate whatever the verdict: a box on a clean empty frame; boxes not on their
  barrel up beyond the margin (+1.85); any box on the near-barrel traps `*_neg_02` and `lampwarm6_glass_occl_02`
  that today's default does not draw (checked by name, every train frame with those names).
- "Worth proposing" = no hard limit broken, no FAIL, and it gains the named barrels of the vendor list.
- Group 3 (the very dark ottoman, lamp mid 3) is extreme: report only, never judged.

## Afterwards

`tools/vs_vendor.py --all --contrast-from <worktree>/barrels --cand-callable <run.py:best>` with the best candidate;
the new totals reported against 221 / 211 of 258.

## Addendum 2026-11-27 (written after the first three leave-one-place-out runs, E, H and S, all NO CLEAR DIFFERENCE with no change at all; before any second-round run)

What the first runs show is structural, not a result about the additions: every addition fixes barrels at ONE ordinary
place (E: the bathroom edge; H, S, B: the ottoman; O: one box on the bathroom floor), so when that place is held out
its fold sees no gain and leaves the addition off, and at every other place the addition changes nothing. Leave one
place out cannot show a fix that exists at one place. The registered verdicts stand as they come.

Second round, said now, before it runs: the same families judged as FIXED callables at the setting the fold rule picks
on all eight places (`run.all_places_pick`; per family and for ALL, `run.py --insample`). These numbers are
IN-SAMPLE: the place judged took part in choosing them. They are reported as "what the addition does at the setting
the rule would adopt", never as the held-out result, and the hard limits (empty frames, boxes not on their barrel,
traps) are checked on them as on the first round.
