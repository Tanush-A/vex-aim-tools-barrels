#!/usr/bin/env python3
"""The one page for Tanush: ``results/2026-11-20_occl_combined/scorecard.md``. ONE table (rows = what hides the barrel,
columns = 25 / 50 / 75 % hidden, each cell ``before → after`` of n scenes), the totals, and the false boxes everywhere
in the battery. Read off the files the other scripts wrote (``cells.csv``, ``levels.csv``, ``eval.csv`` of one results
folder); computes nothing new. The sentences under the tables are in ``scorecard_notes.md`` next to this script
(written by hand after looking at the numbers and the sheets) and are appended as they are.

    python barrels/experiments/2026-11-20_occl_combined/make_scorecard.py round2 --after combined
Output: results/2026-11-20_occl_combined/scorecard.md
"""
from __future__ import annotations

import argparse
import csv

import common as C

ROWS = [("frame", "cut by the frame edge"), ("edge", "a straight upright edge, one side"), ("slant", "a slanted edge, one side"),
        ("both", "both sides cut"), ("top", "hidden from above"), ("bottom", "hidden from below (a low thing in front)"),
        ("post", "a post across the middle"), ("barrel_side/other", "a barrel of the OTHER color, beside it"),
        ("barrel_low/other", "a barrel of the OTHER color, beside it and lower"), ("barrel_front/other", "a barrel of the OTHER color, straight in front"),
        ("barrel_side/same", "a barrel of the SAME color, beside it"), ("barrel_low/same", "a barrel of the SAME color, beside it and lower"),
        ("barrel_front/same", "a barrel of the SAME color, straight in front"), ("block/same", "a plain block of the barrel's body color"),
        ("block/other", "a plain block of the barrel's stripe color")]
