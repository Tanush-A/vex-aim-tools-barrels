# TODO.md — the live task list

**Updated:** 2026-11-06 evening (first live run done: the programs work, the detector does not off the training table; `tm save` / `tm rec` and the multi-frame program `BarrelTracker` built; next: the campus capture session 2026-11-07, then attribution → detector hardening → segmentation redesign). Rule (`CLAUDE.md`): updated every time a task starts, finishes or changes priority, at the same moment as `STATUS.md`. Done items move to the bottom with the date. P0 = this week, in order; P1 = next; P2 = parked but real. Owner in brackets.

## P0 (in this order)

- [ ] **1. Campus capture session, 2026-11-07** [Tanush]. Plan, packing list and shot order: `DATA.md` → "Session 2026-11-07". Block A the scenes that broke the live run (`room`, `hand`, `board`, `window`, `neg`), block B the one-table list, block C four ten-second recordings (`tm rec`), block D the 12 `calib` frames + `horizon`. Import with `import_snaps.py --src barrels/live/snapshots`, then `make_splits.py --v2` and `data/calib.csv`, the same day; box labels after (≈ 45 frames at ≈ 30 s).
- [ ] **2. Attribution of the live failures** [Claude]. The real pipeline on the new frames; per frame: is each miss / false box the segmentation's or the detector's (the stripe-finder log of `experiments/2026-11-06_live_first_run/run.py`, now on real masks). `EXPERIMENTS.md` entry. Its outcome decides whether 3 or 4 goes first.
- [ ] **3. Detector hardening** [Claude designs; walkthrough before commit; `HOW-IT-WORKS.md` §3 in the same commit]. Pre-registered, from the first-run diagnosis: (a) a band with no stripe-colored pixels is not a stripe on its own; (b) the stripe is measured from its own colored pixels, so unlabeled shadow glued to it cannot veto it; (c) a box must hold enough body color. Judged under the v2 rule on the 16 train frames + the new train frames; no test frame touched.
- [ ] **4. Segmentation redesign** [Claude designs, Tanush understands]. Triggers: zero barrel pixels on all 20 of Dave's frames; on the live run, false orange on the board edge, on the glow a barrel throws on the table and on skin, and shaded barrel faces left unlabeled. Candidates: background statistics not tied to the top rows; barrel-referenced color (find the unmistakable cores, grow by similarity, verify with the stripe); illumination-invariant color (chromaticity / opponent channels) instead of raw RGB boxes; a tight orange hue sector that excludes pink and skin. Dev set = the campus frames by scene-held-out CV; Dave's 12 labeled frames stay the outside check. Pre-register the rule before the first sweep.
- [ ] **5. Try both live programs on the new scenes** [Tanush]. `simple_cli BarrelViewer` vs `simple_cli BarrelTracker`: do the one-frame boxes vanish, does a box lag or stick after a barrel moves, do boxes follow a slow pan. Report in chat; Claude adjusts `TrackConfig` (3 of 4, overlap 0.3, forget after 4) only from that report.

## P1 (after P0, rough order)

- [ ] **Hidden-stripe barrels** (`cluster_01`, `occl_01`, `occl_02`) [Claude]. Pre-registered idea: allow a stripeless body piece when it sits directly above a found barrel of the same color and is barrel-sized for its row. Score under v2 before and after.
- [ ] **Calibration fit** [Claude]. The frames are shot in P0 item 1 (block D); the fit script is like `experiments/2026-11-03_geo_boxfit/run.py` but with known distances. Replaces the provisional `AIM_4A8B6118_BOXFIT`; answers f vs tilt.
- [ ] **Mixed-color occlusion** (an orange barrel behind a blue one): the back barrel's lower body reads as a band of the front barrel's body color; needs a rule that a band belongs to the body whose stripe height it matches, not both [Claude]. Seen in `occl_02`.
- [ ] **One test run** (the 5 locked frames) with the detector of the day, one pre-chosen config, logged, emailed to Dave [Claude drafts, Tanush sends]. Only after P0 and the hidden-stripe item are settled, so the one look is not wasted.
- [ ] **Fix `scene:far` tolerance**: at 30 cm the camera error (≈ 5 px) is about the size of the 15 % tolerance, so the geometry can overrule a correct seen bottom (`far_02`, 7 px) [Claude]. Likely resolved by the calibration; re-check after it.
- [ ] **Replay the recordings through the tracker offline** [Claude]: a script that runs the detector on a `rec_<stamp>/` folder frame by frame and reports blips removed, frames of lag, boxes lost on the pan; the numbers behind item 5's impressions.

