#!/usr/bin/env python3
"""The proof harness with the paint checks on (plan: PREREG.md, yardstick H).

    cd barrels && env PYTHONPATH=src python experiments/2026-11-27_checks/harness.py <inputs.pkl> <before.json> <scene_truth.json> [--jobs 8] [--ref]

``inputs.pkl`` / ``before.json``: the 5435 masks of experiments/2026-11-26_collapse and today's boxes on them (the
switches off must reproduce them: ``diff.py`` says IDENTICAL BOXES ON EVERY INPUT). ``scene_truth.json``: the true
boxes of the simulated scenes (experiments/2026-11-26_slack/scene_truth.py, on branch wip/exp-slack).

For every arm (``arms.ARMS``): ``detector.detect`` with those switches; every box it removes, with the reason, the
rule that drew it, the three readings, and what the box was before (on its barrel and found, on its barrel with the
box off, a wrong color, a second box, on nothing). Scored where the truth is known: masks made from a train frame
against its hand boxes, the scenes against their own boxes.

``--ref``: also checks that ``detector.detect`` with both switches on draws exactly the boxes of the experiment's own
post-filter (``ref/checks.py`` + ``ref/stages.py``, copied unchanged from wip/exp-bluer-geom) at the same numbers.

Outputs: results/2026-11-27_checks/harness.md, harness.json, harness_removed.csv."""
from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import pickle
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
sys.path.insert(0, str(BARRELS / "src"))
sys.path.insert(0, str(HERE))
from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
import arms as am  # noqa: E402

assert str(Path(det.__file__).resolve()).startswith(str(BARRELS)), det.__file__
OUT = BARRELS / "results" / "2026-11-27_checks"
_S: dict = {}


def _init(path: str, ref: bool) -> None:
    cv2.setNumThreads(1)
    _S["enc"] = pickle.load(open(path, "rb"))
    _S["ref"] = ref
    if ref:
        sys.path.insert(0, str(HERE / "ref"))
        import checks as rck  # noqa: F401
        import stages as rst  # noqa: F401
        _S["rck"], _S["rst"] = rck, rst


def work(key: str) -> tuple[str, dict]:
    m = cv2.imdecode(np.frombuffer(_S["enc"][key], np.uint8), cv2.IMREAD_UNCHANGED)
    out: dict = {"arms": {}}
    for a, over in am.ARMS.items():
        log: list = []
        boxes = det.detect(m, dataclasses.replace(det.DetConfig(), **over), log=log)
        removed = [{k: (v if not isinstance(v, float) else round(v, 4)) for k, v in e.items() if k in ("why", "bbox", "body", "rule", "solid", "stripe_h", "body_share")}
                   for e in log if e["stage"] == "verify" and e["why"] in ("speckle", "label")]
        out["arms"][a] = {"boxes": [[int(p.color), [int(v) for v in p.bbox]] for p in boxes], "removed": removed}
    if _S["ref"]:
        rck, rst = _S["rck"], _S["rst"]
        mism = {}
        for a in ("SL", "SLm"):
            o = am.ARMS[a]
            ck = rck.Checks(o["solid_min"], o["label_stripe"], o["label_body"])
            ref = [[int(b.color), [int(v) for v in b.bbox]] for b in sorted(rck.apply(rst.found(m), m, ck), key=lambda b: b.bbox[0])]
            mine = out["arms"][a]["boxes"]
            if sorted(map(json.dumps, ref)) != sorted(map(json.dumps, mine)):
                mism[a] = {"ref": ref, "mine": mine}
        out["ref_mismatch"] = mism
    return key, out


def stem_of(key: str) -> str | None:
    return None if key.startswith("scene/") else key.rsplit("/", 1)[1]


