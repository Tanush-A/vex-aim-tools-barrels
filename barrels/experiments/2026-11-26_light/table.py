#!/usr/bin/env python3
"""Part A, step 2: the readings compared (from per_frame.csv, made by measure.py; no image is opened here).

    python barrels/experiments/2026-11-26_light/table.py

For each reading (``common.READINGS``):
- how many ordinary frames it says anything on;
- how well its condition mean tracks the labelled paint over the 17 ordinary conditions: Pearson r and Spearman rho
  against the blue paint's median S, the blue paint's median hue and the orange paint's median hue;
- leave one place out, per frame: a line (target = a + b x reading) is fitted on the frames of the other places, every
  place weighing the same, and predicts each frame of the held-out place; "skill" = 1 - (its mean squared error /
  that of predicting the other places' mean); above 0 = the reading helps, at or below 0 = it does not;
- how stable it is: the spread between frames of one condition (SD, pooled), the spread between conditions, their
  ratio; and the frame furthest from its condition's median;
- what fools it: the mean distance from the condition's median on the close-up, the clutter and the empty frames;
- what a rule needs: do the frames of the conditions whose blue paint is under the fixed floor (its 10th percentile
  of S below 113) read warmer than all other frames? AUC, and how many other frames read at least as warm as the
  10th percentile of those frames.

Writes results/2026-11-26_light/readings.md and readings.json.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402

FIXED_BLUE_S = 113.0


def load() -> list[dict]:
    rows = []
    with (cm.OUT / "per_frame.csv").open() as fh:
        for r in csv.DictReader(fh):
            rows.append({k: (v if k in ("stem", "condition", "place", "class", "scene") else float(v)) for k, v in r.items()})
    return rows


def rank(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    r[order] = np.arange(len(x), dtype=float)
    for v in np.unique(x):
        m = x == v
        r[m] = r[m].mean()
    return r


def pearson(x, y) -> float:
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 3 or np.std(x[ok]) == 0 or np.std(y[ok]) == 0:
        return float("nan")
    return float(np.corrcoef(x[ok], y[ok])[0, 1])


def spearman(x, y) -> float:
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 3:
        return float("nan")
    return pearson(rank(x[ok]), rank(y[ok]))


def cond_mean(rows: list[dict], key: str) -> dict[str, float]:
    by = defaultdict(list)
    for r in rows:
        if np.isfinite(r[key]):
            by[r["condition"]].append(r[key])
    return {c: float(np.mean(v)) for c, v in by.items()}


def lopo(rows: list[dict], xkey: str, ykey: str) -> dict:
    """Leave one place out, per frame, every place weighing the same in the fit and in the error."""
    use = [r for r in rows if np.isfinite(r[xkey]) and np.isfinite(r[ykey])]
    places = sorted({r["place"] for r in use})
    n_place = defaultdict(int)
    for r in use:
        n_place[r["place"]] += 1
    mse, mse0, per = [], [], {}
    for p in places:
        tr = [r for r in use if r["place"] != p]
        te = [r for r in use if r["place"] == p]
        if len({r["place"] for r in tr}) < 2:
            continue
        w = np.array([1.0 / n_place[r["place"]] for r in tr])
        x, y = np.array([r[xkey] for r in tr]), np.array([r[ykey] for r in tr])
        if np.std(x) == 0:
            b, a = 0.0, float(np.average(y, weights=w))
        else:
            b, a = np.polyfit(x, y, 1, w=np.sqrt(w))
        y0 = float(np.average(y, weights=w))
        xt, yt = np.array([r[xkey] for r in te]), np.array([r[ykey] for r in te])
        e, e0 = float(np.mean((a + b * xt - yt) ** 2)), float(np.mean((y0 - yt) ** 2))
        mse.append(e); mse0.append(e0)
        per[p] = {"rmse": e ** 0.5, "rmse_baseline": e0 ** 0.5, "frames": len(te)}
    if not mse:
        return {"rmse": float("nan"), "rmse_baseline": float("nan"), "skill": float("nan"), "places": per}
    return {"rmse": float(np.mean(mse)) ** 0.5, "rmse_baseline": float(np.mean(mse0)) ** 0.5,
            "skill": 1.0 - float(np.mean(mse)) / float(np.mean(mse0)), "places": per}


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    r = rank(np.concatenate([pos, neg]))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) - 1) / 2) / (len(pos) * len(neg)))


def analyse(rows: list[dict]) -> dict:
    ordinary = [r for r in rows if r["class"] == "ordinary"]
    conds = sorted({r["condition"] for r in ordinary}, key=lambda c: (next(r["place"] for r in ordinary if r["condition"] == c), c))
    truth = {k: cond_mean(ordinary, k) for k in ("blue_all.s_med", "blue_all.s_p10", "blue_all.h_med", "blue_all.h_p02", "blue_all.v_med", "blue_all.dark",
                                                  "orange_all.h_med", "orange_all.h_p98", "orange_all.s_med", "orange_all.s_p10", "orange_all.v_med",
                                                  "v_med_below", "ext_share_bg")}
    need = {c for c in conds if truth["blue_all.s_p10"].get(c, 999) < FIXED_BLUE_S}
    out = {"conditions": conds, "truth": truth, "need": sorted(need), "readings": {}, "frames": len(ordinary)}
    for name in cm.READINGS:
        k = f"{name}.w"
        cmn = cond_mean(ordinary, k)
        vals = np.array([r[k] for r in ordinary])
        ok = np.isfinite(vals)
        med = {c: float(np.median([r[k] for r in ordinary if r["condition"] == c and np.isfinite(r[k])] or [np.nan])) for c in conds}
        dev = [(r[k] - med[r["condition"]], r) for r in ordinary if np.isfinite(r[k]) and np.isfinite(med[r["condition"]])]
        within = float(np.sqrt(np.mean([(r[k] - cmn[r["condition"]]) ** 2 for r in ordinary if np.isfinite(r[k])]))) if ok.any() else float("nan")
        between = float(np.std([cmn[c] for c in conds if c in cmn])) if cmn else float("nan")
        worst = sorted(dev, key=lambda t: -abs(t[0]))[:3]
        fooled = {s: float(np.mean([d for d, r in dev if r["scene"] == s] or [np.nan])) for s in ("close", "clutter", "neg")}
        fooled_max = {s: float(max([abs(d) for d, r in dev if r["scene"] == s] or [np.nan])) for s in ("close", "clutter", "neg")}
        pos = np.array([r[k] for r in ordinary if r["condition"] in need and np.isfinite(r[k])])
        neg = np.array([r[k] for r in ordinary if r["condition"] not in need and np.isfinite(r[k])])
        thr = float(np.percentile(pos, 10)) if len(pos) else float("nan")
        xs = lambda key: [cmn.get(c, np.nan) for c in conds]  # noqa: E731
        ys = lambda key: [truth[key].get(c, np.nan) for c in conds]  # noqa: E731
        out["readings"][name] = {
            "valid": int(ok.sum()), "cond_mean": cmn,
            "r_blue_s": pearson(xs(k), ys("blue_all.s_med")), "rho_blue_s": spearman(xs(k), ys("blue_all.s_med")),
            "r_blue_h": pearson(xs(k), ys("blue_all.h_med")), "rho_blue_h": spearman(xs(k), ys("blue_all.h_med")),
            "r_orange_h": pearson(xs(k), ys("orange_all.h_med")), "rho_orange_h": spearman(xs(k), ys("orange_all.h_med")),
            "lopo_blue_s": lopo(ordinary, k, "blue_all.s_med"), "lopo_blue_h": lopo(ordinary, k, "blue_all.h_med"),
            "lopo_orange_h": lopo(ordinary, k, "orange_all.h_med"),
            "within_sd": within, "between_sd": between, "ratio": between / within if within else float("nan"),
            "worst": [{"stem": r["stem"], "dev": float(d), "value": r[k], "cond_median": med[r["condition"]]} for d, r in worst],
            "fooled_mean": fooled, "fooled_max": fooled_max,
            "auc_need": auc(pos, neg), "thr_p10_need": thr, "false_alarms": int((neg >= thr).sum()) if len(pos) else -1,
            "need_frames": int(len(pos)), "other_frames": int(len(neg)),
            "need_min": float(pos.min()) if len(pos) else float("nan"), "other_max": float(neg.max()) if len(neg) else float("nan"),
        }
    return out


def fmt(x, d=2) -> str:
    return "n/a" if x is None or not np.isfinite(x) else f"{x:+.{d}f}" if d and abs(x) < 10 and False else f"{x:.{d}f}"


def write(a: dict, rows: list[dict]) -> str:
    R = a["readings"]
    L = ["# The readings compared (part A of the 2026-11-26 light experiment)", "",
         "`python barrels/experiments/2026-11-26_light/measure.py` then `table.py`. Train frames only (the ordinary conditions: "
         f"{a['frames']} frames, {len(a['conditions'])} conditions, 8 places). In-sample unless a column says leave one place out. "
         "A reading is a set of pixels picked without knowing where a barrel is; its number is the median of (R - B) / (R + G + B) over them: "
         "0 = neutral light, positive = yellow. The truth it is compared with is the labelled paint inside the hand boxes (body and stripe bands).", "",
         "## The one table", "",
         "| reading | frames it speaks on | r / rho with the blue paint's S (17 conditions) | r / rho with the blue paint's hue | r / rho with the orange paint's hue | "
         "leave one place out, blue S: skill (error against the baseline, S units) | leave one place out, blue hue: skill | leave one place out, orange hue: skill | "
         "spread inside a condition / between conditions (ratio) | close-up / clutter / empty frame: mean shift from the condition's median | "
         "warm-needing frames against the others: AUC | other frames at least as warm as the 10th percentile of the needing ones |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name in cm.READINGS:
        r = R[name]
        lb, lh, lo_ = r["lopo_blue_s"], r["lopo_blue_h"], r["lopo_orange_h"]
        L.append(f"| `{name}`: {cm.READING_NOTES[name]} | {r['valid']} of {a['frames']} | {fmt(r['r_blue_s'])} / {fmt(r['rho_blue_s'])} | "
                 f"{fmt(r['r_blue_h'])} / {fmt(r['rho_blue_h'])} | {fmt(r['r_orange_h'])} / {fmt(r['rho_orange_h'])} | "
                 f"{fmt(lb['skill'])} ({fmt(lb['rmse'], 0)} against {fmt(lb['rmse_baseline'], 0)}) | {fmt(lh['skill'])} | {fmt(lo_['skill'])} | "
                 f"{fmt(r['within_sd'], 3)} / {fmt(r['between_sd'], 3)} ({fmt(r['ratio'], 1)}) | "
                 f"{fmt(r['fooled_mean']['close'], 3)} / {fmt(r['fooled_mean']['clutter'], 3)} / {fmt(r['fooled_mean']['neg'], 3)} | "
                 f"{fmt(r['auc_need'], 3)} | {r['false_alarms']} of {r['other_frames']} |")
    L += ["", f"Warm-needing conditions (the blue paint's 10th percentile of S is under the fixed floor of 113): {', '.join(a['need'])}.", "",
          "## Per condition: the paint, and each reading's mean", "",
          "| condition | blue S median / 10th pct | blue hue median / 2nd pct | blue brightness, share under the gate | orange hue median / 98th pct | orange S 10th pct | "
          + " | ".join(f"`{n}`" for n in cm.READINGS) + " |",
          "|---|---|---|---|---|---|" + "---|" * len(cm.READINGS)]
    T = a["truth"]
    g = lambda k, c, d=0: fmt(T[k].get(c, np.nan), d)  # noqa: E731
    for c in a["conditions"]:
        L.append(f"| {c}{' (needs)' if c in a['need'] else ''} | {g('blue_all.s_med', c)} / {g('blue_all.s_p10', c)} | {g('blue_all.h_med', c)} / {g('blue_all.h_p02', c)} | "
                 f"{g('blue_all.v_med', c)}, {g('blue_all.dark', c, 2)} | {g('orange_all.h_med', c, 1)} / {g('orange_all.h_p98', c, 1)} | {g('orange_all.s_p10', c)} | "
                 + " | ".join(fmt(R[n]["cond_mean"].get(c, np.nan), 2) for n in cm.READINGS) + " |")
    ext = [r for r in rows if r["class"] == "extreme"]
    if ext:
        L += ["", "Extreme conditions (report only; not in any number above):", "",
              "| condition | blue S median | blue hue median | orange hue median | " + " | ".join(f"`{n}`" for n in cm.READINGS) + " |",
              "|---|---|---|---|" + "---|" * len(cm.READINGS)]
        for c in sorted({r["condition"] for r in ext}):
            rr = [r for r in ext if r["condition"] == c]
            m = lambda k: fmt(float(np.nanmean([r[k] for r in rr])) if np.isfinite([r[k] for r in rr]).any() else np.nan, 0 if "." in k and not k.endswith(".w") else 2)  # noqa: E731
            L.append(f"| {c} | {m('blue_all.s_med')} | {m('blue_all.h_med')} | {m('orange_all.h_med')} | " + " | ".join(m(f"{n}.w") for n in cm.READINGS) + " |")
    L += ["", "## Where each reading is furthest off (the three frames furthest from their condition's median)", ""]
    for name in cm.READINGS:
        L.append(f"- `{name}`: " + "; ".join(f"{w['stem'].replace('4A8B_', '')} reads {w['value']:.2f} (its condition {w['cond_median']:.2f})" for w in R[name]["worst"]))
    L += ["", "## Largest shift on a close-up, a clutter and an empty frame (absolute, any condition)", "",
          "| reading | close-up | clutter | empty |", "|---|---|---|---|"]
    for name in cm.READINGS:
        f = R[name]["fooled_max"]
        L.append(f"| `{name}` | {fmt(f['close'], 2)} | {fmt(f['clutter'], 2)} | {fmt(f['neg'], 2)} |")
    text = "\n".join(L) + "\n"
    (cm.OUT / "readings.md").write_text(text)
    (cm.OUT / "readings.json").write_text(json.dumps(a, indent=1, default=float) + "\n")
    return text


def main() -> int:
    rows = load()
    print(write(analyse(rows), rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
