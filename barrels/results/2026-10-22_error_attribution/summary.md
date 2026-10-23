# Error attribution, final config `afd85483`, LOSO-CV predictions on the 16 pool frames

## orange: 134111 labeled pixels

| missed because | pixels | % of labeled |
|---|---|---|
| above horizon | 0 | 0.0 % |
| brightness gate | 216 | 0.2 % |
| saturation floor | 3045 | 2.3 % |
| wall prior | 17 | 0.0 % |
| outside class box | 3319 | 2.5 % |
| lost tie to other class | 1 | 0.0 % |

| false pixels | pixels | % of labeled |
|---|---|---|
| boundary halo (≤4 px from a barrel) | 1466 | 1.1 % |
| elsewhere (shadow / reflection / clutter) | 5229 | 3.9 % |
| hand frame, elsewhere | 841 | 0.6 % |

## blue: 40987 labeled pixels

| missed because | pixels | % of labeled |
|---|---|---|
| above horizon | 0 | 0.0 % |
| brightness gate | 408 | 1.0 % |
| saturation floor | 8605 | 21.0 % |
| wall prior | 838 | 2.0 % |
| outside class box | 1506 | 3.7 % |
| lost tie to other class | 196 | 0.5 % |

| false pixels | pixels | % of labeled |
|---|---|---|
| boundary halo (≤4 px from a barrel) | 207 | 0.5 % |
| elsewhere (shadow / reflection / clutter) | 0 | 0.0 % |
| hand frame, elsewhere | 1 | 0.0 % |

## Per frame

| frame | floor | orange: missed (floor / wall / box) · false (halo / elsewhere) | blue: missed (floor / wall / box) · false (halo / elsewhere) | 'elsewhere' false pixels look like |
|---|---|---|---|---|
| _close_01 | 47 | 181 / 0 / 38 · 234 / 1 | 227 / 39 / 49 · 0 / 0 |  |
| _close_02 | 51 | 170 / 1 / 48 · 0 / 0 | 455 / 153 / 261 · 21 / 0 |  |
| _cluster_01 | 51 | 281 / 8 / 190 · 3 / 0 | 421 / 105 / 69 · 10 / 0 |  |
| _cluster_02 | 51 | 318 / 3 / 309 · 56 / 0 | 633 / 92 / 166 · 39 / 0 |  |
| _core_01 | 55 | 170 / 0 / 87 · 25 / 0 | 188 / 49 / 287 · 22 / 0 |  |
| _core_02 | 55 | 189 / 0 / 43 · 12 / 0 | 146 / 73 / 93 · 7 / 0 |  |
| _core_03 | 51 | 25 / 2 / 29 · 41 / 321 | 33 / 32 / 0 · 1 / 0 | o [107, 70, 51] sat 55 (n=321) |
| _edge_01 | 47 | 207 / 0 / 13 · 0 / 0 | 396 / 1 / 3 · 15 / 0 |  |
| _far_02 | 48 | 154 / 3 / 83 · 75 / 520 | 157 / 35 / 130 · 73 / 1 | o [94, 57, 44] sat 50 (n=520) |
| _neg_01 | 47 | 0 / 0 / 0 · 0 / 0 | 0 / 0 / 0 · 0 / 0 |  |
| _neg_02 | 48 | 0 / 0 / 0 · 0 / 0 | 0 / 0 / 0 · 0 / 0 |  |
| _occl_01 | 51 | 139 / 0 / 60 · 35 / 0 | 471 / 68 / 31 · 5 / 0 |  |
| _occl_02 | 51 | 198 / 0 / 48 · 22 / 0 | 443 / 124 / 178 · 1 / 0 |  |
| _top_01 | 44 | 260 / 0 / 795 · 424 / 681 | 121 / 0 / 2 · 0 / 0 | o [118, 102, 74] sat 45 (n=681) |
| _topstripe_01 | 44 | 490 / 0 / 1170 · 487 / 4547 | 4548 / 0 / 72 · 0 / 0 | o [120, 102, 70] sat 47 (n=4547) |
| _touch_02 | 48 | 263 / 0 / 406 · 52 / 0 | 366 / 67 / 165 · 13 / 0 |  |

## Table prior back on (band floor config), LOSO CV — primary excludes the two close/top-only frames

| k_table | primary | orange IoU | blue IoU | top/topstripe orange IoU |
|---|---|---|---|---|
| off | 0.809 | 0.825 | 0.793 | 0.918 |
| 1.5 | 0.809 | 0.825 | 0.793 | 0.762 |
| 2.0 | 0.808 | 0.824 | 0.793 | 0.297 |
| 2.5 | 0.806 | 0.819 | 0.793 | 0.076 |
| 3.0 | 0.800 | 0.810 | 0.791 | 0.009 |
