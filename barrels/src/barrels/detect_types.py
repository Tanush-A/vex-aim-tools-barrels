"""The detection output type and its conversions (docs/PROBLEM.md v2 proposal).

A ``Barrel`` is one detected (or ground-truth) barrel: its color class, its box in 640x480
pixels, and optionally its ground position in the robot base frame. ``to_aivision_spec``
produces exactly the dict that aim_fsm/worldmap.py's make_new_aiv_objects reads (320x240 units).
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np

from . import geometry as geo
from .io import BLUE, ORANGE

AIVISION_NAMES = {ORANGE: "OrangeBarrel", BLUE: "BlueBarrel"}
AIVISION_COLORS = {v: k for k, v in AIVISION_NAMES.items()}
COLOR_NAMES = {ORANGE: "orange", BLUE: "blue"}
COLOR_BY_NAME = {v: k for k, v in COLOR_NAMES.items()}
AIVISION_SCALE = 2                       # aivision reports 320x240; the image is 640x480
FLAGS = ("truncated", "occluded", "no_stripe", "top_only", "bottom_inferred")


@dataclass(frozen=True)
class Barrel:
    color: int                                        # ORANGE | BLUE
    bbox: tuple[int, int, int, int]                   # x0, y0, x1, y1 — half-open, 640x480 pixels
    confidence: float = 1.0
    bottom_mid: tuple[float, float] | None = None     # default ((x0+x1)/2, y1): the ground-contact pixel worldmap uses
    ground_xy_mm: tuple[float, float] | None = None   # robot base frame, x forward / y left
    flags: frozenset[str] = field(default_factory=frozenset)
    area: int | None = None                           # pixels, when it came from a mask
    source: str = ""                                  # "gt" | "cc" | "aivision" | ...

    def __post_init__(self):
        x0, y0, x1, y1 = self.bbox
        if not (x1 > x0 and y1 > y0):
            raise ValueError(f"empty bbox {self.bbox}")
        if self.color not in AIVISION_NAMES:
            raise ValueError(f"color must be ORANGE or BLUE, got {self.color}")
        bad = set(self.flags) - set(FLAGS)
        if bad:
            raise ValueError(f"unknown flags {sorted(bad)}")
        if self.bottom_mid is None:
            object.__setattr__(self, "bottom_mid", ((x0 + x1) / 2, float(y1)))

    # ---------------------------------------------------------------- derived
    @property
    def width(self) -> int:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> int:
        return self.bbox[3] - self.bbox[1]

    @property
    def bottom_row(self) -> int:
        """Last image row the barrel occupies."""
        return self.bbox[3] - 1

    @property
    def color_name(self) -> str:
        return COLOR_NAMES[self.color]

    def with_ground(self, cam: geo.CameraModel, radius_mm: float = geo.BARREL_END_DIAMETER_MM / 2) -> "Barrel":
        """Fill ground_xy_mm from the bottom-mid pixel via worldmap's recipe (base radius by default)."""
        u, v = self.bottom_mid
        return replace(self, ground_xy_mm=cam.barrel_axis_xy(u, v, radius_mm))

    # ---------------------------------------------------------------- aivision spec
    def to_aivision_spec(self, id: str | None = None) -> dict:
        """The dict worldmap.make_new_aiv_objects / viewer.camera_overlay read (320x240 ints)."""
        x0, y0, x1, y1 = self.bbox
        s = AIVISION_SCALE
        spec = {"type_str": "aiobj", "name": AIVISION_NAMES[self.color],
                "originx": int(round(x0 / s)), "originy": int(round(y0 / s)),
                "width": max(1, int(round((x1 - x0) / s))), "height": max(1, int(round((y1 - y0) / s))),
                "score": float(self.confidence)}
        if id is not None:
            spec["id"] = id
        return spec

    @classmethod
    def from_aivision_spec(cls, spec: dict) -> "Barrel":
        s = AIVISION_SCALE
        x0, y0 = int(spec["originx"]) * s, int(spec["originy"]) * s
        return cls(color=AIVISION_COLORS[spec["name"]], bbox=(x0, y0, x0 + int(spec["width"]) * s, y0 + int(spec["height"]) * s),
                   confidence=float(spec.get("score", 1.0)), source="aivision")

    # ---------------------------------------------------------------- masks / json
    @classmethod
    def from_instance_mask(cls, inst: np.ndarray, mask: np.ndarray, inst_id: int, color: int | None = None,
                           flags=(), cam: geo.CameraModel | None = None, source: str = "gt") -> "Barrel":
        sel = inst == inst_id
        if not sel.any():
            raise ValueError(f"instance id {inst_id} not present")
        ys, xs = np.where(sel)
        bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
        if color is None:
            n_o, n_b = int((mask[sel] == ORANGE).sum()), int((mask[sel] == BLUE).sum())
            color = ORANGE if n_o >= n_b else BLUE
        b = cls(color=color, bbox=bbox, flags=frozenset(flags), area=int(sel.sum()), source=source)
        return b.with_ground(cam) if cam is not None else b

    def to_dict(self) -> dict:
        return {"color": self.color_name, "bbox": list(self.bbox), "confidence": self.confidence,
                "bottom_mid": list(self.bottom_mid), "ground_xy_mm": None if self.ground_xy_mm is None else list(self.ground_xy_mm),
                "flags": sorted(self.flags), "area": self.area, "source": self.source}

    @classmethod
    def from_dict(cls, d: dict) -> "Barrel":
        return cls(color=COLOR_BY_NAME[d["color"]], bbox=tuple(d["bbox"]), confidence=d.get("confidence", 1.0),
                   bottom_mid=None if d.get("bottom_mid") is None else tuple(d["bottom_mid"]),
                   ground_xy_mm=None if d.get("ground_xy_mm") is None else tuple(d["ground_xy_mm"]),
                   flags=frozenset(d.get("flags", ())), area=d.get("area"), source=d.get("source", ""))


def barrels_from_instances(inst: np.ndarray, meta: dict, mask: np.ndarray | None = None,
                           cam: geo.CameraModel | None = None) -> list[Barrel]:
    """Ground-truth Barrel list from a loaded instance mask + its JSON (colors/flags/ground from the JSON)."""
    out = []
    for rec in meta.get("barrels", []):
        i = rec["id"]
        sel = inst == i
        if not sel.any():
            continue
        ys, xs = np.where(sel)
        bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
        color = COLOR_BY_NAME.get(rec.get("color"), None)
        if color is None:
            if mask is None:
                raise ValueError(f"instance {i} has no color in the JSON and no mask was given")
            color = ORANGE if (mask[sel] == ORANGE).sum() >= (mask[sel] == BLUE).sum() else BLUE
        g = rec.get("ground_xy_mm")
        b = Barrel(color=color, bbox=bbox, flags=frozenset(rec.get("flags", ())), area=int(sel.sum()), source="gt",
                   ground_xy_mm=None if g is None else tuple(g))
        if b.ground_xy_mm is None and cam is not None:
            b = b.with_ground(cam)
        out.append(b)
    return out
