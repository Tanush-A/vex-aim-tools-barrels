"""Near-miss colors count next to strong evidence of a barrel (experiment 2026-11-26_nearmiss, TODO C2).

NOT part of what runs by default: nothing imports this module except the experiment
(``experiments/2026-11-26_nearmiss``) and its tests.

The fixed color step paints a pixel orange or blue when its hue and saturation are inside fixed ranges ("strict").
A barrel whose stripe or body reads just outside the range gets no box, because the detector needs both colors.
Loosening the ranges everywhere floods the picture. Here a pixel outside the strict range ("loose") is painted
only where a barrel's other color says it should be. Three ways to build the mask, all of them a strict superset of
the fixed mask (strict paint is never changed, pixels are never changed, only painted or not):

``hysteresis_mask``   the reference: a loose pixel counts when it is connected to strict pixels of its own color.
``partner_mask``      a loose pixel counts only beside the PARTNER color:
    direction 1, the stripe: loose stripe-colored pixels in a gap of stripe height between two strict body pieces
                 in the same column (``stripe_slots``);
    direction 2, the body: loose body-colored pixels right above or below a strict stripe-colored band of stripe
                 size for its row, inside the barrel box that row predicts (``stripe_bands``, ``body_fill``).

How loose "loose" is comes from a ladder of levels (``LADDER``, 0 to 5): each level widens the hue sector, lowers
the saturation floor and lowers the brightness floor. Each direction then has levels with no color range at all:
the stripe direction (``STRIPE_LADDER``) ends in "anything" (6): any pixel that is clearly not the body color. The
body direction (``BODY_LADDER``) goes on with "darker than the ground" (6): the widest range, or any pixel that is
not stripe-colored and clearly darker than the ground beside the barrel; and "anything" (7): any pixel that is not
stripe-colored, in the band's own columns.

The bottom edge (``NearMissConfig.bottom``). Shadow and reflection sit under a barrel, and loose paint there moves
the box bottom. "strict": where strict body color is seen below the band, loose paint stops at its lowest row; where
there is none, it stops at the bottom the stripe's row predicts. The top is treated the same way (what stands behind
a barrel shows right above it). "pred": always the predicted top and bottom. "free": the predicted rows plus the
detector's own tolerance (no protection; kept to measure what the protection is worth).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache

import cv2
import numpy as np

from . import geometry as geo
from . import pipeline as pl
from .io import BLUE, ORANGE, OTHER

OTHER_COLOR = {ORANGE: BLUE, BLUE: ORANGE}
BOTTOM_MODES = ("strict", "pred", "free")


@dataclass(frozen=True)
class Level:
    """How far outside the strict range a loose pixel may be: hue units added on each side of the class's hue
    sector, saturation units taken off its floor, and the brightness floor (the strict one is 40)."""
    name: str
    dh: float = 0.0
    ds: float = 0.0
    v_min: int = 40
    kind: str = "range"             # "range": a color range | "dark": that range, or darker than the ground | "anything": no color test

    @property
    def anything(self) -> bool:
        return self.kind == "anything"


LADDER: tuple[Level, ...] = (
    Level("off"),                                   # 0: strict only
    Level("near", 3, 20, 40),                       # 1
    Level("loose", 6, 40, 25),                      # 2: the audit's "everything loosened"
    Level("looser", 10, 60, 25),                    # 3
    Level("wide", 15, 80, 20),                      # 4
    Level("very wide", 25, 100, 15),                # 5: orange S >= 40, blue S >= 13 (almost gray)
)
RANGE_MAX = len(LADDER) - 1                         # the last level that is a color range
STRIPE_LADDER: tuple[Level, ...] = LADDER + (Level("anything", kind="anything"),)
BODY_LADDER: tuple[Level, ...] = LADDER + (Level("darker than the ground", 25, 100, 15, kind="dark"), Level("anything", kind="anything"))
STRIPE_ANY = len(STRIPE_LADDER) - 1                 # 6
BODY_DARK, BODY_ANY = len(BODY_LADDER) - 2, len(BODY_LADDER) - 1      # 6, 7
ANY_REF = 2                                         # "clearly not that color" = not inside that color's level-2 range


@dataclass(frozen=True)
class NearMissConfig:
    stripe_level: int = 0           # direction 1: index into STRIPE_LADDER (0 = off)
    body_level: int = 0             # direction 2: index into BODY_LADDER (0 = off)
    bottom: str = "strict"          # direction 2: how far down (and up) loose body paint may go (module docstring)
    # direction 1: what "a gap of stripe height between two strong body pieces" means (fixed, never tuned)
    slot_max: float = 2.0           # the gap is at most this x the stripe height its row predicts
    run_min: float = 0.75           # the body piece above and the one below are each at least this x that height tall, in that column
    slot_w_min: int = 3             # a slot narrower than this many columns is dropped
    # direction 2: what "a band of plausible stripe size for its row" means (the detector's own numbers where it has one)
    min_area_px: int = 20           # DetConfig.min_area_px
    min_width_px: float = 16.0      # DetConfig.min_width_px: rows where a barrel would be narrower hold no barrel
    band_h_min: float = 0.45        # DetConfig.stripe_h_min
    band_h_max: float = 1.6         # DetConfig.stripe_h_max
    band_w_min: float = 0.5         # at least half a barrel wide: strong evidence, not a speck
    band_w_max: float = 1.2         # DetConfig.body_width
    own_max: float = 0.25           # a band with more than this share of its OWN color in the body rows above or below it is part of a
                                    # thing of its own color (the lower body of a barrel of that color), not a stripe
    own_slot: float = 0.5           # ... and so is a band that, in this share of its columns, is one of the two pieces around a stripe
                                    # slot of its own color (``stripe_slots``): it is the upper or lower body of a barrel of that color
    edge_tol: float = 0.15          # DetConfig.bottom_tol: with "free", paint may pass the predicted top and bottom by this x height
    edge_tol_min_px: int = 4        # DetConfig.bottom_tol_min_px
    runs_on: float = 0.5            # the body color that goes on above where the barrel's top must be is what stands behind the barrel,
                                    # not its body: when, in this share of the band's columns, the allowed color fills the rows from two
                                    # tolerances to one tolerance above the predicted top, nothing is painted above the band. 0 = off
    cover_min: float = 0.5          # loose paint must complete a body: a side (above / below the band) is painted only when strict and
                                    # loose body color together then cover this share of the band's columns x the predicted body rows
                                    # of that side. 0 = off
    side_pad: float = 0.1           # loose body paint may reach this x a barrel width past where a barrel holding the band can end
    seed_gap: int = 3               # "right above or below": within this many rows of the band (the detector's body walk allows 3)
    # the "darker than the ground" body level
    dark_ratio: float = 0.6         # clearly darker = brightness under this x the ground's (a blue body under a warm lamp reads 0.3,
                                    # a well-lit blue body on a white table 0.8 to 1.0: experiments/2026-11-26_nearmiss/look_body.py)
    ground_pad: float = 0.25        # the ground = the strips this x a barrel width wide left and right of where the barrel can be,
                                    # beside its lower half, strict paint left out
    ground_min_px: int = 20         # fewer ground pixels than this: no ground reading, the level falls back to its color range

    def __post_init__(self):
        for name, top in (("stripe_level", STRIPE_ANY), ("body_level", BODY_ANY)):
            v = getattr(self, name)
            if not (isinstance(v, int) and 0 <= v <= top):
                raise ValueError(f"{name} must be an int 0..{top}, got {v!r}")
        if self.bottom not in BOTTOM_MODES:
            raise ValueError(f"bottom must be one of {BOTTOM_MODES}, got {self.bottom!r}")


# ---------------------------------------------------------------- loose colors

def strict_mask(frame: pl.Frame, model: pl.Model) -> np.ndarray:
    """The fixed color step's mask (0 other, 1 orange, 2 blue): ``pipeline.segment``, nothing else."""
    return pl.segment(frame, model)[0]


