"""The judged candidates of the white-balance experiment (PREREG.md). EXPERIMENT ONLY: the standing rule forbids
correcting the image; nothing here may be adopted without Dave.

F1..F5: full correction (alpha 1), one estimator each, no chosen number: a plain ``detect_frame``.
P1..P5: the same estimators, alpha chosen inside each fold from {0.25, 0.5, 0.75, 1.0}. P3 is the primary.
U3: today's mask, plus the without_loose-corrected photo's class where today paints nothing; alpha chosen in the fold.

How a setting is picked inside a fold (the light experiment's rule): every setting and the fixed model run on every
ordinary train frame (``table``, built once); on the training places together a setting the standard pass rule calls
FAIL against the fixed model is out; the highest gain (Δ found per placement − Δ boxes not on their barrel) wins; a
tie goes to the smaller alpha; no allowed setting with a gain above zero = no correction.
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wb  # noqa: E402

from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402

S = wb.Setting
NUM = {e: i + 1 for i, e in enumerate(wb.ESTIMATORS)}

FULL = {f"F{NUM[e]}_{e}": S(e, 1.0) for e in wb.ESTIMATORS}
FAMILIES = {f"P{NUM[e]}_{e}_partial": [S(e, a) for a in wb.ALPHAS] for e in wb.ESTIMATORS}
FAMILIES["U3_without_loose_added"] = [S("without_loose", a, True) for a in wb.ALPHAS]

TITLES = {**{k: f"{k.split('_')[0]} {st.estimator}, full correction" for k, st in FULL.items()},
          **{k: f"{k.split('_')[0]} {fam[0].estimator}, partial (alpha chosen in the fold)" + (" (primary)" if k.startswith("P3") else "") for k, fam in FAMILIES.items()}}
TITLES["U3_without_loose_added"] = "U3 today's mask plus the without_loose-corrected paint where today paints nothing (alpha in the fold)"


def all_settings() -> list[S]:
    return list(dict.fromkeys([wb.FIXED] + list(FULL.values()) + [s for f in FAMILIES.values() for s in f]))


def _frame_counts(args):
    import cv2
    cv2.setNumThreads(1)
    stem, keys = args
    frame = jg.load_frame(stem)
    label = io.load_boxes(stem, check_image=False)
    gts = dtp.barrels_from_boxes(label)
    out = {}
    for k in keys:
        preds = wb.detect(frame, S.from_key(k))
        out[k] = ct.classify_frame(stem, preds, gts, bool(label.get("clean", True))).to_dict()
    return stem, out


def build_table(stems: list[str], settings: list[S] | None = None, jobs: int = 8) -> dict[str, dict]:
    """stem -> setting key -> FrameCount (train frames only)."""
    jg.require_train(stems)
    keys = [s.key for s in (settings or all_settings())]
    table = {}
    with Pool(jobs) as pool:
        for i, (stem, out) in enumerate(pool.imap_unordered(_frame_counts, [(s, keys) for s in stems], chunksize=1)):
            table[stem] = {k: ct.FrameCount.from_dict(v) for k, v in out.items()}
            if (i + 1) % 40 == 0:
                print(f"  table: {i + 1}/{len(stems)}", flush=True)
    return table


def tallies(table, key, stems, placements):
    counts = {s: table[s][key] for s in stems}
    return ct.tally(counts, stems, placements), {p: ct.tally(counts, ss, placements) for p, ss in ct.group_stems(stems, "place").items()}


def choose(table, family, stems, placements, margins):
    base, base_places = tallies(table, wb.FIXED.key, stems, placements)
    best, best_gain, allowed, rows = wb.FIXED, 0.0, 0, []
    for st in family:
        cand, cand_places = tallies(table, st.key, stems, placements)
        v = jg.decide(base, cand, {p: (base_places[p], cand_places[p]) for p in base_places}, margins)
        gain = (cand.found_w - base.found_w) - (cand.extra_w - base.extra_w)
        rows.append({"setting": st.describe(), "verdict": v.result, "gain": round(gain, 3), "found_w": round(cand.found_w - base.found_w, 3), "extra_w": round(cand.extra_w - base.extra_w, 3)})
        if v.result == jg.FAIL:
            continue
        allowed += 1
        if gain > best_gain + 1e-9:
            best, best_gain = st, gain
    return best, {"allowed": allowed, "of": len(family), "gain": round(best_gain, 3), "all": rows}


class Fitter:
    def __init__(self, table, placements, margins=None):
        self.table, self.placements, self.margins = table, placements, margins or jg.load_margins()
        self.chosen: dict[str, dict] = {n: {} for n in FAMILIES}

    def fit(self, name: str):
        family = FAMILIES[name]

        def fit(train_stems, held_place):
            st, info = choose(self.table, family, [s for s in train_stems if s in self.table], self.placements, self.margins)
            self.chosen[name][held_place] = {"setting": st.describe(), "key": st.key, **info}
            return wb.detector_for(st)
        fit.describe = f"{TITLES[name]}: the setting picked on the other places"
        return fit
