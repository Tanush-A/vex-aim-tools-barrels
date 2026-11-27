# PREREG — a barrel hidden at the side by a thing that is not a barrel: the photo at the cut (2026-11-27)

Branch `wip/exp-occl-photo` (from `barrels` at `a27304f`). Written and committed before any judged run.

## Deviation from the brief, stated first

The brief said: branch from `barrels`, then `git merge wip/exp-contrast`. Since that brief was written, `barrels` itself
adopted the stripe by contrast (`125aed7`, "Merge wip/adopt-contrast"): `pipeline.detect_frame` = color step, detector,
`contrast.add_boxes`, and the adoption proof says it draws the judged contrast candidate's boxes on all 231 train frames.
`wip/exp-contrast` is the pre-collapse branch (its `detector.py` differs by 2746 lines). Merging it would only re-import
the old copy. So it was NOT merged: the baseline "contrast as the color step" is today's default (`judge.fixed_detector()`),
and the candidate is the same path with the photo handed to `detect` (`lib.run_frame`). `test_contrast.py` needs no port
(it is already in `barrels`).

Also: the proof harness's stored `before.json` predates the seam reading (adopted 2026-11-27): today's unmodified code
differs from it on 54 inputs, exactly the seam reading's 54. The proof is therefore made against a fresh run of today's
code (`golden/occlphoto/base.json`, 5435 inputs, 6207 boxes, sha256 `4211c205a6a6d456`).

## Question

A partly seen stripe that no reason places (frame edge, nearer found barrel, body and stripe ending apart) and the outline
cannot place gets a centred guess or no box. Can the PHOTO say which end of the seen part is cut by a thing standing in
front, so that the box is drawn W wide from the other end, without a single new box that is not on its barrel?

## The rule (behind `DetConfig.side_photo`, default "off"; `detect(..., photo=None)`, default today)

`cut_by_photo` / `cut_line_in_band` in `detector.py`. For each end of the seen part, in a band of rows 0.1 H to 0.5 H
above the barrel's top and the same below its bottom: per row, the strongest horizontal step of the photo
(|I(x+2) − I(x−2)|, R+G+B, smoothed 3×3) within 0.3 W of the seen end; rows with a step ≥ 60 get a straight line fitted
(trimmed at 1.5 px). The end is CUT when in the band above OR below:
1. at least `photo_frac` of the band's rows lie on the line, leaning at most 0.5 px per row;
2. barrel color lies beyond the line (more than 2 px + `photo_slack` × rows from the band's edge) in at most `photo_cross`
   of the barrel's rows from that band's side to the stripe's middle row (a thing in front hides everything past its edge;
   an edge behind the barrel is crossed by its bulge);
3. the line meets the seen part (median gap to the barrel's outermost pixel ≤ max(3 px, 0.15 W)).
Exactly one end cut → box W wide from the other end (rule `photo_cut`, thin pieces `thin_photo_cut`). It is asked after
the outline and before the centred guess, and in the thin branch after `thin_outline`; like the outline it never takes a
found box's place. `cut+bulge` additionally needs the sidecut bulge to agree (the other end bulges, the cut end does not).

Idea 2 (the photo just beside the seen end against the photo one W further out) was measured
(`measure.py`, `beside_diff`) and does not separate hidden from free ends: no arm.

## Candidates judged (all of them reported)

| name | fields |
|---|---|
| `cut` | side_photo=cut, photo_frac 0.6, photo_cross 0.1, photo_slack 0 |
| `cut+bulge` | side_photo=cut+bulge, same numbers |
| `slack` | side_photo=cut, photo_slack 0.1 |
| `loose` | side_photo=cut, photo_slack 0.1, photo_frac 0.5, photo_cross 0.2 |
| `fit` (leave one place out) | per fold, one of the four above, chosen on the OTHER places only: the arm with the most barrels found (strict) on the training frames among arms that add no box that is not on its barrel there; ties → the stricter arm, in the order cut+bulge, cut, slack, loose; no arm finds more → today |

How the numbers were chosen: 60, 1.5 px, 0.5 px/row, 0.1–0.5 H, 0.3 W, 2 px, max(3 px, 0.15 W) were set from the size of a
barrel and of a step between two things, before looking at numbers; `photo_frac`, `photo_cross` and `photo_slack` were
set in development (below). Only the `fit` row has numbers chosen inside each fold; the four fixed arms are judged
in-sample and are NOT a held-out test.

## Yardsticks and success line

- Proof harness at defaults: IDENTICAL BOXES ON EVERY INPUT (against today's code). Full test suite passes.
- Standard judge (`judge.judge`, baseline today's default with contrast): must not FAIL; boxes not on their barrel must not
  rise. Success = PASS of the `fit` row. Expected honestly: NO CLEAR DIFFERENCE (the targets are a handful of placements).
- Real train frames barrel by barrel (`real.py`), contact sheets of every changed frame; traps `lampwarm6_glass_occl_02`
  (tin label) and every `*_neg_02` frame: no new box.
- Simulated side cuts (`sim.py`): the sidecut scenes (straight and slanted edge, 0.5 / 0.6 / 0.65 / 0.75 hidden), with a
  synthetic photo (the source frame's photo with the occluder painted flat over its region, taller than the barrel and
  standing nearer); strict and "centre within 10 %". This tests only the geometry of the rule, not real photos.
- Hard limit: any new box on nothing, any new box on an empty frame → not recommended, whatever else.

## What I looked at before this file (honest list)

- The six frames of the brief (`occlx_02`, `occlx_03`, `palewood_occl_02`, `lampcool6/lampmid6_ottoman_occl_02`,
  `lampwarm6_glass_occl_02`), as pictures.
- `measure.py`: the cue numbers on every partly seen stripe of all 261 labelled train frames, against the labels.
- `real.py --out dev` / `dev2`: the arms `cut`, `cut+bulge`, `slack`, `loose` on all 261 labelled train frames, with
  the contact sheets of the 6 changed frames. Result there: `cut` +2 barrels, `slack` +3, `loose` +4 (one moved), no new
  box off its barrel in any arm. The cross band (half the barrel) and `photo_slack` were added after seeing `occlx_03`'s
  slightly curved box edge. So the in-sample real-frame numbers are development numbers.
