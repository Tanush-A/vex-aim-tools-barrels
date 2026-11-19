# The scorecard against PREREG rule 4, per arm

`base`: found 2401, right place 2521, false boxes 63, of 3888 scenes.

| arm | found | right place | false boxes | cells where found is lower | cells where right place is lower | target cells not higher | rule 4 |
|---|---|---|---|---|---|---|---|
| slice | 3068 | 3231 | 82 (more) | 0 | 1 | 0 | **FAILS** |
| slice+cover | 3068 | 3232 | 82 (more) | 0 | 1 | 0 | **FAILS** |
| two | 2471 | 2588 | 66 (more) | 0 | 0 | 0 | **FAILS** |
| edge | 2412 | 2521 | 45 | 0 | 0 | 0 | pass |
| cap | 2406 | 2532 | 63 | 0 | 0 | 0 | pass |
| edge+cap | 2417 | 2532 | 45 | 0 | 0 | 0 | pass |
| all | 3155 | 3312 | 58 | 0 | 0 | 0 | pass |
| all-cover | 3155 | 3311 | 58 | 0 | 0 | 0 | pass |

- `slice`, right place lower: barrel_front/same at 50 %: 30 → 29 of 48
- `slice+cover`, right place lower: barrel_front/same at 50 %: 30 → 29 of 48
