# Judge: F2 against F0: NO CLEAR DIFFERENCE

```
JUDGE: F2 against F0

baseline  = F0 contrast alone (C1 as judged on wip/exp-contrast)
candidate = F2 F1, then boxes of SC/P2/NM/B4 kept when k of them agree and the checks pass: its choice picked on the other places
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git 50ca1a1, 2026-11-27; 0 s in the detectors.
LEAVE ONE PLACE OUT: every place was scored by a candidate fitted on the other places only; the verdict rests on held-out results.

BY PLACE (the verdict is computed on these)
                                            |                        F0                        |                        F2
                    lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
-------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_study             1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
abp_gray                 1      8   16   16 |  15.0  15 1.0 (1)   0.0 (0)     0   0    0     0 |  15.0  15 1.0 (1)   0.0 (0)     0   0    0     0
home_bathtile            4     28   60   15 |  13.5  54 0.0 (0)   1.5 (6)     1   1    0     0 |  13.5  54 0.0 (0)   1.5 (6)     1   1    0     0
home_glass               5     36   75   15 |  14.8  74 0.2 (1)   0.0 (0)     0   0    5     0 |  15.0  75 0.0 (0)   0.0 (0)     0   0    0     0
home_ottoman             3     21   45   15 |  10.0  30 0.0 (0)  5.0 (15)     0   0    1     0 |   9.3  28 0.7 (2)  5.0 (15)     0   0    1     0
uc_palewood              1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0
abp_white                1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0
-------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 155.3 275 1.2 (2) 15.5 (30)     1   1    7     0 | 154.8 274 1.7 (3) 15.5 (30)     1   1    2     0
-------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                       F0                       |                       F2
                     lights frames brls plcm | found raw box off  missed wrong 2nd none empty | found raw box off  missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  28.0  28 0.0 (0) 1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0) 1.0 (1)     0   0    0     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0) 0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0) 0.0 (0)     0   0    0     0
both_abpgray              1      8   16   16 |  15.0  15 1.0 (1) 0.0 (0)     0   0    0     0 |  15.0  15 1.0 (1) 0.0 (0)     0   0    0     0
lampcool6_bathtile        1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0
lampcool6_glass           1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0
lampcool6_ottoman         1      7   15   15 |  12.0  12 0.0 (0) 3.0 (3)     0   0    0     0 |  12.0  12 0.0 (0) 3.0 (3)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |  13.0  13 0.0 (0) 2.0 (2)     0   1    0     0 |  13.0  13 0.0 (0) 2.0 (2)     0   1    0     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0
lampmid6_bathtile         1      7   15   15 |  13.0  13 0.0 (0) 2.0 (2)     0   0    0     0 |  13.0  13 0.0 (0) 2.0 (2)     0   0    0     0
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0
lampmid6_ottoman          1      7   15   15 |  10.0  10 0.0 (0) 5.0 (5)     0   0    0     0 |   8.0   8 2.0 (2) 5.0 (5)     0   0    0     0
lampwarm6_bathtile        1      7   15   15 |  13.0  13 0.0 (0) 2.0 (2)     1   0    0     0 |  13.0  13 0.0 (0) 2.0 (2)     1   0    0     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    3     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0
lampwarm6_ottoman         1      7   15   15 |   8.0   8 0.0 (0) 7.0 (7)     0   0    1     0 |   8.0   8 0.0 (0) 7.0 (7)     0   0    1     0
overheaddim_palewood      1      7   15   15 |  13.0  13 0.0 (0) 2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0) 2.0 (2)     0   0    1     0
window_abpwhite           1     17   32   32 |  26.0  26 0.0 (0) 6.0 (6)     0   0    0     0 |  26.0  26 0.0 (0) 6.0 (6)     0   0    0     0
window_glass              1      8   15   15 |  14.0  14 1.0 (1) 0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                        F0                        |                        F2
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |  15.0  15 0.0 (0)   6.0 (6)     0   0    0     0 |  14.0  14 0.0 (0)   7.0 (7)     0   0    0     0
lampcool6_wood        1     10   21   21 |  11.0  11 3.0 (3)   7.0 (7)     2   0    0     0 |  10.0  10 2.0 (2)   9.0 (9)     1   0    0     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0
lampmid3_wood         1     10   21   21 |  12.0  12 1.0 (1)   8.0 (8)     1   0    0     0 |  13.0  13 0.0 (0)   8.0 (8)     1   0    0     0
lampmid6_wood         1     10   21   21 |  16.0  16 2.0 (2)   3.0 (3)     0   0    1     0 |  17.0  17 1.0 (1)   3.0 (3)     0   0    1     0
lampwarm3_wood        1     10   21   21 |  12.0  12 1.0 (1)   8.0 (8)     0   0    0     0 |  13.0  13 0.0 (0)   8.0 (8)     0   0    0     0
lampwarm6_wood        1     10   21   21 |  13.0  13 3.0 (3)   5.0 (5)     2   0    0     0 |  15.0  15 1.0 (1)   5.0 (5)     2   0    0     0
window_black          1     10   26   26 |   5.0   5 2.0 (2) 19.0 (19)     0   0    0     0 |   6.0   6 1.0 (1) 19.0 (19)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 1 gained, 2 lost (counted per frame)
  + 4A8B_window_glass_occl_02 #1 blue at [254, 114, 300, 163]: off -> found
  - 4A8B_lampmid6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: found -> off
  - 4A8B_lampmid6_ottoman_edge_01 #1 blue at [0, 141, 43, 229]: found -> off
  report only: 6 gained, 2 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 4 frame(s)
  4A8B_lampmid3_glass_occl_02: nothing 1 -> 0
  4A8B_lampmid6_glass_clutter_01: nothing 1 -> 0
  4A8B_lampwarm6_glass_clutter_01: nothing 1 -> 0
  4A8B_lampwarm6_glass_occl_02: nothing 2 -> 0

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [within the noise] found, the ordinary conditions together: 155.3 -> 154.8 of 172 placements (-0.5; counted per frame 275 -> 274 of 307). Better above
      +4.0, worse below -10.9.
  [within the noise] found, place by place: home_glass +0.2 of 15 (margin 1.0); home_ottoman -0.7 of 15 (margin 2.3).
  [within the noise] boxes that are not on their barrel: 2.8 -> 1.8 counted once per arrangement (-1.0; per frame: on nothing 7 -> 2, second box 1 -> 1,
      wrong color 1 -> 1). Worse above +1.9, better below -1.0.
  [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 0.0 per arrangement (margin
      1.0).

VERDICT: NO CLEAR DIFFERENCE. no count moved by more than a change that means nothing moves it.
```
