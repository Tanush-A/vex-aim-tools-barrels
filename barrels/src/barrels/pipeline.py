"""v1 barrel segmentation pipeline (docs/PROBLEM.md): per-pixel gates + per-image priors +
per-class color boxes fit on labeled training pixels.

Stages (each a config flag; off = no-op, so ablations are just configs):
    horizon gate -> brightness gate -> table prior -> background prior
    -> per class: saturation floor AND inside the class box -> tie rule -> mask {0,1,2}

No image correction anywhere: pixel values are never rescaled; the priors compare pixels to
band statistics and the boxes are fixed thresholds. Frames with no barrels need no special
handling because the boxes come from the training fold, never from the frame itself.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, replace

import numpy as np

from . import boxfit as bf
from . import priors
from .io import BLUE, ORANGE, OTHER

CLASSES = (ORANGE, BLUE)


@dataclass(frozen=True)
class RefitConfig:
    """v1.5: barrel-referenced re-fit of the class boxes inside each image."""
    inner_pct: tuple[float, float] = (10.0, 90.0)   # train-fold "high-confidence" inner box
    min_px: int = 300                               # fewer confident pixels -> keep the v1 box
    pct: tuple[float, float] = (1.0, 99.0)          # percentile box of the confident in-image pixels
    margin_scale: float = 1.0                       # dilate by margin_scale * MAD per channel
    outer_pct: tuple[float, float] = (0.1, 99.9)    # train-fold box the refit may never exceed
    n_iter: int = 2


@dataclass(frozen=True)
class Config:
    # geometry
    horizon_row: int | None = 50            # rows above are never barrel; None = gate off
    bg_rows: tuple[int, int] = (0, 50)      # background prior band
    table_rows: int = 80                    # table prior band = bottom N rows
    # pixel gates
    s_min: int = 40                         # saturation floor (max-min), orange and default for blue
    s_min_blue: int | None = None           # per-class override; None = s_min
    v_min: int = 40                         # brightness floor (max channel)
    s_min_mode: str = "fixed"               # "fixed" | "band": floor = percentile of the known-background band's saturation + margin, per image
    s_band_q: float = 99.5                  # band mode: percentile of band saturation
    s_band_margin: float = 10.0             # band mode: added on top of that percentile
    s_band_source: str = "bg"               # band mode: "bg" (rows above the horizon only) | "both" (bg + bottom table rows)
    s_min_lo: int = 20                      # band mode: clamp
    s_min_hi: int = 120
    # priors
    table_prior: bool = True
    bg_prior: bool = True
    k_table: float = 3.0
    k_bg: float = 3.0
    prior_fit: str = "lowsat"               # "lowsat": fit band stats on band pixels with sat < s_min; "all"
    scale_floor: float = 4.0
    prior_min_frac: float = 0.3
    # class boxes
    box_space: str = "rgb"                  # "rgb" | "yuv_chroma" (v1.5)
    box_pct: tuple[float, float] = (1.0, 99.0)
    fit_after_gates: bool = True            # sample training pixels after horizon/v_min/s_min gates
    fit_max_px_per_image: int | None = 3000
    tie: str = "rb_sign"                    # pixel in both boxes: "rb_sign" (R>B -> orange) | "orange" | "blue"
    seed: int = 0
    refit: RefitConfig | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Config":
        d = dict(d)
        for key in ("bg_rows", "box_pct"):
            if key in d and d[key] is not None:
                d[key] = tuple(d[key])
        if d.get("refit") is not None:
            r = dict(d["refit"])
            for key in ("inner_pct", "pct", "outer_pct"):
                r[key] = tuple(r[key])
            d["refit"] = RefitConfig(**r)
        return cls(**d)

    def short_hash(self) -> str:
        return hashlib.sha1(json.dumps(self.to_dict(), sort_keys=True).encode()).hexdigest()[:8]

    def s_min_for(self, cls: int) -> int:
        return self.s_min_blue if (cls == BLUE and self.s_min_blue is not None) else self.s_min


@dataclass
class Frame:
    """Per-image features computed once (BGR in, everything else derived)."""
    bgr: np.ndarray
    rgb: np.ndarray      # HxWx3 int16, RGB order
    sat: np.ndarray      # HxW int16, max - min
    val: np.ndarray      # HxW int16, max channel
    uv: np.ndarray | None = None   # HxWx2 float32 YUV chroma, lazily built

    @classmethod
    def from_image(cls, bgr: np.ndarray) -> "Frame":
        rgb = bgr[..., ::-1].astype(np.int16)
        return cls(bgr=bgr, rgb=rgb, sat=(rgb.max(-1) - rgb.min(-1)).astype(np.int16), val=rgb.max(-1).astype(np.int16))

    @property
    def shape(self) -> tuple[int, int]:
        return self.rgb.shape[:2]

    def features(self, space: str) -> np.ndarray:
        if space == "rgb":
            return self.rgb
        if space == "yuv_chroma":
            if self.uv is None:
                self.uv = rgb_to_uv(self.rgb)
            return self.uv
        raise ValueError(f"unknown box_space {space!r}")


def rgb_to_uv(rgb: np.ndarray) -> np.ndarray:
    """8-bit YUV chroma (U = blueness, V = redness), Dave's slides (NAVIGATOR.md K-1)."""
    r, g, b = [rgb[..., i].astype(np.float32) for i in range(3)]
    u = (-37.945 * r - 74.494 * g + 112.439 * b) / 256 + 128
    v = (112.439 * r - 94.154 * g - 18.285 * b) / 256 + 128
    return np.stack([u, v], -1)


