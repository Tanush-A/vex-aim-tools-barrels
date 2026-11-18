#!/usr/bin/env python3
"""TODO F: is there a relation between a frame's own hue x saturation histogram and the right thresholds?
The plan, the nine features, the tests and what would count are in PREREG.md in this folder (committed before
the first run). Nothing is adopted here; the detector, pipeline, geometry and eval are untouched.

What happens, in order:

1. ``load``      the train frames with box labels, grouped into conditions (one table under one light);
   brightness 1 is dropped; every other condition is ordinary or extreme. Test frames are refused before any
   image is opened. Per frame: the nine histogram features (no label used), the box-derived thresholds (the
   ceiling-check recipe on the frame's own boxes) and the hand label ``<stem>_hs.json`` when it exists.
2. ``per_condition``  features averaged, thresholds taken as the median: one row per condition.
3. ``analyse``   for a target (box / hand) and a scope (ordinary / ordinary + extreme): Spearman and permutation
   p for every (feature, threshold) pair, Holm-corrected; leave-one-condition-out predictions (feature chosen
   inside the loop) against the fixed value and the mean of the others.
4. ``detect``    today's detector with: the adopted model, the predicted thresholds, the box target as a
   model, the per-frame ceiling, the hand labels.
5. ``write``     summary.md, the CSVs, config.json, one scatter figure per threshold; a copy under runs/.

    python barrels/experiments/2026-11-18_hs_relation/run.py          # no arguments; safe to re-run as data grows

Outputs: results/2026-11-18_hs_relation/ (``--out DIR`` writes elsewhere and keeps no copy under runs/).
"""
from __future__ import annotations

import argparse
import csv
import datetime
import importlib.util
import json
import math
import shutil
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import detector as det, hsrel as hr, io, pipeline as pl, report as rp, splits, worldmap_bridge as wb  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

_spec = importlib.util.spec_from_file_location("oracle", HERE.parent / "2026-11-16_hs_oracle" / "run.py")
oracle = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(oracle)
pooled = oracle.pooled

OUT = PKG_ROOT / "results" / "2026-11-18_hs_relation"
CAM = pooled.CAM
MIN_CONDITIONS = 8          # under this many ORDINARY conditions the run is a dry run (PREREG 4)
N_PERM, SEED, ALPHA = 20000, 0, 0.05
BOX_ARM = "hue+sat+stripes"
SCOPES = ("ordinary", "all")
SCOPE_TITLE = {"ordinary": "ORDINARY conditions only", "all": "ordinary + EXTREME conditions (optimistic: the wood lamps are one table)"}
ALIAS = {"window_light": "HOME", "campus_light": "CAMPUS", "window_black": "BLACK"}
UNIT = {t: ("S" if t.endswith("s_lo") else "hue") for t in hr.THRESHOLDS}
NAN = float("nan")


def name(key: str) -> str:
    return ALIAS.get(key) or (key.replace("lamp", "wood ").replace("_wood", "") if key.endswith("_wood") and key.startswith("lamp") else key)


def git_state() -> str:
    try:
        h = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=HERE, capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", str(HERE), str(PKG_ROOT / "src"), str(PKG_ROOT / "data")], cwd=HERE, capture_output=True, text=True).stdout.strip()
        return h + ("-dirty" if dirty else "")
    except Exception:
        return "unknown"


def fmt(x, nd: int = 0) -> str:
    return "-" if x is None or (isinstance(x, float) and x != x) else f"{x:.{nd}f}"


def nanstat(fn, a) -> float:
    a = np.asarray(a, float)
    return float(fn(a[np.isfinite(a)])) if np.isfinite(a).any() else NAN


# ---------------------------------------------------------------- 1. load

