"""The fusion candidates of PREREG.md, as the judge runs them.

    python barrels/tools/judge.py --cand-fit barrels/experiments/2026-11-27_fusion/fuse.py:fit_F5

Per frame, ``record(stem)`` holds every box every method draws at every setting any fold uses (cached in
``results/2026-11-27_fusion/cache/``, not committed). A candidate is a function of a record, the fold's bundle of
method picks (``methods.bundle``) and its own choice (the checks; k). ``Fitter`` picks the choice inside each fold on
the other places (the rule of PREREG.md) and hands the judge a ``fit(train_stems, held_place) -> detect_frame``.
"""
from __future__ import annotations

import pickle
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import methods as M  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import fusion as fu  # noqa: E402
from barrels import judge as jg  # noqa: E402

OUT = M.RES / "2026-11-27_fusion"
CACHE = OUT / "cache"
CHECKS = (fu.OFF, fu.MILD, fu.STRONG)               # most cautious first = off
ORDER = ("SC", "P2", "NM", "B4")
VERSION = 1


# ---------------------------------------------------------------- one frame, every method at every pick

def _c1_specs():
    return sorted({b["C1"] for b in M.bundles()})


def build_record(stem: str, frame=None) -> dict:
    frame = frame if frame is not None else jg.load_frame(stem)     # refuses anything but a train frame
    fr = M.Frame(frame)
    rec: dict = {"v": VERSION, "FX:def": fr.fixed("def"), "FX:flags": fr.fixed("flags")}
    for spec in _c1_specs():
        for cfg in ("def", "flags"):
            rec[f"C1:{spec}:{cfg}"] = fr.c1(spec, cfg)[0]
    for b in M.bundles():
        for m in ORDER:
            rec[mkey(m, b)] = fr.method_items(m, b)
        for ck in CHECKS:
            kept = fu.apply_checks(rec[f"C1:{b['C1']}:flags"], ck)
            rec[f"F4:{M.bundle_key(b)}:{ck.key}"] = fr.f4(b, kept, ck)
    rec["LOW"] = fr.low_candidates()
    return rec


def mkey(m: str, b: dict) -> str:
    sub = {"SC": M.sc_key(b["SC"]), "P2": M.p2_key(b["P2"]), "NM": b["NM"], "B4": b["B4"]}[m]
    return f"M:{m}:{sub}"


_REC: dict = {}


def record(stem: str, frame=None) -> dict:
    if stem in _REC:
        return _REC[stem]
    p = CACHE / f"{stem}.pkl"
    if p.exists():
        rec = pickle.loads(p.read_bytes())
        if rec.get("v") == VERSION:
            _REC[stem] = rec
            return rec
    rec = build_record(stem, frame)
    CACHE.mkdir(parents=True, exist_ok=True)
    p.write_bytes(pickle.dumps(rec))
    _REC[stem] = rec
    return rec


def _work(stem):
    import cv2
    cv2.setNumThreads(1)
    record(stem)
    return stem


def prepare(stems, jobs: int = 8) -> None:
    jg.require_train(stems)
    todo = [s for s in stems if not (CACHE / f"{s}.pkl").exists()]
    if todo:
        with Pool(jobs) as pool:
            for i, _ in enumerate(pool.imap_unordered(_work, todo, chunksize=1)):
                if (i + 1) % 25 == 0:
                    print(f"  records {i + 1}/{len(todo)}", flush=True)


# ---------------------------------------------------------------- the candidates: (record, bundle, choice) -> items

def contrast_vote(rec: dict):
    low = rec["LOW"]

    def v(it: fu.Item) -> bool:
        x0, y0, x1, y1 = it.bbox
        return any(c == it.color and x0 <= x < x1 and y0 <= y < y1 for c, x, y, _ in low)
    return v


def others(rec, b):
    return {m: rec[mkey(m, b)] for m in ORDER}


def f0(rec, b, ch=None):
    return rec[f"C1:{b['C1']}:def"]


def f1(rec, b, ck):
    return fu.apply_checks(rec[f"C1:{b['C1']}:flags"], ck)


def f1a(rec, b, ck):
    return fu.apply_checks(rec[f"C1:{b['C1']}:def"], ck)


def f1b(rec, b, ck=None):
    return rec[f"C1:{b['C1']}:flags"]


def f2(rec, b, ch):
    ck, k = ch
    return fu.vote(f1(rec, b, ck), others(rec, b), ORDER, k, ck)


def f3(rec, b, ch):
    ck, k = ch
    return fu.vote(f1(rec, b, ck), others(rec, b), ORDER, k, ck, contrast_vote(rec))


def f4(rec, b, ck):
    return f1(rec, b, ck) + rec[f"F4:{M.bundle_key(b)}:{ck.key}"]


def f5(rec, b, ch):
    ck, k = ch
    return fu.vote(f4(rec, b, ck), others(rec, b), ORDER, k, ck, contrast_vote(rec))


def f6(rec, b, ch):
    return fu.tidy(f5(rec, b, ch))


def today(rec, b=None, ch=None):
    return rec["FX:def"]


