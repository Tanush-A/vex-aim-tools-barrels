# Camera calibration from the ruler set (TODO A4)

git 6503924. Data: the 12 ruler frames `4A8B_lampmid6_wood_calib_01` to `_12` with their hand-drawn boxes and `data/calib.csv`. They are in no split. No train or test frame is opened by this script.

## What is known, what is fit

| number | value | where it comes from | fit? |
|---|---|---|---|
| image size, centre | 640 × 480, centre (320, 240) | assumed (never measured) | no |
| barrel | 24 mm tall, 18 mm at lid and base, 25.5 mm at the bulge | tape measure, 2026-10-19 | no |
| focal length f | 400 px | `aim_fsm/camera.py`, an estimate | tried; the data cannot tell it from 400 |
| tilt | 22.25° (old), fit to boxes 2026-11-03 | no specification for this robot | **yes** |
| camera height | 43.47 mm | `aim_fsm/aim_kin.py` | **yes** (the ruler frames do not fit without it) |
| offset: camera behind the ruler's zero | 3 mm (camera 27 mm ahead of the centre, front edge at 30) | `aim_kin.py`, "approx" | **yes**, but it is not a camera number |

What a box gives: top row always (11 frames), bottom row when it is inside the frame (6 frames: 30 mm and further), width when both sides are inside the frame (11). 28 numbers in all. Frame 01 (0 mm) is left out: the barrel sits in the kicker, off the table, and its distance from the front edge is not the ruler's.
Error model: a box edge is drawn to 1.5 px; the barrel was placed to 1 mm. Close to the robot one millimetre is many pixels (top row: 5 px per mm at 10 mm; bottom row: 7 px per mm at 30 mm), so close frames count for little.
`weighted` = rms of residual / expected error: about 1 when the model fits as well as the error model allows.

## Which parameters are needed

| fitted | result | horizon row | rms px | weighted | 1-sigma from the fit |
|---|---|---|---|---|---|
| nothing (old camera, offset 3) | f 400.0, tilt 22.25, camera height 43.47, offset 3.00 | 76.4 | 14.0 | 3.67 | - |
| offset only (old camera) | f 400.0, tilt 22.25, camera height 43.47, offset 6.13 | 76.4 | 10.7 | 3.16 | offset ± 0.83 |
| tilt | f 400.0, tilt 22.01, camera height 43.47, offset 3.00 | 78.3 | 14.8 | 3.67 | tilt ± 0.26 |
| tilt + offset | f 400.0, tilt 21.55, camera height 43.47, offset 7.42 | 82.1 | 12.6 | 2.73 | tilt ± 0.21, offset ± 0.82 |
| f + tilt + offset | f 421.7, tilt 20.78, camera height 43.47, offset 10.03 | 80.0 | 12.5 | 2.75 | f ± 15.09, tilt ± 0.57, offset ± 2.03 |
| tilt + offset + camera height **(kept)** | f 400.0, tilt 20.39, camera height 40.21, offset 6.05 | 91.3 | 3.0 | 0.80 | tilt ± 0.09, offset ± 0.26, camera height ± 0.19 |
| f + tilt + offset + camera height | f 398.6, tilt 20.44, camera height 40.19, offset 5.88 | 91.5 | 3.0 | 0.81 | f ± 4.44, tilt ± 0.17, offset ± 0.61, camera height ± 0.20 |
| for the record: tilt + offset + barrel height | f 400.0, tilt 20.95, camera height 43.47, offset 5.95, barrel height 26.66 | 86.8 | 6.0 | 1.28 | tilt ± 0.12, offset ± 0.41, barrel height ± 0.26 |
| for the record: f + tilt + offset + barrel height | f 378.9, tilt 21.66, camera height 43.47, offset 3.08, barrel height 27.18 | 89.5 | 4.5 | 1.08 | f ± 6.64, tilt ± 0.26, offset ± 0.99, barrel height ± 0.28 |
| for the record: tilt + offset + centre row | f 400.0, tilt -0.96, camera height 43.47, offset 14.89, centre row 83.7 | 90.5 | 5.3 | 1.28 | tilt ± 2.23, offset ± 1.25, centre row ± 15.58 |

