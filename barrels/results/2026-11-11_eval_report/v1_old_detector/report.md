# Eval report: 2026-11-09_hs_candidate/config.json; DetConfig defaults  vs  2026-10-20_v1_test_adaptive/config.json; DetConfig stripe_mode=bands, body_min=0.0, height_max=0.0, body_width=0.0, cover_rows=False

```
                      |          CANDIDATE           |           BASELINE           |     DELTA (cand - base)      |      score      | negF
set/scenario frm brls | found miss false width   bot | found miss false width   bot | found miss false width   bot | cand base delta | c/b
------------------------------------------------------------------------------------------------------------------------------------------
  close        2    2 |     2    0     0  0.92   1.0 |     2    0     0  0.89   1.5 |     .    .     . +0.04  -0.5 |                 |
  cluster      2    8 |     6    2     0  1.02   1.5 |     6    2     0  0.99   1.0 |     .    .     . +0.04  +0.5 |                 |
  core         3    5 |     5    0     0  0.94   1.0 |     5    0     0  0.92   1.0 |     .    .     . +0.02     . |                 |
  edge         1    1 |     1    0     0  1.29   1.0 |     1    0     0  1.29   0.0 |     .    .     .     .  +1.0 |                 |
  far          1    4 |     4    0     0  1.03   0.5 |     4    0     0  0.86   1.0 |     .    .     . +0.17  -0.5 |                 |
  neg          2    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl         2    4 |     2    2     0  0.98   0.5 |     2    2     0  0.89   1.0 |     .    .     . +0.10  -0.5 |                 |
  top          1    1 |     1    0     0  0.99   0.0 |     1    0     0  1.09   0.0 |     .    .     . -0.10     . |                 |
  topstripe    1    1 |     1    0     0  0.98   0.0 |     1    0     0  1.20   0.0 |     .    .     . -0.22     . |                 |
  touch        1    3 |     3    0     0  0.94   1.0 |     3    0     0  0.96   1.0 |     .    .     . -0.02     . |                 |
HOME all      16   29 |    25    4     0  0.98   1.0 |    25    4     0  0.93   1.0 |     .    .     . +0.05     . | 0.93 0.93     . | 0/0

  close        1    1 |     1    0     0  0.95   1.0 |     0    1     0     -     - |    +1   -1     .     -     - |                 |
  cluster      1    4 |     4    0     0  0.94   2.0 |     0    4     0     -     - |    +4   -4     .     -     - |                 |
  clutter      1    3 |     3    0     0  1.11   2.0 |     0    3     0     -     - |    +3   -3     .     -     - |                 |
  core         1    4 |     4    0     0  0.94   1.5 |     1    3     1  1.00   2.0 |    +3   -3    -1 -0.06  -0.5 |                 |
  edge         1    1 |     1    0     0  1.50   1.0 |     0    1     0     -     - |    +1   -1     .     -     - |                 |
  far          1    4 |     4    0     0  1.01   1.0 |     3    1     0  1.05   1.0 |    +1   -1     . -0.04     . |                 |
  hand         1    2 |     2    0     0  1.07   1.0 |     2    0     0  0.87   2.0 |     .    .     . +0.20  -1.0 |                 |
  held         1    1 |     1    0     0  0.98   1.0 |     0    1     0     -     - |    +1   -1     .     -     - |                 |
  neg          4    0 |     0    0     0     -     - |     0    0     0     -     - |     .    .     .     -     - |                 |
  occl         1    1 |     0    1     0     -     - |     0    1     0     -     - |     .    .     .     -     - |                 |
  plain        2    4 |     4    0     0  0.94   2.0 |     2    2     0  0.86   1.5 |    +2   -2     . +0.08  +0.5 |                 |
  room         2    4 |     4    0     0  0.99   2.5 |     0    4     0     -     - |    +4   -4     .     -     - |                 |
  top          1    1 |     1    0     0  0.94   2.0 |     1    0     0  0.57   2.0 |     .    .     . +0.37     . |                 |
  topstripe    1    1 |     1    0     0  0.94   3.0 |     1    0     0  0.79   3.0 |     .    .     . +0.15     . |                 |
  touch        1    2 |     2    0     0  0.97   1.5 |     0    2     0     -     - |    +2   -2     .     -     - |                 |
  window       1    2 |     2    0     0  0.88   1.0 |     0    2     0     -     - |    +2   -2     .     -     - |                 |
CAMPUS all    21   35 |    34    1     0  0.96   2.0 |    10   25     1  0.92   1.5 |   +24  -24    -1 +0.04  +0.5 | 0.99 0.41 +0.58 | 0/0

  snap        12   34 |    11   23     2  0.96   1.0 |     0   34     0     -     - |   +11  -11    +2     -     - |                 |
DAVE* all     12   34 |    11   23     2  0.96   1.0 |     0   34     0     -     - |   +11  -11    +2     -     - | 0.47 0.00 +0.47 | 0/0

------------------------------------------------------------------------------------------------------------------------------------------
ALL all       37   64 |    59    5     0  0.97   1.0 |    35   29     1  0.93   1.0 |   +24  -24    -1 +0.04     . |                 | 0/0
------------------------------------------------------------------------------------------------------------------------------------------
candidate = 2026-11-09_hs_candidate/config.json; DetConfig defaults
baseline  = 2026-10-20_v1_test_adaptive/config.json; DetConfig stripe_mode=bands, body_min=0.0, height_max=0.0,
    body_width=0.0, cover_rows=False
delta = candidate - baseline ('.' = no change). Frames: train split only, test frames never opened; HOME 16, CAMPUS 21,
    DAVE* 12. git 1c9f373; 14.7 s.
Rule: EVAL.md v2, as eval_det implements it — a box is right when same color, IoU >= 0.5 and bottom edge within max(3
    px, 10 % of the true height).
found / miss = true barrels with / without a right box; false = boxes that match no barrel; width = median box width /
    true width over the found;
bot = median |bottom-edge error| in px over the found; score = mean of the orange and blue F1 (pooled over the set's
    frames), on the set rows only.
negF c/b = false boxes on empty (negative) frames, candidate/baseline; DQ:c / DQ:b = that arm drew a box on a CLEAN
    empty frame, which disqualifies it.
HOME is scored leave-one-scene-out: the color model is fit on these frames, so each scene is segmented by a model re-fit
    without it (the published home number). Other sets use the model file as it is.
The ALL row adds up the counts of the sets that are not indicative; it has no score (no agreed headline pools different
    sets).
* indicative only: Dave's boxes group touching barrels, and his frames are in no split.
```

