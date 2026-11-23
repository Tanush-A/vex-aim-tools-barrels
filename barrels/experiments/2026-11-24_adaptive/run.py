#!/usr/bin/env python3
"""TODO F updated, and the test of the adaptive color rule. One command, no arguments, re-run on whatever
conditions exist (the plan and the acceptance rule: PREREG.md in this folder, committed before the rule's test).

    python barrels/experiments/2026-11-24_adaptive/run.py       # exit 0 = the rule passes its PREREG acceptance, 1 = it does not
    python barrels/experiments/2026-11-24_adaptive/run.py --freeze   # once, 2026-11-23: also write rule_frozen_<date>.json

What happens, in order:

1. ``load``         train frames with box labels (test frames refused before any image is opened), grouped into
   conditions; each gets its place and light kind (``data/conditions.json``) and a class: parked extreme (the wood
   lamp ladder, the black table), excluded (brightness 1), ``extreme (ceiling)`` (even its own best thresholds find
   under half its barrels), else ordinary.
2. ``part_a``       TODO F updated: hand against box; Spearman at condition and at place level; the nested
   one-feature prediction leave one PLACE out (and leave one condition out beside it); residuals by light kind.
3. ``fit_rule`` / ``lopo_detection``   the rule of the PREREG (three terms, a line through the home point each),
   fit on the slider labels with every place weighted equally; leave one place out: fit without the place,
   detect on its frames, fixed against adaptive.
4. ``gate_check``   the never-regress gate with the rule ON (fit on all places) against the stored baseline, next
   to the same gate for the fixed model (it fails today on one known box: TODO A9).
5. ``frozen_check`` the copy of the rule frozen on 2026-11-23, applied to the places that are new since then.
6. ``write``        summary.md (one page), analysis.md, CSVs, rule.json, model_adaptive.json, gate.txt,
   config.json; a copy under runs/. Exit 0 / 1 = pass / fail of the acceptance (PREREG part C).
"""
from __future__ import annotations

import argparse
import csv
import datetime
import importlib.util
import json
import math
import shutil
import sys
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import adaptive as ad, conditions as cd, detector as det, gate as gt, hsrel as hr, pipeline as pl  # noqa: E402
from barrels import report as rp, worldmap_bridge as wb  # noqa: E402
from barrels.io import PKG_ROOT, parse_name  # noqa: E402

_spec = importlib.util.spec_from_file_location("frel", HERE.parent / "2026-11-18_hs_relation" / "run.py")
frel = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(frel)

OUT = PKG_ROOT / "results" / "2026-11-24_adaptive"
FROZEN_GLOB = "rule_frozen_*.json"
NAN = float("nan")
CAM = frel.CAM
ORD, EXT_CEIL = hr.ORDINARY, "extreme (ceiling)"
CEILING_SHARE = 0.5          # PREREG: under half the barrels with its own best thresholds -> extreme (ceiling)

# ---- the rule (PREREG part B): threshold, feature, max_delta
RULE = (("orange_h_lo", "orange_peak_h", 10.0), ("orange_h_hi", "orange_peak_h", 10.0), ("blue_s_lo", "blue_s_p90", 60.0))
# ---- acceptance (PREREG part C)
MIN_HAND_PLACES = 5
MIN_MORE_FOUND, MIN_PLACES_GAINING = 3, 2
MAX_MORE_FALSE = 2
MAX_SCORE_DROP = 0.02
FROZEN_MAX_MORE_FALSE = 1
UNIT = {t: ("S" if t.endswith("s_lo") else "hue") for t in hr.THRESHOLDS}


def fmt(x, nd: int = 0) -> str:
    return "-" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{x:.{nd}f}"


def name(key: str) -> str:
    return frel.ALIAS.get(key, key)


# ---------------------------------------------------------------- 1. load and classify

def load(base: pl.Model) -> tuple[dict, dict, dict]:
    data = frel.load(base)
    cond = frel.per_condition(data)
    for k, c in cond.items():
        i = cd.info(k)
        c["place"], c["light"], c["guessed"] = i.place, i.light, i.guessed
    res, _ = frel.detect(data, cond, base, {})               # fixed, box per frame, box median, hand median
    for k, c in cond.items():
        if c["class"] != ORD:
            continue
        st = data["conds"][k]["stems"]
        cells = [frel.cell(res, a, st) for a in ("box per frame", "hand median")]
        best = max((x.found for x in cells if x is not None), default=0)
        barrels = cells[0].barrels if cells[0] is not None else 0
        c["ceiling_found"], c["ceiling_barrels"] = best, barrels
        if barrels and best < CEILING_SHARE * barrels:
            c["class"] = EXT_CEIL
    return data, cond, res


