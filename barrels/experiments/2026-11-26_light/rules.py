"""The candidate color steps of the 2026-11-26 light experiment: a frame in, a class mask out. Nothing here runs by
default; the judge calls them through ``candidates.py``. A pixel is never changed: only thresholds move, with numbers
read from the frame itself, and nothing is carried from one frame to the next.

One ``Setting`` is one color step:

- **The reading** (``reading``): where the light's warmth w is read from (``common.READINGS``).
- **Blue follows the light** (``w0``, ``w1``, ``s_warm``, ``h_warm``): the share t = clip((w - w0) / (w1 - w0), 0, 1);
  the blue S floor moves from the adopted 113 toward ``s_warm`` and the low end of the blue hue range from the adopted
  103 toward ``h_warm`` by that share. Only ever lowered. At w <= w0 nothing changes. (The form of
  ``lightcolor.warm_blue_boxes``; here the reading can be any of the readings.)
- **Bluer than the light** (``delta``; 0 = off): under a warm lamp the blue paint goes gray-olive (hue 26-44, S about
  50), which no blue hue range reaches. So, only where the light reads warm (w > w0), a pixel that the moved boxes
  left unpainted and that is under the adopted blue S floor (S < 113) is also blue when its own warmth
  (R - B) / (R + G + B + 1) is at least ``delta`` below the lower of two references: the light's warmth w, and the
  warmth of the whole scene below the gate (``lightread.gray_world``). The second reference keeps a dark neutral
  table (the black ottoman) from being "bluer than the light" all over.
- **Orange follows a reading** (``o_reading``, ``o_x0``, ``o_x1``, ``o_hi``; part C): the high end of the orange hue
  range moves from the adopted 13 toward ``o_hi`` as the reading ``o_reading`` goes from ``o_x0`` to ``o_x1``
  (``o_x1`` may be below ``o_x0``: then it widens as the reading FALLS, for "the darker the scene"). ``o_reading`` is a
  light reading, or ``dark`` (the median brightness of the frame below the gate), or ``always`` (the value 1 on every
  frame: with ``o_x0`` = 0 and ``o_x1`` = 1 the range is ``o_hi`` everywhere, and only the flood guard decides).
- **The flood guard** (``o_guard``; 0 = off): the orange range is widened only if the pixels it would ADD make up at
  most this share of the gated frame. Barrels cover a few percent of a frame; if the added band holds more than
  that, it is the table.

Everything else (the horizon gate, the brightness gate, the tie rule) is ``pipeline.segment`` with the adopted model.
"""
from __future__ import annotations

import dataclasses
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402

from barrels import boxfit as bf  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import lightread as lr  # noqa: E402
from barrels import pipeline as pl  # noqa: E402
from barrels.io import BLUE, ORANGE, OTHER  # noqa: E402

CAM = geo.AIM_4A8B6118_BOXFIT


@dataclass(frozen=True)
class Setting:
    reading: str = ""               # "" = the fixed model
    w0: float = 0.0
    w1: float = 1.0
    s_warm: float = 113.0
    h_warm: float = 103.0
    delta: float = 0.0              # bluer than the light by this much; 0 = off
    o_reading: str = ""             # "" = orange as adopted
    o_x0: float = 0.0
    o_x1: float = 1.0
    o_hi: float = 13.0
    o_guard: float = 0.0            # the flood guard; 0 = off

    @property
    def key(self) -> str:
        return "|".join(f"{v:g}" if isinstance(v, float) else str(v) for v in dataclasses.astuple(self))

    @property
    def is_fixed(self) -> bool:
        return not self.reading and not self.o_reading

    def describe(self) -> str:
        if self.is_fixed:
            return "the fixed model"
        parts = []
        if self.reading:
            t = f"blue follows `{self.reading}`: from warmth {self.w0:g} to {self.w1:g} the S floor goes 113 -> {self.s_warm:g}, the hue low end 103 -> {self.h_warm:g}"
            if self.delta:
                t += f"; and bluer than the light by {self.delta:g}"
            parts.append(t)
        if self.o_reading:
            t = f"orange hue high end 13 -> {self.o_hi:g} as `{self.o_reading}` goes {self.o_x0:g} -> {self.o_x1:g}"
            if self.o_guard:
                t += f", only where the added band is at most {100 * self.o_guard:g} % of the frame"
            parts.append(t)
        return "; ".join(parts)


