## 2026-11-27 — A barrel hidden at the side by a thing that is not a barrel: the cut line in the photo. WEAK PASS, small

**Branch** `wip/exp-occl-photo`. **Scripts** `experiments/2026-11-27_occl_photo/` (`PREREG.md`, `candidate.py`, `judge_all.py`, `real.py`, `sim.py`, `sim_wrong.py`, `measure.py`). **Results** `results/2026-11-27_occl_photo/` (`judge_summary.md` first).

**Why.** A barrel half hidden by a box, a book or a charger gets a box only if one side has a reason to be hidden. A thing that is not a barrel is "other" in the mask, like bare table. So it is never a reason. Then the outline may place the barrel, else a centred guess, else nothing. The real frames `occlx_02`, `occlx_03`, `palewood_occl_02` and `ottoman_occl_02` had no box.

**Hypothesis.** A thing in front of a barrel has a straight, near-upright edge in the photo. That edge runs on past the barrel: above its top (the thing is taller) or below its bottom (the thing stands nearer, so its foot is lower). A barrel's own side stops at its lid and base. So the photo can say which end of the seen part is cut.

**The rule** (behind `DetConfig.side_photo`, default `off`; `detect(..., photo=None)` is today). It runs only for a partly seen stripe that no reason and no outline places. In a band of rows above the barrel (0.1 H to 0.5 H) and a band below, find the strongest left-right step in the photo near the seen end, row by row. Fit a straight line. An end is cut when, in either band:
1. most rows (`photo_frac` 0.6) lie on the line, and it leans at most 0.5 px per row;
2. the barrel's paint does not cross the line (in at most `photo_cross` 0.1 of the rows between that band and the stripe). An edge behind the barrel would be crossed by its bulge;
3. the line touches the seen part (within max(3 px, 0.15 W)).
Exactly one end cut: the box is W wide from the other end. `slack` lets the "does not cross" allowance grow 0.1 px per row away from the band (a real box edge curves a little). `cut+bulge` also needs the bulge rule of 2026-11-26_sidecut to agree.

**Not merged:** `wip/exp-contrast`. `barrels` already has contrast in its default. The baseline is today's default.

**Results.**
- Proof harness at defaults: IDENTICAL BOXES ON EVERY INPUT (5435 masks, against today's code; the stored `before.json` predates the seam reading). Tests 1004 pass (5 new).
- Standard judge, contrast in the baseline, margin +1.0:

| candidate | verdict | found (placements) | gained / lost | boxes not on their barrel |
|---|---|---|---|---|
| `cut` | PASS (weak) | 156.6 → 158.0 | 2 / 0 | 2.4 → 2.4 |
| `cut+bulge` | no clear difference | 156.6 → 157.6 | 1 / 0 | 2.4 → 2.4 |
| `slack` | PASS (weak) | 156.6 → 159.0 | 3 / 0 | 2.4 → 2.4 |
| `loose` | PASS (weak) | 156.6 → 159.0 | 3 / 0 | 2.4 → 2.4 |
| `fit`, leave one place out | PASS (weak) | 156.6 → 158.0 | 2 / 0 | 2.4 → 2.4 |

- All 261 labelled real train frames: no new box that is not on its barrel, in any arm. The tin label (`lampwarm6_glass_occl_02`) and every `*_neg_02` frame: unchanged. Found: `occlx_02` (black box), `lampcool6_ottoman_occl_02` (white box, the right side this time; the bulge rule had put it on the wrong side), `occlx_03` (`slack` only).
- Not found: `palewood_occl_02` (black charger on a black background: the line above is the charger's faint rim, 17 px off), `lampmid6_ottoman_occl_02` (no stripe in the mask at all).
- Simulated side cuts with a painted dark box (only a test of the geometry): at 60 % hidden, found 151 → 237 of 312 (`cut`), 241 (`slack`), 290 (`loose`). At 75 %, 28 → 197. Boxes on nothing across all amounts: today 2, `cut` 7, `slack` 9, `loose` 2, `cut+bulge` 2.
- Idea 2 (the photo beside the cut against the photo one W further out) did not separate hidden from free ends: no rule.

**Takeaway.** The cut line works where the photo shows a clear edge: a box against a light wall or table. It adds 2 or 3 barrels and draws no box off a barrel on the real frames. The gain is small because few real frames have this case. Dark things on dark backgrounds are out of reach.

**Next.** Shoot more side cuts by real boxes, books and chargers, on more tables. The judged numbers rest on 3 barrels. Before any adoption, `slack` needs held-out frames: in leave one place out it was never tested on abp_white.
