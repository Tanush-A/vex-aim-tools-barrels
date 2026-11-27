#!/usr/bin/env python3
"""Part B: every box B4 draws on the ordinary train frames (each place under the setting its own fold picked,
``results/2026-11-27_bluer_geom/repro.json``), with its state under the judge's counting and the measurements of
``stages.measure``. Also the boxes of the fixed colors, for comparison. Writes:

- ``results/2026-11-27_bluer_geom/boxes.csv``: one line per box (arm b4 / fixed).
- ``results/2026-11-27_bluer_geom/masks/<stem>.npz`` (not committed): the B4 and fixed masks, for the sheets.

Train frames only (``judge.load_frame``).
"""
from __future__ import annotations

import csv
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bg  # noqa: E402
from bg import ru  # noqa: E402
import stages as sg  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402

MASKS = bg.OUT / "masks"


def setting_of(key: str) -> ru.Setting:
    r, w0, w1, s, h, d, o, x0, x1, hi, g = key.split("|")
    return ru.Setting(r, float(w0), float(w1), float(s), float(h), float(d), o, float(x0), float(x1), float(hi), float(g))


def folds() -> dict[str, ru.Setting]:
    j = json.loads((bg.OUT / "repro.json").read_text())
    return {p: setting_of(c["key"]) for p, c in j["folds"].items()}


def one(args):
    import cv2
    cv2.setNumThreads(1)
    stem, key = args
    st = setting_of(key)
    frame = jg.load_frame(stem)
    label = io.load_boxes(stem, check_image=False)
    gts = dtp.barrels_from_boxes(label)
    clean = bool(label.get("clean", True))
    info: dict = {}
    m_b4 = ru.segment(frame, st, info)
    m_fx = ru.segment(frame, ru.FIXED)
    MASKS.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(MASKS / f"{stem}.npz", b4=m_b4, fixed=m_fx)
    rows = []
    fixed_boxes = None
    for arm, m in (("fixed", m_fx), ("b4", m_b4)):
        fs = sg.found(m)
        preds = [f.barrel for f in fs]
        if arm == "fixed":
            fixed_boxes = {(p.color, p.bbox) for p in preds}
        fc = ct.classify_frame(stem, preds, gts, clean)
        for i, (f, state) in enumerate(zip(fs, fc.boxes)):
            r = {"arm": arm, "stem": stem, "place": ct.place_of(stem), "condition": ct.condition_of(stem), "empty": not gts, "clean": clean,
                 "i": i, "state": state, "in_fixed": (f.barrel.color, f.barrel.bbox) in fixed_boxes,
                 "warmth": round(info.get("warmth", float("nan")), 4), "rel_px": info.get("rel_px", 0)}
            r.update(sg.measure(f, m))
            rows.append(r)
    return rows


def main() -> int:
    ordinary = jg.train_frames()[cnd.ORDINARY]
    fo = folds()
    jobs = [(s, fo[ct.place_of(s)].key) for s in ordinary]
    out = []
    with Pool(9) as pool:
        for rows in pool.imap_unordered(one, jobs, chunksize=2):
            out += rows
    keys = list(dict.fromkeys(k for r in out for k in r))
    out.sort(key=lambda r: (r["arm"], r["stem"], r["i"]))
    with open(bg.OUT / "boxes.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, keys)
        w.writeheader()
        w.writerows(out)
    print(len(out), "boxes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
