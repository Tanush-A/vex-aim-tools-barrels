# Why the barrel colours move between conditions: measurements on the labelled train frames

Date 2026-11-23. Read-only analysis of the snapshot; train frames only (261 stems; the loader refuses any stem that is not in `splits.json["train"]`, and no test frame was loaded, scored or viewed). Scripts and raw outputs: `/private/tmp/claude-502/-Users-tanush-Desktop-Celeste-vex-aim-tools-barrels/bc194f8a-459b-4746-98d1-b23688f2f947/scratchpad/work_color` (`common.py`, `s0_calib.py`, `s0_render.py`, `s1_build.py`, `q1.py`, `q1b.py`, `q2.py`, `q2b.py`, `q3.py`, `q4.py`, `q4b.py`, `q56.py`; tables in `out/`).

## Verdicts in one screen

| Hypothesis | Verdict | The numbers |
|---|---|---|
| A. The orange hue shift on the dark ottoman is sensor clipping (R pinned at 255) | **Refuted** | On all four ottoman conditions 0.0% of orange pixels have R >= 250 (side-wall patches, lid, and the whole barrel; 99th percentile of R is 182-190). Hue is 13-15 on the side wall and 15-21 on the lid against 7 and 8 at home. At the same R level (100-149) home reads hue 5, the ottoman 13-16. The frame is not brightened either: frame mean V is 47-53 (home 135). Clipping exists only on the black table (24% of orange patch pixels), and there it accounts for about 2 of a 15-unit hue shift. |
| B. Barrel colour depends on the surface under the same lamp nearly as much as on the lamp; so camera auto gain / white balance is a major cause | **Mixed**: first half supported, the attribution not | 4 lamps x 4 surfaces: surface carries 85% of the variance of orange log R/G (lamp 12%) and 75% of blue log R/G (lamp 18%). But the blue result is the glass table (window light mixed in): without it the lamp carries 73%. No sign of content-driven white balance: frame casts are left uncorrected (gray-world log B/G down to -1.14), and within a condition barrel chroma does not follow frame content (r = +0.03 and -0.09, 98 frames). |
| C. Body-minus-stripe colour difference is nearly constant across conditions | **Refuted as stated; a weaker form holds** | The difference in log(R/B) runs from 1.25 to 4.64 over the ordinary conditions (SD 0.99); the absolute orange body it was meant to replace has SD 0.19. What does hold is the sign with a margin: "both body patches differ from the stripe by more than 0.3, same sign" passes 220 of 220 ordinary barrels and 97 of 98 extreme ones, with 0.63% of random non-barrel triplets passing. |
| (Q4) One von Kries translation in log-chromaticity describes the shift | **Refuted** | One translation removes 41% of the squared shift in the ordinary conditions (RMS 0.75 to 0.57 log units), 34% in the extreme ones. Orange and blue move in opposite directions in log R/G in 15 of 17 ordinary conditions. Hue/S is not regular either (45% and 54%). |
| (Q5) The translation can be read from barrel-free frame statistics | **Not well enough** | Best statistics (gray-world, white patch, top rows) correlate 0.6-0.8 with the common translation; leave-one-place-out error 0.39 against a shift of 0.47 (ordinary). For the orange cluster the prediction is worse than no shift (0.51 against 0.45). |
| (Q6) A 2-parameter physical adaptation beats moving HSV box edges | **Not shown** | With oracle parameters the log-chroma model with a translation matches the best rectangle on orange (97.7 against 97.9) and beats it on blue (89.8 against 84.7). But the same model with no translation scores 94.0 and 89.0: the gain is the per-condition threshold and the region's shape, not the translation. With the predicted translation: 94.3 and 88.6. |

## Methods (short)

**Frames and conditions.** 261 train frames, 28 conditions. Groups as the project uses them: ordinary (18), extreme (7: lamp on the orange wood desk at brightness 6 and 3, and the black table), excluded (3: lamp brightness 1). Home = `window_light`.

**Step 0, patches.** On the 16 home train frames that have pixel masks (19 unflagged barrels) the stripe occupies box-relative rows 0.46-0.67 on average (top edge 0.40-0.50, bottom edge 0.625-0.70), not the middle of the box, because the lid takes the top of the box; the top edge sits lower for close barrels (correlation with box height 0.54). Patches used, all in the centre columns 0.36-0.64 of the box width: stripe rows 0.51-0.61; lower body 0.75-0.90; upper body 0.27-0.37 (box height under 45 px), 0.30-0.40 (45-79), 0.34-0.44 (80 and over), which keeps it under the lid's front edge and above the stripe. Checked against the home masks: 100% of the pixels of every patch carry the expected class (19 barrels, minimum 1.000). Five sheets of crops with the patch outlines over 17 conditions were rendered and looked at (`/private/tmp/claude-502/-Users-tanush-Desktop-Celeste-vex-aim-tools-barrels/bc194f8a-459b-4746-98d1-b23688f2f947/scratchpad/work_color/patches_sheet0.png`, `patches_sheet1.png`, `patches_sheet2.png`, `patches_v2_sheet0.png`, `patches_v2_sheet1.png`): the patches sit on paint. The three `patches_sheet*` files show the first-draft upper patch (rows 0.29-0.41 for every size, before the tipped scenes were dropped); the two `patches_v2_*` files show the final geometry. The first sheets showed that unflagged barrels in the `top`, `topstripe`, `held` and `hand` scenes are tipped or hand-held and have no stripe where an upright barrel has it; those scenes are dropped, as are boxes with width/height outside 0.75-1.25 or height under 24 px (6 barrels dropped in all).

**Barrels used: 360** (ordinary 220 = 109 orange + 111 blue; extreme 98; brightness 1 42). Per condition:

| condition | orange | blue | frames |
|---|---|---|---|
| both_abpgray | 5 | 5 | 4 |
| campus_light | 13 | 13 | 11 |
| lampcool1/mid1/warm1_wood | 6 each | 8 each | 6 each |
| lampcool3/mid3/warm3_wood | 6 each | 8 each | 6 each |
| lampcool6/mid6/warm6_wood | 6 each | 8 each | 6 each |
| lampcool6/mid6/warm6/mid3_bathtile | 6 each | 6 each | 4 each |
| lampcool6/mid6/warm6/mid3_glass | 6 each | 4 each | 4 each |
| lampcool6/mid6/warm6/mid3_ottoman | 5 each | 5 each | 4 each |
| overheaddim_palewood | 6 | 4 | 4 |
| window_abpwhite | 3 | 14 | 16 (the occlusion set: the same barrels shot repeatedly) |
| window_black | 6 | 8 | 7 |
| window_glass | 6 | 4 | 4 |
| window_light (home) | 8 | 11 | 11 |

**Colour measures.** OpenCV hue (0-179; orange hue is unwrapped so 177 reads -3), S, V; log-chromaticity (log((R+1)/(G+1)), log((B+1)/(G+1))) on the camera values as they are. "Clipped" = any channel >= 250; "dark" = brightest channel < 40. Paint classes: orange paint = body of orange barrels and stripe of blue barrels; blue paint likewise.

**Non-barrel pixels.** Rows >= 50, outside every labelled box grown by 4 px (flagged barrels included), every second pixel in both directions, all train frames including negatives and clutter (about 60 000 pixels a frame). Mirror images of barrels on the glass table count as non-barrel.

## Q1. Colours per condition, clipping, and hypothesis A

"orange-stripe" is the orange stripe on a blue barrel; "blue-stripe" the blue stripe on an orange barrel. Medians over the pooled patch pixels of the condition.

### Q1 orange-body

| condition | grp | barrels | px | R | G | B | hue | S | V | clip % | dark % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| window_light | ord | 8 | 1910 | 168 | 52 | 21 | 7 | 223 | 168 | 0 | 0 |
| campus_light | ord | 13 | 4858 | 138 | 50 | 20 | 8 | 217 | 138 | 0 | 0 |
| window_abpwhite | ord | 3 | 688 | 180 | 60 | 25 | 7 | 220 | 180 | 0 | 0 |
| both_abpgray | ord | 5 | 1408 | 197 | 22 | 18 | 1 | 232 | 197 | 0 | 0 |
| overheaddim_palewood | ord | 6 | 1839 | 196 | 65 | 27 | 6 | 221 | 196 | 0 | 0 |
| window_glass | ord | 6 | 1392 | 168 | 57 | 26 | 7 | 213 | 168 | 0 | 0 |
| lampcool6_glass | ord | 6 | 1392 | 156 | 59 | 27 | 7 | 210 | 156 | 0 | 0 |
| lampmid6_glass | ord | 6 | 1392 | 163 | 58 | 22 | 7 | 220 | 163 | 0 | 0 |
| lampwarm6_glass | ord | 6 | 1392 | 167 | 57 | 21 | 7 | 223 | 167 | 0 | 0 |
| lampmid3_glass | ord | 6 | 1392 | 164 | 59 | 26 | 7 | 214 | 164 | 0 | 0 |
| lampcool6_bathtile | ord | 6 | 981 | 148 | 64 | 22 | 10 | 219 | 148 | 0 | 0 |
| lampmid6_bathtile | ord | 6 | 981 | 172 | 69 | 24 | 9 | 221 | 172 | 0 | 0 |
| lampwarm6_bathtile | ord | 6 | 981 | 178 | 64 | 23 | 8 | 222 | 178 | 0 | 0 |
| lampmid3_bathtile | ord | 6 | 981 | 161 | 71 | 24 | 10 | 218 | 161 | 0 | 0 |
| lampcool6_ottoman | ord | 5 | 3036 | 114 | 66 | 19 | 15 | 211 | 114 | 0 | 0 |
| lampmid6_ottoman | ord | 5 | 3036 | 132 | 70 | 21 | 14 | 215 | 132 | 0 | 0 |
| lampwarm6_ottoman | ord | 5 | 3000 | 129 | 67 | 20 | 13 | 214 | 129 | 0 | 0 |
| lampmid3_ottoman | ord | 5 | 3036 | 46 | 23 | 11 | 13 | 205 | 46 | 0 | 38 |
| lampcool6_wood | ext | 6 | 2142 | 171 | 76 | 26 | 12 | 216 | 171 | 0 | 0 |
| lampmid6_wood | ext | 6 | 2142 | 181 | 79 | 27 | 10 | 217 | 181 | 0 | 0 |
| lampwarm6_wood | ext | 6 | 2142 | 186 | 76 | 27 | 9 | 219 | 186 | 0 | 0 |
| lampcool3_wood | ext | 6 | 2142 | 128 | 65 | 23 | 13 | 209 | 128 | 0 | 0 |
| lampmid3_wood | ext | 6 | 2142 | 142 | 73 | 31 | 12 | 200 | 142 | 0 | 0 |
| lampwarm3_wood | ext | 6 | 2142 | 144 | 72 | 27 | 12 | 209 | 144 | 0 | 0 |
| lampcool1_wood | exc | 6 | 2142 | 20 | 19 | 16 | 0 | 0 | 20 | 0 | 90 |
| lampmid1_wood | exc | 6 | 2142 | 21 | 19 | 16 | 0 | 0 | 22 | 0 | 82 |
| lampwarm1_wood | exc | 6 | 2142 | 25 | 21 | 16 | 9 | 71 | 25 | 0 | 69 |
| window_black | ext | 6 | 1540 | 241 | 198 | 114 | 19 | 134 | 241 | 16 | 0 |


### Q1 blue-body

| condition | grp | barrels | px | R | G | B | hue | S | V | clip % | dark % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| window_light | ord | 11 | 2540 | 11 | 48 | 129 | 111 | 233 | 129 | 0 | 0 |
| campus_light | ord | 13 | 4173 | 19 | 53 | 98 | 106 | 214 | 98 | 0 | 0 |
| window_abpwhite | ord | 14 | 4712 | 19 | 87 | 190 | 108 | 230 | 190 | 0 | 0 |
| both_abpgray | ord | 5 | 1872 | 8 | 32 | 112 | 113 | 237 | 112 | 0 | 0 |
| overheaddim_palewood | ord | 4 | 675 | 14 | 58 | 132 | 109 | 226 | 132 | 0 | 0 |
| window_glass | ord | 4 | 1104 | 14 | 62 | 154 | 110 | 232 | 154 | 0 | 0 |
| lampcool6_glass | ord | 4 | 1104 | 14 | 60 | 141 | 109 | 231 | 141 | 0 | 0 |
| lampmid6_glass | ord | 4 | 1104 | 14 | 58 | 135 | 109 | 230 | 135 | 0 | 0 |
| lampwarm6_glass | ord | 4 | 1104 | 16 | 57 | 133 | 110 | 225 | 133 | 0 | 0 |
| lampmid3_glass | ord | 4 | 1104 | 14 | 60 | 144 | 109 | 231 | 144 | 0 | 0 |
| lampcool6_bathtile | ord | 6 | 1560 | 18 | 51 | 72 | 102 | 192 | 72 | 0 | 0 |
| lampmid6_bathtile | ord | 6 | 1560 | 43 | 55 | 58 | 96 | 57 | 58 | 0 | 0 |
| lampwarm6_bathtile | ord | 6 | 1560 | 49 | 49 | 40 | 26 | 50 | 51 | 0 | 0 |
| lampmid3_bathtile | ord | 6 | 1560 | 42 | 46 | 48 | 96 | 31 | 48 | 0 | 6 |
| lampcool6_ottoman | ord | 5 | 1847 | 23 | 60 | 98 | 105 | 192 | 98 | 0 | 2 |
| lampmid6_ottoman | ord | 5 | 1847 | 37 | 57 | 80 | 106 | 126 | 80 | 0 | 8 |
| lampwarm6_ottoman | ord | 5 | 1847 | 42 | 47 | 52 | 102 | 45 | 52 | 0 | 30 |
| lampmid3_ottoman | ord | 5 | 1847 | 18 | 18 | 18 | 0 | 0 | 18 | 0 | 90 |
| lampcool6_wood | ext | 8 | 2161 | 48 | 62 | 67 | 103 | 64 | 67 | 0 | 0 |
| lampmid6_wood | ext | 8 | 2207 | 59 | 62 | 65 | 101 | 30 | 67 | 0 | 0 |
| lampwarm6_wood | ext | 8 | 2207 | 61 | 59 | 54 | 14 | 33 | 62 | 0 | 0 |
| lampcool3_wood | ext | 8 | 2184 | 41 | 46 | 49 | 103 | 37 | 49 | 0 | 23 |
| lampmid3_wood | ext | 8 | 2207 | 52 | 55 | 57 | 83 | 21 | 58 | 0 | 0 |
| lampwarm3_wood | ext | 8 | 2207 | 52 | 53 | 51 | 24 | 19 | 54 | 0 | 0 |
| lampcool1_wood | exc | 8 | 2207 | 2 | 2 | 2 | 0 | 0 | 2 | 0 | 100 |
| lampmid1_wood | exc | 8 | 2207 | 2 | 2 | 2 | 0 | 0 | 2 | 0 | 100 |
| lampwarm1_wood | exc | 8 | 2207 | 2 | 2 | 2 | 0 | 0 | 2 | 0 | 100 |
| window_black | ext | 8 | 3823 | 85 | 190 | 232 | 98 | 161 | 232 | 5 | 0 |


### Q1 orange-stripe (on blue barrels)

| condition | grp | barrels | px | R | G | B | hue | S | V | clip % | dark % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| window_light | ord | 11 | 1026 | 166 | 53 | 20 | 7 | 224 | 166 | 0 | 0 |
| campus_light | ord | 13 | 1654 | 131 | 55 | 29 | 8 | 212 | 131 | 0 | 0 |
| window_abpwhite | ord | 14 | 1929 | 211 | 85 | 33 | 9 | 214 | 211 | 0 | 0 |
| both_abpgray | ord | 5 | 771 | 189 | 20 | 18 | 0 | 234 | 189 | 0 | 0 |
| overheaddim_palewood | ord | 4 | 255 | 206 | 74 | 28 | 8 | 221 | 206 | 0 | 0 |
| window_glass | ord | 4 | 437 | 178 | 63 | 31 | 7 | 212 | 178 | 0 | 0 |
| lampcool6_glass | ord | 4 | 437 | 168 | 63 | 28 | 8 | 213 | 168 | 0 | 0 |
| lampmid6_glass | ord | 4 | 437 | 174 | 63 | 23 | 7 | 221 | 174 | 0 | 0 |
| lampwarm6_glass | ord | 4 | 437 | 178 | 62 | 24 | 7 | 222 | 178 | 0 | 0 |
| lampmid3_glass | ord | 4 | 437 | 174 | 63 | 27 | 7 | 216 | 174 | 0 | 0 |
| lampcool6_bathtile | ord | 6 | 611 | 146 | 62 | 20 | 10 | 219 | 146 | 0 | 0 |
| lampmid6_bathtile | ord | 6 | 611 | 171 | 67 | 25 | 9 | 217 | 171 | 0 | 0 |
| lampwarm6_bathtile | ord | 6 | 611 | 179 | 63 | 24 | 7 | 221 | 179 | 0 | 0 |
| lampmid3_bathtile | ord | 6 | 611 | 160 | 68 | 23 | 10 | 219 | 160 | 0 | 0 |
| lampcool6_ottoman | ord | 5 | 766 | 142 | 92 | 25 | 17 | 210 | 142 | 0 | 0 |
| lampmid6_ottoman | ord | 5 | 766 | 162 | 97 | 27 | 16 | 212 | 162 | 0 | 0 |
| lampwarm6_ottoman | ord | 5 | 744 | 160 | 93 | 26 | 15 | 212 | 160 | 0 | 0 |
| lampmid3_ottoman | ord | 5 | 766 | 57 | 31 | 10 | 13 | 213 | 57 | 0 | 2 |
| lampcool6_wood | ext | 8 | 910 | 169 | 78 | 25 | 11 | 218 | 169 | 0 | 0 |
| lampmid6_wood | ext | 8 | 930 | 185 | 77 | 27 | 10 | 218 | 185 | 0 | 0 |
| lampwarm6_wood | ext | 8 | 930 | 188 | 73 | 27 | 8 | 218 | 188 | 0 | 0 |
| lampcool3_wood | ext | 8 | 920 | 124 | 64 | 21 | 13 | 212 | 124 | 0 | 0 |
| lampmid3_wood | ext | 8 | 930 | 141 | 75 | 30 | 12 | 201 | 141 | 0 | 0 |
| lampwarm3_wood | ext | 8 | 930 | 143 | 74 | 24 | 12 | 212 | 143 | 0 | 0 |
| lampcool1_wood | exc | 8 | 930 | 19 | 19 | 17 | 0 | 0 | 20 | 0 | 94 |
| lampmid1_wood | exc | 8 | 930 | 18 | 19 | 16 | 0 | 0 | 19 | 0 | 95 |
| lampwarm1_wood | exc | 8 | 930 | 22 | 19 | 17 | 0 | 35 | 23 | 0 | 90 |
| window_black | ext | 8 | 1480 | 247 | 230 | 150 | 24 | 100 | 247 | 35 | 0 |


### Q1 blue-stripe (on orange barrels)

| condition | grp | barrels | px | R | G | B | hue | S | V | clip % | dark % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| window_light | ord | 8 | 758 | 11 | 48 | 128 | 110 | 232 | 128 | 0 | 0 |
| campus_light | ord | 13 | 1968 | 24 | 44 | 79 | 108 | 196 | 93 | 0 | 0 |
| window_abpwhite | ord | 3 | 285 | 16 | 58 | 156 | 110 | 230 | 156 | 0 | 0 |
| both_abpgray | ord | 5 | 577 | 11 | 46 | 133 | 112 | 234 | 133 | 0 | 0 |
| overheaddim_palewood | ord | 6 | 740 | 14 | 63 | 145 | 109 | 229 | 145 | 0 | 0 |
| window_glass | ord | 6 | 543 | 12 | 53 | 137 | 110 | 233 | 137 | 0 | 0 |
| lampcool6_glass | ord | 6 | 543 | 11 | 52 | 124 | 109 | 233 | 124 | 0 | 0 |
| lampmid6_glass | ord | 6 | 543 | 11 | 50 | 115 | 109 | 230 | 115 | 0 | 0 |
| lampwarm6_glass | ord | 6 | 543 | 14 | 49 | 111 | 109 | 221 | 111 | 0 | 0 |
| lampmid3_glass | ord | 6 | 543 | 12 | 51 | 125 | 109 | 232 | 125 | 0 | 0 |
| lampcool6_bathtile | ord | 6 | 394 | 19 | 54 | 73 | 102 | 184 | 73 | 0 | 0 |
| lampmid6_bathtile | ord | 6 | 394 | 46 | 55 | 59 | 99 | 60 | 59 | 0 | 0 |
| lampwarm6_bathtile | ord | 6 | 394 | 50 | 50 | 43 | 34 | 40 | 51 | 0 | 0 |
| lampmid3_bathtile | ord | 6 | 394 | 45 | 48 | 50 | 83 | 33 | 52 | 0 | 1 |
| lampcool6_ottoman | ord | 5 | 1187 | 23 | 61 | 90 | 105 | 193 | 95 | 0 | 2 |
| lampmid6_ottoman | ord | 5 | 1187 | 36 | 58 | 75 | 105 | 143 | 81 | 0 | 4 |
| lampwarm6_ottoman | ord | 5 | 1205 | 42 | 48 | 48 | 98 | 51 | 52 | 0 | 22 |
| lampmid3_ottoman | ord | 5 | 1187 | 19 | 18 | 17 | 0 | 0 | 19 | 0 | 95 |
| lampcool6_wood | ext | 6 | 847 | 56 | 70 | 86 | 107 | 88 | 86 | 0 | 0 |
| lampmid6_wood | ext | 6 | 847 | 66 | 65 | 70 | 126 | 18 | 71 | 0 | 0 |
| lampwarm6_wood | ext | 6 | 847 | 68 | 62 | 59 | 18 | 43 | 68 | 0 | 0 |
| lampcool3_wood | ext | 6 | 847 | 44 | 48 | 54 | 103 | 40 | 54 | 0 | 0 |
| lampmid3_wood | ext | 6 | 847 | 56 | 57 | 59 | 103 | 20 | 60 | 0 | 0 |
| lampwarm3_wood | ext | 6 | 847 | 56 | 55 | 54 | 21 | 13 | 56 | 0 | 0 |
| lampcool1_wood | exc | 6 | 847 | 4 | 4 | 4 | 0 | 0 | 4 | 0 | 100 |
| lampmid1_wood | exc | 6 | 847 | 4 | 4 | 4 | 0 | 0 | 4 | 0 | 100 |
| lampwarm1_wood | exc | 6 | 847 | 5 | 5 | 5 | 0 | 0 | 5 | 0 | 100 |
| window_black | ext | 6 | 638 | 89 | 174 | 229 | 102 | 155 | 229 | 2 | 0 |


