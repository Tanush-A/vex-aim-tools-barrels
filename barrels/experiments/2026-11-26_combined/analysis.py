#!/usr/bin/env python3
"""After the judged runs of experiment 2026-11-26_combined: the tables for parts C to G (PREREG.md, "Reported, never
judged"). Nothing here is a verdict and nothing here chooses a number.

    python barrels/experiments/2026-11-26_combined/analysis.py overlap          # C: what each winner finds that the other does not
    python barrels/experiments/2026-11-26_combined/analysis.py boxes [WAY]      # D: every box that is not on its barrel
    python barrels/experiments/2026-11-26_combined/analysis.py extreme [WAY]    # E: the extreme conditions, and Dave's frames
    python barrels/experiments/2026-11-26_combined/analysis.py vendor [WAY]     # F: against the vendor detector
    python barrels/experiments/2026-11-26_combined/analysis.py left [WAY]       # G: every barrel still missed, by cause
    python barrels/experiments/2026-11-26_combined/analysis.py all [WAY]

``WAY``: one of the five combinations (default: the pick written in summary.json by run.py). Reads
results/2026-11-26_combined/boxes.json (the held-out boxes of the judged run) and chosen.json (what each fold
picked); where a mask or a seed is needed the frame is run again with exactly those settings. Train frames only
(``judge.load_frame``), plus Dave's 12 office frames, which are in no split (``extreme``; indicative).
Writes overlap.md, overlap3.md, and false_boxes_<WAY>.md, extreme_<WAY>.md, vendor_<WAY>.md, left_<WAY>.md (and .json) next to the summary.
"""
from __future__ import annotations

import collections
import json
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cb_common as cb  # noqa: E402

cand = cb._load("cb_candidates", cb.HERE / "candidates.py")

from barrels import combined as cmb  # noqa: E402
from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import report as rp  # noqa: E402
from barrels import selfcal as sc  # noqa: E402
from barrels import splits as splits_mod  # noqa: E402
from barrels.detect_types import COLOR_NAMES, Barrel  # noqa: E402

OUT = cb.RESULTS
HIDDEN = {"occluded", "truncated", "held"}
BOX_WAYS = ("box_union", "box_agree")
CODE = {ct.FOUND: "found", ct.OFF: "box off", ct.MISSED: "missed"}
NOTES = cb.HERE / "notes.json"          # what the pictures show, written by hand after looking (objects, corrected causes)


def short(stem: str) -> str:
    return stem.replace("4A8B_", "")


def notes() -> dict:
    return json.loads(NOTES.read_text()) if NOTES.exists() else {}


@lru_cache(maxsize=1)
def data():
    """(frames by class, the labels, per detector the box states per frame, per detector the boxes per frame): the
    judged run, read back."""
    raw = json.loads((OUT / "boxes.json").read_text())
    frames = jg.train_frames()
    stems = frames[cnd.ORDINARY] + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    truth = jg.load_truth(stems)
    counts = {n: {s: ct.FrameCount.from_dict(v["count"]) for s, v in d.items()} for n, d in raw.items()}
    preds = {n: {s: [Barrel(color=b[0], bbox=tuple(b[1:5]), flags=frozenset(b[5])) for b in v["boxes"]] for s, v in d.items()} for n, d in raw.items()}
    return frames, truth, counts, preds


def arms_of(way: str) -> list[str]:
    """The detectors shown beside ``way``: today, each winner alone, mask_union, ``way``."""
    _, _, counts, _ = data()
    return list(dict.fromkeys(n for n in ("fixed", "nearmiss", "selfcal", "cn_alone", "mask_union", way) if n in counts))


def best_way() -> str:
    return json.loads((OUT / "summary.json").read_text())["picked"]["best_combination"]


def weights(stems) -> dict[str, float]:
    """1 / (the lights of its arrangement among these frames): how much one frame's barrel or box counts."""
    _, truth, _, _ = data()
    per = collections.Counter(truth.placements.arrangement[s] for s in stems)
    return {s: 1.0 / per[truth.placements.arrangement[s]] for s in stems}


def table(head: list[str], rows: list[list]) -> list[str]:
    return ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(str(v) for v in r) + " |" for r in rows] + [""]


# ---------------------------------------------------------------- one frame again, with the settings its fold picked

