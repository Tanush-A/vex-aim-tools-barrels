# Pre-registration: counting placements, a misplaced box once, the vendor assumed on white (2026-11-26, TODO M1)

Written 2026-11-26 on branch `wip/measure`, **before `run.py` existed and before any number below was computed with the
new counting**. This is not a test of a method. It is a change in how results are counted, so what is fixed in advance
is the definitions and the checks the new counting must pass. Train frames only; no test frame is opened, scored or
listed.

## What was seen before this was written (honesty)

- The review's audit (`eval_audit.md`, sections 1 and 2.4) and its train-only scripts: ours 148 and the vendor 177 of
  243 under the strict rule on the new ordinary conditions; 150 and 195 by overlap alone; 150 and 200 by position; the
  243 barrels are 108 placements in 47 arrangements at 6 places; 23 of the vendor's 30 "false" boxes sit on a real
  barrel.
- Today's `python barrels/tools/report.py --vendor` and `--gate` on train frames (the old table and its looser counts).
- A label-only check: in every arrangement shot under several lights, every light has the same number of boxes with
  the same colors (31 such arrangements among the train frames, no mismatch).

Not seen: any count under the definition of "on a barrel" chosen below, and any placement-weighted count.

## The definitions (fixed here)

1. **Place** = a table in a room, `data/conditions.json`. **Arrangement** = one scene at one place: the frames
   `{scene}_{nn}` of that place, one per light. **Placement** = one barrel in one arrangement (the same physical barrel
   in every light). Which label box is which placement is decided from the labels alone: in every light a box takes
   the number of the same-colored box it overlaps most in the arrangement's first frame; a light whose boxes do not all
   pair up at IoU >= 0.5 is an error, not a number.
2. **Each placement counts once.** Shot under k lights and found in j of them, it counts j / k. Totals over places add
   these shares. Raw counts (per frame, the old numbers) stay beside them.
3. **The strict rule is unchanged** (same color, IoU >= 0.5, bottom edge within max(3 px, 10 % of the true height),
   highest IoU first). "Found" always means a strict hit.
4. **The second accounting.** After the strict hits are taken:
   - a true barrel is `found, box off` when a box of its color that no barrel has taken is **on it**; else `missed`;
   - a box is `on its barrel` (a strict hit, or the box of a `found, box off` barrel), `wrong color on a barrel`,
     `second box on a barrel`, or `on nothing`. Boxes on empty frames are `on nothing` and are also counted on their
     own, clean empty frames apart.
5. **On a barrel** = at least half of the smaller of the two boxes lies inside the other (intersection area / the
   smaller area >= 0.5). Chosen before any count, for these reasons:
   - *Not "overlap" (IoU >= 0.5, the bottom not checked).* It still carries the labelling convention that the box must
     be the whole barrel: a box around the visible half of a hidden barrel has IoU under 0.5 and would stay "a miss
     plus a false box", which is the double charge this accounting is meant to remove.
   - *Not "position" (centers at most half the true width apart).* It depends on the true box's width, so the test
     gets tighter for a barrel the frame cuts; it is not nested with the strict rule (a tall thin clipped box can pass
     IoU >= 0.5 and fail it); and it mixes a sideways limit with an up-down one.
   - *This one* has no unit, treats the two boxes alike, and every pair with IoU >= 0.5 passes it, so the three states
     are nested: strict hit, on the barrel, not on it. Its known weak point, stated now: a small box that lies inside
     a barrel's box counts as on it wherever it sits. One box per barrel at most gets that credit; any further one is
     a `second box`.
6. **Boxes that are not on their barrel are weighted like placements**: each counts 1 / (the lights of its
   arrangement), so one tin boxed under five lights is one box.
7. **The vendor on white tables** (Tanush, 2026-11-26): on a condition marked `vendor_assumed` in
   `data/conditions.json` (home and campus: white table, window or overhead light, no vendor file) the vendor counts
   as finding every barrel. The row is marked ASSUMED, says nothing about the vendor's boxes there, and is never added
   into a measured total without the word "assumed" on that total.

## Checks the new counting must pass (a failure is a bug, and is fixed before any number is quoted)

- C1. For every train frame and both arms, the number of `found` barrels equals `eval_det.evaluate_frame(rule="v2")`'s
  hits, and found + box off + missed = the true barrels, and the box states add up to the boxes drawn.
- C2. The old strict numbers are reproduced exactly: on the frames with vendor files, ordinary new conditions, ours
  148 of 243 and the vendor 177 of 243; HOME 28 of 29; CAMPUS 35 of 35.
- C3. The ordinary new conditions are 108 placements in 47 arrangements at 6 places, as the audit derived.
- C4. A raw count never differs between the old table and the new one for the same frames.

## What is reported, and how it will be read

- The headline table: ours against the vendor **by place**, under strict and under the second accounting, with the
  placements, arrangements and lights each number rests on; a total over the measured places; the two assumed places
  as their own rows; no winner is named for a single condition.
- The per-condition table (raw counts), kept.
- A sensitivity table: the second accounting with "overlap" and with "position" as the test in place of the chosen
  one. If the chosen test and "position" disagree on a box, every such box is listed with both boxes' corners. The
  definition above stands whatever the table shows; a listed case that is plainly not on its barrel would be recorded
  as a flaw in a dated addendum, not fixed silently.

## Outputs

`results/2026-11-26_measure/`: `summary.md` (the headline table and the checks), `places.json`, `per_barrel.csv` (every
train barrel: its placement, its state per arm), `sensitivity.md`.
