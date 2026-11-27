#!/usr/bin/env python3
"""The judged runs of experiment 2026-11-26_combined (TODO E8; plan: PREREG.md in this folder).

    python barrels/experiments/2026-11-26_combined/run.py              # the judged runs, then the summary (about 20 minutes)
    python barrels/experiments/2026-11-26_combined/run.py --summary    # summary.md again, from the pages that exist
    python barrels/experiments/2026-11-26_combined/run.py --timing     # seconds per frame of every candidate (fixed numbers, no cache)

Run with ``PYTHONPATH=barrels/src``. Train frames only: the judge refuses anything else before an image is opened.

One pass over the frames (the 154 ordinary ones and the 77 report-only ones): today's detector, the two winners alone
(their own ``fit`` functions) and the five ways to combine them (``candidates.py``), each fitted leave one place out.
Every image is read once and handed to each detector (``judge.run_many``); every pair is then compared by the
standard pass rule (``judge.compare``): each candidate against today's detector (the verdict), and each combination
against each winner alone (is it worth having both?). This is what ``judge.judge(fit=...)`` does, for eight detectors
at once; the bottom of ENTRY.md has the ``tools/judge.py`` line that repeats one of them alone.

Two more detectors are run as a check and never judged: each winner alone, built from the combination module's own
building blocks. They must give the winner's own boxes on every frame (``checks`` in summary.json).

Writes results/2026-11-26_combined/: ``<name>/`` (the judge's pages against today's detector), ``<way>_vs_<winner>/``,
``boxes.json`` (every detector's boxes and box states on every frame; the other scripts here read it), ``chosen.json``
(what each winner's rule picked in each fold), ``timing.json``, ``summary.md`` and ``summary.json``.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cb_common as cb  # noqa: E402

cand = cb._load("cb_candidates", cb.HERE / "candidates.py")

from barrels import combined as cmb  # noqa: E402
from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import judge as jg  # noqa: E402

WINNERS = ("nearmiss", "selfcal")
WAYS = tuple(cmb.WAYS)
NAMES = WINNERS + WAYS
ANY = "(any place that is not an ordinary one)"
SIMPLER_FIRST = ("mask_union", "box_union", "nm_then_sc", "sc_then_nm", "box_agree")       # PREREG.md: the order of a tie
WEAK = 2.0


def check_fit(which: str):
    """A winner alone, built from ``barrels.combined``'s building blocks (the other step off). Never judged."""
    def fit(train_stems, held_place):
        spec, cfg = cand.fold_settings(train_stems, held_place)
        nm_cfg = cand.nm_config(spec)
        if which == "nearmiss":
            return lambda stem, frame: cmb.nm_then_sc(frame, cand.MODEL, nm_cfg, None, cand.CAM).boxes
        return lambda stem, frame: cmb.box_union(frame, cand.MODEL, None, cfg, cand.CAM).boxes
    return fit


def key(boxes) -> list:
    return [[int(b.color), *(int(v) for v in b.bbox)] for b in boxes]


