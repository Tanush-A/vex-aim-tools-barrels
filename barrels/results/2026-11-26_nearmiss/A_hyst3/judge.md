# Judge: A_hyst3 against baseline: FAIL

```
JUDGE: A_hyst3 against baseline

baseline  = today's default (the adopted color model, DetConfig defaults)
candidate = hyst:3: two-level thresholds: loose = hue +-10, S -60, V >= 25, kept when connected to strict; then detector.detect with DetConfig
    defaults
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git c648d95, 2026-11-26; 54 s in the detectors.

BY PLACE (the verdict is computed on these)
                                            |                      BASELINE                      |                      A_HYST3
                    lights frames brls plcm | found raw   box off    missed wrong 2nd none empty | found raw   box off    missed wrong 2nd none empty
-----------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28   0.0 (0)   1.0 (1)     0   0    0     0 |  22.0  22   4.0 (4)   3.0 (3)     3   0    0     0
campus_study             1     21   35   35 |  35.0  35   0.0 (0)   0.0 (0)     0   0    0     0 |  34.0  34   1.0 (1)   0.0 (0)     0   1    2     1
abp_gray                 1      8   16   16 |  10.0  10   1.0 (1)   5.0 (5)     0   0    0     0 |  16.0  16   0.0 (0)   0.0 (0)     0   0    7     2
home_bathtile            4     28   60   15 |   4.0  16   0.0 (0) 11.0 (44)     0   0    0     0 |   4.0  16   0.2 (1) 10.8 (43)     4   0    2     0
home_glass               5     36   75   15 |  14.8  74   0.2 (1)   0.0 (0)     0   0    3     0 |  11.2  56   1.6 (8)  2.2 (11)     2   0   15     7
home_ottoman             3     21   45   15 |   3.0   9   0.0 (0) 12.0 (36)     0   0    1     0 |  10.0  30   0.7 (2)  4.3 (13)     1   0    0     0
uc_palewood              1      7   15   15 |  13.0  13   0.0 (0)   2.0 (2)     0   0    1     0 |  12.0  12   1.0 (1)   2.0 (2)     0   0    0     0
abp_white                1     17   32   32 |  26.0  26   0.0 (0)   6.0 (6)     0   0    0     0 |  24.0  24   2.0 (2)   6.0 (6)     1   0    1     1
-----------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 133.8 211   1.2 (2) 37.0 (94)     0   0    5     0 | 133.2 210 10.5 (19) 28.3 (78)    11   1   27    11
-----------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                     BASELINE                     |                     A_HYST3
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  22.0  22 4.0 (4)   3.0 (3)     3   0    0     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  34.0  34 1.0 (1)   0.0 (0)     0   1    2     1
both_abpgray              1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  16.0  16 0.0 (0)   0.0 (0)     0   0    7     2
lampcool6_bathtile        1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0 |  14.0  14 0.0 (0)   1.0 (1)     0   0    0     0
lampcool6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0 |  12.0  12 1.0 (1)   2.0 (2)     0   0    2     1
lampcool6_ottoman         1      7   15   15 |   3.0   3 0.0 (0) 12.0 (12)     0   0    0     0 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   0.0   0 0.0 (0) 15.0 (15)     2   0    0     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |   9.0   9 4.0 (4)   2.0 (2)     0   0    2     1
lampmid6_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   2.0   2 1.0 (1) 12.0 (12)     2   0    2     0
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    3     1
lampmid6_ottoman          1      7   15   15 |   6.0   6 0.0 (0)   9.0 (9)     0   0    0     0 |  13.0  13 1.0 (1)   1.0 (1)     0   0    0     0
lampwarm6_bathtile        1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   0.0   0 0.0 (0) 15.0 (15)     0   0    0     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  11.0  11 3.0 (3)   1.0 (1)     0   0    2     0
lampwarm6_ottoman         1      7   15   15 |   0.0   0 0.0 (0) 15.0 (15)     0   0    1     0 |   3.0   3 0.0 (0) 12.0 (12)     1   0    0     0
overheaddim_palewood      1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  12.0  12 1.0 (1)   2.0 (2)     0   0    0     0
window_abpwhite           1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  24.0  24 2.0 (2)   6.0 (6)     1   0    1     1
window_glass              1      8   15   15 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0 |  11.0  11 0.0 (0)   4.0 (4)     2   0    6     4
--------------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                     BASELINE                     |                     A_HYST3
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |   2.0   2 0.0 (0) 19.0 (19)     0   0    0     0 |   3.0   3 0.0 (0) 18.0 (18)     1   0    0     0
lampcool6_wood        1     10   21   21 |   2.0   2 2.0 (2) 17.0 (17)     2   0    0     0 |   9.0   9 0.0 (0) 12.0 (12)     1   0    0     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0 |   2.0   2 0.0 (0) 13.0 (13)     0   0    0     0
lampmid3_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     1   0    0     0 |   0.0   0 1.0 (1) 20.0 (20)     1   0    0     0
lampmid6_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   0.0   0 2.0 (2) 19.0 (19)     5   0    0     0
lampwarm3_wood        1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   0.0   0 0.0 (0) 21.0 (21)     1   0    0     0
lampwarm6_wood        1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     1   0    0     0 |   0.0   0 0.0 (0) 21.0 (21)     1   0    0     0
window_black          1     10   26   26 |   5.0   5 1.0 (1) 20.0 (20)     0   0    0     0 |  18.0  18 3.0 (3)   5.0 (5)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 32 gained, 33 lost, 6 moved between 'box off' and 'missed' (counted per frame)
  + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found
  + 4A8B_both_abpgray_core_01 #2 blue at [233, 165, 353, 299]: missed -> found
  + 4A8B_both_abpgray_core_01 #4 orange at [408, 125, 472, 192]: missed -> found
  + 4A8B_both_abpgray_edge_01 #1 orange at [291, 127, 356, 197]: missed -> found
  + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: missed -> found
  + 4A8B_both_abpgray_touch_01 #2 blue at [246, 123, 301, 181]: missed -> found
  + 4A8B_lampcool6_bathtile_clutter_01 #3 orange at [410, 108, 442, 141]: missed -> found
  + 4A8B_lampcool6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #1 blue at [79, 146, 177, 241]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #3 orange at [313, 141, 401, 236]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #4 orange at [413, 126, 479, 190]: missed -> found
  + 4A8B_lampcool6_ottoman_edge_01 #1 blue at [0, 141, 43, 229]: missed -> found
  + 4A8B_lampcool6_ottoman_edge_01 #2 orange at [267, 139, 351, 231]: missed -> found
  + 4A8B_lampcool6_ottoman_occl_02 #1 orange at [225, 125, 286, 192]: missed -> found
  + 4A8B_lampcool6_ottoman_touch_01 #1 blue at [198, 129, 262, 198]: missed -> found
  + 4A8B_lampmid6_bathtile_edge_01 #2 orange at [279, 122, 331, 178]: missed -> found
  + 4A8B_lampmid6_bathtile_touch_01 #2 blue at [337, 123, 390, 180]: missed -> found
  + 4A8B_lampmid6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found
  + 4A8B_lampmid6_ottoman_clutter_01 #1 blue at [79, 146, 177, 241]: missed -> found
  + 4A8B_lampmid6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: missed -> found
  + 4A8B_lampmid6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: missed -> found
  + 4A8B_lampmid6_ottoman_core_01 #3 blue at [273, 113, 316, 160]: missed -> found
  + 4A8B_lampmid6_ottoman_edge_01 #1 blue at [0, 141, 43, 229]: missed -> found
  + 4A8B_lampmid6_ottoman_touch_01 #1 blue at [198, 129, 262, 198]: missed -> found
  + 4A8B_lampwarm6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: missed -> found
  + 4A8B_lampwarm6_ottoman_edge_01 #2 orange at [267, 139, 351, 231]: missed -> found
  + 4A8B_lampwarm6_ottoman_touch_01 #3 orange at [324, 128, 389, 199]: missed -> found
  + 4A8B_window_abpwhite_occlx_06 #1 orange at [133, 115, 181, 160]: missed -> found
  + 4A8B_window_abpwhite_occlx_14 #1 orange at [0, 120, 45, 179]: missed -> found
  - 4A8B_window_light_cluster_01 #2 blue at [331, 119, 382, 171]: found -> off
  - 4A8B_window_light_cluster_02 #2 blue at [351, 119, 398, 167]: found -> missed
  - 4A8B_window_light_cluster_02 #4 blue at [443, 122, 500, 179]: found -> off
  - 4A8B_window_light_far_02 #4 blue at [433, 106, 468, 139]: found -> off
  - 4A8B_window_light_occl_01 #2 blue at [386, 115, 430, 161]: found -> missed
  - 4A8B_window_light_touch_02 #2 blue at [187, 122, 240, 178]: found -> off
  - 4A8B_campus_light_cluster_02 #4 blue at [379, 117, 419, 163]: found -> off
  - 4A8B_lampcool6_glass_clutter_01 #2 blue at [254, 114, 300, 163]: found -> missed
  - 4A8B_lampcool6_glass_edge_01 #1 blue at [0, 145, 40, 237]: found -> off
  - 4A8B_lampcool6_glass_occl_02 #1 blue at [254, 114, 300, 163]: found -> missed
  - 4A8B_lampmid3_bathtile_close_01 #1 orange at [122, 242, 395, 480]: found -> missed
  - 4A8B_lampmid3_glass_clutter_01 #2 blue at [254, 114, 300, 163]: found -> missed
  - 4A8B_lampmid3_glass_clutter_01 #4 orange at [520, 118, 579, 169]: found -> off
  - 4A8B_lampmid3_glass_core_01 #2 blue at [176, 123, 233, 185]: found -> off
  - 4A8B_lampmid3_glass_edge_01 #1 blue at [0, 145, 40, 237]: found -> off
  - 4A8B_lampmid3_glass_occl_02 #1 blue at [254, 114, 300, 163]: found -> missed
  - 4A8B_lampmid3_glass_touch_01 #1 blue at [224, 124, 280, 185]: found -> off
  - 4A8B_lampmid6_bathtile_close_01 #1 orange at [122, 242, 395, 480]: found -> missed
  - 4A8B_lampmid6_glass_clutter_01 #2 blue at [254, 114, 300, 163]: found -> missed
  - 4A8B_lampmid6_glass_occl_02 #1 blue at [254, 114, 300, 163]: found -> missed
  - 4A8B_lampwarm6_bathtile_close_01 #1 orange at [122, 242, 395, 480]: found -> missed
  - 4A8B_lampwarm6_glass_clutter_01 #3 orange at [359, 104, 387, 133]: found -> off
  - 4A8B_lampwarm6_glass_clutter_01 #4 orange at [520, 118, 579, 169]: found -> off
  - 4A8B_lampwarm6_glass_core_01 #1 orange at [143, 112, 182, 152]: found -> missed
  - 4A8B_lampwarm6_glass_occl_02 #1 blue at [254, 114, 300, 163]: found -> off
  - 4A8B_overheaddim_palewood_close_01 #1 orange at [291, 243, 566, 480]: found -> missed
  - 4A8B_window_abpwhite_occlx_01 #2 blue at [307, 120, 360, 176]: found -> off
  - 4A8B_window_abpwhite_occlx_08 #1 orange at [111, 114, 160, 164]: found -> missed
  - 4A8B_window_abpwhite_occlx_09 #1 blue at [106, 114, 152, 164]: found -> missed
  - 4A8B_window_abpwhite_occlx_17 #1 blue at [0, 124, 19, 183]: found -> missed
  - 4A8B_window_glass_clutter_01 #2 blue at [254, 114, 300, 163]: found -> missed
  - 4A8B_window_glass_core_01 #2 blue at [176, 123, 233, 185]: found -> missed
  - 4A8B_window_glass_edge_01 #1 blue at [0, 145, 40, 237]: found -> missed
  ~ 4A8B_lampcool6_ottoman_clutter_01 #2 blue at [288, 116, 333, 163]: missed -> off
  ~ 4A8B_lampmid6_bathtile_touch_01 #3 blue at [390, 124, 446, 183]: missed -> off
  ~ 4A8B_lampmid6_ottoman_occl_02 #1 orange at [225, 125, 286, 192]: missed -> off
  ~ 4A8B_overheaddim_palewood_occl_02 #1 orange at [344, 115, 388, 162]: missed -> off
  ~ 4A8B_window_abpwhite_occlx_10 #1 orange at [99, 118, 148, 168]: missed -> off
  ~ 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> missed
  report only: 24 gained, 5 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 30 frame(s)
  4A8B_window_light_core_03: wrong color 0 -> 1; now [('blue', (315, 98, 346, 125))]
  4A8B_window_light_far_02: wrong color 0 -> 2; now [('blue', (246, 97, 274, 124)), ('blue', (332, 98, 363, 125))]
  4A8B_campus_light_cluster_02: second 0 -> 1; now [('orange', (316, 131, 378, 202))]
  4A8B_campus_light_held_01: nothing 0 -> 1; now [('blue', (423, 107, 460, 155))]
  4A8B_campus_light_neg_05 [empty frame, clean]: nothing 0 -> 1; now [('blue', (422, 106, 461, 157))]
  4A8B_both_abpgray_clutter_01: nothing 0 -> 3; now [('orange', (0, 306, 187, 480)), ('orange', (187, 235, 456, 480)), ('orange', (489, 111, 523, 153))]
  4A8B_both_abpgray_neg_02 [empty frame with clutter]: nothing 0 -> 2; now [('orange', (0, 307, 183, 480)), ('orange', (183, 248, 432, 480))]
  4A8B_both_abpgray_occl_02: nothing 0 -> 2; now [('orange', (16, 296, 207, 480)), ('orange', (207, 240, 463, 480))]
  4A8B_lampcool6_glass_clutter_01: nothing 0 -> 1; now [('orange', (560, 117, 610, 171))]
  4A8B_lampcool6_glass_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('orange', (560, 122, 609, 166))]
  4A8B_lampmid3_bathtile_edge_01: wrong color 0 -> 1; now [('orange', (0, 115, 35, 173))]
  4A8B_lampmid3_bathtile_touch_01: wrong color 0 -> 1; now [('orange', (396, 109, 443, 151))]
  4A8B_lampmid3_glass_clutter_01: nothing 0 -> 1; now [('orange', (560, 117, 610, 172))]
  4A8B_lampmid3_glass_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('orange', (559, 122, 608, 169))]
  4A8B_lampmid3_glass_occl_02: nothing 1 -> 0
  4A8B_lampmid6_bathtile_clutter_01: nothing 0 -> 1; now [('orange', (330, 96, 351, 117))]
  4A8B_lampmid6_bathtile_core_01: wrong color 0 -> 1; now [('orange', (479, 101, 513, 132))]
  4A8B_lampmid6_bathtile_occl_02: nothing 0 -> 1; now [('orange', (326, 96, 348, 120))]
  4A8B_lampmid6_bathtile_touch_01: wrong color 0 -> 1; now [('orange', (340, 128, 418, 198))]
  4A8B_lampmid6_glass_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('orange', (559, 116, 608, 170))]
  4A8B_lampmid6_glass_occl_02: nothing 0 -> 1; now [('orange', (559, 116, 608, 170))]
  4A8B_lampwarm6_glass_occl_02: nothing 0 -> 1; now [('orange', (552, 117, 609, 177))]
  4A8B_lampwarm6_ottoman_clutter_01: wrong color 0 -> 1; now [('orange', (90, 136, 171, 203))]
  4A8B_lampwarm6_ottoman_core_01: nothing 1 -> 0
  4A8B_overheaddim_palewood_core_01: nothing 1 -> 0
  4A8B_window_abpwhite_occlx_01: wrong color 0 -> 1; now [('orange', (317, 108, 360, 149))]
  4A8B_window_abpwhite_occlx_15 [empty frame with clutter]: nothing 0 -> 1; now [('blue', (397, 118, 453, 172))]
  4A8B_window_glass_clutter_01: wrong color 0 -> 1, nothing 0 -> 2; now [('blue', (492, 117, 541, 171)), ('blue', (525, 125, 597, 190)), ('orange', (561, 117, 611, 172))]
  4A8B_window_glass_core_01: wrong color 0 -> 1; now [('blue', (148, 118, 190, 172))]
  4A8B_window_glass_occlx_16 [empty frame with clutter]: nothing 0 -> 4; now [('blue', (385, 106, 428, 145)), ('blue', (432, 106, 466, 144)), ('blue', (466, 104, 503, 146)), ('blue', (550, 126, 609, 188))]

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [within the noise] found, the ordinary conditions together: 133.8 -> 133.2 of 172 placements (-0.6; counted per frame 211 -> 210 of 307). Better above
      +4.0, worse below -10.9.
  [WORSE] found, place by place: home_white -6.0 of 29 (margin 1.0, WORSE); campus_study -1.0 of 35 (margin 1.0); abp_gray +6.0 of 16 (margin 6.0);
      home_glass -3.6 of 15 (margin 1.0, WORSE); home_ottoman +7.0 of 15 (margin 2.3); uc_palewood -1.0 of 15 (margin 1.0); abp_white -2.0 of 32 (margin
      1.0, WORSE).
  [WORSE] boxes that are not on their barrel: 1.9 -> 23.4 counted once per arrangement (+21.5; per frame: on nothing 5 -> 27, second box 0 -> 1, wrong
      color 0 -> 11). Worse above +1.9, better below -1.0.
  [WORSE] boxes on empty frames: on clean ones 0 -> 1 (margin 0: none is allowed); on ones with clutter 0.0 -> 7.6 per arrangement (margin 1.0).

VERDICT: FAIL. worse than the baseline by more than the noise in: found at home_white, home_glass, abp_white; boxes that are not on their barrel; boxes on empty frames.
```