@dataclass
class Model:
    cfg: Config
    boxes: dict[int, bf.Box]                 # class -> box in cfg.box_space
    inner: dict[int, bf.Box] = field(default_factory=dict)   # refit: high-confidence boxes
    outer: dict[int, bf.Box] = field(default_factory=dict)   # refit: never exceed
    fit_info: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"cfg": self.cfg.to_dict(), "boxes": {str(c): b.to_dict() for c, b in self.boxes.items()},
                "inner": {str(c): b.to_dict() for c, b in self.inner.items()},
                "outer": {str(c): b.to_dict() for c, b in self.outer.items()}, "fit_info": self.fit_info}


# ---------------------------------------------------------------- gates

def effective_s_min(frame: Frame, cfg: Config) -> tuple[dict[int, int], dict]:
    """Per-class saturation floor for this frame. "fixed": the config constants. "band": the
    cfg.s_band_q percentile of the saturation of the frame's own known-non-barrel rows (above the
    horizon, optionally plus the bottom table rows) plus a margin, clamped to [s_min_lo, s_min_hi]
    — the floor adapts to how colorful this image's background is, no pixel is ever changed."""
    if cfg.s_min_mode == "fixed":
        return {ORANGE: cfg.s_min, BLUE: cfg.s_min_for(BLUE)}, {"s_min_mode": "fixed", "s_min_eff": cfg.s_min}
    h = frame.shape[0]
    parts = [frame.sat[cfg.bg_rows[0]:cfg.bg_rows[1]].ravel()]
    if cfg.s_band_source == "both":
        parts.append(frame.sat[max(0, h - cfg.table_rows):h].ravel())
    band = np.concatenate(parts)
    base = float(np.percentile(band, cfg.s_band_q)) if band.size else float(cfg.s_min)
    s_eff = int(round(min(max(base + cfg.s_band_margin, cfg.s_min_lo), cfg.s_min_hi)))
    return {ORANGE: s_eff, BLUE: s_eff}, {"s_min_mode": "band", "band_sat_pct": base, "s_min_eff": s_eff}


def _fixed_keep(frame: Frame, cfg: Config) -> np.ndarray:
    """Pixels surviving the content-independent gates (horizon + brightness)."""
    keep = frame.val >= cfg.v_min
    if cfg.horizon_row is not None:
        keep[: max(0, cfg.horizon_row)] = False
    return keep


def _prior_keep(frame: Frame, cfg: Config, info: dict, s_floor: int) -> np.ndarray:
    """Pixels NOT rejected by the table/background priors; records BandStats in info."""
    h = frame.shape[0]
    keep = np.ones(frame.shape, bool)
    fit_mask = (frame.sat < s_floor) if cfg.prior_fit == "lowsat" else None
    for name, on, rows, k in (("table", cfg.table_prior, slice(max(0, h - cfg.table_rows), h), cfg.k_table),
                              ("bg", cfg.bg_prior, slice(cfg.bg_rows[0], cfg.bg_rows[1]), cfg.k_bg)):
        if not on:
            info[name] = None
            continue
        st = priors.band_stats(frame.rgb, rows, fit_mask=fit_mask, scale_floor=cfg.scale_floor, min_frac=cfg.prior_min_frac)
        rej = priors.reject_like(frame.rgb, st, k)
        info[name] = st.to_dict() | {"rejected_frac": float(rej.mean())}
        keep &= ~rej
    return keep


# ---------------------------------------------------------------- fit

