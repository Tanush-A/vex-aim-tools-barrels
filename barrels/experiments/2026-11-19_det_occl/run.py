#!/usr/bin/env python3
"""The occlusion scorecard (2026-11-19): how good is the detector when part of a barrel is hidden, per kind of
occlusion and per amount hidden?

Part 1, synthetic and measured (``barrels.occlude``): every unhidden barrel of the train frames is cut out of a good
mask, put alone on an empty mask at its own place, and one occluder hides 25, 50 or 75 % of it: a frame edge, a
straight edge, a slanted edge, both sides, from above, from below, a post, a barrel of the other or of the same body
color (beside, beside and lower, straight in front), a plain block of barrel color. The detector is scored against
the barrel's FULL box. Three pools of source barrels:

  ``HOME hand masks``     the hand-made masks of the HOME train frames (perfect segmentation);
  ``HOME color model``    the same frames segmented as in the eval table (color model re-fit without the frame's scene);
  ``CAMPUS color model``  the CAMPUS train frames with the adopted color model.

A source barrel is one with no flag, at least 3 px inside the frame, not overlapping another barrel's box by more
than 2 px, and found by ``base`` when it stands alone and unhidden (so the card measures occlusion and nothing else).

Per cell (kind x amount), for each arm:
  found (v2)        the v2 rule against the full box: same color, IoU >= 0.5, bottom within max(3 px, 10 % of the height);
  right place       looser: a box of the same color whose centre is within half a barrel width of the true centre;
  overlap           mean IoU of those right-place boxes with the full box;
  too small / big   of the right-place boxes: narrower or shorter than 0.85 of the full box / wider or taller than 1.15;
  false boxes       boxes that are in the right place of no true barrel (the hidden one, or a barrel pasted in front);
  front found       for the barrel kinds: the pasted front barrel, v2 rule.

Part 2, real: every barrel flagged ``occluded`` or ``truncated`` in the train frames, one by one, same counts.

Train frames only; a test frame is never opened (asserted).

    python barrels/experiments/2026-11-19_det_occl/run.py                         # every arm of occl_arms.py
    python barrels/experiments/2026-11-19_det_occl/run.py --arms base --out step1_baseline

Outputs: results/2026-11-19_det_occl/[<out>/] scorecard.md, summary.md, cells.csv, scenes.csv, real.md, real.csv,
config.json (committed); sheets/ (ignored): one contact sheet per kind of occlusion.
"""
from __future__ import annotations

import argparse
import collections
import csv
import dataclasses
import importlib.util
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
sys.path.insert(0, str(HERE))
from barrels import cv as bcv, detect_types as dtp, detector as det, eval_det as ed, geometry as geo, io, occlude as oc, pipeline as pl  # noqa: E402
from barrels import splits, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402
import occl_arms  # noqa: E402

_spec = importlib.util.spec_from_file_location("occl_attribution", HERE.parent / "2026-11-11_occl_attribution" / "run.py")
att = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(att)

OUT = PKG_ROOT / "results" / "2026-11-19_det_occl"
CAM = geo.AIM_4A8B6118_BOXFIT
SEED = 0
EDGE_MARGIN = 3            # a source barrel's box is at least this far inside the frame
OVERLAP_MAX = 2            # ... and overlaps no other barrel's box by more than this many columns
SMALL, BIG = 0.85, 1.15    # a right-place box is "too small" / "too big" when a side is under / over this x the full box's
POOLS = ("HOME hand masks", "HOME color model", "CAMPUS color model")
SETS = {"HOME": "4A8B_window_light_", "CAMPUS": "4A8B_campus_light_", "BLACK": "4A8B_window_black_", "WOOD": "_wood_"}

