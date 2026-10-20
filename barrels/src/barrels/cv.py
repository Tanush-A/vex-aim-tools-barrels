"""Leave-one-scene-out cross-validation, parameter sweeps, and result writing (docs/EVAL.md).

Every pool frame is predicted exactly once, by a model fit on the frames of all *other* scenes.
Scores follow EVAL.md: pooled (micro) per-class IoU over in-scope positive frames, per-fold
spread, negative-frame false-positive rate, out-of-scope frames reported separately.
"""
from __future__ import annotations

import csv
import json
import math
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from . import eval as ev
from . import io
from . import pipeline as pl
from .io import BLUE, ORANGE

OUT_OF_SCOPE = ("top", "topstripe")
NEG_FP_LIMIT = 0.005        # pre-registered: disqualify if negative-frame FP rate exceeds this
TIE_BAND = 0.02             # pre-registered: primary-score differences below this are "no difference"


def scene_of(stem: str) -> str:
    try:
        return io.parse_name(stem)["scene"]
    except ValueError:
        return "unknown"


class Dataset:
    """Frames + masks + scene tags for a list of stems, loaded once."""

    def __init__(self, stems: list[str], raw_dir: Path | None = None, labels_dir: Path | None = None):
        self.stems = list(stems)
        self.frames: dict[str, pl.Frame] = {}
        self.masks: dict[str, np.ndarray] = {}
        self.scene: dict[str, str] = {}
        raw = Path(raw_dir or io.RAW_DIR)
        for s in self.stems:
            img_path = next((p for p in raw.glob(f"{s}.*") if p.suffix.lower() in io.IMAGE_SUFFIXES), None)
            if img_path is None:
                raise FileNotFoundError(f"no image for {s} in {raw}")
            self.frames[s] = pl.Frame.from_image(io.load_image(img_path))
            self.masks[s] = io.load_mask(io.mask_path(img_path, labels_dir))
            self.scene[s] = scene_of(s)

    @classmethod
    def from_arrays(cls, frames: dict[str, pl.Frame], masks: dict[str, np.ndarray], scenes: dict[str, str]) -> "Dataset":
        ds = cls.__new__(cls)
        ds.stems = list(frames); ds.frames = dict(frames); ds.masks = dict(masks); ds.scene = dict(scenes)
        return ds


@dataclass(frozen=True)
class Fold:
    name: str
    train: tuple[str, ...]
    held_out: tuple[str, ...]


def loso_folds(stems: list[str], scenes: dict[str, str]) -> list[Fold]:
    """One fold per scene tag: that scene's frames are held out, all other frames train."""
    groups: dict[str, list[str]] = {}
    for s in sorted(stems):
        groups.setdefault(scenes[s], []).append(s)
    folds = []
    for g in sorted(groups):
        held = tuple(groups[g])
        folds.append(Fold(g, tuple(s for s in sorted(stems) if s not in held), held))
    return folds


def grouped_kfold(stems: list[str], scenes: dict[str, str], k: int, seed: int = 0) -> list[Fold]:
    """k folds; frames of one scene never split across folds (greedy by group size)."""
    import random
    groups: dict[str, list[str]] = {}
    for s in sorted(stems):
        groups.setdefault(scenes[s], []).append(s)
    rng = random.Random(seed)
    order = sorted(groups, key=lambda g: (-len(groups[g]), rng.random()))
    buckets: list[list[str]] = [[] for _ in range(k)]
    for g in order:
        buckets[min(range(k), key=lambda i: len(buckets[i]))].extend(groups[g])
    return [Fold(f"fold{i}", tuple(s for s in sorted(stems) if s not in b), tuple(sorted(b))) for i, b in enumerate(buckets) if b]