### Hypothesis A: orange paint, clipped (R>=250) vs unclipped pixels

| condition | grp | frame mean V | R clipped % | G clipped % | hue all | hue unclipped | hue clipped | barrels w/ both | paired hue diff (clipped-unclipped) | log(R/G) unclipped | shift from clipping (all-uncl) | shift without clipping (uncl - home uncl) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| window_light | ord | 135.4 | 0.0 | 0.0 | 7.0 | 7.0 | nan | 0 | nan | 1.1 | 0.0 | 0.0 |
| campus_light | ord | 135.9 | 0.0 | 0.0 | 8.0 | 8.0 | nan | 0 | nan | 0.9 | 0.0 | 1.0 |
| window_abpwhite | ord | 142.8 | 0.0 | 0.0 | 8.0 | 8.0 | nan | 0 | nan | 0.9 | 0.0 | 1.0 |
| both_abpgray | ord | 157.0 | 0.0 | 0.0 | 1.0 | 1.0 | nan | 0 | nan | 2.2 | 0.0 | -6.0 |
| overheaddim_palewood | ord | 158.4 | 0.0 | 0.0 | 6.0 | 6.0 | nan | 0 | nan | 1.1 | 0.0 | -1.0 |
| window_glass | ord | 157.2 | 0.0 | 0.0 | 7.0 | 7.0 | nan | 0 | nan | 1.0 | 0.0 | 0.0 |
| lampcool6_glass | ord | 146.8 | 0.0 | 0.0 | 8.0 | 8.0 | nan | 0 | nan | 1.0 | 0.0 | 1.0 |
| lampmid6_glass | ord | 140.4 | 0.0 | 0.0 | 7.0 | 7.0 | nan | 0 | nan | 1.0 | 0.0 | 0.0 |
| lampwarm6_glass | ord | 144.0 | 0.0 | 0.0 | 7.0 | 7.0 | nan | 0 | nan | 1.1 | 0.0 | 0.0 |
| lampmid3_glass | ord | 141.3 | 0.0 | 0.0 | 7.0 | 7.0 | nan | 0 | nan | 1.0 | 0.0 | 0.0 |
| lampcool6_bathtile | ord | 140.6 | 0.0 | 0.0 | 10.0 | 10.0 | nan | 0 | nan | 0.9 | 0.0 | 3.0 |
| lampmid6_bathtile | ord | 165.5 | 0.0 | 0.0 | 9.0 | 9.0 | nan | 0 | nan | 0.9 | 0.0 | 2.0 |
| lampwarm6_bathtile | ord | 174.3 | 0.0 | 0.0 | 8.0 | 8.0 | nan | 0 | nan | 1.0 | 0.0 | 1.0 |
| lampmid3_bathtile | ord | 157.5 | 0.0 | 0.0 | 10.0 | 10.0 | nan | 0 | nan | 0.8 | 0.0 | 3.0 |
| lampcool6_ottoman | ord | 46.8 | 0.0 | 0.0 | 15.0 | 15.0 | nan | 0 | nan | 0.5 | 0.0 | 8.0 |
| lampmid6_ottoman | ord | 52.3 | 0.0 | 0.0 | 14.0 | 14.0 | nan | 0 | nan | 0.6 | 0.0 | 7.0 |
| lampwarm6_ottoman | ord | 53.3 | 0.0 | 0.0 | 14.0 | 14.0 | nan | 0 | nan | 0.6 | 0.0 | 7.0 |
| lampmid3_ottoman | ord | 20.1 | 0.0 | 0.0 | 13.0 | 13.0 | nan | 0 | nan | 0.6 | 0.0 | 6.0 |
| lampcool6_wood | ext | 168.0 | 0.0 | 0.0 | 11.0 | 11.0 | nan | 0 | nan | 0.7 | 0.0 | 4.0 |
| lampmid6_wood | ext | 184.4 | 0.0 | 0.0 | 10.0 | 10.0 | nan | 0 | nan | 0.8 | 0.0 | 3.0 |
| lampwarm6_wood | ext | 190.0 | 0.0 | 0.0 | 9.0 | 9.0 | nan | 0 | nan | 0.9 | 0.0 | 2.0 |
| lampcool3_wood | ext | 120.8 | 0.0 | 0.0 | 13.0 | 13.0 | nan | 0 | nan | 0.6 | 0.0 | 6.0 |
| lampmid3_wood | ext | 138.6 | 0.0 | 0.0 | 12.0 | 12.0 | nan | 0 | nan | 0.6 | 0.0 | 5.0 |
| lampwarm3_wood | ext | 141.4 | 0.0 | 0.0 | 12.0 | 12.0 | nan | 0 | nan | 0.7 | 0.0 | 5.0 |
| lampcool1_wood | exc | 21.7 | 0.0 | 0.0 | 0.0 | 10.0 | nan | 0 | nan | 0.8 | -10.0 | 3.0 |
| lampmid1_wood | exc | 22.1 | 0.0 | 0.0 | 0.0 | 10.0 | nan | 0 | nan | 0.8 | -10.0 | 3.0 |
| lampwarm1_wood | exc | 24.5 | 0.0 | 0.0 | 6.0 | 11.0 | nan | 0 | nan | 0.8 | -5.0 | 4.0 |
| window_black | ext | 86.6 | 23.7 | 11.9 | 22.0 | 20.0 | 28.0 | 11 | 3.2 | 0.2 | 2.0 | 13.0 |

- all 28: Spearman(orange hue all, R clipped share) = -0.14; Spearman(orange hue unclipped, R clipped share) = -0.30; Spearman(hue all, frame mean V) = -0.12; Spearman(clipped share, frame mean V) = 0.15
- ordinary: Spearman(orange hue all, R clipped share) = -0.15; Spearman(orange hue unclipped, R clipped share) = -0.15; Spearman(hue all, frame mean V) = -0.42; Spearman(clipped share, frame mean V) = -0.08
- not excl: Spearman(orange hue all, R clipped share) = -0.36; Spearman(orange hue unclipped, R clipped share) = -0.36; Spearman(hue all, frame mean V) = -0.48; Spearman(clipped share, frame mean V) = 0.13

### Orange paint hue by R level (median hue; n px), selected conditions

| condition | R 40-99 | R 100-149 | R 150-199 | R 200-234 | R 235-249 | R 250-255 |
|---|---|---|---|---|---|---|
| window_light | - (0) | 5 (374) | 7 (2503) | 9 (59) | - (0) | - (0) |
| campus_light | 8 (330) | 8 (4114) | 8 (1142) | 12 (885) | - (28) | - (0) |
| both_abpgray | -38 (36) | -10 (35) | 0 (1121) | 1 (889) | - (1) | - (0) |
| lampcool6_ottoman | 13 (991) | 16 (1942) | 17 (869) | - (0) | - (0) | - (0) |
| lampmid6_ottoman | 10 (450) | 13 (2039) | 16 (1313) | - (0) | - (0) | - (0) |
| lampwarm6_ottoman | 11 (461) | 13 (2006) | 16 (1277) | - (0) | - (0) | - (0) |
| lampmid3_ottoman | 13 (2624) | - (0) | - (0) | - (0) | - (0) | - (0) |
| lampmid6_glass | - (0) | 9 (253) | 7 (1576) | - (0) | - (0) | - (0) |
| lampmid6_bathtile | - (0) | - (13) | 9 (1541) | 9 (38) | - (0) | - (0) |
| lampwarm6_bathtile | - (0) | - (3) | 8 (1504) | 8 (85) | - (0) | - (0) |
| lampmid6_wood | - (0) | - (0) | 9 (2262) | 11 (810) | - (0) | - (0) |
| lampwarm6_wood | - (0) | - (0) | 8 (2167) | 11 (905) | - (0) | - (0) |
| window_black | - (0) | - (0) | - (0) | 17 (201) | 20 (2103) | 28 (716) |


### Same, G/R and B/R of orange paint (median of pixel values) for clipped vs unclipped

| condition | pixels | n | R | G | B | hue | S |
|---|---|---|---|---|---|---|---|
| window_light | unclipped | 2936 | 167 | 53 | 21 | 7 | 223 |
| lampcool6_ottoman | unclipped | 3802 | 119 | 71 | 21 | 15 | 211 |
| lampmid6_ottoman | unclipped | 3802 | 135 | 76 | 22 | 14 | 214 |
| lampwarm6_ottoman | unclipped | 3744 | 132 | 71 | 21 | 14 | 214 |
| lampmid3_ottoman | unclipped | 2624 | 55 | 29 | 9 | 13 | 213 |
| lampmid6_wood | unclipped | 3072 | 183 | 78 | 27 | 10 | 217 |
| lampwarm6_bathtile | unclipped | 1592 | 178 | 64 | 24 | 8 | 221 |
| window_black | unclipped | 2304 | 242 | 202 | 121 | 20 | 128 |
| window_black | clipped | 716 | 252 | 249 | 187 | 28 | 67 |

### Q1b orange barrels: the lid (rows 0.06-0.20 of the box, centre columns) and the whole barrel (ellipse inside the box)

| condition | grp | lid R | lid G | lid B | lid hue | lid S | lid R>=250 % | whole barrel R>=250 % | whole barrel any channel >=250 % | whole barrel R 99th pct |
|---|---|---|---|---|---|---|---|---|---|---|
| window_light | ord | 184.0 | 66.0 | 26.0 | 8.0 | 220.0 | 0.0 | 0.0 | 0.0 | 208.0 |
| campus_light | ord | 166.0 | 65.0 | 25.0 | 9.0 | 218.0 | 0.7 | 0.1 | 0.1 | 229.0 |
| window_abpwhite | ord | 202.0 | 76.0 | 29.0 | 8.0 | 218.0 | 0.0 | 0.0 | 0.0 | 222.0 |
| both_abpgray | ord | 226.0 | 114.0 | 49.0 | 10.0 | 200.0 | 6.3 | 0.5 | 0.5 | 244.0 |
| overheaddim_palewood | ord | 227.0 | 119.0 | 46.0 | 11.0 | 204.0 | 0.4 | 0.0 | 0.0 | 237.0 |
| window_glass | ord | 192.0 | 72.0 | 29.0 | 8.0 | 215.0 | 0.0 | 0.0 | 0.0 | 222.0 |
| lampcool6_glass | ord | 186.0 | 72.0 | 27.0 | 9.0 | 218.0 | 0.0 | 0.0 | 0.0 | 206.0 |
| lampmid6_glass | ord | 193.0 | 72.0 | 25.0 | 8.0 | 221.0 | 0.0 | 0.0 | 0.0 | 210.0 |
| lampwarm6_glass | ord | 197.0 | 70.0 | 26.0 | 8.0 | 221.0 | 0.0 | 0.0 | 0.0 | 211.0 |
| lampmid3_glass | ord | 192.0 | 72.0 | 27.0 | 8.0 | 219.0 | 0.0 | 0.0 | 0.0 | 214.0 |
| lampcool6_bathtile | ord | 201.0 | 92.0 | 28.0 | 12.0 | 219.0 | 0.0 | 0.0 | 0.0 | 219.0 |
| lampmid6_bathtile | ord | 215.0 | 92.0 | 29.0 | 10.0 | 219.0 | 0.0 | 0.0 | 0.0 | 228.0 |
| lampwarm6_bathtile | ord | 217.0 | 85.0 | 29.0 | 9.0 | 220.0 | 0.0 | 0.0 | 0.0 | 228.0 |
| lampmid3_bathtile | ord | 208.0 | 100.0 | 32.0 | 12.0 | 216.0 | 0.0 | 0.0 | 0.0 | 223.0 |
| lampcool6_ottoman | ord | 163.0 | 118.0 | 44.0 | 19.0 | 183.0 | 0.0 | 0.0 | 0.0 | 184.0 |
| lampmid6_ottoman | ord | 173.0 | 129.0 | 35.0 | 21.0 | 204.0 | 0.0 | 0.0 | 0.0 | 189.8 |
| lampwarm6_ottoman | ord | 167.0 | 124.0 | 32.0 | 21.0 | 204.0 | 0.0 | 0.0 | 0.0 | 182.0 |
| lampmid3_ottoman | ord | 74.0 | 44.0 | 14.0 | 15.0 | 205.0 | 0.0 | 0.0 | 0.0 | 81.8 |
| lampcool6_wood | ext | 234.0 | 169.0 | 49.0 | 19.0 | 202.0 | 2.6 | 0.2 | 0.2 | 245.0 |
| lampmid6_wood | ext | 234.0 | 165.0 | 44.0 | 19.0 | 207.0 | 2.9 | 0.3 | 0.3 | 244.0 |
| lampwarm6_wood | ext | 233.0 | 165.0 | 43.0 | 19.0 | 208.0 | 1.8 | 0.2 | 0.2 | 243.0 |
| lampcool3_wood | ext | 200.0 | 133.0 | 60.0 | 15.0 | 180.0 | 0.0 | 0.0 | 0.0 | 216.0 |
| lampmid3_wood | ext | 216.0 | 139.0 | 54.0 | 15.0 | 190.0 | 0.0 | 0.0 | 0.0 | 229.0 |
| lampwarm3_wood | ext | 216.0 | 135.0 | 42.0 | 16.0 | 204.0 | 0.0 | 0.0 | 0.0 | 228.0 |
| lampcool1_wood | exc | 53.0 | 28.0 | 11.0 | 13.0 | 204.0 | 0.0 | 0.0 | 0.0 | 68.0 |
| lampmid1_wood | exc | 58.0 | 29.0 | 10.0 | 12.0 | 213.0 | 0.0 | 0.0 | 0.0 | 70.0 |
| lampwarm1_wood | exc | 62.0 | 31.0 | 9.0 | 13.0 | 215.0 | 0.0 | 0.0 | 0.0 | 76.0 |
| window_black | ext | 247.0 | 229.0 | 139.0 | 24.0 | 110.0 | 34.5 | 14.3 | 16.0 | 255.0 |

**Verdict on A: refuted for the ottoman.** No orange pixel on the ottoman is clipped, on the side wall, on the lid, or anywhere in the barrel (0.0% with R >= 250; the 99th percentile of R is 182-190, and 82 at lamp brightness 3). The hue is nevertheless 13-15 on the side wall (home 7) and, on the lid, 19-21 at lamp brightness 6 and 15 at brightness 3 (home 8). The premise does not hold either: the camera does not brighten the ottoman scene (frame mean V 47-53 against 135 at home; 20 at brightness 3), and the orange barrels come out darker than at home (R 114-132 against 168). At lamp brightness 3 the orange R is 46 and the hue is still 13. Comparing like with like, orange pixels with R in 100-149 read hue 5 at home and 13-16 on the ottoman. What changed is the ratio G/R of unclipped pixels: log(R/G) is 1.1 at home and 0.5-0.6 on the ottoman. Across conditions the hue does not follow the clipped share (Spearman -0.15, ordinary) and it rises as the frame gets darker, not brighter (Spearman with frame mean V -0.42). Clipping is real in one condition only, the black table (24% of orange patch pixels, 14% of the whole barrel): there clipped pixels read hue 28 and unclipped ones 20 (paired within 11 barrels: +3.2), so clipping adds about 2 units to a median that is already 13 above home through desaturation (S 134, R 241, G 198: glare).

Within every condition the brighter orange pixels are somewhat more yellow (home: hue 5, 7, 9 for R 100-149, 150-199, 200-234; ottoman 13, 16, 17), a few units, without clipping. I did not identify what causes the G/R change on the ottoman; it is not 8-bit clipping.

## Q2. Lamp against surface; auto exposure and white balance (hypothesis B)

### Q2 per-condition barrel body colour (mean over barrels of patch-mean colour) and frame statistics

| condition | grp | orange logR/G | orange logB/G | orange brightness | blue logR/G | blue logB/G | blue brightness | frame mean V | frame clipped % | gray-world logR/G | gray-world logB/G | table(bottom 80 rows) logR/G | table logB/G |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| window_light | ord | 1.05 | -0.89 | 87.59 | -1.45 | 0.91 | 69.07 | 135.37 | 1.47 | -0.05 | -0.03 | -0.05 | -0.20 |
| campus_light | ord | 0.90 | -0.85 | 81.05 | -1.04 | 0.59 | 61.54 | 135.88 | 0.45 | -0.03 | -0.03 | -0.11 | -0.02 |
| window_abpwhite | ord | 1.00 | -0.80 | 94.62 | -1.43 | 0.76 | 97.24 | 142.84 | 0.15 | 0.04 | -0.08 | -0.00 | -0.18 |
| both_abpgray | ord | 1.90 | -0.34 | 82.52 | -1.33 | 1.15 | 59.42 | 157.03 | 2.73 | 0.23 | 0.12 | 0.21 | 0.09 |
| overheaddim_palewood | ord | 1.09 | -0.81 | 100.91 | -1.19 | 0.79 | 70.32 | 158.44 | 0.37 | 0.31 | -0.10 | 0.38 | -0.26 |
| window_glass | ord | 1.00 | -0.73 | 85.89 | -1.44 | 0.88 | 79.68 | 157.17 | 0.25 | -0.07 | 0.14 | -0.17 | 0.14 |
| lampcool6_glass | ord | 0.94 | -0.77 | 81.99 | -1.42 | 0.83 | 72.88 | 146.78 | 0.01 | -0.10 | 0.07 | -0.19 | 0.06 |
| lampmid6_glass | ord | 1.00 | -0.91 | 82.89 | -1.34 | 0.82 | 70.26 | 140.36 | 0.01 | 0.03 | 0.01 | -0.02 | -0.02 |
| lampwarm6_glass | ord | 1.03 | -0.93 | 83.85 | -1.07 | 0.80 | 70.87 | 144.04 | 0.01 | 0.11 | -0.04 | 0.06 | -0.07 |
| lampmid3_glass | ord | 0.99 | -0.78 | 83.39 | -1.42 | 0.84 | 74.12 | 141.28 | 0.02 | -0.00 | 0.07 | -0.06 | 0.06 |
| lampcool6_bathtile | ord | 0.86 | -1.07 | 80.44 | -0.99 | 0.33 | 49.78 | 140.60 | 0.00 | 0.02 | -0.40 | -0.03 | -0.40 |
| lampmid6_bathtile | ord | 0.94 | -1.05 | 90.16 | -0.25 | 0.06 | 53.59 | 165.45 | 0.01 | 0.23 | -0.70 | 0.17 | -0.73 |
| lampwarm6_bathtile | ord | 1.02 | -0.99 | 91.03 | 0.00 | -0.17 | 48.17 | 174.31 | 0.01 | 0.34 | -1.14 | 0.28 | -1.21 |
| lampmid3_bathtile | ord | 0.84 | -1.05 | 87.20 | -0.09 | 0.03 | 47.43 | 157.51 | 0.01 | 0.20 | -0.62 | 0.16 | -0.66 |
| lampcool6_ottoman | ord | 0.52 | -1.14 | 64.79 | -0.90 | 0.44 | 59.32 | 46.78 | 0.01 | 0.02 | -0.08 | 0.00 | -0.00 |
| lampmid6_ottoman | ord | 0.60 | -1.22 | 71.19 | -0.37 | 0.29 | 57.32 | 52.31 | 0.01 | 0.10 | -0.16 | 0.01 | -0.01 |
| lampwarm6_ottoman | ord | 0.63 | -1.20 | 69.42 | -0.12 | 0.07 | 48.01 | 53.30 | 0.00 | 0.16 | -0.25 | 0.02 | -0.02 |
| lampmid3_ottoman | ord | 0.49 | -0.67 | 26.16 | -0.05 | 0.06 | 18.88 | 20.09 | 0.00 | 0.06 | -0.07 | 0.00 | 0.00 |
| lampcool6_wood | ext | 0.75 | -1.11 | 98.31 | -0.29 | 0.19 | 68.73 | 167.98 | 0.12 | 0.11 | -0.51 | 0.06 | -0.58 |
| lampmid6_wood | ext | 0.84 | -1.04 | 100.96 | -0.07 | 0.07 | 68.37 | 184.39 | 0.28 | 0.26 | -0.76 | 0.24 | -0.91 |
| lampwarm6_wood | ext | 0.90 | -1.03 | 101.56 | 0.02 | -0.07 | 63.90 | 189.97 | 0.21 | 0.35 | -0.96 | 0.34 | -1.08 |
| lampcool3_wood | ext | 0.65 | -1.04 | 76.59 | -0.14 | 0.10 | 52.31 | 120.85 | 0.00 | 0.11 | -0.42 | 0.08 | -0.49 |
| lampmid3_wood | ext | 0.63 | -0.87 | 87.49 | -0.06 | 0.05 | 60.71 | 138.55 | 0.00 | 0.21 | -0.51 | 0.20 | -0.60 |
| lampwarm3_wood | ext | 0.66 | -1.03 | 86.23 | -0.02 | -0.02 | 57.32 | 141.44 | 0.00 | 0.27 | -0.70 | 0.27 | -0.90 |
| lampcool1_wood | exc | 0.24 | -0.20 | 20.65 | -0.01 | -0.00 | 6.46 | 21.65 | 0.00 | 0.01 | -0.05 | 0.00 | 0.00 |
| lampmid1_wood | exc | 0.39 | -0.27 | 21.49 | -0.00 | 0.01 | 6.26 | 22.10 | 0.00 | 0.03 | -0.06 | 0.00 | 0.00 |
| lampwarm1_wood | exc | 0.45 | -0.49 | 23.93 | -0.00 | 0.01 | 6.98 | 24.48 | 0.00 | 0.04 | -0.09 | 0.00 | 0.00 |
| window_black | ext | 0.16 | -0.46 | 194.49 | -0.68 | 0.20 | 171.64 | 86.57 | 0.98 | 0.01 | -0.06 | 0.05 | -0.07 |


