"""Hue x saturation histograms of frames (TODO step 8, 2026-11-16): how much do H and S of the barrels and of the
table move between light settings and tables? An analysis helper, not part of the detector: nothing here feeds
``pipeline`` or ``detector``.

How the data flows:

1. ``planes``        BGR -> (hue rolled by +30 so orange does not straddle the 0/180 wrap, HSV saturation, value).
2. ``region_masks``  from the hand-drawn boxes: per class the **core** of every unoccluded box (the inner
   0.6 x 0.8 of it, minus anything inside another barrel's box), and **rest** = everything outside every box
   (padded by 4 px). Boxes, not masks: the new sets have boxes only. A core is nearly all barrel, but it holds
   the stripe (the other color) too, so
3. ``SetHist.body``  keeps the core pixels whose hue is within +-12 of the tallest hue peak of that class's cores:
   the body color. Where masks exist (HOME) the same numbers are also made from the masks, as a check.
4. ``SetHist``       accumulates, per set of frames, one fine histogram (hue 180 x S 128 x V 32) per region; every
   table and picture is made from those.
5. ``recall_at_flood``  the best a per-set lookup in H x S (or H x S x V) could do: the share of body pixels in the
   bins it may paint while painting at most 1 % of the non-barrel pixels. In-sample, so an upper bound.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np

from . import pipeline as pl
from .io import BLUE, ORANGE

ROLL = 30                       # hue is handled as (h + 30) % 180: orange (about 3-13) becomes 33-43, contiguous
NH, NS, NV = 180, 128, 32       # fine bins: hue 1 unit, S 2 units, V 8 units
CORE = (0.6, 0.8)               # the inner fraction (width, height) of a box taken as "surely barrel"
PEAK_HALF = 12                  # body color = hue within this of the tallest hue peak of the cores
REST_PAD = 4                    # px added around every box before calling the outside "rest"
SKIP_FLAGS = ("occluded",)      # boxes whose inside may hold the occluder: no core taken
NAMES = {ORANGE: "orange", BLUE: "blue"}


def planes(bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(rolled hue 0-179, HSV saturation 0-255, value 0-255) as int32, the same HSV the hs color model uses."""
    hsv = cv2.cvtColor(np.ascontiguousarray(bgr), cv2.COLOR_BGR2HSV).astype(np.int32)
    return (hsv[..., 0] + ROLL) % 180, hsv[..., 1], hsv[..., 2]


def unroll(h) -> np.ndarray:
    """Rolled hue -> real OpenCV hue in -30..149 (-3 means 177), so a sector across the red wrap reads naturally."""
    return np.asarray(h, float) % 180 - ROLL


def fine_hist(h: np.ndarray, s: np.ndarray, v: np.ndarray, sel: np.ndarray) -> np.ndarray:
    """Counts [NH, NS, NV] of the selected pixels."""
    idx = (h[sel] * NS + (s[sel] >> 1)) * NV + (v[sel] >> 3)
    return np.bincount(idx, minlength=NH * NS * NV).reshape(NH, NS, NV)


def rebin(a: np.ndarray, h_bins: int, s_bins: int, v_bins: int | None = None) -> np.ndarray:
    """A fine histogram [NH, NS(, NV)] summed into coarser bins; the total is unchanged. V is summed away when
    ``v_bins`` is None and the input has a V axis."""
    if a.ndim == 3 and v_bins is None:
        a = a.sum(2)
    hi = (np.arange(NH) * h_bins) // NH
    si = (np.arange(NS) * s_bins) // NS
    out = np.zeros((h_bins, NS) + a.shape[2:], a.dtype)
    np.add.at(out, hi, a)
    out2 = np.zeros((h_bins, s_bins) + a.shape[2:], a.dtype)
    np.add.at(out2, (slice(None), si), out)
    if a.ndim == 3:
        vi = (np.arange(NV) * v_bins) // NV
        out3 = np.zeros((h_bins, s_bins, v_bins), a.dtype)
        np.add.at(out3, (slice(None), slice(None), vi), out2)
        return out3
    return out2


