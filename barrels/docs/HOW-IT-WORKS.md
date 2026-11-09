# HOW-IT-WORKS.md — the main code, in plain English

Written for Tanush, so he can explain the detector to Dave without help. One section per **main** module: color segmentation, camera geometry, the detector, the detection eval, plus the live feed. Side tools (labelers, importers) are not covered — they are allowed to be black boxes. The one-page version is `HOW-IT-WORKS-SHORT.md`; the file-level diagrams are `ARCHITECTURE.md`. Naming: what the lab notebook calls "detector step 2" (the stripe) is **step 4** of section 3 here. Rule since 2026-11-02 (`DECISIONS.md`): every commit that changes main code updates its section here and gets a walkthrough in chat first.

Every number in this file is a real number from the code or from a real frame, so you can check it: `4A8B_window_light_touch_02` (three touching barrels, orange–blue–orange, about 18 cm away) is the worked example throughout.

## 0. The whole thing in one paragraph

A photo comes in (640 × 480). **Section 1** looks at every pixel and says "barrel orange", "barrel blue" or "other", producing a *class mask* — an image the same size holding 0, 1 or 2 per pixel. **Section 3** takes that mask, groups the barrel pixels into blobs, works out how many barrels each blob is and where each barrel's edges are, using the camera geometry from **section 2** whenever an edge cannot be seen. Out comes a list of barrels, each with a color and a box, and the photo is written back with the boxes drawn on it. **Section 4** is how we score that against hand-drawn truth. The one command that does 1 → 3:

```
python barrels/tools/detect_image.py barrels/data/raw/4A8B_window_light_touch_02.png
```

Nothing in this chain learns anything from the photo it is looking at. The only "learned" numbers are two color boxes in section 1, fit once from labeled frames; everything else is either computed fresh from the image (the saturation floor, the wall model) or is physics (barrel size, camera height, tilt).

## 1. Color segmentation — `src/barrels/pipeline.py` (v1, frozen at config `afd85483`)

**What it does.** Takes one image and labels every pixel as barrel-orange (1), barrel-blue (2), or other (0). This is the front end of everything after it; the detector works on these pixel labels, not on the raw image. (A fourth value, 255 = "ignore", exists only in hand-painted label masks for glare we did not want to score.)

**The idea.** A pixel has to survive a chain of cheap tests to be called barrel. Each test throws out pixels that *cannot* be barrel; the last test decides which color the survivors are.

1. **Horizon gate.** Nothing above row 50 can be a barrel. The camera is 43 mm above the table and a barrel is 24 mm tall, so every barrel standing on the table appears below the horizon line, which for our robot is around row 76 (section 2). Row 50 is a safe margin above that. Those top rows are therefore *guaranteed background*, which the next two tests exploit.
2. **Saturation floor.** Barrels are vivid; tables, walls and glare are grayish. "Saturation" here is simply max(R, G, B) − min(R, G, B), a number from 0 to 255. The floor is not a fixed number: the program takes rows 0–50 (guaranteed background), finds the 99.5th percentile of their saturation (i.e. "how colorful is the most colorful 0.5 % of the background"), adds a margin of 10, and clamps the result to between 20 and 120. Any pixel below that floor is out. On `touch_02` the floor comes out at 48; on `core_01`, 55. A warm-lit room with a yellowish wall gets a higher floor by itself, with nothing changed in the code. This is what "adaptive thresholds, no image correction" means in practice.
3. **Wall model.** From the same background rows, a robust estimate (median and spread, per channel) of the background color, fit on the low-saturation background pixels; any pixel within 2.5 spreads of that color is rejected. Also per image. This catches bluish or warm walls that pass the floor.
4. **Brightness gate.** Any pixel whose brightest channel is below 40 is out: in near-black pixels the color is noise. This changes nothing on a light table; it exists for dark ones.
5. **Color boxes — the only learned part.** For each class, a box in RGB space: the 1st-to-99th percentile range of hand-labeled barrel pixels that survived the gates above, fit once on the 16 training frames. The frozen numbers are orange = R 74–211, G 14–121, B 4–104 and blue = R 0–127, G 11–110, B 36–185. A surviving pixel inside the orange box is orange, inside the blue box is blue; if it is inside both, the redder one (R > B) is orange. Outside both, it is other.

A "table model" built from the bottom rows, mirroring the wall model, exists as a switch but is **off**: a close barrel's shadow sits in those rows and fools it.

**Worked example.** Take a pixel on the shaded lower face of the blue barrel in `touch_02`, say RGB (30, 45, 110). Row ≈ 160, below 50: passes the horizon gate. Saturation 110 − 30 = 80 ≥ 48: passes the floor. Nothing like the gray-blue wall (the wall median is around (120, 125, 135) with a spread of a few units): passes the wall model. Brightest channel 110 ≥ 40: passes. Inside the blue box (R 0–127, G 11–110, B 36–185) and outside the orange box (B 110 > 104): **blue**. Now a slightly darker pixel on the same face, (25, 30, 60): saturation 35 < 48 — thrown out by the floor. That is the main v1 miss, and it is why the detector (section 3) must be able to fill in a bottom edge the mask does not show.

**Why the boxes alone don't work.** Barrel pixels in RGB form a long smear along the brightness axis (bright lit face, dark shaded face), so a box wide enough to include the shadowed faces also includes a lot of table and wall. The floor and the wall model do the separating; the boxes only decide orange vs blue among the survivors.

**Where it lives.** `Config` (every knob; defaults = the frozen v1 config; `horizon_row=50, s_min_mode="band", s_band_q=99.5, s_band_margin=10, s_min_lo=20, s_min_hi=120, v_min=40, bg_prior=True, k_bg=2.5, table_prior=False, box_space="rgb", box_pct=(1, 99), tie="rb_sign"`). `Frame.from_image(bgr)` (the image plus its saturation and brightness planes). `effective_s_min(frame, cfg)` (the per-image floor). `fit(frames, masks, cfg)` → `Model` (learns the two boxes; done once, saved in `results/2026-10-20_v1_test_adaptive/config.json`). `segment(frame, model)` → the mask + an info dict (`s_min_eff` is the floor it used).

