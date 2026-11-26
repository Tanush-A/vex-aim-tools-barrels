# The one planned look at the test frames (TODO G), written before any test frame is opened

Written 2026-11-25 by Claude (coordinator), committed before the run. Tanush: "G goes last; run it only after the adaptive rule is in or shown not to work, and after tomorrow's data is scored." Both are true: the adaptive rules failed their pre-registered tests in four rounds (2026-11-24 adaptive, adaptive_range; 2026-11-25 color, two rounds), and all new conditions are scored on train frames.

## What is scored, chosen now
- **One configuration:** the detector and color model of branch `wip/final` as committed with this file: `barrels` (b72ed6f) + `wip/occl-strict` (verify step `verify_front`, `verify_readings` on) + `wip/color` (adaptive rules OFF; default model `eb863d84`). This is the configuration proposed to Tanush. Report-only second line: the same with `verify_front` and `verify_readings` off (= what `barrels` runs today), to show what the verify step does on unseen frames.
- **The vendor**, on every test frame that has a vendor file, scored by the same rule against the same hand boxes.
- **Frames:** every frame in the test split (78): HOME 5, CAMPUS 10, the new ordinary conditions (gray 2, glass 10, bathroom 8, ottoman bright 6, pale wood 2, white occlusion set 1), and report-only extreme ones (ottoman mid 3: 2, bathroom warm 6 is reported apart, wood ladder 27, black 5).
- **Numbers:** per condition, found / missed / false (strict v2 rule) and found by place (same color, centre within half a barrel width); boxes on empty frames; ours vs vendor side by side. HOME and CAMPUS also as the v2 score.

## Rules
- The test frames are opened only by the scoring code in this run. No picture of a test frame is looked at before the numbers are written.
- **Nothing is changed afterwards because of these numbers.** No threshold, no switch, no rule. If a problem shows, it is reported as found on the test set; any fix would need new train-frame evidence and a new test set.
- The result is reported as it comes, including where it is worse than the train-frame numbers.
