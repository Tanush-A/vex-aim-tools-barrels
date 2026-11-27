# The yardstick: "more paint, box disappears" on the ordinary train frames (337f04c)

`python barrels/experiments/2026-11-26_bottom/yardstick.py`. Today's detector (`DetConfig()`), no candidate rule. 154 ordinary train frames; test frames never opened. Counting: `counting.py` (found = the strict rule; "box off" = a box of the right color is on the barrel and fails the strict rule).

The color steps:

- `fixed`: the fixed color model (what runs today)
- `s20`: both saturation floors lowered by 20 (orange 140 -> 120, blue 113 -> 93)
- `s40`: both saturation floors lowered by 40 (orange 100, blue 73)
- `hue3`: both hue ranges widened by 3 at each end (orange 0-16, blue 100-122)
- `dil1`: the fixed model's mask with one pixel added around each color (3 x 3 dilation)
- `hand`: Tanush's hand thresholds: per condition the median of its slider labels (others keep the fixed model)

## 1. The count per color step

| color step | paint (x fixed) | found, placements | found, per frame | box off, per frame (placements) | missed | boxes not on their barrel (per arrangement) | on empty frames |
|---|---|---|---|---|---|---|---|
| `fixed` | 1.00 | 133.8 of 172 | 211 of 307 | 2 (1.2) | 94 | 5 (1.9) | 0 |
| `s20` | 1.29 | 133.6 of 172 | 209 of 307 | 8 (3.3) | 90 | 16 (7.3) | 3 |
| `s40` | 1.75 | 125.4 of 172 | 204 of 307 | 14 (7.0) | 89 | 27 (12.8) | 7 |
| `hue3` | 1.30 | 142.1 of 172 | 230 of 307 | 4 (1.9) | 73 | 11 (4.1) | 3 |
| `dil1` | 1.25 | 136.6 of 172 | 217 of 307 | 8 (4.3) | 82 | 16 (7.3) | 3 |
| `hand` | 0.95 | 156.8 of 172 | 281 of 307 | 4 (1.9) | 22 | 3 (1.5) | 2 |

## 2. THE YARDSTICK: boxes that are on their barrel and fail the strict rule

Per frame. "bottom only" = the overlap passes (IoU >= 0.5), the bottom edge is outside the scorer's tolerance. "bottom, and so the overlap" = both fail, and with the bottom put right the box would be a hit. low = the box ends below the true bottom, high = above. "other" = it would still fail with the bottom right.

| color step | box off | bottom only: low / high | bottom, and so the overlap: low / high | **the bottom edge is the cause** | other |
|---|---|---|---|---|---|
| `fixed` | 2 | 1 / 1 | 0 / 0 | **2** | 0 |
| `s20` | 8 | 4 / 3 | 0 / 0 | **7** | 1 |
| `s40` | 14 | 8 / 5 | 0 / 0 | **13** | 1 |
| `hue3` | 4 | 2 / 2 | 0 / 0 | **4** | 0 |
| `dil1` | 8 | 2 / 5 | 0 / 0 | **7** | 1 |
| `hand` | 4 | 1 / 3 | 0 / 0 | **4** | 0 |

## 3. Barrels found under the fixed model and not found under the color step ("more paint, the barrel is lost")

| color step | gained | lost | lost: box on the barrel, the bottom edge is the cause | lost: box on the barrel, other | lost: no box on it |
|---|---|---|---|---|---|
| `s20` | 6 | 8 | 6 | 0 | 2 |
| `s40` | 12 | 19 | 10 | 0 | 9 |
| `hue3` | 21 | 2 | 0 | 0 | 2 |
| `dil1` | 10 | 4 | 4 | 0 | 0 |
| `hand` | 71 | 1 | 0 | 0 | 1 |

## 4. The bottom-edge error of every box that is on a barrel (found or box off)

The box's bottom row minus the true one. Only true bottoms that say where the barrel stands: inside the frame and not flagged `bottom_estimated`. near = a true box at least 40 px tall, far = shorter. med / p90 = the median and the 90th percentile of the absolute error; signed = the median with its sign (+ = the box ends too low); outside = the share outside the scorer's tolerance (10 % of the true height, at least 3 px).

