# Occlusion scorecard: before all the occlusion work → the detector on `wip/occl-combined`

**before** = the defaults of `barrels` today (arm `before`: none of the unmerged occlusion branches). **after** = the default on this branch (arm `reduced+thin`). 3888 simulated scenes: each of 50 free-standing barrels of the train frames, alone on an empty mask at its own place, hidden 25, 50 or 75 % by one thing. A cell counts the scenes where the detector draws a box of the right color on the barrel's FULL box (overlap of half or more, bottom edge right: the project's v2 rule). Each cell: **before → after, of n**.

| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |
|---|---|---|---|
| cut by the frame edge | 100 → 100 of 100 | 86 → 99 of 100 | 0 → 29 of 100 |
| a straight upright edge, one side | 100 → 100 of 100 | 38 → 90 of 100 | 0 → 28 of 100 |
| a slanted edge, one side | 200 → 200 of 200 | 116 → 170 of 200 | 0 → 0 of 200 |
| both sides cut | 50 → 50 of 50 | 49 → 49 of 50 | 0 → 0 of 50 |
| hidden from above | 50 → 50 of 50 | 1 → 45 of 50 | 0 → 0 of 50 |
| hidden from below (a low thing in front) | 49 → 49 of 50 | 1 → 40 of 50 | 1 → 1 of 50 |
| a post across the middle | 49 → 49 of 50 | 9 → 41 of 50 | 0 → 11 of 50 |
| a barrel of the OTHER color, beside it | 99 → 99 of 100 | 67 → 94 of 100 | 44 → 50 of 100 |
| a barrel of the OTHER color, beside it and lower | 93 → 98 of 100 | 81 → 92 of 100 | 69 → 77 of 100 |
| a barrel of the OTHER color, straight in front | 29 → 40 of 47 | 36 → 38 of 48 | 17 → 22 of 49 |
| a barrel of the SAME color, beside it | 80 → 96 of 100 | 32 → 88 of 100 | 15 → 17 of 100 |
| a barrel of the SAME color, beside it and lower | 88 → 91 of 100 | 60 → 87 of 100 | 1 → 29 of 100 |
| a barrel of the SAME color, straight in front | 45 → 44 of 47 | 25 → 29 of 48 | 1 → 8 of 49 |
| a plain block of the barrel's body color | 100 → 100 of 100 | 85 → 99 of 100 | 2 → 36 of 100 |
| a plain block of the barrel's stripe color | 100 → 100 of 100 | 85 → 99 of 100 | 0 → 3 of 100 |
| **all 15 kinds** | **1232 → 1266 of 1294** | **771 → 1160 of 1296** | **150 → 311 of 1298** |

## Totals, all scenes

| | before (`before`) | the five merged switches (`stack`) | after (`reduced+thin`) |
|---|---|---|---|
| found (v2 rule) | 2153 | 2417 | 2737 of 3888 |
| a box of the right color in the right place, whatever its size | 2318 | 2532 | 2854 |
| **boxes where no barrel is** | 88 | 45 | 45 |
| right-place boxes too small | 157 | 299 | 324 |
| ... about right | 1998 | 2129 | 2445 |
| ... too big | 163 | 104 | 85 |

## False boxes, everywhere in the battery