# ---------------------------------------------------------------- 2. part A: TODO F updated

def place_means(keys, cond, field, sub) -> tuple[list[str], np.ndarray]:
    places = list(dict.fromkeys(cond[k]["place"] for k in keys))
    vals = np.array([np.nanmean([cond[k][field][sub] for k in keys if cond[k]["place"] == p]) if any(np.isfinite(cond[k][field][sub]) for k in keys if cond[k]["place"] == p) else NAN
                     for p in places])
    return places, vals


def part_a(cond: dict, fixed: dict) -> dict:
    ords = [k for k, c in cond.items() if c["class"] == ORD]
    out = {"targets": {}}
    for target in ("hand", "box"):
        ks = [k for k in ords if any(np.isfinite(cond[k][target][t]) for t in hr.THRESHOLDS)]
        x_all = np.array([[cond[k]["feat"][f] for f in hr.FEATURES] for k in ks], float).reshape(len(ks), len(hr.FEATURES))
        per_t = {}
        for t in hr.THRESHOLDS:
            y = np.array([cond[k][target][t] for k in ks], float)
            ok = np.isfinite(y)
            kk = [k for k, o in zip(ks, ok) if o]
            x, y = x_all[ok], y[ok]
            g = [cond[k]["place"] for k in kk]
            r = {"n_cond": len(kk), "n_place": len(set(g)), "keys": kk}
            # Spearman for the two primary pairs, condition level and place level
            r["spearman"] = {}
            for f in hr.PRIMARY[t]:
                j = hr.FEATURES.index(f)
                fin = np.isfinite(x[:, j]) if len(y) else np.zeros(0, bool)
                cl = hr.perm_pvalue(x[fin, j], y[fin], frel.N_PERM, frel.SEED)
                pl_, fy = place_means(kk, cond, target, t)
                _, fx = place_means(kk, cond, "feat", f)
                fin2 = np.isfinite(fx) & np.isfinite(fy)
                pp = hr.perm_pvalue(fx[fin2], fy[fin2], frel.N_PERM, frel.SEED)
                r["spearman"][f] = {"cond": cl, "place": pp}
            if len(y) >= 2:
                lopo = hr.loco(x, y, 1, groups=g)
                loco = hr.loco(x, y, 1)
                mean_other_places = [float(np.mean([y[j] for j in range(len(y)) if g[j] != g[i]])) if any(gg != g[i] for gg in g) else NAN for i in range(len(y))]
                r["rows"] = [{"condition": k, "place": g[i], "light": cond[k]["light"], "target": float(y[i]), "fixed": fixed[t],
                              "lopo": lopo[i]["pred"], "lopo_feats": "+".join(hr.FEATURES[j] for j in lopo[i]["feats"]), "lopo_fallback": lopo[i]["fallback"],
                              "loco": loco[i]["pred"], "loco_feats": "+".join(hr.FEATURES[j] for j in loco[i]["feats"]),
                              "mean_other_places": mean_other_places[i]} for i, k in enumerate(kk)]
            else:
                r["rows"] = []
            per_t[t] = r
        out["targets"][target] = per_t
    return out


def mae(rows, col, by_place: bool = True) -> float:
    """Mean |col - target|: over places (each place's mean over its conditions) when ``by_place``, else rows."""
    rows = [r for r in rows if math.isfinite(r[col])]
    if not rows:
        return NAN
    if not by_place:
        return float(np.mean([abs(r[col] - r["target"]) for r in rows]))
    places = dict.fromkeys(r["place"] for r in rows)
    return float(np.mean([np.mean([abs(r[col] - r["target"]) for r in rows if r["place"] == p]) for p in places]))


def wins_by_place(rows, col) -> tuple[int, int]:
    places = list(dict.fromkeys(r["place"] for r in rows if math.isfinite(r[col])))
    w = sum(np.mean([abs(r[col] - r["target"]) for r in rows if r["place"] == p]) < np.mean([abs(r["fixed"] - r["target"]) for r in rows if r["place"] == p]) for p in places)
    return int(w), len(places)


# ---------------------------------------------------------------- 3. the rule

def home_refs(data: dict) -> dict[str, float]:
    st = data["conds"][hr.REF_CONDITION]["stems"]
    return {f: float(np.nanmean([data["frames"][s]["feat"][f] for s in st])) for _, f, _ in RULE}


