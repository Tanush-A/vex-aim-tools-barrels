# NAVIGATOR.md: notes from the navigator session

**Ownership: written ONLY by the navigator** (Tanush's planning/Q&A session in the claude.ai Project "Celeste Barrel Detection"). **Claude Code reads this file but never edits it.** It's a one-way channel from the navigator to Claude Code, so Tanush doesn't have to relay things by hand.

How Claude Code uses this file:
- **Read it at the start of every session**, right after `STATUS.md`.
- **Requests** = action items. Act on open ones if they fit the current task (or queue them in `STATUS.md`). When one is done, note it in `STATUS.md` with its ID (e.g. "N-001 done"). The navigator moves it to Closed.
- **Knowledge** = background from navigator ↔ Tanush discussions: things to know, ideas parked for later, context behind decisions. Not action items. Use it when designing experiments or planning later milestones. **Don't implement anything from Knowledge unless a Request or Tanush says to.**
- **Review notes** = suggestions to weigh. Tanush decides. Foundation-doc changes still go through `DECISIONS.md`.
- To reply to the navigator, write in `STATUS.md` or `NOTES-INBOX.md`, never here.

Precedence: Tanush's direct instructions > foundation docs (`PROBLEM.md`, `constraints.md`, `EVAL.md`) > this file.

_Last updated: 2026-10-14 (evening)._

---

## Requests (open)

### N-001 (2026-10-14): register this file in CLAUDE.md
Add `docs/NAVIGATOR.md` to the running-docs table in `barrels/CLAUDE.md`: *Read when: start of every session (after STATUS.md). Update when: never; navigator-owned, read-only for Claude Code.* Also add "check NAVIGATOR.md requests" to the end-of-session checklist's triage step.

### N-002 (2026-10-14): measure tilt + focal length before the v1 experiment
Right now the horizon gate and the background band are both the conservative top ~25 rows, so horizon gating removes almost nothing beyond the band itself. Unknowns #2 (focal length) and #3 (tilt) are cheap (a ruler + ~5 barrel photos at known distances; width = f·22/d) and would move the gate to its real row (~70 nominal). Slot a small "measure camera geometry" task into STATUS.md between steps 5 and 7. Tanush can shoot the calibration frames in the same session as the black-table data.

### N-003 (2026-10-14): add a "known confusers" section to constraints.md
The 10/7 findings only live in EXPERIMENTS.md, but they're constraints the algorithm must respect. Add a short section to `constraints.md` (log it in DECISIONS.md as a doc update, not a scope change):
- Wood under warm light falls inside naive orange thresholds (H≈15, S≈170).
- Skin (Lab a*≈29) and orange cardboard (a*≈33) sit near barrel orange (a*≈50).
- Barrel **reflections on glossy tables** create orange/blue smears *below* the barrel's ground contact. Likely worse on a glossy black table, so check the first black-table frames. (Geometry can reject them later: they're below the contact row.)
- The blue stripe darkens and desaturates under warm light (S 236→103, V≈60). It's the weakest class.
- A dark (black) table makes the table prior's color nearly black, so rejection-by-table-similarity mostly removes dark pixels. The background prior, saturation floor (N-004), and v1.5 do the rest.

