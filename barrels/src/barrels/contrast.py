"""The stripe by color DIFFERENCE, then the barrel's own colors (2026-11-26, experiment C4; imported by nothing
that runs by default; plan and results: ``experiments/2026-11-26_contrast``).

The fixed color step asks of every pixel "is this the home orange, is this the home blue". Under another light the
answer is no for one of a barrel's two colors, and the detector, which needs both, drops the barrel. This module asks
a question that the light mostly cancels out of: **is this band bluer (or redder) than what is right above it AND
right below it, by a margin, at the size its row predicts?**

In the order the data flows:

1. ``channel``: red against blue, per pixel, without brightness: ``log((R + o) / (B + o))`` ("logrb") or
   ``(R - B) / (R + G + B + o)`` ("opp"). A change of light adds roughly a constant to the first one everywhere, and
   a difference between two bands removes a constant.
2. ``row_bands``: for every image row taken as the middle of a stripe, the camera model gives the barrel that would
   stand there: its stripe's rows, the body's rows above and below, its top, bottom and width (``geometry.py``).
3. ``band_means``: per pixel, the mean of the channel over the stripe band, the upper body band and the lower body
   band in its own column (running sums; dark and clipped pixels are left out, never changed).
4. ``sandwich``: per pixel, the smaller of (upper - stripe) and (lower - stripe) when both have the same sign, else
   0. Positive: the band is bluer than both neighbours (an ORANGE barrel's blue stripe). Negative: redder (a BLUE
   barrel's orange stripe).
5. ``find``: a candidate is a place where at least ``width_share`` of the predicted width passes the margin with one
   sign. The strongest first; a weaker one whose stripe point lies in a stronger one's predicted box is dropped (a
   barrel's own body bands are "sandwiches" of the other sign: lid or table, body, stripe).
6. ``measure``: for one candidate, THAT barrel's own two colors, read from its stripe band and its two body bands,
   and what is around its predicted box (left, right, above, below).
7. ``paint``: inside the predicted box only, a pixel is body when it is nearer to this barrel's body color than to
   its stripe color and than to anything around the box, and stripe likewise (stripe only near the stripe's rows).

No pixel is ever changed: every step compares one part of the picture with another. Nothing is learned; the numbers
are the fields of ``Params``.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from . import geometry as geo
from .io import BLUE, ORANGE, OTHER

_MID_Z = geo.BARREL_HEIGHT_MM / 2
_BULGE_R = geo.BARREL_BULGE_DIAMETER_MM / 2


@dataclass(frozen=True)
class Params:
    # the channel
    channel: str = "logrb"          # "logrb": log((R + o) / (B + o));  "opp": (R - B) / (R + G + B + o)
    offset: float = 8.0             # o: keeps the ratio of two nearly black values from being noise
    v_min: int = 25                 # a pixel whose brightest channel is below this is left out of every band mean
    clip: int = 250                 # ... and one with any channel at or above this (glare): its ratio means nothing
    band_valid: float = 0.5         # a band mean counts when at least this share of its pixels were usable
    # the bands, in units of the stripe height the row predicts
    core: float = 0.6               # the stripe band = the middle ``core`` of the predicted stripe rows
    gap: float = 0.25               # the body bands start this far beyond the predicted stripe edge ...
    body: float = 0.9               # ... and are this tall (the side wall above / below the stripe is about 1.5)
    # the candidate
    margin: float = 0.5             # both body bands differ from the stripe band by more than this, same sign
    width_share: float = 0.5        # ... in at least this share of the columns of the counting window
    window: float = 0.8             # the counting window = this share of the predicted barrel width, centred
    min_stripe_px: float = 4.0      # rows whose predicted stripe is thinner are not searched (the detector's own floor)
    min_width_px: float = 16.0      # ... nor rows whose predicted barrel is narrower (beyond the table)
    top_row: int = 50               # the horizon gate of the color step: no stripe point above it
    max_candidates: int = 20
    strength_min: float = 0.0       # ... and the mean size of the score over the counting window is at least this
    # the guards (None = off)
    d_min: float | None = None      # the body's and the stripe's own colors are at least this far apart (feature distance)
    alike: float | None = None      # the two body bands differ from each other by at most this (channel units)
    alike_rel: float | None = None  # ... or by at most this share of the weaker of the two differences from the stripe
    alike_feat: float | None = None  # the two body bands' own colors (color AND brightness) are at most this far apart,
    #                                  in units of the body-stripe distance: one body above and below, not two things
    orange_min: float | None = None  # the orange part (an orange barrel's body, a blue barrel's stripe) reads at least this
    extent_top: float | None = None  # what is right above the predicted top differs from the body by at least this
    #                                  (a feature distance, in units of the body-stripe distance)
    extent_bottom: float | None = None  # ... and what is right below the predicted bottom
    surround: float | None = None   # at least one side flank differs from the body by at least this (same unit)
    # the paint
    feat_offset: float = 8.0        # the own-color comparison: (log R/G, log B/G, bright * log brightness), same offset idea
    bright: float = 0.5
    box_slack: float = 0.08         # the paint box = the predicted box grown by this share of its height / width
    match: float = 0.6              # a pixel matches a color when its distance to it is under this x the body-stripe distance
    distinct: float = 0.35          # a surround sample nearer than this x the body-stripe distance to the body or the
    #                                 stripe is a neighbour (or a table of the barrel's color), not something to tell apart
    stripe_zone: float = 0.75       # stripe paint only within this many stripe heights beyond the predicted stripe rows


# ---------------------------------------------------------------- 1. the channel

def usable(rgb: np.ndarray, p: Params = Params()) -> np.ndarray:
    """Pixels bright enough and not clipped: the only ones a band mean reads."""
    v = np.asarray(rgb).max(-1)
    return (v >= p.v_min) & (v < p.clip)


def channel(rgb: np.ndarray, kind: str = "logrb", offset: float = 8.0) -> np.ndarray:
    """Red against blue per pixel, float32. ``rgb``: H x W x 3 in R, G, B order, any number type; not written to."""
    x = np.asarray(rgb, np.float32)
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    if kind == "logrb":
        return np.log((r + offset) / (b + offset))
    if kind == "opp":
        return (r - b) / (r + g + b + offset)
    raise ValueError(f"unknown channel {kind!r}")


def features(rgb: np.ndarray, offset: float = 8.0, bright: float = 0.5) -> np.ndarray:
    """H x W x 3 float32: (log R/G, log B/G, ``bright`` x log mean brightness). What "nearer to which color" is
    measured in: two numbers for the color, and a weaker one for how light it is (a dark gray body on a pale floor)."""
    x = np.asarray(rgb, np.float32) + offset
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    return np.stack([np.log(r / g), np.log(b / g), bright * np.log((r + g + b) / 3.0)], -1)


# ---------------------------------------------------------------- 2. what the row predicts

@dataclass(frozen=True)
class RowBands:
    """Per image row y taken as a stripe's middle row (arrays of length H). ``ok``: a barrel can stand there, is
    large enough to search, and the frame does not cut any of its three bands to under half. Row ranges are
    half-open and clipped to the frame."""
    ok: np.ndarray
    top: np.ndarray                 # float: the barrel's top row
    bottom: np.ndarray              # float: its bottom row
    s_top: np.ndarray               # float: the stripe's rows
    s_bot: np.ndarray
    width: np.ndarray               # float: the barrel's width, px
    s0: np.ndarray                  # int: the stripe band [s0, s1)
    s1: np.ndarray
    u0: np.ndarray                  # int: the upper body band
    u1: np.ndarray
    l0: np.ndarray                  # int: the lower body band
    l1: np.ndarray
    half: np.ndarray                # int: half the counting window, in columns

    @property
    def stripe_h(self) -> np.ndarray:
        return self.s_bot - self.s_top

    @property
    def height(self) -> np.ndarray:
        return self.bottom - self.top


def barrel_at(cam: geo.CameraModel, stripe_row: float) -> geo.BarrelRows | None:
    """The barrel whose stripe's middle is at ``stripe_row`` (None above the horizon or nearer than a barrel can be)."""
    d = cam._d_axis_from_point_row(stripe_row, _MID_Z, -_BULGE_R)
    if not math.isfinite(d) or d <= _BULGE_R + 1:
        return None
    return cam.barrel_rows(d)


