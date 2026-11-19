"""A second opinion on the class mask: stencil matching (2026-11-20, experiments/2026-11-20_stencil).

NOT the detector. ``detector.py`` is the detector; nothing here is called by it or by the live view. This module
asks one question of the same class mask, in one way, and the experiment measures the answer against the rules.
Plain-English walkthrough in the order the data flows: results/2026-11-20_stencil/method.md.

The idea. The camera is fixed, so a barrel standing at a given distance has a known size AND known rows in the
picture; and in the class mask a barrel has a known look: body color, a band of the other color, body color again.
So for every distance (a list of ``Stencil``s, one per size, 5 % apart) a stencil is made: a barrel-shaped cut-out
with three bands (upper body ``U``, stripe ``S``, lower body ``L``) and a thin ring just outside it (``HALO``). Its
rows are fixed by the distance; only its column is free. The stencil is slid along its rows (and a few rows up and
down, because the camera constants are a few pixels off), for an orange barrel and for a blue one, and every place
gets ONE score:

    score = seen  -  absent_cost x missing  -  outside_cost x outside

computed column by column of the stencil:

  * a column is worth what its WORST band shows: q = min over its bands of (pixels painted the predicted color /
    pixels of the band), a band counting as fully there from the share ``band_full`` on. A column counts only as far
    as it shows the whole pattern, body / stripe / body, top to bottom; a stripe with nothing above it is worth
    nothing. This is what makes half of an orange thing not a barrel.
  * a band of a column that is known to be hidden is not asked for: it is outside the frame, or inside the box of a
    barrel already accepted that stands nearer. The column then counts only for the bands that were checked
    (the stripe is half of a column's weight, each body part a quarter).
  * ``seen``    = the mean over the stencil's columns of weight x q            (0 .. 1: the share of the barrel seen and right)
  * ``missing`` = the mean of weight x (1 - q)                                  (checked, and not there: unexplained)
  * ``outside`` = the share of the ring painted as if the barrel went on (body color beside / above / below the
    body, stripe color beside the stripe): the thing is bigger than this stencil.

A place is a barrel when its score is at least ``accept``. A non-barrel thing in front of a barrel is unpainted in
the mask, exactly like bare table: the mask cannot tell "hidden" from "absent". So a barrel hidden by such a thing
only gets what is seen of it, minus the cost of what is missing, and ``accept`` decides how little is enough.

Arbitration: the best place is accepted first; its box is then claimed: its pixels are evidence for no other place,
and for a place standing further away they count as hidden (explained) instead of missing. Scores are computed
again and the next best place is accepted, until none reaches ``accept``. (In one round several places are accepted,
best first, as long as they do not touch each other; a place that touches an accepted box waits for the next round,
when its score is up to date, and so does every place overlapping it.) Where several columns fit equally well
(a slice of a barrel with nothing saying which side is hidden) the box is put in the middle of them.

Every number of ``StencilConfig`` was fit or chosen on HOME train masks: results/2026-11-20_stencil/fit.md
(shape) and calibration.md (the three score numbers); the rule that chose them is in the experiment's PREREG.md.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from functools import lru_cache

import numpy as np

from . import geometry as geo
from .detect_types import Barrel
from .io import BLUE, ORANGE

NONE, U, S, L, HALO = 0, 1, 2, 3, 4          # the labels of ``render``
OTHER = {ORANGE: BLUE, BLUE: ORANGE}


@dataclass(frozen=True)
class StencilConfig:
    # the score (calibration.md)
    accept: float = 0.30          # a place is a barrel when its score is at least this
    absent_cost: float = 0.25     # what a checked-and-missing share costs, against 1 for a seen share
    outside_cost: float = 0.5     # what a fully painted ring costs
    band_full: float = 1.0        # a band of a column counts as fully there when at least this share of it is painted; below, in
                                  # proportion (1.0 = the painted share itself). Holes inside a seen barrel (a highlight) are not occlusion
    stripe_weight: float = 0.5    # the stripe's share of a column's weight (the two body parts share the rest equally)
    min_checked: float = 0.5      # a band of a column is checked when at least this share of it is not known to be hidden
    # the shape (fit.md): corrections to the camera model's rows, in px, as a + b x (barrel width in px)
    top_fit: tuple[float, float] = (1.96, 0.0)      # added to the model's top row (the median: the line did not predict better)
    bottom_fit: tuple[float, float] = (-4.62, 0.0887)   # added to the model's bottom row (-1.8 px at 32 px wide, +2.8 at 84)
    rim: float = 0.208            # the outer share of the width, each side, where the outline is rounded ...
    rim_top: float = 0.125        # ... there the upper body starts this share of its height lower
    rim_bottom: float = 0.333     # ... and the lower body ends this share of its height higher
    seam: float = 0.10            # not looked at: this share of the stripe's height on each side of every band edge (mixed pixels)
    halo: float = 0.10            # thickness of the ring outside the outline, as a share of the width (at least 2 px)
    # the search
    scale_step: float = 1.05      # neighbouring stencils differ by this factor in size
    min_width_px: float = 16.0    # the smallest stencil (the detector's far limit, ~60 cm)
    max_width_px: float = 420.0   # the largest (a barrel touching the bumper)
    dy_range: float = 0.08        # the stencil is also tried this share of its width up and down ...
    dy_step: float = 0.02         # ... in steps of this share (at least 1 px)
    plateau: float = 0.02         # columns scoring within this of the best one fit "equally well": the box goes in their middle
    depth_margin_px: int = 2      # an accepted barrel hides a place whose bottom row is at least this far above its own
    max_passes: int = 6           # rounds of accept / claim / score again

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Stencil:
    """The stencil of one size: rows (at vertical offset 0) and column shares, all in whole pixels."""
    d_mm: float       # the barrel's distance (axis, from the camera)
    W: int            # box width
    top: int          # box top row
    s_top: int        # first stripe row
    s_bot: int        # row after the last stripe row
    bottom: int       # row after the last barrel row (the box bottom)
    seam: int         # rows skipped on each side of a band edge
    halo: int         # ring thickness
    rim: int          # rim columns on each side
    rim_u: int        # first upper-body row in the rim columns
    rim_l: int        # row after the last lower-body row in the rim columns

    def bands(self, dy: int = 0) -> dict[str, tuple[int, int]]:
        """name -> (first row, row after the last), shifted ``dy`` rows down. ``U`` / ``S`` / ``L`` in the centre
        columns, ``Ur`` / ``Lr`` the body bands in the rim columns (the stripe is the same there), ``top`` / ``bot``
        the ring's strips above and below."""
        s, m = self.seam, self.halo
        b = {"U": (self.top + s, self.s_top - s), "S": (self.s_top + s, self.s_bot - s), "L": (self.s_bot + s, self.bottom - s),
             "Ur": (self.rim_u, self.s_top - s), "Lr": (self.s_bot + s, self.rim_l),
             "top": (self.top - s - m, self.top - s), "bot": (self.bottom + s, self.bottom + s + m)}
        return {k: (r0 + dy, r1 + dy) for k, (r0, r1) in b.items()}

    @property
    def pad(self) -> int:
        """How far the ring reaches outside the box."""
        return self.seam + self.halo

    def box(self, u: int, dy: int = 0) -> tuple[int, int, int, int]:
        return (u, self.top + dy, u + self.W, self.bottom + dy)


