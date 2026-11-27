#!/usr/bin/env python3
"""Write the threshold PROPOSALS for the slider-labelled bathroom frames (TODO C1): one proposal file per frame in
data/labels, written by ``tools/hs_slider.py --save-proposal`` (the tool names the file). A proposal is not a label:
Tanush's ``_hs.json`` files are not touched, and nothing reads a proposal file back. This experiment's two
"relabelled" ceilings take the numbers from ``PROPOSALS`` below.

    PYTHONPATH=barrels/src python barrels/experiments/2026-11-26_place_ceiling/write_proposals.py

Where the numbers come from (``explore/bath_props.py``, looked at as pictures before this was written):

- a frame with free-standing barrels: its net setting, ``barrels.placecal.net_setting`` with outside weight 1: per
  color the hue range and saturation floor that paint the most barrel pixels (body rows of that color's barrels, stripe
  rows of the other color's) minus the pixels painted outside the boxes. Full hue range for blue (0 to 179). No
  detector is run to get them.
- ``occl_02`` (its one barrel is half hidden, so the frame gives no clean barrel pixels): the net setting of the
  condition's six frames with barrels pooled.
- one number was changed by hand after looking: ``lampwarm6 core_01`` blue hue high 174 -> 110 (see its reasoning).
"""
from __future__ import annotations

import sys
from pathlib import Path

BARRELS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BARRELS / "tools"))
import hs_slider as tool  # noqa: E402

OWN = ("Computed from this frame and its boxes with the full hue range (net setting, outside weight 1: the most barrel pixels painted minus the "
       "pixels painted outside the boxes). No detector was used to get the numbers. ")
POOLED = ("The only barrel of this frame is half hidden, so the frame gives no clean barrel pixels. These are the numbers of the condition's six "
          "frames with barrels pooled (net setting, outside weight 1). ")
PROPOSALS = {
    "4A8B_lampcool6_bathtile_core_01": ("o:6,15,198;b:89,110,121", OWN + "Blue sits at hue 98 to 105 here, at or below the fixed range's lower edge of 103."),
    "4A8B_lampcool6_bathtile_clutter_01": ("o:10,14,195;b:94,106,108", OWN + "Paints 57 px of blue and 76 px of orange outside the boxes."),
    "4A8B_lampcool6_bathtile_occl_02": ("o:9,14,207;b:89,106,120", POOLED),
    "4A8B_lampmid3_bathtile_core_01": ("o:7,14,202;b:46,140,9", OWN + "The blue paint is nearly gray here (S about 48), so its hue scatters; the floor is "
                                       "far more saturated, so a floor of 9 on S does not paint it."),
    "4A8B_lampmid3_bathtile_clutter_01": ("o:10,13,205;b:80,112,14", OWN),
    "4A8B_lampmid3_bathtile_occl_02": ("o:9,13,208;b:66,109,18", POOLED + "It paints little of the shaded visible half: check the orange S floor."),
    "4A8B_lampmid6_bathtile_core_01": ("o:7,14,204;b:66,125,9", OWN),
    "4A8B_lampmid6_bathtile_clutter_01": ("o:9,13,213;b:55,108,10", OWN),
    "4A8B_lampmid6_bathtile_occl_02": ("o:8,11,213;b:66,112,17", POOLED + "It paints little of the shaded visible half: check the orange S floor."),
    "4A8B_lampwarm6_bathtile_core_01": ("o:5,10,213;b:26,110,8", OWN + "Under the warm lamp the blue paint reads gray-olive: hue 25 to 57 for the middle half "
                                        "of its pixels, S about 42. The floor is hue 10 to 29 with S above 100, so blue from hue 26 up paints the "
                                        "barrels and not the floor (63 px outside). The computed blue range ran up to hue 174 because nothing else in "
                                        "this frame has those hues; I cut it to 110 by hand."),
    "4A8B_lampwarm6_bathtile_clutter_01": ("o:8,10,215;b:26,101,8", OWN + "Blue from hue 26: the barrels, not the floor (110 px outside, on the tin and the jar)."),
    "4A8B_lampwarm6_bathtile_occl_02": ("o:7,9,215;b:30,103,7", POOLED),
}


def main() -> int:
    for stem, (setting, why) in PROPOSALS.items():
        rc = tool.main(["--filter", stem, "--save-proposal", setting, "--reasoning", why])
        if rc != 0:
            return rc
    print(f"{len(PROPOSALS)} proposals written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