| color step | | boxes | med px | p90 px | signed px | med % of height | p90 % | outside |
|---|---|---|---|---|---|---|---|---|
| `fixed` | near | 176 | 1.0 | 3.0 | -1.0 | 1.9 | 5.4 | 1.1 % |
| `fixed` | far | 18 | 1.0 | 1.3 | +0.0 | 2.9 | 4.0 | 0.0 % |
| `s20` | near | 178 | 1.0 | 4.0 | +0.0 | 2.1 | 6.1 | 3.9 % |
| `s20` | far | 19 | 1.0 | 2.0 | +0.0 | 3.3 | 6.1 | 0.0 % |
| `s40` | near | 183 | 2.0 | 5.0 | +0.0 | 2.5 | 7.7 | 6.0 % |
| `s40` | far | 18 | 1.0 | 3.6 | +0.5 | 3.4 | 11.8 | 11.1 % |
| `hue3` | near | 195 | 1.0 | 3.0 | -1.0 | 1.9 | 5.6 | 1.0 % |
| `hue3` | far | 18 | 1.0 | 1.0 | +0.0 | 3.1 | 3.4 | 0.0 % |
| `dil1` | near | 184 | 1.0 | 3.7 | +0.0 | 1.9 | 6.1 | 3.8 % |
| `dil1` | far | 20 | 1.0 | 2.0 | +1.0 | 3.1 | 6.9 | 0.0 % |
| `hand` | near | 235 | 1.0 | 3.0 | -1.0 | 2.0 | 5.4 | 1.3 % |
| `hand` | far | 28 | 1.0 | 2.0 | +0.0 | 3.0 | 5.7 | 0.0 % |

## 5. Where the bad bottoms come from

The boxes of section 2 whose bottom edge is the cause, by the rule that drew them and by whether the drawn bottom was a seen one or the predicted one (flag `bottom_inferred`).

| color step | rule: seen bottom / predicted bottom |
|---|---|
| `fixed` | body_span 1 / 0; whole_stripe 1 / 0 |
| `s20` | body_span 2 / 0; half_stripe 1 / 0; hidden_side 1 / 2; whole_stripe 1 / 0 |
| `s40` | body_span 1 / 0; half_stripe 0 / 2; hidden_side 4 / 2; whole_stripe 4 / 0 |
| `hue3` | body_span 2 / 0; hidden_side 1 / 0; whole_stripe 1 / 0 |
| `dil1` | centred 1 / 0; hidden_side 0 / 2; thin_span 1 / 0; whole_stripe 2 / 1 |
| `hand` | hidden_side 3 / 0; whole_stripe 1 / 0 |

For the stripe boxes among them (seen bottom drawn): three rows. seen - predicted = how far the painted bottom is below the bottom the stripe's row predicts; predicted - true = how good the prediction was; both as a share of the predicted height (the detector's "agrees" is 15 %) and of the true height.

| color step | boxes | seen bottom below the predicted one: median, range (% of height) | predicted bottom minus true bottom: median, range (% of true height) | would the predicted bottom pass the scorer |
|---|---|---|---|---|
| `fixed` | 2 | 0.0, -10.1 to 10.1 | -1.6, -3.2 to 0.0 | 2 of 2 |
| `s20` | 4 | 10.1, -10.1 to 10.1 | 0.0, -3.2 to 0.0 | 4 of 4 |
| `s40` | 9 | 12.6, -10.1 to 14.2 | 0.0, -3.2 to 2.8 | 9 of 9 |
| `hue3` | 4 | -1.7, -14.4 to 10.4 | -4.4, -9.3 to 0.0 | 4 of 4 |
| `dil1` | 4 | 0.8, -14.8 to 10.1 | 0.2, -3.2 to 2.8 | 4 of 4 |
| `hand` | 4 | -4.1, -14.4 to 12.1 | -8.0, -11.1 to -0.3 | 3 of 4 |

