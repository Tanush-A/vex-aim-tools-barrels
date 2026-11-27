# Judge: cn_box_nm against cn_alone: NO CLEAR DIFFERENCE

```
JUDGE: cn_box_nm against cn_alone

baseline  = combined cn_alone (barrels.combined.WAYS3): near-miss, self-calibration and contrast settings each picked by that winner's own rule on the
    other places; nothing is chosen for the combination
candidate = combined cn_box_nm (barrels.combined.WAYS3): near-miss, self-calibration and contrast settings each picked by that winner's own rule on
    the other places; nothing is chosen for the combination
Frames: 154 ordinary train frames, 17 conditions at 8 places: 172 placements (physical barrels) in 91 arrangements, 307 barrels when every light is
    counted. Test frames never opened. git a52f0b1, 2026-11-26; 66 s in the detectors.
LEAVE ONE PLACE OUT: every place was scored by a candidate fitted on the other places only; the verdict rests on held-out results.

BY PLACE (the verdict is computed on these)
                                            |                     CN_ALONE                     |                    CN_BOX_NM
                    lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
-------------------------------------------------------------------------------------------------------------------------------------------------
home_white               1     16   29   29 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0)   1.0 (1)     0   0    0     0
campus_study             1     21   35   35 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0)   0.0 (0)     0   0    0     0
abp_gray                 1      8   16   16 |  15.0  15 1.0 (1)   0.0 (0)     0   0    0     0 |  14.0  14 2.0 (2)   0.0 (0)     0   0    0     0
home_bathtile            4     28   60   15 |  13.5  54 0.0 (0)   1.5 (6)     1   1    0     0 |  13.5  54 0.0 (0)   1.5 (6)     2   1    0     0
home_glass               5     36   75   15 |  14.8  74 0.2 (1)   0.0 (0)     0   0    5     0 |  14.8  74 0.2 (1)   0.0 (0)     0   0    9     2
home_ottoman             3     21   45   15 |  10.0  30 0.0 (0)  5.0 (15)     0   0    1     0 |  10.3  31 0.3 (1)  4.3 (13)     0   1    1     0
uc_palewood              1      7   15   15 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0)   2.0 (2)     0   0    1     0
abp_white                1     17   32   32 |  26.0  26 0.0 (0)   6.0 (6)     0   0    0     0 |  28.0  28 0.0 (0)   4.0 (4)     0   0    0     0
-------------------------------------------------------------------------------------------------------------------------------------------------
all ordinary places     17    154  307  172 | 155.3 275 1.2 (2) 15.5 (30)     1   1    7     0 | 156.6 277 2.5 (4) 12.8 (26)     2   2   11     2
-------------------------------------------------------------------------------------------------------------------------------------------------

BY CONDITION (one light each)
                                             |                    CN_ALONE                    |                   CN_BOX_NM
                     lights frames brls plcm | found raw box off  missed wrong 2nd none empty | found raw box off  missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
window_light              1     16   29   29 |  28.0  28 0.0 (0) 1.0 (1)     0   0    0     0 |  28.0  28 0.0 (0) 1.0 (1)     0   0    0     0
campus_light              1     21   35   35 |  35.0  35 0.0 (0) 0.0 (0)     0   0    0     0 |  35.0  35 0.0 (0) 0.0 (0)     0   0    0     0
both_abpgray              1      8   16   16 |  15.0  15 1.0 (1) 0.0 (0)     0   0    0     0 |  14.0  14 2.0 (2) 0.0 (0)     0   0    0     0
lampcool6_bathtile        1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0
lampcool6_glass           1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    0     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    2     1
lampcool6_ottoman         1      7   15   15 |  12.0  12 0.0 (0) 3.0 (3)     0   0    0     0 |  13.0  13 0.0 (0) 2.0 (2)     0   0    0     0
lampmid3_bathtile         1      7   15   15 |  13.0  13 0.0 (0) 2.0 (2)     0   1    0     0 |  13.0  13 0.0 (0) 2.0 (2)     0   1    0     0
lampmid3_glass            1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    2     1
lampmid6_bathtile         1      7   15   15 |  13.0  13 0.0 (0) 2.0 (2)     0   0    0     0 |  13.0  13 0.0 (0) 2.0 (2)     1   0    0     0
lampmid6_glass            1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    1     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    2     0
lampmid6_ottoman          1      7   15   15 |  10.0  10 0.0 (0) 5.0 (5)     0   0    0     0 |  10.0  10 1.0 (1) 4.0 (4)     0   1    0     0
lampwarm6_bathtile        1      7   15   15 |  13.0  13 0.0 (0) 2.0 (2)     1   0    0     0 |  13.0  13 0.0 (0) 2.0 (2)     1   0    0     0
lampwarm6_glass           1      7   15   15 |  15.0  15 0.0 (0) 0.0 (0)     0   0    3     0 |  15.0  15 0.0 (0) 0.0 (0)     0   0    3     0
lampwarm6_ottoman         1      7   15   15 |   8.0   8 0.0 (0) 7.0 (7)     0   0    1     0 |   8.0   8 0.0 (0) 7.0 (7)     0   0    1     0
overheaddim_palewood      1      7   15   15 |  13.0  13 0.0 (0) 2.0 (2)     0   0    1     0 |  13.0  13 0.0 (0) 2.0 (2)     0   0    1     0
window_abpwhite           1     17   32   32 |  26.0  26 0.0 (0) 6.0 (6)     0   0    0     0 |  28.0  28 0.0 (0) 4.0 (4)     0   0    0     0
window_glass              1      8   15   15 |  14.0  14 1.0 (1) 0.0 (0)     0   0    0     0 |  14.0  14 1.0 (1) 0.0 (0)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

REPORT ONLY (extreme or unlisted conditions; never judged)
                                         |                     CN_ALONE                     |                    CN_BOX_NM
                 lights frames brls plcm | found raw box off    missed wrong 2nd none empty | found raw box off    missed wrong 2nd none empty
----------------------------------------------------------------------------------------------------------------------------------------------
lampcool3_wood        1     10   21   21 |  15.0  15 0.0 (0)   6.0 (6)     0   0    0     0 |  16.0  16 0.0 (0)   5.0 (5)     0   0    0     0
lampcool6_wood        1     10   21   21 |  11.0  11 3.0 (3)   7.0 (7)     2   0    0     0 |  16.0  16 1.0 (1)   4.0 (4)     1   0    0     0
lampmid3_ottoman      1      7   15   15 |   1.0   1 1.0 (1) 13.0 (13)     0   0    0     0 |   1.0   1 2.0 (2) 12.0 (12)     0   0    0     0
lampmid3_wood         1     10   21   21 |  12.0  12 1.0 (1)   8.0 (8)     1   0    0     0 |  14.0  14 1.0 (1)   6.0 (6)     1   0    0     0
lampmid6_wood         1     10   21   21 |  16.0  16 2.0 (2)   3.0 (3)     0   0    1     0 |  15.0  15 2.0 (2)   4.0 (4)     1   0    2     0
lampwarm3_wood        1     10   21   21 |  12.0  12 1.0 (1)   8.0 (8)     0   0    0     0 |  12.0  12 1.0 (1)   8.0 (8)     0   0    0     0
lampwarm6_wood        1     10   21   21 |  13.0  13 3.0 (3)   5.0 (5)     2   0    0     0 |  11.0  11 4.0 (4)   6.0 (6)     2   0    0     0
window_black          1     10   26   26 |   5.0   5 2.0 (2) 19.0 (19)     0   0    0     0 |  14.0  14 5.0 (5)   7.0 (7)     0   0    0     0
----------------------------------------------------------------------------------------------------------------------------------------------

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw
    = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements
    (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel,
    empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements
    (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

BARRELS THAT CHANGED on the ordinary conditions: 5 gained, 3 lost (counted per frame)
  + 4A8B_lampcool6_ottoman_close_01 #1 orange at [218, 232, 470, 480]: missed -> found
  + 4A8B_lampmid6_bathtile_edge_01 #1 blue at [0, 127, 31, 196]: missed -> found
  + 4A8B_lampmid6_ottoman_touch_01 #1 blue at [198, 129, 262, 198]: missed -> found
  + 4A8B_window_abpwhite_occlx_06 #1 orange at [133, 115, 181, 160]: missed -> found
  + 4A8B_window_abpwhite_occlx_14 #1 orange at [0, 120, 45, 179]: missed -> found
  - 4A8B_both_abpgray_core_01 #4 orange at [408, 125, 472, 192]: found -> off
  - 4A8B_lampmid6_bathtile_clutter_01 #2 blue at [292, 111, 330, 152]: found -> missed
  - 4A8B_lampmid6_ottoman_core_01 #1 blue at [77, 133, 155, 208]: found -> off
  report only: 17 gained, 3 lost on the extreme conditions (judge.json lists them)

BOXES NOT ON THEIR BARREL that changed: 6 frame(s)
  4A8B_lampcool6_glass_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('orange', (555, 124, 604, 171))]
  4A8B_lampcool6_glass_occl_02: nothing 0 -> 1; now [('orange', (560, 123, 610, 170))]
  4A8B_lampmid3_glass_neg_02 [empty frame with clutter]: nothing 0 -> 1; now [('orange', (560, 123, 609, 171))]
  4A8B_lampmid6_bathtile_clutter_01: wrong color 0 -> 1; now [('orange', (292, 104, 329, 138))]
  4A8B_lampmid6_glass_clutter_01: nothing 1 -> 2; now [('blue', (490, 98, 516, 125)), ('orange', (555, 117, 603, 171))]
  4A8B_lampmid6_ottoman_core_01: second 0 -> 1; now [('blue', (120, 139, 186, 203))]

THE CLAUSES (margins: margins.json, made 2026-11-26 at git f20ad1c)
  [within the noise] found, the ordinary conditions together: 155.3 -> 156.6 of 172 placements (+1.3; counted per frame 275 -> 277 of 307). Better above
      +4.0, worse below -10.9.
  [within the noise] found, place by place: abp_gray -1.0 of 16 (margin 6.0); home_ottoman +0.3 of 15 (margin 2.3); abp_white +2.0 of 32 (margin 1.0).
  [within the noise] boxes that are not on their barrel: 2.8 -> 4.2 counted once per arrangement (+1.4; per frame: on nothing 7 -> 11, second box 1 ->
      2, wrong color 1 -> 2). Worse above +1.9, better below -1.0.
  [within the noise] boxes on empty frames: on clean ones 0 -> 0 (margin 0: none is allowed); on ones with clutter 0.0 -> 0.4 per arrangement (margin
      1.0).

VERDICT: NO CLEAR DIFFERENCE. no count moved by more than a change that means nothing moves it.
```
