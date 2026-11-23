#!/usr/bin/env python3
"""TODO A9, part 1: the census of the stripeless close-up pieces (step-1 pieces whose box reaches the frame bottom).

For every train frame of every set (the report's frame selection and segmentation: HOME leave one scene out, every other
set with the default model as it is), every step-1 piece whose resolved box reaches the frame bottom is listed with what
the detector does with it today (refused by the size test, covered by a stripe barrel, kept as a box) and whether it is
a real barrel (same color, IoU >= 0.5 with a labeled box; the label's flags are shown). Also listed: every labeled barrel
whose box reaches the frame bottom (or is flagged close / held / no_stripe), with which part of the detector found it.

For each piece the candidate cues are measured (see ``cues``). Train frames only (``report.select_frames`` refuses test).

    python barrels/experiments/2026-11-23_closeup_shape/census.py [--cfg start] [--out census] [--sheets]
Outputs: results/2026-11-23_closeup_shape/<out>/census.csv, census.md, gt.csv, sheets/*.png
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

import closeup as K  # noqa: E402
from barrels import cv as bcv, detect_types as dtp, detector as det, geometry as geo, io, pipeline as pl  # noqa: E402
from barrels import report as rp, splits as splits_mod, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE, parse_name  # noqa: E402

CAM = geo.AIM_4A8B6118_BOXFIT


def masks(only_sets=None):
    """(set label, stem, image, class mask) for every train frame, segmented as ``report.run_arm`` does."""
    splits = splits_mod.load_splits()
    sel = rp.select_frames(rp.labeled_stems(), splits, "train", only_sets)
    rp.refuse_test_frames(sel.stems, splits)
    cache = rp.FrameCache()
    model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    keys = list(sel.sets)
    for key, stems in sel.sets.items():
        label = rp.set_label(key, keys)
        if key == rp.FIT_SET:
            scenes = {s: parse_name(s)["scene"] for s in stems}
            for fold in bcv.loso_folds(stems, scenes):
                m = pl.fit([cache.frame(s) for s in fold.train], [cache.mask(s) for s in fold.train], model.cfg)
                for s in fold.held_out:
                    yield label, s, cache.frame(s), pl.segment(cache.frame(s), m)[0]
        else:
            for s in stems:
                yield label, s, cache.frame(s), pl.segment(cache.frame(s), model)[0]


def bottom_pieces(mask, cfg):
    """Step-1 pieces (with their pixels) whose resolved box reaches the frame bottom, as ``detect_step1`` makes them,
    with the size test's verdict ('' = passed)."""
    h, w = mask.shape
    out = []
    for blob in det.find_blobs(mask, cfg):
        for piece in det.split_blob(blob, mask, CAM, cfg):
            x0, y0, x1, y1 = piece.bbox
            y1r, _ = det.resolve_bottom(piece.bbox, CAM, h, cfg)
            if y1r < h:
                continue
            W = det.expected_width_px((x0, y0, x1, h), CAM, h)
            why = ""
            if not math.isfinite(W) or W < cfg.min_width_px:
                why = "too_far"
            elif not (cfg.width_min * W <= (x1 - x0) <= cfg.width_max * W):
                why = "width"
            color = ORANGE if piece.n_orange >= piece.n_blue else BLUE
            out.append(dict(piece=piece, box=(x0, y0, x1, h), seen_y1=y1, W=W, size=why, color=color))
    return out


def best_gt(box, color, gts):
    best, bi = 0.0, None
    for g in gts:
        if g.color != color:
            continue
        iou = det.box_iou(box, g.bbox)
        if iou > best:
            best, bi = iou, g
    return best, bi


