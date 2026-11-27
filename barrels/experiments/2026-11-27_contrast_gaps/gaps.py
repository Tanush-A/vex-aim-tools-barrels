"""Three small additions to the stripe by contrast, for the frames where the vendor still finds more (plan: PREREG.md).

Every addition runs AFTER today's default (``pipeline.detect_frame``: the color step, the detector, the stripe by
contrast) and only adds to its answer; with every addition off, ``detect`` gives exactly today's boxes (the test in
``check.py``). Nothing here is called by anything that runs by default. No pixel is changed; nothing is carried
between frames.

1. ``edge`` (a barrel cut by the side of the frame). Today the counting window of a candidate counts the part of it
   outside the frame as "does not agree", so a barrel half outside the frame can never reach half of the window or the
   strength floor. Here the window is the part INSIDE the frame, when at least ``edge`` of the window is inside. Only a
   candidate whose window the frame cuts is new; everything else reads exactly as today.
2. ``half`` (a close-up whose stripe is at the bottom of the frame). Today a row is searched only when all three
   bands (body above, stripe, body below) are at least half inside the frame. Here, for the rows where only the body
   band BELOW is cut by the bottom of the frame, the band is compared with the body above it alone ("a half
   sandwich"), at the size the row predicts, and the strength floor is ``half``. Measured and painted as a whole
   candidate is (the lower band is read as the upper one; nothing below the frame is checked).
3. ``split`` (touching barrels of one color). A box the detector drew on the fixed colors that is wider than
   ``split`` x the width its top row predicts is two barrels in one box. When the detector's run on the painted mask
   has two or more boxes of that color on it, each no wider than ``split`` x its own width, they replace it.

The candidates of 1 and 2 are measured (``contrast.measure``: the orange part reddish at all, the barrel ends where
its row says) and painted (``contrast.paint``) exactly as today's candidates are, into the mask today's contrast stage
painted, only where nothing is painted yet; the detector runs again on that mask, and a box of that run is added when
it is on no box of today's answer.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
sys.path.insert(0, str(BARRELS / "src"))

from barrels import contrast as cn  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import pipeline as pl  # noqa: E402
from barrels.io import BLUE, ORANGE, OTHER  # noqa: E402

assert str(Path(cn.__file__).resolve()).startswith(str(BARRELS)), f"barrels is imported from {cn.__file__}, not from this checkout"

CAM = geo.AIM_4A8B6118_BOXFIT
CFG = cn.ContrastConfig()
DCFG = det.DetConfig()
_MODEL = None
SAME_SIZE = 1.25        # the other-color rule: two boxes are one barrel read twice only when their heights are this close
TIE = 0.25              # ... and the stripe pattern decides between them unless its two readings are closer than this


def model():
    global _MODEL
    if _MODEL is None:
        _MODEL = pl.default_model()
    return _MODEL


@dataclass(frozen=True)
class Gaps:
    edge: float | None = None       # the share of the counting window that must be inside the frame (None = off)
    half: float | None = None       # the strength floor of a half sandwich at the bottom of the frame (None = off)
    split: float | None = None      # a first-run box wider than this x its predicted width may be split (None = off)
    other: float | None = None      # two boxes of different colors overlapping by more than this share of the smaller, at least one
    #                                 added by contrast, about the same height: the added one is dropped when the stripe pattern (or, on a near tie, the fixed
    #                                 colors) supports the other box's color better (None = off)
    beside: float | None = None     # the strength floor of a candidate at a found barrel's stripe row, right beside it (None = off)

    @property
    def key(self) -> str:
        g = lambda v: "-" if v is None else f"{v:g}"      # noqa: E731
        return f"e{g(self.edge)}|h{g(self.half)}|s{g(self.split)}|b{g(self.beside)}|o{g(self.other)}"

    def describe(self) -> str:
        parts = []
        if self.edge is not None:
            parts.append(f"edge (window counted inside the frame, >= {self.edge:g} of it inside)")
        if self.half is not None:
            parts.append(f"half sandwich at the frame bottom (strength >= {self.half:g})")
        if self.split is not None:
            parts.append(f"split a box wider than {self.split:g} W")
        if self.other is not None:
            parts.append(f"drop an added box overlapping a box of the other color by over {self.other:g}")
        if self.beside is not None:
            parts.append(f"beside a found barrel at its row (strength >= {self.beside:g})")
        return "today's default" + ("" if not parts else " plus " + ", ".join(parts))


# ---------------------------------------------------------------- 1. the window inside the frame

def _hmean_in(a: np.ndarray, half: np.ndarray, keep: float) -> np.ndarray:
    """As ``contrast._hmean``, but the divisor is the part of the window inside the frame; 0 where under ``keep`` of
    the window is inside."""
    h, w = a.shape
    cs = np.zeros((h, w + 1), np.float64)
    np.cumsum(a, axis=1, out=cs[:, 1:])
    x = np.arange(w)[None, :]
    hi = np.clip(x + half[:, None] + 1, 0, w)
    lo = np.clip(x - half[:, None], 0, w)
    n = (hi - lo).astype(np.float64)
    full = (2 * half[:, None] + 1).astype(np.float64)
    m = (np.take_along_axis(cs, hi, 1) - np.take_along_axis(cs, lo, 1)) / np.maximum(n, 1.0)
    return np.where(n >= keep * full, m, 0.0)


def edge_response(resp: cn.Response, keep: float, cfg: cn.ContrastConfig = CFG) -> cn.Response:
    share, strength = {}, {}
    for color, sgn in ((ORANGE, 1.0), (BLUE, -1.0)):
        s = np.maximum(sgn * resp.score, 0.0)
        share[color] = _hmean_in((s > cfg.margin).astype(np.float64), resp.rb.half, keep)
        strength[color] = _hmean_in(s, resp.rb.half, keep)
    return replace(resp, share=share, strength=strength)


def window_cut(c: cn.Candidate, rb: cn.RowBands, w: int) -> bool:
    hw = int(rb.half[c.row])
    return c.x - hw < 0 or c.x + hw >= w


# ---------------------------------------------------------------- 2. the half sandwich at the frame bottom

@lru_cache(maxsize=4)
def half_bands(cam: geo.CameraModel, h: int, cfg: cn.ContrastConfig = CFG) -> cn.RowBands:
    """The rows today's ``row_bands`` leaves out because the frame's BOTTOM cuts the lower body band to under half,
    while the stripe band and the upper body band are at least half inside. Their lower band is the upper band (so the
    sandwich is the one difference, U - S, and ``measure`` reads the body from above the stripe only)."""
    f = {k: np.zeros(h, np.float64) for k in ("top", "bottom", "s_top", "s_bot", "width")}
    i = {k: np.zeros(h, np.int64) for k in ("s0", "s1", "u0", "u1", "l0", "l1", "half")}
    ok = np.zeros(h, bool)
    for y in range(max(0, cfg.top_row), h):
        b = cn.barrel_at(cam, y + 0.5)
        if b is None:
            continue
        hs = b.stripe_bottom - b.stripe_top
        if hs < cfg.min_stripe_px or b.width_px < cfg.min_width_px:
            continue
        mid = (b.stripe_top + b.stripe_bottom) / 2
        s0, s1 = mid - cfg.core * hs / 2, mid + cfg.core * hs / 2
        u1 = b.stripe_top - cfg.gap * hs
        u0 = max(u1 - cfg.body * hs, b.top + 0.25 * (b.stripe_top - b.top))
        l0 = b.stripe_bottom + cfg.gap * hs
        l1 = min(l0 + cfg.body * hs, b.bottom - 0.1 * (b.bottom - b.stripe_bottom))
        r = [int(round(v)) for v in (s0, s1, u0, u1, l0, l1)]
        r[1] = max(r[1], r[0] + 1); r[3] = max(r[3], r[2] + 1); r[5] = max(r[5], r[4] + 1)
        want = (r[1] - r[0], r[3] - r[2], r[5] - r[4])
        c = [min(max(v, 0), h) for v in r]
        got = (c[1] - c[0], c[3] - c[2], c[5] - c[4])
        full = all(g >= 0.5 * w_ and g >= 1 for g, w_ in zip(got, want))
        top_two = all(g >= 0.5 * w_ and g >= 1 for g, w_ in zip(got[:2], want[:2]))
        if full or not top_two or r[5] <= h:            # today's rows, or a band cut by something else than the bottom
            continue
        ok[y] = True
        f["top"][y], f["bottom"][y], f["s_top"][y], f["s_bot"][y], f["width"][y] = b.top, b.bottom, b.stripe_top, b.stripe_bottom, b.width_px
        for k, v in zip(("s0", "s1", "u0", "u1", "l0", "l1"), (c[0], c[1], c[2], c[3], c[2], c[3])):
            i[k][y] = v
        i["half"][y] = max(1, int(round(cfg.window * b.width_px / 2)))
    for a in (*f.values(), *i.values(), ok):
        a.setflags(write=False)
    return cn.RowBands(ok=ok, **f, **i)


# ---------------------------------------------------------------- 3. the width a box's top row predicts

def rows_of_top(top_row: float, cam: geo.CameraModel = CAM):
    d = cam._d_axis_from_point_row(top_row, geo.BARREL_HEIGHT_MM, geo._END_R)
    if not math.isfinite(d) or d <= 0:
        return None
    return cam.barrel_rows(d)


def width_of_top(top_row: float, cam: geo.CameraModel = CAM) -> float:
    r = rows_of_top(top_row, cam)
    return math.inf if r is None else r.width_px


def beside(c: cn.Candidate, box, cam: geo.CameraModel = CAM) -> bool:
    """The candidate's stripe point is on the stripe row of a found barrel (within half a stripe height of the row the
    box's top predicts) and its predicted box touches that barrel's box (centres at most 1.25 widths apart), outside it."""
    r = rows_of_top(box[1], cam)
    if r is None:
        return False
    hs = r.stripe_bottom - r.stripe_top
    mid = (r.stripe_top + r.stripe_bottom) / 2
    cx = (box[0] + box[2]) / 2
    return abs(c.row + 0.5 - mid) <= max(2.0, 0.5 * hs) and abs(c.x + 0.5 - cx) <= 1.25 * max(c.width, r.width_px) \
        and not (box[0] <= c.x < box[2])


# ---------------------------------------------------------------- the detector

@dataclass
class Trace:
    """What one frame did, for looking at (``detect(..., trace=Trace())``)."""
    base_mask: np.ndarray | None = None
    painted: np.ndarray | None = None       # today's contrast paint
    painted2: np.ndarray | None = None      # plus the extra candidates' paint
    cands: list | None = None               # today's candidates
    extra: list | None = None               # (kind, candidate)
    added: list | None = None
    split: list | None = None
    dropped: list | None = None


def _inside(box, x, y) -> bool:
    return box[0] <= x < box[2] and box[1] <= y < box[3]


def detect(frame, g: Gaps = Gaps(), trace: Trace | None = None) -> list:
    rgb = frame.rgb
    h, w = rgb.shape[:2]
    mask = pl.segment(frame, model())[0]
    b1 = det.detect(mask, DCFG, CAM)
    painted, cands = cn.contrast_mask(rgb, mask, CAM, CFG, skip_boxes=tuple(b.bbox for b in b1))
    run2 = b1
    out = list(b1)
    if any(c.info.get("painted") for c in cands):
        run2 = det.detect(painted, DCFG, CAM)
        out += [replace(b, source=cn.SOURCE) for b in run2 if not any(ct.is_on(b, o) for o in b1)]
    out = sorted(out, key=lambda b: b.bbox[0])                  # == pipeline.detect_frame(frame)
    if trace is not None:
        trace.base_mask, trace.painted, trace.cands, trace.extra, trace.added, trace.split = mask, painted, cands, [], [], []
    if g.edge is None and g.half is None and g.split is None and g.beside is None and g.other is None:
        return out
    # extra candidates: not inside a box of today's answer, nor in the predicted box of one of today's candidates
    extra: list[tuple[str, cn.Candidate]] = []
    resp = None
    if g.edge is not None:
        resp = cn.respond(rgb, CAM, CFG)
        er = edge_response(resp, g.edge)
        for c in cn.find(rgb, CAM, CFG, resp=er):
            if window_cut(c, er.rb, w):
                extra.append(("edge", c))
    if g.beside is not None:
        resp = resp if resp is not None else cn.respond(rgb, CAM, CFG)
        bcfg = replace(CFG, strength_min=g.beside)
        weak = [c for c in cn.find(rgb, CAM, bcfg, resp=resp) if c.strength < CFG.strength_min]
        anchors = [b.bbox for b in out]
        grew = True
        while grew:                                     # a chain: beside a found barrel, or beside one taken here
            grew = False
            for c in weak:
                if any(c is k for _, k in extra) or not any(beside(c, a) for a in anchors):
                    continue
                extra.append(("beside", c))
                anchors.append(c.box)
                grew = True
    if g.half is not None:
        hcfg = replace(CFG, strength_min=g.half)
        hresp = cn.respond(rgb, CAM, hcfg, rb=half_bands(CAM, h))
        for c in cn.find(rgb, CAM, hcfg, resp=hresp):
            extra.append(("half", c))
    else:
        hresp = None
    final = run2
    painted2 = painted
    keep = []
    for kind, c in extra:
        if any(_inside(b.bbox, c.x, c.row) for b in out) or any(_inside(k.box, c.x, c.row) for k in cands) \
                or any(_inside(k.box, c.x, c.row) for _, k in keep):
            continue
        keep.append((kind, c))
    if keep:
        painted2 = painted.copy()
        free = painted2 == OTHER
        feat = cn.features(rgb, CFG.feat_offset, CFG.bright)
        for kind, c in keep:
            r = hresp if kind == "half" else (resp if resp is not None else cn.respond(rgb, CAM, CFG))
            cn.measure(c, r, feat, CFG)
            c.info["painted"] = cn.paint(c, feat, r.good, painted2, CFG, free)
        if any(c.info.get("painted") for _, c in keep):
            final = det.detect(painted2, DCFG, CAM)
            new = []
            for b in final:
                if any(ct.is_on(b, o) for o in out):
                    continue
                kinds = [k for k, c in keep if c.info.get("painted") and _inside(b.bbox, c.x, c.row)]
                new.append(replace(b, source="contrast_" + (kinds[0] if kinds else "extra")))
            out += new
            if trace is not None:
                trace.added += new
    if trace is not None:
        trace.extra, trace.painted2 = keep, painted2
    if g.split is not None and final is not b1:
        for o in [b for b in out if b in b1]:
            if o.width <= g.split * width_of_top(o.bbox[1]):
                continue
            ns = [n for n in final if n.color == o.color and ct.is_on(n, o) and n.width <= g.split * width_of_top(n.bbox[1])]
            ns = [n for n in ns if not any(ct.is_on(n, p) for p in out if p is not o)]
            if len(ns) >= 2:
                out = [p for p in out if p is not o] + [replace(n, source="contrast_split") for n in ns]
                if trace is not None:
                    trace.split.append((o, ns))
    if g.other is not None:
        resp = resp if resp is not None else cn.respond(rgb, CAM, CFG)
        added = lambda b: b.source.startswith(cn.SOURCE) and b.source != "contrast_split"      # noqa: E731
        drop = []
        for b in out:
            if not added(b):
                continue
            for o in out:
                if o is b or o.color == b.color or overlap_of_smaller(b.bbox, o.bbox) <= g.other:
                    continue
                if not (1 / SAME_SIZE <= b.height / o.height <= SAME_SIZE):
                    continue                            # a barrel in front of another one: both can be real
                pb, po = pattern_support(resp, b), pattern_support(resp, o)
                if abs(pb - po) >= TIE:
                    worse = pb < po                     # the stripe pattern decides
                else:
                    worse = color_support(mask, b) < color_support(mask, o)     # a near tie: the fixed colors decide
                if worse:
                    drop.append(b)
                    break
        out = [b for b in out if not any(b is d for d in drop)]
        if trace is not None:
            trace.dropped = drop
    return sorted(out, key=lambda b: b.bbox[0])


def inside_share(a, b) -> float:
    """The share of box ``a``'s area that lies inside box ``b``."""
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    area = (a[2] - a[0]) * (a[3] - a[1])
    return 0.0 if w <= 0 or h <= 0 or area <= 0 else w * h / area