| set / scenario | frames | barrels | cand found | cand miss | cand false | cand width | cand bot | base found | base miss | base false | base width | base bot | Δ found | Δ miss | Δ false | Δ width | Δ bot | score cand | score base | score Δ | negF c/b |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| close | 2 | 2 | 2 | 0 | 0 | 0.92 | 1.0 | 2 | 0 | 0 | 0.89 | 1.5 | . | . | . | +0.04 | -0.5 |  |  |  |  |
| cluster | 2 | 8 | 6 | 2 | 0 | 1.02 | 1.5 | 6 | 2 | 0 | 0.99 | 1.0 | . | . | . | +0.04 | +0.5 |  |  |  |  |
| core | 3 | 5 | 5 | 0 | 0 | 0.94 | 1.0 | 5 | 0 | 0 | 0.92 | 1.0 | . | . | . | +0.02 | . |  |  |  |  |
| edge | 1 | 1 | 1 | 0 | 0 | 1.29 | 1.0 | 1 | 0 | 0 | 1.29 | 0.0 | . | . | . | . | +1.0 |  |  |  |  |
| far | 1 | 4 | 4 | 0 | 0 | 1.03 | 0.5 | 4 | 0 | 0 | 0.86 | 1.0 | . | . | . | +0.17 | -0.5 |  |  |  |  |
| neg | 2 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 2 | 4 | 2 | 2 | 0 | 0.98 | 0.5 | 2 | 2 | 0 | 0.89 | 1.0 | . | . | . | +0.10 | -0.5 |  |  |  |  |
| top | 1 | 1 | 1 | 0 | 0 | 0.99 | 0.0 | 1 | 0 | 0 | 1.09 | 0.0 | . | . | . | -0.10 | . |  |  |  |  |
| topstripe | 1 | 1 | 1 | 0 | 0 | 0.98 | 0.0 | 1 | 0 | 0 | 1.20 | 0.0 | . | . | . | -0.22 | . |  |  |  |  |
| touch | 1 | 3 | 3 | 0 | 0 | 0.94 | 1.0 | 3 | 0 | 0 | 0.96 | 1.0 | . | . | . | -0.02 | . |  |  |  |  |
| **HOME all** | **16** | **29** | **25** | **4** | **0** | **0.98** | **1.0** | **25** | **4** | **0** | **0.93** | **1.0** | **.** | **.** | **.** | **+0.05** | **.** | **0.93** | **0.93** | **.** | **0/0** |
| close | 1 | 1 | 1 | 0 | 0 | 0.95 | 1.0 | 0 | 1 | 0 | - | - | +1 | -1 | . | - | - |  |  |  |  |
| cluster | 1 | 4 | 4 | 0 | 0 | 0.94 | 2.0 | 0 | 4 | 0 | - | - | +4 | -4 | . | - | - |  |  |  |  |
| clutter | 1 | 3 | 3 | 0 | 0 | 1.11 | 2.0 | 0 | 3 | 0 | - | - | +3 | -3 | . | - | - |  |  |  |  |
| core | 1 | 4 | 4 | 0 | 0 | 0.94 | 1.5 | 1 | 3 | 1 | 1.00 | 2.0 | +3 | -3 | -1 | -0.06 | -0.5 |  |  |  |  |
| edge | 1 | 1 | 1 | 0 | 0 | 1.50 | 1.0 | 0 | 1 | 0 | - | - | +1 | -1 | . | - | - |  |  |  |  |
| far | 1 | 4 | 4 | 0 | 0 | 1.01 | 1.0 | 3 | 1 | 0 | 1.05 | 1.0 | +1 | -1 | . | -0.04 | . |  |  |  |  |
| hand | 1 | 2 | 2 | 0 | 0 | 1.07 | 1.0 | 2 | 0 | 0 | 0.87 | 2.0 | . | . | . | +0.20 | -1.0 |  |  |  |  |
| held | 1 | 1 | 1 | 0 | 0 | 0.98 | 1.0 | 0 | 1 | 0 | - | - | +1 | -1 | . | - | - |  |  |  |  |
| neg | 4 | 0 | 0 | 0 | 0 | - | - | 0 | 0 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| occl | 1 | 1 | 0 | 1 | 0 | - | - | 0 | 1 | 0 | - | - | . | . | . | - | - |  |  |  |  |
| plain | 2 | 4 | 4 | 0 | 0 | 0.94 | 2.0 | 2 | 2 | 0 | 0.86 | 1.5 | +2 | -2 | . | +0.08 | +0.5 |  |  |  |  |
| room | 2 | 4 | 4 | 0 | 0 | 0.99 | 2.5 | 0 | 4 | 0 | - | - | +4 | -4 | . | - | - |  |  |  |  |
| top | 1 | 1 | 1 | 0 | 0 | 0.94 | 2.0 | 1 | 0 | 0 | 0.57 | 2.0 | . | . | . | +0.37 | . |  |  |  |  |
| topstripe | 1 | 1 | 1 | 0 | 0 | 0.94 | 3.0 | 1 | 0 | 0 | 0.79 | 3.0 | . | . | . | +0.15 | . |  |  |  |  |
| touch | 1 | 2 | 2 | 0 | 0 | 0.97 | 1.5 | 0 | 2 | 0 | - | - | +2 | -2 | . | - | - |  |  |  |  |
| window | 1 | 2 | 2 | 0 | 0 | 0.88 | 1.0 | 0 | 2 | 0 | - | - | +2 | -2 | . | - | - |  |  |  |  |
| **CAMPUS all** | **21** | **35** | **34** | **1** | **0** | **0.96** | **2.0** | **10** | **25** | **1** | **0.92** | **1.5** | **+24** | **-24** | **-1** | **+0.04** | **+0.5** | **0.99** | **0.41** | **+0.58** | **0/0** |
| snap | 12 | 34 | 11 | 23 | 2 | 0.96 | 1.0 | 0 | 34 | 0 | - | - | +11 | -11 | +2 | - | - |  |  |  |  |
| **DAVE* all** | **12** | **34** | **11** | **23** | **2** | **0.96** | **1.0** | **0** | **34** | **0** | **-** | **-** | **+11** | **-11** | **+2** | **-** | **-** | **0.47** | **0.00** | **+0.47** | **0/0** |
| **ALL all** | **37** | **64** | **59** | **5** | **0** | **0.97** | **1.0** | **35** | **29** | **1** | **0.93** | **1.0** | **+24** | **-24** | **-1** | **+0.04** | **.** |  |  |  | **0/0** |

