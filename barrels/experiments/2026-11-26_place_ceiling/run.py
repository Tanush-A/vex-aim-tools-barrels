#!/usr/bin/env python3
"""What can a color setting made per place reach, without hand sliders? (2026-11-26; TODO C1, C7, the third idea of
E6. Plan: PREREG.md in this folder, written and committed before any stage below was run on all frames.)

    python barrels/experiments/2026-11-26_place_ceiling/run.py settings   # one setting per frame, from the frame and its boxes
    python barrels/experiments/2026-11-26_place_ceiling/run.py oracle     # the best rectangle pair per condition, by search (in-sample)
    python barrels/experiments/2026-11-26_place_ceiling/run.py judge      # every candidate through the standard pass rule; contact sheets
    python barrels/experiments/2026-11-26_place_ceiling/run.py cross      # each frame in turn; one light / one place applied to another
    python barrels/experiments/2026-11-26_place_ceiling/run.py report     # summary.md from the files the stages wrote
    python barrels/experiments/2026-11-26_place_ceiling/run.py all

Train frames only: every image is read through ``judge.load_frame``, which refuses anything else. No pixel is changed.
The judge is ``barrels.judge`` (``run_many`` + ``compare``: what ``judge.judge`` does, with several candidates in one
pass over the frames). Outputs: ``results/2026-11-26_place_ceiling/``.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import json
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

BARRELS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BARRELS / "src"))
sys.path.insert(0, str(BARRELS / "tools"))
from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import cv as bcv  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import hsrange as hx  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402
from barrels import placecal as pc  # noqa: E402

OUT = BARRELS / "results" / "2026-11-26_place_ceiling"
CAM = geo.AIM_4A8B6118_BOXFIT
METHODS = ("mid", "net", "tool")        # PREREG: mid is the primary computation
PRIMARY = "mid"
ROTATIONS = (1, 2, 3, 4)
STRONG = 2.0                            # a PASS less than this many placements above the gain margin is WEAK
ENOUGH = 0.8                            # "one frame is enough": at least this share of the way from fixed to the hand thresholds
HUE_STEPS, S_STEPS, MAX_MOVES = (1, 2, 4, 8), (4, 8, 16, 32), 12
BATH = ("lampcool6_bathtile", "lampmid3_bathtile", "lampmid6_bathtile", "lampwarm6_bathtile")


def six_of(thr) -> tuple:
    f = hx.flat(thr)
    return tuple(int(f[t]) for t in hx.THRESHOLDS)


def nested_of(six) -> dict:
    return hx.nested(dict(zip(hx.THRESHOLDS, six)))


def model_of(base: pl.Model, six) -> pl.Model:
    return hl.model_from_thresholds(base, nested_of(six))


def text_of(six) -> str:
    return "o " + "/".join(str(v) for v in six[:3]) + "  b " + "/".join(str(v) for v in six[3:])


def scene_of(stem: str) -> str:
    return io.parse_name(stem)["scene"]


def short(stem: str) -> str:
    t = io.parse_name(stem)
    return f"{t['scene']}_{t['nn']}"


# ---------------------------------------------------------------- which frame calibrates which

def eligible(stem: str) -> bool:
    """A frame can calibrate when at least one of its barrels is free-standing (not flagged occluded, truncated, held
    or no_stripe): only such a barrel gives zone pixels. Read from the label file."""
    boxes = io.load_boxes(stem, check_image=False)["barrels"]
    return any(not any(f in pc.SKIP_FLAGS for f in (b.get("flags") or ())) for b in boxes)


@dataclasses.dataclass
class Layout:
    ordinary: list
    by_cond: dict           # condition -> its ordinary train frames, by name
    conds_of: dict          # place -> its conditions, by name
    eligible: dict          # condition -> the frames that can calibrate, by name
    cal: dict               # condition -> THE calibration frame: core_01, else the first eligible frame by name
    backup: dict            # condition -> the frame that calibrates the calibration frame itself: the next eligible one

    def place(self, cond: str) -> str:
        return cnd.info(cond).place


def layout() -> Layout:
    ordinary = sorted(jg.train_frames()[cnd.ORDINARY])
    jg.require_train(ordinary)
    by_cond = dict(sorted(ct.group_stems(ordinary, "condition").items()))
    conds_of = defaultdict(list)
    for c in by_cond:
        conds_of[cnd.info(c).place].append(c)
    el = {c: [s for s in ss if eligible(s)] for c, ss in by_cond.items()}
    cal, backup = {}, {}
    for c, e in el.items():
        if len(e) < 2:
            raise ValueError(f"{c}: fewer than two frames can calibrate")
        core = [s for s in e if short(s) == "core_01"]
        cal[c] = core[0] if core else e[0]
        backup[c] = e[(e.index(cal[c]) + 1) % len(e)]
    return Layout(ordinary, by_cond, dict(sorted(conds_of.items())), el, cal, backup)


def source_frame(L: Layout, stem: str, rot: int = 0) -> str:
    """The frame whose setting scores ``stem``, never ``stem`` itself. ``rot`` 0: the condition's calibration frame
    (its backup for the calibration frame). ``rot`` r >= 1: the eligible frame k places after ``stem`` in the
    condition's list, k = ((r - 1) mod (n - 1)) + 1; for a frame that cannot calibrate, the r-th eligible frame."""
    c = ct.condition_of(stem)
    e = L.eligible[c]
    if rot == 0:
        return L.backup[c] if stem == L.cal[c] else L.cal[c]
    if stem in e:
        return e[(e.index(stem) + ((rot - 1) % (len(e) - 1)) + 1) % len(e)]
    return e[(rot - 1) % len(e)]


