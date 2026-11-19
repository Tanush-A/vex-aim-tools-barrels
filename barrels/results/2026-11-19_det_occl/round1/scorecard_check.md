# The scorecard against PREREG rule 4, per arm

`base`: found 2401, right place 2521, false boxes 63, of 3888 scenes.

| arm | found | right place | false boxes | cells where found is lower | cells where right place is lower | target cells not higher | rule 4 |
|---|---|---|---|---|---|---|---|
| slice | 3086 | 3251 | 315 (more) | 1 | 2 | 0 | **FAILS** |
| slice+cover | 3087 | 3253 | 315 (more) | 1 | 2 | 0 | **FAILS** |
| two | 2485 | 2615 | 70 (more) | 0 | 0 | 0 | **FAILS** |
| edge | 2412 | 2521 | 45 | 0 | 0 | 0 | pass |
| cap | 2404 | 2528 | 61 | 1 | 1 | 0 | **FAILS** |
| all | 3186 | 3356 | 300 (more) | 1 | 1 | 0 | **FAILS** |
| all-cover | 3185 | 3354 | 300 (more) | 1 | 1 | 0 | **FAILS** |

- `slice`, found lower: barrel_low/other at 50 %: 92 → 91 of 100
- `slice`, right place lower: barrel_side/other at 50 %: 96 → 95 of 100
- `slice`, right place lower: barrel_front/same at 50 %: 30 → 29 of 48
- `slice+cover`, found lower: barrel_low/other at 50 %: 92 → 91 of 100
- `slice+cover`, right place lower: barrel_side/other at 50 %: 96 → 95 of 100
- `slice+cover`, right place lower: barrel_front/same at 50 %: 30 → 29 of 48
- `cap`, found lower: barrel_low/same at 75 %: 26 → 25 of 100
- `cap`, right place lower: barrel_low/same at 75 %: 32 → 30 of 100
- `all`, found lower: barrel_low/other at 50 %: 92 → 91 of 100
- `all`, right place lower: barrel_side/other at 50 %: 96 → 95 of 100
- `all-cover`, found lower: barrel_low/other at 50 %: 92 → 91 of 100
- `all-cover`, right place lower: barrel_side/other at 50 %: 96 → 95 of 100
