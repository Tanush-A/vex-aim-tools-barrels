#!/usr/bin/env python3
"""Looked at AFTER round 1 (before the addendum of PREREG.md was written): which part of arm B admits each new box.

    cd barrels && env PYTHONPATH=src python experiments/2026-11-26_slack/after_round1_gains.py

For every box arm B draws that today's detector does not draw on the same mask (ordinary train frames; fixed and hand
colors; unharmed, one and two pixels shaved off), the stripe candidate it was read from is found again and asked
which of B's parts it needs:

- small: under 20 px by its own pixels (so it needs the area's second reading);
- "the rest, as seen": the rest of the barrel supports it with the edges as they are seen;
- "the rest, with the eaten pixels": it supports it only when an edge is given the eaten pixels back;
- "width with the eaten pixels": only the stripe's own width with the eaten pixels given back says "seen whole".

Tallied against what the box is by the hand boxes (found / on its barrel with the box off / not on a barrel).
Train frames only. Nothing is judged here."""
from __future__ import annotations

import collections
import dataclasses
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))
import run as R  # noqa: E402
from barrels import conditions as cnd, counting as ct, detector as det, judge as jg, pipeline as pl  # noqa: E402

CAM = R.CAM
ARM = sys.argv[1] if len(sys.argv) > 1 else "B"


def candidates(mask, cfg):
    """Every stage-2 candidate (a group of sandwiched pieces), as ``find_stripes`` forms them."""
    out = []
    for body, sw in det.sandwiches(mask, CAM, cfg).items():
        sandwich = sw.above & sw.below
        n, lab, st, _ = cv2.connectedComponentsWithStats((sw.stripe & sandwich).astype(np.uint8), connectivity=8)
        for ids in det._join_pieces(st, CAM, cfg, lab, sandwich):
            x, y = int(min(st[i][0] for i in ids)), int(min(st[i][1] for i in ids))
            bw, bh = int(max(st[i][0] + st[i][2] for i in ids)) - x, int(max(st[i][1] + st[i][3] for i in ids)) - y
            out.append((body, sw, x, y, bw, bh, int(sum(st[i][4] for i in ids)), np.isin(lab, ids)))
    return out


def route(mask, s: det.Stripe, cands, cfg) -> str:
    x0, y0, x1, y1 = s.cut_from if s.cut_from is not None else s.bbox
    match = [c for c in cands if c[0] == s.body and c[2] <= s.bbox[0] and s.bbox[2] <= c[2] + c[4] and s.bbox[1] <= c[3] and c[3] + c[5] <= s.bbox[3]]
    if not match:
        return "candidate not found again"
    body, sw, x, y, bw, bh, area, sel = max(match, key=lambda c: c[6])
    ys = np.where(sel)[0]
    at = det.BarrelAt.from_stripe_row(CAM, float(np.median(ys)) + 0.5)
    core = float(np.percentile(ys, 90) - np.percentile(ys, 10) + 1)
    lo, hi = cfg.stripe_h_min * at.Hs, cfg.stripe_h_max * at.Hs
    sh, eaten, sy0, sy1 = det._seam_reading(sw, sel, core)
    sy0, sy1 = min(y, sy0), max(y + bh, sy1)
    small, thin = area < cfg.min_area_px, core < lo
    w_today, w_give = bw >= cfg.stripe_full * at.W, bw + 2 * eaten >= cfg.stripe_full * at.W
    if not small and (lo <= core <= hi or (thin and w_today and lo <= sh <= hi)):
        return "passes stage 2 today (its box changed for another reason)"
    rest_seen = det._rest_supports(body, x, bw, sy0, sy1, at, 0.0, mask, cfg)
    rest = det._rest_supports(body, x, bw, sy0, sy1, at, eaten, mask, cfg)
    if small and (w_today or w_give):
        return "small, width" + (", as today" if w_today else " with the eaten pixels") + f" (the rest as seen: {rest_seen}, with the eaten pixels: {rest})"
    how = ("width, as today" if w_today else "the rest, as seen" if rest_seen else "the rest, with the eaten pixels" if rest
           else "width with the eaten pixels" if w_give else "?")
    return ("small, " if small else "") + how


def main() -> int:
    frames = jg.train_frames()
    stems = frames[cnd.ORDINARY]
    gts, clean = ct.load_gts(stems)
    R._init(R.hand_thresholds(stems + frames[cnd.EXTREME] + frames[cnd.EXCLUDED]))
    cfg0, cfg1 = det.DetConfig(), dataclasses.replace(det.DetConfig(), slack=ARM)
    tally: dict = collections.defaultdict(collections.Counter)
    for s in stems:
        frame = jg.load_frame(s)
        fixed = pl.segment(frame, R._STATE["model"])[0]
        hm = R._STATE["hand"].get(ct.condition_of(s))
        hand = pl.segment(frame, hm)[0] if hm is not None else fixed
        for colors, unharmed in (("fixed", fixed), ("hand", hand)):
            for px in (0, 1, 2):
                mask = R.erode(unharmed, px) if px else unharmed
                p0, p1 = det.detect(mask, cfg0, CAM), det.detect(mask, cfg1, CAM)
                base = {R.box_key(p) for p in p0}
                if all(R.box_key(p) in base for p in p1):
                    continue
                c1 = ct.classify_frame(s, p1, gts[s], clean[s])
                stripes, _ = det.find_stripes(mask, CAM, cfg1)
                found, _, _ = det.boxes_from_stripes(stripes, mask, CAM, cfg1)
                cands = candidates(mask, cfg1)
                for p, st in zip(p1, c1.boxes):
                    if R.box_key(p) in base:
                        continue
                    f = next((f for f in found if tuple(f.barrel.bbox) == tuple(p.bbox)), None)
                    r = route(mask, f.stripe, cands, cfg1) if f is not None else f"not a stripe box ({p.source})"
                    state = "found" if st == ct.FOUND else "on its barrel, box off" if st == ct.OFF else "NOT ON A BARREL"
                    tally[(colors, px)][(state, r)] += 1
                    if st != ct.FOUND or "small" in r or "width with" in r:
                        print(f"{colors} {px}px {s.replace('4A8B_', '')} {tuple(p.bbox)} {state}: {r}")
    print()
    total = collections.Counter()
    for key in sorted(tally):
        print(f"{key[0]} colors, {key[1]} px shaved off")
        for (state, r), n in sorted(tally[key].items()):
            print(f"   {n:3d}  {state:24s} {r}")
            total[(state, r)] += n
    print("all six masks")
    for (state, r), n in sorted(total.items()):
        print(f"   {n:3d}  {state:24s} {r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