# the rows of the scorecard: (key, plain name, kind, color or None)
ROWS = [
    ("frame", "cut by the frame edge", "frame", None),
    ("edge", "a straight upright edge, one side", "edge", None),
    ("slant", "a slanted edge, one side", "slant", None),
    ("both", "both sides cut", "both", None),
    ("top", "hidden from above", "top", None),
    ("bottom", "hidden from below (a low thing in front)", "bottom", None),
    ("post", "a post across the middle", "post", None),
    ("barrel_side/other", "a barrel of the OTHER color, beside it", "barrel_side", "other"),
    ("barrel_low/other", "a barrel of the OTHER color, beside it and lower", "barrel_low", "other"),
    ("barrel_front/other", "a barrel of the OTHER color, straight in front", "barrel_front", "other"),
    ("barrel_side/same", "a barrel of the SAME color, beside it", "barrel_side", "same"),
    ("barrel_low/same", "a barrel of the SAME color, beside it and lower", "barrel_low", "same"),
    ("barrel_front/same", "a barrel of the SAME color, straight in front", "barrel_front", "same"),
    ("block/same", "a plain block of the barrel's body color", "block", "same"),
    ("block/other", "a plain block of the barrel's stripe color", "block", "other"),
]
ROW_NAME = {k: n for k, n, _, _ in ROWS}
# what the arms after `base` are, for the scorecard's first paragraph (the verdict is in verdict.md)
AFTER_TEXT = ("`edge+cap` = what passed the pre-registered rule and is on by default (`edge_check`, `cap_same`). `all` = with the three switches "
              "that did not pass by the letter and are OFF (`slice_box`, `cover_unpinned`, `stripe_two`): what occlusion handling would be with them on.")


# ---------------------------------------------------------------- frames and source barrels

def train_stems() -> dict[str, list[str]]:
    sp = splits.load_splits()
    test = set(sp["test"])
    out: dict[str, list[str]] = {k: [] for k in SETS}
    for s in sorted(sp["train"]):
        assert s not in test, "a test frame leaked into the train list"
        if not io.boxes_path(s).exists():
            continue
        for name, key in SETS.items():
            if (s.startswith(key) if name != "WOOD" else key in s):
                out[name].append(s)
    return out


def segmentations(stems: dict[str, list[str]], with_extreme: bool = False) -> dict[str, dict[str, np.ndarray]]:
    """pool or set name -> {stem: class mask}. HOME is segmented leave-one-scene-out, as in the eval table."""
    model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    home = [s for s in stems["HOME"] if io.mask_path(s).exists()]
    frames = {s: pl.Frame.from_image(io.load_image(io.find_image(s))) for s in home}
    hand = {s: io.load_mask(io.mask_path(s)) for s in home}
    loso = {}
    for fold in bcv.loso_folds(home, {s: io.parse_name(s)["scene"] for s in home}):
        m = pl.fit([frames[s] for s in fold.train], [hand[s] for s in fold.train], model.cfg)
        for s in fold.held_out:
            loso[s] = pl.segment(frames[s], m)[0]
    out = {"HOME hand masks": hand, "HOME color model": loso,
           "CAMPUS color model": {s: pl.segment(pl.Frame.from_image(io.load_image(io.find_image(s))), model)[0] for s in stems["CAMPUS"]}}
    if with_extreme:
        for name in ("BLACK", "WOOD"):
            out[name] = {s: pl.segment(pl.Frame.from_image(io.load_image(io.find_image(s))), model)[0] for s in stems[name]}
    return out


def eligible(b: dict, others: list[dict]) -> bool:
    x0, y0, x1, y1 = b["bbox"]
    if b.get("flags") or x0 < EDGE_MARGIN or y0 < EDGE_MARGIN or x1 > oc.FRAME_W - EDGE_MARGIN or y1 > oc.FRAME_H - EDGE_MARGIN:
        return False
    for o in others:
        ox0, oy0, ox1, oy1 = o["bbox"]
        if min(x1, ox1) - max(x0, ox0) > OVERLAP_MAX and min(y1, oy1) > max(y0, oy0):
            return False
    return True


def found_v2(preds, color: int, box) -> bool:
    g = dtp.Barrel(color=color, bbox=tuple(box), source="gt")
    return not ed.evaluate_frame("scene", preds, [g], CAM, rule="v2").unmatched_gt


def build_sources(segs) -> tuple[dict[str, list[oc.Source]], list[dict]]:
    """pool -> source barrels; and the barrels left out because ``base`` does not find them alone and unhidden."""
    pools: dict[str, list[oc.Source]] = {p: [] for p in POOLS}
    dropped = []
    for pool in POOLS:
        for stem, mask in sorted(segs[pool].items()):
            barrels = io.load_boxes(stem)["barrels"]
            for i, b in enumerate(barrels):
                others = [o for j, o in enumerate(barrels) if j != i]
                if not eligible(b, others):
                    continue
                src = oc.cut_source(mask, b["bbox"], dtp.COLOR_BY_NAME[b["color"]], [o["bbox"] for o in others], stem=stem, pool=pool)
                alone = oc.make_scene(src, "edge", 0.0)
                if found_v2(det.detect(alone.mask, occl_arms.BASE, CAM), src.color, src.bbox):
                    pools[pool].append(src)
                else:
                    dropped.append({"pool": pool, "stem": stem, "color": b["color"], "bbox": b["bbox"]})
    return pools, dropped


