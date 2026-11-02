# CLAUDE.md — Barrel Detection (barrels/)

## What this project is

A robust **barrel detector for the VEX AIM robot**, replacing the unreliable vendor detector ("aivision"). Research project: Tanush Aggarwal (CMU SCS, `Tanush-A`) with Prof. David Touretzky (dst@cs.cmu.edu), ~10 hrs/week, fall 2026.

**Current scope (v2.0): barrel detection = one still image in, the same image out with one box per barrel in its color, on the laptop** (spec: the v2 section of `docs/PROBLEM.md`, agreed with Dave 2026-10-30). v1 per-pixel segmentation is frozen (config `afd85483`) as the front end; the v1.5 infrastructure (geometry, eval, `Barrel` type) is in place. Ground positions, the world map, the aivision spec and running on the robot are **out until Dave says so**. **Never correct the image itself (no white balance)**. Plain-English guide to the main code: `docs/HOW-IT-WORKS.md`.

Everything lives in `barrels/`, independent of `aim_fsm` for now. The repo (fork `Tanush-A/vex-aim-tools-barrels`, branch `barrels`; upstream `touretzkyds/vex-aim-tools`) is the **single source of truth** — the claude.ai Project only mirrors `CLAUDE.md` + `barrels/docs/` via manual GitHub sync.

## Environment

- macOS, Python 3.13, venv at `~/Desktop/Celeste/env` (OpenCV, numpy, pytest). The `barrels` package is installed editable: `pip install -e barrels` from the repo root. Tests: `cd barrels && python -m pytest`. Robot ops: `docs/RUNBOOK.md`.
- Code layout: `src/barrels/` (io, labeling, priors, boxfit, pipeline, cv, eval, splits, viz; v1.5 adds geometry, instances, detect_types, eval_det, cleanup, detect_cc, worldmap_bridge; v2 adds detect_stripe), `tools/` (label_tool, instance_tool, box_tool, segment_image, detect_image, eval_masks, eval_boxes, import_snaps, make_splits, attach_measured), `experiments/`, `tests/`.
- Small hand-taken image sets are **committed to git** under `barrels/data/`.

## The docs and when to touch them

**Foundation docs** — the research analog of a spec. SSOT for the current milestone, agreed with Dave, changed **only via a logged decision** in `DECISIONS.md`, re-versioned per milestone:

| Doc | Read when | Update when |
|---|---|---|
| `docs/PROBLEM.md` | Starting any task — it defines v1 | A scope decision is made (log it first) |
| `docs/constraints.md` | Designing an algorithm or experiment | A fact is measured / an unknown is resolved |
| `docs/EVAL.md` | Before running or judging any experiment | The metrics/protocol change (log it first) |

**Running docs** — updated continuously:

| Doc | Read when | Update when |
|---|---|---|
| `docs/STATUS.md` | Start of every session | End of every session + whenever next-steps change |
| `docs/EXPERIMENTS.md` | Before designing a new experiment (what's been tried?) | Every experiment, immediately after it runs |
| `docs/DECISIONS.md` | When wondering "why is it like this?" | Every decision, dated, with alternatives |
| `docs/DATA.md` | Before capturing or using data | Datasets/labels/splits change |
| `docs/RUNBOOK.md` | Operating the robot | Procedures/gotchas change |
| `docs/NOTES-INBOX.md` | Start of session (triage it) | Tanush pastes in notes from phone/browser chats |
| `docs/HOW-IT-WORKS.md` | Before touching main code (pipeline, geometry, detector, eval) | In the same commit as any main-code change |
| `docs/NAVIGATOR.md` | Start of every session (after `STATUS.md`) | **Never** — navigator-owned, read-only for Claude Code. Act on its open requests; reply via `STATUS.md` or `NOTES-INBOX.md` |

## Workflow loop

Every piece of algorithm work follows:

1. **Hypothesis** — state it explicitly, referencing `constraints.md` facts.
2. **Experiment script** — one script per experiment in `experiments/`, parameterized by a config. No one-off notebook pokes for anything that produces a claim.
3. **Run eval** — per `docs/EVAL.md`. Outputs go to `results/<date>_<name>/`.
4. **Log** — entry in `EXPERIMENTS.md`: date, hypothesis, method/params, data split, results table, takeaway, next.
5. **Decide** — if it changes direction, record it in `DECISIONS.md`.
6. **Update `STATUS.md`.**

## Testing policy

- **Unit tests for infrastructure only**: image/mask/instance IO, label parsing, metric computation (pixel and box matching), geometry math. These must be correct for eval numbers to mean anything.
- **Algorithms are judged by eval numbers**, not unit tests. A segmentation method is "good" per `EVAL.md`, never per a hand-picked example.

## Rules

- **No tuning on test.** The held-out test split is fixed early and never touched for tuning (see `EVAL.md`).
- **Reproducibility:** every experiment = a script + config committed to git; generated outputs in `results/<date>_<name>/` (big artifacts gitignored).
- **No image correction.** Adaptive thresholds, per Dave (decision 2026-10-07).
- **Main code is explained before it is committed (2026-11-02):** changes to pipeline, geometry, the detector or the eval get a plain-English walkthrough in chat that Tanush acknowledges, and their section of `docs/HOW-IT-WORKS.md` is updated in the same commit. Side tools (labelers, importers) are exempt. Dave: Tanush must be able to explain the main program himself.
- **Restate the plan:** Tanush asks questions mid-task. When moving to a new step, restate the current plan **in full** — never "see above."
- **One email to Dave per finished task** (Tanush sends; Claude drafts).

## End-of-session checklist

1. Update `STATUS.md` (state, next steps, open questions, blockers).
2. Log any experiments in `EXPERIMENTS.md`, decisions in `DECISIONS.md`.
3. Triage anything new in `NOTES-INBOX.md`; check `NAVIGATOR.md` requests and mark done ones in `STATUS.md` by ID.
4. **Commit and push** (docs included — the claude.ai mirror depends on it).
