# The live programs with the new default, on saved train frames (no robot)

Made by `experiments/2026-11-27_adopt_contrast/live_check.py`.

- imported `barrel_live`, `BarrelViewer`, `BarrelTracker` (aim_fsm included) in 8.1 s
- 4A8B_lampmid6_bathtile_core_01: 4 boxes (4 added by the contrast stage); viewer = detect_frame box for box: yes; tracker shows 4 after 4 frames; view 216 to 218 ms
- 4A8B_campus_light_core_01: 4 boxes (0 added by the contrast stage); viewer = detect_frame box for box: yes; tracker shows 4 after 4 frames; view 98 to 101 ms
- 4A8B_lampmid6_bathtile_neg_02: 0 boxes (0 added by the contrast stage); viewer = detect_frame box for box: yes; tracker shows 0 after 4 frames; view 103 to 110 ms

RESULT: the live code runs the new default
