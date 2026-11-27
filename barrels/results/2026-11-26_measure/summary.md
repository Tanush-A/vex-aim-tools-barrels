# Ours against the vendor, every placement counted once (2026-11-26, git f20ad1c)

`python barrels/experiments/2026-11-26_measure/run.py` (definitions and checks: `../../experiments/2026-11-26_measure/PREREG.md`). Train frames only; test frames never opened. Ours = today's default (color model `eb863d84`, `DetConfig()`); the vendor = the boxes the robot's own detector reported, saved with each frame. HOME is scored leave one scene out, as in the eval table.

**How to read it.** A *place* is a table in a room. An *arrangement* is one scene at one place; under five lamp settings it is still one arrangement. A *placement* is one barrel in one arrangement. A placement counts once: shot under several lights, it counts the share of its lights in which it is found. *Found* is the strict rule agreed with Dave (same color, IoU >= 0.5, bottom edge within 10 % of the height), unchanged. *Box off* is new: a box of the right color sits on the barrel but fails the strict rule; it used to be charged as a miss plus a false box. No winner is named for a single condition: most conditions are 15 placements at one place.

## The headline table: by place

| place / condition | lights | frames | barrels | placements | ours found | ours raw | ours box off | ours missed | ours wrong | ours 2nd | ours none | ours empty | vendor found | vendor raw | vendor box off | vendor missed | vendor wrong | vendor 2nd | vendor none | vendor empty |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| abp_gray | 1 | 8 | 16 | 16 | 10.0 | 10 | 1.0 (1) | 5.0 (5) | 0 | 0 | 0 | 0 | 16.0 | 16 | 0.0 (0) | 0.0 (0) | 0 | 0 | 0 | 0 |
| home_bathtile | 4 | 28 | 60 | 15 | 4.0 | 16 | 0.0 (0) | 11.0 (44) | 0 | 0 | 0 | 0 | 7.0 | 28 | 0.8 (3) | 7.2 (29) | 0 | 0 | 0 | 0 |
| home_glass | 5 | 36 | 75 | 15 | 14.8 | 74 | 0.2 (1) | 0.0 (0) | 0 | 0 | 3 | 0 | 12.0 | 60 | 2.8 (14) | 0.2 (1) | 0 | 0 | 6 | 6 |
| home_ottoman | 3 | 21 | 45 | 15 | 3.0 | 9 | 0.0 (0) | 12.0 (36) | 0 | 0 | 1 | 0 | 12.3 | 37 | 0.7 (2) | 2.0 (6) | 0 | 0 | 0 | 0 |
| uc_palewood | 1 | 7 | 15 | 15 | 13.0 | 13 | 0.0 (0) | 2.0 (2) | 0 | 0 | 1 | 0 | 12.0 | 12 | 1.0 (1) | 2.0 (2) | 0 | 0 | 0 | 0 |
| abp_white | 1 | 17 | 32 | 32 | 26.0 | 26 | 0.0 (0) | 6.0 (6) | 0 | 0 | 0 | 0 | 24.0 | 24 | 3.0 (3) | 5.0 (5) | 0 | 0 | 1 | 1 |
| **measured, all places** | **15** | **117** | **243** | **108** | **70.8** | **148** | **1.2 (2)** | **36.0 (93)** | **0** | **0** | **5** | **0** | **83.3** | **177** | **8.2 (23)** | **16.5 (43)** | **0** | **0** | **7** | **7** |
| campus_study (vendor ASSUMED) | 1 | 21 | 35 | 35 | 35.0 | 35 | 0.0 (0) | 0.0 (0) | 0 | 0 | 0 | 0 | 35.0* | 35* | - | - | - | - | - | - |
| home_white (vendor ASSUMED) | 1 | 16 | 29 | 29 | 28.0 | 28 | 0.0 (0) | 1.0 (1) | 0 | 0 | 0 | 0 | 29.0* | 29* | - | - | - | - | - | - |
| **measured + ASSUMED** | **17** | **154** | **307** | **172** | **133.8** | **211** | **1.2 (2)** | **37.0 (94)** | **0** | **0** | **5** | **0** | **147.3*** | **241*** | **8.2 (23)** | **16.5 (43)** | **0** | **0** | **7** | **7** |

