#!/usr/bin/env python3
"""The planned look at the test frames of 2026-11-27 (plan: PREREG.md in this folder, committed before this ran).

    python barrels/experiments/2026-11-27_test_look/run.py
    python barrels/experiments/2026-11-27_test_look/run.py --rehearse OUTDIR    # the same code on the TRAIN frames, into OUTDIR

Run ONCE without ``--rehearse``. ``--rehearse`` runs every line of it on the train split instead (no test frame is
opened) and writes into OUTDIR, to find a bug before the one run. It opens the test frames only to run the detectors on them (no picture is written or shown). Three arms:

- ``now``: the default as merged (``pipeline.detect_frame(frame)``: the fixed colors eb863d84, ``DetConfig()``, the
  stripe by contrast); the one configuration of the plan.
- ``before``: the default before the contrast stage (``pipeline.detect_frame(frame, contrast=False)``), for comparison.
- ``vendor``: the robot's own detector, its boxes as saved with each frame (``data/vendor/<stem>_vendor.json``), on the
  frames that have a usable vendor file only. No assumption is made where there is none.

Every frame is scored by ``counting.classify_frame`` (the strict v2 rule, a box on its barrel that fails it = "off",
the other boxes wrong color / second / on nothing) against the hand boxes, and pooled per placement where the
arrangements allow it (``counting.build_placements``). Writes results/2026-11-27_test_look/: summary.md, numbers.json,
frames.json (every frame's boxes and states), and the two standard tables (``report.py``) for HOME and CAMPUS.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BARRELS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BARRELS / "src"))
from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import cv as bcv  # noqa: E402
from barrels import pipeline as pl  # noqa: E402
from barrels import report as rp  # noqa: E402
from barrels import splits as sp  # noqa: E402
from barrels import worldmap_bridge as wb  # noqa: E402
from barrels.detect_types import COLOR_NAMES  # noqa: E402

OUT = BARRELS / "results" / "2026-11-27_test_look"
assert str(Path(pl.__file__).resolve()).startswith(str(BARRELS)), f"barrels is imported from {pl.__file__}, not from this checkout"
ARMS = ("before", "now", "vendor")


def klass(s: str) -> str:
    return cnd.info(ct.condition_of(s)).klass


def cells(t: ct.Tally | None) -> dict | None:
    if t is None or t.frames == 0:
        return None
    return {"frames": t.frames, "placements": t.placements, "barrels": t.barrels, "found_w": round(t.found_w, 2), "found": t.found,
            "off": t.off, "extra": t.extra, "extra_w": round(t.extra_w, 2), "wrong": t.wrong, "second": t.second, "nothing": t.nothing,
            "empty_frames": t.empty_frames, "clean_empty": t.clean_empty, "cluttered_empty_w": round(t.cluttered_empty_w, 2), "empty": t.empty}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rehearse", default=None, metavar="OUTDIR", help="run on the train split into OUTDIR (no test frame opened)")
    args = ap.parse_args()
    split = "train" if args.rehearse else "test"
    out = Path(args.rehearse) if args.rehearse else OUT
    splits = sp.load_splits()
    sel = rp.select_frames(rp.labeled_stems(), splits, split=split)
    sel = rp.Selection({k: v for k, v in sel.sets.items() if not rp.is_indicative(k)}, sel.skipped, sel.split)
    stems = [s for v in sel.sets.values() for s in v]
    rp.refuse_test_frames(stems, splits, allow_test=split == "test")
    vendor = rp.vendor_coverage(sel, splits)
    gts, clean = ct.load_gts(stems)
    cache = rp.FrameCache()
    model = pl.default_model()
    boxes = {"before": {}, "now": {}, "vendor": {}}
    for s in stems:
        f = cache.frame(s)
        boxes["before"][s] = pl.detect_frame(f, model, contrast=False)
        boxes["now"][s] = pl.detect_frame(f, model)
        if s in vendor.barrels:
            boxes["vendor"][s] = vendor.barrels[s]
    counts = {a: {s: ct.classify_frame(s, p, gts[s], clean[s]) for s, p in boxes[a].items()} for a in ARMS}
    try:
        placements = ct.build_placements(gts)
        why = ""
    except ct.ArrangementMismatch as e:             # then per frame only (the plan says so)
        placements, why = None, str(e)

    def tal(arm: str, group: list[str]) -> ct.Tally | None:
        g = [s for s in group if s in counts[arm]]
        if not g or placements is None:
            return None
        return ct.tally(counts[arm], g, placements)

    vstems = [s for s in stems if s in boxes["vendor"]]
    groups: dict[str, dict[str, list[str]]] = {
        "set": {rp.set_label(k, list(sel.sets)): v for k, v in sel.sets.items()},
        "place": ct.group_stems([s for s in stems if klass(s) == cnd.ORDINARY], "place"),
        "place_report_only": ct.group_stems([s for s in stems if klass(s) != cnd.ORDINARY], "place"),
        "condition": ct.group_stems(stems, "condition"),
        "total": {"all test frames": stems, "ordinary conditions": [s for s in stems if klass(s) == cnd.ORDINARY],
                  "report only (extreme / other)": [s for s in stems if klass(s) != cnd.ORDINARY]},
    }
    numbers: dict = {"git": bcv.git_hash(), "frames": len(stems), "vendor_frames": len(vstems), "placements_error": why,
                     "vendor_no_file": len(vendor.no_file), "vendor_not_measured": len(vendor.not_measured), "groups": {}}
    for level, gs in groups.items():
        numbers["groups"][level] = {}
        for name, g in gs.items():
            gv = [s for s in g if s in boxes["vendor"]]
            numbers["groups"][level][name] = {
                "klass": sorted({klass(s) for s in g}),
                "all": {a: cells(tal(a, g)) for a in ("before", "now")},
                "vendor_frames": {a: cells(tal(a, gv)) for a in ARMS} if gv else None,
            }
    frames = {s: {"set": rp.set_label(rp.set_key(s), list(sel.sets)), "condition": ct.condition_of(s), "place": ct.place_of(s), "klass": klass(s),
                  "clean": clean[s], "truth": [(COLOR_NAMES[g.color], list(g.bbox)) for g in gts[s]],
                  **{a: {"boxes": [(COLOR_NAMES[b.color], list(b.bbox)) for b in boxes[a][s]], "gt": list(counts[a][s].gt),
                         "box_states": list(counts[a][s].boxes)} for a in ARMS if s in boxes[a]}} for s in stems}
    out.mkdir(parents=True, exist_ok=True)
    (out / "numbers.json").write_text(json.dumps(numbers, indent=1) + "\n")
    (out / "frames.json").write_text(json.dumps(frames, indent=1) + "\n")
    # the standard tables, as the previous look printed them (HOME and CAMPUS v2 score among them)
    now_arm = rp.Arm("now", wb.DEFAULT_MODEL)
    before_arm = rp.Arm("before", wb.DEFAULT_MODEL, contrast=False)
    rep = rp.make_report(now_arm, before_arm, split=split)
    rp.write_all(rep, out / "now_vs_before", title="Test look 2026-11-27: now (contrast) vs before")
    rep_v = rp.make_report(now_arm, rp.vendor_arm(), split=split)
    rp.write_all(rep_v, out / "now_vs_vendor", title="Test look 2026-11-27: now (contrast) vs the vendor")
    print(json.dumps(numbers["groups"]["total"], indent=1))
    print("written to", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
