#!/usr/bin/env python3
"""TODO item A (2026-11-18): "if the segmentation is good, the detector finds the barrel", as a measured test.

The detector is fed segmentation that is good by construction, and found / missed / false is counted per
scenario under the v2 rule (the same scoring as ``barrels.report``):

  level 1   perfect masks: the hand-made class masks of the 16 HOME train frames.
  level 2   the same masks with seeded, measured damage (``barrels.degrade``): three severities, 5 seeds each,
            and one kind of damage at a time (report only).
  level 3a  real: the CAMPUS train frames with the adopted color model.
  level 3b  real: the BLACK-table train frames with thresholds read from each frame's own labels (arm
            ``hue+sat+stripes`` of ``experiments/2026-11-16_hs_oracle``; the thresholds read the answer, so the
            pixels are as good as this color model can make them).
  level 3c  report only: the wood frames under the cool lamp (brightness 3 and 6), same per-frame thresholds.

For every missed barrel the detector's reason log says which test refused it (``attribute`` of
``experiments/2026-11-11_occl_attribution``).

Also: the expected barrel size against the hand-drawn boxes (``--size-check``, part of the default run): for
every unoccluded, untruncated truth box of the train sets, box width and height divided by what the camera model
predicts for a barrel whose bottom edge is at that row (what the box tool's ``g`` key draws, and what the
detector's width tests use).

Train frames only; a test frame is never opened (asserted).

    python barrels/experiments/2026-11-18_det_given_seg/run.py            # every arm in ARMS
    python barrels/experiments/2026-11-18_det_given_seg/run.py --arms base

Outputs: results/2026-11-18_det_given_seg/ — summary.md, scenarios.csv, per_barrel.csv, size_check.md,
size_check.csv, config.json (committed); sheets/ (ignored).
"""
from __future__ import annotations

import argparse
import collections
import csv
import dataclasses
import importlib.util
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import cv as bcv, degrade as dg, detect_types as dtp, detector as det, eval_det as ed, geometry as geo, io, pipeline as pl  # noqa: E402
from barrels import report as rp, splits, worldmap_bridge as wb  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402

_spec = importlib.util.spec_from_file_location("oracle", HERE.parent / "2026-11-16_hs_oracle" / "run.py")
oracle = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(oracle)
pooled, att = oracle.pooled, oracle.att

OUT = PKG_ROOT / "results" / "2026-11-18_det_given_seg"
CAM = geo.AIM_4A8B6118_BOXFIT
SEEDS = (0, 1, 2, 3, 4)
SKIP_SIZE_FLAGS = ("occluded", "truncated", "held", "bottom_estimated")

sys.path.insert(0, str(HERE))
from arms import ARMS  # noqa: E402  (the detector settings compared: arms.py next to this file)


# ---------------------------------------------------------------- frames

def train_sets() -> dict[str, list[str]]:
    sp = splits.load_splits()
    test = set(sp["test"])
    stems = [s for s in sorted(sp["train"]) if io.boxes_path(s).exists()]
    assert not set(stems) & test, "a test frame leaked into the train list"
    out: dict[str, list[str]] = {}
    for s in stems:
        out.setdefault(pooled.group_of(s), []).append(s)
    return out


def truth(stem: str):
    label = io.load_boxes(stem)
    return [b.with_ground(CAM) for b in dtp.barrels_from_boxes(label)], label.get("clean", True)


class Scenario:
    """One row of the result table: a list of (stem, mask) to detect on. ``key`` = level / name."""

    def __init__(self, level: str, name: str, rule: bool):
        self.level, self.name, self.rule = level, name, rule      # rule: counts for the acceptance rule (else report only)
        self.items: list[tuple[str, str, np.ndarray]] = []         # (stem, tag, mask); tag tells seeds apart

    @property
    def key(self) -> str:
        return f"{self.level} {self.name}"


