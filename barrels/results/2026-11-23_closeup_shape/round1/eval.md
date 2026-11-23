# The eval table of every arm

git 576658f; v2 rule; train frames only; adopted color model; HOME leave-one-scene-out. Each cell: found / missed / false (on a set's `all` row: then the boxes on its negative frames). HOME and CAMPUS decide (PREREG clause (a)); the other sets are report only, except that no set may have a box on a negative frame. `*` = indicative labels.

| set | scenario | barrels | `start` | `side` | `stripe` | `shape` |
|---|---|---|---|---|---|---|
| HOME | close | 2 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 |
| HOME | cluster | 8 | 7 / 1 / 0 | 7 / 1 / 0 | 7 / 1 / 0 | 7 / 1 / 0 |
| HOME | core | 5 | 5 / 0 / 0 | 5 / 0 / 0 | 5 / 0 / 0 | 5 / 0 / 0 |
| HOME | edge | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| HOME | far | 4 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| HOME | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| HOME | occl | 4 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| HOME | top | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| HOME | topstripe | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| HOME | touch | 3 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 |
| HOME | **all** | 29 | 28 / 1 / 0; neg 0 | 28 / 1 / 0; neg 0 | 28 / 1 / 0; neg 0 | 28 / 1 / 0; neg 0 |
| CAMPUS | close | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| CAMPUS | cluster | 4 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| CAMPUS | clutter | 3 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 |
| CAMPUS | core | 4 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| CAMPUS | edge | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| CAMPUS | far | 4 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| CAMPUS | hand | 2 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 |
| CAMPUS | held | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| CAMPUS | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| CAMPUS | occl | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| CAMPUS | plain | 4 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| CAMPUS | room | 4 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| CAMPUS | top | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| CAMPUS | topstripe | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| CAMPUS | touch | 2 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 |
| CAMPUS | window | 2 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 |
| CAMPUS | **all** | 35 | 35 / 0 / 0; neg 0 | 35 / 0 / 0; neg 0 | 35 / 0 / 0; neg 0 | 35 / 0 / 0; neg 0 |
| 4A8B_both_abpgray | close | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| 4A8B_both_abpgray | clutter | 4 | 3 / 1 / 2 | 3 / 1 / 2 | 3 / 1 / 2 | 3 / 1 / 2 |
| 4A8B_both_abpgray | core | 4 | 2 / 2 / 0 | 2 / 2 / 0 | 2 / 2 / 0 | 2 / 2 / 0 |
| 4A8B_both_abpgray | edge | 2 | 1 / 1 / 0 | 1 / 1 / 0 | 1 / 1 / 0 | 1 / 1 / 0 |
| 4A8B_both_abpgray | held | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| 4A8B_both_abpgray | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_both_abpgray | occl | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| 4A8B_both_abpgray | touch | 3 | 1 / 2 / 0 | 1 / 2 / 0 | 1 / 2 / 0 | 1 / 2 / 0 |
| 4A8B_both_abpgray | **all** | 16 | 10 / 6 / 2; neg 0 | 10 / 6 / 2; neg 0 | 10 / 6 / 2; neg 0 | 10 / 6 / 2; neg 0 |
| 4A8B_lampcool1_wood | close | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampcool1_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool1_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool1_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool1_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampcool1_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampcool1_wood | occl | 5 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 |
| 4A8B_lampcool1_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampcool1_wood | **all** | 21 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 |
| 4A8B_lampcool3_wood | close | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| 4A8B_lampcool3_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool3_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool3_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool3_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampcool3_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampcool3_wood | occl | 5 | 1 / 4 / 0 | 1 / 4 / 0 | 1 / 4 / 0 | 1 / 4 / 0 |
| 4A8B_lampcool3_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampcool3_wood | **all** | 21 | 2 / 19 / 0; neg 0 | 2 / 19 / 0; neg 0 | 2 / 19 / 0; neg 0 | 2 / 19 / 0; neg 0 |
| 4A8B_lampcool6_ottoman | close | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampcool6_ottoman | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool6_ottoman | core | 4 | 1 / 3 / 0 | 1 / 3 / 0 | 1 / 3 / 0 | 1 / 3 / 0 |
| 4A8B_lampcool6_ottoman | edge | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampcool6_ottoman | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampcool6_ottoman | occl | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampcool6_ottoman | touch | 3 | 2 / 1 / 0 | 2 / 1 / 0 | 2 / 1 / 0 | 2 / 1 / 0 |
| 4A8B_lampcool6_ottoman | **all** | 15 | 3 / 12 / 0; neg 0 | 3 / 12 / 0; neg 0 | 3 / 12 / 0; neg 0 | 3 / 12 / 0; neg 0 |
| 4A8B_lampcool6_wood | close | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| 4A8B_lampcool6_wood | cluster | 4 | 0 / 4 / 1 | 0 / 4 / 1 | 0 / 4 / 1 | 0 / 4 / 1 |
| 4A8B_lampcool6_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool6_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool6_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampcool6_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampcool6_wood | occl | 5 | 1 / 4 / 2 | 1 / 4 / 2 | 1 / 4 / 2 | 1 / 4 / 2 |
| 4A8B_lampcool6_wood | touch | 2 | 0 / 2 / 1 | 0 / 2 / 1 | 0 / 2 / 1 | 0 / 2 / 1 |
| 4A8B_lampcool6_wood | **all** | 21 | 2 / 19 / 4; neg 0 | 2 / 19 / 4; neg 0 | 2 / 19 / 4; neg 0 | 2 / 19 / 4; neg 0 |
| 4A8B_lampmid1_wood | close | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampmid1_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid1_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid1_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid1_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampmid1_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampmid1_wood | occl | 5 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 |
| 4A8B_lampmid1_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampmid1_wood | **all** | 21 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 |
| 4A8B_lampmid3_ottoman | close | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| 4A8B_lampmid3_ottoman | clutter | 4 | 0 / 4 / 1 | 0 / 4 / 1 | 0 / 4 / 1 | 0 / 4 / 1 |
| 4A8B_lampmid3_ottoman | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid3_ottoman | edge | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampmid3_ottoman | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampmid3_ottoman | occl | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampmid3_ottoman | touch | 3 | 0 / 3 / 0 | 0 / 3 / 0 | 0 / 3 / 0 | 0 / 3 / 0 |
| 4A8B_lampmid3_ottoman | **all** | 15 | 1 / 14 / 1; neg 0 | 1 / 14 / 1; neg 0 | 1 / 14 / 1; neg 0 | 1 / 14 / 1; neg 0 |
| 4A8B_lampmid3_wood | close | 1 | 1 / 0 / 1 | 1 / 0 / 1 | 1 / 0 / 1 | 1 / 0 / 1 |
| 4A8B_lampmid3_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid3_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid3_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid3_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampmid3_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampmid3_wood | occl | 5 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 |
| 4A8B_lampmid3_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampmid3_wood | **all** | 21 | 1 / 20 / 1; neg 0 | 1 / 20 / 1; neg 0 | 1 / 20 / 1; neg 0 | 1 / 20 / 1; neg 0 |
| 4A8B_lampmid6_ottoman | close | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampmid6_ottoman | clutter | 4 | 1 / 3 / 0 | 1 / 3 / 0 | 1 / 3 / 0 | 1 / 3 / 0 |
| 4A8B_lampmid6_ottoman | core | 4 | 2 / 2 / 0 | 2 / 2 / 0 | 2 / 2 / 0 | 2 / 2 / 0 |
| 4A8B_lampmid6_ottoman | edge | 2 | 1 / 1 / 0 | 1 / 1 / 0 | 1 / 1 / 0 | 1 / 1 / 0 |
| 4A8B_lampmid6_ottoman | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampmid6_ottoman | occl | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampmid6_ottoman | touch | 3 | 2 / 1 / 0 | 2 / 1 / 0 | 2 / 1 / 0 | 2 / 1 / 0 |
| 4A8B_lampmid6_ottoman | **all** | 15 | 6 / 9 / 0; neg 0 | 6 / 9 / 0; neg 0 | 6 / 9 / 0; neg 0 | 6 / 9 / 0; neg 0 |
| 4A8B_lampmid6_wood | close | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| 4A8B_lampmid6_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid6_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid6_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid6_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampmid6_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampmid6_wood | occl | 5 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 |
| 4A8B_lampmid6_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampmid6_wood | **all** | 21 | 1 / 20 / 0; neg 0 | 1 / 20 / 0; neg 0 | 1 / 20 / 0; neg 0 | 1 / 20 / 0; neg 0 |
| 4A8B_lampwarm1_wood | close | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampwarm1_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm1_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm1_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm1_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampwarm1_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampwarm1_wood | occl | 5 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 |
| 4A8B_lampwarm1_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampwarm1_wood | **all** | 21 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 |
| 4A8B_lampwarm3_wood | close | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| 4A8B_lampwarm3_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm3_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm3_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm3_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampwarm3_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampwarm3_wood | occl | 5 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 |
| 4A8B_lampwarm3_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampwarm3_wood | **all** | 21 | 1 / 20 / 0; neg 0 | 1 / 20 / 0; neg 0 | 1 / 20 / 0; neg 0 | 1 / 20 / 0; neg 0 |
| 4A8B_lampwarm6_ottoman | close | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampwarm6_ottoman | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm6_ottoman | core | 4 | 0 / 4 / 1 | 0 / 4 / 1 | 0 / 4 / 1 | 0 / 4 / 1 |
| 4A8B_lampwarm6_ottoman | edge | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampwarm6_ottoman | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampwarm6_ottoman | occl | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampwarm6_ottoman | touch | 3 | 0 / 3 / 0 | 0 / 3 / 0 | 0 / 3 / 0 | 0 / 3 / 0 |
| 4A8B_lampwarm6_ottoman | **all** | 15 | 0 / 15 / 1; neg 0 | 0 / 15 / 1; neg 0 | 0 / 15 / 1; neg 0 | 0 / 15 / 1; neg 0 |
| 4A8B_lampwarm6_wood | close | 1 | 0 / 1 / 1 | 0 / 1 / 1 | 0 / 1 / 1 | 0 / 1 / 1 |
| 4A8B_lampwarm6_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm6_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm6_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm6_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampwarm6_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampwarm6_wood | occl | 5 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 |
| 4A8B_lampwarm6_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampwarm6_wood | **all** | 21 | 0 / 21 / 1; neg 0 | 0 / 21 / 1; neg 0 | 0 / 21 / 1; neg 0 | 0 / 21 / 1; neg 0 |
| 4A8B_overheaddim_palewood | close | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| 4A8B_overheaddim_palewood | clutter | 4 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| 4A8B_overheaddim_palewood | core | 4 | 4 / 0 / 1 | 4 / 0 / 1 | 4 / 0 / 1 | 4 / 0 / 1 |
| 4A8B_overheaddim_palewood | edge | 2 | 1 / 1 / 0 | 1 / 1 / 0 | 1 / 1 / 0 | 1 / 1 / 0 |
| 4A8B_overheaddim_palewood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_overheaddim_palewood | occl | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_overheaddim_palewood | touch | 3 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 |
| 4A8B_overheaddim_palewood | **all** | 15 | 12 / 3 / 1; neg 0 | 12 / 3 / 1; neg 0 | 13 / 2 / 1; neg 0 | 13 / 2 / 1; neg 0 |
| 4A8B_window_abpwhite | occlx | 32 | 26 / 6 / 2 | 26 / 6 / 1 | 26 / 6 / 2 | 26 / 6 / 1 |
| 4A8B_window_abpwhite | **all** | 32 | 26 / 6 / 2; neg 1 | 26 / 6 / 1; neg 0 | 26 / 6 / 2; neg 1 | 26 / 6 / 1; neg 0 |
| 4A8B_window_black | close | 3 | 1 / 2 / 0 | 1 / 2 / 0 | 1 / 2 / 0 | 1 / 2 / 0 |
| 4A8B_window_black | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_window_black | clutter | 4 | 1 / 3 / 1 | 1 / 3 / 1 | 1 / 3 / 1 | 1 / 3 / 1 |
| 4A8B_window_black | far | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_window_black | held | 3 | 1 / 2 / 0 | 1 / 2 / 0 | 1 / 2 / 0 | 1 / 2 / 0 |
| 4A8B_window_black | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_window_black | occl | 6 | 1 / 5 / 0 | 1 / 5 / 0 | 1 / 5 / 0 | 1 / 5 / 0 |
| 4A8B_window_black | touch | 2 | 1 / 1 / 0 | 1 / 1 / 0 | 1 / 1 / 0 | 1 / 1 / 0 |
| 4A8B_window_black | **all** | 26 | 5 / 21 / 1; neg 0 | 5 / 21 / 1; neg 0 | 5 / 21 / 1; neg 0 | 5 / 21 / 1; neg 0 |
| DAVE* | snap | 34 | 13 / 21 / 4 | 13 / 21 / 4 | 13 / 21 / 4 | 13 / 21 / 4 |
| DAVE* | **all** | 34 | 13 / 21 / 4; neg 0 | 13 / 21 / 4; neg 0 | 13 / 21 / 4; neg 0 | 13 / 21 / 4; neg 0 |

## Clause (a), each arm against `start`

| arm | HOME and CAMPUS rows that lose a found barrel | ... that gain a false box | boxes on negative frames, any set | (a) |
|---|---|---|---|---|
| `side` | 0 | 0 | 0 | pass |
| `stripe` | 0 | 0 | 1 | **FAILS** |
| `shape` | 0 | 0 | 0 | pass |

Every scenario row that differs from `start`:

- `side`, 4A8B_window_abpwhite occlx: 26 / 6 / 2 → 26 / 6 / 1 (report only)
- `stripe`, 4A8B_overheaddim_palewood close: 0 / 1 / 0 → 1 / 0 / 0 (report only)
- `shape`, 4A8B_overheaddim_palewood close: 0 / 1 / 0 → 1 / 0 / 0 (report only)
- `shape`, 4A8B_window_abpwhite occlx: 26 / 6 / 2 → 26 / 6 / 1 (report only)
