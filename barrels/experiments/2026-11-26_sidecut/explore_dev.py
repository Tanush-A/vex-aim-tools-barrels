#!/usr/bin/env python3
"""EXPLORATION, run BEFORE the PREREG was written, on the development material only (PREREG.md lists it):
the HOME and ABP white train frames (source barrels and simulated cuts on them) and the five real frames with a black
box at the side (occlx_01 to occlx_05). It answers: how much does a barrel's own side bulge in a real mask, how much
does a cut side, which split of the rows shows it best, and where a threshold between the two would sit.

    python barrels/experiments/2026-11-26_sidecut/explore_dev.py [POOL ...]        # default: HOME "ABP white"
"""
from __future__ import annotations

import sys

import numpy as np

import lib
from lib import dtp, io, oc

BANDS = (1 / 6, 0.25, 1 / 3)
SHARES = (0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5)
FLOOR = 1.0


def q(v, p):
    return float(np.percentile(v, p)) if len(v) else float("nan")


def main() -> None:
    pools = sys.argv[1:] or ["HOME", "ABP white"]
    for pool in pools:
        srcs = lib.sources(pool)
        print(f"\n================ {pool}: {len(srcs)} source barrels, widths {sorted(s.width for s in srcs)}")
        print("-- own sides: each source barrel alone and unhidden (both sides are its own): bulge in px, per band")
        own = {b: [] for b in BANDS}
        for src in srcs:
            ms = [m for m in lib.measure(oc.make_scene(src, "edge", 0.0).mask, BANDS) if m["stripe"].body == src.color]
            if not ms:
                print("   no stripe", src.stem); continue
            m = max(ms, key=lambda m: m["stripe"].bbox[2] - m["stripe"].bbox[0])
            line = []
            for b in BANDS:
                r = m["bulges"][b]
                if r is None:
                    line.append("None"); continue
                own[b] += [(r[0], r[2]), (r[1], r[2])]
                line.append(f"L {r[0]:+.1f} R {r[1]:+.1f} outline {r[2]:.1f}")
            print(f"   {src.stem[5:]:34s} W {m['W']:5.1f} inferred {m['inferred']} | " + " | ".join(line))
        for b in BANDS:
            v = np.array([a / p for a, p in own[b]])
            print(f"   band {b:.2f}: n {len(v)}  share of the outline's bulge: min {v.min():.2f}  5% {q(v, 5):.2f}  25% {q(v, 25):.2f}  median {np.median(v):.2f}  75% {q(v, 75):.2f}")

        print("-- simulated cuts: (cut side, own side) as a share of the outline's bulge; then what a threshold would decide")
        for short in (0, lib.SHORT_PX):
            for kind in ("edge", "slant"):
                for b in BANDS:
                    rows, none = [], 0
                    for src in srcs:
                        for k, amount, side, lean, sh, sc in lib.side_cut_scenes(src):
                            if k != kind or sh != short:
                                continue
                            ms = [m for m in lib.measure(sc.mask, (b,)) if m["stripe"].body == src.color]
                            if not ms or ms[0]["bulges"][b] is None or ms[0]["inferred"] or ms[0]["bulges"][b][2] <= 0:
                                none += 1; continue
                            L, R, P = ms[0]["bulges"][b]
                            rows.append(((L, R) if side == "L" else (R, L)) + (P, amount))
                    a = np.array(rows)
                    cut, kept, P = a[:, 0], a[:, 1], a[:, 2]
                    print(f"   {kind:5s} short {short} band {b:.2f}: measured {len(a)}, not {none} | cut side px max {cut.max():.1f} 95% {q(cut, 95):.1f}, share max {(cut / P).max():.2f} "
                          f"95% {q(cut / P, 95):.2f} | own side px min {kept.min():.1f} 5% {q(kept, 5):.1f} median {np.median(kept):.1f}, share min {(kept / P).min():.2f} "
                          f"5% {q(kept / P, 5):.2f} median {np.median(kept / P):.2f}")
                    out = []
                    for sh_ in SHARES:
                        need = sh_ * P
                        tell = need >= FLOOR
                        o, c = kept >= need, cut >= need
                        out.append(f"{sh_}: right {int((tell & o & ~c).sum())} none {int((~tell | (~o & ~c)).sum())} both {int((tell & o & c).sum())} WRONG {int((tell & ~o & c).sum())}")
                    print("        share -> " + " | ".join(out))

    print("\n================ the real frames with a black box at the side: (left, right, outline) px per band")
    for tag in ("01", "02", "03", "04", "05"):
        stem = f"4A8B_window_abpwhite_occlx_{tag}"
        mask = lib.mask_of(stem)
        gts = [g for g in dtp.barrels_from_boxes(io.load_boxes(stem)) if "occluded" in g.flags]
        for m in lib.measure(mask, BANDS):
            s = m["stripe"]
            if not any(g.bbox[0] - 5 <= (s.bbox[0] + s.bbox[2]) / 2 <= g.bbox[2] + 5 and g.color == s.body for g in gts):
                continue
            print(f"   occlx_{tag} truth {gts[0].bbox} stripe {s.bbox} thin {s.thin} W {m['W']:.1f} inferred {m['inferred']} rows {m['top']}-{m['bottom']} "
                  f"span {m['sx0']}-{m['sx1']} | " + " | ".join(
                      f"band {b:.2f}: {m['bulges'][b] and tuple(round(x, 1) for x in m['bulges'][b])}" for b in BANDS))


if __name__ == "__main__":
    main()