def load(base: pl.Model) -> dict:
    sp = splits.load_splits()
    test = set(sp["test"])
    stems = [s for s in sorted(sp["train"]) if io.boxes_path(s).exists()]
    rp.refuse_test_frames(stems, sp)
    groups = hr.group_conditions(stems, test)                # raises on a test frame too
    excluded = {k: g["stems"] for k, g in groups.items() if g["class"] == hr.EXCLUDED}
    conds = {k: g for k, g in groups.items() if g["class"] != hr.EXCLUDED}
    if hr.REF_CONDITION not in conds:
        raise SystemExit(f"the reference condition {hr.REF_CONDITION} has no train frames")
    used = {s for g in conds.values() for s in g["stems"]}
    # slider labels that sit on a frame this run does not use (test, brightness 1, no boxes, no split): never read
    hs_skipped = sorted(p.name for p in io.LABELS_DIR.glob("*_hs.json") if p.name[:-len("_hs.json")] not in used)
    cfg = base.cfg
    frames: dict[str, dict] = {}
    for key, g in conds.items():
        for s in g["stems"]:
            assert s not in test, s
            bgr = io.load_image(io.find_image(s))
            frame = pl.Frame.from_image(bgr)
            hist, v_mean = hr.gated_hist(bgr, cfg.horizon_row or 0, cfg.v_min)
            label = io.load_boxes(s)
            if io.mask_path(s).exists():                     # home: the hand-made masks (stripes are in them)
                lab = io.load_mask(io.mask_path(s))
            else:                                            # boxes only: cores at the class's hue peak, plus its stripes
                lab = oracle.with_stripes(bgr, label["barrels"], pooled.body_mask(bgr, label["barrels"], cfg), cfg)
            m = oracle.frame_model(BOX_ARM, frame, lab, base)
            box = hr.thresholds_of(m)
            for cname, c in hr.COLOR_OF.items():
                if m.boxes[c] is base.boxes[c]:              # too few pixels of this color in the frame: no reading
                    for k in ("h_lo", "h_hi", "s_lo"):
                        box[f"{cname}_{k}"] = NAN
            hp = io.LABELS_DIR / f"{s}_hs.json"
            frames[s] = {"cond": key, "frame": frame, "hist": hist, "v_mean": v_mean, "box_model": m, "box": box,
                         "hand": hr.load_hs_label(hp) if hp.exists() else None}
    ref = hr.Reference.from_hists([frames[s]["hist"] for s in conds[hr.REF_CONDITION]["stems"]])
    for f in frames.values():
        f["feat"] = hr.frame_features(f["hist"], f["v_mean"], ref)
    no_boxes = [s for s in sorted(sp["train"]) if not io.boxes_path(s).exists()]
    return {"conds": conds, "frames": frames, "excluded": excluded, "hs_skipped": hs_skipped, "no_boxes": no_boxes, "n_test": len(test)}


# ---------------------------------------------------------------- 2. one row per condition

def per_condition(data: dict) -> dict[str, dict]:
    rows = {}
    for key, g in data["conds"].items():
        fr = [data["frames"][s] for s in g["stems"]]
        hand = [f["hand"] for f in fr if f["hand"]]
        r = {"class": g["class"], "frames": len(fr), "hand_frames": len(hand),
             "feat": {k: nanstat(np.mean, [f["feat"][k] for f in fr]) for k in hr.FEATURES},
             "box": {t: nanstat(np.median, [f["box"][t] for f in fr]) for t in hr.THRESHOLDS},
             "box_n": {t: int(np.isfinite([f["box"][t] for f in fr]).sum()) for t in hr.THRESHOLDS},
             "box_iqr": {t: nanstat(lambda a: np.percentile(a, 75) - np.percentile(a, 25), [f["box"][t] for f in fr]) for t in hr.THRESHOLDS},
             "hand": {t: (float(np.median([h[t] for h in hand])) if hand else NAN) for t in hr.THRESHOLDS}}
        rows[key] = r
    return rows


# ---------------------------------------------------------------- 3. relation and prediction

def analyse(keys: list[str], cond: dict[str, dict], target: str, fixed: dict[str, float]) -> tuple[list[dict], list[dict]]:
    x_all = np.array([[cond[k]["feat"][f] for f in hr.FEATURES] for k in keys], float).reshape(len(keys), len(hr.FEATURES))
    pairs, preds = [], []
    for t in hr.THRESHOLDS:
        y_all = np.array([cond[k][target][t] for k in keys], float)
        ok = np.isfinite(y_all)
        x, y, ks = x_all[ok], y_all[ok], [k for k, o in zip(keys, ok) if o]
        for j, f in enumerate(hr.FEATURES):
            fin = np.isfinite(x[:, j]) if len(y) else np.zeros(0, bool)
            r = hr.perm_pvalue(x[fin, j], y[fin], N_PERM, SEED)
            pairs.append({"threshold": t, "feature": f, "primary": f in hr.PRIMARY[t], **r})
        if not len(y):
            continue
        one, two = hr.loco(x, y, 1), hr.loco(x, y, 2)
        opt, opt_f = hr.loco_optimistic(x, y, 1)
        for i, k in enumerate(ks):
            others = np.delete(y, i)
            preds.append({"threshold": t, "condition": k, "target": float(y[i]), "fixed": fixed[t],
                          "mean_others": float(others.mean()) if len(others) else NAN,
                          "pred1": one[i]["pred"], "pred1_feats": "+".join(hr.FEATURES[j] for j in one[i]["feats"]), "pred1_fallback": one[i]["fallback"],
                          "pred1_optimistic": opt[i], "optimistic_feat": "+".join(hr.FEATURES[j] for j in opt_f),
                          "pred2": two[i]["pred"], "pred2_feats": "+".join(hr.FEATURES[j] for j in two[i]["feats"]), "pred2_fallback": two[i]["fallback"]})
    p = np.array([r["p"] for r in pairs], float)
    prim = np.array([r["primary"] for r in pairs])
    h_all, h_prim = hr.holm(p), np.full(len(p), NAN)
    h_prim[prim] = hr.holm(p[prim])
    for r, a, b in zip(pairs, h_all, h_prim):
        r["p_holm_all"], r["p_holm_primary"] = float(a), float(b)
    return pairs, preds


