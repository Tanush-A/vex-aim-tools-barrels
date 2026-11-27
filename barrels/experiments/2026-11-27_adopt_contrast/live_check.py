#!/usr/bin/env python3
"""The live programs with the new default, without a robot (2026-11-27).

    python barrels/experiments/2026-11-27_adopt_contrast/live_check.py

Imports ``live/barrel_live.py``, ``live/BarrelViewer.py`` and ``live/BarrelTracker.py`` (and so aim_fsm), then does on
saved TRAIN frames exactly what their ``ShowFrame`` states do with a camera image: the viewer's
``hook.view(image, mode)`` + ``hook.last_barrels``, and the tracker's ``hook.on_image`` -> ``tracker.update`` ->
``hook.render(..., raw=...)``, for each mode. ``imshow`` is not called (no display). Checks that the hook's answer is
``pipeline.detect_frame``'s, box for box, and prints the time per frame. Writes
results/2026-11-27_adopt_contrast/live_check.md. Exit 0 = all held.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

BARRELS = Path(__file__).resolve().parents[2]
REPO = BARRELS.parent
sys.path[:0] = [str(BARRELS / "src"), str(REPO), str(BARRELS / "live")]
import numpy as np  # noqa: E402

from barrels import conditions as cnd  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels import pipeline as pl  # noqa: E402
from barrels import tracker as tk  # noqa: E402

OUT = BARRELS / "results" / "2026-11-27_adopt_contrast"
# train frames: an ordinary bathroom frame under the mid lamp (the contrast stage adds there), campus, and an empty frame
STEMS = ("4A8B_lampmid6_bathtile_core_01", "4A8B_campus_light_core_01", "4A8B_lampmid6_bathtile_neg_02")


def main() -> int:
    lines = ["# The live programs with the new default, on saved train frames (no robot)", "",
             "Made by `experiments/2026-11-27_adopt_contrast/live_check.py`.", ""]
    t0 = time.perf_counter()
    import barrel_live          # noqa: F401  (imports aim_fsm)
    import BarrelTracker        # noqa: F401
    import BarrelViewer         # noqa: F401
    lines.append(f"- imported `barrel_live`, `BarrelViewer`, `BarrelTracker` (aim_fsm included) in {time.perf_counter() - t0:.1f} s")
    hook = barrel_live.wb.BarrelDetectorHook.default()
    train = set(sum(jg.train_frames().values(), []))
    ok = True
    for stem in STEMS:
        if stem not in train:
            lines.append(f"- {stem}: not a train frame, skipped"); ok = False
            continue
        frame = jg.load_frame(stem)
        image = np.ascontiguousarray(frame.bgr[..., ::-1])          # what robot.camera_image gives: RGB
        want = [(b.color, b.bbox, b.source) for b in pl.detect_frame(frame)]
        times = []
        for mode in ("boxes", "seg", "both"):
            t = time.perf_counter()
            pic = hook.view(image, mode)                               # BarrelViewer.ShowFrame
            times.append(time.perf_counter() - t)
            got = [(b.color, b.bbox, b.source) for b in hook.last_barrels]
            ok &= got == want and pic.shape == image.shape and pic.dtype == np.uint8
            ok &= (hook.seg_only() is not None)
        tr = tk.Tracker()
        for _ in range(4):                                             # BarrelTracker.ShowFrame, four frames in a row
            raw = hook.on_image(image)
            shown = tr.update(raw)
            pic = hook.render(image, shown, "both", raw=raw)
        ok &= [(b.color, b.bbox) for b in raw] == [(c, bb) for c, bb, _ in want] and len(shown) == len(raw)
        added = sum(1 for w in want if w[2] == "contrast")
        lines.append(f"- {stem}: {len(want)} boxes ({added} added by the contrast stage); viewer = detect_frame box for box: "
                     f"{'yes' if [(b.color, b.bbox, b.source) for b in hook.last_barrels] == want else 'NO'}; tracker shows {len(shown)} after 4 frames; "
                     f"view {1000 * min(times):.0f} to {1000 * max(times):.0f} ms")
    lines += ["", f"RESULT: {'the live code runs the new default' if ok else 'NOT AS EXPECTED'}", ""]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "live_check.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
