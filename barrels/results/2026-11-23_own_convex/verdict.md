# Verdict: does "an own end bulges outward, an end cut by a round barrel bulges inward" separate them? (2026-11-23)

Branch `wip/own-convex` (from `origin/barrels` e0d01e0). **Census only; no detector change; no PREREG** (the task's
stop rule: the census says the mask cannot tell them apart in the way the idea needs). Train frames only; no test
frame opened. Scripts: `experiments/2026-11-23_own_convex/` (`census_convex.py`, `census_summary.py`, `convex.py`,
`battery.py`, `real_frames.py`, `look_scenes.py`, `look_real.py`); tables: `census.md`, `diag/`, `pre/`.

## Outcome

1. **No.** On the class mask an end cut by a barrel in front does not bulge inward: its top and bottom stay flat
   (chord bulge median +0.000 / +0.001 H, hand / color model; 5th percentile -0.034 / -0.013), exactly like a straight
   cut (+0.000 / +0.001). Own ends bulge outward only weakly (median +0.026 / +0.020 H, 5th percentile -0.004 /
   -0.016). The sign does not separate them; no threshold has a margin.
2. **And the convexity test would have nothing to remove.** With today's defaults (`stripe_bridge`, `thin_frame` on),
   barrel-cut ends almost never "close in": closure median -0.026 / -0.004 H, and of 853 barrel-cut ends only 4 reach
   own_close's 0.15 on a full slice, none of which passes own_close's round-2 test (not against barrel color). Every
   one of the 1029 calls own_close makes (scorecard, real frames, 20-seed damage levels) that returns a box picks a
   true own end: 400 of 400.
3. **What own_close still gets wrong is something else.** Three scorecard scenes are lost (no box where no barrel is
   is added). In all three the piece is the stripe of the FRONT barrel of a same-colored pair; own_close finds its
   own end correctly (convex: chord +0.015 to +0.018 H, side +0.08 to +0.10 W), but its OTHER end "stands" only
   because the same-colored back barrel's body fills in above it; the box W wide from the own end then swallows the
   back barrel and its cap box is lost. Convexity at the own end cannot see that.

## The census (zone 0.15 W; `census.md` has 0.1 and 0.2 W and every measure)

Measure `chord` = mean of (top: chord - top row; bottom: bottom row - chord), the chord from the end column to the
column 0.15 W in, in barrel heights; + = outward (convex), - = inward (concave). `side` = the end column per row
against the chord from the top row to the bottom row, in W. Ends of every partly seen stripe piece (< 0.8 W seen) in
the scorecard scenes, labelled by the true boxes (target and pasted front barrels).

| end | masks | n | closure (median) | chord: median (5th to 95th) | side: median (5th to 95th) |
|---|---|---|---|---|---|
| own | hand | 609 | +0.176 | +0.026 (-0.004 to +0.052) | +0.076 (+0.000 to +0.094) |
| own | color model | 2050 | +0.162 | +0.020 (-0.016 to +0.064) | +0.068 (+0.000 to +0.104) |
| cut, straight edge | hand / model | 120 / 361 | +0.005 / +0.015 | +0.000 / +0.001 (-0.004 to +0.023) | +0.000 (+0.000 to +0.087) |
| cut, slanted edge | hand / model | 104 / 307 | +0.040 / +0.039 | +0.000 / -0.003 (-0.023 to +0.003) | +0.011 / +0.035 |
| cut, block | hand / model | 65 / 197 | -0.001 / +0.009 | +0.000 / +0.001 | +0.000 |
| **cut by a barrel in front** (all kinds) | hand | 152 | -0.026 | +0.000 (-0.034 to +0.033) | +0.000 (+0.000 to +0.062) |
| **cut by a barrel in front** | color model | 701 | -0.004 | +0.001 (-0.013 to +0.037) | +0.000 (+0.000 to +0.076) |

The ends own_close can call own (closure >= 0.15, full slice, not against barrel color): own 255 + 724 (+ 109 own
ends of pasted front barrels), slanted cut 3 (chord -0.014: these three would be removed by a convexity test), barrel
cut **0**. The 4 barrel-cut ends that close (before the round-2 test) have chord +0.013, +0.034, +0.034, +0.078:
convex, not concave.

Why no inward bulge: own_close reads each column's top and bottom row of the body color. Next to a cut by a barrel in
front, the back barrel's top and bottom both still stand at their predicted rows (the front barrel hides the middle
rows, and with the other color its body even reads as stripe), so the profile is flat, not dented. The dent the idea
predicts would be in the shape of the cut edge itself, which this reading never sees, and for a front barrel of the
same color the two bodies are one blob and there is no edge at all in the mask.

## own_close as it is, against today's defaults (`diag/`; for the record: is it now safe to switch on?)

| check | `start` | `close` (own_close on) |
|---|---|---|
| gate (`report.py --gate --cand-det own_close=true`) | FAIL only on the known `occlx_15` box | identical rows; +1 right barrel on BLACK `occl_03` (report only) |
| scorecard found / right place / boxes where no barrel is / too big | 2876 / 2992 / 48 / 91 | 3045 / 3170 / **48** / **92** |
| 75 % cells, found: straight edge / slanted / body block | 28 / 0 / 36 | 57 / 62 / 63 |
| cells lower | | same color beside 50 %: 88 -> 87 (3 scenes lost, above) |
| damage levels, 20 seeds, false boxes (perfect, typical, bad day, bad day w/o patch, light, medium, heavy) | 0, 0, 0, 0, 0, 4, 0 | 0, 0, 0, 0, 0, 4, 0 |
| every labeled train frame incl. the new sets (436 barrels) | 146 found, 18 false | 147 found, 18 false (the BLACK box) |

So with `stripe_bridge` on, A8's bad-day false box is gone (bad day 0 = 0); what remains against A8's rule is one
cell one scene lower (same color beside 50 %) and too big +1. That is a separate decision (Tanush's), not made here.

## The real occlusion set R1 (`4A8B_window_abpwhite_occlx_*`, 17 train frames; `pre/real_frames.md`, sheets looked at)

own_close changes no box on any of them. It is asked twice, both at a box edge (not a barrel), and declines both:
`occlx_02` (three quarters behind the box edge: own end closure 0.078 < 0.15) and `occlx_03` (a third showing: own
end 0.149, just under 0.15). No real frame has a barrel cut by a barrel in front where own_close is asked, so the
real check of the idea is empty. Frame by frame (today's defaults; `close` identical):

| shot | what | result |
|---|---|---|
| 01 | half behind a box edge | both found |
| 02 | three quarters behind the box edge | orange missed (thin piece; outline and own_close both unsure) |
| 03 | a third showing | orange missed (side unexplained; own_close 0.149 < 0.15) |
| 04 | slanted box edge | both found |
| 05 | gap between two boxes | both found |
| 06 | book in front, lower third | orange missed (not a full slice) |
| 07, 08 | book lower half / ruler upper half | both found |
| 09 | same color side by side | both found |
| 10 | same color, one nearer | back orange missed (one blob, covered by the front box) |
| 11 | other color straight in front | both found |
| 13 | next to a blue patterned box | both found |
| 14 | hand on a barrel at the frame edge | orange missed (not a full slice) |
| 15 | no barrels, striped clutter | 1 false orange box on the wrapper (pre-existing, `det1`, the other branch) |
| 17 | quarter inside the frame edge | both found; 1 false orange box above the far blue barrel (pre-existing) |
| 18 | pencil in front of the stripe | both found |
| 19 | blue block hiding three quarters of an orange barrel | orange missed (stripeless pieces) |
