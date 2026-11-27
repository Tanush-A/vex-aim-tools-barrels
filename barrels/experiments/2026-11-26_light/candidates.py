"""The candidates of the 2026-11-26 light experiment, as the judge wants them: per family a function
``fit(train_stems, held_place) -> detect_frame`` (plan: PREREG.md; the color steps: rules.py).

A *family* is a list of settings (``rules.Setting``), the most cautious first. ``fit`` picks one setting of its family
on the training places and returns the detector of that setting; the judge runs it on the held-out place only.

**How a setting is picked inside a fold** (``choose``; the same rule for every family):

1. Every setting of the family and the fixed model are run on every training frame (the color step, today's detector,
   the judge's own counting: ``counting.classify_frame``). Done once for all frames and kept in ``table``.
2. On the training places together, a setting is *allowed* when the standard pass rule (``judge.decide``, with the
   stored margins) does not call it FAIL against the fixed model on those places.
3. Among the allowed settings the one with the highest *gain* is taken: gain = (found, per placement) minus (boxes
   that are not on their barrel, per arrangement), each as the difference from the fixed model.
4. A tie goes to the setting that comes first in the family (the most cautious). No allowed setting with a gain above
   zero: the fixed model.

Train frames only: the table is built with ``judge.load_frame``, which refuses anything else.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as cm  # noqa: E402
import rules as ru  # noqa: E402

from barrels import counting as ct  # noqa: E402
from barrels import detect_types as dtp  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402

CACHE = cm.OUT / "cache"
S = ru.Setting

# ---------------------------------------------------------------- the families (PREREG.md, "The candidates")

RAMP = list(itertools.product((0.11, 0.08, 0.05), (0.30, 0.24, 0.18), (60.0, 45.0, 30.0), (96.0, 88.0)))     # w0, w1, s_warm, h_warm: most cautious first
DELTAS = (0.30, 0.25, 0.20, 0.15)                                                                           # the larger, the more cautious


def ramp(reading: str) -> list[S]:
    return [S(reading, w0, w1, s, h) for w0, w1, s, h in RAMP]


def ramp_rel(reading: str) -> list[S]:
    return ramp(reading) + [S(reading, w0, w1, s, h, d) for d in DELTAS for w0, w1, s, h in RAMP]


def orange(reading: str, ends: list[tuple[float, float]], guards=(0.0,)) -> list[S]:
    return [S(o_reading=reading, o_x0=x0, o_x1=x1, o_hi=hi, o_guard=g) for hi in (16.0, 19.0, 22.0) for g in guards for x0, x1 in ends]


FAMILIES: dict[str, list[S]] = {
    "B1_ramp_without_loose": ramp("without_loose"),
    "B2_ramp_above_gate": ramp("above_gate20"),
    "B3_ramp_whole_frame": ramp("whole_frame"),
    "B4_ramp_rel_without_loose": ramp_rel("without_loose"),
    "O1_orange_follows_light": orange("without_loose", [(0.10, 0.25), (0.05, 0.20), (0.0, 0.15)]),
    "O2_orange_follows_dark": orange("dark", [(60.0, 40.0), (90.0, 45.0), (120.0, 60.0)]),
    "O3_orange_wide_with_guard": orange("always", [(0.0, 1.0)], guards=(0.02, 0.05, 0.10, 0.20)),
}
TITLES = {
    "B1_ramp_without_loose": "B1 blue follows the light; light = the brightest 5 % after taking out anything barrel-like (primary)",
    "B2_ramp_above_gate": "B2 the same; light = the brightest 20 % of the rows above the horizon gate",
    "B3_ramp_whole_frame": "B3 the same; light = the brightest 5 % of the whole frame (the reading of 2026-11-25)",
    "B4_ramp_rel_without_loose": "B4 = B1 plus 'bluer than the light' for the gray-olive blue",
    "O1_orange_follows_light": "O1 the orange hue high end follows the light",
    "O2_orange_follows_dark": "O2 the orange hue high end follows how dark the scene is",
    "O3_orange_wide_with_guard": "O3 a wider orange range everywhere it does not flood (the flood guard)",
}


def all_settings() -> list[S]:
    return list(dict.fromkeys([ru.FIXED] + [s for fam in FAMILIES.values() for s in fam]))


# ---------------------------------------------------------------- every setting on every frame, once

def _frame_counts(args) -> tuple[str, dict]:
    """One frame, many settings -> key -> the frame's counts (``FrameCount.to_dict``). A mask seen before on this
    frame is not detected again. Kept in results/2026-11-26_light/cache/ (not committed)."""
    import cv2
    cv2.setNumThreads(1)
    stem, settings = args
    p = CACHE / f"{stem}.json"
    have = json.loads(p.read_text()) if p.exists() else {}
    todo = [s for s in settings if s.key not in have]
    if todo:
        frame = jg.load_frame(stem)                                     # refuses anything but a train frame
        label = io.load_boxes(stem, check_image=False)
        gts = dtp.barrels_from_boxes(label)
        seen: dict = {}
        for s in todo:
            mask = ru.segment(frame, s)
            h = hashlib.blake2b(mask.tobytes(), digest_size=16).digest()
            if h not in seen:
                preds = det.detect(mask, det.DetConfig(), ru.CAM)
                seen[h] = ct.classify_frame(stem, preds, gts, bool(label.get("clean", True))).to_dict()
            have[s.key] = seen[h]
        CACHE.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(have))
    return stem, {s.key: have[s.key] for s in settings}


def build_table(stems: list[str], settings: list[S] | None = None, jobs: int = 8, progress: bool = True) -> dict[str, dict]:
    """stem -> setting key -> ``FrameCount``, for every setting on every one of ``stems`` (train frames only)."""
    jg.require_train(stems)
    settings = settings or all_settings()
    table: dict[str, dict] = {}
    with Pool(jobs) as pool:
        for i, (stem, out) in enumerate(pool.imap_unordered(_frame_counts, [(s, settings) for s in stems], chunksize=1)):
            table[stem] = {k: ct.FrameCount.from_dict(v) for k, v in out.items()}
            if progress and (i + 1) % 40 == 0:
                print(f"  table: {i + 1}/{len(stems)} frames x {len(settings)} settings", flush=True)
    return table


# ---------------------------------------------------------------- the rule that picks a setting

def tallies(table: dict, key: str, stems: list[str], placements: ct.Placements) -> tuple[ct.Tally, dict[str, ct.Tally]]:
    counts = {s: table[s][key] for s in stems}
    return ct.tally(counts, stems, placements), {p: ct.tally(counts, ss, placements) for p, ss in ct.group_stems(stems, "place").items()}


def choose(table: dict, family: list[S], stems: list[str], placements: ct.Placements, margins: jg.Margins) -> tuple[S, dict]:
    """The setting of ``family`` picked on the frames ``stems`` by the written rule, and what it rests on."""
    base, base_places = tallies(table, ru.FIXED.key, stems, placements)
    best, best_gain, allowed, top = ru.FIXED, 0.0, 0, []
    for st in family:
        cand, cand_places = tallies(table, st.key, stems, placements)
        verdict = jg.decide(base, cand, {p: (base_places[p], cand_places[p]) for p in base_places}, margins)
        if verdict.result == jg.FAIL:
            continue
        allowed += 1
        gain = (cand.found_w - base.found_w) - (cand.extra_w - base.extra_w)
        top.append((gain, st))
        if gain > best_gain + 1e-9:
            best, best_gain = st, gain
    cand, _ = tallies(table, best.key, stems, placements)
    return best, {"allowed": allowed, "of": len(family), "gain": round(best_gain, 3), "found_w": round(cand.found_w - base.found_w, 3),
                  "extra_w": round(cand.extra_w - base.extra_w, 3),
                  "runner_up_gain": round(sorted((g for g, s in top if s != best), reverse=True)[0], 3) if len(top) > 1 else None}


class Fitter:
    """Holds the table and hands the judge one ``fit`` per family. ``chosen[family][held_place]`` records the picks."""

    def __init__(self, table: dict, placements: ct.Placements, margins: jg.Margins | None = None):
        self.table, self.placements, self.margins = table, placements, margins or jg.load_margins()
        self.chosen: dict[str, dict] = {n: {} for n in FAMILIES}

    def fit(self, name: str):
        family = FAMILIES[name]

        def fit(train_stems: list[str], held_place: str):
            st, info = choose(self.table, family, [s for s in train_stems if s in self.table], self.placements, self.margins)
            self.chosen[name][held_place] = {"setting": st.describe(), "key": st.key, **info}

            def detect_frame(stem: str, frame) -> list:
                return ru.detect(frame, st)
            detect_frame.describe = st.describe()
            return detect_frame
        fit.describe = f"{TITLES[name]}: the setting picked on the other places"
        return fit
