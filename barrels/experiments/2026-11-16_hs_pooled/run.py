#!/usr/bin/env python3
"""The same hs color model, fit on all train tables instead of home only. Hypothesis, arms, scoring and the
acceptance rule: PREREG.md in this folder (written before the run).

    python barrels/experiments/2026-11-16_hs_pooled/run.py

Outputs: results/2026-11-16_hs_pooled/ — summary.md, per_set.csv, config.json (committed), sheets/ (ignored).
"""
from __future__ import annotations

import csv
import dataclasses
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import cv as bcv, detect_types as dtp, detector as det, geometry as geo, hshist as hh, io, pipeline as pl  # noqa: E402
from barrels import report as rp, splits, viz, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-16_hs_pooled"
CAM = geo.AIM_4A8B6118_BOXFIT
ARMS = ("all", "nowood", "blue")
GROUPS = ("HOME", "CAMPUS", "BLACK", "WOOD bright", "WOOD dark")
TARGET = ("BLACK", "WOOD bright")
# Run 2 (2026-11-16, after run 1): in 20 wood frames the tallest hue peak inside the blue box cores was the orange
# stripe, not the blue body (a dull blue body spreads over many hues, the stripe is one sharp peak), so 7 % of the
# "blue" fit pixels were orange and the pooled blue range came out as hue 12 to 113. The peak is now looked for
# only on the class's own side of the hue circle (real OpenCV hue). Run 1 is kept in results/.../run1/.
PEAK_RANGE = {ORANGE: (-30, 45), BLUE: (75, 150)}
SHEET_WOOD = [f"4A8B_lamp{l}_wood_{s}" for l in ("cool3", "mid6", "warm6") for s in ("core_01", "cluster_01", "occl_02", "clutter_01")]


def group_of(stem: str) -> str:
    t = io.parse_name(stem)
    if t["surface"] == "wood":
        return "WOOD dark" if t["light"].endswith("1") else "WOOD bright"
    return {"window_light": "HOME", "campus_light": "CAMPUS", "window_black": "BLACK"}[f"{t['light']}_{t['surface']}"]


def body_mask(bgr: np.ndarray, barrels: list[dict], cfg: pl.Config) -> np.ndarray:
    """A class mask from boxes: box cores, kept where the hue is within +-PEAK_HALF of the class's tallest hue
    peak in this frame (the body color; the stripe and anything else inside the core are left out)."""
    h, s, v = hh.planes(bgr)
    reg = hh.region_masks(h.shape, barrels)
    m = np.zeros(h.shape, np.uint8)
    for c in (ORANGE, BLUE):
        sel = reg[c] & (v >= cfg.v_min)
        sel[: max(0, cfg.horizon_row or 0)] = False
        if sel.sum() < 50:
            continue
        marg = np.bincount(h[sel], minlength=180).astype(float)
        real = hh.unroll(np.arange(180))
        marg[(real < PEAK_RANGE[c][0]) | (real > PEAK_RANGE[c][1])] = 0      # run 2: the peak must be on the class's side of the hue circle
        if marg.sum() < 50:
            continue
        peak = int(np.argmax(sum(np.roll(marg, k) for k in range(-2, 3))))
        m[sel & (np.abs((h - peak + 90) % 180 - 90) <= hh.PEAK_HALF)] = c
    return m


class Data:
    def __init__(self, cfg: pl.Config):
        sp = splits.load_splits()
        test = set(sp["test"])
        self.stems = [s for s in sorted(sp["train"]) if io.boxes_path(s).exists()]
        assert not set(self.stems) & test
        self.group = {s: group_of(s) for s in self.stems}
        self.scene = {s: io.parse_name(s)["scene"] for s in self.stems}
        self.frame, self.mask = {}, {}
        for s in self.stems:
            bgr = io.load_image(io.find_image(s))
            self.frame[s] = pl.Frame.from_image(bgr)
            if self.group[s] == "HOME":
                self.mask[s] = io.load_mask(io.mask_path(s))
            else:
                self.mask[s] = body_mask(bgr, io.load_boxes(s)["barrels"], cfg)

    def fit(self, stems: list[str], cfg: pl.Config) -> pl.Model:
        return pl.fit([self.frame[s] for s in stems], [self.mask[s] for s in stems], cfg)


