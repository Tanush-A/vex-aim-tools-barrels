"""The barrel as its own color reference (experiment 2026-11-26_selfcal; NOT called by anything that runs by default).

The fixed color ranges break when the light or the table changes, and the right ranges cannot be predicted from the
whole frame, because barrels are a few percent of it. This module lets a barrel that is found, or half found, say what
this frame's colors are. Pixels are never changed; only the ranges a pixel is tested against are set per frame, and
nothing is carried from one frame to the next (``Result`` is per frame; ``extra`` exists for the report-only "one
session in one room" number).

In the order the data flows (``SelfCal.run``):

1. **First pass.** The fixed model -> mask -> ``detector.detect`` -> today's boxes.
2. **Seeds** (``find_seeds``): places where one barrel is known or half known.
   - ``found``: a box of the first pass (by default only one with no flag: not partly hidden, not cut, no edge guessed).
   - ``body``: a strict body color with a gap in it that has the size and the row of a stripe (the stripe is not
     painted).
   - ``stripe``: a solid band of one strict color with the size of a stripe for its row (the body is not painted).
   Every seed is a box: the stripe's row gives the distance, the distance the top and the bottom (``rows_at_stripe``).
3. **The photo check** (``verify``), the guard against a seed that is not a barrel. Inside the box the three bands a
   barrel has (upper body, stripe, lower body; ``bands``) are read from the photo. Kept only if: the part that made
   it a seed is really painted there; both body bands differ from the stripe band in log(R/B), with the sign of the
   seed's color, by ``rel_margin`` (orange above and below blue, or blue above and below orange); and a part that was
   read rather than painted does not look like what is around the box (``surround``).
4. **What a kept seed changes.**
   - ``local``: its own unpainted part is painted inside its own box, with the range read on that part
     (``ReadBox``: hue, saturation and brightness, percentile to percentile plus a margin). Cannot flood.
   - ``frame``: its two readings are added to the frame's ranges for the two classes (``frame_ranges``): a range may
     only widen, a hue end may move at most ``hue_move_max``, the saturation floor not under ``s_floor_min``, several
     seeds must agree, and a widened range that paints more than ``flood_max`` of the frame is dropped
     (``flood``).
5. **Second pass.** The frame's ranges -> mask, plus the local paint -> ``detector.detect``. The boxes of the two
   passes are combined (``combine``): the first-pass boxes stay as they are, a second-pass box is added where no
   first-pass box is.
"""
from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass, field

import cv2
import numpy as np

from . import boxfit as bf
from . import detector as det
from . import geometry as geo
from . import pipeline as pl
from .counting import on_share
from .io import BLUE, ORANGE

OTHER_OF = {ORANGE: BLUE, BLUE: ORANGE}
NAME = {ORANGE: "orange", BLUE: "blue"}
# the bands of a barrel inside its box, as shares of the box (docs/review-2026-11-26/color_physics.md, "Step 0": measured
# on the home masks, 100 % of every patch carries the expected class)
BAND_COLS = (0.36, 0.64)
STRIPE_ROWS = (0.51, 0.61)
LOWER_ROWS = (0.75, 0.90)
STRIPE_FULL_ROWS = (0.40, 0.72)          # the rows the whole stripe may occupy (its edges sit at 0.40-0.50 and 0.625-0.70)


def upper_rows(box_h: float) -> tuple[float, float]:
    """The upper-body band: under the lid's front edge, above the stripe; lower in the box for a near (tall) barrel."""
    return (0.27, 0.37) if box_h < 45 else (0.30, 0.40) if box_h < 80 else (0.34, 0.44)


