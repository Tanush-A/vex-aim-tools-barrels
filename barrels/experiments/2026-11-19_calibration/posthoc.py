#!/usr/bin/env python3
"""TODO A4, after the validation failed (2026-11-19): why does the camera that fits the ruler frames not fit
the other sessions? POST HOC: written after validation.md was seen. It decides nothing and adopts nothing.

1. Without any camera model: a hand-drawn box of the ruler set against the hand-drawn boxes of each train set
   whose top edge is on the same row (within 4 px). If the sessions shared one camera pose and one way of
   drawing, a barrel with its top on the same row would be the same size everywhere.
2. With the model: for each set, the tilt at which the median "bottom from top" error is zero (f 400; camera
   height 43.47 and 40.2). One camera fits every session only if those tilts agree.

Train frames and the ruler frames only; a test frame is never opened.

    python barrels/experiments/2026-11-19_calibration/posthoc.py

Output: results/2026-11-19_calibration/posthoc.md
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))
from barrels import camfit as cf, cv as bcv, detector as det, geometry as geo, io  # noqa: E402
import validate as va  # noqa: E402

OUT = va.OUT
SETS = ("HOME", "CAMPUS", "BLACK", "WOOD")
TOP_TOL = 4


def zero_tilt(tops_bottoms: list[tuple[float, float]], height_mm: float) -> float:
    """The tilt (f 400) at which the median of predicted-bottom-from-top minus drawn bottom is zero."""
    tilts = np.arange(18.0, 24.001, 0.02)
    meds = []
    for t in tilts:
        cam = geo.CameraModel(f=400.0, tilt_deg=float(t), height_mm=height_mm)
        e = [det.predicted_bottom(cam, y0) - y1 for y0, y1 in tops_bottoms]
        meds.append(np.median([x for x in e if np.isfinite(x)]))
    meds = np.array(meds)
    i = int(np.argmin(np.abs(meds)))
    return float(tilts[i])


def main() -> int:
    rows, _ = va.size_rows(va.train_stems())
    shots = [s for s in cf.load_ruler_set() if s.bbox[3] < io.FRAME_H and "held" not in s.flags]
    L = ["# After the failed validation: is the ruler session like the other sessions? (post hoc)", "",
         f"git {bcv.git_hash()}. Written after `validation.md` was seen. It decides nothing. Train frames and ruler frames only.", "",
         "## 1. No camera model: boxes whose top edge is on the same row", "",
         f"For each whole box of the ruler set: the hand-drawn boxes of each train set whose top row is within {TOP_TOL} px of it "
         "(unoccluded, untruncated boxes, as in the size check). Height and width in px; `n` = how many boxes.", "",
         "| ruler frame | mm | top row | ruler box: height | width | " + " | ".join(f"{g}: n, median height, width" for g in SETS) + " |",
         "|---|---|---|---|---|" + "---|" * len(SETS)]
    ratios = {g: [] for g in SETS}
    for s in shots:
        x0, y0, x1, y1 = s.bbox
        cells = []
        for g in SETS:
            rs = [r for r in rows if r["set"] == g and abs(r["bbox"][1] - y0) <= TOP_TOL]
            if rs:
                h, w = np.median([r["h"] for r in rs]), np.median([r["w"] for r in rs])
                cells.append(f"{len(rs)}, {h:.0f}, {w:.0f}")
                if len(rs) >= 3:
                    ratios[g].append((h / (y1 - y0), w / (x1 - x0)))
            else:
                cells.append("-")
        L.append(f"| {s.stem.split('_')[-1]} | {s.d_ruler_mm:.0f} | {y0} | {y1 - y0} | {x1 - x0} | " + " | ".join(cells) + " |")
    L += ["", "Train box / ruler box at the same top row, averaged over the ruler frames with at least 3 such boxes:", "",
          "| set | ruler frames used | height ratio | width ratio |", "|---|---|---|---|"]
    for g in SETS:
        if ratios[g]:
            a = np.array(ratios[g])
            L.append(f"| {g} | {len(a)} | {a[:, 0].mean():.2f} | {a[:, 1].mean():.2f} |")

    L += ["", "## 2. With the model: the tilt each set would need", "",
          "f 400. For each set, the tilt at which the median error of the bottom inferred from the top row is zero, over its far and mid boxes "
          "(drawn width under 60 px), for the two camera heights. The horizon row follows from the tilt.", "",
          "| boxes | n | camera height 43.47: tilt | horizon row | camera height 40.2: tilt | horizon row |", "|---|---|---|---|---|---|"]

    def line(name, tb):
        cells = []
        for h in (geo.H_CAM_MM, 40.2):
            t = zero_tilt(tb, h)
            cells += [f"{t:.2f}°", f"{geo.CameraModel(f=400.0, tilt_deg=t, height_mm=h).horizon_row():.0f}"]
        return f"| {name} | {len(tb)} | " + " | ".join(cells) + " |"

    far_ruler = [(s.bbox[1], s.bbox[3]) for s in shots if s.d_ruler_mm >= 150]
    L.append(line("ruler set (150, 200, 300 mm)", far_ruler))
    per_set = {g: [(r["bbox"][1], r["bbox"][3]) for r in rows if r["set"] == g and r["band"] != "near"] for g in SETS}
    for g in SETS:
        if per_set[g]:
            L.append(line(g, per_set[g]))
    pooled = per_set["HOME"] + per_set["CAMPUS"]
    L.append(line("HOME and CAMPUS together", pooled))
    t2 = zero_tilt(pooled, 40.2)
    L += ["", "The wood ladder is 8 scenes under 9 lamp settings with the boxes copied between settings, so its 72 boxes are 8 independent ones.",
          "", "## Reading", "",
          "- At the same top row the wood boxes (same table and day as the ruler set) are the size of the ruler boxes; campus and black boxes are larger. "
          "The sessions do not share one geometry to better than a few percent, or the boxes were not drawn the same way.",
          "- Every set, the ruler set included, wants a tilt within about 0.3° of the others once the camera height is fixed: horizon rows 79 to 84 at 43.47 mm, 85 to 90 at 40.2 mm.",
          "- The ruler fit (tilt 20.4°, height 40.2 mm) takes away the drift with distance that the old camera has (`validation.md`, by distance), "
          "but sits 0.5° from what HOME and CAMPUS want at that height, which is the constant 6 to 8 px it is off by there.",
          f"- A camera with the ruler set's height and the tilt HOME and CAMPUS want together: f 400, tilt {t2:.2f}° (rounded {round(t2 / 0.05) * 0.05:.2f}°), height 40.2 mm, "
          f"horizon row {geo.CameraModel(f=400.0, tilt_deg=round(t2 / 0.05) * 0.05, height_mm=40.2).horizon_row():.1f}. Its tilt is read off the train boxes, so the size check is "
          "no longer an independent test of it; PREREG.md, addendum."]
    (OUT / "posthoc.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
