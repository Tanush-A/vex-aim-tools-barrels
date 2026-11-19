# TODO.md — the plan for the week (meeting with Dave: Monday 2026-11-23)

**Updated:** 2026-11-18 (evening). Re-planned with Tanush after the 2026-11-16 meeting with Dave. Rule (`CLAUDE.md`): updated whenever a task starts, finishes or changes priority, together with `STATUS.md`.

## The goal

A detector at least as good as the vendor's in the vendor's own conditions, and working in more ordinary conditions than the one we had (white table, normal light). Any win beyond that is a bonus.

- **Occlusion gets fixed.**
- **If the segmentation is good, the detector finds the barrel.** A measured test (`experiments/2026-11-18_det_given_seg`), not an assumption.
- **Never regress:** no scenario row of the eval table (`tools/report.py`) on home or campus may drop. A fix for one case that breaks another (close-ups, say) does not merge.
- **Ordinary conditions only.** Parked as extreme: the orange wood table under a lamp, glare on the black table, lamp brightness 1. They stay in the eval table as report-only rows.
- **Adaptive thresholds from evidence:** Tanush sets the best hue and saturation thresholds by hand per frame; if something in the frame's histogram predicts his settings, that relation becomes the adaptive rule.

## Where the detector stands (train frames, 2026-11-18)

| test | found |
|---|---|
| eval table, home | 27 of 29, no false box (was 25) |
| eval table, campus | 34 of 35 |
| perfect home masks in | 28 of 29 |
| lightly / medium / heavily damaged masks in | 141 / 64 / 13 of 145 |
| black table, thresholds read from the labels (extreme) | 19 of 26 |

Still missed on the white tables: the barrel behind the robot (campus `occl_02`, side occlusion), and two barrels in home `cluster_01` (one shows only a wedge between two barrels).

## Claude, now (none of this needs new data)

| # | what | state |
|---|---|---|
| **A2** | **Side occlusion.** A barrel half hidden at the side by something that is not a barrel (campus `occl_02`, the live miss with Dave). The old fix (`stripe_w_min` 0.25 + `occl_body_side`) draws boxes half off the barrel because it takes the barrel's own body for the thing hiding it. New rule to try: a side counts as hidden only where a found barrel or the frame edge is, or where the body color visibly stops. Detector = main code: `wip/` branch, pre-registered, walkthrough. | **built 2026-11-18 on `wip/detector-side`, waits for Tanush's "understood".** `side_hidden`: a side counts as hidden only for a reason (frame edge, a found nearer barrel, body and stripe ending apart). Campus 34 → 35 of 35, home unchanged, no row worse; medium damage 64 → 99 of 145 with false boxes 22 → 1 |
| **A3** | **The misses left when the segmentation is good.** The wedge barrel in `cluster_01` (box it or accept it, with the reason); stripes eaten at far range; a highlight across a stripe (medium damage: 64 of 145). Same branch and rule as A2. | **done with A2.** The wedge barrel in `cluster_01`: no box on purpose (nothing to size it from). The second `cluster_01` miss is the bottom predicted 10 px low from the top row (calibration). `seam_height` for thin far stripes: passes, changes no real frame |
| **A4** | **Bottom edges 4 to 7 px low for far barrels: calibrate from the ruler frames.** The 12 `calib` frames and `data/calib.csv` exist; no new shots. New camera constants only if home and campus do not regress; then the `g` size guide in the box tool is right as well. Geometry = main code: `wip/` branch, walkthrough. | **done 2026-11-18 on `wip/calibration`, nothing adopted.** The ruler frames fit only with a lower camera (height 40.2 mm, tilt 20.4°), and that camera fails on home and campus; a second one (tilt 20.95°) gets sizes and bottoms right within a pixel but loses one hidden barrel in home `occl_01`. Each session wants a tilt about 0.3° from the others. Finding to act on: a bottom inferred from the box width is right to 1–2 px with any camera (from the top row: 4–7 px). Next: A5 |
| **A5** | **Infer hidden bottoms from the box width, not from the top row** (the A4 finding: it does not depend on the camera tilt). Should bring back the second `cluster_01` barrel and make the calibration question less urgent. Detector = main code: pre-registered, never-regress gate, walkthrough. | proposed 2026-11-18, waits for Tanush's go |
| **H** | **Vendor column in the eval table.** Reads `data/vendor/<stem>_vendor.json`, scores the vendor's boxes by the same rule against the same labels, next to ours. Ready before the first frames arrive. Eval = main code: `wip/` branch, walkthrough. | **merged 2026-11-19 (Tanush: ok).** `python barrels/tools/report.py --vendor`; run only on made-up vendor files so far |
| **I** | **The never-regress rule as a command.** One command that compares the eval table with the stored numbers for home and campus, row by row, and fails on any drop. Run before every merge. With H. | **merged 2026-11-19 with H.** `python barrels/tools/report.py --gate` against `results/baseline/`; fails and names the row when a home or campus row drops |
| **F** | **Histogram against the hand-set thresholds.** Script merged; needs about 8 ordinary conditions. Re-run as conditions and slider labels arrive: `python barrels/experiments/2026-11-18_hs_relation/run.py`. If a relation holds: the adaptive rule, pre-registered, scored with the eval table. | waiting on data |
| **G** | **Against the vendor, and one look at the test frames**, after the adaptive rule is in (or shown not to work). | Sunday 2026-11-22 |

