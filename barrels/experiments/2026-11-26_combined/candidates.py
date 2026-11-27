"""The judged candidates of experiment 2026-11-26_combined (TODO E8; plan: PREREG.md in this folder).

    python barrels/tools/judge.py --cand-fit barrels/experiments/2026-11-26_combined/candidates.py:fit_nm_then_sc
    python barrels/tools/judge.py --cand-fit barrels/experiments/2026-11-26_combined/candidates.py:fit_box_union
    python barrels/tools/judge.py --cand-callable barrels/experiments/2026-11-26_combined/candidates.py:detect_nm_then_sc   # fixed numbers: IN-SAMPLE

Run with ``PYTHONPATH=barrels/src`` from the checkout this file is in (``cb_common`` stops otherwise).

Five ways to run the two winners on one frame (``barrels.combined``), each a ``fit(train_stems, held_place) ->
detect_frame`` for the standard judge, leave one place out:

    fit_nm_then_sc    near-miss paint first, then self-calibration on that mask
    fit_sc_then_nm    self-calibration first, then near-miss paint on its mask
    fit_mask_union    each alone on the fixed mask, the two masks together, one detector pass
    fit_box_union     each alone from start to end, the boxes merged
    fit_box_agree     each alone; a box today's detector did not draw stays only when both drew it

and the two winners alone, with their own code and nothing of this folder: ``fit_nearmiss`` (nearmiss
``candidates.fit_partner``), ``fit_selfcal`` (selfcal ``candidates.fit_AB``).

**No number is chosen here.** In each fold each step gets the setting ITS OWN rule picks on the training places, for
that step alone (``fold_settings``): the near-miss step by ``nm_common.choose`` over its 65 settings, self-calibration
by its ``candidates.choose`` over its 8. The combination itself is never scored on the training places.

``detect_<way>(stem, frame)``: the same five with the two fixed settings the winners offered (near-miss
``pc:5,5,pred``; self-calibration ``rel_margin`` 1.0, ``hue_move_max`` 6, ``flood_max`` 0.03). With fixed numbers a
judged result is IN-SAMPLE; the held-out result is the ``fit_`` one. ``fit`` and ``detect_frame`` (bottom of the file)
name the candidate the experiment ends on; they are set after the judged runs.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cb_common as cb  # noqa: E402

import best as sc_best  # noqa: E402  (selfcal's best.py: its fixed setting)
from barrels import combined as cmb  # noqa: E402
from barrels import selfcal as sc  # noqa: E402

MODEL, CAM = cb.scc.MODEL, cb.scc.CAM           # the adopted color model (never changed) and the camera
JOBS = 8
CHOSEN: dict[str, dict] = {}                    # held-out place -> {"nm": spec, "sc": the grid entry or None}: what each winner's rule picked
SECONDS: dict[str, list] = {}                   # way -> [seconds in the combination, frames]: the cost per frame, the fit left out

NM_FIXED = cb.nm_cand.FINAL_SPEC                # "pc:5,5,pred"
SC_FIXED = sc.SelfCalConfig(rel_margin=1.0, hue_move_max=6.0, flood_max=0.03)
assert SC_FIXED == sc_best.CONFIG, "selfcal's best.py no longer holds the setting written here"


def nm_config(spec: str):
    """The near-miss config of a spec of its grid; None for ``fixed`` (the step is off)."""
    p = cb.nmc.parse(spec)
    return None if p[0] == "fixed" else p[1]


def fold_settings(train_stems, held_place: str) -> tuple[str, sc.SelfCalConfig | None]:
    """(the near-miss spec, the self-calibration config or None) for one fold: each winner's own selection rule, run
    on the training places only, for that winner alone. Kept per held-out place, so the five ways share one choice."""
    if held_place not in CHOSEN:
        spec, _ = cb.nmc.choose(cb.nm_cand.GRID_B, list(train_stems), jobs=JOBS)
        cfg, _ = cb.sc_cand.choose("AB", list(train_stems))
        kw = None if cfg is None else next(k for k, c in zip(cb.sc_cand.GRIDS["AB"], cb.sc_cand.settings("AB")) if c == cfg)
        CHOSEN[held_place] = {"nm": spec, "sc": kw, "_sc_cfg": cfg, "_n_train": len(list(train_stems))}
    c = CHOSEN[held_place]
    return c["nm"], c["_sc_cfg"]


def _detector(way: str, nm_spec: str, sc_cfg, note: str):
    fn, nm_cfg = cmb.WAYS[way], nm_config(nm_spec)

    def detect_frame(stem: str, frame) -> list:
        t0 = time.perf_counter()
        boxes = fn(frame, MODEL, nm_cfg, sc_cfg, CAM).boxes
        t = SECONDS.setdefault(way, [0.0, 0])
        t[0] += time.perf_counter() - t0
        t[1] += 1
        return boxes
    detect_frame.describe = f"combined {way}: near-miss {nm_spec}; self-calibration {'off' if sc_cfg is None else _sc_words(sc_cfg)}; {note}"
    detect_frame.way, detect_frame.nm_spec, detect_frame.sc_cfg = way, nm_spec, sc_cfg
    return detect_frame


def _sc_words(cfg) -> str:
    return f"rel_margin {cfg.rel_margin:g}, hue_move_max {cfg.hue_move_max:g}, flood_max {cfg.flood_max:g}"


def make_fit(way: str):
    def fit(train_stems, held_place: str):
        spec, cfg = fold_settings(train_stems, held_place)
        return _detector(way, spec, cfg, f"each picked by its own rule without {held_place}")
    fit.describe = (f"combined {way} (barrels.combined): in each fold the near-miss setting is picked by nearmiss's own rule and the "
                    f"self-calibration setting by selfcal's own rule, each on the other places; nothing is chosen for the combination")
    fit.__name__ = f"fit_{way}"
    fit.way = way
    return fit


fit_nm_then_sc = make_fit("nm_then_sc")
fit_sc_then_nm = make_fit("sc_then_nm")
fit_mask_union = make_fit("mask_union")
fit_box_union = make_fit("box_union")
fit_box_agree = make_fit("box_agree")
fit_nearmiss = cb.nm_cand.fit_partner           # the winners alone: their own code, untouched
fit_selfcal = cb.sc_cand.fit_AB
FITS = {"nearmiss": fit_nearmiss, "selfcal": fit_selfcal, "nm_then_sc": fit_nm_then_sc, "sc_then_nm": fit_sc_then_nm,
        "mask_union": fit_mask_union, "box_union": fit_box_union, "box_agree": fit_box_agree}

# ---------------------------------------------------------------- fixed numbers (in-sample when judged)
detect_nm_then_sc = _detector("nm_then_sc", NM_FIXED, SC_FIXED, "fixed numbers: in-sample when judged")
detect_sc_then_nm = _detector("sc_then_nm", NM_FIXED, SC_FIXED, "fixed numbers: in-sample when judged")
detect_mask_union = _detector("mask_union", NM_FIXED, SC_FIXED, "fixed numbers: in-sample when judged")
detect_box_union = _detector("box_union", NM_FIXED, SC_FIXED, "fixed numbers: in-sample when judged")
detect_box_agree = _detector("box_agree", NM_FIXED, SC_FIXED, "fixed numbers: in-sample when judged")
detect_nearmiss = cb.nm_cand.detect_frame
detect_selfcal = sc_best.detect_frame
FIXED = {"nearmiss": detect_nearmiss, "selfcal": detect_selfcal, "nm_then_sc": detect_nm_then_sc, "sc_then_nm": detect_sc_then_nm,
         "mask_union": detect_mask_union, "box_union": detect_box_union, "box_agree": detect_box_agree}


def run(way: str, frame, nm_spec: str = NM_FIXED, sc_cfg=SC_FIXED) -> cmb.Combined:
    """One frame through one way, everything kept (masks, seeds): for pictures and for the analysis of what is left."""
    return cmb.WAYS[way](frame, MODEL, nm_config(nm_spec), sc_cfg, CAM)


def settings_json(place: str) -> dict:
    """What the judged run picked for a place, as written in results/.../chosen.json: {"nm": spec, "sc": the grid
    entry or None}. A place that is not an ordinary one gets what was picked on all the ordinary frames."""
    import json
    d = json.loads((cb.RESULTS / "chosen.json").read_text())
    return d.get(place) or d["(any place that is not an ordinary one)"]


def settings_for(place: str) -> tuple[str, sc.SelfCalConfig | None]:
    """What the judged run used at a place (after a judged run in this process, or from results/.../chosen.json)."""
    if place in CHOSEN:
        return CHOSEN[place]["nm"], CHOSEN[place]["_sc_cfg"]
    import dataclasses
    c = settings_json(place)
    return c["nm"], (None if c["sc"] is None else dataclasses.replace(cb.sc_cand.BASE["AB"], **c["sc"]))


# ---------------------------------------------------------------- the third winner (PREREG addendum, 2026-11-27)
# Contrast's own fold rule runs in a process of its own (cn_picks.py: its folder has a common.py too, and its rule builds
# its table in a process pool). It writes the setting its rule picks for each held-out place, on the other places,
# alone: results/2026-11-26_combined/cn_chosen.json. Nothing is chosen here.

from barrels import contrast as cn  # noqa: E402

CN_FIXED = cn.Params(strength_min=1.15, orange_min=0.8, extent_top=0.15, extent_bottom=0.15)    # contrast's candidate.BEST
ANY_PLACE = "(any place that is not an ordinary one)"
_CN: dict | None = None


def cn_params(held_place: str):
    """The contrast setting contrast's own rule picked without ``held_place`` (cn_chosen.json); None = its rule kept
    today's detector. A place that is not an ordinary one gets the pick on all ordinary places."""
    global _CN
    if _CN is None:
        import json
        _CN = json.loads((cb.RESULTS / "cn_chosen.json").read_text())
    c = _CN.get(held_place, _CN[ANY_PLACE])
    return None if c is None else cn.Params(**c["params"])


