#!/usr/bin/env python3
"""The sanity checks of the standard pass rule (2026-11-26, TODO M3; plan: PREREG.md in this folder).

    python barrels/experiments/2026-11-26_judge/run.py [--jobs 8]

Train frames only (``judge.run_many`` and ``judge.load_frame`` refuse anything else before an image is opened).

S1  today's detector against itself                      -> must be NO CLEAR DIFFERENCE, nothing changed
S2  the changes that mean nothing                        -> read from the noise run; two re-run through the whole tool
S3  Tanush's hand thresholds, per condition              -> must PASS
S4  "blue follows the light", leave one place out as experiments/2026-11-25_color did (families C2 and C2b)

Outputs: results/2026-11-26_judge/ (summary.md, chosen.json, one folder per judged candidate).
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import importlib.util
import json
import sys
import time
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

BARRELS = Path(__file__).resolve().parents[2]
COLOR = BARRELS / "experiments" / "2026-11-25_color"
sys.path.insert(0, str(BARRELS / "src"))
sys.path.insert(0, str(COLOR))
from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import cv as bcv  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import eval_det as ed  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import hsrange as hx  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402


def load_module(name: str, path: Path):
    """A script of another experiment as a module (workers started by multiprocessing import it the same way)."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


color = load_module("color_test", COLOR / "test.py")                        # Setting, families, choose: the 2026-11-25 selection rule, unchanged
noise = load_module("noise_floor_run", BARRELS / "experiments" / "2026-11-26_noise_floor" / "run.py")
OUT = BARRELS / "results" / "2026-11-26_judge"
CAM = geo.AIM_4A8B6118_BOXFIT
NOISE_JSON = BARRELS / "results" / "2026-11-26_noise_floor" / "noise.json"


# ---------------------------------------------------------------- S4: every setting of the two families on every ordinary frame

def eval_settings(args) -> tuple[str, dict]:
    """One frame, every setting -> what the 2026-11-25 selection rule reads: hits, false boxes, misses per color (the
    strict rule), per setting. A mask seen before on this frame is not detected again."""
    import cv2
    cv2.setNumThreads(1)
    stem, settings = args
    frame = jg.load_frame(stem)
    label = io.load_boxes(stem, check_image=False)
    gts = [b.with_ground(CAM) for b in dtp.barrels_from_boxes(label)]
    base = hl.adopted_model()
    seen, out = {}, {}
    for s in settings:
        mask = pl.segment(frame, s.model(base))[0]
        h = hashlib.blake2b(mask.tobytes(), digest_size=16).digest()
        if h not in seen:
            preds = det.detect(mask, det.DetConfig(), CAM)
            r = ed.evaluate_frame(stem, preds, gts, CAM, rule="v2", clean=bool(label.get("clean", True)))
            seen[h] = {"tp": [r.tp[1], r.tp[2]], "fp": [r.fp[1], r.fp[2]], "fn": [r.fn[1], r.fn[2]],
                       "found": sorted(m.gt_idx for m in r.matches), "neg": len(gts) == 0, "boxes": len(preds)}
        out[s.key] = seen[h]
    return stem, out


def make_fit(res: dict, family: list, chosen: dict):
    """``fit(train_stems, held_place)`` for one family: that experiment's rule picks the setting on the training
    places; the detector of that setting is returned. ``chosen`` records what each fold picked."""
    def fit(train_stems: list[str], held_place: str):
        setting, info = color.choose(res, family, list(train_stems))
        chosen[held_place] = {"setting": setting.describe(), "numbers": dataclasses.asdict(setting), **info}
        return jg.model_detector(setting.model(hl.adopted_model()), describe=setting.describe())
    return fit


# ---------------------------------------------------------------- S3: the hand thresholds

def hand_thresholds(stems: list[str]) -> dict[str, tuple]:
    """condition -> the six numbers: the median of the slider labels of that condition's train frames."""
    by = defaultdict(list)
    for s in stems:
        if io.hs_path(s).exists():
            d = io.load_hs(s, check_image=False)
            by[ct.condition_of(s)].append([d["orange"]["h_lo"], d["orange"]["h_hi"], d["orange"]["s_lo"], d["blue"]["h_lo"], d["blue"]["h_hi"], d["blue"]["s_lo"]])
    return {c: tuple(int(round(x)) for x in np.median(np.array(v, float), 0)) for c, v in sorted(by.items())}


def hand_detector(hand: dict[str, tuple]):
    base = hl.adopted_model()
    per = {c: jg.model_detector(hl.model_from_thresholds(base, hx.nested(dict(zip(hx.THRESHOLDS, six))))) for c, six in hand.items()}
    fixed = jg.fixed_detector()

    def detect_frame(stem: str, frame) -> list:
        return per.get(ct.condition_of(stem), fixed)(stem, frame)
    detect_frame.describe = f"hand thresholds: per condition the median of its slider labels ({len(hand)} conditions; the others keep the fixed model); DetConfig defaults"
    return detect_frame


# ---------------------------------------------------------------- the page

