# Simulated side cuts

Source barrels: HOME 12, ABP white 14. Each cell: **found / placed / scenes**. found = the strict rule against the FULL box. placed = found, and the box's centre within 10 % of the width of the true centre. A box centred on the visible half is a quarter of a width off: found, not placed.

`centred` = today. `own_side` = the candidate. `own_side+centred` = the own side first, else today's guess.

## all pools

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

- `centred`, 50 %: hidden_side (found) 148, outline (found) 114, no box (not found) 26, centred (found) 20, thin_outline (found) 4
- `centred`, 60 %: no box (not found) 121, hidden_side (found) 113, outline (found) 62, thin_outline (found) 16
- `centred`, 65 %: no box (not found) 180, hidden_side (found) 63, outline (found) 39, thin_outline (found) 30
- `centred`, 75 %: no box (not found) 287, thin_outline (found) 25
- `own_side`, 50 %: hidden_side (found) 148, outline (found) 114, own_side (found) 32, thin_own_side (found) 7, no box (not found) 7, thin_outline (found) 4
- `own_side`, 60 %: hidden_side (found) 113, outline (found) 62, own_side (found) 57, thin_own_side (found) 49, thin_outline (found) 16, no box (not found) 15
- `own_side`, 65 %: thin_own_side (found) 105, hidden_side (found) 63, own_side (found) 47, outline (found) 39, thin_outline (found) 30, no box (not found) 28
- `own_side`, 75 %: thin_own_side (found) 164, no box (not found) 109, thin_outline (found) 25, thin_own_side (not found) 13, own_side (found) 1
- `own_side+centred`, 50 %: hidden_side (found) 148, outline (found) 114, own_side (found) 32, thin_own_side (found) 7, no box (not found) 6, thin_outline (found) 4, centred (found) 1
- `own_side+centred`, 60 %: hidden_side (found) 113, outline (found) 62, own_side (found) 57, thin_own_side (found) 49, thin_outline (found) 16, no box (not found) 15
- `own_side+centred`, 65 %: thin_own_side (found) 105, hidden_side (found) 63, own_side (found) 47, outline (found) 39, thin_outline (found) 30, no box (not found) 28
- `own_side+centred`, 75 %: thin_own_side (found) 164, no box (not found) 109, thin_outline (found) 25, thin_own_side (not found) 13, own_side (found) 1

## Why there is no found box (all pools)

- `centred`: outline_unknown 367, side_unexplained 125, area 50, width 44, slice_not_full 17, nothing 11
- `own_side`: area 50, width 44, outline_unknown 30, slice_not_full 16, box by thin_own_side, not right 13, nothing 11, side_unexplained 8
- `own_side+centred`: area 50, width 44, outline_unknown 30, slice_not_full 16, box by thin_own_side, not right 13, nothing 11, side_unexplained 7
