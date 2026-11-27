# Judge: AB_noguard against baseline: FAIL

```
JUDGE: AB_noguard against baseline

baseline  = today's default (the adopted color model, DetConfig defaults)
candidate = selfcal AB with every guard off (photo check, surround, agreement, flood limit, seed color rule)
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git 8eb94de, 2026-11-26; 168 s in the detectors.

BY PLACE (the verdict is computed on these)
                                            |                     BASELINE                      |                    AB_NOGUARD
                    lights frames brls plcm | found raw  box off    missed wrong 2nd none empty | found raw  box off    missed wrong 2nd none empty
---------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28  0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28  0.0 (0)   1.0 (1)     0   0    1     0
campus_study             1     21   35   35 |  35.0  35  0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35  0.0 (0)   0.0 (0)     0   0    4     0
abp_gray                 1      8   16   16 |  10.0  10  1.0 (1)   5.0 (5)     0   0    0     0 |  15.0  15  1.0 (1)   0.0 (0)     0   0    2     1
home_bathtile            4     28   60   15 |   4.0  16  0.0 (0) 11.0 (44)     0   0    0     0 |   9.8  39  1.5 (6)  3.8 (15)    10   0    8     1
home_glass               5     36   75   15 |  14.8  74  0.2 (1)   0.0 (0)     0   0    3     0 |  14.8  74  0.2 (1)   0.0 (0)     0   0   13     3
home_ottoman             3     21   45   15 |   3.0   9  0.0 (0) 12.0 (36)     0   0    1     0 |  10.0  30  1.3 (4)  3.7 (11)     4   1    8     0
uc_palewood              1      7   15   15 |  13.0  13  0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13  1.0 (1)   1.0 (1)     0   0    5     0
abp_white                1     17   32   32 |  26.0  26  0.0 (0)   6.0 (6)     0   0    0     0 |  27.0  27  0.0 (0)   5.0 (5)     0   0    5     2
---------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 133.8 211  1.2 (2) 37.0 (94)     0   0    5     0 | 152.6 261 5.0 (13) 14.4 (33)    14   1   46     7
---------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                     BASELINE                     |                    AB_NOGUARD
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    1     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    4     0
both_abpgray              1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  15.0  15 1.0 (1)   0.0 (0)     0   0    2     1
lampcool6_bathtile        1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     1
lampcool6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampcool6_ottoman         1      7   15   15 |   3.0   3 0.0 (0) 12.0 (12)     0   0    0     0 |  12.0  12 1.0 (1)   2.0 (2)     0   1    2     0
lampmid3_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |  11.0  11 1.0 (1)   3.0 (3)     2   0    3     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     1
lampmid6_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   7.0   7 4.0 (4)   4.0 (4)     4   0    3     0
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     0
lampmid6_ottoman          1      7   15   15 |   6.0   6 0.0 (0)   9.0 (9)     0   0    0     0 |  12.0  12 1.0 (1)   2.0 (2)     1   0    3     0
lampwarm6_bathtile        1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   6.0   6 1.0 (1)   8.0 (8)     4   0    1     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0
lampwarm6_ottoman         1      7   15   15 |   0.0   0 0.0 (0) 15.0 (15)     0   0    1     0 |   6.0   6 2.0 (2)   7.0 (7)     3   0    3     0
overheaddim_palewood      1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 1.0 (1)   1.0 (1)     0   0    5     0
window_abpwhite           1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  27.0  27 0.0 (0)   5.0 (5)     0   0    5     2
window_glass              1      8   15   15 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0 |  14.0  14 1.0 (1)   0.0 (0)     0   0    8     2
--------------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                     BASELINE                     |                    AB_NOGUARD
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |   2.0   2 0.0 (0) 19.0 (19)     0   0    0     0 |  15.0  15 0.0 (0)   6.0 (6)     1   0    0     0
lampcool6_wood        1     10   21   21 |   2.0   2 2.0 (2) 17.0 (17)     2   0    0     0 |  12.0  12 2.0 (2)   7.0 (7)     3   0    1     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0 |   4.0   4 2.0 (2)   9.0 (9)     2   0    3     1
lampmid3_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     1   0    0     0 |  12.0  12 1.0 (1)   8.0 (8)     4   0    0     0
lampmid6_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |  10.0  10 1.0 (1) 10.0 (10)     4   0    1     0
lampwarm3_wood        1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   7.0   7 0.0 (0) 14.0 (14)     1   0    2     1
lampwarm6_wood        1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     1   0    0     0 |   6.0   6 2.0 (2) 13.0 (13)     1   0    1     0
window_black          1     10   26   26 |   5.0   5 1.0 (1) 20.0 (20)     0   0    0     0 |  16.0  16 3.0 (3)   7.0 (7)     2   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 50 gained, 0 lost, 11 moved between 'box off' and 'missed' (counted per frame)
  + 4A8B_both_abpgray_core_01 #2 blue at [233, 165, 353, 299]: missed -> found
  + 4A8B_both_abpgray_core_01 #4 orange at [408, 125, 472, 192]: missed -> found
  + 4A8B_both_abpgray_edge_01 #1 orange at [291, 127, 356, 197]: missed -> found
  + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: missed -> found
  + 4A8B_both_abpgray_touch_01 #2 blue at [246, 123, 301, 181]: missed -> found
  + 4A8B_lampcool6_bathtile_clutter_01 #3 orange at [410, 108, 442, 141]: missed -> found
  + 4A8B_lampcool6_bathtile_occl_02 #1 orange at [346, 107, 376, 137]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #1 blue at [79, 146, 177, 241]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #2 blue at [288, 116, 333, 163]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #3 orange at [313, 141, 401, 236]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #4 orange at [413, 126, 479, 190]: missed -> found
  + 4A8B_lampcool6_ottoman_edge_01 #1 blue at [0, 141, 43, 229]: missed -> found
  + 4A8B_lampcool6_ottoman_edge_01 #2 orange at [267, 139, 351, 231]: missed -> found
  + 4A8B_lampcool6_ottoman_touch_01 #1 blue at [198, 129, 262, 198]: missed -> found
  + 4A8B_lampmid3_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: missed -> found
  + 4A8B_lampmid3_bathtile_clutter_01 #2 blue at [292, 111, 330, 152]: missed -> found
  + 4A8B_lampmid3_bathtile_clutter_01 #3 orange at [410, 108, 442, 141]: missed -> found
  + 4A8B_lampmid3_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: missed -> found
  + 4A8B_lampmid3_bathtile_core_01 #3 blue at [374, 140, 457, 226]: missed -> found
  + 4A8B_lampmid3_bathtile_core_01 #4 blue at [475, 110, 513, 147]: missed -> found
  + 4A8B_lampmid3_bathtile_edge_01 #2 orange at [279, 122, 331, 178]: missed -> found
  + 4A8B_lampmid3_bathtile_occl_02 #1 orange at [346, 107, 376, 137]: missed -> found
  + 4A8B_lampmid3_bathtile_touch_01 #1 orange at [285, 121, 337, 177]: missed -> found
  + 4A8B_lampmid3_bathtile_touch_01 #2 blue at [337, 123, 390, 180]: missed -> found
  + 4A8B_lampmid6_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: missed -> found
  + 4A8B_lampmid6_bathtile_clutter_01 #2 blue at [292, 111, 330, 152]: missed -> found
  + 4A8B_lampmid6_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: missed -> found
  + 4A8B_lampmid6_bathtile_core_01 #1 orange at [223, 115, 270, 165]: missed -> found
  + 4A8B_lampmid6_bathtile_core_01 #3 blue at [374, 140, 457, 226]: missed -> found
  + 4A8B_lampmid6_bathtile_core_01 #4 blue at [475, 110, 513, 147]: missed -> found
  + 4A8B_lampmid6_ottoman_clutter_01 #1 blue at [79, 146, 177, 241]: missed -> found
  + 4A8B_lampmid6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: missed -> found
  + 4A8B_lampmid6_ottoman_core_01 #3 blue at [273, 113, 316, 160]: missed -> found
  + 4A8B_lampmid6_ottoman_edge_01 #1 blue at [0, 141, 43, 229]: missed -> found
  + 4A8B_lampmid6_ottoman_occl_02 #1 orange at [225, 125, 286, 192]: missed -> found
  + 4A8B_lampmid6_ottoman_touch_01 #1 blue at [198, 129, 262, 198]: missed -> found
  + 4A8B_lampwarm6_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: missed -> found
  + 4A8B_lampwarm6_bathtile_core_01 #1 orange at [223, 115, 270, 165]: missed -> found
  + 4A8B_lampwarm6_bathtile_core_01 #3 blue at [374, 140, 457, 226]: missed -> found
  + 4A8B_lampwarm6_bathtile_core_01 #4 blue at [475, 110, 513, 147]: missed -> found
  + 4A8B_lampwarm6_bathtile_edge_01 #2 orange at [279, 122, 331, 178]: missed -> found
  + 4A8B_lampwarm6_ottoman_clutter_01 #1 blue at [79, 146, 177, 241]: missed -> found
  + 4A8B_lampwarm6_ottoman_clutter_01 #3 orange at [313, 141, 401, 236]: missed -> found
  + 4A8B_lampwarm6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: missed -> found
  + 4A8B_lampwarm6_ottoman_core_01 #4 orange at [415, 126, 479, 191]: missed -> found
  + 4A8B_lampwarm6_ottoman_edge_01 #2 orange at [267, 139, 351, 231]: missed -> found
  + 4A8B_lampwarm6_ottoman_touch_01 #3 orange at [324, 128, 389, 199]: missed -> found
  + 4A8B_window_abpwhite_occlx_06 #1 orange at [133, 115, 181, 160]: missed -> found
  ~ 4A8B_lampcool6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: missed -> off
  ~ 4A8B_lampmid3_bathtile_core_01 #1 orange at [223, 115, 270, 165]: missed -> off
  ~ 4A8B_lampmid6_bathtile_edge_01 #1 blue at [0, 127, 31, 196]: missed -> off
  ~ 4A8B_lampmid6_bathtile_edge_01 #2 orange at [279, 122, 331, 178]: missed -> off
  ~ 4A8B_lampmid6_bathtile_touch_01 #1 orange at [285, 121, 337, 177]: missed -> off
  ~ 4A8B_lampmid6_bathtile_touch_01 #2 blue at [337, 123, 390, 180]: missed -> off
  ~ 4A8B_lampmid6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: missed -> off
  ~ 4A8B_lampwarm6_bathtile_touch_01 #1 orange at [285, 121, 337, 177]: missed -> off
  ~ 4A8B_lampwarm6_ottoman_clutter_01 #2 blue at [288, 116, 333, 163]: missed -> off
  ~ 4A8B_lampwarm6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: missed -> off
  ~ 4A8B_overheaddim_palewood_occl_02 #1 orange at [344, 115, 388, 162]: missed -> off
  report only: 69 gained, 0 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 37 frame(s)
  4A8B_window_light_core_03: nothing 0 -> 1; now [('blue', (571, 101, 608, 141))]
  4A8B_campus_light_hand_02: nothing 0 -> 2; now [('orange', (471, 130, 538, 192)), ('orange', (495, 91, 513, 112))]
  4A8B_campus_light_plain_01: nothing 0 -> 1; now [('blue', (79, 115, 129, 167))]
  4A8B_campus_light_touch_02: nothing 0 -> 1; now [('blue', (255, 105, 289, 145))]
  4A8B_both_abpgray_clutter_01: nothing 0 -> 1; now [('orange', (85, 253, 273, 480))]
  4A8B_both_abpgray_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('blue', (446, 100, 480, 133))]
  4A8B_lampcool6_bathtile_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('orange', (224, 112, 272, 168))]
  4A8B_lampcool6_ottoman_clutter_01: second 0 -> 1, nothing 0 -> 1; now [('blue', (282, 94, 305, 125)), ('blue', (295, 101, 324, 136))]
  4A8B_lampcool6_ottoman_occl_02: nothing 0 -> 1; now [('blue', (556, 152, 640, 258))]
  4A8B_lampmid3_bathtile_close_01: nothing 0 -> 2; now [('orange', (200, 140, 294, 241)), ('orange', (247, 157, 374, 272))]
  4A8B_lampmid3_bathtile_touch_01: wrong color 0 -> 2, nothing 0 -> 1; now [('orange', (142, 94, 162, 118)), ('orange', (341, 109, 388, 152)), ('orange', (396, 109, 443, 151))]
  4A8B_lampmid3_glass_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('orange', (560, 123, 609, 168))]
  4A8B_lampmid6_bathtile_core_01: wrong color 0 -> 1; now [('orange', (478, 101, 514, 133))]
  4A8B_lampmid6_bathtile_edge_01: wrong color 0 -> 1; now [('orange', (0, 115, 36, 173))]
  4A8B_lampmid6_bathtile_occl_02: wrong color 0 -> 1, nothing 0 -> 2; now [('blue', (338, 110, 373, 149)), ('orange', (375, 96, 403, 123)), ('orange', (381, 91, 402, 109))]
  4A8B_lampmid6_bathtile_touch_01: wrong color 0 -> 1, nothing 0 -> 1; now [('orange', (394, 112, 443, 164)), ('orange', (435, 99, 465, 131))]
  4A8B_lampmid6_glass_clutter_01: nothing 1 -> 2; now [('blue', (485, 98, 515, 127)), ('orange', (554, 117, 604, 171))]
  4A8B_lampmid6_ottoman_clutter_01: wrong color 0 -> 1, nothing 0 -> 1; now [('blue', (449, 141, 532, 220)), ('blue', (538, 124, 597, 187))]
  4A8B_lampmid6_ottoman_occl_02: nothing 0 -> 2; now [('blue', (465, 145, 547, 263)), ('blue', (547, 145, 628, 263))]
  4A8B_lampwarm6_bathtile_clutter_01: wrong color 0 -> 1; now [('blue', (413, 99, 441, 129))]
  4A8B_lampwarm6_bathtile_core_01: wrong color 0 -> 3; now [('orange', (355, 148, 443, 236)), ('orange', (377, 126, 452, 200)), ('orange', (476, 101, 512, 135))]
  4A8B_lampwarm6_bathtile_occl_02: nothing 0 -> 1; now [('orange', (209, 291, 382, 480))]
  4A8B_lampwarm6_ottoman_clutter_01: wrong color 0 -> 1; now [('orange', (307, 120, 362, 176))]
  4A8B_lampwarm6_ottoman_core_01: wrong color 0 -> 1; now [('orange', (166, 248, 282, 480)), ('blue', (409, 133, 480, 203))]
  4A8B_lampwarm6_ottoman_occl_02: nothing 0 -> 2; now [('blue', (465, 137, 547, 249)), ('blue', (547, 152, 640, 268))]
  4A8B_lampwarm6_ottoman_touch_01: wrong color 0 -> 1; now [('blue', (320, 136, 396, 210))]
  4A8B_overheaddim_palewood_clutter_01: nothing 0 -> 1; now [('blue', (353, 111, 391, 145))]
  4A8B_overheaddim_palewood_edge_01: nothing 0 -> 1; now [('orange', (549, 94, 570, 121))]
  4A8B_overheaddim_palewood_occl_02: nothing 0 -> 2; now [('orange', (33, 124, 96, 197)), ('blue', (35, 140, 102, 193))]
  4A8B_window_abpwhite_occlx_09: nothing 0 -> 2; now [('orange', (79, 280, 303, 480)), ('blue', (176, 92, 198, 119))]
  4A8B_window_abpwhite_occlx_10: nothing 0 -> 1; now [('blue', (172, 94, 192, 116))]
  4A8B_window_abpwhite_occlx_15 [empty frame with clutter]: nothing 0 -> 2; now [('orange', (113, 286, 324, 480)), ('orange', (328, 138, 406, 203))]
  4A8B_window_glass_clutter_01: nothing 0 -> 2; now [('blue', (0, 283, 321, 480)), ('blue', (321, 296, 640, 480))]
  4A8B_window_glass_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('blue', (537, 131, 599, 188))]
  4A8B_window_glass_occl_02: nothing 0 -> 3; now [('blue', (0, 304, 416, 480)), ('blue', (54, 105, 94, 142)), ('blue', (424, 308, 640, 480))]
  4A8B_window_glass_occlx_16 [empty frame with clutter]: nothing 0 -> 1; now [('blue', (72, 115, 108, 162))]
  4A8B_window_glass_touch_01: nothing 0 -> 1; now [('orange', (59, 99, 90, 133))]

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [BETTER] found, the ordinary conditions together: 133.8 -> 152.6 of 172 placements (+18.8; counted per frame 211 -> 261 of 307). Better above +4.0,
      worse below -10.9.
  [within the noise] found, place by place: abp_gray +5.0 of 16 (margin 6.0); home_bathtile +5.8 of 15 (margin 1.2); home_ottoman +7.0 of 15 (margin
      2.3); abp_white +1.0 of 32 (margin 1.0).
  [WORSE] boxes that are not on their barrel: 1.9 -> 29.2 counted once per arrangement (+27.3; per frame: on nothing 5 -> 46, second box 0 -> 1, wrong
      color 0 -> 14). Worse above +1.9, better below -1.0.
  [WORSE] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 4.7 per arrangement (margin 1.0).

VERDICT: FAIL. worse than the baseline by more than the noise in: boxes that are not on their barrel; boxes on empty frames.
```
