#!/usr/bin/env python3
"""TODO A4 (2026-11-19): calibrate the camera from the ruler set.

Hypothesis. The camera in use (``geometry.AIM_4A8B6118_BOXFIT``: f 400, tilt 22.25, camera height 43.47 mm)
was fit to hand-drawn boxes without known distances, and the size check of 2026-11-18 found that it puts the
bottom edge inferred from a barrel's top row 4 to 7 px too low for far barrels. The 12 ruler frames (one
orange barrel on the crosshair, the near edge of its base 0 to 300 mm from the robot's front edge,
``data/calib.csv``) have known distances, so they can say which camera numbers are wrong.

Method. ``barrels.camfit``: for each frame the known distance predicts the box's top row, bottom row and width;
the hand-drawn box is the measurement; weighted least squares (box edge 1.5 px, placement 1 mm). Parameter sets
are tried from small to large; the one kept is the smallest whose residuals are as small as the error model
says (weighted rms <= 1). Then: residuals per frame for the old camera and the new one, one fit per frame left
out, 200 refits with the boxes and placements disturbed, other error models, subsets of the data, and the tape
measure lying in the frames as a check that needs no box (``tape.py``).

Data. ``4A8B_lampmid6_wood_calib_01`` to ``_12``: geometry-only frames, in no split. No train or test frame is
opened here. The validation on the train frames is ``validate.py`` (rule in PREREG.md, committed before it ran).

    python barrels/experiments/2026-11-19_calibration/run.py

Outputs: results/2026-11-19_calibration/ fit.md, fit.json, residuals.csv.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))
from barrels import camfit as cf, cv as bcv, geometry as geo, io  # noqa: E402
import tape as tp  # noqa: E402

OUT = io.PKG_ROOT / "results" / "2026-11-19_calibration"
OLD = geo.AIM_4A8B6118_BOXFIT
SIGMA_PX, SIGMA_D_MM = 1.5, 1.0
# parameter sets, small to large. The camera's own numbers are f, tilt and height; off_mm only says where the
# ruler's zero (the robot's front edge) is relative to the camera.
LADDER = (("tilt_deg",), ("tilt_deg", "off_mm"), ("f", "tilt_deg", "off_mm"), ("tilt_deg", "off_mm", "height_mm"),
          ("f", "tilt_deg", "off_mm", "height_mm"))
# for the record only: other single numbers that could absorb the same misfit
ALTERNATIVES = (("tilt_deg", "off_mm", "barrel_h_mm"), ("f", "tilt_deg", "off_mm", "barrel_h_mm"), ("tilt_deg", "off_mm", "cy"))
ROUND = {"f": 1.0, "tilt_deg": 0.05, "height_mm": 0.1, "off_mm": 0.5}
NAMES = {"f": "f", "tilt_deg": "tilt", "off_mm": "offset", "height_mm": "camera height", "cy": "centre row", "barrel_h_mm": "barrel height"}


def short(stem: str) -> str:
    return stem.split("_")[-1]


def describe(fr: cf.Fit) -> str:
    p = fr.params
    return (f"f {p['f']:.1f}, tilt {p['tilt_deg']:.2f}, camera height {p['height_mm']:.2f}, offset {p['off_mm']:.2f}"
            + (f", barrel height {p['barrel_h_mm']:.2f}" if abs(p["barrel_h_mm"] - geo.BARREL_HEIGHT_MM) > 1e-9 else "")
            + (f", centre row {p['cy']:.1f}" if abs(p["cy"] - 240) > 1e-9 else ""))


def fit_row(name: str, fr: cf.Fit) -> str:
    se = ", ".join(f"{NAMES[k]} ± {v:.2f}" for k, v in fr.stderr.items()) or "-"
    return (f"| {name} | {describe(fr)} | {fr.camera.horizon_row():.1f} | {fr.rms_px:.1f} | {fr.rms_weighted:.2f} | {se} |")


def rounded(p: dict) -> dict:
    return {k: (round(v / ROUND[k]) * ROUND[k] if k in ROUND else v) for k, v in p.items()}


def horizon_from_known_distances(obs: list, kind: str, weights_at: dict, horizons=np.arange(60.0, 110.01, 0.5)) -> dict:
    """Without any camera model: the row of a point at fixed height is ``horizon + A / (distance + B)``. For each
    trial horizon the best A and B are found (B on a grid, A in closed form) and the weighted rms misfit kept.
    Returns the best horizon, its misfit, the horizons whose misfit is within twice the best (at least 0.5 px),
    and the misfit at a few rows."""
    sel = [o for o in obs if o.kind == kind]
    d = np.array([o.d_ruler_mm for o in sel]); r = np.array([o.value for o in sel])
    w = np.array([1.0 / cf.sigma(weights_at, o, SIGMA_PX, SIGMA_D_MM) ** 2 for o in sel])
    scan = []
    for hz in horizons:
        best = np.inf
        for B in np.arange(0.0, 60.01, 0.25):
            x = 1.0 / (d + B)
            A = np.sum(w * x * (r - hz)) / np.sum(w * x * x)
            best = min(best, float(np.sqrt(np.sum(w * (r - hz - A * x) ** 2) / np.sum(w))))
        scan.append((float(hz), best))
    b = min(scan, key=lambda t: t[1])
    ok = [hz for hz, c in scan if c <= max(2 * b[1], 0.5)]
    return {"n": len(sel), "best": b, "range": (min(ok), max(ok)), "at": {hz: c for hz, c in scan if hz in (76.5, 84.0, 91.0)}}


def by_shot(fr: cf.Fit) -> dict:
    out: dict = {}
    for o, r in zip(fr.obs, fr.res_px):
        out.setdefault(o.stem, {})[o.kind] = float(r)
    return out


def main() -> int:
    out = OUT
    out.mkdir(parents=True, exist_ok=True)
    shots = cf.load_ruler_set()
    obs = cf.observations(shots)
    start = cf.params_of(OLD)
    kw = dict(sigma_px=SIGMA_PX, sigma_d_mm=SIGMA_D_MM)

    old = cf.fit(obs, start, free=(), **kw)
    old_off = cf.fit(obs, start, free=("off_mm",), **kw)
    ladder = {free: cf.fit(obs, start, free=free, **kw) for free in LADDER}
    alts = {free: cf.fit(obs, start, free=free, **kw) for free in ALTERNATIVES}
    chosen_free = next((free for free in LADDER if ladder[free].rms_weighted <= 1.0), LADDER[-1])
    best = ladder[chosen_free]
    cand_p = rounded(best.params)
    cand = cf.fit(obs, cand_p, free=(), **kw)
    cam_new = cand.camera

    L = ["# Camera calibration from the ruler set (TODO A4)", "",
         f"git {bcv.git_hash()}. Data: the 12 ruler frames `4A8B_lampmid6_wood_calib_01` to `_12` with their hand-drawn boxes and "
         "`data/calib.csv`. They are in no split. No train or test frame is opened by this script.", "",
         "## What is known, what is fit", "",
         "| number | value | where it comes from | fit? |", "|---|---|---|---|",
         "| image size, centre | 640 × 480, centre (320, 240) | assumed (never measured) | no |",
         "| barrel | 24 mm tall, 18 mm at lid and base, 25.5 mm at the bulge | tape measure, 2026-10-19 | no |",
         "| focal length f | 400 px | `aim_fsm/camera.py`, an estimate | tried; the data cannot tell it from 400 |",
         "| tilt | 22.25° (old), fit to boxes 2026-11-03 | no specification for this robot | **yes** |",
         "| camera height | 43.47 mm | `aim_fsm/aim_kin.py` | **yes** (the ruler frames do not fit without it) |",
         "| offset: camera behind the ruler's zero | 3 mm (camera 27 mm ahead of the centre, front edge at 30) | `aim_kin.py`, \"approx\" | **yes**, but it is not a camera number |",
         "",
         f"What a box gives: top row always (11 frames), bottom row when it is inside the frame (6 frames: 30 mm and further), "
         f"width when both sides are inside the frame (11). {len(obs)} numbers in all. Frame 01 (0 mm) is left out: the barrel sits in the kicker, "
         "off the table, and its distance from the front edge is not the ruler's.",
         f"Error model: a box edge is drawn to {SIGMA_PX} px; the barrel was placed to {SIGMA_D_MM:.0f} mm. Close to the robot one millimetre is many pixels "
         "(top row: 5 px per mm at 10 mm; bottom row: 7 px per mm at 30 mm), so close frames count for little.",
         "`weighted` = rms of residual / expected error: about 1 when the model fits as well as the error model allows.", "",
         "## Which parameters are needed", "",
         "| fitted | result | horizon row | rms px | weighted | 1-sigma from the fit |", "|---|---|---|---|---|---|",
         fit_row("nothing (old camera, offset 3)", old), fit_row("offset only (old camera)", old_off)]
    for free in LADDER:
        L.append(fit_row(" + ".join(NAMES[k] for k in free) + (" **(kept)**" if free == chosen_free else ""), ladder[free]))
    for free in ALTERNATIVES:
        L.append(fit_row("for the record: " + " + ".join(NAMES[k] for k in free), alts[free]))
    L += ["",
          f"Kept: **{' + '.join(NAMES[k] for k in chosen_free)}**, the smallest set whose weighted rms is at most 1. "
          "With the camera height held at 43.47 mm no tilt, focal length and offset fit the frames: tops and bottoms miss in opposite directions. "
          "Letting the focal length go as well changes nothing (it comes back as 400 within its error).",
          "A taller barrel or a moved centre row instead of a lower camera fit worse, and the centre row lands at an impossible value.",
          f"Rounded candidate: **f {cand_p['f']:.0f}, tilt {cand_p['tilt_deg']:.2f}°, camera height {cand_p['height_mm']:.1f} mm** "
          f"(horizon row {cam_new.horizon_row():.1f}; old: {OLD.horizon_row():.1f}), offset {cand_p['off_mm']:.1f} mm. "
          f"Rounded, its rms is {cand.rms_px:.1f} px, weighted {cand.rms_weighted:.2f}.", "",
          "## Residuals per frame: hand-drawn box minus model, px", "",
          "`old` = old camera with the offset of 3 mm from `aim_kin.py`. `old, best offset` = old camera, offset fitted "
          f"({old_off.params['off_mm']:.1f} mm), so that the old camera is not blamed for the offset. `new` = the rounded candidate.", "",
          "| frame | mm | top: old | old, best offset | new | bottom: old | old, best offset | new | width: old | old, best offset | new |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    tabs = [by_shot(old), by_shot(old_off), by_shot(cand)]

    def cell(t, stem, kind):
        return f"{t[stem][kind]:+.1f}" if kind in t.get(stem, {}) else "-"

    for s in shots:
        if s.stem not in tabs[0]:
            L.append(f"| {short(s.stem)} | {s.d_ruler_mm:.0f} | left out (in the kicker) | | | | | | | | |")
            continue
        L.append(f"| {short(s.stem)} | {s.d_ruler_mm:.0f} | " + " | ".join(cell(t, s.stem, kind) for kind in cf.KINDS for t in tabs) + " |")

    def rms_of(t, kind, far=None):
        v = [t[s.stem][kind] for s in shots if kind in t.get(s.stem, {}) and (far is None or (s.d_ruler_mm >= 100) == far)]
        return f"{np.sqrt(np.mean(np.square(v))):.1f}" if v else "-"

    L.append("| **rms** | all | " + " | ".join(rms_of(t, kind) for kind in cf.KINDS for t in tabs) + " |")
    L.append("| **rms** | 100 mm and further | " + " | ".join(rms_of(t, kind, True) for kind in cf.KINDS for t in tabs) + " |")
    L.append("| **rms** | nearer than 100 mm | " + " | ".join(rms_of(t, kind, False) for kind in cf.KINDS for t in tabs) + " |")
    with (out / "residuals.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["stem", "distance_mm", "kind", "measured", "old", "old_best_offset", "new", "expected_error_px"])
        for o, a, b, c, sg in zip(obs, old.res_px, old_off.res_px, cand.res_px, cand.sig_px):
            w.writerow([o.stem, o.d_ruler_mm, o.kind, o.value, round(float(a), 2), round(float(b), 2), round(float(c), 2), round(float(sg), 2)])

    # ---------------------------------------------------------------- how well each number is pinned
    loo = cf.leave_one_out(obs, start, chosen_free, **kw)
    J = cf.jitter(obs, start, chosen_free, n=200, seed=0, box_px=SIGMA_PX, place_mm=SIGMA_D_MM, **kw)
    loo4 = cf.leave_one_out(obs, start, LADDER[-1], **kw)
    J4 = cf.jitter(obs, start, LADDER[-1], n=200, seed=0, box_px=SIGMA_PX, place_mm=SIGMA_D_MM, **kw)
    L += ["", "## How well each number is pinned", "",
          "| number | fit | 1-sigma from the fit | range over 11 fits, one frame left out each | spread of 200 refits, boxes ± 1.5 px and placement ± 1 mm |",
          "|---|---|---|---|---|"]
    for j, k in enumerate(chosen_free):
        v = [fr.params[k] for fr in loo.values()]
        L.append(f"| {NAMES[k]} | {best.params[k]:.2f} | {best.stderr[k]:.2f} | {min(v):.2f} to {max(v):.2f} | ± {J[:, j].std():.2f} |")
    hz = [fr.camera.horizon_row() for fr in loo.values()]
    hzj = [cf.camera_of({**best.params, **dict(zip(chosen_free, row))}).horizon_row() for row in J]
    L.append(f"| horizon row | {best.camera.horizon_row():.1f} | - | {min(hz):.1f} to {max(hz):.1f} | ± {np.std(hzj):.1f} |")
    L += ["", "The same with the focal length free as well (four numbers):", "",
          "| number | fit | 1-sigma from the fit | range, one frame left out | spread of 200 refits |", "|---|---|---|---|---|"]
    for j, k in enumerate(LADDER[-1]):
        v = [fr.params[k] for fr in loo4.values()]
        L.append(f"| {NAMES[k]} | {ladder[LADDER[-1]].params[k]:.2f} | {ladder[LADDER[-1]].stderr[k]:.2f} | {min(v):.2f} to {max(v):.2f} | ± {J4[:, j].std():.2f} |")
    names4 = [NAMES[k] for k in LADDER[-1]]
    c4 = ladder[LADDER[-1]].corr
    L += ["", "Correlations in the four-number fit: " + ", ".join(f"{names4[i]} / {names4[j]} {c4[i, j]:+.2f}" for i in range(4) for j in range(i + 1, 4)) + ". "
          "Focal length, tilt and offset trade against each other; holding f at 400 removes that."]

    # ---------------------------------------------------------------- other choices
    L += ["", "## Does the answer depend on the choices made here", "", "| change | tilt | camera height | offset | horizon row | weighted |", "|---|---|---|---|---|---|"]

    def line(name, fr):
        p = fr.params
        return f"| {name} | {p['tilt_deg']:.2f} | {p['height_mm']:.2f} | {p['off_mm']:.2f} | {fr.camera.horizon_row():.1f} | {fr.rms_weighted:.2f} |"

    L.append(line("as above", best))
    variants = {}
    for name, sp, sd in (("box edge 1 px, placement 0.5 mm", 1.0, 0.5), ("box edge 2 px, placement 2 mm", 2.0, 2.0), ("no placement error (every px counts the same)", 1.5, 0.0)):
        variants[name] = cf.fit(obs, start, chosen_free, sigma_px=sp, sigma_d_mm=sd)
    for name, sel in (("rows only (no widths)", [o for o in obs if o.kind != "width"]),
                      ("tops and widths only (no bottom rows)", [o for o in obs if o.kind != "bottom"]),
                      ("30 mm and further (6 frames)", [o for o in obs if o.d_ruler_mm >= 30]),
                      ("100 mm and further (4 frames)", [o for o in obs if o.d_ruler_mm >= 100]),
                      ("nearer than 100 mm (7 frames)", [o for o in obs if o.d_ruler_mm < 100])):
        variants[name] = cf.fit(sel, start, chosen_free, **kw)
    for name, fr in variants.items():
        L.append(line(name, fr))
    with_held = cf.fit(cf.observations(shots, skip_flags=()), start, chosen_free, **kw)
    L.append(line("frame 01 (in the kicker) included", with_held))

    # ---------------------------------------------------------------- checks that need no distance
    L += ["", "## Checks inside the image (no distance used): the 6 frames whose box is whole", "",
          "What the detector does with a box: infer the bottom row from the top row, or from the width; and what the box tool's `g` draws: "
          "the expected width and height for a barrel whose bottom edge is at that row. px = inferred minus drawn (+ = inferred lower).", "",
          "| frame | mm | bottom from top: old | new | bottom from width: old | new | width / expected: old | new | height / expected: old | new | width / exact outline, new |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in shots:
        x0, y0, x1, y1 = s.bbox
        if y1 >= io.FRAME_H or "held" in s.flags:
            continue
        cells = []
        for fn in (lambda c: c.bottom_row_from_top_row(y0) - y1, lambda c: c.bottom_row_from_width(x1 - x0) - y1):
            cells += [f"{fn(OLD):+.1f}", f"{fn(cam_new):+.1f}"]
        for fn in (lambda c: (x1 - x0) / c.expected_barrel_width_px(bottom_row=y1), lambda c: (y1 - y0) / c.expected_barrel_height_px(bottom_row=y1)):
            cells += [f"{fn(OLD):.2f}", f"{fn(cam_new):.2f}"]
        cells.append(f"{(x1 - x0) / cam_new.silhouette_width_px(cam_new.d_axis_from_bottom_row(y1)):.2f}")
        L.append(f"| {short(s.stem)} | {s.d_ruler_mm:.0f} | " + " | ".join(cells) + " |")
    L += ["", "The width the code expects is `f × 25.5 / distance`, with the horizontal distance. The pinhole divides by the depth along the tilted "
          "optical axis. The two agree near 16 cm; the shortcut is too narrow further out and too wide close up (new camera):", "",
          "| barrel axis at | " + " | ".join(f"{d} mm" for d in (40, 60, 100, 150, 200, 300, 400)) + " |", "|---|" + "---|" * 7,
          "| shortcut, px | " + " | ".join(f"{cam_new.expected_barrel_width_px(d):.0f}" for d in (40, 60, 100, 150, 200, 300, 400)) + " |",
          "| exact outline, px | " + " | ".join(f"{cam_new.silhouette_width_px(d):.0f}" for d in (40, 60, 100, 150, 200, 300, 400)) + " |",
          "| shortcut / exact | " + " | ".join(f"{cam_new.expected_barrel_width_px(d) / cam_new.silhouette_width_px(d):.2f}" for d in (40, 60, 100, 150, 200, 300, 400)) + " |"]

    # ---------------------------------------------------------------- the tape in the frames
    stem0 = shots[0].stem[:-2]
    t = tp.analyse(lambda k: io.find_image(f"{stem0}{k:02d}"), {"old": OLD, "new": cam_new})
    free_hz = {kind: horizon_from_known_distances(obs, kind, cand_p) for kind in ("top", "bottom")}
    L += ["", "## The horizon row without a camera model", "",
          "The row of a point at a fixed height is `horizon + A / (distance + B)`, whatever the focal length, tilt and camera height are. "
          "Fitting that curve (three free numbers) separately to the box tops, the box bottoms and the tape's centimetre lines gives three "
          "independent readings of the horizon row. Misfit in px (weighted rms for the boxes).", "",
          "| from | points | distance range | best horizon row | misfit there | rows within twice that misfit | misfit at 76.5 (old) | at 84 | at 91 (new) |", "|---|---|---|---|---|---|---|---|---|"]
    for kind, rng in (("top", "10 to 300 mm"), ("bottom", "30 to 300 mm")):
        v = free_hz[kind]
        L.append(f"| box {kind}s, known distances | {v['n']} | {rng} | {v['best'][0]:.1f} | {v['best'][1]:.2f} | {v['range'][0]:.1f} to {v['range'][1]:.1f} | "
                 f"{v['at'][76.5]:.2f} | {v['at'][84.0]:.2f} | {v['at'][91.0]:.2f} |")
    v = t["horizon_scan"][0.0]
    L.append(f"| tape centimetre lines (next section) | {len(t['lines'])} | about 40 to 110 mm | {v['best'][0]:.1f} | {v['best'][1]:.2f} | {v['range'][0]:.1f} to {v['range'][1]:.1f} | "
             f"{v['at'][76.5]:.2f} | {v['at'][84.0]:.2f} | {v['at'][91.0]:.2f} |")
    L += ["", "The tops and the bottoms each put the horizon near row 90 to 92 and rule out 76. The tape's lines, which only reach 11 cm, prefer a row near 80 and "
          "fit 91 less well (about 1 px). The two do not agree; see the reading under the tape section."]
    L += ["", "## The tape measure in the frames (a check that needs no box)", "",
          "The tape lies on the table in every frame. Frames 09 to 12 are used (the barrel is far and does not cover it; the tape did not move).", "",
          "**1. Where its two edges meet.** Parallel lines on the table meet on the horizon row.", "",
          "| rows used | meeting row in frames 09, 10, 11, 12 | left edge rms px | right edge rms px |", "|---|---|---|---|"]
    for name, v in t["vanishing"].items():
        L.append(f"| {name} | {', '.join(f'{r:.1f}' for r in v['rows'])} | {v['left_rms']:.2f} | {v['right_rms']:.2f} |")
    L += ["", "The answer moves by about 10 rows with the rows used: the right edge is not straight (it carries the tick marks and bends by about 2 px). "
          f"So the tape's edges say the horizon is somewhere between rows 82 and 96. Old camera: {OLD.horizon_row():.1f}. New: {cam_new.horizon_row():.1f}.", "",
          "**2. The centimetre lines.** Rows of the lines 142 cm down to 135 cm, read in the tape's left margin. A right camera reads 10 mm between neighbours.", "",
          "| line | row | column | contrast | old camera: mm to the next line | new camera: mm to the next line |", "|---|---|---|---|---|---|"]
    for i, ln in enumerate(t["lines"]):
        so = f"{t['spacing']['old'][i]:.1f}" if i < len(t["spacing"]["old"]) else "-"
        sn = f"{t['spacing']['new'][i]:.1f}" if i < len(t["spacing"]["new"]) else "-"
        L.append(f"| {ln['reading_cm']} | {ln['row']:.1f} | {ln['col']:.0f} | {ln['depth']:.0f} | {so} | {sn} |")
    L.append(f"| mean | | | | {np.mean(t['spacing']['old']):.2f} | {np.mean(t['spacing']['new']):.2f} |")
    L += ["", "Which horizon row makes the lines equally spaced (1 / (row − horizon) must be a straight line in distance, whatever f, tilt and height are). "
          "The tape is 35 to 70 px right of the centre column, so the answer is given for three camera rolls (it hardly moves: the tape's left margin "
          "heads for the centre column at the horizon, where a roll changes nothing):", "",
          "| assumed roll | best horizon row | misfit there, px | horizon rows within twice that misfit | misfit at 76.5 | at 84 | at 91 |", "|---|---|---|---|---|---|---|"]
    for roll, v in t["horizon_scan"].items():
        L.append(f"| {roll:+.0f}° | {v['best'][0]:.1f} | {v['best'][1]:.2f} | {v['range'][0]:.1f} to {v['range'][1]:.1f} | {v['at'][76.5]:.2f} | {v['at'][84.0]:.2f} | {v['at'][91.0]:.2f} |")
    L += ["", "Reading. The lines cover only rows 230 to 402, about 4 to 11 cm in front of the robot. There the old camera spaces them 10 mm apart "
          f"(mean {np.mean(t['spacing']['old']):.2f}) and the new one {np.mean(t['spacing']['new']):.2f}: the new camera stretches near distances by about 4 %. "
          "The boxes say the opposite at 15 to 30 cm, where the old camera is 4 to 9 px off and the new one within 2 px.",
          "So one pinhole camera with these numbers does not fit both the tape close up and the boxes far away to better than about 1 px. "
          "Things that could cause it, none of which these frames can separate: the tape is not flat (its lines bow by 1 to 2 px across its width, "
          "and its last line before the robot is visibly curved); the lens bends straight lines a little (the tape's right edge sags by 2 px); "
          "the hand-drawn top and bottom edges are not exactly the lid's far edge and the base's near edge.",
          "The candidate is the fit to the boxes, because the detector's sizes are compared with hand-drawn boxes and the misfit that matters is the far one. "
          "What would settle it: the `horizon` frame that was not shot (a mark at camera height on a wall at least 1 m away), "
          "and the lens height above the table measured with a ruler (the fit says 40.2 mm, `aim_kin.py` says 43.47)."]

    (out / "fit.md").write_text("\n".join(L) + "\n")
    json.dump({"git": bcv.git_hash(), "sigma_px": SIGMA_PX, "sigma_d_mm": SIGMA_D_MM, "n_obs": len(obs),
               "old": {"params": old.params, "rms_px": old.rms_px, "rms_weighted": old.rms_weighted},
               "ladder": {"+".join(free): {"params": fr.params, "stderr": fr.stderr, "rms_px": fr.rms_px, "rms_weighted": fr.rms_weighted,
                                           "horizon_row": fr.camera.horizon_row()} for free, fr in {**ladder, **alts}.items()},
               "kept": "+".join(chosen_free),
               "candidate": {"f": cand_p["f"], "tilt_deg": cand_p["tilt_deg"], "height_mm": cand_p["height_mm"], "off_mm": cand_p["off_mm"],
                             "horizon_row": cam_new.horizon_row(), "rms_px": cand.rms_px, "rms_weighted": cand.rms_weighted},
               "leave_one_out": {short(s): {k: fr.params[k] for k in chosen_free} for s, fr in loo.items()},
               "jitter_sd": dict(zip(chosen_free, J.std(axis=0).tolist())),
               "horizon_without_model": {k: {"best": v["best"], "range": v["range"]} for k, v in free_hz.items()},
               "tape": {"vanishing": t["vanishing"], "lines": t["lines"], "spacing": t["spacing"],
                        "horizon_scan": {str(k): {"best": v["best"], "range": v["range"]} for k, v in t["horizon_scan"].items()}}},
              (out / "fit.json").open("w"), indent=1)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
