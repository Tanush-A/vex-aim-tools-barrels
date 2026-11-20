"""The arms of this experiment (PREREG.md), and how the earlier harnesses run them.

Every arm is spelled out field by field, so a later change of the defaults does not move it:

  ``before``          the defaults of `origin/barrels` (2026-11-18 evening: stripe_join and cap_behind on; nothing of the
                      unmerged occlusion work). It is the ``base`` arm of ``2026-11-19_det_side/side_arms.py``.
  ``stack``           the defaults of `wip/detector-occl` (side_hidden, seam_height, cap_seen_bottom, edge_check, cap_same
                      on; slice_box, cover_unpinned, stripe_two off). The ``edge+cap`` arm of ``2026-11-19_det_occl``.
  ``combined``        ``stack`` + the six switches of `wip/occl-vertical` + ``pin_outline``.
  ``combined+thin``   ... + ``pin_thin``.
  ``combined+cover``  report only: ``combined`` + ``slice_box``, ``cover_unpinned``, ``stripe_two`` (they stay off, Tanush 2026-11-19).
  ``combined+verify`` ``combined``, then every box is checked against the stencil at its place (``stencil.box_score``, the
                      other boxes given as on `wip/stencil`'s ``veto`` arm) and dropped when it scores under ``verify``.
  ``combined+verify2``  the same, but a box made by ``half_stripes`` is not checked (the stencil cannot score a barrel
                      hidden from above or below by a thing that is not painted: stencil PREREG, "what follows from the design").

The verify limit is read from results/2026-11-20_occl_combined/verify_calibration.json (written by
``verify_calibrate.py`` by the rule of PREREG.md); until that file exists the two verify arms do not exist.

An arm is a ``DetConfig`` with two more fields; ``install()`` puts ``detect`` below in the place of
``detector.detect`` FOR THIS PROCESS ONLY, so the earlier scripts (scorecard, levels, recordings, ``barrels.report``)
run every arm unchanged. A plain ``DetConfig`` goes straight to the rule detector.
"""
from __future__ import annotations

import dataclasses
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import detector as det, geometry as geo, stencil as stn  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-20_occl_combined"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


occl_arms = _load("occl_arms_2026_11_19", HERE.parent / "2026-11-19_det_occl" / "occl_arms.py")
side_arms = _load("side_arms_2026_11_19", HERE.parent / "2026-11-19_det_side" / "side_arms.py")

SIX = ("half_stripe", "half_thin", "post_pair", "stripe_wide", "slice_behind", "cap_low")       # wip/occl-vertical
FIVE = tuple(k for k in SIX if k != "slice_behind")                                             # ... without slice_behind (round 2)
PIN = ("pin_outline",)                                                                          # wip/occl-pin (on there)
THIN = ("pin_thin",)                                                                            # wip/occl-pin (off there)
COVER = ("slice_box", "cover_unpinned", "stripe_two")                                           # wip/detector-occl (off; they stay off)
SOURCE_BASE = occl_arms.BASE        # what chose the scorecard's 50 source barrels on 2026-11-19 (kept, so the 3888 scenes are the same)
STENCIL = stn.StencilConfig()
_cal = OUT / "verify_calibration.json"
VERIFY = json.loads(_cal.read_text())["limit"] if _cal.exists() else None
VERIFY2 = json.loads(_cal.read_text())["limit2"] if _cal.exists() else None


@dataclasses.dataclass(frozen=True)
class Arm(det.DetConfig):
    verify: float | None = None       # drop a box whose stencil score at its place is under this (None = no check)
    verify_skip_half: bool = False    # ... but do not check the boxes made by half_stripes


def _arm(base: det.DetConfig, verify=None, skip_half=False, **on) -> Arm:
    return Arm(**{**dataclasses.asdict(base), **on}, verify=verify, verify_skip_half=skip_half)


def _on(names) -> dict:
    return {k: True for k in names}


