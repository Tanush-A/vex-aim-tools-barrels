# Simulated side cuts

Source barrels: HOME 12, CAMPUS 26, ABP white 14. Each cell: **found / placed / scenes**. found = the strict rule against the FULL box. placed = found, and the box's centre within 10 % of the width of the true centre. A box centred on the visible half is a quarter of a width off: found, not placed.

`centred` = today. `own_side` = the candidate. `own_side+centred` = the own side first, else today's guess.

## all pools

### plain cut

| kind | mode | 50 % hidden | 60 % hidden | 65 % hidden | 75 % hidden | boxes that are not the barrel |
|---|---|---|---|---|---|---|
| edge | `centred` | 96 / 63 / 104 | 64 / 63 / 104 | 54 / 54 / 104 | 28 / 28 / 104 | 5 |
| edge | `own_side` | 94 / 92 / 104 | 93 / 91 / 104 | 92 / 90 / 104 | 81 / 79 / 104 | 5 |
| edge | `own_side+centred` | 100 / 92 / 104 | 93 / 91 / 104 | 92 / 90 / 104 | 81 / 79 / 104 | 5 |
| slant | `centred` | 183 / 153 / 208 | 87 / 87 / 208 | 49 / 49 / 208 | 0 / 0 / 208 | 9 |
| slant | `own_side` | 195 / 185 / 208 | 176 / 172 / 208 | 167 / 163 / 208 | 114 / 114 / 208 | 30 |
| slant | `own_side+centred` | 199 / 185 / 208 | 176 / 172 / 208 | 167 / 163 / 208 | 114 / 114 / 208 | 30 |
| edge + slant | `centred` | 279 / 216 / 312 | 151 / 150 / 312 | 103 / 103 / 312 | 28 / 28 / 312 | 14 |
| edge + slant | `own_side` | 289 / 277 / 312 | 269 / 263 / 312 | 259 / 253 / 312 | 195 / 193 / 312 | 35 |
| edge + slant | `own_side+centred` | 299 / 277 / 312 | 269 / 263 / 312 | 259 / 253 / 312 | 195 / 193 / 312 | 35 |

### real-like: the stripe ends 6 px before the cut

| kind | mode | 50 % hidden | 60 % hidden | 65 % hidden | 75 % hidden | boxes that are not the barrel |
|---|---|---|---|---|---|---|
| edge | `centred` | 71 / 65 / 104 | 60 / 60 / 104 | 49 / 49 / 104 | 9 / 9 / 104 | 4 |
| edge | `own_side` | 95 / 93 / 104 | 90 / 88 / 104 | 80 / 80 / 104 | 26 / 26 / 104 | 8 |
| edge | `own_side+centred` | 95 / 93 / 104 | 90 / 88 / 104 | 80 / 80 / 104 | 26 / 26 / 104 | 8 |
| slant | `centred` | 183 / 173 / 208 | 96 / 96 / 208 | 41 / 41 / 208 | 0 / 0 / 208 | 9 |
| slant | `own_side` | 197 / 189 / 208 | 165 / 165 / 208 | 151 / 151 / 208 | 68 / 68 / 208 | 20 |
| slant | `own_side+centred` | 198 / 189 / 208 | 165 / 165 / 208 | 151 / 151 / 208 | 68 / 68 / 208 | 20 |
| edge + slant | `centred` | 254 / 238 / 312 | 156 / 156 / 312 | 90 / 90 / 312 | 9 / 9 / 312 | 13 |
| edge + slant | `own_side` | 292 / 282 / 312 | 255 / 253 / 312 | 231 / 231 / 312 | 94 / 94 / 312 | 28 |
| edge + slant | `own_side+centred` | 293 / 282 / 312 | 255 / 253 / 312 | 231 / 231 / 312 | 94 / 94 / 312 | 28 |

## the pools the numbers were chosen on (HOME, ABP white)

### plain cut

