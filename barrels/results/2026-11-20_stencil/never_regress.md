# Never regress: the eval table of each arm against `rules` (today's rule detector), adopted color model

Found / missed / false; width = median box width / true width, bottom = median bottom-edge error in px, over the found barrels. Listed: each set's total and every scenario row that differs from `rules`. HOME (leave one scene out) and CAMPUS rows decide; the other sets are report only, except that no set may gain a box on a negative frame.

## `stencil`: FAILS

| set | scenario | rules | arm | width | bottom px | boxes on negatives | |
|---|---|---|---|---|---|---|---|
| HOME | topstripe | 1 / 0 / 0 | 0 / 1 / 0 | 0.98 -> - | 0.0 -> - | 0 -> 0 | **FAILS**: found 1 -> 0 |
| HOME | ALL ROWS | 28 / 1 / 0 | 27 / 2 / 0 | 0.95 -> 0.96 | 1.0 -> 2.0 | 0 -> 0 | **FAILS**: found 28 -> 27 |
| CAMPUS | cluster | 4 / 0 / 0 | 3 / 1 / 1 | 0.95 -> 1.00 | 2.0 -> 3.0 | 0 -> 0 | **FAILS**: found 4 -> 3, false 0 -> 1 |
| CAMPUS | clutter | 3 / 0 / 0 | 2 / 1 / 0 | 1.09 -> 0.97 | 2.0 -> 1.5 | 0 -> 0 | **FAILS**: found 3 -> 2 |
| CAMPUS | held | 1 / 0 / 0 | 0 / 1 / 0 | 0.98 -> - | 1.0 -> - | 0 -> 0 | **FAILS**: found 1 -> 0 |
| CAMPUS | occl | 1 / 0 / 0 | 0 / 1 / 0 | 1.02 -> - | 2.0 -> - | 0 -> 0 | **FAILS**: found 1 -> 0 |
| CAMPUS | ALL ROWS | 35 / 0 / 0 | 31 / 4 / 1 | 0.94 -> 0.98 | 2.0 -> 3.0 | 0 -> 0 | **FAILS**: found 35 -> 31, false 0 -> 1 |
| 4A8B_lampcool1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | close | 1 / 0 / 0 | 0 / 1 / 0 | 0.95 -> - | 0.0 -> - | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | occl | 1 / 4 / 0 | 0 / 5 / 0 | 0.93 -> - | 1.0 -> - | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | ALL ROWS | 2 / 19 / 0 | 0 / 21 / 0 | 0.94 -> - | 0.5 -> - | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | occl | 1 / 4 / 2 | 0 / 5 / 0 | 1.07 -> - | 2.0 -> - | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | ALL ROWS | 2 / 19 / 2 | 1 / 20 / 0 | 1.02 -> 1.09 | 1.0 -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampmid1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_lampmid3_wood | close | 1 / 0 / 1 | 0 / 1 / 0 | 0.91 -> - | 0.0 -> - | 0 -> 0 | report only |
| 4A8B_lampmid3_wood | ALL ROWS | 1 / 20 / 1 | 0 / 21 / 0 | 0.91 -> - | 0.0 -> - | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0.93 -> 1.09 | 0.0 -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampwarm1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_lampwarm3_wood | close | 1 / 0 / 0 | 0 / 1 / 0 | 0.86 -> - | 0.0 -> - | 0 -> 0 | report only |
| 4A8B_lampwarm3_wood | ALL ROWS | 1 / 20 / 0 | 0 / 21 / 0 | 0.86 -> - | 0.0 -> - | 0 -> 0 | report only |
| 4A8B_lampwarm6_wood | close | 0 / 1 / 1 | 1 / 0 / 0 | - -> 1.04 | - -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampwarm6_wood | ALL ROWS | 0 / 21 / 1 | 1 / 20 / 0 | - -> 1.04 | - -> 0.0 | 0 -> 0 | report only |
| 4A8B_window_black | close | 1 / 2 / 0 | 0 / 3 / 0 | 0.76 -> - | 0.0 -> - | 0 -> 0 | report only |
| 4A8B_window_black | clutter | 1 / 3 / 1 | 0 / 4 / 0 | 0.85 -> - | 4.0 -> - | 0 -> 0 | report only |
| 4A8B_window_black | held | 1 / 2 / 0 | 0 / 3 / 0 | 0.73 -> - | 0.0 -> - | 0 -> 0 | report only |
| 4A8B_window_black | occl | 1 / 5 / 0 | 0 / 6 / 0 | 0.98 -> - | 1.0 -> - | 0 -> 0 | report only |
| 4A8B_window_black | touch | 1 / 1 / 0 | 0 / 2 / 0 | 1.17 -> - | 4.0 -> - | 0 -> 0 | report only |
| 4A8B_window_black | ALL ROWS | 5 / 21 / 1 | 0 / 26 / 0 | 0.85 -> - | 1.0 -> - | 0 -> 0 | report only |
| DAVE* | snap | 12 / 22 / 3 | 3 / 31 / 0 | 0.95 -> 0.61 | 1.0 -> 1.0 | 0 -> 0 | report only |
| DAVE* | ALL ROWS | 12 / 22 / 3 | 3 / 31 / 0 | 0.95 -> 0.61 | 1.0 -> 1.0 | 0 -> 0 | report only |

