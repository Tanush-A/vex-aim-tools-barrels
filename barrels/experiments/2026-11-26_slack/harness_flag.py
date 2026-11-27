#!/usr/bin/env python3
"""Yardstick (d), second half: the 5435 masks of the collapse harness with the flag ON (plan: PREREG.md).

    cd barrels && env PYTHONPATH=src python experiments/2026-11-26_slack/harness_flag.py <inputs.pkl> <before.json> [scene_truth.json] [--jobs 8] [--sheet ARM]

``before.json`` = today's boxes on every input (run_detect.py of experiments/2026-11-26_collapse; the flag off must
reproduce it, which diff.py checks). For every arm: the inputs whose boxes change, per group, boxes added and
removed. Where the truth is known, both sides are scored with ``counting.classify_frame``: the groups made from
train frames (real, real_erode, real_dilate, hand, pool, damage) against the hand boxes, the simulated scenes against
the scene's own true boxes (scene_truth.py). ``--sheet ARM`` writes contact sheets of the scenes where that arm adds
a box that is not a strict hit.

Outputs: results/2026-11-26_slack/<round>/harness.md, harness.json, harness_sheets/."""
from __future__ import annotations

import argparse
import dataclasses
import json
import pickle
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import cv2
import numpy as np

BARRELS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BARRELS / "src"))
from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402

OUT = BARRELS / "results" / "2026-11-26_slack"
ARMS = ("A", "B", "C", "AB", "ABC")
_S: dict = {}


def _init(path: str, arms: tuple = ARMS) -> None:
    cv2.setNumThreads(1)
    _S["enc"] = pickle.load(open(path, "rb"))
    _S["cfg"] = {a: dataclasses.replace(det.DetConfig(), slack=a) for a in arms}


def work(key: str) -> tuple[str, dict]:
    m = cv2.imdecode(np.frombuffer(_S["enc"][key], np.uint8), cv2.IMREAD_UNCHANGED)
    return key, {a: [[int(p.color), [int(v) for v in p.bbox]] for p in det.detect(m, cfg)] for a, cfg in _S["cfg"].items()}


def stem_of(key: str) -> str | None:
    """The train frame an input was made from (None for a simulated scene)."""
    return None if key.startswith("scene/") else key.rsplit("/", 1)[1]


def barrels_of(boxes) -> list:
    return [dtp.Barrel(color=int(c), bbox=tuple(b), source="harness") for c, b in boxes]


