# Time per frame (26 ordinary train frames, one thread; setting: contrast path added to today's boxes: margin 0.5, share of the width 0.5, mean difference >= 1.15, guards: orange part reddish >= 0.8, top edge seen >= 0.15, bottom edge seen >= 0.15)

| piece | median ms | mean ms | max ms |
|---|---|---|---|
| fixed colors | 23 | 22 | 27 |
| today's detector | 58 | 71 | 142 |
| response | 47 | 46 | 56 |
| candidates | 4 | 3 | 4 |
| own colors and paint | 6 | 7 | 15 |
| detector, second run | 0 | 22 | 196 |
| whole path (cd.detect) | 139 | 165 | 355 |
| today's path (fixed colors + detector) | 82 | 93 | 168 |

The second detector run is needed on 4 of 26 frames (those where a candidate was painted).
