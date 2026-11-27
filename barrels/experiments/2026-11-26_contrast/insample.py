#!/usr/bin/env python3
"""In-sample views of the contrast experiment, for the record; never a verdict (run after the judged round).

    python barrels/experiments/2026-11-26_contrast/insample.py [--jobs 8]

From the table ``run.py`` built (every setting on every ordinary train frame, no leave one place out):

1. Every setting of the primary family on all eight places: found, boxes that are not on their barrel, boxes on
   empty frames, and what the pass rule would say in-sample.
2. One guard at a time, around the setting the rule picks on all eight places: what switching it costs or buys.

Writes results/2026-11-26_contrast/insample.md.
"""
from __future__ import annotations

import argparse
import dataclasses
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402
import table as tb  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import judge as jg  # noqa: E402

WATCH = ("home_bathtile", "home_ottoman", "abp_gray")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    ordinary = jg.train_frames()[cnd.ORDINARY]
    truth = jg.load_truth(ordinary)
    margins = jg.load_margins()
    table = tb.build_table(ordinary, tb.all_settings(), a.jobs, progress=False)
    base, base_places = tb.tallies(table, tb.FIXED, ordinary, truth.placements)

    def line(st, name: str = "") -> str:
        c, cp = tb.tallies(table, st.key, ordinary, truth.placements)
        v = jg.decide(base, c, {p: (base_places[p], cp[p]) for p in base_places}, margins)
        g = lambda x: "off" if x is None else f"{x:g}"       # noqa: E731
        return (f"| {name or st.mode} | {st.strength_min:g} | {g(st.d_min)} | {g(st.orange_min)} | {g(st.alike_feat)} | {g(st.extent_top)} | "
                f"{c.found_w - base.found_w:+.2f} | {c.found} | {c.extra_w - base.extra_w:+.2f} | {c.extra} | {c.clean_empty} | {c.cluttered_empty_w:.2f} | "
                + " / ".join(f"{cp[p].found_w:.1f}" for p in WATCH) + f" | {v.result} |")
    head = ("| | strength floor | own colors apart | orange part reddish | one body | extent | found, placements | found, per frame | boxes not on their barrel | per frame | "
            "on clean empty frames | on empty frames with clutter | bathroom / ottoman / gray table | in-sample |\n|" + "---|" * 14)
    pick, _ = tb.choose(table, tb.FAMILIES["C1_add_guards"], ordinary, truth.placements, margins)
    L = ["# In-sample views (all eight places, no leave one place out; for the record, never a verdict)", "",
         f"`python barrels/experiments/2026-11-26_contrast/insample.py`. Today: found {base.found_w:.1f} of {base.placements} placements ({base.found} of {base.barrels} per frame), "
         f"boxes not on their barrel {base.extra_w:.2f} ({base.extra} per frame); bathroom / ottoman / gray table "
         + " / ".join(f"{base_places[p].found_w:.1f}" for p in WATCH) + " of 15 / 15 / 16. Differences are from today.", "",
         "## One guard at a time, around the setting the rule picks on all eight places", "", head, line(pick, "the pick")]
    for label, kw in (("no absolute check", {"orange_min": None}), ("no extent guard", {"extent_top": None, "extent_bottom": None}),
                      ("plus own colors apart", {"d_min": tb.D_MIN}), ("plus one body", {"alike_feat": tb.ALIKE_FEAT}),
                      ("strength floor 1.0", {"strength_min": 1.0}), ("strength floor 1.3", {"strength_min": 1.3}),
                      ("no guard at all", {"orange_min": None, "extent_top": None, "extent_bottom": None}),
                      ("every guard", {"d_min": tb.D_MIN, "alike_feat": tb.ALIKE_FEAT}),
                      ("the pick, merged into the fixed mask", {"mode": "merge"}), ("the pick, alone (fixed colors off)", {"mode": "alone"})):
        L.append(line(dataclasses.replace(pick, **kw), label))
    L += ["", "## Every setting of the primary family (add)", "", head] + [line(st) for st in tb.FAMILIES["C1_add_guards"]]
    L += ["", "## Every setting of the merge family", "", head] + [line(st) for st in tb.FAMILIES["C2_merge_guards"]]
    (cm.OUT / "insample.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:20]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
