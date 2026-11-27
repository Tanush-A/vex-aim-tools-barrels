#!/usr/bin/env python3
"""Exploration, in-sample, before the plan was written (listed in PREREG.md): what the guards read on candidates
that are on a barrel and on candidates that are on nothing, and which of them ended in a box.

    python barrels/experiments/2026-11-26_contrast/explore_guards.py [--setting mode=add,strength_min=1.0] [--jobs 8]

Every ordinary train frame, one setting WITHOUT guards. For every candidate that was painted: is it on a labelled
barrel's stripe (right color), inside a hand box otherwise, or on nothing; the numbers each guard would look at; and
whether the detector drew a new box around it. Writes results/2026-11-26_contrast/explore_guards.md.
"""
from __future__ import annotations

import argparse
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candidate as cd  # noqa: E402
import common as cm  # noqa: E402

from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

COLOR = {"orange": ORANGE, "blue": BLUE}
COLS = ("share", "strength", "d", "orange_part", "alike_rel", "alike_feat", "above", "below", "left", "right")


def _one(args) -> list[dict]:
    import cv2
    cv2.setNumThreads(1)
    stem, spec = args
    st = cd.setting_from(spec)
    frame = jg.load_frame(stem)
    lab = io.load_boxes(stem, check_image=False)
    fw = cd.FrameWork(frame)
    _, cands = fw.masks(st)
    final = fw.detect(st)
    new = [b for b in final if not any(o.bbox == b.bbox and o.color == b.color for o in fw.base_boxes)] if st.mode == "add" else final
    out = []
    for c in cands:
        if not c.info.get("painted"):
            continue
        i = c.info
        onb = next((b for b in lab["barrels"] if COLOR[b["color"]] == c.color and cm.on_stripe(c, b["bbox"])), None)
        where = "barrel" if onb is not None else "in a box" if any(cm.in_box(c, b["bbox"]) for b in lab["barrels"]) else "nothing"
        got = any(b.color == c.color and b.bbox[0] <= c.x < b.bbox[2] and b.bbox[1] <= c.row < b.bbox[3] for b in new)
        off = i["off"]
        out.append({"stem": stem, "color": "O" if c.color == ORANGE else "B", "x": c.x, "row": c.row, "where": where, "box": got, "empty": not lab["barrels"],
                    "kind": None if onb is None else cm.barrel_kind(stem, onb), "share": c.share, "strength": c.strength, "d": i["d"],
                    "orange_part": i["orange_part"], "alike_rel": i["alike_rel"], "alike_feat": i["alike_feat"],
                    **{k: (float("nan") if off[k] is None else off[k]) for k in ("above", "below", "left", "right")}})
    return out


def line(r: dict) -> str:
    return (f"| {r['stem'].replace('4A8B_', '')} | {r['color']} | {r['x']}, {r['row']} | {r['where']}{' (' + r['kind'] + ')' if r['kind'] else ''} | {'yes' if r['box'] else 'no'} | "
            + " | ".join(f"{r[k]:.2f}" for k in COLS) + " |")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--setting", default="mode=add,strength_min=1.0")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--name", default="explore_guards")
    a = ap.parse_args()
    stems = cm.frames()["ordinary"]
    with Pool(a.jobs) as pool:
        recs = [r for rs in pool.map(_one, [(s, a.setting) for s in stems], chunksize=2) for r in rs]
    head = "| frame | color | x, row | on | new box | " + " | ".join(COLS) + " |\n|" + "---|" * (5 + len(COLS))
    loose = sorted((r for r in recs if r["where"] != "barrel"), key=lambda r: (not r["box"], r["stem"]))
    on = [r for r in recs if r["where"] == "barrel"]
    L = [f"# Guard values of painted candidates, in-sample ({a.setting}; ordinary train frames; exploration, not a verdict)", "",
         f"{len(on)} painted candidates on a labelled barrel's stripe ({sum(r['box'] for r in on)} ended in a new box); {len(loose)} not on one "
         f"({sum(r['box'] for r in loose)} ended in a new box). Candidates inside a box today's detector already drew are left alone and are not listed.", "",
         "share, strength: the finder's two numbers. d: the feature distance between the body's and the stripe's own colors. orange_part: the red-against-blue "
         "value of the part that should be orange. alike_rel, alike_feat: how much the two body bands differ (red-blue channel, relative; color and brightness, "
         "in units of d). above, below, left, right: how far what is around the predicted box is from the body color, in units of d.", "",
         "## Not on a barrel", "", head] + [line(r) for r in loose] + ["", "## On a barrel", "", head] + [line(r) for r in on]
    cm.OUT.mkdir(parents=True, exist_ok=True)
    (cm.OUT / f"{a.name}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
