# STATUS.md — current state

**Updated:** 2026-10-19.

## Where we are

- Fork + branch verified: origin `Tanush-A/vex-aim-tools-barrels` (public fork of `touretzkyds/vex-aim-tools`), branch `barrels`, upstream set. Note: the fork is named `vex-aim-tools-barrels`, not `vex-aim-tools` (see `DECISIONS.md` 2026-10-14).
- `barrels/` skeleton + all docs created from the planning handoff (archived at `docs/archive/HANDOFF.md`). 10/7 baseline code copied to `experiments/2026-10-07_baselines/`.
- Docs sent to Dave 2026-10-14; quick reply received, detailed review pending. Package `barrels` (`pip install -e barrels`) has IO, label growing + label tool, eval harness, splits, output rendering. **No segmentation algorithm code yet** — blocked on labeled black-table data.
- Prior findings (directional, 19 unlabeled frames): orange body robust across lighting; blue stripe collapses under warm light; wood floods the orange channel; camera does not fully auto-WB. See `EXPERIMENTS.md` 2026-10-07.

## Next steps (in order)

1. ~~Repo setup + skeleton~~ ✓
2. ~~Write the docs~~ ✓ (this session)
3. ~~Tanush reviews the docs → fix → commit + push.~~ ✓
4. ~~Email to Dave (constraints + PROBLEM + update).~~ ✓ sent 2026-10-14; **reply 2026-10-14** (logged in `DECISIONS.md`): horizon gating OK for v1, f=400 is an estimate, no-barrel frames are a required case. He'll review the repo in detail when back in Pittsburgh — expect more notes.
5. ~~Semi-automatic labeling tool + unit tests for mask IO.~~ ✓ `tools/label_tool.py`, `src/barrels/{io,labeling}.py`, tests pass. Not yet used on a real session by Tanush.
6. ~~Shoot the v1 set~~ ✓ 21 frames (`window_light`, CMU 10/19) + calib/ruler (`upcool_wood`). ~~N-002 geometry~~ ✓ f = 404, tilt = 23.3°, horizon ≈ 66 (`EXPERIMENTS.md` 2026-10-19). **Tanush is labeling** (11/21 masks as of 10/19). ← **we are here**
7. ~~Eval harness~~ ✓ (`src/barrels/{eval,splits,viz}.py`, `tools/{eval_masks,make_splits,import_snaps}.py`, 22 tests). **v1 experiment** once labels exist: RGB-box thresholds + saturation floor + brightness gate + table/background rejection + horizon gating (config flag; conservative row until measured). Log it, email Dave.
8. Then: plot RGB clusters (box vs. diagonal) → v1.5 barrel-referenced adaptive thresholds → other color spaces.

## Navigator requests

- N-001 done (2026-10-14): `NAVIGATOR.md` registered in `barrels/CLAUDE.md` (docs table + end-of-session checklist).
- N-004 done (2026-10-14): saturation floor, brightness gate, box-fullness report in `PROBLEM.md`; capture guidance in `DATA.md`; logged in `DECISIONS.md`.
- N-002 done (2026-10-19): tilt + focal length measured (`EXPERIMENTS.md` 2026-10-19; `constraints.md` updated).
- N-003 done (2026-10-14): confusers section in `constraints.md`.
- Review notes applied (2026-10-14): barrel-size provenance, table band default, stripes rule + negative-frame metric in `EVAL.md`. **Deferred:** moving `color_data/` into `barrels/data/raw/` — do it together with the `top&stripe` rename when the labeling tool lands (step 5), so paths change once.

## Housekeeping

- ~~`color_data/` move + `top&stripe` rename~~ ✓ done 2026-10-14, now `barrels/data/raw/`. `snapshots/4A8B_upcool_wood_closeup_01.png` (gitignored folder) is named per convention — move it into `data/raw/` if wanted.
- Still unmeasured: barrel dimensions with the tape measure (`constraints.md` #1).

## Open questions for Dave

1. Is the eventual output a drop-in aivision replacement (host-side, same spec into worldmap)? Latency budget?
2. How will "good" segmentation be judged (metrics, numeric targets)?
3. Close barrels: full predicted (unclipped) boxes later? Is fixing the world-map side (focal length, the 1.1·w pad) in scope?
4. Can we get `detect.py` + `bounding_boxes*.png` from his zip? Lab 6 student submissions / the ChatGPT watershed conversation?
5. What's on the vex-aim-tools `openvocab` / `depthmap` branches — anything reusable?

## Blockers

None.
