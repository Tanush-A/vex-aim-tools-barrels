#!/usr/bin/env python3
"""Ours against the vendor, counted per placement and with a misplaced box counted once (2026-11-26, TODO M1; the
definitions and the checks: PREREG.md in this folder). No arguments.

    python barrels/experiments/2026-11-26_measure/run.py

It runs today's detector and reads the saved vendor boxes on the TRAIN frames (``report.make_report`` refuses test
frames before anything is opened), then:

1. checks the new counting against the old one (PREREG C1-C4; a failed check stops the script: it is a bug);
2. writes the headline table: by place, strict and second accounting, with the placements each number rests on, the
   vendor ASSUMED on the two white tables that have no vendor file;
3. writes the per-condition table (kept), every barrel's state (``per_barrel.csv``) and a sensitivity table: the same
   counts with "overlap" and with "position" as the test for "this box is on this barrel".

Outputs: results/2026-11-26_measure/ (summary.md, places.json, per_barrel.csv, sensitivity.md).
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import math
import sys
from pathlib import Path

BARRELS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BARRELS / "src"))
from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import eval_det as ed  # noqa: E402
from barrels import report as rp  # noqa: E402
from barrels import worldmap_bridge as wb  # noqa: E402
from barrels.detect_types import COLOR_NAMES  # noqa: E402

OUT = BARRELS / "results" / "2026-11-26_measure"
OLD = {"ours": 148, "vendor": 177, "barrels": 243, "home": (28, 29), "campus": (35, 35), "placements": 108, "arrangements_with_barrels": 47, "places": 6}


def on_overlap(p, g) -> bool:
    """The audit's "overlap" rule as the test: IoU >= 0.5 (the bottom edge not checked)."""
    return ed.box_iou(p.bbox, g.bbox) >= ed.IOU_THR


def on_position(p, g) -> bool:
    """The audit's "place" rule as the test: the two box centers at most half the true box's width apart."""
    (px, py), (gx, gy) = rp.box_center(p), rp.box_center(g)
    return math.hypot(px - gx, py - gy) <= rp.CENTER_TOL_WIDTHS * g.width


