#!/usr/bin/env python3
"""A census before the fix (no acceptance number comes from here): can a barrel's own side be told from a cut side?

A barrel bulges: it is 25.5 mm wide at the stripe and 18 mm at the lid and at the base, so at its own side the
outline runs inward toward the top and toward the bottom, by up to (25.5 - 18) / 2 / 25.5 = 0.147 of its width. A
straight upright edge in front of it cuts every row at the same column.

For every source barrel of the scorecard (``run.py``: the unhidden barrels of the train frames, three pools), alone
on an empty mask, and for the same barrel cut by a straight edge (``occlude`` kind ``edge``) and by a slanted one, this
measures on each side of what is seen:

  end_top, end_bottom   how far inward (in barrel widths W, + = inward) the body color ends in the top / bottom
                        sixth of the barrel's rows, compared with where it ends in the rows next to the stripe.

    python barrels/experiments/2026-11-19_det_occl/outline_census.py
Output: results/2026-11-19_det_occl/outline_census.md, outline_census.csv.
"""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location("det_occl_run", HERE / "run.py")
R = importlib.util.module_from_spec(spec); sys.modules["det_occl_run"] = R; spec.loader.exec_module(R)
from barrels import detector as det, occlude as oc  # noqa: E402

OUT = R.OUT


def side_insets(mask: np.ndarray, body: int, stripe: det.Stripe, rows, W: float) -> dict:
    """{'L': (end_top, end_bottom), 'R': ...} in units of W; None where a band holds no body pixel."""
    h, w = mask.shape
    top, bottom = max(0, int(round(rows.top))), min(h, int(round(rows.bottom)))
    y0, y1 = stripe.bbox[1], stripe.bbox[3]
    hs = max(2, int(round(rows.stripe_bottom - rows.stripe_top)))
    band = max(2, int(round((bottom - top) / 6)))
    bm = mask == body

    def ends(r0, r1):
        cols = np.flatnonzero(bm[max(0, r0):max(0, r1)].any(axis=0))
        return (int(cols[0]), int(cols[-1]) + 1) if len(cols) else None

    mid_a, mid_b = ends(y0 - hs, y0), ends(y1, y1 + hs)
    mids = [m for m in (mid_a, mid_b) if m]
    t, b = ends(top, top + band), ends(bottom - band, bottom)
    out = {}
    if not mids:
        return {"L": (None, None), "R": (None, None)}
    mL, mR = min(m[0] for m in mids), max(m[1] for m in mids)
    out["L"] = (None if t is None else (t[0] - mL) / W, None if b is None else (b[0] - mL) / W)
    out["R"] = (None if t is None else (mR - t[1]) / W, None if b is None else (mR - b[1]) / W)
    return out


def main() -> int:
    stems = R.train_stems()
    segs = R.segmentations(stems)
    pools, _ = R.build_sources(segs)
    cfg = R.occl_arms.BASE
    rows_out = []
    for pool in R.POOLS:
        for src in pools[pool]:
            for kind, amount, side, lean in [("edge", 0.0, "L", 1)] + [(k, a, s, ln) for k in ("edge", "slant") for a in oc.AMOUNTS
                                                                         for s in ("L", "R") for ln in ((1, -1) if k == "slant" else (1,))]:
                sc = oc.make_scene(src, kind, amount, side, lean=lean)
                # the stripe of the barrel: the widest stripe piece of its body color the finder's first stage would see
                stripes = [s for s in det.find_stripes(sc.mask, R.CAM, cfg) if s.body == src.color]
                if not stripes:
                    continue
                s = max(stripes, key=lambda s: s.bbox[2] - s.bbox[0])
                g = det._stripe_geometry(R.CAM, s.center_row)
                if g is None:
                    continue
                ins = side_insets(sc.mask, src.color, s, g[1], g[1].width_px)
                for sd in ("L", "R"):
                    what = "own" if (amount == 0 or sd != side) else ("cut straight" if kind == "edge" else f"cut slanted {'+' if lean > 0 else '-'}")
                    rows_out.append({"pool": pool, "stem": src.stem.replace("4A8B_", ""), "W": round(g[1].width_px, 1), "kind": kind, "amount": amount,
                                     "cut_side": side if amount else "", "side": sd, "what": what,
                                     "end_top": "" if ins[sd][0] is None else round(ins[sd][0], 3), "end_bottom": "" if ins[sd][1] is None else round(ins[sd][1], 3)})
    with (OUT / "outline_census.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys())); w.writeheader(); w.writerows(rows_out)

    def stat(v):
        v = np.asarray([x for x in v if x != ""], float)
        if not len(v):
            return "-"
        return f"{np.median(v):+.3f} ({np.percentile(v, 5):+.3f} to {np.percentile(v, 95):+.3f}; min {v.min():+.3f}, max {v.max():+.3f}; n {len(v)})"

    L = ["# Can a barrel's own side be told from a cut side? (a census; no acceptance number)", "",
         "`end_top` / `end_bottom`: how far inward the body color ends in the top / bottom sixth of the barrel's rows, compared with the rows next to "
         "the stripe, in barrel widths (+ = inward). Median (5th to 95th percentile; min, max; n). `both` = the smaller of the two.", "",
         "| pool | side | end_top | end_bottom | the smaller of the two |", "|---|---|---|---|---|"]
    for pool in R.POOLS + ("ALL",):
        for what in ("own", "cut straight", "cut slanted +", "cut slanted -"):
            rs = [r for r in rows_out if (pool == "ALL" or r["pool"] == pool) and r["what"] == what]
            both = [min(r["end_top"], r["end_bottom"]) for r in rs if r["end_top"] != "" and r["end_bottom"] != ""]
            L.append(f"| {pool} | {what} | {stat([r['end_top'] for r in rs])} | {stat([r['end_bottom'] for r in rs])} | {stat(both)} |")
    L += ["", "Own sides by barrel size (all pools; the smaller of the two):", "", "| expected width | the smaller of end_top and end_bottom |", "|---|---|"]
    for name, lo, hi in (("under 35 px", 0, 35), ("35 to 60 px", 35, 60), ("over 60 px", 60, 1e9)):
        rs = [r for r in rows_out if r["what"] == "own" and lo <= r["W"] < hi and r["end_top"] != "" and r["end_bottom"] != ""]
        L.append(f"| {name} | {stat([min(r['end_top'], r['end_bottom']) for r in rs])} |")
    (OUT / "outline_census.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
