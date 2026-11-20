# The eval table of every arm

git b4defce; v2 rule; train frames only; adopted color model; HOME leave-one-scene-out. Each cell: found / missed / false (on a set's `all` row: then the boxes on its negative frames). HOME and CAMPUS decide (PREREG clause (a)); the other sets are report only, except that no set may have a box on a negative frame. `*` = indicative labels.

| set | scenario | barrels | `stack` | `before` | `combined` | `combined+thin` | `combined+cover` |
|---|---|---|---|---|---|---|---|
| HOME | close | 2 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 |
| HOME | cluster | 8 | 7 / 1 / 0 | 6 / 2 / 0 | 7 / 1 / 0 | 7 / 1 / 0 | 7 / 1 / 0 |
| HOME | core | 5 | 5 / 0 / 0 | 5 / 0 / 0 | 5 / 0 / 0 | 5 / 0 / 0 | 5 / 0 / 0 |
| HOME | edge | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| HOME | far | 4 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| HOME | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| HOME | occl | 4 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| HOME | top | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| HOME | topstripe | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| HOME | touch | 3 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 |
| HOME | **all** | 29 | 28 / 1 / 0; neg 0 | 27 / 2 / 0; neg 0 | 28 / 1 / 0; neg 0 | 28 / 1 / 0; neg 0 | 28 / 1 / 0; neg 0 |
| CAMPUS | close | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| CAMPUS | cluster | 4 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| CAMPUS | clutter | 3 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 |
| CAMPUS | core | 4 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| CAMPUS | edge | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| CAMPUS | far | 4 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| CAMPUS | hand | 2 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 |
| CAMPUS | held | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| CAMPUS | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| CAMPUS | occl | 1 | 1 / 0 / 0 | 0 / 1 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| CAMPUS | plain | 4 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| CAMPUS | room | 4 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 | 4 / 0 / 0 |
| CAMPUS | top | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| CAMPUS | topstripe | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| CAMPUS | touch | 2 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 |
| CAMPUS | window | 2 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 |
| CAMPUS | **all** | 35 | 35 / 0 / 0; neg 0 | 34 / 1 / 0; neg 0 | 35 / 0 / 0; neg 0 | 35 / 0 / 0; neg 0 | 35 / 0 / 0; neg 0 |
| 4A8B_lampcool1_wood | close | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampcool1_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool1_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool1_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool1_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampcool1_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampcool1_wood | occl | 5 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 |
| 4A8B_lampcool1_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampcool1_wood | **all** | 21 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 |
| 4A8B_lampcool3_wood | close | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| 4A8B_lampcool3_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool3_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool3_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool3_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampcool3_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampcool3_wood | occl | 5 | 1 / 4 / 0 | 1 / 4 / 0 | 1 / 4 / 0 | 1 / 4 / 0 | 1 / 4 / 0 |
| 4A8B_lampcool3_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampcool3_wood | **all** | 21 | 2 / 19 / 0; neg 0 | 2 / 19 / 0; neg 0 | 2 / 19 / 0; neg 0 | 2 / 19 / 0; neg 0 | 2 / 19 / 0; neg 0 |
| 4A8B_lampcool6_wood | close | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| 4A8B_lampcool6_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 1 | 0 / 4 / 1 | 0 / 4 / 1 |
| 4A8B_lampcool6_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool6_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampcool6_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampcool6_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampcool6_wood | occl | 5 | 1 / 4 / 2 | 1 / 4 / 2 | 1 / 4 / 2 | 1 / 4 / 2 | 1 / 4 / 2 |
| 4A8B_lampcool6_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampcool6_wood | **all** | 21 | 2 / 19 / 2; neg 0 | 2 / 19 / 2; neg 0 | 2 / 19 / 3; neg 0 | 2 / 19 / 3; neg 0 | 2 / 19 / 3; neg 0 |
| 4A8B_lampmid1_wood | close | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampmid1_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid1_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid1_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid1_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampmid1_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampmid1_wood | occl | 5 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 |
| 4A8B_lampmid1_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampmid1_wood | **all** | 21 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 |
| 4A8B_lampmid3_wood | close | 1 | 1 / 0 / 1 | 1 / 0 / 1 | 1 / 0 / 1 | 1 / 0 / 1 | 1 / 0 / 1 |
| 4A8B_lampmid3_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid3_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid3_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid3_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampmid3_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampmid3_wood | occl | 5 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 |
| 4A8B_lampmid3_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampmid3_wood | **all** | 21 | 1 / 20 / 1; neg 0 | 1 / 20 / 1; neg 0 | 1 / 20 / 1; neg 0 | 1 / 20 / 1; neg 0 | 1 / 20 / 1; neg 0 |
| 4A8B_lampmid6_wood | close | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| 4A8B_lampmid6_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid6_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid6_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampmid6_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampmid6_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampmid6_wood | occl | 5 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 |
| 4A8B_lampmid6_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampmid6_wood | **all** | 21 | 1 / 20 / 0; neg 0 | 1 / 20 / 0; neg 0 | 1 / 20 / 0; neg 0 | 1 / 20 / 0; neg 0 | 1 / 20 / 0; neg 0 |
| 4A8B_lampwarm1_wood | close | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampwarm1_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm1_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm1_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm1_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampwarm1_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampwarm1_wood | occl | 5 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 |
| 4A8B_lampwarm1_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampwarm1_wood | **all** | 21 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 | 0 / 21 / 0; neg 0 |
| 4A8B_lampwarm3_wood | close | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |
| 4A8B_lampwarm3_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm3_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm3_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm3_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampwarm3_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampwarm3_wood | occl | 5 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 |
| 4A8B_lampwarm3_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampwarm3_wood | **all** | 21 | 1 / 20 / 0; neg 0 | 1 / 20 / 0; neg 0 | 1 / 20 / 0; neg 0 | 1 / 20 / 0; neg 0 | 1 / 20 / 0; neg 0 |
| 4A8B_lampwarm6_wood | close | 1 | 0 / 1 / 1 | 0 / 1 / 1 | 0 / 1 / 1 | 0 / 1 / 1 | 0 / 1 / 1 |
| 4A8B_lampwarm6_wood | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm6_wood | clutter | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm6_wood | core | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_lampwarm6_wood | held | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| 4A8B_lampwarm6_wood | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_lampwarm6_wood | occl | 5 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 | 0 / 5 / 0 |
| 4A8B_lampwarm6_wood | touch | 2 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 | 0 / 2 / 0 |
| 4A8B_lampwarm6_wood | **all** | 21 | 0 / 21 / 1; neg 0 | 0 / 21 / 1; neg 0 | 0 / 21 / 1; neg 0 | 0 / 21 / 1; neg 0 | 0 / 21 / 1; neg 0 |
| 4A8B_window_black | close | 3 | 1 / 2 / 0 | 1 / 2 / 0 | 1 / 2 / 0 | 1 / 2 / 0 | 1 / 2 / 0 |
| 4A8B_window_black | cluster | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_window_black | clutter | 4 | 1 / 3 / 1 | 0 / 4 / 1 | 1 / 3 / 1 | 1 / 3 / 1 | 1 / 3 / 1 |
| 4A8B_window_black | far | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 | 0 / 4 / 0 |
| 4A8B_window_black | held | 3 | 1 / 2 / 0 | 1 / 2 / 0 | 1 / 2 / 0 | 1 / 2 / 0 | 1 / 2 / 0 |
| 4A8B_window_black | neg | 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 4A8B_window_black | occl | 6 | 1 / 5 / 0 | 0 / 6 / 0 | 1 / 5 / 0 | 1 / 5 / 0 | 3 / 3 / 0 |
| 4A8B_window_black | touch | 2 | 1 / 1 / 0 | 1 / 1 / 0 | 1 / 1 / 0 | 1 / 1 / 0 | 1 / 1 / 0 |
| 4A8B_window_black | **all** | 26 | 5 / 21 / 1; neg 0 | 3 / 23 / 1; neg 0 | 5 / 21 / 1; neg 0 | 5 / 21 / 1; neg 0 | 7 / 19 / 1; neg 0 |
| DAVE* | snap | 34 | 12 / 22 / 3 | 12 / 22 / 2 | 12 / 22 / 4 | 12 / 22 / 4 | 12 / 22 / 3 |
| DAVE* | **all** | 34 | 12 / 22 / 3; neg 0 | 12 / 22 / 2; neg 0 | 12 / 22 / 4; neg 0 | 12 / 22 / 4; neg 0 | 12 / 22 / 3; neg 0 |

## Clause (a), each arm against `stack`

| arm | HOME and CAMPUS rows that lose a found barrel | ... that gain a false box | boxes on negative frames, any set | (a) |
|---|---|---|---|---|
| `before` | 2 | 0 | 0 | **FAILS** |
| `combined` | 0 | 0 | 0 | pass |
| `combined+thin` | 0 | 0 | 0 | pass |
| `combined+cover` | 0 | 0 | 0 | pass |

Every scenario row that differs from `stack`:

- `before`, HOME cluster: 7 / 1 / 0 → 6 / 2 / 0
- `before`, CAMPUS occl: 1 / 0 / 0 → 0 / 1 / 0
- `before`, 4A8B_window_black clutter: 1 / 3 / 1 → 0 / 4 / 1 (report only)
- `before`, 4A8B_window_black occl: 1 / 5 / 0 → 0 / 6 / 0 (report only)
- `before`, DAVE* snap: 12 / 22 / 3 → 12 / 22 / 2 (report only)
- `combined`, 4A8B_lampcool6_wood cluster: 0 / 4 / 0 → 0 / 4 / 1 (report only)
- `combined`, DAVE* snap: 12 / 22 / 3 → 12 / 22 / 4 (report only)
- `combined+thin`, 4A8B_lampcool6_wood cluster: 0 / 4 / 0 → 0 / 4 / 1 (report only)
- `combined+thin`, DAVE* snap: 12 / 22 / 3 → 12 / 22 / 4 (report only)
- `combined+cover`, 4A8B_lampcool6_wood cluster: 0 / 4 / 0 → 0 / 4 / 1 (report only)
- `combined+cover`, 4A8B_window_black occl: 1 / 5 / 0 → 3 / 3 / 0 (report only)