- **Measured places** (6 places, 108 placements in 47 arrangements with barrels; 243 barrels when every light is counted): ours **70.8** found, the vendor **83.3**. Found either way (strict, or with the box off): ours 72.0, the vendor 91.5.
- **Boxes.** Ours: 2 on their barrel but off, 0 wrong color, 0 second boxes, 5 on nothing (0 on empty frames). The vendor: 23 on their barrel but off, 0 wrong color, 0 second boxes, 7 on nothing (7 of them on empty frames).
- **The same frames counted the old way:** ours 148 and the vendor 177 of 243 found; "false boxes" 7 against 30. Of the vendor's 30, 23 sit on a real barrel of their color and fail the strict rule; of ours 7, 2.
- **ASSUMED, not measured** (starred): on the two white tables without vendor files (home and the campus study room, 37 frames, 64 placements) the vendor counts as finding every barrel (Tanush, 2026-11-26). With that assumption added: ours 133.8 of 172 placements, the vendor 147.3* of 172. The assumption says nothing about the vendor's boxes there.
- **The one white table where the vendor was measured** is the ABP occlusion set (window light): 24 of 32 strict, 3 more with the box off. It is an occlusion set, harder than the home and campus scenes; it is the only check on the assumption that exists.

## By condition (kept; one light each, so per placement = per frame)

| place / condition | lights | frames | barrels | placements | ours found | ours raw | ours box off | ours missed | ours wrong | ours 2nd | ours none | ours empty | vendor found | vendor raw | vendor box off | vendor missed | vendor wrong | vendor 2nd | vendor none | vendor empty |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| abp_gray / both_abpgray | 1 | 8 | 16 | 16 | 10.0 | 10 | 1.0 (1) | 5.0 (5) | 0 | 0 | 0 | 0 | 16.0 | 16 | 0.0 (0) | 0.0 (0) | 0 | 0 | 0 | 0 |
| home_bathtile / lampcool6_bathtile | 1 | 7 | 15 | 15 | 13.0 | 13 | 0.0 (0) | 2.0 (2) | 0 | 0 | 0 | 0 | 11.0 | 11 | 2.0 (2) | 2.0 (2) | 0 | 0 | 0 | 0 |
| home_glass / lampcool6_glass | 1 | 7 | 15 | 15 | 15.0 | 15 | 0.0 (0) | 0.0 (0) | 0 | 0 | 0 | 0 | 12.0 | 12 | 3.0 (3) | 0.0 (0) | 0 | 0 | 1 | 1 |
| home_ottoman / lampcool6_ottoman | 1 | 7 | 15 | 15 | 3.0 | 3 | 0.0 (0) | 12.0 (12) | 0 | 0 | 0 | 0 | 13.0 | 13 | 1.0 (1) | 1.0 (1) | 0 | 0 | 0 | 0 |
| home_bathtile / lampmid3_bathtile | 1 | 7 | 15 | 15 | 1.0 | 1 | 0.0 (0) | 14.0 (14) | 0 | 0 | 0 | 0 | 9.0 | 9 | 0.0 (0) | 6.0 (6) | 0 | 0 | 0 | 0 |
| home_glass / lampmid3_glass | 1 | 7 | 15 | 15 | 15.0 | 15 | 0.0 (0) | 0.0 (0) | 0 | 0 | 1 | 0 | 12.0 | 12 | 3.0 (3) | 0.0 (0) | 0 | 0 | 1 | 1 |
| home_ottoman / lampmid3_ottoman [extreme] | 1 | 7 | 15 | 15 | 1.0 | 1 | 1.0 (1) | 13.0 (13) | 0 | 0 | 0 | 0 | 10.0 | 10 | 1.0 (1) | 4.0 (4) | 0 | 0 | 0 | 0 |
| home_bathtile / lampmid6_bathtile | 1 | 7 | 15 | 15 | 1.0 | 1 | 0.0 (0) | 14.0 (14) | 0 | 0 | 0 | 0 | 8.0 | 8 | 1.0 (1) | 6.0 (6) | 0 | 0 | 0 | 0 |
| home_glass / lampmid6_glass | 1 | 7 | 15 | 15 | 15.0 | 15 | 0.0 (0) | 0.0 (0) | 0 | 0 | 1 | 0 | 12.0 | 12 | 3.0 (3) | 0.0 (0) | 0 | 0 | 1 | 1 |
| home_ottoman / lampmid6_ottoman | 1 | 7 | 15 | 15 | 6.0 | 6 | 0.0 (0) | 9.0 (9) | 0 | 0 | 0 | 0 | 13.0 | 13 | 1.0 (1) | 1.0 (1) | 0 | 0 | 0 | 0 |
| home_bathtile / lampwarm6_bathtile | 1 | 7 | 15 | 15 | 1.0 | 1 | 0.0 (0) | 14.0 (14) | 0 | 0 | 0 | 0 | 0.0 | 0 | 0.0 (0) | 15.0 (15) | 0 | 0 | 0 | 0 |
| home_glass / lampwarm6_glass | 1 | 7 | 15 | 15 | 15.0 | 15 | 0.0 (0) | 0.0 (0) | 0 | 0 | 1 | 0 | 12.0 | 12 | 2.0 (2) | 1.0 (1) | 0 | 0 | 0 | 0 |
| home_ottoman / lampwarm6_ottoman | 1 | 7 | 15 | 15 | 0.0 | 0 | 0.0 (0) | 15.0 (15) | 0 | 0 | 1 | 0 | 11.0 | 11 | 0.0 (0) | 4.0 (4) | 0 | 0 | 0 | 0 |
| uc_palewood / overheaddim_palewood | 1 | 7 | 15 | 15 | 13.0 | 13 | 0.0 (0) | 2.0 (2) | 0 | 0 | 1 | 0 | 12.0 | 12 | 1.0 (1) | 2.0 (2) | 0 | 0 | 0 | 0 |
| abp_white / window_abpwhite | 1 | 17 | 32 | 32 | 26.0 | 26 | 0.0 (0) | 6.0 (6) | 0 | 0 | 0 | 0 | 24.0 | 24 | 3.0 (3) | 5.0 (5) | 0 | 0 | 1 | 1 |
| home_glass / window_glass | 1 | 8 | 15 | 15 | 14.0 | 14 | 1.0 (1) | 0.0 (0) | 0 | 0 | 0 | 0 | 12.0 | 12 | 3.0 (3) | 0.0 (0) | 0 | 0 | 3 | 3 |
| campus_study / campus_light (vendor ASSUMED) | 1 | 21 | 35 | 35 | 35.0 | 35 | 0.0 (0) | 0.0 (0) | 0 | 0 | 0 | 0 | 35.0* | 35* | - | - | - | - | - | - |
| home_white / window_light (vendor ASSUMED) | 1 | 16 | 29 | 29 | 28.0 | 28 | 0.0 (0) | 1.0 (1) | 0 | 0 | 0 | 0 | 29.0* | 29* | - | - | - | - | - | - |

