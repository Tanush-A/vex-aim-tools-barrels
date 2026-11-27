# The photo at the cut (analysis P; not a rule)

261 labelled train frames. D = the largest difference over blue, green and red (0 to 255) between the strip just beside a barrel's seen end and the table just below the barrel. Left out: 320 barrels with no stripe in the mask, 27 whose bottom is not seen.

## The sides hidden by a thing that is not a barrel: 18

| frame | barrel | side | D |
|---|---|---|---|
| both_abpgray_occl_02 | blue [366, 123, 422, 181] | left | 30 |
| campus_light_occl_02 | blue [275, 123, 328, 180] | right | 152 |
| lampcool6_glass_clutter_01 | blue [254, 114, 300, 163] | left | 146 |
| lampcool6_glass_occl_02 | blue [254, 114, 300, 163] | left | 143 |
| lampcool6_ottoman_occl_02 | orange [225, 125, 286, 192] | right | 128 |
| lampmid3_glass_clutter_01 | blue [254, 114, 300, 163] | left | 140 |
| lampmid3_glass_occl_02 | blue [254, 114, 300, 163] | left | 138 |
| lampmid6_glass_clutter_01 | blue [254, 114, 300, 163] | left | 144 |
| lampmid6_glass_occl_02 | blue [254, 114, 300, 163] | left | 136 |
| lampwarm6_glass_clutter_01 | blue [254, 114, 300, 163] | left | 144 |
| lampwarm6_glass_occl_02 | blue [254, 114, 300, 163] | left | 130 |
| overheaddim_palewood_occl_02 | orange [344, 115, 388, 162] | left | 60 |
| window_abpwhite_occlx_01 | orange [103, 120, 153, 172] | left | 146 |
| window_abpwhite_occlx_02 | orange [92, 119, 143, 170] | left | 17 |
| window_abpwhite_occlx_03 | orange [99, 120, 152, 172] | right | 178 |
| window_abpwhite_occlx_04 | orange [98, 119, 151, 174] | right | 146 |
| window_glass_clutter_01 | blue [254, 114, 300, 163] | left | 148 |
| window_glass_occl_02 | blue [254, 114, 300, 163] | left | 144 |

The smallest D of a hidden side: **17**.

## The free sides (barrels with no flag), by place

| place | sides | median D | 90 % | 99 % | max | at or above 17 |
|---|---|---|---|---|---|---|
| abp_gray | 8 | 89 | 139 | 151 | 152 | 8 |
| abp_white | 34 | 35 | 102 | 142 | 150 | 28 |
| campus_study | 57 | 44 | 133 | 154 | 166 | 51 |
| home_bathtile | 18 | 53 | 133 | 152 | 154 | 17 |
| home_black | 12 | 56 | 209 | 216 | 216 | 8 |
| home_glass | 100 | 59 | 160 | 175 | 177 | 91 |
| home_ottoman | 16 | 6 | 97 | 108 | 108 | 4 |
| home_white | 38 | 69 | 137 | 147 | 150 | 30 |
| home_wooddesk | 4 | 122 | 122 | 122 | 122 | 4 |
| uc_palewood | 8 | 41 | 80 | 95 | 96 | 8 |
| **all places** | 295 | 44 | 143 | 177 | 216 | 249 |
| all places, no other barrel beside | 225 | 35 | 124 | 179 | 216 | 182 |
| ordinary places only | 279 | 44 | 142 | 169 | 177 | 237 |
| ordinary places, no other barrel beside | 212 | 35 | 119 | 170 | 177 | 173 |

## The other sides of the flagged barrels: 50 (the free side of a hidden barrel, a barrel in front, the frame)

| frame | barrel | flags | side | D | another barrel beside |
|---|---|---|---|---|---|
| window_abpwhite_occlx_01 | orange [103, 120, 153, 172] | occluded | right | 42 |  |
| window_abpwhite_occlx_02 | orange [92, 119, 143, 170] | occluded | right | 143 |  |
| window_abpwhite_occlx_03 | orange [99, 120, 152, 172] | occluded | left | 35 |  |
| window_abpwhite_occlx_04 | orange [98, 119, 151, 174] | occluded | left | 73 |  |
| window_abpwhite_occlx_05 | orange [46, 118, 98, 170] | occluded | left | 129 |  |
| window_abpwhite_occlx_05 | orange [46, 118, 98, 170] | occluded | right | 146 |  |
| window_abpwhite_occlx_09 | blue [106, 114, 152, 164] | occluded | left | 21 |  |
| window_abpwhite_occlx_09 | blue [106, 114, 152, 164] | occluded | right | 128 | yes |
| window_abpwhite_occlx_10 | orange [99, 118, 148, 168] | bottom_estimated+occluded | left | 30 |  |
| window_abpwhite_occlx_10 | orange [99, 118, 148, 168] | bottom_estimated+occluded | right | 16 | yes |
| window_abpwhite_occlx_18 | blue [311, 134, 381, 210] | occluded | left | 64 |  |
| window_abpwhite_occlx_18 | blue [311, 134, 381, 210] | occluded | right | 33 |  |
