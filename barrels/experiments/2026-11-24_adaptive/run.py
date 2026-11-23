#!/usr/bin/env python3
"""TODO F, updated, and the adaptive rule's test: one command, re-run on whatever conditions exist.

    python barrels/experiments/2026-11-24_adaptive/run.py            # exit 0 = the rule passes its PREREG acceptance, 1 = it does not

Stage 1 (stage 2 is added after the PREREG is committed).
"""
from __future__ import annotations

import argparse
import importlib.util
import math
import sys
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import conditions as cd, hsrel as hr, pipeline as pl, worldmap_bridge as wb  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

_spec = importlib.util.spec_from_file_location("frel", HERE.parent / "2026-11-18_hs_relation" / "run.py")
frel = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(frel)

OUT = PKG_ROOT / "results" / "2026-11-24_adaptive"
NAN = float("nan")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    base = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=frel.CAM).model
    fixed = hr.thresholds_of(base)
    data = frel.load(base)
    cond = frel.per_condition(data)
    for k, c in cond.items():
        i = cd.info(k)
        c["place"], c["light"], c["guessed"] = i.place, i.light, i.guessed
    res, kept = frel.detect(data, cond, base, {})
    for k, c in cond.items():
        st = data["conds"][k]["stems"]
        print(k, c["class"], c["place"], c["light"], {a: frel.cell_text(frel.cell(res, a, st)) for a in ("fixed", "box per frame", "hand median")})
    keys = [k for k, c in cond.items() if c["class"] == hr.ORDINARY]
    from barrels import detector as det, report as rp
    dcfg = det.DetConfig()
    for k in keys:
        if not cond[k]["hand_frames"]:
            continue
        row = []
        for t in hr.THRESHOLDS + ("orange", "blue"):
            th = dict(fixed)
            for tt in hr.THRESHOLDS:
                if tt == t or tt.startswith(t + "_"):
                    th[tt] = cond[k]["hand"][tt]
            m, _ = hr.model_from_thresholds(base, th)
            got = [rp.score_frame(s, pl.segment(data["frames"][s]["frame"], m)[0], dcfg, frel.CAM) for s in data["conds"][k]["stems"]]
            c = rp.summarize(got)
            row.append(f"{t} {c.found}({c.false})")
        print("ABL", k, " | ".join(row))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        for target in ("hand", "box"):
            ks = [k for k in keys if any(np.isfinite(cond[k][target][t]) for t in hr.THRESHOLDS)]
            x = np.array([[cond[k]["feat"][f] for f in hr.FEATURES] for k in ks], float)
            g = [cond[k]["place"] for k in ks]
            print(f"\n== target {target}: {len(ks)} conditions, {len(set(g))} places")
            for t in hr.THRESHOLDS:
                y = np.array([cond[k][target][t] for k in ks], float)
                ok = np.isfinite(y)
                xx, yy, gg = x[ok], y[ok], [p for p, o in zip(g, ok) if o]
                lo = hr.loco(xx, yy, 1, groups=gg)
                lc = hr.loco(xx, yy, 1)
                e = lambda P: np.mean(np.abs(np.array(P) - yy))
                mo = []
                for i, p in enumerate(gg):
                    m = [yy[j] for j in range(len(yy)) if gg[j] != p]
                    mo.append(np.mean(m) if m else NAN)
                print(f"{t:12s} fixed {e([fixed[t]]*len(yy)):5.1f} meanothers(LOPO) {e(mo):5.1f} LOPO1 {e([r['pred'] for r in lo]):5.1f} "
                      f"({','.join(sorted({'+'.join(hr.FEATURES[j] for j in r['feats']) or 'fb' for r in lo}))}) LOCO1 {e([r['pred'] for r in lc]):5.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
