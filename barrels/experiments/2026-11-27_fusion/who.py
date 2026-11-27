#!/usr/bin/env python3
"""Which methods voted for each box F3r adds to F1 (held out; ordinary and extreme frames).

    PYTHONPATH=barrels/src python barrels/experiments/2026-11-27_fusion/who.py

Writes results/2026-11-27_fusion/who_F3r.md: per added box, its frame, its state (counting.classify_frame) and the
methods in its cluster (+ "contrast" when the contrast response voted).
"""
from __future__ import annotations

import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fuse  # noqa: E402
import methods as M  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import fusion as fu  # noqa: E402
from barrels import judge as jg  # noqa: E402


def main():
    frames = jg.train_frames()
    F = fuse.fitter()
    d = jg.leave_one_place_out(F.fit("F3r"), frames[cnd.ORDINARY])
    stems = frames[cnd.ORDINARY] + frames[cnd.EXTREME]
    rows, tally = [], collections.Counter()
    for s in stems:
        boxes = d(s, None)
        place = ct.place_of(s)
        fitted = d.fitted[place]
        rec, b = fuse.record(s), M.bundle(place)
        ch = F.chosen["F3r"][place]["choice"]
        ck = fu.MILD if "s0.35" in ch else fu.STRONG if "s0.4" in ch else fu.OFF
        kept = fuse.f1(rec, b, ck)
        added = [x for x in fuse.f3r(rec, b, (ck, None if ch.endswith("off") else int(ch.split("k ")[1])))
                 if not any(x is y for y in kept)]
        if not added:
            continue
        fc = ct.classify_frame(s, boxes, F.truth.gts[s], F.truth.clean[s])
        state = {tuple(bb.bbox): st for bb, st in zip(boxes, fc.boxes)}
        props = {m: [p for p in fu.proposals(v, kept) if not any(fu.is_on(p, r) for r in fuse.removed(rec, b, ck))]
                 for m, v in fuse.others(rec, b).items()}
        cl = fu.clusters(props, fuse.ORDER)
        vote = fuse.contrast_vote(rec)
        for x in added:
            c = next(c for c in cl if c[0] is x)
            who = "+".join(sorted({i.method for i in c})) + ("+contrast" if vote(x) else "")
            st = state.get(tuple(x.bbox), "?")
            kind = "judged" if s in frames[cnd.ORDINARY] else "report only"
            rows.append(f"| {s} | {kind} | {x.bbox} | {st} | {who} |")
            tally[(kind, st, who)] += 1
    md = ["# F3r: who voted for each added box (held out)", "", "| frame | | box | state | voters |", "|---|---|---|---|---|"] + rows
    md += ["", "| kind | state | voters | boxes |", "|---|---|---|---|"] + [f"| {k} | {st} | {w} | {n} |" for (k, st, w), n in sorted(tally.items())]
    (fuse.OUT / "who_F3r.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
