# By eye: the recordings and the scorecard sheets (2026-11-19)

Sheets: `sheets/` and `round1/sheets/` (ignored by git), made by `recordings.py`, `run.py` and `diag.py` of
`experiments/2026-11-20_occl_pin`. 337 recorded frames (campus r1 to r4, the black-table clip, the wood clip),
adopted color model; `base` draws 506 boxes.

## Recordings, round 2 (these decide, PREREG clause 2)

| arm | appear | disappear | verdict |
|---|---|---|---|
| `pin` | 0 | 0 | **pass.** No frame of any clip changes. |
| `pin+thin` | 0 | 0 | **pass.** No frame of any clip changes. |

Nothing to judge: on the recordings no partly seen stripe without a side reason has an end that follows the
barrel's outline to 0.05 of its height. The hand clip (`r4_hand_occlusion`) is unchanged too.

## Recordings, round 1 (the sliding outline; not adopted)

`pin`: no frame changes. `pin+thin`: two boxes appear, none disappears, both on a barrel:
- campus `r3_enter_leave` 013: the orange barrel entering at the right frame edge, box (615, 142, 640, 215), on the
  barrel.
- black clip 032 (report only): the blue barrel beside the hand, box (104, 147, 181, 218), tight on the barrel.

Round 2 draws neither: the own corner of each is more than 0.05 of the height off the outline (the thin census had
them at a cost of 0.034 and 0.037 for the sliding fit).

## Scorecard sheets, round 2 (`sheets/00_frame.png`, `01_edge.png`, `02_slant.png`; three example barrels)

- Straight edge, 25 and 50 % hidden: `base` draws a barrel-wide box centred on what is seen, a part of it over the
  empty side (HOME `core_02`: a quarter barrel off). `pin` draws the box from the barrel's own side: it lies on the
  hand-drawn box to a pixel or two in all three examples.
- Straight edge, 75 %: `base` and `pin` draw nothing; `pin+thin` draws the full box for one of the three examples
  (HOME hand mask), tight; nothing for the other two (ragged corner).
- Slanted edge: `pin` equals `base` in these three examples at 25 and 50 % (the boxes are already on the barrel);
  nothing is drawn at 75 % by any arm. The 16 scenes gained at 50 % are not among the examples.
- Frame edge: unchanged at 25 and 50 %; at 75 % `pin+thin` boxes one of the three, cut by the frame.

`diag.py` over all 3888 scenes, round 2: no scene where an arm loses the hidden barrel, loses a right-place box, or
draws one more box where no barrel is. Round 1 had 8 such scenes for `pin` and 11 for `pin+thin`
(`round1/sheets/diag_*.png`): boxes put on the wrong side of a barrel cut by a slanted edge.
