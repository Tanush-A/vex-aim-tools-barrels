# Judge: cal_otherplace_mid against today: FAIL

```
JUDGE: cal_otherplace_mid against today

baseline  = today's default (the adopted color model, DetConfig defaults)
candidate = CONTROL: the setting of the calibration frame of ANOTHER place (the next place by name, its first condition)
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git 8b81375, 2026-11-26; 32 s in the detectors.

BY PLACE (the verdict is computed on these)
                                            |                       TODAY                        |                 CAL_OTHERPLACE_MID
                    lights frames brls plcm | found raw  box off     missed wrong 2nd none empty | found raw  box off     missed wrong 2nd none empty
-----------------------------------------------------------------------------------------------------------------------------------------------------
abp_gray                 1      8   16   16 |  10.0  10  1.0 (1)    5.0 (5)     0   0    0     0 |   2.0   2  0.0 (0)  14.0 (14)     0   0    0     0
campus_study             1     21   35   35 |  35.0  35  0.0 (0)    0.0 (0)     0   0    0     0 |  30.0  30  0.0 (0)    5.0 (5)     0   0    0     0
home_bathtile            4     28   60   15 |   4.0  16  0.0 (0)  11.0 (44)     0   0    0     0 |   2.8  11  0.2 (1)  12.0 (48)     0   0    0     0
home_glass               5     36   75   15 |  14.8  74  0.2 (1)    0.0 (0)     0   0    3     0 |  13.2  66  1.0 (5)    0.8 (4)     2   0   19     7
home_ottoman             3     21   45   15 |   3.0   9  0.0 (0)  12.0 (36)     0   0    1     0 |   0.0   0  0.0 (0)  15.0 (45)     0   0    0     0
uc_palewood              1      7   15   15 |  13.0  13  0.0 (0)    2.0 (2)     0   0    1     0 |   8.0   8  0.0 (0)    7.0 (7)     1   0    0     0
abp_white                1     17   32   32 |  26.0  26  0.0 (0)    6.0 (6)     0   0    0     0 |   1.0   1  3.0 (3)  28.0 (28)     0   0    0     0
home_white               1     16   29   29 |  28.0  28  0.0 (0)    1.0 (1)     0   0    0     0 |  24.0  24  1.0 (1)    4.0 (4)     0   0    0     0
-----------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 133.8 211  1.2 (2)  37.0 (94)     0   0    5     0 |  80.9 142 5.2 (10) 85.8 (155)     3   0   19     7
-----------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                      TODAY                       |                CAL_OTHERPLACE_MID
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
both_abpgray              1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |   2.0   2 0.0 (0) 14.0 (14)     0   0    0     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  30.0  30 0.0 (0)   5.0 (5)     0   0    0     0
lampcool6_bathtile        1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0 |   9.0   9 1.0 (1)   5.0 (5)     0   0    0     0
lampcool6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    4     1
lampcool6_ottoman         1      7   15   15 |   3.0   3 0.0 (0) 12.0 (12)     0   0    0     0 |   0.0   0 0.0 (0) 15.0 (15)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   0.0   0 0.0 (0) 15.0 (15)     0   0    0     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  12.0  12 2.0 (2)   1.0 (1)     1   0    4     1
lampmid6_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     1   0    6     2
lampmid6_ottoman          1      7   15   15 |   6.0   6 0.0 (0)   9.0 (9)     0   0    0     0 |   0.0   0 0.0 (0) 15.0 (15)     0   0    0     0
lampwarm6_bathtile        1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  12.0  12 3.0 (3)   0.0 (0)     0   0    3     1
lampwarm6_ottoman         1      7   15   15 |   0.0   0 0.0 (0) 15.0 (15)     0   0    1     0 |   0.0   0 0.0 (0) 15.0 (15)     0   0    0     0
overheaddim_palewood      1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |   8.0   8 0.0 (0)   7.0 (7)     1   0    0     0
window_abpwhite           1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |   1.0   1 3.0 (3) 28.0 (28)     0   0    0     0
window_glass              1      8   15   15 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0 |  14.0  14 0.0 (0)   1.0 (1)     0   0    2     2
window_light              1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  24.0  24 1.0 (1)   4.0 (4)     0   0    0     0
--------------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 1 gained, 70 lost, 1 moved between 'box off' and 'missed' (counted per frame)
  + 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found
  - 4A8B_both_abpgray_clutter_01 #1 blue at [34, 132, 110, 203]: found -> missed
  - 4A8B_both_abpgray_clutter_01 #3 blue at [365, 123, 422, 182]: found -> missed
  - 4A8B_both_abpgray_clutter_01 #4 orange at [506, 124, 579, 190]: found -> missed
  - 4A8B_both_abpgray_core_01 #1 orange at [134, 125, 194, 186]: found -> missed
  - 4A8B_both_abpgray_core_01 #3 blue at [372, 109, 408, 147]: found -> missed
  - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> missed
  - 4A8B_both_abpgray_occl_02 #1 blue at [366, 123, 422, 181]: found -> missed
  - 4A8B_both_abpgray_touch_01 #3 blue at [299, 122, 352, 179]: found -> missed
  - 4A8B_campus_light_far_01 #4 orange at [379, 113, 414, 150]: found -> missed
  - 4A8B_campus_light_occl_02 #1 blue at [275, 123, 328, 180]: found -> missed
  - 4A8B_campus_light_plain_02 #1 blue at [82, 131, 153, 204]: found -> missed
  - 4A8B_campus_light_room_01 #1 blue at [64, 123, 125, 181]: found -> missed
  - 4A8B_campus_light_room_03 #1 blue at [179, 112, 216, 153]: found -> missed
  - 4A8B_lampcool6_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: found -> missed
  - 4A8B_lampcool6_bathtile_core_01 #2 orange at [328, 106, 358, 138]: found -> missed
  - 4A8B_lampcool6_bathtile_core_01 #4 blue at [475, 110, 513, 147]: found -> missed
  - 4A8B_lampcool6_bathtile_edge_01 #1 blue at [0, 127, 31, 196]: found -> off
  - 4A8B_lampcool6_glass_close_01 #1 orange at [164, 249, 438, 480]: found -> missed
  - 4A8B_lampcool6_glass_clutter_01 #2 blue at [254, 114, 300, 163]: found -> missed
  - 4A8B_lampcool6_ottoman_core_01 #3 blue at [273, 113, 316, 160]: found -> missed
  - 4A8B_lampcool6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> missed
  - 4A8B_lampcool6_ottoman_touch_01 #3 orange at [324, 128, 389, 199]: found -> missed
  - 4A8B_lampmid3_bathtile_close_01 #1 orange at [122, 242, 395, 480]: found -> missed
  - 4A8B_lampmid3_glass_clutter_01 #2 blue at [254, 114, 300, 163]: found -> off
  - 4A8B_lampmid3_glass_core_01 #2 blue at [176, 123, 233, 185]: found -> missed
  - 4A8B_lampmid3_glass_touch_01 #1 blue at [224, 124, 280, 185]: found -> off
  - 4A8B_lampmid6_ottoman_clutter_01 #3 orange at [313, 141, 401, 236]: found -> missed
  - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> missed
  - 4A8B_lampmid6_ottoman_core_01 #4 orange at [413, 126, 479, 190]: found -> missed
  - 4A8B_lampmid6_ottoman_edge_01 #2 orange at [267, 139, 351, 231]: found -> missed
  - 4A8B_lampmid6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> missed
  - 4A8B_lampmid6_ottoman_touch_01 #3 orange at [324, 128, 389, 199]: found -> missed
  - 4A8B_lampwarm6_glass_core_01 #4 blue at [371, 111, 412, 151]: found -> off
  - 4A8B_lampwarm6_glass_edge_01 #1 blue at [0, 145, 40, 237]: found -> off
  - 4A8B_lampwarm6_glass_occl_02 #1 blue at [254, 114, 300, 163]: found -> off
  - 4A8B_overheaddim_palewood_clutter_01 #1 blue at [136, 118, 187, 169]: found -> missed
  - 4A8B_overheaddim_palewood_core_01 #2 blue at [246, 111, 282, 148]: found -> missed
  - 4A8B_overheaddim_palewood_core_01 #3 orange at [364, 105, 396, 138]: found -> missed
  - 4A8B_overheaddim_palewood_touch_01 #1 blue at [253, 118, 302, 172]: found -> missed
  - 4A8B_overheaddim_palewood_touch_01 #2 orange at [300, 118, 349, 173]: found -> missed
  - 4A8B_window_abpwhite_occlx_01 #1 orange at [103, 120, 153, 172]: found -> missed
  - 4A8B_window_abpwhite_occlx_01 #2 blue at [307, 120, 360, 176]: found -> missed
  - 4A8B_window_abpwhite_occlx_02 #2 blue at [307, 119, 359, 178]: found -> missed
  - 4A8B_window_abpwhite_occlx_03 #2 blue at [317, 132, 390, 211]: found -> off
  - 4A8B_window_abpwhite_occlx_04 #1 orange at [98, 119, 151, 174]: found -> missed
  - 4A8B_window_abpwhite_occlx_05 #1 orange at [46, 118, 98, 170]: found -> missed
  - 4A8B_window_abpwhite_occlx_05 #2 blue at [316, 133, 390, 212]: found -> off
  - 4A8B_window_abpwhite_occlx_06 #2 blue at [317, 133, 389, 212]: found -> missed
  - 4A8B_window_abpwhite_occlx_07 #1 orange at [108, 116, 159, 166]: found -> missed
  - 4A8B_window_abpwhite_occlx_07 #2 blue at [316, 132, 389, 211]: found -> missed
  - 4A8B_window_abpwhite_occlx_08 #1 orange at [111, 114, 160, 164]: found -> missed
  - 4A8B_window_abpwhite_occlx_08 #2 blue at [317, 133, 390, 211]: found -> missed
  - 4A8B_window_abpwhite_occlx_09 #1 blue at [106, 114, 152, 164]: found -> missed
  - 4A8B_window_abpwhite_occlx_09 #2 blue at [127, 118, 176, 169]: found -> missed
  - 4A8B_window_abpwhite_occlx_10 #2 orange at [105, 130, 173, 197]: found -> missed
  - 4A8B_window_abpwhite_occlx_11 #1 blue at [86, 141, 174, 230]: found -> missed
  - 4A8B_window_abpwhite_occlx_11 #2 orange at [99, 117, 147, 169]: found -> missed
  - 4A8B_window_abpwhite_occlx_13 #1 orange at [101, 118, 153, 166]: found -> missed
  - 4A8B_window_abpwhite_occlx_13 #2 blue at [311, 133, 383, 210]: found -> off
  - 4A8B_window_abpwhite_occlx_14 #2 blue at [190, 120, 244, 177]: found -> missed
  - 4A8B_window_abpwhite_occlx_17 #1 blue at [0, 124, 19, 183]: found -> missed
  - 4A8B_window_abpwhite_occlx_17 #2 blue at [142, 115, 187, 161]: found -> missed
  - 4A8B_window_abpwhite_occlx_18 #1 orange at [102, 118, 153, 166]: found -> missed
  - 4A8B_window_abpwhite_occlx_18 #2 blue at [311, 134, 381, 210]: found -> missed
  - 4A8B_window_abpwhite_occlx_19 #1 blue at [27, 135, 108, 212]: found -> missed
  - 4A8B_window_glass_edge_01 #1 blue at [0, 145, 40, 237]: found -> missed
  - 4A8B_window_light_edge_01 #1 blue at [0, 133, 34, 198]: found -> missed
  - 4A8B_window_light_far_02 #1 blue at [218, 106, 250, 144]: found -> missed
  - 4A8B_window_light_occl_02 #2 orange at [395, 114, 441, 158]: found -> missed
  - 4A8B_window_light_touch_02 #1 orange at [148, 121, 192, 176]: found -> off
  ~ 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> missed

BOXES NOT ON THEIR BARREL that changed: 15 frame(s)
  4A8B_lampcool6_glass_clutter_01: nothing 0 -> 2; now [('blue', (580, 135, 640, 191)), ('orange', (580, 124, 640, 189))]
  4A8B_lampcool6_glass_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('blue', (548, 124, 608, 188))]
  4A8B_lampcool6_glass_occl_02: nothing 0 -> 1; now [('blue', (571, 133, 640, 191))]
  4A8B_lampmid3_glass_clutter_01: nothing 0 -> 2; now [('blue', (493, 116, 541, 168)), ('orange', (556, 117, 605, 170))]
  4A8B_lampmid3_glass_core_01: wrong color 0 -> 1; now [('blue', (143, 120, 189, 171))]
  4A8B_lampmid3_glass_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('blue', (548, 130, 607, 188))]
  4A8B_lampmid6_glass_clutter_01: wrong color 0 -> 1, nothing 1 -> 3; now [('blue', (480, 240, 640, 480)), ('blue', (493, 116, 541, 168)), ('blue', (532, 107, 568, 153)), ('orange', (560, 117, 610, 171))]
  4A8B_lampmid6_glass_neg_02 [empty frame with clutter]: nothing 0 -> 2; now [('blue', (536, 131, 594, 186)), ('orange', (560, 116, 609, 166))]
  4A8B_lampmid6_glass_occl_02: nothing 0 -> 1; now [('blue', (544, 132, 599, 187))]
  4A8B_lampwarm6_glass_clutter_01: nothing 1 -> 2; now [('orange', (556, 117, 605, 172)), ('blue', (579, 135, 640, 191))]
  4A8B_lampwarm6_glass_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('orange', (556, 117, 605, 169))]
  4A8B_lampwarm6_ottoman_core_01: nothing 1 -> 0
  4A8B_overheaddim_palewood_clutter_01: wrong color 0 -> 1; now [('orange', (147, 108, 185, 148))]
  4A8B_overheaddim_palewood_core_01: nothing 1 -> 0
  4A8B_window_glass_occlx_16 [empty frame with clutter]: nothing 0 -> 2; now [('blue', (401, 102, 432, 136)), ('blue', (568, 134, 640, 190))]

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [WORSE] found, the ordinary conditions together: 133.8 -> 80.9 of 172 placements (-52.8; counted per frame 211 -> 142 of 307). Better above +4.0,
      worse below -10.9.
  [WORSE] found, place by place: abp_gray -8.0 of 16 (margin 6.0, WORSE); campus_study -5.0 of 35 (margin 1.0, WORSE); home_bathtile -1.2 of 15 (margin
      1.2); home_glass -1.6 of 15 (margin 1.0, WORSE); home_ottoman -3.0 of 15 (margin 2.3, WORSE); uc_palewood -5.0 of 15 (margin 1.0, WORSE);
      abp_white -25.0 of 32 (margin 1.0, WORSE); home_white -4.0 of 29 (margin 1.0, WORSE).
  [WORSE] boxes that are not on their barrel: 1.9 -> 6.8 counted once per arrangement (+4.9; per frame: on nothing 5 -> 19, second box 0 -> 0, wrong
      color 0 -> 3). Worse above +1.9, better below -1.0.
  [WORSE] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 3.0 per arrangement (margin 1.0).

VERDICT: FAIL. worse than the baseline by more than the noise in: found over all places; found at abp_gray, campus_study, home_glass, home_ottoman, uc_palewood, abp_white, home_white; boxes that are not on their barrel; boxes on empty frames.
```
