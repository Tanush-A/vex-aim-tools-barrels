# DECISIONS.md — dated decision records

Short records: decision, why, who, alternatives. Newest first.

---

## 2026-10-28 — constraints.md geometry table regenerated from `barrels.geometry` (doc update)

- **Decision:** the nominal geometry table in `constraints.md` is now produced by `python -m barrels.geometry` with the measured barrel (24 mm tall, 25.5 mm bulge, 18 mm ends; silhouette = lid far edge to base near edge). The old table used 25 × 22 mm and no edge offsets (e.g. 126 px wide at 70 mm; it is ≈ 146 px). No scope change.
- **Who:** Claude Code, 2026-10-28 (v1.5 M1).

## 2026-10-28 — v1.5 = detection infrastructure (no detector); instance ground truth; `measured` split

- **Decision (1) scope:** v1 is frozen at config `afd85483`. v1.5 builds what v2 (barrel detection) needs and stops short of a detector: per-barrel instance ground truth, a camera-geometry module, a detection evaluation, cheap pixel-cleanup flags, a connected-components reference detector (a labeled baseline, never tuned), a ruler-measured capture set, and a world-map integration stub. Dave (2026-10-24): accurate barrel detection is the goal, not pixel labeling; use the known barrel size and fixed camera to infer bottom edges in shadow; wood tables are out of scope. The 10/22 v2 proposal (wood data, hue test, seed-and-grow, table-prior cap) is withdrawn.
- **Decision (2) instance labels:** per-barrel ground truth is derived from the existing class masks by an automatic split (stripe-seeded watershed on the distance transform) plus click edits recorded by image point so they can be replayed; stored as `<stem>_inst.png` (uint8 ids) + `<stem>_inst.json` (per-barrel color, box, flags, the class mask's sha1). Tanush chose auto-split + fix over fully manual boxes (2026-10-27).
- **Decision (3) measured split:** frames with ruler-measured barrel positions (`meas` scene) form a fourth split, `measured`, never used for fitting or selection; positions are the barrel axis in the robot base frame (x forward, y left), distance measured to the near edge of the 18 mm base. The wood-desk `calib` frames stay geometry-only (Tanush, 2026-10-27).
- **Why:** jumping straight to a detector was rejected because there is no ground truth or metric to judge one by; the reference detector exists only to prove the harness and set the floor.
- **Who:** Tanush + Claude Code, 2026-10-27/28 (plan approved 2026-10-28).
- **Alternatives:** manual boxes (slower, rejected); detection scored on box overlap only without a measured set (rejected — the planner cares about mm).

## 2026-10-20 — v1 saturation floor is derived per image from the above-horizon rows (band mode); second test evaluation logged

- **Decision:** v1 final config becomes `afd85483` = `ee36a1e9` with `s_min_mode="band"` (floor = 99.5th percentile of the saturation of rows 0–50 + 10, clamped to [20, 120], computed per image; source = above-horizon rows only, never the table rows). The brightness gate stays a fixed constant (40): it guards against sensor noise in near-black pixels, which is a property of the camera, not of the scene. The per-class RGB boxes stay fixed from labels (something must encode what barrel orange/blue look like); adapting them per image is v1.5's job. Because this changes the shipped config after the first test run, the test set was evaluated a **second** time, with the reason recorded in `results/2026-10-20_v1_test_adaptive/config.json`; both numbers are reported (0.844/0.811 fixed, 0.843/0.813 band).
- **Why:** Tanush (2026-10-20): the intent is "see any random photo and classify it", so thresholds should be set from the image, not memorised from a training set. On the real data the two tie exactly (the band floor derives 44–55 by itself); on the synthetic cool-cast probe the fixed floor floods the negatives with blue (7.7 %) and the band floor does not. Table rows are excluded as a source because a close barrel sits in them (top-only frames).
- **Who:** Tanush (intent), Claude Code (implementation + evidence), 2026-10-20.
- **Alternatives:** keep the fixed 50 (rejected — same score, worse robustness, one more hand-set number); include the table rows in the source (rejected — poisoned by close barrels); adapt the brightness gate too (rejected — physical constant); adapt the boxes now (deferred to v1.5 with real multi-light data).

## 2026-10-20 — v1 final config chosen by CV; two documented departures from the mechanical rule

- **Decision:** v1 ships config `ee36a1e9` (`results/2026-10-20_v1_sweep2_pair/configs/`): horizon gate row 50, saturation floor 50, brightness gate 40, **table prior off**, wall prior k = 2.5 (rows 0–50, low-sat fit), RGB box 1–99 % (fit after gates, 3000 px/frame cap), R > B tie rule. LOSO-CV primary 0.810. Two judgment calls on top of the pre-registered rule, both recorded in `EXPERIMENTS.md` 2026-10-20: (1) **horizon_row = 90 not adopted** although it scored +0.022 — the gain comes only from masking the hand in two frames, and 90 is inside the measured horizon band (55–100), so it would be tuning to a confuser at the cost of a physical constraint; (2) **"simplest among ties" means fewest active stages in the ablation round and "unchanged" in the parameter rounds** — otherwise the parameter sweep would switch off the brightness gate (v_min = 0 ties exactly) just because it is a no-op on this table, while the data analysis predicts it matters on dark tables. The stage stays, at 40.
- **Why:** both choices favour the physically motivated setting over a score difference that is either an artifact (the hand) or exactly zero (v_min).
- **Who:** Claude Code, unattended block 2026-10-20; Tanush to confirm.
- **Alternatives:** take the rule literally (horizon 90, v_min 0) — rejected for the reasons above; keep the table prior (base config) — rejected, it is redundant on this table and destroys the top-only frames.

## 2026-10-20 — constraints.md unknowns #4/#5 marked measured for the v1 table (doc update)

- **Decision:** record the pool-frame color analysis (`EXPERIMENTS.md` 2026-10-20) against unknowns #4/#5 in `constraints.md`; they stay open for other surfaces/lights. No scope change.
- **Who:** Claude Code, unattended block, 2026-10-20.

## 2026-10-19 — v1 evaluation protocol: 5-frame test set locked; leave-one-scene-out CV replaces dev; pre-registered selection rule

- **Decision:** (1) **Test set = 5 frames**, picked deterministically by `splits.pick_test` (seed 0: one frame from each of the two largest scene groups, `core` and `neg`, then one from three of the six two-frame scenes): `core_04, edge_02, far_01, neg_03, touch_01`. `top_01` and `topstripe_01` are excluded from test (the close/top-only case is out of v1 scope); they stay in the pool, are predicted and reported, but are **excluded from the headline score**. (2) The **dev split is empty**; all tuning uses **leave-one-scene-out (LOSO) cross-validation over the 16 pool frames** (10 scene groups → 10 folds; every pool frame is predicted exactly once by a model that never saw its scene). (3) **Pre-registered selection rule**, fixed before any sweep: primary score = mean of pooled orange IoU and pooled blue IoU over in-scope positive pool frames; any config with pooled negative-frame false-positive rate > 0.5 % for either class is disqualified; differences < 0.02 in the primary score count as "no difference" unless the sign is consistent across ≥ 6 of the 7 positive folds, in which case prefer the simplest setting; at most two coordinate-descent passes. The test set is evaluated **once**, with the single chosen config.
- **Why:** with 16 tuning frames a single 4-frame dev split is a noisy judge (Tanush's k-fold suggestion). Frames of one scene were shot seconds apart and are near-duplicates, so folds must be grouped by scene or the CV score leaks. Selecting a config by CV and then reporting that same CV score is biased (Varma & Simon 2006; Cawley & Talbot 2010), so the untouched test set is the only headline number. The 0.02 / 0.5 % thresholds are written down in advance so the sweep can't be read selectively afterwards.
- **Who:** Tanush chose "5 fixed test + k-fold on 16" on 2026-10-19; details by Claude Code.
- **Alternatives:** leave-one-out over all 21 with no fixed test (rejected — violates EVAL.md and leaks between same-scene frames); per-frame k-fold (rejected — same leak); keep a 4-frame dev split (rejected — too noisy).

## 2026-10-14 — Dave's reply to the first update (logged 2026-10-18)

- **Decision / facts:** (1) **Horizon gating stays in v1** — Dave: fine to include, probably little effect in practice. Kept as a config flag. (2) **Focal length 400 is an estimate**, no official value, likely varies per camera — calibration of AIM-4A8B6118 stands (N-002). (3) **Frames with no barrels are a required case** — "you should not assume that an image always contains some orange or blue barrel pixels." Added to `PROBLEM.md` Input and to the v1.5 fallback rule; `constraints.md` scene assumptions; already covered by `neg` frames in the capture plan and the negative-frame FP-rate metric in `EVAL.md`.
- **Why:** Dave's email 2026-10-14 (he will review the repo in detail once back in Pittsburgh).
- **Who:** Dave; logged by Tanush/Claude Code.

## 2026-10-17 — v1 base set = light campus table under white light; warm black table = stress set

- **Decision:** the v1 "simple scene" data is shot on a light-colored matte table under normal white overhead light at CMU (tags `overhead_light`), 21 scene frames + 5 calib + 1 ruler. The home black table is only available under warm yellow overhead light; that set (21 frames, tags `overheadwarm_black`) is shot too, but as the first stress condition, not the v1 base.
- **Why:** under the yellow light the camera (no auto-WB) renders the glossy black table as dark orange-brown and the blue barrel as gray — the warm-light failure mode from 10/7, worse. That is not a "simple scene." Daylight on the black table isn't possible before Tanush leaves CA (2026-10-18). A matte light table under white light is the easiest case for the saturation floor and keeps the blue stripe saturated.
- **Who:** Tanush, 2026-10-17.
- **Alternatives:** black table + yellow light as the v1 base (rejected — would make v1 a stress test).
- **Update 2026-10-17:** Tanush skipped the black-table/warm-light set entirely; only the CMU set is shot. A warm-light stress set can be captured in Pittsburgh later.

## 2026-10-14 — Doc updates from the navigator review (N-003 + review notes)

- **Decision:** documentation updates, no scope change. `constraints.md`: barrel size attributed to Dave's draft spec + `worldmap.py` and marked unverified; new "Known confusers" section (wood under warm light, skin, orange cardboard, glossy-table reflections, warm-light blue stripe, expected black-table behavior). `PROBLEM.md`: table band default = bottom 80 rows, a config parameter to revisit after tilt/focal length are measured. `EVAL.md`: stripes scored as their own color; negative-frame false-positive-rate metric. `STATUS.md`: new step to measure tilt + focal length before the v1 experiment (N-002).
- **Why:** confusers are exploitable constraints and belong in the constraints doc even though v1 scenes exclude them. A stated band default makes v1 reproducible. The stripe rule prevents label drift between docs. Negative frames need their own metric because IoU is undefined without positives. Measuring the geometry first moves the horizon gate from the safe row (~25) to its real row (~70).
- **Who:** Tanush, 2026-10-14, on navigator suggestions.
- **Alternatives:** keep confusers only in `EXPERIMENTS.md` (rejected — the lab notebook is not what experiments cite); leave the band size to the config only (rejected — the spec should name the default).

## 2026-10-14 — v1 method details, approved by Tanush (N-004)

- **Decision:** v1 adds (1) a **saturation floor** `max(R,G,B) − min(R,G,B) ≥ s_min`, (2) a **minimum-brightness gate** `brightness ≥ v_min`, (3) a **box-fullness report** alongside the RGB box (fraction of box volume occupied by labeled barrel pixels + 3D scatter), and (4) **data-capture guidance**: shoot v1 black-table frames under indirect/bounced light, tag direct/overhead-light frames for later stress tests. `s_min`, `v_min` are config parameters fit on train/dev.
- **Why:** from Dave's vision-pipeline slides (`NAVIGATOR.md` K-1): saturation is the CMVision-era test for "is this colored at all," and the RGBK map gates color classes on minimum Y because chroma is noise in dark pixels. Black table, gray wall, and white glare are all low-saturation, so these two gates do cheap, safe work before the box. Both are pixel thresholds, not image correction. Box fullness answers Dave's box-vs-diagonal question with a number. Indirect light keeps glare (out of scope) out of the v1 data.
- **Who:** Tanush approved 2026-10-14 (via navigator, N-004).
- **Alternatives:** RGB box alone (rejected — the box would have to be stretched to cover dark/desaturated barrel pixels and would swallow the table); direct lamp light for v1 data (rejected — glare is out of scope and would contaminate labels).

## 2026-10-14 — Horizon gating is in v1

- **Decision:** v1 rejects every pixel above the horizon row as non-barrel, regardless of color. Gate at the conservative row (~25) until tilt and focal length of AIM-4A8B6118 are measured, then move to the computed row.
- **Why:** it's one comparison per pixel and geometrically sound (barrel height 25 mm < camera height 43.47 mm, so no barrel pixel can be above the horizon). The conservative row protects against a wrong horizon estimate (plausible range ≈ row 26–126) erasing real barrels. Other geometry (expected size by row) stays deferred.
- **Who:** Tanush, 2026-10-14. To confirm with Dave in the first update email.
- **Alternatives:** keep all geometry out of v1 (rejected — leaves an easy, safe constraint unused); gate at the nominal row 70 now (rejected — too risky until measured).

## 2026-10-14 — Fork is named `vex-aim-tools-barrels`

- **Decision:** origin = `github.com/Tanush-A/vex-aim-tools-barrels` (public fork of `touretzkyds/vex-aim-tools`), not `Tanush-A/vex-aim-tools` as originally planned. Keep the name.
- **Why:** that's how the fork was created; it's a true GitHub fork of upstream, so PRs and syncs work the same. Renaming buys nothing.
- **Who:** Tanush (setup), noted during repo verification.

## 2026-10-14 — Docs-first research workflow; repo is the SSOT

- **Decision:** write all foundation + running docs (`PROBLEM.md`, `constraints.md`, `EVAL.md`, `EXPERIMENTS.md`, `DECISIONS.md`, `STATUS.md`, `DATA.md`, `RUNBOOK.md`, `NOTES-INBOX.md`) before any algorithm code; send `constraints.md` + `PROBLEM.md` + an update/directions email to Dave first, then one email per finished task. The repo is the single source of truth; the claude.ai Project mirrors `CLAUDE.md` + `barrels/docs/` via manual sync. Commit + push docs every session.
- **Why:** Dave's meta-strategy (AI proposes/implements/evaluates algorithms) needs a very solid problem spec with every exploitable constraint, plus reproducible experiment logs.
- **Who:** Tanush, 2026-10-14.
- **Alternatives:** code-first with docs later (rejected — the spec IS the research artifact Dave asked for); claude.ai Project as SSOT (rejected — git history + review beat a chat mirror).

## 2026-10-14 — Repo layout: everything in `barrels/`, data in git

- **Decision:** all barrel work in a separate `barrels/` subfolder, independent of `aim_fsm` for now, on branch `barrels`. Small hand-taken image sets committed to git under `barrels/data/`.
- **Why:** clean separation from Dave's upstream code; datasets are small, hand-made, and need to travel with the repo for reproducibility and the claude.ai mirror.
- **Who:** Tanush, 2026-10-14.
- **Alternatives:** integrate into `aim_fsm` now (rejected — premature until there's a working detector); external data storage (rejected — overkill for ~dozens of PNGs).

## 2026-10-14 — v1 data: black table at home, then Pittsburgh tables

- **Decision:** v1 dataset = simple scenes on a black table at Tanush's home (CA, ordinary home light), no distractors; then Pittsburgh with different tables. Goal: table-agnostic.
- **Why:** start with the easiest controlled surface; the 10/7 baselines showed the hard failure modes (warm light + wood) — walk before running.
- **Who:** Tanush, 2026-10-14.

## 2026-10-07 — v1 = color segmentation only, no bounding boxes

- **Decision:** step 1 is per-pixel color segmentation: one 640×480 frame in → orange image + blue image out (flat (255,128,0) / (0,100,255) on gray (128,128,128)). Bounding boxes, geometry checks, close-range top-only barrels, glare/shadow handling, learned classifiers: all deferred.
- **Why:** nail the core pixel question first; everything downstream depends on it.
- **Who:** Dave (meeting 10/7), scope finalized by Tanush 10/14.
- **Alternatives:** go straight to boxes like the old Claude detector (rejected — that's what failed: merged barrels, background FPs, missed close barrels).

## 2026-10-07 — Adaptive thresholding; NO image correction

- **Decision:** adjust thresholds per image; **never white-balance or otherwise correct the image.** Use the table prior (bottom rows = non-barrel samples) and background prior (top rows = non-barrel) to adapt. Planned v1.5: barrel-referenced thresholds (use high-confidence barrel pixels as the in-image color reference, re-fit iteratively).
- **Why:** Dave's call (10/7). Also empirically: gray-world WB fixed the warm-light failures but over-corrected when the table dominated the scene (wood-dominated → grays go blue). Per-image adaptation is necessary; a global "average is gray" assumption fails on a dominant table color.
- **Who:** Dave (meeting 10/7).
- **Alternatives:** gray-world / other WB (rejected, above); stored reference table color (rejected — no ground truth in a new setting).

## 2026-10-07 — v1 threshold shape: axis-aligned RGB box

- **Decision:** v1 thresholds = an axis-aligned box in RGB. First plot labeled barrel pixels in 3D RGB to see the cluster shape. If elongated/diagonal, move to fancier functions or other color spaces (HSV, YUV, Lab) after v1.
- **Why:** simplest thing that can work; the cluster-shape plot tells us if/why it can't.
- **Who:** Dave (meeting 10/7).