## P2

- [ ] Label the 8 unlabeled Dave frames (`DAVE_office_dark_snap_12–19`) with the box tool once the segmentation shows anything on them [Tanush].
- [ ] Per-robot vs once calibration: decided by shooting the calib session on a second robot when one is available [Tanush + Dave].
- [ ] Knocked-over barrels, wood tables, the world map, the aivision spec: out until Dave says (`PROBLEM.md`). The bridge stub `worldmap_bridge.py` already exists.
- [ ] `NOTES-INBOX.md` triage and `NAVIGATOR.md` requests: nothing open as of 2026-11-06.

## Done

- 2026-11-06 — **First live run** (Tanush, campus table, grey board as the backdrop): window, modes and the robot link work. The detector did not: a floating orange box above the orange barrel, the barrel itself missed, false orange on skin and a laptop edge. Diagnosed from the screenshots (`experiments/2026-11-06_live_first_run/`, `EXPERIMENTS.md`): the stripe finder accepted a dark gap under a false orange smear as a shadowed stripe and rejected the real stripe (band too tall). Raw frames come 2026-11-07.
- 2026-11-06 — **Multi-frame live program + frame capture**: `live/BarrelTracker.fsm` (a barrel is shown after 3 of the last 4 frames; `src/barrels/tracker.py`), `tm save` / `tm rec` in both programs (`src/barrels/capture.py`), `live/barrel_live.py` as the shared base, `BarrelDetectorHook.render`; 178 tests. Decision logged; `PROBLEM.md` out-of-scope line amended (display-only persistence allowed).
- 2026-11-05 — **Live feed built** (`live/BarrelViewer.fsm` + generated `.py`; `BarrelDetectorHook.default()` / `view()`; detector defaults moved into the hook so the photo path and the robot path share one definition; RUNBOOK + HOW-IT-WORKS §5).
- 2026-11-05 — **Doc cleanup**: `PROBLEM.md` banner + v2 scope/milestones current; `MEETING-2026-10-28`, `OVERNIGHT-*`, `Post-v1-SUMMARY` and the v1 capture plan archived; `STATUS.md` one screen; `HOW-IT-WORKS-SHORT.md` the entry page; `ARCHITECTURE.md` (diagrams) and `barrels/README.md` new; stale "to build" sentences removed; `EXPERIMENTS.md` index; `CLAUDE.md` doc map.
- 2026-11-05 — Walkthrough of detector step 2 and the v2 scoring rule acknowledged by Tanush; committed. **The stripe step is now the default** (`DetConfig.require_stripe=True`, `detect_image.py --step1` for steps 1–3 alone); the step-2 experiment re-run under both rules, numbers identical. `.fsm` location for the live feed decided: `barrels/live/`.
- 2026-11-03 — v2 scoring rule implemented (`eval_det.py` `rule="v2"`, `eval_boxes.py --rule v2`, 9 tests).
- 2026-11-03 — Detector step 2, the stripe anchor: train v2-rule 0.91 vs step 1 0.71 vs floor 0.43.
- 2026-11-03 — `HOW-IT-WORKS.md` rewritten with worked numbers; `HOW-IT-WORKS-SHORT.md` one-pager with the reading map; `MEETING-2026-11-03.md`.
- 2026-11-03 — Dave's barrels.zip imported (20 frames, 12 recovered box sets); finding: v1 segmentation outputs nothing on them (`EXPERIMENTS.md`).
- 2026-11-03 — Tanush reviewed the 21 box labels (11 files changed).
- 2026-11-03 — Detector step 1 + provisional camera committed (272abb0); box tool, box-label IO, `make_splits --v2` committed (7d0787e).
- 2026-11-02 — v2.0 spec (`PROBLEM.md` v2 section), v2 eval rule (`EVAL.md`), box label format and capture plan (`DATA.md`), decision log entry.