def row_bands(cam: geo.CameraModel, h: int, p: Params = Params()) -> RowBands:
    f = {k: np.zeros(h, np.float64) for k in ("top", "bottom", "s_top", "s_bot", "width")}
    i = {k: np.zeros(h, np.int64) for k in ("s0", "s1", "u0", "u1", "l0", "l1", "half")}
    ok = np.zeros(h, bool)
    for y in range(max(0, p.top_row), h):
        b = barrel_at(cam, y + 0.5)
        if b is None:
            continue
        hs = b.stripe_bottom - b.stripe_top
        if hs < p.min_stripe_px or b.width_px < p.min_width_px:
            continue
        mid = (b.stripe_top + b.stripe_bottom) / 2
        s0, s1 = mid - p.core * hs / 2, mid + p.core * hs / 2
        # the body bands never leave the barrel: a close barrel is seen from above, so its wall below the stripe is
        # shorter in the picture than the stripe is tall, and the lid takes the top of the box
        u1 = b.stripe_top - p.gap * hs
        u0 = max(u1 - p.body * hs, b.top + 0.25 * (b.stripe_top - b.top))
        l0 = b.stripe_bottom + p.gap * hs
        l1 = min(l0 + p.body * hs, b.bottom - 0.1 * (b.bottom - b.stripe_bottom))
        r = [int(round(v)) for v in (s0, s1, u0, u1, l0, l1)]
        r[1] = max(r[1], r[0] + 1); r[3] = max(r[3], r[2] + 1); r[5] = max(r[5], r[4] + 1)
        want = (r[1] - r[0], r[3] - r[2], r[5] - r[4])
        c = [min(max(v, 0), h) for v in r]
        got = (c[1] - c[0], c[3] - c[2], c[5] - c[4])
        if any(g < 0.5 * w_ or g < 1 for g, w_ in zip(got, want)):
            continue                                        # the frame cuts a band: no sandwich to read here
        ok[y] = True
        f["top"][y], f["bottom"][y], f["s_top"][y], f["s_bot"][y], f["width"][y] = b.top, b.bottom, b.stripe_top, b.stripe_bottom, b.width_px
        for k, v in zip(("s0", "s1", "u0", "u1", "l0", "l1"), c):
            i[k][y] = v
        i["half"][y] = max(1, int(round(p.window * b.width_px / 2)))
    return RowBands(ok=ok, **f, **i)


