#!/usr/bin/env python3
"""The pre-registered test of the 2026-11-25 color candidates (``PREREG.md``): three families, the setting chosen
inside each leave-one-place-out fold by the written rule, scored on the held-out place; the acceptance clauses; the
final model of the chosen family. Train frames only.

    python barrels/experiments/2026-11-25_color/test.py [--jobs 8]

Every setting runs through ``pipeline.segment`` with a ``pipeline.Model`` built from the adopted model (six numbers
via ``hslabel.model_from_thresholds``; the light rule via ``Config.hs_light``), today's detector and the v2 rule.
Per-frame results are cached in results/2026-11-25_color/test_cache/ (ignored by git). Writes
results/2026-11-25_color/test/ and, for the chosen family, the model file (PREREG "Outputs").
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import datetime as dt
import itertools
import json
import math
import subprocess
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402

from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import eval_det as ed  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import hsrange as hx  # noqa: E402
from barrels import pipeline as pl  # noqa: E402

CAM = geo.AIM_4A8B6118_BOXFIT
OUT = cm.RESULTS / "test"
CACHE = cm.RESULTS / "test_cache"
ADOPTED = (3, 13, 140, 103, 119, 113)
SIXK = hx.THRESHOLDS


@dataclasses.dataclass(frozen=True)
class Setting:
    six: tuple = ADOPTED            # orange h_lo, h_hi, s_lo, blue h_lo, h_hi, s_lo
    light: tuple = ()               # (w0, w1, s_warm, h_warm) or ()

    @property
    def key(self) -> str:
        return "s" + ",".join(map(str, self.six)) + ("|L" + ",".join(f"{x:g}" for x in self.light) if self.light else "")

    def distance(self) -> float:
        d = sum(abs(a - b) * (0.1 if i in (2, 5) else 1.0) for i, (a, b) in enumerate(zip(self.six, ADOPTED)))
        return d + (1.0 if self.light else 0.0)

    def model(self, base: pl.Model) -> pl.Model:
        m = hl.model_from_thresholds(base, hx.nested(dict(zip(SIXK, self.six))))
        if self.light:
            m = dataclasses.replace(m, cfg=dataclasses.replace(m.cfg, hs_light=tuple(float(x) for x in self.light)))
        return m

    def describe(self) -> str:
        o, b = self.six[:3], self.six[3:]
        t = f"orange {o[0]}..{o[1]} S>={o[2]}, blue {b[0]}..{b[1]} S>={b[2]}"
        if self.light:
            w0, w1, s, h = self.light[:4]
            t += f"; light rule w0 {w0:g}, w1 {w1:g}, blue S -> {s:g}, hue low -> {h:g}"
            if len(self.light) > 4:
                t += f" (light read from rows < {self.light[4]:g}, brightest {self.light[5]:g} %)"
        return t


FIXED = Setting()
O_GRID = list(itertools.product((0, 1, 2, 3), (13, 14, 15, 16, 17), (140, 150, 160, 170)))


BAND = (50, 20)          # round 2 (PREREG addendum): the light read from rows 0-49, brightest 20 %


def families(round_: int = 1) -> dict[str, list[Setting]]:
    c1 = [Setting((ol, oh, os_, bl, 119, bs)) for (ol, oh, os_), bl, bs in itertools.product(O_GRID, (100, 103), (100, 113, 125))]
    c2 = [Setting(ADOPTED, (w0, w1, s, h)) for w0, w1, s, h in itertools.product((0.06, 0.08, 0.10, 0.12), (0.20, 0.25, 0.30), (30, 40, 50), (92, 98))]
    c3 = [Setting((ol, oh, os_, 103, 119, 113), (w0, w1, 40, 92)) for (ol, oh, os_), w0, w1 in itertools.product(O_GRID, (0.08, 0.10), (0.22, 0.25))]
    if round_ == 2:
        c2 = [Setting(s.six, s.light + BAND) for s in c2]
        c3 = [Setting(s.six, s.light + BAND) for s in c3]
    for fam in (c1, c2, c3):
        fam.sort(key=lambda s: s.distance())        # grid order = closest to the adopted values first (tie rule 3)
    return {"C1": c1, "C2": c2, "C3": c3} if round_ == 1 else {"C1": c1, "C2b": c2, "C3b": c3}


# ---------------------------------------------------------------- per-frame runs

def run_frame(args) -> tuple[str, dict]:
    import cv2
    cv2.setNumThreads(1)
    stem, settings = args
    p = CACHE / f"{stem}.json"
    have = json.loads(p.read_text()) if p.exists() else {}
    todo = [s for s in settings if s.key not in have]
    if todo:
        bgr, lab = cm.load(stem)
        frame = pl.Frame.from_image(bgr)
        base = hl.adopted_model()
        gts = [b.with_ground(CAM) for b in dtp.barrels_from_boxes({"barrels": lab.get("barrels", [])})]
        seen: dict = {}
        for s in todo:
            mask = pl.segment(frame, s.model(base))[0]
            h = mask.tobytes().__hash__()
            if h not in seen:
                preds = det.detect(mask, det.DetConfig(), CAM)
                r = ed.evaluate_frame(stem, preds, gts, CAM, rule="v2", clean=bool(lab.get("clean", True)))
                seen[h] = {"tp": [r.tp[1], r.tp[2]], "fp": [r.fp[1], r.fp[2]], "fn": [r.fn[1], r.fn[2]],
                           "found": sorted(m.gt_idx for m in r.matches), "neg": len(gts) == 0, "boxes": len(preds)}
            have[s.key] = seen[h]
        CACHE.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(have))
    return stem, {s.key: have[s.key] for s in settings}


def frames() -> dict[str, list[str]]:
    """class -> stems (ordinary and extreme; excluded left out)."""
    out = defaultdict(list)
    for s in cm.train_stems_with_boxes():
        k = cm.class_of(cm.condition_of(s))
        if k in ("ordinary", "extreme"):
            out[k].append(s)
    return out


# ---------------------------------------------------------------- scores

def _f1(tp, fp, fn) -> float:
    p = tp / (tp + fp) if tp + fp else math.nan
    r = tp / (tp + fn) if tp + fn else math.nan
    if not math.isnan(p) and not math.isnan(r) and p + r:
        return 2 * p * r / (p + r)
    return 0.0 if (tp + fp + fn) else math.nan


@dataclasses.dataclass
class Cell:
    found: int = 0
    barrels: int = 0
    false: int = 0
    empty: int = 0                   # boxes on empty frames
    tp: np.ndarray = dataclasses.field(default_factory=lambda: np.zeros(2))
    fp: np.ndarray = dataclasses.field(default_factory=lambda: np.zeros(2))
    fn: np.ndarray = dataclasses.field(default_factory=lambda: np.zeros(2))

    def add(self, r: dict) -> None:
        self.tp += r["tp"]; self.fp += r["fp"]; self.fn += r["fn"]
        self.found += sum(r["tp"]); self.false += sum(r["fp"]); self.barrels += sum(r["tp"]) + sum(r["fn"])
        if r["neg"]:
            self.empty += sum(r["fp"])

    @property
    def score(self) -> float:
        f = [_f1(*(x[i] for x in (self.tp, self.fp, self.fn))) for i in range(2)]
        f = [x for x in f if not math.isnan(x)]
        return float(np.mean(f)) if f else math.nan

    @property
    def net(self) -> float:
        return self.found - 2 * self.false


def cell(res: dict, stems, key: str) -> Cell:
    c = Cell()
    for s in stems:
        c.add(res[s][key])
    return c


def empty_frames_with_box(res: dict, stems, key: str) -> set:
    return {s for s in stems if res[s][key]["neg"] and sum(res[s][key]["fp"]) > 0}


# ---------------------------------------------------------------- the rule

def choose(res: dict, family: list[Setting], train_stems: list[str]) -> tuple[Setting, dict]:
    by_cond = defaultdict(list)
    for s in train_stems:
        by_cond[cm.condition_of(s)].append(s)
    by_place = defaultdict(list)
    for s in train_stems:
        by_place[cm.place_of(cm.condition_of(s))].append(s)
    base_cond = {c: cell(res, v, FIXED.key).score for c, v in by_cond.items()}
    base_empty = empty_frames_with_box(res, train_stems, FIXED.key)
    base_empty_n = sum(cell(res, v, FIXED.key).empty for v in by_place.values())
    best, best_j, n_ok = None, -math.inf, 0
    for st in family:
        k = st.key
        if any(cell(res, v, k).score < base_cond[c] - 0.02 for c, v in by_cond.items()):
            continue
        if not empty_frames_with_box(res, train_stems, k) <= base_empty:
            continue
        if sum(cell(res, v, k).empty for v in by_place.values()) > base_empty_n:
            continue
        n_ok += 1
        j = sum(cell(res, v, k).net / max(1, cell(res, v, k).barrels) for v in by_place.values())
        if j > best_j + 1e-9:
            best, best_j = st, j
    if best is None:
        return FIXED, {"eligible": 0, "J": None}
    return best, {"eligible": n_ok, "J": best_j}


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--round", type=int, default=2, choices=(1, 2), help="1 = the PREREG as first written; 2 = the addendum (default)")
    a = ap.parse_args()
    fams = families(a.round)
    out_dir = OUT if a.round == 2 else cm.RESULTS / "test_round1"
    settings = [FIXED] + [s for f in fams.values() for s in f]
    settings = list(dict.fromkeys(settings))
    fr = frames()
    res = {}
    with Pool(a.jobs) as pool:
        for i, (stem, out) in enumerate(pool.imap_unordered(run_frame, [(s, settings) for s in fr["ordinary"]], chunksize=1)):
            res[stem] = out
            if (i + 1) % 20 == 0:
                print(f"{i + 1}/{len(fr['ordinary'])} frames", flush=True)
    ordinary = fr["ordinary"]
    places = sorted({cm.place_of(cm.condition_of(s)) for s in ordinary})
    conds = sorted({cm.condition_of(s) for s in ordinary}, key=lambda c: (cm.place_of(c), c))
    st_of = lambda pl_: [s for s in ordinary if cm.place_of(cm.condition_of(s)) == pl_]  # noqa: E731
    OUT.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, fam in fams.items():
        chosen, held = {}, {}
        for p in places:
            train = [s for s in ordinary if cm.place_of(cm.condition_of(s)) != p]
            st, info = choose(res, fam, train)
            chosen[p] = (st, info)
            for s in st_of(p):
                held[s] = res[s][st.key]
        final, finfo = choose(res, fam, ordinary)
        results[name] = {"chosen": chosen, "held": held, "final": final, "final_info": finfo}
    # the extreme sets: only the fixed model and each family's final setting (report only)
    finals = [FIXED] + list(dict.fromkeys(results[n]["final"] for n in fams))
    with Pool(a.jobs) as pool:
        for stem, out in pool.imap_unordered(run_frame, [(s, finals) for s in fr["extreme"]], chunksize=1):
            res[stem] = out
    # tables
    fixed_held = {s: res[s][FIXED.key] for s in ordinary}

    def cell_of(held, stems):
        c = Cell()
        for s in stems:
            c.add(held[s])
        return c

    L = [f"# The color candidates, leave one place out ({dt.date.today().isoformat()}, git {git()})", "",
         "`python barrels/experiments/2026-11-25_color/test.py` (plan: `../../experiments/2026-11-25_color/PREREG.md`). "
         f"Ordinary train frames: {len(ordinary)} at {len(places)} places; test frames never opened. Each cell: found / "
         "barrels, false boxes (boxes on empty frames), score. Each family's setting is chosen on the other 7 places by "
         "the written rule and scored on the held-out place.", "",
         f"Round {a.round} ({'the PREREG addendum: the light read above the horizon gate' if a.round == 2 else 'the PREREG as first written'}).", "",
         "## Per condition", "", "| condition | place | fixed | " + " | ".join(fams) + " |", "|---|---|---|" + "---|" * len(fams)]
    verdict = {}
    for c in conds:
        stems_c = [s for s in ordinary if cm.condition_of(s) == c]
        f = cell_of(fixed_held, stems_c)
        cells = [cell_of(results[n]["held"], stems_c) for n in fams]
        L.append(f"| {c} | {cm.place_of(c)} | {fmt(f)} | " + " | ".join(fmt(x, f) for x in cells) + " |")
    tot_f = cell_of(fixed_held, ordinary)
    L.append("| **all ordinary** | | " + fmt(tot_f) + " | " + " | ".join(fmt(cell_of(results[n]["held"], ordinary), tot_f) for n in fams) + " |")
    L += ["", "## Per place (found - 2 x false; held out)", "", "| place | fixed | " + " | ".join(fams) + " |", "|---|---:|" + "---:|" * len(fams)]
    for p in places:
        f = cell_of(fixed_held, st_of(p))
        L.append(f"| {p} | {f.net:.0f} | " + " | ".join(f"{cell_of(results[n]['held'], st_of(p)).net:.0f}" for n in fams) + " |")
    # acceptance
    L += ["", "## Acceptance (PREREG A1-A3 on the held-out numbers)", ""]
    for n in fams:
        held = results[n]["held"]
        tot = cell_of(held, ordinary)
        gain = tot.net - tot_f.net
        better = sum(cell_of(held, st_of(p)).net > cell_of(fixed_held, st_of(p)).net for p in places)
        worse = [p for p in places if cell_of(held, st_of(p)).net < cell_of(fixed_held, st_of(p)).net]
        new_empty = sorted({s for s in ordinary if held[s]["neg"] and sum(held[s]["fp"]) > 0}
                           - {s for s in ordinary if fixed_held[s]["neg"] and sum(fixed_held[s]["fp"]) > 0})
        drops = [(c, cell_of(held, [s for s in ordinary if cm.condition_of(s) == c]).score - cell_of(fixed_held, [s for s in ordinary if cm.condition_of(s) == c]).score) for c in conds]
        drops = [(c, d) for c, d in drops if d < -0.02]
        a1 = gain >= 20 and better >= 4 and not worse
        a2 = not new_empty and tot.empty <= tot_f.empty
        a3 = not drops
        verdict[n] = {"A1": a1, "A2": a2, "A3": a3, "J": sum(cell_of(held, st_of(p)).net / max(1, cell_of(held, st_of(p)).barrels) for p in places),
                      "gain": gain}
        L += [f"**{n}**: A1 {'pass' if a1 else 'FAIL'} (net {tot_f.net:.0f} -> {tot.net:.0f}, {gain:+.0f}; better in {better} of {len(places)} "
              f"places{', worse in ' + ', '.join(worse) if worse else ''}); A2 {'pass' if a2 else 'FAIL'} (boxes on empty frames {tot_f.empty} -> "
              f"{tot.empty}{', new on ' + ', '.join(new_empty) if new_empty else ''}); A3 {'pass' if a3 else 'FAIL'}"
              f"{' (' + ', '.join(f'{c} {d:+.3f}' for c, d in drops) + ')' if drops else ''}.", ""]
    passing = [n for n in fams if all(verdict[n][k] for k in ("A1", "A2", "A3"))]
    pick = max(passing, key=lambda n: (verdict[n]["J"], -list(fams).index(n))) if passing else max(fams, key=lambda n: verdict[n]["J"])
    L += [f"**Chosen family: {pick}** ({'passes A1-A3' if passing else 'best, NOT passing A1-A3'}; held-out J: "
          + ", ".join(f"{n} {verdict[n]['J']:.2f}" for n in fams) + ").", ""]
    L += ["## The setting chosen in each fold", "", "| held-out place | " + " | ".join(fams) + " |", "|---|" + "---|" * len(fams)]
    for p in places:
        L.append(f"| {p} | " + " | ".join(f"{results[n]['chosen'][p][0].describe()} ({results[n]['chosen'][p][1]['eligible']} eligible)" for n in fams) + " |")
    L.append("| **all 8 (final)** | " + " | ".join(results[n]["final"].describe() for n in fams) + " |")
    # extreme, report only (the final setting of each family)
    L += ["", "## Extreme sets (report only; each family's final setting)", "", "| condition | fixed | " + " | ".join(fams) + " |", "|---|---|" + "---|" * len(fams)]
    for c in sorted({cm.condition_of(s) for s in fr["extreme"]}):
        sc = [s for s in fr["extreme"] if cm.condition_of(s) == c]
        f = cell(res, sc, FIXED.key)
        L.append(f"| {c} | {fmt(f)} | " + " | ".join(fmt(cell(res, sc, results[n]['final'].key), f) for n in fams) + " |")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.md").write_text("\n".join(L) + "\n")
    with open(out_dir / "per_frame.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["stem", "condition", "place", "arm", "found", "false", "barrels", "found_ids"])
        for s in ordinary:
            for arm, r in [("fixed", fixed_held[s])] + [(n, results[n]["held"][s]) for n in fams]:
                w.writerow([s, cm.condition_of(s), cm.place_of(cm.condition_of(s)), arm, sum(r["tp"]), sum(r["fp"]), sum(r["tp"]) + sum(r["fn"]), " ".join(map(str, r["found"]))])
    chosen = {n: {"folds": {p: {"setting": dataclasses.asdict(results[n]["chosen"][p][0]), **results[n]["chosen"][p][1]} for p in places},
                  "final": dataclasses.asdict(results[n]["final"]), "final_info": results[n]["final_info"], "verdict": verdict[n]} for n in fams}
    chosen["pick"] = pick
    chosen["passing"] = passing
    chosen["round"] = a.round
    (out_dir / "chosen.json").write_text(json.dumps(chosen, indent=1, default=float) + "\n")
    if a.round == 2:
        write_model(results[pick]["final"], passing=bool(passing), family=pick)
    print("\n".join(L))
    return 0 if passing else 1


def fmt(c: Cell, ref: Cell | None = None) -> str:
    s = f"{c.found}/{c.barrels}, {c.false} ({c.empty}), {c.score:.2f}"
    if ref is not None and c.score < ref.score - 0.02:
        s = "**" + s + "**"
    return s


def git() -> str:
    try:
        return subprocess.run(["git", "-C", str(cm.BARRELS), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def write_model(st: Setting, passing: bool, family: str) -> Path:
    """The model file of the chosen family's final setting, in the format ``BarrelDetectorHook.load`` reads."""
    m = st.model(hl.adopted_model())
    d = {"name": f"2026-11-25 color, family {family}: {st.describe()}", "config": m.cfg.to_dict(), "config_hash": m.cfg.short_hash(),
         "git": git(), "fit_frames": "chosen by the PREREG rule on the ordinary train frames of 8 places (experiments/2026-11-25_color)",
         "passed_prereg": passing, "base_model": "eb863d84", "setting": dataclasses.asdict(st),
         "model": m.to_dict()}
    p = cm.RESULTS / ("config.json" if passing else "config_best_not_passing.json")
    p.write_text(json.dumps(d, indent=1, default=float) + "\n")
    return p


if __name__ == "__main__":
    sys.exit(main())
