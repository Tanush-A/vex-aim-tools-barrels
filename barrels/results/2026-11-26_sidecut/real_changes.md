# Every box that changes on a real train frame

261 real train frames (every train frame that has an image; 261 have a box label). Frames whose boxes differ from today: `own_side` 9, `own_side+centred` 7. One contact sheet per changed frame in `sheets/`.

State of a box against the labels: found (strict) / off (on its barrel, fails strict) / second / wrong_color / nothing.

| frame | arm | what | box | rule | state | the barrel it is on |
|---|---|---|---|---|---|---|
| lampcool6_ottoman_occl_02 | `own_side` | new box | orange [200, 134, 260, 188] | thin_own_side | off | [[225, 125, 286, 192]] |
| lampcool6_ottoman_occl_02 | `own_side+centred` | new box | orange [200, 134, 260, 188] | thin_own_side | off | [[225, 125, 286, 192]] |
| lampmid6_glass_clutter_01 | `own_side` | box gone | orange [554, 117, 604, 171] | centred | nothing |  |
| lampwarm6_glass_clutter_01 | `own_side` | new box | orange [550, 117, 599, 172] | own_side | second | [[520, 118, 579, 169]] |
| lampwarm6_glass_clutter_01 | `own_side` | box gone | orange [555, 117, 605, 172] | centred | nothing |  |
| lampwarm6_glass_clutter_01 | `own_side+centred` | new box | orange [550, 117, 599, 172] | own_side | second | [[520, 118, 579, 169]] |
| lampwarm6_glass_clutter_01 | `own_side+centred` | box gone | orange [555, 117, 605, 172] | centred | nothing |  |
| lampwarm6_glass_occl_02 | `own_side` | new box | orange [584, 123, 635, 167] | thin_own_side | nothing |  |
| lampwarm6_glass_occl_02 | `own_side+centred` | new box | orange [584, 123, 635, 167] | thin_own_side | nothing |  |
| overheaddim_palewood_occl_02 | `own_side` | new box | orange [340, 115, 384, 160] | own_side | found | [[344, 115, 388, 162]] |
| overheaddim_palewood_occl_02 | `own_side+centred` | new box | orange [340, 115, 384, 160] | own_side | found | [[344, 115, 388, 162]] |
| window_abpwhite_occlx_02 | `own_side` | new box | orange [91, 122, 140, 171] | thin_own_side | found | [[92, 119, 143, 170]] |
| window_abpwhite_occlx_02 | `own_side+centred` | new box | orange [91, 122, 140, 171] | thin_own_side | found | [[92, 119, 143, 170]] |
| window_abpwhite_occlx_03 | `own_side` | new box | orange [101, 120, 151, 171] | own_side | found | [[99, 120, 152, 172]] |
| window_abpwhite_occlx_03 | `own_side+centred` | new box | orange [101, 120, 151, 171] | own_side | found | [[99, 120, 152, 172]] |
| window_black_occl_03 | `own_side` | new box | blue [272, 151, 373, 270] | thin_own_side | found | [[270, 157, 376, 275]] |
| window_black_occl_03 | `own_side+centred` | new box | blue [272, 151, 373, 270] | thin_own_side | found | [[270, 157, 376, 275]] |
| window_light_far_02 | `own_side` | box gone | orange [332, 107, 363, 135] | centred | found | [[333, 106, 363, 137]] |

Totals over all real train frames (per frame, not per placement):

| | today | `own_side` | `own_side+centred` |
|---|---|---|---|
| barrels found (strict) | 224 | 227 | 228 |
| barrels with the box off | 6 | 7 | 7 |
| barrels missed | 307 | 303 | 302 |
| boxes on nothing | 5 | 4 | 5 |
| second boxes | 0 | 1 | 1 |
| boxes of the wrong color | 4 | 4 | 4 |
