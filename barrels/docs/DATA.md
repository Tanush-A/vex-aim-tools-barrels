# DATA.md — the frames, their labels, the splits, what to shoot

**Updated:** 2026-11-06 (`tm save` capture; the 2026-11-07 campus session plan at the end). Before capturing or using data, read this; new frames are assigned to a split at import, before any method sees them.

## Storage and naming

Small hand-taken sets, **committed to git**: images in `barrels/data/raw/`, labels in `barrels/data/labels/`, the split assignment in `barrels/data/splits.json`.

`{robot}_{light}_{surface}_{scene}_{nn}.png` — e.g. `4A8B_window_light_touch_02.png`. Use exact tags.

- **robot:** short id, e.g. `4A8B` (= AIM-4A8B6118); `DAVE` for Dave's snapshots.
- **light:** the source — `window`, `overhead`, `lamp`, `bounce` (indirect), `dim`, `side`, `mixed`, or the home-lamp tags `{up,at,away}{cool,mid,warm}`.
- **surface:** `light` (the white matte table), `beige`, `black`, `wood`, `floor`, `paper`, … (extend as needed).
- **scene:** `core` (orange + blue touching ~15 cm, one far, one close) · `far` · `close` · `top` (lid only) · `topstripe` (lid + stripe, bottom below the frame) · `touch` · `occl` · `cluster` · `edge` · `glare` · `shadow` · `clutter` · `held` (in the kicker) · `neg` (no barrels) · `calib` (one barrel straight ahead at a measured distance) · `ruler` · `horizon` (a mark at camera height on a far wall) · backdrop scenes since 2026-11-06: `room` (the open room behind the barrels), `hand` (a hand and laptop behind), `board` (the plain grey board behind), `window` (a bright window or lamp behind).
- **nn:** two-digit counter per (robot, light, surface, scene).

**Capture:** `tm save` in the live programs (`RUNBOOK.md`), or the camera viewer's key `s`; both write `snapshots/robot_snapN.png` (under `barrels/live/` for the live programs). **Import right away** with `tools/import_snaps.py --src barrels/live/snapshots --scenes …` (it renames in shooting order; the viewer's counter restarts each session and would overwrite, so use one or the other in a session). `tm rec` writes ten-second sequences to `snapshots/rec_<stamp>/` for replaying the multi-frame view offline; they are not frames to label unless imported one by one.

## Labels

Three label kinds exist next to each frame. **Boxes are the truth the detector is scored against**; masks are the segmentation's truth; instances are superseded.

### Box labels — `<stem>_boxes.json` (v2, since 2026-11-02)

```json
{"version": 1, "stem": "4A8B_window_light_touch_01", "image_sha1": "…", "reviewed": true,
 "negative": false, "clean": true,
 "barrels": [
   {"id": 1, "color": "orange", "bbox": [212, 160, 290, 262],
    "flags": ["occluded", "bottom_estimated"], "note": ""}
 ]}
```

- `bbox` = `[x0, y0, x1, y1]`, half-open, in the 640×480 frame, **clipped to the frame**. `color` = the body color (an orange barrel has a blue stripe).
- `negative` = true when the frame has no barrels. `clean` = true when nothing orange or blue is in the frame besides barrels; a false box on a clean frame disqualifies a config (`EVAL.md`).
- `flags` ⊆ {`occluded` (something hides part of it), `truncated` (the frame edge cuts it; set automatically), `held` (in the kicker), `bottom_estimated` (you could not see where the base meets the table), `no_stripe` (the stripe is not visible)}.
- `source` = `manual` | `from_inst` | `from_inst+manual` | `dave_gt`. The 21 v1 frames were converted from their instances on 2026-11-03 and then fixed by hand by Tanush (11 files changed); all are `reviewed: true`.

**Rules.** Draw the **full barrel**: lid top to where the base meets the table, bulge to bulge; the stripe is inside. Draw **through occluders** as if they were transparent and flag `occluded`; if the bottom cannot be seen, estimate it from the barrel's size and flag `bottom_estimated`. A barrel cut by the frame gets a box that **stops at the edge**. A shadowed bottom you can still see is the bottom, no flag. Reflections are not barrel. Other orange/blue objects get no box; set `clean: false`. A held barrel is boxed normally, flag `held`. 1–2 px precision is enough; the eval tolerance is a tenth of the box height.