def make_stencil(cam: geo.CameraModel, d_mm: float, cfg: StencilConfig = StencilConfig()) -> Stencil:
    """The stencil of a barrel standing ``d_mm`` from the camera: the camera model's rows for that distance
    (``barrel_rows``), the top and bottom rows corrected by the fit, everything rounded to pixels."""
    r = cam.barrel_rows(d_mm)
    w = r.width_px
    W = max(4, int(round(w)))
    top = int(round(r.top + cfg.top_fit[0] + cfg.top_fit[1] * w))
    bottom = int(round(r.bottom + cfg.bottom_fit[0] + cfg.bottom_fit[1] * w))
    a, b = int(round(r.stripe_top)), int(round(r.stripe_bottom))
    b = max(b, a + 1)
    top, bottom = min(top, a - 2), max(bottom, b + 2)
    seam = max(0, min(max(1, int(round(cfg.seam * (b - a)))), (b - a - 1) // 2, (a - top - 1) // 2, (bottom - b - 1) // 2))
    rim = max(1, int(round(cfg.rim * W)))
    rim_u = min(a - seam - 1, top + max(seam, int(round(cfg.rim_top * (a - top)))))
    rim_l = max(b + seam + 1, bottom - max(seam, int(round(cfg.rim_bottom * (bottom - b)))))
    return Stencil(d_mm, W, top, a, b, bottom, seam, max(2, int(round(cfg.halo * W))), rim, rim_u, rim_l)


@lru_cache(maxsize=8)
def stencils(cam: geo.CameraModel, cfg: StencilConfig = StencilConfig()) -> tuple[Stencil, ...]:
    """One stencil per size, far to near: widths ``min_width_px`` x ``scale_step``^k up to ``max_width_px``."""
    out, w = [], cfg.min_width_px
    while w <= cfg.max_width_px:
        st = make_stencil(cam, cam.f * geo.BARREL_BULGE_DIAMETER_MM / w, cfg)
        if not out or st.W > out[-1].W:
            out.append(st)
        w *= cfg.scale_step
    return tuple(out)


def offsets(st: Stencil, cfg: StencilConfig = StencilConfig()) -> np.ndarray:
    """The vertical offsets tried for this stencil, in rows (whole numbers, 0 included)."""
    step = max(1, int(round(cfg.dy_step * st.W)))
    n = max(1, int(round(cfg.dy_range * st.W / step)))
    return np.arange(-n, n + 1) * step


def render(st: Stencil, dy: int = 0) -> tuple[np.ndarray, tuple[int, int]]:
    """The stencil as a picture: a label image (``NONE`` / ``U`` / ``S`` / ``L`` / ``HALO``) and the (column offset,
    row) of its top-left pixel relative to (the box's left column, row 0). For looking at, and for the slow scorer."""
    b, p = st.bands(dy), st.pad
    r0 = b["top"][0]
    lab = np.zeros((b["bot"][1] - r0, st.W + 2 * p), np.uint8)

    def put(rows, c0, c1, v):
        lab[max(0, rows[0] - r0):max(0, rows[1] - r0), c0 + p:c1 + p] = v
    put(b["U"], st.rim, st.W - st.rim, U); put(b["L"], st.rim, st.W - st.rim, L); put(b["S"], 0, st.W, S)
    for c0, c1 in ((0, st.rim), (st.W - st.rim, st.W)):
        put(b["Ur"], c0, c1, U); put(b["Lr"], c0, c1, L)
    put(b["top"], st.rim, st.W - st.rim, HALO); put(b["bot"], st.rim, st.W - st.rim, HALO)
    for c0, c1 in ((-p, -st.seam), (st.W + st.seam, st.W + p)):
        put(b["Ur"], c0, c1, HALO); put(b["S"], c0, c1, HALO); put(b["Lr"], c0, c1, HALO)
    return lab, (-p, r0)


def score_at(mask: np.ndarray, st: Stencil, color: int, u: int, dy: int = 0, cfg: StencilConfig = StencilConfig(),
             claimed: np.ndarray | None = None, hidden: np.ndarray | None = None) -> dict:
    """The score of ONE place, counted pixel by pixel from the rendered stencil (slow; the reference the fast
    scorer is tested against, and what ``method.md`` walks through). ``claimed``: pixels inside accepted boxes (no
    evidence for anybody); ``hidden``: the claimed pixels that belong to a barrel standing nearer than this place
    (not asked for). Returns score, seen, missing, explained, outside."""
    h, w = mask.shape
    lab, (c_off, r_off) = render(st, dy)
    rows = np.arange(lab.shape[0])[:, None] + r_off
    cols = np.arange(lab.shape[1])[None, :] + u + c_off
    inside = (rows >= 0) & (rows < h) & (cols >= 0) & (cols < w)
    rr, cc = np.clip(rows, 0, h - 1), np.clip(cols, 0, w - 1)
    m = np.where(inside, mask[rr, cc], 0)
    cl = np.where(inside, claimed[rr, cc], False) if claimed is not None else np.zeros(lab.shape, bool)
    hid = ~inside | (np.where(inside, hidden[rr, cc], False) if hidden is not None else False)
    other = OTHER[color]
    wanted = np.where(lab == S, other, color)                               # stripe band: the other color; body: the color
    agree = (m == wanted) & ~cl & inside
    weight = {U: (1 - cfg.stripe_weight) / 2, S: cfg.stripe_weight, L: (1 - cfg.stripe_weight) / 2}
    seen = missing = 0.0
    for x in range(st.pad, st.pad + st.W):                                  # the stencil's own columns
        q, wt = math.inf, 0.0
        for band in (U, S, L):
            sel = lab[:, x] == band
            n = int(sel.sum())
            if n == 0:
                continue
            open_ = n - int((sel & hid[:, x]).sum())
            if open_ < cfg.min_checked * n:
                continue                                                    # known to be hidden: not asked for
            q = min(q, min(1.0, int((sel & agree[:, x] & ~hid[:, x]).sum()) / max(open_, 1) / cfg.band_full))
            wt += weight[band]
        if wt > 0:
            seen += wt * q; missing += wt * (1 - q)
    seen /= st.W; missing /= st.W
    ring = (lab == HALO) & inside
    # in the ring the barrel "goes on" where the pixel has the color of the band beside it: the side strips' stripe rows
    # expect the stripe color, everything else the body color
    b = st.bands(dy)
    stripe_rows = (rows >= b["S"][0]) & (rows < b["S"][1])
    side = (np.arange(lab.shape[1])[None, :] < st.pad) | (np.arange(lab.shape[1])[None, :] >= st.pad + st.W)
    goes_on = np.where(stripe_rows & side, m == other, m == color) & ~cl
    outside = float((ring & goes_on).sum()) / max(1, int(ring.sum()))
    return {"score": seen - cfg.absent_cost * missing - cfg.outside_cost * outside, "seen": seen, "missing": missing,
            "explained": 1.0 - seen - missing, "outside": outside}


# ---------------------------------------------------------------- the fast scorer: every column of one stencil at once

def _cum_rows(a: np.ndarray) -> np.ndarray:
    """Running sum down the rows with a leading zero row: out[r1] - out[r0] = the count in rows r0 .. r1 - 1."""
    out = np.zeros((a.shape[0] + 1, a.shape[1]), np.int32)
    np.cumsum(a, axis=0, out=out[1:])
    return out


def _cum_cols(a: np.ndarray, pad: int) -> np.ndarray:
    """Running sum along the columns of ``a`` padded with ``pad`` zero columns on each side, with a leading zero."""
    out = np.zeros(a.shape[:-1] + (a.shape[-1] + 2 * pad + 1,), np.float64)
    np.cumsum(a, axis=-1, out=out[..., pad + 1:pad + 1 + a.shape[-1]])
    out[..., pad + 1 + a.shape[-1]:] = out[..., pad + a.shape[-1]:pad + a.shape[-1] + 1]
    return out


def score_map(st: Stencil, color: int, cum: dict, dys: np.ndarray, cfg: StencilConfig, shape: tuple[int, int],
              cum_hidden: np.ndarray | None = None) -> np.ndarray:
    """The score of every place of one stencil and one barrel color: out[i, j] = the score with vertical offset
    ``dys[i]`` and the box's left column at ``j - st.W`` (so j runs over every column where any of the box is in
    the frame). ``cum``: {color: running row sums of that color's unclaimed pixels}; ``cum_hidden``: the same for
    the pixels hidden by nearer accepted barrels (None = none). Same numbers as ``score_at``."""
    h, w = shape
    other = OTHER[color]
    b0 = st.bands(0)
    mu, wS = cfg.absent_cost, cfg.stripe_weight
    wB = (1 - wS) / 2

    def count(name, c):
        r0, r1 = b0[name]
        n = r1 - r0
        a0, a1 = np.clip(r0 + dys, 0, h), np.clip(r1 + dys, 0, h)
        agree = (cum[c][a1] - cum[c][a0]).astype(np.float64)                # (n_dy, w)
        hid = (n - (a1 - a0))[:, None].astype(np.float64)                   # rows outside the frame
        if cum_hidden is not None:
            hid = hid + (cum_hidden[a1] - cum_hidden[a0])
        return agree, n, hid, (a1 - a0)

    def frac(name, c):
        agree, n, hid, _ = count(name, c)
        open_ = n - hid
        checked = (open_ >= cfg.min_checked * n) & (n > 0)
        return np.where(checked, np.minimum(1.0, agree / np.maximum(open_, 1) / cfg.band_full), np.inf), checked, agree

    fS, cS, aS = frac("S", other)
    out_cols = {}
    side_paint = aS.copy()
    side_rows = count("S", other)[3].astype(np.float64)
    for prof, (un, ln) in (("centre", ("U", "L")), ("rim", ("Ur", "Lr"))):
        fU, cU, aU = frac(un, color)
        fL, cL, aL = frac(ln, color)
        q = np.minimum(np.minimum(fU, fS), fL)
        wt = wB * cU + wS * cS + wB * cL
        q = np.where(wt > 0, q, 0.0)
        out_cols[prof] = wt * ((1 + mu) * q - mu)
        if prof == "rim":
            side_paint += aU + aL
            side_rows += count(un, color)[3] + count(ln, color)[3]
    top_paint, _, _, top_rows = count("top", color)
    bot_paint, _, _, bot_rows = count("bot", color)

    W, rim, p = st.W, st.rim, st.pad
    P = W + p                                                                # zero columns on each side
    cs_c, cs_r = _cum_cols(out_cols["centre"], P), _cum_cols(out_cols["rim"], P)
    cs_t, cs_b, cs_s = _cum_cols(top_paint, P), _cum_cols(bot_paint, P), _cum_cols(side_paint, P)
    cin = _cum_cols(np.ones((1, w)), P)[0]                                   # how many frame columns up to here
    j = np.arange(w + W) + (P - W)                                           # padded index of the box's left column
    cols = (cs_c[:, j + W - rim] - cs_c[:, j + rim] + cs_r[:, j + rim] - cs_r[:, j] + cs_r[:, j + W] - cs_r[:, j + W - rim]) / W
    n_mid = cin[j + W - rim] - cin[j + rim]
    n_side = cin[j - st.seam] - cin[j - p] + cin[j + W + p] - cin[j + W + st.seam]
    paint = (cs_t[:, j + W - rim] - cs_t[:, j + rim] + cs_b[:, j + W - rim] - cs_b[:, j + rim]
             + cs_s[:, j - st.seam] - cs_s[:, j - p] + cs_s[:, j + W + p] - cs_s[:, j + W + st.seam])
    ring = (top_rows + bot_rows)[:, None] * n_mid[None, :] + side_rows[:, None] * n_side[None, :]
    return cols - cfg.outside_cost * paint / np.maximum(ring, 1.0)


# ---------------------------------------------------------------- arbitration

@dataclass
class _Claim:
    box: tuple[int, int, int, int]      # the accepted box grown by its seam, clipped to the frame
    bottom: int                         # the accepted stencil's bottom row (may be below the frame)


def _hidden_levels(claims: list[_Claim], shape) -> tuple[list[int], list[np.ndarray | None]]:
    """The accepted bottoms, nearest first, and for each k the running row sums of the pixels claimed by the k
    nearest ones (k = 0: None). A place is hidden by the accepted barrels whose bottom is far enough below its own."""
    order = sorted(claims, key=lambda c: -c.bottom)
    cums: list[np.ndarray | None] = [None]
    m = np.zeros(shape, bool)
    for c in order:
        x0, y0, x1, y1 = c.box
        m[y0:y1, x0:x1] = True
        cums.append(_cum_rows(m))
    return [c.bottom for c in order], cums


def _cannot_score(st: Stencil, color: int, dys: np.ndarray, row_paint: dict, row_claim: np.ndarray, h: int) -> bool:
    """True when no place of this stencil and color can score above 0, so its score map need not be computed: one of
    its three bands lies wholly inside the frame at every offset, with no claimed pixel in its rows (so it is checked
    in every column) and not one pixel of the color it predicts in those rows. Every column is then worth 0. A
    shortcut only: the answer is the same without it (tested)."""
    b = st.bands(0)
    for name, c in (("U", color), ("S", OTHER[color]), ("L", color)):
        r0, r1 = b[name][0] + int(dys.min()), b[name][1] + int(dys.max())
        if r0 >= 0 and r1 <= h and row_claim[r1] == row_claim[r0] and row_paint[c][r1] == row_paint[c][r0]:
            return True
    return False


def detect(mask: np.ndarray, cfg: StencilConfig = StencilConfig(), cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT,
           log: list | None = None, given: tuple[Barrel, ...] | list[Barrel] = (), shortcut: bool = True) -> list[Barrel]:
    """Class mask (0 other / 1 orange / 2 blue) -> barrels, by stencil matching. Same signature as
    ``detector.detect``. ``given``: barrels already known (another detector's boxes): they are claimed before the
    search starts and are not returned. ``log``: when a list, every accepted place is appended (diagnostics).
    ``shortcut=False`` computes every score map (slower, same answer)."""
    h, w = mask.shape
    sts = stencils(cam, cfg)
    claims = [_Claim((max(0, g.bbox[0]), max(0, g.bbox[1]), min(w, g.bbox[2]), min(h, g.bbox[3])), g.bbox[3]) for g in given]
    out: list[Barrel] = []
    paint = {c: mask == c for c in (ORANGE, BLUE)}
    for _ in range(cfg.max_passes):
        claimed = np.zeros((h, w), bool)
        for c in claims:
            x0, y0, x1, y1 = c.box
            claimed[y0:y1, x0:x1] = True
        cum = {c: _cum_rows(paint[c] & ~claimed) for c in (ORANGE, BLUE)}
        bottoms, cums = _hidden_levels(claims, (h, w))
        row_paint = {c: np.concatenate([[0], np.cumsum((paint[c] & ~claimed).sum(axis=1))]) for c in (ORANGE, BLUE)}
        row_claim = np.concatenate([[0], np.cumsum(claimed.sum(axis=1))])
        maps, cand = {}, []
        for k, st in enumerate(sts):
            dys = offsets(st, cfg)
            # how many accepted barrels stand nearer than this stencil at each offset
            level = np.array([sum(1 for b in bottoms if b >= st.bottom + int(dy) + cfg.depth_margin_px) for dy in dys]) if bottoms else np.zeros(len(dys), int)
            for color in (ORANGE, BLUE):
                if shortcut and _cannot_score(st, color, dys, row_paint, row_claim, h):
                    continue
                q = np.empty((len(dys), w + st.W))
                for lv in np.unique(level):
                    sel = level == lv
                    q[sel] = score_map(st, color, cum, dys[sel], cfg, (h, w), cums[lv])
                maps[(color, k)] = q
                i, j = np.nonzero(q >= cfg.accept)
                if len(i):
                    cand.append(np.stack([q[i, j], np.full(len(i), color), np.full(len(i), k), i, j], axis=1))
        if not cand:
            break
        cand = np.concatenate(cand)
        W_ = np.array([s.W for s in sts])[cand[:, 2].astype(int)]
        top_ = np.array([s.top for s in sts])[cand[:, 2].astype(int)]
        bot_ = np.array([s.bottom for s in sts])[cand[:, 2].astype(int)]
        dy_ = np.empty(len(cand))
        for k in np.unique(cand[:, 2]).astype(int):
            sel = cand[:, 2] == k
            dy_[sel] = offsets(sts[k], cfg)[cand[sel, 3].astype(int)]
        x0_ = cand[:, 4] - W_
        x1_, y0_, y1_ = x0_ + W_, top_ + dy_, bot_ + dy_
        area_ = (x1_ - x0_) * (y1_ - y0_)
        alive = np.ones(len(cand), bool)
        stale = np.zeros(len(cand), bool)                                    # touches a box accepted in this round: its score is out of date
        new: list[_Claim] = []
        while alive.any():
            n = int(np.argmax(np.where(alive, cand[:, 0], -np.inf)))
            color, k, i, j = int(cand[n, 1]), int(cand[n, 2]), int(cand[n, 3]), int(cand[n, 4])
            st, row = sts[k], maps[(color, k)][i]
            dy = int(dy_[n])
            if stale[n]:
                # this place waits for the next round, and so does every place that overlaps it by a quarter or more of the
                # smaller box: they explain the same paint, less well
                inter = np.clip(np.minimum(x1_, x1_[n]) - np.maximum(x0_, x0_[n]), 0, None) * np.clip(np.minimum(y1_, y1_[n]) - np.maximum(y0_, y0_[n]), 0, None)
                alive &= ~(inter >= 0.25 * np.minimum(area_, area_[n]))
                alive[n] = False
                continue
            lo = hi = j                                                      # the columns that fit as well as the best one
            while lo > 0 and row[lo - 1] >= row[j] - cfg.plateau:
                lo -= 1
            while hi < len(row) - 1 and row[hi + 1] >= row[j] - cfg.plateau:
                hi += 1
            jm = (lo + hi) // 2
            bx = st.box(jm - st.W, dy)
            box = (max(0, bx[0]), max(0, bx[1]), min(w, bx[2]), min(h, bx[3]))
            g = st.pad
            touch = (x0_ < bx[2] + g) & (x1_ > bx[0] - g) & (y0_ < bx[3] + g) & (y1_ > bx[1] - g)
            stale |= touch
            alive[n] = False
            inter = np.clip(np.minimum(x1_, bx[2]) - np.maximum(x0_, bx[0]), 0, None) * np.clip(np.minimum(y1_, bx[3]) - np.maximum(y0_, bx[1]), 0, None)
            alive &= ~(inter >= 0.25 * np.minimum(area_, (bx[2] - bx[0]) * (bx[3] - bx[1])))      # the accepted place's own neighbours in the search
            if box[2] <= box[0] or box[3] <= box[1]:
                continue
            flags = set()
            if box != bx:
                flags.add("truncated")
            if row[jm] < 0.6:
                flags.add("occluded")
            out.append(Barrel(color=color, bbox=box, confidence=float(row[jm]), flags=frozenset(flags), source="stencil"))
            new.append(_Claim((max(0, bx[0] - st.seam), max(0, bx[1] - st.seam), min(w, bx[2] + st.seam), min(h, bx[3] + st.seam)), bx[3]))
            if log is not None:
                log.append({"stage": "stencil", "why": "kept", "bbox": box, "body": color, "score": float(row[jm]), "best": float(row[j]),
                            "width": st.W, "dy": dy, "plateau": hi - lo + 1})
        if not new:
            break
        claims += new
    return sorted(out, key=lambda b: b.bbox[0])


# ---------------------------------------------------------------- the stencil as a checker of another detector's boxes

def box_score(mask: np.ndarray, barrel: Barrel, cfg: StencilConfig = StencilConfig(), cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT,
              others: tuple[Barrel, ...] | list[Barrel] = (), iou_min: float = 0.5) -> float:
    """How well a stencil fits where another detector drew ``barrel``: the best score over the places whose box
    overlaps the drawn one by ``iou_min`` or more (same color). ``others``: the other drawn barrels; the ones
    standing nearer hide. -inf when no stencil overlaps the box that much."""
    h, w = mask.shape
    x0, y0, x1, y1 = barrel.bbox
    claims = [_Claim((max(0, o.bbox[0]), max(0, o.bbox[1]), min(w, o.bbox[2]), min(h, o.bbox[3])), o.bbox[3]) for o in others]
    claimed = np.zeros((h, w), bool)
    for c in claims:
        if c.bottom >= y1 + cfg.depth_margin_px:                             # only what stands nearer is taken away from this box
            claimed[c.box[1]:c.box[3], c.box[0]:c.box[2]] = True
    cum = {c: _cum_rows((mask == c) & ~claimed) for c in (ORANGE, BLUE)}
    cum_h = _cum_rows(claimed) if claimed.any() else None
    best = -math.inf
    area = (x1 - x0) * (y1 - y0)
    for st in stencils(cam, cfg):
        if not 0.5 * (x1 - x0) <= st.W <= 2.5 * (x1 - x0) and not (x0 == 0 or x1 == w or y1 == h):
            continue
        dys = offsets(st, cfg)
        q = score_map(st, barrel.color, cum, dys, cfg, (h, w), cum_h)
        u = np.arange(w + st.W) - st.W
        bx0, bx1 = np.clip(u, 0, w), np.clip(u + st.W, 0, w)
        by0, by1 = np.clip(st.top + dys, 0, h), np.clip(st.bottom + dys, 0, h)
        iw = np.clip(np.minimum(bx1, x1) - np.maximum(bx0, x0), 0, None)[None, :]
        ih = np.clip(np.minimum(by1, y1) - np.maximum(by0, y0), 0, None)[:, None]
        inter = iw * ih
        union = area + ((bx1 - bx0)[None, :] * (by1 - by0)[:, None]) - inter
        ok = inter >= iou_min * np.maximum(union, 1)
        if ok.any():
            best = max(best, float(q[ok].max()))
    return best