# ---------------------------------------------------------------- stage 1: one setting per frame

def _calibrate(stem: str) -> tuple:
    import cv2
    cv2.setNumThreads(1)
    base = hl.adopted_model()
    adopted = hl.thresholds_from_model(base)
    frame = jg.load_frame(stem)                                 # refuses anything but a train frame
    label = io.load_boxes(stem, check_image=False)
    fe = hx.FrameEval(frame.bgr, label, base, stem=stem)
    net = six_of(pc.net_setting(frame, label["barrels"], base, adopted))
    m = pc.mid_setting(fe, adopted)
    p = hx.propose(fe, adopted)                                 # the slider tool's computed proposal, unchanged (old span)
    z = pc.zones(frame.shape, label["barrels"], base.cfg.horizon_row or 0)
    rec = {"net": net, "mid": six_of(m.thresholds), "mid_source": m.source, "tool": six_of(p.thresholds), "tool_source": p.source,
           "boxes": len(fe.boxes), "zone_boxes": z.used, "zone_px": {c: int(z.pos[c].sum()) for c in pc.CLASS_NAMES},
           "found_on_itself": {k: len(fe.evaluate(dict(zip(hx.THRESHOLDS, v))).found) for k, v in (("net", net), ("mid", six_of(m.thresholds)), ("tool", six_of(p.thresholds)))}}
    return stem, rec


def stage_settings(jobs: int) -> None:
    L = layout()
    stems = [s for e in L.eligible.values() for s in e]
    res = {}
    with Pool(jobs) as pool:
        for i, (stem, rec) in enumerate(pool.imap_unordered(_calibrate, stems, chunksize=1)):
            res[stem] = rec
            if (i + 1) % 20 == 0:
                print(f"  settings: {i + 1}/{len(stems)} frames", flush=True)
    base = hl.adopted_model()
    adopted = hl.thresholds_from_model(base)
    pooled = {}
    for c, ss in L.by_cond.items():
        pairs = [(jg.load_frame(s), io.load_boxes(s, check_image=False)["barrels"]) for s in ss]
        pooled[c] = six_of(pc.pooled_net_setting([p for p in pairs if p[1]], base, adopted))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "settings.json").write_text(json.dumps({"made": dt.date.today().isoformat(), "git": bcv.git_hash(), "thresholds": list(hx.THRESHOLDS),
                                                   "calibration_frame": L.cal, "backup_frame": L.backup, "eligible": L.eligible,
                                                   "pooled_net": pooled, "frames": dict(sorted(res.items()))}, indent=1) + "\n")
    print(f"settings: {len(res)} frames at {len(L.by_cond)} conditions -> {OUT / 'settings.json'}")


def load_settings() -> dict:
    d = json.loads((OUT / "settings.json").read_text())
    d["pooled_net"] = {c: tuple(v) for c, v in d["pooled_net"].items()}
    for rec in d["frames"].values():
        for m in METHODS:
            rec[m] = tuple(rec[m])
    return d


# ---------------------------------------------------------------- the hand thresholds and the proposals

def _median_six(by: dict) -> dict:
    return {c: tuple(int(round(x)) for x in np.median(np.array(v, float), 0)) for c, v in sorted(by.items())}


def hand_thresholds(stems) -> dict:
    """condition -> the median of its slider labels (as ``experiments/2026-11-26_judge`` built the hand ceiling)."""
    by = defaultdict(list)
    for s in stems:
        if io.hs_path(s).exists():
            by[ct.condition_of(s)].append(six_of(io.load_hs(s, check_image=False)))
    return _median_six(by)


def proposal_thresholds(stems) -> dict:
    """condition -> the median of the proposals written for its frames (``write_proposals.py``)."""
    by = defaultdict(list)
    for s in stems:
        if io.hs_proposed_path(s).exists():
            by[ct.condition_of(s)].append(six_of(io.load_hs_proposed(s)))
    return _median_six(by)


# ---------------------------------------------------------------- stage 2: the oracle per condition

class CondEval:
    """The frames of one condition: ``score(six)`` = (found - boxes not on their barrel, found, -boxes), summed over
    its frames, counted per frame as the judge counts them (``counting.classify_frame``)."""

    def __init__(self, stems):
        self.base = hl.adopted_model()
        self.items = []
        for s in stems:
            label = io.load_boxes(s, check_image=False)
            self.items.append((s, jg.load_frame(s), dtp.barrels_from_boxes(label), bool(label.get("clean", True)), {}))
        self.cache: dict = {}

    def score(self, six) -> tuple:
        if six not in self.cache:
            model = model_of(self.base, six)
            found = extra = 0
            for s, frame, gts, clean, seen in self.items:
                f, _, e = count_frame(s, frame, gts, clean, model, seen)
                found, extra = found + f, extra + e
            self.cache[six] = (found - extra, found, -extra)
        return self.cache[six]


