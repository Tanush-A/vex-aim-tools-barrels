#!/usr/bin/env python3
"""TODO step 8: hue x saturation histograms. How much do H and S of the barrels and of the table move between
light settings and tables, and is H x S enough to tell a barrel from a wood table?

Written before the run.
  H1. The barrels' hue moves little between lights (a few OpenCV units); their saturation moves a lot, down with
      dim light and with a lamp of the barrel's opposite warmth (blue under a warm lamp).
  H2. The wood table sits inside or next to the orange hue sector, with saturation overlapping the orange body
      under at least the warm lamp settings. If so no H x S threshold, fixed or adaptive, separates orange barrel
      from wood there, and the adaptive model needs a third cue (brightness, or shape via the detector).
  H3. The fixed model (fit on the white home table) loses most of the barrel body at brightness 1 because the
      pixels fail the V >= 40 gate, not because of H or S.
What would count against them: H1 fails if a body's median hue moves by more than its own 5-95 width between
lights; H2 fails if the best H x S lookup at 1 % flood keeps > 90 % of the orange body under every wood light;
H3 fails if the bright share of the cores at brightness 1 is above one half.

Nothing is tuned here and nothing is adopted: this is a look. Train frames only (HOME 16, CAMPUS 21, wood
ladder 90 = 10 arrangements x 9 lights, black 10); the 47 test frames are refused. Boxes give the barrel pixels
(the core of each unoccluded box, body color = the tallest hue peak, see ``barrels.hshist``); for HOME the masks
give the same numbers a second way, as a check of that shortcut.

    python barrels/experiments/2026-11-16_hs_hist/run.py

Outputs: results/2026-11-16_hs_hist/ — summary.md, per_set.csv, transfer.csv, config.json, and pictures
(hist_*.png, bars_*.png, ladder_grid.png, shift.png, seg_*.png).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import cv as bcv, hshist as hh, io, pipeline as pl, splits, viz, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-16_hs_hist"
ALIASES = {"window_light": "HOME", "campus_light": "CAMPUS", "window_black": "BLACK"}
WARMTH, LEVELS = ("warm", "mid", "cool"), ("1", "3", "6")
LADDER = [f"lamp{w}{b}_wood" for w in WARMTH for b in LEVELS]
FLOOD = 0.01
HS_BINS, HSV_BINS = (36, 32), (36, 32, 8)
SEG_SCENES = ("core_01", "occl_02", "clutter_01")
TOO_DARK = 0.10        # under this share of bright core pixels a class has no measurable body color in the set


def train_sets() -> dict[str, list[str]]:
    sp = splits.load_splits()
    test = set(sp["test"])
    sets: dict[str, list[str]] = {}
    for s in sorted(sp["train"]):
        assert s not in test
        if not io.boxes_path(s).exists():
            continue
        t = io.parse_name(s)
        key = f"{t['light']}_{t['surface']}"
        sets.setdefault(ALIASES.get(key, key), []).append(s)
    return sets


def pct(x: float, nd: int = 0) -> str:
    return "-" if x != x else f"{100 * x:.{nd}f}"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL).model
    sets = train_sets()
    order = [n for n in ("HOME", "CAMPUS", "BLACK") if n in sets] + [n for n in LADDER if n in sets]
    hists: dict[str, hh.SetHist] = {}
    for name in order:
        sh = hh.SetHist(name)
        for s in sets[name]:
            sh.add(s, io.load_image(io.find_image(s)), io.load_boxes(s)["barrels"], model)
        hists[name] = sh
    # HOME a second way: the barrel pixels from the masks (exact), to check the box-core shortcut
    hm = hh.SetHist("HOME (masks)", exact_body=True)
    for s in sets["HOME"]:
        hm.add(s, io.load_image(io.find_image(s)), io.load_boxes(s)["barrels"], model, mask=io.load_mask(io.mask_path(s)))
    wood = hh.SetHist("WOOD, all 9 lights")
    for n in LADDER:
        wood.merge(hists[n])
    table_rows = [("HOME (masks)", hm)] + [(n, hists[n]) for n in order] + [(wood.name, wood)]

    # ---- per-set numbers
    rows = []
    for name, sh in table_rows:
        r = {"set": name, "frames": sh.frames}
        rs = sh.rest_stats()
        r.update({f"rest_{k}": v for k, v in rs.items()})
        for c in (ORANGE, BLUE):
            n = hh.NAMES[c]
            r.update({f"{n}_{k}": v for k, v in sh.stats(c).items()})
            s_pct = model.cfg.hs_s_pct[0 if c == ORANGE else 1]
            r.update({f"{n}_refit_{k}": v for k, v in sh.refit(c, s_pct, model.cfg.hs_h_pct, model.cfg.hs_h_margin).items()})
            b, rest = sh.body(c), sh.rest_gated()
            tot = max(1, sh.rest.sum())
            # flood is counted against ALL rest pixels below the horizon, dark ones included, like the model's flood
            bb, rr = hh.rebin(b, *HS_BINS), hh.rebin(rest, *HS_BINS)
            pick = hh.best_bins(bb, rr * 1.0, FLOOD * tot / max(1, rr.sum()))
            r[f"{n}_best_hs"] = float(bb[pick].sum() / bb.sum()) if bb.sum() else float("nan")
            b3, r3 = hh.rebin(b, *HSV_BINS), hh.rebin(rest, *HSV_BINS)
            pick3 = hh.best_bins(b3, r3 * 1.0, FLOOD * tot / max(1, r3.sum()))
            r[f"{n}_best_hsv"] = float(b3[pick3].sum() / b3.sum()) if b3.sum() else float("nan")
        rows.append(r)
    with (OUT / "per_set.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    # ---- transfer: the best H x S lookup of set i (1 % flood there) applied to set j
    names = order
    trans = []
    for c in (ORANGE, BLUE):
        for i in names:
            a = hists[i]
            bi, ri = hh.rebin(a.body(c), *HS_BINS), hh.rebin(a.rest_gated(), *HS_BINS)
            pick = hh.best_bins(bi, ri * 1.0, FLOOD * max(1, a.rest.sum()) / max(1, ri.sum()))
            for j in names:
                d = hists[j]
                bj, rj = hh.rebin(d.body(c), *HS_BINS), hh.rebin(d.rest_gated(), *HS_BINS)
                trans.append({"class": hh.NAMES[c], "from": i, "to": j,
                              "recall": float(bj[pick].sum() / bj.sum()) if bj.sum() else float("nan"),
                              "flood": float(rj[pick].sum() / max(1, d.rest.sum()))})
    with (OUT / "transfer.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(trans[0].keys())); w.writeheader(); w.writerows(trans)

    # ---- pictures
    for name, sh in [(n, hists[n]) for n in order] + [("WOOD_all", wood)]:
        hh.figure_set(sh, model, OUT / f"hist_{name}.png", (16, 16))
        hh.figure_set(sh, model, OUT / f"hist_{name}_36x32.png", HS_BINS)
        hh.figure_bars(sh, OUT / f"bars_{name}.png", (16, 16))
    ladder_grid(hists, model)
    shift_plot(rows, model)
    for sc in SEG_SCENES:
        seg_sheet(sc, model)

    # ---- summary
    by = {r["set"]: r for r in rows}
    L = ["# Hue x saturation histograms (TODO 8)", "",
         f"Adopted hs model `{model.cfg.short_hash()}`: orange hue 3 to 13, S >= 140; blue hue 103 to 119, S >= 113; pixels below row "
         f"{model.cfg.horizon_row} with V >= {model.cfg.v_min}. Train frames only. Hue in OpenCV units (0-179; a negative hue is below the wrap: -3 = 177).", "",
         "## 1. Where the body colors sit, and what the fixed model does with them", "",
         "`bright` = share of the box-core pixels with V >= 40. `model` = share of the bright body pixels the fixed model labels as that class.", "",
         "| set | frames | mean V | orange hue 50 (5 to 95) | orange S 50 (5 to 95) | orange bright % | orange model % | blue hue 50 (5 to 95) | blue S 50 (5 to 95) | blue bright % | blue model % |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, _ in table_rows:
        r = by[name]
        cells = []
        for n in ("orange", "blue"):
            if r[f"{n}_bright"] < TOO_DARK:          # the few bright pixels in the cores are not the body: no color to report
                cells += ["too dark", "too dark", pct(r[f"{n}_bright"]), "0"]
            else:
                cells += [f"{r[f'{n}_h50']:.0f} ({r[f'{n}_h5']:.0f} to {r[f'{n}_h95']:.0f})", f"{r[f'{n}_s50']:.0f} ({r[f'{n}_s5']:.0f} to {r[f'{n}_s95']:.0f})",
                          pct(r[f"{n}_bright"]), pct(r[f"{n}_pass"])]
        L.append(f"| {name} | {r['frames']} | {r['rest_mean_v']:.0f} | " + " | ".join(cells) + " |")
    L += ["", "## 2. Everything that is not a barrel (table, clutter, robot parts; below the horizon row)", "",
          "`flood` = share of all those pixels the fixed model paints as a barrel color.", "",
          "| set | bright % | hue 50 (5 to 95) | S 50 (5 to 95) | flood orange % | flood blue % |", "|---|---|---|---|---|---|"]
    for name, _ in table_rows:
        r = by[name]
        L.append(f"| {name} | {pct(r['rest_bright'])} | {r['rest_h50']:.0f} ({r['rest_h5']:.0f} to {r['rest_h95']:.0f}) | {r['rest_s50']:.0f} ({r['rest_s5']:.0f} to {r['rest_s95']:.0f}) | "
                 f"{pct(r['rest_flood_orange'], 1)} | {pct(r['rest_flood_blue'], 1)} |")
    L += ["", "## 3. The thresholds the model's own recipe would give if it were fit on each set", "",
          "Same recipe as the adopted model (S floor = 5th percentile of the orange body's S, 15th of the blue; hue sector = 5th to 95th percentile above the floor, widened by 2), "
          "but on this set's body pixels. `flood` = share of the non-barrel pixels of the same set inside that box. This is a description of where the colors are, not a model anyone runs.", "",
          "| set | orange hue | orange S floor | orange flood % | blue hue | blue S floor | blue flood % |", "|---|---|---|---|---|---|---|"]
    for name, _ in table_rows:
        r = by[name]
        cells = []
        for n in ("orange", "blue"):
            cells += (["too dark"] * 3 if r[f"{n}_bright"] < TOO_DARK else
                      [f"{r[f'{n}_refit_h_lo']:.0f} to {r[f'{n}_refit_h_hi']:.0f}", f"{r[f'{n}_refit_s_lo']:.0f}", pct(r[f"{n}_refit_flood"], 1)])
        L.append(f"| {name} | " + " | ".join(cells) + " |")
    L += ["", f"## 4. The most any H x S lookup could keep at {100 * FLOOD:.0f} % flood", "",
          f"Bins {HS_BINS[0]} x {HS_BINS[1]} (H x S) and {HSV_BINS[0]} x {HSV_BINS[1]} x {HSV_BINS[2]} (with V). The lookup is built on the very frames it is scored on, so this is a ceiling, not a result.", "",
          "| set | orange: fixed model % (its flood %) | orange: best H x S % | orange: best H x S x V % | blue: fixed model % (its flood %) | blue: best H x S % | blue: best H x S x V % |",
          "|---|---|---|---|---|---|---|"]
    for name, _ in table_rows:
        r = by[name]
        cells = []
        for n in ("orange", "blue"):
            cells += ([f"0 ({pct(r[f'rest_flood_{n}'], 1)})", "too dark", "too dark"] if r[f"{n}_bright"] < TOO_DARK else
                      [f"{pct(r[f'{n}_pass'])} ({pct(r[f'rest_flood_{n}'], 1)})", pct(r[f"{n}_best_hs"]), pct(r[f"{n}_best_hsv"])])
        L.append(f"| {name} | " + " | ".join(cells) + " |")
    for c in ("orange", "blue"):
        L += ["", f"## 5. Transfer, {c}: the best H x S lookup of the row's set applied to the column's set", "",
              "Each cell: body kept % / non-barrel painted %. The diagonal is section 4.", "",
              "| from \\ to | " + " | ".join(n.replace("_wood", "").replace("lamp", "") for n in names) + " |", "|---|" + "---|" * len(names)]
        t = {(x["from"], x["to"]): x for x in trans if x["class"] == c}
        for i in names:
            L.append(f"| {i.replace('_wood', '').replace('lamp', '')} | " + " | ".join(f"{pct(t[(i, j)]['recall'])} / {pct(t[(i, j)]['flood'], 1)}" for j in names) + " |")
    (OUT / "summary.md").write_text("\n".join(L) + "\n")
    json.dump({"model": str(wb.DEFAULT_MODEL), "config_hash": model.cfg.short_hash(), "git": bcv.git_hash(),
               "core": hh.CORE, "peak_half": hh.PEAK_HALF, "rest_pad": hh.REST_PAD, "flood": FLOOD, "hs_bins": HS_BINS, "hsv_bins": HSV_BINS,
               "sets": {n: sets[n] for n in order}}, (OUT / "config.json").open("w"), indent=1)
    print("\n".join(L))
    return 0


def ladder_grid(hists, model) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rects = hh.model_rects(model)
    fig, axs = plt.subplots(3, 3, figsize=(13, 10))
    for i, wm in enumerate(WARMTH):
        for j, lv in enumerate(LEVELS):
            sh = hists[f"lamp{wm}{lv}_wood"]
            allpx = (sh.core[ORANGE] + sh.core[BLUE] + sh.rest).copy(); allpx[:, :, :sh.vb] = 0
            ax = axs[i, j]
            ax.imshow(hh.color_image(hh.rebin(allpx, *HS_BINS)), origin="lower", extent=(0, 180, 0, 256), aspect="auto", interpolation="nearest")
            rs = sh.rest_stats()
            hh._axes(ax, rects, f"{wm} lamp, brightness {lv}: mean V {rs['mean_v']:.0f}, {pct(rs['bright'])} % of the table bright enough")
            for c, mk in ((ORANGE, "o"), (BLUE, "s")):
                st = sh.stats(c)
                if st["n"] and st["bright"] >= TOO_DARK:
                    ax.plot([st["h50"] + hh.ROLL], [st["s50"]], mk, ms=9, mfc="none", mec="white", mew=1.6)
            ax.plot([rs["h50"] + hh.ROLL], [rs["s50"]], "x", ms=9, mec="white", mew=1.6)
            if i == 2:
                ax.set_xlabel("hue", fontsize=8)
            if j == 0:
                ax.set_ylabel("saturation", fontsize=8)
    fig.suptitle("Wood table, 9 lamp settings: every pixel, each bin in its own color. Dashed = what the fixed model accepts. "
                 "o orange body, square blue body, x everything else (medians)", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "ladder_grid.png", dpi=110); plt.close(fig)


def shift_plot(rows, model) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rects = hh.model_rects(model)
    fig, axs = plt.subplots(1, 3, figsize=(17, 6))
    titles = {"orange": "orange barrel body", "blue": "blue barrel body", "rest": "everything that is not a barrel"}
    colors = {"warm": "#d1495b", "mid": "#555555", "cool": "#2e86ab", "HOME": "#2a9d8f", "CAMPUS": "#8338ec", "BLACK": "#000000"}
    for ax, key in zip(axs, ("orange", "blue", "rest")):
        for r in rows:
            n = r["set"]
            if n.startswith("HOME (") or n.startswith("WOOD,"):
                continue
            if n.startswith("lamp"):
                wm = next(w for w in WARMTH if w in n); lv = n[len("lamp" + wm)]
                col, ms, lab = colors[wm], {"1": 5, "3": 8, "6": 11}[lv], f"{wm[0]}{lv}"
            else:
                col, ms, lab = colors[n], 9, n
            h50, h5, h95, s50, s5, s95 = (r[f"{key}_{k}"] for k in ("h50", "h5", "h95", "s50", "s5", "s95"))
            if h50 != h50 or (key != "rest" and r[f"{key}_bright"] < TOO_DARK):
                continue
            ax.errorbar([h50], [s50], xerr=[[max(0, h50 - h5)], [max(0, h95 - h50)]], yerr=[[max(0, s50 - s5)], [max(0, s95 - s50)]], fmt="o", ms=ms, color=col, alpha=0.75, lw=0.8, capsize=2)
            ax.annotate(lab, (h50, s50), xytext=(5, 5), textcoords="offset points", fontsize=8, color=col)
        for c, (lo, hi, slo) in rects.items():
            if (key == "orange" and c == ORANGE) or (key == "blue" and c == BLUE) or key == "rest":
                from matplotlib.patches import Rectangle
                ax.add_patch(Rectangle((lo - hh.ROLL, slo), hi - lo, 256 - slo, fill=False, ec="k", ls="--", lw=1))
        ax.set_ylim(0, 260); ax.set_xlabel("hue (OpenCV; negative = below the wrap)"); ax.set_ylabel("saturation")
        ax.set_title(titles[key] + ": median, bars = 5th to 95th percentile", fontsize=10); ax.grid(alpha=0.3)
    axs[0].set_xlim(-12, 30); axs[1].set_xlim(85, 135)
    fig.suptitle("Where the colors sit per set. w/m/c = warm/mid/cool lamp on wood, 1/3/6 = brightness (dot size). Dashed = the fixed model", fontsize=11)
    fig.tight_layout(); fig.savefig(OUT / "shift.png", dpi=110); plt.close(fig)


def seg_sheet(scene: str, model) -> None:
    """One wood arrangement under the 9 lights: raw | what the fixed model labels."""
    test = set(splits.load_splits()["test"])
    tiles = []
    for wm in WARMTH:
        row = []
        for lv in LEVELS:
            stem = f"4A8B_lamp{wm}{lv}_wood_{scene}"
            assert stem not in test, stem
            img = io.load_image(io.find_image(stem))
            seg, _ = pl.segment(pl.Frame.from_image(img), model)
            t = cv2.resize(np.hstack([img, viz.overlay(img, seg, 0.75)]), None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            cv2.putText(t, f"{wm} {lv}", (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 3)
            cv2.putText(t, f"{wm} {lv}", (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
            row.append(t)
        tiles.append(np.hstack(row))
    cv2.imwrite(str(OUT / f"seg_{scene}.png"), np.vstack(tiles))


if __name__ == "__main__":
    raise SystemExit(main())
