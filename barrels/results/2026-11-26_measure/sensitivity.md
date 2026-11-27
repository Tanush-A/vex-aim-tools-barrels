# How much the second accounting depends on the test for "on a barrel"

The measured ordinary conditions (frames with vendor files). Found is the strict rule in every row; only what happens to the boxes that fail it changes. Cells: per placement (per frame).

| test | ours found | ours box off | ours missed | ours wrong | ours 2nd | ours none | vendor found | vendor box off | vendor missed | vendor wrong | vendor 2nd | vendor none |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| chosen: half of the smaller box inside the other | 70.8 (148) | 1.2 (2) | 36.0 (93) | 0 | 0 | 5 | 83.3 (177) | 8.2 (23) | 16.5 (43) | 0 | 0 | 7 |
| overlap: IoU >= 0.5 | 70.8 (148) | 1.2 (2) | 36.0 (93) | 0 | 0 | 5 | 83.3 (177) | 6.4 (18) | 18.3 (48) | 0 | 0 | 12 |
| position: centers within half the true width | 70.8 (148) | 1.2 (2) | 36.0 (93) | 0 | 0 | 5 | 83.3 (177) | 8.2 (23) | 16.5 (43) | 0 | 0 | 7 |

Frames on which the chosen test and "position" give another state to a barrel or a box: 0. The two agree on every box of today's train frames.
