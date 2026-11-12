# STATUS.md — where we are

**Updated:** 2026-11-11 (end of the unattended block). The step-3 shot list is agreed and in `DATA.md` ("Next shoot"); Tanush shoots it. Steps 5, 6, 7 are coded and pushed on `wip/tm-seg`, `wip/eval-report`, `wip/occlusion`; **nothing is merged, what runs is unchanged**. Summary, both walkthroughs and Tanush's action list: `docs/OVERNIGHT-2026-11-11.md`. Before that (2026-11-09): hs color model + hardened detector (a–g) on `barrels`; steps 0–2 done.

## State

- **What runs** (`worldmap_bridge.DEFAULT_MODEL`, `detect_image.py`, `BarrelViewer`, `BarrelTracker`): hs model `eb863d84` (orange hue 3–13 S ≥ 140, blue hue 103–119 S ≥ 113, fit once on the 16 home frames) → stripe detector with hardening a–g → provisional camera `AIM_4A8B6118_BOXFIT` (f 400, tilt 22.25°, horizon row 76). `BARRELS_MODEL` in the environment swaps the model file; v1 is `results/2026-10-20_v1_test_adaptive/config.json`.
- **Numbers** (v2 rule, train frames only): campus **0.99** (v1 front end: 0.41), home LOSO **0.93** (= v1), zero false detections on every negative of both sessions, Dave's office 0.47 (indicative, his boxes group touching barrels). Median box width / true width 0.96 on campus (was 0.90). Recordings: barrels found in all four clips, 0 blips shown, lag 2 frames.
- **Live run with Dave (2026-11-09):** segmentation good; two detector bugs found and fixed the same day — boxes 15 % too thin (f), and a close-up under a far barrel got no box (g). Still open from that run: a barrel touching the kicker got no box (needs a `tm save`); partial occlusion worse than expected (TODO 7); a persistent false blue box on clutter at the frame edge (TODO 9).
- **Unattended block 2026-11-11:** (5) `tm seg` second window + dimmed main window, untested on the robot. (6) `tools/report.py`, one table, reproduces 0.93 / 0.99 / 0.47. (7) the 5 train misses are all occluded barrels: 1 hidden at the side by a non-barrel (stripe 16 px, floor 21.4 px; the live miss), 4 behind a barrel of the other color (step 9). The pre-registered fix (`stripe_w_min` 0.25 + (h) `occl_body_side`) finds the one (campus 35 of 35) and adds only real barrels on home, campus, Dave and the recordings, but 2 false boxes on wood: not adopted, both switches off.
- **Direction for the week (Tanush):** hs is the right front end; (1) fix bugs, (2) generalize — many light settings, table colors incl. wood, clutter, occlusion. His measure: scenarios where the vendor detector fails and ours works.
- **Data:** HOME 21 (16/5), CAMPUS 31 (21/10), DAVE 20 (12 boxed), WOOD 24 unlabeled, 4 recordings, 1 live frame. Test frames untouched. The multi-setting collection is TODO step 3.
- **Camera:** provisional; calibration with a ruler is inside the step-3 shoot.

## Now (`TODO.md`, in order)

0–2 done → **3 collect data** (Tanush; list in `DATA.md`) → **5, 6, 7 wait on Tanush** (live check; "understood"; "understood" + decision), then merge in that order → 4 close-ups (code done, live confirm) → 8 histograms + email to Dave → 9 occlusion (extreme) + edge clutter → 9b test look 1 → 10 slider labels + adaptive plan → 10b test look 2.

## Tanush's part

In order: shoot step 3 (`DATA.md`); live-check `tm seg` on `wip/tm-seg` and confirm the close-up fix (step 4) in the same sitting; read `OVERNIGHT-2026-11-11.md` §3 and say "understood" (step 6); read §4, say "understood" and decide: occlusion fix stays off until the wood front end exists (Claude's recommendation, what the pre-registered rule says) or goes on now; `tm save` the kicker case and any live occlusion miss when they happen.

## Open questions for Dave (for the step-8 email)

Wood tables now in scope — fine? Which of his scenes to handle first; calibration once or per robot; knocked-over barrels ever; his grouped boxes (by design or shortcut); is a display-only persistence rule in the live view fine for the demo.
