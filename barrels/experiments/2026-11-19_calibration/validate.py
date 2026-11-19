#!/usr/bin/env python3
"""TODO A4, validation (2026-11-19): the ruler-fit camera against the old one on data the fit never saw.
The acceptance rule is in PREREG.md next to this file, committed before this script was run.

1. The size check on the hand-drawn boxes of the train frames (HOME, CAMPUS, BLACK, the wood ladder): width and
   height against what each camera expects at the box's bottom row, and the bottom row inferred from the top
   row and from the width.
2. The eval table (``barrels.report``; adopted color model, ``DetConfig()``, v2 rule, HOME leave-one-scene-out)
   with each camera, row by row.

Train frames only; a test frame is never opened (``report.refuse_test_frames`` and an assert here).

    python barrels/experiments/2026-11-19_calibration/validate.py                                             # the ruler fit (PREREG.md)
    python barrels/experiments/2026-11-19_calibration/validate.py --cam f=400,tilt=20.95,height=40.2 --tag _round2   # PREREG.md, addendum

Outputs: results/2026-11-19_calibration/ validation<tag>.md, validation<tag>.json, size_check<tag>.csv, eval_new_vs_old<tag>/.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import camfit as cf, cv as bcv, detector as det, geometry as geo, io, report as rp, splits, worldmap_bridge as wb  # noqa: E402

OUT = io.PKG_ROOT / "results" / "2026-11-19_calibration"
OLD = geo.AIM_4A8B6118_BOXFIT
NEW = geo.camera("f=400,tilt=20.4,height=40.2")          # PREREG.md; checked against fit.json below
CAMS = {"old": OLD, "new": NEW}
SKIP_FLAGS = ("occluded", "truncated", "held", "bottom_estimated")
BANDS = (("far", 0, 35), ("mid", 35, 60), ("near", 60, 10 ** 9))     # by DRAWN width, px
RULE_SETS = ("HOME", "CAMPUS")
RATIO_RANGE = (0.95, 1.05)


def group_of(stem: str) -> str:
    t = io.parse_name(stem)
    if t["surface"] == "wood":
        return "WOOD"
    return {"window_light": "HOME", "campus_light": "CAMPUS", "window_black": "BLACK"}.get(f"{t['light']}_{t['surface']}", f"other {t['light']}_{t['surface']}")


def train_stems() -> list[str]:
    sp = splits.load_splits()
    stems = [s for s in sorted(sp["train"]) if io.boxes_path(s).exists()]
    assert not set(stems) & set(sp["test"]), "a test frame leaked into the train list"
    return stems


# ---------------------------------------------------------------- 1. the size check

def size_rows(stems: list[str]) -> tuple[list[dict], int]:
    """One row per usable hand-drawn box, with every measure for both cameras. Also the number of boxes left
    out because one of the cameras has no finite size at their bottom row."""
    rows, dropped = [], 0
    for s in stems:
        for b in io.load_boxes(s)["barrels"]:
            x0, y0, x1, y1 = b["bbox"]
            if any(f in b.get("flags", ()) for f in SKIP_FLAGS) or io.touches_frame(b["bbox"]):
                continue
            w, h = x1 - x0, y1 - y0
            r = {"set": group_of(s), "stem": s, "color": b["color"], "bbox": [x0, y0, x1, y1], "w": w, "h": h, "col": (x0 + x1) / 2 - 320.0,
                 "band": next(n for n, lo, hi in BANDS if lo <= w < hi)}
            ok = True
            for name, cam in CAMS.items():
                W, H = cam.expected_barrel_width_px(bottom_row=y1), cam.expected_barrel_height_px(bottom_row=y1)
                pb = det.predicted_bottom(cam, y0)
                if not (np.isfinite(W) and np.isfinite(H) and W > 0 and np.isfinite(pb)):
                    ok = False
                    break
                r[f"w_ratio_{name}"] = w / W
                r[f"h_ratio_{name}"] = h / H
                r[f"bottom_from_top_{name}"] = pb - y1
                r[f"bottom_from_width_{name}"] = y0 + cam.expected_barrel_height_px(d_axis_mm=cam.f * geo.BARREL_BULGE_DIAMETER_MM / w) - y1
                r[f"w_exact_ratio_{name}"] = w / cam.silhouette_width_px(cam.d_axis_from_bottom_row(y1))
            if ok:
                rows.append(r)
            else:
                dropped += 1
    return rows, dropped


def med(v) -> float:
    return float(np.median(v)) if len(v) else float("nan")


def stat(v, fmt=".2f") -> str:
    if not len(v):
        return "-"
    v = np.asarray(v, float)
    return f"{np.median(v):{fmt}} ({np.percentile(v, 10):{fmt}} to {np.percentile(v, 90):{fmt}})"


def size_tables(rows: list[dict]) -> list[str]:
    sets = [g for g in ("HOME", "CAMPUS", "BLACK", "WOOD") if any(r["set"] == g for r in rows)] + sorted({r["set"] for r in rows if r["set"].startswith("other")})
    L = ["| set | boxes | camera | width ratio | height ratio | bottom from top, px | bottom from width, px |", "|---|---|---|---|---|---|---|"]

    def line(label, rs, name):
        return (f"| {label} | {len(rs)} | {name} | {stat([r[f'w_ratio_{name}'] for r in rs])} | {stat([r[f'h_ratio_{name}'] for r in rs])} | "
                f"{stat([r[f'bottom_from_top_{name}'] for r in rs], '+.1f')} | {stat([r[f'bottom_from_width_{name}'] for r in rs], '+.1f')} |")

    for g in sets:
        rs = [r for r in rows if r["set"] == g]
        L += [line(g, rs, "old"), line(g, rs, "new")]
    L += ["", "By distance (drawn width: far under 35 px, mid 35 to 60, near over 60):", "",
          "| set | range | boxes | camera | width ratio | height ratio | bottom from top, px | bottom from width, px |", "|---|---|---|---|---|---|---|---|"]
    for g in sets:
        for band, _, _ in BANDS:
            rs = [r for r in rows if r["set"] == g and r["band"] == band]
            if rs:
                for name in CAMS:
                    L.append(line(f"{g} | {band}", rs, name))
    return L


def rule_a_b(rows: list[dict]) -> tuple[dict, list[str]]:
    out = {"a": {}, "b": {}}
    L = ["| set | boxes | median bottom from top, old | new | far + mid boxes | old | new | (a) | median width ratio, new | median height ratio, new | (b) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for g in RULE_SETS:
        rs = [r for r in rows if r["set"] == g]
        fm = [r for r in rs if r["band"] != "near"]
        o_all, n_all = med([r["bottom_from_top_old"] for r in rs]), med([r["bottom_from_top_new"] for r in rs])
        o_fm, n_fm = med([r["bottom_from_top_old"] for r in fm]), med([r["bottom_from_top_new"] for r in fm])
        a = bool(abs(n_all) < abs(o_all) and abs(n_fm) < abs(o_fm))
        wr, hr = med([r["w_ratio_new"] for r in rs]), med([r["h_ratio_new"] for r in rs])
        b = bool(RATIO_RANGE[0] <= wr <= RATIO_RANGE[1] and RATIO_RANGE[0] <= hr <= RATIO_RANGE[1])
        out["a"][g] = {"all_old": o_all, "all_new": n_all, "far_mid_old": o_fm, "far_mid_new": n_fm, "pass": a}
        out["b"][g] = {"width_ratio_new": wr, "height_ratio_new": hr, "pass": b}
        L.append(f"| {g} | {len(rs)} | {o_all:+.1f} | {n_all:+.1f} | {len(fm)} | {o_fm:+.1f} | {n_fm:+.1f} | {'pass' if a else 'FAIL'} | {wr:.2f} | {hr:.2f} | {'pass' if b else 'FAIL'} |")
    return out, L


def report_only(rows: list[dict]) -> list[str]:
    sets = [g for g in ("HOME", "CAMPUS", "BLACK", "WOOD") if any(r["set"] == g for r in rows)]
    L = ["### Bottom from the width against bottom from the top row", "",
         "Median of the absolute error in px (how far the inferred bottom is from the drawn one, either way).", "",
         "| set | range | boxes | from top, old | from width, old | from top, new | from width, new |", "|---|---|---|---|---|---|---|"]
    for g in sets:
        for band in ("all", "far", "mid", "near"):
            rs = [r for r in rows if r["set"] == g and (band == "all" or r["band"] == band)]
            if rs:
                L.append(f"| {g} | {band} | {len(rs)} | " + " | ".join(f"{med([abs(r[f'bottom_from_{k}_{c}']) for r in rs]):.1f}" for c in CAMS for k in ("top", "width")) + " |")
    L += ["", "### Width against the exact outline instead of the shortcut `f × 25.5 / distance`", "",
          "| set | range | boxes | shortcut, old | exact, old | shortcut, new | exact, new |", "|---|---|---|---|---|---|---|"]
    for g in sets:
        for band in ("all", "far", "mid", "near"):
            rs = [r for r in rows if r["set"] == g and (band == "all" or r["band"] == band)]
            if rs:
                L.append(f"| {g} | {band} | {len(rs)} | " + " | ".join(f"{med([r[f'{k}_{c}'] for r in rs]):.2f}" for c in CAMS for k in ("w_ratio", "w_exact_ratio")) + " |")
    L += ["", "### Bottom-from-top error against the box's column (far and mid boxes)", "",
          "A camera rolled about its axis would put barrels on one side of the frame lower than on the other; the error would then change with the column. "
          "Slope in px of error per 100 px of column, with its 1-sigma.", "",
          "| set | boxes | columns covered | slope, old | slope, new |", "|---|---|---|---|---|"]
    for g in sets:
        rs = [r for r in rows if r["set"] == g and r["band"] != "near"]
        if len(rs) < 6:
            continue
        x = np.array([r["col"] for r in rs])
        cells = []
        for c in CAMS:
            y = np.array([r[f"bottom_from_top_{c}"] for r in rs])
            p, cov = np.polyfit(x, y, 1, cov=True)
            cells.append(f"{100 * p[0]:+.1f} ± {100 * np.sqrt(cov[0, 0]):.1f}")
        L.append(f"| {g} | {len(rs)} | {x.min():+.0f} to {x.max():+.0f} | {cells[0]} | {cells[1]} |")
    return L


# ---------------------------------------------------------------- 2. the eval table

def eval_table() -> tuple[rp.Report, dict, dict]:
    sp = splits.load_splits()
    sel = rp.select_frames(rp.labeled_stems(), sp, split="train")
    t0 = time.time()
    cache = rp.FrameCache()
    arm_new = rp.Arm("new camera", wb.DEFAULT_MODEL, {}, cam=NEW)
    arm_old = rp.Arm("old camera", wb.DEFAULT_MODEL, {}, cam=OLD)
    res_new = rp.run_arm(arm_new, sel, sp, cache=cache)
    res_old = rp.run_arm(arm_old, sel, sp, cache=cache)
    rep = rp.Report(rp.build_rows(sel.sets, res_new, res_old), arm_new, arm_old, sel, "loso", bcv.git_hash(), time.time() - t0)
    return rep, res_new, res_old


def rule_c(rep: rp.Report, res_new: dict, res_old: dict) -> tuple[dict, list[str]]:
    keys = list(rep.selection.sets)
    bad_rows, changed = [], []
    for row in rep.rows:
        if row.kind != "scene":
            continue
        d_found, d_false = row.cand.found - row.base.found, row.cand.false - row.base.false
        if d_found or d_false:
            changed.append((row.label, row.scene, row.base.found, row.cand.found, row.cand.barrels, row.base.false, row.cand.false))
            if row.label in RULE_SETS and (d_found < 0 or d_false > 0):
                bad_rows.append(f"{row.label} {row.scene}")
    neg_bad, neg_any = [], []
    for stem, r in res_new.items():
        if not r.negative:
            continue
        n_new, n_old = sum(r.fp.values()), sum(res_old[stem].fp.values())
        if n_new or n_old:
            neg_any.append((stem, n_old, n_new))
        if n_new > n_old:
            neg_bad.append(stem)
    L = ["| set | scenario | barrels | found, old | found, new | false, old | false, new | in the rule |", "|---|---|---|---|---|---|---|---|"]
    for label, scene, fo, fn, nb, xo, xn in changed:
        L.append(f"| {label} | {scene} | {nb} | {fo} | {fn} | {xo} | {xn} | {'yes' if label in RULE_SETS else 'report only'} |")
    if not changed:
        L.append("| (no scenario row differs) | | | | | | | |")
    L += ["", "Subtotals:", "", "| set | barrels | found, old | found, new | false, old | false, new | boxes on negative frames, old | new | score, old | new |", "|---|---|---|---|---|---|---|---|---|---|"]
    for row in rep.rows:
        if row.kind == "subtotal":
            L.append(f"| {row.label} | {row.cand.barrels} | {row.base.found} | {row.cand.found} | {row.base.false} | {row.cand.false} | {row.base.neg_false} | {row.cand.neg_false} | "
                     f"{row.base.score:.2f} | {row.cand.score:.2f} |")
    L += ["", "Negative frames with a box under either camera: " + (", ".join(f"{s} (old {a}, new {b})" for s, a, b in neg_any) if neg_any else "none") + "."]
    # frame by frame, what differs
    L += ["", "Frames where the two cameras differ (found / false):", "", "| set | frame | barrels | found, old | new | false, old | new |", "|---|---|---|---|---|---|---|"]
    n_diff = 0
    for key in keys:
        for stem in rep.selection.sets[key]:
            a, b = res_old[stem], res_new[stem]
            fa, fb, xa, xb = sum(a.tp.values()), sum(b.tp.values()), sum(a.fp.values()), sum(b.fp.values())
            if (fa, xa) != (fb, xb):
                n_diff += 1
                L.append(f"| {rp.set_label(key, keys)} | {stem} | {sum(a.n_gt.values())} | {fa} | {fb} | {xa} | {xb} |")
    if not n_diff:
        L.append("| (none) | | | | | | |")
    ok = not bad_rows and not neg_bad
    return {"pass": bool(ok), "rows_that_regress": bad_rows, "negative_frames_that_gain_a_box": neg_bad,
            "changed_rows": [dict(zip(("set", "scenario", "found_old", "found_new", "barrels", "false_old", "false_new"), c)) for c in changed]}, L


# ---------------------------------------------------------------- main

def ruler_lines() -> list[str]:
    """Report only: the ruler set's whole boxes, the same image-internal measures (no distance used)."""
    L = ["| ruler frame | mm | bottom from top: old | new | bottom from width: old | new | width ratio: old | new | height ratio: old | new |", "|---|---|---|---|---|---|---|---|---|---|"]
    for s in cf.load_ruler_set():
        x0, y0, x1, y1 = s.bbox
        if y1 >= io.FRAME_H or "held" in s.flags:
            continue
        cells = []
        for fn in (lambda c: det.predicted_bottom(c, y0) - y1,
                   lambda c: y0 + c.expected_barrel_height_px(d_axis_mm=c.f * geo.BARREL_BULGE_DIAMETER_MM / (x1 - x0)) - y1):
            cells += [f"{fn(c):+.1f}" for c in CAMS.values()]
        for fn in (lambda c: (x1 - x0) / c.expected_barrel_width_px(bottom_row=y1), lambda c: (y1 - y0) / c.expected_barrel_height_px(bottom_row=y1)):
            cells += [f"{fn(c):.2f}" for c in CAMS.values()]
        L.append(f"| {s.stem.split('_')[-1]} | {s.d_ruler_mm:.0f} | " + " | ".join(cells) + " |")
    return L


