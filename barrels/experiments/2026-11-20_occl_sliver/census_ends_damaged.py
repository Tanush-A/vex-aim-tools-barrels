#!/usr/bin/env python3
"""Part 2, census (second half): does "the body closes on the stripe at one end and stands at the other" ever accept
a CUT end outside the scorecard? Measurement only. ``census_ends.py`` measured it on the scorecard's scenes (one barrel
alone on an empty mask); here the same reading is asked of every partly seen stripe piece the stripe finder gives on
the masks where the rule could draw a wrong box: the 16 HOME hand masks with a stripe patch or stripe breaks at each
width, "bad day", "bad day without the stripe patch" and medium damage, seeds 0 to 4; the HOME hand masks, HOME leave
one scene out and CAMPUS as the eval table segments them; black and wood report only.

Per piece (narrower than stripe_full x W once joined with its body, as ``census_ends.seen_piece`` takes it): the closure
of each end (``census_ends.end_gaps``, zone 0.05 W), and what the end is by the hand-drawn boxes: ``own`` = the end is
within the edge tolerance (bottom_tol x W, at least bottom_tol_min_px) of a side of the box of its body color that holds
the piece's centre; ``cut`` = inside that box, further from both sides; ``no barrel`` = no box of its color holds the
piece's centre. The rule speaks when one end is OWN (closed >= own) and the other CUT (closed <= cut); it is WRONG when
the end it calls own is not ``own`` by the boxes, or the piece is on no barrel.

Train frames only (the loaded scripts assert it; data/splits.json is never asked for a test frame).

    python barrels/experiments/2026-11-20_occl_sliver/census_ends_damaged.py
Outputs: results/2026-11-20_occl_sliver/ census_ends_damaged.md, census_ends_damaged.csv
"""
from __future__ import annotations

import collections
import csv
import dataclasses
import sys
import types

import census_ends as E
import sliver as S
from barrels import degrade as dg, detect_types as dtp, detector as det, geometry as geo, io

C, A = S.C, S.A
CAM = geo.AIM_4A8B6118_BOXFIT
WIDTHS = (0.03, 0.06, 0.1, 0.15, 0.2, 0.3)
SEEDS = tuple(range(5))
ZONE = 0.05
RULES = ((0.15, 0.05), (0.15, 0.1), (0.1, 0.05), (0.2, 0.1), (0.15, 0.15))


def pieces(mask, cfg):
    """(stripe, rows, sx0, sx1, full_slice, thin) of every partly seen stripe piece, as ``census_ends.seen_piece`` takes one."""
    h, w = mask.shape
    narrow: list = []
    st = det.find_stripes(mask, CAM, cfg, narrow=narrow)
    cands = st + [s for s in narrow if not any(s.bbox == o.bbox for o in st)]
    out = []
    for s in cands:
        g = det._stripe_geometry(CAM, s.center_row)
        if g is None:
            continue
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
        if sx1 - sx0 >= cfg.stripe_full * W:
            continue                                   # seen whole: the span is the box, the ends are not asked
        out.append((s, rows, sx0, sx1, not (top_inf or bot_inf), bool(s.small or s.narrow)))
    return out


def kinds_of(s, sx0, sx1, W, truths, cfg):
    cx, cy = (s.bbox[0] + s.bbox[2]) / 2, (s.bbox[1] + s.bbox[3]) / 2
    best = None
    for c, b in truths:
        if c == s.body and b[0] <= cx < b[2] and b[1] <= cy < b[3]:
            if best is None or abs(cx - (b[0] + b[2]) / 2) < abs(cx - (best[0] + best[2]) / 2):
                best = b
    if best is None:
        return "no barrel", "no barrel"
    tol = max(cfg.bottom_tol_min_px, cfg.bottom_tol * W)
    return ("own" if abs(sx0 - best[0]) <= tol else "cut"), ("own" if abs(sx1 - best[2]) <= tol else "cut")


