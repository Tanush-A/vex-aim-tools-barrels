#!/usr/bin/env python3
"""Step 4 of the 2026-11-25 color work: ours with the candidate color model, ours with the fixed one, and the vendor,
per condition and per place, on the train frames that have a vendor file.

    python barrels/experiments/2026-11-25_color/vendor.py [--model results/2026-11-25_color/config.json]

Arms: ``report.run_arm`` (unchanged) with the adopted model, with the candidate model file, and the vendor's saved
boxes (``report.vendor_arm``); scored by the v2 rule (strict) and the looser "place" count (a box of the right color
centred on the barrel; ``report.loose_counts``). Test frames are refused before any vendor file is read. Writes
results/2026-11-25_color/vendor.md and vendor_per_barrel.csv.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402

from barrels import geometry as geo  # noqa: E402
from barrels import report as rp  # noqa: E402
from barrels import splits as sp  # noqa: E402
from barrels import worldmap_bridge as wb  # noqa: E402

CAM = geo.AIM_4A8B6118_BOXFIT


def counts(res, loose, stems) -> dict:
    c = rp.summarize([res[s] for s in stems], [loose[s] for s in stems])
    return {"barrels": c.barrels, "found": c.found, "false": c.false, "empty": c.neg_false, "place": c.loose["found_center"],
            "score": c.score}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", type=Path, default=cm.RESULTS / "config.json")
    ap.add_argument("--name", default="vendor", help="output files <name>.md and <name>_per_barrel.csv")
    a = ap.parse_args()
    a.model = a.model.resolve()
    if not a.model.exists():
        alt = cm.RESULTS / "config_best_not_passing.json"
        print(f"{a.model} does not exist; using {alt}")
        a.model = alt
    splits = sp.load_splits()
    sel = rp.select_frames(rp.labeled_stems(), splits, split="train")
    cov = rp.vendor_coverage(sel, splits)
    assert not (cov.stems & set(splits["test"]))
    cache = rp.FrameCache()
    arms = {"fixed": rp.Arm("fixed", wb.DEFAULT_MODEL), "candidate": rp.Arm("candidate", a.model), "vendor": rp.vendor_arm("vendor")}
    res, loose = {}, {}
    for name, arm in arms.items():
        loose[name] = {}
        res[name] = rp.run_arm(arm, sel, splits, cam=CAM, cache=cache, only=cov.stems, loose=loose[name], vendor=cov)
    by_cond = defaultdict(list)
    for s in sorted(cov.stems):
        by_cond[cm.condition_of(s)].append(s)
    conds = sorted(by_cond, key=lambda c: (cm.class_of(c) != "ordinary", cm.place_of(c), c))
    L = ["# Ours (candidate color model) against ours (fixed) and the vendor, per condition (2026-11-25, step 4)", "",
         f"`python barrels/experiments/2026-11-25_color/vendor.py --model {a.model.relative_to(cm.BARRELS)}`. Train frames with a vendor "
         f"file ({len(cov.stems)}); test frames never opened. Cells: strict found / barrels (v2 rule), false boxes, and in brackets "
         "the place count (a box of the right color centred on the barrel). Better = more found (strict) unless it brings as many "
         "more false boxes.", "",
         "| condition | class | barrels | fixed | candidate | vendor | candidate vs vendor |", "|---|---|---:|---|---|---|---|"]
    tot = defaultdict(lambda: defaultdict(int))
    per_place = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for c in conds:
        st = by_cond[c]
        k = {n: counts(res[n], loose[n], st) for n in arms}
        cell = lambda d: f"{d['found']} f{d['false']} ({d['place']})"  # noqa: E731
        df, dx = k["candidate"]["found"] - k["vendor"]["found"], k["candidate"]["false"] - k["vendor"]["false"]
        v = "tie" if df == 0 and dx == 0 else ("ours" if (df > 0 and dx < df) or (df == 0 and dx < 0) else
                                             "vendor" if (df < 0 and -dx < -df) or (df == 0 and dx > 0) else "mixed")
        L.append(f"| {c} | {cm.class_of(c)} | {k['vendor']['barrels']} | {cell(k['fixed'])} | {cell(k['candidate'])} | {cell(k['vendor'])} | "
                 f"{v} ({df:+d} found, {dx:+d} false) |")
        if cm.class_of(c) == "ordinary":
            for n in arms:
                for f in ("barrels", "found", "false", "place", "empty"):
                    tot[n][f] += k[n][f]
                    per_place[cm.place_of(c)][n][f] += k[n][f]
    L.append(f"| **all ordinary** | | {tot['vendor']['barrels']} | " + " | ".join(f"**{tot[n]['found']} f{tot[n]['false']} ({tot[n]['place']})**" for n in arms) + " | |")
    L += ["", "## By place (ordinary)", "", "| place | barrels | fixed | candidate | vendor |", "|---|---:|---|---|---|"]
    for p, d in sorted(per_place.items()):
        L.append(f"| {p} | {d['vendor']['barrels']} | " + " | ".join(f"{d[n]['found']} f{d[n]['false']} ({d[n]['place']})" for n in arms) + " |")
    # per barrel: what the vendor finds and the candidate misses
    rows = []
    for s in sorted(cov.stems):
        fo = {n: {m.gt_idx for m in res[n][s].matches} for n in arms}
        n_gt = sum(res["vendor"][s].n_gt.values())
        for g in range(n_gt):
            rows.append({"stem": s, "condition": cm.condition_of(s), "gt": g + 1, **{n: int(g in fo[n]) for n in arms}})
    with open(cm.RESULTS / f"{a.name}_per_barrel.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    miss = defaultdict(int)
    gain = defaultdict(int)
    for r in rows:
        if cm.class_of(r["condition"]) != "ordinary":
            continue
        if r["vendor"] and not r["candidate"]:
            miss[r["condition"]] += 1
        if r["candidate"] and not r["vendor"]:
            gain[r["condition"]] += 1
    L += ["", "Barrels (strict) the vendor finds and the candidate misses, per condition: " + (", ".join(f"{c} {n}" for c, n in sorted(miss.items(), key=lambda t: -t[1])) or "none")
          + ". The other way: " + (", ".join(f"{c} {n}" for c, n in sorted(gain.items(), key=lambda t: -t[1])) or "none") + ".", ""]
    (cm.RESULTS / f"{a.name}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
