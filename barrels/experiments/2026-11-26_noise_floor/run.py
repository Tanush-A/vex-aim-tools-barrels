#!/usr/bin/env python3
"""The noise floor of the counts (2026-11-26, TODO M2; plan: PREREG.md in this folder, with its addendum). How much
do the counts move under a change that means nothing? The answer is written as the margins of the never-regress
check and of the standard pass rule (``results/baseline/margins.json``).

    python barrels/experiments/2026-11-26_noise_floor/run.py [--jobs 8]

Train frames only: every frame comes from ``judge.train_frames`` and ``judge.run_many`` refuses anything else before
an image is opened. Re-run it whenever the default color model or the default detector changes.

- Set A: the 14 one-step neighbours of the fixed color model (each hue edge -1 / +1, each saturation floor -3 / +3,
  the brightness floor -2 / +2).
- Set B: 12 seeded joint moves, each of the seven numbers moved by -1, 0 or +1 step at once.
- Set C: 12 more joint moves with another seed. A check only: no margin is ever taken from it.

For every neighbour, the change against the fixed model in found, in boxes that are not on their barrel and in boxes
on empty frames, per condition, per place, per protected set and over the ordinary conditions together; then the
median, the 90th percentile and the maximum of the absolute change.

The margins. As first registered (PREREG rule 1): the largest absolute change in set A, at least one unit; rule 3
widens them to sets A and B when more than 2 joint moves break them. As used (the addendum): the same, but one margin
per direction, because the changes turned out one-sided: a gain is compared with the largest gain, a loss with the
largest loss. Both are stored.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import random
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

BARRELS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BARRELS / "src"))
from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import cv as bcv  # noqa: E402
from barrels import gate as gt  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import hsrange as hx  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import report as rp  # noqa: E402

OUT = BARRELS / "results" / "2026-11-26_noise_floor"
NUMBERS = tuple(hx.THRESHOLDS) + ("v_min",)             # orange_h_lo, orange_h_hi, orange_s_lo, blue_h_lo, blue_h_hi, blue_s_lo, v_min
STEP = {n: (3 if n.endswith("s_lo") else 2 if n == "v_min" else 1) for n in NUMBERS}
SEED_B, SEED_C, N_JOINT = 20261126, 20261127, 12
FLOOR = 1.0
METRICS = ("found", "found_w", "any_w", "extra", "extra_w", "nothing", "nothing_w", "empty", "clean_empty", "cluttered_empty_w")


# ---------------------------------------------------------------- the neighbours

def set_a() -> dict[str, tuple]:
    """name -> the seven moves in steps: one number moved by one step, the others left."""
    out = {}
    for i, n in enumerate(NUMBERS):
        for sgn in (-1, 1):
            out[f"{n}{'+' if sgn > 0 else '-'}{STEP[n]}"] = tuple(sgn if j == i else 0 for j in range(len(NUMBERS)))
    return out


def joint(seed: int, prefix: str, taken=(), n: int = N_JOINT) -> dict[str, tuple]:
    """name -> seven moves, each -1, 0 or +1 step with equal chance; at least two numbers move; no draw twice (nor
    one that is in ``taken``)."""
    rng, out, seen = random.Random(seed), {}, set(taken)
    while len(out) < n:
        d = tuple(rng.choice((-1, 0, 1)) for _ in NUMBERS)
        if sum(x != 0 for x in d) < 2 or d in seen:
            continue
        seen.add(d)
        out[f"{prefix}{len(out) + 1:02d}"] = d
    return out


def set_b() -> dict[str, tuple]:
    return joint(SEED_B, "joint")


def set_c() -> dict[str, tuple]:
    return joint(SEED_C, "check", taken=set_b().values())


def neighbours() -> dict[str, tuple]:
    return {"fixed": (0,) * len(NUMBERS)} | set_a() | set_b() | set_c()


def fixed_numbers() -> dict:
    base = hl.adopted_model()
    return hx.flat(hl.thresholds_from_model(base)) | {"v_min": int(base.cfg.v_min)}


def values(moves: tuple, fixed: dict) -> dict:
    return {n: fixed[n] + m * STEP[n] for n, m in zip(NUMBERS, moves)}


def detector_for(moves: tuple, name: str):
    """The fixed color model with its numbers moved, and today's detector."""
    base = hl.adopted_model()
    v = values(moves, fixed_numbers())
    model = hl.model_from_thresholds(base, hx.nested({k: v[k] for k in hx.THRESHOLDS}), gates={"v_min": int(v["v_min"])})
    return jg.model_detector(model, describe=name)


