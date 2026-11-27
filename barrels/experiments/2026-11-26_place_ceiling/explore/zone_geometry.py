#!/usr/bin/env python3
"""EXPLORATION (listed in PREREG.md): where in a hand-drawn box do the body and the stripe sit?

Home train frames only (the 16 frames that have pixel masks). For every free-standing box: the share of pixels, per
band of the box height (20 bands) in the central half of the box width, that the pixel mask labels as the barrel's
own color, as the other color (the stripe), or as nothing. The answer fixes the zones of ``barrels.placecal``.

    PYTHONPATH=barrels/src python barrels/experiments/2026-11-26_place_ceiling/explore/zone_geometry.py
"""
from __future__ import annotations

import numpy as np

from barrels import io, judge as jg
from barrels.io import BLUE, ORANGE

BANDS = 20


def main() -> None:
    frames = jg.train_frames()
    stems = [s for s in frames["ordinary"] if "_window_light_" in s]
    jg.require_train(stems)
    rows = {"all": [], "tall (>= 50 px)": [], "short (< 50 px)": []}
    n = 0
    for s in sorted(stems):
        img = io.find_image(s)
        mp = io.mask_path(img)
        if not mp.exists():
            continue
        mask = io.load_mask(mp)
        for b in io.load_boxes(s, check_image=False)["barrels"]:
            if any(f in ("occluded", "truncated", "held", "no_stripe") for f in (b.get("flags") or [])):
                continue
            x0, y0, x1, y1 = b["bbox"]
            w, h = x1 - x0, y1 - y0
            own = ORANGE if b["color"] == "orange" else BLUE
            other = BLUE if own == ORANGE else ORANGE
            cx0, cx1 = x0 + w // 4, x1 - w // 4
            prof = np.zeros((BANDS, 3))
            for k in range(BANDS):
                r0, r1 = y0 + int(round(k * h / BANDS)), y0 + int(round((k + 1) * h / BANDS))
                m = mask[r0:max(r1, r0 + 1), cx0:cx1]
                if m.size:
                    prof[k] = [(m == own).mean(), (m == other).mean(), (m == 0).mean()]
            rows["all"].append(prof)
            rows["tall (>= 50 px)" if h >= 50 else "short (< 50 px)"].append(prof)
            n += 1
    print(f"{n} free-standing boxes on the home train frames with masks")
    for name, profs in rows.items():
        if not profs:
            continue
        p = np.mean(profs, 0)
        print(f"\n{name}: {len(profs)} boxes. band of the box height: own color / other color (stripe) / unlabelled")
        for k in range(BANDS):
            print(f"  {100 * k // BANDS:3d}-{100 * (k + 1) // BANDS:3d} %   {p[k, 0]:.2f}  {p[k, 1]:.2f}  {p[k, 2]:.2f}")


if __name__ == "__main__":
    main()
