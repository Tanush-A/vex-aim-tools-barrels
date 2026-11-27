"""The geometry checks of the 2026-11-27 experiment: a post-filter on the detector's boxes. Nothing here runs by
default and ``detector.py`` is not touched: the boxes are those of ``detector.detect`` (``stages.found`` draws the
same ones, with what each was drawn from), and a check can only take a box away.

Each check removes one kind of false box measured in part B (``results/2026-11-27_bluer_geom/false_boxes.md``):

- **K1, speckle** (``solid_min``): a barrel is painted as a solid shape; the blue tin, the small figure and the jar
  under the warm lamp are painted as speckle. Of the barrel-colored pixels in the box, the share whose 3 x 3
  neighbourhood is all barrel color (``stages.measure``: ``solid``). The box is removed when that share is under
  ``solid_min``.
- **K2, a label, not a stripe** (``label_sh``, ``label_bf``): the jar's teal label is taller than a barrel's stripe at
  that row, and the jar around it is thin in body color. The box is removed when its stripe is taller than
  ``label_sh`` x the stripe height its row predicts AND the box outside the stripe's rows holds less than ``label_bf``
  body color. A box with no stripe (a close-up, a cap) is not asked.

``None`` = that check is off. ``OFF`` removes nothing.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass

import numpy as np

import stages as sg


@dataclass(frozen=True)
class Checks:
    solid_min: float | None = None
    label_sh: float | None = None
    label_bf: float | None = None

    @property
    def key(self) -> str:
        g = lambda v: "-" if v is None else f"{v:g}"      # noqa: E731
        return f"s{g(self.solid_min)}|l{g(self.label_sh)}/{g(self.label_bf)}"

    def describe(self) -> str:
        parts = []
        if self.solid_min is not None:
            parts.append(f"K1 speckle: solid < {self.solid_min:g}")
        if self.label_sh is not None:
            parts.append(f"K2 label: stripe > {self.label_sh:g} x the row's stripe and body fill < {self.label_bf:g}")
        return "; ".join(parts) or "no check"


OFF = Checks()

# the grids (PREREG.md): a check off first, then from the least to the most aggressive
K1 = (None, 0.30, 0.35, 0.40)
K2 = ((None, None), (1.5, 0.45), (1.5, 0.6), (1.35, 0.45), (1.35, 0.6), (1.25, 0.45), (1.25, 0.6))
GRID = [Checks(s, sh, bf) for s, (sh, bf) in itertools.product(K1, K2)]
GRID_K1 = [Checks(s) for s in K1]
GRID_K2 = [Checks(None, sh, bf) for sh, bf in K2]


def _num(m: dict, k: str) -> float | None:
    v = m.get(k)
    return v if isinstance(v, (int, float)) and math.isfinite(v) else None


def removes(m: dict, ck: Checks) -> bool:
    """Does ``ck`` remove the box with the measurements ``m`` (``stages.measure``)?"""
    if ck.solid_min is not None:
        s = _num(m, "solid")
        if s is not None and s < ck.solid_min:
            return True
    if ck.label_sh is not None:
        sh, bf = _num(m, "stripe_h_ratio"), _num(m, "body_fill")
        if sh is not None and bf is not None and sh > ck.label_sh and bf < ck.label_bf:
            return True
    return False


def kept(meas: list[dict], ck: Checks) -> tuple[int, ...]:
    return tuple(i for i, m in enumerate(meas) if not removes(m, ck))


def apply(found: list, mask: np.ndarray, ck: Checks) -> list:
    """The boxes of ``found`` (``stages.found``) that ``ck`` keeps, as ``Barrel`` objects, in the same order."""
    if ck == OFF:
        return [f.barrel for f in found]
    return [f.barrel for f in found if not removes(sg.measure(f, mask), ck)]