@dataclass(frozen=True)
class SelfCalConfig:
    # which seeds
    seed_found: bool = True
    found_flags: str = "none"        # "none": only first-pass boxes with no flag; "any": every first-pass box
    seed_body: bool = True
    seed_stripe: bool = True
    # what a kept seed changes
    local: bool = True
    frame: bool = True
    rounds: int = 1                  # 2 = the seeds are looked for once more on the second-pass mask
    # a seed's shape, as multiples of what its row predicts
    stripe_h: tuple[float, float] = (0.45, 1.6)      # the detector's own stripe-height window (here: thickness for its width)
    width: tuple[float, float] = (0.55, 1.25)        # the band's width against the width its row predicts (the box is sized
                                                     # by the band itself: on the soft ottoman barrels are 0.6-0.7 of the row's size)
    cover_min: float = 0.85          # the band holds a pixel in at least this share of its columns (a band, not speckles)
    min_area_px: int = 20
    min_width_px: float = 16.0       # beyond the table (the detector's min_width_px)
    # the photo check
    painted_min: float = 0.5         # the part that makes it a seed is painted on at least this share of its band
    complete_below: float = 0.8      # a part painted on less than this share of its band is read and completed
    rel_margin: float = 0.5          # log(R/B): body minus stripe, both body bands, with the body's sign
    min_band_px: int = 6
    surround_share: float = 0.5      # a side "looks like the read part" when this share of it is inside the read range
    surround_sides_max: int = 1      # a read part may look like at most this many sides of its surround (99 = guard off)
    # a reading -> a range
    pct: tuple[float, float] = (5.0, 95.0)
    hue_margin: float = 3.0
    s_margin: float = 20.0
    v_margin: float = 15.0
    # the frame's ranges
    hue_move_max: float = 10.0       # a hue end moves at most this far from the fixed one
    s_floor_min: float = 60.0        # the saturation floor never goes under this; pixels under it are not read for hue
    agree_hue: float = 6.0           # several readings of one class: their median hues lie within this of their median
    hue_spread_max: float = 12.0     # a reading moves a frame range only when it is one color: its hue percentiles this close
    min_range_px: int = 20           # ... and it holds at least this many colorful pixels
    seed_rules: bool = True          # a second-pass box on a kept seed's box must have the seed's color
    flood_max: float = 0.03         # a widened range may newly paint at most this share of the frame under the horizon gate,
                                    # not counting what it paints inside the kept seeds' own boxes
    combine: str = "add"             # "add": first-pass boxes stay, second-pass boxes fill in; "second": the reverse


# ---------------------------------------------------------------- geometry: a stripe's row -> the barrel's rows

def rows_at_stripe(cam: geo.CameraModel, center_row: float) -> geo.BarrelRows | None:
    """The rows of a barrel whose stripe centre (12 mm up, on the bulge's near side) is seen at ``center_row``; None
    at or above the horizon, or nearer than a barrel can stand."""
    angle = math.atan2(center_row - cam.cy, cam.f) + cam.tilt
    if angle <= 0:
        return None
    d = (cam.height_mm - geo.BARREL_HEIGHT_MM / 2) / math.tan(angle) + geo.BARREL_BULGE_DIAMETER_MM / 2
    if d <= geo.BARREL_BULGE_DIAMETER_MM / 2 + 1:
        return None
    return cam.barrel_rows(d)


def _clip(rect, shape) -> tuple[int, int, int, int] | None:
    h, w = shape
    x0, y0, x1, y1 = rect
    x0, y0, x1, y1 = max(0, int(round(x0))), max(0, int(round(y0))), min(w, int(round(x1))), min(h, int(round(y1)))
    return (x0, y0, x1, y1) if x1 > x0 and y1 > y0 else None


def band_rows(bbox, stripe: tuple[float, float] | None = None) -> dict[str, tuple[float, float]]:
    """The rows of the three read bands (``upper``, ``stripe``, ``lower``) and of the whole stripe (``stripe_full``).

    Without ``stripe``: shares of the box (a found box; measured on the home masks). With ``stripe`` = the seen
    (top row, bottom row) of the stripe or of the gap where it should be: around that, in stripe heights. The side wall
    above and below the stripe is 9 mm against the stripe's 6, so each body band is the 0.25 to 0.9 stripe heights
    next to it; the stripe band is the stripe's middle half."""
    x0, y0, x1, y1 = bbox
    h = y1 - y0
    if stripe is None:
        return {"upper": tuple(y0 + a * h for a in upper_rows(h)), "stripe": tuple(y0 + a * h for a in STRIPE_ROWS),
                "lower": tuple(y0 + a * h for a in LOWER_ROWS), "stripe_full": tuple(y0 + a * h for a in STRIPE_FULL_ROWS)}
    st, sb = stripe
    t = max(2.0, sb - st)
    return {"upper": (st - 0.9 * t, st - 0.25 * t), "stripe": (st + 0.25 * t, sb - 0.25 * t), "lower": (sb + 0.25 * t, sb + 0.9 * t),
            "stripe_full": (st - 0.25 * t, sb + 0.25 * t)}


