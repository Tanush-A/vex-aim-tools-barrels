# Pre-registration: thresholds as RANGES, and a range-based adaptive rule (2026-11-24 experiment)

Written 2026-11-23, late evening, **before any range was computed** and before the rule below ran on a single
frame. Committed on `wip/adaptive-range` before `run.py` existed. Nothing is adopted by this experiment: the
default color model stays `eb863d84`; the rule lives behind the existing switch (`pipeline.Config.hs_adapt`, empty =
off), with no change to `pipeline.py`. The earlier rule (`experiments/2026-11-24_adaptive/`, its PREREG, its frozen
copy and its scoring) is left untouched; the rule below is a new arm.

## Why (Tanush, 2026-11-23)

"For some frames I put the saturation floor super low because I could and it slightly helped with barrels, but I
could also put it higher and it'd be fine. A lot of it depended on what background clutter existed in the image."
So a frame has a **range** of thresholds that work, and his slider value is one point inside it, chosen partly
arbitrarily. The 2026-11-24 analysis tried to predict the exact point (partly noise) and found nothing with 3 places.
Here the target is the range: a prediction is right when it lands inside it.

## What was looked at before this was written

The 2026-11-24 adaptive results (`results/2026-11-24_adaptive/summary.md`, `analysis.md`): hand values, box-derived
values, features per condition, the failed rule. The slider label values (`data/labels/*_hs.json`). Tanush's quote
above. No range of any kind has been computed on any frame.

## Data

Train frames with a slider label `<stem>_hs.json` AND a box label (today 18 frames: `core_01`, `clutter_01`,
`occl_02` of 6 conditions at 3 places). Test frames are refused before any image is opened (`data/splits.json`).
Condition, place, light kind and class exactly as in the 2026-11-24 PREREG (`data/conditions.json`; parked
extreme; `extreme (ceiling)` by the same mechanical rule, computed by that experiment's loader; today
`lampmid3_ottoman`). Ranges are computed for every slider-labelled frame; the prediction analysis and the rule use
the **ordinary** conditions only; ceiling conditions are printed beside them.
**Clutter:** a frame is "with clutter" when its scene tag is `clutter`; `core` and `occl` frames are "without".
Labels written through the slider proposal (`"proposed": true`, see `docs/DATA.md`) count as slider labels; the
summary counts them and says how many were saved without moving a slider.

## Part 1 — the feasible range of each threshold on one frame

**Anchor** A = his six slider values for the frame. The detector is today's (`detector.DetConfig()`, camera
`AIM_4A8B6118_BOXFIT`), scored against **his hand-drawn boxes** with the v2 rule (`eval_det.evaluate_frame`,
`rule="v2"`). The detector's boxes are never treated as truth.

Per setting T (six numbers) and frame, measured on `pipeline.segment` with the adopted model's gates (rows ≥ 50,
V ≥ 40, tie rule) and T as its two class boxes:
- `found(T)`: the set of his boxes matched by a detector box (v2); `false(T)`: detector boxes matching none.
- `core_c(T)`: for class c (orange / blue), the share of the pixels in the **cores** of his c-colored boxes that are
  painted c. Core = the box shrunk by 15 % of its width on the left and on the right and by 15 % of its height at the
  top and the bottom (the corners of a box hold table). nan when the frame has no c box.
- `out_c(T)`: the number of pixels painted c **outside** his boxes, each box padded by 4 px, rows ≥ 50.

**"Working", detector version (primary).** T works when, for every class c (both are checked):
1. `found(T) ⊇ found(A)` (every barrel found at his values is still found; finding more is fine),
2. `false(T) ≤ false(A)`,
3. `out_c(T) ≤ out_c(A) + max(150 px, 10 % of out_c(A))` (150 px is a blob about 12 × 12).

**"Working", pixel version (secondary, no detector).** T works when, for every class c,
`core_c(T) ≥ core_c(A) − 0.05` (5 percentage points; skipped when nan) and clause 3 above.

**The sweep (one threshold at a time).** For each of the six thresholds, the other five at his values: step away
from his value, down and then up, by 1 hue unit or 2 S units, and stop at the first value that does not work. The
range is [last working value below, last working value above]: the contiguous run that contains his value.
The sweep also stops at the slider's limits (orange hue −30..60, blue hue 60..150, S 0..255; the end is then marked
**open**) and where a hue end meets the other end of its sector (marked **other end**). Each closed end records
**why** it stopped: `barrel lost`, `false box`, `outside paint`, or `core paint` (pixel version).

**Joint check (the box of ranges).** One-at-a-time ranges need not work together. For the six detector ranges of a
frame: the 64 corners of the box and 64 points drawn uniformly inside it (integer values, seed 0) are each run with
all six numbers set at once and judged by the same "working". Reported: the share of corners and of random points
that work. **Confirmed box** = the box shrunk toward his values by the largest factor s in {1, 0.75, 0.5, 0.25} for
which every corner works and at least 90 % of 64 random points inside it work; s = 0 (his values alone) when none
does. The ranges "hold jointly" on a frame when s = 1.