@dataclass
class CVResult:
    cfg: pl.Config
    folds: list[Fold]
    results: list[ev.ImageResult]
    preds: dict[str, np.ndarray]
    infos: dict[str, dict]
    fold_models: dict[str, pl.Model]
    scenes: dict[str, str]
    runtime_s: float = 0.0

    def score(self, out_scope: tuple[str, ...] = OUT_OF_SCOPE) -> dict:
        by_name = {r.name: r for r in self.results}
        in_pos = [r for r in self.results if not r.negative and self.scenes[r.name] not in out_scope]
        negs = [r for r in self.results if r.negative]
        oos = [r for r in self.results if not r.negative and self.scenes[r.name] in out_scope]

        def pooled(rs, c):
            tot = ev.Counts()
            for r in rs:
                tot = tot + r.counts[c]
            return tot
        s: dict = {}
        for c, nm in ((ORANGE, "o"), (BLUE, "b")):
            p = pooled(in_pos, c)
            s[f"iou_{nm}"] = p.iou; s[f"prec_{nm}"] = p.precision; s[f"rec_{nm}"] = p.recall
            s[f"neg_fp_{nm}"] = pooled(negs, c).fp_rate if negs else math.nan
            s[f"oos_iou_{nm}"] = pooled(oos, c).iou if oos else math.nan
        s["primary"] = float(np.nanmean([s["iou_o"], s["iou_b"]]))
        # per-fold IoU (folds that hold out in-scope positives)
        fold_iou = {"o": [], "b": []}
        fold_rows = []
        for f in self.folds:
            rs = [by_name[st] for st in f.held_out if st in by_name]
            pos = [r for r in rs if not r.negative and self.scenes[r.name] not in out_scope]
            row = {"fold": f.name, "n": len(rs), "iou_o": math.nan, "iou_b": math.nan, "neg_fp_o": math.nan, "neg_fp_b": math.nan,
                   "guard_trips": sum(1 for r in rs for k in ("table", "bg") if (self.infos[r.name].get(k) or {}).get("enabled") is False)}
            if pos:
                row["iou_o"] = pooled(pos, ORANGE).iou; row["iou_b"] = pooled(pos, BLUE).iou
                fold_iou["o"].append(row["iou_o"]); fold_iou["b"].append(row["iou_b"])
            ng = [r for r in rs if r.negative]
            if ng:
                row["neg_fp_o"] = pooled(ng, ORANGE).fp_rate; row["neg_fp_b"] = pooled(ng, BLUE).fp_rate
            fold_rows.append(row)
        s["fold_rows"] = fold_rows
        for nm in ("o", "b"):
            v = np.array(fold_iou[nm], float)
            s[f"fold_mean_{nm}"] = float(np.nanmean(v)) if v.size else math.nan
            s[f"fold_std_{nm}"] = float(np.nanstd(v)) if v.size else math.nan
        s["fold_primary"] = [float(np.nanmean([a, b])) for a, b in zip(fold_iou["o"], fold_iou["b"])]
        s["n_pos_folds"] = len(fold_iou["o"])
        s["guard_trips"] = int(sum(r["guard_trips"] for r in fold_rows))
        s["disqualified"] = bool((not math.isnan(s["neg_fp_o"]) and s["neg_fp_o"] > NEG_FP_LIMIT) or
                                 (not math.isnan(s["neg_fp_b"]) and s["neg_fp_b"] > NEG_FP_LIMIT))
        s["runtime_s"] = self.runtime_s
        return s


def cross_validate(ds: Dataset, cfg: pl.Config, folds: list[Fold] | None = None) -> CVResult:
    t0 = time.time()
    folds = folds or loso_folds(ds.stems, ds.scene)
    results, preds, infos, models = [], {}, {}, {}
    for f in folds:
        model = pl.fit([ds.frames[s] for s in f.train], [ds.masks[s] for s in f.train], cfg)
        models[f.name] = model
        for s in f.held_out:
            pred, info = pl.segment(ds.frames[s], model)
            preds[s] = pred; infos[s] = info
            results.append(ev.evaluate_image(s, pred, ds.masks[s]))
    return CVResult(cfg, folds, results, preds, infos, models, dict(ds.scene), time.time() - t0)


def git_hash() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def fresh_dir(path: Path) -> Path:
    """Append-only results: never overwrite an existing folder."""
    path = Path(path)
    if path.exists():
        i = 2
        while path.with_name(f"{path.name}_{i}").exists():
            i += 1
        path = path.with_name(f"{path.name}_{i}")
    path.mkdir(parents=True)
    return path


def _f(x) -> str:
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.3f}"


