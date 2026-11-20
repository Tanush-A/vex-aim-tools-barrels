#!/usr/bin/env python3
"""Part 2, census: can an end of the seen part be told apart as the barrel's OWN side or a CUT side, by a coarser
reading than the corner cost of ``pin_outline``? Measurement only; nothing here decides anything by itself.

The reading. The stripe's row gives the distance, hence the rows where the barrel's top and bottom must be. At a
barrel's own side the body closes on the stripe: the top runs down and the bottom runs up, both, until they meet at
mid-height (the barrel is widest at its stripe). At a side cut by a straight edge the top and the bottom both stand
where the row predicts them, right up to the end. A slanted cut closes ONE of them. So for each end of the seen
columns, over the columns within ``zone`` x W of the end (at least 2):

    top_gap    = mean of (highest body pixel of the column - predicted top) / H     0 where the top stands
    bottom_gap = mean of (predicted bottom - lowest body pixel of the column) / H
    closed     = min(top_gap, bottom_gap)                       large only when BOTH have closed

(a column with no body color above the stripe has its top at the stripe; the body is looked for between the predicted
top less the edge tolerance and the stripe, and the same below; no walk, so a hole in the body does not close it.)

Scenes: the scorecard's own (``2026-11-19_det_occl``, loaded by path: 50 source barrels), every kind hidden from the
side, 25 / 50 / 75 %, and each source barrel unhidden (both ends its own). The end's true kind is known from how the
scene was made. For each scene the target's widest stripe piece and its seen columns are taken as the stripe step
takes them (``_partly_seen``: the body joined to the stripe; where that body is wider than a barrel can be, the
stripe's own end on the side where body and stripe end apart).

Train frames only (asserted in the loaded script).

    python barrels/experiments/2026-11-20_occl_sliver/census_ends.py
Outputs: results/2026-11-20_occl_sliver/ census_ends.md, census_ends.csv
"""
from __future__ import annotations

import collections
import csv
import sys
import types

import numpy as np

import sliver as S
from barrels import detect_types as dtp, detector as det, geometry as geo, occlude as oc

C, A = S.C, S.A
CAM = geo.AIM_4A8B6118_BOXFIT
ZONES = (0.05, 0.1)
KINDS = ("frame", "edge", "slant", "both", "block")
RULES = ((0.15, 0.05), (0.15, 0.1), (0.1, 0.05), (0.2, 0.05), (0.15, 0.15))        # (own >=, cut <=)


def overlaps(a, b) -> bool:
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def seen_piece(mask, color, tb, cfg):
    """(stripe, rows, sx0, sx1, full_slice, thin, trusted) of the target's widest stripe piece, as ``_partly_seen`` sees it."""
    h, w = mask.shape
    narrow: list = []
    stripes = det.find_stripes(mask, CAM, cfg, narrow=narrow)
    cands = [s for s in stripes if s.body == color and overlaps(s.bbox, tb)]
    cands += [s for s in narrow if s.body == color and overlaps(s.bbox, tb) and not any(s.bbox == o.bbox for o in cands)]
    if not cands:
        return None
    s = max(cands, key=lambda s: s.bbox[2] - s.bbox[0])
    g = det._stripe_geometry(CAM, s.center_row)
    if g is None:
        return None
    rows = g[1]
    W, H = rows.width_px, rows.bottom - rows.top
    x0, y0, x1, y1 = s.bbox
    top_s, bot_s = det._body_extent(mask, s.body, x0, x1, y0, y1)
    tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * H)
    top_inf, bot_inf = abs(top_s - rows.top) > tol, abs(bot_s - rows.bottom) > tol
    top, bottom = (int(round(rows.top)) if top_inf else top_s), (int(round(rows.bottom)) if bot_inf else bot_s)
    span = det._body_span(mask, s.body, x0, x1, max(0, top), min(h, bottom), y0, y1) if bottom - top >= 2 else None
    trusted = span is not None and max(span[1], x1) - min(span[0], x0) <= cfg.body_width * W
    sx0, sx1 = (min(span[0], x0), max(span[1], x1)) if trusted else (x0, x1)
    if span is not None and not trusted:
        tolw = max(cfg.bottom_tol_min_px, cfg.bottom_tol * W)
        sx0 = x0 if abs(span[0] - x0) > tolw else min(span[0], x0)
        sx1 = x1 if abs(span[1] - x1) > tolw else max(span[1], x1)
    return s, rows, sx0, sx1, not (top_inf or bot_inf), bool(s.small or s.narrow), trusted


