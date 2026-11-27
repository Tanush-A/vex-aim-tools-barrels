# Pre-registration: the standard pass rule and its sanity checks (2026-11-26, TODO M3)

Written 2026-11-26 on branch `wip/measure`, after the noise floor was measured (its numbers are the input of this
rule) and **before any candidate was run through the judge**. Train frames only; no test frame is opened, scored or
listed.

## What was seen before this was written (honesty)

- Every number of `results/2026-11-26_noise_floor/summary.md`, including the check on 12 unseen joint moves (set C): 2
  of 12 were called (one PASS, one FAIL).
- From the review's forensic report, counted per frame under the strict rule: the hand thresholds find 281 against 211
  of 307 with 7 false boxes each and two boxes on empty bathroom frames; "blue follows the light", leave one place out
  in round 1 of `2026-11-25_color`, found 22 more with 6 more false boxes and one box on an empty glass frame.
- Not seen: any of these candidates counted per placement, or any verdict of this rule on them.

## The rule (fixed here; code: `src/barrels/judge.py`, `decide`)

**Where.** The ordinary train conditions of `data/conditions.json`: 154 frames, 17 conditions at 8 places, 172
placements (307 barrels when every light is counted). Extreme conditions are run and printed, never judged.

**What is counted** (`src/barrels/counting.py`). Found = the strict v2 rule, every placement once (the share of its
lights in which it is found). Boxes that are not on their barrel = on nothing, a second box on a barrel, or the wrong
color; each once per arrangement. Boxes on empty frames: on clean ones, and on ones that hold clutter.

**The clauses.** Candidate minus baseline. Each margin is the largest change, in that direction, that a change which
means nothing produced (26 neighbours of the fixed color model: 14 with one number moved one step, 12 with several
moved at once), and never less than one whole unit.

1. *Found, all ordinary places together.* Up by more than **4.00** placements: better. Down by more than **10.92**:
   worse.
2. *Found, place by place.* Down at any one place by more than that place's margin: worse. Home white table 1.00,
   campus study room 1.00, ABP gray 6.00, bathroom floor 1.25, glass table 1.00, ottoman 2.34, pale wood 1.00, ABP
   white 1.00 (a place that was never measured: 1.00).
3. *Boxes that are not on their barrel.* Up by more than **1.85**: worse. Down by more than 1.00: better.
4. *Boxes on empty frames.* Any more boxes on clean empty frames than the baseline has: worse. On empty frames with
   clutter, up by more than **1.00**: worse.

**The verdict.**

- **FAIL** when any clause says worse.
- **PASS** when no clause says worse and clause 1 says better; or no clause says worse, clause 3 says better and
  found is not lower.
- **NO CLEAR DIFFERENCE** otherwise.

**A candidate with fitted numbers** is judged leave one place out: the caller's `fit(train_stems, held_place)` is
called with the ordinary train frames of the other places, and what it returns is run on the held-out place only. The
same clauses, on held-out results.

**Printed and not judged:** found counted per frame, found either way (strict, or with the box off), every condition,
the extreme conditions, and every barrel gained and lost.

## The sanity checks, and what each must say

- **S1. Today's detector against itself.** NO CLEAR DIFFERENCE, with no barrel and no box changed. Anything else is a
  bug in the tool.
- **S2. The changes that mean nothing.** Sets A (14 one-step) and B (12 joint) are inside the margins by construction:
  all 26 must be NO CLEAR DIFFERENCE, which checks the tool end to end, not the margins. Two of them (the largest gain
  and the largest one-step loss) are run through the whole tool and must give what the noise run recorded. Set C (12
  unseen joint moves) is the check of the margins; its result is already known (2 of 12 called) and is repeated.
- **S3. Tanush's hand thresholds** (per condition, the median of the slider labels of that condition's train frames;
  conditions without labels keep the fixed model). In-sample by nature: the labels were set on three of each
  condition's frames. **Must PASS.** If the verdict is anything else, the rule is wrong, and the rule is changed with
  a dated addendum that names the clause; the candidate is not touched.
- **S4. "Blue follows the light"** (`Config.hs_light`), leave one place out exactly as `2026-11-25_color` did it:
  inside each fold that experiment's own selection rule picks the setting on the other places (`test.choose`), for
  its two families C2 (the light read from the whole frame) and C2b (read above the horizon gate). **No verdict is
  required.** Reported: the verdict, each clause, the places, the setting chosen in each fold.

Every verdict of S3 and S4 is given twice: with the margins as used, and with the margins as first registered (the
largest absolute change both ways: found 10.92, boxes 1.85), so that the effect of the noise-floor addendum is
visible. Also reported: how long one judge run takes.

## What would make me distrust the rule

S1 not identical (a bug). S3 not PASS (the rule is wrong). A verdict that sits within one whole unit of a margin: the
clause and the distance are named in the summary, and the verdict is to be read as "at the margin".

## Outputs

`results/2026-11-26_judge/`: `summary.md`; one folder per judged candidate with `judge.md`, `judge.json`,
`changes.csv`; `chosen.json` (the settings the folds picked).
