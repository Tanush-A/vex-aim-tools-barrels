# TODO.md — the live task list

**Updated:** 2026-11-08, second unattended block (campus boxes in; the hs candidate scores 0.97 on the campus train frames against 0.41 today; next: Tanush's walkthrough and decision, then adoption). Rule (`CLAUDE.md`): updated every time a task starts, finishes or changes priority, at the same moment as `STATUS.md`. Done items move to the bottom with the date. P0 = this week, in order; P1 = next; P2 = parked but real. Owner in brackets.

## P0 (in this order)

- [ ] **1. Walkthrough + decision on branch `wip/redesign`** [Tanush reads, Claude explains]. `docs/OVERNIGHT-2026-11-08.md` (both parts) in plain English; `HOW-IT-WORKS.md` §1 (last subsection, the hs color model) and §3 ("The hardening", a–e) in full. Decide: (a) merge the detector hardening — five reversible `DetConfig` fields, home 0.91 → 0.93 with the old pixels; (b) the selection rule (proposed: home LOSO v2 ≥ 0.91, zero false detections on every negative of both sessions, then campus v2) — it picks `hs o5 b15 h5-95 m2` once `held_01` is boxed or set aside; (c) `held_01`: box the barrel in the kicker with the `h` flag, or write `held` out of scope in `PROBLEM.md` via `DECISIONS.md`; (d) `clean` on `neg_05` / `clutter_02` (orange cap, glue stick present) — stricter than the definition, fine if intended.
- [ ] **2. Adopt the chosen front end** [Claude, after 1]. Fit once on the 16 home train frames, save to `results/2026-11-xx_hs_default/config.json`, `worldmap_bridge.DEFAULT_MODEL` → it, `detect_image.py` and both live programs follow; `HOW-IT-WORKS` §1 rewritten (hs as the front end, v1 as history); `PROBLEM.md` banner via `DECISIONS.md`. Merge = fast-forward of `barrels` to the branch.
- [ ] **3. Both live programs on campus with the new front end** [Tanush]. `simple_cli BarrelViewer` vs `simple_cli BarrelTracker` in the room scene: one-frame boxes, lag, stickiness, a slow pan; two `tm rec` clips; report in chat. Numbers to compare with: `results/2026-11-08_rec_replay_hs/` (lag 2 frames, 0 blips shown, one persistent false blue box on clutter at the right frame edge).
- [ ] **4. One test run** [Claude]: the 10 campus test frames + the 5 home test frames, the adopted config, once, logged in `EXPERIMENTS.md`, emailed to Dave.
- [ ] **5. One email to Dave** [Claude drafts — draft in `OVERNIGHT-2026-11-08.md`, add 0.97 vs 0.41; Tanush sends].

## P1 (after P0, rough order)

- [ ] **Hidden-stripe barrels** (`cluster_01`, `occl_01`, `occl_02`) [Claude]. Pre-registered idea: allow a stripeless body piece when it sits directly above a found barrel of the same color and is barrel-sized for its row. Score under v2 before and after.
- [ ] **Calibration session + fit** [Tanush shoots and boxes, with a ruler; Claude fits]. The 12 `calib` frames + `horizon` per `DATA.md` (not shot on 2026-11-07: no ruler); the fit script is like `experiments/2026-11-03_geo_boxfit/run.py` but with known distances. Replaces the provisional `AIM_4A8B6118_BOXFIT`; answers f vs tilt.
- [ ] **Mixed-color occlusion** (an orange barrel behind a blue one): the back barrel's lower body reads as a band of the front barrel's body color; needs a rule that a band belongs to the body whose stripe height it matches, not both [Claude]. Seen in `occl_02`.
- [ ] **One test run** (the 5 locked frames) with the detector of the day, one pre-chosen config, logged, emailed to Dave [Claude drafts, Tanush sends]. Only after P0 and the hidden-stripe item are settled, so the one look is not wasted.
- [ ] **Fix `scene:far` tolerance**: at 30 cm the camera error (≈ 5 px) is about the size of the 15 % tolerance, so the geometry can overrule a correct seen bottom (`far_02`, 7 px) [Claude]. Likely resolved by the calibration; re-check after it.
- [ ] **Dave's box labels are per group of touching barrels** (seen 2026-11-08 in `snap_05`: one box around two barrels). Ask Dave whether his detector boxed groups by design; until then his frames score only indicatively under the v2 rule [Tanush asks].

## P2

- [ ] Label the 8 unlabeled Dave frames (`DAVE_office_dark_snap_12–19`) with the box tool once the segmentation shows anything on them [Tanush].
- [ ] Per-robot vs once calibration: decided by shooting the calib session on a second robot when one is available [Tanush + Dave].
- [ ] Knocked-over barrels, wood tables, the world map, the aivision spec: out until Dave says (`PROBLEM.md`). The bridge stub `worldmap_bridge.py` already exists.
- [ ] `NOTES-INBOX.md` triage and `NAVIGATOR.md` requests: nothing open as of 2026-11-06.

## Done

- 2026-11-08 — **Campus frames boxed** by Tanush (31 files; `held_01` unboxed). **hs model with per-class S floors scored under v2** on the branch (`experiments/2026-11-08_seg_hs_v2/`): campus train **0.97 vs 0.41** (today's detector), home 0.93 = v1, nothing on real negatives. Detector hardening (e) (frame-edge stripe) added. Recordings replayed with the hs front end: blips 0 shown, lag 2 frames.

- 2026-11-08 — **Detector hardening implemented** on branch `wip/redesign` (`stripe_mode="cores"`, `dark_stripe=False`, `body_min=0.1`, `height_min/max`), 5 new tests (183 pass), `experiments/2026-11-08_det_hardening/`: home 0.91 → 0.93 (v1 pixels), 0.57 → 0.78 (hue pixels). Awaiting walkthrough (P0-2).
- 2026-11-08 — **hs color model built and swept** on the branch (`pipeline.Config(color_model="hs")`, `experiments/2026-11-08_seg_hs/`): home LOSO 0.93–0.95 at the 15th–20th-percentile S floor, campus 16–17 / 21 right (v1 8), nothing on negatives. The pre-registered rule's pick (5th percentile) regresses at home — rule flaw recorded in `DECISIONS.md`. Not adopted (P0-2/3).
- 2026-11-07 — **Recordings replayed** (`experiments/2026-11-07_rec_replay/`): the old front end finds nothing in the clips; the tracker suppressed all 7 blips offered. Re-run after the front end changes (P0-4).
- 2026-11-07 — **Attribution done** (`experiments/2026-11-07_campus_attribution/`, `EXPERIMENTS.md`): 21 train frames, 7 ok / 9 segmentation / 5 segmentation + detector / 0 detector; mechanisms = the two top-row stages and the RGB boxes; the detector's share = the pre-registered glued-shadow flaw plus one wrong-color box. Segmentation first.
- 2026-11-07 — **Campus capture session** (Tanush): all 31 frames + 4 recordings as planned; imported as `4A8B_campus_light_*`, split 10 test / 21 train (`DATA.md`).

- 2026-11-06 — **First live run** (Tanush, campus table, the back of his laptop as a plain backdrop): window, modes and the robot link work. The detector did not: a floating orange box above the orange barrel, the barrel itself missed, false orange on skin and a laptop edge. Diagnosed from the screenshots (`experiments/2026-11-06_live_first_run/`, `EXPERIMENTS.md`): the stripe finder accepted a dark gap under a false orange smear as a shadowed stripe and rejected the real stripe (band too tall). Raw frames come 2026-11-07.
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