def _detector3(way: str, nm_spec: str, sc_cfg, cn_p, note: str):
    fn, nm_cfg = cmb.WAYS3[way], nm_config(nm_spec)

    def detect_frame(stem: str, frame) -> list:
        t0 = time.perf_counter()
        boxes = fn(frame, MODEL, nm_cfg, sc_cfg, CAM, None, cn_p).boxes
        t = SECONDS.setdefault(way, [0.0, 0])
        t[0] += time.perf_counter() - t0
        t[1] += 1
        return boxes
    detect_frame.describe = f"combined {way}: near-miss {nm_spec}; self-calibration {'off' if sc_cfg is None else _sc_words(sc_cfg)}; contrast {cn_p}; {note}"
    return detect_frame


def make_fit3(way: str):
    def fit(train_stems, held_place: str):
        spec, cfg = fold_settings(train_stems, held_place)
        return _detector3(way, spec, cfg, cn_params(held_place), f"each picked by its own rule without {held_place}")
    fit.describe = (f"combined {way} (barrels.combined.WAYS3): near-miss, self-calibration and contrast settings each picked by that winner's "
                    f"own rule on the other places; nothing is chosen for the combination")
    fit.__name__ = f"fit_{way}"
    fit.way = way
    return fit


FITS3 = {w: make_fit3(w) for w in cmb.WAYS3}
FIXED3 = {w: _detector3(w, NM_FIXED, SC_FIXED, CN_FIXED, "fixed numbers: in-sample when judged") for w in cmb.WAYS3}


def settings3_for(place: str):
    """(near-miss spec, self-calibration config, contrast params) the judged run used at a place."""
    spec, cfg = settings_for(place)
    return spec, cfg, cn_params(place)


# ---------------------------------------------------------------- the candidate the experiment ends on
# Set after the judged runs. The two-way rule (run.py, pick) gave mask_union (152.8). The addendum's rule (run3.py, pick)
# then gave CONTRAST ALONE (155.3): no combination is PASS against it. So the answer is contrast alone. Its own code is
# the reference: experiments/2026-11-26_contrast/table.py:fit (held out) and candidate.py:detect_frame (fixed numbers);
# `fit` / `detect_frame` here are the same thing built from barrels.combined (identical judge pages: run3_checks.json).
best_two_way_fit, best_two_way_detect_frame = fit_mask_union, detect_mask_union
fit = FITS3["cn_alone"]
detect_frame = FIXED3["cn_alone"]