# ---------------------------------------------------------------- the scenes

def scenes_of(pool: list[oc.Source]):
    """Every scene of one pool: (row key, amount, variant text, source, Scene). Deterministic: both sides for the
    sided kinds, both leans for the slanted edge; the barrel pasted in front is drawn from the same pool with a
    seeded generator (one draw per source and kind)."""
    for si, src in enumerate(pool):
        for ki, (key, _, kind, color) in enumerate(ROWS):
            rng = np.random.default_rng([SEED, si, ki])
            front = pool[int(rng.integers(len(pool)))] if kind in oc.BARRELS else None
            for amount in oc.AMOUNTS:
                for side in (("L", "R") if kind in oc.SIDED else ("L",)):
                    for lean in ((1, -1) if kind == "slant" else (1,)):
                        try:
                            sc = oc.make_scene(src, kind, amount, side, color or "other", front, CAM, lean)
                        except ValueError:
                            continue                     # no room for a barrel straight in front of a close-up
                        variant = (side if kind in oc.SIDED else "") + ({1: "+", -1: "-"}[lean] if kind == "slant" else "")
                        yield key, amount, variant, src, sc


def centre(box) -> tuple[float, float]:
    return (box[0] + box[2]) / 2, (box[1] + box[3]) / 2


def right_place(preds: list[dtp.Barrel], truths: list[tuple[int, tuple]]) -> dict[int, int]:
    """truth index -> pred index: a box of the same color whose centre is within half the true box's width of the
    true centre; nearest pairs first, each box and each truth used once."""
    pairs = []
    for ti, (c, tb) in enumerate(truths):
        tx, ty = centre(tb)
        for pi, p in enumerate(preds):
            if p.color != c:
                continue
            px, py = centre(p.bbox)
            d = float(np.hypot(px - tx, py - ty))
            if d <= (tb[2] - tb[0]) / 2:
                pairs.append((d, ti, pi))
    out: dict[int, int] = {}
    used = set()
    for d, ti, pi in sorted(pairs):
        if ti not in out and pi not in used:
            out[ti] = pi; used.add(pi)
    return out


def score_scene(sc: oc.Scene, cfg: det.DetConfig) -> dict:
    log: list = []
    preds = det.detect(sc.mask, cfg, CAM, log=log)
    truths = [sc.target] + list(sc.fronts)
    gts = [dtp.Barrel(color=c, bbox=tuple(b), source="gt") for c, b in truths if b[2] > b[0] and b[3] > b[1]]
    res = ed.evaluate_frame("scene", preds, gts, CAM, rule="v2")
    place = right_place(preds, truths)
    row = {"found": int(0 not in res.unmatched_gt), "place": int(0 in place), "iou": "", "size": "", "w_ratio": "", "h_ratio": "",
           "false": len(preds) - len(place), "false_v2": len(res.unmatched_pred), "boxes": len(preds),
           "fronts": len(sc.fronts), "fronts_found": sum(1 for gi in range(1, len(gts)) if gi not in res.unmatched_gt),
           "box": "", "cause": "", "preds": preds, "log": log}
    tc, tb = sc.target
    if 0 in place:
        p = preds[place[0]]
        wr, hr = p.width / (tb[2] - tb[0]), p.height / (tb[3] - tb[1])
        row.update(iou=round(ed.box_iou(p.bbox, tb), 3), w_ratio=round(wr, 3), h_ratio=round(hr, 3), box=list(p.bbox),
                   size="small" if min(wr, hr) < SMALL else ("big" if max(wr, hr) > BIG else "right"))
    if not row["found"]:
        g = dtp.Barrel(color=tc, bbox=tuple(tb), source="gt")
        row["cause"] = att.attribute(g, preds, log, att.inside(sc.mask, g))[0]
    return row


# ---------------------------------------------------------------- cells

