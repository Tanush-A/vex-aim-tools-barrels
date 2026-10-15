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
- **nn:** two-digit counter per (robot, light, surface, scene) combo.

## Capture procedure

Camera viewer, key `s` → `snapshots/robot_snapN.png`. **The counter resets each session — rename immediately** to the convention above. Robot ops: `RUNBOOK.md`.

**Lighting for v1 black-table frames (N-004):** use **indirect/bounced light** — lamp pointed at the ceiling or wall, not straight at the barrels. Direct light puts specular glare on the lids and body, and glare is out of v1 scope. Frames under overhead/direct light are welcome but must be tagged as such (`overhead`, `lamp`, …); they become later stress tests, not v1 training data. Use a `bounce` light tag for the indirect setup.

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

## Splits

Fixed **train / dev / test**; test is held out early and **never used for tuning** (see `EVAL.md`). Assignments recorded here when data lands:

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
