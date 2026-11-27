"""The judged candidates of the self-calibration experiment (PREREG.md), for the standard pass rule.

    python barrels/tools/judge.py --cand-fit barrels/experiments/2026-11-26_selfcal/candidates.py:fit_AB
    python barrels/tools/judge.py --cand-fit barrels/experiments/2026-11-26_selfcal/candidates.py:fit_B_local
    python barrels/tools/judge.py --cand-callable barrels/experiments/2026-11-26_selfcal/candidates.py:detect_noguard

Four families, each a ``fit(train_stems, held_place) -> detect_frame``: the few numbers of ``GRIDS`` are chosen on the
training places by ``choose`` (the rule is in its docstring and in PREREG.md), and the detector with the chosen
numbers is run on the held-out place only.

    A_found   seeds = the first pass's unflagged boxes; their colors widen the frame's ranges
    B_local   seeds = half-found barrels; each one's missing color is painted inside its own box only
    B_frame   seeds = half-found barrels; their colors widen the frame's ranges (no local paint)
    AB        all seeds, local paint and frame ranges

``detect_noguard`` is AB with every guard off (no fitted number): what the guards are worth.

Every (setting, frame) is run once and kept in memory, so the folds and the families share the work.
"""
from __future__ import annotations

import dataclasses

import common as cm
from barrels import counting as ct
from barrels import detector as det
from barrels import judge as jg
from barrels import selfcal as sc

C = sc.SelfCalConfig
BASE = {
    "A_found": C(seed_body=False, seed_stripe=False, local=False),
    "B_local": C(seed_found=False, frame=False),
    "B_frame": C(seed_found=False, local=False),
    "AB": C(),
}
# the numbers chosen leave one place out; the most careful setting first (a tie keeps the earlier one)
_FRAME_GRID = [dict(rel_margin=r, hue_move_max=m, flood_max=f) for r in (1.0, 0.5) for m in (6.0, 10.0) for f in (0.01, 0.03)]
GRIDS = {
    "A_found": [dict(found_flags=g, hue_move_max=m, flood_max=f) for g in ("none", "any") for m in (6.0, 10.0) for f in (0.01, 0.03)],
    "B_local": [dict(rel_margin=r) for r in (1.0, 0.5)],
    "B_frame": _FRAME_GRID,
    "AB": _FRAME_GRID,
}
NOGUARD = C(rel_margin=-99.0, surround_sides_max=99, agree_hue=999.0, hue_spread_max=999.0, min_range_px=0, flood_max=1.0, seed_rules=False)

_first: dict = {}        # stem -> (mask of the fixed model, its boxes): the same for every setting
_boxes: dict = {}        # (setting, stem) -> the boxes
_gts: dict = {}          # stem -> (true barrels, clean flag)
CHOSEN: dict = {}        # (family, held place) -> {"setting": ..., "table": [...]}: what each fold picked, for the report
_cal: dict = {}


def settings(family: str) -> list[C]:
    return [dataclasses.replace(BASE[family], **kw) for kw in GRIDS[family]]


def cal(cfg: C) -> sc.SelfCal:
    if cfg not in _cal:
        _cal[cfg] = sc.SelfCal(cm.MODEL, cfg, cm.CAM)
    return _cal[cfg]


def ensure(cfgs: list[C], stems: list[str]) -> None:
    """Run every setting on every frame that has not been run yet. Each image is read once (train frames only)."""
    for s in stems:
        todo = [c for c in cfgs if (c, s) not in _boxes]
        if not todo and s in _first:
            continue
        frame = jg.load_frame(s)
        if s not in _first:
            _first[s] = cal(todo[0] if todo else cfgs[0]).first_pass(frame)
        for c in todo:
            _boxes[(c, s)] = cal(c).run(frame, first=_first[s]).boxes


def gts(stem: str):
    if stem not in _gts:
        g, clean = ct.load_gts([stem])
        _gts[stem] = (g[stem], clean[stem])
    return _gts[stem]


def tally(boxes_of, stems: list[str], placements) -> ct.Tally:
    counts = {s: ct.classify_frame(s, boxes_of(s), gts(s)[0], gts(s)[1]) for s in stems}
    return ct.tally(counts, stems, placements)


