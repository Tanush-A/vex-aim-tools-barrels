"""The families of settings of the contrast experiment, and how a fold picks one (plan: PREREG.md).

A *family* is a list of ``candidate.Setting``, the most cautious first. Per family the judge gets a function
``fit(train_stems, held_place) -> detect_frame``: it picks one setting of the family on the training places and
returns the detector of that setting; the judge runs it on the held-out place only.

**How a setting is picked inside a fold** (``choose``; the rule of the 2026-11-26 light experiment, word for word,
so the two experiments can be compared):

1. Every setting of the family and today's detector are run on every training frame (the contrast path, today's
   detector, the judge's own counting: ``counting.classify_frame``). Done once for all frames and kept in ``table``.
2. On the training places together, a setting is *allowed* when the standard pass rule (``judge.decide``, with the
   stored margins) does not call it FAIL against today's detector on those places.
3. Among the allowed settings the one with the highest *gain* is taken: gain = (found, per placement) minus (boxes
   that are not on their barrel, per arrangement), each as the difference from today's detector.
4. A tie goes to the setting that comes first in the family (the most cautious). No allowed setting with a gain above
   zero: today's detector, unchanged.

Train frames only: the table is built with ``judge.load_frame``, which refuses anything else.
"""
from __future__ import annotations

import dataclasses
import itertools
import pickle
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidate as cd  # noqa: E402
import common as cm  # noqa: E402

from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402

CACHE = cm.OUT / "cache_v2"           # per-frame counts of every setting (not committed; delete after changing contrast.py)
FIXED = "fixed"                       # the table key of today's detector
S = cd.Setting

# ---------------------------------------------------------------- the families (PREREG.md, "The candidates")

STRENGTHS = (1.3, 1.15, 1.0)          # the mean difference over the predicted width: the larger, the more cautious
D_MIN, ORANGE_MIN, ALIKE_FEAT, EXTENT = 1.1, 0.8, 0.42, 0.15


def grid(mode: str, strengths=STRENGTHS, d=(D_MIN, None), o=(ORANGE_MIN, None), a=(ALIKE_FEAT, None), e=(EXTENT, None)) -> list[S]:
    """Every combination, the most cautious first (a guard on before the same guard off, a high floor before a low one)."""
    return [S(mode=mode, strength_min=k, d_min=dv, orange_min=ov, alike_feat=av, extent_top=ev, extent_bottom=ev)
            for k, dv, ov, av, ev in itertools.product(strengths, d, o, a, e)]


OFF = (None,)
FAMILIES: dict[str, list[S]] = {
    "C1_add_guards": grid("add"),
    "C2_merge_guards": grid("merge"),
    "C3_add_no_guards": grid("add", strengths=(1.5, 1.3, 1.15, 1.0), d=OFF, o=OFF, a=OFF, e=OFF),
    "C4_add_no_abs": grid("add", o=OFF),
}
ALONE = "C5_alone"                    # report only: the numbers C1's fold picked, with the fixed colors switched off
ALONE_OF = "C1_add_guards"
TITLES = {
    "C1_add_guards": "C1 today's boxes plus the contrast path, guards chosen in the fold (primary)",
    "C2_merge_guards": "C2 the contrast path painted into the fixed mask, one detector run, guards chosen in the fold",
    "C3_add_no_guards": "C3 as C1 with no guard at all: only the size for the row and the difference",
    "C4_add_no_abs": "C4 as C1 without the absolute check (the orange part reddish at all)",
    ALONE: "C5 the contrast path alone, fixed colors off, the numbers of C1's fold (report only)",
}


def all_settings() -> list[S]:
    out = [s for fam in FAMILIES.values() for s in fam]
    out += [dataclasses.replace(s, mode="alone") for s in FAMILIES[ALONE_OF]]
    return list(dict.fromkeys(out))


# ---------------------------------------------------------------- every setting on every frame, once

def _frame_counts(args) -> tuple[str, dict]:
    """One frame, many settings -> key -> the frame's counts (``FrameCount.to_dict``)."""
    import cv2
    cv2.setNumThreads(1)
    stem, settings = args
    p = CACHE / f"{stem}.pkl"
    have = pickle.loads(p.read_bytes()) if p.exists() else {}
    todo = [s for s in settings if s.key not in have]
    if todo or FIXED not in have:
        frame = jg.load_frame(stem)                                     # refuses anything but a train frame
        label = io.load_boxes(stem, check_image=False)
        gts = dtp.barrels_from_boxes(label)
        clean = bool(label.get("clean", True))
        fw = cd.FrameWork(frame)
        have[FIXED] = ct.classify_frame(stem, fw.detect(None), gts, clean).to_dict()
        for s in todo:
            have[s.key] = ct.classify_frame(stem, fw.detect(s), gts, clean).to_dict()
        CACHE.mkdir(parents=True, exist_ok=True)
        p.write_bytes(pickle.dumps(have))
    return stem, {k: have[k] for k in [FIXED] + [s.key for s in settings]}


