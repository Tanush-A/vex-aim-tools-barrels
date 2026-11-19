# Worked examples: `all` against `base`

The barrel: HOME hand masks, `4A8B_window_light_core_02`, orange, hand-drawn box [368, 120, 418, 173] (50 wide, 53 tall).

## hidden from above, 50 % hidden

- full box of the hidden barrel: [368, 120, 418, 173]
- `base` draws: nothing
- `all` draws: [('orange', [368, 117, 417, 173], 'occluded+top_inferred')]
- found under the v2 rule: `base` False, `all` True; overlap of the best box with the full box: 0.93
- `half` kept: {'bbox': (368, 146, 417, 154), 'body': 1, 'box': (368, 117, 417, 173), 'hidden': 'top', 'seam': 154.0, 'distance_mm': 205.9, 'expected_w': 49.5, 'expected_h': 53.7, 'expected_stripe_h': 12.7, 'core_h': 7.0, 'predicted_top': 117.1, 'predicted_bottom': 170.9, 'tol': 8.1, 'seen_far_edge': 173, 'body_span': (368, 417)}

## hidden from below (a low thing in front), 50 % hidden

- full box of the hidden barrel: [368, 120, 418, 173]
- `base` draws: nothing
- `all` draws: [('orange', [368, 120, 418, 172], 'bottom_inferred+occluded')]
- found under the v2 rule: `base` False, `all` True; overlap of the best box with the full box: 0.98
- `half` kept: {'bbox': (368, 141, 418, 147), 'body': 1, 'box': (368, 120, 418, 172), 'hidden': 'bottom', 'seam': 142.0, 'distance_mm': 203.6, 'expected_w': 50.1, 'expected_h': 54.3, 'expected_stripe_h': 12.9, 'core_h': 5.0, 'predicted_top': 117.6, 'predicted_bottom': 171.9, 'tol': 8.2, 'seen_far_edge': 120, 'body_span': (368, 418)}

## a post across the middle, 50 % hidden

- full box of the hidden barrel: [368, 120, 418, 173]
- `base` draws: nothing
- `all` draws: [('orange', [368, 120, 418, 173], 'occluded')]
- found under the v2 rule: `base` False, `all` True; overlap of the best box with the full box: 1.00
- `pair` kept: {'bbox': (368, 141, 380, 153), 'body': 1, 'box': (368, 120, 418, 173), 'other': (405, 141, 416, 154), 'expected_w': 49.1, 'outer_span': 50}

## a barrel of the OTHER color, straight in front, 75 % hidden

- full box of the hidden barrel: [368, 120, 418, 173]; the barrel in front: blue [359, 128, 427, 205]
- `base` draws: [('blue', [360, 129, 427, 205])]
- `all` draws: [('blue', [360, 129, 427, 205], '')]
- found under the v2 rule: `base` False, `all` False; overlap of the best box with the full box: 0.00

## a barrel of the SAME color, beside it, 50 % hidden

- full box of the hidden barrel: [368, 120, 418, 173]; the barrel in front: orange [340, 124, 393, 178]
- `base` draws: [('orange', [348, 120, 410, 178])]
- `all` draws: [('orange', [342, 121, 396, 178], 'occluded'), ('orange', [367, 120, 418, 178], 'occluded')]
- found under the v2 rule: `base` True, `all` True; overlap of the best box with the full box: 0.90

## a barrel of the SAME color, beside it and lower, 75 % hidden

- full box of the hidden barrel: [368, 120, 418, 173]; the barrel in front: orange [344, 129, 406, 194]
- `base` draws: [('orange', [346, 120, 418, 195])]
- `all` draws: [('orange', [346, 120, 418, 195], '')]
- found under the v2 rule: `base` False, `all` False; overlap of the best box with the full box: 0.49

