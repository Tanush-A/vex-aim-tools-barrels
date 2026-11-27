#!/usr/bin/env python3
"""Looked at BEFORE the pre-registration, second part: for every stripe refused as "height" or "area" on the white
tables' masks with one pixel shaved off, the numbers a second reading could use: the gap between the bodies, the
seam reading, the widths as shares of W, the seen top and bottom against the predicted ones, the body's span.
And, for the same barrel on the unharmed mask, the rule that drew its box.

    cd barrels && env PYTHONPATH=src python experiments/2026-11-26_slack/look_white_detail.py [pixels, default 1]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

BARRELS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BARRELS / "src"))
from barrels import conditions as cnd, counting as ct, degrade as dg, detector as det, geometry as geo, judge as jg, pipeline as pl  # noqa: E402
from barrels import hslabel as hl  # noqa: E402

CAM = geo.AIM_4A8B6118_BOXFIT
CFG = det.DetConfig()
WHITE = ("home_white", "campus_study")


def touches(a, b) -> bool:
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def numbers(mask, e) -> str:
    body = e["body"]
    x0, y0, x1, y1 = e["bbox"]
    sw = det.sandwiches(mask, CAM, CFG)[body]
    sel = np.zeros(mask.shape, bool)
    sel[y0:y1, x0:x1] = (sw.stripe & sw.above & sw.below)[y0:y1, x0:x1]
    ys = np.where(sel)[0]
    if not len(ys):
        return "no pixels"
    at = det.BarrelAt.from_stripe_row(CAM, float(np.median(ys)) + 0.5)
    core = float(np.percentile(ys, 90) - np.percentile(ys, 10) + 1)
    gap = float(np.median((sw.dn - sw.up - 1)[sel]))
    top, bottom = det._body_extent(mask, body, x0, x1, y0, y1)
    span = det._body_span(mask, body, x0, x1, max(0, top), min(mask.shape[0], bottom), y0, y1) if bottom - top >= 2 else None
    return (f"area {int(sel.sum())} core_h {core:.1f} gap {gap:.1f} seam {(core + gap) / 2:.1f} | Hs {at.Hs:.1f} floor {CFG.stripe_h_min * at.Hs:.1f} "
            f"W {at.W:.1f} H {at.H:.1f} tol {at.tol(CFG):.1f} | stripe w {x1 - x0} = {(x1 - x0) / at.W:.2f} W | top seen {top} pred {at.top:.1f} "
            f"({top - at.top:+.1f}) bottom seen {bottom} pred {at.bottom:.1f} ({bottom - at.bottom:+.1f}) | body span {span} "
            f"= {((max(span[1], x1) - min(span[0], x0)) / at.W if span else 0):.2f} W, ends apart L {abs(span[0] - x0) if span else '-'} R {abs(span[1] - x1) if span else '-'} "
            f"(cut tol {det.edge_tol(CFG, at.W):.1f}) | floor area 0.18 W Hs = {0.18 * at.W * at.Hs:.1f}")


def main() -> int:
    px = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    stems = [s for s in jg.train_frames()[cnd.ORDINARY] if ct.place_of(s) in WHITE]
    gts, clean = ct.load_gts(stems)
    model = hl.adopted_model()
    for s in stems:
        mask = pl.segment(jg.load_frame(s), model)[0]
        eroded = dg.damage(mask, [], dg.Damage(erode_px=px))
        log0: list = []
        log: list = []
        p0 = det.detect(mask, cam=CAM, log=log0)
        c0 = ct.classify_frame(s, p0, gts[s], clean[s])
        c1 = ct.classify_frame(s, det.detect(eroded, cam=CAM, log=log), gts[s], clean[s])
        for i, (a, b) in enumerate(zip(c0.gt, c1.gt)):
            if a == ct.FOUND and b != ct.FOUND:
                g = gts[s][i]
                print(f"\n{s} #{i + 1} {g.color} {tuple(g.bbox)} flags={sorted(g.flags)}: found -> {b}")
                for e in log0:
                    if e["why"] == "kept" and "box" in e and det.box_iou(e["box"], g.bbox) > 0.5:
                        print(f"    unharmed: {e['stage']} kept {e['bbox']} box {e['box']} rule {e.get('rule')}")
                        if e["stage"] == "barrel":
                            print("      " + numbers(mask, e))
                for e in log:
                    if e["stage"] == "stripe" and e["why"] in ("height", "area", "width") and touches(e["bbox"], g.bbox):
                        print(f"    eroded: stripe:{e['why']} {e['bbox']} body {e['body']}")
                        print("      " + numbers(eroded, e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
