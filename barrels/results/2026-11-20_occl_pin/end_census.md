# Can one end of the seen part be recognised as the barrel's own side? (a census after round 1; no acceptance number)

The scorecard's own scenes (50 source barrels). An end's cost = the largest of the three lines' mean distances in rows between seen and predicted, with the outline's side put on that end, over the columns within `window` x W of the end; in barrel heights H.

## The cost, per kind of end

Median (10th to 90th percentile; n), and how many ends cost at most each limit.

| window | group | end | cost | at most 0.02 H | at most 0.03 H | at most 0.04 H | at most 0.05 H |
|---|---|---|---|---|---|---|---|
| 0.25 W | hand masks | own | 0.057 (0.030 to 0.144; n 238) | 16 | 18 | 71 | 105 |
| 0.25 W | hand masks | cut straight | 0.096 (0.087 to 0.166; n 144) | 0 | 0 | 0 | 0 |
| 0.25 W | hand masks | cut slanted | 0.086 (0.079 to 0.097; n 142) | 0 | 0 | 0 | 0 |
| 0.25 W | color model | own | 0.061 (0.045 to 0.136; n 695) | 8 | 16 | 33 | 117 |
| 0.25 W | color model | cut straight | 0.097 (0.088 to 0.180; n 439) | 0 | 0 | 0 | 1 |
| 0.25 W | color model | cut slanted | 0.090 (0.080 to 0.107; n 404) | 0 | 0 | 0 | 0 |
| 0.35 W | hand masks | own | 0.049 (0.029 to 0.181; n 238) | 16 | 44 | 101 | 125 |
| 0.35 W | hand masks | cut straight | 0.088 (0.073 to 0.166; n 144) | 0 | 0 | 0 | 0 |
| 0.35 W | hand masks | cut slanted | 0.091 (0.073 to 0.116; n 142) | 0 | 0 | 0 | 0 |
| 0.35 W | color model | own | 0.054 (0.040 to 0.167; n 695) | 8 | 21 | 69 | 297 |
| 0.35 W | color model | cut straight | 0.094 (0.073 to 0.191; n 439) | 0 | 0 | 1 | 1 |
| 0.35 W | color model | cut slanted | 0.096 (0.074 to 0.128; n 404) | 0 | 0 | 0 | 0 |
| 0.5 W | hand masks | own | 0.046 (0.023 to 0.184; n 238) | 16 | 65 | 99 | 131 |
| 0.5 W | hand masks | cut straight | 0.086 (0.058 to 0.166; n 144) | 0 | 0 | 0 | 3 |
| 0.5 W | hand masks | cut slanted | 0.081 (0.055 to 0.110; n 142) | 0 | 0 | 0 | 3 |
| 0.5 W | color model | own | 0.060 (0.033 to 0.170; n 695) | 6 | 40 | 209 | 287 |
| 0.5 W | color model | cut straight | 0.096 (0.059 to 0.191; n 439) | 0 | 0 | 0 | 7 |
| 0.5 W | color model | cut slanted | 0.087 (0.058 to 0.132; n 404) | 0 | 0 | 2 | 10 |

## The rule: exactly one end costs at most the limit

Then that end is the barrel's own side and the centre is W / 2 in from it. Each cell: **scenes where the rule speaks / of those, the centre wrong by more than 0.15 W / the largest error**. Seen parts 0.8 W wide or wider are left out (the detector takes the seen width as the box there), so `n` is the number of scenes with less than 0.8 W seen.

### window 0.25 W

| what hides the barrel | hidden | n | limit 0.02 H | limit 0.03 H | limit 0.04 H | limit 0.05 H |
|---|---|---|---|---|---|---|
| a straight edge | 25 % | 88 | 3 / 0 / 0.03 | 4 / 0 / 0.03 | 12 / 0 / 0.08 | 26 / 0 / 0.09 |
| a straight edge | 50 % | 98 | 3 / 0 / 0.03 | 4 / 0 / 0.03 | 13 / 0 / 0.08 | 27 / 0 / 0.09 |
| a straight edge | 75 % | 93 | 3 / 0 / 0.02 | 6 / 0 / 0.02 | 15 / 0 / 0.07 | 30 / 0 / 0.09 |
| a slanted edge | 25 % | 76 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 2 / 0 / 0.08 | 11 / 0 / 0.09 |
| a slanted edge | 50 % | 196 | 6 / 0 / 0.03 | 8 / 0 / 0.03 | 27 / 0 / 0.08 | 55 / 0 / 0.09 |
| a slanted edge | 75 % | 154 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 1 / 0 / 0.08 |
| both sides (equal) | 25 % | 40 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 |
| both sides (equal) | 50 % | 49 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 |
| both sides (equal) | 75 % | 49 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 |

### window 0.35 W

| what hides the barrel | hidden | n | limit 0.02 H | limit 0.03 H | limit 0.04 H | limit 0.05 H |
|---|---|---|---|---|---|---|
| a straight edge | 25 % | 88 | 3 / 0 / 0.03 | 8 / 0 / 0.08 | 22 / 0 / 0.08 | 57 / 0 / 0.12 |
| a straight edge | 50 % | 98 | 3 / 0 / 0.03 | 9 / 0 / 0.08 | 22 / 0 / 0.08 | 58 / 0 / 0.12 |
| a straight edge | 75 % | 93 | 3 / 0 / 0.02 | 7 / 0 / 0.02 | 15 / 0 / 0.07 | 30 / 0 / 0.09 |
| a slanted edge | 25 % | 76 | 0 / 0 / 0.00 | 2 / 0 / 0.08 | 9 / 0 / 0.08 | 42 / 0 / 0.12 |
| a slanted edge | 50 % | 196 | 6 / 0 / 0.03 | 16 / 0 / 0.03 | 42 / 0 / 0.07 | 104 / 0 / 0.09 |
| a slanted edge | 75 % | 154 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 |
| both sides (equal) | 25 % | 40 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 |
| both sides (equal) | 50 % | 49 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 |
| both sides (equal) | 75 % | 49 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 |

### window 0.5 W

| what hides the barrel | hidden | n | limit 0.02 H | limit 0.03 H | limit 0.04 H | limit 0.05 H |
|---|---|---|---|---|---|---|
| a straight edge | 25 % | 88 | 4 / 0 / 0.03 | 20 / 0 / 0.08 | 57 / 0 / 0.12 | 73 / 0 / 0.12 |
| a straight edge | 50 % | 98 | 4 / 0 / 0.03 | 18 / 0 / 0.08 | 53 / 0 / 0.09 | 72 / 0 / 0.12 |
| a straight edge | 75 % | 93 | 3 / 0 / 0.02 | 7 / 0 / 0.02 | 15 / 0 / 0.07 | 30 / 0 / 0.09 |
| a slanted edge | 25 % | 76 | 0 / 0 / 0.00 | 8 / 0 / 0.08 | 42 / 2 / 0.21 | 58 / 5 / 0.21 |
| a slanted edge | 50 % | 196 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 4 / 0 / 0.07 | 8 / 0 / 0.07 |
| a slanted edge | 75 % | 154 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 |
| both sides (equal) | 25 % | 40 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 3 / 1 / 0.18 |
| both sides (equal) | 50 % | 49 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 |
| both sides (equal) | 75 % | 49 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 | 0 / 0 / 0.00 |