@lru_cache(maxsize=24)
def parts(stem: str, way: str):
    """(the frame, both winners alone on it, the way on it), with the settings the judged run used at its place."""
    frame = jg.load_frame(stem)
    spec, cfg, cnp = cand.settings3_for(ct.place_of(stem))
    nm_cfg = cand.nm_config(spec)
    both = cmb.box_union(frame, cand.MODEL, nm_cfg, cfg, cand.CAM)
    c = both if way in BOX_WAYS else cmb.ALL_WAYS[way](frame, cand.MODEL, nm_cfg, cfg, cand.CAM, None, cnp)
    return frame, both, c


def paint(mask, g) -> tuple[float, float] | None:
    """(the share of the barrel's two body bands painted its body color, the share of its stripe band painted the
    other color), the bands of ``selfcal.bands`` in its hand box; None when a band is off the frame."""
    b = sc.bands(g.bbox, mask.shape)
    if b is None:
        return None
    rects = (b["upper"], b["lower"])
    body = sum(int((mask[r[1]:r[3], r[0]:r[2]] == g.color).sum()) for r in rects) / max(1, sum((r[3] - r[1]) * (r[2] - r[0]) for r in rects))
    r = b["stripe"]
    return float(body), float((mask[r[1]:r[3], r[0]:r[2]] == sc.OTHER_OF[g.color]).mean())


def words(p) -> str:
    if p is None:
        return "bands off the frame"
    return ("both" if p[0] >= 0.5 and p[1] >= 0.5 else "body only" if p[0] >= 0.5 else "stripe only" if p[1] >= 0.5 else "neither") + f" ({p[0]:.2f}, {p[1]:.2f})"


def well(p) -> bool:
    return p is not None and p[0] >= 0.5 and p[1] >= 0.5


def touching(g, gts) -> bool:
    x0, y0, x1, y1 = g.bbox
    for h in gts:
        if h is g:
            continue
        a0, b0, a1, b1 = h.bbox
        if min(x1 + 2, a1) > max(x0 - 2, a0) and min(y1 + 2, b1) > max(y0 - 2, b0):
            return True
    return False


def diagnose(stem: str, i: int, way: str) -> dict:
    """Everything the tables say about one true barrel: what each mask paints of it, what happened to the seed
    candidates on it, what the near-miss step added in its box, and what the detector's reason log says there."""
    _, truth, counts, _ = data()
    g = truth.gts[stem][i]
    frame, both, c = parts(stem, way)
    x0, y0, x1, y1 = g.bbox
    seen = {"nearmiss mask": both.nm_mask, "selfcal mask": both.sc_mask} if way in BOX_WAYS else {f"{way} mask": c.mask}
    on = [x for x in c.seeds if x.why != "duplicate" and ct.on_share(x.bbox, g.bbox) >= 0.5]
    kept = [x for x in on if x.ok]
    seed = ("kept: " + "+".join(sorted({x.kind for x in kept})) if kept else
            "refused: " + "+".join(sorted({f"{x.kind}:{x.why}" for x in on})) if on else "no seed candidate")
    cn_on = [x for x in c.info.get("contrast", []) if x0 <= x.x < x1 and y0 <= x.row < y1]
    if way in cmb.WAYS3:
        contrast = ("no contrast candidate" if not cn_on else "painted" if any(x.info.get("painted") for x in cn_on) else
                    "refused: " + "+".join(sorted({r for x in cn_on for r in (x.info.get("reasons") or ["not painted"])})))
    else:
        contrast = "-"
    box_nm, box_st = both.nm_mask[y0:y1, x0:x1], both.strict[y0:y1, x0:x1]
    added = box_nm != box_st
    reasons = set()
    for name, m in seen.items():
        log: list = []
        det.detect(m, det.DetConfig(), cand.CAM, log)
        reasons |= {f"{e['stage']}: {e['why']}" for e in log if e["why"] != "kept" and ct.on_share(e["bbox"], g.bbox) >= 0.5}
    final = [paint(m, g) for m in seen.values()]
    return {"stem": stem, "barrel": i + 1, "color": COLOR_NAMES[g.color], "bbox": list(g.bbox), "flags": sorted(g.flags),
            "condition": ct.condition_of(stem), "place": ct.place_of(stem),
            "states": {n: counts[n][stem].gt[i] for n in arms_of(way)},
            "paint_fixed": paint(both.strict, g), "paint_nearmiss": paint(both.nm_mask, g), "paint_selfcal": paint(both.sc_mask, g),
            "paint_final": final, "well_painted": any(well(p) for p in final), "seed": seed, "contrast": contrast,
            "nm_added_body_px": int((added & (box_nm == g.color)).sum()), "nm_added_stripe_px": int((added & (box_nm == sc.OTHER_OF[g.color])).sum()),
            "touching": touching(g, truth.gts[stem]), "hidden": bool(set(g.flags) & HIDDEN), "detector": sorted(reasons)}


