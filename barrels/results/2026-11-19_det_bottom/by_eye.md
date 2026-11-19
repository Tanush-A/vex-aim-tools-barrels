# By eye: boxes that appear or disappear on the unlabeled recordings (PREREG rule (c))

337 frames (campus r1 to r4, the black-table clip, the wood clip), adopted color model. `base` (the defaults of
`wip/detector-side`) draws 506 boxes. Made by `experiments/2026-11-19_det_bottom/recordings.py`; the list of
boxes is `recordings.csv` (empty), the counts `recordings.md`.

| arm | boxes | appear | disappear | verdict |
|---|---|---|---|---|
| `bottom` (`cap_seen_bottom` on) | 506 | 0 | 0 | **passes.** No frame of any clip changes, so there is no contact sheet to look at: nothing appears, nothing disappears, on the campus clips, the black clip or the wood clip. |

What this says: in 337 frames of video there is no narrow cap whose seen end is refused by the top-row estimate.
The rule acts on one barrel of the labeled frames (HOME `cluster_01`) and on none of the recordings.
