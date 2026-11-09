#!/usr/bin/env python3
"""The four campus recordings (2026-11-07, `tm rec`) replayed offline: the per-frame detector vs the multi-frame view.

For every frame of each clip (data/recordings/2026-11-07_campus/<clip>/frame_NNN.png, ≈ 6 frames a second): the
detector as it stands (BarrelDetectorHook.default()) gives the frame's own barrels ("raw"); `tracker.Tracker`
(TrackConfig(): shown after 3 of the last 4 frames, kept through one miss, forgotten after 4) gives what the live
program BarrelTracker would show. Reported per clip:

  * raw boxes per frame (orange / blue) and how often the count changes from one frame to the next ("flicker");
  * raw blips: a raw box matched (same color, IoU >= 0.3) to no raw box in the frame before or after — the
    one-frame boxes Tanush saw; and how many of them reached the screen through the tracker (should be 0);
  * shown boxes per frame and the frames the shown count changes; lag = frames from a barrel's first raw box to its
    first shown box (new tracks only);
  * a timeline image (raw count above, shown count below, one column per frame) and a strip of 8 frames with the
    raw boxes in white and the shown ones in yellow/green.

Counts only: the recordings have no labels and the clips were shot to try the persistence rule, not to score the
detector. Results: results/2026-11-07_rec_replay/ (summary.md + per_frame.csv committed; images gitignored).

    python barrels/experiments/2026-11-07_rec_replay/run.py                      # the detector on `barrels` (frozen v1, old finder)
    python barrels/experiments/2026-11-07_rec_replay/run.py --front hs --out 2026-11-08_rec_replay_hs
        # 2026-11-08: the hs color model (fit on the 16 home train masks with the config given by --hs, default
        # the per-class candidate) and the hardened detector; results in results/<--out>/
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from barrels import cv as bcv, detector as det, io, pipeline as pl, splits, tracker as tr, worldmap_bridge as wb  # noqa: E402
from barrels.io import BLUE, ORANGE, PKG_ROOT  # noqa: E402

REC = PKG_ROOT / "data" / "recordings" / "2026-11-07_campus"
OUT = PKG_ROOT / "results" / "2026-11-07_rec_replay"


def hs_hook(spec: str) -> wb.BarrelDetectorHook:
    """A hook running the hs color model fit on the home train masks: spec = 'o5,b15,m4' (S percentiles, hue margin)."""
    kv = dict(x.strip()[0:1] and (x.strip()[0], float(x.strip()[1:])) for x in spec.split(","))
    cfg = pl.Config(color_model="hs", hs_s_pct=(kv["o"], kv["b"]), hs_h_pct=(5, 95), hs_h_margin=kv["m"])
    home = sorted(s for s in splits.load_splits()["train"] if s.startswith("4A8B_window_light"))
    frames = [pl.Frame.from_image(io.load_image(io.find_image(s))) for s in home]
    masks = [io.load_mask(io.mask_path(io.find_image(s))) for s in home]
    return wb.BarrelDetectorHook(model=pl.fit(frames, masks, cfg), det_cfg=det.DetConfig())
CLIPS = {"r1_static": "two barrels at about 15 cm, nothing moves", "r2_pan": "the robot turned slowly by hand, barrels in view",
         "r3_enter_leave": "a barrel slid into the view from the side and out again", "r4_hand_occlusion": "a hand waved across the barrels twice"}


def matched(b, others, iou=0.3) -> bool:
    return any(o.color == b.color and det.box_iou(o.bbox, b.bbox) >= iou for o in others)


def main(argv=None) -> int:
    global OUT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--front", choices=("v1", "hs"), default="v1")
    ap.add_argument("--hs", default="o5,b15,m4", help="hs config: orange S pct, blue S pct, hue margin")
    ap.add_argument("--out", default=None, help="results folder name (default 2026-11-07_rec_replay)")
    args = ap.parse_args(argv)
    if args.out:
        OUT = PKG_ROOT / "results" / args.out
    OUT.mkdir(parents=True, exist_ok=True)
    if args.front == "hs":
        hook = hs_hook(args.hs)
        front = f"hs color model ({args.hs}, fit on the home train masks) + hardened detector DetConfig()"
    else:
        hook = wb.BarrelDetectorHook.default()
        hook.det_cfg = dataclasses.replace(det.DetConfig(), stripe_mode="bands", body_min=0.0, height_max=0.0) if hasattr(det.DetConfig(), "stripe_mode") else det.DetConfig()
        front = "frozen v1 model + the 2026-11-05 detector (as on `barrels`)"
    md = ["# Recordings 2026-11-07 replayed: per-frame detector vs the 3-of-4 view", "",
          f"git {bcv.git_hash()}; front end: {front}; camera boxfit; TrackConfig {tr.TrackConfig().__dict__}.", "",
          "| clip | frames | raw O/B per frame (median, min–max) | raw count changes | raw blips | blips shown | shown O/B per frame (median, min–max) | shown count changes | lag frames (new tracks) |",
          "|---|---|---|---|---|---|---|---|---|"]
    rows = []
    for clip, what in CLIPS.items():
        folder = REC / clip
        if not folder.exists():
            md.append(f"| {clip} | missing | | | | | | | |"); continue
        frames = json.loads((folder / "frames.json").read_text())["frames"]
        tracker = tr.Tracker()
        raws, showns, imgs = [], [], []
        for fr in frames:
            bgr = cv2.imread(str(folder / fr["file"]))
            rgb = np.ascontiguousarray(bgr[..., ::-1])
            raw = hook.on_image(rgb)
            shown = tracker.update(raw)
            raws.append(raw); showns.append(shown); imgs.append(bgr)
        n = len(frames)
        raw_o = [sum(b.color == ORANGE for b in r) for r in raws]; raw_b = [sum(b.color == BLUE for b in r) for r in raws]
        sh_o = [sum(b.color == ORANGE for b in s) for s in showns]; sh_b = [sum(b.color == BLUE for b in s) for s in showns]
        raw_changes = sum(1 for i in range(1, n) if (raw_o[i], raw_b[i]) != (raw_o[i - 1], raw_b[i - 1]))
        sh_changes = sum(1 for i in range(1, n) if (sh_o[i], sh_b[i]) != (sh_o[i - 1], sh_b[i - 1]))
        blips, blips_shown = 0, 0
        for i in range(n):
            prev = raws[i - 1] if i else []; nxt = raws[i + 1] if i + 1 < n else []
            for b in raws[i]:
                if not matched(b, prev) and not matched(b, nxt):
                    blips += 1
                    if matched(b, showns[i], iou=0.5):
                        blips_shown += 1
        # lag: for each raw box that starts a run (no match in the previous frame) and persists >= 3 of the next 4 frames,
        # frames until a shown box overlaps it
        lags = []
        for i in range(n):
            for b in raws[i]:
                if i and matched(b, raws[i - 1]):
                    continue
                run = sum(matched(b, raws[j]) for j in range(i, min(n, i + 4)))
                if run < 3:
                    continue
                lag = next((j - i for j in range(i, n) if matched(b, showns[j], iou=0.3)), None)
                if lag is not None:
                    lags.append(lag)
        def rng(v): return f"{int(np.median(v))} ({min(v)}–{max(v)})"
        md.append(f"| {clip} | {n} | {rng(raw_o)} / {rng(raw_b)} | {raw_changes} | {blips} | {blips_shown} | {rng(sh_o)} / {rng(sh_b)} | {sh_changes} | "
                  f"{', '.join(map(str, lags)) if lags else '–'} |")
        for i, fr in enumerate(frames):
            rows.append(dict(clip=clip, frame=fr["file"], t=fr["t"], raw_orange=raw_o[i], raw_blue=raw_b[i], shown_orange=sh_o[i], shown_blue=sh_b[i]))
        # timeline: one column per frame, raw count (top) and shown count (bottom), 0..4
        W = max(4, 640 // n); tl = np.full((2 * 60 + 30, W * n, 3), 255, np.uint8)
        for i in range(n):
            for k, (o, b) in enumerate(((raw_o[i], raw_b[i]), (sh_o[i], sh_b[i]))):
                y0 = k * 75
                cv2.rectangle(tl, (i * W, y0 + 60 - 12 * o), ((i + 1) * W - 1, y0 + 60), (0, 128, 255), -1)
                cv2.rectangle(tl, (i * W, y0 + 60 - 12 * (o + b)), ((i + 1) * W - 1, y0 + 60 - 12 * o), (255, 100, 0), -1)
        cv2.putText(tl, f"{clip}: raw boxes per frame (top), shown (bottom); orange / blue", (4, 148), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
        cv2.imwrite(str(OUT / f"{clip}_timeline.png"), tl)
        pick = np.linspace(0, n - 1, 8).astype(int)
        strip = []
        for i in pick:
            im = imgs[i].copy()
            for b in raws[i]:
                x0, y0, x1, y1 = b.bbox; cv2.rectangle(im, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
            im = det.draw(im, showns[i])
            cv2.putText(im, f"{i}  t={frames[i]['t']:.1f}s", (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)
            cv2.putText(im, f"{i}  t={frames[i]['t']:.1f}s", (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            strip.append(cv2.resize(im, (320, 240)))
        cv2.imwrite(str(OUT / f"{clip}_strip.png"), np.vstack([np.hstack(strip[:4]), np.hstack(strip[4:])]))
    md += ["", "Clips: " + "; ".join(f"{k} = {v}" for k, v in CLIPS.items()) + ".",
           "", "Raw = the frame's own answer (what BarrelViewer shows); shown = what BarrelTracker shows. White boxes in the strips are raw, colored ones shown."]
    (OUT / "summary.md").write_text("\n".join(md))
    with (OUT / "per_frame.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump({"git": bcv.git_hash(), "front": front, "track_cfg": tr.TrackConfig().__dict__, "det_cfg": hook.det_cfg.to_dict(), "seg_cfg": hook.model.cfg.to_dict(), "clips": CLIPS}, (OUT / "config.json").open("w"), indent=1)
    print("\n".join(md)); print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
