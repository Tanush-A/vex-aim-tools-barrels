# The verifier's limit (PREREG.md, "The stencil as a verifier")

git d7877b8. Rule detector: arm `reduced`. Masks: A1 16, A2 16, A4 10. Right boxes: A1 28, A2 28; made by `half_stripes`: 0.

The lowest stencil score at a right box of A1 and A2 is 0.182; **limit = that − 0.02 = 0.16** (rounded down to 0.01). Without the boxes of `half_stripes`: lowest 0.182, **limit2 = 0.16**.

The eight lowest right boxes:

| pool | frame | color | box | flags | drawn by | score |
|---|---|---|---|---|---|---|
| A2 | window_light_topstripe_01 | orange | [176, 242, 423, 480] | bottom_inferred+truncated | stripeless piece | 0.182 |
| A2 | window_light_edge_01 | blue | [0, 132, 32, 197] | occluded+truncated | stripe step | 0.212 |
| A1 | window_light_cluster_01 | orange | [314, 117, 363, 164] | bottom_inferred+occluded | caps_behind | 0.220 |
| A2 | window_light_occl_02 | orange | [399, 117, 439, 161] | bottom_inferred+occluded | caps_behind | 0.224 |
| A2 | window_light_cluster_01 | orange | [315, 118, 366, 162] | bottom_inferred+occluded | caps_behind | 0.226 |
| A2 | window_light_occl_01 | blue | [387, 112, 432, 158] | bottom_inferred+occluded | caps_behind | 0.231 |
| A1 | window_light_occl_01 | blue | [386, 115, 430, 160] | bottom_inferred+occluded | caps_behind | 0.232 |
| A1 | window_light_top_01 | orange | [163, 259, 452, 480] | truncated | stripeless piece | 0.234 |

Boxes that are not right (A1, A2), and every box on a negative frame (A4); they do not enter the limit:

- none
