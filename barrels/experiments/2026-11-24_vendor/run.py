#!/usr/bin/env python3
"""Ours against the robot's built-in detector (the vendor, "aivision"), per condition, on the real vendor files
(2026-11-23, for the week's goal: at least as good as the vendor in its own conditions).

No arguments. Two parts, both on the TRAIN frames that have a usable vendor file:

1. VALIDATE the vendor files before trusting a score built on them. Every vendor barrel is paired with the hand box
   of the same color it overlaps most (IoU >= 0.05, best pair first). For those pairs: IoU, vendor width / hand
   width, vendor height / hand height, the offset of each edge and of the center (vendor minus hand, px). The same
   numbers on the free-standing barrels only (hand box with no flag: nothing hides it, not cut by the frame), where
   the vendor sees the whole barrel and a difference is a difference in how it draws. The conversion from the
   vendor's 320x240 units (corner + size, times 2; ``capture.vendor_bbox``) is checked twice: a straight-line fit of
   the hand box edges against the vendor's raw edges (slope ~2 and a small intercept = the conversion is right), and
   the IoU the pairs would have under the other reading (``originx/originy`` as the box CENTER). Pictures: the
   hand boxes (white) and the vendor boxes (its color, with the score) on the raw frame, two frames per condition,
   in ``look/``; and every frame where the vendor finds a barrel we miss, with our boxes too.

2. THE TABLE. Ours (the default color model + ``DetConfig()``) and the vendor scored by the v2 rule
   (``report.run_arm``, unchanged), per condition (``{light}_{surface}``) and per scenario, with the two looser
   counts (overlap only; place only), false boxes and boxes on empty frames. Per barrel: found by ours, found by the
   vendor (strict and by place); the barrels the vendor finds and we miss are listed by frame.

New conditions are picked up by themselves (every labeled train frame with a vendor file). Test frames are refused
before any vendor file is read (``report.vendor_coverage``) and asserted again here.

Outputs: results/<today>_vendor/ — summary.md (plain English), table.md (the one table, ours vs the vendor),
validation.md, per_set.csv, per_frame.csv, per_barrel.csv, pairs.csv, summary.json; look/*.png (ignored by git).
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from barrels import cv as bcv, eval_det as ed, geometry as geo, io, report as rp, splits as splits_mod, worldmap_bridge as wb  # noqa: E402
from barrels.capture import write_rgb  # noqa: E402
from barrels.detect_types import COLOR_NAMES, barrels_from_boxes  # noqa: E402

PAIR_IOU = 0.05                 # a vendor box and a hand box of the same color "are the same barrel" for the validation
LOOK_PER_SET = 2                # validation pictures per condition
CAM = geo.AIM_4A8B6118_BOXFIT
DRAW = {"hand": (255, 255, 255), "orange": (0, 140, 255), "blue": (255, 90, 0), "ours": (0, 220, 0)}    # BGR


def condition(key: str) -> str:
    """``4A8B_lampwarm6_ottoman`` -> ``lampwarm6_ottoman``."""
    return key.split("_", 1)[1] if "_" in key else key


def med(xs) -> float:
    xs = [x for x in xs if x is not None and math.isfinite(x)]
    return float(np.median(xs)) if xs else math.nan


def f2(x, fmt=".2f") -> str:
    return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:{fmt}}"


# ---------------------------------------------------------------- frames

def select(splits):
    """Train frames with a box label, grouped by set; then the ones with a usable vendor file (test refused first)."""
    sel = rp.select_frames(rp.labeled_stems(), splits, split="train")
    cov = rp.vendor_coverage(sel, splits)
    test = set(splits.get("test", []))
    assert not (cov.stems & test), "a test frame got through the vendor selection"
    sets = {k: v for k, v in cov.measured.items() if v}
    return sel, cov, sets


# ---------------------------------------------------------------- 1. validation

def raw_barrels(stem: str):
    """The vendor's barrel objects of one (train, measured) frame with their raw fields: [(color, bbox, raw)]."""
    meta = io.load_vendor(stem)
    out = []
    for o in meta["objects"]:
        c = io.VENDOR_BARREL_NAMES.get(o["name"])
        if c is not None and o.get("bbox") is not None:
            out.append((c, tuple(o["bbox"]), o.get("raw", {})))
    return out, meta


