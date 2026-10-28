"""Detection evaluation (docs/EVAL.md, "Detection metrics"): match predicted barrels to ground-truth
barrels, count hits/misses/false detections per class, and measure how far off the matched boxes,
bottom edges and ground positions are.

Matching is greedy by IoU (predictions in confidence order take the best free ground-truth box of
the same class with IoU >= IOU_THR). Ground-truth barrels flagged occluded / truncated / top_only
are "ignored" VOC-style: matching one is not a hit, missing one is not a miss. A second, looser
criterion counts a prediction as a hit when its projected ground position is within
CENTER_TOL_MM of the ground truth's (what the planner cares about).
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from . import geometry as geo
from .detect_types import Barrel
from .io import BLUE, ORANGE, parse_name

CLASSES = (ORANGE, BLUE)
NAMES = {ORANGE: "orange", BLUE: "blue"}
IOU_THR = 0.5
CENTER_TOL_MM = 15.0                      # = the RRT "skinny" obstacle inflation
IGNORE_FLAGS = ("occluded", "truncated", "top_only")
CONDITION_KEYS = ("light", "surface", "scene")


def box_iou(a: tuple, b: tuple) -> float:
    ax0, ay0, ax1, ay1 = a; bx0, by0, bx1, by1 = b
    iw = max(0, min(ax1, bx1) - max(ax0, bx0)); ih = max(0, min(ay1, by1) - max(ay0, by0))
    inter = iw * ih
    union = (ax1 - ax0) * (ay1 - ay0) + (bx1 - bx0) * (by1 - by0) - inter
    return inter / union if union else 0.0


def match_greedy(preds: list[Barrel], gts: list[Barrel], score_fn, thr: float, same_class: bool = True) -> list[tuple[int, int, float]]:
    """[(pred_idx, gt_idx, score)]: predictions by confidence desc (ties: larger area first) each take
    the best still-free ground truth with score >= thr. Deterministic."""
    order = sorted(range(len(preds)), key=lambda i: (-preds[i].confidence, -preds[i].width * preds[i].height, i))
    free = set(range(len(gts)))
    out = []
    for pi in order:
        best, best_s = None, thr
        for gi in free:
            if same_class and preds[pi].color != gts[gi].color:
                continue
            s = score_fn(preds[pi], gts[gi])
            if s >= best_s and (best is None or s > best_s):
                best, best_s = gi, s
        if best is not None:
            free.discard(best); out.append((pi, best, best_s))
    return out


@dataclass(frozen=True)
class Match:
    gt_idx: int
    pred_idx: int
    color: int
    iou: float
    bottom_row_err_px: float      # pred bottom row − gt bottom row (positive = predicted lower)
    bottom_mid_err_px: float      # Euclidean distance between bottom-mid points
    ground_err_proj_mm: float     # both bottom-mids projected through the same camera (every frame)
    ground_err_mm: float          # vs the measured ground truth position, nan if none
    range_err_mm: float           # projected: pred x − gt x (forward)
    lateral_err_mm: float         # projected: pred y − gt y (left)


@dataclass
class DetImageResult:
    name: str
    tags: dict
    negative: bool
    n_gt: dict[int, int]
    tp: dict[int, int]
    fp: dict[int, int]
    fn: dict[int, int]
    n_ignored: dict[int, int]
    tp_loose: dict[int, int]
    fp_loose: dict[int, int]
    fn_loose: dict[int, int]
    color_confusions: int
    matches: list[Match] = field(default_factory=list)
    unmatched_gt: list[int] = field(default_factory=list)
    unmatched_pred: list[int] = field(default_factory=list)

    def condition(self) -> str:
        return "_".join(self.tags.get(k, "?") for k in CONDITION_KEYS)


def _project(b: Barrel, cam: geo.CameraModel) -> tuple[float, float]:
    return cam.barrel_axis_xy(*b.bottom_mid)


def evaluate_frame(name: str, preds: list[Barrel], gts: list[Barrel], cam: geo.CameraModel = geo.NOMINAL,
                   iou_thr: float = IOU_THR, ignore_flags=IGNORE_FLAGS, center_tol_mm: float = CENTER_TOL_MM) -> DetImageResult:
    try:
        tags = parse_name(name)
    except ValueError:
        tags = {}
    ignored = [bool(set(g.flags) & set(ignore_flags)) for g in gts]
    # strict: IoU, class-aware
    pairs = match_greedy(preds, gts, lambda p, g: box_iou(p.bbox, g.bbox), iou_thr, same_class=True)
    matched_p = {pi for pi, _, _ in pairs}; matched_g = {gi for _, gi, _ in pairs}
    tp = {c: 0 for c in CLASSES}; fp = {c: 0 for c in CLASSES}; fn = {c: 0 for c in CLASSES}; n_ign = {c: 0 for c in CLASSES}
    n_gt = {c: sum(1 for g in gts if g.color == c) for c in CLASSES}
    matches = []
    for pi, gi, iou in pairs:
        p, g = preds[pi], gts[gi]
        if ignored[gi]:
            n_ign[g.color] += 1
        else:
            tp[g.color] += 1
        px, py = _project(p, cam); gx, gy = _project(g, cam)
        proj = math.hypot(px - gx, py - gy) if all(map(math.isfinite, (px, py, gx, gy))) else math.nan
        meas = math.nan
        if g.ground_xy_mm is not None and math.isfinite(px) and math.isfinite(py):
            meas = math.hypot(px - g.ground_xy_mm[0], py - g.ground_xy_mm[1])
        matches.append(Match(gi, pi, g.color, iou, p.bottom_row - g.bottom_row,
                             math.hypot(p.bottom_mid[0] - g.bottom_mid[0], p.bottom_mid[1] - g.bottom_mid[1]),
                             proj, meas, px - gx if math.isfinite(proj) else math.nan, py - gy if math.isfinite(proj) else math.nan))
    for gi, g in enumerate(gts):
        if gi not in matched_g:
            if ignored[gi]:
                n_ign[g.color] += 1
            else:
                fn[g.color] += 1
    for pi, p in enumerate(preds):
        if pi not in matched_p:
            fp[p.color] += 1
    # color confusions: class-agnostic IoU match whose colors differ
    agn = match_greedy(preds, gts, lambda p, g: box_iou(p.bbox, g.bbox), iou_thr, same_class=False)
    confusions = sum(1 for pi, gi, _ in agn if preds[pi].color != gts[gi].color)
    # loose: projected ground distance within tolerance, class-aware
    def close(p: Barrel, g: Barrel) -> float:
        px, py = _project(p, cam); gx, gy = _project(g, cam)
        if not all(map(math.isfinite, (px, py, gx, gy))):
            return 0.0
        d = math.hypot(px - gx, py - gy)
        return 1.0 - d / center_tol_mm if d <= center_tol_mm else 0.0
    loose = match_greedy(preds, gts, close, 1e-9, same_class=True)
    lm_p = {pi for pi, _, _ in loose}; lm_g = {gi for _, gi, _ in loose}
    tp_l = {c: 0 for c in CLASSES}; fp_l = {c: 0 for c in CLASSES}; fn_l = {c: 0 for c in CLASSES}
    for pi, gi, _ in loose:
        if not ignored[gi]:
            tp_l[gts[gi].color] += 1
    for gi, g in enumerate(gts):
        if gi not in lm_g and not ignored[gi]:
            fn_l[g.color] += 1
    for pi, p in enumerate(preds):
        if pi not in lm_p:
            fp_l[p.color] += 1
    return DetImageResult(name=name, tags=tags, negative=(len(gts) == 0), n_gt=n_gt, tp=tp, fp=fp, fn=fn, n_ignored=n_ign,
                          tp_loose=tp_l, fp_loose=fp_l, fn_loose=fn_l, color_confusions=confusions, matches=matches,
                          unmatched_gt=[gi for gi in range(len(gts)) if gi not in matched_g],
                          unmatched_pred=[pi for pi in range(len(preds)) if pi not in matched_p])


# ---------------------------------------------------------------- aggregation

def _prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    p = tp / (tp + fp) if tp + fp else math.nan
    r = tp / (tp + fn) if tp + fn else math.nan
    f = 2 * p * r / (p + r) if (not math.isnan(p) and not math.isnan(r) and p + r) else (0.0 if (tp + fp + fn) else math.nan)
    return p, r, f


def _stats(values: list[float]) -> dict:
    v = np.array([x for x in values if x is not None and not math.isnan(x)], float)
    if v.size == 0:
        return {"n": 0, "mean": math.nan, "mean_abs": math.nan, "median": math.nan, "p90": math.nan}
    return {"n": int(v.size), "mean": float(v.mean()), "mean_abs": float(np.abs(v).mean()), "median": float(np.median(np.abs(v))), "p90": float(np.percentile(np.abs(v), 90))}


@dataclass
class DetAggregate:
    key: str
    n_frames: int = 0
    n_negative: int = 0
    counts: dict = field(default_factory=lambda: {c: {"tp": 0, "fp": 0, "fn": 0, "ign": 0, "tp_l": 0, "fp_l": 0, "fn_l": 0, "n_gt": 0} for c in CLASSES})
    neg_false_detections: int = 0
    color_confusions: int = 0
    ious: list = field(default_factory=list)
    bottom_errs: list = field(default_factory=list)
    ground_proj: list = field(default_factory=list)
    ground_meas: list = field(default_factory=list)

    def prf(self, c: int, loose: bool = False) -> tuple[float, float, float]:
        k = self.counts[c]
        return _prf(k["tp_l"], k["fp_l"], k["fn_l"]) if loose else _prf(k["tp"], k["fp"], k["fn"])


def aggregate(results: list[DetImageResult]) -> dict[str, DetAggregate]:
    aggs: dict[str, DetAggregate] = {}
    for r in results:
        for key in (r.condition(), "ALL"):
            a = aggs.setdefault(key, DetAggregate(key))
            a.n_frames += 1
            if r.negative:
                a.n_negative += 1
                a.neg_false_detections += sum(r.fp.values())
            for c in CLASSES:
                k = a.counts[c]
                k["tp"] += r.tp[c]; k["fp"] += r.fp[c]; k["fn"] += r.fn[c]; k["ign"] += r.n_ignored[c]; k["n_gt"] += r.n_gt[c]
                k["tp_l"] += r.tp_loose[c]; k["fp_l"] += r.fp_loose[c]; k["fn_l"] += r.fn_loose[c]
            a.color_confusions += r.color_confusions
            for m in r.matches:
                a.ious.append(m.iou); a.bottom_errs.append(m.bottom_row_err_px)
                a.ground_proj.append(m.ground_err_proj_mm); a.ground_meas.append(m.ground_err_mm)
    return dict(sorted(aggs.items(), key=lambda kv: (kv[0] != "ALL", kv[0])))


def _f(x) -> str:
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.3f}"


def write_results(results: list[DetImageResult], out_dir: Path | str, title: str = "") -> tuple[Path, Path, Path]:
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    aggs = aggregate(results)
    per_image = out_dir / "per_image.csv"
    with per_image.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "condition", "negative"] + [f"{NAMES[c]}_{m}" for c in CLASSES for m in ("n_gt", "tp", "fp", "fn", "ignored", "tp_loose", "fp_loose", "fn_loose")] + ["color_confusions"])
        for r in results:
            w.writerow([r.name, r.condition(), int(r.negative)] + [v for c in CLASSES for v in (r.n_gt[c], r.tp[c], r.fp[c], r.fn[c], r.n_ignored[c], r.tp_loose[c], r.fp_loose[c], r.fn_loose[c])] + [r.color_confusions])
    per_barrel = out_dir / "per_barrel.csv"
    with per_barrel.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "kind", "color", "gt_idx", "pred_idx", "iou", "bottom_row_err_px", "bottom_mid_err_px", "ground_err_proj_mm", "ground_err_mm", "range_err_mm", "lateral_err_mm"])
        for r in results:
            for m in r.matches:
                w.writerow([r.name, "match", NAMES[m.color], m.gt_idx, m.pred_idx, f"{m.iou:.4f}", f"{m.bottom_row_err_px:.1f}", f"{m.bottom_mid_err_px:.1f}", _f(m.ground_err_proj_mm), _f(m.ground_err_mm), _f(m.range_err_mm), _f(m.lateral_err_mm)])
            for gi in r.unmatched_gt:
                w.writerow([r.name, "miss", "", gi, "", "", "", "", "", "", "", ""])
            for pi in r.unmatched_pred:
                w.writerow([r.name, "false", "", "", pi, "", "", "", "", "", "", ""])
    summary_csv = out_dir / "summary.csv"
    with summary_csv.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["condition", "n_frames", "n_neg", "neg_false_detections"] + [f"{NAMES[c]}_{m}" for c in CLASSES for m in ("n_gt", "P", "R", "F1", "P_loose", "R_loose")] + ["mean_iou", "bottom_err_median_px", "bottom_err_p90_px", "ground_proj_median_mm", "ground_meas_median_mm", "ground_meas_n", "color_confusions"])
        for a in aggs.values():
            row = [a.key, a.n_frames, a.n_negative, a.neg_false_detections]
            for c in CLASSES:
                p, r_, f = a.prf(c); pl, rl, _ = a.prf(c, loose=True)
                row += [a.counts[c]["n_gt"], _f(p), _f(r_), _f(f), _f(pl), _f(rl)]
            be, gp, gm = _stats(a.bottom_errs), _stats(a.ground_proj), _stats(a.ground_meas)
            row += [_f(float(np.mean(a.ious)) if a.ious else math.nan), _f(be["median"]), _f(be["p90"]), _f(gp["median"]), _f(gm["median"]), gm["n"], a.color_confusions]
            w.writerow(row)
    md = out_dir / "summary.md"
    lines = [f"# {title or out_dir.name}", "",
             f"Detection metrics (EVAL.md): greedy class-aware matching at IoU ≥ {IOU_THR}; GT flagged {', '.join(IGNORE_FLAGS)} is ignored; "
             f"loose = projected ground position within {CENTER_TOL_MM:g} mm. Errors are over matched pairs (|·| median / p90).", "",
             "| condition | frames (neg) | neg false det | orange n / P / R / F1 | blue n / P / R / F1 | loose P/R o · b | mean IoU | bottom err px | ground proj mm | ground meas mm (n) | color conf |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for a in aggs.values():
        po, ro, fo = a.prf(ORANGE); pb, rb, fb = a.prf(BLUE)
        plo, rlo, _ = a.prf(ORANGE, True); plb, rlb, _ = a.prf(BLUE, True)
        be, gp, gm = _stats(a.bottom_errs), _stats(a.ground_proj), _stats(a.ground_meas)
        lines.append(f"| {a.key} | {a.n_frames} ({a.n_negative}) | {a.neg_false_detections} | {a.counts[ORANGE]['n_gt']} / {_f(po)} / {_f(ro)} / {_f(fo)} | {a.counts[BLUE]['n_gt']} / {_f(pb)} / {_f(rb)} / {_f(fb)} | "
                     f"{_f(plo)}/{_f(rlo)} · {_f(plb)}/{_f(rlb)} | {_f(float(np.mean(a.ious)) if a.ious else math.nan)} | {_f(be['median'])} / {_f(be['p90'])} | {_f(gp['median'])} / {_f(gp['p90'])} | {_f(gm['median'])} ({gm['n']}) | {a.color_confusions} |")
    lines += ["", "Per-image counts: `per_image.csv`; every match/miss/false: `per_barrel.csv`.", ""]
    md.write_text("\n".join(lines))
    return md, summary_csv, per_image


def score(results: list[DetImageResult], scenes: dict[str, str], out_scope: tuple[str, ...] = ("top", "topstripe")) -> dict:
    """Flat dict for sweeps: primary = mean F1@IoU over classes on in-scope frames; any false detection
    on a negative frame disqualifies."""
    in_scope = [r for r in results if scenes.get(r.name, "") not in out_scope]
    a = aggregate(in_scope).get("ALL", DetAggregate("ALL"))
    s: dict = {}
    for c, nm in ((ORANGE, "o"), (BLUE, "b")):
        p, r, f = a.prf(c); pl, rl, fl = a.prf(c, True)
        s[f"P_{nm}"], s[f"R_{nm}"], s[f"F1_{nm}"], s[f"F1loose_{nm}"] = p, r, f, fl
    s["primary"] = float(np.nanmean([s["F1_o"], s["F1_b"]]))
    s["neg_false_detections"] = a.neg_false_detections
    s["mean_iou"] = float(np.mean(a.ious)) if a.ious else math.nan
    s["bottom_err_median_px"] = _stats(a.bottom_errs)["median"]
    s["ground_proj_median_mm"] = _stats(a.ground_proj)["median"]
    s["ground_meas_median_mm"] = _stats(a.ground_meas)["median"]
    s["color_confusions"] = a.color_confusions
    s["disqualified"] = a.neg_false_detections > 0
    return s
