# PROBLEM.md — the spec

> **This file is the spec.** It says what we are building and what is out of scope; `EVAL.md` says how it is scored and `constraints.md` lists the physical facts we exploit. The three are foundation docs: they change only through a dated entry in `DECISIONS.md`. **The live spec is the v2 section below**; the v1 section is kept as the record of the frozen front end.

# v1 — barrel color segmentation (frozen 2026-10-20)

**Version:** v1 (2026-10-14; v1 frozen at config `afd85483` 2026-10-20). **v2.0 spec appended 2026-11-02** (agreed with Dave 2026-10-30; replaces the 2026-10-28 proposal). Foundation doc — change only via a logged entry in `DECISIONS.md`. Source: Dave meeting 2026-10-07 + Tanush's scope decisions 2026-10-14.

## Task

*(Record of v1. The v1 method ships unchanged as the front end of v2; the "planned v1.5" ideas below were tried on 2026-10-20 and tied, so v1 stayed as it was — `EXPERIMENTS.md`.)*

Given one camera frame from the VEX AIM robot, decide **per pixel**: is this pixel part of a barrel, and if so, is it barrel-orange or barrel-blue? This is step 1 toward a full detector that will eventually replace the vendor "aivision" detector, whose unreliable barrel detection is a real problem robot users face right now.

## Input

- One **640×480 RGB** frame from the robot camera (PNG snapshot or live frame).
- **The frame may contain no barrels at all** (Dave, 2026-10-14: the robot is often looking at other stuff). Nothing in the method may assume barrel pixels exist; on such frames both outputs are all gray.

## Output

Two images, plus an optional combined debug preview:

- **Orange image:** every pixel judged *barrel orange* — an orange barrel body OR the orange stripe of a blue barrel — rendered flat **(255, 128, 0)**; every other pixel flat gray **(128, 128, 128)**.
- **Blue image:** every pixel judged *barrel blue* — a blue barrel body OR the blue stripe of an orange barrel — rendered flat **(0, 100, 255)**; every other pixel flat gray **(128, 128, 128)**.

"Barrel orange/blue" means **barrel portions only** — not just anything orange or blue in the scene.

## Method (constrained by design)

**Adaptive thresholding.** Per Dave (10/7): **do not correct or adjust the image (no white balance); adjust the thresholds per image.** The only question ever asked is "is this pixel part of a barrel?"

- **Table prior:** the bottom of the frame is mostly table (unless a barrel is very close) → known non-barrel samples → reject pixels that look like the table. "Table" means whatever surface the robot drives on. Known limit: a close-range top-only barrel fills the bottom of the frame and breaks this prior (that case is out of v1 scope, see below).
- **Background prior:** rows above the **horizon** are wall/background, never a barrel → known non-barrel samples. The horizon is the row where the ground plane projects at infinite distance (`constraints.md`, Geometry), **not the visible table edge** — a barrel near the far edge of the table rises above the edge line and appears against the wall, so the band must sit above the true horizon.
- **Region choice:** compute the bands from camera geometry: `horizon_row = 240 − f·tan(tilt)`, measured at rows 55–100 for AIM-4A8B6118 (2026-10-19; `constraints.md`). Background band: **rows 0–50**. Table band: the bottom rows, **default 80 rows** (ground ≈ 32–43 mm from the camera), a config parameter. Use robust statistics (median/MAD) so a barrel inside a band doesn't skew the estimate.
- **Saturation floor:** a pixel can only be barrel if `max(R,G,B) − min(R,G,B) ≥ s_min`. Black table, gray wall, and white glare are all low-saturation. This is a threshold on the pixel, not a correction of the image, so it's consistent with the no-correction rule. **`s_min` is derived per image** (decided 2026-10-20): the 99.5th percentile of the saturation of the rows above the horizon plus a margin of 10, clamped to [20, 120] — the image's own guaranteed-non-barrel rows say how colorful the background is. A fixed value (50 on the v1 table) remains available as a config option.
- **Minimum-brightness gate:** a pixel can only be barrel if its brightness (max channel, or Y) is `≥ v_min`. Color is unreliable in very dark pixels (black table, shadows). Same idea as Tekkotsu's RGBK threshold map, which gates color classes on a minimum Y. Config parameter.
- **Threshold shape, v1: an axis-aligned box in RGB.** First plot labeled barrel pixels in 3D RGB. If the cluster is compact, a box works. If it's elongated/diagonal (e.g. along brightness), a box swallows other hues → after v1, try fancier threshold functions or other color spaces (HSV, YUV, Lab). **Report how full the fitted box is** (fraction of the box volume occupied by labeled barrel pixels, plus the 3D scatter) — that is the evidence for the box-vs-diagonal question.
- **Lighting estimation is an open problem.** There is no absolute "ground truth" table color in a new setting (e.g. a lab with one overhead light), so don't rely on a stored table color. Planned **v1.5**: use the **barrels themselves as the reference** — their colors are known, so find high-confidence barrel pixels → measure how barrel orange/blue look *in this image* → re-fit the thresholds (iterative). Still adaptive thresholding; still no image correction. **Must degrade gracefully when no high-confidence barrel pixels are found** (no barrels in view): fall back to the v1 thresholds rather than re-fitting on noise.

