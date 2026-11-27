# Judge: mask_union against nearmiss: PASS

```
JUDGE: mask_union against nearmiss

baseline  = B_partner_fit: partner-conditioned, stripe and body level 0..5, edges strict or pred; the setting is chosen in each fold on the other
    places (rule: PREREG.md)
candidate = combined mask_union (barrels.combined): in each fold the near-miss setting is picked by nearmiss's own rule and the self-calibration
    setting by selfcal's own rule, each on the other places; nothing is chosen for the combination
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git 7347008, 2026-11-26; 172 s in the detectors.
LEAVE ONE PLACE OUT: every place was scored by a candidate fitted on the other places only; the verdict rests on held-out results.

BY PLACE (the verdict is computed on these)
                                            |                     NEARMISS                     |                    MASK_UNION
                    lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
-------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_study             1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
abp_gray                 1      8   16   16 |  12.0  12 2.0 (2)   2.0 (2)     0   0    0     0 |  15.0  15 1.0 (1)   0.0 (0)     0   0    0     0
home_bathtile            4     28   60   15 |   9.0  36 0.0 (0)  6.0 (24)     1   1    0     0 |  11.0  44 0.2 (1)  3.8 (15)     0   1    0     0
home_glass               5     36   75   15 |  14.8  74 0.2 (1)   0.0 (0)     0   0    7     2 |  14.8  74 0.2 (1)   0.0 (0)     0   0    7     2
home_ottoman             3     21   45   15 |   7.7  23 0.3 (1)  7.0 (21)     0   1    1     0 |   8.0  24 0.3 (1)  6.7 (20)     0   1    1     0
uc_palewood              1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0
abp_white                1     17   32   32 |  28.0  28 0.0 (0)   4.0 (4)     0   0    0     0 |  28.0  28 0.0 (0)   4.0 (4)     0   0    0     0
-------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 147.5 249 2.5 (4) 22.0 (54)     1   2    9     2 | 152.8 261 1.8 (4) 17.4 (42)     0   2    9     2
-------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                     NEARMISS                     |                    MASK_UNION
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
both_abpgray              1      8   16   16 |  12.0  12 2.0 (2)   2.0 (2)     0   0    0     0 |  15.0  15 1.0 (1)   0.0 (0)     0   0    0     0
lampcool6_bathtile        1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampcool6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     1 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     1
lampcool6_ottoman         1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0 |  14.0  14 0.0 (0)   1.0 (1)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |   9.0   9 0.0 (0)   6.0 (6)     0   1    0     0 |  11.0  11 0.0 (0)   4.0 (4)     0   1    0     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     1 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     1
lampmid6_bathtile         1      7   15   15 |  11.0  11 0.0 (0)   4.0 (4)     1   0    0     0 |  12.0  12 1.0 (1)   2.0 (2)     0   0    0     0
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     0
lampmid6_ottoman          1      7   15   15 |   9.0   9 1.0 (1)   5.0 (5)     0   1    0     0 |   9.0   9 1.0 (1)   5.0 (5)     0   1    0     0
lampwarm6_bathtile        1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   6.0   6 0.0 (0)   9.0 (9)     0   0    0     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0
lampwarm6_ottoman         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    1     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    1     0
overheaddim_palewood      1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0
window_abpwhite           1     17   32   32 |  28.0  28 0.0 (0)   4.0 (4)     0   0    0     0 |  28.0  28 0.0 (0)   4.0 (4)     0   0    0     0
window_glass              1      8   15   15 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0
--------------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                     NEARMISS                     |                    MASK_UNION
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |  10.0  10 0.0 (0) 11.0 (11)     0   0    0     0 |  12.0  12 0.0 (0)   9.0 (9)     1   0    0     0
lampcool6_wood        1     10   21   21 |  11.0  11 0.0 (0) 10.0 (10)     0   0    0     0 |  11.0  11 2.0 (2)   8.0 (8)     2   0    0     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 2.0 (2) 12.0 (12)     0   0    0     0 |   1.0   1 2.0 (2) 12.0 (12)     0   0    0     0
lampmid3_wood         1     10   21   21 |  12.0  12 0.0 (0)   9.0 (9)     1   0    0     0 |  14.0  14 1.0 (1)   6.0 (6)     1   0    0     0
lampmid6_wood         1     10   21   21 |   9.0   9 0.0 (0) 12.0 (12)     1   0    1     0 |  10.0  10 1.0 (1) 10.0 (10)     0   0    1     0
lampwarm3_wood        1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   6.0   6 0.0 (0) 15.0 (15)     0   0    0     0
lampwarm6_wood        1     10   21   21 |   0.0   0 2.0 (2) 19.0 (19)     1   0    0     0 |   6.0   6 2.0 (2) 13.0 (13)     1   0    0     0
window_black          1     10   26   26 |  14.0  14 5.0 (5)   7.0 (7)     0   0    0     0 |  12.0  12 5.0 (5)   9.0 (9)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 12 gained, 0 lost, 1 moved between 'box off' and 'missed' (counted per frame)
  + 4A8B_both_abpgray_core_01 #4 orange at [408, 125, 472, 192]: off -> found
  + 4A8B_both_abpgray_edge_01 #1 orange at [291, 127, 356, 197]: missed -> found
  + 4A8B_both_abpgray_touch_01 #1 orange at [193, 124, 247, 181]: missed -> found
  + 4A8B_lampcool6_ottoman_touch_01 #1 blue at [198, 129, 262, 198]: missed -> found
  + 4A8B_lampmid3_bathtile_core_01 #3 blue at [374, 140, 457, 226]: missed -> found
  + 4A8B_lampmid3_bathtile_core_01 #4 blue at [475, 110, 513, 147]: missed -> found
  + 4A8B_lampmid6_bathtile_touch_01 #3 blue at [390, 124, 446, 183]: missed -> found
  + 4A8B_lampwarm6_bathtile_clutter_01 #4 orange at [495, 128, 565, 191]: missed -> found
  + 4A8B_lampwarm6_bathtile_core_01 #1 orange at [223, 115, 270, 165]: missed -> found
  + 4A8B_lampwarm6_bathtile_core_01 #3 blue at [374, 140, 457, 226]: missed -> found
  + 4A8B_lampwarm6_bathtile_core_01 #4 blue at [475, 110, 513, 147]: missed -> found
  + 4A8B_lampwarm6_bathtile_touch_01 #1 orange at [285, 121, 337, 177]: missed -> found
  ~ 4A8B_lampmid6_bathtile_touch_01 #2 blue at [337, 123, 390, 180]: missed -> off
  report only: 23 gained, 9 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 1 frame(s)
  4A8B_lampmid6_bathtile_clutter_01: wrong color 1 -> 0

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [BETTER] found, the ordinary conditions together: 147.5 -> 152.8 of 172 placements (+5.3; counted per frame 249 -> 261 of 307). Better above +4.0,
      worse below -10.9.
  [within the noise] found, place by place: abp_gray +3.0 of 16 (margin 6.0); home_bathtile +2.0 of 15 (margin 1.2); home_ottoman +0.3 of 15 (margin
      2.3).
  [within the noise] boxes that are not on their barrel: 3.6 -> 3.3 counted once per arrangement (-0.3; per frame: on nothing 9 -> 9, second box 2 -> 2,
      wrong color 1 -> 0). Worse above +1.9, better below -1.0.
  [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.4 -> 0.4 per arrangement (margin
      1.0).

VERDICT: PASS. found is up by more than the noise, and nothing is worse by more than the noise.
```
