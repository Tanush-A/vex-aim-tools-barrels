#!/usr/bin/env python3
"""Census, before any detector change: does an own end bulge OUTWARD and an end cut by a round barrel in front bulge
INWARD, measurably, on the class mask? Measurement only; no acceptance number is decided here.

Why: ``own_close`` (A8, off) calls an end of a thin seen slice the barrel's own side when the body has closed on the
stripe there (top and bottom both 0.15 H in over the last 0.05 W). It was right on every clean slice, but a barrel B
standing behind a barrel A ends along A's outline, and A is round: B's cut end closes in too. The user's idea: an own
end is convex (the rounded end of a capsule), an end cut by a round thing in front is concave seen from B (A's convex
outline intrudes). The measures are in ``convex.py`` (chord bulge of the top and of the bottom, hull deficiency, side
profile), at zones 0.1, 0.15 and 0.2 W.

Part A, every end (the scorecard's scenes): every partly seen stripe piece (seen narrower than 0.8 W, taken as
``census_ends_damaged.pieces`` takes them, with today's defaults, ``start``), both ends; the end's kind from the true
boxes, the target's AND the barrels' pasted in front, as in Part B, named by the scene's kind (own; cut straight /
slanted / frame / block; cut by a barrel of the other or the same color beside, beside and lower, straight in front).
A first version took the target's widest piece only: with a same-colored barrel in front that was often the FRONT
barrel's stripe, and its own end was labelled a cut one. Pools: HOME hand masks, HOME color model
(leave one scene out), CAMPUS color model.

Part B, every call ``own_close`` makes (arm ``close`` = ``start`` + ``own_close``; ``_closed_end`` is wrapped and
records, it changes nothing): the scorecard (3888 scenes), the real train frames as the eval table segments them
(HOME hand masks, HOME leave one scene out, CAMPUS), and the damage levels of the battery (16 HOME hand masks, seeds 0
to 19, every level). Each end's kind from the true boxes: ``own`` = within the edge tolerance of a side of the box of
its color holding the piece's centre; ``cut by barrel`` = not, and another true barrel's box holds the column just
beyond the end at the stripe's row; ``cut`` = not, and none does; ``no barrel`` = no box of its color holds the piece.
A call SPEAKS when ``own_close`` returns a box; it is RIGHT when the end it calls own is ``own``.

Train frames only (the loaded scripts assert it). No new frames of 2026-11-19 to 21 are used here (they are the
acceptance check).

    python barrels/experiments/2026-11-23_own_convex/census_convex.py [--seeds 20]
Outputs: results/2026-11-23_own_convex/ census.md, census_ends.csv, census_calls.csv
"""
from __future__ import annotations

import argparse
import collections
import csv
import dataclasses
import sys
import types

import numpy as np

import own_arms as O
import convex as V
from barrels import degrade as dg, detect_types as dtp, detector as det, geometry as geo, io, occlude as oc

C, A, S = O.C, O.A, O.S
CAM = geo.AIM_4A8B6118_BOXFIT
ZONES = (0.1, 0.15, 0.2)
MEASURES = ("chord", "chord_min", "chord_top", "chord_bot", "hull", "side")
PART_A_KINDS = ("frame", "edge", "slant", "both", "block", "barrel_side", "barrel_low", "barrel_front")
CUT_NAME = {"frame": "cut: frame edge", "edge": "cut: straight edge", "slant": "cut: slanted edge", "both": "cut: straight edge",
            "block": "cut: block"}


def a_kind(key: str, variant: str, amount: float):
    """(left, right) kinds of the target's ends as the scene was made."""
    if amount == 0 or key == "unhidden":
        return "own", "own"
    kind = key.split("/")[0]
    if kind == "both":
        return CUT_NAME["both"], CUT_NAME["both"]
    if kind == "barrel_front":
        return "own (front barrel below)", "own (front barrel below)"
    if kind in ("barrel_side", "barrel_low"):
        cut = f"cut by barrel: {key.split('/')[1]} color, {'beside' if kind == 'barrel_side' else 'beside and lower'}"
    else:
        cut = CUT_NAME[kind] + (f" ({key.split('/')[1]})" if kind == "block" else "")
    return (cut, "own") if variant[0] == "L" else ("own", cut)


