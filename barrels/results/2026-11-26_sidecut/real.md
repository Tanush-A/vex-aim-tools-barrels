# The real occlusion set, barrel by barrel

The 18 train `occlx` frames. found = the strict rule. box off = a box of the right color is on the barrel but fails the strict rule. "centre off" = the box's centre is more than 10 % of the width from the true centre. In brackets: the rule that drew the box.

| frame | barrel | flags | today (`centred`) | `own_side` | `own_side+centred` |
|---|---|---|---|---|---|
| abpwhite_occlx_01 | orange [103, 120, 153, 172] | occluded | found [103, 122, 152, 173] (outline) | found [103, 122, 152, 173] (outline) | found [103, 122, 152, 173] (outline) |
| abpwhite_occlx_01 | blue [307, 120, 360, 176] |  | found [310, 123, 359, 177] (whole_stripe) | found [310, 123, 359, 177] (whole_stripe) | found [310, 123, 359, 177] (whole_stripe) |
| abpwhite_occlx_02 | orange [92, 119, 143, 170] | occluded | missed | found [91, 122, 140, 171] (thin_own_side) | found [91, 122, 140, 171] (thin_own_side) |
| abpwhite_occlx_02 | blue [307, 119, 359, 178] |  | found [310, 123, 358, 177] (whole_stripe) | found [310, 123, 358, 177] (whole_stripe) | found [310, 123, 358, 177] (whole_stripe) |
| abpwhite_occlx_03 | orange [99, 120, 152, 172] | occluded | missed | found [101, 120, 151, 171] (own_side) | found [101, 120, 151, 171] (own_side) |
| abpwhite_occlx_03 | blue [317, 132, 390, 211] |  | found [319, 132, 389, 211] (whole_stripe) | found [319, 132, 389, 211] (whole_stripe) | found [319, 132, 389, 211] (whole_stripe) |
| abpwhite_occlx_04 | orange [98, 119, 151, 174] | occluded | found [101, 121, 151, 172] (hidden_side) | found [101, 121, 151, 172] (hidden_side) | found [101, 121, 151, 172] (hidden_side) |
| abpwhite_occlx_04 | blue [317, 132, 389, 211] |  | found [320, 134, 388, 212] (whole_stripe) | found [320, 134, 388, 212] (whole_stripe) | found [320, 134, 388, 212] (whole_stripe) |
| abpwhite_occlx_05 | orange [46, 118, 98, 170] | occluded | found [50, 121, 99, 170] (body_span) | found [50, 121, 99, 170] (body_span) | found [50, 121, 99, 170] (body_span) |
| abpwhite_occlx_05 | blue [316, 133, 390, 212] |  | found [318, 130, 388, 211] (whole_stripe) | found [318, 130, 388, 211] (whole_stripe) | found [318, 130, 388, 211] (whole_stripe) |
| abpwhite_occlx_06 | orange [133, 115, 181, 160] | bottom_estimated+occluded | missed | missed | missed |
| abpwhite_occlx_06 | blue [317, 133, 389, 212] |  | found [320, 135, 388, 211] (whole_stripe) | found [320, 135, 388, 211] (whole_stripe) | found [320, 135, 388, 211] (whole_stripe) |
| abpwhite_occlx_07 | orange [108, 116, 159, 166] | bottom_estimated+occluded | found [111, 118, 156, 165] (half) | found [111, 118, 156, 165] (half) | found [111, 118, 156, 165] (half) |
| abpwhite_occlx_07 | blue [316, 132, 389, 211] |  | found [321, 135, 388, 211] (whole_stripe) | found [321, 135, 388, 211] (whole_stripe) | found [321, 135, 388, 211] (whole_stripe) |
| abpwhite_occlx_08 | orange [111, 114, 160, 164] | occluded | found [113, 115, 157, 166] (half) | found [113, 115, 157, 166] (half) | found [113, 115, 157, 166] (half) |
| abpwhite_occlx_08 | blue [317, 133, 390, 211] |  | found [321, 135, 388, 212] (whole_stripe) | found [321, 135, 388, 212] (whole_stripe) | found [321, 135, 388, 212] (whole_stripe) |
| abpwhite_occlx_09 | blue [106, 114, 152, 164] | occluded | found [107, 117, 153, 168] (hidden_side) | found [107, 117, 153, 168] (hidden_side) | found [107, 117, 153, 168] (hidden_side) |
| abpwhite_occlx_09 | blue [127, 118, 176, 169] |  | found [127, 118, 174, 168] (hidden_side) | found [127, 118, 174, 168] (hidden_side) | found [127, 118, 174, 168] (hidden_side) |
| abpwhite_occlx_10 | orange [99, 118, 148, 168] | bottom_estimated+occluded | missed [100, 118, 171, 197] (whole_stripe, centre off) | missed [100, 118, 171, 197] (whole_stripe, centre off) | missed [100, 118, 171, 197] (whole_stripe, centre off) |
| abpwhite_occlx_10 | orange [105, 130, 173, 197] |  | found [100, 118, 171, 197] (whole_stripe) | found [100, 118, 171, 197] (whole_stripe) | found [100, 118, 171, 197] (whole_stripe) |
| abpwhite_occlx_11 | blue [86, 141, 174, 230] |  | found [87, 136, 170, 230] (whole_stripe) | found [87, 136, 170, 230] (whole_stripe) | found [87, 136, 170, 230] (whole_stripe) |
| abpwhite_occlx_11 | orange [99, 117, 147, 169] | bottom_estimated+occluded | found [101, 118, 145, 166] (cap) | found [101, 118, 145, 166] (cap) | found [101, 118, 145, 166] (cap) |
| abpwhite_occlx_13 | orange [101, 118, 153, 166] |  | found [104, 118, 151, 165] (whole_stripe) | found [104, 118, 151, 165] (whole_stripe) | found [104, 118, 151, 165] (whole_stripe) |
| abpwhite_occlx_13 | blue [311, 133, 383, 210] |  | found [314, 132, 390, 211] (whole_stripe) | found [314, 132, 390, 211] (whole_stripe) | found [314, 132, 390, 211] (whole_stripe) |
| abpwhite_occlx_14 | orange [0, 120, 45, 179] | occluded+truncated | missed | missed | missed |
| abpwhite_occlx_14 | blue [190, 120, 244, 177] |  | found [192, 123, 242, 178] (whole_stripe) | found [192, 123, 242, 178] (whole_stripe) | found [192, 123, 242, 178] (whole_stripe) |
| abpwhite_occlx_17 | blue [0, 124, 19, 183] | truncated | found [0, 128, 16, 185] (thin_frame) | found [0, 128, 16, 185] (thin_frame) | found [0, 128, 16, 185] (thin_frame) |
| abpwhite_occlx_17 | blue [142, 115, 187, 161] |  | found [144, 117, 185, 160] (whole_stripe) | found [144, 117, 185, 160] (whole_stripe) | found [144, 117, 185, 160] (whole_stripe) |
| abpwhite_occlx_18 | orange [102, 118, 153, 166] |  | found [104, 119, 151, 166] (whole_stripe) | found [104, 119, 151, 166] (whole_stripe) | found [104, 119, 151, 166] (whole_stripe) |
| abpwhite_occlx_18 | blue [311, 134, 381, 210] | occluded | found [315, 134, 382, 213] (body_span) | found [315, 134, 382, 213] (body_span) | found [315, 134, 382, 213] (body_span) |
| abpwhite_occlx_19 | blue [27, 135, 108, 212] |  | found [25, 135, 107, 211] (whole_stripe) | found [25, 135, 107, 211] (whole_stripe) | found [25, 135, 107, 211] (whole_stripe) |
| abpwhite_occlx_19 | orange [232, 121, 288, 181] | bottom_estimated+occluded | missed | missed | missed |

| | today | `own_side` | `own_side+centred` |
|---|---|---|---|
| flagged barrels found, of 15 | 9 | 11 | 11 |
| all barrels found, of 32 | 26 | 28 | 28 |
| boxes not on their barrel | 0 | 0 | 0 |
