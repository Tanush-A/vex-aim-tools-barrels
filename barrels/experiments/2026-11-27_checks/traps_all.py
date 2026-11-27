#!/usr/bin/env python3
"""Addendum 3 (plan: PREREG.md): the stage-11 variants of ``variants.py`` on everything.

    env PYTHONPATH=<export>/src python traps_all.py <export> <inputs.pkl> <before.json> <scene_truth.json> [--jobs 8]

``<export>`` as for ``b4_traps.py``. The boxes are the ten stages (bluer_geom's ``stages.found``, the detector before
stage 11) then the variant as a post-filter.

1. The proof harness: 5435 masks; "none" must reproduce ``before.json``. Real barrels lost against "none" (found or
   box off → missed, and found → box off), per group; boxes not on a barrel removed.
2. The train frames (ordinary judged, extreme report only), four color steps, each judged against itself without a
   variant: the fixed colors; the contrast winner C1 as judged (each place under the setting its own fold picked,
   ``results/2026-11-26_contrast/chosen.json``), with the variant inside every ``detect`` call of the contrast path;
   B4 and delta 0.20 under the folds' picks of ``b4/picks.json`` (B4_i_off, D0.20_i_off).
3. Every box not on its barrel that "none" draws on the ordinary frames, per color step, and which variants remove it.

Outputs: results/2026-11-27_checks/variants/ (summary.md, harness.json, false_boxes.csv, judge_*/)."""
from __future__ import annotations

import csv
import json
import multiprocessing as mp
import pickle
import sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
EXPORT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(EXPORT / "src"))
sys.path.insert(0, str(EXPORT / "experiments" / "2026-11-27_bluer_geom"))
import bg  # noqa: E402,F401
import fitgeo as fg  # noqa: E402
import stages as sg  # noqa: E402
from bg import ru  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402

sys.path.insert(0, str(HERE))
import variants as vr  # noqa: E402

OUT = BARRELS / "results" / "2026-11-27_checks" / "variants"
CAM = sg.CAM
V = list(vr.VARIANTS)
SOURCES = ("fixed", "contrast", "B4", "D0.20")
_S: dict = {}


def boxes_of(found, mask, spec):
    return sorted([f.barrel for f in vr.apply(found, mask, CAM, spec)], key=lambda b: b.bbox[0])


def enc(bs):
    return [[int(b.color), [int(v) for v in b.bbox]] for b in bs]


# ---------------------------------------------------------------- 1. harness

def h_init(path):
    cv2.setNumThreads(1)
    _S["enc"] = pickle.load(open(path, "rb"))


def h_work(key):
    m = cv2.imdecode(np.frombuffer(_S["enc"][key], np.uint8), cv2.IMREAD_UNCHANGED)
    fs = sg.found(m)
    return key, {v: enc(boxes_of(fs, m, vr.VARIANTS[v])) for v in V}


# ---------------------------------------------------------------- 2. frames

def f_init(cspecs, picks):
    cv2.setNumThreads(1)
    _S["model"] = hl.adopted_model()
    sys.path.insert(0, str(EXPORT / "experiments" / "2026-11-26_contrast"))
    light_common = sys.modules.pop("common", None)          # the light experiment's common.py; the contrast one has the same name
    import candidate as cand
    if light_common is not None:
        sys.modules["common"] = light_common
    _S["cand"] = cand
    _S["cspecs"] = {p: cand.setting_from(s) for p, s in cspecs.items()}
    members = {fg.key(m): m for m in fg.fam(fg.B4, [fg.ck.OFF])}
    _S["picks"] = {f: {p: (members[k][0] if k else fg.FIXED[0]) for p, k in d.items()} for f, d in picks.items()}


