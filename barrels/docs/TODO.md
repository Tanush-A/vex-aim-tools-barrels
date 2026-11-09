# TODO.md — the live task list

**Updated:** 2026-11-09, rewritten from Tanush's notes after the live run with Dave. **Draft — awaiting Tanush's approval of the order and the data step.** Current work only; history lives in `EXPERIMENTS.md`, `DECISIONS.md` and git. Rule (`CLAUDE.md`): updated every time a task starts, finishes or changes priority, with `STATUS.md`.

**Direction for the week (Tanush, 2026-11-09):** hue + HSV-saturation is the right front end. (1) Fix bugs. (2) Generalize: many light settings, table colors, clutter, occlusion. Claude's eval metrics stay; Tanush's own measure is "scenarios where the vendor detector fails and ours works". Everything on branch `wip/redesign` until the walkthrough is acknowledged.

## Data sets (the tags used below)

| tag | what | labels | where |
|---|---|---|---|
| HOME | 21 frames, white table, window light (`4A8B_window_light_*`), 16 train / 5 test | masks + boxes | `data/raw/` |
| CAMPUS | 31 frames, glass-walled study room, daylight (`4A8B_campus_light_*`), 21 train / 10 test | boxes | `data/raw/` |
| DAVE | 20 office frames, pink desk, lamp (`DAVE_office_*`), 12 with boxes (grouped per touching pair) | boxes, indicative | `data/raw/` |
| WOOD | 5 wood-desk frames (`4A8B_upcool_wood_calib_*`) + 19 lamp-color frames on wood, unlabeled | none | `data/raw/` |
| REC | 4 campus recordings 2026-11-07 (static, pan, enter/leave, hand) | none | `data/recordings/` (local) |
| LIVE-1109 | 1 frame from the run with Dave (close-up under a far barrel) | none | `live/snapshots/robot_snap0.png` (local) |
| **NEW** | the multi-setting collection, step 3 below: not shot yet | boxes by Tanush; slider labels later (step 10) | — |

Test frames (HOME 5, CAMPUS 10) are never loaded except in the one test run at the end.

## In order

- [ ] **0. Walkthrough acknowledgement + merge** [Tanush reads, Claude merges]. `OVERNIGHT-2026-11-08.md` §6 plus the (f) and (g) paragraphs in `HOW-IT-WORKS.md` §3. On "understood": adopt the hs candidate as the default (`DEFAULT_MODEL` → `results/2026-11-09_hs_candidate/config.json`), fast-forward `barrels` to `wip/redesign`, `BARRELS_MODEL` no longer needed. *Added by Claude: everything below builds on the branch, so it has to land.* Data: none.

- [ ] **1. Doc cleanup** [Claude]. The docs are long and convoluted; current facts must be findable in seconds (example: the tilt and focal length actually in use — `AIM_4A8B6118_BOXFIT`: f 400, tilt 22.25°, horizon row 76 — are buried in `constraints.md`). Every doc gets a short "current state" block at the top; history moves below a line or to `archive/`. Order: `constraints.md`, `STATUS.md`, `HOW-IT-WORKS-SHORT.md`, `DATA.md`, `EVAL.md`, `PROBLEM.md`, `CLAUDE.md`, `EXPERIMENTS.md` (index first, entries after), `DECISIONS.md`, `RUNBOOK.md`. Foundation docs change only via `DECISIONS.md`, so the cleanup there is layout, not content. Data: none.

- [ ] **2. Move to the Claude Code CLI** [Claude writes, Tanush switches]. Tanush works better in the CLI (multiple sessions, easier context transfer). Deliverables: `docs/HANDOFF.md` with the context a fresh session needs (state, rules, where things are, open decisions, the current numbers), warm-up prompts per kind of session (experiment session, labeling session, doc session, live session), and the general to-dos; `CLAUDE.md` checked so a fresh session reads the right things first. Data: none.

- [ ] **3. Collect data: the multi-setting set (NEW)** [Tanush shoots and boxes; Claude writes the shot list first]. One session plan, one import, one labeling pass. Needed by 6, 7, 8, 9, 10 below. Contents (draft, Claude finalizes in `DATA.md` before shooting): ≥ 3 light settings (window day, overhead fluorescent, warm lamp; dim if possible) × ≥ 2 table colors (white, a dark or beige table; wood as an out-of-scope probe only) × the scenario list: `close` 0–30 mm in steps (the close-up and kicker cases), `occl` at 25 / 50 / 75 % hidden by a barrel and by clutter, `touch`, `cluster`, `clutter` incl. orange/blue non-barrels, `neg` per setting, `held`/kicker. Plus one `calib` set with a ruler (P1 for a month) and one `horizon` frame. One recording per setting. Boxes with `box_tool.py` (`--cam boxfit`). Data: produces NEW.

