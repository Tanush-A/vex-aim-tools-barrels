# The second pass of the collapse (2026-11-26): the numbers it quotes

Made by the two scripts in `experiments/2026-11-26_collapse/`. No frame is read by the first; the second reads the 5435
masks of the proof harness (train frames only, no test frame).

## The facts behind B13, B1 and C1 (`second_pass_margins.py`)

For each camera, and for the two main cameras with one number changed: every top row with every seen bottom row, through
the lines of stage 1 (`find_pieces`). Per line:

- **tallest piece**: the tallest box that gets to the height check, in heights of a barrel at its bottom row. The limit that
  was removed was 1.5 (B13).
- **too short**: pieces under `height_min` x that height, with a predicted bottom (never) and with none (the case the
  check is for).
- **thinnest stripe at the middle row**: of the pieces that are not close-ups. The rule that was removed kept a piece when
  this was under 4 px (B1). "under 4 px: 0" means it kept none.
- **stripe of the farthest barrel on the table**: what `on_the_table` asserts is at least 4 px.
- **stripe rows**: the rows (whole and half) where a barrel can have its stripe are one unbroken range (C1).

The four cameras the repo names, then the four corners of the measured camera range, at the default numbers. Then BOXFIT
(the detector's default) and NOMINAL with one number changed, to show how far each fact is from breaking.

```
BOXFIT                       default numbers: tallest piece 1.086 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 4.14 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.31 px | stripe rows: a distance from row 76.5 down without a gap: True
NOMINAL                      default numbers: tallest piece 1.094 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 4.16 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.35 px | stripe rows: a distance from row 70.5 down without a gap: True
AIM_4A8B6118                 default numbers: tallest piece 1.087 x H | too short with a predicted bottom 0, with none 1770 | not a close-up: thinnest stripe at the middle row 4.20 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.36 px | stripe rows: a distance from row 66.5 down without a gap: True
WORLDMAP_CURRENT             default numbers: tallest piece 1.089 x H | too short with a predicted bottom 0, with none 2080 | not a close-up: thinnest stripe at the middle row 4.31 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.39 px | stripe rows: a distance from row 64.5 down without a gap: True
corner f=355 tilt=21.50      default numbers: tallest piece 1.089 x H | too short with a predicted bottom 0, with none 2278 | not a close-up: thinnest stripe at the middle row 4.17 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.26 px | stripe rows: a distance from row 100.5 down without a gap: True
corner f=355 tilt=25.50      default numbers: tallest piece 1.086 x H | too short with a predicted bottom 0, with none 4753 | not a close-up: thinnest stripe at the middle row 4.33 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.48 px | stripe rows: a distance from row 71.0 down without a gap: True
corner f=405 tilt=21.50      default numbers: tallest piece 1.089 x H | too short with a predicted bottom 0, with none 946 | not a close-up: thinnest stripe at the middle row 4.12 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.27 px | stripe rows: a distance from row 80.5 down without a gap: True
corner f=405 tilt=25.50      default numbers: tallest piece 1.083 x H | too short with a predicted bottom 0, with none 3003 | not a close-up: thinnest stripe at the middle row 4.32 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.50 px | stripe rows: a distance from row 47.0 down without a gap: True
BOXFIT     bottom_tol=0.05: tallest piece 1.086 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 4.14 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.31 px | stripe rows: a distance from row 76.5 down without a gap: True
BOXFIT     bottom_tol=0.1: tallest piece 1.086 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 4.14 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.31 px | stripe rows: a distance from row 76.5 down without a gap: True
BOXFIT     bottom_tol=0.2: tallest piece 1.086 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 4.14 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.31 px | stripe rows: a distance from row 76.5 down without a gap: True
BOXFIT     bottom_tol=0.25: tallest piece 1.093 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 4.14 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.31 px | stripe rows: a distance from row 76.5 down without a gap: True
BOXFIT     bottom_tol=0.3: tallest piece 1.111 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 4.14 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.31 px | stripe rows: a distance from row 76.5 down without a gap: True
BOXFIT     bottom_tol=0.4: tallest piece 1.141 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 4.05 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.31 px | stripe rows: a distance from row 76.5 down without a gap: True
BOXFIT     bottom_tol=0.5: tallest piece 1.162 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 4.05 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.31 px | stripe rows: a distance from row 76.5 down without a gap: True
BOXFIT     bottom_tol_min_px=2: tallest piece 1.057 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 4.23 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.31 px | stripe rows: a distance from row 76.5 down without a gap: True
BOXFIT     bottom_tol_min_px=6: tallest piece 1.133 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 4.05 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.31 px | stripe rows: a distance from row 76.5 down without a gap: True
BOXFIT     bottom_tol_min_px=8: tallest piece 1.190 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 3.96 px, under 4 px: 1 | stripe of the farthest barrel on the table 4.31 px | stripe rows: a distance from row 76.5 down without a gap: True
BOXFIT     bottom_tol_min_px=12: tallest piece 1.278 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 3.86 px, under 4 px: 3 | stripe of the farthest barrel on the table 4.31 px | stripe rows: a distance from row 76.5 down without a gap: True
BOXFIT     min_width_px=10.0: tallest piece 1.133 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 2.66 px, under 4 px: 1572 | stripe of the farthest barrel on the table 2.71 px | stripe rows: a distance from row 76.5 down without a gap: True
BOXFIT     min_width_px=12.0: tallest piece 1.121 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 3.13 px, under 4 px: 1175 | stripe of the farthest barrel on the table 3.25 px | stripe rows: a distance from row 76.5 down without a gap: True
BOXFIT     min_width_px=14.0: tallest piece 1.104 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 3.59 px, under 4 px: 392 | stripe of the farthest barrel on the table 3.78 px | stripe rows: a distance from row 76.5 down without a gap: True
BOXFIT     min_width_px=20.0: tallest piece 1.073 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 5.23 px, under 4 px: 0 | stripe of the farthest barrel on the table 5.35 px | stripe rows: a distance from row 76.5 down without a gap: True
BOXFIT     height_min=0.3: tallest piece 1.086 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 4.14 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.31 px | stripe rows: a distance from row 76.5 down without a gap: True
BOXFIT     height_min=0.7: tallest piece 1.086 x H | too short with a predicted bottom 0, with none 1378 | not a close-up: thinnest stripe at the middle row 4.14 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.31 px | stripe rows: a distance from row 76.5 down without a gap: True
NOMINAL    bottom_tol=0.05: tallest piece 1.094 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 4.16 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.35 px | stripe rows: a distance from row 70.5 down without a gap: True
NOMINAL    bottom_tol=0.1: tallest piece 1.094 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 4.16 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.35 px | stripe rows: a distance from row 70.5 down without a gap: True
NOMINAL    bottom_tol=0.2: tallest piece 1.094 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 4.16 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.35 px | stripe rows: a distance from row 70.5 down without a gap: True
NOMINAL    bottom_tol=0.25: tallest piece 1.094 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 4.16 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.35 px | stripe rows: a distance from row 70.5 down without a gap: True
NOMINAL    bottom_tol=0.3: tallest piece 1.109 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 4.16 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.35 px | stripe rows: a distance from row 70.5 down without a gap: True
NOMINAL    bottom_tol=0.4: tallest piece 1.140 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 4.07 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.35 px | stripe rows: a distance from row 70.5 down without a gap: True
NOMINAL    bottom_tol=0.5: tallest piece 1.169 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 4.07 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.35 px | stripe rows: a distance from row 70.5 down without a gap: True
NOMINAL    bottom_tol_min_px=2: tallest piece 1.059 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 4.26 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.35 px | stripe rows: a distance from row 70.5 down without a gap: True
NOMINAL    bottom_tol_min_px=6: tallest piece 1.133 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 4.07 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.35 px | stripe rows: a distance from row 70.5 down without a gap: True
NOMINAL    bottom_tol_min_px=8: tallest piece 1.185 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 3.98 px, under 4 px: 1 | stripe of the farthest barrel on the table 4.35 px | stripe rows: a distance from row 70.5 down without a gap: True
NOMINAL    bottom_tol_min_px=12: tallest piece 1.273 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 3.89 px, under 4 px: 3 | stripe of the farthest barrel on the table 4.35 px | stripe rows: a distance from row 70.5 down without a gap: True
NOMINAL    min_width_px=10.0: tallest piece 1.125 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 2.69 px, under 4 px: 1595 | stripe of the farthest barrel on the table 2.74 px | stripe rows: a distance from row 70.5 down without a gap: True
NOMINAL    min_width_px=12.0: tallest piece 1.115 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 3.25 px, under 4 px: 1189 | stripe of the farthest barrel on the table 3.28 px | stripe rows: a distance from row 70.5 down without a gap: True
NOMINAL    min_width_px=14.0: tallest piece 1.094 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 3.80 px, under 4 px: 394 | stripe of the farthest barrel on the table 3.81 px | stripe rows: a distance from row 70.5 down without a gap: True
NOMINAL    min_width_px=20.0: tallest piece 1.070 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 5.26 px, under 4 px: 0 | stripe of the farthest barrel on the table 5.40 px | stripe rows: a distance from row 70.5 down without a gap: True
NOMINAL    height_min=0.3: tallest piece 1.094 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 4.16 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.35 px | stripe rows: a distance from row 70.5 down without a gap: True
NOMINAL    height_min=0.7: tallest piece 1.094 x H | too short with a predicted bottom 0, with none 1711 | not a close-up: thinnest stripe at the middle row 4.16 px, under 4 px: 0 | stripe of the farthest barrel on the table 4.35 px | stripe rows: a distance from row 70.5 down without a gap: True
```

Read: B13 holds everywhere tried (at most 1.28 x, with the tolerance floor at 12 px). B1 holds at the default numbers
for all eight cameras, by a small margin (4.12 px at the worst), and breaks with `min_width_px` at 14 or less or with the
tolerance floor at 8 px or more: the removed rule would then have kept far pieces with no stripe.

## B7 was not done (`second_pass_b7.py`)

Would the last stage (`drop_single_reading`) decide the same if it read the span stage 3 measured (`seen_span`) and did
not measure again? Per (group of masks, rule that placed the box, kept today, kept if it read the stage-3 span):

```
asked boxes by (group, rule, kept today, kept if it read seen_span):
   ('damage', 'body_span', True, True) 16
   ('damage', 'hidden_side', False, False) 1
   ('real', 'body_span', True, True) 2
   ('real', 'centred', False, False) 1
   ('real', 'hidden_side', False, False) 2
   ('real_dilate', 'body_span', False, True) 1
   ('real_dilate', 'body_span', True, True) 2
   ('real_dilate', 'centred', False, False) 3
   ('real_erode', 'body_span', True, True) 1
   ('scene', 'body_span', False, True) 2
   ('scene', 'centred', False, False) 7
   ('scene', 'hidden_side', False, False) 5
the two measurements: {('same span', 'same W'): 7, ('same span', 'W differs'): 22, ('span differs', 'W differs'): 10, ('span differs', 'same W'): 4}
verdicts that differ: 3
   ('real_dilate/4A8B_window_black_touch_02', 'body_span', (239, 133, 298, 211), False, True)
   ('scene/CAMPUS color model/01765/barrel_low/same/0.75/L', 'body_span', (242, 108, 274, 149), False, True)
   ('scene/HOME color model/00119/barrel_side/other/0.75/R', 'body_span', (315, 127, 382, 196), False, True)
```

43 boxes are asked on the 5435 masks; 3 get the other answer. Stage 3 says their body shows the whole width (rule
"body_span"); the last stage, with its own row and without leaving out other stripes' columns, measures under 0.8 W
and drops them. Reading the stage-3 span would keep those 3 boxes: a change of boxes, so B7 stays an experiment.
