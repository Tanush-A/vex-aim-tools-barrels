#!/usr/bin/env python3
"""Part B of the white-balance experiment (PREREG.md): what each correction does to the paint and to the rest, before
any judging. EXPERIMENT ONLY (the standing rule forbids correction); nothing is written to data/.

    python barrels/experiments/2026-11-27_whitebalance/measure.py

For every train frame (ordinary, extreme, excluded) and every estimator at alpha 1 and 0.5: the share of the paint
pixels (body and stripe bands of free-standing upright barrels, from the hand boxes) that the fixed model paints the
right class, before and after; the median hue and S of the paint after; the share of non-barrel pixels (rows >= 50,
outside every hand box grown 4 px, V >= 40) painted; for the home white table also rows 0-49 as if there were no
horizon gate (the wall); the median gains. Writes results/2026-11-27_whitebalance/measure.md, measure.json, measure.csv.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wb  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402

OUT = wb.BARRELS / "results" / "2026-11-27_whitebalance"
SKIP_FLAGS = {"occluded", "truncated", "held", "bottom_estimated"}
SKIP_SCENES = {"top", "topstripe", "held", "hand"}
SETTINGS = [wb.FIXED] + [wb.Setting(e, a) for a in (1.0, 0.5) for e in wb.ESTIMATORS]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


color_common = _load("color_common_2026_11_25", wb.BARRELS / "experiments" / "2026-11-25_color" / "common.py")


def paint_masks(stem: str, shape) -> dict[str, np.ndarray]:
    """orange paint (orange bodies + orange stripes of blue barrels), blue paint, and every hand box grown 4 px."""
    lab = io.load_boxes(stem, check_image=False)
    h, w = shape[:2]
    out = {k: np.zeros((h, w), bool) for k in ("orange", "blue", "boxes")}
    scene = io.parse_name(stem)["scene"]
    for b in lab.get("barrels", []):
        x0, y0, x1, y1 = (int(v) for v in b["bbox"])
        out["boxes"][max(0, y0 - 4):y1 + 4, max(0, x0 - 4):x1 + 4] = True
        bw, bh = x1 - x0, y1 - y0
        if set(b.get("flags", [])) & SKIP_FLAGS or scene in SKIP_SCENES or bh < 24 or not (0.75 <= bw / bh <= 1.25):
            continue
        reg = color_common.expected_regions(b, (h, w))
        other = "blue" if b["color"] == "orange" else "orange"
        out[b["color"]] |= reg["body"]
        out[other] |= reg["stripe"]
    return out


def main() -> int:
    frames = jg.train_frames()
    klass = {s: k for k, ss in frames.items() for s in ss}
    stems = [s for k in (cnd.ORDINARY, cnd.EXTREME, cnd.EXCLUDED) for s in frames[k]]
    # acc[setting key][condition] -> counts; hs[setting][cond][paint] -> list of (hue, S) arrays
    acc = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    hs = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    gl = defaultdict(lambda: defaultdict(list))
    rng = np.random.default_rng(0)
    nog = wb.nogate_model()
    for i, s in enumerate(stems):
        frame = jg.load_frame(s)
        cond = ct.condition_of(s)
        pm = paint_masks(s, frame.shape)
        bg = ~pm["boxes"] & (frame.val >= wb.V_MIN)
        bg[:wb.GATE_ROW] = False
        wall = np.zeros(frame.shape, bool)
        wall[:wb.GATE_ROW] = True
        wall &= frame.val >= wb.V_MIN
        for st in SETTINGS:
            info: dict = {}
            m = wb.segment(frame, st, info)
            f2 = info.get("corrected", frame)
            a = acc[st.key][cond]
            a["frames"] += 1
            for name, cls in (("orange", ORANGE), ("blue", BLUE)):
                p = pm[name]
                a[f"{name}_px"] += p.sum()
                a[f"{name}_in"] += (p & (m == cls)).sum()
                if p.any():
                    hue = f2.hs(pl.HUE_SHIFT[cls])[..., 0] - pl.HUE_SHIFT[cls]
                    sat = f2.hs(0)[..., 1]
                    idx = np.flatnonzero(p)
                    if len(idx) > 400:
                        idx = rng.choice(idx, 400, replace=False)
                    hs[st.key][cond][name].append(np.stack([hue.ravel()[idx], sat.ravel()[idx], f2.val.ravel()[idx]], 1))
            a["bg_px"] += bg.sum()
            a["bg_orange"] += (bg & (m == ORANGE)).sum()
            a["bg_blue"] += (bg & (m == BLUE)).sum()
            if cond == "window_light":
                mw = pl.segment(f2, nog)[0]
                a["wall_px"] += (wall & (f2.val >= wb.V_MIN)).sum()
                a["wall_in"] += (wall & (mw > 0)).sum()
            if st.estimator:
                gl[st.key][cond].append(info["gains"])
        if (i + 1) % 50 == 0:
            print(f"{i + 1}/{len(stems)}", flush=True)
    conds = list(dict.fromkeys(ct.condition_of(s) for s in stems))
    ckl = {c: cnd.info(c).klass for c in conds}
    res = {}
    for st in SETTINGS:
        rows = {}
        for c in conds:
            a = acc[st.key][c]
            r = {"class": ckl[c], "frames": int(a["frames"])}
            for name in ("orange", "blue"):
                r[f"{name}_in"] = float(a[f"{name}_in"] / a[f"{name}_px"]) if a[f"{name}_px"] else None
                arr = hs[st.key][c][name]
                if arr:
                    z = np.concatenate(arr)
                    r[f"{name}_hue"], r[f"{name}_s"], r[f"{name}_v"] = (float(np.median(z[:, k])) for k in range(3))
            r["flood_orange"] = float(a["bg_orange"] / a["bg_px"]) if a["bg_px"] else None
            r["flood_blue"] = float(a["bg_blue"] / a["bg_px"]) if a["bg_px"] else None
            if a["wall_px"]:
                r["wall_in"] = float(a["wall_in"] / a["wall_px"])
            if gl[st.key][c]:
                r["gains"] = [float(v) for v in np.median(np.array(gl[st.key][c]), 0)]
            rows[c] = r
        res[st.key] = rows
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "measure.json").write_text(json.dumps(res, indent=1) + "\n")
    with open(OUT / "measure.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["setting", "condition", "class", "frames", "orange_in", "blue_in", "orange_hue", "orange_s", "blue_hue", "blue_s", "flood_orange", "flood_blue", "wall_in", "gR", "gG", "gB"])
        for k, rows in res.items():
            for c, r in rows.items():
                g = r.get("gains", [None] * 3)
                w.writerow([k, c, r["class"], r["frames"], r.get("orange_in"), r.get("blue_in"), r.get("orange_hue"), r.get("orange_s"), r.get("blue_hue"), r.get("blue_s"),
                            r["flood_orange"], r["flood_blue"], r.get("wall_in"), *g])
    write_md(res, conds, ckl)
    return 0


def pct(x) -> str:
    return "–" if x is None else f"{100 * x:.0f}"


def pct1(x) -> str:
    return "–" if x is None else f"{100 * x:.1f}"


def write_md(res: dict, conds: list[str], ckl: dict) -> None:
    base = res[wb.FIXED.key]
    L = ["# Part B: what each correction does to the paint and to the rest (measured before any judging)", "",
         "EXPERIMENT ONLY: the standing rule (2026-10-07) forbids correcting the image. `measure.py`; train frames only.", "",
         "*Paint in* = share of the paint pixels (body and stripe bands of free-standing upright barrels) that the fixed model paints the right class. "
         "*Flood* = share of non-barrel pixels (rows ≥ 50, outside every hand box + 4 px, V ≥ 40) painted orange + blue. Percent. "
         "*Gains* = median (R, G, B) gains over the condition's frames.", ""]
    order = sorted(conds, key=lambda c: ({"ordinary": 0, "extreme": 1, "excluded": 2}[ckl[c]], c))
    for alpha in (1.0, 0.5):
        L += [f"## alpha {alpha:g}", ""]
        for e in wb.ESTIMATORS:
            r = res[wb.Setting(e, alpha).key]
            L += [f"### {e}, alpha {alpha:g}", "",
                  "| condition | class | orange paint in | blue paint in | orange hue / S after (before) | blue hue / S after (before) | flood orange | flood blue | gains R G B |",
                  "|---|---|---|---|---|---|---|---|---|"]
            for c in order:
                a, b = r[c], base[c]
                hsx = lambda d, n: f"{d.get(n + '_hue', float('nan')):.0f} / {d.get(n + '_s', float('nan')):.0f}" if d.get(n + "_hue") is not None else "–"  # noqa: E731
                g = " ".join(f"{v:.2f}" for v in a.get("gains", []))
                L.append(f"| {c} | {a['class']} | {pct(b['orange_in'])} → {pct(a['orange_in'])} | {pct(b['blue_in'])} → {pct(a['blue_in'])} | "
                         f"{hsx(a, 'orange')} ({hsx(b, 'orange')}) | {hsx(a, 'blue')} ({hsx(b, 'blue')}) | {pct1(b['flood_orange'])} → {pct1(a['flood_orange'])} | "
                         f"{pct1(b['flood_blue'])} → {pct1(a['flood_blue'])} | {g} |")
            w = r["window_light"].get("wall_in")
            L += ["", f"Home wall (rows 0–49 of the home white-table frames, as if there were no horizon gate): painted {pct1(base['window_light'].get('wall_in'))} % → {pct1(w)} %.", ""]
    # one summary table: ordinary means
    L += ["## Summary over the ordinary conditions (mean of the condition shares)", "",
          "| setting | orange paint in | blue paint in | flood orange | flood blue | pale wood flood | bathroom flood (4 lamps) | home flood | home wall |", "|---|---|---|---|---|---|---|---|---|"]
    ords = [c for c in order if ckl[c] == "ordinary"]
    bath = [c for c in ords if c.endswith("_bathtile")]
    for st in SETTINGS:
        r = res[st.key]
        mean = lambda k, cs=ords: float(np.mean([r[c][k] for c in cs if r[c].get(k) is not None]))  # noqa: E731
        fl = lambda c: r[c]["flood_orange"] + r[c]["flood_blue"]  # noqa: E731
        L.append(f"| {st.describe()} | {pct(mean('orange_in'))} | {pct(mean('blue_in'))} | {pct1(mean('flood_orange'))} | {pct1(mean('flood_blue'))} | "
                 f"{pct1(fl('overheaddim_palewood'))} | {pct1(float(np.mean([fl(c) for c in bath])))} | {pct1(fl('window_light'))} | {pct1(r['window_light'].get('wall_in'))} |")
    (OUT / "measure.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[-(len(SETTINGS) + 3):]))


if __name__ == "__main__":
    sys.exit(main())