def f_work(stem):
    frame = jg.load_frame(stem)
    place = ct.place_of(stem)
    out = {}
    m = pl.segment(frame, _S["model"])[0]
    fs = sg.found(m)
    out["fixed"] = {v: enc(boxes_of(fs, m, vr.VARIANTS[v])) for v in V}
    for f in ("B4", "D0.20"):
        c = _S["picks"][f].get(place)
        if c is None:
            continue
        mm = ru.segment(frame, c)
        ff = sg.found(mm)
        out[f] = {v: enc(boxes_of(ff, mm, vr.VARIANTS[v])) for v in V}
    st = _S["cspecs"].get(place, _S["cspecs"].get("__all__"))
    cand = _S["cand"]
    cache: dict = {}

    class FW(cand.FrameWork):
        spec: dict = {}

        def _detect(self, mask):
            k = mask.tobytes()
            if k not in cache:
                cache[k] = sg.found(mask)
            return boxes_of(cache[k], mask, self.spec)
    fw = FW(frame)
    out["contrast"] = {}
    for v in V:
        fw.spec = vr.VARIANTS[v]
        fw._base_boxes = None
        out["contrast"][v] = enc(fw.detect(st))
    return stem, out


def to_barrels(rows):
    return [dtp.Barrel(color=c, bbox=tuple(b), source="x") for c, b in rows]


