# Every labeled train frame: boxes that appear or disappear against `start`

Segmented as the eval table does (HOME leave one scene out; every other set the adopted model file); v2 rule against the hand boxes. `right` = matched to a true barrel by the v2 rule; `WRONG` = not. Sheets (white = hand boxes): `sheets_real/` (not committed).

| set | frame | arm | found | false | boxes added | boxes removed |
|---|---|---|---|---|---|---|
| 4A8B_window_black | window_black_occl_03 | close | 0 -> 1 of 2 | 0 -> 0 | blue [272, 151, 373, 270] right | - |

Totals over every train frame: `start` found 146 of 436, false 18; `close` found 147 of 436, false 18

## The occlusion set R1 (`4A8B_window_abpwhite_occlx_*`, train frames), every box of every arm

| shot | `start` found, false | `close` found, false | `start` boxes | `close` boxes |
|---|---|---|---|---|
| 01 | 2 of 2, 0 false | 2 of 2, 0 false | orange [103, 122, 152, 173] right; blue [310, 123, 359, 177] right | orange [103, 122, 152, 173] right; blue [310, 123, 359, 177] right |
| 02 | 1 of 2, 0 false | 1 of 2, 0 false | blue [310, 123, 358, 177] right | blue [310, 123, 358, 177] right |
| 03 | 1 of 2, 0 false | 1 of 2, 0 false | blue [319, 132, 389, 211] right | blue [319, 132, 389, 211] right |
| 04 | 2 of 2, 0 false | 2 of 2, 0 false | orange [101, 121, 151, 172] right; blue [320, 134, 388, 212] right | orange [101, 121, 151, 172] right; blue [320, 134, 388, 212] right |
| 05 | 2 of 2, 0 false | 2 of 2, 0 false | orange [50, 121, 99, 170] right; blue [318, 130, 388, 211] right | orange [50, 121, 99, 170] right; blue [318, 130, 388, 211] right |
| 06 | 1 of 2, 0 false | 1 of 2, 0 false | blue [320, 135, 388, 211] right | blue [320, 135, 388, 211] right |
| 07 | 2 of 2, 0 false | 2 of 2, 0 false | orange [111, 118, 156, 165] right; blue [321, 135, 388, 211] right | orange [111, 118, 156, 165] right; blue [321, 135, 388, 211] right |
| 08 | 2 of 2, 0 false | 2 of 2, 0 false | orange [113, 115, 157, 166] right; blue [321, 135, 388, 212] right | orange [113, 115, 157, 166] right; blue [321, 135, 388, 212] right |
| 09 | 2 of 2, 0 false | 2 of 2, 0 false | blue [107, 117, 153, 168] right; blue [127, 118, 174, 168] right | blue [107, 117, 153, 168] right; blue [127, 118, 174, 168] right |
| 10 | 1 of 2, 0 false | 1 of 2, 0 false | orange [100, 118, 171, 197] right | orange [100, 118, 171, 197] right |
| 11 | 2 of 2, 0 false | 2 of 2, 0 false | blue [87, 136, 170, 230] right; orange [101, 118, 145, 166] right | blue [87, 136, 170, 230] right; orange [101, 118, 145, 166] right |
| 13 | 2 of 2, 0 false | 2 of 2, 0 false | orange [104, 118, 151, 165] right; blue [314, 132, 390, 211] right | orange [104, 118, 151, 165] right; blue [314, 132, 390, 211] right |
| 14 | 1 of 2, 0 false | 1 of 2, 0 false | blue [192, 123, 242, 178] right | blue [192, 123, 242, 178] right |
| 15 | 0 of 0, 1 false | 0 of 0, 1 false | orange [465, 286, 640, 480] WRONG | orange [465, 286, 640, 480] WRONG |
| 17 | 2 of 2, 1 false | 2 of 2, 1 false | blue [0, 128, 16, 185] right; blue [144, 117, 185, 160] right; orange [161, 105, 196, 143] WRONG | blue [0, 128, 16, 185] right; blue [144, 117, 185, 160] right; orange [161, 105, 196, 143] WRONG |
| 18 | 2 of 2, 0 false | 2 of 2, 0 false | orange [104, 119, 151, 166] right; blue [315, 134, 382, 213] right | orange [104, 119, 151, 166] right; blue [315, 134, 382, 213] right |
| 19 | 1 of 2, 0 false | 1 of 2, 0 false | blue [25, 135, 107, 211] right | blue [25, 135, 107, 211] right |
