"""Hand-set color thresholds as label data (TODO D, 2026-11-18): the six numbers of the hs color model, set by
hand per frame with ``tools/hs_slider.py`` and stored in ``data/labels/<stem>_hs.json`` (``io.save_hs``).

A side module, not part of the detector: it only *builds* a ``pipeline.Model`` from six numbers, so that the
picture the slider tool shows is exactly what ``pipeline.segment`` produces with them. Nothing here thresholds
a pixel.

The six numbers (``thresholds``), in the units a person reads::

    {"orange": {"h_lo": 3, "h_hi": 13, "s_lo": 140}, "blue": {"h_lo": 103, "h_hi": 119, "s_lo": 113}}

``h_lo`` / ``h_hi``: the hue sector, OpenCV units, both ends included. Orange sits at the red wrap (0 = 180), so
its hue is written on a line that runs from -30 to 149: -3 means 177, and "-3 to 5" is the sector 177, 178, 179,
0, 1, ... 5. Blue's runs from 0 to 179. ``s_lo``: the floor on HSV saturation (0-255); a pixel needs S >= s_lo.

How that becomes the model: ``pipeline`` stores each class as a box in (hue + ``HUE_SHIFT``, S), where the
shifted hue is ``(hue + shift) % 180`` — orange's shift is 30, which is what makes its sector one piece. So the
box is ``lo = (h_lo + shift, s_lo)``, ``hi = (h_hi + shift, 255)``, and everything else (the horizon row, the
brightness gate V >= 40, the tie rule) is the base model's config, untouched.

Also here: which frames may be slider-labeled (train frames only; test frames are refused before anything is
opened), and the dict that goes into the label file.
"""
from __future__ import annotations

import dataclasses
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from . import boxfit as bf
from . import io
from . import pipeline as pl
from . import splits as sp
from .io import BLUE, ORANGE, PKG_ROOT

CLASS_OF = {"orange": ORANGE, "blue": BLUE}
S_MAX = 255.0
DEFAULT_SCENES = ("core_01", "occl_01", "clutter_01")      # the three frames the plan slider-labels per condition (TODO E)


# ---------------------------------------------------------------- thresholds <-> model

def copy_thresholds(thresholds: dict) -> dict:
    """A plain, independent copy holding only the six numbers."""
    return {name: {k: int(thresholds[name][k]) for k in io.HS_KEYS} for name in io.HS_CLASSES}


def model_from_thresholds(base_model: pl.Model, thresholds: dict) -> pl.Model:
    """``base_model`` with its two class boxes replaced by the hand-set thresholds; config, gates and tie rule
    are the base model's. Raises ValueError when the base is not an hs model or the numbers are not valid."""
    if base_model.cfg.color_model != "hs":
        raise ValueError(f"the base model must be an hs model, got color_model={base_model.cfg.color_model!r}")
    io.validate_hs_thresholds(thresholds)
    boxes = {}
    for name, c in CLASS_OF.items():
        t, shift = thresholds[name], pl.HUE_SHIFT[c]
        boxes[c] = bf.Box((float(t["h_lo"] + shift), float(t["s_lo"])), (float(t["h_hi"] + shift), S_MAX))
    return dataclasses.replace(base_model, boxes=boxes)


def thresholds_from_model(model: pl.Model) -> dict:
    """The six numbers of an hs model (the inverse of ``model_from_thresholds``). Raises ValueError when the
    model is not hs, a bound is not a whole number, or a box has a saturation ceiling below 255 — such a model
    cannot be written as six integers without changing what it segments."""
    if model.cfg.color_model != "hs":
        raise ValueError(f"not an hs model: color_model={model.cfg.color_model!r}")
    out = {}
    for name, c in CLASS_OF.items():
        box, shift = model.boxes[c], pl.HUE_SHIFT[c]
        if box.dims != 2:
            raise ValueError(f"{name}: an hs box has two dimensions (hue, S), got {box.dims}")
        vals = (box.lo[0], box.hi[0], box.lo[1])
        if any(float(v) != int(v) for v in vals):
            raise ValueError(f"{name}: the box bounds {box.lo}, {box.hi} are not whole numbers")
        if box.hi[1] < S_MAX:
            raise ValueError(f"{name}: the box has a saturation ceiling {box.hi[1]}; the six thresholds cannot express it")
        out[name] = {"h_lo": int(box.lo[0]) - shift, "h_hi": int(box.hi[0]) - shift, "s_lo": int(box.lo[1])}
    io.validate_hs_thresholds(out)
    return out


def adopted_model() -> pl.Model:
    """The adopted hs model (``worldmap_bridge.DEFAULT_MODEL``, config eb863d84). Always that file: the
    environment variable BARRELS_MODEL does not change what the labels are relative to."""
    from . import worldmap_bridge as wb
    return wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL).model


def hue_text(h: int) -> str:
    """A hue as a person reads it: a negative (orange, past the red wrap) hue with its real value, '-3 (=177)'."""
    return f"{h} (={h + 180})" if h < 0 else str(h)


