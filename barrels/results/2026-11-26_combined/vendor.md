# F. Against the vendor detector: `mask_union` beside today's detector, each winner and the vendor

The six places with vendor files: 117 frames, 243 barrels counted per frame, 108 placements (physical barrels) in 54 arrangements, 15 lights. The accounting of `tools/report.py --vendor --places` (`counting.py`): found = the strict rule, every placement once (per frame in brackets). Ours = the held-out boxes of the judged run (leave one place out). The vendor = the boxes the robot saved with each frame. **Train frames, and our methods were shaped on them; the vendor was not.** Made by `analysis.py vendor`.

### Found (strict), placements (per frame)

| place | placements (per frame) | today | `nearmiss` | `selfcal` | `mask_union` | vendor |
|---|---|---|---|---|---|---|
| abp_gray | 16 (16) | 10.0 (10) | 12.0 (12) | 15.0 (15) | 15.0 (15) | 16.0 (16) |
| home_bathtile | 15 (60) | 4.0 (16) | 9.0 (36) | 9.8 (39) | 11.0 (44) | 7.0 (28) |
| home_glass | 15 (75) | 14.8 (74) | 14.8 (74) | 14.8 (74) | 14.8 (74) | 12.0 (60) |
| home_ottoman | 15 (45) | 3.0 (9) | 7.7 (23) | 6.0 (18) | 8.0 (24) | 12.3 (37) |
| uc_palewood | 15 (15) | 13.0 (13) | 13.0 (13) | 13.0 (13) | 13.0 (13) | 12.0 (12) |
| abp_white | 32 (32) | 26.0 (26) | 28.0 (28) | 26.0 (26) | 28.0 (28) | 24.0 (24) |
| **six places** | 108 (243) | 70.8 (148) | 84.5 (186) | 84.5 (185) | 89.8 (198) | 83.3 (177) |

### Found with the box off (a same-color box is on the barrel and fails the strict rule)

| place | placements (per frame) | today | `nearmiss` | `selfcal` | `mask_union` | vendor |
|---|---|---|---|---|---|---|
| abp_gray | 16 (16) | 1.0 (1) | 2.0 (2) | 1.0 (1) | 1.0 (1) | 0.0 (0) |
| home_bathtile | 15 (60) | 0.0 (0) | 0.0 (0) | 0.2 (1) | 0.2 (1) | 0.8 (3) |
| home_glass | 15 (75) | 0.2 (1) | 0.2 (1) | 0.2 (1) | 0.2 (1) | 2.8 (14) |
| home_ottoman | 15 (45) | 0.0 (0) | 0.3 (1) | 0.0 (0) | 0.3 (1) | 0.7 (2) |
| uc_palewood | 15 (15) | 0.0 (0) | 0.0 (0) | 0.0 (0) | 0.0 (0) | 1.0 (1) |
| abp_white | 32 (32) | 0.0 (0) | 0.0 (0) | 0.0 (0) | 0.0 (0) | 3.0 (3) |
| **six places** | 108 (243) | 1.2 (2) | 2.5 (4) | 1.4 (3) | 1.8 (4) | 8.2 (23) |

### Missed (no box of its color on it)

| place | placements (per frame) | today | `nearmiss` | `selfcal` | `mask_union` | vendor |
|---|---|---|---|---|---|---|
| abp_gray | 16 (16) | 5.0 (5) | 2.0 (2) | 0.0 (0) | 0.0 (0) | 0.0 (0) |
| home_bathtile | 15 (60) | 11.0 (44) | 6.0 (24) | 5.0 (20) | 3.8 (15) | 7.2 (29) |
| home_glass | 15 (75) | 0.0 (0) | 0.0 (0) | 0.0 (0) | 0.0 (0) | 0.2 (1) |
| home_ottoman | 15 (45) | 12.0 (36) | 7.0 (21) | 9.0 (27) | 6.7 (20) | 2.0 (6) |
| uc_palewood | 15 (15) | 2.0 (2) | 2.0 (2) | 2.0 (2) | 2.0 (2) | 2.0 (2) |
| abp_white | 32 (32) | 6.0 (6) | 4.0 (4) | 6.0 (6) | 4.0 (4) | 5.0 (5) |
| **six places** | 108 (243) | 36.0 (93) | 21.0 (53) | 22.0 (55) | 16.4 (41) | 16.5 (43) |