def count_frame(stem, frame, gts, clean, model, seen: dict) -> tuple:
    """(found, barrels, boxes not on their barrel) of one frame with one color model; ``seen`` caches by mask."""
    mask = pl.segment(frame, model)[0]
    h = hashlib.blake2b(mask.tobytes(), digest_size=16).digest()
    if h not in seen:
        fc = ct.classify_frame(stem, det.detect(mask, det.DetConfig(), CAM), gts, clean)
        seen[h] = (fc.n_gt(ct.FOUND), len(fc.gt), fc.extra)
    return seen[h]


def neighbours(six) -> list:
    out = []
    for i, t in enumerate(hx.THRESHOLDS):
        lo, hi = pc.FULL_LIMITS[t]
        for step in (S_STEPS if t.endswith("s_lo") else HUE_STEPS):
            for d in (-step, step):
                v = list(six)
                v[i] += d
                if lo <= v[i] <= hi and v[0] <= v[1] and v[3] <= v[4]:
                    out.append(tuple(v))
    return out


def _oracle(args) -> tuple:
    import cv2
    cv2.setNumThreads(1)
    cond, stems, seeds = args
    ev = CondEval(stems)
    scored = [(ev.score(six), -i, name, six) for i, (name, six) in enumerate(seeds)]
    best_score, _, seed, best = max(scored)
    moves = 0
    while moves < MAX_MOVES:
        cand = max(((ev.score(n), n) for n in neighbours(best)), key=lambda x: (x[0][0], x[0][1]))
        if cand[0][0] <= best_score[0]:
            break
        best_score, best = cand
        moves += 1
    return cond, {"best": best, "score": best_score[0], "found": best_score[1], "extra": -best_score[2], "seed": seed, "moves": moves,
                  "seeds": {name: {"six": six, "score": sc[0], "found": sc[1], "extra": -sc[2]} for sc, _, name, six in scored},
                  "settings_tried": len(ev.cache)}


def stage_oracle(jobs: int) -> None:
    L, S = layout(), load_settings()
    base = hl.adopted_model()
    fixed = six_of(hl.thresholds_from_model(base))
    hand, prop = hand_thresholds(L.ordinary), proposal_thresholds(L.ordinary)
    tasks = []
    for c, ss in L.by_cond.items():
        seeds = [("fixed", fixed)]
        if c in hand:
            seeds.append(("hand thresholds", hand[c]))
        if c in prop:
            seeds.append(("relabelled", prop[c]))
        seeds.append(("pooled net setting", S["pooled_net"][c]))
        for g in L.eligible[c]:
            seeds += [(f"{m} of {short(g)}", S["frames"][g][m]) for m in ("mid", "net")]
        tasks.append((c, ss, seeds))
    res = {}
    with Pool(jobs) as pool:
        for c, r in pool.imap_unordered(_oracle, tasks, chunksize=1):
            res[c] = r
            print(f"  oracle {c}: found {r['found']} with {r['extra']} boxes not on their barrel, from '{r['seed']}' in {r['moves']} moves: {text_of(r['best'])}", flush=True)
    (OUT / "oracle.json").write_text(json.dumps({"made": dt.date.today().isoformat(), "git": bcv.git_hash(), "conditions": dict(sorted(res.items()))}, indent=1) + "\n")


def load_oracle() -> dict:
    d = json.loads((OUT / "oracle.json").read_text())["conditions"]
    return {c: tuple(r["best"]) for c, r in d.items()}


# ---------------------------------------------------------------- stage 3: every candidate through the judge

def assignments(L: Layout, S: dict, hand: dict, prop: dict, oracle: dict) -> dict:
    """name -> (what it is, kind, {stem: six numbers or None = the fixed model}). kind: 'held out' (no frame is scored
    with a setting computed from itself), 'in-sample' (a ceiling) or 'control'."""
    F = S["frames"]
    places = list(L.conds_of)
    out = {}

    def per_cond(table: dict) -> dict:
        return {s: table.get(ct.condition_of(s)) for s in L.ordinary}
    out["hand"] = ("Tanush's hand thresholds: per condition the median of its slider labels", "in-sample", per_cond(hand))
    out["relabel"] = ("the hand thresholds, the four bathroom conditions replaced by the median of the proposals (full hue range)", "in-sample",
                      per_cond({**hand, **prop}))
    out["relabel_blue"] = ("the hand thresholds; in the bathroom his orange numbers with the proposals' blue numbers", "in-sample",
                           per_cond({**hand, **{c: hand[c][:3] + prop[c][3:] for c in prop if c in hand}}))
    for m in METHODS:
        out[f"cal_core_{m}"] = (f"ONE frame sets the condition ({m}): the calibration frame (core_01), applied to the other frames; the calibration "
                                "frame itself is scored with the backup frame's setting", "held out",
                                {s: F[source_frame(L, s)][m] for s in L.ordinary})
    for r in ROTATIONS:
        out[f"cal_rot{r}_{PRIMARY}"] = (f"each frame in turn, rotation {r} ({PRIMARY}): every frame is scored with the setting of another frame of its condition",
                                        "held out", {s: F[source_frame(L, s, r)][PRIMARY] for s in L.ordinary})
    other_light = {}
    for p, cs in L.conds_of.items():
        for i, c in enumerate(cs):
            other_light[c] = F[L.cal[cs[(i + 1) % len(cs)]]][PRIMARY] if len(cs) > 1 else None
    out[f"cal_otherlight_{PRIMARY}"] = ("the setting of ANOTHER light of the same place (the next light by name; places with one light keep the fixed model)",
                                        "held out", per_cond(other_light))
    other_place = {}
    for i, p in enumerate(places):
        src = L.conds_of[places[(i + 1) % len(places)]][0]
        for c in L.conds_of[p]:
            other_place[c] = F[L.cal[src]][PRIMARY]
    out[f"cal_otherplace_{PRIMARY}"] = ("CONTROL: the setting of the calibration frame of ANOTHER place (the next place by name, its first condition)",
                                        "control", per_cond(other_place))
    out["cal_all_net"] = ("every frame of the condition at once: the net setting of its pooled barrel pixels (no sliders, no detector)", "in-sample",
                          per_cond(S["pooled_net"]))
    out["oracle"] = ("the best rectangle pair per condition found by search on its own frames", "in-sample", per_cond(oracle))
    return out


