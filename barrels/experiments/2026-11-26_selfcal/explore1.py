"""Exploration 1 (in-sample, before PREREG): what the bands of a HAND box read, per condition. Train frames only.

For every unflagged hand box: the body bands (upper + lower) and the stripe band, centre columns; hue (on the class's
shifted line: orange -30..149, blue 0..179), HSV saturation and brightness; and the share of the band the fixed
ranges paint. Tells how far a per-frame range has to move and how wide a band's own colors are.
"""
import collections
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from barrels import counting as ct  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

MODEL = hl.adopted_model()
COLS = (0.36, 0.64)


def bands(bbox):
    x0, y0, x1, y1 = bbox
    w, h = x1 - x0, y1 - y0
    up = (0.27, 0.37) if h < 45 else (0.30, 0.40) if h < 80 else (0.34, 0.44)
    cx0, cx1 = int(round(x0 + COLS[0] * w)), max(int(round(x0 + COLS[1] * w)), int(round(x0 + COLS[0] * w)) + 1)

    def rect(a, b):
        r0 = int(round(y0 + a * h))
        return (cx0, r0, cx1, max(int(round(y0 + b * h)), r0 + 1))
    return {"upper": rect(*up), "stripe": rect(0.51, 0.61), "lower": rect(0.75, 0.90)}


def stats(frame, rects, cls):
    hs = frame.hs(pl.HUE_SHIFT[cls])
    px, v = [], []
    for x0, y0, x1, y1 in rects:
        px.append(hs[y0:y1, x0:x1].reshape(-1, 2))
        v.append(frame.val[y0:y1, x0:x1].ravel())
    px, v = np.concatenate(px), np.concatenate(v)
    hue = np.where(px[:, 0] > 105 + pl.HUE_SHIFT[cls], px[:, 0] - 180, px[:, 0]) - pl.HUE_SHIFT[cls] if cls == ORANGE else px[:, 0]
    box = MODEL.boxes[cls]
    inside = (px[:, 0] >= box.lo[0]) & (px[:, 0] <= box.hi[0]) & (px[:, 1] >= box.lo[1]) & (v >= 40)
    q = lambda a: [float(np.percentile(a, p)) for p in (5, 50, 95)]  # noqa: E731
    return q(hue), q(px[:, 1]), q(v), float(inside.mean())


fr = jg.train_frames()
stems = fr["ordinary"] + fr["extreme"]
truth = jg.load_truth(stems)
agg = collections.defaultdict(list)
for s in stems:
    f = jg.load_frame(s)
    for g in truth.gts[s]:
        if g.flags:
            continue
        b = bands(g.bbox)
        other = BLUE if g.color == ORANGE else ORANGE
        agg[(ct.condition_of(s), "orange" if g.color == ORANGE else "blue", "body")].append(stats(f, [b["upper"], b["lower"]], g.color))
        agg[(ct.condition_of(s), "orange" if other == ORANGE else "blue", "stripe")].append(stats(f, [b["stripe"]], other))
print("condition                paint  role    n | hue p5 p50 p95 (min p5 .. max p95) | S p5 p50 p95 (min p5) | V p5 p50 p95 | painted by the fixed range (median, min)")
for (c, col, role), rows in sorted(agg.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
    h = np.array([r[0] for r in rows]); sa = np.array([r[1] for r in rows]); v = np.array([r[2] for r in rows]); p = np.array([r[3] for r in rows])
    m = lambda a: np.median(a, axis=0)  # noqa: E731
    print(f"{c:24s} {col:6s} {role:6s} {len(rows):2d} | {m(h)[0]:5.0f} {m(h)[1]:4.0f} {m(h)[2]:4.0f} ({h[:, 0].min():4.0f} .. {h[:, 2].max():4.0f}) | "
          f"{m(sa)[0]:4.0f} {m(sa)[1]:4.0f} {m(sa)[2]:4.0f} ({sa[:, 0].min():4.0f}) | {m(v)[0]:4.0f} {m(v)[1]:4.0f} {m(v)[2]:4.0f} | {np.median(p):.2f} {p.min():.2f}")