def build_table(stems: list[str], settings: list[S] | None = None, jobs: int = 8, progress: bool = True) -> dict[str, dict]:
    """stem -> setting key -> ``FrameCount``, for every setting on every one of ``stems`` (train frames only)."""
    jg.require_train(stems)
    settings = settings or all_settings()
    table: dict[str, dict] = {}
    with Pool(jobs) as pool:
        for i, (stem, out) in enumerate(pool.imap_unordered(_frame_counts, [(s, settings) for s in stems], chunksize=1)):
            table[stem] = {k: ct.FrameCount.from_dict(v) for k, v in out.items()}
            if progress and (i + 1) % 40 == 0:
                print(f"  table: {i + 1}/{len(stems)} frames x {len(settings)} settings", flush=True)
    return table


# ---------------------------------------------------------------- the rule that picks a setting

def tallies(table: dict, key: str, stems: list[str], placements: ct.Placements) -> tuple[ct.Tally, dict[str, ct.Tally]]:
    counts = {s: table[s][key] for s in stems}
    return ct.tally(counts, stems, placements), {p: ct.tally(counts, ss, placements) for p, ss in ct.group_stems(stems, "place").items()}


def choose(table: dict, family: list[S], stems: list[str], placements: ct.Placements, margins: jg.Margins) -> tuple[S | None, dict]:
    """The setting of ``family`` picked on the frames ``stems`` by the written rule (None = today's detector), and
    what the pick rests on."""
    base, base_places = tallies(table, FIXED, stems, placements)
    best, best_gain, allowed, top = None, 0.0, 0, []
    for st in family:
        cand, cand_places = tallies(table, st.key, stems, placements)
        verdict = jg.decide(base, cand, {p: (base_places[p], cand_places[p]) for p in base_places}, margins)
        if verdict.result == jg.FAIL:
            continue
        allowed += 1
        gain = (cand.found_w - base.found_w) - (cand.extra_w - base.extra_w)
        top.append((gain, st))
        if gain > best_gain + 1e-9:
            best, best_gain = st, gain
    cand, _ = tallies(table, FIXED if best is None else best.key, stems, placements)
    others = sorted((g for g, s in top if s != best), reverse=True)
    return best, {"allowed": allowed, "of": len(family), "gain": round(best_gain, 3), "found_w": round(cand.found_w - base.found_w, 3),
                  "extra_w": round(cand.extra_w - base.extra_w, 3), "runner_up_gain": round(others[0], 3) if others else None}


def describe(st: S | None) -> str:
    return "today's detector, unchanged (no setting allowed with a gain)" if st is None else st.describe()


def detector_of(st: S | None):
    def detect_frame(stem: str, frame) -> list:
        return cd.detect(frame, st)
    detect_frame.describe = describe(st)
    return detect_frame


class Fitter:
    """Holds the table and hands the judge one ``fit`` per family. ``chosen[family][held_place]`` records the picks."""

    def __init__(self, table: dict, placements: ct.Placements, margins: jg.Margins | None = None):
        self.table, self.placements, self.margins = table, placements, margins or jg.load_margins()
        self.chosen: dict[str, dict] = {n: {} for n in list(FAMILIES) + [ALONE]}

    def _pick(self, name: str, train_stems: list[str]) -> tuple[S | None, dict]:
        return choose(self.table, FAMILIES[name], [s for s in train_stems if s in self.table], self.placements, self.margins)

    def fit(self, name: str):
        if name == ALONE:
            return self.fit_alone()

        def fit(train_stems: list[str], held_place: str):
            st, info = self._pick(name, train_stems)
            self.chosen[name][held_place] = {"setting": describe(st), "spec": "" if st is None else st.spec, **info}
            return detector_of(st)
        fit.describe = f"{TITLES[name]}: the setting picked on the other places"
        return fit

    def fit_alone(self):
        """Report only: the setting ``ALONE_OF``'s rule picks on the training places, run with the fixed colors off
        (when the rule picks nothing: the family's most cautious setting, so that there is something to report)."""
        def fit(train_stems: list[str], held_place: str):
            st, info = self._pick(ALONE_OF, train_stems)
            st = dataclasses.replace(st or FAMILIES[ALONE_OF][0], mode="alone")
            self.chosen[ALONE][held_place] = {"setting": describe(st), "spec": st.spec, **info}
            return detector_of(st)
        fit.describe = f"{TITLES[ALONE]}"
        return fit


def fit_family(name: str, jobs: int = 8):
    """``fit(train_stems, held_place)`` for one family, for ``tools/judge.py --cand-fit`` or ``judge.judge(fit=...)``:
    builds (or reads from the cache) the table of that family on the ordinary train frames first."""
    from barrels import conditions as cnd
    ordinary = jg.train_frames()[cnd.ORDINARY]
    settings = FAMILIES[ALONE_OF if name == ALONE else name]
    table = build_table(ordinary, settings, jobs)
    return Fitter(table, jg.load_truth(ordinary).placements).fit(name)


def fit(train_stems: list[str], held_place: str):
    """The primary candidate as the judge's ``--cand-fit``:

        python barrels/tools/judge.py --cand-fit barrels/experiments/2026-11-26_contrast/table.py:fit --no-save
    """
    global _PRIMARY
    if _PRIMARY is None:
        _PRIMARY = fit_family("C1_add_guards")
    return _PRIMARY(train_stems, held_place)


_PRIMARY = None
fit.describe = TITLES["C1_add_guards"] + ": the setting picked on the other places"
