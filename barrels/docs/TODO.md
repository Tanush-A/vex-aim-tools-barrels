# TODO.md — the plan for the week (meeting with Dave: Monday 2026-11-23)

**Updated:** 2026-11-18. Re-planned with Tanush after the 2026-11-16 meeting with Dave. This replaces the 2026-11-09 list; what that list finished is under "Done" at the bottom. Rule (`CLAUDE.md`): updated whenever a task starts, finishes or changes priority, together with `STATUS.md`.

## The goal

A detector at least as good as the vendor's in the vendor's own conditions, and working in more ordinary conditions than the one we had (white table, normal light). Any win beyond that is a bonus.

- **Occlusion gets fixed.**
- **If the segmentation is good, the detector finds the barrel.** Checked as a test, not assumed.
- **Never regress:** no scenario row of the eval table (`tools/report.py`) on home or campus may drop. A fix for one case that breaks another (close-ups, say) does not merge.
- **Ordinary conditions only.** Parked as extreme: the orange wood table under a lamp, glare on the black table, lamp brightness 1. They stay in the eval table as report-only rows.
- **Adaptive thresholds from evidence:** Tanush sets the best hue and saturation thresholds by hand per frame; if something in the frame's histogram predicts his settings, that relation becomes the adaptive rule.

## In order

| # | what | who | state |
|---|---|---|---|
| **A** | **The detector finds every barrel when the segmentation is good.** (1) Perfect masks in (the home masks), every barrel out. (2) Realistic masks in: the same with holes and eaten edges (simulated highlights and shadows), and the black-table frames with thresholds read from their labels. (3) Fix what fails: barrel behind a barrel of the other color (4 of the 5 white-table misses), a stripe that comes out in pieces, the side-occlusion switch. Also check the expected barrel size against the hand-drawn boxes (Tanush: `g` in the box tool was sometimes wrong). Detector = main code: `wip/` branch, walkthrough, merge on "understood". | Claude | **built 2026-11-18 on `wip/detector-given-seg`, not merged, both new switches off.** Barrel behind barrel (`cap_behind`) and stripe in pieces (`stripe_join`): home 25 → 27 of 29, no false box, campus unchanged; fails the written rule on two boxes (black `occl_04` 7 px low against an estimated label bottom; one wrong box in the wood clip). Waits on Tanush: read the walkthrough, decide whether those two block it. Open leads: side occlusion (hidden side only where a found barrel or the frame edge is), ruler calibration (bottoms 4–7 px low) |
| **B** | **Vendor detections saved with each frame.** One keypress stores the raw frame and what the vendor detector reported at that moment, so the eval table gets a vendor column. | Claude | **merged 2026-11-18** (`tm save` writes `robot_snapN.png` + `robot_snapN_vendor.json` + a look-at `_vendor.png`; `import_snaps.py` carries the JSON to `data/vendor/`); not run on the robot yet: live check in `RUNBOOK.md`, first thing at the first shoot |
| **C** | **Shot list** (below, and `DATA.md`). | both | agreed 2026-11-18 |
| **D** | **Slider tool.** Six numbers (hue low, hue high, saturation floor, per color), live segmentation and live boxes; saves `data/labels/<stem>_hs.json`. | Claude | **merged 2026-11-18**: `python barrels/tools/hs_slider.py --filter <light>_<surface>` (keys in `DATA.md`, "Slider labels"); the window itself is unchecked until Tanush opens it |
| **E** | **Shoot, box, slider-label**, as tables and lights come up. Boxes on every frame; slider labels on three frames per condition (`core_01`, `occl_01`, `clutter_01`). Criterion: as much barrel painted as needed to detect it, as little else as possible. | Tanush | with the data session (prompt in `HANDOFF.md`) |
| **F** | **Histogram against the hand-set thresholds.** Is there a relation? Each condition is one data point, so it needs about ten; tested by leaving whole conditions out. Runs on whatever conditions exist, re-run as data arrives. If the relation holds: the adaptive rule, pre-registered, scored with the eval table. | Claude | **script merged 2026-11-18**, run 01 is a dry run (2 ordinary conditions, 8 needed); re-run with `python barrels/experiments/2026-11-18_hs_relation/run.py` as conditions and slider labels arrive |
| **G** | **Against the vendor, and one look at the test frames**, after the adaptive rule is in (or shown not to work). | Claude | Sunday 2026-11-22 |

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

Clutter is in shots 2, 5, 6 and 9. If the light can change without touching the table (overhead on and off, blinds), keep the arrangement and reshoot all nine: that is a second condition with the same scenes, and it is split by scene.

Conditions to try for: white table with window light, overhead light, both, sun, dim evening light; dark wood table with overhead and with window; gray table (yellow overhead); black table with window and with overhead; anything else ordinary. A new table: tell the data session, it adds the tags.

## Tanush's part

1. Shoot (E) whenever a new table or light comes up; box every frame; slider-label three per condition once D is ready.
2. Live checks when the robot is on: B (the vendor save), and the close-up fix: a barrel about 2 cm from the bumper with a far barrel behind it in the picture must get its box; a barrel seated in the kicker should too, and if it does not, `tm save` it.
3. Read the walkthrough for A when it is ready and say "understood".

## Parked

- Extreme conditions: orange wood under a lamp, black-table glare, brightness 1; finding blue barrels from the blue body alone (the idea for wood).
- Ruler calibration (12 frames exist, `data/calib.csv`): un-parked only if A shows the expected sizes are off.
- Whether the camera's auto exposure / white balance can be locked: a quick look, not a task.

## Done (the 2026-11-09 list)

0 walkthrough + merge of hs · 1 doc cleanup · 2 move to the CLI · 3 data: wood ladder 117, black 15, ruler 12 (2026-11-16) · 5 `tm seg` (merged 2026-11-16) · 6 eval table `tools/report.py` (merged 2026-11-16) · 7 side occlusion: explained, fix merged switched off (2026-11-16) · 8 histograms + `HISTOGRAMS-FOR-DAVE.pdf` (2026-11-16). Tried and not adopted 2026-11-16: one color range fit on all tables; ceiling check of per-frame thresholds (53 of 152 on black + bright wood). Not finished: 4 close-up live confirm (in "Tanush's part"), 9 barrel behind barrel (now A), 9b / 10b test looks (now G), 10 slider labels (now D, E, F).