def judged_runs() -> None:
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    stems = ordinary + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    truth = jg.load_truth(stems)
    dets = {"fixed": jg.fixed_detector()}
    for name in NAMES:
        fit = cand.FITS[name]
        dets[name] = jg.leave_one_place_out(fit, ordinary, getattr(fit, "describe", name))
    for w in WINNERS:
        dets[f"check_{w}"] = jg.leave_one_place_out(check_fit(w), ordinary, f"{w} alone, from barrels.combined (a check, never judged)")
    t0 = time.time()
    runs = jg.run_many(dets, stems, truth)
    print(f"ran {len(dets)} detectors on {len(stems)} train frames in {time.time() - t0:.0f} s", flush=True)
    out = cb.RESULTS
    out.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        j = jg.compare(runs["fixed"], runs[name], frames, truth, lopo=True)
        jg.write(j, out / name)
        b, c = j.total
        print(f"{name:<12} {j.result:<20} found {b.found_w:.1f} -> {c.found_w:.1f} ({c.found_w - b.found_w:+.1f}), per frame {b.found} -> {c.found}, "
              f"not on barrel {b.extra_w:.2f} -> {c.extra_w:.2f}, clean empty {b.clean_empty} -> {c.clean_empty}", flush=True)
    for way in WAYS:
        for w in WINNERS:
            jg.write(jg.compare(runs[w], runs[way], frames, truth, lopo=True), out / f"{way}_vs_{w}")
    jg.write(jg.compare(runs["selfcal"], runs["nearmiss"], frames, truth, lopo=True), out / "nearmiss_vs_selfcal")
    checks = {}
    for w in WINNERS:
        bad = [s for s in stems if key(runs[w].boxes[s]) != key(runs[f"check_{w}"].boxes[s])]
        checks[w] = {"frames": len(stems), "frames_that_differ": bad}
        print(f"check: {w} alone from barrels.combined gives the winner's own boxes on {len(stems) - len(bad)} of {len(stems)} frames", flush=True)
    boxes = {n: {s: {"boxes": [[int(b.color), *(int(v) for v in b.bbox), sorted(b.flags)] for b in runs[n].boxes[s]],
                     "count": runs[n].counts[s].to_dict()} for s in stems} for n in ("fixed",) + NAMES}
    (out / "boxes.json").write_text(json.dumps(boxes) + "\n")
    chosen = {p: {"nm": c["nm"], "sc": c["sc"], "train_frames": c["_n_train"]} for p, c in cand.CHOSEN.items()}
    not_ordinary = [p for p in chosen if p not in {ct.place_of(s) for s in ordinary}]
    if not_ordinary:
        chosen[ANY] = chosen[not_ordinary[0]]
    (out / "chosen.json").write_text(json.dumps(chosen, indent=1) + "\n")
    secs = {w: {"seconds": round(v[0], 2), "frames": v[1], "ms_per_frame": round(1000 * v[0] / max(1, v[1]), 1)} for w, v in cand.SECONDS.items()}
    (out / "run_seconds.json").write_text(json.dumps({"checks": checks, "in_the_judged_run": secs}, indent=1) + "\n")


