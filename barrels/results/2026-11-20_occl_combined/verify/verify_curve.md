# The stencil as a checker of the `combined` detector's boxes: every limit (REPORT ONLY)

Every box `combined` draws gets the stencil's score at its place. A verifier at limit t drops the boxes scoring under t. Each cell: boxes dropped of boxes drawn. The registered limit is 0.16 (`verify_calibration.md`); the other columns were not used to choose anything and may not be: they show what a different limit would have cost and bought.

| boxes of `combined` | limit 0.0 | limit 0.02 | limit 0.05 | limit 0.08 | limit 0.1 | limit 0.13 | limit 0.16 | limit 0.2 |
|---|---|---|---|---|---|---|---|---|
| scorecard: right | 93 of 4072 | 108 of 4072 | 133 of 4072 | 166 of 4072 | 185 of 4072 | 258 of 4072 | 345 of 4072 | 506 of 4072 |
| scorecard: on a barrel, box not right | 6 of 248 | 16 of 248 | 21 of 248 | 26 of 248 | 29 of 248 | 35 of 248 | 45 of 248 | 51 of 248 |
| scorecard: no barrel there | 3 of 45 | 18 of 45 | 27 of 45 | 29 of 45 | 32 of 45 | 35 of 45 | 37 of 45 | 39 of 45 |
| HOME: right | 0 of 28 | 0 of 28 | 0 of 28 | 0 of 28 | 0 of 28 | 0 of 28 | 0 of 28 | 1 of 28 |
| CAMPUS: right | 0 of 35 | 0 of 35 | 0 of 35 | 1 of 35 | 1 of 35 | 2 of 35 | 2 of 35 | 3 of 35 |
| BLACK (report only): right | 3 of 5 | 3 of 5 | 3 of 5 | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 |
| BLACK (report only): on a barrel, box not right | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| WOOD (report only): right | 1 of 7 | 2 of 7 | 2 of 7 | 3 of 7 | 4 of 7 | 5 of 7 | 5 of 7 | 5 of 7 |
| WOOD (report only): no barrel there | 4 of 4 | 4 of 4 | 4 of 4 | 4 of 4 | 4 of 4 | 4 of 4 | 4 of 4 | 4 of 4 |
| WOOD (report only): on a barrel, box not right | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |

## The scorecard's right boxes a verifier would drop, by the rule that drew them

| drawn by | boxes | limit 0.0 | limit 0.02 | limit 0.05 | limit 0.08 | limit 0.1 | limit 0.13 | limit 0.16 | limit 0.2 |
|---|---|---|---|---|---|---|---|---|---|
| stripe step | 3605 | 9 | 17 | 23 | 32 | 40 | 74 | 109 | 209 |
| slices_behind | 115 | 0 | 2 | 12 | 24 | 27 | 52 | 82 | 111 |
| half_stripes | 83 | 82 | 82 | 82 | 82 | 82 | 82 | 82 | 82 |
| post_pairs | 39 | 0 | 0 | 4 | 8 | 9 | 9 | 12 | 17 |
| caps_behind | 191 | 1 | 6 | 10 | 16 | 22 | 35 | 50 | 73 |
| stripeless piece | 39 | 1 | 1 | 2 | 4 | 5 | 6 | 10 | 14 |

## The scorecard's boxes where no barrel is, by the rule that drew them

| drawn by | boxes | limit 0.0 | limit 0.02 | limit 0.05 | limit 0.08 | limit 0.1 | limit 0.13 | limit 0.16 | limit 0.2 |
|---|---|---|---|---|---|---|---|---|---|
| stripe step | 32 | 2 | 17 | 24 | 26 | 28 | 30 | 31 | 32 |
| caps_behind | 4 | 0 | 0 | 2 | 2 | 3 | 4 | 4 | 4 |
| stripeless piece | 9 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 3 |

The eight lowest right boxes on HOME (leave one scene out) and CAMPUS:

- 0.065  CAMPUS campus_light_occl_02 blue [277, 127, 331, 178] (stripe step)
- 0.111  CAMPUS campus_light_clutter_02 blue [470, 122, 521, 171] (stripe step)
- 0.162  CAMPUS campus_light_held_01 blue [98, 334, 505, 480] (stripeless piece)
- 0.182  HOME window_light_topstripe_01 orange [176, 242, 423, 480] (stripeless piece)
- 0.212  HOME window_light_edge_01 blue [0, 132, 32, 197] (stripe step)
- 0.224  HOME window_light_occl_02 orange [399, 117, 439, 161] (caps_behind)
- 0.226  HOME window_light_cluster_01 orange [315, 118, 366, 162] (caps_behind)
- 0.231  HOME window_light_occl_01 blue [387, 112, 432, 158] (caps_behind)