## `union`: passes

| set | scenario | rules | arm | width | bottom px | boxes on negatives | |
|---|---|---|---|---|---|---|---|
| HOME | ALL ROWS | 28 / 1 / 0 | 28 / 1 / 0 | 0.95 -> 0.95 | 1.0 -> 1.0 | 0 -> 0 | ok |
| CAMPUS | ALL ROWS | 35 / 0 / 0 | 35 / 0 / 0 | 0.94 -> 0.94 | 2.0 -> 2.0 | 0 -> 0 | ok |
| 4A8B_lampcool1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | ALL ROWS | 2 / 19 / 0 | 2 / 19 / 0 | 0.94 -> 0.94 | 0.5 -> 0.5 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | ALL ROWS | 2 / 19 / 2 | 2 / 19 / 2 | 1.02 -> 1.02 | 1.0 -> 1.0 | 0 -> 0 | report only |
| 4A8B_lampmid1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_lampmid3_wood | ALL ROWS | 1 / 20 / 1 | 1 / 20 / 1 | 0.91 -> 0.91 | 0.0 -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0.93 -> 0.93 | 0.0 -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampwarm1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_lampwarm3_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0.86 -> 0.86 | 0.0 -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampwarm6_wood | ALL ROWS | 0 / 21 / 1 | 0 / 21 / 1 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_window_black | ALL ROWS | 5 / 21 / 1 | 5 / 21 / 1 | 0.85 -> 0.85 | 1.0 -> 1.0 | 0 -> 0 | report only |
| DAVE* | snap | 12 / 22 / 3 | 13 / 21 / 3 | 0.95 -> 0.94 | 1.0 -> 1.0 | 0 -> 0 | report only |
| DAVE* | ALL ROWS | 12 / 22 / 3 | 13 / 21 / 3 | 0.95 -> 0.94 | 1.0 -> 1.0 | 0 -> 0 | report only |

## `veto`: passes

| set | scenario | rules | arm | width | bottom px | boxes on negatives | |
|---|---|---|---|---|---|---|---|
| HOME | ALL ROWS | 28 / 1 / 0 | 28 / 1 / 0 | 0.95 -> 0.95 | 1.0 -> 1.0 | 0 -> 0 | ok |
| CAMPUS | ALL ROWS | 35 / 0 / 0 | 35 / 0 / 0 | 0.94 -> 0.94 | 2.0 -> 2.0 | 0 -> 0 | ok |
| 4A8B_lampcool1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | occl | 1 / 4 / 0 | 0 / 5 / 0 | 0.93 -> - | 1.0 -> - | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | ALL ROWS | 2 / 19 / 0 | 1 / 20 / 0 | 0.94 -> 0.95 | 0.5 -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | occl | 1 / 4 / 2 | 1 / 4 / 0 | 1.07 -> 1.07 | 2.0 -> 2.0 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | ALL ROWS | 2 / 19 / 2 | 2 / 19 / 0 | 1.02 -> 1.02 | 1.0 -> 1.0 | 0 -> 0 | report only |
| 4A8B_lampmid1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_lampmid3_wood | ALL ROWS | 1 / 20 / 1 | 1 / 20 / 1 | 0.91 -> 0.91 | 0.0 -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0.93 -> 0.93 | 0.0 -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampwarm1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_lampwarm3_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0.86 -> 0.86 | 0.0 -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampwarm6_wood | ALL ROWS | 0 / 21 / 1 | 0 / 21 / 1 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_window_black | clutter | 1 / 3 / 1 | 0 / 4 / 0 | 0.85 -> - | 4.0 -> - | 0 -> 0 | report only |
| 4A8B_window_black | touch | 1 / 1 / 0 | 0 / 2 / 0 | 1.17 -> - | 4.0 -> - | 0 -> 0 | report only |
| 4A8B_window_black | ALL ROWS | 5 / 21 / 1 | 3 / 23 / 0 | 0.85 -> 0.76 | 1.0 -> 0.0 | 0 -> 0 | report only |
| DAVE* | snap | 12 / 22 / 3 | 12 / 22 / 1 | 0.95 -> 0.95 | 1.0 -> 1.0 | 0 -> 0 | report only |
| DAVE* | ALL ROWS | 12 / 22 / 3 | 12 / 22 / 1 | 0.95 -> 0.95 | 1.0 -> 1.0 | 0 -> 0 | report only |

