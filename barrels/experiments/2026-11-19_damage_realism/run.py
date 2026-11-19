#!/usr/bin/env python3
"""How damaged is the damaged-mask test? (2026-11-19; Tanush's question.)

The test "if the segmentation is good, the detector finds the barrel" (``experiments/2026-11-18_det_given_seg``)
damages the hand-made HOME masks at three made-up levels (``degrade.SEVERITIES``: light, medium, heavy). A detector
change that finds many more hidden barrels (``slice_box`` + ``cover_unpinned`` + ``stripe_two``, arm ``all`` of
``experiments/2026-11-19_det_occl``) is held back because at "medium" it draws 4 false boxes instead of 1. Nobody
has checked whether real segmentation looks like "medium". This script measures it. It changes no detector, no
color model, no geometry and no scoring rule.

HYPOTHESIS (written before the first run):
  H1  On the white tables (HOME, CAMPUS) a free-standing barrel loses under 10 % of its pixels at the median, and
      nearly all of that is at the edges: about 1 px at the outline and at the body / stripe seam (mixed pixels).
      That is the "light" level's edge setting.
  H2  At the median there is no hole on the upper body and the stripe is in one piece. At the 90th percentile a
      hole is smaller than "light"'s (0.3 W x 0.2 H) and the stripe is still in one piece. "Medium" puts a
      0.5 W x 0.3 H hole, a pale patch across the stripe AND a break in the stripe on EVERY barrel: expected to be
      beyond the 90th percentile white-table barrel in at least three of its six kinds, and to look like the black
      table or the wood table under a lamp instead.
  H3  Random dropout inside a barrel is under 2 %; fewer than 5 specks of barrel color per frame off the barrels.
  H4  At the two realistic levels defined below, arm ``all`` draws no more false boxes than the default
      (``edge+cap``), and finds at least as many barrels. So the "4 false boxes instead of 1" exists only at damage
      the white tables do not show.
  H5  Of the measured kinds at their 90th-percentile amount, eaten edges cost the most barrels (they thin the
      stripe of a far barrel below the height floor), not highlights.
  What would count against: "medium" inside the 90th percentile for most kinds; or ``all`` drawing 2 or more false
  boxes over the default at "bad day".

THE RULE FOR THE REALISTIC LEVELS (fixed before the run):
  Measured on the free-standing, unflagged barrels of the 16 HOME train frames as the eval table segments them
  (color model re-fit without the frame's scene), against the hand-made masks, with ``barrels.damage_measure``.
    "white tables, typical"   every field = the median over those barrels;
    "white tables, bad day"   every field = the 90th percentile.
  top_highlight = (top_hole_w, top_hole_h); stripe_highlight = stripe_hole_w; stripe_breaks = (breaks rounded up,
  stripe_break_w); erode_px = the larger of edge_outer_px and edge_seam_px, rounded to a whole pixel (the field
  is whole pixels; the unrounded number is reported); dropout = dropout; speckle = specks per frame (groups under
  20 px) over the HOME and CAMPUS train frames. A hole across the stripe is read by two instruments (the hole and
  the column reading), so it enters twice: the levels err on the harsh side. "Bad day" puts the 90th percentile of
  EVERY kind on EVERY barrel at once, which is harsher than a 90th-percentile barrel: an upper bound of a bad day.
  CAMPUS has no hand masks: the box instrument (``measure_box``) says whether CAMPUS is worse than HOME; if it is
  for some kind, that is reported, not folded into the rule.

WHAT IS RUN
  measure   the mask instrument on HOME (stored model; leave-one-scene-out) and, to check the instrument and to
            have the three made-up levels in the same units, on the simulated damage itself; the box instrument on
            the HOME hand masks (its zero point), the simulated levels, HOME, CAMPUS, and as extreme references the
            black table and the wood table under three lamps (cool 3, mid 6, warm 6), all with the adopted model;
            specks per frame. Writes the levels the rule gives (``proposed_levels.json``).
  arms      ``base``, ``edge+cap`` (the default) and ``all`` of ``2026-11-19_det_occl/occl_arms.py`` (loaded by
            path) on: the perfect masks, light / medium / heavy (must reproduce the stored numbers), the two
            realistic levels (``degrade.REALISTIC``), the real segmentations themselves, and one measured kind at
            a time at its 90th-percentile amount (alone, and "bad day" without it). 5 seeds as in the earlier
            test, and 20 seeds for the false-box counts. Every false box at the realistic levels gets a sheet.

Train frames only; a test frame is never opened (asserted here and in the loaded scripts).

    python barrels/experiments/2026-11-19_damage_realism/run.py            # measure, then arms
    python barrels/experiments/2026-11-19_damage_realism/run.py measure

Outputs: results/2026-11-19_damage_realism/ — measured.md, per_barrel.csv, per_box.csv, specks.csv,
proposed_levels.json, levels.md, levels.csv, false_boxes.csv, config.json (committed); false_sheets/ (ignored by git).
``summary.md`` there is written by hand from these.
"""
from __future__ import annotations