def cause(d: dict) -> str:
    """PREREG.md, part G, in its order."""
    if d["hidden"]:
        return "hidden or cut by the frame"
    p = d["paint_fixed"]
    if p is not None and p[0] < 0.5 and p[1] < 0.5:
        return "neither color painted"
    if d["touching"]:
        return "touching another barrel"
    if d["well_painted"]:
        return "the detector refused a well-painted barrel"
    return "a guard refused it"


# ---------------------------------------------------------------- C: the overlap

def overlap() -> str:
    frames, truth, counts, _ = data()
    stems = frames[cnd.ORDINARY]
    w = weights(stems)
    groups = collections.defaultdict(list)
    for s in stems:
        for i, _ in enumerate(truth.gts[s]):
            f, a, b = (counts[n][s].gt[i] for n in ("fixed", "nearmiss", "selfcal"))
            if f == ct.FOUND:
                groups["found by today's detector" if a == ct.FOUND and b == ct.FOUND else "LOST by a winner"].append((s, i))
            else:
                k = ("gained by both" if a == ct.FOUND and b == ct.FOUND else "gained by nearmiss only" if a == ct.FOUND else
                     "gained by selfcal only" if b == ct.FOUND else "found by neither")
                groups[k].append((s, i))
    order = ["found by today's detector", "gained by both", "gained by nearmiss only", "gained by selfcal only", "found by neither", "LOST by a winner"]
    out = ["# C. The overlap: what each winner finds that the other does not", "",
           "The held-out boxes of the judged run, ordinary conditions, 307 barrels counted per frame (172 placements). "
           "Made by `analysis.py overlap`.", ""]
    out += table(["barrels", "per frame", "placements"], [[k, len(groups[k]), f"{sum(w[s] for s, _ in groups[k]):.2f}"] for k in order])
    by = collections.defaultdict(collections.Counter)
    for k in order[1:5]:
        for s, _ in groups[k]:
            by[ct.condition_of(s)][k] += 1
    out += ["By condition (per frame; conditions with no such barrel are left out):", ""]
    out += table(["condition"] + order[1:5], [[c] + [v[k] for k in order[1:5]] for c, v in by.items()])
    rows_json = {}
    for k in ("gained by nearmiss only", "gained by selfcal only"):
        other = "selfcal" if "nearmiss" in k else "nearmiss"
        rows, js = [], []
        for s, i in groups[k]:
            d = diagnose(s, i, "box_union")
            js.append(d)
            rows.append([short(s), i + 1, d["color"], ",".join(d["flags"]) or "-", words(d["paint_fixed"]), CODE[d["states"][other]],
                         words(d["paint_nearmiss"]), f"{d['nm_added_body_px']} / {d['nm_added_stripe_px']}", words(d["paint_selfcal"]), d["seed"],
                         "yes" if d["touching"] else "", "; ".join(d["detector"]) or "-"])
        rows_json[k] = js
        out += [f"## {k} ({len(rows)})", "",
                f"paint = which of (body bands, stripe band) of the hand box a mask paints, with the two shares. `{other}` = that barrel's state under the other winner. "
                "near-miss added = pixels the near-miss step painted in the hand box (body color / stripe color). seed = what self-calibration did with the "
                "seed candidates on the barrel. detector = what the reason log says on that barrel in either winner's mask.", ""]
        out += table(["frame", "#", "color", "flags", "fixed colors paint", f"under `{other}`", "near-miss mask paints", "near-miss added (body / stripe px)",
                      "selfcal mask paints", "selfcal seed", "touching", "detector's reasons"], rows)
    n = notes().get("overlap")
    if n:
        out += ["## What the pictures show (written after looking at the sheets)", ""] + [f"- {x}" for x in n] + [""]
    (OUT / "overlap.json").write_text(json.dumps({"counts": {k: len(v) for k, v in groups.items()}, "only": rows_json}, indent=1) + "\n")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- D: every box that is not on its barrel

