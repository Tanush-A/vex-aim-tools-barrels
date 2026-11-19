# Never regress: the eval table of each arm against `base` (today's defaults), adopted color model

Found / missed / false. Listed: each set's total and every scenario row that differs from `base`. HOME (leave-one-scene-out) and CAMPUS rows decide; the other sets are report only, except that no set may gain a box on a negative frame.

## `base`: passes

| set | scenario | base | arm | boxes on negatives | |
|---|---|---|---|---|---|
| HOME | ALL ROWS | 28 / 1 / 0 | 28 / 1 / 0 | 0 -> 0 | ok |
| CAMPUS | ALL ROWS | 35 / 0 / 0 | 35 / 0 / 0 | 0 -> 0 | ok |
| 4A8B_lampcool1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | ALL ROWS | 2 / 19 / 0 | 2 / 19 / 0 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | ALL ROWS | 2 / 19 / 2 | 2 / 19 / 2 | 0 -> 0 | report only |
| 4A8B_lampmid1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampmid3_wood | ALL ROWS | 1 / 20 / 1 | 1 / 20 / 1 | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm3_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm6_wood | ALL ROWS | 0 / 21 / 1 | 0 / 21 / 1 | 0 -> 0 | report only |
| 4A8B_window_black | ALL ROWS | 5 / 21 / 1 | 5 / 21 / 1 | 0 -> 0 | report only |
| DAVE* | ALL ROWS | 12 / 22 / 2 | 12 / 22 / 2 | 0 -> 0 | report only |

## `slice`: FAILS

| set | scenario | base | arm | boxes on negatives | |
|---|---|---|---|---|---|
| HOME | cluster | 7 / 1 / 0 | 7 / 1 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| HOME | core | 5 / 0 / 0 | 5 / 0 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| HOME | far | 4 / 0 / 0 | 4 / 0 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| HOME | ALL ROWS | 28 / 1 / 0 | 28 / 1 / 3 | 0 -> 0 | **FAILS**: false 0 -> 3 |
| CAMPUS | cluster | 4 / 0 / 0 | 4 / 0 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| CAMPUS | ALL ROWS | 35 / 0 / 0 | 35 / 0 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| 4A8B_lampcool1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | occl | 1 / 4 / 0 | 1 / 4 / 1 | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | ALL ROWS | 2 / 19 / 0 | 2 / 19 / 1 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | core | 0 / 4 / 0 | 0 / 4 / 1 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | occl | 1 / 4 / 2 | 1 / 4 / 3 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | touch | 0 / 2 / 0 | 1 / 1 / 0 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | ALL ROWS | 2 / 19 / 2 | 3 / 18 / 4 | 0 -> 0 | report only |
| 4A8B_lampmid1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampmid3_wood | ALL ROWS | 1 / 20 / 1 | 1 / 20 / 1 | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | close | 1 / 0 / 0 | 1 / 0 / 1 | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 1 | 0 -> 0 | report only |
| 4A8B_lampwarm1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm3_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm6_wood | ALL ROWS | 0 / 21 / 1 | 0 / 21 / 1 | 0 -> 0 | report only |
| 4A8B_window_black | occl | 1 / 5 / 0 | 3 / 3 / 0 | 0 -> 0 | report only |
| 4A8B_window_black | ALL ROWS | 5 / 21 / 1 | 7 / 19 / 1 | 0 -> 0 | report only |
| DAVE* | snap | 12 / 22 / 2 | 13 / 21 / 2 | 0 -> 0 | report only |
| DAVE* | ALL ROWS | 12 / 22 / 2 | 13 / 21 / 2 | 0 -> 0 | report only |

## `slice+cover`: FAILS