import collections
import csv
import dataclasses
import importlib.util
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import cv as bcv, damage_measure as dm, degrade as dg, detect_types as dtp, detector as det, eval_det as ed, geometry as geo  # noqa: E402
from barrels import io, pipeline as pl, report as rp, splits, worldmap_bridge as wb  # noqa: E402
from barrels.io import PKG_ROOT  # noqa: E402


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod)
    return mod


OCCL = HERE.parent / "2026-11-19_det_occl"
sys.path.insert(0, str(OCCL))                                             # its run.py does ``import occl_arms``
R = load("det_occl_run", OCCL / "run.py")                                 # train_stems, segmentations, eligible
G = load("det_given_seg_run", HERE.parent / "2026-11-18_det_given_seg" / "run.py")   # truth, att (reason log, sheet)
occl_arms = R.occl_arms

OUT = PKG_ROOT / "results" / "2026-11-19_damage_realism"
CAM = geo.AIM_4A8B6118_BOXFIT
ARMS = ("base", "edge+cap", "all")
SEEDS = tuple(range(5))            # as in the earlier test: found is "of 145"
MORE_SEEDS = tuple(range(20))      # for the false-box counts
WOOD = {"lampcool3": "WOOD cool lamp 3", "lampmid6": "WOOD mid lamp 6", "lampwarm6": "WOOD warm lamp 6"}
TYPICAL, BAD = "white tables, typical", "white tables, bad day"
LOW_BAD = {"stripe_thickness", "stripe_span", "core_cov", "upper_cov"}    # fields where a LOW value is the damage
TEST = set(splits.load_splits()["test"])


def no_test(stems) -> None:
    assert not set(stems) & TEST, "a test frame leaked in"


# ---------------------------------------------------------------- the masks to measure

def sources():
    """(hand, boxes, mask_src, box_src, frames): the HOME hand masks; every truth box per HOME stem (what the
    damage is applied around, as in the earlier test); name -> [(stem, tag, mask)] for the mask instrument and for
    the box instrument; name -> [(stem, mask)] of the real sets, for the specks."""
    stems = R.train_stems()
    for v in stems.values():
        no_test(v)
    segs = R.segmentations(stems, with_extreme=True)
    hand = segs["HOME hand masks"]
    home = sorted(hand)
    assert home == [s for s in G.train_sets()["HOME"] if io.mask_path(s).exists()], "not the earlier test's HOME frames"
    model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    stored = {s: pl.segment(pl.Frame.from_image(io.load_image(io.find_image(s))), model)[0] for s in home}
    boxes = {s: [tuple(g.bbox) for g in G.truth(s)[0]] for s in home}

    def sim(d):
        return [(s, f"seed{seed}", dg.damage(hand[s], boxes[s], d, seed=1000 * seed + i)) for seed in SEEDS for i, s in enumerate(home)]

    sims = {f"simulated: {k}": sim(d) for k, d in dg.SEVERITIES.items()}
    sims.update({f"simulated: {k}": sim(d) for k, d in {**getattr(dg, "REALISTIC", {}), **getattr(dg, "WORST_SEEN", {})}.items()})
    real_home = {"HOME, stored model": [(s, "", stored[s]) for s in home],
                 "HOME, leave-one-scene-out": [(s, "", segs["HOME color model"][s]) for s in home]}
    mask_src = {**real_home, **sims}
    box_src = {"HOME hand masks (no damage)": [(s, "", hand[s]) for s in home], **sims, **real_home,
               "CAMPUS": [(s, "", m) for s, m in sorted(segs["CAMPUS color model"].items())],
               "BLACK table": [(s, "", m) for s, m in sorted(segs["BLACK"].items())]}
    for light, name in WOOD.items():
        box_src[name] = [(s, "", m) for s, m in sorted(segs["WOOD"].items()) if io.parse_name(s)["light"] == light]
    frames = {k: [(s, m) for s, _, m in v] for k, v in box_src.items() if not k.startswith(("simulated", "HOME hand"))}
    return hand, boxes, mask_src, box_src, frames


