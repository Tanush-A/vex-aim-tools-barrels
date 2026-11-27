"""Group 3, report only: what the contrast finder sees on the very dark ottoman (lamp mid 3, an extreme condition)
against the same arrangements under the mid lamp at 6 (ordinary). Never judged.

Per labelled upright barrel, from its hand box and the geometry of its bottom row (its top row when the frame cuts the bottom): the brightest channel V of the body
(the wall above the stripe) and of the stripe, the share of their pixels under the contrast stage's floor (V 25) and the
color step's gate (V 40), and the red-against-blue difference between body and stripe, log((R + o) / (B + o)), for
offsets o = 2, 8 (today), 16, with the pixel noise of the body band in the same channel: the signal the sandwich reads,
and whether it stands above the noise. Then the finder itself at a few report-only settings (lower brightness floor,
smaller offset): candidates on a barrel's stripe and on nothing.

    python barrels/experiments/2026-11-27_contrast_gaps/dark.py
"""
from __future__ import annotations

import math
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gaps as gp  # noqa: E402

from barrels import contrast as cn  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import judge as jg  # noqa: E402

OUT = gp.BARRELS / "results" / "2026-11-27_contrast_gaps"
SCENES = ("core_01", "edge_01", "touch_01", "clutter_01", "close_01", "occl_02")
LIGHTS = ("lampmid3", "lampmid6")
OFFSETS = (2.0, 8.0, 16.0)


def regions(bbox, cam=gp.CAM):
    x0, y0, x1, y1 = bbox
    if y1 >= 479:                                   # cut by the frame bottom: the distance from the top row instead
        d = cam._d_axis_from_point_row(y0 + 0.5, geo.BARREL_HEIGHT_MM, geo._END_R)
    else:
        d = cam._d_axis_from_point_row(y1 - 0.5, 0.0, -geo._END_R)
    if not math.isfinite(d) or d <= 0:
        return None
    r = cam.barrel_rows(d)
    w = x1 - x0
    cx0, cx1 = int(x0 + 0.2 * w), int(x1 - 0.2 * w)
    hs = r.stripe_bottom - r.stripe_top
    s = (int(round(r.stripe_top + 0.2 * hs)), int(round(r.stripe_bottom - 0.2 * hs)))
    u = (int(round(max(y0 + 0.25 * (r.stripe_top - y0), r.stripe_top - 1.15 * hs))), int(round(r.stripe_top - 0.25 * hs)))
    if s[1] <= s[0] or u[1] <= u[0] or cx1 <= cx0 or s[1] > 480:
        return None
    return (cx0, cx1), s, u


def chan(px, o):
    px = px.astype(np.float64)
    return np.log((px[:, 0] + o) / (px[:, 2] + o))