def bands(bbox, shape, stripe: tuple[float, float] | None = None) -> dict[str, tuple] | None:
    """The three read bands of a barrel box (centre columns): ``upper``, ``stripe``, ``lower``, each a pixel rect
    (x0, y0, x1, y1). None when one of them is off the frame. ``stripe``: see ``band_rows``."""
    x0, y0, x1, y1 = bbox
    w = x1 - x0
    rows = band_rows(bbox, stripe)
    out = {}
    for name in ("upper", "stripe", "lower"):
        r0, r1 = rows[name]
        c0 = x0 + BAND_COLS[0] * w
        r = _clip((c0, r0, max(x0 + BAND_COLS[1] * w, c0 + 1), max(r1, r0 + 1)), shape)
        if r is None:
            return None
        out[name] = r
    return out


# ---------------------------------------------------------------- reading a band of the photo

def hue_line(frame: pl.Frame, cls: int) -> np.ndarray:
    """Hue on the class's own line: orange -30..149 (so its sector at the red wrap is one piece), blue 0..179."""
    s = pl.HUE_SHIFT[cls]
    return frame.hs(s)[..., 0] - s


@dataclass(frozen=True)
class Reading:
    """What the photo shows in one band (or two pooled), for the class that band should be."""
    cls: int
    n: int
    hue: tuple[float, float, float]              # low percentile, median, high percentile, all pixels
    sat: tuple[float, float, float]
    val: tuple[float, float, float]
    hue_col: tuple[float, float, float] | None   # the same over the pixels with S >= s_floor_min; None when too few
    colorful: float                              # the share of pixels with S >= s_floor_min
    n_col: int                                   # how many pixels that is
    lrb: float                                  # log((R + 1) / (B + 1)) of the mean color
    painted: float                               # the share the mask already paints ``cls``


def read_band(frame: pl.Frame, mask: np.ndarray, rects, cls: int, cfg: SelfCalConfig = SelfCalConfig()) -> Reading | None:
    hl_, hs = hue_line(frame, cls), frame.hs(pl.HUE_SHIFT[cls])
    hue, sat, val, rgb, m = [], [], [], [], []
    for x0, y0, x1, y1 in rects:
        hue.append(hl_[y0:y1, x0:x1].ravel()); sat.append(hs[y0:y1, x0:x1, 1].ravel()); val.append(frame.val[y0:y1, x0:x1].ravel())
        rgb.append(frame.rgb[y0:y1, x0:x1].reshape(-1, 3)); m.append(mask[y0:y1, x0:x1].ravel())
    hue, sat, val, rgb, m = (np.concatenate(a) for a in (hue, sat, val, rgb, m))
    if len(hue) < cfg.min_band_px:
        return None
    q = (cfg.pct[0], 50.0, cfg.pct[1])

    def pc(a) -> tuple:
        return tuple(float(v) for v in np.percentile(a, q))
    col = sat >= cfg.s_floor_min
    mean = rgb.astype(np.float64).mean(axis=0)
    return Reading(cls, int(len(hue)), pc(hue), pc(sat), pc(val), pc(hue[col]) if int(col.sum()) >= cfg.min_band_px else None,
                   float(col.mean()), int(col.sum()), float(math.log((mean[0] + 1) / (mean[2] + 1))), float((m == cls).mean()))


@dataclass(frozen=True)
class ReadBox:
    """A range read on one band: hue (the class's line), saturation and brightness, each from the low to the high
    percentile of the band, widened by a margin."""
    cls: int
    h: tuple[float, float]
    s: tuple[float, float]
    v: tuple[float, float]


def read_box(r: Reading, cfg: SelfCalConfig = SelfCalConfig()) -> ReadBox:
    return ReadBox(r.cls, (r.hue[0] - cfg.hue_margin, r.hue[2] + cfg.hue_margin), (r.sat[0] - cfg.s_margin, r.sat[2] + cfg.s_margin),
                   (r.val[0] - cfg.v_margin, r.val[2] + cfg.v_margin))


def in_read_box(frame: pl.Frame, box: ReadBox, rect) -> np.ndarray:
    """Which pixels of ``rect`` are inside the read range (a bool array of the rect's shape)."""
    x0, y0, x1, y1 = rect
    h = hue_line(frame, box.cls)[y0:y1, x0:x1]
    s = frame.hs(pl.HUE_SHIFT[box.cls])[y0:y1, x0:x1, 1]
    v = frame.val[y0:y1, x0:x1]
    return (h >= box.h[0]) & (h <= box.h[1]) & (s >= box.s[0]) & (s <= box.s[1]) & (v >= box.v[0]) & (v <= box.v[1])


