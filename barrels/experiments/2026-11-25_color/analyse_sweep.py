#!/usr/bin/env python3
"""Step 2 of the 2026-11-25 color work, the reading of the sweep (run ``sweep.py`` first).

    python barrels/experiments/2026-11-25_color/analyse_sweep.py

Writes results/2026-11-25_color/sweep.md (+ ranges.csv, events.csv):

1. The working range of each threshold and gate per frame (around his slider values, one at a time; working = every
   barrel found at his values still found, no more false boxes, outside paint at most max(150 px, 10 %) more), per
   place: the intersection over the place's frames, the median width, why the ends stopped, and on how many frames
   today's fixed value lies inside.
2. Do the ranges hold jointly (150 random settings inside the box of the one-at-a-time ranges)?
3. The non-monotone cases: a barrel found at one value and lost one step looser (more paint). Each is re-run with
   the detector's reason log at both values and classified:
   - "box moved": a box of the barrel's color still overlaps it (IoU >= 0.3) but fails the v2 rule; the edge that
     moved and by how much, and the detector part that made the box (from the log's "kept" entry);
   - "box gone": no such box; the part that made the box at the stricter value ("kept") and the test that drops the
     same candidate at the looser value (the first dropped entry of that stage overlapping the barrel).
   Plus how much paint the step added on the barrel cores and outside. Only events from settings that do not flood.
"""
from __future__ import annotations

import csv
import glob
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402
import evalcore as ec  # noqa: E402

from barrels import eval_det as ed  # noqa: E402

SWEEP = cm.RESULTS / "sweep"
PARAMS = ("orange_h_lo", "orange_h_hi", "orange_s_lo", "blue_h_lo", "blue_h_hi", "blue_s_lo", "v_min", "horizon_row")
FIXED = {"orange_h_lo": 3, "orange_h_hi": 13, "orange_s_lo": 140, "blue_h_lo": 103, "blue_h_hi": 119, "blue_s_lo": 113,
         "v_min": 40, "horizon_row": 50}
SLIDER = {"orange_h_lo": (-30, 60), "orange_h_hi": (-30, 60), "orange_s_lo": (0, 255), "blue_h_lo": (60, 150),
          "blue_h_hi": (60, 150), "blue_s_lo": (0, 255), "v_min": (40, 40), "horizon_row": (50, 50)}


def load_all() -> list[dict]:
    out = []
    for p in sorted(glob.glob(str(SWEEP / "*.json"))):
        d = json.loads(Path(p).read_text())
        cm.require_train(d["stem"])
        out.append(d)
    return out


def end_reason(d: dict, p: str, side: str) -> str:
    """Why the working run stopped on one side: the first value beyond the range, judged against his values."""
    lo, hi = d["ranges"][p]
    rows = {v: r for v, r in d["sweeps"][p]}
    vals = sorted(rows)
    beyond = [v for v in vals if (v < lo if side == "lo" else v > hi)]
    if not beyond:
        return "open"
    v = max(beyond) if side == "lo" else min(beyond)
    r, ref = rows[v], d["ref"]
    if r["flood"]:
        return "flood"
    if not set(r["found"]) >= set(ref["found"]):
        return "barrel lost"
    if r["false"] > ref["false"]:
        return "false box"
    return "outside paint"