### Q2 lamp x surface layout (4 lamp settings x 4 surfaces): share of the variance of the 16 condition means

| barrel | measure | SD of 16 cells | lamp % | surface % | interaction % | mean range across surfaces (lamp fixed) | mean range across lamps (surface fixed) |
|---|---|---|---|---|---|---|---|
| orange | log R/G | 0.18 | 12.21 | 84.52 | 3.27 | 0.43 | 0.17 |
| orange | log B/G | 0.15 | 31.23 | 30.58 | 38.19 | 0.33 | 0.26 |
| orange | log brightness | 0.31 | 15.27 | 52.69 | 32.04 | 0.59 | 0.32 |
| blue | log R/G | 0.54 | 17.90 | 74.55 | 7.55 | 1.22 | 0.63 |
| blue | log B/G | 0.34 | 9.56 | 85.73 | 4.71 | 0.80 | 0.29 |
| blue | log brightness | 0.32 | 17.28 | 45.35 | 37.37 | 0.60 | 0.36 |


orange lr (rows lamp ['cool6', 'mid6', 'warm6', 'mid3'], cols surface ['glass', 'bathtile', 'ottoman', 'wood']):
  cool6: +0.94  +0.86  +0.52  +0.75
  mid6: +1.00  +0.94  +0.60  +0.84
  warm6: +1.03  +1.02  +0.63  +0.90
  mid3: +0.99  +0.84  +0.49  +0.63

orange lb (rows lamp ['cool6', 'mid6', 'warm6', 'mid3'], cols surface ['glass', 'bathtile', 'ottoman', 'wood']):
  cool6: -0.77  -1.07  -1.14  -1.11
  mid6: -0.91  -1.05  -1.22  -1.04
  warm6: -0.93  -0.99  -1.20  -1.03
  mid3: -0.78  -1.05  -0.67  -0.87

orange ly (rows lamp ['cool6', 'mid6', 'warm6', 'mid3'], cols surface ['glass', 'bathtile', 'ottoman', 'wood']):
  cool6: +4.41  +4.39  +4.17  +4.59
  mid6: +4.42  +4.50  +4.27  +4.61
  warm6: +4.43  +4.51  +4.24  +4.62
  mid3: +4.42  +4.47  +3.26  +4.47

blue lr (rows lamp ['cool6', 'mid6', 'warm6', 'mid3'], cols surface ['glass', 'bathtile', 'ottoman', 'wood']):
  cool6: -1.42  -0.99  -0.90  -0.29
  mid6: -1.34  -0.25  -0.37  -0.07
  warm6: -1.07  +0.00  -0.12  +0.02
  mid3: -1.42  -0.09  -0.05  -0.06

blue lb (rows lamp ['cool6', 'mid6', 'warm6', 'mid3'], cols surface ['glass', 'bathtile', 'ottoman', 'wood']):
  cool6: +0.83  +0.33  +0.44  +0.19
  mid6: +0.82  +0.06  +0.29  +0.07
  warm6: +0.80  -0.17  +0.07  -0.07
  mid3: +0.84  +0.03  +0.06  +0.05

blue ly (rows lamp ['cool6', 'mid6', 'warm6', 'mid3'], cols surface ['glass', 'bathtile', 'ottoman', 'wood']):
  cool6: +4.29  +3.91  +4.08  +4.23
  mid6: +4.25  +3.98  +4.05  +4.22
  warm6: +4.26  +3.87  +3.87  +4.16
  mid3: +4.31  +3.86  +2.94  +4.11

Same decomposition on the three lamp-only surfaces (bathtile, ottoman, wood; glass has window light mixed in):
| barrel | measure | SD of 12 cells | lamp % | surface % | interaction % |
|---|---|---|---|---|---|
| orange | lr | 0.17 | 20.27 | 77.89 | 1.84 |
| orange | lb | 0.14 | 50.23 | 1.71 | 48.06 |
| orange | ly | 0.35 | 20.70 | 52.14 | 27.16 |
| blue | lr | 0.33 | 72.60 | 13.02 | 14.39 |
| blue | lb | 0.16 | 69.89 | 19.75 | 10.36 |
| blue | ly | 0.33 | 30.81 | 31.06 | 38.12 |


### Q2 within one condition: barrel-to-barrel and frame-to-frame spread

| group | barrel | measure | barrels | SD within condition (barrels) | SD of frame means within condition | SD between condition means | between / within |
|---|---|---|---|---|---|---|---|
| ordinary | orange | lr | 109 | 0.101 | 0.100 | 0.298 | 2.937 |
| ordinary | orange | lb | 109 | 0.102 | 0.094 | 0.208 | 2.038 |
| ordinary | orange | ly | 109 | 0.124 | 0.110 | 0.284 | 2.292 |
| ordinary | blue | lr | 111 | 0.127 | 0.134 | 0.549 | 4.319 |
| ordinary | blue | lb | 111 | 0.066 | 0.065 | 0.381 | 5.776 |
| ordinary | blue | ly | 111 | 0.157 | 0.151 | 0.336 | 2.141 |
| extreme | orange | lr | 42 | 0.047 | 0.051 | 0.222 | 4.750 |
| extreme | orange | lb | 42 | 0.060 | 0.062 | 0.206 | 3.408 |
| extreme | orange | ly | 42 | 0.047 | 0.050 | 0.281 | 5.985 |
| extreme | blue | lr | 56 | 0.067 | 0.056 | 0.226 | 3.377 |
| extreme | blue | lb | 56 | 0.045 | 0.042 | 0.091 | 2.035 |
| extreme | blue | ly | 56 | 0.112 | 0.097 | 0.370 | 3.305 |


### Q2 within one condition: does a frame whose content differs show the barrels in another colour?

Per frame: deviation of its barrels (both colours, each from its condition-and-colour mean) against the deviation of the frame statistic from the condition mean. AWB that follows scene content predicts a NEGATIVE slope for chroma; AE that follows scene brightness predicts a NEGATIVE slope for brightness against the brightness of the rest of the scene.

| conditions | pair | frames | r | slope | SD x | SD y |
|---|---|---|---|---|---|---|
| ordinary | log R/G vs frame gray-world log R/G | 98 | 0.034 | 0.182 | 0.017 | 0.090 |
| ordinary | log B/G vs frame gray-world log B/G | 98 | -0.093 | -0.290 | 0.023 | 0.073 |
| ordinary | log R/G vs non-barrel mean log R/G | 98 | -0.051 | -0.294 | 0.016 | 0.090 |
| ordinary | log B/G vs non-barrel mean log B/G | 98 | -0.054 | -0.193 | 0.020 | 0.073 |
| ordinary | brightness vs frame mean V (log) | 98 | 0.237 | 0.247 | 0.122 | 0.127 |
| ordinary | brightness vs non-barrel mean V (log) | 98 | 0.186 | 0.196 | 0.120 | 0.127 |
| ordinary+extreme | log R/G vs frame gray-world log R/G | 141 | 0.036 | 0.130 | 0.022 | 0.080 |
| ordinary+extreme | log B/G vs frame gray-world log B/G | 141 | 0.049 | 0.073 | 0.043 | 0.065 |
| ordinary+extreme | log R/G vs non-barrel mean log R/G | 141 | -0.015 | -0.073 | 0.016 | 0.080 |
| ordinary+extreme | log B/G vs non-barrel mean log B/G | 141 | 0.077 | 0.140 | 0.036 | 0.065 |
| ordinary+extreme | brightness vs frame mean V (log) | 141 | 0.211 | 0.227 | 0.108 | 0.116 |
| ordinary+extreme | brightness vs non-barrel mean V (log) | 141 | 0.167 | 0.183 | 0.106 | 0.116 |


By scene kind (mean deviation of the barrels of that scene from their condition mean, over conditions; ordinary + extreme, not brightness 1):

| scene | conditions | d logR/G | se | d logB/G | se | d log brightness | se | brighter than condition mean % |
|---|---|---|---|---|---|---|---|---|
| core | 23 | 0.004 | 0.012 | -0.001 | 0.009 | 0.047 | 0.024 | 78.261 |
| edge | 15 | 0.041 | 0.024 | 0.031 | 0.026 | -0.030 | 0.009 | 20.000 |
| touch | 24 | 0.001 | 0.010 | -0.001 | 0.007 | -0.042 | 0.017 | 25.000 |
| occl | 8 | 0.030 | 0.016 | -0.003 | 0.013 | -0.121 | 0.021 | 12.500 |
| clutter | 23 | -0.061 | 0.016 | -0.005 | 0.012 | 0.040 | 0.019 | 69.565 |
| cluster | 9 | 0.031 | 0.007 | -0.003 | 0.009 | -0.019 | 0.025 | 22.222 |

### Q2b noise inside the lower body patch (SD after removing a plane), a stand-in for camera gain

| condition | grp | orange patch noise G | orange patch noise R | blue patch noise G | orange log R/G | orange brightness | frame mean V |
|---|---|---|---|---|---|---|---|
| window_light | ord | 1.44 | 2.00 | 1.47 | 1.05 | 87.59 | 135.37 |
| campus_light | ord | 1.79 | 2.47 | 1.61 | 0.90 | 81.05 | 135.88 |
| window_abpwhite | ord | 1.48 | 2.43 | 1.61 | 1.00 | 94.62 | 142.84 |
| both_abpgray | ord | 1.92 | 2.65 | 2.17 | 1.90 | 82.52 | 157.03 |
| overheaddim_palewood | ord | 3.50 | 3.61 | 2.97 | 1.09 | 100.91 | 158.44 |
| window_glass | ord | 1.44 | 2.74 | 1.32 | 1.00 | 85.89 | 157.17 |
| lampcool6_glass | ord | 1.72 | 2.62 | 1.63 | 0.94 | 81.99 | 146.78 |
| lampmid6_glass | ord | 1.39 | 2.56 | 1.68 | 1.00 | 82.89 | 140.36 |
| lampwarm6_glass | ord | 1.34 | 2.43 | 1.67 | 1.03 | 83.85 | 144.04 |
| lampmid3_glass | ord | 1.61 | 2.56 | 1.58 | 0.99 | 83.39 | 141.28 |
| lampcool6_bathtile | ord | 1.74 | 3.39 | 1.99 | 0.86 | 80.44 | 140.60 |
| lampmid6_bathtile | ord | 1.47 | 2.27 | 1.62 | 0.94 | 90.16 | 165.45 |
| lampwarm6_bathtile | ord | 2.16 | 2.69 | 1.59 | 1.02 | 91.03 | 174.31 |
| lampmid3_bathtile | ord | 2.12 | 3.27 | 1.85 | 0.84 | 87.20 | 157.51 |
| lampcool6_ottoman | ord | 1.99 | 2.87 | 2.35 | 0.52 | 64.79 | 46.78 |
| lampmid6_ottoman | ord | 2.02 | 2.98 | 2.55 | 0.60 | 71.19 | 52.31 |
| lampwarm6_ottoman | ord | 2.11 | 2.78 | 1.77 | 0.63 | 69.42 | 53.30 |
| lampmid3_ottoman | ord | 1.52 | 2.51 | 0.96 | 0.49 | 26.16 | 20.09 |
| lampcool6_wood | ext | 2.10 | 2.52 | 1.81 | 0.75 | 98.31 | 167.98 |
| lampmid6_wood | ext | 2.26 | 2.49 | 1.43 | 0.84 | 100.96 | 184.39 |
| lampwarm6_wood | ext | 1.86 | 2.47 | 1.62 | 0.90 | 101.56 | 189.97 |
| lampcool3_wood | ext | 2.10 | 2.78 | 2.06 | 0.65 | 76.59 | 120.85 |
| lampmid3_wood | ext | 2.30 | 2.49 | 1.96 | 0.63 | 87.49 | 138.55 |
| lampwarm3_wood | ext | 1.84 | 2.09 | 1.58 | 0.66 | 86.23 | 141.44 |
| lampcool1_wood | exc | 1.44 | 2.27 | 0.89 | 0.24 | 20.65 | 21.65 |
| lampmid1_wood | exc | 1.34 | 2.20 | 0.81 | 0.39 | 21.49 | 22.10 |
| lampwarm1_wood | exc | 1.34 | 2.75 | 0.87 | 0.45 | 23.93 | 24.48 |
| window_black | ext | 2.87 | 3.23 | 3.54 | 0.16 | 194.49 | 86.57 |

- not brightness 1 (25): Spearman(orange log R/G, orange patch noise G) = -0.40; (orange log R/G, blue patch noise G) = -0.24; (orange log R/G, orange brightness) = 0.29; (orange log R/G, frame mean V) = 0.53
- ordinary (18): Spearman(orange log R/G, orange patch noise G) = -0.22; (orange log R/G, blue patch noise G) = -0.06; (orange log R/G, orange brightness) = 0.74; (orange log R/G, frame mean V) = 0.58

**Verdict on B: mixed.** The descriptive half is supported. Under the same four lamp settings, the surface accounts for 85% of the variance of the orange body's log R/G (lamp 12%); the mean range across surfaces at a fixed lamp is 0.43 against 0.17 across lamps at a fixed surface. For blue the surface share is 75-86%, but that is the glass table, which stands next to a window and reads like home under every lamp setting; on the three surfaces lit by the lamp alone the lamp carries 73% (log R/G) and 70% (log B/G) of the blue variance and the surface 13-20%, while the orange log R/G is still 78% surface. Brightness is about half surface (45-53%).

The attribution to camera auto white balance is not supported by anything measured here:
- The frame's own cast is left uncorrected: gray-world log B/G is -0.40 to -1.14 on the bathroom tile and -0.42 to -0.96 on the wood desk, and the table itself reads as yellow as that. A white balance that followed scene content would have pulled these toward 0.
- Within one condition, a frame whose content differs does not show its barrels in a different colour: r = +0.03 (log R/G) and -0.09 (log B/G) over 98 ordinary frames, against the frame's gray-world deviation; the spread of barrels within a condition (SD 0.10 in orange log R/G) is a third of the spread between conditions (0.30). The one systematic content effect is in clutter frames: barrels read 0.061 +- 0.016 lower in log R/G (23 conditions), a fifth of the between-condition SD. Frame content varies little within a condition (SD 0.02), so this test is weak against a slow or small adjustment.
- Auto exposure is visible in brightness: lamp brightness 3 against 6 leaves frame mean V and barrel brightness nearly unchanged on glass (83 and 83), tile (87 and 90) and wood (87 and 101). It does not act on the ottoman (orange brightness 71 at brightness 6, 26 at brightness 3; frame mean V 52 and 20). Within a condition barrels are not darker when the rest of the frame is brighter (slope +0.20, r 0.19).
- Patch noise as a stand-in for camera gain does not track the orange colour (Spearman -0.22, ordinary): inconclusive.

Surface is confounded with things that are not the camera: the glass table has daylight mixed in, the lamp pointed at the ceiling on the wood desk and down at the table on the ottoman and tile, the rooms differ. The data cannot separate "the camera changed its gains" from "the light reaching the barrel changed"; they show only that scene-content-driven white balance is not visible.

## Q3. The sandwich (hypothesis C)

Per barrel, from the mean colour of each patch: absolute body log(R/B); body minus stripe; and the sandwich score = the smaller of (upper minus stripe) and (lower minus stripe) when both have the same sign, else 0. A barrel passes at T when the score is beyond T with the sign of its colour (positive for orange, negative for blue). False-alarm side: 600 random triplets per train frame with the same patch geometry, box height taken from the bottom row (h = 0.630 * bottom row - 56.1, residual SD 1.7 px over the 360 barrels) times a random 0.85-1.15, not overlapping any labelled box grown by 4 px, upper patch below row 50; a triplet is a false alarm when its score is beyond T with either sign. A second sample uses any height 24-160 at any row.

### Q3 per condition: absolute body log(R/B) against body-minus-stripe log(R/B)

| condition | grp | n orange | orange |abs| mean | sd | orange diff mean | sd | orange worst sandwich | n blue | blue abs mean | sd | blue diff mean | sd | blue worst sandwich (sign flipped) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| window_light | ord | 8 | 1.92 | 0.20 | 3.97 | 0.69 | 1.91 | 11 | -2.36 | 0.08 | -4.40 | 0.13 | 3.99 |
| campus_light | ord | 13 | 1.75 | 0.18 | 3.09 | 0.73 | 1.08 | 13 | -1.64 | 0.34 | -3.28 | 0.58 | 1.65 |
| window_abpwhite | ord | 3 | 1.76 | 0.15 | 3.97 | 0.23 | 3.37 | 14 | -2.18 | 0.08 | -3.80 | 0.25 | 3.36 |
| both_abpgray | ord | 5 | 2.23 | 0.10 | 4.64 | 0.07 | 4.36 | 5 | -2.47 | 0.03 | -4.49 | 0.47 | 3.58 |
| overheaddim_palewood | ord | 6 | 1.88 | 0.08 | 3.92 | 0.27 | 3.50 | 4 | -1.95 | 0.17 | -3.79 | 0.38 | 2.84 |
| window_glass | ord | 6 | 1.73 | 0.13 | 4.02 | 0.27 | 3.42 | 4 | -2.31 | 0.05 | -3.94 | 0.33 | 3.44 |
| lampcool6_glass | ord | 6 | 1.71 | 0.06 | 4.00 | 0.15 | 3.74 | 4 | -2.25 | 0.05 | -4.00 | 0.05 | 3.91 |
| lampmid6_glass | ord | 6 | 1.90 | 0.05 | 4.05 | 0.24 | 3.42 | 4 | -2.16 | 0.13 | -4.13 | 0.13 | 3.94 |
| lampwarm6_glass | ord | 6 | 1.95 | 0.08 | 3.86 | 0.27 | 3.17 | 4 | -1.90 | 0.24 | -3.93 | 0.23 | 3.58 |
| lampmid3_glass | ord | 6 | 1.77 | 0.03 | 4.03 | 0.13 | 3.70 | 4 | -2.27 | 0.05 | -4.09 | 0.10 | 3.93 |
| lampcool6_bathtile | ord | 6 | 1.94 | 0.04 | 3.12 | 0.36 | 2.60 | 6 | -1.34 | 0.15 | -3.30 | 0.16 | 2.93 |
| lampmid6_bathtile | ord | 6 | 1.99 | 0.05 | 2.24 | 0.10 | 2.10 | 6 | -0.33 | 0.07 | -2.23 | 0.09 | 2.01 |
| lampwarm6_bathtile | ord | 6 | 2.01 | 0.04 | 1.80 | 0.11 | 1.58 | 6 | 0.16 | 0.04 | -1.85 | 0.08 | 1.66 |
| lampmid3_bathtile | ord | 6 | 1.89 | 0.05 | 1.97 | 0.11 | 1.80 | 6 | -0.14 | 0.06 | -2.04 | 0.10 | 1.87 |
| lampcool6_ottoman | ord | 5 | 1.66 | 0.08 | 2.84 | 0.43 | 2.21 | 5 | -1.31 | 0.13 | -2.99 | 0.13 | 2.69 |
| lampmid6_ottoman | ord | 5 | 1.81 | 0.05 | 2.38 | 0.30 | 1.89 | 5 | -0.66 | 0.03 | -2.42 | 0.04 | 2.35 |
| lampwarm6_ottoman | ord | 5 | 1.82 | 0.04 | 1.88 | 0.23 | 1.41 | 5 | -0.21 | 0.04 | -1.99 | 0.04 | 1.85 |
| lampmid3_ottoman | ord | 5 | 1.26 | 0.19 | 1.25 | 0.11 | 0.37 | 5 | -0.13 | 0.16 | -1.80 | 0.16 | 1.51 |
| lampcool6_wood | ext | 6 | 1.86 | 0.03 | 2.25 | 0.06 | 2.12 | 8 | -0.53 | 0.13 | -2.29 | 0.21 | 1.76 |
| lampmid6_wood | ext | 6 | 1.87 | 0.02 | 1.94 | 0.02 | 1.82 | 8 | -0.16 | 0.08 | -1.97 | 0.12 | 1.62 |
| lampwarm6_wood | ext | 6 | 1.92 | 0.03 | 1.79 | 0.05 | 1.70 | 8 | 0.08 | 0.09 | -1.83 | 0.09 | 1.60 |
| lampcool3_wood | ext | 6 | 1.68 | 0.09 | 1.86 | 0.12 | 1.57 | 8 | -0.27 | 0.12 | -1.85 | 0.17 | 1.47 |
| lampmid3_wood | ext | 6 | 1.50 | 0.05 | 1.56 | 0.04 | 1.44 | 8 | -0.13 | 0.06 | -1.56 | 0.14 | 1.24 |
| lampwarm3_wood | ext | 6 | 1.68 | 0.05 | 1.65 | 0.05 | 1.50 | 8 | -0.01 | 0.06 | -1.64 | 0.24 | 1.20 |
| lampcool1_wood | exc | 6 | 0.50 | 0.30 | 0.48 | 0.28 | 0.00 | 8 | -0.01 | 0.02 | -0.25 | 0.40 | -0.00 |
| lampmid1_wood | exc | 6 | 0.75 | 0.39 | 0.74 | 0.39 | 0.00 | 8 | -0.01 | 0.03 | -0.33 | 0.63 | -0.00 |
| lampwarm1_wood | exc | 6 | 1.01 | 0.50 | 0.99 | 0.49 | 0.00 | 8 | -0.01 | 0.02 | -0.53 | 0.51 | -0.00 |
| window_black | ext | 6 | 0.58 | 0.19 | 1.36 | 0.48 | 0.23 | 8 | -0.82 | 0.13 | -1.36 | 0.27 | 0.85 |


