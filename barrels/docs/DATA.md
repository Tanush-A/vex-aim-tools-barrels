# DATA.md — dataset index, naming, labels, splits

**Updated:** 2026-10-14.

## Storage

Small hand-taken sets, **committed to git**: images in `barrels/data/raw/`, masks in `barrels/data/labels/`.

## Naming convention

`{robot}_{light}_{surface}_{scene}_{nn}.png` — e.g. `4A8B_overhead_black_core_01.png`. Use exact tags.

- **robot:** short id, e.g. `4A8B` (= AIM-4A8B6118).
- **light:** describe the source — `overhead`, `lamp`, `window`, `dim`, `side`, `mixed`, or the home-lamp tags `{up,at,away}{cool,mid,warm}` (lamp direction × warmth).
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

## Label format

Full per-pixel masks: same stem + `_mask.png`, single-channel PNG:

| value | meaning |
|---|---|
| 0 | other (table, background, anything non-barrel) |
| 1 | barrel orange (orange body or orange stripe of a blue barrel) |
| 2 | barrel blue (blue body or blue stripe of an orange barrel) |
| 255 | ignore (glare / uncertain) — excluded from eval |

**Labeling tool (to build — task 5):** semi-automatic, extending `experiments/2026-10-07_baselines/label_strokes.py`. User scribbles stroke labels `1` orange, `2` blue, `3` table+background, `4` glare/uncertain → a key triggers auto-grow (GrabCut / seeded region growing) → user fixes with more strokes → save `_mask.png`. Target ~1 min/image.

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
| Home color baselines (10/7) | `~/Desktop/Celeste/vex-aim-tools/color_data/` (repo root, untracked) | 19 PNG, wood desk, 3 lamp directions × 3 warmths | Unlabeled; used for probe-based baselines (`EXPERIMENTS.md` 2026-10-07). **Two filenames contain `top&stripe` → rename to `topstripe`.** To move into `barrels/data/raw/` when triaged. |
| Dave's barrels.zip (9/28) | not in repo | 20 snapshots; snap00–11 have GIMP-drawn GT boxes baked into pixels (not machine-readable) | Reference only; zip lacked `detect.py` + `bounding_boxes*.png` (asked Dave) |
| v1 black-table set | — | planned ~20–30 frames, black table, home light (task 6) | Not captured yet |
