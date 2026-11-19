"""The arms of this experiment (PREREG.md, "Combinations"), and how the earlier harnesses run them.

The earlier scripts (the scorecard, the levels, the recordings, ``barrels.report``) all call
``detector.detect(mask, cfg, cam)`` with a ``DetConfig``. Here an arm is a ``DetConfig`` with one more field,
``method``, and ``install()`` puts ``detect`` below in the place of ``detector.detect`` FOR THIS PROCESS ONLY, so
those scripts run every arm without a line of them or of ``detector.py`` being changed:

  ``rules``       ``detector.detect`` as it is on this branch (spelled out: the `edge+cap` arm of 2026-11-19_det_occl)
  ``stencil``     ``stencil.detect`` alone
  ``union``       the rule detector's boxes + what the stencil finds with those boxes given as already accepted
  ``veto``        the rule detector's boxes whose stencil score at their place is at least ``VETO``
  ``veto+union``  ``veto``, then the stencil's additions with the kept boxes given

The stencil's numbers are ``StencilConfig()``'s defaults (set from results/2026-11-20_stencil/calibration.json);
``VETO`` is read from that file.
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

OUT = PKG_ROOT / "results" / "2026-11-20_stencil"
_spec = importlib.util.spec_from_file_location("occl_arms_2026_11_19", HERE.parent / "2026-11-19_det_occl" / "occl_arms.py")
occl_arms = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(occl_arms)

RULES_CFG = occl_arms.ARMS["edge+cap"]            # today's default on this branch, spelled out
assert RULES_CFG == det.DetConfig(), "the rule detector's defaults moved: the `rules` arm is no longer today's default"
SOURCE_BASE = occl_arms.BASE                      # what chose the scorecard's 50 source barrels on 2026-11-19 (kept, so the scenes are the same)
STENCIL = stn.StencilConfig()
_cal = OUT / "calibration.json"
VETO = json.loads(_cal.read_text())["chosen"]["veto"] if _cal.exists() else None
METHODS = ("rules", "stencil", "union", "veto", "veto+union")


@dataclasses.dataclass(frozen=True)
class Arm(det.DetConfig):
    method: str = "rules"


ARMS = {m: Arm(**dataclasses.asdict(RULES_CFG), method=m) for m in METHODS}
RULES_DETECT = det.detect                         # the rule detector itself, whatever is installed later


def detect(mask, cfg=det.DetConfig(), cam: geo.CameraModel = geo.AIM_4A8B6118_BOXFIT, log: list | None = None):
    """``detector.detect``'s signature; the arm is read from ``cfg.method`` (a plain DetConfig is ``rules``)."""
    method = getattr(cfg, "method", "rules")
    if method == "rules":
        return RULES_DETECT(mask, cfg, cam, log)
    if method == "stencil":
        return stn.detect(mask, STENCIL, cam, log)
    found = RULES_DETECT(mask, cfg, cam, log)
    if method in ("veto", "veto+union"):
        found = [b for b in found if stn.box_score(mask, b, STENCIL, cam, others=[o for o in found if o is not b]) >= VETO]
    if method in ("union", "veto+union"):
        found = found + stn.detect(mask, STENCIL, cam, log, given=found)
    return sorted(found, key=lambda b: b.bbox[0])


def install() -> None:
    det.detect = detect