def measures_of(mask, s, rows, sx0, sx1, cfg) -> dict:
    W, H = rows.width_px, rows.bottom - rows.top
    t, b = V.profiles(mask, s, rows, sx0, sx1, cfg)
    out = {}
    for side, left in (("left", True), ("right", False)):
        out[f"{side}_closed"] = round(V.closure(t, b, left, rows, W, H), 4)
        for z in ZONES:
            for k, v in V.end_measures(t, b, left, W, H, z).items():
                out[f"{side}_{k}_{z}"] = round(v, 4) if v == v else ""
    return out


def seen_edge(mask, s, sx0, sx1, cfg, left: bool) -> bool:
    """``own_close``'s round-2 test: the end is not against barrel color (the close_px columns beyond it, stripe rows)."""
    h, w = mask.shape
    y0, y1 = s.bbox[1], s.bbox[3]
    cols = [c for c in (range(sx0 - cfg.close_px, sx0) if left else range(sx1, sx1 + cfg.close_px)) if 0 <= c < w]
    barrel = np.isin(mask, (det.ORANGE, det.BLUE))
    return not cols or float(barrel[y0:y1, cols].any(axis=1).mean()) < 0.5


def box_kinds(s, sx0, sx1, W, truths, cfg):
    cx, cy = (s.bbox[0] + s.bbox[2]) / 2, (s.bbox[1] + s.bbox[3]) / 2
    best = None
    for c, b in truths:
        if c == s.body and b[0] <= cx < b[2] and b[1] <= cy < b[3]:
            if best is None or abs(cx - (b[0] + b[2]) / 2) < abs(cx - (best[0] + best[2]) / 2):
                best = b
    if best is None:
        return "no barrel", "no barrel"
    tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * W)
    row = int(s.center_row)

    def beyond(col) -> bool:
        return any(b is not best and b[0] <= col < b[2] and b[1] <= row < b[3] for _, b in truths)
    kl = "own" if abs(sx0 - best[0]) <= tol else ("cut by barrel" if beyond(sx0 - 2) else "cut")
    kr = "own" if abs(sx1 - best[2]) <= tol else ("cut by barrel" if beyond(sx1 + 1) else "cut")
    return kl, kr


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", type=int, default=20)
    args = ap.parse_args(argv)
    O.register()
    assert not O.check_start(), O.check_start()
    cfg_start = A.rule_config(A.ARMS["start"])
    cfg_close = A.rule_config(A.ARMS["close"])
    sys.path.insert(0, str(C.OCCL))
    R = C.load("det_occl_run", C.OCCL / "run.py")
    R.occl_arms = types.SimpleNamespace(ARMS={"start": A.ARMS["start"]}, BASE=A.SOURCE_BASE)
    E = C.load("census_ends_a8", O.SLIVER / "census_ends.py")
    A.install()
    segs = R.segmentations(R.train_stems())
    pools, _ = R.build_sources(segs)

    # ---------------- Part A: every partly seen piece of each scene; each end labelled by the true boxes (target AND pasted fronts)
    D = C.load("census_ends_damaged_a8", O.SLIVER / "census_ends_damaged.py")
    ends = []
    for pool in R.POOLS:
        scenes = [("unhidden", 0.0, "", src, oc.make_scene(src, "edge", 0.0)) for src in pools[pool]]
        scenes += [t for t in R.scenes_of(pools[pool]) if t[0].split("/")[0] in PART_A_KINDS]
        for si, (key, amount, variant, src, sc) in enumerate(scenes):
            truths = [sc.target] + list(sc.fronts)
            kind = key.split("/")[0]
            tc, tb = sc.target
            for s, rows, sx0, sx1, full, thin in D.pieces(sc.mask, cfg_start):
                W = rows.width_px
                kl, kr = box_kinds(s, sx0, sx1, W, truths, cfg_start)
                if kl == "no barrel":
                    continue
                cx, cy = (s.bbox[0] + s.bbox[2]) / 2, (s.bbox[1] + s.bbox[3]) / 2
                whose = "target" if (s.body == tc and tb[0] <= cx < tb[2] and tb[1] <= cy < tb[3]) else "front"

                def name(k):
                    if k == "own":
                        return "own" if whose == "target" else "own (a pasted front barrel's)"
                    if k == "cut by barrel":
                        return (f"cut by barrel: {key.split('/')[1]} color, "
                                + {"barrel_side": "beside", "barrel_low": "beside and lower", "barrel_front": "straight in front"}.get(kind, kind))
                    return CUT_NAME.get(kind, f"cut: {kind}") + (f" ({key.split('/')[1]})" if kind == "block" else "")
                m = measures_of(sc.mask, s, rows, sx0, sx1, cfg_start)
                for side, k in (("left", name(kl)), ("right", name(kr))):
                    r = {"pool": pool, "scene": f"{pool}#{si}", "row": key, "amount": amount, "variant": variant, "stem": src.stem.replace("4A8B_", ""),
                         "color": dtp.COLOR_NAMES[s.body], "whose": whose, "piece": list(s.bbox), "seen": [sx0, sx1],
                         "seen_w": round((sx1 - sx0) / W, 3), "W": round(W, 1), "full_slice": int(full), "thin": int(thin), "end": side, "kind": k,
                         "seen_edge": int(seen_edge(sc.mask, s, sx0, sx1, cfg_start, side == "left")),
                         "closed": m[f"{side}_closed"]}
                    for z in ZONES:
                        for k2 in MEASURES:
                            r[f"{k2}_{z}"] = m[f"{side}_{k2}_{z}"]
                    ends.append(r)

    # ---------------- Part B: every own_close call
    calls = []
    ctx: dict = {}
    orig = det._closed_end

    def spy(s, mask, cam, cfg, sx0, sx1):
        res = orig(s, mask, cam, cfg, sx0, sx1)
        g = det._stripe_geometry(cam, s.center_row)
        if g is None:
            return res
        rows = g[1]
        W = rows.width_px
        kl, kr = box_kinds(s, sx0, sx1, W, ctx["truths"], cfg)
        pick = "" if res is None else ("left" if res[0] == sx0 else "right")
        r = {"group": ctx["group"], "level": ctx["level"], "item": ctx["item"], "body": dtp.COLOR_NAMES[s.body], "piece": list(s.bbox),
             "seen": [sx0, sx1], "seen_w": round((sx1 - sx0) / W, 3), "W": round(W, 1), "small": int(s.small), "pick": pick,
             "left_kind": kl, "right_kind": kr, "left_seen_edge": int(seen_edge(mask, s, sx0, sx1, cfg, True)),
             "right_seen_edge": int(seen_edge(mask, s, sx0, sx1, cfg, False))}
        r.update(measures_of(mask, s, rows, sx0, sx1, cfg))
        calls.append(r)
        return res

    det._closed_end = spy
    try:
        for pool in R.POOLS:
            for si, (key, amount, variant, src, sc) in enumerate(R.scenes_of(pools[pool])):
                ctx.update(group=f"scorecard, {pool}", level=key, item=f"{src.stem.replace('4A8B_', '')} {amount} {variant}",
                           truths=[sc.target] + list(sc.fronts))
                det.detect(sc.mask, A.ARMS["close"], CAM)
        stems = R.train_stems()
        for pool in R.POOLS:
            for stem, m in sorted(segs[pool].items()):
                ctx.update(group="real frames", level=pool, item=stem.replace("4A8B_", ""),
                           truths=[(dtp.COLOR_BY_NAME[b["color"]], tuple(b["bbox"])) for b in io.load_boxes(stem)["barrels"]])
                det.detect(m, A.ARMS["close"], CAM)
        L = C.load("comb_levels_for_census", S.COMB / "run_levels.py")
        G = C.load("det_given_seg_run", C.SEG / "run.py")
        home = [s for s in stems["HOME"] if io.mask_path(s).exists()]          # G.train_sets() cannot group the new sets of 2026-11-19..21
        hand = {s: io.load_mask(io.mask_path(s)) for s in home}
        truth = {s: G.truth(s) for s in home}
        boxes = {s: [tuple(g.bbox) for g in truth[s][0]] for s in home}
        for level, d in L.LEVELS.items():
            for seed in ((-1,) if d is None else range(args.seeds)):
                for i, s in enumerate(home):
                    mask = hand[s] if d is None else dg.damage(hand[s], boxes[s], d, seed=1000 * seed + i)
                    ctx.update(group="damage levels", level=level, item=f"{s.replace('4A8B_', '')} seed {seed}",
                               truths=[(g.color, tuple(g.bbox)) for g in truth[s][0]])
                    det.detect(mask, A.ARMS["close"], CAM)
    finally:
        det._closed_end = orig

    O.OUT.mkdir(parents=True, exist_ok=True)
    for name, rows_ in (("census_ends.csv", ends), ("census_calls.csv", calls)):
        fields = list(dict.fromkeys(k for r in rows_ for k in r))
        with (O.OUT / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, restval=""); w.writeheader(); w.writerows(rows_)
    print(f"{len(ends)} ends (part A), {len(calls)} own_close calls (part B); written to {O.OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
