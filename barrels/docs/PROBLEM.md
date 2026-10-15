# PROBLEM.md — v1 spec: barrel color segmentation

**Version:** v1 (2026-10-14). Foundation doc — change only via a logged entry in `DECISIONS.md`. Source: Dave meeting 2026-10-07 + Tanush's scope decisions 2026-10-14.

## Task

Given one camera frame from the VEX AIM robot, decide **per pixel**: is this pixel part of a barrel, and if so, is it barrel-orange or barrel-blue? This is step 1 toward a full detector that will eventually replace the vendor "aivision" detector, whose unreliable barrel detection is a real problem robot users face right now.

## Input

- One **640×480 RGB** frame from the robot camera (PNG snapshot or live frame).

## Output

Two images, plus an optional combined debug preview:

- **Orange image:** every pixel judged *barrel orange* — an orange barrel body OR the orange stripe of a blue barrel — rendered flat **(255, 128, 0)**; every other pixel flat gray **(128, 128, 128)**.
- **Blue image:** every pixel judged *barrel blue* — a blue barrel body OR the blue stripe of an orange barrel — rendered flat **(0, 100, 255)**; every other pixel flat gray **(128, 128, 128)**.

"Barrel orange/blue" means **barrel portions only** — not just anything orange or blue in the scene.

## Method (constrained by design)

**Adaptive thresholding.** Per Dave (10/7): **do not correct or adjust the image (no white balance); adjust the thresholds per image.** The only question ever asked is "is this pixel part of a barrel?"

- **Table prior:** the bottom of the frame is mostly table (unless a barrel is very close) → known non-barrel samples → reject pixels that look like the table. "Table" means whatever surface the robot drives on. Known limit: a close-range top-only barrel fills the bottom of the frame and breaks this prior (that case is out of v1 scope, see below).
- **Background prior:** rows above the **horizon** are wall/background, never a barrel → known non-barrel samples. The horizon is the row where the ground plane projects at infinite distance (`constraints.md`, Geometry), **not the visible table edge** — a barrel near the far edge of the table rises above the edge line and appears against the wall, so the band must sit above the true horizon.
- **Region choice:** compute the bands from camera geometry: `horizon_row = 240 − f·tan(tilt)` ≈ row 70 nominally (23° tilt, f ≈ 400 — **unverified**, see `constraints.md`). Because tilt and focal length are not yet measured, the conservative background band is the top ~25 rows. The table band is the bottom rows: **default 80 rows** (nominally ground 32–43 mm from the camera), a config parameter, to be revisited once tilt and focal length are measured (`constraints.md` unknowns #2–3). Use robust statistics (median/MAD) so a barrel inside a band doesn't skew the estimate.
- **Saturation floor:** a pixel can only be barrel if `max(R,G,B) − min(R,G,B) ≥ s_min`. Black table, gray wall, and white glare are all low-saturation. This is a threshold on the pixel, not a correction of the image, so it's consistent with the no-correction rule. `s_min` is a config parameter fit on train/dev (it may also adapt per image from the table/background bands).
- **Minimum-brightness gate:** a pixel can only be barrel if its brightness (max channel, or Y) is `≥ v_min`. Color is unreliable in very dark pixels (black table, shadows). Same idea as Tekkotsu's RGBK threshold map, which gates color classes on a minimum Y. Config parameter.
- **Threshold shape, v1: an axis-aligned box in RGB.** First plot labeled barrel pixels in 3D RGB. If the cluster is compact, a box works. If it's elongated/diagonal (e.g. along brightness), a box swallows other hues → after v1, try fancier threshold functions or other color spaces (HSV, YUV, Lab). **Report how full the fitted box is** (fraction of the box volume occupied by labeled barrel pixels, plus the 3D scatter) — that is the evidence for the box-vs-diagonal question.
- **Lighting estimation is an open problem.** There is no absolute "ground truth" table color in a new setting (e.g. a lab with one overhead light), so don't rely on a stored table color. Planned **v1.5**: use the **barrels themselves as the reference** — their colors are known, so find high-confidence barrel pixels → measure how barrel orange/blue look *in this image* → re-fit the thresholds (iterative). Still adaptive thresholding; still no image correction.

## In scope (v1)

- Per-pixel orange/blue barrel segmentation on single frames, per the output spec above.
- Table + background priors; saturation floor; minimum-brightness gate; adaptive RGB-box thresholds with a box-fullness report.
- **Horizon gating:** any pixel above the horizon row is rejected as non-barrel regardless of color (`constraints.md`, Geometry). Until tilt and focal length are measured, gate at the conservative row (~25, the top of the plausible range) rather than the nominal row 70, so a wrong estimate can't erase real barrels.
- Simple scenes on a **black table** (Tanush's home, CA, ordinary home light, indirect/bounced light preferred — see `DATA.md`), no distractors. Then Pittsburgh with different tables. Goal: **table-agnostic**.
- Assumption: no deliberately adversarial objects in view (ordinary clutter is fine; nothing placed specifically to fool the detector).

## Out of scope (v1)

- Glare/specular highlights and shadowed barrel faces (eventual goal: detect them).
- Close-range top-only barrels (v2 — but think about it early; it also breaks the table prior).
- Bounding boxes; expected-size-by-row checks and other geometry beyond horizon gating.
- Per-robot calibration; a second robot.
- Learned pixel classifiers.
- White balance / any image correction (permanently out, by decision).

## Success criteria

Judged by the metrics and protocol in `EVAL.md` (per-pixel precision/recall/IoU per class, reported per condition, on a fixed held-out test set). Exact numeric targets are an open question for Dave (see `STATUS.md`).

## Milestones

1. **v1:** RGB-box thresholds + saturation floor + brightness gate + table/background rejection + horizon gating, evaluated on labeled black-table data. Includes the box-fullness report.
2. **v1.5:** barrel-referenced adaptive thresholds (iterative re-fit using high-confidence barrel pixels).
3. **Later:** other color spaces / threshold shapes; glare + shadow handling; close/top-only barrels; bounding boxes emitting the aivision spec shape (`OrangeBarrel`, `originx, originy, width, height`) so the detector can drop into `worldmap.py`.
