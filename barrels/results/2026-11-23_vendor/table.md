# Ours (candidate) against the vendor (baseline)

```
                                       |          CANDIDATE           |           BASELINE           |     DELTA (cand - base)      |      score      | negF
set/scenario                  frm brls | found miss false width   bot | found miss false width   bot | found miss false width   bot | cand base delta | c/b
-----------------------------------------------------------------------------------------------------------------------------------------------------------
  close                         1    1 |     1    0     0  1.00   0.0 |     1    0     0  1.12  12.0 |     .    .     . -0.12 -12.0 |                 |
  clutter                       1    4 |     3    1     2  0.97   3.0 |     4    0     0  1.08   2.0 |    -1   +1    +2 -0.10  +1.0 |                 |
  core                          1    4 |     2    2     0  0.90   1.0 |     4    0     0  1.13   3.5 |    -2   +2     . -0.23  -2.5 |                 |
  edge                          1    2 |     1    1     0  0.98   9.0 |     2    0     0  0.96   4.5 |    -1   +1     . +0.02  +4.5 |                 |
  held                          1    1 |     1    0     0  1.01   0.0 |     1    0     0  0.91   6.0 |     .    .     . +0.10  -6.0 |                 |
  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    1 |     1    0     0  0.95   2.0 |     1    0     0  0.96   1.0 |     .    .     . -0.02  +1.0 |                 |
  touch                         1    3 |     1    2     0  1.08   1.0 |     3    0     0  1.17   5.0 |    -2   +2     . -0.09  -4.0 |                 |
4A8B_both_abpgray all           8   16 |    10    6     2  0.98   1.5 |    16    0     0  1.09   3.0 |    -6   +6    +2 -0.12  -1.5 | 0.68 1.00 -0.32 | 0/0

  close                         1    1 |     0    1     0     -     - |     1    0     0  1.02   0.0 |    -1   +1     .     -     - |                 |
  clutter                       1    4 |     0    4     0     -     - |     2    2     1  1.06   1.5 |    -2   +2    -1     -     - |                 |
  core                          1    4 |     1    3     0  0.88   2.0 |     4    0     0  0.98   2.5 |    -3   +3     . -0.10  -0.5 |                 |
  edge                          1    2 |     0    2     0     -     - |     2    0     0  1.07   4.0 |    -2   +2     .     -     - |                 |
  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    1 |     0    1     0     -     - |     1    0     0  0.72   0.0 |    -1   +1     .     -     - |                 |
  touch                         1    3 |     2    1     0  1.11   1.0 |     3    0     0  1.00   2.0 |    -1   +1     . +0.11  -1.0 |                 |
4A8B_lampcool6_ottoman all      7   15 |     3   12     0  0.94   1.0 |    13    2     1  1.02   2.0 |   -10  +10    -1 -0.09  -1.0 | 0.33 0.90 -0.57 | 0/0

  close                         1    1 |     1    0     0  0.79   0.0 |     1    0     0  1.02  16.0 |     .    .     . -0.23 -16.0 |                 |
  clutter                       1    4 |     0    4     1     -     - |     2    2     1  0.93   1.5 |    -2   +2     .     -     - |                 |
  core                          1    4 |     0    4     0     -     - |     3    1     0  0.96   4.0 |    -3   +3     .     -     - |                 |
  edge                          1    2 |     0    2     0     -     - |     2    0     0  0.94   3.0 |    -2   +2     .     -     - |                 |
  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    1 |     0    1     0     -     - |     0    1     0     -     - |     .    .     .     -     - |                 |
  touch                         1    3 |     0    3     0     -     - |     2    1     0  0.98   3.5 |    -2   +2     .     -     - |                 |
4A8B_lampmid3_ottoman all       7   15 |     1   14     1  0.79   0.0 |    10    5     1  0.97   3.0 |    -9   +9     . -0.18  -3.0 | 0.11 0.76 -0.65 | 0/0

  close                         1    1 |     0    1     0     -     - |     1    0     0  1.04   2.0 |    -1   +1     .     -     - |                 |
  clutter                       1    4 |     1    3     0  0.99   3.0 |     2    2     1  1.09   1.5 |    -1   +1    -1 -0.11  +1.5 |                 |
  core                          1    4 |     2    2     0  0.95   0.5 |     4    0     0  1.09   3.5 |    -2   +2     . -0.14  -3.0 |                 |
  edge                          1    2 |     1    1     0  0.96   1.0 |     2    0     0  1.05   3.0 |    -1   +1     . -0.08  -2.0 |                 |
  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    1 |     0    1     0     -     - |     1    0     0  0.72   0.0 |    -1   +1     .     -     - |                 |
  touch                         1    3 |     2    1     0  1.13   2.0 |     3    0     0  1.14   2.0 |    -1   +1     . -0.01     . |                 |
4A8B_lampmid6_ottoman all       7   15 |     6    9     0  1.00   1.0 |    13    2     1  1.06   2.0 |    -7   +7    -1 -0.05  -1.0 | 0.51 0.90 -0.39 | 0/0

  close                         1    1 |     0    1     0     -     - |     1    0     0  1.16  24.0 |    -1   +1     .     -     - |                 |
  clutter                       1    4 |     0    4     0     -     - |     2    2     0  1.09   1.5 |    -2   +2     .     -     - |                 |
  core                          1    4 |     0    4     1     -     - |     3    1     0  1.03   3.0 |    -3   +3    +1     -     - |                 |
  edge                          1    2 |     0    2     0     -     - |     2    0     0  1.02   3.0 |    -2   +2     .     -     - |                 |
  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    1 |     0    1     0     -     - |     0    1     0     -     - |     .    .     .     -     - |                 |
  touch                         1    3 |     0    3     0     -     - |     3    0     0  1.17   2.0 |    -3   +3     .     -     - |                 |
4A8B_lampwarm6_ottoman all      7   15 |     0   15     1     -     - |    11    4     0  1.14   3.0 |   -11  +11    +1     -     - | 0.00 0.85 -0.85 | 0/0

  close                         1    1 |     0    1     0     -     - |     0    1     0     -     - |     .    .     .     -     - |                 |
  clutter                       1    4 |     4    0     0  0.94   4.0 |     3    1     0  1.11   2.0 |    +1   -1     . -0.17  +2.0 |                 |
  core                          1    4 |     4    0     1  0.91   1.5 |     4    0     0  1.19   2.5 |     .    .    +1 -0.28  -1.0 |                 |
  edge                          1    2 |     1    1     0  1.06   3.0 |     2    0     0  1.08   1.0 |    -1   +1     . -0.02  +2.0 |                 |
  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    1 |     0    1     0     -     - |     1    0     0  0.77   4.0 |    -1   +1     .     -     - |                 |
  touch                         1    3 |     3    0     0  1.06   2.0 |     2    1     1  1.16   0.5 |    +1   -1    -1 -0.10  +1.5 |                 |
4A8B_overheaddim_palewood all   7   15 |    12    3     1  0.97   2.0 |    12    3     1  1.14   2.0 |     .    .     . -0.17     . | 0.87 0.87     . | 0/0

  occlx                        17   32 |    26    6     2  0.94   1.0 |    24    8     4  1.05   2.0 |    +2   -2    -2 -0.10  -1.0 |                 |
4A8B_window_abpwhite all       17   32 |    26    6     2  0.94   1.0 |    24    8     4  1.05   2.0 |    +2   -2    -2 -0.10  -1.0 | 0.85 0.77 +0.08 | 1/1

-----------------------------------------------------------------------------------------------------------------------------------------------------------
ALL all                        60  123 |    58   65     7  0.95   1.0 |    99   24     8  1.06   2.0 |   -41  +41    -1 -0.11  -1.0 |                 | 1/1
-----------------------------------------------------------------------------------------------------------------------------------------------------------
candidate = 2026-11-09_hs_candidate/config.json; DetConfig defaults
baseline  = the robot's built-in detector (vendor), its boxes as saved with each frame in data/vendor/<stem>_vendor.json
delta = candidate - baseline ('.' = no change). Frames: train split only, test frames never opened; 4A8B_both_abpgray 8,
    4A8B_lampcool6_ottoman 7, 4A8B_lampmid3_ottoman 7, 4A8B_lampmid6_ottoman 7, 4A8B_lampwarm6_ottoman 7,
    4A8B_overheaddim_palewood 7, 4A8B_window_abpwhite 17. git e0d01e0; nan s.
Rule: EVAL.md v2, as eval_det implements it — a box is right when same color, IoU >= 0.5 and bottom edge within max(3
    px, 10 % of the true height).
found / miss = true barrels with / without a right box; false = boxes that match no barrel; width = median box width /
    true width over the found;
bot = median |bottom-edge error| in px over the found; score = mean of the orange and blue F1 (pooled over the set's
    frames), on the set rows only.
negF c/b = false boxes on empty (negative) frames, candidate/baseline; DQ:c / DQ:b = that arm drew a box on a CLEAN
    empty frame, which disqualifies it.
VENDOR COMPARISON: both arms are scored on the frames that have a vendor file, and only on those (60 of 209 frames):
    HOME 0 of 16, CAMPUS 0 of 21, 4A8B_both_abpgray 8 of 8, 4A8B_lampcool1_wood 0 of 10, 4A8B_lampcool3_wood 0 of 10,
    4A8B_lampcool6_ottoman 7 of 7, 4A8B_lampcool6_wood 0 of 10, 4A8B_lampmid1_wood 0 of 10, 4A8B_lampmid3_ottoman 7 of
    7, 4A8B_lampmid3_wood 0 of 10, 4A8B_lampmid6_ottoman 7 of 7, 4A8B_lampmid6_wood 0 of 10, 4A8B_lampwarm1_wood 0 of
    10, 4A8B_lampwarm3_wood 0 of 10, 4A8B_lampwarm6_ottoman 7 of 7, 4A8B_lampwarm6_wood 0 of 10,
    4A8B_overheaddim_palewood 7 of 7, 4A8B_window_abpwhite 17 of 17, 4A8B_window_black 0 of 10, DAVE* 0 of 12.
Left out, for both arms: 149 with no vendor file.
Vendor objects that are not barrels (ball, robot, tag) are ignored: 1. Vendor barrels without a usable box, ignored: 0.
Caveat: the vendor may not draw its boxes the way our labels are drawn (how tight, whether the whole barrel is covered),
    so the v2 rule may be harsh on it. Read the looser counts below next to the strict ones; the score is the strict
    one.

LOOSER COUNTS per set, candidate/baseline (reporting only: the table and the score above are the v2 rule, unchanged)
set                           brls | strict c/b | overlap c/b false c/b | place c/b false c/b
---------------------------------------------------------------------------------------------
4A8B_both_abpgray all           16 |      10/16 |       11/16       1/0 |     11/16       1/0
4A8B_lampcool6_ottoman all      15 |       3/13 |        3/14       0/0 |      3/14       0/0
4A8B_lampmid3_ottoman all       15 |       1/10 |        2/11       0/0 |      2/11       0/0
4A8B_lampmid6_ottoman all       15 |       6/13 |        6/14       0/0 |      6/14       0/0
4A8B_lampwarm6_ottoman all      15 |       0/11 |        0/11       1/0 |      0/11       1/0
4A8B_overheaddim_palewood all   15 |      12/12 |       12/13       1/0 |     12/13       1/0
4A8B_window_abpwhite all        32 |      26/24 |       26/26       2/2 |     26/27       2/1
ALL all                        123 |      58/99 |      60/105       5/2 |    60/106       5/1
---------------------------------------------------------------------------------------------
strict = barrels found under the v2 rule (the table above). overlap = same color and IoU >= 0.5, the bottom edge not
    checked. place = same color and the two box centers at most half the true box's width apart (it does not depend on
    how tight a box is). false = boxes left without a barrel under that count.
```
