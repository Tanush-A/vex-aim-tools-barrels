#!/usr/bin/env python3
"""The tables of the 2026-11-27 test look, from results/2026-11-27_test_look/numbers.json (opens no frame).

    python barrels/experiments/2026-11-27_test_look/tables.py

Writes results/2026-11-27_test_look/tables.md: by data set, by place (ordinary and report only), by condition, and the
totals; each on every test frame (before, now) and on the frames with a vendor file (before, now, vendor). The reading
goes into summary.md by hand, below these tables, as PREREG.md says.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "results" / "2026-11-27_test_look"


def f(c: dict | None, key: str, of: str | None = None) -> str:
    if c is None:
        return "–"
    v = c[key]
    s = f"{v:g}" if isinstance(v, float) else str(v)
    return f"{s} of {c[of]}" if of else s


def block(title: str, rows: dict, note: str) -> list[str]:
    out = [f"## {title}", "", note, "",
           "**Every test frame** (found per placement; per frame; boxes not on their barrel per frame; boxes on empty frames clean / with clutter):", "",
           "| group | frames | found per placement, before → now | found per frame, before → now | found with the box off, before → now | boxes not on their barrel, before → now | on empty frames, before → now |",
           "|---|---:|---|---|---|---|---|"]
    for name, r in rows.items():
        b, n = r["all"]["before"], r["all"]["now"]
        if n is None:
            continue
        out.append(f"| {name} | {n['frames']} | {f(b, 'found_w')} → {f(n, 'found_w', 'placements')} | {f(b, 'found')} → {f(n, 'found', 'barrels')} | "
                   f"{f(b, 'off')} → {f(n, 'off')} | {f(b, 'extra')} → {f(n, 'extra')} | {f(b, 'clean_empty')}/{f(b, 'cluttered_empty_w')} → "
                   f"{f(n, 'clean_empty')}/{f(n, 'cluttered_empty_w')} (of {n['empty_frames']} empty frames) |")
    vrows = {k: r for k, r in rows.items() if r.get("vendor_frames")}
    if vrows:
        out += ["", "**The frames with a vendor file** (the same three counts for ours before, ours now and the vendor):", "",
                "| group | frames | found per placement: before / now / vendor | found per frame: before / now / vendor | off: b / n / v | boxes not on their barrel: b / n / v | on empty frames (clean): b / n / v |",
                "|---|---:|---|---|---|---|---|"]
        for name, r in vrows.items():
            v = r["vendor_frames"]
            b, n, d = v["before"], v["now"], v["vendor"]
            out.append(f"| {name} | {n['frames']} | {f(b, 'found_w')} / {f(n, 'found_w')} / {f(d, 'found_w')} of {n['placements']} | "
                       f"{f(b, 'found')} / {f(n, 'found')} / {f(d, 'found')} of {n['barrels']} | {f(b, 'off')} / {f(n, 'off')} / {f(d, 'off')} | "
                       f"{f(b, 'extra')} / {f(n, 'extra')} / {f(d, 'extra')} | {f(b, 'clean_empty')} / {f(n, 'clean_empty')} / {f(d, 'clean_empty')} |")
    return out + [""]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", default=str(OUT), help="the folder with numbers.json (default: the test look's)")
    out = Path(ap.parse_args().dir)
    j = json.loads((out / "numbers.json").read_text())
    g = j["groups"]
    lines = ["# Test look 2026-11-27: the tables", "",
             f"Made by `experiments/2026-11-27_test_look/tables.py` from `numbers.json` (git {j['git']}). {j['frames']} test frames, "
             f"{j['vendor_frames']} with a usable vendor file ({j['vendor_no_file']} without a file, {j['vendor_not_measured']} not measured)."
             + (f" Placements could not be built: {j['placements_error']}" if j["placements_error"] else ""), ""]
    lines += block("Totals", g["total"], "Ordinary = the conditions the judge judges (data/conditions.json); report only = extreme and other.")
    lines += block("By data set", g["set"], "The data sets of `report.py` (HOME, CAMPUS, and one per {robot}_{light}_{surface}).")
    lines += block("By place, ordinary conditions", g["place"], "Each place pools its lights; a placement counts the share of its lights in which it is found.")
    lines += block("By place, report only", g["place_report_only"], "Extreme conditions (parked): never judged.")
    lines += block("By condition", g["condition"], "One light at one place.")
    (out / "tables.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
