"""The color of the light, and the blue threshold that follows it (2026-11-25; behind a switch, off by default:
``pipeline.Config.hs_light``; plan and test: ``experiments/2026-11-25_color/PREREG.md``).

Why. Under a warm (yellow) lamp the blue paint of a barrel loses its saturation: on the bathroom floor at the lamp's
middle setting the blue body reads S about 50-80 against the adopted floor of 113, so the blue is not painted and the
orange barrels lose their stripe. Under daylight the opposite holds: gray walls and white tables read slightly blue,
which is why the floor had to be 113 at home. So the floor that is right depends on the color of the light.

The idea, in one line (Tanush's picture: "if the whole image is more yellow, shift the thresholds that way"): read how
yellow the LIGHT is from the frame itself, and lower the blue saturation floor (and the low end of the blue hue
range) the more yellow it is.

1. ``light_warmth(frame)``: the brightest 5 % of the frame's pixels (by V, the brightest channel) are mostly white or
   pale surfaces and highlights, which take the light's own color (the "white patch" idea). Their median
   (R - B) / (R + G + B) is the light's warmth: about 0 under daylight or white ceiling light, about 0.25 under the
   lamp's middle setting, 0.4 under its warm setting. A warm-colored TABLE under neutral light (the pale wood) does
   not count, because its brightest pixels are still near white.
2. ``warm_blue_boxes``: with ``(w0, w1, s_warm, h_warm)``, the share t = (warmth - w0) / (w1 - w0), clipped to 0..1;
   the blue box's S floor moves from the model's value toward ``s_warm`` and its hue low end from the model's value
   toward ``h_warm`` by that share. At warmth <= w0 nothing changes (the adopted model); the rule only ever LOWERS the
   two numbers, never raises them, and never touches orange.

What is never done: a pixel is never changed (no white balance; the warmth only moves the blue box), and nothing is
carried from one frame to the next.
"""
from __future__ import annotations

import numpy as np

from . import boxfit as bf
from .io import BLUE

TOP_SHARE = 5.0         # percent of the frame's pixels (the brightest) the light's color is read from


def light_warmth(rgb: np.ndarray, top: float = TOP_SHARE) -> float:
    """The light's warmth from one frame (``rgb``: H x W x 3 in R, G, B order, any int or float type): the median of
    (R - B) / (R + G + B + 1) over the brightest ``top`` % of the pixels (by the brightest channel; ties at the
    threshold included). 0 for a neutral light, positive for a yellow one, negative for a blue one."""
    x = np.asarray(rgb).reshape(-1, 3).astype(np.float32)
    if len(x) == 0:
        return 0.0
    v = x.max(1)
    sel = v >= np.percentile(v, 100.0 - top)
    y = x[sel]
    return float(np.median((y[:, 0] - y[:, 2]) / (y.sum(1) + 1.0)))


def share(warmth: float, w0: float, w1: float) -> float:
    """0 at warmth <= w0, 1 at warmth >= w1, a straight line between."""
    if w1 <= w0:
        raise ValueError(f"w1 must be above w0, got w0={w0}, w1={w1}")
    return float(np.clip((warmth - w0) / (w1 - w0), 0.0, 1.0))


def validate(params) -> tuple[float, float, float, float]:
    """``(w0, w1, s_warm, h_warm)`` as floats; ValueError when it is not four finite numbers with w0 < w1."""
    try:
        w0, w1, s_warm, h_warm = (float(x) for x in params)
    except (TypeError, ValueError):
        raise ValueError(f"hs_light must be (w0, w1, s_warm, h_warm), got {params!r}") from None
    if not all(np.isfinite([w0, w1, s_warm, h_warm])) or w1 <= w0:
        raise ValueError(f"hs_light needs finite numbers with w0 < w1, got {params!r}")
    if not (0 <= s_warm <= 255 and 0 <= h_warm <= 179):
        raise ValueError(f"hs_light: s_warm must be 0-255 and h_warm 0-179, got {params!r}")
    return w0, w1, s_warm, h_warm


def warm_blue_boxes(rgb: np.ndarray, boxes: dict, params) -> tuple[dict, dict]:
    """(boxes with the blue box moved for this frame's light, info). Only the blue box's lower corner moves: its S floor
    toward ``s_warm`` and its hue low end toward ``h_warm`` by ``share(light_warmth)``; a value already below its target
    is left as it is. The other boxes are returned untouched."""
    w0, w1, s_warm, h_warm = validate(params)
    w = light_warmth(rgb)
    t = share(w, w0, w1)
    out = dict(boxes)
    b = boxes[BLUE]
    h_lo, s_lo = float(b.lo[0]), float(b.lo[1])
    new_h = h_lo - t * max(0.0, h_lo - h_warm)
    new_s = s_lo - t * max(0.0, s_lo - s_warm)
    out[BLUE] = bf.Box((new_h, new_s) + tuple(b.lo[2:]), tuple(b.hi))
    return out, {"warmth": w, "share": t, "blue_h_lo": new_h, "blue_s_lo": new_s}