def loose_class(frame: pl.Frame, model: pl.Model, color: int, level: Level) -> np.ndarray:
    """Pixels inside ``color``'s range widened by ``level`` (bool). The horizon gate of the model stays. Strict
    pixels of that color are inside it at every level of the ladder. Not defined for the "anything" level;
    for the "dark" level it is that level's color range alone."""
    if level.anything:
        raise ValueError("the 'anything' level has no color range of its own")
    cfg, box, shift = model.cfg, model.boxes[color], pl.HUE_SHIFT[color]
    h_lo, h_hi, s_lo = box.lo[0] - level.dh, box.hi[0] + level.dh, box.lo[1] - level.ds
    if h_lo < 0 or h_hi >= 180:
        raise ValueError(f"level {level.name!r} takes the hue sector of class {color} past the wrap ({h_lo}..{h_hi}, shifted by {shift})")
    hs = frame.hs(shift)
    out = (frame.val >= min(level.v_min, cfg.v_min)) & (hs[..., 0] >= h_lo) & (hs[..., 0] <= h_hi) & (hs[..., 1] >= s_lo)
    if cfg.horizon_row is not None:
        out[: max(0, cfg.horizon_row)] = False
    return out


def _tie(frame: pl.Frame, add: dict[int, np.ndarray]) -> None:
    """A pixel both colors claim goes to orange when it is redder than blue (the model's own tie rule). In place."""
    both = add[ORANGE] & add[BLUE]
    if both.any():
        orange_wins = frame.rgb[..., 0] > frame.rgb[..., 2]
        add[ORANGE] &= ~both | orange_wins
        add[BLUE] &= ~both | ~orange_wins