def free_barrels(stem: str) -> list[dict]:
    """The barrels measured: no flag, 3 px inside the frame, not overlapping another barrel's box (``eligible`` of
    the occlusion scorecard)."""
    barrels = io.load_boxes(stem)["barrels"]
    return [b for i, b in enumerate(barrels) if R.eligible(b, [o for j, o in enumerate(barrels) if j != i])]


# ---------------------------------------------------------------- statistics and tables

def finite(vals) -> np.ndarray:
    v = np.asarray([x for x in vals if x is not None and x != ""], float)
    return v[np.isfinite(v)]


def pct(vals, q: float) -> float:
    v = finite(vals)
    return float(np.percentile(v, q)) if len(v) else math.nan


def tri(rows: list[dict], field: str, fmt: str) -> str:
    """median / 90th percentile / worst (for the LOW_BAD fields: median / 10th percentile / lowest)."""
    v = finite(r.get(field) for r in rows)
    if not len(v):
        return "-"
    low = field in LOW_BAD
    return f"{np.median(v):{fmt}} / {np.percentile(v, 10 if low else 90):{fmt}} / {(v.min() if low else v.max()):{fmt}}"


def share(rows: list[dict], test) -> str:
    return f"{sum(1 for r in rows if test(r))} of {len(rows)}" if rows else "-"


MASK_ROWS = [   # (plain name, field, format, the degrade field it stands for)
    ("barrel pixels not painted, share", "lost", ".2f", ""),
    ("edges eaten at the outline, px", "edge_outer_px", ".1f", "erode_px"),
    ("edges eaten at the body / stripe seam, px", "edge_seam_px", ".1f", "erode_px"),
    ("random dropout inside, share", "dropout", ".3f", "dropout"),
    ("largest hole on the upper body: width / W", "top_hole_w", ".2f", "top_highlight w"),
    ("... its height / H", "top_hole_h", ".2f", "top_highlight h"),
    ("widest hole across the stripe, / W", "stripe_hole_w", ".2f", "stripe_highlight"),
    ("breaks in the stripe (count)", "stripe_breaks", ".0f", "stripe_breaks n"),
    ("widest break in the stripe, / W", "stripe_break_w", ".2f", "stripe_breaks w"),
    ("stripe unpainted at its two ends, / W", "stripe_end_gap", ".2f", ""),
    ("painted stripe thickness / hand-made (low = worse)", "stripe_thickness", ".2f", ""),
    ("paint spilled beside the barrel, / its area", "spill", ".2f", "(not simulated)"),
]
BOX_ROWS = [
    ("box core painted, share (low = worse)", "core_cov", ".2f"),
    ("upper core painted body color (low = worse)", "upper_cov", ".2f"),
    ("stripe: first to last painted column / W (low = worse)", "stripe_span", ".2f"),
    ("breaks in the stripe (count)", "stripe_breaks", ".0f"),
    ("widest break in the stripe, / W", "stripe_break_w", ".2f"),
    ("largest hole in the upper core: width / W", "top_hole_w", ".2f"),
    ("... its height / H", "top_hole_h", ".2f"),
    ("widest hole across the middle rows, / W", "mid_hole_w", ".2f"),
]