def timing() -> None:
    """Seconds per frame, every candidate with its fixed numbers, one after the other on each ordinary train frame,
    nothing cached. ``fixed`` is today's detector; every candidate's time includes its own fixed-colors pass."""
    frames = jg.train_frames()
    stems = frames[cnd.ORDINARY]
    dets = {"fixed": jg.fixed_detector(), **cand.FIXED}
    tot = {n: 0.0 for n in dets}
    for s in stems:
        frame = jg.load_frame(s)
        for n, d in dets.items():
            t0 = time.perf_counter()
            d(s, frame)
            tot[n] += time.perf_counter() - t0
    out = {n: {"ms_per_frame": round(1000 * t / len(stems), 1)} for n, t in tot.items()}
    out["_note"] = f"{len(stems)} ordinary train frames, fixed numbers, one process, nothing cached"
    (cb.RESULTS / "timing.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


# ---------------------------------------------------------------- the summary, from the pages

def _j(name: str) -> dict:
    return json.loads((cb.RESULTS / name / "judge.json").read_text())


def _row(j: dict) -> dict:
    b, c = j["total"]["baseline"], j["total"]["candidate"]
    ch = [x for x in j["changes"] if x["judged"]]
    return {"verdict": j["verdict"], "found_w": [b["found_w"], c["found_w"]], "found": [b["found"], c["found"]],
            "off_w": [b["off_w"], c["off_w"]], "missed_w": [b["missed_w"], c["missed_w"]],
            "gained": sum(1 for x in ch if x["kind"] == "gained"), "lost": sum(1 for x in ch if x["kind"] == "lost"),
            "extra_w": [b["extra_w"], c["extra_w"]], "per_frame": {k: [b[k], c[k]] for k in ("nothing", "second", "wrong")},
            "clean_empty": [b["clean_empty"], c["clean_empty"]], "cluttered_empty_w": [b["cluttered_empty_w"], c["cluttered_empty_w"]],
            "empty": [b["empty"], c["empty"]],
            "places": {p: [v["baseline"]["found_w"], v["candidate"]["found_w"], v["baseline"]["placements"], v["baseline"]["found"], v["candidate"]["found"]]
                       for p, v in j["places"].items()},
            "place_clause": next(x["text"] for x in j["clauses"] if x["key"] == "place"),
            "clauses": {x["key"]: x["state"] for x in j["clauses"]}}


def pick(rows: dict, vs: dict) -> dict:
    """PREREG.md, "Which one is the best": among the ways the judge calls PASS against today's detector, the most found;
    within 1.0 placement of it, the fewest boxes not on their barrel; within 0.25 of that, the simpler one. Then the
    question whether it is worth having both: PASS against EACH winner alone."""
    ok = [w for w in WAYS if rows[w]["verdict"] == jg.PASS]
    pool = ok or [w for w in WAYS if rows[w]["verdict"] != jg.FAIL] or list(WAYS)
    top = max(rows[w]["found_w"][1] for w in pool)
    near = [w for w in pool if rows[w]["found_w"][1] >= top - 1.0 + 1e-9]
    low = min(rows[w]["extra_w"][1] for w in near)
    near = [w for w in near if rows[w]["extra_w"][1] <= low + 0.25 + 1e-9]
    best = min(near, key=SIMPLER_FIRST.index)
    worth = all(vs[f"{best}_vs_{w}"]["verdict"] == jg.PASS for w in WINNERS)
    return {"best_combination": best, "passes_against_today": best in ok, "ways_that_pass": ok,
            "worth_having_both": worth, "against_each_winner": {w: vs[f"{best}_vs_{w}"]["verdict"] for w in WINNERS}}


def summary() -> str:
    m = jg.load_margins()
    rows = {n: _row(_j(n)) for n in NAMES}
    vs = {f"{way}_vs_{w}": _row(_j(f"{way}_vs_{w}")) for way in WAYS for w in WINNERS}
    vs["nearmiss_vs_selfcal"] = _row(_j("nearmiss_vs_selfcal"))
    timing_p = cb.RESULTS / "timing.json"
    tm = json.loads(timing_p.read_text()) if timing_p.exists() else {}
    chosen = json.loads((cb.RESULTS / "chosen.json").read_text())
    extra = json.loads((cb.RESULTS / "run_seconds.json").read_text())
    picked = pick(rows, vs)
    base = rows[NAMES[0]]

    def d(pair, f=".1f"):
        return f"{pair[1]:{f}} ({pair[1] - pair[0]:+{f}})"

    def verdict(r):
        v = r["verdict"]
        if v == jg.PASS and r["found_w"][1] - r["found_w"][0] < m.found_gain + WEAK:
            v += " (WEAK)"
        de = r["extra_w"][1] - r["extra_w"][0]
        if v.startswith(jg.PASS) and de > m.extra_rise - 1.0:
            v += f", boxes at the margin ({de:+.2f} of +{m.extra_rise:.2f})"
        return v

    def ms(n):
        return f"{tm[n]['ms_per_frame']:.0f}" if n in tm else "-"
    out = ["# The two winners together: every judged candidate (2026-11-26, TODO E8)", "",
           "Made by `experiments/2026-11-26_combined/run.py`. Train frames only (154 ordinary frames, 8 places, 172 placements; 307 barrels counted "
           "per frame). Every candidate is fitted leave one place out: in each fold each step's setting is picked by that step's own rule on the "
           "other places. Found = the strict rule. Boxes = boxes that are not on their barrel, counted once per arrangement. "
           f"Margins: found better above +{m.found_gain:.1f}, worse below -{m.found_loss:.2f}; boxes worse above +{m.extra_rise:.2f}; any new box on a clean "
           "empty frame fails; no place may drop by more than its margin.", "",
           f"Today's detector (the fixed colors): {base['found_w'][0]:.1f} of 172 placements, {base['found'][0]} of 307 per frame, "
           f"{base['extra_w'][0]:.2f} boxes not on their barrel, {base['clean_empty'][0]} on clean empty frames.", "",
           "## Against today's detector", "",
           "| candidate | verdict | found, placements | per frame | gained / lost | boxes not on their barrel | per frame: on nothing, second, wrong color | "
           "empty frames: clean, with clutter | ms per frame |", "|---|---|---|---|---|---|---|---|---|"]
    for n in NAMES:
        r = rows[n]
        pf = r["per_frame"]
        out.append(f"| `{n}` | **{verdict(r)}** | {d(r['found_w'])} | {r['found'][1]} ({r['found'][1] - r['found'][0]:+d}) | +{r['gained']} / -{r['lost']} | "
                   f"{d(r['extra_w'], '.2f')} | {pf['nothing'][1]}, {pf['second'][1]}, {pf['wrong'][1]} (today {pf['nothing'][0]}, {pf['second'][0]}, {pf['wrong'][0]}) | "
                   f"{r['clean_empty'][1]}, {r['cluttered_empty_w'][1]:.2f} | {ms(n)} |")
    out += ["", f"Today's detector alone: {ms('fixed')} ms per frame. Times: fixed numbers, one process, nothing cached (`timing.json`).", "",
            "## Each combination against each winner alone (the same judge, the winner as the baseline)", "",
            "| combination | against `nearmiss`: verdict | found | gained / lost | boxes | against `selfcal`: verdict | found | gained / lost | boxes |",
            "|---|---|---|---|---|---|---|---|---|"]
    for way in WAYS:
        a, b_ = vs[f"{way}_vs_nearmiss"], vs[f"{way}_vs_selfcal"]
        out.append(f"| `{way}` | {a['verdict']} | {d(a['found_w'])} | +{a['gained']} / -{a['lost']} | {d(a['extra_w'], '.2f')} | "
                   f"{b_['verdict']} | {d(b_['found_w'])} | +{b_['gained']} / -{b_['lost']} | {d(b_['extra_w'], '.2f')} |")
    w = vs["nearmiss_vs_selfcal"]
    out += ["", f"The two winners against each other (`nearmiss` with `selfcal` as the baseline): {w['verdict']}; found {d(w['found_w'])}; "
            f"`nearmiss` finds {w['gained']} barrels that `selfcal` does not and misses {w['lost']} that `selfcal` finds (per frame); boxes {d(w['extra_w'], '.2f')}.", "",
            "## By place: found, placements (per frame in brackets)", "",
            "| place | placements | today | " + " | ".join(f"`{n}`" for n in NAMES) + " |", "|---|---|---|" + "---|" * len(NAMES)]
    for p, v in base["places"].items():
        out.append(f"| {p} | {v[2]} | {v[0]:.1f} ({v[3]}) | " + " | ".join(f"{rows[n]['places'][p][1]:.1f} ({rows[n]['places'][p][4]})" for n in NAMES) + " |")
    out.append(f"| **all** | 172 | **{base['found_w'][0]:.1f} ({base['found'][0]})** | " + " | ".join(f"**{rows[n]['found_w'][1]:.1f} ({rows[n]['found'][1]})**" for n in NAMES) + " |")
    out += ["", "The place clause of the judge, per candidate:", ""] + [f"- `{n}`: [{rows[n]['clauses']['place']}] {rows[n]['place_clause']}" for n in NAMES]
    out += ["", "## What each winner's rule picked in each fold", "", "| held-out place | near-miss | self-calibration |", "|---|---|---|"]
    out += [f"| {p} | `{c['nm']}` | {json.dumps(c['sc']) if c['sc'] else 'the fixed detector'} |" for p, c in chosen.items()]
    out += ["", "## Checks", ""]
    for wn, c in extra["checks"].items():
        out.append(f"- `{wn}` alone, built from `barrels.combined`'s building blocks, gives the winner's own boxes on "
                   f"{c['frames'] - len(c['frames_that_differ'])} of {c['frames']} frames." + (f" DIFFERENT: {c['frames_that_differ'][:5]}" if c["frames_that_differ"] else ""))
    out += ["", "## The pick (the rule is in PREREG.md)", "",
            f"- Ways the judge calls PASS against today's detector: {', '.join('`' + x + '`' for x in picked['ways_that_pass']) or 'none'}.",
            f"- The best combination by the rule: `{picked['best_combination']}`" + ("" if picked["passes_against_today"] else " (it does NOT pass against today's detector)") + ".",
            f"- Is it worth having both? Against each winner alone: " + ", ".join(f"`{k}` {v}" for k, v in picked["against_each_winner"].items()) +
            f". So: {'yes' if picked['worth_having_both'] else 'NO: by the registered rule one winner is enough'}."]
    (cb.RESULTS / "summary.json").write_text(json.dumps({"against_today": rows, "against_winners": vs, "picked": picked, "timing": tm}, indent=1) + "\n")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--summary", action="store_true", help="only write summary.md again from the pages that exist")
    ap.add_argument("--timing", action="store_true", help="only the seconds per frame")
    a = ap.parse_args(argv)
    if a.timing:
        timing()
        return 0
    if not a.summary:
        judged_runs()
        timing()
    text = summary()
    (cb.RESULTS / "summary.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
