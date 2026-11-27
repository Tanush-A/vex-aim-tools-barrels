# Judge: box_agree against selfcal: FAIL

```
JUDGE: box_agree against selfcal

baseline  = selfcal AB: 8 settings, one picked per fold on the other places (candidates.py: choose)
candidate = combined box_agree (barrels.combined): in each fold the near-miss setting is picked by nearmiss's own rule and the self-calibration
    setting by selfcal's own rule, each on the other places; nothing is chosen for the combination
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git 7347008, 2026-11-26; 282 s in the detectors.
LEAVE ONE PLACE OUT: every place was scored by a candidate fitted on the other places only; the verdict rests on held-out results.

BY PLACE (the verdict is computed on these)
                                            |                     SELFCAL                      |                    BOX_AGREE
                    lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
-------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_study             1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
abp_gray                 1      8   16   16 |  15.0  15 1.0 (1)   0.0 (0)     0   0    0     0 |  13.0  13 1.0 (1)   2.0 (2)     0   0    0     0
home_bathtile            4     28   60   15 |   9.8  39 0.2 (1)  5.0 (20)     0   1    0     0 |   7.8  31 0.0 (0)  7.2 (29)     0   1    0     0
home_glass               5     36   75   15 |  14.8  74 0.2 (1)   0.0 (0)     0   0    3     0 |  14.8  74 0.2 (1)   0.0 (0)     0   0    3     0
home_ottoman             3     21   45   15 |   6.0  18 0.0 (0)  9.0 (27)     0   0    1     0 |   5.7  17 0.0 (0)  9.3 (28)     0   0    1     0
uc_palewood              1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0
abp_white                1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0
-------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 147.6 248 1.4 (3) 23.0 (56)     0   1    5     0 | 143.2 237 1.2 (2) 27.6 (68)     0   1    5     0
-------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                     SELFCAL                      |                    BOX_AGREE
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
both_abpgray              1      8   16   16 |  15.0  15 1.0 (1)   0.0 (0)     0   0    0     0 |  13.0  13 1.0 (1)   2.0 (2)     0   0    0     0
lampcool6_bathtile        1      7   15   15 |  14.0  14 0.0 (0)   1.0 (1)     0   0    0     0 |  14.0  14 0.0 (0)   1.0 (1)     0   0    0     0
lampcool6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampcool6_ottoman         1      7   15   15 |  11.0  11 0.0 (0)   4.0 (4)     0   0    0     0 |  10.0  10 0.0 (0)   5.0 (5)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |  10.0  10 0.0 (0)   5.0 (5)     0   1    0     0 |   8.0   8 0.0 (0)   7.0 (7)     0   1    0     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0
lampmid6_bathtile         1      7   15   15 |   9.0   9 1.0 (1)   5.0 (5)     0   0    0     0 |   8.0   8 0.0 (0)   7.0 (7)     0   0    0     0
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0
lampmid6_ottoman          1      7   15   15 |   7.0   7 0.0 (0)   8.0 (8)     0   0    0     0 |   7.0   7 0.0 (0)   8.0 (8)     0   0    0     0
lampwarm6_bathtile        1      7   15   15 |   6.0   6 0.0 (0)   9.0 (9)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0
lampwarm6_ottoman         1      7   15   15 |   0.0   0 0.0 (0) 15.0 (15)     0   0    1     0 |   0.0   0 0.0 (0) 15.0 (15)     0   0    1     0
overheaddim_palewood      1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0
window_abpwhite           1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0
window_glass              1      8   15   15 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0
--------------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                     SELFCAL                      |                    BOX_AGREE
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |  11.0  11 0.0 (0) 10.0 (10)     1   0    0     0 |   9.0   9 0.0 (0) 12.0 (12)     0   0    0     0
lampcool6_wood        1     10   21   21 |   8.0   8 2.0 (2) 11.0 (11)     2   0    0     0 |   5.0   5 2.0 (2) 14.0 (14)     2   0    0     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0
lampmid3_wood         1     10   21   21 |  11.0  11 1.0 (1)   9.0 (9)     1   0    0     0 |   8.0   8 1.0 (1) 12.0 (12)     1   0    0     0
lampmid6_wood         1     10   21   21 |   9.0   9 1.0 (1) 11.0 (11)     0   0    0     0 |   7.0   7 1.0 (1) 13.0 (13)     0   0    0     0
lampwarm3_wood        1     10   21   21 |   6.0   6 0.0 (0) 15.0 (15)     0   0    0     0 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0
lampwarm6_wood        1     10   21   21 |   6.0   6 0.0 (0) 15.0 (15)     1   0    0     0 |   0.0   0 0.0 (0) 21.0 (21)     1   0    0     0
window_black          1     10   26   26 |   8.0   8 1.0 (1) 17.0 (17)     0   0    0     0 |   8.0   8 1.0 (1) 17.0 (17)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 0 gained, 11 lost, 1 moved between 'box off' and 'missed' (counted per frame)
  - 4A8B_both_abpgray_edge_01 #1 orange at [291, 127, 356, 197]: found -> missed
  - 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: found -> missed
  - 4A8B_lampcool6_ottoman_touch_01 #1 blue at [198, 129, 262, 198]: found -> missed
  - 4A8B_lampmid3_bathtile_core_01 #3 blue at [374, 140, 457, 226]: found -> missed
  - 4A8B_lampmid3_bathtile_core_01 #4 blue at [475, 110, 513, 147]: found -> missed
  - 4A8B_lampmid6_bathtile_touch_01 #3 blue at [390, 124, 446, 183]: found -> missed
  - 4A8B_lampwarm6_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: found -> missed
  - 4A8B_lampwarm6_bathtile_core_01 #1 orange at [223, 115, 270, 165]: found -> missed
  - 4A8B_lampwarm6_bathtile_core_01 #3 blue at [374, 140, 457, 226]: found -> missed
  - 4A8B_lampwarm6_bathtile_core_01 #4 blue at [475, 110, 513, 147]: found -> missed
  - 4A8B_lampwarm6_bathtile_touch_01 #1 orange at [285, 121, 337, 177]: found -> missed
  ~ 4A8B_lampmid6_bathtile_touch_01 #2 blue at [337, 123, 390, 180]: off -> missed
  report only: 0 gained, 21 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 0 frame(s)

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [within the noise] found, the ordinary conditions together: 147.6 -> 143.2 of 172 placements (-4.3; counted per frame 248 -> 237 of 307). Better above
      +4.0, worse below -10.9.
  [WORSE] found, place by place: abp_gray -2.0 of 16 (margin 6.0); home_bathtile -2.0 of 15 (margin 1.2, WORSE); home_ottoman -0.3 of 15 (margin 2.3).
  [within the noise] boxes that are not on their barrel: 2.2 -> 2.2 counted once per arrangement (+0.0; per frame: on nothing 5 -> 5, second box 1 -> 1,
      wrong color 0 -> 0). Worse above +1.9, better below -1.0.
  [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 0.0 per arrangement (margin
      1.0).

VERDICT: FAIL. worse than the baseline by more than the noise in: found at home_bathtile.
```
