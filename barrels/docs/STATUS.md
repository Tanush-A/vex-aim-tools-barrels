# STATUS.md — where we are

**Updated:** 2026-11-09 evening. The hs color model is the front end and the hardened detector (a–g) is on `barrels` (walkthrough acknowledged, fast-forward merge). The week's plan is `TODO.md` (order approved by Tanush). Steps 0 and 1 done (merge; doc cleanup: every doc opens with a "Now" block). Next: TODO step 2, the Claude Code CLI handoff, on Tanush's go.

## State

- **What runs** (`worldmap_bridge.DEFAULT_MODEL`, `detect_image.py`, `BarrelViewer`, `BarrelTracker`): hs model `eb863d84` (orange hue 3–13 S ≥ 140, blue hue 103–119 S ≥ 113, fit once on the 16 home frames) → stripe detector with hardening a–g → provisional camera `AIM_4A8B6118_BOXFIT` (f 400, tilt 22.25°, horizon row 76). `BARRELS_MODEL` in the environment swaps the model file; v1 is `results/2026-10-20_v1_test_adaptive/config.json`.
- **Numbers** (v2 rule, train frames only): campus **0.99** (v1 front end: 0.41), home LOSO **0.93** (= v1), zero false detections on every negative of both sessions, Dave's office 0.47 (indicative, his boxes group touching barrels). Median box width / true width 0.96 on campus (was 0.90). Recordings: barrels found in all four clips, 0 blips shown, lag 2 frames.
- **Live run with Dave (2026-11-09):** segmentation good; two detector bugs found and fixed the same day — boxes 15 % too thin (f), and a close-up under a far barrel got no box (g). Still open from that run: a barrel touching the kicker got no box (needs a `tm save`); partial occlusion worse than expected (TODO 7); a persistent false blue box on clutter at the frame edge (TODO 9).
- **Direction for the week (Tanush):** hs is the right front end; (1) fix bugs, (2) generalize — many light settings, table colors incl. wood, clutter, occlusion. His measure: scenarios where the vendor detector fails and ours works.
- **Data:** HOME 21 (16/5), CAMPUS 31 (21/10), DAVE 20 (12 boxed), WOOD 24 unlabeled, 4 recordings, 1 live frame. Test frames untouched. The multi-setting collection is TODO step 3.
- **Camera:** provisional; calibration with a ruler is inside the step-3 shoot.

## Now (`TODO.md`, in order)

0, 1 done → **2 CLI handoff** (on go) → 3 collect data → 4 close-ups (code done, live confirm) → 5 `tm seg` → 6 eval cleanup → 7 occlusion (less extreme) → 8 histograms + email to Dave → 9 occlusion (extreme) + edge clutter → 9b test look 1 → 10 slider labels + adaptive plan → 10b test look 2.

## Tanush's part

Approve nothing further for step 1; shoot step 3 once the shot list is in `DATA.md`; `tm save` the kicker case when it happens; confirm the close-up fix live (step 4).

## Open questions for Dave (for the step-8 email)

Wood tables now in scope — fine? Which of his scenes to handle first; calibration once or per robot; knocked-over barrels ever; his grouped boxes (by design or shortcut); is a display-only persistence rule in the live view fine for the demo.
