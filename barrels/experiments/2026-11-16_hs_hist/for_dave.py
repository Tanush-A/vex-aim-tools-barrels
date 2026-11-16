#!/usr/bin/env python3
"""The hue x saturation histograms as pictures to show (for Dave, who asked what the distributions look like):
one page per light / table condition, 3-D bars with every bar in the color of its bin.

    python barrels/experiments/2026-11-16_hs_hist/for_dave.py

Writes ``docs/HISTOGRAMS-FOR-DAVE.pdf`` (one page per condition + an overview page) and the same pages as PNG in
``results/2026-11-16_hs_hist/for_dave/``. Per page: a sample frame, then three 3-D bar plots over a 16 x 16 grid
(hue x HSV saturation, OpenCV units): all pixels, the barrel pixels, everything else. Bar height = log10(1 +
pixel count). Pixels are the ones below the horizon row (50) with brightness V >= 40, i.e. what the color model
looks at. Barrel pixels come from the hand-drawn boxes (the inner 0.6 x 0.8 of each unoccluded box, at the main
hue of its class); Dave's own frames have no per-barrel boxes, so they show all pixels only.
Train frames and unsplit frames only; test frames are never opened. Code: ``src/barrels/hshist.py``.
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import hshist as hh, io, splits, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-16_hs_hist" / "for_dave"
PDF = PKG_ROOT / "docs" / "HISTOGRAMS-FOR-DAVE.pdf"
BINS = (16, 16)
# (name filter, page title, short title, frames have per-barrel boxes)
CONDITIONS = [
    ("4A8B_window_light_", "White table, window light (home; the frames the color model was fit on)", "white, window", True),
    ("4A8B_campus_light_", "White table, campus study room (daylight + ceiling lights)", "white, campus", True),
    ("DAVE_office_speckle_", "Dave's office: speckled desk, window + room light", "Dave: speckled desk", False),
    ("DAVE_office_dark_", "Dave's office: dark table, warm dim light", "Dave: dark table", False),
    ("4A8B_window_black_", "Black table, window light", "black, window", True),
    ("4A8B_lampcool6_wood_", "Wood table, cool lamp, brightness 6", "wood, cool 6", True),
    ("4A8B_lampcool3_wood_", "Wood table, cool lamp, brightness 3", "wood, cool 3", True),
    ("4A8B_lampmid6_wood_", "Wood table, mid lamp, brightness 6", "wood, mid 6", True),
    ("4A8B_lampmid3_wood_", "Wood table, mid lamp, brightness 3", "wood, mid 3", True),
    ("4A8B_lampwarm6_wood_", "Wood table, warm lamp, brightness 6", "wood, warm 6", True),
    ("4A8B_lampwarm3_wood_", "Wood table, warm lamp, brightness 3", "wood, warm 3", True),
    ("4A8B_lampmid1_wood_", "Wood table, mid lamp, brightness 1 (nearly dark)", "wood, mid 1", True),
]


def stems_for(prefix: str) -> list[str]:
    sp = splits.load_splits()
    test, train = set(sp["test"]), set(sp["train"])
    out = []
    for p in io.list_images():
        s = p.stem
        if not s.startswith(prefix) or s in test:
            continue
        try:
            if io.parse_name(s)["scene"] in splits.UNASSIGNED_SCENES:
                continue
        except ValueError:
            continue
        if s in train or s.startswith("DAVE_"):
            out.append(s)
    return out


def bars(ax, a: np.ndarray, title: str, zmax: float) -> None:
    """3-D bars of a fine histogram: one bar per (hue, saturation) bin in the bin's own color."""
    cnt = hh.rebin(a, *BINS)
    col = hh.bin_colors(*BINS)
    hw, sw = 180 / BINS[0], 256 / BINS[1]
    xs, ys, zs, cs = [], [], [], []
    for i in range(BINS[0]):
        for j in range(BINS[1]):
            if cnt[i, j] > 0:
                xs.append(i * hw); ys.append(j * sw); zs.append(np.log10(1 + cnt[i, j])); cs.append(col[j, i])
    if xs:
        ax.bar3d(xs, ys, np.zeros(len(xs)), hw * 0.9, sw * 0.9, zs, color=cs, shade=True)
    ax.set_xticks([0, 30, 60, 90, 120, 150]); ax.set_xticklabels(["150", "0", "30", "60", "90", "120"], fontsize=7)
    ax.set_yticks([0, 64, 128, 192, 256]); ax.tick_params(labelsize=7)
    ax.set_xlim(0, 180); ax.set_ylim(0, 256); ax.set_zlim(0, zmax)
    ax.set_xlabel("hue", fontsize=8); ax.set_ylabel("saturation", fontsize=8); ax.set_zlabel("log10(1 + pixels)", fontsize=8)
    ax.view_init(elev=38, azim=-62)
    ax.set_title(title, fontsize=9)