def assign_detector(assign: dict, describe: str):
    base = hl.adopted_model()
    fixed = jg.fixed_detector()
    made: dict = {}

    def detect_frame(stem: str, frame) -> list:
        six = assign.get(stem)
        if six is None:
            return fixed(stem, frame)
        if six not in made:
            made[six] = jg.model_detector(model_of(base, six))
        return made[six](stem, frame)
    detect_frame.describe = describe
    return detect_frame


def vendor_counts(L: Layout, truth) -> tuple:
    """(stem -> FrameCount of the vendor's saved boxes, the stems where the vendor is ASSUMED perfect)."""
    counts, assumed = {}, []
    for s in L.ordinary:
        try:
            meta = io.load_vendor(s)
        except FileNotFoundError:
            meta = None
        if meta is not None and meta["available"]:
            counts[s] = ct.classify_frame(s, io.vendor_barrels(meta)[0], truth.gts[s], truth.clean[s])
        elif cnd.info(ct.condition_of(s)).vendor_assumed:
            counts[s] = ct.assumed_perfect(s, len(truth.gts[s]), truth.clean[s])
            assumed.append(s)
    return counts, assumed


def stage_judge(sheets: bool = True) -> None:
    L, S = layout(), load_settings()
    hand, prop, oracle = hand_thresholds(L.ordinary), proposal_thresholds(L.ordinary), load_oracle()
    A = assignments(L, S, hand, prop, oracle)
    frames = {cnd.ORDINARY: L.ordinary, cnd.EXTREME: [], cnd.EXCLUDED: [], cnd.UNLISTED: []}
    truth = jg.load_truth(L.ordinary)
    margins = jg.load_margins()
    dets = {"today": jg.fixed_detector()}
    dets.update({n: assign_detector(a, d) for n, (d, _, a) in A.items()})
    runs = jg.run_many(dets, L.ordinary, truth)
    vcounts, assumed = vendor_counts(L, truth)
    measured = [s for s in L.ordinary if s in vcounts and s not in assumed]

    def tallies(counts: dict, stems=None) -> dict:
        stems = [s for s in (stems or L.ordinary) if s in counts]
        return {"all": ct.tally(counts, stems, truth.placements).to_dict(),
                "measured": ct.tally(counts, [s for s in stems if s in measured], truth.placements).to_dict(),
                "places": {p: ct.tally(counts, ss, truth.placements).to_dict() for p, ss in ct.group_stems(stems, "place").items()},
                "conditions": {c: ct.tally(counts, ss, truth.placements).to_dict() for c, ss in ct.group_stems(stems, "condition").items()}}
    judged = {"made": dt.date.today().isoformat(), "git": bcv.git_hash(), "margins": dataclasses.asdict(margins),
              "today": tallies(runs["today"].counts), "vendor": {**tallies(vcounts), "assumed_frames": len(assumed), "measured_frames": len(measured)},
              "candidates": {}}
    js = {}
    for n, (describe, kind, assign) in A.items():
        j = jg.compare(runs["today"], runs[n], frames, truth, margins)
        js[n] = j
        jg.write(j, OUT / "judge" / n)
        b, c = j.total
        gain = c.found_w - b.found_w
        weak = j.result == jg.PASS and gain < margins.found_gain + STRONG
        ch = [x for x in j.changes if x.judged]
        judged["candidates"][n] = {"describe": describe, "kind": kind, "verdict": j.result, "weak": weak, "reason": j.verdict.reason,
                                   "clauses": [dataclasses.asdict(x) for x in j.verdict.clauses], "gain": round(gain, 4),
                                   "gained": sum(x.kind == "gained" for x in ch), "lost": sum(x.kind == "lost" for x in ch),
                                   "settings": {c: assign[ss[0]] for c, ss in L.by_cond.items()} if kind != "held out" or "rot" not in n else None,
                                   **tallies(runs[n].counts)}
        print(f"{n:24s} {j.result}{' (WEAK)' if weak else ''}: found {b.found_w:.1f} -> {c.found_w:.1f} ({gain:+.1f}), per frame {b.found} -> {c.found}, "
              f"boxes not on their barrel {b.extra_w:.1f} -> {c.extra_w:.1f}", flush=True)
    (OUT / "judged.json").write_text(json.dumps(judged, indent=1, default=str) + "\n")
    (OUT / "thresholds.json").write_text(json.dumps({"hand": hand, "proposals_median": prop, "oracle": oracle}, indent=1) + "\n")
    if sheets:
        make_sheets(L, A, runs, js, truth)


# ---------------------------------------------------------------- contact sheets (pictures to look at; not committed)