# ---------------------------------------------------------------- the surround of a seed's box

def surround(bbox, part: str, shape, stripe: tuple[float, float] | None = None) -> dict[str, list]:
    """Rects around a barrel box where the table (or whatever stands there) is seen. ``part`` "stripe": left and right
    of the box at the stripe's rows. ``part`` "body": left and right at the two body bands' rows, above the top, below
    the bottom. A side that is off the frame has no rect. ``stripe``: see ``band_rows``."""
    x0, y0, x1, y1 = bbox
    w, h = x1 - x0, y1 - y0
    gap, sw = 0.15 * w, 0.30 * w
    rows = band_rows(bbox, stripe)
    spans = [rows["stripe_full"]] if part == "stripe" else [rows["upper"], rows["lower"]]
    out: dict[str, list] = {"left": [], "right": []}
    for r0, r1 in spans:
        for side, (c0, c1) in (("left", (x0 - gap - sw, x0 - gap)), ("right", (x1 + gap, x1 + gap + sw))):
            r = _clip((c0, r0, c1, max(r1, r0 + 1)), shape)
            if r is not None and (r[2] - r[0]) >= 2:
                out[side].append(r)
    if part == "body":
        for side, (r0, r1) in (("above", (y0 - 0.25 * h, y0 - 0.08 * h)), ("below", (y1 + 0.08 * h, y1 + 0.25 * h))):
            r = _clip((x0 + 0.25 * w, r0, x1 - 0.25 * w, r1), shape)
            out[side] = [r] if r is not None and (r[3] - r[1]) >= 2 else []
    return out


def sides_like(frame: pl.Frame, box: ReadBox, bbox, part: str, cfg: SelfCalConfig = SelfCalConfig(),
               stripe: tuple[float, float] | None = None) -> list[str]:
    """The sides of the surround whose pixels are mostly inside the read range (they look like the read part)."""
    out = []
    for side, rects in surround(bbox, part, frame.shape, stripe).items():
        if not rects:
            continue
        inside = np.concatenate([in_read_box(frame, box, r).ravel() for r in rects])
        if inside.mean() >= cfg.surround_share:
            out.append(side)
    return out


# ---------------------------------------------------------------- seeds

@dataclass(frozen=True)
class Seed:
    kind: str                      # found | body | stripe
    body: int                      # the barrel's body class
    bbox: tuple[int, int, int, int]
    ok: bool = False
    why: str = ""                  # "ok", or the guard that refused it
    rel: float = 0.0               # the smaller of (upper - stripe) and (lower - stripe) in log(R/B), with the body's sign
    body_reading: Reading | None = None
    stripe_reading: Reading | None = None
    body_box: ReadBox | None = None        # set when the body is read rather than painted: its local range
    stripe_box: ReadBox | None = None      # the same for the stripe
    like: tuple = ()                       # the sides of the surround that looked like a read part
    stripe: tuple[float, float] | None = None      # the seen (top row, bottom row) of the stripe or gap; None for a found box

    @property
    def stripe_cls(self) -> int:
        return OTHER_OF[self.body]


def verify(frame: pl.Frame, mask: np.ndarray, kind: str, body: int, bbox, cfg: SelfCalConfig = SelfCalConfig(),
           stripe: tuple[float, float] | None = None) -> Seed:
    """The photo check on one seed box. Returns the seed with ``ok`` and the guard that refused it in ``why``.
    ``stripe``: the seen rows of the stripe (or gap) of a half-found seed; the bands are then placed around it."""
    bbox = tuple(int(v) for v in bbox)
    seed = Seed(kind, body, bbox, stripe=stripe)

    def no(why: str, **kw) -> Seed:
        return dataclasses.replace(seed, ok=False, why=why, **kw)
    b = bands(bbox, frame.shape, stripe)
    if b is None:
        return no("off_frame")
    other = OTHER_OF[body]
    up, lo, st = (read_band(frame, mask, [b[k]], c, cfg) for k, c in (("upper", body), ("lower", body), ("stripe", other)))
    both = read_band(frame, mask, [b["upper"], b["lower"]], body, cfg)
    if up is None or lo is None or st is None or both is None:
        return no("too_small")
    sign = 1.0 if body == ORANGE else -1.0
    rel = min(sign * (up.lrb - st.lrb), sign * (lo.lrb - st.lrb))
    kw = dict(rel=float(rel), body_reading=both, stripe_reading=st)
    if kind == "body" and both.painted < cfg.painted_min:
        return no("body_not_painted", **kw)
    if kind == "stripe" and st.painted < cfg.painted_min:
        return no("stripe_not_painted", **kw)
    if rel < cfg.rel_margin:
        return no("not_two_colors", **kw)
    like: list[str] = []
    if st.painted < cfg.complete_below:
        kw["stripe_box"] = read_box(st, cfg)
        sides = sides_like(frame, kw["stripe_box"], bbox, "stripe", cfg, stripe)
        like += [f"stripe:{s}" for s in sides]
        if len(sides) > cfg.surround_sides_max:
            return no("stripe_like_surround", like=tuple(like), **kw)
    if both.painted < cfg.complete_below:
        kw["body_box"] = read_box(both, cfg)
        sides = sides_like(frame, kw["body_box"], bbox, "body", cfg, stripe)
        like += [f"body:{s}" for s in sides]
        if len(sides) > cfg.surround_sides_max:
            return no("body_like_surround", like=tuple(like), **kw)
    return dataclasses.replace(seed, ok=True, why="ok", like=tuple(like), **kw)


