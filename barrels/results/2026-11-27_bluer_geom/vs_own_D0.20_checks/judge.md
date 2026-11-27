# Judge: D0.20_checks against D0.20_no_checks: PASS

```
JUDGE: D0.20_checks against D0.20_no_checks

baseline  = D bluer than the light by 0.20 (ramp chosen in the fold), no checks; fitted leave one place out
candidate = D bluer than the light by 0.20 (ramp chosen in the fold) plus the checks; fitted leave one place out
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git 3094b20, 2026-11-26; 23 s in the detectors.
LEAVE ONE PLACE OUT: every place was scored by a candidate fitted on the other places only; the verdict rests on held-out results.

BY PLACE (the verdict is computed on these)
                                            |                 D0.20_NO_CHECKS                  |                   D0.20_CHECKS
                    lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
-------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_study             1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
abp_gray                 1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0
home_bathtile            4     28   60   15 |  14.0  56 0.0 (0)   1.0 (4)     1   1    6     3 |  14.0  56 0.0 (0)   1.0 (4)     1   1    3     1
home_glass               5     36   75   15 |  14.8  74 0.2 (1)   0.0 (0)     0   0    3     0 |  14.8  74 0.2 (1)   0.0 (0)     0   0    2     0
home_ottoman             3     21   45   15 |   3.0   9 0.0 (0) 12.0 (36)     0   0    1     0 |   5.0  15 0.0 (0) 10.0 (30)     1   0    0     0
uc_palewood              1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0
abp_white                1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0
-------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 143.8 251 1.2 (2) 27.0 (54)     1   1   11     3 | 145.8 257 1.2 (2) 25.0 (48)     2   1    5     1
-------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                 D0.20_NO_CHECKS                  |                   D0.20_CHECKS
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
both_abpgray              1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0
lampcool6_bathtile        1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0
lampcool6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampcool6_ottoman         1      7   15   15 |   3.0   3 0.0 (0) 12.0 (12)     0   0    0     0 |   3.0   3 0.0 (0) 12.0 (12)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   1    0     0 |  15.0  15 0.0 (0)   0.0 (0)     0   1    0     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampmid6_bathtile         1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     1 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0
lampmid6_ottoman          1      7   15   15 |   6.0   6 0.0 (0)   9.0 (9)     0   0    0     0 |   6.0   6 0.0 (0)   9.0 (9)     0   0    0     0
lampwarm6_bathtile        1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     1   0    4     2 |  13.0  13 0.0 (0)   2.0 (2)     1   0    2     1
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0
lampwarm6_ottoman         1      7   15   15 |   0.0   0 0.0 (0) 15.0 (15)     0   0    1     0 |   6.0   6 0.0 (0)   9.0 (9)     1   0    0     0
overheaddim_palewood      1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0
window_abpwhite           1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0
window_glass              1      8   15   15 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0
--------------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                 D0.20_NO_CHECKS                  |                   D0.20_CHECKS
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |   2.0   2 0.0 (0) 19.0 (19)     0   0    0     0 |   1.0   1 1.0 (1) 19.0 (19)     0   0    0     0
lampcool6_wood        1     10   21   21 |   2.0   2 2.0 (2) 17.0 (17)     2   0    0     0 |   5.0   5 1.0 (1) 15.0 (15)     0   0    0     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0
lampmid3_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     1   0    0     0 |   4.0   4 0.0 (0) 17.0 (17)     1   0    0     0
lampmid6_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   6.0   6 2.0 (2) 13.0 (13)     0   0    1     0
lampwarm3_wood        1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   3.0   3 2.0 (2) 16.0 (16)     1   0    0     0
lampwarm6_wood        1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     1   0    0     0 |   9.0   9 1.0 (1) 11.0 (11)     1   0    0     0
window_black          1     10   26   26 |   5.0   5 1.0 (1) 20.0 (20)     0   0    0     0 |   5.0   5 1.0 (1) 20.0 (20)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 6 gained, 0 lost (counted per frame)
  + 4A8B_lampwarm6_ottoman_clutter_01 #2 blue at [288, 116, 333, 163]: missed -> found
  + 4A8B_lampwarm6_ottoman_clutter_01 #3 orange at [313, 141, 401, 236]: missed -> found
  + 4A8B_lampwarm6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: missed -> found
  + 4A8B_lampwarm6_ottoman_core_01 #4 orange at [415, 126, 479, 191]: missed -> found
  + 4A8B_lampwarm6_ottoman_edge_01 #2 orange at [267, 139, 351, 231]: missed -> found
  + 4A8B_lampwarm6_ottoman_touch_01 #3 orange at [324, 128, 389, 199]: missed -> found
  report only: 23 gained, 2 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 7 frame(s)
  4A8B_lampmid3_glass_occl_02: nothing 1 -> 0
  4A8B_lampmid6_bathtile_neg_02 [empty frame with clutter]: nothing 1 -> 0
  4A8B_lampwarm6_bathtile_neg_02 [empty frame with clutter]: nothing 2 -> 1; now [('orange', (528, 111, 571, 160))]
  4A8B_lampwarm6_bathtile_occl_02: nothing 2 -> 1; now [('orange', (531, 111, 577, 163))]
  4A8B_lampwarm6_ottoman_core_01: nothing 1 -> 0
  4A8B_lampwarm6_ottoman_touch_01: wrong color 0 -> 1; now [('blue', (298, 129, 357, 184))]
  4A8B_overheaddim_palewood_core_01: nothing 1 -> 0

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [within the noise] found, the ordinary conditions together: 143.8 -> 145.8 of 172 placements (+2.0; counted per frame 251 -> 257 of 307). Better above
      +4.0, worse below -10.9.
  [within the noise] found, place by place: home_ottoman +2.0 of 15 (margin 2.3).
  [BETTER] boxes that are not on their barrel: 3.9 -> 2.0 counted once per arrangement (-2.0; per frame: on nothing 11 -> 5, second box 1 -> 1, wrong
      color 1 -> 2). Worse above +1.9, better below -1.0.
  [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.8 -> 0.2 per arrangement (margin
      1.0).

VERDICT: PASS. boxes that are not on their barrel are down by more than the noise, found is not lower, and nothing is worse by more than the noise.
```
