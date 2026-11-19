#!/usr/bin/env python3
"""Census, before any rule is built (measurements only; nothing here is part of the detector).

Part A, the readings on barrels that stand free (the 50 source barrels of the occlusion scorecard, each alone on an
empty mask): where the two seams of the stripe are, and how well each seam alone predicts the rest of the barrel:
the top row, the bottom row, the width, the height of the upper and of the lower body.

Part B, "a stripe with body color on ONE side only" as a candidate, counted everywhere: every connected band of one
barrel color that has the other barrel color right above it or right below it but not both, with the numbers a rule
could ask for, as a funnel (how many are left after each test), split by what the candidate lies on: a labeled barrel
the detector finds today, a labeled barrel it misses, or something that is not a barrel. Data: the train frames
(HOME hand masks, HOME as in the eval table, CAMPUS; BLACK and WOOD report only), the HOME hand masks with medium and
heavy damage (5 seeds), the recordings (unlabeled: every candidate is "not known"), and the scorecard's scenes hidden
from above and from below at 25 to 75 %.

Part C, a top alone and a base alone (no stripe at all), counted the same way: a piece of one color, a barrel wide for
its top row and no taller than an upper body (or: a barrel wide for its bottom row and no taller than a lower body).

Train frames only; a test frame is never opened (asserted in the loaded harness).

    python barrels/experiments/2026-11-20_occl_vertical/census_half.py --rec <path to data/recordings>
Output: results/2026-11-20_occl_vertical/census_half.md, census_half.csv; sheets/census_half_*.png (ignored).
"""
from __future__ import annotations

import argparse
import collections
import csv
import math
from pathlib import Path

import cv2
import numpy as np

import common
from barrels import degrade as dg, detect_types as dtp, detector as det, geometry as geo, io, occlude as oc, pipeline as pl, splits
from barrels import worldmap_bridge as wb
from barrels.io import BLUE, ORANGE

CAM = geo.AIM_4A8B6118_BOXFIT
CFG = common.vert_arms.BASE
Z_STRIPE_TOP = geo.BARREL_HEIGHT_MM / 2 + geo.STRIPE_HEIGHT_MM / 2          # 15 mm
Z_STRIPE_BOTTOM = geo.BARREL_HEIGHT_MM / 2 - geo.STRIPE_HEIGHT_MM / 2       # 9 mm
BULGE_R = geo.BARREL_BULGE_DIAMETER_MM / 2
EXTRA_AMOUNTS = (0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.75)
STAGES = ("one side only", "not taller than a stripe", "whole width (0.8 to 1.2 W)",
          "body's far edge where the seam predicts", "body a barrel wide (0.8 to 1.2 W)", "open side clear of barrel color",
          "body's far edge not against barrel color", "not inside a found box")


def rows_from_seam(seam: float, z_mm: float):
    d = CAM._d_axis_from_point_row(seam, z_mm, -BULGE_R)
    if not math.isfinite(d) or d <= BULGE_R + 1:
        return None
    return CAM.barrel_rows(d)


# ---------------------------------------------------------------- part B: the candidates

