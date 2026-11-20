# Two pieces of stripe color at the same rows: one stripe or not? (a census; no acceptance number)

A pair = a piece of sandwiched stripe color and the nearest such piece to its right that shares rows with it. `fits` = the two together span at most 1.2 barrel widths (the limit of `stripe_join`). `shaped` = both pieces have a stripe's shape (what `stripe_join` asks today). `body over the gap` = the share of the gap's columns with body color right above and right below.

## real masks (HOME hand, HOME leave one scene out, CAMPUS)

| the two pieces lie on | pairs | fits | fits and shaped (joined today) | fits, not shaped | fits, body over the whole gap (1.0) | fits, body over 0.8 of the gap | fits, gap at most one stripe height | fits, either (0.8 or one stripe height) |
|---|---|---|---|---|---|---|---|---|
| same barrel | 7 | 7 | 1 | 6 | 3 | 3 | 5 | 6 |
| two barrels | 7 | 2 | 0 | 2 | 0 | 0 | 1 | 1 |
| one on no barrel | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| both on no barrel | 7 | 6 | 0 | 6 | 0 | 0 | 2 | 2 |

- same barrel, pairs that fit: span / W median 0.54 (largest 0.95); gap / W median 0.05 (largest 0.77); body over the gap median 0.50 (lowest 0.00).
- two barrels, pairs that fit: span / W median 0.51 (largest 0.78); gap / W median 0.41 (largest 0.62); body over the gap median 0.00 (lowest 0.00).
- both on no barrel, pairs that fit: span / W median 0.73 (largest 1.04); gap / W median 0.28 (largest 0.68); body over the gap median 0.00 (lowest 0.00).

## black and wood tables (report only)

| the two pieces lie on | pairs | fits | fits and shaped (joined today) | fits, not shaped | fits, body over the whole gap (1.0) | fits, body over 0.8 of the gap | fits, gap at most one stripe height | fits, either (0.8 or one stripe height) |
|---|---|---|---|---|---|---|---|---|
| same barrel | 47 | 47 | 13 | 34 | 10 | 10 | 41 | 42 |
| two barrels | 5 | 4 | 3 | 1 | 1 | 1 | 4 | 4 |
| one on no barrel | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| both on no barrel | 31 | 31 | 2 | 29 | 2 | 2 | 28 | 28 |

- same barrel, pairs that fit: span / W median 0.26 (largest 1.14); gap / W median 0.04 (largest 0.77); body over the gap median 0.00 (lowest 0.00).
- two barrels, pairs that fit: span / W median 0.47 (largest 0.51); gap / W median 0.18 (largest 0.21); body over the gap median 0.23 (lowest 0.00).
- both on no barrel, pairs that fit: span / W median 0.16 (largest 0.65); gap / W median 0.01 (largest 0.64); body over the gap median 0.00 (lowest 0.00).

## HOME hand masks with a stripe patch

| the two pieces lie on | pairs | fits | fits and shaped (joined today) | fits, not shaped | fits, body over the whole gap (1.0) | fits, body over 0.8 of the gap | fits, gap at most one stripe height | fits, either (0.8 or one stripe height) |
|---|---|---|---|---|---|---|---|---|
| same barrel | 623 | 623 | 133 | 490 | 606 | 606 | 590 | 623 |
| two barrels | 138 | 59 | 11 | 48 | 0 | 11 | 49 | 52 |
| one on no barrel | 50 | 23 | 0 | 23 | 3 | 3 | 16 | 18 |
| both on no barrel | 3 | 3 | 0 | 3 | 0 | 0 | 1 | 1 |