_before, _stack = side_arms.ARMS["base"], occl_arms.ARMS["edge+cap"]
ARMS = {
    "before": _arm(_before),
    "stack": _arm(_stack),
    "combined": _arm(_stack, **_on(SIX + PIN)),
    "combined+thin": _arm(_stack, **_on(SIX + PIN + THIN)),
    "combined+cover": _arm(_stack, **_on(SIX + PIN + COVER)),
    # round 2 (PREREG addendum): `combined` failed clause (c) by the boxes of slices_behind, so the rule takes slice_behind out
    "reduced": _arm(_stack, **_on(FIVE + PIN)),
    "reduced+thin": _arm(_stack, **_on(FIVE + PIN + THIN)),
}


def cal_path(base: str) -> Path:
    """Where ``verify_calibrate.py --arm <base>`` writes the verifier's limit for the rule detector ``base``."""
    return OUT / ("verify_calibration.json" if base == "combined" else f"verify_calibration_{base}.json")


for _base in ("combined", "reduced", "reduced+thin"):       # `<base>+verify`, `<base>+verify2`: once that base's limit has been calibrated
    if cal_path(_base).exists():
        _lim = json.loads(cal_path(_base).read_text())
        ARMS[f"{_base}+verify"] = dataclasses.replace(ARMS[_base], verify=_lim["limit"])
        ARMS[f"{_base}+verify2"] = dataclasses.replace(ARMS[_base], verify=_lim["limit2"], verify_skip_half=True)
# each branch alone, exactly as its own experiment pins it (the other branch's switches off): for "does the combination
# find less, or draw more wrong boxes, than either branch alone?" (interactions.py; run_levels.py --arms ...)
_vert = _load("vert_arms_2026_11_20", HERE.parent / "2026-11-20_occl_vertical" / "vert_arms.py")
_pin = _load("pin_arms_2026_11_20", HERE.parent / "2026-11-20_occl_pin" / "pin_arms.py")
ALONE = {"vertical_alone": _arm(_vert.ARMS["all"]), "pin_alone": _arm(_pin.ARMS["pin"]), "pin+thin_alone": _arm(_pin.ARMS["pin+thin"])}
ARMS.update(ALONE)
BASE = SOURCE_BASE                  # the name the scorecard's harness reads for choosing the source barrels
REPORT_ONLY = ("combined+cover",)
RULES_DETECT = det.detect           # the rule detector itself, whatever is installed later
_RULE_FIELDS = {f.name for f in dataclasses.fields(det.DetConfig)}


def rule_config(cfg: det.DetConfig) -> det.DetConfig:
    """The plain DetConfig of an arm (without the two verify fields)."""
    return det.DetConfig(**{k: v for k, v in dataclasses.asdict(cfg).items() if k in _RULE_FIELDS})


def checked_scores(mask, cfg, cam=geo.AIM_4A8B6118_BOXFIT, log: list | None = None):
    """The rule detector's boxes for ``cfg`` with, for each, the stencil's score at its place (None = not checked:
    a box of ``half_stripes`` when ``cfg.verify_skip_half``). Returns [(barrel, score or None)]."""
    mylog: list = [] if log is None else log
    found = RULES_DETECT(mask, rule_config(cfg), cam, mylog)
    half = set()
    if getattr(cfg, "verify_skip_half", False):
        half = {tuple(e["box"]) for e in mylog if e.get("stage") == "half" and e.get("why") == "kept"}
    out = []
    for b in found:
        if tuple(b.bbox) in half:
            out.append((b, None))
        else:
            out.append((b, stn.box_score(mask, b, STENCIL, cam, others=[o for o in found if o is not b])))
    return out


def detect(mask, cfg=det.DetConfig(), cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT, log: list | None = None):
    """``detector.detect``'s signature; the verify step is read from ``cfg.verify`` (a plain DetConfig has none)."""
    limit = getattr(cfg, "verify", None)
    if limit is None:
        return RULES_DETECT(mask, rule_config(cfg) if isinstance(cfg, Arm) else cfg, cam, log)
    out = []
    for b, s in checked_scores(mask, cfg, cam, log):
        if s is None or s >= limit:
            out.append(b)
        elif log is not None:
            log.append({"stage": "verify", "why": "dropped", "bbox": tuple(b.bbox), "body": b.color, "score": float(s), "limit": limit})
    return out


def install() -> None:
    det.detect = detect