def hand_rows(cond: dict, exclude_place: str | None = None) -> list[str]:
    return [k for k, c in cond.items() if c["class"] == ORD and c["hand_frames"] and c["place"] != exclude_place]


def fit_rule(cond: dict, fixed: dict, refs: dict, keys: list[str]) -> list[ad.Term]:
    w = ad.place_weights([cond[k]["place"] for k in keys]) if keys else []
    out = []
    for t, f, md in RULE:
        b = ad.fit_slope([cond[k]["feat"][f] for k in keys], [cond[k]["hand"][t] for k in keys], fixed[t], refs[f], w) if keys else 0.0
        out.append(ad.Term(t, f, b, refs[f], md))
    return out


def with_rule(base: pl.Model, ts) -> pl.Model:
    import dataclasses
    return dataclasses.replace(base, cfg=dataclasses.replace(base.cfg, hs_adapt=ad.as_config_value(ts)))


def run_model(data: dict, stems: list[str], model: pl.Model, dcfg) -> dict:
    return {s: rp.score_frame(s, pl.segment(data["frames"][s]["frame"], model)[0], dcfg, CAM) for s in stems}


def lopo_detection(data, cond, base, fixed, refs) -> dict:
    """place -> {"terms": the rule fit without it, "n_train_places", "adaptive": {stem: scored}}; plus the fixed arm."""
    dcfg = det.DetConfig()
    places = list(dict.fromkeys(c["place"] for c in cond.values() if c["class"] == ORD))
    out = {"folds": {}, "fixed": {}, "adaptive": {}}
    for p in places:
        keys = hand_rows(cond, exclude_place=p)
        ts = fit_rule(cond, fixed, refs, keys)
        stems = [s for k, c in cond.items() if c["class"] == ORD and c["place"] == p for s in data["conds"][k]["stems"]]
        out["folds"][p] = {"terms": ts, "train_places": sorted({cond[k]["place"] for k in keys}), "fallback": not keys}
        out["adaptive"].update(run_model(data, stems, with_rule(base, ts), dcfg))
        out["fixed"].update(run_model(data, stems, base, dcfg))
    return out


def rule_thresholds(data, cond, base, ts, keys) -> dict[str, dict[str, float]]:
    """condition -> the rule's thresholds, median over the condition's frames (for the residuals)."""
    m = with_rule(base, ts)
    out = {}
    for k in keys:
        vals = [ad.frame_thresholds(data["frames"][s]["frame"], m) for s in data["conds"][k]["stems"]]
        out[k] = {t: float(np.median([v[t] for v in vals])) for t in hr.THRESHOLDS}
    return out


# ---------------------------------------------------------------- 4. the gate, 5. frozen

def model_file(base_path: Path, model: pl.Model, out: Path, label: str) -> Path:
    d = json.loads(Path(base_path).read_text())
    cfgd = model.cfg.to_dict()
    d["name"] = label
    d["config"] = cfgd
    d["config_hash"] = model.cfg.short_hash()
    d["model"]["cfg"] = cfgd
    out.write_text(json.dumps(d, indent=1))
    return out


def gate_check(model_path: Path) -> tuple[gt.GateResult, gt.GateResult]:
    base_arm = rp.Arm("candidate", wb.DEFAULT_MODEL)
    adapt_arm = rp.Arm("candidate", model_path)
    snaps = []
    for arm in (base_arm, adapt_arm):
        rep = rp.make_report(arm, arm)
        snaps.append(gt.snapshot(rep, made=datetime.date.today().isoformat()))
    baseline = gt.load_baseline()
    prot = gt.load_protected()
    return gt.compare(baseline, snaps[0], prot), gt.compare(baseline, snaps[1], prot)


def failing(res: gt.GateResult) -> set[str]:
    return {f"{r.set}|{r.scene}" for r in res.failures}


def latest_frozen() -> Path | None:
    files = sorted(HERE.glob(FROZEN_GLOB))
    return files[0] if files else None


# ---------------------------------------------------------------- 6. write

