# Verdict: the stripeless close-up piece (A9), round 1

Pre-registration: `experiments/2026-11-23_closeup_shape/PREREG.md` (committed before the rules existed in code). One
round; no addendum. Both switches pass every clause and are **on by default on `wip/closeup-shape`**.

| clause | `side` (A) | `stripe` (B) | `shape` (A + B) | where |
|---|---|---|---|---|
| 1. box on `occlx_15` gone; no empty frame gets a box | gone; none | none added (start's fruit box stays: A's job) | gone; none | `round1/compare.md`, `round1/eval.md` |
| 2. `--gate --cand-det` | – | – | **PASS** (and PASS with the new defaults) | `report.py --gate` |
| 3. no real close-up / held / edge / top barrel lost | 31 → 31 of 61 | 31 → 32 | 31 → 32 (palewood `close_01` found) | `round1/compare.md` |
| 4. HOME 28 / 1 / 0, CAMPUS 35 / 0 / 0 | same | same | same | `round1/eval.md` |
| 5. scorecard: found / boxes where no barrel is | 2876 / 48 | 2876 / 48 | 2876 / 48 (all 3888 scenes identical to `start`) | `round1/scorecard.md` |
| 6. damage levels, false boxes | identical at every level, 5 and 20 seeds | identical | identical | `round1/levels.md` |
| 7. recordings (337 frames) | 0 boxes appear / disappear | 0 | 0 | `round1/rec_vs_start/` |

Every box that changes on any train frame of any set (`round1/compare.md`): `occlx_15` orange (465, 286, 640, 480)
removed (not a barrel); `overheaddim_palewood_close_01` orange (292, 241, 568, 477) added (finds the labeled barrel
(291, 243, 566, 480)). Nothing else.

**Recordings by eye.** No box appears or disappears, so there is no changed frame to judge. The close look
(`rec_asked.py`): neither rule is even asked on the 337 frames — there are 7 stripeless frame-bottom pieces in all, none
cut by the frame's side, and no piece whose predicted stripe straddles the frame bottom. The barrels entering at the frame
edge in `r2_pan` and `r3_enter_leave` are mid-range barrels (bottom in view) boxed from their stripe (`det2`), which these
rules never touch; `r4_hand_occlusion` has no frame-bottom piece the rules ask about.

What could not be verified: no real frame of a side-cut close-up barrel whose body is too dark to be seen down to its
stripe exists; such a barrel would now be missed (a miss, not a wrong box). Dave's three side-cut close-ups are the only
real side-cut ones, all seen to the frame bottom.
