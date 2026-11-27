#!/usr/bin/env python3
"""Part A of the contrast experiment: the candidate finder measured against the hand boxes (no detector, no judge).

    python barrels/experiments/2026-11-26_contrast/finder.py [--jobs 8] [--grid]

For every train frame and every setting of the finder (channel, margin, share of the width): the candidates, the
strongest first. Per labelled barrel: the rank of the first candidate of the right color on its stripe
(``common.on_stripe``), and how well that candidate's predicted box fits the hand box. Per frame: the candidates
that are on no barrel. Writes results/2026-11-26_contrast/finder.md and finder.json.

``--grid``: the whole grid of settings (the comparison table). Without it: the reference setting only, with the
per-condition table and the list of where it breaks.

This is a measurement at known barrel locations. It chooses nothing by itself; what was read off it before the plan
was written is listed in PREREG.md.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402

from barrels import contrast_c4 as cn  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

KS = (3, 5, 10, 20)
REF = ("logrb", 8.0, 0.5, 0.5)                                  # channel, offset, margin, width_share
GRID = ([("logrb", o, m, q) for o in (1.0, 8.0, 16.0) for m in (0.3, 0.5, 0.75, 1.0) for q in (0.4, 0.5, 0.7)]
        + [("opp", 8.0, m, q) for m in (0.08, 0.12, 0.2, 0.3) for q in (0.4, 0.5, 0.7)])
COLOR = {"orange": ORANGE, "blue": BLUE}


def key(s) -> str:
    return f"{s[0]} o={s[1]:g} margin={s[2]:g} share={s[3]:g}"


def params(s) -> cn.Params:
    return cn.Params(channel=s[0], offset=s[1], margin=s[2], width_share=s[3])


def _one(args) -> dict:
    """One frame, many settings -> per setting: per barrel (rank of the first candidate on its stripe, IoU of its
    predicted box, the measured guard values), and the candidates on no barrel."""
    import cv2
    cv2.setNumThreads(1)
    stem, settings = args
    frame = jg.load_frame(stem)                                 # refuses anything but a train frame
    lab = io.load_boxes(stem, check_image=False)
    gts = dtp.barrels_from_boxes(lab)
    base = jg.fixed_detector()(stem, frame)
    fc = ct.classify_frame(stem, base, gts, bool(lab.get("clean", True)))
    out = {"stem": stem, "barrels": [{"color": b["color"], "bbox": b["bbox"], "kind": cm.barrel_kind(stem, b), "fixed": st,
                                      "flags": b.get("flags", [])} for b, st in zip(lab["barrels"], fc.gt)], "by": {}}
    feat = None
    for s in settings:
        p = params(s)
        resp = cn.respond(frame.rgb, cm.CAM, p)
        cands = cn.find(frame.rgb, cm.CAM, p, resp=resp, limit=max(KS))
        if feat is None:
            feat = cn.features(frame.rgb, p.feat_offset, p.bright)
        rec = {"n": len(cands), "barrels": [], "loose": []}
        for b in lab["barrels"]:
            hit = next(((i, c) for i, c in enumerate(cands) if c.color == COLOR[b["color"]] and cm.on_stripe(c, b["bbox"])), None)
            wrong = next((i for i, c in enumerate(cands) if c.color != COLOR[b["color"]] and cm.on_stripe(c, b["bbox"])), None)
            r = {"rank": None if hit is None else hit[0], "wrong_rank": wrong}
            if hit is not None:
                c = hit[1]
                info = cn.measure(c, resp, feat, p)
                r.update(iou=round(cm.iou(c.box, b["bbox"]), 3), share=round(c.share, 3), strength=round(c.strength, 3),
                         dbottom=round(c.box[3] - b["bbox"][3], 1), dtop=round(c.box[1] - b["bbox"][1], 1),
                         **_guards(info))
            rec["barrels"].append(r)
        for i, c in enumerate(cands):
            if not any(cm.in_box(c, b["bbox"]) for b in lab["barrels"]):
                info = cn.measure(c, resp, feat, p)
                rec["loose"].append({"rank": i, "color": c.color, "row": c.row, "x": c.x, "share": round(c.share, 3),
                                     "strength": round(c.strength, 3), **_guards(info)})
        out["by"][key(s)] = rec
    return out


def _guards(info: dict) -> dict:
    if "d" not in info:
        return {"unreadable": True}
    off = info["off"]
    return {"alike": round(info["alike"], 3), "alike_rel": round(info["alike_rel"], 3), "orange_part": round(info["orange_part"], 3),
            "off": {k: (None if v is None else round(v, 3)) for k, v in off.items()}, "d": round(info["d"], 3)}


def summarize(recs: list[dict], k: str, stems: list[str], kinds=("clean",)) -> dict:
    """Over ``stems``: barrels of ``kinds`` with a candidate on their stripe within the top K; candidates on no barrel
    per frame (all frames / empty frames)."""
    by = {r["stem"]: r for r in recs}
    n = 0
    hit = dict.fromkeys(KS, 0)
    loose_all, loose_empty, n_empty, ious = [], [], 0, []
    for s in stems:
        r = by[s]
        rec = r["by"][k]
        for b, br in zip(r["barrels"], rec["barrels"]):
            if b["kind"] not in kinds:
                continue
            n += 1
            for kk in KS:
                hit[kk] += br["rank"] is not None and br["rank"] < kk
            if br["rank"] is not None:
                ious.append(br["iou"])
        loose_all.append(len(rec["loose"]))
        if not r["barrels"]:
            n_empty += 1
            loose_empty.append(len(rec["loose"]))
    return {"barrels": n, "hit": hit, "frames": len(stems), "loose_per_frame": sum(loose_all) / max(1, len(stems)),
            "empty_frames": n_empty, "loose_per_empty": (sum(loose_empty) / n_empty) if n_empty else None,
            "empty_with_any": sum(1 for v in loose_empty if v), "iou_median": sorted(ious)[len(ious) // 2] if ious else None,
            "iou_ge_05": sum(1 for v in ious if v >= 0.5)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--grid", action="store_true")
    a = ap.parse_args()
    fr = cm.frames()
    stems = fr["ordinary"] + fr["extreme"] + fr["excluded"]
    jg.require_train(stems)
    settings = GRID if a.grid else [REF]
    with Pool(a.jobs) as pool:
        recs = pool.map(_one, [(s, settings) for s in stems], chunksize=2)
    cm.OUT.mkdir(parents=True, exist_ok=True)
    L: list[str] = []
    if a.grid:
        L += ["# The finder, every setting (in-sample; a measurement at known barrel locations, not a verdict)", "",
              "`python barrels/experiments/2026-11-26_contrast/finder.py --grid`. Ordinary train frames: clean upright barrels and partly hidden ones "
              "(flag occluded or truncated) with a candidate of the right color on their stripe among the 5 / 20 strongest candidates of the frame; "
              "candidates on no barrel per frame and per empty frame (of at most 20). Extreme = the parked conditions; brightness 1 = excluded.", "",
              "| setting | clean, top 5 | clean, top 20 | hidden, top 20 | extreme clean, top 20 | brightness 1 clean, top 20 | on no barrel, per ordinary frame | per empty frame | empty frames with any (of 22) |",
              "|---|---|---|---|---|---|---|---|---|"]
        for s in settings:
            k = key(s)
            o = summarize(recs, k, fr["ordinary"])
            hdn = summarize(recs, k, fr["ordinary"], ("hidden",))
            e = summarize(recs, k, fr["extreme"])
            x = summarize(recs, k, fr["excluded"])
            L.append(f"| {k} | {o['hit'][5]} of {o['barrels']} | {o['hit'][20]} | {hdn['hit'][20]} of {hdn['barrels']} | {e['hit'][20]} of {e['barrels']} | "
                     f"{x['hit'][20]} of {x['barrels']} | {o['loose_per_frame']:.2f} | {o['loose_per_empty']:.2f} | {o['empty_with_any']} |")
        (cm.OUT / "finder_grid.md").write_text("\n".join(L) + "\n")
        print("\n".join(L))
        return 0
    k = key(REF)
    L += [f"# The finder at the reference setting ({k}; no guard, at most 20 candidates a frame)", "",
          "`python barrels/experiments/2026-11-26_contrast/finder.py`. A measurement at known barrel locations: a barrel counts when a candidate of its "
          "color has its stripe point on the barrel's stripe (the middle 70 % of the hand box's columns, rows 0.35 to 0.80 of its height). "
          "Clean = upright, whole, in view. Hidden = flagged occluded or truncated. 'On no barrel' = the stripe point is in no hand box.", "",
          "| condition | class | frames | clean: top 3 | top 5 | top 10 | top 20 | of | missed by the fixed colors, with a candidate | hidden: top 20 | of | predicted box IoU, median | IoU >= 0.5 | on no barrel per frame | empty frames: candidates |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    by = {r["stem"]: r for r in recs}
    groups: dict[str, list[str]] = defaultdict(list)
    for s in stems:
        groups[ct.condition_of(s)].append(s)
    totals = defaultdict(list)
    for cond, ss in groups.items():
        klass = cm.klass_of(ss[0])
        totals[klass] += ss
        L.append(_row(cond, klass, recs, by, k, ss))
    for klass, ss in totals.items():
        L.append(_row(f"**all {klass}**", klass, recs, by, k, ss))
    # where it breaks
    L += ["", "## Clean barrels without a candidate on their stripe (top 20)", ""]
    for s in stems:
        r = by[s]
        for i, (b, br) in enumerate(zip(r["barrels"], r["by"][k]["barrels"])):
            if b["kind"] == "clean" and br["rank"] is None:
                x0, y0, x1, y1 = b["bbox"]
                L.append(f"- {s.replace('4A8B_', '')} #{i + 1} {b['color']} {b['bbox']} (h {y1 - y0}, bottom {y1}); fixed colors: {b['fixed']}"
                         + (f"; a candidate of the OTHER color is on it (rank {br['wrong_rank']})" if br["wrong_rank"] is not None else ""))
    L += ["", "## Hidden barrels without a candidate (top 20)", ""]
    for s in stems:
        r = by[s]
        for i, (b, br) in enumerate(zip(r["barrels"], r["by"][k]["barrels"])):
            if b["kind"] == "hidden" and br["rank"] is None and cm.klass_of(s) == "ordinary":
                L.append(f"- {s.replace('4A8B_', '')} #{i + 1} {b['color']} {b['bbox']} {b['flags']}; fixed colors: {b['fixed']}")
    L += ["", "## The named traps: candidates on the cluttered empty frames", ""]
    for s in cm.TRAPS:
        lo = by[s]["by"][k]["loose"]
        L.append(f"- {s.replace('4A8B_', '')}: {len(lo)} candidates: " + "; ".join(
            f"{'orange' if c['color'] == ORANGE else 'blue'} at ({c['x']}, {c['row']}) share {c['share']:.2f} strength {c['strength']:.2f}" for c in lo))
    (cm.OUT / "finder.md").write_text("\n".join(L) + "\n")
    (cm.OUT / "finder.json").write_text(json.dumps({"setting": k, "params": dataclasses.asdict(params(REF)), "frames": recs}, indent=None) + "\n")
    print("\n".join(L))
    return 0


def _row(name: str, klass: str, recs, by, k, ss) -> str:
    o = summarize(recs, k, ss)
    hdn = summarize(recs, k, ss, ("hidden",))
    miss = [(b, br) for s in ss for b, br in zip(by[s]["barrels"], by[s]["by"][k]["barrels"]) if b["kind"] == "clean" and b["fixed"] != "found"]
    got = sum(1 for b, br in miss if br["rank"] is not None)
    empt = [len(by[s]["by"][k]["loose"]) for s in ss if not by[s]["barrels"]]
    return (f"| {name} | {klass} | {len(ss)} | {o['hit'][3]} | {o['hit'][5]} | {o['hit'][10]} | {o['hit'][20]} | {o['barrels']} | {got} of {len(miss)} | "
            f"{hdn['hit'][20]} | {hdn['barrels']} | {o['iou_median'] if o['iou_median'] is not None else ''} | {o['iou_ge_05']} | {o['loose_per_frame']:.2f} | "
            f"{', '.join(map(str, empt))} |")


if __name__ == "__main__":
    sys.exit(main())
