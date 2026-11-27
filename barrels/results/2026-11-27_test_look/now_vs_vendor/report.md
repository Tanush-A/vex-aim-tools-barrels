# Test look 2026-11-27: now (contrast) vs the vendor

```
                                       |          CANDIDATE           |           BASELINE           |     DELTA (cand - base)      |      score      | negF
set/scenario                  frm brls | found miss false width   bot | found miss false width   bot | found miss false width   bot | cand base delta | c/b
-----------------------------------------------------------------------------------------------------------------------------------------------------------
  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    2 |     2    0     0  1.00   1.5 |     2    0     0  1.07   4.0 |     .    .     . -0.07  -2.5 |                 |
4A8B_both_abpgray all           2    2 |     2    0     0  1.00   1.5 |     2    0     0  1.07   4.0 |     .    .     . -0.07  -2.5 | 1.00 1.00     . | 0/0

  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    2 |     2    0     0  1.05   1.5 |     1    1     1  1.28   1.0 |    +1   -1    -1 -0.23  +0.5 |                 |
4A8B_lampcool6_bathtile all     2    2 |     2    0     0  1.05   1.5 |     1    1     1  1.28   1.0 |    +1   -1    -1 -0.23  +0.5 | 1.00 0.50 +0.50 | 0/0

  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    2 |     2    0     0  0.99   2.5 |     2    0     0  1.15   4.0 |     .    .     . -0.15  -1.5 |                 |
4A8B_lampcool6_glass all        2    2 |     2    0     0  0.99   2.5 |     2    0     0  1.15   4.0 |     .    .     . -0.15  -1.5 | 1.00 1.00     . | 0/0

  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    2 |     1    1     0  0.91   2.0 |     2    0     0  1.01   5.0 |    -1   +1     . -0.11  -3.0 |                 |
4A8B_lampcool6_ottoman all      2    2 |     1    1     0  0.91   2.0 |     2    0     0  1.01   5.0 |    -1   +1     . -0.11  -3.0 | 0.50 1.00 -0.50 | 0/0

  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    2 |     2    0     0  0.99   3.0 |     1    1     0  1.42   3.0 |    +1   -1     . -0.43     . |                 |
4A8B_lampmid3_bathtile all      2    2 |     2    0     0  0.99   3.0 |     1    1     0  1.42   3.0 |    +1   -1     . -0.43     . | 1.00 0.50 +0.50 | 0/0

  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    2 |     1    1     1  1.07   0.0 |     2    0     0  1.15   3.0 |    -1   +1    +1 -0.07  -3.0 |                 |
4A8B_lampmid3_glass all         2    2 |     1    1     1  1.07   0.0 |     2    0     0  1.15   3.0 |    -1   +1    +1 -0.07  -3.0 | 0.50 1.00 -0.50 | 0/0

  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    2 |     0    2     0     -     - |     1    1     1  1.04   7.0 |    -1   +1    -1     -     - |                 |
4A8B_lampmid3_ottoman all       2    2 |     0    2     0     -     - |     1    1     1  1.04   7.0 |    -1   +1    -1     -     - | 0.00 0.50 -0.50 | 0/0

  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    2 |     0    2     1     -     - |     1    1     0  1.20   3.0 |    -1   +1    +1     -     - |                 |
4A8B_lampmid6_bathtile all      2    2 |     0    2     1     -     - |     1    1     0  1.20   3.0 |    -1   +1    +1     -     - | 0.00 0.50 -0.50 | 0/0

  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    2 |     1    1     1  1.07   1.0 |     2    0     0  1.15   4.0 |    -1   +1    +1 -0.07  -3.0 |                 |
4A8B_lampmid6_glass all         2    2 |     1    1     1  1.07   1.0 |     2    0     0  1.15   4.0 |    -1   +1    +1 -0.07  -3.0 | 0.50 1.00 -0.50 | 0/0

  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    2 |     1    1     0  1.04   4.0 |     2    0     0  1.12   4.0 |    -1   +1     . -0.08     . |                 |
4A8B_lampmid6_ottoman all       2    2 |     1    1     0  1.04   4.0 |     2    0     0  1.12   4.0 |    -1   +1     . -0.08     . | 0.50 1.00 -0.50 | 0/0

  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    2 |     1    1     0  1.00   0.0 |     0    2     0     -     - |    +1   -1     .     -     - |                 |
4A8B_lampwarm6_bathtile all     2    2 |     1    1     0  1.00   0.0 |     0    2     0     -     - |    +1   -1     .     -     - | 0.50 0.00 +0.50 | 0/0

  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    2 |     1    1     0  1.05   2.0 |     1    1     1  1.12   3.0 |     .    .    -1 -0.07  -1.0 |                 |
4A8B_lampwarm6_glass all        2    2 |     1    1     0  1.05   2.0 |     1    1     1  1.12   3.0 |     .    .    -1 -0.07  -1.0 | 0.50 0.50     . | 0/0

  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    2 |     0    2     0     -     - |     2    0     0  1.11   7.0 |    -2   +2     .     -     - |                 |
4A8B_lampwarm6_ottoman all      2    2 |     0    2     0     -     - |     2    0     0  1.11   7.0 |    -2   +2     .     -     - | 0.00 1.00 -1.00 | 0/0

  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    2 |     1    1     0  1.07   3.0 |     1    1     1  1.18   1.0 |     .    .    -1 -0.12  +2.0 |                 |
4A8B_overheaddim_palewood all   2    2 |     1    1     0  1.07   3.0 |     1    1     1  1.18   1.0 |     .    .    -1 -0.12  +2.0 | 0.50 0.50     . | 0/0

  occlx                         1    2 |     2    0     0  0.94   1.0 |     2    0     0  1.06   2.0 |     .    .     . -0.12  -1.0 |                 |
4A8B_window_abpwhite all        1    2 |     2    0     0  0.94   1.0 |     2    0     0  1.06   2.0 |     .    .     . -0.12  -1.0 | 1.00 1.00     . | 0/0

  neg                           1    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl                          1    2 |     1    1     1  1.10   3.0 |     1    1     1  1.12   3.0 |     .    .     . -0.02     . |                 |
4A8B_window_glass all           2    2 |     1    1     1  1.10   3.0 |     1    1     1  1.12   3.0 |     .    .     . -0.02     . | 0.50 0.50     . | 0/0

-----------------------------------------------------------------------------------------------------------------------------------------------------------
ALL all                        31   32 |    18   14     4  1.03   2.0 |    23    9     5  1.12   3.0 |    -5   +5    -1 -0.09  -1.0 |                 | 0/0
-----------------------------------------------------------------------------------------------------------------------------------------------------------
candidate = 2026-11-09_hs_candidate/config.json; DetConfig defaults
baseline  = the robot's built-in detector (vendor), its boxes as saved with each frame in data/vendor/<stem>_vendor.json
delta = candidate - baseline ('.' = no change). Frames: test split only (a PLANNED test look); 4A8B_both_abpgray 2,
    4A8B_lampcool6_bathtile 2, 4A8B_lampcool6_glass 2, 4A8B_lampcool6_ottoman 2, 4A8B_lampmid3_bathtile 2,
    4A8B_lampmid3_glass 2, 4A8B_lampmid3_ottoman 2, 4A8B_lampmid6_bathtile 2, 4A8B_lampmid6_glass 2,
    4A8B_lampmid6_ottoman 2, 4A8B_lampwarm6_bathtile 2, 4A8B_lampwarm6_glass 2, 4A8B_lampwarm6_ottoman 2,
    4A8B_overheaddim_palewood 2, 4A8B_window_abpwhite 1, 4A8B_window_glass 2. git 9d43df8; 5.2 s.
Rule: EVAL.md v2, as eval_det implements it — a box is right when same color, IoU >= 0.5 and bottom edge within max(3
    px, 10 % of the true height).
found / miss = true barrels with / without a right box; false = boxes that match no barrel; width = median box width /
    true width over the found;
bot = median |bottom-edge error| in px over the found; score = mean of the orange and blue F1 (pooled over the set's
    frames), on the set rows only.
negF c/b = false boxes on empty (negative) frames, candidate/baseline; DQ:c / DQ:b = that arm drew a box on a CLEAN
    empty frame, which disqualifies it.
VENDOR COMPARISON: both arms are scored on the frames that have a vendor file, and only on those (31 of 78 frames): HOME
    0 of 5, CAMPUS 0 of 10, 4A8B_both_abpgray 2 of 2, 4A8B_lampcool1_wood 0 of 3, 4A8B_lampcool3_wood 0 of 3,
    4A8B_lampcool6_bathtile 2 of 2, 4A8B_lampcool6_glass 2 of 2, 4A8B_lampcool6_ottoman 2 of 2, 4A8B_lampcool6_wood 0 of
    3, 4A8B_lampmid1_wood 0 of 3, 4A8B_lampmid3_bathtile 2 of 2, 4A8B_lampmid3_glass 2 of 2, 4A8B_lampmid3_ottoman 2 of
    2, 4A8B_lampmid3_wood 0 of 3, 4A8B_lampmid6_bathtile 2 of 2, 4A8B_lampmid6_glass 2 of 2, 4A8B_lampmid6_ottoman 2 of
    2, 4A8B_lampmid6_wood 0 of 3, 4A8B_lampwarm1_wood 0 of 3, 4A8B_lampwarm3_wood 0 of 3, 4A8B_lampwarm6_bathtile 2 of
    2, 4A8B_lampwarm6_glass 2 of 2, 4A8B_lampwarm6_ottoman 2 of 2, 4A8B_lampwarm6_wood 0 of 3, 4A8B_overheaddim_palewood
    2 of 2, 4A8B_window_abpwhite 1 of 1, 4A8B_window_black 0 of 5, 4A8B_window_glass 2 of 2.
Left out, for both arms: 47 with no vendor file.
Vendor objects that are not barrels (ball, robot, tag) are ignored: 1. Vendor barrels without a usable box, ignored: 0.
Caveat: the vendor may not draw its boxes the way our labels are drawn (how tight, whether the whole barrel is covered),
    so the v2 rule may be harsh on it. Read the looser counts below next to the strict ones; the score is the strict
    one.

LOOSER COUNTS per set, candidate/baseline (reporting only: the table and the score above are the v2 rule, unchanged)
set                           brls | strict c/b | overlap c/b false c/b | place c/b false c/b
---------------------------------------------------------------------------------------------
4A8B_both_abpgray all            2 |        2/2 |         2/2       0/0 |       2/2       0/0
4A8B_lampcool6_bathtile all      2 |        2/1 |         2/2       0/0 |       2/2       0/0
4A8B_lampcool6_glass all         2 |        2/2 |         2/2       0/0 |       2/2       0/0
4A8B_lampcool6_ottoman all       2 |        1/2 |         1/2       0/0 |       1/2       0/0
4A8B_lampmid3_bathtile all       2 |        2/1 |         2/1       0/0 |       2/1       0/0
4A8B_lampmid3_glass all          2 |        1/2 |         1/2       1/0 |       1/2       1/0
4A8B_lampmid3_ottoman all        2 |        0/1 |         0/1       0/1 |       0/2       0/0
4A8B_lampmid6_bathtile all       2 |        0/1 |         1/1       0/0 |       1/1       0/0
4A8B_lampmid6_glass all          2 |        1/2 |         1/2       1/0 |       1/2       1/0
4A8B_lampmid6_ottoman all        2 |        1/2 |         1/2       0/0 |       1/2       0/0
4A8B_lampwarm6_bathtile all      2 |        1/0 |         1/0       0/0 |       1/0       0/0
4A8B_lampwarm6_glass all         2 |        1/1 |         1/2       0/0 |       1/2       0/0
4A8B_lampwarm6_ottoman all       2 |        0/2 |         0/2       0/0 |       0/2       0/0
4A8B_overheaddim_palewood all    2 |        1/1 |         1/2       0/0 |       1/2       0/0
4A8B_window_abpwhite all         2 |        2/2 |         2/2       0/0 |       2/2       0/0
4A8B_window_glass all            2 |        1/1 |         2/2       0/0 |       2/2       0/0
ALL all                         32 |      18/23 |       20/27       2/1 |     20/28       2/0
---------------------------------------------------------------------------------------------
strict = barrels found under the v2 rule (the table above). overlap = same color and IoU >= 0.5, the bottom edge not
    checked. place = same color and the two box centers at most half the true box's width apart (it does not depend on
    how tight a box is). false = boxes left without a barrel under that count.
```