def slug(name: str) -> str:
    """A folder name; ``-1`` and ``+1`` stay apart (minus / plus)."""
    name = name.replace("-", " minus ").replace("+", " plus ")
    return "_".join("".join(c if c.isalnum() else " " for c in name).lower().split())


def near_margin(j: jg.Judgement) -> list[str]:
    """Clauses whose number sits within one whole unit of the margin that decides them."""
    b, c, m = j.total[0], j.total[1], j.margins
    out = []
    d = c.found_w - b.found_w
    for label, value, limit in (("found over all places", d, m.found_gain), ("found over all places", -d, m.found_loss),
                                ("boxes not on their barrel", c.extra_w - b.extra_w, m.extra_rise),
                                ("boxes on empty frames with clutter", c.cluttered_empty_w - b.cluttered_empty_w, m.cluttered_empty)):
        if abs(value - limit) <= 1.0 and value > 0:
            out.append(f"{label}: {value:+.2f} against a margin of {limit:.2f}")
    for p, (pb, pc) in j.places.items():
        drop = pb.found_w - pc.found_w
        if drop > 0 and abs(drop - m.for_place(p)) <= 1.0 and drop > m.for_place(p) - 1.0 + 1e-9 and drop != 0:
            out.append(f"found at {p}: -{drop:.2f} against a margin of {m.for_place(p):.2f}")
    return out


