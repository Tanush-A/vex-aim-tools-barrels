# Judge: C_both6_7 against baseline: FAIL

```
JUDGE: C_both6_7 against baseline

baseline  = today's default (the adopted color model, DetConfig defaults)
candidate = pc:6,7,pred: partner-conditioned: stripe direction level 6 (anything), body direction level 7 (anything), edges 'pred'; then
    detector.detect with DetConfig defaults
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git c648d95, 2026-11-26; 80 s in the detectors.

BY PLACE (the verdict is computed on these)
                                            |                     BASELINE                     |                    C_BOTH6_7
                    lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
-------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  26.0  26 0.0 (0)   3.0 (3)     3   0    0     0
campus_study             1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  34.0  34 0.0 (0)   1.0 (1)     2   0    5     3
abp_gray                 1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  16.0  16 0.0 (0)   0.0 (0)     1   0    2     1
home_bathtile            4     28   60   15 |   4.0  16 0.0 (0) 11.0 (44)     0   0    0     0 |  12.8  51 0.0 (0)   2.2 (9)     2   1   12     5
home_glass               5     36   75   15 |  14.8  74 0.2 (1)   0.0 (0)     0   0    3     0 |  14.6  73 0.2 (1)   0.2 (1)     0   0   21     9
home_ottoman             3     21   45   15 |   3.0   9 0.0 (0) 12.0 (36)     0   0    1     0 |  10.7  32 1.3 (4)   3.0 (9)    15   0   11     4
uc_palewood              1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  12.0  12 0.0 (0)   3.0 (3)     2   0    6     3
abp_white                1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  25.0  25 0.0 (0)   7.0 (7)     3   0    7     4
-------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 133.8 211 1.2 (2) 37.0 (94)     0   0    5     0 | 151.0 269 1.5 (5) 19.5 (33)    28   1   64    29
-------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                     BASELINE                     |                    C_BOTH6_7
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  26.0  26 0.0 (0)   3.0 (3)     3   0    0     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  34.0  34 0.0 (0)   1.0 (1)     2   0    5     3
both_abpgray              1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  16.0  16 0.0 (0)   0.0 (0)     1   0    2     1
lampcool6_bathtile        1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0 |  15.0  15 0.0 (0)   0.0 (0)     1   0    4     4
lampcool6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    7     2
lampcool6_ottoman         1      7   15   15 |   3.0   3 0.0 (0) 12.0 (12)     0   0    0     0 |  12.0  12 1.0 (1)   2.0 (2)     2   0    3     1
lampmid3_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |  13.0  13 0.0 (0)   2.0 (2)     1   1    0     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    4     3
lampmid6_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    2     1
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     0
lampmid6_ottoman          1      7   15   15 |   6.0   6 0.0 (0)   9.0 (9)     0   0    0     0 |  10.0  10 2.0 (2)   3.0 (3)     8   0    5     2
lampwarm6_bathtile        1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |  10.0  10 0.0 (0)   5.0 (5)     0   0    6     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  14.0  14 0.0 (0)   1.0 (1)     0   0    3     0
lampwarm6_ottoman         1      7   15   15 |   0.0   0 0.0 (0) 15.0 (15)     0   0    1     0 |  10.0  10 1.0 (1)   4.0 (4)     5   0    3     1
overheaddim_palewood      1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  12.0  12 0.0 (0)   3.0 (3)     2   0    6     3
window_abpwhite           1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  25.0  25 0.0 (0)   7.0 (7)     3   0    7     4
window_glass              1      8   15   15 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0 |  14.0  14 1.0 (1)   0.0 (0)     0   0    5     4
--------------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                     BASELINE                     |                    C_BOTH6_7
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |   2.0   2 0.0 (0) 19.0 (19)     0   0    0     0 |  14.0  14 2.0 (2)   5.0 (5)     3   0    0     0
lampcool6_wood        1     10   21   21 |   2.0   2 2.0 (2) 17.0 (17)     2   0    0     0 |  14.0  14 2.0 (2)   5.0 (5)     7   0    0     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0 |   5.0   5 0.0 (0) 10.0 (10)     3   0    4     1
lampmid3_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     1   0    0     0 |  15.0  15 0.0 (0)   6.0 (6)     1   0    0     0
lampmid6_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |  10.0  10 3.0 (3)   8.0 (8)     0   0    2     0
lampwarm3_wood        1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |  11.0  11 1.0 (1)   9.0 (9)     0   0    0     0
lampwarm6_wood        1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     1   0    0     0 |   7.0   7 1.0 (1) 13.0 (13)     3   0    1     0
window_black          1     10   26   26 |   5.0   5 1.0 (1) 20.0 (20)     0   0    0     0 |  12.0  12 3.0 (3) 11.0 (11)    10   0    2     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 66 gained, 8 lost, 4 moved between 'box off' and 'missed' (counted per frame)
  + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found
  + 4A8B_both_abpgray_core_01 #2 blue at [233, 165, 353, 299]: missed -> found
  + 4A8B_both_abpgray_core_01 #4 orange at [408, 125, 472, 192]: missed -> found
  + 4A8B_both_abpgray_edge_01 #1 orange at [291, 127, 356, 197]: missed -> found
  + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: missed -> found
  + 4A8B_both_abpgray_touch_01 #2 blue at [246, 123, 301, 181]: missed -> found
  + 4A8B_lampcool6_bathtile_clutter_01 #3 orange at [410, 108, 442, 141]: missed -> found
  + 4A8B_lampcool6_bathtile_occl_02 #1 orange at [346, 107, 376, 137]: missed -> found
  + 4A8B_lampcool6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #1 blue at [79, 146, 177, 241]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #2 blue at [288, 116, 333, 163]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #3 orange at [313, 141, 401, 236]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #4 orange at [413, 126, 479, 190]: missed -> found
  + 4A8B_lampcool6_ottoman_edge_01 #1 blue at [0, 141, 43, 229]: missed -> found
  + 4A8B_lampcool6_ottoman_edge_01 #2 orange at [267, 139, 351, 231]: missed -> found
  + 4A8B_lampmid3_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: missed -> found
  + 4A8B_lampmid3_bathtile_clutter_01 #2 blue at [292, 111, 330, 152]: missed -> found
  + 4A8B_lampmid3_bathtile_clutter_01 #3 orange at [410, 108, 442, 141]: missed -> found
  + 4A8B_lampmid3_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: missed -> found
  + 4A8B_lampmid3_bathtile_core_01 #1 orange at [223, 115, 270, 165]: missed -> found
  + 4A8B_lampmid3_bathtile_core_01 #2 orange at [328, 106, 358, 138]: missed -> found
  + 4A8B_lampmid3_bathtile_core_01 #3 blue at [374, 140, 457, 226]: missed -> found
  + 4A8B_lampmid3_bathtile_core_01 #4 blue at [475, 110, 513, 147]: missed -> found
  + 4A8B_lampmid3_bathtile_edge_01 #1 blue at [0, 127, 31, 196]: missed -> found
  + 4A8B_lampmid3_bathtile_edge_01 #2 orange at [279, 122, 331, 178]: missed -> found
  + 4A8B_lampmid3_bathtile_occl_02 #1 orange at [346, 107, 376, 137]: missed -> found
  + 4A8B_lampmid3_bathtile_touch_01 #1 orange at [285, 121, 337, 177]: missed -> found
  + 4A8B_lampmid6_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: missed -> found
  + 4A8B_lampmid6_bathtile_clutter_01 #2 blue at [292, 111, 330, 152]: missed -> found
  + 4A8B_lampmid6_bathtile_clutter_01 #3 orange at [410, 108, 442, 141]: missed -> found
  + 4A8B_lampmid6_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: missed -> found
  + 4A8B_lampmid6_bathtile_core_01 #1 orange at [223, 115, 270, 165]: missed -> found
  + 4A8B_lampmid6_bathtile_core_01 #2 orange at [328, 106, 358, 138]: missed -> found
  + 4A8B_lampmid6_bathtile_core_01 #3 blue at [374, 140, 457, 226]: missed -> found
  + 4A8B_lampmid6_bathtile_core_01 #4 blue at [475, 110, 513, 147]: missed -> found
  + 4A8B_lampmid6_bathtile_edge_01 #1 blue at [0, 127, 31, 196]: missed -> found
  + 4A8B_lampmid6_bathtile_edge_01 #2 orange at [279, 122, 331, 178]: missed -> found
  + 4A8B_lampmid6_bathtile_occl_02 #1 orange at [346, 107, 376, 137]: missed -> found
  + 4A8B_lampmid6_bathtile_touch_01 #1 orange at [285, 121, 337, 177]: missed -> found
  + 4A8B_lampmid6_ottoman_clutter_01 #1 blue at [79, 146, 177, 241]: missed -> found
  + 4A8B_lampmid6_ottoman_clutter_01 #2 blue at [288, 116, 333, 163]: missed -> found
  + 4A8B_lampmid6_ottoman_core_01 #3 blue at [273, 113, 316, 160]: missed -> found
  + 4A8B_lampmid6_ottoman_touch_01 #1 blue at [198, 129, 262, 198]: missed -> found
  + 4A8B_lampwarm6_bathtile_clutter_01 #3 orange at [410, 108, 442, 141]: missed -> found
  + 4A8B_lampwarm6_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: missed -> found
  + 4A8B_lampwarm6_bathtile_core_01 #1 orange at [223, 115, 270, 165]: missed -> found
  + 4A8B_lampwarm6_bathtile_core_01 #3 blue at [374, 140, 457, 226]: missed -> found
  + 4A8B_lampwarm6_bathtile_core_01 #4 blue at [475, 110, 513, 147]: missed -> found
  + 4A8B_lampwarm6_bathtile_edge_01 #1 blue at [0, 127, 31, 196]: missed -> found
  + 4A8B_lampwarm6_bathtile_edge_01 #2 orange at [279, 122, 331, 178]: missed -> found
  + 4A8B_lampwarm6_bathtile_occl_02 #1 orange at [346, 107, 376, 137]: missed -> found
  + 4A8B_lampwarm6_bathtile_touch_01 #1 orange at [285, 121, 337, 177]: missed -> found
  + 4A8B_lampwarm6_ottoman_clutter_01 #1 blue at [79, 146, 177, 241]: missed -> found
  + 4A8B_lampwarm6_ottoman_clutter_01 #2 blue at [288, 116, 333, 163]: missed -> found
  + 4A8B_lampwarm6_ottoman_clutter_01 #3 orange at [313, 141, 401, 236]: missed -> found
  + 4A8B_lampwarm6_ottoman_core_01 #1 blue at [79, 133, 155, 209]: missed -> found
  + 4A8B_lampwarm6_ottoman_core_01 #3 blue at [273, 113, 316, 160]: missed -> found
  + 4A8B_lampwarm6_ottoman_core_01 #4 orange at [415, 126, 479, 191]: missed -> found
  + 4A8B_lampwarm6_ottoman_edge_01 #2 orange at [267, 139, 351, 231]: missed -> found
  + 4A8B_lampwarm6_ottoman_occl_02 #1 orange at [225, 125, 286, 192]: missed -> found
  + 4A8B_lampwarm6_ottoman_touch_01 #1 blue at [198, 129, 262, 198]: missed -> found
  + 4A8B_lampwarm6_ottoman_touch_01 #3 orange at [324, 128, 389, 199]: missed -> found
  + 4A8B_window_abpwhite_occlx_06 #1 orange at [133, 115, 181, 160]: missed -> found
  + 4A8B_window_abpwhite_occlx_14 #1 orange at [0, 120, 45, 179]: missed -> found
  - 4A8B_window_light_cluster_01 #1 orange at [313, 115, 356, 164]: found -> missed
  - 4A8B_window_light_occl_02 #2 orange at [395, 114, 441, 158]: found -> missed
  - 4A8B_campus_light_occl_02 #1 blue at [275, 123, 328, 180]: found -> missed
  - 4A8B_lampwarm6_glass_core_01 #1 orange at [143, 112, 182, 152]: found -> missed
  - 4A8B_overheaddim_palewood_clutter_01 #1 blue at [136, 118, 187, 169]: found -> missed
  - 4A8B_window_abpwhite_occlx_04 #1 orange at [98, 119, 151, 174]: found -> missed
  - 4A8B_window_abpwhite_occlx_08 #1 orange at [111, 114, 160, 164]: found -> missed
  - 4A8B_window_abpwhite_occlx_09 #1 blue at [106, 114, 152, 164]: found -> missed
  ~ 4A8B_lampcool6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: missed -> off
  ~ 4A8B_lampmid6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: missed -> off
  ~ 4A8B_lampmid6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: missed -> off
  ~ 4A8B_lampwarm6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: missed -> off
  report only: 76 gained, 1 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 56 frame(s)
  4A8B_window_light_cluster_01: wrong color 0 -> 2; now [('blue', (314, 105, 348, 147)), ('blue', (366, 103, 393, 142))]
  4A8B_window_light_occl_02: wrong color 0 -> 1; now [('blue', (399, 105, 439, 142))]
  4A8B_campus_light_core_01: wrong color 0 -> 1; now [('blue', (247, 101, 279, 133))]
  4A8B_campus_light_held_01: nothing 0 -> 1; now [('blue', (419, 108, 464, 162))]
  4A8B_campus_light_neg_04 [empty frame, clean]: nothing 0 -> 2; now [('blue', (140, 117, 184, 160)), ('blue', (224, 110, 272, 154))]
  4A8B_campus_light_neg_05 [empty frame, clean]: nothing 0 -> 1; now [('blue', (420, 107, 465, 162))]
  4A8B_campus_light_occl_02: wrong color 0 -> 1; now [('orange', (246, 128, 311, 198))]
  4A8B_campus_light_touch_02: nothing 0 -> 1; now [('blue', (254, 104, 286, 145))]
  4A8B_both_abpgray_clutter_01: wrong color 0 -> 1; now [('blue', (207, 105, 244, 142))]
  4A8B_both_abpgray_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('blue', (446, 101, 475, 132))]
  4A8B_both_abpgray_occl_02: nothing 0 -> 1; now [('blue', (491, 120, 534, 177))]
  4A8B_lampcool6_bathtile_neg_02 [empty frame with clutter]: nothing 0 -> 4; now [('blue', (224, 125, 272, 188)), ('orange', (225, 113, 272, 164)), ('blue', (301, 96, 323, 121)), ('orange', (315, 100, 342, 131))]
  4A8B_lampcool6_bathtile_touch_01: wrong color 0 -> 1; now [('orange', (399, 114, 442, 163))]
  4A8B_lampcool6_glass_clutter_01: nothing 0 -> 4; now [('blue', (88, 100, 116, 131)), ('blue', (97, 104, 128, 137)), ('orange', (461, 98, 487, 127)), ('blue', (491, 97, 512, 124))]
  4A8B_lampcool6_glass_neg_02 [empty frame with clutter]: nothing 0 -> 2; now [('orange', (556, 112, 607, 172)), ('orange', (567, 130, 634, 166))]
  4A8B_lampcool6_glass_occl_02: nothing 0 -> 1; now [('orange', (560, 118, 611, 172))]
  4A8B_lampcool6_ottoman_clutter_01: wrong color 0 -> 1, nothing 0 -> 1; now [('blue', (456, 138, 543, 230)), ('blue', (536, 115, 576, 167))]
  4A8B_lampcool6_ottoman_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('blue', (99, 137, 175, 219))]
  4A8B_lampcool6_ottoman_occl_02: nothing 0 -> 1; now [('blue', (542, 149, 637, 250))]
  4A8B_lampcool6_ottoman_touch_01: wrong color 0 -> 1; now [('blue', (325, 136, 401, 220))]
  4A8B_lampmid3_bathtile_clutter_01: wrong color 0 -> 1; now [('orange', (80, 114, 127, 165))]
  4A8B_lampmid3_bathtile_core_01: second 0 -> 1; now [('orange', (218, 104, 256, 145))]
  4A8B_lampmid3_glass_neg_02 [empty frame with clutter]: nothing 0 -> 3; now [('blue', (514, 100, 542, 129)), ('orange', (537, 100, 564, 129)), ('orange', (556, 117, 607, 171))]
  4A8B_lampmid6_bathtile_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('blue', (426, 112, 469, 158))]
  4A8B_lampmid6_bathtile_occl_02: nothing 0 -> 1; now [('orange', (369, 102, 399, 132))]
  4A8B_lampmid6_glass_clutter_01: nothing 1 -> 2; now [('blue', (485, 98, 513, 125)), ('orange', (554, 117, 604, 171))]
  4A8B_lampmid6_ottoman_clutter_01: wrong color 0 -> 2, nothing 0 -> 1; now [('orange', (87, 132, 144, 194)), ('blue', (305, 152, 403, 260)), ('blue', (437, 141, 520, 230))]
  4A8B_lampmid6_ottoman_core_01: wrong color 0 -> 2; now [('blue', (416, 133, 477, 211)), ('blue', (416, 116, 463, 167))]
  4A8B_lampmid6_ottoman_edge_01: wrong color 0 -> 1; now [('blue', (272, 150, 367, 256))]
  4A8B_lampmid6_ottoman_neg_02 [empty frame with clutter]: nothing 0 -> 2; now [('blue', (223, 113, 268, 162)), ('orange', (562, 148, 640, 247))]
  4A8B_lampmid6_ottoman_occl_02: nothing 0 -> 2; now [('blue', (465, 148, 565, 259)), ('blue', (517, 148, 628, 259))]
  4A8B_lampmid6_ottoman_touch_01: wrong color 0 -> 3; now [('orange', (207, 117, 260, 176)), ('orange', (268, 117, 320, 176)), ('blue', (326, 136, 402, 220))]
  4A8B_lampwarm6_bathtile_clutter_01: nothing 0 -> 2; now [('orange', (317, 98, 341, 121)), ('blue', (321, 92, 337, 112))]
  4A8B_lampwarm6_bathtile_core_01: nothing 0 -> 1; now [('orange', (465, 101, 495, 134))]
  4A8B_lampwarm6_bathtile_occl_02: nothing 0 -> 3; now [('orange', (169, 93, 193, 115)), ('orange', (298, 105, 327, 133)), ('blue', (301, 96, 324, 121))]
  4A8B_lampwarm6_glass_occl_02: nothing 0 -> 2; now [('blue', (355, 107, 392, 146)), ('orange', (571, 123, 621, 167))]
  4A8B_lampwarm6_ottoman_clutter_01: wrong color 0 -> 1; now [('blue', (315, 152, 398, 259))]
  4A8B_lampwarm6_ottoman_core_01: wrong color 0 -> 2; now [('blue', (147, 183, 296, 338)), ('blue', (177, 90, 192, 108)), ('blue', (408, 133, 479, 211))]
  4A8B_lampwarm6_ottoman_edge_01: wrong color 0 -> 1; now [('blue', (260, 151, 357, 255))]
  4A8B_lampwarm6_ottoman_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('blue', (224, 113, 269, 162))]
  4A8B_lampwarm6_ottoman_occl_02: nothing 0 -> 1; now [('blue', (465, 148, 553, 248))]
  4A8B_lampwarm6_ottoman_touch_01: wrong color 0 -> 1; now [('blue', (324, 119, 375, 176))]
  4A8B_overheaddim_palewood_clutter_01: wrong color 0 -> 1; now [('orange', (139, 103, 183, 148))]
  4A8B_overheaddim_palewood_edge_01: wrong color 0 -> 1; now [('orange', (0, 116, 29, 168))]
  4A8B_overheaddim_palewood_neg_02 [empty frame with clutter]: nothing 0 -> 3; now [('orange', (187, 123, 245, 186)), ('orange', (330, 123, 392, 190)), ('orange', (437, 152, 536, 263))]
  4A8B_overheaddim_palewood_occl_02: nothing 0 -> 2; now [('blue', (44, 129, 111, 202)), ('orange', (517, 99, 543, 131))]
  4A8B_window_abpwhite_occlx_04: wrong color 0 -> 1; now [('blue', (88, 125, 149, 191))]
  4A8B_window_abpwhite_occlx_08: wrong color 0 -> 1; now [('blue', (107, 122, 163, 182))]
  4A8B_window_abpwhite_occlx_09: nothing 0 -> 1; now [('blue', (170, 94, 193, 115))]
  4A8B_window_abpwhite_occlx_13: nothing 0 -> 1; now [('blue', (401, 119, 452, 174))]
  4A8B_window_abpwhite_occlx_14: wrong color 0 -> 1; now [('blue', (0, 127, 43, 196))]
  4A8B_window_abpwhite_occlx_15 [empty frame with clutter]: nothing 0 -> 4; now [('orange', (247, 141, 342, 230)), ('blue', (391, 177, 530, 323)), ('blue', (401, 118, 458, 173)), ('blue', (456, 175, 640, 380))]
  4A8B_window_abpwhite_occlx_17: nothing 0 -> 1; now [('blue', (170, 94, 191, 117))]
  4A8B_window_glass_close_01: nothing 0 -> 1; now [('orange', (59, 102, 86, 136))]
  4A8B_window_glass_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('orange', (308, 94, 329, 117))]
  4A8B_window_glass_occlx_16 [empty frame with clutter]: nothing 0 -> 3; now [('blue', (212, 129, 278, 200)), ('blue', (219, 112, 269, 166)), ('orange', (462, 98, 488, 127))]

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [BETTER] found, the ordinary conditions together: 133.8 -> 151.0 of 172 placements (+17.2; counted per frame 211 -> 269 of 307). Better above +4.0,
      worse below -10.9.
  [WORSE] found, place by place: home_white -2.0 of 29 (margin 1.0, WORSE); campus_study -1.0 of 35 (margin 1.0); abp_gray +6.0 of 16 (margin 6.0);
      home_bathtile +8.8 of 15 (margin 1.2); home_glass -0.2 of 15 (margin 1.0); home_ottoman +7.7 of 15 (margin 2.3); uc_palewood -1.0 of 15 (margin
      1.0); abp_white -1.0 of 32 (margin 1.0).
  [WORSE] boxes that are not on their barrel: 1.9 -> 50.0 counted once per arrangement (+48.1; per frame: on nothing 5 -> 64, second box 0 -> 1, wrong
      color 0 -> 28). Worse above +1.9, better below -1.0.
  [WORSE] boxes on empty frames: on clean ones 0 -> 3 (margin 0: none is allowed); on ones with clutter 0.0 -> 14.8 per arrangement (margin 1.0).

VERDICT: FAIL. worse than the baseline by more than the noise in: found at home_white; boxes that are not on their barrel; boxes on empty frames.
```
