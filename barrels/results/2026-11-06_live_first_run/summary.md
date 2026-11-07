# First live run, 2026-11-06 — what the detector did on Tanush's screenshots (approximate: masks rebuilt from the tint)

git c44432a; camera AIM_4A8B6118_BOXFIT; DetConfig defaults. Columns: body color the band sits between; band x, y, size; pixels of the other barrel color (a real stripe) and unlabeled pixels (shadow) inside it; expected barrel width / stripe height at that row.

## board_a_both

rebuilt mask: 22369 orange px, 13658 blue px

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 255-259 | 134-197 | 4×63 | 0 | 252 | 62 / 16 | dropped: stripe height 63 not in 7-25; band 63 taller than 47; narrower than 25; taller than wide |
| orange | 297-312 | 141-165 | 15×24 | 0 | 360 | 53 / 14 | dropped: stripe height 24 not in 6-22; narrower than 21; taller than wide |
| orange | 316-372 | 141-168 | 56×27 | 0 | 1226 | 54 / 14 | dropped: stripe height 27 not in 6-22 |
| orange | 179-188 | 169-224 | 9×55 | 133 | 276 | 83 / 20 | dropped: narrower than 33; taller than wide |
| orange | 294-331 | 177-200 | 37×23 | 0 | 707 | 78 / 19 | **KEPT → a barrel** |
| orange | 286-448 | 200-292 | 162×92 | 3645 | 2758 | 118 / 28 | dropped: band 92 taller than 83 |
| blue | 76-184 | 216-261 | 108×45 | 2921 | 171 | 113 / 27 | **KEPT → a barrel** |

detect() returns:

- blue x 76-184 y 168-295 from det2 [] conf 0.97
- orange x 294-372 y 134-222 from det2 ['bottom_inferred', 'occluded'] conf 0.50

## board_b_both

rebuilt mask: 20141 orange px, 13927 blue px

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 308-458 | 144-306 | 150×162 | 3793 | 1958 | 103 / 25 | dropped: band 162 taller than 74 |
| orange | 420-456 | 268-306 | 36×38 | 0 | 588 | 146 / 33 | dropped: narrower than 59; taller than wide |
| orange | 326-362 | 293-306 | 36×13 | 0 | 241 | 155 / 34 | dropped: stripe height 13 not in 15-55; narrower than 62 |
| blue | 89-196 | 182-231 | 107×49 | 2994 | 239 | 90 / 22 | **KEPT → a barrel** |

detect() returns:

- blue x 89-196 y 134-249 from det2 ['bottom_inferred'] conf 0.96

## board_c_both

rebuilt mask: 19901 orange px, 12584 blue px

| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |
|---|---|---|---|---|---|---|---|
| orange | 0-17 | 58-123 | 17×65 | 0 | 547 | 10 / 3 | dropped: too far; stripe height 65 not in 1-4; band 65 taller than 8; taller than wide |
| orange | 375-454 | 141-218 | 79×77 | 0 | 2313 | 72 / 18 | dropped: stripe height 77 not in 8-29; band 77 taller than 54 |
| orange | 85-100 | 147-220 | 15×73 | 233 | 826 | 74 / 19 | dropped: stripe height 73 not in 8-30; band 73 taller than 56; narrower than 30; taller than wide |
| orange | 296-447 | 173-284 | 151×111 | 3392 | 3172 | 106 / 25 | dropped: band 111 taller than 75 |
| blue | 97-199 | 203-252 | 102×49 | 2827 | 196 | 105 / 25 | **KEPT → a barrel** |

detect() returns:

- blue x 97-199 y 157-286 from det2 [] conf 0.97

## hand_raw (a raw frame, the real live path on the resized screenshot)

per-image saturation floor from the top rows: orange 120, blue 120 (clamp 20-120); segmentation: 0 orange px, 0 blue px; no barrels
