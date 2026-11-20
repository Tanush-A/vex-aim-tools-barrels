# The damage levels: found / barrels (false boxes)

git c0ab041; v2 rule; the 16 HOME hand masks (29 barrels), train frames only. Arms: `experiments/2026-11-20_occl_combined/comb_arms.py`. PREREG clause (c): at the judged levels the false boxes may not be above `stack`'s, with 5 seeds and with 20.

## Seeds 0 to 4 (as every earlier test: 145 barrels per damaged level)

| level | `before` | `stack` | `combined` | `combined+thin` | `combined+cover` |
|---|---|---|---|---|---|
| perfect masks **(judged)** | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) |
| white tables, typical **(judged)** | 140 / 145 (0) | 145 / 145 (0) | 145 / 145 (0) | 145 / 145 (0) | 145 / 145 (0) |
| white tables, bad day (reported; not more than double) | 115 / 145 (15) | 135 / 145 (3) | 136 / 145 (3) | 135 / 145 (3) | 139 / 145 (4) |
| bad day without the stripe patch **(judged)** | 140 / 145 (1) | 144 / 145 (0) | 144 / 145 (0) | 144 / 145 (0) | 144 / 145 (0) |
| light **(judged)** | 141 / 145 (0) | 143 / 145 (0) | 143 / 145 (0) | 143 / 145 (0) | 143 / 145 (0) |
| medium (reported; not more than double) | 64 / 145 (22) | 99 / 145 (1) | 115 / 145 (1) | 103 / 145 (1) | 125 / 145 (4) |
| heavy (report only) | 13 / 145 (2) | 21 / 145 (0) | 21 / 145 (0) | 21 / 145 (0) | 24 / 145 (0) |
| white tables, worst seen (report only) | 41 / 145 (21) | 84 / 145 (2) | 105 / 145 (2) | 98 / 145 (2) | 115 / 145 (6) |

## Seeds 0 to 19 (580 barrels per damaged level)

| level | `before` | `stack` | `combined` | `combined+thin` | `combined+cover` |
|---|---|---|---|---|---|
| perfect masks **(judged)** | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) | 28 / 29 (0) |
| white tables, typical **(judged)** | 560 / 580 (0) | 579 / 580 (0) | 579 / 580 (0) | 579 / 580 (0) | 579 / 580 (0) |
| white tables, bad day (reported; not more than double) | 454 / 580 (75) | 547 / 580 (5) | 555 / 580 (6) | 547 / 580 (5) | 560 / 580 (17) |
| bad day without the stripe patch **(judged)** | 563 / 580 (4) | 577 / 580 (0) | 577 / 580 (0) | 577 / 580 (0) | 577 / 580 (0) |
| light **(judged)** | 564 / 580 (5) | 574 / 580 (0) | 574 / 580 (0) | 574 / 580 (0) | 572 / 580 (2) |
| medium (reported; not more than double) | 242 / 580 (87) | 388 / 580 (3) | 444 / 580 (7) | 404 / 580 (4) | 481 / 580 (21) |
| heavy (report only) | 47 / 580 (5) | 89 / 580 (0) | 89 / 580 (0) | 89 / 580 (0) | 98 / 580 (0) |
| white tables, worst seen (report only) | 154 / 580 (72) | 337 / 580 (6) | 419 / 580 (10) | 387 / 580 (6) | 463 / 580 (17) |

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
| white tables, bad day | `before` | 75 | 0 | 0 | 0 | 0 | 0 |
| white tables, bad day | `stack` | 5 | 0 | 0 | 0 | 0 | 0 |
| white tables, bad day | `combined` | 5 | 0 | 0 | 1 | 0 | 0 |
| white tables, bad day | `combined+thin` | 5 | 0 | 0 | 0 | 0 | 0 |
| white tables, bad day | `combined+cover` | 17 | 0 | 0 | 0 | 0 | 0 |
| bad day without the stripe patch | `before` | 4 | 0 | 0 | 0 | 0 | 0 |
| light | `before` | 5 | 0 | 0 | 0 | 0 | 0 |
| light | `combined+cover` | 2 | 0 | 0 | 0 | 0 | 0 |
| medium | `before` | 86 | 1 | 0 | 0 | 0 | 0 |
| medium | `stack` | 3 | 0 | 0 | 0 | 0 | 0 |
| medium | `combined` | 3 | 0 | 0 | 4 | 0 | 0 |
| medium | `combined+thin` | 3 | 0 | 0 | 1 | 0 | 0 |
| medium | `combined+cover` | 21 | 0 | 0 | 0 | 0 | 0 |
| heavy | `before` | 5 | 0 | 0 | 0 | 0 | 0 |
| white tables, worst seen | `before` | 72 | 0 | 0 | 0 | 0 | 0 |
| white tables, worst seen | `stack` | 5 | 1 | 0 | 0 | 0 | 0 |
| white tables, worst seen | `combined` | 5 | 1 | 0 | 4 | 0 | 0 |
| white tables, worst seen | `combined+thin` | 5 | 1 | 0 | 0 | 0 | 0 |
| white tables, worst seen | `combined+cover` | 17 | 0 | 0 | 0 | 0 | 0 |

