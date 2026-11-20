#!/usr/bin/env python3
"""The pre-registered rule, clause by clause, read off the files the other scripts wrote (``cells.csv`` of the
scorecard, ``levels.csv``, ``eval.csv``); computes nothing new. The recordings clause is judged by eye (``by_eye.md``)
and is not in here.

    python barrels/experiments/2026-11-20_occl_combined/check.py [folder] [--arms combined,combined+thin] [--ref stack] [--on-top combined]
    python barrels/experiments/2026-11-20_occl_combined/check.py verify --verify --ref combined --arms combined+verify,combined+verify2

Default rule (PREREG "The rule"), each arm against ``--ref`` (`stack`):
  (a) no HOME or CAMPUS scenario row loses a found barrel or gains a false box; no box on a negative frame of any set;
  (b) the scorecard's boxes where no barrel is not above the reference's; no cell (found, v2) lower;
  (c) false boxes not higher on the perfect masks, typical, bad day without the stripe patch and light, with 5 and with
      20 seeds; on bad day and medium not more than double.
``--on-top X`` adds, for the arms other than X: no scorecard cell lower than X's, false boxes at every judged level not
higher than X's (PREREG, how it is applied, 3: `pin_thin`).

``--verify`` (PREREG "The verifier's rule"), each arm against ``--ref`` (`combined`): removes wrong boxes somewhere;
loses no right box on HOME, CAMPUS, the perfect masks or typical; no scorecard cell drops by more than 1.

Output: results/2026-11-20_occl_combined/<folder>/check[_verify].md, and the same as text.
"""
from __future__ import annotations

import argparse
import csv

import common as C

