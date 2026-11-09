# HOW-IT-WORKS, the short version — start here

One page to understand (or re-explain) the detector. The long form with worked numbers is `HOW-IT-WORKS.md`; the diagrams of how the files fit are `ARCHITECTURE.md`. State as of 2026-11-09 (the hs color model is the front end, the stripe step with hardening a–g is the detector; all on `barrels`).

**Naming note.** `EXPERIMENTS.md`, `DECISIONS.md` and `TODO.md` call the stripe step "detector step 2" (it was the second thing built, after "step 1" = blobs → count → bottom edge). In the two HOW-IT-WORKS files the detector is explained as four steps, and the stripe is **step 4**. Same thing.

## The chain

**Photo (640 × 480) → class mask → barrels → photo with boxes.**

```
python barrels/tools/detect_image.py barrels/data/raw/4A8B_window_light_touch_02.png            # the detector (steps 1–4)
python barrels/tools/detect_image.py barrels/data/raw/4A8B_window_light_touch_02.png --step1    # steps 1–3 only, for comparison
```

Nothing learns from the photo it is looking at. The only learned numbers are two per color — a hue range and a saturation floor — fit once from labeled frames. Everything else is physics: barrel size, camera height, tilt.

## 1. Color segmentation (`pipeline.py`, the hs model since 2026-11-09)

Every pixel becomes orange (1), blue (2) or other (0). A pixel is a barrel color when it is below row 50 (above the horizon nothing is a barrel), brighter than 40, its **hue** is inside the class's range and its **HSV saturation** ((max − min)/max: a shaded navy face keeps it high, a gray wall never reaches it) is above the class's floor. Orange: hue 3–13, S ≥ 140. Blue: hue 103–119, S ≥ 113. Those four numbers were read off the 16 labeled home frames once; nothing is estimated from the image being looked at. Scores: campus 0.99 vs 0.41 for the old front end, home 0.93 unchanged, nothing on any empty frame.

