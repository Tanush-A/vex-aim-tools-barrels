# What AB gains and what it still misses (each place with its own held-out setting)

Counted per frame (a placement once per light). 'paint' = what the FIXED colors paint of the barrel's hand box: the body bands and the stripe band, painted when at least half. 'seed' = what happened to the seed candidates on the barrel.

## ordinary conditions: 307 barrels, 211 found by the fixed detector, 248 by AB

### gained, by what the fixed colors painted and by its seed (37)

| paint | seed | n |
|---|---|---|
| body painted, stripe not | kept: body | 15 |
| stripe painted, body not | kept: stripe | 15 |
| both painted | kept: body | 1 |
| body painted, stripe not | refused: stripe:body_like_surround | 1 |
| stripe painted, body not | no seed candidate | 1 |
| body painted, stripe not | no seed candidate | 1 |
| neither painted | kept: stripe | 1 |
| body painted, stripe not | refused: body:not_two_colors+stripe:stripe_not_painted | 1 |
| body painted, stripe not | refused: stripe:not_two_colors | 1 |

### gained without a kept seed of its own (by the frame's ranges) (5)

| condition | seed | frame_moved | n |
|---|---|---|---|
| lampmid6_bathtile | refused: stripe:body_like_surround | blue | 1 |
| lampmid6_bathtile | no seed candidate | blue | 1 |
| lampcool6_ottoman | no seed candidate | orange,blue | 1 |
| lampcool6_ottoman | refused: body:not_two_colors+stripe:stripe_not_painted | orange,blue | 1 |
| lampmid6_ottoman | refused: stripe:not_two_colors | orange | 1 |

### still not found, by cause (59)

| hidden | paint | seed | n |
|---|---|---|---|
| True | neither painted | no seed candidate | 9 |
| False | stripe painted, body not | no seed candidate | 7 |
| True | stripe painted, body not | no seed candidate | 6 |
| False | body painted, stripe not | refused: stripe:body_like_surround | 4 |
| False | body painted, stripe not | kept: body | 3 |
| True | body painted, stripe not | refused: stripe:not_two_colors | 3 |
| False | body painted, stripe not | refused: stripe:not_two_colors | 3 |
| True | neither painted | refused: stripe:not_two_colors | 2 |
| False | neither painted | refused: stripe:body_like_surround | 2 |
| False | neither painted | refused: stripe:stripe_not_painted | 2 |
| True | neither painted | kept: found | 1 |
| True | stripe painted, body not | kept: found | 1 |
| True | body painted, stripe not | refused: stripe:body_like_surround | 1 |
| False | stripe painted, body not | kept: stripe | 1 |
| True | body painted, stripe not | refused: body:not_two_colors | 1 |
| True | body painted, stripe not | no seed candidate | 1 |
| True | neither painted | refused: stripe:off_frame | 1 |
| False | stripe painted, body not | refused: stripe:stripe_not_painted | 1 |
| False | body painted, stripe not | refused: stripe:body_like_surround+stripe:stripe_not_painted | 1 |
| False | body painted, stripe not | no seed candidate | 1 |
| True | neither painted | refused: stripe:body_like_surround | 1 |
| False | body painted, stripe not | refused: stripe:body_like_surround+stripe:not_two_colors | 1 |
| True | neither painted | refused: stripe:stripe_not_painted | 1 |
| False | neither painted | no seed candidate | 1 |
| False | body painted, stripe not | refused: body:stripe_like_surround+stripe:body_like_surround+stripe:stripe_not_painted | 1 |
| True | stripe painted, body not | refused: stripe:body_like_surround+stripe:not_two_colors | 1 |
| True | body painted, stripe not | kept: found | 1 |
| True | both painted | refused: stripe:body_like_surround | 1 |

### still not found, by condition (59)

| condition | after | n |
|---|---|---|
| lampwarm6_ottoman | missed | 15 |
| lampwarm6_bathtile | missed | 9 |
| lampmid6_ottoman | missed | 8 |
| window_abpwhite | missed | 6 |
| lampmid3_bathtile | missed | 5 |
| lampmid6_bathtile | missed | 5 |
| lampcool6_ottoman | missed | 4 |
| overheaddim_palewood | missed | 2 |
| window_light | missed | 1 |
| both_abpgray | off | 1 |
| lampcool6_bathtile | missed | 1 |
| lampmid6_bathtile | off | 1 |
| window_glass | off | 1 |

### still not found and not hidden, in detail (28)