def end_gaps(mask, s, rows, sx0, sx1, cfg, zone: float):
    """((top_gap, bottom_gap) of the left end, the same of the right end), in barrel heights."""
    h = mask.shape[0]
    W, H = rows.width_px, rows.bottom - rows.top
    tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * H)
    x0, y0, x1, y1 = s.bbox
    lim_top, lim_bot = max(0, int(rows.top - tol)), min(h, int(rows.bottom + tol) + 1)
    n = max(2, int(round(zone * W)))
    out = []
    for cols in (range(sx0, min(sx1, sx0 + n)), range(max(sx0, sx1 - n), sx1)):
        tg, bg = [], []
        for x in cols:
            up = np.flatnonzero(mask[lim_top:y0, x] == s.body)
            dn = np.flatnonzero(mask[y1:lim_bot, x] == s.body)
            tg.append(((lim_top + up[0]) if len(up) else y0) - rows.top)
            bg.append(rows.bottom - ((y1 + dn[-1] + 1) if len(dn) else y1))
        out.append((float(np.mean(tg)) / H, float(np.mean(bg)) / H))
    return out[0], out[1]


def true_kinds(kind: str, variant: str, amount: float):
    """(kind of the left end, kind of the right end) as the scene was made."""
    if amount == 0:
        return "own", "own"
    if kind == "both":
        return "cut straight", "cut straight"
    cut = {"frame": "frame edge", "edge": "cut straight", "slant": "cut slanted", "block": "block"}[kind]
    return (cut, "own") if variant[0] == "L" else ("own", cut)


