#!/usr/bin/env python3
"""Looked at AFTER round 1 (before the addendum of PREREG.md was written): why an arm does what it does.

    cd barrels && env PYTHONPATH=src python experiments/2026-11-26_slack/after_round1.py lost  <fixed|hand> <pixels> <ARM>
    cd barrels && env PYTHONPATH=src python experiments/2026-11-26_slack/after_round1.py boxes <fixed|hand> <pixels> <ARM>

``lost``: the barrels today's detector finds on the unharmed mask, loses with <pixels> shaved off, and the arm does
not bring back: the reason-log notes of the arm that touch the hand box, and a tally of them.
``boxes``: every box the arm draws on that mask that today's detector does not, and that is not a strict hit: the
stripe it was read from, with the numbers of the second reading (the stripe's own height, the gap, the eaten pixels,
which of the two "seen whole" readings said yes).

Train frames only (``judge.load_frame``). Nothing is judged here."""
from __future__ import annotations

import collections
import dataclasses
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))
import run as R  # noqa: E402
from barrels import conditions as cnd, counting as ct, detector as det, judge as jg, pipeline as pl  # noqa: E402

CAM = R.CAM


def touches(a, b) -> bool:
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def stripe_numbers(mask, s: det.Stripe, cfg: det.DetConfig) -> str:
    """The second reading of a stripe as ``find_stripes`` computes it (from the sandwiched pixels inside its box)."""
    x0, y0, x1, y1 = s.bbox
    sw = det.sandwiches(mask, CAM, cfg)[s.body]
    sel = np.zeros(mask.shape, bool)
    sel[y0:y1, x0:x1] = (sw.stripe & sw.above & sw.below)[y0:y1, x0:x1]
    ys = np.where(sel)[0]
    if not len(ys):
        return "no sandwiched pixels in its box"
    at = det._at(s, CAM)
    core = float(np.percentile(ys, 90) - np.percentile(ys, 10) + 1)
    sh, eaten, sy0, sy1 = det._seam_reading(sw, sel, core)
    bw = x1 - x0
    r1 = bw + 2 * eaten >= cfg.stripe_full * at.W
    r2 = det._rest_supports(s.body, x0, bw, min(y0, sy0), max(y1, sy1), at, eaten, mask, cfg)
    top, bottom = det._body_extent(mask, s.body, x0, x1, y0, y1)
    return (f"pixels {int(sel.sum())} own height {core:.1f} gap {2 * sh - core:.1f} seam {sh:.1f} eaten {eaten:.2f} | Hs {at.Hs:.1f} (floor {cfg.stripe_h_min * at.Hs:.1f}) "
            f"W {at.W:.1f} H {at.H:.1f} | width {bw} = {bw / at.W:.2f} W, with the eaten pixels {(bw + 2 * eaten) / at.W:.2f} W | seen whole by width: {r1}, by the rest: {r2} | "
            f"top {top} (predicted {at.top:.1f}) bottom {bottom} (predicted {at.bottom:.1f}) tol {at.tol(cfg):.1f} | floor_px {s.floor_px} marginal {s.marginal}")


def main() -> int:
    what, colors, px, arm = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    frames = jg.train_frames()
    stems = frames[cnd.ORDINARY]
    gts, clean = ct.load_gts(stems)
    R._init(R.hand_thresholds(stems + frames[cnd.EXTREME] + frames[cnd.EXCLUDED]))
    cfg0, cfg1 = det.DetConfig(), dataclasses.replace(det.DetConfig(), slack=arm)
    tally = collections.Counter()
    n = 0
    for s in stems:
        frame = jg.load_frame(s)
        hm = R._STATE["hand"].get(ct.condition_of(s)) if colors == "hand" else None
        unharmed = pl.segment(frame, hm or R._STATE["model"])[0]
        mask = R.erode(unharmed, px) if px else unharmed
        log: list = []
        p0, p1 = det.detect(mask, cfg0, CAM), det.detect(mask, cfg1, CAM, log=log)
        cu = ct.classify_frame(s, det.detect(unharmed, cfg0, CAM), gts[s], clean[s])
        c0, c1 = ct.classify_frame(s, p0, gts[s], clean[s]), ct.classify_frame(s, p1, gts[s], clean[s])
        if what == "lost":
            for i, (u, a, b) in enumerate(zip(cu.gt, c0.gt, c1.gt)):
                if u == ct.FOUND and a != ct.FOUND and b != ct.FOUND:
                    g = gts[s][i]
                    notes = [e for e in log if e["stage"] in ("stripe", "barrel", "verify", "cap") and touches(e["bbox"], g.bbox)]
                    whys = sorted({f"{e['stage']}:{e['why']}" for e in notes if e["stage"] != "cap"} | ({"box drawn, " + b} if b == ct.OFF else set()))
                    key = " + ".join(w for w in whys if w != "barrel:kept") or ("only cap notes" if notes else "no note at all")
                    tally[key] += 1
                    n += 1
                    print(f"{s.replace('4A8B_', '')} #{i + 1} {tuple(g.bbox)} flags={sorted(g.flags)} -> {b}: {key}")
                    for e in notes:
                        if e["stage"] != "cap":
                            rest = {k: (round(v, 1) if isinstance(v, float) else v) for k, v in e.items() if k not in ("stage", "why", "bbox", "body")}
                            print(f"      {e['stage']}:{e['why']} body {e.get('body')} {e['bbox']} {rest}")
        else:
            base = {R.box_key(p) for p in p0}
            new = [(p, st) for p, st in zip(p1, c1.boxes) if R.box_key(p) not in base and st != ct.FOUND]
            if new:
                layers = det.sandwiches(mask, CAM, cfg1)
                stripes, _ = det.find_stripes(mask, CAM, cfg1, None, layers)
                found, _, _ = det.boxes_from_stripes(stripes, mask, CAM, cfg1)
                for p, st in new:
                    n += 1
                    tally[st] += 1
                    f = next((f for f in found if tuple(f.barrel.bbox) == tuple(p.bbox)), None)
                    print(f"{s.replace('4A8B_', '')} {p.color} {tuple(p.bbox)} {st} flags={sorted(p.flags)} rule {f.rule if f else '?'}; hand boxes {[tuple(g.bbox) for g in gts[s]]}")
                    if f is not None:
                        print(f"      stripe {f.stripe.bbox} thin {f.stripe.thin}: " + stripe_numbers(mask, f.stripe, cfg1))
    print(f"\n{what}, {colors} colors, {px} px shaved off, arm {arm}: {n}")
    for k, v in tally.most_common():
        print(f"  {v:3d}  {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