| set | scenario | base | arm | boxes on negatives | |
|---|---|---|---|---|---|
| HOME | cluster | 7 / 1 / 0 | 7 / 1 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| HOME | core | 5 / 0 / 0 | 5 / 0 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| HOME | far | 4 / 0 / 0 | 4 / 0 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| HOME | ALL ROWS | 28 / 1 / 0 | 28 / 1 / 3 | 0 -> 0 | **FAILS**: false 0 -> 3 |
| CAMPUS | cluster | 4 / 0 / 0 | 4 / 0 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| CAMPUS | ALL ROWS | 35 / 0 / 0 | 35 / 0 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| 4A8B_lampcool1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | occl | 1 / 4 / 0 | 1 / 4 / 1 | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | ALL ROWS | 2 / 19 / 0 | 2 / 19 / 1 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | core | 0 / 4 / 0 | 0 / 4 / 1 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | occl | 1 / 4 / 2 | 1 / 4 / 3 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | touch | 0 / 2 / 0 | 1 / 1 / 0 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | ALL ROWS | 2 / 19 / 2 | 3 / 18 / 4 | 0 -> 0 | report only |
| 4A8B_lampmid1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampmid3_wood | ALL ROWS | 1 / 20 / 1 | 1 / 20 / 1 | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | close | 1 / 0 / 0 | 1 / 0 / 1 | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 1 | 0 -> 0 | report only |
| 4A8B_lampwarm1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm3_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm6_wood | ALL ROWS | 0 / 21 / 1 | 0 / 21 / 1 | 0 -> 0 | report only |
| 4A8B_window_black | occl | 1 / 5 / 0 | 3 / 3 / 0 | 0 -> 0 | report only |
| 4A8B_window_black | ALL ROWS | 5 / 21 / 1 | 7 / 19 / 1 | 0 -> 0 | report only |
| DAVE* | snap | 12 / 22 / 2 | 13 / 21 / 2 | 0 -> 0 | report only |
| DAVE* | ALL ROWS | 12 / 22 / 2 | 13 / 21 / 2 | 0 -> 0 | report only |

## `two`: passes

| set | scenario | base | arm | boxes on negatives | |
|---|---|---|---|---|---|
| HOME | ALL ROWS | 28 / 1 / 0 | 28 / 1 / 0 | 0 -> 0 | ok |
| CAMPUS | ALL ROWS | 35 / 0 / 0 | 35 / 0 / 0 | 0 -> 0 | ok |
| 4A8B_lampcool1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | ALL ROWS | 2 / 19 / 0 | 2 / 19 / 0 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | ALL ROWS | 2 / 19 / 2 | 2 / 19 / 2 | 0 -> 0 | report only |
| 4A8B_lampmid1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampmid3_wood | ALL ROWS | 1 / 20 / 1 | 1 / 20 / 1 | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm3_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm6_wood | ALL ROWS | 0 / 21 / 1 | 0 / 21 / 1 | 0 -> 0 | report only |
| 4A8B_window_black | ALL ROWS | 5 / 21 / 1 | 5 / 21 / 1 | 0 -> 0 | report only |
| DAVE* | ALL ROWS | 12 / 22 / 2 | 12 / 22 / 2 | 0 -> 0 | report only |

## `edge`: passes

| set | scenario | base | arm | boxes on negatives | |
|---|---|---|---|---|---|
| HOME | ALL ROWS | 28 / 1 / 0 | 28 / 1 / 0 | 0 -> 0 | ok |
| CAMPUS | ALL ROWS | 35 / 0 / 0 | 35 / 0 / 0 | 0 -> 0 | ok |
| 4A8B_lampcool1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | ALL ROWS | 2 / 19 / 0 | 2 / 19 / 0 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | ALL ROWS | 2 / 19 / 2 | 2 / 19 / 2 | 0 -> 0 | report only |
| 4A8B_lampmid1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampmid3_wood | ALL ROWS | 1 / 20 / 1 | 1 / 20 / 1 | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm3_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm6_wood | ALL ROWS | 0 / 21 / 1 | 0 / 21 / 1 | 0 -> 0 | report only |
| 4A8B_window_black | ALL ROWS | 5 / 21 / 1 | 5 / 21 / 1 | 0 -> 0 | report only |
| DAVE* | ALL ROWS | 12 / 22 / 2 | 12 / 22 / 2 | 0 -> 0 | report only |

## `cap`: passes

| set | scenario | base | arm | boxes on negatives | |
|---|---|---|---|---|---|
| HOME | ALL ROWS | 28 / 1 / 0 | 28 / 1 / 0 | 0 -> 0 | ok |
| CAMPUS | ALL ROWS | 35 / 0 / 0 | 35 / 0 / 0 | 0 -> 0 | ok |
| 4A8B_lampcool1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | ALL ROWS | 2 / 19 / 0 | 2 / 19 / 0 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | ALL ROWS | 2 / 19 / 2 | 2 / 19 / 2 | 0 -> 0 | report only |
| 4A8B_lampmid1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampmid3_wood | ALL ROWS | 1 / 20 / 1 | 1 / 20 / 1 | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm3_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm6_wood | ALL ROWS | 0 / 21 / 1 | 0 / 21 / 1 | 0 -> 0 | report only |
| 4A8B_window_black | ALL ROWS | 5 / 21 / 1 | 5 / 21 / 1 | 0 -> 0 | report only |
| DAVE* | snap | 12 / 22 / 2 | 12 / 22 / 3 | 0 -> 0 | report only |
| DAVE* | ALL ROWS | 12 / 22 / 2 | 12 / 22 / 3 | 0 -> 0 | report only |

## `all`: FAILS

