# D. Every box of `mask_union` that is not on its barrel

The held-out boxes of the judged run. A box is listed when it is on nothing, a second box on a barrel, or on a barrel of the other color. weight = 1 / the lights its arrangement was shot under (how the judge counts it). 'today, this frame' = today's detector (fixed colors) draws a box on the same thing in this frame; 'today, another light' = it does so in another light of the same arrangement (the camera did not move between lights). 'nearmiss' / 'selfcal' = that winner alone draws a box on it in this frame. The object and the check that would remove it are from the pictures, written by hand; no rule was tuned or run on these frames. Made by `analysis.py boxes`.

## Ordinary conditions (these are the boxes the judge counted): 11 boxes, 3.32 counted once per arrangement; 5 of them (1.93) are also drawn by today's detector in the same frame

| frame | color | box | state | weight | frame kind | today, this frame | today, another light | nearmiss | selfcal | object (from the picture) | what kind of check would remove it |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lampcool6_glass_neg_02 | orange | [555, 124, 604, 171] | nothing | 0.20 | empty frame with clutter | no | no | yes | no | the red jar with a blue label and a gold lid (empty frame). The near-miss body direction paints the jar's red-brown side and the glass reflection under it orange around the strict blue label | a second reading: self-calibration's photo check does not keep it (box_agree drops it); or shape: the 'stripe' (label) is taller than a stripe and the orange is on one side only |
| lampcool6_glass_occl_02 | orange | [560, 123, 610, 170] | nothing | 0.20 | - | no | lampmid3 | yes | no | the same jar, same place (the barrels are elsewhere in the frame) | as above |
| lampmid3_bathtile_core_01 | orange | [218, 104, 256, 145] | second | 0.25 | - | no | lampcool6 | yes | yes | a second orange box on the upper half of a near orange barrel that already has its full box (top to the stripe); both winners draw it alone too | one box per barrel: a box whose columns lie inside a surer same-color box and whose bottom sits on that box's stripe is the same barrel (a duplicate rule with 'inside' instead of IoU > 0.5) |
| lampmid3_glass_neg_02 | orange | [560, 123, 609, 171] | nothing | 0.20 | empty frame with clutter | no | no | yes | no | the same jar (empty frame) | as above |
| lampmid3_glass_occl_02 | orange | [577, 117, 636, 167] | nothing | 0.20 | - | yes | no | yes | yes | the same jar; today's detector boxes it too in this frame | today's box: fixed colors paint red side and blue label at full strength. A body test on both sides of the band (orange above AND below at full height) or the jar's gold lid above the 'top' |
| lampmid6_glass_clutter_01 | blue | [490, 98, 516, 125] | nothing | 0.20 | - | no | no | yes | no | a small gray-blue clutter object behind the barrels with an orange strip across it; the near-miss body direction paints its gray-blue part as blue body under the strip | a second reading (self-calibration does not draw it; its log(R/B) test would refuse a gray body); size: the box is 26 px wide, at the small end for its row |
| lampmid6_glass_clutter_01 | orange | [554, 117, 604, 171] | nothing | 0.20 | - | yes | lampmid3, lampwarm6, window | yes | yes | the jar again; today's detector draws the same box (and in three other lights of this arrangement) | already today's: not caused by the combination |
| lampmid6_ottoman_core_01 | blue | [120, 139, 186, 203] | second | 0.33 | - | no | no | yes | no | a second blue box shifted right of a blue barrel, reaching onto the lid of the near orange barrel; the near-miss step painted that lid's dark edge blue | one box per barrel (overlaps the barrel's own box over most of its rows), or size for the row: 66 px wide where a barrel is about 48 |
| lampwarm6_glass_clutter_01 | orange | [555, 117, 605, 172] | nothing | 0.20 | - | yes | lampmid3, lampmid6, window | yes | yes | the jar again; today's detector draws the same box | already today's |
| lampwarm6_ottoman_core_01 | orange | [166, 248, 282, 480] | nothing | 0.33 | - | yes | no | yes | yes | a close-up box on orange glints of the woven ottoman under the warm lamp; today's detector draws it too | already today's. Shape: the piece is a sparse speckle, under a quarter of its box painted |
| overheaddim_palewood_core_01 | orange | [235, 273, 564, 480] | nothing | 1.00 | - | yes | no | yes | yes | a close-up box 329 px wide on the pale wood grain that the fixed orange range paints; today's detector draws it too | already today's. Size for the row: a close-up barrel cut by the frame bottom at row 273 is about 150 px wide, not 329; or shape (speckled grain) |

## Extreme conditions (report only): 6 boxes, 1.00 counted once per arrangement; 4 of them (0.67) are also drawn by today's detector in the same frame

| frame | color | box | state | weight | frame kind | today, this frame | today, another light | nearmiss | selfcal | object (from the picture) | what kind of check would remove it |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lampcool3_wood_clutter_01 | blue | [232, 121, 287, 173] | wrong color | 0.17 | - | no | no | yes | yes | an orange barrel with a blue stripe boxed blue: both steps paint its washed-out orange body as blue (cyan) under the cool lamp on the wood | a second reading of the color (log R/B of the body against the stripe would say orange body) |
| lampcool6_wood_cluster_01 | orange | [220, 115, 268, 163] | wrong color | 0.17 | - | yes | no | no | yes | an orange box on a blue barrel among three; today's detector draws it too | already today's |
| lampcool6_wood_occl_02 | orange | [186, 131, 261, 215] | wrong color | 0.17 | - | yes | no | yes | yes | an orange box on a blue barrel (the wood around it paints orange); today too | already today's |
| lampmid3_wood_close_01 | orange | [214, 231, 458, 469] | wrong color | 0.17 | - | yes | lampcool3, lampcool6, lampmid6, lampwarm3, lampwarm6 | yes | yes | a close-up box on orange wood grain beside a close blue barrel; today too | already today's; size for the row |
| lampmid6_wood_touch_02 | orange | [191, 107, 225, 144] | nothing | 0.17 | - | no | no | yes | no | orange paper on the wall behind two touching barrels, painted by the near-miss body direction above an orange band | the top: it sits above the horizon gate's band of the barrels behind; a second reading (self-calibration does not draw it) |
| lampwarm6_wood_close_01 | orange | [102, 265, 512, 480] | wrong color | 0.17 | - | yes | lampcool3, lampcool6, lampmid3, lampmid6, lampwarm3 | yes | yes | a close-up box on the orange wood under the warm lamp; today too | already today's; size for the row |

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

