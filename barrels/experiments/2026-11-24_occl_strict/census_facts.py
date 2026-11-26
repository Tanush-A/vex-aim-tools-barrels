#!/usr/bin/env python3
"""The census (PREREG step 2): every box drawn by one arm on three test beds, each box judged true or false and measured
for every consistency fact of ``measures.py``. No detector change.

  real      every train frame of every set (the report's frames and segmentation); judged by the hand labels
            (``strict.judge``: hit / loose / part / wrongcolor / false).
  card      the 3888 occlusion scorecard scenes of 2026-11-19 (same sources, same scenes); a box is true when it is in the
            right place of the hidden barrel or of a barrel pasted in front (the scorecard's own "right place").
  levels    the 16 HOME hand masks, perfect and at every damage level, seeds 0 to 19 (2026-11-20_occl_combined's harness);
            judged by the v2 rule against the hand labels, then ``strict.judge`` for the misses.

    python barrels/experiments/2026-11-24_occl_strict/census_facts.py [--beds real,card,levels] [--cfg start] [--out census]
Outputs: results/2026-11-24_occl_strict/<out>/census_<bed>.csv. Train frames only (asserted in the loaded harnesses).
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import types

import strict as S
import measures as M
from barrels import detect_types as dtp, detector as det, eval_det as ed, io, report as rp
from barrels.io import ORANGE


def rows_of(bed, where, mask, cfg, judge_fn):
    log: list = []
    found = det.detect(mask, cfg, S.CAM, log)
    kinds = judge_fn(found)
    out = []
    for b, m, k in zip(found, M.measure(mask, found, log, S.CAM), kinds):
        out.append(dict(bed=bed, **where, color="orange" if b.color == ORANGE else "blue", box=" ".join(map(str, b.bbox)), kind=k,
                        true=int(k in ("hit", "loose", "part", "place")), flags=" ".join(sorted(b.flags)), source=b.source,
                        **{kk: (" ".join(map(str, v)) if isinstance(v, tuple) else v) for kk, v in m.items()}))
    return out


def real(cfg):
    CE = S.closeup_census()
    for label, stem, frame, mask in CE.masks():
        gts = dtp.barrels_from_boxes(io.load_boxes(stem))

        def judge(found, stem=stem, gts=gts):
            res = rp.score_boxes(stem, found, S.CAM)
            hit = {m.pred_idx for m in res.matches}
            return [S.judge(b.bbox, b.color, gts, i in hit) for i, b in enumerate(found)]
        yield from rows_of("real", dict(set=label, extreme=int(S.is_extreme(label)), scene=stem), mask, cfg, judge)


def card(cfg):
    C = S.battery()
    R = C.load("det_occl_run", C.OCCL / "run.py")
    R.occl_arms = types.SimpleNamespace(ARMS={}, BASE=C.A.SOURCE_BASE)
    stems = R.train_stems()
    segs = R.segmentations(stems)
    pools, _ = R.build_sources(segs)
    for pool in R.POOLS:
        for key, amount, variant, src, sc in R.scenes_of(pools[pool]):
            truths = [sc.target] + list(sc.fronts)

            def judge(found, truths=truths):
                place = R.right_place(found, truths)
                placed = set(place.values())
                return ["place" if i in placed else "false" for i in range(len(found))]
            yield from rows_of("card", dict(set=pool, extreme=0, scene=f"{key}|{amount}|{variant}|{src.stem}|{list(src.bbox)}"), sc.mask, cfg, judge)


def levels(cfg, seeds=range(20)):
    C = S.battery()
    G = C.load("det_given_seg_run", C.SEG / "run.py")
    L = C.load("comb_levels", C.HERE / "run_levels.py")
    home = [s for s in G.train_sets()["HOME"] if io.mask_path(s).exists()]
    hand = {s: io.load_mask(io.mask_path(s)) for s in home}
    truth = {s: G.truth(s) for s in home}
    boxes = {s: [tuple(g.bbox) for g in truth[s][0]] for s in home}
    for level, d in L.LEVELS.items():
        for seed in ((-1,) if d is None else seeds):
            for i, s in enumerate(home):
                mask = hand[s] if d is None else L.dg.damage(hand[s], boxes[s], d, seed=1000 * seed + i)
                gts, clean = truth[s]

                def judge(found, s=s, gts=gts, clean=clean):
                    res = ed.evaluate_frame(s, found, gts, S.CAM, rule="v2", clean=clean)
                    hit = {m.pred_idx for m in res.matches}
                    return [S.judge(b.bbox, b.color, gts, j in hit) for j, b in enumerate(found)]
                yield from rows_of("levels", dict(set=level, extreme=0, scene=f"{s}|{seed}"), mask, cfg, judge)


BEDS = {"real": real, "card": card, "levels": levels}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--beds", default="real,card,levels")
    ap.add_argument("--cfg", default="start")
    ap.add_argument("--out", default="census")
    a = ap.parse_args(argv)
    cfg = S.ARMS[a.cfg]
    out_dir = S.OUT / a.out
    out_dir.mkdir(parents=True, exist_ok=True)
    for bed in a.beds.split(","):
        rows = list(BEDS[bed](cfg))
        with open(out_dir / f"census_{bed}.csv", "w", newline="") as f:
            wr = csv.DictWriter(f, list(rows[0])); wr.writeheader(); wr.writerows(rows)
        print(bed, len(rows), "boxes,", sum(1 for r in rows if not r["true"]), "not on a barrel")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
