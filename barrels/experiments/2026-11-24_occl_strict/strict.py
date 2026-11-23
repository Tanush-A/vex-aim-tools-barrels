"""Shared by the scripts of this experiment (occl_strict, 2026-11-24): paths, the arms, the frames, and how a box is
judged against the hand labels.

The question (Tanush): the occlusion rules may be too lenient; strengthen them everywhere against false boxes without
breaking real cases, by logic, not by trial and error. See PREREG.md.
"""
from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
CLOSEUP = EXP / "2026-11-23_closeup_shape"      # its frame iterator (census.masks) and battery are reused, loaded by path
COMB = EXP / "2026-11-20_occl_combined"
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(CLOSEUP))
sys.path.insert(0, str(HERE))

from barrels import detector as det, geometry as geo  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-24_occl_strict"
CAM = geo.AIM_4A8B6118_BOXFIT
_FIELDS = {f.name for f in dataclasses.fields(det.DetConfig)}

# the rules that can CREATE a box that would not be there without them (each a DetConfig switch, all on today)
CREATORS = ("stripe_join", "stripe_bridge", "seam_height", "stripe_wide", "side_hidden", "pin_outline", "pin_thin", "thin_span",
            "thin_frame", "cap_behind", "cap_same", "cap_low", "cap_seen_bottom", "post_pair", "half_stripe", "half_thin",
            "closeup_stripe")

# this experiment's switches (PREREG.md); pinned off in START so START = origin/barrels' detector, field by field
NEW = tuple(n for n in ("verify_front", "verify_readings") if n in _FIELDS)
START = det.DetConfig(**{k: False for k in NEW})
ARMS = {"start": START}
for n in NEW:
    ARMS[n] = dataclasses.replace(START, **{n: True})
if NEW:
    ARMS["strict"] = dataclasses.replace(START, **{n: True for n in NEW})     # every check of this experiment, the candidate default
ARMS["defaults"] = det.DetConfig()     # NOT pinned


def battery():
    """The combined experiment's ``common`` module with this experiment's arms and output folder (as closeup.battery)."""
    sys.path.insert(0, str(COMB))
    import common as C  # noqa: E402
    C.A.ARMS.update(ARMS)
    C.OUT = C.A.OUT = OUT
    C.RULE_ARMS = tuple(ARMS)
    if not getattr(C, "_strict_patched", False):
        load = C.load

        def patched_load(name, path):
            # as 2026-11-23_closeup_shape/battery.py: the levels harness groups the train frames with 2026-11-16_hs_pooled's
            # group_of, which knows only HOME, CAMPUS and BLACK; any other set is "OTHER" (only the HOME list is used)
            mod = load(name, path)
            pooled = getattr(mod, "pooled", None)
            if pooled is not None and not getattr(pooled, "_other_ok", False):
                known = pooled.group_of

                def group_of(stem):
                    try:
                        return known(stem)
                    except KeyError:
                        return "OTHER"
                pooled.group_of, pooled._other_ok = group_of, True
            return mod
        C.load, C._strict_patched = patched_load, True
    return C


def closeup_census():
    """2026-11-23_closeup_shape's census module (its ``masks()``: every train frame of every set, segmented as the report
    does), loaded by path (this folder has a census script of its own)."""
    import importlib.util
    if "closeup_census" not in sys.modules:
        spec = importlib.util.spec_from_file_location("closeup_census", CLOSEUP / "census.py")
        mod = importlib.util.module_from_spec(spec); sys.modules["closeup_census"] = mod; spec.loader.exec_module(mod)
    return sys.modules["closeup_census"]


def judge(box, color, gts, matched: bool) -> str:
    """What a detector box is, by the hand labels: ``hit`` (a v2 match), ``loose`` (same color, IoU >= 0.5, bottom off),
    ``part`` (same color, IoU 0.1 to 0.5: on a real barrel, wrong place or size), ``wrongcolor`` (on a labeled barrel of the
    other color, IoU >= 0.3), ``false`` (no labeled barrel there: a random box)."""
    if matched:
        return "hit"
    best = max((det.box_iou(box, g.bbox) for g in gts if g.color == color), default=0.0)
    if best >= 0.5:
        return "loose"
    if best >= 0.1:
        return "part"
    if max((det.box_iou(box, g.bbox) for g in gts if g.color != color), default=0.0) >= 0.3:
        return "wrongcolor"
    return "false"


EXTREME = ("_wood", "window_black")     # parked extreme sets: report only


def is_extreme(label: str) -> bool:
    return any(t in label for t in EXTREME)
