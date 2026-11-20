# The occlusion scorecard, in full

git a485ecf; camera AIM_4A8B6118_BOXFIT; train frames only. Source barrels: HOME hand masks 12, HOME color model 12, CAMPUS color model 26 (left out because `base` does not find them alone and unhidden: 0).

Each cell: found under the v2 rule / box in the right place / scenes; (mean overlap of the right-place boxes with the FULL box; too small · about right · too big; false boxes). `front` = the barrel pasted in front, found / pasted.

## `combined`, all three pools

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 / 100 / 100 (0.92; 1 · 99 · 0; 0) | 99 / 99 / 100 (0.90; 3 · 94 · 2; 0) | 87 / 88 / 100 (0.82; 26 · 54 · 8; 0) |
| a straight upright edge, one side | 100 / 100 / 100 (0.83; 12 · 88 · 0; 0) | 90 / 94 / 100 (0.77; 4 · 90 · 0; 0) | 2 / 2 / 100 (0.80; 1 · 1 · 0; 0) |
| a slanted edge, one side | 200 / 200 / 200 (0.82; 83 · 116 · 1; 0) | 170 / 172 / 200 (0.84; 9 · 163 · 0; 0) | 0 / 0 / 200 (-; 0 · 0 · 0; 0) |
| both sides cut | 50 / 50 / 50 (0.88; 10 · 40 · 0; 0) | 49 / 50 / 50 (0.90; 2 · 48 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| hidden from above | 50 / 50 / 50 (0.87; 2 · 47 · 1; 0) | 45 / 45 / 50 (0.88; 2 · 42 · 1; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 49 / 50 / 50 (0.89; 1 · 49 · 0; 0) | 40 / 40 / 50 (0.90; 0 · 40 · 0; 0) | 1 / 1 / 50 (0.53; 1 · 0 · 0; 0) |
| a post across the middle | 49 / 49 / 50 (0.90; 1 · 48 · 0; 0) | 41 / 41 / 50 (0.88; 2 · 39 · 0; 0) | 9 / 11 / 50 (0.86; 2 · 9 · 0; 0) |
| a barrel of the OTHER color, beside it | 99 / 99 / 100 (0.83; 26 · 73 · 0; 0); front 94 / 100 | 94 / 96 / 100 (0.84; 6 · 87 · 3; 4); front 95 / 100 | 60 / 71 / 100 (0.81; 10 · 58 · 3; 1); front 94 / 100 |
| a barrel of the OTHER color, beside it and lower | 98 / 98 / 100 (0.85; 17 · 81 · 0; 1); front 90 / 100 | 92 / 92 / 100 (0.86; 4 · 87 · 1; 1); front 90 / 100 | 81 / 94 / 100 (0.83; 15 · 71 · 8; 2); front 90 / 100 |
| a barrel of the OTHER color, straight in front | 40 / 42 / 47 (0.87; 2 · 39 · 1; 3); front 32 / 47 | 38 / 39 / 48 (0.87; 0 · 39 · 0; 3); front 39 / 48 | 22 / 35 / 49 (0.82; 1 · 29 · 5; 1); front 42 / 49 |
| a barrel of the SAME color, beside it | 96 / 99 / 100 (0.83; 19 · 78 · 2; 2); front 92 / 100 | 88 / 97 / 100 (0.79; 18 · 72 · 7; 2); front 90 / 100 | 18 / 34 / 100 (0.71; 2 · 3 · 29; 4); front 79 / 100 |
| a barrel of the SAME color, beside it and lower | 91 / 99 / 100 (0.83; 25 · 71 · 3; 0); front 91 / 100 | 87 / 94 / 100 (0.83; 6 · 83 · 5; 0); front 87 / 100 | 42 / 49 / 100 (0.83; 3 · 44 · 2; 0); front 89 / 100 |
| a barrel of the SAME color, straight in front | 44 / 45 / 47 (0.87; 2 · 43 · 0; 4); front 34 / 47 | 29 / 37 / 48 (0.85; 3 · 30 · 4; 6); front 38 / 48 | 8 / 14 / 49 (0.76; 3 · 11 · 0; 2); front 42 / 49 |
| a plain block of the barrel's body color | 100 / 100 / 100 (0.87; 1 · 99 · 0; 2) | 99 / 99 / 100 (0.87; 2 · 95 · 2; 0) | 5 / 5 / 100 (0.78; 1 · 2 · 2; 0) |
| a plain block of the barrel's stripe color | 100 / 100 / 100 (0.86; 9 · 91 · 0; 2) | 99 / 99 / 100 (0.86; 8 · 91 · 0; 2) | 3 / 4 / 100 (0.78; 1 · 3 · 0; 3) |

## `combined`, HOME hand masks

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 24 / 24 / 24 (0.97; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.96; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.90; 3 · 21 · 0; 0) |
| a straight upright edge, one side | 24 / 24 / 24 (0.89; 0 · 24 · 0; 0) | 23 / 23 / 24 (0.84; 0 · 23 · 0; 0) | 1 / 1 / 24 (0.90; 0 · 1 · 0; 0) |
| a slanted edge, one side | 48 / 48 / 48 (0.86; 16 · 32 · 0; 0) | 45 / 45 / 48 (0.89; 0 · 45 · 0; 0) | 0 / 0 / 48 (-; 0 · 0 · 0; 0) |
| both sides cut | 12 / 12 / 12 (0.91; 2 · 10 · 0; 0) | 12 / 12 / 12 (0.94; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from above | 12 / 12 / 12 (0.91; 1 · 10 · 1; 0) | 12 / 12 / 12 (0.92; 0 · 11 · 1; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 12 / 12 / 12 (0.93; 1 · 11 · 0; 0) | 11 / 11 / 12 (0.95; 0 · 11 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a post across the middle | 12 / 12 / 12 (0.95; 1 · 11 · 0; 0) | 12 / 12 / 12 (0.94; 1 · 11 · 0; 0) | 6 / 6 / 12 (0.89; 0 · 6 · 0; 0) |
| a barrel of the OTHER color, beside it | 23 / 23 / 24 (0.90; 2 · 21 · 0; 0); front 24 / 24 | 24 / 24 / 24 (0.90; 0 · 24 · 0; 1); front 24 / 24 | 22 / 22 / 24 (0.88; 1 · 18 · 3; 0); front 24 / 24 |
| a barrel of the OTHER color, beside it and lower | 24 / 24 / 24 (0.91; 1 · 23 · 0; 0); front 20 / 24 | 23 / 23 / 24 (0.91; 0 · 23 · 0; 0); front 20 / 24 | 23 / 24 / 24 (0.90; 0 · 23 · 1; 0); front 20 / 24 |
| a barrel of the OTHER color, straight in front | 11 / 11 / 12 (0.93; 0 · 11 · 0; 0); front 8 / 12 | 10 / 10 / 12 (0.95; 0 · 10 · 0; 0); front 9 / 12 | 9 / 10 / 12 (0.87; 0 · 10 · 0; 0); front 11 / 12 |
| a barrel of the SAME color, beside it | 21 / 24 / 24 (0.85; 3 · 21 · 0; 0); front 24 / 24 | 16 / 24 / 24 (0.83; 2 · 20 · 2; 0); front 24 / 24 | 1 / 10 / 24 (0.73; 0 · 0 · 10; 0); front 23 / 24 |
| a barrel of the SAME color, beside it and lower | 20 / 24 / 24 (0.87; 6 · 18 · 0; 0); front 23 / 24 | 19 / 22 / 24 (0.85; 2 · 17 · 3; 0); front 22 / 24 | 10 / 10 / 24 (0.88; 0 · 10 · 0; 0); front 21 / 24 |
| a barrel of the SAME color, straight in front | 12 / 12 / 12 (0.92; 1 · 11 · 0; 0); front 9 / 12 | 11 / 12 / 12 (0.92; 1 · 11 · 0; 2); front 10 / 12 | 4 / 4 / 12 (0.85; 0 · 4 · 0; 0); front 11 / 12 |
| a plain block of the barrel's body color | 24 / 24 / 24 (0.92; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.92; 0 · 24 · 0; 0) | 1 / 1 / 24 (0.90; 0 · 1 · 0; 0) |
| a plain block of the barrel's stripe color | 24 / 24 / 24 (0.90; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.90; 1 · 23 · 0; 0) | 1 / 1 / 24 (0.89; 0 · 1 · 0; 0) |

## `combined`, HOME color model

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 24 / 24 / 24 (0.90; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.87; 1 · 22 · 1; 0) | 22 / 22 / 24 (0.80; 7 · 12 · 3; 0) |
| a straight upright edge, one side | 24 / 24 / 24 (0.83; 3 · 21 · 0; 0) | 22 / 23 / 24 (0.78; 0 · 23 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 48 / 48 / 48 (0.81; 20 · 28 · 0; 0) | 41 / 41 / 48 (0.86; 0 · 41 · 0; 0) | 0 / 0 / 48 (-; 0 · 0 · 0; 0) |
| both sides cut | 12 / 12 / 12 (0.88; 2 · 10 · 0; 0) | 12 / 12 / 12 (0.90; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from above | 12 / 12 / 12 (0.87; 0 · 12 · 0; 0) | 10 / 10 / 12 (0.90; 0 · 10 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 12 / 12 / 12 (0.89; 0 · 12 · 0; 0) | 8 / 8 / 12 (0.90; 0 · 8 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a post across the middle | 12 / 12 / 12 (0.89; 0 · 12 · 0; 0) | 10 / 10 / 12 (0.88; 0 · 10 · 0; 0) | 2 / 3 / 12 (0.82; 1 · 2 · 0; 0) |
| a barrel of the OTHER color, beside it | 24 / 24 / 24 (0.81; 7 · 17 · 0; 0); front 24 / 24 | 22 / 24 / 24 (0.80; 1 · 21 · 2; 2); front 24 / 24 | 11 / 16 / 24 (0.75; 4 · 12 · 0; 0); front 24 / 24 |
| a barrel of the OTHER color, beside it and lower | 23 / 23 / 24 (0.82; 6 · 17 · 0; 0); front 24 / 24 | 21 / 21 / 24 (0.85; 1 · 20 · 0; 0); front 24 / 24 | 18 / 22 / 24 (0.81; 5 · 15 · 2; 0); front 24 / 24 |
| a barrel of the OTHER color, straight in front | 10 / 11 / 12 (0.85; 0 · 11 · 0; 1); front 9 / 12 | 9 / 9 / 12 (0.86; 0 · 9 · 0; 1); front 10 / 12 | 5 / 7 / 12 (0.82; 0 · 7 · 0; 0); front 11 / 12 |
| a barrel of the SAME color, beside it | 24 / 24 / 24 (0.81; 5 · 19 · 0; 1); front 24 / 24 | 22 / 23 / 24 (0.80; 4 · 18 · 1; 2); front 24 / 24 | 5 / 10 / 24 (0.68; 1 · 1 · 8; 4); front 20 / 24 |
| a barrel of the SAME color, beside it and lower | 22 / 24 / 24 (0.84; 3 · 20 · 1; 0); front 22 / 24 | 22 / 24 / 24 (0.82; 1 · 22 · 1; 0); front 22 / 24 | 10 / 13 / 24 (0.82; 2 · 10 · 1; 0); front 22 / 24 |
| a barrel of the SAME color, straight in front | 10 / 11 / 12 (0.88; 0 · 11 · 0; 3); front 8 / 12 | 4 / 7 / 12 (0.79; 1 · 5 · 1; 3); front 9 / 12 | 0 / 2 / 12 (0.74; 1 · 1 · 0; 2); front 10 / 12 |
| a plain block of the barrel's body color | 24 / 24 / 24 (0.86; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.86; 0 · 24 · 0; 0) | 1 / 1 / 24 (0.76; 0 · 1 · 0; 0) |
| a plain block of the barrel's stripe color | 24 / 24 / 24 (0.84; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.84; 1 · 23 · 0; 0) | 1 / 1 / 24 (0.76; 0 · 1 · 0; 0) |

## `combined`, CAMPUS color model

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 52 / 52 / 52 (0.91; 0 · 52 · 0; 0) | 51 / 51 / 52 (0.88; 1 · 49 · 1; 0) | 41 / 42 / 52 (0.79; 16 · 21 · 5; 0) |
| a straight upright edge, one side | 52 / 52 / 52 (0.80; 9 · 43 · 0; 0) | 45 / 48 / 52 (0.72; 4 · 44 · 0; 0) | 1 / 1 / 52 (0.69; 1 · 0 · 0; 0) |
| a slanted edge, one side | 104 / 104 / 104 (0.80; 47 · 56 · 1; 0) | 84 / 86 / 104 (0.80; 9 · 77 · 0; 0) | 0 / 0 / 104 (-; 0 · 0 · 0; 0) |
| both sides cut | 26 / 26 / 26 (0.86; 6 · 20 · 0; 0) | 25 / 26 / 26 (0.88; 2 · 24 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| hidden from above | 26 / 26 / 26 (0.86; 1 · 25 · 0; 0) | 23 / 23 / 26 (0.85; 2 · 21 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 25 / 26 / 26 (0.87; 0 · 26 · 0; 0) | 21 / 21 / 26 (0.88; 0 · 21 · 0; 0) | 1 / 1 / 26 (0.53; 1 · 0 · 0; 0) |
| a post across the middle | 25 / 25 / 26 (0.88; 0 · 25 · 0; 0) | 19 / 19 / 26 (0.85; 1 · 18 · 0; 0) | 1 / 2 / 26 (0.79; 1 · 1 · 0; 0) |
| a barrel of the OTHER color, beside it | 52 / 52 / 52 (0.81; 17 · 35 · 0; 0); front 46 / 52 | 48 / 48 / 52 (0.82; 5 · 42 · 1; 1); front 47 / 52 | 27 / 33 / 52 (0.79; 5 · 28 · 0; 1); front 46 / 52 |
| a barrel of the OTHER color, beside it and lower | 51 / 51 / 52 (0.84; 10 · 41 · 0; 1); front 46 / 52 | 48 / 48 / 52 (0.85; 3 · 44 · 1; 1); front 46 / 52 | 40 / 48 / 52 (0.81; 10 · 33 · 5; 2); front 46 / 52 |
| a barrel of the OTHER color, straight in front | 19 / 20 / 23 (0.84; 2 · 17 · 1; 2); front 15 / 23 | 19 / 20 / 24 (0.84; 0 · 20 · 0; 2); front 20 / 24 | 8 / 18 / 25 (0.80; 1 · 12 · 5; 1); front 20 / 25 |
| a barrel of the SAME color, beside it | 51 / 51 / 52 (0.82; 11 · 38 · 2; 1); front 44 / 52 | 50 / 50 / 52 (0.77; 12 · 34 · 4; 0); front 42 / 52 | 12 / 14 / 52 (0.72; 1 · 2 · 11; 0); front 36 / 52 |
| a barrel of the SAME color, beside it and lower | 49 / 51 / 52 (0.81; 16 · 33 · 2; 0); front 46 / 52 | 46 / 48 / 52 (0.83; 3 · 44 · 1; 0); front 43 / 52 | 22 / 26 / 52 (0.81; 1 · 24 · 1; 0); front 46 / 52 |
| a barrel of the SAME color, straight in front | 22 / 22 / 23 (0.85; 1 · 21 · 0; 1); front 17 / 23 | 14 / 18 / 24 (0.83; 1 · 14 · 3; 1); front 19 / 24 | 4 / 8 / 25 (0.72; 2 · 6 · 0; 0); front 21 / 25 |
| a plain block of the barrel's body color | 52 / 52 / 52 (0.85; 1 · 51 · 0; 2) | 51 / 51 / 52 (0.85; 2 · 47 · 2; 0) | 3 / 3 / 52 (0.74; 1 · 0 · 2; 0) |
| a plain block of the barrel's stripe color | 52 / 52 / 52 (0.84; 7 · 45 · 0; 2) | 51 / 51 / 52 (0.84; 6 · 45 · 0; 2) | 1 / 2 / 52 (0.73; 1 · 1 · 0; 3) |

### `combined`: why the hidden barrel was not found under the v2 rule (all pools)

- cut by the frame edge, 50 %: stripe_refused:side_unexplained 1
- cut by the frame edge, 75 %: stripe_refused:width 9, stripe_refused:height 2, misplaced 1, stripe_not_sandwiched 1
- a straight upright edge, one side, 50 %: stripe_refused:side_unexplained 6, misplaced 4
- a straight upright edge, one side, 75 %: stripe_refused:width 94, stripe_refused:height 2, stripe_refused:side_unexplained 1, stripe_not_sandwiched 1
- a slanted edge, one side, 50 %: stripe_refused:side_unexplained 28, misplaced 2
- a slanted edge, one side, 75 %: stripe_refused:width 178, stripe_refused:area 15, stripe_refused:height 4, stripe_refused:side_unexplained 1, stripe_hidden 1, stripe_not_sandwiched 1
- both sides cut, 50 %: misplaced 1
- both sides cut, 75 %: stripe_refused:width 34, stripe_refused:side_unexplained 15, stripe_not_sandwiched 1
- hidden from above, 50 %: stripe_not_sandwiched 4, stripe_refused:width 1
- hidden from above, 75 %: stripe_hidden 49, stripe_refused:width 1
- hidden from below (a low thing in front), 25 %: misplaced 1
- hidden from below (a low thing in front), 50 %: stripe_not_sandwiched 10
- hidden from below (a low thing in front), 75 %: stripe_hidden 49
- a post across the middle, 25 %: stripe_refused:width 1
- a post across the middle, 50 %: stripe_refused:width 7, stripe_refused:side_unexplained 1, stripe_refused:height 1
- a post across the middle, 75 %: stripe_refused:width 25, stripe_refused:area 13, misplaced 2, stripe_hidden 1
- a barrel of the OTHER color, beside it, 25 %: stripe_refused:height 1
- a barrel of the OTHER color, beside it, 50 %: stripe_refused:height 4, misplaced 2
- a barrel of the OTHER color, beside it, 75 %: stripe_refused:height 20, misplaced 11, stripe_refused:width 8, stripe_refused:side_unexplained 1
- a barrel of the OTHER color, beside it and lower, 25 %: stripe_refused:height 2
- a barrel of the OTHER color, beside it and lower, 50 %: stripe_refused:height 6, stripe_refused:width 2
- a barrel of the OTHER color, beside it and lower, 75 %: misplaced 13, stripe_refused:height 4, stripe_refused:width 2
- a barrel of the OTHER color, straight in front, 25 %: stripe_refused:height 3, misplaced 2, stripe_not_sandwiched 2
- a barrel of the OTHER color, straight in front, 50 %: stripe_refused:height 8, misplaced 1, stripe_refused:body_min 1
- a barrel of the OTHER color, straight in front, 75 %: misplaced 13, stripe_refused:height 13, stripe_refused:top_against_barrel 1
- a barrel of the SAME color, beside it, 25 %: misplaced 4
- a barrel of the SAME color, beside it, 50 %: misplaced 12
- a barrel of the SAME color, beside it, 75 %: misplaced 81, stripe_refused:width 1
- a barrel of the SAME color, beside it and lower, 25 %: misplaced 8, stripe_refused:height 1
- a barrel of the SAME color, beside it and lower, 50 %: misplaced 11, stripe_refused:height 2
- a barrel of the SAME color, beside it and lower, 75 %: misplaced 58
- a barrel of the SAME color, straight in front, 25 %: misplaced 1, stripe_refused:height 1, stripe_hidden 1
- a barrel of the SAME color, straight in front, 50 %: misplaced 19
- a barrel of the SAME color, straight in front, 75 %: misplaced 41
- a plain block of the barrel's body color, 50 %: stripe_refused:side_unexplained 1
- a plain block of the barrel's body color, 75 %: stripe_refused:width 93, stripe_refused:height 2
- a plain block of the barrel's stripe color, 50 %: stripe_refused:width 1
- a plain block of the barrel's stripe color, 75 %: stripe_refused:width 95, stripe_refused:height 1, misplaced 1

## `combined+verify`, all three pools

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 / 100 / 100 (0.92; 1 · 99 · 0; 0) | 98 / 98 / 100 (0.90; 3 · 93 · 2; 0) | 32 / 32 / 100 (0.89; 3 · 27 · 2; 0) |
| a straight upright edge, one side | 99 / 99 / 100 (0.83; 12 · 87 · 0; 0) | 90 / 92 / 100 (0.77; 2 · 90 · 0; 0) | 0 / 0 / 100 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 198 / 198 / 200 (0.82; 83 · 115 · 0; 0) | 158 / 158 / 200 (0.85; 5 · 153 · 0; 0) | 0 / 0 / 200 (-; 0 · 0 · 0; 0) |
| both sides cut | 50 / 50 / 50 (0.88; 10 · 40 · 0; 0) | 48 / 48 / 50 (0.91; 1 · 47 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| hidden from above | 47 / 47 / 50 (0.88; 2 · 44 · 1; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 47 / 47 / 50 (0.89; 1 · 46 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| a post across the middle | 49 / 49 / 50 (0.90; 1 · 48 · 0; 0) | 33 / 33 / 50 (0.89; 1 · 32 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 99 / 99 / 100 (0.83; 26 · 73 · 0; 0); front 94 / 100 | 88 / 89 / 100 (0.85; 4 · 82 · 3; 0); front 95 / 100 | 17 / 18 / 100 (0.85; 1 · 16 · 1; 0); front 94 / 100 |
| a barrel of the OTHER color, beside it and lower | 97 / 97 / 100 (0.85; 17 · 80 · 0; 0); front 90 / 100 | 91 / 91 / 100 (0.86; 4 · 86 · 1; 0); front 90 / 100 | 46 / 49 / 100 (0.87; 2 · 44 · 3; 0); front 90 / 100 |
| a barrel of the OTHER color, straight in front | 40 / 42 / 47 (0.87; 2 · 39 · 1; 0); front 32 / 47 | 37 / 38 / 48 (0.88; 0 · 38 · 0; 1); front 39 / 48 | 19 / 31 / 49 (0.83; 1 · 25 · 5; 0); front 42 / 49 |
| a barrel of the SAME color, beside it | 95 / 98 / 100 (0.83; 19 · 77 · 2; 0); front 92 / 100 | 87 / 96 / 100 (0.80; 17 · 72 · 7; 0); front 90 / 100 | 16 / 30 / 100 (0.72; 0 · 1 · 29; 0); front 79 / 100 |
| a barrel of the SAME color, beside it and lower | 91 / 99 / 100 (0.83; 25 · 71 · 3; 0); front 91 / 100 | 85 / 92 / 100 (0.84; 5 · 82 · 5; 0); front 87 / 100 | 21 / 21 / 100 (0.86; 0 · 21 · 0; 0); front 89 / 100 |
| a barrel of the SAME color, straight in front | 42 / 43 / 47 (0.88; 2 · 41 · 0; 0); front 34 / 47 | 28 / 33 / 48 (0.86; 1 · 29 · 3; 0); front 38 / 48 | 8 / 13 / 49 (0.80; 2 · 11 · 0; 0); front 42 / 49 |
| a plain block of the barrel's body color | 97 / 97 / 100 (0.87; 1 · 96 · 0; 1) | 74 / 74 / 100 (0.87; 2 · 70 · 2; 0) | 2 / 2 / 100 (0.76; 0 · 0 · 2; 0) |
| a plain block of the barrel's stripe color | 99 / 99 / 100 (0.86; 9 · 90 · 0; 2) | 91 / 91 / 100 (0.86; 8 · 83 · 0; 2) | 0 / 0 / 100 (-; 0 · 0 · 0; 2) |

## `combined+verify`, HOME hand masks

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 24 / 24 / 24 (0.97; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.96; 1 · 23 · 0; 0) | 18 / 18 / 24 (0.93; 1 · 17 · 0; 0) |
| a straight upright edge, one side | 24 / 24 / 24 (0.89; 0 · 24 · 0; 0) | 23 / 23 / 24 (0.84; 0 · 23 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 48 / 48 / 48 (0.86; 16 · 32 · 0; 0) | 45 / 45 / 48 (0.89; 0 · 45 · 0; 0) | 0 / 0 / 48 (-; 0 · 0 · 0; 0) |
| both sides cut | 12 / 12 / 12 (0.91; 2 · 10 · 0; 0) | 12 / 12 / 12 (0.94; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from above | 12 / 12 / 12 (0.91; 1 · 10 · 1; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 12 / 12 / 12 (0.93; 1 · 11 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a post across the middle | 12 / 12 / 12 (0.95; 1 · 11 · 0; 0) | 12 / 12 / 12 (0.94; 1 · 11 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 23 / 23 / 24 (0.90; 2 · 21 · 0; 0); front 24 / 24 | 22 / 22 / 24 (0.90; 0 · 22 · 0; 0); front 24 / 24 | 6 / 6 / 24 (0.90; 0 · 5 · 1; 0); front 24 / 24 |
| a barrel of the OTHER color, beside it and lower | 24 / 24 / 24 (0.91; 1 · 23 · 0; 0); front 20 / 24 | 23 / 23 / 24 (0.91; 0 · 23 · 0; 0); front 20 / 24 | 18 / 19 / 24 (0.91; 0 · 18 · 1; 0); front 20 / 24 |
| a barrel of the OTHER color, straight in front | 11 / 11 / 12 (0.93; 0 · 11 · 0; 0); front 8 / 12 | 10 / 10 / 12 (0.95; 0 · 10 · 0; 0); front 9 / 12 | 9 / 10 / 12 (0.87; 0 · 10 · 0; 0); front 11 / 12 |
| a barrel of the SAME color, beside it | 21 / 24 / 24 (0.85; 3 · 21 · 0; 0); front 24 / 24 | 16 / 24 / 24 (0.83; 2 · 20 · 2; 0); front 24 / 24 | 1 / 10 / 24 (0.73; 0 · 0 · 10; 0); front 23 / 24 |
| a barrel of the SAME color, beside it and lower | 20 / 24 / 24 (0.87; 6 · 18 · 0; 0); front 23 / 24 | 19 / 22 / 24 (0.85; 2 · 17 · 3; 0); front 22 / 24 | 7 / 7 / 24 (0.89; 0 · 7 · 0; 0); front 21 / 24 |
| a barrel of the SAME color, straight in front | 12 / 12 / 12 (0.92; 1 · 11 · 0; 0); front 9 / 12 | 10 / 10 / 12 (0.95; 0 · 10 · 0; 0); front 10 / 12 | 4 / 4 / 12 (0.85; 0 · 4 · 0; 0); front 11 / 12 |
| a plain block of the barrel's body color | 24 / 24 / 24 (0.92; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.92; 0 · 24 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a plain block of the barrel's stripe color | 24 / 24 / 24 (0.90; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.90; 1 · 23 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |

## `combined+verify`, HOME color model

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 24 / 24 / 24 (0.90; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.87; 1 · 22 · 1; 0) | 8 / 8 / 24 (0.84; 1 · 6 · 1; 0) |
| a straight upright edge, one side | 24 / 24 / 24 (0.83; 3 · 21 · 0; 0) | 22 / 23 / 24 (0.78; 0 · 23 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 48 / 48 / 48 (0.81; 20 · 28 · 0; 0) | 39 / 39 / 48 (0.86; 0 · 39 · 0; 0) | 0 / 0 / 48 (-; 0 · 0 · 0; 0) |
| both sides cut | 12 / 12 / 12 (0.88; 2 · 10 · 0; 0) | 12 / 12 / 12 (0.90; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from above | 11 / 11 / 12 (0.88; 0 · 11 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 12 / 12 / 12 (0.89; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a post across the middle | 12 / 12 / 12 (0.89; 0 · 12 · 0; 0) | 8 / 8 / 12 (0.88; 0 · 8 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 24 / 24 / 24 (0.81; 7 · 17 · 0; 0); front 24 / 24 | 21 / 22 / 24 (0.82; 0 · 20 · 2; 0); front 24 / 24 | 4 / 4 / 24 (0.83; 0 · 4 · 0; 0); front 24 / 24 |
| a barrel of the OTHER color, beside it and lower | 23 / 23 / 24 (0.82; 6 · 17 · 0; 0); front 24 / 24 | 21 / 21 / 24 (0.85; 1 · 20 · 0; 0); front 24 / 24 | 8 / 8 / 24 (0.87; 0 · 8 · 0; 0); front 24 / 24 |
| a barrel of the OTHER color, straight in front | 10 / 11 / 12 (0.85; 0 · 11 · 0; 0); front 9 / 12 | 9 / 9 / 12 (0.86; 0 · 9 · 0; 1); front 10 / 12 | 2 / 4 / 12 (0.82; 0 · 4 · 0; 0); front 11 / 12 |
| a barrel of the SAME color, beside it | 24 / 24 / 24 (0.81; 5 · 19 · 0; 0); front 24 / 24 | 22 / 23 / 24 (0.80; 4 · 18 · 1; 0); front 24 / 24 | 5 / 8 / 24 (0.73; 0 · 0 · 8; 0); front 20 / 24 |
| a barrel of the SAME color, beside it and lower | 22 / 24 / 24 (0.84; 3 · 20 · 1; 0); front 22 / 24 | 22 / 24 / 24 (0.82; 1 · 22 · 1; 0); front 22 / 24 | 5 / 5 / 24 (0.85; 0 · 5 · 0; 0); front 22 / 24 |
| a barrel of the SAME color, straight in front | 9 / 10 / 12 (0.88; 0 · 10 · 0; 0); front 8 / 12 | 4 / 5 / 12 (0.84; 0 · 5 · 0; 0); front 9 / 12 | 0 / 2 / 12 (0.74; 1 · 1 · 0; 0); front 10 / 12 |
| a plain block of the barrel's body color | 24 / 24 / 24 (0.86; 0 · 24 · 0; 0) | 21 / 21 / 24 (0.86; 0 · 21 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a plain block of the barrel's stripe color | 24 / 24 / 24 (0.84; 1 · 23 · 0; 0) | 23 / 23 / 24 (0.84; 1 · 22 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |

## `combined+verify`, CAMPUS color model

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 52 / 52 / 52 (0.91; 0 · 52 · 0; 0) | 50 / 50 / 52 (0.88; 1 · 48 · 1; 0) | 6 / 6 / 52 (0.82; 1 · 4 · 1; 0) |
| a straight upright edge, one side | 51 / 51 / 52 (0.80; 9 · 42 · 0; 0) | 45 / 46 / 52 (0.73; 2 · 44 · 0; 0) | 0 / 0 / 52 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 102 / 102 / 104 (0.80; 47 · 55 · 0; 0) | 74 / 74 / 104 (0.81; 5 · 69 · 0; 0) | 0 / 0 / 104 (-; 0 · 0 · 0; 0) |
| both sides cut | 26 / 26 / 26 (0.86; 6 · 20 · 0; 0) | 24 / 24 / 26 (0.90; 1 · 23 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| hidden from above | 24 / 24 / 26 (0.86; 1 · 23 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 23 / 23 / 26 (0.88; 0 · 23 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| a post across the middle | 25 / 25 / 26 (0.88; 0 · 25 · 0; 0) | 13 / 13 / 26 (0.86; 0 · 13 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 52 / 52 / 52 (0.81; 17 · 35 · 0; 0); front 46 / 52 | 45 / 45 / 52 (0.83; 4 · 40 · 1; 0); front 47 / 52 | 7 / 8 / 52 (0.81; 1 · 7 · 0; 0); front 46 / 52 |
| a barrel of the OTHER color, beside it and lower | 50 / 50 / 52 (0.84; 10 · 40 · 0; 0); front 46 / 52 | 47 / 47 / 52 (0.84; 3 · 43 · 1; 0); front 46 / 52 | 20 / 22 / 52 (0.83; 2 · 18 · 2; 0); front 46 / 52 |
| a barrel of the OTHER color, straight in front | 19 / 20 / 23 (0.84; 2 · 17 · 1; 0); front 15 / 23 | 18 / 19 / 24 (0.84; 0 · 19 · 0; 0); front 20 / 24 | 8 / 17 / 25 (0.80; 1 · 11 · 5; 0); front 20 / 25 |
| a barrel of the SAME color, beside it | 50 / 50 / 52 (0.82; 11 · 37 · 2; 0); front 44 / 52 | 49 / 49 / 52 (0.78; 11 · 34 · 4; 0); front 42 / 52 | 10 / 12 / 52 (0.70; 0 · 1 · 11; 0); front 36 / 52 |
| a barrel of the SAME color, beside it and lower | 49 / 51 / 52 (0.81; 16 · 33 · 2; 0); front 46 / 52 | 44 / 46 / 52 (0.83; 2 · 43 · 1; 0); front 43 / 52 | 9 / 9 / 52 (0.84; 0 · 9 · 0; 0); front 46 / 52 |
| a barrel of the SAME color, straight in front | 21 / 21 / 23 (0.85; 1 · 20 · 0; 0); front 17 / 23 | 14 / 18 / 24 (0.83; 1 · 14 · 3; 0); front 19 / 24 | 4 / 7 / 25 (0.78; 1 · 6 · 0; 0); front 21 / 25 |
| a plain block of the barrel's body color | 49 / 49 / 52 (0.85; 1 · 48 · 0; 1) | 29 / 29 / 52 (0.84; 2 · 25 · 2; 0) | 2 / 2 / 52 (0.76; 0 · 0 · 2; 0) |
| a plain block of the barrel's stripe color | 51 / 51 / 52 (0.84; 7 · 44 · 0; 2) | 44 / 44 / 52 (0.84; 6 · 38 · 0; 2) | 0 / 0 / 52 (-; 0 · 0 · 0; 2) |

### `combined+verify`: why the hidden barrel was not found under the v2 rule (all pools)

- cut by the frame edge, 50 %: stripe_not_sandwiched 1, stripe_refused:side_unexplained 1
- cut by the frame edge, 75 %: stripe_refused:width 65, stripe_refused:height 2, stripe_not_sandwiched 1
- a straight upright edge, one side, 25 %: stripe_not_sandwiched 1
- a straight upright edge, one side, 50 %: stripe_refused:side_unexplained 6, misplaced 2, stripe_not_sandwiched 1, stripe_refused:width 1
- a straight upright edge, one side, 75 %: stripe_refused:width 94, stripe_not_sandwiched 3, stripe_refused:height 2, stripe_refused:side_unexplained 1
- a slanted edge, one side, 25 %: stripe_not_sandwiched 2
- a slanted edge, one side, 50 %: stripe_refused:side_unexplained 28, stripe_not_sandwiched 13, stripe_refused:width 1
- a slanted edge, one side, 75 %: stripe_refused:width 178, stripe_refused:area 15, stripe_refused:height 4, stripe_refused:side_unexplained 1, stripe_hidden 1, stripe_not_sandwiched 1
- both sides cut, 50 %: stripe_not_sandwiched 2
- both sides cut, 75 %: stripe_refused:width 34, stripe_refused:side_unexplained 15, stripe_not_sandwiched 1
- hidden from above, 25 %: stripe_not_sandwiched 3
- hidden from above, 50 %: stripe_not_sandwiched 49, stripe_refused:width 1
- hidden from above, 75 %: stripe_hidden 49, stripe_refused:width 1
- hidden from below (a low thing in front), 25 %: stripe_not_sandwiched 2, stripe_refused:side_unexplained 1
- hidden from below (a low thing in front), 50 %: stripe_not_sandwiched 49, stripe_hidden 1
- hidden from below (a low thing in front), 75 %: stripe_hidden 50
- a post across the middle, 25 %: stripe_refused:width 1
- a post across the middle, 50 %: stripe_refused:width 11, stripe_not_sandwiched 4, stripe_refused:side_unexplained 1, stripe_refused:height 1
- a post across the middle, 75 %: stripe_refused:width 36, stripe_refused:area 13, stripe_hidden 1
- a barrel of the OTHER color, beside it, 25 %: stripe_refused:height 1
- a barrel of the OTHER color, beside it, 50 %: stripe_refused:height 5, stripe_not_sandwiched 2, stripe_refused:area 2, stripe_refused:side_unexplained 1, misplaced 1, stripe_refused:width 1
- a barrel of the OTHER color, beside it, 75 %: stripe_refused:height 54, stripe_refused:width 18, stripe_refused:area 8, stripe_not_sandwiched 1, stripe_refused:side_unexplained 1, misplaced 1
- a barrel of the OTHER color, beside it and lower, 25 %: stripe_refused:height 2, stripe_not_sandwiched 1
- a barrel of the OTHER color, beside it and lower, 50 %: stripe_refused:height 6, stripe_refused:width 2, stripe_not_sandwiched 1
- a barrel of the OTHER color, beside it and lower, 75 %: stripe_refused:height 33, stripe_refused:width 11, stripe_refused:area 4, misplaced 3, stripe_not_sandwiched 3
- a barrel of the OTHER color, straight in front, 25 %: stripe_refused:height 3, misplaced 2, stripe_not_sandwiched 2
- a barrel of the OTHER color, straight in front, 50 %: stripe_refused:height 8, misplaced 1, stripe_refused:body_min 1, stripe_refused:width 1
- a barrel of the OTHER color, straight in front, 75 %: stripe_refused:height 14, misplaced 12, stripe_not_sandwiched 3, stripe_refused:top_against_barrel 1
- a barrel of the SAME color, beside it, 25 %: misplaced 4, stripe_refused:height 1
- a barrel of the SAME color, beside it, 50 %: misplaced 13
- a barrel of the SAME color, beside it, 75 %: misplaced 82, stripe_refused:width 1, stripe_refused:area 1
- a barrel of the SAME color, beside it and lower, 25 %: misplaced 8, stripe_refused:height 1
- a barrel of the SAME color, beside it and lower, 50 %: misplaced 13, stripe_refused:height 2
- a barrel of the SAME color, beside it and lower, 75 %: misplaced 77, stripe_not_sandwiched 2
- a barrel of the SAME color, straight in front, 25 %: misplaced 2, stripe_hidden 2, stripe_refused:height 1
- a barrel of the SAME color, straight in front, 50 %: misplaced 20
- a barrel of the SAME color, straight in front, 75 %: misplaced 41
- a plain block of the barrel's body color, 25 %: stripe_not_sandwiched 3
- a plain block of the barrel's body color, 50 %: stripe_not_sandwiched 25, stripe_refused:side_unexplained 1
- a plain block of the barrel's body color, 75 %: stripe_refused:width 93, stripe_not_sandwiched 3, stripe_refused:height 2
- a plain block of the barrel's stripe color, 25 %: stripe_not_sandwiched 1
- a plain block of the barrel's stripe color, 50 %: stripe_not_sandwiched 8, stripe_refused:width 1
- a plain block of the barrel's stripe color, 75 %: stripe_refused:width 95, stripe_not_sandwiched 4, stripe_refused:height 1

## `combined+verify2`, all three pools

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 / 100 / 100 (0.92; 1 · 99 · 0; 0) | 98 / 98 / 100 (0.90; 3 · 93 · 2; 0) | 32 / 32 / 100 (0.89; 3 · 27 · 2; 0) |
| a straight upright edge, one side | 99 / 99 / 100 (0.83; 12 · 87 · 0; 0) | 90 / 92 / 100 (0.77; 2 · 90 · 0; 0) | 0 / 0 / 100 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 198 / 198 / 200 (0.82; 83 · 115 · 0; 0) | 158 / 158 / 200 (0.85; 5 · 153 · 0; 0) | 0 / 0 / 200 (-; 0 · 0 · 0; 0) |
| both sides cut | 50 / 50 / 50 (0.88; 10 · 40 · 0; 0) | 48 / 48 / 50 (0.91; 1 · 47 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| hidden from above | 47 / 47 / 50 (0.88; 2 · 44 · 1; 0) | 43 / 43 / 50 (0.88; 0 · 42 · 1; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 47 / 47 / 50 (0.89; 1 · 46 · 0; 0) | 39 / 39 / 50 (0.90; 0 · 39 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| a post across the middle | 49 / 49 / 50 (0.90; 1 · 48 · 0; 0) | 33 / 33 / 50 (0.89; 1 · 32 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 99 / 99 / 100 (0.83; 26 · 73 · 0; 0); front 94 / 100 | 88 / 89 / 100 (0.85; 4 · 82 · 3; 0); front 95 / 100 | 17 / 18 / 100 (0.85; 1 · 16 · 1; 0); front 94 / 100 |
| a barrel of the OTHER color, beside it and lower | 97 / 97 / 100 (0.85; 17 · 80 · 0; 0); front 90 / 100 | 91 / 91 / 100 (0.86; 4 · 86 · 1; 0); front 90 / 100 | 46 / 49 / 100 (0.87; 2 · 44 · 3; 0); front 90 / 100 |
| a barrel of the OTHER color, straight in front | 40 / 42 / 47 (0.87; 2 · 39 · 1; 0); front 32 / 47 | 37 / 38 / 48 (0.88; 0 · 38 · 0; 1); front 39 / 48 | 19 / 31 / 49 (0.83; 1 · 25 · 5; 0); front 42 / 49 |
| a barrel of the SAME color, beside it | 95 / 98 / 100 (0.83; 19 · 77 · 2; 0); front 92 / 100 | 87 / 96 / 100 (0.80; 17 · 72 · 7; 0); front 90 / 100 | 16 / 30 / 100 (0.72; 0 · 1 · 29; 0); front 79 / 100 |
| a barrel of the SAME color, beside it and lower | 91 / 99 / 100 (0.83; 25 · 71 · 3; 0); front 91 / 100 | 85 / 92 / 100 (0.84; 5 · 82 · 5; 0); front 87 / 100 | 21 / 21 / 100 (0.86; 0 · 21 · 0; 0); front 89 / 100 |
| a barrel of the SAME color, straight in front | 42 / 43 / 47 (0.88; 2 · 41 · 0; 0); front 34 / 47 | 28 / 33 / 48 (0.86; 1 · 29 · 3; 0); front 38 / 48 | 8 / 13 / 49 (0.80; 2 · 11 · 0; 0); front 42 / 49 |
| a plain block of the barrel's body color | 97 / 97 / 100 (0.87; 1 · 96 · 0; 1) | 74 / 74 / 100 (0.87; 2 · 70 · 2; 0) | 2 / 2 / 100 (0.76; 0 · 0 · 2; 0) |
| a plain block of the barrel's stripe color | 99 / 99 / 100 (0.86; 9 · 90 · 0; 2) | 91 / 91 / 100 (0.86; 8 · 83 · 0; 2) | 0 / 0 / 100 (-; 0 · 0 · 0; 2) |

## `combined+verify2`, HOME hand masks

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 24 / 24 / 24 (0.97; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.96; 1 · 23 · 0; 0) | 18 / 18 / 24 (0.93; 1 · 17 · 0; 0) |
| a straight upright edge, one side | 24 / 24 / 24 (0.89; 0 · 24 · 0; 0) | 23 / 23 / 24 (0.84; 0 · 23 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 48 / 48 / 48 (0.86; 16 · 32 · 0; 0) | 45 / 45 / 48 (0.89; 0 · 45 · 0; 0) | 0 / 0 / 48 (-; 0 · 0 · 0; 0) |
| both sides cut | 12 / 12 / 12 (0.91; 2 · 10 · 0; 0) | 12 / 12 / 12 (0.94; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from above | 12 / 12 / 12 (0.91; 1 · 10 · 1; 0) | 12 / 12 / 12 (0.92; 0 · 11 · 1; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 12 / 12 / 12 (0.93; 1 · 11 · 0; 0) | 11 / 11 / 12 (0.95; 0 · 11 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a post across the middle | 12 / 12 / 12 (0.95; 1 · 11 · 0; 0) | 12 / 12 / 12 (0.94; 1 · 11 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 23 / 23 / 24 (0.90; 2 · 21 · 0; 0); front 24 / 24 | 22 / 22 / 24 (0.90; 0 · 22 · 0; 0); front 24 / 24 | 6 / 6 / 24 (0.90; 0 · 5 · 1; 0); front 24 / 24 |
| a barrel of the OTHER color, beside it and lower | 24 / 24 / 24 (0.91; 1 · 23 · 0; 0); front 20 / 24 | 23 / 23 / 24 (0.91; 0 · 23 · 0; 0); front 20 / 24 | 18 / 19 / 24 (0.91; 0 · 18 · 1; 0); front 20 / 24 |
| a barrel of the OTHER color, straight in front | 11 / 11 / 12 (0.93; 0 · 11 · 0; 0); front 8 / 12 | 10 / 10 / 12 (0.95; 0 · 10 · 0; 0); front 9 / 12 | 9 / 10 / 12 (0.87; 0 · 10 · 0; 0); front 11 / 12 |
| a barrel of the SAME color, beside it | 21 / 24 / 24 (0.85; 3 · 21 · 0; 0); front 24 / 24 | 16 / 24 / 24 (0.83; 2 · 20 · 2; 0); front 24 / 24 | 1 / 10 / 24 (0.73; 0 · 0 · 10; 0); front 23 / 24 |
| a barrel of the SAME color, beside it and lower | 20 / 24 / 24 (0.87; 6 · 18 · 0; 0); front 23 / 24 | 19 / 22 / 24 (0.85; 2 · 17 · 3; 0); front 22 / 24 | 7 / 7 / 24 (0.89; 0 · 7 · 0; 0); front 21 / 24 |
| a barrel of the SAME color, straight in front | 12 / 12 / 12 (0.92; 1 · 11 · 0; 0); front 9 / 12 | 10 / 10 / 12 (0.95; 0 · 10 · 0; 0); front 10 / 12 | 4 / 4 / 12 (0.85; 0 · 4 · 0; 0); front 11 / 12 |
| a plain block of the barrel's body color | 24 / 24 / 24 (0.92; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.92; 0 · 24 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a plain block of the barrel's stripe color | 24 / 24 / 24 (0.90; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.90; 1 · 23 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |

## `combined+verify2`, HOME color model

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 24 / 24 / 24 (0.90; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.87; 1 · 22 · 1; 0) | 8 / 8 / 24 (0.84; 1 · 6 · 1; 0) |
| a straight upright edge, one side | 24 / 24 / 24 (0.83; 3 · 21 · 0; 0) | 22 / 23 / 24 (0.78; 0 · 23 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 48 / 48 / 48 (0.81; 20 · 28 · 0; 0) | 39 / 39 / 48 (0.86; 0 · 39 · 0; 0) | 0 / 0 / 48 (-; 0 · 0 · 0; 0) |
| both sides cut | 12 / 12 / 12 (0.88; 2 · 10 · 0; 0) | 12 / 12 / 12 (0.90; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from above | 11 / 11 / 12 (0.88; 0 · 11 · 0; 0) | 10 / 10 / 12 (0.90; 0 · 10 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 12 / 12 / 12 (0.89; 0 · 12 · 0; 0) | 8 / 8 / 12 (0.90; 0 · 8 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a post across the middle | 12 / 12 / 12 (0.89; 0 · 12 · 0; 0) | 8 / 8 / 12 (0.88; 0 · 8 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 24 / 24 / 24 (0.81; 7 · 17 · 0; 0); front 24 / 24 | 21 / 22 / 24 (0.82; 0 · 20 · 2; 0); front 24 / 24 | 4 / 4 / 24 (0.83; 0 · 4 · 0; 0); front 24 / 24 |
| a barrel of the OTHER color, beside it and lower | 23 / 23 / 24 (0.82; 6 · 17 · 0; 0); front 24 / 24 | 21 / 21 / 24 (0.85; 1 · 20 · 0; 0); front 24 / 24 | 8 / 8 / 24 (0.87; 0 · 8 · 0; 0); front 24 / 24 |
| a barrel of the OTHER color, straight in front | 10 / 11 / 12 (0.85; 0 · 11 · 0; 0); front 9 / 12 | 9 / 9 / 12 (0.86; 0 · 9 · 0; 1); front 10 / 12 | 2 / 4 / 12 (0.82; 0 · 4 · 0; 0); front 11 / 12 |
| a barrel of the SAME color, beside it | 24 / 24 / 24 (0.81; 5 · 19 · 0; 0); front 24 / 24 | 22 / 23 / 24 (0.80; 4 · 18 · 1; 0); front 24 / 24 | 5 / 8 / 24 (0.73; 0 · 0 · 8; 0); front 20 / 24 |
| a barrel of the SAME color, beside it and lower | 22 / 24 / 24 (0.84; 3 · 20 · 1; 0); front 22 / 24 | 22 / 24 / 24 (0.82; 1 · 22 · 1; 0); front 22 / 24 | 5 / 5 / 24 (0.85; 0 · 5 · 0; 0); front 22 / 24 |
| a barrel of the SAME color, straight in front | 9 / 10 / 12 (0.88; 0 · 10 · 0; 0); front 8 / 12 | 4 / 5 / 12 (0.84; 0 · 5 · 0; 0); front 9 / 12 | 0 / 2 / 12 (0.74; 1 · 1 · 0; 0); front 10 / 12 |
| a plain block of the barrel's body color | 24 / 24 / 24 (0.86; 0 · 24 · 0; 0) | 21 / 21 / 24 (0.86; 0 · 21 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a plain block of the barrel's stripe color | 24 / 24 / 24 (0.84; 1 · 23 · 0; 0) | 23 / 23 / 24 (0.84; 1 · 22 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |

## `combined+verify2`, CAMPUS color model

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 52 / 52 / 52 (0.91; 0 · 52 · 0; 0) | 50 / 50 / 52 (0.88; 1 · 48 · 1; 0) | 6 / 6 / 52 (0.82; 1 · 4 · 1; 0) |
| a straight upright edge, one side | 51 / 51 / 52 (0.80; 9 · 42 · 0; 0) | 45 / 46 / 52 (0.73; 2 · 44 · 0; 0) | 0 / 0 / 52 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 102 / 102 / 104 (0.80; 47 · 55 · 0; 0) | 74 / 74 / 104 (0.81; 5 · 69 · 0; 0) | 0 / 0 / 104 (-; 0 · 0 · 0; 0) |
| both sides cut | 26 / 26 / 26 (0.86; 6 · 20 · 0; 0) | 24 / 24 / 26 (0.90; 1 · 23 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| hidden from above | 24 / 24 / 26 (0.86; 1 · 23 · 0; 0) | 21 / 21 / 26 (0.85; 0 · 21 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 23 / 23 / 26 (0.88; 0 · 23 · 0; 0) | 20 / 20 / 26 (0.87; 0 · 20 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| a post across the middle | 25 / 25 / 26 (0.88; 0 · 25 · 0; 0) | 13 / 13 / 26 (0.86; 0 · 13 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 52 / 52 / 52 (0.81; 17 · 35 · 0; 0); front 46 / 52 | 45 / 45 / 52 (0.83; 4 · 40 · 1; 0); front 47 / 52 | 7 / 8 / 52 (0.81; 1 · 7 · 0; 0); front 46 / 52 |
| a barrel of the OTHER color, beside it and lower | 50 / 50 / 52 (0.84; 10 · 40 · 0; 0); front 46 / 52 | 47 / 47 / 52 (0.84; 3 · 43 · 1; 0); front 46 / 52 | 20 / 22 / 52 (0.83; 2 · 18 · 2; 0); front 46 / 52 |
| a barrel of the OTHER color, straight in front | 19 / 20 / 23 (0.84; 2 · 17 · 1; 0); front 15 / 23 | 18 / 19 / 24 (0.84; 0 · 19 · 0; 0); front 20 / 24 | 8 / 17 / 25 (0.80; 1 · 11 · 5; 0); front 20 / 25 |
| a barrel of the SAME color, beside it | 50 / 50 / 52 (0.82; 11 · 37 · 2; 0); front 44 / 52 | 49 / 49 / 52 (0.78; 11 · 34 · 4; 0); front 42 / 52 | 10 / 12 / 52 (0.70; 0 · 1 · 11; 0); front 36 / 52 |
| a barrel of the SAME color, beside it and lower | 49 / 51 / 52 (0.81; 16 · 33 · 2; 0); front 46 / 52 | 44 / 46 / 52 (0.83; 2 · 43 · 1; 0); front 43 / 52 | 9 / 9 / 52 (0.84; 0 · 9 · 0; 0); front 46 / 52 |
| a barrel of the SAME color, straight in front | 21 / 21 / 23 (0.85; 1 · 20 · 0; 0); front 17 / 23 | 14 / 18 / 24 (0.83; 1 · 14 · 3; 0); front 19 / 24 | 4 / 7 / 25 (0.78; 1 · 6 · 0; 0); front 21 / 25 |
| a plain block of the barrel's body color | 49 / 49 / 52 (0.85; 1 · 48 · 0; 1) | 29 / 29 / 52 (0.84; 2 · 25 · 2; 0) | 2 / 2 / 52 (0.76; 0 · 0 · 2; 0) |
| a plain block of the barrel's stripe color | 51 / 51 / 52 (0.84; 7 · 44 · 0; 2) | 44 / 44 / 52 (0.84; 6 · 38 · 0; 2) | 0 / 0 / 52 (-; 0 · 0 · 0; 2) |

### `combined+verify2`: why the hidden barrel was not found under the v2 rule (all pools)

- cut by the frame edge, 50 %: stripe_not_sandwiched 1, stripe_refused:side_unexplained 1
- cut by the frame edge, 75 %: stripe_refused:width 65, stripe_refused:height 2, stripe_not_sandwiched 1
- a straight upright edge, one side, 25 %: stripe_not_sandwiched 1
- a straight upright edge, one side, 50 %: stripe_refused:side_unexplained 6, misplaced 2, stripe_not_sandwiched 1, stripe_refused:width 1
- a straight upright edge, one side, 75 %: stripe_refused:width 94, stripe_not_sandwiched 3, stripe_refused:height 2, stripe_refused:side_unexplained 1
- a slanted edge, one side, 25 %: stripe_not_sandwiched 2
- a slanted edge, one side, 50 %: stripe_refused:side_unexplained 28, stripe_not_sandwiched 13, stripe_refused:width 1
- a slanted edge, one side, 75 %: stripe_refused:width 178, stripe_refused:area 15, stripe_refused:height 4, stripe_refused:side_unexplained 1, stripe_hidden 1, stripe_not_sandwiched 1
- both sides cut, 50 %: stripe_not_sandwiched 2
- both sides cut, 75 %: stripe_refused:width 34, stripe_refused:side_unexplained 15, stripe_not_sandwiched 1
- hidden from above, 25 %: stripe_not_sandwiched 3
- hidden from above, 50 %: stripe_not_sandwiched 6, stripe_refused:width 1
- hidden from above, 75 %: stripe_hidden 49, stripe_refused:width 1
- hidden from below (a low thing in front), 25 %: stripe_not_sandwiched 2, stripe_refused:side_unexplained 1
- hidden from below (a low thing in front), 50 %: stripe_not_sandwiched 10, stripe_hidden 1
- hidden from below (a low thing in front), 75 %: stripe_hidden 50
- a post across the middle, 25 %: stripe_refused:width 1
- a post across the middle, 50 %: stripe_refused:width 11, stripe_not_sandwiched 4, stripe_refused:side_unexplained 1, stripe_refused:height 1
- a post across the middle, 75 %: stripe_refused:width 36, stripe_refused:area 13, stripe_hidden 1
- a barrel of the OTHER color, beside it, 25 %: stripe_refused:height 1
- a barrel of the OTHER color, beside it, 50 %: stripe_refused:height 5, stripe_not_sandwiched 2, stripe_refused:area 2, stripe_refused:side_unexplained 1, misplaced 1, stripe_refused:width 1
- a barrel of the OTHER color, beside it, 75 %: stripe_refused:height 54, stripe_refused:width 18, stripe_refused:area 8, stripe_not_sandwiched 1, stripe_refused:side_unexplained 1, misplaced 1
- a barrel of the OTHER color, beside it and lower, 25 %: stripe_refused:height 2, stripe_not_sandwiched 1
- a barrel of the OTHER color, beside it and lower, 50 %: stripe_refused:height 6, stripe_refused:width 2, stripe_not_sandwiched 1
- a barrel of the OTHER color, beside it and lower, 75 %: stripe_refused:height 33, stripe_refused:width 11, stripe_refused:area 4, misplaced 3, stripe_not_sandwiched 3
- a barrel of the OTHER color, straight in front, 25 %: stripe_refused:height 3, misplaced 2, stripe_not_sandwiched 2
- a barrel of the OTHER color, straight in front, 50 %: stripe_refused:height 8, misplaced 1, stripe_refused:body_min 1, stripe_refused:width 1
- a barrel of the OTHER color, straight in front, 75 %: stripe_refused:height 14, misplaced 12, stripe_not_sandwiched 3, stripe_refused:top_against_barrel 1
- a barrel of the SAME color, beside it, 25 %: misplaced 4, stripe_refused:height 1
- a barrel of the SAME color, beside it, 50 %: misplaced 13
- a barrel of the SAME color, beside it, 75 %: misplaced 82, stripe_refused:width 1, stripe_refused:area 1
- a barrel of the SAME color, beside it and lower, 25 %: misplaced 8, stripe_refused:height 1
- a barrel of the SAME color, beside it and lower, 50 %: misplaced 13, stripe_refused:height 2
- a barrel of the SAME color, beside it and lower, 75 %: misplaced 77, stripe_not_sandwiched 2
- a barrel of the SAME color, straight in front, 25 %: misplaced 2, stripe_hidden 2, stripe_refused:height 1
- a barrel of the SAME color, straight in front, 50 %: misplaced 20
- a barrel of the SAME color, straight in front, 75 %: misplaced 41
- a plain block of the barrel's body color, 25 %: stripe_not_sandwiched 3
- a plain block of the barrel's body color, 50 %: stripe_not_sandwiched 25, stripe_refused:side_unexplained 1
- a plain block of the barrel's body color, 75 %: stripe_refused:width 93, stripe_not_sandwiched 3, stripe_refused:height 2
- a plain block of the barrel's stripe color, 25 %: stripe_not_sandwiched 1
- a plain block of the barrel's stripe color, 50 %: stripe_not_sandwiched 8, stripe_refused:width 1
- a plain block of the barrel's stripe color, 75 %: stripe_refused:width 95, stripe_not_sandwiched 4, stripe_refused:height 1

