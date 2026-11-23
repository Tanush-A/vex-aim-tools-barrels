#!/usr/bin/env python3
"""Thresholds as RANGES, and the range-based adaptive rule R2. One command, no arguments, re-run on whatever slider
labels exist (the plan and the acceptance: PREREG.md in this folder, committed before this script existed).

    python barrels/experiments/2026-11-24_adaptive_range/run.py            # exit 0 = R2 passes C1-C7, 1 = it does not
    python barrels/experiments/2026-11-24_adaptive_range/run.py --freeze   # once, 2026-11-23: also write rule_range_frozen_<date>.json

What happens, in order:

1. ``load``        the 2026-11-24 adaptive experiment's loader (train frames with boxes; test frames refused before
   any image is opened; conditions, places, light kinds, classes incl. ``extreme (ceiling)``).
2. ``ranges``      for every slider-labelled train frame, the range of each threshold around his values (detector and
   pixel versions) and the joint check (``barrels.hsrange.analyse_frame``, in parallel over frames).
3. ``part 2``      condition ranges (intersection over the frames); leave one PLACE out: how often fixed, the mean of
   the other places, and a line on each histogram feature land inside the held-out condition's range.
4. ``R2``          the rule of PREREG part 3, fit per fold; detection leave one place out, fixed against R2; the gate
   with R2 on; the frozen copy on new places; clauses C1-C7.
5. ``write``       summary.md (one page, plain words), the CSVs, rule.json, model_r2.json, gate.txt, config.json;
   a copy under runs/.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime
import importlib.util
import json
import math
import os
import shutil
import sys
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import adaptive as ad, detector as det, hslabel as hl, hsrange as hx, hsrel as hr, io, pipeline as pl  # noqa: E402
from barrels import splits as sp, worldmap_bridge as wb  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

_spec = importlib.util.spec_from_file_location("adv", HERE.parent / "2026-11-24_adaptive" / "run.py")
adv = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(adv)

OUT = PKG_ROOT / "results" / "2026-11-24_adaptive_range"
FROZEN_GLOB = "rule_range_frozen_*.json"
NAN = float("nan")
ORD = hr.ORDINARY
# PREREG part 3: the primary frame-only feature per threshold, and the clip
R2_FEATURE = {"orange_h_lo": "orange_peak_h", "orange_h_hi": "orange_peak_h", "orange_s_lo": "orange_s_p90",
              "blue_h_lo": "blue_peak_h", "blue_h_hi": "blue_peak_h", "blue_s_lo": "blue_s_p90"}
MAX_DELTA = {t: (60.0 if t.endswith("s_lo") else 10.0) for t in hr.THRESHOLDS}
# PREREG part 1: "constrained"
NARROW = {t: (30 if t.endswith("s_lo") else 6) for t in hr.THRESHOLDS}
HOLD_SHARE, HOLD_S = 2 / 3, 0.5         # PREREG: "the range version holds" (a)
fmt = adv.fmt


def name(k: str) -> str:
    return adv.name(k)


# ---------------------------------------------------------------- 2. ranges

def compute_ranges(stems: list[str], jobs: int) -> dict[str, dict]:
    out = {}
    if jobs <= 1:
        for s in stems:
            out[s] = hx.analyse_frame(s)
            print(f"  ranges: {s}", flush=True)
        return out
    with cf.ProcessPoolExecutor(max_workers=jobs) as ex:
        futs = {ex.submit(hx.analyse_frame, s): s for s in stems}
        for f in cf.as_completed(futs):
            out[futs[f]] = f.result()
            print(f"  ranges: {futs[f]}", flush=True)
    return {s: out[s] for s in stems}


def is_clutter(stem: str) -> bool:
    return io.parse_name(stem)["scene"] == "clutter"


def cond_ranges(R: dict, stems: list[str], version: str = "det") -> dict[str, tuple[float, float, bool]]:
    """threshold -> (lo, hi, empty) over the frames' ranges; ``version`` 'det', 'pix' or 'confirmed'."""
    out = {}
    for t in hr.THRESHOLDS:
        rs = [(R[s]["confirmed"][t] if version == "confirmed" else R[s][version][t][:2]) for s in stems]
        out[t] = hx.intersect(rs)
    return out


