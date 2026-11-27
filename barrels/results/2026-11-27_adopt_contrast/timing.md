# Time per frame, previous default against the new default

Made by `experiments/2026-11-27_adopt_contrast/timing.py`: 154 ordinary train frames, one thread, the fastest of three runs per frame.

| path | median ms | mean ms | 90th percentile ms | max ms |
|---|---:|---:|---:|---:|
| previous default (color step + detector) | 43 | 50 | 77 | 235 |
| new default (+ the stripe by contrast) | 76 | 93 | 156 | 306 |
| the contrast stage alone (difference) | 29 | 43 | 89 | 141 |

The second detector run (on the painted mask) happens on 30 of 154 frames: only when a candidate was painted.
