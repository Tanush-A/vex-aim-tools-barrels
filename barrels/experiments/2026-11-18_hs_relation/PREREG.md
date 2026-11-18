# Pre-registration: does a frame's own histogram predict the right thresholds? (TODO F)

Written 2026-11-18, before the first run on real numbers. Plan agreed by Tanush and Dave (meeting 2026-11-16,
`TODO.md` 2026-11-18). Script: `run.py` in this folder; helpers: `src/barrels/hsrel.py`. Nothing is adopted by
this experiment and the detector, pipeline, geometry and eval are not changed.

## The question

The adopted color model has six numbers: per color a hue range and a saturation floor (orange hue 3 to 13,
S ≥ 140; blue hue 103 to 119, S ≥ 113). They were fit at home and are wrong elsewhere. Tanush sets the best six
numbers by hand on three frames per condition (`data/labels/<stem>_hs.json`). **If something measurable in the
frame's own hue × saturation histogram predicts those numbers, that relation becomes the adaptive rule.**

## Data

- A **condition** = one table under one light = the `{light}_{surface}` part of the frame name. Frames of one
  condition share the light, so **the unit of evidence is the condition, not the frame**: n is the number of
  conditions everywhere.
- Train frames with box labels only. The script refuses any test frame before an image is opened.
- Classes (`hsrel.classify`): **excluded** = lamp brightness 1 (`lamp*1`), nowhere in the analysis;
  **extreme** = a lamp on the orange wood table (`lamp*_wood`) and the black table under window light
  (`window_black`), parked on 2026-11-18, not targets; **ordinary** = everything else, so every new condition
  is ordinary unless it is added to that list (a logged choice, made before its numbers are looked at).
- Every result is given twice: **ordinary only**, and **ordinary + extreme** (marked). The six wood conditions
  are one table and the same ten arrangements under six lamp settings: they are not six independent points,
  and leaving one out leaves five near-copies in. The "with extreme" tables are therefore optimistic and are
  never the basis of a conclusion.

## Targets: the six thresholds per condition

1. **hand**: the slider labels, median per threshold over the condition's labeled train frames. The analysis
   on this target runs on the conditions that have at least one.