def center_reading(raw: dict) -> tuple | None:
    """The other reading of the vendor's fields: (originx, originy) as the box CENTER, times 2."""
    try:
        x, y, w, h = (float(raw[k]) for k in ("originx", "originy", "width", "height"))
    except (KeyError, TypeError, ValueError):
        return None
    return (2 * (x - w / 2), 2 * (y - h / 2), 2 * (x + w / 2), 2 * (y + h / 2))


def iou_xyxy(a, b) -> float:
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / u if u > 0 else 0.0


def validate(sets: dict) -> dict:
    """Pair every vendor barrel with a hand box; the numbers that say whether the files are sound."""
    pairs, names, scores, unpaired = [], Counter(), [], 0
    fit_x, fit_y = [], []           # (raw box CENTER in vendor units, hand box center in px) on free barrels: the
                                    # center does not depend on how much margin either side draws
    for key, stems in sets.items():
        for s in stems:
            vb, meta = raw_barrels(s)
            names.update(o["name"] for o in meta["objects"])
            gts = barrels_from_boxes(io.load_boxes(s))
            from barrels.detect_types import Barrel
            preds = [Barrel(color=c, bbox=b, source="aivision") for c, b, _ in vb]
            for _, _, raw in vb:
                if isinstance(raw.get("score"), (int, float)):
                    scores.append(raw["score"])
            m = ed.match_best_first(preds, gts, lambda p, g: ed.box_iou(p.bbox, g.bbox), PAIR_IOU)
            unpaired += len(preds) - len(m)
            for pi, gi, iou in m:
                p, g, raw = preds[pi], gts[gi], vb[pi][2]
                free = not g.flags
                alt = center_reading(raw)
                d = {"stem": s, "set": condition(key), "color": COLOR_NAMES[p.color], "free": int(free),
                     "flags": "+".join(sorted(g.flags)), "score": raw.get("score"), "iou": iou,
                     "iou_if_center": iou_xyxy(alt, g.bbox) if alt else math.nan,
                     "w_ratio": p.width / g.width, "h_ratio": p.height / g.height,
                     "dx0": p.bbox[0] - g.bbox[0], "dy0": p.bbox[1] - g.bbox[1], "dx1": p.bbox[2] - g.bbox[2], "dy1": p.bbox[3] - g.bbox[3],
                     "dcx": (p.bbox[0] + p.bbox[2] - g.bbox[0] - g.bbox[2]) / 2, "dcy": (p.bbox[1] + p.bbox[3] - g.bbox[1] - g.bbox[3]) / 2,
                     "hand_w": g.width, "hand_h": g.height, "vendor": list(p.bbox), "hand": list(g.bbox)}
                pairs.append(d)
                if free and all(k in raw for k in ("originx", "originy", "width", "height")):
                    fit_x.append((raw["originx"] + raw["width"] / 2, (g.bbox[0] + g.bbox[2]) / 2))
                    fit_y.append((raw["originy"] + raw["height"] / 2, (g.bbox[1] + g.bbox[3]) / 2))

    def fit(pts):
        if len(pts) < 4:
            return {"n": len(pts), "slope": math.nan, "intercept": math.nan}
        a = np.array(pts, float)
        slope, icpt = np.polyfit(a[:, 0], a[:, 1], 1)
        resid = a[:, 1] - (slope * a[:, 0] + icpt)
        return {"n": len(pts), "slope": float(slope), "intercept": float(icpt), "resid_med_abs": float(np.median(np.abs(resid)))}

    def stats(ps):
        return {"pairs": len(ps), **{k: med(p[k] for p in ps) for k in
                ("iou", "iou_if_center", "w_ratio", "h_ratio", "dx0", "dy0", "dx1", "dy1", "dcx", "dcy")}}
    per_set = {}
    for p in pairs:
        per_set.setdefault(p["set"], []).append(p)
    return {"pairs": pairs, "all": stats(pairs), "free": stats([p for p in pairs if p["free"]]),
            "occluded": stats([p for p in pairs if "occluded" in p["flags"]]),
            "truncated": stats([p for p in pairs if "truncated" in p["flags"]]),
            "visible_only": sum(1 for p in pairs if "occluded" in p["flags"] and (p["w_ratio"] < 0.85 or p["dy1"] <= -8 or p["dy0"] >= 10)),
            "per_set_free": {k: stats([p for p in v if p["free"]]) for k, v in per_set.items()},
            "fit_x": fit(fit_x), "fit_y": fit(fit_y), "names": dict(names), "unpaired_vendor_boxes": unpaired,
            "score_min": min(scores) if scores else None, "score_median": med(scores), "n_scores": len(scores),
            "scores_below_80": sum(1 for x in scores if x < 80)}