def main():
    lines = ["# Group 3 (report only): the very dark ottoman", "",
             "Per labelled barrel (not tipped, stripe inside the frame): V = the brightest channel (median); under 25 / 40 = share of the pixels under "
             "the contrast floor / the color gate; diff = median red-against-blue of the body minus the stripe's, at offset o; noise = the spread "
             "(median absolute deviation x 1.48) of the body band in the same channel; z = diff / noise.", "",
             "| frame | color | body V | stripe V | body under 25 / 40 | stripe under 25 / 40 | " + " | ".join(f"diff o={o:g} (z)" for o in OFFSETS) + " |",
             "|---|---|---|---|---|---|" + "---|" * len(OFFSETS)]
    summ = {L: [] for L in LIGHTS}
    for L in LIGHTS:
        for sc in SCENES:
            stem = f"4A8B_{L}_ottoman_{sc}"
            try:
                f = jg.load_frame(stem)
            except Exception as e:  # noqa: BLE001
                lines.append(f"| {stem} | not loaded: {e} |")
                continue
            gts, _ = ct.load_gts([stem])
            for g in gts.get(stem, []):
                reg = regions(g.bbox)
                if reg is None:
                    continue
                (cx0, cx1), s, u = reg
                body = f.rgb[u[0]:u[1], cx0:cx1].reshape(-1, 3)
                stripe = f.rgb[s[0]:s[1], cx0:cx1].reshape(-1, 3)
                vb, vs = body.max(1), stripe.max(1)
                cells = []
                zs = []
                for o in OFFSETS:
                    cb, cs = chan(body, o), chan(stripe, o)
                    diff = float(np.median(cb) - np.median(cs))
                    noise = float(1.48 * np.median(np.abs(cb - np.median(cb)))) or 1e-6
                    cells.append(f"{diff:+.2f} ({abs(diff) / noise:.1f})")
                    zs.append(abs(diff) / noise)
                summ[L].append((float(np.median(vb)), float(np.median(vs)), zs, abs(float(np.median(chan(body, 8)) - np.median(chan(stripe, 8))))))
                lines.append(f"| {stem[5:]} | {'orange' if g.color == 1 else 'blue'} | {np.median(vb):.0f} | {np.median(vs):.0f} | "
                             f"{(vb < 25).mean():.2f} / {(vb < 40).mean():.2f} | {(vs < 25).mean():.2f} / {(vs < 40).mean():.2f} | " + " | ".join(cells) + " |")
    lines += ["", "| light | barrels | median body V | median stripe V | median diff at o=8 | " + " | ".join(f"median z o={o:g}" for o in OFFSETS) + " |",
              "|---|---|---|---|---|" + "---|" * len(OFFSETS)]
    for L, rr in summ.items():
        if rr:
            lines.append(f"| {L} | {len(rr)} | {np.median([r[0] for r in rr]):.0f} | {np.median([r[1] for r in rr]):.0f} | {np.median([r[3] for r in rr]):.2f} | "
                         + " | ".join(f"{np.median([r[2][i] for r in rr]):.1f}" for i in range(len(OFFSETS))) + " |")
    # the finder at report-only settings on the dark frames
    lines += ["", "## The finder on the lamp-mid-3 ottoman frames at report-only settings", "",
              "Candidates whose stripe point is on a labelled barrel's stripe (middle 70 % of columns, rows 0.35-0.80 of the box) / on nothing. "
              "Today: offset 8, brightness floor 25, margin 0.5, strength 1.15.", "",
              "| setting | barrels with a candidate on their stripe | candidates on nothing |", "|---|---|---|"]
    settings = {"today": cn.ContrastConfig(),
                "floor V 10": replace(cn.ContrastConfig(), v_min=10),
                "offset 2": replace(cn.ContrastConfig(), offset=2.0),
                "offset 2, floor V 10": replace(cn.ContrastConfig(), offset=2.0, v_min=10),
                "floor V 10, margin 0.3, strength 0.8": replace(cn.ContrastConfig(), v_min=10, margin=0.3, strength_min=0.8)}
    stems = [s for s in jg.train_frames()["extreme"] if "lampmid3_ottoman" in s]
    gts, _ = ct.load_gts(stems)
    for name, cfg in settings.items():
        on, off, n = 0, 0, 0
        for s in stems:
            f = jg.load_frame(s)
            cands = cn.find(f.rgb, gp.CAM, cfg, rb=cn.row_bands(gp.CAM, f.rgb.shape[0], cfg))
            gg = [g for g in gts.get(s, []) if "no_stripe" not in getattr(g, "flags", ())]
            n += len(gg)
            hit = set()
            for c in cands:
                k = [i for i, g in enumerate(gg) if g.bbox[0] + 0.15 * (g.bbox[2] - g.bbox[0]) <= c.x < g.bbox[2] - 0.15 * (g.bbox[2] - g.bbox[0])
                     and g.bbox[1] + 0.35 * (g.bbox[3] - g.bbox[1]) <= c.row < g.bbox[1] + 0.80 * (g.bbox[3] - g.bbox[1])]
                if k:
                    hit.update(k)
                else:
                    off += 1
            on += len(hit)
        lines.append(f"| {name} | {on} of {n} | {off} |")
    (OUT / "dark.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
