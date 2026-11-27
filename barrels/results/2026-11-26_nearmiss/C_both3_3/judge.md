# Judge: C_both3_3 against baseline: PASS

```
JUDGE: C_both3_3 against baseline

baseline  = today's default (the adopted color model, DetConfig defaults)
candidate = pc:3,3,pred: partner-conditioned: stripe direction level 3 (hue +-10, S -60, V >= 25), body direction level 3 (hue +-10, S -60, V >= 25),
    edges 'pred'; then detector.detect with DetConfig defaults
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git c648d95, 2026-11-26; 70 s in the detectors.

BY PLACE (the verdict is computed on these)
                                            |                     BASELINE                     |                    C_BOTH3_3
                    lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
-------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_study             1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
abp_gray                 1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  16.0  16 0.0 (0)   0.0 (0)     0   0    0     0
home_bathtile            4     28   60   15 |   4.0  16 0.0 (0) 11.0 (44)     0   0    0     0 |   7.0  28 0.2 (1)  7.8 (31)     0   1    0     0
home_glass               5     36   75   15 |  14.8  74 0.2 (1)   0.0 (0)     0   0    3     0 |  14.8  74 0.2 (1)   0.0 (0)     0   0    3     0
home_ottoman             3     21   45   15 |   3.0   9 0.0 (0) 12.0 (36)     0   0    1     0 |   7.3  22 0.3 (1)  7.3 (22)     0   2    1     0
uc_palewood              1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0
abp_white                1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  27.0  27 0.0 (0)   5.0 (5)     0   0    0     0
-------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 133.8 211 1.2 (2) 37.0 (94)     0   0    5     0 | 148.1 243 0.8 (3) 23.1 (61)     0   3    5     0
-------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                     BASELINE                     |                    C_BOTH3_3
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
both_abpgray              1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  16.0  16 0.0 (0)   0.0 (0)     0   0    0     0
lampcool6_bathtile        1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampcool6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampcool6_ottoman         1      7   15   15 |   3.0   3 0.0 (0) 12.0 (12)     0   0    0     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   4.0   4 1.0 (1) 10.0 (10)     0   1    0     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0
lampmid6_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   8.0   8 0.0 (0)   7.0 (7)     0   0    0     0
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0
lampmid6_ottoman          1      7   15   15 |   6.0   6 0.0 (0)   9.0 (9)     0   0    0     0 |   9.0   9 1.0 (1)   5.0 (5)     0   2    0     0
lampwarm6_bathtile        1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0
lampwarm6_ottoman         1      7   15   15 |   0.0   0 0.0 (0) 15.0 (15)     0   0    1     0 |   0.0   0 0.0 (0) 15.0 (15)     0   0    1     0
overheaddim_palewood      1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0
window_abpwhite           1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  27.0  27 0.0 (0)   5.0 (5)     0   0    0     0
window_glass              1      8   15   15 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0
--------------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                     BASELINE                     |                    C_BOTH3_3
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |   2.0   2 0.0 (0) 19.0 (19)     0   0    0     0 |   5.0   5 1.0 (1) 15.0 (15)     0   0    0     0
lampcool6_wood        1     10   21   21 |   2.0   2 2.0 (2) 17.0 (17)     2   0    0     0 |   8.0   8 0.0 (0) 13.0 (13)     0   0    0     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0
lampmid3_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     1   0    0     0 |   1.0   1 0.0 (0) 20.0 (20)     1   0    0     0
lampmid6_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   1.0   1 1.0 (1) 19.0 (19)     0   0    1     0
lampwarm3_wood        1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0
lampwarm6_wood        1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     1   0    0     0 |   0.0   0 0.0 (0) 21.0 (21)     1   0    0     0
window_black          1     10   26   26 |   5.0   5 1.0 (1) 20.0 (20)     0   0    0     0 |  13.0  13 4.0 (4)   9.0 (9)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 32 gained, 0 lost, 2 moved between 'box off' and 'missed' (counted per frame)
  + 4A8B_both_abpgray_clutter_01 #2 orange at [205, 114, 246, 158]: off -> found
  + 4A8B_both_abpgray_core_01 #2 blue at [233, 165, 353, 299]: missed -> found
  + 4A8B_both_abpgray_core_01 #4 orange at [408, 125, 472, 192]: missed -> found
  + 4A8B_both_abpgray_edge_01 #1 orange at [291, 127, 356, 197]: missed -> found
  + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: missed -> found
  + 4A8B_both_abpgray_touch_01 #2 blue at [246, 123, 301, 181]: missed -> found
  + 4A8B_lampcool6_bathtile_clutter_01 #3 orange at [410, 108, 442, 141]: missed -> found
  + 4A8B_lampcool6_bathtile_occl_02 #1 orange at [346, 107, 376, 137]: missed -> found
  + 4A8B_lampcool6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #1 blue at [79, 146, 177, 241]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #2 blue at [288, 116, 333, 163]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #3 orange at [313, 141, 401, 236]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #4 orange at [541, 129, 613, 202]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #4 orange at [413, 126, 479, 190]: missed -> found
  + 4A8B_lampcool6_ottoman_edge_01 #1 blue at [0, 141, 43, 229]: missed -> found
  + 4A8B_lampcool6_ottoman_edge_01 #2 orange at [267, 139, 351, 231]: missed -> found
  + 4A8B_lampmid3_bathtile_clutter_01 #3 orange at [410, 108, 442, 141]: missed -> found
  + 4A8B_lampmid3_bathtile_core_01 #1 orange at [223, 115, 270, 165]: missed -> found
  + 4A8B_lampmid3_bathtile_edge_01 #2 orange at [279, 122, 331, 178]: missed -> found
  + 4A8B_lampmid6_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: missed -> found
  + 4A8B_lampmid6_bathtile_clutter_01 #2 blue at [292, 111, 330, 152]: missed -> found
  + 4A8B_lampmid6_bathtile_clutter_01 #3 orange at [410, 108, 442, 141]: missed -> found
  + 4A8B_lampmid6_bathtile_core_01 #1 orange at [223, 115, 270, 165]: missed -> found
  + 4A8B_lampmid6_bathtile_core_01 #3 blue at [374, 140, 457, 226]: missed -> found
  + 4A8B_lampmid6_bathtile_edge_01 #2 orange at [279, 122, 331, 178]: missed -> found
  + 4A8B_lampmid6_bathtile_touch_01 #1 orange at [285, 121, 337, 177]: missed -> found
  + 4A8B_lampmid6_ottoman_clutter_01 #1 blue at [79, 146, 177, 241]: missed -> found
  + 4A8B_lampmid6_ottoman_core_01 #3 blue at [273, 113, 316, 160]: missed -> found
  + 4A8B_lampmid6_ottoman_touch_01 #1 blue at [198, 129, 262, 198]: missed -> found
  + 4A8B_window_abpwhite_occlx_14 #1 orange at [0, 120, 45, 179]: missed -> found
  ~ 4A8B_lampmid3_bathtile_clutter_01 #1 blue at [73, 133, 152, 209]: missed -> off
  ~ 4A8B_lampmid6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: missed -> off
  report only: 19 gained, 2 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 3 frame(s)
  4A8B_lampmid3_bathtile_core_01: second 0 -> 1; now [('orange', (220, 104, 256, 143))]
  4A8B_lampmid6_ottoman_clutter_01: second 0 -> 1; now [('orange', (288, 134, 360, 224))]
  4A8B_lampmid6_ottoman_core_01: second 0 -> 1; now [('blue', (120, 139, 186, 203))]

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [BETTER] found, the ordinary conditions together: 133.8 -> 148.1 of 172 placements (+14.3; counted per frame 211 -> 243 of 307). Better above +4.0,
      worse below -10.9.
  [within the noise] found, place by place: abp_gray +6.0 of 16 (margin 6.0); home_bathtile +3.0 of 15 (margin 1.2); home_ottoman +4.3 of 15 (margin
      2.3); abp_white +1.0 of 32 (margin 1.0).
  [within the noise] boxes that are not on their barrel: 1.9 -> 2.8 counted once per arrangement (+0.9; per frame: on nothing 5 -> 5, second box 0 -> 3,
      wrong color 0 -> 0). Worse above +1.9, better below -1.0.
  [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 0.0 per arrangement (margin
      1.0).

VERDICT: PASS. found is up by more than the noise, and nothing is worse by more than the noise.
```
