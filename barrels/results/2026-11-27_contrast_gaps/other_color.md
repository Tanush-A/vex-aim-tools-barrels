# Group 5: an added contrast box on a barrel that has a box of the other color

Rule (gaps.Gaps.other): two boxes of different colors whose overlap is more than SHARE of the smaller box's area, at least one of them added by the contrast stage: two boxes of about the same height (within 1.25x): the added one is dropped when the stripe pattern supports the other color better (gaps.pattern_support: the signed sandwich score at the stripe row its bottom predicts; on a near tie, under 0.25 apart, gaps.color_support in the fixed mask). Today's default, every train frame (ordinary, extreme, excluded) and Dave's 12 office frames (in no split; indicative, his labels group touching barrels).

| share | frame | dropped box | color | source | the other box (box, color, source, overlap) | on a labelled barrel of its color | real barrel lost |
|---|---|---|---|---|---|---|---|
| 0.4 | 4A8B_lampwarm6_bathtile_core_01 | (465, 104, 495, 134) | orange | contrast | [((476, 111, 513, 146), 2, 'contrast', 0.49)] | no | no |
| 0.3 | 4A8B_lampwarm6_bathtile_core_01 | (465, 104, 495, 134) | orange | contrast | [((476, 111, 513, 146), 2, 'contrast', 0.49)] | no | no |
| 0.5 | 4A8B_lampmid6_wood_occl_04 | (181, 139, 261, 232) | orange | contrast | [((182, 148, 264, 243), 2, 'contrast', 0.89)] | [(178, 128, 238, 186)] | [(178, 128, 238, 186)] |
| 0.4 | 4A8B_lampmid6_wood_occl_04 | (181, 139, 261, 232) | orange | contrast | [((182, 148, 264, 243), 2, 'contrast', 0.89)] | [(178, 128, 238, 186)] | [(178, 128, 238, 186)] |
| 0.3 | 4A8B_lampmid6_wood_occl_04 | (181, 139, 261, 232) | orange | contrast | [((182, 148, 264, 243), 2, 'contrast', 0.89)] | [(178, 128, 238, 186)] | [(178, 128, 238, 186)] |
| 0.5 | 4A8B_lampwarm6_wood_cluster_01 | (209, 129, 269, 193) | orange | contrast | [((221, 125, 268, 182), 2, 'contrast', 0.93)] | no | no |
| 0.4 | 4A8B_lampwarm6_wood_cluster_01 | (209, 129, 269, 193) | orange | contrast | [((221, 125, 268, 182), 2, 'contrast', 0.93)] | no | no |
| 0.3 | 4A8B_lampwarm6_wood_cluster_01 | (209, 129, 269, 193) | orange | contrast | [((221, 125, 268, 182), 2, 'contrast', 0.93)] | no | no |
| 0.5 | DAVE_office_speckle_snap_07 | (195, 107, 242, 159) | blue | contrast | [((192, 119, 244, 174), 1, 'contrast', 0.77)] | no | no |
| 0.4 | DAVE_office_speckle_snap_07 | (195, 107, 242, 159) | blue | contrast | [((192, 119, 244, 174), 1, 'contrast', 0.77)] | no | no |
| 0.3 | DAVE_office_speckle_snap_07 | (195, 107, 242, 159) | blue | contrast | [((192, 119, 244, 174), 1, 'contrast', 0.77)] | no | no |

| share | set | frames | boxes dropped | of them on a labelled barrel of their color | real barrels lost |
|---|---|---|---|---|---|
| 0.5 | ordinary | 154 | 0 | 0 | 0 |
| 0.5 | extreme | 77 | 2 | 1 | 1 |
| 0.5 | excluded | 30 | 0 | 0 | 0 |
| 0.5 | Dave office | 12 | 1 | 0 | 0 |
| 0.4 | ordinary | 154 | 1 | 0 | 0 |
| 0.4 | extreme | 77 | 2 | 1 | 1 |
| 0.4 | excluded | 30 | 0 | 0 | 0 |
| 0.4 | Dave office | 12 | 1 | 0 | 0 |
| 0.3 | ordinary | 154 | 1 | 0 | 0 |
| 0.3 | extreme | 77 | 2 | 1 | 1 |
| 0.3 | excluded | 30 | 0 | 0 | 0 |
| 0.3 | Dave office | 12 | 1 | 0 | 0 |