### Q3 spread across conditions (SD of the condition means; and the smallest / largest condition mean)

| conditions | barrel | quantity | mean | SD across conditions | min | max | |mean| / SD |
|---|---|---|---|---|---|---|---|
| ordinary (18) | orange | absolute body log(R/B) | 1.83 | 0.19 | 1.26 | 2.23 | 9.58 |
| ordinary (18) | orange | body - stripe log(R/B) | 3.17 | 0.99 | 1.25 | 4.64 | 3.20 |
| ordinary (18) | blue | absolute body log(R/B) | -1.41 | 0.91 | -2.47 | 0.16 | 1.55 |
| ordinary (18) | blue | body - stripe log(R/B) | -3.25 | 0.92 | -4.49 | -1.80 | 3.52 |
| ordinary (18) | orange | absolute body 2-D log-chroma (RMS distance from the mean vector) | 1.29 | 0.35 | nan | nan | 3.67 |
| ordinary (18) | blue | absolute body 2-D log-chroma (RMS distance from the mean vector) | 1.03 | 0.66 | nan | nan | 1.56 |
| ordinary (18) | orange | body - stripe 2-D log-chroma (RMS distance from the mean vector) | 2.25 | 0.81 | nan | nan | 2.79 |
| ordinary (18) | blue | body - stripe 2-D log-chroma (RMS distance from the mean vector) | 2.31 | 0.81 | nan | nan | 2.85 |
| ordinary + extreme (25) | orange | absolute body log(R/B) | 1.76 | 0.30 | 0.58 | 2.23 | 5.85 |
| ordinary + extreme (25) | orange | body - stripe log(R/B) | 2.78 | 1.06 | 1.25 | 4.64 | 2.63 |
| ordinary + extreme (25) | blue | absolute body log(R/B) | -1.09 | 0.94 | -2.47 | 0.16 | 1.16 |
| ordinary + extreme (25) | blue | body - stripe log(R/B) | -2.84 | 1.03 | -4.49 | -1.36 | 2.75 |
| ordinary + extreme (25) | orange | absolute body 2-D log-chroma (RMS distance from the mean vector) | 1.25 | 0.36 | nan | nan | 3.42 |
| ordinary + extreme (25) | blue | absolute body 2-D log-chroma (RMS distance from the mean vector) | 0.80 | 0.69 | nan | nan | 1.16 |
| ordinary + extreme (25) | orange | body - stripe 2-D log-chroma (RMS distance from the mean vector) | 1.97 | 0.84 | nan | nan | 2.33 |
| ordinary + extreme (25) | blue | body - stripe 2-D log-chroma (RMS distance from the mean vector) | 2.01 | 0.86 | nan | nan | 2.35 |
| all 28 | orange | absolute body log(R/B) | 1.65 | 0.43 | 0.50 | 2.23 | 3.87 |
| all 28 | orange | body - stripe log(R/B) | 2.56 | 1.18 | 0.48 | 4.64 | 2.16 |
| all 28 | blue | absolute body log(R/B) | -0.98 | 0.95 | -2.47 | 0.16 | 1.03 |
| all 28 | blue | body - stripe log(R/B) | -2.57 | 1.24 | -4.49 | -0.25 | 2.08 |
| all 28 | orange | absolute body 2-D log-chroma (RMS distance from the mean vector) | 1.17 | 0.41 | nan | nan | 2.84 |
| all 28 | blue | absolute body 2-D log-chroma (RMS distance from the mean vector) | 0.71 | 0.69 | nan | nan | 1.03 |
| all 28 | orange | body - stripe 2-D log-chroma (RMS distance from the mean vector) | 1.81 | 0.92 | nan | nan | 1.98 |
| all 28 | blue | body - stripe 2-D log-chroma (RMS distance from the mean vector) | 1.83 | 0.98 | nan | nan | 1.87 |


Box height against bottom row over the 360 barrels: h = 0.630 * y1 + -56.1; residual SD 1.7 px, relative 0.03; bottom rows 133..357

non-barrel triplets, mode row: 156600
non-barrel triplets, mode any: 156600

### Q3 ROC-like table: sandwich in log(R/B): upper-stripe and lower-stripe both beyond T with the same sign

| T | barrels pass % ordinary | extreme | brightness 1 | condition-colours under 95% (of 36 ordinary) | (of 14 extreme) | false triplets % (row-sized, not brightness 1) | in clutter frames | in negative frames | worst condition | any-size triplets |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 100.00 | 100.00 | 66.67 | 0 | 0 | 7.99 | 12.03 | 11.47 | 25.38 | 8.85 |
| 0.10 | 100.00 | 100.00 | 61.90 | 0 | 0 | 3.28 | 6.29 | 6.32 | 9.40 | 3.54 |
| 0.20 | 100.00 | 100.00 | 45.24 | 0 | 0 | 1.15 | 2.62 | 2.92 | 3.60 | 1.06 |
| 0.30 | 100.00 | 98.98 | 38.10 | 0 | 1 | 0.63 | 1.65 | 1.74 | 2.17 | 0.53 |
| 0.40 | 99.55 | 98.98 | 28.57 | 1 | 1 | 0.42 | 1.12 | 1.21 | 1.55 | 0.32 |
| 0.50 | 99.55 | 98.98 | 23.81 | 1 | 1 | 0.30 | 0.83 | 0.88 | 1.17 | 0.19 |
| 0.60 | 99.09 | 98.98 | 19.05 | 1 | 1 | 0.22 | 0.62 | 0.64 | 0.81 | 0.13 |
| 0.80 | 98.64 | 98.98 | 14.29 | 1 | 1 | 0.11 | 0.29 | 0.33 | 0.52 | 0.07 |
| 1.00 | 98.18 | 92.86 | 9.52 | 1 | 2 | 0.05 | 0.13 | 0.15 | 0.35 | 0.04 |
| 1.20 | 97.27 | 92.86 | 4.76 | 2 | 2 | 0.03 | 0.08 | 0.07 | 0.23 | 0.02 |
| 1.50 | 96.82 | 77.55 | 4.76 | 3 | 6 | 0.01 | 0.03 | 0.02 | 0.07 | 0.01 |
| 2.00 | 80.45 | 11.22 | 0.00 | 12 | 13 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |


### Q3 ROC-like table: body-minus-stripe log(R/B) alone (no sandwich requirement)

| T | barrels pass % ordinary | extreme | brightness 1 | condition-colours under 95% (of 36 ordinary) | (of 14 extreme) | false triplets % (row-sized, not brightness 1) | in clutter frames | in negative frames | worst condition | any-size triplets |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 100.00 | 100.00 | 71.43 | 0 | 0 | 20.93 | 27.71 | 26.81 | 46.90 | 21.64 |
| 0.10 | 100.00 | 100.00 | 69.05 | 0 | 0 | 9.71 | 15.40 | 16.11 | 20.43 | 10.07 |
| 0.20 | 100.00 | 100.00 | 61.90 | 0 | 0 | 3.95 | 7.52 | 8.91 | 9.79 | 3.73 |
| 0.30 | 100.00 | 100.00 | 54.76 | 0 | 0 | 2.37 | 5.13 | 5.61 | 6.43 | 2.05 |
| 0.40 | 100.00 | 100.00 | 47.62 | 0 | 0 | 1.55 | 3.60 | 3.80 | 4.40 | 1.32 |
| 0.50 | 100.00 | 98.98 | 42.86 | 0 | 1 | 1.09 | 2.65 | 2.68 | 3.43 | 0.87 |
| 0.60 | 100.00 | 98.98 | 40.48 | 0 | 1 | 0.76 | 1.85 | 1.97 | 2.50 | 0.57 |
| 0.80 | 100.00 | 98.98 | 26.19 | 0 | 1 | 0.34 | 0.76 | 0.94 | 1.31 | 0.25 |
| 1.00 | 100.00 | 98.98 | 21.43 | 0 | 1 | 0.14 | 0.23 | 0.45 | 1.04 | 0.12 |
| 1.20 | 99.09 | 94.90 | 16.67 | 1 | 2 | 0.07 | 0.11 | 0.23 | 0.69 | 0.06 |
| 1.50 | 96.82 | 86.73 | 4.76 | 3 | 4 | 0.03 | 0.04 | 0.09 | 0.42 | 0.02 |
| 2.00 | 83.64 | 22.45 | 0.00 | 10 | 13 | 0.01 | 0.00 | 0.02 | 0.10 | 0.00 |


### Q3 ROC-like table: sandwich + upper and lower agree (|log(R/B) upper - lower| <= 0.5)

| T | barrels pass % ordinary | extreme | brightness 1 | condition-colours under 95% (of 36 ordinary) | (of 14 extreme) | false triplets % (row-sized, not brightness 1) | in clutter frames | in negative frames | worst condition | any-size triplets |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 93.64 | 87.76 | 38.10 | 8 | 4 | 7.30 | 10.86 | 9.66 | 24.67 | 8.33 |
| 0.10 | 93.64 | 87.76 | 35.71 | 8 | 4 | 2.78 | 5.47 | 4.95 | 8.83 | 3.16 |
| 0.20 | 93.64 | 87.76 | 26.19 | 8 | 4 | 0.87 | 2.13 | 2.10 | 3.14 | 0.86 |
| 0.30 | 93.64 | 86.73 | 21.43 | 8 | 4 | 0.46 | 1.39 | 1.21 | 1.88 | 0.42 |
| 0.40 | 93.64 | 86.73 | 14.29 | 8 | 4 | 0.31 | 0.94 | 0.85 | 1.33 | 0.24 |
| 0.50 | 93.64 | 86.73 | 11.90 | 8 | 4 | 0.22 | 0.72 | 0.63 | 0.98 | 0.14 |
| 0.60 | 93.64 | 86.73 | 9.52 | 8 | 4 | 0.17 | 0.56 | 0.46 | 0.69 | 0.09 |
| 0.80 | 93.64 | 86.73 | 7.14 | 8 | 4 | 0.08 | 0.25 | 0.24 | 0.24 | 0.05 |
| 1.00 | 93.64 | 85.71 | 7.14 | 8 | 4 | 0.04 | 0.12 | 0.10 | 0.17 | 0.03 |
| 1.20 | 92.73 | 85.71 | 4.76 | 9 | 4 | 0.02 | 0.07 | 0.05 | 0.15 | 0.02 |
| 1.50 | 92.27 | 71.43 | 4.76 | 10 | 7 | 0.01 | 0.03 | 0.01 | 0.06 | 0.01 |
| 2.00 | 77.27 | 8.16 | 0.00 | 16 | 13 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |


### Q3 ROC-like table: sandwich + brightest patch mean channel >= 40 (the V gate)

| T | barrels pass % ordinary | extreme | brightness 1 | condition-colours under 95% (of 36 ordinary) | (of 14 extreme) | false triplets % (row-sized, not brightness 1) | in clutter frames | in negative frames | worst condition | any-size triplets |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 100.00 | 100.00 | 28.57 | 0 | 0 | 7.81 | 11.66 | 11.09 | 25.36 | 8.61 |
| 0.10 | 100.00 | 100.00 | 26.19 | 0 | 0 | 3.19 | 6.02 | 6.12 | 9.40 | 3.42 |
| 0.20 | 100.00 | 100.00 | 26.19 | 0 | 0 | 1.12 | 2.55 | 2.86 | 3.43 | 1.03 |
| 0.30 | 100.00 | 98.98 | 23.81 | 0 | 1 | 0.61 | 1.61 | 1.70 | 2.12 | 0.52 |
| 0.40 | 99.55 | 98.98 | 21.43 | 1 | 1 | 0.41 | 1.11 | 1.18 | 1.52 | 0.31 |
| 0.50 | 99.55 | 98.98 | 19.05 | 1 | 1 | 0.30 | 0.82 | 0.85 | 1.17 | 0.19 |
| 0.60 | 99.09 | 98.98 | 16.67 | 1 | 1 | 0.21 | 0.62 | 0.62 | 0.81 | 0.13 |
| 0.80 | 98.64 | 98.98 | 14.29 | 1 | 1 | 0.11 | 0.29 | 0.32 | 0.50 | 0.07 |
| 1.00 | 98.18 | 92.86 | 9.52 | 1 | 2 | 0.05 | 0.13 | 0.15 | 0.35 | 0.04 |
| 1.20 | 97.27 | 92.86 | 4.76 | 2 | 2 | 0.03 | 0.08 | 0.07 | 0.23 | 0.02 |
| 1.50 | 96.82 | 77.55 | 4.76 | 3 | 6 | 0.01 | 0.03 | 0.02 | 0.07 | 0.01 |
| 2.00 | 80.45 | 11.22 | 0.00 | 12 | 13 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |


### Q3 ROC-like table: sandwich in the opponent (R-B)/(R+G+B)

| T | barrels pass % ordinary | extreme | brightness 1 | condition-colours under 95% (of 36 ordinary) | (of 14 extreme) | false triplets % (row-sized, not brightness 1) | in clutter frames | in negative frames | worst condition | any-size triplets |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.02 | 100.00 | 100.00 | 66.67 | 0 | 0 | 4.81 | 8.90 | 8.76 | 14.76 | 4.85 |
| 0.05 | 100.00 | 100.00 | 50.00 | 0 | 0 | 1.45 | 3.25 | 3.71 | 4.52 | 1.26 |
| 0.10 | 100.00 | 98.98 | 38.10 | 0 | 1 | 0.56 | 1.59 | 1.58 | 2.00 | 0.44 |
| 0.15 | 99.55 | 98.98 | 26.19 | 1 | 1 | 0.31 | 0.90 | 0.87 | 1.19 | 0.20 |
| 0.20 | 99.09 | 98.98 | 19.05 | 1 | 1 | 0.18 | 0.56 | 0.51 | 0.62 | 0.11 |
| 0.30 | 98.64 | 93.88 | 11.90 | 1 | 2 | 0.06 | 0.21 | 0.16 | 0.33 | 0.04 |
| 0.40 | 96.82 | 87.76 | 4.76 | 3 | 4 | 0.01 | 0.06 | 0.04 | 0.10 | 0.02 |
| 0.50 | 91.36 | 38.78 | 2.38 | 7 | 11 | 0.00 | 0.00 | 0.02 | 0.02 | 0.01 |


### Q3 ROC-like table: for contrast: ABSOLUTE body log(R/B) beyond T with the right sign (no stripe)

| T | barrels pass % ordinary | extreme | brightness 1 | condition-colours under 95% (of 36 ordinary) | (of 14 extreme) | false triplets % (row-sized, not brightness 1) | in clutter frames | in negative frames | worst condition | any-size triplets |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 96.36 | 85.71 | 40.48 | 2 | 3 | 72.65 | 70.88 | 73.32 | 100.00 | 73.14 |
| 0.10 | 95.00 | 76.53 | 35.71 | 3 | 4 | 61.92 | 65.12 | 60.88 | 100.00 | 63.26 |
| 0.20 | 92.27 | 67.35 | 35.71 | 4 | 6 | 50.76 | 55.78 | 48.40 | 100.00 | 52.07 |
| 0.30 | 89.55 | 61.22 | 33.33 | 5 | 6 | 43.32 | 47.94 | 38.47 | 99.87 | 43.74 |
| 0.40 | 88.64 | 57.14 | 33.33 | 5 | 7 | 38.30 | 40.99 | 33.13 | 99.50 | 38.20 |
| 0.50 | 87.27 | 55.10 | 30.95 | 5 | 7 | 35.78 | 38.21 | 30.25 | 99.17 | 35.73 |
| 0.60 | 87.27 | 52.04 | 30.95 | 5 | 7 | 33.80 | 36.58 | 27.75 | 98.88 | 33.72 |
| 0.80 | 85.00 | 39.80 | 19.05 | 6 | 8 | 28.24 | 29.20 | 23.35 | 98.62 | 27.88 |
| 1.00 | 84.55 | 38.78 | 14.29 | 7 | 8 | 18.41 | 18.11 | 14.99 | 98.36 | 18.63 |
| 1.20 | 82.27 | 36.73 | 9.52 | 10 | 8 | 12.67 | 13.39 | 10.44 | 98.00 | 12.85 |
| 1.50 | 76.36 | 34.69 | 0.00 | 11 | 9 | 7.46 | 7.71 | 7.04 | 73.70 | 7.52 |
| 2.00 | 29.09 | 0.00 | 0.00 | 28 | 14 | 0.03 | 0.17 | 0.08 | 0.29 | 0.01 |


### Q3 distribution of upper-vs-lower disagreement |log(R/B)| on barrels (percentiles 50/90/95/99/max)

- ordinary: 0.12 / 0.41 / 0.66 / 1.21 / 1.46
- extreme: 0.17 / 0.52 / 0.59 / 0.82 / 0.85
- excluded: 0.01 / 1.17 / 1.33 / 1.45 / 1.49

### Q3 barrels failing the sandwich at T = 0.3 and at T = 0.5

34 barrels under 0.5; by group: {'ordinary': 1, 'extreme': 1, 'excluded': 32}; under 0.3: {'ordinary': 0, 'extreme': 1, 'excluded': 26}
| frame | colour | h | sandwich | body-stripe | upper-lower | body RGB | stripe RGB | clip % | dark % |
|---|---|---|---|---|---|---|---|---|---|
| 4A8B_lampmid3_ottoman_core_01 | orange | 64 | 0.37 | 1.08 | 1.36 | [33.0, 22.0, 13.0] | [13.0, 14.0, 14.0] | 0.00 | 63.40 |
| 4A8B_window_black_clutter_02 | orange | 32 | 0.23 | 0.40 | 0.37 | [250.0, 250.0, 196.0] | [201.0, 241.0, 247.0] | 82.81 | 0.00 |

**Verdict on C: the invariance is refuted; a signed threshold holds.** The body-minus-stripe difference is not constant: for orange barrels its condition mean runs from 1.25 (ottoman, lamp brightness 3) through 1.8-2.4 (warm and mid lamp on tile and ottoman) to 4.0-4.6 (daylight), SD 0.99 over the ordinary conditions, while the absolute orange body it would replace has SD 0.19. For blue barrels difference and absolute value are equally unstable (SD 0.92 and 0.91). The difference shrinks because the blue paint loses its colour under the lamp while the orange keeps it; a gain common to both paints would have cancelled, and this does not.

What survives is the order. One fixed threshold with the right sign per colour holds for at least 95% of barrels in every ordinary condition up to T = 0.3 (all 220 ordinary barrels pass; at 0.4 one of five orange barrels of `lampmid3_ottoman` fails), and in every ordinary and extreme condition up to T = 0.2 (all 318). At T = 0.3, 0.63% of row-sized random non-barrel triplets pass (1.65% in clutter frames, 1.74% in negative frames, 2.17% in the worst condition); at T = 1.0, 0.05% pass with 98.2% of ordinary and 92.9% of extreme barrels. Requiring both sides (the sandwich) rather than the body-stripe difference alone cuts false triplets about fourfold at the same T (0.63% against 2.37% at 0.3). An absolute threshold on the body cannot do this: the blue body's log(R/B) changes sign under the warm lamp (+0.16 on the tile), and no threshold keeps every condition.

Where it breaks: very dark barrels (`lampmid3_ottoman` orange, body RGB 33/22/13, 63% of body pixels under 40: score 0.37), clipped glare (`window_black_clutter_02` orange, body 250/250/196, 83% clipped: 0.23), and lamp brightness 1, where 38-45% pass at 0.2-0.3. Adding "upper and lower agree within 0.5" costs 6% of ordinary barrels (the 95th percentile of their disagreement is 0.66) and is not worth it. These rates are per random triplet, not per frame: a search over thousands of positions per frame would meet many passing triplets at T = 0.3, so the test is a strong cue, not a detector.

## Q4. One translation in log-chromaticity (von Kries), against hue and S

Per condition, the mean log-chromaticity of the orange bodies and of the blue bodies, minus the same at home; the best single translation is the mean of the two shifts, and the residual is what it leaves. "Share explained" = 1 - residual^2 / shift^2.

### Q4 translation fit, 2 classes (orange body, blue body): patch-mean colours, camera values as they are (primary)