JUDGED_SETS = ("HOME", "CAMPUS")
PERFECT, TYPICAL, BAD, NO_PATCH = "perfect masks", "white tables, typical", "white tables, bad day", "bad day without the stripe patch"
JUDGED = (PERFECT, TYPICAL, NO_PATCH, "light")
DOUBLE = (BAD, "medium")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", nargs="?", default="")
    ap.add_argument("--arms", default="combined,combined+thin")
    ap.add_argument("--ref", default="stack")
    ap.add_argument("--on-top", default="")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args(argv)
    folder = C.OUT / args.folder
    arms = [a for a in args.arms.split(",") if a]
    ref = args.ref

    cells = {(r["arm"], r["row"], float(r["amount"])): r for r in csv.DictReader((folder / "cells.csv").open()) if r["pool"] == "ALL"}
    keys = list(dict.fromkeys((k[1], k[2]) for k in cells))
    levels = {(r["level"], r["arm"], int(r["seeds"])): r for r in csv.DictReader((folder / "levels.csv").open())}
    ev = {(r["arm"], r["set"], r["scenario"], r["kind"]): r for r in csv.DictReader((folder / "eval.csv").open())}
    ev_keys = list(dict.fromkeys(k[1:] for k in ev))

    def card(arm, field):
        return sum(int(cells[(arm, *k)][field]) for k in keys)

    def lvl(level, arm, seeds, field):
        r = levels.get((level, arm, 1 if level == PERFECT else seeds))
        return int(r[field])

    def lower_cells(arm, against, slack=0):
        return [(k, int(cells[(against, *k)]["found_v2"]), int(cells[(arm, *k)]["found_v2"])) for k in keys
                if int(cells[(arm, *k)]["found_v2"]) < int(cells[(against, *k)]["found_v2"]) - slack]

    def eval_rows(arm, against):
        lost, gained, neg = [], [], 0
        for s, sc, kind in ev_keys:
            c, b = ev[(arm, s, sc, kind)], ev[(against, s, sc, kind)]
            if kind == "subtotal":
                neg += int(c["boxes_on_negatives"])
            if kind != "scene" or s.rstrip("*").upper() not in JUDGED_SETS:
                continue
            if int(c["found"]) < int(b["found"]):
                lost.append(f"{s} {sc}: found {b['found']} → {c['found']}")
            if int(c["false"]) > int(b["false"]):
                gained.append(f"{s} {sc}: false {b['false']} → {c['false']}")
        return lost, gained, neg

    def sub(arm, s):
        r = ev[(arm, s, "", "subtotal")]
        return f"{r['found']} / {r['missed']} / {r['false']}"

    L: list[str] = []
    if not args.verify:
        L += [f"# The rule, clause by clause: each arm against `{ref}`", "",
              f"Folder `{folder.name or 'results/2026-11-20_occl_combined'}`. `{ref}`: scorecard found {card(ref, 'found_v2')}, boxes where no barrel is {card(ref, 'false_boxes')}; "
              f"eval table HOME {sub(ref, 'HOME')}, CAMPUS {sub(ref, 'CAMPUS')}.", ""]
        for a in arms:
            lost, gained, neg = eval_rows(a, ref)
            ok_a = not lost and not gained and neg == 0
            low = lower_cells(a, ref)
            ok_b = card(a, "false_boxes") <= card(ref, "false_boxes") and not low
            c_lines, ok_c = [], True
            for level in JUDGED:
                for seeds in ((5,) if level == PERFECT else (5, 20)):
                    x, y = lvl(level, a, seeds, "false"), lvl(level, ref, seeds, "false")
                    good = x <= y
                    ok_c = ok_c and good
                    c_lines.append(f"| {level} | {'-' if level == PERFECT else seeds} | {y} | {x} | not higher | {'pass' if good else '**FAILS**'} | "
                                   f"{lvl(level, ref, seeds, 'found')} → {lvl(level, a, seeds, 'found')} of {lvl(level, a, seeds, 'barrels')} |")
            for level in DOUBLE:
                for seeds in (5, 20):
                    x, y = lvl(level, a, seeds, "false"), lvl(level, ref, seeds, "false")
                    good = x <= 2 * y
                    ok_c = ok_c and good
                    c_lines.append(f"| {level} | {seeds} | {y} | {x} | not more than double | {'pass' if good else '**FAILS**'} | "
                                   f"{lvl(level, ref, seeds, 'found')} → {lvl(level, a, seeds, 'found')} of {lvl(level, a, seeds, 'barrels')} |")
            for level in ("heavy", "white tables, worst seen"):
                for seeds in (5, 20):
                    c_lines.append(f"| {level} | {seeds} | {lvl(level, ref, seeds, 'false')} | {lvl(level, a, seeds, 'false')} | report only | | "
                                   f"{lvl(level, ref, seeds, 'found')} → {lvl(level, a, seeds, 'found')} of {lvl(level, a, seeds, 'barrels')} |")
            L += [f"## `{a}`", "",
                  f"- **(a) eval table: {'pass' if ok_a else 'FAILS'}.** HOME {sub(ref, 'HOME')} → {sub(a, 'HOME')}, CAMPUS {sub(ref, 'CAMPUS')} → {sub(a, 'CAMPUS')} "
                  f"(found / missed / false); rows that lose a barrel: {lost or 'none'}; rows that gain a false box: {gained or 'none'}; boxes on negative frames, any set: {neg}.",
                  f"- **(b) scorecard: {'pass' if ok_b else 'FAILS'}.** Found {card(ref, 'found_v2')} → {card(a, 'found_v2')} of {card(a, 'n')}; right place "
                  f"{card(ref, 'right_place')} → {card(a, 'right_place')}; boxes where no barrel is {card(ref, 'false_boxes')} → {card(a, 'false_boxes')}; cells lower: "
                  + (", ".join(f"{k[0]} at {int(round(100 * k[1]))} % ({x} → {y})" for k, x, y in low) or "none") + ".",
                  f"- **(c) damage levels: {'pass' if ok_c else 'FAILS'}** (the recordings: `by_eye.md`).", "",
                  f"| level | seeds | false, `{ref}` | false, `{a}` | must be | | found |", "|---|---|---|---|---|---|---|"] + c_lines + [""]
            found_down = [f"{level} ({seeds} seeds): {lvl(level, ref, seeds, 'found')} → {lvl(level, a, seeds, 'found')}" for level in dict.fromkeys(k[0] for k in levels)
                          for seeds in ((5,) if level == PERFECT else (5, 20)) if lvl(level, a, seeds, "found") < lvl(level, ref, seeds, "found")]
            L += ["Found lower at a damage level (not in the rule, named): " + ("; ".join(found_down) or "none") + ".", ""]
            top = args.on_top
            if top and a != top:
                low2 = lower_cells(a, top)
                worse = [f"{level} ({seeds} seeds): {lvl(level, top, seeds, 'false')} → {lvl(level, a, seeds, 'false')}" for level in JUDGED + DOUBLE
                         for seeds in ((5,) if level == PERFECT else (5, 20)) if lvl(level, a, seeds, "false") > lvl(level, top, seeds, "false")]
                ok_t = not low2 and not worse
                L += [f"- **on top of `{top}`: {'pass' if ok_t else 'FAILS'}.** Scorecard found {card(top, 'found_v2')} → {card(a, 'found_v2')}, boxes where no barrel is "
                      f"{card(top, 'false_boxes')} → {card(a, 'false_boxes')}; cells lower than `{top}`: "
                      + (", ".join(f"{k[0]} at {int(round(100 * k[1]))} % ({x} → {y})" for k, x, y in low2) or "none")
                      + "; false boxes higher than `" + top + "` at a judged level: " + ("; ".join(worse) or "none") + ".", ""]
                ok_a = ok_a and ok_t
            L += [f"**`{a}`: {'passes (a), (b) and the counted part of (c)' if (ok_a and ok_b and ok_c) else 'FAILS'}.**", ""]
        name = "check.md"
    else:
        L += [f"# The verifier's rule: each arm against `{ref}`", "",
              f"`{ref}`: scorecard found {card(ref, 'found_v2')}, right place {card(ref, 'right_place')}, boxes where no barrel is {card(ref, 'false_boxes')}.", ""]
        for a in arms:
            lost, gained, neg = eval_rows(a, ref)
            low = lower_cells(a, ref, slack=1)
            any_low = lower_cells(a, ref)
            lv = []
            for level in dict.fromkeys(k[0] for k in levels):
                for seeds in ((5,) if level == PERFECT else (5, 20)):
                    lv.append(f"| {level} | {'-' if level == PERFECT else seeds} | {lvl(level, ref, seeds, 'found')} ({lvl(level, ref, seeds, 'false')}) | "
                              f"{lvl(level, a, seeds, 'found')} ({lvl(level, a, seeds, 'false')}) |")
            lost_lv = [f"{level} ({seeds} seeds): {lvl(level, ref, seeds, 'found')} → {lvl(level, a, seeds, 'found')}" for level in (PERFECT, TYPICAL)
                       for seeds in ((5,) if level == PERFECT else (5, 20)) if lvl(level, a, seeds, "found") < lvl(level, ref, seeds, "found")]
            removes = card(a, "false_boxes") < card(ref, "false_boxes") or any(
                lvl(level, a, 20 if level != PERFECT else 5, "false") < lvl(level, ref, 20 if level != PERFECT else 5, "false") for level in dict.fromkeys(k[0] for k in levels))
            ok = removes and not lost and not lost_lv and not low
            L += [f"## `{a}`", "",
                  f"- removes wrong boxes somewhere: **{'yes' if removes else 'no'}** (scorecard boxes where no barrel is {card(ref, 'false_boxes')} → {card(a, 'false_boxes')}).",
                  f"- HOME {sub(ref, 'HOME')} → {sub(a, 'HOME')}, CAMPUS {sub(ref, 'CAMPUS')} → {sub(a, 'CAMPUS')}; rows that lose a found barrel: {lost or 'none'}.",
                  f"- perfect masks and typical, found lower: {lost_lv or 'none'}.",
                  f"- scorecard: found {card(ref, 'found_v2')} → {card(a, 'found_v2')}, right place {card(ref, 'right_place')} → {card(a, 'right_place')}; cells lower at all: {len(any_low)}; "
                  f"cells that drop by more than 1: " + (", ".join(f"{k[0]} at {int(round(100 * k[1]))} % ({x} → {y})" for k, x, y in low) or "none") + ".",
                  "", f"| level | seeds | `{ref}`: found (false) | `{a}`: found (false) |", "|---|---|---|---|"]
            L += lv + ["", f"**`{a}`: {'passes the counted clauses (the campus recordings: by_eye.md)' if ok else 'FAILS'}.**", ""]
        name = "check_verify.md"
    (folder / name).write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