def half_bands(mask: np.ndarray, found: list, cfg: det.DetConfig = CFG) -> list[dict]:
    """Every band of one barrel color with the other color (the body) on one side only, with its numbers and the
    list of tests it passes (``STAGES``, in order; ``n_pass`` = how many in a row from the first)."""
    h, w = mask.shape
    rows_idx = np.arange(h)[:, None]
    reach = det._reach_by_row(CAM, h, cfg)[:, None]
    barrel = np.isin(mask, (ORANGE, BLUE))
    inside = np.zeros(mask.shape, bool)
    for b in found:
        inside[b.bbox[1]:b.bbox[3], b.bbox[0]:b.bbox[2]] = True
    out = []
    for body in (ORANGE, BLUE):
        other = BLUE if body == ORANGE else ORANGE
        bm = det._closed(mask == body, cfg)
        om = det._closed(mask == other, cfg) & ~bm
        up = np.maximum.accumulate(np.where(bm, rows_idx, -10 ** 6), axis=0)
        dn = np.minimum.accumulate(np.where(bm, rows_idx, 10 ** 6)[::-1], axis=0)[::-1]
        above, below = (rows_idx - up) <= reach, (dn - rows_idx) <= reach
        n, lab, st, _ = cv2.connectedComponentsWithStats(om.astype(np.uint8), connectivity=8)
        for i in range(1, n):
            x, y, bw, bh, area = (int(v) for v in st[i])
            if area < cfg.min_area_px:
                continue
            sel = lab == i
            cols = np.flatnonzero(sel.any(axis=0))
            fa = float((sel & above).any(axis=0)[cols].mean())
            fb = float((sel & below).any(axis=0)[cols].mean())
            if fb >= cfg.stripe_full and fa <= 1 - cfg.stripe_full:
                kind = "top hidden"            # the stripe with the lower body under it
            elif fa >= cfg.stripe_full and fb <= 1 - cfg.stripe_full:
                kind = "bottom hidden"         # the upper body with the stripe under it
            else:
                continue
            first = np.argmax(sel[:, cols], axis=0)                                   # first band row per column
            last = h - 1 - np.argmax(sel[::-1][:, cols], axis=0)                       # last band row per column
            if kind == "top hidden":
                seams = dn[last, cols]; seams = seams[seams < 10 ** 5]
                seam = float(np.median(seams))                                         # first body row under the band
                rows = rows_from_seam(seam, Z_STRIPE_BOTTOM)
            else:
                seams = up[first, cols]; seams = seams[seams > -10 ** 5]
                seam = float(np.median(seams)) + 1                                     # one past the last body row above the band
                rows = rows_from_seam(seam, Z_STRIPE_TOP)
            if rows is None:
                continue
            W, H, Hs = rows.width_px, rows.bottom - rows.top, rows.stripe_bottom - rows.stripe_top
            if W < cfg.min_width_px or Hs < cfg.min_stripe_px:
                continue
            ys = np.where(sel)[0]
            core_h = float(np.percentile(ys, 90) - np.percentile(ys, 10) + 1)
            tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * H)
            top_s, bottom_s = det._body_extent(mask, body, x, x + bw, y, y + bh)
            if kind == "top hidden":
                err = bottom_s - rows.bottom
                edge_ok = abs(err) <= tol and bottom_s < h
                r0, r1 = y, bottom_s
                open_rows = [(max(0, f - 4), f) for f in first]
                box_rows = (max(0, int(round(rows.top))), bottom_s)
            else:
                err = top_s - rows.top
                edge_ok = abs(err) <= tol and top_s > 0
                r0, r1 = top_s, y + bh
                open_rows = [(l + 1, min(h, l + 5)) for l in last]
                box_rows = (top_s, min(h, int(round(rows.bottom))))
            span = det._body_span(mask, body, x, x + bw, r0, r1, y, y + bh) if r1 - r0 >= 2 else None
            sx0, sx1 = (min(span[0], x), max(span[1], x + bw)) if span else (x, x + bw)
            blocked = float(np.mean([barrel[a:b, c].any() for (a, b), c in zip(open_rows, cols)]))
            far = barrel[bottom_s:min(h, bottom_s + 4), x:x + bw] if kind == "top hidden" else barrel[max(0, top_s - 4):max(0, top_s), x:x + bw]
            far_against = far.size > 0 and float(far.any(axis=0).mean()) >= 0.5      # the body's far edge ends against barrel color
            tests = [True, core_h <= cfg.stripe_h_max * Hs,
                     cfg.stripe_full * W <= bw <= max(cfg.body_width, 1.0) * W, bool(edge_ok),
                     span is not None and cfg.stripe_full * W <= sx1 - sx0 <= max(cfg.body_width, 1.0) * W, blocked < 0.5,
                     not far_against, 2 * int((sel & inside).sum()) < area]
            out.append({"kind": kind, "body": body, "band": (x, y, x + bw, y + bh), "area": area, "seam": seam, "W": W, "H": H, "Hs": Hs,
                        "floor_ok": core_h >= cfg.stripe_h_min * Hs,
                        "h_ratio": core_h / Hs, "w_ratio": bw / W, "edge_err": float(err), "tol": tol, "span_ratio": (sx1 - sx0) / W,
                        "blocked": blocked, "tests": tests, "box": (sx0, box_rows[0], sx1, box_rows[1])})
    return out


