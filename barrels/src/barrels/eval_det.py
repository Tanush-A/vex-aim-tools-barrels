"""Detection evaluation (docs/EVAL.md, "Detection metrics"): match predicted barrels to ground-truth
barrels, count hits/misses/false detections per class, and measure how far off the matched boxes,
bottom edges and ground positions are. Two rules, chosen per frame with ``evaluate_frame(..., rule=)``:

* ``"v1"`` (the v1.5 scaffolding; default): greedy by IoU — predictions in confidence order take the best
  still-free ground-truth box of the same class with IoU >= IOU_THR. Ground truth flagged occluded /
  truncated / top_only is "ignored" VOC-style: matching one is not a hit, missing one is not a miss. Any
  false detection on a negative frame disqualifies (``score``).
* ``"v2"`` (EVAL.md "Detection metrics (v2, decided 2026-11-02)"): a prediction is correct iff it has the
  same color as a ground-truth box, IoU >= IOU_THR **and** its bottom edge is within
  max(BOTTOM_TOL_MIN_PX, BOTTOM_TOL_FRAC x gt box height) of the true bottom edge. Matching is greedy over
  the pairs that pass both conditions, highest IoU first. Every ground-truth barrel counts — the flags
  (occluded, truncated, held, bottom_estimated, no_stripe) only split the reporting. Unmatched predictions
  are FP, unmatched truth FN; false detections on negative frames count in the pooled score, and one on a
  *clean* negative frame (label ``clean: true``, no orange/blue clutter) disqualifies.

Reported under both rules: matched-pair IoU; signed bottom-edge error (px and as a fraction of the gt box
height, positive = predicted lower), split by whether the gt box is ``bottom_estimated``; barrel-count error
per frame (n_pred - n_gt); color confusions (class-agnostic IoU matches whose colors differ). A second,
looser criterion counts a prediction as a hit when its projected ground position is within CENTER_TOL_MM of
the ground truth's (kept for the world map; not part of the v2 score). Aggregates: v1 per
light_surface_scene + ALL; v2 per condition (light_surface), per scene tag (``scene:<tag>``) and ALL.
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
RULES = ("v1", "v2")
IOU_THR = 0.5
CENTER_TOL_MM = 15.0                      # = the RRT "skinny" obstacle inflation
IGNORE_FLAGS = ("occluded", "truncated", "top_only")      # v1 only; v2 ignores nothing
BOTTOM_TOL_FRAC = 0.10                    # v2: |pred bottom − gt bottom| ≤ max(BOTTOM_TOL_MIN_PX, BOTTOM_TOL_FRAC × gt height)
BOTTOM_TOL_MIN_PX = 3
CONDITION_KEYS = ("light", "surface", "scene")            # v1 aggregate key
CONDITION_KEYS_V2 = ("light", "surface")                  # v2 condition; the scene tag gets its own "scene:<tag>" aggregate
BOTTOM_CASES = ("seen", "estimated")                      # bottom-error split: gt box without / with the bottom_estimated flag


def box_iou(a: tuple, b: tuple) -> float:
    ax0, ay0, ax1, ay1 = a; bx0, by0, bx1, by1 = b
    iw = max(0, min(ax1, bx1) - max(ax0, bx0)); ih = max(0, min(ay1, by1) - max(ay0, by0))
    inter = iw * ih
    union = (ax1 - ax0) * (ay1 - ay0) + (bx1 - bx0) * (by1 - by0) - inter
    return inter / union if union else 0.0


def bottom_tol_px(gt: Barrel, frac: float = BOTTOM_TOL_FRAC, min_px: float = BOTTOM_TOL_MIN_PX) -> float:
    """v2 bottom-edge tolerance for one ground-truth box: max(min_px, frac × its height)."""
    return max(min_px, frac * gt.height)


def bottom_within_tol(p: Barrel, g: Barrel, frac: float = BOTTOM_TOL_FRAC, min_px: float = BOTTOM_TOL_MIN_PX) -> bool:
    """v2 eligibility: the predicted bottom edge is within bottom_tol_px(g) of the true one (inclusive)."""
    return abs(p.bottom_row - g.bottom_row) <= bottom_tol_px(g, frac, min_px)


def match_greedy(preds: list[Barrel], gts: list[Barrel], score_fn, thr: float, same_class: bool = True) -> list[tuple[int, int, float]]:
    """[(pred_idx, gt_idx, score)]: predictions by confidence desc (ties: larger area first) each take
    the best still-free ground truth with score >= thr. Deterministic. The v1 matcher."""
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


def match_best_first(preds: list[Barrel], gts: list[Barrel], score_fn, thr: float, same_class: bool = True,
                     eligible=None) -> list[tuple[int, int, float]]:
    """[(pred_idx, gt_idx, score)]: every eligible pair (same class when ``same_class``, ``eligible(p, g)``
    true when given, score >= thr) sorted highest score first; a pair is taken when both sides are still
    free. Deterministic (ties: higher confidence, then lower pred index, then lower gt index). The v2 matcher."""
    cand = []
    for pi, p in enumerate(preds):
        for gi, g in enumerate(gts):
            if same_class and p.color != g.color:
                continue
            if eligible is not None and not eligible(p, g):
                continue
            s = score_fn(p, g)
            if s >= thr:
                cand.append((pi, gi, s))
    cand.sort(key=lambda t: (-t[2], -preds[t[0]].confidence, t[0], t[1]))
    free_p, free_g = set(range(len(preds))), set(range(len(gts)))
    out = []
    for pi, gi, s in cand:
        if pi in free_p and gi in free_g:
            free_p.discard(pi); free_g.discard(gi); out.append((pi, gi, s))
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
    bottom_err_frac: float = math.nan     # bottom_row_err_px / gt box height (v2 accepts |·| ≤ BOTTOM_TOL_FRAC, or BOTTOM_TOL_MIN_PX)
    width_ratio: float = math.nan         # pred box width / gt box width (1 = right; the IoU match hides a box 15 % too thin)
    gt_flags: tuple[str, ...] = ()        # the ground truth's flags, sorted — reporting only

    @property
    def bottom_estimated(self) -> bool:
        return "bottom_estimated" in self.gt_flags


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
    rule: str = "v1"
    clean: bool = True            # label-file flag: a negative frame with no orange/blue clutter (v2: a false detection there disqualifies)
    count_err: int = 0            # n_pred − n_gt

    def condition(self) -> str:
        """v1: light_surface_scene (as before). v2: light_surface — the scene is its own aggregate."""
        keys = CONDITION_KEYS if self.rule == "v1" else CONDITION_KEYS_V2
        return "_".join(self.tags.get(k, "?") for k in keys)

    def scene(self) -> str:
        return self.tags.get("scene", "?")

    def aggregate_keys(self) -> tuple[str, ...]:
        """Which ``aggregate`` buckets this frame pools into (v1 unchanged; v2 adds the scene tag)."""
        if self.rule == "v1":
            return (self.condition(), "ALL")
        return (self.condition(), f"scene:{self.scene()}", "ALL")


def _project(b: Barrel, cam: geo.CameraModel) -> tuple[float, float]:
    return cam.barrel_axis_xy(*b.bottom_mid)


def evaluate_frame(name: str, preds: list[Barrel], gts: list[Barrel], cam: geo.CameraModel = geo.NOMINAL,
                   iou_thr: float = IOU_THR, ignore_flags=IGNORE_FLAGS, center_tol_mm: float = CENTER_TOL_MM,
                   rule: str = "v1", clean: bool = True,
                   bottom_tol_frac: float = BOTTOM_TOL_FRAC, bottom_tol_min_px: float = BOTTOM_TOL_MIN_PX) -> DetImageResult:
    """Score one frame under ``rule``. "v1": confidence-ordered greedy IoU matching, gt with any of
    ``ignore_flags`` ignored VOC-style. "v2": highest-IoU-first greedy matching over the pairs that pass
    both IoU >= iou_thr and the bottom-edge tolerance (``bottom_within_tol``); nothing is ignored
    (``ignore_flags`` unused). ``clean`` is the label file's flag and only matters for negative frames
    (v2 disqualification). Color confusions and the loose ground criterion are computed the same way under
    both rules (IoU-only, confidence-ordered; loose respects the v1 ignores)."""
    if rule not in RULES:
        raise ValueError(f"rule must be one of {RULES}, got {rule!r}")
    try:
        tags = parse_name(name)
    except ValueError:
        tags = {}
    iou_fn = lambda p, g: box_iou(p.bbox, g.bbox)  # noqa: E731
    if rule == "v1":
        ignored = [bool(set(g.flags) & set(ignore_flags)) for g in gts]
        pairs = match_greedy(preds, gts, iou_fn, iou_thr, same_class=True)
    else:
        ignored = [False] * len(gts)
        pairs = match_best_first(preds, gts, iou_fn, iou_thr, same_class=True,
                                 eligible=lambda p, g: bottom_within_tol(p, g, bottom_tol_frac, bottom_tol_min_px))
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
        b_err = p.bottom_row - g.bottom_row
        matches.append(Match(gi, pi, g.color, iou, b_err,
                             math.hypot(p.bottom_mid[0] - g.bottom_mid[0], p.bottom_mid[1] - g.bottom_mid[1]),
                             proj, meas, px - gx if math.isfinite(proj) else math.nan, py - gy if math.isfinite(proj) else math.nan,
                             bottom_err_frac=b_err / g.height, gt_flags=tuple(sorted(g.flags)), width_ratio=p.width / max(1, g.width)))
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
    agn = match_greedy(preds, gts, iou_fn, iou_thr, same_class=False)
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
                          unmatched_pred=[pi for pi in range(len(preds)) if pi not in matched_p],
                          rule=rule, clean=bool(clean), count_err=len(preds) - len(gts))


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


def rule_of(results: list[DetImageResult]) -> str:
    """The rule the results were scored under ("v1" when empty). Raises ValueError when they mix rules."""
    rules = {r.rule for r in results}
    if len(rules) > 1:
        raise ValueError(f"results mix rules {sorted(rules)}; score each rule separately")
    return rules.pop() if rules else "v1"


@dataclass
class DetAggregate:
    key: str
    n_frames: int = 0
    n_negative: int = 0
    n_clean_negative: int = 0
    counts: dict = field(default_factory=lambda: {c: {"tp": 0, "fp": 0, "fn": 0, "ign": 0, "tp_l": 0, "fp_l": 0, "fn_l": 0, "n_gt": 0} for c in CLASSES})
    neg_false_detections: int = 0           # false detections on negative frames (v1: > 0 disqualifies)
    neg_clean_false_detections: int = 0     # … on *clean* negative frames (v2: > 0 disqualifies)
    color_confusions: int = 0
    ious: list = field(default_factory=list)
    bottom_errs: list = field(default_factory=list)          # px, all matches
    bottom_fracs: list = field(default_factory=list)         # bottom_err / gt height, all matches
    width_ratios: list = field(default_factory=list)         # pred width / gt width, all matches
    bottom_by_case: dict = field(default_factory=lambda: {k: {"px": [], "frac": []} for k in BOTTOM_CASES})
    count_errs: list = field(default_factory=list)           # one per frame: n_pred − n_gt
    ground_proj: list = field(default_factory=list)
    ground_meas: list = field(default_factory=list)

    def prf(self, c: int, loose: bool = False) -> tuple[float, float, float]:
        k = self.counts[c]
        return _prf(k["tp_l"], k["fp_l"], k["fn_l"]) if loose else _prf(k["tp"], k["fp"], k["fn"])


def aggregate(results: list[DetImageResult]) -> dict[str, DetAggregate]:
    """Pool frames into ``DetAggregate`` buckets keyed per ``DetImageResult.aggregate_keys`` — "ALL" first,
    then conditions, then (v2) the ``scene:<tag>`` buckets, each alphabetical."""
    aggs: dict[str, DetAggregate] = {}
    for r in results:
        for key in r.aggregate_keys():
            a = aggs.setdefault(key, DetAggregate(key))
            a.n_frames += 1
            if r.negative:
                a.n_negative += 1
                a.neg_false_detections += sum(r.fp.values())
                if r.clean:
                    a.n_clean_negative += 1
                    a.neg_clean_false_detections += sum(r.fp.values())
            for c in CLASSES:
                k = a.counts[c]
                k["tp"] += r.tp[c]; k["fp"] += r.fp[c]; k["fn"] += r.fn[c]; k["ign"] += r.n_ignored[c]; k["n_gt"] += r.n_gt[c]
                k["tp_l"] += r.tp_loose[c]; k["fp_l"] += r.fp_loose[c]; k["fn_l"] += r.fn_loose[c]
            a.color_confusions += r.color_confusions
            a.count_errs.append(r.count_err)
            for m in r.matches:
                a.ious.append(m.iou); a.bottom_errs.append(m.bottom_row_err_px); a.bottom_fracs.append(m.bottom_err_frac)
                a.width_ratios.append(m.width_ratio)
                case = a.bottom_by_case["estimated" if m.bottom_estimated else "seen"]
                case["px"].append(m.bottom_row_err_px); case["frac"].append(m.bottom_err_frac)
                a.ground_proj.append(m.ground_err_proj_mm); a.ground_meas.append(m.ground_err_mm)
    return dict(sorted(aggs.items(), key=lambda kv: (kv[0] != "ALL", kv[0].startswith("scene:"), kv[0])))


def _f(x) -> str:
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.3f}"


def _rule_text(rule: str) -> str:
    if rule == "v1":
        return (f"Rule **v1**: greedy class-aware matching (confidence order) at IoU ≥ {IOU_THR}; GT flagged {', '.join(IGNORE_FLAGS)} is ignored; "
                f"any false detection on a negative frame disqualifies.")
    return (f"Rule **v2** (EVAL.md 2026-11-02): greedy class-aware matching, highest IoU first, over pairs with IoU ≥ {IOU_THR} and "
            f"|bottom-edge error| ≤ max({BOTTOM_TOL_MIN_PX:g} px, {BOTTOM_TOL_FRAC:.0%} of the GT box height); every GT barrel counts (no ignores); "
            f"a false detection on a *clean* negative frame disqualifies.")


def write_results(results: list[DetImageResult], out_dir: Path | str, title: str = "") -> tuple[Path, Path, Path]:
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    rule = rule_of(results)
    aggs = aggregate(results)
    per_image = out_dir / "per_image.csv"
    with per_image.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "condition", "negative"] + [f"{NAMES[c]}_{m}" for c in CLASSES for m in ("n_gt", "tp", "fp", "fn", "ignored", "tp_loose", "fp_loose", "fn_loose")]
                   + ["color_confusions", "scene", "clean", "count_err"])
        for r in results:
            w.writerow([r.name, r.condition(), int(r.negative)] + [v for c in CLASSES for v in (r.n_gt[c], r.tp[c], r.fp[c], r.fn[c], r.n_ignored[c], r.tp_loose[c], r.fp_loose[c], r.fn_loose[c])]
                       + [r.color_confusions, r.scene(), int(r.clean), r.count_err])
    per_barrel = out_dir / "per_barrel.csv"
    with per_barrel.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "kind", "color", "gt_idx", "pred_idx", "iou", "bottom_row_err_px", "bottom_mid_err_px", "ground_err_proj_mm", "ground_err_mm", "range_err_mm", "lateral_err_mm", "bottom_err_frac", "width_ratio", "gt_flags"])
        for r in results:
            for m in r.matches:
                w.writerow([r.name, "match", NAMES[m.color], m.gt_idx, m.pred_idx, f"{m.iou:.4f}", f"{m.bottom_row_err_px:.1f}", f"{m.bottom_mid_err_px:.1f}", _f(m.ground_err_proj_mm), _f(m.ground_err_mm), _f(m.range_err_mm), _f(m.lateral_err_mm),
                            _f(m.bottom_err_frac), _f(m.width_ratio), " ".join(m.gt_flags)])
            for gi in r.unmatched_gt:
                w.writerow([r.name, "miss", "", gi, "", "", "", "", "", "", "", "", "", "", ""])
            for pi in r.unmatched_pred:
                w.writerow([r.name, "false", "", "", pi, "", "", "", "", "", "", "", "", ""])
    summary_csv = out_dir / "summary.csv"
    with summary_csv.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["condition", "n_frames", "n_neg", "neg_false_detections"] + [f"{NAMES[c]}_{m}" for c in CLASSES for m in ("n_gt", "P", "R", "F1", "P_loose", "R_loose")]
                   + ["mean_iou", "bottom_err_median_px", "bottom_err_p90_px", "ground_proj_median_mm", "ground_meas_median_mm", "ground_meas_n", "color_confusions",
                      "bottom_err_frac_median", "bottom_seen_median_px", "bottom_seen_n", "bottom_est_median_px", "bottom_est_n", "count_err_mean", "count_err_mean_abs",
                      "n_clean_neg", "neg_clean_false_detections", "rule"])
        for a in aggs.values():
            row = [a.key, a.n_frames, a.n_negative, a.neg_false_detections]
            for c in CLASSES:
                p, r_, f = a.prf(c); pl, rl, _ = a.prf(c, loose=True)
                row += [a.counts[c]["n_gt"], _f(p), _f(r_), _f(f), _f(pl), _f(rl)]
            be, gp, gm = _stats(a.bottom_errs), _stats(a.ground_proj), _stats(a.ground_meas)
            bf, bs, be_, ce = _stats(a.bottom_fracs), _stats(a.bottom_by_case["seen"]["px"]), _stats(a.bottom_by_case["estimated"]["px"]), _stats(a.count_errs)
            row += [_f(float(np.mean(a.ious)) if a.ious else math.nan), _f(be["median"]), _f(be["p90"]), _f(gp["median"]), _f(gm["median"]), gm["n"], a.color_confusions,
                    _f(bf["median"]), _f(bs["median"]), bs["n"], _f(be_["median"]), be_["n"], _f(ce["mean"]), _f(ce["mean_abs"]), a.n_clean_negative, a.neg_clean_false_detections, rule]
            w.writerow(row)
    md = out_dir / "summary.md"
    lines = [f"# {title or out_dir.name}", "",
             f"Detection metrics (EVAL.md). {_rule_text(rule)} Loose = projected ground position within {CENTER_TOL_MM:g} mm (not part of the v2 score). "
             f"Errors are over matched pairs (|·| median / p90); bottom err seen · est. splits them by the GT box's bottom_estimated flag; count err = n_pred − n_gt per frame.", "",
             "| condition | frames (neg, clean) | neg false det (on clean) | orange n / P / R / F1 | blue n / P / R / F1 | loose P/R o · b | mean IoU | bottom err px | bottom err seen · est. px (n) | bottom err frac | width ratio median (min) | count err mean (abs) | ground proj mm | ground meas mm (n) | color conf |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for a in aggs.values():
        po, ro, fo = a.prf(ORANGE); pb, rb, fb = a.prf(BLUE)
        plo, rlo, _ = a.prf(ORANGE, True); plb, rlb, _ = a.prf(BLUE, True)
        be, gp, gm = _stats(a.bottom_errs), _stats(a.ground_proj), _stats(a.ground_meas)
        bf, bs, bst, ce = _stats(a.bottom_fracs), _stats(a.bottom_by_case["seen"]["px"]), _stats(a.bottom_by_case["estimated"]["px"]), _stats(a.count_errs)
        wr = [x for x in a.width_ratios if math.isfinite(x)]
        wr_s = f"{_f(float(np.median(wr)))} ({_f(min(wr))})" if wr else "—"
        lines.append(f"| {a.key} | {a.n_frames} ({a.n_negative}, {a.n_clean_negative}) | {a.neg_false_detections} ({a.neg_clean_false_detections}) | "
                     f"{a.counts[ORANGE]['n_gt']} / {_f(po)} / {_f(ro)} / {_f(fo)} | {a.counts[BLUE]['n_gt']} / {_f(pb)} / {_f(rb)} / {_f(fb)} | "
                     f"{_f(plo)}/{_f(rlo)} · {_f(plb)}/{_f(rlb)} | {_f(float(np.mean(a.ious)) if a.ious else math.nan)} | {_f(be['median'])} / {_f(be['p90'])} | "
                     f"{_f(bs['median'])} ({bs['n']}) · {_f(bst['median'])} ({bst['n']}) | {_f(bf['median'])} | {wr_s} | {_f(ce['mean'])} ({_f(ce['mean_abs'])}) | "
                     f"{_f(gp['median'])} / {_f(gp['p90'])} | {_f(gm['median'])} ({gm['n']}) | {a.color_confusions} |")
    lines += ["", "Per-image counts: `per_image.csv`; every match/miss/false: `per_barrel.csv`.", ""]
    md.write_text("\n".join(lines))
    return md, summary_csv, per_image


def score(results: list[DetImageResult], scenes: dict[str, str], out_scope: tuple[str, ...] = ("top", "topstripe"),
          rule: str | None = None) -> dict:
    """Flat dict for sweeps: primary = mean F1@rule over classes on in-scope frames (pooled). ``disqualified``
    = a false detection on a negative frame — any negative frame under v1, a *clean* one under v2. The
    rule is read from the results unless given (mixed rules raise)."""
    rule = rule or rule_of(results)
    in_scope = [r for r in results if scenes.get(r.name, "") not in out_scope]
    a = aggregate(in_scope).get("ALL", DetAggregate("ALL"))
    s: dict = {"rule": rule}
    for c, nm in ((ORANGE, "o"), (BLUE, "b")):
        p, r, f = a.prf(c); pl, rl, fl = a.prf(c, True)
        s[f"P_{nm}"], s[f"R_{nm}"], s[f"F1_{nm}"], s[f"F1loose_{nm}"] = p, r, f, fl
    s["primary"] = float(np.nanmean([s["F1_o"], s["F1_b"]]))
    s["neg_false_detections"] = a.neg_false_detections
    s["neg_clean_false_detections"] = a.neg_clean_false_detections
    s["mean_iou"] = float(np.mean(a.ious)) if a.ious else math.nan
    s["bottom_err_median_px"] = _stats(a.bottom_errs)["median"]
    s["bottom_err_frac_median"] = _stats(a.bottom_fracs)["median"]
    wr = [x for x in a.width_ratios if math.isfinite(x)]
    s["width_ratio_median"] = float(np.median(wr)) if wr else math.nan
    s["width_ratio_min"] = float(min(wr)) if wr else math.nan
    s["bottom_err_seen_median_px"] = _stats(a.bottom_by_case["seen"]["px"])["median"]
    s["bottom_err_est_median_px"] = _stats(a.bottom_by_case["estimated"]["px"])["median"]
    s["count_err_mean"] = _stats(a.count_errs)["mean"]
    s["count_err_mean_abs"] = _stats(a.count_errs)["mean_abs"]
    s["ground_proj_median_mm"] = _stats(a.ground_proj)["median"]
    s["ground_meas_median_mm"] = _stats(a.ground_meas)["median"]
    s["color_confusions"] = a.color_confusions
    s["disqualified"] = (a.neg_clean_false_detections if rule == "v2" else a.neg_false_detections) > 0
    return s
