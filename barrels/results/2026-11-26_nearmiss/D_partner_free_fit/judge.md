# Judge: D_partner_free_fit against baseline: FAIL

```
JUDGE: D_partner_free_fit against baseline

baseline  = today's default (the adopted color model, DetConfig defaults)
candidate = D_partner_free_fit: partner-conditioned, stripe and body level 0..5, edges free (unprotected); the setting is chosen in each fold on the
    other places (rule: PREREG.md)
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git c648d95, 2026-11-26; 84 s in the detectors.
LEAVE ONE PLACE OUT: every place was scored by a candidate fitted on the other places only; the verdict rests on held-out results.

BY PLACE (the verdict is computed on these)
                                            |                     BASELINE                      |                D_PARTNER_FREE_FIT
                    lights frames brls plcm | found raw  box off    missed wrong 2nd none empty | found raw  box off    missed wrong 2nd none empty
---------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28  0.0 (0)   1.0 (1)     0   0    0     0 |  27.0  27  1.0 (1)   1.0 (1)     0   0    0     0
campus_study             1     21   35   35 |  35.0  35  0.0 (0)   0.0 (0)     0   0    0     0 |  31.0  31  4.0 (4)   0.0 (0)     0   0    0     0
abp_gray                 1      8   16   16 |  10.0  10  1.0 (1)   5.0 (5)     0   0    0     0 |  12.0  12  1.0 (1)   3.0 (3)     0   0    0     0
home_bathtile            4     28   60   15 |   4.0  16  0.0 (0) 11.0 (44)     0   0    0     0 |   4.5  18  0.0 (0) 10.5 (42)     0   0    0     0
home_glass               5     36   75   15 |  14.8  74  0.2 (1)   0.0 (0)     0   0    3     0 |  14.4  72  0.6 (3)   0.0 (0)     0   0    5     1
home_ottoman             3     21   45   15 |   3.0   9  0.0 (0) 12.0 (36)     0   0    1     0 |   5.3  16  0.7 (2)  9.0 (27)     0   1    1     0
uc_palewood              1      7   15   15 |  13.0  13  0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13  0.0 (0)   2.0 (2)     0   0    1     0
abp_white                1     17   32   32 |  26.0  26  0.0 (0)   6.0 (6)     0   0    0     0 |  25.0  25  2.0 (2)   5.0 (5)     0   0    0     0
---------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 133.8 211  1.2 (2) 37.0 (94)     0   0    5     0 | 132.2 214 9.3 (13) 30.5 (80)     0   1    7     1
---------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                     BASELINE                     |                D_PARTNER_FREE_FIT
                     lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
--------------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  27.0  27 1.0 (1)   1.0 (1)     0   0    0     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  31.0  31 4.0 (4)   0.0 (0)     0   0    0     0
both_abpgray              1      8   16   16 |  10.0  10 1.0 (1)   5.0 (5)     0   0    0     0 |  12.0  12 1.0 (1)   3.0 (3)     0   0    0     0
lampcool6_bathtile        1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    0     0 |  14.0  14 0.0 (0)   1.0 (1)     0   0    0     0
lampcool6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    0     0
lampcool6_ottoman         1      7   15   15 |   3.0   3 0.0 (0) 12.0 (12)     0   0    0     0 |  10.0  10 0.0 (0)   5.0 (5)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     1
lampmid6_bathtile         1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   2.0   2 0.0 (0) 13.0 (13)     0   0    0     0
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0)   0.0 (0)     0   0    2     0
lampmid6_ottoman          1      7   15   15 |   6.0   6 0.0 (0)   9.0 (9)     0   0    0     0 |   6.0   6 2.0 (2)   7.0 (7)     0   1    0     0
lampwarm6_bathtile        1      7   15   15 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0 |   1.0   1 0.0 (0) 14.0 (14)     0   0    0     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0)   0.0 (0)     0   0    1     0 |  14.0  14 1.0 (1)   0.0 (0)     0   0    1     0
lampwarm6_ottoman         1      7   15   15 |   0.0   0 0.0 (0) 15.0 (15)     0   0    1     0 |   0.0   0 0.0 (0) 15.0 (15)     0   0    1     0
overheaddim_palewood      1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0
window_abpwhite           1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  25.0  25 2.0 (2)   5.0 (5)     0   0    0     0
window_glass              1      8   15   15 |  14.0  14 1.0 (1)   0.0 (0)     0   0    0     0 |  13.0  13 2.0 (2)   0.0 (0)     0   0    0     0
--------------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                     BASELINE                     |                D_PARTNER_FREE_FIT
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |   2.0   2 0.0 (0) 19.0 (19)     0   0    0     0 |   8.0   8 1.0 (1) 12.0 (12)     0   0    0     0
lampcool6_wood        1     10   21   21 |   2.0   2 2.0 (2) 17.0 (17)     2   0    0     0 |  10.0  10 0.0 (0) 11.0 (11)     0   0    0     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0
lampmid3_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     1   0    0     0 |   5.0   5 0.0 (0) 16.0 (16)     1   0    0     0
lampmid6_wood         1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   7.0   7 1.0 (1) 13.0 (13)     1   0    1     0
lampwarm3_wood        1     10   21   21 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0 |   1.0   1 0.0 (0) 20.0 (20)     0   0    0     0
lampwarm6_wood        1     10   21   21 |   0.0   0 0.0 (0) 21.0 (21)     1   0    0     0 |   0.0   0 1.0 (1) 20.0 (20)     1   0    0     0
window_black          1     10   26   26 |   5.0   5 1.0 (1) 20.0 (20)     0   0    0     0 |  15.0  15 4.0 (4)   7.0 (7)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 13 gained, 10 lost, 3 moved between 'box off' and 'missed' (counted per frame)
  + 4A8B_both_abpgray_core_01 #2 blue at [233, 165, 353, 299]: missed -> found
  + 4A8B_both_abpgray_touch_01 #2 blue at [246, 123, 301, 181]: missed -> found
  + 4A8B_lampcool6_bathtile_occl_02 #1 orange at [346, 107, 376, 137]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #1 blue at [79, 146, 177, 241]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #2 blue at [288, 116, 333, 163]: missed -> found
  + 4A8B_lampcool6_ottoman_clutter_01 #3 orange at [313, 141, 401, 236]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #2 orange at [155, 166, 280, 311]: missed -> found
  + 4A8B_lampcool6_ottoman_core_01 #4 orange at [413, 126, 479, 190]: missed -> found
  + 4A8B_lampcool6_ottoman_edge_01 #2 orange at [267, 139, 351, 231]: missed -> found
  + 4A8B_lampmid6_bathtile_edge_01 #2 orange at [279, 122, 331, 178]: missed -> found
  + 4A8B_lampmid6_ottoman_clutter_01 #1 blue at [79, 146, 177, 241]: missed -> found
  + 4A8B_window_abpwhite_occlx_06 #1 orange at [133, 115, 181, 160]: missed -> found
  - 4A8B_window_light_cluster_02 #4 blue at [443, 122, 500, 179]: found -> off
  - 4A8B_campus_light_core_01 #2 orange at [247, 110, 279, 145]: found -> off
  - 4A8B_campus_light_far_01 #1 orange at [196, 116, 238, 161]: found -> off
  - 4A8B_campus_light_far_01 #3 blue at [318, 114, 357, 154]: found -> off
  - 4A8B_campus_light_far_01 #4 orange at [379, 113, 414, 150]: found -> off
  - 4A8B_lampmid6_ottoman_touch_01 #2 blue at [262, 129, 325, 198]: found -> missed
  - 4A8B_lampwarm6_glass_touch_01 #1 blue at [224, 124, 280, 185]: found -> off
  - 4A8B_window_abpwhite_occlx_08 #1 orange at [111, 114, 160, 164]: found -> missed
  - 4A8B_window_abpwhite_occlx_18 #1 orange at [102, 118, 153, 166]: found -> off
  - 4A8B_window_glass_clutter_01 #3 orange at [359, 104, 387, 133]: found -> off
  ~ 4A8B_lampmid6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: missed -> off
  ~ 4A8B_lampmid6_ottoman_touch_01 #1 blue at [198, 129, 262, 198]: missed -> off
  ~ 4A8B_window_abpwhite_occlx_14 #1 orange at [0, 120, 45, 179]: missed -> off
  report only: 36 gained, 2 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 3 frame(s)
  4A8B_lampmid3_glass_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('orange', (560, 123, 609, 171))]
  4A8B_lampmid6_glass_clutter_01: nothing 1 -> 2; now [('blue', (491, 98, 516, 125)), ('orange', (555, 117, 603, 171))]
  4A8B_lampmid6_ottoman_clutter_01: second 0 -> 1; now [('orange', (288, 135, 362, 218))]

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [within the noise] found, the ordinary conditions together: 133.8 -> 132.2 of 172 placements (-1.6; counted per frame 211 -> 214 of 307). Better above
      +4.0, worse below -10.9.
  [WORSE] found, place by place: home_white -1.0 of 29 (margin 1.0); campus_study -4.0 of 35 (margin 1.0, WORSE); abp_gray +2.0 of 16 (margin 6.0);
      home_bathtile +0.5 of 15 (margin 1.2); home_glass -0.4 of 15 (margin 1.0); home_ottoman +2.3 of 15 (margin 2.3); abp_white -1.0 of 32 (margin
      1.0).
  [within the noise] boxes that are not on their barrel: 1.9 -> 2.7 counted once per arrangement (+0.7; per frame: on nothing 5 -> 7, second box 0 -> 1,
      wrong color 0 -> 0). Worse above +1.9, better below -1.0.
  [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 0.2 per arrangement (margin
      1.0).

VERDICT: FAIL. worse than the baseline by more than the noise in: found at campus_study.
```
