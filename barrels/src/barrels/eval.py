"""Per-pixel evaluation per docs/EVAL.md.

Classes scored: ORANGE and BLUE. Pixels with ground truth IGNORE (255) are excluded
from every count. Frames whose ground truth has no barrel pixels are "negative" frames:
they get a false-positive rate per class instead of P/R/IoU, and are kept out of the
P/R/IoU aggregates.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .io import BLUE, CLASS_NAMES, IGNORE, ORANGE, parse_name

CLASSES = (ORANGE, BLUE)
CONDITION_KEYS = ("light", "surface", "scene")


@dataclass
class Counts:
    tp: int = 0
    fp: int = 0
    fn: int = 0
    tn: int = 0

    def __add__(self, o: "Counts") -> "Counts":
        return Counts(self.tp + o.tp, self.fp + o.fp, self.fn + o.fn, self.tn + o.tn)

    @property
    def valid(self) -> int:
        return self.tp + self.fp + self.fn + self.tn

    @property
    def precision(self) -> float:
        d = self.tp + self.fp
        return self.tp / d if d else math.nan

    @property
    def recall(self) -> float:
        d = self.tp + self.fn
        return self.tp / d if d else math.nan

    @property
    def iou(self) -> float:
        d = self.tp + self.fp + self.fn
        return self.tp / d if d else math.nan

    @property
    def fp_rate(self) -> float:
        """Fraction of valid pixels flagged as this class — the negative-frame metric."""
        return (self.tp + self.fp) / self.valid if self.valid else math.nan


def confusion(pred: np.ndarray, gt: np.ndarray) -> dict[int, Counts]:
    """Per-class counts over pixels where gt != IGNORE. pred must not contain IGNORE."""
    if pred.shape != gt.shape:
        raise ValueError(f"pred {pred.shape} and gt {gt.shape} differ in shape")
    if (pred == IGNORE).any():
        raise ValueError("prediction masks must not contain IGNORE (255)")
    valid = gt != IGNORE
    out = {}
    for c in CLASSES:
        p = (pred == c) & valid
        g = (gt == c) & valid
        out[c] = Counts(
            tp=int((p & g).sum()),
            fp=int((p & ~g).sum()),
            fn=int((~p & g).sum()),
            tn=int((~p & ~g & valid).sum()),
        )
    return out


def is_negative(gt: np.ndarray) -> bool:
    return not np.isin(gt, CLASSES).any()


@dataclass
class ImageResult:
    name: str
    tags: dict[str, str]
    negative: bool
    counts: dict[int, Counts]

    def condition(self) -> str:
        return "_".join(self.tags.get(k, "?") for k in CONDITION_KEYS)


def evaluate_image(name: str, pred: np.ndarray, gt: np.ndarray) -> ImageResult:
    try:
        tags = parse_name(name)
    except ValueError:
        tags = {}
    return ImageResult(name=name, tags=tags, negative=is_negative(gt), counts=confusion(pred, gt))


@dataclass
class Aggregate:
    key: str
    n_positive: int = 0
    n_negative: int = 0
    pos: dict[int, Counts] = field(default_factory=lambda: {c: Counts() for c in CLASSES})
    neg: dict[int, Counts] = field(default_factory=lambda: {c: Counts() for c in CLASSES})


def aggregate(results: list[ImageResult]) -> dict[str, Aggregate]:
    """Micro-average per condition (light_surface_scene) plus 'ALL'. Pools pixel counts."""
    aggs: dict[str, Aggregate] = {}
    for r in results:
        for key in (r.condition(), "ALL"):
            a = aggs.setdefault(key, Aggregate(key))
            if r.negative:
                a.n_negative += 1
                for c in CLASSES:
                    a.neg[c] = a.neg[c] + r.counts[c]
            else:
                a.n_positive += 1
                for c in CLASSES:
                    a.pos[c] = a.pos[c] + r.counts[c]
    return dict(sorted(aggs.items(), key=lambda kv: (kv[0] != "ALL", kv[0])))


def _fmt(x: float) -> str:
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.3f}"


def write_results(results: list[ImageResult], out_dir: Path | str, title: str = "") -> tuple[Path, Path]:
    """Write per_image.csv and summary.md (+ summary.csv). Returns (summary_md, per_image_csv)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    aggs = aggregate(results)

    per_image = out_dir / "per_image.csv"
    with per_image.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "condition", "negative"] + [
            f"{CLASS_NAMES[c]}_{m}" for c in CLASSES for m in ("tp", "fp", "fn", "precision", "recall", "iou", "fp_rate")])
        for r in results:
            row = [r.name, r.condition(), int(r.negative)]
            for c in CLASSES:
                k = r.counts[c]
                row += [k.tp, k.fp, k.fn, _fmt(k.precision), _fmt(k.recall), _fmt(k.iou), _fmt(k.fp_rate)]
            w.writerow(row)

    summary_csv = out_dir / "summary.csv"
    with summary_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["condition", "n_pos", "n_neg"] + [
            f"{CLASS_NAMES[c]}_{m}" for c in CLASSES for m in ("precision", "recall", "iou", "neg_fp_rate")])
        for a in aggs.values():
            row = [a.key, a.n_positive, a.n_negative]
            for c in CLASSES:
                row += [_fmt(a.pos[c].precision), _fmt(a.pos[c].recall), _fmt(a.pos[c].iou), _fmt(a.neg[c].fp_rate)]
            w.writerow(row)

    summary_md = out_dir / "summary.md"
    lines = [f"# {title or out_dir.name}", "",
             "Per-pixel micro-average per condition; IGNORE pixels excluded. "
             "`neg fp` = fraction of pixels flagged on frames with no barrels (target ≈ 0).", "",
             "| condition | n pos | n neg | orange P | orange R | orange IoU | blue P | blue R | blue IoU | orange neg fp | blue neg fp |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for a in aggs.values():
        o, b = a.pos[ORANGE], a.pos[BLUE]
        lines.append(f"| {a.key} | {a.n_positive} | {a.n_negative} | {_fmt(o.precision)} | {_fmt(o.recall)} | {_fmt(o.iou)} "
                     f"| {_fmt(b.precision)} | {_fmt(b.recall)} | {_fmt(b.iou)} | {_fmt(a.neg[ORANGE].fp_rate)} | {_fmt(a.neg[BLUE].fp_rate)} |")
    lines += ["", f"Per-image numbers: `{per_image.name}`.", ""]
    summary_md.write_text("\n".join(lines))
    return summary_md, per_image
