"""The six color methods of the fusion experiment, each brought in unchanged from its own experiment folder, and the
per-fold picks each method's own rule made (plan: PREREG.md).

Several experiment folders hold modules with the same names (``common``, ``candidates``), so each is loaded here under
a name of its own, with the right ``common`` put in place while it loads (``_load``).

    FX   the fixed colors                    pipeline.segment with the adopted model
    C1   contrast, "add" mode               barrels.contrast + experiments/2026-11-26_contrast/candidate.py (Setting)
    P2   peaks, the stripe-pair finder       experiments/2026-11-27_peaks (peaks.find_all, candidates.frame_thresholds)
    SC   self-calibration AB                 barrels.combined.calibrate (= selfcal.SelfCal.run, one round)
    NM   near-miss                           barrels.combined.near_miss with nm_common.parse
    B4   bluer than the light                experiments/2026-11-26_light/rules.segment with B4's Setting

``bundle(place)`` = what each method's own rule picked for the fold that holds ``place`` out (read from the committed
results of each method's branch). Train frames only: images are read by the caller with ``judge.load_frame``.
"""
from __future__ import annotations

import dataclasses
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BARRELS = HERE.parents[1]
EXP = BARRELS / "experiments"
RES = BARRELS / "results"
sys.path.insert(0, str(BARRELS / "src"))

import barrels  # noqa: E402

assert str(Path(barrels.__file__).resolve()).startswith(str(BARRELS)), f"barrels is imported from {barrels.__file__}, not this checkout"

from barrels import combined as cmb  # noqa: E402
from barrels import contrast as cn  # noqa: E402
from barrels import detector as det  # noqa: E402
from barrels import fusion as fu  # noqa: E402
from barrels import geometry as geo  # noqa: E402
from barrels import hslabel as hl  # noqa: E402
from barrels import pipeline as pl  # noqa: E402
from barrels import selfcal as sc  # noqa: E402
from barrels.counting import is_on  # noqa: E402


def _load(name: str, path: Path, aliases: dict | None = None):
    """``path`` as the module ``name``; while it runs, ``aliases`` (module name -> module) stand in sys.modules and
    its folder is first on the import path."""
    if name in sys.modules:
        return sys.modules[name]
    saved = {k: sys.modules.get(k) for k in (aliases or {})}
    sys.modules.update(aliases or {})
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(path.parent))
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    return mod


cn_common = _load("fz_cn_common", EXP / "2026-11-26_contrast" / "common.py")
cn_cand = _load("fz_cn_candidate", EXP / "2026-11-26_contrast" / "candidate.py", {"common": cn_common})
pk_peaks = _load("peaks", EXP / "2026-11-27_peaks" / "peaks.py")
pk_cand = _load("fz_pk_candidates", EXP / "2026-11-27_peaks" / "candidates.py", {"peaks": pk_peaks})
nm_common = _load("nm_common", EXP / "2026-11-26_nearmiss" / "nm_common.py")
lt_common = _load("fz_lt_common", EXP / "2026-11-26_light" / "common.py")
lt_rules = _load("fz_lt_rules", EXP / "2026-11-26_light" / "rules.py", {"common": lt_common})
lt_cand = _load("fz_lt_candidates", EXP / "2026-11-26_light" / "candidates.py", {"common": lt_common, "rules": lt_rules})
stages = _load("stages", EXP / "2026-11-27_bluer_geom" / "stages.py")

CAM = geo.AIM_4A8B6118_BOXFIT
MODEL = hl.adopted_model()
DEF = det.DetConfig()                                        # the detector as it runs today
CFG = det.DetConfig(seams=True, bottom_rule="low_uncut")     # every fusion candidate (PREREG)
CFGS = {"def": DEF, "flags": CFG}
B4_NAME = "B4_ramp_rel_without_loose"
B4_BY_KEY = {s.key: s for s in lt_cand.FAMILIES[B4_NAME]}
LOW = cn.Params(strength_min=1.0)                            # the contrast voter of F3 (margin 0.5, share 0.5: defaults)
ORANGE_MIN = 0.8                                             # ... and the absolute check (contrast's own number)


# ---------------------------------------------------------------- the per-fold picks, as each method's rule made them