**Tool:** `python barrels/tools/box_tool.py [--filter <light>_<surface>] [--unlabeled]`. Drag on empty space to draw (takes the color of the last box); click inside a box to select; drag an edge or corner to move just that edge. `o`/`b` color; `x`/`h`/`e`/`s` toggle occluded / held / bottom_estimated / no_stripe; `c` toggles `clean`; `d` deletes; `u` undoes; `g` shows the barrel size the geometry expects at the cursor row (a check — draw what you see first); `v` raw view; `w` saves; `n`/`p` save and move; `q` saves and quits. ≈ 30 s per frame.

### Pixel masks — `<stem>_mask.png` (v1)

Single-channel PNG: **0** other, **1** barrel orange (orange body or the orange stripe of a blue barrel), **2** barrel blue, **255** ignore (glare / uncertain; excluded from pixel eval). Painted with `tools/label_tool.py` (scribble `1`/`2`/`3`/`4`, `g` grows along image edges, `n` saves; `<stem>_strokes.png` keeps the strokes). Rules: stroke every barrel incl. its stripe; `3` on table, wall and every other object; `4` only on blown-out glare; reflections are `3`; shadowed barrel faces are barrel; the VEX logo is the lid's color. All 21 v1 frames are masked; masks are not needed for v2 frames (optional on two frames per table as a segmentation check).

### Instances — `<stem>_inst.png` + `.json` (v1.5; superseded 2026-11-02)

Per-barrel ids derived from the masks by an automatic split (`src/barrels/instances.py`, stripe-seeded watershed) plus click edits (`tools/instance_tool.py`). Kept in the repo because the box labels were converted from them; no longer edited or needed. `io.load_instances` refuses stale files.

## What to shoot next (v2.0: one table, one background)

Decided 2026-11-03 (timeline): one table and one background, not wood, whatever light is there, tagged honestly. Variety comes from arrangements, positions and clutter. Shoot the list **once at minimum, twice if time** (second pass: different clutter, positions, distances). Clutter is Tanush's own, mostly not orange/blue, with a few orange/blue distractors. Barrels upright. Shoot in this order in one session:

| # | scene | shot |
|---|---|---|
| 1–2 | `core` | orange + blue touching ~15 cm, one far ~30 cm, one close ~7 cm; vary the layout |
| 3 | `far` | all barrels 25–30 cm, spread out |
| 4 | `close` | one barrel ~5 cm, full body visible |
| 5 | `topstripe` | one barrel ~2–3 cm: lid + stripe visible, bottom below the frame |
| 6 | `top` | one barrel against the bumper: lid only |
| 7–8 | `touch` | three touching in a row ~15 cm, mixed colors; then two of the same color side by side |
| 9–10 | `occl` | a barrel ~10 cm partly hiding one ~20 cm behind it; then a barrel partly hidden behind a clutter object |
| 11–12 | `cluster` | all barrels bunched 15–25 cm, some touching |
| 13 | `edge` | a barrel half out of frame at the side |
| 14–15 | `clutter` | barrels among varied clutter; the second with an orange or blue object right next to a barrel of the same color |
| 16–18 | `neg` | empty table; clutter only (nothing orange/blue); clutter including an orange and a blue object |
| 19 | `held` | a barrel in the kicker, if the robot can hold one |

```zsh
python barrels/tools/import_snaps.py --light <light> --surface <light|beige|black> --scenes \
core,core,far,close,topstripe,top,touch,touch,occl,occl,cluster,cluster,edge,clutter,clutter,neg,neg,neg,held --dry-run   # then without --dry-run
python barrels/tools/make_splits.py --v2 --filter 4A8B_<light>_<surface>     # right away, before any method sees the frames
python barrels/tools/box_tool.py --filter <light>_<surface>                   # then label
```

If a shot is bad, retake it immediately and delete the bad `robot_snapN.png` before importing; the tool pairs files with the scene list in order, so the counts must match. Commit `data/raw/`, `data/labels/` and `data/splits.json`.

