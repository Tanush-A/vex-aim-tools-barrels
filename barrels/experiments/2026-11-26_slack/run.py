#!/usr/bin/env python3
"""The slack experiment: every arm of ``DetConfig.slack`` against today's detector ON THE SAME MASK (plan: PREREG.md).

    cd barrels && env PYTHONPATH=src python experiments/2026-11-26_slack/run.py [--jobs 8] [--no-sheets]         # round 1: A, B, C, AB, ABC
    cd barrels && env PYTHONPATH=src python experiments/2026-11-26_slack/run.py --round round2 --arms B,C,D      # round 2 (the addendum of PREREG.md)

Train frames only: every frame is read by ``judge.load_frame``, which refuses anything else. No pixel is changed.

Per train frame the masks are made once: the fixed model's mask, the same with one and two pixels shaved off every
painted region, with one pixel added; the same three for the hand thresholds (the median per condition); and, on the
white tables, the two realistic damage levels of ``degrade.py`` with seeds 0, 1, 2. On every mask the detector runs
with ``slack`` = "" (today), "A", "B", "C", "AB", "ABC". Scoring is the standard judge's (``judge.compare``,
``counting.classify_frame``).

Outputs in results/2026-11-26_slack/<round>/: summary.md (every arm on every yardstick), changes.csv (every barrel whose
state changed), boxes_changed.csv and sheets/ (every box that appears or disappears on a real frame), raw.json,
and one folder of judge pages per arm for the unharmed masks.
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import cv2
import numpy as np

BARRELS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BARRELS / "src"))
from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import cv as bcv  # noqa: E402
from barrels import degrade as dg  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import hsrange as hx  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402

OUT = BARRELS / "results" / "2026-11-26_slack"
CAM = geo.AIM_4A8B6118_BOXFIT
ARMS = ("A", "B", "C", "AB", "ABC")
WHITE2 = ("home_white", "campus_study")                 # "the two white tables" of the audit
WHITE3 = WHITE2 + ("abp_white",)                        # the white-table frames the damage levels are applied to
LEVELS = tuple(dg.REALISTIC)
SEEDS = (0, 1, 2)
SHEET_VARIANTS = ("fixed", "fixed_e1", "fixed_e2", "hand", "hand_e1", "hand_e2")
NAMES = {"fixed": "fixed colors, unharmed", "fixed_e1": "fixed colors, 1 px shaved off", "fixed_e2": "fixed colors, 2 px shaved off",
         "fixed_d1": "fixed colors, 1 px added", "hand": "hand colors, unharmed", "hand_e1": "hand colors, 1 px shaved off",
         "hand_e2": "hand colors, 2 px shaved off"}
_K = np.ones((3, 3), np.uint8)
_STATE: dict = {}


def dmg(level: str, seed: int) -> str:
    return f"dmg|{level}|{seed}"


def erode(mask: np.ndarray, px: int) -> np.ndarray:
    """The mask with ``px`` pixels shaved off every painted region (each color by itself; the frame edge is not an edge)."""
    return dg.damage(mask, [], dg.Damage(erode_px=px))


def dilate(mask: np.ndarray) -> np.ndarray:
    """One pixel added to every painted region, onto unpainted pixels only (as the collapse harness does)."""
    out = mask.copy()
    for c in (io.ORANGE, io.BLUE):
        out[(out == 0) & (cv2.dilate((mask == c).astype(np.uint8), _K) > 0)] = c
    return out


def hand_thresholds(stems: list[str]) -> dict[str, tuple]:
    """condition -> the six numbers: the median of the slider labels of that condition's train frames (as
    experiments/2026-11-26_judge/run.py)."""
    by = defaultdict(list)
    for s in stems:
        if io.hs_path(s).exists():
            d = io.load_hs(s, check_image=False)
            by[ct.condition_of(s)].append([d["orange"]["h_lo"], d["orange"]["h_hi"], d["orange"]["s_lo"], d["blue"]["h_lo"], d["blue"]["h_hi"], d["blue"]["s_lo"]])
    return {c: tuple(int(round(x)) for x in np.median(np.array(v, float), 0)) for c, v in sorted(by.items())}


def _init(hand: dict, arms: tuple = ARMS) -> None:
    cv2.setNumThreads(1)
    base = hl.adopted_model()
    _STATE["model"] = base
    _STATE["hand"] = {c: hl.model_from_thresholds(base, hx.nested(dict(zip(hx.THRESHOLDS, six)))) for c, six in hand.items()}
    _STATE["cfg"] = {a: dataclasses.replace(det.DetConfig(), slack=a) for a in ("",) + tuple(arms)}


def masks_of(stem: str) -> dict[str, np.ndarray]:
    """Every mask of one TRAIN frame (``judge.load_frame`` refuses any other)."""
    frame = jg.load_frame(stem)
    fixed = pl.segment(frame, _STATE["model"])[0]
    out = {"fixed": fixed, "fixed_e1": erode(fixed, 1), "fixed_e2": erode(fixed, 2), "fixed_d1": dilate(fixed)}
    hm = _STATE["hand"].get(ct.condition_of(stem))
    hand = pl.segment(frame, hm)[0] if hm is not None else fixed          # a condition without slider labels keeps the fixed model
    out.update(hand=hand, hand_e1=erode(hand, 1), hand_e2=erode(hand, 2))
    if ct.place_of(stem) in WHITE3:
        boxes = [tuple(b["bbox"]) for b in io.load_boxes(stem, check_image=False)["barrels"]]
        for level in LEVELS:
            for seed in SEEDS:
                out[dmg(level, seed)] = dg.damage(fixed, boxes, dg.REALISTIC[level], seed)
    return out


def work(stem: str) -> tuple[str, dict]:
    """One frame: every mask, every arm -> the boxes, each with the rule that drew it."""
    res: dict = {}
    seen: dict = {}
    for variant, mask in masks_of(stem).items():
        key = mask.tobytes()
        if key not in seen:
            per = {}
            for arm, cfg in _STATE["cfg"].items():
                log: list = []
                preds = det.detect(mask, cfg, CAM, log=log)
                rules = {tuple(e["box"]): (e.get("rule") or e["stage"]) for e in log if e["why"] == "kept" and "box" in e}
                per[arm] = [(p, rules.get(tuple(p.bbox), "piece")) for p in preds]
            seen[key] = per
        res[variant] = seen[key]
    return stem, res


# ---------------------------------------------------------------- scoring

def make_run(res: dict, stems, gts: dict, clean: dict, variant: str, arm: str) -> jg.Run:
    name = f"{variant}, slack={arm or 'off'}"
    r = jg.Run(name, name)
    for s in stems:
        if variant not in res[s]:
            continue
        preds = [p for p, _ in res[s][variant][arm]]
        r.boxes[s] = preds
        r.counts[s] = ct.classify_frame(s, preds, gts[s], clean[s])
    return r


def tally(unharmed: jg.Run, base: jg.Run, cand: jg.Run, stems) -> dict:
    """Per-frame counts on ``stems``: found on the unharmed mask by today's detector, found on the harmed mask by today's
    detector and by the arm; of the barrels the harm lost, how many the arm finds; what else the arm gains and loses; the
    boxes that are not on their barrel; the boxes on empty frames."""
    t = dict(barrels=0, found_unharmed=0, found_base=0, found_arm=0, lost_to_harm=0, back=0, gained_other=0, lost_by_arm=0,
             off_base=0, off_arm=0, extra_base=0, extra_arm=0, empty_base=0, empty_arm=0, clean_empty_base=0, clean_empty_arm=0, boxes_base=0, boxes_arm=0)
    for s in stems:
        u, b, c = unharmed.counts[s], base.counts[s], cand.counts[s]
        for x, y, z in zip(u.gt, b.gt, c.gt):
            fu, fb, fc = x == ct.FOUND, y == ct.FOUND, z == ct.FOUND
            t["barrels"] += 1; t["found_unharmed"] += fu; t["found_base"] += fb; t["found_arm"] += fc
            t["lost_to_harm"] += fu and not fb
            t["back"] += fu and not fb and fc
            t["gained_other"] += fc and not fb and not fu
            t["lost_by_arm"] += fb and not fc
        t["off_base"] += b.n_gt(ct.OFF); t["off_arm"] += c.n_gt(ct.OFF)
        t["extra_base"] += b.extra; t["extra_arm"] += c.extra
        t["boxes_base"] += len(b.boxes); t["boxes_arm"] += len(c.boxes)
        if b.negative:
            t["empty_base"] += len(b.boxes); t["empty_arm"] += len(c.boxes)
            if b.clean:
                t["clean_empty_base"] += len(b.boxes); t["clean_empty_arm"] += len(c.boxes)
    return {k: int(v) for k, v in t.items()}


def cell(t: dict) -> str:
    return (f"{t['found_base']} → {t['found_arm']} (back {t['back']} of {t['lost_to_harm']}; other +{t['gained_other']} −{t['lost_by_arm']}); "
            f"not on barrel {t['extra_base']} → {t['extra_arm']}")


# ---------------------------------------------------------------- the contact sheets

def box_key(p) -> tuple:
    return (int(p.color), tuple(int(v) for v in p.bbox))


def changed_boxes(res: dict, runs: dict, stems, variants) -> list[dict]:
    """Every box an arm draws that today's detector does not draw on the same mask ("appears"), and the reverse
    ("disappears"), with the arms in which it does and its state against the hand boxes."""
    tiles: dict = {}
    for v in variants:
        for s in stems:
            if v not in res[s]:
                continue
            base = {box_key(p): (i, r) for i, (p, r) in enumerate(res[s][v][""])}
            for arm in ARMS:
                cand = {box_key(p): (i, r) for i, (p, r) in enumerate(res[s][v][arm])}
                for k, (i, rule) in cand.items():
                    if k not in base:
                        t = tiles.setdefault((v, s, "appears", k), {"variant": v, "stem": s, "kind": "appears", "color": k[0], "bbox": k[1], "arms": [],
                                                                    "state": runs[(v, arm)].counts[s].boxes[i], "rule": rule})
                        t["arms"].append(arm)
                for k, (i, rule) in base.items():
                    if k not in cand:
                        t = tiles.setdefault((v, s, "disappears", k), {"variant": v, "stem": s, "kind": "disappears", "color": k[0], "bbox": k[1], "arms": [],
                                                                       "state": runs[(v, "")].counts[s].boxes[i], "rule": rule})
                        t["arms"].append(arm)
    out = sorted(tiles.values(), key=lambda t: (SHEET_VARIANTS.index(t["variant"]) if t["variant"] in SHEET_VARIANTS else 99, t["stem"], t["kind"], t["bbox"]))
    for n, t in enumerate(out, 1):
        t["tile"] = n
    return out


def draw_tile(t: dict, frame_bgr: np.ndarray, mask: np.ndarray, gts: list, base_boxes: list, size: int = 220) -> np.ndarray:
    x0, y0, x1, y1 = t["bbox"]
    pad = max(40, int(0.8 * max(x1 - x0, y1 - y0)))
    cx0, cy0, cx1, cy1 = max(0, x0 - pad), max(0, y0 - pad), min(640, x1 + pad), min(480, y1 + pad)
    side = max(cx1 - cx0, cy1 - cy0)
    paint = np.zeros((*mask.shape, 3), np.uint8)
    paint[mask == io.ORANGE] = (0, 140, 255); paint[mask == io.BLUE] = (255, 120, 0)
    panels = []
    for img, interp in ((frame_bgr, cv2.INTER_LINEAR), (paint, cv2.INTER_NEAREST)):
        canvas = np.zeros((side, side, 3), np.uint8)
        canvas[:cy1 - cy0, :cx1 - cx0] = img[cy0:cy1, cx0:cx1]
        big = cv2.resize(canvas, (size, size), interpolation=interp)
        f = size / side

        def rect(b, color, thick=1):
            cv2.rectangle(big, (int((b[0] - cx0) * f), int((b[1] - cy0) * f)), (int((b[2] - cx0) * f) - 1, int((b[3] - cy0) * f) - 1), color, thick)
        for g in gts:
            rect(g.bbox, (255, 255, 255))
        for b in base_boxes:
            rect(b.bbox, (160, 160, 160))
        rect(t["bbox"], (255, 0, 255) if t["kind"] == "appears" else (0, 0, 255), 2)
        panels.append(big)
    tile = np.full((size + 34, 2 * size + 4, 3), 30, np.uint8)
    tile[:size, :size] = panels[0]; tile[:size, size + 4:] = panels[1]
    name = t["stem"].replace("4A8B_", "")
    cv2.putText(tile, f"#{t['tile']} {name} [{t['variant']}]", (2, size + 13), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(tile, f"{t['kind']} {dtp.COLOR_NAMES[t['color']]} {'+'.join(t['arms'])} {t['state']} {t['rule']}", (2, size + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.38,
                (255, 0, 255) if t["kind"] == "appears" else (80, 80, 255), 1, cv2.LINE_AA)
    return tile


def write_sheets(tiles: list[dict], res: dict, gts: dict, hand: dict, out: Path, per_sheet: int = 20, cols: int = 4) -> int:
    """White = the hand boxes, gray = today's boxes on that mask, magenta = a box that appears, red = one that disappears.
    Left the photo, right the mask the detector saw."""
    out.mkdir(parents=True, exist_ok=True)
    for old in list(out.glob("sheet_*.png")) + list(out.glob("sheet_*.jpg")):
        old.unlink()
    _init(hand, ARMS)
    images, cache = [], {}
    for t in tiles:
        s = t["stem"]
        if cache.get("stem") != s:
            cache = {"stem": s, "frame": jg.load_frame(s), "masks": masks_of(s)}
        base_boxes = [p for p, _ in res[s][t["variant"]][""]]
        images.append(draw_tile(t, cache["frame"].bgr, cache["masks"][t["variant"]], gts[s], base_boxes))
    n = 0
    for i in range(0, len(images), per_sheet):
        chunk = images[i:i + per_sheet]
        h, w = chunk[0].shape[:2]
        rows = (len(chunk) + cols - 1) // cols
        sheet = np.zeros((rows * (h + 6), cols * (w + 6), 3), np.uint8)
        for j, im in enumerate(chunk):
            r, c = divmod(j, cols)
            sheet[r * (h + 6):r * (h + 6) + h, c * (w + 6):c * (w + 6) + w] = im
        n += 1
        cv2.imwrite(str(out / f"sheet_{n:02d}.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])
    return n


# ---------------------------------------------------------------- main

def main() -> int:
    global ARMS, OUT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--no-sheets", action="store_true")
    ap.add_argument("--round", default="round1", help="the subfolder of results/2026-11-26_slack/ to write to")
    ap.add_argument("--arms", default=",".join(ARMS), help="the values of DetConfig.slack to judge, separated by commas")
    args = ap.parse_args()
    ARMS, OUT = tuple(args.arms.split(",")), OUT / args.round
    OUT.mkdir(parents=True, exist_ok=True)
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    judged_stems = ordinary + frames[cnd.EXTREME] + frames[cnd.UNLISTED]
    all_stems = judged_stems + frames[cnd.EXCLUDED]
    jg.require_train(all_stems)
    truth = jg.load_truth(judged_stems)
    gts, clean = ct.load_gts(all_stems)
    hand = hand_thresholds(all_stems)

    res: dict = {}
    with Pool(args.jobs, initializer=_init, initargs=(hand, ARMS)) as pool:
        for i, (stem, r) in enumerate(pool.imap_unordered(work, all_stems, chunksize=2)):
            res[stem] = r
            if (i + 1) % 50 == 0:
                print(f"  {i + 1}/{len(all_stems)} frames", flush=True)

    variants = list(NAMES) + [dmg(lv, sd) for lv in LEVELS for sd in SEEDS]
    runs = {(v, a): make_run(res, all_stems, gts, clean, v, a) for v in variants for a in ("",) + ARMS}
    margins = jg.load_margins()
    groups = {"the two white tables": [s for s in ordinary if ct.place_of(s) in WHITE2],
              "the other ordinary places": [s for s in ordinary if ct.place_of(s) not in WHITE2],
              "all ordinary": ordinary}
    hand_stems = [s for s in ordinary if ct.condition_of(s) in hand]
    white3 = [s for s in ordinary if ct.place_of(s) in WHITE3]
    empties = [s for s in all_stems if not gts[s]]

    raw: dict = {"git": bcv.git_hash(), "frames": {k: len(v) for k, v in frames.items()}, "hand_conditions": sorted(hand), "empty_frames": len(empties),
                 "white3_frames": len(white3), "arms": {}}
    judgements: dict = {}
    for arm in ARMS:
        a: dict = {"erosion": {}, "damage": {}, "unharmed": {}, "empty": {}, "hand": {}}
        for v in ("fixed_e1", "fixed_e2"):                                              # (a)
            a["erosion"][v] = {g: tally(runs[("fixed", "")], runs[(v, "")], runs[(v, arm)], ss) for g, ss in groups.items()}
            j = jg.compare(runs[(v, "")], runs[(v, arm)], frames, truth, margins)
            a["erosion"][v]["verdict"] = j.result
            a["erosion"][v]["found_w"] = [round(j.total[0].found_w, 2), round(j.total[1].found_w, 2)]
            a["erosion"][v]["extra_w"] = [round(j.total[0].extra_w, 2), round(j.total[1].extra_w, 2)]
        for lv in LEVELS:                                                               # (b)
            ts = [tally(runs[("fixed", "")], runs[(dmg(lv, sd), "")], runs[(dmg(lv, sd), arm)], white3) for sd in SEEDS]
            a["damage"][lv] = {k: sum(t[k] for t in ts) for k in ts[0]}
        j = jg.compare(runs[("fixed", "")], runs[("fixed", arm)], frames, truth, margins)   # (c)
        judgements[("fixed", arm)] = j
        jg.write(j, OUT / f"judge_unharmed_{arm}")
        a["unharmed"] = {"verdict": j.result, "reason": j.verdict.reason, "found_w": [round(j.total[0].found_w, 2), round(j.total[1].found_w, 2)],
                         "extra_w": [round(j.total[0].extra_w, 2), round(j.total[1].extra_w, 2)],
                         **{g: tally(runs[("fixed", "")], runs[("fixed", "")], runs[("fixed", arm)], ss) for g, ss in groups.items()}}
        for v in ("fixed", "fixed_e1", "fixed_e2", "fixed_d1", "hand", "hand_e1", "hand_e2"):   # (d) every empty train frame
            new = []
            for s in empties:
                b = {box_key(p) for p, _ in res[s][v][""]}
                new += [(s, k) for k in (box_key(p) for p, _ in res[s][v][arm]) if k not in b]
            a["empty"][v] = {"today": sum(len(res[s][v][""]) for s in empties), "arm": sum(len(res[s][v][arm]) for s in empties),
                             "new": [[s, dtp.COLOR_NAMES[k[0]], list(k[1])] for s, k in new]}
        for v in ("hand", "hand_e1", "hand_e2"):                                        # (e)
            a["hand"][v] = {"all ordinary": tally(runs[("hand", "")], runs[(v, "")], runs[(v, arm)], ordinary),
                            "conditions with hand labels": tally(runs[("hand", "")], runs[(v, "")], runs[(v, arm)], hand_stems)}
            j = jg.compare(runs[(v, "")], runs[(v, arm)], frames, truth, margins)
            a["hand"][v]["verdict"] = j.result
            a["hand"][v]["found_w"] = [round(j.total[0].found_w, 2), round(j.total[1].found_w, 2)]
            a["hand"][v]["extra_w"] = [round(j.total[0].extra_w, 2), round(j.total[1].extra_w, 2)]
            if v == "hand":
                jg.write(j, OUT / f"judge_hand_unharmed_{arm}")
        raw["arms"][arm] = a
    (OUT / "raw.json").write_text(json.dumps(raw, indent=1) + "\n")

    # every barrel whose state changed, per mask and arm
    with (OUT / "changes.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["mask", "arm", "stem", "barrel", "color", "bbox", "today_unharmed", "today_this_mask", "arm_this_mask", "place", "class"])
        for v in variants:
            un = "hand" if v.startswith("hand") else "fixed"
            for arm in ARMS:
                for s in all_stems:
                    if s not in runs[(v, arm)].counts:
                        continue
                    for i, (x, y, z) in enumerate(zip(runs[(un, "")].counts[s].gt, runs[(v, "")].counts[s].gt, runs[(v, arm)].counts[s].gt)):
                        if y != z:
                            g = gts[s][i]
                            w.writerow([v, arm, s, i + 1, dtp.COLOR_NAMES[g.color], " ".join(map(str, g.bbox)), x, y, z, ct.place_of(s), cnd.info(ct.condition_of(s)).klass])

    # every box that appears or disappears on a real frame
    tiles = changed_boxes(res, runs, all_stems, SHEET_VARIANTS)
    with (OUT / "boxes_changed.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["tile", "mask", "stem", "kind", "color", "bbox", "arms", "state_against_hand_boxes", "rule", "place", "class"])
        for t in tiles:
            w.writerow([t["tile"], t["variant"], t["stem"], t["kind"], dtp.COLOR_NAMES[t["color"]], " ".join(map(str, t["bbox"])), "+".join(t["arms"]), t["state"],
                        t["rule"], ct.place_of(t["stem"]), cnd.info(ct.condition_of(t["stem"])).klass])
    n_sheets = 0 if args.no_sheets else write_sheets(tiles, res, gts, hand, OUT / "sheets")
    dmg_tiles = changed_boxes(res, runs, white3, [dmg(lv, sd) for lv in LEVELS for sd in SEEDS])

    # ---- the page
    A = raw["arms"]
    L = [f"# The slack experiment: every arm on every yardstick (git {raw['git']})", "",
         f"`python barrels/experiments/2026-11-26_slack/run.py --round {OUT.name} --arms {','.join(ARMS)}`; plan: `experiments/2026-11-26_slack/PREREG.md`. Train frames only. Every arm is compared with "
         "today's detector **on the same mask**. Counts are per frame (a barrel once per light) unless they say \"placements\".", "",
         f"Frames: {len(ordinary)} ordinary ({len(groups['the two white tables'])} on the two white tables), {len(frames[cnd.EXTREME])} extreme, "
         f"{len(frames[cnd.EXCLUDED])} excluded, {len(frames[cnd.UNLISTED])} unlisted; {len(empties)} empty frames; hand thresholds for {len(hand)} conditions "
         f"({len(hand_stems)} ordinary frames).", "",
         "Cell: found by today's detector → by the arm (back X of Y = of the Y barrels today's detector finds on the unharmed mask and loses on this mask, the arm "
         "finds X; other +g −l = barrels the arm gains that were not found unharmed, and barrels the arm loses); then the boxes that are not on their barrel.", ""]
    for v, title in (("fixed_e1", "(a) Fixed colors, ONE pixel shaved off"), ("fixed_e2", "(a) Fixed colors, TWO pixels shaved off")):
        L += [f"## {title}", "", "| arm | " + " | ".join(groups) + " | judge on this mask (placements) | new boxes on empty frames |", "|---|" + "---|" * (len(groups) + 2)]
        for arm in ARMS:
            e = A[arm]["erosion"][v]
            L.append(f"| {arm} | " + " | ".join(cell(e[g]) for g in groups) + f" | {e['verdict']}: {e['found_w'][0]} → {e['found_w'][1]}, boxes {e['extra_w'][0]} → {e['extra_w'][1]} | "
                     f"{len(A[arm]['empty'][v]['new'])} |")
        t0 = A[ARMS[0]]["erosion"][v]["all ordinary"]
        L += ["", f"Today's detector on the unharmed mask finds {t0['found_unharmed']} of {t0['barrels']}; on this mask {t0['found_base']}.", ""]
    L += ["## (b) Realistic damage on the white tables (HOME, CAMPUS, ABP white; three seeds added up)", "", "| arm | " + " | ".join(LEVELS) + " |", "|---|" + "---|" * len(LEVELS)]
    for arm in ARMS:
        L.append(f"| {arm} | " + " | ".join(cell(A[arm]["damage"][lv]) for lv in LEVELS) + " |")
    t0 = A[ARMS[0]]["damage"][LEVELS[0]]
    L += ["", f"Unharmed, today's detector: {t0['found_unharmed']} of {t0['barrels']} (three times the {len(white3)} frames). "
              f"Boxes that appear or disappear on the damaged masks: {len(dmg_tiles)} (listed in raw form only; no sheet).", "",
          "## (c) The unharmed masks, fixed colors (the standard judge)", "",
          "| arm | verdict | found, placements | found, per frame | barrels gained / lost | boxes not on their barrel, per arrangement (per frame) | pages |", "|---|---|---|---|---|---|---|"]
    for arm in ARMS:
        u = A[arm]["unharmed"]; t = u["all ordinary"]
        L.append(f"| {arm} | **{u['verdict']}** | {u['found_w'][0]} → {u['found_w'][1]} | {t['found_base']} → {t['found_arm']} | +{t['found_arm'] - t['found_base'] + t['lost_by_arm']} / −{t['lost_by_arm']} | "
                 f"{u['extra_w'][0]} → {u['extra_w'][1]} ({t['extra_base']} → {t['extra_arm']}) | `judge_unharmed_{arm}/` |")
    L += ["", "## (d) Boxes on the empty train frames (every condition)", "",
          "| arm | " + " | ".join(NAMES[v] for v in NAMES) + " |", "|---|" + "---|" * len(NAMES)]
    for arm in ARMS:
        L.append(f"| {arm} | " + " | ".join(f"{A[arm]['empty'][v]['today']} → {A[arm]['empty'][v]['arm']} (new {len(A[arm]['empty'][v]['new'])})" for v in NAMES) + " |")
    news = sorted({(v, s, c, tuple(b)) for arm in ARMS for v in NAMES for s, c, b in A[arm]["empty"][v]["new"]})
    L += [""] + ([f"New boxes on empty frames: " + "; ".join(f"{s} [{v}] {c} {list(b)}" for v, s, c, b in news) + "."] if news else ["No arm draws a new box on any empty frame on any of these masks."]) + [""]
    L += ["The simulated scenes and the other masks of the collapse harness: `harness.md` (made by `harness_flag.py`).", "",
          "## (e) Hand-set colors (the median per condition)", ""]
    for v, title in (("hand", "unharmed"), ("hand_e1", "one pixel shaved off"), ("hand_e2", "two pixels shaved off")):
        L += [f"**{title}**", "", "| arm | all ordinary | the conditions with hand labels | judge on this mask (placements) |", "|---|---|---|---|"]
        for arm in ARMS:
            e = A[arm]["hand"][v]
            L.append(f"| {arm} | {cell(e['all ordinary'])} | {cell(e['conditions with hand labels'])} | {e['verdict']}: {e['found_w'][0]} → {e['found_w'][1]}, boxes {e['extra_w'][0]} → {e['extra_w'][1]} |")
        t0 = A[ARMS[0]]["hand"][v]["all ordinary"]
        L += ["", f"Today's detector, hand colors, unharmed: {t0['found_unharmed']} of {t0['barrels']}; on this mask {t0['found_base']}.", ""]
    by = defaultdict(lambda: defaultdict(int))
    for t in tiles:
        for arm in t["arms"]:
            by[arm][(t["kind"], t["state"])] += 1
    L += ["## Every box that appears or disappears on a real frame", "",
          f"{len(tiles)} boxes over the six real masks (fixed and hand colors; unharmed, one and two pixels shaved off), {n_sheets} sheets in `sheets/`, the list in "
          "`boxes_changed.csv` (tile number = the number on the sheet). Left the photo, right the mask the detector saw. White = the hand boxes, gray = today's "
          "boxes on that mask, magenta = a box that appears, red = one that disappears.", "",
          "| arm | appears: found | appears: on its barrel, box off | appears: second box | appears: wrong color | appears: on nothing | disappears: was found | disappears: was off | disappears: was not on a barrel |",
          "|---|---|---|---|---|---|---|---|---|"]
    for arm in ARMS:
        c = by[arm]
        L.append(f"| {arm} | {c[('appears', ct.FOUND)]} | {c[('appears', ct.OFF)]} | {c[('appears', ct.SECOND)]} | {c[('appears', ct.WRONG)]} | {c[('appears', ct.NOTHING)]} | "
                 f"{c[('disappears', ct.FOUND)]} | {c[('disappears', ct.OFF)]} | {c[('disappears', ct.SECOND)] + c[('disappears', ct.WRONG)] + c[('disappears', ct.NOTHING)]} |")
    L.append("")
    (OUT / "summary.md").write_text("\n".join(L))
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
