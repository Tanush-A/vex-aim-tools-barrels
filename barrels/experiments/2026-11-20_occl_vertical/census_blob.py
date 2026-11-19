#!/usr/bin/env python3
"""Census 2, before any rule is built (measurements only): the four other leads.

P. A post across the middle. The stripe pieces the finder refuses for their width: how wide they are; and "two such
   pieces at the same rows, each seen from top to bottom, whose outer edges are one barrel apart" as a candidate:
   how many of the post scenes have one, how many such pairs exist anywhere else.
W. Two barrels of one color side by side. How wide a stripe is against three references: the barrel width its row
   gives, the width of a barrel as tall as the body seen above and below it (the 2026-11-19 ``stripe_two`` reference),
   and the stripe's own height (a stripe is a fixed number of times as wide as it is tall). For barrels standing
   alone, and for the joined stripe of the scorecard's "same color beside" scenes. And the three scenes where
   ``stripe_two`` cut one barrel in two: why.
K. The cap rule's height floor. For "a barrel straight in front": how tall the top is that shows, as a share of an
   upper body; and what a lower floor would box, everywhere.
S. A narrow stripe piece beside a found nearer barrel ("same color beside and lower", three quarters hidden): is it
   seen from top to bottom, is exactly one side next to a found nearer barrel; and how many such pieces exist elsewhere.
F. Same color straight in front, half hidden: the scenes not found, one by one.

    python barrels/experiments/2026-11-20_occl_vertical/census_blob.py --rec <path to data/recordings>
Output: results/2026-11-20_occl_vertical/census_blob.md; sheets/census_blob_*.png (ignored).
"""
from __future__ import annotations

import argparse
import collections
import dataclasses
import math

import cv2
import numpy as np

import common
import census_half as ch
from barrels import detect_types as dtp, detector as det, geometry as geo, io, occlude as oc
from barrels.io import BLUE, ORANGE

CAM = geo.AIM_4A8B6118_BOXFIT
CFG = common.vert_arms.BASE
FLOORS = (0.5, 0.4, 0.3, 0.25)


def q(v, fmt="{:.2f}") -> str:
    v = np.asarray(v, float)
    if len(v) == 0:
        return "-"
    return f"{fmt.format(np.median(v))} ({fmt.format(v.min())} to {fmt.format(v.max())}; 10th to 90th pct {fmt.format(np.percentile(v, 10))} to {fmt.format(np.percentile(v, 90))})"


# ---------------------------------------------------------------- stripe pieces, as the finder sees them

def pieces(mask: np.ndarray, cfg: det.DetConfig = CFG) -> list[dict]:
    """Every connected piece of sandwiched stripe color (as ``_find_stripes_cores`` forms them, before ``stripe_join``),
    with its numbers: size, the expected sizes at its row, the body seen above and below it, the body's span."""
    h, w = mask.shape
    rows_idx = np.arange(h)[:, None]
    reach = det._reach_by_row(CAM, h, cfg)[:, None]
    out = []
    for body in (ORANGE, BLUE):
        other = BLUE if body == ORANGE else ORANGE
        bm = det._closed(mask == body, cfg)
        om = det._closed(mask == other, cfg) & ~bm
        up = np.maximum.accumulate(np.where(bm, rows_idx, -10 ** 6), axis=0)
        dn = np.minimum.accumulate(np.where(bm, rows_idx, 10 ** 6)[::-1], axis=0)[::-1]
        cand = om & ((rows_idx - up) <= reach) & ((dn - rows_idx) <= reach)
        n, lab, st, _ = cv2.connectedComponentsWithStats(cand.astype(np.uint8), connectivity=8)
        for i in range(1, n):
            x, y, bw, bh, area = (int(v) for v in st[i])
            ys = np.where(lab == i)[0]
            g = det._stripe_geometry(CAM, float(np.median(ys)) + 0.5)
            if g is None:
                continue
            rows = g[1]
            W, H, Hs = rows.width_px, rows.bottom - rows.top, rows.stripe_bottom - rows.stripe_top
            if W < cfg.min_width_px or Hs < cfg.min_stripe_px:
                continue
            core_h = float(np.percentile(ys, 90) - np.percentile(ys, 10) + 1)
            top_s, bottom_s = det._body_extent(mask, body, x, x + bw, y, y + bh)
            tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * H)
            span = det._body_span(mask, body, x, x + bw, max(0, top_s), min(h, bottom_s), y, y + bh) if bottom_s - top_s >= 2 else None
            out.append({"body": body, "bbox": (x, y, x + bw, y + bh), "area": area, "center": float(np.median(ys)) + 0.5, "W": W, "H": H, "Hs": Hs,
                        "core_h": core_h, "top_s": top_s, "bottom_s": bottom_s, "rows": rows, "tol": tol,
                        "full_slice": abs(top_s - rows.top) <= tol and abs(bottom_s - rows.bottom) <= tol,
                        "span": (min(span[0], x), max(span[1], x + bw)) if span else (x, x + bw),
                        "h_ok": cfg.stripe_h_min * Hs <= core_h <= cfg.stripe_h_max * Hs,
                        "narrow": bw < Hs or bw < core_h})                # under the finder's floor (one stripe height wide, not taller than wide)
    return out


