#!/usr/bin/env python3
"""Part A, step 1: every reading on every train frame, next to what the labelled paint really is there.

    python barrels/experiments/2026-11-26_light/measure.py [--jobs 8]

Per frame (ordinary and extreme train conditions; ``judge.load_frame`` refuses anything else):
- each reading of ``common.READINGS``: warmth, log R/G, log B/G, pixels read;
- the TRUTH from the hand boxes (never an input of any rule): for the blue paint and the orange paint, body and
  stripe bands of free-standing upright barrels: pixels, median hue, hue percentiles 2 and 98, median S, S
  percentile 10, median brightness, the share darker than the brightness gate, median warmth of the paint itself;
- a few scene numbers for part C: the median brightness below the gate, the share of the gated pixels in the band the
  ottoman's orange needs (hue 14..23 with S >= 150), the share of the gated pixels the fixed model paints.

Writes results/2026-11-26_light/per_frame.csv. ``table.py`` makes the tables from it.
"""
from __future__ import annotations

import argparse
import csv
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import lightread as lr  # noqa: E402


def paint_stats(frame, mask: np.ndarray, color: str) -> dict:
    n = int(mask.sum())
    keys = ("n", "h_med", "h_p02", "h_p98", "s_med", "s_p10", "v_med", "dark", "warmth")
    if n < 30:
        return dict(zip(keys, [n] + [float("nan")] * (len(keys) - 1)))
    h = (cm.hue_orange(frame) if color == "orange" else cm.hue_blue(frame))[mask]
    s = cm.sat(frame)[mask]
    v = frame.val[mask]
    w = lr.pixel_warmth(frame.rgb)[mask]
    lit = v >= 40
    hh, ss = (h[lit], s[lit]) if lit.sum() >= 30 else (h, s)
    return {"n": n, "h_med": float(np.median(hh)), "h_p02": float(np.percentile(hh, 2)), "h_p98": float(np.percentile(hh, 98)),
            "s_med": float(np.median(ss)), "s_p10": float(np.percentile(ss, 10)), "v_med": float(np.median(v)),
            "dark": float((~lit).mean()), "warmth": float(np.median(w))}


def one(stem: str) -> dict:
    import cv2
    cv2.setNumThreads(1)
    frame = jg.load_frame(stem)
    cond = ct.condition_of(stem)
    row = {"stem": stem, "condition": cond, "place": ct.place_of(stem), "class": cnd.info(cond).klass, "scene": cm.scene_of(stem)}
    for name, r in cm.all_readings(frame).items():
        row.update({f"{name}.w": r.warmth, f"{name}.rg": r.log_rg, f"{name}.bg": r.log_bg, f"{name}.n": r.n})
    pm = cm.paint_masks(stem, frame.shape)
    for color in ("blue", "orange"):
        for part, m in (("all", pm[f"{color}_body"] | pm[f"{color}_stripe"]), ("body", pm[f"{color}_body"]), ("stripe", pm[f"{color}_stripe"])):
            row.update({f"{color}_{part}.{k}": v for k, v in paint_stats(frame, m, color).items()})
    g = cm.gate(frame)
    ho, s = cm.hue_orange(frame), cm.sat(frame)
    bg = g & ~pm["boxes"]
    row["v_med_below"] = float(np.median(frame.val[lr.GATE_ROW:]))
    row["v_mean"] = float(frame.val.mean())
    row["ext_share"] = float(((ho >= 14) & (ho <= 23) & (s >= 150))[g].mean()) if g.any() else 0.0
    row["ext_share_bg"] = float(((ho >= 14) & (ho <= 23) & (s >= 150))[bg].mean()) if bg.any() else 0.0
    row["fixed_share"] = float(cm.fixed_mask(frame)[g].mean()) if g.any() else 0.0
    row["boxes_share"] = float(pm["boxes"][lr.GATE_ROW:].mean())
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    fr = cm.frames()
    stems = fr[cnd.ORDINARY] + fr[cnd.EXTREME]
    jg.require_train(stems)
    with Pool(a.jobs) as pool:
        rows = pool.map(one, stems, chunksize=4)
    cm.OUT.mkdir(parents=True, exist_ok=True)
    out = cm.OUT / "per_frame.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in r.items()})
    print(f"{len(rows)} frames ({len(fr[cnd.ORDINARY])} ordinary, {len(fr[cnd.EXTREME])} extreme) -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