def boxes(way: str) -> str:
    frames, truth, counts, preds = data()
    obj = notes().get("objects", {})
    out = [f"# D. Every box of `{way}` that is not on its barrel", "",
           "The held-out boxes of the judged run. A box is listed when it is on nothing, a second box on a barrel, or on a barrel of the other color. "
           "weight = 1 / the lights its arrangement was shot under (how the judge counts it). 'today, this frame' = today's detector (fixed colors) "
           "draws a box on the same thing in this frame; 'today, another light' = it does so in another light of the same arrangement (the camera did "
           "not move between lights). 'nearmiss' / 'selfcal' = that winner alone draws a box on it in this frame. The object and the check that would "
           "remove it are from the pictures, written by hand; no rule was tuned or run on these frames. Made by `analysis.py boxes`.", ""]
    js = []
    for klass, title in ((cnd.ORDINARY, "Ordinary conditions (these are the boxes the judge counted)"), (cnd.EXTREME, "Extreme conditions (report only)")):
        stems = frames[klass]
        w = weights(stems)
        sib = collections.defaultdict(list)
        for s in stems:
            sib[truth.placements.arrangement[s]].append(s)
        rows, tot = [], collections.Counter()
        for s in stems:
            fc = counts[way][s]
            for p, st in zip(preds[way][s], fc.boxes):
                if st not in ct.EXTRA_STATES:
                    continue

                def on(name, stem):
                    return any(ct.on_share(q.bbox, p.bbox) >= 0.5 for q in preds[name][stem])
                here = on("fixed", s)
                other = [short(o).split("_")[0] for o in sib[truth.placements.arrangement[s]] if o != s and on("fixed", o)]
                kind = "empty frame, clean" if fc.negative and fc.clean else "empty frame with clutter" if fc.negative else ""
                key = f"{short(s)} {COLOR_NAMES[p.color]} {list(p.bbox)}"
                o = obj.get(key, {})
                rows.append([short(s), COLOR_NAMES[p.color], list(p.bbox), st.replace("_", " "), f"{w[s]:.2f}", kind or "-", "yes" if here else "no",
                             ", ".join(other) or "no", "yes" if on("nearmiss", s) else "no", "yes" if on("selfcal", s) else "no",
                             ("yes" if on("cn_alone", s) else "no") if "cn_alone" in preds else "-", o.get("object", ""), o.get("check", "")])
                tot["boxes"] += 1
                tot["weight"] += w[s]
                tot["today here"] += here
                tot["today here w"] += w[s] * here
                js.append({"class": klass, "stem": s, "color": COLOR_NAMES[p.color], "bbox": list(p.bbox), "state": st, "weight": w[s], "frame": kind,
                           "today_this_frame": here, "today_other_lights": other, "nearmiss": on("nearmiss", s), "selfcal": on("selfcal", s),
                           "contrast": on("cn_alone", s) if "cn_alone" in preds else None, **o})
        out += [f"## {title}: {tot['boxes']} boxes, {tot['weight']:.2f} counted once per arrangement; {tot['today here']} of them "
                f"({tot['today here w']:.2f}) are also drawn by today's detector in the same frame", ""]
        out += table(["frame", "color", "box", "state", "weight", "frame kind", "today, this frame", "today, another light", "nearmiss", "selfcal", "contrast",
                      "object (from the picture)", "what kind of check would remove it"], rows)
    arms = ["fixed", "nearmiss", "selfcal"] + [x for x in cmb.ALL_WAYS if x in counts]
    w = weights(frames[cnd.ORDINARY])
    rows = []
    for n in arms:
        c = collections.Counter()
        for s in frames[cnd.ORDINARY]:
            for st in counts[n][s].boxes:
                if st in ct.EXTRA_STATES:
                    c[st] += 1
                    c["w"] += w[s]
        rows.append([f"`{n}`" if n != "fixed" else "today", c[ct.NOTHING], c[ct.SECOND], c[ct.WRONG], f"{c['w']:.2f}"])
    out += ["## Every candidate, ordinary conditions: boxes not on their barrel, per frame", ""]
    out += table(["candidate", "on nothing", "second box", "wrong color", "counted once per arrangement"], rows)
    (OUT / f"false_boxes_{way}.json").write_text(json.dumps(js, indent=1) + "\n")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- E: the extreme conditions and Dave's frames

def _cells(t: ct.Tally) -> list:
    return [f"{t.found} ({t.found_w:.1f})", f"{t.off}", f"{t.missed}", f"{t.nothing} / {t.second} / {t.wrong} ({t.extra_w:.2f})", f"{t.empty} ({t.clean_empty})"]