| condition | color | paint | seed | n |
|---|---|---|---|---|
| lampwarm6_bathtile | blue | stripe painted, body not | no seed candidate | 4 |
| lampwarm6_ottoman | orange | body painted, stripe not | refused: stripe:body_like_surround | 3 |
| lampmid3_bathtile | blue | stripe painted, body not | no seed candidate | 2 |
| lampwarm6_bathtile | orange | body painted, stripe not | refused: stripe:not_two_colors | 2 |
| lampwarm6_ottoman | blue | neither painted | refused: stripe:body_like_surround | 2 |
| lampwarm6_ottoman | blue | neither painted | refused: stripe:stripe_not_painted | 2 |
| lampmid3_bathtile | orange | body painted, stripe not | kept: body | 1 |
| lampmid6_bathtile | blue | stripe painted, body not | kept: stripe | 1 |
| lampmid6_bathtile | orange | body painted, stripe not | kept: body | 1 |
| lampmid6_bathtile | orange | body painted, stripe not | refused: stripe:body_like_surround | 1 |
| lampmid6_bathtile | blue | stripe painted, body not | no seed candidate | 1 |
| lampwarm6_bathtile | orange | body painted, stripe not | kept: body | 1 |
| lampcool6_ottoman | orange | stripe painted, body not | refused: stripe:stripe_not_painted | 1 |
| lampmid6_ottoman | blue | body painted, stripe not | refused: stripe:body_like_surround+stripe:stripe_not_painted | 1 |
| lampmid6_ottoman | blue | body painted, stripe not | refused: stripe:not_two_colors | 1 |
| lampmid6_ottoman | blue | body painted, stripe not | no seed candidate | 1 |
| lampwarm6_ottoman | orange | body painted, stripe not | refused: stripe:body_like_surround+stripe:not_two_colors | 1 |
| lampwarm6_ottoman | blue | neither painted | no seed candidate | 1 |
| lampwarm6_ottoman | orange | body painted, stripe not | refused: body:stripe_like_surround+stripe:body_like_surround+stripe:stripe_not_painted | 1 |

## extreme conditions: 167 barrels, 13 found by the fixed detector, 60 by AB

### gained, by what the fixed colors painted and by its seed (47)

| paint | seed | n |
|---|---|---|
| stripe painted, body not | kept: stripe | 27 |
| body painted, stripe not | kept: body | 18 |
| stripe painted, body not | refused: body:not_two_colors+stripe:body_like_surround | 1 |
| neither painted | refused: body:body_not_painted+stripe:stripe_not_painted | 1 |

### gained without a kept seed of its own (by the frame's ranges) (2)

| condition | seed | frame_moved | n |
|---|---|---|---|
| lampcool6_wood | refused: body:not_two_colors+stripe:body_like_surround | blue | 1 |
| lampmid3_wood | refused: body:body_not_painted+stripe:stripe_not_painted | orange | 1 |

### still not found, by cause (107)

| hidden | paint | seed | n |
|---|---|---|---|
| False | stripe painted, body not | no seed candidate | 12 |
| True | neither painted | no seed candidate | 11 |
| False | body painted, stripe not | no seed candidate | 10 |
| False | neither painted | refused: stripe:not_two_colors | 7 |
| True | neither painted | kept: stripe | 7 |
| False | stripe painted, body not | kept: stripe | 6 |
| True | stripe painted, body not | no seed candidate | 4 |
| True | body painted, stripe not | no seed candidate | 4 |
| False | neither painted | refused: stripe:stripe_not_painted | 4 |
| False | body painted, stripe not | refused: stripe:not_two_colors | 3 |
| True | body painted, stripe not | refused: stripe:not_two_colors | 3 |
| False | neither painted | refused: stripe:not_two_colors+stripe:stripe_not_painted | 3 |
| True | neither painted | refused: stripe:body_like_surround | 2 |
| False | stripe painted, body not | refused: stripe:stripe_not_painted | 2 |
| False | body painted, stripe not | refused: body:body_like_surround+stripe:not_two_colors | 2 |
| False | body painted, stripe not | kept: body | 2 |
| False | neither painted | no seed candidate | 2 |
| True | neither painted | refused: stripe:not_two_colors | 2 |
| False | body painted, stripe not | refused: stripe:body_like_surround | 1 |
| False | neither painted | refused: body:body_not_painted+stripe:not_two_colors | 1 |
| False | stripe painted, body not | refused: stripe:body_like_surround | 1 |
| True | body painted, stripe not | kept: stripe | 1 |
| True | neither painted | refused: body:off_frame | 1 |
| True | stripe painted, body not | refused: body:body_not_painted+stripe:body_like_surround+stripe:stripe_not_painted | 1 |
| False | stripe painted, body not | refused: stripe:not_two_colors | 1 |
| False | stripe painted, body not | refused: stripe:not_two_colors+stripe:stripe_not_painted | 1 |
| True | both painted | no seed candidate | 1 |
| True | stripe painted, body not | refused: stripe:body_like_surround | 1 |
| False | body painted, stripe not | refused: body:body_not_painted+stripe:not_two_colors | 1 |
| True | body painted, stripe not | kept: body | 1 |
| True | stripe painted, body not | refused: body:body_not_painted | 1 |
| True | neither painted | refused: body:body_not_painted+stripe:not_two_colors | 1 |
| True | neither painted | refused: body:not_two_colors | 1 |
| False | stripe painted, body not | refused: body:body_like_surround | 1 |
| True | body painted, stripe not | refused: body:not_two_colors | 1 |
| True | neither painted | refused: body:not_two_colors+stripe:not_two_colors+stripe:stripe_not_painted | 1 |
| False | stripe painted, body not | refused: body:body_not_painted+stripe:stripe_not_painted | 1 |
| False | body painted, stripe not | refused: body:not_two_colors | 1 |
| True | neither painted | refused: stripe:stripe_not_painted | 1 |