def _closed(m: np.ndarray) -> np.ndarray:
    return cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)).astype(bool)


def _stripe_h_by_row(cam: geo.CameraModel, h: int) -> np.ndarray:
    out = np.zeros(h, np.float32)
    for r in range(h):
        rows = rows_at_stripe(cam, r + 0.5)
        if rows is not None:
            out[r] = rows.stripe_bottom - rows.stripe_top
    return out


def stripe_shaped(sub: np.ndarray, x: int, y: int, cam: geo.CameraModel, cfg: SelfCalConfig = SelfCalConfig(), frame_h: int = 480):
    """Is this band (``sub``: its pixels inside its own box, whose corner is at column ``x``, row ``y``) a stripe?
    -> the barrel box it implies, or None.

    Its width must be ``width`` x the barrel width its row predicts. The barrel is then sized by the band itself (as
    wide as the band; rows scaled by the same factor around the band's middle row), and the band's thickness (the
    median over its columns, so a curved stripe is not read as a tall one) must be ``stripe_h`` x the stripe height of
    a barrel of that size. It must hold a pixel in ``cover_min`` of its columns."""
    bh, bw = sub.shape
    area = int(sub.sum())
    if area < cfg.min_area_px or bw < cfg.width[0] * cfg.min_width_px:
        return None
    col_t = sub.sum(axis=0)
    if (col_t > 0).mean() < cfg.cover_min:
        return None
    center = float(np.median(np.where(sub)[0])) + y + 0.5
    rows = rows_at_stripe(cam, center)
    if rows is None or rows.width_px < cfg.min_width_px:
        return None
    k = bw / rows.width_px
    if not (cfg.width[0] <= k <= cfg.width[1]):
        return None
    hs = (rows.stripe_bottom - rows.stripe_top) * k
    t = float(np.median(col_t[col_t > 0]))
    if not (cfg.stripe_h[0] * hs <= t <= cfg.stripe_h[1] * hs):
        return None
    top, bottom = int(round(center - (center - rows.top) * k)), int(round(center + (rows.bottom - center) * k))
    top, bottom = max(0, top), min(frame_h, bottom)
    if bottom - top < 8:
        return None
    mid = sub[:, int(BAND_COLS[0] * bw):max(int(BAND_COLS[1] * bw), int(BAND_COLS[0] * bw) + 1)]
    mid = mid[:, mid.any(axis=0)]
    if mid.shape[1] == 0:
        return None
    s_top = float(np.median(mid.argmax(axis=0))) + y                              # the band's rows in its centre columns
    s_bot = float(np.median(bh - mid[::-1].argmax(axis=0))) + y
    return (x, top, x + bw, bottom), (s_top, s_bot)


def _stripe_shaped(sel_stats, lab: np.ndarray, i: int, cam: geo.CameraModel, cfg: SelfCalConfig):
    x, y, bw, bh, area = (int(v) for v in sel_stats[i])
    if area < cfg.min_area_px or bw < cfg.width[0] * cfg.min_width_px:
        return None
    return stripe_shaped(lab[y:y + bh, x:x + bw] == i, x, y, cam, cfg, lab.shape[0])