## What the columns mean

found = strict hits (the v2 rule), each placement once: a placement shot under several lights counts the share of its lights in which it is found; raw = strict hits counted per frame (the old number, out of brls). box off = a same-color box is on the barrel but fails the strict rule, placements (frames); missed = no box of its color on it. Boxes: wrong = on a barrel of the other color, 2nd = a second box on a barrel, none = on no barrel, empty = on empty frames (part of none). On a barrel = at least half of the smaller of the two boxes lies inside the other. plcm = placements (physical barrels), brls = label boxes (a placement once per light). * = ASSUMED, not measured (on a total: it holds assumed frames).

## The checks of the pre-registration

- C1 pass: on all 285 frame x arm pairs, found = the v2 rule's hits, found + box off + missed = the true barrels, and the box states add up to the boxes drawn.
- C2 pass: the old strict numbers are reproduced exactly: ordinary new conditions, frames with vendor files, ours 148 and the vendor 177 of 243; HOME 28 of 29 (leave one scene out), CAMPUS 35 of 35.
- C3 pass: the 243 barrels of the ordinary new conditions are 108 placements in 47 arrangements at 6 places (with the 7 arrangements that hold no barrel: 54).
- C4 pass: for every data set and both arms, found, missed, false boxes and boxes on empty frames counted per frame are the old table's numbers.

## Does it depend on the test for "on a barrel"?

`sensitivity.md` recounts the measured places with the audit's two other rules as the test. Frames where the chosen test and "position" disagree: 0.

Files: `places.json` (every number), `per_barrel.csv` (every train barrel: its placement and its state for ours and for the vendor), `sensitivity.md`.
