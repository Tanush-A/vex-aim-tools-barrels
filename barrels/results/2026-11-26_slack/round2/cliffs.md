# The cliffs, with and without slack=D (report only)

| arm | found (per frame) | boxes not on their barrel (per frame / per arrangement) | boxes on empty frames |
|---|---|---|---|
| slack=off defaults | 211 (133.8 placements) | 5 / 1.93 | 0 |
| slack=off min_width_px=12.8 | refused: a barrel 13.4 px wide has a stripe only 3.61 px tall (min_stripe_px = 4.0): with this came | | |
| slack=off min_stripe_px=4.8 | refused: a barrel 16.9 px wide has a stripe only 4.54 px tall (min_stripe_px = 4.8): with this came | | |
| slack=off height_max=1.2 | 211 (133.8 placements) | 5 / 1.93 | 0 |
| slack=D defaults | 214 (135.4 placements) | 5 / 1.93 | 0 |
| slack=D min_width_px=12.8 | refused: a barrel 13.4 px wide has a stripe only 3.61 px tall (min_stripe_px = 4.0): with this came | | |
| slack=D min_stripe_px=4.8 | refused: a barrel 16.9 px wide has a stripe only 4.54 px tall (min_stripe_px = 4.8): with this came | | |
| slack=D height_max=1.2 | 214 (135.4 placements) | 5 / 1.93 | 0 |
