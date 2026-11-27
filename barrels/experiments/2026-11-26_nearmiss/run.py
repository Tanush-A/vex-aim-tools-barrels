#!/usr/bin/env python3
"""The judged runs of experiment 2026-11-26_nearmiss (TODO C2; plan: PREREG.md in this folder).

    python barrels/experiments/2026-11-26_nearmiss/run.py --list
    python barrels/experiments/2026-11-26_nearmiss/run.py --precompute [--jobs 8]     # every setting on every ordinary train frame, once
    python barrels/experiments/2026-11-26_nearmiss/run.py --only NAME [NAME ...]      # judge these candidates
    python barrels/experiments/2026-11-26_nearmiss/run.py --all                       # judge every candidate
    python barrels/experiments/2026-11-26_nearmiss/run.py --summary                   # summary.md from the runs that exist
    python barrels/experiments/2026-11-26_nearmiss/run.py --final                     # the selection rule on all eight places at once

Every candidate goes through the standard pass rule (``barrels.judge.judge``) against today's default. Candidates
with a chosen number are judged leave one place out. Train frames only: the judge refuses anything else before an
image is opened. Per candidate, in results/2026-11-26_nearmiss/<name>/: judge.md, judge.json, changes.csv (the
judge's own pages), extras.json (paint outside the hand boxes, what happened to the bottom edges, what each fold
chose). ``--summary`` writes results/2026-11-26_nearmiss/summary.md and summary.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidates as cand  # noqa: E402
import nm_common as cm  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import eval_det as ed  # noqa: E402
from barrels import judge as jg  # noqa: E402

WEAK = 2.0                                          # a PASS less than this many placements above the gain margin is weak
# clutter with an orange part and a blue band is the trap for any loose level beside a partner (PREREG.md): reported by name
TRAPS = ("4A8B_lampmid3_bathtile_neg_02", "4A8B_lampmid6_bathtile_neg_02", "4A8B_lampwarm6_bathtile_neg_02")


def registry() -> dict[str, tuple]:
    """name -> ("fixed", spec, group) | ("fit", fit function, group), in the order of the summary."""
    r: dict[str, tuple] = {}
    for spec in cand.HYST_FIXED:
        r[f"A_{spec.replace(':', '')}"] = ("fixed", spec, "A")
    r["A_hyst_fit"] = ("fit", cand.fit_hyst, "A")
    r["A_hyst_guard_fit"] = ("fit", cand.fit_hyst_guard, "A")
    r["B_partner_fit"] = ("fit", cand.fit_partner, "B")
    r["D_partner_free_fit"] = ("fit", cand.fit_partner_free, "D")
    r["C_wide_fit"] = ("fit", cand.fit_wide, "C")
    for k, spec in enumerate(cand.STRIPE_ONLY, 1):
        r[f"C_stripe{k}"] = ("fixed", spec, "C")
    for k, spec in enumerate(cand.BODY_ONLY, 1):
        r[f"C_body{k}"] = ("fixed", spec, "C")
    for spec in cand.BOTH:
        s, b, _ = spec.split(":")[1].split(",")
        r[f"C_both{s}_{b}"] = ("fixed", spec, "C")
    return r


# ---------------------------------------------------------------- what the judge does not print

def _best(boxes, g):
    """The box of the barrel's color that overlaps it most (None when none overlaps)."""
    same = [(ed.box_iou(p.bbox, g.bbox), p) for p in boxes if p.color == g.color]
    same = [x for x in same if x[0] > 0]
    return max(same, key=lambda x: x[0])[1] if same else None


def bottoms(j) -> dict:
    """What happened to the bottom edge of the barrels the baseline finds (ordinary frames, counted per frame)."""
    out = {"base_found": 0, "kept": 0, "lost_box_off": 0, "lost_missed": 0, "bottom_moved": 0, "bottom_down": 0, "bottom_up": 0,
           "moved_px": [], "cand_bottom_err": [], "base_bottom_err": []}
    for s in j.frames[cnd.ORDINARY]:
        gts = j.truth.gts[s]
        b, c = j.baseline.counts[s], j.candidate.counts[s]
        for i, g in enumerate(gts):
            pc = _best(j.candidate.boxes[s], g)
            if c.gt[i] == ct.FOUND and pc is not None:
                out["cand_bottom_err"].append(pc.bbox[3] - g.bbox[3])
            if b.gt[i] != ct.FOUND:
                continue
            out["base_found"] += 1
            pb = _best(j.baseline.boxes[s], g)
            if pb is not None:
                out["base_bottom_err"].append(pb.bbox[3] - g.bbox[3])
            if c.gt[i] == ct.FOUND:
                out["kept"] += 1
            elif c.gt[i] == ct.OFF:
                out["lost_box_off"] += 1
            else:
                out["lost_missed"] += 1
            if pb is not None and pc is not None and pc.bbox[3] != pb.bbox[3]:
                d = pc.bbox[3] - pb.bbox[3]
                out["bottom_moved"] += 1
                out["bottom_down" if d > 0 else "bottom_up"] += 1
                out["moved_px"].append(d)
    for k in ("cand_bottom_err", "base_bottom_err"):
        v = np.array(out.pop(k), float)
        out[k + "_mean"] = round(float(v.mean()), 2) if len(v) else None
        out[k + "_abs_mean"] = round(float(np.abs(v).mean()), 2) if len(v) else None
    v = out.pop("moved_px")
    out["moved_px_abs_mean"] = round(float(np.mean(np.abs(v))), 2) if v else None
    return out


