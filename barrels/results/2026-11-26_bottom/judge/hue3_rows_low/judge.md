# Judge: rows+low [hue3] against today [hue3]: NO CLEAR DIFFERENCE

```
JUDGE: rows+low [hue3] against today [hue3]

baseline  = both hue ranges widened by 3 at each end (orange 0-16, blue 100-122); DetConfig defaults
candidate = both hue ranges widened by 3 at each end (orange 0-16, blue 100-122); DetConfig bottom_rows=0.5,bottom_rule=low
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git 1ccdbaf, 2026-11-26; 0 s in the detectors.

BY PLACE (the verdict is computed on these)
                                            |                   TODAY [HUE3]                   |                 ROWS+LOW [HUE3]
                    lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
-------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 1.0 (1)   0.0 (0)     0   0    0     0
campus_study             1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  34.0  34 1.0 (1)   0.0 (0)     0   0    0     0
abp_gray                 1      8   16   16 |  15.0  15 1.0 (1)   0.0 (0)     0   0    0     0 |  14.0  14 2.0 (2)   0.0 (0)     0   0    0     0
home_bathtile            4     28   60   15 |   4.0  16 0.0 (0) 11.0 (44)     1   0    0     0 |   3.8  15 0.2 (1) 11.0 (44)     1   0    1     0
home_glass               5     36   75   15 |  14.8  74 0.2 (1)   0.0 (0)     0   0    6     3 |  15.0  75 0.0 (0)   0.0 (0)     0   0    6     3
home_ottoman             3     21   45   15 |   8.3  25 0.7 (2)  6.0 (18)     0   1    1     0 |   8.3  25 1.0 (3)  5.7 (17)     0   2    1     0
uc_palewood              1      7   15   15 |  11.0  11 0.0 (0)   4.0 (4)     0   0    2     0 |  11.0  11 0.0 (0)   4.0 (4)     0   0    2     0
abp_white                1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0
-------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 142.1 230 1.9 (4) 28.0 (73)     1   1    9     3 | 140.1 228 5.2 (8) 26.7 (71)     1   2   10     3
-------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                   TODAY [HUE3]                   |                 ROWS+LOW [HUE3]
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 1.0 (1)   0.0 (0)     0   0    0     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  34.0  34 1.0 (1)   0.0 (0)     0   0    0     0
both_abpgray              1      8   16   16 |  15.0  15 1.0 (1)   0.0 (0)     0   0    0     0 |  14.0  14 2.0 (2)   0.0 (0)     0   0    0     0
lampcool6_bathtile        1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0 |  12.0  12 1.0 (1)   2.0 (2)     0   0    0     0
lampcool6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     1 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     1
lampcool6_ottoman         1      7   15   15 |  13.0  13 1.0 (1)   1.0 (1)     0   1    0     0 |  14.0  14 0.0 (0)   1.0 (1)     0   2    0     0
lampmid3_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     1 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     1
lampmid6_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     1   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     1   0    1     0
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     1 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     1
lampmid6_ottoman          1      7   15   15 |  11.0  11 1.0 (1)   3.0 (3)     0   0    0     0 |   9.0   9 3.0 (3)   3.0 (3)     0   0    0     0
lampwarm6_bathtile        1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0
lampwarm6_ottoman         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    1     0 |   2.0   2 0.0 (0) 13.0 (13)     0   0    1     0
overheaddim_palewood      1      7   15   15 |  11.0  11 0.0 (0)   4.0 (4)     0   0    2     0 |  11.0  11 0.0 (0)   4.0 (4)     0   0    2     0
window_abpwhite           1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0
window_glass              1      8   15   15 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
--------------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                   TODAY [HUE3]                   |                 ROWS+LOW [HUE3]
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |   3.0   3 0.0 (0) 18.0 (18)     1   0    0     0 |   3.0   3 0.0 (0) 18.0 (18)     1   0    0     0
lampcool6_wood        1     10   21   21 |   6.0   6 1.0 (1) 14.0 (14)     2   0    0     0 |   6.0   6 1.0 (1) 14.0 (14)     1   0    0     0
lampmid3_ottoman      1      7   15   15 |   0.0   0 1.0 (1) 14.0 (14)     0   0    0     0 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0
lampmid3_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0
lampmid6_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0
lampwarm3_wood        1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    1     0 |   1.0   1 0.0 (0) 20.0 (20)     0   0    1     0
lampwarm6_wood        1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     1   0    0     0 |   0.0   0 0.0 (0) 21.0 (21)     1   0    0     0
window_black          1     10   26   26 |  12.0  12 4.0 (4) 10.0 (10)     0   0    0     0 |  12.0  12 2.0 (2) 12.0 (12)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 5 gained, 7 lost, 2 moved between 'box off' and 'missed' (counted per frame)
  + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: off -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: off -> found
  + 4A8B_lampmid6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found
  + 4A8B_lampwarm6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found
  + 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found
  - 4A8B_campus_light_room_01 #1 blue at [64, 123, 125, 181]: found -> off
  - 4A8B_both_abpgray_clutter_01 #1 blue at [34, 132, 110, 203]: found -> off
  - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off
  - 4A8B_lampcool6_bathtile_edge_01 #1 blue at [0, 127, 31, 196]: found -> off
  - 4A8B_lampmid6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: found -> off
  - 4A8B_lampmid6_ottoman_edge_01 #1 blue at [0, 141, 43, 229]: found -> off
  - 4A8B_lampmid6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off
  ~ 4A8B_window_light_cluster_01 #3 orange at [361, 117, 400, 163]: missed -> off
  ~ 4A8B_lampmid6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: off -> missed
  report only: 3 gained, 2 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 2 frame(s)
  4A8B_lampcool6_ottoman_clutter_01: second 0 -> 1; now [('blue', (62, 147, 151, 239))]
  4A8B_lampmid6_bathtile_touch_01: nothing 0 -> 1; now [('orange', (368, 111, 410, 157)), ('orange', (391, 109, 434, 146))]

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [within the noise] found, the ordinary conditions together: 142.1 -> 140.1 of 172 placements (-2.1; counted per frame 230 -> 228 of 307). Better above
      +4.0, worse below -10.9.
  [within the noise] found, place by place: campus_study -1.0 of 35 (margin 1.0); abp_gray -1.0 of 16 (margin 6.0); home_bathtile -0.2 of 15 (margin
      1.2); home_glass +0.2 of 15 (margin 1.0).
  [within the noise] boxes that are not on their barrel: 4.1 -> 4.7 counted once per arrangement (+0.6; per frame: on nothing 9 -> 10, second box 1 ->
      2, wrong color 1 -> 1). Worse above +1.9, better below -1.0.
  [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.6 -> 0.6 per arrangement (margin
      1.0).

VERDICT: NO CLEAR DIFFERENCE. no count moved by more than a change that means nothing moves it.
```
