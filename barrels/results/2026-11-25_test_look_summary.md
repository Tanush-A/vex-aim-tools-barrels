# The one look at the test frames (2026-11-25), as it came

Rule written first: `experiments/2026-11-25_test_look/PREREG.md`. Configuration: `wip/final` (today's detector + the verify step; color model `eb863d84`, adaptive rules off). Nothing was changed after these numbers. Full tables: `2026-11-25_test_look_ours/`, `2026-11-25_test_look_vendor/`.

**Home and campus (strict v2):** home 9 of 9, no false box, score 1.00; campus 22 of 24, 1 false box, score 0.94 (train: 28 of 29 and 35 of 35).

**The new conditions (test frames with a vendor file, 31 frames, 32 barrels), found (false):**

| condition | ours | vendor |
|---|---|---|
| gray table | 2 (0) | 2 (0) |
| bathroom cool 6 | 2 (0) | 1 (1) |
| bathroom mid 3 / mid 6 | 0 (0) / 0 (1) | 1 (0) / 1 (0) |
| bathroom warm 6 | 0 | 0 |
| glass, 5 lights | 6 (3) of 10 | 8 (1) |
| ottoman cool 6 / mid 6 / warm 6 | 1 / 0 / 0 (0) | 2 / 2 / 2 (0) |
| ottoman mid 3 (extreme) | 0 | 1 (1) |
| pale wood | 1 (0) | 1 (1) |
| white occlusion set | 2 (0) | 2 (0) |
| **all** | **14 of 32 (4)** | **23 of 32 (5)** |

By place (box in the right place, ignoring tightness): ours 16, vendor 28.

**The verify step on unseen frames:** same barrels found (47 against 48 of 121 over all 78 test frames; the one difference is on the parked orange wood set), 6 false boxes against 9.

**Reading.** On home and campus the detector holds up on frames it never saw. On the new conditions the test set is small (2 barrels per condition), so single barrels swing the numbers; the pattern matches the train frames: the vendor wins on the ottoman and the dim bathroom (our color step), we win on the cool bathroom, they tie elsewhere. The glass test frames go worse than the train frames (6 of 10 against 74 of 75 on train), which is the first sign of a gap the train frames did not show.