def wpct(counts: np.ndarray, centers: np.ndarray, qs) -> list[float]:
    """Percentiles of a 1-D histogram (nan when it is empty)."""
    tot = counts.sum()
    if tot <= 0:
        return [float("nan")] * len(qs)
    cum = np.cumsum(counts) / tot
    return [float(centers[min(int(np.searchsorted(cum, q / 100.0)), len(centers) - 1)]) for q in qs]


def core_of(bbox, fx: float = CORE[0], fy: float = CORE[1]) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = bbox
    dx, dy = (x1 - x0) * (1 - fx) / 2, (y1 - y0) * (1 - fy) / 2
    return int(round(x0 + dx)), int(round(y0 + dy)), int(round(x1 - dx)), int(round(y1 - dy))


def region_masks(shape: tuple[int, int], barrels: list[dict]) -> dict:
    """{ORANGE: cores of the orange boxes, BLUE: cores of the blue boxes, "rest": outside every padded box}.
    ``barrels`` are the label dicts (``color``, ``bbox``, ``flags``). A core never includes a pixel that lies
    inside another barrel's box; occluded boxes give no core but still count as "not rest"."""
    h, w = shape
    out = {ORANGE: np.zeros(shape, bool), BLUE: np.zeros(shape, bool), "rest": np.ones(shape, bool)}
    cls = {"orange": ORANGE, "blue": BLUE}
    for b in barrels:
        x0, y0, x1, y1 = b["bbox"]
        out["rest"][max(0, y0 - REST_PAD):min(h, y1 + REST_PAD), max(0, x0 - REST_PAD):min(w, x1 + REST_PAD)] = False
    for i, b in enumerate(barrels):
        if any(f in b.get("flags", ()) for f in SKIP_FLAGS):
            continue
        m = np.zeros(shape, bool)
        x0, y0, x1, y1 = core_of(b["bbox"])
        m[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True
        for j, o in enumerate(barrels):
            if j != i:
                ox0, oy0, ox1, oy1 = o["bbox"]
                m[max(0, oy0):max(0, oy1), max(0, ox0):max(0, ox1)] = False
        out[cls[b["color"]]] |= m
    return out


def _z() -> np.ndarray:
    return np.zeros((NH, NS, NV), np.int64)


@dataclass
class SetHist:
    """The fine histograms of one set of frames. Everything is below the model's horizon row; the brightness
    gate (V >= v_min) is applied when a number is read, so the dark pixels are still counted."""
    name: str
    exact_body: bool = False            # True: the "core" pixels came from masks, so the body is all of them
    v_min: int = 40
    frames: int = 0
    core: dict = field(default_factory=lambda: {ORANGE: _z(), BLUE: _z()})
    core_pass: dict = field(default_factory=lambda: {ORANGE: _z(), BLUE: _z()})     # ... that the model labels as that class
    rest: np.ndarray = field(default_factory=_z)
    rest_pass: dict = field(default_factory=lambda: {ORANGE: 0, BLUE: 0})           # rest pixels the model paints
    stems: list = field(default_factory=list)

    @property
    def vb(self) -> int:
        return self.v_min >> 3

    def add(self, stem: str, bgr: np.ndarray, barrels: list[dict], model: pl.Model, mask: np.ndarray | None = None) -> None:
        """One frame. ``mask`` (a class mask) replaces the box cores as the source of the barrel pixels."""
        assert model.cfg.v_min == self.v_min and self.v_min % 8 == 0
        seg, _ = pl.segment(pl.Frame.from_image(bgr), model)
        h, s, v = planes(bgr)
        rows = np.zeros(h.shape, bool)
        rows[max(0, model.cfg.horizon_row or 0):] = True
        reg = region_masks(h.shape, barrels)
        for c in (ORANGE, BLUE):
            sel = ((mask == c) if mask is not None else reg[c]) & rows
            self.core[c] += fine_hist(h, s, v, sel)
            self.core_pass[c] += fine_hist(h, s, v, sel & (seg == c))
        sel = reg["rest"] & rows
        self.rest += fine_hist(h, s, v, sel)
        for c in (ORANGE, BLUE):
            self.rest_pass[c] += int((sel & (seg == c)).sum())
        self.frames += 1
        self.stems.append(stem)

    def merge(self, other: "SetHist") -> None:
        for c in (ORANGE, BLUE):
            self.core[c] += other.core[c]; self.core_pass[c] += other.core_pass[c]; self.rest_pass[c] += other.rest_pass[c]
        self.rest += other.rest; self.frames += other.frames; self.stems += other.stems

    # ---- reading

    def window(self, c: int) -> np.ndarray:
        """Boolean [NH]: the rolled hues counted as this class's body color."""
        if self.exact_body:
            return np.ones(NH, bool)
        marg = self.core[c][:, :, self.vb:].sum((1, 2)).astype(float)
        if marg.sum() == 0:
            return np.zeros(NH, bool)
        sm = sum(np.roll(marg, k) for k in range(-2, 3))
        peak = int(np.argmax(sm))
        d = np.abs((np.arange(NH) - peak + 90) % 180 - 90)
        return d <= PEAK_HALF

    def body(self, c: int, passed: bool = False) -> np.ndarray:
        """[NH, NS, NV] of the body pixels bright enough for the model (others zeroed)."""
        a = (self.core_pass if passed else self.core)[c].copy()
        a[~self.window(c)] = 0
        a[:, :, :self.vb] = 0
        return a

    def rest_gated(self) -> np.ndarray:
        a = self.rest.copy()
        a[:, :, :self.vb] = 0
        return a

    def stats(self, c: int) -> dict:
        """Where this class's body color sits, and how much of it the fixed model catches."""
        b = self.body(c)
        n = int(b.sum())
        hm, sm = b.sum((1, 2)), b.sum((0, 2))
        w = self.window(c)
        peak = int(np.argmax(np.where(w, hm, -1))) if n else 0
        order = (np.arange(NH) + peak - 90) % NH                     # centre the peak so percentiles never straddle the wrap
        hq = [float(unroll(peak)) + (q - 90) for q in wpct(hm[order], np.arange(NH, dtype=float), (5, 50, 95))]
        sq = wpct(sm, np.arange(NS) * 2.0 + 1, (5, 50, 95))
        tot = int(self.core[c].sum())
        return {"n": n, "bright": (self.core[c][:, :, self.vb:].sum() / tot) if tot else float("nan"),
                "h5": hq[0], "h50": hq[1], "h95": hq[2],
                "s5": sq[0], "s50": sq[1], "s95": sq[2],
                "pass": (self.body(c, passed=True).sum() / n) if n else float("nan")}

    def rest_stats(self) -> dict:
        r = self.rest_gated()
        tot = int(self.rest.sum())
        hq = wpct(r.sum((1, 2)), np.arange(NH, dtype=float), (5, 50, 95))
        sq = wpct(r.sum((0, 2)), np.arange(NS) * 2.0 + 1, (5, 50, 95))
        vm = self.rest.sum((0, 1)) + self.core[ORANGE].sum((0, 1)) + self.core[BLUE].sum((0, 1))
        return {"n": tot, "bright": (r.sum() / tot) if tot else float("nan"),
                "h5": float(unroll(hq[0])), "h50": float(unroll(hq[1])), "h95": float(unroll(hq[2])),
                "s5": sq[0], "s50": sq[1], "s95": sq[2],
                "flood_orange": self.rest_pass[ORANGE] / tot if tot else float("nan"),
                "flood_blue": self.rest_pass[BLUE] / tot if tot else float("nan"),
                "mean_v": float((vm * (np.arange(NV) * 8 + 4)).sum() / max(1, vm.sum()))}

    def refit(self, c: int, s_pct: float, h_pct=(5, 95), margin: float = 2) -> dict:
        """The thresholds the hs model's own recipe (``pipeline.fit_hs``) would give on this set's body pixels:
        S floor = the ``s_pct`` percentile of S, hue sector = the ``h_pct`` percentiles of hue above that floor,
        widened by ``margin``; and the share of the non-barrel pixels that box would paint."""
        b = self.body(c).sum(2)
        if b.sum() == 0:
            return {"h_lo": float("nan"), "h_hi": float("nan"), "s_lo": float("nan"), "flood": float("nan")}
        s_lo = wpct(b.sum(0), np.arange(NS) * 2.0, (s_pct,))[0]
        above = b[:, int(s_lo // 2):].sum(1)
        peak = int(np.argmax(above))
        order = (np.arange(NH) + peak - 90) % NH
        lo, hi = wpct(above[order], np.arange(NH, dtype=float), h_pct)
        lo, hi = lo - margin, hi + margin
        r = self.rest_gated().sum(2)[order][max(0, int(round(lo))):int(round(hi)) + 1, int(s_lo // 2):].sum()
        tot = self.rest.sum()
        mid = float(unroll(peak))
        return {"h_lo": mid + (lo - 90), "h_hi": mid + (hi - 90), "s_lo": float(s_lo),
                "flood": float(r / tot) if tot else float("nan")}


def best_bins(body: np.ndarray, rest: np.ndarray, flood: float = 0.01) -> np.ndarray:
    """Boolean array like ``body``: the bins a lookup would paint, taken in order of body/rest ratio until the
    painted rest pixels reach ``flood`` of all rest pixels (``rest.sum()``)."""
    b, r = body.ravel().astype(float), rest.ravel().astype(float)
    order = np.argsort(-(b / (r + 0.5)), kind="stable")
    order = order[b[order] > 0]
    ok = np.cumsum(r[order]) <= flood * r.sum()
    pick = np.zeros(b.shape, bool)
    pick[order[ok]] = True
    return pick.reshape(body.shape)


def recall_at_flood(body: np.ndarray, rest: np.ndarray, flood: float = 0.01) -> float:
    """Share of the body pixels inside ``best_bins``. In-sample: an upper bound for a lookup with these bins."""
    if body.sum() == 0:
        return float("nan")
    return float(body[best_bins(body, rest, flood)].sum() / body.sum())


# ---------------------------------------------------------------- pictures (matplotlib, imported lazily)

def bin_colors(h_bins: int, s_bins: int, value: int = 230) -> np.ndarray:
    """RGB float [s_bins, h_bins, 3]: the color each (rolled hue, S) bin stands for, at a fixed brightness."""
    hc = ((np.arange(h_bins) + 0.5) * 180 / h_bins - ROLL) % 180
    sc = (np.arange(s_bins) + 0.5) * 256 / s_bins
    hsv = np.zeros((s_bins, h_bins, 3), np.uint8)
    hsv[..., 0] = hc[None, :]; hsv[..., 1] = np.clip(sc[:, None], 0, 255); hsv[..., 2] = value
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB).astype(float) / 255


def _level(counts: np.ndarray) -> np.ndarray:
    """0-1 per bin, logarithmic, [s_bins, h_bins] (S upward)."""
    lv = np.log1p(counts.T.astype(float))
    return lv / lv.max() if lv.max() > 0 else lv


def color_image(counts: np.ndarray) -> np.ndarray:
    """The 'color of the bin' picture: each bin in its own color, faded to dark where it holds few pixels."""
    lv = _level(counts)[..., None]
    bg = 0.10
    return bg + (bin_colors(counts.shape[0], counts.shape[1]) - bg) * lv ** 0.6


def model_rects(model: pl.Model) -> dict:
    """{class: (rolled hue lo, hue hi, S lo)} of the fixed hs model."""
    out = {}
    for c in (ORANGE, BLUE):
        b = model.boxes[c]
        sh = ROLL - pl.HUE_SHIFT[c]
        out[c] = (b.lo[0] + sh, b.hi[0] + sh, b.lo[1])
    return out


def _axes(ax, rects=None, title=""):
    from matplotlib.patches import Rectangle
    ax.set_xticks([0, 30, 60, 90, 120, 150, 180]); ax.set_xticklabels(["150", "0", "30", "60", "90", "120", "150"], fontsize=7)
    ax.set_yticks([0, 64, 128, 192, 256]); ax.tick_params(labelsize=7)
    ax.set_title(title, fontsize=8)
    for c, (lo, hi, slo) in (rects or {}).items():
        ax.add_patch(Rectangle((lo, slo), hi - lo + 1, 256 - slo, fill=False, ec="white", lw=0.9, ls="--"))


def figure_set(sh: SetHist, model: pl.Model, path, bins=(16, 16)) -> None:
    """Two rows x four panels for one set: all pixels, orange body, blue body, the rest; top row = counts in
    gray (log), bottom row = each bin in its own color. Dashed boxes = what the fixed model accepts."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ob, bb, r = sh.body(ORANGE), sh.body(BLUE), sh.rest_gated()
    allpx = (sh.core[ORANGE] + sh.core[BLUE] + sh.rest).copy(); allpx[:, :, :sh.vb] = 0
    panels = [("all pixels", allpx), ("orange barrel bodies", ob), ("blue barrel bodies", bb), ("everything that is not a barrel", r)]
    rects = model_rects(model)
    fig, axs = plt.subplots(2, 4, figsize=(15, 6.4))
    for k, (title, a) in enumerate(panels):
        cnt = rebin(a, *bins)
        axs[0, k].imshow(_level(cnt), cmap="gray", origin="lower", extent=(0, 180, 0, 256), aspect="auto", interpolation="nearest")
        _axes(axs[0, k], rects, f"{title}: {int(a.sum()):,} px (count, log)")
        axs[1, k].imshow(color_image(cnt), origin="lower", extent=(0, 180, 0, 256), aspect="auto", interpolation="nearest")
        _axes(axs[1, k], rects, "the same, each bin in its color")
        axs[1, k].set_xlabel("hue (OpenCV 0-179)", fontsize=7)
    axs[0, 0].set_ylabel("saturation", fontsize=7); axs[1, 0].set_ylabel("saturation", fontsize=7)
    fig.suptitle(f"{sh.name}: {sh.frames} frames, {bins[0]} x {bins[1]} bins, pixels below row {model.cfg.horizon_row} with V >= {sh.v_min}", fontsize=10)
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)


def figure_bars(sh: SetHist, path, bins=(16, 16)) -> None:
    """The 3-D bar plot: all pixels, one bar per bin in the bin's own color, height = log10(1 + count)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    allpx = (sh.core[ORANGE] + sh.core[BLUE] + sh.rest).copy(); allpx[:, :, :sh.vb] = 0
    cnt = rebin(allpx, *bins)
    col = bin_colors(*bins)
    hw, sw = 180 / bins[0], 256 / bins[1]
    xs, ys, zs, cs = [], [], [], []
    for i in range(bins[0]):
        for j in range(bins[1]):
            if cnt[i, j] > 0:
                xs.append(i * hw); ys.append(j * sw); zs.append(np.log10(1 + cnt[i, j])); cs.append(col[j, i])
    fig = plt.figure(figsize=(8.5, 6.5))
    ax = fig.add_subplot(projection="3d")
    ax.bar3d(xs, ys, np.zeros(len(xs)), hw * 0.9, sw * 0.9, zs, color=cs, shade=True)
    ax.set_xticks([0, 30, 60, 90, 120, 150]); ax.set_xticklabels(["150", "0", "30", "60", "90", "120"])
    ax.set_xlabel("hue"); ax.set_ylabel("saturation"); ax.set_zlabel("log10(1 + pixels)")
    ax.view_init(elev=38, azim=-62)
    ax.set_title(f"{sh.name}: all pixels, {bins[0]} x {bins[1]} bins", fontsize=10)
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)