def _painted(strict: np.ndarray, add: dict[int, np.ndarray]) -> np.ndarray:
    out = strict.copy()
    free = strict == OTHER
    out[add[ORANGE] & free] = ORANGE
    out[add[BLUE] & free] = BLUE
    return out


# ---------------------------------------------------------------- the reference: plain two-level thresholds

def hysteresis_mask(frame: pl.Frame, model: pl.Model, level: int, guard_bottom: bool = False,
                    strict: np.ndarray | None = None) -> np.ndarray:
    """Strict paint, plus every loose pixel (``LADDER[level]``) that is connected (8 neighbours) to strict pixels of
    its own color through loose or strict pixels of that color. ``guard_bottom``: a loose pixel lower than the
    lowest strict pixel of the piece it joins is not painted (loose paint cannot move a piece's bottom down)."""
    if not (isinstance(level, int) and 0 <= level <= RANGE_MAX):
        raise ValueError(f"level must be an int 0..{RANGE_MAX}, got {level!r}")
    strict = strict_mask(frame, model) if strict is None else strict
    if level == 0:
        return strict.copy()
    rows = np.arange(strict.shape[0])[:, None]
    add = {}
    for c in pl.CLASSES:
        seed = strict == c
        loose = loose_class(frame, model, c, LADDER[level]) & (strict == OTHER)
        n, lab = cv2.connectedComponents((seed | loose).astype(np.uint8), connectivity=8)
        seeded = np.zeros(n, bool)
        seeded[lab[seed]] = True
        seeded[0] = False
        keep = seeded[lab] & loose
        if guard_bottom:
            lowest = np.full(n, -1, np.int64)
            np.maximum.at(lowest, lab[seed], np.broadcast_to(rows, strict.shape)[seed])
            keep &= rows <= lowest[lab]
        add[c] = keep
    _tie(frame, add)
    return _painted(strict, add)


# ---------------------------------------------------------------- geometry: what a stripe at a row implies

def stripe_geometry(cam: geo.CameraModel, center_row: float):
    """(axis distance, BarrelRows) of a barrel whose stripe centre is at ``center_row``; None when no barrel can
    have its stripe there. The same reading as the detector's."""
    d = cam._d_axis_from_point_row(center_row, geo.BARREL_HEIGHT_MM / 2, -geo.BARREL_BULGE_DIAMETER_MM / 2)
    if not math.isfinite(d) or d <= geo.BARREL_BULGE_DIAMETER_MM / 2 + 1:
        return None
    return d, cam.barrel_rows(d)