### N-004 (2026-10-14): finalize v1 method details (approved by Tanush 10/14)
Tanush approved these v1 additions (from Dave's vision-pipeline slides; see Knowledge K-1). Update `PROBLEM.md` §Method / §In scope and log in `DECISIONS.md` (2026-10-14, "v1 method details, approved by Tanush"):
1. **Saturation floor:** a pixel can only be barrel if `max(R,G,B) − min(R,G,B) ≥ s_min`. This is thresholding, not image correction, so it's consistent with Dave's rule. Black table, gray wall, and white glare are all low-saturation. `s_min` is a config parameter fit on train/dev (it can also adapt per image from the table/background bands).
2. **Minimum-brightness gate:** a pixel can only be barrel if its brightness is above `v_min` (e.g. max channel or Y). Color is unreliable in very dark pixels (black table, shadows). Same idea as Tekkotsu's RGBK map, which gates color classes on minimum Y. Config parameter.
3. **RGB box** as already specified, plus **report how "full" the fitted box is** (fraction of box volume actually occupied by labeled barrel pixels, and the 3D scatter). This is the evidence for Dave's "is the cluster box-shaped or diagonal?" question.
4. **Data capture guidance** (add to `DATA.md`): shoot v1 black-table frames with **indirect/bounced light** (lamp pointed at the ceiling), not a lamp aimed straight at the barrels, to keep specular glare out of v1 (glare is out of scope). Overhead/direct-light frames are welcome but tag them as such (they'll be later stress tests).
Everything else from the slides is Knowledge, not v1.

## Knowledge

### K-1 (2026-10-14): Dave's "Vision Pipeline & Color Image Segmentation" slides (15-494, 2016)
Dave gave Tanush this deck. It's the CMVision/Tekkotsu lineage vex-aim-tools descends from, and it's where much of Dave's framing comes from:
- **Slide 9:** robots cope by color segmentation, discarding shading/texture, a **planar world assumption**, and **domain knowledge for occlusion**. That's our ground-plane geometry plan.
- **Saturation (slides 14–15):** `max(r,g,b) − min(r,g,b)`. Basis of the N-004 saturation floor.
- **YUV/YCbCr (slides 16–19):** Y = intensity, U = blueness, V = redness. RGB→YUV (8-bit): `Y = (65.738R + 129.057G + 25.064B)/256 + 16`, `U = (−37.945R − 74.494G + 112.439B)/256 + 128`, `V = (112.439R − 94.154G − 18.285B)/256 + 128`. Many cameras natively produce YUV. This is the "YUV" Dave mentioned on 10/7.
- **Classification by boxes (slide 21):** the origin of Dave's "box in RGB" idea. The slide's own example orange cluster is a **diagonal smear in RGB**; its stated drawback is "real regions aren't rectangular."
- **Lookup tables / CMVision (slides 22–23):** arbitrary-shaped class regions via a LUT. CMVision uses a reduced YUV LUT with **4 bits Y, 6 bits U, 6 bits V** (brightness matters least), stored as a `.tm` threshold map. Candidate "fancier function" for later: a LUT learned from labels.
- **EasyTrain / EasierTrain (slides 24–27):** tools that scatter image pixels in a color space (HSB/YUV/xy) and let you paint class regions → a threshold file. Inspiration for an "EasyTrain-lite" visualization (labeled pixels + fitted box) for showing Dave results.
- **RGBK threshold map (slide 28):** for robustness, a few broad classes with U/V thresholds **gated by minimum Y** (e.g. Blue: `Y≥32 & U≥136` or `Y≥64 & U≥144`; Black: `Y≤80` and not another class). Basis of the N-004 brightness gate.
- **Diagnosing (slide 29):** bad segmentation = lighting-spectrum shifts + **specular reflections turning shiny surfaces white**. Fixes: controlled lighting, **avoid overhead lights, use reflected light**. Check with a live **SegCam** view.
- **After segmentation (slides 30–31):** run-length encoding (also **removes noise by bridging short gaps**) → connected components. CC assumes **same-colored objects don't touch**, which is exactly our touching-barrels case (and why Dave's Lab 6 said not to rely on plain CC).
- **Slide 35:** image pyramids (half/quarter res) and Y-gradient channels for edges.

### K-2 (2026-10-14): navigator's quick color-space test on the 10/7 data (UNLABELED, directional only)
Probe-sampled barrel and distractor pixels from the 19 warm-wood-desk frames (9 lamp settings). Fit a 2–98th-percentile axis-aligned box to each barrel class, then counted distractor pixels inside it:
- **Orange:** a box excluded wood, skin, and orange cardboard in **every** space tried (RGB, YUV, HSV, Lab: 0–1% inside). But in RGB the orange cluster is a **diagonal smear** (like slide 21), so the box is mostly empty space where future distractors could fall. In the **YUV chroma plane (Y dropped) orange is a tight blob.**
- **Blue:** **not compact in any space.** It's a long curve from bright blue (body, cool light) to dull blue-gray (stripe, warm light). Its box swallowed a blue bottle cap (53% RGB, 69% HSV, 87–88% YUV/Lab). Blue likely needs per-image adaptation (v1.5) and/or non-color cues (shape, structure).
- **Caveats:** unlabeled, probe-based (bright faces only, no shadowed sides), boxes fit and tested on the same frames, one surface. **Re-do this properly on labeled black-table data** before drawing conclusions. Tanush is labeling soon and will dig into the slides himself.

### K-3 (2026-10-14): parked ideas (v1.5 and later, NOT v1)
- **v1.5:** a **YUV (or Lab) chroma-plane box** as a parallel arm to the RGB box. It drops brightness, which directly targets the diagonal problem. Plus the **barrel-referenced adaptive re-fit** (already in PROBLEM.md), especially for blue. Plus an **EasyTrain-lite** scatter tool (labeled pixels + fitted box, RGB and YUV views) for presenting to Dave.
- **Later:** a learned reduced-YUV **lookup table** (CMVision-style); **run-length gap bridging** as mask cleanup; **connected components only with geometry** to split touching barrels; a **live SegCam-style view** in vex-aim-tools (`imshow`) as a demo; Y-gradient **edges** to split touching barrels; a half-resolution pyramid for speed.

### K-4 (2026-10-14): context from navigator discussions
- **Lighting "ground truth":** Tanush pointed out that a stored table color can't serve as ground truth in a new setting (e.g. a lab with one overhead light). Hence the plan to use the **barrels themselves** as the reference in v1.5 (known object colors), not the table.
- **Docs philosophy:** foundation docs (PROBLEM/constraints/EVAL) act as the per-milestone spec (agreed with Dave, changed only via DECISIONS.md, re-versioned per milestone). Running docs are the lab notebook. Tanush wanted "an SSOT blueprint" like a spec, and this is the research-appropriate version.
- **Labels:** semi-automatic full masks (scribble → auto-grow → fix). Classes: 0 other, 1 orange (incl. orange stripes), 2 blue (incl. blue stripes), 255 ignore (glare/uncertain edges).
- **Data plan:** black table at home (CA, ordinary home light; the multi-warmth lamp is in Pittsburgh), then Pittsburgh tables. The table-agnostic goal is reached across these.
- **Dave comms:** one email per finished task. First email = `constraints.md` + `PROBLEM.md` + general update + directions (being drafted with the navigator now).
- **Lab 6:** the homework (part VI) was what Dave actually intended; Tanush did parts I–V. Skipped, since v1 covers its first half.

## Review notes

### 2026-10-14: docs review (PROBLEM, constraints, EVAL, STATUS, CLAUDE)
Overall: strong, accurate to the 10/7 meeting and the 10/14 decisions. Small fixes before sending to Dave:
- **constraints.md, barrel size:** says "Dave's measurement". The 25×22×6 numbers came from Dave's draft CLAUDE.md in his barrels.zip (and `worldmap.py`), not a confirmed measurement. Suggest: "from Dave's draft spec + worldmap.py; unverified."
- **PROBLEM.md, table band:** "a fixed strip of bottom rows". Say how many (e.g. bottom 80 rows ≈ ground 32–45 mm from the camera nominally); it's a v1 config parameter, so put the default here.
- **PROBLEM.md, success criteria:** fine to leave numeric targets for Dave, but propose a strawman in the email (e.g. per-class IoU ≥ 0.8 on black-table test frames, excluding ignore pixels).
- **EVAL.md / DATA.md:** state explicitly that **stripes are labeled as their own color** (orange stripe → orange, blue stripe → blue), matching PROBLEM.md.
- **EVAL.md:** add an image-level metric for **negative frames** (no barrels: % pixels flagged, target ≈ 0); P/R/IoU are uninformative when a class is absent.
- **STATUS.md housekeeping:** move `color_data/` into `barrels/data/raw/` before labeling to avoid path churn.

## Navigator context
- The repo's default branch was `master`, so the claude.ai Project only saw master. Fixed: the Project now syncs the `barrels` branch.

## Closed
*(none yet)*
