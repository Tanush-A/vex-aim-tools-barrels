# HOW-IT-WORKS.md — the main code, in plain English

Written for Tanush, so he can explain the detector to Dave without help. One section per **main** module: color segmentation, camera geometry, the detector, the detection eval. Side tools (labelers, importers, viewers) are not covered — they are allowed to be black boxes. Rule since 2026-11-02 (`DECISIONS.md`): every commit that changes main code updates its section here and gets a walkthrough in chat first.

Each section: *what it does*, *the idea* (why it works), *where it lives* (the file and the two or three functions that matter), *how to run it*, *what can go wrong*.

---

## 1. Color segmentation — `src/barrels/pipeline.py` (v1, frozen at config `afd85483`)

**What it does.** Takes one image and labels every pixel as barrel-orange, barrel-blue, or other. This is the front end of everything after it; the detector works on these pixel labels, not on the raw image.

**The idea.** Four cheap tests, each throwing out pixels that cannot be barrel:

1. **Horizon gate.** Nothing above row 50 can be a barrel: the camera (43 mm up) is higher than a barrel is tall (24 mm), so every barrel standing on the table appears below the horizon line. Those top rows are therefore guaranteed background, which the next two tests exploit.
2. **Saturation floor.** Barrels are vivid; tables, walls and glare are grayish. "Saturation" here is simply max(R, G, B) − min(R, G, B). The floor is not a fixed number: the image's own background rows say how colorful the background is, and the floor is set a margin above that. A warm-lit room with a yellowish wall gets a higher floor by itself. Computed fresh for every image.
3. **Wall model.** From the same background rows, a robust estimate (median and spread) of the background color; pixels within a few spreads of it are rejected. Also per image.
4. **Color boxes.** The one thing learned from labels: for each class, a box in RGB space (the 1st–99th percentile range of labeled barrel pixels that survive the gates). A surviving pixel inside the orange box is orange, inside the blue box is blue; in both, the redder one wins.

A brightness gate (reject near-black pixels, where color is noise) sits alongside; it changes nothing on light tables and exists for dark ones. A "table model" built from the bottom rows exists as a switch but is off: a close barrel's shadow fools it.

**Why the boxes alone don't work.** Barrel pixels in RGB form a smear along the brightness axis, so a box wide enough to include shadowed faces also includes table and wall. The floor and the wall model do the separating; the boxes only decide orange vs blue among the survivors.

**Where it lives.** `Config` (every knob; defaults = the frozen v1 config), `Frame.from_image` (the image plus its saturation and brightness planes), `fit(frames, masks, cfg)` → `Model` (learns the two boxes from labeled frames), `segment(frame, model)` → mask + an info dict (which floor it used, and so on).

**How to run it.** `python barrels/tools/segment_image.py image.png` writes the orange, blue, class-mask and overlay images to `results/segment_image/`. The fitted model is `results/2026-10-20_v1_test_adaptive/config.json`.

**What can go wrong.** Shadowed lower faces of blue barrels fall below the saturation floor (the main v1 miss). Skin lands inside the orange box. Under a strong color cast the fixed RGB boxes can miss while the floor and wall model adapt — this is why v2 allows one re-fit of the boxes on frames from all tables.

**Numbers.** Held-out test: orange IoU 0.84, blue 0.81, zero false pixels on the empty frame (`EXPERIMENTS.md` 2026-10-20).

## 2. Camera geometry — `src/barrels/geometry.py` (v1.5)

**What it does.** Converts between image rows and real-world distances for this robot's camera, and says how big a barrel should look at any place in the image.

**The idea.** The camera is a pinhole at a known height (43.47 mm), tilted down by a known angle (about 23°), with a known focal length (about 400 px). With those three numbers, a point on the table at a given distance appears at a row you can compute, and the other way round. Because the barrel's size is known (24 mm tall, 25.5 mm at the bulge, stripe at mid-height), every row has an expected barrel width and height. So seeing any one part of a barrel — top edge, stripe, or width — tells you how far away it is, and therefore where every other edge must be. Two subtleties: the box's top is the lid's *far* edge and its bottom is the base's *near* edge, so they are at slightly different distances; and rows are not linear in height, so the stripe's center row is not the average of its top and bottom rows.

**Where it lives.** `CameraModel` (f, tilt, height) with `horizon_row`, `row_to_ground_distance`, `point_row(d, z)`, `barrel_rows(d_axis)` → the top, stripe and bottom rows and the width of a barrel at that distance, and the inverses `bottom_row_from_top_row`, `bottom_row_from_stripe_row`, `bottom_row_from_width`. Presets: `AIM_4A8B6118` (our robot, f 404 / tilt 23.3), `NOMINAL`, and the honest range `AIM_4A8B6118_RANGE`. `image_to_ground` reproduces the robot's own ground projection; kept for later, not used in v2.

**How to run it.** `python -m barrels.geometry --tilt 23.3 --f 404` prints the table in `constraints.md`.

**What can go wrong.** f and tilt for our robot are known only to about ±10 % (three methods disagree). Close to the robot, small tilt errors move rows a lot. v2 M4 fits both from the known-distance `calib` frames.

**Numbers to remember.** Horizon row ≈ 66–70. The bottom edge leaves the frame when the barrel's base is within ≈ 28 mm of the bumper; in that zone the top edge moves ≈ 13 px per mm.

## 3. The detector — `src/barrels/detect_stripe.py` (v2, to be written)

Filled in step by step as v2 M6 lands. Planned sections: the stripe finder; a barrel from its stripe (color, distance, expected box); stripeless candidates and the size-and-shape check; carving boxes out of merged blobs; bottom-edge precedence; clipping and drawing.

Until then, `detect_cc.py` is the deliberately dumb reference: one box per connected blob of barrel pixels. It merges touching barrels by design and exists only to set the floor the real detector must beat.

## 4. Detection eval — `src/barrels/eval_det.py`

**What it does.** Scores predicted boxes against the hand-drawn boxes: for each image, which predictions match which true barrels, and from that precision, recall and F1 per color, plus how far off the bottom edges are.

**The idea.** A prediction and a true box match only if they have the same color, overlap enough (intersection over union ≥ 0.5) and their bottom edges agree within a tenth of the barrel's height. Matching is greedy: the best-overlapping eligible pair is taken first, then the next, so each true barrel is used at most once. What is left over is either false (an extra box) or missed (a barrel with no box). On frames with no barrels every box is false. *(The bottom-edge condition and box ground truth arrive in v2 M2; the current code still reads instance masks and ignores occluded barrels.)*

**Where it lives.** `evaluate_frame`, `aggregate`, `write_results`, `score`. CLI: `tools/eval_boxes.py --pred DIR --split test`.

**What can go wrong.** The true bottom edge of a hidden base is itself a human estimate, so bottom-edge error is reported separately for `bottom_estimated` boxes.