## 6. The two readings of the bottom, on every stripe box that is on a barrel

For every box the stripe step drew that is on a barrel with a measurable true bottom: the seen bottom (the last row of body color under the stripe, as the detector walks it) and the bottom the stripe's row predicts, each against the true bottom. Absolute error, px and % of the true height; signed = the median with its sign (+ = too low).

| color step | | boxes | seen: med px / p90 px / signed / med % / p90 % | predicted: med px / p90 px / signed / med % / p90 % |
|---|---|---|---|---|
| `fixed` | near | 171 | 1.0 / 5.0 / +0.0 / 2.0 / 8.2 | 2.1 / 5.9 / -1.9 / 3.7 / 7.5 |
| `fixed` | far | 18 | 1.0 / 4.1 / +0.0 / 3.4 / 11.8 | 1.1 / 1.5 / +0.9 / 3.2 / 5.1 |
| `s20` | near | 173 | 2.0 / 8.8 / +0.0 / 2.4 / 17.5 | 2.1 / 5.3 / -2.1 / 3.7 / 7.4 |
| `s20` | far | 19 | 1.0 / 3.4 / +0.0 / 3.4 / 10.4 | 1.2 / 1.6 / +0.9 / 3.5 / 5.2 |
| `s40` | near | 178 | 2.0 / 12.3 / +1.0 / 3.4 / 28.1 | 2.4 / 5.9 / -2.1 / 3.9 / 8.2 |
| `s40` | far | 18 | 1.0 / 6.2 / +0.5 / 3.4 / 19.0 | 1.3 / 1.7 / +1.1 / 3.7 / 5.2 |
| `hue3` | near | 189 | 1.0 / 5.0 / +0.0 / 1.9 / 6.8 | 2.0 / 5.4 / -1.9 / 3.6 / 6.6 |
| `hue3` | far | 18 | 1.0 / 1.3 / +0.0 / 3.2 / 4.0 | 1.1 / 1.5 / +0.9 / 3.1 / 5.1 |
| `dil1` | near | 178 | 1.0 / 6.0 / +1.0 / 2.0 / 10.6 | 2.2 / 5.5 / -1.9 / 3.9 / 7.5 |
| `dil1` | far | 20 | 1.0 / 2.6 / +1.0 / 3.3 / 8.4 | 1.1 / 1.5 / +0.9 / 3.1 / 5.1 |
| `hand` | near | 229 | 1.0 / 5.2 / -1.0 / 2.0 / 9.3 | 2.2 / 5.9 / -2.2 / 3.6 / 7.2 |
| `hand` | far | 28 | 1.0 / 2.0 / +0.0 / 3.0 / 5.7 | 1.3 / 1.5 / +1.3 / 3.7 / 5.1 |

## 7. Five readings of the bottom, side by side

Stripe boxes on a barrel with a measurable true bottom and a SEEN top (not predicted, not at the frame top). The readings: `seen` = the last row of body color under the stripe; `stripe row` = the bottom the stripe's row predicts (the detector's prediction); `seen top + height` = the seen top plus the height the stripe's row predicts; `seen top and stripe row` = the stripe's row plus the seen distance from top to stripe, scaled by the barrel's proportions (no distance needed: the barrel is a rigid shape); `seen top + height from width` = the seen top plus the height of a barrel as wide as the box (only where the whole width is seen). Each cell: median / 90th percentile of the absolute error in % of the true height, the signed median in px, and the share outside the scorer's tolerance.

