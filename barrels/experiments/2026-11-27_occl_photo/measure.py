#!/usr/bin/env python3
"""Measure the photo cues on every partly seen stripe of the real train frames, side by side with the truth (analysis;
no rule, nothing judged).

For every train frame with a box label: the fixed colors' mask; the detector's stripes; for each stripe narrower than
stripe_full x W whose top and bottom pass ``read_edges``: the seen span, what today does with it (``place_sides``), and
on each side the cut-line numbers and the photo-beside numbers (``cue.py``). The truth of a side: the stripe is matched
to the labelled barrel of its body color whose box holds the stripe's middle; that side is "hidden" when the true box
runs on past the seen end by more than 0.2 W, "free" when within 0.1 W, else "unclear". A stripe on no labelled barrel
is "none".

    python barrels/experiments/2026-11-27_occl_photo/measure.py [--contains occl]

Writes results/2026-11-27_occl_photo/measure.csv.
"""
from __future__ import annotations

import argparse
import csv

import cue
import lib
from lib import det, jg, pl


def stripes_of(mask):
    cfg = det.DetConfig()
    stripes, _ = det.find_stripes(mask, lib.CAM, cfg)
    for s in stripes:
        at = det._at(s, lib.CAM)
        if at is None:
            continue
        x0, y0, x1, y1 = s.bbox
        if (x1 - x0) >= cfg.stripe_full * at.W:
            continue
        e = det.read_edges(s, at, mask, cfg)
        if e is None or (s.thin and e.inferred):
            continue
        top, bottom = max(0, e.top), min(mask.shape[0], e.bottom)
        others = tuple((o.bbox[0], o.bbox[2]) for o in stripes if o is not s and not o.thin)
        seen = det.seen_span(s, mask, at.W, top, bottom, cfg, others)
        placed = det.place_sides(s, mask, lib.CAM, at.W, top, bottom, at.bottom, cfg, others, ())
        yield s, at, e, top, bottom, seen, placed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contains", nargs="*", default=[""])
    a = ap.parse_args()
    rows = []
    for stem in lib.train_stems(tuple(a.contains)):
        frame = jg.load_frame(stem)
        mask = pl.segment(frame, lib.model())[0]
        grad = cue.gradient(frame.rgb)
        gts, _ = lib.truth(stem)
        for s, at, e, top, bottom, seen, placed in stripes_of(mask):
            cx, cy = (s.bbox[0] + s.bbox[2]) / 2, s.center_row
            g = next((g for g in gts if g.color == s.body and g.bbox[0] <= cx < g.bbox[2] and g.bbox[1] <= cy < g.bbox[3]), None)
            for side, x_end in (("L", seen.x0), ("R", seen.x1)):
                if g is None:
                    truth = "none"
                else:
                    over = (x_end - g.bbox[0]) if side == "L" else (g.bbox[2] - x_end)
                    truth = "hidden" if over > 0.2 * at.W else ("free" if abs(over) <= 0.1 * at.W else "unclear")
                m = cue.band_lines(grad, mask, side, x_end, top, bottom, at.W, at.H, cy)
                b = cue.beside(frame.rgb, side, x_end, int(s.bbox[1]), int(s.bbox[3]), at.W)
                rows.append({"stem": stem, "body": s.body, "stripe": list(s.bbox), "thin": int(s.thin), "W": round(at.W, 1),
                             "top": top, "bottom": bottom, "inferred": "+".join(sorted(e.inferred)), "sx0": seen.x0, "sx1": seen.x1,
                             "today": "" if placed is None else placed[2], "side": side, "truth": truth,
                             "gt": "" if g is None else list(g.bbox),
                             **{k: (round(v, 3) if isinstance(v, float) else v) for k, v in m.items() if k not in ("side", "x_end")},
                             "beside_diff": None if b["diff"] is None else round(b["diff"], 1)})
    lib.OUT.mkdir(parents=True, exist_ok=True)
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(lib.OUT / "measure.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, keys)
        wr.writeheader()
        wr.writerows(rows)
    print(len(rows), "sides written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
