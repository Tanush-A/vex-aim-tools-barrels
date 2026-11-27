# Judge: cal_core_net against today: FAIL

```
JUDGE: cal_core_net against today

baseline  = today's default (the adopted color model, DetConfig defaults)
candidate = ONE frame sets the condition (net): the calibration frame (core_01), applied to the other frames; the calibration frame itself is scored
    with the backup frame's setting
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git 8b81375, 2026-11-26; 31 s in the detectors.

BY PLACE (the verdict is computed on these)
                                            |                      TODAY                       |                   CAL_CORE_NET
                    lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
-------------------------------------------------------------------------------------------------------------------------------------------------
abp_gray                 1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  15.0  15 0.0 (0)   1.0 (1)     1   0    0     0
campus_study             1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  28.0  28 2.0 (2)   5.0 (5)     0   0    0     0
home_bathtile            4     28   60   15 |   4.0  16 0.0 (0) 11.0 (44)     0   0    0     0 |  13.8  55 0.2 (1)   1.0 (4)     0   0    1     0
home_glass               5     36   75   15 |  14.8  74 0.2 (1)   0.0 (0)     0   0    3     0 |  14.8  74 0.0 (0)   0.2 (1)     0   0    0     0
home_ottoman             3     21   45   15 |   3.0   9 0.0 (0) 12.0 (36)     0   0    1     0 |  12.3  37 1.3 (4)   1.3 (4)     0   0    0     0
uc_palewood              1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     1   0    0     0
abp_white                1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  19.0  19 0.0 (0) 13.0 (13)     0   0    0     0
home_white               1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  25.0  25 0.0 (0)   4.0 (4)     0   0    0     0
-------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 133.8 211 1.2 (2) 37.0 (94)     0   0    5     0 | 140.9 266 3.6 (7) 27.5 (34)     2   0    1     0
-------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                      TODAY                       |                   CAL_CORE_NET
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
both_abpgray              1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  15.0  15 0.0 (0)   1.0 (1)     1   0    0     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  28.0  28 2.0 (2)   5.0 (5)     0   0    0     0
lampcool6_bathtile        1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampcool6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampcool6_ottoman         1      7   15   15 |   3.0   3 0.0 (0) 12.0 (12)     0   0    0     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampmid6_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |  14.0  14 0.0 (0)   1.0 (1)     0   0    0     0
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampmid6_ottoman          1      7   15   15 |   6.0   6 0.0 (0)   9.0 (9)     0   0    0     0 |  13.0  13 1.0 (1)   1.0 (1)     0   0    0     0
lampwarm6_bathtile        1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |  12.0  12 0.0 (0)   3.0 (3)     0   0    1     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampwarm6_ottoman         1      7   15   15 |   0.0   0 0.0 (0) 15.0 (15)     0   0    1     0 |   9.0   9 3.0 (3)   3.0 (3)     0   0    0     0
overheaddim_palewood      1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     1   0    0     0
window_abpwhite           1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  19.0  19 0.0 (0) 13.0 (13)     0   0    0     0
window_glass              1      8   15   15 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0 |  14.0  14 0.0 (0)   1.0 (1)     0   0    0     0
window_light              1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  25.0  25 0.0 (0)   4.0 (4)     0   0    0     0
--------------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 74 gained, 19 lost, 5 moved between 'box off' and 'missed' (counted per frame)
  + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found
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
  + 4A8B_lampcool6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #4 orange at [413, 126, 479, 190]: missed -> found
  + 4A8B_lampcool6_ottoman_edge_01 #1 blue at [0, 141, 43, 229]: missed -> found
  + 4A8B_lampcool6_ottoman_edge_01 #2 orange at [267, 139, 351, 231]: missed -> found
  + 4A8B_lampcool6_ottoman_occl_02 #1 orange at [225, 125, 286, 192]: missed -> found
  + 4A8B_lampcool6_ottoman_touch_01 #1 blue at [198, 129, 262, 198]: missed -> found
  + 4A8B_lampmid3_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: missed -> found
  + 4A8B_lampmid3_bathtile_clutter_01 #2 blue at [292, 111, 330, 152]: missed -> found
  + 4A8B_lampmid3_bathtile_clutter_01 #3 orange at [410, 108, 442, 141]: missed -> found
  + 4A8B_lampmid3_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: missed -> found
  + 4A8B_lampmid3_bathtile_core_01 #1 orange at [223, 115, 270, 165]: missed -> found
  + 4A8B_lampmid3_bathtile_core_01 #2 orange at [328, 106, 358, 138]: missed -> found
  + 4A8B_lampmid3_bathtile_core_01 #3 blue at [374, 140, 457, 226]: missed -> found
  + 4A8B_lampmid3_bathtile_core_01 #4 blue at [475, 110, 513, 147]: missed -> found
  + 4A8B_lampmid3_bathtile_edge_01 #2 orange at [279, 122, 331, 178]: missed -> found
  + 4A8B_lampmid3_bathtile_occl_02 #1 orange at [346, 107, 376, 137]: missed -> found
  + 4A8B_lampmid3_bathtile_touch_01 #1 orange at [285, 121, 337, 177]: missed -> found
  + 4A8B_lampmid3_bathtile_touch_01 #2 blue at [337, 123, 390, 180]: missed -> found
  + 4A8B_lampmid3_bathtile_touch_01 #3 blue at [390, 124, 446, 183]: missed -> found
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
  + 4A8B_lampmid6_bathtile_touch_01 #1 orange at [285, 121, 337, 177]: missed -> found
  + 4A8B_lampmid6_bathtile_touch_01 #2 blue at [337, 123, 390, 180]: missed -> found
  + 4A8B_lampmid6_bathtile_touch_01 #3 blue at [390, 124, 446, 183]: missed -> found
  + 4A8B_lampmid6_ottoman_clutter_01 #1 blue at [79, 146, 177, 241]: missed -> found
  + 4A8B_lampmid6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: missed -> found
  + 4A8B_lampmid6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: missed -> found
  + 4A8B_lampmid6_ottoman_core_01 #3 blue at [273, 113, 316, 160]: missed -> found
  + 4A8B_lampmid6_ottoman_edge_01 #1 blue at [0, 141, 43, 229]: missed -> found
  + 4A8B_lampmid6_ottoman_occl_02 #1 orange at [225, 125, 286, 192]: missed -> found
  + 4A8B_lampmid6_ottoman_touch_01 #1 blue at [198, 129, 262, 198]: missed -> found
  + 4A8B_lampwarm6_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: missed -> found
  + 4A8B_lampwarm6_bathtile_clutter_01 #2 blue at [292, 111, 330, 152]: missed -> found
  + 4A8B_lampwarm6_bathtile_clutter_01 #3 orange at [410, 108, 442, 141]: missed -> found
  + 4A8B_lampwarm6_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: missed -> found
  + 4A8B_lampwarm6_bathtile_core_01 #1 orange at [223, 115, 270, 165]: missed -> found
  + 4A8B_lampwarm6_bathtile_core_01 #4 blue at [475, 110, 513, 147]: missed -> found
  + 4A8B_lampwarm6_bathtile_edge_01 #1 blue at [0, 127, 31, 196]: missed -> found
  + 4A8B_lampwarm6_bathtile_edge_01 #2 orange at [279, 122, 331, 178]: missed -> found
  + 4A8B_lampwarm6_bathtile_touch_01 #1 orange at [285, 121, 337, 177]: missed -> found
  + 4A8B_lampwarm6_bathtile_touch_01 #2 blue at [337, 123, 390, 180]: missed -> found
  + 4A8B_lampwarm6_bathtile_touch_01 #3 blue at [390, 124, 446, 183]: missed -> found
  + 4A8B_lampwarm6_ottoman_clutter_01 #1 blue at [79, 146, 177, 241]: missed -> found
  + 4A8B_lampwarm6_ottoman_clutter_01 #3 orange at [313, 141, 401, 236]: missed -> found
  + 4A8B_lampwarm6_ottoman_core_01 #1 blue at [79, 133, 155, 209]: missed -> found
  + 4A8B_lampwarm6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: missed -> found
  + 4A8B_lampwarm6_ottoman_core_01 #4 orange at [415, 126, 479, 191]: missed -> found
  + 4A8B_lampwarm6_ottoman_edge_01 #2 orange at [267, 139, 351, 231]: missed -> found
  + 4A8B_lampwarm6_ottoman_touch_01 #1 blue at [198, 129, 262, 198]: missed -> found
  + 4A8B_lampwarm6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: missed -> found
  + 4A8B_lampwarm6_ottoman_touch_01 #3 orange at [324, 128, 389, 199]: missed -> found
  + 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found
  + 4A8B_window_light_cluster_01 #3 orange at [361, 117, 400, 163]: missed -> found
  - 4A8B_campus_light_core_01 #1 blue at [90, 161, 208, 286]: found -> off
  - 4A8B_campus_light_core_01 #2 orange at [247, 110, 279, 145]: found -> missed
  - 4A8B_campus_light_core_01 #3 blue at [333, 131, 397, 200]: found -> missed
  - 4A8B_campus_light_far_01 #1 orange at [196, 116, 238, 161]: found -> missed
  - 4A8B_campus_light_occl_02 #1 blue at [275, 123, 328, 180]: found -> missed
  - 4A8B_campus_light_plain_01 #2 orange at [498, 145, 603, 243]: found -> off
  - 4A8B_campus_light_room_03 #2 orange at [215, 112, 252, 152]: found -> missed
  - 4A8B_window_abpwhite_occlx_01 #1 orange at [103, 120, 153, 172]: found -> missed
  - 4A8B_window_abpwhite_occlx_04 #1 orange at [98, 119, 151, 174]: found -> missed
  - 4A8B_window_abpwhite_occlx_07 #1 orange at [108, 116, 159, 166]: found -> missed
  - 4A8B_window_abpwhite_occlx_08 #1 orange at [111, 114, 160, 164]: found -> missed
  - 4A8B_window_abpwhite_occlx_09 #1 blue at [106, 114, 152, 164]: found -> missed
  - 4A8B_window_abpwhite_occlx_10 #2 orange at [105, 130, 173, 197]: found -> missed
  - 4A8B_window_abpwhite_occlx_11 #2 orange at [99, 117, 147, 169]: found -> missed
  - 4A8B_window_glass_core_01 #2 blue at [176, 123, 233, 185]: found -> missed
  - 4A8B_window_light_far_02 #2 orange at [244, 105, 273, 135]: found -> missed
  - 4A8B_window_light_far_02 #3 orange at [333, 106, 363, 137]: found -> missed
  - 4A8B_window_light_occl_01 #2 blue at [386, 115, 430, 161]: found -> missed
  - 4A8B_window_light_occl_02 #2 orange at [395, 114, 441, 158]: found -> missed
  ~ 4A8B_lampmid3_bathtile_edge_01 #1 blue at [0, 127, 31, 196]: missed -> off
  ~ 4A8B_lampmid6_ottoman_clutter_01 #2 blue at [288, 116, 333, 163]: missed -> off
  ~ 4A8B_lampwarm6_ottoman_core_01 #3 blue at [273, 113, 316, 160]: missed -> off
  ~ 4A8B_lampwarm6_ottoman_edge_01 #1 blue at [0, 141, 43, 229]: missed -> off
  ~ 4A8B_lampwarm6_ottoman_occl_02 #1 orange at [225, 125, 286, 192]: missed -> off

BOXES NOT ON THEIR BARREL that changed: 8 frame(s)
  4A8B_both_abpgray_core_01: wrong color 0 -> 1; now [('orange', (237, 155, 349, 265))]
  4A8B_lampmid3_glass_occl_02: nothing 1 -> 0
  4A8B_lampmid6_glass_clutter_01: nothing 1 -> 0
  4A8B_lampwarm6_bathtile_occl_02: nothing 0 -> 1; now [('blue', (536, 107, 576, 149))]
  4A8B_lampwarm6_glass_clutter_01: nothing 1 -> 0
  4A8B_lampwarm6_ottoman_core_01: nothing 1 -> 0
  4A8B_overheaddim_palewood_clutter_01: wrong color 0 -> 1; now [('blue', (139, 130, 206, 211))]
  4A8B_overheaddim_palewood_core_01: nothing 1 -> 0

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [BETTER] found, the ordinary conditions together: 133.8 -> 140.9 of 172 placements (+7.1; counted per frame 211 -> 266 of 307). Better above +4.0,
      worse below -10.9.
  [WORSE] found, place by place: abp_gray +5.0 of 16 (margin 6.0); campus_study -7.0 of 35 (margin 1.0, WORSE); home_bathtile +9.8 of 15 (margin 1.2);
      home_ottoman +9.3 of 15 (margin 2.3); abp_white -7.0 of 32 (margin 1.0, WORSE); home_white -3.0 of 29 (margin 1.0, WORSE).
  [within the noise] boxes that are not on their barrel: 1.9 -> 2.2 counted once per arrangement (+0.3; per frame: on nothing 5 -> 1, second box 0 -> 0,
      wrong color 0 -> 2). Worse above +1.9, better below -1.0.
  [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 0.0 per arrangement (margin
      1.0).

VERDICT: FAIL. worse than the baseline by more than the noise in: found at campus_study, abp_white, home_white.
```