| condition | grp | orange d logR/G | orange d logB/G | blue d logR/G | blue d logB/G | t logR/G | t logB/G | RMS shift before | RMS residual after | share explained | d log brightness (common) | brightness resid |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| campus_light | ord | -0.15 | 0.04 | 0.41 | -0.32 | 0.13 | -0.14 | 0.39 | 0.33 | 0.25 | -0.10 | 0.02 |
| window_abpwhite | ord | -0.05 | 0.09 | 0.01 | -0.15 | -0.02 | -0.03 | 0.13 | 0.12 | 0.06 | 0.21 | 0.13 |
| both_abpgray | ord | 0.85 | 0.54 | 0.12 | 0.24 | 0.49 | 0.39 | 0.74 | 0.40 | 0.71 | -0.11 | 0.05 |
| overheaddim_palewood | ord | 0.04 | 0.08 | 0.26 | -0.12 | 0.15 | -0.02 | 0.21 | 0.15 | 0.51 | 0.08 | 0.06 |
| window_glass | ord | -0.05 | 0.16 | 0.00 | -0.03 | -0.02 | 0.06 | 0.12 | 0.10 | 0.31 | 0.06 | 0.08 |
| lampcool6_glass | ord | -0.12 | 0.12 | 0.03 | -0.08 | -0.04 | 0.02 | 0.13 | 0.12 | 0.12 | -0.01 | 0.06 |
| lampmid6_glass | ord | -0.05 | -0.02 | 0.11 | -0.09 | 0.03 | -0.06 | 0.11 | 0.09 | 0.34 | -0.02 | 0.04 |
| lampwarm6_glass | ord | -0.02 | -0.04 | 0.37 | -0.11 | 0.18 | -0.07 | 0.28 | 0.20 | 0.48 | -0.01 | 0.03 |
| lampmid3_glass | ord | -0.06 | 0.11 | 0.02 | -0.07 | -0.02 | 0.02 | 0.10 | 0.10 | 0.07 | 0.01 | 0.06 |
| lampcool6_bathtile | ord | -0.19 | -0.18 | 0.45 | -0.58 | 0.13 | -0.38 | 0.55 | 0.38 | 0.53 | -0.21 | 0.12 |
| lampmid6_bathtile | ord | -0.11 | -0.16 | 1.19 | -0.85 | 0.54 | -0.51 | 1.05 | 0.74 | 0.50 | -0.11 | 0.14 |
| lampwarm6_bathtile | ord | -0.03 | -0.10 | 1.45 | -1.08 | 0.71 | -0.59 | 1.28 | 0.89 | 0.52 | -0.16 | 0.20 |
| lampmid3_bathtile | ord | -0.21 | -0.16 | 1.35 | -0.88 | 0.57 | -0.52 | 1.16 | 0.86 | 0.45 | -0.19 | 0.19 |
| lampcool6_ottoman | ord | -0.53 | -0.25 | 0.55 | -0.47 | 0.01 | -0.36 | 0.66 | 0.55 | 0.30 | -0.23 | 0.07 |
| lampmid6_ottoman | ord | -0.45 | -0.33 | 1.08 | -0.62 | 0.32 | -0.47 | 0.96 | 0.78 | 0.35 | -0.20 | 0.01 |
| lampwarm6_ottoman | ord | -0.42 | -0.31 | 1.33 | -0.84 | 0.45 | -0.57 | 1.17 | 0.91 | 0.39 | -0.30 | 0.07 |
| lampmid3_ottoman | ord | -0.56 | 0.22 | 1.39 | -0.85 | 0.42 | -0.32 | 1.23 | 1.11 | 0.18 | -1.25 | 0.04 |
| lampcool6_wood | ext | -0.30 | -0.22 | 1.16 | -0.72 | 0.43 | -0.47 | 1.00 | 0.77 | 0.41 | 0.06 | 0.06 |
| lampmid6_wood | ext | -0.21 | -0.15 | 1.38 | -0.84 | 0.59 | -0.49 | 1.16 | 0.87 | 0.44 | 0.07 | 0.08 |
| lampwarm6_wood | ext | -0.15 | -0.14 | 1.47 | -0.98 | 0.66 | -0.56 | 1.26 | 0.91 | 0.47 | 0.04 | 0.11 |
| lampcool3_wood | ext | -0.40 | -0.15 | 1.31 | -0.81 | 0.45 | -0.48 | 1.13 | 0.92 | 0.34 | -0.21 | 0.07 |
| lampmid3_wood | ext | -0.42 | 0.02 | 1.39 | -0.86 | 0.49 | -0.42 | 1.19 | 1.00 | 0.29 | -0.07 | 0.06 |
| lampwarm3_wood | ext | -0.39 | -0.14 | 1.42 | -0.93 | 0.52 | -0.53 | 1.24 | 0.99 | 0.36 | -0.10 | 0.09 |
| lampcool1_wood | exc | -0.81 | 0.69 | 1.44 | -0.91 | 0.31 | -0.11 | 1.42 | 1.38 | 0.05 | -1.91 | 0.46 |
| lampmid1_wood | exc | -0.66 | 0.62 | 1.44 | -0.90 | 0.39 | -0.14 | 1.36 | 1.30 | 0.09 | -1.90 | 0.50 |
| lampwarm1_wood | exc | -0.60 | 0.40 | 1.45 | -0.90 | 0.42 | -0.25 | 1.31 | 1.21 | 0.14 | -1.79 | 0.50 |
| window_black | ext | -0.89 | 0.43 | 0.77 | -0.71 | -0.06 | -0.14 | 1.02 | 1.00 | 0.02 | 0.85 | 0.06 |

- ordinary: RMS shift before 0.748, RMS residual after one translation 0.573, share of squared shift explained 41%
- extreme: RMS shift before 1.144, RMS residual after one translation 0.926, share of squared shift explained 34%
- excluded (brightness 1): RMS shift before 1.365, RMS residual after one translation 1.299, share of squared shift explained 9%
- all: RMS shift before 0.948, RMS residual after one translation 0.786, share of squared shift explained 31%

4 classes (bodies and stripes of both paints), one translation:
- ordinary: RMS shift before 0.725, after 0.562, explained 40%
- extreme: RMS shift before 1.086, after 0.903, explained 31%
- excluded (brightness 1): RMS shift before 1.352, after 1.321, explained 5%
- all: RMS shift before 0.916, after 0.777, explained 28%

Per paint (body and stripe of the SAME paint averaged), residual by paint: orange-paint shift minus blue-paint shift (log R/G, log B/G):
| condition | grp | orange-blue d logR/G | orange-blue d logB/G | orange body-vs-stripe drift logR/G | blue body-vs-stripe drift logB/G |
|---|---|---|---|---|---|
| campus_light | ord | -0.57 | 0.44 | 0.03 | -0.02 |
| window_abpwhite | ord | -0.03 | 0.24 | 0.14 | -0.13 |
| both_abpgray | ord | 0.95 | 0.56 | -0.16 | 0.04 |
| overheaddim_palewood | ord | -0.10 | 0.20 | 0.08 | -0.06 |
| window_glass | ord | 0.04 | 0.24 | 0.01 | -0.08 |
| lampcool6_glass | ord | 0.02 | 0.21 | 0.00 | -0.03 |
| lampmid6_glass | ord | -0.01 | 0.08 | -0.01 | -0.02 |
| lampwarm6_glass | ord | -0.23 | 0.07 | 0.00 | -0.01 |
| lampmid3_glass | ord | 0.05 | 0.18 | -0.01 | -0.05 |
| lampcool6_bathtile | ord | -0.58 | 0.42 | 0.03 | -0.00 |
| lampmid6_bathtile | ord | -1.22 | 0.74 | 0.01 | -0.07 |
| lampwarm6_bathtile | ord | -1.37 | 1.00 | -0.00 | -0.05 |
| lampmid3_bathtile | ord | -1.45 | 0.74 | 0.00 | -0.03 |
| lampcool6_ottoman | ord | -1.03 | 0.22 | 0.07 | 0.01 |
| lampmid6_ottoman | ord | -1.46 | 0.32 | 0.09 | -0.01 |
| lampwarm6_ottoman | ord | -1.69 | 0.56 | 0.08 | 0.02 |
| lampmid3_ottoman | ord | -1.78 | 0.94 | -0.14 | 0.01 |
| lampcool6_wood | ext | -1.39 | 0.54 | 0.04 | -0.06 |
| lampmid6_wood | ext | -1.51 | 0.73 | 0.04 | -0.04 |
| lampwarm6_wood | ext | -1.54 | 0.84 | 0.04 | -0.06 |
| lampcool3_wood | ext | -1.61 | 0.73 | 0.03 | -0.03 |
| lampmid3_wood | ext | -1.72 | 0.91 | 0.05 | -0.04 |
| lampwarm3_wood | ext | -1.72 | 0.83 | 0.05 | -0.03 |
| lampcool1_wood | exc | -2.18 | 1.68 | 0.11 | -0.04 |
| lampmid1_wood | exc | -2.10 | 1.59 | 0.25 | -0.04 |
| lampwarm1_wood | exc | -2.02 | 1.44 | 0.20 | -0.02 |
| window_black | ext | -1.60 | 1.17 | 0.05 | -0.07 |


### Q4 translation fit, 2 classes (orange body, blue body): pixel medians over unclipped (all channels < 250), not-dark (max >= 40) pixels

| condition | grp | orange d logR/G | orange d logB/G | blue d logR/G | blue d logB/G | t logR/G | t logB/G | RMS shift before | RMS residual after | share explained | d log brightness (common) | brightness resid |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| campus_light | ord | -0.18 | 0.00 | 0.24 | -0.39 | 0.03 | -0.19 | 0.35 | 0.28 | 0.32 | -0.11 | 0.03 |
| window_abpwhite | ord | -0.10 | 0.01 | -0.04 | -0.19 | -0.07 | -0.09 | 0.16 | 0.11 | 0.52 | 0.27 | 0.18 |
| both_abpgray | ord | 1.01 | 0.64 | 0.16 | 0.25 | 0.58 | 0.44 | 0.87 | 0.46 | 0.71 | -0.11 | 0.09 |
| overheaddim_palewood | ord | -0.03 | 0.13 | 0.13 | -0.18 | 0.05 | -0.02 | 0.18 | 0.17 | 0.10 | 0.12 | 0.04 |
| window_glass | ord | -0.09 | 0.13 | -0.01 | -0.08 | -0.05 | 0.03 | 0.13 | 0.11 | 0.20 | 0.13 | 0.08 |
| lampcool6_glass | ord | -0.19 | 0.15 | 0.01 | -0.12 | -0.09 | 0.01 | 0.19 | 0.17 | 0.22 | 0.07 | 0.06 |
| lampmid6_glass | ord | -0.12 | -0.02 | 0.03 | -0.14 | -0.05 | -0.08 | 0.13 | 0.10 | 0.48 | 0.06 | 0.04 |
| lampwarm6_glass | ord | -0.09 | -0.07 | 0.24 | -0.12 | 0.07 | -0.10 | 0.20 | 0.16 | 0.35 | 0.06 | 0.03 |
| lampmid3_glass | ord | -0.14 | 0.12 | 0.01 | -0.10 | -0.06 | 0.01 | 0.15 | 0.13 | 0.19 | 0.09 | 0.05 |
| lampcool6_bathtile | ord | -0.27 | -0.19 | 0.40 | -0.63 | 0.06 | -0.41 | 0.58 | 0.40 | 0.52 | -0.15 | 0.14 |
| lampmid6_bathtile | ord | -0.19 | -0.14 | 1.21 | -0.93 | 0.51 | -0.54 | 1.09 | 0.80 | 0.46 | -0.05 | 0.14 |
| lampwarm6_bathtile | ord | -0.13 | -0.10 | 1.47 | -1.13 | 0.67 | -0.62 | 1.32 | 0.95 | 0.48 | -0.09 | 0.20 |
| lampmid3_bathtile | ord | -0.30 | -0.16 | 1.35 | -0.93 | 0.52 | -0.54 | 1.18 | 0.91 | 0.41 | -0.12 | 0.19 |
| lampcool6_ottoman | ord | -0.61 | -0.30 | 0.53 | -0.48 | -0.04 | -0.39 | 0.70 | 0.58 | 0.32 | -0.11 | 0.08 |
| lampmid6_ottoman | ord | -0.53 | -0.35 | 1.05 | -0.66 | 0.26 | -0.51 | 0.99 | 0.81 | 0.33 | -0.06 | 0.01 |
| lampwarm6_ottoman | ord | -0.49 | -0.30 | 1.30 | -0.87 | 0.40 | -0.59 | 1.18 | 0.94 | 0.36 | -0.11 | 0.02 |
| lampmid3_ottoman | ord | -0.51 | -0.20 | 1.10 | -0.61 | 0.30 | -0.41 | 0.98 | 0.83 | 0.27 | -0.79 | 0.17 |
| lampcool6_wood | ext | -0.42 | -0.20 | 1.25 | -0.85 | 0.42 | -0.53 | 1.12 | 0.90 | 0.36 | 0.04 | 0.08 |
| lampmid6_wood | ext | -0.34 | -0.15 | 1.42 | -0.95 | 0.54 | -0.55 | 1.23 | 0.96 | 0.39 | 0.08 | 0.08 |
| lampwarm6_wood | ext | -0.26 | -0.12 | 1.51 | -1.03 | 0.62 | -0.58 | 1.31 | 0.99 | 0.42 | 0.06 | 0.11 |
| lampcool3_wood | ext | -0.52 | -0.14 | 1.33 | -0.90 | 0.41 | -0.52 | 1.20 | 1.00 | 0.30 | -0.16 | 0.06 |
| lampmid3_wood | ext | -0.52 | 0.00 | 1.41 | -0.97 | 0.44 | -0.48 | 1.26 | 1.08 | 0.27 | -0.05 | 0.08 |
| lampwarm3_wood | ext | -0.48 | -0.13 | 1.44 | -0.97 | 0.48 | -0.55 | 1.27 | 1.05 | 0.33 | -0.09 | 0.09 |
| lampcool1_wood | exc | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| lampmid1_wood | exc | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| lampwarm1_wood | exc | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| window_black | ext | -0.91 | 0.32 | 0.64 | -0.77 | -0.14 | -0.23 | 0.98 | 0.94 | 0.07 | 0.89 | 0.08 |

- ordinary: RMS shift before 0.749, RMS residual after one translation 0.571, share of squared shift explained 42%
- extreme: RMS shift before 1.201, RMS residual after one translation 0.990, share of squared shift explained 32%
- excluded (brightness 1): RMS shift before nan, RMS residual after one translation nan, share of squared shift explained nan%
- all: RMS shift before 0.904, RMS residual after one translation 0.719, share of squared shift explained 37%

### Q4 translation fit, 2 classes (orange body, blue body): patch means after undoing the sRGB curve

- ordinary: RMS shift before 1.251, RMS residual after one translation 0.953, share of squared shift explained 42%
- extreme: RMS shift before 1.879, RMS residual after one translation 1.464, share of squared shift explained 39%
- excluded (brightness 1): RMS shift before 2.400, RMS residual after one translation 2.358, share of squared shift explained 4%
- all: RMS shift before 1.594, RMS residual after one translation 1.321, share of squared shift explained 31%

### Q4 the same shift described in OpenCV hue / S (median over pooled body pixels)

home: orange hue 7 S 223; blue hue 111 S 233

| condition | grp | orange hue | orange S | blue hue | blue S | d hue orange | d hue blue | d S orange | d S blue | log S ratio orange | log S ratio blue |
|---|---|---|---|---|---|---|---|---|---|---|---|
| campus_light | ord | 8.0 | 217.0 | 106.0 | 214.0 | 1.0 | -5.0 | -6.0 | -19.0 | -0.0 | -0.1 |
| window_abpwhite | ord | 7.0 | 220.0 | 108.0 | 230.0 | 0.0 | -3.0 | -3.0 | -3.0 | -0.0 | -0.0 |
| both_abpgray | ord | 1.0 | 232.0 | 113.0 | 237.0 | -6.0 | 2.0 | 9.0 | 4.0 | 0.0 | 0.0 |
| overheaddim_palewood | ord | 6.0 | 221.0 | 109.0 | 226.0 | -1.0 | -2.0 | -2.0 | -7.0 | -0.0 | -0.0 |
| window_glass | ord | 7.0 | 213.0 | 110.0 | 232.0 | 0.0 | -1.0 | -10.0 | -1.0 | -0.0 | -0.0 |
| lampcool6_glass | ord | 7.0 | 210.0 | 109.0 | 231.0 | 0.0 | -2.0 | -13.0 | -2.0 | -0.1 | -0.0 |
| lampmid6_glass | ord | 7.0 | 220.0 | 109.0 | 230.0 | 0.0 | -2.0 | -3.0 | -3.0 | -0.0 | -0.0 |
| lampwarm6_glass | ord | 7.0 | 223.0 | 110.0 | 225.0 | 0.0 | -1.0 | 0.0 | -8.0 | 0.0 | -0.0 |
| lampmid3_glass | ord | 7.0 | 214.0 | 109.0 | 231.0 | 0.0 | -2.0 | -9.0 | -2.0 | -0.0 | -0.0 |
| lampcool6_bathtile | ord | 10.0 | 219.0 | 102.0 | 192.0 | 3.0 | -9.0 | -4.0 | -41.0 | -0.0 | -0.2 |
| lampmid6_bathtile | ord | 9.0 | 221.0 | 96.0 | 57.0 | 2.0 | -15.0 | -2.0 | -176.0 | -0.0 | -1.4 |
| lampwarm6_bathtile | ord | 8.0 | 222.0 | 26.0 | 50.0 | 1.0 | -85.0 | -1.0 | -183.0 | -0.0 | -1.5 |
| lampmid3_bathtile | ord | 10.0 | 218.0 | 96.0 | 31.0 | 3.0 | -15.0 | -5.0 | -202.0 | -0.0 | -2.0 |
| lampcool6_ottoman | ord | 15.0 | 211.0 | 105.0 | 192.0 | 8.0 | -6.0 | -12.0 | -41.0 | -0.1 | -0.2 |
| lampmid6_ottoman | ord | 14.0 | 215.0 | 106.0 | 126.0 | 7.0 | -5.0 | -8.0 | -107.0 | -0.0 | -0.6 |
| lampwarm6_ottoman | ord | 13.0 | 214.0 | 102.0 | 45.0 | 6.0 | -9.0 | -9.0 | -188.0 | -0.0 | -1.6 |
| lampmid3_ottoman | ord | 13.0 | 205.0 | 0.0 | 0.0 | 6.0 | -111.0 | -18.0 | -233.0 | -0.1 | -5.5 |
| lampcool6_wood | ext | 12.0 | 216.0 | 103.0 | 64.0 | 5.0 | -8.0 | -7.0 | -169.0 | -0.0 | -1.3 |
| lampmid6_wood | ext | 10.0 | 217.0 | 101.0 | 30.0 | 3.0 | -10.0 | -6.0 | -203.0 | -0.0 | -2.0 |
| lampwarm6_wood | ext | 9.0 | 219.0 | 14.0 | 33.0 | 2.0 | -97.0 | -4.0 | -200.0 | -0.0 | -2.0 |
| lampcool3_wood | ext | 13.0 | 209.0 | 103.0 | 37.0 | 6.0 | -8.0 | -14.0 | -196.0 | -0.1 | -1.8 |
| lampmid3_wood | ext | 12.0 | 200.0 | 83.0 | 21.0 | 5.0 | -28.0 | -23.0 | -212.0 | -0.1 | -2.4 |
| lampwarm3_wood | ext | 12.0 | 209.0 | 24.0 | 19.0 | 5.0 | -87.0 | -14.0 | -214.0 | -0.1 | -2.5 |
| lampcool1_wood | exc | 0.0 | 0.0 | 0.0 | 0.0 | -7.0 | -111.0 | -223.0 | -233.0 | -5.4 | -5.5 |
| lampmid1_wood | exc | 0.0 | 0.0 | 0.0 | 0.0 | -7.0 | -111.0 | -223.0 | -233.0 | -5.4 | -5.5 |
| lampwarm1_wood | exc | 9.0 | 71.0 | 0.0 | 0.0 | 2.0 | -111.0 | -152.0 | -233.0 | -1.1 | -5.5 |
| window_black | ext | 19.0 | 134.0 | 98.0 | 161.0 | 12.0 | -13.0 | -89.0 | -72.0 | -0.5 | -0.4 |


### Regularity: does ONE number per axis (the same for both classes) describe the shift?

| conditions | axis | n | corr(orange shift, blue shift) | slope blue on orange | share explained by a common shift % | same sign % | RMS shift orange | RMS shift blue |
|---|---|---|---|---|---|---|---|---|
| ordinary | hue | 17 | -0.30 | -2.73 | 45.10 | 5.88 | 3.80 | 34.53 |
| ordinary | S (additive) | 17 | 0.27 | 3.85 | 54.34 | 94.12 | 8.22 | 111.20 |
| ordinary | S (ratio, log) | 17 | 0.46 | 22.60 | 51.53 | 94.12 | 0.04 | 1.56 |
| ordinary | log R/G | 17 | -0.48 | -0.87 | 29.73 | 11.76 | 0.33 | 0.81 |
| ordinary | log B/G | 17 | 0.64 | 1.15 | 66.12 | 58.82 | 0.21 | 0.56 |
| extreme | hue | 7 | 0.43 | 5.18 | 44.34 | 0.00 | 6.19 | 50.93 |
| extreme | S (additive) | 7 | -0.90 | -1.51 | 57.99 | 100.00 | 35.74 | 186.74 |
| extreme | S (ratio, log) | 7 | -0.77 | -3.25 | 53.38 | 100.00 | 0.20 | 1.90 |
| extreme | log R/G | 7 | 0.87 | 0.88 | 25.55 | 0.00 | 0.45 | 1.29 |
| extreme | log B/G | 7 | 0.44 | 0.19 | 56.73 | 71.43 | 0.21 | 0.84 |
| excluded (brightness 1) | hue | 3 | nan | -0.00 | 53.59 | 66.67 | 5.83 | 111.00 |
| excluded (brightness 1) | S (additive) | 3 | nan | 0.00 | 98.82 | 100.00 | 202.12 | 233.00 |
| excluded (brightness 1) | S (ratio, log) | 3 | nan | -0.00 | 93.77 | 100.00 | 4.46 | 5.45 |
| excluded (brightness 1) | log R/G | 3 | 0.99 | 0.05 | 11.14 | 0.00 | 0.70 | 1.44 |
| excluded (brightness 1) | log B/G | 3 | -0.72 | -0.04 | 5.44 | 0.00 | 0.58 | 0.91 |
| all | hue | 27 | 0.22 | 2.12 | 49.06 | 11.11 | 4.78 | 52.84 |
| all | S (additive) | 27 | 0.43 | 0.65 | 72.50 | 96.30 | 70.09 | 151.19 |
| all | S (ratio, log) | 27 | 0.66 | 0.86 | 80.90 | 96.30 | 1.49 | 2.40 |
| all | log R/G | 27 | -0.55 | -0.96 | 23.87 | 7.41 | 0.42 | 1.04 |
| all | log B/G | 27 | 0.16 | 0.21 | 48.48 | 55.56 | 0.28 | 0.68 |

