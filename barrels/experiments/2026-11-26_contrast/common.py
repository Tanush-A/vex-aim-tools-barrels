"""Shared by the scripts of the 2026-11-26 contrast experiment (C4): which frames, the fixed model, how a labelled
barrel is classed, and when a candidate counts as "on a barrel's stripe".

Train frames only: every list comes from ``judge.train_frames`` and every image is read with ``judge.load_frame``,
which refuses anything that is not a train frame before it is opened. Nothing here changes a pixel.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
sys.path.insert(0, str(BARRELS / "src"))

from barrels import conditions as cnd  # noqa: E402
from barrels import contrast_c4 as cn  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402

OUT = BARRELS / "results" / "2026-11-26_contrast"
CAM = geo.AIM_4A8B6118_BOXFIT
assert str(Path(cn.__file__).resolve()).startswith(str(BARRELS)), f"barrels is imported from {cn.__file__}, not from this checkout"

# the cluttered empty frames the task names as traps (a red jar with a teal label, a blue tin, a small figure, a jar
# with an orange lid and a blue label)
TRAPS = ("4A8B_lampmid3_bathtile_neg_02", "4A8B_lampmid6_bathtile_neg_02", "4A8B_lampwarm6_bathtile_neg_02",
         "4A8B_lampwarm6_glass_neg_02", "4A8B_lampmid6_glass_neg_02")
TIPPED_SCENES = {"top", "topstripe", "held", "hand"}        # tipped or hand-held: no stripe where an upright barrel has it
HIDDEN_FLAGS = {"occluded", "truncated"}

_MODEL = None


def model() -> pl.Model:
    """The adopted color model (orange hue 3..13 S >= 140, blue 103..119 S >= 113)."""
    global _MODEL
    if _MODEL is None:
        _MODEL = hl.adopted_model()
    return _MODEL


def fixed_mask(frame):
    return pl.segment(frame, model())[0]


def frames() -> dict[str, list[str]]:
    """ordinary / extreme / excluded train frames (``judge.train_frames``; a test frame raises there)."""
    return jg.train_frames()


def scene_of(stem: str) -> str:
    return io.parse_name(stem)["scene"]


def barrel_kind(stem: str, b: dict) -> str:
    """``clean`` (upright, whole, in view), ``hidden`` (flagged occluded or truncated) or ``other`` (a tipped or
    hand-held scene, or flagged no_stripe / held: no stripe where an upright barrel has it)."""
    flags = set(b.get("flags", []))
    if scene_of(stem) in TIPPED_SCENES or flags & {"no_stripe", "held"}:
        return "other"
    return "hidden" if flags & HIDDEN_FLAGS else "clean"


def on_stripe(c: cn.Candidate, bbox) -> bool:
    """The candidate's stripe point lies where this hand box has its stripe: the middle 70 % of its columns and rows
    0.35 to 0.80 of its height (the stripe sits at 0.46 to 0.67, lower for close barrels; slack for a truncated box)."""
    x0, y0, x1, y1 = bbox
    w, h = x1 - x0, y1 - y0
    return x0 + 0.15 * w <= c.x < x1 - 0.15 * w and y0 + 0.35 * h <= c.row < y0 + 0.80 * h


def in_box(c: cn.Candidate, bbox, grow: float = 0.1) -> bool:
    x0, y0, x1, y1 = bbox
    gx, gy = grow * (x1 - x0), grow * (y1 - y0)
    return x0 - gx <= c.x < x1 + gx and y0 - gy <= c.row < y1 + gy


def iou(a, b) -> float:
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - ix * iy
    return ix * iy / u if u > 0 else 0.0


def klass_of(stem: str) -> str:
    return cnd.info(ct.condition_of(stem)).klass
