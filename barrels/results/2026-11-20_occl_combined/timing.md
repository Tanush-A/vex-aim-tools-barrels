# Time per frame, detection only

37 HOME and CAMPUS train frames; one core; the fastest of three runs per frame; milliseconds. Segmentation (about 26 ms) is not in it.

| arm | median | 90th percentile | slowest frame |
|---|---|---|---|
| `before` | 15 | 27 | 33 |
| `stack` | 17 | 29 | 35 |
| `combined` | 25 | 38 | 44 |
| `reduced` | 25 | 38 | 53 |
| `reduced+thin` | 26 | 38 | 48 |