def main() -> int:
    mp.set_start_method("fork", force=True)
    inputs, before_p, truth_p = sys.argv[2], sys.argv[3], sys.argv[4]
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 8
    OUT.mkdir(parents=True, exist_ok=True)

    # 1. harness
    before = {k: [[b[0], b[1]] for b in v["boxes"]] for k, v in json.load(open(before_p)).items()}
    scene_truth = json.load(open(truth_p))
    keys = sorted(before)
    stems_h = sorted({k.rsplit("/", 1)[1] for k in keys if not k.startswith("scene/")})
    jg.require_train(stems_h)
    gts, clean = ct.load_gts([s for s in stems_h if io.boxes_path(s).exists()])
    hres = {}
    with mp.Pool(jobs, initializer=h_init, initargs=(inputs,)) as pool:
        for k, r in pool.imap_unordered(h_work, keys, chunksize=20):
            hres[k] = r
    bad = [k for k in keys if hres[k]["none"] != before[k]]
    H = {v: defaultdict(lambda: defaultdict(int)) for v in V}
    lost_list = defaultdict(list)
    for k in keys:
        g = k.split("/")[0]
        if k.startswith("scene/"):
            t = scene_truth.get(k)
            t = None if t is None else ([dtp.Barrel(color=int(c), bbox=tuple(b), source="gt") for c, b in t["truths"]], True)
        else:
            s = k.rsplit("/", 1)[1]
            t = (gts[s], clean[s]) if s in gts else None
        if t is None:
            continue
        c0 = ct.classify_frame(k, to_barrels(hres[k]["none"]), t[0], t[1])
        for v in V:
            c1 = ct.classify_frame(k, to_barrels(hres[k][v]), t[0], t[1])
            r = H[v][g]
            r["removed"] += len(hres[k]["none"]) - len(hres[k][v])
            lost = [i for i, (x, y) in enumerate(zip(c0.gt, c1.gt)) if (x != ct.MISSED and y == ct.MISSED) or (x == ct.FOUND and y == ct.OFF)]
            r["lost"] += len(lost)
            r["extra_removed"] += c0.extra - c1.extra
            for i in lost:
                lost_list[v].append(f"{k} #{i + 1}")
    (OUT / "harness.json").write_text(json.dumps({"none_equals_before": not bad, "bad": bad[:20],
                                                   "groups": {v: {g: dict(r) for g, r in H[v].items()} for v in V}, "lost": lost_list}, indent=1) + "\n")
    print("harness: none == before.json:", not bad, flush=True)

    # 2. frames
    frames = jg.train_frames()
    stems = frames[cnd.ORDINARY] + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    truth = jg.load_truth(stems)
    cj = json.loads((EXPORT / "results" / "2026-11-26_contrast" / "chosen.json").read_text())
    cspecs = {p: d["spec"] for p, d in cj["folds"]["C1_add_guards"].items()}
    ins = cj.get("in_sample_all_places", {}).get("C1_add_guards", {})
    cspecs["__all__"] = ins.get("spec", next(iter(cspecs.values())))
    picks = json.loads((BARRELS / "results" / "2026-11-27_checks" / "b4" / "picks.json").read_text())
    picks = {"B4": picks["B4_i_off"], "D0.20": picks["D0.20_i_off"]}
    fres = {}
    with mp.Pool(jobs, initializer=f_init, initargs=(cspecs, picks)) as pool:
        for s, r in pool.imap_unordered(f_work, stems, chunksize=1):
            fres[s] = r
    (OUT / "boxes.json").write_text(json.dumps(fres) + "\n")
    margins = jg.load_margins()
    L = ["# Addendum 3: the stage-11 variants on everything", "",
         f"Harness: 'none' reproduces before.json on every input: {not bad}.", "",
         "## The proof harness (5435 masks): real barrels lost / boxes not on a barrel removed, against no stage 11", "",
         "| variant | " + " | ".join(sorted({g for v in V for g in H[v]})) + " | all |", "|---|" + "---|" * (len({g for v in V for g in H[v]}) + 1)]
    groups = sorted({g for v in V for g in H[v]})
    for v in V:
        tot = [sum(H[v][g]["lost"] for g in groups), sum(H[v][g]["extra_removed"] for g in groups)]
        L.append(f"| {v} | " + " | ".join(f"{H[v][g]['lost']} / {H[v][g]['extra_removed']}" for g in groups) + f" | **{tot[0]}** / {tot[1]} |")
    L += ["", "## The train frames: each color step with the variant against itself without (ordinary judged; extreme report only)", "",
          "| color step | variant | verdict | found, placements | gained / lost (ordinary) | boxes not on their barrel (per frame) | extreme: lost | cluttered empty |",
          "|---|---|---|---|---|---|---|---|"]
    rows = []
    for src in SOURCES:
        have = [s for s in stems if src in fres[s]]
        sub = {k: [s for s in v if s in have] for k, v in frames.items()}
        runs = {}
        for v in V:
            r = jg.Run(f"{src}_{v}", f"{src}, stage-11 variant {v}")
            for s in have:
                r.boxes[s] = to_barrels(fres[s][src][v])
                r.counts[s] = ct.classify_frame(s, r.boxes[s], truth.gts[s], truth.clean[s])
            runs[v] = r
        for v in V[1:]:
            j = jg.compare(runs["none"], runs[v], sub, truth, margins)
            jg.write(j, OUT / f"judge_{src}_{v}")
            b, c = j.total
            g_ = sum(1 for x in j.changes if x.judged and x.kind == "gained")
            lo = sum(1 for x in j.changes if x.judged and x.kind == "lost")
            elo = sum(1 for x in j.changes if not x.judged and x.kind == "lost")
            L.append(f"| {src} | {v} | {j.verdict.result} | {b.found_w:.2f} → {c.found_w:.2f} | {g_} / {lo} | {b.extra_w:.2f} → {c.extra_w:.2f} ({b.extra} → {c.extra}) | {elo} | {b.cluttered_empty_w:.2f} → {c.cluttered_empty_w:.2f} |")
            print(L[-1], flush=True)
        for s in [x for x in frames[cnd.ORDINARY] if x in have]:
            c0 = runs["none"].counts[s]
            for i, st in enumerate(c0.boxes):
                if st not in ct.EXTRA_STATES:
                    continue
                b = runs["none"].boxes[s][i]
                gone = {v: [int(b.color), list(b.bbox)] not in fres[s][src][v] for v in V[1:]}
                rows.append({"source": src, "stem": s, "state": st, "color": "orange" if b.color == 1 else "blue", "bbox": " ".join(map(str, b.bbox)), **gone})
    with open(OUT / "false_boxes.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    L += ["", "## Every box not on its barrel drawn with no stage 11 (ordinary frames): which variants remove it", "",
          "| color step | frame | state | color | box | " + " | ".join(V[1:]) + " |", "|---|---|---|---|---|" + "---|" * (len(V) - 1)]
    for r in rows:
        L.append(f"| {r['source']} | {r['stem'].replace('4A8B_', '')} | {r['state']} | {r['color']} | {r['bbox']} | " + " | ".join("**yes**" if r[v] else "no" for v in V[1:]) + " |")
    L += ["", "Harness losses, by variant (first 30):", ""]
    for v in V[1:]:
        L.append(f"- {v}: {len(lost_list[v])}: " + "; ".join(lost_list[v][:30]))
    (OUT / "summary.md").write_text("\n".join(L) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
