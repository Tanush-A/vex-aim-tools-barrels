#!/usr/bin/env python3
"""Exploration harness of the 2026-11-25 color work (BEFORE the pre-registration): run named candidate rules on every
boxed train frame and print found / false per condition. Not a claim: the pre-registered test is ``test.py``.

    python barrels/experiments/2026-11-25_color/explore.py RULE [RULE ...] [--jobs 8] [--extreme]

A RULE is a name in ``registry()`` below, or a spec: const:oL,oH,oS,bL,bH,bS | hyst:oL,oH,oS,bL,bH,bS:radius
| peak. Results cached per (frame, rule) in results/2026-11-25_color/explore_cache/ (ignored by git).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402
import rules as rl  # noqa: E402

from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import eval_det as ed  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import pipeline as pl  # noqa: E402

CAM = geo.AIM_4A8B6118_BOXFIT
CACHE = cm.RESULTS / "explore_cache"
SIXK = ("orange_h_lo", "orange_h_hi", "orange_s_lo", "blue_h_lo", "blue_h_hi", "blue_s_lo")


def six_of(text: str) -> dict:
    v = [int(x) for x in text.split(",")]
    return dict(zip(SIXK, v))


def make_rule(spec: str):
    if spec == "fixed":
        return rl.fixed
    kind, _, rest = spec.partition(":")
    if kind == "const":
        six = six_of(rest)
        return lambda f: rl.const(f, six)
    if kind == "hyst":
        parts = rest.split(":")
        six = six_of(parts[0]); radius = int(parts[1])
        vmin = int(parts[2]) if len(parts) > 2 else None
        return lambda f: rl.hyst(f, six, radius, loose_v_min=vmin)
    if kind == "peak":
        return rl.peak
    if kind == "combo":       # combo:orange=hyst,blue=warm,w0=0.08,... (keyword=value pairs; tuples with /)
        kw = {}
        for part in rest.split(","):
            k, _, v = part.partition("=")
            if k in ("o_loose", "o_const"):
                kw[k] = tuple(int(x) for x in v.split("/"))
            elif k in ("radius", "s_warm", "h_warm", "erode"):
                kw[k] = int(v)
            elif k in ("w0", "w1", "k_top"):
                kw[k] = float(v)
            else:
                kw[k] = v
        return lambda f: rl.combo(f, **kw)
    raise ValueError(spec)


def score(stem: str, mask: np.ndarray, lab: dict) -> dict:
    gts = [b.with_ground(CAM) for b in dtp.barrels_from_boxes({"barrels": lab.get("barrels", [])})]
    preds = det.detect(mask, det.DetConfig(), CAM)
    r = ed.evaluate_frame(stem, preds, gts, CAM, rule="v2", clean=bool(lab.get("clean", True)))
    return {"tp": {str(k): v for k, v in r.tp.items()}, "fp": {str(k): v for k, v in r.fp.items()},
            "n_gt": {str(k): v for k, v in r.n_gt.items()}, "found": sorted(m.gt_idx for m in r.matches),
            "neg": len(gts) == 0, "clean": bool(lab.get("clean", True)), "n_pred": len(preds)}


def work(args) -> tuple[str, dict]:
    import cv2
    cv2.setNumThreads(1)
    stem, specs = args
    out = {}
    todo = []
    for spec in specs:
        p = CACHE / f"{stem}__{hashlib.sha1(spec.encode()).hexdigest()[:12]}.json"
        if p.exists():
            out[spec] = json.loads(p.read_text())
        else:
            todo.append((spec, p))
    if todo:
        bgr, lab = cm.load(stem)
        fr = pl.Frame.from_image(bgr)
        for spec, p in todo:
            m = make_rule(spec)(fr)
            out[spec] = score(stem, m, lab)
            CACHE.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(out[spec]))
    return stem, out


def frames(extreme: bool) -> list[str]:
    out = []
    for s in cm.train_stems_with_boxes():
        k = cm.class_of(cm.condition_of(s))
        if k == "ordinary" or (extreme and k == "extreme"):
            out.append(s)
    return out


def run(specs: list[str], jobs: int = 8, extreme: bool = False) -> dict:
    stems = frames(extreme)
    res = {}
    with Pool(jobs) as pool:
        for stem, out in pool.imap_unordered(work, [(s, specs) for s in stems], chunksize=1):
            res[stem] = out
    return res


def table(res: dict, specs: list[str]) -> str:
    agg = defaultdict(lambda: defaultdict(lambda: np.zeros(4, int)))   # cond -> spec -> found, barrels, false, empty-frame false
    for stem, out in res.items():
        c = cm.condition_of(stem)
        for spec in specs:
            r = out[spec]
            a = agg[c][spec]
            a += [sum(r["tp"].values()), sum(r["n_gt"].values()), sum(r["fp"].values()), sum(r["fp"].values()) if r["neg"] else 0]
    lines = ["condition".ljust(24) + "".join(f"{s[:22]:>24s}" for s in specs)]
    tot = defaultdict(lambda: np.zeros(4, int))
    for c in sorted(agg, key=lambda c: (cm.class_of(c), cm.place_of(c), c)):
        lines.append(f"{c[:23]:24s}" + "".join(f"{f'{a[0]}/{a[1]} f{a[2]} e{a[3]}':>24s}" for a in (agg[c][s] for s in specs)))
        if cm.class_of(c) == "ordinary":
            for s in specs:
                tot[s] += agg[c][s]
    lines.append(f"{'ORDINARY':24s}" + "".join(f"{f'{a[0]}/{a[1]} f{a[2]} e{a[3]}':>24s}" for a in (tot[s] for s in specs)))
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("specs", nargs="+")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--extreme", action="store_true")
    a = ap.parse_args()
    res = run(a.specs, a.jobs, a.extreme)
    print(table(res, a.specs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