# ---------------------------------------------------------------- 3. band means, 4. the sandwich

def _vsum(a: np.ndarray) -> np.ndarray:
    out = np.zeros((a.shape[0] + 1,) + a.shape[1:], np.float64)
    np.cumsum(a, axis=0, out=out[1:])
    return out


def band_means(chan: np.ndarray, good: np.ndarray, rb: RowBands, p: Params = Params()):
    """(S, U, L, valid): per pixel (y, x) the mean of ``chan`` over the usable pixels of the stripe band, the upper
    body band and the lower body band that row y predicts, in column x; ``valid`` where all three bands had at least
    ``band_valid`` of their pixels usable and the row can hold a stripe."""
    cs = _vsum(np.where(good, chan, 0.0))
    cn = _vsum(good.astype(np.float64))
    out, valid = [], np.repeat(rb.ok[:, None], chan.shape[1], axis=1)
    for a, b in ((rb.s0, rb.s1), (rb.u0, rb.u1), (rb.l0, rb.l1)):
        n = cn[b] - cn[a]
        full = np.maximum(b - a, 1)[:, None]
        out.append((cs[b] - cs[a]) / np.maximum(n, 1.0))
        valid = valid & (n >= p.band_valid * full)
    return out[0], out[1], out[2], valid


def sandwich(S: np.ndarray, U: np.ndarray, L: np.ndarray, valid: np.ndarray | None = None) -> np.ndarray:
    """The signed sandwich score: the smaller of (U - S) and (L - S) in size when they have the same sign, else 0.
    Positive = the band is bluer than both neighbours (orange barrel), negative = redder (blue barrel)."""
    du, dl = U - S, L - S
    pos = np.minimum(du, dl)
    neg = np.maximum(du, dl)
    out = np.where(pos > 0, pos, np.where(neg < 0, neg, 0.0))
    if valid is not None:
        out = np.where(valid, out, 0.0)
    return out