| kind | mode | 50 % hidden | 60 % hidden | 65 % hidden | 75 % hidden | boxes that are not the barrel |
|---|---|---|---|---|---|---|
| edge | `centred` | 51 / 38 / 52 | 38 / 38 / 52 | 36 / 36 / 52 | 18 / 18 / 52 | 0 |
| edge | `own_side` | 50 / 49 / 52 | 50 / 49 / 52 | 51 / 50 / 52 | 48 / 47 / 52 | 0 |
| edge | `own_side+centred` | 51 / 49 / 52 | 50 / 49 / 52 | 51 / 50 / 52 | 48 / 47 / 52 | 0 |
| slant | `centred` | 99 / 92 / 104 | 55 / 55 / 104 | 36 / 36 / 104 | 0 / 0 / 104 | 0 |
| slant | `own_side` | 102 / 99 / 104 | 101 / 99 / 104 | 99 / 97 / 104 | 74 / 74 / 104 | 8 |
| slant | `own_side+centred` | 102 / 99 / 104 | 101 / 99 / 104 | 99 / 97 / 104 | 74 / 74 / 104 | 8 |
| edge + slant | `centred` | 150 / 130 / 156 | 93 / 93 / 156 | 72 / 72 / 156 | 18 / 18 / 156 | 0 |
| edge + slant | `own_side` | 152 / 148 / 156 | 151 / 148 / 156 | 150 / 147 / 156 | 122 / 121 / 156 | 8 |
| edge + slant | `own_side+centred` | 153 / 148 / 156 | 151 / 148 / 156 | 150 / 147 / 156 | 122 / 121 / 156 | 8 |

### real-like: the stripe ends 6 px before the cut

| kind | mode | 50 % hidden | 60 % hidden | 65 % hidden | 75 % hidden | boxes that are not the barrel |
|---|---|---|---|---|---|---|
| edge | `centred` | 39 / 38 / 52 | 37 / 37 / 52 | 33 / 33 / 52 | 7 / 7 / 52 | 0 |
| edge | `own_side` | 51 / 50 / 52 | 49 / 48 / 52 | 46 / 46 / 52 | 19 / 19 / 52 | 1 |
| edge | `own_side+centred` | 51 / 50 / 52 | 49 / 48 / 52 | 46 / 46 / 52 | 19 / 19 / 52 | 1 |
| slant | `centred` | 97 / 97 / 104 | 61 / 61 / 104 | 27 / 27 / 104 | 0 / 0 / 104 | 0 |
| slant | `own_side` | 102 / 100 / 104 | 97 / 97 / 104 | 88 / 88 / 104 | 49 / 49 / 104 | 4 |
| slant | `own_side+centred` | 102 / 100 / 104 | 97 / 97 / 104 | 88 / 88 / 104 | 49 / 49 / 104 | 4 |
| edge + slant | `centred` | 136 / 135 / 156 | 98 / 98 / 156 | 60 / 60 / 156 | 7 / 7 / 156 | 0 |
| edge + slant | `own_side` | 153 / 150 / 156 | 146 / 145 / 156 | 134 / 134 / 156 | 68 / 68 / 156 | 5 |
| edge + slant | `own_side+centred` | 153 / 150 / 156 | 146 / 145 / 156 | 134 / 134 / 156 | 68 / 68 / 156 | 5 |

## held out (CAMPUS)

### plain cut

