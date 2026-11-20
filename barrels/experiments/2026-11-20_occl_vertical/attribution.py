#!/usr/bin/env python3
"""Which test refuses the hidden barrel, in the seven rows of the scorecard this experiment is about (a measurement,
made before any rule is designed). For every scene of those rows that an arm does not find: every entry of the
detector's reason log (``det.detect(..., log=[])``) that touches the hidden barrel's full box, all stages (stripe,
barrel, piece, cap), as a "signature"; counted per cell. Also what the scene still shows of the barrel.

    python barrels/experiments/2026-11-20_occl_vertical/attribution.py [--arm base] [--tiles top:0.5,bottom:0.5]
Output: results/2026-11-20_occl_vertical/attribution_<arm>.md; sheets/attr_<arm>_<row>_<amount>.png (ignored) with --tiles.
"""
from __future__ import annotations

import argparse
import collections

import cv2
import numpy as np

import common
from barrels import detector as det, geometry as geo, occlude as oc
from barrels.io import BLUE, ORANGE

CAM = geo.AIM_4A8B6118_BOXFIT


def touches(a, b) -> bool:
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def signature(log: list, box, color: int) -> str:
    """The refusals that touch the box: stripe / barrel entries of this body color, cap entries of this color, in log order."""
    out = []
    for e in log:
        if e["why"] == "kept" or not touches(e["bbox"], box):
            continue
        if e["stage"] in ("stripe", "barrel", "cap") and e.get("body") not in (None, color):
            continue
        if e["stage"] == "piece":
            continue
        out.append(f"{e['stage']}:{e['why']}")
    return " + ".join(dict.fromkeys(out)) or "nothing tried"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arm", default="base")
    ap.add_argument("--tiles", default="", help="row:amount pairs to draw, comma-separated (first 24 missed scenes of each)")
    args = ap.parse_args(argv)
    occ = common.scorecard()
    cfg = common.vert_arms.ARMS[args.arm]
    stems, segs, pools, dropped = common.pools_and_segs(occ)
    want = {(t.split(":")[0], float(t.split(":")[1])) for t in args.tiles.split(",") if t}
    sig = collections.defaultdict(collections.Counter)
    n = collections.Counter(); found = collections.Counter(); front_found = collections.Counter(); fronts = collections.Counter()
    tiles = collections.defaultdict(list)
    for pool in occ.POOLS:
        for key, amount, variant, src, sc in occ.scenes_of(pools[pool]):
            if key not in common.TARGET_ROWS:
                continue
            r = occ.score_scene(sc, cfg)
            cell = (key, amount)
            n[cell] += 1; found[cell] += r["found"]; fronts[cell] += r["fronts"]; front_found[cell] += r["fronts_found"]
            if not r["found"]:
                s = signature(r["log"], sc.target[1], sc.target[0])
                if r["place"]:
                    s = "box in the right place, not v2 | " + s
                elif r["fronts"] and not r["fronts_found"]:
                    s = "front barrel not found | " + s
                sig[cell][s] += 1
                if cell in want and len(tiles[cell]) < 24:
                    tiles[cell].append(occ.render(sc, r["preds"], f"{src.stem.split('_', 3)[-1]} {variant} {s[:28]}"))
    L = [f"# Which test refuses the hidden barrel (`{args.arm}`), the seven rows", "",
         f"Sources: {', '.join(f'{p} {len(pools[p])}' for p in occ.POOLS)}. Per cell: found of n; then, for the scenes not found, the "
         "refusals in the reason log that touch the barrel's full box (stage:test, in log order), most frequent first.", ""]
    for key in common.TARGET_ROWS:
        for amount in oc.AMOUNTS:
            c = (key, amount)
            L.append(f"## {occ.ROW_NAME[key]}, {int(round(100 * amount))} % hidden: found {found[c]} of {n[c]}" +
                     (f"; front barrel found {front_found[c]} of {fronts[c]}" if fronts[c] else ""))
            L += [f"- {v} x {k}" for k, v in sig[c].most_common(8)] + [""]
    common.OUT.mkdir(parents=True, exist_ok=True)
    (common.OUT / f"attribution_{args.arm}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    d = common.OUT / "sheets"
    for (key, amount), ts in tiles.items():
        d.mkdir(parents=True, exist_ok=True)
        while len(ts) % 6:
            ts.append(np.zeros_like(ts[0]))
        cv2.imwrite(str(d / f"attr_{args.arm}_{key.replace('/', '_')}_{int(100 * amount)}.png"), np.vstack([np.hstack(ts[i:i + 6]) for i in range(0, len(ts), 6)]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
