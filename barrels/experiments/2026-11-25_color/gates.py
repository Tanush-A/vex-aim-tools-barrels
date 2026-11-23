#!/usr/bin/env python3
"""Step 1 of the 2026-11-25 color work: which barrel pixels can NO setting of the six sliders paint, and which fixed
gate blocks them.

    python barrels/experiments/2026-11-25_color/gates.py

For every boxed train frame and every free-standing barrel in it (no `occluded`, no `truncated` flag), the pixels
that should be the body color (core columns, rows 15-30 % and 70-85 % of the box height from the bottom) and the
stripe color (rows 42-58 %) are tested against the fixed gates of the hs model, in this order:

- horizon: the row is above 50 (nothing there is ever painted);
- dark: V < 40 (V = the brightest channel);
- hue limit: the hue is outside what the slider can reach (blue 60..150; orange -30..60, i.e. 150..179 and 0..60);
- reachable: none of the three; some slider setting paints it.

With a slider label on the frame, the same pixels at his values: painted their color, lost to the tie rule (inside
both color sectors, the other color won), or not painted. Also the median hue, S, V and RGB of each part, to see what
the color looks like to the camera. Output: results/2026-11-25_color/gates.md + gates.csv. Train frames only.
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402

from barrels import hslabel as hl  # noqa: E402
from barrels import io  # noqa: E402
from barrels import pipeline as pl  # noqa: E402

HORIZON, V_MIN = 50, 40
REACH = {"blue": (60, 150), "orange": (-30, 60)}


def hue_reachable(h: np.ndarray, color: str) -> np.ndarray:
    if color == "blue":
        return (h >= 60) & (h <= 150)
    return (h <= 60) | (h >= 150)


def main() -> int:
    stems = cm.train_stems_with_boxes()
    out_dir = cm.RESULTS
    out_dir.mkdir(parents=True, exist_ok=True)
    base = hl.adopted_model()
    rows = []
    for stem in stems:
        key = cm.condition_of(stem)
        klass = cm.class_of(key)
        if klass == "excluded":
            continue
        bgr, lab = cm.load(stem)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        H, S, V = (hsv[..., i].astype(int) for i in range(3))
        rgb = bgr[..., ::-1].astype(int)
        yy = np.arange(bgr.shape[0])[:, None] * np.ones((1, bgr.shape[1]), int)
        label_mask = None
        if io.hs_path(stem).exists():
            thr = io.load_hs(stem, check_image=False)
            label_mask, info = pl.segment(pl.Frame.from_image(bgr), hl.model_from_thresholds(base, thr))
            # tie: pixels inside both sectors at his values
            m = hl.model_from_thresholds(base, thr)
            fr = pl.Frame.from_image(bgr)
            from barrels import boxfit as bf
            in_o = bf.in_box(fr.hs(pl.HUE_SHIFT[io.ORANGE]), m.boxes[io.ORANGE])
            in_b = bf.in_box(fr.hs(pl.HUE_SHIFT[io.BLUE]), m.boxes[io.BLUE])
        for i, b in enumerate(lab.get("barrels", [])):
            flags = set(b.get("flags", []))
            if flags & {"occluded", "truncated"}:
                continue
            reg = cm.expected_regions(b, bgr.shape)
            for part, m_ in reg.items():
                color = b["color"] if part == "body" else cm.OTHER_COLOR[b["color"]]
                sel = m_
                n = int(sel.sum())
                if n == 0:
                    continue
                above = sel & (yy < HORIZON)
                dark = sel & ~above & (V < V_MIN)
                hue_out = sel & ~above & ~dark & ~hue_reachable(np.where(H > 150, H - 180, H) if color == "orange" else H, color)
                reach = sel & ~above & ~dark & ~hue_out
                r = {"stem": stem, "condition": key, "class": klass, "place": cm.place_of(key), "light": cm.light_of(key),
                     "box": i + 1, "barrel": b["color"], "part": part, "color": color, "n": n,
                     "horizon": int(above.sum()), "dark": int(dark.sum()), "hue_out": int(hue_out.sum()), "reachable": int(reach.sum()),
                     "h_med": float(np.median(H[sel])), "s_med": float(np.median(S[sel])), "v_med": float(np.median(V[sel])),
                     "r_med": float(np.median(rgb[..., 0][sel])), "g_med": float(np.median(rgb[..., 1][sel])), "b_med": float(np.median(rgb[..., 2][sel])),
                     "s_reach_med": float(np.median(S[reach])) if reach.any() else float("nan")}
                if label_mask is not None:
                    cid = io.ORANGE if color == "orange" else io.BLUE
                    oid = io.BLUE if color == "orange" else io.ORANGE
                    in_own = in_o if color == "orange" else in_b
                    in_oth = in_b if color == "orange" else in_o
                    r["label_painted"] = int((sel & (label_mask == cid)).sum())
                    r["label_tie_lost"] = int((sel & (label_mask == oid) & in_own & in_oth).sum())
                    r["label_other"] = int((sel & (label_mask == oid)).sum())
                rows.append(r)
    keys = sorted({k for r in rows for k in r}, key=lambda k: list(rows[0]).index(k) if k in rows[0] else 99)
    with open(out_dir / "gates.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)

    # per condition and part, pixel-weighted shares
    agg = defaultdict(lambda: defaultdict(float))
    for r in rows:
        k = (r["condition"], r["color"], r["part"])
        a = agg[k]
        for f in ("n", "horizon", "dark", "hue_out", "reachable"):
            a[f] += r[f]
        if "label_painted" in r:
            a["ln"] += r["n"]
            for f in ("label_painted", "label_tie_lost", "label_other"):
                a[f] += r[f]
        a.setdefault("hs", []).append((r["h_med"], r["s_med"], r["v_med"], r["r_med"], r["g_med"], r["b_med"]))
        a["barrels"] += 1
    # warm lights first
    def order(k):
        light = k[0].split("_")[0]
        warm = 0 if "warm" in light else 1 if "mid" in light else 2 if light.startswith("both") else 3
        return (cm.class_of(k[0]) != "ordinary", warm, k[0], k[1], k[2])
    lines = ["# Which barrel pixels no slider setting can paint (2026-11-25, step 1)", "",
             "`python barrels/experiments/2026-11-25_color/gates.py`. Train frames only; free-standing barrels (no `occluded` / "
             "`truncated` flag). Body = core columns, rows 15-30 % and 70-85 % of the box height from the bottom; stripe = rows "
             "42-58 % (the other color). Each pixel is put in the first gate that blocks it: **horizon** (row < 50), **dark** "
             "(V < 40), **hue limit** (outside the slider's reach: blue 60-150, orange 150-179 and 0-60); **reachable** = some "
             "setting paints it. With a slider label: at his values, the share **painted**, **lost to the tie** (inside both "
             "sectors, the other color won). Medians are of the per-barrel medians (OpenCV H 0-179, S and V 0-255, RGB).", "",
             "| condition | class | color (part) | barrels | px | horizon % | dark % | hue limit % | reachable % | his label: painted % | tie lost % | median H / S / V | median RGB |",
             "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|"]
    for k in sorted(agg, key=order):
        a = agg[k]
        n = a["n"]
        med = np.median(np.array(a["hs"]), 0)
        lp = f"{100 * a['label_painted'] / a['ln']:.0f}" if a.get("ln") else "-"
        lt = f"{100 * a['label_tie_lost'] / a['ln']:.1f}" if a.get("ln") else "-"
        lines.append(f"| {k[0]} | {cm.class_of(k[0])} | {k[1]} ({k[2]}) | {int(a['barrels'])} | {int(n)} | {100 * a['horizon'] / n:.1f} | "
                     f"{100 * a['dark'] / n:.1f} | {100 * a['hue_out'] / n:.1f} | {100 * a['reachable'] / n:.0f} | {lp} | {lt} | "
                     f"{med[0]:.0f} / {med[1]:.0f} / {med[2]:.0f} | {med[3]:.0f}, {med[4]:.0f}, {med[5]:.0f} |")
    (out_dir / "gates.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