def cell_of(scored: dict, stems: list[str]):
    got = [scored[s] for s in stems if s in scored]
    return rp.summarize(got) if got and len(got) == len(stems) else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=None, help="write here instead of results/2026-11-24_adaptive (no copy under runs/)")
    ap.add_argument("--freeze", action="store_true", help="also write rule_frozen_<today>.json (once; refuses when one exists)")
    ap.add_argument("--no-gate", action="store_true", help="skip the gate (for a quick look; the run then FAILS clause C6)")
    args = ap.parse_args()
    out = args.out or OUT
    out.mkdir(parents=True, exist_ok=True)
    today, git = datetime.date.today().isoformat(), frel.git_state()
    base = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    fixed = hr.thresholds_of(base)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        data, cond, res = load(base)
        A = part_a(cond, fixed)
        refs = home_refs(data)
        all_keys = hand_rows(cond)
        rule_all = fit_rule(cond, fixed, refs, all_keys)
        L = lopo_detection(data, cond, base, fixed, refs)
        thr_rule = {}
        for p, fold in L["folds"].items():
            ks = [k for k in all_keys if cond[k]["place"] == p]
            thr_rule.update(rule_thresholds(data, cond, base, fold["terms"], ks))

    ords = [k for k, c in cond.items() if c["class"] == ORD]
    places = list(dict.fromkeys(cond[k]["place"] for k in ords))
    hand_places = sorted({cond[k]["place"] for k in all_keys})
    stems_of = {k: data["conds"][k]["stems"] for k in cond}

    # --- model file with the rule on (all places), the gate
    model_path = model_file(wb.DEFAULT_MODEL, with_rule(base, rule_all), out / "model_adaptive.json",
                            "hs eb863d84 + the adaptive rule of experiments/2026-11-24_adaptive (NOT adopted)")
    gate_fixed = gate_adapt = None
    if not args.no_gate:
        gate_fixed, gate_adapt = gate_check(model_path)
        (out / "gate.txt").write_text("=== FIXED MODEL (today's default) ===\n" + gt.format_gate(gate_fixed) + "\n\n=== RULE ON ===\n" + gt.format_gate(gate_adapt) + "\n")

    # --- frozen rule
    frozen_path = latest_frozen()
    if args.freeze:
        if frozen_path is not None:
            raise SystemExit(f"{frozen_path.name} exists: the rule is frozen once")
        frozen_path = HERE / f"rule_frozen_{today}.json"
        frozen_path.write_text(json.dumps({"date": today, "git": git, "terms": [t.as_tuple() for t in rule_all],
                                           "hand_places": hand_places, "places_seen": sorted({c["place"] for c in cond.values()}),
                                           "conditions_seen": sorted(cond)}, indent=1) + "\n")
    frozen = json.loads(frozen_path.read_text()) if frozen_path else None
    new_places = [p for p in places if frozen and p not in frozen["places_seen"]]
    frozen_res = {}
    if frozen and new_places:
        dcfg = det.DetConfig()
        fm = with_rule(base, ad.terms(frozen["terms"]))
        for k in ords:
            if cond[k]["place"] in new_places:
                frozen_res.update(run_model(data, stems_of[k], fm, dcfg))

    # --- per-condition detection table
    rows = []
    for k in ords:
        st = stems_of[k]
        cf, ca = cell_of(L["fixed"], st), cell_of(L["adaptive"], st)
        cz = cell_of(frozen_res, st) if cond[k]["place"] in new_places else None
        rows.append({"condition": k, "place": cond[k]["place"], "light": cond[k]["light"], "frames": len(st), "barrels": cf.barrels,
                     "fixed_found": cf.found, "fixed_false": cf.false, "fixed_neg": cf.neg_false, "fixed_clean_neg": cf.clean_neg_false, "fixed_score": cf.score,
                     "adapt_found": ca.found, "adapt_false": ca.false, "adapt_neg": ca.neg_false, "adapt_clean_neg": ca.clean_neg_false, "adapt_score": ca.score,
                     "frozen_found": cz.found if cz else None, "frozen_false": cz.false if cz else None,
                     "hand_found": (frel.cell(res, "hand median", st).found if cond[k]["hand_frames"] else None)})

    # --- acceptance
    tot = lambda col: sum(r[col] for r in rows)  # noqa: E731
    gain_places = sum(sum(r["adapt_found"] - r["fixed_found"] for r in rows if r["place"] == p) > 0 for p in places)
    C = {}
    C["C1"] = (len(hand_places) >= MIN_HAND_PLACES, f"{len(hand_places)} places with slider labels ({', '.join(hand_places) or 'none'}); {MIN_HAND_PLACES} needed")
    C["C2"] = (tot("adapt_found") - tot("fixed_found") >= MIN_MORE_FOUND and gain_places >= MIN_PLACES_GAINING,
               f"found {tot('adapt_found')} vs {tot('fixed_found')} fixed (+{tot('adapt_found') - tot('fixed_found')}; {MIN_MORE_FOUND} needed), more in {gain_places} places ({MIN_PLACES_GAINING} needed)")
    C["C3"] = (tot("adapt_false") - tot("fixed_false") <= MAX_MORE_FALSE, f"false boxes {tot('adapt_false')} vs {tot('fixed_false')} fixed (at most +{MAX_MORE_FALSE})")
    neg_bad = [name(r["condition"]) for r in rows if r["adapt_neg"] > r["fixed_neg"] or r["adapt_clean_neg"] > 0]
    C["C4"] = (not neg_bad, "no new box on an empty frame" if not neg_bad else f"new box(es) on an empty frame in {', '.join(neg_bad)}")
    drop = [name(r["condition"]) for r in rows if math.isfinite(r["fixed_score"]) and math.isfinite(r["adapt_score"]) and r["adapt_score"] < r["fixed_score"] - MAX_SCORE_DROP]
    C["C5"] = (not drop, "no condition loses more than 0.02" if not drop else f"score drops by more than 0.02 in {', '.join(drop)}")
    if gate_adapt is None:
        C["C6"] = (False, "gate not run (--no-gate)")
    else:
        added = sorted(failing(gate_adapt) - failing(gate_fixed))
        C["C6"] = (not added, f"the rule adds no failing gate row (the fixed model's own: {', '.join(sorted(failing(gate_fixed))) or 'none'})"
                   if not added else f"the rule adds failing gate rows: {', '.join(added)}")
    if new_places:
        fz = [r for r in rows if r["place"] in new_places]
        ok7 = sum(r["frozen_found"] for r in fz) >= sum(r["fixed_found"] for r in fz) and sum(r["frozen_false"] for r in fz) <= sum(r["fixed_false"] for r in fz) + FROZEN_MAX_MORE_FALSE
        C["C7"] = (ok7, f"on the {len(new_places)} new place(s) ({', '.join(new_places)}) the frozen rule finds {sum(r['frozen_found'] for r in fz)} vs {sum(r['fixed_found'] for r in fz)} fixed, "
                        f"false {sum(r['frozen_false'] for r in fz)} vs {sum(r['fixed_false'] for r in fz)}")
    else:
        C["C7"] = (True, "not applicable: no place new since the frozen rule" + ("" if frozen else " (no frozen rule yet)"))
    passed = all(ok for ok, _ in C.values())

    # --- relation verdict per threshold (part A, hand target, leave one place out)
    def rel_line(target: str, t: str) -> str:
        r = A["targets"][target][t]
        rws = r["rows"]
        if not rws:
            return f"| {t} | {r['n_cond']} / {r['n_place']} | - | - | - | - | - |"
        fb = all(x["lopo_fallback"] for x in rws)
        w, n = wins_by_place(rws, "lopo")
        sp = r["spearman"][hr.PRIMARY[t][0]]["place"]
        return (f"| {t} | {r['n_cond']} / {r['n_place']} | {fmt(mae(rws, 'fixed'), 1)} | {fmt(mae(rws, 'mean_other_places'), 1)} | "
                f"{fmt(mae(rws, 'lopo'), 1)}{' (fallback: too few places)' if fb else ''} | {fmt(mae(rws, 'loco', by_place=False), 1)} | "
                f"{w} of {n} | {hr.PRIMARY[t][0]}: {fmt(sp['rho'], 2)} (p {fmt(sp['p'], 2)}, n {sp['n']}) |")

    def rel_shows(target: str, t: str) -> bool:
        rws = A["targets"][target][t]["rows"]
        if not rws or all(x["lopo_fallback"] for x in rws):
            return False
        w, n = wins_by_place(rws, "lopo")
        return mae(rws, "lopo") < min(mae(rws, "fixed"), mae(rws, "mean_other_places")) and w >= math.ceil(2 * n / 3)

    shows = {tg: [t for t in hr.THRESHOLDS if rel_shows(tg, t)] for tg in ("hand", "box")}

    # --- hand vs box
    hk = [k for k in ords if cond[k]["hand_frames"]]
    hb = {t: float(np.nanmedian([abs(cond[k]["hand"][t] - cond[k]["box"][t]) for k in hk])) if hk else NAN for t in hr.THRESHOLDS}

    # --- residuals by light kind: the rule's thresholds against the hand labels (LOPO), and part A's nested line
    kinds = list(dict.fromkeys(cond[k]["light"] for k in ords))

    def resid_table(pairs) -> list[str]:
        """pairs: threshold -> list of (light, residual)"""
        head = "| threshold | " + " | ".join(f"{kd} (n)" for kd in kinds) + " |"
        lines = [head, "|---|" + "---|" * len(kinds)]
        for t, lst in pairs.items():
            cells = []
            for kd in kinds:
                v = [r for l_, r in lst if l_ == kd and math.isfinite(r)]
                cells.append(f"{fmt(np.mean(np.abs(v)), 1)} / {fmt(np.mean(v), 1)} ({len(v)})" if v else "-")
            lines.append(f"| {t} | " + " | ".join(cells) + " |")
        return lines

    res_rule = {t: [(cond[k]["light"], cond[k]["hand"][t] - thr_rule[k][t]) for k in hk if k in thr_rule] for t, _, _ in RULE}
    res_fixed = {t: [(cond[k]["light"], cond[k]["hand"][t] - fixed[t]) for k in hk] for t, _, _ in RULE}
    res_line = {t: [(x["light"], x["target"] - x["lopo"]) for x in A["targets"]["box"][t]["rows"]] for t in hr.THRESHOLDS}
    mixed_flag = []
    for t, lst in list(res_rule.items()) + [(f"{t} (box, nested line)", v) for t, v in res_line.items()]:
        mx = [abs(r) for l_, r in lst if l_ == "mixed" and math.isfinite(r)]
        ot = [abs(r) for l_, r in lst if l_ != "mixed" and math.isfinite(r)]
        if len(mx) >= 2 and ot and np.mean(mx) > 2 * np.mean(ot):
            mixed_flag.append(t)
    n_mixed = sum(cond[k]["light"] == "mixed" for k in ords)

    # ================================================================ summary.md (one page)
    guessed = [k for k in cond if cond[k]["guessed"]]
    S = [f"# Adaptive color rule: {'PASS' if passed else 'FAIL'} — {today}, git {git}", "",
         f"One command: `python barrels/experiments/2026-11-24_adaptive/run.py` (plan and acceptance: `PREREG.md`). Train frames only; "
         f"the {data['n_test']} test frames are refused before any image is opened. Nothing is adopted; the default model is unchanged (`eb863d84`).", "",
         f"**Data.** {len(ords)} ordinary conditions at {len(places)} places; slider labels on {len(all_keys)} conditions at "
         f"**{len(hand_places)} independent places** ({', '.join(hand_places) or 'none'}). "
         + ("Extreme (ceiling: under half the barrels even with its own best thresholds): " + ", ".join(name(k) for k, c in cond.items() if c["class"] == EXT_CEIL) + ". " if any(c["class"] == EXT_CEIL for c in cond.values()) else "")
         + "Parked extreme: the wood lamp ladder, the black table."
         + (f" **Not in `data/conditions.json` (place and light guessed from the tags):** {', '.join(guessed)}." if guessed else ""), "",
         "## 1. Does a relation show? (leave one PLACE out; the honest test)", ""]
    for tg in ("hand", "box"):
        S.append(f"**{tg} target**: " + (f"a frame-histogram line beats the fixed value and the mean of the other places, in two thirds of the places, for: **{', '.join(shows[tg])}**." if shows[tg]
                                         else "**no threshold** is predicted from the frame's histogram better than by the fixed value (or the mean of the other places)."))
    S += ["", "| threshold | conditions / places | fixed | mean of other places | nested line, leave one place out | leave one condition out (flatters) | LOPO prediction better than fixed in (places) | place-level Spearman, primary feature |",
          "|---|---|---|---|---|---|---|---|"]
    S += [rel_line("hand", t) for t in hr.THRESHOLDS]
    S += ["", "Hand target above (mean |error| per place, then over places; hue or S units). With fewer than 4 hand-labelled places no feature can be chosen inside the loop and the line falls back to the mean of the others. "
          "The box-target version of this table is in `analysis.md`.", "",
          "## 2. Hand labels against box-derived thresholds", "",
          f"Median |hand − box| over {len(hk)} conditions: " + "; ".join(f"{t} {fmt(hb[t], 1)}" for t in hr.THRESHOLDS)
          + ". The 2026-11-18 PREREG lets box stand in for hand at ≤ 3 hue and ≤ 20 S units: "
          + ("it can." if all(hb[t] <= (20 if UNIT[t] == "S" else 3) for t in hr.THRESHOLDS if math.isfinite(hb[t])) and hk else "**it cannot**; box is a cross-check only."), "",
          "## 3. Mixed light", "",
          f"Mixed-light ordinary conditions: {n_mixed}. Residual (hand − rule's threshold, leave one place out), mean |r| / mean r (n) by light kind:", ""]
    S += resid_table(res_rule)
    S += ["", ("**Flag: mixed light sits off the line** (mean |residual| > 2 × the others') on " + ", ".join(mixed_flag) + "." if mixed_flag
               else ("No flag." if n_mixed >= 2 else f"Not judged: {n_mixed} mixed condition(s); 2 needed.")) + " The fixed model's residuals and the box-target nested line are in `analysis.md`.", "",
          "## 4. The rule and its test", "",
          "Rule (PREREG part B): `threshold = fixed + b · (feature − home's feature)`, clipped, per frame from its own histogram; fit with every place weighted equally. "
          "Fit on all hand-labelled places now: " + "; ".join(f"`{t.threshold}` ← `{t.feature}`: b = {t.slope:+.3f} (home {t.f_ref:.1f}, clip ±{t.max_delta:g})" for t in rule_all) + ". "
          + "Slope across the leave-one-place-out folds: " + "; ".join(
              f"{t} {min(sl):+.3f} to {max(sl):+.3f}" + (" (**the sign flips**)" if min(sl) < 0 < max(sl) else "")
              for t, sl in ((t, [x.slope for f in L["folds"].values() if not f["fallback"] for x in f["terms"] if x.threshold == t]) for t, _, _ in RULE) if sl) + ".", "",
          "Leave one place out, per condition: found / barrels (false boxes; boxes on empty frames).", "",
          "| condition | place | light | fixed | adaptive | hand labels (ceiling, not a method) |" + (" frozen rule |" if new_places else ""), "|---|---|---|---|---|---|" + ("---|" if new_places else "")]
    for r in rows:
        S.append(f"| {name(r['condition'])} | {r['place']} | {r['light']} | {r['fixed_found']} / {r['barrels']} ({r['fixed_false']}; {r['fixed_neg']}) | "
                 f"{r['adapt_found']} / {r['barrels']} ({r['adapt_false']}; {r['adapt_neg']}) | {'-' if r['hand_found'] is None else r['hand_found']} |"
                 + (f" {'-' if r['frozen_found'] is None else str(r['frozen_found']) + ' (' + str(r['frozen_false']) + ')'} |" if new_places else ""))
    S.append(f"| **total** | | | {tot('fixed_found')} / {tot('barrels')} ({tot('fixed_false')}; {tot('fixed_neg')}) | {tot('adapt_found')} / {tot('barrels')} ({tot('adapt_false')}; {tot('adapt_neg')}) | |" + (" |" if new_places else ""))
    S += ["", "**Acceptance (PREREG part C):**", ""]
    S += [f"- {c}: {'pass' if ok else '**FAIL**'} — {txt}" for c, (ok, txt) in C.items()]
    S += ["", f"**Verdict: {'PASS — proposed, not adopted (walkthrough with Tanush first).' if passed else 'FAIL — the default stays the fixed model.'}**", "",
          "Files: `analysis.md` (part A in full), `detection.csv`, `per_condition.csv`, `rule.json`, `model_adaptive.json` (`tools/report.py --gate --cand-model` takes it), `gate.txt`, `config.json`."]
    summary = "\n".join(S) + "\n"
    (out / "summary.md").write_text(summary)

    # ================================================================ analysis.md (part A in full)
    AL = [f"# Part A in full: TODO F updated — {today}, git {git}", "",
          "Conditions (class, place, light, frames, hand-labelled frames, ceiling found / barrels):", "",
          "| condition | class | place | light | frames | hand | ceiling |", "|---|---|---|---|---|---|---|"]
    for k, c in cond.items():
        AL.append(f"| {name(k)} | {c['class']} | {c['place']} | {c['light']}{' (guessed)' if c['guessed'] else ''} | {c['frames']} | {c['hand_frames']} | "
                  f"{c.get('ceiling_found', '-')} / {c.get('ceiling_barrels', '-')} |")
    AL += ["", "## Targets per ordinary condition (hand, box, hand − box)", "", "| condition | target | " + " | ".join(hr.THRESHOLDS) + " |", "|---|---|" + "---|" * 6,
           "| adopted | fixed | " + " | ".join(fmt(fixed[t]) for t in hr.THRESHOLDS) + " |"]
    for k in ords:
        c = cond[k]
        AL.append(f"| {name(k)} | box | " + " | ".join(fmt(c["box"][t]) for t in hr.THRESHOLDS) + " |")
        if c["hand_frames"]:
            AL.append("| | hand | " + " | ".join(fmt(c["hand"][t]) for t in hr.THRESHOLDS) + " |")
            AL.append("| | hand − box | " + " | ".join(fmt(c["hand"][t] - c["box"][t]) for t in hr.THRESHOLDS) + " |")
    for tg in ("hand", "box"):
        AL += ["", f"## Prediction, {tg} target: leave one place out (lead) and leave one condition out", "",
               "| threshold | conditions / places | fixed | mean of other places | nested line, LOPO | LOCO (flatters) | LOPO prediction better than fixed in (places) | place-level Spearman, primary feature |", "|---|---|---|---|---|---|---|---|"]
        AL += [rel_line(tg, t) for t in hr.THRESHOLDS]
        AL += ["", "Features chosen inside the loop (LOPO / LOCO), per threshold:", ""]
        for t in hr.THRESHOLDS:
            rws = A["targets"][tg][t]["rows"]
            ch = lambda col: ", ".join(f"{f or 'fallback'} ×{n}" for f, n in sorted({x[col]: sum(1 for y in rws if y[col] == x[col]) for x in rws}.items(), key=lambda kv: -kv[1]))  # noqa: E731
            AL.append(f"- {t}: LOPO {ch('lopo_feats') or '-'}; LOCO {ch('loco_feats') or '-'}")
        AL += ["", f"Spearman, primary pairs, {tg} target (condition level, then place level; permutation p):", "", "| threshold | feature | rho cond (n) | p | rho place (n) | p |", "|---|---|---|---|---|---|"]
        for t in hr.THRESHOLDS:
            for f, s in A["targets"][tg][t]["spearman"].items():
                AL.append(f"| {t} | {f} | {fmt(s['cond']['rho'], 2)} ({s['cond']['n']}) | {fmt(s['cond']['p'], 3)} | {fmt(s['place']['rho'], 2)} ({s['place']['n']}) | {fmt(s['place']['p'], 3)} |")
    AL += ["", "## Residuals by light kind", "", "Hand − the FIXED value (mean |r| / mean r (n)):", ""] + resid_table(res_fixed)
    AL += ["", "Box target − the nested line, leave one place out:", ""] + resid_table(res_line)
    AL += ["", "## The rule's leave-one-place-out folds", "", "| held-out place | training places with hand labels | b per term |", "|---|---|---|"]
    for p, f in L["folds"].items():
        AL.append(f"| {p} | {', '.join(f['train_places']) or 'none (b = 0: the fixed model)'} | " + "; ".join(f"{t.threshold} {t.slope:+.3f}" for t in f["terms"]) + " |")
    (out / "analysis.md").write_text("\n".join(AL) + "\n")

    # ================================================================ CSVs, json
    def dump(fname, rws):
        with (out / fname).open("w", newline="") as fh:
            if rws:
                w = csv.DictWriter(fh, fieldnames=list(rws[0])); w.writeheader(); w.writerows(rws)
    dump("detection.csv", rows)
    dump("per_condition.csv", [{"condition": k, "class": c["class"], "place": c["place"], "light": c["light"], "guessed": c["guessed"], "frames": c["frames"], "hand_frames": c["hand_frames"],
                                **{f"feat_{f}": c["feat"][f] for f in hr.FEATURES}, **{f"hand_{t}": c["hand"][t] for t in hr.THRESHOLDS}, **{f"box_{t}": c["box"][t] for t in hr.THRESHOLDS}}
                               for k, c in cond.items()])
    (out / "rule.json").write_text(json.dumps({"date": today, "git": git, "terms": [t.as_tuple() for t in rule_all], "hand_places": hand_places,
                                               "hand_conditions": all_keys, "home_refs": refs}, indent=1) + "\n")
    json.dump({"date": today, "git": git, "passed": passed, "clauses": {c: {"pass": ok, "text": txt} for c, (ok, txt) in C.items()},
               "rule": [list(r) for r in RULE], "frozen": frozen_path.name if frozen_path else None, "new_places": new_places,
               "relation_shows": shows, "hand_minus_box_median_abs": hb, "n_test_refused": data["n_test"],
               "conditions": {k: {"class": c["class"], "place": c["place"], "light": c["light"], "stems": stems_of[k]} for k, c in cond.items()}},
              (out / "config.json").open("w"), indent=1)
    if args.out is None:
        runs = out / "runs"; runs.mkdir(exist_ok=True)
        nn = 1 + max([int(p.name[:2]) for p in runs.iterdir() if p.is_dir() and p.name[:2].isdigit()] or [0])
        dest = runs / f"{nn:02d}_{today}_{git}_places{len(places)}_hand{len(hand_places)}"
        dest.mkdir()
        for p in out.iterdir():
            if p.is_file():
                shutil.copy2(p, dest / p.name)
    print(summary)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