_DETECTORS = None


def work(chunk: list[str]) -> dict:
    """One process, a few frames, every neighbour: name -> {stem: FrameCount}. Each image is read once."""
    import cv2
    cv2.setNumThreads(1)
    global _DETECTORS
    if _DETECTORS is None:
        _DETECTORS = {n: detector_for(m, n) for n, m in neighbours().items()}
        _DETECTORS["default file"] = jg.fixed_detector()             # the model file itself: must give what "fixed" gives
    gts, clean = ct.load_gts(chunk)
    runs = jg.run_many(_DETECTORS, chunk, jg.Truth(gts, clean, ct.Placements()))
    return {n: r.counts for n, r in runs.items()}


# ---------------------------------------------------------------- the changes and the margins

def metric(t: ct.Tally, m: str) -> float:
    return t.found_w + t.off_w if m == "any_w" else float(getattr(t, m))


def delta(base: ct.Tally, cand: ct.Tally) -> dict:
    return {m: metric(cand, m) - metric(base, m) for m in METRICS}


def dist(xs) -> dict:
    a = np.abs(np.array(list(xs), float))
    if a.size == 0:
        return {"n": 0, "median": math.nan, "p90": math.nan, "max": math.nan}
    return {"n": int(a.size), "median": float(np.median(a)), "p90": float(np.percentile(a, 90)), "max": float(a.max())}


def up(x: float) -> float:
    """Rounded up to two decimals (a margin written with fewer digits must not fall below the change it came from)."""
    return math.ceil(x * 100 - 1e-9) / 100


def rise(xs) -> float:
    """The largest rise among the changes (0 when nothing rose)."""
    return max([0.0] + [x for x in xs])


def fall(xs) -> float:
    """The largest fall among the changes, as a positive number."""
    return max([0.0] + [-x for x in xs])


def margin(x: float) -> float:
    """Never less than one whole unit; rounded up."""
    return max(FLOOR, up(x))


def make_margins(D: dict, names, levels: dict, signed: bool) -> tuple[dict, dict]:
    """(the pass rule's margins, the never-regress check's margins) from the neighbours ``names``. ``signed`` (the
    addendum): a margin per direction. Not signed (rule 1 as first registered): the largest absolute change for both."""
    def col(lv, unit, m):
        return [D[n][lv][unit][m] for n in names]

    def both(xs):
        return max(rise(xs), fall(xs))
    r, f = (rise, fall) if signed else (both, both)
    clean = up(rise(col("overall", "all train", "clean_empty")))
    judge = {"found_gain": margin(r(col("overall", "ordinary", "found_w"))), "found_loss": margin(f(col("overall", "ordinary", "found_w"))),
             "extra_rise": margin(r(col("overall", "ordinary", "extra_w"))), "extra_fall": margin(f(col("overall", "ordinary", "extra_w"))),
             "cluttered_empty": margin(r(col("overall", "ordinary", "cluttered_empty_w"))), "clean_empty": clean,
             "place": {p: margin(f(col("place", p, "found_w"))) for p in levels["place"]}, "place_default": FLOOR}
    gate = {"groups": {g: {"found": margin(f(col("protected", g, "found_w"))), "extra": margin(r(col("protected", g, "extra_w")))} for g in levels["protected"]},
            "cluttered_empty": margin(r(col("overall", "all train", "cluttered_empty_w"))), "clean_empty": clean}
    return judge, gate


