# Does anything in the frame predict the working ranges? (leave one PLACE out; 2026-11-25, step 3)

`python barrels/experiments/2026-11-25_color/relation.py`. 14 ordinary slider-labelled conditions at 5 places (abp_gray, home_bathtile, home_glass, home_ottoman, uc_palewood); ranges from the sweep (detector version, around his values). Right = the prediction lies inside the held-out condition's range. Score = mean over places of the share of the place's conditions that are right. Lines are anchored at the centre of the training places, not at home.

| threshold | fixed | mean of others | best feature (kind) | its score | features beating fixed AND the mean |
|---|---:|---:|---|---:|---|
| orange_h_lo | 0.56 | 0.44 | blue_peak_h (line) | 0.72 | blue_peak_h (line), blue_peak_h (interval) |
| orange_h_hi | 0.34 | 0.40 | s_median (line) | 0.40 | none |
| orange_s_lo | 0.19 | 0.68 | s_share100 (line) | 0.82 | s_share100 (line), warmth (interval), v_mean (line), s_median (line), s_share100 (interval) ... |
| blue_h_lo | 0.45 | 0.50 | blue_top300 (interval) | 0.59 | blue_top300 (interval), s_median (interval), blue_peak_h (line), blue_top300 (line), s_share100 (interval) |
| blue_h_hi | 0.52 | 0.38 | orange_peak_h (line) | 0.63 | orange_peak_h (line), orange_peak_h (interval), orange_s_p90 (interval), v_mean (interval) |
| blue_s_lo | 0.45 | 0.40 | s_median (line) | 0.54 | s_median (line), s_median (interval), warmth (line), warmth (interval), light_warmth (line) |

Each condition's range and features: `relation.csv` (one row per threshold x held-out condition x predictor).
With 5 places a feature that 'beats' both baselines on one threshold is description, not proof: 11 features x 2 kinds = 22 tries per threshold, so a chance winner is expected.

## The conditions (range of each threshold; features)

| condition | place | orange_h_lo | orange_h_hi | orange_s_lo | blue_h_lo | blue_h_hi | blue_s_lo | light_warmth | blue_top300 | orange_peak150 |
|---|---|---|---|---|---|---|---|---|---|---|
| both_abpgray | abp_gray | -5..0 | 17..90 | 156..231* | 23..111 | 116..126* | 69..240* | -0.00 | 255 | 1 |
| lampcool6_bathtile | home_bathtile | 9..12 | 11..14 | 162..207 | 89..99 | 104..111 | 54..120 | 0.09 | 198 | 19 |
| lampcool6_glass | home_glass | 3..7 | 8..14 | 135..195 | 105..108 | 110..111 | 189..225 | -0.05 | 244 | 18 |
| lampcool6_ottoman | home_ottoman | -1..8 | 18..90 | 108..153 | 86..104 | 107..111 | 98..105 | 0.15 | 220 | 16 |
| lampmid3_bathtile | home_bathtile | 8..11 | 11..15 | 180..222* | 58..80 | 114..124 | 25..27 | 0.23 | 90 | 21 |
| lampmid3_glass | home_glass | 1..7 | 8..10 | 138..201 | 23..109 | 109..112 | 180..210 | -0.01 | 241 | 13 |
| lampmid6_bathtile | home_bathtile | 8..10 | 9..12 | 201..213 | 41..96 | 102..114 | 0..57 | 0.26 | 112 | 21 |
| lampmid6_glass | home_glass | 6..8 | 8..10 | 132..213 | 24..108 | 110..112 | 168..198 | 0.02 | 237 | 18 |
| lampmid6_ottoman | home_ottoman | -30..13 | 15..90 | 180..192 | 77..103 | 107..117 | 18..105 | 0.27 | 161 | 14 |
| lampwarm6_bathtile | home_bathtile | 7..7 | 8..10 | 186..198 | 58..68 | 120..156* | 0..12 | 0.40 | 9 | 20 |
| lampwarm6_glass | home_glass | 2..7 | 7..12* | 153..201 | 27..109 | 110..113 | 138..183 | 0.06 | 230 | 17 |
| lampwarm6_ottoman | home_ottoman | -30..12 | 17..90 | 165..180* | 37..101 | 110..154 | 0..18 | 0.34 | 89 | 18 |
| overheaddim_palewood | uc_palewood | -3..6 | 6..15* | 168..198 | 105..108 | 111..122 | 42..132 | -0.01 | 245 | 11 |
| window_glass | home_glass | -30..3* | 7..12 | 150..180 | 104..106 | 112..112 | 204..222 | -0.05 | 246 | 7 |

\* = the frames' ranges do not overlap (median of the ends shown).
