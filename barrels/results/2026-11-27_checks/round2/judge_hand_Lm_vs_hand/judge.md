# Judge: hand_Lm against hand: NO CLEAR DIFFERENCE

```
JUDGE: hand_Lm against hand

baseline  = the hand thresholds per condition (median of its slider labels), DetConfig defaults
candidate = the hand thresholds per condition (median of its slider labels), DetConfig defaults; paint checks Lm: label only, over 1.5 x with body
    under 0.6 (M)
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git 625f33f, 2026-11-27; 0 s in the detectors.

BY PLACE (the verdict is computed on these)
                                            |                       HAND                       |                     HAND_LM
                    lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
-------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_study             1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
abp_gray                 1      8   16   16 |  15.0  15 1.0 (1)   0.0 (0)     0   0    0     0 |  15.0  15 1.0 (1)   0.0 (0)     0   0    0     0
home_bathtile            4     28   60   15 |  12.5  50 0.2 (1)   2.2 (9)     0   0    2     2 |  12.5  50 0.2 (1)   2.2 (9)     0   0    2     2
home_glass               5     36   75   15 |  15.0  75 0.0 (0)   0.0 (0)     0   0    0     0 |  15.0  75 0.0 (0)   0.0 (0)     0   0    0     0
home_ottoman             3     21   45   15 |  13.3  40 0.7 (2)   1.0 (3)     0   0    0     0 |  13.3  40 0.7 (2)   1.0 (3)     0   0    0     0
uc_palewood              1      7   15   15 |  12.0  12 0.0 (0)   3.0 (3)     1   0    0     0 |  12.0  12 0.0 (0)   3.0 (3)     1   0    0     0
abp_white                1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0
-------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 156.8 281 1.9 (4) 13.2 (22)     1   0    2     2 | 156.8 281 1.9 (4) 13.2 (22)     1   0    2     2
-------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                      HAND                      |                    HAND_LM
                     lights frames brls plcm | found raw box off  missed wrong 2nd none empty | found raw box off  missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  28.0  28 0.0 (0) 1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0) 1.0 (1)     0   0    0     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0) 0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0) 0.0 (0)     0   0    0     0
both_abpgray              1      8   16   16 |  15.0  15 1.0 (1) 0.0 (0)     0   0    0     0 |  15.0  15 1.0 (1) 0.0 (0)     0   0    0     0
lampcool6_bathtile        1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    1     1 |  15.0  15 0.0 (0) 0.0 (0)     0   0    1     1
lampcool6_glass           1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0
lampcool6_ottoman         1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |  14.0  14 1.0 (1) 0.0 (0)     0   0    0     0 |  14.0  14 1.0 (1) 0.0 (0)     0   0    0     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0
lampmid6_bathtile         1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    1     1 |  15.0  15 0.0 (0) 0.0 (0)     0   0    1     1
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0
lampmid6_ottoman          1      7   15   15 |  13.0  13 1.0 (1) 1.0 (1)     0   0    0     0 |  13.0  13 1.0 (1) 1.0 (1)     0   0    0     0
lampwarm6_bathtile        1      7   15   15 |   6.0   6 0.0 (0) 9.0 (9)     0   0    0     0 |   6.0   6 0.0 (0) 9.0 (9)     0   0    0     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0
lampwarm6_ottoman         1      7   15   15 |  12.0  12 1.0 (1) 2.0 (2)     0   0    0     0 |  12.0  12 1.0 (1) 2.0 (2)     0   0    0     0
overheaddim_palewood      1      7   15   15 |  12.0  12 0.0 (0) 3.0 (3)     1   0    0     0 |  12.0  12 0.0 (0) 3.0 (3)     1   0    0     0
window_abpwhite           1     17   32   32 |  26.0  26 0.0 (0) 6.0 (6)     0   0    0     0 |  26.0  26 0.0 (0) 6.0 (6)     0   0    0     0
window_glass              1      8   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                       HAND                       |                     HAND_LM
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |   2.0   2 0.0 (0) 19.0 (19)     0   0    0     0 |   2.0   2 0.0 (0) 19.0 (19)     0   0    0     0
lampcool6_wood        1     10   21   21 |   2.0   2 2.0 (2) 17.0 (17)     2   0    0     0 |   2.0   2 2.0 (2) 17.0 (17)     2   0    0     0
lampmid3_ottoman      1      7   15   15 |   0.0   0 1.0 (1) 14.0 (14)     0   0    0     0 |   0.0   0 1.0 (1) 14.0 (14)     0   0    0     0
lampmid3_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     1   0    0     0 |   1.0   1 0.0 (0) 20.0 (20)     1   0    0     0
lampmid6_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0
lampwarm3_wood        1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0
lampwarm6_wood        1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     1   0    0     0 |   0.0   0 0.0 (0) 21.0 (21)     1   0    0     0
window_black          1     10   26   26 |   5.0   5 1.0 (1) 20.0 (20)     0   0    0     0 |   5.0   5 1.0 (1) 20.0 (20)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 0 gained, 0 lost (counted per frame)

BOXES NOT ON THEIR BARREL that changed: 0 frame(s)

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [within the noise] found, the ordinary conditions together: 156.8 -> 156.8 of 172 placements (+0.0; counted per frame 281 -> 281 of 307). Better above
      +4.0, worse below -10.9.
  [within the noise] found, place by place: no place moved.
  [within the noise] boxes that are not on their barrel: 1.5 -> 1.5 counted once per arrangement (+0.0; per frame: on nothing 2 -> 2, second box 0 -> 0,
      wrong color 1 -> 1). Worse above +1.9, better below -1.0.
  [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.5 -> 0.5 per arrangement (margin
      1.0).

VERDICT: NO CLEAR DIFFERENCE. no count moved by more than a change that means nothing moves it.
```