## Tanush

1. **Start the data session** (prompt in `HANDOFF.md`).
2. **First shoot, first two minutes: the vendor save.** `simple_cli BarrelTracker`, one orange and one blue barrel, `tm save`: the console line ends `vendor: 2 objects (OrangeBarrel, BlueBarrel)` and `robot_snapN_vendor.png` shows a tight box on each (`RUNBOOK.md`).
3. **Same sitting: the close-up check.** A barrel about 2 cm from the bumper with a far barrel behind it in the picture: both get a box. A barrel seated in the kicker: if it gets no box, `tm save` it.
4. **Shoot conditions**, 9 shots each (list below), as tables and lights come up. Two lights on one arrangement: same session.
5. **Box every frame** (`box_tool.py`).
6. **Slider labels**, three frames per condition (`core_01`, `occl_01`, `clutter_01`): `python barrels/tools/hs_slider.py --filter <light>_<surface>`. Criterion: as much barrel painted as needed to detect it, as little else as possible. On first open, check that a slider knob follows the mouse.
7. **Tell Claude when a condition is in** (F is re-run each time).
8. **Read the walkthroughs** for A2 / A3, A4 and H when they are ready; each merges on "understood".
9. Optional, after A4: re-box the three hidden barrels whose boxes are no taller than wide (home `occl_02`, black `occl_02`, `occl_04`) with the corrected size guide.

## Shot list: 9 shots per condition, about 6 minutes

A condition = one table under one light. Aim for ten or more conditions; few scenes each.

| # | name | shot |
|---|---|---|
| 1 | `neg_01` | empty table |
| 2 | `neg_02` | clutter only, including one orange and one blue thing that is not a barrel |
| 3 | `core_01` | four barrels spread out, mixed colors, near to far, nothing else |
| 4 | `touch_01` | two or three touching, mixed colors |
| 5 | `occl_01` | a barrel about half hidden behind a barrel of the other color, clutter in the background |
| 6 | `occl_02` | a barrel about half hidden at the side by a clutter object |
| 7 | `close_01` | one barrel about 2 cm from the bumper |
| 8 | `edge_01` | one barrel cut by the left or right frame edge, one fully in view |
| 9 | `clutter_01` | barrels among clutter, an orange or blue non-barrel right next to a barrel |

Conditions to try for: white table with window light, overhead light, both, sun, dim evening light; dark wood table with overhead and with window; gray table (yellow overhead); black table with window and with overhead; anything else ordinary. A new table: tell the data session, it adds the tags.

## Parked

- Extreme conditions: orange wood under a lamp, black-table glare, brightness 1; finding blue barrels from the blue body alone (the idea for wood).
- Whether the camera's auto exposure / white balance can be locked: a quick look, not a task.

## Done this week

- **2026-11-18:** A, the detector given good segmentation: the test, `cap_behind` (a barrel behind a found barrel, from its visible top) and `stripe_join` (a stripe in pieces), on by default and merged on Tanush's "understood" · B, `tm save` stores the vendor's detections with each frame (merged; live check open) · C, the shot list · D, the slider tool `tools/hs_slider.py` (merged; window unchecked) · F, the histogram-against-thresholds script (merged; dry run).
- **Before (the 2026-11-09 list):** hs color model adopted · doc cleanup · move to the CLI · data: wood ladder 117, black 15, ruler 12 · `tm seg` · eval table `tools/report.py` · side occlusion explained, first fix off · histograms + `HISTOGRAMS-FOR-DAVE.pdf`. Tried and not adopted 2026-11-16: one color range fit on all tables; thresholds read from labels as a ceiling (53 of 152 on black + bright wood).