def _picks() -> dict[str, dict]:
    c1 = json.loads((RES / "2026-11-26_contrast" / "chosen.json").read_text())["folds"]["C1_add_guards"]
    pk = json.loads((RES / "2026-11-27_peaks" / "chosen.json").read_text())["chosen"]
    cb = json.loads((RES / "2026-11-26_combined" / "chosen.json").read_text())
    bg = json.loads((RES / "2026-11-27_bluer_geom" / "chosen.json").read_text())["folds"]["G1_b4_checks"]
    out = {}
    for place in c1:
        out[place] = {"C1": c1[place]["spec"], "P2": pk[f"P2 without {place}"], "NM": cb[place]["nm"],
                      "SC": cb[place]["sc"], "B4": bg[place]["key"].split("#")[0]}
    return out


PICKS = _picks()


def bundle(place: str) -> dict:
    """What each method's own rule picked for the fold that holds ``place`` out."""
    if place not in PICKS:
        raise KeyError(f"no stored picks for {place!r}")
    return PICKS[place]


def bundle_key(b: dict) -> str:
    return json.dumps(b, sort_keys=True)


def bundles() -> list[dict]:
    return list({bundle_key(b): b for b in PICKS.values()}.values())


def p2_key(s: dict | None) -> str:
    return "fixed" if s is None else json.dumps(s, sort_keys=True)


def sc_key(kw: dict | None) -> str:
    return "fixed" if kw is None else json.dumps(kw, sort_keys=True)


# ---------------------------------------------------------------- one frame

def items_of(mask, cfg: det.DetConfig, method: str) -> list[fu.Item]:
    """The detector's boxes on ``mask`` (``stages.found`` draws exactly ``detector.detect``'s boxes), each with the shape
    checks' measurements."""
    return [fu.Item(f.barrel, method, stages.measure(f, mask, CAM)) for f in stages.found(mask, cfg, CAM)]