| color step | | boxes (with a width) | seen | stripe row | seen top + height | seen top and stripe row | seen top + height from width |
|---|---|---|---|---|---|---|---|
| `fixed` | near | 149 (118) | 2.0 / 8.0, +0.0 px, 8.7 % | 3.8 / 7.3, -2.0 px, 2.0 % | 3.2 / 8.7, +0.0 px, 6.0 % | 6.5 / 11.6, -4.0 px, 14.8 % | 5.5 / 12.3, -2.0 px, 20.3 % |
| `fixed` | far | 18 (15) | 3.4 / 11.8, +0.0 px, 11.1 % | 3.1 / 3.4, +1.0 px, 0.0 % | 10.8 / 13.8, +4.0 px, 55.6 % | 6.8 / 13.3, -1.5 px, 22.2 % | 8.6 / 20.7, +0.0 px, 40.0 % |
| `s20` | near | 141 (112) | 2.5 / 18.5, +0.0 px, 13.5 % | 3.8 / 7.7, -2.0 px, 3.5 % | 3.8 / 10.1, -1.0 px, 10.6 % | 6.4 / 11.5, -4.0 px, 15.6 % | 5.4 / 12.2, -2.0 px, 18.8 % |
| `s20` | far | 17 (16) | 3.4 / 13.6, +0.0 px, 11.8 % | 3.0 / 4.2, +1.0 px, 0.0 % | 6.9 / 13.4, +2.0 px, 35.3 % | 6.5 / 13.8, -1.0 px, 23.5 % | 7.5 / 23.1, -0.5 px, 25.0 % |
| `s40` | near | 138 (109) | 3.2 / 29.7, +1.0 px, 21.7 % | 3.9 / 7.8, -2.0 px, 2.9 % | 3.8 / 11.5, -1.0 px, 12.3 % | 6.3 / 11.3, -3.5 px, 15.2 % | 5.0 / 12.3, -2.0 px, 17.4 % |
| `s40` | far | 14 (13) | 3.4 / 22.0, +0.0 px, 28.6 % | 2.9 / 4.7, +1.0 px, 0.0 % | 8.8 / 12.6, +2.5 px, 28.6 % | 6.8 / 12.8, -1.0 px, 21.4 % | 8.1 / 23.1, +0.0 px, 38.5 % |
| `hue3` | near | 166 (133) | 1.9 / 7.6, +0.0 px, 7.8 % | 3.6 / 6.8, -2.0 px, 1.8 % | 3.2 / 8.6, +0.0 px, 6.0 % | 6.3 / 11.2, -4.0 px, 13.9 % | 5.5 / 13.0, -2.0 px, 20.3 % |
| `hue3` | far | 16 (14) | 3.1 / 4.4, -0.5 px, 6.2 % | 2.9 / 3.4, +1.0 px, 0.0 % | 10.8 / 13.7, +4.0 px, 56.2 % | 6.8 / 12.0, -1.5 px, 18.8 % | 6.9 / 25.7, +0.0 px, 42.9 % |
| `dil1` | near | 152 (122) | 1.9 / 11.2, +1.0 px, 11.2 % | 3.8 / 7.2, -2.0 px, 3.9 % | 3.4 / 8.5, -1.0 px, 6.6 % | 5.4 / 10.6, -3.0 px, 15.1 % | 5.1 / 12.7, -1.0 px, 18.0 % |
| `dil1` | far | 18 (18) | 3.2 / 11.3, +1.0 px, 11.1 % | 2.9 / 3.4, +1.0 px, 0.0 % | 8.8 / 11.7, +3.0 px, 16.7 % | 3.4 / 10.5, -1.0 px, 16.7 % | 5.5 / 27.4, +0.5 px, 33.3 % |
| `hand` | near | 213 (168) | 2.0 / 9.4, -1.0 px, 8.9 % | 3.6 / 7.2, -2.0 px, 2.8 % | 3.4 / 8.8, +0.0 px, 8.0 % | 6.5 / 10.7, -4.0 px, 14.1 % | 5.3 / 13.0, -2.0 px, 19.6 % |
| `hand` | far | 28 (24) | 3.0 / 5.7, +0.0 px, 0.0 % | 3.0 / 3.4, +1.0 px, 0.0 % | 10.1 / 15.8, +3.5 px, 50.0 % | 6.1 / 9.5, -1.5 px, 7.1 % | 6.9 / 17.1, +0.5 px, 33.3 % |

Files: `yardstick.json` (every number), `yardstick_barrels.csv` (one line per true barrel per color step), `yardstick_boxes.json` (every box), `sheets/yardstick_*.png` (the boxes with a bad bottom, to look at).
