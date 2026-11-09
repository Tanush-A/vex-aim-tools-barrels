# Recordings 2026-11-07 replayed: per-frame detector vs the 3-of-4 view

git e881cf2; front end: hs color model (o5,b15,m4, fit on the home train masks) + hardened detector DetConfig(); camera boxfit; TrackConfig {'window': 4, 'min_hits': 3, 'iou_min': 0.3, 'max_misses': 4, 'smooth': 3}.

| clip | frames | raw O/B per frame (median, min–max) | raw count changes | raw blips | blips shown | shown O/B per frame (median, min–max) | shown count changes | lag frames (new tracks) |
|---|---|---|---|---|---|---|---|---|
| r1_static | 54 | 1 (1–1) / 2 (2–2) | 0 | 0 | 0 | 1 (0–1) / 2 (0–2) | 1 | 2, 2, 2 |
| r2_pan | 63 | 1 (1–1) / 2 (1–2) | 5 | 2 | 0 | 1 (0–1) / 2 (0–2) | 2 | 2, 2, 2 |
| r3_enter_leave | 60 | 1 (0–1) / 0 (0–0) | 2 | 0 | 0 | 1 (0–1) / 0 (0–0) | 2 | 2 |
| r4_hand_occlusion | 61 | 1 (0–3) / 1 (0–1) | 14 | 5 | 0 | 1 (0–1) / 1 (0–1) | 8 | 2, 2, 2, 2, 2, 2 |

Clips: r1_static = two barrels at about 15 cm, nothing moves; r2_pan = the robot turned slowly by hand, barrels in view; r3_enter_leave = a barrel slid into the view from the side and out again; r4_hand_occlusion = a hand waved across the barrels twice.

Raw = the frame's own answer (what BarrelViewer shows); shown = what BarrelTracker shows. White boxes in the strips are raw, colored ones shown.