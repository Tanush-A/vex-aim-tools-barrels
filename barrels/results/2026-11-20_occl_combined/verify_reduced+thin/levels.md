# The damage levels: found / barrels (false boxes)

git da1412f; v2 rule; the 16 HOME hand masks (29 barrels), train frames only. Arms: `experiments/2026-11-20_occl_combined/comb_arms.py`. PREREG clause (c): at the judged levels the false boxes may not be above `stack`'s, with 5 seeds and with 20.

## Seeds 0 to 4 (as every earlier test: 145 barrels per damaged level)

| level | `reduced+thin` | `reduced+thin+verify` | `reduced+thin+verify2` |
|---|---|---|---|
| perfect masks **(judged)** | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) |
| white tables, typical **(judged)** | 145 / 145 (0) | 145 / 145 (0) | 145 / 145 (0) |
| white tables, bad day (reported; not more than double) | 135 / 145 (3) | 134 / 145 (3) | 134 / 145 (3) |
| bad day without the stripe patch **(judged)** | 144 / 145 (0) | 141 / 145 (0) | 141 / 145 (0) |
| light **(judged)** | 143 / 145 (0) | 129 / 145 (0) | 129 / 145 (0) |
| medium (reported; not more than double) | 102 / 145 (1) | 52 / 145 (0) | 52 / 145 (0) |
| heavy (report only) | 21 / 145 (0) | 5 / 145 (0) | 5 / 145 (0) |
| white tables, worst seen (report only) | 95 / 145 (2) | 41 / 145 (0) | 41 / 145 (0) |

## Seeds 0 to 19 (580 barrels per damaged level)

| level | `reduced+thin` | `reduced+thin+verify` | `reduced+thin+verify2` |
|---|---|---|---|
| perfect masks **(judged)** | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) |
| white tables, typical **(judged)** | 579 / 580 (0) | 579 / 580 (0) | 579 / 580 (0) |
| white tables, bad day (reported; not more than double) | 547 / 580 (5) | 536 / 580 (5) | 536 / 580 (5) |
| bad day without the stripe patch **(judged)** | 577 / 580 (0) | 563 / 580 (0) | 563 / 580 (0) |
| light **(judged)** | 574 / 580 (0) | 516 / 580 (0) | 516 / 580 (0) |
| medium (reported; not more than double) | 400 / 580 (3) | 209 / 580 (1) | 209 / 580 (1) |
| heavy (report only) | 89 / 580 (0) | 20 / 580 (0) | 20 / 580 (0) |
| white tables, worst seen (report only) | 378 / 580 (6) | 186 / 580 (1) | 186 / 580 (1) |

## What each level is

- `perfect masks`: no damage
- `white tables, typical`: erode_px 1, speckle 6
- `white tables, bad day`: top_highlight (0.16, 0.09), stripe_highlight 0.06, erode_px 1, dropout 0.005, speckle 20
- `bad day without the stripe patch`: top_highlight (0.16, 0.09), erode_px 1, dropout 0.005, speckle 20
- `light`: top_highlight (0.3, 0.2), erode_px 1, dropout 0.02, speckle 5
- `medium`: top_highlight (0.5, 0.3), stripe_highlight 0.15, stripe_breaks (1, 0.06), erode_px 1, dropout 0.05, speckle 15
- `heavy`: top_highlight (0.7, 0.4), stripe_highlight 0.3, stripe_breaks (2, 0.08), erode_px 2, dropout 0.1, speckle 30
- `white tables, worst seen`: top_highlight (0.41, 0.3), stripe_highlight 0.4, stripe_breaks (1, 0.03), erode_px 1, dropout 0.014, speckle 37

## The false boxes, by the rule that drew them (seeds 0 to 19)

| level | arm | stripe step | caps_behind | post_pairs | slices_behind | half_stripes | stripeless piece |
|---|---|---|---|---|---|---|---|
| white tables, bad day | `reduced+thin` | 5 | 0 | 0 | 0 | 0 | 0 |
| white tables, bad day | `reduced+thin+verify` | 5 | 0 | 0 | 0 | 0 | 0 |
| white tables, bad day | `reduced+thin+verify2` | 5 | 0 | 0 | 0 | 0 | 0 |
| medium | `reduced+thin` | 3 | 0 | 0 | 0 | 0 | 0 |
| medium | `reduced+thin+verify` | 1 | 0 | 0 | 0 | 0 | 0 |
| medium | `reduced+thin+verify2` | 1 | 0 | 0 | 0 | 0 | 0 |
| white tables, worst seen | `reduced+thin` | 5 | 1 | 0 | 0 | 0 | 0 |
| white tables, worst seen | `reduced+thin+verify` | 1 | 0 | 0 | 0 | 0 | 0 |
| white tables, worst seen | `reduced+thin+verify2` | 1 | 0 | 0 | 0 | 0 | 0 |

