#!/usr/bin/env python3
"""Worked examples in numbers, for HOW-IT-WORKS: one scene of the scorecard per rule of this experiment, with the
boxes `base` and an arm draw and the numbers the rule compared (read off the detector's reason log; nothing is
computed here that the detector does not compute). The example barrel is the middle-sized one of a pool.

    python barrels/experiments/2026-11-20_occl_vertical/example.py [--pool "HOME hand masks"] [--arm all]
Output: text, and results/2026-11-20_occl_vertical/examples.md.
"""
from __future__ import annotations

import argparse

import common
from barrels import detect_types as dtp, detector as det, geometry as geo, occlude as oc

CAM = geo.AIM_4A8B6118_BOXFIT
CASES = (("top", 0.5, "L"), ("bottom", 0.5, "L"), ("post", 0.5, "L"), ("barrel_side/same", 0.5, "L"), ("barrel_low/same", 0.75, "L"),
         ("barrel_front/other", 0.75, "L"))
STAGES = ("half", "pair", "slice", "cap")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pool", default="HOME hand masks")
    ap.add_argument("--arm", default="all")
    args = ap.parse_args(argv)
    occ = common.scorecard()
    stems, segs, pools, dropped = common.pools_and_segs(occ)
    srcs = pools[args.pool]
    mid = sorted(srcs, key=lambda s: s.width)[len(srcs) // 2]
    L = [f"# Worked examples: `{args.arm}` against `base`", "",
         f"The barrel: {args.pool}, `{mid.stem}`, {dtp.COLOR_NAMES[mid.color]}, hand-drawn box {list(mid.bbox)} ({mid.width} wide, {mid.height} tall).", ""]
    for key, amount, variant, src, sc in occ.scenes_of(srcs):
        if src is not mid or (key, amount, variant) not in [(k, a, v if k.split("/")[0] in oc.SIDED else "") for k, a, v in CASES]:
            continue
        log: list = []
        new = det.detect(sc.mask, common.vert_arms.ARMS[args.arm], CAM, log=log)
        old = det.detect(sc.mask, common.vert_arms.BASE, CAM)
        L += [f"## {occ.ROW_NAME[key]}, {int(100 * amount)} % hidden", "",
              f"- full box of the hidden barrel: {list(sc.target[1])}" + (f"; the barrel in front: {dtp.COLOR_NAMES[sc.fronts[0][0]]} {list(sc.fronts[0][1])}" if sc.fronts else ""),
              f"- `base` draws: {[(dtp.COLOR_NAMES[b.color], list(b.bbox)) for b in old] or 'nothing'}",
              f"- `{args.arm}` draws: {[(dtp.COLOR_NAMES[b.color], list(b.bbox), '+'.join(sorted(b.flags))) for b in new] or 'nothing'}",
              f"- found under the v2 rule: `base` {occ.found_v2(old, src.color, src.bbox)}, `{args.arm}` {occ.found_v2(new, src.color, src.bbox)}; "
              f"overlap of the best box with the full box: {max([det.box_iou(b.bbox, sc.target[1]) for b in new if b.color == src.color], default=0):.2f}"]
        for e in log:
            if e["stage"] in STAGES and e["why"] == "kept":
                vals = {k: (round(v, 1) if isinstance(v, float) else v) for k, v in e.items() if k not in ("stage", "why")}
                L.append(f"- `{e['stage']}` kept: {vals}")
        L.append("")
    common.OUT.mkdir(parents=True, exist_ok=True)
    (common.OUT / "examples.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