**Calibration session** (once per robot until Dave says otherwise; his "lookup table"): one **orange** barrel centred on the vertical crosshair, ruler zero at the robot's front edge, distance to the **near edge of the base at table level** (the bulge overhangs it by ≈ 3.75 mm — slide the ruler under): **0, 5, 10, 15, 20, 25, 30, 50, 100, 150, 200, 300 mm** → 12 `calib` frames in that order, ruler out of frame before `s`. Plus one `horizon` frame if a wall ≥ 1 m away is available: a mark **43.47 mm** above the table, centred. Import with `--scenes` listing `calib` twelve times, then `horizon` (the importer takes no repeat count); the distances go in `data/calib.csv` (`stem, d_ruler_mm`). Geometry-only, no split. **Box the calib frames too** (`box_tool.py --filter calib`): their top row, bottom row and width are what the calibration fits f and tilt from (`TODO.md`, P1).

## Dave's snapshots (barrels.zip, 2026-09-28; imported 2026-11-03)

20 frames from Dave's robot in his office: `DAVE_office_speckle_snap_00–11` (speckled gray-pink desk, window + room light; 12 frames with his ground-truth boxes) and `DAVE_office_dark_snap_12–19` (dark table, warm dim light, 5–7 barrels, a hand; no truth). `tools/import_dave_zip.py ~/Downloads/barrels.zip`; his boxes (yellow = orange barrel, green = blue, drawn in `<snap>_ground_truth.png`) are recovered pixel-exactly as the difference from the raw snapshot → `_boxes.json` with `source: "dave_gt"`, `clean: false`. His notes: `DAVE-barrels-zip-notes.md`. **Outside check only: in no split, never tuned on.** The v1 segmentation finds nothing on them (`EXPERIMENTS.md` 2026-11-03).

## Splits

Fixed **train / test**; dev is empty by design; test is **never used for tuning** (`EVAL.md`). `data/splits.json` is written by `tools/make_splits.py` (seeded, append-only — a stem never moves once assigned).

| split | images |
|---|---|
| test (5, locked 2026-10-19) | `window_light_core_04`, `window_light_edge_02`, `window_light_far_01`, `window_light_neg_03`, `window_light_touch_01` |
| train (16) | all other `4A8B_window_light_*`: close 01–02, cluster 01–02, core 01–03, edge_01, far_02, neg 01–02, occl 01–02, top_01, topstripe_01, touch_02 — tuned by leave-one-scene-out CV |
| v2.0 frames | assigned at import by `make_splits.py --v2`: one frame per scene tag with ≥ 2 frames → test, the rest → train |
| not in any split | `calib`, `ruler`, `horizon` (geometry only); Dave's 20 frames (outside check); the 19 wood-desk frames (unlabeled) |
| `measured` | defined 2026-10-28 for mm positions, never shot; parked with the world map (`DECISIONS.md` 2026-11-02) |

## Dataset index

| set | location | count | status |
|---|---|---|---|
| v1 base set (2026-10-19, CMU) | `data/raw/4A8B_window_light_*.png` | 21 frames + masks + instances + **boxes** | labeled and reviewed; splits locked; the training and test data |
| wood-desk geometry frames (2026-10-19) | `data/raw/4A8B_upcool_wood_{calib_01–05,ruler_01}.png` | 6 | camera measurement only (`EXPERIMENTS.md` 2026-10-19); distances below |
| home color baselines (2026-10-07) | `data/raw/4A8B_*_wood_*.png` | 19, wood desk, 3 lamp directions × 3 warmths | unlabeled; probe-based baselines only; later stress tests |
| Dave's barrels.zip (2026-09-28) | `data/raw/DAVE_office_*_snap_NN.png` + 12 `_boxes.json` | 20 | outside check, no split |
| v2.0 one-table set | to shoot (above) | 19–38 + 12 `calib` + `horizon` | not captured yet |

**Wood-desk calib distances** (front edge → barrel near edge, measured 2026-10-19): `calib_01` 50 mm (138 px wide), `calib_02` 100 (78), `calib_03` 150 (55), `calib_04` 200 (42), `calib_05` 300 (28). The camera sits ≈ 3 mm behind the front edge (`aim_kin.py`); with the 25.5 mm bulge these widths give f ≈ 356, the ruler marks ≈ 405: `constraints.md` #2.

## Session 2026-11-07 (campus): the plan

**Why.** The first live run (2026-11-06) failed in ways the committed frames cannot show: a grey board behind the barrels, the room, a hand, harsh light. These frames are the dev set for the segmentation redesign and the detector hardening, the one-table list is the v2.0 dataset as planned, the recordings test the multi-frame view, the calibration frames replace the provisional camera. ≈ 1 h on campus plus the import.