| set / scenario | frames | barrels | cand found | cand miss | cand false | cand width | cand bot | base found | base miss | base false | base width | base bot | Δ found | Δ miss | Δ false | Δ width | Δ bot | score cand | score base | score Δ | negF c/b |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| neg | 1 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 1 | 2 | 2 | 0 | 0 | 1.00 | 1.5 | 2 | 0 | 0 | 1.07 | 4.0 | . | . | . | -0.07 | -2.5 |  |  |  |  |
| **4A8B_both_abpgray all** | **2** | **2** | **2** | **0** | **0** | **1.00** | **1.5** | **2** | **0** | **0** | **1.07** | **4.0** | **.** | **.** | **.** | **-0.07** | **-2.5** | **1.00** | **1.00** | **.** | **0/0** |
| neg | 1 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 1 | 2 | 2 | 0 | 0 | 1.05 | 1.5 | 1 | 1 | 1 | 1.28 | 1.0 | +1 | -1 | -1 | -0.23 | +0.5 |  |  |  |  |
| **4A8B_lampcool6_bathtile all** | **2** | **2** | **2** | **0** | **0** | **1.05** | **1.5** | **1** | **1** | **1** | **1.28** | **1.0** | **+1** | **-1** | **-1** | **-0.23** | **+0.5** | **1.00** | **0.50** | **+0.50** | **0/0** |
| neg | 1 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 1 | 2 | 2 | 0 | 0 | 0.99 | 2.5 | 2 | 0 | 0 | 1.15 | 4.0 | . | . | . | -0.15 | -1.5 |  |  |  |  |
| **4A8B_lampcool6_glass all** | **2** | **2** | **2** | **0** | **0** | **0.99** | **2.5** | **2** | **0** | **0** | **1.15** | **4.0** | **.** | **.** | **.** | **-0.15** | **-1.5** | **1.00** | **1.00** | **.** | **0/0** |
| neg | 1 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 1 | 2 | 1 | 1 | 0 | 0.91 | 2.0 | 2 | 0 | 0 | 1.01 | 5.0 | -1 | +1 | . | -0.11 | -3.0 |  |  |  |  |
| **4A8B_lampcool6_ottoman all** | **2** | **2** | **1** | **1** | **0** | **0.91** | **2.0** | **2** | **0** | **0** | **1.01** | **5.0** | **-1** | **+1** | **.** | **-0.11** | **-3.0** | **0.50** | **1.00** | **-0.50** | **0/0** |
| neg | 1 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 1 | 2 | 2 | 0 | 0 | 0.99 | 3.0 | 1 | 1 | 0 | 1.42 | 3.0 | +1 | -1 | . | -0.43 | . |  |  |  |  |
| **4A8B_lampmid3_bathtile all** | **2** | **2** | **2** | **0** | **0** | **0.99** | **3.0** | **1** | **1** | **0** | **1.42** | **3.0** | **+1** | **-1** | **.** | **-0.43** | **.** | **1.00** | **0.50** | **+0.50** | **0/0** |
| neg | 1 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 1 | 2 | 1 | 1 | 1 | 1.07 | 0.0 | 2 | 0 | 0 | 1.15 | 3.0 | -1 | +1 | +1 | -0.07 | -3.0 |  |  |  |  |
| **4A8B_lampmid3_glass all** | **2** | **2** | **1** | **1** | **1** | **1.07** | **0.0** | **2** | **0** | **0** | **1.15** | **3.0** | **-1** | **+1** | **+1** | **-0.07** | **-3.0** | **0.50** | **1.00** | **-0.50** | **0/0** |
| neg | 1 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 1 | 2 | 0 | 2 | 0 | - | - | 1 | 1 | 1 | 1.04 | 7.0 | -1 | +1 | -1 | - | - |  |  |  |  |
| **4A8B_lampmid3_ottoman all** | **2** | **2** | **0** | **2** | **0** | **-** | **-** | **1** | **1** | **1** | **1.04** | **7.0** | **-1** | **+1** | **-1** | **-** | **-** | **0.00** | **0.50** | **-0.50** | **0/0** |
| neg | 1 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 1 | 2 | 0 | 2 | 1 | - | - | 1 | 1 | 0 | 1.20 | 3.0 | -1 | +1 | +1 | - | - |  |  |  |  |
| **4A8B_lampmid6_bathtile all** | **2** | **2** | **0** | **2** | **1** | **-** | **-** | **1** | **1** | **0** | **1.20** | **3.0** | **-1** | **+1** | **+1** | **-** | **-** | **0.00** | **0.50** | **-0.50** | **0/0** |
| neg | 1 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 1 | 2 | 1 | 1 | 1 | 1.07 | 1.0 | 2 | 0 | 0 | 1.15 | 4.0 | -1 | +1 | +1 | -0.07 | -3.0 |  |  |  |  |
| **4A8B_lampmid6_glass all** | **2** | **2** | **1** | **1** | **1** | **1.07** | **1.0** | **2** | **0** | **0** | **1.15** | **4.0** | **-1** | **+1** | **+1** | **-0.07** | **-3.0** | **0.50** | **1.00** | **-0.50** | **0/0** |
| neg | 1 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 1 | 2 | 1 | 1 | 0 | 1.04 | 4.0 | 2 | 0 | 0 | 1.12 | 4.0 | -1 | +1 | . | -0.08 | . |  |  |  |  |
| **4A8B_lampmid6_ottoman all** | **2** | **2** | **1** | **1** | **0** | **1.04** | **4.0** | **2** | **0** | **0** | **1.12** | **4.0** | **-1** | **+1** | **.** | **-0.08** | **.** | **0.50** | **1.00** | **-0.50** | **0/0** |
| neg | 1 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 1 | 2 | 1 | 1 | 0 | 1.00 | 0.0 | 0 | 2 | 0 | - | - | +1 | -1 | . | - | - |  |  |  |  |
| **4A8B_lampwarm6_bathtile all** | **2** | **2** | **1** | **1** | **0** | **1.00** | **0.0** | **0** | **2** | **0** | **-** | **-** | **+1** | **-1** | **.** | **-** | **-** | **0.50** | **0.00** | **+0.50** | **0/0** |
| neg | 1 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 1 | 2 | 1 | 1 | 0 | 1.05 | 2.0 | 1 | 1 | 1 | 1.12 | 3.0 | . | . | -1 | -0.07 | -1.0 |  |  |  |  |
| **4A8B_lampwarm6_glass all** | **2** | **2** | **1** | **1** | **0** | **1.05** | **2.0** | **1** | **1** | **1** | **1.12** | **3.0** | **.** | **.** | **-1** | **-0.07** | **-1.0** | **0.50** | **0.50** | **.** | **0/0** |
| neg | 1 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 1 | 2 | 0 | 2 | 0 | - | - | 2 | 0 | 0 | 1.11 | 7.0 | -2 | +2 | . | - | - |  |  |  |  |
| **4A8B_lampwarm6_ottoman all** | **2** | **2** | **0** | **2** | **0** | **-** | **-** | **2** | **0** | **0** | **1.11** | **7.0** | **-2** | **+2** | **.** | **-** | **-** | **0.00** | **1.00** | **-1.00** | **0/0** |
| neg | 1 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 1 | 2 | 1 | 1 | 0 | 1.07 | 3.0 | 1 | 1 | 1 | 1.18 | 1.0 | . | . | -1 | -0.12 | +2.0 |  |  |  |  |
| **4A8B_overheaddim_palewood all** | **2** | **2** | **1** | **1** | **0** | **1.07** | **3.0** | **1** | **1** | **1** | **1.18** | **1.0** | **.** | **.** | **-1** | **-0.12** | **+2.0** | **0.50** | **0.50** | **.** | **0/0** |
| occlx | 1 | 2 | 2 | 0 | 0 | 0.94 | 1.0 | 2 | 0 | 0 | 1.06 | 2.0 | . | . | . | -0.12 | -1.0 |  |  |  |  |
| **4A8B_window_abpwhite all** | **1** | **2** | **2** | **0** | **0** | **0.94** | **1.0** | **2** | **0** | **0** | **1.06** | **2.0** | **.** | **.** | **.** | **-0.12** | **-1.0** | **1.00** | **1.00** | **.** | **0/0** |
| neg | 1 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 1 | 2 | 1 | 1 | 1 | 1.10 | 3.0 | 1 | 1 | 1 | 1.12 | 3.0 | . | . | . | -0.02 | . |  |  |  |  |
| **4A8B_window_glass all** | **2** | **2** | **1** | **1** | **1** | **1.10** | **3.0** | **1** | **1** | **1** | **1.12** | **3.0** | **.** | **.** | **.** | **-0.02** | **.** | **0.50** | **0.50** | **.** | **0/0** |
| **ALL all** | **31** | **32** | **18** | **14** | **4** | **1.03** | **2.0** | **23** | **9** | **5** | **1.12** | **3.0** | **-5** | **+5** | **-1** | **-0.09** | **-1.0** |  |  |  | **0/0** |

