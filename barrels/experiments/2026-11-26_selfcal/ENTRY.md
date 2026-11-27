## 2026-11-26 — The barrel as its own color reference (TODO E6, first idea; pre-registered, one round; branch `wip/exp-selfcal`; nothing adopted)

- **Hypothesis:** The fixed colors fail when the light or the table changes. Whole-frame statistics cannot say what the
  right colors are, because barrels are 4 % of the pixels. A barrel that is found, or half found, can: its place is
  known, so its two colors can be read from the photo there. Of 63 clean missed barrels, 49 have one color at full
  strength (review, detector audit 3.3). Per frame, nothing carried between frames, no pixel changed.
- **Method / params:** `src/barrels/selfcal.py` (new; nothing that runs by default calls it; 27 unit tests).
  `experiments/2026-11-26_selfcal/`: `PREREG.md` (committed before any judged run), `candidates.py`, `run.py`.
  - Pass 1 is today's detector. Then seeds: a found box; a strict body color with a stripe-sized gap (`body`); a
    strict stripe-sized band with no body (`stripe`).
  - The guard: three bands (upper body, stripe, lower body) are read from the photo. Kept only if both body bands
    differ from the stripe band in log(R/B) by a margin with the right sign, and a part that was read does not look
    like what is around the box.
  - A kept seed paints its own missing color inside its own box (`local`), and its two readings widen the frame's
    ranges (`frame`), bounded: only wider, a hue end at most 6 or 10, saturation floor never under 60, readings must
    agree, a flood limit.
  - Pass 2: the same detector on the new mask. Every first-pass box stays; second-pass boxes fill in.
  - Three numbers are chosen leave one place out (`rel_margin`, `hue_move_max`, `flood_max`). The rest was fixed
    before the judged runs, but shaped while looking at all eight places (the list is in `PREREG.md`).
- **Data / split:** Train frames only. Judged on the 154 ordinary frames (17 conditions, 8 places, 172 placements,
  307 barrels counted per frame), by the standard pass rule, leave one place out. Extreme conditions report only. No
  test frame opened.
- **Results** (`results/2026-11-26_selfcal/summary.md`; every candidate, also the one that lost):

  | candidate | verdict | found, placements | found, per frame | boxes not on their barrel | boxes on empty frames | places that moved |
  |---|---|---|---|---|---|---|
  | fixed colors (baseline) | | 133.8 | 211 | 1.9 | 0 | |
  | `A_found`: found boxes set the frame's ranges | PASS (+7.2) | 141.0 | 223 | 2.1 | 0 | gray +5.0, ottoman +2.0, bathroom +0.2 |
  | `B_local`: a half-found barrel completes itself | PASS (+12.2) | 146.0 | 243 | 2.2 | 0 | gray +5.0, bathroom +5.5, ottoman +1.7 |
  | `B_frame`: half-found barrels set the frame's ranges | PASS (+9.3) | 143.1 | 230 | 1.9 | 0 | gray +5.0, ottoman +3.0, bathroom +1.2 |
  | **`AB`: all of it (the main candidate)** | **PASS (+13.8)** | **147.6** | **248** | 2.2 | 0 | gray +5.0, bathroom +5.8, ottoman +3.0 |
  | `AB_noguard`: the same with every guard off | FAIL | 152.6 | 261 | 29.2 | 7 (cluttered) | ottoman +7.0, gray +5.0, bathroom +5.8, ABP white +1.0 |

  - No candidate lost a barrel. The gain margin is +4.0; none of the four passes is weak (all above +6.0).
  - `AB` by condition, per frame of 15: bathroom mid 3: 1 → 10, mid 6: 1 → 9, warm: 1 → 6, cool: 13 → 14. Ottoman
    cool: 3 → 11, mid 6: 6 → 7, warm: 0 → 0. Gray table: 10 → 15 of 16. Five places do not move.
  - The one new box of `AB` that is not on its barrel: a second orange box on an orange barrel
    (`lampmid3_bathtile_core_01`). No kept seed on any empty frame. No kept seed off a hand box.
  - The folds agree: every fold picked `rel_margin` 1.0 and, for `AB`, `hue_move_max` 6; `flood_max` 0.03 in 9 of 10,
    0.01 when the ottoman was held out (which cost it 4 barrels there: `A_found` gets 11 on ottoman mid 6, `AB` 7).
  - A usable seed exists in 87 of the 132 ordinary frames with barrels. A sure found box alone exists in 65, and in
    none on the bathroom floor under the mid and warm lamp or on the ottoman under the cool and warm lamp. Warm
    ottoman: no seed of any kind in 6 frames.
  - Painted pixels outside the hand boxes, ordinary frames: 634 216 → 664 143 (+4.7 %).
  - Extreme conditions, report only: wood under the lamp 7 → 51 of 126, black table 5 → 8 of 26, dark ottoman 1 → 1.
  - Report only, colors carried across the frames of one condition: 147.6 → 150.4 placements (248 → 253), boxes not on
    their barrel 2.2 → 3.8. Black table 8 → 16 of 26.
  - What it gains (37 barrels, counted per frame): 32 through a kept seed of their own (15 had the body painted and
    no stripe, 15 the stripe and no body, 2 other); 5 had no kept seed and were found through the frame's ranges.
  - What it still misses (59 per frame; `results/2026-11-26_selfcal/misses.md`): 31 are hidden or cut. The 28 that
    are not: warm ottoman 10 (all 15 barrels there stay missed), warm bathroom 7, bathroom mid 6: 4, mid 3: 3,
    ottoman mid 6: 3, cool: 1. By what happened to their seed: 15 refused by a guard, 9 had no seed candidate, 4 had
    a kept seed and the detector still drew no good box.
    - Warm ottoman: neither color is painted at full strength, and the blue body reads like the dark fabric, so
      the surround guard refuses it. With the guards off these frames get boxes of the wrong color.
    - Two blue barrels touching under the bathroom lamp (4 of the 9): their orange stripes run into one band two
      barrels wide. That is not a one-barrel band, so there is no seed.
- **Takeaway:** It works, per frame, with no new box on an empty frame. Most of the gain is the plainest part: a
  barrel with one strict color finishes itself (+12.2). Sharing the colors with the rest of the frame adds little on
  top (+1.6), because under the warm lamp the blue is not a color any more (saturation under 60) and cannot be a
  range. The guards are what make it usable: off, it finds 5 more placements and draws 27 more boxes on things that
  are not barrels. Caution: the method was shaped on all eight places and only three numbers are held out, so the
  verdict is optimistic by an unknown amount. A new place, or the test frames, is the clean check.
- **Next:** (1) Walk Tanush through it; it touches the color step, so it is main code if adopted. (2) Judge it on a
  place it has never seen (the next shoot). (3) Cut a band wider than a barrel into barrel widths (the two touching
  blue barrels). (4) The warm ottoman needs something else: no strict color is there to start from; the relative
  test without a strict seed (TODO C4) is the candidate. (5) Read the ottoman's size, not only its colors: barrels
  there are 0.6 to 0.7 of the size their row predicts.
