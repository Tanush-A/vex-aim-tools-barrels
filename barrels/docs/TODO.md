# TODO.md — the live task list

**Updated:** 2026-11-05 (step 2 + v2 rule committed; next: the doc cleanup). Rule (`CLAUDE.md`): updated every time a task starts, finishes or changes priority, at the same moment as `STATUS.md`. Done items move to the bottom with the date. P0 = this week, in order; P1 = next; P2 = parked but real. Owner in brackets.

## P0 (in this order)

- [ ] **2. Clean up the docs — everything human-readable and clean** [Claude, Tanush reviews]. Plan: (1) `PROBLEM.md` is the spec — said in `CLAUDE.md` and at the top of `PROBLEM.md` (done 2026-11-03), with `EVAL.md` = how it is scored and `constraints.md` = the physical facts; (2) move `MEETING-2026-10-28.md`, `OVERNIGHT-*.md`, `Post-v1-SUMMARY.md` and the v1 capture plan from `DATA.md` into `docs/archive/`; (3) cut `STATUS.md` to one screen (state, today, next, blockers — the history lives in `EXPERIMENTS.md`/`DECISIONS.md`); (4) one guide, not two: `HOW-IT-WORKS-SHORT.md` is the entry page, `HOW-IT-WORKS.md` the long form it links to; (5) remove every "to be written / to build / arrives with M2" sentence that is now false; (6) `PROBLEM.md` v2 milestones to match this file; (7) `README.md` in `barrels/` with the five commands a new reader needs; (8) log the 2026-11-03 meeting outcome in `DECISIONS.md` (priority: live feed → segmentation → rest of the boxes) and add Dave's notes to `MEETING-2026-11-03.md`.
- [ ] **3. Live feed on the robot** [Claude writes, Tanush runs and understands]. Dave's spec (2026-11-03 meeting): a state machine (`genfsm X.fsm` → `simple_cli X`, 1-second loop; example `ImageChomper.fsm` in Downloads, lecture-1 slides) that takes `robot.cameraimage` (numpy array), runs segmentation + detector, draws the boxes with OpenCV and shows them with `cv2.imshow`; a key toggles to the segmentation view. Lives in `barrels/live/BarrelViewer.fsm` (decided 2026-11-05: `simple_cli` imports from the current directory, so any folder works; ours keeps all barrel work in `barrels/`). Glue only — the work is `worldmap_bridge.BarrelDetectorHook`; convert RGB→BGR in, BGR→RGB out for Dave's PyQt `imshow`. This is the first time `barrels` meets `aim_fsm`.
- [ ] **4. Segmentation redesign (pulled forward from P1 by the meeting)** [Claude designs, Tanush understands]. Trigger: zero barrel pixels on all 20 of Dave's frames. Candidates: background statistics not tied to the top rows; barrel-referenced color (find the unmistakable cores, grow by similarity, verify with the stripe); illumination-invariant color (chromaticity / opponent channels) instead of raw RGB boxes; a tight orange hue sector that excludes pink. Tuned on our frames by scene-held-out CV; Dave's 12 labeled frames stay the outside check. Pre-register the rule before the first sweep.

## P1 (after P0, rough order)

- [ ] **Hidden-stripe barrels** (`cluster_01`, `occl_01`, `occl_02`) [Claude]. Pre-registered idea: allow a stripeless body piece when it sits directly above a found barrel of the same color and is barrel-sized for its row. Score under v2 before and after.
- [ ] **Calibration session** (12 `calib` frames + `horizon`, `DATA.md`) [Tanush shoots and boxes, Claude fits]. Replaces the provisional `AIM_4A8B6118_BOXFIT`; answers f vs tilt. Fit script to write: like `experiments/2026-11-03_geo_boxfit/run.py` but with known distances.
- [ ] **Mixed-color occlusion** (an orange barrel behind a blue one): the back barrel's lower body reads as a band of the front barrel's body color; needs a rule that a band belongs to the body whose stripe height it matches, not both [Claude]. Seen in `occl_02`.
- [ ] **One test run** (the 5 locked frames) with the stripe step, one pre-chosen config, logged, emailed to Dave [Claude drafts, Tanush sends]. Only after P0 and the hidden-stripe item are settled, so the one look is not wasted.
- [ ] **Shoot the one-table session** (19-shot list, twice if time) and label boxes; splits via `make_splits.py --v2` [Tanush]. Needed for tuning the segmentation redesign and the final run.
- [ ] **Fix `scene:far` tolerance**: at 30 cm the camera error (≈ 5 px) is about the size of the 15 % tolerance, so the geometry can overrule a correct seen bottom (`far_02`, 7 px) [Claude]. Likely resolved by the calibration; re-check after it.

## P2

- [ ] Label the 8 unlabeled Dave frames (`DAVE_office_dark_snap_12–19`) with the box tool once the segmentation shows anything on them [Tanush].
- [ ] Per-robot vs once calibration: decided by shooting the calib session on a second robot when one is available [Tanush + Dave].
- [ ] Knocked-over barrels, wood tables, the world map, the aivision spec, running on the robot: out until Dave says (`PROBLEM.md`). The bridge stub `worldmap_bridge.py` already exists.
- [ ] `NOTES-INBOX.md` triage and `NAVIGATOR.md` requests: nothing open as of 2026-11-03.

## Done

- 2026-11-05 — Walkthrough of detector step 2 and the v2 scoring rule acknowledged by Tanush; committed. **The stripe step is now the default** (`DetConfig.require_stripe=True`, `detect_image.py --step1` for steps 1–3 alone); the step-2 experiment re-run under both rules, numbers identical. `.fsm` location for the live feed decided: `barrels/live/`.
- 2026-11-03 — v2 scoring rule implemented (`eval_det.py` `rule="v2"`, `eval_boxes.py --rule v2`, 9 tests).
- 2026-11-03 — Detector step 2, the stripe anchor: train v2-rule 0.91 vs step 1 0.71 vs floor 0.43.
- 2026-11-03 — `HOW-IT-WORKS.md` rewritten with worked numbers; `HOW-IT-WORKS-SHORT.md` one-pager with the reading map; `MEETING-2026-11-03.md`.
- 2026-11-03 — Dave's barrels.zip imported (20 frames, 12 recovered box sets); finding: v1 segmentation outputs nothing on them (`EXPERIMENTS.md`).
- 2026-11-03 — Tanush reviewed the 21 box labels (11 files changed).
- 2026-11-03 — Detector step 1 + provisional camera committed (272abb0); box tool, box-label IO, `make_splits --v2` committed (7d0787e).
- 2026-11-02 — v2.0 spec (`PROBLEM.md` v2 section), v2 eval rule (`EVAL.md`), box label format and capture plan (`DATA.md`), decision log entry.