def body_gap_boxes(mask: np.ndarray, cam: geo.CameraModel, cfg: SelfCalConfig = SelfCalConfig()) -> list[tuple[int, tuple]]:
    """(body class, barrel box) for every gap in one strict color that has that color above and below it, column by
    column (within three stripe heights, the detector's reach), and the height and width of a stripe for its row."""
    h, w = mask.shape
    rows_idx = np.arange(h)[:, None]
    reach = (3.0 * _stripe_h_by_row(cam, h))[:, None]
    out = []
    for body in (ORANGE, BLUE):
        bm = _closed(mask == body)
        if not bm.any():
            continue
        up = np.maximum.accumulate(np.where(bm, rows_idx, -10 ** 6), axis=0)
        dn = np.minimum.accumulate(np.where(bm, rows_idx, 10 ** 6)[::-1], axis=0)[::-1]
        gap = ~bm & ((rows_idx - up) <= reach) & ((dn - rows_idx) <= reach)
        n, lab, st, _ = cv2.connectedComponentsWithStats(gap.astype(np.uint8), connectivity=8)
        for i in range(1, n):
            got = _stripe_shaped(st, lab, i, cam, cfg)
            if got is not None:
                out.append((body, *got))
    return out


def stripe_band_boxes(mask: np.ndarray, cam: geo.CameraModel, cfg: SelfCalConfig = SelfCalConfig()) -> list[tuple[int, tuple]]:
    """(body class, barrel box) for every solid band of one strict color with the height and width of a stripe for
    its row: the barrel it would be the stripe of has the OTHER color as its body."""
    out = []
    for other in (ORANGE, BLUE):
        om = _closed(mask == other)
        if not om.any():
            continue
        n, lab, st, _ = cv2.connectedComponentsWithStats(om.astype(np.uint8), connectivity=8)
        for i in range(1, n):
            got = _stripe_shaped(st, lab, i, cam, cfg)
            if got is not None:
                out.append((OTHER_OF[other], *got))
    return out


def find_seeds(frame: pl.Frame, mask: np.ndarray, boxes: list, cam: geo.CameraModel,
               cfg: SelfCalConfig = SelfCalConfig()) -> list[Seed]:
    """Every seed candidate with its verdict, kept ones first found first: first-pass boxes, then body gaps, then stripe
    bands. A candidate whose box sits on a kept seed's box is that barrel again (``why`` = "duplicate")."""
    cands: list[tuple[str, int, tuple, tuple | None]] = []
    if cfg.seed_found:
        cands += [("found", b.color, b.bbox, None) for b in boxes if cfg.found_flags == "any" or not b.flags]
    if cfg.seed_body:
        cands += [("body", c, bb, st) for c, bb, st in body_gap_boxes(mask, cam, cfg)]
    if cfg.seed_stripe:
        cands += [("stripe", c, bb, st) for c, bb, st in stripe_band_boxes(mask, cam, cfg)]
    out: list[Seed] = []
    for kind, body, bbox, stripe in cands:
        if any(s.ok and on_share(s.bbox, bbox) >= 0.5 for s in out):
            out.append(Seed(kind, body, tuple(int(v) for v in bbox), False, "duplicate", stripe=stripe))
            continue
        out.append(verify(frame, mask, kind, body, bbox, cfg, stripe))
    return out


# ---------------------------------------------------------------- the frame's ranges

def class_readings(seeds: list[Seed]) -> dict[int, list[Reading]]:
    """The readings of the kept seeds, by the class they are a sample of."""
    out: dict[int, list[Reading]] = {ORANGE: [], BLUE: []}
    for s in seeds:
        if s.ok:
            out[s.body].append(s.body_reading)
            out[s.stripe_cls].append(s.stripe_reading)
    return out


