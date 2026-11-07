# Recordings 2026-11-07 replayed: per-frame detector vs the 3-of-4 view

git 091a616; detector as it stands (frozen v1 model, stripe step, boxfit camera); TrackConfig {'window': 4, 'min_hits': 3, 'iou_min': 0.3, 'max_misses': 4, 'smooth': 3}.

| clip | frames | raw O/B per frame (median, min–max) | raw count changes | raw blips | blips shown | shown O/B per frame (median, min–max) | shown count changes | lag frames (new tracks) |
|---|---|---|---|---|---|---|---|---|
| r1_static | 54 | 0 (0–0) / 0 (0–0) | 0 | 0 | 0 | 0 (0–0) / 0 (0–0) | 0 | – |
| r2_pan | 63 | 0 (0–1) / 0 (0–1) | 6 | 2 | 0 | 0 (0–0) / 0 (0–1) | 2 | 2 |
| r3_enter_leave | 60 | 0 (0–0) / 0 (0–0) | 0 | 0 | 0 | 0 (0–0) / 0 (0–0) | 0 | – |
| r4_hand_occlusion | 61 | 0 (0–1) / 0 (0–1) | 9 | 5 | 0 | 0 (0–0) / 0 (0–0) | 0 | – |

Clips: r1_static = two barrels at about 15 cm, nothing moves; r2_pan = the robot turned slowly by hand, barrels in view; r3_enter_leave = a barrel slid into the view from the side and out again; r4_hand_occlusion = a hand waved across the barrels twice.

Raw = the frame's own answer (what BarrelViewer shows); shown = what BarrelTracker shows. White boxes in the strips are raw, colored ones shown.