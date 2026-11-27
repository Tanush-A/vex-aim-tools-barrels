# Judge: contrast_L against contrast: NO CLEAR DIFFERENCE

```
JUDGE: contrast_L against contrast

baseline  = the contrast winner (wip/exp-contrast, candidate.detect_frame, setting BEST), DetConfig defaults
candidate = the contrast winner (wip/exp-contrast, candidate.detect_frame, setting BEST), DetConfig defaults; paint checks L: label only, stripe over
    1.25 x a stripe height with body under 0.6 dropped (P)
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git 2bb405b, 2026-11-27; 0 s in the detectors.

BY PLACE (the verdict is computed on these)
                                            |                     CONTRAST                     |                    CONTRAST_L
                    lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
-------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_study             1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
abp_gray                 1      8   16   16 |  15.0  15 1.0 (1)   0.0 (0)     0   0    0     0 |  15.0  15 1.0 (1)   0.0 (0)     0   0    0     0
home_bathtile            4     28   60   15 |  13.5  54 0.0 (0)   1.5 (6)     1   1    0     0 |  13.5  54 0.0 (0)   1.5 (6)     0   1    0     0
home_glass               5     36   75   15 |  14.8  74 0.2 (1)   0.0 (0)     0   0    3     0 |  14.8  74 0.2 (1)   0.0 (0)     0   0    3     0
home_ottoman             3     21   45   15 |  10.7  32 0.0 (0)  4.3 (13)     0   0    1     0 |  10.7  32 0.0 (0)  4.3 (13)     0   0    1     0
uc_palewood              1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0
abp_white                1     17   32   32 |  27.0  27 1.0 (1)   4.0 (4)     0   0    0     0 |  27.0  27 1.0 (1)   4.0 (4)     0   0    0     0
-------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 157.0 278 2.2 (3) 12.8 (26)     1   1    5     0 | 157.0 278 2.2 (3) 12.8 (26)     0   1    5     0
-------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                    CONTRAST                    |                   CONTRAST_L
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
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    2     0
lampmid6_ottoman          1      7   15   15 |  11.0  11 0.0 (0) 4.0 (4)     0   0    0     0 |  11.0  11 0.0 (0) 4.0 (4)     0   0    0     0
lampwarm6_bathtile        1      7   15   15 |  13.0  13 0.0 (0) 2.0 (2)     1   0    0     0 |  13.0  13 0.0 (0) 2.0 (2)     0   0    0     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    1     0
lampwarm6_ottoman         1      7   15   15 |   9.0   9 0.0 (0) 6.0 (6)     0   0    1     0 |   9.0   9 0.0 (0) 6.0 (6)     0   0    1     0
overheaddim_palewood      1      7   15   15 |  13.0  13 0.0 (0) 2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0) 2.0 (2)     0   0    1     0
window_abpwhite           1     17   32   32 |  27.0  27 1.0 (1) 4.0 (4)     0   0    0     0 |  27.0  27 1.0 (1) 4.0 (4)     0   0    0     0
window_glass              1      8   15   15 |  14.0  14 1.0 (1) 0.0 (0)     0   0    0     0 |  14.0  14 1.0 (1) 0.0 (0)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                     CONTRAST                     |                    CONTRAST_L
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |  15.0  15 0.0 (0)   6.0 (6)     0   0    0     0 |  15.0  15 0.0 (0)   6.0 (6)     0   0    0     0
lampcool6_wood        1     10   21   21 |  11.0  11 3.0 (3)   7.0 (7)     2   0    0     0 |  13.0  13 2.0 (2)   6.0 (6)     1   0    0     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0
lampmid3_wood         1     10   21   21 |  12.0  12 1.0 (1)   8.0 (8)     1   0    0     0 |  12.0  12 1.0 (1)   8.0 (8)     1   0    0     0
lampmid6_wood         1     10   21   21 |  16.0  16 2.0 (2)   3.0 (3)     0   0    1     0 |  16.0  16 2.0 (2)   3.0 (3)     0   0    1     0
lampwarm3_wood        1     10   21   21 |  12.0  12 1.0 (1)   8.0 (8)     0   0    0     0 |  12.0  12 1.0 (1)   8.0 (8)     0   0    0     0
lampwarm6_wood        1     10   21   21 |  13.0  13 3.0 (3)   5.0 (5)     2   0    0     0 |  13.0  13 3.0 (3)   5.0 (5)     2   0    0     0
window_black          1     10   26   26 |   5.0   5 2.0 (2) 19.0 (19)     0   0    0     0 |   5.0   5 2.0 (2) 19.0 (19)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 0 gained, 0 lost (counted per frame)
  report only: 3 gained, 1 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 3 frame(s)
  4A8B_lampmid3_glass_occl_02: nothing 1 -> 0
  4A8B_lampmid6_glass_clutter_01: nothing 1 -> 2; now [('orange', (561, 117, 610, 172)), ('orange', (570, 108, 605, 146))]
  4A8B_lampwarm6_bathtile_core_01: wrong color 1 -> 0

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [within the noise] found, the ordinary conditions together: 157.0 -> 157.0 of 172 placements (+0.0; counted per frame 278 -> 278 of 307). Better above
      +4.0, worse below -10.9.
  [within the noise] found, place by place: no place moved.
  [within the noise] boxes that are not on their barrel: 2.4 -> 2.2 counted once per arrangement (-0.2; per frame: on nothing 5 -> 5, second box 1 -> 1,
      wrong color 1 -> 0). Worse above +1.9, better below -1.0.
  [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 0.0 per arrangement (margin
      1.0).

VERDICT: NO CLEAR DIFFERENCE. no count moved by more than a change that means nothing moves it.
```
