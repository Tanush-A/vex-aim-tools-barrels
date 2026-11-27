#!/usr/bin/env python3
"""EXPLORATION (listed in PREREG.md): candidate threshold proposals for the slider-labelled bathroom frames, with the
full hue range, from each frame and its boxes; one picture per frame to LOOK at.

Per frame (core_01, clutter_01, occl_02 of the four bathroom conditions; train frames): the hand label that is saved,
the net setting of the frame (``placecal.net_setting``, outside weights 1 and 0.25), the net setting of the whole
condition (all its frames with barrels pooled), and the middle-of-the-ranges setting (``placecal.mid_setting``). For
each: what today's detector finds on that frame with it. The picture (``hs_slider.render_grid``) shows the paint.

    PYTHONPATH=barrels/src python barrels/experiments/2026-11-26_place_ceiling/explore/bath_props.py OUT_DIR [surface]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2

BARRELS = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BARRELS / "tools"))
import hs_slider as tool  # noqa: E402

from barrels import counting as ct, hslabel as hl, hsrange as hx, io, judge as jg, placecal as pc  # noqa: E402

SCENES = ("core_01", "clutter_01", "occl_02")


def main() -> None:
    out_dir = Path(sys.argv[1])
    surface = sys.argv[2] if len(sys.argv) > 2 else "bathtile"
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = jg.train_frames()
    stems = sorted(s for s in frames["ordinary"] if ct.condition_of(s).endswith("_" + surface))
    jg.require_train(stems)
    base = hl.adopted_model()
    adopted = hl.thresholds_from_model(base)
    record = {}
    for cond, ss in sorted(ct.group_stems(stems, "condition").items()):
        loaded = {s: (jg.load_frame(s), io.load_boxes(s, check_image=False)) for s in ss}
        pooled = pc.pooled_net_setting([(f, lab["barrels"]) for f, lab in loaded.values() if lab["barrels"]], base, adopted)
        print(f"\n=== {cond}: pooled net setting {hl.describe(hx.nested(pooled))}")
        for s in ss:
            if not any(s.endswith("_" + sc) for sc in SCENES):
                continue
            frame, label = loaded[s]
            fe = hx.FrameEval(frame.bgr, label, base, stem=s)
            settings = {}
            if io.hs_path(s).exists():
                settings["saved (hand)"] = hx.flat(io.load_hs(s, check_image=False))
            settings["net w=1"] = pc.net_setting(frame, label["barrels"], base, adopted, 1.0)
            settings["net w=0.25"] = pc.net_setting(frame, label["barrels"], base, adopted, 0.25)
            settings["pooled net w=1"] = pooled
            m = pc.mid_setting(fe, adopted)
            settings["mid"] = m.thresholds
            print(f"  {s}  ({len(label['barrels'])} boxes; mid from: {m.source})")
            rec = {}
            for name, t in settings.items():
                o = fe.evaluate(t)
                core = ", ".join(f"{c} {100 * o.core[c]:.0f} %" for c in ("orange", "blue") if o.core[c] == o.core[c])
                print(f"     {name:16s} {hl.describe(hx.nested(t)):60s} found {len(o.found)}/{len(fe.boxes)} false {o.n_false}  cores painted: {core}  "
                      f"outside px: orange {o.out['orange']}, blue {o.out['blue']}")
                rec[name] = {"thresholds": t, "found": len(o.found), "false": o.n_false, "out": o.out}
            record[s] = rec
            pic = tool.render_grid(frame.bgr.copy(), label["barrels"], base, [(n, hx.nested(t)) for n, t in settings.items()])
            cv2.imwrite(str(out_dir / f"{s}.jpg"), pic, [cv2.IMWRITE_JPEG_QUALITY, 80])
    (out_dir / "bath_props.json").write_text(json.dumps(record, indent=1) + "\n")


if __name__ == "__main__":
    main()