def build_scenarios(sets: dict[str, list[str]]) -> tuple[list[Scenario], dict[str, np.ndarray]]:
    images: dict[str, np.ndarray] = {}
    base = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    out = []
    # level 1 and 2: the HOME hand masks
    home = [s for s in sets["HOME"] if io.mask_path(s).exists()]
    masks = {s: io.load_mask(io.mask_path(s)) for s in home}
    for s in home:
        images[s] = io.load_image(io.find_image(s))
    l1 = Scenario("1", "perfect masks (HOME)", True)
    l1.items = [(s, "", masks[s]) for s in home]
    out.append(l1)
    boxes = {s: [tuple(g.bbox) for g in truth(s)[0]] for s in home}
    for group, table, rule in ((dg.SEVERITIES, "2", True), (dg.SINGLE, "2s", False)):
        for name, d in group.items():
            sc = Scenario(table, name, rule)
            for seed in SEEDS:
                for i, s in enumerate(home):
                    sc.items.append((s, f"seed{seed}", dg.damage(masks[s], boxes[s], d, seed=1000 * seed + i)))
            out.append(sc)
    # level 3a: campus, the adopted model
    l3a = Scenario("3a", "CAMPUS, adopted color model", True)
    for s in sets["CAMPUS"]:
        images[s] = io.load_image(io.find_image(s))
        l3a.items.append((s, "", pl.segment(pl.Frame.from_image(images[s]), base)[0]))
    out.append(l3a)
    # level 3b / 3c: thresholds read from the frame's own labels (2026-11-16_hs_oracle, arm hue+sat+stripes)
    cool = [s for s in sets.get("WOOD bright", []) if io.parse_name(s)["light"] in ("lampcool3", "lampcool6")]
    for level, name, stems, rule in (("3b", "BLACK, thresholds from the frame's labels", sets.get("BLACK", []), True),
                                     ("3c", "wood cool lamp, thresholds from the frame's labels", cool, False)):
        sc = Scenario(level, name, rule)
        for s in stems:
            images[s] = io.load_image(io.find_image(s))
            frame = pl.Frame.from_image(images[s])
            barrels = io.load_boxes(s)["barrels"]
            lab = oracle.with_stripes(images[s], barrels, pooled.body_mask(images[s], barrels, base.cfg), base.cfg)
            sc.items.append((s, "", pl.segment(frame, oracle.frame_model("hue+sat+stripes", frame, lab, base))[0]))
        out.append(sc)
    return out, images


# ---------------------------------------------------------------- one arm on one scenario

def run_scenario(sc: Scenario, dcfg: det.DetConfig, images, sheet_dir: Path | None):
    results, rows, causes = [], [], collections.Counter()
    for stem, tag, mask in sc.items:
        gts, clean = truth(stem)
        log: list[dict] = []
        preds = det.detect(mask, dcfg, CAM, log=log)
        res = ed.evaluate_frame(stem, preds, gts, CAM, rule="v2", clean=clean)
        results.append(res)
        for gi in res.unmatched_gt:
            g = gts[gi]
            cause, detail = att.attribute(g, preds, log, att.inside(mask, g))
            causes[cause] += 1
            rows.append({"scenario": sc.key, "stem": stem, "tag": tag, "kind": "missed", "color": dtp.COLOR_NAMES[g.color],
                         "bbox": list(g.bbox), "flags": "+".join(sorted(g.flags)), "cause": cause, "detail": detail})
        for pi in res.unmatched_pred:
            p = preds[pi]
            rows.append({"scenario": sc.key, "stem": stem, "tag": tag, "kind": "false", "color": dtp.COLOR_NAMES[p.color],
                         "bbox": list(p.bbox), "flags": "+".join(sorted(p.flags)), "cause": "false_box", "detail": p.source})
        if sheet_dir is not None and tag in ("", "seed0") and (res.unmatched_gt or res.unmatched_pred):
            sheet_dir.mkdir(parents=True, exist_ok=True)
            name = f"{sc.level}_{sc.name.split(',')[0].replace(' ', '-')}_{stem.replace('4A8B_', '')}.png"
            cv2.imwrite(str(sheet_dir / name), att.sheet(images[stem], mask, gts, preds, log, f"{sc.key} | {stem}"))
    return rp.summarize(results), rows, causes


# ---------------------------------------------------------------- the expected size against the hand-drawn boxes

