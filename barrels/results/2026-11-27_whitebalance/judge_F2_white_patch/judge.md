# Judge: F2_white_patch against today: FAIL

```
JUDGE: F2_white_patch against today

baseline  = today's default (the adopted color model, DetConfig defaults)
candidate = white_patch, alpha 1
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git 3778d2e, 2026-11-26; 34 s in the detectors.

BY PLACE (the verdict is computed on these)
                                            |                      TODAY                       |                  F2_WHITE_PATCH
                    lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
-------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_study             1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  34.0  34 1.0 (1)   0.0 (0)     0   0    0     0
abp_gray                 1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0
home_bathtile            4     28   60   15 |   4.0  16 0.0 (0) 11.0 (44)     0   0    0     0 |  10.5  42 0.0 (0)  4.5 (18)     1   0    5     1
home_glass               5     36   75   15 |  14.8  74 0.2 (1)   0.0 (0)     0   0    3     0 |  14.2  71 0.8 (4)   0.0 (0)     0   0    4     0
home_ottoman             3     21   45   15 |   3.0   9 0.0 (0) 12.0 (36)     0   0    1     0 |   1.3   4 0.3 (1) 13.3 (40)     0   0    5     0
uc_palewood              1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    3     2
abp_white                1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0
-------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 133.8 211 1.2 (2) 37.0 (94)     0   0    5     0 | 137.0 228 3.1 (7) 31.8 (72)     1   0   17     3
-------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                      TODAY                       |                  F2_WHITE_PATCH
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  34.0  34 1.0 (1)   0.0 (0)     0   0    0     0
both_abpgray              1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0
lampcool6_bathtile        1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0 |  14.0  14 0.0 (0)   1.0 (1)     0   0    1     0
lampcool6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0
lampcool6_ottoman         1      7   15   15 |   3.0   3 0.0 (0) 12.0 (12)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |  14.0  14 0.0 (0)   1.0 (1)     1   0    2     1
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampmid6_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |  14.0  14 0.0 (0)   1.0 (1)     0   0    2     0
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0
lampmid6_ottoman          1      7   15   15 |   6.0   6 0.0 (0)   9.0 (9)     0   0    0     0 |   2.0   2 1.0 (1) 12.0 (12)     0   0    0     0
lampwarm6_bathtile        1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   0.0   0 0.0 (0) 15.0 (15)     0   0    0     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  14.0  14 1.0 (1)   0.0 (0)     0   0    2     0
lampwarm6_ottoman         1      7   15   15 |   0.0   0 0.0 (0) 15.0 (15)     0   0    1     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    5     0
overheaddim_palewood      1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    3     2
window_abpwhite           1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0
window_glass              1      8   15   15 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0 |  13.0  13 2.0 (2)   0.0 (0)     0   0    1     0
--------------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                      TODAY                       |                  F2_WHITE_PATCH
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |   2.0   2 0.0 (0) 19.0 (19)     0   0    0     0 |   5.0   5 3.0 (3) 13.0 (13)     1   0    0     0
lampcool6_wood        1     10   21   21 |   2.0   2 2.0 (2) 17.0 (17)     2   0    0     0 |  16.0  16 1.0 (1)   4.0 (4)     0   0    1     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0 |   0.0   0 0.0 (0) 15.0 (15)     0   0    0     0
lampmid3_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     1   0    0     0 |   7.0   7 0.0 (0) 14.0 (14)     0   0    0     0
lampmid6_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |  16.0  16 1.0 (1)   4.0 (4)     0   1    0     0
lampwarm3_wood        1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |  11.0  11 0.0 (0) 10.0 (10)     0   0    0     0
lampwarm6_wood        1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     1   0    0     0 |  12.0  12 0.0 (0)   9.0 (9)     0   0    0     0
window_black          1     10   26   26 |   5.0   5 1.0 (1) 20.0 (20)     0   0    0     0 |   5.0   5 1.0 (1) 20.0 (20)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 34 gained, 17 lost, 1 moved between 'box off' and 'missed' (counted per frame)
  + 4A8B_lampcool6_bathtile_clutter_01 #3 orange at [410, 108, 442, 141]: missed -> found
  + 4A8B_lampcool6_bathtile_occl_02 #1 orange at [346, 107, 376, 137]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: missed -> found
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
  + 4A8B_lampmid6_bathtile_occl_02 #1 orange at [346, 107, 376, 137]: missed -> found
  + 4A8B_lampmid6_bathtile_touch_01 #1 orange at [285, 121, 337, 177]: missed -> found
  + 4A8B_lampmid6_bathtile_touch_01 #2 blue at [337, 123, 390, 180]: missed -> found
  + 4A8B_lampmid6_bathtile_touch_01 #3 blue at [390, 124, 446, 183]: missed -> found
  + 4A8B_lampmid6_ottoman_clutter_01 #1 blue at [79, 146, 177, 241]: missed -> found
  + 4A8B_lampmid6_ottoman_clutter_01 #2 blue at [288, 116, 333, 163]: missed -> found
  + 4A8B_lampwarm6_ottoman_clutter_01 #1 blue at [79, 146, 177, 241]: missed -> found
  - 4A8B_campus_light_room_01 #1 blue at [64, 123, 125, 181]: found -> off
  - 4A8B_lampcool6_bathtile_close_01 #1 orange at [122, 242, 395, 480]: found -> missed
  - 4A8B_lampcool6_glass_occl_02 #1 blue at [254, 114, 300, 163]: found -> off
  - 4A8B_lampcool6_ottoman_core_01 #3 blue at [273, 113, 316, 160]: found -> missed
  - 4A8B_lampcool6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> missed
  - 4A8B_lampcool6_ottoman_touch_01 #3 orange at [324, 128, 389, 199]: found -> missed
  - 4A8B_lampmid3_bathtile_close_01 #1 orange at [122, 242, 395, 480]: found -> missed
  - 4A8B_lampmid6_bathtile_close_01 #1 orange at [122, 242, 395, 480]: found -> missed
  - 4A8B_lampmid6_ottoman_clutter_01 #3 orange at [313, 141, 401, 236]: found -> missed
  - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> missed
  - 4A8B_lampmid6_ottoman_core_01 #4 orange at [413, 126, 479, 190]: found -> missed
  - 4A8B_lampmid6_ottoman_edge_01 #2 orange at [267, 139, 351, 231]: found -> missed
  - 4A8B_lampmid6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> missed
  - 4A8B_lampmid6_ottoman_touch_01 #3 orange at [324, 128, 389, 199]: found -> missed
  - 4A8B_lampwarm6_bathtile_close_01 #1 orange at [122, 242, 395, 480]: found -> missed
  - 4A8B_lampwarm6_glass_occl_02 #1 blue at [254, 114, 300, 163]: found -> off
  - 4A8B_window_glass_clutter_01 #2 blue at [254, 114, 300, 163]: found -> off
  ~ 4A8B_lampmid6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: missed -> off
  report only: 64 gained, 5 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 13 frame(s)
  4A8B_lampcool6_bathtile_close_01: nothing 0 -> 1; now [('blue', (387, 255, 531, 480))]
  4A8B_lampmid3_bathtile_clutter_01: wrong color 0 -> 1; now [('blue', (510, 115, 562, 169))]
  4A8B_lampmid3_bathtile_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('blue', (534, 105, 568, 142))]
  4A8B_lampmid3_bathtile_occl_02: nothing 0 -> 1; now [('blue', (536, 106, 578, 144))]
  4A8B_lampmid3_glass_occl_02: nothing 1 -> 0
  4A8B_lampmid6_bathtile_close_01: nothing 0 -> 2; now [('blue', (4, 194, 173, 370)), ('blue', (47, 240, 170, 480))]
  4A8B_lampwarm6_glass_clutter_01: nothing 1 -> 0
  4A8B_lampwarm6_glass_occl_02: nothing 0 -> 2; now [('orange', (544, 117, 593, 163)), ('orange', (580, 123, 632, 166))]
  4A8B_lampwarm6_ottoman_clutter_01: nothing 0 -> 3; now [('blue', (440, 145, 530, 239)), ('blue', (471, 140, 557, 227)), ('orange', (507, 126, 568, 202))]
  4A8B_lampwarm6_ottoman_core_01: nothing 1 -> 0
  4A8B_lampwarm6_ottoman_occl_02: nothing 0 -> 2; now [('blue', (456, 150, 560, 253)), ('blue', (516, 153, 628, 260))]
  4A8B_overheaddim_palewood_neg_02 [empty frame with clutter]: nothing 0 -> 2; now [('orange', (316, 269, 525, 480)), ('orange', (388, 197, 535, 351))]
  4A8B_window_glass_clutter_01: nothing 0 -> 1; now [('orange', (556, 120, 601, 171))]

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [within the noise] found, the ordinary conditions together: 133.8 -> 137.0 of 172 placements (+3.2; counted per frame 211 -> 228 of 307). Better above
      +4.0, worse below -10.9.
  [within the noise] found, place by place: campus_study -1.0 of 35 (margin 1.0); home_bathtile +6.5 of 15 (margin 1.2); home_glass -0.6 of 15 (margin
      1.0); home_ottoman -1.7 of 15 (margin 2.3).
  [WORSE] boxes that are not on their barrel: 1.9 -> 7.0 counted once per arrangement (+5.0; per frame: on nothing 5 -> 17, second box 0 -> 0, wrong
      color 0 -> 1). Worse above +1.9, better below -1.0.
  [WORSE] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 2.2 per arrangement (margin 1.0).

VERDICT: FAIL. worse than the baseline by more than the noise in: boxes that are not on their barrel; boxes on empty frames.
```