@lru_cache(maxsize=8)
def stripe_height_by_row(cam: geo.CameraModel, h: int, min_width_px: float = 16.0) -> np.ndarray:
    """For every image row: the height in pixels of a stripe centred there; -1 where no barrel can have its stripe
    (at or above the horizon, or so far that the barrel is narrower than ``min_width_px``)."""
    out = np.full(h, -1.0)
    for r in range(h):
        g = stripe_geometry(cam, r + 0.5)
        if g is not None and g[1].width_px >= min_width_px:
            out[r] = g[1].stripe_bottom - g[1].stripe_top
    out.setflags(write=False)
    return out


def _closed3(m: np.ndarray) -> np.ndarray:
    """Gaps of one pixel filled (3 x 3 closing), as the detector closes a color before it looks for stripes."""
    return cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)).astype(bool)


# ---------------------------------------------------------------- direction 1: the stripe between two body pieces

def stripe_slots(body: np.ndarray, stripe_h: np.ndarray, cfg: NearMissConfig = NearMissConfig()) -> np.ndarray:
    """Where a stripe should be, given strict body color ``body`` (bool): the non-body pixels that, in their own
    column, lie in a gap between a body piece above and a body piece below, the gap at most ``slot_max`` x the
    stripe height their row predicts (``stripe_h``, per row) and each of the two pieces at least ``run_min`` x that
    height tall. Slots narrower than ``slot_w_min`` columns are dropped."""
    h, w = body.shape
    rows = np.arange(h)[:, None]
    up = np.maximum.accumulate(np.where(body, rows, -1), axis=0)                   # last body row at or above
    dn = np.minimum.accumulate(np.where(body, rows, h)[::-1], axis=0)[::-1]        # first body row at or below
    last_non = np.maximum.accumulate(np.where(~body, rows, -1), axis=0)            # last non-body row at or above
    next_non = np.minimum.accumulate(np.where(~body, rows, h)[::-1], axis=0)[::-1]
    run_up = rows - last_non                                                       # on a body pixel: the run that ends here, going up
    run_dn = next_non - rows                                                       # ... the run that starts here, going down
    has = ~body & (up >= 0) & (dn < h)
    above = np.take_along_axis(run_up, np.clip(up, 0, h - 1), axis=0)
    below = np.take_along_axis(run_dn, np.clip(dn, 0, h - 1), axis=0)
    hs = stripe_h[:, None]
    slot = has & (hs > 0) & ((dn - up - 1) <= cfg.slot_max * hs) & (above >= cfg.run_min * hs) & (below >= cfg.run_min * hs)
    if cfg.slot_w_min > 1:
        slot = cv2.morphologyEx(slot.astype(np.uint8), cv2.MORPH_OPEN, np.ones((1, cfg.slot_w_min), np.uint8)).astype(bool)
    return slot


# ---------------------------------------------------------------- direction 2: the body around a stripe-sized band

@dataclass(frozen=True)
class Band:
    """A strict piece of one color that has the size of a stripe for its row, and the barrel that row predicts."""
    color: int                          # the band's own color (the stripe color); the body it asks for is the other one
    label: int                          # its number in the label image ``stripe_bands`` returns
    bbox: tuple[int, int, int, int]     # half-open
    center_row: float
    width_px: float                     # the barrel's expected width
    top: float                          # the barrel's predicted top row
    bottom: float                       # ... and bottom row