**Condition range** of a threshold = the intersection of the ranges of the condition's labelled frames; when the
intersection is empty, the median of the lower ends to the median of the upper ends, flagged `empty`.

Reported: per threshold, the width of the range (median, min, max over frames) **with and without clutter**; per end,
how often each reason stopped it; the share of open ends; the joint check per frame; whether the adopted (fixed)
value lies inside each frame's and each condition's range. A threshold is called **constrained** when the fixed
value lies outside the condition range of at least one ordinary condition, or its median width is ≤ 6 hue units
(≤ 30 S units); otherwise **loose**.

## Part 2 — does anything predict the ranges (leave one PLACE out)

Unit: ordinary conditions with slider labels; feature = the condition's mean of the frame feature (the nine
features of `hsrel.FEATURES`, from the frame's own histogram, no label). For each held-out place, predictors fit on
the other places only:
- **fixed**: the adopted value;
- **mean of the other places**: the place-weighted mean of their condition-range midpoints;
- per feature f, **line through home**: `fixed + b · (f − f_home)` with b by place-weighted least squares on the
  other places' range midpoints (`adaptive.fit_slope`; f_home = the mean over the home train frames);
- per feature f, **interval fit**: the same line, b chosen to put the most other-place conditions inside their
  ranges (place-weighted), ties broken by least squares to the midpoints.

A prediction is **right** when it lands inside the held-out condition's range (one-at-a-time detector version; the
confirmed-box version is printed beside it). Reported per threshold and per place: how often each predictor is right
(a place's score = the share of its conditions that are right; then the mean over places). A feature **beats** fixed
and the mean when its right-rate over places is higher than both. With 3 places this is description, not proof;
frame-level hits (each frame's own feature into its own range) are printed too.

## Part 3 — the revised rule (R2) and its test

**R2, fit on a set of places (per leave-one-place-out fold, or on all for the gate and the frozen copy):**
for each of the six thresholds t, over the training places' ordinary slider-labelled conditions:
1. if the fixed value lies inside the condition range of **every** training condition, t stays fixed (no term);
2. otherwise t adapts with its **primary frame-only feature**, fixed now: `orange_peak_h` for both orange hue ends,
   `orange_s_p90` for the orange S floor, `blue_peak_h` for both blue hue ends, `blue_s_p90` for the blue S floor;
   form `fixed + b · (feature − f_home)`, clipped to ±10 hue / ±60 S units (the 2026-11-24 form; an `adaptive.Term`),
   b by the **interval fit** above (clipping applied when counting hits). The term is kept only when its
   place-weighted hits are **strictly more** than the fixed value's (b = 0); else t stays fixed.
Per frame, the threshold is computed from that frame's own histogram (as the earlier rule; a frame without a reading
keeps fixed; an empty hue range keeps the color's fixed box). Pixels are never changed; nothing is carried between
frames.

**Test — exactly the 2026-11-24 PREREG part C, with R2 in place of that rule.** Leave one place out (R2 fit without
the held-out place, applied to every frame of its ordinary conditions); per condition found / false / boxes on empty
frames, fixed against R2; the never-regress gate with R2 (fit on all places) ON (`report.make_report` +
`gate.compare`, HOME leave-one-scene-out); R2 frozen tonight (`rule_range_frozen_2026-11-23.json`) applied unchanged
to places new since tonight. Acceptance clauses **C1–C7 with the same numbers** (C1 ≥ 5 slider-labelled places;
C2 ≥ 3 more barrels, more in ≥ 2 places; C3 ≤ 2 more false boxes; C4 no new box on an empty frame, none on a clean
empty frame; C5 no ordinary condition's score drops by more than 0.02; C6 the gate with R2 on adds no failing row to
the fixed model's; C7 on new places the frozen R2 finds at least as many as fixed with at most 1 more false box).
Exit 0 only if every clause holds. A pass is **proposed, not adopted**.

Also printed (report-only): the 2026-11-24 rule's per-condition thresholds (as that experiment computes them, leave
one place out) scored as hits against the ranges, so the two rules can be compared on the range target.

## "The range version holds" (the one-line verdict for the summary)

It holds when (a) the ranges hold jointly (confirmed box s ≥ 0.5) on at least two thirds of the frames, AND (b) for at
least one threshold that is constrained, R2's leave-one-place-out thresholds land inside the held-out condition ranges
more often than the fixed value does, AND (c) R2 passes C2–C6. Otherwise it does not hold, and the summary says which
part failed. C1 (number of places) is reported separately: with fewer than 5 places nothing is adopted either way.

## What would make me distrust a pass, or "holds"

A range narrower than the noise of one detector call (an end closed one step from his value: printed as the share of
such ends); joint check failing on most frames (then one-at-a-time ranges overstate the freedom); a gain carried by
one place; the frozen R2 failing on new places while the refit passes.

## Outputs

`results/2026-11-24_adaptive_range/`: `summary.md` (one page, plain words: does the range version hold),
`ranges.csv` (frame × threshold × version), `joint.csv`, `prediction.csv`, `detection.csv`, `rule.json`,
`model_r2.json`, `gate.txt`, `config.json`; a copy under `runs/`. `experiments/run_all.py` runs it as its own step.