def flood(spec_of: dict[str, str]) -> dict:
    """Paint outside the hand boxes (grown by 4 px) and inside them, candidate against the fixed model, summed over
    the ordinary frames. ``spec_of``: frame -> the setting that scored it."""
    stems = list(spec_of)
    recs = cm.ensure(["fixed", *spec_of.values()], stems)
    f_out = sum(recs["fixed"][s]["px_out"] for s in stems)
    f_in = sum(recs["fixed"][s]["px_in"] for s in stems)
    c_out = sum(recs[spec_of[s]][s]["px_out"] for s in stems)
    c_in = sum(recs[spec_of[s]][s]["px_in"] for s in stems)
    empties = [s for s in stems if not cm.truth().gts[s]]
    return {"px_out_fixed": f_out, "px_out": c_out, "px_out_ratio": round(c_out / max(1, f_out), 3),
            "px_in_fixed": f_in, "px_in": c_in, "px_in_ratio": round(c_in / max(1, f_in), 3),
            "px_added_on_empty_frames": sum(recs[spec_of[s]][s]["px_added"] for s in empties), "empty_frames": len(empties)}


def run_one(name: str, entry: tuple) -> dict:
    kind, what, group = entry
    out_dir = cm.RESULTS / name
    t0 = time.time()
    if kind == "fit":
        cand.CHOSEN.pop(name, None)
        j = jg.judge(fit=what, name=name, out_dir=out_dir, frames=cm.frames(), truth=cm.truth())
        chosen = cand.CHOSEN[name]
        spec_of = {s: chosen[ct.place_of(s)]["spec"] for s in j.frames[cnd.ORDINARY]}
        folds = {}
        for place, c in chosen.items():
            rows = c["rows"]
            row = next(r for r in rows if r["spec"] == c["spec"])
            base = next(r for r in rows if r["spec"] == "fixed")
            top = sorted((r for r in rows if r["eligible"]), key=lambda r: -r["J"])[:5]
            folds[place] = {"spec": c["spec"], "J": round(row["J"], 3), "J_fixed": round(base["J"], 3), "settings": len(rows),
                            "eligible": sum(1 for r in rows if r["eligible"]),
                            "top5": [{"spec": r["spec"], "J": round(r["J"], 3), "found_w": round(r["found_w"], 2), "extra_w": round(r["extra_w"], 2)} for r in top]}
    else:
        j = jg.judge(cand.fixed(what), name=name, out_dir=out_dir, frames=cm.frames(), truth=cm.truth())
        spec_of = {s: what for s in j.frames[cnd.ORDINARY]}
        folds = None
    traps = {s: {"baseline": len(j.baseline.boxes[s]), "candidate": [[int(p.color), *(int(v) for v in p.bbox)] for p in j.candidate.boxes[s]]}
             for s in TRAPS if s in j.candidate.boxes}
    extras = {"name": name, "group": group, "kind": kind, "spec": what if kind == "fixed" else None, "traps": traps,
              "describe": j.candidate.describe if kind == "fixed" else what.describe,
              "folds": folds, "flood": flood(spec_of), "bottoms": bottoms(j), "seconds": round(time.time() - t0, 1)}
    (out_dir / "extras.json").write_text(json.dumps(extras, indent=1) + "\n")
    b, c = j.total
    print(f"{name:<22} {j.result:<20} found {b.found_w:.1f} -> {c.found_w:.1f} ({c.found_w - b.found_w:+.1f}), per frame {b.found} -> {c.found}, "
          f"not on barrel {b.extra_w:.1f} -> {c.extra_w:.1f}, clean empty {b.clean_empty} -> {c.clean_empty}  [{time.time() - t0:.0f} s]", flush=True)
    return extras


