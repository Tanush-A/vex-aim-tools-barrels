#!/usr/bin/env python3
"""Yardstick (b) of the side-cut experiment (PREREG.md): real frames.

1. The real occlusion set (the 18 train ``occlx`` frames), barrel by barrel: today, the candidate, the comparison arm.
2. Every real train frame (all of ``splits.json``'s "train" that have an image): every box an arm adds, moves or
   removes, with its state against the labels (``counting.classify_frame``), and one contact sheet per changed frame
   in ``sheets/``: the photo with the labels (green) and today's boxes (white) | the same with ``own_side``'s boxes
   (magenta) | with ``own_side+centred``'s (cyan) | the mask.

    python barrels/experiments/2026-11-26_sidecut/real.py

Train frames only (``judge.load_frame`` refuses anything else). The photo is read, never written.
Writes results/2026-11-26_sidecut/ real.md, real.csv, real_changes.md, real_changes.csv, sheets/*.png.
"""
from __future__ import annotations

import csv

import cv2
import numpy as np

import lib
from lib import dtp, io, jg, pl, splits
from barrels import counting as ct

EXTRA = (ct.NOTHING, ct.SECOND, ct.WRONG)


def run(stem: str) -> dict:
    """Everything about one train frame: its photo, mask, labels, and per mode the boxes, their rules and states."""
    frame = jg.load_frame(stem)
    mask = pl.segment(frame, lib.model())[0]
    has_label = io.boxes_path(stem).exists()
    label = io.load_boxes(stem) if has_label else {"barrels": [], "clean": True}
    gts = dtp.barrels_from_boxes(label) if has_label else []
    out = {"stem": stem, "bgr": frame.bgr, "mask": mask, "gts": gts, "labelled": has_label, "modes": {}}
    for mode in lib.MODES:
        preds, log = lib.detect(mask, mode)
        fc = ct.classify_frame(stem, preds, gts, label.get("clean", True))
        out["modes"][mode] = {"preds": preds, "rules": [lib.rule_of(log, p.bbox) or p.source for p in preds], "fc": fc, "log": log}
    return out


def placed(p, g) -> bool:
    return abs((p.bbox[0] + p.bbox[2]) - (g.bbox[0] + g.bbox[2])) / 2 <= lib.CENTRE_TOL * g.width


def box_for(gi: int, r: dict, mode: str):
    """The box that is on true barrel ``gi`` (the same-color box with the largest overlap that is on it), or None."""
    g, m = r["gts"][gi], r["modes"][mode]
    on = [(lib.ed.box_iou(p.bbox, g.bbox), i) for i, p in enumerate(m["preds"]) if p.color == g.color and ct.is_on(p, g) and m["fc"].boxes[i] in (ct.FOUND, ct.OFF)]
    return max(on)[1] if on else None