def gated(sh: hh.SetHist, a: np.ndarray) -> np.ndarray:
    a = a.copy(); a[:, :, :sh.vb] = 0
    return a


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    model = wb.BarrelDetectorHook.load(wb.DEFAULT_MODEL).model
    pages = []
    for prefix, title, short, boxed in CONDITIONS:
        stems = stems_for(prefix)
        if not stems:
            continue
        sh = hh.SetHist(short)
        for s in stems:
            barrels = io.load_boxes(s)["barrels"] if boxed and io.boxes_path(s).exists() else []
            sh.add(s, io.load_image(io.find_image(s)), barrels, model)
        sample = next((s for s in stems if "_core_01" in s or "_cluster_01" in s), stems[0])
        pages.append((title, short, boxed, sh, sample, len(stems)))

    with PdfPages(PDF) as pdf:
        # overview: all pixels, every condition
        n = len(pages)
        cols = 4
        rows = (n + cols - 1) // cols
        fig = plt.figure(figsize=(17, 4.4 * rows))
        for k, (title, short, boxed, sh, sample, nf) in enumerate(pages):
            ax = fig.add_subplot(rows, cols, k + 1, projection="3d")
            bars(ax, gated(sh, sh.core[ORANGE] + sh.core[BLUE] + sh.rest), f"{short} ({nf} frames)", 6.5)
        fig.suptitle("Hue x saturation of every pixel, per light and table. One bar per bin, drawn in the bin's own color; height = log10(1 + pixels).\n"
                     "Pixels below the horizon row with V >= 40. Hue in OpenCV units (orange barrels near 10, blue near 105).", fontsize=12)
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        pdf.savefig(fig, dpi=110); fig.savefig(OUT / "00_overview.png", dpi=110); plt.close(fig)

        for k, (title, short, boxed, sh, sample, nf) in enumerate(pages):
            allpx = gated(sh, sh.core[ORANGE] + sh.core[BLUE] + sh.rest)
            fig = plt.figure(figsize=(15, 10.5))
            ax = fig.add_subplot(2, 2, 1)
            ax.imshow(cv2.cvtColor(io.load_image(io.find_image(sample)), cv2.COLOR_BGR2RGB)); ax.axis("off")
            ax.set_title(f"a sample frame ({sample})", fontsize=9)
            bars(fig.add_subplot(2, 2, 2, projection="3d"), allpx, f"all pixels ({int(allpx.sum()):,})", 6.5)
            if boxed:
                body = sh.body(ORANGE) + sh.body(BLUE)
                bars(fig.add_subplot(2, 2, 3, projection="3d"), body, f"barrel pixels only, from the hand-drawn boxes ({int(body.sum()):,})", 6.5)
                rest = sh.rest_gated()
                bars(fig.add_subplot(2, 2, 4, projection="3d"), rest, f"everything that is not a barrel ({int(rest.sum()):,})", 6.5)
            else:
                ax = fig.add_subplot(2, 2, 3); ax.axis("off")
                ax.text(0.02, 0.6, "No per-barrel boxes for these frames\n(Dave's boxes group touching barrels),\nso only the all-pixel histogram is shown.", fontsize=11, va="center")
            fig.suptitle(f"{title}: {nf} frames, {BINS[0]} x {BINS[1]} bins", fontsize=13)
            fig.tight_layout(rect=(0, 0, 1, 0.96))
            pdf.savefig(fig, dpi=110); fig.savefig(OUT / f"{k + 1:02d}_{short.replace(', ', '_').replace(': ', '_').replace(' ', '_')}.png", dpi=110); plt.close(fig)
    print(f"{len(pages)} conditions -> {PDF}  ({PDF.stat().st_size / 1e6:.1f} MB); PNG pages in {OUT}")
    for title, short, boxed, sh, sample, nf in pages:
        print(f"  {short}: {nf} frames, sample {sample}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
