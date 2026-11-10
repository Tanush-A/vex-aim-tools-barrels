# HANDOFF.md — moving the work to the Claude Code CLI (2026-11-09)

Written for the next Claude Code session, started in a terminal. Tanush runs the project from the CLI from now on (several sessions, easier context transfer). This file holds what a fresh session cannot get from the docs alone, plus the one warm-up prompt to paste.

## Start the session

```zsh
cd ~/Desktop/Celeste/vex-aim-tools/barrels
source ../../setup.zsh          # venv + aim_fsm on the path; never commit this file (it holds credentials)
claude
```

Started there, the session loads `vex-aim-tools/CLAUDE.md` (one line: read `barrels/CLAUDE.md`) and `barrels/CLAUDE.md` (the rules, the doc map, the start-of-session reading order). Then paste the warm-up below.

## The warm-up prompt (paste as the first message)

```
Read docs/HANDOFF.md, then docs/STATUS.md, docs/TODO.md and docs/HOW-IT-WORKS-SHORT.md, in that order.
Then tell me in plain English, in under 15 lines: what runs today and its numbers, the first unchecked TODO
item and what it needs from me, and anything in HANDOFF you think I should correct. Do not change any file
until I say go. Converse first.
```

## Working agreements that are not written anywhere else

- **Converse first, then code.** A one-line message from Tanush is a conversation turn, not a go signal. Say what you are about to do and wait for "go". Restate the plan in full when the step changes, never "see above".
- **Answer first.** Tanush's time is the bottleneck: answer the question before building anything; front-load what unblocks shooting or labeling; batch walkthroughs rather than interrupting with them.
- **Plain English for main code.** Changes to pipeline, geometry, detector or eval get a walkthrough Tanush acknowledges ("understood") before they land on `barrels`; `HOW-IT-WORKS.md` changes in the same commit. Dave's requirement: Tanush must be able to explain the program. Side tools (labelers, importers, the live `tm` commands) are exempt.
- **Branch convention.** Main-code work that awaits a walkthrough goes on a `wip/<name>` branch rebased on `barrels`; merge is a fast-forward. Docs, data and experiments that need no new code go straight to `barrels`. Commit and push docs every session (the claude.ai mirror and the phone depend on it). Commit messages end with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- **Every number from a committed script.** Experiment script + config → `results/<date>_<name>/` (summaries committed, sheets ignored) → `EXPERIMENTS.md` entry. Pre-register the selection rule before a sweep. Look at the contact sheets before reporting a score: the v2 rule passed boxes 15 % too thin for a week.
- **Never pre-fill labels from the detector.** Ground truth is drawn by Tanush by hand; the detector's output anchoring the labels would score the thing being measured.
- **Test frames** (HOME 5, CAMPUS 10, later NEW's) are never loaded except in the looks planned in `TODO.md` (9b, 10b).
- **Unattended blocks.** After a long block without Tanush, write `docs/OVERNIGHT-<date>.md` in plain English (what changed, numbers, action items) and repeat the short version in chat; archive it once acknowledged.
- **Parallel shell calls share one working directory.** Use absolute paths and `git -C <repo>`.
- **People.** Tanush Aggarwal (CMU SCS, GitHub `Tanush-A`, tanusha@andrew.cmu.edu) owns the project and sends every email; Prof. David Touretzky (he/him, dst@cs.cmu.edu) advises. One email to Dave per finished task, Claude drafts. `docs/NAVIGATOR.md` is read-only for Claude Code.

## Where things are, beyond the doc map

- The live frame from the run with Dave: `live/snapshots/robot_snap0.png` (local, not in git). Recordings: `data/recordings/` (local). The hs model file: `results/2026-11-09_hs_candidate/config.json`; the old v1 model: `results/2026-10-20_v1_test_adaptive/config.json`; `BARRELS_MODEL=<path>` swaps them in every tool and the live programs.
- The sweep that produces the headline numbers: `python barrels/experiments/2026-11-08_seg_hs_v2/run.py` (≈ 1 min; `--body-width 0` = before hardening (f)).
- The box tool: `python barrels/tools/box_tool.py --filter <light>_<surface>` (default camera `boxfit`; `g` shows the expected barrel size at the cursor, assuming the cursor is on the bottom edge).
- Tests: `cd barrels && python -m pytest` (220 as of 2026-11-09, infrastructure only).

## Open items a fresh session should know about (2026-11-09)

- Step 4 of `TODO.md`: the close-up fix (g) is in code; Tanush reviews it at that step and confirms live. The barrel-touching-the-kicker case has no saved frame yet.
- Step 7: partial occlusion was worse live than on the frames; reproduce before fixing.
- Step 3's shoot plan is a draft in `DATA.md` ("Next shoot"); finalize with Tanush before shooting.
- `experiments/2026-11-08_det_hardening/` was last run before (f) and (g); its "old" arm now pins them off, so a re-run reproduces the 2026-11-05 detector.
- Dave's ground-truth boxes group touching barrels; his frames stay indicative. No more data expected from him.

## Per-session memory

The VS Code sessions kept a small memory folder at `~/.claude/projects/-Users-tanush-Desktop-Celeste/memory/`. A CLI session started in `barrels/` reads the folder named after the **git repo root**, `~/.claude/projects/-Users-tanush-Desktop-Celeste-vex-aim-tools/memory/` (checked 2026-11-09; the `...-barrels` copy is not loaded). The five notes were copied there on 2026-11-09. Everything in them is also in this file.
