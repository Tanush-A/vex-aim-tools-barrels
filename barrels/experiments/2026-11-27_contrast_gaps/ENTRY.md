## 2026-11-27 — Contrast gaps: the frames where the vendor still beats the stripe by contrast

**Branch** `wip/exp-contrast-gaps` (from `barrels` at 125aed7, contrast is the default; `wip/exp-contrast` merged in, its
module kept as `contrast_c4.py`). Code `experiments/2026-11-27_contrast_gaps/`; results `results/2026-11-27_contrast_gaps/`.
Plan `PREREG.md` (committed before the first judged run) and its addendum (committed before the second round).

**Question.** The vendor finds more than we do on 16 train frames with a vendor file. Which of those can a small
addition after today's default recover, with no box on an empty frame and no new box off its barrel?

**What the losses were (from the pictures and the diagnosis).**
- Ottoman close-ups (3 frames): the frame's bottom cuts the body band below the stripe, so contrast never searches that
  row. The orange body reads hue 16-17, outside 3-13, so the fixed colors paint only specks.
- A barrel cut by the side of the frame (bathroom edge, 3 frames; pale wood edge; wood core): the counting window
  counts the part outside the frame as "no", so share and strength stay under the floors (strength 0.87-1.08).
- Touching blue barrels on the ottoman, cool and mid lamp: contrast DOES paint the left barrel. Its box is then refused
  because the fixed colors' box on the middle barrel is 78-81 px wide (1.2-1.3 barrels) and covers half of it. The
  "one body" guard was not the cause (the adopted stage has no such guard).
- The same under the warm lamp: both blue candidates are too weak (0.92 and 0.97, floor 1.15).
- The very dark ottoman (lamp mid 3, report only): the signal is there, but the dark parts are dark. Body minus stripe
  is still 1.22 in the channel (2.15 at mid 6), about 10 times the pixel noise. But 80-100 % of a blue barrel's body
  and of an orange barrel's stripe have V under 25 (the contrast floor), so the band is unreadable. The log offset is
  not the problem: offset 2, 8 or 16 gives the same signal-to-noise. A floor of V 10 finds 2 of 15 barrels, and with a
  lower margin and strength 5 of 15, with no candidate on nothing (`dark.md`).
- Side occlusion (`*_occl_02`, abp white occlx, pale wood occl_02): left to the occlusion experiment.