| kind | mode | 50 % hidden | 60 % hidden | 65 % hidden | 75 % hidden | boxes that are not the barrel |
|---|---|---|---|---|---|---|
| edge | `centred` | 45 / 25 / 52 | 26 / 25 / 52 | 18 / 18 / 52 | 10 / 10 / 52 | 5 |
| edge | `own_side` | 44 / 43 / 52 | 43 / 42 / 52 | 41 / 40 / 52 | 33 / 32 / 52 | 5 |
| edge | `own_side+centred` | 49 / 43 / 52 | 43 / 42 / 52 | 41 / 40 / 52 | 33 / 32 / 52 | 5 |
| slant | `centred` | 84 / 61 / 104 | 32 / 32 / 104 | 13 / 13 / 104 | 0 / 0 / 104 | 9 |
| slant | `own_side` | 93 / 86 / 104 | 75 / 73 / 104 | 68 / 66 / 104 | 40 / 40 / 104 | 22 |
| slant | `own_side+centred` | 97 / 86 / 104 | 75 / 73 / 104 | 68 / 66 / 104 | 40 / 40 / 104 | 22 |
| edge + slant | `centred` | 129 / 86 / 156 | 58 / 57 / 156 | 31 / 31 / 156 | 10 / 10 / 156 | 14 |
| edge + slant | `own_side` | 137 / 129 / 156 | 118 / 115 / 156 | 109 / 106 / 156 | 73 / 72 / 156 | 27 |
| edge + slant | `own_side+centred` | 146 / 129 / 156 | 118 / 115 / 156 | 109 / 106 / 156 | 73 / 72 / 156 | 27 |

### real-like: the stripe ends 6 px before the cut

| kind | mode | 50 % hidden | 60 % hidden | 65 % hidden | 75 % hidden | boxes that are not the barrel |
|---|---|---|---|---|---|---|
| edge | `centred` | 32 / 27 / 52 | 23 / 23 / 52 | 16 / 16 / 52 | 2 / 2 / 52 | 4 |
| edge | `own_side` | 44 / 43 / 52 | 41 / 40 / 52 | 34 / 34 / 52 | 7 / 7 / 52 | 7 |
| edge | `own_side+centred` | 44 / 43 / 52 | 41 / 40 / 52 | 34 / 34 / 52 | 7 / 7 / 52 | 7 |
| slant | `centred` | 86 / 76 / 104 | 35 / 35 / 104 | 14 / 14 / 104 | 0 / 0 / 104 | 9 |
| slant | `own_side` | 95 / 89 / 104 | 68 / 68 / 104 | 63 / 63 / 104 | 19 / 19 / 104 | 16 |
| slant | `own_side+centred` | 96 / 89 / 104 | 68 / 68 / 104 | 63 / 63 / 104 | 19 / 19 / 104 | 16 |
| edge + slant | `centred` | 118 / 103 / 156 | 58 / 58 / 156 | 30 / 30 / 156 | 2 / 2 / 156 | 13 |
| edge + slant | `own_side` | 139 / 132 / 156 | 109 / 108 / 156 | 97 / 97 / 156 | 26 / 26 / 156 | 23 |
| edge + slant | `own_side+centred` | 140 / 132 / 156 | 109 / 108 / 156 | 97 / 97 / 156 | 26 / 26 / 156 | 23 |

## HOME

### plain cut

| kind | mode | 50 % hidden | 60 % hidden | 65 % hidden | 75 % hidden | boxes that are not the barrel |
|---|---|---|---|---|---|---|
| edge | `centred` | 23 / 17 / 24 | 17 / 17 / 24 | 16 / 16 / 24 | 5 / 5 / 24 | 0 |
| edge | `own_side` | 22 / 21 / 24 | 22 / 21 / 24 | 23 / 22 / 24 | 20 / 19 / 24 | 0 |
| edge | `own_side+centred` | 23 / 21 / 24 | 22 / 21 / 24 | 23 / 22 / 24 | 20 / 19 / 24 | 0 |
| slant | `centred` | 43 / 39 / 48 | 19 / 19 / 48 | 11 / 11 / 48 | 0 / 0 / 48 | 0 |
| slant | `own_side` | 46 / 43 / 48 | 45 / 43 / 48 | 43 / 41 / 48 | 29 / 29 / 48 | 3 |
| slant | `own_side+centred` | 46 / 43 / 48 | 45 / 43 / 48 | 43 / 41 / 48 | 29 / 29 / 48 | 3 |
| edge + slant | `centred` | 66 / 56 / 72 | 36 / 36 / 72 | 27 / 27 / 72 | 5 / 5 / 72 | 0 |
| edge + slant | `own_side` | 68 / 64 / 72 | 67 / 64 / 72 | 66 / 63 / 72 | 49 / 48 / 72 | 3 |
| edge + slant | `own_side+centred` | 69 / 64 / 72 | 67 / 64 / 72 | 66 / 63 / 72 | 49 / 48 / 72 | 3 |

