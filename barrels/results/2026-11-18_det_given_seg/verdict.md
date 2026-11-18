# Verdict against the pre-registered rule (round 2; round 1 is in `round1/` and in the PREREG addendum)

Rule: `experiments/2026-11-18_det_given_seg/PREREG.md`. Numbers: `summary.md`, `scenarios.csv`, `report_<arm>/`,
`recordings.md`, `by_eye.md`. Found / barrels (false boxes).

| | base | cap | join | cap+join | cap+join+side | side (report only) |
|---|---|---|---|---|---|---|
| 1 perfect masks | 25 / 29 (0) | 28 / 29 (0) | 25 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) | 25 / 29 (0) |
| 2 light | 131 / 145 (0) | 141 (0) | 131 (0) | 141 (0) | 141 (0) | 131 (0) |
| 2 medium | 36 / 145 (24) | 37 (24) | 62 (22) | 64 (22) | 99 (7) | 92 (16) |
| 2 heavy | 12 / 145 (2) | 12 (2) | 13 (2) | 13 (2) | 20 (0) | 20 (1) |
| 3a CAMPUS | 34 / 35 (0) | 34 (0) | 34 (0) | 34 (0) | 35 (0) | 35 (0) |
| 3b BLACK, label thresholds | 17 / 26 (1) | 19 (2) | 17 (1) | 19 (2) | 19 (2) | 17 (1) |
| 3c wood cool, label thresholds (report only) | 24 / 42 (7) | 24 (7) | 25 (7) | 25 (7) | 28 (8) | 27 (9) |
| eval table HOME (found / missed / false, score) | 25 / 4 / 0, 0.93 | 27 / 2 / 0, 0.97 | 25 / 4 / 0, 0.93 | 27 / 2 / 0, 0.97 | 27 / 2 / 0, 0.97 | 25 / 4 / 0, 0.93 |
| eval table CAMPUS | 34 / 1 / 0, 0.99 | 34 / 1 / 0 | 34 / 1 / 0 | 34 / 1 / 0 | 35 / 0 / 0, 1.00 | 35 / 0 / 0, 1.00 |
| eval table BLACK (report only) | 2 / 24 / 0 | 2 / 24 / 0 | 3 / 23 / 1 | 3 / 23 / 1 | 5 / 21 / 1 | 4 / 22 / 2 |
| eval table wood, brightness 3 and 6 (report only) | 7 / 119 / 3 | 7 / 119 / 4 | 7 / 119 / 3 | 7 / 119 / 4 | 7 / 119 / 4 | 7 / 119 / 4 |
| eval table wood, brightness 1 (report only) | 0 / 63 / 0 | same | same | same | same | same |
| eval table Dave (indicative) | 11 / 23 / 2, 0.47 | 11 / 23 / 2 | 12 / 22 / 2, 0.49 | 12 / 22 / 2 | 12 / 22 / 2 | 12 / 22 / 2 |
| recordings: boxes appearing / of them wrong; disappearing | | 1 / 1; 0 | 0 / 0; 1 | 1 / 1; 1 | 9 / 4; 1 | 5 / 0; 0 |

| rule | cap | join | cap+join | cap+join+side |
|---|---|---|---|---|
| 1 never regress (HOME and CAMPUS rows; no box on any negative frame) | pass | pass | pass | pass |
| 2 level 1: all found, or the miss explained | 28 of 29; see below | no (the 4 hidden barrels) | 28 of 29; see below | 28 of 29; see below |
| 3 level 2: more found at each severity, no more false | **no** (heavy 12 = 12) | **no** (light 131 = 131) | pass | pass |
| 4 level 3: 3a not lower, 3b higher, no more false | **no** (3b false 1 → 2) | **no** (3b 17 = 17) | **no** (3b false 1 → 2) | **no** (3b false 1 → 2) |
| 5 recordings by eye | **no** (1 wrong box, wood clip) | pass | **no** (the same box) | **no** (4 wrong boxes) |

**No arm passes. Nothing is adopted: `stripe_join` and `cap_behind` stay off, `stripe_w_min` stays 0.4,
`occl_body_side` stays off. The default detector is the one on `barrels`.**

What stands between `cap+join` and a pass, exactly:

- **Rule 4, one box.** Black `occl_04`: the hidden orange barrel is boxed (268, 128, 335, 200), IoU 0.86 with
  the label (267, 129, 334, 193). The label's bottom is hand-estimated (`bottom_estimated`) and makes the barrel
  67 wide and 64 tall; unoccluded barrels are taller than wide (median 1.05 to 1.07). The v2 rule counts the box
  as a miss and a false box. This is the weak point written into the PREREG before round 1.
- **Rule 5, one box.** Wood clip `frame_022`: an orange box on a hand above a blue barrel, next to a wrong orange
  box `base` already draws. The wood table is parked as extreme in the eval table, but rule 5 was written without
  that exception.
- **Rule 2, a judgment.** The one barrel still missed on the perfect masks is the middle orange barrel of
  `cluster_01`: only a wedge of its top shows between two blue barrels, no stripe, no side, no bottom. Its
  presence can be seen; its box cannot be measured from the mask (round 1 drew it 8 px too low). Round 2 draws
  no box there on purpose.

What `cap+join+side` adds and why it fails: campus `occl_02` found (35 of 35), medium damage 64 → 99, but two
boxes on the black-table clip are drawn half off the barrel (`by_eye.md`).

Not fixed by any arm: stripes eaten by 2 px at far range (95 of 145 with that damage alone), heavy damage, the
two far barrels cut by the left frame edge on black (`close_02`, `held_01`: glare, almost nothing painted),
black `clutter_02` (a stripe 3 px tall), black `far_01` (the reflection on the glossy table is painted as body
and the box bottom is 7 px low).