## Which test refused the missed barrels (seeds 0 to 4; the detector's reason log)

- perfect masks, `reduced+thin`: stripe_refused:height 1
- perfect masks, `reduced+thin+verify`: stripe_refused:height 1
- perfect masks, `reduced+thin+verify2`: stripe_refused:height 1
- white tables, bad day, `reduced+thin`: stripe_refused:height 5, misplaced 3, stripe_refused:side_unexplained 1, stripe_refused:outline_unknown 1
- white tables, bad day, `reduced+thin+verify`: stripe_refused:height 5, misplaced 3, stripe_refused:outline_unknown 2, stripe_refused:side_unexplained 1
- white tables, bad day, `reduced+thin+verify2`: stripe_refused:height 5, misplaced 3, stripe_refused:outline_unknown 2, stripe_refused:side_unexplained 1
- bad day without the stripe patch, `reduced+thin`: stripe_refused:height 1
- bad day without the stripe patch, `reduced+thin+verify`: stripe_refused:area 3, stripe_refused:height 1
- bad day without the stripe patch, `reduced+thin+verify2`: stripe_refused:area 3, stripe_refused:height 1
- light, `reduced+thin`: stripe_refused:height 2
- light, `reduced+thin+verify`: stripe_refused:height 13, stripe_refused:area 3
- light, `reduced+thin+verify2`: stripe_refused:height 13, stripe_refused:area 3
- medium, `reduced+thin`: stripe_refused:outline_unknown 14, stripe_refused:slice_not_full 10, stripe_refused:width 6, stripe_refused:area 5, stripe_refused:height 4, stripe_refused:side_unexplained 2, misplaced 2
- medium, `reduced+thin+verify`: stripe_refused:outline_unknown 18, stripe_refused:area 17, stripe_not_sandwiched 16, stripe_refused:width 15, stripe_refused:slice_not_full 11, stripe_refused:stripe_piece 9, stripe_refused:height 5, stripe_refused:side_unexplained 2
- medium, `reduced+thin+verify2`: stripe_refused:outline_unknown 18, stripe_refused:area 17, stripe_not_sandwiched 16, stripe_refused:width 15, stripe_refused:slice_not_full 11, stripe_refused:stripe_piece 9, stripe_refused:height 5, stripe_refused:side_unexplained 2
- heavy, `reduced+thin`: stripe_not_sandwiched 32, stripe_refused:area 26, stripe_refused:width 22, stripe_refused:slice_not_full 19, stripe_hidden 14, stripe_refused:height 7, stripe_refused:outline_unknown 3, not_segmented 1
- heavy, `reduced+thin+verify`: stripe_not_sandwiched 39, stripe_refused:width 27, stripe_refused:area 27, stripe_refused:slice_not_full 20, stripe_hidden 15, stripe_refused:height 7, stripe_refused:outline_unknown 3, stripe_refused:stripe_piece 1, not_segmented 1
- heavy, `reduced+thin+verify2`: stripe_not_sandwiched 39, stripe_refused:width 27, stripe_refused:area 27, stripe_refused:slice_not_full 20, stripe_hidden 15, stripe_refused:height 7, stripe_refused:outline_unknown 3, stripe_refused:stripe_piece 1, not_segmented 1
- white tables, worst seen, `reduced+thin`: stripe_refused:slice_not_full 17, stripe_refused:outline_unknown 15, stripe_refused:width 6, stripe_refused:area 5, stripe_refused:height 3, misplaced 3, stripe_refused:side_unexplained 1
- white tables, worst seen, `reduced+thin+verify`: stripe_refused:outline_unknown 26, stripe_not_sandwiched 18, stripe_refused:slice_not_full 17, stripe_refused:area 15, stripe_refused:width 15, stripe_refused:stripe_piece 8, stripe_refused:height 3, stripe_refused:side_unexplained 2
- white tables, worst seen, `reduced+thin+verify2`: stripe_refused:outline_unknown 26, stripe_not_sandwiched 18, stripe_refused:slice_not_full 17, stripe_refused:area 15, stripe_refused:width 15, stripe_refused:stripe_piece 8, stripe_refused:height 3, stripe_refused:side_unexplained 2

## Every false box at the judged levels (seeds 0 to 19)

| level | arm | frame | seed | color | box | drawn by | width / a barrel's | best overlap with a true box of its color | that barrel also missed |
|---|---|---|---|---|---|---|---|---|---|
