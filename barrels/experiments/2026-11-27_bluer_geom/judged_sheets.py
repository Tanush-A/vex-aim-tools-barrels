#!/usr/bin/env python3
"""Contact sheets of what each judged candidate changed against today's default (or against its own color step with
``--own``): every barrel gained, every barrel lost, and the boxes not on their barrel on every frame where they rose.
Each panel: the photo crop (hand boxes white, the item magenta) and the mask of the member the fold picked for that
place (G3: the fixed mask; the contrast paint is not shown). Train frames only. Images are not committed.

    python judged_sheets.py G1_b4_checks [G2_fixed_checks ...] [--own]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bg  # noqa: E402
from bg import ru  # noqa: E402
import bgsheets as sh  # noqa: E402

from barrels import counting as ct  # noqa: E402
from barrels import io  # noqa: E402
from barrels import judge as jg  # noqa: E402
from barrels.io import BLUE, ORANGE  # noqa: E402


def setting_of(key: str | None):
    if not key:
        return ru.FIXED
    r, w0, w1, s, h, d, o, x0, x1, hi, g = key.split("#")[0].split("|")
    return ru.Setting(r, float(w0), float(w1), float(s), float(h), float(d), o, float(x0), float(x1), float(hi), float(g))


def panel(stem, box, st, note, color):
    frame = jg.load_frame(stem)
    img = frame.bgr.copy()
    for g in io.load_boxes(stem, check_image=False).get("barrels", []):
        a, b, c, d = (int(v) for v in g["bbox"])
        cv2.rectangle(img, (a, b), (c - 1, d - 1), (255, 255, 255), 1)
    x0, y0, x1, y1 = box
    cv2.rectangle(img, (x0, y0), (x1 - 1, y1 - 1), (255, 0, 255), 1)
    m = ru.segment(frame, st)
    mi = (frame.bgr.astype(np.float32) * 0.35).astype(np.uint8)
    for c_, col in sh.PAINT.items():
        mi[m == c_] = col
    cv2.rectangle(mi, (x0, y0), (x1 - 1, y1 - 1), (255, 0, 255), 1)
    row = np.hstack([sh.crop(img, *box), sh.crop(mi, *box)])
    lab = np.zeros((28, row.shape[1], 3), np.uint8)
    cv2.putText(lab, stem.replace("4A8B_", "")[:44], (2, 11), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (255, 255, 255), 1)
    cv2.putText(lab, f"{color} {note}"[:50], (2, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (200, 255, 200), 1)
    return np.vstack([lab, row])


def main() -> int:
    own = "--own" in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    chosen = json.loads((bg.OUT / "chosen.json").read_text()) if (bg.OUT / "chosen.json").exists() else {"folds": {}}
    for n in names:
        folds = chosen["folds"].get(n, {})
        d = json.loads((bg.OUT / (f"vs_own_{n}" if own else f"judge_{n}") / "judge.json").read_text())
        tag = n + ("_own" if own else "")
        for kind in ("gained", "lost"):
            ps = [panel(c["stem"], tuple(c["bbox"]), setting_of(folds.get(ct.place_of(c["stem"]), {}).get("key")), f"{kind} {c['before']}->{c['after']}", c["color"])
                  for c in d["changes"] if c["kind"] == kind and c["judged"]]
            if ps:
                sh.save(ps, f"{tag}_{kind}")
        ps = []
        for b in d["box_changes"]:
            if sum(b["after"].values()) > sum(b["before"].values()):
                st = setting_of(folds.get(ct.place_of(b["stem"]), {}).get("key"))
                ps += [panel(b["stem"], tuple(box), st, "not on barrel" + (" (empty)" if b["empty"] else ""), col) for col, box in b["boxes_after"]]
        if ps:
            sh.save(ps, f"{tag}_newbox")
    return 0


if __name__ == "__main__":
    sys.exit(main())
