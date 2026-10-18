# DATA.md — dataset index, naming, labels, splits

**Updated:** 2026-10-14 (labeling tool built; color_data moved).

## Storage

Small hand-taken sets, **committed to git**: images in `barrels/data/raw/`, masks in `barrels/data/labels/`.

## Naming convention

`{robot}_{light}_{surface}_{scene}_{nn}.png` — e.g. `4A8B_overhead_black_core_01.png`. Use exact tags.

- **robot:** short id, e.g. `4A8B` (= AIM-4A8B6118).
- **light:** describe the source — `bounce` (indirect, lamp at ceiling/wall; the v1 default), `overhead`, `lamp`, `window`, `dim`, `side`, `mixed`, or the home-lamp tags `{up,at,away}{cool,mid,warm}` (lamp direction × warmth).
- **surface:** `black`, `wood`, `light`, `floor`, `paper`, … (extend as needed).
- **scene:**
  - `core` — orange + blue touching ~15 cm, one far ~30 cm, one close ~7 cm
  - `far`, `close`, `top` (top-only view), `topstripe` (top + stripe visible)
  - `touch` (touching barrels), `occl` (occlusion), `cluster`, `edge` (frame edge)
  - `glare`, `shadow`
  - `neg` — no barrels
  - `calib` — one barrel centered straight ahead at a measured distance (for focal length; distances in the calibration table below)
  - `ruler` — a mm ruler laid flat from the robot's front edge straight ahead (for tilt + focal length from row ↔ distance)
- **nn:** two-digit counter per (robot, light, surface, scene) combo.

## Capture procedure

Camera viewer, key `s` → `snapshots/robot_snapN.png`. **The counter resets each session — rename immediately** to the convention above. Robot ops: `RUNBOOK.md`.

**Lighting for v1 black-table frames (N-004):** use **indirect/bounced light** — lamp pointed at the ceiling or wall, not straight at the barrels. Direct light puts specular glare on the lids and body, and glare is out of v1 scope. Frames under overhead/direct light are welcome but must be tagged as such (`overhead`, `lamp`, …); they become later stress tests, not v1 training data. Use a `bounce` light tag for the indirect setup.

## v1 capture plan (2026-10, two sessions)

| session | where | tags | frames |
|---|---|---|---|
| B (2026-10-18, CMU) | light-colored **matte** table, white overhead light | `--light overhead --surface light` | scenes 1–21 + calib 22–26 + ruler 27 (**v1 base set**) |
| ~~A~~ | ~~home black table, warm yellow overhead light~~ | | skipped 2026-10-17 (Tanush's call); a warm-light black-table stress set can be shot in Pittsburgh later |

Direct overhead light puts glare on lids; label glare as ignore (255). On a light table the barrel shadows are visible: label them other (3).

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

### Calibration table (fill in after shooting)

| stem | distance front-edge → barrel near edge (mm) | camera → barrel center (mm) = d + 3 + 11 | measured width (px) |
|---|---|---|---|
| `4A8B_overhead_light_calib_01` | 50 | 64 | |
| `4A8B_overhead_light_calib_02` | 100 | 114 | |
| `4A8B_overhead_light_calib_03` | 150 | 164 | |
| `4A8B_overhead_light_calib_04` | 200 | 214 | |
| `4A8B_overhead_light_calib_05` | 300 | 314 | |

(camera sits ≈ 3 mm behind the front edge per the `aim_kin.py` tilt procedure; barrel radius 11 mm.)

## Label format

Full per-pixel masks: same stem + `_mask.png`, single-channel PNG:

| value | meaning |
|---|---|
| 0 | other (table, background, anything non-barrel) |
| 1 | barrel orange (orange body or orange stripe of a blue barrel) |
| 2 | barrel blue (blue body or blue stripe of an orange barrel) |
| 255 | ignore (glare / uncertain) — excluded from eval |

**Labeling tool:** `tools/label_tool.py` (semi-automatic). Run from the venv:

```zsh
python barrels/tools/label_tool.py                  # all of data/raw
python barrels/tools/label_tool.py --filter black   # subset by filename
```

Scribble strokes `1` orange, `2` blue, `3` table+background, `4` glare/uncertain (stripes get their own color: orange stripe → 1, blue stripe → 2). Press `g` to grow — a marker-based watershed (`src/barrels/labeling.py`) gives every pixel the class of the nearest stroke along image edges; the top 10 rows are auto-seeded as background (above the horizon). Fix with more strokes (they override the grown mask immediately), `n` saves and advances. Anything you don't stroke gets absorbed by its neighbours, so every barrel needs at least one stroke, and put a background stroke on the table **and** on the wall. ~1 min/image. The tool writes two files per image to `data/labels/`: `<stem>_strokes.png` (your strokes, for resuming/re-growing) and `<stem>_mask.png` (the label). Both are committed.

## Labeling rules

- **Stroke every barrel**: `1` on orange bodies, lids, and the orange stripe of blue barrels; `2` on blue bodies, lids, and the blue stripe of orange barrels. A stripe needs its own stroke — the grow step won't cross the stripe edge on its own.
- **Stroke `3`** on the table near and far, on the wall, and on every non-barrel object. Several short strokes beat one long one.
- **Stroke `4` (ignore)** only on specular glare: blown-out white spots on lids/bodies. A bright but still-orange face is barrel, not glare.
- **Reflections** of a barrel in the glossy table → `3` (other). They are not barrel pixels.
- **Shadowed barrel faces** → barrel color. The algorithm may miss them in v1; the label is still the truth.
- **VEX logo** on the lid → the lid's color.
- Don't fuss over 1-px boundaries.
- `top`/`topstripe`/`calib` frames: label normally. `ruler` frame: one `3` stroke, `g`, save (all other).
- `g` to grow, check, fix with more strokes (they override immediately), `g` again if the fill is off, `n` to save and move on.

## Splits

Fixed **train / dev / test**; test is held out early and **never used for tuning** (see `EVAL.md`). Machine-readable copy: `data/splits.json`, written by `tools/make_splits.py` (stratified by condition, seeded, append-only — a stem never moves once assigned). Summary here:

| split | images |
|---|---|
| train | — (none yet) |
| dev | — |
| test | — |

## Dataset index

| set | location | count | status |
|---|---|---|---|
| Home color baselines (10/7) | `barrels/data/raw/4A8B_*_wood_*.png` (moved from repo-root `color_data/` 2026-10-14; `top&stripe` renamed `topstripe`) | 19 PNG, wood desk, 3 lamp directions × 3 warmths | Unlabeled; used for probe-based baselines (`EXPERIMENTS.md` 2026-10-07). Not v1 training data (wood, direct lamp light) — later stress tests. |
| Dave's barrels.zip (9/28) | not in repo | 20 snapshots; snap00–11 have GIMP-drawn GT boxes baked into pixels (not machine-readable) | Reference only; zip lacked `detect.py` + `bounding_boxes*.png` (asked Dave) |
| v1 black-table set | — | planned ~20–30 frames, black table, home light (task 6) | Not captured yet |