def frame_ranges(readings: dict[int, list[Reading]], fixed: dict[int, bf.Box], cfg: SelfCalConfig = SelfCalConfig()) -> tuple[dict[int, bf.Box], dict]:
    """The frame's class boxes (shifted hue, S) from the readings: the fixed box, widened to hold what was read.

    Per class: only readings that are one color count (at least half their pixels and at least ``min_range_px`` of them
    at S >= ``s_floor_min``; their hue is read on those pixels and spans at most ``hue_spread_max``); several readings must agree (median hues within ``agree_hue`` of their median; the ones that
    do not are left out, and if fewer than half agree none is used); a hue end moves at most ``hue_move_max``; the
    saturation floor only goes down, never under ``s_floor_min``."""
    out, info = {}, {}
    for c in (ORANGE, BLUE):
        fx = fixed[c]
        shift = pl.HUE_SHIFT[c]
        rs = [r for r in readings.get(c, []) if r is not None and r.hue_col is not None and r.colorful >= 0.5
              and r.n_col >= cfg.min_range_px and (r.hue_col[2] - r.hue_col[0]) <= cfg.hue_spread_max]
        n_all = len([r for r in readings.get(c, []) if r is not None])
        used = rs
        if len(rs) >= 2:
            med = float(np.median([r.hue_col[1] for r in rs]))
            used = [r for r in rs if abs(r.hue_col[1] - med) <= cfg.agree_hue]
            if 2 * len(used) < len(rs):
                used = []
        if not used:
            out[c] = fx
            info[NAME[c]] = {"readings": n_all, "colorful": len(rs), "used": 0}
            continue
        f_lo, f_hi, f_s = fx.lo[0] - shift, fx.hi[0] - shift, fx.lo[1]
        lo = max(f_lo - cfg.hue_move_max, min(f_lo, min(r.hue_col[0] for r in used) - cfg.hue_margin))
        hi = min(f_hi + cfg.hue_move_max, max(f_hi, max(r.hue_col[2] for r in used) + cfg.hue_margin))
        s = max(min(cfg.s_floor_min, f_s), min(f_s, min(r.sat[0] for r in used) - cfg.s_margin))
        lo, hi, s = float(math.floor(lo)), float(math.ceil(hi)), float(math.floor(s))
        out[c] = bf.Box((lo + shift, s), (hi + shift, fx.hi[1]))
        info[NAME[c]] = {"readings": n_all, "colorful": len(rs), "used": len(used), "h_lo": lo, "h_hi": hi, "s_lo": s,
                         "moved": bool((lo, hi, s) != (f_lo, f_hi, f_s))}
    return out, info


def flood(frame: pl.Frame, model: pl.Model, boxes: dict[int, bf.Box], cfg: SelfCalConfig = SelfCalConfig(),
          seeds: list | tuple = ()) -> tuple[dict[int, bf.Box], dict]:
    """The flood guard: a class whose widened box newly paints more than ``flood_max`` of the pixels under the horizon
    gate goes back to its fixed box. New paint inside a kept seed's box (grown by a tenth) is on a barrel and is not
    counted. Returns (boxes, {class name: the share it would have painted})."""
    keep = frame.val >= model.cfg.v_min
    hz = model.cfg.horizon_row or 0
    keep[:hz] = False
    for s in seeds:
        if s.ok:
            x0, y0, x1, y1 = s.bbox
            r = _clip((x0 - 0.1 * (x1 - x0), y0 - 0.1 * (y1 - y0), x1 + 0.1 * (x1 - x0), y1 + 0.1 * (y1 - y0)), frame.shape)
            if r is not None:
                keep[r[1]:r[3], r[0]:r[2]] = False
    total = max(1, (frame.shape[0] - hz) * frame.shape[1])
    out, shares = dict(boxes), {}
    for c in (ORANGE, BLUE):
        if boxes[c] == model.boxes[c]:
            continue
        hs = frame.hs(pl.HUE_SHIFT[c])
        new = keep & bf.in_box(hs, boxes[c]) & ~bf.in_box(hs, model.boxes[c])
        shares[NAME[c]] = float(new.sum() / total)
        if shares[NAME[c]] > cfg.flood_max:
            out[c] = model.boxes[c]
    return out, shares


def paint_local(frame: pl.Frame, mask: np.ndarray, seeds: list[Seed]) -> np.ndarray:
    """A copy of ``mask`` with each kept seed's read part painted inside its own box: the stripe's rows first (pixels
    inside the stripe's read range -> the stripe's class), then the box (pixels inside the body's read range -> the
    body's class). Only unpainted pixels are painted; what the ranges painted is never changed."""
    out = mask.copy()
    for s in seeds:
        if not s.ok:
            continue
        x0, y0, x1, y1 = s.bbox
        if s.stripe_box is not None:
            r0, r1 = band_rows(s.bbox, s.stripe)["stripe_full"]
            rect = _clip((x0, r0, x1, r1), frame.shape)
            if rect is not None:
                sub = out[rect[1]:rect[3], rect[0]:rect[2]]
                sub[(sub == 0) & in_read_box(frame, s.stripe_box, rect)] = s.stripe_cls
        if s.body_box is not None:
            rect = _clip(s.bbox, frame.shape)
            if rect is not None:
                sub = out[rect[1]:rect[3], rect[0]:rect[2]]
                sub[(sub == 0) & in_read_box(frame, s.body_box, rect)] = s.body
    return out