def classify_event(d: dict, e: dict, judges: dict) -> dict:
    stem = d["stem"]
    if stem not in judges:
        bgr, lab = cm.load(stem)
        judges[stem] = ec.Judge(stem, bgr, lab)
    j = judges[stem]
    a = d["anchor"]
    s_from, s_to = {**a, e["param"]: e["from"]}, {**a, e["param"]: e["to"]}
    g = j.gts[e["gt"]]
    gb = tuple(j.boxes[e["gt"]]["bbox"])
    p_from, log_from = j.log(s_from)
    p_to, log_to = j.log(s_to)

    def best(preds):
        cand = [(ed.box_iou(p.bbox, gb), p) for p in preds if p.color == g.color]
        return max(cand, key=lambda t: t[0]) if cand else (0.0, None)

    iou_f, bf = best(p_from)
    iou_t, bt = best(p_to)
    kept_from = [x for x in log_from if x.get("why") == "kept" and "box" in x and ed.box_iou(tuple(x["box"]), tuple(bf.bbox)) > 0.9] if bf else []
    maker = kept_from[0]["stage"] if kept_from else "step-1 piece (no stripe)"
    out = {"stem": stem, "place": d["place"], "condition": d["condition"], "param": e["param"], "from": e["from"], "to": e["to"],
           "gt": e["gt"], "color": e["color"], "flags": ",".join(e["flags"]), "maker": maker,
           "core_gain": round(np.nansum([e["core_to"][c] - e["core_from"][c] for c in ("orange", "blue")]), 3),
           "out_gain": e["out_to"] - e["out_from"], "false_from": e["false_from"], "false_to": e["false_to"]}
    if bt is not None and iou_t >= 0.3:
        tol = ed.bottom_tol_px(g)
        moved = {k: int(bt.bbox[i] - bf.bbox[i]) for i, k in enumerate(("left", "top", "right", "bottom"))} if bf else {}
        big = max(moved, key=lambda k: abs(moved[k])) if moved else ""
        kept_to = [x for x in log_to if x.get("why") == "kept" and "box" in x and ed.box_iou(tuple(x["box"]), tuple(bt.bbox)) > 0.9]
        out.update(kind="box moved", iou=round(iou_t, 2), bottom_err=int(bt.bbox[3] - gb[3]), tol=round(tol, 1),
                   edge=f"{big} {moved.get(big, 0):+d} px" if big else "", maker_to=kept_to[0]["stage"] if kept_to else "step-1 piece",
                   check=("bottom edge" if abs(bt.bbox[3] - gb[3]) > tol else "") + (" IoU" if iou_t < 0.5 else ""))
    else:
        stage = kept_from[0]["stage"] if kept_from else "piece"
        drops = [x for x in log_to if x.get("why") != "kept" and x["stage"] == stage
                 and (ec.overlap(x["bbox"], gb) > 0.3 or ec.overlap(gb, x["bbox"]) > 0.3)]
        if not drops:      # the stripe itself may be gone: look one stage up
            drops = [x for x in log_to if x.get("why") != "kept" and x["stage"] == "stripe"
                     and (ec.overlap(x["bbox"], gb) > 0.3 or ec.overlap(gb, x["bbox"]) > 0.3)]
        other = [p for p in p_to if p.color != g.color and ed.box_iou(p.bbox, gb) > 0.3]
        out.update(kind="box gone" if not other else "color flip", iou=round(iou_t, 2), bottom_err="", tol="", edge="", maker_to="",
                   check=(f"{drops[0]['stage']}:{drops[0]['why']}" if drops else "no candidate logged"))
    return out