def mae(preds: list[dict], t: str, col: str) -> float:
    e = [abs(r[col] - r["target"]) for r in preds if r["threshold"] == t and r[col] == r[col]]
    return float(np.mean(e)) if e else NAN


# ---------------------------------------------------------------- 4. detection

def detect(data: dict, cond: dict, base: pl.Model, runs: dict) -> tuple[dict, dict]:
    """arm -> {stem: scored frame}; and arm -> {condition: colors that kept the adopted box}."""
    dcfg = det.DetConfig()
    res: dict[str, dict] = {}
    kept: dict[str, dict] = {}

    def run(arm: str, key: str, model_for) -> None:
        for s in data["conds"][key]["stems"]:
            f = data["frames"][s]
            res.setdefault(arm, {})[s] = rp.score_frame(s, pl.segment(f["frame"], model_for(f))[0], dcfg, CAM)

    for key, c in cond.items():
        run("fixed", key, lambda f: base)
        run("box per frame", key, lambda f: f["box_model"])
        m, k = hr.model_from_thresholds(base, c["box"])
        kept.setdefault("box median", {})[key] = k
        run("box median", key, lambda f, m=m: m)
        if c["hand_frames"]:
            m, k = hr.model_from_thresholds(base, c["hand"])
            kept.setdefault("hand median", {})[key] = k
            run("hand median", key, lambda f, m=m: m)
    for (target, scope), (_, preds) in runs.items():
        for col in ("pred1", "pred2"):
            arm = f"{col} [{target}, {scope}]"
            by: dict[str, dict] = {}
            for r in preds:
                by.setdefault(r["condition"], {})[r["threshold"]] = r[col]
            for key, th in by.items():
                m, k = hr.model_from_thresholds(base, th)
                kept.setdefault(arm, {})[key] = k
                run(arm, key, lambda f, m=m: m)
    return res, kept


def cell(res: dict, arm: str, stems: list[str]):
    got = [res[arm][s] for s in stems if s in res.get(arm, {})]
    return rp.summarize(got) if len(got) == len(stems) and got else None


def cell_text(c) -> str:
    if c is None:
        return "-"
    return f"{c.found} / {c.barrels} ({c.false}), {fmt(c.score, 2)}" + (" DQ" if c.clean_neg_false else "")


# ---------------------------------------------------------------- 5. figures

