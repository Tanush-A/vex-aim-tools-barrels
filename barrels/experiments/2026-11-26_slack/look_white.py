#!/usr/bin/env python3
"""What was looked at BEFORE the pre-registration (2026-11-26_slack): the barrels of the two white tables (HOME and
CAMPUS, train frames) that the detector finds on the fixed model's mask and loses when one pixel is shaved off every
painted region. For each: the notes of the reason log that touch its hand box, with the numbers.

    cd barrels && env PYTHONPATH=src python experiments/2026-11-26_slack/look_white.py [pixels, default 1]

Train frames only (``judge.load_frame`` refuses anything else). Nothing is judged here.
"""
from __future__ import annotations

import sys
from pathlib import Path

BARRELS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BARRELS / "src"))
from barrels import conditions as cnd, counting as ct, degrade as dg, detector as det, geometry as geo, judge as jg, pipeline as pl  # noqa: E402
from barrels import hslabel as hl  # noqa: E402

CAM = geo.AIM_4A8B6118_BOXFIT
WHITE = ("home_white", "campus_study")


def touches(a, b) -> bool:
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def main() -> int:
    px = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    stems = [s for s in jg.train_frames()[cnd.ORDINARY] if ct.place_of(s) in WHITE]
    gts, clean = ct.load_gts(stems)
    model = hl.adopted_model()
    found0 = found1 = 0
    for s in stems:
        mask = pl.segment(jg.load_frame(s), model)[0]
        eroded = dg.damage(mask, [], dg.Damage(erode_px=px))
        log: list = []
        c0 = ct.classify_frame(s, det.detect(mask, cam=CAM), gts[s], clean[s])
        c1 = ct.classify_frame(s, det.detect(eroded, cam=CAM, log=log), gts[s], clean[s])
        found0 += c0.n_gt(ct.FOUND); found1 += c1.n_gt(ct.FOUND)
        for i, (a, b) in enumerate(zip(c0.gt, c1.gt)):
            if a == ct.FOUND and b != ct.FOUND:
                g = gts[s][i]
                print(f"\n{s} #{i + 1} {g.color} {tuple(g.bbox)} flags={sorted(g.flags)}: found -> {b}")
                for e in log:
                    if e["stage"] in ("stripe", "barrel", "verify", "cap", "half") and touches(e["bbox"], g.bbox):
                        rest = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in e.items() if k not in ("stage", "why", "bbox")}
                        print(f"    {e['stage']}:{e['why']} {e['bbox']} {rest}")
    print(f"\nwhite tables, {len(stems)} frames: found {found0} -> {found1} with {px} px shaved off")
    return 0


if __name__ == "__main__":
    sys.exit(main())
