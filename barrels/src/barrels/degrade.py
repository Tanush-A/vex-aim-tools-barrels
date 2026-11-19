"""Damage a good class mask the way real segmentation damages it (2026-11-18, TODO item A).

Used only by the test "if the segmentation is good, the detector finds the barrel"
(``experiments/2026-11-18_det_given_seg``): a hand-made mask goes in, the same mask with seeded, measured damage
comes out, and the detector is scored on it. Nothing here is part of the detector or the color model.

Every amount is a plain number relative to the barrel's hand-drawn box (W wide, H tall), so "medium damage" means
the same thing for a near barrel and a far one. Six fields, applied in this order:

1. ``top_highlight`` (w, h)   a pale patch on the upper body, as a window or a lamp makes: an ellipse w x W wide
   and h x H tall, centred a fifth of the way down the box and up to 0.15 W left or right of its middle, set to
   "not barrel".
2. ``stripe_highlight`` w     a pale patch across the stripe: an ellipse w x W wide and a third of H tall, centred
   on the middle row of the box, anywhere along the width.
3. ``stripe_breaks`` (n, w)   the stripe in pieces: n vertical slits, each w x W wide (at least 1 px), through the
   middle half of the box's rows.
4. ``erode_px`` e             eaten edges: every color loses e pixels all around (so the seam between body and
   stripe opens by 2e pixels, as mixed pixels do).
5. ``dropout`` p              every barrel pixel is lost with probability p.
6. ``speckle`` n              n specks of barrel color (2 or 3 px squares, random color) on the table: below the
   color gate row, at least 4 px outside every box.

``SEVERITIES`` names three made-up levels; ``SINGLE`` has one kind at a time; ``REALISTIC`` and ``WORST_SEEN``
are levels measured on real white-table segmentation (2026-11-19), under their own names. ``damage(mask, boxes, d, seed)`` is a pure
function of its arguments.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import cv2
import numpy as np

from .io import BLUE, ORANGE

GATE_ROW = 50          # the color model labels nothing above this row (the pipeline's horizon gate)
SPECK_PAD = 4          # specks stay this many px outside every box


@dataclass(frozen=True)
class Damage:
    top_highlight: tuple[float, float] = (0.0, 0.0)   # ellipse (width / W, height / H) on the upper body
    stripe_highlight: float = 0.0                     # ellipse width / W across the stripe (height H / 3)
    stripe_breaks: tuple[int, float] = (0, 0.0)       # (how many slits, slit width / W)
    erode_px: int = 0                                 # pixels eaten off every edge of every color
    dropout: float = 0.0                              # share of barrel pixels lost at random
    speckle: int = 0                                  # specks of barrel color on the table, per frame

    def to_dict(self) -> dict:
        return asdict(self)


SEVERITIES = {
    "light": Damage(top_highlight=(0.3, 0.2), erode_px=1, dropout=0.02, speckle=5),
    "medium": Damage(top_highlight=(0.5, 0.3), stripe_highlight=0.15, stripe_breaks=(1, 0.06), erode_px=1, dropout=0.05, speckle=15),
    "heavy": Damage(top_highlight=(0.7, 0.4), stripe_highlight=0.3, stripe_breaks=(2, 0.08), erode_px=2, dropout=0.10, speckle=30),
}
# Levels MEASURED on real segmentation (2026-11-19, experiments/2026-11-19_damage_realism; results/.../measured.md).
# Separate from SEVERITIES on purpose: the three made-up levels and every earlier result stay as they are.
# The two of REALISTIC follow a rule fixed before the measurement: every field is the median ("typical") or the
# 90th percentile ("bad day") over the free-standing barrels of the HOME train frames, segmented as the eval table
# does and compared with the hand-made masks. "Bad day" puts the 90th percentile of every kind on every barrel at
# once, so it is harsher than a 90th-percentile barrel.
REALISTIC = {
    "white tables, typical": Damage(erode_px=1, speckle=6),
    "white tables, bad day": Damage(top_highlight=(0.16, 0.09), stripe_highlight=0.06, erode_px=1, dropout=0.005, speckle=20),
}
# Not from the rule (added after the measurement, report only): the worst single barrel or frame seen on HOME or
# CAMPUS for each kind, all at once on every barrel. No real barrel looks like this; it bounds the white tables.
WORST_SEEN = {
    "white tables, worst seen": Damage(top_highlight=(0.41, 0.30), stripe_highlight=0.40, stripe_breaks=(1, 0.03), erode_px=1, dropout=0.014, speckle=37),
}
LEVELS = {**SEVERITIES, **REALISTIC, **WORST_SEEN}      # every named level, by name
# one kind at a time: which damage is the one that hurts
SINGLE = {
    "top highlight 0.5 x 0.3": Damage(top_highlight=(0.5, 0.3)),
    "top highlight 0.7 x 0.4": Damage(top_highlight=(0.7, 0.4)),
    "stripe highlight 0.15": Damage(stripe_highlight=0.15),
    "stripe highlight 0.3": Damage(stripe_highlight=0.3),
    "stripe breaks 2 x 0.08": Damage(stripe_breaks=(2, 0.08)),
    "edges 1 px": Damage(erode_px=1),
    "edges 2 px": Damage(erode_px=2),
    "dropout 10 %": Damage(dropout=0.10),
    "speckle 30": Damage(speckle=30),
}


def _ellipse(shape, cx: float, cy: float, w: float, h: float) -> np.ndarray:
    m = np.zeros(shape, np.uint8)
    if w >= 1 and h >= 1:
        cv2.ellipse(m, (int(round(cx)), int(round(cy))), (max(1, int(round(w / 2))), max(1, int(round(h / 2)))), 0, 0, 360, 1, -1)
    return m.astype(bool)


def damage(mask: np.ndarray, boxes: list[tuple[int, int, int, int]], d: Damage, seed: int = 0) -> np.ndarray:
    """``mask`` (0 other / 1 orange / 2 blue) with the damage ``d`` applied around every box of ``boxes``
    (x0, y0, x1, y1, half-open). Same arguments, same result. Damage only ever removes barrel pixels, except
    the specks, which are added outside the boxes."""
    rng = np.random.default_rng(seed)
    out = mask.copy()
    h, w = out.shape
    barrel = np.isin(out, (ORANGE, BLUE))
    for x0, y0, x1, y1 in boxes:
        W, H = x1 - x0, y1 - y0
        cx = (x0 + x1) / 2
        tw, th = d.top_highlight
        if tw > 0 and th > 0:
            out[_ellipse(out.shape, cx + rng.uniform(-0.15, 0.15) * W, y0 + 0.2 * H, tw * W, th * H) & barrel] = 0
        if d.stripe_highlight > 0:
            sw = d.stripe_highlight * W
            out[_ellipse(out.shape, rng.uniform(x0 + sw / 2, max(x0 + sw / 2, x1 - sw / 2)), (y0 + y1) / 2, sw, H / 3) & barrel] = 0
        n, bw = d.stripe_breaks
        for _ in range(n):
            px = max(1, int(round(bw * W)))
            c = int(rng.integers(x0, max(x0 + 1, x1 - px)))
            ya, yb = int(round(y0 + 0.25 * H)), int(round(y0 + 0.75 * H))
            sl = out[max(0, ya):min(h, yb), max(0, c):min(w, c + px)]
            sl[np.isin(sl, (ORANGE, BLUE))] = 0
    if d.erode_px > 0:
        k = np.ones((3, 3), np.uint8)
        for c in (ORANGE, BLUE):
            # the frame edge is not an edge of the barrel: replicate the border before eroding
            kept = cv2.erode((out == c).astype(np.uint8), k, iterations=d.erode_px, borderType=cv2.BORDER_REPLICATE).astype(bool)
            out[(out == c) & ~kept] = 0
    if d.dropout > 0:
        out[np.isin(out, (ORANGE, BLUE)) & (rng.random(out.shape) < d.dropout)] = 0
    if d.speckle > 0:
        free = ~barrel
        free[:GATE_ROW] = False
        for x0, y0, x1, y1 in boxes:
            free[max(0, y0 - SPECK_PAD):max(0, y1 + SPECK_PAD), max(0, x0 - SPECK_PAD):max(0, x1 + SPECK_PAD)] = False
        ys, xs = np.where(free)
        if len(ys):
            for i in rng.integers(0, len(ys), d.speckle):
                s = int(rng.integers(2, 4))
                y, x = int(ys[i]), int(xs[i])
                out[y:y + s, x:x + s][free[y:y + s, x:x + s]] = ORANGE if rng.random() < 0.5 else BLUE
    return out