**What it replaced (v1, until 2026-11-09):** a saturation floor and a wall color estimated **per image** from the top 50 rows, then fixed RGB boxes. That assumed the top rows are a plain wall; in a real room (Dave's office, the campus study room) they are clutter, the floor jumped to 96–120, and the barrel bodies themselves were thrown away. Kept as `--model results/2026-10-20_v1_test_adaptive/config.json`; `HOW-IT-WORKS.md` §1, second half.

**Open question (TODO steps 8 and 10):** the thresholds are fixed, so a strong color cast can move orange out of its hue range. The plan is to look at hue/saturation histograms across light settings first, then decide what an adaptive version keys on.

## 2. Camera geometry (`geometry.py`)

Pinhole camera 43.47 mm above the table, tilted down 22.25°, focal length 400 px. Two formulas: a point at distance d and height z lands on row `240 + f·tan(atan((h − z)/d) − tilt)`, and backwards a row gives a distance. The barrel is 24 mm tall, 25.5 mm wide at the bulge, stripe 6 mm at mid-height. So for a barrel at any distance the geometry says its top row, stripe rows, bottom row and width (`barrel_rows`); and seeing any one of those tells you the distance and therefore all the others. At 20 cm: 51 px wide, 55 tall, bottom at row 174. Horizon row 76.

The tilt was corrected on 2026-11-03: the October estimate (23.3°) put every predicted bottom ≈ 20 px too low; fitting from 24 labeled barrels gives 22.25°. Labeled boxes pin the horizon row, not f and tilt separately; the known-distance calibration frames will do that.

## 3. The detector (`detector.py`)

- **Step 1, blobs.** Group touching barrel-colored pixels, orange and blue together (body + stripe stay together); close 3 px gaps; drop specks under 20 px.
- **Step 2, how many barrels.** Blob width ÷ the width one barrel must have at that row (from the bottom row, or the top row if the bottom is out of frame), rounded. Two or more → cut at the waist, the narrowest column near the halfway point, because touching barrels meet only at their bulges. Each piece's color is its majority color, the body.
- **Step 3, the bottom edge.** The top row gives the distance, the distance says where the base must be. Keep the seen bottom if it agrees within 15 % of the height (min 4 px); otherwise draw the predicted bottom and flag `bottom_inferred`. Clip to the frame; a box at the frame edge is `truncated`. Drop pieces that are not barrel-sized for their row (0.4–1.6 × the expected width, and nearer than ≈ 60 cm).
- **Step 4, the stripe (the default since 2026-11-05).** A stripe is a patch of the *other* color with body color right above *and* right below it (within 3 stripe heights, pixel by pixel — since 2026-11-08; before, it was any non-body gap between body above and below, which let glued shadow veto a stripe and let a dark gap pass as one). It must have stripe proportions for its row (0.45–1.6 × the expected stripe height, at least 0.4 barrels wide). Every stripe is one barrel: its row gives the distance, the distance the full box; seen edges are used when they agree; the box must hold body color in the stripe's columns (else it belongs to something else). A narrow stripe is partly hidden → the box is widened to a full barrel toward the occluder, flagged `occluded`. Pieces without a stripe survive only where a stripe could not be seen: the blob reaches the frame bottom (close barrel) or the expected stripe is under 4 px (too far) — and they must be barrel-tall as well as barrel-wide.

**Numbers** (16 train frames, Tanush's boxes; re-run 2026-11-05, identical). Overlap rule: floor 0.48, steps 1–3 **0.86**, with step 4 **0.97**. Honest v2 rule (every barrel counts, bottom within a tenth of the height): floor 0.43, steps 1–3 **0.71**, with step 4 **0.91**. Bottom edge within 1 px on 23 of 25 matches. Nothing drawn on empty frames.

**Works:** single barrels at any distance; touching rows, same or mixed colors; bunched barrels that each show a stripe; a partly hidden barrel whose stripe shows (full box through the occluder); close barrels with the bottom below the frame; hands, even touching a barrel; empty frames; barrels cut by the frame side.
**Doesn't:** a barrel whose stripe is entirely hidden; Dave's frames (section 1); untested: knocked-over barrels, other tables and lights, orange or blue clutter.

## 4. Scoring (`eval_det.py`)

A predicted box matches a true box if same color and overlap (intersection over union) ≥ 0.5; greedy, each true barrel used once. Precision = hits ÷ boxes drawn; recall = hits ÷ barrels; F1 blends them; the headline is the mean of the orange and blue F1. The v2 rule (`--rule v2`) adds "bottom edge within a tenth of the box height" and counts every barrel, occluded ones included; a box on a clean empty frame disqualifies.

## 5. On the robot (`live/`, `worldmap_bridge.py`, `tracker.py`)

Two small aim_fsm state machines on one base (`live/barrel_live.py`). **`BarrelViewer`**: once a second, take `robot.camera_image`, hand it to `BarrelDetectorHook.view`, show the result with Dave's `imshow`; every frame is answered on its own, exactly as a photo is. **`BarrelTracker`**: five times a second, the same detector, but a barrel is shown only once it has been seen in 3 of the last 4 frames, stays through a missed frame and is forgotten after 4 misses in a row (`tracker.py`; the box drawn is the median of the recent ones), so one-frame blips never show and a barrel lost for a frame does not blink. The hook converts RGB → BGR, runs sections 1 and 3, draws with `detector.draw`, converts back. At the `C>` prompt: `tm seg` / `tm boxes` / `tm both` switch the view, `tm save` / `tm rec` write raw frames to `live/snapshots/` for importing, `tm raw` (tracker only) overlays the per-frame boxes in white. Run: `cd barrels/live && simple_cli BarrelViewer` or `simple_cli BarrelTracker` (`RUNBOOK.md`). First live run 2026-11-06: the programs work; the detector failed off the training table, in both the segmentation and the stripe step (`EXPERIMENTS.md` 2026-11-06).

## What code to read, in order

| file | lines | read | what you'll see |
|---|---|---|---|
| `tools/detect_image.py` | 72 | all | the whole chain in 10 lines: load model → segment → detect → draw |
| `src/barrels/detector.py` | 395 | `DetConfig` (l. 28), `find_blobs` (69), `expected_width_px` (92), `split_blob` (105), `predicted_bottom` (140), `resolve_bottom` (150), `detect_step1` (170); then `find_stripes` (212), `barrel_from_stripe` (289), `detect` (345), `draw` (388) | the detector, in the order of this page |
| `src/barrels/geometry.py` | 199 | `horizon_row` (61), `point_row` (65), `row_to_ground_distance` (71), `barrel_rows` (117), the presets (≈ 165) | the two formulas and the barrel table |
| `src/barrels/detect_types.py` | 147 | the `Barrel` dataclass at the top | what one detected barrel is |
| `src/barrels/pipeline.py` | 293 | `Config` (39), `effective_s_min` (158), `segment` (252) | the per-image floor and the pixel tests; skip `fit` |
| `src/barrels/eval_det.py` | 429 | `box_iou`, `match_best_first`, `evaluate_frame` | how a hit is decided |
| `src/barrels/worldmap_bridge.py` | ≈ 150 | `BarrelDetectorHook` (`view`, `render`) | the live feed's one function: RGB in, drawn RGB out |
| `live/BarrelViewer.fsm`, `live/BarrelTracker.fsm` | ≈ 50 each | all | the two state machines (half docstring); `live/barrel_live.py` is what they share |
| `src/barrels/tracker.py` | ≈ 110 | the docstring, `Tracker.update` | the 3-of-4 rule |
| `experiments/2026-11-03_det_step2/run.py` | 84 | all | how the numbers above are produced; the sheets |
| `experiments/2026-11-03_geo_boxfit/run.py` | 97 | `residuals`, `main` | the tilt re-fit |

Side tools you can treat as black boxes: `tools/box_tool.py`, `tools/import_snaps.py`, `tools/import_dave_zip.py`, `tools/make_splits.py`, `tools/segment_image.py`, `src/barrels/capture.py` (`tm save` / `tm rec`).
