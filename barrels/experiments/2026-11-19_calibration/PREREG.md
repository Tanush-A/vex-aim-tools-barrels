# Pre-registration: does the ruler-fit camera replace the old one? (TODO A4)

Written 2026-11-19 **before** `validate.py` was run. Committed before any number of the new camera on a train frame existed.

## What exists when this is written

- The fit on the 12 ruler frames (`run.py`, `results/2026-11-19_calibration/fit.md`). Those frames are geometry-only and in no split.
- The size check of 2026-11-18 with the **old** camera (`results/2026-11-18_det_given_seg/size_check.md`): hand box / expected size 0.95 to 1.03 per set; the bottom inferred from the top row is too low by a median of 4.4 px (HOME), 5.35 (CAMPUS), 7.05 (wood), 1.1 (BLACK).
- Nothing has been computed with the new camera on any train frame. No test frame has been opened, and none will be.

## The two cameras

| | f, px | tilt | camera height, mm | horizon row |
|---|---|---|---|---|
| old: `geometry.AIM_4A8B6118_BOXFIT` | 400 | 22.25° | 43.47 | 76.4 |
| new: the rounded ruler fit | 400 | 20.4° | 40.2 | 91.2 |

Everything else is the same: centre (320, 240), the barrel 24 mm tall, 25.5 mm at the bulge, 18 mm at the ends. The new numbers are fixed here. They are not changed after the validation is seen.

## Validation 1: the size check on boxes the fit never saw

Frames: the train frames of HOME, CAMPUS, BLACK and the wood lamp ladder that have box labels. Boxes: every hand-drawn box not flagged `occluded`, `truncated`, `held` or `bottom_estimated` and not touching the frame (the selection of the 2026-11-18 size check).

Per box, for each camera:

- **width ratio** = drawn width / `expected_barrel_width_px(bottom_row)`: what the detector's width tests and the box tool's `g` use.
- **height ratio** = drawn height / `expected_barrel_height_px(bottom_row)`.
- **bottom from top** = `detector.predicted_bottom(cam, top row)` minus the drawn bottom row, px. Plus means the inferred bottom is too low.
- **bottom from width** = top row + `expected_barrel_height_px` at the distance the width gives (`f × 25.5 / width`), minus the drawn bottom row. This is how `cap_behind` sizes a box whose whole width shows.

Reported as median (10th to 90th percentile) per set, and per set by distance. Distance bands are by **drawn** width, so that both cameras are compared on the same boxes: far under 35 px, mid 35 to 60, near over 60. (The 2026-11-18 table used the old camera's expected width for the bands; the old-camera numbers are recomputed here with the new bands.)

## Validation 2: the eval table

`barrels.report.run_arm` with the adopted color model, `DetConfig()` as it is on this branch, HOME leave-one-scene-out, train frames, v2 rule: once with the old camera, once with the new. The camera is given to the arm (`Arm(cam=...)`, `tools/report.py --cand-cam / --base-cam`); no constant is edited.

## The acceptance rule

The new camera replaces the old one as the default **only if all three hold**:

**(a) The top-row bottom bias shrinks on HOME and on CAMPUS.** For each of the two sets: |median bottom from top| is smaller with the new camera than with the old one, over all its boxes, **and** over its far and mid boxes together (drawn width under 60 px), where the bias was reported.

**(b) Sizes stay right.** With the new camera the median width ratio and the median height ratio of HOME and of CAMPUS (four numbers, all boxes of the set) are each between 0.95 and 1.05.

**(c) Never regress.** In the eval table, for every scenario row of HOME and of CAMPUS: found with the new camera ≥ found with the old, and false boxes with the new ≤ with the old. And no negative frame of any set (HOME, CAMPUS, BLACK, every wood lamp setting, Dave's) has a box with the new camera. If the old camera already draws a box on a negative frame, the rule for that frame is: no more boxes than the old camera draws there.

If any of the three fails: no default changes, the new camera is not added as the default anywhere, and the report says which part failed and what measurement would settle it.

## Report only (does not decide)

- BLACK, the wood ladder and Dave's rows of the eval table, and the size check on BLACK and wood.
- The by-distance rows of the size check.
- Bottom from width against bottom from top with each camera (the question: should inferred bottoms come from the width; the detector is not changed for it here).
- Width ratio against the exact outline width (`silhouette_width_px`) instead of the shortcut.
- Bottom-from-top error against the box's column (a camera roll would show as a slope).
- Which found boxes, misses and false boxes differ between the two cameras, frame by frame.

## If it passes

The new camera becomes a named constant in `geometry.py` and the default everywhere the old one is the default (detector, eval table, live hook, detector tools, the box tool's `g`). The old constant stays selectable. Tests that pin numbers of the old camera keep testing the old constant.