def make_sheets(L: Layout, A: dict, runs: dict, js: dict, truth) -> None:
    import cv2
    import hs_slider as tool
    base = hl.adopted_model()
    fixed = six_of(hl.thresholds_from_model(base))
    out = OUT / "sheets"
    out.mkdir(parents=True, exist_ok=True)
    size, font = 210, cv2.FONT_HERSHEY_SIMPLEX

    def setting(name: str, stem: str):
        return fixed if name == "today" else (A[name][2].get(stem) or fixed)

    def panel(bgr, stem, name, g) -> np.ndarray:
        x0, y0, x1, y1 = g.bbox
        if name is None:
            pic = bgr.copy()
            cv2.rectangle(pic, (x0, y0), (x1 - 1, y1 - 1), (255, 255, 255), 1)
        else:
            mask = pl.segment(pl.Frame.from_image(bgr), model_of(base, setting(name, stem)))[0]
            pic = tool.seg_picture(bgr, mask, runs[name].boxes[stem], [{"bbox": g.bbox}], True, True, "flat")
        half = int(0.9 * max(x1 - x0, y1 - y0)) + 14
        pad = cv2.copyMakeBorder(pic, half, half, half, half, cv2.BORDER_CONSTANT, value=(0, 0, 0))
        cx, cy = (x0 + x1) // 2 + half, (y0 + y1) // 2 + half
        return cv2.resize(pad[cy - half:cy + half, cx - half:cx + half], (size, size), interpolation=cv2.INTER_NEAREST)

    def sheet(title: str, items: list, a: str, b: str) -> None:
        tiles = []
        for stem, gi in items:
            jg.require_train([stem])
            bgr = io.load_image(io.find_image(stem))
            g = truth.gts[stem][gi]
            row = np.hstack([panel(bgr, stem, None, g), panel(bgr, stem, a, g), panel(bgr, stem, b, g)])
            head = np.full((32, row.shape[1], 3), 32, np.uint8)
            cv2.putText(head, f"{ct.condition_of(stem)} {short(stem)} #{gi + 1} {dtp.COLOR_NAMES[g.color]}   {a}: {runs[a].counts[stem].gt[gi]}   {b}: {runs[b].counts[stem].gt[gi]}",
                        (4, 12), font, 0.36, (235, 235, 235), 1, cv2.LINE_AA)
            cv2.putText(head, f"{a} {text_of(setting(a, stem))}   |   {b} {text_of(setting(b, stem))}", (4, 27), font, 0.34, (0, 255, 255), 1, cv2.LINE_AA)
            tiles.append(np.vstack([head, row]))
        per = 14
        for k in range(0, len(tiles), per):
            chunk = tiles[k:k + per]
            if len(chunk) % 2:
                chunk.append(np.zeros_like(chunk[0]))
            pic = np.vstack([np.hstack(chunk[i:i + 2]) for i in range(0, len(chunk), 2)])
            name = f"{title}_{k // per + 1:02d}.jpg"
            cv2.imwrite(str(out / name), pic, [cv2.IMWRITE_JPEG_QUALITY, 82])
        print(f"  sheets: {title}: {len(items)} barrels on {(len(tiles) + per - 1) // per} sheet(s)")

    def changed(name: str, kind: str) -> list:
        return [(x.stem, x.index) for x in js[name].changes if x.judged and x.kind == kind]

    def state(name: str, stem: str, gi: int) -> str:
        return runs[name].counts[stem].gt[gi]
    prim = f"cal_core_{PRIMARY}"
    sheet("cal_core_gained", changed(prim, "gained"), "today", prim)
    sheet("cal_core_lost", changed(prim, "lost"), "today", prim)
    every = [(s, i) for s in L.ordinary for i in range(len(truth.gts[s]))]
    sheet("hand_finds_cal_core_misses", [(s, i) for s, i in every if state("hand", s, i) == ct.FOUND and state(prim, s, i) != ct.FOUND], "hand", prim)
    sheet("oracle_still_missed", [(s, i) for s, i in every if state("oracle", s, i) != ct.FOUND], prim, "oracle")
    bath = [(s, i) for s, i in every if ct.condition_of(s) == "lampwarm6_bathtile"]
    sheet("warm_bathroom_hand_vs_relabel", bath, "hand", "relabel")
    sheet("otherlight_lost", [(s, i) for s, i in every if state(prim, s, i) == ct.FOUND and state(f"cal_otherlight_{PRIMARY}", s, i) != ct.FOUND],
          prim, f"cal_otherlight_{PRIMARY}")


# ---------------------------------------------------------------- stage 4: each frame in turn; another light; another place

def _cross(args) -> tuple:
    """One target condition: every given setting on every one of its frames. Returns {key: {stem: [found, barrels, boxes not on their barrel]}}."""
    import cv2
    cv2.setNumThreads(1)
    cond, stems, sixes = args
    base = hl.adopted_model()
    out = {k: {} for k in sixes}
    for s in stems:
        label = io.load_boxes(s, check_image=False)
        frame, gts, clean, seen = jg.load_frame(s), dtp.barrels_from_boxes(label), bool(label.get("clean", True)), {}
        for k, six in sixes.items():
            out[k][s] = list(count_frame(s, frame, gts, clean, base if six is None else model_of(base, tuple(six)), seen))
    return cond, out


