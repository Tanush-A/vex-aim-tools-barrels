# barrels — a barrel detector for the VEX AIM robot

One 640×480 camera image in, the same image out with one box around every barrel, yellow for an orange barrel and green for a blue one. The bottom edge of each box is the number the robot's world map will eventually use, so it is the edge that has to be right. Research project: Tanush Aggarwal (CMU SCS) with Prof. David Touretzky, fall 2026. The spec is `docs/PROBLEM.md`.

Where it stands (2026-11-05): on the 16 training frames the detector scores **0.91** mean F1 under the strict rule (overlap ≥ ½ and bottom edge within a tenth of the height), against 0.43 for one-box-per-blob, with nothing drawn on empty frames. It fails on Dave's office frames because the color front end assumes the rows above the horizon are plain wall; that redesign is next. Current state and the task list: `docs/STATUS.md`, `docs/TODO.md`.

## Setup

```zsh
source ~/Desktop/Celeste/setup.zsh        # the venv (Python 3.13, numpy, OpenCV, pytest) + aim_fsm on the path
pip install -e barrels                     # once, from the repo root; the package is `barrels`
```

## The commands

```zsh
cd barrels && python -m pytest                                              # 1. the tests (infrastructure only)
python barrels/tools/detect_image.py barrels/data/raw/4A8B_window_light_touch_02.png   # 2. the detector on a photo → results/detect_image/<stem>_boxes.png
python barrels/tools/segment_image.py barrels/data/raw/4A8B_window_light_touch_02.png  # 3. the color segmentation alone → results/segment_image/
python barrels/experiments/2026-11-03_det_step2/run.py --rule v2            # 4. reproduce the headline number (floor / steps 1–3 / full detector)
cd barrels/live && genfsm BarrelViewer.fsm && simple_cli BarrelViewer       # 5. live on the robot (robot on, setup.zsh sourced; docs/RUNBOOK.md)
python barrels/tools/box_tool.py --filter window                            # 6. draw the ground-truth boxes on new frames
```

`detect_image.py --step1` runs the detector without the stripe step, for comparison. In the live view, type `tm seg`, `tm boxes` or `tm both` at the `C>` prompt to switch between the segmentation and the boxes.

## Where to read

| want | read |
|---|---|
| the one-page explanation of how it works | `docs/HOW-IT-WORKS-SHORT.md` |
| the same with worked numbers, per module | `docs/HOW-IT-WORKS.md` |
| how the files fit together (diagrams) | `docs/ARCHITECTURE.md` |
| what we are building, exactly | `docs/PROBLEM.md` (the spec), `docs/constraints.md` (the physical facts), `docs/EVAL.md` (how it is scored) |
| what happened and why | `docs/EXPERIMENTS.md` (every experiment, newest first), `docs/DECISIONS.md` (every decision, with alternatives) |
| the data: naming, labels, splits, what to shoot | `docs/DATA.md` |
| the robot: setup, wifi, the live feed | `docs/RUNBOOK.md` |
| the working rules for Claude Code | `CLAUDE.md` |

Older write-ups (meeting briefs, overnight summaries, the v1 summary) are in `docs/archive/`.

## Layout

`src/barrels/` the package · `tools/` one CLI per job · `live/` the robot program · `experiments/<date>_<name>/` one script per experiment · `results/<date>_<name>/` what it wrote · `data/` frames, labels, splits · `tests/` · `docs/`. Details and a module table: `docs/ARCHITECTURE.md`.
