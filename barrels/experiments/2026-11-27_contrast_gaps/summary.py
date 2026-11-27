"""summary.md: every judged candidate of both rounds in one table (from rows.json and rows_insample.json).

    python barrels/experiments/2026-11-27_contrast_gaps/summary.py
"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "results" / "2026-11-27_contrast_gaps"


def table(rows, title):
    out = [f"## {title}", "",
           "| candidate | setting | verdict | found per placement | found per frame (strict) | gained / lost (ordinary) | report only gained / lost | "
           "boxes not on their barrel (per arrangement) | boxes on empty frames | places that moved (found; boxes) | traps |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        moved = "; ".join(f"{p} {v:+g}" for p, v in r["places_found"].items()) or "none"
        mx = "; ".join(f"{p} {v:+g}" for p, v in r["places_extra"].items())
        out.append(f"| {r['name']} | {r.get('key', 'per fold')} | {r['verdict']} | {r['found_w'][0]} -> {r['found_w'][1]} | {r['found_frame'][0]} -> {r['found_frame'][1]} | "
                   f"{r['gained']} / {r['lost']} | {r['report_gained']} / {r['report_lost']} | {r['extra_w'][0]} -> {r['extra_w'][1]} | "
                   f"{r['empty'][0]} -> {r['empty'][1]} (clean {r['clean_empty'][0]} -> {r['clean_empty'][1]}) | {moved}{'; boxes ' + mx if mx else ''} | "
                   f"{'; '.join(r['traps']) or 'clean'} |")
    return out


def main():
    lines = ["# Contrast gaps: every judged candidate", "",
             "Baseline: today's default (fixed colors, detector, stripe by contrast). Ordinary train frames: 154 frames, 172 placements, 8 places.", ""]
    if (OUT / "rows.json").exists():
        lines += table(json.loads((OUT / "rows.json").read_text())["rows"], "Round 1: leave one place out (the registered result)") + [""]
    if (OUT / "rows_insample.json").exists():
        lines += table(json.loads((OUT / "rows_insample.json").read_text())["rows"],
                       "Round 2 (PREREG addendum): fixed at the all-places pick, IN-SAMPLE") + [""]
    (OUT / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