def wide_stripes(ps: list[dict], cfg: det.DetConfig = CFG) -> list[dict]:
    """Stripe pieces wider than a barrel can be: wider than body_width x the larger of the width the stripe's row gives and
    the width of a barrel as tall as the body seen above and below the stripe. Asked only where body IS seen right above
    and right below the stripe (else nothing but the row says how big the barrel is)."""
    out = []
    for p in ps:
        x0, y0, x1, y1 = p["bbox"]
        if not p["h_ok"] or p["area"] < cfg.min_area_px or not (p["top_s"] < y0 and p["bottom_s"] > y1):
            continue
        ref = max(p["W"], (p["bottom_s"] - p["top_s"]) * p["W"] / p["H"])
        if x1 - x0 > max(cfg.body_width, 1.0) * ref:
            out.append({"kind": "wide stripe", "body": p["body"], "box": (x0, p["top_s"], x1, p["bottom_s"]), "stripe": p["bbox"], "ratio": (x1 - x0) / ref})
    return out


def holds(stripe, truths: list, color: int) -> int:
    """How many true barrels of this body color a stripe region lies on: their box holds the stripe's middle row and shares
    at least 0.3 of its own width with the stripe's columns."""
    row = (stripe[1] + stripe[3]) / 2
    return sum(1 for c, b in truths if c == color and b[1] <= row < b[3] and min(b[2], stripe[2]) - max(b[0], stripe[0]) >= 0.3 * (b[2] - b[0]))


def post_pairs(ps: list[dict], cfg: det.DetConfig = CFG, full: bool = True) -> list[dict]:
    """Two pieces of one body color, each under stripe_w_min of a barrel wide (alone such a piece gives no box), at the
    same rows, outer edges one barrel apart; ``full``: each also a full slice (its body ends where its row predicts the
    top and the bottom)."""
    ok = [p for p in ps if p["bbox"][2] - p["bbox"][0] < cfg.stripe_w_min * p["W"] and p["h_ok"] and p["area"] >= cfg.min_area_px
          and (p["full_slice"] or not full)]
    out = []
    for i, a in enumerate(ok):
        for b in ok[i + 1:]:
            if a["body"] != b["body"]:
                continue
            l, r = (a, b) if a["bbox"][0] <= b["bbox"][0] else (b, a)
            shared = min(l["bbox"][3], r["bbox"][3]) - max(l["bbox"][1], r["bbox"][1])
            if 2 * shared < min(l["bbox"][3] - l["bbox"][1], r["bbox"][3] - r["bbox"][1]):
                continue
            W = (l["W"] + r["W"]) / 2
            x0, x1 = l["span"][0], r["span"][1]
            if not (cfg.stripe_full * W <= x1 - x0 <= max(cfg.body_width, 1.0) * W) or r["bbox"][0] <= l["bbox"][2]:
                continue
            out.append({"kind": "post pair" if full else "post pair, slices not checked", "body": l["body"],
                        "box": (x0, min(l["top_s"], r["top_s"]), x1, max(l["bottom_s"], r["bottom_s"])), "span_ratio": (x1 - x0) / W})
    return out