def describe(thresholds: dict) -> str:
    """One line: 'orange hue -3..13 (=177..13) S>=140   blue hue 103..119 S>=113'."""
    parts = []
    for name in io.HS_CLASSES:
        t = thresholds[name]
        wrap = f" (={t['h_lo'] % 180}..{t['h_hi'] % 180})" if t["h_lo"] < 0 else ""
        parts.append(f"{name} hue {t['h_lo']}..{t['h_hi']}{wrap} S>={t['s_lo']}")
    return "   ".join(parts)


# ---------------------------------------------------------------- which frames may be labeled

class RefusedFrame(ValueError):
    """A frame the slider tool must not open (a test frame, a geometry-only frame, a frame in no split)."""


REFUSE_TEST = "test frame (held out; never opened)"
REFUSE_GEOMETRY = "geometry-only frame (calib / ruler / horizon)"
REFUSE_NO_SPLIT = "in no split yet: assign splits first (python barrels/tools/make_splits.py --v2 --filter <robot>_<light>_<surface>)"
REFUSE_NAME = "name not {robot}_{light}_{surface}_{scene}_{nn}"


def refusal(stem: str, splits: dict[str, list[str]]) -> str | None:
    """Why this frame may not be slider-labeled, or None when it may (it is a train frame). Looks at the name
    and the split lists only; no file is opened."""
    if stem in splits.get("test", ()):
        return REFUSE_TEST
    try:
        tags = io.parse_name(stem)
    except ValueError:
        return REFUSE_NAME
    if tags["scene"] in sp.UNASSIGNED_SCENES:
        return REFUSE_GEOMETRY
    where = next((name for name in sp.SPLIT_NAMES if stem in splits.get(name, ())), None)
    if where is None:
        return REFUSE_NO_SPLIT
    if where != "train":
        return f"split {where} (only train frames are slider-labeled)"
    return None


def require_labelable(stem: str, splits: dict[str, list[str]]) -> None:
    """Raise ``RefusedFrame`` unless the frame is a train frame. Called before a frame's image is read."""
    why = refusal(stem, splits)
    if why:
        raise RefusedFrame(f"{stem}: {why}")


def parse_scenes(text: str | None) -> tuple[str, ...] | None:
    """'core_01,occl_01' -> ('core_01', 'occl_01'); 'all' -> None (every scene); empty -> the default three."""
    if text is None or not text.strip():
        return DEFAULT_SCENES
    items = tuple(x.strip() for x in text.split(",") if x.strip())
    return None if "all" in items else items


def scene_matches(stem: str, scenes: tuple[str, ...] | None) -> bool:
    """True when the frame's '{scene}_{nn}' (or its bare scene tag) is in ``scenes``; ``None`` matches all."""
    if scenes is None:
        return True
    try:
        t = io.parse_name(stem)
    except ValueError:
        return False
    return f"{t['scene']}_{t['nn']}" in scenes or t["scene"] in scenes


@dataclass
class Selection:
    stems: list[str]                                              # the frames to label, sorted by name
    refused: dict[str, list[str]] = field(default_factory=dict)   # reason -> stems that matched but may not be opened


def select_frames(stems: list[str], splits: dict[str, list[str]], scenes: tuple[str, ...] | None = DEFAULT_SCENES,
                  filter_: str = "") -> Selection:
    """The frames the slider tool will show: name contains ``filter_``, scene is in ``scenes``, and the frame is
    a train frame. Frames that match but may not be opened are listed under ``refused`` by reason; there is no
    way to include them."""
    keep: list[str] = []
    refused: dict[str, list[str]] = {}
    for stem in sorted(set(stems)):
        if filter_ not in stem or not (scene_matches(stem, scenes)):
            continue
        why = refusal(stem, splits)
        if why:
            refused.setdefault(why, []).append(stem)
        else:
            keep.append(stem)
    return Selection(keep, refused)


# ---------------------------------------------------------------- the label

def detector_git() -> str:
    """Short git hash of the checkout this package runs from, with '+dirty' when ``src/barrels`` has uncommitted
    changes; 'unknown' outside git. Recorded in every label: which detector drew the boxes the labeler saw."""
    def run(*args: str) -> str:
        return subprocess.run(["git", "-C", str(PKG_ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()
    try:
        return run("rev-parse", "--short", "HEAD") + ("+dirty" if run("status", "--porcelain", "--", "src/barrels") else "")
    except Exception:  # noqa: BLE001 — no git, or not a checkout
        return "unknown"


def label_meta(stem: str, image_sha1: str, thresholds: dict, base_model: pl.Model, boxes_drawn: int,
               git: str, note: str = "") -> dict:
    """The dict ``io.save_hs`` writes: the six numbers plus what they were set against (the base model's fixed
    gates and hash, the detector's git hash, how many boxes it drew with them)."""
    return {"stem": Path(stem).stem, "image_sha1": image_sha1, **copy_thresholds(thresholds),
            "v_min": int(base_model.cfg.v_min), "horizon_row": base_model.cfg.horizon_row,
            "base_model": base_model.cfg.short_hash(), "detector_git": git, "boxes_drawn": int(boxes_drawn),
            "reviewed": True, "note": note}