| where | before (`before`) | `stack` | after (`reduced+thin`) |
|---|---|---|---|
| real frames: HOME (16 train frames, leave one scene out) | 27 of 29 found, **0 false**, 0 on negative frames | 28 of 29 found, **0 false**, 0 on negative frames | 28 of 29 found, **0 false**, 0 on negative frames |
| real frames: CAMPUS (21 train frames) | 34 of 35 found, **0 false**, 0 on negative frames | 35 of 35 found, **0 false**, 0 on negative frames | 35 of 35 found, **0 false**, 0 on negative frames |
| real frames: black table (extreme, report only) | 3 of 26 found, **1 false**, 0 on negative frames | 5 of 26 found, **1 false**, 0 on negative frames | 5 of 26 found, **1 false**, 0 on negative frames |
| real frames: orange wood table, 9 lamp settings (extreme, report only) | 7 of 189 found, **4 false**, 0 on negative frames | 7 of 189 found, **4 false**, 0 on negative frames | 7 of 189 found, **5 false**, 0 on negative frames |
| real frames: Dave's (indicative labels) | 12 of 34 found, **2 false**, 0 on negative frames | 12 of 34 found, **3 false**, 0 on negative frames | 12 of 34 found, **4 false**, 0 on negative frames |
| boxes on negative frames, every set together | **0** | **0** | **0** |
| occlusion scorecard: boxes where no barrel is (3888 scenes) | 88 | 45 | 45 |
| damaged masks: perfect masks | 28 of 29 found, **0 false** | 28 of 29 found, **0 false** | 28 of 29 found, **0 false** |
| damaged masks: white tables, typical, 5 seeds (measured on real white-table segmentation) | 140 of 145 found, **0 false** | 145 of 145 found, **0 false** | 145 of 145 found, **0 false** |
| damaged masks: white tables, typical, 20 seeds (measured on real white-table segmentation) | 560 of 580 found, **0 false** | 579 of 580 found, **0 false** | 579 of 580 found, **0 false** |
| damaged masks: white tables, bad day, 5 seeds (harsher than any real barrel measured) | 115 of 145 found, **15 false** | 135 of 145 found, **3 false** | 135 of 145 found, **3 false** |
| damaged masks: white tables, bad day, 20 seeds (harsher than any real barrel measured) | 454 of 580 found, **75 false** | 547 of 580 found, **5 false** | 547 of 580 found, **5 false** |
| damaged masks: bad day without the stripe patch, 5 seeds (bad day, minus the one kind real masks almost never show) | 140 of 145 found, **1 false** | 144 of 145 found, **0 false** | 144 of 145 found, **0 false** |
| damaged masks: bad day without the stripe patch, 20 seeds (bad day, minus the one kind real masks almost never show) | 563 of 580 found, **4 false** | 577 of 580 found, **0 false** | 577 of 580 found, **0 false** |
| damaged masks: light, 5 seeds (made up, 2026-11-18) | 141 of 145 found, **0 false** | 143 of 145 found, **0 false** | 143 of 145 found, **0 false** |
| damaged masks: light, 20 seeds (made up, 2026-11-18) | 564 of 580 found, **5 false** | 574 of 580 found, **0 false** | 574 of 580 found, **0 false** |
| damaged masks: medium, 5 seeds (made up; far harsher than real white-table segmentation) | 64 of 145 found, **22 false** | 99 of 145 found, **1 false** | 102 of 145 found, **1 false** |
| damaged masks: medium, 20 seeds (made up; far harsher than real white-table segmentation) | 242 of 580 found, **87 false** | 388 of 580 found, **3 false** | 400 of 580 found, **3 false** |
| damaged masks: heavy, 5 seeds (made up) | 13 of 145 found, **2 false** | 21 of 145 found, **0 false** | 21 of 145 found, **0 false** |
| damaged masks: heavy, 20 seeds (made up) | 47 of 580 found, **5 false** | 89 of 580 found, **0 false** | 89 of 580 found, **0 false** |
| damaged masks: white tables, worst seen, 5 seeds (report only) | 41 of 145 found, **21 false** | 84 of 145 found, **2 false** | 95 of 145 found, **2 false** |
| damaged masks: white tables, worst seen, 20 seeds (report only) | 154 of 580 found, **72 false** | 337 of 580 found, **6 false** | 378 of 580 found, **6 false** |

## In five sentences

1. **What works now:** a barrel hidden up to a half is found in 1160 of 1296 scenes (771 before), whatever hides it: from the side, from above, from below, by a post, by a barrel of either color beside it; and a quarter hidden is found in 1266 of 1294.
2. **What works partly:** three quarters hidden is found in 311 of 1298 scenes (150 before), and only where something says where the rest is: a found barrel in front or beside (other color beside and lower 77 of 100), or the barrel's own rounded corner showing at the frame edge, a straight edge or a block (28 to 36 of 100).
3. **What does not work, and why:** three quarters hidden by a slanted edge, on both sides, from above or from below (0 or 1 in every such cell), because what is left shows no stripe with a corner or a seam, and in the class mask a thing in front that is not a barrel looks exactly like empty table; and half hidden by a barrel of the same color straight in front (29 of 48), because the two are one blob with one stripe.
4. **False boxes:** none on HOME, CAMPUS or any negative frame, none on the perfect masks, at "typical", at "bad day without the stripe patch" or at light damage, and on the white tables and the simulations far fewer than before the occlusion work (scorecard 88 → 45, bad day 75 → 5 and medium damage 87 → 3 over 20 seeds); the two report-only sets each have more than before (wood 4 → 5, Dave's 2 → 4 (one wrong-color box on the orange wood table, one box on two barrels standing together in Dave's frames), and the campus clips keep 11 wrong boxes on a hand or a chair that were there before and are not from these rules (`by_eye.md`).
5. **What is simulated only:** every cell of the table (the hiding is done on the segmentation mask, so no shadow, no reflection and no color bleed of a real occluder is in it); on real pictures the check is 13 occluded or cut barrels of HOME and CAMPUS (12 found, the wedge in `cluster_01` left without a box on purpose) and the recordings, and no real frame exists yet of a barrel hidden from above or below, behind a post, behind a straight edge, or beside a barrel of its own color (shot requests R3 to R5 in `DATA.md`).

Not on by default, and what it would add: `slice_behind` (frame edge at three quarters 29 → 87 of 100, same color beside and lower 29 → 44, 2737 → 2825 scenes in all; it draws 4 more false boxes at medium damage over 20 seeds, which is what the rule refused; `verdict.md`), and the full-size cover box (`slice_box`, `cover_unpinned`, `stripe_two`: 3261 of 3888 found, 58 boxes where no barrel is, 21 false boxes at medium damage; they stay off).