def drawn_by(log, bbox):
    for e in reversed(log):
        if e.get("why") == "kept" and e.get("box") is not None and tuple(e["box"]) == tuple(bbox):
            return e.get("stage")
    return "piece"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cfg", default="start")
    ap.add_argument("--out", default="census")
    ap.add_argument("--sets", default=None)
    ap.add_argument("--sheets", action="store_true")
    a = ap.parse_args(argv)
    cfg = K.ARMS[a.cfg]
    out_dir = K.OUT / a.out
    (out_dir / "sheets").mkdir(parents=True, exist_ok=True)
    rows, gtrows, cutrows = [], [], []
    for label, stem, frame, mask in masks(a.sets.split(",") if a.sets else None):
        h, w = mask.shape
        lab = io.load_boxes(stem)
        gts = dtp.barrels_from_boxes(lab)
        log: list = []
        found = det.detect(mask, cfg, CAM, log)
        for p in bottom_pieces(mask, cfg):
            x0, y0, x1, y1 = p["box"]
            kept = [b for b in found if b.source == "det1" and b.bbox[0] == x0 and b.bbox[1] == y0 and b.bbox[2] == x1 and b.bbox[3] == h]
            if p["size"]:
                status = "refused:" + p["size"]
            elif kept:
                status = "BOX"
            else:
                status = "covered"
            iou, g = best_gt(p["box"], p["color"], gts)
            c = K.cues(mask, p["piece"].pixels, p["box"], p["color"], CAM)
            rows.append(dict(set=label, stem=stem, color="orange" if p["color"] == ORANGE else "blue", x0=x0, y0=y0, x1=x1,
                             seen_y1=p["seen_y1"], W=round(p["W"], 1), status=status, real=int(iou >= 0.5), iou=round(iou, 2),
                             gt_flags=" ".join(sorted(g.flags)) if g is not None and iou > 0 else "",
                             negative=int(bool(lab.get("negative"))), **c))
        # the "specific position" lead: pieces refused as stripeless whose predicted stripe runs past the frame bottom
        # (no body can be seen below it, so the stripe finder cannot find it, and the piece's seen bottom agreed with the
        # predicted bottom, so it does not count as reaching the frame bottom)
        for e in log:
            if e.get("stage") == "piece" and e.get("why") == "stripeless":
                bx0, by0, bx1, by1 = e["bbox"]
                dd = CAM._d_axis_from_point_row(by0, geo.BARREL_HEIGHT_MM, +geo.BARREL_END_DIAMETER_MM / 2)
                try:
                    rr = CAM.barrel_rows(dd)
                    sb, stp = rr.stripe_bottom, rr.stripe_top
                except ValueError:
                    sb = stp = math.inf
                if sb < h:
                    continue
                col = e["body"]
                iou, g = best_gt(e["bbox"], col, gts)
                cutrows.append(dict(set=label, stem=stem, color="orange" if col == ORANGE else "blue", box=" ".join(map(str, e["bbox"])),
                                    stripe_top=round(stp, 1), stripe_bottom=round(sb, 1), real=int(iou >= 0.5), iou=round(iou, 2),
                                    negative=int(bool(lab.get("negative")))))
        for g in gts:
            fl = set(g.flags)
            if not (g.bbox[3] >= h - 2 or fl & {"close", "held", "no_stripe"}):
                continue
            bi, by = 0.0, None
            for b in found:
                if b.color == g.color:
                    i = det.box_iou(b.bbox, g.bbox)
                    if i > bi:
                        bi, by = i, b
            gtrows.append(dict(set=label, stem=stem, color="orange" if g.color == ORANGE else "blue", box=" ".join(map(str, g.bbox)),
                               flags=" ".join(sorted(fl)), best_iou=round(bi, 2),
                               by=("" if by is None else (by.source if by.source == "det1" else drawn_by(log, by.bbox))),
                               box_found=" ".join(map(str, by.bbox)) if by is not None else ""))
        if a.sheets and any(r["stem"] == stem for r in rows):
            img = frame.bgr.copy() if hasattr(frame, "bgr") else None
            if img is None:
                img = cv2.imread(str(io.find_image(stem)))
            vis = np.zeros_like(img)
            vis[mask == ORANGE] = (0, 140, 255)
            vis[mask == BLUE] = (255, 80, 0)
            for r in rows:
                if r["stem"] != stem:
                    continue
                col = (0, 255, 0) if r["status"] == "BOX" else (0, 0, 255) if r["status"] == "covered" else (128, 128, 128)
                for im in (img, vis):
                    cv2.rectangle(im, (r["x0"], r["y0"]), (r["x1"] - 1, h - 1), col, 2)
            for g in gts:
                cv2.rectangle(img, (g.bbox[0], g.bbox[1]), (g.bbox[2] - 1, g.bbox[3] - 1), (255, 255, 255), 1)
            cv2.imwrite(str(out_dir / "sheets" / f"{stem}.png"), np.hstack([img, vis]))
    keys = list(rows[0])
    with open(out_dir / "census.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, keys); wr.writeheader(); wr.writerows(rows)
    with open(out_dir / "gt.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, list(gtrows[0])); wr.writeheader(); wr.writerows(gtrows)
    if cutrows:
        with open(out_dir / "stripe_cut.csv", "w", newline="") as f:
            wr = csv.DictWriter(f, list(cutrows[0])); wr.writeheader(); wr.writerows(cutrows)
    def table(f, rs, ks):
        f.write("| " + " | ".join(ks) + " |\n|" + "---|" * len(ks) + "\n")
        for r in rs:
            f.write("| " + " | ".join(str(r[k]) for k in ks) + " |\n")

    import collections
    with open(out_dir / "census.md", "w") as f:
        f.write(f"# Census of the frame-bottom step-1 pieces (arm `{a.cfg}`; train frames; all rows in census.csv)\n\n")
        cnt = collections.Counter((r["status"].split(":")[0], "real" if r["real"] else ("empty frame" if r["negative"] else "not a barrel"))
                                  for r in rows)
        f.write("| what the detector does | real barrel | not a barrel | on an empty frame |\n|---|---|---|---|\n")
        for st in ("BOX", "covered", "refused"):
            f.write(f"| {st} | {cnt[(st, 'real')]} | {cnt[(st, 'not a barrel')]} | {cnt[(st, 'empty frame')]} |\n")
        f.write("\n## Every piece kept or covered (the refused ones fail the size test and are untouched)\n\n")
        table(f, [r for r in rows if not r["status"].startswith("refused")],
              ["set", "stem", "color", "x0", "y0", "x1", "seen_y1", "status", "real", "iou", "cut_l", "cut_r", "ratio", "st_pred",
               "upper", "reach", "rule_pass", "cost_l", "cost_r", "fill_box", "row_fill", "top_flat", "body", "other"])
        f.write("\n## Labeled barrels at the frame bottom (or close / held / no_stripe)\n\n")
        table(f, gtrows, list(gtrows[0]))
        if cutrows:
            f.write("\n## Pieces refused as stripeless whose predicted stripe runs past the frame bottom\n\n")
            table(f, cutrows, list(cutrows[0]))
    print(f"{len(rows)} pieces, {len(gtrows)} labeled barrels -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
