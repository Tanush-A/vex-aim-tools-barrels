"""The judged round of the contrast-gaps experiment (plan: PREREG.md). Every family judged leave one place out by the
standard pass rule against today's default; the results in ``results/2026-11-27_contrast_gaps/``.

    python barrels/experiments/2026-11-27_contrast_gaps/run.py            # every family, then summary.md
    python barrels/experiments/2026-11-27_contrast_gaps/run.py ALL        # one family

``best`` (below) is the primary candidate (ALL) as one importable callable: each number the pick of its own family on
all eight places (in-sample; the judged result is the leave-one-place-out run).
"""
from __future__ import annotations

import json
import pickle
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gaps as gp  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402

OUT = gp.BARRELS / "results" / "2026-11-27_contrast_gaps"
CACHE = OUT / "cache"                  # per-frame counts of every setting (not committed)
G = gp.Gaps
FIXED = G().key

FAMILIES: dict[str, list] = {
    "E_edge": [G(edge=v) for v in (0.6, 0.5, 0.4)],
    "H_half": [G(half=v) for v in (1.5, 1.3, 1.15, 1.0)],
    "S_split": [G(split=v) for v in (1.25, 1.2, 1.15, 1.1)],
    "B_beside": [G(beside=v) for v in (1.0, 0.9, 0.8)],
    "O_other": [G(other=v) for v in (0.5, 0.4)],
}
FIELD = {"E_edge": "edge", "H_half": "half", "S_split": "split", "B_beside": "beside", "O_other": "other"}
TITLES = {
    "E_edge": "E: a window the side of the frame cuts is counted inside the frame",
    "H_half": "H: the half sandwich at the bottom of the frame (close-ups)",
    "S_split": "S: a fixed-colors box two barrels wide is split by the run on the painted mask",
    "B_beside": "B: a weaker candidate beside a found barrel, at its stripe row",
    "O_other": "O: two boxes of different colors on one barrel: the one the stripe pattern supports less is dropped",
    "ALL": "ALL (primary): E + H + S + B + O, each number its own family's pick",
}
TRAPS = ("_neg_02", "lampwarm6_glass_occl_02")


# ---------------------------------------------------------------- every setting on every ordinary frame, once

def _frame_counts(args):
    import cv2
    cv2.setNumThreads(1)
    stem, settings = args
    p = CACHE / f"{stem}.pkl"
    have = pickle.loads(p.read_bytes()) if p.exists() else {}
    todo = [s for s in [G()] + settings if s.key not in have]
    if todo:
        frame = jg.load_frame(stem)
        label = io.load_boxes(stem, check_image=False)
        gts = dtp.barrels_from_boxes(label)
        clean = bool(label.get("clean", True))
        for s in todo:
            have[s.key] = ct.classify_frame(stem, gp.detect(frame, s), gts, clean).to_dict()
        CACHE.mkdir(parents=True, exist_ok=True)
        p.write_bytes(pickle.dumps(have))
    return stem, {k: have[k] for k in [FIXED] + [s.key for s in settings]}


def build_table(stems, settings, jobs=8):
    jg.require_train(stems)
    table = {}
    with Pool(jobs) as pool:
        for stem, out in pool.imap_unordered(_frame_counts, [(s, settings) for s in stems], chunksize=1):
            table[stem] = {k: ct.FrameCount.from_dict(v) for k, v in out.items()}
    return table


# ---------------------------------------------------------------- the fold rule (2026-11-26_contrast/table.choose, word for word)

def tallies(table, key, stems, placements):
    counts = {s: table[s][key] for s in stems}
    return ct.tally(counts, stems, placements), {p: ct.tally(counts, ss, placements) for p, ss in ct.group_stems(stems, "place").items()}


def choose(table, family, stems, placements, margins):
    base, base_places = tallies(table, FIXED, stems, placements)
    best, best_gain, allowed = None, 0.0, 0
    for st in family:
        cand, cand_places = tallies(table, st.key, stems, placements)
        verdict = jg.decide(base, cand, {p: (base_places[p], cand_places[p]) for p in base_places}, margins)
        if verdict.result == jg.FAIL:
            continue
        allowed += 1
        gain = (cand.found_w - base.found_w) - (cand.extra_w - base.extra_w)
        if gain > best_gain + 1e-9:
            best, best_gain = st, gain
    return best, {"allowed": allowed, "of": len(family), "gain": round(best_gain, 3)}