| set | scenario | base | arm | boxes on negatives | |
|---|---|---|---|---|---|
| HOME | cluster | 7 / 1 / 0 | 7 / 1 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| HOME | core | 5 / 0 / 0 | 5 / 0 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| HOME | far | 4 / 0 / 0 | 4 / 0 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| HOME | ALL ROWS | 28 / 1 / 0 | 28 / 1 / 3 | 0 -> 0 | **FAILS**: false 0 -> 3 |
| CAMPUS | cluster | 4 / 0 / 0 | 4 / 0 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| CAMPUS | ALL ROWS | 35 / 0 / 0 | 35 / 0 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| 4A8B_lampcool1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | occl | 1 / 4 / 0 | 1 / 4 / 1 | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | ALL ROWS | 2 / 19 / 0 | 2 / 19 / 1 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | core | 0 / 4 / 0 | 0 / 4 / 1 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | occl | 1 / 4 / 2 | 1 / 4 / 3 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | touch | 0 / 2 / 0 | 1 / 1 / 0 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | ALL ROWS | 2 / 19 / 2 | 3 / 18 / 4 | 0 -> 0 | report only |
| 4A8B_lampmid1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampmid3_wood | ALL ROWS | 1 / 20 / 1 | 1 / 20 / 1 | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | close | 1 / 0 / 0 | 1 / 0 / 1 | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 1 | 0 -> 0 | report only |
| 4A8B_lampwarm1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm3_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm6_wood | ALL ROWS | 0 / 21 / 1 | 0 / 21 / 1 | 0 -> 0 | report only |
| 4A8B_window_black | occl | 1 / 5 / 0 | 3 / 3 / 0 | 0 -> 0 | report only |
| 4A8B_window_black | ALL ROWS | 5 / 21 / 1 | 7 / 19 / 1 | 0 -> 0 | report only |
| DAVE* | snap | 12 / 22 / 2 | 13 / 21 / 3 | 0 -> 0 | report only |
| DAVE* | ALL ROWS | 12 / 22 / 2 | 13 / 21 / 3 | 0 -> 0 | report only |

## `all-cover`: FAILS

| set | scenario | base | arm | boxes on negatives | |
|---|---|---|---|---|---|
| HOME | cluster | 7 / 1 / 0 | 7 / 1 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| HOME | core | 5 / 0 / 0 | 5 / 0 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| HOME | far | 4 / 0 / 0 | 4 / 0 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| HOME | ALL ROWS | 28 / 1 / 0 | 28 / 1 / 3 | 0 -> 0 | **FAILS**: false 0 -> 3 |
| CAMPUS | cluster | 4 / 0 / 0 | 4 / 0 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| CAMPUS | ALL ROWS | 35 / 0 / 0 | 35 / 0 / 1 | 0 -> 0 | **FAILS**: false 0 -> 1 |
| 4A8B_lampcool1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | occl | 1 / 4 / 0 | 1 / 4 / 1 | 0 -> 0 | report only |
| 4A8B_lampcool3_wood | ALL ROWS | 2 / 19 / 0 | 2 / 19 / 1 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | core | 0 / 4 / 0 | 0 / 4 / 1 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | occl | 1 / 4 / 2 | 1 / 4 / 3 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | touch | 0 / 2 / 0 | 1 / 1 / 0 | 0 -> 0 | report only |
| 4A8B_lampcool6_wood | ALL ROWS | 2 / 19 / 2 | 3 / 18 / 4 | 0 -> 0 | report only |
| 4A8B_lampmid1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampmid3_wood | ALL ROWS | 1 / 20 / 1 | 1 / 20 / 1 | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | close | 1 / 0 / 0 | 1 / 0 / 1 | 0 -> 0 | report only |
| 4A8B_lampmid6_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 1 | 0 -> 0 | report only |
| 4A8B_lampwarm1_wood | ALL ROWS | 0 / 21 / 0 | 0 / 21 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm3_wood | ALL ROWS | 1 / 20 / 0 | 1 / 20 / 0 | 0 -> 0 | report only |
| 4A8B_lampwarm6_wood | ALL ROWS | 0 / 21 / 1 | 0 / 21 / 1 | 0 -> 0 | report only |
| 4A8B_window_black | occl | 1 / 5 / 0 | 3 / 3 / 0 | 0 -> 0 | report only |
| 4A8B_window_black | ALL ROWS | 5 / 21 / 1 | 7 / 19 / 1 | 0 -> 0 | report only |
| DAVE* | snap | 12 / 22 / 2 | 13 / 21 / 3 | 0 -> 0 | report only |
| DAVE* | ALL ROWS | 12 / 22 / 2 | 13 / 21 / 3 | 0 -> 0 | report only |