def choose(family: str, train_stems: list[str]) -> tuple[C | None, list[dict]]:
    """The setting for one fold, from the training places only.

    Every setting of the family's grid and the fixed detector are counted on the training frames, the way the judge
    counts (placements; boxes once per arrangement). A setting is out if, against the fixed detector on those frames,
    it would fail one of the judge's box clauses: boxes that are not on their barrel up by more than the judge's
    margin, any more box on a clean empty frame, or boxes on empty frames with clutter up by more than the margin.
    Of the rest, the one that finds the most placements wins; a tie keeps the more careful one (earlier in the grid).
    If none is left, or none finds more than the fixed detector, the fold uses the fixed detector (None)."""
    cfgs = settings(family)
    ensure(cfgs, train_stems)
    m = jg.load_margins()
    placements = ct.build_placements({s: gts(s)[0] for s in train_stems})
    base = tally(lambda s: _first[s][1], train_stems, placements)
    best, table = None, []
    for kw, cfg in zip(GRIDS[family], cfgs):
        t = tally(lambda s, c=cfg: _boxes[(c, s)], train_stems, placements)
        ok = (t.extra_w - base.extra_w <= m.extra_rise + jg.EPS and t.clean_empty - base.clean_empty <= m.clean_empty + jg.EPS
              and t.cluttered_empty_w - base.cluttered_empty_w <= m.cluttered_empty + jg.EPS)
        table.append({**kw, "found_w": round(t.found_w, 2), "found": t.found, "extra_w": round(t.extra_w, 2), "clean_empty": t.clean_empty,
                      "cluttered_empty_w": round(t.cluttered_empty_w, 2), "allowed": bool(ok)})
        if ok and t.found_w > base.found_w + jg.EPS and (best is None or t.found_w > best[1] + jg.EPS):
            best = (cfg, t.found_w, kw)
    table.append({"fixed": True, "found_w": round(base.found_w, 2), "found": base.found, "extra_w": round(base.extra_w, 2),
                  "clean_empty": base.clean_empty, "cluttered_empty_w": round(base.cluttered_empty_w, 2)})
    return (best[0] if best else None), table


def _fixed(stem: str, frame) -> list:
    if stem not in _first:
        _first[stem] = cal(BASE["AB"]).first_pass(frame)
    return _first[stem][1]


def make_fit(family: str):
    def fit(train_stems: list[str], held_place: str):
        cfg, table = choose(family, list(train_stems))
        kw = None if cfg is None else next(k for k, c in zip(GRIDS[family], settings(family)) if c == cfg)
        CHOSEN[(family, held_place)] = {"setting": kw, "table": table}
        if cfg is None:
            _fixed.describe = f"{family}: the fixed detector (no setting was better on the training places), picked without {held_place}"
            return _fixed

        def detect(stem: str, frame) -> list:
            if (cfg, stem) not in _boxes:
                if stem not in _first:
                    _first[stem] = cal(cfg).first_pass(frame)
                _boxes[(cfg, stem)] = cal(cfg).run(frame, first=_first[stem]).boxes
            return _boxes[(cfg, stem)]
        detect.describe = f"{family} with {kw}, picked without {held_place}"
        return detect
    fit.describe = f"selfcal {family}: {len(GRIDS[family])} settings, one picked per fold on the other places (candidates.py: choose)"
    fit.__name__ = f"fit_{family}"
    return fit


fit_A_found = make_fit("A_found")
fit_B_local = make_fit("B_local")
fit_B_frame = make_fit("B_frame")
fit_AB = make_fit("AB")


def detect_noguard(stem: str, frame) -> list:
    """AB with every guard off: any strict body gap or stripe band of the right size is a seed, nothing is checked on
    the photo, readings need not agree, no flood limit. No fitted number."""
    if (NOGUARD, stem) not in _boxes:
        _boxes[(NOGUARD, stem)] = cal(NOGUARD).run(frame).boxes
    return _boxes[(NOGUARD, stem)]


detect_noguard.describe = "selfcal AB with every guard off (photo check, surround, agreement, flood limit, seed color rule)"
__all__ = ["fit_A_found", "fit_B_local", "fit_B_frame", "fit_AB", "detect_noguard", "det"]