def fit_groups(arm: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """(groups the orange range is fit on, groups the blue range is fit on)."""
    everything = ("HOME", "CAMPUS", "BLACK", "WOOD bright")
    return {"all": (everything, everything), "nowood": (everything[:3], everything[:3]), "blue": (("HOME",), everything)}[arm]


def arm_model(arm: str, data: Data, cfg: pl.Config, exclude_scene: str | None) -> pl.Model:
    og, bg = fit_groups(arm)
    pool = [s for s in data.stems if data.scene[s] != exclude_scene]
    mo = data.fit([s for s in pool if data.group[s] in og], cfg)
    mb = mo if og == bg else data.fit([s for s in pool if data.group[s] in bg], cfg)
    return dataclasses.replace(mo, boxes={ORANGE: mo.boxes[ORANGE], BLUE: mb.boxes[BLUE]})


def ranges(m: pl.Model) -> str:
    o, b = m.boxes[ORANGE], m.boxes[BLUE]
    return (f"orange hue {o.lo[0] - pl.HUE_SHIFT[ORANGE]:.0f} to {o.hi[0] - pl.HUE_SHIFT[ORANGE]:.0f}, S >= {o.lo[1]:.0f}; "
            f"blue hue {b.lo[0]:.0f} to {b.hi[0]:.0f}, S >= {b.lo[1]:.0f}")


def sheet(stems, data, masks, title) -> np.ndarray:
    tiles = []
    for s in stems:
        img = data.frame[s].bgr
        seg = viz.overlay(img, masks[s], 0.6)
        for b in io.load_boxes(s)["barrels"]:
            x0, y0, x1, y1 = b["bbox"]
            cv2.rectangle(seg, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
        seg = det.draw(seg, det.detect(masks[s], det.DetConfig(), CAM), 2)
        t = cv2.resize(np.hstack([img, seg]), None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        lab = s.replace("4A8B_", "")
        cv2.putText(t, lab, (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 3); cv2.putText(t, lab, (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        tiles.append(t)
    cols = 2
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    return np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)])


def main() -> int:
    (OUT / "sheets").mkdir(parents=True, exist_ok=True)
    base_model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL, cam=CAM).model
    cfg = base_model.cfg
    data = Data(cfg)
    sp = splits.load_splits()
    dcfg = det.DetConfig()
    dave = [s for s in rp.labeled_stems() if s.startswith("DAVE_")]
    dave_frames = {s: pl.Frame.from_image(io.load_image(io.find_image(s))) for s in dave}

    results: dict[str, dict[str, object]] = {}
    masks: dict[str, dict[str, np.ndarray]] = {}
    full: dict[str, pl.Model] = {"base": base_model}
    # base: as published (home leave-one-scene-out, the stored model elsewhere)
    sel = rp.select_frames(rp.labeled_stems(), sp)
    results["base"] = rp.run_arm(rp.Arm("base", wb.DEFAULT_MODEL), sel, sp, cam=CAM)
    masks["base"] = {s: pl.segment(data.frame[s], base_model)[0] for s in data.stems}
    scenes = sorted(set(data.scene.values()))
    for arm in ARMS:
        res, mk = {}, {}
        for sc in scenes:
            m = arm_model(arm, data, cfg, exclude_scene=sc)
            for s in data.stems:
                if data.scene[s] == sc:
                    mk[s] = pl.segment(data.frame[s], m)[0]
                    res[s] = rp.score_frame(s, mk[s], dcfg, CAM)
        full[arm] = arm_model(arm, data, cfg, exclude_scene=None)
        for s in dave:
            res[s] = rp.score_frame(s, pl.segment(dave_frames[s], full[arm])[0], dcfg, CAM)
        results[arm], masks[arm] = res, mk

    rows = []
    for arm in ("base",) + ARMS:
        res = results[arm]
        cells = {g: rp.summarize([res[s] for s in data.stems if data.group[s] == g]) for g in GROUPS}
        cells["DAVE*"] = rp.summarize([res[s] for s in dave])
        lights = {}
        for s in data.stems:
            if data.group[s].startswith("WOOD"):
                lights.setdefault(io.parse_name(s)["light"], []).append(res[s])
        for k in sorted(lights):
            cells[f"  wood {k.replace('lamp', '')}"] = rp.summarize(lights[k])
        for g, c in cells.items():
            rows.append({"arm": arm, "set": g, "frames": c.frames, "barrels": c.barrels, "found": c.found, "missed": c.missed, "false": c.false,
                         "score": c.score, "width": c.width, "clean_neg_false": c.clean_neg_false, "disqualified": c.disqualified})
    with (OUT / "per_set.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    by = {(r["arm"], r["set"]): r for r in rows}

    # per scene tag, on the target sets, to see whether a gain comes from one tag only
    tag_rows = []
    for arm in ("base",) + ARMS:
        for sc in scenes:
            c = rp.summarize([results[arm][s] for s in data.stems if data.scene[s] == sc and data.group[s] in TARGET])
            if c.frames:
                tag_rows.append((arm, sc, c))

    verdict = {}
    for arm in ARMS:
        c1 = by[(arm, "HOME")]["score"] >= 0.91 and by[(arm, "CAMPUS")]["score"] >= 0.97
        c2 = not any(by[(arm, g)]["clean_neg_false"] for g in ("HOME", "CAMPUS", "BLACK", "WOOD bright"))
        verdict[arm] = {"c1": c1, "c2": c2, "target_found": sum(by[(arm, g)]["found"] for g in TARGET)}
    passing = [a for a in ARMS if verdict[a]["c1"] and verdict[a]["c2"]]
    winner = None
    if passing:
        best = max(verdict[a]["target_found"] for a in passing)
        winner = next(a for a in ARMS if a in passing and verdict[a]["target_found"] >= best - 3)

    L = ["# The hs color model fit on all train tables", "",
         f"git {bcv.git_hash()}; v2 rule; train frames only; new arms scored leave-one-scene-tag-out. Rule: `experiments/2026-11-16_hs_pooled/PREREG.md`.", "",
         "## The ranges (each arm fit on all its fit frames)", ""]
    L += [f"- `{a}`: {ranges(full[a])}" for a in ("base",) + ARMS]
    L += ["", "## Found / barrels (false boxes), score", "", "| set | " + " | ".join(("base",) + ARMS) + " |", "|---|" + "---|" * (1 + len(ARMS))]
    for g in [r["set"] for r in rows if r["arm"] == "base"]:
        cells = []
        for a in ("base",) + ARMS:
            r = by[(a, g)]
            sc = "-" if r["score"] != r["score"] else f"{r['score']:.2f}"
            cells.append(f"{r['found']} / {r['barrels']} ({r['false']}), {sc}" + (" DQ" if r["clean_neg_false"] else ""))
        L.append(f"| {g} | " + " | ".join(cells) + " |")
    L += ["", "## Black + bright wood, by scene tag: found / barrels (false)", "", "| scene | " + " | ".join(("base",) + ARMS) + " |", "|---|" + "---|" * (1 + len(ARMS))]
    for sc in scenes:
        cs = {a: c for a, s2, c in tag_rows if s2 == sc}
        if cs:
            L.append(f"| {sc} | " + " | ".join(f"{cs[a].found} / {cs[a].barrels} ({cs[a].false})" for a in ("base",) + ARMS) + " |")
    L += ["", "## Acceptance", ""]
    for a in ARMS:
        v = verdict[a]
        L.append(f"- `{a}`: 1 home >= 0.91 and campus >= 0.97: {'pass' if v['c1'] else 'FAIL'}; 2 no box on a clean negative: {'pass' if v['c2'] else 'FAIL'}; "
                 f"3 found on black + bright wood: {v['target_found']} of {sum(by[('base', g)]['barrels'] for g in TARGET)} (base {sum(by[('base', g)]['found'] for g in TARGET)})")
    L += ["", f"**By conditions 1 to 3: {'`' + winner + '`' if winner else 'no arm passes'}.** Condition 4 (by eye on the sheets) is recorded in `by_eye.md`."]
    (OUT / "summary.md").write_text("\n".join(L) + "\n")
    json.dump({"git": bcv.git_hash(), "base_model": str(wb.DEFAULT_MODEL), "cfg_hash": cfg.short_hash(), "arms": {a: fit_groups(a) for a in ARMS},
               "ranges": {a: {str(c): full[a].boxes[c].to_dict() for c in (ORANGE, BLUE)} for a in full},
               "frames": {g: [s for s in data.stems if data.group[s] == g] for g in GROUPS}, "winner_by_1_to_3": winner},
              (OUT / "config.json").open("w"), indent=1)
    for arm in ("base",) + ARMS:
        cv2.imwrite(str(OUT / "sheets" / f"{arm}_black.png"), sheet([s for s in data.stems if data.group[s] == "BLACK"], data, masks[arm], arm))
        cv2.imwrite(str(OUT / "sheets" / f"{arm}_wood.png"), sheet(SHEET_WOOD, data, masks[arm], arm))
        cv2.imwrite(str(OUT / "sheets" / f"{arm}_campus.png"), sheet([s for s in data.stems if data.group[s] == "CAMPUS"][:12], data, masks[arm], arm))
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
