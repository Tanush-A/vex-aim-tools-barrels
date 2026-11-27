"""The judged runs of the self-calibration experiment, exactly as PREREG.md registers them, and the report.

    python barrels/experiments/2026-11-26_selfcal/run.py               # everything (about half an hour)
    python barrels/experiments/2026-11-26_selfcal/run.py AB B_local    # only these families (plus the report on the first)

Writes ``results/2026-11-26_selfcal/``: one folder per judged candidate (judge.md, judge.json, changes.csv),
``summary.md`` and ``summary.json`` (every candidate, the setting each fold picked, seeds per condition, the guards on
empty and clutter frames, paint outside the hand boxes, the report-only "one session" numbers) and ``sheets/*.png``
(contact sheets of every barrel gained or lost and every new box that is not on its barrel; not committed).
Train frames only: every image goes through ``judge.load_frame``.
"""
from __future__ import annotations

import collections
import dataclasses
import json
import sys

import candidates as cand
import common as cm
import look
import sheets as sh
from barrels import conditions as cnd
from barrels import counting as ct
from barrels import judge as jg
from barrels import selfcal as sc

FAMILIES = ["A_found", "B_local", "B_frame", "AB"]
WEAK_ABOVE_MARGIN = 2.0          # a PASS less than this many placements above the gain margin is WEAK (the brief; EVAL.md says 1.5)


def cfg_of(family: str, place: str):
    kw = cand.CHOSEN[(family, place)]["setting"]
    return None if kw is None else dataclasses.replace(cand.BASE[family], **kw)


def judged_row(name: str, j) -> dict:
    b, c = j.total
    m = j.margins
    d = c.found_w - b.found_w
    moved = {p: round(cc.found_w - bb.found_w, 2) for p, (bb, cc) in j.places.items() if abs(cc.found_w - bb.found_w) > 1e-9}
    weak = j.result == jg.PASS and d < m.found_gain + WEAK_ABOVE_MARGIN
    return {"candidate": name, "verdict": j.result + (" (WEAK)" if weak else ""), "found_w": [round(b.found_w, 1), round(c.found_w, 1)],
            "found": [b.found, c.found], "barrels": b.barrels, "placements": b.placements, "delta_found_w": round(d, 2),
            "extra_w": [round(b.extra_w, 2), round(c.extra_w, 2)], "extra": [b.nothing + b.second + b.wrong, c.nothing + c.second + c.wrong],
            "empty": [b.empty, c.empty], "clean_empty": [b.clean_empty, c.clean_empty], "cluttered_empty_w": [round(b.cluttered_empty_w, 2), round(c.cluttered_empty_w, 2)],
            "places_moved": moved, "reason": j.verdict.reason,
            "conditions": {k: [bb.found, cc.found, bb.barrels] for k, (bb, cc) in j.conditions.items()},
            "report_only": {k: [bb.found, cc.found, bb.barrels] for k, (bb, cc) in j.report_only.items()},
            "gained": sum(1 for x in j.changes if x.judged and x.kind == "gained"), "lost": sum(1 for x in j.changes if x.judged and x.kind == "lost")}


def seeds_report(family: str, frames: dict, truth) -> tuple[dict, dict]:
    """With each place's own held-out setting: per condition the seed counts (``common.per_condition``), and what the
    guards did with seed candidates that are NOT on a hand box (empty frames, clutter, the room)."""
    stems = frames[cnd.ORDINARY] + frames[cnd.EXTREME]
    recs = {}
    for place, ss in ct.group_stems(stems, "place").items():
        cfg = cfg_of(family, place)
        if cfg is None:
            cfg = dataclasses.replace(cand.BASE[family], seed_found=False, seed_body=False, seed_stripe=False)       # the fixed detector
        recs.update(cm.run_setting(cfg, ss, truth))
    recs = {s: recs[s] for s in stems}
    guards = collections.Counter()
    for s, r in recs.items():
        gts = truth.gts[s]
        klass = cnd.info(ct.condition_of(s)).klass
        kind_of_frame = "empty" if not gts else "clutter" if not truth.clean[s] else "plain"
        for kind, _, bbox, ok, why, _ in r["seeds"]:
            if why == "duplicate" or cm.seed_on_barrel(bbox, gts):
                continue
            guards[(klass, kind_of_frame, kind, why)] += 1
    return recs, guards


