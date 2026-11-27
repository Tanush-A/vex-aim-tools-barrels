"""Shared by the scripts of the self-calibration experiment: the fixed model, running one setting on train frames,
the counts per condition, the seed statistics, the paint outside the hand boxes. Train frames only: every image is
read through ``judge.load_frame``, which refuses anything else."""
from __future__ import annotations

import collections
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import selfcal as sc  # noqa: E402

CAM = geo.AIM_4A8B6118_BOXFIT
MODEL = hl.adopted_model()
HERE = Path(__file__).resolve().parent
RESULTS = HERE.parents[1] / "results" / "2026-11-26_selfcal"
GROW = 4                                    # a hand box grown by this many pixels: paint inside it is on the barrel


def outside_paint(mask: np.ndarray, gts) -> int:
    """Painted pixels that are not inside any hand box (grown by ``GROW``)."""
    inside = np.zeros(mask.shape, bool)
    for g in gts:
        x0, y0, x1, y1 = g.bbox
        inside[max(0, y0 - GROW):y1 + GROW, max(0, x0 - GROW):x1 + GROW] = True
    return int(((mask > 0) & ~inside).sum())


def run_setting(cfg: sc.SelfCalConfig, stems, truth, extra: dict | None = None, keep_results: bool = False) -> dict:
    """One setting on a list of train frames -> {stem: record}. ``extra``: {stem: readings} carried in from other
    frames (report only)."""
    cal = sc.SelfCal(MODEL, cfg, CAM)
    out = {}
    for s in stems:
        frame = jg.load_frame(s)
        r = cal.run(frame, (extra or {}).get(s))
        out[s] = {
            "count": ct.classify_frame(s, r.boxes, truth.gts[s], truth.clean[s]),
            "first": ct.classify_frame(s, r.first, truth.gts[s], truth.clean[s]),
            "boxes": r.boxes,
            "seeds": [(x.kind, sc.NAME[x.body], x.bbox, x.ok, x.why, round(x.rel, 2)) for x in r.seeds],
            "kept": [x for x in r.seeds if x.ok],
            "moved": r.info.get("moved", []), "flood": r.info.get("flood", {}), "ranges": r.info.get("ranges", {}),
            "out1": outside_paint(r.mask1, truth.gts[s]), "out2": outside_paint(r.mask2, truth.gts[s]),
            "result": r if keep_results else None,
        }
    return out


def seed_on_barrel(seed_bbox, gts) -> bool:
    return any(ct.on_share(seed_bbox, g.bbox) >= 0.5 for g in gts)


def per_condition(recs: dict, truth, placements=None) -> list[dict]:
    """One row per condition: frames, barrels, found (per frame), found before, boxes not on their barrel, boxes on
    empty frames, kept seeds by kind, kept seeds that are not on a hand box, frames with a kept seed, frames whose
    range moved, paint outside the hand boxes before and after."""
    rows = collections.OrderedDict()
    for s, r in recs.items():
        c = ct.condition_of(s)
        row = rows.setdefault(c, collections.Counter())
        gts = truth.gts[s]
        fc, f1 = r["count"], r["first"]
        row["frames"] += 1
        row["frames_b"] += bool(gts)
        row["barrels"] += len(gts)
        row["found"] += fc.n_gt(ct.FOUND)
        row["found1"] += f1.n_gt(ct.FOUND)
        row["off"] += fc.n_gt(ct.OFF)
        row["extra"] += fc.extra
        row["extra1"] += f1.extra
        row["empty"] += fc.extra if not gts else 0
        for x in r["kept"]:
            row["seed_" + x.kind] += 1
            row["seed_off_barrel"] += not seed_on_barrel(x.bbox, gts)
        row["frames_seed"] += bool(r["kept"]) and bool(gts)
        row["frames_seed_empty"] += bool(r["kept"]) and not gts
        row["frames_moved"] += bool(r["moved"])
        row["out1"] += r["out1"]
        row["out2"] += r["out2"]
    return [{"condition": c, "class": cnd.info(c).klass, **v} for c, v in rows.items()]


def format_conditions(rows: list[dict], title: str = "") -> str:
    cols = [("frames", "frm"), ("barrels", "brl"), ("found1", "fix"), ("found", "cand"), ("off", "off"), ("extra1", "xtr1"), ("extra", "xtr"),
            ("empty", "emp"), ("frames_b", "fr.b"), ("frames_seed", "fr.sd"), ("seed_found", "s.fnd"), ("seed_body", "s.bdy"), ("seed_stripe", "s.str"),
            ("seed_off_barrel", "s.off"), ("frames_seed_empty", "sd.emp"), ("frames_moved", "moved"), ("out1", "paint.out1"), ("out2", "paint.out2")]
    lines = [title] if title else []
    lines.append(f"{'condition':22s} {'class':8s} " + " ".join(f"{h:>6s}" if k not in ("out1", "out2") else f"{h:>10s}" for k, h in cols))
    tot = collections.Counter()
    for r in rows:
        lines.append(f"{r['condition']:22s} {r['class']:8s} " + " ".join(f"{r.get(k, 0):6d}" if k not in ("out1", "out2") else f"{r.get(k, 0):10d}" for k, _ in cols))
        if r["class"] == cnd.ORDINARY:
            for k, _ in cols:
                tot[k] += r.get(k, 0)
    lines.append(f"{'ALL ORDINARY':22s} {'':8s} " + " ".join(f"{tot[k]:6d}" if k not in ("out1", "out2") else f"{tot[k]:10d}" for k, _ in cols))
    return "\n".join(lines)


def tally_ordinary(recs: dict, frames: dict, truth) -> ct.Tally:
    return ct.tally({s: r["count"] for s, r in recs.items()}, frames[cnd.ORDINARY], truth.placements)


def refusals(recs: dict) -> collections.Counter:
    c = collections.Counter()
    for r in recs.values():
        for kind, _, _, ok, why, _ in r["seeds"]:
            c[(kind, why)] += 1
    return c