def main() -> int:
    rep = rp.make_report(rp.Arm("ours", wb.DEFAULT_MODEL), rp.vendor_arm("vendor"))
    assert rep.placements is not None, rep.placement_error
    arms = {"ours": (rep.cand_boxes, rep.cand_counts), "vendor": (rep.base_boxes, rep.base_counts)}
    assumed = set(rep.assumed)
    measured = [s for ss in rep.selection.sets.values() for s in ss]
    ordinary = [s for s in measured if cnd.info(ct.condition_of(s)).klass == cnd.ORDINARY]
    checks = []

    # ---- C1: found is the strict rule, on every frame, for both arms
    n = 0
    for name, (boxes, counts) in arms.items():
        for s, preds in boxes.items():
            old, fc = ed.evaluate_frame(s, preds, rep.gts[s], rule="v2"), counts[s]
            assert fc.n_gt(ct.FOUND) == sum(old.tp.values()) and fc.n_gt(ct.OFF) + fc.n_gt(ct.MISSED) == sum(old.fn.values()), (name, s)
            assert len(fc.boxes) - fc.n_box(ct.FOUND) == sum(old.fp.values()) and len(fc.gt) == len(rep.gts[s]) and len(fc.boxes) == len(preds), (name, s)
            n += 1
    checks.append(f"C1 pass: on all {n} frame x arm pairs, found = the v2 rule's hits, found + box off + missed = the true barrels, and the box states add up to the boxes drawn.")

    # ---- C2: the old strict numbers
    to, tv = (ct.tally(c, ordinary, rep.placements) for _, c in arms.values())
    home = ct.tally(rep.cand_counts, [s for s in assumed if ct.condition_of(s) == "window_light"], rep.placements)
    campus = ct.tally(rep.cand_counts, [s for s in assumed if ct.condition_of(s) == "campus_light"], rep.placements)
    got = {"ours": to.found, "vendor": tv.found, "barrels": to.barrels, "home": (home.found, home.barrels), "campus": (campus.found, campus.barrels)}
    assert all(got[k] == OLD[k] for k in got), f"old strict numbers not reproduced: {got} against {OLD}"
    checks.append(f"C2 pass: the old strict numbers are reproduced exactly: ordinary new conditions, frames with vendor files, ours {to.found} and the vendor "
                  f"{tv.found} of {to.barrels}; HOME {home.found} of {home.barrels} (leave one scene out), CAMPUS {campus.found} of {campus.barrels}.")

    # ---- C3: what the 243 barrels are
    with_barrels = {rep.placements.arrangement[s] for s in ordinary if rep.gts[s]}
    n_pl, n_arr = rep.placements.count(ordinary)
    n_places = len({ct.place_of(s) for s in ordinary})
    assert (n_pl, len(with_barrels), n_places) == (OLD["placements"], OLD["arrangements_with_barrels"], OLD["places"]), (n_pl, len(with_barrels), n_places)
    checks.append(f"C3 pass: the {to.barrels} barrels of the ordinary new conditions are {n_pl} placements in {len(with_barrels)} arrangements at {n_places} places "
                  f"(with the {n_arr - len(with_barrels)} arrangements that hold no barrel: {n_arr}).")

    # ---- C4: a raw count is the same in the old table and in the new one
    for r in rep.rows:
        if r.kind != "subtotal":
            continue
        ss = rep.selection.sets[r.set_key]
        for cell, (_, counts) in zip((r.cand, r.base), arms.values()):
            t = ct.tally(counts, ss, rep.placements)
            assert (t.found, t.off + t.missed, t.strict_false, t.empty, t.clean_empty) == (cell.found, cell.missed, cell.false, cell.neg_false, cell.clean_neg_false), r.label
    checks.append("C4 pass: for every data set and both arms, found, missed, false boxes and boxes on empty frames counted per frame are the old table's numbers.")

    # ---- the tables
    tables = rp.place_tables(rep)
    names = ["ours", "vendor"]
    places_md = ct.format_table(tables["places"], names, markdown=True)
    cond_md = ct.format_table(tables["conditions"], names, markdown=True)
    both = ordinary + sorted(assumed)
    ao = ct.tally(rep.cand_counts, both, rep.placements)
    av = ct.tally(rep.base_counts, both, rep.placements)
    white = ct.tally(rep.base_counts, [s for s in ordinary if ct.condition_of(s) == "window_abpwhite"], rep.placements)
    v_empty_share = f"{tv.empty} of them on empty frames" if tv.nothing else "none"

    # ---- sensitivity: another test for "on a barrel"
    sens_rows, differ = [], []
    for label, on in (("chosen: half of the smaller box inside the other", ct.is_on), ("overlap: IoU >= 0.5", on_overlap),
                      ("position: centers within half the true width", on_position)):
        row = [label]
        for name, (boxes, _) in arms.items():
            counts = {s: ct.classify_frame(s, boxes[s], rep.gts[s], on=on) for s in ordinary}
            t = ct.tally(counts, ordinary, rep.placements)
            row += [f"{t.found_w:.1f} ({t.found})", f"{t.off_w:.1f} ({t.off})", f"{t.missed_w:.1f} ({t.missed})", str(t.wrong), str(t.second), str(t.nothing)]
            if on is on_position:
                for s in ordinary:
                    a, b = arms[name][1][s], counts[s]
                    if (a.gt, a.boxes) != (b.gt, b.boxes):
                        differ.append(f"| {name} | {s} | barrels {' '.join(a.gt)} / boxes {' '.join(a.boxes) or '-'} | barrels {' '.join(b.gt)} / boxes {' '.join(b.boxes) or '-'} | "
                                      f"true {[(COLOR_NAMES[g.color], list(g.bbox)) for g in rep.gts[s]]}; drawn {[(COLOR_NAMES[p.color], list(p.bbox)) for p in boxes[s]]} |")
        sens_rows.append("| " + " | ".join(row) + " |")
    sens = ["# How much the second accounting depends on the test for \"on a barrel\"", "",
            "The measured ordinary conditions (frames with vendor files). Found is the strict rule in every row; only what happens to the boxes that fail it changes. "
            "Cells: per placement (per frame).", "",
            "| test | ours found | ours box off | ours missed | ours wrong | ours 2nd | ours none | vendor found | vendor box off | vendor missed | vendor wrong | vendor 2nd | vendor none |",
            "|---|" + "---:|" * 12] + sens_rows + ["",
            f"Frames on which the chosen test and \"position\" give another state to a barrel or a box: {len(differ)}." + ("" if differ else " The two agree on every box of today's train frames."), ""]
    if differ:
        sens += ["| arm | frame | chosen test | position test | boxes (x0, y0, x1, y1) |", "|---|---|---|---|---|"] + differ + [""]

    # ---- per barrel
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "per_barrel.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["stem", "barrel", "color", "bbox", "flags", "place", "condition", "class", "arrangement", "placement", "ours", "vendor"])
        for s in sorted(rep.gts):
            for i, g in enumerate(rep.gts[s]):
                v = rep.base_counts.get(s)
                w.writerow([s, i + 1, COLOR_NAMES[g.color], " ".join(map(str, g.bbox)), " ".join(sorted(g.flags)), ct.place_of(s), ct.condition_of(s),
                            cnd.info(ct.condition_of(s)).klass, "/".join(rep.placements.arrangement[s]), rep.placements.key[(s, i)][-1] + 1,
                            rep.cand_counts[s].gt[i], "" if v is None else ("assumed found" if v.assumed else v.gt[i])])
    (OUT / "places.json").write_text(json.dumps(rp.places_json(rep) | {"checks": checks, "git": rep.git}, indent=1) + "\n")
    (OUT / "sensitivity.md").write_text("\n".join(sens))

    L = [f"# Ours against the vendor, every placement counted once ({dt.date.today().isoformat()}, git {rep.git})", "",
         "`python barrels/experiments/2026-11-26_measure/run.py` (definitions and checks: `../../experiments/2026-11-26_measure/PREREG.md`). Train frames only; test "
         "frames never opened. Ours = today's default (color model `eb863d84`, `DetConfig()`); the vendor = the boxes the robot's own detector reported, saved with each "
         "frame. HOME is scored leave one scene out, as in the eval table.", "",
         "**How to read it.** A *place* is a table in a room. An *arrangement* is one scene at one place; under five lamp settings it is still one arrangement. A "
         "*placement* is one barrel in one arrangement. A placement counts once: shot under several lights, it counts the share of its lights in which it is found. "
         "*Found* is the strict rule agreed with Dave (same color, IoU >= 0.5, bottom edge within 10 % of the height), unchanged. *Box off* is new: a box of the "
         "right color sits on the barrel but fails the strict rule; it used to be charged as a miss plus a false box. No winner is named for a single condition: "
         "most conditions are 15 placements at one place.", "",
         "## The headline table: by place", "", places_md, "",
         f"- **Measured places** ({n_places} places, {n_pl} placements in {len(with_barrels)} arrangements with barrels; {to.barrels} barrels when every light is counted): "
         f"ours **{to.found_w:.1f}** found, the vendor **{tv.found_w:.1f}**. Found either way (strict, or with the box off): ours {to.found_w + to.off_w:.1f}, the vendor "
         f"{tv.found_w + tv.off_w:.1f}.",
         f"- **Boxes.** Ours: {to.off} on their barrel but off, {to.wrong} wrong color, {to.second} second boxes, {to.nothing} on nothing ({to.empty} on empty frames). "
         f"The vendor: {tv.off} on their barrel but off, {tv.wrong} wrong color, {tv.second} second boxes, {tv.nothing} on nothing ({v_empty_share}).",
         f"- **The same frames counted the old way:** ours {to.found} and the vendor {tv.found} of {to.barrels} found; \"false boxes\" {to.strict_false} against {tv.strict_false}. "
         f"Of the vendor's {tv.strict_false}, {tv.off} sit on a real barrel of their color and fail the strict rule; of ours {to.strict_false}, {to.off}.",
         f"- **ASSUMED, not measured** (starred): on the two white tables without vendor files (home and the campus study room, {len(assumed)} frames, "
         f"{home.placements + campus.placements} placements) the vendor counts as finding every barrel (Tanush, 2026-11-26). With that assumption added: ours "
         f"{ao.found_w:.1f} of {ao.placements} placements, the vendor {av.found_w:.1f}* of {av.placements}. The assumption says nothing about the vendor's boxes there.",
         f"- **The one white table where the vendor was measured** is the ABP occlusion set (window light): {white.found} of {white.barrels} strict, {white.off} more with "
         "the box off. It is an occlusion set, harder than the home and campus scenes; it is the only check on the assumption that exists.", "",
         "## By condition (kept; one light each, so per placement = per frame)", "", cond_md, "",
         "## What the columns mean", "", ct.LEGEND, "",
         "## The checks of the pre-registration", ""] + [f"- {c}" for c in checks] + ["",
         "## Does it depend on the test for \"on a barrel\"?", "",
         f"`sensitivity.md` recounts the measured places with the audit's two other rules as the test. Frames where the chosen test and \"position\" disagree: {len(differ)}.", "",
         "Files: `places.json` (every number), `per_barrel.csv` (every train barrel: its placement and its state for ours and for the vendor), `sensitivity.md`.", ""]
    (OUT / "summary.md").write_text("\n".join(L))
    print("\n".join(L))
    print("\n".join(sens[:9]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
