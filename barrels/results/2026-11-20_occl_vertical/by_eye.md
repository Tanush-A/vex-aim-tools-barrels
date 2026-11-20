# By eye: boxes that appear or disappear on the unlabeled recordings (round 2; round 1 was the same)

337 frames (campus r1 to r4, the black-table clip, the wood clip), adopted color model, `base` draws 506 boxes.
Sheets: `sheets/rec_<arm>/` (ignored by git), made by `experiments/2026-11-20_occl_vertical/recordings.py`; the list of
boxes is `recordings.csv`, the counts `recordings.md`. Looked at 2026-11-19: the one sheet of `all` (the same single
frame as `behind`); in round 1 the sheet of `behind`.

## Campus clips (these decide, PREREG rule 4)

| arm | appear | disappear | verdict |
|---|---|---|---|
| `half`, `half+thin`, `post`, `wide`, `caplow` | 0 | 0 | **pass.** No frame of any clip changes. Nothing is drawn on the hand over the barrel in r4. |
| `behind`, `all` | 1 | 0 | **pass.** `r3_enter_leave` frame 013: the orange barrel entering at the right frame edge, box (619, 142, 640, 215), on the barrel (its stripe piece is 0.15 of a barrel wide at the frame edge, seen from top to bottom). |

## Black-table clip and wood clip (described, not judged)

No arm changes any frame of either clip: no box appears, none disappears.

## Still frames that are report only

- Dave's frames (indicative: his boxes group touching barrels): `caplow` and `all` draw one more box, orange (396, 168,
  520, 258) on `office_speckle_snap_02`. It lies on the two orange barrels standing together there (looked at:
  `sheets/dave_caplow.png`); against the grouped hand-drawn box it counts as a false box (3 → 4).
- Wood (parked as extreme): in round 1 `half` drew one orange box each on `lampcool3_wood_core_01` and
  `lampcool6_wood_cluster_01`, on a BLUE barrel whose lower body is not painted by the color model (looked at:
  `sheets/wood_half.png`): the wrong color. Round 2's "the stripe is the thinner band" removes the first. The second
  stays, (220, 115, 268, 163): what is painted of the blue upper body there is 12 rows, thinner than the orange stripe
  under it (15 rows), so the picture reads as an orange barrel hidden from above. It is the one box `half`, `half+thin`
  and `all` add on the 90 wood train frames (`levels/never_regress.md`: `lampcool6_wood`, cluster, false 0 → 1).