def barrels_of(boxes) -> list:
    return [dtp.Barrel(color=int(c), bbox=tuple(b), source="harness") for c, b in boxes]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs")
    ap.add_argument("before")
    ap.add_argument("truth")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--ref", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    before = {k: [[b[0], b[1]] for b in v["boxes"]] for k, v in json.load(open(args.before)).items()}
    scene_truth = json.load(open(args.truth))
    keys = sorted(before)
    stems = sorted({s for s in map(stem_of, keys) if s})
    jg.require_train(stems)
    labeled = [s for s in stems if io.boxes_path(s).exists()]
    gts, clean = ct.load_gts(labeled)

    def truth_of(key: str):
        s = stem_of(key)
        if s is None:
            t = scene_truth.get(key)
            return None if t is None else ([dtp.Barrel(color=int(c), bbox=tuple(b), source="gt") for c, b in t["truths"]], True)
        return (gts[s], clean[s]) if s in gts else None

    after: dict = {}
    with Pool(args.jobs, initializer=_init, initargs=(args.inputs, args.ref)) as pool:
        for i, (k, r) in enumerate(pool.imap_unordered(work, keys, chunksize=20)):
            after[k] = r
            if (i + 1) % 1000 == 0:
                print(f"  {i + 1}/{len(keys)}", flush=True)

    res = {a: defaultdict(lambda: defaultdict(int)) for a in am.ARMS}
    rows = []
    lost_list = defaultdict(list)
    for k in keys:
        g = k.split("/")[0]
        t = truth_of(k)
        b0 = before[k]
        c0 = ct.classify_frame(k, barrels_of(b0), t[0], t[1]) if t else None
        state0 = {(c, tuple(b)): st for (c, b), st in zip(b0, c0.boxes)} if c0 else {}
        for a in am.ARMS:
            r, b1 = res[a][g], after[k]["arms"][a]["boxes"]
            s0, s1 = {(c, tuple(b)) for c, b in b0}, {(c, tuple(b)) for c, b in b1}
            assert s1 <= s0, (k, a, "a check may only take boxes away")
            r["inputs"] += 1
            r["changed"] += s0 != s1
            r["removed"] += len(s0 - s1)
            for e in after[k]["arms"][a]["removed"]:
                st = state0.get((int(e["body"]), tuple(e["bbox"])), "unscored")
                r[f"removed_{st}"] += 1
                row = {"arm": a, "group": g, "key": k, "why": e["why"], "rule": e["rule"], "color": "orange" if e["body"] == 1 else "blue",
                       "bbox": " ".join(map(str, e["bbox"])), "before": st, "solid": e.get("solid"), "stripe_h": e.get("stripe_h"),
                       "body_share": e.get("body_share")}
                if k in scene_truth:
                    row.update(kind=scene_truth[k]["kind"], amount=scene_truth[k]["amount"], hidden=scene_truth[k]["hidden"])
                rows.append(row)
            if t:
                c1 = ct.classify_frame(k, barrels_of(b1), t[0], t[1])
                r["scored"] += 1
                r["barrels"] += len(t[0])
                r["found0"] += c0.n_gt(ct.FOUND)
                r["found1"] += c1.n_gt(ct.FOUND)
                r["off0"] += c0.n_gt(ct.OFF)
                r["off1"] += c1.n_gt(ct.OFF)
                lostk = [i for i, (x, y) in enumerate(zip(c0.gt, c1.gt)) if x != ct.MISSED and y == ct.MISSED]
                downk = [i for i, (x, y) in enumerate(zip(c0.gt, c1.gt)) if x == ct.FOUND and y == ct.OFF]
                r["lost"] += len(lostk)
                r["found_to_off"] += len(downk)
                r["extra0"] += c0.extra
                r["extra1"] += c1.extra
                for i in lostk + downk:
                    lost_list[a].append({"key": k, "gt": [int(t[0][i].color), list(t[0][i].bbox)], "was": c0.gt[i], "now": c1.gt[i]})
    mism = {k: v["ref_mismatch"] for k, v in after.items() if v.get("ref_mismatch")}
    groups = sorted({k.split("/")[0] for k in keys})
    summary = {a: {g: dict(res[a][g]) for g in groups} for a in am.ARMS}
    (OUT / "harness.json").write_text(json.dumps({"arms": summary, "lost": lost_list, "ref_checked": args.ref, "ref_mismatch": mism}, indent=1) + "\n")
    with open(OUT / "harness_removed.csv", "w", newline="") as fh:
        cols = ["arm", "group", "key", "why", "rule", "color", "bbox", "before", "solid", "stripe_h", "body_share", "kind", "amount", "hidden"]
        w = csv.DictWriter(fh, cols)
        w.writeheader()
        w.writerows(rows)

    L = ["# The proof harness with the paint checks on (yardstick H)", "",
         f"`harness.py`: {len(keys)} masks. Before = today's boxes (`before.json`). Scored where the truth is known: masks made from a train frame against "
         f"its hand boxes ({len(labeled)} of {len(stems)} frames have box labels), the {len(scene_truth)} simulated scenes against their own true boxes. "
         "A check only takes boxes away. Removed boxes by what they were before: F = on its barrel and found, O = on its barrel with the box off, "
         "W = wrong color on a barrel, S = a second box on a barrel, N = on nothing; unscored = a mask with no truth.", ""]
    if args.ref:
        L += [f"Same as the experiment's own post-filter (ref/checks.py + ref/stages.py) at the same numbers, arms SL and SLm: "
              + ("**yes, on every input**." if not mism else f"**NO: {len(mism)} inputs differ** (harness.json, ref_mismatch)."), ""]
    for a in am.ARMS:
        L += [f"## {a}: {am.DESCRIBE[a]}", "",
              "| group | inputs changed | boxes removed | removed by what they were: F / O / W / S / N / unscored | barrels found (strict) before → after | "
              "found → box off | lost (no box left on it) | boxes not on their barrel before → after |", "|---|---|---|---|---|---|---|---|"]
        tot = defaultdict(int)
        for g in groups:
            r = res[a][g]
            for kk, v in r.items():
                tot[kk] += v
            L.append(f"| {g} | {r['changed']} / {r['inputs']} | {r['removed']} | " + " / ".join(str(r[f'removed_{s}']) for s in (ct.FOUND, ct.OFF, ct.WRONG, ct.SECOND, ct.NOTHING, 'unscored'))
                     + f" | {r['found0']} → {r['found1']} of {r['barrels']} | {r['found_to_off']} | {r['lost']} | {r['extra0']} → {r['extra1']} |")
        L.append(f"| **all** | {tot['changed']} / {tot['inputs']} | {tot['removed']} | " + " / ".join(str(tot[f'removed_{s}']) for s in (ct.FOUND, ct.OFF, ct.WRONG, ct.SECOND, ct.NOTHING, 'unscored'))
                 + f" | {tot['found0']} → {tot['found1']} of {tot['barrels']} | {tot['found_to_off']} | {tot['lost']} | {tot['extra0']} → {tot['extra1']} |")
        L.append("")
        mine = [x for x in rows if x["arm"] == a]
        if mine:
            L += ["Every box removed (all groups):", "", "| group | input | why | rule | color | box | before | solid | stripe h | body share | scene |", "|---|---|---|---|---|---|---|---|---|---|---|"]
            for x in mine:
                sc = f"{x.get('kind')} {x.get('amount')} (hidden {x.get('hidden')})" if "kind" in x else ""
                L.append(f"| {x['group']} | `{x['key'].split('/', 1)[1]}` | {x['why']} | {x['rule']} | {x['color']} | {x['bbox']} | {x['before']} | {x['solid']} | {x['stripe_h']} | {x['body_share']} | {sc} |")
            L.append("")
    (OUT / "harness.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:6]))
    for a in am.ARMS:
        tot = defaultdict(int)
        for g in groups:
            for kk, v in res[a][g].items():
                tot[kk] += v
        print(a, dict(removed=tot["removed"], F=tot["removed_found"] if "removed_found" in tot else None, lost=tot["lost"], found_to_off=tot["found_to_off"],
                      extra=(tot["extra0"], tot["extra1"])), {kk: v for kk, v in tot.items() if kk.startswith("removed_")})
    return 0


if __name__ == "__main__":
    sys.exit(main())