def tile(r: dict, pad: int = 30, scale: int = 3) -> np.ndarray:
    boxes = [p.bbox for m in r["modes"].values() for p in m["preds"]] + [g.bbox for g in r["gts"]]
    base = {(p.color, p.bbox) for p in r["modes"]["centred"]["preds"]}
    changed = [p.bbox for mode in lib.MODES[1:] for p in r["modes"][mode]["preds"] if (p.color, p.bbox) not in base]
    changed += [b for c, b in base if any((c, b) not in {(p.color, p.bbox) for p in r["modes"][mode]["preds"]} for mode in lib.MODES[1:])]
    focus = changed or boxes
    x0, y0 = max(0, min(b[0] for b in focus) - pad), max(0, min(b[1] for b in focus) - pad)
    x1, y1 = min(640, max(b[2] for b in focus) + pad), min(480, max(b[3] for b in focus) + pad)
    seg = np.full((480, 640, 3), 45, np.uint8)
    seg[r["mask"] == io.ORANGE] = (0, 140, 255); seg[r["mask"] == io.BLUE] = (255, 120, 0)
    panels = []
    for name, color in (("centred", (255, 255, 255)), ("own_side", (255, 0, 255)), ("own_side+centred", (255, 255, 0)), ("mask", None)):
        img = (seg if name == "mask" else r["bgr"]).copy()
        crop = cv2.resize(img[y0:y1, x0:x1], None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)

        def box(b, c, t=1):
            cv2.rectangle(crop, ((b[0] - x0) * scale, (b[1] - y0) * scale), ((b[2] - x0) * scale - 1, (b[3] - y0) * scale - 1), c, t)
        for g in r["gts"]:
            box(g.bbox, (0, 255, 0))
        if name != "mask":
            for p in r["modes"][name]["preds"]:
                box(p.bbox, color, 2)
        else:
            for p in r["modes"]["own_side"]["preds"]:
                box(p.bbox, (255, 0, 255))
        head = np.zeros((16, crop.shape[1], 3), np.uint8)
        cv2.putText(head, name if name != "centred" else "today (white) labels (green)", (2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)
        panels.append(np.vstack([head, crop]))
        panels.append(np.zeros((panels[-1].shape[0], 4, 3), np.uint8))
    return np.hstack(panels[:-1])


def main() -> int:
    out = lib.OUT
    (out / "sheets").mkdir(parents=True, exist_ok=True)
    for old in (out / "sheets").glob("*.png"):
        old.unlink()
    sp = splits.load_splits()
    train = sorted(sp["train"])
    jg.require_train(train, sp)
    stems = [s for s in train if io.find_image(s) is not None]
    print(len(train), "train frames,", len(stems), "with an image,", sum(io.boxes_path(s).exists() for s in stems), "with a box label")

    occl_rows, change_rows, totals = [], [], {m: {k: 0 for k in ("found", "off", "missed") + EXTRA} for m in lib.MODES}
    n_changed = {m: 0 for m in lib.MODES[1:]}
    sheet = 0
    for stem in stems:
        r = run(stem)
        for mode in lib.MODES:
            fc = r["modes"][mode]["fc"]
            for s in fc.gt:
                totals[mode][s] += 1
            for s in fc.boxes:
                if s in EXTRA:
                    totals[mode][s] += 1
        if "occlx" in stem:
            for gi, g in enumerate(r["gts"]):
                row = {"frame": stem.replace("4A8B_", ""), "barrel": dtp.COLOR_NAMES[g.color], "truth": list(g.bbox), "flags": "+".join(sorted(g.flags))}
                for mode in lib.MODES:
                    m = r["modes"][mode]
                    pi = box_for(gi, r, mode)
                    row[f"{mode}:state"] = m["fc"].gt[gi]
                    row[f"{mode}:box"] = "" if pi is None else list(m["preds"][pi].bbox)
                    row[f"{mode}:rule"] = "" if pi is None else m["rules"][pi]
                    row[f"{mode}:placed"] = "" if pi is None else int(placed(m["preds"][pi], g))
                occl_rows.append(row)
            for mode in lib.MODES:
                m = r["modes"][mode]
                for pi, p in enumerate(m["preds"]):
                    if m["fc"].boxes[pi] in EXTRA:
                        occl_rows.append({"frame": stem.replace("4A8B_", ""), "barrel": f"BOX NOT ON ITS BARREL ({m['fc'].boxes[pi]})", "truth": "", "flags": "",
                                          **{f"{mm}:{k}": "" for mm in lib.MODES for k in ("state", "box", "rule", "placed")},
                                          f"{mode}:box": list(p.bbox), f"{mode}:rule": m["rules"][pi], f"{mode}:state": m["fc"].boxes[pi]})
        base = r["modes"]["centred"]
        bset = {(p.color, p.bbox): i for i, p in enumerate(base["preds"])}
        differs = False
        for mode in lib.MODES[1:]:
            m = r["modes"][mode]
            mset = {(p.color, p.bbox): i for i, p in enumerate(m["preds"])}
            if set(bset) == set(mset):
                continue
            differs = True
            n_changed[mode] += 1
            for key, i in mset.items():
                if key not in bset:
                    change_rows.append({"frame": stem, "mode": mode, "what": "new box", "color": dtp.COLOR_NAMES[key[0]], "box": list(key[1]), "rule": m["rules"][i],
                                        "state": m["fc"].boxes[i], "labelled": int(r["labelled"]), "truth": [list(g.bbox) for g in r["gts"] if ct.is_on(m["preds"][i], g)]})
            for key, i in bset.items():
                if key not in mset:
                    change_rows.append({"frame": stem, "mode": mode, "what": "box gone", "color": dtp.COLOR_NAMES[key[0]], "box": list(key[1]), "rule": base["rules"][i],
                                        "state": base["fc"].boxes[i], "labelled": int(r["labelled"]), "truth": [list(g.bbox) for g in r["gts"] if ct.is_on(base["preds"][i], g)]})
        if differs:
            cv2.imwrite(str(out / "sheets" / f"{sheet:02d}_{stem}.png"), tile(r))
            sheet += 1

    if occl_rows:
        with (out / "real.csv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(occl_rows[0].keys())); w.writeheader(); w.writerows(occl_rows)
    fields = ["frame", "mode", "what", "color", "box", "rule", "state", "labelled", "truth"]
    with (out / "real_changes.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(change_rows)

    def txt(row, mode):
        s = row[f"{mode}:state"]
        if not row["truth"]:
            return f"{s}: {row[f'{mode}:box']} by {row[f'{mode}:rule']}" if s else ""
        word = {"found": "found", "off": "box off", "missed": "missed"}[s]
        if row[f"{mode}:box"] != "":
            word += f" {row[f'{mode}:box']} ({row[f'{mode}:rule']}{'' if row[f'{mode}:placed'] else ', centre off'})"
        return word
    L = ["# The real occlusion set, barrel by barrel", "",
         "The 18 train `occlx` frames. found = the strict rule. box off = a box of the right color is on the barrel but fails the strict rule. "
         "\"centre off\" = the box's centre is more than 10 % of the width from the true centre. In brackets: the rule that drew the box.", "",
         "| frame | barrel | flags | today (`centred`) | `own_side` | `own_side+centred` |", "|---|---|---|---|---|---|"]
    for row in occl_rows:
        L.append(f"| {row['frame'].replace('window_', '')} | {row['barrel']} {row['truth']} | {row['flags']} | " + " | ".join(txt(row, m) for m in lib.MODES) + " |")
    hid = [r for r in occl_rows if r["truth"] and r["flags"]]
    allb = [r for r in occl_rows if r["truth"]]
    L += ["", "| | today | `own_side` | `own_side+centred` |", "|---|---|---|---|",
          f"| flagged barrels found, of {len(hid)} | " + " | ".join(str(sum(r[f'{m}:state'] == 'found' for r in hid)) for m in lib.MODES) + " |",
          f"| all barrels found, of {len(allb)} | " + " | ".join(str(sum(r[f'{m}:state'] == 'found' for r in allb)) for m in lib.MODES) + " |",
          "| boxes not on their barrel | " + " | ".join(str(sum(1 for r in occl_rows if not r["truth"] and r[f"{m}:state"])) for m in lib.MODES) + " |"]
    (out / "real.md").write_text("\n".join(L) + "\n")

    C = ["# Every box that changes on a real train frame", "",
         f"{len(stems)} real train frames (every train frame that has an image; {sum(io.boxes_path(s).exists() for s in stems)} have a box label). Frames whose boxes "
         f"differ from today: `own_side` {n_changed['own_side']}, `own_side+centred` {n_changed['own_side+centred']}. One contact sheet per changed frame in `sheets/`.", "",
         "State of a box against the labels: found (strict) / off (on its barrel, fails strict) / second / wrong_color / nothing.", "",
         "| frame | arm | what | box | rule | state | the barrel it is on |", "|---|---|---|---|---|---|---|"]
    for c in change_rows:
        C.append(f"| {c['frame'].replace('4A8B_', '')} | `{c['mode']}` | {c['what']} | {c['color']} {c['box']} | {c['rule']} | {c['state'] if c['labelled'] else 'no label'} | {c['truth'] or ''} |")
    C += ["", "Totals over all real train frames (per frame, not per placement):", "", "| | today | `own_side` | `own_side+centred` |", "|---|---|---|---|"]
    for k, name in (("found", "barrels found (strict)"), ("off", "barrels with the box off"), ("missed", "barrels missed"), (ct.NOTHING, "boxes on nothing"),
                    (ct.SECOND, "second boxes"), (ct.WRONG, "boxes of the wrong color")):
        C.append(f"| {name} | " + " | ".join(str(totals[m][k]) for m in lib.MODES) + " |")
    (out / "real_changes.md").write_text("\n".join(C) + "\n")
    print("\n".join(L)); print(); print("\n".join(C))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