AMOUNTS = (0.25, 0.5, 0.75)
PERFECT = "perfect masks"
LEVEL_NOTE = {"perfect masks": "", "white tables, typical": "measured on real white-table segmentation", "white tables, bad day": "harsher than any real barrel measured",
              "bad day without the stripe patch": "bad day, minus the one kind real masks almost never show", "light": "made up, 2026-11-18",
              "medium": "made up; far harsher than real white-table segmentation", "heavy": "made up", "white tables, worst seen": "report only"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--before", default="before")
    ap.add_argument("--mid", default="stack")
    ap.add_argument("--after", default="combined")
    args = ap.parse_args(argv)
    folder = C.OUT / args.folder
    b, m, a = args.before, args.mid, args.after
    cells = {(r["arm"], r["row"], float(r["amount"])): r for r in csv.DictReader((folder / "cells.csv").open()) if r["pool"] == "ALL"}
    levels = {(r["level"], r["arm"], int(r["seeds"])): r for r in csv.DictReader((folder / "levels.csv").open())}
    ev = {(r["arm"], r["set"], r["scenario"], r["kind"]): r for r in csv.DictReader((folder / "eval.csv").open())}

    def tot(arm, field):
        return sum(int(cells[(arm, k, am)][field]) for k, _ in ROWS for am in AMOUNTS)

    def col(am, field="found_v2"):
        return [sum(int(cells[(arm, k, am)][field]) for k, _ in ROWS) for arm in (b, a)]

    L = ["# Occlusion scorecard: before all the occlusion work → the detector on `wip/occl-combined`", "",
         f"**before** = the defaults of `barrels` today (arm `{b}`: none of the unmerged occlusion branches). **after** = the default on this branch (arm `{a}`). "
         f"{tot(b, 'n')} simulated scenes: each of 50 free-standing barrels of the train frames, alone on an empty mask at its own place, hidden 25, 50 or 75 % "
         "by one thing. A cell counts the scenes where the detector draws a box of the right color on the barrel's FULL box (overlap of half or more, bottom "
         "edge right: the project's v2 rule). Each cell: **before → after, of n**.", "",
         "| what hides the barrel | 25 % hidden | 50 % hidden | 75 % hidden |", "|---|---|---|---|"]
    for k, name in ROWS:
        L.append(f"| {name} | " + " | ".join(f"{cells[(b, k, am)]['found_v2']} → {cells[(a, k, am)]['found_v2']} of {cells[(b, k, am)]['n']}" for am in AMOUNTS) + " |")
    n_am = [sum(int(cells[(b, k, am)]["n"]) for k, _ in ROWS) for am in AMOUNTS]
    L.append("| **all 15 kinds** | " + " | ".join(f"**{col(am)[0]} → {col(am)[1]} of {n}**" for am, n in zip(AMOUNTS, n_am)) + " |")
    L += ["", "## Totals, all scenes", "",
          f"| | before (`{b}`) | the five merged switches (`{m}`) | after (`{a}`) |", "|---|---|---|---|"]
    for name, field in (("found (v2 rule)", "found_v2"), ("a box of the right color in the right place, whatever its size", "right_place"),
                        ("**boxes where no barrel is**", "false_boxes"), ("right-place boxes too small", "too_small"), ("... about right", "about_right"),
                        ("... too big", "too_big")):
        L.append(f"| {name} | {tot(b, field)} | {tot(m, field)} | {tot(a, field)} |")
    L[-6] = L[-6].replace(f"| {tot(a, 'found_v2')} |", f"| {tot(a, 'found_v2')} of {tot(a, 'n')} |")

    def sub(arm, s):
        r = ev[(arm, s, "", "subtotal")]
        return f"{r['found']} of {r['barrels']} found, **{r['false']} false**, {r['boxes_on_negatives']} on negative frames"

    sets = list(dict.fromkeys(k[1] for k in ev if k[3] == "subtotal"))
    wood = [s for s in sets if "wood" in s]

    def many(arm, group):
        f = sum(int(ev[(arm, s, "", "subtotal")]["found"]) for s in group); n = sum(int(ev[(arm, s, "", "subtotal")]["barrels"]) for s in group)
        x = sum(int(ev[(arm, s, "", "subtotal")]["false"]) for s in group); g = sum(int(ev[(arm, s, "", "subtotal")]["boxes_on_negatives"]) for s in group)
        return f"{f} of {n} found, **{x} false**, {g} on negative frames"

    L += ["", "## False boxes, everywhere in the battery", "",
          f"| where | before (`{b}`) | `{m}` | after (`{a}`) |", "|---|---|---|---|",
          f"| real frames: HOME (16 train frames, leave one scene out) | {sub(b, 'HOME')} | {sub(m, 'HOME')} | {sub(a, 'HOME')} |",
          f"| real frames: CAMPUS (21 train frames) | {sub(b, 'CAMPUS')} | {sub(m, 'CAMPUS')} | {sub(a, 'CAMPUS')} |"]
    black = [s for s in sets if "black" in s]
    if black:
        L.append(f"| real frames: black table (extreme, report only) | {many(b, black)} | {many(m, black)} | {many(a, black)} |")
    if wood:
        L.append(f"| real frames: orange wood table, {len(wood)} lamp settings (extreme, report only) | {many(b, wood)} | {many(m, wood)} | {many(a, wood)} |")
    dave = [s for s in sets if s.startswith("DAVE")]
    if dave:
        L.append(f"| real frames: Dave's (indicative labels) | {many(b, dave)} | {many(m, dave)} | {many(a, dave)} |")
    neg = {arm: sum(int(ev[(arm, s, "", "subtotal")]["boxes_on_negatives"]) for s in sets) for arm in (b, m, a)}
    L.append(f"| boxes on negative frames, every set together | **{neg[b]}** | **{neg[m]}** | **{neg[a]}** |")
    L.append(f"| occlusion scorecard: boxes where no barrel is ({tot(b, 'n')} scenes) | {tot(b, 'false_boxes')} | {tot(m, 'false_boxes')} | {tot(a, 'false_boxes')} |")
    for level in dict.fromkeys(k[0] for k in levels):
        for seeds in ((1,) if level == PERFECT else (5, 20)):
            def t(arm):
                r = levels[(level, arm, seeds)]
                return f"{r['found']} of {r['barrels']} found, **{r['false']} false**"
            note = LEVEL_NOTE.get(level, "")
            L.append(f"| damaged masks: {level}" + ("" if level == PERFECT else f", {seeds} seeds") + (f" ({note})" if note else "") + f" | {t(b)} | {t(m)} | {t(a)} |")
    notes = C.HERE / "scorecard_notes.md"
    L += ["", notes.read_text().rstrip() if notes.exists() else "(scorecard_notes.md not written yet)"]
    (C.OUT / "scorecard.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
