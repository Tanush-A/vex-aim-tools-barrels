# The scorecard against PREREG rule 3, per arm

`base`: found 2417, right place 2532, boxes where no barrel is 45, of 3888 scenes.

| arm | found | right place | boxes where no barrel is | cells where found is lower | cells where right place is lower | target cells not higher | rule 3 |
|---|---|---|---|---|---|---|---|
| half | 2457 | 2572 | 45 | 0 | 0 | 0 | pass |
| half+thin | 2500 | 2615 | 45 | 0 | 0 | 0 | pass |
| post | 2459 | 2576 | 46 (more) | 0 | 0 | 0 | **FAILS** |
| wide | 2487 | 2599 | 45 | 0 | 0 | 0 | pass |
| behind | 2538 | 2655 | 51 (more) | 0 | 0 | 0 | **FAILS** |
| caplow | 2429 | 2547 | 45 | 0 | 0 | 0 | pass |
| all | 2745 | 2864 | 51 (more) | 0 | 0 | 0 | **FAILS** |

- `post`, boxes where no barrel is: barrel_side/same at 75 %: 4 → 5
- `behind`, boxes where no barrel is: frame at 75 %: 0 → 1
- `behind`, boxes where no barrel is: barrel_side/other at 75 %: 1 → 2
- `behind`, boxes where no barrel is: barrel_low/other at 25 %: 1 → 2
- `behind`, boxes where no barrel is: barrel_low/other at 75 %: 2 → 3
- `behind`, boxes where no barrel is: barrel_side/same at 75 %: 4 → 5
- `behind`, boxes where no barrel is: barrel_low/same at 75 %: 0 → 1
- `all`, boxes where no barrel is: frame at 75 %: 0 → 1
- `all`, boxes where no barrel is: barrel_side/other at 75 %: 1 → 2
- `all`, boxes where no barrel is: barrel_low/other at 25 %: 1 → 2
- `all`, boxes where no barrel is: barrel_low/other at 75 %: 2 → 3
- `all`, boxes where no barrel is: barrel_side/same at 75 %: 4 → 5
- `all`, boxes where no barrel is: barrel_low/same at 75 %: 0 → 1

## The seven rows: found (v2) of n, at 25 / 50 / 75 % hidden

| what hides the barrel | `base` | `half` | `half+thin` | `post` | `wide` | `behind` | `caplow` | `all` |
|---|---|---|---|---|---|---|---|---|
| hidden from above (of 50 / 50 / 50) | 50 / 2 / 0 | 50 / 40 / 0 | 50 / 45 / 0 | 50 / 2 / 0 | 50 / 2 / 0 | 50 / 2 / 0 | 50 / 2 / 0 | 50 / 45 / 0 |
| hidden from below (of 50 / 50 / 50) | 49 / 1 / 1 | 49 / 2 / 1 | 49 / 40 / 1 | 49 / 1 / 1 | 49 / 1 / 1 | 49 / 1 / 1 | 49 / 1 / 1 | 49 / 40 / 1 |
| a post across the middle (of 50 / 50 / 50) | 49 / 9 / 0 | 49 / 9 / 0 | 49 / 9 / 0 | 49 / 42 / 9 | 49 / 9 / 0 | 49 / 9 / 0 | 49 / 9 / 0 | 49 / 42 / 9 |
| OTHER color straight in front (of 47 / 48 / 49) | 39 / 38 / 17 | 40 / 38 / 17 | 40 / 38 / 17 | 39 / 38 / 17 | 39 / 38 / 17 | 39 / 38 / 17 | 39 / 38 / 22 | 40 / 38 / 22 |
| SAME color straight in front (of 47 / 48 / 49) | 44 / 29 / 2 | 44 / 29 / 2 | 44 / 29 / 2 | 44 / 29 / 2 | 44 / 29 / 2 | 44 / 29 / 2 | 44 / 29 / 8 | 44 / 29 / 8 |
| SAME color beside (of 100 / 100 / 100) | 81 / 36 / 16 | 81 / 36 / 16 | 81 / 36 / 16 | 81 / 36 / 16 | 96 / 88 / 17 | 81 / 36 / 17 | 81 / 36 / 16 | 96 / 88 / 18 |
| SAME color beside and lower (of 100 / 100 / 100) | 91 / 85 / 26 | 91 / 85 / 26 | 91 / 85 / 26 | 91 / 85 / 26 | 91 / 87 / 26 | 91 / 85 / 42 | 91 / 85 / 27 | 91 / 87 / 43 |