### Q4b does a fixed floor (subtracted from every channel before the logs) rescue the common translation?

| floor subtracted | ordinary: share explained % | extreme: share explained % |
|---|---|---|
| 0 | 41 | 34 |
| 4 | 42 | 34 |
| 8 | 42 | 35 |
| 12 | 45 | 38 |
| 16 | 47 | 37 |
| 20 | 48 | 33 |


### Q4b the weak channel of each paint (mean of patch means): orange B and blue R per condition, with the strong channel

| condition | grp | orange R | orange G | orange B | blue R | blue G | blue B |
|---|---|---|---|---|---|---|---|
| window_light | ord | 175 | 61 | 25 | 12 | 56 | 138 |
| campus_light | ord | 157 | 66 | 27 | 23 | 61 | 108 |
| window_abpwhite | ord | 185 | 68 | 31 | 20 | 87 | 185 |
| both_abpgray | ord | 196 | 29 | 20 | 10 | 40 | 127 |
| overheaddim_palewood | ord | 203 | 68 | 30 | 18 | 60 | 132 |
| window_glass | ord | 166 | 61 | 29 | 15 | 65 | 157 |
| lampcool6_glass | ord | 156 | 60 | 28 | 14 | 61 | 141 |
| lampmid6_glass | ord | 163 | 60 | 23 | 15 | 59 | 134 |
| lampwarm6_glass | ord | 167 | 59 | 23 | 20 | 58 | 132 |
| lampmid3_glass | ord | 162 | 59 | 27 | 14 | 61 | 144 |
| lampcool6_bathtile | ord | 153 | 64 | 21 | 19 | 53 | 74 |
| lampmid6_bathtile | ord | 176 | 68 | 23 | 43 | 56 | 59 |
| lampwarm6_bathtile | ord | 182 | 65 | 23 | 50 | 50 | 42 |
| lampmid3_bathtile | ord | 164 | 70 | 24 | 43 | 48 | 49 |
| lampcool6_ottoman | ord | 109 | 64 | 20 | 24 | 60 | 93 |
| lampmid6_ottoman | ord | 125 | 68 | 19 | 39 | 56 | 76 |
| lampwarm6_ottoman | ord | 123 | 65 | 19 | 43 | 48 | 52 |
| lampmid3_ottoman | ord | 40 | 24 | 12 | 17 | 18 | 19 |
| lampcool6_wood | ext | 180 | 85 | 27 | 52 | 69 | 84 |
| lampmid6_wood | ext | 190 | 81 | 28 | 63 | 68 | 73 |
| lampwarm6_wood | ext | 195 | 79 | 28 | 66 | 64 | 60 |
| lampcool3_wood | ext | 134 | 70 | 24 | 45 | 52 | 58 |
| lampmid3_wood | ext | 149 | 78 | 32 | 56 | 60 | 64 |
| lampwarm3_wood | ext | 151 | 78 | 27 | 56 | 57 | 57 |
| lampcool1_wood | exc | 25 | 19 | 15 | 7 | 7 | 7 |
| lampmid1_wood | exc | 29 | 19 | 14 | 7 | 7 | 7 |
| lampwarm1_wood | exc | 35 | 21 | 13 | 8 | 8 | 8 |
| window_black | ext | 243 | 207 | 132 | 96 | 189 | 229 |

**Verdict: one translation does not describe the shift, and neither does one hue/S movement.** A single translation removes 41% of the squared shift in the ordinary conditions (RMS 0.75 before, 0.57 after), 34% in the extreme ones, 9% at brightness 1. Restricting to unclipped, not-dark pixels gives 42%; undoing the sRGB curve first gives 42%; subtracting a fixed floor of up to 20 counts first gives at most 48%; using bodies and stripes of both paints as four classes gives 40%. The reason is in the table: the two paints move differently. Orange log R/G falls by up to 0.56 while blue log R/G rises by up to 1.45; the signs are opposite in 15 of 17 ordinary conditions and the two shifts are negatively correlated (-0.48). Log B/G is more regular (66% explained, correlation +0.64). A common brightness scale does fit (residual at most 0.2 log units).

In hue/S terms the shift is no more regular: a common hue shift explains 45% (orange moves up 0-8 units, or down 6 on the gray table; blue moves down 1-15; the same direction in 1 of 17), a common S shift 54% (same direction in 16 of 17, but blue moves 13 times as far: RMS 111 against 8). **Neither description is a single simple movement; the regular statement is per class.** Orange stays close to home in every ordinary condition (hue 1-15, S 205-232) and its only large departures are the ottoman (hue +6 to +8) and the gray table (hue -6, where G falls to 22). Blue keeps its hue and S under daylight and on the glass table, and under the mid and warm lamp without daylight its S falls from 233 to 31-57 on the tile and to 45-126 on the ottoman, with R, G and B nearly equal at the low end (49/49/40 on the tile under the warm lamp), at which point its hue is undefined (26 on the tile; 14 and 24 on the wood desk). The weak channel of each paint does not scale with the strong one (medians, Q1 tables): orange B stays 18-27 while orange R runs 114-197 (leaving out the ottoman at brightness 3: R 46, B 11); blue R is 8-19 under daylight and on the glass table and 37-61 under the mid and warm lamp elsewhere, where blue B is 40-80 (129 at home). With two paints I cannot fit or test a richer model (three gains plus three offsets is exactly determined by two colours).

## Q5. Can the shift be read from the frame without knowing where the barrels are?

Targets: the shift of each paint's pixel cluster from home (median log-chromaticity of the patch pixels with V >= 40), and their mean (the common translation). 25 conditions (brightness 1 left out), 10 places. Each statistic is computed on whole frames as a detector would (barrels included where the region contains them) and averaged over a condition's frames. Two predictors: a line fitted on the other places (leave one place out), and the parameter-free "statistic minus its home value". The nested version chooses the statistic inside each fold from the other places only, then predicts every frame of the held-out place from that frame alone.

### Q5 the targets: per-condition shift of the paint clusters from home, in log-chroma (pixel medians, V >= 40)

| condition | grp | place | orange d logR/G | orange d logB/G | blue d logR/G | blue d logB/G | common t logR/G | common t logB/G | |orange - blue| / 2 (what a common t cannot reach) |
|---|---|---|---|---|---|---|---|---|---|
| window_light | ord | home_white | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| campus_light | ord | campus_study | -0.18 | 0.02 | 0.34 | -0.40 | 0.08 | -0.19 | 0.33 |
| window_abpwhite | ord | abp_white | -0.20 | 0.04 | -0.05 | -0.18 | -0.13 | -0.07 | 0.13 |
| both_abpgray | ord | abp_gray | 1.05 | 0.72 | 0.12 | 0.18 | 0.59 | 0.45 | 0.54 |
| overheaddim_palewood | ord | uc_palewood | -0.03 | 0.12 | 0.09 | -0.14 | 0.03 | -0.01 | 0.14 |
| window_glass | ord | home_glass | -0.08 | 0.15 | -0.03 | -0.07 | -0.05 | 0.04 | 0.11 |
| lampcool6_glass | ord | home_glass | -0.17 | 0.15 | -0.03 | -0.12 | -0.10 | 0.01 | 0.15 |
| lampmid6_glass | ord | home_glass | -0.10 | -0.02 | -0.00 | -0.13 | -0.05 | -0.08 | 0.07 |
| lampwarm6_glass | ord | home_glass | -0.07 | -0.06 | 0.23 | -0.14 | 0.08 | -0.10 | 0.16 |
| lampmid3_glass | ord | home_glass | -0.12 | 0.12 | -0.02 | -0.10 | -0.07 | 0.01 | 0.12 |
| lampcool6_bathtile | ord | home_bathtile | -0.26 | -0.18 | 0.39 | -0.63 | 0.07 | -0.41 | 0.40 |
| lampmid6_bathtile | ord | home_bathtile | -0.20 | -0.10 | 1.19 | -0.92 | 0.50 | -0.51 | 0.81 |
| lampwarm6_bathtile | ord | home_bathtile | -0.09 | -0.05 | 1.44 | -1.13 | 0.67 | -0.59 | 0.93 |
| lampmid3_bathtile | ord | home_bathtile | -0.28 | -0.15 | 1.33 | -0.94 | 0.52 | -0.55 | 0.90 |
| lampcool6_ottoman | ord | home_ottoman | -0.62 | -0.29 | 0.51 | -0.51 | -0.06 | -0.40 | 0.57 |
| lampmid6_ottoman | ord | home_ottoman | -0.55 | -0.34 | 1.02 | -0.66 | 0.24 | -0.50 | 0.80 |
| lampwarm6_ottoman | ord | home_ottoman | -0.51 | -0.30 | 1.29 | -0.88 | 0.39 | -0.59 | 0.94 |
| lampmid3_ottoman | ord | home_ottoman | -0.50 | -0.19 | 1.11 | -0.63 | 0.30 | -0.41 | 0.84 |
| lampcool6_wood | ext | home_wooddesk | -0.38 | -0.19 | 1.22 | -0.80 | 0.42 | -0.50 | 0.85 |
| lampmid6_wood | ext | home_wooddesk | -0.30 | -0.13 | 1.42 | -0.92 | 0.56 | -0.53 | 0.94 |
| lampwarm6_wood | ext | home_wooddesk | -0.22 | -0.11 | 1.49 | -1.03 | 0.63 | -0.57 | 0.97 |
| lampcool3_wood | ext | home_wooddesk | -0.49 | -0.13 | 1.32 | -0.90 | 0.42 | -0.51 | 0.98 |
| lampmid3_wood | ext | home_wooddesk | -0.50 | 0.01 | 1.42 | -0.97 | 0.46 | -0.48 | 1.07 |
| lampwarm3_wood | ext | home_wooddesk | -0.46 | -0.14 | 1.42 | -0.97 | 0.48 | -0.55 | 1.02 |
| window_black | ext | home_black | -0.99 | 0.43 | 0.65 | -0.75 | -0.17 | -0.16 | 1.01 |


### Q5 each frame statistic as a predictor of the shift (25 conditions, 10 places; error = RMS length of the 2-D error vector, log units)

| target | statistic | r logR/G | r logB/G | LOPO linear error, ordinary | extreme | identity (stat - home stat) error, ordinary | extreme |
|---|---|---|---|---|---|---|---|
| common | baseline: no shift |  |  | 0.47 | 0.68 |  |  |
| common | baseline: mean shift of the other places |  |  | 0.44 | 0.47 |  |  |
| common | (a) rows 0-49 mean | 0.68 | 0.79 | 0.34 | 0.33 | 0.28 | 0.26 |
| common | (a) rows 0-49 brightest 20% | 0.66 | 0.79 | 0.34 | 0.32 | 0.29 | 0.32 |
| common | (a) rows 0-49 median chroma | 0.62 | 0.73 | 0.38 | 0.42 | 0.30 | 0.28 |
| common | (a) rows 0-49 mean, unclipped not-dark px | 0.70 | 0.81 | 0.34 | 0.34 | 0.28 | 0.26 |
| common | (b) gray-world, all pixels | 0.81 | 0.78 | 0.33 | 0.15 | 0.30 | 0.29 |
| common | (b) gray-world, rows >= 50 | 0.80 | 0.77 | 0.33 | 0.14 | 0.31 | 0.30 |
| common | (c) white patch: brightest 5% mean | 0.61 | 0.82 | 0.31 | 0.34 | 0.29 | 0.39 |
| common | (c) brightest 5% median chroma | 0.59 | 0.82 | 0.29 | 0.36 | 0.29 | 0.41 |
| common | (c) brightest 5% of unclipped px | 0.64 | 0.82 | 0.31 | 0.34 | 0.29 | 0.39 |
| common | (d) bottom 80 rows median chroma | 0.70 | 0.67 | 0.41 | 0.17 | 0.43 | 0.33 |
| common | (e) low-saturation px (S<64) mean chroma | 0.45 | 0.70 | 0.37 | 0.38 | 0.43 | 0.62 |
| common | (e) low-saturation px most common chroma | 0.22 | 0.71 | 0.37 | 0.38 | 0.42 | 0.60 |
| common | (e) gray-edge (mean abs gradient per channel) | -0.20 | -0.20 | 0.42 | 0.45 | 0.49 | 0.81 |
| common | (e) shades of gray p=6 | 0.77 | 0.78 | 0.34 | 0.25 | 0.29 | 0.34 |
| orange | baseline: no shift |  |  | 0.45 | 0.57 |  |  |
| orange | baseline: mean shift of the other places |  |  | 0.46 | 0.41 |  |  |
| orange | (a) rows 0-49 mean | -0.08 | 0.48 | 0.52 | 0.40 | 0.70 | 0.89 |
| orange | (a) rows 0-49 brightest 20% | -0.22 | 0.47 | 0.50 | 0.41 | 0.67 | 0.85 |
| orange | (a) rows 0-49 median chroma | -0.05 | 0.42 | 0.52 | 0.39 | 0.72 | 0.87 |
| orange | (a) rows 0-49 mean, unclipped not-dark px | -0.09 | 0.51 | 0.53 | 0.40 | 0.71 | 0.90 |
| orange | (b) gray-world, all pixels | 0.14 | 0.41 | 0.53 | 0.38 | 0.57 | 0.90 |
| orange | (b) gray-world, rows >= 50 | 0.17 | 0.40 | 0.54 | 0.38 | 0.57 | 0.92 |
| orange | (c) white patch: brightest 5% mean | -0.25 | 0.55 | 0.48 | 0.46 | 0.64 | 0.74 |
| orange | (c) brightest 5% median chroma | -0.22 | 0.55 | 0.47 | 0.46 | 0.64 | 0.75 |
| orange | (c) brightest 5% of unclipped px | -0.20 | 0.55 | 0.50 | 0.44 | 0.63 | 0.74 |
| orange | (d) bottom 80 rows median chroma | 0.13 | 0.31 | 0.56 | 0.42 | 0.56 | 0.86 |
| orange | (e) low-saturation px (S<64) mean chroma | 0.18 | 0.65 | 0.47 | 0.38 | 0.45 | 0.61 |
| orange | (e) low-saturation px most common chroma | -0.06 | 0.60 | 0.44 | 0.39 | 0.44 | 0.58 |
| orange | (e) gray-edge (mean abs gradient per channel) | 0.47 | -0.01 | 0.49 | 0.50 | 0.41 | 0.54 |
| orange | (e) shades of gray p=6 | -0.19 | 0.44 | 0.55 | 0.41 | 0.59 | 0.76 |
| blue | baseline: no shift |  |  | 0.92 | 1.59 |  |  |
| blue | baseline: mean shift of the other places |  |  | 0.81 | 0.94 |  |  |
| blue | (a) rows 0-49 mean | 0.67 | 0.83 | 0.61 | 0.73 | 0.54 | 1.13 |
| blue | (a) rows 0-49 brightest 20% | 0.73 | 0.83 | 0.59 | 0.71 | 0.58 | 1.19 |
| blue | (a) rows 0-49 median chroma | 0.59 | 0.78 | 0.71 | 0.85 | 0.53 | 1.15 |
| blue | (a) rows 0-49 mean, unclipped not-dark px | 0.69 | 0.84 | 0.61 | 0.74 | 0.51 | 1.12 |
| blue | (b) gray-world, all pixels | 0.66 | 0.86 | 0.54 | 0.39 | 0.68 | 1.13 |
| blue | (b) gray-world, rows >= 50 | 0.63 | 0.85 | 0.55 | 0.36 | 0.70 | 1.13 |
| blue | (c) white patch: brightest 5% mean | 0.70 | 0.83 | 0.54 | 0.76 | 0.62 | 1.30 |
| blue | (c) brightest 5% median chroma | 0.67 | 0.82 | 0.47 | 0.81 | 0.61 | 1.31 |
| blue | (c) brightest 5% of unclipped px | 0.70 | 0.83 | 0.54 | 0.75 | 0.62 | 1.30 |
| blue | (d) bottom 80 rows median chroma | 0.56 | 0.76 | 0.71 | 0.41 | 0.83 | 1.19 |
| blue | (e) low-saturation px (S<64) mean chroma | 0.30 | 0.61 | 0.68 | 0.71 | 0.89 | 1.53 |
| blue | (e) low-saturation px most common chroma | 0.24 | 0.64 | 0.62 | 0.74 | 0.87 | 1.52 |
| blue | (e) gray-edge (mean abs gradient per channel) | -0.46 | -0.27 | 0.73 | 0.96 | 0.96 | 1.72 |
| blue | (e) shades of gray p=6 | 0.81 | 0.84 | 0.59 | 0.61 | 0.66 | 1.26 |


### Q5 nested leave-one-place-out (the statistic is chosen inside each fold, on the other places only)

- target common: picked abp_gray: b_grayworld, abp_white: b_grayworld, campus_study: b_grayworld, home_bathtile: a_top_bright20, home_black: b_grayworld, home_glass: b_grayworld_gate, home_ottoman: b_grayworld_gate, home_white: b_grayworld, home_wooddesk: c_white5_median, uc_palewood: b_grayworld
- target orange: picked abp_gray: e_lowS_mode, abp_white: e_lowS_mode, campus_study: e_lowS_mode, home_bathtile: c_white5_median, home_black: e_lowS_mode, home_glass: e_lowS_mode, home_ottoman: a_top_median, home_white: e_lowS_mode, home_wooddesk: f_grayedge, uc_palewood: e_lowS_mode
- target blue: picked abp_gray: b_grayworld, abp_white: b_grayworld_gate, campus_study: b_grayworld_gate, home_bathtile: g_shades6, home_black: b_grayworld_gate, home_glass: b_grayworld_gate, home_ottoman: b_grayworld_gate, home_white: b_grayworld_gate, home_wooddesk: c_white5_median, uc_palewood: b_grayworld
| target | ordinary: size of the shift (RMS) | ordinary: error of the prediction | extreme: size | extreme: error | frames (ordinary) | per frame: size of the shift | per frame: error, ordinary | per frame: error, extreme |
|---|---|---|---|---|---|---|---|---|
| common | 0.467 | 0.387 | 0.677 | 0.357 | 95 | 0.439 | 0.393 | 0.371 |
| orange | 0.449 | 0.513 | 0.567 | 0.508 | 98 | 0.409 | 0.450 | 0.511 |
| blue | 0.923 | 0.712 | 1.589 | 0.796 | 95 | 0.868 | 0.726 | 0.789 |


Per condition (length of the shift, and of the error of the nested prediction):

| condition | grp | place | common: shift | error | orange: shift | error | blue: shift | error |
|---|---|---|---|---|---|---|---|---|
| window_light | ord | home_white | 0.00 | 0.23 | 0.00 | 0.21 | 0.00 | 0.56 |
| campus_light | ord | campus_study | 0.21 | 0.10 | 0.18 | 0.03 | 0.52 | 0.05 |
| window_abpwhite | ord | abp_white | 0.15 | 0.25 | 0.21 | 0.03 | 0.19 | 0.53 |
| both_abpgray | ord | abp_gray | 0.74 | 0.78 | 1.28 | 1.45 | 0.21 | 0.38 |
| overheaddim_palewood | ord | uc_palewood | 0.03 | 0.56 | 0.12 | 0.08 | 0.16 | 0.74 |
| window_glass | ord | home_glass | 0.07 | 0.22 | 0.17 | 0.37 | 0.07 | 0.39 |
| lampcool6_glass | ord | home_glass | 0.10 | 0.28 | 0.22 | 0.27 | 0.13 | 0.50 |
| lampmid6_glass | ord | home_glass | 0.09 | 0.16 | 0.10 | 0.16 | 0.13 | 0.49 |
| lampwarm6_glass | ord | home_glass | 0.13 | 0.08 | 0.09 | 0.14 | 0.27 | 0.32 |
| lampmid3_glass | ord | home_glass | 0.07 | 0.19 | 0.17 | 0.23 | 0.10 | 0.43 |
| lampcool6_bathtile | ord | home_bathtile | 0.41 | 0.46 | 0.32 | 0.13 | 0.75 | 0.71 |
| lampmid6_bathtile | ord | home_bathtile | 0.71 | 0.34 | 0.22 | 0.35 | 1.50 | 0.84 |
| lampwarm6_bathtile | ord | home_bathtile | 0.89 | 0.68 | 0.11 | 0.83 | 1.82 | 1.80 |
| lampmid3_bathtile | ord | home_bathtile | 0.76 | 0.19 | 0.32 | 0.22 | 1.63 | 0.46 |
| lampcool6_ottoman | ord | home_ottoman | 0.40 | 0.31 | 0.68 | 0.58 | 0.72 | 0.31 |
| lampmid6_ottoman | ord | home_ottoman | 0.55 | 0.39 | 0.65 | 0.64 | 1.21 | 0.71 |
| lampwarm6_ottoman | ord | home_ottoman | 0.71 | 0.48 | 0.59 | 0.55 | 1.56 | 0.93 |
| lampmid3_ottoman | ord | home_ottoman | 0.51 | 0.39 | 0.54 | 0.60 | 1.28 | 0.89 |
| lampcool6_wood | ext | home_wooddesk | 0.65 | 0.48 | 0.42 | 0.31 | 1.46 | 0.98 |
| lampmid6_wood | ext | home_wooddesk | 0.77 | 0.28 | 0.33 | 0.21 | 1.69 | 0.56 |
| lampwarm6_wood | ext | home_wooddesk | 0.85 | 0.19 | 0.25 | 0.15 | 1.81 | 0.28 |
| lampcool3_wood | ext | home_wooddesk | 0.66 | 0.57 | 0.50 | 0.41 | 1.60 | 1.27 |
| lampmid3_wood | ext | home_wooddesk | 0.66 | 0.33 | 0.50 | 0.50 | 1.71 | 0.91 |
| lampwarm3_wood | ext | home_wooddesk | 0.73 | 0.25 | 0.48 | 0.61 | 1.71 | 0.62 |
| window_black | ext | home_black | 0.23 | 0.24 | 1.08 | 0.92 | 1.00 | 0.51 |