def stage_cross(jobs: int) -> None:
    L, S = layout(), load_settings()
    F = S["frames"]
    tasks = []
    for c, ss in L.by_cond.items():
        sixes = {"fixed": None}
        sixes.update({f"frame:{g}": F[g][PRIMARY] for g in L.eligible[c]})            # each frame of this condition in turn
        sixes.update({f"cond:{src}": F[L.cal[src]][PRIMARY] for src in L.by_cond})    # the calibration frame of every condition
        tasks.append((c, ss, sixes))
    res = {}
    with Pool(jobs) as pool:
        for c, r in pool.imap_unordered(_cross, tasks, chunksize=1):
            res[c] = r
            print(f"  cross: {c} done", flush=True)
    (OUT / "cross.json").write_text(json.dumps({"made": dt.date.today().isoformat(), "git": bcv.git_hash(), "primary": PRIMARY,
                                                "targets": dict(sorted(res.items()))}, indent=1) + "\n")


# ---------------------------------------------------------------- the report

def _pf(t: dict) -> str:
    return f"{t['found_w']:.1f} ({t['found']})"


def stage_report() -> None:
    L, S = layout(), load_settings()
    J = json.loads((OUT / "judged.json").read_text())
    X = json.loads((OUT / "cross.json").read_text())["targets"]
    O = json.loads((OUT / "oracle.json").read_text())["conditions"]
    T = json.loads((OUT / "thresholds.json").read_text())
    C, today, vendor, m = J["candidates"], J["today"], J["vendor"], J["margins"]
    prim = f"cal_core_{PRIMARY}"
    rots = [f"cal_rot{r}_{PRIMARY}" for r in ROTATIONS]
    places = list(today["places"])
    lines = [f"# One setting per place, without sliders: results ({J['made']}, git {J['git']})", "",
             "`python barrels/experiments/2026-11-26_place_ceiling/run.py all` (plan: `../../experiments/2026-11-26_place_ceiling/PREREG.md`). Train frames only; "
             f"no test frame opened. {len(L.ordinary)} ordinary train frames, {len(L.by_cond)} conditions at {len(places)} places: {today['all']['placements']} placements, "
             f"{today['all']['barrels']} barrels when every light is counted. Baseline everywhere: today's default (the fixed colors). "
             f"Margins: found better above +{m['found_gain']:.2f} placements, worse below -{m['found_loss']:.2f}; boxes not on their barrel worse above +{m['extra_rise']:.2f}.", "",
             "## Every judged candidate", "",
             "| candidate | kind | found, placements | per frame | found either way | boxes not on their barrel | on empty frames: clean / with clutter | gained / lost (per frame) | verdict |",
             "|---|---|---|---|---|---|---|---|---|"]
    t0 = today["all"]
    for n, c in C.items():
        a = c["all"]
        lines.append(f"| `{n}` | {c['kind']} | {t0['found_w']:.1f} → {a['found_w']:.1f} ({c['gain']:+.1f}) | {t0['found']} → {a['found']} | {a['found_w'] + a['off_w']:.1f} | "
                     f"{t0['extra_w']:.1f} → {a['extra_w']:.1f} ({t0['extra']} → {a['extra']}) | {a['clean_empty']} / {a['cluttered_empty_w']:.1f} | "
                     f"{c['gained']} / {c['lost']} | **{c['verdict']}{' (WEAK)' if c['weak'] else ''}** |")
    lines += ["", "What each candidate is:", ""] + [f"- `{n}`: {c['describe']}." for n, c in C.items()]
    rw = [C[r]["all"]["found_w"] for r in rots]
    rf = [C[r]["all"]["found"] for r in rots]
    re = [C[r]["all"]["extra_w"] for r in rots]
    lines += ["", f"Each frame in turn, the {len(rots)} rotations together: found {np.mean(rw):.1f} placements on average (lowest {min(rw):.1f}, highest {max(rw):.1f}); "
              f"per frame {np.mean(rf):.1f} ({min(rf)} to {max(rf)}); boxes not on their barrel {np.mean(re):.1f} ({min(re):.1f} to {max(re):.1f}); verdicts: "
              + ", ".join(C[r]["verdict"] + (" (WEAK)" if C[r]["weak"] else "") for r in rots) + ".", ""]

    # ---- table D
    def cell(t: dict | None, star: bool = False) -> str:
        if t is None or not t.get("frames"):
            return "-"
        if star:
            return f"{t['found_w']:.1f}* ({t['found']}*)"
        return f"{t['found_w']:.1f} ({t['found']}) / {t['extra_w']:.1f}"

    def rot_cell(key: str, p: str | None) -> str:
        ts = [(C[r][key] if p is None else C[r][key].get(p)) for r in rots]
        return f"{np.mean([t['found_w'] for t in ts]):.1f} ({np.mean([t['found'] for t in ts]):.1f}) / {np.mean([t['extra_w'] for t in ts]):.1f}"
    cols = [("fixed", None), ("one frame, core_01 (held out)", prim), ("one frame, each in turn (held out, mean)", "rot"), ("hand thresholds", "hand"),
            ("relabelled hand", "relabel"), ("oracle", "oracle"), ("vendor", "vendor")]
    lines += ["## D. By place: found placements (found per frame) / boxes not on their barrel, once per arrangement", "",
              "| place | placements (barrels, lights) | " + " | ".join(n for n, _ in cols) + " |", "|---|---|" + "---|" * len(cols)]

    def row(name: str, key: str, p: str | None, bold: bool = False) -> str:
        src = today[key] if p is None else today[key][p]
        cells = []
        for _, k in cols:
            if k is None:
                cells.append(cell(src))
            elif k == "rot":
                cells.append(rot_cell(key, p))
            elif k == "vendor":
                v = vendor[key] if p is None else vendor[key].get(p)
                cells.append(cell(v, star=bool(v and v.get("assumed_frames"))))
            else:
                cells.append(cell(C[k][key] if p is None else C[k][key].get(p)))
        b = "**" if bold else ""
        return f"| {b}{name}{b} | {src['placements']} ({src['barrels']}, {src['conditions']}) | " + " | ".join(f"{b}{x}{b}" for x in cells) + " |"
    for p in places:
        lines.append(row(p, "places", p))
    lines.append(row("the six places with vendor files", "measured", None, True))
    lines.append(row("all eight places", "all", None, True))
    lines += ["", "\\* = the vendor is ASSUMED to find every barrel on the two white tables without vendor files (home, campus; Tanush 2026-11-26); "
              "a starred total holds assumed frames. The vendor's row for the six measured places is measured.", ""]
    v6, f6 = vendor["measured"], today["measured"]
    gap = v6["found_w"] - f6["found_w"]
    lines += ["### The gap to the vendor on the six measured places", "",
              f"Fixed colors {f6['found_w']:.1f}, the vendor {v6['found_w']:.1f} of {f6['placements']} placements: a gap of {gap:.1f}.", "",
              "| arm | found, placements | gap to the vendor closed | found either way | boxes not on their barrel |", "|---|---|---|---|---|",
              f"| fixed | {f6['found_w']:.1f} | 0 % | {f6['found_w'] + f6['off_w']:.1f} | {f6['extra_w']:.1f} |"]
    for label, k in cols[1:-1]:
        if k == "rot":
            fw = float(np.mean([C[r]["measured"]["found_w"] for r in rots]))
            ow = float(np.mean([C[r]["measured"]["off_w"] for r in rots]))
            ew = float(np.mean([C[r]["measured"]["extra_w"] for r in rots]))
        else:
            fw, ow, ew = C[k]["measured"]["found_w"], C[k]["measured"]["off_w"], C[k]["measured"]["extra_w"]
        lines.append(f"| {label} | {fw:.1f} | {100 * (fw - f6['found_w']) / gap:.0f} % | {fw + ow:.1f} | {ew:.1f} |")
    lines += [f"| vendor | {v6['found_w']:.1f} | 100 % | {v6['found_w'] + v6['off_w']:.1f} | {v6['extra_w']:.1f} |", ""]

    # ---- A: the bathroom
    lines += ["## A. The bathroom, by lamp: found per frame", "", "| condition | barrels | fixed | hand | relabelled | relabelled, blue only | one frame, core_01 | oracle | vendor |",
              "|---|---|---|---|---|---|---|---|---|"]
    for c in BATH:
        lines.append(f"| {c} | {today['conditions'][c]['barrels']} | {today['conditions'][c]['found']} | " + " | ".join(
            str(C[k]["conditions"][c]["found"]) for k in ("hand", "relabel", "relabel_blue", prim, "oracle")) + f" | {vendor['conditions'][c]['found']} |")
    lines += ["", "The numbers used (orange hue low / high / S floor, blue hue low / high / S floor):", "",
              "| condition | hand (median of his labels) | relabelled (median of the proposals) | one frame, core_01 | oracle |", "|---|---|---|---|---|"]
    for c in BATH:
        lines.append(f"| {c} | {text_of(T['hand'][c])} | {text_of(T['proposals_median'][c])} | {text_of(S['frames'][L.cal[c]][PRIMARY])} | {text_of(T['oracle'][c])} |")

    # ---- every condition
    lines += ["", "## Every condition: found per frame", "",
              "| place / condition | barrels | fixed | one frame, core_01 | each in turn (mean of 4) | another light | another place | all frames pooled | hand | relabelled | oracle | vendor |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in L.by_cond:
        v = vendor["conditions"].get(c)
        vt = "-" if not v else (f"{v['found']}*" if v.get("assumed_frames") else str(v["found"]))
        lines.append(f"| {L.place(c)} / {c} | {today['conditions'][c]['barrels']} | {today['conditions'][c]['found']} | {C[prim]['conditions'][c]['found']} | "
                     f"{np.mean([C[r]['conditions'][c]['found'] for r in rots]):.1f} | {C[f'cal_otherlight_{PRIMARY}']['conditions'][c]['found']} | "
                     f"{C[f'cal_otherplace_{PRIMARY}']['conditions'][c]['found']} | {C['cal_all_net']['conditions'][c]['found']} | {C['hand']['conditions'][c]['found']} | "
                     f"{C['relabel']['conditions'][c]['found']} | {C['oracle']['conditions'][c]['found']} | {vt} |")
    lines += ["", "The setting each condition got (orange hue low / high / S floor, blue hue low / high / S floor):", "",
              "| condition | calibration frame | its setting (mid) | its net setting | the tool's proposal | hand | oracle (seed, moves) |", "|---|---|---|---|---|---|---|"]
    for c in L.by_cond:
        f = S["frames"][L.cal[c]]
        lines.append(f"| {c} | {short(L.cal[c])} | {text_of(f['mid'])} | {text_of(f['net'])} | {text_of(f['tool'])} | {text_of(T['hand'][c]) if c in T['hand'] else '-'} | "
                     f"{text_of(O[c]['best'])} ({O[c]['seed']}, {O[c]['moves']}) |")

    # ---- each frame in turn, by the kind of calibration shot
    by_scene, per_cond = defaultdict(lambda: [0, 0, 0, 0, 0]), {}
    for c, r in X.items():
        shares = []
        for g in L.eligible[c]:
            got = r[f"frame:{g}"]
            others = [s for s in L.by_cond[c] if s != g]
            f, n, e = (sum(got[s][i] for s in others) for i in range(3))
            fx = sum(r["fixed"][s][0] for s in others)
            shares.append((f, n, fx, short(g), e))
            a = by_scene[scene_of(g)]
            a[0] += f; a[1] += n; a[2] += fx; a[3] += 1; a[4] += e
        per_cond[c] = shares
    lines += ["", "## B. Which frame calibrates: each frame in turn (found per frame on the OTHER frames of its condition)", "",
              "| condition | frames that can calibrate | fixed, mean | calibrated, mean | worst calibration frame | best calibration frame |", "|---|---|---|---|---|---|"]
    for c, sh in per_cond.items():
        w, b = min(sh, key=lambda x: x[0] / max(1, x[1])), max(sh, key=lambda x: x[0] / max(1, x[1]))
        lines.append(f"| {c} | {len(sh)} | {np.mean([x[2] for x in sh]):.1f} of {np.mean([x[1] for x in sh]):.1f} | {np.mean([x[0] for x in sh]):.1f} | "
                     f"{w[3]}: {w[0]} of {w[1]} | {b[3]}: {b[0]} of {b[1]} |")
    lines += ["", "By the kind of shot that calibrates (all conditions together; found on the other frames of the same condition):", "",
              "| calibration shot | times used | fixed | calibrated | share found | boxes not on their barrel |", "|---|---|---|---|---|---|"]
    for sc, (f, n, fx, k, e) in sorted(by_scene.items(), key=lambda x: -x[1][3]):
        lines.append(f"| {sc} | {k} | {fx} of {n} | {f} of {n} | {100 * f / max(1, n):.0f} % (fixed {100 * fx / max(1, n):.0f} %) | {e} |")

    # ---- another light, another place
    def block(src: str, tgt: str) -> tuple:
        got = X[tgt][f"cond:{src}"]
        ss = [s for s in L.by_cond[tgt] if not (src == tgt and s == L.cal[src])]
        return sum(got[s][0] for s in ss), sum(got[s][1] for s in ss), sum(X[tgt]["fixed"][s][0] for s in ss)
    lines += ["", "## B. One light of a place applied to the other lights (found per frame; rows = the light whose core_01 set the numbers; the same light: its other frames only)", ""]
    for p, cs in L.conds_of.items():
        if len(cs) < 2:
            continue
        lines += [f"**{p}**", "", "| setting from \\ applied to | " + " | ".join(cs) + " |", "|---|" + "---|" * len(cs),
                  "| (fixed colors) | " + " | ".join(f"{sum(X[t]['fixed'][s][0] for s in L.by_cond[t])} of {sum(X[t]['fixed'][s][1] for s in L.by_cond[t])}" for t in cs) + " |"]
        for src in cs:
            lines.append(f"| {src} | " + " | ".join(("**%d of %d**" if src == t else "%d of %d") % block(src, t)[:2] for t in cs) + " |")
        lines.append("")
    same = other_light = other_place = None
    agg = {"the same condition (its other frames)": [0, 0, 0], "another light of the same place": [0, 0, 0], "another place": [0, 0, 0]}
    for tgt in L.by_cond:
        for src in L.by_cond:
            f, n, fx = block(src, tgt)
            k = "the same condition (its other frames)" if src == tgt else "another light of the same place" if L.place(src) == L.place(tgt) else "another place"
            agg[k][0] += f; agg[k][1] += n; agg[k][2] += fx
    lines += ["## B. Where the calibration frame comes from (every pair of conditions; found per frame)", "",
              "| the setting comes from | found | share | fixed colors on the same frames |", "|---|---|---|---|"]
    for k, (f, n, fx) in agg.items():
        lines.append(f"| {k} | {f} of {n} | {100 * f / max(1, n):.1f} % | {fx} of {n} ({100 * fx / max(1, n):.1f} %) |")
    lines += ["", "Files: `settings.json` (the setting of every frame that can calibrate), `oracle.json`, `judged.json` (every tally), `cross.json`, "
              "`thresholds.json`, `judge/<candidate>/judge.md` (the judge's page: tables, every barrel gained and lost, the clauses), `sheets/` (contact sheets, not committed).", ""]
    (OUT / "summary.md").write_text("\n".join(lines))
    print("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=("settings", "oracle", "judge", "cross", "report", "all"))
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--no-sheets", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.stage in ("settings", "all"):
        stage_settings(args.jobs)
    if args.stage in ("oracle", "all"):
        stage_oracle(args.jobs)
    if args.stage in ("judge", "all"):
        stage_judge(not args.no_sheets)
    if args.stage in ("cross", "all"):
        stage_cross(args.jobs)
    if args.stage in ("report", "all"):
        stage_report()
    return 0


if __name__ == "__main__":
    sys.exit(main())