class Frame:
    """One frame: the masks and boxes of each method at any setting, computed once."""

    def __init__(self, frame):
        self.frame = frame
        self.rgb = frame.rgb
        self.fixed_mask = pl.segment(frame, MODEL)[0]
        self._items: dict = {}
        self._masks: dict = {}
        self._resp = None
        self._feat = None
        self._peaks = None

    # contrast's shared work
    def resp(self):
        if self._resp is None:
            p = cn.Params()
            self._resp = cn.respond(self.rgb, CAM, p, cn_cand._rows(self.frame.shape, p))
        return self._resp

    def feat(self):
        if self._feat is None:
            p = cn.Params()
            self._feat = cn.features(self.rgb, p.feat_offset, p.bright)
        return self._feat

    def fixed(self, cfg: str) -> list[fu.Item]:
        k = ("FX", cfg)
        if k not in self._items:
            self._items[k] = items_of(self.fixed_mask, CFGS[cfg], fu.FIXED)
        return self._items[k]

    def c1(self, spec: str, cfg: str) -> tuple[list[fu.Item], list]:
        """(C1's boxes: today's boxes plus the contrast mask's boxes on none of them; the candidates that passed C1's
        guards and were painted)."""
        k = ("C1", spec, cfg)
        if k not in self._items:
            st = cn_cand.setting_from(spec)
            p = st.params()
            assert (p.channel, p.offset, p.margin) == ("logrb", 8.0, 0.5), "the shared response assumes contrast's defaults"
            base = self.fixed(cfg)
            cands = cn.find(self.rgb, CAM, p, resp=self.resp())
            mask, cands = cn.contrast_mask(self.rgb, self.fixed_mask, CAM, p, skip_boxes=tuple(b.bbox for b in base),
                                           resp=self.resp(), feat=self.feat(), cands=cands)
            passed = [c for c in cands if not c.info.get("reasons")]
            if not any(c.info.get("painted") for c in cands):
                out = list(base)
            else:
                new = items_of(mask, CFGS[cfg], "C1")
                out = list(base) + [x for x in new if not any(is_on(x.barrel, o.barrel) for o in base)]
            self._items[k] = (sorted(out, key=lambda x: x.bbox[0]), passed)
        return self._items[k]

    def p2_mask(self, s: dict | None):
        k = ("P2", p2_key(s))
        if k not in self._masks:
            if s is None:
                self._masks[k] = self.fixed_mask
            else:
                if self._peaks is None:
                    self._peaks = pk_peaks.find_all(self.frame.bgr)
                th = pk_cand.frame_thresholds(self._peaks["F5_pair"], s)
                self._masks[k] = pl.segment(self.frame, pk_cand.model_of(th))[0]
        return self._masks[k]

    def nm_mask(self, spec: str):
        k = ("NM", spec)
        if k not in self._masks:
            p = nm_common.parse(spec)
            self._masks[k] = cmb.near_miss(self.frame, MODEL, None if p[0] == "fixed" else p[1], CAM, self.fixed_mask)
        return self._masks[k]

    def b4_mask(self, key: str):
        k = ("B4", key)
        if k not in self._masks:
            self._masks[k] = lt_rules.segment(self.frame, B4_BY_KEY[key])
        return self._masks[k]

    def sc_run(self, kw: dict | None):
        """(SC's second-pass mask, its items after the seed rule)."""
        k = ("SC", sc_key(kw))
        if k not in self._items:
            base = self.fixed("flags")
            if kw is None:
                self._items[k] = (self.fixed_mask, list(base))
            else:
                cfg = dataclasses.replace(sc.SelfCalConfig(), **kw)
                b1 = [x.barrel for x in base]
                mask, boxes, seeds, _ = cmb.calibrate(self.frame, MODEL, self.fixed_mask, b1, cfg, CAM, CFG)
                if mask is self.fixed_mask:
                    self._items[k] = (mask, list(base))
                else:
                    its = items_of(mask, CFG, "SC")
                    if cfg.seed_rules:
                        keep = {id(b) for b in cmb.seed_rule([x.barrel for x in its], [s for s in seeds if s.ok])}
                        its = [x for x in its if id(x.barrel) in keep]
                    self._items[k] = (mask, its)
        return self._items[k]

    def method_items(self, m: str, b: dict) -> list[fu.Item]:
        """The boxes of method ``m`` (SC, P2, NM, B4) at the bundle's pick, with the fusion's detector (CFG)."""
        if m == "SC":
            return self.sc_run(b["SC"])[1]
        mask = {"P2": lambda: self.p2_mask(b["P2"]), "NM": lambda: self.nm_mask(b["NM"]), "B4": lambda: self.b4_mask(b["B4"])}[m]()
        if mask is self.fixed_mask:
            return [dataclasses.replace(x, method=m) for x in self.fixed("flags")]
        key = (m, {"P2": p2_key(b["P2"]), "NM": b["NM"], "B4": b["B4"]}[m])
        if key not in self._items:
            self._items[key] = items_of(mask, CFG, m)
        return self._items[key]

    def method_mask(self, m: str, b: dict):
        return {"SC": lambda: self.sc_run(b["SC"])[0], "P2": lambda: self.p2_mask(b["P2"]), "NM": lambda: self.nm_mask(b["NM"])}[m]()

    def low_candidates(self) -> list[tuple]:
        """The contrast voter: (color, x, row, strength) of the candidates at strength >= 1.0 that pass the absolute check."""
        k = ("LOW",)
        if k not in self._items:
            out = []
            for c in cn.find(self.rgb, CAM, LOW, resp=self.resp()):
                info = cn.measure(c, self.resp(), self.feat(), LOW)
                op = info.get("orange_part")
                if op is not None and op >= ORANGE_MIN:
                    out.append((c.color, c.x, c.row, c.strength))
            self._items[k] = out
        return self._items[k]

    def f4(self, b: dict, kept: list[fu.Item], ck: fu.Checks) -> list[fu.Item]:
        """F4: the C1 candidates (its guards passed) whose stripe point is in no kept box; inside each one's predicted box
        (grown by contrast's box_slack) the paint of SC, P2 and NM where the fixed mask is empty; the detector once more;
        the new boxes on no kept box that pass the checks."""
        _, passed = self.c1(b["C1"], "flags")
        todo = [c for c in passed if not any(x.bbox[0] <= c.x < x.bbox[2] and x.bbox[1] <= c.row < x.bbox[3] for x in kept)]
        if not todo:
            return []
        out = self.fixed_mask.copy()
        h, w = out.shape
        slack = cn.Params().box_slack
        region = out == 255
        region[:] = False
        for c in todo:
            x0, top, x1, bottom = c.box
            sx, sy = slack * (x1 - x0), slack * (bottom - top)
            xa, xb = max(0, int(round(x0 - sx))), min(w, int(round(x1 + sx)))
            ya, yb = max(0, int(round(top - sy))), min(h, int(round(bottom + sy)))
            region[ya:yb, xa:xb] = True
        for m in ("SC", "P2", "NM"):
            src = self.method_mask(m, b)
            sel = region & (out == 0) & ((src == 1) | (src == 2))
            out[sel] = src[sel]
        if (out == self.fixed_mask).all():
            return []
        new = items_of(out, CFG, "F4")
        return [x for x in new if not any(fu.is_on(x, k) for k in kept) and not fu.removes(x.measure, ck)]
