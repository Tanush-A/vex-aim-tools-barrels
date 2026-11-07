# STATUS.md — where we are

**Updated:** 2026-11-06 (first live run; the multi-frame program and frame capture built). One screen by design: history lives in `EXPERIMENTS.md` and `DECISIONS.md`, the task list in `TODO.md`, the code guide in `HOW-IT-WORKS-SHORT.md`.

## State

- **The detector works on the simple data.** One image in, boxes out (`tools/detect_image.py`). Steps: frozen v1 color segmentation → stripe-anchored detector (default since 2026-11-05) → bottom edge from the geometry when hidden. 16 train frames, Tanush's boxes, v2 rule: **0.91** mean F1 (orange 0.87, blue 0.96), 23 of 25 bottoms within 1 px, nothing drawn on empty frames; floor 0.43. Last committed detector change: fc2c98c.
- **It does not work off the training table (live run 2026-11-06).** On a campus table with a grey board behind the barrels the live view drew a floating orange box above the orange barrel and missed the barrel; with the room behind, false orange on skin and a laptop edge. From the screenshots (`EXPERIMENTS.md` 2026-11-06): the segmentation labels the board edge, the glow a barrel throws on the table and skin as orange and leaves shaded faces unlabeled; the stripe step then takes a dark gap for a shadowed stripe and rejects the real stripe because the shadow glued to it makes its band too tall. The blue barrel was right in every frame. Raw frames come 2026-11-07.
- **The front end does not transfer.** On Dave's 20 office frames the v1 segmentation outputs zero barrel pixels: both adaptive stages assume the rows above the horizon are plain wall, and his shelf is not; his pink desk then floods orange (`EXPERIMENTS.md` 2026-11-03).
- **Known misses on our data:** a barrel whose stripe is entirely hidden behind another (`cluster_01`, `occl_01`, `occl_02`); an orange-behind-blue band in `occl_02`.
- **Camera:** provisional preset `AIM_4A8B6118_BOXFIT` (f 400, tilt 22.25°, horizon 76), fit from labeled boxes; the known-distance calibration frames (tomorrow) will replace it.
- **Live feed:** two programs in `live/` (`RUNBOOK.md`): `BarrelViewer` shows each frame's own answer once a second; `BarrelTracker` shows a barrel once 3 of the last 4 frames agree and keeps it through a miss (Tanush's ask; display only, the per-image answer is unchanged). `tm save` / `tm rec` write raw frames for importing. Window, modes and the robot link verified live 2026-11-06; the tracker not yet tried on the robot.

## Now (order agreed 2026-11-06)

1. **Campus capture session 2026-11-07** (`DATA.md` → "Session 2026-11-07"): the failure scenes, the one-table list, four recordings, calibration + horizon. Import, splits and `calib.csv` the same day.
2. **Attribution** of the live failures on the real frames: segmentation or detector, per frame.
3. **Detector hardening** (pre-registered in `TODO.md`), or 4 first if attribution says the segmentation is most of it.
4. **Segmentation redesign**, with the campus frames as its dev set and Dave's as the outside check.
5. Try `BarrelTracker` vs `BarrelViewer` live; then the remaining box work: hidden-stripe barrels, the calibration fit, one test run, one email to Dave.

## Tanush's part

Tomorrow's session (`DATA.md`; ≈ 1 h on campus) and the import + splits the same day; box labels after (≈ 45 frames, ≈ 25 min); try both live programs and report what the tracker does with blips, moves and a slow pan; send Dave the short update (drafted 2026-11-06).

## Open questions for Dave

Which of his scenes to handle first (cluttered shelf, pink desk, dark warm table, lid filling the frame); calibration once or per robot; knocked-over barrels ever; is "bottom within a tenth of the height" the right tolerance; does his `detect.py` from the zip still exist. New: a display-only persistence rule in the live view (3 of the last 4 frames) is fine for the demo, since the per-image answer stays the spec? The 2026-11-03 "one table, one background" plan: the live run says the background is the problem, so the 2026-11-07 session adds backdrop variety on the one table — agreed?

## Parked (not v2.0)

World-map integration (display vs replace aivision, latency, worldmap's 22 mm / 11 mm / 1.1·w pad), ground positions in mm and the `measured` split, more tables and the unseen-table hold-out (v2.1), skin-vs-orange hue test, the `openvocab` / `depthmap` branches. Navigator requests: none open.

## Blockers

None. Tomorrow needs the robot charged, the grey board, a mm ruler and the barrels (`DATA.md` packing list).