Kept: **tilt + offset + camera height**, the smallest set whose weighted rms is at most 1. With the camera height held at 43.47 mm no tilt, focal length and offset fit the frames: tops and bottoms miss in opposite directions. Letting the focal length go as well changes nothing (it comes back as 400 within its error).
A taller barrel or a moved centre row instead of a lower camera fit worse, and the centre row lands at an impossible value.
Rounded candidate: **f 400, tilt 20.40°, camera height 40.2 mm** (horizon row 91.2; old: 76.4), offset 6.0 mm. Rounded, its rms is 2.9 px, weighted 0.75.

## Residuals per frame: hand-drawn box minus model, px

`old` = old camera with the offset of 3 mm from `aim_kin.py`. `old, best offset` = old camera, offset fitted (6.1 mm), so that the old camera is not blamed for the offset. `new` = the rounded candidate.

| frame | mm | top: old | old, best offset | new | bottom: old | old, best offset | new | width: old | old, best offset | new |
|---|---|---|---|---|---|---|---|---|---|---|
| 01 | 0 | left out (in the kicker) | | | | | | | | |
| 02 | 10 | -32.7 | -15.3 | +1.5 | - | - | - | -6.6 | +21.9 | -0.0 |
| 03 | 10 | -34.7 | -17.3 | -0.5 | - | - | - | -0.6 | +27.9 | +6.0 |
| 04 | 15 | -27.1 | -13.4 | +0.9 | - | - | - | -9.8 | +12.9 | -2.5 |
| 05 | 20 | -26.0 | -14.9 | -2.7 | - | - | - | -10.1 | +7.8 | -3.5 |
| 06 | 25 | -19.8 | -10.6 | -0.3 | - | - | - | -5.6 | +8.8 | +0.2 |
| 07 | 30 | -16.5 | -8.8 | -0.1 | -16.1 | +7.2 | +9.5 | -7.4 | +4.4 | -2.4 |
| 08 | 50 | -10.5 | -6.1 | -2.4 | -7.1 | +5.0 | +6.8 | -6.8 | -0.6 | -3.6 |
| 09 | 100 | +0.1 | +1.8 | -1.0 | -0.4 | +3.8 | +1.4 | -3.8 | -1.6 | -2.3 |
| 10 | 150 | +4.8 | +5.7 | -0.2 | +3.8 | +5.9 | +0.7 | -2.2 | -1.1 | -1.2 |
| 11 | 200 | +6.9 | +7.5 | -0.3 | +7.7 | +9.0 | +1.9 | -1.1 | -0.4 | -0.4 |
| 12 | 300 | +9.0 | +9.3 | -0.6 | +8.4 | +9.0 | -0.3 | +0.0 | +0.4 | +0.5 |
| **rms** | all | 20.5 | 11.0 | 1.3 | 8.7 | 6.9 | 4.9 | 6.0 | 12.0 | 2.7 |
| **rms** | 100 mm and further | 6.2 | 6.7 | 0.6 | 6.0 | 7.3 | 1.2 | 2.3 | 1.0 | 1.3 |
| **rms** | nearer than 100 mm | 25.2 | 12.9 | 1.5 | 12.4 | 6.2 | 8.3 | 7.3 | 15.0 | 3.2 |

## How well each number is pinned

| number | fit | 1-sigma from the fit | range over 11 fits, one frame left out each | spread of 200 refits, boxes ± 1.5 px and placement ± 1 mm |
|---|---|---|---|---|
| tilt | 20.39 | 0.09 | 20.34 to 20.44 | ± 0.10 |
| offset | 6.05 | 0.26 | 5.97 to 6.13 | ± 0.42 |
| camera height | 40.21 | 0.19 | 40.15 to 40.26 | ± 0.14 |
| horizon row | 91.3 | - | 91.0 to 91.7 | ± 0.8 |

The same with the focal length free as well (four numbers):

| number | fit | 1-sigma from the fit | range, one frame left out | spread of 200 refits |
|---|---|---|---|---|
| f | 398.57 | 4.44 | 396.92 to 400.28 | ± 7.00 |
| tilt | 20.44 | 0.17 | 20.38 to 20.52 | ± 0.24 |
| offset | 5.88 | 0.61 | 5.70 to 6.06 | ± 0.96 |
| camera height | 40.19 | 0.20 | 40.10 to 40.24 | ± 0.18 |