def main() -> int:
    global ARMS, OUT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs")
    ap.add_argument("before")
    ap.add_argument("truth", nargs="?")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--sheet", default=None)
    ap.add_argument("--round", default="round1", help="the subfolder of results/2026-11-26_slack/ to write to")
    ap.add_argument("--arms", default=",".join(ARMS), help="the values of DetConfig.slack to run, separated by commas")
    args = ap.parse_args()
    ARMS, OUT = tuple(args.arms.split(",")), OUT / args.round
    OUT.mkdir(parents=True, exist_ok=True)
    before = {k: [[b[0], b[1]] for b in v["boxes"]] for k, v in json.load(open(args.before)).items()}
    scene_truth = json.load(open(args.truth)) if args.truth else {}
    keys = sorted(before)
    stems = sorted({s for s in map(stem_of, keys) if s})
    jg.require_train(stems)                                                    # every real input is a train frame
    labeled = [s for s in stems if io.boxes_path(s).exists()]
    gts, clean = ct.load_gts(labeled)

    def truth_of(key: str):
        s = stem_of(key)
        if s is None:
            t = scene_truth.get(key)
            return None if t is None else ([dtp.Barrel(color=int(c), bbox=tuple(b), source="gt") for c, b in t["truths"]], True)
        return (gts[s], clean[s]) if s in gts else None

    after: dict = {}
    with Pool(args.jobs, initializer=_init, initargs=(args.inputs, ARMS)) as pool:
        for i, (k, r) in enumerate(pool.imap_unordered(work, keys, chunksize=20)):
            after[k] = r
            if (i + 1) % 1000 == 0:
                print(f"  {i + 1}/{len(keys)}", flush=True)

    res: dict = {a: defaultdict(lambda: defaultdict(int)) for a in ARMS}
    bad_scenes: dict = defaultdict(list)
    for k in keys:
        g = k.split("/")[0]
        t = truth_of(k)
        b0 = before[k]
        c0 = ct.classify_frame(k, barrels_of(b0), t[0], t[1]) if t else None
        for a in ARMS:
            r, b1 = res[a][g], after[k][a]
            s0, s1 = {(c, tuple(b)) for c, b in b0}, {(c, tuple(b)) for c, b in b1}
            r["inputs"] += 1
            r["changed"] += s0 != s1
            r["added"] += len(s1 - s0); r["removed"] += len(s0 - s1)
            if t:
                c1 = ct.classify_frame(k, barrels_of(b1), t[0], t[1])
                r["scored"] += 1; r["barrels"] += len(t[0])
                r["found0"] += c0.n_gt(ct.FOUND); r["found1"] += c1.n_gt(ct.FOUND)
                r["gained"] += sum(x != ct.FOUND and y == ct.FOUND for x, y in zip(c0.gt, c1.gt))
                r["lost"] += sum(x == ct.FOUND and y != ct.FOUND for x, y in zip(c0.gt, c1.gt))
                r["off0"] += c0.n_gt(ct.OFF); r["off1"] += c1.n_gt(ct.OFF)
                r["extra0"] += c0.extra; r["extra1"] += c1.extra
                if not t[0]:
                    r["empty0"] += len(b0); r["empty1"] += len(b1)
                new_extra = [(c, b) for (c, b), st in zip(b1, c1.boxes) if st in ct.EXTRA_STATES and (c, tuple(b)) not in s0]
                r["new_extra"] += len(new_extra)
                if new_extra:
                    bad_scenes[a].append({"key": k, "new": new_extra, "after": b1, "before": b0})
    groups = sorted({k.split("/")[0] for k in keys})
    out = {a: {g: dict(res[a][g]) for g in groups} for a in ARMS}
    (OUT / "harness.json").write_text(json.dumps({"arms": out, "new_boxes_not_on_a_barrel": {a: v for a, v in bad_scenes.items()}}, indent=1) + "\n")

    L = ["# The collapse harness with the flag on (yardstick d)", "",
         f"`harness_flag.py`: {len(keys)} masks, the same ones the collapse was proven on. \"Today\" = the boxes of `before.json` (the flag off reproduces them: "
         "`diff.py` prints IDENTICAL BOXES ON EVERY INPUT). Scored where the truth is known: masks made from a train frame against its hand boxes "
         f"({len(labeled)} of {len(stems)} frames have box labels), simulated scenes against the scene's own boxes"
         + ("" if scene_truth else " (NOT AVAILABLE in this run: scenes are counted only)") + ". Strict rule; a box on its barrel with the bottom off counts once.", "",
         "Cell: inputs whose boxes change / all; boxes +added −removed; found today → arm (+gained −lost); boxes not on their barrel today → arm (new ones); "
         "boxes on empty inputs today → arm.", ""]
    L += ["| arm | " + " | ".join(groups) + " |", "|---|" + "---|" * len(groups)]
    for a in ARMS:
        cells = []
        for g in groups:
            r = res[a][g]
            c = f"{r['changed']} / {r['inputs']}; +{r['added']} −{r['removed']}"
            if r["scored"]:
                c += f"; found {r['found0']} → {r['found1']} (+{r['gained']} −{r['lost']}); not on barrel {r['extra0']} → {r['extra1']} (new {r['new_extra']}); empty {r['empty0']} → {r['empty1']}"
            cells.append(c)
        L.append(f"| {a} | " + " | ".join(cells) + " |")
    L.append("")
    for a in ARMS:
        kinds = defaultdict(int)
        for x in bad_scenes[a]:
            kinds[x["key"].split("/")[0]] += len(x["new"])
        L.append(f"- {a}: new boxes that are not on their barrel, by group: " + (", ".join(f"{g} {n}" for g, n in sorted(kinds.items())) or "none") + ".")
    L.append("")

    if args.sheet:
        enc = pickle.load(open(args.inputs, "rb"))
        sheet_dir = OUT / "harness_sheets"
        sheet_dir.mkdir(exist_ok=True)
        for old in list(sheet_dir.glob("*.png")) + list(sheet_dir.glob("*.jpg")):
            old.unlink()
        tiles = []
        for n, x in enumerate(bad_scenes[args.sheet], 1):
            m = cv2.imdecode(np.frombuffer(enc[x["key"]], np.uint8), cv2.IMREAD_UNCHANGED)
            paint = np.zeros((*m.shape, 3), np.uint8)
            paint[m == io.ORANGE] = (0, 140, 255); paint[m == io.BLUE] = (255, 120, 0)
            t = truth_of(x["key"])
            xs = [v for c, b in x["new"] for v in (b[0], b[2])] + [v for g in t[0] for v in (g.bbox[0], g.bbox[2])]
            ys = [v for c, b in x["new"] for v in (b[1], b[3])] + [v for g in t[0] for v in (g.bbox[1], g.bbox[3])]
            x0, y0, x1, y1 = max(0, min(xs) - 30), max(0, min(ys) - 30), min(640, max(xs) + 30), min(480, max(ys) + 30)
            side = max(x1 - x0, y1 - y0)
            canvas = np.zeros((side, side, 3), np.uint8)
            canvas[:y1 - y0, :x1 - x0] = paint[y0:y1, x0:x1]
            big = cv2.resize(canvas, (260, 260), interpolation=cv2.INTER_NEAREST)
            f = 260 / side
            for g in t[0]:
                cv2.rectangle(big, (int((g.bbox[0] - x0) * f), int((g.bbox[1] - y0) * f)), (int((g.bbox[2] - x0) * f) - 1, int((g.bbox[3] - y0) * f) - 1), (255, 255, 255), 1)
            for c, b in x["before"]:
                cv2.rectangle(big, (int((b[0] - x0) * f), int((b[1] - y0) * f)), (int((b[2] - x0) * f) - 1, int((b[3] - y0) * f) - 1), (160, 160, 160), 1)
            for c, b in x["new"]:
                cv2.rectangle(big, (int((b[0] - x0) * f), int((b[1] - y0) * f)), (int((b[2] - x0) * f) - 1, int((b[3] - y0) * f) - 1), (255, 0, 255), 2)
            tile = np.full((260 + 30, 260, 3), 30, np.uint8)
            tile[:260] = big
            parts = x["key"].split("/")
            cv2.putText(tile, f"#{n} {parts[0]} {parts[-3][:22]}", (2, 272), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(tile, f"{parts[-2]} {parts[-1]} {parts[1][:14]}", (2, 286), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (255, 255, 255), 1, cv2.LINE_AA)
            tiles.append(tile)
        for i in range(0, len(tiles), 24):
            chunk = tiles[i:i + 24]
            rows = (len(chunk) + 5) // 6
            sheet = np.zeros((rows * 296, 6 * 266, 3), np.uint8)
            for j, im in enumerate(chunk):
                r_, c_ = divmod(j, 6)
                sheet[r_ * 296:r_ * 296 + 290, c_ * 266:c_ * 266 + 260] = im
            cv2.imwrite(str(sheet_dir / f"{args.sheet}_{i // 24 + 1:02d}.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])
        L += [f"Contact sheets of every input where `{args.sheet}` adds a box that is not on its barrel: `harness_sheets/` ({len(tiles)} tiles; white = the true boxes, "
              "gray = today's boxes, magenta = the new box).", ""]
    (OUT / "harness.md").write_text("\n".join(L))
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