## In scope (v1)

- Per-pixel orange/blue barrel segmentation on single frames, per the output spec above.
- Table + background priors; saturation floor; minimum-brightness gate; adaptive RGB-box thresholds with a box-fullness report.
- **Horizon gating** (Dave OK'd for v1, 2026-10-14; he expects little practical effect): any pixel above the horizon row is rejected as non-barrel regardless of color (`constraints.md`, Geometry). Config flag. For AIM-4A8B6118 gate at **row 50** (below every measured fit of the horizon, 55–100); for an unmeasured robot fall back to row 25.
- Simple scenes on a **light-colored matte table under white overhead light** (CMU campus), no distractors — the v1 base set. A **black table under warm yellow overhead light** (Tanush's home, CA) is shot alongside as the first stress condition. Then more Pittsburgh tables. Goal: **table-agnostic**. Capture details: `DATA.md`.
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

1. **v1:** RGB-box thresholds + saturation floor + brightness gate + table/background rejection + horizon gating, evaluated on the labeled light-table set (and reported on the warm black-table stress set). Includes the box-fullness report.
2. **v1.5:** barrel-referenced adaptive thresholds (iterative re-fit using high-confidence barrel pixels).
3. **Later:** other color spaces / threshold shapes; glare + shadow handling; close/top-only barrels; bounding boxes emitting the aivision spec shape (`OrangeBarrel`, `originx, originy, width, height`) so the detector can drop into `worldmap.py`.

---

# v2 — barrel detection: draw the boxes

**Version:** v2.0 spec (Dave meeting 2026-10-30, relayed by Tanush; details settled with Tanush 2026-11-02; `DECISIONS.md` 2026-11-02; one-table data 2026-11-03). Replaces the 2026-10-28 proposal. Foundation doc — change only via a logged decision.

## Task

Take one 640×480 camera image and give back the same image with **one box drawn around every barrel**, in the barrel's color. That is the whole deliverable: a still image in, a still image with boxes out, running on the laptop. Everything downstream of the boxes (the world map, the planners) is assumed correct and is **not touched** in v2.

The boxes are what will later feed the robot's world map, which relies on the **bottom edge** of each box. So the bottom edge is the edge that has to be right.

## Input

- One 640×480 RGB frame (snapshot or live frame), as in v1.
- The frame **may contain no barrels**. It may contain **clutter**, including other orange or blue objects; those must not get boxes.
- Any table that is not wood, under whatever light is there (Dave 2026-10-24: don't bother with wood). **v2.0 is built and tested on one table and one background** with varied arrangements, positions and clutter (Tanush 2026-11-03, timeline); more tables are the v2.1 generalisation step.
- Barrels are **upright** (a knocked-over barrel is a question for Dave). Any number of barrels in any arrangement: alone, touching (same or mixed colors), one behind another, cut by the frame edges, partly hidden by clutter, held in the robot's kicker.

## Output

A list of barrels; for each: **color** (orange | blue) and **box** `[x0, y0, x1, y1]` in image pixels. The box is the **full barrel** — lid top to the base's contact with the table, bulge to bulge — drawn **as if whatever hides part of the barrel were transparent**, then **clipped to the frame**. A barrel whose bottom is below the frame therefore gets a box that ends at the frame edge; a barrel that fits in the frame gets its whole box.

Drawn output: the image with each box as a thin (1 px) rectangle in a color that says the class but stands out from the barrels — yellow for an orange barrel, green for a blue one, Dave's convention from his ground-truth images (Tanush 2026-11-03). Nothing else is drawn.

Kept with each box internally but **not shown**: the inferred distance, which edges were seen vs inferred, a confidence. They are there for the world map later (`detect_types.Barrel`).

## Method (constrained by design)

- **Start from the v1 segmentation** (`afd85483`). Its per-image parts (saturation floor, wall model) stay adaptive at run time. Its fixed part — the two per-class RGB boxes — may be **re-fit once on training frames** (same method, new numbers, logged as an experiment; with v2.0's single table this is expected to stay unused). Nothing is fit per image or per table when an image is shown: the program must work on a frame from a table it has never seen.
- **The stripe is the barrel anchor.** Color says "orange thing"; the stripe says "barrel". The stripe is a ring at mid-height, so it is visible from any side whenever the barrel's middle is visible. Find stripes first — a band of one color sandwiched by the other, at the height the geometry expects for that row — and each stripe gives one barrel, its color (the body color) and its distance.
- **One good measurement plus the known shape gives the whole box.** Measure any one feature reliably — the top edge row, the stripe rows, the width — and the fixed camera (`geometry.py`) gives the distance, and from the distance every other edge. This is how the bottom edge is drawn when it cannot be seen: below the frame, in shadow, behind another barrel, behind clutter. All four cases are in scope.
- **Bottom-edge precedence:** the seen bottom when it is trustworthy (it agrees with the size the geometry predicts); otherwise inferred from the top edge, then from the stripe, then from the width. Which edges were inferred is recorded.
- **Stripeless candidates** (a very close barrel with its stripe below the frame; a hidden middle; a blue stripe lost in shadow) must pass a **size-and-shape check** for their row — a barrel at that row is about this wide and this tall — or they are dropped. A stripeless orange object of about barrel size can fool this; accepted for v2.0 and measured by the eval.
- **Merged blobs:** when a barrel stands in front of or beside something of its own color, its box is carved out of the merged blob around its stripe at the expected size; the leftover pixels are judged on their own.
- **Known-distance frames calibrate the geometry.** A dozen frames with one barrel at a measured distance from the bumper (from touching to the far end of the table) fit the focal length and tilt for this robot and check the formula where it is weakest, up close. This is Dave's "lookup table", built as a calibration so it is computable for any robot by shooting the same frames (Dave 2026-10-30: focal length should not differ much between robots).
- **No image correction** (standing rule). **Nothing from the world map** — no ground positions as an output, no aivision spec — until Dave says so. The detector is one function, image in → barrels out, so wiring it in later or swapping the method is trivial.

## In scope (v2.0)

Everything above; all four hidden-bottom cases; a held barrel is detected like any other (Tanush: it sits barely off the ground); occluded barrels are reported with their inferred full box; zero boxes on frames without barrels, including frames with orange/blue clutter.

## Out of scope (v2.0)

Ground positions, the world map, the aivision spec; knocked-over barrels; wood tables; temporal tracking that feeds anything downstream (a display-only persistence of boxes over frames in the live view, `BarrelTracker`, is allowed since 2026-11-06, `DECISIONS.md`: it changes what is shown, never the per-image answer this spec and `EVAL.md` score); learned detectors; confidence shown to the user; per-pixel polish beyond the one re-fit — if the segmentation turns out to be the bottleneck, fixing it becomes v2.1 (Dave 2026-10-30: only if its flaws actually cost detections) — **it is: on Dave's frames it costs every detection, so the redesign was pulled into v2.0 on 2026-11-03.** A **display-only live view** of the boxes on the robot's own camera is *in* scope since 2026-11-03 (Dave; `DECISIONS.md`): it draws on the image and touches nothing downstream. Wiring into the world map stays out.

## Success criteria

"It works" = the held-out images come back with every barrel boxed correctly and nothing else boxed. The number for that is the v2 rule in `EVAL.md`: a box is correct when it overlaps the true box by at least half **and** its bottom edge is within a tenth of the barrel's image height (at least 3 px); the primary score is the mean over colors of F1 under that rule, reported per arrangement and on the held-out frames (per table × light and on an unseen table once there is more than one table, v2.1). Floor to beat: the connected-components baseline re-scored under the same rule.

## Milestones

1. **v2.0** (this spec), in the order of `TODO.md`: ~~box labels + tool~~, ~~the eval rule~~, ~~the stripe-anchored detector~~ (all 2026-11-03), ~~the live view on the robot~~ (2026-11-05; first run and the multi-frame variant 2026-11-06), the segmentation redesign, one-table data + calibration frames, the geometry calibration, hidden-stripe barrels, one test run, results to Dave.
2. **v2.1 — generalise:** more tables (white / beige / black), an unseen-table hold-out, the one segmentation re-fit if a table needs it, and fixing the segmentation where it is the bottleneck.
3. **Later, when Dave says:** ground positions from the stored distances; wiring into the robot — the bridge stub and the aivision spec shape already exist (`worldmap_bridge.py`).
