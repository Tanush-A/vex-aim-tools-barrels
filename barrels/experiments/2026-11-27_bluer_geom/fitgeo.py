"""The families of this experiment and how a fold picks one member (plan: PREREG.md).

A member is a pair (a color step of the light experiment, ``rules.Setting``; a set of checks, ``checks.Checks``). Its
detector: the color step, ``detector.detect`` (via ``stages.found``, the same boxes), then the checks take boxes away.

**How a member is picked inside a fold** (``choose``): the rule of the light experiment, word for word.

1. Every member and the fixed model are run on every training frame and counted with the judge's own counting
   (``counting.classify_frame``). Done once for all frames and kept in ``table``.
2. On the training places together, a member is *allowed* when the standard pass rule (``judge.decide``, the stored
   margins) does not call it FAIL against the fixed model (no checks) on those places.
3. Among the allowed members the highest *gain* wins: (found, per placement) minus (boxes that are not on their
   barrel, per arrangement), each as the difference from the fixed model.
4. A tie goes to the member that comes first in the family. Families list the color step outer and the checks inner,
   each from the most cautious: so on a tie the more cautious color step, then the fewer / milder checks. No allowed
   member with a gain above zero: the fixed model.

Train frames only: the table is built with ``judge.load_frame``, which refuses anything else.
"""
from __future__ import annotations

import hashlib
import json
import pickle
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bg  # noqa: E402
from bg import cd, ru  # noqa: E402
import checks as ck  # noqa: E402
import stages as sg  # noqa: E402

from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402

CACHE = bg.OUT / "cache_geo"
FIXED = (ru.FIXED, ck.OFF)

B4 = cd.FAMILIES[bg.B4]                                               # 54 ramps, then each with delta 0.30 / 0.25 / 0.20 / 0.15
DELTAS = (0.30, 0.25, 0.20, 0.15)


def fam(colors, grid) -> list[tuple]:
    return [(c, k) for c in colors for k in grid]


FAMILIES: dict[str, list[tuple]] = {
    "G1_b4_checks": fam(B4, ck.GRID),
    "G1a_b4_k1_only": fam(B4, ck.GRID_K1),
    "G1b_b4_k2_only": fam(B4, ck.GRID_K2),
    "G2_fixed_checks": fam([ru.FIXED], ck.GRID),
}
for _d in DELTAS:
    FAMILIES[f"D{_d:.2f}_checks"] = fam([s for s in B4 if s.delta == _d], ck.GRID)
    FAMILIES[f"D{_d:.2f}_no_checks"] = fam([s for s in B4 if s.delta == _d], [ck.OFF])
TITLES = {
    "G1_b4_checks": "G1 B4's color step plus the geometry checks, both chosen in the fold (primary)",
    "G1a_b4_k1_only": "G1a B4 plus K1 (speckle) only",
    "G1b_b4_k2_only": "G1b B4 plus K2 (label, not a stripe) only",
    "G2_fixed_checks": "G2 the fixed colors plus the checks",
}
for _d in DELTAS:
    TITLES[f"D{_d:.2f}_checks"] = f"D bluer than the light by {_d:.2f} (ramp chosen in the fold) plus the checks"
    TITLES[f"D{_d:.2f}_no_checks"] = f"D bluer than the light by {_d:.2f} (ramp chosen in the fold), no checks"


def key(member: tuple) -> str:
    return member[0].key + "#" + member[1].key


def all_members() -> list[tuple]:
    return list(dict.fromkeys([FIXED] + [m for f in FAMILIES.values() for m in f]))


# ---------------------------------------------------------------- every member on every frame, once

def _frame(args) -> tuple[str, dict]:
    import cv2
    cv2.setNumThreads(1)
    stem, colors, grid = args
    p = CACHE / f"{stem}.pkl"
    have = pickle.loads(p.read_bytes()) if p.exists() else {}
    want = [(c, k) for c in colors for k in grid]
    todo_colors = list(dict.fromkeys(c for c, k in want if key((c, k)) not in have))
    if todo_colors:
        frame = jg.load_frame(stem)
        label = io.load_boxes(stem, check_image=False)
        gts = dtp.barrels_from_boxes(label)
        clean = bool(label.get("clean", True))
        per_mask: dict = {}
        per_kept: dict = {}
        for c in todo_colors:
            m = ru.segment(frame, c)
            h = hashlib.blake2b(m.tobytes(), digest_size=16).digest()
            if h not in per_mask:
                fs = sg.found(m)
                per_mask[h] = (fs, [sg.measure(f, m) for f in fs])
            fs, meas = per_mask[h]
            for k in grid:
                kp = ck.kept(meas, k)
                if (h, kp) not in per_kept:
                    per_kept[(h, kp)] = json.dumps(ct.classify_frame(stem, [fs[i].barrel for i in kp], gts, clean).to_dict())
                have[key((c, k))] = per_kept[(h, kp)]
        CACHE.mkdir(parents=True, exist_ok=True)
        p.write_bytes(pickle.dumps(have))
    return stem, {key(m): have[key(m)] for m in want}