**How to run it.** `python barrels/tools/segment_image.py image.png` writes the orange, blue, class-mask and overlay images to `results/segment_image/`.

**What can go wrong.** Shadowed lower faces of blue barrels fall below the saturation floor (the main miss; `far_02`'s middle orange barrel loses its lower face the same way). Skin lands inside the orange box — hands are orange to this program. Under a strong color cast the fixed RGB boxes can miss while the floor and wall model adapt; v2 allows one re-fit of the boxes on more frames if that happens.

**Numbers.** Held-out test: orange IoU 0.84, blue 0.81, zero false pixels on the empty frame (`EXPERIMENTS.md` 2026-10-20). (IoU for pixels = correct barrel pixels ÷ (correct + missed + falsely added).)

### The "hs" color model — the redesign candidate (2026-11-08, branch `wip/redesign`, not yet the default)

**Why.** On the campus frames (2026-11-07) tests 2 and 3 above removed the barrels themselves: with a dark, cluttered room in rows 0–50 the floor came out at 67–120 and the wall model's spread at 35–52 per channel, so navy-blue bodies (saturation 52–84) and shaded orange faces were rejected as "background" — blue bodies 0–7 % labeled in nine frames (`EXPERIMENTS.md` 2026-11-07, attribution). Every adaptive part assumed the top rows are a plain wall and the barrels the only colorful thing in the picture.

**The idea.** Describe a barrel color by two numbers that do not change with brightness, and read both off the labeled frames once:

- **Hue** (the position on the color circle, OpenCV units 0–179): orange barrels sit at about 5–12, blue ones at 104–118, in the home frames and on campus alike. Hue is computed from the ratios of R, G and B, so a lit face and a shaded face of the same barrel have the same hue. Orange sits next to the wrap at 0/180, so its hue is rotated by +30 before taking percentiles (a sector 3–13 would otherwise read as "3 to 168").
- **HSV saturation**, S = (max − min) / max, 0–255: how far from gray a color is *relative to its brightness*. A navy-blue shaded face (RGB 12, 45, 85) has S = 219 even though v1's max − min is only 73; a bluish-gray wall (160, 150, 140 or so) stays under 110. This is the number that separates a dark barrel from a gray wall, which v1's max − min could not.

Per class: the S floor = the `hs_s_pct` percentile of the labeled pixels' S; the hue sector = the `hs_h_pct` percentiles of the labeled pixels above that floor, widened by `hs_h_margin` on each side. Then a pixel is that class when it is below row 50, brighter than 40, inside the sector and above the floor; in both → the redder one is orange (the same tie rule). **No per-image floor, no wall model, no table model**: nothing is estimated from the image being segmented.

**Worked numbers** (fit on the 16 home train frames, `hs_s_pct=15, hs_h_pct=(5, 95), hs_h_margin=4`, config `…`, the sweep's runner-up): orange hue 1–14, S ≥ 174; blue hue 101–121, S ≥ 113. The campus `room_01` blue body (RGB ≈ 12, 45, 85; hue 108, S 219) passes; the home wall in the blue hue sector (S ≤ 110) does not; skin on the campus hand (hue 13, S 149) fails the orange floor; the orange glue-stick cap (hue 9, S 222) passes — and is then refused by the detector because nothing sandwiches a band in it.

**Where it lives.** `Config(color_model="hs", hs_s_pct, hs_h_pct, hs_h_margin)`; `Frame.hs(shift)` (the hue/saturation planes, cached per shift); `fit_hs` (called by `fit`); the `"hs"` branch at the top of `segment`. The fields are omitted from the config hash at their defaults, so every v1 hash (`afd85483` included) is unchanged. `pipeline.HUE_SHIFT` = {orange: 30, blue: 0}.

**What the sweep said** (`EXPERIMENTS.md` 2026-11-08, `experiments/2026-11-08_seg_hs/`; home = leave-one-scene-out, campus = count-level): the S floor is the whole game for blue at home — at the 5th percentile (S ≥ 64) the wall produces false blue boxes on the positive frames (blue F1 0.48), at the 15th (S ≥ 113) it is gone (0.96) with the campus barrels still found; orange needs hue slack toward yellow (the campus barrels in daylight read hue 7–13 against 5–10 at home), so a margin of 2–4 units. Not adopted yet: the pre-registered selection rule chose the 5th-percentile floor by the campus count and ignored the home score, which is a flaw in the rule, not the data; the decision waits for Tanush's box labels on the campus frames and the walkthrough.

**What can go wrong.** Hue is noise where S is low, so dark low-saturation pixels are excluded by the floor rather than by hue; the orange sector (1–14) touches skin and wood hue — the S floor (≥ 174) is what keeps skin out, and wood tables are out of scope; a bright blue object in the room (a jacket, a chair) is labeled blue, and only the detector's stripe and size checks keep it from becoming a barrel.

## 2. Camera geometry — `src/barrels/geometry.py` (v1.5)

**What it does.** Converts between image rows and real-world distances for this robot's camera, and says how big a barrel should look at any place in the image.

**The idea.** The camera is a pinhole at a known height above the table (h = 43.47 mm), tilted down by an angle θ, with a focal length f that says how many pixels one radian of view is (≈ 400 px). A point on the table at horizontal distance d in front of the camera is seen at an angle atan(h / d) below horizontal; subtract the tilt, and the row it lands on is

    row = 240 + f · tan( atan(h / d) − θ )

(240 is the image center row.) Run it backwards and a row gives a distance:

    d = h / tan( atan((row − 240) / f) + θ )

A point that is not on the table but at height z (the top of a barrel) uses h − z instead of h. Two consequences worth holding in your head: rows near the horizon are very far away and a one-row change there is many millimetres, while rows near the bottom of the frame are close and a row is a fraction of a millimetre; and the **horizon row** — where a point infinitely far away lands — is 240 − f · tan θ, which for our numbers is **row 76**. Nothing on the table can appear above it.

**The barrel.** 24 mm tall, 25.5 mm across at the bulge, 18 mm across at the ends, stripe 6 mm tall centred at mid-height. The box's top is the *far* edge of the lid (9 mm beyond the barrel's axis), its bottom is the *near* edge of the base (9 mm in front of the axis), so top and bottom are at slightly different distances. `barrel_rows(d_axis)` applies all of that and returns the top row, the stripe's rows, the bottom row and the width in pixels for a barrel whose axis is d_axis away. With the current camera:

| barrel axis distance | top row | stripe rows | bottom row | width px | height px |
|---|---|---|---|---|---|
| 50 mm | 212 | 348–390 | 422 | 204 | 210 |
| 100 mm | 154 | 211–235 | 263 | 102 | 109 |
| 150 mm | 131 | 166–183 | 204 | 68 | 73 |
| 200 mm | 118 | 143–156 | 174 | 51 | 55 |
| 300 mm | 105 | 121–130 | 142 | 34 | 37 |
| 400 mm | 98 | 110–116 | 126 | 26 | 28 |

So a barrel at 20 cm is about 51 px wide and 55 px tall with its bottom at row 174; seeing *any one* of those — the top row, the stripe, the width, the bottom — tells you the distance, and from the distance every other number in that row of the table. That is the whole trick the detector uses. The inverses are `bottom_row_from_top_row`, `bottom_row_from_stripe_row`, `bottom_row_from_width`, `expected_barrel_width_px(bottom_row=…)`, `expected_barrel_height_px(bottom_row=…)`.

**Worked example.** In `touch_02` the left orange barrel's top row is 122. Backwards through the formula with z = 24 mm: the lid's far edge is 191 mm from the camera, so the axis is 182 mm away, so the base's near edge is 173 mm away, which lands on row 182.6. The segmentation saw the bottom at row 175: 7.6 px higher than predicted, which is within what we expect from the camera numbers (next paragraph), so the seen bottom is believed.

**Where it lives.** `CameraModel(f, tilt_deg, height_mm)` with `horizon_row()`, `row_to_ground_distance(row)`, `point_row(d, z)`, `barrel_rows(d_axis)`, the inverses above, and `image_to_ground(u, v)` (reproduces the robot's own ground projection; kept for the world map later, not used in v2). Presets: `AIM_4A8B6118_BOXFIT` (the current default, f 400 / tilt 22.25°), `AIM_4A8B6118` (the October measurement, f 404 / tilt 23.3°), `NOMINAL` (Dave's 23° / 400), and the honest range `AIM_4A8B6118_RANGE`.

**How to run it.** `python -m barrels.geometry --tilt 22.25 --f 400` prints the table in `constraints.md` for any camera numbers.

**What can go wrong.** The tilt and focal length are only known to a few percent, and close to the robot small tilt errors move rows a lot (at 5 cm, 1° of tilt is ≈ 7 px). The known-distance `calib` frames (the calibration session, `TODO.md` P1) will measure both properly.

**Update 2026-11-03 — the preset was off.** On the labeled frames the October camera (f 404, tilt 23.3°, horizon row 66) put every predicted bottom edge about 20 px too low: the top row said "this barrel is closer than it is". Re-fitting the tilt from 24 labeled, fully visible barrels on the train frames (f held at 400, the known barrel height and width as the ruler) gives tilt 22.25°, horizon row 76 — inside the band measured in October. With it, predicted bottoms land within about 5 px of the truth. That is the provisional preset `AIM_4A8B6118_BOXFIT`, now the detector's default, until the known-distance `calib` session measures it properly. Note what the boxes actually pin down: the horizon row, not f and tilt separately (they trade off along a ridge: f 356 with tilt 24.75° fits exactly as well as f 400 with 22.25°). `experiments/2026-11-03_geo_boxfit/`, `EXPERIMENTS.md` 2026-11-03.

**Numbers to remember.** Horizon row ≈ 76. A barrel at 20 cm is ≈ 51 px wide. The bottom edge leaves the frame when the barrel's base is within ≈ 28 mm of the bumper; in that zone the top edge moves ≈ 13 px per mm.

## 3. The detector — `src/barrels/detector.py` (v2; steps 1–3 built 2026-11-03, the stripe step the default since 2026-11-05, hardened 2026-11-08 on branch `wip/redesign`)

**What it does.** Takes the class mask from section 1 and returns a list of barrels. Each barrel is a `Barrel` record (`detect_types.py`): `color` (orange or blue), `bbox` = `(x0, y0, x1, y1)` in pixels, half-open (x1 and y1 are one past the last pixel), `confidence` (0–1), `flags` (`bottom_inferred` / `top_inferred` when that edge was computed rather than seen; `occluded` when the stripe was partly hidden and the full box drawn anyway; `truncated` when the box reaches a frame edge), `area` (how many mask pixels it came from) and `source` (`"det2"` for a barrel found from its stripe, `"det1"` for a stripeless piece). `detect(mask, cfg, cam)` is the one entry point: mask in, barrels out, same signature as the dumb reference `detect_cc.detect`, so either can be plugged into `detect_image.py` or the experiment scripts. `draw(image, barrels)` paints a 1-px rectangle per barrel — yellow for an orange barrel, green for a blue one, so the lines stand out from the barrels — and nothing else: the v2 deliverable image.

Nothing is remembered between images and nothing is fit per image. The numbers in `DetConfig` (table below) were written down before the first run and have not been tuned.

### Step 1 — blobs (`find_blobs`)

Take every pixel that is orange *or* blue (both at once, so a barrel's body and its stripe land in the same blob). Run a 3 × 3 *morphological close* over it — "fill any hole or gap up to 3 px wide" — so a shaded, speckled face does not break a barrel into two or three bits. Then find the 8-connected components (groups of touching barrel pixels; diagonal touching counts). Throw away components under 20 px (specks). For each surviving blob, record its bounding box and how many of its pixels were orange and how many blue.

*`touch_02`:* the mask has 3409 orange and 2337 blue pixels. They form **two** blobs: one at x 149–237, y 122–178 (88 px wide, 56 tall, 1763 orange / 1884 blue — this is the orange *and* blue barrel merged, because the orange barrel's blue stripe touches the blue barrel's body, exactly the case Dave's notes call "color adjacency"), and one at x 240–288, y 122–175 (48 wide, 1646 orange / 453 blue — the right orange barrel on its own; the 453 blue are its stripe).

### Step 2 — how many barrels is this blob? (`expected_width_px`, `split_blob`)

Section 2 says how wide one barrel is at the blob's distance. Which distance? If the blob's bottom is inside the frame, its bottom row gives the distance (the base sits on the table, and the bottom row of a thing on the table is the most reliable distance cue). If the blob touches the frame's bottom edge, the real bottom is somewhere below the frame and the row is meaningless, so the top row is used instead (`expected_width_px` makes that choice).

Divide the blob's width by that expected width and round to the nearest whole number: that is how many barrels stand side by side in the blob. One → done. Two or more → cut the blob into that many pieces. Where to cut: not at the exact halfway point but at the *narrowest column* near it — barrels bulge in the middle, so two touching barrels have a waist where they meet, and the column with the fewest barrel pixels in a window of ± a quarter barrel-width around the equal-spacing point is that waist (if several columns tie, the one nearest the equal-spacing point wins). Each piece gets its own tight box around its own pixels and its own orange/blue counts, and its **color is whichever count is larger** — that is the body color, because the stripe is always the minority of a barrel's pixels.

*`touch_02`, first blob:* bottom row 178 → the expected barrel width at that row is 53.4 px. 88 ÷ 53.4 = 1.65 → rounds to **2** barrels. The narrowest column near x = 193 is found and the blob is cut there: piece A, x 149–193, 1301 orange / 335 blue → **orange**; piece B, x 193–237, 462 orange / 1549 blue → **blue**. Second blob: 48 ÷ 51.8 = 0.93 → **1** barrel, 1646 orange / 453 blue → orange. Three barrels, correct colors, at this point without the geometry having drawn a single edge.

### Step 3 — the bottom edge (`predicted_bottom`, `resolve_bottom`)

This is the step that exists because the bottom edge is the one the world map will use and the one most often hidden (shadow, another barrel, clutter, the frame edge). The top row of a piece says how far away the barrel is — a 24 mm-tall thing whose top appears at that row can only be at one distance — and from the distance, section 2 says where its base must be: that is `predicted_bottom(cam, top_row)`. Then `resolve_bottom` compares the predicted bottom with the bottom the mask shows:

- If they agree to within a tolerance — 15 % of the predicted box height, but never less than 4 px — the seen bottom is kept (it was seen; the geometry is only a check).
- If they disagree, the mask's bottom is wrong for one of the known reasons (a shadowed face made the blob too short, a reflection below the barrel made it too tall, an occluder hides the base) and the **predicted bottom replaces it**, with the flag `bottom_inferred`.
- Exception: when both the seen bottom and the predicted one are at or below the frame edge, the box is simply cut at the frame (no inference needed, nothing visible to infer from).
- Finally the bottom is clipped to the frame and any box touching a frame edge gets `truncated`.

*`touch_02`, piece A:* top row 122 → axis 182 mm away → predicted bottom 182.6. Seen bottom 175. Tolerance = max(4, 0.15 × (182.6 − 122)) = 9.1 px; the difference is 7.6 → **seen bottom kept**, no flag. Same for the other two (differences 9.5 and 7.6 against tolerances 9.5 and 9.1).

*`far_02`, the middle orange barrel:* top row 106 → 290 mm → predicted bottom 144.4; the mask's bottom is 136 because the shaded lower face fell below the saturation floor; tolerance 5.8; difference 8.4 → **bottom replaced by 144**, flagged `bottom_inferred`. The hand-labeled truth has the bottom at 137, so here the inference overshot by 7 px: at 30 cm the camera numbers are good to about 5 px and the tolerance is only 6, so the geometry can "correct" a bottom that was in fact right. That is a known weakness of step 1 at far range (see "What can go wrong").

### Shape checks — is this piece barrel-shaped for its row?

After the bottom is settled, the expected width at that bottom row is computed once more and the piece must satisfy all of:

- expected width ≥ 16 px, i.e. the barrel is nearer than about 60 cm (anything "smaller" would be off the far end of a table — or above the horizon, where the expected width is infinite or zero);
- piece width between 0.4 × and 1.6 × the expected width (narrower is a sliver — a stripe fragment, a reflection edge; wider is not one barrel).

*`far_02`:* the hand resting on the table edge produces orange specks around rows 60–85, near the horizon. Expected width there is 1.8–4.4 px → **all dropped** by the 16 px rule. That is how the hand's fingers disappear without any "skin detector".

### Step 4 — the stripe is the barrel (`find_stripes`, `barrel_from_stripe`; built 2026-11-03, the default since 2026-11-05)

Steps 1–3 box anything barrel-colored and barrel-sized. Step 4 adds the one thing that proves "barrel": the **stripe**, a band of the other color around the middle. With it, every stripe is one barrel, wherever the blob boundaries happen to fall, so touching and partly hidden barrels separate by themselves, and an orange thing without a stripe is not a barrel.

*Finding stripes.* Take the orange pixels as "body" (then repeat with blue). For every column, note where body pixels exist above and below. A **band** is a connected region of non-body pixels that has body above it *and* below it in every one of its columns — that is the sandwich. The band's pixels are either blue (a proper stripe) or unlabeled (a stripe the segmentation lost to shadow): either counts, and the ratio sets the confidence. The band must have stripe proportions for its row: the height of its colored core (10th-to-90th percentile of its blue rows) between 0.45 and 1.6 × the stripe height the geometry expects there, the whole band (core plus shadow) at most 3 ×, and the band at least 0.4 barrel-widths wide and not taller than wide. A band wider than 1.4 barrels is the merged stripes of touching same-color barrels (their stripes meet at the bulges) and is cut into equal parts.

*A barrel from its stripe.* The stripe's middle row (the median row of its colored pixels) gives the distance; the distance gives the full box the geometry predicts: top, bottom and width (section 2's table). Then the seen body extent in the stripe's own columns — walked upward from the band and downward from it while body pixels keep coming, gaps of 3 rows allowed — supplies the top and bottom when they agree with the prediction within the same 15 % tolerance as step 3; otherwise the predicted edge is drawn and flagged (`top_inferred`, `bottom_inferred`). A stripe narrower than 0.8 barrel-widths is partly hidden: the box is widened to a full barrel, on the side where something barrel-colored borders the stripe (the occluder), and flagged `occluded`. Clip, `truncated` as before.

*Stripeless pieces.* The step-1 pieces are then only kept where no stripe barrel already covers them **and** a stripe could not have been seen: the piece reaches the frame bottom (a close barrel, stripe below the frame — `topstripe_01`, `top_01`) or the expected stripe at that distance is thinner than 4 px. Everything else without a stripe is dropped — the hand, a tomato, a reflection.

*`touch_02`:* three bands found — blue between orange at x 152–191, orange between blue at 189–235, blue between orange at 241–288 — three barrels, no width rule needed. *`cluster_01`:* three of the four bunched barrels have a visible stripe and come out right; the fourth, directly behind another of the same color, shows no stripe and is missed (and the width rule, no longer trusted alone, is not allowed to guess it). That is the honest limit: **a barrel whose stripe is completely hidden is not found.**

*Status.* The default since 2026-11-05 (`DetConfig.require_stripe=True`): it beat steps 1–3 on the train frames under both rules (below). `detect_image.py --step1` runs steps 1–3 alone for comparison.

### The hardening (2026-11-08, branch `wip/redesign`, awaiting walkthrough)

The campus attribution (`EXPERIMENTS.md` 2026-11-07) confirmed the two flaws pre-registered after the first live run and found a third; a fourth showed up under the new color model. Each is a `DetConfig` field, so the 2026-11-05 behaviour stays reproducible (`stripe_mode="bands"`, `body_min=0`, `height_max=0`).

- **(a) A dark gap is not a stripe** (`dark_stripe=False`). The 2026-11-03 finder accepted a band with *no* stripe-colored pixel as a "shadowed stripe". On the laptop-lid scene that made a floating box out of the dark gap under a false orange smear; under the hue model it made boxes out of gaps in the patchily labeled home wall. Off by default; `dark_stripe=True` restores it.
- **(b) The stripe is measured from its own pixels** (`stripe_mode="cores"`). The old band was *everything that is not body color* between body above and below, so unlabeled shadow glued to a stripe made its band taller than 3 × the expected stripe height and the stripe was dropped (campus `core_01`, `plain_01`, `close_01`, `window_01`). Now a stripe is a connected component of the *other* color whose every pixel has body color within 3 stripe heights above **and** below it (the sandwich, pixel by pixel — so a stripe touching a neighbouring barrel's body is cut from that body), with the same proportions checks as before on the component itself: height 0.45–1.6 × the expected stripe height, at least 0.4 barrels wide, not taller than wide; wider than 1.4 barrels → cut evenly as before. Shadow around the stripe changes nothing because it is never part of the component.
- **(c) A box must hold body color** (`body_min=0.1`). In the stripe's own columns, outside the stripe rows, the box must contain more body-colored than stripe-colored pixels, and at least 10 % body color. `core_01`'s pair: the blue barrel's body, lying between its own orange stripe below and the orange neighbour's bulge above, had been boxed as an orange barrel.
- **(d) A stripeless piece must be barrel-tall** (`height_min=0.5, height_max=1.5`). Step 3's shape checks looked at width only; a blue jacket above the table edge in `core_01`, 24 px wide and 45 tall with its bottom just under the horizon, passed as a "far barrel whose stripe is too thin to see". Now the piece's height must also be 0.5–1.5 × the barrel height the geometry expects at its bottom row (skipped for pieces cut by the frame edge).

- **(f) The box is as wide as the body, not the stripe** (`body_width=1.2`, 2026-11-09). A stripe's outermost pixels curve away from the camera and go dark, so a box copied from the stripe's columns ran about 15 % narrow on the big campus barrels (Tanush saw it on `core_02`; the IoU ≥ 0.5 match never would). Now, when the stripe is "full" (not the partly-hidden path), the box's left and right edges come from the body-colored columns joined to the stripe above and below it (`_body_columns`: walk outward while a column holds ≥ 2 body pixels, gaps of 2 allowed), never into another found stripe's columns (a touching same-color neighbour), and at most 1.2 × the expected width. Median box-width ratio on the campus train frames 0.90 → 0.96, worst 0.74 → 0.88 (`EXPERIMENTS.md` 2026-11-09); the score is unchanged because the rule did not see the flaw. `body_width=0` is the old behaviour.
- **(e) A stripe cut by the frame edge is hidden on that side.** The "partly hidden" rule widens a narrow stripe to a full barrel on the side where something barrel-colored borders it; a frame edge now counts as that side too, so a barrel half out of the frame gets its box drawn into the edge (and clipped, `truncated`) instead of into the empty table beside it (campus `edge_01`; found after the first v2 scoring on Tanush's boxes, so added after (a)–(d)).

*Numbers* (`experiments/2026-11-08_det_hardening/`, same pixels and camera for every row; before (e), which changes only frame-edge barrels): with the frozen v1 pixels, home train v2 **0.91 → 0.93** (orange 0.87 → 0.90, blue 0.96 unchanged, nothing on the negatives) and the campus train frames 7 → 8 right; under the hue model (probe fit) home **0.57 → 0.78**, Dave's 12 frames 0.31 → 0.40, campus 12 → 15 of 21 right, frames with an extra box 5 → 1, nothing on the four campus negatives. With the dark-gap path back on, every number is worse (home 0.67, campus 10, boxes on a negative).

### The code, in call order

| function | one line |
|---|---|
| `DetConfig` | the seven numbers (below) |
| `Blob` | a blob: `bbox`, its pixel mask, `n_orange`, `n_blue` |
| `find_blobs(mask, cfg)` | step 1 |
| `expected_width_px(bbox, cam, frame_h)` | one barrel's width at this blob's distance (bottom row if in frame, else top row) |
| `split_blob(blob, mask, cam, cfg)` | step 2: how many, cut at the waists, re-box and re-count each piece |
| `predicted_bottom(cam, top_row)` | where the base must be, given the top row |
| `resolve_bottom(bbox, cam, frame_h, cfg)` | step 3: seen vs predicted, clip, flags |
| `detect_step1(mask, cfg, cam)` | steps 1–3: for each blob, for each piece → bottom → shape checks → `Barrel`; sorted left to right |
| `Stripe` | a band: body color, box, colored and dark pixel counts, centre row |
| `find_stripes(mask, cam, cfg)` | step 4a: dispatches on `stripe_mode` — `_find_stripes_cores` (default: components of the other color sandwiched pixel by pixel, 2026-11-08) or `_find_stripes_bands` (the 2026-11-03 non-body bands) |
| `_reach_by_row(cam, h, cfg)`, `_closed`, `_split_merged` | helpers of the cores finder: how far body color may be from a stripe at each row; a closed class mask; cutting a merged stripe region into one `Stripe` per barrel |
| `_body_extent(mask, body, x0, x1, y0, y1)` | seen top and bottom of the body in the stripe's columns |
| `barrel_from_stripe(stripe, mask, cam, cfg, others)` | step 4b: the full box from the stripe's row; seen edges when they agree; width from the body columns joined to the stripe, never into `others` (the other stripes' columns) (`body_width`, (f)); refused when the box holds too little body color (`body_min`) |
| `detect(mask, cfg, cam)` | the entry point: stripe barrels + the stripeless pieces that could not show a stripe; with `require_stripe=False`, steps 1–3 alone |
| `draw(image, barrels)` | the output image (yellow = orange barrel, green = blue barrel, 1 px) |

`detect` itself is about twenty lines; read it with the table above beside it.

### The numbers (`DetConfig`)

| name | value | what it is | why this value |
|---|---|---|---|
| `min_area_px` | 20 | drop blobs smaller than this | the same speck threshold the v1.5 auto-split used; a real barrel is never this small inside the 60 cm range |
| `close_px` | 3 | close gaps up to this wide before finding blobs | 1–2 px speckle gaps inside shaded faces; larger would start merging neighbours |
| `bottom_tol` | 0.15 | seen bottom trusted within this fraction of the predicted height | the camera numbers are good to ≈ 5–10 % of a barrel's height; 15 % leaves room without accepting a shadow-shortened box (those are 30 %+ short) |
| `bottom_tol_min_px` | 4 | …and never less than this many pixels | far barrels are 30 px tall; 15 % of that is 4.5 px, about the labeling precision |
| `width_min` | 0.4 | a piece narrower than this × expected width is a sliver | a half-hidden barrel is still ≥ 0.5 wide; stripe fragments and edges are < 0.3 |
| `width_max` | 1.6 | a piece wider than this × expected width is not one barrel | after splitting, nothing legitimate should be wider than ≈ 1.2; 1.6 is slack |
| `min_width_px` | 16 | expected width below this → not on the table | 16 px ≈ 64 cm away, past the far end of any table we use; it also kills everything at the horizon |
| `split_search` | 0.25 | look for the waist within ± this × expected width of the equal-spacing cut | the waist is within a few px of the midpoint for same-size barrels; a quarter width tolerates one barrel being slightly closer |
| `require_stripe` | on | step 4 on/off | on since 2026-11-05: step 4 beat steps 1–3 under both rules; `--step1` in the CLI turns it off |
| `stripe_h_min` / `stripe_h_max` | 0.45 / 1.6 | the stripe core's height as a fraction of the expected stripe height | segmentation erodes a stripe by a pixel or two each side (far: 9 px → 5–7); 1.6 keeps a slightly fat band, excludes an upper body (1.5 ×) read as a band |
| `band_h_max` | 3.0 | the whole band (core + shadow) at most this × the expected stripe height | shadow below a stripe can double the band; a band 3 × tall is a whole barrel face, not a stripe |
| `stripe_w_min` | 0.4 | a band narrower than this × a barrel width is not a stripe | a stripe hidden more than 60 % cannot place its barrel reliably |
| `stripe_merge` | 1.4 | a band wider than this × a barrel is several merged stripes | touching same-color barrels' stripes meet at the bulges; cut evenly |
| `stripe_full` | 0.8 | a stripe narrower than this × a barrel is partly hidden → widen to a full barrel | a free-standing stripe is 0.85–1.05 widths after erosion |
| `min_stripe_px` | 4 | stripes thinner than this cannot be resolved → stripeless pieces allowed | 4 px is the expected stripe at ≈ 60 cm, the far end of a table |
| `stripe_mode` | cores | how stripes are found: from their own pixels (`cores`, 2026-11-08) or as non-body bands (`bands`, 2026-11-03) | hardening (b) above |
| `dark_stripe` | off | accept a gap with no stripe-colored pixel as a shadowed stripe | hardening (a): the floating boxes of the first live run were such gaps |
| `body_min` | 0.1 | least body-color fraction in the stripe's columns outside the stripe rows (and body must outnumber stripe color) | hardening (c); 0.1 keeps heavily shadowed barrels whose faces are mostly unlabeled |
| `body_width` | 1.2 | the box may be this × the expected width at most when widened to the body columns joined to the stripe; 0 = stripe-wide boxes | hardening (f), 2026-11-09: stripe-wide boxes ran 15 % narrow on big barrels; 1.2 leaves room for a shaded edge, not a neighbour |
| `height_min` / `height_max` | 0.5 / 1.5 | a stripeless piece's height as a fraction of the expected barrel height at its bottom row | hardening (d): the width check alone took a jacket; 0.5–1.5 matches the width band |

### How to run and how to score

```
python barrels/tools/detect_image.py barrels/data/raw/4A8B_window_light_touch_02.png
```

writes `barrels/results/detect_image/4A8B_window_light_touch_02_boxes.png` and prints one line per barrel: color, box, and how its edges were decided — "bottom seen" or "bottom inferred", "top inferred", "partly hidden, full box drawn", "cut by frame", and whether it came "from its stripe" or was a stripeless piece ("no stripe seen"). `--step1` runs steps 1–3 alone. `--json` also writes `<stem>_det.json` (the `Barrel` records) so a folder of them can be scored with `tools/eval_boxes.py --pred DIR [--rule v2]`. The experiment that produced the numbers below is `python barrels/experiments/2026-11-03_det_step2/run.py [--rule v2]`; it writes `results/2026-11-03_det_step2[_v2]/` with one sheet per frame (our boxes yellow/green, the hand-drawn truth in thin white, the stripes found in magenta) and the score tables for the floor, steps 1–3 and the full detector.

### What went wrong with steps 1–3 — and what step 4 (the stripe) fixed

- **Same-color occlusion.** A barrel partly behind another of the same color merges into one blob with it, and the width rule cannot tell "one barrel in front of another" from "one wide blob": `occl_01` and `occl_02` are missed. Four barrels bunched together (`cluster_01`) come out as two.
- **Anything orange or blue of about the right size gets a box.** The shape checks only ask "is this barrel-sized for its row", not "is this a barrel". A hand that *touches* a barrel is worse: in `far_02` the fingers merge with the right blue barrel into one blob whose top row is at the hand, so the geometry thinks the barrel is 2.5 m away and throws it out — a real barrel lost because of a hand.
- **Far range.** At 30 cm the tolerance (6 px) is about the size of the camera error (5 px), so the geometry can overrule a seen bottom that was right (`far_02`, 7 px). The calibration session will shrink the camera error; the tolerance may also need to be looser far away.

Step 4 (the stripe) attacks the first two directly and fixed them on the train frames (which is why it is the default): a band of one color sandwiched between the other color above and below, at the height the geometry expects, proves "this is a barrel", gives one barrel per stripe even inside a merged blob, and refuses hands and other orange or blue objects. What remains is a barrel whose stripe is entirely hidden behind another barrel.

### Numbers to remember

16 train frames, same pixels (frozen `afd85483`) and camera for every row, Tanush's hand-fixed boxes as the truth (`EXPERIMENTS.md` 2026-11-03 evening; re-run 2026-11-05, identical):

| | full detector (steps 1–4) | steps 1–3 | floor (one box per blob) |
|---|---|---|---|
| mean F1, **v2 rule** (every barrel counts, bottom within a tenth of the height) | **0.91** (orange 0.87 / blue 0.96) | 0.71 | 0.43 |
| mean F1, overlap-only rule | 0.97 | 0.86 | 0.48 |
| matched bottoms within 1 px | 23 of 25 | | |
| boxes drawn on the two empty frames | 0 | 0 | 0 |

The misses are the barrels whose stripe is entirely hidden (`cluster_01`, `occl_01`, `occl_02`). Two caveats: the camera was fit on these same frames (one physical number), and the pixels come from a segmentation model fit on these frames. With the October camera instead of the re-fit one, steps 1–3 scored 0.52 with bottoms 21 px off — the geometry, not the logic, was the limit then.

## 4. Detection eval — `src/barrels/eval_det.py`

**What it does.** Scores predicted boxes against the hand-drawn boxes: for each image, which predictions match which true barrels, and from that precision, recall and F1 per color, plus how far off the bottom edges are.

**The idea.** A prediction and a true box *match* only if they have the same color and overlap enough — intersection over union ≥ 0.5, i.e. the overlapping area is at least half the area the two boxes cover together. Matching is greedy: the most confident prediction takes the best-overlapping free truth box, then the next, so each true barrel is used at most once. What is left over is either a *false* box (a prediction with no truth) or a *miss* (a truth with no prediction). On frames with no barrels every box is false. Per color: precision = matches ÷ boxes drawn, recall = matches ÷ true barrels, F1 = their harmonic mean (2PR ÷ (P + R)), and the headline number is the mean of the orange and blue F1. That is the **v1 rule**, which also ignores true barrels flagged occluded / truncated / top-only (they count neither as hits nor as misses). The **v2 rule** (`EVAL.md`, in the code since 2026-11-03 evening, `rule="v2"`) is stricter in two ways: a match also needs the predicted bottom edge within max(3 px, a tenth of the true box height), and **every** true barrel counts — occluded, truncated, held, all of them; the flags only split the error reports (bottom error for seen vs `bottom_estimated` boxes). Matching under v2 takes the highest-overlap eligible pair first. A false box on an empty frame marked `clean` (nothing orange or blue in it) disqualifies the configuration outright. Scores are also broken down per scene tag.

**Where it lives.** `evaluate_frame(name, preds, gts, cam, rule="v1"|"v2", clean=…)` → per-frame counts and the list of matches with their IoU and bottom-row error; `bottom_tol_px` / `bottom_within_tol` (the v2 bottom condition); `match_greedy` (v1) and `match_best_first` (v2); `aggregate` pools frames per condition, per scene and overall; `write_results` writes `summary.md`, `summary.csv`, `per_image.csv` (counts per frame) and `per_barrel.csv` (every match, miss and false box with its IoU, bottom error and `width_ratio` = predicted width / true width, added 2026-11-09 because the IoU match passes a box 15 % too thin); `score` reduces a run to one dict for sweeps (primary = mean F1; `disqualified` when a clean empty frame got a box). CLI: `tools/eval_boxes.py --pred DIR --split train --gt-boxes --rule v2`.

**What can go wrong.** The true bottom edge of a hidden base is itself a human estimate, so bottom-edge error is reported separately for `bottom_estimated` boxes (`per_barrel.csv`). Five test frames hold about ten barrels, so the test number will be coarse: one miss moves recall by 10 %.

## 5. The live feed — `live/` + `worldmap_bridge.py` + `tracker.py` (2026-11-05; the multi-frame program and frame capture 2026-11-06)

**What it does.** Shows sections 1 and 3 on the robot's own camera, in a window on the laptop. Dave's ask from the 2026-11-03 meeting. Display only: the world map still runs on the vendor detector. Two programs: `BarrelViewer` answers every frame on its own (the spec's answer, once a second); `BarrelTracker` shows boxes that persist over frames (Tanush's ask after the first live run, 2026-11-06).

**The idea.** aim_fsm programs are state machines: *nodes* do something when entered, *transitions* move between nodes when an event happens. `BarrelViewer`'s own node is `ShowFrame`: it reads `robot.camera_image` (the latest frame, RGB; skipped when no new frame has arrived since the last tick), hands it to the hook, and calls `imshow`. A one-second timer (`=T(1)=>`) re-enters `ShowFrame`, so the window refreshes once a second. The nodes both programs share live in `live/barrel_live.py`: `SetMode` changes which picture is shown, `Save` and `Record` write raw frames (below). Each is reached by a text message (`tm seg` at the `C>` prompt fires `=TM('seg')=>`) and returns to the loop at once (`=N=>`). The whole machine is six lines in `$setup{}`; `genfsm` turns them into the Python that wires nodes to transitions (`live/BarrelViewer.py`, committed so `simple_cli BarrelViewer` works without regenerating).

**The hook.** `BarrelDetectorHook` holds the three things the detector needs — the frozen segmentation model (`afd85483`), the detector and its config (`detector.detect`, `DetConfig()`), the camera preset (`AIM_4A8B6118_BOXFIT`) — and `default()` builds that exact combination, so "the detector as it stands" is defined in one place and `tools/detect_image.py` loads the same model file. One escape hatch: the environment variable `BARRELS_MODEL` names another model file, and `default()` (hence both live programs and `detect_image.py`) loads that instead, so a candidate front end can be tried on the robot before it is adopted (`RUNBOOK.md`). `view(image_rgb, mode)` is the live frame's whole path: RGB → BGR (OpenCV's order, what the pipeline takes), `segment` (section 1), `detect` (section 3), then `detector.draw` for `"boxes"` (the v2 output image: yellow = orange barrel, green = blue, 1 px), `viz.overlay` for `"seg"` (the class mask blended over the image), or both; then BGR → RGB because `imshow` wants RGB. `render(image_rgb, barrels, mode, raw=None)` is the drawing half on its own, for a program that decides itself which barrels to draw; `view` = `on_image` + `render`. A test checks that `view` produces pixel-for-pixel what `detect_image.py` writes for the same frame.

**The multi-frame view (`BarrelTracker`).** The detector still answers each frame on its own — that answer is what the eval scores and what `tm raw` overlays in white. `tracker.Tracker` sits on top and decides what to *show*. Each frame's barrels are matched to the known tracks by color and box overlap (IoU ≥ 0.3, best overlap first, each used once); unmatched ones start new tracks. A track is shown once it has been seen in 3 of the last 4 frames, stays shown through one missed frame, is hidden at two, and is forgotten after four misses in a row. The box drawn is the per-edge median of the last three matched boxes, so one odd frame cannot move it. `BarrelTracker.fsm` runs the loop five times a second (`=T(0.2)=>`) and counts only distinct camera frames (`robot.frame_count`). Worked example at 5 fps: a barrel that enters the picture is drawn 3 frames later (0.6 s); missing from one frame it stays; missing from two it disappears; back for three it reappears, on the same track. What this cannot do: hide a mistake that is there frame after frame, like the floating box of the first live run — that is the detector's to fix.

**Saving frames (`capture.py`).** `tm save` writes the current frame as `snapshots/robot_snapN.png` under `barrels/live/` (the camera viewer's naming, N continuing past existing files, so `tools/import_snaps.py --src barrels/live/snapshots` takes them as usual). `tm rec` records every frame for ten seconds, at most ten a second, into `snapshots/rec_<stamp>/` with a `frames.json` of times and frame counts. Recording runs in `user_image`, the per-frame callback aim_fsm gives every program, on the image thread, so it costs the detector loop nothing; a disk error stops the recording, never the stream. Frames come in RGB and are written BGR, so they load like every committed frame.

**Where it lives.** `live/BarrelViewer.fsm`, `live/BarrelTracker.fsm` (≈ 50 lines each, half docstring), `live/barrel_live.py` (the base: hook, modes, `new_frame`, `report`, `user_image`, the shared nodes); `worldmap_bridge.BarrelDetectorHook` with `default()`, `segment`, `on_image` (barrels), `view` (picture), `render` (picture for given barrels), `annotate`; `wb.DEFAULT_MODEL`, `wb.VIEWS`; `tracker.TrackConfig` / `Tracker.update` / `visible`; `capture.FrameCapture.save` / `start_recording` / `on_frame`. The rest of `worldmap_bridge.py` is the parked world-map route.

**How to run it.** `RUNBOOK.md`: `cd barrels/live && simple_cli BarrelViewer` (per frame) or `simple_cli BarrelTracker` (persisting boxes); `tm seg` / `tm boxes` / `tm both`; `tm save` / `tm rec`; `tm raw` in the tracker; Ctrl+\ to quit; `genfsm X.fsm` only after editing an `.fsm`. ≈ 60 ms per frame on the laptop.

**What can go wrong.** First run 2026-11-06 (Tanush, the back of his laptop as a plain backdrop on a campus table): the window and the controls work; the detector drew a floating orange box above the orange barrel and missed the barrel itself. Rebuilt from his screenshots (`experiments/2026-11-06_live_first_run/`): the stripe finder took a band of unlabeled pixels under a false orange smear for a shadowed stripe, and threw the real blue stripe away because the unlabeled shadow glued to it made its band taller than three stripe heights. That is the detector-hardening task; the segmentation's own false orange (the edge of the laptop lid, the glow a barrel throws on the table, skin) and its missing shaded faces are the redesign's. On a scene like Dave's office the segmentation finds nothing (section 1), so the boxes view is just the camera image; `tm seg` shows why (no tint). The camera preset is fit for Tanush's robot; on another robot the predicted bottoms will be off by the tilt difference. If the window never appears, no frame has arrived yet (the console says so); if it freezes, `restart img_thread`.