def _hmean(a: np.ndarray, half: np.ndarray) -> np.ndarray:
    """Per row y, the mean of ``a`` over the columns x - half[y] .. x + half[y] (clipped at the frame; the divisor
    stays the full window, so a window the frame cuts counts its missing part as "does not agree")."""
    h, w = a.shape
    cs = np.zeros((h, w + 1), np.float64)
    np.cumsum(a, axis=1, out=cs[:, 1:])
    x = np.arange(w)[None, :]
    hi = np.clip(x + half[:, None] + 1, 0, w)
    lo = np.clip(x - half[:, None], 0, w)
    return (np.take_along_axis(cs, hi, 1) - np.take_along_axis(cs, lo, 1)) / (2 * half[:, None] + 1)


# ---------------------------------------------------------------- 5. candidates

@dataclass
class Candidate:
    color: int                      # ORANGE | BLUE: the barrel (its body); the stripe is the other color
    row: int                        # the stripe's middle row
    x: int                          # ... and its middle column
    share: float                    # the share of the counting window that passes the margin
    strength: float                 # the mean size of the score over the window (what candidates are ranked by)
    box: tuple[float, float, float, float]      # the predicted barrel: x0, top, x1, bottom (floats, not clipped)
    stripe: tuple[float, float]     # the predicted stripe rows
    width: float
    info: dict = field(default_factory=dict)    # measure(): the colors read, the guards

    @property
    def stripe_color(self) -> int:
        return BLUE if self.color == ORANGE else ORANGE


@dataclass
class Response:
    """Everything ``respond`` computed, for looking at: the channel, the signed score, and per color the share map."""
    chan: np.ndarray
    good: np.ndarray
    score: np.ndarray
    share: dict
    strength: dict
    rb: RowBands
    S: np.ndarray
    U: np.ndarray
    L: np.ndarray


def respond(rgb: np.ndarray, cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT, p: Params = Params(), rb: RowBands | None = None) -> Response:
    h = rgb.shape[0]
    rb = rb or row_bands(cam, h, p)
    chan = channel(rgb, p.channel, p.offset)
    good = usable(rgb, p)
    S, U, L, valid = band_means(chan, good, rb, p)
    score = sandwich(S, U, L, valid)
    share, strength = {}, {}
    for color, sgn in ((ORANGE, 1.0), (BLUE, -1.0)):
        s = np.maximum(sgn * score, 0.0)
        share[color] = _hmean((s > p.margin).astype(np.float64), rb.half)
        strength[color] = _hmean(s, rb.half)
    return Response(chan, good, score, share, strength, rb, S, U, L)


def _inside(box, x: float, y: float) -> bool:
    x0, y0, x1, y1 = box
    return x0 <= x < x1 and y0 <= y < y1


def _recentre(passes: np.ndarray, x: int, half: int, w: float) -> int:
    """The stripe's middle column, from the run of agreeing columns of its row. ``passes``: that row, True where the
    column passes the margin. The longest run inside the counting window around ``x`` is followed to its two ends.
    A run no wider than 1.2 barrels is one stripe: its middle. A longer one is the shared stripe of touching barrels
    of one color, each ``w`` wide: the middle of the barrel-wide slot ``x`` falls in, counted from the nearer end of
    the run. The move is at most half a window."""
    n = len(passes)
    lo, hi = max(0, x - half), min(n, x + half + 1)
    seg = passes[lo:hi]
    if not seg.any():
        return x
    edges = np.flatnonzero(np.diff(np.concatenate(([0], seg.astype(np.int8), [0]))))
    starts, ends = edges[::2], edges[1::2]
    k = int(np.argmax(ends - starts))
    a, b = lo + int(starts[k]), lo + int(ends[k])
    while a > 0 and passes[a - 1]:
        a -= 1
    while b < n and passes[b]:
        b += 1
    if b - a <= 1.2 * w:
        new = (a + b - 1) / 2
    elif x - a <= b - 1 - x:
        new = a + (math.floor(max(0.0, x - a) / w) + 0.5) * w - 0.5
    else:
        new = b - (math.floor(max(0.0, b - 1 - x) / w) + 0.5) * w - 0.5
    return int(round(min(max(new, x - half), x + half)))


