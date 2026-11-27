#!/usr/bin/env python3
"""Step A of 2026-11-26_bottom: reproduce "more paint, box disappears" and build its yardstick.

    python barrels/experiments/2026-11-26_bottom/yardstick.py [--jobs 8]

Today's detector (``DetConfig()``; no candidate rule) is run on every ordinary train frame under six color steps
(``lib.PAINT``: the fixed model, saturation floors -20 and -40, hue ranges +-3, the mask dilated by one pixel, the
hand thresholds). Per color step it counts, with the second accounting of ``counting.py``:

- found (strict), found with the box off, missed, boxes that are not on their barrel;
- of the "box off" barrels: how many fail the strict rule by the bottom edge only (``lib.why_off``), and which way;
- of the barrels found under the fixed model and not under this step: how many are lost that way;
- the bottom-edge error of every box that is on a barrel, near and far;
- which rule drew the boxes with the bad bottom, and for stripe boxes the three rows behind the decision: the seen
  bottom, the bottom the stripe's row predicts, the true bottom.

Train frames only (``judge.load_frame`` refuses anything else). Nothing here is a judged run: no candidate is run.
Outputs: results/2026-11-26_bottom/yardstick.md, yardstick.json, yardstick_barrels.csv, sheets/yardstick_*.png.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402
from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import cv as bcv  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import eval_det as ed  # noqa: E402
from barrels import judge as jg  # noqa: E402

_HAND_STEMS: list = []


def _init(hand_stems):
    import cv2
    cv2.setNumThreads(1)
    _HAND_STEMS[:] = hand_stems


def one_frame(stem: str) -> tuple[str, dict]:
    """Every color step on one frame -> per step: the boxes (with the rule that drew each and, for a stripe box, the rows
    behind its bottom) and how much is painted."""
    frame = jg.load_frame(stem)
    out = {}
    for level, mask in lib.masks_for(stem, frame, _HAND_STEMS).items():
        found = lib.detect_found(mask)
        plain = det.detect(mask, det.DetConfig(), lib.CAM)
        assert [f.barrel for f in found] == plain, (stem, level)
        boxes = []
        for f in found:
            more = {"rule": f.rule}
            if f.stripe is not None:
                at = det._at(f.stripe, lib.CAM)
                x0, y0, x1, y1 = f.stripe.bbox
                top_seen, bottom_seen = det._body_extent(mask, f.stripe.body, x0, x1, y0, y1)
                more.update(seen_bottom=int(bottom_seen), pred_bottom=float(at.bottom), seen_top=int(top_seen), pred_top=float(at.top), H=float(at.H), W=float(at.W),
                            center_row=float(f.stripe.center_row), frame_w=int(mask.shape[1]))
            boxes.append(lib.box_dict(f.barrel, **more))
        out[level] = {"boxes": boxes, "paint": int((mask != 0).sum())}
    return stem, out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()
    lib.OUT.mkdir(parents=True, exist_ok=True)
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    hand_stems = [s for v in frames.values() for s in v]
    truth = jg.load_truth(ordinary)
    with Pool(args.jobs, initializer=_init, initargs=(hand_stems,)) as pool:
        res = dict(pool.imap_unordered(one_frame, ordinary, chunksize=2))
    (lib.OUT / "yardstick_boxes.json").write_text(json.dumps(res) + "\n")

    counts: dict[str, dict] = {lv: {} for lv in lib.PAINT}
    rec: dict[str, dict] = {lv: {} for lv in lib.PAINT}          # level -> (stem, gt index) -> one line
    for lv in lib.PAINT:
        for s in ordinary:
            gts = truth.gts[s]
            raw = res[s][lv]["boxes"]
            preds = [lib.as_barrel(b) for b in raw]
            fc, pair = lib.pair_frame(s, preds, gts, truth.clean[s])
            counts[lv][s] = fc
            for gi, g in enumerate(gts):
                r = {"stem": s, "gt": gi, "color": g.color_name, "gt_bbox": list(g.bbox), "gt_flags": sorted(g.flags), "state": fc.gt[gi],
                     "near": lib.is_near(g), "measurable": lib.measurable(g), "why": "", "pred": None}
                if gi in pair:
                    p, b = preds[pair[gi]], raw[pair[gi]]
                    e_px, e_fr = lib.bottom_err(p, g)
                    r.update(pred=b, iou=ed.box_iou(p.bbox, g.bbox), err_px=e_px, err_frac=e_fr, tol_px=ed.bottom_tol_px(g),
                             why=lib.why_off(p, g) if fc.gt[gi] == ct.OFF else "")
                rec[lv][(s, gi)] = r

    def pct(x: float) -> str:
        return f"{100 * x:.1f}"
    base_found = {k for k, r in rec["fixed"].items() if r["state"] == ct.FOUND}
    summary = {}
    L = [f"# The yardstick: \"more paint, box disappears\" on the ordinary train frames ({bcv.git_hash()})", "",
         "`python barrels/experiments/2026-11-26_bottom/yardstick.py`. Today's detector (`DetConfig()`), no candidate rule. "
         f"{len(ordinary)} ordinary train frames; test frames never opened. Counting: `counting.py` (found = the strict rule; "
         "\"box off\" = a box of the right color is on the barrel and fails the strict rule).", "",
         "The color steps:", ""] + [f"- `{lv}`: {lib.PAINT_TEXT[lv]}" for lv in lib.PAINT] + ["",
         "## 1. The count per color step", "",
         "| color step | paint (x fixed) | found, placements | found, per frame | box off, per frame (placements) | missed | boxes not on their barrel (per arrangement) | on empty frames |",
         "|---|---|---|---|---|---|---|---|"]
    paint0 = sum(res[s]["fixed"]["paint"] for s in ordinary)
    for lv in lib.PAINT:
        t = ct.tally(counts[lv], ordinary, truth.placements)
        paint = sum(res[s][lv]["paint"] for s in ordinary) / paint0
        summary[lv] = {"tally": t.to_dict(), "paint_ratio": paint}
        L.append(f"| `{lv}` | {paint:.2f} | {t.found_w:.1f} of {t.placements} | {t.found} of {t.barrels} | {t.off} ({t.off_w:.1f}) | {t.missed} | "
                 f"{t.extra} ({t.extra_w:.1f}) | {t.empty} |")
    L += ["", "## 2. THE YARDSTICK: boxes that are on their barrel and fail the strict rule", "",
          "Per frame. \"bottom only\" = the overlap passes (IoU >= 0.5), the bottom edge is outside the scorer's tolerance. "
          "\"bottom, and so the overlap\" = both fail, and with the bottom put right the box would be a hit. "
          "low = the box ends below the true bottom, high = above. \"other\" = it would still fail with the bottom right.", "",
          "| color step | box off | bottom only: low / high | bottom, and so the overlap: low / high | **the bottom edge is the cause** | other |",
          "|---|---|---|---|---|---|"]
    for lv in lib.PAINT:
        off = [r for r in rec[lv].values() if r["state"] == ct.OFF]
        n = Counter((r["why"], "low" if r["err_px"] > 0 else "high") for r in off)
        cause = sum(v for (w, _), v in n.items() if w != "other")
        summary[lv]["off"] = {"n": len(off), "bottom_low": n[("bottom", "low")], "bottom_high": n[("bottom", "high")],
                              "both_low": n[("bottom+iou", "low")], "both_high": n[("bottom+iou", "high")], "bottom_cause": cause,
                              "other": len(off) - cause}
        L.append(f"| `{lv}` | {len(off)} | {n[('bottom', 'low')]} / {n[('bottom', 'high')]} | {n[('bottom+iou', 'low')]} / {n[('bottom+iou', 'high')]} | "
                 f"**{cause}** | {len(off) - cause} |")
    L += ["", "## 3. Barrels found under the fixed model and not found under the color step (\"more paint, the barrel is lost\")", "",
          "| color step | gained | lost | lost: box on the barrel, the bottom edge is the cause | lost: box on the barrel, other | lost: no box on it |",
          "|---|---|---|---|---|---|"]
    for lv in lib.PAINT[1:]:
        found = {k for k, r in rec[lv].items() if r["state"] == ct.FOUND}
        lost = [rec[lv][k] for k in sorted(base_found - found)]
        nb = sum(1 for r in lost if r["state"] == ct.OFF and r["why"] != "other")
        no = sum(1 for r in lost if r["state"] == ct.OFF and r["why"] == "other")
        summary[lv]["vs_fixed"] = {"gained": len(found - base_found), "lost": len(lost), "lost_bottom": nb, "lost_off_other": no,
                                   "lost_missed": len(lost) - nb - no}
        L.append(f"| `{lv}` | {len(found - base_found)} | {len(lost)} | {nb} | {no} | {len(lost) - nb - no} |")
    L += ["", "## 4. The bottom-edge error of every box that is on a barrel (found or box off)", "",
          f"The box's bottom row minus the true one. Only true bottoms that say where the barrel stands: inside the frame and not flagged "
          f"`bottom_estimated`. near = a true box at least {lib.NEAR_H} px tall, far = shorter. med / p90 = the median and the 90th percentile "
          "of the absolute error; signed = the median with its sign (+ = the box ends too low); outside = the share outside the scorer's "
          "tolerance (10 % of the true height, at least 3 px).", "",
          "| color step | | boxes | med px | p90 px | signed px | med % of height | p90 % | outside |", "|---|---|---|---|---|---|---|---|---|"]
    for lv in lib.PAINT:
        summary[lv]["bottom"] = {}
        for name, sel in (("near", True), ("far", False)):
            rs = [r for r in rec[lv].values() if r["pred"] is not None and r["measurable"] and r["near"] == sel]
            px, fr = lib.stat(r["err_px"] for r in rs), lib.stat(r["err_frac"] for r in rs)
            out = sum(1 for r in rs if abs(r["err_px"]) > r["tol_px"]) / max(1, len(rs))
            summary[lv]["bottom"][name] = {"px": px, "frac": fr, "outside": out}
            L.append(f"| `{lv}` | {name} | {px['n']} | {px['med']:.1f} | {px['p90']:.1f} | {px['signed']:+.1f} | {pct(fr['med'])} | {pct(fr['p90'])} | {pct(out)} % |")
    L += ["", "## 5. Where the bad bottoms come from", "",
          "The boxes of section 2 whose bottom edge is the cause, by the rule that drew them and by whether the drawn bottom was a seen one "
          "or the predicted one (flag `bottom_inferred`).", "",
          "| color step | rule: seen bottom / predicted bottom |", "|---|---|"]
    stripe_rows = []
    for lv in lib.PAINT:
        bad = [r for r in rec[lv].values() if r["state"] == ct.OFF and r["why"] != "other"]
        n = Counter((r["pred"]["rule"], "predicted" if "bottom_inferred" in r["pred"]["flags"] else "seen") for r in bad)
        rules = sorted({k[0] for k in n})
        summary[lv]["bad_by_rule"] = {f"{a}/{b}": v for (a, b), v in n.items()}
        L.append(f"| `{lv}` | " + ("; ".join(f"{ru} {n[(ru, 'seen')]} / {n[(ru, 'predicted')]}" for ru in rules) or "none") + " |")
        for r in bad:
            p = r["pred"]
            if "seen_bottom" in p:
                stripe_rows.append((lv, r, p))
    L += ["", "For the stripe boxes among them (seen bottom drawn): three rows. seen - predicted = how far the painted bottom is below the bottom "
          "the stripe's row predicts; predicted - true = how good the prediction was; both as a share of the predicted height (the detector's "
          "\"agrees\" is 15 %) and of the true height.", "",
          "| color step | boxes | seen bottom below the predicted one: median, range (% of height) | predicted bottom minus true bottom: median, range (% of true height) | "
          "would the predicted bottom pass the scorer |", "|---|---|---|---|---|"]
    for lv in lib.PAINT:
        rs = [(r, p) for l2, r, p in stripe_rows if l2 == lv and "bottom_inferred" not in p["flags"]]
        if not rs:
            L.append(f"| `{lv}` | 0 | | | |")
            continue
        a = np.array([(p["seen_bottom"] - p["pred_bottom"]) / p["H"] for r, p in rs])
        gh = np.array([r["gt_bbox"][3] - r["gt_bbox"][1] for r, p in rs], float)
        b = np.array([(p["pred_bottom"] - r["gt_bbox"][3]) for r, p in rs]) / gh
        ok = sum(1 for (r, p), bb, g in zip(rs, b, gh) if abs(round(p["pred_bottom"]) - r["gt_bbox"][3]) <= max(3, 0.1 * g))
        summary[lv]["stripe_bad"] = {"n": len(rs), "seen_minus_pred": [float(np.median(a)), float(a.min()), float(a.max())],
                                     "pred_minus_true": [float(np.median(b)), float(b.min()), float(b.max())], "pred_would_pass": ok}
        L.append(f"| `{lv}` | {len(rs)} | {pct(np.median(a))}, {pct(a.min())} to {pct(a.max())} | {pct(np.median(b))}, {pct(b.min())} to {pct(b.max())} | {ok} of {len(rs)} |")

    # every stripe box that is on a barrel with a seen bottom: how good are the two rows, whatever the state
    L += ["", "## 6. The two readings of the bottom, on every stripe box that is on a barrel", "",
          "For every box the stripe step drew that is on a barrel with a measurable true bottom: the seen bottom (the last row of body color "
          "under the stripe, as the detector walks it) and the bottom the stripe's row predicts, each against the true bottom. "
          "Absolute error, px and % of the true height; signed = the median with its sign (+ = too low).", "",
          "| color step | | boxes | seen: med px / p90 px / signed / med % / p90 % | predicted: med px / p90 px / signed / med % / p90 % |", "|---|---|---|---|---|"]
    for lv in lib.PAINT:
        summary[lv]["readings"] = {}
        for name, sel in (("near", True), ("far", False)):
            rs = [r for r in rec[lv].values() if r["pred"] is not None and "seen_bottom" in r["pred"] and r["measurable"] and r["near"] == sel]
            gh = [r["gt_bbox"][3] - r["gt_bbox"][1] for r in rs]
            cells = []
            for key in ("seen_bottom", "pred_bottom"):
                e = [r["pred"][key] - r["gt_bbox"][3] for r in rs]
                px, fr = lib.stat(e), lib.stat(x / g for x, g in zip(e, gh))
                summary[lv]["readings"][f"{name}_{key}"] = {"px": px, "frac": fr}
                cells.append(f"{px['med']:.1f} / {px['p90']:.1f} / {px['signed']:+.1f} / {pct(fr['med'])} / {pct(fr['p90'])}")
            L.append(f"| `{lv}` | {name} | {len(rs)} | {cells[0]} | {cells[1]} |")
    # five readings of the bottom, side by side, where all can be made: a stripe box with a SEEN top
    def readings(p: dict) -> dict:
        """The rows a stripe box's bottom could be read from. None where a reading cannot be made."""
        out = {"seen": float(p["seen_bottom"]), "stripe row": p["pred_bottom"]}
        if "top_inferred" not in p["flags"] and p["seen_top"] > 0:
            out["seen top + height"] = p["seen_top"] + p["H"]
            upper = p["center_row"] - p["pred_top"]
            out["seen top and stripe row"] = p["center_row"] + (p["center_row"] - p["seen_top"]) * (p["pred_bottom"] - p["center_row"]) / upper
            x0, _, x1, _ = p["bbox"]
            if p["rule"] in ("whole_stripe", "body_span", "thin_span") and x0 > 0 and x1 < p["frame_w"]:
                out["seen top + height from width"] = p["seen_top"] + lib.CAM.expected_barrel_height_px(d_axis_mm=lib.CAM.f * 25.5 / (x1 - x0))
        return out
    names = ["seen", "stripe row", "seen top + height", "seen top and stripe row", "seen top + height from width"]
    L += ["", "## 7. Five readings of the bottom, side by side", "",
          "Stripe boxes on a barrel with a measurable true bottom and a SEEN top (not predicted, not at the frame top). The readings: "
          "`seen` = the last row of body color under the stripe; `stripe row` = the bottom the stripe's row predicts (the detector's prediction); "
          "`seen top + height` = the seen top plus the height the stripe's row predicts; `seen top and stripe row` = the stripe's row plus "
          "the seen distance from top to stripe, scaled by the barrel's proportions (no distance needed: the barrel is a rigid shape); "
          "`seen top + height from width` = the seen top plus the height of a barrel as wide as the box (only where the whole width is seen). "
          "Each cell: median / 90th percentile of the absolute error in % of the true height, the signed median in px, and the share outside "
          "the scorer's tolerance.", "",
          "| color step | | boxes (with a width) | " + " | ".join(names) + " |", "|---|---|---|" + "---|" * len(names)]
    for lv in lib.PAINT:
        summary[lv]["five"] = {}
        for name, sel in (("near", True), ("far", False)):
            rs = [r for r in rec[lv].values() if r["pred"] is not None and "seen_bottom" in r["pred"] and r["measurable"] and r["near"] == sel
                  and "seen top + height" in readings(r["pred"])]
            cells, n_w = [], 0
            for nm in names:
                e, gh, tol = [], [], []
                for r in rs:
                    v = readings(r["pred"]).get(nm)
                    if v is not None:
                        e.append(round(v) - r["gt_bbox"][3]); gh.append(r["gt_bbox"][3] - r["gt_bbox"][1]); tol.append(r["tol_px"])
                if nm == names[-1]:
                    n_w = len(e)
                if not e:
                    cells.append("-")
                    continue
                fr = lib.stat(x / g for x, g in zip(e, gh))
                out = sum(1 for x, t in zip(e, tol) if abs(x) > t) / len(e)
                summary[lv]["five"][f"{name}_{nm}"] = {"n": len(e), "frac": fr, "signed_px": float(np.median(e)), "outside": out}
                cells.append(f"{pct(fr['med'])} / {pct(fr['p90'])}, {np.median(e):+.1f} px, {pct(out)} %")
            L.append(f"| `{lv}` | {name} | {len(rs)} ({n_w}) | " + " | ".join(cells) + " |")
    L += ["", "Files: `yardstick.json` (every number), `yardstick_barrels.csv` (one line per true barrel per color step), "
          "`yardstick_boxes.json` (every box), `sheets/yardstick_*.png` (the boxes with a bad bottom, to look at).", ""]
    (lib.OUT / "yardstick.md").write_text("\n".join(L))
    (lib.OUT / "yardstick.json").write_text(json.dumps(summary, indent=1) + "\n")
    with (lib.OUT / "yardstick_barrels.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["level", "stem", "barrel", "color", "gt_bbox", "gt_flags", "near", "measurable", "state", "why", "pred_bbox", "rule", "pred_flags",
                    "iou", "bottom_err_px", "bottom_err_frac", "tol_px", "seen_bottom", "pred_bottom", "seen_top", "pred_top", "H"])
        for lv in lib.PAINT:
            for (s, gi), r in sorted(rec[lv].items()):
                p = r["pred"] or {}
                w.writerow([lv, s, gi + 1, r["color"], " ".join(map(str, r["gt_bbox"])), " ".join(r["gt_flags"]), int(r["near"]), int(r["measurable"]),
                            r["state"], r["why"], " ".join(map(str, p.get("bbox", []))), p.get("rule", ""), " ".join(p.get("flags", [])),
                            f"{r['iou']:.3f}" if p else "", f"{r['err_px']:.0f}" if p else "", f"{r['err_frac']:.3f}" if p else "", f"{r['tol_px']:.1f}" if p else "",
                            p.get("seen_bottom", ""), f"{p['pred_bottom']:.1f}" if "pred_bottom" in p else "", p.get("seen_top", ""),
                            f"{p['pred_top']:.1f}" if "pred_top" in p else "", f"{p['H']:.1f}" if "H" in p else ""])

    # contact sheets: the boxes whose bottom edge is the cause, per color step
    for lv in lib.PAINT:
        bad = sorted((r for r in rec[lv].values() if r["state"] == ct.OFF and r["why"] != "other"), key=lambda r: (r["stem"], r["gt"]))
        panels, cache = [], {}
        for r in bad:
            s = r["stem"]
            if s not in cache:
                fr = jg.load_frame(s)
                cache = {s: (fr.bgr, lib.masks_for(s, fr, hand_stems))}
            bgr, masks = cache[s]
            p = r["pred"]
            rows = [(p["pred_bottom"], (0, 255, 0))] if "pred_bottom" in p else []
            txt = [f"{s.replace('4A8B_', '')} #{r['gt'] + 1} {r['color']}  [{lv}]",
                   f"{p['rule']}{' (bottom predicted)' if 'bottom_inferred' in p['flags'] else ''}: bottom {r['err_px']:+.0f} px = {100 * r['err_frac']:+.0f} % (tol {r['tol_px']:.1f})"]
            panels.append(lib.panel(bgr, masks[lv], r["gt_bbox"], [(p["bbox"], (0, 0, 255))], txt, rows=rows))
        if panels:
            lib.sheet(panels, lib.OUT / "sheets" / f"yardstick_{lv}.png")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