def main(argv=None) -> int:
    S.register()
    cfg = A.rule_config(A.ARMS["start"])
    sys.path.insert(0, str(C.OCCL))
    R = C.load("det_occl_run", C.OCCL / "run.py")
    R.occl_arms = types.SimpleNamespace(ARMS={"start": A.ARMS["start"]}, BASE=A.SOURCE_BASE)
    segs = R.segmentations(R.train_stems(), with_extreme=True)

    def truths_of(stem):
        return [(dtp.COLOR_BY_NAME[b["color"]], tuple(b["bbox"])) for b in io.load_boxes(stem)["barrels"]]

    masks = []                                         # (group, level, stem, seed, mask)
    for group, pool in (("real masks", "HOME hand masks"), ("real masks", "HOME color model"), ("real masks", "CAMPUS color model"),
                        ("black and wood (report only)", "BLACK"), ("black and wood (report only)", "WOOD")):
        for stem, m in sorted(segs[pool].items()):
            masks.append((group, pool, stem, "", m))
    hand = segs["HOME hand masks"]
    levels = {f"stripe patch {w} W": dg.Damage(stripe_highlight=w) for w in WIDTHS}
    levels.update({f"one stripe break {w} W": dg.Damage(stripe_breaks=(1, w)) for w in WIDTHS})
    levels.update({f"two stripe breaks {w} W": dg.Damage(stripe_breaks=(2, w)) for w in WIDTHS})
    bad = dg.REALISTIC["white tables, bad day"]
    levels.update({"white tables, bad day": bad, "bad day without the stripe patch": dataclasses.replace(bad, stripe_highlight=0.0),
                   "light": dg.SEVERITIES["light"], "medium": dg.SEVERITIES["medium"]})
    for level, d in levels.items():
        grp = "stripe patch / breaks" if ("stripe" in level and "bad day" not in level) else "named levels"
        for seed in SEEDS:
            for i, s in enumerate(sorted(hand)):
                masks.append((grp, level, s, seed, dg.damage(hand[s], [b for _, b in truths_of(s)], d, seed=1000 * seed + i)))
    rows = []
    for group, level, stem, seed, m in masks:
        t = truths_of(stem)
        for s, rws, sx0, sx1, full, thin in pieces(m, cfg):
            W = rws.width_px
            kl, kr = kinds_of(s, sx0, sx1, W, t, cfg)
            gl, gr = E.end_gaps(m, s, rws, sx0, sx1, cfg, ZONE)
            rows.append({"group": group, "level": level, "stem": stem.replace("4A8B_", ""), "seed": seed, "body": dtp.COLOR_NAMES[s.body],
                         "piece": list(s.bbox), "seen": [sx0, sx1], "seen_w": round((sx1 - sx0) / W, 3), "full_slice": int(full), "thin": int(thin),
                         "left_kind": kl, "right_kind": kr, "left_closed": round(min(gl), 4), "right_closed": round(min(gr), 4)})
    S.OUT.mkdir(parents=True, exist_ok=True)
    with (S.OUT / "census_ends_damaged.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    groups = ("real masks", "stripe patch / breaks", "named levels", "black and wood (report only)")
    L = ["# Own side or cut side, outside the scorecard: every partly seen stripe piece on real and damaged masks (a census; no acceptance number)", "",
         f"Zone {ZONE} W. Pieces seen narrower than 0.8 W (stripe + the body joined to it). An end's kind is read off the hand-drawn boxes (`own` = within the "
         "edge tolerance of a side of the box of its color holding the piece's centre). The rule speaks when one end has closed (>= own) and the other "
         "stands (<= cut); WRONG = the end it calls own is not a box side, or the piece lies on no barrel. Seeds 0 to 4. Train frames only.", "",
         "## Closure by end kind (median; share at least 0.15; share at most 0.1)", "", "| masks | end kind | ends | median closed | >= 0.15 | <= 0.1 |", "|---|---|---|---|---|---|"]
    import numpy as np
    for g in groups:
        for k in ("own", "cut", "no barrel"):
            v = np.array([r[f"{side}_closed"] for r in rows if r["group"] == g for side in ("left", "right") if r[f"{side}_kind"] == k])
            if len(v):
                L.append(f"| {g} | {k} | {len(v)} | {np.median(v):.3f} | {int((v >= 0.15).sum())} | {int((v <= 0.1).sum())} |")
    L += ["", "## The rule, by masks: pieces / speaks / wrong (thin full slices: speaks / wrong)", "",
          "| masks | pieces | " + " | ".join(f"own >= {o}, cut <= {c}" for o, c in RULES) + " |", "|---|---|" + "---|" * len(RULES)]
    wrong_rows = collections.defaultdict(list)
    for g in groups + tuple(levels):
        rs = [r for r in rows if r["group"] == g or r["level"] == g]
        if not rs:
            continue
        cells = []
        for o, c in RULES:
            sp = wr = tsp = twr = 0
            for r in rs:
                pick = "left" if (r["left_closed"] >= o and r["right_closed"] <= c) else ("right" if (r["right_closed"] >= o and r["left_closed"] <= c) else "")
                if not pick:
                    continue
                bad_ = r[f"{pick}_kind"] != "own"
                sp += 1; wr += bad_
                if r["thin"] and r["full_slice"]:
                    tsp += 1; twr += bad_
                if bad_ and (o, c) == (0.15, 0.1) and g in groups:
                    wrong_rows[g].append(r)
            cells.append(f"{sp} / {wr} ({tsp} / {twr})")
        L.append(f"| {g} | {len(rs)} | " + " | ".join(cells) + " |")
    L += ["", "## Every wrong call of own >= 0.15, cut <= 0.1", "", "| masks | level | frame | seed | body | piece | seen | thin, full slice | left (kind, closed) | right (kind, closed) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for g in groups:
        for r in wrong_rows[g]:
            L.append(f"| {g} | {r['level']} | {r['stem']} | {r['seed']} | {r['body']} | {r['piece']} | {r['seen']} | {r['thin']}, {r['full_slice']} | "
                     f"{r['left_kind']}, {r['left_closed']} | {r['right_kind']}, {r['right_closed']} |")
    (S.OUT / "census_ends_damaged.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
