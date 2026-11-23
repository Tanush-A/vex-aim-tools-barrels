# Ours against the vendor detector, per condition (2026-11-23, git 093203b)

Train frames with a vendor file only; test frames are never opened. Ours = the default color model and detector. Strict = the v2 rule (same color, IoU at least 0.5, bottom edge within a tenth of the height). Overlap = same color and IoU at least 0.5. Place = a box of the right color centered on the barrel. False = boxes on no barrel; empty = boxes on frames with no barrel.

## Are the vendor files sound?

- 106 vendor barrel boxes paired with a hand box (1 vendor barrel boxes sit on no hand box). Classes seen: BlueBarrel 52, OrangeBarrel 55, Robot 1.
- Placement and scale: the hand box centers against the vendor's raw box centers (its own 320x240 units) fit a line of slope 1.99 (x) and 2.03 (y), offsets 1.3 and -0.2 px (expected: slope 2, offset 0). The conversion (corner and size, times 2) is right.
- Read as a center instead of a corner, the median IoU would be 0.12 instead of 0.81: the corner reading is the right one.
- On free-standing barrels (74 pairs): median IoU 0.82, vendor width / hand width 1.07, height 1.09; median offsets (vendor minus hand, px): left -3, top -6, right +3, bottom +2.
- On hidden barrels (18 pairs, median IoU 0.69) the vendor boxes the part it sees, our labels the whole barrel: 12 of them are visibly cut (narrower than 0.85 of the hand box, or the bottom 8 px or more above the hand box's, or the top 10 px or more below). That is where the strict rule is harsh on it; the place count is the fairer one on hidden barrels.
- Timing: every frame was still, so a lag of the vendor's list behind the frame cannot be seen here (the vendor list is read when the frame arrives, `read_at: frame`).
- Scores: median 99, lowest 64; 2 of 107 below 80.
- Pictures: `look/` (33 frames; white = hand, colored with V = vendor, green = ours).

## Per condition

| condition | frames | barrels | ours strict / overlap / place | ours false (empty) | vendor strict / overlap / place | vendor false (empty) | better |
|---|---:|---:|---|---|---|---|---|
| both_abpgray | 8 | 16 | 10 / 11 / 11 | 2 (0) | 16 / 16 / 16 | 0 (0) | vendor (+6 found, -2 false) |
| lampcool6_ottoman | 7 | 15 | 3 / 3 / 3 | 0 (0) | 13 / 14 / 14 | 1 (0) | vendor (+10 found, +1 false) |
| lampmid3_ottoman | 7 | 15 | 1 / 2 / 2 | 1 (0) | 10 / 11 / 11 | 1 (0) | vendor (+9 found, +0 false) |
| lampmid6_ottoman | 7 | 15 | 6 / 6 / 6 | 0 (0) | 13 / 14 / 14 | 1 (0) | vendor (+7 found, +1 false) |
| lampwarm6_ottoman | 7 | 15 | 0 / 0 / 0 | 1 (0) | 11 / 11 / 11 | 0 (0) | vendor (+11 found, -1 false) |
| overheaddim_palewood | 7 | 15 | 12 / 12 / 12 | 1 (0) | 12 / 13 / 13 | 1 (0) | tie |
| window_abpwhite | 17 | 32 | 26 / 26 / 26 | 2 (1) | 24 / 26 / 27 | 4 (1) | ours (+2 found, -2 false) |

- **both_abpgray**: ours found 10 of 16 with 2 false; the vendor found 16 of 16 with 0 false. Better: vendor (+6 found, -2 false).
- **lampcool6_ottoman**: ours found 3 of 15 with 0 false; the vendor found 13 of 15 with 1 false. Better: vendor (+10 found, +1 false).
- **lampmid3_ottoman**: ours found 1 of 15 with 1 false; the vendor found 10 of 15 with 1 false. Better: vendor (+9 found, +0 false).
- **lampmid6_ottoman**: ours found 6 of 15 with 0 false; the vendor found 13 of 15 with 1 false. Better: vendor (+7 found, +1 false).
- **lampwarm6_ottoman**: ours found 0 of 15 with 1 false; the vendor found 11 of 15 with 0 false. Better: vendor (+11 found, -1 false).
- **overheaddim_palewood**: ours found 12 of 15 with 1 false; the vendor found 12 of 15 with 1 false. Better: tie.
- **window_abpwhite**: ours found 26 of 32 with 2 false; the vendor found 24 of 32 with 4 false. Better: ours (+2 found, -2 false).

All together: ours 58 of 123 with 7 false, the vendor 99 of 123 with 8 false.

## Per scenario, all conditions together (strict; place in brackets)

| scenario | barrels | ours | vendor |
|---|---:|---:|---:|
| close | 6 | 2 (2) | 5 (5) |
| clutter | 24 | 8 (10) | 15 (18) |
| core | 24 | 9 (9) | 22 (22) |
| edge | 12 | 3 (3) | 12 (12) |
| held | 1 | 1 (1) | 1 (1) |
| occl | 6 | 1 (1) | 4 (4) |
| occlx | 32 | 26 (26) | 24 (27) |
| touch | 18 | 8 (8) | 16 (17) |

## Where the vendor finds a barrel we miss (the list for the detector work)

45 barrels the vendor finds under the strict rule and we do not; 6 more the vendor at least points at (place count) where we have nothing in place. Hand box number as in the picture (`look/<frame>.png`, thick white).

| frame | # | color | flags | ours by place | vendor |
|---|---:|---|---|---|---|
| 4A8B_both_abpgray_clutter_01 | 2 | orange | occluded | yes | strict |
| 4A8B_both_abpgray_core_01 | 2 | blue | - | no | strict |
| 4A8B_both_abpgray_core_01 | 4 | orange | - | no | strict |
| 4A8B_both_abpgray_edge_01 | 1 | orange | - | no | strict |
| 4A8B_both_abpgray_touch_01 | 1 | orange | - | no | strict |
| 4A8B_both_abpgray_touch_01 | 2 | blue | - | no | strict |
| 4A8B_lampcool6_ottoman_close_01 | 1 | orange | truncated | no | strict |
| 4A8B_lampcool6_ottoman_clutter_01 | 1 | blue | - | no | strict |
| 4A8B_lampcool6_ottoman_clutter_01 | 3 | orange | - | no | strict |
| 4A8B_lampcool6_ottoman_core_01 | 1 | blue | - | no | strict |
| 4A8B_lampcool6_ottoman_core_01 | 2 | orange | - | no | strict |
| 4A8B_lampcool6_ottoman_core_01 | 4 | orange | - | no | strict |
| 4A8B_lampcool6_ottoman_edge_01 | 1 | blue | truncated | no | strict |
| 4A8B_lampcool6_ottoman_edge_01 | 2 | orange | - | no | strict |
| 4A8B_lampcool6_ottoman_occl_02 | 1 | orange | occluded | no | strict |
| 4A8B_lampcool6_ottoman_touch_01 | 1 | blue | - | no | strict |
| 4A8B_lampmid3_ottoman_clutter_01 | 1 | blue | - | yes | strict |
| 4A8B_lampmid3_ottoman_clutter_01 | 3 | orange | - | no | strict |
| 4A8B_lampmid3_ottoman_core_01 | 1 | blue | - | no | strict |
| 4A8B_lampmid3_ottoman_core_01 | 2 | orange | - | no | strict |
| 4A8B_lampmid3_ottoman_core_01 | 4 | orange | - | no | strict |
| 4A8B_lampmid3_ottoman_edge_01 | 1 | blue | truncated | no | strict |
| 4A8B_lampmid3_ottoman_edge_01 | 2 | orange | - | no | strict |
| 4A8B_lampmid3_ottoman_touch_01 | 1 | blue | - | no | strict |
| 4A8B_lampmid3_ottoman_touch_01 | 3 | orange | - | no | strict |
| 4A8B_lampmid6_ottoman_close_01 | 1 | orange | truncated | no | strict |
| 4A8B_lampmid6_ottoman_clutter_01 | 1 | blue | - | no | strict |
| 4A8B_lampmid6_ottoman_core_01 | 1 | blue | - | no | strict |
| 4A8B_lampmid6_ottoman_core_01 | 3 | blue | - | no | strict |
| 4A8B_lampmid6_ottoman_edge_01 | 1 | blue | truncated | no | strict |
| 4A8B_lampmid6_ottoman_occl_02 | 1 | orange | occluded | no | strict |
| 4A8B_lampmid6_ottoman_touch_01 | 1 | blue | - | no | strict |
| 4A8B_lampwarm6_ottoman_close_01 | 1 | orange | truncated | no | strict |
| 4A8B_lampwarm6_ottoman_clutter_01 | 1 | blue | - | no | strict |
| 4A8B_lampwarm6_ottoman_clutter_01 | 3 | orange | - | no | strict |
| 4A8B_lampwarm6_ottoman_core_01 | 1 | blue | - | no | strict |
| 4A8B_lampwarm6_ottoman_core_01 | 2 | orange | - | no | strict |
| 4A8B_lampwarm6_ottoman_core_01 | 4 | orange | - | no | strict |
| 4A8B_lampwarm6_ottoman_edge_01 | 1 | blue | truncated | no | strict |
| 4A8B_lampwarm6_ottoman_edge_01 | 2 | orange | - | no | strict |
| 4A8B_lampwarm6_ottoman_touch_01 | 1 | blue | - | no | strict |
| 4A8B_lampwarm6_ottoman_touch_01 | 2 | blue | - | no | strict |
| 4A8B_lampwarm6_ottoman_touch_01 | 3 | orange | - | no | strict |
| 4A8B_overheaddim_palewood_edge_01 | 1 | blue | truncated | no | strict |
| 4A8B_overheaddim_palewood_occl_02 | 1 | orange | occluded | no | strict |
| 4A8B_lampcool6_ottoman_clutter_01 | 4 | orange | bottom_estimated+occluded | no | place only |
| 4A8B_lampmid3_ottoman_clutter_01 | 4 | orange | bottom_estimated+occluded | no | place only |
| 4A8B_lampmid6_ottoman_clutter_01 | 4 | orange | bottom_estimated+occluded | no | place only |
| 4A8B_window_abpwhite_occlx_03 | 1 | orange | occluded | no | place only |
| 4A8B_window_abpwhite_occlx_06 | 1 | orange | bottom_estimated+occluded | no | place only |
| 4A8B_window_abpwhite_occlx_10 | 1 | orange | bottom_estimated+occluded | no | place only |

The other way: 4 barrels we find (strict) and the vendor does not.

Occlusion shots (`occl`, `occlx`): ours 27, the vendor 28 of 38 barrels (strict); by place ours 27, the vendor 31.

Left out: 149 train frames have no vendor file (shot before 2026-11-18).

Full table: `table.md`. Numbers: `per_set.csv`, `per_frame.csv`, `per_barrel.csv`, `pairs.csv`, `validation.md`.
