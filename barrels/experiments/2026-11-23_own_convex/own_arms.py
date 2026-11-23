"""Shared by the scripts of this experiment: the arms, the results folder, and the earlier harnesses loaded by path
(nothing is copied). The A8 experiment's ``sliver.py`` is loaded as it is (it loads the combined experiment's
``common.py`` / ``comb_arms.py``); this experiment's arms are added to the same arm table, so the earlier battery
scripts run them unchanged.

Arms, each spelled out field by field from the A8 arm ``span`` (so a later change of the defaults does not move them):

  ``start``    the defaults of ``origin/barrels`` on 2026-11-23 (e0d01e0): A8's ``span`` + ``stripe_bridge`` + ``thin_frame``
               (merged on by Tanush 2026-11-23); ``own_close`` and ``own_convex`` off. Checked field by field against
               ``DetConfig()`` of that commit (``check_start``).
  ``close``    ``start`` + ``own_close`` (the A8 rule as it is, against today's defaults).
  ``convex``   ``start`` + ``own_close`` + ``own_convex`` (this experiment's candidate).
"""
from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
SLIVER = EXP / "2026-11-20_occl_sliver"
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(SLIVER))
sys.path.insert(0, str(HERE))

import sliver as S  # noqa: E402  (the A8 experiment's arms; it loads the combined experiment's common.py)
from barrels import detector as det  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

C, A = S.C, S.A
OUT = PKG_ROOT / "results" / "2026-11-23_own_convex"
_FIELDS = {f.name for f in dataclasses.fields(det.DetConfig)}
NEW = ("own_convex",)                                     # this experiment's switch (pinned off in START)

START = dataclasses.replace(S.ARMS["span"], stripe_bridge=True, thin_frame=True, own_close=False,
                            **{k: False for k in NEW if k in _FIELDS})
ARMS = {"start": START, "close": dataclasses.replace(START, own_close=True)}
if set(NEW) <= _FIELDS:
    ARMS["convex"] = dataclasses.replace(START, own_close=True, own_convex=True)


def check_start() -> list[str]:
    """The fields where START differs from the code's DetConfig() with own_close and own_convex off (must be none while
    the code's defaults are those of origin/barrels plus, at most, these two switches)."""
    ref = dataclasses.replace(det.DetConfig(), own_close=False, **{k: False for k in NEW if k in _FIELDS})
    return sorted(f for f in _FIELDS if getattr(ref, f) != getattr(START, f))


def register() -> None:
    """Put this experiment's arms into the combined experiment's arm table."""
    S.register()
    A.ARMS.update(ARMS)


if __name__ == "__main__":
    import barrels
    print("barrels from", barrels.__file__)
    print("START differs from DetConfig() in:", check_start() or "nothing")
    print("arms:", list(ARMS))