def stripe_bands(strict: np.ndarray, color: int, cam: geo.CameraModel, cfg: NearMissConfig = NearMissConfig()) -> tuple[list[Band], np.ndarray]:
    """The strict pieces of ``color`` that could be a barrel's stripe by size alone: at least ``min_area_px``, at a
    row where a barrel can stand, ``band_h_min`` to ``band_h_max`` x the expected stripe height tall (10th to 90th
    percentile of its rows, as the detector measures a stripe), ``band_w_min`` to ``band_w_max`` x the expected
    barrel width wide, without its own color in the body rows above and below it (``own_max``), and not one of the
    two body pieces around a stripe slot of its own color (``own_slot``). Returns the bands and the label image of
    the pieces."""
    h, w = strict.shape
    own = _closed3(strict == color)
    n, lab, st, _ = cv2.connectedComponentsWithStats(own.astype(np.uint8), connectivity=8)
    # the stripe slots of a barrel whose BODY has this color, grown so that they touch the two body pieces around them
    near_slot = cv2.dilate(stripe_slots(own, stripe_height_by_row(cam, h, cfg.min_width_px), cfg).astype(np.uint8),
                           np.ones((2 * cfg.seed_gap + 1, 1), np.uint8)) > 0
    bands = []
    for i in range(1, n):
        x, y, bw, bh, area = (int(v) for v in st[i])
        if area < cfg.min_area_px:
            continue
        ys = np.where(lab[y:y + bh, x:x + bw] == i)[0] + y
        center = float(np.median(ys)) + 0.5
        g = stripe_geometry(cam, center)
        if g is None:
            continue
        rows = g[1]
        W, Hs = rows.width_px, rows.stripe_bottom - rows.stripe_top
        if W < cfg.min_width_px:
            continue
        core_h = np.percentile(ys, 90) - np.percentile(ys, 10) + 1
        if not (cfg.band_h_min * Hs <= core_h <= cfg.band_h_max * Hs) or not (cfg.band_w_min * W <= bw <= cfg.band_w_max * W):
            continue
        t, b = max(0, int(round(rows.top))), min(h, int(round(rows.bottom)))
        above, below = strict[t:y, x:x + bw], strict[y + bh:b, x:x + bw]
        if any(part.size and float((part == color).mean()) > cfg.own_max for part in (above, below)):
            continue
        piece = lab[y:y + bh, x:x + bw] == i
        if float((piece & near_slot[y:y + bh, x:x + bw]).any(axis=0).mean()) >= cfg.own_slot:
            continue
        bands.append(Band(color, i, (x, y, x + bw, y + bh), center, W, rows.top, rows.bottom))
    return bands, lab


def _strict_bottom(body: np.ndarray, x0: int, x1: int, y1: int, max_gap: int) -> int:
    """The lowest row + 1 of body color seen walking down from row ``y1`` in columns x0..x1 (gaps of up to
    ``max_gap`` rows allowed); ``y1`` when there is none. The detector's own walk."""
    col = body[:, x0:x1].any(axis=1)
    bottom, gap, r = y1, 0, y1
    while r < len(col) and gap <= max_gap:
        if col[r]:
            bottom, gap = r + 1, 0
        else:
            gap += 1
        r += 1
    return bottom


def _strict_top(body: np.ndarray, x0: int, x1: int, y0: int, max_gap: int) -> int:
    """The highest row of body color seen walking up from row ``y0`` in columns x0..x1; ``y0`` when there is none."""
    col = body[:, x0:x1].any(axis=1)
    top, gap, r = y0, 0, y0 - 1
    while r >= 0 and gap <= max_gap:
        if col[r]:
            top, gap = r, 0
        else:
            gap += 1
        r -= 1
    return top