@dataclasses.dataclass
class Cell:
    n: int = 0
    found: int = 0
    place: int = 0
    ious: list = dataclasses.field(default_factory=list)
    small: int = 0
    right: int = 0
    big: int = 0
    false: int = 0
    false_v2: int = 0
    fronts: int = 0
    fronts_found: int = 0
    hidden: list = dataclasses.field(default_factory=list)
    causes: collections.Counter = dataclasses.field(default_factory=collections.Counter)

    def add(self, r: dict, hidden: float) -> None:
        self.n += 1; self.found += r["found"]; self.place += r["place"]
        if r["iou"] != "":
            self.ious.append(r["iou"])
        self.small += r["size"] == "small"; self.right += r["size"] == "right"; self.big += r["size"] == "big"
        self.false += r["false"]; self.false_v2 += r["false_v2"]; self.fronts += r["fronts"]; self.fronts_found += r["fronts_found"]
        self.hidden.append(hidden)
        if r["cause"]:
            self.causes[r["cause"]] += 1

    @property
    def iou(self) -> float:
        return float(np.mean(self.ious)) if self.ious else float("nan")


def amount_text(a: float) -> str:
    return f"{int(round(100 * a))} %"


# ---------------------------------------------------------------- pictures

def render(sc: oc.Scene, preds, label: str, size: int = 240) -> np.ndarray:
    """One tile: the scene's mask around the hidden barrel (class colors on dark gray), the full true box in white,
    a pasted front barrel's box in gray, the boxes drawn in yellow (orange barrel) / green (blue barrel)."""
    boxes = [sc.target[1]] + [b for _, b in sc.fronts + sc.clutter] + [p.bbox for p in preds]
    pad = 12
    x0, y0 = max(0, min(b[0] for b in boxes) - pad), max(0, min(b[1] for b in boxes) - pad)
    x1, y1 = min(oc.FRAME_W, max(b[2] for b in boxes) + pad), min(oc.FRAME_H, max(b[3] for b in boxes) + pad)
    f = min(size / (x1 - x0), size / (y1 - y0))
    seg = np.full((oc.FRAME_H, oc.FRAME_W, 3), 45, np.uint8)
    seg[sc.mask == ORANGE] = (0, 140, 255); seg[sc.mask == BLUE] = (255, 120, 0)
    crop = cv2.resize(seg[y0:y1, x0:x1], None, fx=f, fy=f, interpolation=cv2.INTER_NEAREST)

    def box(b, color, t=1):
        cv2.rectangle(crop, (int((b[0] - x0) * f), int((b[1] - y0) * f)), (int((b[2] - x0) * f) - 1, int((b[3] - y0) * f) - 1), color, t)

    for _, b in sc.fronts + sc.clutter:
        box(b, (150, 150, 150))
    box(sc.target[1], (255, 255, 255))
    for p in preds:
        box(p.bbox, det.BOX_COLOR_BGR[p.color], 2)
    tile = np.full((size + 18, size, 3), 0, np.uint8)
    tile[18:18 + crop.shape[0], :crop.shape[1]] = crop[:size, :size]
    cv2.putText(tile, label, (3, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)
    return tile


def write_sheets(pools, arms: list[str], out: Path) -> None:
    """One sheet per scorecard row: three example barrels (the first source of each pool) down, the three amounts
    across, and each arm side by side (left to right in the order given)."""
    d = out / "sheets"
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob("*.png"):
        old.unlink()
    examples = []
    for pool in POOLS:
        srcs = pools[pool]
        if srcs:
            mid = sorted(srcs, key=lambda s: s.width)[len(srcs) // 2]          # a barrel of middle size
            examples.append((pool, srcs.index(mid), mid))
    for ki, (key, name, kind, color) in enumerate(ROWS):
        rows = []
        for pool, si, src in examples:
            rng = np.random.default_rng([SEED, si, ki])
            front = pools[pool][int(rng.integers(len(pools[pool])))] if kind in oc.BARRELS else None
            tiles = []
            for amount in oc.AMOUNTS:
                try:
                    sc = oc.make_scene(src, kind, amount, "L", color or "other", front, CAM, 1)
                except ValueError:
                    continue
                for a in arms:
                    preds = det.detect(sc.mask, occl_arms.ARMS[a], CAM)
                    tiles.append(render(sc, preds, f"{amount_text(amount)} {a} | {pool.split(' ')[0]} {src.stem.split('_', 3)[-1]}"))
            if tiles:
                rows.append(np.hstack(tiles))
        if rows:
            w = max(r.shape[1] for r in rows)
            rows = [np.pad(r, ((0, 0), (0, w - r.shape[1]), (0, 0))) for r in rows]
            cv2.imwrite(str(d / f"{ki:02d}_{key.replace('/', '_')}.png"), np.vstack(rows))


# ---------------------------------------------------------------- part 2: the real occluded barrels

def real_rows(segs, stems, arms: list[str]) -> list[dict]:
    rows = []
    for set_name, pool in (("HOME hand masks", "HOME hand masks"), ("HOME", "HOME color model"), ("CAMPUS", "CAMPUS color model"),
                           ("BLACK (extreme)", "BLACK"), ("WOOD (extreme)", "WOOD")):
        for stem, mask in sorted(segs[pool].items()):
            label = io.load_boxes(stem)
            gts = dtp.barrels_from_boxes(label)
            for a in arms:
                log: list = []
                preds = det.detect(mask, occl_arms.ARMS[a], CAM, log=log)
                res = ed.evaluate_frame(stem, preds, gts, CAM, rule="v2", clean=label.get("clean", True))
                place = right_place(preds, [(g.color, g.bbox) for g in gts])
                for gi, g in enumerate(gts):
                    if not ({"occluded", "truncated"} & set(g.flags)):
                        continue
                    r = {"arm": a, "set": set_name, "stem": stem.replace("4A8B_", ""), "color": dtp.COLOR_NAMES[g.color], "truth": list(g.bbox),
                         "flags": "+".join(sorted(g.flags)), "found": int(gi not in res.unmatched_gt), "place": int(gi in place),
                         "box": "", "iou": "", "w_ratio": "", "cause": ""}
                    if gi in place:
                        p = preds[place[gi]]
                        r.update(box=list(p.bbox), iou=round(ed.box_iou(p.bbox, g.bbox), 2), w_ratio=round(p.width / g.width, 2))
                    if not r["found"]:
                        r["cause"] = att.attribute(g, preds, log, att.inside(mask, g))[0]
                    rows.append(r)
    return rows


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arms", default=",".join(occl_arms.ARMS))
    ap.add_argument("--out", default="", help="sub-folder of the results folder (default: the folder itself)")
    ap.add_argument("--after", default="", help="the arm shown as 'after' on the scorecard (default: the last arm given)")
    ap.add_argument("--no-sheets", action="store_true")
    args = ap.parse_args(argv)
    out = OUT / args.out if args.out else OUT
    out.mkdir(parents=True, exist_ok=True)
    arms = [a for a in args.arms.split(",") if a]
    afters = [a for a in (args.after or arms[-1]).split(",") if a]      # one or more arms shown after `base` on the scorecard, in this order
    stems = train_stems()
    segs = segmentations(stems, with_extreme=True)
    pools, dropped = build_sources(segs)

    cells: dict[tuple, Cell] = collections.defaultdict(Cell)        # (arm, pool or ALL, row key, amount)
    scene_rows = []
    for pool in POOLS:
        for key, amount, variant, src, sc in scenes_of(pools[pool]):
            for a in arms:
                r = score_scene(sc, occl_arms.ARMS[a])
                for p in (pool, "ALL"):
                    cells[(a, p, key, amount)].add(r, sc.hidden)
                scene_rows.append({"arm": a, "pool": pool, "row": key, "amount": amount, "variant": variant, "stem": src.stem.replace("4A8B_", ""),
                                   "color": dtp.COLOR_NAMES[src.color], "truth": list(sc.target[1]), "hidden_share": round(sc.hidden, 2),
                                   **{k: r[k] for k in ("found", "place", "iou", "size", "w_ratio", "h_ratio", "false", "false_v2", "fronts", "fronts_found", "box", "cause")}})

    with (out / "scenes.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(scene_rows[0].keys())); w.writeheader(); w.writerows(scene_rows)
    with (out / "cells.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["arm", "pool", "row", "amount", "n", "found_v2", "right_place", "mean_iou", "too_small", "about_right", "too_big", "false_boxes",
                    "false_boxes_v2", "fronts", "fronts_found", "median_hidden_share"])
        for (a, p, key, amount), c in cells.items():
            w.writerow([a, p, key, amount, c.n, c.found, c.place, "" if not c.ious else round(c.iou, 3), c.small, c.right, c.big, c.false, c.false_v2,
                        c.fronts, c.fronts_found, round(float(np.median(c.hidden)), 2)])

    real = real_rows(segs, stems, arms)
    with (out / "real.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(real[0].keys())); w.writeheader(); w.writerows(real)

    # ---- summary.md: every arm, every pool
    n_src = {p: len(pools[p]) for p in POOLS}
    L = ["# The occlusion scorecard, in full", "",
         f"git {bcv.git_hash()}; camera AIM_4A8B6118_BOXFIT; train frames only. Source barrels: " + ", ".join(f"{p} {n_src[p]}" for p in POOLS) +
         f" (left out because `base` does not find them alone and unhidden: {len(dropped)}).", "",
         "Each cell: found under the v2 rule / box in the right place / scenes; (mean overlap of the right-place boxes with the FULL box; "
         "too small · about right · too big; false boxes). `front` = the barrel pasted in front, found / pasted.", ""]
    for a in arms:
        for p in ("ALL",) + POOLS:
            L += [f"## `{a}`, {'all three pools' if p == 'ALL' else p}", "", "| kind of occlusion | 25 % hidden | 50 % hidden | 75 % hidden |", "|---|---|---|---|"]
            for key, name, kind, color in ROWS:
                txt = []
                for amount in oc.AMOUNTS:
                    c = cells.get((a, p, key, amount))
                    if c is None or c.n == 0:
                        txt.append("-"); continue
                    t = f"{c.found} / {c.place} / {c.n} ({'-' if not c.ious else f'{c.iou:.2f}'}; {c.small} · {c.right} · {c.big}; {c.false})"
                    if c.fronts:
                        t += f"; front {c.fronts_found} / {c.fronts}"
                    txt.append(t)
                L.append(f"| {name} | " + " | ".join(txt) + " |")
            L.append("")
        L += [f"### `{a}`: why the hidden barrel was not found under the v2 rule (all pools)", ""]
        for key, name, kind, color in ROWS:
            for amount in oc.AMOUNTS:
                c = cells.get((a, "ALL", key, amount))
                if c and c.causes:
                    L.append(f"- {name}, {amount_text(amount)}: " + ", ".join(f"{k} {v}" for k, v in c.causes.most_common()))
        L.append("")
    if dropped:
        L += ["## Source barrels left out (not found alone and unhidden by `base`)", ""] + [f"- {d['pool']}: {d['stem']} {d['color']} {d['bbox']}" for d in dropped] + [""]
    (out / "summary.md").write_text("\n".join(L) + "\n")

    # ---- real.md
    R = ["# The real occluded barrels of the train frames, one by one", "",
         "Every hand-drawn box flagged `occluded` or `truncated` (cut by the frame). HOME = segmented as in the eval table; BLACK and WOOD are the "
         "extreme sets (adopted color model, report only). found = v2 rule; place = a box of the right color centred within half a barrel width.", ""]
    by = collections.defaultdict(list)
    for r in real:
        by[(r["set"], r["stem"], r["color"], tuple(r["truth"]), r["flags"])].append(r)
    R += ["| set | frame | barrel | flags | " + " | ".join(f"`{a}`" for a in arms) + " |", "|---|---|---|---|" + "---|" * len(arms)]
    tot = collections.Counter()
    for (s, stem, color, truth, flags), rs in by.items():
        d = {r["arm"]: r for r in rs}
        for a in arms:
            tot[(s, a, "n")] += 1; tot[(s, a, "found")] += d[a]["found"]; tot[(s, a, "place")] += d[a]["place"]
        if s.startswith("WOOD"):
            continue                                     # 9 lamp settings x the same scenes: counted below, not listed
        txt = []
        for a in arms:
            r = d[a]
            txt.append(("found" if r["found"] else ("right place, not v2" if r["place"] else "no box")) +
                       (f", overlap {r['iou']}, width {r['w_ratio']}" if r["place"] else "") + (f" ({r['cause']})" if r["cause"] else ""))
        R.append(f"| {s} | {stem.split('_', 2)[-1]} | {color} {list(truth)} | {flags} | " + " | ".join(txt) + " |")
    R += ["", "Totals (found under v2 / box in the right place / barrels):", "", "| set | " + " | ".join(f"`{a}`" for a in arms) + " |", "|---|" + "---|" * len(arms)]
    for s in dict.fromkeys(k[0] for k in tot):
        R.append(f"| {s} | " + " | ".join(f"{tot[(s, a, 'found')]} / {tot[(s, a, 'place')]} / {tot[(s, a, 'n')]}" for a in arms) + " |")
    (out / "real.md").write_text("\n".join(R) + "\n")

    # ---- scorecard.md: one page
    before = "base" if "base" in arms else arms[0]
    afters = [a for a in afters if a != before]
    two = bool(afters)

    def cell(key, amount, field):
        b = cells.get((before, "ALL", key, amount))
        if b is None or b.n == 0:
            return "-"
        return " → ".join(str(getattr(cells[(a, "ALL", key, amount)], field)) for a in [before] + afters) + f" of {b.n}"

    S = ["# Occlusion scorecard", "",
         f"How often the detector boxes a barrel when part of it is hidden. {sum(n_src.values())} unhidden barrels of the train frames "
         f"({', '.join(f'{n_src[p]} from {p}' for p in POOLS)}), each hidden by one thing at a time, by a measured amount. "
         + (f"Each cell: **{' → '.join(['before'] + [f'`{a}`' for a in afters])}, of n scenes**." if two else "Each cell: **found of n scenes** (the baseline, before any fix).")
         + f" Before = the detector at the start of this work (`{before}`)." + (f" {AFTER_TEXT}" if two else ""), "",
         "## Found: a box of the right color, overlapping the barrel's FULL box by half or more, bottom edge right (the project's v2 rule)", "",
         "| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |", "|---|---|---|---|"]
    for key, name, kind, color in ROWS:
        S.append(f"| {name} | " + " | ".join(cell(key, a, "found") for a in oc.AMOUNTS) + " |")
    S += ["", "## Looser: a box of the right color in the right place (centre within half a barrel width), whatever its size", "",
          "| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |", "|---|---|---|---|"]
    for key, name, kind, color in ROWS:
        S.append(f"| {name} | " + " | ".join(cell(key, a, "place") for a in oc.AMOUNTS) + " |")
    tot_scenes = sum(c.n for (a, p, k, m), c in cells.items() if a == before and p == "ALL")

    def total(arm, field):
        return sum(getattr(c, field) for (a, p, k, m), c in cells.items() if a == arm and p == "ALL")
    def chain(*fields):
        return " → ".join(" / ".join(str(total(a, f)) for f in fields) for a in [before] + afters)
    S += ["", f"All {tot_scenes} scenes together: found {chain('found')}; right place {chain('place')}; boxes drawn where no barrel is {chain('false')}; "
          f"right-place boxes too small / about right / too big: {chain('small', 'right', 'big')}.", "",
          "Limits: the hiding is done on the segmentation mask (pixels erased, or a real barrel's pixels pasted in front, scaled for its distance). "
          "A real occluder also casts a shadow, reflects, and bleeds color at the seam; none of that is in these numbers. "
          "The real occluded barrels of the train frames are in `real.md`, one by one; every number per pool is in `summary.md`."]
    (out / "scorecard.md").write_text("\n".join(S) + "\n")

    json.dump({"git": bcv.git_hash(), "camera": "AIM_4A8B6118_BOXFIT", "model": str(Path(wb.DEFAULT_MODEL).relative_to(PKG_ROOT)), "seed": SEED,
               "amounts": oc.AMOUNTS, "rows": [k for k, _, _, _ in ROWS], "arms": {a: dataclasses.asdict(occl_arms.ARMS[a]) for a in arms},
               "generator": {"slant_lean": oc.SLANT_LEAN, "side_lower": oc.SIDE_LOWER, "low_lower": oc.LOW_LOWER, "block_shift": oc.BLOCK_SHIFT},
               "sources": {p: [[s.stem, dtp.COLOR_NAMES[s.color], list(s.bbox)] for s in pools[p]] for p in POOLS}, "dropped": dropped},
              (out / "config.json").open("w"), indent=1)
    if not args.no_sheets:
        write_sheets(pools, arms, out)
    print("\n".join(S)); print(); print("\n".join(R[-(len(dict.fromkeys(k[0] for k in tot)) + 3):]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