def gate_fails(d_groups: dict, d_all: dict, gm: dict) -> list[str]:
    """Why a neighbour would fail the never-regress check with these margins ([] = it passes)."""
    why = [f"{g} found {d['found_w']:+.2f}" for g, d in d_groups.items() if d["found_w"] < -(gm["groups"][g]["found"] + 1e-9)]
    why += [f"{g} boxes {d['extra_w']:+.2f}" for g, d in d_groups.items() if d["extra_w"] > gm["groups"][g]["extra"] + 1e-9]
    if d_all["clean_empty"] > gm["clean_empty"] + 1e-9:
        why.append(f"clean empty frames {d_all['clean_empty']:+.0f}")
    if d_all["cluttered_empty_w"] > gm["cluttered_empty"] + 1e-9:
        why.append(f"empty frames with clutter {d_all['cluttered_empty_w']:+.2f}")
    return why


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--no-margins", action="store_true", help="do not write results/baseline/margins.json (a look, not an update)")
    args = ap.parse_args()
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    stems = sorted(s for v in frames.values() for s in v)
    truth = jg.load_truth(stems)
    A, B, C = set_a(), set_b(), set_c()
    fixed = fixed_numbers()
    print(f"{len(stems)} train frames ({len(ordinary)} ordinary); {len(A)} one-step neighbours, {len(B)} joint moves, {len(C)} check moves; {args.jobs} processes", flush=True)
    counts: dict[str, dict] = {}
    chunks = [stems[i:i + 4] for i in range(0, len(stems), 4)]
    with Pool(args.jobs) as pool:
        for i, part in enumerate(pool.imap_unordered(work, chunks)):
            for n, c in part.items():
                counts.setdefault(n, {}).update(c)
            if (i + 1) % 20 == 0:
                print(f"  {i + 1}/{len(chunks)} chunks", flush=True)
    assert counts["default file"] == counts["fixed"], "the fixed model rebuilt from its six numbers does not give the model file's boxes"
    del counts["default file"]

    protected = gt.load_protected()
    levels = {
        "condition": ct.group_stems(stems, "condition"),
        "place": ct.group_stems(ordinary, "place"),
        "protected": {g.name: [s for s in stems if rp.set_key(s) in g.sets] for g in protected},
        "overall": {"ordinary": ordinary, "all train": stems},
    }
    tallies = {n: {lv: {u: ct.tally(c, ss, truth.placements) for u, ss in units.items()} for lv, units in levels.items()} for n, c in counts.items()}
    base = tallies["fixed"]
    D = {n: {lv: {u: delta(base[lv][u], t[lv][u]) for u in levels[lv]} for lv in levels} for n, t in tallies.items() if n != "fixed"}

    def check(names, jm: dict, gm: dict) -> dict:
        m = jg.margins_from_dict(jm)
        out = {}
        for n in names:
            places = {p: (base["place"][p], tallies[n]["place"][p]) for p in levels["place"]}
            v = jg.decide(base["overall"]["ordinary"], tallies[n]["overall"]["ordinary"], places, m)
            out[n] = {"verdict": v.result, "why": v.reason if v.result != jg.NO_CLEAR else "",
                      "gate": gate_fails(D[n]["protected"], D[n]["overall"]["all train"], gm)}
        return out

    # ---- rule 1 as first registered, and rule 3 (do the joint moves break the one-step margins?)
    reg_a = make_margins(D, A, levels, signed=False)
    rule3 = check(B, *reg_a)
    b_judge = [n for n, c in rule3.items() if c["verdict"] != jg.NO_CLEAR]
    b_gate = [n for n, c in rule3.items() if c["gate"]]
    widened = len(b_judge) > 2 or len(b_gate) > 2
    names = list(A) + (list(B) if widened else [])
    registered = make_margins(D, names, levels, signed=False)           # the margins as first registered
    jm, gm = make_margins(D, names, levels, signed=True)                # the margins as used (the addendum)
    final = check(list(A) + list(B) + list(C), jm, gm)
    c_registered = check(C, *registered)
    clean_hit = [n for n in list(A) + list(B) if D[n]["overall"]["all train"]["clean_empty"] > 0]

    def table(lv: str, units, ns) -> dict:
        return {m: dist(D[n][lv][u][m] for n in ns for u in units) for m in METRICS}
    ordinary_conditions = [c for c in levels["condition"] if cnd.info(c).klass == cnd.ORDINARY]
    dists = {}
    for tag, ns in (("A", A), ("B", B), ("C", C)):
        dists[tag] = {"condition, all": table("condition", levels["condition"], ns),
                      "condition, ordinary": table("condition", ordinary_conditions, ns),
                      "place": table("place", levels["place"], ns),
                      "protected set": table("protected", levels["protected"], ns),
                      "overall, ordinary": table("overall", ["ordinary"], ns),
                      "overall, all train": table("overall", ["all train"], ns),
                      "worst place per neighbour": dist(fall(D[n]["place"][p]["found_w"] for p in levels["place"]) for n in ns)}

    OUT.mkdir(parents=True, exist_ok=True)
    made, git = dt.date.today().isoformat(), bcv.git_hash()
    tag_of = {n: t for t, ns in (("A", A), ("B", B), ("C", C)) for n in ns}
    with (OUT / "per_neighbour.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["neighbour", "set", "level", "unit"] + list(METRICS))
        for n in D:
            for lv in levels:
                for u in levels[lv]:
                    w.writerow([n, tag_of[n], lv, u] + [f"{D[n][lv][u][m]:.4f}" for m in METRICS])
    numbers = {n: values(m, fixed) for n, m in neighbours().items()}
    (OUT / "noise.json").write_text(json.dumps({
        "made": made, "git": git, "fixed": fixed, "steps": STEP, "seeds": {"B": SEED_B, "C": SEED_C}, "neighbours": numbers,
        "set_a": list(A), "set_b": list(B), "set_c": list(C),
        "frames": {k: len(v) for k, v in frames.items()}, "levels": {lv: {u: len(ss) for u, ss in units.items()} for lv, units in levels.items()},
        "fixed_tallies": {lv: {u: t.to_dict() for u, t in base[lv].items()} for lv in levels},
        "changes": D, "distributions": dists, "margins": {"judge": jm, "gate": gm},
        "margins_as_first_registered": {"judge": registered[0], "gate": registered[1]}, "margins_set_a_absolute": {"judge": reg_a[0], "gate": reg_a[1]},
        "rule3_set_b_under_set_a_margins": rule3, "widened_with_set_b": widened, "final_check": final, "set_c_under_registered_margins": c_registered,
        "clean_empty_hit_by": clean_hit}, indent=1) + "\n")
    if not args.no_margins:
        gt.MARGINS_PATH.write_text(json.dumps({
            "version": 1, "made": made, "git": git, "model_config_hash": hl.adopted_model().cfg.short_hash(),
            "source": "python barrels/experiments/2026-11-26_noise_floor/run.py (results/2026-11-26_noise_floor/summary.md)",
            "rule": "each margin = the largest change, in that direction, that a change which means nothing produced at that level, never less than one "
                    "whole unit. The changes: the fixed color model with one number moved one step (one hue unit, three saturation units, two brightness "
                    "units; 14 neighbours)" + (" and 12 seeded moves of several numbers at once (they broke the one-step margins, so they are included)" if widened else "")
                    + ". found_gain / extra_fall: the largest improvement; found_loss / extra_rise / place / groups: the largest worsening.",
            "units": "found: placements (each physical barrel once, by the share of its lights). extra / cluttered_empty: boxes, each once per arrangement. clean_empty: boxes.",
            "widened_with_set_b": widened, "judge": jm, "gate": gm,
            "as_first_registered": {"note": "PREREG rule 1 before its addendum: the largest ABSOLUTE change, the same in both directions", "judge": registered[0], "gate": registered[1]}},
            indent=1) + "\n")
    summary = write_summary(made, git, frames, levels, fixed, numbers, A, B, C, base, D, dists, reg_a, registered, jm, gm, widened, rule3, final, c_registered, clean_hit)
    (OUT / "summary.md").write_text(summary)
    print(summary)
    return 0


def f(x: float, signed: bool = True) -> str:
    if abs(x) < 5e-3:
        return "." if signed else "0"
    return (f"{x:+.2f}" if signed else f"{x:.2f}").rstrip("0").rstrip(".")


def write_summary(made, git, frames, levels, fixed, numbers, A, B, C, base, D, dists, reg_a, registered, jm, gm, widened, rule3, final, c_registered, clean_hit) -> str:
    o = base["overall"]["ordinary"]
    AB = list(A) + list(B)
    c_judge = [n for n in C if final[n]["verdict"] != jg.NO_CLEAR]
    c_gate = [n for n in C if final[n]["gate"]]
    ov = [D[n]["overall"]["ordinary"]["found_w"] for n in AB]
    L = [f"# The noise floor of the counts ({made}, git {git})", "",
         "`python barrels/experiments/2026-11-26_noise_floor/run.py` (plan: `../../experiments/2026-11-26_noise_floor/PREREG.md` and its addendum; the first run, "
         f"before the addendum: `first_run/`). Train frames only; test frames never opened. {sum(len(v) for v in frames.values())} frames; the ordinary conditions are "
         f"{len(frames[cnd.ORDINARY])} frames, {o.placements} placements ({o.barrels} barrels when every light is counted) at {len(levels['place'])} places.", "",
         "## In short", "",
         f"- **A change that means nothing moves found by up to {f(fall(ov), False)} placements down and {f(rise(ov), False)} up** over the ordinary conditions "
         f"({o.placements} placements). One number moved one step: median {f(dists['A']['overall, ordinary']['found_w']['median'], False)}, 90th percentile "
         f"{f(dists['A']['overall, ordinary']['found_w']['p90'], False)}, largest {f(dists['A']['overall, ordinary']['found_w']['max'], False)}. Several numbers at once: "
         f"median {f(dists['B']['overall, ordinary']['found_w']['median'], False)}, largest {f(dists['B']['overall, ordinary']['found_w']['max'], False)}.",
         f"- **It is one-sided.** Of the {len(AB)} neighbours, {sum(x < -5e-3 for x in ov)} lose found and {sum(x > 5e-3 for x in ov)} gain. The fixed model was picked "
         "because it scores well, so a small move mostly hurts it.",
         f"- **At one condition** (about 15 barrels): no change for most neighbours (median 0, 90th percentile {f(dists['A']['condition, ordinary']['found_w']['p90'], False)} "
         f"for one step, {f(dists['B']['condition, ordinary']['found_w']['p90'], False)} for joint moves), but up to "
         f"{f(dists['A']['condition, ordinary']['found_w']['max'], False)} barrels in the worst case.",
         f"- **At one place:** median {f(dists['A']['place']['found_w']['median'], False)}, 90th percentile {f(dists['A']['place']['found_w']['p90'], False)}, largest "
         f"{f(dists['A']['place']['found_w']['max'], False)} placements for one step (joint moves: {f(dists['B']['place']['found_w']['median'], False)} / "
         f"{f(dists['B']['place']['found_w']['p90'], False)} / {f(dists['B']['place']['found_w']['max'], False)}).",
         "- **Clean empty frames:** " + ("no neighbour of sets A and B puts a box on a clean empty frame. The zero for clean empty frames stays."
                                         if not clean_hit else f"**{', '.join(clean_hit)} put a box on a clean empty frame.** A zero there is not tenable; see the margins."),
         f"- **The check on moves the margins have never seen (set C):** {len(c_judge)} of {len(C)} get a verdict other than NO CLEAR DIFFERENCE"
         + (" (" + ", ".join(f"{n}: {final[n]['verdict']}" for n in c_judge) + ")" if c_judge else "") + f"; {len(c_gate)} of {len(C)} fail the never-regress check"
         + (" (" + "; ".join(f"{n}: {', '.join(final[n]['gate'])}" for n in c_gate) + ")" if c_gate else "") + "."
         + (" **More than 2: the margins still call changes that mean nothing.**" if len(c_judge) > 2 or len(c_gate) > 2 else ""), "",
         f"The fixed model: orange hue {fixed['orange_h_lo']}..{fixed['orange_h_hi']}, S >= {fixed['orange_s_lo']}; blue hue {fixed['blue_h_lo']}..{fixed['blue_h_hi']}, "
         f"S >= {fixed['blue_s_lo']}; brightness floor {fixed['v_min']}. With it: found {o.found_w:.1f} of {o.placements} placements ({o.found} of {o.barrels} per frame), "
         f"{o.off} found with the box off, {o.extra} boxes not on their barrel, {o.empty} on empty frames.", "",
         "## The margins", "",
         "Each margin is the largest change, in that direction, that a neighbour of sets A" + (" and B" if widened else "") + " produced at that level, and never less than "
         "one whole unit. Units: placements for found; boxes counted once per arrangement.", "",
         f"- **Pass rule, found over the ordinary conditions:** better above **+{jm['found_gain']:.2f}**, worse below **-{jm['found_loss']:.2f}**.",
         f"- **Pass rule, boxes not on their barrel:** worse above +{jm['extra_rise']:.2f}, better below -{jm['extra_fall']:.2f}.",
         f"- **Pass rule, boxes on empty frames:** with clutter, worse above +{jm['cluttered_empty']:.2f}; clean, any new box (margin {jm['clean_empty']:g}).",
         "- **Pass rule, each place (a drop in found larger than):** " + ", ".join(f"{p} {v:.2f}" for p, v in jm["place"].items()) + f"; a place not measured: {jm['place_default']:.1f}.",
         "- **Never-regress check, each protected set (drop in found / rise in boxes):** " + ", ".join(f"{g} {v['found']:.2f} / {v['extra']:.2f}" for g, v in gm["groups"].items())
         + f"; boxes on empty frames with clutter, all train sets: {gm['cluttered_empty']:.2f}; on clean empty frames: {gm['clean_empty']:g}.",
         f"- *As first registered* (the largest absolute change, the same both ways; kept for the record in `margins.json`): found {registered[0]['found_gain']:.2f}, "
         f"boxes {registered[0]['extra_rise']:.2f}.", "",
         "## Every neighbour, the ordinary conditions together (neighbour minus fixed)", "",
         "found = strict, per placement; either way = strict or found with the box off; boxes = not on their barrel, once per arrangement; a dot = no change. The "
         "last two columns apply the pass rule and the never-regress check with the margins above: by construction \"no clear difference\" and \"pass\" for sets A"
         + (" and B" if widened else "") + ", a real check for set C.", "",
         "| set | neighbour | what moved | found | found per frame | found either way | boxes | boxes per frame | on clean empty | on empty with clutter | largest drop at one place | pass rule | never-regress check |",
         "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|"]
    for tag, names in (("A", A), ("B", B), ("C", C)):
        for n in names:
            d = D[n]["overall"]["ordinary"]
            moved = ", ".join(f"{k} {fixed[k]}→{numbers[n][k]}" for k in NUMBERS if numbers[n][k] != fixed[k])
            worst = min(levels["place"], key=lambda p: D[n]["place"][p]["found_w"])
            wv = D[n]["place"][worst]["found_w"]
            L.append(f"| {tag} | {n} | {moved} | {f(d['found_w'])} | {f(d['found'])} | {f(d['any_w'])} | {f(d['extra_w'])} | {f(d['extra'])} | "
                     f"{f(D[n]['overall']['all train']['clean_empty'])} | {f(d['cluttered_empty_w'])} | {(worst + ' ' + f(wv)) if wv < -5e-3 else '.'} | "
                     f"{final[n]['verdict'] if final[n]['verdict'] != jg.NO_CLEAR else 'no clear difference'} | {'FAIL: ' + '; '.join(final[n]['gate']) if final[n]['gate'] else 'pass'} |")
    L += ["", "## How far the counts move (absolute change: median / 90th percentile / maximum)", "",
          "| level | what | one step (set A) | joint moves (set B) | check moves (set C) |", "|---|---|---|---|---|"]
    show = (("found_w", "found (per placement; at condition level = per frame)"), ("any_w", "found either way"), ("extra_w", "boxes not on their barrel (per arrangement)"),
            ("nothing_w", "boxes on nothing (per arrangement)"), ("clean_empty", "boxes on clean empty frames"), ("cluttered_empty_w", "boxes on empty frames with clutter (per arrangement)"))

    def cell(d: dict) -> str:
        return f"{f(d['median'], False)} / {f(d['p90'], False)} / {f(d['max'], False)} (n {d['n']})"
    for lv in ("condition, all", "condition, ordinary", "place", "protected set", "overall, ordinary", "overall, all train"):
        for m, text in show:
            L.append(f"| {lv} | {text} | {cell(dists['A'][lv][m])} | {cell(dists['B'][lv][m])} | {cell(dists['C'][lv][m])} |")
    k = "worst place per neighbour"
    L.append(f"| place | the largest drop in found at any one place, per neighbour | {cell(dists['A'][k])} | {cell(dists['B'][k])} | {cell(dists['C'][k])} |")
    L += ["", "n = neighbours x units (28 conditions, 17 ordinary conditions, 8 places, 6 protected sets) or neighbours (overall).", "",
          "## Place by place: found, per placement", "",
          "| place | placements | found with the fixed model | largest drop, one step | largest drop, joint | largest gain, any | margin (a drop larger than) | on a threshold edge? |",
          "|---|---:|---:|---:|---:|---:|---:|---|"]
    edges = []
    for p in levels["place"]:
        t = base["place"][p]
        da = [D[n]["place"][p]["found_w"] for n in A]
        edge = max(rise(da), fall(da)) > t.placements / 3
        if edge:
            who = max(A, key=lambda n: abs(D[n]["place"][p]["found_w"]))
            edges.append(f"{p} ({who}: {f(D[who]['place'][p]['found_w'])} of {t.placements})")
        L.append(f"| {p} | {t.placements} | {t.found_w:.1f} | {f(fall(da), False)} | {f(fall(D[n]['place'][p]['found_w'] for n in B), False)} | "
                 f"{f(rise(D[n]['place'][p]['found_w'] for n in AB), False)} | {jm['place'][p]:.2f} | {'YES' if edge else 'no'} |")
    L += ["", ("**On a threshold edge under the fixed model** (one step moves the place by more than a third of its placements): " + "; ".join(edges)
               + ". The wide margin there is a finding about the place, not a licence to lose it.") if edges else
          "No place moves by more than a third of its placements under one step.", "",
          "## The protected sets", "",
          "| protected set | placements | found | largest drop in found | margin, found | largest rise in boxes | margin, boxes |", "|---|---:|---:|---:|---:|---:|---:|"]
    for g in levels["protected"]:
        t = base["protected"][g]
        L.append(f"| {g} | {t.placements} | {t.found_w:.1f} | {f(fall(D[n]['protected'][g]['found_w'] for n in AB), False)} | {gm['groups'][g]['found']:.2f} | "
                 f"{f(rise(D[n]['protected'][g]['extra_w'] for n in AB), False)} | {gm['groups'][g]['extra']:.2f} |")
    bj = [n for n, c in rule3.items() if c["verdict"] != jg.NO_CLEAR]
    bg = [n for n, c in rule3.items() if c["gate"]]
    cr = [n for n in C if c_registered[n]["verdict"] != jg.NO_CLEAR]
    L += ["", "HOME is scored here with the model as it is (a neighbour is a model moved by hand; there is nothing to re-fit). The never-regress check itself keeps "
          "the leave-one-scene-out protocol for HOME; its margin is a difference and is taken from here.", "",
          "## How the margins were arrived at (the registered rules, in order)", "",
          f"1. *Rule 1 as first registered:* the largest absolute change in set A, at least one unit: found {reg_a[0]['found_gain']:.2f}, boxes {reg_a[0]['extra_rise']:.2f}; "
          "places " + ", ".join(f"{p} {v:.2f}" for p, v in reg_a[0]["place"].items()) + ".",
          f"2. *Rule 3:* with those margins, {len(bj)} of {len(B)} joint moves get a verdict other than NO CLEAR DIFFERENCE"
          + (" (" + ", ".join(f"{n}: {rule3[n]['verdict']}" for n in bj) + ")" if bj else "") + f" and {len(bg)} of {len(B)} fail the never-regress check. "
          + ("More than 2: small changes that come together add up, so the margins are taken over sets A and B." if widened else "Not more than 2: the margins stay as taken from set A."),
          "3. *The addendum (written after the first run, before any candidate was judged):* the changes are one-sided, so each margin is taken per direction. "
          f"The absolute version would ask for a gain of {registered[0]['found_gain']:.2f} placements when no change that means nothing gained more than {jm['found_gain']:.2f}.",
          f"4. *Set C,* 12 joint moves the margins have never seen: {len(c_judge)} of {len(C)} called by the pass rule, {len(c_gate)} of {len(C)} fail the never-regress check "
          f"(with the margins as first registered: {len(cr)} of {len(C)} called by the pass rule).", "",
          "Files: `noise.json` (every change at every level), `per_neighbour.csv`; the margins as data: `results/baseline/margins.json`.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