class Fitter:
    def __init__(self, table, placements, margins=None):
        self.table, self.placements, self.margins = table, placements, margins or jg.load_margins()
        self.chosen: dict[str, dict] = {}

    def pick(self, name, train_stems):
        return choose(self.table, FAMILIES[name], [s for s in train_stems if s in self.table], self.placements, self.margins)

    def fit(self, name):
        def fit(train_stems, held_place):
            if name == "ALL":
                kw, info = {}, {}
                for fam in FAMILIES:
                    st, i = self.pick(fam, train_stems)
                    if st is not None:
                        kw[FIELD[fam]] = getattr(st, FIELD[fam])
                    info[fam] = i
                g = G(**kw)
            else:
                g, info = self.pick(name, train_stems)
                g = g or G()
            self.chosen.setdefault(name, {})[held_place] = {"setting": g.describe(), "key": g.key, "info": info}
            return gp.detector_of(g)
        fit.describe = TITLES[name] + ": the setting picked on the other places"
        return fit


def all_places_pick(table, placements):
    """ALL's numbers picked on all eight places (in-sample): what ``best`` runs."""
    stems = list(table)
    kw = {}
    for fam in FAMILIES:
        st, _ = choose(table, FAMILIES[fam], stems, placements, jg.load_margins())
        if st is not None:
            kw[FIELD[fam]] = getattr(st, FIELD[fam])
    return G(**kw)


# ---------------------------------------------------------------- the round

def traps(j) -> list[str]:
    """Boxes on the near-barrel traps that today's default does not draw."""
    bad = []
    for s, boxes in j.candidate.boxes.items():
        if any(t in s for t in TRAPS):
            base = {(b.color, b.bbox) for b in j.baseline.boxes.get(s, [])}
            new = [b.bbox for b in boxes if (b.color, b.bbox) not in base]
            if new:
                bad.append(f"{s}: {new}")
    return bad


def row_of(name, j, fitter) -> dict:
    b, c = j.total
    gained = [ch for ch in j.changes if ch.judged and ch.kind == "gained"]
    lost = [ch for ch in j.changes if ch.judged and ch.kind == "lost"]
    rep_g = [ch for ch in j.changes if not ch.judged and ch.kind == "gained"]
    rep_l = [ch for ch in j.changes if not ch.judged and ch.kind == "lost"]
    moved = {p: round(t[1].found_w - t[0].found_w, 2) for p, t in j.places.items() if abs(t[1].found_w - t[0].found_w) > 1e-9}
    moved_x = {p: round(t[1].extra_w - t[0].extra_w, 2) for p, t in j.places.items() if abs(t[1].extra_w - t[0].extra_w) > 1e-9}
    return {"name": name, "title": TITLES[name], "verdict": j.result, "why": j.verdict.reason if hasattr(j.verdict, "reason") else "",
            "found_w": [round(b.found_w, 2), round(c.found_w, 2)], "found_frame": [b.found, c.found], "off": [b.off, c.off],
            "extra_w": [round(b.extra_w, 2), round(c.extra_w, 2)], "extra_raw": [b.wrong + b.second + b.nothing, c.wrong + c.second + c.nothing],
            "empty": [b.empty, c.empty], "clean_empty": [b.clean_empty, c.clean_empty],
            "gained": len(gained), "lost": len(lost), "report_gained": len(rep_g), "report_lost": len(rep_l),
            "places_found": moved, "places_extra": moved_x, "traps": traps(j), "chosen": fitter.chosen.get(name, {}),
            "gained_list": [(ch.stem, ch.bbox, ch.before) for ch in gained + rep_g], "lost_list": [(ch.stem, ch.bbox, ch.after) for ch in lost + rep_l],
            "box_changes": j.box_changes}