def main(argv=None) -> int:
    S.register()
    cfg = A.rule_config(A.ARMS["start"])
    sys.path.insert(0, str(C.OCCL))
    R = C.load("det_occl_run", C.OCCL / "run.py")
    R.occl_arms = types.SimpleNamespace(ARMS={"start": A.ARMS["start"]}, BASE=A.SOURCE_BASE)
    A.install()
    segs = R.segmentations(R.train_stems())
    pools, _ = R.build_sources(segs)
    rows_out = []
    n_scenes = collections.Counter()
    for pool in R.POOLS:
        scenes = [("unhidden", 0.0, "", src, oc.make_scene(src, "edge", 0.0)) for src in pools[pool]]
        scenes += [t for t in R.scenes_of(pools[pool]) if t[0].split("/")[0] in KINDS]
        for si, (key, amount, variant, src, sc) in enumerate(scenes):
            kind = key.split("/")[0]
            color, tb = sc.target
            n_scenes[(key, amount)] += 1
            p = seen_piece(sc.mask, color, tb, cfg)
            if p is None:
                continue
            s, rows, sx0, sx1, full, thin, trusted = p
            W, H = rows.width_px, rows.bottom - rows.top
            kl, kr = ("own", "own") if key == "unhidden" else true_kinds(kind, variant, amount)
            costs = det._end_costs(s, sc.mask, CAM, cfg, sx0, sx1) or (float("nan"), float("nan"))
            base = {"scene": f"{pool}#{si}", "pool": pool, "row": key, "amount": amount, "variant": variant, "stem": src.stem.replace("4A8B_", ""),
                    "color": dtp.COLOR_NAMES[color], "piece": list(s.bbox), "seen": [sx0, sx1], "seen_w": round((sx1 - sx0) / W, 3),
                    "piece_w": round((s.bbox[2] - s.bbox[0]) / W, 3), "W": round(W, 1), "H": round(H, 1), "full_slice": int(full), "thin": int(thin),
                    "trusted": int(trusted), "truth": list(tb), "at_frame_left": int(sx0 <= 0), "at_frame_right": int(sx1 >= sc.mask.shape[1])}
            for side, k, cost in (("left", kl, costs[0]), ("right", kr, costs[1])):
                r = dict(base, end=side, end_kind=k, corner_cost=round(cost, 4))
                for z in ZONES:
                    gl, gr = end_gaps(sc.mask, s, rows, sx0, sx1, cfg, z)
                    tg, bg = gl if side == "left" else gr
                    r[f"top_gap_{z}"], r[f"bottom_gap_{z}"] = round(tg, 4), round(bg, 4)
                rows_out.append(r)
    fields = list(dict.fromkeys(k for r in rows_out for k in r))
    S.OUT.mkdir(parents=True, exist_ok=True)
    with (S.OUT / "census_ends.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, restval=""); w.writeheader(); w.writerows(rows_out)

    def pct(v, q):
        return float(np.percentile(v, q)) if len(v) else float("nan")

    L = ["# Own side or cut side? The body closing on the stripe at each end of the seen part (a census; no acceptance number)", "",
         "Scorecard scenes hidden from the side (frame edge, straight edge, slanted edge, both sides, a block of the body color or of the stripe color), "
         "25 / 50 / 75 %, and every source barrel unhidden. `closed` = min(top gap, bottom gap) over the columns within `zone` x W of the end, in barrel "
         "heights: how far BOTH the top and the bottom are from where the stripe's row predicts them. Median (5th to 95th percentile; lowest; highest).", "",
         "| zone | end | pool | closed | n | at most 0.05 | 0.05 to 0.1 | 0.1 to 0.15 | 0.15 to 0.2 | over 0.2 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for z in ZONES:
        for k in ("own", "cut straight", "cut slanted", "frame edge", "block"):
            for grp, pred in (("hand masks", lambda r: "hand" in r["pool"]), ("color model", lambda r: "hand" not in r["pool"])):
                v = np.array([min(r[f"top_gap_{z}"], r[f"bottom_gap_{z}"]) for r in rows_out if r["end_kind"] == k and pred(r)])
                if not len(v):
                    continue
                bins = [int((v <= 0.05).sum()), int(((v > 0.05) & (v <= 0.1)).sum()), int(((v > 0.1) & (v <= 0.15)).sum()),
                        int(((v > 0.15) & (v <= 0.2)).sum()), int((v > 0.2).sum())]
                L.append(f"| {z} W | {k} | {grp} | {np.median(v):.3f} ({pct(v, 5):.3f} to {pct(v, 95):.3f}; {v.min():.3f}; {v.max():.3f}) | {len(v)} | "
                         + " | ".join(str(b) for b in bins) + " |")
    L += ["", "## The rule \"one end has closed, the other stands\": per cell", "",
          "An end is OWN when closed >= `own`; it is CUT when closed <= `cut`. The rule speaks when one end is OWN and the other is CUT; the box is W wide "
          "from the OWN end. Asked of the scenes with less than 0.8 W seen (wider: the seen width is the box already). Each cell: **speaks / of those "
          "wrong (the OWN end is not the barrel's own side) / both ends CUT / both ends OWN / scenes with a stripe piece and less than 0.8 W seen / all scenes**.", ""]
    scenes = collections.defaultdict(dict)
    for r in rows_out:
        scenes[r["scene"]][r["end"]] = r
    for z in ZONES:
        for own, cut in RULES:
            L += [f"### zone {z} W, own >= {own}, cut <= {cut}", "", "| what hides the barrel | 25 % | 50 % | 75 % | 75 %, thin full slices only |", "|---|---|---|---|---|"]
            table = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
            for e in scenes.values():
                l, r = e["left"], e["right"]
                if l["seen_w"] >= 0.8 or l["row"] == "unhidden":
                    continue
                cl = min(l[f"top_gap_{z}"], l[f"bottom_gap_{z}"]); cr = min(r[f"top_gap_{z}"], r[f"bottom_gap_{z}"])
                keys = [(l["row"], l["amount"])] + ([(l["row"], "thin")] if l["amount"] == 0.75 and l["thin"] and l["full_slice"] else [])
                pick = "left" if (cl >= own and cr <= cut) else ("right" if (cr >= own and cl <= cut) else "")
                for kk in keys:
                    t = table[kk]
                    t[4] += 1
                    if pick:
                        t[0] += 1; t[1] += e[pick]["end_kind"] != "own"
                    t[2] += cl <= cut and cr <= cut
                    t[3] += cl >= own and cr >= own
            for row in dict.fromkeys(k[0] for k in table):
                def txt(a):
                    if (row, a) not in table:
                        return "-"
                    t = table[(row, a)]
                    return f"{t[0]} / {t[1]} / {t[2]} / {t[3]} / {t[4]}" + (f" / {n_scenes[(row, a)]}" if a != "thin" else "")
                L.append(f"| {row} | " + " | ".join(txt(a) for a in (0.25, 0.5, 0.75, "thin")) + " |")
            L.append("")
    (S.OUT / "census_ends.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:75]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
