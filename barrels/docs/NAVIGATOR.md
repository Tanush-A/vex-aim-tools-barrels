# NAVIGATOR.md: notes from the navigator session

**Ownership: written ONLY by the navigator** (Tanush's planning/Q&A session in the claude.ai Project "Celeste Barrel Detection"). **Claude Code reads this file but never edits it.** It's a one-way channel from the navigator to Claude Code, so Tanush doesn't have to relay things by hand.

How Claude Code uses this file:
- **Read it at the start of every session**, right after `STATUS.md`.
- **Requests** = action items. Act on open ones if they fit the current task (or queue them in `STATUS.md`). When one is done, note it in `STATUS.md` with its ID (e.g. "N-001 done"). The navigator moves it to Closed.
- **Knowledge** = background from navigator ↔ Tanush discussions: things to know, ideas parked for later, context behind decisions. Not action items. Use it when designing experiments or planning later milestones. **Don't implement anything from Knowledge unless a Request or Tanush says to.**
- **Review notes** = suggestions to weigh. Tanush decides. Foundation-doc changes still go through `DECISIONS.md`.
- To reply to the navigator, write in `STATUS.md` or `NOTES-INBOX.md`, never here.

Precedence: Tanush's direct instructions > foundation docs (`PROBLEM.md`, `constraints.md`, `EVAL.md`) > this file.

_Last updated: 2026-10-14 (night)._

---

## Requests (open)
*(none right now)*

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
- **Dave comms:** one email per finished task. **First email sent 2026-10-14** (see K-5).
- **Lab 6:** the homework (part VI) was what Dave actually intended; Tanush did parts I–V. Skipped, since v1 covers its first half.

### K-5 (2026-10-14): first email to Dave, SENT
Subject: "Barrel detector: spec docs for review before I start coding". Contents:
- Links to the fork (branch `barrels`), `PROBLEM.md`, and `constraints.md`, asking him to read them.
- A v1 summary: per-pixel color segmentation, adaptive thresholds from table rows + above-horizon rows, saturation floor + minimum-brightness gate (from his slides/RGBK map), a report on how well an RGB box fits (box-vs-diagonal), and the repo built around a fixed labeled set + eval harness so Claude can propose/score variants. Deferred to v2+: bounding boxes, glare/shadow, close-range top-only, other color spaces.
- **Question asked:** should horizon gating be in v1 (conservative near the top until tilt/f are measured), or keep v1 purely color? **→ Until Dave answers, keep horizon gating in v1 as written (conservative), but implement it as a config flag so it can be switched off.**
- **Note given:** camera.py f = 400 vs. the 70°×50° FOV (implies f ≈ 457 horizontal / 515 vertical). Tanush will calibrate AIM-4A8B6118 and send numbers.
- **Promised next steps:** labeling tool → 20–30 black-table frames + tilt/focal-length measurements this week (CA) → eval harness → first RGB-box experiment. A short note to Dave after each significant step.
- Questions deliberately NOT asked (Tanush will resolve them himself): verifying barrel dimensions (ruler), success targets (strawman IoU ≥ 0.8 stays internal), the Lab 6 top-only assumption, the missing detect.py / bounding_boxes*.png.
- When Dave replies: Tanush pastes it to the navigator (or into NOTES-INBOX.md), and decisions get logged in DECISIONS.md.

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
- **N-001** (register NAVIGATOR.md in CLAUDE.md): done 2026-10-14 (commit 2a29846).
- **N-002** (measure tilt + focal length before v1 experiment): queued as STATUS.md step 6, 2026-10-14 (commit 8adc749).
- **N-003** (known confusers in constraints.md): done 2026-10-14 (commits 8adc749, 7749859).
- **N-004** (v1 method details: saturation floor, brightness gate, box-fullness report, bounced-light capture): done 2026-10-14 (commit 2a29846; DECISIONS.md entry).
- **Review notes 2026-10-14:** applied 2026-10-14 (commit 8adc749).