### real-like: the stripe ends 6 px before the cut

| kind | mode | 50 % hidden | 60 % hidden | 65 % hidden | 75 % hidden | boxes that are not the barrel |
|---|---|---|---|---|---|---|
| edge | `centred` | 17 / 17 / 24 | 16 / 16 / 24 | 12 / 12 / 24 | 1 / 1 / 24 | 0 |
| edge | `own_side` | 23 / 22 / 24 | 21 / 20 / 24 | 18 / 18 / 24 | 5 / 5 / 24 | 0 |
| edge | `own_side+centred` | 23 / 22 / 24 | 21 / 20 / 24 | 18 / 18 / 24 | 5 / 5 / 24 | 0 |
| slant | `centred` | 41 / 41 / 48 | 21 / 21 / 48 | 8 / 8 / 48 | 0 / 0 / 48 | 0 |
| slant | `own_side` | 46 / 44 / 48 | 41 / 41 / 48 | 32 / 32 / 48 | 17 / 17 / 48 | 0 |
| slant | `own_side+centred` | 46 / 44 / 48 | 41 / 41 / 48 | 32 / 32 / 48 | 17 / 17 / 48 | 0 |
| edge + slant | `centred` | 58 / 58 / 72 | 37 / 37 / 72 | 20 / 20 / 72 | 1 / 1 / 72 | 0 |
| edge + slant | `own_side` | 69 / 66 / 72 | 62 / 61 / 72 | 50 / 50 / 72 | 22 / 22 / 72 | 0 |
| edge + slant | `own_side+centred` | 69 / 66 / 72 | 62 / 61 / 72 | 50 / 50 / 72 | 22 / 22 / 72 | 0 |

## CAMPUS

### plain cut

| kind | mode | 50 % hidden | 60 % hidden | 65 % hidden | 75 % hidden | boxes that are not the barrel |
|---|---|---|---|---|---|---|
| edge | `centred` | 45 / 25 / 52 | 26 / 25 / 52 | 18 / 18 / 52 | 10 / 10 / 52 | 5 |
| edge | `own_side` | 44 / 43 / 52 | 43 / 42 / 52 | 41 / 40 / 52 | 33 / 32 / 52 | 5 |
| edge | `own_side+centred` | 49 / 43 / 52 | 43 / 42 / 52 | 41 / 40 / 52 | 33 / 32 / 52 | 5 |
| slant | `centred` | 84 / 61 / 104 | 32 / 32 / 104 | 13 / 13 / 104 | 0 / 0 / 104 | 9 |
| slant | `own_side` | 93 / 86 / 104 | 75 / 73 / 104 | 68 / 66 / 104 | 40 / 40 / 104 | 22 |
| slant | `own_side+centred` | 97 / 86 / 104 | 75 / 73 / 104 | 68 / 66 / 104 | 40 / 40 / 104 | 22 |
| edge + slant | `centred` | 129 / 86 / 156 | 58 / 57 / 156 | 31 / 31 / 156 | 10 / 10 / 156 | 14 |
| edge + slant | `own_side` | 137 / 129 / 156 | 118 / 115 / 156 | 109 / 106 / 156 | 73 / 72 / 156 | 27 |
| edge + slant | `own_side+centred` | 146 / 129 / 156 | 118 / 115 / 156 | 109 / 106 / 156 | 73 / 72 / 156 | 27 |

### real-like: the stripe ends 6 px before the cut

