# The never-regress check of the new default, against the baseline of the seam reading

`python barrels/tools/report.py --gate`, run on branch `wip/adopt-contrast` with the code of commit 50a7e7f (the run printed `git bb9fc23` because the code was not yet committed; the code is the same). Baseline: saved 2026-11-27 from fa3b289 (the seam reading, no contrast stage). After it passed, the baseline and the margins were re-measured on the new default.

```
NEVER-REGRESS CHECK
this run : 2026-11-09_hs_candidate/config.json; DetConfig defaults; git bb9fc23
baseline : saved 2026-11-27 from git fa3b289 (2026-11-09_hs_candidate/config.json; DetConfig defaults)
Protected sets: HOME, CAMPUS, GLASS, PALEWOOD, ABPWHITE, BATH-COOL. A protected set fails when its found (strict rule, each placement once) is lower than the baseline's by
more than its margin, or its boxes that are not on their barrel are higher by more than its margin. A new box on a clean empty
frame fails in any set. Every barrel and box that changed is listed below, whether or not anything fails.
Margins (found / boxes): margins.json, made 2026-11-27 at git fa3b289.

PROTECTED SETS, baseline -> this run
  HOME  found 28.0 -> 28.0 of 29 placements [per frame 28 -> 28 of 29]; boxes not on their barrel 0.0 -> 0.0; margins 1.0 / 1.0: same  [protected]
  CAMPUS  found 35.0 -> 35.0 of 35 placements [per frame 35 -> 35 of 35]; boxes not on their barrel 0.0 -> 0.0; margins 1.0 / 1.0: same  [protected]
  GLASS  found 14.8 -> 14.8 of 15 placements [per frame 74 -> 74 of 75]; boxes not on their barrel 0.6 -> 0.6; margins 1.0 / 1.0: same  [protected]
  PALEWOOD  found 13.0 -> 13.0 of 15 placements [per frame 13 -> 13 of 15]; boxes not on their barrel 1.0 -> 1.0; margins 1.0 / 1.0: same  [protected]
  ABPWHITE  found 26.0 -> 27.0 of 32 placements (+1.0) [per frame 26 -> 27 of 32]; boxes not on their barrel 0.0 -> 0.0; margins 1.0 / 1.0: better  [protected]
      barrel  4A8B_window_abpwhite_occlx_06 #1: missed -> off
      barrel  4A8B_window_abpwhite_occlx_14 #1: missed -> found
  BATH-COOL  found 14.0 -> 15.0 of 15 placements (+1.0) [per frame 14 -> 15 of 15]; boxes not on their barrel 0.0 -> 0.0; margins 4.0 / 1.0: better  [protected]
      barrel  4A8B_lampcool6_bathtile_occl_02 #1: missed -> found

EMPTY FRAMES (every set)
  clean empty frames with a new box: none
  boxes on empty frames with clutter, once per arrangement: 0.0 -> 0.0 (margin 1.0)

OTHER SETS, for information only (they cannot fail the check)
  4A8B_both_abpgray  found 11.0 -> 15.0 of 16 placements (+4.0) [per frame 11 -> 15 of 16]; boxes not on their barrel 0.0 -> 0.0: better  [information only]
      barrel  4A8B_both_abpgray_core_01 #2: missed -> found
      barrel  4A8B_both_abpgray_core_01 #4: missed -> found
      barrel  4A8B_both_abpgray_edge_01 #1: missed -> found
      barrel  4A8B_both_abpgray_touch_01 #1: missed -> found
  4A8B_lampcool3_wood  found 2.0 -> 15.0 of 21 placements (+13.0) [per frame 2 -> 15 of 21]; boxes not on their barrel 0.0 -> 0.0: better  [information only]
      barrel  4A8B_lampcool3_wood_cluster_01 #1: missed -> found
      barrel  4A8B_lampcool3_wood_cluster_01 #2: missed -> found
      barrel  4A8B_lampcool3_wood_cluster_01 #3: missed -> found
      barrel  4A8B_lampcool3_wood_cluster_01 #4: missed -> found
      barrel  4A8B_lampcool3_wood_clutter_01 #1: missed -> found
      barrel  4A8B_lampcool3_wood_clutter_01 #2: missed -> found
      barrel  4A8B_lampcool3_wood_clutter_01 #4: missed -> found
      barrel  4A8B_lampcool3_wood_core_01 #2: missed -> found
      barrel  4A8B_lampcool3_wood_core_01 #3: missed -> found
      barrel  4A8B_lampcool3_wood_core_01 #4: missed -> found
      barrel  4A8B_lampcool3_wood_occl_02 #2: missed -> found
      barrel  4A8B_lampcool3_wood_touch_02 #1: missed -> found
      barrel  4A8B_lampcool3_wood_touch_02 #2: missed -> found
  4A8B_lampcool6_ottoman  found 3.0 -> 12.0 of 15 placements (+9.0) [per frame 3 -> 12 of 15]; boxes not on their barrel 0.0 -> 0.0: better  [information only]
      barrel  4A8B_lampcool6_ottoman_clutter_01 #1: missed -> found
      barrel  4A8B_lampcool6_ottoman_clutter_01 #2: missed -> found
      barrel  4A8B_lampcool6_ottoman_clutter_01 #3: missed -> found
      barrel  4A8B_lampcool6_ottoman_clutter_01 #4: missed -> found
      barrel  4A8B_lampcool6_ottoman_core_01 #1: missed -> found
      barrel  4A8B_lampcool6_ottoman_core_01 #2: missed -> found
      barrel  4A8B_lampcool6_ottoman_core_01 #4: missed -> found
      barrel  4A8B_lampcool6_ottoman_edge_01 #1: missed -> found
      barrel  4A8B_lampcool6_ottoman_edge_01 #2: missed -> found
  4A8B_lampcool6_wood  found 2.0 -> 11.0 of 21 placements (+9.0) [per frame 2 -> 11 of 21]; boxes not on their barrel 2.0 -> 2.0: better  [information only]
      barrel  4A8B_lampcool6_wood_cluster_01 #1: missed -> found
      barrel  4A8B_lampcool6_wood_cluster_01 #2: missed -> found
      barrel  4A8B_lampcool6_wood_cluster_01 #4: missed -> found
      barrel  4A8B_lampcool6_wood_clutter_01 #1: missed -> found
      barrel  4A8B_lampcool6_wood_clutter_01 #3: missed -> found
      barrel  4A8B_lampcool6_wood_clutter_01 #4: missed -> found
      barrel  4A8B_lampcool6_wood_core_01 #1: missed -> off
      barrel  4A8B_lampcool6_wood_core_01 #2: missed -> found
      barrel  4A8B_lampcool6_wood_core_01 #3: missed -> found
      barrel  4A8B_lampcool6_wood_core_01 #4: missed -> found
  4A8B_lampmid3_bathtile  found 1.0 -> 13.0 of 15 placements (+12.0) [per frame 1 -> 13 of 15]; boxes not on their barrel 0.0 -> 1.0 (+1.0): lower, within the margin  [information only]
      barrel  4A8B_lampmid3_bathtile_clutter_01 #1: missed -> found
      barrel  4A8B_lampmid3_bathtile_clutter_01 #2: missed -> found
      barrel  4A8B_lampmid3_bathtile_clutter_01 #3: missed -> found
      barrel  4A8B_lampmid3_bathtile_clutter_01 #4: missed -> found
      barrel  4A8B_lampmid3_bathtile_core_01 #1: missed -> found
      barrel  4A8B_lampmid3_bathtile_core_01 #2: missed -> found
      barrel  4A8B_lampmid3_bathtile_core_01 #3: missed -> found
      barrel  4A8B_lampmid3_bathtile_core_01 #4: missed -> found
      barrel  4A8B_lampmid3_bathtile_edge_01 #2: missed -> found
      barrel  4A8B_lampmid3_bathtile_touch_01 #1: missed -> found
      barrel  4A8B_lampmid3_bathtile_touch_01 #2: missed -> found
      barrel  4A8B_lampmid3_bathtile_touch_01 #3: missed -> found
      boxes   4A8B_lampmid3_bathtile_core_01: second 0 -> 1
  4A8B_lampmid3_wood  found 1.0 -> 12.0 of 21 placements (+11.0) [per frame 1 -> 12 of 21]; boxes not on their barrel 1.0 -> 1.0: better  [information only]
      barrel  4A8B_lampmid3_wood_cluster_01 #1: missed -> found
      barrel  4A8B_lampmid3_wood_cluster_01 #2: missed -> found
      barrel  4A8B_lampmid3_wood_cluster_01 #3: missed -> found
      barrel  4A8B_lampmid3_wood_cluster_01 #4: missed -> found
      barrel  4A8B_lampmid3_wood_clutter_01 #1: missed -> found
      barrel  4A8B_lampmid3_wood_core_01 #2: missed -> found
      barrel  4A8B_lampmid3_wood_core_01 #3: missed -> found
      barrel  4A8B_lampmid3_wood_occl_02 #1: missed -> found
      barrel  4A8B_lampmid3_wood_occl_02 #2: missed -> found
      barrel  4A8B_lampmid3_wood_occl_04 #2: missed -> found
      barrel  4A8B_lampmid3_wood_touch_02 #1: missed -> off
      barrel  4A8B_lampmid3_wood_touch_02 #2: missed -> found
  4A8B_lampmid6_bathtile  found 1.0 -> 13.0 of 15 placements (+12.0) [per frame 1 -> 13 of 15]; boxes not on their barrel 0.0 -> 0.0: better  [information only]
      barrel  4A8B_lampmid6_bathtile_clutter_01 #1: missed -> found
      barrel  4A8B_lampmid6_bathtile_clutter_01 #2: missed -> found
      barrel  4A8B_lampmid6_bathtile_clutter_01 #3: missed -> found
      barrel  4A8B_lampmid6_bathtile_clutter_01 #4: missed -> found
      barrel  4A8B_lampmid6_bathtile_core_01 #1: missed -> found
      barrel  4A8B_lampmid6_bathtile_core_01 #2: missed -> found
      barrel  4A8B_lampmid6_bathtile_core_01 #3: missed -> found
      barrel  4A8B_lampmid6_bathtile_core_01 #4: missed -> found
      barrel  4A8B_lampmid6_bathtile_edge_01 #2: missed -> found
      barrel  4A8B_lampmid6_bathtile_touch_01 #1: missed -> found
      barrel  4A8B_lampmid6_bathtile_touch_01 #2: missed -> found
      barrel  4A8B_lampmid6_bathtile_touch_01 #3: missed -> found
  4A8B_lampmid6_ottoman  found 7.0 -> 10.0 of 15 placements (+3.0) [per frame 7 -> 10 of 15]; boxes not on their barrel 0.0 -> 0.0: better  [information only]
      barrel  4A8B_lampmid6_ottoman_clutter_01 #1: missed -> found
      barrel  4A8B_lampmid6_ottoman_clutter_01 #4: missed -> found
      barrel  4A8B_lampmid6_ottoman_core_01 #3: missed -> found
  4A8B_lampmid6_wood  found 1.0 -> 16.0 of 21 placements (+15.0) [per frame 1 -> 16 of 21]; boxes not on their barrel 0.0 -> 1.0 (+1.0): lower, within the margin  [information only]
      barrel  4A8B_lampmid6_wood_cluster_01 #1: missed -> found
      barrel  4A8B_lampmid6_wood_cluster_01 #2: missed -> found
      barrel  4A8B_lampmid6_wood_cluster_01 #3: missed -> found
      barrel  4A8B_lampmid6_wood_cluster_01 #4: missed -> found
      barrel  4A8B_lampmid6_wood_clutter_01 #1: missed -> found
      barrel  4A8B_lampmid6_wood_clutter_01 #2: missed -> found
      barrel  4A8B_lampmid6_wood_clutter_01 #3: missed -> found
      barrel  4A8B_lampmid6_wood_clutter_01 #4: missed -> found
      barrel  4A8B_lampmid6_wood_core_01 #2: missed -> found
      barrel  4A8B_lampmid6_wood_core_01 #3: missed -> found
      barrel  4A8B_lampmid6_wood_core_01 #4: missed -> found
      barrel  4A8B_lampmid6_wood_occl_02 #1: missed -> found
      barrel  4A8B_lampmid6_wood_occl_02 #2: missed -> found
      barrel  4A8B_lampmid6_wood_occl_04 #1: missed -> off
      barrel  4A8B_lampmid6_wood_occl_04 #2: missed -> found
      barrel  4A8B_lampmid6_wood_touch_02 #1: missed -> off
      barrel  4A8B_lampmid6_wood_touch_02 #2: missed -> found
      boxes   4A8B_lampmid6_wood_cluster_01: nothing 0 -> 1
  4A8B_lampwarm3_wood  found 1.0 -> 12.0 of 21 placements (+11.0) [per frame 1 -> 12 of 21]; boxes not on their barrel 0.0 -> 0.0: better  [information only]
      barrel  4A8B_lampwarm3_wood_cluster_01 #1: missed -> found
      barrel  4A8B_lampwarm3_wood_cluster_01 #3: missed -> found
      barrel  4A8B_lampwarm3_wood_cluster_01 #4: missed -> found
      barrel  4A8B_lampwarm3_wood_clutter_01 #1: missed -> found
      barrel  4A8B_lampwarm3_wood_clutter_01 #2: missed -> found
      barrel  4A8B_lampwarm3_wood_core_01 #2: missed -> found
      barrel  4A8B_lampwarm3_wood_core_01 #3: missed -> found
      barrel  4A8B_lampwarm3_wood_core_01 #4: missed -> found
      barrel  4A8B_lampwarm3_wood_occl_02 #2: missed -> found
      barrel  4A8B_lampwarm3_wood_occl_04 #2: missed -> found
      barrel  4A8B_lampwarm3_wood_touch_02 #1: missed -> found
      barrel  4A8B_lampwarm3_wood_touch_02 #2: missed -> off
  4A8B_lampwarm6_bathtile  found 1.0 -> 13.0 of 15 placements (+12.0) [per frame 1 -> 13 of 15]; boxes not on their barrel 0.0 -> 1.0 (+1.0): lower, within the margin  [information only]
      barrel  4A8B_lampwarm6_bathtile_clutter_01 #1: missed -> found
      barrel  4A8B_lampwarm6_bathtile_clutter_01 #2: missed -> found
      barrel  4A8B_lampwarm6_bathtile_clutter_01 #3: missed -> found
      barrel  4A8B_lampwarm6_bathtile_clutter_01 #4: missed -> found
      barrel  4A8B_lampwarm6_bathtile_core_01 #1: missed -> found
      barrel  4A8B_lampwarm6_bathtile_core_01 #2: missed -> found
      barrel  4A8B_lampwarm6_bathtile_core_01 #3: missed -> found
      barrel  4A8B_lampwarm6_bathtile_core_01 #4: missed -> found
      barrel  4A8B_lampwarm6_bathtile_edge_01 #2: missed -> found
      barrel  4A8B_lampwarm6_bathtile_touch_01 #1: missed -> found
      barrel  4A8B_lampwarm6_bathtile_touch_01 #2: missed -> found
      barrel  4A8B_lampwarm6_bathtile_touch_01 #3: missed -> found
      boxes   4A8B_lampwarm6_bathtile_core_01: wrong color 0 -> 1
  4A8B_lampwarm6_ottoman  found 0.0 -> 9.0 of 15 placements (+9.0) [per frame 0 -> 9 of 15]; boxes not on their barrel 1.0 -> 1.0: better  [information only]
      barrel  4A8B_lampwarm6_ottoman_clutter_01 #1: missed -> found
      barrel  4A8B_lampwarm6_ottoman_clutter_01 #3: missed -> found
      barrel  4A8B_lampwarm6_ottoman_clutter_01 #4: missed -> found
      barrel  4A8B_lampwarm6_ottoman_core_01 #1: missed -> found
      barrel  4A8B_lampwarm6_ottoman_core_01 #3: missed -> found
      barrel  4A8B_lampwarm6_ottoman_core_01 #4: missed -> found
      barrel  4A8B_lampwarm6_ottoman_edge_01 #1: missed -> found
      barrel  4A8B_lampwarm6_ottoman_edge_01 #2: missed -> found
      barrel  4A8B_lampwarm6_ottoman_touch_01 #3: missed -> found
  4A8B_lampwarm6_wood  found 0.0 -> 13.0 of 21 placements (+13.0) [per frame 0 -> 13 of 21]; boxes not on their barrel 1.0 -> 2.0 (+1.0): lower, within the margin  [information only]
      barrel  4A8B_lampwarm6_wood_cluster_01 #1: missed -> found
      barrel  4A8B_lampwarm6_wood_cluster_01 #2: missed -> found
      barrel  4A8B_lampwarm6_wood_cluster_01 #3: missed -> found
      barrel  4A8B_lampwarm6_wood_cluster_01 #4: missed -> off
      barrel  4A8B_lampwarm6_wood_clutter_01 #1: missed -> found
      barrel  4A8B_lampwarm6_wood_clutter_01 #3: missed -> found
      barrel  4A8B_lampwarm6_wood_clutter_01 #4: missed -> found
      barrel  4A8B_lampwarm6_wood_core_01 #2: missed -> found
      barrel  4A8B_lampwarm6_wood_core_01 #3: missed -> found
      barrel  4A8B_lampwarm6_wood_core_01 #4: missed -> found
      barrel  4A8B_lampwarm6_wood_occl_02 #1: missed -> off
      barrel  4A8B_lampwarm6_wood_occl_02 #2: missed -> found
      barrel  4A8B_lampwarm6_wood_occl_04 #1: missed -> off
      barrel  4A8B_lampwarm6_wood_occl_04 #2: missed -> found
      barrel  4A8B_lampwarm6_wood_touch_02 #1: missed -> found
      barrel  4A8B_lampwarm6_wood_touch_02 #2: missed -> found
      boxes   4A8B_lampwarm6_wood_cluster_01: wrong color 0 -> 1
  DAVE_office_speckle  found 17.0 -> 23.0 of 34 placements (+6.0) [per frame 17 -> 23 of 34]; boxes not on their barrel 4.0 -> 11.0 (+7.0): WORSE  [information only]
      barrel  DAVE_office_speckle_snap_00 #2: missed -> off
      barrel  DAVE_office_speckle_snap_02 #1: missed -> found
      barrel  DAVE_office_speckle_snap_04 #1: missed -> found
      barrel  DAVE_office_speckle_snap_04 #2: missed -> off
      barrel  DAVE_office_speckle_snap_05 #2: missed -> found
      barrel  DAVE_office_speckle_snap_07 #2: missed -> found
      barrel  DAVE_office_speckle_snap_07 #4: missed -> found
      barrel  DAVE_office_speckle_snap_11 #3: missed -> found
      boxes   DAVE_office_speckle_snap_00: second 0 -> 1
      boxes   DAVE_office_speckle_snap_04: second 0 -> 1
      boxes   DAVE_office_speckle_snap_05: second 0 -> 1
      boxes   DAVE_office_speckle_snap_06: wrong color 0 -> 1
      boxes   DAVE_office_speckle_snap_07: wrong color 0 -> 1
      boxes   DAVE_office_speckle_snap_10: second 0 -> 1
      boxes   DAVE_office_speckle_snap_11: wrong color 0 -> 1
  unchanged: 5 set(s) (4A8B_lampcool1_wood, 4A8B_lampmid1_wood, 4A8B_lampmid3_ottoman, 4A8B_lampwarm1_wood, 4A8B_window_black)

RESULT: PASS. No protected set is worse than the baseline by more than its margin, and no clean empty frame gained a box.
```