def setting(d: dg.Damage, key: str) -> str:
    return {"erode_px": str(d.erode_px), "dropout": f"{d.dropout:g}", "top_highlight w": f"{d.top_highlight[0]:g}", "top_highlight h": f"{d.top_highlight[1]:g}",
            "stripe_highlight": f"{d.stripe_highlight:g}", "stripe_breaks n": str(d.stripe_breaks[0]), "stripe_breaks w": f"{d.stripe_breaks[1]:g}"}.get(key, "")


def propose(rows: list[dict], specks_per_frame: list[int]) -> tuple[dict[str, dg.Damage], dict]:
    """The rule of the header: the two realistic levels from the HOME leave-one-scene-out barrels and the specks
    per white-table frame. Also the unrounded numbers."""
    levels, raw = {}, {}
    for name, p in ((TYPICAL, 50), (BAD, 90)):
        q = {f: pct([r.get(f) for r in rows], p) for f in ("top_hole_w", "top_hole_h", "stripe_hole_w", "stripe_breaks", "stripe_break_w",
                                                         "edge_outer_px", "edge_seam_px", "dropout")}
        q["specks"] = pct(specks_per_frame, p)
        raw[name] = {k: round(v, 4) for k, v in q.items()}
        tw, th = round(q["top_hole_w"], 2), round(q["top_hole_h"], 2)
        if min(tw, th) <= 0:
            tw = th = 0.0
        n, bw = int(math.ceil(q["stripe_breaks"] - 1e-9)), round(q["stripe_break_w"], 2)
        if n == 0 or bw == 0:
            n, bw = 0, 0.0
        levels[name] = dg.Damage(top_highlight=(tw, th), stripe_highlight=round(q["stripe_hole_w"], 2), stripe_breaks=(n, bw),
                                 erode_px=int(round(max(q["edge_outer_px"], q["edge_seam_px"]))), dropout=round(q["dropout"], 3),
                                 speckle=int(round(q["specks"])))
    return levels, raw


# ---------------------------------------------------------------- stage 1: measure

