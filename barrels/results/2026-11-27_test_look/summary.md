# The planned look at the test frames, 2026-11-27, as it came

Rule written first and pushed before the run: `experiments/2026-11-27_test_look/PREREG.md` (commit 9d43df8). One configuration: the default of `barrels` at 125aed7 (`pipeline.detect_frame`: fixed colors `eb863d84`, `DetConfig()`, the stripe by contrast), called **now**. Beside it, report only: the default before the contrast stage (**before**) and the robot's own detector (**vendor**, on the 31 test frames that have a vendor file; nothing assumed elsewhere). Run once (`run.py`, at 9d43df8, whose detection code is that of 125aed7). Strict v2 rule; per placement = each physical barrel once. **Nothing was changed after these numbers.** No picture of a test frame was looked at. Every number: `tables.md`, `numbers.json`, `frames.json`; the standard tables: `now_vs_before/`, `now_vs_vendor/`.

## Home and campus (strict v2)

Home 9 of 9, no box off its barrel, score 1.00; campus 22 of 24, 1 box not on its barrel, score 0.94. The same before and now, and the same as the look of 2026-11-25. (Train: 28 of 29 and 35 of 35.)

## By place, ours before, ours now, the vendor

Found per frame (per placement in brackets). The vendor columns are on the frames with a vendor file only; home and campus have none.

| place (lights in the test set) | frames | before | now | vendor (same frames) | boxes not on their barrel, before / now / vendor |
|---|---:|---|---|---|---|
| home white table (window) | 5 | 9 of 9 (9 of 9) | 9 of 9 (9 of 9) | no file | 0 / 0 / – |
| campus study room | 10 | 22 of 24 (22 of 24) | 22 of 24 (22 of 24) | no file | 1 / 1 / – |
| ABP gray table | 2 | 2 of 2 (2 of 2) | 2 of 2 (2 of 2) | 2 of 2 | 0 / 0 / 0 |
| bathroom floor (cool 6, mid 3, mid 6, warm 6) | 8 | 2 of 8 (0.5 of 2) | **5 of 8 (1.25 of 2)** | 3 of 8 (0.75 of 2) | 0 / 0 / 0 |
| glass table (window, cool 6, mid 3, mid 6, warm 6) | 10 | 6 of 10 (1.2 of 2) | 6 of 10 (1.2 of 2) | 8 of 10 (1.6 of 2) | 2 / 2 / 0 |
| ottoman (cool 6, mid 6, warm 6) | 6 | 2 of 6 (0.67 of 2) | 2 of 6 (0.67 of 2) | **6 of 6 (2 of 2)** | 0 / 0 / 0 |
| pale wood (overhead dim) | 2 | 1 of 2 (1 of 2) | 1 of 2 (1 of 2) | 1 of 2 | 0 / 0 / 0 |
| ABP white occlusion set (window) | 1 | 2 of 2 (2 of 2) | 2 of 2 (2 of 2) | 2 of 2 | 0 / 0 / 0 |
| **ordinary conditions, all** | 44 | 46 of 63 (38.37 of 45) | **49 of 63 (39.12 of 45)** | – | 3 / 3 / – |
| **the 29 ordinary frames with a vendor file** | 29 | 15 of 30 (7.37 of 12) | 18 of 30 (8.12 of 12) | **22 of 30 (9.35 of 12)** | 2 / 2 / 0 |
| *report only:* orange wood under the lamp (12 lights) | 27 | 1 of 45 (0.11 of 5) | 18 of 45 (2.0 of 5) | no file | 0 / 0 / – |
| *report only:* ottoman, mid 3 | 2 | 0 of 2 | 0 of 2 | 1 of 2 | 0 / 0 / 0 |
| *report only:* black table | 5 | 1 of 11 (1 of 11) | 3 of 11 (3 of 11) | no file | 0 / 0 / – |
| **all 31 frames with a vendor file** (the previous look's comparison) | 31 | 15 of 32 (7.2 of 12) | **18 of 32 (7.95 of 12)** | **23 of 32 (9.1 of 12)** | 2 / 2 / 0 |
| **all 78 test frames** | 78 | 48 of 121 (39.31 of 61) | 70 of 121 (43.95 of 61) | – | 3 / 3 / – |

Boxes on empty frames: none, for any arm, on any of the 27 empty test frames (clean or with clutter). Found with the box off: before 3, now 5 (all 78 frames); on the vendor frames before 2, now 2, vendor 5.

By light, on the vendor frames (found per frame, of 2 each; before / now / vendor): bathroom cool 6 2 / 2 / 1, mid 3 0 / **2** / 1, mid 6 0 / 0 / 1 (ours: one box off), warm 6 0 / **1** / 0; glass cool 6 2 / 2 / 2, mid 3 1 / 1 / 2, mid 6 1 / 1 / 2, warm 6 1 / 1 / 1, window 1 / 1 / 1; ottoman cool 6 1 / 1 / 2, mid 6 1 / 1 / 2, warm 6 0 / 0 / 2, mid 3 (extreme) 0 / 0 / 1.

## Reading

- **Home and campus hold** on frames the detector never saw, as on 2026-11-25. The contrast stage changes nothing there, as on train.
- **The contrast stage helps on the test frames where it helped on train, but less.** On the bathroom floor 2 → 5 of 8 (now ahead of the vendor's 3); under the parked orange-wood lamp 1 → 18 of 45; the black table 1 → 3 of 11. Over all 78 frames 48 → 70 of 121. It lost no barrel, drew no new box that is not on a barrel, and nothing on an empty frame.
- **The ottoman did not move** (2 of 6, the vendor 6 of 6). On train the stage took the ottoman from 3.3 to 10.3 of 15 placements; on its 6 test frames it found none of the missing four. The glass table stays at 6 of 10 (vendor 8), as on 2026-11-25: the gap to its 74 of 75 on train is still there, and it is not one the contrast stage touches.
- **Against the vendor on its frames: 18 of 32 against 23 of 32** (per placement 7.95 against 9.1 of 12). We were 14 of 32 on 2026-11-25 and 15 before the contrast stage today. The vendor puts no box off its barrel here; we put 2 (both on glass). It has 5 boxes on their barrel but off under the strict rule, we 2.
- The test set is small: 2 placements per place on the new conditions, so one barrel moves a place by half. The direction is the train frames' direction (bathroom gains, nothing lost); the size is not.
- Nothing is changed because of these numbers (PREREG). Anything learned here needs new train frames and new test frames.
