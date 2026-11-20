#!/usr/bin/env python3
"""Worked examples in numbers for the walkthrough: for a few scorecard cells, the first scene (HOME hand masks first)
that one arm finds and another does not, with the boxes both draw and the numbers the rule compared (read off the
detector's reason log; for a cap, the sizes its top row gives). Nothing is chosen or scored here.

    python barrels/experiments/2026-11-20_occl_combined/examples.py
Output: text, and results/2026-11-20_occl_combined/examples.md.
"""
from __future__ import annotations

import sys
import types

import common as C
from barrels import detect_types as dtp, detector as det

A = C.A
# (scorecard row, amount, the arm without, the arm with)
CASES = (("barrel_front/other", 0.75, "stack", "combined"), ("barrel_front/same", 0.75, "stack", "combined"),
         ("barrel_low/same", 0.75, "stack", "combined"), ("post", 0.5, "stack", "combined"), ("top", 0.5, "stack", "combined"),
         ("bottom", 0.5, "stack", "combined"), ("barrel_side/same", 0.5, "stack", "combined"), ("edge", 0.5, "stack", "combined"),
         ("edge", 0.75, "combined", "combined+thin"), ("frame", 0.75, "combined", "combined+thin"))
STAGES = ("half", "pair", "slice", "cap")


def main() -> int:
    sys.path.insert(0, str(C.OCCL))
    R = C.load("det_occl_run", C.OCCL / "run.py")
    R.occl_arms = types.SimpleNamespace(ARMS=A.ARMS, BASE=A.SOURCE_BASE)
    pools, _ = R.build_sources(R.segmentations(R.train_stems()))
    L = ["# Worked examples in numbers (for `walkthrough.md`)", ""]
    for key, amount, without, with_ in CASES:
        hit = None
        for pool in R.POOLS:
            for k, am, variant, src, sc in R.scenes_of(pools[pool]):
                if (k, am) != (key, amount):
                    continue
                old = A.RULES_DETECT(sc.mask, A.rule_config(A.ARMS[without]), R.CAM)
                log: list = []
                new = A.RULES_DETECT(sc.mask, A.rule_config(A.ARMS[with_]), R.CAM, log)
                if R.found_v2(new, src.color, src.bbox) and not R.found_v2(old, src.color, src.bbox):
                    hit = (pool, variant, src, sc, old, new, log)
                    break
            if hit:
                break
        L += [f"## {R.ROW_NAME[key]}, {int(100 * amount)} % hidden: `{without}` → `{with_}`", ""]
        if not hit:
            L += ["- no scene that the second arm finds and the first does not", ""]
            continue
        pool, variant, src, sc, old, new, log = hit
        L += [f"- {pool}, `{src.stem.replace('4A8B_', '')}`, {dtp.COLOR_NAMES[src.color]}, full box {list(sc.target[1])} ({src.width} wide, {src.height} tall), variant `{variant}`"
              + (f"; the barrel in front: {dtp.COLOR_NAMES[sc.fronts[0][0]]} {list(sc.fronts[0][1])}" if sc.fronts else ""),
              f"- `{without}` draws: {[(dtp.COLOR_NAMES[b.color], list(b.bbox)) for b in old] or 'nothing'}",
              f"- `{with_}` draws: {[(dtp.COLOR_NAMES[b.color], list(b.bbox), '+'.join(sorted(b.flags)), C.drawn_by(log, b.bbox)) for b in new] or 'nothing'}",
              f"- overlap of the best box with the full box: {max([det.box_iou(b.bbox, sc.target[1]) for b in new if b.color == src.color], default=0):.2f}"]
        for e in log:
            if e["stage"] in STAGES and e["why"] == "kept":
                vals = {k: (round(v, 1) if isinstance(v, float) else v) for k, v in e.items() if k not in ("stage", "why")}
                L.append(f"- `{e['stage']}` kept: {vals}")
                if e["stage"] == "cap":
                    top = e["bbox"][1]
                    d = min(range(45, 900), key=lambda mm: abs(R.CAM.barrel_rows(mm).top - top))
                    r = R.CAM.barrel_rows(d)
                    upper = r.stripe_top - r.top
                    L.append(f"  - the cap's top row {top} → a barrel {d} mm away: W {r.width_px:.1f}, H {r.bottom - r.top:.1f}, upper body {upper:.1f} tall, bottom {r.bottom:.1f}; "
                             f"the cap is {e['bbox'][2] - e['bbox'][0]} wide ({(e['bbox'][2] - e['bbox'][0]) / r.width_px:.2f} W) and {e['bbox'][3] - e['bbox'][1]} tall "
                             f"({(e['bbox'][3] - e['bbox'][1]) / upper:.2f} of an upper body)")
        for s in det.find_stripes(sc.mask, R.CAM, A.rule_config(A.ARMS[with_])):
            if s.body == src.color and s.small:
                g = det._stripe_geometry(R.CAM, s.center_row)
                if g is None:
                    continue
                d, rows = g
                W, H = rows.width_px, rows.bottom - rows.top
                x0, y0, x1, y1 = s.bbox
                span = det._body_span(sc.mask, s.body, x0, x1, max(0, int(round(rows.top))), int(round(rows.bottom)), y0, y1)
                sx0, sx1 = (min(span[0], x0), max(span[1], x1)) if span else (x0, x1)
                costs = det._end_costs(s, sc.mask, R.CAM, A.rule_config(A.ARMS[with_]), sx0, sx1)
                L.append(f"- thin stripe piece {list(s.bbox)}: its row {s.center_row:.1f} → {d:.0f} mm, W {W:.1f}, H {H:.1f}, top {rows.top:.1f}, bottom {rows.bottom:.1f}; "
                         f"seen columns {sx0} to {sx1} ({(sx1 - sx0) / W:.2f} W); limit {0.05 * H:.1f} rows; cost of the left end {costs[0] * H:.1f} rows, of the right end {costs[1] * H:.1f} rows")
        L.append("")
    (C.OUT / "examples.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
