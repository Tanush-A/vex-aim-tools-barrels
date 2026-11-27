# Judge: rows [s40] against today [s40]: NO CLEAR DIFFERENCE

```
JUDGE: rows [s40] against today [s40]

baseline  = both saturation floors lowered by 40 (orange 100, blue 73); DetConfig defaults
candidate = both saturation floors lowered by 40 (orange 100, blue 73); DetConfig bottom_rows=0.5
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git d86fd73, 2026-11-26; 0 s in the detectors.

BY PLACE (the verdict is computed on these)
                                            |                    TODAY [S40]                    |                    ROWS [S40]
                    lights frames brls plcm | found raw  box off    missed wrong 2nd none empty | found raw  box off    missed wrong 2nd none empty
---------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  23.0  23  2.0 (2)   4.0 (4)     5   0    0     0 |  24.0  24  1.0 (1)   4.0 (4)     5   0    0     0
campus_study             1     21   35   35 |  34.0  34  1.0 (1)   0.0 (0)     0   0    0     0 |  35.0  35  0.0 (0)   0.0 (0)     0   0    0     0
abp_gray                 1      8   16   16 |  10.0  10  1.0 (1)   5.0 (5)     0   0    0     0 |   7.0   7  4.0 (4)   5.0 (5)     0   0    0     0
home_bathtile            4     28   60   15 |   4.8  19  0.5 (2)  9.8 (39)     1   0    2     0 |   4.5  18  0.8 (3)  9.8 (39)     1   0    2     0
home_glass               5     36   75   15 |  13.6  68  1.2 (6)   0.2 (1)     1   0   17     7 |  14.0  70  0.8 (4)   0.2 (1)     1   0   16     7
home_ottoman             3     21   45   15 |   5.0  15  0.3 (1)  9.7 (29)     0   0    0     0 |   3.7  11  1.0 (3) 10.3 (31)     0   0    0     0
uc_palewood              1      7   15   15 |  11.0  11  0.0 (0)   4.0 (4)     1   0    0     0 |  11.0  11  1.0 (1)   3.0 (3)     0   0    0     0
abp_white                1     17   32   32 |  24.0  24  1.0 (1)   7.0 (7)     0   0    0     0 |  25.0  25  1.0 (1)   6.0 (6)     0   0    0     0
---------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 125.4 204 7.0 (14) 39.6 (89)     8   0   19     7 | 124.2 201 9.6 (17) 38.3 (89)     7   0   18     7
---------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                   TODAY [S40]                    |                    ROWS [S40]
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  23.0  23 2.0 (2)   4.0 (4)     5   0    0     0 |  24.0  24 1.0 (1)   4.0 (4)     5   0    0     0
campus_light              1     21   35   35 |  34.0  34 1.0 (1)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
both_abpgray              1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |   7.0   7 4.0 (4)   5.0 (5)     0   0    0     0
lampcool6_bathtile        1      7   15   15 |  14.0  14 0.0 (0)   1.0 (1)     0   0    0     0 |  13.0  13 1.0 (1)   1.0 (1)     0   0    0     0
lampcool6_glass           1      7   15   15 |  13.0  13 2.0 (2)   0.0 (0)     0   0    2     1 |  13.0  13 2.0 (2)   0.0 (0)     0   0    2     1
lampcool6_ottoman         1      7   15   15 |   6.0   6 0.0 (0)   9.0 (9)     0   0    0     0 |   4.0   4 1.0 (1) 10.0 (10)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |   3.0   3 0.0 (0) 12.0 (12)     0   0    1     0 |   3.0   3 0.0 (0) 12.0 (12)     0   0    1     0
lampmid3_glass            1      7   15   15 |  13.0  13 2.0 (2)   0.0 (0)     0   0    2     1 |  13.0  13 2.0 (2)   0.0 (0)     0   0    2     1
lampmid6_bathtile         1      7   15   15 |   1.0   1 2.0 (2) 12.0 (12)     1   0    1     0 |   1.0   1 2.0 (2) 12.0 (12)     1   0    1     0
lampmid6_glass            1      7   15   15 |  13.0  13 2.0 (2)   0.0 (0)     1   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     1   0    1     0
lampmid6_ottoman          1      7   15   15 |   8.0   8 1.0 (1)   6.0 (6)     0   0    0     0 |   7.0   7 1.0 (1)   7.0 (7)     0   0    0     0
lampwarm6_bathtile        1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    3     1 |  15.0  15 0.0 (0)   0.0 (0)     0   0    3     1
lampwarm6_ottoman         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   0.0   0 1.0 (1) 14.0 (14)     0   0    0     0
overheaddim_palewood      1      7   15   15 |  11.0  11 0.0 (0)   4.0 (4)     1   0    0     0 |  11.0  11 1.0 (1)   3.0 (3)     0   0    0     0
window_abpwhite           1     17   32   32 |  24.0  24 1.0 (1)   7.0 (7)     0   0    0     0 |  25.0  25 1.0 (1)   6.0 (6)     0   0    0     0
window_glass              1      8   15   15 |  14.0  14 0.0 (0)   1.0 (1)     0   0    9     4 |  14.0  14 0.0 (0)   1.0 (1)     0   0    8     4
--------------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                   TODAY [S40]                    |                    ROWS [S40]
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |   3.0   3 4.0 (4) 14.0 (14)     1   0    0     0 |   3.0   3 4.0 (4) 14.0 (14)     0   0    0     0
lampcool6_wood        1     10   21   21 |   8.0   8 2.0 (2) 11.0 (11)     2   0    0     0 |   8.0   8 2.0 (2) 11.0 (11)     2   0    0     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0
lampmid3_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0
lampmid6_wood         1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     2   0    1     0 |   0.0   0 0.0 (0) 21.0 (21)     2   0    1     0
lampwarm3_wood        1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0
lampwarm6_wood        1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0
window_black          1     10   26   26 |  10.0  10 3.0 (3) 13.0 (13)     0   0    0     0 |  11.0  11 3.0 (3) 12.0 (12)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 10 gained, 13 lost, 1 moved between 'box off' and 'missed' (counted per frame)
  + 4A8B_window_light_far_02 #2 orange at [244, 105, 273, 135]: off -> found
  + 4A8B_campus_light_cluster_02 #4 blue at [379, 117, 419, 163]: off -> found
  + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found
  + 4A8B_lampcool6_glass_core_01 #2 blue at [176, 123, 233, 185]: off -> found
  + 4A8B_lampmid3_glass_core_01 #4 blue at [371, 111, 412, 151]: off -> found
  + 4A8B_lampmid6_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found
  + 4A8B_lampmid6_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found
  + 4A8B_overheaddim_palewood_core_01 #2 blue at [246, 111, 282, 148]: missed -> found
  + 4A8B_window_abpwhite_occlx_09 #1 blue at [106, 114, 152, 164]: off -> found
  + 4A8B_window_abpwhite_occlx_17 #1 blue at [0, 124, 19, 183]: missed -> found
  - 4A8B_both_abpgray_clutter_01 #1 blue at [34, 132, 110, 203]: found -> off
  - 4A8B_both_abpgray_clutter_01 #4 orange at [506, 124, 579, 190]: found -> off
  - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off
  - 4A8B_both_abpgray_occl_02 #1 blue at [366, 123, 422, 181]: found -> off
  - 4A8B_lampcool6_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: found -> off
  - 4A8B_lampcool6_glass_core_01 #4 blue at [371, 111, 412, 151]: found -> off
  - 4A8B_lampcool6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> missed
  - 4A8B_lampcool6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off
  - 4A8B_lampmid3_glass_clutter_01 #2 blue at [254, 114, 300, 163]: found -> off
  - 4A8B_lampmid6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off
  - 4A8B_lampwarm6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off
  - 4A8B_overheaddim_palewood_core_01 #1 orange at [125, 137, 207, 223]: found -> off
  - 4A8B_window_abpwhite_occlx_18 #1 orange at [102, 118, 153, 166]: found -> off
  ~ 4A8B_lampmid6_ottoman_occl_02 #1 orange at [225, 125, 286, 192]: off -> missed
  report only: 1 gained, 0 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 2 frame(s)
  4A8B_overheaddim_palewood_core_01: wrong color 1 -> 0
  4A8B_window_glass_clutter_01: nothing 2 -> 1; now [('orange', (561, 117, 602, 165))]

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [within the noise] found, the ordinary conditions together: 125.4 -> 124.2 of 172 placements (-1.2; counted per frame 204 -> 201 of 307). Better above
      +4.0, worse below -10.9.
  [within the noise] found, place by place: home_white +1.0 of 29 (margin 1.0); campus_study +1.0 of 35 (margin 1.0); abp_gray -3.0 of 16 (margin 6.0);
      home_bathtile -0.2 of 15 (margin 1.2); home_glass +0.4 of 15 (margin 1.0); home_ottoman -1.3 of 15 (margin 2.3); abp_white +1.0 of 32 (margin
      1.0).
  [BETTER] boxes that are not on their barrel: 12.8 -> 11.6 counted once per arrangement (-1.2; per frame: on nothing 19 -> 18, second box 0 -> 0, wrong
      color 8 -> 7). Worse above +1.9, better below -1.0.
  [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 3.8 -> 3.8 per arrangement (margin
      1.0).

VERDICT: NO CLEAR DIFFERENCE. no count moved by more than a change that means nothing moves it.
```
