# Bottom edges: where each box's bottom comes from, and its distance from the hand-drawn bottom

HOME (leave-one-scene-out) and CAMPUS train frames, adopted color model. `on a barrel` = same color, IoU >= 0.5 with a hand-drawn box (the bottom rule not asked). Error = box bottom row - hand-drawn bottom row, px (+ = lower). `within` = inside the v2 bottom tolerance (a tenth of the hand-drawn height, at least 3 px).

| arm | set | boxes | on a barrel | within the v2 bottom tolerance | median abs error, px | median signed error, px |
|---|---|---|---|---|---|---|
| base | HOME | 27 | 27 | 27 | 1.0 | 0.0 |
| base | CAMPUS | 35 | 35 | 35 | 2.0 | -1.0 |

## By where the bottom came from

| arm | set | bottom from | boxes | on a barrel | within | median abs error | median signed error |
|---|---|---|---|---|---|---|---|
| base | HOME | cap, whole width: from the width | 1 | 1 | 1 | 3.0 | 3.0 |
| base | HOME | cap, whole width: seen | 1 | 1 | 1 | 3.0 | -3.0 |
| base | HOME | frame edge | 2 | 2 | 2 | 0.0 | 0.0 |
| base | HOME | stripe: seen | 23 | 23 | 23 | 1.0 | 0.0 |
| base | CAMPUS | frame edge | 3 | 3 | 3 | 2.0 | 2.0 |
| base | CAMPUS | stripe: seen | 32 | 32 | 32 | 2.0 | -1.0 |

## Other ways to work out the bottom, on the same boxes (report only; no box is changed)

Boxes on a barrel whose hand-drawn bottom was seen (no `bottom_estimated`, `occluded` or `truncated` flag on the label), and for which all three estimates apply (top seen, a stripe, not flagged occluded or truncated by the detector). Median abs / median signed error, px.

| arm | set | boxes | the box as drawn | from the top row | from the stripe row | top + height of a barrel as wide as the box |
|---|---|---|---|---|---|---|
| base | HOME | 16 | 1.0 / 0.0 | 7.0 / 3.4 | 1.6 / -1.6 | 4.0 / -3.4 |
| base | CAMPUS | 20 | 2.0 / -2.0 | 5.8 / 3.4 | 3.0 / -3.0 | 4.0 / -1.1 |

## Every box whose bottom is not a seen one

| arm | frame | color | box | bottom from | hand-drawn | error | tolerance | counted found |
|---|---|---|---|---|---|---|---|---|
| base | window_light_occl_02 | orange | [399, 117, 439, 161] | cap, whole width: from the width | [395, 114, 441, 158] | 3 | 4.4 | 1 |
| base | window_light_top_01 | orange | [164, 260, 449, 480] | frame edge | [163, 259, 452, 480] | 0 | 22.1 | 1 |
| base | window_light_topstripe_01 | orange | [176, 242, 423, 480] | frame edge | [173, 240, 426, 480] | 0 | 24.0 | 1 |
| base | campus_light_held_01 | blue | [98, 334, 505, 480] | frame edge | [97, 332, 512, 479] | 1 | 14.7 | 1 |
| base | campus_light_top_01 | orange | [167, 281, 479, 480] | frame edge | [160, 280, 493, 478] | 2 | 19.8 | 1 |
| base | campus_light_topstripe_01 | orange | [230, 241, 463, 480] | frame edge | [221, 238, 468, 477] | 3 | 23.9 | 1 |