def passes(c: dict, floor: bool) -> bool:
    """All tests; ``floor`` = also at least 0.45 of a stripe tall (else any band of min_area_px counts)."""
    return all(c["tests"]) and (c["floor_ok"] or not floor)


def lone_pieces(mask: np.ndarray, found: list, cfg: det.DetConfig = CFG) -> list[dict]:
    """Part C: one-color pieces that are a barrel wide for their top row and no taller than an upper body ("top alone"),
    or a barrel wide for their bottom row and no taller than a lower body ("base alone"); not inside a found box."""
    h, w = mask.shape
    out = []
    for c in (ORANGE, BLUE):
        n, lab, st, _ = cv2.connectedComponentsWithStats(det._closed(mask == c, cfg).astype(np.uint8), connectivity=8)
        for i in range(1, n):
            x, y, bw, bh, area = (int(v) for v in st[i])
            if area < cfg.min_area_px or y <= 0 or y + bh >= h:
                continue
            cx, cy = x + bw / 2, y + bh / 2
            if any(b.bbox[0] <= cx < b.bbox[2] and b.bbox[1] <= cy < b.bbox[3] for b in found):
                continue
            d = CAM._d_axis_from_point_row(y, geo.BARREL_HEIGHT_MM, +geo.BARREL_END_DIAMETER_MM / 2)
            if math.isfinite(d) and d > BULGE_R + 1:
                r = CAM.barrel_rows(d)
                W, H, upper = r.width_px, r.bottom - r.top, r.stripe_top - r.top
                tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * H)
                if W >= cfg.min_width_px and cfg.stripe_full * W <= bw <= cfg.body_width * W and cfg.height_min * upper <= bh <= upper + tol:
                    out.append({"kind": "top alone", "body": c, "box": (x, y, x + bw, int(round(r.bottom)))})
            d = CAM.d_axis_from_bottom_row(y + bh)
            if math.isfinite(d) and d > BULGE_R + 1:
                r = CAM.barrel_rows(d)
                W, H, lower = r.width_px, r.bottom - r.top, r.bottom - r.stripe_bottom
                tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * H)
                if W >= cfg.min_width_px and cfg.stripe_full * W <= bw <= cfg.body_width * W and cfg.height_min * lower <= bh <= lower + tol:
                    out.append({"kind": "base alone", "body": c, "box": (x, max(0, int(round(r.top))), x + bw, y + bh)})
    return out


def lies_on(box, truths: list | None, found: list) -> str:
    """What a candidate box lies on: a labeled barrel found today, a labeled barrel missed today, not a barrel; or
    'not known' on unlabeled frames."""
    if truths is None:
        return "not known (unlabeled)"
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    for g in truths:
        if g.bbox[0] <= cx < g.bbox[2] and g.bbox[1] <= cy < g.bbox[3]:
            hit = any(p.color == g.color and det.box_iou(p.bbox, g.bbox) >= 0.5 for p in found)
            return "a labeled barrel found today" if hit else "a labeled barrel missed today"
    return "NOT a barrel"


# ---------------------------------------------------------------- part A: free barrels