- candidate = 2026-11-09_hs_candidate/config.json; DetConfig defaults
- baseline  = the robot's built-in detector (vendor), its boxes as saved with each frame in data/vendor/<stem>_vendor.json
- delta = candidate - baseline ('.' = no change). Frames: test split only (a PLANNED test look); 4A8B_both_abpgray 2, 4A8B_lampcool6_bathtile 2, 4A8B_lampcool6_glass 2, 4A8B_lampcool6_ottoman 2, 4A8B_lampmid3_bathtile 2, 4A8B_lampmid3_glass 2, 4A8B_lampmid3_ottoman 2, 4A8B_lampmid6_bathtile 2, 4A8B_lampmid6_glass 2, 4A8B_lampmid6_ottoman 2, 4A8B_lampwarm6_bathtile 2, 4A8B_lampwarm6_glass 2, 4A8B_lampwarm6_ottoman 2, 4A8B_overheaddim_palewood 2, 4A8B_window_abpwhite 1, 4A8B_window_glass 2. git 9d43df8; 5.2 s.
- Rule: EVAL.md v2, as eval_det implements it — a box is right when same color, IoU >= 0.5 and bottom edge within max(3 px, 10 % of the true height).
- found / miss = true barrels with / without a right box; false = boxes that match no barrel; width = median box width / true width over the found;
- bot = median |bottom-edge error| in px over the found; score = mean of the orange and blue F1 (pooled over the set's frames), on the set rows only.
- negF c/b = false boxes on empty (negative) frames, candidate/baseline; DQ:c / DQ:b = that arm drew a box on a CLEAN empty frame, which disqualifies it.
- VENDOR COMPARISON: both arms are scored on the frames that have a vendor file, and only on those (31 of 78 frames): HOME 0 of 5, CAMPUS 0 of 10, 4A8B_both_abpgray 2 of 2, 4A8B_lampcool1_wood 0 of 3, 4A8B_lampcool3_wood 0 of 3, 4A8B_lampcool6_bathtile 2 of 2, 4A8B_lampcool6_glass 2 of 2, 4A8B_lampcool6_ottoman 2 of 2, 4A8B_lampcool6_wood 0 of 3, 4A8B_lampmid1_wood 0 of 3, 4A8B_lampmid3_bathtile 2 of 2, 4A8B_lampmid3_glass 2 of 2, 4A8B_lampmid3_ottoman 2 of 2, 4A8B_lampmid3_wood 0 of 3, 4A8B_lampmid6_bathtile 2 of 2, 4A8B_lampmid6_glass 2 of 2, 4A8B_lampmid6_ottoman 2 of 2, 4A8B_lampmid6_wood 0 of 3, 4A8B_lampwarm1_wood 0 of 3, 4A8B_lampwarm3_wood 0 of 3, 4A8B_lampwarm6_bathtile 2 of 2, 4A8B_lampwarm6_glass 2 of 2, 4A8B_lampwarm6_ottoman 2 of 2, 4A8B_lampwarm6_wood 0 of 3, 4A8B_overheaddim_palewood 2 of 2, 4A8B_window_abpwhite 1 of 1, 4A8B_window_black 0 of 5, 4A8B_window_glass 2 of 2.
- Left out, for both arms: 47 with no vendor file.
- Vendor objects that are not barrels (ball, robot, tag) are ignored: 1. Vendor barrels without a usable box, ignored: 0.
- Caveat: the vendor may not draw its boxes the way our labels are drawn (how tight, whether the whole barrel is covered), so the v2 rule may be harsh on it. Read the looser counts below next to the strict ones; the score is the strict one.

## Looser counts (reporting only; candidate / baseline)

| set / scenario | barrels | strict found | overlap found | overlap false | place found | place false |
|---|---:|---:|---:|---:|---:|---:|
| neg | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| occl | 2 | 2 / 2 | 2 / 2 | 0 / 0 | 2 / 2 | 0 / 0 |
| **4A8B_both_abpgray all** | **2** | **2 / 2** | **2 / 2** | **0 / 0** | **2 / 2** | **0 / 0** |
| neg | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| occl | 2 | 2 / 1 | 2 / 2 | 0 / 0 | 2 / 2 | 0 / 0 |
| **4A8B_lampcool6_bathtile all** | **2** | **2 / 1** | **2 / 2** | **0 / 0** | **2 / 2** | **0 / 0** |
| neg | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| occl | 2 | 2 / 2 | 2 / 2 | 0 / 0 | 2 / 2 | 0 / 0 |
| **4A8B_lampcool6_glass all** | **2** | **2 / 2** | **2 / 2** | **0 / 0** | **2 / 2** | **0 / 0** |
| neg | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| occl | 2 | 1 / 2 | 1 / 2 | 0 / 0 | 1 / 2 | 0 / 0 |
| **4A8B_lampcool6_ottoman all** | **2** | **1 / 2** | **1 / 2** | **0 / 0** | **1 / 2** | **0 / 0** |
| neg | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| occl | 2 | 2 / 1 | 2 / 1 | 0 / 0 | 2 / 1 | 0 / 0 |
| **4A8B_lampmid3_bathtile all** | **2** | **2 / 1** | **2 / 1** | **0 / 0** | **2 / 1** | **0 / 0** |
| neg | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| occl | 2 | 1 / 2 | 1 / 2 | 1 / 0 | 1 / 2 | 1 / 0 |
| **4A8B_lampmid3_glass all** | **2** | **1 / 2** | **1 / 2** | **1 / 0** | **1 / 2** | **1 / 0** |
| neg | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| occl | 2 | 0 / 1 | 0 / 1 | 0 / 1 | 0 / 2 | 0 / 0 |
| **4A8B_lampmid3_ottoman all** | **2** | **0 / 1** | **0 / 1** | **0 / 1** | **0 / 2** | **0 / 0** |
| neg | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| occl | 2 | 0 / 1 | 1 / 1 | 0 / 0 | 1 / 1 | 0 / 0 |
| **4A8B_lampmid6_bathtile all** | **2** | **0 / 1** | **1 / 1** | **0 / 0** | **1 / 1** | **0 / 0** |
| neg | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| occl | 2 | 1 / 2 | 1 / 2 | 1 / 0 | 1 / 2 | 1 / 0 |
| **4A8B_lampmid6_glass all** | **2** | **1 / 2** | **1 / 2** | **1 / 0** | **1 / 2** | **1 / 0** |
| neg | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| occl | 2 | 1 / 2 | 1 / 2 | 0 / 0 | 1 / 2 | 0 / 0 |
| **4A8B_lampmid6_ottoman all** | **2** | **1 / 2** | **1 / 2** | **0 / 0** | **1 / 2** | **0 / 0** |
| neg | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| occl | 2 | 1 / 0 | 1 / 0 | 0 / 0 | 1 / 0 | 0 / 0 |
| **4A8B_lampwarm6_bathtile all** | **2** | **1 / 0** | **1 / 0** | **0 / 0** | **1 / 0** | **0 / 0** |
| neg | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| occl | 2 | 1 / 1 | 1 / 2 | 0 / 0 | 1 / 2 | 0 / 0 |
| **4A8B_lampwarm6_glass all** | **2** | **1 / 1** | **1 / 2** | **0 / 0** | **1 / 2** | **0 / 0** |
| neg | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| occl | 2 | 0 / 2 | 0 / 2 | 0 / 0 | 0 / 2 | 0 / 0 |
| **4A8B_lampwarm6_ottoman all** | **2** | **0 / 2** | **0 / 2** | **0 / 0** | **0 / 2** | **0 / 0** |
| neg | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| occl | 2 | 1 / 1 | 1 / 2 | 0 / 0 | 1 / 2 | 0 / 0 |
| **4A8B_overheaddim_palewood all** | **2** | **1 / 1** | **1 / 2** | **0 / 0** | **1 / 2** | **0 / 0** |
| occlx | 2 | 2 / 2 | 2 / 2 | 0 / 0 | 2 / 2 | 0 / 0 |
| **4A8B_window_abpwhite all** | **2** | **2 / 2** | **2 / 2** | **0 / 0** | **2 / 2** | **0 / 0** |
| neg | 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| occl | 2 | 1 / 1 | 2 / 2 | 0 / 0 | 2 / 2 | 0 / 0 |
| **4A8B_window_glass all** | **2** | **1 / 1** | **2 / 2** | **0 / 0** | **2 / 2** | **0 / 0** |
| **ALL all** | **32** | **18 / 23** | **20 / 27** | **2 / 1** | **20 / 28** | **2 / 0** |

- strict = the v2 rule. overlap = same color and IoU >= 0.5, bottom edge not checked. place = same color and box centers at most half the true box's width apart. false = boxes left without a barrel under that count.
