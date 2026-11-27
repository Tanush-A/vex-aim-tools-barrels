"""After the judged runs: contact sheets of what the main candidate still misses, and of what the guards stop.

    python barrels/experiments/2026-11-26_selfcal/missed_sheets.py            # needs results/.../summary.json and misses.json

``AB_missed_NN.png``: the ordinary frames with the most barrels that are still not found and are not hidden, each with
its own place's held-out setting (photo with seeds, first pass, second pass). ``noguard_NN.png``: frames where the
guards-off run draws a box that is not on a barrel, drawn with the guards off (so the refused seeds show as kept).
Images are not committed. Train frames only.
"""
from __future__ import annotations

import collections
import dataclasses
import json
import sys

import candidates as cand
import common as cm
import look
import sheets as sh
from barrels import counting as ct


def main(argv) -> int:
    family = "AB"
    summary = json.loads((cm.RESULTS / "summary.json").read_text())
    chosen = {k.split("|")[1]: v["setting"] for k, v in summary["chosen"].items() if k.split("|")[0] == family}
    rows = json.loads((cm.RESULTS / "misses.json").read_text())
    n = collections.Counter(r["stem"] for r in rows if r["class"] == "ordinary" and r["after"] != "found" and not r["hidden"])
    stems = [s for s, _ in n.most_common(12)]
    out = []
    for i in range(0, len(stems), 6):
        sheet = []
        for s in stems[i:i + 6]:
            cfg = dataclasses.replace(cand.BASE[family], **chosen[ct.place_of(s)])
            notes = "; ".join(f"{r['color']} {r['after']}: {r['seed']}" for r in rows if r["stem"] == s and r["after"] != "found")
            sheet.append(look.two_pass_row(s, cfg, note="| " + notes)[0])
            print(s, notes)
        out.append(sh.save_sheet(cm.RESULTS / "sheets" / f"AB_missed_{i // 6 + 1:02d}.png", sheet, scale=0.75))
    j = json.loads((cm.RESULTS / "AB_noguard" / "judge.json").read_text())
    bad = [x["stem"] for x in j["box_changes"] if x["judged"]]
    pick = [s for s in bad if any(k in s for k in ("campus_light_hand_02", "abpgray_neg_02", "bathtile_neg_02", "glass_occl_02", "lampwarm6_bathtile_core_01",
                                                    "lampwarm6_ottoman_core_01", "lampmid6_ottoman_occl_02", "abpwhite_occlx_15", "lampmid3_bathtile_touch_01",
                                                    "palewood_occl_02", "window_glass_neg_02", "lampmid3_bathtile_close_01"))]
    for i in range(0, len(pick), 6):
        sheet = [look.two_pass_row(s, cand.NOGUARD, note="| GUARDS OFF")[0] for s in pick[i:i + 6]]
        out.append(sh.save_sheet(cm.RESULTS / "sheets" / f"noguard_{i // 6 + 1:02d}.png", sheet, scale=0.75))
    print("\n".join(str(p) for p in out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
