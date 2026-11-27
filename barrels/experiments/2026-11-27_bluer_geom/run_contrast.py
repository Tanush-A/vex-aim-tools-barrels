#!/usr/bin/env python3
"""G3: the checks on the contrast winner (C1 of `wip/exp-contrast`, brought in unchanged). Plan: PREREG.md.

    python barrels/experiments/2026-11-27_bluer_geom/run_contrast.py [--jobs 9]

C1 per held-out place is the setting its own fold picked (``results/2026-11-26_contrast/chosen.json``; picked on the
other places, so still leave one place out). Its boxes: today's boxes on the fixed mask, plus the boxes of the
contrast mask that are on none of them (``candidate.FrameWork.detect``, mode "add"), each box with what it was drawn
from (``stages.found`` on the mask it came from). The checks are then chosen inside each fold on the other places, by
the rule of ``fitgeo.choose``, among ``checks.GRID``, with that place's C1 setting fixed.

This script does not import the light experiment (its ``common`` module has the contrast experiment's name).
Writes results/2026-11-27_bluer_geom/: judge_C1_repro/, judge_G3_contrast_checks/, vs_own_G3_contrast_checks/,
chosen_contrast.json.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pickle
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
CONTRAST = BARRELS / "experiments" / "2026-11-26_contrast"
sys.path.insert(0, str(BARRELS / "src"))
sys.path.insert(0, str(CONTRAST))
sys.path.insert(0, str(HERE))
import candidate as cc  # noqa: E402  (the contrast experiment's)
import checks as ck  # noqa: E402
import stages as sg  # noqa: E402

import barrels  # noqa: E402
from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import cv as bcv  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402

assert str(Path(barrels.__file__).resolve()).startswith(str(BARRELS)), barrels.__file__
OUT = BARRELS / "results" / "2026-11-27_bluer_geom"
CACHE = OUT / "cache_contrast"
CHOSEN = json.loads((BARRELS / "results" / "2026-11-26_contrast" / "chosen.json").read_text())["folds"]["C1_add_guards"]
FIXED = "fixed"
WEAK = 2.0


def spec_of(place: str) -> str:
    return CHOSEN[place]["spec"]


SPECS = sorted(set(c["spec"] for c in CHOSEN.values()))


class GeoWork(cc.FrameWork):
    """``FrameWork`` with what each box was drawn from: (Found, the mask it came from)."""

    def __init__(self, frame):
        super().__init__(frame)
        self._found: dict = {}

    def _found_of(self, mask):
        h = hashlib.blake2b(mask.tobytes(), digest_size=16).digest()
        if h not in self._found:
            fs = sg.found(mask)
            self._found[h] = [(f, mask, sg.measure(f, mask)) for f in fs]
        return self._found[h]

    def found(self, st):
        base = self._found_of(self.base_mask)
        if st is None:
            return list(base)
        mask, cands = self.masks(st)
        if not any(c.info.get("painted") for c in cands):
            return list(base)
        new = self._found_of(mask)
        bb = [f.barrel for f, _, _ in base]
        out = list(base) + [x for x in new if not any(ct.is_on(x[0].barrel, o) for o in bb)]
        return sorted(out, key=lambda x: x[0].barrel.bbox[0])


def boxes(items, k: ck.Checks) -> list:
    return [f.barrel for f, _, m in items if not ck.removes(m, k)]


def _frame(stem: str):
    import cv2
    cv2.setNumThreads(1)
    p = CACHE / f"{stem}.pkl"
    if p.exists():
        return stem, pickle.loads(p.read_bytes())
    frame = jg.load_frame(stem)
    label = io.load_boxes(stem, check_image=False)
    gts = dtp.barrels_from_boxes(label)
    clean = bool(label.get("clean", True))
    gw = GeoWork(frame)
    have = {}
    for spec in [None] + SPECS:
        items = gw.found(None if spec is None else cc.setting_from(spec))
        for k in ck.GRID:
            have[(spec or FIXED) + "#" + k.key] = json.dumps(ct.classify_frame(stem, boxes(items, k), gts, clean).to_dict())
    CACHE.mkdir(parents=True, exist_ok=True)
    p.write_bytes(pickle.dumps(have))
    return stem, have


_FC: dict = {}


def fc(code):
    if code not in _FC:
        _FC[code] = ct.FrameCount.from_dict(json.loads(code))
    return _FC[code]


def tallies(table, k, stems, placements):
    counts = {s: fc(table[s][k]) for s in stems}
    return ct.tally(counts, stems, placements), {p: ct.tally(counts, ss, placements) for p, ss in ct.group_stems(stems, "place").items()}


def choose(table, spec, stems, placements, margins):
    base, base_places = tallies(table, FIXED + "#" + ck.OFF.key, stems, placements)
    best, best_gain, allowed = None, 0.0, 0
    for k in ck.GRID:
        cand, cand_places = tallies(table, spec + "#" + k.key, stems, placements)
        v = jg.decide(base, cand, {p: (base_places[p], cand_places[p]) for p in base_places}, margins)
        if v.result == jg.FAIL:
            continue
        allowed += 1
        gain = (cand.found_w - base.found_w) - (cand.extra_w - base.extra_w)
        if gain > best_gain + 1e-9:
            best, best_gain = k, gain
    return best, {"allowed": allowed, "of": len(ck.GRID), "gain": round(best_gain, 3)}


def detector(spec_for_place, checks_for_place, name):
    works: dict = {}

    def detect_frame(stem, frame):
        place = ct.place_of(stem)
        spec = spec_for_place(place)
        k = checks_for_place(place)
        return boxes(GeoWork(frame).found(None if spec is None else cc.setting_from(spec)), k)
    detect_frame.describe = name
    return detect_frame


def strength(j) -> str:
    if j.result != jg.PASS:
        return j.result
    return "PASS" if j.total[1].found_w - j.total[0].found_w >= j.margins.found_gain + WEAK - 1e-9 else "PASS (WEAK)"


def row(j) -> dict:
    b, c = j.total
    return {"verdict": strength(j), "found_w": [round(b.found_w, 2), round(c.found_w, 2)], "found": [b.found, c.found],
            "extra_w": [round(b.extra_w, 2), round(c.extra_w, 2)], "extra": [b.extra, c.extra],
            "clean_empty": [b.clean_empty, c.clean_empty], "cluttered_empty_w": [round(b.cluttered_empty_w, 2), round(c.cluttered_empty_w, 2)],
            "gained": sum(x.kind == "gained" for x in j.changes if x.judged), "lost": sum(x.kind == "lost" for x in j.changes if x.judged),
            "places": {p: [round(pb.found_w, 2), round(pc.found_w, 2)] for p, (pb, pc) in j.places.items() if abs(pc.found_w - pb.found_w) > 1e-9},
            "report_only": {c_: [cb.found, cc_.found, cb.barrels, cb.extra, cc_.extra] for c_, (cb, cc_) in j.report_only.items() if cb.found != cc_.found or cb.extra != cc_.extra}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=9)
    a = ap.parse_args()
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    stems = ordinary + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    truth = jg.load_truth(stems)
    margins = jg.load_margins()
    jg.require_train(ordinary)
    table = {}
    with Pool(a.jobs) as pool:
        for i, (s, have) in enumerate(pool.imap_unordered(_frame, ordinary, chunksize=1)):
            table[s] = have
            if (i + 1) % 40 == 0:
                print(f"  table {i + 1}/{len(ordinary)}", flush=True)
    chosen: dict = {}

    def checks_for(place):
        if place not in chosen:
            train = [s for s in ordinary if ct.place_of(s) != place]
            k, info = choose(table, spec_of(place), train, truth.placements, margins)
            chosen[place] = {"spec": spec_of(place), "checks": None if k is None else k.describe(), "key": None if k is None else k.key, **info}
        k = ck.Checks(*[None if v == "-" else float(v) for v in _parse(chosen[place]["key"])]) if chosen[place]["key"] else ck.OFF
        return k

    dets = {"today": jg.fixed_detector(),
            "C1_repro": detector(spec_of, lambda p: ck.OFF, "C1 of the contrast experiment, its folds' settings, reproduced"),
            "G3_contrast_checks": detector(spec_of, checks_for, "G3 C1 plus the checks chosen in the fold")}
    runs = jg.run_many(dets, stems, truth)
    out = {"made": dt.date.today().isoformat(), "git": bcv.git_hash(), "verdicts": {}, "folds": chosen}
    for n in ("C1_repro", "G3_contrast_checks"):
        j = jg.compare(runs["today"], runs[n], frames, truth, margins, lopo=True)
        jg.write(j, OUT / f"judge_{n}")
        out["verdicts"][n] = row(j)
        print(n, strength(j), j.total[0].found_w, "->", j.total[1].found_w, j.total[0].extra_w, "->", j.total[1].extra_w, flush=True)
    j = jg.compare(runs["C1_repro"], runs["G3_contrast_checks"], frames, truth, margins, lopo=True)
    jg.write(j, OUT / "vs_own_G3_contrast_checks")
    out["vs_own"] = {"G3_contrast_checks": {"against": "C1_repro", **row(j)}}
    (OUT / "chosen_contrast.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    return 0


def _parse(k: str):
    s, l = k.split("|")
    sh, bf = l[1:].split("/")
    return s[1:], sh, bf


if __name__ == "__main__":
    sys.exit(main())
