#!/usr/bin/env python3
"""Barrel color distribution on the v1 pool frames (train split only; test is never touched).

Answers constraints.md unknowns #4/#5 for the white table + window light: where orange and
blue barrel pixels sit in RGB, whether an axis-aligned box is a good shape (fullness, PCA),
how much table/wall falls inside the boxes, how the saturation/brightness gates and the
median/MAD priors trade barrel recall against non-barrel rejection.

    python barrels/experiments/2026-10-19_data_analysis/analyze.py [--out results/<date>_data_analysis]

Writes stats.md + figures to the results folder and copies three downsized figures next to this
script. The YUV chroma-plane figure is a non-v1 extra (feeds v1.5), flagged as such.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

import cv2
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from barrels import boxfit as bf  # noqa: E402
from barrels import io, priors, splits  # noqa: E402

HERE = Path(__file__).resolve().parent
CAP = 3000
BG_ROWS, TABLE_ROWS, WALL_MID = slice(0, 50), slice(400, 480), slice(50, 150)


def rgb_to_uv(rgb: np.ndarray) -> np.ndarray:
    """8-bit YUV chroma (U, V) per Dave's slides (NAVIGATOR.md K-1)."""
    r, g, b = [rgb[..., i].astype(np.float64) for i in range(3)]
    u = (-37.945 * r - 74.494 * g + 112.439 * b) / 256 + 128
    v = (112.439 * r - 94.154 * g - 18.285 * b) / 256 + 128
    return np.stack([u, v], -1)