def behind_slices(ps: list[dict], found: list, mask: np.ndarray, cfg: det.DetConfig = CFG) -> list[dict]:
    """A narrow piece that is a full slice, with exactly one side next to a found barrel standing nearer (that barrel's box
    holds one of the close_px pixels beside the seen span at the piece's middle row, and its bottom is lower than the
    bottom the piece's row predicts) or at the frame edge: a barrel wide from the seen edge of the other side."""
    h, w = mask.shape
    out = []
    for p in ps:
        if not (p["narrow"] and p["h_ok"] and p["area"] >= cfg.min_area_px and p["full_slice"]):
            continue
        sx0, sx1 = p["span"]
        if sx1 - sx0 > cfg.body_width * p["W"]:
            sx0, sx1 = p["bbox"][0], p["bbox"][2]
        row = int(p["center"])

        def nearer(pixels) -> bool:
            return any(b.bbox[3] > p["rows"].bottom and b.bbox[1] <= row < b.bbox[3] and any(b.bbox[0] <= px < b.bbox[2] for px in pixels) for b in found)
        left = sx0 <= 0 or nearer(range(sx0 - cfg.close_px, sx0))
        right = sx1 >= w or nearer(range(sx1, sx1 + cfg.close_px))
        if left == right:
            continue
        Wi = int(round(p["W"]))
        bx = (sx1 - Wi, sx1) if left else (sx0, sx0 + Wi)
        box = (max(0, bx[0]), max(0, p["top_s"]), min(w, bx[1]), min(h, p["bottom_s"]))
        if any(b.color == p["body"] and det.box_iou(b.bbox, box) > 0.5 for b in found):
            continue
        out.append({"kind": "slice behind", "body": p["body"], "box": box})
    return out


