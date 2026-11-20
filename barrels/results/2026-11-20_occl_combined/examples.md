# Worked examples in numbers (for `walkthrough.md`)

## a barrel of the OTHER color, straight in front, 75 % hidden: `stack` → `combined`

- HOME hand masks, `window_light_core_01`, blue, full box [239, 123, 290, 178] (51 wide, 55 tall), variant ``; the barrel in front: orange [230, 133, 299, 210]
- `stack` draws: [('orange', [231, 134, 299, 212])]
- `combined` draws: [('orange', [231, 134, 299, 212], '', 'stripe step'), ('blue', [241, 123, 287, 173], 'bottom_inferred+occluded', 'caps_behind')]
- overlap of the best box with the full box: 0.82
- `cap` kept: {'bbox': (241, 123, 287, 136), 'body': 2, 'box': (241, 123, 287, 173)}
  - the cap's top row 123 → a barrel 178 mm away: W 57.3, H 62.0, upper body 28.5 tall, bottom 185.0; the cap is 46 wide (0.80 W) and 13 tall (0.46 of an upper body)

## a barrel of the SAME color, straight in front, 75 % hidden: `stack` → `combined`

- HOME hand masks, `window_light_close_02`, blue, full box [308, 141, 392, 231] (84 wide, 90 tall), variant ``; the barrel in front: blue [289, 165, 411, 294]
- `stack` draws: [('blue', [292, 160, 411, 294])]
- `combined` draws: [('blue', [292, 160, 411, 294], 'top_inferred', 'stripe step'), ('blue', [312, 141, 389, 226], 'bottom_inferred+occluded', 'caps_behind')]
- overlap of the best box with the full box: 0.87
- `cap` kept: {'bbox': (312, 141, 389, 160), 'body': 2, 'box': (312, 141, 389, 226)}
  - the cap's top row 141 → a barrel 124 mm away: W 82.3, H 88.4, upper body 43.7 tall, bottom 229.2; the cap is 77 wide (0.94 W) and 19 tall (0.44 of an upper body)

## a barrel of the SAME color, beside it and lower, 75 % hidden: `stack` → `combined`

- HOME hand masks, `window_light_cluster_02`, blue, full box [443, 122, 500, 179] (57 wide, 57 tall), variant `L`; the barrel in front: blue [416, 127, 486, 202]
- `stack` draws: [('blue', [418, 122, 488, 202])]
- `combined` draws: [('blue', [418, 122, 488, 202], '', 'stripe step'), ('blue', [442, 124, 496, 178], 'occluded', 'slices_behind')]
- overlap of the best box with the full box: 0.87
- `slice` kept: {'bbox': (487, 148, 496, 159), 'body': 2, 'box': (442, 124, 496, 178), 'expected_w': 53.6, 'seen': (487, 496), 'hidden_side': 'left', 'predicted_top': 120.2, 'predicted_bottom': 178.3}

## a post across the middle, 50 % hidden: `stack` → `combined`

- HOME hand masks, `window_light_close_01`, orange, full box [302, 143, 390, 235] (88 wide, 92 tall), variant ``
- `stack` draws: nothing
- `combined` draws: [('orange', [305, 143, 389, 231], 'occluded', 'post_pairs')]
- overlap of the best box with the full box: 0.91
- `pair` kept: {'bbox': (306, 182, 324, 204), 'body': 1, 'box': (305, 143, 389, 231), 'other': (368, 183, 385, 206), 'expected_w': 81.4, 'outer_span': 84}

## hidden from above, 50 % hidden: `stack` → `combined`

- HOME hand masks, `window_light_close_01`, orange, full box [302, 143, 390, 235] (88 wide, 92 tall), variant ``
- `stack` draws: nothing
- `combined` draws: [('orange', [303, 141, 389, 235], 'occluded+top_inferred', 'half_stripes')]
- overlap of the best box with the full box: 0.96
- `half` kept: {'bbox': (303, 189, 389, 207), 'body': 1, 'box': (303, 141, 389, 235), 'hidden': 'top', 'seam': 205.0, 'distance_mm': 123.8, 'expected_w': 82.4, 'expected_h': 88.5, 'expected_stripe_h': 20.3, 'core_h': 14.0, 'predicted_top': 141.0, 'predicted_bottom': 229.5, 'tol': 13.3, 'seen_far_edge': 235, 'body_span': (303, 389)}

## hidden from below (a low thing in front), 50 % hidden: `stack` → `combined`

- HOME hand masks, `window_light_close_01`, orange, full box [302, 143, 390, 235] (88 wide, 92 tall), variant ``
- `stack` draws: nothing
- `combined` draws: [('orange', [302, 143, 390, 230], 'bottom_inferred+occluded', 'half_stripes')]
- overlap of the best box with the full box: 0.95
- `half` kept: {'bbox': (302, 181, 390, 189), 'body': 1, 'box': (302, 143, 390, 230), 'hidden': 'bottom', 'seam': 185.0, 'distance_mm': 123.5, 'expected_w': 82.6, 'expected_h': 88.7, 'expected_stripe_h': 20.3, 'core_h': 5.0, 'predicted_top': 141.1, 'predicted_bottom': 229.8, 'tol': 13.3, 'seen_far_edge': 143, 'body_span': (302, 390)}

## a barrel of the SAME color, beside it, 50 % hidden: `stack` → `combined`

- HOME hand masks, `window_light_close_01`, orange, full box [302, 143, 390, 235] (88 wide, 92 tall), variant `R`; the barrel in front: orange [346, 151, 440, 244]
- `stack` draws: [('orange', [318, 143, 421, 246])]
- `combined` draws: [('orange', [305, 143, 388, 243], 'occluded', 'stripe step'), ('orange', [350, 145, 438, 246], 'occluded', 'stripe step')]
- overlap of the best box with the full box: 0.87

## a straight upright edge, one side, 50 % hidden: `stack` → `combined`

- HOME color model, `window_light_far_02`, blue, full box [433, 106, 468, 139] (35 wide, 33 tall), variant `L`
- `stack` draws: nothing
- `combined` draws: [('blue', [434, 107, 467, 140], 'occluded', 'stripe step')]
- overlap of the best box with the full box: 0.89

## a straight upright edge, one side, 75 % hidden: `combined` → `combined+thin`

- HOME hand masks, `window_light_close_01`, orange, full box [302, 143, 390, 235] (88 wide, 92 tall), variant `L`
- `combined` draws: nothing
- `combined+thin` draws: [('orange', [307, 145, 389, 231], 'occluded', 'stripe step')]
- overlap of the best box with the full box: 0.87
- thin stripe piece [368, 183, 385, 206]: its row 194.5 → 124 mm, W 82.1, H 88.2, top 140.7, bottom 228.9; seen columns 368 to 389 (0.26 W); limit 4.4 rows; cost of the left end 17.7 rows, of the right end 3.1 rows

## cut by the frame edge, 75 % hidden: `combined` → `combined+thin`

- no scene that the second arm finds and the first does not