def parts_of(src: oc.Source) -> dict | None:
    """The seams and the edges of one free barrel, read off its own mask (the hidden-from-nowhere scene)."""
    sc = oc.make_scene(src, "edge", 0.0)
    m = sc.mask
    x0, y0, x1, y1 = src.bbox
    other = BLUE if src.color == ORANGE else ORANGE
    body, stripe = m == src.color, m == other
    cols = np.flatnonzero(stripe.any(axis=0))
    if len(cols) < 0.5 * (x1 - x0) or not body.any():
        return None
    first = np.argmax(stripe[:, cols], axis=0)
    last = m.shape[0] - 1 - np.argmax(stripe[::-1][:, cols], axis=0)
    s0, s1 = float(np.median(first)), float(np.median(last)) + 1               # stripe top row, one past its last row
    ys, xs = np.where(body)
    top, bottom = int(ys.min()), int(ys.max()) + 1
    up_cols, lo_cols = np.flatnonzero(body[:int(s0)].any(axis=0)), np.flatnonzero(body[int(s1):].any(axis=0))
    up_w = (up_cols.max() - up_cols.min() + 1) if len(up_cols) else 0
    lo_w = (lo_cols.max() - lo_cols.min() + 1) if len(lo_cols) else 0
    ra, rb = rows_from_seam(s0, Z_STRIPE_TOP), rows_from_seam(s1, Z_STRIPE_BOTTOM)
    rc = det._stripe_geometry(CAM, (s0 + s1) / 2)
    if ra is None or rb is None or rc is None:
        return None
    rc = rc[1]
    H = y1 - y0
    return {"stem": src.stem, "pool": src.pool, "H": H, "W": x1 - x0,
            # from the stripe's TOP seam alone (what is left when the barrel is hidden from below)
            "A_top_err": top - ra.top, "A_bottom_err": ra.bottom - y1, "A_w_ratio": up_w / ra.width_px,
            "A_upper_ratio": (s0 - top) / (ra.stripe_top - ra.top), "A_tol": max(CFG.bottom_tol_min_px, CFG.bottom_tol * (ra.bottom - ra.top)),
            # from the stripe's BOTTOM seam alone (what is left when it is hidden from above)
            "B_bottom_err": bottom - rb.bottom, "B_top_err": rb.top - y0, "B_w_ratio": lo_w / rb.width_px,
            "B_lower_ratio": (bottom - s1) / (rb.bottom - rb.stripe_bottom), "B_tol": max(CFG.bottom_tol_min_px, CFG.bottom_tol * (rb.bottom - rb.top)),
            # for comparison: the bottom from the stripe's middle row (what the detector uses today), and from the top row
            "C_bottom_err": rc.bottom - y1, "T_bottom_err": det.predicted_bottom(CAM, top) - y1,
            "v2_tol": max(3.0, 0.1 * H), "stripe_h_ratio": (s1 - s0) / (rc.stripe_bottom - rc.stripe_top)}


def stat(v) -> str:
    v = np.asarray(v, float)
    return f"{np.median(v):+.1f} ({np.percentile(v, 10):+.1f} to {np.percentile(v, 90):+.1f}; worst {v[np.argmax(np.abs(v))]:+.1f})"


def ratio(v) -> str:
    v = np.asarray(v, float)
    return f"{np.median(v):.2f} ({v.min():.2f} to {v.max():.2f})"


# ---------------------------------------------------------------- main