# ---------------------------------------------------------------- 2. the two arms, every box kept

class Capture:
    """Wraps ``report.score_boxes`` while an arm runs, so the boxes each arm drew and the true barrels are kept per
    frame. The scoring itself is the unchanged function."""

    def __init__(self):
        self.boxes: dict[str, dict[str, tuple[list, list]]] = defaultdict(dict)
        self.arm = ""
        self._orig = rp.score_boxes

    def __enter__(self):
        orig = self._orig

        def wrapped(stem, preds, cam, loose=None, labels_dir=None):
            gts = [b.with_ground(cam) for b in barrels_from_boxes(io.load_boxes(stem, labels_dir))]
            self.boxes[self.arm][stem] = (list(preds), gts)
            return orig(stem, preds, cam, loose, labels_dir)
        rp.score_boxes = wrapped
        return self

    def __exit__(self, *exc):
        rp.score_boxes = self._orig


def place_found(preds, gts) -> set[int]:
    """The true barrels found by the place count (``report.loose_counts``, same rule, with the indices)."""
    def dist(p, g):
        (px, py), (gx, gy) = rp.box_center(p), rp.box_center(g)
        return math.hypot(px - gx, py - gy)
    m = ed.match_best_first(preds, gts, lambda p, g: 1.0 / (1.0 + dist(p, g)), 0.0,
                            eligible=lambda p, g: dist(p, g) <= rp.CENTER_TOL_WIDTHS * g.width)
    return {gi for _, gi, _ in m}


def run_arms(sel, cov, splits):
    ours, vendor = rp.Arm("ours", wb.DEFAULT_MODEL), rp.vendor_arm("vendor")
    cache, cap = rp.FrameCache(), Capture()
    lo, lv = {}, {}
    with cap:
        cap.arm = "ours"
        ro = rp.run_arm(ours, sel, splits, cam=CAM, cache=cache, only=cov.stems, loose=lo, vendor=cov)
        cap.arm = "vendor"
        rv = rp.run_arm(vendor, sel, splits, cam=CAM, only=cov.stems, loose=lv, vendor=cov)
    return ours, vendor, ro, rv, lo, lv, cap, cache


def per_barrel(sets, ro, rv, cap) -> list[dict]:
    rows = []
    for key, stems in sets.items():
        for s in stems:
            gts = cap.boxes["ours"][s][1]
            fo = {m.gt_idx for m in ro[s].matches}
            fv = {m.gt_idx for m in rv[s].matches}
            po = place_found(*cap.boxes["ours"][s])
            pv = place_found(*cap.boxes["vendor"][s])
            for gi, g in enumerate(gts):
                rows.append({"set": condition(key), "stem": s, "scene": io.parse_name(s)["scene"], "nn": io.parse_name(s)["nn"],
                             "gt": gi + 1, "color": COLOR_NAMES[g.color], "bbox": list(g.bbox), "flags": "+".join(sorted(g.flags)),
                             "ours": int(gi in fo), "vendor": int(gi in fv), "ours_place": int(gi in po), "vendor_place": int(gi in pv)})
    return rows


