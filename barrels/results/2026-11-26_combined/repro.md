# Step A: each winner alone on the collapsed detector, against its own committed judge pages

Made by `experiments/2026-11-26_combined/repro.py`. The same `fit` functions, the same judge, leave one place out; the only thing that differs from the winners' own runs is `detector.py` (collapsed on 2026-11-26).

## nearmiss: IDENTICAL

- verdict PASS (committed: PASS); found 133.80 -> 147.47 of 172 placements (committed 147.47), per frame 211 -> 249 (committed 249); boxes not on their barrel 1.93 -> 3.57 (committed 3.57); 38 barrels gained, 0 lost (committed 38 and 0).
- compared: total, places, conditions, report_only, changes, box_changes (98 changed barrels, 11 frames with changed boxes, 17 conditions, 8 report-only conditions): 0 difference(s).

## selfcal: IDENTICAL

- verdict PASS (committed: PASS); found 133.80 -> 147.55 of 172 placements (committed 147.55), per frame 211 -> 248 (committed 248); boxes not on their barrel 1.93 -> 2.18 (committed 2.18); 37 barrels gained, 0 lost (committed 37 and 0).
- compared: total, places, conditions, report_only, changes, box_changes (87 changed barrels, 2 frames with changed boxes, 17 conditions, 8 report-only conditions): 0 difference(s).

## what each fold chose, nearmiss: IDENTICAL

- abp_gray: "pc:5,5,strict"
- abp_white: "pc:5,5,pred"
- campus_study: "pc:5,5,pred"
- home_bathtile: "pc:5,5,pred"
- home_black: "pc:5,5,pred"
- home_glass: "pc:5,5,pred"
- home_ottoman: "pc:5,4,pred"
- home_white: "pc:5,5,pred"
- home_wooddesk: "pc:5,5,pred"
- uc_palewood: "pc:5,5,pred"

## what each fold chose, selfcal: IDENTICAL

- abp_gray: {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03}
- abp_white: {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03}
- campus_study: {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03}
- home_bathtile: {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03}
- home_black: {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03}
- home_glass: {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03}
- home_ottoman: {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.01}
- home_white: {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03}
- home_wooddesk: {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03}
- uc_palewood: {"rel_margin": 1.0, "hue_move_max": 6.0, "flood_max": 0.03}

RESULT: both winners reproduce exactly.