def _recentre_row(col: np.ndarray, y: int, reach: int, keep: float = 0.9) -> int:
    """The stripe's middle row: the middle of the run of rows around ``y`` (at most ``reach`` rows each way) whose
    strength in this column is at least ``keep`` x the strength at ``y``. The stripe band is shorter than the stripe,
    so the strength is flat over a few rows, and the first of them is not the middle."""
    t = keep * col[y]
    a = b = y
    while a > max(0, y - reach) and col[a - 1] >= t:
        a -= 1
    while b < min(len(col) - 1, y + reach) and col[b + 1] >= t:
        b += 1
    return (a + b + 1) // 2


def find(rgb: np.ndarray, cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT, p: Params = Params(), rb: RowBands | None = None,
         resp: Response | None = None, limit: int | None = None) -> list[Candidate]:
    """The candidates of one picture, the strongest first, at most ``limit`` (default ``p.max_candidates``). A
    candidate is the strongest point of its neighbourhood where ``share >= width_share`` (and the mean score over
    the window is at least ``strength_min``); a weaker candidate of
    either color whose stripe point lies inside a stronger one's predicted box (or the other way round) is dropped."""
    resp = resp or respond(rgb, cam, p, rb)
    rb = resp.rb
    limit = p.max_candidates if limit is None else limit
    pts = []
    for color in (ORANGE, BLUE):
        ys, xs = np.nonzero((resp.share[color] >= p.width_share) & (resp.strength[color] >= p.strength_min))
        if len(ys) == 0:
            continue
        st = resp.strength[color][ys, xs]
        pts.append(np.stack([st, ys.astype(np.float64), xs.astype(np.float64), np.full(len(ys), float(color))], 1))
    if not pts:
        return []
    a = np.concatenate(pts)
    a = a[np.argsort(-a[:, 0], kind="stable")]
    alive = np.ones(len(a), bool)
    out: list[Candidate] = []
    ya, xa = a[:, 1], a[:, 2]
    yi = ya.astype(np.int64)
    wj, tj, bj, hj = rb.width[yi], rb.top[yi], rb.bottom[yi], rb.height[yi]
    for i in range(len(a)):
        if not alive[i]:
            continue
        y, x, color = int(a[i, 1]), int(a[i, 2]), int(a[i, 3])
        sgn = 1.0 if color == ORANGE else -1.0
        # the middle of the stripe, not the first point of a flat top: first the row, then the column
        ny = _recentre_row(resp.strength[color][:, x], y, max(1, int(rb.stripe_h[y] / 2)))
        ny = ny if rb.ok[ny] else y
        nx = _recentre(sgn * resp.score[ny] > p.margin, x, int(rb.half[ny]), float(rb.width[ny]))
        if resp.share[color][ny, nx] >= p.width_share and resp.strength[color][ny, nx] >= 0.9 * a[i, 0]:
            y, x = ny, nx
        w = float(rb.width[y])
        box = (x + 0.5 - w / 2, float(rb.top[y]), x + 0.5 + w / 2, float(rb.bottom[y]))
        out.append(Candidate(color, y, x, float(resp.share[color][y, x]), float(resp.strength[color][y, x]), box,
                             (float(rb.s_top[y]), float(rb.s_bot[y])), w))
        if len(out) >= limit:
            break
        # drop every weaker point inside this box (grown by a quarter of a width at the sides: no second stripe can
        # have its middle there), and every weaker point whose own box holds this stripe point
        gx, gy = 0.25 * (box[2] - box[0]), 0.1 * (box[3] - box[1])
        inside = (xa >= box[0] - gx) & (xa < box[2] + gx) & (ya >= box[1] - gy) & (ya < box[3] + gy)
        holds = (np.abs(xa - x) <= 0.75 * wj) & (tj - 0.1 * hj <= y) & (y < bj + 0.1 * hj)
        alive &= ~(inside | holds)
    return out


# ---------------------------------------------------------------- 6. the barrel's own colors

def _cell(feat: np.ndarray, good: np.ndarray, x0: float, y0: float, x1: float, y1: float) -> np.ndarray | None:
    """The median feature of the usable pixels of a rectangle (None when under 4 of them are usable)."""
    h, w = good.shape
    xa, xb, ya, yb = max(0, int(round(x0))), min(w, int(round(x1))), max(0, int(round(y0))), min(h, int(round(y1)))
    if xb - xa < 1 or yb - ya < 1:
        return None
    g = good[ya:yb, xa:xb]
    if int(g.sum()) < 4:
        return None
    return np.median(feat[ya:yb, xa:xb][g], axis=0)