def extreme(way: str) -> str:
    frames, truth, counts, _ = data()
    stems = frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    arms = {("today" if n == "fixed" else f"`{n}`"): n for n in arms_of(way)}
    sub = ["found per frame (placements)", "box off", "missed", "boxes: on nothing / second / wrong color (once per arrangement)", "boxes on empty frames (on clean ones)"]
    out = [f"# E. The extreme conditions (report only, never judged): `{way}` beside today's detector and each winner", "",
           "77 train frames: the orange wood desk under the lamp at six settings (10 frames each, one place, the same 21 placements under every setting), "
           "the black table by the window (10), the ottoman under the dim mid lamp (7; the same arrangements as the ordinary ottoman lights). Each frame "
           "is scored with the settings each winner's rule picked on ALL ordinary frames (the dark ottoman: by the fold that left the ottoman out). "
           "Found = the strict rule. **These frames are not blind:** both winners' authors saw per-condition counts on them while shaping the "
           "methods (PREREG.md). No number was chosen on them. Made by `analysis.py extreme`.", ""]
    for name, key in arms.items():
        rows = []
        for c, ss in list(ct.group_stems(stems, "condition").items()) + [("ALL 77 frames", stems)]:
            t = ct.tally(counts[key], ss, truth.placements)
            rows.append([c, t.frames, t.barrels, t.placements] + _cells(t))
        out += [f"## {name}", ""] + table(["condition", "frames", "barrels", "placements"] + sub, rows)
    rows = []
    for c, ss in list(ct.group_stems(stems, "condition").items()) + [("ALL", stems)]:
        ts = [ct.tally(counts[k], ss, truth.placements) for k in arms.values()]
        rows.append([c, ts[0].barrels] + [f"{t.found}" for t in ts] + [f"{t.extra}" for t in ts] + [f"{t.empty}" for t in ts])
    out += ["## Side by side, per frame", ""]
    out += table(["condition", "barrels"] + [f"found: {a}" for a in arms] + [f"boxes not on their barrel: {a}" for a in arms] + [f"on empty frames: {a}" for a in arms], rows)
    rows = []
    for p, ss in ct.group_stems(stems, "place").items():
        ts = [ct.tally(counts[k], ss, truth.placements) for k in arms.values()]
        rows.append([p, ts[0].conditions, ts[0].placements] + [f"{t.found_w:.1f}" for t in ts] + [f"{t.extra_w:.2f}" for t in ts])
    out += ["## By place, every placement once", ""]
    out += table(["place", "lights", "placements"] + [f"found: {a}" for a in arms] + [f"boxes not on their barrel: {a}" for a in arms], rows)
    out += dave(way)
    return "\n".join(out) + "\n"


def dave(way: str) -> list[str]:
    """Dave's office frames (DAVE_office_speckle, 12 frames, in no split; his boxes group touching barrels, so the
    numbers are indicative). Scored with the settings picked on all the ordinary frames."""
    from barrels import io, pipeline as pl
    splits = splits_mod.load_splits()
    sel = rp.select_frames(rp.labeled_stems(), splits)
    stems = [s for k, v in sel.sets.items() if rp.is_indicative(k) for s in v]
    rp.refuse_test_frames(stems, splits)
    if not stems:
        return ["## Dave's office frames", "", "None with a box label.", ""]
    spec, cfg, cnp = cand.settings3_for("(no such place)")
    nm_cfg = cand.nm_config(spec)
    fixed = jg.fixed_detector()
    dets = {"today": lambda s, f: fixed(s, f), "`nearmiss`": lambda s, f: cmb.nm_then_sc(f, cand.MODEL, nm_cfg, None, cand.CAM).boxes,
            "`selfcal`": lambda s, f: cmb.box_union(f, cand.MODEL, None, cfg, cand.CAM).boxes,
            "`cn_alone`": lambda s, f: cmb.cn_alone(f, cand.MODEL, None, None, cand.CAM, None, cnp).boxes,
            "`mask_union`": lambda s, f: cmb.mask_union(f, cand.MODEL, nm_cfg, cfg, cand.CAM).boxes}
    dets[f"`{way}`"] = lambda s, f: cmb.ALL_WAYS[way](f, cand.MODEL, nm_cfg, cfg, cand.CAM, None, cnp).boxes
    gts, clean = ct.load_gts(stems)
    placements = ct.build_placements(gts)
    counts = {n: {} for n in dets}
    for s in stems:
        frame = pl.Frame.from_image(io.load_image(io.find_image(s)))
        for a in (frame.bgr, frame.rgb, frame.sat, frame.val):
            a.setflags(write=False)
        for n, d in dets.items():
            counts[n][s] = ct.classify_frame(s, d(s, frame), gts[s], clean[s])
    rows = []
    for n in dets:
        t = ct.tally(counts[n], stems, placements)
        rows.append([n, t.frames, t.barrels, t.found, t.off, t.missed, f"{t.nothing} / {t.second} / {t.wrong}", f"{t.empty} ({t.clean_empty})"])
    (OUT / f"dave_{way}.json").write_text(json.dumps({n: {s: c.to_dict() for s, c in v.items()} for n, v in counts.items()}, indent=1) + "\n")
    return ["## Dave's office frames (the set the eval table calls DAVE; INDICATIVE only)", "",
            f"{len(stems)} frames, in no split (so not test frames), read directly. His boxes group touching barrels, so 'found' under the strict rule "
            f"undercounts, and a box on one barrel of a group can count as a second box. Settings: the ones picked on all ordinary frames "
            f"(near-miss `{spec}`; self-calibration {json.dumps(cand.settings_json("(no such place)")["sc"])}; contrast: the pick of its rule on all ordinary places).", ""] + \
        table(["detector", "frames", "label boxes", "found (strict)", "box off", "missed", "boxes: on nothing / second / wrong color", "on empty frames (clean)"], rows)