def session_report(family: str, recs: dict, frames: dict, truth) -> list[dict]:
    """REPORT ONLY. The same detector, but every frame also gets the readings of the kept seeds of the OTHER frames of
    its condition (one table under one light: what a robot working there for a session would have seen)."""
    stems = list(recs)
    rows = []
    for c, ss in ct.group_stems(stems, "condition").items():
        cfg = cfg_of(family, ct.place_of(ss[0]))
        if cfg is None or not cfg.frame:
            continue
        own = {s: sc.class_readings(recs[s]["kept"]) for s in ss}
        extra = {s: {k: [r for o in ss if o != s for r in own[o][k]] for k in (sc.ORANGE, sc.BLUE)} for s in ss}
        rec2 = cm.run_setting(cfg, ss, truth, extra=extra)
        rows.append({"condition": c, "class": cnd.info(c).klass, "barrels": sum(len(truth.gts[s]) for s in ss),
                     "fixed": sum(recs[s]["first"].n_gt(ct.FOUND) for s in ss), "per_frame": sum(recs[s]["count"].n_gt(ct.FOUND) for s in ss),
                     "session": sum(rec2[s]["count"].n_gt(ct.FOUND) for s in ss),
                     "extra_per_frame": sum(recs[s]["count"].extra for s in ss), "extra_session": sum(rec2[s]["count"].extra for s in ss),
                     "frames_with_readings": sum(1 for s in ss if any(extra[s].values()) or recs[s]["kept"]), "frames": len(ss),
                     "_counts": {s: rec2[s]["count"] for s in ss}})
    return rows


def make_sheets(family: str, j, out_dir) -> list[str]:
    """Photo | first pass | second pass for every frame with a barrel gained or lost or a changed box that is not on
    its barrel (ordinary conditions), six frames to a sheet."""
    groups = collections.OrderedDict()
    for x in j.changes:
        if x.judged and x.kind in ("gained", "lost"):
            groups.setdefault(x.kind, []).append(x.stem)
    groups["boxes"] = [x["stem"] for x in j.box_changes if x["judged"]]
    written = []
    for kind, stems in groups.items():
        stems = list(dict.fromkeys(stems))
        for i in range(0, len(stems), 6):
            rows = []
            for s in stems[i:i + 6]:
                cfg = cfg_of(family, ct.place_of(s))
                if cfg is None:
                    continue
                notes = [f"{c.color} {c.before}->{c.after}" for c in j.changes if c.stem == s]
                rows.append(look.two_pass_row(s, cfg, note="| " + "; ".join(notes))[0])
            if rows:
                written.append(str(sh.save_sheet(out_dir / f"{family}_{kind}_{i // 6 + 1:02d}.png", rows, scale=0.75)))
    return written


def md_table(head: list[str], rows: list[list]) -> str:
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(str(v) for v in r) + " |" for r in rows])