def measure(out: Path) -> None:
    hand, _, mask_src, box_src, frames = sources()
    brow, xrow, srow = [], [], []
    for name, items in mask_src.items():
        for stem, tag, mask in items:
            for b in free_barrels(stem):
                m = dm.measure_barrel(hand[stem], mask, tuple(b["bbox"]), dtp.COLOR_BY_NAME[b["color"]])
                brow.append({"source": name, "stem": stem, "tag": tag, "id": b["id"], "color": b["color"], **m})
    for name, items in box_src.items():
        for stem, tag, mask in items:
            for b in free_barrels(stem):
                m = dm.measure_box(mask, tuple(b["bbox"]), dtp.COLOR_BY_NAME[b["color"]])
                xrow.append({"source": name, "stem": stem, "tag": tag, "id": b["id"], "color": b["color"], **m})
    for name, items in frames.items():
        for stem, mask in items:
            boxes = [tuple(b["bbox"]) for b in io.load_boxes(stem)["barrels"]]
            areas = dm.specks(mask, boxes, hand[stem] if name.startswith("HOME") else None)
            srow.append({"source": name, "stem": stem, **dm.speck_counts(areas), "areas": " ".join(map(str, areas[:40]))})

    for fname, rows in (("per_barrel.csv", brow), ("per_box.csv", xrow), ("specks.csv", srow)):
        fields = list(dict.fromkeys(k for r in rows for k in r))
        with (out / fname).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
            w.writerows({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()} for r in rows)

    def of(rows, name):
        return [r for r in rows if r["source"] == name]

    loso = of(brow, "HOME, leave-one-scene-out")
    white_specks = [r["specks"] for r in srow if r["source"] in ("HOME, leave-one-scene-out", "CAMPUS")]
    levels, raw = propose(loso, white_specks)
    json.dump({"rule": "see the header of experiments/2026-11-19_damage_realism/run.py", "barrels": len(loso), "frames_for_specks": len(white_specks),
               "unrounded": raw, "levels": {k: v.to_dict() for k, v in levels.items()}}, (out / "proposed_levels.json").open("w"), indent=1)

    sims = [k for k in mask_src if k.startswith("simulated")]
    reals = [k for k in mask_src if not k.startswith("simulated")]
    L = ["# Measured: the damage real segmentation has, next to the simulated levels", "",
         f"git {bcv.git_hash()}; train frames only; adopted color model `{Path(wb.DEFAULT_MODEL).parent.name}`. Barrels measured: no flag, free-standing "
         "(the occlusion scorecard's rule). W, H = the hand-drawn box.", "",
         "## 1. With the hand-made masks (HOME): the same units as `degrade.py`", "",
         f"{len(loso)} barrels of the 16 HOME train frames. Real columns: median / 90th percentile / worst barrel. Simulated columns: the level's "
         "setting, then what the same instrument reads back from the simulated masks (median / 90th percentile; 5 seeds).", "",
         "| kind of damage | " + " | ".join(reals) + " | " + " | ".join(s.replace("simulated: ", "") for s in sims) + " |",
         "|---|" + "---|" * (len(reals) + len(sims))]
    all_levels = {**dg.SEVERITIES, **getattr(dg, "REALISTIC", {}), **getattr(dg, "WORST_SEEN", {})}
    for label, field, fmt, key in MASK_ROWS:
        cells = [tri(of(brow, k), field, fmt) for k in reals]
        for s in sims:
            v = finite(r.get(field) for r in of(brow, s))
            st = setting(all_levels[s.replace("simulated: ", "")], key)
            back = f"{np.median(v):{fmt}} / {np.percentile(v, 10 if field in LOW_BAD else 90):{fmt}}" if len(v) else "-"
            cells.append((f"**{st}** → " if st else "") + back)
        L.append(f"| {label} | " + " | ".join(cells) + " |")
    L.append("| barrels with a hole on the upper body | " + " | ".join(share(of(brow, k), lambda r: r.get("top_hole_w", 0) > 0) for k in reals + sims) + " |")
    L.append("| barrels with a hole across the stripe | " + " | ".join(share(of(brow, k), lambda r: r.get("stripe_hole_w", 0) > 0) for k in reals + sims) + " |")
    L.append("| barrels whose stripe is in one piece | " + " | ".join(share(of(brow, k), lambda r: r.get("stripe_pieces") == 1) for k in reals + sims) + " |")
    L.append("| barrels whose stripe is not painted at all | " + " | ".join(share(of(brow, k), lambda r: r.get("stripe_pieces") == 0) for k in reals + sims) + " |")
    L += ["", "Where the largest upper-body hole sits (HOME, leave-one-scene-out; centre as a share of the box, 0 = left / top): "
          + "; ".join(f"{r['stem'].replace('4A8B_window_light_', '')} {r['color']} {r['top_hole_w']:.2f} x {r['top_hole_h']:.2f} at ({r['top_hole_cx']:.2f}, {r['top_hole_cy']:.2f})"
                      for r in loso if r.get("top_hole_w", 0) > 0) + ".", "",
          "## 2. With the hand-drawn boxes only (every set): comparable between the rows of THIS table", "",
          "No hand mask is needed, so CAMPUS, the black table and the wood table can be measured. The first row is the zero point: the hand-made "
          "masks read with this instrument (a barrel is not a rectangle, so the core is not all paint). Median / 90th percentile / worst "
          "(for the 'low = worse' columns: median / 10th percentile / lowest).", "",
          "| set | barrels | " + " | ".join(lbl for lbl, _, _ in BOX_ROWS) + " | stripe in one piece | no stripe paint |",
          "|---|---|" + "---|" * (len(BOX_ROWS) + 2)]
    for name in box_src:
        rows = of(xrow, name)
        L.append(f"| {name} | {len(rows)} | " + " | ".join(tri(rows, f, fmt) for _, f, fmt in BOX_ROWS)
                 + f" | {share(rows, lambda r: r.get('stripe_pieces') == 1)} | {share(rows, lambda r: r.get('stripe_pieces') == 0)} |")
    L += ["", "## 3. Barrel-colored paint off the barrels, per frame", "",
          f"Groups of barrel-colored pixels more than {dm.PAD} px outside every hand-drawn box (HOME: and where the hand mask says 'other'). "
          f"A speck is a group under {dm.SPECK_MAX} px (the detector drops those); a blob is larger (an orange or blue thing that is not a barrel, "
          "a reflection). The simulation's specks are 4 or 9 px: light 5, medium 15, heavy 30 per frame. Median / 90th percentile / worst frame.", "",
          "| set | frames | specks per frame | blobs per frame | largest group, px | median speck size, px |", "|---|---|---|---|---|---|"]
    for name in frames:
        rows = of(srow, name)
        sizes = [int(a) for r in rows for a in r["areas"].split() if int(a) < dm.SPECK_MAX]
        L.append(f"| {name} | {len(rows)} | {tri(rows, 'specks', '.0f')} | {tri(rows, 'blobs', '.0f')} | {tri(rows, 'largest', '.0f')} | "
                 f"{np.median(sizes) if sizes else 0:.0f} |")
    L += ["", "## 4. The levels the rule gives", "",
          f"From the {len(loso)} HOME barrels (leave-one-scene-out) and the specks of {len(white_specks)} HOME and CAMPUS frames. Unrounded: "
          + "; ".join(f"{k}: " + ", ".join(f"{a} {b:g}" for a, b in v.items()) for k, v in raw.items()) + ".", ""]
    for k, d in levels.items():
        L.append(f"- `{k}`: `{d}`")
    have = getattr(dg, "REALISTIC", None)
    L += ["", "`degrade.REALISTIC` " + ("holds exactly these." if have == levels else "does NOT hold these (yet): " + repr(have))]
    (out / "measured.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


# ---------------------------------------------------------------- stage 2: the arms on the levels

def zoom(sheet: np.ndarray, box, pad: int = 45, scale: int = 3) -> np.ndarray:
    """The part of an attribution sheet (photo | mask with boxes, 2 x) around ``box``, both halves, enlarged."""
    x0, y0, x1, y1 = box
    a, b = max(0, x0 - pad), max(0, y0 - pad)
    c, d = min(640, x1 + pad), min(480, y1 + pad)
    left, right = sheet[2 * b:2 * d, 2 * a:2 * c], sheet[2 * b:2 * d, 1280 + 2 * a:1280 + 2 * c]
    return cv2.resize(np.hstack([left, right]), None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)


def run_items(level: str, arm: str, items, images, sheet_dir: Path | None):
    """One arm on one list of (stem, tag, mask): the cell, the false boxes, the causes of the misses."""
    cfg = occl_arms.ARMS[arm]
    results, false, causes = [], [], collections.Counter()
    for stem, tag, mask in items:
        gts, clean = G.truth(stem)
        log: list[dict] = []
        preds = det.detect(mask, cfg, CAM, log=log)
        res = ed.evaluate_frame(stem, preds, gts, CAM, rule="v2", clean=clean)
        results.append(res)
        for gi in res.unmatched_gt:
            causes[G.att.attribute(gts[gi], preds, log, G.att.inside(mask, gts[gi]))[0]] += 1
        for pi in res.unmatched_pred:
            p = preds[pi]
            same = [(ed.box_iou(p.bbox, g.bbox), g) for g in gts if g.color == p.color]
            iou, g = max(same, key=lambda t: t[0]) if same else (0.0, None)
            false.append({"level": level, "arm": arm, "stem": stem, "tag": tag, "color": dtp.COLOR_NAMES[p.color], "box": list(p.bbox),
                          "box_w_over_expected": round(p.width / CAM.expected_barrel_width_px(bottom_row=p.bbox[3]), 2),
                          "flags": "+".join(sorted(p.flags)), "source": p.source, "best_overlap_same_color": round(iou, 2),
                          "that_truth_box": list(g.bbox) if g is not None else "", "that_truth_flags": "+".join(sorted(g.flags)) if g is not None else "",
                          "that_truth_also_missed": int(g is not None and any(gts[gi] is g for gi in res.unmatched_gt))})
            if sheet_dir is not None:
                sheet_dir.mkdir(parents=True, exist_ok=True)
                sh = G.att.sheet(images[stem], mask, gts, preds, log, "")
                name = f"{level.replace(', ', '_').replace(' ', '-')}_{arm}_{stem.replace('4A8B_', '')}_{tag or 'real'}_{p.bbox[0]}-{p.bbox[1]}.png"
                cv2.imwrite(str(sheet_dir / name), zoom(sh, p.bbox))
    return rp.summarize(results), false, causes


def one_at_a_time(d: dg.Damage) -> dict[str, dg.Damage]:
    """``d`` one kind at a time, and ``d`` without one kind."""
    zero = dg.Damage().to_dict()
    kinds = [k for k, v in d.to_dict().items() if v != zero[k] and v not in ((0.0, 0.0), (0, 0.0))]
    out = {f"only {k}": dg.Damage(**{k: getattr(d, k)}) for k in kinds}
    out.update({f"bad day without {k}": dataclasses.replace(d, **{k: getattr(dg.Damage(), k)}) for k in kinds})
    return out


def arms(out: Path) -> None:
    assert hasattr(dg, "REALISTIC"), "degrade.REALISTIC is not defined yet: run `measure`, then add the two levels to degrade.py"
    hand, boxes, mask_src, box_src, _ = sources()
    home = sorted(hand)
    images = {s: io.load_image(io.find_image(s)) for s in home + [s for s, _, _ in box_src["CAMPUS"]]}

    def sim(d, seeds):
        return [(s, f"seed{seed}", dg.damage(hand[s], boxes[s], d, seed=1000 * seed + i)) for seed in seeds for i, s in enumerate(home)]

    bad = dg.REALISTIC[BAD]
    kinds = one_at_a_time(bad)
    levels = [("perfect masks (HOME)", [(s, "", hand[s]) for s in home], None)]
    levels += [(k, sim(d, SEEDS), sim(d, MORE_SEEDS)) for k, d in {**dg.REALISTIC, **dg.WORST_SEEN, **dg.SEVERITIES}.items()]
    levels += [("real: HOME, leave-one-scene-out", mask_src["HOME, leave-one-scene-out"], None), ("real: HOME, stored model", mask_src["HOME, stored model"], None),
               ("real: CAMPUS", box_src["CAMPUS"], None)]
    levels += [(k, sim(d, SEEDS), sim(d, MORE_SEEDS)) for k, d in kinds.items()]

    cells, more, false_rows, causes = {}, {}, [], {}
    for name, items, items20 in levels:
        for a in ARMS:
            sheets = out / "false_sheets" if name in dg.REALISTIC or name in dg.WORST_SEEN or name.startswith("real") else None
            cells[(name, a)], f5, causes[(name, a)] = run_items(name, a, items, images, None if items20 is not None else sheets)
            if items20 is not None:
                more[(name, a)], f20, _ = run_items(name, a, items20, images, sheets)
                false_rows += f20
            else:
                false_rows += f5

    with (out / "levels.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["level", "arm", "seeds", "frames", "barrels", "found", "missed", "false"])
        for (name, a), c in cells.items():
            w.writerow([name, a, len(SEEDS) if (name, a) in more else 1, c.frames, c.barrels, c.found, c.missed, c.false])
        for (name, a), c in more.items():
            w.writerow([name, a, len(MORE_SEEDS), c.frames, c.barrels, c.found, c.missed, c.false])
    fields = list(false_rows[0].keys()) if false_rows else ["level"]
    with (out / "false_boxes.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(false_rows)

    def txt(c):
        return f"{c.found} / {c.barrels} ({c.false})"

    def table(names, cellmap, title):
        T = [title, "", "| level | " + " | ".join(f"`{a}`" for a in ARMS) + " |", "|---|" + "---|" * len(ARMS)]
        for n in names:
            if (n, ARMS[0]) in cellmap:
                T.append(f"| {n} | " + " | ".join(txt(cellmap[(n, a)]) for a in ARMS) + " |")
        return T + [""]

    main_names = [n for n, _, _ in levels if n not in kinds]
    L = ["# The occlusion arms on realistic damage", "",
         f"git {bcv.git_hash()}; v2 rule; train frames only; the 16 HOME hand masks (29 barrels). Cells: found / barrels (false boxes). "
         "`base` = the defaults before the occlusion round; `edge+cap` = today's default on `wip/detector-occl`; `all` = with the three held-back "
         "switches (`slice_box`, `cover_unpinned`, `stripe_two`).", ""]
    L += table(main_names, cells, f"## {len(SEEDS)} seeds, as in the earlier test (light / medium / heavy must match `results/2026-11-19_det_occl/verdict.md`)")
    L += table(main_names, more, f"## {len(MORE_SEEDS)} seeds (the simulated levels only): the false-box counts on four times as many masks")
    L += ["## What each level is", ""]
    for k, d in {**dg.REALISTIC, **dg.WORST_SEEN, **dg.SEVERITIES}.items():
        L.append(f"- `{k}`: " + (", ".join(f"{a} {b}" for a, b in d.to_dict().items() if b not in (0, 0.0, (0.0, 0.0), (0, 0.0))) or "no damage"))
    L += ["", f"## One measured kind at a time, at its 90th-percentile amount (`{BAD}`), and that level without one kind", ""]
    L += table(list(kinds), cells, f"{len(SEEDS)} seeds:")
    L += table(list(kinds), more, f"{len(MORE_SEEDS)} seeds:")
    L += ["## Which test refused the missed barrels (5 seeds; the detector's reason log)", ""]
    for n in [TYPICAL, BAD, *dg.WORST_SEEN] + list(kinds):
        for a in ("edge+cap", "all"):
            cs = causes[(n, a)]
            if cs:
                L.append(f"- {n}, `{a}`: " + ", ".join(f"{k} {v}" for k, v in cs.most_common()))
    L += ["", f"## Every false box at the realistic levels and on the real segmentations ({len(MORE_SEEDS)} seeds; sheets in `false_sheets/`)", "",
          "| level | arm | frame | seed | color | box | width / a barrel's | flags | best overlap with a true box of its color | that barrel | also missed |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in false_rows:
        if r["level"] in dg.REALISTIC or r["level"] in dg.WORST_SEEN or r["level"].startswith("real"):
            L.append(f"| {r['level']} | {r['arm']} | {r['stem'].replace('4A8B_window_light_', '').replace('4A8B_', '')} | {r['tag'].replace('seed', '')} | {r['color']} | {r['box']} | "
                     f"{r['box_w_over_expected']} | {r['flags']} | {r['best_overlap_same_color']} | {r['that_truth_box']} {r['that_truth_flags']} | {'yes' if r['that_truth_also_missed'] else 'no'} |")
    (out / "levels.md").write_text("\n".join(L) + "\n")
    json.dump({"git": bcv.git_hash(), "camera": "AIM_4A8B6118_BOXFIT", "model": str(Path(wb.DEFAULT_MODEL).relative_to(PKG_ROOT)), "seeds": SEEDS,
               "more_seeds": MORE_SEEDS, "arms": {a: dataclasses.asdict(occl_arms.ARMS[a]) for a in ARMS},
               "levels": {k: d.to_dict() for k, d in {**dg.REALISTIC, **dg.WORST_SEEN, **dg.SEVERITIES, **kinds}.items()},
               "home_frames": home}, (out / "config.json").open("w"), indent=1)
    print("\n".join(L))


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    OUT.mkdir(parents=True, exist_ok=True)
    what = argv[0] if argv else "both"
    if what in ("measure", "both"):
        measure(OUT)
    if what in ("arms", "both") and (what == "arms" or hasattr(dg, "REALISTIC")):
        arms(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
