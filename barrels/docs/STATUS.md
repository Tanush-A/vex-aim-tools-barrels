# STATUS.md — current state

**Updated:** 2026-10-17.

## Where we are

- Fork + branch verified: origin `Tanush-A/vex-aim-tools-barrels` (public fork of `touretzkyds/vex-aim-tools`), branch `barrels`, upstream set. Note: the fork is named `vex-aim-tools-barrels`, not `vex-aim-tools` (see `DECISIONS.md` 2026-10-14).
- `barrels/` skeleton + all docs created from the planning handoff (archived at `docs/archive/HANDOFF.md`). 10/7 baseline code copied to `experiments/2026-10-07_baselines/`.
- Docs sent to Dave 2026-10-14. Package `barrels` (`pip install -e barrels`) has IO, label growing + label tool, eval harness, splits, output rendering. **No segmentation algorithm code yet** — blocked on labeled black-table data.
- Prior findings (directional, 19 unlabeled frames): orange body robust across lighting; blue stripe collapses under warm light; wood floods the orange channel; camera does not fully auto-WB. See `EXPERIMENTS.md` 2026-10-07.

## Next steps (in order)

1. ~~Repo setup + skeleton~~ ✓
2. ~~Write the docs~~ ✓ (this session)
3. ~~Tanush reviews the docs → fix → commit + push.~~ ✓
4. ~~Email to Dave (constraints + PROBLEM + update).~~ ✓ sent 2026-10-14 (`NAVIGATOR.md` K-5). Awaiting reply; horizon gating stays in v1 as a config flag until he answers.
5. ~~Semi-automatic labeling tool + unit tests for mask IO.~~ ✓ `tools/label_tool.py`, `src/barrels/{io,labeling}.py`, tests pass. Not yet used on a real session by Tanush.
6. **Tanush shoots session A (black/warm, 21) tonight and session B (light table/white, 27 incl. calib + ruler) at CMU 10/18, imports, labels (`DATA.md` → v1 capture plan).** ← **we are here** **Same session (N-002): measure camera geometry** — tilt via the `aim_kin.py` ruler procedure, focal length from ~5 barrel photos at known distances (width = f·22/d). Record in `constraints.md`, move the horizon gate + bands from the safe rows to the computed ones.
7. ~~Eval harness~~ ✓ (`src/barrels/{eval,splits,viz}.py`, `tools/{eval_masks,make_splits,import_snaps}.py`, 22 tests). **v1 experiment** once labels exist: RGB-box thresholds + saturation floor + brightness gate + table/background rejection + horizon gating (config flag; conservative row until measured). Log it, email Dave.
8. Then: plot RGB clusters (box vs. diagonal) → v1.5 barrel-referenced adaptive thresholds → other color spaces.

## Navigator requests

- N-001 done (2026-10-14): `NAVIGATOR.md` registered in `barrels/CLAUDE.md` (docs table + end-of-session checklist).
- N-004 done (2026-10-14): saturation floor, brightness gate, box-fullness report in `PROBLEM.md`; capture guidance in `DATA.md`; logged in `DECISIONS.md`.
- N-002 done (2026-10-14): geometry-measurement task added to step 6.
- N-003 done (2026-10-14): confusers section in `constraints.md`.
- Review notes applied (2026-10-14): barrel-size provenance, table band default, stripes rule + negative-frame metric in `EVAL.md`. **Deferred:** moving `color_data/` into `barrels/data/raw/` — do it together with the `top&stripe` rename when the labeling tool lands (step 5), so paths change once.

## Housekeeping

- ~~`color_data/` move + `top&stripe` rename~~ ✓ done 2026-10-14, now `barrels/data/raw/`. `snapshots/4A8B_upcool_wood_closeup_01.png` (gitignored folder) is named per convention — move it into `data/raw/` if wanted.
- Unknowns to measure with a ruler/robot: barrel dimensions, camera tilt, focal length, horizon row (`constraints.md` table).

## Open questions for Dave

1. Is the eventual output a drop-in aivision replacement (host-side, same spec into worldmap)? Latency budget?
2. How will "good" segmentation be judged (metrics, numeric targets)?
3. Close barrels: full predicted (unclipped) boxes later? Is fixing the world-map side (focal length, the 1.1·w pad) in scope?
4. Can we get `detect.py` + `bounding_boxes*.png` from his zip? Lab 6 student submissions / the ChatGPT watershed conversation?
5. What's on the vex-aim-tools `openvocab` / `depthmap` branches — anything reusable?

## Blockers

None.