def main(argv=None) -> int:
    global NEW
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cam", type=geo.camera, default=None, help="the new camera, as numbers (default: the ruler fit of PREREG.md)")
    ap.add_argument("--tag", default="", help="suffix of the output names, e.g. _round2")
    args = ap.parse_args(argv)
    out = OUT
    out.mkdir(parents=True, exist_ok=True)
    tag = args.tag
    if args.cam is None:
        fit = json.load((out / "fit.json").open())["candidate"]
        assert (fit["f"], round(fit["tilt_deg"], 2), round(fit["height_mm"], 1)) == (NEW.f, NEW.tilt_deg, NEW.height_mm), "the camera here is not the one run.py fitted"
    else:
        NEW = args.cam
        CAMS["new"] = NEW

    rows, dropped = size_rows(train_stems())
    with (out / f"size_check{tag}.csv").open("w", newline="") as f:
        fields = list(rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    ab, ab_lines = rule_a_b(rows)

    rep, res_new, res_old = eval_table()
    rp.write_all(rep, out / f"eval_new_vs_old{tag}", title=f"Eval table: the new camera (candidate; f {NEW.f:g}, tilt {NEW.tilt_deg:g}, height {NEW.height_mm:g}) vs the old camera (baseline)")
    c, c_lines = rule_c(rep, res_new, res_old)

    a_ok = all(v["pass"] for v in ab["a"].values())
    b_ok = all(v["pass"] for v in ab["b"].values())
    verdict = a_ok and b_ok and c["pass"]
    L = [f"# Validation of the new camera on the train frames (rule: PREREG.md{', addendum' if tag else ''})", "",
         f"git {bcv.git_hash()}. Old camera: f {OLD.f:g}, tilt {OLD.tilt_deg:g}°, height {OLD.height_mm:g} mm, horizon row {OLD.horizon_row():.1f}. "
         f"New camera: f {NEW.f:g}, tilt {NEW.tilt_deg:g}°, height {NEW.height_mm:g} mm, horizon row {NEW.horizon_row():.1f}. Train frames only.", "",
         "## Verdict", "",
         f"- (a) the top-row bottom bias shrinks on HOME and CAMPUS: **{'pass' if a_ok else 'FAIL'}**",
         f"- (b) width and height ratios of HOME and CAMPUS within {RATIO_RANGE[0]} to {RATIO_RANGE[1]}: **{'pass' if b_ok else 'FAIL'}**",
         f"- (c) never regress: **{'pass' if c['pass'] else 'FAIL'}**"
         + ("" if c["pass"] else f" (rows: {', '.join(c['rows_that_regress']) or 'none'}; negative frames that gain a box: {', '.join(c['negative_frames_that_gain_a_box']) or 'none'})"),
         f"- **{'The new camera passes the pre-registered rule.' if verdict else 'The new camera does NOT pass the pre-registered rule: no default changes.'}**", "",
         "## Rule (a) and (b): the size check", ""] + ab_lines + [
         "", f"## The size check in full ({len(rows)} boxes; {dropped} left out because a camera has no finite size at their row)", "",
         "Ratio = drawn size / the size the camera expects for a barrel whose bottom edge is at the box's bottom row. Bottom from top / from width = inferred bottom row "
         "minus drawn bottom row (+ = inferred lower). Median (10th to 90th percentile).", ""] + size_tables(rows) + [
         "", "## Rule (c): the eval table, scenario rows that differ between the cameras", "",
         f"Adopted color model, `DetConfig()`, v2 rule, HOME leave-one-scene-out. Full table: `eval_new_vs_old{tag}/report.md` (candidate = new camera, baseline = old).", ""] + c_lines + [
         "", "## Report only", ""] + report_only(rows) + [
         "", "### The ruler set's whole boxes, the same measures (no distance used)", ""] + ruler_lines()
    (out / f"validation{tag}.md").write_text("\n".join(L) + "\n")
    json.dump({"git": bcv.git_hash(), "old": {"f": OLD.f, "tilt_deg": OLD.tilt_deg, "height_mm": OLD.height_mm}, "new": {"f": NEW.f, "tilt_deg": NEW.tilt_deg, "height_mm": NEW.height_mm},
               "rule": {"a": ab["a"], "b": ab["b"], "c": c}, "verdict": bool(verdict), "boxes": len(rows), "boxes_left_out": dropped},
              (out / f"validation{tag}.json").open("w"), indent=1)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
