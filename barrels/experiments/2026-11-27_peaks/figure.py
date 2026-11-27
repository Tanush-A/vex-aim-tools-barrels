"""One picture for part A: the hue profile (S >= 40) of a few frames: every gated pixel, the hand-box cores, and
what the pair finder keeps. Train frames only.

    PYTHONPATH=barrels/src python barrels/experiments/2026-11-27_peaks/figure.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import measure as ms  # noqa: E402
import peaks as pk  # noqa: E402

from barrels import counting as ct  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

STEMS = ["4A8B_window_light_touch_02", "4A8B_lampmid6_bathtile_core_01", "4A8B_window_abpwhite_occlx_10",
         "4A8B_lampmid6_ottoman_edge_01", "4A8B_campus_light_window_01", "4A8B_lampwarm6_bathtile_core_01"]


def main():
    frames = jg.train_frames()
    have = set(frames["ordinary"])
    stems = [s for s in STEMS if s in have]
    if len(stems) < len(STEMS):
        # fall back to the first frame of each named condition
        conds = [ct.condition_of(s) for s in STEMS]
        stems = []
        for cnd_ in conds:
            c = [s for s in frames["ordinary"] if ct.condition_of(s) == cnd_]
            if c:
                stems.append(c[0])
    gts, _ = ct.load_gts(stems)
    fig, axes = plt.subplots(len(stems), 1, figsize=(10, 2.3 * len(stems)), sharex=True)
    x = np.arange(180) - pk.ROLL
    for ax, stem in zip(axes, stems):
        fr = jg.load_frame(stem)
        h, s, v, sel = pk.selections(fr.bgr)
        cores, _ = ms.truth_masks(h.shape, gts[stem])
        g = pk.gate(h.shape) & (v >= pk.V_MIN) & (s >= 40)
        allp = np.bincount(h[g], minlength=180)
        core = np.bincount(h[g & (cores[ORANGE] | cores[BLUE])], minlength=180)
        keep = np.zeros(h.shape, bool)
        for c in (ORANGE, BLUE):
            m, _ = sel["F6_pair_small"][c]
            lo, hi = pk.REGION[c]
            keep |= m & (h >= lo) & (h < hi)
        pair = np.bincount(h[g & keep], minlength=180)
        order = np.argsort(x)
        for arr, lab, col in ((allp, "every pixel", "0.5"), (core, "inside hand boxes", "C3"), (pair, "pair finder keeps", "C0")):
            ax.semilogy(x[order], np.maximum(arr[order], 0.8), label=lab, color=col)
        ax.axvspan(3, 13, color="orange", alpha=0.15)
        ax.axvspan(103, 119, color="blue", alpha=0.1)
        ax.set_xlim(-15, 140)
        ax.set_ylim(0.8, None)
        ax.set_title(stem.replace("4A8B_", ""), fontsize=9)
    axes[0].legend(fontsize=8, loc="upper right")
    axes[-1].set_xlabel("hue (OpenCV units; shaded = the fixed ranges)")
    fig.tight_layout()
    out = ms.OUT / "hue_profiles.png"
    fig.savefig(out, dpi=90)
    print(out, stems)


if __name__ == "__main__":
    main()
