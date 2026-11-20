# STATUS.md — where we are

**Updated:** 2026-11-20. The occlusion work is merged (Tanush: "understood"): side occlusion, hidden bottoms, cut from above or below, a post, same-colored pairs, a cut barrel placed by its own rounded corners. Home 28 of 29, campus 35 of 35, no false box; occlusion scorecard 2153 → 2737 of 3888 (simulated). Running: A8 (fill a cut stripe; a sliver with stripe and body gets a good box). Tanush has shot 36 ottoman frames (4 lamp settings) with vendor detections; boxing and slider labels pending. Plan: `TODO.md`.

## What runs

hs color model `eb863d84` (orange hue 3–13, S ≥ 140; blue hue 103–119, S ≥ 113; fit on the 16 home frames) → stripe detector, hardening a–g, with the reason log, `stripe_join` and `cap_behind` (2026-11-18); side-occlusion fix in the code but switched off → provisional camera `AIM_4A8B6118_BOXFIT`. Live: `BarrelViewer`, `BarrelTracker`, `tm seg` with a second window. Eval: `python barrels/tools/report.py`.

## Numbers (train frames, v2 rule)

| set | found | note |
|---|---|---|
| home (white, window) | 28 of 29 | the miss is the wedge barrel in `cluster_01` |
| campus (white) | 35 of 35 | |
| black table | 2 of 26 | parked as extreme (glare) |
| wood, bright lamp | 7 of 126 | parked as extreme |
| Dave's office | 11 of 34 (0.47) | indicative, his boxes group barrels |

No false box on any clean empty frame. Test frames (47) untouched.

## What we know (2026-11-16, `EXPERIMENTS.md`)

- Barrel colors move between settings: hue by about half a range, blue loses saturation under a warm lamp; the black table shifts them as much as a lamp does.
- One fixed color range for every table fails (wide paints the wood table and the home wall, tight misses the barrels).
- Thresholds read from each frame's labels reach about two thirds on black and cool-lit wood, almost nothing under mid and warm lamps: thresholds alone are not enough there; many misses are stripes that come out in pieces.
- Given perfect home masks the detector finds 28 of 29; with medium simulated damage 64 of 145. Left on the white tables: 1 hidden at the side (campus `occl_02`; A2) and 2 in home `cluster_01` (A3). Expected sizes are right; bottoms inferred from the top row are 4–7 px low for far barrels (A4).

## New data (data session, 2026-11-19; details in `DATA.md`, "Conditions shot this week")

- **2026-11-20: condition 5 in**, pale wood under weak overhead light on campus (9 frames with vendor files, split 7 / 2, not boxed). The table itself reads orange to the camera, and on a test frame our detector drew one false box on bare table: another case for the adaptive thresholds. **The close-up check passed** there (ours boxed near and far barrels on all three test frames; the vendor missed the near one on two); a barrel seated in the kicker is still unchecked.
- **2026-11-19: 4 conditions in.** The black ottoman lid at home under the lamp aimed down at it, at warm 6, mid 6, cool 6 and mid 3: 36 frames, every one with the vendor's saved answer, split by scene 28 train / 8 test. Not boxed yet, no slider labels yet (Tanush, after a later shoot).
- **The vendor save works** (the first real vendor files; `report.py --vendor` can run on them once the frames are boxed).
- **First look, no score:** with the lamp at mid 6 the barrels are plain to see and the vendor reports them, but our fixed color ranges miss them (orange reads hue 14 to 19 against our 3 to 13; blue sits on the lower edge of its range), and our detector drew no box on the three check frames. `lampmid3` is very dark (barrels around the brightness floor of 40) and the vendor still names barrels on it. This is the kind of case the adaptive thresholds (F) are for.
- **Open:** the kicker check; boxes for all 45 new frames; slider labels and slider labels for the ottoman frames; the 16-shot occlusion set (R1 in `DATA.md`); no white-table condition has a vendor file yet.

## Now

`TODO.md`: Claude on A2, A3, A4, H, I now; Tanush shoots and labels as tables come up; F as data arrives; G on Sunday.

## Tanush's part

Shoot and label (E) with the data session (`HANDOFF.md` has its prompt); live-check B and the close-up fix; read A's walkthrough when it is ready.

## Open questions

Can the camera's auto exposure / white balance be locked (not asked yet)? The vendor save works on the robot (checked 2026-11-19, `RUNBOOK.md`); its moving-barrel timing and stream-speed checks were not done.
