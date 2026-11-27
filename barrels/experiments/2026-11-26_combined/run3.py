#!/usr/bin/env python3
"""ADDENDUM 2026-11-27 of experiment 2026-11-26_combined: the judged runs with the third winner (contrast).

    python barrels/experiments/2026-11-26_combined/cn_picks.py     # first: contrast reproduces, and its picks per fold
    python barrels/experiments/2026-11-26_combined/run3.py         # then this (about 20 minutes)
    python barrels/experiments/2026-11-26_combined/run3.py --summary

Run with ``PYTHONPATH=barrels/src``. Train frames only. One pass over the 231 train frames (ordinary and report-only):
today's detector, contrast alone (from ``barrels.combined``'s blocks, with contrast's own fold picks), ``mask_union``
again, and the six three-way candidates (``barrels.combined.WAYS3``), each fitted leave one place out. Then the standard
pass rule (``judge.compare``):

- every candidate against today's detector (the verdict);
- every candidate against CONTRAST ALONE (is anything worth adding to it?), and the two other winners and
  ``mask_union`` against contrast alone (which single method does most of the work?).

Checks, never judged: contrast alone from ``barrels.combined`` gives exactly contrast's own judged pages
(``repro_contrast/``); ``mask_union`` gives exactly its boxes of the first judged run (``boxes.json``).

Writes results/2026-11-26_combined/: ``<name>/`` and ``<name>_vs_contrast/`` (judge pages), the new detectors' boxes
added to ``boxes.json``, ``timing3.json``, ``summary3.md``, ``summary3.json``.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cb_common as cb  # noqa: E402
from jdiff import KEYS, diff, norm  # noqa: E402

cand = cb._load("cb_candidates", cb.HERE / "candidates.py")

from barrels import combined as cmb  # noqa: E402
from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels.detect_types import Barrel  # noqa: E402

NEW = tuple(cmb.WAYS3)                      # cn_alone and the six combinations
SIMPLER_FIRST = ("cn_box_sc", "cn_box_nm", "cn_on_sc", "cn_on_nm", "cn_box_all", "cn_on_all")      # PREREG addendum: the order of a tie
OLD = ("nearmiss", "selfcal", "mask_union")
WEAK = 2.0


def stored_run(name: str, stems) -> jg.Run:
    """A detector of the first judged run, read back from boxes.json (its held-out boxes and their states)."""
    raw = json.loads((cb.RESULTS / "boxes.json").read_text())[name]
    r = jg.Run(name, f"{name} (the first judged run, read back from boxes.json)")
    for s in stems:
        r.boxes[s] = [Barrel(color=b[0], bbox=tuple(b[1:5]), flags=frozenset(b[5])) for b in raw[s]["boxes"]]
        r.counts[s] = ct.FrameCount.from_dict(raw[s]["count"])
    return r


def key(boxes) -> list:
    return [[int(b.color), *(int(v) for v in b.bbox)] for b in boxes]


def judged_runs() -> None:
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    stems = ordinary + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    truth = jg.load_truth(stems)
    dets = {"fixed": jg.fixed_detector(), "mask_union_again": jg.leave_one_place_out(cand.FITS["mask_union"], ordinary, "mask_union, run again (a check)")}
    for w in NEW:
        dets[w] = jg.leave_one_place_out(cand.FITS3[w], ordinary, cand.FITS3[w].describe)
    t0 = time.time()
    runs = jg.run_many(dets, stems, truth)
    print(f"ran {len(dets)} detectors on {len(stems)} train frames in {time.time() - t0:.0f} s", flush=True)
    for n in OLD:
        runs[n] = stored_run(n, stems)
    out = cb.RESULTS
    checks = {}
    bad = [s for s in stems if key(runs["mask_union_again"].boxes[s]) != key(runs["mask_union"].boxes[s])]
    checks["mask_union run again gives the boxes of the first run"] = {"frames": len(stems), "frames_that_differ": bad}
    for w in NEW:
        j = jg.compare(runs["fixed"], runs[w], frames, truth, lopo=True)
        jg.write(j, out / w)
        b, c = j.total
        print(f"{w:<12} {j.result:<20} found {b.found_w:.1f} -> {c.found_w:.1f} ({c.found_w - b.found_w:+.1f}), per frame {b.found} -> {c.found}, "
              f"not on barrel {b.extra_w:.2f} -> {c.extra_w:.2f}, clean empty {b.clean_empty} -> {c.clean_empty}", flush=True)
        if w == "cn_alone":
            now, ref = norm(jg.to_json(j)), json.loads((out / "repro_contrast" / "judge.json").read_text())
            d = [x for k in KEYS for x in diff(now[k], ref[k], k)]
            checks["contrast alone from barrels.combined gives contrast's own judged pages"] = {"differences": d[:20], "n": len(d)}
    for n in [w for w in NEW if w != "cn_alone"] + list(OLD):
        jg.write(jg.compare(runs["cn_alone"], runs[n], frames, truth, lopo=True), out / f"{n}_vs_contrast")
    raw = json.loads((out / "boxes.json").read_text())
    for w in NEW:
        raw[w] = {s: {"boxes": [[int(b.color), *(int(v) for v in b.bbox), sorted(b.flags)] for b in runs[w].boxes[s]],
                      "count": runs[w].counts[s].to_dict()} for s in stems}
    (out / "boxes.json").write_text(json.dumps(raw) + "\n")
    secs = {w: {"ms_per_frame_in_the_judged_run": round(1000 * v[0] / max(1, v[1]), 1), "frames": v[1]} for w, v in cand.SECONDS.items()}
    (out / "run3_checks.json").write_text(json.dumps({"checks": checks, "in_the_judged_run": secs}, indent=1) + "\n")
    for k, v in checks.items():
        print(f"check: {k}: {v}", flush=True)


def timing() -> None:
    frames = jg.train_frames()
    stems = frames[cnd.ORDINARY]
    dets = {"fixed": jg.fixed_detector(), **cand.FIXED3}
    tot = {n: 0.0 for n in dets}
    for s in stems:
        frame = jg.load_frame(s)
        for n, d in dets.items():
            t0 = time.perf_counter()
            d(s, frame)
            tot[n] += time.perf_counter() - t0
    out = {n: {"ms_per_frame": round(1000 * t / len(stems), 1)} for n, t in tot.items()}
    out["_note"] = f"{len(stems)} ordinary train frames, fixed numbers, one process, nothing cached"
    (cb.RESULTS / "timing3.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


# ---------------------------------------------------------------- the summary

def _row(name: str) -> dict:
    j = json.loads((cb.RESULTS / name / "judge.json").read_text())
    b, c = j["total"]["baseline"], j["total"]["candidate"]
    ch = [x for x in j["changes"] if x["judged"]]
    return {"verdict": j["verdict"], "found_w": [b["found_w"], c["found_w"]], "found": [b["found"], c["found"]],
            "gained": sum(1 for x in ch if x["kind"] == "gained"), "lost": sum(1 for x in ch if x["kind"] == "lost"),
            "extra_w": [b["extra_w"], c["extra_w"]], "per_frame": [c["nothing"], c["second"], c["wrong"]],
            "clean_empty": [b["clean_empty"], c["clean_empty"]], "cluttered_empty_w": [b["cluttered_empty_w"], c["cluttered_empty_w"]],
            "places": {p: [v["baseline"]["found_w"], v["candidate"]["found_w"], v["baseline"]["placements"], v["candidate"]["found"]] for p, v in j["places"].items()},
            "clauses": {x["key"]: x["state"] for x in j["clauses"]}}


def pick(today: dict, vs: dict) -> dict:
    """The addendum's rule: contrast alone is the answer, unless a combination is PASS against today's detector AND
    PASS against contrast alone. Among those: the most found; within 1.0 placement, the fewest boxes not on their
    barrel; within 0.25 box, the simpler one (``SIMPLER_FIRST``)."""
    combos = [w for w in NEW if w != "cn_alone"]
    better = [w for w in combos if today[w]["verdict"] == jg.PASS and vs[w]["verdict"] == jg.PASS]
    if not better:
        return {"answer": "cn_alone", "combinations_better_than_contrast_alone": [], "why": "no combination is PASS against contrast alone"}
    top = max(today[w]["found_w"][1] for w in better)
    near = [w for w in better if today[w]["found_w"][1] >= top - 1.0 + 1e-9]
    low = min(today[w]["extra_w"][1] for w in near)
    near = [w for w in near if today[w]["extra_w"][1] <= low + 0.25 + 1e-9]
    return {"answer": min(near, key=SIMPLER_FIRST.index), "combinations_better_than_contrast_alone": better, "why": "PASS against today and against contrast alone"}


def summary() -> str:
    m = jg.load_margins()
    old = json.loads((cb.RESULTS / "summary.json").read_text())["against_today"]
    today = {w: _row(w) for w in NEW}
    for n in OLD:
        today[n] = old[n]
    vs = {n: _row(f"{n}_vs_contrast") for n in [w for w in NEW if w != "cn_alone"] + list(OLD)}
    tm = json.loads((cb.RESULTS / "timing3.json").read_text()) if (cb.RESULTS / "timing3.json").exists() else {}
    tm_old = json.loads((cb.RESULTS / "timing.json").read_text())
    ms = {**{k: v["ms_per_frame"] for k, v in tm_old.items() if isinstance(v, dict)}, **{k: v["ms_per_frame"] for k, v in tm.items() if isinstance(v, dict)}}
    checks = json.loads((cb.RESULTS / "run3_checks.json").read_text())["checks"]
    pk = pick(today, vs)
    names = ["cn_alone", "nearmiss", "selfcal", "mask_union"] + [w for w in NEW if w != "cn_alone"]

    def d(pair, f=".1f"):
        return f"{pair[1]:{f}} ({pair[1] - pair[0]:+{f}})"

    def verdict(r):
        v = r["verdict"]
        if v == jg.PASS and r["found_w"][1] - r["found_w"][0] < m.found_gain + WEAK:
            v += " (WEAK)"
        if v.startswith(jg.PASS) and r["extra_w"][1] - r["extra_w"][0] > m.extra_rise - 1.0:
            v += f", boxes at the margin ({r['extra_w'][1] - r['extra_w'][0]:+.2f} of +{m.extra_rise:.2f})"
        return v
    out = ["# Addendum 2026-11-27: the third winner (contrast) with the other two", "",
           "Made by `experiments/2026-11-26_combined/run3.py`. Train frames only; every candidate leave one place out, each component's setting picked "
           "by that component's own rule on the other places. `nearmiss`, `selfcal` and `mask_union` are the held-out boxes of the first judged run "
           f"(`summary.md`). Margins: found better above +{m.found_gain:.1f}, worse below -{m.found_loss:.2f}; boxes worse above +{m.extra_rise:.2f}.", "",
           "## Against today's detector (133.8 of 172 placements, 211 of 307 per frame, 1.93 boxes not on their barrel)", "",
           "| candidate | verdict | found, placements | per frame | gained / lost | boxes not on their barrel | per frame: on nothing, second, wrong | empty frames: clean, with clutter | ms per frame |",
           "|---|---|---|---|---|---|---|---|---|"]
    for n in names:
        r = today[n]
        pf = r["per_frame"] if isinstance(r["per_frame"], list) else [r["per_frame"]["nothing"][1], r["per_frame"]["second"][1], r["per_frame"]["wrong"][1]]
        out.append(f"| `{n}` | **{verdict(r)}** | {d(r['found_w'])} | {r['found'][1]} ({r['found'][1] - r['found'][0]:+d}) | +{r['gained']} / -{r['lost']} | "
                   f"{d(r['extra_w'], '.2f')} | {pf[0]}, {pf[1]}, {pf[2]} | {r['clean_empty'][1]}, {r['cluttered_empty_w'][1]:.2f} | {ms.get(n, '-')} |")
    out += ["", f"Today's detector alone: {ms.get('fixed', '-')} ms per frame.", "",
            "## Against CONTRAST ALONE (the same judge, contrast alone as the baseline): is anything worth adding to it?", "",
            "| candidate | verdict | found, placements | per frame | gained / lost (per frame) | boxes not on their barrel |", "|---|---|---|---|---|---|"]
    for n in [w for w in NEW if w != "cn_alone"] + list(OLD):
        r = vs[n]
        out.append(f"| `{n}` | {r['verdict']} | {d(r['found_w'])} | {r['found'][1]} ({r['found'][1] - r['found'][0]:+d}) | +{r['gained']} / -{r['lost']} | {d(r['extra_w'], '.2f')} |")
    places = list(today["cn_alone"]["places"])
    out += ["", "## By place: found, placements (per frame)", "", "| place | placements | today | " + " | ".join(f"`{n}`" for n in names) + " |",
            "|---|---|---|" + "---|" * len(names)]
    for p in places:
        base = today["cn_alone"]["places"][p]
        cells = []
        for n in names:
            v = today[n]["places"][p]
            cells.append(f"{v[1]:.1f} ({v[3] if len(v) == 4 else v[4]})")
        out.append(f"| {p} | {base[2]} | {base[0]:.1f} | " + " | ".join(cells) + " |")
    out += ["", "## Checks", ""] + [f"- {k}: " + (f"{v['n']} difference(s)" if "n" in v else f"{v['frames'] - len(v['frames_that_differ'])} of {v['frames']} frames identical")
                                     for k, v in checks.items()]
    out += ["", "## The pick (the addendum's rule)", "",
            f"- Combinations that are PASS against today's detector AND against contrast alone: {', '.join('`' + x + '`' for x in pk['combinations_better_than_contrast_alone']) or 'none'}.",
            f"- The answer: `{pk['answer']}` ({pk['why']})."]
    (cb.RESULTS / "summary3.json").write_text(json.dumps({"against_today": today, "against_contrast": vs, "pick": pk, "ms": ms}, indent=1) + "\n")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--timing", action="store_true")
    a = ap.parse_args(argv)
    if a.timing:
        timing()
        return 0
    if not a.summary:
        judged_runs()
        timing()
    text = summary()
    (cb.RESULTS / "summary3.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
