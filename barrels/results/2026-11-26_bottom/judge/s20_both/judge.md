# Judge: both [s20] against today [s20]: NO CLEAR DIFFERENCE

```
JUDGE: both [s20] against today [s20]

baseline  = both saturation floors lowered by 20 (orange 140 -> 120, blue 113 -> 93); DetConfig defaults
candidate = both saturation floors lowered by 20 (orange 140 -> 120, blue 113 -> 93); DetConfig bottom_rule=both
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git d86fd73, 2026-11-26; 0 s in the detectors.

BY PLACE (the verdict is computed on these)
                                            |                   TODAY [S20]                    |                    BOTH [S20]
                    lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
-------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  27.0  27 0.0 (0)   2.0 (2)     3   0    0     0 |  26.0  26 0.0 (0)   3.0 (3)     3   0    0     0
campus_study             1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
abp_gray                 1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0
home_bathtile            4     28   60   15 |   4.2  17 0.0 (0) 10.8 (43)     0   0    0     0 |   4.2  17 0.0 (0) 10.8 (43)     0   0    0     0
home_glass               5     36   75   15 |  14.0  70 1.0 (5)   0.0 (0)     2   0    9     3 |  14.4  72 0.6 (3)   0.0 (0)     2   0    9     3
home_ottoman             3     21   45   15 |   3.3  10 0.3 (1) 11.3 (34)     0   0    1     0 |   3.0   9 0.7 (2) 11.3 (34)     0   0    1     0
uc_palewood              1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0
abp_white                1     17   32   32 |  27.0  27 1.0 (1)   4.0 (4)     0   0    0     0 |  27.0  27 1.0 (1)   4.0 (4)     0   0    0     0
-------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 133.6 209 3.3 (8) 35.1 (90)     5   0   11     3 | 132.6 209 3.3 (7) 36.1 (91)     5   0   11     3
-------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                   TODAY [S20]                    |                    BOTH [S20]
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  27.0  27 0.0 (0)   2.0 (2)     3   0    0     0 |  26.0  26 0.0 (0)   3.0 (3)     3   0    0     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
both_abpgray              1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0
lampcool6_bathtile        1      7   15   15 |  14.0  14 0.0 (0)   1.0 (1)     0   0    0     0 |  14.0  14 0.0 (0)   1.0 (1)     0   0    0     0
lampcool6_glass           1      7   15   15 |  14.0  14 1.0 (1)   0.0 (0)     0   0    3     1 |  14.0  14 1.0 (1)   0.0 (0)     0   0    3     1
lampcool6_ottoman         1      7   15   15 |   4.0   4 0.0 (0) 11.0 (11)     0   0    0     0 |   3.0   3 1.0 (1) 11.0 (11)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampmid3_glass            1      7   15   15 |  13.0  13 2.0 (2)   0.0 (0)     1   0    2     1 |  14.0  14 1.0 (1)   0.0 (0)     1   0    2     1
lampmid6_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     1   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     1   0    1     0
lampmid6_ottoman          1      7   15   15 |   6.0   6 1.0 (1)   8.0 (8)     0   0    0     0 |   6.0   6 1.0 (1)   8.0 (8)     0   0    0     0
lampwarm6_bathtile        1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0
lampwarm6_ottoman         1      7   15   15 |   0.0   0 0.0 (0) 15.0 (15)     0   0    1     0 |   0.0   0 0.0 (0) 15.0 (15)     0   0    1     0
overheaddim_palewood      1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0
window_abpwhite           1     17   32   32 |  27.0  27 1.0 (1)   4.0 (4)     0   0    0     0 |  27.0  27 1.0 (1)   4.0 (4)     0   0    0     0
window_glass              1      8   15   15 |  13.0  13 2.0 (2)   0.0 (0)     0   0    2     1 |  14.0  14 1.0 (1)   0.0 (0)     0   0    2     1
--------------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                   TODAY [S20]                    |                    BOTH [S20]
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |   2.0   2 2.0 (2) 17.0 (17)     0   0    0     0 |   2.0   2 2.0 (2) 17.0 (17)     0   0    0     0
lampcool6_wood        1     10   21   21 |   6.0   6 2.0 (2) 13.0 (13)     3   0    0     0 |   6.0   6 2.0 (2) 13.0 (13)     3   0    0     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0
lampmid3_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     1   0    0     0 |   1.0   1 0.0 (0) 20.0 (20)     1   0    0     0
lampmid6_wood         1     10   21   21 |   0.0   0 2.0 (2) 19.0 (19)     2   0    0     0 |   0.0   0 2.0 (2) 19.0 (19)     2   0    0     0
lampwarm3_wood        1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0
lampwarm6_wood        1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0
window_black          1     10   26   26 |  10.0  10 0.0 (0) 16.0 (16)     0   0    0     0 |   9.0   9 1.0 (1) 16.0 (16)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 4 gained, 4 lost (counted per frame)
  + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found
  + 4A8B_lampcool6_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found
  + 4A8B_lampmid3_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found
  + 4A8B_window_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found
  - 4A8B_window_light_cluster_01 #1 orange at [313, 115, 356, 164]: found -> missed
  - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off
  - 4A8B_lampcool6_glass_edge_01 #1 blue at [0, 145, 40, 237]: found -> off
  - 4A8B_lampcool6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> off
  report only: 0 gained, 1 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 0 frame(s)

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [within the noise] found, the ordinary conditions together: 133.6 -> 132.6 of 172 placements (-0.9; counted per frame 209 -> 209 of 307). Better above
      +4.0, worse below -10.9.
  [within the noise] found, place by place: home_white -1.0 of 29 (margin 1.0); home_glass +0.4 of 15 (margin 1.0); home_ottoman -0.3 of 15 (margin
      2.3).
  [within the noise] boxes that are not on their barrel: 7.3 -> 7.3 counted once per arrangement (+0.0; per frame: on nothing 11 -> 11, second box 0 ->
      0, wrong color 5 -> 5). Worse above +1.9, better below -1.0.
  [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 1.4 -> 1.4 per arrangement (margin
      1.0).

VERDICT: NO CLEAR DIFFERENCE. no count moved by more than a change that means nothing moves it.
```