Correlations in the four-number fit: f / tilt -0.84, f / offset +0.90, f / camera height +0.31, tilt / offset -0.76, tilt / camera height +0.14, offset / camera height +0.42. Focal length, tilt and offset trade against each other; holding f at 400 removes that.

## Does the answer depend on the choices made here

| change | tilt | camera height | offset | horizon row | weighted |
|---|---|---|---|---|---|
| as above | 20.39 | 40.21 | 6.05 | 91.3 | 0.80 |
| box edge 1 px, placement 0.5 mm | 20.39 | 40.21 | 6.02 | 91.3 | 1.39 |
| box edge 2 px, placement 2 mm | 20.39 | 40.20 | 6.10 | 91.3 | 0.48 |
| no placement error (every px counts the same) | 20.35 | 40.25 | 5.86 | 91.7 | 1.97 |
| rows only (no widths) | 20.17 | 39.10 | 3.67 | 93.0 | 0.49 |
| tops and widths only (no bottom rows) | 20.49 | 40.27 | 6.30 | 90.5 | 0.61 |
| 30 mm and further (6 frames) | 20.42 | 40.30 | 6.05 | 91.1 | 0.97 |
| 100 mm and further (4 frames) | 20.50 | 40.72 | 6.81 | 90.5 | 0.75 |
| nearer than 100 mm (7 frames) | 20.61 | 40.35 | 5.90 | 89.5 | 0.89 |
| frame 01 (in the kicker) included | 20.49 | 40.50 | 6.41 | 90.6 | 0.95 |

## Checks inside the image (no distance used): the 6 frames whose box is whole

What the detector does with a box: infer the bottom row from the top row, or from the width; and what the box tool's `g` draws: the expected width and height for a barrel whose bottom edge is at that row. px = inferred minus drawn (+ = inferred lower).

| frame | mm | bottom from top: old | new | bottom from width: old | new | width / expected: old | new | height / expected: old | new | width / exact outline, new |
|---|---|---|---|---|---|---|---|---|---|---|
| 07 | 30 | -32.9 | -9.9 | -44.1 | -47.4 | 0.87 | 0.86 | 1.05 | 1.01 | 0.96 |
| 08 | 50 | -21.7 | -14.4 | -26.3 | -27.9 | 0.89 | 0.89 | 1.05 | 1.03 | 0.95 |
| 09 | 100 | +0.8 | -4.2 | -10.0 | -7.4 | 0.94 | 0.95 | 1.00 | 1.02 | 0.97 |
| 10 | 150 | +8.1 | -1.3 | -7.3 | -2.1 | 0.94 | 0.98 | 0.95 | 1.01 | 0.97 |
| 11 | 200 | +9.1 | -2.7 | -7.9 | -1.0 | 0.92 | 0.99 | 0.93 | 1.02 | 0.97 |
| 12 | 300 | +13.0 | -1.3 | -5.9 | +3.1 | 0.92 | 1.06 | 0.87 | 1.01 | 1.02 |

The width the code expects is `f × 25.5 / distance`, with the horizontal distance. The pinhole divides by the depth along the tilted optical axis. The two agree near 16 cm; the shortcut is too narrow further out and too wide close up (new camera):

| barrel axis at | 40 mm | 60 mm | 100 mm | 150 mm | 200 mm | 300 mm | 400 mm |
|---|---|---|---|---|---|---|---|
| shortcut, px | 255 | 170 | 102 | 68 | 51 | 34 | 26 |
| exact outline, px | 224 | 157 | 99 | 68 | 52 | 35 | 27 |
| shortcut / exact | 1.14 | 1.08 | 1.03 | 1.00 | 0.98 | 0.97 | 0.96 |

## The horizon row without a camera model

The row of a point at a fixed height is `horizon + A / (distance + B)`, whatever the focal length, tilt and camera height are. Fitting that curve (three free numbers) separately to the box tops, the box bottoms and the tape's centimetre lines gives three independent readings of the horizon row. Misfit in px (weighted rms for the boxes).

| from | points | distance range | best horizon row | misfit there | rows within twice that misfit | misfit at 76.5 (old) | at 84 | at 91 (new) |
|---|---|---|---|---|---|---|---|---|
| box tops, known distances | 11 | 10 to 300 mm | 92.0 | 0.71 | 88.0 to 95.5 | 4.18 | 2.38 | 0.77 |
| box bottoms, known distances | 6 | 30 to 300 mm | 91.0 | 0.83 | 85.0 to 97.0 | 3.28 | 1.80 | 0.83 |
| tape centimetre lines (next section) | 8 | about 40 to 110 mm | 80.0 | 0.19 | 75.5 to 84.0 | 0.31 | 0.38 | 0.94 |