def body_window(band: Band, strict: np.ndarray, cfg: NearMissConfig = NearMissConfig(), anything: bool = False,
                horizon: int = 0) -> tuple[int, int, int, int]:
    """(x0, y0, x1, y1), half-open: where loose body paint may go for this band. Rows: between the top and bottom
    limits of ``cfg.bottom`` (module docstring). Columns: every place a barrel that holds the band can be, plus
    ``side_pad``; with ``anything`` the band's own columns only."""
    h, w = strict.shape
    x0, y0, x1, y1 = band.bbox
    H = band.bottom - band.top
    tol = max(cfg.edge_tol_min_px, cfg.edge_tol * H)
    pred_top, pred = int(round(band.top)), int(round(band.bottom))
    if cfg.bottom == "free":
        top, bot = int(math.floor(band.top - tol)), int(math.ceil(band.bottom + tol))
    elif cfg.bottom == "pred":
        top, bot = pred_top, pred
    else:
        body = strict == OTHER_COLOR[band.color]
        seen_top = _strict_top(body, x0, x1, y0, cfg.seed_gap)
        top = max(seen_top, pred_top) if seen_top < y0 else pred_top
        seen = _strict_bottom(body, x0, x1, y1, cfg.seed_gap)
        bot = min(seen, pred) if seen > y1 else pred
    top = min(y0, max(horizon, 0, top))
    bot = max(y1, min(h, bot))
    if anything:
        return x0, top, x1, bot
    reach = (1.0 + cfg.side_pad) * band.width_px
    return max(0, int(math.floor(x1 - reach))), top, min(w, int(math.ceil(x0 + reach))), bot


def ground_value(val: np.ndarray, strict: np.ndarray, band: Band, cfg: NearMissConfig = NearMissConfig(), horizon: int = 0) -> float | None:
    """The brightness of the ground beside the barrel a band predicts: the median brightness (max channel) of the
    pixels in two strips, ``ground_pad`` x a barrel width wide, left and right of every place the barrel can be,
    from the band's top row down to the predicted bottom; strict paint (other barrels) left out. None when fewer
    than ``ground_min_px`` such pixels exist."""
    h, w = strict.shape
    x0, y0, x1, _ = band.bbox
    lo, hi = int(math.floor(x1 - band.width_px)), int(math.ceil(x0 + band.width_px))
    pad = max(2, int(round(cfg.ground_pad * band.width_px)))
    r0, r1 = max(horizon, 0, y0), min(h, int(round(band.bottom)))
    if r1 <= r0:
        return None
    parts = []
    for a, b in ((lo - pad, lo), (hi, hi + pad)):
        a, b = max(0, a), max(0, min(w, b))
        parts.append(val[r0:r1, a:b][strict[r0:r1, a:b] == OTHER])
    px = np.concatenate(parts)
    return float(np.median(px)) if len(px) >= cfg.ground_min_px else None


def body_fill(strict: np.ndarray, allowed: np.ndarray, body: int, cam: geo.CameraModel,
              cfg: NearMissConfig = NearMissConfig(), anything: bool = False, horizon: int = 0,
              dark: tuple[np.ndarray, np.ndarray] | None = None) -> tuple[np.ndarray, list[Band]]:
    """Loose body paint for body color ``body``: for every stripe-sized strict band of the other color, the
    ``allowed`` pixels inside its window (``body_window``) that are joined to the band, starting right above or
    right below it (within ``seed_gap`` rows, in the band's own columns). Nothing is painted above a band whose
    body color runs on above the predicted top (``runs_on``), and a side is painted only when the paint completes a
    body there (``cover_min``). ``dark`` = (brightness, pixels that may count as dark): per band, the pixels of the
    second array that are darker than ``dark_ratio`` x the ground beside that band (``ground_value``) are allowed
    too. Returns (bool mask, the bands)."""
    bands, lab = stripe_bands(strict, OTHER_COLOR[body], cam, cfg)
    h, w = strict.shape
    paint = np.zeros(strict.shape, bool)
    free = strict == OTHER
    is_body = strict == body
    k = np.ones((2 * cfg.seed_gap + 1, 1), np.uint8)
    everywhere = allowed
    for b in bands:
        allowed = everywhere
        if dark is not None:
            ground = ground_value(dark[0], strict, b, cfg, horizon)
            if ground is not None:
                allowed = everywhere | (dark[1] & (dark[0] < cfg.dark_ratio * ground))
        x0, y0, x1, y1 = body_window(b, strict, cfg, anything, horizon)
        bx0, by0, bx1, by1 = b.bbox
        pred_top, pred_bot = max(0, int(round(b.top))), min(h, int(round(b.bottom)))
        if cfg.runs_on > 0 and not anything:
            tol = max(cfg.edge_tol_min_px, cfg.edge_tol * (b.bottom - b.top))
            r0, r1 = int(math.floor(b.top - 2 * tol)), int(math.floor(b.top - tol))
            beyond = allowed[max(0, r0):max(0, r1), bx0:bx1]
            if beyond.shape[0] and float((beyond.mean(axis=0) >= 0.5).mean()) >= cfg.runs_on:
                y0 = by0                                            # the color runs on above the barrel's top: background
        if x1 <= x0 or y1 <= y0:
            continue
        win = allowed[y0:y1, x0:x1]
        seed = cv2.dilate((lab[y0:y1, x0:x1] == b.label).astype(np.uint8), k) > 0
        n, comp = cv2.connectedComponents(win.astype(np.uint8), connectivity=8)
        ids = np.unique(comp[seed & win])
        keep = np.zeros(n, bool)
        keep[ids] = True
        keep[0] = False
        mine = np.zeros(strict.shape, bool)
        mine[y0:y1, x0:x1] = keep[comp]
        mine &= free
        if cfg.cover_min > 0:
            for ra, rb in ((pred_top, by0), (by1, pred_bot)):       # above the band, below the band
                side = (mine | is_body)[ra:rb, bx0:bx1]
                if side.size and float(side.mean()) < cfg.cover_min:
                    if ra == pred_top:
                        mine[:by0] = False
                    else:
                        mine[by1:] = False
        paint |= mine
    return paint, bands


