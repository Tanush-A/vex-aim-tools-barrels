# The occlusion scorecard, in full

git 9e7d088; camera AIM_4A8B6118_BOXFIT; train frames only. Source barrels: HOME hand masks 12, HOME color model 12, CAMPUS color model 26 (left out because `base` does not find them alone and unhidden: 0).

Each cell: found under the v2 rule / box in the right place / scenes; (mean overlap of the right-place boxes with the FULL box; too small · about right · too big; false boxes). `front` = the barrel pasted in front, found / pasted.

## `rules`, all three pools

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 / 100 / 100 (0.92; 1 · 99 · 0; 0) | 99 / 99 / 100 (0.90; 3 · 94 · 2; 0) | 3 / 3 / 100 (0.84; 0 · 2 · 1; 0) |
| a straight upright edge, one side | 100 / 100 / 100 (0.76; 12 · 88 · 0; 0) | 82 / 86 / 100 (0.59; 4 · 82 · 0; 0) | 0 / 0 / 100 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 200 / 200 / 200 (0.82; 83 · 114 · 3; 0) | 154 / 156 / 200 (0.77; 9 · 147 · 0; 0) | 0 / 0 / 200 (-; 0 · 0 · 0; 0) |
| both sides cut | 50 / 50 / 50 (0.88; 10 · 40 · 0; 0) | 49 / 50 / 50 (0.90; 2 · 48 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| hidden from above | 50 / 50 / 50 (0.87; 2 · 47 · 1; 0) | 2 / 2 / 50 (0.83; 2 · 0 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 49 / 50 / 50 (0.89; 1 · 49 · 0; 0) | 1 / 1 / 50 (0.91; 0 · 1 · 0; 0) | 1 / 1 / 50 (0.53; 1 · 0 · 0; 0) |
| a post across the middle | 49 / 49 / 50 (0.90; 1 · 48 · 0; 0) | 9 / 9 / 50 (0.87; 0 · 9 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 99 / 99 / 100 (0.83; 26 · 73 · 0; 0); front 94 / 100 | 94 / 96 / 100 (0.83; 6 · 87 · 3; 4); front 95 / 100 | 49 / 60 / 100 (0.81; 10 · 47 · 3; 1); front 94 / 100 |
| a barrel of the OTHER color, beside it and lower | 98 / 98 / 100 (0.85; 17 · 81 · 0; 1); front 90 / 100 | 92 / 92 / 100 (0.86; 4 · 87 · 1; 1); front 90 / 100 | 77 / 90 / 100 (0.83; 15 · 67 · 8; 2); front 90 / 100 |
| a barrel of the OTHER color, straight in front | 39 / 41 / 47 (0.87; 2 · 38 · 1; 3); front 32 / 47 | 38 / 39 / 48 (0.87; 0 · 39 · 0; 3); front 39 / 48 | 17 / 28 / 49 (0.83; 1 · 22 · 5; 1); front 42 / 49 |
| a barrel of the SAME color, beside it | 81 / 88 / 100 (0.81; 18 · 65 · 5; 2); front 81 / 100 | 36 / 49 / 100 (0.66; 7 · 14 · 28; 2); front 77 / 100 | 16 / 31 / 100 (0.70; 1 · 3 · 27; 4); front 79 / 100 |
| a barrel of the SAME color, beside it and lower | 91 / 98 / 100 (0.83; 25 · 70 · 3; 0); front 91 / 100 | 85 / 89 / 100 (0.84; 4 · 82 · 3; 0); front 87 / 100 | 26 / 32 / 100 (0.83; 2 · 28 · 2; 0); front 89 / 100 |
| a barrel of the SAME color, straight in front | 44 / 45 / 47 (0.87; 2 · 43 · 0; 4); front 34 / 47 | 29 / 37 / 48 (0.85; 3 · 30 · 4; 6); front 38 / 48 | 2 / 7 / 49 (0.70; 3 · 4 · 0; 2); front 42 / 49 |
| a plain block of the barrel's body color | 100 / 100 / 100 (0.87; 1 · 99 · 0; 2) | 99 / 99 / 100 (0.87; 2 · 95 · 2; 0) | 5 / 5 / 100 (0.78; 1 · 2 · 2; 0) |
| a plain block of the barrel's stripe color | 100 / 100 / 100 (0.86; 9 · 91 · 0; 2) | 99 / 99 / 100 (0.86; 8 · 91 · 0; 2) | 3 / 4 / 100 (0.78; 1 · 3 · 0; 3) |

## `rules`, HOME hand masks

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 24 / 24 / 24 (0.97; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.96; 1 · 23 · 0; 0) | 1 / 1 / 24 (0.91; 0 · 1 · 0; 0) |
| a straight upright edge, one side | 24 / 24 / 24 (0.79; 0 · 24 · 0; 0) | 23 / 23 / 24 (0.61; 0 · 23 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 48 / 48 / 48 (0.86; 16 · 32 · 0; 0) | 44 / 44 / 48 (0.79; 0 · 44 · 0; 0) | 0 / 0 / 48 (-; 0 · 0 · 0; 0) |
| both sides cut | 12 / 12 / 12 (0.91; 2 · 10 · 0; 0) | 12 / 12 / 12 (0.94; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from above | 12 / 12 / 12 (0.91; 1 · 10 · 1; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 12 / 12 / 12 (0.93; 1 · 11 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a post across the middle | 12 / 12 / 12 (0.95; 1 · 11 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 23 / 23 / 24 (0.90; 2 · 21 · 0; 0); front 24 / 24 | 24 / 24 / 24 (0.90; 0 · 24 · 0; 1); front 24 / 24 | 18 / 18 / 24 (0.89; 1 · 14 · 3; 0); front 24 / 24 |
| a barrel of the OTHER color, beside it and lower | 24 / 24 / 24 (0.91; 1 · 23 · 0; 0); front 20 / 24 | 23 / 23 / 24 (0.91; 0 · 23 · 0; 0); front 20 / 24 | 21 / 22 / 24 (0.91; 0 · 21 · 1; 0); front 20 / 24 |
| a barrel of the OTHER color, straight in front | 11 / 11 / 12 (0.93; 0 · 11 · 0; 0); front 8 / 12 | 10 / 10 / 12 (0.95; 0 · 10 · 0; 0); front 9 / 12 | 6 / 6 / 12 (0.88; 0 · 6 · 0; 0); front 11 / 12 |
| a barrel of the SAME color, beside it | 16 / 21 / 24 (0.82; 2 · 17 · 2; 0); front 21 / 24 | 1 / 9 / 24 (0.60; 0 · 0 · 9; 0); front 23 / 24 | 1 / 9 / 24 (0.72; 0 · 0 · 9; 0); front 23 / 24 |
| a barrel of the SAME color, beside it and lower | 20 / 23 / 24 (0.87; 6 · 17 · 0; 0); front 23 / 24 | 18 / 19 / 24 (0.88; 1 · 17 · 1; 0); front 22 / 24 | 8 / 8 / 24 (0.88; 0 · 8 · 0; 0); front 21 / 24 |
| a barrel of the SAME color, straight in front | 12 / 12 / 12 (0.92; 1 · 11 · 0; 0); front 9 / 12 | 11 / 12 / 12 (0.92; 1 · 11 · 0; 2); front 10 / 12 | 0 / 0 / 12 (-; 0 · 0 · 0; 0); front 11 / 12 |
| a plain block of the barrel's body color | 24 / 24 / 24 (0.92; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.92; 0 · 24 · 0; 0) | 1 / 1 / 24 (0.90; 0 · 1 · 0; 0) |
| a plain block of the barrel's stripe color | 24 / 24 / 24 (0.91; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.90; 1 · 23 · 0; 0) | 1 / 1 / 24 (0.89; 0 · 1 · 0; 0) |

## `rules`, HOME color model

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 24 / 24 / 24 (0.90; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.87; 1 · 22 · 1; 0) | 1 / 1 / 24 (0.78; 0 · 0 · 1; 0) |
| a straight upright edge, one side | 24 / 24 / 24 (0.76; 3 · 21 · 0; 0) | 21 / 22 / 24 (0.59; 0 · 22 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 48 / 48 / 48 (0.81; 20 · 28 · 0; 0) | 39 / 39 / 48 (0.77; 0 · 39 · 0; 0) | 0 / 0 / 48 (-; 0 · 0 · 0; 0) |
| both sides cut | 12 / 12 / 12 (0.88; 2 · 10 · 0; 0) | 12 / 12 / 12 (0.90; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from above | 12 / 12 / 12 (0.87; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 12 / 12 / 12 (0.89; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a post across the middle | 12 / 12 / 12 (0.89; 0 · 12 · 0; 0) | 4 / 4 / 12 (0.87; 0 · 4 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 24 / 24 / 24 (0.81; 7 · 17 · 0; 0); front 24 / 24 | 22 / 24 / 24 (0.79; 1 · 21 · 2; 2); front 24 / 24 | 8 / 13 / 24 (0.74; 4 · 9 · 0; 0); front 24 / 24 |
| a barrel of the OTHER color, beside it and lower | 23 / 23 / 24 (0.82; 6 · 17 · 0; 0); front 24 / 24 | 21 / 21 / 24 (0.85; 1 · 20 · 0; 0); front 24 / 24 | 17 / 21 / 24 (0.81; 5 · 14 · 2; 0); front 24 / 24 |
| a barrel of the OTHER color, straight in front | 9 / 10 / 12 (0.85; 0 · 10 · 0; 1); front 9 / 12 | 9 / 9 / 12 (0.86; 0 · 9 · 0; 1); front 10 / 12 | 4 / 6 / 12 (0.83; 0 · 6 · 0; 0); front 11 / 12 |
| a barrel of the SAME color, beside it | 21 / 21 / 24 (0.82; 5 · 16 · 0; 1); front 21 / 24 | 9 / 11 / 24 (0.64; 1 · 4 · 6; 2); front 19 / 24 | 4 / 9 / 24 (0.67; 1 · 1 · 7; 4); front 20 / 24 |
| a barrel of the SAME color, beside it and lower | 22 / 24 / 24 (0.84; 3 · 20 · 1; 0); front 22 / 24 | 22 / 23 / 24 (0.83; 1 · 21 · 1; 0); front 22 / 24 | 4 / 6 / 24 (0.83; 1 · 4 · 1; 0); front 22 / 24 |
| a barrel of the SAME color, straight in front | 10 / 11 / 12 (0.88; 0 · 11 · 0; 3); front 8 / 12 | 4 / 7 / 12 (0.79; 1 · 5 · 1; 3); front 9 / 12 | 0 / 1 / 12 (0.74; 1 · 0 · 0; 2); front 10 / 12 |
| a plain block of the barrel's body color | 24 / 24 / 24 (0.86; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.86; 0 · 24 · 0; 0) | 1 / 1 / 24 (0.76; 0 · 1 · 0; 0) |
| a plain block of the barrel's stripe color | 24 / 24 / 24 (0.85; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.84; 1 · 23 · 0; 0) | 1 / 1 / 24 (0.76; 0 · 1 · 0; 0) |

## `rules`, CAMPUS color model

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 52 / 52 / 52 (0.91; 0 · 52 · 0; 0) | 51 / 51 / 52 (0.88; 1 · 49 · 1; 0) | 1 / 1 / 52 (0.83; 0 · 1 · 0; 0) |
| a straight upright edge, one side | 52 / 52 / 52 (0.75; 9 · 43 · 0; 0) | 38 / 41 / 52 (0.58; 4 · 37 · 0; 0) | 0 / 0 / 52 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 104 / 104 / 104 (0.81; 47 · 54 · 3; 0) | 71 / 73 / 104 (0.75; 9 · 64 · 0; 0) | 0 / 0 / 104 (-; 0 · 0 · 0; 0) |
| both sides cut | 26 / 26 / 26 (0.86; 6 · 20 · 0; 0) | 25 / 26 / 26 (0.88; 2 · 24 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| hidden from above | 26 / 26 / 26 (0.86; 1 · 25 · 0; 0) | 2 / 2 / 26 (0.83; 2 · 0 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 25 / 26 / 26 (0.87; 0 · 26 · 0; 0) | 1 / 1 / 26 (0.91; 0 · 1 · 0; 0) | 1 / 1 / 26 (0.53; 1 · 0 · 0; 0) |
| a post across the middle | 25 / 25 / 26 (0.88; 0 · 25 · 0; 0) | 5 / 5 / 26 (0.87; 0 · 5 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 52 / 52 / 52 (0.81; 17 · 35 · 0; 0); front 46 / 52 | 48 / 48 / 52 (0.82; 5 · 42 · 1; 1); front 47 / 52 | 23 / 29 / 52 (0.79; 5 · 24 · 0; 1); front 46 / 52 |
| a barrel of the OTHER color, beside it and lower | 51 / 51 / 52 (0.84; 10 · 41 · 0; 1); front 46 / 52 | 48 / 48 / 52 (0.85; 3 · 44 · 1; 1); front 46 / 52 | 39 / 47 / 52 (0.81; 10 · 32 · 5; 2); front 46 / 52 |
| a barrel of the OTHER color, straight in front | 19 / 20 / 23 (0.84; 2 · 17 · 1; 2); front 15 / 23 | 19 / 20 / 24 (0.84; 0 · 20 · 0; 2); front 20 / 24 | 7 / 16 / 25 (0.80; 1 · 10 · 5; 1); front 20 / 25 |
| a barrel of the SAME color, beside it | 44 / 46 / 52 (0.80; 11 · 32 · 3; 1); front 39 / 52 | 26 / 29 / 52 (0.68; 6 · 10 · 13; 0); front 35 / 52 | 11 / 13 / 52 (0.72; 0 · 2 · 11; 0); front 36 / 52 |
| a barrel of the SAME color, beside it and lower | 49 / 51 / 52 (0.81; 16 · 33 · 2; 0); front 46 / 52 | 45 / 47 / 52 (0.83; 2 · 44 · 1; 0); front 43 / 52 | 14 / 18 / 52 (0.80; 1 · 16 · 1; 0); front 46 / 52 |
| a barrel of the SAME color, straight in front | 22 / 22 / 23 (0.85; 1 · 21 · 0; 1); front 17 / 23 | 14 / 18 / 24 (0.83; 1 · 14 · 3; 1); front 19 / 24 | 2 / 6 / 25 (0.69; 2 · 4 · 0; 0); front 21 / 25 |
| a plain block of the barrel's body color | 52 / 52 / 52 (0.85; 1 · 51 · 0; 2) | 51 / 51 / 52 (0.85; 2 · 47 · 2; 0) | 3 / 3 / 52 (0.74; 1 · 0 · 2; 0) |
| a plain block of the barrel's stripe color | 52 / 52 / 52 (0.85; 7 · 45 · 0; 2) | 51 / 51 / 52 (0.84; 6 · 45 · 0; 2) | 1 / 2 / 52 (0.73; 1 · 1 · 0; 3) |

### `rules`: why the hidden barrel was not found under the v2 rule (all pools)

- cut by the frame edge, 50 %: stripe_refused:side_unexplained 1
- cut by the frame edge, 75 %: stripe_refused:width 94, stripe_refused:height 2, stripe_not_sandwiched 1
- a straight upright edge, one side, 50 %: stripe_refused:side_unexplained 14, misplaced 4
- a straight upright edge, one side, 75 %: stripe_refused:width 94, stripe_refused:side_unexplained 3, stripe_refused:height 2, stripe_not_sandwiched 1
- a slanted edge, one side, 50 %: stripe_refused:side_unexplained 44, misplaced 2
- a slanted edge, one side, 75 %: stripe_refused:width 178, stripe_refused:area 15, stripe_refused:height 4, stripe_refused:side_unexplained 1, stripe_hidden 1, stripe_not_sandwiched 1
- both sides cut, 50 %: misplaced 1
- both sides cut, 75 %: stripe_refused:width 34, stripe_refused:side_unexplained 15, stripe_not_sandwiched 1
- hidden from above, 50 %: stripe_not_sandwiched 47, stripe_refused:width 1
- hidden from above, 75 %: stripe_hidden 49, stripe_refused:width 1
- hidden from below (a low thing in front), 25 %: misplaced 1
- hidden from below (a low thing in front), 50 %: stripe_not_sandwiched 49
- hidden from below (a low thing in front), 75 %: stripe_hidden 49
- a post across the middle, 25 %: stripe_refused:width 1
- a post across the middle, 50 %: stripe_refused:width 37, stripe_refused:side_unexplained 3, stripe_refused:height 1
- a post across the middle, 75 %: stripe_refused:width 36, stripe_refused:area 13, stripe_hidden 1
- a barrel of the OTHER color, beside it, 25 %: stripe_refused:height 1
- a barrel of the OTHER color, beside it, 50 %: stripe_refused:height 4, misplaced 2
- a barrel of the OTHER color, beside it, 75 %: stripe_refused:height 25, stripe_refused:width 14, misplaced 11, stripe_refused:side_unexplained 1
- a barrel of the OTHER color, beside it and lower, 25 %: stripe_refused:height 2
- a barrel of the OTHER color, beside it and lower, 50 %: stripe_refused:height 6, stripe_refused:width 2
- a barrel of the OTHER color, beside it and lower, 75 %: misplaced 13, stripe_refused:width 5, stripe_refused:height 5
- a barrel of the OTHER color, straight in front, 25 %: stripe_refused:height 4, misplaced 2, stripe_not_sandwiched 2
- a barrel of the OTHER color, straight in front, 50 %: stripe_refused:height 8, misplaced 1, stripe_refused:body_min 1
- a barrel of the OTHER color, straight in front, 75 %: stripe_refused:height 20, misplaced 11, stripe_refused:top_against_barrel 1
- a barrel of the SAME color, beside it, 25 %: misplaced 19
- a barrel of the SAME color, beside it, 50 %: misplaced 64
- a barrel of the SAME color, beside it, 75 %: misplaced 83, stripe_refused:width 1
- a barrel of the SAME color, beside it and lower, 25 %: misplaced 8, stripe_refused:height 1
- a barrel of the SAME color, beside it and lower, 50 %: misplaced 13, stripe_refused:height 2
- a barrel of the SAME color, beside it and lower, 75 %: misplaced 74
- a barrel of the SAME color, straight in front, 25 %: misplaced 1, stripe_refused:height 1, stripe_hidden 1
- a barrel of the SAME color, straight in front, 50 %: misplaced 19
- a barrel of the SAME color, straight in front, 75 %: misplaced 47
- a plain block of the barrel's body color, 50 %: stripe_refused:side_unexplained 1
- a plain block of the barrel's body color, 75 %: stripe_refused:width 93, stripe_refused:height 2
- a plain block of the barrel's stripe color, 50 %: stripe_refused:width 1
- a plain block of the barrel's stripe color, 75 %: stripe_refused:width 95, stripe_refused:height 1, misplaced 1

## `union`, all three pools

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 / 100 / 100 (0.92; 1 · 99 · 0; 0) | 100 / 100 / 100 (0.90; 3 · 95 · 2; 0) | 6 / 6 / 100 (0.82; 0 · 3 · 3; 0) |
| a straight upright edge, one side | 100 / 100 / 100 (0.76; 12 · 88 · 0; 0) | 91 / 95 / 100 (0.59; 4 · 91 · 0; 0) | 0 / 0 / 100 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 200 / 200 / 200 (0.82; 83 · 114 · 3; 0) | 175 / 178 / 200 (0.76; 9 · 169 · 0; 0) | 0 / 0 / 200 (-; 0 · 0 · 0; 0) |
| both sides cut | 50 / 50 / 50 (0.88; 10 · 40 · 0; 0) | 49 / 50 / 50 (0.90; 2 · 48 · 0; 0) | 7 / 7 / 50 (0.79; 1 · 6 · 0; 0) |
| hidden from above | 50 / 50 / 50 (0.87; 2 · 47 · 1; 0) | 2 / 2 / 50 (0.83; 2 · 0 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 49 / 50 / 50 (0.89; 1 · 49 · 0; 0) | 1 / 1 / 50 (0.91; 0 · 1 · 0; 0) | 1 / 1 / 50 (0.53; 1 · 0 · 0; 0) |
| a post across the middle | 50 / 50 / 50 (0.90; 1 · 49 · 0; 0) | 32 / 33 / 50 (0.87; 0 · 33 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 100 / 100 / 100 (0.83; 26 · 74 · 0; 0); front 94 / 100 | 99 / 99 / 100 (0.85; 5 · 91 · 3; 6); front 95 / 100 | 50 / 61 / 100 (0.81; 10 · 48 · 3; 1); front 94 / 100 |
| a barrel of the OTHER color, beside it and lower | 100 / 100 / 100 (0.85; 17 · 83 · 0; 1); front 90 / 100 | 98 / 99 / 100 (0.86; 5 · 93 · 1; 1); front 90 / 100 | 77 / 90 / 100 (0.83; 15 · 67 · 8; 2); front 90 / 100 |
| a barrel of the OTHER color, straight in front | 43 / 45 / 47 (0.87; 2 · 42 · 1; 3); front 32 / 47 | 40 / 42 / 48 (0.87; 0 · 42 · 0; 3); front 39 / 48 | 20 / 34 / 49 (0.81; 3 · 26 · 5; 1); front 42 / 49 |
| a barrel of the SAME color, beside it | 81 / 88 / 100 (0.81; 18 · 65 · 5; 2); front 81 / 100 | 36 / 49 / 100 (0.66; 7 · 14 · 28; 2); front 77 / 100 | 16 / 31 / 100 (0.70; 1 · 3 · 27; 4); front 79 / 100 |
| a barrel of the SAME color, beside it and lower | 92 / 99 / 100 (0.83; 26 · 70 · 3; 0); front 92 / 100 | 87 / 91 / 100 (0.84; 5 · 83 · 3; 0); front 88 / 100 | 26 / 33 / 100 (0.82; 3 · 28 · 2; 0); front 89 / 100 |
| a barrel of the SAME color, straight in front | 44 / 45 / 47 (0.87; 2 · 43 · 0; 4); front 34 / 47 | 32 / 43 / 48 (0.84; 5 · 34 · 4; 6); front 38 / 48 | 4 / 15 / 49 (0.74; 4 · 11 · 0; 2); front 42 / 49 |
| a plain block of the barrel's body color | 100 / 100 / 100 (0.87; 1 · 99 · 0; 2) | 99 / 99 / 100 (0.87; 2 · 95 · 2; 0) | 5 / 5 / 100 (0.78; 1 · 2 · 2; 0) |
| a plain block of the barrel's stripe color | 100 / 100 / 100 (0.86; 9 · 91 · 0; 2) | 99 / 99 / 100 (0.86; 8 · 91 · 0; 2) | 3 / 4 / 100 (0.78; 1 · 3 · 0; 3) |

## `union`, HOME hand masks

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 24 / 24 / 24 (0.97; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.96; 1 · 23 · 0; 0) | 3 / 3 / 24 (0.82; 0 · 1 · 2; 0) |
| a straight upright edge, one side | 24 / 24 / 24 (0.79; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.61; 0 · 24 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 48 / 48 / 48 (0.86; 16 · 32 · 0; 0) | 47 / 48 / 48 (0.78; 0 · 48 · 0; 0) | 0 / 0 / 48 (-; 0 · 0 · 0; 0) |
| both sides cut | 12 / 12 / 12 (0.91; 2 · 10 · 0; 0) | 12 / 12 / 12 (0.94; 0 · 12 · 0; 0) | 3 / 3 / 12 (0.86; 0 · 3 · 0; 0) |
| hidden from above | 12 / 12 / 12 (0.91; 1 · 10 · 1; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 12 / 12 / 12 (0.93; 1 · 11 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a post across the middle | 12 / 12 / 12 (0.95; 1 · 11 · 0; 0) | 11 / 11 / 12 (0.88; 0 · 11 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 24 / 24 / 24 (0.90; 2 · 22 · 0; 0); front 24 / 24 | 24 / 24 / 24 (0.90; 0 · 24 · 0; 1); front 24 / 24 | 19 / 19 / 24 (0.89; 1 · 15 · 3; 0); front 24 / 24 |
| a barrel of the OTHER color, beside it and lower | 24 / 24 / 24 (0.91; 1 · 23 · 0; 0); front 20 / 24 | 24 / 24 / 24 (0.91; 0 · 24 · 0; 0); front 20 / 24 | 21 / 22 / 24 (0.91; 0 · 21 · 1; 0); front 20 / 24 |
| a barrel of the OTHER color, straight in front | 12 / 12 / 12 (0.93; 0 · 12 · 0; 0); front 8 / 12 | 11 / 11 / 12 (0.95; 0 · 11 · 0; 0); front 9 / 12 | 8 / 9 / 12 (0.85; 1 · 8 · 0; 0); front 11 / 12 |
| a barrel of the SAME color, beside it | 16 / 21 / 24 (0.82; 2 · 17 · 2; 0); front 21 / 24 | 1 / 9 / 24 (0.60; 0 · 0 · 9; 0); front 23 / 24 | 1 / 9 / 24 (0.72; 0 · 0 · 9; 0); front 23 / 24 |
| a barrel of the SAME color, beside it and lower | 20 / 23 / 24 (0.87; 6 · 17 · 0; 0); front 23 / 24 | 18 / 19 / 24 (0.88; 1 · 17 · 1; 0); front 22 / 24 | 8 / 8 / 24 (0.88; 0 · 8 · 0; 0); front 21 / 24 |
| a barrel of the SAME color, straight in front | 12 / 12 / 12 (0.92; 1 · 11 · 0; 0); front 9 / 12 | 11 / 12 / 12 (0.92; 1 · 11 · 0; 2); front 10 / 12 | 1 / 4 / 12 (0.79; 1 · 3 · 0; 0); front 11 / 12 |
| a plain block of the barrel's body color | 24 / 24 / 24 (0.92; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.92; 0 · 24 · 0; 0) | 1 / 1 / 24 (0.90; 0 · 1 · 0; 0) |
| a plain block of the barrel's stripe color | 24 / 24 / 24 (0.91; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.90; 1 · 23 · 0; 0) | 1 / 1 / 24 (0.89; 0 · 1 · 0; 0) |

## `union`, HOME color model

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 24 / 24 / 24 (0.90; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.87; 1 · 22 · 1; 0) | 1 / 1 / 24 (0.78; 0 · 0 · 1; 0) |
| a straight upright edge, one side | 24 / 24 / 24 (0.76; 3 · 21 · 0; 0) | 23 / 24 / 24 (0.58; 0 · 24 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 48 / 48 / 48 (0.81; 20 · 28 · 0; 0) | 44 / 44 / 48 (0.76; 0 · 44 · 0; 0) | 0 / 0 / 48 (-; 0 · 0 · 0; 0) |
| both sides cut | 12 / 12 / 12 (0.88; 2 · 10 · 0; 0) | 12 / 12 / 12 (0.90; 0 · 12 · 0; 0) | 2 / 2 / 12 (0.71; 0 · 2 · 0; 0) |
| hidden from above | 12 / 12 / 12 (0.87; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 12 / 12 / 12 (0.89; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a post across the middle | 12 / 12 / 12 (0.89; 0 · 12 · 0; 0) | 9 / 10 / 12 (0.86; 0 · 10 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 24 / 24 / 24 (0.81; 7 · 17 · 0; 0); front 24 / 24 | 24 / 24 / 24 (0.84; 0 · 22 · 2; 4); front 24 / 24 | 8 / 13 / 24 (0.74; 4 · 9 · 0; 0); front 24 / 24 |
| a barrel of the OTHER color, beside it and lower | 24 / 24 / 24 (0.82; 6 · 18 · 0; 0); front 24 / 24 | 24 / 24 / 24 (0.86; 1 · 23 · 0; 0); front 24 / 24 | 17 / 21 / 24 (0.81; 5 · 14 · 2; 0); front 24 / 24 |
| a barrel of the OTHER color, straight in front | 11 / 12 / 12 (0.85; 0 · 12 · 0; 1); front 9 / 12 | 9 / 10 / 12 (0.85; 0 · 10 · 0; 1); front 10 / 12 | 4 / 7 / 12 (0.81; 1 · 6 · 0; 0); front 11 / 12 |
| a barrel of the SAME color, beside it | 21 / 21 / 24 (0.82; 5 · 16 · 0; 1); front 21 / 24 | 9 / 11 / 24 (0.64; 1 · 4 · 6; 2); front 19 / 24 | 4 / 9 / 24 (0.67; 1 · 1 · 7; 4); front 20 / 24 |
| a barrel of the SAME color, beside it and lower | 22 / 24 / 24 (0.84; 3 · 20 · 1; 0); front 22 / 24 | 22 / 23 / 24 (0.83; 1 · 21 · 1; 0); front 22 / 24 | 4 / 7 / 24 (0.80; 2 · 4 · 1; 0); front 22 / 24 |
| a barrel of the SAME color, straight in front | 10 / 11 / 12 (0.88; 0 · 11 · 0; 3); front 8 / 12 | 5 / 10 / 12 (0.78; 2 · 7 · 1; 3); front 9 / 12 | 0 / 3 / 12 (0.73; 1 · 2 · 0; 2); front 10 / 12 |
| a plain block of the barrel's body color | 24 / 24 / 24 (0.86; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.86; 0 · 24 · 0; 0) | 1 / 1 / 24 (0.76; 0 · 1 · 0; 0) |
| a plain block of the barrel's stripe color | 24 / 24 / 24 (0.85; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.84; 1 · 23 · 0; 0) | 1 / 1 / 24 (0.76; 0 · 1 · 0; 0) |

## `union`, CAMPUS color model

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 52 / 52 / 52 (0.91; 0 · 52 · 0; 0) | 52 / 52 / 52 (0.88; 1 · 50 · 1; 0) | 2 / 2 / 52 (0.84; 0 · 2 · 0; 0) |
| a straight upright edge, one side | 52 / 52 / 52 (0.75; 9 · 43 · 0; 0) | 44 / 47 / 52 (0.58; 4 · 43 · 0; 0) | 0 / 0 / 52 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 104 / 104 / 104 (0.81; 47 · 54 · 3; 0) | 84 / 86 / 104 (0.75; 9 · 77 · 0; 0) | 0 / 0 / 104 (-; 0 · 0 · 0; 0) |
| both sides cut | 26 / 26 / 26 (0.86; 6 · 20 · 0; 0) | 25 / 26 / 26 (0.88; 2 · 24 · 0; 0) | 2 / 2 / 26 (0.77; 1 · 1 · 0; 0) |
| hidden from above | 26 / 26 / 26 (0.86; 1 · 25 · 0; 0) | 2 / 2 / 26 (0.83; 2 · 0 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 25 / 26 / 26 (0.87; 0 · 26 · 0; 0) | 1 / 1 / 26 (0.91; 0 · 1 · 0; 0) | 1 / 1 / 26 (0.53; 1 · 0 · 0; 0) |
| a post across the middle | 26 / 26 / 26 (0.88; 0 · 26 · 0; 0) | 12 / 12 / 26 (0.88; 0 · 12 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 52 / 52 / 52 (0.81; 17 · 35 · 0; 0); front 46 / 52 | 51 / 51 / 52 (0.82; 5 · 45 · 1; 1); front 47 / 52 | 23 / 29 / 52 (0.79; 5 · 24 · 0; 1); front 46 / 52 |
| a barrel of the OTHER color, beside it and lower | 52 / 52 / 52 (0.84; 10 · 42 · 0; 1); front 46 / 52 | 50 / 51 / 52 (0.84; 4 · 46 · 1; 1); front 46 / 52 | 39 / 47 / 52 (0.81; 10 · 32 · 5; 2); front 46 / 52 |
| a barrel of the OTHER color, straight in front | 20 / 21 / 23 (0.84; 2 · 18 · 1; 2); front 15 / 23 | 20 / 21 / 24 (0.84; 0 · 21 · 0; 2); front 20 / 24 | 8 / 18 / 25 (0.80; 1 · 12 · 5; 1); front 20 / 25 |
| a barrel of the SAME color, beside it | 44 / 46 / 52 (0.80; 11 · 32 · 3; 1); front 39 / 52 | 26 / 29 / 52 (0.68; 6 · 10 · 13; 0); front 35 / 52 | 11 / 13 / 52 (0.72; 0 · 2 · 11; 0); front 36 / 52 |
| a barrel of the SAME color, beside it and lower | 50 / 52 / 52 (0.81; 17 · 33 · 2; 0); front 47 / 52 | 47 / 49 / 52 (0.83; 3 · 45 · 1; 0); front 44 / 52 | 14 / 18 / 52 (0.80; 1 · 16 · 1; 0); front 46 / 52 |
| a barrel of the SAME color, straight in front | 22 / 22 / 23 (0.85; 1 · 21 · 0; 1); front 17 / 23 | 16 / 21 / 24 (0.83; 2 · 16 · 3; 1); front 19 / 24 | 3 / 8 / 25 (0.72; 2 · 6 · 0; 0); front 21 / 25 |
| a plain block of the barrel's body color | 52 / 52 / 52 (0.85; 1 · 51 · 0; 2) | 51 / 51 / 52 (0.85; 2 · 47 · 2; 0) | 3 / 3 / 52 (0.74; 1 · 0 · 2; 0) |
| a plain block of the barrel's stripe color | 52 / 52 / 52 (0.85; 7 · 45 · 0; 2) | 51 / 51 / 52 (0.84; 6 · 45 · 0; 2) | 1 / 2 / 52 (0.73; 1 · 1 · 0; 3) |

### `union`: why the hidden barrel was not found under the v2 rule (all pools)

- cut by the frame edge, 75 %: stripe_refused:width 91, stripe_refused:height 2, stripe_not_sandwiched 1
- a straight upright edge, one side, 50 %: stripe_refused:side_unexplained 5, misplaced 4
- a straight upright edge, one side, 75 %: stripe_refused:width 94, stripe_refused:side_unexplained 3, stripe_refused:height 2, stripe_not_sandwiched 1
- a slanted edge, one side, 50 %: stripe_refused:side_unexplained 22, misplaced 3
- a slanted edge, one side, 75 %: stripe_refused:width 178, stripe_refused:area 15, stripe_refused:height 4, stripe_refused:side_unexplained 1, stripe_hidden 1, stripe_not_sandwiched 1
- both sides cut, 50 %: misplaced 1
- both sides cut, 75 %: stripe_refused:width 34, stripe_refused:side_unexplained 8, stripe_not_sandwiched 1
- hidden from above, 50 %: stripe_not_sandwiched 47, stripe_refused:width 1
- hidden from above, 75 %: stripe_hidden 49, stripe_refused:width 1
- hidden from below (a low thing in front), 25 %: misplaced 1
- hidden from below (a low thing in front), 50 %: stripe_not_sandwiched 49
- hidden from below (a low thing in front), 75 %: stripe_hidden 49
- a post across the middle, 50 %: stripe_refused:width 15, misplaced 1, stripe_refused:height 1, stripe_refused:side_unexplained 1
- a post across the middle, 75 %: stripe_refused:width 36, stripe_refused:area 13, stripe_hidden 1
- a barrel of the OTHER color, beside it, 50 %: stripe_refused:height 1
- a barrel of the OTHER color, beside it, 75 %: stripe_refused:height 24, stripe_refused:width 14, misplaced 11, stripe_refused:side_unexplained 1
- a barrel of the OTHER color, beside it and lower, 50 %: stripe_refused:width 1, misplaced 1
- a barrel of the OTHER color, beside it and lower, 75 %: misplaced 13, stripe_refused:width 5, stripe_refused:height 5
- a barrel of the OTHER color, straight in front, 25 %: misplaced 2, stripe_not_sandwiched 1, stripe_refused:height 1
- a barrel of the OTHER color, straight in front, 50 %: stripe_refused:height 5, misplaced 2, stripe_refused:body_min 1
- a barrel of the OTHER color, straight in front, 75 %: misplaced 14, stripe_refused:height 14, stripe_refused:top_against_barrel 1
- a barrel of the SAME color, beside it, 25 %: misplaced 19
- a barrel of the SAME color, beside it, 50 %: misplaced 64
- a barrel of the SAME color, beside it, 75 %: misplaced 83, stripe_refused:width 1
- a barrel of the SAME color, beside it and lower, 25 %: misplaced 8
- a barrel of the SAME color, beside it and lower, 50 %: misplaced 13
- a barrel of the SAME color, beside it and lower, 75 %: misplaced 74
- a barrel of the SAME color, straight in front, 25 %: misplaced 1, stripe_refused:height 1, stripe_hidden 1
- a barrel of the SAME color, straight in front, 50 %: misplaced 16
- a barrel of the SAME color, straight in front, 75 %: misplaced 45
- a plain block of the barrel's body color, 50 %: stripe_refused:side_unexplained 1
- a plain block of the barrel's body color, 75 %: stripe_refused:width 93, stripe_refused:height 2
- a plain block of the barrel's stripe color, 50 %: stripe_refused:width 1
- a plain block of the barrel's stripe color, 75 %: stripe_refused:width 95, stripe_refused:height 1, misplaced 1

