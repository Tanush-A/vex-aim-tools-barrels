# The v1 capture plan (October 2026) — archived from `DATA.md` on 2026-11-05

The frames this plan produced are the 21 `4A8B_window_light_*` frames (the v1 base set, still the training and test data) and the wood-desk `calib`/`ruler` frames. Kept for the record; the live plan is the v2 section of `DATA.md`.

## Sessions

| session | where | tags | frames |
|---|---|---|---|
| B (2026-10-19, CMU) | white matte table, daylight from the side, plain blue-gray wall | `--light window --surface light` | scenes 1–21 (**v1 base set**) |
| C (2026-10-19, Pittsburgh) | wood desk, cool lamp pointed up | `--light upcool --surface wood` | calib 22–26 + ruler 27 (camera geometry only) |
| ~~A~~ | ~~home black table, warm yellow overhead light~~ | | skipped 2026-10-17 (Tanush's call); a warm-light black-table stress set can be shot in Pittsburgh later |

**Lighting for black-table frames (N-004):** use **indirect/bounced light** — lamp pointed at the ceiling or wall, not straight at the barrels. Direct light puts specular glare on the lids and body, and glare is out of v1 scope. Frames under overhead/direct light are welcome but must be tagged as such (`overhead`, `lamp`, …); they become later stress tests, not v1 training data. Use a `bounce` light tag for the indirect setup.

Direct overhead light puts glare on lids; label glare as ignore (255). On a light table the barrel shadows are visible: label them other (3).

## The shot list

Setup: robot on the table, at least 4 barrels (2 orange, 2 blue), **nothing orange/blue/yellow in the background** for the data frames (plush toys, books, remotes out of view). Frame so the far edge of the table and some wall are visible when possible. Shoot in **this order** in **one session** (the snapshot counter resets per session), then import with `tools/import_snaps.py` using the same scene list.

| # | scene | shot |
|---|---|---|
| 1–4 | `core` | orange + blue touching at ~15 cm, one barrel far (~30 cm), one close (~7 cm). Vary layout/robot angle each time. |
| 5–6 | `far` | all barrels 25–30 cm away, spread out, not touching |
| 7–8 | `close` | one barrel at ~7 cm, centered, full body visible: one orange, one blue |
| 9–10 | `touch` | three barrels touching in a row at ~15 cm, mixed colors; second shot in a different order/angle |
| 11–12 | `cluster` | all barrels bunched at 15–25 cm, some touching, some not |
| 13–14 | `occl` | a barrel at ~10 cm partly hiding another at ~20 cm behind it; swap colors for the second |
| 15–16 | `edge` | a barrel half out of frame on the left; then on the right |
| 17 | `top` | one barrel pushed against the robot's front so only the lid shows |
| 18 | `topstripe` | one barrel ~3–4 cm away: lid + stripe visible, bottom off-frame |
| 19–21 | `neg` | empty table; empty table with the robot turned another way; table with one non-orange/non-blue object (cup, book) |
| 22–26 | `calib` | one **orange** barrel centered on the vertical crosshair, near edge at **50, 100, 150, 200, 300 mm** from the robot's front edge (ruler), in that order |
| 27 | `ruler` | mm ruler flat on the table, zero at the robot's front edge, running straight ahead along the vertical crosshair, tick numbers readable |

Import commands (dry-run first, then without `--dry-run`):

```zsh
python barrels/tools/import_snaps.py --light overhead --surface light --scenes \
core,core,core,core,far,far,close,close,touch,touch,cluster,cluster,occl,occl,edge,edge,top,topstripe,neg,neg,neg,calib,calib,calib,calib,calib,ruler --dry-run
```

If a shot is bad, retake it immediately (press `s` again) and delete the bad `robot_snapN.png` before importing; the tool pairs the remaining files with the scene list in numeric order, so the counts must match.

## Pixel masks (the v1 labels)

Labeled with `tools/label_tool.py` (scribble `1` orange, `2` blue, `3` other, `4` ignore; `g` grows; `n` saves). The format and rules are still in `DATA.md` (masks are the segmentation's truth); the per-barrel instance files (`_inst.*`, v1.5) were superseded by box labels on 2026-11-02.
