"""Contact sheets of the two passes: photo with hand boxes and seeds | first-pass mask and boxes | second-pass mask
and the combined boxes. Train frames only.

    python barrels/experiments/2026-11-26_selfcal/look.py OUT.png SETTING STEM [STEM ...]
"""
import sys

import cv2

import common as cm
import sheets as sh
from barrels import judge as jg
from barrels import selfcal as sc

SEED_COL = {"found": (255, 255, 255), "body": (0, 255, 255), "stripe": (255, 0, 255)}


def two_pass_row(stem: str, cfg: sc.SelfCalConfig, cal: sc.SelfCal | None = None, note: str = ""):
    frame = jg.load_frame(stem)
    r = (cal or sc.SelfCal(cm.MODEL, cfg, cm.CAM)).run(frame)
    photo = sh.draw_boxes(frame.bgr.copy(), sh.gt_of(stem), 1, (255, 255, 255), dashed=True)
    for s in r.seeds:
        if s.why == "duplicate":
            continue
        x0, y0, x1, y1 = s.bbox
        col = SEED_COL[s.kind] if s.ok else (0, 0, 255)
        cv2.rectangle(photo, (x0, y0), (x1 - 1, y1 - 1), col, 1)
        if not s.ok:
            cv2.putText(photo, s.why[:14], (x0, max(22, y0 - 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.3, col, 1, cv2.LINE_AA)
    p1 = sh.draw_boxes(sh.mask_picture(r.mask1, frame.bgr), r.first, 2)
    p2 = sh.draw_boxes(sh.mask_picture(r.mask2, frame.bgr), r.boxes, 2)
    moved = ",".join(f"{k} {v.get('h_lo', 0):.0f}..{v.get('h_hi', 0):.0f} S>={v.get('s_lo', 0):.0f}" for k, v in r.info.get("ranges", {}).items()
                     if v.get("moved") and k in r.info.get("moved", []))
    return sh.row(stem.replace("4A8B_", ""), [(f"photo; hand boxes dashed; seeds: white found, yellow body, magenta stripe, red refused {note}", photo),
                                             ("first pass (fixed colors)", p1), (f"second pass + combined boxes  {moved}", p2)]), r


def main(argv) -> int:
    import explore2
    out, setting, stems = argv[0], argv[1], argv[2:]
    cfg = explore2.SETTINGS[setting]
    rows = []
    for s in stems:
        row, r = two_pass_row(s, cfg)
        rows.append(row)
        print(s, [(x.kind, sc.NAME[x.body], x.bbox, x.why, round(x.rel, 2), x.like) for x in r.seeds], r.info)
    print(sh.save_sheet(out, rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
