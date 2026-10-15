# STATUS.md — current state

**Updated:** 2026-10-14.

## Where we are

- Fork + branch verified: origin `Tanush-A/vex-aim-tools-barrels` (public fork of `touretzkyds/vex-aim-tools`), branch `barrels`, upstream set. Note: the fork is named `vex-aim-tools-barrels`, not `vex-aim-tools` (see `DECISIONS.md` 2026-10-14).
- `barrels/` skeleton + all docs created from the planning handoff (archived at `docs/archive/HANDOFF.md`). 10/7 baseline code copied to `experiments/2026-10-07_baselines/`.
- **No segmentation code yet** — by design; docs go to Dave first.
- Prior findings (directional, 19 unlabeled frames): orange body robust across lighting; blue stripe collapses under warm light; wood floods the orange channel; camera does not fully auto-WB. See `EXPERIMENTS.md` 2026-10-07.

## Next steps (in order)

1. ~~Repo setup + skeleton~~ ✓
2. ~~Write the docs~~ ✓ (this session)
3. **Tanush reviews the docs** → fix → commit + push. ← **we are here**
4. Draft the email to Dave (constraints + PROBLEM + general update + directions). Tanush sends it.
5. Build the semi-automatic labeling tool (extend `experiments/2026-10-07_baselines/label_strokes.py`) + unit tests for mask IO.
6. Tanush shoots ~20–30 black-table frames + labels them. **Same session (N-002): measure camera geometry** — tilt via the `aim_kin.py` ruler procedure, focal length from ~5 barrel photos at known distances (width = f·22/d). Record in `constraints.md`, move the horizon gate + bands from the safe rows to the computed ones.
7. Eval harness (per-pixel P/R/IoU per class, per condition) + v1 experiment: RGB-box thresholds with table/background rejection + horizon gating (conservative row until measured). Log it, email Dave.
8. Then: plot RGB clusters (box vs. diagonal) → v1.5 barrel-referenced adaptive thresholds → other color spaces.

## Navigator requests

- N-001 done (2026-10-14): `NAVIGATOR.md` registered in `barrels/CLAUDE.md` (docs table + end-of-session checklist).
- N-004 done (2026-10-14): saturation floor, brightness gate, box-fullness report in `PROBLEM.md`; capture guidance in `DATA.md`; logged in `DECISIONS.md`.
- N-002 done (2026-10-14): geometry-measurement task added to step 6.
- N-003 done (2026-10-14): confusers section in `constraints.md`.
- Review notes applied (2026-10-14): barrel-size provenance, table band default, stripes rule + negative-frame metric in `EVAL.md`. **Deferred:** moving `color_data/` into `barrels/data/raw/` — do it together with the `top&stripe` rename when the labeling tool lands (step 5), so paths change once.

## Housekeeping

- `color_data/` (repo root): rename the two `top&stripe` files → `topstripe` **and** move the set into `barrels/data/raw/` in one commit, when the labeling tool is built (step 5). Claude Code: raise this at the start of step 5.
- Untracked at repo root: `Lab6a.*`, `Lab6b.*`, `color_data.zip`, leftover `handoff/prior_work/` (now copied into `experiments/`) — triage/commit/delete.
- Unknowns to measure with a ruler/robot: barrel dimensions, camera tilt, focal length, horizon row (`constraints.md` table).

## Open questions for Dave

1. Is the eventual output a drop-in aivision replacement (host-side, same spec into worldmap)? Latency budget?
2. How will "good" segmentation be judged (metrics, numeric targets)?
3. Close barrels: full predicted (unclipped) boxes later? Is fixing the world-map side (focal length, the 1.1·w pad) in scope?
4. Can we get `detect.py` + `bounding_boxes*.png` from his zip? Lab 6 student submissions / the ChatGPT watershed conversation?
5. What's on the vex-aim-tools `openvocab` / `depthmap` branches — anything reusable?

## Blockers

None.
