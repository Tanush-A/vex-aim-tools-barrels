# The stencil as a checker of the rule detector's boxes (report only)

Every box the rule detector draws gets the stencil's score at its place (the best stencil place overlapping the box by half or more, same color). A veto at level t removes the boxes scoring under t. Each cell: boxes removed of boxes drawn. The pre-registered `veto` arm is the first column (-0.01: the lowest score of a right box on the calibration masks, minus 0.05). Nothing here was used to choose anything.

| boxes of the rule detector | veto -0.01 | veto 0.0 | veto 0.05 | veto 0.1 | veto 0.15 | veto 0.2 |
|---|---|---|---|---|---|---|
| scorecard: right | 9 of 3701 | 11 of 3701 | 35 of 3701 | 67 of 3701 | 142 of 3701 | 273 of 3701 |
| scorecard: on a barrel, box not right | 3 of 239 | 5 of 239 | 19 of 239 | 27 of 239 | 35 of 239 | 48 of 239 |
| scorecard: no barrel there | 3 of 45 | 3 of 45 | 27 of 45 | 32 of 45 | 37 of 45 | 39 of 45 |
| HOME: right | 0 of 28 | 0 of 28 | 0 of 28 | 0 of 28 | 0 of 28 | 1 of 28 |
| CAMPUS: right | 0 of 35 | 0 of 35 | 0 of 35 | 1 of 35 | 2 of 35 | 3 of 35 |
| BLACK (report only): right | 2 of 5 | 3 of 5 | 3 of 5 | 5 of 5 | 5 of 5 | 5 of 5 |
| BLACK (report only): on a barrel, box not right | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| WOOD (report only): right | 1 of 7 | 1 of 7 | 2 of 7 | 4 of 7 | 5 of 7 | 5 of 7 |
| WOOD (report only): no barrel there | 1 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| WOOD (report only): on a barrel, box not right | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |

On the scorecard a "right" box is right for a barrel that is partly hidden in most scenes, which is where the stencil scores low.