# ---------------------------------------------------------------- pictures

def draw(stem: str, cap, out: Path, with_ours: bool, mark: set[int] = frozenset()) -> Path:
    img = io.load_image(io.find_image(stem))          # a train frame: the caller only draws measured train frames
    _, gts = cap.boxes["vendor"][stem]
    for gi, g in enumerate(gts):
        x0, y0, x1, y1 = g.bbox
        cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), DRAW["hand"], 3 if gi in mark else 1)
        cv2.putText(img, f"#{gi + 1}", (x0 + 2, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, DRAW["hand"], 1, cv2.LINE_AA)
    vb, _ = raw_barrels(stem)
    for c, (x0, y0, x1, y1), raw in vb:
        col = DRAW[COLOR_NAMES[c]]
        cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), col, 2)
        cv2.putText(img, f"V{raw.get('score', '')}", (x0 + 2, max(10, y0 - 3)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, col, 1, cv2.LINE_AA)
    if with_ours:
        for p in cap.boxes["ours"][stem][0]:
            x0, y0, x1, y1 = p.bbox
            cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), DRAW["ours"], 1)
            cv2.putText(img, "ours " + COLOR_NAMES[p.color][0], (x0 + 2, y0 + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, DRAW["ours"], 1, cv2.LINE_AA)
    cv2.putText(img, stem + ("  white=hand  V=vendor  green=ours" if with_ours else "  white=hand  V=vendor"), (6, 472),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"{stem}.png"
    cv2.imwrite(str(p), img)
    return p


def look_frames(stems: list[str], cap) -> list[str]:
    """Two frames of a condition for the validation pictures: core_01 if there, and the frame with most vendor barrels."""
    pick = [s for s in stems if io.parse_name(s)["scene"] == "core"][:1]
    rest = sorted((s for s in stems if s not in pick), key=lambda s: -len(cap.boxes["vendor"][s][0]))
    return (pick + rest)[:LOOK_PER_SET]


# ---------------------------------------------------------------- the words

def set_counts(res: dict, loose: dict, stems: list[str]) -> dict:
    c = rp.summarize([res[s] for s in stems], [loose[s] for s in stems])
    return {"frames": c.frames, "barrels": c.barrels, "found": c.found, "false": c.false, "empty_frame_boxes": c.neg_false,
            "found_overlap": c.loose["found_iou"], "false_overlap": c.loose["false_iou"],
            "found_place": c.loose["found_center"], "false_place": c.loose["false_center"], "width": c.width, "score": c.score}


def verdict(o: dict, v: dict) -> str:
    """Who is better on a condition: more barrels found (strict) wins unless it also brings at least as many more
    false boxes; then "mixed". The difference is spelled out: "vendor (+10 found, +1 false)"."""
    df, dx = v["found"] - o["found"], v["false"] - o["false"]
    if df == 0 and dx == 0:
        return "tie"
    if df == 0:
        return f"{'ours' if dx > 0 else 'vendor'} (same found, {abs(dx)} fewer false)"
    who, n, extra = ("vendor", df, dx) if df > 0 else ("ours", -df, -dx)
    if extra >= n:
        return f"mixed ({who} +{n} found, +{extra} false)"
    return f"{who} (+{n} found, {extra:+d} false)"


def write_summary(out: Path, val: dict, sets: dict, cmp: dict, barrels: list[dict], cov, git: str, looked: list[str]) -> str:
    L = [f"# Ours against the vendor detector, per condition ({dt.date.today().isoformat()}, git {git})", "",
         "Train frames with a vendor file only; test frames are never opened. Ours = the default color model and detector. "
         "Strict = the v2 rule (same color, IoU at least 0.5, bottom edge within a tenth of the height). "
         "Overlap = same color and IoU at least 0.5. Place = a box of the right color centered on the barrel. "
         "False = boxes on no barrel; empty = boxes on frames with no barrel.", ""]
    a, f = val["all"], val["free"]
    L += ["## Are the vendor files sound?", "",
          f"- {a['pairs']} vendor barrel boxes paired with a hand box ({val['unpaired_vendor_boxes']} vendor barrel boxes sit on no hand box). "
          f"Classes seen: " + ", ".join(f"{k} {v}" for k, v in sorted(val["names"].items())) + ".",
          f"- Placement and scale: the hand box centers against the vendor's raw box centers (its own 320x240 units) fit a line of slope "
          f"{f2(val['fit_x']['slope'])} (x) and {f2(val['fit_y']['slope'])} (y), offsets {f2(val['fit_x']['intercept'], '.1f')} and "
          f"{f2(val['fit_y']['intercept'], '.1f')} px (expected: slope 2, offset 0). The conversion (corner and size, times 2) is "
          + ("right." if abs(val['fit_x']['slope'] - 2) < 0.1 and abs(val['fit_y']['slope'] - 2) < 0.1 else "**in doubt: check.**"),
          f"- Read as a center instead of a corner, the median IoU would be {f2(a['iou_if_center'])} instead of {f2(a['iou'])}: the corner reading is the right one.",
          f"- On free-standing barrels ({f['pairs']} pairs): median IoU {f2(f['iou'])}, vendor width / hand width {f2(f['w_ratio'])}, "
          f"height {f2(f['h_ratio'])}; median offsets (vendor minus hand, px): left {f2(f['dx0'], '+.0f')}, top {f2(f['dy0'], '+.0f')}, "
          f"right {f2(f['dx1'], '+.0f')}, bottom {f2(f['dy1'], '+.0f')}.",
          f"- On hidden barrels ({val['occluded']['pairs']} pairs, median IoU {f2(val['occluded']['iou'])}) the vendor boxes the part it "
          f"sees, our labels the whole barrel: {val['visible_only']} of them are visibly cut (narrower than 0.85 of the hand box, or the "
          "bottom 8 px or more above the hand box's, or the top 10 px or more below). That is where the strict rule is harsh on it; "
          "the place count is the fairer one on hidden barrels.\n"
          "- Timing: every frame was still, so a lag of the vendor's list behind the frame cannot be seen here (the vendor "
          "list is read when the frame arrives, `read_at: frame`).",
          f"- Scores: median {f2(val['score_median'], '.0f')}, lowest {val['score_min']}; {val['scores_below_80']} of {val['n_scores']} below 80.",
          f"- Pictures: `look/` ({len(looked)} frames; white = hand, colored with V = vendor, green = ours).", ""]
    L += ["## Per condition", "", "| condition | frames | barrels | ours strict / overlap / place | ours false (empty) | vendor strict / overlap / place | vendor false (empty) | better |",
          "|---|---:|---:|---|---|---|---|---|"]
    for k in sets:
        o, v = cmp[k]["ours"], cmp[k]["vendor"]
        L.append(f"| {condition(k)} | {o['frames']} | {o['barrels']} | {o['found']} / {o['found_overlap']} / {o['found_place']} | {o['false']} ({o['empty_frame_boxes']}) | "
                 f"{v['found']} / {v['found_overlap']} / {v['found_place']} | {v['false']} ({v['empty_frame_boxes']}) | {verdict(o, v)} |")
    L.append("")
    for k in sets:
        o, v = cmp[k]["ours"], cmp[k]["vendor"]
        L.append(f"- **{condition(k)}**: ours found {o['found']} of {o['barrels']} with {o['false']} false; "
                 f"the vendor found {v['found']} of {v['barrels']} with {v['false']} false. Better: {verdict(o, v)}.")
    to = sum(cmp[k]["ours"]["found"] for k in sets); tv = sum(cmp[k]["vendor"]["found"] for k in sets)
    tn = sum(cmp[k]["ours"]["barrels"] for k in sets)
    fo = sum(cmp[k]["ours"]["false"] for k in sets); fv = sum(cmp[k]["vendor"]["false"] for k in sets)
    L += ["", f"All together: ours {to} of {tn} with {fo} false, the vendor {tv} of {tn} with {fv} false.", ""]
    by_scene = defaultdict(list)
    for b in barrels:
        by_scene[b["scene"]].append(b)
    L += ["## Per scenario, all conditions together (strict; place in brackets)", "", "| scenario | barrels | ours | vendor |", "|---|---:|---:|---:|"]
    for sc in sorted(by_scene):
        bs = by_scene[sc]
        L.append(f"| {sc} | {len(bs)} | {sum(b['ours'] for b in bs)} ({sum(b['ours_place'] for b in bs)}) | "
                 f"{sum(b['vendor'] for b in bs)} ({sum(b['vendor_place'] for b in bs)}) |")
    L.append("")
    vm = [b for b in barrels if b["vendor"] and not b["ours"]]
    vm_place = [b for b in barrels if b["vendor_place"] and not b["vendor"] and not b["ours"] and not b["ours_place"]]
    om = [b for b in barrels if b["ours"] and not b["vendor"]]
    L += ["## Where the vendor finds a barrel we miss (the list for the detector work)", "",
          f"{len(vm)} barrels the vendor finds under the strict rule and we do not; {len(vm_place)} more the vendor at least "
          "points at (place count) where we have nothing in place. Hand box number as in the picture (`look/<frame>.png`, thick white).", "",
          "| frame | # | color | flags | ours by place | vendor |", "|---|---:|---|---|---|---|"]
    for b in vm:
        L.append(f"| {b['stem']} | {b['gt']} | {b['color']} | {b['flags'] or '-'} | {'yes' if b['ours_place'] else 'no'} | strict |")
    for b in vm_place:
        L.append(f"| {b['stem']} | {b['gt']} | {b['color']} | {b['flags'] or '-'} | no | place only |")
    L += ["", f"The other way: {len(om)} barrels we find (strict) and the vendor does not.", ""]
    occl = [b for b in barrels if b["scene"].startswith("occl")]
    if occl:
        L += [f"Occlusion shots (`occl`, `occlx`): ours {sum(b['ours'] for b in occl)}, the vendor {sum(b['vendor'] for b in occl)} "
              f"of {len(occl)} barrels (strict); by place ours {sum(b['ours_place'] for b in occl)}, the vendor {sum(b['vendor_place'] for b in occl)}.", ""]
    left = [f"{len(cov.no_file)} train frames have no vendor file (shot before 2026-11-18)"]
    if cov.not_measured:
        left.append(f"{len(cov.not_measured)} say available: false (not measured): {', '.join(cov.not_measured)}")
    if cov.unreadable:
        left.append(f"{len(cov.unreadable)} could not be read: {', '.join(cov.unreadable)}")
    L += ["Left out: " + "; ".join(left) + ".", "", "Full table: `table.md`. Numbers: `per_set.csv`, `per_frame.csv`, `per_barrel.csv`, `pairs.csv`, `validation.md`.", ""]
    text = "\n".join(L)
    (out / "summary.md").write_text(text)
    return text


def main() -> int:
    splits = splits_mod.load_splits()
    sel, cov, sets = select(splits)
    out = bcv.fresh_dir(io.PKG_ROOT / "results" / f"{dt.date.today().isoformat()}_vendor")
    if not sets:
        (out / "summary.md").write_text("# Ours against the vendor\n\nNo train frame has a usable vendor file.\n")
        print("no train frame has a usable vendor file"); return 1
    ours, vendor, ro, rv, lo, lv, cap, cache = run_arms(sel, cov, splits)
    val = validate(sets)
    shown = rp.Selection(sets, sel.skipped, sel.split)
    rep = rp.Report(rp.build_rows(sets, ro, rv, lo, lv), ours, vendor, shown, "loso", bcv.git_hash(), math.nan, cov, True)
    (out / "table.md").write_text("# Ours (candidate) against the vendor (baseline)\n\n```\n" + rp.format_text(rep) + "\n```\n")
    cmp = {k: {"ours": set_counts(ro, lo, v), "vendor": set_counts(rv, lv, v)} for k, v in sets.items()}
    barrels = per_barrel(sets, ro, rv, cap)
    looked = []
    for k, stems in sets.items():
        for s in look_frames(stems, cap):
            draw(s, cap, out / "look", with_ours=True); looked.append(s)
    marks = defaultdict(set)
    for b in barrels:
        if (b["vendor"] or b["vendor_place"]) and not b["ours"]:
            marks[b["stem"]].add(b["gt"] - 1)
    for s, m in marks.items():
        draw(s, cap, out / "look", with_ours=True, mark=m)
        if s not in looked:
            looked.append(s)
    # files
    with (out / "per_set.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        cols = list(next(iter(cmp.values()))["ours"])
        w.writerow(["condition", "arm"] + cols)
        for k in sets:
            for a in ("ours", "vendor"):
                w.writerow([condition(k), a] + [cmp[k][a][c] for c in cols])
    with (out / "per_frame.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["condition", "stem", "scene", "barrels", "ours_found", "ours_false", "vendor_found", "vendor_false",
                    "ours_place", "vendor_place", "vendor_boxes"])
        for k, stems in sets.items():
            for s in stems:
                w.writerow([condition(k), s, io.parse_name(s)["scene"], sum(ro[s].n_gt.values()), sum(ro[s].tp.values()), sum(ro[s].fp.values()),
                            sum(rv[s].tp.values()), sum(rv[s].fp.values()), lo[s]["found_center"], lv[s]["found_center"], len(cap.boxes["vendor"][s][0])])
    with (out / "per_barrel.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(barrels[0]) if barrels else ["stem"]); w.writeheader(); w.writerows(barrels)
    with (out / "pairs.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(val["pairs"][0]) if val["pairs"] else ["stem"]); w.writeheader(); w.writerows(val["pairs"])
    vl = ["# Vendor files: validation", "", "| subset | pairs | IoU | IoU if center | w ratio | h ratio | left | top | right | bottom | center x | center y |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, st in [("all pairs", val["all"]), ("free-standing", val["free"]), ("hidden (occluded)", val["occluded"]),
                     ("cut by the frame (truncated)", val["truncated"])] + [(f"free, {k}", v) for k, v in val["per_set_free"].items()]:
        vl.append(f"| {name} | {st['pairs']} | {f2(st['iou'])} | {f2(st['iou_if_center'])} | {f2(st['w_ratio'])} | {f2(st['h_ratio'])} | "
                  + " | ".join(f2(st[k], '+.1f') for k in ("dx0", "dy0", "dx1", "dy1", "dcx", "dcy")) + " |")
    vl += ["", f"Center fit, hand box center px = slope x vendor raw center (320x240 units) + offset (free barrels): x {val['fit_x']}, y {val['fit_y']}.",
           "Offsets are vendor minus hand, px (negative top = the vendor box starts higher). Medians.", ""]
    (out / "validation.md").write_text("\n".join(vl))
    summary = {"git": bcv.git_hash(), "date": dt.date.today().isoformat(),
               "conditions": {condition(k): cmp[k] for k in sets},
               "validation": {k: v for k, v in val.items() if k != "pairs"},
               "vendor_finds_we_miss": [b for b in barrels if b["vendor"] and not b["ours"]],
               "vendor_place_only_we_miss": [b for b in barrels if b["vendor_place"] and not b["vendor"] and not b["ours"] and not b["ours_place"]],
               "coverage": cov.to_dict()}
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=float) + "\n")
    print(write_summary(out, val, sets, cmp, barrels, cov, bcv.git_hash(), looked))
    print("written to", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
