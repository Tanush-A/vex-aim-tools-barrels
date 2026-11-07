#!/usr/bin/env python3
"""Diagnostic for the first live run (2026-11-06): Tanush's screenshots of the live window, no raw frames yet.

screens/: three "both" views (segmentation tint + boxes) with the back of Tanush's laptop as a plain backdrop (board_a/b/c — "board" in the names means the laptop lid), one raw
frame of the hand-and-laptop scene (hand_raw) and its "seg" view (hand_seg). The screenshots are hand-cropped and
scaled, so each is resized to 640x480 — an approximation, not the frame the robot saw.

For the board views the class mask is rebuilt from the tint (orange tint -> orange, blue tint -> blue), and on
that mask the script lists every band the stripe finder considered and why it was kept or dropped (it mirrors
detector.find_stripes step by step), then what detector.detect returns. For the raw hand frame it runs the real
live path (BarrelDetectorHook.view). Results: results/2026-11-06_live_first_run/ (summary.md committed; the
overlays are gitignored). Verdict: EXPERIMENTS.md 2026-11-06.

    python barrels/experiments/2026-11-06_live_first_run/run.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import detector as det, geometry as geo, pipeline as pl, viz, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

OUT = PKG_ROOT / "results" / "2026-11-06_live_first_run"
CAM = geo.AIM_4A8B6118_BOXFIT
CFG = det.DetConfig()
# the "both" view is 0.5*image + 0.5*tint (viz.overlay): tinted orange ends up at hue 5-25, tinted blue at 98-128 (OpenCV 0-180)
TINT = {"orange": ((5, 25), 110, 110), "blue": ((98, 128), 110, 90)}


def load_640(path: Path) -> np.ndarray:
    return cv2.resize(cv2.imread(str(path), cv2.IMREAD_COLOR), (640, 640 * 3 // 4), interpolation=cv2.INTER_AREA)


def mask_from_tint(bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h, s, v = (hsv[..., i].astype(int) for i in range(3))
    mask = np.zeros(bgr.shape[:2], np.uint8)
    (lo, hi), smin, vmin = TINT["orange"]
    mask[(h >= lo) & (h <= hi) & (s >= smin) & (v >= vmin)] = ORANGE
    (lo, hi), smin, vmin = TINT["blue"]
    mask[(h >= lo) & (h <= hi) & (s >= smin) & (v >= vmin)] = BLUE
    return mask


def band_report(mask: np.ndarray, lines: list[str]) -> None:
    """Every band the stripe finder looks at, and the verdict — the same tests as detector.find_stripes."""
    for body in (ORANGE, BLUE):
        other, name = (BLUE, "orange") if body == ORANGE else (ORANGE, "blue")
        bm = (mask == body).astype(np.uint8)
        k = CFG.close_px if CFG.close_px % 2 else CFG.close_px + 1
        bm = cv2.morphologyEx(bm, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8)).astype(bool)
        above = np.maximum.accumulate(bm, axis=0)
        below = np.maximum.accumulate(bm[::-1], axis=0)[::-1]
        band = (~bm) & above & below
        n, lab, st, _ = cv2.connectedComponentsWithStats(band.astype(np.uint8), connectivity=8)
        for i in range(1, n):
            x, y, bw, bh, area = (int(t) for t in st[i])
            if area < 200:
                continue
            sel = lab == i
            n_other, n_dark = int((mask[sel] == other).sum()), int((mask[sel] == 0).sum())
            g = det._stripe_geometry(CAM, y + bh / 2)
            why = []
            if g is None:
                why.append("row impossible"); W = Hs = float("nan")
            else:
                _, rows = g
                W, Hs = rows.width_px, rows.stripe_bottom - rows.stripe_top
                if W < CFG.min_width_px or Hs < CFG.min_stripe_px:
                    why.append("too far")
                if n_other + n_dark < 0.5 * area:
                    why.append("not a band (mostly body/ignore)")
                ys_other = np.where(sel & (mask == other))[0]
                core_h = (np.percentile(ys_other, 90) - np.percentile(ys_other, 10) + 1) if len(ys_other) >= 0.25 * area else bh
                if not (CFG.stripe_h_min * Hs <= core_h <= CFG.stripe_h_max * Hs):
                    why.append(f"stripe height {core_h:.0f} not in {CFG.stripe_h_min * Hs:.0f}-{CFG.stripe_h_max * Hs:.0f}")
                if bh > CFG.band_h_max * Hs:
                    why.append(f"band {bh} taller than {CFG.band_h_max * Hs:.0f}")
                if bw < CFG.stripe_w_min * W:
                    why.append(f"narrower than {CFG.stripe_w_min * W:.0f}")
                if bw < core_h:
                    why.append("taller than wide")
            verdict = "**KEPT → a barrel**" if not why else "dropped: " + "; ".join(why)
            lines.append(f"| {name} | {x}-{x + bw} | {y}-{y + bh} | {bw}×{bh} | {n_other} | {n_dark} | {W:.0f} / {Hs:.0f} | {verdict} |")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=PKG_ROOT).stdout.strip()
    json.dump({"git": git, "cam": "AIM_4A8B6118_BOXFIT", "det_cfg": CFG.to_dict(), "tint": TINT, "note": "masks rebuilt from screenshots; approximate"},
              (OUT / "config.json").open("w"), indent=1)
    md = ["# First live run, 2026-11-06 — what the detector did on Tanush's screenshots (approximate: masks rebuilt from the tint)", "",
          f"git {git}; camera AIM_4A8B6118_BOXFIT; DetConfig defaults. Columns: body color the band sits between; band x, y, size; "
          "pixels of the other barrel color (a real stripe) and unlabeled pixels (shadow) inside it; expected barrel width / stripe height at that row.", ""]
    for name in ("board_a_both", "board_b_both", "board_c_both"):
        bgr = load_640(HERE / "screens" / f"{name}.png")
        mask = mask_from_tint(bgr)
        md += [f"## {name}", "", f"rebuilt mask: {int((mask == ORANGE).sum())} orange px, {int((mask == BLUE).sum())} blue px", "",
               "| body | x | y | w×h | stripe-colored | unlabeled | exp. W / stripe h | verdict |", "|---|---|---|---|---|---|---|---|"]
        band_report(mask, md)
        bars = det.detect(mask, CFG, CAM)
        md += ["", "detect() returns:" if bars else "detect() returns nothing.", ""]
        for b in bars:
            md.append(f"- {b.color_name} x {b.bbox[0]}-{b.bbox[2]} y {b.bbox[1]}-{b.bbox[3]} from {b.source} {sorted(b.flags)} conf {b.confidence:.2f}")
        md.append("")
        cv2.imwrite(str(OUT / f"{name}_recon_mask.png"), viz.overlay(bgr, mask))
        cv2.imwrite(str(OUT / f"{name}_recon_boxes.png"), det.draw(viz.overlay(bgr, mask), bars))
    hook = wb.BarrelDetectorHook.default()
    bgr = load_640(HERE / "screens" / "hand_raw.png")
    rgb = np.ascontiguousarray(bgr[..., ::-1])
    bars = hook.on_image(rgb)
    cv2.imwrite(str(OUT / "hand_raw_live_path.png"), hook.render(rgb, bars, "both")[..., ::-1])
    floor, _ = pl.effective_s_min(pl.Frame.from_image(bgr), hook.model.cfg)     # the per-image saturation floor (from the top rows)
    md += ["## hand_raw (a raw frame, the real live path on the resized screenshot)", "",
           f"per-image saturation floor from the top rows: orange {floor.get(ORANGE)}, blue {floor.get(BLUE)} "
           f"(clamp {hook.model.cfg.s_min_lo}-{hook.model.cfg.s_min_hi}); "
           f"segmentation: {int((hook.last_mask == ORANGE).sum())} orange px, {int((hook.last_mask == BLUE).sum())} blue px; "
           + (f"{len(bars)} barrel(s): " + "; ".join(f"{b.color_name} x {b.bbox[0]}-{b.bbox[2]} y {b.bbox[1]}-{b.bbox[3]} ({b.source})" for b in bars) if bars else "no barrels"), ""]
    (OUT / "summary.md").write_text("\n".join(md))
    print("\n".join(md))
    print(f"\nwrote {OUT}/summary.md (+ overlays)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
