#!/usr/bin/env python3
"""IN-SAMPLE exploration for experiment 2026-11-26_nearmiss: candidates on all ordinary train frames, counted as
the judge counts. NOT a judged result: what was looked at with this before PREREG.md was written is listed there.

    python barrels/experiments/2026-11-26_nearmiss/explore.py SPEC [SPEC ...] [--jobs 8] [--extreme] [--changes SPEC]

SPEC as in nm_common.py (fixed | hyst:K | hystg:K | pc:S,B,MODE). Train frames only.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nm_common as cm  # noqa: E402

from barrels import counting as ct  # noqa: E402


def table(specs, stems, recs, title: str) -> str:
    places = list(ct.group_stems(stems, "place"))
    by_place = ct.group_stems(stems, "place")
    short = [p.replace("home_", "").replace("_study", "").replace("uc_", "")[:9] for p in places]
    head = f"{'candidate':<18}" + "".join(f"{s:>10}" for s in short) + f"{'ALL':>8}{'frames':>8}{'notOn':>7}{'clean0':>7}{'clut0':>7}{'gain':>6}{'lost':>6}{'px out':>8}{'px in':>7}"
    lines = [title, head]
    base = cm.counts_of(recs["fixed"])
    px0 = sum(recs["fixed"][s]["px_out"] for s in stems) or 1
    pin0 = sum(recs["fixed"][s]["px_in"] for s in stems) or 1
    for spec in specs:
        t = cm.tally(recs[spec], stems)
        c = cm.counts_of(recs[spec])
        gain = sum(1 for s in stems for a, b in zip(base[s].gt, c[s].gt) if b == ct.FOUND and a != ct.FOUND)
        lost = sum(1 for s in stems for a, b in zip(base[s].gt, c[s].gt) if a == ct.FOUND and b != ct.FOUND)
        cells = "".join(f"{cm.tally(recs[spec], by_place[p]).found_w:>10.1f}" for p in places)
        lines.append(f"{spec:<18}{cells}{t.found_w:>8.1f}{t.found:>8d}{t.extra_w:>7.1f}{t.clean_empty:>7d}{t.cluttered_empty_w:>7.1f}{gain:>6d}{lost:>6d}"
                     f"{sum(recs[spec][s]['px_out'] for s in stems) / px0:>8.2f}{sum(recs[spec][s]['px_in'] for s in stems) / pin0:>7.2f}")
    t = cm.tally(recs["fixed"], stems)
    lines.append(f"({t.placements} placements, {t.barrels} barrels per frame, {len(stems)} frames; placements per place: "
                 + ", ".join(f"{s} {cm.tally(recs['fixed'], by_place[p]).placements}" for s, p in zip(short, places)) + ")")
    return "\n".join(lines)


def changes(spec: str, stems, recs) -> str:
    base, c = cm.counts_of(recs["fixed"]), cm.counts_of(recs[spec])
    out = [f"CHANGES {spec} against fixed"]
    for s in stems:
        d = [f"#{i + 1} {a}->{b}" for i, (a, b) in enumerate(zip(base[s].gt, c[s].gt)) if a != b]
        if d or base[s].boxes != c[s].boxes:
            # one letter per box: F found, O box off, W wrong color, S second box, N on nothing
            b0, b1 = base[s].to_dict()["boxes"], c[s].to_dict()["boxes"]
            extra = [tuple(bx) for bx, st in zip(recs[spec][s]["boxes"], b1) if st in "WSN"]
            kind = " [empty]" if base[s].negative else ""
            out.append(f"  {s}{kind}: {', '.join(d) or 'barrels same'}; boxes {b0 or '-'} -> {b1 or '-'}" + (f"; not on a barrel: {extra}" if extra else ""))
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("specs", nargs="+")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--extreme", action="store_true", help="also the report-only (extreme) conditions")
    ap.add_argument("--changes", action="append", default=[], help="list every frame that differs from fixed for this spec")
    a = ap.parse_args(argv)
    specs = list(dict.fromkeys(["fixed", *a.specs, *a.changes]))
    stems = cm.ordinary()
    recs = cm.ensure(specs, stems, a.jobs)
    print(table(specs, stems, recs, "ORDINARY train frames, in-sample (found = strict, per placement)"))
    if a.extreme:
        ext = cm.report_only()
        recs_x = cm.ensure(specs, ext, a.jobs)
        print()
        print(table(specs, ext, recs_x, "REPORT ONLY (extreme conditions), in-sample"))
    for spec in a.changes:
        print()
        print(changes(spec, stems, recs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
