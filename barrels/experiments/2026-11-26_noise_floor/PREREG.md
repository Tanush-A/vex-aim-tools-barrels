# Pre-registration: the noise floor of the counts (2026-11-26, TODO M2)

Written 2026-11-26 on branch `wip/measure`, **before `run.py` existed and before any number below was computed**.
Question: how much do the counts move under a change that means nothing? The answer sets the margin of the
never-regress check (M2) and of the standard pass rule (M3). Train frames only; no test frame is opened, scored or
listed.

## What was seen before this was written (honesty)

The review's forensic report (section h) and the output of its train-only script (`k_analyse.out`): for the 12
one-step neighbours of the fixed color model on the 154 ordinary train frames, under the strict rule and counted per
frame, found moved between 204 and 215 against 211, false boxes between 5 and 11 against 7, one neighbour put a box on
three empty glass frames, and single conditions moved by up to 0.36 of their score (the gray table, orange hue low
3 -> 4). Not seen: anything counted per placement, anything under the second accounting, any per-place or
per-protected-set distribution, the brightness-floor neighbours, any joint move.

## What is changed (the "changes that mean nothing")

The fixed color model is `eb863d84`: orange hue 3..13, S >= 140; blue hue 103..119, S >= 113; brightness floor 40.

- **Set A, one step (14 neighbours). The margins come from this set and from nothing else.** Each of the four hue edges
  moved by -1 and by +1 (8); each of the two saturation floors by -3 and by +3 (4); the brightness floor by -2 and by
  +2 (2). One number changes at a time; the detector (`DetConfig()`), the camera and the labels do not change.
- **Set B, joint moves (12). A check, never a source of margins unless the rule at the end says so.** Seeded draws
  (seed 20261126): each of the seven numbers moves by -1 step, 0 or +1 step (a step as in set A), independently, each
  with probability one third; a draw that moves fewer than two numbers is drawn again. This asks how much larger the
  effect is when several small changes come together.
- Not added: the horizon row (it only changes four image rows); detector constants (a different question: the
  detector's own sensitivity, not asked here).

## Frames and scoring

Every train frame with a box label, without Dave's frames and the geometry-only scenes: 261 frames, 28 conditions, 10
places. HOME is scored with the model as it is, not leave-one-scene-out: a neighbour is a model moved by hand, there is
nothing to re-fit (the never-regress check keeps its leave-one-scene-out protocol for HOME; its margin is a
difference, taken from here). Counting: `src/barrels/counting.py`, definitions in
`experiments/2026-11-26_measure/PREREG.md`.

## What is measured

For every neighbour, the change against the fixed model (neighbour minus fixed) in:

- found, strict (the v2 rule): per frame count at condition level, placement-weighted from place level up;
- found either way (strict hit or found with the box off);
- extra boxes (wrong color + second box + on nothing), and boxes on nothing alone; counted per arrangement from place
  level up;
- boxes on empty frames: on clean empty frames, and on the others (clutter only).

At these levels: every condition (28); every place (10); every proposed protected set (HOME, CAMPUS, the glass table
with its 5 lights, pale wood, the ABP white occlusion set, the bathroom under the cool lamp); the ordinary conditions
together (17 conditions, 8 places: what the pass rule is computed on); all train frames together.

Reported for each measure and level: the median, the 90th percentile and the maximum of the absolute change, over
neighbour x unit pairs (condition and place level) or over neighbours (overall), for set A and for set B apart. For
the place level also, per neighbour, the largest drop in any one place.

## How the margins will be taken from the numbers (decided now)

1. **A margin at a level is the largest absolute change that any set-A neighbour produces at that level, and never
   less than one whole unit** (one placement for found; one box, counted per arrangement, for boxes). Each place and
   each protected set gets its own; the ordinary conditions together get one.
   Why the maximum and not the 90th percentile: with 14 samples the 90th percentile leaves one or two changes that
   mean nothing beyond the margin in every clause, and a rule with four clauses would then call a clear difference on
   several of them. The 90th percentile is printed beside it as the tighter choice.
   Why one whole unit as the floor: one barrel flipping is the smallest thing that can happen, and a margin below it is
   the zero-tolerance rule again.
2. **Clean empty frames stay at zero** if no set-A neighbour puts a box on a clean empty frame. If one does, that is
   reported in the first line of the summary and the zero is no longer tenable; the margin is then that maximum.
3. **The check with set B.** The gate and the pass rule, with the margins from set A, are applied to each joint move.
   If more than 2 of the 12 fail the gate, or more than 2 of the 12 get a verdict other than NO CLEAR DIFFERENCE, the
   margins are too tight for small changes that come together; they are then taken from the largest change over sets A
   and B, and the summary says so.

## What would count as what

- The largest set-A change in strict found over the ordinary conditions together is **under one placement**: the
  counts are stable to within one barrel and every margin is its floor.
- It is **several placements**: a difference of that size between two candidates is not evidence; only larger ones are.
- A set-A neighbour moves **one place by more than a third of its placements**: that place sits on a threshold edge
  under the fixed model. It is named. Its wide margin is a finding about the place, not a licence to lose it.
- A set-A neighbour puts a box on a **clean** empty frame: see 2.

## Outputs

`results/2026-11-26_noise_floor/`: `summary.md` (the distributions and the margins), `noise.json` (every change, every
level), `per_neighbour.csv`; and the margins as data in `results/baseline/margins.json`, read by `gate.py` and
`judge.py`. The script is re-run whenever the default color model or the default detector changes
(`python barrels/experiments/2026-11-26_noise_floor/run.py`).