The tops and the bottoms each put the horizon near row 90 to 92 and rule out 76. The tape's lines, which only reach 11 cm, prefer a row near 80 and fit 91 less well (about 1 px). The two do not agree; see the reading under the tape section.

## The tape measure in the frames (a check that needs no box)

The tape lies on the table in every frame. Frames 09 to 12 are used (the barrel is far and does not cover it; the tape did not move).

**1. Where its two edges meet.** Parallel lines on the table meet on the horizon row.

| rows used | meeting row in frames 09, 10, 11, 12 | left edge rms px | right edge rms px |
|---|---|---|---|
| rows 250 to 477 (near half) | 83.8, 84.0, 82.8, 83.4 | 0.20 | 0.36 |
| rows 170 to 477 (all) | 90.6, 90.6, 89.6, 89.5 | 0.22 | 0.86 |
| rows 170 to 329 (far half) | 95.6, 94.6, 90.9, 91.9 | 0.23 | 0.71 |

The answer moves by about 10 rows with the rows used: the right edge is not straight (it carries the tick marks and bends by about 2 px). So the tape's edges say the horizon is somewhere between rows 82 and 96. Old camera: 76.4. New: 91.2.

**2. The centimetre lines.** Rows of the lines 142 cm down to 135 cm, read in the tape's left margin. A right camera reads 10 mm between neighbours.

| line | row | column | contrast | old camera: mm to the next line | new camera: mm to the next line |
|---|---|---|---|---|---|
| 142 | 402.0 | 394 | 65 | 10.0 | 9.9 |
| 141 | 357.1 | 384 | 46 | 10.1 | 10.3 |
| 140 | 322.6 | 376 | 25 | 10.0 | 10.3 |
| 139 | 296.0 | 370 | 21 | 9.7 | 10.2 |
| 138 | 275.0 | 365 | 22 | 10.2 | 10.9 |
| 137 | 257.0 | 361 | 16 | 9.7 | 10.5 |
| 136 | 242.6 | 358 | 6 | 9.7 | 10.7 |
| 135 | 230.3 | 354 | 4 | - | - |
| mean | | | | 9.93 | 10.39 |

Which horizon row makes the lines equally spaced (1 / (row − horizon) must be a straight line in distance, whatever f, tilt and height are). The tape is 35 to 70 px right of the centre column, so the answer is given for three camera rolls (it hardly moves: the tape's left margin heads for the centre column at the horizon, where a roll changes nothing):

| assumed roll | best horizon row | misfit there, px | horizon rows within twice that misfit | misfit at 76.5 | at 84 | at 91 |
|---|---|---|---|---|---|---|
| -2° | 80.0 | 0.19 | 75.5 to 84.0 | 0.31 | 0.38 | 0.94 |
| +0° | 80.0 | 0.19 | 75.5 to 84.0 | 0.31 | 0.38 | 0.94 |
| +2° | 80.0 | 0.19 | 75.5 to 84.0 | 0.31 | 0.38 | 0.94 |

Reading. The lines cover only rows 230 to 402, about 4 to 11 cm in front of the robot. There the old camera spaces them 10 mm apart (mean 9.93) and the new one 10.39: the new camera stretches near distances by about 4 %. The boxes say the opposite at 15 to 30 cm, where the old camera is 4 to 9 px off and the new one within 2 px.
So one pinhole camera with these numbers does not fit both the tape close up and the boxes far away to better than about 1 px. Things that could cause it, none of which these frames can separate: the tape is not flat (its lines bow by 1 to 2 px across its width, and its last line before the robot is visibly curved); the lens bends straight lines a little (the tape's right edge sags by 2 px); the hand-drawn top and bottom edges are not exactly the lid's far edge and the base's near edge.
The candidate is the fit to the boxes, because the detector's sizes are compared with hand-drawn boxes and the misfit that matters is the far one. What would settle it: the `horizon` frame that was not shot (a mark at camera height on a wall at least 1 m away), and the lens height above the table measured with a ruler (the fit says 40.2 mm, `aim_kin.py` says 43.47).
