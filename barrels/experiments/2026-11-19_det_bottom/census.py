#!/usr/bin/env python3
"""Where does each box's bottom edge come from, and how far is it from the hand-drawn one? (PREREG part (d), and
the baseline's "does it matter" count.) HOME (leave-one-scene-out, as in the eval table) and CAMPUS, train frames
only, adopted color model. For every box an arm draws: the part of the detector that made it, where its bottom
came from, and its bottom row minus the bottom row of the hand-drawn box it sits on (same color, IoU >= 0.5; the
v2 bottom rule is not asked here, so a box that fails only on its bottom is still listed).

Also, on the same boxes, what other ways of working out the bottom would have given (report only, no box changes):
``from the top row`` (predicted_bottom of the box's top), ``from the stripe row``, ``top + the height of a barrel
as wide as the box``.

    python barrels/experiments/2026-11-19_det_bottom/census.py --arms base [--out step1_baseline]
Outputs: results/2026-11-19_det_bottom/[<out>/] bottom_edges.csv, bottom_edges.md.
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))
import bottom_arms  # noqa: E402
from barrels import detect_types as dtp, detector as det, eval_det as ed, geometry as geo, io, report as rp, splits  # noqa: E402
from barrels import worldmap_bridge as wb  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-19_det_bottom"
CAM = geo.AIM_4A8B6118_BOXFIT
SETS = ("HOME", "CAMPUS")


def eval_table_masks() -> dict[str, dict[str, np.ndarray]]:
    """set label -> stem -> the mask the eval table gives the detector (``report.run_arm`` does the segmenting,
    leave-one-scene-out on HOME; its scoring step is replaced by one that keeps the mask)."""
    sp = splits.load_splits()
    sel = rp.select_frames(rp.labeled_stems(), sp, split="train", only_sets=list(SETS))
    rp.refuse_test_frames(sel.stems, sp)
    masks: dict[str, np.ndarray] = {}
    keep, rp.score_frame = rp.score_frame, lambda stem, mask, dcfg, cam: masks.__setitem__(stem, mask)
    try:
        rp.run_arm(rp.Arm("masks", wb.DEFAULT_MODEL), sel, sp, cam=CAM)
    finally:
        rp.score_frame = keep
    return {rp.set_label(k, list(sel.sets)).rstrip("*"): {s: masks[s] for s in stems} for k, stems in sel.sets.items()}


def origin(b: dtp.Barrel, log: list, h: int) -> str:
    """Where this box's bottom row came from."""
    if b.bbox[3] >= h:
        return "frame edge"
    if b.source == "det1":
        return "step 1: top row" if "bottom_inferred" in b.flags else "step 1: seen"
    if b.source == "det2":
        return "stripe: stripe row" if "bottom_inferred" in b.flags else "stripe: seen"
    cap = next((e for e in log if e["stage"] == "cap" and e["why"] == "kept" and tuple(e["box"]) == tuple(b.bbox)), None)
    x0, y0, x1, y1 = cap["bbox"]
    d = CAM._d_axis_from_point_row(y0, geo.BARREL_HEIGHT_MM, +geo.BARREL_END_DIAMETER_MM / 2)
    rows = CAM.barrel_rows(d)
    if (x1 - x0) >= bottom_arms.BASE.stripe_full * rows.width_px:
        est = y0 + CAM.expected_barrel_height_px(d_axis_mm=CAM.f * geo.BARREL_BULGE_DIAMETER_MM / (x1 - x0))
        return "cap, whole width: from the width" if b.bbox[3] == int(round(est)) else "cap, whole width: seen"
    return "cap, narrow: top row" if b.bbox[3] == int(round(rows.bottom)) else "cap, narrow: seen"


