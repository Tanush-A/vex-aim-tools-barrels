#!/usr/bin/env python3
"""Step C of 2026-11-26_bottom: every candidate rule for the bottom edge, judged two ways (plan: PREREG.md).

    python barrels/experiments/2026-11-26_bottom/run.py [--jobs 8]

Today's detector and the candidates (``CANDS``; DetConfig fields, all off by default) are run on the SAME masks: the six
color steps of ``lib.PAINT`` on every ordinary train frame, and on the extreme ones (reported, never judged).

1. the fixed colors: each candidate against today's default (what ``tools/judge.py --cand-det`` does);
2. each "more paint" color step: the candidate against today's detector on the same masks.

Every comparison is ``judge.compare`` (the standard pass rule, the stored margins). Beside it: the yardstick (boxes on
their barrel that fail the strict rule with the bottom edge as the cause) and the bottom-edge error against the labels.
Then the five conditions of the PREREG and the recommendation they give.

Train frames only (``judge.load_frame`` refuses anything else).
Outputs: results/2026-11-26_bottom/summary.md, summary.json, judge/<step>_<candidate>/, sheets/changed_<candidate>.png.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402
from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import cv as bcv  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import eval_det as ed  # noqa: E402
from barrels import judge as jg  # noqa: E402

CANDS = {"low": {"bottom_rule": "low"}, "both": {"bottom_rule": "both"}, "predicted": {"bottom_rule": "predicted"},
         "rows": {"bottom_rows": 0.5}, "rows+low": {"bottom_rows": 0.5, "bottom_rule": "low"}}
ARMS = {"today": {}, **CANDS}
MORE = lib.PAINT[1:]            # the five "more paint" color steps
_HAND_STEMS: list = []


def setting(name: str) -> str:
    return ",".join(f"{k}={v}" for k, v in ARMS[name].items()) or "defaults"


def _init(hand_stems):
    import cv2
    cv2.setNumThreads(1)
    _HAND_STEMS[:] = hand_stems


def one_frame(stem: str) -> tuple[str, dict]:
    """Every arm on every color step of one frame -> {step: {arm: [boxes]}}. A mask seen before on this frame (the hand
    step where the condition has no hand thresholds) is not detected again."""
    frame = jg.load_frame(stem)
    cfgs = {a: dataclasses.replace(det.DetConfig(), **ov) for a, ov in ARMS.items()}
    seen, out = {}, {}
    for level, mask in lib.masks_for(stem, frame, _HAND_STEMS).items():
        h = hashlib.blake2b(mask.tobytes(), digest_size=16).digest()
        if h not in seen:
            seen[h] = {a: [lib.box_dict(b) for b in det.detect(mask, cfg, lib.CAM)] for a, cfg in cfgs.items()}
        out[level] = seen[h]
    return stem, out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()
    lib.OUT.mkdir(parents=True, exist_ok=True)
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    extra = frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    stems = ordinary + extra
    hand_stems = [s for v in frames.values() for s in v]
    truth = jg.load_truth(stems)
    margins = jg.load_margins()
    with Pool(args.jobs, initializer=_init, initargs=(hand_stems,)) as pool:
        res = dict(pool.imap_unordered(one_frame, stems, chunksize=2))

    # ---- one Run per (color step, arm); the pairing of boxes and barrels kept beside it
    runs: dict = {lv: {} for lv in lib.PAINT}
    pairs: dict = {lv: {a: {} for a in ARMS} for lv in lib.PAINT}          # step -> arm -> stem -> {barrel: box index}
    preds: dict = {lv: {a: {} for a in ARMS} for lv in lib.PAINT}
    for lv in lib.PAINT:
        for a in ARMS:
            r = jg.Run(f"{a} [{lv}]", f"{lib.PAINT_TEXT[lv]}; DetConfig {setting(a)}")
            for s in stems:
                ps = [lib.as_barrel(b) for b in res[s][lv][a]]
                fc, pair = lib.pair_frame(s, ps, truth.gts[s], truth.clean[s])
                r.boxes[s], r.counts[s] = ps, fc
                pairs[lv][a][s], preds[lv][a][s] = pair, ps
            runs[lv][a] = r

    def yard(lv: str, a: str, which: list[str]) -> dict:
        """The yardstick: "box off" barrels whose box fails the strict rule with the bottom edge as the cause."""
        n = Counter()
        for s in which:
            fc = runs[lv][a].counts[s]
            for gi, st in enumerate(fc.gt):
                if st == ct.OFF:
                    p, g = preds[lv][a][s][pairs[lv][a][s][gi]], truth.gts[s][gi]
                    why = lib.why_off(p, g)
                    n["other" if why == "other" else ("low" if p.bottom_row > g.bottom_row else "high")] += 1
        return {"low": n["low"], "high": n["high"], "bottom": n["low"] + n["high"], "other": n["other"]}

    def errors(lv: str, a: str, keys) -> dict:
        """Bottom-edge error of the boxes of arm ``a`` on the true barrels ``keys`` [(stem, barrel)], near and far."""
        out = {}
        for name, sel in (("near", True), ("far", False)):
            px, fr, bad = [], [], 0
            for s, gi in keys:
                g = truth.gts[s][gi]
                if lib.is_near(g) != sel:
                    continue
                e_px, e_fr = lib.bottom_err(preds[lv][a][s][pairs[lv][a][s][gi]], g)
                px.append(e_px); fr.append(e_fr); bad += abs(e_px) > ed.bottom_tol_px(g)
            out[name] = {"px": lib.stat(px), "frac": lib.stat(fr), "outside": bad / max(1, len(px))}
        return out

    def on_keys(lv: str, a: str) -> set:
        return {(s, gi) for s in ordinary for gi in pairs[lv][a][s] if lib.measurable(truth.gts[s][gi])}

    S: dict = {"git": bcv.git_hash(), "frames": {"ordinary": len(ordinary), "report_only": len(extra)}, "arms": {a: setting(a) for a in ARMS},
               "steps": {}, "criteria": {}}
    J: dict = {}
    for lv in lib.PAINT:
        S["steps"][lv] = {}
        for a in ARMS:
            t = ct.tally(runs[lv][a].counts, ordinary, truth.placements)
            te = ct.tally(runs[lv][a].counts, extra, truth.placements)
            d = {"found_w": t.found_w, "found": t.found, "off": t.off, "off_w": t.off_w, "missed": t.missed, "extra": t.extra, "extra_w": t.extra_w,
                 "empty": t.empty, "clean_empty": t.clean_empty, "placements": t.placements, "barrels": t.barrels,
                 "yard": yard(lv, a, ordinary), "own_err": errors(lv, a, on_keys(lv, a)),
                 "report_only": {"found_w": te.found_w, "found": te.found, "barrels": te.barrels, "placements": te.placements, "off": te.off,
                                 "extra": te.extra, "yard": yard(lv, a, extra)}}
            if a != "today":
                j = jg.compare(runs[lv]["today"], runs[lv][a], frames, truth, margins)
                jg.write(j, lib.OUT / "judge" / f"{lv}_{a.replace('+', '_')}")
                J[(lv, a)] = j
                judged = [c for c in j.changes if c.judged]
                common = on_keys(lv, "today") & on_keys(lv, a)
                moved = sum(1 for s, gi in common if preds[lv]["today"][s][pairs[lv]["today"][s][gi]].bbox[3] != preds[lv][a][s][pairs[lv][a][s][gi]].bbox[3])
                d.update(verdict=j.result, reason=j.verdict.reason, clauses=[f"[{c.state}] {c.text}" for c in j.verdict.clauses],
                         gained=[jg._box(c) for c in judged if c.kind == "gained"], lost=[jg._box(c) for c in judged if c.kind == "lost"],
                         other=[jg._box(c) for c in judged if c.kind == "other"],
                         common={"n": len(common), "bottoms_moved": moved, "today": errors(lv, "today", common), "cand": errors(lv, a, common)})
            S["steps"][lv][a] = d

    # ---- the five conditions of the PREREG
    def total(a: str, key) -> float:
        return sum(key(S["steps"][lv][a]) for lv in MORE)
    base_c, base_d = total("today", lambda d: d["yard"]["bottom"]), total("today", lambda d: d["found_w"])
    works = []
    for a in CANDS:
        fx = S["steps"]["fixed"][a]
        c, dsum = total(a, lambda d: d["yard"]["bottom"]), total(a, lambda d: d["found_w"])
        e = {n: (fx["common"]["today"][n]["px"]["med"], fx["common"]["cand"][n]["px"]["med"]) for n in ("near", "far")}
        crit = {"a": fx["verdict"] != jg.FAIL, "b": all(S["steps"][lv][a]["verdict"] != jg.FAIL for lv in MORE), "c": c < base_c, "d": dsum > base_d + 1e-9,
                "e": all(cand <= today + 0.5 + 1e-9 for today, cand in e.values())}
        S["criteria"][a] = {"met": crit, "works": all(crit.values()), "yard_sum": c, "yard_sum_today": base_c, "found_sum": dsum, "found_sum_today": base_d,
                            "fixed_median_px": e, "verdicts": {lv: S["steps"][lv][a]["verdict"] for lv in lib.PAINT}}
        if all(crit.values()):
            works.append(a)
    order = list(CANDS)
    best = min(works, key=lambda a: (S["criteria"][a]["yard_sum"], -S["criteria"][a]["found_sum"], order.index(a))) if works else None
    S["works"], S["recommended"] = works, best
    (lib.OUT / "summary.json").write_text(json.dumps(S, indent=1) + "\n")

    # ---- the page
    def pct(x: float) -> str:
        return f"{100 * x:.1f}"

    def err_cell(e: dict) -> str:
        return f"{e['px']['med']:.1f} / {e['px']['p90']:.1f} px, {pct(e['frac']['med'])} / {pct(e['frac']['p90'])} %, {pct(e['outside'])} % out"
    L = [f"# The bottom edge: every candidate, judged two ways ({bcv.git_hash()})", "",
         "`python barrels/experiments/2026-11-26_bottom/run.py` (plan: `../../experiments/2026-11-26_bottom/PREREG.md`; the yardstick alone: `yardstick.md`). "
         f"{len(ordinary)} ordinary train frames ({S['steps']['fixed']['today']['placements']} placements, {S['steps']['fixed']['today']['barrels']} barrels); "
         f"{len(extra)} extreme frames reported, never judged. Test frames never opened. Every verdict is `judge.compare` with the stored margins "
         "(found better above +4.0 placements, worse below -10.9; boxes not on their barrel worse above +1.85).", "",
         "The candidates (all off by default):", ""] + [f"- `{a}`: `--cand-det {setting(a)}`" for a in CANDS] + ["",
         "The color steps:", ""] + [f"- `{lv}`: {lib.PAINT_TEXT[lv]}" for lv in lib.PAINT] + ["",
         "## 1. Every candidate at every color step, against today's detector on the same masks", "",
         "`fixed` is judgement 1 of the PREREG (the candidate against today's default). The five others are judgement 2. "
         "yardstick = boxes that are on their barrel and fail the strict rule with the bottom edge as the cause, per frame (too low / too high). "
         "Found per placement, with the change; per frame in brackets.", "",
         "| color step | arm | found, placements | found, per frame | box off | **yardstick** (low / high) | boxes not on their barrel, per arrangement | on clean empty frames | gained / lost | verdict |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for lv in lib.PAINT:
        b = S["steps"][lv]["today"]
        for a in ARMS:
            d = S["steps"][lv][a]
            dv = "" if a == "today" else f" ({d['found_w'] - b['found_w']:+.1f})"
            L.append(f"| `{lv}` | `{a}` | {d['found_w']:.1f}{dv} | {d['found']} | {d['off']} | **{d['yard']['bottom']}** ({d['yard']['low']} / {d['yard']['high']}) | "
                     f"{d['extra_w']:.1f} ({d['extra']}) | {d['clean_empty']} | " + ("" if a == "today" else f"{len(d['gained'])} / {len(d['lost'])}") + " | "
                     + ("" if a == "today" else f"**{d['verdict']}**") + " |")
    L += ["", "## 2. The five conditions of the PREREG", "",
          f"Today: the yardstick summed over the five \"more paint\" steps = {base_c}; found summed over them = {base_d:.1f} placements.", "",
          "| candidate | (a) fixed colors not FAIL | (b) no FAIL on the five steps | (c) yardstick sum lower | (d) found sum higher | (e) fixed colors: median bottom error, near / far, today -> candidate | works |",
          "|---|---|---|---|---|---|---|"]
    for a in CANDS:
        c = S["criteria"][a]
        m, e = c["met"], c["fixed_median_px"]
        yes = lambda k: "yes" if m[k] else "**no**"  # noqa: E731
        L.append(f"| `{a}` | {yes('a')} ({c['verdicts']['fixed']}) | {yes('b')} | {yes('c')} ({c['yard_sum']} against {base_c}) | "
                 f"{yes('d')} ({c['found_sum']:.1f} against {base_d:.1f}, {c['found_sum'] - base_d:+.1f}) | "
                 f"{yes('e')} ({e['near'][0]:.1f} -> {e['near'][1]:.1f} px / {e['far'][0]:.1f} -> {e['far'][1]:.1f} px) | {'**yes**' if c['works'] else 'no'} |")
    L += ["", f"**Recommended by the PREREG's rule: {'`' + best + '` (`--cand-det ' + setting(best) + '`)' if best else 'none (no candidate meets all five)'}.**", "",
          "## 3. The bottom-edge error against the labels, before and after", "",
          "The box's bottom row minus the true one, on the barrels that have a box on them in BOTH arms and a measurable true bottom (inside the "
          f"frame, not flagged `bottom_estimated`). near = a true box at least {lib.NEAR_H} px tall. Each cell: median / 90th percentile of the "
          "absolute error in px, the same in % of the true height, and the share outside the scorer's tolerance. \"moved\" = boxes whose bottom "
          "row differs between the two arms.", "",
          "| color step | candidate | barrels (moved) | near: today | near: candidate | far: today | far: candidate |", "|---|---|---|---|---|---|---|"]
    for lv in lib.PAINT:
        for a in CANDS:
            c = S["steps"][lv][a]["common"]
            L.append(f"| `{lv}` | `{a}` | {c['n']} ({c['bottoms_moved']}) | {err_cell(c['today']['near'])} | {err_cell(c['cand']['near'])} | "
                     f"{err_cell(c['today']['far'])} | {err_cell(c['cand']['far'])} |")
    L += ["", "Each arm on its own boxes (every box that is on a barrel with a measurable bottom; the sets differ a little between arms):", "",
          "| color step | arm | near: boxes, error | far: boxes, error |", "|---|---|---|---|"]
    for lv in lib.PAINT:
        for a in ARMS:
            o = S["steps"][lv][a]["own_err"]
            L.append(f"| `{lv}` | `{a}` | {o['near']['px']['n']}: {err_cell(o['near'])} | {o['far']['px']['n']}: {err_cell(o['far'])} |")
    L += ["", "## 4. The extreme conditions (report only, never judged)", "",
          "| color step | arm | found, placements | found, per frame | box off | yardstick (low / high) | boxes not on their barrel |", "|---|---|---|---|---|---|---|"]
    for lv in lib.PAINT:
        for a in ARMS:
            d = S["steps"][lv][a]["report_only"]
            L.append(f"| `{lv}` | `{a}` | {d['found_w']:.1f} of {d['placements']} | {d['found']} of {d['barrels']} | {d['off']} | "
                     f"{d['yard']['bottom']} ({d['yard']['low']} / {d['yard']['high']}) | {d['extra']} |")
    L += ["", "## 5. Every barrel that changed (ordinary frames)", ""]
    for a in CANDS:
        L += [f"### `{a}`", ""]
        for lv in lib.PAINT:
            d = S["steps"][lv][a]
            if d["gained"] or d["lost"] or d["other"]:
                L += [f"- `{lv}`: " + "; ".join([f"+ {x}" for x in d["gained"]] + [f"- {x}" for x in d["lost"]] + [f"~ {x}" for x in d["other"]])]
            else:
                L += [f"- `{lv}`: nothing changed"]
        L.append("")
    L += ["Files: `summary.json` (every number), `judge/<step>_<candidate>/judge.md` (the full judgement of each comparison), "
          "`sheets/changed_<candidate>.png` (every barrel whose state changed: white = the true box, red = today's box, green = the candidate's).", ""]
    (lib.OUT / "summary.md").write_text("\n".join(L))

    # ---- contact sheets: every barrel whose state changed, per candidate
    for a in CANDS:
        items = [(lv, c) for lv in lib.PAINT for c in J[(lv, a)].changes if c.judged]
        items.sort(key=lambda t: (t[1].stem, t[1].index, lib.PAINT.index(t[0])))
        panels, cache = [], {}
        for lv, c in items:
            s, gi = c.stem, c.index
            if s not in cache:
                fr = jg.load_frame(s)
                cache = {s: (fr.bgr, lib.masks_for(s, fr, hand_stems))}
            bgr, masks = cache[s]
            g = truth.gts[s][gi]
            boxes, txt = [], [f"{s.replace('4A8B_', '')} #{gi + 1} {c.color} [{lv}]: {c.before} -> {c.after}"]
            line = []
            for arm, col in (("today", (0, 0, 255)), (a, (0, 200, 0))):
                if gi in pairs[lv][arm][s]:
                    p = preds[lv][arm][s][pairs[lv][arm][s][gi]]
                    boxes.append((p.bbox, col))
                    line.append(f"{arm}: bottom {p.bottom_row - g.bottom_row:+d} px, IoU {ed.box_iou(p.bbox, g.bbox):.2f}")
                else:
                    line.append(f"{arm}: no box on it")
            txt.append("; ".join(line) + f" (tol {ed.bottom_tol_px(g):.1f})")
            panels.append(lib.panel(bgr, masks[lv], g.bbox, boxes, txt))
        if panels:
            lib.sheet(panels, lib.OUT / "sheets" / f"changed_{a.replace('+', '_')}.png")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