- same barrel, pairs that fit: span / W median 0.90 (largest 1.01); gap / W median 0.10 (largest 0.77); body over the gap median 1.00 (lowest 0.00).
- two barrels, pairs that fit: span / W median 0.24 (largest 1.19); gap / W median 0.21 (largest 1.01); body over the gap median 0.00 (lowest 0.00).
- one on no barrel, pairs that fit: span / W median 0.78 (largest 1.18); gap / W median 0.14 (largest 1.08); body over the gap median 0.00 (lowest 0.00).
- both on no barrel, pairs that fit: span / W median 0.72 (largest 0.73); gap / W median 0.31 (largest 0.32); body over the gap median 0.00 (lowest 0.00).

## HOME hand masks with one stripe break

| the two pieces lie on | pairs | fits | fits and shaped (joined today) | fits, not shaped | fits, body over the whole gap (1.0) | fits, body over 0.8 of the gap | fits, gap at most one stripe height | fits, either (0.8 or one stripe height) |
|---|---|---|---|---|---|---|---|---|
| same barrel | 595 | 595 | 102 | 493 | 567 | 574 | 469 | 593 |
| two barrels | 126 | 55 | 4 | 51 | 0 | 12 | 47 | 47 |
| one on no barrel | 31 | 10 | 0 | 10 | 1 | 1 | 2 | 2 |
| both on no barrel | 8 | 8 | 0 | 8 | 0 | 0 | 6 | 6 |

- same barrel, pairs that fit: span / W median 0.91 (largest 1.01); gap / W median 0.15 (largest 0.77); body over the gap median 1.00 (lowest 0.00).
- two barrels, pairs that fit: span / W median 0.24 (largest 1.20); gap / W median 0.21 (largest 0.43); body over the gap median 0.00 (lowest 0.00).
- one on no barrel, pairs that fit: span / W median 1.18 (largest 1.20); gap / W median 1.04 (largest 1.08); body over the gap median 0.00 (lowest 0.00).
- both on no barrel, pairs that fit: span / W median 0.62 (largest 0.62); gap / W median 0.17 (largest 0.41); body over the gap median 0.00 (lowest 0.00).

## Every pair on the real masks that fits in one barrel's width and is NOT on one barrel

| frames | frame | body | left piece | right piece | span / W | gap / W | shaped | body over the gap | truth |
|---|---|---|---|---|---|---|---|---|---|
| HOME hand masks | window_light_cluster_01 | blue | [376, 158, 377, 161] (3 px) | [389, 159, 390, 162] (3 px) | 0.241 | 0.207 | no | 0.0 | two barrels |
| HOME, leave one scene out | window_light_cluster_01 | blue | [369, 118, 372, 120] (6 px) | [391, 118, 393, 123] (8 px) | 0.783 | 0.62 | no | 0.0 | two barrels |
| HOME, leave one scene out | window_light_cluster_02 | blue | [316, 120, 335, 139] (361 px) | [346, 121, 350, 139] (43 px) | 0.921 | 0.298 | no | 0.0 | both on no barrel |
| HOME, leave one scene out | window_light_core_03 | blue | [318, 114, 319, 116] (2 px) | [336, 107, 344, 118] (78 px) | 1.036 | 0.677 | no | 0.0 | both on no barrel |
| HOME, leave one scene out | window_light_far_02 | orange | [436, 108, 444, 119] (70 px) | [451, 107, 455, 120] (49 px) | 0.737 | 0.271 | no | 0.0 | both on no barrel |
| HOME, leave one scene out | window_light_far_02 | orange | [451, 107, 455, 120] (49 px) | [458, 107, 461, 120] (37 px) | 0.388 | 0.116 | no | 0.0 | both on no barrel |
| HOME, leave one scene out | window_light_far_02 | orange | [458, 107, 461, 120] (37 px) | [464, 109, 467, 120] (27 px) | 0.349 | 0.116 | no | 0.0 | both on no barrel |
| HOME, leave one scene out | window_light_far_02 | blue | [336, 107, 339, 117] (29 px) | [351, 107, 354, 118] (33 px) | 0.717 | 0.478 | no | 0.0 | both on no barrel |
