"""White balance in memory, then the fixed colors (experiment 2026-11-27_whitebalance; plan: PREREG.md).

EXPERIMENT ONLY. The standing rule (Dave, 2026-10-07) is "never white-balance or otherwise correct the image". Nothing
that runs by default imports this file. The corrected photo exists only inside ``segment`` / ``detect`` and is never
written anywhere.

A *setting* is (estimator, alpha, union). The estimator reads the light L = (R, G, B) from the frame; the gains are
g_c = (mean(L) / L_c) ** alpha, each held inside [0.25, 4]; the corrected photo is the camera values times the gains,
rounded and held in 0..255; then the adopted color model (``pipeline.segment``) and today's detector run on it.
``union``: today's mask is kept, and only where it paints nothing does the corrected photo's class count.
"""
from __future__ import annotations

import dataclasses
import sys
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
sys.path.insert(0, str(BARRELS / "src"))

from barrels import detector as det  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import pipeline as pl  # noqa: E402

assert str(Path(pl.__file__).resolve()).startswith(str(BARRELS)), f"barrels is imported from {pl.__file__}, not from this checkout"

CAM = geo.AIM_4A8B6118_BOXFIT
V_MIN, CLIP, MIN_PX = 40, 250, 200
GAIN_LO, GAIN_HI = 0.25, 4.0
GATE_ROW = 50
P_SOG = 6.0
ESTIMATORS = ("gray_world", "white_patch", "without_loose", "gray_above", "shades_of_gray")
ALPHAS = (0.25, 0.5, 0.75, 1.0)

_MODEL = None


def model() -> pl.Model:
    global _MODEL
    if _MODEL is None:
        _MODEL = hl.adopted_model()
    return _MODEL


def nogate_model() -> pl.Model:
    """The adopted model without the horizon gate (only for measuring the home wall; never a detector)."""
    m = model()
    return dataclasses.replace(m, cfg=dataclasses.replace(m.cfg, horizon_row=None))


# ---------------------------------------------------------------- reading the light

def readable(rgb: np.ndarray) -> np.ndarray:
    """Pixels an estimator may read: brightest channel >= 40, no channel >= 250."""
    x = np.asarray(rgb)
    return (x.max(-1) >= V_MIN) & (x.max(-1) < CLIP)