## `veto+union`: passes

| set | scenario | rules | arm | width | bottom px | boxes on negatives | |
|---|---|---|---|---|---|---|---|
| HOME | ALL ROWS | 28 / 1 / 0 | 28 / 1 / 0 | 0.95 -> 0.95 | 1.0 -> 1.0 | 0 -> 0 | ok |
| CAMPUS | ALL ROWS | 35 / 0 / 0 | 35 / 0 / 0 | 0.94 -> 0.94 | 2.0 -> 2.0 | 0 -> 0 | ok |
| 4A8B_lampcool1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | occl | 1 / 4 / 0 | 0 / 5 / 0 | 0.93 -> - | 1.0 -> - | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | ALL ROWS | 2 / 19 / 0 | 1 / 20 / 0 | 0.94 -> 0.95 | 0.5 -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | occl | 1 / 4 / 2 | 1 / 4 / 0 | 1.07 -> 1.07 | 2.0 -> 2.0 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | ALL ROWS | 2 / 19 / 2 | 2 / 19 / 0 | 1.02 -> 1.02 | 1.0 -> 1.0 | 0 -> 0 | report only |
| 4A8B_lampmid1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_lampmid3_wood | ALL ROWS | 1 / 20 / 1 | 1 / 20 / 1 | 0.91 -> 0.91 | 0.0 -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0.93 -> 0.93 | 0.0 -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampwarm1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_lampwarm3_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0.86 -> 0.86 | 0.0 -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampwarm6_wood | ALL ROWS | 0 / 21 / 1 | 0 / 21 / 1 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_window_black | clutter | 1 / 3 / 1 | 0 / 4 / 0 | 0.85 -> - | 4.0 -> - | 0 -> 0 | report only |
| 4A8B_window_black | touch | 1 / 1 / 0 | 0 / 2 / 0 | 1.17 -> - | 4.0 -> - | 0 -> 0 | report only |
| 4A8B_window_black | ALL ROWS | 5 / 21 / 1 | 3 / 23 / 0 | 0.85 -> 0.76 | 1.0 -> 0.0 | 0 -> 0 | report only |
| DAVE* | snap | 12 / 22 / 3 | 13 / 21 / 1 | 0.95 -> 0.94 | 1.0 -> 1.0 | 0 -> 0 | report only |
| DAVE* | ALL ROWS | 12 / 22 / 3 | 13 / 21 / 1 | 0.95 -> 0.94 | 1.0 -> 1.0 | 0 -> 0 | report only |

## `union1`: passes

| set | scenario | rules | arm | width | bottom px | boxes on negatives | |
|---|---|---|---|---|---|---|---|
| HOME | ALL ROWS | 28 / 1 / 0 | 28 / 1 / 0 | 0.95 -> 0.95 | 1.0 -> 1.0 | 0 -> 0 | ok |
| CAMPUS | ALL ROWS | 35 / 0 / 0 | 35 / 0 / 0 | 0.94 -> 0.94 | 2.0 -> 2.0 | 0 -> 0 | ok |
| 4A8B_lampcool1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | ALL ROWS | 2 / 19 / 0 | 2 / 19 / 0 | 0.94 -> 0.94 | 0.5 -> 0.5 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | ALL ROWS | 2 / 19 / 2 | 2 / 19 / 2 | 1.02 -> 1.02 | 1.0 -> 1.0 | 0 -> 0 | report only |
| 4A8B_lampmid1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_lampmid3_wood | ALL ROWS | 1 / 20 / 1 | 1 / 20 / 1 | 0.91 -> 0.91 | 0.0 -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0.93 -> 0.93 | 0.0 -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampwarm1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_lampwarm3_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0.86 -> 0.86 | 0.0 -> 0.0 | 0 -> 0 | report only |
| 4A8B_lampwarm6_wood | ALL ROWS | 0 / 21 / 1 | 0 / 21 / 1 | - -> - | - -> - | 0 -> 0 | report only |
| 4A8B_window_black | ALL ROWS | 5 / 21 / 1 | 5 / 21 / 1 | 0.85 -> 0.85 | 1.0 -> 1.0 | 0 -> 0 | report only |
| DAVE* | snap | 12 / 22 / 3 | 13 / 21 / 3 | 0.95 -> 0.94 | 1.0 -> 1.0 | 0 -> 0 | report only |
| DAVE* | ALL ROWS | 12 / 22 / 3 | 13 / 21 / 3 | 0.95 -> 0.94 | 1.0 -> 1.0 | 0 -> 0 | report only |