### still not found, by condition (107)

| condition | after | n |
|---|---|---|
| window_black | missed | 17 |
| lampwarm3_wood | missed | 15 |
| lampwarm6_wood | missed | 15 |
| lampmid3_ottoman | missed | 13 |
| lampcool6_wood | missed | 11 |
| lampmid6_wood | missed | 11 |
| lampcool3_wood | missed | 10 |
| lampmid3_wood | missed | 9 |
| lampcool6_wood | off | 2 |
| lampmid3_ottoman | off | 1 |
| lampmid3_wood | off | 1 |
| lampmid6_wood | off | 1 |
| window_black | off | 1 |

### still not found and not hidden, in detail (62)

| condition | color | paint | seed | n |
|---|---|---|---|---|
| lampcool6_wood | blue | stripe painted, body not | kept: stripe | 3 |
| lampmid6_wood | blue | stripe painted, body not | no seed candidate | 3 |
| lampwarm3_wood | blue | stripe painted, body not | no seed candidate | 3 |
| lampwarm3_wood | orange | body painted, stripe not | no seed candidate | 3 |
| lampmid3_ottoman | blue | stripe painted, body not | no seed candidate | 2 |
| lampmid3_ottoman | orange | neither painted | refused: stripe:not_two_colors | 2 |
| lampcool3_wood | orange | body painted, stripe not | refused: stripe:not_two_colors | 2 |
| lampcool6_wood | orange | body painted, stripe not | no seed candidate | 2 |
| lampmid3_wood | blue | stripe painted, body not | kept: stripe | 2 |
| lampmid3_wood | orange | body painted, stripe not | no seed candidate | 2 |
| lampmid6_wood | orange | body painted, stripe not | no seed candidate | 2 |
| lampwarm6_wood | blue | stripe painted, body not | no seed candidate | 2 |
| window_black | blue | neither painted | refused: stripe:stripe_not_painted | 2 |
| window_black | orange | neither painted | refused: stripe:not_two_colors | 2 |
| window_black | blue | neither painted | refused: stripe:not_two_colors | 2 |
| window_black | blue | neither painted | refused: stripe:not_two_colors+stripe:stripe_not_painted | 2 |
| lampmid3_ottoman | blue | neither painted | refused: stripe:not_two_colors | 1 |
| lampmid3_ottoman | orange | body painted, stripe not | refused: stripe:body_like_surround | 1 |
| lampmid3_ottoman | blue | stripe painted, body not | refused: stripe:stripe_not_painted | 1 |
| lampmid3_ottoman | orange | body painted, stripe not | refused: stripe:not_two_colors | 1 |
| lampmid3_ottoman | orange | neither painted | refused: body:body_not_painted+stripe:not_two_colors | 1 |
| lampmid3_ottoman | blue | stripe painted, body not | refused: stripe:body_like_surround | 1 |
| lampcool3_wood | blue | stripe painted, body not | no seed candidate | 1 |
| lampcool3_wood | blue | neither painted | refused: stripe:stripe_not_painted | 1 |
| lampcool3_wood | blue | stripe painted, body not | kept: stripe | 1 |
| lampcool6_wood | orange | body painted, stripe not | refused: body:body_like_surround+stripe:not_two_colors | 1 |
| lampcool6_wood | blue | stripe painted, body not | refused: stripe:not_two_colors | 1 |
| lampcool6_wood | blue | stripe painted, body not | refused: stripe:not_two_colors+stripe:stripe_not_painted | 1 |
| lampmid3_wood | orange | body painted, stripe not | refused: body:body_not_painted+stripe:not_two_colors | 1 |
| lampmid3_wood | blue | stripe painted, body not | no seed candidate | 1 |
| lampmid6_wood | orange | body painted, stripe not | kept: body | 1 |
| lampwarm3_wood | orange | body painted, stripe not | refused: body:body_like_surround+stripe:not_two_colors | 1 |
| lampwarm3_wood | blue | neither painted | refused: stripe:stripe_not_painted | 1 |
| lampwarm3_wood | blue | neither painted | no seed candidate | 1 |
| lampwarm6_wood | blue | stripe painted, body not | refused: body:body_like_surround | 1 |
| lampwarm6_wood | orange | body painted, stripe not | kept: body | 1 |
| lampwarm6_wood | blue | stripe painted, body not | refused: stripe:stripe_not_painted | 1 |
| lampwarm6_wood | blue | stripe painted, body not | refused: body:body_not_painted+stripe:stripe_not_painted | 1 |
| lampwarm6_wood | orange | body painted, stripe not | refused: body:not_two_colors | 1 |
| lampwarm6_wood | orange | body painted, stripe not | no seed candidate | 1 |
| window_black | orange | neither painted | no seed candidate | 1 |
| window_black | orange | neither painted | refused: stripe:not_two_colors+stripe:stripe_not_painted | 1 |

