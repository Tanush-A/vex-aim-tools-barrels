# Vendor files: validation

| subset | pairs | IoU | IoU if center | w ratio | h ratio | left | top | right | bottom | center x | center y |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all pairs | 106 | 0.81 | 0.12 | 1.06 | 1.09 | -2.5 | -5.0 | +3.0 | +1.0 | +0.5 | -2.5 |
| free-standing | 74 | 0.82 | 0.12 | 1.07 | 1.09 | -3.0 | -6.0 | +3.0 | +2.0 | +0.5 | -2.5 |
| hidden (occluded) | 18 | 0.69 | 0.11 | 0.96 | 1.07 | -2.0 | -5.0 | +0.5 | +0.0 | -1.0 | -2.5 |
| cut by the frame (truncated) | 14 | 0.86 | 0.13 | 1.02 | 1.01 | +0.0 | -3.0 | +1.0 | -2.5 | +0.8 | -3.5 |
| free, both_abpgray | 10 | 0.79 | 0.11 | 1.11 | 1.13 | -3.5 | -6.5 | +3.5 | +2.5 | +0.0 | -1.5 |
| free, lampcool6_ottoman | 10 | 0.84 | 0.12 | 1.02 | 1.12 | -2.5 | -7.0 | +1.0 | +2.0 | -0.2 | -3.2 |
| free, lampmid3_ottoman | 8 | 0.83 | 0.14 | 0.96 | 1.06 | +4.5 | -6.0 | +1.0 | -0.5 | +2.8 | -3.5 |
| free, lampmid6_ottoman | 10 | 0.81 | 0.12 | 1.10 | 1.06 | -3.5 | -5.0 | +4.0 | +0.5 | -0.2 | -3.5 |
| free, lampwarm6_ottoman | 9 | 0.83 | 0.12 | 1.14 | 1.09 | -4.0 | -6.0 | +3.0 | +1.0 | -1.0 | -3.0 |
| free, overheaddim_palewood | 10 | 0.73 | 0.11 | 1.17 | 1.11 | -4.5 | -5.0 | +4.0 | +1.0 | +0.2 | -2.2 |
| free, window_abpwhite | 17 | 0.83 | 0.12 | 1.06 | 1.09 | -1.0 | -5.0 | +3.0 | +2.0 | +0.5 | -1.5 |

Center fit, hand box center px = slope x vendor raw center (320x240 units) + offset (free barrels): x {'n': 74, 'slope': 1.9903911798823768, 'intercept': 1.2996812538162685, 'resid_med_abs': 1.1231128202328478}, y {'n': 74, 'slope': 2.0331888003320984, 'intercept': -0.17541263292010803, 'resid_med_abs': 0.8615778072655189}.
Offsets are vendor minus hand, px (negative top = the vendor box starts higher). Medians.