def color_support(mask: np.ndarray, b) -> float:
    """How well the class mask supports box ``b`` being a barrel of ITS color: (pixels of its color - pixels of the
    other color) / the box's area, in the mask the detector saw (the fixed colors plus the contrast paint). A barrel's
    body is about three quarters of it and its stripe one quarter, so a box on a barrel of its color reads positive,
    and a box of the wrong color on the same barrel (its "body" the real stripe and lid) reads negative."""
    x0, y0, x1, y1 = b.bbox
    m = mask[max(0, y0):y1, max(0, x0):x1]
    if m.size == 0:
        return 0.0
    own = int((m == b.color).sum())
    oth = int((m == (BLUE if b.color == ORANGE else ORANGE)).sum())
    return (own - oth) / m.size


def pattern_support(resp: cn.Response, b, cam: geo.CameraModel = CAM) -> float:
    """How well the picture supports box ``b`` being a barrel of ITS color: the barrel the box's bottom row puts there
    has its stripe band bluer (orange barrel) or redder (blue barrel) than both body bands; the signed sandwich score
    of contrast at that barrel's stripe row, over the middle 40 % of the box's columns (3 rows), in the box's sign.
    0 when the row cannot be read (a band cut by the frame)."""
    d = cam._d_axis_from_point_row(b.bbox[3] - 0.5, 0.0, -geo._END_R)
    if not math.isfinite(d) or d <= 0:
        return 0.0
    r = cam.barrel_rows(d)
    y = int(round((r.stripe_top + r.stripe_bottom) / 2 - 0.5))
    h, w = resp.score.shape
    x0, x1 = b.bbox[0], b.bbox[2]
    xa, xb = max(0, int(x0 + 0.3 * (x1 - x0))), min(w, int(math.ceil(x1 - 0.3 * (x1 - x0))))
    ys = [v for v in (y - 1, y, y + 1) if 0 <= v < h and resp.rb.ok[v]]
    if not ys or xb <= xa:
        return 0.0
    sgn = 1.0 if b.color == ORANGE else -1.0
    return float(sgn * resp.score[ys, xa:xb].mean())


def overlap_of_smaller(a, b) -> float:
    """The share of the smaller box's area that lies inside the other box."""
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    small = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
    return 0.0 if w <= 0 or h <= 0 or small <= 0 else w * h / small


def detector_of(g: Gaps):
    def detect_frame(stem: str, frame) -> list:
        return detect(frame, g)
    detect_frame.describe = g.describe()
    return detect_frame
