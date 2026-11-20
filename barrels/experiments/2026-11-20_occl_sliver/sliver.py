"""Shared by the scripts of this experiment: paths, the arms, and the earlier harnesses loaded by path (nothing is
copied). The combined experiment's ``common.py`` / ``comb_arms.py`` are loaded as they are; this experiment's arms are
added to its arm table so that its battery scripts run them unchanged (``battery.py``)."""
from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
COMB = EXP / "2026-11-20_occl_combined"
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(COMB))
sys.path.insert(0, str(HERE))

import common as C  # noqa: E402  (the combined experiment's shared module)
from barrels import detector as det  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

A = C.A
OUT = PKG_ROOT / "results" / "2026-11-20_occl_sliver"
_FIELDS = {f.name for f in dataclasses.fields(det.DetConfig)}
START = A.ARMS["reduced+thin"]          # the defaults of the starting branch (wip/occl-combined, d7b4fca), field by field

ARMS = {
    "start": START,
    "start+behind": dataclasses.replace(START, slice_behind=True),                                    # report only: what slice_behind buys
    "start+cover": dataclasses.replace(START, slice_box=True, cover_unpinned=True, stripe_two=True),   # report only: the held-back cover rules
}


def add(name: str, base: str = "start", **on) -> None:
    """An arm of this experiment: ``base`` with these switches changed; skipped while the detector lacks one of them."""
    if set(on) <= _FIELDS and base in ARMS:
        ARMS[name] = dataclasses.replace(ARMS[base], **on)


def register() -> None:
    """Put this experiment's arms into the combined experiment's arm table (its scripts look arms up there)."""
    A.ARMS.update(ARMS)
