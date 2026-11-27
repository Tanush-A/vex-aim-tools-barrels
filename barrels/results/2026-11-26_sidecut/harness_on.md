# The proof harness's masks with the flag on

5435 masks (damage 666, hand 45, pool 53, real 261, real_dilate 261, real_erode 261, scene 3888), each run with `centred` (today), `own_side` and `own_side+centred`. A box's state is read against the frame's labels: found (strict) / off (on its barrel, fails strict) / second / wrong color / nothing. `scene` has no labels here; `sim.py` scores those kinds.

| group | arm | masks whose boxes differ from today | boxes | barrels found | box off | missed | boxes on nothing | second | wrong color |
|---|---|---|---|---|---|---|---|---|---|
| damage | `centred` | 0 of 666 | 816 | 803 | 6 | 343 | 0 | 0 | 7 |
| damage | `own_side` | 57 of 666 | 807 | 792 | 7 | 353 | 1 | 0 | 7 |
| damage | `own_side+centred` | 39 of 666 | 825 | 810 | 7 | 335 | 1 | 0 | 7 |
| hand | `centred` | 0 of 45 | 118 | 115 | 2 | 18 | 0 | 0 | 1 |
| hand | `own_side` | 4 of 45 | 117 | 115 | 2 | 18 | 0 | 0 | 0 |
| hand | `own_side+centred` | 2 of 45 | 118 | 115 | 2 | 18 | 0 | 0 | 1 |
| pool | `centred` | 0 of 53 | 91 | 91 | 0 | 2 | 0 | 0 | 0 |
| pool | `own_side` | 1 of 53 | 90 | 90 | 0 | 3 | 0 | 0 | 0 |
| pool | `own_side+centred` | 0 of 53 | 91 | 91 | 0 | 2 | 0 | 0 | 0 |
| real | `centred` | 0 of 261 | 239 | 224 | 6 | 307 | 5 | 0 | 4 |
| real | `own_side` | 9 of 261 | 243 | 227 | 7 | 303 | 4 | 1 | 4 |
| real | `own_side+centred` | 7 of 261 | 245 | 228 | 7 | 302 | 5 | 1 | 4 |
| real_dilate | `centred` | 0 of 261 | 267 | 234 | 15 | 288 | 15 | 1 | 2 |
| real_dilate | `own_side` | 9 of 261 | 267 | 234 | 16 | 287 | 14 | 1 | 2 |
| real_dilate | `own_side+centred` | 5 of 261 | 271 | 236 | 16 | 285 | 16 | 1 | 2 |
| real_erode | `centred` | 0 of 261 | 184 | 181 | 1 | 355 | 0 | 0 | 2 |
| real_erode | `own_side` | 5 of 261 | 185 | 182 | 1 | 354 | 0 | 0 | 2 |
| real_erode | `own_side+centred` | 4 of 261 | 186 | 183 | 1 | 353 | 0 | 0 | 2 |
| scene | `centred` | 0 of 3888 | 4437 | - | - | - | - | - | - |
| scene | `own_side` | 601 of 3888 | 4618 | - | - | - | - | - | - |
| scene | `own_side+centred` | 484 of 3888 | 4732 | - | - | - | - | - | - |

## The new boxes on labelled masks, by the rule that drew them and their state

- `own_side`: damage hidden_side found 7, damage own_side found 20, damage own_side off 1, damage thin_own_side found 16, damage thin_own_side nothing 1, damage thin_own_side off 1, hand cap found 1, hand own_side found 2, real own_side found 2, real own_side second 1, real thin_own_side found 2, real thin_own_side nothing 1, real thin_own_side off 1, real_dilate own_side found 3, real_dilate thin_own_side nothing 1, real_dilate thin_own_side off 1, real_erode hidden_side found 1, real_erode own_side found 3, real_erode thin_own_side found 1
- `own_side+centred`: damage hidden_side found 7, damage own_side found 20, damage own_side off 1, damage thin_own_side found 16, damage thin_own_side nothing 1, damage thin_own_side off 1, hand own_side found 2, real own_side found 2, real own_side second 1, real thin_own_side found 2, real thin_own_side nothing 1, real thin_own_side off 1, real_dilate own_side found 3, real_dilate thin_own_side nothing 1, real_dilate thin_own_side off 1, real_erode hidden_side found 1, real_erode own_side found 3, real_erode thin_own_side found 1

## New boxes that are not on their barrel (every one)

- `own_side` damage/white tables, worst seen/2/HOME hand masks/4A8B_window_light_occl_02: orange (367, 118, 410, 152) by thin_own_side: nothing
- `own_side+centred` damage/white tables, worst seen/2/HOME hand masks/4A8B_window_light_occl_02: orange (367, 118, 410, 152) by thin_own_side: nothing
- `own_side` real/4A8B_lampwarm6_glass_clutter_01: orange (550, 117, 599, 172) by own_side: second
- `own_side+centred` real/4A8B_lampwarm6_glass_clutter_01: orange (550, 117, 599, 172) by own_side: second
- `own_side` real/4A8B_lampwarm6_glass_occl_02: orange (584, 123, 635, 167) by thin_own_side: nothing
- `own_side+centred` real/4A8B_lampwarm6_glass_occl_02: orange (584, 123, 635, 167) by thin_own_side: nothing
- `own_side` real_dilate/4A8B_lampwarm6_glass_occl_02: orange (548, 121, 599, 168) by thin_own_side: nothing
- `own_side+centred` real_dilate/4A8B_lampwarm6_glass_occl_02: orange (548, 121, 599, 168) by thin_own_side: nothing