def tile(img: np.ndarray, mask: np.ndarray, box, label: str, size: int = 200) -> np.ndarray:
    pad = 30
    x0, y0, x1, y1 = max(0, box[0] - pad), max(0, box[1] - pad), min(mask.shape[1], box[2] + pad), min(mask.shape[0], box[3] + pad)
    seg = np.full((*mask.shape, 3), 45, np.uint8)
    seg[mask == ORANGE] = (0, 140, 255); seg[mask == BLUE] = (255, 120, 0)
    pair = []
    for src in (img, seg):
        t = src.copy()
        cv2.rectangle(t, (box[0], box[1]), (box[2] - 1, box[3] - 1), (0, 0, 255), 1)
        t = t[y0:y1, x0:x1]
        f = min(size / t.shape[1], size / t.shape[0])
        t = cv2.resize(t, None, fx=f, fy=f, interpolation=cv2.INTER_NEAREST)
        canvas = np.zeros((size, size, 3), np.uint8); canvas[:t.shape[0], :t.shape[1]] = t[:size, :size]
        pair.append(canvas)
    out = np.vstack([np.zeros((16, 2 * size, 3), np.uint8), np.hstack(pair)])
    cv2.putText(out, label, (3, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (255, 255, 255), 1)
    return out


def frame_sets(segs: dict, rec_path: str) -> list[tuple[str, list]]:
    """Every place a candidate is counted: (name, [(frame name, mask, image or None, labeled barrels or None)]). The train
    frames per set, the HOME hand masks with medium and heavy damage (5 seeds, as in ``2026-11-18_det_given_seg``), and
    the recordings per clip (unlabeled, segmented with the adopted color model)."""
    model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    test = set(splits.load_splits()["test"])
    sets: list[tuple[str, list]] = []
    for name, pool in (("HOME hand masks", "HOME hand masks"), ("HOME as in the eval table", "HOME color model"), ("CAMPUS", "CAMPUS color model"),
                       ("BLACK (report only)", "BLACK"), ("WOOD (report only)", "WOOD")):
        items = []
        for stem, mask in sorted(segs[pool].items()):
            assert stem not in test
            items.append((stem, mask, io.load_image(io.find_image(stem)), dtp.barrels_from_boxes(io.load_boxes(stem))))
        sets.append((name, items))
    home = sorted(segs["HOME hand masks"].items())
    for sev in ("medium", "heavy"):
        items = []
        for seed in range(5):
            for i, (stem, mask) in enumerate(home):
                gts = dtp.barrels_from_boxes(io.load_boxes(stem))
                items.append((f"{stem} seed{seed}", dg.damage(mask, [tuple(g.bbox) for g in gts], dg.SEVERITIES[sev], seed=1000 * seed + i), None, gts))
        sets.append((f"HOME hand masks, {sev} damage, 5 seeds", items))
    rec = Path(rec_path)
    clips = collections.defaultdict(list)
    for p in sorted(rec.rglob("*.png")):
        assert p.stem not in test
        img = cv2.imread(str(p))
        if img is not None and p.parent != rec:
            clips[f"{p.parent.parent.name}/{p.parent.name}"].append((f"{p.parent.name}/{p.stem}", pl.segment(pl.Frame.from_image(img), model)[0], img, None))
    return sets + [(f"recording {k}", v) for k, v in sorted(clips.items())]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rec", default=str(io.PKG_ROOT / "data" / "recordings"))
    args = ap.parse_args(argv)
    occ = common.scorecard()
    stems = occ.train_stems()
    segs = occ.segmentations(stems, with_extreme=True)
    pools, dropped = occ.build_sources(segs)
    out = common.OUT
    out.mkdir(parents=True, exist_ok=True)
    L = ["# Census: a stripe with body color on one side only; a top or a base alone", "",
         "Measurements made before any rule was built (`experiments/2026-11-20_occl_vertical/census_half.py`). Camera AIM_4A8B6118_BOXFIT; train frames only.", ""]

    # ---- part A
    parts = [p for pool in occ.POOLS for src in pools[pool] if (p := parts_of(src)) is not None]
    L += [f"## A. What one seam of the stripe says about the rest of the barrel ({len(parts)} free-standing barrels)", "",
          "Errors in px, median (10th to 90th percentile; worst). + = lower in the picture / larger.", "",
          "| reading | value |", "|---|---|",
          f"| stripe's TOP seam alone → the top row: seen top minus predicted | {stat([p['A_top_err'] for p in parts])} |",
          f"| ... inside the usual edge tolerance (15 % of the height, 4 px at least) | {sum(abs(p['A_top_err']) <= p['A_tol'] for p in parts)} of {len(parts)} |",
          f"| stripe's TOP seam alone → the bottom row: predicted minus hand-drawn | {stat([p['A_bottom_err'] for p in parts])} |",
          f"| ... inside the v2 bottom tolerance (10 % of the height, 3 px at least) | {sum(abs(p['A_bottom_err']) <= p['v2_tol'] for p in parts)} of {len(parts)} |",
          f"| upper body's width / the width that seam predicts | {ratio([p['A_w_ratio'] for p in parts])} |",
          f"| upper body's height / predicted | {ratio([p['A_upper_ratio'] for p in parts])} |",
          f"| stripe's BOTTOM seam alone → the bottom row: seen bottom minus predicted | {stat([p['B_bottom_err'] for p in parts])} |",
          f"| ... inside the usual edge tolerance | {sum(abs(p['B_bottom_err']) <= p['B_tol'] for p in parts)} of {len(parts)} |",
          f"| stripe's BOTTOM seam alone → the top row: predicted minus hand-drawn | {stat([p['B_top_err'] for p in parts])} |",
          f"| lower body's width / the width that seam predicts | {ratio([p['B_w_ratio'] for p in parts])} |",
          f"| lower body's height / predicted | {ratio([p['B_lower_ratio'] for p in parts])} |",
          f"| for comparison, the stripe's MIDDLE row (today's reading) → the bottom row: predicted minus hand-drawn | {stat([p['C_bottom_err'] for p in parts])} |",
          f"| ... inside the v2 bottom tolerance | {sum(abs(p['C_bottom_err']) <= p['v2_tol'] for p in parts)} of {len(parts)} |",
          f"| for comparison, the TOP ROW → the bottom row: predicted minus hand-drawn | {stat([p['T_bottom_err'] for p in parts])} |",
          f"| ... inside the v2 bottom tolerance | {sum(abs(p['T_bottom_err']) <= p['v2_tol'] for p in parts)} of {len(parts)} |",
          f"| stripe's height / predicted from its middle row | {ratio([p['stripe_h_ratio'] for p in parts])} |", ""]

    # ---- parts B and C on frames
    sets = frame_sets(segs, args.rec)

    funnel = collections.defaultdict(lambda: collections.Counter())    # (set, kind) -> stage index -> count ; plus finals by where
    finals = []
    lone = collections.Counter()
    tiles = collections.defaultdict(list)
    for name, items in sets:
        for frame, mask, img, truths in items:
            found = det.detect(mask, CFG, CAM)
            for c in half_bands(mask, found):
                ok = 0
                for t in c["tests"]:
                    if not t:
                        break
                    ok += 1
                for k in range(ok):
                    funnel[(name, c["kind"])][k] += 1
                if ok == len(STAGES) - 1 and img is not None and len(tiles["only the found box stops it " + name]) < 12:
                    tiles["only the found box stops it " + name].append(tile(img, mask, c["box"], f"{frame[-22:]} {c['kind']} {dtp.COLOR_NAMES[c['body']]}"))
                for floor in (True, False):
                    if passes(c, floor):
                        where = lies_on(c["box"], truths, found)
                        funnel[(name, c["kind"])][("final", floor, where)] += 1
                        if floor is False:
                            finals.append({"set": name, "frame": frame, "kind": c["kind"], "body": dtp.COLOR_NAMES[c["body"]], "box": list(c["box"]),
                                           "band": list(c["band"]), "h_ratio": round(c["h_ratio"], 2), "w_ratio": round(c["w_ratio"], 2),
                                           "edge_err": round(c["edge_err"], 1), "tol": round(c["tol"], 1), "span_ratio": round(c["span_ratio"], 2),
                                           "passes_height_floor": int(passes(c, True)), "lies_on": where})
                            if img is not None and len(tiles[name]) < 36:
                                tiles[name].append(tile(img, mask, c["box"], f"{frame[-22:]} {c['kind']} h{c['h_ratio']:.2f}"))
            for c in lone_pieces(mask, found):
                lone[(name, c["kind"], lies_on(c["box"], truths, found))] += 1
                if img is not None and len(tiles["lone " + name]) < 36:
                    tiles["lone " + name].append(tile(img, mask, c["box"], f"{frame[-22:]} {c['kind']}"))

    L += ["## B. A band with body color on one side only, counted everywhere", "",
          "`top hidden` = body color under the band only (the stripe and the lower body show). `bottom hidden` = body color above the band only "
          "(the upper body and the stripe show). The distance comes from the seam between band and body. Each column = how many candidates are "
          "left after that test and all before it (a band is any connected piece of 20 px or more). The last two: all tests, by what the candidate lies "
          "on; and the same when the band must also be at least 0.45 of a stripe tall.", "",
          "| data | kind | " + " | ".join(STAGES) + " | all tests, and 0.45 of a stripe tall | all tests, any band of 20 px |", "|---|---|" + "---|" * (len(STAGES) + 2)]
    for name, _ in sets:
        for kind in ("top hidden", "bottom hidden"):
            f = funnel[(name, kind)]

            def fin(floor):
                d = {k[2]: v for k, v in f.items() if isinstance(k, tuple) and k[1] is floor}
                return "; ".join(f"{v} on {k}" for k, v in sorted(d.items())) or "0"
            L.append(f"| {name} | {kind} | " + " | ".join(str(f[k]) for k in range(len(STAGES))) + f" | {fin(True)} | {fin(False)} |")
    L += ["", "Every candidate that passes all tests (without the height floor) is listed in `census_half.csv`.", ""]
    with (out / "census_half.csv").open("w", newline="") as fh:
        fields = ["set", "frame", "kind", "body", "box", "band", "h_ratio", "w_ratio", "edge_err", "tol", "span_ratio", "passes_height_floor", "lies_on"]
        wr = csv.DictWriter(fh, fieldnames=fields); wr.writeheader(); wr.writerows(finals)

    L += ["## C. A top alone, a base alone (no stripe): one-color pieces of the right size, outside the boxes found today", "",
          "| data | kind | lies on | pieces |", "|---|---|---|---|"]
    for (name, kind, where), v in sorted(lone.items()):
        L.append(f"| {name} | {kind} | {where} | {v} |")
    L.append("")

    # ---- the scorecard's scenes hidden from above and from below, at more amounts
    L += ["## What the candidates would give on the scorecard's scenes (a forecast, not the experiment)", "",
          "Each of the free-standing barrels hidden from above or from below by the stated share of its height; 'boxed' = a candidate passes all "
          "tests and its box is a hit under the v2 rule against the full box. Each cell: found today → found today or boxed by a candidate at least "
          "0.45 of a stripe tall → the same with any band of 20 px; then (boxes of the wrong color or place with any band).", "",
          "| hidden | from above | from below | n |", "|---|---|---|---|"]
    for amount in EXTRA_AMOUNTS:
        cnt = collections.Counter(); n = 0
        for pool in occ.POOLS:
            for src in pools[pool]:
                n += 1
                for kind in ("top", "bottom"):
                    sc = oc.make_scene(src, kind, amount)
                    today = det.detect(sc.mask, CFG, CAM)
                    cands = half_bands(sc.mask, today)
                    cnt[(kind, "today")] += int(occ.found_v2(today, src.color, src.bbox))
                    for floor in (True, False):
                        preds = today + [dtp.Barrel(color=c["body"], bbox=tuple(c["box"]), source="census") for c in cands if passes(c, floor)]
                        cnt[(kind, floor)] += int(occ.found_v2(preds, src.color, src.bbox))
                        if not floor:
                            cnt[(kind, "false")] += len(preds) - len(occ.right_place(preds, [sc.target]))
        L.append(f"| {int(round(100 * amount))} % | " + " | ".join(
            f"{cnt[(k, 'today')]} → {cnt[(k, True)]} → {cnt[(k, False)]} ({cnt[(k, 'false')]})" for k in ("top", "bottom")) + f" | {n} |")
    L.append("")
    (out / "census_half.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    d = out / "sheets"
    d.mkdir(parents=True, exist_ok=True)
    for name, ts in tiles.items():
        while len(ts) % 4:
            ts.append(np.zeros_like(ts[0]))
        cv2.imwrite(str(d / f"census_half_{name.replace(' ', '_').replace('/', '_').replace(',', '').replace('(', '').replace(')', '')}.png"),
                    np.vstack([np.hstack(ts[i:i + 4]) for i in range(0, len(ts), 4)]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