home orange cluster: mean (1.12, -0.93), SD (0.14, 0.24), radius holding 98% of the home pixels = 3.14 (Mahalanobis)

home blue cluster: mean (-1.46, 0.96), SD (0.42, 0.12), radius holding 98% of the home pixels = 3.56 (Mahalanobis)

### Q5 is it good enough? Share of barrel paint pixels inside the home cluster (98% radius) moved by the shift, and share of non-barrel pixels inside it (flood)


orange paint (body + stripe pixels):

| condition | grp | no shift: inside % | flood % | oracle common t: inside % | flood % | oracle per-class shift: inside % | flood % | predicted common t: inside % | flood % | predicted per-class: inside % | flood % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| window_light | ord | 98.0 | 0.0 | 98.0 | 0.0 | 98.0 | 0.0 | 98.1 | 0.0 | 92.0 | 0.0 |
| campus_light | ord | 83.2 | 0.1 | 68.1 | 0.1 | 92.6 | 0.2 | 82.0 | 0.1 | 93.6 | 0.2 |
| window_abpwhite | ord | 77.5 | 0.1 | 83.1 | 0.2 | 94.3 | 0.4 | 65.3 | 0.0 | 92.1 | 0.4 |
| both_abpgray | ord | 10.2 | 0.1 | 30.8 | 0.1 | 68.6 | 0.0 | 10.1 | 0.0 | 6.5 | 0.1 |
| overheaddim_palewood | ord | 87.5 | 0.1 | 88.5 | 0.1 | 87.9 | 0.3 | 28.9 | 0.0 | 81.3 | 0.4 |
| window_glass | ord | 94.8 | 0.1 | 97.8 | 0.1 | 99.1 | 0.1 | 87.4 | 0.1 | 85.6 | 0.1 |
| lampcool6_glass | ord | 97.0 | 0.1 | 99.5 | 0.1 | 99.8 | 0.1 | 89.7 | 0.1 | 98.0 | 0.1 |
| lampmid6_glass | ord | 99.5 | 0.1 | 99.5 | 0.1 | 99.7 | 0.2 | 96.7 | 0.1 | 99.2 | 0.2 |
| lampwarm6_glass | ord | 99.5 | 0.2 | 99.0 | 0.1 | 99.6 | 0.2 | 97.0 | 0.1 | 99.3 | 0.2 |
| lampmid3_glass | ord | 97.6 | 0.1 | 99.2 | 0.1 | 99.5 | 0.1 | 93.9 | 0.1 | 97.4 | 0.1 |
| lampcool6_bathtile | ord | 94.7 | 0.2 | 70.2 | 0.1 | 99.1 | 0.2 | 0.0 | 0.0 | 98.7 | 0.4 |
| lampmid6_bathtile | ord | 98.8 | 0.4 | 0.0 | 0.0 | 99.6 | 0.9 | 0.0 | 0.0 | 98.5 | 13.7 |
| lampwarm6_bathtile | ord | 99.4 | 0.6 | 0.0 | 0.0 | 99.4 | 3.2 | 0.0 | 0.0 | 0.0 | 93.8 |
| lampmid3_bathtile | ord | 97.8 | 0.3 | 0.0 | 0.0 | 100.0 | 0.5 | 0.0 | 0.0 | 99.9 | 3.4 |
| lampcool6_ottoman | ord | 6.7 | 0.0 | 11.2 | 0.0 | 98.5 | 0.0 | 5.2 | 0.0 | 44.8 | 0.0 |
| lampmid6_ottoman | ord | 25.1 | 0.0 | 1.2 | 0.0 | 97.3 | 0.2 | 7.6 | 0.0 | 40.9 | 0.1 |
| lampwarm6_ottoman | ord | 33.2 | 0.1 | 0.0 | 0.0 | 98.1 | 1.8 | 6.0 | 0.0 | 55.3 | 0.2 |
| lampmid3_ottoman | ord | 13.4 | 0.0 | 0.0 | 0.0 | 65.6 | 0.2 | 4.1 | 0.0 | 20.1 | 0.1 |
| lampcool6_wood | ext | 73.2 | 0.0 | 0.0 | 0.0 | 99.8 | 1.3 | 41.8 | 0.0 | 99.5 | 1.0 |
| lampmid6_wood | ext | 89.6 | 0.0 | 0.0 | 0.0 | 100.0 | 15.8 | 8.6 | 0.0 | 99.9 | 16.3 |
| lampwarm6_wood | ext | 98.0 | 0.2 | 0.0 | 0.0 | 99.9 | 23.6 | 0.0 | 0.0 | 99.6 | 36.2 |
| lampcool3_wood | ext | 33.4 | 0.0 | 0.0 | 0.0 | 99.6 | 5.0 | 9.0 | 1.3 | 79.0 | 0.2 |
| lampmid3_wood | ext | 13.0 | 0.0 | 0.0 | 0.0 | 100.0 | 49.9 | 0.0 | 0.0 | 30.8 | 0.0 |
| lampwarm3_wood | ext | 36.8 | 0.0 | 0.0 | 0.0 | 99.6 | 58.7 | 0.0 | 0.0 | 22.2 | 0.0 |
| window_black | ext | 0.0 | 0.0 | 0.0 | 0.0 | 99.8 | 60.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| MEAN ordinary |  | 73.0 | 0.1 | 52.6 | 0.1 | 94.3 | 0.5 | 42.9 | 0.0 | 72.4 | 6.3 |
| MEAN extreme |  | 49.1 | 0.0 | 0.0 | 0.0 | 99.8 | 30.6 | 8.5 | 0.2 | 61.6 | 7.7 |


blue paint (body + stripe pixels):

| condition | grp | no shift: inside % | flood % | oracle common t: inside % | flood % | oracle per-class shift: inside % | flood % | predicted common t: inside % | flood % | predicted per-class: inside % | flood % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| window_light | ord | 98.0 | 0.0 | 98.0 | 0.0 | 98.0 | 0.0 | 93.2 | 0.0 | 45.3 | 4.7 |
| campus_light | ord | 48.9 | 0.1 | 84.4 | 0.2 | 89.4 | 0.4 | 82.7 | 0.2 | 90.1 | 0.4 |
| window_abpwhite | ord | 95.0 | 0.4 | 97.9 | 0.4 | 99.7 | 0.5 | 99.7 | 0.6 | 95.3 | 1.4 |
| both_abpgray | ord | 66.2 | 0.6 | 54.3 | 0.4 | 70.9 | 0.5 | 62.6 | 0.7 | 56.2 | 1.0 |
| overheaddim_palewood | ord | 97.2 | 0.1 | 97.7 | 0.1 | 98.7 | 0.2 | 97.2 | 0.2 | 90.6 | 0.7 |
| window_glass | ord | 99.9 | 1.0 | 99.9 | 0.9 | 99.9 | 1.0 | 99.9 | 1.0 | 97.3 | 2.2 |
| lampcool6_glass | ord | 100.0 | 0.9 | 100.0 | 0.9 | 99.9 | 0.9 | 99.8 | 0.7 | 96.6 | 1.6 |
| lampmid6_glass | ord | 99.4 | 0.8 | 99.6 | 0.7 | 99.6 | 0.7 | 99.4 | 0.6 | 97.8 | 1.0 |
| lampwarm6_glass | ord | 99.2 | 0.6 | 99.2 | 0.6 | 99.2 | 0.7 | 99.2 | 0.6 | 98.6 | 0.9 |
| lampmid3_glass | ord | 99.6 | 0.8 | 99.6 | 0.8 | 99.7 | 0.7 | 99.7 | 0.6 | 97.8 | 1.0 |
| lampcool6_bathtile | ord | 0.2 | 0.0 | 97.2 | 0.2 | 99.8 | 0.5 | 99.8 | 0.5 | 88.8 | 24.8 |
| lampmid6_bathtile | ord | 0.0 | 0.0 | 36.2 | 0.2 | 100.0 | 1.4 | 99.5 | 0.6 | 12.8 | 82.2 |
| lampwarm6_bathtile | ord | 0.0 | 0.0 | 2.4 | 0.1 | 99.6 | 1.6 | 99.6 | 1.5 | 0.0 | 86.8 |
| lampmid3_bathtile | ord | 0.0 | 0.0 | 28.1 | 0.1 | 94.7 | 6.4 | 92.7 | 0.6 | 86.9 | 68.5 |
| lampcool6_ottoman | ord | 22.1 | 0.2 | 91.6 | 0.3 | 93.9 | 1.7 | 49.9 | 0.2 | 90.4 | 0.4 |
| lampmid6_ottoman | ord | 0.2 | 0.0 | 85.7 | 0.3 | 89.0 | 15.7 | 1.1 | 0.1 | 60.8 | 0.3 |
| lampwarm6_ottoman | ord | 0.0 | 0.0 | 56.5 | 0.3 | 68.7 | 27.5 | 0.0 | 0.0 | 1.4 | 0.1 |
| lampmid3_ottoman | ord | 0.0 | 0.0 | 5.8 | 0.0 | 5.8 | 1.0 | 0.0 | 0.0 | 4.0 | 0.0 |
| lampcool6_wood | ext | 0.0 | 0.0 | 59.1 | 0.3 | 100.0 | 15.9 | 15.4 | 0.0 | 50.5 | 1.3 |
| lampmid6_wood | ext | 0.0 | 0.0 | 27.1 | 0.1 | 100.0 | 9.8 | 22.1 | 0.2 | 73.2 | 4.7 |
| lampwarm6_wood | ext | 0.0 | 0.0 | 10.5 | 0.2 | 99.9 | 7.8 | 20.9 | 0.5 | 99.8 | 5.0 |
| lampcool3_wood | ext | 0.0 | 0.0 | 30.8 | 0.1 | 83.1 | 25.2 | 4.0 | 0.0 | 24.7 | 0.7 |
| lampmid3_wood | ext | 0.0 | 0.0 | 2.6 | 0.0 | 99.9 | 24.4 | 11.7 | 0.0 | 24.9 | 1.5 |
| lampwarm3_wood | ext | 0.0 | 0.0 | 4.8 | 0.1 | 99.8 | 12.8 | 13.7 | 0.2 | 58.0 | 2.9 |
| window_black | ext | 0.0 | 0.0 | 3.0 | 0.0 | 100.0 | 58.5 | 5.6 | 0.0 | 45.3 | 0.2 |
| MEAN ordinary |  | 51.4 | 0.3 | 74.1 | 0.4 | 89.2 | 3.4 | 76.4 | 0.5 | 67.3 | 15.4 |
| MEAN extreme |  | 0.0 | 0.0 | 19.7 | 0.1 | 97.5 | 22.1 | 13.4 | 0.1 | 53.8 | 2.3 |

**Verdict: the frame statistics carry the direction of the light, not enough to place the clusters.** For the common translation the best are gray-world (r 0.81 and 0.78 on the two axes), the white patch (0.59-0.64 and 0.82) and the rows above the gate (0.62-0.70 and 0.73-0.81); the low-saturation mode and gray-edge are worse. Leave-one-place-out error is 0.29-0.34 log units for the best single statistics, and 0.39 with the statistic chosen inside the fold, against a shift of 0.47 (ordinary); in the extreme conditions 0.36 against 0.68. Per class the picture splits: the blue shift is partly predictable (0.71 against 0.92; ordinary), the orange shift is not (0.51 against 0.45: worse than predicting no shift), because the orange shift does not follow the light's colour (r -0.25 to +0.18 on log R/G for every statistic but gray-edge, +0.47).

Good enough, by the test asked for (share of barrel paint pixels inside the home 98% cluster after moving it; mean over the 18 ordinary conditions):

| | orange inside | orange flood | blue inside | blue flood |
|---|---|---|---|---|
| no shift | 73.0% | 0.1% | 51.4% | 0.3% |
| oracle common translation | 52.6% | 0.1% | 74.1% | 0.4% |
| oracle per-class shift | 94.3% | 0.5% | 89.2% | 3.4% |
| predicted common translation | 42.9% | 0.0% | 76.4% | 0.5% |
| predicted per-class shift | 72.4% | 6.3% | 67.3% | 15.4% |

The common translation is the wrong target for orange even when known exactly (52.6% against 73.0% with no shift: it drags the orange cluster after the blue one; on the tile under mid and warm lamp it takes orange from 99% to 0%). It helps blue (51% to 74-76%, predicted as well as oracle). Predicted per-class shifts flood (the predicted blue cluster lands on the tile: 68-87% of non-barrel pixels). So: not good enough.

## Q6. Pixel-level ceilings at 1% flood

### Q6 barrel-paint pixel recall at 1% flood of non-barrel pixels (rows >= 50, outside boxes + 4 px; V >= 40 required everywhere)

(i) fixed hs rectangle: its own operating point (recall / flood as they fall). (ii) per-condition H x S lookup, in-sample oracle (hue 2 x S 8 bins). (ii-b) per-condition best rectangle hue range x S floor, in-sample oracle. (iii) home log-chroma Gaussian, no shift. (iv) oracle common translation. (iv-b) oracle per-class translation. (v) predicted common translation (nested leave-one-place-out, per frame). (v-b) predicted per-class translation.


orange paint:

| condition | grp | (i) fixed: recall | (i) fixed: flood | (ii) lookup | (ii-b) best rectangle | (iii) LC no shift | (iv) LC oracle common | (iv-b) LC oracle per-class | (v) LC predicted common | (v-b) LC predicted per-class | best rectangle (h_lo, h_hi, s_lo) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| window_light | ord | 99.7 | 0.1 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | (-43, 11, 16) |
| campus_light | ord | 95.9 | 0.3 | 100.0 | 99.5 | 99.2 | 99.2 | 99.2 | 99.1 | 99.1 | (-42, 17, 56) |
| window_abpwhite | ord | 99.9 | 0.6 | 100.0 | 100.0 | 99.9 | 99.3 | 99.4 | 99.9 | 99.4 | (-43, 12, 108) |
| both_abpgray | ord | 19.6 | 0.5 | 100.0 | 94.8 | 27.4 | 93.3 | 93.8 | 29.8 | 11.8 | (-38, 8, 168) |
| overheaddim_palewood | ord | 96.2 | 8.4 | 100.0 | 98.6 | 98.1 | 98.8 | 97.0 | 99.9 | 90.1 | (1, 11, 164) |
| window_glass | ord | 99.7 | 0.2 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | (-43, 12, 20) |
| lampcool6_glass | ord | 99.9 | 0.2 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | (-43, 11, 4) |
| lampmid6_glass | ord | 99.9 | 0.3 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | (-43, 11, 48) |
| lampwarm6_glass | ord | 100.0 | 0.4 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 99.9 | (-43, 12, 92) |
| lampmid3_glass | ord | 99.9 | 0.2 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | (-43, 13, 48) |
| lampcool6_bathtile | ord | 99.6 | 0.3 | 100.0 | 100.0 | 100.0 | 100.0 | 99.8 | 100.0 | 99.0 | (-43, 14, 0) |
| lampmid6_bathtile | ord | 100.0 | 1.7 | 100.0 | 100.0 | 99.9 | 100.0 | 99.6 | 100.0 | 19.3 | (-43, 13, 176) |
| lampwarm6_bathtile | ord | 100.0 | 5.3 | 100.0 | 100.0 | 99.4 | 100.0 | 99.4 | 99.6 | 0.0 | (-43, 11, 156) |
| lampmid3_bathtile | ord | 99.7 | 1.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 99.6 | (-43, 14, 148) |
| lampcool6_ottoman | ord | 23.0 | 0.1 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | (-43, 19, 44) |
| lampmid6_ottoman | ord | 38.8 | 0.3 | 100.0 | 100.0 | 99.5 | 99.9 | 99.1 | 99.7 | 99.1 | (-43, 19, 136) |
| lampwarm6_ottoman | ord | 47.9 | 0.5 | 100.0 | 99.9 | 99.9 | 100.0 | 95.7 | 100.0 | 99.4 | (-43, 19, 184) |
| lampmid3_ottoman | ord | 53.5 | 0.3 | 69.0 | 69.0 | 68.9 | 69.0 | 68.3 | 68.9 | 68.7 | (-43, 18, 80) |
| lampcool6_wood | ext | 89.2 | 0.3 | 100.0 | 100.0 | 100.0 | 100.0 | 99.8 | 84.2 | 99.5 | (-43, 17, 164) |
| lampmid6_wood | ext | 99.3 | 1.6 | 100.0 | 100.0 | 100.0 | 99.7 | 99.8 | 70.2 | 98.1 | (-43, 14, 168) |
| lampwarm6_wood | ext | 100.0 | 2.5 | 100.0 | 100.0 | 99.9 | 99.9 | 99.6 | 68.7 | 96.8 | (-43, 13, 184) |
| lampcool3_wood | ext | 77.5 | 0.3 | 100.0 | 99.5 | 99.9 | 99.8 | 98.6 | 6.9 | 98.0 | (-43, 17, 156) |
| lampmid3_wood | ext | 82.6 | 0.8 | 99.2 | 98.7 | 98.3 | 97.5 | 95.1 | 70.4 | 94.7 | (-43, 15, 160) |
| lampwarm3_wood | ext | 85.5 | 2.0 | 97.4 | 96.4 | 96.9 | 95.7 | 91.7 | 69.1 | 88.9 | (-43, 15, 180) |
| window_black | ext | 0.1 | 0.1 | 96.4 | 86.4 | 51.7 | 56.8 | 71.4 | 63.0 | 55.8 | (14, 34, 64) |
| MEAN ordinary |  | 81.9 | 1.1 | 98.3 | 97.9 | 94.0 | 97.7 | 97.3 | 94.3 | 82.5 |  |
| MEDIAN ordinary |  | 99.7 | 0.3 | 100.0 | 100.0 | 100.0 | 100.0 | 99.7 | 100.0 | 99.4 |  |
| MIN ordinary |  | 19.6 | 0.1 | 69.0 | 69.0 | 27.4 | 69.0 | 68.3 | 29.8 | 0.0 |  |
| MEAN extreme |  | 76.3 | 1.1 | 99.0 | 97.3 | 92.4 | 92.8 | 93.7 | 61.8 | 90.3 |  |
| MIN extreme |  | 0.1 | 0.1 | 96.4 | 86.4 | 51.7 | 56.8 | 71.4 | 6.9 | 55.8 |  |


blue paint:

