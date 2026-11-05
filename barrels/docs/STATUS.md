# STATUS.md — where we are

**Updated:** 2026-11-05 (doc cleanup; live feed built). One screen by design: history lives in `EXPERIMENTS.md` and `DECISIONS.md`, the task list in `TODO.md`, the code guide in `HOW-IT-WORKS-SHORT.md`.

## State

- **The detector works on the simple data.** One image in, boxes out (`tools/detect_image.py`). Steps: frozen v1 color segmentation → stripe-anchored detector (default since 2026-11-05) → bottom edge from the geometry when hidden. 16 train frames, Tanush's boxes, v2 rule: **0.91** mean F1 (orange 0.87, blue 0.96), 23 of 25 bottoms within 1 px, nothing drawn on empty frames; floor 0.43. Last committed detector change: fc2c98c.
- **The front end does not transfer.** On Dave's 20 office frames the v1 segmentation outputs zero barrel pixels: both adaptive stages assume the rows above the horizon are plain wall, and his shelf is not; his pink desk then floods orange. This is the blocker for any new scene (`EXPERIMENTS.md` 2026-11-03).
- **Known misses on our data:** a barrel whose stripe is entirely hidden behind another (`cluster_01`, `occl_01`, `occl_02`); an orange-behind-blue band in `occl_02`.
- **Camera:** provisional preset `AIM_4A8B6118_BOXFIT` (f 400, tilt 22.25°, horizon 76), fit from labeled boxes; the known-distance calibration session will replace it.
- **Live feed:** `live/BarrelViewer.fsm` shows the boxes (or the segmentation) on the robot's camera once a second (`RUNBOOK.md`). Untested on the robot as of this writing — first run is Tanush's.

## Now (order set after the 2026-11-03 meeting)

1. ~~Doc cleanup~~ done 2026-11-05.
2. **Live feed on the robot** — built 2026-11-05; Tanush runs it, reports what the camera shows.
3. **Segmentation redesign** — the front end that finds nothing on Dave's frames. Candidates and the pre-registration rule: `TODO.md`.
4. Then the remaining box work: hidden-stripe barrels, calibration session, one test run, one email to Dave.

## Tanush's part

Shoot the one-table session + 12 `calib` frames + `horizon` (`DATA.md`); label boxes (`box_tool.py`, ≈ 30 s/frame); run the live feed and say what it shows.

## Open questions for Dave

Which of his scenes to handle first (cluttered shelf, pink desk, dark warm table, lid filling the frame); calibration once or per robot; knocked-over barrels ever; is "bottom within a tenth of the height" the right tolerance; does his `detect.py` from the zip still exist.

## Parked (not v2.0)

World-map integration (display vs replace aivision, latency, worldmap's 22 mm / 11 mm / 1.1·w pad), ground positions in mm and the `measured` split, more tables and the unseen-table hold-out (v2.1), skin-vs-orange hue test, the `openvocab` / `depthmap` branches. Navigator requests: none open.

## Blockers

None. The live feed needs the robot on and `setup.zsh` sourced.
