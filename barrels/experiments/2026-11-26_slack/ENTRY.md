## 2026-11-26/27 — The detector has no slack (branch `wip/exp-slack`; pre-registered, two rounds; not adopted, awaiting Tanush)

**Question.** One pixel shaved off every painted region loses 40 of the 211 barrels the detector finds on the ordinary train frames (12 of 63 on the two white tables by the audit; 11 of 63 with the stored model). Can one rule keep those barrels without a single new false box?

**Where they die.** Looked at barrel by barrel on the white tables before the plan (`look_white*.py`). A stripe 5 rows tall becomes 3. The floor is 3.6 to 4.7. The existing second reading at the seams would pass it (6.5 to 8.0 against 8.1 to 10.3). It is not asked: after the pixel the stripe is 0.65 to 0.73 of a barrel wide, under the 0.8 it needs. One pixel moves several readings at once.

**Method.** One experiment flag, `DetConfig.slack`, off by default (letters A B C D). The proof harness at defaults: IDENTICAL BOXES ON EVERY INPUT (5435 masks, 6152 boxes). Each arm against today's detector on the same mask. Train frames only.

- **A**: the stripe's area floor scales with the barrel (18 % of the predicted stripe, never above 20 px; it changes only beyond 50 cm).
- **B**: a stripe too thin or too small is read at the seams when the barrel is seen whole, by its width (eaten pixels given back) or by the rest of the barrel (top and bottom where the row predicts them, not against the other color, one side ending with the stripe).
- **C**: one size floor missed by one pixel per edge is forgiven when the top and bottom are seen, body is above and below, the box is half filled.
- **D** (round 2, addendum committed first): B, but a stripe too *small* is read again only when the rest of the barrel supports it with its edges as seen.

**Results** (per frame; "back" = of the barrels lost to the harm, found by the arm).

| arm | (a) 1 px, back of 40 | (a) 2 px, back of 107 | (b) typical / bad day, back of 42 / 51 | (c) unharmed, judge | (e) hand colors: unharmed boxes not on barrel; 1 px back of 61; 2 px back of 150 | (d) new boxes not on a barrel, 5435 harness masks; empty frames |
|---|---|---|---|---|---|---|
| A | 0 | 0 | 0 / 0 | NO CLEAR DIFFERENCE, 211 → 211 | 3 → 3; 0; 0 | 0; none |
| B | 11 | 58 | 18 / 20 | NO CLEAR DIFFERENCE, 211 → 214 | **3 → 7**; 22; 69 | **4** (hand 2, pool 1, scene 1); **1 on an empty frame** |
| C | 6 | 1 | 15 / 15 | NO CLEAR DIFFERENCE, 211 → 213 | 3 → 3; 7; 1 | 0; none (loses 2 scene barrels) |
| **D** | **11** | **55** | **18 / 20** | **NO CLEAR DIFFERENCE, 211 → 214** (133.8 → 135.4 placements) | **3 → 3; 22; 66** | **0; none** |
| CD | 11 | 55 | 18 / 20 | NO CLEAR DIFFERENCE, 211 → 215 | 3 → 3; 22; 66 | 0; none |

- No arm loses a found barrel on any real mask. On the eroded masks every arm lowers the boxes not on their barrel.
- B's four false boxes (hand colors: bathroom tile under the mid and dim lamp, an empty bathroom frame, the warm ottoman) all came from a stripe under 20 px called "seen whole" by its width alone. D removes all four and keeps 11 of 11 at one pixel.
- Contact sheets: every box that appears or disappears on a real frame (252 in round 1, all looked at). D's new boxes are all on a barrel. 186 are strict hits; 12 sit on their barrel with the box off. One of those straddles two touching blue barrels (`lampmid6_ottoman_touch_01`, one pixel off). D removes 4 boxes of the wrong color.
- The cliffs: `height_max` 1.5 → 1.2 changes nothing with or without D. `min_width_px` 12.8 and `min_stripe_px` 4.8 are refused by the code's own assertion. D does not touch them.

**Takeaway.** The pre-registered success line was one in three at one pixel. **D brings back 11 of 40 (27 %): under the line.** It breaks no hard limit and is the arm the rule picks. At two pixels it brings back half (55 of 107), with hand colors 66 of 150. The barrels it cannot save die through caps (7), side occlusion (4), and stripes under 20 px whose barrel edges do not agree (about 15). Slack in the stripe's size tests helps, and nothing else in the chain moves.

**Next.** Tanush decides whether D becomes plain code. If yes: the `DETECTOR-MAP.md` changes listed in the report. The caps and the small far stripes are separate experiments.