**Five additions** (each runs after today's default and only adds; all off = today's boxes on all 261 train frames, `check.py`):
E counts an edge window inside the frame. H is a half sandwich at the frame bottom. S splits a fixed-colors box two
barrels wide by the run on the painted mask. B takes a weaker candidate beside a found barrel at its stripe row. O
handles two boxes of different colors on one barrel: it drops the added one the stripe pattern supports less (the
coordinator's group 5).

**Group 5 (other-color boxes), counted on all train frames and Dave's 12 office frames (`other_color.md`).** Both
named cases are pairs where BOTH boxes were added by contrast. So "drop an added box inside a fixed-colors box" finds
none. Three ways of choosing failed on Dave's snap 07 (they dropped the real orange barrel): a candidate inside the
box, the sandwich alone, and the mask share alone. The wrong blue box reads the orange top as a stripe between a
purple sign and the real blue stripe. Kept: only same-size pairs (heights within 1.25x); the sandwich at the stripe
row decides; on a near tie (under 0.25 apart), the fixed colors decide. At overlap 0.4 it drops 1 wrong box on an
ordinary frame (warm bathroom core), 2 on extreme frames (1 wrong, 1 misplaced box over a hidden orange barrel), and
the wrong blue box on Dave's snap 07. It removes no real barrel except that hidden one on `lampmid6_wood_occl_04`. Its two
numbers were set on these 7 pairs (in-sample).

**Results (`summary.md`).** Baseline 156.63 of 172 placements, 277 of 307 per frame, boxes not on their barrel 2.43.

| candidate | round | verdict | found per placement | per frame | gained / lost | boxes not on barrel | empty |
|---|---|---|---|---|---|---|---|
| E edge | leave one place out | NO CLEAR DIFFERENCE | 156.63 | 277 | 0 / 0 (+3 extreme) | 2.43 | 0 |
| H half | leave one place out | NO CLEAR DIFFERENCE | 156.63 | 277 | 0 / 0 | 2.43 | 0 |
| S split | leave one place out | NO CLEAR DIFFERENCE | 156.63 | 277 | 0 / 0 | 2.43 | 0 |
| B beside | leave one place out | NO CLEAR DIFFERENCE | 156.63 | 277 | 0 / 0 | 3.43 (campus +1) | 0 |
| O other | leave one place out | NO CLEAR DIFFERENCE | 156.63 | 277 | 0 / 0 | 2.43 | 0 |
| ALL | leave one place out | NO CLEAR DIFFERENCE | 156.63 | 277 | 0 / 0 (+3 extreme) | 3.43 (campus +1) | 0 |
| E edge 0.6 | in-sample | NO CLEAR DIFFERENCE | 157.38 | 280 | 3 / 0 | 2.43 | 0 |
| H half 1.3 | in-sample | NO CLEAR DIFFERENCE | 157.63 | 280 | 3 / 0 | 2.43 | 0 |
| S split 1.25 | in-sample | NO CLEAR DIFFERENCE | 156.97 | 278 | 1 / 0 | 2.43 | 0 |
| B beside 1.0 | in-sample | NO CLEAR DIFFERENCE | 156.97 | 278 | 1 / 0 | 2.43 | 0 |
| O other 0.4 | in-sample | NO CLEAR DIFFERENCE | 156.63 | 277 | 0 / 0 | 2.18 | 0 |
| ALL | in-sample | PASS (weak, in-sample) | 159.05 | 285 | 8 / 0 (+3 extreme) | 2.18 | 0 |

The traps (`*_neg_02` on every train frame, `lampwarm6_glass_occl_02`) get no new box, at the chosen and at the
loosest settings.

**Why leave one place out shows nothing.** Each addition fixes barrels at ONE ordinary place. When that place is
held out, its fold sees no gain there, so the addition stays off; at the other places it changes nothing. This is
the honest result of the registered rule: these fixes cannot be chosen blind with 8 places. B's held-out run also
shows the one false box any addition made: a blue box on a purple sign with an orange thing behind it
(`campus_light_clutter_02`, chosen at 0.9 when the campus was held out).

**Against the vendor** (`tools/vs_vendor.py --all --cand-callable experiments/2026-11-27_contrast_gaps/run.py:best`,
the in-sample ALL): box on the barrel 221 -> 229 of 258 (vendor 211). Strict 215 -> 223; extra boxes 12 -> 11. Frames
where the vendor finds more: 16 -> 11.

**Cannot.** The dark ottoman (report only); side occlusion; the mid-lamp touching pair (split needs 1.19, picked 1.25);
the pale-wood edge barrel (no stripe reading at all: share 0.67, strength 0.64); a barrel inside a wrong detector box
(`lampwarm6_ottoman_core_01`).

**Tanush's question (`seg_why.md`, pictures in `results/.../seg_why/`).** Warm bathroom: the blue reads hue 20-55
with S 32-83, so the warm lamp turns it gray-yellow. The hue gate stops 100 % of every blue part. Contrast paints 80-100 % of
them. Ottoman: the orange reads hue 16-17, just above the range 3-13, at S about 200 and V 130-230. The hue gate stops
85-96 %, and the specks are the few pixels at 13 or below. Contrast paints about 90 % of the orange of the barrels it
adds, but it leaves a barrel the fixed colors found as speckled as it was: it paints only barrels that were missed. Brightness and
saturation stop almost nothing there. On the dark ottoman (mid 3) it is brightness: V under 40 for most of the blue.

**Next.** E, H and S are narrow and clean (no wrong box in any run). Adopting them needs a decision that a
one-place fix may be taken on its pictures. A held-out place with close-ups or edge barrels would let the judge see them.
