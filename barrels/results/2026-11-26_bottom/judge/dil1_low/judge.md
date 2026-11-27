# Judge: low [dil1] against today [dil1]: NO CLEAR DIFFERENCE

```
JUDGE: low [dil1] against today [dil1]

baseline  = the fixed model's mask with one pixel added around each color (3 x 3 dilation); DetConfig defaults
candidate = the fixed model's mask with one pixel added around each color (3 x 3 dilation); DetConfig bottom_rule=low
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git 1ccdbaf, 2026-11-26; 0 s in the detectors.

BY PLACE (the verdict is computed on these)
                                            |                   TODAY [DIL1]                    |                    LOW [DIL1]
                    lights frames brls plcm | found raw  box off    missed wrong 2nd none empty | found raw  box off    missed wrong 2nd none empty
---------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28  0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28  0.0 (0)   1.0 (1)     0   0    0     0
campus_study             1     21   35   35 |  34.0  34  1.0 (1)   0.0 (0)     0   0    0     0 |  33.0  33  2.0 (2)   0.0 (0)     0   0    0     0
abp_gray                 1      8   16   16 |  10.0  10  2.0 (2)   4.0 (4)     0   0    1     0 |   9.0   9  3.0 (3)   4.0 (4)     0   0    1     0
home_bathtile            4     28   60   15 |   4.5  18  0.0 (0) 10.5 (42)     0   0    0     0 |   4.5  18  0.0 (0) 10.5 (42)     0   0    0     0
home_glass               5     36   75   15 |  14.4  72  0.6 (3)   0.0 (0)     0   1    9     2 |  14.6  73  0.4 (2)   0.0 (0)     0   1    9     2
home_ottoman             3     21   45   15 |   4.7  14  0.7 (2)  9.7 (29)     0   0    1     0 |   4.3  13  1.0 (3)  9.7 (29)     0   0    1     0
uc_palewood              1      7   15   15 |  14.0  14  0.0 (0)   1.0 (1)     0   0    4     1 |  14.0  14  0.0 (0)   1.0 (1)     0   0    3     1
abp_white                1     17   32   32 |  27.0  27  0.0 (0)   5.0 (5)     0   0    0     0 |  27.0  27  0.0 (0)   5.0 (5)     0   0    0     0
---------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 136.6 217  4.3 (8) 31.2 (82)     0   1   15     3 | 134.4 215 6.4 (10) 31.2 (82)     0   1   14     3
---------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                   TODAY [DIL1]                   |                    LOW [DIL1]
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_light              1     21   35   35 |  34.0  34 1.0 (1)   0.0 (0)     0   0    0     0 |  33.0  33 2.0 (2)   0.0 (0)     0   0    0     0
both_abpgray              1      8   16   16 |  10.0  10 2.0 (2)   4.0 (4)     0   0    1     0 |   9.0   9 3.0 (3)   4.0 (4)     0   0    1     0
lampcool6_bathtile        1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampcool6_glass           1      7   15   15 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0
lampcool6_ottoman         1      7   15   15 |   6.0   6 1.0 (1)   8.0 (8)     0   0    0     0 |   6.0   6 1.0 (1)   8.0 (8)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    3     2 |  15.0  15 0.0 (0)   0.0 (0)     0   0    3     2
lampmid6_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     0
lampmid6_ottoman          1      7   15   15 |   8.0   8 0.0 (0)   7.0 (7)     0   0    0     0 |   7.0   7 1.0 (1)   7.0 (7)     0   0    0     0
lampwarm6_bathtile        1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    3     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    3     0
lampwarm6_ottoman         1      7   15   15 |   0.0   0 1.0 (1) 14.0 (14)     0   0    1     0 |   0.0   0 1.0 (1) 14.0 (14)     0   0    1     0
overheaddim_palewood      1      7   15   15 |  14.0  14 0.0 (0)   1.0 (1)     0   0    4     1 |  14.0  14 0.0 (0)   1.0 (1)     0   0    3     1
window_abpwhite           1     17   32   32 |  27.0  27 0.0 (0)   5.0 (5)     0   0    0     0 |  27.0  27 0.0 (0)   5.0 (5)     0   0    0     0
window_glass              1      8   15   15 |  13.0  13 2.0 (2)   0.0 (0)     0   1    1     0 |  14.0  14 1.0 (1)   0.0 (0)     0   1    1     0
--------------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                   TODAY [DIL1]                   |                    LOW [DIL1]
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |   2.0   2 1.0 (1) 18.0 (18)     0   0    0     0 |   2.0   2 1.0 (1) 18.0 (18)     0   0    0     0
lampcool6_wood        1     10   21   21 |   5.0   5 2.0 (2) 14.0 (14)     2   0    0     0 |   5.0   5 2.0 (2) 14.0 (14)     2   0    0     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0
lampmid3_wood         1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0
lampmid6_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0
lampwarm3_wood        1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0
lampwarm6_wood        1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0 |   0.0   0 0.0 (0) 21.0 (21)     0   0    0     0
window_black          1     10   26   26 |   8.0   8 3.0 (3) 15.0 (15)     0   0    0     0 |   9.0   9 2.0 (2) 15.0 (15)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 1 gained, 3 lost (counted per frame)
  + 4A8B_window_glass_clutter_01 #2 blue at [254, 114, 300, 163]: off -> found
  - 4A8B_campus_light_edge_01 #1 orange at [602, 143, 638, 228]: found -> off
  - 4A8B_both_abpgray_edge_01 #2 blue at [588, 150, 640, 260]: found -> off
  - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off
  report only: 1 gained, 0 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 1 frame(s)
  4A8B_overheaddim_palewood_core_01: nothing 1 -> 0

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [within the noise] found, the ordinary conditions together: 136.6 -> 134.4 of 172 placements (-2.1; counted per frame 217 -> 215 of 307). Better above
      +4.0, worse below -10.9.
  [within the noise] found, place by place: campus_study -1.0 of 35 (margin 1.0); abp_gray -1.0 of 16 (margin 6.0); home_glass +0.2 of 15 (margin 1.0);
      home_ottoman -0.3 of 15 (margin 2.3).
  [within the noise] boxes that are not on their barrel: 7.3 -> 6.3 counted once per arrangement (-1.0; per frame: on nothing 15 -> 14, second box 1 ->
      1, wrong color 0 -> 0). Worse above +1.9, better below -1.0.
  [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 1.4 -> 1.4 per arrangement (margin
      1.0).

VERDICT: NO CLEAR DIFFERENCE. no count moved by more than a change that means nothing moves it.
```