- [ ] **4. Fix close-ups** [Claude; done in code 2026-11-09, (g) `cover_rows`; closes when Tanush confirms live]. The close-up under a far barrel now gets its box (LIVE-1109). Open: a barrel touching the kicker — needs a `tm save` of it (same route, probably the same bug). Data: LIVE-1109, HOME `close_*`, CAMPUS `close_01`, NEW `close`.

- [ ] **5. Fix `tm seg` in the live programs** [Claude; side tool, no walkthrough]. `tm seg` opens a second window with only the segmented pixels; the main window dims every pixel not classified as a barrel color. Data: none (live).

- [ ] **6. Clean up the eval** [Claude; eval = main code, walkthrough]. Many sets (HOME, CAMPUS, DAVE, soon NEW) and many tables make it hard to see what is better where. One command (`tools/eval_boxes.py` or a new `tools/report.py`) and the test suite's summary print **one table**: rows = data set × scenario tag, columns = found / missed / false / width ratio / bottom error, for the candidate and for the baseline side by side, with the delta. Metrics unchanged (`EVAL.md`); presentation condensed. Data: HOME, CAMPUS, DAVE train frames; NEW when it exists.

- [ ] **7. Occlusion, the less extreme cases** [Claude; detector, walkthrough]. Live with Dave, a barrel with half its body showing got no box. Expected limit was "stripe fully hidden"; this is worse. First reproduce on frames (CAMPUS `occl_01/02`, `cluster_01`, LIVE frames if saved), attribute (stripe not found? found and refused by `body_min`/`stripe_w_min`? covered by the front barrel's box?), then fix with a pre-registered rule. Data: CAMPUS occl/cluster, HOME occl, NEW `occl` 25/50 %.

- [ ] **8. Histograms: look, then decide** [Claude writes the tool; Tanush looks]. For a frame or a set, every pixel into a 2-D hue × saturation histogram (start 16 × 16, try others), displayed two ways: a 3-D bar plot with each bar in its own color (matplotlib) if it works easily, else two 2-D images (counts in gray, color of the bin). Overlay the labeled-barrel pixels vs the rest. Purpose: see how much H and S actually move between light settings and tables, as the ground for an adaptive hs model. Deliverable: `tools/hs_hist.py` + a short note with the pictures and what they show; then decide what the adaptation should key on. Data: HOME, CAMPUS, DAVE, WOOD (19 lamp frames: 3 directions × 3 warmths, exactly the lighting variation), NEW.

- [ ] **9. Occlusion, the extreme cases** [Claude; detector, walkthrough]. Stripe fully hidden (CAMPUS `occl_02`, `cluster_01`), mixed-color stacking (the back barrel's body reads as a band of the front one). Pre-registered idea: a stripeless body piece directly above a found barrel of the same color, barrel-sized for its row, is a barrel. Best effort this week. Data: CAMPUS occl/cluster, NEW `occl` 75 %.

- [ ] **10. Slider labeling + the adaptive-threshold plan** [Claude builds; Tanush labels; then plan together]. A tool with H and S sliders per class on one image, segmentation updating live; Tanush picks the setting that minimizes false pixels while keeping the barrels; the chosen thresholds per frame are saved as labels (`<stem>_hs.json`). Those per-frame thresholds, plotted against the frame's histogram (step 8), are the data for the adaptive model: what in the frame's H/S distribution predicts the right threshold. Deliverable: `tools/hs_slider.py`, the labels, and a written plan (hypothesis, rule, how it is scored) before any adaptive code. Data: NEW primarily; HOME, CAMPUS, DAVE, WOOD for the spread.

## After the list (when the week's items are done)

- [ ] **One test run** [Claude]: HOME 5 + CAMPUS 10 test frames, the adopted config, once, logged. *Claude's addition.*
- [ ] **Email to Dave** [Claude drafts, Tanush sends]: the week's result in his terms (where the vendor detector fails and ours works). Ask about his grouped boxes. *Claude's addition.*
- [ ] **Blue clutter at the frame edge above the table** (REC r1): a persistent false box; pre-register a rule once seen live again.
- [ ] Wood tables: out of scope (Dave). WOOD frames are used only for lighting variation in step 8.