def main(argv) -> int:
    families = [a for a in argv if a in FAMILIES] or FAMILIES
    noguard = not argv or "noguard" in argv
    frames = jg.train_frames()
    stems = frames[cnd.ORDINARY] + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    truth = jg.load_truth(stems)
    out = cm.RESULTS
    out.mkdir(parents=True, exist_ok=True)
    rows, judgements = [], {}
    for fam in families:
        j = jg.judge(fit=getattr(cand, f"fit_{fam}"), name=fam, out_dir=out / fam, frames=frames, truth=truth)
        judgements[fam] = j
        print(jg.format_judgement(j), "\n", flush=True)
        rows.append(judged_row(fam, j))
    if noguard:
        j = jg.judge(cand.detect_noguard, name="AB_noguard", out_dir=out / "AB_noguard", frames=frames, truth=truth)
        judgements["AB_noguard"] = j
        print(jg.format_judgement(j), "\n", flush=True)
        rows.append(judged_row("AB_noguard", j))
    main_fam = "AB" if "AB" in families else families[0]
    chosen = {f"{fam}|{place}": v for (fam, place), v in cand.CHOSEN.items()}
    recs, guards = seeds_report(main_fam, frames, truth)
    cond_rows = cm.per_condition(recs, truth)
    session = session_report(main_fam, recs, frames, truth)
    ordinary = set(frames[cnd.ORDINARY])
    sess_counts = {s: r["count"] for s, r in recs.items()}
    for r in session:
        sess_counts.update(r.pop("_counts"))
    t_frame = ct.tally({s: r["count"] for s, r in recs.items()}, [s for s in recs if s in ordinary], truth.placements)
    t_sess = ct.tally(sess_counts, [s for s in recs if s in ordinary], truth.placements)
    sheets = make_sheets(main_fam, judgements[main_fam], out / "sheets")
    summary = {"candidates": rows, "chosen": chosen, "main_family": main_fam, "conditions": cond_rows,
               "guards_off_barrel": [{"class": k[0], "frame": k[1], "seed": k[2], "verdict": k[3], "n": v} for k, v in sorted(guards.items())],
               "session_report_only": {"rows": session, "ordinary_found_w": [round(t_frame.found_w, 2), round(t_sess.found_w, 2)],
                                       "ordinary_found": [t_frame.found, t_sess.found], "ordinary_extra_w": [round(t_frame.extra_w, 2), round(t_sess.extra_w, 2)]},
               "sheets": [s.split("/results/")[-1] for s in sheets]}
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=str) + "\n")
    md = ["# Self-calibration (2026-11-26_selfcal): the judged runs", "",
          "Made by `python barrels/experiments/2026-11-26_selfcal/run.py`. Train frames only. Every verdict is the standard pass rule's "
          "(`docs/EVAL.md`), leave one place out for the four families.", "", "## Every judged candidate", "",
          md_table(["candidate", "verdict", "found, placements (of 172)", "found, per frame (of 307)", "boxes not on their barrel (per arrangement)",
                    "boxes on empty frames (clean)", "gained / lost", "places that moved"],
                   [[r["candidate"], r["verdict"], f"{r['found_w'][0]} -> {r['found_w'][1]} ({r['delta_found_w']:+.1f})", f"{r['found'][0]} -> {r['found'][1]}",
                     f"{r['extra_w'][0]} -> {r['extra_w'][1]}", f"{r['empty'][0]} -> {r['empty'][1]} ({r['clean_empty'][0]} -> {r['clean_empty'][1]})",
                     f"{r['gained']} / {r['lost']}", ", ".join(f"{p} {d:+.1f}" for p, d in r["places_moved"].items()) or "none"] for r in rows]), "",
          "## The setting each fold picked", "",
          md_table(["family", "held-out place", "setting picked on the other places"],
                   [[k.split("|")[0], k.split("|")[1], json.dumps(v["setting"]) if v["setting"] else "the fixed detector"] for k, v in sorted(chosen.items())]), "",
          f"## Seeds per condition ({main_fam}, each place with its own held-out setting)", "", "```", cm.format_conditions(cond_rows), "```", "",
          "fix / cand = barrels found per frame by the fixed detector / the candidate; fr.b = frames with barrels; fr.sd = of those, frames with at "
          "least one kept seed; s.fnd / s.bdy / s.str = kept seeds by kind; s.off = kept seeds that are not on a hand box; sd.emp = empty frames "
          "with a kept seed; moved = frames whose range moved; paint.out = painted pixels outside the hand boxes (grown 4 px), first and second pass.", "",
          "## The guards on seed candidates that are not on a barrel", "",
          md_table(["conditions", "frame", "seed kind", "verdict", "n"], [[g["class"], g["frame"], g["seed"], g["verdict"], g["n"]] for g in summary["guards_off_barrel"]]), "",
          "## REPORT ONLY: the colors carried across the frames of one condition (one table, one light)", "",
          f"Ordinary conditions, found per placement: per frame {t_frame.found_w:.1f}, with the session's readings {t_sess.found_w:.1f} "
          f"(per frame counted {t_frame.found} and {t_sess.found} of {t_frame.barrels}); boxes not on their barrel {t_frame.extra_w:.1f} and {t_sess.extra_w:.1f}. "
          "Not a judged candidate: it uses other frames of the same place.", "",
          md_table(["condition", "class", "barrels", "fixed", "per frame", "session", "extra boxes per frame", "extra boxes session"],
                   [[r["condition"], r["class"], r["barrels"], r["fixed"], r["per_frame"], r["session"], r["extra_per_frame"], r["extra_session"]] for r in session]), "",
          "## Sheets (not committed)", ""] + [f"- `{s}`" for s in summary["sheets"]]
    (out / "summary.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