### Boxes on nothing, per frame (of them on empty frames)

| place | placements (per frame) | today | `nearmiss` | `selfcal` | `mask_union` | vendor |
|---|---|---|---|---|---|---|
| abp_gray | 16 (16) | 0 (0) | 0 (0) | 0 (0) | 0 (0) | 0 (0) |
| home_bathtile | 15 (60) | 0 (0) | 0 (0) | 0 (0) | 0 (0) | 0 (0) |
| home_glass | 15 (75) | 3 (0) | 7 (2) | 3 (0) | 7 (2) | 6 (6) |
| home_ottoman | 15 (45) | 1 (0) | 1 (0) | 1 (0) | 1 (0) | 0 (0) |
| uc_palewood | 15 (15) | 1 (0) | 1 (0) | 1 (0) | 1 (0) | 0 (0) |
| abp_white | 32 (32) | 0 (0) | 0 (0) | 0 (0) | 0 (0) | 1 (1) |
| **six places** | 108 (243) | 5 (0) | 9 (2) | 5 (0) | 9 (2) | 7 (7) |

### Boxes not on their barrel, once per arrangement (on nothing + second box + wrong color; per frame in brackets)

| place | placements (per frame) | today | `nearmiss` | `selfcal` | `mask_union` | vendor |
|---|---|---|---|---|---|---|
| abp_gray | 16 (16) | 0.00 (0+0+0) | 0.00 (0+0+0) | 0.00 (0+0+0) | 0.00 (0+0+0) | 0.00 (0+0+0) |
| home_bathtile | 15 (60) | 0.00 (0+0+0) | 0.50 (0+1+1) | 0.25 (0+1+0) | 0.25 (0+1+0) | 0.00 (0+0+0) |
| home_glass | 15 (75) | 0.60 (3+0+0) | 1.40 (7+0+0) | 0.60 (3+0+0) | 1.40 (7+0+0) | 2.00 (6+0+0) |
| home_ottoman | 15 (45) | 0.33 (1+0+0) | 0.67 (1+1+0) | 0.33 (1+0+0) | 0.67 (1+1+0) | 0.00 (0+0+0) |
| uc_palewood | 15 (15) | 1.00 (1+0+0) | 1.00 (1+0+0) | 1.00 (1+0+0) | 1.00 (1+0+0) | 0.00 (0+0+0) |
| abp_white | 32 (32) | 0.00 (0+0+0) | 0.00 (0+0+0) | 0.00 (0+0+0) | 0.00 (0+0+0) | 1.00 (1+0+0) |
| **six places** | 108 (243) | 1.93 (5+0+0) | 3.57 (9+2+1) | 2.18 (5+1+0) | 3.32 (9+2+0) | 3.00 (7+0+0) |

### In one line each

- Total found: today 70.8 (148), `nearmiss` 84.5 (186), `selfcal` 84.5 (185), `mask_union` 89.8 (198), vendor 83.3 (177) of 108 (243).
- `mask_union` against the vendor: +6.5 placements (+21 per frame). On a barrel at all (found + box off): 91.6 against 91.5.
- Places where `mask_union` finds fewer than the vendor: abp_gray (15.0 against 16.0); home_ottoman (8.0 against 12.3).
- Places where it finds more: home_bathtile (11.0 against 7.0); home_glass (14.8 against 12.0); uc_palewood (13.0 against 12.0); abp_white (28.0 against 24.0).
- The two white tables without vendor files (home, campus; 64 placements) are not in this table. There the vendor is ASSUMED to find every barrel (Tanush, 2026-11-26); every candidate here finds what today's detector finds there (63.0 of 64).