def fit(frames: list[Frame], masks: list[np.ndarray], cfg: Config) -> Model:
    """Fit the per-class boxes on labeled training frames (pixels sampled after the fixed gates
    when cfg.fit_after_gates, capped per image so no frame dominates)."""
    rng = np.random.default_rng(cfg.seed)
    samples: dict[int, list[np.ndarray]] = {c: [] for c in CLASSES}
    for frame, mask in zip(frames, masks):
        feats = frame.features(cfg.box_space)
        base_keep = _fixed_keep(frame, cfg) if cfg.fit_after_gates else None
        smin, _ = effective_s_min(frame, cfg)
        for c in CLASSES:
            keep = None
            if cfg.fit_after_gates:
                keep = base_keep & (frame.sat >= smin[c])
            samples[c].append(bf.sample_class_pixels(feats, mask, c, keep=keep, max_px=cfg.fit_max_px_per_image, rng=rng))
    boxes, inner, outer, info = {}, {}, {}, {}
    for c in CLASSES:
        px = np.concatenate(samples[c]) if samples[c] else np.zeros((0, 3))
        if len(px) == 0:
            raise ValueError(f"no training pixels for class {c}")
        boxes[c] = bf.fit_box(px, *cfg.box_pct)
        info[str(c)] = {"n_px": int(len(px)), "box": boxes[c].to_dict(),
                        "fullness8": bf.fullness(px, boxes[c], 8), "pca": bf.pca(px) if px.shape[1] >= 2 else None}
        if cfg.refit is not None:
            inner[c] = bf.fit_box(px, *cfg.refit.inner_pct)
            outer[c] = bf.fit_box(px, *cfg.refit.outer_pct)
    return Model(cfg=cfg, boxes=boxes, inner=inner, outer=outer, fit_info=info)


# ---------------------------------------------------------------- segment

def _refit_box(feats: np.ndarray, cand: np.ndarray, model: Model, c: int, info: dict) -> bf.Box:
    """v1.5: re-fit class c's box to this image's high-confidence pixels (inside the inner box)."""
    rc = model.cfg.refit
    box = model.boxes[c]
    used = False
    for _ in range(rc.n_iter):
        conf = cand & bf.in_box(feats, model.inner[c]) & bf.in_box(feats, box)
        n = int(conf.sum())
        if n < rc.min_px:
            break
        px = feats[conf]
        new = bf.fit_box(px, *rc.pct)
        mad = np.median(np.abs(px - np.median(px, axis=0)), axis=0) * priors.MAD_TO_SIGMA
        new = bf.Box(tuple((np.array(new.lo) - rc.margin_scale * mad).tolist()), tuple((np.array(new.hi) + rc.margin_scale * mad).tolist()))
        box = new.clip_to(model.outer[c])
        used = True
    info.setdefault("refit", {})[str(c)] = {"used": used, "box": box.to_dict()}
    return box


def segment(frame: Frame, model: Model) -> tuple[np.ndarray, dict]:
    """Returns (mask uint8 {OTHER, ORANGE, BLUE}, info dict with per-stage survivor counts)."""
    cfg = model.cfg
    info: dict = {}
    keep = _fixed_keep(frame, cfg)
    info["after_fixed_gates"] = int(keep.sum())
    smin, s_info = effective_s_min(frame, cfg)
    info.update(s_info)
    keep &= _prior_keep(frame, cfg, info, smin[ORANGE])
    info["after_priors"] = int(keep.sum())
    feats = frame.features(cfg.box_space)
    cand = {}
    for c in CLASSES:
        base = keep & (frame.sat >= smin[c])
        box = model.boxes[c]
        if cfg.refit is not None and model.inner:
            box = _refit_box(feats, base, model, c, info)
        cand[c] = base & bf.in_box(feats, box)
        info[f"cand_{c}"] = int(cand[c].sum())
    both = cand[ORANGE] & cand[BLUE]
    info["both"] = int(both.sum())
    if both.any():
        if cfg.tie == "rb_sign":
            orange_wins = frame.rgb[..., 0] > frame.rgb[..., 2]
        elif cfg.tie == "orange":
            orange_wins = np.ones(frame.shape, bool)
        else:
            orange_wins = np.zeros(frame.shape, bool)
        cand[ORANGE] &= ~both | orange_wins
        cand[BLUE] &= ~both | ~orange_wins
    mask = np.full(frame.shape, OTHER, np.uint8)
    mask[cand[ORANGE]] = ORANGE
    mask[cand[BLUE]] = BLUE
    return mask, info


def with_overrides(cfg: Config, **kw) -> Config:
    return replace(cfg, **kw)