| kind | mode | 50 % hidden | 60 % hidden | 65 % hidden | 75 % hidden | boxes that are not the barrel |
|---|---|---|---|---|---|---|
| edge | `centred` | 32 / 27 / 52 | 23 / 23 / 52 | 16 / 16 / 52 | 2 / 2 / 52 | 4 |
| edge | `own_side` | 44 / 43 / 52 | 41 / 40 / 52 | 34 / 34 / 52 | 7 / 7 / 52 | 7 |
| edge | `own_side+centred` | 44 / 43 / 52 | 41 / 40 / 52 | 34 / 34 / 52 | 7 / 7 / 52 | 7 |
| slant | `centred` | 86 / 76 / 104 | 35 / 35 / 104 | 14 / 14 / 104 | 0 / 0 / 104 | 9 |
| slant | `own_side` | 95 / 89 / 104 | 68 / 68 / 104 | 63 / 63 / 104 | 19 / 19 / 104 | 16 |
| slant | `own_side+centred` | 96 / 89 / 104 | 68 / 68 / 104 | 63 / 63 / 104 | 19 / 19 / 104 | 16 |
| edge + slant | `centred` | 118 / 103 / 156 | 58 / 58 / 156 | 30 / 30 / 156 | 2 / 2 / 156 | 13 |
| edge + slant | `own_side` | 139 / 132 / 156 | 109 / 108 / 156 | 97 / 97 / 156 | 26 / 26 / 156 | 23 |
| edge + slant | `own_side+centred` | 140 / 132 / 156 | 109 / 108 / 156 | 97 / 97 / 156 | 26 / 26 / 156 | 23 |

## ABP white

### plain cut

| kind | mode | 50 % hidden | 60 % hidden | 65 % hidden | 75 % hidden | boxes that are not the barrel |
|---|---|---|---|---|---|---|
| edge | `centred` | 28 / 21 / 28 | 21 / 21 / 28 | 20 / 20 / 28 | 13 / 13 / 28 | 0 |
| edge | `own_side` | 28 / 28 / 28 | 28 / 28 / 28 | 28 / 28 / 28 | 28 / 28 / 28 | 0 |
| edge | `own_side+centred` | 28 / 28 / 28 | 28 / 28 / 28 | 28 / 28 / 28 | 28 / 28 / 28 | 0 |
| slant | `centred` | 56 / 53 / 56 | 36 / 36 / 56 | 25 / 25 / 56 | 0 / 0 / 56 | 0 |
| slant | `own_side` | 56 / 56 / 56 | 56 / 56 / 56 | 56 / 56 / 56 | 45 / 45 / 56 | 5 |
| slant | `own_side+centred` | 56 / 56 / 56 | 56 / 56 / 56 | 56 / 56 / 56 | 45 / 45 / 56 | 5 |
| edge + slant | `centred` | 84 / 74 / 84 | 57 / 57 / 84 | 45 / 45 / 84 | 13 / 13 / 84 | 0 |
| edge + slant | `own_side` | 84 / 84 / 84 | 84 / 84 / 84 | 84 / 84 / 84 | 73 / 73 / 84 | 5 |
| edge + slant | `own_side+centred` | 84 / 84 / 84 | 84 / 84 / 84 | 84 / 84 / 84 | 73 / 73 / 84 | 5 |

### real-like: the stripe ends 6 px before the cut

| kind | mode | 50 % hidden | 60 % hidden | 65 % hidden | 75 % hidden | boxes that are not the barrel |
|---|---|---|---|---|---|---|
| edge | `centred` | 22 / 21 / 28 | 21 / 21 / 28 | 21 / 21 / 28 | 6 / 6 / 28 | 0 |
| edge | `own_side` | 28 / 28 / 28 | 28 / 28 / 28 | 28 / 28 / 28 | 14 / 14 / 28 | 1 |
| edge | `own_side+centred` | 28 / 28 / 28 | 28 / 28 / 28 | 28 / 28 / 28 | 14 / 14 / 28 | 1 |
| slant | `centred` | 56 / 56 / 56 | 40 / 40 / 56 | 19 / 19 / 56 | 0 / 0 / 56 | 0 |
| slant | `own_side` | 56 / 56 / 56 | 56 / 56 / 56 | 56 / 56 / 56 | 32 / 32 / 56 | 4 |
| slant | `own_side+centred` | 56 / 56 / 56 | 56 / 56 / 56 | 56 / 56 / 56 | 32 / 32 / 56 | 4 |
| edge + slant | `centred` | 78 / 77 / 84 | 61 / 61 / 84 | 40 / 40 / 84 | 6 / 6 / 84 | 0 |
| edge + slant | `own_side` | 84 / 84 / 84 | 84 / 84 / 84 | 84 / 84 / 84 | 46 / 46 / 84 | 5 |
| edge + slant | `own_side+centred` | 84 / 84 / 84 | 84 / 84 / 84 | 84 / 84 / 84 | 46 / 46 / 84 | 5 |