def others(b: dtp.Barrel, log: list) -> dict:
    """The bottom row other estimates would give for this box (nan where the estimate does not apply)."""
    x0, y0, x1, y1 = b.bbox
    out = {"from_top": math.nan, "from_stripe": math.nan, "from_width": math.nan}
    top_ok = y0 > 0 and "top_inferred" not in b.flags
    if top_ok:
        out["from_top"] = det.predicted_bottom(CAM, y0)
    kept = next((e for e in log if e["stage"] == "barrel" and e["why"] == "kept" and tuple(e["box"]) == tuple(b.bbox)), None)
    if kept is not None:
        g = det._stripe_geometry(CAM, (kept["bbox"][1] + kept["bbox"][3]) / 2)
        if g is not None:
            out["from_stripe"] = g[1].bottom
    if top_ok and not ({"occluded", "truncated"} & set(b.flags)):
        out["from_width"] = y0 + CAM.expected_barrel_height_px(d_axis_mm=CAM.f * geo.BARREL_BULGE_DIAMETER_MM / (x1 - x0))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arms", default=",".join(bottom_arms.ARMS))
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    out = OUT / args.out if args.out else OUT
    out.mkdir(parents=True, exist_ok=True)
    arms = [a for a in args.arms.split(",") if a]
    masks = eval_table_masks()
    rows = []
    for a in arms:
        for label, per in masks.items():
            for stem, mask in per.items():
                lab = io.load_boxes(stem)
                gts = [g.with_ground(CAM) for g in dtp.barrels_from_boxes(lab)]
                log: list = []
                preds = det.detect(mask, bottom_arms.ARMS[a], CAM, log=log)
                res = ed.evaluate_frame(stem, preds, gts, CAM, rule="v2", clean=lab.get("clean", True))
                hit = {m.pred_idx for m in res.matches}
                for pi, b in enumerate(preds):
                    on = max((g for g in gts if g.color == b.color), key=lambda g: ed.box_iou(b.bbox, g.bbox), default=None)
                    if on is not None and ed.box_iou(b.bbox, on.bbox) < ed.IOU_THR:
                        on = None
                    r = {"arm": a, "set": label, "stem": stem, "color": dtp.COLOR_NAMES[b.color], "bbox": list(b.bbox), "source": b.source,
                         "flags": "+".join(sorted(b.flags)), "bottom_from": origin(b, log, mask.shape[0]), "counted_found": int(pi in hit),
                         "truth_bbox": "", "truth_flags": "", "err": "", "tol": "", "within_tol": "", "err_from_top": "", "err_from_stripe": "", "err_from_width": ""}
                    if on is not None:
                        o = others(b, log)
                        r.update({"truth_bbox": list(on.bbox), "truth_flags": "+".join(sorted(on.flags)), "err": b.bbox[3] - on.bbox[3],
                                  "tol": round(ed.bottom_tol_px(on), 1), "within_tol": int(ed.bottom_within_tol(b, on)),
                                  **{f"err_{k}": ("" if not math.isfinite(v) else round(v - on.bbox[3], 1)) for k, v in o.items()}})
                    rows.append(r)
    with (out / "bottom_edges.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    def med(v, absolute=False):
        v = [abs(x) if absolute else x for x in v if x != ""]
        return f"{np.median(v):.1f}" if v else "-"

    L = ["# Bottom edges: where each box's bottom comes from, and its distance from the hand-drawn bottom", "",
         "HOME (leave-one-scene-out) and CAMPUS train frames, adopted color model. `on a barrel` = same color, IoU >= 0.5 with a "
         "hand-drawn box (the bottom rule not asked). Error = box bottom row - hand-drawn bottom row, px (+ = lower). "
         "`within` = inside the v2 bottom tolerance (a tenth of the hand-drawn height, at least 3 px).", "",
         "| arm | set | boxes | on a barrel | within the v2 bottom tolerance | median abs error, px | median signed error, px |", "|---|---|---|---|---|---|---|"]
    for a in arms:
        for label in masks:
            rs = [r for r in rows if r["arm"] == a and r["set"] == label]
            on = [r for r in rs if r["err"] != ""]
            L.append(f"| {a} | {label} | {len(rs)} | {len(on)} | {sum(r['within_tol'] for r in on)} | {med([r['err'] for r in on], True)} | {med([r['err'] for r in on])} |")
    L += ["", "## By where the bottom came from", "",
          "| arm | set | bottom from | boxes | on a barrel | within | median abs error | median signed error |", "|---|---|---|---|---|---|---|---|"]
    for a in arms:
        for label in masks:
            rs = [r for r in rows if r["arm"] == a and r["set"] == label]
            for k in sorted({r["bottom_from"] for r in rs}):
                ks = [r for r in rs if r["bottom_from"] == k]
                on = [r for r in ks if r["err"] != ""]
                L.append(f"| {a} | {label} | {k} | {len(ks)} | {len(on)} | {sum(r['within_tol'] for r in on)} | {med([r['err'] for r in on], True)} | {med([r['err'] for r in on])} |")
    L += ["", "## Other ways to work out the bottom, on the same boxes (report only; no box is changed)", "",
          "Boxes on a barrel whose hand-drawn bottom was seen (no `bottom_estimated`, `occluded` or `truncated` flag on the label), and "
          "for which all three estimates apply (top seen, a stripe, not flagged occluded or truncated by the detector). Median abs / median signed error, px.", "",
          "| arm | set | boxes | the box as drawn | from the top row | from the stripe row | top + height of a barrel as wide as the box |", "|---|---|---|---|---|---|---|"]
    for a in arms:
        for label in masks:
            rs = [r for r in rows if r["arm"] == a and r["set"] == label and r["err"] != "" and "" not in (r["err_from_top"], r["err_from_stripe"], r["err_from_width"])
                  and not ({"bottom_estimated", "occluded", "truncated"} & set(r["truth_flags"].split("+")))]
            L.append(f"| {a} | {label} | {len(rs)} | " + " | ".join(f"{med([r[k] for r in rs], True)} / {med([r[k] for r in rs])}"
                                                                    for k in ("err", "err_from_top", "err_from_stripe", "err_from_width")) + " |")
    L += ["", "## Every box whose bottom is not a seen one", "", "| arm | frame | color | box | bottom from | hand-drawn | error | tolerance | counted found |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if not r["bottom_from"].endswith("seen"):
            L.append(f"| {r['arm']} | {r['stem'].replace('4A8B_', '')} | {r['color']} | {r['bbox']} | {r['bottom_from']} | {r['truth_bbox'] or 'none'} | {r['err']} | {r['tol']} | {r['counted_found']} |")
    (out / "bottom_edges.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
