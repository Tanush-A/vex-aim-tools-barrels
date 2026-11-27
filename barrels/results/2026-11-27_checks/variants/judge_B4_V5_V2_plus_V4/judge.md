# Judge: B4_V5_V2_plus_V4 against B4_none: PASS

```
JUDGE: B4_V5_V2_plus_V4 against B4_none

baseline  = B4, stage-11 variant none
candidate = B4, stage-11 variant V5_V2_plus_V4
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git d5f1fb6, 2026-11-27; 0 s in the detectors.

BY PLACE (the verdict is computed on these)
                                            |                     B4_NONE                      |                 B4_V5_V2_PLUS_V4
                    lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
-------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_study             1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
abp_gray                 1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0
home_bathtile            4     28   60   15 |  14.2  57 0.0 (0)   0.8 (3)     1   1   17     5 |  14.2  57 0.0 (0)   0.8 (3)     1   1   10     3
home_glass               5     36   75   15 |  14.8  74 0.2 (1)   0.0 (0)     0   0    3     0 |  14.8  74 0.2 (1)   0.0 (0)     0   0    0     0
home_ottoman             3     21   45   15 |   4.7  14 0.0 (0) 10.3 (31)     1   0    0     0 |   4.7  14 0.0 (0) 10.3 (31)     1   0    0     0
uc_palewood              1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0
abp_white                1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0
-------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 145.7 257 1.2 (2) 25.1 (48)     2   1   21     5 | 145.7 257 1.2 (2) 25.1 (48)     2   1   11     3
-------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                     B4_NONE                      |                 B4_V5_V2_PLUS_V4
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
both_abpgray              1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0
lampcool6_bathtile        1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0
lampcool6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampcool6_ottoman         1      7   15   15 |   3.0   3 0.0 (0) 12.0 (12)     0   0    0     0 |   3.0   3 0.0 (0) 12.0 (12)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   1    4     1 |  15.0  15 0.0 (0)   0.0 (0)     0   1    3     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampmid6_bathtile         1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    3     1 |  15.0  15 0.0 (0)   0.0 (0)     0   0    3     1
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampmid6_ottoman          1      7   15   15 |   6.0   6 0.0 (0)   9.0 (9)     0   0    0     0 |   6.0   6 0.0 (0)   9.0 (9)     0   0    0     0
lampwarm6_bathtile        1      7   15   15 |  14.0  14 0.0 (0)   1.0 (1)     1   0   10     3 |  14.0  14 0.0 (0)   1.0 (1)     1   0    4     2
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampwarm6_ottoman         1      7   15   15 |   5.0   5 0.0 (0) 10.0 (10)     1   0    0     0 |   5.0   5 0.0 (0) 10.0 (10)     1   0    0     0
overheaddim_palewood      1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0
window_abpwhite           1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0
window_glass              1      8   15   15 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0
--------------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                     B4_NONE                      |                 B4_V5_V2_PLUS_V4
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |   2.0   2 0.0 (0) 19.0 (19)     0   0    0     0 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0
lampcool6_wood        1     10   21   21 |   2.0   2 2.0 (2) 17.0 (17)     2   0    0     0 |   2.0   2 1.0 (1) 18.0 (18)     1   0    0     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0
lampmid3_wood         1     10   21   21 |   2.0   2 0.0 (0) 19.0 (19)     1   0    0     0 |   2.0   2 0.0 (0) 19.0 (19)     1   0    0     0
lampmid6_wood         1     10   21   21 |   3.0   3 0.0 (0) 18.0 (18)     0   0    0     0 |   3.0   3 0.0 (0) 18.0 (18)     0   0    0     0
lampwarm3_wood        1     10   21   21 |   1.0   1 1.0 (1) 19.0 (19)     0   0    0     0 |   1.0   1 1.0 (1) 19.0 (19)     0   0    0     0
lampwarm6_wood        1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     2   0    0     0 |   1.0   1 0.0 (0) 20.0 (20)     2   0    0     0
window_black          1     10   26   26 |   5.0   5 1.0 (1) 20.0 (20)     0   0    0     0 |   5.0   5 1.0 (1) 20.0 (20)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 0 gained, 0 lost (counted per frame)
  report only: 0 gained, 1 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 6 frame(s)
  4A8B_lampmid3_bathtile_neg_02 [empty frame with clutter]: nothing 1 -> 0
  4A8B_lampmid3_glass_occl_02: nothing 1 -> 0
  4A8B_lampmid6_glass_clutter_01: nothing 1 -> 0
  4A8B_lampwarm6_bathtile_neg_02 [empty frame with clutter]: nothing 3 -> 2; now [('blue', (305, 95, 332, 121)), ('orange', (527, 111, 581, 160))]
  4A8B_lampwarm6_bathtile_occl_02: nothing 6 -> 1; now [('orange', (527, 111, 580, 161))]
  4A8B_lampwarm6_glass_clutter_01: nothing 1 -> 0

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [within the noise] found, the ordinary conditions together: 145.7 -> 145.7 of 172 placements (+0.0; counted per frame 257 -> 257 of 307). Better above
      +4.0, worse below -10.9.
  [within the noise] found, place by place: no place moved.
  [BETTER] boxes that are not on their barrel: 6.7 -> 4.3 counted once per arrangement (-2.3; per frame: on nothing 21 -> 11, second box 1 -> 1, wrong
      color 2 -> 2). Worse above +1.9, better below -1.0.
  [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 1.2 -> 0.8 per arrangement (margin
      1.0).

VERDICT: PASS. boxes that are not on their barrel are down by more than the noise, found is not lower, and nothing is worse by more than the noise.
```
