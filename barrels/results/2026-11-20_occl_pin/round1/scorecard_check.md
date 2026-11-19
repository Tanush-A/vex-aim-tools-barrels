# The scorecard against the PREREG's scorecard clauses, per arm

`base`: found 2417, right place 2532, boxes where no barrel is 45, too big 104 of the right-place boxes (4.11 %), of 3888 scenes. Targeted cells together: 593 of 1300.

| arm | found | right place | boxes where no barrel is | too big (share) | cells with found lower | cells with right place lower | targeted cells together | committed cells not higher | scorecard clauses |
|---|---|---|---|---|---|---|---|---|---|
| pin | 2429 | 2554 | 45 | 104 (4.07 %) | 2 | 1 | 593 → 603 | 1 | **FAILS** |
| pin+thin | 2699 | 2824 | 48 (more) | 117 (4.14 %) (more) | 1 | 0 | 593 → 811 | 2 | **FAILS** |

- `pin`, found lower: slant at 50 %: 154 → 148 of 200
- `pin`, found lower: barrel_low/same at 75 %: 26 → 25 of 100
- `pin`, right place lower: barrel_low/same at 75 %: 32 → 31 of 100
- `pin`, committed cell not higher: slant at 50 %: 154 → 148
- `pin+thin`, found lower: slant at 50 %: 154 → 148 of 200
- `pin+thin`, committed cell not higher: slant at 50 %: 154 → 148
- `pin+thin`, committed cell not higher: slant at 75 %: 0 → 0

## The targeted cells, found of n

| cell | n | `base` | `pin` | `pin+thin` |
|---|---|---|---|---|
| edge at 50 % | 100 | 82 | 94 | 94 |
| edge at 75 % | 100 | 0 | 3 | 80 |
| slant at 50 % | 200 | 154 | 148 | 148 |
| slant at 75 % | 200 | 0 | 0 | 0 |
| both at 50 % | 50 | 49 | 49 | 49 |
| both at 75 % | 50 | 0 | 0 | 0 |
| frame at 50 % | 100 | 99 | 100 | 100 |
| frame at 75 % | 100 | 3 | 3 | 80 |
| block/same at 50 % | 100 | 99 | 99 | 99 |
| block/same at 75 % | 100 | 5 | 5 | 53 |
| block/other at 50 % | 100 | 99 | 99 | 99 |
| block/other at 75 % | 100 | 3 | 3 | 9 |

## Every other cell that changes (found; right place)

| cell | n | `base` | `pin` | `pin+thin` |
|---|---|---|---|---|
| post at 50 % | 50 | 9; 9 | 12; 12 | 47; 47 |
| post at 75 % | 50 | 0; 0 | 0; 0 | 6; 6 |
| barrel_side/other at 75 % | 100 | 49; 60 | 49; 60 | 55; 66 |
| barrel_low/other at 75 % | 100 | 77; 90 | 77; 90 | 79; 92 |
| barrel_side/same at 75 % | 100 | 16; 31 | 16; 31 | 17; 32 |
| barrel_low/same at 75 % | 100 | 26; 32 | 25; 31 | 37; 43 |