def caps_at(mask: np.ndarray, floor: float, cfg: det.DetConfig = CFG) -> list:
    """The detector's own boxes with the cap rule's height floor at ``floor`` x an upper body (the stripe step unchanged:
    ``caps_behind`` is called again on what the stripe step found, with only that number changed)."""
    seen = {}
    orig = det.caps_behind

    def spy(m, found, used, cam, c, log=None):
        seen["args"] = (list(found), list(used))
        return []
    det.caps_behind = spy
    try:
        det.detect(mask, cfg, CAM)
    finally:
        det.caps_behind = orig
    found, used = seen["args"]
    return found + det.caps_behind(mask, found, used, CAM, dataclasses.replace(cfg, height_min=floor))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rec", default=str(io.PKG_ROOT / "data" / "recordings"))
    args = ap.parse_args(argv)
    occ = common.scorecard()
    stems = occ.train_stems()
    segs = occ.segmentations(stems, with_extreme=True)
    pools, dropped = occ.build_sources(segs)
    sets = ch.frame_sets(segs, args.rec)
    out = common.OUT
    out.mkdir(parents=True, exist_ok=True)
    L = ["# Census 2: a post, a joined stripe, the cap's height floor, a slice beside a found barrel", "",
         "Measurements made before any rule was built (`experiments/2026-11-20_occl_vertical/census_blob.py`). Train frames only.", ""]
    scenes = [(pool, key, amount, variant, src, sc) for pool in occ.POOLS for key, amount, variant, src, sc in occ.scenes_of(pools[pool])
              if key in common.TARGET_ROWS]

    def gt(sc):
        return dtp.Barrel(color=sc.target[0], bbox=tuple(sc.target[1]), source="gt")

    # ---------------------------------------------------------------- P
    L += ["## P. A post across the middle", "",
          "| hidden | scenes | narrow pieces on the barrel (median per scene) | piece width / stripe height | piece area, px | pieces of 20 px or more that are full slices | "
          "found today or boxed (v2) by a pair of full slices (boxes where no barrel is) | the same, slices not checked |", "|---|---|---|---|---|---|---|---|"]
    for amount in oc.AMOUNTS:
        ss = [s for s in scenes if s[1] == "post" and s[2] == amount]
        npieces, widths, areas, full, hit, fal = [], [], [], [0, 0], [0, 0], [0, 0]
        for pool, key, a, variant, src, sc in ss:
            ps = [p for p in pieces(sc.mask) if p["body"] == src.color and p["bbox"][2] - p["bbox"][0] < CFG.stripe_w_min * p["W"]]
            npieces.append(len(ps)); widths += [(p["bbox"][2] - p["bbox"][0]) / p["Hs"] for p in ps]; areas += [p["area"] for p in ps]
            big = [p for p in ps if p["area"] >= CFG.min_area_px and p["h_ok"]]
            full[0] += sum(p["full_slice"] for p in big); full[1] += len(big)
            today = det.detect(sc.mask, CFG, CAM)
            for k, fl in enumerate((True, False)):
                preds = today + [dtp.Barrel(color=c["body"], bbox=tuple(c["box"]), source="census") for c in post_pairs(pieces(sc.mask), full=fl)
                                 if not any(o.color == c["body"] and det.box_iou(o.bbox, c["box"]) > 0.5 for o in today)]
                hit[k] += int(occ.found_v2(preds, src.color, src.bbox)); fal[k] += len(preds) - len(occ.right_place(preds, [sc.target]))
        L.append(f"| {int(100 * amount)} % | {len(ss)} | {np.median(npieces):.0f} | {q(widths)} | {q(areas, '{:.0f}')} | {full[0]} of {full[1]} | "
                 f"{hit[0]} ({fal[0]}) | {hit[1]} ({fal[1]}) |")
    L.append("")

    # ---------------------------------------------------------------- W
    def stripe_refs(mask, color, box):
        """The widest kept stripe of this body color that touches ``box``: its width against the three references."""
        log: list = []
        det.detect(mask, CFG, CAM, log=log)
        best = None
        for p in pieces(mask):
            if p["body"] != color or not (min(p["bbox"][2], box[2]) > max(p["bbox"][0], box[0]) and min(p["bbox"][3], box[3]) > max(p["bbox"][1], box[1])):
                continue
            if best is None or p["bbox"][2] - p["bbox"][0] > best["bbox"][2] - best["bbox"][0]:
                best = p
        if best is None:
            return None
        bw = best["bbox"][2] - best["bbox"][0]
        seen_h = best["bottom_s"] - best["top_s"]
        return {"row": bw / best["W"], "tall": bw / max(best["W"], seen_h * best["W"] / best["H"]), "own": bw / (best["core_h"] * best["W"] / best["Hs"]),
                "body": (best["span"][1] - best["span"][0]) / best["W"]}
    alone = [r for pool in occ.POOLS for src in pools[pool] if (r := stripe_refs(oc.make_scene(src, "edge", 0.0).mask, src.color, src.bbox))]
    L += ["## W. How wide a stripe is, against three references", "",
          "`row` = the barrel width the stripe's row gives. `tall` = the larger of that and the width of a barrel as tall as the body seen above and "
          "below the stripe (`stripe_two`, 2026-11-19). `own` = the width of a barrel whose stripe is as tall as this one. Median (min to max; 10th to 90th percentile).", "",
          "| what | n | stripe / `row` | stripe / `tall` | stripe / `own` | body joined to the stripe / `row` |", "|---|---|---|---|---|---|",
          f"| a barrel standing alone | {len(alone)} | {q([r['row'] for r in alone])} | {q([r['tall'] for r in alone])} | {q([r['own'] for r in alone])} | {q([r['body'] for r in alone])} |"]
    for key in ("barrel_side/same", "barrel_low/same", "barrel_front/same", "barrel_front/other"):
        for amount in oc.AMOUNTS:
            rs = [r for pool, k, a, variant, src, sc in scenes if k == key and a == amount if (r := stripe_refs(sc.mask, src.color, src.bbox))]
            L.append(f"| {occ.ROW_NAME[key]}, {int(100 * amount)} % hidden: the widest stripe on the hidden barrel | {len(rs)} | {q([r['row'] for r in rs])} | "
                     f"{q([r['tall'] for r in rs])} | {q([r['own'] for r in rs])} | {q([r['body'] for r in rs])} |")
    L.append("")
    for name, items in sets[:3]:
        rs = []
        for frame, mask, img, truths in items:
            for g in truths:
                if not g.flags and (r := stripe_refs(mask, g.color, g.bbox)):
                    rs.append(r)
        L.append(f"- every unflagged labeled barrel of {name} ({len(rs)}; touching neighbours included): stripe / `row` {q([r['row'] for r in rs])}; "
                 f"/ `tall` {q([r['tall'] for r in rs])}; / `own` {q([r['own'] for r in rs])}")
    L.append("")
    two = dataclasses.replace(CFG, stripe_two=True)
    L += ["The three scenes where `stripe_two` (2026-11-19) cut one barrel in two (CAMPUS `plain_01`, the near barrel [498, 145, 603, 243]):", ""]
    for pool, key, amount, variant, src, sc in scenes:
        if "plain_01" in src.stem and tuple(src.bbox) == (498, 145, 603, 243) and (key, amount) in (("barrel_front/other", 0.5), ("barrel_front/same", 0.25), ("barrel_front/same", 0.5)):
            r = stripe_refs(sc.mask, src.color, src.bbox) or {"row": float("nan"), "tall": float("nan"), "own": float("nan")}
            L.append(f"- {key} at {int(100 * amount)} %: stripe / `row` {r['row']:.2f}, / `tall` {r['tall']:.2f}, / `own` {r['own']:.2f}; boxes today "
                     f"{[b.bbox for b in det.detect(sc.mask, CFG, CAM)]}; with `stripe_two` {[b.bbox for b in det.detect(sc.mask, two, CAM)]}; the front barrel is {sc.fronts[0][1]}")
    L.append("")

    # ---------------------------------------------------------------- K
    L += ["## K. The cap rule's height floor (today: half an upper body)", "",
          "For each scene with a barrel straight in front: the tallest piece the cap rule refuses for its height on the hidden barrel, as a share of the upper "
          "body its top row predicts; then how many hidden barrels are found (v2) with the floor at 0.5 (today), 0.4, 0.3, 0.25.", "",
          "| scenes | n | refused top / upper body | found at 0.5 | 0.4 | 0.3 | 0.25 | boxes where no barrel is at 0.5 / 0.4 / 0.3 / 0.25 |", "|---|---|---|---|---|---|---|---|"]
    for key in ("barrel_front/other", "barrel_front/same"):
        for amount in oc.AMOUNTS:
            ss = [s for s in scenes if s[1] == key and s[2] == amount]
            ratios, hits, false = [], collections.Counter(), collections.Counter()
            for pool, k, a, variant, src, sc in ss:
                log: list = []
                det.detect(sc.mask, CFG, CAM, log=log)
                rr = [(e["bbox"][3] - e["bbox"][1]) / e["expected_upper_h"] for e in log if e["stage"] == "cap" and e["why"] == "height" and e.get("body") == src.color
                      and e["bbox"][3] - e["bbox"][1] < e["expected_upper_h"] and attribution_touch(e["bbox"], src.bbox)]
                if rr:
                    ratios.append(max(rr))
                for f in FLOORS:
                    preds = caps_at(sc.mask, f)
                    hits[f] += int(occ.found_v2(preds, src.color, src.bbox))
                    false[f] += len(preds) - len(occ.right_place(preds, [sc.target] + list(sc.fronts)))
            L.append(f"| {occ.ROW_NAME[key]}, {int(100 * amount)} % | {len(ss)} | {q(ratios)} (n {len(ratios)}) | " + " | ".join(str(hits[f]) for f in FLOORS) +
                     " | " + " / ".join(str(false[f]) for f in FLOORS) + " |")
    L += ["", "The same change everywhere else: boxes that appear with the lower floor, by what they lie on.", "",
          "| data | floor 0.4 | floor 0.3 | floor 0.25 |", "|---|---|---|---|"]
    tiles = collections.defaultdict(list)
    extra = {"post pair": collections.Counter(), "post pair, slices not checked": collections.Counter(), "slice behind": collections.Counter(),
             "wide stripe": collections.Counter()}
    for name, items in sets:
        cnt = {f: collections.Counter() for f in FLOORS[1:]}
        for frame, mask, img, truths in items:
            base = det.detect(mask, CFG, CAM)
            for f in FLOORS[1:]:
                for b in caps_at(mask, f):
                    if not any(o.color == b.color and det.box_iou(o.bbox, b.bbox) > 0.5 for o in base):
                        where = ch.lies_on(b.bbox, truths, base)
                        cnt[f][where] += 1
                        if img is not None and f == 0.25 and len(tiles["cap floor " + name]) < 24:
                            tiles["cap floor " + name].append(ch.tile(img, mask, b.bbox, f"{frame[-24:]} cap"))
            ps = pieces(mask)
            for c in wide_stripes(ps):
                where = "not known (unlabeled)" if truths is None else (
                    {0: "NOT a barrel", 1: "ONE labeled barrel"}.get(holds(c["stripe"], [(g.color, g.bbox) for g in truths], c["body"]), "two or more labeled barrels"))
                extra["wide stripe"][(name, where)] += 1
                if img is not None and where != "two or more labeled barrels" and len(tiles["wide stripe " + name]) < 24:
                    tiles["wide stripe " + name].append(ch.tile(img, mask, c["box"], f"{frame[-24:]} wide {c['ratio']:.2f}"))
            for c in post_pairs(ps) + post_pairs(ps, full=False) + behind_slices(ps, base, mask):
                if any(o.color == c["body"] and det.box_iou(o.bbox, c["box"]) > 0.5 for o in base):
                    continue
                where = ch.lies_on(c["box"], truths, base)
                extra[c["kind"]][(name, where)] += 1
                if img is not None and len(tiles[c["kind"] + " " + name]) < 24:
                    tiles[c["kind"] + " " + name].append(ch.tile(img, mask, c["box"], f"{frame[-24:]} {c['kind']}"))
        L.append(f"| {name} | " + " | ".join("; ".join(f"{v} on {k}" for k, v in sorted(cnt[f].items())) or "0" for f in FLOORS[1:]) + " |")
    L.append("")

    # ---------------------------------------------------------------- P and S everywhere
    L += ["## W on the scorecard: stripes wider than a barrel can be (1.2 x the taller reference, body seen right above and below)", "",
          "Per cell: scenes with such a stripe; of those stripes, how many lie on two true barrels of that color (the hidden one and the one pasted "
          "in front) / on one only (it would be cut in two wrongly).", "", "| scenes | n | scenes with a wide stripe | on two barrels | on one only |", "|---|---|---|---|---|"]
    for key in common.TARGET_ROWS:
        for amount in oc.AMOUNTS:
            ss = [s for s in scenes if s[1] == key and s[2] == amount]
            n_sc = n2 = n1 = 0
            for pool, k, a, variant, src, sc in ss:
                ws = wide_stripes(pieces(sc.mask))
                n_sc += bool(ws)
                for c in ws:
                    m = holds(c["stripe"], [sc.target] + list(sc.fronts), c["body"])
                    n2 += m >= 2; n1 += m < 2
            L.append(f"| {occ.ROW_NAME[key]}, {int(100 * amount)} % | {len(ss)} | {n_sc} | {n2} | {n1} |")
    L.append("")
    for kind, title in (("wide stripe", "W, everywhere: stripes wider than a barrel can be"),
                        ("post pair, slices not checked", "P, everywhere, slices not checked: pairs of narrow pieces at the same rows one barrel apart, not already boxed"),
                        ("post pair", "P, everywhere: pairs of full slices one barrel apart, not already boxed"),
                        ("slice behind", "S, everywhere: a narrow full slice with exactly one side next to a found nearer barrel or the frame edge, not already boxed")):
        L += [f"## {title}", "", "| data | lies on | candidates |", "|---|---|---|"]
        L += [f"| {name} | {where} | {v} |" for (name, where), v in sorted(extra[kind].items())] or ["| (none anywhere) | | 0 |"]
        L.append("")

    # ---------------------------------------------------------------- S on the scorecard
    L += ["## S. A narrow piece beside a found nearer barrel, on the scorecard", "",
          "| scenes | n | found today | found with the slice rule | boxes where no barrel is: today / with it |", "|---|---|---|---|---|"]
    for key in ("barrel_low/same", "barrel_side/same"):
        for amount in oc.AMOUNTS:
            ss = [s for s in scenes if s[1] == key and s[2] == amount]
            a0 = a1 = f0 = f1 = 0
            for pool, k, a, variant, src, sc in ss:
                base = det.detect(sc.mask, CFG, CAM)
                more = base + [dtp.Barrel(color=c["body"], bbox=tuple(c["box"]), source="census") for c in behind_slices(pieces(sc.mask), base, sc.mask)]
                truths = [sc.target] + list(sc.fronts)
                a0 += int(occ.found_v2(base, src.color, src.bbox)); a1 += int(occ.found_v2(more, src.color, src.bbox))
                f0 += len(base) - len(occ.right_place(base, truths)); f1 += len(more) - len(occ.right_place(more, truths))
            L.append(f"| {occ.ROW_NAME[key]}, {int(100 * amount)} % | {len(ss)} | {a0} | {a1} | {f0} / {f1} |")
    L.append("")

    # ---------------------------------------------------------------- F
    L += ["## F. Same color straight in front, half hidden: the scenes not found, one by one", "",
          "| barrel | full box | front barrel | boxes drawn (color, box, how) | best overlap with the full box | bottom off by / allowed |", "|---|---|---|---|---|---|"]
    for pool, key, amount, variant, src, sc in scenes:
        if key != "barrel_front/same" or amount != 0.5:
            continue
        preds = det.detect(sc.mask, CFG, CAM)
        if occ.found_v2(preds, src.color, src.bbox):
            continue
        same = [p for p in preds if p.color == src.color]
        best = max(same, key=lambda p: det.box_iou(p.bbox, src.bbox), default=None)
        L.append(f"| {pool.split(' ')[0]} {src.stem.split('_', 3)[-1]} | {list(src.bbox)} | {list(sc.fronts[0][1])} | "
                 f"{'; '.join(f'{dtp.COLOR_NAMES[p.color]} {list(p.bbox)} {p.source}' for p in preds)} | "
                 f"{'-' if best is None else f'{det.box_iou(best.bbox, src.bbox):.2f}'} | {'-' if best is None else best.bbox[3] - src.bbox[3]} / {max(3.0, 0.1 * src.height):.1f} |")
    L.append("")
    (out / "census_blob.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    d = out / "sheets"
    d.mkdir(parents=True, exist_ok=True)
    for name, ts in tiles.items():
        while len(ts) % 4:
            ts.append(np.zeros_like(ts[0]))
        fn = name.replace(' ', '_').replace('/', '_').replace(',', '').replace('(', '').replace(')', '')
        cv2.imwrite(str(d / f"census_blob_{fn}.png"), np.vstack([np.hstack(ts[i:i + 4]) for i in range(0, len(ts), 4)]))
    return 0


def attribution_touch(a, b) -> bool:
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


if __name__ == "__main__":
    raise SystemExit(main())