2. **box**: the thresholds read from the hand-drawn boxes, per frame, by the recipe of the ceiling check
   (`2026-11-16_hs_oracle/run.py`, arm `hue+sat+stripes`: S floor = 5th percentile of the orange pixels' S, 15th
   of the blue; hue range = 5th to 95th percentile above the floor, widened by 2; pixels = home masks, elsewhere
   box cores at the class's hue peak plus that color's stripes on the other color's barrels). Median over the
   condition's frames in which that color has at least 200 such pixels. Used until hand labels exist and always
   alongside as a cross-check.

The two targets are never mixed in one fit. Where both exist the summary gives hand − box per threshold: that
says whether box can stand in for hand.

## Features: from the frame alone, no label (9, fixed)

From the H × S histogram of the pixels below row 50 with V ≥ 40 (the pixels the model may label). Window
features use pixels with S ≥ 40 only (below that a hue means nothing) and are missing for a frame whose window
holds fewer than 200 pixels. Per-frame values are averaged per condition.

| # | feature | why it might track a threshold |
|---|---|---|
| 1 | `v_mean`: mean V | exposure; a dim scene lowers the saturation the camera records |
| 2 | `s_median`: median S of all pixels | how colored the scene as a whole is (a color cast lifts it) |
| 3 | `s_share100`: share of pixels with S ≥ 100 | how much strongly colored stuff the S floors must tell from the barrels |
| 4 | `blue_peak_h`: tallest hue in 85 to 125 | where blue sits in this frame → the blue hue range |
| 5 | `blue_s_p90`: 90th percentile of S in that window | how saturated the most saturated blue is → the blue S floor |
| 6 | `orange_peak_h`: tallest hue in −10 to 30 | where orange sits → the orange hue range (on wood this peak is the table: said in advance) |
| 7 | `orange_s_p90`: 90th percentile of S in that window | → the orange S floor |
| 8 | `ref_hue_shift`: the hue offset (−20 to 20) that best lines the frame's hue distribution up with the pooled home one | Tanush's idea: the whole histogram moves with the light |
| 9 | `ref_s_scale`: median ratio of the frame's S deciles to the pooled home ones | the same for saturation |

Left out on purpose: the number of pixels in each window (it measures how many barrels are in view, not the
light). The reference for 8 and 9 is the pooled histogram of the home train frames, a constant of the method;
home therefore reads shift ≈ 0, scale ≈ 1 by construction.

## Analysis

**1. Is there a relation?** For every (feature, threshold) pair at condition level: Spearman rank correlation
and a two-sided permutation p-value (all n! re-pairings when n ≤ 8, else 20 000 random ones, seed 0). Up to
9 × 6 = 54 pairs: at p < 0.05 about 2.7 would look significant by chance alone. So:
- a **primary family of 12 pairs** with a physical reason, named now: each hue threshold with its color's peak
  hue and with `ref_hue_shift`; each S floor with its color's `*_s_p90` and with `ref_s_scale`. Holm correction
  over the 12 (about 0.6 expected by chance uncorrected).
- all 54 pairs are exploratory, Holm-corrected over the 54; a hit there is a lead, not a finding.
- n is printed in every table. With all permutations the smallest possible p is 2 / n!: 0.33 at n = 3, 0.083 at
  n = 4, 0.017 at n = 5. Below n = 5 nothing can reach 0.05 whatever the data.
One scatter figure per threshold: its two primary features and its best other one.

**2. Does it predict?** Leave one condition out (LOCO). Fit `threshold = a + b · feature` on the other
conditions, predict the held-out one; error = |prediction − target|, mean over conditions (MAE), in hue units
or S units. Baselines: the **adopted fixed value**, and the **mean of the other conditions**.
- **The feature is chosen inside the loop**: for each held-out condition, the feature with the smallest
  leave-one-out error over the *remaining* conditions (ties: the earlier feature in the table above). Choosing
  the feature on all conditions first lets the held-out condition vote for its own predictor and the error
  reads too low; the script prints that number too, labeled **optimistic**, to show the size of the effect. It
  is never the result.
- Then at most a **two-feature** rule (a pair is taken only when its inner error is below the best single
  feature's), nested the same way.
- Too few conditions for a nested fit (fewer than 4 for one feature, 5 for two): the prediction falls back to
  the mean of the others and is flagged; it is then not evidence about the features.

**3. Does it detect?** For each held-out condition the six predicted thresholds replace the two boxes of the
adopted model and today's detector (`DetConfig()` defaults) runs on the condition's frames. Found / missed /
false and score per condition (`report.score_frame`, `report.summarize`, v2 rule) for: `fixed` (the adopted
model as stored, also at home: not the leave-one-scene-out home number), `pred1` (nested one-feature rule),
`pred2` (nested two-feature rule), `box median` (the box target itself, one model per condition: is the target
any good as a model?), `box per frame` (the ceiling check: thresholds read from each frame's own labels, not a
method), and `hand median` when hand labels exist. A predicted color whose range is not a range keeps the
adopted box and is flagged.

**4. Honesty about n.** With fewer than **8 ordinary conditions** the summary opens with: no conclusion about
a relation can be drawn, the tables are a dry run. The 2026-11-18 run has 2 ordinary conditions: it checks that
the pipeline works and gives a first look, nothing more.

## What must be true for a relation to count (checked only at n ≥ 8 ordinary conditions, aim: 10)

On the **ordinary** conditions, with the **hand** target (the box target only if hand − box is small: median
|difference| ≤ 3 hue units and ≤ 20 S units), per threshold:

- **A, relation:** at least one primary pair with Holm-corrected p < 0.05.
- **B, prediction:** the nested one-feature MAE is below both baselines, and its error is below the fixed
  value's in at least two thirds of the conditions.

and for the rule as a whole (thresholds that pass A and B predicted, the others left at the adopted value —
that mixed arm is built only then, as a new pre-registered step):

- **C, detection:** summed over the ordinary conditions `pred1` finds more barrels than `fixed`, with at most
  2 more false boxes in total, no box on a clean negative, and no condition whose score falls by more than 0.02
  (never regress).

A threshold that fails A or B stays fixed; that is a result too. A rule that passes is **proposed, not
adopted**: it is then written up as the adaptive rule, pre-registered, and scored with the eval table.

## What would make me distrust a result

A correlation carried by one condition (look at the scatter); a relation that exists only when the extreme
conditions are in; a feature that is chosen in few of the LOCO folds (the choice is unstable); a within-condition
spread of the per-frame thresholds as large as the spread between conditions (then there is nothing to predict
at condition level; the summary prints both); hand labels that differ from box by more than the differences
between conditions.

## Outputs

`results/2026-11-18_hs_relation/`: `summary.md`, `per_condition.csv`, `pairs.csv`, `predictions.csv`,
`detection.csv`, `per_frame.csv`, `config.json`, `fig_*.png` (ignored by git). The summary states the date, the
git hash and the conditions it was made from; every run is also copied to `runs/<nn>_<date>_<git>/`, so a
re-run with more conditions never overwrites the record of an earlier one.
