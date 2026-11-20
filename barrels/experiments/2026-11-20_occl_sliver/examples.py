#!/usr/bin/env python3
"""One worked example in numbers per rule of this experiment (for walkthrough.md). Train frames only.

    python barrels/experiments/2026-11-20_occl_sliver/examples.py
Outputs: results/2026-11-20_occl_sliver/examples.md
"""
from __future__ import annotations

import sys
import types

import sliver as S
from barrels import degrade as dg, detector as det, geometry as geo, io

C, A = S.C, S.A
CAM = geo.AIM_4A8B6118_BOXFIT


def stripe_info(mask, cfg, color, tb):
    narrow: list = []
    st = det.find_stripes(mask, CAM, cfg, narrow=narrow)
    c = [s for s in st if s.body == color and s.bbox[0] < tb[2] and s.bbox[2] > tb[0] and s.bbox[1] < tb[3] and s.bbox[3] > tb[1]]
    return c


def boxes(mask, cfg):
    return [(b.color, b.bbox) for b in det.detect(mask, cfg, CAM)]


def main() -> int:
    S.register()
    L = ["# Worked examples, one per rule (numbers from the masks; train frames only)", ""]
    start, arms = A.rule_config(A.ARMS["start"]), {k: A.rule_config(A.ARMS[k]) for k in ("bridge", "frame", "close", "span")}
    # stripe_bridge: HOME cluster_02, stripe patch 0.06 W, seed 1
    G = C.load("det_given_seg_run", C.SEG / "run.py")
    home = [s for s in G.train_sets()["HOME"] if io.mask_path(s).exists()]
    for stem, d, seed, tb, color, what in (("edge_01", dg.Damage(stripe_breaks=(1, 0.1)), 12, (0, 133, 34, 198), io.BLUE, "one stripe break 0.1 W"),
                                           ("cluster_02", dg.Damage(stripe_highlight=0.06), 1, (390, 116, 432, 163), io.ORANGE,
                                            "a patch 0.06 W (what round 2's same-rows test refuses)")):
        i = [k for k, s in enumerate(home) if s.endswith(stem)][0]
        gts, _ = G.truth(home[i])
        m = dg.damage(io.load_mask(io.mask_path(home[i])), [tuple(g.bbox) for g in gts], d, seed=1000 * seed + i)
        pcs = stripe_info(m, start, color, tb)
        g = det._stripe_geometry(CAM, pcs[0].center_row)[1] if pcs else None
        L += [f"## `stripe_bridge` (off): HOME `{stem}`, {'orange' if color == io.ORANGE else 'blue'} {tb}, {what} (seed {seed})", ""]
        if g is not None:
            L.append(f"- Expected at the stripe's row: W {g.width_px:.1f} px, stripe height {g.stripe_bottom - g.stripe_top:.1f} px.")
        L += [f"- Stripe pieces before: {[s.bbox for s in pcs]}; boxes of its color: {[b for c, b in boxes(m, start) if c == color]}",
              f"- With the bridge: {[s.bbox for s in stripe_info(m, arms['bridge'], color, tb)]}; boxes of its color: "
              f"{[b for c, b in boxes(m, arms['bridge']) if c == color]}", ""]
    # the scorecard examples
    sys.path.insert(0, str(C.OCCL))
    R = C.load("det_occl_run", C.OCCL / "run.py")
    R.occl_arms = types.SimpleNamespace(ARMS={"start": A.ARMS["start"]}, BASE=A.SOURCE_BASE)
    pools, _ = R.build_sources(R.segmentations(R.train_stems()))
    want = {"frame": ("frame", 0.75, "L"), "close": ("edge", 0.75, "L"), "span": ("block/other", 0.75, "R")}
    done = set()
    for key, am, var, src, sc in R.scenes_of(pools["HOME hand masks"]):
        for arm, (k, a, v) in want.items():
            if arm in done or key != k or am != a or var != v:
                continue
            color, tb = sc.target
            before, after = boxes(sc.mask, start), boxes(sc.mask, arms[arm])
            hit = [b for c, b in after if c == color and det.box_iou(b, tb) > 0.5]
            if not hit or any(c == color and det.box_iou(b, tb) > 0.5 for c, b in before):
                continue
            s = max(stripe_info(sc.mask, arms[arm], color, tb), key=lambda s: s.bbox[2] - s.bbox[0])
            rows = det._stripe_geometry(CAM, s.center_row)[1]
            W, H = rows.width_px, rows.bottom - rows.top
            L += [f"## `{ {'frame': 'thin_frame', 'close': 'own_close', 'span': 'thin_span'}[arm] }`: HOME `{src.stem.replace('4A8B_window_light_', '')}`, "
                  f"{'orange' if color == io.ORANGE else 'blue'} {tb}, scorecard '{k}' {int(a * 100)} % from the {'left' if v == 'L' else 'right'}", "",
                  f"- Stripe piece {s.bbox} ({s.bbox[2] - s.bbox[0]} px wide, thin: {s.small}); its row {s.center_row:.1f} → W {W:.1f}, H {H:.1f}, "
                  f"predicted top {rows.top:.1f}, bottom {rows.bottom:.1f}."]
            if arm == "close":
                cols = [x for x in range(sc.mask.shape[1]) if (sc.mask[:, x] == color).any()]
                sx0, sx1 = cols[0], cols[-1] + 1
                c = det._end_closure(s, sc.mask, CAM, arms[arm], sx0, sx1)
                L.append(f"- Seen columns {sx0}–{sx1}; closure left {c[0]:.3f} H, right {c[1]:.3f} H (own needs ≥ 0.15, the other ≤ 0.1).")
            if arm == "span":
                L.append("- The body joined to the piece (the barrel's upper body above the block) spans the barrel's width; no column of it "
                         "holds body color across the stripe's rows.")
            L += [f"- Before: {[b for c, b in before if c == color] or 'no box'}. After: {hit[0]}, overlap with the truth {det.box_iou(hit[0], tb):.2f}.", ""]
            done.add(arm)
    (S.OUT / "examples.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