def size_check(sets: dict[str, list[str]]) -> tuple[list[dict], list[str]]:
    """Every unoccluded, untruncated truth box of the train sets against the camera model at its bottom row."""
    rows = []
    for group, stems in sets.items():
        for s in stems:
            for b in io.load_boxes(s)["barrels"]:
                x0, y0, x1, y1 = b["bbox"]
                if any(f in b.get("flags", ()) for f in SKIP_SIZE_FLAGS) or io.touches_frame(b["bbox"]):
                    continue
                W, H = CAM.expected_barrel_width_px(bottom_row=y1), CAM.expected_barrel_height_px(bottom_row=y1)
                if not (np.isfinite(W) and np.isfinite(H) and W > 0):
                    continue
                pb = det.predicted_bottom(CAM, y0)
                rows.append({"set": group, "light": io.parse_name(s)["light"], "stem": s, "color": b["color"], "bbox": [x0, y0, x1, y1],
                             "bottom_row": y1, "w": x1 - x0, "h": y1 - y0, "w_expected": round(W, 1), "h_expected": round(H, 1),
                             "w_ratio": round((x1 - x0) / W, 3), "h_ratio": round((y1 - y0) / H, 3),
                             "bottom_from_top_err_px": round(pb - y1, 1) if np.isfinite(pb) else ""})

    def stat(v):
        v = np.asarray(v, float)
        return f"{np.median(v):.2f} ({np.percentile(v, 10):.2f} to {np.percentile(v, 90):.2f})"

    L = ["# Expected barrel size against the hand-drawn boxes", "",
         f"Camera `AIM_4A8B6118_BOXFIT` (f {CAM.f:.0f}, tilt {CAM.tilt_deg}, horizon row {CAM.horizon_row():.0f}). Train frames only. "
         "Boxes flagged occluded, truncated, held or bottom_estimated, and boxes touching the frame, are left out.",
         "Ratio = hand-drawn size / the size the camera model expects for a barrel whose bottom edge is at the box's bottom row "
         "(what `g` in the box tool draws). Median (10th to 90th percentile).",
         "`bottom from top` = the bottom row the detector predicts from the box's top row, minus the drawn bottom row, in px (+ = predicted lower).", "",
         "| set | boxes | width ratio | height ratio | bottom from top, px |", "|---|---|---|---|---|"]

    def line(name, rs):
        if not rs:
            return f"| {name} | 0 | - | - | - |"
        e = [r["bottom_from_top_err_px"] for r in rs if r["bottom_from_top_err_px"] != ""]
        return f"| {name} | {len(rs)} | {stat([r['w_ratio'] for r in rs])} | {stat([r['h_ratio'] for r in rs])} | {stat(e)} |"

    order = ["HOME", "CAMPUS", "BLACK", "WOOD bright", "WOOD dark"]
    for g in order:
        L.append(line(g, [r for r in rows if r["set"] == g]))
    L.append(line("wood, all 9 lamp settings", [r for r in rows if r["set"].startswith("WOOD")]))
    L += ["", "By distance (expected width: far under 35 px, mid 35 to 60, near over 60):", "",
          "| set | range | boxes | width ratio | height ratio | bottom from top, px |", "|---|---|---|---|---|---|"]
    bands = (("far", 0, 35), ("mid", 35, 60), ("near", 60, 1e9))
    for g in ("HOME", "CAMPUS", "BLACK", "WOOD"):
        for name, lo, hi in bands:
            rs = [r for r in rows if r["set"].startswith(g) and lo <= r["w_expected"] < hi]
            if rs:
                L.append(line(g, rs).replace(f"| {g} |", f"| {g} | {name} |", 1))
    return rows, L


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arms", default=",".join(ARMS), help=f"comma-separated, from: {', '.join(ARMS)}")
    ap.add_argument("--out", default=str(OUT), help="output folder (default: the results folder of this experiment)")
    ap.add_argument("--no-sheets", action="store_true")
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    arms = [a for a in args.arms.split(",") if a]
    sets = train_sets()

    size_rows, size_md = size_check(sets)
    with (out / "size_check.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(size_rows[0].keys())); w.writeheader(); w.writerows(size_rows)
    (out / "size_check.md").write_text("\n".join(size_md) + "\n")

    scenarios, images = build_scenarios(sets)
    cells, all_rows, causes = {}, [], {}
    for a in arms:
        for sc in scenarios:
            cell, rows, cs = run_scenario(sc, ARMS[a], images, None if args.no_sheets else out / "sheets" / a)
            cells[(a, sc.key)] = cell; causes[(a, sc.key)] = cs
            all_rows += [{"arm": a, **r} for r in rows]

    with (out / "scenarios.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["arm", "level", "scenario", "in_rule", "frames", "barrels", "found", "missed", "false", "false_on_negatives", "false_on_clean_negatives"])
        for a in arms:
            for sc in scenarios:
                c = cells[(a, sc.key)]
                w.writerow([a, sc.level, sc.name, int(sc.rule), c.frames, c.barrels, c.found, c.missed, c.false, c.neg_false, c.clean_neg_false])
    with (out / "per_barrel.csv").open("w", newline="") as f:
        fields = ["arm", "scenario", "stem", "tag", "kind", "color", "bbox", "flags", "cause", "detail"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(all_rows)

    def txt(c):
        return f"{c.found} / {c.barrels} ({c.false})"

    L = ["# The detector given good segmentation", "",
         f"git {bcv.git_hash()}; v2 rule; train frames only; camera AIM_4A8B6118_BOXFIT. Cells: found / barrels (false boxes). "
         f"Level 2 rows add up {len(SEEDS)} seeds of the 16 HOME frames (29 barrels each).", "",
         "| level | scenario | in the rule | " + " | ".join(arms) + " |", "|---|---|---|" + "---|" * len(arms)]
    for sc in scenarios:
        L.append(f"| {sc.level} | {sc.name} | {'yes' if sc.rule else 'report only'} | " + " | ".join(txt(cells[(a, sc.key)]) for a in arms) + " |")
    L += ["", "## What each damage level is (fractions of the barrel's box, W wide and H tall)", ""]
    for name, d in list(dg.SEVERITIES.items()) + list(dg.SINGLE.items()):
        L.append(f"- `{name}`: " + ", ".join(f"{k} {v}" for k, v in d.to_dict().items() if v not in (0, 0.0, (0.0, 0.0), (0, 0.0))))
    L += ["", "## Which test refused the missed barrels (the detector's reason log)", ""]
    for a in arms:
        L.append(f"### `{a}`")
        L.append("")
        for sc in scenarios:
            cs = causes[(a, sc.key)]
            if cs:
                L.append(f"- {sc.key}: " + ", ".join(f"{k} {v}" for k, v in cs.most_common()))
        L.append("")
    L += ["## Level 1 and level 3: every missed barrel and every false box", ""]
    for a in arms:
        L += [f"### `{a}`", "", "| scenario | frame | what | box | flags | cause | detail |", "|---|---|---|---|---|---|---|"]
        for r in all_rows:
            if r["arm"] == a and r["scenario"].split(" ")[0] in ("1", "3a", "3b"):
                L.append(f"| {r['scenario'].split(',')[0]} | {r['stem'].replace('4A8B_', '')} | {r['kind']} {r['color']} | {r['bbox']} | {r['flags']} | {r['cause']} | {r['detail']} |")
        L.append("")
    L += size_md
    (out / "summary.md").write_text("\n".join(L) + "\n")
    json.dump({"git": bcv.git_hash(), "camera": "AIM_4A8B6118_BOXFIT", "model": str(Path(wb.DEFAULT_MODEL).relative_to(PKG_ROOT)),
               "seeds": SEEDS, "arms": {a: dataclasses.asdict(ARMS[a]) for a in arms},
               "severities": {k: v.to_dict() for k, v in dg.SEVERITIES.items()}, "single": {k: v.to_dict() for k, v in dg.SINGLE.items()},
               "frames": {sc.key: sorted({s for s, _, _ in sc.items}) for sc in scenarios}}, (out / "config.json").open("w"), indent=1)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
