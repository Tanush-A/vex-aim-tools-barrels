# Condition 4, by eye (Claude, 2026-11-11): every box `w25` / `w25h` adds, looked at on the sheets

| frame | added box | what it is on | verdict |
|---|---|---|---|
| CAMPUS `occl_02` | blue | the barrel behind the robot (the step-7 miss) | real, now found |
| DAVE `speckle_snap_10` | orange | the big orange barrel in front | real, now found |
| REC `r2_pan` frames 034, 035 | blue | a blue barrel entering at the right frame edge | real |
| REC `r3_enter_leave` frames 014, 047 | orange | an orange barrel entering at the right frame edge | real |
| WOOD `atwarm_wood_core_01` | orange | the left third of the big orange barrel plus wood table: a second box on a barrel that already has one. The table is segmented as orange and a shadow hole cuts the stripe in two; the left piece is now wide enough to count | **false** |
| WOOD `upmid_wood_core_01` | orange | an orange box overlapping the far blue barrel next to the colored box | **false** |

**Verdict: condition 4 FAILS** for `w25` and `w25h` (2 false boxes on the 25 wood frames; 6 of 8 added boxes are real
barrels, and none of the false ones is on a white-table frame). By the pre-registered rule nothing is adopted:
`stripe_w_min` stays 0.4 and `occl_body_side` stays off on `wip/occlusion`.

Context, not an excuse: on wood the color model already fails (the table itself reads orange; `base` draws 61
boxes on those 25 frames), and wood is step 8 / 10 work. Whether to adopt before the wood front end exists is
Tanush's call, not the script's.

(h) alone (`h`): moves 90 boxes on unlabeled frames (median largest-edge shift 2 px on the recordings, 8 px on
wood), loses and gains nothing on labeled frames, mean IoU of found barrels 0.878 -> 0.888 home, 0.865 -> 0.864
campus. Too small to adopt on its own; it matters only together with the narrow stripe (`occl_02` IoU 0.51 -> 0.68).
