# Overnight, 2026-11-23 → 24: one report for everything

Written by Claude for Tanush. Plain English. Read sections 1 to 3; the rest is reference.

## 1. The short version

- **The vendor beats us, and it is the color step, not the detector.** On the 7 new conditions with vendor files, ours finds 59 of 123 barrels, the vendor 99. Almost all of the gap is the black ottoman and the gray table, where our fixed colors paint too little of the barrels. On pale wood we tie; on your occlusion set we win (26 against 24, fewer false boxes).
- **Your slider labels prove the fix exists.** On the ottoman, your hand-set thresholds find 12–15 of 15 barrels where the fixed ones find 0–6. So thresholds set per condition close most of the gap.
- **But nothing yet predicts those thresholds from the picture.** With only 3 places slider-labelled (ottoman, pale wood, gray table), no relation holds up when a whole place is held out. The adaptive rule written last night fails its own test. Tomorrow's data (glass, bathroom, white tables) is exactly what can settle it.
- **The close-up false box is fixed,** and it explained your "specific position": a close barrel where the frame bottom cuts the stripe itself is now found. The never-regress check passes again.
- **Your bulge idea was checked and is not needed.** On the painted pixels a barrel-cut end is flat, not bulging inward, and the own-side rule turned out to make no wrong-side calls anyway. It stays off for a different, small reason.

## 2. What you need to do

1. **Say "understood" on the close-up fix** (section 4.1). It is on branch `wip/tomorrow`; I merge it on your word.
2. **Tomorrow, after importing, boxing and slider-labelling:** switch to the combined branch and run one command:
   ```
   git checkout wip/tomorrow && git pull
   python barrels/experiments/run_all.py
   ```
   It runs the tests, the never-regress check, the full table, ours against the vendor per condition, and the adaptive-rule test, and writes one page: `barrels/results/<date>_run_all/summary.md`. Last night's dry run took a few minutes and worked end to end.
3. **Slider-label the white tables too** if you can (home or ABP white): the adaptive rule is anchored on home, and labels there test that anchor.
4. **Tell the data session each new condition's light kind** (window / overhead / lamp / mixed). It goes in `barrels/data/conditions.json`; the glass-table lamp frames are "mixed".
5. **Decide:** do the four ottoman lamp settings and the gray table count as ordinary conditions? The goal is to match the vendor in ordinary conditions, and those are where it beats us. My view: yes for the gray table and the three bright ottoman settings; `lampmid3_ottoman` is too dark (nothing finds more than 1 of 15 there, at any thresholds).

## 3. The numbers that matter

**Ours against the vendor** (train frames with a vendor file; strict rule; found / false):

| condition | barrels | ours | vendor |
|---|---|---|---|
| gray table (window + weak overhead) | 16 | 10 / 2 | 16 / 0 |
| ottoman, cool lamp 6 | 15 | 3 / 0 | 13 / 1 |
| ottoman, mid lamp 3 | 15 | 1 / 1 | 10 / 1 |
| ottoman, mid lamp 6 | 15 | 6 / 0 | 13 / 1 |
| ottoman, warm lamp 6 | 15 | 0 / 1 | 11 / 0 |
| pale wood, overhead | 15 | 13 / 1 | 12 / 1 |
| occlusion set, white table | 32 | 26 / 1 | 24 / 4 |
| **all** | 123 | **59 / 6** | **99 / 8** |

- The vendor files are sound: its boxes land where its numbers say (checked on 33 pictures), and they are a little looser than your boxes (median overlap 0.82).
- On hidden barrels the vendor boxes only the visible part; three of its "false" boxes on the occlusion set are that.
- Tomorrow's white-table frames are the first where the vendor runs in its own home conditions. That comparison matters most.

**Home and campus:** unchanged, 28 of 29 and 35 of 35, no false box.

## 4. What was done overnight, one paragraph each

**4.1 The close-up fix (branch `wip/tomorrow`, needs your "understood").** The old rule said "a barrel-colored piece reaching the frame bottom is a close barrel whose stripe is below the frame". It boxed a printed orange fruit on your trap shot 15. Two changes:
- If the frame's side also cuts the piece, it must be visible from its top down to where its stripe would be. A real close barrel is; the fruit stopped halfway, so no box.
- A piece whose stripe runs off the frame bottom is also a close barrel. This is your "specific position": the frame bottom cuts the stripe itself, so the detector sees no body below the stripe and dropped it. Now it is found (pale wood `close_01`).

Result: the fruit box is gone, one new close barrel is found, none is lost, nothing else changes anywhere (scorecard, damage tests, recordings identical), and the never-regress check passes. The baseline is re-saved so your new tables are now watched for boxes on empty frames.

**4.2 Ours against the vendor (merged).** Described in section 3. The list of the 45 barrels the vendor finds and we miss is in `barrels/results/2026-11-23_vendor/summary.md`. Ten of them are hidden barrels; the rest are the color step failing on the ottoman and gray table.

**4.3 Histograms against your slider labels (branch `wip/tomorrow`).**
- There are 6 independent places so far, 3 with slider labels.
- Held out one place at a time, no feature of the picture predicts your thresholds better than just averaging the other places.
- Held out one condition at a time it looks good, but that is the four ottoman settings vouching for each other: same table, same lamp, same room.
- Your hand labels and thresholds computed from your boxes differ by more than the agreed limit, so only hand labels count.
- One lead: the blue saturation floor tracks the frame's bright-blue level across places.
- The rule written before testing moves three thresholds with the frame's histogram. It fails tonight: 1 more barrel overall, but worse on the ottoman and one new box on an empty frame. A copy of it is frozen tonight and will be tested on tomorrow's new places, which is the honest test.
- To pass tomorrow it needs at least 5 labelled places, at least 3 more barrels found in at least 2 places, at most 2 more false boxes, no box on an empty frame, no condition worse, and the never-regress check passing.

**4.4 Your bulge idea for the own-side sliver (not merged; nothing to merge).** Measured on 853 ends cut by a barrel in front: they come out flat, not bulging inward, because the detector reads only where the body starts and stops in each column, and beside a front barrel those stay put. More useful: the own-side rule made no wrong-side call at all in 400 boxes. It still loses 3 simulated scenes where two same-colored barrels stand together and its full-width box swallows the back barrel. So it stays off; one same-colored-pair check would likely fix that, if you want it.

## 5. Where things are

| what | where |
|---|---|
| tomorrow's one command | `python barrels/experiments/run_all.py` on branch `wip/tomorrow` |
| the vendor comparison alone | `python barrels/experiments/2026-11-24_vendor/run.py` |
| the adaptive test alone | `python barrels/experiments/2026-11-24_adaptive/run.py` |
| conditions and their light kind | `barrels/data/conditions.json` |
| merged on `barrels` | the vendor comparison and the runner |
| on `wip/tomorrow`, waiting for "understood" | the close-up fix, the adaptive rule (off by default) |

The test frames have not been opened. The one look at them comes last, after tomorrow's data is scored and the adaptive rule is in or shown not to work.