def measure(c: Candidate, resp: Response, feat: np.ndarray, p: Params = Params()) -> dict:
    """Read candidate ``c``'s own colors and what stands around its predicted box. Fills and returns ``c.info``:

    - ``body``, ``stripe``: the feature of the upper and lower body bands (the mean of their two medians) / the
      median of the stripe band, over the middle 60 % of the predicted width. ``upper``, ``lower``: the bands apart.
    - ``d``: the feature distance between body and stripe (the unit every "differs" below is measured in).
    - ``chan_body``, ``chan_stripe``, ``chan_upper``, ``chan_lower``: the same cells in the red-against-blue channel.
    - ``around``: the median features left of, right of, above and below the predicted box; ``off``: how far each
      is from the body, in units of ``d``.
    - ``reasons``: the guards of ``p`` this candidate fails (empty = it passes)."""
    rb, y = resp.rb, c.row
    x0, top, x1, bottom = c.box
    w = c.width
    cx0, cx1 = c.x + 0.5 - 0.3 * w, c.x + 0.5 + 0.3 * w
    good = resp.good
    cells = {"stripe": (cx0, rb.s0[y], cx1, rb.s1[y]), "upper": (cx0, rb.u0[y], cx1, rb.u1[y]), "lower": (cx0, rb.l0[y], cx1, rb.l1[y])}
    info: dict = {"reasons": []}
    for k, r in cells.items():
        info[k] = _cell(feat, good, *r)
        ch = _cell(resp.chan[..., None], good, *r)
        info["chan_" + k] = None if ch is None else float(ch[0])
    if any(info[k] is None for k in cells):
        info["reasons"].append("unreadable")
        c.info = info
        return info
    info["body"] = (info["upper"] + info["lower"]) / 2
    info["chan_body"] = (info["chan_upper"] + info["chan_lower"]) / 2
    d = float(np.linalg.norm(info["body"] - info["stripe"]))
    info["d"] = d
    hgt = bottom - top
    hs = c.stripe[1] - c.stripe[0]
    band = max(2.0, 0.6 * hs)
    info["around"] = {
        "left": _cell(feat, good, x0 - 0.45 * w, top + 0.15 * hgt, x0 - 0.12 * w, bottom - 0.1 * hgt),
        "right": _cell(feat, good, x1 + 0.12 * w, top + 0.15 * hgt, x1 + 0.45 * w, bottom - 0.1 * hgt),
        "above": _cell(feat, good, cx0, top - 0.1 * hgt - band, cx1, top - 0.1 * hgt),
        "below": _cell(feat, good, cx0, bottom + 0.1 * hgt, cx1, bottom + 0.1 * hgt + band),
    }
    info["off"] = {k: (None if a is None or d <= 0 else float(np.linalg.norm(a - info["body"])) / d) for k, a in info["around"].items()}
    cu, cl, cs = info["chan_upper"], info["chan_lower"], info["chan_stripe"]
    info["alike"] = abs(cu - cl)
    info["alike_rel"] = abs(cu - cl) / max(1e-6, min(abs(cu - cs), abs(cl - cs)))
    info["orange_part"] = info["chan_body"] if c.color == ORANGE else cs
    info["alike_feat"] = float(np.linalg.norm(info["upper"] - info["lower"])) / max(1e-6, d)
    rs = info["reasons"]
    if p.alike_feat is not None and info["alike_feat"] > p.alike_feat:
        rs.append("alike_feat")
    if d <= 0:
        rs.append("unreadable")
    if p.d_min is not None and d < p.d_min:
        rs.append("d_min")
    if p.alike is not None and info["alike"] > p.alike:
        rs.append("alike")
    if p.alike_rel is not None and info["alike_rel"] > p.alike_rel:
        rs.append("alike_rel")
    if p.orange_min is not None and info["orange_part"] < p.orange_min:
        rs.append("orange_min")
    if p.extent_top is not None and info["off"]["above"] is not None and info["off"]["above"] < p.extent_top:
        rs.append("extent_top")
    if p.extent_bottom is not None and info["off"]["below"] is not None and info["off"]["below"] < p.extent_bottom:
        rs.append("extent_bottom")
    if p.surround is not None:
        sides = [v for v in (info["off"]["left"], info["off"]["right"]) if v is not None]
        if sides and max(sides) < p.surround:
            rs.append("surround")
    c.info = info
    return info