def figures(out: Path, cond: dict, runs: dict, fixed: dict, targets: list[str]) -> list[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ink, blue, gray = "#222222", "#1f5fa8", "#6b6b6b"
    made = []
    for target in targets:
        pairs = runs[(target, "all")][0]
        for t in hr.THRESHOLDS:
            mine = {r["feature"]: r for r in pairs if r["threshold"] == t}
            rest = sorted((f for f in hr.FEATURES if f not in hr.PRIMARY[t]), key=lambda f: -(abs(mine[f]["rho"]) if mine[f]["rho"] == mine[f]["rho"] else -1))
            feats = list(hr.PRIMARY[t]) + rest[:1]
            fig, axs = plt.subplots(1, 3, figsize=(13.5, 4.2), sharey=True)
            for ax, f in zip(axs, feats):
                for cls, mk, kw in ((hr.ORDINARY, "o", {"color": blue}), (hr.EXTREME, "s", {"mfc": "none", "mec": gray, "color": gray})):
                    ks = [k for k, c in cond.items() if c["class"] == cls and c["feat"][f] == c["feat"][f] and c[target][t] == c[target][t]]
                    ax.plot([cond[k]["feat"][f] for k in ks], [cond[k][target][t] for k in ks], mk, ms=8, ls="none", label=f"{cls} condition", **kw)
                    for k in ks:
                        ax.annotate(name(k), (cond[k]["feat"][f], cond[k][target][t]), xytext=(5, 4), textcoords="offset points", fontsize=7, color=ink)
                ax.axhline(fixed[t], color=ink, lw=0.8, ls="--", label="adopted fixed value")
                r = mine[f]
                ax.set_title(f"{f}{' (primary pair)' if r['primary'] else ' (best other feature)'}\nall conditions: rho {fmt(r['rho'], 2)}, p {fmt(r['p'], 3)}, n {r['n']}", fontsize=9, color=ink)
                ax.set_xlabel(f, fontsize=9); ax.grid(alpha=0.25, lw=0.5); ax.tick_params(labelsize=8)
                for side in ("top", "right"):
                    ax.spines[side].set_visible(False)
            axs[0].set_ylabel(f"{t} ({target} target, {UNIT[t]} units)", fontsize=9)
            axs[0].legend(fontsize=7, frameon=False, loc="best")
            n_ord = sum(c["class"] == hr.ORDINARY for c in cond.values())
            fig.suptitle(f"{t}: {target}-derived threshold per condition against three histogram features. {n_ord} ordinary condition(s)"
                         + (": a dry run, not a finding" if n_ord < MIN_CONDITIONS else ""), fontsize=10, color=ink)
            fig.tight_layout()
            p = out / f"fig_{target}_{t}.png"
            fig.savefig(p, dpi=110); plt.close(fig)
            made.append(p.name)
    return made


# ---------------------------------------------------------------- 5. the summary

def acceptance(runs, res, data, cond, target: str) -> list[str]:
    """PREREG 'what must be true', on the ordinary conditions. Only called at n >= MIN_CONDITIONS."""
    pairs, preds = runs[(target, "ordinary")]
    L = ["| threshold | A: best primary pair (Holm p) | B: MAE nested one-feature vs fixed / mean of others | B: better than fixed in | A and B |", "|---|---|---|---|---|"]
    for t in hr.THRESHOLDS:
        prim = [r for r in pairs if r["threshold"] == t and r["primary"] and r["p_holm_primary"] == r["p_holm_primary"]]
        best = min(prim, key=lambda r: r["p_holm_primary"]) if prim else None
        a = bool(best and best["p_holm_primary"] < ALPHA)
        rows = [r for r in preds if r["threshold"] == t and not r["pred1_fallback"]]
        m1, mf, mm = mae(rows, t, "pred1"), mae(rows, t, "fixed"), mae(rows, t, "mean_others")
        wins = sum(abs(r["pred1"] - r["target"]) < abs(r["fixed"] - r["target"]) for r in rows)
        b = bool(rows) and m1 < mf and m1 < mm and wins >= math.ceil(2 * len(rows) / 3)
        L.append(f"| {t} | {best['feature'] + ' (' + fmt(best['p_holm_primary'], 3) + ')' if best else '-'}: {'pass' if a else 'fail'} | "
                 f"{fmt(m1, 1)} vs {fmt(mf, 1)} / {fmt(mm, 1)} | {wins} of {len(rows)}: {'pass' if b else 'fail'} | {'PASS' if a and b else 'fail'} |")
    arm = f"pred1 [{target}, ordinary]"
    ks = [k for k, c in cond.items() if c["class"] == hr.ORDINARY and cell(res, arm, data["conds"][k]["stems"])]
    cp = [cell(res, arm, data["conds"][k]["stems"]) for k in ks]
    cf = [cell(res, "fixed", data["conds"][k]["stems"]) for k in ks]
    found_p, found_f = sum(c.found for c in cp), sum(c.found for c in cf)
    false_p, false_f = sum(c.false for c in cp), sum(c.false for c in cf)
    dq = sum(c.clean_neg_false for c in cp)
    drop = [name(k) for k, a_, b_ in zip(ks, cp, cf) if a_.score == a_.score and b_.score == b_.score and a_.score < b_.score - 0.02]
    ok = found_p > found_f and false_p <= false_f + 2 and dq == 0 and not drop
    L += ["", f"C (all six thresholds predicted, the arm `{arm}`; the mixed arm of the PREREG is a later step): found {found_p} vs {found_f} fixed; "
              f"false {false_p} vs {false_f}; boxes on clean negatives {dq}; conditions losing more than 0.02: {', '.join(drop) or 'none'}: **{'pass' if ok else 'fail'}**."]
    return L


def write(out: Path, data: dict, cond: dict, runs: dict, res: dict, kept: dict, base: pl.Model, archive: bool) -> str:
    out.mkdir(parents=True, exist_ok=True)
    fixed = hr.thresholds_of(base)
    git, today = git_state(), datetime.date.today().isoformat()
    keys = list(cond)
    ordinary = [k for k in keys if cond[k]["class"] == hr.ORDINARY]
    extreme = [k for k in keys if cond[k]["class"] == hr.EXTREME]
    hand_keys = [k for k in keys if cond[k]["hand_frames"]]
    targets = sorted({t for t, _ in runs})
    dry = len(ordinary) < MIN_CONDITIONS
    scope_keys = {"ordinary": ordinary, "all": keys}
    th_head = " | ".join(t.replace("_", " ") for t in hr.THRESHOLDS)

    L = ["# Histogram against thresholds: is there a relation? (TODO F)", ""]
    if dry:
        L += [f"> **DRY RUN. {len(ordinary)} ordinary condition(s); under {MIN_CONDITIONS} no conclusion about a relation can be drawn.** "
              "Every table below shows that the pipeline runs and gives a first look. None of it is a finding.", ""]
    L += [f"Run {today}, git {git}. Plan and criteria: `experiments/2026-11-18_hs_relation/PREREG.md`. Train frames only "
          f"(the {data['n_test']} test frames are refused before any image is opened). Nothing is adopted.", "",
          f"- **Ordinary conditions ({len(ordinary)}):** " + (", ".join(f"{name(k)} `{k}` ({cond[k]['frames']} frames)" for k in ordinary) or "none"),
          f"- **Extreme conditions ({len(extreme)}; parked, not targets):** " + (", ".join(f"{name(k)} ({cond[k]['frames']})" for k in extreme) or "none"),
          f"- **Excluded (lamp brightness 1):** " + (", ".join(f"{k} ({len(v)})" for k, v in data["excluded"].items()) or "none"),
          f"- **Hand labels (`_hs.json`):** " + (", ".join(f"{name(k)} ({cond[k]['hand_frames']} frames)" for k in hand_keys) or "none yet; every number below uses the **box-derived** target")]
    if data["hs_skipped"]:
        L.append(f"- Slider labels not used (their frame is a test frame, brightness 1, or has no boxes / split): {', '.join(data['hs_skipped'])}")
    if data["no_boxes"]:
        L.append(f"- Train frames without box labels, left out: {len(data['no_boxes'])} ({', '.join(data['no_boxes'][:4])}{', ...' if len(data['no_boxes']) > 4 else ''})")
    L += ["", "Targets: **box** = thresholds read from the hand-drawn boxes per frame (the ceiling-check recipe), median per condition; "
              "**hand** = Tanush's slider labels, median per condition. Hue in OpenCV units (a negative hue is below the red wrap: -3 = 177).", ""]

    # --- 1 targets
    L += ["## 1. The targets: six thresholds per condition", "", f"| condition | class | target | {th_head} | frames with a reading (orange / blue) |", "|---|---|---|" + "---|" * 7]
    L.append(f"| adopted model | | fixed | " + " | ".join(fmt(fixed[t]) for t in hr.THRESHOLDS) + " | |")
    for k in keys:
        c = cond[k]
        L.append(f"| {name(k)} | {c['class']} | box | " + " | ".join(fmt(c["box"][t]) for t in hr.THRESHOLDS) + f" | {c['box_n']['orange_h_lo']} / {c['box_n']['blue_h_lo']} of {c['frames']} |")
        if c["hand_frames"]:
            L.append(f"| | | hand | " + " | ".join(fmt(c["hand"][t]) for t in hr.THRESHOLDS) + f" | {c['hand_frames']} labeled |")
            L.append(f"| | | hand − box | " + " | ".join(fmt(c["hand"][t] - c["box"][t]) for t in hr.THRESHOLDS) + " | |")
    if hand_keys:
        L += ["", f"Hand against box over the {len(hand_keys)} condition(s) that have both, median |hand − box|: "
                  + "; ".join(f"{t} {fmt(nanstat(np.median, [abs(cond[k]['hand'][t] - cond[k]['box'][t]) for k in hand_keys]), 1)}" for t in hr.THRESHOLDS)
                  + ". PREREG: box can stand in for hand when this is at most 3 hue units and 20 S units."]
    L += ["", "Is there anything to predict at condition level? Spread of the box-derived thresholds between conditions (max − min of the condition medians) "
              "against the spread inside a condition (median over conditions of the per-frame interquartile range):", "",
          f"| | {th_head} |", "|---|" + "---|" * 6]
    for label, ks in (("between, ordinary", ordinary), ("between, ordinary + extreme", keys)):
        L.append(f"| {label} (n = {len(ks)}) | " + " | ".join(fmt(nanstat(np.ptp, [cond[k]['box'][t] for k in ks]) if len(ks) > 1 else NAN) for t in hr.THRESHOLDS) + " |")
    L.append("| inside a condition | " + " | ".join(fmt(nanstat(np.median, [cond[k]["box_iqr"][t] for k in keys])) for t in hr.THRESHOLDS) + " |")

    # --- 2 features
    L += ["", "## 2. The features: from the frame alone, mean per condition", "", "| condition | class | " + " | ".join(hr.FEATURES) + " |", "|---|---|" + "---|" * len(hr.FEATURES)]
    nd = {"s_share100": 3, "ref_s_scale": 2, "ref_hue_shift": 1, "blue_peak_h": 1, "orange_peak_h": 1}
    for k in keys:
        L.append(f"| {name(k)} | {cond[k]['class']} | " + " | ".join(fmt(cond[k]["feat"][f], nd.get(f, 0)) for f in hr.FEATURES) + " |")
    L += ["", f"`ref_hue_shift` and `ref_s_scale` compare each frame with the pooled {name(hr.REF_CONDITION)} histogram, so {name(hr.REF_CONDITION)} reads about 0 and 1 by construction."]

    # --- 3 relation
    L += ["", "## 3. Is there a relation? Spearman correlation at condition level", ""]
    for target in targets:
        for scope in SCOPES:
            pairs, _ = runs[(target, scope)]
            ks = [k for k in scope_keys[scope] if any(cond[k][target][t] == cond[k][target][t] for t in hr.THRESHOLDS)]
            n = len(ks)
            tested = [r for r in pairs if r["p"] == r["p"]]
            L += [f"### Target: {target}. {SCOPE_TITLE[scope]}. n = {n} conditions", ""]
            if n < 3:
                L += [f"n = {n}: a rank correlation needs at least 3 conditions. Nothing to report.", ""]
                continue
            minp = 2 / math.factorial(n) if n <= 8 else 1 / (N_PERM + 1)
            n_prim = sum(r["primary"] for r in tested)
            L += [f"{len(tested)} pairs tested ({n_prim} primary). At p < {ALPHA} about **{ALPHA * len(tested):.1f} of them ({ALPHA * n_prim:.1f} of the primary) would look significant by chance alone**; "
                  f"hence the Holm-corrected column. Smallest p this n can produce: {minp:.3g}"
                  + (f", so **no pair can reach {ALPHA} at this n**." if minp >= ALPHA else (f"; after Holm over the primary family a pair needs p < {ALPHA / max(1, n_prim):.4f}" + (", **out of reach at this n**." if minp >= ALPHA / max(1, n_prim) else "."))),
                  "", "Primary pairs (named in the PREREG):", "", "| threshold | feature | n | rho | p | p, Holm over the primary |", "|---|---|---|---|---|---|"]
            for r in pairs:
                if r["primary"]:
                    L.append(f"| {r['threshold']} | {r['feature']} | {r['n']} | {fmt(r['rho'], 2)} | {fmt(r['p'], 3)} | {fmt(r['p_holm_primary'], 3)} |")
            top = sorted((r for r in tested if not r["primary"]), key=lambda r: (r["p"], -abs(r["rho"])))[:6]
            L += ["", "The six strongest of the other pairs (exploratory: leads, not findings):", "", "| threshold | feature | n | rho | p | p, Holm over all pairs |", "|---|---|---|---|---|---|"]
            L += [f"| {r['threshold']} | {r['feature']} | {r['n']} | {fmt(r['rho'], 2)} | {fmt(r['p'], 3)} | {fmt(r['p_holm_all'], 3)} |" for r in top]
            sig_p = [r for r in tested if r["primary"] and r["p_holm_primary"] < ALPHA]
            sig_a = [r for r in tested if r["p_holm_all"] < ALPHA]
            L += ["", f"After correction: {len(sig_p)} primary pair(s) and {len(sig_a)} of all pairs below {ALPHA}"
                      + (": " + ", ".join(sorted({f"{r['threshold']} ~ {r['feature']}" for r in sig_p + sig_a})) if sig_p or sig_a else "") + ".", ""]

    # --- 4 prediction
    L += ["## 4. Does it predict? Leave one condition out", "",
          "Mean |prediction − target| over the held-out conditions, in hue units (S units for the floors). `fixed` = the adopted value; `mean of others` = the mean target of the other conditions; "
          "`one feature` = a line on one feature, **the feature chosen inside the loop** from the other conditions only; `two features` = the same with at most two. "
          "`optimistic` = the feature chosen once on all conditions: the held-out condition then helped pick its own predictor, so this number reads too low. It is printed to show the size of that mistake and is never the result.", ""]
    for target in targets:
        for scope in SCOPES:
            _, preds = runs[(target, scope)]
            n = len({r["condition"] for r in preds})
            L += [f"### Target: {target}. {SCOPE_TITLE[scope]}. n = {n} conditions", ""]
            if n < 2:
                L += ["Fewer than 2 conditions: nothing can be held out.", ""]
                continue
            fb1 = all(r["pred1_fallback"] for r in preds)
            if fb1:
                L += [f"**n = {n} is too small for a nested fit (4 conditions needed for one feature, 5 for two): `one feature` and `two features` are the mean of the others here, not a rule.**", ""]
            L += ["| threshold | n | fixed | mean of others | one feature (nested) | features chosen | two features (nested) | optimistic (not a result) |", "|---|---|---|---|---|---|---|---|"]
            for t in hr.THRESHOLDS:
                rows = [r for r in preds if r["threshold"] == t]
                chosen: dict[str, int] = {}
                for r in rows:
                    chosen[r["pred1_feats"] or "none (fallback)"] = chosen.get(r["pred1_feats"] or "none (fallback)", 0) + 1
                ch = ", ".join(f"{k} ×{v}" for k, v in sorted(chosen.items(), key=lambda kv: -kv[1]))
                n2 = sum(not r["pred2_fallback"] for r in rows)
                L.append(f"| {t} | {len(rows)} | {fmt(mae(rows, t, 'fixed'), 1)} | {fmt(mae(rows, t, 'mean_others'), 1)} | {fmt(mae(rows, t, 'pred1'), 1)} | {ch} | "
                         f"{fmt(mae(rows, t, 'pred2'), 1)}{'' if n2 == len(rows) else f' ({len(rows) - n2} fallback)'} | {fmt(mae(rows, t, 'pred1_optimistic'), 1)} ({rows[0]['optimistic_feat'] or 'none'}) |")
            L.append("")

    # --- 5 detection
    L += ["## 5. Does it detect? Today's detector with each set of thresholds", "",
          "Each cell: found / barrels (false boxes), score; `DQ` = a box on a clean empty frame. v2 rule, `DetConfig()` defaults. `fixed` = the adopted model as stored (also at home: not the leave-one-scene-out home number). "
          "`pred1` / `pred2` = the six thresholds predicted for the held-out condition by the nested one- / two-feature rule (with the fallback of section 4 they are the mean of the other conditions). "
          "`box median` = the box target used as one model per condition. `box per frame` = thresholds read from each frame's own labels (the ceiling check; not a method).", ""]
    for target in targets:
        for scope in SCOPES:
            ks = [k for k in scope_keys[scope] if cell(res, f"pred1 [{target}, {scope}]", data["conds"][k]["stems"])]
            arms = ["fixed", f"pred1 [{target}, {scope}]", f"pred2 [{target}, {scope}]", "box median", "box per frame"] + (["hand median"] if hand_keys else [])
            L += [f"### Predictions from the {target} target. {SCOPE_TITLE[scope]}. n = {len(ks)} conditions", ""]
            if not ks:
                L += ["No condition to score.", ""]
                continue
            L += ["| condition | class | frames | " + " | ".join(a.split(" [")[0] for a in arms) + " |", "|---|---|---|" + "---|" * len(arms)]
            for k in ks:
                st = data["conds"][k]["stems"]
                L.append(f"| {name(k)} | {cond[k]['class']} | {len(st)} | " + " | ".join(cell_text(cell(res, a, st)) for a in arms) + " |")
            for label, sub in (("**ordinary, total**", [k for k in ks if cond[k]["class"] == hr.ORDINARY]), ("**extreme, total**", [k for k in ks if cond[k]["class"] == hr.EXTREME])):
                if len(sub) > 1:
                    tot = []
                    for a in arms:
                        cs = [cell(res, a, data["conds"][k]["stems"]) for k in sub]
                        tot.append("-" if any(c is None for c in cs) else f"{sum(c.found for c in cs)} / {sum(c.barrels for c in cs)} ({sum(c.false for c in cs)})")
                    L.append(f"| {label} | | {sum(len(data['conds'][k]['stems']) for k in sub)} | " + " | ".join(tot) + " |")
            flagged = [f"{a.split(' [')[0]} on {name(k)}: {' and '.join(v)}" for a in arms for k, v in kept.get(a, {}).items() if v and k in ks]
            if flagged:
                L += ["", "Kept the adopted box (no usable range): " + "; ".join(flagged) + "."]
            L.append("")

    # --- 6 verdict
    L += ["## 6. Against the pre-registered criteria", ""]
    if dry:
        L += [f"**Not evaluated: {len(ordinary)} ordinary condition(s), {MIN_CONDITIONS} needed (aim: 10).** Criteria A (a primary pair with Holm p < {ALPHA}), "
              "B (nested one-feature error below both baselines, better than fixed in two thirds of the conditions) and C (more barrels found, at most 2 more false boxes, no clean-negative box, "
              "no condition losing more than 0.02) are in the PREREG and are checked on the ordinary conditions only."]
    else:
        tgt = "hand" if "hand" in targets and len([k for k in ordinary if cond[k]["hand_frames"]]) >= MIN_CONDITIONS else "box"
        L += [f"Ordinary conditions, target `{tgt}`" + (" (hand labels cover fewer than 8 ordinary conditions; box is a stand-in only if hand − box is small, section 1)" if tgt == "box" else "") + ".", ""]
        L += acceptance(runs, res, data, cond, tgt)
    figs = figures(out, cond, runs, fixed, targets)
    L += ["", "## Files", "", "`per_condition.csv` (features, targets, detection per condition), `pairs.csv` (every pair, both scopes), `predictions.csv` (every held-out prediction), "
          "`detection.csv`, `per_frame.csv`, `config.json`; figures " + (f"`fig_<target>_<threshold>.png` ({len(figs)}, not in git)" if figs else "none") + ". A copy of this run is under `runs/`."]
    text = "\n".join(L) + "\n"
    (out / "summary.md").write_text(text)

    # --- CSVs
    def dump(fname: str, rows: list[dict]) -> None:
        if not rows:
            (out / fname).write_text("")
            return
        with (out / fname).open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    def num(x):
        return "" if isinstance(x, float) and x != x else (round(x, 4) if isinstance(x, float) else x)

    arms_all = list(res)
    pc, dt = [], []
    for k in keys:
        c = cond[k]
        st = data["conds"][k]["stems"]
        r = {"condition": k, "name": name(k), "class": c["class"], "frames": c["frames"], "hand_frames": c["hand_frames"]}
        r.update({f"feat_{f}": num(c["feat"][f]) for f in hr.FEATURES})
        r.update({f"box_{t}": num(c["box"][t]) for t in hr.THRESHOLDS})
        r.update({f"box_n_{t}": c["box_n"][t] for t in ("orange_h_lo", "blue_h_lo")})
        r.update({f"box_iqr_{t}": num(c["box_iqr"][t]) for t in hr.THRESHOLDS})
        r.update({f"hand_{t}": num(c["hand"][t]) for t in hr.THRESHOLDS})
        for a in ("fixed", "box median", "box per frame"):
            cc = cell(res, a, st)
            r.update({f"{a.replace(' ', '_')}_{q}": getattr(cc, q) for q in ("barrels", "found", "missed", "false")})
        pc.append(r)
        for a in arms_all:
            cc = cell(res, a, st)
            if cc:
                dt.append({"condition": k, "class": c["class"], "arm": a, "frames": cc.frames, "barrels": cc.barrels, "found": cc.found, "missed": cc.missed, "false": cc.false,
                           "score": num(cc.score), "clean_neg_false": cc.clean_neg_false, "kept_adopted_box": "+".join(kept.get(a, {}).get(k, []))})
    dump("per_condition.csv", pc)
    dump("detection.csv", dt)
    dump("pairs.csv", [{"target": tg, "scope": sc, **{kk: num(v) for kk, v in r.items()}} for (tg, sc), (pairs, _) in runs.items() for r in pairs])
    dump("predictions.csv", [{"target": tg, "scope": sc, **{kk: num(v) for kk, v in r.items()}} for (tg, sc), (_, preds) in runs.items() for r in preds])
    dump("per_frame.csv", [{"stem": s, "condition": f["cond"], **{f"feat_{k}": num(v) for k, v in f["feat"].items()}, **{f"box_{k}": num(v) for k, v in f["box"].items()},
                            **{f"hand_{t}": (f["hand"][t] if f["hand"] else "") for t in hr.THRESHOLDS}} for s, f in data["frames"].items()])
    json.dump({"date": today, "git": git, "dry_run": dry, "min_conditions": MIN_CONDITIONS, "n_ordinary": len(ordinary), "n_extreme": len(extreme),
               "model": str(Path(wb.DEFAULT_MODEL).relative_to(PKG_ROOT)), "config_hash": base.cfg.short_hash(), "fixed": fixed,
               "features": hr.FEATURES, "thresholds": hr.THRESHOLDS, "primary": hr.PRIMARY, "windows": hr.WINDOWS, "s_color": hr.S_COLOR, "min_window_px": hr.MIN_WINDOW_PX,
               "shift_max": hr.SHIFT_MAX, "reference": hr.REF_CONDITION, "box_arm": BOX_ARM, "n_perm": N_PERM, "seed": SEED, "alpha": ALPHA,
               "targets": targets, "conditions": {k: {"class": cond[k]["class"], "stems": data["conds"][k]["stems"],
                                                      "hand_stems": [s for s in data["conds"][k]["stems"] if data["frames"][s]["hand"]]} for k in keys},
               "excluded": data["excluded"], "hs_labels_not_used": data["hs_skipped"], "train_without_boxes": data["no_boxes"]},
              (out / "config.json").open("w"), indent=1)
    if archive:
        runs_dir = out / "runs"
        runs_dir.mkdir(exist_ok=True)
        nn = 1 + max([int(p.name[:2]) for p in runs_dir.iterdir() if p.is_dir() and p.name[:2].isdigit()] or [0])
        dest = runs_dir / f"{nn:02d}_{today}_{git}_ord{len(ordinary)}_ext{len(extreme)}"
        dest.mkdir()
        for p in out.iterdir():
            if p.is_file() and p.suffix in (".md", ".csv", ".json"):
                shutil.copy2(p, dest / p.name)
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=None, help="write here instead of results/2026-11-18_hs_relation (no copy under runs/)")
    args = ap.parse_args()
    base = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    fixed = hr.thresholds_of(base)
    data = load(base)
    cond = per_condition(data)
    keys = list(cond)
    targets = ["box"] + (["hand"] if any(c["hand_frames"] for c in cond.values()) else [])
    runs = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        for target in targets:
            for scope in SCOPES:
                ks = [k for k in keys if scope == "all" or cond[k]["class"] == hr.ORDINARY]
                runs[(target, scope)] = analyse(ks, cond, target, fixed)
    res, kept = detect(data, cond, base, runs)
    print(write(args.out or OUT, data, cond, runs, res, kept, base, archive=args.out is None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
