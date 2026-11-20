# The scorecard against the PREREG's scorecard clauses, per arm

`base`: found 2417, right place 2532, boxes where no barrel is 45, too big 104 of the right-place boxes (4.11 %), of 3888 scenes. Targeted cells together: 593 of 1300.

| arm | found | right place | boxes where no barrel is | too big (share) | cells with found lower | cells with right place lower | targeted cells together | committed cells not higher | scorecard clauses |
|---|---|---|---|---|---|---|---|---|---|
| pin | 2445 | 2560 | 45 | 102 (3.98 %) | 0 | 0 | 593 → 619 | 0 | pass |
| pin+thin | 2556 | 2671 | 45 | 104 (3.89 %) | 0 | 0 | 593 → 702 | 1 | **FAILS** |

- `pin+thin`, committed cell not higher: slant at 75 %: 0 → 0

## The targeted cells, found of n

| cell | n | `base` | `pin` | `pin+thin` |
|---|---|---|---|---|
| edge at 50 % | 100 | 82 | 90 | 90 |
| edge at 75 % | 100 | 0 | 2 | 28 |
| slant at 50 % | 200 | 154 | 170 | 170 |
| slant at 75 % | 200 | 0 | 0 | 0 |
| both at 50 % | 50 | 49 | 49 | 49 |
| both at 75 % | 50 | 0 | 0 | 0 |
| frame at 50 % | 100 | 99 | 99 | 99 |
| frame at 75 % | 100 | 3 | 3 | 29 |
| block/same at 50 % | 100 | 99 | 99 | 99 |
| block/same at 75 % | 100 | 5 | 5 | 36 |
| block/other at 50 % | 100 | 99 | 99 | 99 |
| block/other at 75 % | 100 | 3 | 3 | 3 |

## Every other cell that changes (found; right place)

| cell | n | `base` | `pin` | `pin+thin` |
|---|---|---|---|---|
| post at 50 % | 50 | 9; 9 | 11; 11 | 31; 31 |
| post at 75 % | 50 | 0; 0 | 0; 0 | 5; 5 |
| barrel_side/other at 75 % | 100 | 49; 60 | 49; 60 | 50; 61 |
| barrel_low/same at 75 % | 100 | 26; 32 | 26; 32 | 28; 34 |
