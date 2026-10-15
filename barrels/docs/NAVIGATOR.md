# NAVIGATOR.md: notes from the navigator session

**Ownership: written ONLY by the navigator** (Tanush's planning/Q&A session in the claude.ai Project "Celeste Barrel Detection"). **Claude Code reads this file but never edits it.** It's a one-way channel from the navigator to Claude Code, so Tanush doesn't have to relay things by hand.

How Claude Code uses this file:
- **Read it at the start of every session**, right after `STATUS.md`.
- Act on open items under **Requests** if they fit the current task (or queue them in `STATUS.md`). When one is done, note it in `STATUS.md` with the request ID (e.g. "N-001 done"). The navigator will move it to Closed.
- Treat **Review notes** as suggestions to weigh, not orders. Tanush decides. Foundation-doc changes still go through `DECISIONS.md`.
- To reply to the navigator, write in `STATUS.md` or `NOTES-INBOX.md`, never here.

Precedence: Tanush's direct instructions > foundation docs (`PROBLEM.md`, `constraints.md`, `EVAL.md`) > this file.

---

## Requests (open)

### N-001 (2026-10-14): register this file in CLAUDE.md
Add `docs/NAVIGATOR.md` to the running-docs table in `barrels/CLAUDE.md`: *Read when: start of every session (after STATUS.md). Update when: never; navigator-owned, read-only for Claude Code.* Add it to the end-of-session checklist's triage step too ("check NAVIGATOR.md requests").

### N-002 (2026-10-14): measure tilt + focal length before the v1 experiment
Right now the horizon gate and the background band are both the conservative top ~25 rows, so horizon gating removes almost nothing beyond the band itself. Unknowns #2 (focal length) and #3 (tilt) are cheap (a ruler + ~5 barrel photos at known distances; width = f·22/d) and would move the gate to its real row (~70 nominal), excluding ~45 more rows of background/wall per frame. Suggest slotting a small "measure camera geometry" task into STATUS.md between steps 5 and 7 (Tanush can shoot the calibration frames in the same session as the black-table data).

### N-003 (2026-10-14): add a "known confusers" section to constraints.md
The 10/7 findings are only in EXPERIMENTS.md, but they're constraints the algorithm must respect. Propose a short section in `constraints.md` (logged in DECISIONS.md as a doc update, not a scope change):
- Wood under warm light falls inside naive orange thresholds (H≈15, S≈170).
- Skin (Lab a*≈29) and orange cardboard (a*≈33) sit near barrel orange (a*≈50).
- Barrel **reflections on glossy tables** create orange/blue smears *below* the barrel's ground contact. Likely worse on a glossy black table: check the first black-table frames for this. (Geometry can reject them later: they're below the contact row.)
- The blue stripe darkens and desaturates under warm light (S 236→103, V≈60); it's the weakest class.
- A dark (black) table makes the table prior's color nearly black. Rejection-by-table-similarity then mostly rejects dark pixels, so the table prior alone won't remove bright distractors. That's expected; the background prior and the barrel-referenced v1.5 do that work.

## Review notes

### 2026-10-14: docs review (PROBLEM, constraints, EVAL, STATUS, CLAUDE)
Overall: strong, accurate to the 10/7 meeting and the 10/14 decisions. Ready to send to Dave after small fixes. Specific notes:
- **constraints.md, barrel size:** says "Dave's measurement". The 25×22×6 numbers came from Dave's draft CLAUDE.md in his barrels.zip (and `worldmap.py`), not a confirmed measurement. Suggest: "from Dave's draft spec + worldmap.py; unverified."
- **PROBLEM.md, table band:** "a fixed strip of bottom rows". Say how many (e.g. bottom 80 rows ≈ ground 32–45 mm from the camera nominally) so v1 is reproducible; it's a v1 parameter, so put it in the experiment config and mention the default here.
- **PROBLEM.md, success criteria:** fine to leave numeric targets open for Dave, but propose a strawman in the email (e.g. per-class IoU ≥ 0.8 on black-table test frames, excluding ignore pixels) so he has something concrete to react to.
- **EVAL.md:** add that labels mark **stripes as their own color class** (orange stripe → orange, blue stripe → blue). PROBLEM says it; EVAL/DATA should match so labeling is unambiguous.
- **EVAL.md:** add an image-level sanity metric for negatives (frames with no barrels: % of pixels flagged; target ≈ 0), since P/R/IoU are undefined/uninformative when a class is absent.
- **STATUS.md:** good. Housekeeping item about `color_data/`: moving it into `barrels/data/raw/` before labeling avoids path churn later.

## Navigator context (for Claude Code's awareness)
- The repo's **default branch is `master`**, so the claude.ai Project's GitHub sync only sees `master` (no `barrels/`). Tanush is switching the fork's default branch to `barrels` (GitHub → Settings → General → Default branch). No action needed from Claude Code; keep working on `barrels`.

## Closed
*(none yet)*