# ---------------------------------------------------------------- the summary

def summary() -> str:
    margins = jg.load_margins()
    rows, js = [], {}
    for name, entry in registry().items():
        d = cm.RESULTS / name
        if not (d / "judge.json").exists() or not (d / "extras.json").exists():
            continue
        j, x = json.loads((d / "judge.json").read_text()), json.loads((d / "extras.json").read_text())
        b, c = j["total"]["baseline"], j["total"]["candidate"]
        gain = c["found_w"] - b["found_w"]
        verdict = j["verdict"]
        if verdict == jg.PASS and gain < margins.found_gain + WEAK:
            verdict = "PASS (WEAK)"
        ch = [x_ for x_ in j["changes"] if x_["judged"]]
        moved = []
        for p, v in j["places"].items():
            dp = v["candidate"]["found_w"] - v["baseline"]["found_w"]
            if abs(dp) > 1e-9:
                moved.append(f"{p} {dp:+.1f}")
        ro = j.get("report_only", {})
        xb = sum(v["baseline"]["found"] for v in ro.values()); xc = sum(v["candidate"]["found"] for v in ro.values())
        xn = sum(v["baseline"]["barrels"] for v in ro.values())
        xeb = sum(v["baseline"]["extra_w"] for v in ro.values()); xec = sum(v["candidate"]["extra_w"] for v in ro.values())
        bt = x["bottoms"]
        r = {"name": name, "group": x["group"], "what": x["spec"] or "chosen in each fold", "verdict": verdict,
             "found_w": [b["found_w"], c["found_w"]], "found": [b["found"], c["found"]], "barrels": b["barrels"], "placements": b["placements"],
             "gained": sum(1 for q in ch if q["kind"] == "gained"), "lost": sum(1 for q in ch if q["kind"] == "lost"),
             "extra_w": [b["extra_w"], c["extra_w"]], "clean_empty": [b["clean_empty"], c["clean_empty"]],
             "cluttered_empty_w": [b["cluttered_empty_w"], c["cluttered_empty_w"]], "places_moved": moved,
             "px_out_ratio": x["flood"]["px_out_ratio"], "px_in_ratio": x["flood"]["px_in_ratio"],
             "bottom_moved": bt["bottom_moved"], "base_found": bt["base_found"], "lost_box_off": bt["lost_box_off"], "lost_missed": bt["lost_missed"],
             "extreme_found": [xb, xc], "extreme_barrels": xn, "extreme_extra_w": [round(xeb, 2), round(xec, 2)],
             "traps": {s.replace("4A8B_", ""): [v["baseline"], len(v["candidate"])] for s, v in x.get("traps", {}).items()},
             "folds": {p: f["spec"] for p, f in (x["folds"] or {}).items()}}
        rows.append(r)
        js[name] = r
    out = ["# Near-miss colors next to strong evidence: every judged candidate (2026-11-26)", "",
           "Made by `experiments/2026-11-26_nearmiss/run.py --summary` from the judge's pages in the folders beside this file. "
           "Train frames only; every candidate against today's default; candidates with a chosen number judged leave one place out. "
           f"Found = the strict rule. Margins: found better above +{margins.found_gain:.1f}, worse below -{margins.found_loss:.2f} placements; "
           f"boxes not on their barrel worse above +{margins.extra_rise:.2f}; any new box on a clean empty frame fails. "
           f"A PASS less than {WEAK:.0f} placements above the gain margin is marked WEAK.", ""]
    if not rows:
        return "\n".join(out + ["(no judged run yet)"])
    n = rows[0]
    out += [f"Baseline (the fixed model): {n['found_w'][0]:.1f} of {n['placements']} placements, {n['found'][0]} of {n['barrels']} per frame, "
            f"{n['extra_w'][0]:.1f} boxes not on their barrel, {n['clean_empty'][0]} on clean empty frames.", "",
            "| candidate | setting | verdict | found, placements | per frame | gained / lost | boxes not on their barrel | empty frames: clean, with clutter | places that moved |",
            "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        d = r["found_w"][1] - r["found_w"][0]
        out.append(f"| {r['name']} | {r['what']} | **{r['verdict']}** | {r['found_w'][1]:.1f} ({d:+.1f}) | {r['found'][1]} ({r['found'][1] - r['found'][0]:+d}) | "
                   f"+{r['gained']} / -{r['lost']} | {r['extra_w'][1]:.1f} ({r['extra_w'][1] - r['extra_w'][0]:+.1f}) | {r['clean_empty'][1]}, {r['cluttered_empty_w'][1]:.1f} | "
                   f"{'; '.join(r['places_moved']) or 'none'} |")
    out += ["", "## Paint, bottom edges, extreme conditions (report only)", "",
            "Paint outside / inside the hand boxes: the candidate's painted pixels over the fixed model's, ordinary frames, boxes grown by 4 px. "
            "Bottoms moved: of the barrels the fixed model finds, how many get a box with another bottom row; lost: how many are no longer a strict hit "
            "(box still on the barrel but off / no box on it). Extreme: the parked conditions, found per frame and boxes not on their barrel, never judged.", "",
            "| candidate | paint outside | paint inside | bottoms moved | lost: box off / missed | extreme: found per frame | extreme: boxes not on their barrel |",
            "|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['name']} | x {r['px_out_ratio']:.2f} | x {r['px_in_ratio']:.2f} | {r['bottom_moved']} of {r['base_found']} | {r['lost_box_off']} / {r['lost_missed']} | "
                   f"{r['extreme_found'][0]} -> {r['extreme_found'][1]} of {r['extreme_barrels']} | {r['extreme_extra_w'][0]:.1f} -> {r['extreme_extra_w'][1]:.1f} |")
    out += ["", "## The named clutter traps (empty frames with clutter that has an orange part and a blue band)", "",
            "Boxes drawn, fixed model -> candidate.", "", "| candidate | " + " | ".join(s.replace("4A8B_", "") for s in TRAPS) + " |", "|---|" + "---|" * len(TRAPS)]
    for r in rows:
        out.append(f"| {r['name']} | " + " | ".join("{} -> {}".format(*r["traps"][s.replace("4A8B_", "")]) if s.replace("4A8B_", "") in r["traps"] else "" for s in TRAPS) + " |")
    fits = [r for r in rows if r["folds"]]
    if fits:
        out += ["", "## What each fold chose (the setting used on the held-out place)", ""]
        places = list(dict.fromkeys(p for r in fits for p in r["folds"]))
        out += ["| candidate | " + " | ".join(places) + " |", "|---|" + "---|" * len(places)]
        for r in fits:
            out.append(f"| {r['name']} | " + " | ".join(r["folds"].get(p, "") for p in places) + " |")
        out += ["", "A place that is not an ordinary one (the black table, the wood desk) is report only; its setting was chosen on all the ordinary frames."]
    (cm.RESULTS / "summary.json").write_text(json.dumps(js, indent=1) + "\n")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--precompute", action="store_true")
    ap.add_argument("--only", nargs="*", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--final", action="store_true", help="the setting the selection rule gives on all ordinary places; checked against candidates.FINAL_SPEC")
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args(argv)
    reg = registry()
    cand.JOBS = a.jobs
    if a.list:
        for name, (kind, what, group) in reg.items():
            print(f"{name:<22} {group}  {kind:<6} {what if kind == 'fixed' else what.describe}")
    if a.precompute:
        t0 = time.time()
        specs = cand.all_specs()
        cm.ensure(specs, cm.ordinary(), a.jobs)
        print(f"precomputed {len(specs)} settings on {len(cm.ordinary())} ordinary train frames in {time.time() - t0:.0f} s")
    names = list(reg) if a.all else a.only
    bad = [n for n in names if n not in reg]
    if bad:
        raise SystemExit(f"unknown candidate(s) {bad}; --list shows them")
    for n in names:
        run_one(n, reg[n])
    if a.final:
        spec, rows = cm.choose(cand.GRID_B, cm.ordinary(), jobs=a.jobs)
        row = next(r for r in rows if r["spec"] == spec)
        top = sorted((r for r in rows if r["eligible"]), key=lambda r: -r["J"])[:8]
        out = {"spec": spec, "describe": cm.describe(spec), "J": round(row["J"], 3), "found_w": round(row["found_w"], 2), "extra_w": round(row["extra_w"], 2),
               "settings": len(rows), "eligible": sum(1 for r in rows if r["eligible"]),
               "note": "chosen on all eight ordinary places at once: these numbers are in-sample; the held-out result is B_partner_fit's",
               "top8": [{"spec": r["spec"], "J": round(r["J"], 3), "found_w": round(r["found_w"], 2), "extra_w": round(r["extra_w"], 2)} for r in top]}
        (cm.RESULTS / "final_setting.json").write_text(json.dumps(out, indent=1) + "\n")
        print(json.dumps(out, indent=1))
        if spec != cand.FINAL_SPEC:
            raise SystemExit(f"candidates.FINAL_SPEC is {cand.FINAL_SPEC!r} but the rule gives {spec!r}")
    if a.summary:
        text = summary()
        (cm.RESULTS / "summary.md").write_text(text)
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
