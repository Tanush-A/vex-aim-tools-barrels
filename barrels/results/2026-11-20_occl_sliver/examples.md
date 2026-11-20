# Worked examples, one per rule (numbers from the masks; train frames only)

## `stripe_bridge` (off): HOME `edge_01`, blue (0, 133, 34, 198), one stripe break 0.1 W (seed 12)

- Expected at the stripe's row: W 64.0 px, stripe height 16.2 px.
- Stripe pieces before: [(0, 160, 14, 177), (17, 154, 30, 175)]; boxes of its color: []
- With the bridge: [(0, 154, 30, 177)]; boxes of its color: [(0, 133, 34, 198)]

## `stripe_bridge` (off): HOME `cluster_02`, orange (390, 116, 432, 163), a patch 0.06 W (what round 2's same-rows test refuses) (seed 1)

- Expected at the stripe's row: W 42.5 px, stripe height 11.0 px.
- Stripe pieces before: [(391, 121, 410, 146), (413, 135, 429, 147)]; boxes of its color: [(306, 119, 357, 170), (371, 116, 413, 161)]
- With the bridge: [(391, 121, 410, 146), (413, 135, 429, 147)]; boxes of its color: [(306, 119, 357, 170), (371, 116, 413, 161)]

## `thin_span`: HOME `close_01`, orange (302, 143, 390, 235), scorecard 'block/other' 75 % from the right

- Stripe piece (306, 182, 324, 204) (18 px wide, thin: True); its row 192.5 → W 80.7, H 86.7, predicted top 139.8, bottom 226.5.
- The body joined to the piece (the barrel's upper body above the block) spans the barrel's width; no column of it holds body color across the stripe's rows.
- Before: no box. After: (305, 143, 384, 231), overlap with the truth 0.86.

## `thin_frame`: HOME `cluster_02`, orange (0, 119, 11, 170), scorecard 'frame' 75 % from the left

- Stripe piece (0, 141, 11, 154) (11 px wide, thin: True); its row 147.5 → W 49.4, H 53.6, predicted top 117.1, bottom 170.7.
- Before: no box. After: (0, 120, 11, 169), overlap with the truth 0.96.

## `own_close`: HOME `cluster_02`, blue (443, 122, 500, 179), scorecard 'edge' 75 % from the left

- Stripe piece (486, 147, 496, 159) (10 px wide, thin: True); its row 153.5 → W 53.6, H 58.1, predicted top 120.2, bottom 178.3.
- Seen columns 486–499; closure left -0.001 H, right 0.174 H (own needs ≥ 0.15, the other ≤ 0.1).
- Before: no box. After: (445, 124, 499, 179), overlap with the truth 0.91.

