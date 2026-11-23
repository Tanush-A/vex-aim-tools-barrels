#!/usr/bin/env python3
"""Step 2 of the 2026-11-25 color work: sweep every threshold and gate on every slider-labelled train frame.

    python barrels/experiments/2026-11-25_color/sweep.py [--jobs 8] [--only <substring>]

Per frame (anchor = his slider label, gates at today's values):
- one at a time, over the whole reachable span: orange hue low -30..his high (step 1), orange hue high his low..90
  (step 1; the slider stops at 60), orange S floor 0..255 (step 3), blue hue low 0..his high and high his low..179
  (step 2; the slider stops at 60 and 150), blue S floor 0..255 (step 3), the brightness gate V 0..150 (step 5),
  the horizon row 0..150 (step 10); per value: his barrels found (v2), false boxes, boxes, the painted share of
  the cores of his boxes per color, paint outside his padded boxes, flood (painted outside more than
  max(30000 px, 4 x his) - not run through the detector);
- the non-monotone events: walking each threshold from strict to loose, a barrel found at one value and lost at the
  next (looser) value, with the detector's reason log at the looser value (``evalcore.why_lost``) and how much
  paint the step added on the barrel cores and outside;
- the joint check: 150 random settings inside the box of the one-at-a-time working ranges (working = every barrel
  found at his values still found, no more false boxes, outside paint at most max(150 px, 10 %) more; the
  2026-11-24 PREREG definition), all eight numbers moved at once.

Writes results/2026-11-25_color/sweep/<stem>.json. Train frames only (``common.load`` refuses any other).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402
import evalcore as ec  # noqa: E402

OUT = cm.RESULTS / "sweep"


def spans(a: dict) -> dict[str, list[int]]:
    """The values each parameter takes, in the order from STRICT to LOOSE (so a walk along it only adds paint); his own
    value is always one of them."""
    out = _spans(a)
    for p, vals in out.items():
        if a[p] not in vals:
            loose_down = vals[0] > vals[-1]
            vals = sorted(set(vals) | {a[p]}, reverse=loose_down)
            out[p] = vals
    return out


def _spans(a: dict) -> dict[str, list[int]]:
    return {
        "orange_h_lo": list(range(a["orange_h_hi"], -31, -1)),
        "orange_h_hi": list(range(a["orange_h_lo"], 91)),
        "orange_s_lo": list(range(255, -1, -3)) + ([0] if 255 % 3 else []),
        "blue_h_lo": list(range(a["blue_h_hi"], -1, -2)),
        "blue_h_hi": list(range(a["blue_h_lo"], 180, 2)),
        "blue_s_lo": list(range(255, -1, -3)) + ([0] if 255 % 3 else []),
        "v_min": list(range(150, -1, -5)),
        "horizon_row": list(range(150, -1, -10)),
    }


def rec(r: ec.Result) -> dict:
    return {"found": sorted(r.found), "false": r.n_false, "boxes": r.n_boxes, "core": r.core, "out": r.out,
            "flood": r.flood, "empty": r.empty, "best_iou": list(r.best_iou)}


def works(r: ec.Result, ref: ec.Result) -> bool:
    if r.flood or r.empty:
        return False
    return r.found >= ref.found and r.n_false <= ref.n_false and r.out <= ref.out + max(150, 0.1 * ref.out)


def one(stem: str) -> str:
    import cv2
    cv2.setNumThreads(1)
    from barrels import io
    t0 = time.time()
    bgr, lab = cm.load(stem)
    j = ec.Judge(stem, bgr, lab)
    a = ec.full({**{k: v for k, v in __import__("barrels.hsrange", fromlist=["flat"]).flat(io.load_hs(stem, check_image=False)).items()}})
    ref = j.set_reference(a)
    adopted = j.run(ec.full({"orange_h_lo": 3, "orange_h_hi": 13, "orange_s_lo": 140, "blue_h_lo": 103, "blue_h_hi": 119, "blue_s_lo": 113}))
    out = {"stem": stem, "condition": cm.condition_of(stem), "place": cm.place_of(cm.condition_of(stem)), "anchor": a,
           "n_boxes": len(j.boxes), "boxes": [{"color": b["color"], "bbox": b["bbox"], "flags": b.get("flags", [])} for b in j.boxes],
           "clean": j.clean, "ref": rec(ref), "adopted": rec(adopted), "flood_cap": j.flood_cap(), "sweeps": {}, "events": [], "ranges": {}}
    for p, values in spans(a).items():
        rows = []
        prev = None
        for v in values:
            s = {**a, p: v}
            r = j.run(s)
            rows.append([v, rec(r)])
            if prev is not None and not r.flood and not r.empty and not prev[1].flood:
                lost = sorted(prev[1].found - r.found)
                for g in lost:
                    w = ec.why_lost(j, s, g)
                    out["events"].append({"param": p, "from": prev[0], "to": v, "gt": g, "color": j.boxes[g]["color"],
                                          "flags": j.boxes[g].get("flags", []),
                                          "core_from": prev[1].core, "core_to": r.core, "out_from": prev[1].out, "out_to": r.out,
                                          "false_from": prev[1].n_false, "false_to": r.n_false, **w})
            prev = (v, r)
        out["sweeps"][p] = rows
        # the run of working values around the anchor (detector version, relative to his values)
        ok = {v: works(r_, ref) for v, r_ in ((row[0], j.run({**a, p: row[0]})) for row in rows)}
        av = a[p]
        lo = hi = av
        order = sorted(ok)
        idx = order.index(av) if av in ok else None
        if idx is not None:
            i = idx
            while i - 1 >= 0 and ok[order[i - 1]]:
                i -= 1
            k = idx
            while k + 1 < len(order) and ok[order[k + 1]]:
                k += 1
            lo, hi = order[i], order[k]
        out["ranges"][p] = [lo, hi]
    # the joint check: random points in the box of the ranges
    rng = np.random.default_rng(0)
    joint = []
    for _ in range(150):
        s = {p: int(rng.integers(lo, hi + 1)) for p, (lo, hi) in out["ranges"].items()}
        r = j.run(s)
        joint.append([ec.key(s), works(r, ref), rec(r)])
    out["joint"] = joint
    out["joint_share"] = float(np.mean([x[1] for x in joint]))
    out["seconds"] = round(time.time() - t0, 1)
    out["detector_calls"] = j.calls
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{stem}.json").write_text(json.dumps(out, default=float))
    return f"{stem}: {out['seconds']} s, {j.calls} detector calls, {len(out['events'])} events, joint {out['joint_share']:.2f}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    stems = [s for s in cm.slider_stems() if args.only in s]
    print(f"{len(stems)} slider-labelled train frames", flush=True)
    with Pool(args.jobs) as pool:
        for msg in pool.imap_unordered(one, stems):
            print(msg, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
