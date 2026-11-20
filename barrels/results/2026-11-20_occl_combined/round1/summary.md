# The occlusion scorecard, in full

git 60681ad; camera AIM_4A8B6118_BOXFIT; train frames only. Source barrels: HOME hand masks 12, HOME color model 12, CAMPUS color model 26 (left out because `base` does not find them alone and unhidden: 0).

Each cell: found under the v2 rule / box in the right place / scenes; (mean overlap of the right-place boxes with the FULL box; too small · about right · too big; false boxes). `front` = the barrel pasted in front, found / pasted.

## `before`, all three pools

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 / 100 / 100 (0.87; 1 · 80 · 19; 0) | 86 / 86 / 100 (0.76; 8 · 32 · 46; 0) | 0 / 0 / 100 (-; 0 · 0 · 0; 0) |
| a straight upright edge, one side | 100 / 100 / 100 (0.67; 5 · 94 · 1; 0) | 38 / 62 / 100 (0.51; 4 · 58 · 0; 23) | 0 / 0 / 100 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 200 / 200 / 200 (0.80; 8 · 192 · 0; 0) | 116 / 116 / 200 (0.73; 8 · 108 · 0; 0) | 0 / 0 / 200 (-; 0 · 0 · 0; 0) |
| both sides cut | 50 / 50 / 50 (0.88; 9 · 41 · 0; 0) | 49 / 50 / 50 (0.90; 2 · 48 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| hidden from above | 50 / 50 / 50 (0.87; 2 · 47 · 1; 0) | 1 / 1 / 50 (0.93; 0 · 1 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 49 / 49 / 50 (0.89; 1 · 48 · 0; 0) | 1 / 1 / 50 (0.91; 0 · 1 · 0; 0) | 1 / 1 / 50 (0.53; 1 · 0 · 0; 0) |
| a post across the middle | 49 / 49 / 50 (0.90; 1 · 48 · 0; 0) | 9 / 9 / 50 (0.88; 0 · 9 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 99 / 99 / 100 (0.81; 13 · 86 · 0; 0); front 94 / 100 | 67 / 77 / 100 (0.76; 5 · 72 · 0; 6); front 95 / 100 | 44 / 55 / 100 (0.80; 9 · 44 · 2; 2); front 94 / 100 |
| a barrel of the OTHER color, beside it and lower | 93 / 98 / 100 (0.83; 9 · 88 · 1; 1); front 90 / 100 | 81 / 86 / 100 (0.83; 4 · 77 · 5; 2); front 90 / 100 | 69 / 89 / 100 (0.80; 12 · 67 · 10; 1); front 90 / 100 |
| a barrel of the OTHER color, straight in front | 29 / 41 / 47 (0.83; 9 · 32 · 0; 21); front 32 / 47 | 36 / 38 / 48 (0.87; 0 · 37 · 1; 3); front 39 / 48 | 17 / 28 / 49 (0.82; 1 · 22 · 5; 1); front 42 / 49 |
| a barrel of the SAME color, beside it | 80 / 88 / 100 (0.80; 14 · 69 · 5; 1); front 81 / 100 | 32 / 46 / 100 (0.62; 5 · 13 · 28; 1); front 77 / 100 | 15 / 30 / 100 (0.70; 1 · 2 · 27; 0); front 79 / 100 |
| a barrel of the SAME color, beside it and lower | 88 / 98 / 100 (0.77; 8 · 87 · 3; 0); front 91 / 100 | 60 / 68 / 100 (0.70; 4 · 61 · 3; 6); front 87 / 100 | 1 / 3 / 100 (0.69; 1 · 1 · 1; 0); front 89 / 100 |
| a barrel of the SAME color, straight in front | 45 / 45 / 47 (0.88; 1 · 44 · 0; 4); front 33 / 47 | 25 / 29 / 48 (0.85; 3 · 25 · 1; 6); front 38 / 48 | 1 / 3 / 49 (0.62; 2 · 1 · 0; 1); front 42 / 49 |
| a plain block of the barrel's body color | 100 / 100 / 100 (0.82; 1 · 99 · 0; 2) | 85 / 85 / 100 (0.73; 2 · 81 · 2; 0) | 2 / 2 / 100 (0.76; 0 · 0 · 2; 0) |
| a plain block of the barrel's stripe color | 100 / 100 / 100 (0.82; 1 · 99 · 0; 2) | 85 / 85 / 100 (0.73; 2 · 83 · 0; 2) | 0 / 1 / 100 (0.76; 0 · 1 · 0; 3) |

## `before`, HOME hand masks

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 24 / 24 / 24 (0.90; 0 · 17 · 7; 0) | 23 / 23 / 24 (0.76; 0 · 7 · 16; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a straight upright edge, one side | 24 / 24 / 24 (0.65; 0 · 24 · 0; 0) | 7 / 15 / 24 (0.47; 0 · 15 · 0; 8) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 48 / 48 / 48 (0.82; 0 · 48 · 0; 0) | 40 / 40 / 48 (0.72; 0 · 40 · 0; 0) | 0 / 0 / 48 (-; 0 · 0 · 0; 0) |
| both sides cut | 12 / 12 / 12 (0.91; 2 · 10 · 0; 0) | 12 / 12 / 12 (0.94; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from above | 12 / 12 / 12 (0.91; 1 · 10 · 1; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 12 / 12 / 12 (0.93; 1 · 11 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a post across the middle | 12 / 12 / 12 (0.95; 1 · 11 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 23 / 23 / 24 (0.86; 2 · 21 · 0; 0); front 24 / 24 | 22 / 24 / 24 (0.83; 0 · 24 · 0; 1); front 24 / 24 | 17 / 17 / 24 (0.89; 1 · 14 · 2; 0); front 24 / 24 |
| a barrel of the OTHER color, beside it and lower | 24 / 24 / 24 (0.92; 1 · 23 · 0; 0); front 20 / 24 | 23 / 23 / 24 (0.91; 0 · 23 · 0; 0); front 20 / 24 | 21 / 22 / 24 (0.91; 0 · 21 · 1; 0); front 20 / 24 |
| a barrel of the OTHER color, straight in front | 8 / 11 / 12 (0.89; 2 · 9 · 0; 4); front 8 / 12 | 10 / 10 / 12 (0.95; 0 · 10 · 0; 0); front 9 / 12 | 6 / 6 / 12 (0.88; 0 · 6 · 0; 0); front 11 / 12 |
| a barrel of the SAME color, beside it | 16 / 21 / 24 (0.82; 2 · 17 · 2; 0); front 21 / 24 | 1 / 9 / 24 (0.61; 0 · 0 · 9; 0); front 23 / 24 | 1 / 9 / 24 (0.72; 0 · 0 · 9; 0); front 23 / 24 |
| a barrel of the SAME color, beside it and lower | 20 / 23 / 24 (0.84; 2 · 21 · 0; 0); front 23 / 24 | 18 / 19 / 24 (0.73; 1 · 17 · 1; 0); front 22 / 24 | 0 / 0 / 24 (-; 0 · 0 · 0; 0); front 21 / 24 |
| a barrel of the SAME color, straight in front | 12 / 12 / 12 (0.92; 1 · 11 · 0; 0); front 9 / 12 | 9 / 10 / 12 (0.92; 1 · 9 · 0; 2); front 10 / 12 | 0 / 0 / 12 (-; 0 · 0 · 0; 0); front 11 / 12 |
| a plain block of the barrel's body color | 24 / 24 / 24 (0.84; 0 · 24 · 0; 0) | 23 / 23 / 24 (0.72; 0 · 23 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a plain block of the barrel's stripe color | 24 / 24 / 24 (0.84; 0 · 24 · 0; 0) | 23 / 23 / 24 (0.72; 0 · 23 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |

## `before`, HOME color model

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 24 / 24 / 24 (0.86; 0 · 17 · 7; 0) | 23 / 23 / 24 (0.75; 1 · 7 · 15; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a straight upright edge, one side | 24 / 24 / 24 (0.63; 1 · 23 · 0; 0) | 8 / 15 / 24 (0.48; 0 · 15 · 0; 7) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 48 / 48 / 48 (0.79; 0 · 48 · 0; 0) | 30 / 30 / 48 (0.73; 0 · 30 · 0; 0) | 0 / 0 / 48 (-; 0 · 0 · 0; 0) |
| both sides cut | 12 / 12 / 12 (0.88; 2 · 10 · 0; 0) | 12 / 12 / 12 (0.90; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from above | 12 / 12 / 12 (0.87; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 12 / 12 / 12 (0.89; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a post across the middle | 12 / 12 / 12 (0.89; 0 · 12 · 0; 0) | 4 / 4 / 12 (0.87; 0 · 4 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 24 / 24 / 24 (0.79; 2 · 22 · 0; 0); front 24 / 24 | 12 / 14 / 24 (0.74; 0 · 14 · 0; 4); front 24 / 24 | 7 / 11 / 24 (0.71; 3 · 8 · 0; 1); front 24 / 24 |
| a barrel of the OTHER color, beside it and lower | 18 / 23 / 24 (0.73; 1 · 22 · 0; 0); front 24 / 24 | 13 / 15 / 24 (0.79; 1 · 12 · 2; 1); front 24 / 24 | 10 / 21 / 24 (0.68; 3 · 15 · 3; 0); front 24 / 24 |
| a barrel of the OTHER color, straight in front | 6 / 10 / 12 (0.82; 3 · 7 · 0; 6); front 9 / 12 | 8 / 9 / 12 (0.81; 0 · 8 · 1; 1); front 10 / 12 | 4 / 6 / 12 (0.83; 0 · 6 · 0; 0); front 11 / 12 |
| a barrel of the SAME color, beside it | 21 / 21 / 24 (0.81; 4 · 17 · 0; 0); front 21 / 24 | 9 / 11 / 24 (0.60; 0 · 5 · 6; 1); front 19 / 24 | 4 / 9 / 24 (0.67; 1 · 1 · 7; 0); front 20 / 24 |
| a barrel of the SAME color, beside it and lower | 19 / 24 / 24 (0.67; 1 · 22 · 1; 0); front 22 / 24 | 10 / 12 / 24 (0.70; 1 · 10 · 1; 4); front 22 / 24 | 0 / 1 / 24 (0.72; 1 · 0 · 0; 0); front 22 / 24 |
| a barrel of the SAME color, straight in front | 11 / 11 / 12 (0.87; 0 · 11 · 0; 3); front 8 / 12 | 3 / 5 / 12 (0.81; 1 · 3 · 1; 3); front 9 / 12 | 0 / 1 / 12 (0.74; 1 · 0 · 0; 1); front 10 / 12 |
| a plain block of the barrel's body color | 24 / 24 / 24 (0.82; 0 · 24 · 0; 0) | 22 / 22 / 24 (0.72; 0 · 22 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |
| a plain block of the barrel's stripe color | 24 / 24 / 24 (0.82; 0 · 24 · 0; 0) | 23 / 23 / 24 (0.71; 0 · 23 · 0; 0) | 0 / 0 / 24 (-; 0 · 0 · 0; 0) |

## `before`, CAMPUS color model

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 52 / 52 / 52 (0.87; 1 · 46 · 5; 0) | 40 / 40 / 52 (0.77; 7 · 18 · 15; 0) | 0 / 0 / 52 (-; 0 · 0 · 0; 0) |
| a straight upright edge, one side | 52 / 52 / 52 (0.70; 4 · 47 · 1; 0) | 23 / 32 / 52 (0.55; 4 · 28 · 0; 8) | 0 / 0 / 52 (-; 0 · 0 · 0; 0) |
| a slanted edge, one side | 104 / 104 / 104 (0.80; 8 · 96 · 0; 0) | 46 / 46 / 104 (0.75; 8 · 38 · 0; 0) | 0 / 0 / 104 (-; 0 · 0 · 0; 0) |
| both sides cut | 26 / 26 / 26 (0.86; 5 · 21 · 0; 0) | 25 / 26 / 26 (0.88; 2 · 24 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| hidden from above | 26 / 26 / 26 (0.85; 1 · 25 · 0; 0) | 1 / 1 / 26 (0.93; 0 · 1 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 25 / 25 / 26 (0.87; 0 · 25 · 0; 0) | 1 / 1 / 26 (0.91; 0 · 1 · 0; 0) | 1 / 1 / 26 (0.53; 1 · 0 · 0; 0) |
| a post across the middle | 25 / 25 / 26 (0.88; 0 · 25 · 0; 0) | 5 / 5 / 26 (0.88; 0 · 5 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| a barrel of the OTHER color, beside it | 52 / 52 / 52 (0.80; 9 · 43 · 0; 0); front 46 / 52 | 33 / 39 / 52 (0.72; 5 · 34 · 0; 1); front 47 / 52 | 20 / 27 / 52 (0.77; 5 · 22 · 0; 1); front 46 / 52 |
| a barrel of the OTHER color, beside it and lower | 51 / 51 / 52 (0.84; 7 · 43 · 1; 1); front 46 / 52 | 45 / 48 / 52 (0.80; 3 · 42 · 3; 1); front 46 / 52 | 38 / 46 / 52 (0.80; 9 · 31 · 6; 1); front 46 / 52 |
| a barrel of the OTHER color, straight in front | 15 / 20 / 23 (0.81; 4 · 16 · 0; 11); front 15 / 23 | 18 / 19 / 24 (0.85; 0 · 19 · 0; 2); front 20 / 24 | 7 / 16 / 25 (0.80; 1 · 10 · 5; 1); front 20 / 25 |
| a barrel of the SAME color, beside it | 43 / 46 / 52 (0.78; 8 · 35 · 3; 1); front 39 / 52 | 22 / 26 / 52 (0.64; 5 · 8 · 13; 0); front 35 / 52 | 10 / 12 / 52 (0.70; 0 · 1 · 11; 0); front 36 / 52 |
| a barrel of the SAME color, beside it and lower | 49 / 51 / 52 (0.78; 5 · 44 · 2; 0); front 46 / 52 | 32 / 37 / 52 (0.69; 2 · 34 · 1; 2); front 43 / 52 | 1 / 2 / 52 (0.67; 0 · 1 · 1; 0); front 46 / 52 |
| a barrel of the SAME color, straight in front | 22 / 22 / 23 (0.85; 0 · 22 · 0; 1); front 16 / 23 | 13 / 14 / 24 (0.82; 1 · 13 · 0; 1); front 19 / 24 | 1 / 2 / 25 (0.56; 1 · 1 · 0; 0); front 21 / 25 |
| a plain block of the barrel's body color | 52 / 52 / 52 (0.82; 1 · 51 · 0; 2) | 40 / 40 / 52 (0.74; 2 · 36 · 2; 0) | 2 / 2 / 52 (0.76; 0 · 0 · 2; 0) |
| a plain block of the barrel's stripe color | 52 / 52 / 52 (0.82; 1 · 51 · 0; 2) | 39 / 39 / 52 (0.75; 2 · 37 · 0; 2) | 0 / 1 / 52 (0.76; 0 · 1 · 0; 3) |

### `before`: why the hidden barrel was not found under the v2 rule (all pools)

- cut by the frame edge, 50 %: stripe_refused:width 14
- cut by the frame edge, 75 %: stripe_refused:width 97, stripe_refused:height 2, stripe_not_sandwiched 1
- a straight upright edge, one side, 50 %: misplaced 47, stripe_refused:width 15
- a straight upright edge, one side, 75 %: stripe_refused:width 97, stripe_refused:height 2, stripe_not_sandwiched 1
- a slanted edge, one side, 50 %: stripe_refused:width 84
- a slanted edge, one side, 75 %: stripe_refused:width 179, stripe_refused:area 15, stripe_refused:height 4, stripe_hidden 1, stripe_not_sandwiched 1
- both sides cut, 50 %: misplaced 1
- both sides cut, 75 %: stripe_refused:width 49, stripe_not_sandwiched 1
- hidden from above, 50 %: stripe_not_sandwiched 47, stripe_refused:width 2
- hidden from above, 75 %: stripe_hidden 49, stripe_refused:width 1
- hidden from below (a low thing in front), 25 %: stripe_refused:width 1
- hidden from below (a low thing in front), 50 %: stripe_not_sandwiched 49
- hidden from below (a low thing in front), 75 %: stripe_hidden 49
- a post across the middle, 25 %: stripe_refused:width 1
- a post across the middle, 50 %: stripe_refused:width 40, stripe_refused:height 1
- a post across the middle, 75 %: stripe_refused:width 36, stripe_refused:area 13, stripe_hidden 1
- a barrel of the OTHER color, beside it, 25 %: stripe_refused:height 1
- a barrel of the OTHER color, beside it, 50 %: stripe_refused:height 14, misplaced 13, stripe_refused:width 6
- a barrel of the OTHER color, beside it, 75 %: stripe_refused:height 28, stripe_refused:width 17, misplaced 11
- a barrel of the OTHER color, beside it and lower, 25 %: misplaced 5, stripe_refused:height 2
- a barrel of the OTHER color, beside it and lower, 50 %: stripe_refused:width 7, stripe_refused:height 6, misplaced 6
- a barrel of the OTHER color, beside it and lower, 75 %: misplaced 20, stripe_refused:height 6, stripe_refused:width 5
- a barrel of the OTHER color, straight in front, 25 %: misplaced 12, stripe_refused:height 4, stripe_not_sandwiched 2
- a barrel of the OTHER color, straight in front, 50 %: stripe_refused:height 8, misplaced 2, stripe_refused:body_min 1, stripe_refused:width 1
- a barrel of the OTHER color, straight in front, 75 %: stripe_refused:height 20, misplaced 11, stripe_refused:body_min 1
- a barrel of the SAME color, beside it, 25 %: misplaced 20
- a barrel of the SAME color, beside it, 50 %: misplaced 68
- a barrel of the SAME color, beside it, 75 %: misplaced 83, stripe_refused:width 2
- a barrel of the SAME color, beside it and lower, 25 %: misplaced 11, stripe_refused:height 1
- a barrel of the SAME color, beside it and lower, 50 %: misplaced 38, stripe_refused:height 2
- a barrel of the SAME color, beside it and lower, 75 %: misplaced 97, stripe_refused:width 2
- a barrel of the SAME color, straight in front, 25 %: stripe_refused:height 1, stripe_hidden 1
- a barrel of the SAME color, straight in front, 50 %: misplaced 23
- a barrel of the SAME color, straight in front, 75 %: misplaced 48
- a plain block of the barrel's body color, 50 %: stripe_refused:width 15
- a plain block of the barrel's body color, 75 %: stripe_refused:width 96, stripe_refused:height 2
- a plain block of the barrel's stripe color, 50 %: stripe_refused:width 15
- a plain block of the barrel's stripe color, 75 %: stripe_refused:width 98, stripe_refused:height 1, misplaced 1

## `stack`, all three pools

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

## `stack`, HOME hand masks

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

## `stack`, HOME color model

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

## `stack`, CAMPUS color model

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

### `stack`: why the hidden barrel was not found under the v2 rule (all pools)

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

## `combined+thin`, all three pools

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 / 100 / 100 (0.92; 1 · 99 · 0; 0) | 99 / 99 / 100 (0.90; 3 · 94 · 2; 0) | 30 / 30 / 100 (0.86; 6 · 21 · 3; 0) |
| a straight upright edge, one side | 100 / 100 / 100 (0.83; 12 · 88 · 0; 0) | 90 / 94 / 100 (0.77; 4 · 90 · 0; 0) | 28 / 28 / 100 (0.88; 1 · 27 · 0; 0) |
| a slanted edge, one side | 200 / 200 / 200 (0.82; 83 · 116 · 1; 0) | 170 / 172 / 200 (0.84; 9 · 163 · 0; 0) | 0 / 0 / 200 (-; 0 · 0 · 0; 0) |
| both sides cut | 50 / 50 / 50 (0.88; 10 · 40 · 0; 0) | 49 / 50 / 50 (0.90; 2 · 48 · 0; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| hidden from above | 50 / 50 / 50 (0.87; 2 · 47 · 1; 0) | 45 / 45 / 50 (0.88; 2 · 42 · 1; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 49 / 50 / 50 (0.89; 1 · 49 · 0; 0) | 40 / 40 / 50 (0.90; 0 · 40 · 0; 0) | 1 / 1 / 50 (0.53; 1 · 0 · 0; 0) |
| a post across the middle | 49 / 49 / 50 (0.90; 1 · 48 · 0; 0) | 41 / 41 / 50 (0.87; 1 · 40 · 0; 0) | 11 / 13 / 50 (0.84; 4 · 9 · 0; 0) |
| a barrel of the OTHER color, beside it | 99 / 99 / 100 (0.83; 26 · 73 · 0; 0); front 94 / 100 | 94 / 96 / 100 (0.84; 6 · 87 · 3; 4); front 95 / 100 | 50 / 61 / 100 (0.81; 10 · 48 · 3; 1); front 94 / 100 |
| a barrel of the OTHER color, beside it and lower | 98 / 98 / 100 (0.85; 17 · 81 · 0; 1); front 90 / 100 | 92 / 92 / 100 (0.86; 4 · 87 · 1; 1); front 90 / 100 | 77 / 90 / 100 (0.83; 15 · 67 · 8; 2); front 90 / 100 |
| a barrel of the OTHER color, straight in front | 40 / 42 / 47 (0.87; 2 · 39 · 1; 3); front 32 / 47 | 38 / 39 / 48 (0.87; 0 · 39 · 0; 3); front 39 / 48 | 22 / 35 / 49 (0.82; 1 · 29 · 5; 1); front 42 / 49 |
| a barrel of the SAME color, beside it | 96 / 99 / 100 (0.83; 19 · 78 · 2; 2); front 92 / 100 | 88 / 97 / 100 (0.79; 18 · 72 · 7; 2); front 90 / 100 | 17 / 33 / 100 (0.71; 1 · 3 · 29; 4); front 79 / 100 |
| a barrel of the SAME color, beside it and lower | 91 / 99 / 100 (0.83; 25 · 71 · 3; 0); front 91 / 100 | 87 / 94 / 100 (0.83; 6 · 83 · 5; 0); front 87 / 100 | 29 / 36 / 100 (0.83; 3 · 31 · 2; 0); front 89 / 100 |
| a barrel of the SAME color, straight in front | 44 / 45 / 47 (0.87; 2 · 43 · 0; 4); front 34 / 47 | 29 / 37 / 48 (0.85; 3 · 30 · 4; 6); front 38 / 48 | 8 / 14 / 49 (0.76; 3 · 11 · 0; 2); front 42 / 49 |
| a plain block of the barrel's body color | 100 / 100 / 100 (0.87; 1 · 99 · 0; 2) | 99 / 99 / 100 (0.87; 2 · 95 · 2; 0) | 36 / 36 / 100 (0.86; 1 · 33 · 2; 0) |
| a plain block of the barrel's stripe color | 100 / 100 / 100 (0.86; 9 · 91 · 0; 2) | 99 / 99 / 100 (0.86; 8 · 91 · 0; 2) | 3 / 4 / 100 (0.78; 1 · 3 · 0; 3) |

## `combined+thin`, HOME hand masks

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 24 / 24 / 24 (0.97; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.96; 1 · 23 · 0; 0) | 14 / 14 / 24 (0.93; 1 · 13 · 0; 0) |
| a straight upright edge, one side | 24 / 24 / 24 (0.89; 0 · 24 · 0; 0) | 23 / 23 / 24 (0.84; 0 · 23 · 0; 0) | 14 / 14 / 24 (0.91; 0 · 14 · 0; 0) |
| a slanted edge, one side | 48 / 48 / 48 (0.86; 16 · 32 · 0; 0) | 45 / 45 / 48 (0.89; 0 · 45 · 0; 0) | 0 / 0 / 48 (-; 0 · 0 · 0; 0) |
| both sides cut | 12 / 12 / 12 (0.91; 2 · 10 · 0; 0) | 12 / 12 / 12 (0.94; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from above | 12 / 12 / 12 (0.91; 1 · 10 · 1; 0) | 12 / 12 / 12 (0.92; 0 · 11 · 1; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 12 / 12 / 12 (0.93; 1 · 11 · 0; 0) | 11 / 11 / 12 (0.95; 0 · 11 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a post across the middle | 12 / 12 / 12 (0.95; 1 · 11 · 0; 0) | 12 / 12 / 12 (0.91; 0 · 12 · 0; 0) | 7 / 7 / 12 (0.86; 1 · 6 · 0; 0) |
| a barrel of the OTHER color, beside it | 23 / 23 / 24 (0.90; 2 · 21 · 0; 0); front 24 / 24 | 24 / 24 / 24 (0.90; 0 · 24 · 0; 1); front 24 / 24 | 19 / 19 / 24 (0.89; 1 · 15 · 3; 0); front 24 / 24 |
| a barrel of the OTHER color, beside it and lower | 24 / 24 / 24 (0.91; 1 · 23 · 0; 0); front 20 / 24 | 23 / 23 / 24 (0.91; 0 · 23 · 0; 0); front 20 / 24 | 21 / 22 / 24 (0.91; 0 · 21 · 1; 0); front 20 / 24 |
| a barrel of the OTHER color, straight in front | 11 / 11 / 12 (0.93; 0 · 11 · 0; 0); front 8 / 12 | 10 / 10 / 12 (0.95; 0 · 10 · 0; 0); front 9 / 12 | 9 / 10 / 12 (0.87; 0 · 10 · 0; 0); front 11 / 12 |
| a barrel of the SAME color, beside it | 21 / 24 / 24 (0.85; 3 · 21 · 0; 0); front 24 / 24 | 16 / 24 / 24 (0.83; 2 · 20 · 2; 0); front 24 / 24 | 1 / 10 / 24 (0.73; 0 · 0 · 10; 0); front 23 / 24 |
| a barrel of the SAME color, beside it and lower | 20 / 24 / 24 (0.87; 6 · 18 · 0; 0); front 23 / 24 | 19 / 22 / 24 (0.85; 2 · 17 · 3; 0); front 22 / 24 | 9 / 9 / 24 (0.88; 0 · 9 · 0; 0); front 21 / 24 |
| a barrel of the SAME color, straight in front | 12 / 12 / 12 (0.92; 1 · 11 · 0; 0); front 9 / 12 | 11 / 12 / 12 (0.92; 1 · 11 · 0; 2); front 10 / 12 | 4 / 4 / 12 (0.85; 0 · 4 · 0; 0); front 11 / 12 |
| a plain block of the barrel's body color | 24 / 24 / 24 (0.92; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.92; 0 · 24 · 0; 0) | 15 / 15 / 24 (0.91; 0 · 15 · 0; 0) |
| a plain block of the barrel's stripe color | 24 / 24 / 24 (0.90; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.90; 1 · 23 · 0; 0) | 1 / 1 / 24 (0.89; 0 · 1 · 0; 0) |

## `combined+thin`, HOME color model

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 24 / 24 / 24 (0.90; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.87; 1 · 22 · 1; 0) | 5 / 5 / 24 (0.84; 1 · 3 · 1; 0) |
| a straight upright edge, one side | 24 / 24 / 24 (0.83; 3 · 21 · 0; 0) | 22 / 23 / 24 (0.78; 0 · 23 · 0; 0) | 4 / 4 / 24 (0.89; 0 · 4 · 0; 0) |
| a slanted edge, one side | 48 / 48 / 48 (0.81; 20 · 28 · 0; 0) | 41 / 41 / 48 (0.86; 0 · 41 · 0; 0) | 0 / 0 / 48 (-; 0 · 0 · 0; 0) |
| both sides cut | 12 / 12 / 12 (0.88; 2 · 10 · 0; 0) | 12 / 12 / 12 (0.90; 0 · 12 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from above | 12 / 12 / 12 (0.87; 0 · 12 · 0; 0) | 10 / 10 / 12 (0.90; 0 · 10 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 12 / 12 / 12 (0.89; 0 · 12 · 0; 0) | 8 / 8 / 12 (0.90; 0 · 8 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a post across the middle | 12 / 12 / 12 (0.89; 0 · 12 · 0; 0) | 10 / 10 / 12 (0.87; 0 · 10 · 0; 0) | 2 / 3 / 12 (0.82; 1 · 2 · 0; 0) |
| a barrel of the OTHER color, beside it | 24 / 24 / 24 (0.81; 7 · 17 · 0; 0); front 24 / 24 | 22 / 24 / 24 (0.80; 1 · 21 · 2; 2); front 24 / 24 | 8 / 13 / 24 (0.74; 4 · 9 · 0; 0); front 24 / 24 |
| a barrel of the OTHER color, beside it and lower | 23 / 23 / 24 (0.82; 6 · 17 · 0; 0); front 24 / 24 | 21 / 21 / 24 (0.85; 1 · 20 · 0; 0); front 24 / 24 | 17 / 21 / 24 (0.81; 5 · 14 · 2; 0); front 24 / 24 |
| a barrel of the OTHER color, straight in front | 10 / 11 / 12 (0.85; 0 · 11 · 0; 1); front 9 / 12 | 9 / 9 / 12 (0.86; 0 · 9 · 0; 1); front 10 / 12 | 5 / 7 / 12 (0.82; 0 · 7 · 0; 0); front 11 / 12 |
| a barrel of the SAME color, beside it | 24 / 24 / 24 (0.81; 5 · 19 · 0; 1); front 24 / 24 | 22 / 23 / 24 (0.80; 4 · 18 · 1; 2); front 24 / 24 | 5 / 10 / 24 (0.68; 1 · 1 · 8; 4); front 20 / 24 |
| a barrel of the SAME color, beside it and lower | 22 / 24 / 24 (0.84; 3 · 20 · 1; 0); front 22 / 24 | 22 / 24 / 24 (0.82; 1 · 22 · 1; 0); front 22 / 24 | 5 / 8 / 24 (0.81; 2 · 5 · 1; 0); front 22 / 24 |
| a barrel of the SAME color, straight in front | 10 / 11 / 12 (0.88; 0 · 11 · 0; 3); front 8 / 12 | 4 / 7 / 12 (0.79; 1 · 5 · 1; 3); front 9 / 12 | 0 / 2 / 12 (0.74; 1 · 1 · 0; 2); front 10 / 12 |
| a plain block of the barrel's body color | 24 / 24 / 24 (0.86; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.86; 0 · 24 · 0; 0) | 7 / 7 / 24 (0.86; 0 · 7 · 0; 0) |
| a plain block of the barrel's stripe color | 24 / 24 / 24 (0.84; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.84; 1 · 23 · 0; 0) | 1 / 1 / 24 (0.76; 0 · 1 · 0; 0) |

## `combined+thin`, CAMPUS color model

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 52 / 52 / 52 (0.91; 0 · 52 · 0; 0) | 51 / 51 / 52 (0.88; 1 · 49 · 1; 0) | 11 / 11 / 52 (0.79; 4 · 5 · 2; 0) |
| a straight upright edge, one side | 52 / 52 / 52 (0.80; 9 · 43 · 0; 0) | 45 / 48 / 52 (0.72; 4 · 44 · 0; 0) | 10 / 10 / 52 (0.83; 1 · 9 · 0; 0) |
| a slanted edge, one side | 104 / 104 / 104 (0.80; 47 · 56 · 1; 0) | 84 / 86 / 104 (0.80; 9 · 77 · 0; 0) | 0 / 0 / 104 (-; 0 · 0 · 0; 0) |
| both sides cut | 26 / 26 / 26 (0.86; 6 · 20 · 0; 0) | 25 / 26 / 26 (0.88; 2 · 24 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| hidden from above | 26 / 26 / 26 (0.86; 1 · 25 · 0; 0) | 23 / 23 / 26 (0.85; 2 · 21 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 25 / 26 / 26 (0.87; 0 · 26 · 0; 0) | 21 / 21 / 26 (0.88; 0 · 21 · 0; 0) | 1 / 1 / 26 (0.53; 1 · 0 · 0; 0) |
| a post across the middle | 25 / 25 / 26 (0.88; 0 · 25 · 0; 0) | 19 / 19 / 26 (0.85; 1 · 18 · 0; 0) | 2 / 3 / 26 (0.78; 2 · 1 · 0; 0) |
| a barrel of the OTHER color, beside it | 52 / 52 / 52 (0.81; 17 · 35 · 0; 0); front 46 / 52 | 48 / 48 / 52 (0.82; 5 · 42 · 1; 1); front 47 / 52 | 23 / 29 / 52 (0.79; 5 · 24 · 0; 1); front 46 / 52 |
| a barrel of the OTHER color, beside it and lower | 51 / 51 / 52 (0.84; 10 · 41 · 0; 1); front 46 / 52 | 48 / 48 / 52 (0.85; 3 · 44 · 1; 1); front 46 / 52 | 39 / 47 / 52 (0.81; 10 · 32 · 5; 2); front 46 / 52 |
| a barrel of the OTHER color, straight in front | 19 / 20 / 23 (0.84; 2 · 17 · 1; 2); front 15 / 23 | 19 / 20 / 24 (0.84; 0 · 20 · 0; 2); front 20 / 24 | 8 / 18 / 25 (0.80; 1 · 12 · 5; 1); front 20 / 25 |
| a barrel of the SAME color, beside it | 51 / 51 / 52 (0.82; 11 · 38 · 2; 1); front 44 / 52 | 50 / 50 / 52 (0.77; 12 · 34 · 4; 0); front 42 / 52 | 11 / 13 / 52 (0.72; 0 · 2 · 11; 0); front 36 / 52 |
| a barrel of the SAME color, beside it and lower | 49 / 51 / 52 (0.81; 16 · 33 · 2; 0); front 46 / 52 | 46 / 48 / 52 (0.83; 3 · 44 · 1; 0); front 43 / 52 | 15 / 19 / 52 (0.81; 1 · 17 · 1; 0); front 46 / 52 |
| a barrel of the SAME color, straight in front | 22 / 22 / 23 (0.85; 1 · 21 · 0; 1); front 17 / 23 | 14 / 18 / 24 (0.83; 1 · 14 · 3; 1); front 19 / 24 | 4 / 8 / 25 (0.72; 2 · 6 · 0; 0); front 21 / 25 |
| a plain block of the barrel's body color | 52 / 52 / 52 (0.85; 1 · 51 · 0; 2) | 51 / 51 / 52 (0.85; 2 · 47 · 2; 0) | 14 / 14 / 52 (0.82; 1 · 11 · 2; 0) |
| a plain block of the barrel's stripe color | 52 / 52 / 52 (0.84; 7 · 45 · 0; 2) | 51 / 51 / 52 (0.84; 6 · 45 · 0; 2) | 1 / 2 / 52 (0.73; 1 · 1 · 0; 3) |

### `combined+thin`: why the hidden barrel was not found under the v2 rule (all pools)

- cut by the frame edge, 50 %: stripe_refused:side_unexplained 1
- cut by the frame edge, 75 %: stripe_refused:outline_unknown 60, stripe_refused:slice_not_full 4, stripe_refused:width 3, stripe_refused:height 2, stripe_not_sandwiched 1
- a straight upright edge, one side, 50 %: stripe_refused:side_unexplained 6, misplaced 4
- a straight upright edge, one side, 75 %: stripe_refused:outline_unknown 60, stripe_refused:slice_not_full 4, stripe_refused:width 4, stripe_refused:height 2, stripe_refused:side_unexplained 1, stripe_not_sandwiched 1
- a slanted edge, one side, 50 %: stripe_refused:side_unexplained 28, misplaced 2
- a slanted edge, one side, 75 %: stripe_refused:outline_unknown 143, stripe_refused:width 25, stripe_refused:area 15, stripe_refused:slice_not_full 10, stripe_refused:height 4, stripe_refused:side_unexplained 1, stripe_hidden 1, stripe_not_sandwiched 1
- both sides cut, 50 %: misplaced 1
- both sides cut, 75 %: stripe_refused:outline_unknown 34, stripe_refused:side_unexplained 15, stripe_not_sandwiched 1
- hidden from above, 50 %: stripe_not_sandwiched 4, stripe_refused:width 1
- hidden from above, 75 %: stripe_hidden 49, stripe_refused:width 1
- hidden from below (a low thing in front), 25 %: misplaced 1
- hidden from below (a low thing in front), 50 %: stripe_not_sandwiched 10
- hidden from below (a low thing in front), 75 %: stripe_hidden 49
- a post across the middle, 25 %: stripe_refused:width 1
- a post across the middle, 50 %: stripe_refused:outline_unknown 5, stripe_refused:side_unexplained 1, stripe_refused:slice_not_full 1, stripe_refused:height 1, stripe_refused:width 1
- a post across the middle, 75 %: stripe_refused:width 22, stripe_refused:area 13, misplaced 2, stripe_refused:outline_unknown 1, stripe_hidden 1
- a barrel of the OTHER color, beside it, 25 %: stripe_refused:height 1
- a barrel of the OTHER color, beside it, 50 %: stripe_refused:height 4, misplaced 2
- a barrel of the OTHER color, beside it, 75 %: stripe_refused:height 25, misplaced 11, stripe_refused:outline_unknown 6, stripe_refused:width 3, stripe_refused:slice_not_full 3, stripe_refused:top_against_barrel 1, stripe_refused:side_unexplained 1
- a barrel of the OTHER color, beside it and lower, 25 %: stripe_refused:height 2
- a barrel of the OTHER color, beside it and lower, 50 %: stripe_refused:height 6, stripe_refused:slice_not_full 1, stripe_refused:width 1
- a barrel of the OTHER color, beside it and lower, 75 %: misplaced 13, stripe_refused:height 5, stripe_refused:outline_unknown 4, stripe_refused:width 1
- a barrel of the OTHER color, straight in front, 25 %: stripe_refused:height 3, misplaced 2, stripe_not_sandwiched 2
- a barrel of the OTHER color, straight in front, 50 %: stripe_refused:height 8, misplaced 1, stripe_refused:body_min 1
- a barrel of the OTHER color, straight in front, 75 %: misplaced 13, stripe_refused:height 13, stripe_refused:top_against_barrel 1
- a barrel of the SAME color, beside it, 25 %: misplaced 4
- a barrel of the SAME color, beside it, 50 %: misplaced 12
- a barrel of the SAME color, beside it, 75 %: misplaced 82, stripe_refused:outline_unknown 1
- a barrel of the SAME color, beside it and lower, 25 %: misplaced 8, stripe_refused:height 1
- a barrel of the SAME color, beside it and lower, 50 %: misplaced 11, stripe_refused:height 2
- a barrel of the SAME color, beside it and lower, 75 %: misplaced 71
- a barrel of the SAME color, straight in front, 25 %: misplaced 1, stripe_refused:height 1, stripe_hidden 1
- a barrel of the SAME color, straight in front, 50 %: misplaced 19
- a barrel of the SAME color, straight in front, 75 %: misplaced 41
- a plain block of the barrel's body color, 50 %: stripe_refused:side_unexplained 1
- a plain block of the barrel's body color, 75 %: stripe_refused:outline_unknown 55, stripe_refused:slice_not_full 4, stripe_refused:width 3, stripe_refused:height 2
- a plain block of the barrel's stripe color, 50 %: stripe_refused:width 1
- a plain block of the barrel's stripe color, 75 %: stripe_refused:outline_unknown 87, stripe_refused:slice_not_full 4, stripe_refused:width 4, stripe_refused:height 1, misplaced 1

## `combined+cover`, all three pools

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 / 100 / 100 (0.92; 1 · 99 · 0; 0) | 100 / 100 / 100 (0.89; 3 · 94 · 3; 0) | 88 / 89 / 100 (0.82; 28 · 54 · 7; 1) |
| a straight upright edge, one side | 100 / 100 / 100 (0.81; 12 · 59 · 29; 0) | 96 / 100 / 100 (0.76; 2 · 61 · 37; 0) | 74 / 88 / 100 (0.64; 1 · 28 · 59; 1) |
| a slanted edge, one side | 200 / 200 / 200 (0.80; 83 · 88 · 29; 0) | 197 / 200 / 200 (0.80; 9 · 135 · 56; 0) | 125 / 144 / 200 (0.64; 19 · 39 · 86; 0) |
| both sides cut | 50 / 50 / 50 (0.74; 10 · 6 · 34; 0) | 49 / 50 / 50 (0.64; 1 · 1 · 48; 0) | 44 / 49 / 50 (0.55; 0 · 0 · 49; 0) |
| hidden from above | 50 / 50 / 50 (0.87; 2 · 46 · 2; 0) | 45 / 45 / 50 (0.88; 2 · 42 · 1; 0) | 0 / 0 / 50 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 49 / 50 / 50 (0.89; 1 · 48 · 1; 0) | 40 / 40 / 50 (0.90; 0 · 40 · 0; 0) | 1 / 1 / 50 (0.53; 1 · 0 · 0; 0) |
| a post across the middle | 49 / 49 / 50 (0.90; 1 · 47 · 1; 0) | 43 / 48 / 50 (0.66; 0 · 17 · 31; 1) | 11 / 14 / 50 (0.81; 4 · 9 · 1; 0) |
| a barrel of the OTHER color, beside it | 99 / 99 / 100 (0.83; 27 · 70 · 2; 0); front 94 / 100 | 96 / 96 / 100 (0.84; 5 · 82 · 9; 4); front 95 / 100 | 69 / 75 / 100 (0.82; 5 · 62 · 8; 2); front 94 / 100 |
| a barrel of the OTHER color, beside it and lower | 98 / 98 / 100 (0.85; 16 · 81 · 1; 1); front 90 / 100 | 92 / 93 / 100 (0.85; 4 · 86 · 3; 2); front 90 / 100 | 84 / 96 / 100 (0.83; 12 · 74 · 10; 3); front 90 / 100 |
| a barrel of the OTHER color, straight in front | 40 / 42 / 47 (0.84; 2 · 34 · 6; 3); front 32 / 47 | 38 / 39 / 48 (0.87; 1 · 36 · 2; 4); front 39 / 48 | 22 / 35 / 49 (0.82; 1 · 28 · 6; 1); front 42 / 49 |
| a barrel of the SAME color, beside it | 96 / 99 / 100 (0.83; 19 · 77 · 3; 2); front 92 / 100 | 88 / 97 / 100 (0.79; 17 · 71 · 9; 2); front 90 / 100 | 24 / 38 / 100 (0.70; 2 · 4 · 32; 4); front 77 / 100 |
| a barrel of the SAME color, beside it and lower | 91 / 99 / 100 (0.83; 25 · 71 · 3; 1); front 91 / 100 | 87 / 94 / 100 (0.84; 5 · 82 · 7; 0); front 85 / 100 | 68 / 76 / 100 (0.83; 2 · 67 · 7; 0); front 88 / 100 |
| a barrel of the SAME color, straight in front | 44 / 45 / 47 (0.87; 2 · 42 · 1; 6); front 34 / 47 | 29 / 36 / 48 (0.86; 3 · 30 · 3; 8); front 38 / 48 | 8 / 14 / 49 (0.76; 3 · 11 · 0; 2); front 42 / 49 |
| a plain block of the barrel's body color | 100 / 100 / 100 (0.87; 1 · 97 · 2; 2) | 100 / 100 / 100 (0.86; 2 · 94 · 4; 0) | 90 / 91 / 100 (0.81; 3 · 49 · 39; 0) |
| a plain block of the barrel's stripe color | 100 / 100 / 100 (0.85; 8 · 88 · 4; 2) | 99 / 99 / 100 (0.86; 8 · 91 · 0; 2) | 88 / 91 / 100 (0.83; 9 · 81 · 1; 4) |

## `combined+cover`, HOME hand masks

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 24 / 24 / 24 (0.97; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.96; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.90; 3 · 21 · 0; 0) |
| a straight upright edge, one side | 24 / 24 / 24 (0.87; 0 · 16 · 8; 0) | 24 / 24 / 24 (0.83; 0 · 16 · 8; 0) | 24 / 24 / 24 (0.75; 0 · 14 · 10; 0) |
| a slanted edge, one side | 48 / 48 / 48 (0.83; 16 · 21 · 11; 0) | 48 / 48 / 48 (0.87; 0 · 37 · 11; 0) | 41 / 43 / 48 (0.64; 2 · 11 · 30; 0) |
| both sides cut | 12 / 12 / 12 (0.77; 2 · 1 · 9; 0) | 12 / 12 / 12 (0.65; 0 · 0 · 12; 0) | 11 / 12 / 12 (0.56; 0 · 0 · 12; 0) |
| hidden from above | 12 / 12 / 12 (0.91; 1 · 10 · 1; 0) | 12 / 12 / 12 (0.92; 0 · 11 · 1; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 12 / 12 / 12 (0.93; 1 · 11 · 0; 0) | 11 / 11 / 12 (0.95; 0 · 11 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a post across the middle | 12 / 12 / 12 (0.95; 1 · 11 · 0; 0) | 12 / 12 / 12 (0.72; 0 · 6 · 6; 0) | 7 / 7 / 12 (0.86; 1 · 6 · 0; 0) |
| a barrel of the OTHER color, beside it | 23 / 23 / 24 (0.90; 2 · 21 · 0; 0); front 24 / 24 | 24 / 24 / 24 (0.90; 0 · 22 · 2; 1); front 24 / 24 | 22 / 22 / 24 (0.89; 0 · 19 · 3; 0); front 24 / 24 |
| a barrel of the OTHER color, beside it and lower | 24 / 24 / 24 (0.91; 1 · 23 · 0; 0); front 20 / 24 | 23 / 23 / 24 (0.91; 0 · 23 · 0; 0); front 20 / 24 | 23 / 24 / 24 (0.90; 0 · 23 · 1; 0); front 20 / 24 |
| a barrel of the OTHER color, straight in front | 11 / 11 / 12 (0.93; 0 · 11 · 0; 0); front 8 / 12 | 10 / 10 / 12 (0.95; 0 · 10 · 0; 0); front 9 / 12 | 9 / 10 / 12 (0.87; 0 · 10 · 0; 0); front 11 / 12 |
| a barrel of the SAME color, beside it | 21 / 24 / 24 (0.85; 3 · 21 · 0; 0); front 24 / 24 | 16 / 24 / 24 (0.83; 2 · 20 · 2; 0); front 24 / 24 | 1 / 10 / 24 (0.73; 0 · 0 · 10; 0); front 23 / 24 |
| a barrel of the SAME color, beside it and lower | 20 / 24 / 24 (0.87; 6 · 18 · 0; 0); front 23 / 24 | 19 / 22 / 24 (0.85; 2 · 17 · 3; 0); front 22 / 24 | 15 / 16 / 24 (0.86; 0 · 14 · 2; 0); front 21 / 24 |
| a barrel of the SAME color, straight in front | 12 / 12 / 12 (0.92; 1 · 11 · 0; 0); front 9 / 12 | 11 / 12 / 12 (0.92; 1 · 11 · 0; 2); front 10 / 12 | 4 / 4 / 12 (0.85; 0 · 4 · 0; 0); front 11 / 12 |
| a plain block of the barrel's body color | 24 / 24 / 24 (0.92; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.92; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.85; 0 · 15 · 9; 0) |
| a plain block of the barrel's stripe color | 24 / 24 / 24 (0.89; 1 · 21 · 2; 0) | 24 / 24 / 24 (0.90; 1 · 23 · 0; 0) | 24 / 24 / 24 (0.88; 1 · 23 · 0; 0) |

## `combined+cover`, HOME color model

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 24 / 24 / 24 (0.90; 0 · 24 · 0; 0) | 24 / 24 / 24 (0.87; 1 · 22 · 1; 0) | 22 / 22 / 24 (0.80; 8 · 12 · 2; 1) |
| a straight upright edge, one side | 24 / 24 / 24 (0.81; 3 · 15 · 6; 0) | 23 / 24 / 24 (0.78; 0 · 17 · 7; 0) | 18 / 22 / 24 (0.59; 0 · 4 · 18; 1) |
| a slanted edge, one side | 48 / 48 / 48 (0.79; 20 · 23 · 5; 0) | 48 / 48 / 48 (0.82; 0 · 38 · 10; 0) | 35 / 38 / 48 (0.65; 0 · 14 · 24; 0) |
| both sides cut | 12 / 12 / 12 (0.75; 2 · 1 · 9; 0) | 12 / 12 / 12 (0.64; 0 · 0 · 12; 0) | 11 / 12 / 12 (0.55; 0 · 0 · 12; 0) |
| hidden from above | 12 / 12 / 12 (0.86; 0 · 11 · 1; 0) | 10 / 10 / 12 (0.90; 0 · 10 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 12 / 12 / 12 (0.87; 0 · 11 · 1; 0) | 8 / 8 / 12 (0.90; 0 · 8 · 0; 0) | 0 / 0 / 12 (-; 0 · 0 · 0; 0) |
| a post across the middle | 12 / 12 / 12 (0.88; 0 · 11 · 1; 0) | 11 / 12 / 12 (0.66; 0 · 4 · 8; 1) | 2 / 4 / 12 (0.73; 1 · 2 · 1; 0) |
| a barrel of the OTHER color, beside it | 24 / 24 / 24 (0.81; 8 · 16 · 0; 0); front 24 / 24 | 24 / 24 / 24 (0.83; 0 · 20 · 4; 2); front 24 / 24 | 15 / 18 / 24 (0.77; 2 · 14 · 2; 1); front 24 / 24 |
| a barrel of the OTHER color, beside it and lower | 23 / 23 / 24 (0.82; 6 · 17 · 0; 0); front 24 / 24 | 22 / 22 / 24 (0.85; 1 · 21 · 0; 0); front 24 / 24 | 19 / 23 / 24 (0.81; 5 · 15 · 3; 0); front 24 / 24 |
| a barrel of the OTHER color, straight in front | 10 / 11 / 12 (0.84; 0 · 10 · 1; 1); front 9 / 12 | 9 / 9 / 12 (0.86; 0 · 9 · 0; 1); front 10 / 12 | 5 / 7 / 12 (0.80; 0 · 6 · 1; 0); front 11 / 12 |
| a barrel of the SAME color, beside it | 24 / 24 / 24 (0.81; 5 · 19 · 0; 1); front 24 / 24 | 22 / 23 / 24 (0.80; 4 · 17 · 2; 2); front 24 / 24 | 7 / 10 / 24 (0.65; 1 · 0 · 9; 4); front 20 / 24 |
| a barrel of the SAME color, beside it and lower | 22 / 24 / 24 (0.84; 3 · 20 · 1; 1); front 22 / 24 | 22 / 24 / 24 (0.83; 1 · 21 · 2; 0); front 22 / 24 | 17 / 20 / 24 (0.81; 1 · 16 · 3; 0); front 22 / 24 |
| a barrel of the SAME color, straight in front | 10 / 11 / 12 (0.86; 0 · 10 · 1; 4); front 8 / 12 | 4 / 6 / 12 (0.84; 1 · 5 · 0; 4); front 9 / 12 | 0 / 2 / 12 (0.74; 1 · 1 · 0; 2); front 10 / 12 |
| a plain block of the barrel's body color | 24 / 24 / 24 (0.86; 0 · 23 · 1; 0) | 24 / 24 / 24 (0.86; 0 · 23 · 1; 0) | 23 / 23 / 24 (0.79; 0 · 12 · 11; 0) |
| a plain block of the barrel's stripe color | 24 / 24 / 24 (0.84; 0 · 23 · 1; 0) | 24 / 24 / 24 (0.84; 1 · 23 · 0; 0) | 23 / 23 / 24 (0.83; 1 · 22 · 0; 0) |

## `combined+cover`, CAMPUS color model

| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 52 / 52 / 52 (0.91; 0 · 52 · 0; 0) | 52 / 52 / 52 (0.88; 1 · 49 · 2; 0) | 42 / 43 / 52 (0.79; 17 · 21 · 5; 0) |
| a straight upright edge, one side | 52 / 52 / 52 (0.78; 9 · 28 · 15; 0) | 49 / 52 / 52 (0.73; 2 · 28 · 22; 0) | 32 / 42 / 52 (0.60; 1 · 10 · 31; 0) |
| a slanted edge, one side | 104 / 104 / 104 (0.79; 47 · 44 · 13; 0) | 101 / 104 / 104 (0.76; 9 · 60 · 35; 0) | 49 / 63 / 104 (0.63; 17 · 14 · 32; 0) |
| both sides cut | 26 / 26 / 26 (0.73; 6 · 4 · 16; 0) | 25 / 26 / 26 (0.64; 1 · 1 · 24; 0) | 22 / 25 / 26 (0.55; 0 · 0 · 25; 0) |
| hidden from above | 26 / 26 / 26 (0.86; 1 · 25 · 0; 0) | 23 / 23 / 26 (0.85; 2 · 21 · 0; 0) | 0 / 0 / 26 (-; 0 · 0 · 0; 0) |
| hidden from below (a low thing in front) | 25 / 26 / 26 (0.87; 0 · 26 · 0; 0) | 21 / 21 / 26 (0.88; 0 · 21 · 0; 0) | 1 / 1 / 26 (0.53; 1 · 0 · 0; 0) |
| a post across the middle | 25 / 25 / 26 (0.88; 0 · 25 · 0; 0) | 20 / 24 / 26 (0.63; 0 · 7 · 17; 0) | 2 / 3 / 26 (0.78; 2 · 1 · 0; 0) |
| a barrel of the OTHER color, beside it | 52 / 52 / 52 (0.81; 17 · 33 · 2; 0); front 46 / 52 | 48 / 48 / 52 (0.82; 5 · 40 · 3; 1); front 47 / 52 | 32 / 35 / 52 (0.81; 3 · 29 · 3; 1); front 46 / 52 |
| a barrel of the OTHER color, beside it and lower | 51 / 51 / 52 (0.84; 9 · 41 · 1; 1); front 46 / 52 | 47 / 48 / 52 (0.83; 3 · 42 · 3; 2); front 46 / 52 | 42 / 49 / 52 (0.81; 7 · 36 · 6; 3); front 46 / 52 |
| a barrel of the OTHER color, straight in front | 19 / 20 / 23 (0.80; 2 · 13 · 5; 2); front 15 / 23 | 19 / 20 / 24 (0.83; 1 · 17 · 2; 3); front 20 / 24 | 8 / 18 / 25 (0.80; 1 · 12 · 5; 1); front 20 / 25 |
| a barrel of the SAME color, beside it | 51 / 51 / 52 (0.82; 11 · 37 · 3; 1); front 44 / 52 | 50 / 50 / 52 (0.77; 11 · 34 · 5; 0); front 42 / 52 | 16 / 18 / 52 (0.72; 1 · 4 · 13; 0); front 34 / 52 |
| a barrel of the SAME color, beside it and lower | 49 / 51 / 52 (0.81; 16 · 33 · 2; 0); front 46 / 52 | 46 / 48 / 52 (0.83; 2 · 44 · 2; 0); front 41 / 52 | 36 / 40 / 52 (0.83; 1 · 37 · 2; 0); front 45 / 52 |
| a barrel of the SAME color, straight in front | 22 / 22 / 23 (0.85; 1 · 21 · 0; 2); front 17 / 23 | 14 / 18 / 24 (0.83; 1 · 14 · 3; 2); front 19 / 24 | 4 / 8 / 25 (0.72; 2 · 6 · 0; 0); front 21 / 25 |
| a plain block of the barrel's body color | 52 / 52 / 52 (0.85; 1 · 50 · 1; 2) | 52 / 52 / 52 (0.84; 2 · 47 · 3; 0) | 43 / 44 / 52 (0.79; 3 · 22 · 19; 0) |
| a plain block of the barrel's stripe color | 52 / 52 / 52 (0.84; 7 · 44 · 1; 2) | 51 / 51 / 52 (0.84; 6 · 45 · 0; 2) | 41 / 44 / 52 (0.80; 7 · 36 · 1; 4) |

### `combined+cover`: why the hidden barrel was not found under the v2 rule (all pools)

- cut by the frame edge, 75 %: stripe_refused:slice_not_full 4, stripe_refused:width 3, misplaced 2, stripe_refused:height 2, stripe_not_sandwiched 1
- a straight upright edge, one side, 50 %: misplaced 4
- a straight upright edge, one side, 75 %: misplaced 15, stripe_refused:slice_not_full 4, stripe_refused:width 4, stripe_refused:height 2, stripe_not_sandwiched 1
- a slanted edge, one side, 50 %: misplaced 3
- a slanted edge, one side, 75 %: stripe_refused:width 25, misplaced 19, stripe_refused:area 15, stripe_refused:slice_not_full 10, stripe_refused:height 4, stripe_hidden 1, stripe_not_sandwiched 1
- both sides cut, 50 %: misplaced 1
- both sides cut, 75 %: misplaced 5, stripe_not_sandwiched 1
- hidden from above, 50 %: stripe_not_sandwiched 4, stripe_refused:width 1
- hidden from above, 75 %: stripe_hidden 49, stripe_refused:width 1
- hidden from below (a low thing in front), 25 %: misplaced 1
- hidden from below (a low thing in front), 50 %: stripe_not_sandwiched 10
- hidden from below (a low thing in front), 75 %: stripe_hidden 49
- a post across the middle, 25 %: stripe_refused:width 1
- a post across the middle, 50 %: misplaced 5, stripe_refused:height 1, stripe_refused:width 1
- a post across the middle, 75 %: stripe_refused:width 22, stripe_refused:area 13, misplaced 3, stripe_hidden 1
- a barrel of the OTHER color, beside it, 25 %: stripe_refused:height 1
- a barrel of the OTHER color, beside it, 50 %: stripe_refused:height 4
- a barrel of the OTHER color, beside it, 75 %: stripe_refused:height 19, misplaced 6, stripe_refused:width 3, stripe_refused:slice_not_full 3
- a barrel of the OTHER color, beside it and lower, 25 %: stripe_refused:height 2
- a barrel of the OTHER color, beside it and lower, 50 %: stripe_refused:height 6, misplaced 1, stripe_refused:width 1
- a barrel of the OTHER color, beside it and lower, 75 %: misplaced 12, stripe_refused:height 3, stripe_refused:width 1
- a barrel of the OTHER color, straight in front, 25 %: stripe_refused:height 3, misplaced 2, stripe_not_sandwiched 2
- a barrel of the OTHER color, straight in front, 50 %: stripe_refused:height 8, misplaced 1, stripe_refused:body_min 1
- a barrel of the OTHER color, straight in front, 75 %: misplaced 13, stripe_refused:height 13, stripe_refused:top_against_barrel 1
- a barrel of the SAME color, beside it, 25 %: misplaced 4
- a barrel of the SAME color, beside it, 50 %: misplaced 12
- a barrel of the SAME color, beside it, 75 %: misplaced 76
- a barrel of the SAME color, beside it and lower, 25 %: misplaced 8, stripe_refused:height 1
- a barrel of the SAME color, beside it and lower, 50 %: misplaced 11, stripe_refused:height 2
- a barrel of the SAME color, beside it and lower, 75 %: misplaced 32
- a barrel of the SAME color, straight in front, 25 %: misplaced 1, stripe_refused:height 1, stripe_hidden 1
- a barrel of the SAME color, straight in front, 50 %: misplaced 19
- a barrel of the SAME color, straight in front, 75 %: misplaced 41
- a plain block of the barrel's body color, 75 %: stripe_refused:slice_not_full 4, stripe_refused:width 3, stripe_refused:height 2, misplaced 1
- a plain block of the barrel's stripe color, 50 %: stripe_refused:width 1
- a plain block of the barrel's stripe color, 75 %: stripe_refused:slice_not_full 4, stripe_refused:width 4, misplaced 3, stripe_refused:height 1

