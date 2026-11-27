# D. Every box of `cn_alone` that is not on its barrel

The held-out boxes of the judged run. A box is listed when it is on nothing, a second box on a barrel, or on a barrel of the other color. weight = 1 / the lights its arrangement was shot under (how the judge counts it). 'today, this frame' = today's detector (fixed colors) draws a box on the same thing in this frame; 'today, another light' = it does so in another light of the same arrangement (the camera did not move between lights). 'nearmiss' / 'selfcal' = that winner alone draws a box on it in this frame. The object and the check that would remove it are from the pictures, written by hand; no rule was tuned or run on these frames. Made by `analysis.py boxes`.

## Ordinary conditions (these are the boxes the judge counted): 9 boxes, 2.83 counted once per arrangement; 5 of them (1.93) are also drawn by today's detector in the same frame

| frame | color | box | state | weight | frame kind | today, this frame | today, another light | nearmiss | selfcal | contrast | object (from the picture) | what kind of check would remove it |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lampmid3_bathtile_core_01 | orange | [218, 104, 256, 145] | second | 0.25 | - | no | lampcool6 | yes | yes | yes | a second orange box on the upper half of a near orange barrel that already has its full box (top to the stripe); both winners draw it alone too | one box per barrel: a box whose columns lie inside a surer same-color box and whose bottom sits on that box's stripe is the same barrel (a duplicate rule with 'inside' instead of IoU > 0.5) |
| lampmid3_glass_occl_02 | orange | [577, 117, 636, 167] | nothing | 0.20 | - | yes | no | yes | yes | yes | the same jar; today's detector boxes it too in this frame | today's box: fixed colors paint red side and blue label at full strength. A body test on both sides of the band (orange above AND below at full height) or the jar's gold lid above the 'top' |
| lampmid6_glass_clutter_01 | orange | [554, 117, 604, 171] | nothing | 0.20 | - | yes | lampmid3, lampwarm6, window | yes | yes | yes | the jar again; today's detector draws the same box (and in three other lights of this arrangement) | already today's: not caused by the combination |
| lampwarm6_bathtile_core_01 | orange | [465, 104, 495, 134] | wrong color | 0.25 | - | no | no | no | no | yes | an orange box on the upper left of a blue barrel that also gets its own (right) blue box: under the warm lamp the orange floor behind and the barrel's orange stripe read as an orange barrel's body | self-calibration's seed rule (a box of the other color on a found barrel is dropped), or one box per barrel |
| lampwarm6_glass_clutter_01 | orange | [555, 117, 605, 172] | nothing | 0.20 | - | yes | lampmid3, lampmid6, window | yes | yes | yes | the jar again; today's detector draws the same box | already today's |
| lampwarm6_glass_occl_02 | orange | [566, 101, 595, 133] | nothing | 0.20 | - | no | no | no | no | yes | the red jar with the blue label and gold lid under the warm lamp: contrast reads the label as a stripe between the red jar and the gold lid and paints it; two small boxes stacked on it | one thing, two boxes stacked in the same columns (no two barrels stand one above the other at those rows); or a second reading (neither other winner draws it) |
| lampwarm6_glass_occl_02 | orange | [572, 94, 594, 118] | nothing | 0.20 | - | no | no | no | no | yes | the same jar, the upper of the two stacked boxes | as above |
| lampwarm6_ottoman_core_01 | orange | [166, 248, 282, 480] | nothing | 0.33 | - | yes | no | yes | yes | yes | a close-up box on orange glints of the woven ottoman under the warm lamp; today's detector draws it too | already today's. Shape: the piece is a sparse speckle, under a quarter of its box painted |
| overheaddim_palewood_core_01 | orange | [235, 273, 564, 480] | nothing | 1.00 | - | yes | no | yes | yes | yes | a close-up box 329 px wide on the pale wood grain that the fixed orange range paints; today's detector draws it too | already today's. Size for the row: a close-up barrel cut by the frame bottom at row 273 is about 150 px wide, not 329; or shape (speckled grain) |

## Extreme conditions (report only): 6 boxes, 1.00 counted once per arrangement; 4 of them (0.67) are also drawn by today's detector in the same frame

| frame | color | box | state | weight | frame kind | today, this frame | today, another light | nearmiss | selfcal | contrast | object (from the picture) | what kind of check would remove it |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lampcool6_wood_cluster_01 | orange | [220, 115, 268, 163] | wrong color | 0.17 | - | yes | no | no | yes | yes | an orange box on a blue barrel among three; today's detector draws it too | already today's |
| lampcool6_wood_occl_02 | orange | [186, 131, 261, 215] | wrong color | 0.17 | - | yes | no | yes | yes | yes | an orange box on a blue barrel (the wood around it paints orange); today too | already today's |
| lampmid3_wood_close_01 | orange | [214, 231, 458, 469] | wrong color | 0.17 | - | yes | lampcool3, lampcool6, lampmid6, lampwarm3, lampwarm6 | yes | yes | yes | a close-up box on orange wood grain beside a close blue barrel; today too | already today's; size for the row |
| lampmid6_wood_cluster_01 | orange | [190, 112, 233, 159] | nothing | 0.17 | - | no | no | no | yes | yes | orange wood between barrels in the cluster on the wood desk | a second reading |
| lampwarm6_wood_close_01 | orange | [102, 265, 512, 480] | wrong color | 0.17 | - | yes | lampcool3, lampcool6, lampmid3, lampmid6, lampwarm3 | yes | yes | yes | a close-up box on the orange wood under the warm lamp; today too | already today's; size for the row |
| lampwarm6_wood_cluster_01 | orange | [209, 129, 269, 193] | wrong color | 0.17 | - | no | lampcool6 | no | no | yes | an orange box on a blue barrel in the cluster under the warm lamp on the orange wood | the other color on a found barrel |

## Every candidate, ordinary conditions: boxes not on their barrel, per frame

| candidate | on nothing | second box | wrong color | counted once per arrangement |
|---|---|---|---|---|
| today | 5 | 0 | 0 | 1.93 |
| `nearmiss` | 9 | 2 | 1 | 3.57 |
| `selfcal` | 5 | 1 | 0 | 2.18 |
| `nm_then_sc` | 10 | 2 | 1 | 4.57 |
| `sc_then_nm` | 10 | 2 | 0 | 4.32 |
| `mask_union` | 9 | 2 | 0 | 3.32 |
| `box_union` | 9 | 2 | 1 | 3.57 |
| `box_agree` | 5 | 1 | 0 | 2.18 |
| `cn_alone` | 7 | 1 | 1 | 2.83 |
| `cn_on_nm` | 11 | 2 | 2 | 4.22 |
| `cn_on_sc` | 9 | 1 | 2 | 3.58 |
| `cn_on_all` | 13 | 2 | 2 | 4.72 |
| `cn_box_nm` | 11 | 2 | 2 | 4.22 |
| `cn_box_sc` | 7 | 1 | 1 | 2.83 |
| `cn_box_all` | 11 | 2 | 1 | 3.97 |