**Take:** the robot (charged) and its cable; laptop + charger; every barrel you have (at least two orange, two blue); the grey board; a ruler or tape with mm marks (≥ 30 cm); a sticky note, tape and a pen (the horizon mark); a handful of clutter objects, mostly not orange or blue, plus one orange and one blue object that are not barrels (pen, cap, notebook, fruit); your phone for a photo of each block's layout.

**Before the first shot.** `source setup.zsh`, `cd vex-aim-tools/barrels/live`, `simple_cli BarrelViewer`; make sure `barrels/live/snapshots/` is empty (a fresh session) and that the table, light and robot do not change for the whole session. Shoot the list **in this order**, `tm save` for each; retake a bad shot at once and delete its `robot_snapN.png` before importing. Glance at `tm seg` if you like, but shoot the list as written: never choose a shot by what the detector does with it.

| # | scene | shot |
|---|---|---|
| **A — the scenes that broke the live run** (the room as it is, no board unless said) | | |
| 1–3 | `room` | an orange and a blue barrel ~15 cm apart, the open room behind; three layouts (one with a barrel at ~8 cm, one at ~25 cm) |
| 4–5 | `hand` | as yesterday: a hand and laptop behind the barrels; in the second the hand rests on the table next to a barrel |
| 6–8 | `board` | the grey board behind; both barrels at ~8, ~15, ~25 cm |
| 9–10 | `window` | a bright window or lamp behind the barrels, if there is one (else skip and note it) |
| 11–12 | `neg` | no barrels: the room behind; then the board behind |
| **B — the one-table list** (the room behind; the table above) | | |
| 13–31 | `core`,`core`,`far`,`close`,`topstripe`,`top`,`touch`,`touch`,`occl`,`occl`,`cluster`,`cluster`,`edge`,`clutter`,`clutter`,`neg`,`neg`,`neg`,`held` | exactly the 19 shots of the table above, in that order (`held` only if the robot can hold one; else skip and note it) |
| **C — recordings** (`tm rec`, ten seconds each; you may switch to `simple_cli BarrelTracker` to watch it; note the order) | | |
| r1 | static | two barrels at ~15 cm, nothing moves |
| r2 | pan | turn the robot slowly by hand, about 30° over the ten seconds, the barrels staying in view |
| r3 | enter / leave | slide a barrel into the view from the side and out again |
| r4 | occlusion | wave a hand across the barrels twice |
| **D — calibration** (one **orange** barrel; `show viewer` gives the crosshair, then `tm save`) | | |
| 32–43 | `calib` ×12 | the barrel centred on the vertical crosshair; ruler zero at the robot's front edge; the **near edge of the base at table level** at 0, 5, 10, 15, 20, 25, 30, 50, 100, 150, 200, 300 mm (the bulge overhangs the base by ≈ 3.75 mm, slide the ruler under); ruler out of frame before saving |
| 44 | `horizon` | a mark 43.47 mm above the table on a wall ≥ 1 m away, centred (skip if no wall) |

**Then, the same day** (fill in the light and surface tags; drop from `--scenes` anything you skipped, in the same order as the files):

```zsh
python barrels/tools/import_snaps.py --src barrels/live/snapshots --light <overhead|window|…> --surface <light|…> --scenes \
room,room,room,hand,hand,board,board,board,window,window,neg,neg,core,core,far,close,topstripe,top,touch,touch,occl,occl,cluster,cluster,edge,clutter,clutter,neg,neg,neg,held,calib,calib,calib,calib,calib,calib,calib,calib,calib,calib,calib,calib,horizon --dry-run
# then without --dry-run
python barrels/tools/make_splits.py --v2 --filter 4A8B_<light>_<surface>     # before any method sees the frames
python barrels/tools/box_tool.py --filter <light>_<surface>                   # ≈ 45 frames, ≈ 30 s each; calib frames too
```

Write `data/calib.csv` (`stem, d_ruler_mm`) for the 12 calib frames in order. Move the `rec_<stamp>/` folders somewhere safe (they are gitignored) and say which is which. Commit `data/raw/`, `data/labels/`, `data/splits.json`, `data/calib.csv`.