def build_table(stems: list[str], members: list[tuple], jobs: int = 9, progress: bool = True) -> dict[str, dict]:
    """stem -> member key -> FrameCount (as its JSON text; ``fc`` turns it into one)."""
    jg.require_train(stems)
    colors = list(dict.fromkeys(c for c, _ in members))
    grid = list(dict.fromkeys(k for _, k in members))
    table: dict[str, dict] = {}
    with Pool(jobs) as pool:
        for i, (stem, out) in enumerate(pool.imap_unordered(_frame, [(s, colors, grid) for s in stems], chunksize=1)):
            table[stem] = out
            if progress and (i + 1) % 40 == 0:
                print(f"  table: {i + 1}/{len(stems)} frames x {len(colors)} color steps x {len(grid)} checks", flush=True)
    return table


_FC: dict = {}


def fc(code: str) -> ct.FrameCount:
    if code not in _FC:
        _FC[code] = ct.FrameCount.from_dict(json.loads(code))
    return _FC[code]


# ---------------------------------------------------------------- the rule that picks a member

def tallies(table: dict, k: str, stems: list[str], placements: ct.Placements):
    counts = {s: fc(table[s][k]) for s in stems}
    return ct.tally(counts, stems, placements), {p: ct.tally(counts, ss, placements) for p, ss in ct.group_stems(stems, "place").items()}


def choose(table: dict, family: list[tuple], stems: list[str], placements: ct.Placements, margins: jg.Margins, base_key: str | None = None):
    """The member of ``family`` picked on the frames ``stems`` by the written rule, and what it rests on. Members with
    the same counts on every one of ``stems`` are judged once (the first in the family order stands for them)."""
    base_key = base_key or key(FIXED)
    base, base_places = tallies(table, base_key, stems, placements)
    seen: dict = {}
    best, best_gain, allowed, gains = None, 0.0, 0, []
    for m in family:
        k = key(m)
        sig = tuple(table[s][k] for s in stems)
        if sig in seen:
            ok, gain = seen[sig]
        else:
            cand, cand_places = tallies(table, k, stems, placements)
            verdict = jg.decide(base, cand, {p: (base_places[p], cand_places[p]) for p in base_places}, margins)
            ok = verdict.result != jg.FAIL
            gain = (cand.found_w - base.found_w) - (cand.extra_w - base.extra_w)
            seen[sig] = (ok, gain)
        if not ok:
            continue
        allowed += 1
        gains.append(gain)
        if gain > best_gain + 1e-9:
            best, best_gain = m, gain
    cand, _ = tallies(table, base_key if best is None else key(best), stems, placements)
    return best, {"allowed": allowed, "of": len(family), "distinct": len(seen), "gain": round(best_gain, 3),
                  "found_w": round(cand.found_w - base.found_w, 3), "extra_w": round(cand.extra_w - base.extra_w, 3)}


def describe(m: tuple | None) -> str:
    if m is None:
        return "the fixed model, no checks (nothing allowed with a gain)"
    return f"{m[0].describe()}; checks: {m[1].describe()}"


def detector_of(m: tuple | None):
    c, k = m if m is not None else FIXED

    def detect_frame(stem: str, frame) -> list:
        mask = ru.segment(frame, c)
        return ck.apply(sg.found(mask), mask, k)
    detect_frame.describe = describe(m)
    return detect_frame


class Fitter:
    def __init__(self, table: dict, placements: ct.Placements, margins: jg.Margins | None = None):
        self.table, self.placements, self.margins = table, placements, margins or jg.load_margins()
        self.chosen: dict[str, dict] = {n: {} for n in FAMILIES}

    def fit(self, name: str):
        family = FAMILIES[name]

        def fit(train_stems: list[str], held_place: str):
            m, info = choose(self.table, family, [s for s in train_stems if s in self.table], self.placements, self.margins)
            self.chosen[name][held_place] = {"member": describe(m), "key": None if m is None else key(m), **info}
            return detector_of(m)
        fit.describe = f"{TITLES[name]}: the member picked on the other places"
        return fit


# ---------------------------------------------------------------- the best candidate, importable

_PRIMARY = None


def fit(train_stems: list[str], held_place: str):
    """The primary candidate (G1) as the judge's ``--cand-fit``:

        python barrels/tools/judge.py --cand-fit barrels/experiments/2026-11-27_bluer_geom/fitgeo.py:fit
    """
    global _PRIMARY
    if _PRIMARY is None:
        from barrels import conditions as cnd
        ordinary = jg.train_frames()[cnd.ORDINARY]
        table = build_table(ordinary, list(dict.fromkeys([FIXED] + FAMILIES["G1_b4_checks"])))
        _PRIMARY = Fitter(table, jg.load_truth(ordinary).placements).fit("G1_b4_checks")
    return _PRIMARY(train_stems, held_place)


fit.describe = TITLES["G1_b4_checks"] + ": the member picked on the other places"