def main(names) -> int:
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    settings = list(dict.fromkeys(s for f in FAMILIES.values() for s in f))
    table = build_table(ordinary, settings)
    placements = jg.load_truth(ordinary).placements
    fitter = Fitter(table, placements)
    rows = []
    for name in names:
        j = jg.judge(fit=fitter.fit(name), name=name, out_dir=OUT / f"judge_{name}", frames=frames)
        r = row_of(name, j, fitter)
        rows.append(r)
        (OUT / f"judge_{name}" / "chosen.json").write_text(json.dumps(r["chosen"], indent=1))
        print(f"{name:10s} {r['verdict']:22s} found {r['found_w'][0]} -> {r['found_w'][1]} (per frame {r['found_frame'][0]} -> {r['found_frame'][1]}), "
              f"gained {r['gained']} lost {r['lost']}, boxes not on barrel {r['extra_w'][0]} -> {r['extra_w'][1]}, empty {r['empty']}, traps {r['traps'] or 'clean'}", flush=True)
    best_g = all_places_pick(table, placements)
    (OUT / "rows.json").write_text(json.dumps({"rows": rows, "best_in_sample": best_g.key, "best_describe": best_g.describe()}, indent=1, default=str))
    return 0


def best_setting() -> gp.Gaps:
    """The in-sample pick of ALL on all eight places, as written by the last ``main`` (rows.json)."""
    j = json.loads((OUT / "rows.json").read_text())
    kw = {}
    for part in j["best_in_sample"].split("|"):
        k, v = part[0], part[1:]
        if v != "-":
            kw[{"e": "edge", "h": "half", "s": "split", "b": "beside", "o": "other"}[k]] = float(v)
    return G(**kw)


def best(stem: str, frame) -> list:
    """The primary candidate at its all-places setting (``best_setting``); importable for ``tools/vs_vendor.py``."""
    global _BEST
    if _BEST is None:
        _BEST = best_setting()
    return gp.detect(frame, _BEST)


_BEST = None


def masks(stem: str, frame):
    """(the fixed colors' mask, the mask with every paint of ``best``) for the segmentation panel of tools/vs_vendor.py."""
    global _BEST
    if _BEST is None:
        _BEST = best_setting()
    tr = gp.Trace()
    gp.detect(frame, _BEST, tr)
    return tr.base_mask, tr.painted2 if tr.painted2 is not None else tr.painted


def main_insample() -> int:
    """Second round (PREREG addendum): each family and ALL as a FIXED callable at the setting the fold rule picks on all
    eight places. In-sample."""
    frames = jg.train_frames()
    ordinary = frames[cnd.ORDINARY]
    settings = list(dict.fromkeys(s for f in FAMILIES.values() for s in f))
    table = build_table(ordinary, settings)
    placements = jg.load_truth(ordinary).placements
    margins = jg.load_margins()
    rows = []
    fitter = Fitter(table, placements)
    for name in list(FAMILIES) + ["ALL"]:
        if name == "ALL":
            g = all_places_pick(table, placements)
        else:
            g = choose(table, FAMILIES[name], ordinary, placements, margins)[0] or G()
        det = gp.detector_of(g)
        j = jg.judge(det, name=f"{name}_insample", out_dir=OUT / f"judge_insample_{name}", frames=frames)
        r = row_of(name, j, fitter)
        r["setting"] = g.describe()
        r["key"] = g.key
        rows.append(r)
        print(f"{name:10s} [{g.key}] {r['verdict']:22s} found {r['found_w'][0]} -> {r['found_w'][1]} (per frame {r['found_frame'][0]} -> {r['found_frame'][1]}), "
              f"gained {r['gained']} lost {r['lost']} (report only +{r['report_gained']} -{r['report_lost']}), boxes not on barrel {r['extra_w'][0]} -> {r['extra_w'][1]}, "
              f"empty {r['empty']}, traps {r['traps'] or 'clean'}", flush=True)
    (OUT / "rows_insample.json").write_text(json.dumps({"rows": rows}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["--insample"]:
        raise SystemExit(main_insample())
    raise SystemExit(main(sys.argv[1:] or list(FAMILIES) + ["ALL"]))


def today(stem: str, frame) -> list:
    """Today's default through the same path (the baseline row of tools/vs_vendor.py)."""
    return gp.detect(frame, G())