def combine(first: list, second: list, how: str = "add") -> list:
    """The boxes of the two passes as one list. "add": every first-pass box as it is, plus each second-pass box that
    is not on a first-pass box (half of the smaller box inside the other). "second": the reverse."""
    if how not in ("add", "second"):
        raise ValueError(f"combine must be 'add' or 'second', got {how!r}")
    base, more = (first, second) if how == "add" else (second, first)
    out = list(base)
    for b in more:
        if all(on_share(b.bbox, a.bbox) < 0.5 for a in base):
            out.append(b)
    return sorted(out, key=lambda b: b.bbox[0])


# ---------------------------------------------------------------- the whole thing

@dataclass
class Result:
    boxes: list                    # the answer
    first: list                    # the first pass's boxes (today's detector)
    second: list                   # the second pass's boxes
    mask1: np.ndarray
    mask2: np.ndarray
    seeds: list[Seed] = field(default_factory=list)
    info: dict = field(default_factory=dict)

    @property
    def kept(self) -> list[Seed]:
        return [s for s in self.seeds if s.ok]


class SelfCal:
    """The two-pass detector. ``model``: the fixed color model (an hs ``pipeline.Model``); ``cfg``: the numbers above;
    ``det_cfg`` / ``cam``: what ``detector.detect`` is called with."""

    def __init__(self, model: pl.Model, cfg: SelfCalConfig = SelfCalConfig(), cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT,
                 det_cfg: det.DetConfig | None = None):
        if model.cfg.color_model != "hs":
            raise ValueError(f"the fixed model must be an hs model, got {model.cfg.color_model!r}")
        self.model, self.cfg, self.cam = model, cfg, cam
        self.det_cfg = det_cfg or det.DetConfig()

    def first_pass(self, frame: pl.Frame) -> tuple[np.ndarray, list]:
        """Today's detector: the fixed model's mask and its boxes. Does not depend on ``cfg``."""
        mask1, _ = pl.segment(frame, self.model)
        return mask1, det.detect(mask1, self.det_cfg, self.cam)

    def run(self, frame: pl.Frame, extra: dict[int, list[Reading]] | None = None, first: tuple | None = None) -> Result:
        """One frame. ``extra``: readings from elsewhere, added to this frame's own for the frame ranges (report only:
        what carrying the colors across the frames of one session would give). None = strictly per frame. ``first``:
        the result of ``first_pass`` on this same frame, when the caller has it already (several settings on one
        frame); it is the same for every setting."""
        cfg = self.cfg
        mask1, first = first if first is not None else self.first_pass(frame)
        mask, boxes, seeds, info = mask1, first, [], {}
        for _ in range(max(1, cfg.rounds)):
            seeds = find_seeds(frame, mask, boxes, self.cam, cfg)
            kept = [s for s in seeds if s.ok]
            if not kept and not extra:
                break
            new_boxes, shares, rinfo = dict(self.model.boxes), {}, {}
            if cfg.frame:
                readings = class_readings(kept)
                for c, rs in (extra or {}).items():
                    readings[c] = readings[c] + list(rs)
                new_boxes, rinfo = frame_ranges(readings, self.model.boxes, cfg)
                new_boxes, shares = flood(frame, self.model, new_boxes, cfg, kept)
            mask = mask1 if new_boxes == self.model.boxes else pl.segment(frame, dataclasses.replace(self.model, boxes=new_boxes))[0]
            if cfg.local:
                mask = paint_local(frame, mask, kept)
            boxes = det.detect(mask, self.det_cfg, self.cam) if mask is not mask1 else first
            if cfg.seed_rules:
                # a kept seed says which barrel stands in its box: a second-pass box of the other color on it is dropped
                boxes = [b for b in boxes if not any(s.body != b.color and on_share(b.bbox, s.bbox) >= 0.5 for s in kept)]
            info = {"ranges": rinfo, "flood": shares,
                    "moved": [NAME[c] for c in (ORANGE, BLUE) if new_boxes[c] != self.model.boxes[c]]}
        second = boxes
        return Result(combine(first, second, cfg.combine), first, second, mask1, mask, seeds, info)

    def detect_frame(self, stem: str, frame: pl.Frame) -> list:
        return self.run(frame).boxes