KS4 = (None, 4, 3, 2)
KS5 = (None, 5, 4, 3, 2)
# name -> (function, the choices in order (most cautious first), "checks" = the choice is the checks / "k" = k with F1's checks)
CANDS = {
    "today": (today, (None,), None),
    "F0": (f0, (None,), None),
    "F1": (f1, CHECKS, "checks"),
    "F1a": (f1a, None, "F1"),          # report only: at F1's pick
    "F1b": (f1b, (None,), None),       # report only
    "F2": (f2, KS4, "k"),
    "F3": (f3, KS5, "k"),
    "F4": (f4, None, "F1"),            # no number of its own: F1's checks
    "F5": (f5, KS5, "k"),
    "F6": (f6, KS5, "k"),
}
TITLES = {
    "F0": "F0 contrast alone (C1 as judged on wip/exp-contrast)",
    "F1": "F1 contrast + seams + bottom rule + shape checks (checks chosen in the fold)",
    "F1a": "F1a contrast + shape checks only (report only, F1's picks)",
    "F1b": "F1b contrast + seams + bottom rule, no checks (report only)",
    "F2": "F2 F1, then boxes of SC/P2/NM/B4 kept when k of them agree and the checks pass",
    "F3": "F3 as F2, the contrast response one more voter",
    "F4": "F4 contrast says where, SC/P2/NM paint the colors there",
    "F5": "F5 F4, then F3's votes",
    "F6": "F6 F5 + tidy (one box per barrel; no other-color box on a fixed barrel)",
}


def boxes(name: str, rec: dict, b: dict, choice) -> list:
    return fu.barrels(CANDS[name][0](rec, b, choice))


def describe_choice(name: str, choice) -> str:
    kind = CANDS[name][2]
    if kind == "checks" or kind == "F1":
        return f"checks {choice.key}"
    if kind == "k":
        ck, k = choice
        return f"checks {ck.key}, k {'off' if k is None else k}"
    return "-"


# ---------------------------------------------------------------- the rule that picks a choice in a fold

class Fitter:
    def __init__(self, truth: jg.Truth, margins: jg.Margins | None = None):
        self.truth = truth
        self.margins = margins or jg.load_margins()
        self.chosen: dict[str, dict] = {n: {} for n in CANDS}
        self._counts: dict = {}
        self._f1: dict = {}

    def counts(self, name, stems, b, choice):
        out = {}
        for s in stems:
            k = (name, s, M.bundle_key(b), describe_choice(name, choice))
            if k not in self._counts:
                self._counts[k] = ct.classify_frame(s, boxes(name, record(s), b, choice), self.truth.gts[s], self.truth.clean[s])
            out[s] = self._counts[k]
        return out

    def tallies(self, counts, stems):
        return ct.tally(counts, stems, self.truth.placements), {p: ct.tally(counts, ss, self.truth.placements)
                                                               for p, ss in ct.group_stems(stems, "place").items()}

    def choose(self, name: str, stems: list[str], held: str):
        b = M.bundle(held)
        fn, options, kind = CANDS[name]
        if kind is None:
            return None, {}
        if kind == "F1":
            return self.f1_pick(stems, held), {"from": "F1"}
        if kind == "k":
            ck = self.f1_pick(stems, held)
            options = [(ck, k) for k in options]
        base_t, base_p = self.tallies(self.counts("today", stems, b, None), stems)
        f0_t, f0_p = self.tallies(self.counts("F0", stems, b, None), stems)
        best, best_gain, rows = None, None, []
        for ch in options:
            t, tp = self.tallies(self.counts(name, stems, b, ch), stems)
            v1 = jg.decide(base_t, t, {p: (base_p[p], tp[p]) for p in base_p}, self.margins)
            v2 = jg.decide(f0_t, t, {p: (f0_p[p], tp[p]) for p in f0_p}, self.margins)
            ok = v1.result != jg.FAIL and v2.result != jg.FAIL
            gain = (t.found_w - base_t.found_w) - (t.extra_w - base_t.extra_w)
            rows.append({"choice": describe_choice(name, ch), "found_w": round(t.found_w, 2), "extra_w": round(t.extra_w, 2),
                         "gain": round(gain, 3), "vs_today": v1.result, "vs_F0": v2.result, "allowed": ok})
            if best is None:                                  # the first option (checks off / k off) is the fallback
                best, best_gain = ch, (gain if ok else float("-inf"))
                continue
            if ok and gain > best_gain + 1e-9:
                best, best_gain = ch, gain
        return best, {"table": rows}

    def f1_pick(self, stems, held):
        if held not in self._f1:
            ch, info = self.choose("F1", stems, held)
            self._f1[held] = ch
            self.chosen["F1"].setdefault(held, {"choice": describe_choice("F1", ch), **info})
        return self._f1[held]

    def fit(self, name: str):
        def fit(train_stems: list[str], held_place: str):
            stems = [s for s in train_stems if s in self.truth.gts]
            ch, info = self.choose(name, stems, held_place)
            self.chosen[name][held_place] = {"choice": describe_choice(name, ch), **info}
            b = M.bundle(held_place)

            def detect_frame(stem: str, frame) -> list:
                return boxes(name, record(stem, frame), b, ch)
            detect_frame.describe = f"{TITLES[name]}: {describe_choice(name, ch)} (picked without {held_place})"
            return detect_frame
        fit.describe = TITLES[name] + ": its choice picked on the other places"
        return fit


_FITTER: Fitter | None = None


def fitter() -> Fitter:
    global _FITTER
    if _FITTER is None:
        fr = jg.train_frames()
        stems = fr[cnd.ORDINARY] + fr[cnd.EXTREME] + fr[cnd.UNLISTED]
        prepare(stems)
        _FITTER = Fitter(jg.load_truth(stems))
    return _FITTER


def _cli_fit(name):
    def fit(train_stems, held_place):
        return fitter().fit(name)(train_stems, held_place)
    fit.describe = TITLES[name]
    return fit


fit_F0, fit_F1, fit_F2, fit_F3, fit_F4, fit_F5, fit_F6 = (_cli_fit(n) for n in ("F0", "F1", "F2", "F3", "F4", "F5", "F6"))