## Which test refused the missed barrels (seeds 0 to 4; the detector's reason log)

- perfect masks, `before`: stripe_refused:height 1
- perfect masks, `stack`: stripe_refused:height 1
- perfect masks, `combined`: stripe_refused:height 1
- perfect masks, `combined+thin`: stripe_refused:height 1
- perfect masks, `combined+cover`: stripe_refused:height 1
- white tables, typical, `before`: stripe_refused:height 5
- white tables, bad day, `before`: misplaced 15, stripe_refused:width 9, stripe_refused:height 6
- white tables, bad day, `stack`: stripe_refused:height 5, misplaced 3, stripe_refused:side_unexplained 1, stripe_refused:width 1
- white tables, bad day, `combined`: stripe_refused:height 5, misplaced 3, stripe_refused:side_unexplained 1
- white tables, bad day, `combined+thin`: stripe_refused:height 5, misplaced 3, stripe_refused:side_unexplained 1, stripe_refused:outline_unknown 1
- white tables, bad day, `combined+cover`: stripe_refused:height 5, misplaced 1
- bad day without the stripe patch, `before`: stripe_refused:height 4, misplaced 1
- bad day without the stripe patch, `stack`: stripe_refused:height 1
- bad day without the stripe patch, `combined`: stripe_refused:height 1
- bad day without the stripe patch, `combined+thin`: stripe_refused:height 1
- bad day without the stripe patch, `combined+cover`: stripe_refused:height 1
- light, `before`: stripe_refused:height 4
- light, `stack`: stripe_refused:height 2
- light, `combined`: stripe_refused:height 2
- light, `combined+thin`: stripe_refused:height 2
- light, `combined+cover`: stripe_refused:height 2
- medium, `before`: stripe_refused:width 50, misplaced 22, stripe_refused:area 5, stripe_refused:height 4
- medium, `stack`: stripe_refused:width 33, stripe_refused:area 5, stripe_refused:height 4, stripe_refused:side_unexplained 2, misplaced 2
- medium, `combined`: stripe_refused:width 20, stripe_refused:area 5, stripe_refused:side_unexplained 2, misplaced 2, stripe_refused:height 1
- medium, `combined+thin`: stripe_refused:outline_unknown 14, stripe_refused:slice_not_full 10, stripe_refused:width 5, stripe_refused:area 5, stripe_refused:height 4, stripe_refused:side_unexplained 2, misplaced 2
- medium, `combined+cover`: stripe_refused:slice_not_full 8, stripe_refused:width 5, stripe_refused:area 5, misplaced 2
- heavy, `before`: stripe_refused:width 50, stripe_not_sandwiched 32, stripe_refused:area 26, stripe_hidden 14, stripe_refused:height 7, misplaced 2, not_segmented 1
- heavy, `stack`: stripe_refused:width 44, stripe_not_sandwiched 32, stripe_refused:area 26, stripe_hidden 14, stripe_refused:height 7, not_segmented 1
- heavy, `combined`: stripe_refused:width 44, stripe_not_sandwiched 32, stripe_refused:area 26, stripe_hidden 14, stripe_refused:height 7, not_segmented 1
- heavy, `combined+thin`: stripe_not_sandwiched 32, stripe_refused:area 26, stripe_refused:width 22, stripe_refused:slice_not_full 19, stripe_hidden 14, stripe_refused:height 7, stripe_refused:outline_unknown 3, not_segmented 1
- heavy, `combined+cover`: stripe_not_sandwiched 32, stripe_refused:area 26, stripe_refused:width 22, stripe_refused:slice_not_full 19, stripe_hidden 14, stripe_refused:height 7, not_segmented 1
- white tables, worst seen, `before`: stripe_refused:width 75, misplaced 21, stripe_refused:area 5, stripe_refused:height 3
- white tables, worst seen, `stack`: stripe_refused:width 49, stripe_refused:area 5, stripe_refused:height 3, misplaced 3, stripe_refused:side_unexplained 1
- white tables, worst seen, `combined`: stripe_refused:width 29, stripe_refused:area 5, misplaced 3, stripe_refused:height 2, stripe_refused:side_unexplained 1
- white tables, worst seen, `combined+thin`: stripe_refused:slice_not_full 15, stripe_refused:outline_unknown 15, stripe_refused:width 5, stripe_refused:area 5, stripe_refused:height 3, misplaced 3, stripe_refused:side_unexplained 1
- white tables, worst seen, `combined+cover`: stripe_refused:slice_not_full 15, stripe_refused:width 5, stripe_refused:area 5, misplaced 4, stripe_refused:height 1