def pct(a, q):
    return [int(round(x)) for x in np.percentile(a, q)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=io.PKG_ROOT / "results" / f"{dt.date.today().isoformat()}_data_analysis")
    args = ap.parse_args()
    out = args.out
    if out.exists():
        out = out.with_name(out.name + "_2")
    out.mkdir(parents=True)

    pool = splits.load_splits()["train"]
    rng = np.random.default_rng(0)
    cls = {"orange": io.ORANGE, "blue": io.BLUE}
    capped = {c: [] for c in cls}; allpx = {c: [] for c in cls}
    table, wall, wallmid, other = [], [], [], []
    frames = []
    for stem in pool:
        p = io.RAW_DIR / f"{stem}.png"
        bgr = io.load_image(p); m = io.load_mask(io.mask_path(p))
        rgb = bgr[..., ::-1].astype(np.int16)
        frames.append((stem, rgb, m))
        for c, v in cls.items():
            allpx[c].append(rgb[m == v])
            capped[c].append(bf.sample_class_pixels(rgb, m, v, max_px=CAP, rng=rng))
        oth = m == io.OTHER
        table.append(rgb[TABLE_ROWS][oth[TABLE_ROWS]][::3]); wall.append(rgb[BG_ROWS][oth[BG_ROWS]][::3])
        wallmid.append(rgb[WALL_MID][oth[WALL_MID]][::3]); other.append(rgb[oth][::11])
    capped = {c: np.concatenate(v) for c, v in capped.items()}; allpx = {c: np.concatenate(v) for c, v in allpx.items()}
    table, wall, wallmid, other = [np.concatenate(x) for x in (table, wall, wallmid, other)]
    sat = lambda X: X.max(-1) - X.min(-1)   # noqa: E731
    val = lambda X: X.max(-1)               # noqa: E731

    md = [f"# Barrel color distribution — pool frames ({len(pool)}), {dt.date.today()}", "",
          f"Pixels: orange all {len(allpx['orange'])}, capped {len(capped['orange'])} ({CAP}/image); blue all {len(allpx['blue'])}, capped {len(capped['blue'])}; "
          f"table band (rows 400–480, other) {len(table)}, wall band (rows 0–50) {len(wall)}, wall rows 50–150 {len(wallmid)}, all other (subsampled) {len(other)}.", ""]

    # --- percentiles
    md += ["## Per-channel percentiles (1 / 50 / 99)", "", "| set | R | G | B | sat (max−min) 1/5/50/95/99 | val (max) 1/5/50/99 |", "|---|---|---|---|---|---|"]
    for name, X in (("orange (capped)", capped["orange"]), ("blue (capped)", capped["blue"]), ("orange (all)", allpx["orange"]), ("blue (all)", allpx["blue"]),
                    ("table band", table), ("wall band", wall), ("wall rows 50–150", wallmid), ("all other", other)):
        md.append(f"| {name} | {pct(X[:,0],[1,50,99])} | {pct(X[:,1],[1,50,99])} | {pct(X[:,2],[1,50,99])} | {pct(sat(X),[1,5,50,95,99])} | {pct(val(X),[1,5,50,99])} |")

    # --- boxes, fullness, PCA, overlap
    md += ["", "## RGB boxes (percentile bounds), fullness, PCA", "", "| class / fit set | pct | lo | hi | volume | fullness v4 | v8 | v16 | PCA var frac | linearity | cos(axis1, gray) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    boxes = {}
    for c in cls:
        for setname, X in (("capped", capped[c]), ("all", allpx[c])):
            for (plo, phi) in ((1, 99), (2, 98), (5, 95)):
                box = bf.fit_box(X, plo, phi)
                if setname == "capped" and (plo, phi) == (1, 99):
                    boxes[c] = box
                pc = bf.pca(X)
                md.append(f"| {c} / {setname} | {plo}–{phi} | {[int(x) for x in box.lo]} | {[int(x) for x in box.hi]} | {box.volume():.2e} | "
                          f"{bf.fullness(X, box, 4):.2f} | {bf.fullness(X, box, 8):.2f} | {bf.fullness(X, box, 16):.2f} | "
                          f"{[round(v,2) for v in pc['var_fraction']]} | {pc['linearity']:.2f} | {pc['cos_to_gray']:.2f} |")
    md += ["", "## Non-barrel pixels inside each 1–99 capped box", "", "| set | inside orange box | inside blue box |", "|---|---|---|"]
    for name, X in (("table band", table), ("wall band", wall), ("wall rows 50–150", wallmid), ("all other", other)):
        md.append(f"| {name} | {bf.in_box(X, boxes['orange']).mean()*100:.1f} % | {bf.in_box(X, boxes['blue']).mean()*100:.1f} % |")
    ov = bf.box_overlap(boxes["orange"], boxes["blue"])
    if ov is not None:
        o_in = bf.in_box(allpx["orange"], ov); b_in = bf.in_box(allpx["blue"], ov)
        o_res = (allpx["orange"][o_in][:, 0] > allpx["orange"][o_in][:, 2]).mean() if o_in.any() else float("nan")
        b_res = (allpx["blue"][b_in][:, 0] <= allpx["blue"][b_in][:, 2]).mean() if b_in.any() else float("nan")
        md += ["", f"Orange∩blue overlap box: lo {[int(x) for x in ov.lo]} hi {[int(x) for x in ov.hi]}, volume {ov.volume():.2e} "
               f"({ov.volume()/boxes['orange'].volume()*100:.0f} % of orange box, {ov.volume()/boxes['blue'].volume()*100:.0f} % of blue box). "
               f"Labeled pixels inside it: orange {o_in.mean()*100:.1f} %, blue {b_in.mean()*100:.1f} %; the R>B rule resolves {o_res*100:.1f} % of those orange and {b_res*100:.1f} % of those blue pixels correctly."]
    else:
        md += ["", "Orange and blue boxes do not overlap."]

    # --- gate survival
    md += ["", "## Survival under the saturation floor and brightness gate", "", "| threshold | orange | blue | table band | wall band | wall 50–150 | all other |", "|---|---|---|---|---|---|---|"]
    sets = (("orange", allpx["orange"]), ("blue", allpx["blue"]), ("table", table), ("wall", wall), ("wallmid", wallmid), ("other", other))
    surv = {"sat": {}, "val": {}}
    for s in (20, 30, 40, 50, 60, 80):
        row = [(sat(X) >= s).mean() * 100 for _, X in sets]; surv["sat"][s] = row
        md.append(f"| sat ≥ {s} | " + " | ".join(f"{v:.1f} %" for v in row) + " |")
    for v in (20, 40, 60, 80, 100):
        row = [(val(X) >= v).mean() * 100 for _, X in sets]; surv["val"][v] = row
        md.append(f"| val ≥ {v} | " + " | ".join(f"{x:.1f} %" for x in row) + " |")

    # --- prior operating curves (per frame, averaged)
    ks = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 6.0]
    curves = {"table": {k: [] for k in ks}, "wall": {k: [] for k in ks}}
    guard = {"table": 0, "wall": 0}
    for stem, rgb, m in frames:
        s_img = sat(rgb)
        for name, rows in (("table", TABLE_ROWS), ("wall", BG_ROWS)):
            st = priors.band_stats(rgb, rows, fit_mask=s_img < 40)
            if not st.enabled:
                guard[name] += 1; continue
            for k in ks:
                rej = priors.reject_like(rgb, st, k)
                o = (m == io.ORANGE); b = (m == io.BLUE); non = (m == io.OTHER)
                non_sat = non & (s_img >= 40)              # the non-barrel pixels the sat floor would NOT remove
                curves[name][k].append((rej[o].mean() if o.any() else np.nan, rej[b].mean() if b.any() else np.nan,
                                        rej[non].mean(), rej[non_sat].mean() if non_sat.any() else np.nan))
    md += ["", "## Prior operating points (fit on low-sat band pixels, averaged over pool frames)", "",
           "| prior | k | orange rejected | blue rejected | all non-barrel rejected | saturated (≥40) non-barrel rejected |", "|---|---|---|---|---|---|"]
    for name in ("table", "wall"):
        for k in ks:
            a = np.nanmean(np.array(curves[name][k]), axis=0)
            md.append(f"| {name} | {k} | {a[0]*100:.1f} % | {a[1]*100:.1f} % | {a[2]*100:.1f} % | {a[3]*100:.1f} % |")
    md.append(f"\nGuard trips (prior disabled): table {guard['table']}, wall {guard['wall']} of {len(frames)} frames.")

    # --- YUV chroma (non-v1 extra)
    uv = {c: rgb_to_uv(capped[c]) for c in cls}; uv_other = rgb_to_uv(other)
    md += ["", "## Non-v1 extra: YUV chroma plane (U, V), brightness dropped", "", "| class | box 1–99 lo | hi | fullness v4 | v8 | PCA var frac | other inside |", "|---|---|---|---|---|---|---|"]
    for c in cls:
        box = bf.fit_box(uv[c], 1, 99); pc = bf.pca(uv[c])
        md.append(f"| {c} | {[int(x) for x in box.lo]} | {[int(x) for x in box.hi]} | {bf.fullness(uv[c], box, 4):.2f} | {bf.fullness(uv[c], box, 8):.2f} | {[round(v,2) for v in pc['var_fraction']]} | {bf.in_box(uv_other, box).mean()*100:.1f} % |")

    (out / "stats.md").write_text("\n".join(md) + "\n")
    json.dump({"pool": pool, "boxes": {c: boxes[c].to_dict() for c in cls}, "cap": CAP}, (out / "summary.json").open("w"), indent=1)

    # ---------- figures
    def draw_box(ax, box, color, proj):
        lo, hi = box.lo, box.hi
        i, j = proj
        ax.add_patch(plt.Rectangle((lo[i], lo[j]), hi[i] - lo[i], hi[j] - lo[j], fill=False, ec=color, lw=1.5))
    sub = lambda X, n: X[np.random.default_rng(0).choice(len(X), min(n, len(X)), replace=False)]  # noqa: E731
    fig = plt.figure(figsize=(12, 5.5))
    for k, (el, az) in enumerate(((20, -60), (20, 30))):
        ax = fig.add_subplot(1, 2, k + 1, projection="3d")
        for X, col, nm in ((sub(table, 3000), "0.6", "table"), (sub(wall, 3000), "0.3", "wall"), (sub(capped["orange"], 4000), "#ff8000", "orange"), (sub(capped["blue"], 4000), "#0064ff", "blue")):
            ax.scatter(X[:, 0], X[:, 1], X[:, 2], s=1, c=col, label=nm, alpha=0.4)
        for c, col in (("orange", "#ff8000"), ("blue", "#0064ff")):
            lo, hi = boxes[c].lo, boxes[c].hi
            for s_, e_ in [((lo[0],lo[1],lo[2]),(hi[0],lo[1],lo[2])),((lo[0],lo[1],lo[2]),(lo[0],hi[1],lo[2])),((lo[0],lo[1],lo[2]),(lo[0],lo[1],hi[2])),
                           ((hi[0],hi[1],hi[2]),(lo[0],hi[1],hi[2])),((hi[0],hi[1],hi[2]),(hi[0],lo[1],hi[2])),((hi[0],hi[1],hi[2]),(hi[0],hi[1],lo[2])),
                           ((hi[0],lo[1],lo[2]),(hi[0],hi[1],lo[2])),((hi[0],lo[1],lo[2]),(hi[0],lo[1],hi[2])),((lo[0],hi[1],lo[2]),(hi[0],hi[1],lo[2])),
                           ((lo[0],hi[1],lo[2]),(lo[0],hi[1],hi[2])),((lo[0],lo[1],hi[2]),(hi[0],lo[1],hi[2])),((lo[0],lo[1],hi[2]),(lo[0],hi[1],hi[2]))]:
                ax.plot(*zip(s_, e_), c=col, lw=0.8)
        ax.set_xlabel("R"); ax.set_ylabel("G"); ax.set_zlabel("B"); ax.view_init(el, az); ax.set_xlim(0, 255); ax.set_ylim(0, 255); ax.set_zlim(0, 255)
        if k == 0: ax.legend(markerscale=6, loc="upper left")
    fig.suptitle("Labeled barrel pixels in RGB (pool frames, ≤3000/image) with 1–99 % boxes; table/wall bands in gray")
    fig.tight_layout(); fig.savefig(out / "scatter_rgb.png", dpi=110); plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, proj, lab in zip(axes, ((0, 1), (0, 2), (1, 2)), ("R–G", "R–B", "G–B")):
        for X, col, nm in ((sub(other, 6000), "0.7", "other"), (sub(table, 3000), "0.5", "table band"), (sub(wall, 3000), "0.25", "wall band"), (sub(capped["orange"], 5000), "#ff8000", "orange"), (sub(capped["blue"], 5000), "#0064ff", "blue")):
            ax.scatter(X[:, proj[0]], X[:, proj[1]], s=1, c=col, alpha=0.35, label=nm)
        for c, col in (("orange", "#ff8000"), ("blue", "#0064ff")): draw_box(ax, boxes[c], col, proj)
        ax.set_xlim(0, 255); ax.set_ylim(0, 255); ax.set_title(lab); ax.set_xlabel(lab[0]); ax.set_ylabel(lab[-1])
    axes[0].legend(markerscale=6); fig.tight_layout(); fig.savefig(out / "proj_rg_rb_gb.png", dpi=110); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    ts = np.arange(0, 181, 5)
    for ax, fn, title in ((axes[0], sat, "saturation floor: fraction with sat ≥ t"), (axes[1], val, "brightness gate: fraction with max channel ≥ t")):
        for nm, X, col in (("orange", allpx["orange"], "#ff8000"), ("blue", allpx["blue"], "#0064ff"), ("table band", table, "0.6"), ("wall band", wall, "0.3"), ("wall 50–150", wallmid, "0.1"), ("all other", other, "0.8")):
            f = fn(X); ax.plot(ts, [(f >= t).mean() for t in ts], c=col, label=nm, ls="--" if nm in ("wall 50–150", "all other") else "-")
        ax.set_title(title); ax.set_xlabel("t"); ax.set_ylabel("fraction kept"); ax.grid(alpha=0.3)
    axes[0].legend(); fig.tight_layout(); fig.savefig(out / "sat_val_survival.png", dpi=110); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, name in zip(axes, ("table", "wall")):
        a = np.array([np.nanmean(np.array(curves[name][k]), axis=0) for k in ks])
        ax.plot(ks, a[:, 0] * 100, "-o", c="#ff8000", label="orange rejected (bad)"); ax.plot(ks, a[:, 1] * 100, "-o", c="#0064ff", label="blue rejected (bad)")
        ax.plot(ks, a[:, 2] * 100, "-s", c="0.4", label="non-barrel rejected (good)"); ax.plot(ks, a[:, 3] * 100, "--s", c="0.1", label="saturated non-barrel rejected (good)")
        ax.set_title(f"{name} prior (median/MAD, low-sat fit): rejection vs k"); ax.set_xlabel("k"); ax.set_ylabel("%"); ax.grid(alpha=0.3); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(out / "prior_curves.png", dpi=110); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 6))
    for X, col, nm in ((sub(uv_other, 6000), "0.7", "other"), (sub(uv["orange"], 5000), "#ff8000", "orange"), (sub(uv["blue"], 5000), "#0064ff", "blue")):
        ax.scatter(X[:, 0], X[:, 1], s=1, c=col, alpha=0.35, label=nm)
    for c, col in (("orange", "#ff8000"), ("blue", "#0064ff")): draw_box(ax, bf.fit_box(uv[c], 1, 99), col, (0, 1))
    ax.set_xlabel("U (blueness)"); ax.set_ylabel("V (redness)"); ax.set_title("NON-v1 extra: YUV chroma plane, brightness dropped"); ax.legend(markerscale=6)
    fig.tight_layout(); fig.savefig(out / "yuv_chroma.png", dpi=110); plt.close(fig)

    figs = HERE / "figures"; figs.mkdir(exist_ok=True)
    for name in ("scatter_rgb.png", "proj_rg_rb_gb.png", "prior_curves.png"):
        img = cv2.imread(str(out / name)); cv2.imwrite(str(figs / name), cv2.resize(img, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA), [cv2.IMWRITE_PNG_COMPRESSION, 9])
    shutil.copy(out / "stats.md", HERE / "stats.md")
    print((out / "stats.md").read_text()); print("written to", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
