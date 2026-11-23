#!/usr/bin/env python3
"""Why: the reason log of one train frame (segmented as the report does), every blob and step-1 piece, every box.

    python barrels/experiments/2026-11-23_closeup_shape/why.py <stem> [--cfg start]
"""
from __future__ import annotations

import argparse

import census as CE
import closeup as K
from barrels import detector as det, io


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stem")
    ap.add_argument("--cfg", default="start")
    a = ap.parse_args(argv)
    from barrels import report as rp
    key = rp.set_key(a.stem)
    label = rp.set_label(key, [key])
    for lab, stem, frame, mask in CE.masks([label if label in ("HOME", "CAMPUS") else key]):
        if stem != a.stem:
            continue
        cfg = K.ARMS[a.cfg]
        log: list = []
        out = det.detect(mask, cfg, CE.CAM, log)
        for b in det.find_blobs(mask, cfg):
            if b.width > 30:
                print("blob", b.bbox, "pieces", [p.bbox for p in det.split_blob(b, mask, CE.CAM, cfg)],
                      "W", round(det.expected_width_px(b.bbox, CE.CAM, mask.shape[0]), 1))
        for e in log:
            bb = e.get("bbox")
            if bb is not None and (bb[2] - bb[0]) > 30:
                print(e)
        for b in out:
            print("BOX", b.color, b.bbox, b.source, sorted(b.flags))
        print("labels", [(g["color"], g["bbox"], g.get("flags")) for g in io.load_boxes(stem)["barrels"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