# ---------------------------------------------------------------- 3. part 2

def place_rate(rows: list[dict], col: str) -> tuple[float, int, int]:
    """(mean over places of the share of a place's conditions hit, places with all hit, places)."""
    places = list(dict.fromkeys(r["place"] for r in rows))
    shares = [np.mean([r[col] for r in rows if r["place"] == p]) for p in places]
    return (float(np.mean(shares)) if shares else NAN), int(sum(s == 1 for s in shares)), len(places)


def part2(keys, cond, CR, fixed, f_home, version="det") -> dict[str, list[dict]]:
    """threshold -> one row per held-out (condition): hit flags of every predictor."""
    out = {}
    for t in hr.THRESHOLDS:
        rows = []
        for k in keys:
            p = cond[k]["place"]
            tr = [j for j in keys if cond[j]["place"] != p]
            r = CR[version][k][t]
            row = {"condition": k, "place": p, "lo": r[0], "hi": r[1], "empty": r[2], "fixed_hit": r[0] <= fixed[t] <= r[1]}
            if tr:
                w = ad.place_weights([cond[j]["place"] for j in tr])
                mids = [(CR[version][j][t][0] + CR[version][j][t][1]) / 2 for j in tr]
                m = float(np.sum(w * np.array(mids)) / w.sum())
                row["mean_pred"], row["mean_hit"] = m, r[0] <= m <= r[1]
                for f in hr.FEATURES:
                    x = [cond[j]["feat"][f] for j in tr]
                    xh = cond[k]["feat"][f]
                    b_ls = ad.fit_slope(x, mids, fixed[t], f_home[f], w)
                    b_iv, _ = hx.interval_slope(x, [CR[version][j][t][:2] for j in tr], fixed[t], f_home[f], math.inf, w)
                    for tag, b in (("line", b_ls), ("interval", b_iv)):
                        pr = fixed[t] + (b * (xh - f_home[f]) if math.isfinite(xh) else 0.0)
                        row[f"{f}|{tag}_pred"], row[f"{f}|{tag}_hit"] = pr, r[0] <= pr <= r[1]
            rows.append(row)
        out[t] = rows
    return out


# ---------------------------------------------------------------- 4. R2

def fit_r2(keys, cond, CR, fixed, f_home) -> tuple[list[ad.Term], dict]:
    """PREREG part 3 on the conditions ``keys`` (detector condition ranges). Returns (terms, per-threshold info)."""
    terms, info = [], {}
    if not keys:
        return terms, {t: {"why": "no training conditions"} for t in hr.THRESHOLDS}
    w = ad.place_weights([cond[k]["place"] for k in keys])
    for t in hr.THRESHOLDS:
        rs = [CR["det"][k][t][:2] for k in keys]
        if all(lo <= fixed[t] <= hi for lo, hi in rs):
            info[t] = {"why": "fixed inside every training range", "b": 0.0}
            continue
        f = R2_FEATURE[t]
        x = [cond[k]["feat"][f] for k in keys]
        b, hits = hx.interval_slope(x, rs, fixed[t], f_home[f], MAX_DELTA[t], w)
        h0 = hx.hits_at(x, rs, fixed[t], f_home[f], 0.0, MAX_DELTA[t], w)
        if hits > h0 + 1e-9 and b != 0:
            terms.append(ad.Term(t, f, b, f_home[f], MAX_DELTA[t]))
            info[t] = {"why": f"adapts on {f}", "b": b, "hits": hits, "hits_fixed": h0, "of": float(w.sum())}
        else:
            info[t] = {"why": "no line beats fixed on the training ranges", "b": 0.0, "hits": hits, "hits_fixed": h0, "of": float(w.sum())}
    return terms, info


def cond_rule_thresholds(data, keys, base, ts) -> dict[str, dict[str, float]]:
    m = adv.with_rule(base, ts)
    out = {}
    for k in keys:
        vals = [ad.frame_thresholds(data["frames"][s]["frame"], m) for s in data["conds"][k]["stems"]]
        out[k] = {t: float(np.median([v[t] for v in vals])) for t in hr.THRESHOLDS}
    return out