- candidate = 2026-11-09_hs_candidate/config.json; DetConfig defaults
- baseline  = 2026-10-20_v1_test_adaptive/config.json; DetConfig stripe_mode=bands, body_min=0.0, height_max=0.0, body_width=0.0, cover_rows=False
- delta = candidate - baseline ('.' = no change). Frames: train split only, test frames never opened; HOME 16, CAMPUS 21, DAVE* 12. git 1c9f373; 14.7 s.
- Rule: EVAL.md v2, as eval_det implements it — a box is right when same color, IoU >= 0.5 and bottom edge within max(3 px, 10 % of the true height).
- found / miss = true barrels with / without a right box; false = boxes that match no barrel; width = median box width / true width over the found;
- bot = median |bottom-edge error| in px over the found; score = mean of the orange and blue F1 (pooled over the set's frames), on the set rows only.
- negF c/b = false boxes on empty (negative) frames, candidate/baseline; DQ:c / DQ:b = that arm drew a box on a CLEAN empty frame, which disqualifies it.
- HOME is scored leave-one-scene-out: the color model is fit on these frames, so each scene is segmented by a model re-fit without it (the published home number). Other sets use the model file as it is.
- The ALL row adds up the counts of the sets that are not indicative; it has no score (no agreed headline pools different sets).
- * indicative only: Dave's boxes group touching barrels, and his frames are in no split.