# ---------------------------------------------------------------- F: against the vendor

def vendor(way: str) -> str:
    frames, truth, counts, _ = data()
    splits = splits_mod.load_splits()
    sel = rp.select_frames(rp.labeled_stems(), splits)
    cov = rp.vendor_coverage(sel, splits)
    stems = [s for s in frames[cnd.ORDINARY] if s in cov.barrels]
    vc = {s: ct.classify_frame(s, cov.barrels[s], truth.gts[s], truth.clean[s]) for s in stems}
    arms = {**{("today" if n == "fixed" else f"`{n}`"): counts[n] for n in arms_of(way)}, "vendor": vc}
    groups = list(ct.group_stems(stems, "place").items()) + [("**six places**", stems)]
    tal = {p: [ct.tally(a, ss, truth.placements) for a in arms.values()] for p, ss in groups}
    tot = tal["**six places**"]
    out = [f"# F. Against the vendor detector: `{way}` beside today's detector, each winner and the vendor", "",
           f"The six places with vendor files: {tot[0].frames} frames, {tot[0].barrels} barrels counted per frame, {tot[0].placements} placements "
           f"(physical barrels) in {tot[0].arrangements} arrangements, {tot[0].conditions} lights. The accounting of `tools/report.py --vendor --places` "
           "(`counting.py`): found = the strict rule, every placement once (per frame in brackets). Ours = the held-out boxes of the judged run "
           "(leave one place out). The vendor = the boxes the robot saved with each frame. **Train frames, and our methods were shaped on them; the "
           "vendor was not.** Made by `analysis.py vendor`.", ""]
    head = ["place", "placements (per frame)"] + list(arms)

    def tab(title, f):
        return [f"### {title}", ""] + table(head, [[p, f"{ts[0].placements} ({ts[0].barrels})"] + [f(t) for t in ts] for p, ts in tal.items()])
    out += tab("Found (strict), placements (per frame)", lambda t: f"{t.found_w:.1f} ({t.found})")
    out += tab("Found with the box off (a same-color box is on the barrel and fails the strict rule)", lambda t: f"{t.off_w:.1f} ({t.off})")
    out += tab("Missed (no box of its color on it)", lambda t: f"{t.missed_w + 0.0:.1f} ({t.missed})".replace("-0.0", "0.0"))
    out += tab("Boxes on nothing, per frame (of them on empty frames)", lambda t: f"{t.nothing} ({t.empty})")
    out += tab("Boxes not on their barrel, once per arrangement (on nothing + second box + wrong color; per frame in brackets)",
               lambda t: f"{t.extra_w:.2f} ({t.nothing}+{t.second}+{t.wrong})")
    names = list(arms)
    wi = names.index(f"`{way}`")
    v, b = tot[-1], tot[wi]
    lose = [f"{p} ({ts[wi].found_w:.1f} against {ts[-1].found_w:.1f})" for p, ts in tal.items() if p != "**six places**" and ts[wi].found_w < ts[-1].found_w - 1e-9]
    win = [f"{p} ({ts[wi].found_w:.1f} against {ts[-1].found_w:.1f})" for p, ts in tal.items() if p != "**six places**" and ts[wi].found_w > ts[-1].found_w + 1e-9]
    out += ["### In one line each", "",
            f"- Total found: " + ", ".join(f"{n} {t.found_w:.1f} ({t.found})" for n, t in zip(names, tot)) + f" of {v.placements} ({v.barrels}).",
            f"- {names[wi]} against the vendor: {b.found_w - v.found_w:+.1f} placements ({b.found - v.found:+d} per frame). "
            f"On a barrel at all (found + box off): {b.found_w + b.off_w:.1f} against {v.found_w + v.off_w:.1f}.",
            f"- Places where {names[wi]} finds fewer than the vendor: {'; '.join(lose) or 'none'}.",
            f"- Places where it finds more: {'; '.join(win) or 'none'}.",
            "- The two white tables without vendor files (home, campus; 64 placements) are not in this table. There the vendor is ASSUMED to find "
            "every barrel (Tanush, 2026-11-26); every candidate here finds what today's detector finds there (63.0 of 64).", ""]
    (OUT / f"vendor_{way}.json").write_text(json.dumps({p.strip("*"): {n.strip("`"): t.to_dict() for n, t in zip(names, ts)} for p, ts in tal.items()}, indent=1) + "\n")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- G: what is left

