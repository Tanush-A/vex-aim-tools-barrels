#!/usr/bin/env python3
"""A census before the fix (no acceptance number comes from here): if thin stripe pieces were let in, where would
the new boxes be?

A barrel three quarters hidden shows a piece of stripe about as wide as a stripe is tall. The finder refuses such a
piece today (narrower than one stripe height, or taller than wide). The 2026-11-19 round let them in (``slice_box``)
and got false boxes. This census counts, on real frames, the thin pieces that the lower floor lets in, and how many
of them would pass each requirement in turn:

  full slice     the body above and below the piece ends where the piece's row predicts the barrel's top AND bottom
                 (the usual tolerance: 15 % of the height, at least 4 px);
  outline knows  the predicted outline slid over the seen part fits at positions that span no more than 0.15 W, and
                 fits well (``shape_census.py`` part C, the limits taken there).

Each piece is then one of: inside a box the detector already draws for that color (a second piece of that barrel's
stripe: no new box), on a labeled barrel that has no box today (a barrel gained), or on nothing labeled (a false box).
The recordings have no labels: there a piece outside every drawn box is only counted and listed, to be looked at.

Train frames only; a test frame is never opened (asserted in the loaded script).

    python barrels/experiments/2026-11-20_occl_pin/thin_census.py --rec <path to data/recordings>
Output: results/2026-11-20_occl_pin/thin_census.md, thin_census.csv.
"""
from __future__ import annotations

import argparse
import collections
import csv
import importlib.util
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
spec = importlib.util.spec_from_file_location("shape_census", HERE / "shape_census.py")
C = importlib.util.module_from_spec(spec); sys.modules["shape_census"] = C; spec.loader.exec_module(C)
from barrels import detect_types as dtp, detector as det, io, pipeline as pl, splits, worldmap_bridge as wb  # noqa: E402

R, CAM, OUT = C.R, C.CAM, C.OUT
BASE = R.occl_arms.ARMS["edge+cap"]                       # the defaults of wip/detector-occl, spelled out
NEAR, SPAN, GOOD = C.CHOSEN


def pieces(mask: np.ndarray):
    """Every thin stripe piece of the mask (one the lower floor lets in and today's floor refuses), with what the
    census asks of it."""
    found = det.detect(mask, BASE, CAM)
    out = []
    for s in det.find_stripes(mask, CAM, C.FIND):
        if not s.small:
            continue
        m = C.measure_stripe(mask, s)
        if m is None:
            continue
        x0, y0, x1, y1 = s.bbox
        rows, W, H = m["rows"], m["W"], m["H"]
        tol = max(4, 0.15 * H)
        top_seen, bottom_seen = det._body_extent(mask, s.body, x0, x1, y0, y1)
        full = abs(top_seen - rows.top) <= tol and abs(bottom_seen - rows.bottom) <= tol
        e = C.estimates(m, mask, s.body)
        cands, cost = e["curve"]
        lo, hi = C.fitting(cands, cost, NEAR * H)
        knows = (hi - lo) <= SPAN * W and float(np.nanmin(cost)) <= GOOD * H
        cx = (lo + hi) / 2
        box = (int(round(cx - W / 2)), int(round(rows.top)), int(round(cx + W / 2)), int(round(rows.bottom)))
        mid = (x0 + x1) / 2
        in_found = any(b.color == s.body and b.bbox[0] <= mid < b.bbox[2] and b.bbox[1] <= s.center_row < b.bbox[3] for b in found)
        out.append({"s": s, "full": full, "knows": knows, "in_found": in_found, "box": box, "mid": mid, "found": found,
                    "seen": round((m["sx1"] - m["sx0"]) / W, 2), "cost_H": round(float(np.nanmin(cost)) / H, 3), "span": round((hi - lo) / W, 2)})
    return out