## Every false box at the judged levels (seeds 0 to 19)

| level | arm | frame | seed | color | box | drawn by | width / a barrel's | best overlap with a true box of its color | that barrel also missed |
|---|---|---|---|---|---|---|---|---|---|
| bad day without the stripe patch | `before` | cluster_01 | 4 | orange | [348, 111, 390, 162] | stripe step | 0.94 | 0.5 | yes |
| bad day without the stripe patch | `before` | cluster_01 | 7 | orange | [348, 111, 390, 162] | stripe step | 0.94 | 0.5 | yes |
| bad day without the stripe patch | `before` | cluster_01 | 8 | orange | [348, 111, 390, 162] | stripe step | 0.94 | 0.5 | yes |
| bad day without the stripe patch | `before` | cluster_01 | 18 | orange | [348, 111, 390, 162] | stripe step | 0.94 | 0.5 | yes |
| light | `before` | cluster_01 | 6 | orange | [348, 111, 390, 162] | stripe step | 0.94 | 0.5 | yes |
| light | `combined+cover` | occl_02 | 7 | orange | [362, 118, 442, 152] | stripe step | 2.04 | 0.49 | yes |
| light | `before` | cluster_01 | 9 | orange | [348, 111, 390, 162] | stripe step | 0.94 | 0.5 | yes |
| light | `combined+cover` | occl_02 | 12 | orange | [362, 118, 442, 152] | stripe step | 2.04 | 0.49 | yes |
| light | `before` | cluster_01 | 16 | orange | [348, 111, 390, 162] | stripe step | 0.94 | 0.5 | yes |
| light | `before` | cluster_01 | 17 | orange | [348, 111, 390, 162] | stripe step | 0.94 | 0.5 | yes |
| light | `before` | cluster_01 | 19 | orange | [348, 111, 390, 162] | stripe step | 0.94 | 0.5 | yes |