| condition | grp | (i) fixed: recall | (i) fixed: flood | (ii) lookup | (ii-b) best rectangle | (iii) LC no shift | (iv) LC oracle common | (iv-b) LC oracle per-class | (v) LC predicted common | (v-b) LC predicted per-class | best rectangle (h_lo, h_hi, s_lo) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| window_light | ord | 99.7 | 0.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 98.8 | 36.7 | (106, 139, 96) |
| campus_light | ord | 90.8 | 0.3 | 100.0 | 92.9 | 93.0 | 92.7 | 91.3 | 93.0 | 92.5 | (90, 161, 72) |
| window_abpwhite | ord | 99.8 | 1.0 | 100.0 | 100.0 | 99.9 | 99.9 | 99.8 | 99.8 | 81.1 | (61, 115, 100) |
| both_abpgray | ord | 89.1 | 1.3 | 100.0 | 99.9 | 69.5 | 80.9 | 75.8 | 66.8 | 55.7 | (61, 136, 176) |
| overheaddim_palewood | ord | 100.0 | 0.2 | 100.0 | 100.0 | 99.9 | 99.9 | 99.7 | 99.4 | 94.6 | (61, 116, 56) |
| window_glass | ord | 100.0 | 2.4 | 100.0 | 100.0 | 99.9 | 99.9 | 99.9 | 99.9 | 74.7 | (61, 113, 136) |
| lampcool6_glass | ord | 100.0 | 1.5 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 99.9 | 87.2 | (61, 111, 88) |
| lampmid6_glass | ord | 100.0 | 1.3 | 100.0 | 100.0 | 99.6 | 99.6 | 99.6 | 99.6 | 97.8 | (61, 113, 48) |
| lampwarm6_glass | ord | 100.0 | 0.9 | 100.0 | 100.0 | 99.7 | 99.6 | 99.2 | 99.6 | 98.9 | (61, 115, 20) |
| lampmid3_glass | ord | 100.0 | 1.5 | 100.0 | 100.0 | 99.7 | 99.7 | 99.7 | 99.7 | 98.0 | (61, 113, 72) |
| lampcool6_bathtile | ord | 32.4 | 0.2 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 42.5 | (61, 123, 0) |
| lampmid6_bathtile | ord | 2.0 | 0.0 | 100.0 | 98.5 | 100.0 | 100.0 | 99.8 | 100.0 | 0.0 | (61, 156, 0) |
| lampwarm6_bathtile | ord | 0.0 | 0.0 | 100.0 | 7.1 | 99.3 | 99.3 | 99.2 | 99.3 | 0.0 | (61, 159, 0) |
| lampmid3_bathtile | ord | 0.3 | 0.0 | 94.7 | 75.0 | 93.6 | 93.9 | 88.4 | 94.2 | 0.0 | (61, 161, 0) |
| lampcool6_ottoman | ord | 79.4 | 0.4 | 97.9 | 93.6 | 92.0 | 93.1 | 93.3 | 92.8 | 93.2 | (95, 118, 60) |
| lampmid6_ottoman | ord | 60.9 | 0.1 | 92.9 | 88.3 | 87.9 | 88.0 | 87.8 | 88.0 | 87.7 | (61, 150, 0) |
| lampwarm6_ottoman | ord | 0.3 | 0.0 | 70.9 | 63.7 | 62.9 | 64.4 | 62.8 | 58.6 | 25.4 | (61, 145, 0) |
| lampmid3_ottoman | ord | 5.3 | 0.0 | 7.8 | 5.8 | 5.8 | 5.8 | 5.8 | 5.8 | 5.8 | (61, 119, 0) |
| lampcool6_wood | ext | 24.0 | 0.0 | 98.0 | 85.3 | 81.6 | 80.0 | 55.3 | 61.5 | 43.7 | (101, 126, 20) |
| lampmid6_wood | ext | 0.0 | 0.0 | 99.6 | 61.4 | 78.1 | 78.4 | 60.3 | 30.4 | 0.6 | (61, 161, 0) |
| lampwarm6_wood | ext | 0.0 | 0.0 | 95.7 | 18.3 | 55.8 | 56.5 | 58.9 | 25.8 | 7.1 | (61, 160, 0) |
| lampcool3_wood | ext | 2.1 | 0.0 | 79.0 | 67.9 | 60.7 | 62.8 | 34.7 | 34.8 | 29.1 | (98, 120, 28) |
| lampmid3_wood | ext | 0.0 | 0.0 | 98.9 | 58.3 | 89.6 | 89.6 | 47.1 | 25.4 | 22.7 | (61, 161, 0) |
| lampwarm3_wood | ext | 0.0 | 0.0 | 87.6 | 19.6 | 63.3 | 63.5 | 62.9 | 22.0 | 21.8 | (61, 156, 0) |
| window_black | ext | 11.3 | 0.1 | 100.0 | 99.9 | 89.0 | 91.0 | 95.1 | 90.0 | 87.6 | (84, 109, 0) |
| MEAN ordinary |  | 64.5 | 0.6 | 92.5 | 84.7 | 89.0 | 89.8 | 89.0 | 88.6 | 59.6 |  |
| MEDIAN ordinary |  | 89.9 | 0.3 | 100.0 | 99.9 | 99.7 | 99.6 | 99.4 | 99.4 | 77.9 |  |
| MIN ordinary |  | 0.0 | 0.0 | 7.8 | 5.8 | 5.8 | 5.8 | 5.8 | 5.8 | 0.0 |  |
| MEAN extreme |  | 5.4 | 0.0 | 94.1 | 58.7 | 74.0 | 74.6 | 59.2 | 41.4 | 30.4 |  |
| MIN extreme |  | 0.0 | 0.0 | 79.0 | 18.3 | 55.8 | 56.5 | 34.7 | 22.0 | 0.6 |  |


### Q6b no per-condition knob: the home log-chroma model with ONE radius per colour for all conditions (the radius at which the mean flood over the 18 ordinary conditions is 1%)


orange paint:

| condition | grp | (i) fixed hs: recall | flood | no shift (radius 4.50): recall | flood | oracle common t (radius 5.75): recall | flood | oracle per-class (radius 3.50): recall | flood | predicted common t (radius 7.00): recall | flood | predicted per-class (radius 0.50): recall | flood |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| window_light | ord | 99.7 | 0.1 | 99.5 | 0.0 | 99.7 | 0.1 | 98.6 | 0.0 | 99.7 | 0.2 | 4.0 | 0.0 |
| campus_light | ord | 95.9 | 0.3 | 95.6 | 0.2 | 96.4 | 0.2 | 94.9 | 0.2 | 98.6 | 0.5 | 13.9 | 0.0 |
| window_abpwhite | ord | 99.9 | 0.6 | 96.1 | 0.5 | 100.0 | 5.5 | 97.1 | 0.6 | 100.0 | 3.4 | 13.5 | 0.0 |
| both_abpgray | ord | 19.6 | 0.5 | 20.6 | 0.3 | 89.8 | 0.3 | 72.1 | 0.0 | 36.3 | 4.6 | 0.0 | 0.0 |
| overheaddim_palewood | ord | 96.2 | 8.4 | 97.9 | 0.9 | 99.7 | 5.3 | 92.6 | 0.4 | 96.7 | 0.4 | 14.2 | 0.0 |
| window_glass | ord | 99.7 | 0.2 | 100.0 | 0.2 | 100.0 | 0.3 | 99.6 | 0.1 | 100.0 | 0.6 | 0.0 | 0.0 |
| lampcool6_glass | ord | 99.9 | 0.2 | 99.9 | 0.2 | 100.0 | 0.3 | 99.8 | 0.2 | 100.0 | 1.2 | 0.2 | 0.0 |
| lampmid6_glass | ord | 99.9 | 0.3 | 99.9 | 0.2 | 100.0 | 0.4 | 99.7 | 0.2 | 100.0 | 0.6 | 27.5 | 0.0 |
| lampwarm6_glass | ord | 100.0 | 0.4 | 99.9 | 0.3 | 100.0 | 0.4 | 99.8 | 0.2 | 100.0 | 0.6 | 5.9 | 0.0 |
| lampmid3_glass | ord | 99.9 | 0.2 | 100.0 | 0.2 | 100.0 | 0.4 | 99.6 | 0.2 | 100.0 | 0.7 | 0.7 | 0.0 |
| lampcool6_bathtile | ord | 99.6 | 0.3 | 99.2 | 0.3 | 100.0 | 0.3 | 99.2 | 0.3 | 95.4 | 0.1 | 7.6 | 0.0 |
| lampmid6_bathtile | ord | 100.0 | 1.7 | 99.9 | 1.3 | 57.3 | 0.2 | 99.9 | 2.6 | 26.6 | 0.1 | 0.0 | 0.0 |
| lampwarm6_bathtile | ord | 100.0 | 5.3 | 99.7 | 11.4 | 4.6 | 0.2 | 99.5 | 7.0 | 0.0 | 0.0 | 0.0 | 5.8 |
| lampmid3_bathtile | ord | 99.7 | 1.0 | 100.0 | 0.4 | 11.2 | 0.1 | 100.0 | 0.8 | 25.6 | 0.2 | 9.8 | 0.0 |
| lampcool6_ottoman | ord | 23.0 | 0.1 | 55.1 | 0.0 | 99.0 | 0.0 | 99.1 | 0.0 | 99.9 | 0.3 | 0.0 | 0.0 |
| lampmid6_ottoman | ord | 38.8 | 0.3 | 73.5 | 0.2 | 45.7 | 0.0 | 98.2 | 0.3 | 99.5 | 0.4 | 0.4 | 0.0 |
| lampwarm6_ottoman | ord | 47.9 | 0.5 | 85.7 | 0.3 | 14.1 | 0.0 | 99.1 | 2.5 | 100.0 | 1.2 | 0.5 | 0.0 |
| lampmid3_ottoman | ord | 53.5 | 0.3 | 62.4 | 0.1 | 20.9 | 0.0 | 67.0 | 0.3 | 68.7 | 0.4 | 0.0 | 0.0 |
| lampcool6_wood | ext | 89.2 | 0.3 | 99.5 | 0.2 | 33.0 | 0.0 | 99.9 | 3.4 | 96.5 | 7.9 | 8.0 | 0.0 |
| lampmid6_wood | ext | 99.3 | 1.6 | 100.0 | 1.2 | 6.5 | 0.0 | 100.0 | 37.8 | 70.8 | 14.1 | 21.5 | 0.0 |
| lampwarm6_wood | ext | 100.0 | 2.5 | 99.9 | 14.5 | 1.1 | 0.0 | 99.9 | 45.1 | 72.6 | 3.4 | 20.9 | 0.0 |
| lampcool3_wood | ext | 77.5 | 0.3 | 93.6 | 0.1 | 3.0 | 0.0 | 99.8 | 15.2 | 82.9 | 10.5 | 0.3 | 0.0 |
| lampmid3_wood | ext | 82.6 | 0.8 | 95.1 | 0.1 | 0.0 | 0.0 | 100.0 | 61.4 | 71.2 | 3.3 | 0.0 | 0.0 |
| lampwarm3_wood | ext | 85.5 | 2.0 | 96.0 | 0.5 | 0.1 | 0.0 | 99.8 | 66.7 | 70.1 | 4.9 | 0.0 | 0.0 |
| window_black | ext | 0.1 | 0.1 | 0.0 | 0.0 | 21.8 | 0.3 | 99.9 | 60.4 | 17.5 | 0.2 | 0.0 | 0.0 |
| MEAN ordinary |  | 81.9 | 1.1 | 88.0 | 0.9 | 74.4 | 0.8 | 95.3 | 0.9 | 80.4 | 0.9 | 5.5 | 0.3 |
| MIN ordinary |  | 19.6 | 0.1 | 20.6 | 0.0 | 4.6 | 0.0 | 67.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| MAX ordinary |  | 100.0 | 8.4 | 100.0 | 11.4 | 100.0 | 5.5 | 100.0 | 7.0 | 100.0 | 4.6 | 27.5 | 5.8 |
| MEAN extreme |  | 76.3 | 1.1 | 83.4 | 2.4 | 9.4 | 0.0 | 99.9 | 41.4 | 68.8 | 6.3 | 7.2 | 0.0 |
| MIN extreme |  | 0.1 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 99.8 | 3.4 | 17.5 | 0.2 | 0.0 | 0.0 |
| MAX extreme |  | 100.0 | 2.5 | 100.0 | 14.5 | 33.0 | 0.3 | 100.0 | 66.7 | 96.5 | 14.1 | 21.5 | 0.0 |


blue paint:

| condition | grp | (i) fixed hs: recall | flood | no shift (radius 6.00): recall | flood | oracle common t (radius 4.50): recall | flood | oracle per-class (radius 2.00): recall | flood | predicted common t (radius 4.50): recall | flood | predicted per-class (radius 1.50): recall | flood |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| window_light | ord | 99.7 | 0.0 | 99.5 | 0.0 | 98.2 | 0.0 | 91.4 | 0.0 | 98.3 | 0.0 | 1.0 | 0.0 |
| campus_light | ord | 90.8 | 0.3 | 91.6 | 0.5 | 91.2 | 0.4 | 71.6 | 0.1 | 89.5 | 0.3 | 60.5 | 0.1 |
| window_abpwhite | ord | 99.8 | 1.0 | 100.0 | 1.3 | 99.9 | 0.6 | 91.0 | 0.1 | 99.8 | 1.2 | 22.2 | 0.1 |
| both_abpgray | ord | 89.1 | 1.3 | 75.5 | 1.9 | 69.3 | 0.6 | 53.2 | 0.2 | 67.5 | 1.1 | 9.6 | 0.1 |
| overheaddim_palewood | ord | 100.0 | 0.2 | 99.9 | 1.1 | 99.6 | 0.3 | 88.8 | 0.0 | 98.8 | 0.6 | 20.0 | 0.0 |
| window_glass | ord | 100.0 | 2.4 | 100.0 | 3.3 | 100.0 | 1.5 | 99.5 | 0.1 | 100.0 | 1.9 | 6.1 | 0.2 |
| lampcool6_glass | ord | 100.0 | 1.5 | 100.0 | 2.0 | 100.0 | 1.2 | 98.6 | 0.1 | 100.0 | 1.4 | 0.5 | 0.1 |
| lampmid6_glass | ord | 100.0 | 1.3 | 100.0 | 1.8 | 99.8 | 1.2 | 97.1 | 0.0 | 99.8 | 1.3 | 8.2 | 0.0 |
| lampwarm6_glass | ord | 100.0 | 0.9 | 99.9 | 1.7 | 99.7 | 1.2 | 96.8 | 0.0 | 99.7 | 1.3 | 24.8 | 0.0 |
| lampmid3_glass | ord | 100.0 | 1.5 | 99.9 | 1.9 | 99.8 | 1.2 | 97.5 | 0.0 | 99.8 | 1.3 | 10.5 | 0.0 |
| lampcool6_bathtile | ord | 32.4 | 0.2 | 80.1 | 0.3 | 99.7 | 0.4 | 96.8 | 0.0 | 100.0 | 0.8 | 9.9 | 0.3 |
| lampmid6_bathtile | ord | 2.0 | 0.0 | 0.7 | 0.0 | 92.4 | 0.4 | 97.1 | 0.4 | 100.0 | 1.1 | 0.1 | 4.2 |
| lampwarm6_bathtile | ord | 0.0 | 0.0 | 0.0 | 0.0 | 36.6 | 0.2 | 98.7 | 0.7 | 100.0 | 2.5 | 0.0 | 0.1 |
| lampmid3_bathtile | ord | 0.3 | 0.0 | 0.0 | 0.0 | 87.8 | 0.4 | 92.1 | 1.7 | 94.6 | 2.0 | 3.3 | 6.8 |
| lampcool6_ottoman | ord | 79.4 | 0.4 | 90.3 | 0.8 | 93.4 | 1.1 | 88.0 | 0.1 | 76.1 | 0.4 | 27.8 | 0.0 |
| lampmid6_ottoman | ord | 60.9 | 0.1 | 47.0 | 0.3 | 88.2 | 1.2 | 87.4 | 0.6 | 17.8 | 0.2 | 0.4 | 0.0 |
| lampwarm6_ottoman | ord | 0.3 | 0.0 | 0.0 | 0.0 | 67.5 | 2.4 | 67.8 | 13.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| lampmid3_ottoman | ord | 5.3 | 0.0 | 5.0 | 0.0 | 5.8 | 0.0 | 5.8 | 0.0 | 0.3 | 0.0 | 0.0 | 0.0 |
| lampcool6_wood | ext | 24.0 | 0.0 | 15.2 | 0.0 | 97.4 | 2.1 | 94.8 | 4.8 | 27.3 | 0.0 | 21.1 | 0.0 |
| lampmid6_wood | ext | 0.0 | 0.0 | 0.0 | 0.0 | 78.0 | 0.9 | 99.3 | 4.3 | 25.0 | 0.7 | 2.0 | 1.4 |
| lampwarm6_wood | ext | 0.0 | 0.0 | 0.0 | 0.0 | 57.3 | 1.1 | 99.3 | 4.5 | 36.7 | 1.3 | 51.8 | 1.8 |
| lampcool3_wood | ext | 2.1 | 0.0 | 1.0 | 0.0 | 80.1 | 2.6 | 80.4 | 10.8 | 21.1 | 0.0 | 9.6 | 0.0 |
| lampmid3_wood | ext | 0.0 | 0.0 | 0.0 | 0.0 | 49.6 | 0.4 | 99.8 | 8.9 | 22.1 | 0.3 | 22.1 | 0.2 |
| lampwarm3_wood | ext | 0.0 | 0.0 | 0.0 | 0.0 | 64.8 | 1.1 | 98.9 | 5.3 | 21.8 | 0.8 | 21.7 | 0.9 |
| window_black | ext | 11.3 | 0.1 | 38.0 | 0.2 | 22.1 | 0.0 | 91.8 | 0.5 | 33.3 | 0.1 | 0.0 | 0.0 |
| MEAN ordinary |  | 64.5 | 0.6 | 66.1 | 0.9 | 84.9 | 0.8 | 84.4 | 1.0 | 80.1 | 1.0 | 11.4 | 0.7 |
| MIN ordinary |  | 0.0 | 0.0 | 0.0 | 0.0 | 5.8 | 0.0 | 5.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| MAX ordinary |  | 100.0 | 2.4 | 100.0 | 3.3 | 100.0 | 2.4 | 99.5 | 13.1 | 100.0 | 2.5 | 60.5 | 6.8 |
| MEAN extreme |  | 5.4 | 0.0 | 7.7 | 0.0 | 64.2 | 1.2 | 94.9 | 5.6 | 26.8 | 0.5 | 18.3 | 0.6 |
| MIN extreme |  | 0.0 | 0.0 | 0.0 | 0.0 | 22.1 | 0.0 | 80.4 | 0.5 | 21.1 | 0.0 | 0.0 | 0.0 |
| MAX extreme |  | 24.0 | 0.1 | 38.0 | 0.2 | 97.4 | 2.6 | 99.8 | 10.8 | 36.7 | 1.3 | 51.8 | 1.8 |

**Reading.** Means over the 18 ordinary conditions, barrel-patch recall at 1% flood (per-condition threshold):

| | orange | blue | orange, extreme | blue, extreme |
|---|---|---|---|---|
| (i) fixed hs rectangle (at its own flood: 1.1%, 0.6%) | 81.9 | 64.5 | 76.3 | 5.4 |
| (ii) per-condition H x S lookup (in-sample) | 98.3 | 92.5 | 99.0 | 94.1 |
| (ii-b) per-condition best rectangle (in-sample) | 97.9 | 84.7 | 97.3 | 58.7 |
| (iii) home log-chroma model, no shift | 94.0 | 89.0 | 92.4 | 74.0 |
| (iv) with the oracle common translation | 97.7 | 89.8 | 92.8 | 74.6 |
| (iv-b) with the oracle per-class translation | 97.3 | 89.0 | 93.7 | 59.2 |
| (v) with the predicted common translation | 94.3 | 88.6 | 61.8 | 41.4 |
| (v-b) with the predicted per-class translation | 82.5 | 59.6 | 90.3 | 30.4 |

- With oracle parameters, the log-chroma model with one translation equals the best hue/S rectangle on orange and beats it on blue (89.8 against 84.7 ordinary, 74.6 against 58.7 extreme): an elliptical region in log-chromaticity keeps the grayed blue that a hue range with an S floor cannot hold (warm lamp on the tile: 99.3 against 7.1).
- The translation is not what earns that. The same model with no translation, given only its per-condition threshold, scores 94.0 and 89.0; the translation adds 3.7 points on orange (almost all of it the gray table, 27 to 93) and 0.8 on blue. The predicted translation adds nothing in the ordinary conditions (94.3, 88.6) and loses in the extreme ones (61.8, 41.4).
- Every number in rows (ii)-(v) uses a threshold set per condition at exactly 1% flood, which is itself an oracle. With no per-condition knob at all (Q6b: one radius per colour for all conditions, mean flood 1% over the ordinary conditions) the home log-chroma model scores 88.0 orange and 66.1 blue against 81.9 and 64.5 for the fixed rectangle: about the same. With the predicted common translation and one radius, blue rises to 80.1 (the tile goes from 0-80% to 95-100%) and orange falls to 80.4 (the tile under mid and warm lamp goes from 100% to 0-27%); the ottoman under mid and warm lamp stays at 0-18% for blue.
- Floors nobody reaches: `lampmid3_ottoman` (blue 6-8%, orange 69% by every method: the paint is under V 40), and blue on `lampwarm6_ottoman` (59-71%, 25% with the predicted per-class shift).

**So a physically shaped 2-parameter adaptation does not beat moving the HSV box edges on these data.** What separates the good rows from the fixed rectangle is (a) a per-condition threshold and (b) for blue, a region that tolerates low saturation. The 2-number translation is neither necessary (row iii) nor predictable enough (row v).

## Surprises

1. Nothing is clipped on the ottoman, and the camera does not brighten that scene: the stated mechanism for the hue shift there does not exist in the data.
2. Orange is the stable paint and blue the unstable one. Under the mid and warm lamp without daylight the blue body is a dark gray (R, G, B within 10 counts of each other) on tile, ottoman and wood alike.
3. The two paints move in opposite directions in log R/G, which is what defeats a common translation.
4. The body-minus-stripe difference is five times less stable than the absolute orange body colour, yet its sign with a margin of 0.3 never fails in 220 ordinary barrels.
5. The home log-chroma cluster with no adaptation still ranks barrel paint ahead of 99% of the background in most conditions (94% and 89% mean recall): the paints stay the nearest things to their home colour even when they have left the home box.
6. The stripe is at 0.46-0.67 of the box height, not at the middle, and lower in the box for close barrels.
7. On the gray table (`both_abpgray`) orange moves the other way: G falls to 22 (R 197, B 18), hue 1, log R/G 1.9. No other condition does this.
8. Unflagged barrels in the `top`, `topstripe`, `held` and `hand` scenes are not upright; "flags empty" does not mean "stripe at the usual place".

## Limits

- Small counts: 3 to 14 barrels per condition and colour, so "at least 95%" means "all of them" in nearly every cell; 25 conditions and 10 places for the predictions. `window_abpwhite` is 16 shots of the same few barrels.
- Train frames only, one robot camera, one set of barrels. Nothing here was checked on test frames.
- No camera metadata (exposure, gain, white-balance gains) is in the files; auto exposure and white balance are inferred from pixel statistics only. Surface is confounded with room, daylight, and where the lamp pointed, so "surface effect" is not "camera effect".
- Patches are the centre of the side wall. Edges, the lid, shadows under the barrel and occluded barrels are not covered; pixel recall is recall of patch pixels.
- Logs use an offset of 1 count; values near black (brightness 1, the ottoman at brightness 3) are dominated by noise and by that offset.
- Q6 rows (ii)-(v) use a per-condition threshold at exactly 1% flood; the lookup and the best rectangle are fitted and scored on the same pixels. The statistic selection in Q5 is nested, but the list of candidate statistics was written after seeing the conditions.
- The false-alarm rates in Q3 are per random triplet over mostly plain table; they are not the false-alarm rate of a detector that searches every position.
- With two paints, models richer than a translation (gains plus offsets, a full 3 x 3 matrix) cannot be tested; the cause of the blue paint's loss of colour and of the orange G/R change on the ottoman was not identified.