def main(argv=None) -> int:
    global NEAR, SPAN, GOOD
    ap = argparse.ArgumentParser()
    ap.add_argument("--rec", default=str(io.PKG_ROOT / "data" / "recordings"))
    ap.add_argument("--limits", default="", help="near,span,good to try instead of the limits taken, e.g. 0.01,0.3,0.05")
    ap.add_argument("--name", default="thin_census", help="the output files' name")
    args = ap.parse_args(argv)
    if args.limits:
        NEAR, SPAN, GOOD = (float(v) for v in args.limits.split(","))
    stems = R.train_stems()
    segs = R.segmentations(stems, with_extreme=True)
    test = set(splits.load_splits()["test"])
    rows = []
    sets = [("HOME (as in the eval table)", "HOME color model"), ("CAMPUS", "CAMPUS color model"), ("BLACK (extreme)", "BLACK"), ("WOOD (extreme)", "WOOD")]
    for set_name, pool in sets:
        for stem, mask in sorted(segs[pool].items()):
            assert stem not in test
            gts = dtp.barrels_from_boxes(io.load_boxes(stem))
            for p in pieces(mask):
                s = p["s"]
                on = [g for g in gts if g.color == s.body and g.bbox[0] <= p["mid"] < g.bbox[2] and g.bbox[1] <= s.center_row < g.bbox[3]]
                if p["in_found"]:
                    what = "inside a drawn box"
                elif on:
                    what = "on a labeled barrel with no box" + (f" ({'+'.join(sorted(on[0].flags))})" if on[0].flags else "")
                else:
                    what = "on nothing labeled"
                iou = max((det.box_iou(p["box"], g.bbox) for g in on), default=0.0)
                rows.append({"set": set_name, "frame": stem.replace("4A8B_", ""), "color": dtp.COLOR_NAMES[s.body], "piece": list(s.bbox), "full": int(p["full"]),
                             "knows": int(p["knows"]), "what": what, "seen": p["seen"], "cost_H": p["cost_H"], "span": p["span"], "box": list(p["box"]),
                             "overlap_with_label": round(iou, 2)})
    rec = Path(args.rec)
    frames = sorted(rec.rglob("*.png"))
    assert not any(f.stem in test for f in frames), "a test frame among the recordings"
    model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    n_rec = collections.Counter()
    for f in frames:
        img = cv2.imread(str(f))
        if img is None:
            continue
        clip = f.parent.name
        set_name = "recordings: campus clips" if "campus" in str(f.parent) else ("recordings: black clip" if "black" in str(f.parent) else "recordings: wood clip")
        n_rec[set_name] += 1
        mask = pl.segment(pl.Frame.from_image(img), model)[0]
        for p in pieces(mask):
            s = p["s"]
            rows.append({"set": set_name, "frame": f"{clip}/{f.stem}", "color": dtp.COLOR_NAMES[s.body], "piece": list(s.bbox), "full": int(p["full"]),
                         "knows": int(p["knows"]), "what": "inside a drawn box" if p["in_found"] else "outside every drawn box", "seen": p["seen"],
                         "cost_H": p["cost_H"], "span": p["span"], "box": list(p["box"]), "overlap_with_label": ""})
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / f"{args.name}.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    L = ["# If thin stripe pieces were let in, where would the new boxes be? (a census; no acceptance number)", "",
         "A thin piece = a stripe piece the lower floor lets in (0.45 of a stripe height wide) and today's floor refuses (narrower than a stripe is tall, "
         "or taller than wide). `full slice` = the body above and below it ends where its row predicts the top and the bottom. `outline knows` = the "
         f"predicted outline fits the seen part at positions spanning no more than {SPAN} W, with a cost of no more than {GOOD} H (positions within "
         f"{NEAR} H of the best count as fitting). Train frames ({', '.join(f'{k} {len(v)}' for k, v in stems.items())}) and the "
         f"{sum(n_rec.values())} frames of the recordings.", "",
         "| frames | thin pieces | full slice | full slice and outline knows | of those: inside a drawn box | on a labeled barrel with no box | on nothing labeled / outside every drawn box |",
         "|---|---|---|---|---|---|---|"]
    for set_name in [s for s, _ in sets] + sorted(n_rec):
        rs = [r for r in rows if r["set"] == set_name]
        fk = [r for r in rs if r["full"] and r["knows"]]
        L.append(f"| {set_name} | {len(rs)} | {sum(r['full'] for r in rs)} | {len(fk)} | {sum(r['what'] == 'inside a drawn box' for r in fk)} | "
                 f"{sum(r['what'].startswith('on a labeled barrel') for r in fk)} | {sum(r['what'] in ('on nothing labeled', 'outside every drawn box') for r in fk)} |")
    L += ["", "The same with the full slice alone (what the 2026-11-19 round asked for), for comparison:", "",
          "| frames | full slice | of those: inside a drawn box | on a labeled barrel with no box | on nothing labeled / outside every drawn box |", "|---|---|---|---|---|"]
    for set_name in [s for s, _ in sets] + sorted(n_rec):
        fk = [r for r in rows if r["set"] == set_name and r["full"]]
        L.append(f"| {set_name} | {len(fk)} | {sum(r['what'] == 'inside a drawn box' for r in fk)} | "
                 f"{sum(r['what'].startswith('on a labeled barrel') for r in fk)} | {sum(r['what'] in ('on nothing labeled', 'outside every drawn box') for r in fk)} |")
    L += ["", "Every thin piece that is a full slice, where the outline knows, and that is not inside a drawn box:", "",
          "| frames | frame | color | the piece | seen / W | the box the outline gives | overlap with the label | |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["full"] and r["knows"] and r["what"] != "inside a drawn box":
            L.append(f"| {r['set']} | {r['frame']} | {r['color']} | {r['piece']} | {r['seen']} | {r['box']} | {r['overlap_with_label']} | {r['what']} |")
    (OUT / f"{args.name}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