def main() -> int:
    data = load_all()
    if not data:
        print("no sweep records: run sweep.py first")
        return 1
    out = cm.RESULTS
    # 1. ranges
    rows = []
    for d in data:
        for p in PARAMS:
            lo, hi = d["ranges"][p]
            rows.append({"stem": d["stem"], "place": d["place"], "condition": d["condition"], "class": cm.class_of(d["condition"]),
                         "scene": d["stem"].split("_")[3], "param": p, "his": d["anchor"][p], "lo": lo, "hi": hi,
                         "lo_why": end_reason(d, p, "lo"), "hi_why": end_reason(d, p, "hi"),
                         "fixed_inside": lo <= FIXED[p] <= hi, "found_his": len(d["ref"]["found"]), "n_boxes": d["n_boxes"],
                         "found_adopted": len(d["adopted"]["found"])})
    with open(out / "ranges.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    L = ["# The sweep: how wide the working ranges are, where they sit, and the non-monotone cases (2026-11-25, step 2)", "",
         "`python barrels/experiments/2026-11-25_color/sweep.py` then `analyse_sweep.py`. The 45 slider-labelled train frames "
         "(15 conditions, 5 places with slider labels). Working = every barrel found at his values still found, no more false "
         "boxes, outside paint at most max(150 px, 10 %) more (the 2026-11-24 PREREG definition); one threshold at a time, the "
         "others at his values; blue hue now swept over 0-179, orange high up to 90, the V gate 0-150, the horizon row 0-150.", ""]
    ordinary = [d for d in data if cm.class_of(d["condition"]) == "ordinary"]
    places = sorted({d["place"] for d in ordinary})
    L += ["## 1. Ranges per place (ordinary conditions; intersection over the place's labelled frames)", "",
          "| threshold | fixed | " + " | ".join(places) + " | fixed inside (frames) |", "|---|---:|" + "---|" * len(places) + "---:|"]
    for p in PARAMS:
        cells = []
        for pl_ in places:
            rs = [r for r in rows if r["place"] == pl_ and r["param"] == p and r["class"] == "ordinary"]
            lo, hi = max(r["lo"] for r in rs), min(r["hi"] for r in rs)
            med_w = np.median([r["hi"] - r["lo"] for r in rs])
            cells.append((f"{lo}..{hi}" if lo <= hi else f"**empty** ({lo}>{hi})") + f" (w {med_w:.0f})")
        inside = [r["fixed_inside"] for r in rows if r["param"] == p and r["class"] == "ordinary"]
        L.append(f"| {p} | {FIXED[p]} | " + " | ".join(cells) + f" | {sum(inside)} of {len(inside)} |")
    L += ["", "Cell = the values that work on every labelled frame of the place (intersection), and the median width of the "
          "frames' own ranges. An empty intersection = the place's frames want different values for this threshold "
          "(usually clutter against no clutter).", ""]
    # why the ends stopped
    why = defaultdict(Counter)
    for r in rows:
        if r["class"] != "ordinary":
            continue
        why[(r["param"], "low")][r["lo_why"]] += 1
        why[(r["param"], "high")][r["hi_why"]] += 1
    L += ["**Why each end stopped** (ordinary frames):", "", "| threshold | low end | high end |", "|---|---|---|"]
    for p in PARAMS:
        f = lambda c: ", ".join(f"{k} {v}" for k, v in c.most_common())  # noqa: E731
        L.append(f"| {p} | {f(why[(p, 'low')])} | {f(why[(p, 'high')])} |")
    # a constant inside every place's intersection?
    L += ["", "**One value for all places?** Per threshold, the values inside the intersection of EVERY ordinary place "
          "(empty = no constant fits every place's labelled frames one at a time):", ""]
    for p in PARAMS:
        rs = [r for r in rows if r["param"] == p and r["class"] == "ordinary"]
        lo, hi = max(r["lo"] for r in rs), min(r["hi"] for r in rs)
        # the value inside the most frames' ranges
        span = range(min(r["lo"] for r in rs), max(r["hi"] for r in rs) + 1)
        cnt = {v: sum(r["lo"] <= v <= r["hi"] for r in rs) for v in span}
        bestv = max(cnt.values())
        best = [v for v, c in cnt.items() if c == bestv]
        L.append(f"- {p}: all frames {lo}..{hi}" + (" (empty)" if lo > hi else "") +
                 f"; inside the most frames' ranges: {best[0]}..{best[-1]} ({bestv} of {len(rs)} frames); fixed {FIXED[p]} inside {cnt.get(FIXED[p], 0)}.")
    # 2. joint
    js = [d["joint_share"] for d in ordinary]
    L += ["", "## 2. Do the ranges hold together?", "",
          f"150 random settings inside each frame's box of one-at-a-time ranges, all eight numbers moved at once: median share "
          f"working {np.median(js):.2f} (min {min(js):.2f}, max {max(js):.2f}) over {len(js)} ordinary frames; at least 0.9 on "
          f"{sum(x >= 0.9 for x in js)}, under 0.7 on {sum(x < 0.7 for x in js)} ({', '.join(d['stem'][5:] for d in ordinary if d['joint_share'] < 0.7)}).", ""]
    # 3. events
    judges: dict = {}
    ev = []
    for d in data:
        for e in d["events"]:
            ev.append(classify_event(d, e, judges))
    with open(out / "events.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ev[0]) if ev else ["stem"]); w.writeheader(); w.writerows(ev)
    near = [x for x in ev if x["out_gain"] <= 150]
    L += ["## 3. Non-monotone cases: more paint, a barrel lost", "",
          f"{len(ev)} events on {len({x['stem'] for x in ev})} frames (a barrel found at one value and lost one step looser; "
          f"each value of each threshold and gate, from strict to loose). {len(near)} of them added at most 150 px of paint "
          "outside the boxes: the barrel was lost from its OWN extra paint, not from the table gluing on.", "",
          "**By kind and the detector check behind it:**", "", "| kind | check | events | of which outside paint <= 150 px | params |", "|---|---|---:|---:|---|"]
    grp = defaultdict(list)
    for x in ev:
        grp[(x["kind"], x["check"] if x["kind"] != "box moved" else f"{x['check'].strip() or '?'} ({x['edge'].split()[0] if x['edge'] else '?'} edge)")].append(x)
    for (kind, check), xs in sorted(grp.items(), key=lambda t: -len(t[1])):
        L.append(f"| {kind} | {check} | {len(xs)} | {sum(x['out_gain'] <= 150 for x in xs)} | "
                 f"{', '.join(f'{k} {v}' for k, v in Counter(x['param'] for x in xs).most_common(4))} |")
    makers = Counter(x["maker"] for x in ev)
    L += ["", "The part of the detector that made the box at the stricter value: " + ", ".join(f"{k} {v}" for k, v in makers.most_common()) + ".", "",
          "**The list for the detector work** (events with at most 150 px more outside paint, i.e. the barrel's own extra paint "
          "lost it; all in `events.csv`):", "",
          "| frame | barrel | param from -> to | kind | check | box change | IoU / bottom err (tol) | core gain |", "|---|---|---|---|---|---|---|---:|"]
    for x in sorted(near, key=lambda x: (x["kind"], x["check"], x["stem"])):
        L.append(f"| {x['stem'][5:]} | #{x['gt'] + 1} {x['color']}{' (' + x['flags'] + ')' if x['flags'] else ''} | {x['param']} {x['from']} -> {x['to']} | "
                 f"{x['kind']} | {x['check']} | {x['edge']} | {x['iou']} / {x['bottom_err']} ({x['tol']}) | {x['core_gain']:+.3f} |")
    (out / "sweep.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
