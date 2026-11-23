# NOTES-INBOX.md — untriaged notes

Decisions/ideas pasted in from phone/browser chats land here. Triage at the start of each session: move each item into the right doc (`DECISIONS.md`, `constraints.md`, `STATUS.md`, `EXPERIMENTS.md`, …) and delete it from here. Date every item.

Format:

```
## YYYY-MM-DD
- <pasted note> (source: phone chat / claude.ai / email with Dave / ...)
```

---

## 2026-11-21
- **Detector: a stripeless box from bad paint (for the main session; the data session did not change the detector).** Tanush saw it in `hs_slider.py` while trying wide orange thresholds on an ottoman frame (not saved): the lid's rim and its reflection painted orange, and one large orange box over a thin diagonal streak. Traced and reproduced on train frames (thresholds are orange hue low / high / S floor; blue at the adopted 103–119, S ≥ 113):
  - `4A8B_lampmid6_ottoman_occl_02`, orange −30 / 20 / 40: box (154, 244, 315, 480), flags `bottom_inferred`, `truncated`; the painted pixels in it end at row **455**, they fill **12 %** of the box.
  - `4A8B_lampwarm6_ottoman_core_01`, orange −30 / 20 / 0: box (165, 240, 283, 480), same flags; speckle down to row 479, fill **18 %**.
  - The path: the stripeless pieces loop in `detector.py` (≈ line 1121), `if p.bbox[3] >= h or hs < cfg.min_stripe_px: out.append(p)`, the close-barrel exception ("its stripe may be below the frame"). Two gaps: (1) it tests the **box** bottom, which can be the bottom the detector inferred from the top row and clipped at 480, not where the painted pixels end (case 1); (2) a stripeless piece is checked only by its outline (0.4–1.6 × width, height band), never by how full it is: a streak or a speckle cloud has a barrel-sized outline at 10–20 % fill, a real close barrel fills most of its box. The stripe path has the body-color check (hardening c); this path has none.
  - Plausible fix, to be judged on the eval (no real barrel lost): require the painted pixels themselves to reach the frame bottom, and a minimum fill of barrel color for a stripeless box (e.g. ≥ 0.5). With the adopted thresholds no such box has been seen on home, campus or any negative; it appears when the paint is bad, which is what adaptive thresholds (F) and poor light will produce. Tanush's exact frame and numbers were not recorded.
- **`tests/test_labels_consistency.py` fails on `4A8B_window_abpwhite_occlx_15`** (a no-barrel shot of the occlusion set R1 by design; `occlx_16` will be the same): the test expects boxes on every frame whose scene is not `neg`. The label is right; the test needs the R1 no-barrel shots (15, 16) as an exception. 736 pass, this 1 fails.
- **`box_tool.py` fixed (data session, Tanush's go):** the right and bottom frame edges (x 640, y 480) were unreachable with the mouse, so a barrel cut there never got `truncated`; an edge within 2 px now snaps onto the frame edge. Nine short edges in the new labels were snapped (`DATA.md`). Same cause as the 29 edges snapped on 2026-11-16.
- **`hs_slider.py` (data session):** a click that misses every slider now says where it landed (diagnostic; the sliders were working). Tanush finds the sliders hard on frames with orange or blue clutter (data session discussing with him).
- **A heavy-overlap frame where ours beat the vendor**, kept locally, not imported: `live/snapshots/check_2026-11-21_abpwhite/robot_snap0.png` (two blue barrels in front of two orange ones, white table at ABP, window light): ours four boxes, the vendor five (a duplicate orange box, score 80). Tanush: a case to keep in the back pocket.