## Which rule drew the box of the barrel (all pools, plain and real-like together)

- `centred`, 50 %: hidden_side (found) 260, outline (found) 183, no box (not found) 85, centred (found) 68, thin_outline (found) 14, no box (found) 8, hidden_side (not found) 6
- `centred`, 60 %: no box (not found) 315, hidden_side (found) 176, outline (found) 94, thin_outline (found) 36, centred (found) 1, centred (not found) 1, hidden_side (not found) 1
- `centred`, 65 %: no box (not found) 429, hidden_side (found) 87, outline (found) 55, thin_outline (found) 51, hidden_side (not found) 2
- `centred`, 75 %: no box (not found) 586, thin_outline (found) 36, outline (found) 1, thin_outline (not found) 1
- `own_side`, 50 %: hidden_side (found) 260, outline (found) 183, own_side (found) 96, no box (not found) 37, thin_own_side (found) 19, thin_outline (found) 14, no box (found) 8, hidden_side (not found) 6, two_sides (found) 1
- `own_side`, 60 %: hidden_side (found) 176, own_side (found) 118, thin_own_side (found) 100, no box (not found) 99, outline (found) 94, thin_outline (found) 36, hidden_side (not found) 1
- `own_side`, 65 %: thin_own_side (found) 205, no box (not found) 131, own_side (found) 92, hidden_side (found) 87, outline (found) 55, thin_outline (found) 51, hidden_side (not found) 2, thin_own_side (not found) 1
- `own_side`, 75 %: no box (not found) 298, thin_own_side (found) 251, thin_outline (found) 36, thin_own_side (not found) 36, own_side (found) 1, outline (found) 1, thin_outline (not found) 1
- `own_side+centred`, 50 %: hidden_side (found) 260, outline (found) 183, own_side (found) 96, no box (not found) 26, thin_own_side (found) 19, thin_outline (found) 14, centred (found) 12, no box (found) 8, hidden_side (not found) 6
- `own_side+centred`, 60 %: hidden_side (found) 176, own_side (found) 118, thin_own_side (found) 100, no box (not found) 99, outline (found) 94, thin_outline (found) 36, hidden_side (not found) 1
- `own_side+centred`, 65 %: thin_own_side (found) 205, no box (not found) 131, own_side (found) 92, hidden_side (found) 87, outline (found) 55, thin_outline (found) 51, hidden_side (not found) 2, thin_own_side (not found) 1
- `own_side+centred`, 75 %: no box (not found) 298, thin_own_side (found) 251, thin_outline (found) 36, thin_own_side (not found) 36, own_side (found) 1, outline (found) 1, thin_outline (not found) 1

## Why there is no found box (all pools)

- `centred`: outline_unknown 717, side_unexplained 292, width 131, area 128, slice_not_full 68, nothing 57, height 22, box by hidden_side, not right 9, box by centred, not right 1, box by thin_outline, not right 1
- `own_side`: width 131, area 128, outline_unknown 113, slice_not_full 58, nothing 57, side_unexplained 56, box by thin_own_side, not right 37, height 22, box by hidden_side, not right 9, box by thin_outline, not right 1
- `own_side+centred`: width 131, area 128, outline_unknown 113, slice_not_full 58, nothing 57, side_unexplained 45, box by thin_own_side, not right 37, height 22, box by hidden_side, not right 9, box by thin_outline, not right 1