def row(name: str, j: jg.Judgement, jr: jg.Judgement) -> str:
    b, c = j.total
    return (f"| {name} | {b.found_w:.1f} → {c.found_w:.1f} ({c.found_w - b.found_w:+.1f}) | {b.found} → {c.found} | "
            f"{b.found_w + b.off_w:.1f} → {c.found_w + c.off_w:.1f} | {b.extra_w:.1f} → {c.extra_w:.1f} ({b.extra} → {c.extra}) | "
            f"{b.clean_empty} → {c.clean_empty} / {b.cluttered_empty_w:.1f} → {c.cluttered_empty_w:.1f} | **{j.result}** | {jr.result} |")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    margins = jg.load_margins()
    md = json.loads(jg.MARGINS_PATH.read_text())
    registered = jg.margins_from_dict(md["as_first_registered"]["judge"], "as first registered (the largest absolute change, both ways)")
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    stems = ordinary + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    truth = jg.load_truth(stems)

    # ---- S1, as one call of the tool, timed
    t0 = time.time()
    j1 = jg.judge(jg.fixed_detector(), frames=frames, truth=truth, name="today again", base_name="today")
    seconds = time.time() - t0
    jg.write(j1, OUT / "s1_today_against_itself")
    s1_ok = j1.result == jg.NO_CLEAR and not j1.changes and not j1.box_changes
    print(f"S1: {j1.result}, {len(j1.changes)} barrels and {len(j1.box_changes)} frames of boxes changed; one judge run took {seconds:.0f} s", flush=True)

    # ---- S4 preparation: every setting of C2 and C2b on every ordinary frame
    fams = {"C2": color.families(1)["C2"], "C2b": color.families(2)["C2b"]}
    settings = list(dict.fromkeys([color.FIXED] + [s for f in fams.values() for s in f]))
    res, t0 = {}, time.time()
    with Pool(args.jobs) as pool:
        for i, (stem, out) in enumerate(pool.imap_unordered(eval_settings, [(s, settings) for s in ordinary], chunksize=1)):
            res[stem] = out
            if (i + 1) % 40 == 0:
                print(f"  S4: {i + 1}/{len(ordinary)} frames x {len(settings)} settings", flush=True)
    print(f"  S4: settings evaluated in {time.time() - t0:.0f} s", flush=True)
    chosen: dict[str, dict] = {n: {} for n in fams}

    # ---- one pass: the baseline and every candidate
    hand = hand_thresholds([s for v in frames.values() for s in v])
    A = noise.set_a()
    detectors = {"today": jg.fixed_detector(), "hand thresholds": hand_detector(hand),
                 "orange_h_lo-1": noise.detector_for(A["orange_h_lo-1"], "orange hue low 3 -> 2 (the largest gain among the changes that mean nothing)"),
                 "orange_h_lo+1": noise.detector_for(A["orange_h_lo+1"], "orange hue low 3 -> 4 (the largest one-step loss)")}
    for n, fam in fams.items():
        detectors[f"blue follows the light, {n}"] = jg.leave_one_place_out(
            make_fit(res, fam, chosen[n]), ordinary, f"blue follows the light, family {n}: the setting picked on the other places by the 2026-11-25 rule")
    runs = jg.run_many(detectors, stems, truth)
    judged, rows = {}, []
    for name in detectors:
        if name == "today":
            continue
        lopo = name.startswith("blue follows")
        j = jg.compare(runs["today"], runs[name], frames, truth, margins, lopo=lopo)
        jr = jg.compare(runs["today"], runs[name], frames, truth, registered, lopo=lopo)
        jg.write(j, OUT / slug(name))
        judged[name] = (j, jr)
        rows.append(row(name, j, jr))
        print(f"{name}: {j.result} (as first registered: {jr.result})", flush=True)
    (OUT / "chosen.json").write_text(json.dumps({"hand_thresholds": hand, "folds": chosen}, indent=1, default=float) + "\n")

    # ---- S2 from the noise run, and the two neighbours through the whole tool
    nz = json.loads(NOISE_JSON.read_text())
    fc = nz["final_check"]
    counts = {tag: [fc[n]["verdict"] for n in nz[f"set_{tag.lower()}"]] for tag in "ABC"}
    called_c = [f"{n}: {fc[n]['verdict']}" for n in nz["set_c"] if fc[n]["verdict"] != jg.NO_CLEAR]
    agree = {n: (judged[n][0].result, fc[n]["verdict"], round(judged[n][0].total[1].found_w - judged[n][0].total[0].found_w, 2),
                 round(nz["changes"][n]["overall"]["ordinary"]["found_w"], 2)) for n in ("orange_h_lo-1", "orange_h_lo+1")}
    s2_ok = all(v == jg.NO_CLEAR for v in counts["A"] + counts["B"]) and all(a == b and abs(c - d) < 0.011 for a, b, c, d in agree.values())
    jh, jhr = judged["hand thresholds"]
    s3_ok = jh.result == jg.PASS

    L = [f"# The sanity checks of the standard pass rule ({dt.date.today().isoformat()}, git {bcv.git_hash()})", "",
         "`python barrels/experiments/2026-11-26_judge/run.py` (plan: `../../experiments/2026-11-26_judge/PREREG.md`; the rule: `docs/EVAL.md`, \"The standard pass rule\"). "
         f"Train frames only; test frames never opened. Baseline everywhere: today's default. Margins: {margins.source}.", "",
         f"**One judge run** (two detectors on the {len(stems)} ordinary and extreme train frames, one process): **{seconds:.0f} s**.", "",
         "| candidate | found, placements | found, per frame | found either way | boxes not on their barrel (per frame) | on empty frames: clean / with clutter | verdict | with the margins as first registered |",
         "|---|---|---|---|---|---|---|---|",
         row("S1 today against itself", j1, jg.compare(j1.baseline, j1.candidate, frames, truth, registered))] + rows + ["",
         f"## S1. Today's detector against itself: {'as required' if s1_ok else '**NOT AS REQUIRED: a bug**'}", "",
         f"{j1.result}; {len(j1.changes)} barrels changed, {len(j1.box_changes)} frames with other boxes.", "",
         f"## S2. The changes that mean nothing: {'as required' if s2_ok else '**NOT AS REQUIRED**'}", "",
         f"- Set A (14, one number moved one step): {counts['A'].count(jg.NO_CLEAR)} of {len(counts['A'])} NO CLEAR DIFFERENCE. Set B (12, several numbers at once): "
         f"{counts['B'].count(jg.NO_CLEAR)} of {len(counts['B'])}. Both sets are inside the margins by construction, so this checks the tool, not the margins.",
         f"- Set C (12 joint moves the margins have never seen): {counts['C'].count(jg.NO_CLEAR)} of {len(counts['C'])} NO CLEAR DIFFERENCE"
         + (f"; called: {', '.join(called_c)}" if called_c else "") + ".",
         "- Through the whole tool (frames, counting, verdict): " + "; ".join(
             f"{n} {a} with found {c:+.2f} (the noise run recorded {b}, {d:+.2f})" for n, (a, b, c, d) in agree.items()) + ".", "",
         f"## S3. Tanush's hand thresholds: {jh.result}{' (as required)' if s3_ok else ' — **REQUIRED: PASS. The rule is wrong.**'}", "",
         f"Per condition, the median of its slider labels; in-sample by nature. Per frame: found {jh.total[0].found} → {jh.total[1].found} of {jh.total[0].barrels} "
         f"(the review counted 211 → 281). With the margins as first registered: {jhr.result}.", ""]
    for name, (j, jr) in judged.items():
        if name.startswith("orange_"):
            continue
        if name != "hand thresholds":
            fam = name.rsplit(", ", 1)[1]
            L += [f"## S4. {name}, leave one place out: {j.result} (with the margins as first registered: {jr.result})", "",
                  "The setting picked in each fold (on the other places, by the 2026-11-25 rule): "
                  + "; ".join(f"{p}: {c['setting'].split('; light rule ')[-1] if 'light rule' in c['setting'] else 'the fixed model'}" for p, c in chosen[fam].items()) + ".", ""]
        L += [f"- [{c.state}] {c.text}" for c in j.verdict.clauses]
        L += [f"- Verdict: **{j.result}**. {j.verdict.reason}"]
        near = near_margin(j)
        if near:
            L.append("- At the margin (within one whole unit of it): " + "; ".join(near) + ".")
        gained = sum(x.kind == "gained" for x in j.changes if x.judged)
        lost = sum(x.kind == "lost" for x in j.changes if x.judged)
        L += [f"- Barrels, per frame: {gained} gained, {lost} lost. Every one of them, the tables and the boxes: `{slug(name)}/judge.md`.", ""]
    L += ["Files: `chosen.json` (the hand thresholds per condition, the setting each fold picked), one folder per candidate.", ""]
    (OUT / "summary.md").write_text("\n".join(L))
    print("\n".join(L))
    return 0 if (s1_ok and s2_ok and s3_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
