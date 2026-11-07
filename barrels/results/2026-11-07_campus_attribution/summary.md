# Campus session 2026-11-07 — attribution on the 21 train frames

git 091a616; model afd85483 (frozen v1), detector DetConfig() (the stripe step), camera AIM_4A8B6118_BOXFIT. Expected = barrels of each body color counted by eye (`expected.json`); `floor40` = the same model with the saturation floor fixed at 40. Verdict/notes = hand judgments from the sheets (`judgments.json`).

| frame | expected O/B | floor | bg rej | table rej | orange px | blue px | boxes O/B | floor40: px O/B, boxes O/B | verdict | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| close_01 | 1/0 | 67 | 0.492 | nan | 6108 | 425 | 0/0 | 6905/498, 0/0 | seg+det | shaded right half of the orange body unlabeled (prior: 17 % of shaded orange survives); the blue stripe's band then includes that shadow, 72 rows vs 55 allowed: glued shadow |
| cluster_02 | 2/2 | 69 | 0.382 | nan | 2040 | 29 | 0/0 | 2099/29, 0/0 | seg | both blue bodies 5 % labeled (prior + floor 69); near orange shaded half unlabeled; no stripe has body above and below |
| clutter_02 | 1/2 | 120 | 0.411 | nan | 1868 | 0 | 0/0 | 2359/0, 0/0 | seg | floor at its clamp 120 (clutter in the top rows): blue 0 px, orange body partial; the orange glue-stick cap and the pill-bottle cap are labeled orange but draw no box |
| core_01 | 2/2 | 73 | 0.463 | nan | 2573 | 4883 | 2/0 | 2852/5110, 1/0 | seg+det | big blue barrel: body 43 % labeled, stripe band 97 rows vs 72 allowed (glued shadow); far small orange outside the orange box (20 %); touching pair: two ORANGE boxes, one on the blue barrel (wrong color), its own blue stripe dropped (band 52 vs 46, glued shadow) |
| edge_01 | 1/0 | 73 | 0.345 | nan | 1022 | 0 | 0/0 | 1124/0, 0/0 | seg | orange body at the frame edge labeled only on its lit part; no stripe anchored |
| far_01 | 2/2 | 71 | 0.427 | nan | 1553 | 823 | 2/1 | 1619/851, 3/1 | seg | 3 of 4 right (2 orange, 1 blue); the second blue barrel's body 34-47 % labeled (prior + floor 71), no band closed around its stripe |
| hand_02 | 1/1 | 57 | 0.293 | nan | 2165 | 1439 | 1/1 | 2428/1886, 1/1 | ok | both boxes right; the hand is not labeled orange (floor 57 kept skin out); the blue box is widened as 'occluded' because the stripe's labeled part is narrow |
| held_01 | 0/1 | 120 | 0.495 | nan | 1200 | 87 | 0/0 | 1798/314, 0/0 | seg | held barrel (lid only, bottom of frame): 87 blue px of a 60k-px lid; floor at clamp 120 from the clutter. Out of the v2 arrangements; recorded only |
| neg_02 | 0/0 | 33 | 0.382 | nan | 0 | 0 | 0/0 | 0/0, 0/0 | ok | laptop lid: nothing labeled, nothing drawn |
| neg_03 | 0/0 | 92 | 0.311 | nan | 8 | 0 | 0/0 | 51/0, 0/0 | ok | empty table, room behind: 8 orange px, nothing drawn |
| neg_04 | 0/0 | 83 | 0.346 | nan | 0 | 0 | 0/0 | 100/0, 0/0 | ok | clutter: nothing drawn |
| neg_05 | 0/0 | 120 | 0.361 | nan | 1255 | 0 | 0/0 | 2099/10, 0/0 | ok | orange cap + orange glue stick labeled orange (1255 px), no box: nothing sandwiches a band. The detector did its job here |
| occl_02 | 0/1 | 74 | 0.392 | nan | 141 | 51 | 0/0 | 146/31, 0/0 | seg | blue barrel behind the marker: 51 blue px |
| plain_01 | 1/1 | 49 | 0.3 | nan | 7306 | 5112 | 1/0 | 7414/5448, 1/0 | seg+det | orange right; blue barrel: body 41-69 % labeled, its stripe band 67 rows vs 62 allowed (glued shadow) |
| plain_02 | 1/1 | 50 | 0.307 | nan | 3205 | 2313 | 1/0 | 3270/2630, 1/0 | seg+det | as plain_01 at 15 cm: orange right, blue missed |
| room_01 | 1/1 | 86 | 0.711 | nan | 505 | 0 | 0/0 | 588/0, 0/0 | seg | blue body 0 % (prior rejects 71 % of the frame: top rows are a dark room, scale 42-52 per channel; floor 86 > the body's saturation 52-71); orange body 33 % |
| room_03 | 1/1 | 83 | 0.715 | nan | 111 | 0 | 0/0 | 126/0, 0/0 | seg | both barrels at 25 cm: 111 orange px, 0 blue px |
| top_01 | 1/0 | 67 | 0.554 | nan | 11794 | 0 | 1/0 | 22030/0, 1/0 | ok | lid only: a det1 box covering the labeled part of the lid (the shaded half unlabeled, so the box is narrow); acceptable for the out-of-scope 'top' arrangement |
| topstripe_01 | 1/0 | 67 | 0.468 | nan | 16892 | 8 | 1/0 | 20289/574, 1/0 | ok | det1 box on the lid; shaded half unlabeled; stripe at the frame bottom not used |
| touch_02 | 0/2 | 68 | 0.331 | nan | 257 | 132 | 0/0 | 259/140, 0/0 | seg | two blue bodies 4-7 % labeled (prior), orange stripes partly: nothing to anchor |
| window_01 | 1/1 | 49 | 0.297 | nan | 2445 | 1414 | 0/0 | 2541/1487, 0/0 | seg+det | orange: band 35 rows vs 27 (glued shadow); blue: stripe band 25 px wide vs 26 required (0.4 of a barrel) — a one-pixel miss on a partly labeled stripe |

Frames judged: 21 of 21; ok: 7, seg: 9, seg+det: 5


## The stripe finder, band by band

Columns: body color the band sits between; band x, y, size; pixels of the other barrel color (a real stripe) and unlabeled pixels (shadow) inside it; expected barrel width / stripe height at that row. Bands under 200 px are not listed.

### close_01

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 266-292 | 197-265 | 26×68 | 0 | 885 | 107 / 25 | dropped: stripe height 68 not in 11-41; narrower than 43; taller than wide |
| orange | 269-314 | 264-336 | 45×72 | 424 | 1581 | 156 / 34 | dropped: stripe height 72 not in 15-55; narrower than 62; taller than wide |

detect() returns nothing.


### cluster_02

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 237-258 | 132-155 | 21×23 | 2 | 317 | 47 / 12 | dropped: stripe height 23 not in 5-19; taller than wide |
| orange | 288-314 | 155-193 | 26×38 | 2 | 546 | 68 / 17 | dropped: stripe height 38 not in 8-27; narrower than 27; taller than wide |

detect() returns nothing.


### clutter_02

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 206-222 | 146-178 | 16×32 | 0 | 331 | 59 / 15 | dropped: stripe height 32 not in 7-24; narrower than 24; taller than wide |

detect() returns nothing.


### core_01

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 398-423 | 136-178 | 25×42 | 207 | 599 | 56 / 14 | **KEPT → a barrel** |
| orange | 424-458 | 138-180 | 34×42 | 333 | 759 | 57 / 15 | **KEPT → a barrel** |
| orange | 136-162 | 227-250 | 26×23 | 0 | 444 | 113 / 27 | dropped: narrower than 45 |
| blue | 366-389 | 138-190 | 23×52 | 177 | 399 | 61 / 15 | dropped: band 52 taller than 46; narrower than 24 |
| blue | 144-186 | 173-270 | 42×97 | 748 | 826 | 101 / 24 | dropped: band 97 taller than 72 |
| blue | 136-146 | 176-221 | 10×45 | 0 | 330 | 85 / 21 | dropped: stripe height 45 not in 9-33; narrower than 34; taller than wide |

detect() returns:

- orange x 378-443 y 132-198 from det2 ['occluded'] conf 0.63
- orange x 408-474 y 133-200 from det2 ['occluded'] conf 0.65

### edge_01

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 612-630 | 166-216 | 18×50 | 0 | 562 | 80 / 20 | dropped: stripe height 50 not in 9-31; narrower than 32; taller than wide |

detect() returns nothing.


### far_01

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 380-407 | 125-140 | 27×15 | 58 | 222 | 39 / 10 | **KEPT → a barrel** |
| orange | 199-229 | 129-148 | 30×19 | 116 | 250 | 43 / 11 | **KEPT → a barrel** |
| blue | 321-340 | 129-144 | 19×15 | 140 | 81 | 42 / 11 | **KEPT → a barrel** |

detect() returns:

- orange x 192-236 y 118-160 from det2 ['occluded'] conf 0.66
- blue x 310-351 y 116-153 from det2 ['occluded'] conf 0.82
- orange x 374-413 y 114-149 from det2 ['occluded'] conf 0.60

### hand_02

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 394-440 | 145-168 | 46×23 | 355 | 368 | 56 / 14 | **KEPT → a barrel** |
| blue | 143-178 | 148-177 | 35×29 | 279 | 445 | 60 / 15 | **KEPT → a barrel** |

detect() returns:

- blue x 120-178 y 128-184 from det2 ['occluded'] conf 0.69
- orange x 394-440 y 126-184 from det2 [] conf 0.75

### held_01

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 436-443 | 70-146 | 7×76 | 0 | 454 | 22 / 6 | dropped: stripe height 76 not in 3-9; band 76 taller than 18; narrower than 9; taller than wide |

detect() returns nothing.


### neg_02

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|

detect() returns nothing.


### neg_03

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|

detect() returns nothing.


### neg_04

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|

detect() returns nothing.


### neg_05

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 435-440 | 77-145 | 5×68 | 0 | 308 | 24 / 6 | dropped: stripe height 68 not in 3-10; band 68 taller than 19; narrower than 10; taller than wide |

detect() returns nothing.


### occl_02

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|

detect() returns nothing.


### plain_01

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 502-591 | 178-216 | 89×38 | 1464 | 529 | 84 / 21 | **KEPT → a barrel** |
| blue | 127-143 | 160-192 | 16×32 | 0 | 407 | 69 / 17 | dropped: stripe height 32 not in 8-28; narrower than 28; taller than wide |
| blue | 72-143 | 165-232 | 71×67 | 1315 | 1445 | 85 / 21 | dropped: band 67 taller than 62 |

detect() returns:

- orange x 502-591 y 146-240 from det2 [] conf 0.87

### plain_02

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 420-479 | 153-180 | 59×27 | 593 | 401 | 63 / 16 | **KEPT → a barrel** |
| blue | 120-140 | 140-183 | 20×43 | 128 | 377 | 59 / 15 | dropped: narrower than 24 |
| blue | 92-109 | 160-197 | 17×37 | 221 | 209 | 71 / 18 | dropped: narrower than 28 |

detect() returns:

- orange x 420-479 y 132-199 from det2 [] conf 0.80

### room_01

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 341-356 | 140-164 | 15×24 | 0 | 253 | 53 / 13 | dropped: stripe height 24 not in 6-22; narrower than 21; taller than wide |

detect() returns nothing.


### room_03

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|

detect() returns nothing.


### top_01

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 335-356 | 286-331 | 21×45 | 0 | 722 | 161 / 35 | dropped: narrower than 65; taller than wide |
| orange | 305-309 | 301-358 | 4×57 | 0 | 225 | 176 / 38 | dropped: narrower than 70; taller than wide |
| orange | 271-280 | 336-391 | 9×55 | 0 | 305 | 200 / 41 | dropped: narrower than 80; taller than wide |
| orange | 232-255 | 370-438 | 23×68 | 0 | 908 | 228 / 45 | dropped: narrower than 91; taller than wide |

detect() returns:

- orange x 167-356 y 280-480 from det1 ['bottom_inferred', 'truncated'] conf 1.00

### topstripe_01

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 238-240 | 69-290 | 2×221 | 0 | 437 | 72 / 18 | dropped: stripe height 221 not in 8-29; band 221 taller than 54; narrower than 29; taller than wide |
| orange | 238-244 | 405-470 | 6×65 | 3 | 348 | 251 / 47 | dropped: narrower than 101; taller than wide |

detect() returns:

- orange x 225-420 y 240-480 from det1 ['bottom_inferred', 'truncated'] conf 1.00

### touch_02

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|

detect() returns nothing.


### window_01

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 397-432 | 157-192 | 35×35 | 123 | 579 | 68 / 17 | dropped: stripe height 35 not in 8-27 |
| blue | 197-222 | 157-183 | 25×26 | 351 | 113 | 65 / 16 | dropped: narrower than 26 |

detect() returns nothing.

