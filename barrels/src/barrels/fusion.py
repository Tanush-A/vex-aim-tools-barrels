"""Fusion of the passing color methods, box by box (experiment 2026-11-27_fusion; plan:
``experiments/2026-11-27_fusion/PREREG.md``).

NOT part of what runs by default: nothing imports this module except that experiment and its tests.

Every color method (fixed colors, contrast, peaks, self-calibration, near-miss, bluer than the light) ends in the same
detector and gives a list of boxes. This module holds the box-level rules that join such lists without slapping
them on top of each other:

- ``Item``: one box, which method drew it, and what the shape checks measure on it (``measure``, a dict made by the
  experiment's ``stages.measure``).
- ``Checks`` / ``removes``: the two shape checks of 2026-11-27_bluer_geom. K1 speckle: the share of the box's barrel
  paint that is solid (its 3 x 3 neighbourhood all barrel color) under ``solid_min``. K2 a label, not a stripe: the
  stripe is taller than ``label_sh`` x the stripe its row predicts AND the box holds less than ``label_bf`` body
  color outside the stripe. A box with no measurement is never removed.
- ``proposals``: the boxes of one method that are on none of the boxes already kept ("on" = half of the smaller box
  inside the other, ``counting.on_share``; color is not asked, so a box of the other color on a kept barrel is no
  proposal).
- ``clusters``: proposals of several methods, joined when same color and on each other. The first method in the
  given order stands for the cluster (its box is drawn).
- ``vote``: a cluster is added when enough independent methods drew it (``k``), optionally plus one vote from outside
  evidence (``extra_vote``, e.g. the contrast response), and its box passes the shape checks.
- ``tidy``: one box per barrel, and no box of the other color on a barrel the fixed colors found.

No pixel is read here: only boxes and their measurements.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

from .counting import on_share
from .detect_types import Barrel

ON = 0.5            # "on": this share of the smaller of two boxes inside the other (counting.ON_SHARE)
INSIDE = 0.8        # tidy (a): a box at least this share inside a larger box of its color is the same barrel twice
FIXED = "FX"        # the method name of today's fixed colors


@dataclass(frozen=True)
class Item:
    barrel: Barrel
    method: str
    measure: dict = field(default_factory=dict, compare=False, hash=False)

    @property
    def bbox(self) -> tuple:
        return self.barrel.bbox

    @property
    def color(self) -> int:
        return self.barrel.color


@dataclass(frozen=True)
class Checks:
    solid_min: float | None = None
    label_sh: float | None = None
    label_bf: float | None = None

    @property
    def key(self) -> str:
        g = lambda v: "-" if v is None else f"{v:g}"      # noqa: E731
        return f"s{g(self.solid_min)}|l{g(self.label_sh)}/{g(self.label_bf)}"


OFF = Checks()
MILD = Checks(0.35, 1.5, 0.6)
STRONG = Checks(0.40, 1.25, 0.6)


def _num(m: dict, k: str) -> float | None:
    v = m.get(k)
    return float(v) if isinstance(v, (int, float)) and math.isfinite(v) else None


def removes(m: dict, ck: Checks) -> bool:
    """Does ``ck`` remove a box with the measurements ``m``? (The rule of 2026-11-27_bluer_geom ``checks.removes``.)"""
    if ck.solid_min is not None:
        s = _num(m, "solid")
        if s is not None and s < ck.solid_min:
            return True
    if ck.label_sh is not None:
        sh, bf = _num(m, "stripe_h_ratio"), _num(m, "body_fill")
        if sh is not None and bf is not None and sh > ck.label_sh and bf < ck.label_bf:
            return True
    return False


def apply_checks(items: list[Item], ck: Checks) -> list[Item]:
    return list(items) if ck == OFF else [it for it in items if not removes(it.measure, ck)]


def is_on(a, b) -> bool:
    return on_share(a.bbox, b.bbox) >= ON


def proposals(items: list[Item], kept: list[Item]) -> list[Item]:
    """The items on none of ``kept`` (any color)."""
    return [it for it in items if not any(is_on(it, k) for k in kept)]


def clusters(by_method: dict[str, list[Item]], order: tuple[str, ...]) -> list[list[Item]]:
    """Proposals of several methods grouped per barrel. Methods are taken in ``order``; an item joins the first
    cluster of its color whose first item it is on, unless its method is in that cluster already (then it starts its
    own). The first item of a cluster is the one drawn."""
    out: list[list[Item]] = []
    for m in order:
        for it in by_method.get(m, []):
            for c in out:
                if c[0].color == it.color and is_on(c[0], it) and all(x.method != m for x in c):
                    c.append(it)
                    break
            else:
                out.append([it])
    return out


def votes(cluster: list[Item], extra_vote: Callable[[Item], bool] | None = None) -> int:
    n = len({it.method for it in cluster})
    return n + (1 if extra_vote is not None and extra_vote(cluster[0]) else 0)


def vote(kept: list[Item], by_method: dict[str, list[Item]], order: tuple[str, ...], k: int | None, ck: Checks = OFF,
         extra_vote: Callable[[Item], bool] | None = None, blocked: list[Item] = ()) -> list[Item]:
    """``kept`` plus every cluster of the methods' proposals with at least ``k`` votes whose drawn box passes ``ck``.
    Clusters are added most votes first (a tie keeps the order of ``clusters``); one on a box already in the answer is
    not added. ``k`` None: nothing is added. ``blocked`` (round 2 of the experiment): boxes the checks removed; a
    proposal on one of them is no proposal (a trap stays a trap, whichever method draws it again)."""
    out = list(kept)
    if k is None:
        return out
    props = {m: [p for p in proposals(v, kept) if not any(is_on(p, b) for b in blocked)] for m, v in by_method.items()}
    cl = clusters(props, order)
    scored = sorted(((votes(c, extra_vote), i, c) for i, c in enumerate(cl)), key=lambda t: (-t[0], t[1]))
    for n, _, c in scored:
        rep = c[0]
        if n < k or removes(rep.measure, ck) or any(is_on(rep, o) for o in out):
            continue
        out.append(rep)
    return out


def _area(b) -> float:
    x0, y0, x1, y1 = b.bbox
    return float((x1 - x0) * (y1 - y0))


def tidy(items: list[Item]) -> list[Item]:
    """Two rules with no number, for boxes that are not from the fixed colors (``FIXED``):
    (a) one box per barrel: such a box at least ``INSIDE`` inside a larger box of the same color is removed;
    (b) such a box on (``ON``) a box of the other color from the fixed colors is removed."""
    out = []
    for it in items:
        if it.method == FIXED:
            out.append(it)
            continue
        if any(o is not it and o.color == it.color and _area(o) > _area(it) and on_share(it.bbox, o.bbox) >= INSIDE
               for o in items):
            continue
        if any(o.method == FIXED and o.color != it.color and is_on(it, o) for o in items):
            continue
        out.append(it)
    return out


def barrels(items: list[Item]) -> list[Barrel]:
    """The boxes, left to right."""
    return sorted((it.barrel for it in items), key=lambda b: b.bbox[0])
