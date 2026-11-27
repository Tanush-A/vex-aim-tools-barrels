# Judge: rows+low [dil1] against today [dil1]: NO CLEAR DIFFERENCE

```
JUDGE: rows+low [dil1] against today [dil1]

baseline  = the fixed model's mask with one pixel added around each color (3 x 3 dilation); DetConfig defaults
candidate = the fixed model's mask with one pixel added around each color (3 x 3 dilation); DetConfig bottom_rows=0.5,bottom_rule=low
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git 1ccdbaf, 2026-11-26; 0 s in the detectors.

BY PLACE (the verdict is computed on these)
                                            |                   TODAY [DIL1]                    |                  ROWS+LOW [DIL1]
                    lights frames brls plcm | found raw  box off    missed wrong 2nd none empty | found raw  box off    missed wrong 2nd none empty
---------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28  0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28  0.0 (0)   1.0 (1)     0   0    0     0
campus_study             1     21   35   35 |  34.0  34  1.0 (1)   0.0 (0)     0   0    0     0 |  34.0  34  1.0 (1)   0.0 (0)     0   0    0     0
abp_gray                 1      8   16   16 |  10.0  10  2.0 (2)   4.0 (4)     0   0    1     0 |   7.0   7  5.0 (5)   4.0 (4)     0   0    1     0
home_bathtile            4     28   60   15 |   4.5  18  0.0 (0) 10.5 (42)     0   0    0     0 |   4.2  17  0.2 (1) 10.5 (42)     0   0    0     0
home_glass               5     36   75   15 |  14.4  72  0.6 (3)   0.0 (0)     0   1    9     2 |  14.6  73  0.4 (2)   0.0 (0)     0   1    7     1
home_ottoman             3     21   45   15 |   4.7  14  0.7 (2)  9.7 (29)     0   0    1     0 |   4.0  12  0.7 (2) 10.3 (31)     0   0    1     0
uc_palewood              1      7   15   15 |  14.0  14  0.0 (0)   1.0 (1)     0   0    4     1 |  13.0  13  0.0 (0)   2.0 (2)     0   0    3     1
abp_white                1     17   32   32 |  27.0  27  0.0 (0)   5.0 (5)     0   0    0     0 |  27.0  27  0.0 (0)   5.0 (5)     0   0    0     0
---------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 136.6 217  4.3 (8) 31.2 (82)     0   1   15     3 | 131.8 211 7.3 (11) 32.8 (85)     0   1   12     2
---------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                   TODAY [DIL1]                   |                 ROWS+LOW [DIL1]
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_light              1     21   35   35 |  34.0  34 1.0 (1)   0.0 (0)     0   0    0     0 |  34.0  34 1.0 (1)   0.0 (0)     0   0    0     0
both_abpgray              1      8   16   16 |  10.0  10 2.0 (2)   4.0 (4)     0   0    1     0 |   7.0   7 5.0 (5)   4.0 (4)     0   0    1     0
lampcool6_bathtile        1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0
lampcool6_glass           1      7   15   15 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0
lampcool6_ottoman         1      7   15   15 |   6.0   6 1.0 (1)   8.0 (8)     0   0    0     0 |   6.0   6 0.0 (0)   9.0 (9)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    3     2 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     1
lampmid6_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     0
lampmid6_ottoman          1      7   15   15 |   8.0   8 0.0 (0)   7.0 (7)     0   0    0     0 |   6.0   6 1.0 (1)   8.0 (8)     0   0    0     0
lampwarm6_bathtile        1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    3     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     0
lampwarm6_ottoman         1      7   15   15 |   0.0   0 1.0 (1) 14.0 (14)     0   0    1     0 |   0.0   0 1.0 (1) 14.0 (14)     0   0    1     0
overheaddim_palewood      1      7   15   15 |  14.0  14 0.0 (0)   1.0 (1)     0   0    4     1 |  13.0  13 0.0 (0)   2.0 (2)     0   0    3     1
window_abpwhite           1     17   32   32 |  27.0  27 0.0 (0)   5.0 (5)     0   0    0     0 |  27.0  27 0.0 (0)   5.0 (5)     0   0    0     0
window_glass              1      8   15   15 |  13.0  13 2.0 (2)   0.0 (0)     0   1    1     0 |  14.0  14 1.0 (1)   0.0 (0)     0   1    1     0
--------------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                   TODAY [DIL1]                   |                 ROWS+LOW [DIL1]
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |   2.0   2 1.0 (1) 18.0 (18)     0   0    0     0 |   2.0   2 1.0 (1) 18.0 (18)     0   0    0     0
lampcool6_wood        1     10   21   21 |   5.0   5 2.0 (2) 14.0 (14)     2   0    0     0 |   4.0   4 2.0 (2) 15.0 (15)     2   0    0     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0
lampmid3_wood         1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0
lampmid6_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0
lampwarm3_wood        1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0
lampwarm6_wood        1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0
window_black          1     10   26   26 |   8.0   8 3.0 (3) 15.0 (15)     0   0    0     0 |   8.0   8 3.0 (3) 15.0 (15)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 3 gained, 9 lost, 1 moved between 'box off' and 'missed' (counted per frame)
  + 4A8B_campus_light_cluster_02 #4 blue at [379, 117, 419, 163]: off -> found
  + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found
  + 4A8B_window_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found
  - 4A8B_campus_light_room_01 #1 blue at [64, 123, 125, 181]: found -> off
  - 4A8B_both_abpgray_clutter_01 #1 blue at [34, 132, 110, 203]: found -> off
  - 4A8B_both_abpgray_clutter_01 #4 orange at [506, 124, 579, 190]: found -> off
  - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off
  - 4A8B_both_abpgray_occl_02 #1 blue at [366, 123, 422, 181]: found -> off
  - 4A8B_lampcool6_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: found -> off
  - 4A8B_lampmid6_ottoman_clutter_01 #3 orange at [313, 141, 401, 236]: found -> missed
  - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off
  - 4A8B_overheaddim_palewood_close_01 #1 orange at [291, 243, 566, 480]: found -> missed
  ~ 4A8B_lampcool6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: off -> missed
  report only: 3 gained, 4 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 3 frame(s)
  4A8B_lampmid3_glass_neg_02 [empty frame with clutter]: nothing 2 -> 1; now [('orange', (559, 122, 609, 163))]
  4A8B_lampwarm6_glass_clutter_01: nothing 2 -> 1; now [('orange', (556, 117, 605, 167))]
  4A8B_overheaddim_palewood_core_01: nothing 1 -> 0

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [within the noise] found, the ordinary conditions together: 136.6 -> 131.8 of 172 placements (-4.7; counted per frame 217 -> 211 of 307). Better above
      +4.0, worse below -10.9.
  [within the noise] found, place by place: abp_gray -3.0 of 16 (margin 6.0); home_bathtile -0.2 of 15 (margin 1.2); home_glass +0.2 of 15 (margin 1.0);
      home_ottoman -0.7 of 15 (margin 2.3); uc_palewood -1.0 of 15 (margin 1.0).
  [BETTER] boxes that are not on their barrel: 7.3 -> 5.9 counted once per arrangement (-1.4; per frame: on nothing 15 -> 12, second box 1 -> 1, wrong
      color 0 -> 0). Worse above +1.9, better below -1.0.
  [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 1.4 -> 1.2 per arrangement (margin
      1.0).

VERDICT: NO CLEAR DIFFERENCE. no count moved by more than a change that means nothing moves it.
```