def left(way: str) -> str:
    frames, truth, counts, _ = data()
    stems = frames[cnd.ORDINARY]
    w = weights(stems)
    fixes = notes().get("causes", {})
    rows = []
    for s in stems:
        for i, _ in enumerate(truth.gts[s]):
            if counts[way][s].gt[i] != ct.FOUND:
                d = diagnose(s, i, way)
                d["cause_by_rule"] = cause(d)
                fx = fixes.get(f"{short(s)} #{i + 1}")
                d["cause"], d["note"] = (fx["cause"], fx.get("note", "")) if fx else (d["cause_by_rule"], "")
                d["weight"] = w[s]
                rows.append(d)
    order = ["hidden or cut by the frame", "neither color painted", "touching another barrel", "a guard refused it", "the detector refused a well-painted barrel"]
    order += sorted({d["cause"] for d in rows} - set(order))
    out = [f"# G. What is left after `{way}`: every barrel it does not find on the ordinary conditions, by cause", "",
           f"The held-out boxes of the judged run: {len(rows)} barrels not found counted per frame, {sum(d['weight'] for d in rows):.2f} placements "
           f"(of 307 and 172). Not found = no strict hit: 'box off' (a box of its color is on it and fails the strict rule) or 'missed'. The causes and "
           "their order are in PREREG.md, part G; a cause corrected from the picture has a note. Made by `analysis.py left`.", ""]
    tab = []
    for k in order:
        sel = [d for d in rows if d["cause"] == k]
        tab.append([k, len(sel), f"{sum(d['weight'] for d in sel):.2f}", sum(1 for d in sel if d["states"][way] == ct.OFF),
                    ", ".join(f"{c} {n}" for c, n in collections.Counter(d["condition"] for d in sel).most_common())])
    tab.append(["**all**", len(rows), f"{sum(d['weight'] for d in rows):.2f}", sum(1 for d in rows if d["states"][way] == ct.OFF), ""])
    out += table(["cause", "per frame", "placements", "of them with a box on the barrel (box off)", "by condition (per frame)"], tab)
    for k in order:
        sel = [d for d in rows if d["cause"] == k]
        if not sel:
            continue
        out += [f"## {k} ({len(sel)})", ""]
        out += table(["frame", "#", "color", "flags", " / ".join(n if n != "fixed" else "today" for n in arms_of(way)), "fixed colors paint", "final mask paints",
                      "selfcal seed", "contrast candidate", "near-miss added (body / stripe px)", "touching", "detector's reasons", "note"],
                     [[short(d["stem"]), d["barrel"], d["color"], ",".join(d["flags"]) or "-",
                       " / ".join(CODE[d["states"][n]] for n in arms_of(way)), words(d["paint_fixed"]),
                       "; ".join(words(p) for p in d["paint_final"]), d["seed"], d["contrast"], f"{d['nm_added_body_px']} / {d['nm_added_stripe_px']}",
                       "yes" if d["touching"] else "", "; ".join(d["detector"]) or "-",
                       d["note"] + (f" (by rule: {d['cause_by_rule']})" if d["cause"] != d["cause_by_rule"] else "")] for d in sel])
    (OUT / f"left_{way}.json").write_text(json.dumps(rows, indent=1) + "\n")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- C with the third winner (addendum 2026-11-27)

