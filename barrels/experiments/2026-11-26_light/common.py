"""Shared by the scripts of the 2026-11-26 light experiment: which frames, where the paint is, the readings by name.

Train frames only: every list comes from ``judge.train_frames`` and every image is read with ``judge.load_frame``,
which refuses anything that is not a train frame before it is opened. Nothing here changes a pixel.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
sys.path.insert(0, str(BARRELS / "src"))

from barrels import boxfit as bf  # noqa: E402
from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import lightread as lr  # noqa: E402
from barrels import pipeline as pl  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

OUT = BARRELS / "results" / "2026-11-26_light"
assert str(Path(lr.__file__).resolve()).startswith(str(BARRELS)), f"barrels is imported from {lr.__file__}, not from this checkout"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


color_common = _load("color_common_2026_11_25", BARRELS / "experiments" / "2026-11-25_color" / "common.py")   # expected_regions: where a box's body and stripe are

_MODEL = None


def model() -> pl.Model:
    """The adopted color model (orange 3..13 S >= 140, blue 103..119 S >= 113)."""
    global _MODEL
    if _MODEL is None:
        _MODEL = hl.adopted_model()
    return _MODEL


def frames() -> dict[str, list[str]]:
    """ordinary / extreme train frames (``judge.train_frames``; a test frame raises there)."""
    return jg.train_frames()


def scene_of(stem: str) -> str:
    return io.parse_name(stem)["scene"]


# ---------------------------------------------------------------- where the paint is (the TRUTH; never an input of a rule)

SKIP_FLAGS = {"occluded", "truncated", "held", "bottom_estimated"}
SKIP_SCENES = {"top", "topstripe", "held", "hand"}          # tipped or hand-held barrels: no stripe where an upright barrel has it


def paint_masks(stem: str, shape) -> dict[str, np.ndarray]:
    """From the hand boxes of a train frame: ``orange_body``, ``orange_stripe`` (the orange stripe of blue barrels),
    ``blue_body``, ``blue_stripe`` (the blue stripe of orange barrels): the pixels that should be that paint, inside
    the body and stripe bands of free-standing upright barrels (``expected_regions`` of the 2026-11-25 experiment);
    and ``boxes``: every hand box, flagged ones too, grown by 4 px (what is NOT background)."""
    jg.require_train([stem])
    lab = io.load_boxes(stem, check_image=False)
    h, w = shape[:2]
    out = {k: np.zeros((h, w), bool) for k in ("orange_body", "orange_stripe", "blue_body", "blue_stripe", "boxes")}
    for b in lab.get("barrels", []):
        x0, y0, x1, y1 = (int(v) for v in b["bbox"])
        out["boxes"][max(0, y0 - 4):y1 + 4, max(0, x0 - 4):x1 + 4] = True
        bw, bh = x1 - x0, y1 - y0
        if set(b.get("flags", [])) & SKIP_FLAGS or scene_of(stem) in SKIP_SCENES or bh < 24 or not (0.75 <= bw / bh <= 1.25):
            continue
        reg = color_common.expected_regions(b, (h, w))
        other = "blue" if b["color"] == "orange" else "orange"
        out[f"{b['color']}_body"] |= reg["body"]
        out[f"{other}_stripe"] |= reg["stripe"]
    return out


def hue_orange(frame: pl.Frame) -> np.ndarray:
    """Hue on the line orange is written on: -30 .. 149 (177 reads -3)."""
    return frame.hs(pl.HUE_SHIFT[ORANGE])[..., 0] - pl.HUE_SHIFT[ORANGE]


def hue_blue(frame: pl.Frame) -> np.ndarray:
    return frame.hs(0)[..., 0]


def sat(frame: pl.Frame) -> np.ndarray:
    return frame.hs(0)[..., 1]


def gate(frame: pl.Frame, v_min: int = 40, horizon: int = 50) -> np.ndarray:
    k = frame.val >= v_min
    k[:horizon] = False
    return k


# ---------------------------------------------------------------- the readings, by name

def fixed_mask(frame: pl.Frame) -> np.ndarray:
    """What the adopted model paints orange or blue."""
    return pl.segment(frame, model())[0] > 0


def loose_mask(frame: pl.Frame) -> np.ndarray:
    """Anything barrel-like under a much looser model: orange hue -10..25 with S >= 120, blue hue 90..125 with
    S >= 60 (below the gate, brightness >= 40)."""
    ho, hb, s = hue_orange(frame), hue_blue(frame), sat(frame)
    return gate(frame) & (((ho >= -10) & (ho <= 25) & (s >= 120)) | ((hb >= 90) & (hb <= 125) & (s >= 60)))


READING_NOTES = {
    "whole_frame": "the brightest 5 % of the whole frame (the existing rule)",
    "above_gate": "the brightest 5 % of rows 0-49 (above the horizon gate)",
    "above_gate20": "the brightest 20 % of rows 0-49 (round 2 of 2026-11-25)",
    "above_all": "every pixel of rows 0-49 that is not dark",
    "without_barrels": "the brightest 5 % after taking out what the fixed model paints, grown 15 px",
    "without_loose": "the brightest 5 % after taking out anything barrel-like under a loose model, grown 15 px",
    "neutral": "pixels with almost no color (S < 40), middle brightness",
    "least_colored": "the least colored 10 % of the middle-bright pixels",
    "highlights": "nearly clipped pixels (brightest channel 225-249)",
    "near_strip": "the bottom 80 rows (the table nearest the robot)",
    "gray_world": "every pixel below the gate that is not dark",
    "max_rgb": "the 99th percentile of each channel",
    "tiles": "the lower quartile over 4 x 4 tiles of each bright tile's brightest 20 %",
}
READINGS = tuple(READING_NOTES)


def reading_masks(frame: pl.Frame) -> dict[str, np.ndarray | None]:
    """name -> the pixels that reading reads (None for ``max_rgb``, which has no mask)."""
    rgb = frame.rgb
    above = lr.rows_mask(rgb.shape, 0, lr.GATE_ROW)
    return {
        "whole_frame": lr.whole_frame_mask(rgb),
        "above_gate": lr.above_gate_mask(rgb),
        "above_gate20": lr.above_gate_mask(rgb, top=20.0),
        "above_all": above & (frame.val >= 40),
        "without_barrels": lr.without_barrels_mask(rgb, fixed_mask(frame)),
        "without_loose": lr.without_barrels_mask(rgb, loose_mask(frame)),
        "neutral": lr.neutral_mask(rgb),
        "least_colored": lr.least_colored_mask(rgb),
        "highlights": lr.highlights_mask(rgb),
        "near_strip": lr.near_strip_mask(rgb),
        "gray_world": lr.gray_world_mask(rgb),
        "max_rgb": None,
        "tiles": lr.tiles_mask(rgb),
    }


def all_readings(frame: pl.Frame) -> dict[str, lr.Reading]:
    out = {}
    for name, m in reading_masks(frame).items():
        if name == "max_rgb":
            out[name] = lr.max_rgb(frame.rgb)
        elif name == "tiles":
            out[name] = lr.tiles(frame.rgb)
        else:
            out[name] = lr.read(frame.rgb, m)
    return out


def one_reading(name: str, frame: pl.Frame) -> float:
    """The warmth of one reading on one frame (nan when it says nothing). What a rule calls."""
    rgb = frame.rgb
    if name == "whole_frame":
        return lr.whole_frame(rgb).warmth
    if name == "above_gate":
        return lr.above_gate(rgb).warmth
    if name == "above_gate20":
        return lr.above_gate(rgb, top=20.0).warmth
    if name == "without_barrels":
        return lr.without_barrels(rgb, fixed_mask(frame)).warmth
    if name == "without_loose":
        return lr.without_barrels(rgb, loose_mask(frame)).warmth
    if name == "max_rgb":
        return lr.max_rgb(rgb).warmth
    if name == "tiles":
        return lr.tiles(rgb).warmth
    m = reading_masks(frame)[name]
    return lr.read(rgb, m).warmth