def write_cv_results(res: CVResult, out_dir: Path, title: str = "") -> Path:
    """config.json (+ git hash, folds, score), summary.md, and the EVAL.md tables via ev.write_results."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    sc = res.score()
    json.dump({"config": res.cfg.to_dict(), "config_hash": res.cfg.short_hash(), "git": git_hash(),
               "folds": [{"name": f.name, "held_out": list(f.held_out)} for f in res.folds],
               "score": {k: v for k, v in sc.items() if k != "fold_rows"}},
              (out_dir / "config.json").open("w"), indent=1, default=float)
    ev.write_results(res.results, out_dir, title=title)
    lines = [f"# {title or out_dir.name}", "", f"Config `{res.cfg.short_hash()}` (see config.json); git {git_hash()}; {len(res.results)} pool frames predicted once each; {res.runtime_s:.1f} s.", "",
             "## Score (EVAL.md / DECISIONS.md 2026-10-19 rule)", "",
             f"- **primary** (mean of pooled orange/blue IoU, in-scope positives): **{_f(sc['primary'])}**" + ("  ⚠ DISQUALIFIED (neg FP > 0.5 %)" if sc["disqualified"] else ""),
             f"- orange: IoU {_f(sc['iou_o'])}, P {_f(sc['prec_o'])}, R {_f(sc['rec_o'])}; fold IoU {_f(sc['fold_mean_o'])} ± {_f(sc['fold_std_o'])}",
             f"- blue: IoU {_f(sc['iou_b'])}, P {_f(sc['prec_b'])}, R {_f(sc['rec_b'])}; fold IoU {_f(sc['fold_mean_b'])} ± {_f(sc['fold_std_b'])}",
             f"- negative frames: FP rate orange {_f(sc['neg_fp_o'])}, blue {_f(sc['neg_fp_b'])}",
             f"- out-of-scope (top/topstripe): IoU orange {_f(sc['oos_iou_o'])}, blue {_f(sc['oos_iou_b'])}",
             f"- prior guard trips: {sc['guard_trips']}", "",
             "## Folds", "", "| held-out scene | n | orange IoU | blue IoU | neg FP o | neg FP b | guard trips |", "|---|---|---|---|---|---|---|"]
    for r in sc["fold_rows"]:
        lines.append(f"| {r['fold']} | {r['n']} | {_f(r['iou_o'])} | {_f(r['iou_b'])} | {_f(r['neg_fp_o'])} | {_f(r['neg_fp_b'])} | {r['guard_trips']} |")
    lines += ["", "## Box bounds across folds (min … max per channel)", ""]
    for c, nm in ((ORANGE, "orange"), (BLUE, "blue")):
        los = np.array([m.boxes[c].lo for m in res.fold_models.values()]); his = np.array([m.boxes[c].hi for m in res.fold_models.values()])
        full = [m.fit_info[str(c)]["fullness8"] for m in res.fold_models.values()]
        lines.append(f"- {nm}: lo {los.min(0).astype(int).tolist()} … {los.max(0).astype(int).tolist()}, hi {his.min(0).astype(int).tolist()} … {his.max(0).astype(int).tolist()}; fullness(8) {min(full):.2f}–{max(full):.2f}")
    lines += ["", "Per-image numbers: `per_image.csv`; per-condition table: `summary.csv`.", ""]
    (out_dir / "summary.md").write_text("\n".join(lines))
    return out_dir / "summary.md"


SCORE_KEYS = ("primary", "iou_o", "iou_b", "prec_o", "rec_o", "prec_b", "rec_b", "neg_fp_o", "neg_fp_b",
              "fold_mean_o", "fold_std_o", "fold_mean_b", "fold_std_b", "oos_iou_o", "oos_iou_b", "guard_trips", "disqualified", "runtime_s")


def run_configs(ds: Dataset, configs: list[tuple[str, str, object, pl.Config]], folds: list[Fold], out_csv: Path,
                configs_dir: Path | None = None) -> list[dict]:
    """Cross-validate each (axis, value_label, value, cfg); append one CSV row per config as it finishes."""
    out_csv = Path(out_csv); out_csv.parent.mkdir(parents=True, exist_ok=True)
    new_file = not out_csv.exists()
    rows = []
    with out_csv.open("a", newline="") as fh:
        w = csv.writer(fh)
        if new_file:
            w.writerow(["id", "axis", "value", *SCORE_KEYS, "fold_primary"])
        for axis, label, value, cfg in configs:
            res = cross_validate(ds, cfg, folds)
            sc = res.score()
            row = {"id": cfg.short_hash(), "axis": axis, "value": label, **{k: sc[k] for k in SCORE_KEYS}, "fold_primary": sc["fold_primary"]}
            rows.append(row)
            w.writerow([row["id"], axis, label, *[sc[k] for k in SCORE_KEYS], json.dumps([round(x, 4) for x in sc["fold_primary"]])])
            fh.flush()
            if configs_dir is not None:
                configs_dir.mkdir(parents=True, exist_ok=True)
                json.dump(cfg.to_dict(), (configs_dir / f"{cfg.short_hash()}.json").open("w"), indent=1)
    return rows


def sweep(ds: Dataset, base: pl.Config, axes: dict[str, list], folds: list[Fold], out_csv: Path,
          configs_dir: Path | None = None) -> list[dict]:
    """One-at-a-time sweep around ``base`` (the base itself is scored first as axis 'base')."""
    configs = [("base", "base", None, base)]
    for axis, values in axes.items():
        for v in values:
            configs.append((axis, str(v), v, pl.with_overrides(base, **{axis: v})))
    return run_configs(ds, configs, folds, out_csv, configs_dir)


def fit_final_and_predict(pool: Dataset, test: Dataset, cfg: pl.Config) -> tuple[pl.Model, list[ev.ImageResult], dict[str, np.ndarray], dict[str, dict]]:
    """Fit on every pool frame, predict every test frame. Call this exactly once per milestone."""
    model = pl.fit([pool.frames[s] for s in pool.stems], [pool.masks[s] for s in pool.stems], cfg)
    results, preds, infos = [], {}, {}
    for s in test.stems:
        pred, info = pl.segment(test.frames[s], model)
        preds[s] = pred; infos[s] = info
        results.append(ev.evaluate_image(s, pred, test.masks[s]))
    return model, results, preds, infos