# ---------------------------------------------------------------- the partner-conditioned mask

def partner_mask(frame: pl.Frame, model: pl.Model, cfg: NearMissConfig = NearMissConfig(),
                 cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT, strict: np.ndarray | None = None) -> tuple[np.ndarray, dict]:
    """The fixed mask plus loose pixels that sit where a barrel's partner color says they should (module
    docstring). Returns (mask, info); ``info`` counts the pixels each direction painted per color and the bands.
    The picture is only read."""
    strict = strict_mask(frame, model) if strict is None else strict
    h, w = strict.shape
    horizon = max(0, model.cfg.horizon_row or 0)
    free = strict == OTHER
    add = {c: np.zeros(strict.shape, bool) for c in pl.CLASSES}
    info: dict = {"stripe_px": {}, "body_px": {}, "bands": {}}
    stripe_h = stripe_height_by_row(cam, h, cfg.min_width_px)
    s_lvl, b_lvl = STRIPE_LADDER[cfg.stripe_level], BODY_LADDER[cfg.body_level]
    ref = {c: loose_class(frame, model, c, LADDER[ANY_REF]) for c in pl.CLASSES} if (s_lvl.kind != "range" or b_lvl.kind != "range") else {}
    for body in pl.CLASSES:
        other = OTHER_COLOR[body]
        if cfg.stripe_level:
            lvl = s_lvl
            slots = stripe_slots(_closed3(strict == body), stripe_h, cfg)
            slots[:horizon] = False
            ok = ~ref[body] if lvl.anything else loose_class(frame, model, other, lvl)      # anything that is clearly not the body color
            p = slots & ok & free
            add[other] |= p
            info["stripe_px"][other] = int(p.sum())
        if cfg.body_level:
            lvl = b_lvl
            not_stripe = (strict != other) & ~ref[other] if lvl.kind != "range" else None    # anything that is not stripe-colored
            if lvl.anything:
                allowed = not_stripe
            else:
                allowed = loose_class(frame, model, body, lvl) | (strict == body)
            allowed[:horizon] = False
            dark = None
            if lvl.kind == "dark":
                not_stripe[:horizon] = False
                dark = (frame.val, not_stripe)
            p, bands = body_fill(strict, allowed, body, cam, cfg, lvl.anything, horizon, dark)
            add[body] |= p
            info["body_px"][body] = int(p.sum())
            info["bands"][body] = len(bands)
    _tie(frame, add)
    return _painted(strict, add), info