# ---------------------------------------------------------------- 7. the paint

def paint(c: Candidate, feat: np.ndarray, good: np.ndarray, out: np.ndarray, p: Params = Params(), free: np.ndarray | None = None) -> int:
    """Paint candidate ``c`` (already ``measure``d and passing) into the class mask ``out``, inside its predicted box
    grown by ``box_slack``: a pixel becomes body when body is the nearest of (this barrel's body color, its stripe
    color, the distinct things around the box) and nearer than ``match`` x the body-stripe distance; stripe likewise,
    and only within ``stripe_zone`` stripe heights of the predicted stripe rows. Only pixels where ``free`` is True
    are written (default: where ``out`` is still OTHER). Returns the number of pixels painted."""
    info = c.info
    if info.get("reasons") or "body" not in info:
        return 0
    h, w = out.shape
    x0, top, x1, bottom = c.box
    sx, sy = p.box_slack * (x1 - x0), p.box_slack * (bottom - top)
    xa, xb = max(0, int(round(x0 - sx))), min(w, int(round(x1 + sx)))
    ya, yb = max(0, int(round(top - sy))), min(h, int(round(bottom + sy)))
    if xb - xa < 2 or yb - ya < 2:
        return 0
    d = info["d"]
    f = feat[ya:yb, xa:xb]
    refs = [info["body"], info["stripe"]]
    for a in info["around"].values():
        if a is not None and min(np.linalg.norm(a - info["body"]), np.linalg.norm(a - info["stripe"])) >= p.distinct * d:
            refs.append(a)
    dist = np.stack([np.linalg.norm(f - r, axis=-1) for r in refs], 0)
    near = dist.argmin(0)
    ok = good[ya:yb, xa:xb] & (free[ya:yb, xa:xb] if free is not None else out[ya:yb, xa:xb] == OTHER)
    body = ok & (near == 0) & (dist[0] < p.match * d)
    stripe = ok & (near == 1) & (dist[1] < p.match * d)
    hs = c.stripe[1] - c.stripe[0]
    rows = np.arange(ya, yb)[:, None]
    stripe &= (rows >= c.stripe[0] - p.stripe_zone * hs) & (rows < c.stripe[1] + p.stripe_zone * hs)
    view = out[ya:yb, xa:xb]
    view[body] = c.color
    view[stripe] = c.stripe_color
    return int(body.sum() + stripe.sum())


def contrast_mask(rgb: np.ndarray, base: np.ndarray | None = None, cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT, p: Params = Params(),
                  skip_boxes: tuple = (), rb: RowBands | None = None, resp: Response | None = None,
                  feat: np.ndarray | None = None, cands: list[Candidate] | None = None) -> tuple[np.ndarray, list[Candidate]]:
    """The class mask with the contrast path's paint added. ``base``: the fixed model's mask (kept as it is; only
    pixels it left OTHER are painted), or None for the contrast path alone. ``skip_boxes``: boxes (x0, y0, x1, y1)
    of barrels already found; a candidate whose stripe point lies in one is left alone. Returns (mask, candidates);
    each candidate's ``info["painted"]`` says how many pixels it got (0 = a guard refused it, see ``reasons``).
    ``resp``, ``feat``, ``cands``: what ``respond``, ``features`` and ``find`` gave for this picture and these
    ``p``, when the caller has them already (the guards and the paint are then the only work)."""
    h, w = rgb.shape[:2]
    out = np.zeros((h, w), np.uint8) if base is None else base.copy()
    free = out == OTHER
    resp = resp or respond(rgb, cam, p, rb)
    cands = find(rgb, cam, p, resp=resp) if cands is None else cands
    feat = features(rgb, p.feat_offset, p.bright) if feat is None else feat
    for c in cands:
        if any(_inside(b, c.x, c.row) for b in skip_boxes):
            c.info = {"reasons": ["found_already"], "painted": 0}
            continue
        measure(c, resp, feat, p)
        c.info["painted"] = paint(c, feat, resp.good, out, p, free)
    return out, cands
