# DECISIONS.md — dated decision records

Short records: decision, why, who, alternatives. Newest first.

---

## 2026-10-17 — v1 base set = light campus table under white light; warm black table = stress set

- **Decision:** the v1 "simple scene" data is shot on a light-colored matte table under normal white overhead light at CMU (tags `overhead_light`), 21 scene frames + 5 calib + 1 ruler. The home black table is only available under warm yellow overhead light; that set (21 frames, tags `overheadwarm_black`) is shot too, but as the first stress condition, not the v1 base.
- **Why:** under the yellow light the camera (no auto-WB) renders the glossy black table as dark orange-brown and the blue barrel as gray — the warm-light failure mode from 10/7, worse. That is not a "simple scene." Daylight on the black table isn't possible before Tanush leaves CA (2026-10-18). A matte light table under white light is the easiest case for the saturation floor and keeps the blue stripe saturated.
- **Who:** Tanush, 2026-10-17.
- **Alternatives:** black table + yellow light as the v1 base (rejected — would make v1 a stress test); skip the black-table set (rejected — free stress data, 15 minutes).

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