def overlap3() -> str:
    """Which of the three winners finds each barrel today's detector misses; and every barrel near-miss or
    self-calibration finds that contrast does not, with why (contrast's candidate on it, from ``cn_alone``)."""
    frames, truth, counts, _ = data()
    stems = frames[cnd.ORDINARY]
    w = weights(stems)
    names = ("nearmiss", "selfcal", "cn_alone")
    groups = collections.defaultdict(list)
    for s in stems:
        for i, _ in enumerate(truth.gts[s]):
            if counts["fixed"][s].gt[i] == ct.FOUND:
                lost = [n for n in names if counts[n][s].gt[i] != ct.FOUND]
                groups["found by today's detector" + (f" (LOST by {', '.join(lost)})" if lost else "")].append((s, i))
                continue
            by = tuple(n for n in names if counts[n][s].gt[i] == ct.FOUND)
            groups[" + ".join(by) if by else "found by none of the three"].append((s, i))
    order = sorted(groups, key=lambda k: (-len(groups[k]), k))
    out = ["# C (addendum). The overlap of the three winners", "",
           "Held-out boxes of the judged runs, ordinary conditions, 307 barrels counted per frame (172 placements). A row = the set of winners that "
           "find the barrel (strict rule) among the barrels today's detector misses. Made by `analysis.py overlap3`.", ""]
    out += table(["found by", "per frame", "placements"], [[k, len(groups[k]), f"{sum(w[s] for s, _ in groups[k]):.2f}"] for k in order])
    sets = {n: {(s, i) for k, v in groups.items() for (s, i) in v if n in k.split(" + ")} for n in names}
    other = sets["nearmiss"] | sets["selfcal"]
    out += [f"- Gained by contrast: {len(sets['cn_alone'])} per frame. Gained by near-miss or self-calibration: {len(other)}; "
            f"of them contrast finds {len(other & sets['cn_alone'])}, and {len(other - sets['cn_alone'])} it does not. "
            f"Gained by contrast and by neither of the other two: {len(sets['cn_alone'] - other)}.", ""]
    rows, js = [], []
    for s, i in sorted(other - sets["cn_alone"]):
        d = diagnose(s, i, "cn_alone")
        js.append(d)
        rows.append([short(s), i + 1, d["color"], ",".join(d["flags"]) or "-", " / ".join(CODE[d["states"][n]] for n in ("nearmiss", "selfcal", "cn_alone")),
                     words(d["paint_fixed"]), d["contrast"], "; ".join(words(p) for p in d["paint_final"]), "yes" if d["touching"] else "",
                     "; ".join(d["detector"]) or "-"])
    out += [f"## Found by near-miss or self-calibration, not by contrast ({len(rows)})", "",
            "contrast candidate = what contrast's own path did on the barrel: no candidate (no stripe-like band at the size its row predicts), "
            "refused by a guard (the reasons), or painted (the detector then drew no strict box). final mask = contrast's mask.", ""]
    out += table(["frame", "#", "color", "flags", "nearmiss / selfcal / contrast", "fixed colors paint", "contrast candidate", "contrast mask paints",
                  "touching", "detector's reasons (contrast mask)"], rows)
    rows = []
    for s, i in sorted(sets["cn_alone"] - other):
        g = truth.gts[s][i]
        rows.append([short(s), i + 1, COLOR_NAMES[g.color], ",".join(sorted(g.flags)) or "-", ct.condition_of(s)])
    out += [f"## Found by contrast and by neither of the other two ({len(rows)})", ""] + table(["frame", "#", "color", "flags", "condition"], rows)
    by = collections.defaultdict(collections.Counter)
    for k in order:
        if k.startswith("found by today"):
            continue
        for s, _ in groups[k]:
            by[ct.condition_of(s)][k] += 1
    cols = [k for k in order if not k.startswith("found by today")]
    out += ["## By condition (per frame)", ""] + table(["condition"] + cols, [[c] + [v[k] for k in cols] for c, v in sorted(by.items())])
    n = notes().get("overlap3")
    if n:
        out += ["## What the pictures show", ""] + [f"- {x}" for x in n] + [""]
    (OUT / "overlap3.json").write_text(json.dumps({"groups": {k: len(v) for k, v in groups.items()}, "not_by_contrast": js}, indent=1, default=str) + "\n")
    return "\n".join(out) + "\n"


def main(argv) -> int:
    what = argv[0] if argv else "all"
    way = argv[1] if len(argv) > 1 else best_way()
    if way not in cmb.ALL_WAYS:
        raise SystemExit(f"unknown way {way!r}: one of {', '.join(cmb.ALL_WAYS)}")
    jobs = {"overlap": ("overlap.md", overlap), "overlap3": ("overlap3.md", overlap3), "boxes": (f"false_boxes_{way}.md", lambda: boxes(way)),
            "extreme": (f"extreme_{way}.md", lambda: extreme(way)), "vendor": (f"vendor_{way}.md", lambda: vendor(way)), "left": (f"left_{way}.md", lambda: left(way))}
    if what != "all" and what not in jobs:
        raise SystemExit(f"unknown part {what!r}: one of {', '.join(jobs)}, all")
    for k in (jobs if what == "all" else [what]):
        name, fn = jobs[k]
        text = fn()
        (OUT / name).write_text(text)
        print(text, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