def _hue_s(bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    hsv = cv2.cvtColor(np.ascontiguousarray(bgr), cv2.COLOR_BGR2HSV)
    return hsv[..., 0].astype(np.float32), hsv[..., 1].astype(np.float32)


def loose_mask(bgr: np.ndarray) -> np.ndarray:
    """Anything barrel-like under the light experiment's loose model: orange hue -10..25 with S >= 120, blue hue 90..125
    with S >= 60, below the gate, brightness >= 40."""
    h, s = _hue_s(bgr)
    ho = np.where(h >= 150, h - 180, h)
    v = np.asarray(bgr).max(-1)
    k = v >= V_MIN
    k[:GATE_ROW] = False
    return k & (((ho >= -10) & (ho <= 25) & (s >= 120)) | ((h >= 90) & (h <= 125) & (s >= 60)))


def grow(mask: np.ndarray, margin: int) -> np.ndarray:
    k = 2 * margin + 1
    return cv2.dilate(mask.astype(np.uint8), np.ones((k, k), np.uint8)) > 0


def _brightest(rgb: np.ndarray, keep: np.ndarray, top: float = 5.0) -> np.ndarray:
    if keep.sum() < MIN_PX:
        return keep
    v = rgb.max(-1)
    return keep & (v >= np.percentile(v[keep], 100.0 - top))


def estimate(frame: pl.Frame, name: str) -> np.ndarray | None:
    """The light (R, G, B) as ``name`` reads it from ``frame``; None when fewer than 200 pixels can be read."""
    rgb = frame.rgb.astype(np.float32)
    keep = readable(frame.rgb)
    if name == "gray_world" or name == "shades_of_gray":
        pass
    elif name == "white_patch":
        keep = _brightest(rgb, keep)
    elif name == "without_loose":
        keep = _brightest(rgb, keep & ~grow(loose_mask(frame.bgr), 15))
    elif name == "gray_above":
        k = np.zeros(keep.shape, bool)
        k[:GATE_ROW] = True
        keep = keep & k
    else:
        raise ValueError(f"unknown estimator {name!r}")
    if keep.sum() < MIN_PX:
        return None
    px = rgb[keep]
    if name == "shades_of_gray":
        return np.power(np.mean(np.power(px, P_SOG), 0), 1.0 / P_SOG)
    return px.mean(0)


def gains(light: np.ndarray | None, alpha: float) -> np.ndarray:
    """(gR, gG, gB): (mean(L) / L_c) ** alpha, each inside [0.25, 4]; ones when there is no reading."""
    if light is None or alpha == 0:
        return np.ones(3, np.float32)
    L = np.maximum(np.asarray(light, np.float64), 1.0)
    return np.clip((L.mean() / L) ** alpha, GAIN_LO, GAIN_HI).astype(np.float32)


def corrected(frame: pl.Frame, g: np.ndarray) -> pl.Frame:
    """A NEW in-memory frame: the camera values times the gains (R, G, B), rounded, held in 0..255. The input frame is
    not touched (its arrays are read-only)."""
    bgr = np.clip(np.rint(frame.bgr.astype(np.float32) * g[::-1]), 0, 255).astype(np.uint8)
    return pl.Frame.from_image(bgr)


# ---------------------------------------------------------------- the setting

@dataclass(frozen=True)
class Setting:
    estimator: str = ""         # "" = no correction (today)
    alpha: float = 0.0
    union: bool = False

    @property
    def key(self) -> str:
        return f"{self.estimator}|{self.alpha:g}|{int(self.union)}"

    def describe(self) -> str:
        if not self.estimator or self.alpha == 0:
            return "no correction (today)"
        return f"{self.estimator}, alpha {self.alpha:g}" + (", added to today's mask" if self.union else "")

    @classmethod
    def from_key(cls, key: str) -> "Setting":
        e, a, u = key.split("|")
        return cls(e, float(a), bool(int(u)))


FIXED = Setting()


def segment(frame: pl.Frame, st: Setting, info: dict | None = None) -> np.ndarray:
    """The class mask of ``frame`` under setting ``st`` (the adopted model on the corrected photo)."""
    base = pl.segment(frame, model())[0]
    if not st.estimator or st.alpha == 0:
        return base
    L = estimate(frame, st.estimator)
    g = gains(L, st.alpha)
    if info is not None:
        info["light"], info["gains"] = (None if L is None else [float(v) for v in L]), [float(v) for v in g]
        info["corrected"] = corrected(frame, g)
    m = pl.segment(info["corrected"] if info is not None else corrected(frame, g), model())[0]
    if st.union:
        m = np.where(base > 0, base, m).astype(base.dtype)
    return m


def detect(frame: pl.Frame, st: Setting) -> list:
    return det.detect(segment(frame, st), det.DetConfig(), CAM)


def detector_for(st: Setting):
    def detect_frame(stem: str, frame) -> list:
        return detect(frame, st)
    detect_frame.describe = st.describe()
    return detect_frame


# ---------------------------------------------------------------- importable callables (full correction, no chosen number)

detect_frame_gray_world = detector_for(Setting("gray_world", 1.0))
detect_frame_white_patch = detector_for(Setting("white_patch", 1.0))
detect_frame_without_loose = detector_for(Setting("without_loose", 1.0))
detect_frame_gray_above = detector_for(Setting("gray_above", 1.0))
detect_frame_shades_of_gray = detector_for(Setting("shades_of_gray", 1.0))

# The best candidate, P1 (gray world, partial): every fold of the leave-one-place-out run picked alpha 0.5, so this
# plain callable gives exactly P1's boxes. EXPERIMENT ONLY: not adoptable without Dave (the image is corrected).
detect_frame_gray_world_half = detector_for(Setting("gray_world", 0.5))