FIXED = Setting()


def _memo(frame: pl.Frame) -> dict:
    """Numbers already read from this frame (a frame is handed to many settings; nothing is kept between frames)."""
    m = getattr(frame, "_light_memo", None)
    if m is None:
        m = {}
        frame._light_memo = m
    return m


def read_value(name: str, frame: pl.Frame) -> float:
    """A light reading's warmth; ``dark``: the median brightness of the frame below the gate; ``always``: 1."""
    if name == "always":
        return 1.0
    m = _memo(frame)
    if name not in m:
        m[name] = float(np.median(frame.val[lr.GATE_ROW:])) if name == "dark" else cm.one_reading(name, frame)
    return m[name]


def scene_warmth(frame: pl.Frame) -> float:
    m = _memo(frame)
    if "scene" not in m:
        m["scene"] = lr.gray_world(frame.rgb).warmth
    return m["scene"]


def pixel_warmth(frame: pl.Frame) -> np.ndarray:
    m = _memo(frame)
    if "pw" not in m:
        m["pw"] = lr.pixel_warmth(frame.rgb)
    return m["pw"]


def share(x: float, x0: float, x1: float) -> float:
    """0 at x0, 1 at x1, a straight line between, clipped; x1 may be below x0. A nan reading gives 0."""
    if x1 == x0:
        raise ValueError("x0 and x1 must differ")
    if not np.isfinite(x):
        return 0.0
    return float(np.clip((x - x0) / (x1 - x0), 0.0, 1.0))


def segment(frame: pl.Frame, st: Setting, info: dict | None = None) -> np.ndarray:
    """The class mask of ``frame`` under the setting ``st`` (uint8: 0 other, 1 orange, 2 blue)."""
    base = cm.model()
    info = info if info is not None else {}
    if st.is_fixed:
        return pl.segment(frame, base)[0]
    boxes = dict(base.boxes)
    w = t = float("nan")
    if st.reading:
        w = read_value(st.reading, frame)
        t = share(w, st.w0, st.w1)
        b = base.boxes[BLUE]
        h_lo, s_lo = float(b.lo[0]), float(b.lo[1])
        boxes[BLUE] = bf.Box((h_lo - t * max(0.0, h_lo - st.h_warm), s_lo - t * max(0.0, s_lo - st.s_warm)) + tuple(b.lo[2:]), tuple(b.hi))
    info.update(warmth=w, share=t)
    if st.o_reading:
        x = read_value(st.o_reading, frame)
        to = share(x, st.o_x0, st.o_x1)
        o = base.boxes[ORANGE]
        shift = pl.HUE_SHIFT[ORANGE]
        hi = float(o.hi[0]) + to * max(0.0, st.o_hi + shift - float(o.hi[0]))
        if to > 0 and st.o_guard:
            g = cm.gate(frame)
            hs = frame.hs(shift)
            added = g & (hs[..., 0] > o.hi[0]) & (hs[..., 0] <= hi) & (hs[..., 1] >= o.lo[1])
            flood = float(added.sum()) / max(1, int(g.sum()))
            info.update(o_flood=flood)
            if flood > st.o_guard:
                hi = float(o.hi[0])
        boxes[ORANGE] = bf.Box(tuple(o.lo), (hi,) + tuple(o.hi[1:]))
        info.update(o_x=x, o_share=to, o_hi=hi - shift)
    mask = pl.segment(frame, dataclasses.replace(base, boxes=boxes))[0]
    if st.reading and st.delta > 0 and t > 0:
        scene = scene_warmth(frame)
        ref = min(w, scene) if np.isfinite(scene) else w
        rel = (mask == OTHER) & cm.gate(frame, base.cfg.v_min, base.cfg.horizon_row) & (cm.sat(frame) < float(base.boxes[BLUE].lo[1])) \
            & (pixel_warmth(frame) <= ref - st.delta)
        info.update(ref=ref, rel_px=int(rel.sum()))
        mask = mask.copy()
        mask[rel] = BLUE
    return mask


def detect(frame: pl.Frame, st: Setting) -> list:
    """The setting's color step, then today's detector (``DetConfig()``)."""
    return det.detect(segment(frame, st), det.DetConfig(), CAM)
