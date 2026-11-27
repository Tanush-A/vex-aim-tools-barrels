"""Group 5: a box the contrast stage ADDS on a barrel that has a box of the other color. Counted on every train frame
(ordinary, extreme, excluded) and on Dave's 12 office frames (``DAVE_office_speckle_*``: in no split; indicative only,
his labels group touching barrels). For each overlap share of the rule (``gaps.Gaps.other``), every box the rule drops,
whether it was on a labelled barrel of its own color, and whether that barrel is left with no box (a real barrel lost).

    python barrels/experiments/2026-11-27_contrast_gaps/other.py
"""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gaps as gp  # noqa: E402

from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402

OUT = gp.BARRELS / "results" / "2026-11-27_contrast_gaps"
DAVE = [f"DAVE_office_speckle_snap_{i:02d}" for i in range(12)]
SHARES = (0.5, 0.4, 0.3)


def load(stem):
    if stem.startswith("DAVE_"):
        test = set(json.loads((gp.BARRELS / "data" / "splits.json").read_text())["test"])
        assert stem not in test
        return pl.Frame.from_image(io.load_image(io.find_image(stem)))
    return jg.load_frame(stem)


def one(stem):
    import cv2
    cv2.setNumThreads(1)
    f = load(stem)
    base = gp.detect(f, gp.Gaps())
    label = io.load_boxes(stem, check_image=False) if io.boxes_path(stem).exists() else {"boxes": []}
    gts = dtp.barrels_from_boxes(label)
    rows = []
    for sh in SHARES:
        new = gp.detect(f, gp.Gaps(other=sh))
        for b in base:
            if b in new:
                continue
            on = [g for g in gts if g.color == b.color and ct.is_on(b, g)]
            lost = [g.bbox for g in on if not any(p.color == g.color and ct.is_on(p, g) for p in new)]
            partner = [(o.bbox, o.color, o.source, round(gp.overlap_of_smaller(b.bbox, o.bbox), 2)) for o in base
                       if o.color != b.color and gp.overlap_of_smaller(b.bbox, o.bbox) > sh]
            rows.append({"stem": stem, "share": sh, "box": b.bbox, "color": b.color, "source": b.source, "partner": partner,
                         "on_own_color_barrel": [g.bbox for g in on], "real_barrel_lost": lost})
    return stem, rows


def main():
    fr = jg.train_frames()
    stems = [s for v in fr.values() for s in v] + DAVE
    res = {}
    with Pool(8) as p:
        for s, r in p.imap_unordered(one, stems, chunksize=2):
            res[s] = r
    rows = [r for s in stems for r in res[s]]
    (OUT / "other_color.json").write_text(json.dumps(rows, indent=1, default=str))
    lines = ["# Group 5: an added contrast box on a barrel that has a box of the other color", "",
             "Rule (gaps.Gaps.other): two boxes of different colors whose overlap is more than SHARE of the smaller box's area, at least one "
             "of them added by the contrast stage: two boxes of about the same height (within 1.25x): the added one is dropped when the stripe pattern supports the other color better "
             "(gaps.pattern_support: the signed sandwich score at the stripe row its bottom predicts; on a near tie, under 0.25 apart, gaps.color_support in the fixed mask). Today's default, "
             "every train frame (ordinary, extreme, excluded) and Dave's 12 office frames (in no split; indicative, his labels group touching barrels).", "",
             "| share | frame | dropped box | color | source | the other box (box, color, source, overlap) | on a labelled barrel of its color | real barrel lost |",
             "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['share']} | {r['stem']} | {r['box']} | {'orange' if r['color'] == 1 else 'blue'} | {r['source']} | {r['partner']} | "
                     f"{r['on_own_color_barrel'] or 'no'} | {r['real_barrel_lost'] or 'no'} |")
    groups = {"ordinary": fr["ordinary"], "extreme": fr["extreme"], "excluded": fr.get("excluded", []), "Dave office": DAVE}
    lines += ["", "| share | set | frames | boxes dropped | of them on a labelled barrel of their color | real barrels lost |", "|---|---|---|---|---|---|"]
    for sh in SHARES:
        for k, ss in groups.items():
            rr = [r for s in ss for r in res.get(s, []) if r["share"] == sh]
            lines.append(f"| {sh} | {k} | {len(ss)} | {len(rr)} | {sum(1 for r in rr if r['on_own_color_barrel'])} | {sum(len(r['real_barrel_lost']) for r in rr)} |")
    (OUT / "other_color.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