def latest_frozen() -> Path | None:
    files = sorted(HERE.glob(FROZEN_GLOB))
    return files[0] if files else None


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=None, help="write here instead of results/2026-11-24_adaptive_range (no copy under runs/)")
    ap.add_argument("--freeze", action="store_true", help="also write rule_range_frozen_<today>.json (once; refuses when one exists)")
    ap.add_argument("--no-gate", action="store_true", help="skip the gate (quick look; the run then FAILS clause C6)")
    ap.add_argument("--jobs", type=int, default=max(1, min(8, (os.cpu_count() or 2) - 1)), help="processes for the ranges")
    args = ap.parse_args()
    out = args.out or OUT
    out.mkdir(parents=True, exist_ok=True)
    today, git = datetime.date.today().isoformat(), adv.frel.git_state()
    base = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=adv.CAM).model
    fixed = hr.thresholds_of(base)

    print("1. loading (the 2026-11-24 loader; test frames refused)", flush=True)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        data, cond, _ = adv.load(base)
    splits = sp.load_splits()
    test = set(splits["test"])
    hand_stems = [s for k, c in cond.items() for s in data["conds"][k]["stems"] if data["frames"][s]["hand"] is not None]
    assert not set(hand_stems) & test, "a test frame among the slider-labelled stems"
    for s in hand_stems:
        hl.require_labelable(s, splits)
    home_st = data["conds"][hr.REF_CONDITION]["stems"]
    f_home = {f: float(np.nanmean([data["frames"][s]["feat"][f] for s in home_st])) for f in hr.FEATURES}

    print(f"2. ranges on {len(hand_stems)} slider-labelled train frames ({args.jobs} processes)", flush=True)
    R = compute_ranges(hand_stems, args.jobs)
    hk_all = [k for k, c in cond.items() if any(s in R for s in data["conds"][k]["stems"])]
    labelled = {k: [s for s in data["conds"][k]["stems"] if s in R] for k in hk_all}
    CR = {v: {k: cond_ranges(R, labelled[k], v) for k in hk_all} for v in ("det", "pix", "confirmed")}
    keys = [k for k in hk_all if cond[k]["class"] == ORD]
    hand_places = sorted({cond[k]["place"] for k in keys})

    # ---- part 1 summaries
    def widths(t, version, clutter=None):
        return [R[s][version][t][1] - R[s][version][t][0] for s in R if clutter is None or is_clutter(s) == clutter]
    why_count = {t: {} for t in hr.THRESHOLDS}
    for s in R:
        for t in hr.THRESHOLDS:
            for end, w in (("low end", R[s]["det"][t][2]), ("high end", R[s]["det"][t][3])):
                why_count[t].setdefault(end, {}).setdefault(w, 0)
                why_count[t][end][w] += 1
    one_step = sum(1 for s in R for t in hr.THRESHOLDS for e, a in ((R[s]["det"][t][0], -1), (R[s]["det"][t][1], 1))
                   if abs(e - R[s]["anchor"][t]) <= hx.STEPS[t] and R[s]["det"][t][2 if a < 0 else 3] not in (hx.OPEN, hx.OTHER_END))
    n_ends = 2 * len(R) * len(hr.THRESHOLDS)
    constrained = {}
    for t in hr.THRESHOLDS:
        outside = [k for k in keys if not (CR["det"][k][t][0] <= fixed[t] <= CR["det"][k][t][1])]
        med = float(np.median(widths(t, "det"))) if R else NAN
        constrained[t] = {"fixed_outside": outside, "median_width": med, "constrained": bool(outside) or med <= NARROW[t]}
    joint_ok = [s for s in R if R[s]["joint"]["confirmed"] >= HOLD_S]

    # ---- part 2
    P = {v: part2(keys, cond, CR, fixed, f_home, v) for v in ("det", "confirmed")}
    frame_hits = {}
    for t in hr.THRESHOLDS:
        fr = [s for k in keys for s in labelled[k]]
        frame_hits[t] = {"fixed": float(np.mean([R[s]["det"][t][0] <= fixed[t] <= R[s]["det"][t][1] for s in fr])) if fr else NAN}

    # ---- 4. R2: folds, detection, old rule on the range target
    print("3. R2: leave one place out", flush=True)
    dcfg = det.DetConfig()
    ords = [k for k, c in cond.items() if c["class"] == ORD]
    places = list(dict.fromkeys(cond[k]["place"] for k in ords))
    stems_of = {k: data["conds"][k]["stems"] for k in cond}
    r2_all, r2_info_all = fit_r2(keys, cond, CR, fixed, f_home)
    folds, fixed_sc, r2_sc, r2_thr = {}, {}, {}, {}
    refs_old = adv.home_refs(data)
    old_hand = adv.hand_rows(cond)
    old_thr = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        for p in places:
            tr = [k for k in keys if cond[k]["place"] != p]
            ts, info = fit_r2(tr, cond, CR, fixed, f_home)
            folds[p] = {"terms": ts, "info": info, "train_places": sorted({cond[k]["place"] for k in tr})}
            st = [s for k in ords if cond[k]["place"] == p for s in stems_of[k]]
            fixed_sc.update(adv.run_model(data, st, base, dcfg))
            r2_sc.update(adv.run_model(data, st, adv.with_rule(base, ts), dcfg))
            held = [k for k in keys if cond[k]["place"] == p]
            r2_thr.update(cond_rule_thresholds(data, held, base, ts))
            old_ts = adv.fit_rule(cond, fixed, refs_old, [k for k in old_hand if cond[k]["place"] != p])
            old_thr.update(cond_rule_thresholds(data, held, base, old_ts))

    # range-target hits of the rules (LOPO)
    rule_hits = {}
    for t in hr.THRESHOLDS:
        rows = []
        for k in keys:
            lo, hi, _ = CR["det"][k][t]
            rows.append({"place": cond[k]["place"], "fixed": lo <= fixed[t] <= hi, "r2": lo <= r2_thr[k][t] <= hi, "old": lo <= old_thr[k][t] <= hi})
        rule_hits[t] = {c: place_rate(rows, c)[0] for c in ("fixed", "r2", "old")} if rows else {}

    # gate
    model_path = adv.model_file(wb.DEFAULT_MODEL, adv.with_rule(base, r2_all), out / "model_r2.json",
                                "hs eb863d84 + the range rule R2 of experiments/2026-11-24_adaptive_range (NOT adopted)")
    gate_fixed = gate_r2 = None
    if not args.no_gate:
        print("4. the gate (fixed, then R2 on)", flush=True)
        gate_fixed, gate_r2 = adv.gate_check(model_path)
        (out / "gate.txt").write_text("=== FIXED MODEL (today's default) ===\n" + adv.gt.format_gate(gate_fixed) + "\n\n=== R2 ON ===\n" + adv.gt.format_gate(gate_r2) + "\n")

    # frozen
    frozen_path = latest_frozen()
    if args.freeze:
        if frozen_path is not None:
            raise SystemExit(f"{frozen_path.name} exists: the rule is frozen once")
        frozen_path = HERE / f"rule_range_frozen_{today}.json"
        frozen_path.write_text(json.dumps({"date": today, "git": git, "terms": [t.as_tuple() for t in r2_all], "hand_places": hand_places,
                                           "places_seen": sorted({c["place"] for c in cond.values()}), "conditions_seen": sorted(cond)}, indent=1) + "\n")
    frozen = json.loads(frozen_path.read_text()) if frozen_path else None
    new_places = [p for p in places if frozen and p not in frozen["places_seen"]]
    frozen_sc = {}
    if frozen and new_places:
        fm = adv.with_rule(base, ad.terms(frozen["terms"]))
        for k in ords:
            if cond[k]["place"] in new_places:
                frozen_sc.update(adv.run_model(data, stems_of[k], fm, dcfg))

    rows = []
    for k in ords:
        st = stems_of[k]
        cf_, ca = adv.cell_of(fixed_sc, st), adv.cell_of(r2_sc, st)
        cz = adv.cell_of(frozen_sc, st) if cond[k]["place"] in new_places else None
        rows.append({"condition": k, "place": cond[k]["place"], "light": cond[k]["light"], "frames": len(st), "barrels": cf_.barrels,
                     "fixed_found": cf_.found, "fixed_false": cf_.false, "fixed_neg": cf_.neg_false, "fixed_clean_neg": cf_.clean_neg_false, "fixed_score": cf_.score,
                     "adapt_found": ca.found, "adapt_false": ca.false, "adapt_neg": ca.neg_false, "adapt_clean_neg": ca.clean_neg_false, "adapt_score": ca.score,
                     "frozen_found": cz.found if cz else None, "frozen_false": cz.false if cz else None})

    tot = lambda col: sum(r[col] for r in rows)  # noqa: E731
    gain_places = sum(sum(r["adapt_found"] - r["fixed_found"] for r in rows if r["place"] == p) > 0 for p in places)
    C = {}
    C["C1"] = (len(hand_places) >= adv.MIN_HAND_PLACES, f"{len(hand_places)} places with slider labels ({', '.join(hand_places) or 'none'}); {adv.MIN_HAND_PLACES} needed")
    C["C2"] = (tot("adapt_found") - tot("fixed_found") >= adv.MIN_MORE_FOUND and gain_places >= adv.MIN_PLACES_GAINING,
               f"found {tot('adapt_found')} vs {tot('fixed_found')} fixed ({tot('adapt_found') - tot('fixed_found'):+d}; +{adv.MIN_MORE_FOUND} needed), more in {gain_places} places ({adv.MIN_PLACES_GAINING} needed)")
    C["C3"] = (tot("adapt_false") - tot("fixed_false") <= adv.MAX_MORE_FALSE, f"false boxes {tot('adapt_false')} vs {tot('fixed_false')} fixed (at most +{adv.MAX_MORE_FALSE})")
    neg_bad = [name(r["condition"]) for r in rows if r["adapt_neg"] > r["fixed_neg"] or r["adapt_clean_neg"] > 0]
    C["C4"] = (not neg_bad, "no new box on an empty frame" if not neg_bad else f"new box(es) on an empty frame in {', '.join(neg_bad)}")
    drop = [name(r["condition"]) for r in rows if math.isfinite(r["fixed_score"]) and math.isfinite(r["adapt_score"]) and r["adapt_score"] < r["fixed_score"] - adv.MAX_SCORE_DROP]
    C["C5"] = (not drop, "no condition loses more than 0.02" if not drop else f"score drops by more than 0.02 in {', '.join(drop)}")
    if gate_r2 is None:
        C["C6"] = (False, "gate not run (--no-gate)")
    else:
        added = sorted(adv.failing(gate_r2) - adv.failing(gate_fixed))
        C["C6"] = (not added, f"R2 adds no failing gate row (the fixed model's own: {', '.join(sorted(adv.failing(gate_fixed))) or 'none'})"
                   if not added else f"R2 adds failing gate rows: {', '.join(added)}")
    if new_places:
        fz = [r for r in rows if r["place"] in new_places]
        ok7 = sum(r["frozen_found"] for r in fz) >= sum(r["fixed_found"] for r in fz) and sum(r["frozen_false"] for r in fz) <= sum(r["fixed_false"] for r in fz) + adv.FROZEN_MAX_MORE_FALSE
        C["C7"] = (ok7, f"on the {len(new_places)} new place(s) ({', '.join(new_places)}) the frozen R2 finds {sum(r['frozen_found'] for r in fz)} vs {sum(r['fixed_found'] for r in fz)} fixed, "
                        f"false {sum(r['frozen_false'] for r in fz)} vs {sum(r['fixed_false'] for r in fz)}")
    else:
        C["C7"] = (True, "not applicable: no place new since the frozen R2" + ("" if frozen else " (no frozen R2 yet)"))
    passed = all(ok for ok, _ in C.values())

    # the one-line verdict (PREREG "the range version holds")
    hold_a = len(R) > 0 and len(joint_ok) >= HOLD_SHARE * len(R)
    cons = [t for t in hr.THRESHOLDS if constrained[t]["constrained"]]
    hold_b_t = [t for t in cons if rule_hits[t] and rule_hits[t]["r2"] > rule_hits[t]["fixed"] + 1e-9]
    hold_b = bool(hold_b_t)
    hold_c = all(C[c][0] for c in ("C2", "C3", "C4", "C5", "C6"))
    holds = hold_a and hold_b and hold_c

    # ================================================================ summary.md
    n_prop = sum(1 for s in R if R[s]["proposed"])
    n_unmoved = sum(1 for s in R if R[s]["proposed"] and R[s]["moved"] is False)
    S = [f"# Thresholds as ranges: the range version {'HOLDS' if holds else 'does NOT hold'}; R2 {'PASS' if passed else 'FAIL'} — {today}, git {git}", "",
         "One command: `python barrels/experiments/2026-11-24_adaptive_range/run.py` (plan: `PREREG.md`). Train frames only; "
         f"the {data['n_test']} test frames are refused before any image is opened. Nothing is adopted; the default model is unchanged (`eb863d84`).", "",
         f"**Data.** {len(R)} slider-labelled frames in {len(hk_all)} conditions; ordinary: {len(keys)} conditions at **{len(hand_places)} places** "
         f"({', '.join(hand_places) or 'none'}). Labels saved from the slider proposal: {n_prop} ({n_unmoved} saved without moving a slider).", "",
         "**In plain words.** " + (
             "A frame has a run of values for each threshold that work as well as Tanush's; " +
             f"the runs hold when all six move together on {len(joint_ok)} of {len(R)} frames (confirmed box at least half the size). " +
             ("Constrained thresholds: " + ", ".join(cons) + ". " if cons else "No threshold is constrained. ") +
             (f"R2 lands inside the held-out ranges more often than the fixed value for: {', '.join(hold_b_t)}. " if hold_b_t else "R2 does not land inside the held-out ranges more often than the fixed value on any constrained threshold. ") +
             ("R2's detection test passes C2-C6." if hold_c else "R2's detection test fails " + ", ".join(c for c in ("C2", "C3", "C4", "C5", "C6") if not C[c][0]) + ".")), "",
         f"Verdict parts (PREREG): (a) ranges hold jointly: {'yes' if hold_a else 'no'}; (b) R2 beats fixed on a constrained threshold: {'yes' if hold_b else 'no'}; "
         f"(c) R2 passes C2-C6: {'yes' if hold_c else 'no'}. C1 (5 places) is separate: {'met' if C['C1'][0] else 'not met'}.", "",
         "## 1. How wide the ranges are (detector version, one threshold at a time, around his values)", "",
         "| threshold | fixed | median width (min-max) | without clutter | with clutter | low end stopped by | high end stopped by | fixed inside the condition range | constrained |",
         "|---|---|---|---|---|---|---|---|---|"]
    def wtxt(ws):
        return f"{np.median(ws):.0f} ({min(ws)}-{max(ws)})" if ws else "-"
    def whys(t, end):
        d = why_count[t].get(end, {})
        return ", ".join(f"{k} {v}" for k, v in sorted(d.items(), key=lambda kv: -kv[1]))
    for t in hr.THRESHOLDS:
        inside = len(keys) - len(constrained[t]["fixed_outside"])
        S.append(f"| {t} | {fmt(fixed[t])} | {wtxt(widths(t, 'det'))} | {wtxt(widths(t, 'det', False))} | {wtxt(widths(t, 'det', True))} | "
                 f"{whys(t, 'low end')} | {whys(t, 'high end')} | {inside} of {len(keys)} | {'**yes**' if constrained[t]['constrained'] else 'no'} |")
    S += ["", f"Hue in OpenCV units, S in 0-255. 'open' = the slider's end was reached still working. Ends closed one step from his value: {one_step} of {n_ends} "
          "(a lone failure next to his value is possible detector noise). Pixel-version widths are in `ranges.csv`.", "",
          f"**Joint check:** the box of the six ranges works at all its corners on {sum(1 for s in R if R[s]['joint']['corner_share'] == 1)} of {len(R)} frames; "
          f"median share of random points inside it that work {np.median([R[s]['joint']['random_share'] for s in R]):.2f}; the confirmed box (shrunk toward his values until it holds) "
          f"is full size on {sum(1 for s in R if R[s]['joint']['confirmed'] == 1)}, at least half size on {len(joint_ok)}, his values alone on {sum(1 for s in R if R[s]['joint']['confirmed'] == 0)} frames.", "",
          "## 2. Does anything land inside the held-out ranges? (leave one PLACE out)", "",
          "Mean over places of the share of a place's conditions whose range holds the prediction. Best feature = the best of the nine histogram features (line through home, or interval fit), named.", "",
          "| threshold | fixed | mean of other places | best feature | its rate | features beating both fixed and the mean |", "|---|---|---|---|---|---|"]
    best_feat = {}
    for t in hr.THRESHOLDS:
        rws = P["det"][t]
        if not rws or "mean_hit" not in rws[0]:
            S.append(f"| {t} | - | - | - | - | - |")
            continue
        fx, mn = place_rate(rws, "fixed_hit")[0], place_rate(rws, "mean_hit")[0]
        cand = [(place_rate(rws, f"{f}|{tag}_hit")[0], f"{f} ({tag})") for f in hr.FEATURES for tag in ("line", "interval")]
        b = max(cand)
        beats = [n for r_, n in cand if r_ > max(fx, mn) + 1e-9]
        best_feat[t] = (b, fx, mn, beats)
        S.append(f"| {t} | {fx:.2f} | {mn:.2f} | {b[1]} | {b[0]:.2f} | {', '.join(beats) if beats else 'none'} |")
    S += ["", "Confirmed-box version and per-place hits: `prediction.csv`.", "",
          "## 3. The rule R2 and its test", "",
          "R2 (PREREG part 3): a threshold stays fixed when the fixed value is inside every training condition's range; otherwise it moves with its primary feature "
          "along a line through home, slope chosen to land inside the most training ranges, kept only if that beats fixed. Fit on all places now: "
          + ("; ".join(f"`{t.threshold}` <- `{t.feature}` b = {t.slope:+.3f}" for t in r2_all) if r2_all else "**no term: every threshold stays fixed**") + ".", "",
          "Per threshold on the range target, leave one place out (share of held-out places' conditions inside their range): "
          + "; ".join(f"{t} fixed {rule_hits[t]['fixed']:.2f} / R2 {rule_hits[t]['r2']:.2f} / 2026-11-24 rule {rule_hits[t]['old']:.2f}" for t in hr.THRESHOLDS if rule_hits[t]) + ".", "",
          "Leave one place out, per condition: found / barrels (false boxes; boxes on empty frames).", "",
          "| condition | place | light | fixed | R2 |" + (" frozen R2 |" if new_places else ""), "|---|---|---|---|---|" + ("---|" if new_places else "")]
    for r in rows:
        S.append(f"| {name(r['condition'])} | {r['place']} | {r['light']} | {r['fixed_found']} / {r['barrels']} ({r['fixed_false']}; {r['fixed_neg']}) | "
                 f"{r['adapt_found']} / {r['barrels']} ({r['adapt_false']}; {r['adapt_neg']}) |"
                 + (f" {'-' if r['frozen_found'] is None else str(r['frozen_found']) + ' (' + str(r['frozen_false']) + ')'} |" if new_places else ""))
    S.append(f"| **total** | | | {tot('fixed_found')} / {tot('barrels')} ({tot('fixed_false')}; {tot('fixed_neg')}) | {tot('adapt_found')} / {tot('barrels')} ({tot('adapt_false')}; {tot('adapt_neg')}) |" + (" |" if new_places else ""))
    S += ["", "**Acceptance (the 2026-11-24 clauses, R2 in place of that rule):**", ""]
    S += [f"- {c}: {'pass' if ok else '**FAIL**'} — {txt}" for c, (ok, txt) in C.items()]
    S += ["", f"**R2 verdict: {'PASS — proposed, not adopted (walkthrough with Tanush first).' if passed else 'FAIL — the default stays the fixed model.'}**", "",
          "Files: `ranges.csv`, `joint.csv`, `prediction.csv`, `detection.csv`, `rule.json`, `model_r2.json`, `gate.txt`, `config.json`."]
    summary = "\n".join(S) + "\n"
    (out / "summary.md").write_text(summary)

    # ================================================================ CSVs, json
    def dump(fname, rws):
        with (out / fname).open("w", newline="") as fh:
            if rws:
                w = csv.DictWriter(fh, fieldnames=list(rws[0])); w.writeheader(); w.writerows(rws)
    cond_of = {s: k for k in hk_all for s in labelled[k]}
    dump("ranges.csv", [{"stem": s, "condition": cond_of[s], "class": cond[cond_of[s]]["class"], "place": cond[cond_of[s]]["place"], "clutter": is_clutter(s),
                         "threshold": t, "version": v, "anchor": R[s]["anchor"][t], "lo": R[s][v][t][0], "hi": R[s][v][t][1],
                         "lo_why": R[s][v][t][2], "hi_why": R[s][v][t][3], "fixed": fixed[t], "fixed_inside": R[s][v][t][0] <= fixed[t] <= R[s][v][t][1],
                         "proposed": R[s]["proposed"], "moved": R[s]["moved"]}
                        for s in R for v in ("det", "pix") for t in hr.THRESHOLDS])
    dump("joint.csv", [{"stem": s, "found_at_anchor": R[s]["found"], "boxes": R[s]["n_boxes"], "false_at_anchor": R[s]["false"],
                        "corner_share": R[s]["joint"]["corner_share"], "random_share": R[s]["joint"]["random_share"], "confirmed": R[s]["joint"]["confirmed"],
                        "detector_calls": R[s]["detector_calls"]} for s in R])
    dump("prediction.csv", [{"version": v, "threshold": t, **{k: (round(x, 3) if isinstance(x, float) else x) for k, x in r.items()}} for v in P for t in hr.THRESHOLDS for r in P[v][t]])
    dump("detection.csv", rows)
    (out / "rule.json").write_text(json.dumps({"date": today, "git": git, "terms": [t.as_tuple() for t in r2_all], "info": r2_info_all,
                                               "folds": {p: {"terms": [t.as_tuple() for t in f["terms"]], "train_places": f["train_places"], "info": f["info"]} for p, f in folds.items()},
                                               "hand_places": hand_places, "f_home": f_home}, indent=1, default=str) + "\n")
    json.dump({"date": today, "git": git, "passed": passed, "holds": holds, "holds_parts": {"a": hold_a, "b": hold_b, "c": hold_c, "b_thresholds": hold_b_t},
               "clauses": {c: {"pass": ok, "text": txt} for c, (ok, txt) in C.items()}, "constrained": constrained, "rule_hits": rule_hits,
               "condition_ranges": {v: {k: {t: list(x) for t, x in CR[v][k].items()} for k in CR[v]} for v in CR},
               "frozen": frozen_path.name if frozen_path else None, "new_places": new_places, "n_test_refused": data["n_test"],
               "frames": {s: {k: R[s][k] for k in ("anchor", "found", "false", "n_boxes", "proposed", "moved", "proposed_by")} for s in R}},
              (out / "config.json").open("w"), indent=1, default=str)
    if args.out is None:
        runs = out / "runs"; runs.mkdir(exist_ok=True)
        nn = 1 + max([int(p.name[:2]) for p in runs.iterdir() if p.is_dir() and p.name[:2].isdigit()] or [0])
        dest = runs / f"{nn:02d}_{today}_{git}_places{len(hand_places)}_frames{len(R)}"
        dest.mkdir()
        for p in out.iterdir():
            if p.is_file():
                shutil.copy2(p, dest / p.name)
    print(summary)
    print("written to", out)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
