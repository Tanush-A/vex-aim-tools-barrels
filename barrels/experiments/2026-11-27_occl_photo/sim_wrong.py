#!/usr/bin/env python3
"""The "other boxes" of the simulated side cuts (sim.py), for every arm: is each one on the hidden barrel (a box that
touches it but fails the strict rule: wrong side or bottom off) or on nothing? Writes results/.../sim_wrong.md."""
from __future__ import annotations

import collections

import sim
from lib import OUT, ct, det, dtp
import lib as L


def main() -> int:
    srcs = sim.sources()
    cfgs = {a: det.DetConfig(**kv) for a, kv in sim.ARMS.items()}
    agg = collections.Counter()
    for src, rgb in srcs:
        for kind in ("edge", "slant"):
            for amount in sim.AMOUNTS:
                for side in "LR":
                    for lean in ((1, -1) if kind == "slant" else (1,)):
                        for short in (0, sim.SHORT_PX):
                            sc = sim.oc.make_scene(src, kind, amount, side, cam=L.CAM, lean=lean)
                            if short:
                                sim.shorten(sc.mask, src, kind, amount, side, lean, short)
                            for tall in (True, False):
                                photo = sim.photo_of(rgb, src, kind, amount, side, lean, tall)
                                g = dtp.Barrel(color=src.color, bbox=tuple(src.bbox), source="gt")
                                for a, cfg in cfgs.items():
                                    preds = det.detect(sc.mask, cfg, L.CAM, photo=photo if a != "off" else None)
                                    fc = ct.classify_frame("scene", preds, [g], True)
                                    for s in fc.boxes:
                                        if s != ct.FOUND:
                                            agg[(a, amount, s)] += 1
    lines = ["# Simulated side cuts: the boxes that are not a strict hit", "", "| arm | amount | box off (on the barrel, fails strict) | second | wrong color | on nothing |", "|---|---|---|---|---|---|"]
    for a in sim.ARMS:
        for amount in sim.AMOUNTS:
            lines.append(f"| `{a}` | {int(amount * 100)} % | {agg[(a, amount, ct.OFF)]} | {agg[(a, amount, ct.SECOND)]} | {agg[(a, amount, ct.WRONG)]} | {agg[(a, amount, ct.NOTHING)]} |")
    (OUT / "sim_wrong.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
