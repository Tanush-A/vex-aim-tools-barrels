# Hue x saturation histograms (TODO 8)

Adopted hs model `eb863d84`: orange hue 3 to 13, S >= 140; blue hue 103 to 119, S >= 113; pixels below row 50 with V >= 40. Train frames only. Hue in OpenCV units (0-179; a negative hue is below the wrap: -3 = 177).

## 1. Where the body colors sit, and what the fixed model does with them

`bright` = share of the box-core pixels with V >= 40. `model` = share of the bright body pixels the fixed model labels as that class.

| set | frames | mean V | orange hue 50 (5 to 95) | orange S 50 (5 to 95) | orange bright % | orange model % | blue hue 50 (5 to 95) | blue S 50 (5 to 95) | blue bright % | blue model % |
|---|---|---|---|---|---|---|---|---|---|---|
| HOME (masks) | 16 | 139 | 9 (4 to 11) | 213 (141 to 229) | 100 | 93 | 110 (104 to 163) | 225 (65 to 247) | 99 | 80 |
| HOME | 16 | 139 | 9 (6 to 10) | 217 (191 to 227) | 100 | 99 | 110 (105 to 114) | 231 (193 to 245) | 100 | 97 |
| CAMPUS | 21 | 144 | 9 (6 to 11) | 217 (179 to 227) | 100 | 98 | 106 (104 to 110) | 217 (151 to 235) | 100 | 98 |
| BLACK | 10 | 75 | 14 (11 to 19) | 197 (133 to 219) | 99 | 43 | 99 (90 to 105) | 149 (47 to 205) | 100 | 16 |
| lampwarm1_wood | 10 | 24 | 12 (8 to 15) | 215 (175 to 241) | 30 | 89 | too dark | too dark | 1 | 0 |
| lampwarm3_wood | 10 | 145 | 13 (10 to 17) | 207 (63 to 221) | 100 | 46 | 105 (95 to 111) | 97 (27 to 147) | 82 | 43 |
| lampwarm6_wood | 10 | 195 | 11 (8 to 19) | 215 (45 to 225) | 100 | 69 | 106 (95 to 114) | 111 (43 to 163) | 100 | 46 |
| lampmid1_wood | 10 | 22 | 11 (6 to 14) | 213 (171 to 241) | 24 | 93 | too dark | too dark | 1 | 0 |
| lampmid3_wood | 10 | 141 | 13 (9 to 16) | 199 (101 to 215) | 100 | 48 | 103 (98 to 109) | 103 (51 to 201) | 85 | 33 |
| lampmid6_wood | 10 | 189 | 12 (8 to 18) | 215 (105 to 225) | 100 | 73 | 101 (97 to 109) | 133 (81 to 225) | 100 | 30 |
| lampcool1_wood | 10 | 22 | 12 (8 to 15) | 207 (167 to 241) | 18 | 87 | too dark | too dark | 1 | 0 |
| lampcool3_wood | 10 | 123 | 13 (9 to 17) | 203 (117 to 221) | 100 | 46 | 103 (100 to 109) | 161 (73 to 225) | 95 | 48 |
| lampcool6_wood | 10 | 171 | 13 (9 to 19) | 213 (149 to 223) | 100 | 52 | 101 (98 to 108) | 195 (87 to 227) | 100 | 31 |
| WOOD, all 9 lights | 90 | 115 | 13 (8 to 17) | 209 (87 to 225) | 75 | 60 | 102 (94 to 110) | 143 (37 to 223) | 63 | 36 |

## 2. Everything that is not a barrel (table, clutter, robot parts; below the horizon row)

`flood` = share of all those pixels the fixed model paints as a barrel color.

| set | bright % | hue 50 (5 to 95) | S 50 (5 to 95) | flood orange % | flood blue % |
|---|---|---|---|---|---|
| HOME (masks) | 99 | 57 (0 to 116) | 31 (7 to 95) | 0.1 | 0.0 |
| HOME | 99 | 57 (0 to 116) | 31 (7 to 95) | 0.1 | 0.0 |
| CAMPUS | 91 | 66 (4 to 111) | 19 (5 to 59) | 0.3 | 0.3 |
| BLACK | 61 | 13 (0 to 83) | 13 (1 to 55) | 0.1 | 0.1 |
| lampwarm1_wood | 9 | 21 (0 to 33) | 105 (21 to 199) | 0.2 | 0.0 |
| lampwarm3_wood | 98 | 18 (13 to 23) | 181 (83 to 209) | 2.0 | 0.0 |
| lampwarm6_wood | 99 | 17 (13 to 23) | 207 (117 to 217) | 2.5 | 0.0 |
| lampmid1_wood | 7 | 21 (0 to 36) | 85 (1 to 199) | 0.2 | 0.0 |
| lampmid3_wood | 98 | 19 (12 to 24) | 151 (59 to 187) | 0.8 | 0.0 |
| lampmid6_wood | 99 | 19 (13 to 25) | 189 (85 to 211) | 1.6 | 0.0 |
| lampcool1_wood | 7 | 26 (13 to 103) | 67 (31 to 191) | 0.1 | 0.0 |
| lampcool3_wood | 96 | 22 (14 to 37) | 133 (35 to 175) | 0.3 | 0.0 |
| lampcool6_wood | 98 | 22 (15 to 40) | 147 (37 to 189) | 0.3 | 0.0 |
| WOOD, all 9 lights | 68 | 19 (13 to 30) | 161 (47 to 211) | 0.9 | 0.0 |

## 3. The thresholds the model's own recipe would give if it were fit on each set

Same recipe as the adopted model (S floor = 5th percentile of the orange body's S, 15th of the blue; hue sector = 5th to 95th percentile above the floor, widened by 2), but on this set's body pixels. `flood` = share of the non-barrel pixels of the same set inside that box. This is a description of where the colors are, not a model anyone runs.

| set | orange hue | orange S floor | orange flood % | blue hue | blue S floor | blue flood % |
|---|---|---|---|---|---|---|
| HOME (masks) | 3 to 13 | 140 | 0.1 | 104 to 123 | 112 | 0.0 |
| HOME | 4 to 12 | 190 | 0.0 | 104 to 115 | 222 | 0.0 |
| CAMPUS | 5 to 13 | 178 | 0.2 | 102 to 111 | 190 | 0.1 |
| BLACK | 9 to 19 | 132 | 0.2 | 90 to 107 | 82 | 0.0 |
| lampwarm1_wood | 6 to 17 | 174 | 0.7 | too dark | too dark | too dark |
| lampwarm3_wood | 8 to 18 | 62 | 47.2 | 93 to 113 | 34 | 0.0 |
| lampwarm6_wood | 6 to 20 | 44 | 86.7 | 94 to 115 | 58 | 0.0 |
| lampmid1_wood | 4 to 16 | 170 | 0.5 | too dark | too dark | too dark |
| lampmid3_wood | 8 to 18 | 100 | 36.0 | 96 to 110 | 78 | 0.0 |
| lampmid6_wood | 6 to 20 | 104 | 73.0 | 95 to 111 | 100 | 0.0 |
| lampcool1_wood | 6 to 17 | 166 | 0.5 | too dark | too dark | too dark |
| lampcool3_wood | 8 to 18 | 116 | 6.4 | 98 to 111 | 126 | 0.0 |
| lampcool6_wood | 8 to 21 | 148 | 28.0 | 96 to 109 | 160 | 0.0 |
| WOOD, all 9 lights | 6 to 19 | 86 | 31.9 | 96 to 111 | 74 | 0.0 |

## 4. The most any H x S lookup could keep at 1 % flood

Bins 36 x 32 (H x S) and 36 x 32 x 8 (with V). The lookup is built on the very frames it is scored on, so this is a ceiling, not a result.

| set | orange: fixed model % (its flood %) | orange: best H x S % | orange: best H x S x V % | blue: fixed model % (its flood %) | blue: best H x S % | blue: best H x S x V % |
|---|---|---|---|---|---|---|
| HOME (masks) | 93 (0.1) | 100 | 100 | 80 (0.0) | 92 | 98 |
| HOME | 99 (0.1) | 100 | 100 | 97 (0.0) | 100 | 100 |
| CAMPUS | 98 (0.3) | 100 | 100 | 98 (0.3) | 100 | 100 |
| BLACK | 43 (0.1) | 99 | 100 | 16 (0.1) | 100 | 100 |
| lampwarm1_wood | 89 (0.2) | 100 | 100 | 0 (0.0) | too dark | too dark |
| lampwarm3_wood | 46 (2.0) | 66 | 80 | 43 (0.0) | 100 | 100 |
| lampwarm6_wood | 69 (2.5) | 72 | 76 | 46 (0.0) | 100 | 100 |
| lampmid1_wood | 93 (0.2) | 100 | 100 | 0 (0.0) | too dark | too dark |
| lampmid3_wood | 48 (0.8) | 82 | 89 | 33 (0.0) | 100 | 100 |
| lampmid6_wood | 73 (1.6) | 80 | 90 | 30 (0.0) | 100 | 100 |
| lampcool1_wood | 87 (0.1) | 100 | 100 | 0 (0.0) | too dark | too dark |
| lampcool3_wood | 46 (0.3) | 89 | 95 | 48 (0.0) | 100 | 100 |
| lampcool6_wood | 52 (0.3) | 91 | 97 | 31 (0.0) | 99 | 100 |
| WOOD, all 9 lights | 60 (0.9) | 73 | 78 | 36 (0.0) | 100 | 100 |

## 5. Transfer, orange: the best H x S lookup of the row's set applied to the column's set

Each cell: body kept % / non-barrel painted %. The diagonal is section 4.

| from \ to | HOME | CAMPUS | BLACK | warm1 | warm3 | warm6 | mid1 | mid3 | mid6 | cool1 | cool3 | cool6 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HOME | 100 / 0.6 | 100 / 1.1 | 79 / 2.1 | 95 / 1.8 | 82 / 29.3 | 87 / 48.4 | 98 / 1.3 | 83 / 34.8 | 90 / 25.9 | 95 / 0.7 | 81 / 14.3 | 85 / 7.8 |
| CAMPUS | 100 / 0.5 | 100 / 1.0 | 95 / 2.1 | 100 / 2.9 | 95 / 68.8 | 88 / 78.1 | 100 / 1.7 | 98 / 60.8 | 95 / 60.7 | 99 / 0.9 | 98 / 21.0 | 95 / 12.6 |
| BLACK | 89 / 1.1 | 90 / 0.7 | 99 / 1.0 | 95 / 6.3 | 93 / 92.3 | 84 / 95.5 | 92 / 4.2 | 96 / 89.1 | 95 / 93.4 | 95 / 3.0 | 97 / 74.3 | 98 / 76.2 |
| warm1 | 99 / 0.1 | 99 / 0.4 | 90 / 0.2 | 100 / 1.0 | 90 / 56.1 | 82 / 72.8 | 99 / 0.8 | 93 / 32.9 | 91 / 50.9 | 99 / 0.7 | 92 / 6.7 | 92 / 6.4 |
| warm3 | 46 / 4.9 | 54 / 2.5 | 55 / 2.3 | 83 / 0.2 | 66 / 0.9 | 60 / 7.1 | 79 / 0.2 | 59 / 0.4 | 70 / 1.5 | 74 / 0.1 | 57 / 0.5 | 67 / 0.6 |
| warm6 | 93 / 3.8 | 89 / 5.9 | 17 / 5.0 | 62 / 0.1 | 36 / 0.5 | 72 / 1.0 | 60 / 0.1 | 13 / 0.9 | 71 / 0.7 | 46 / 0.0 | 28 / 1.2 | 55 / 1.3 |
| mid1 | 99 / 0.2 | 99 / 0.4 | 92 / 0.3 | 100 / 1.1 | 91 / 59.9 | 82 / 73.9 | 100 / 0.8 | 93 / 42.9 | 92 / 52.9 | 100 / 0.7 | 94 / 8.1 | 92 / 8.1 |
| mid3 | 47 / 0.2 | 55 / 1.9 | 75 / 0.6 | 86 / 0.5 | 86 / 16.1 | 66 / 61.0 | 82 / 0.4 | 82 / 0.9 | 80 / 26.4 | 87 / 0.3 | 80 / 0.5 | 88 / 1.0 |
| mid6 | 97 / 3.5 | 97 / 3.4 | 45 / 23.3 | 83 / 0.6 | 59 / 1.1 | 73 / 2.2 | 85 / 0.6 | 49 / 1.3 | 80 / 1.0 | 69 / 0.2 | 52 / 0.8 | 65 / 0.7 |
| cool1 | 98 / 0.1 | 99 / 0.4 | 92 / 0.2 | 100 / 1.0 | 90 / 59.0 | 82 / 73.7 | 99 / 0.8 | 93 / 40.5 | 91 / 52.6 | 100 / 0.7 | 94 / 8.0 | 92 / 7.7 |
| cool3 | 97 / 0.1 | 98 / 0.4 | 85 / 0.4 | 96 / 0.8 | 90 / 39.2 | 81 / 68.0 | 94 / 0.7 | 90 / 5.4 | 91 / 42.3 | 95 / 0.5 | 89 / 1.0 | 92 / 1.8 |
| cool6 | 98 / 0.1 | 98 / 0.4 | 74 / 0.5 | 97 / 0.7 | 87 / 17.6 | 81 / 61.7 | 96 / 0.5 | 83 / 3.2 | 91 / 28.1 | 95 / 0.3 | 81 / 0.7 | 91 / 1.0 |

## 5. Transfer, blue: the best H x S lookup of the row's set applied to the column's set

Each cell: body kept % / non-barrel painted %. The diagonal is section 4.

| from \ to | HOME | CAMPUS | BLACK | warm1 | warm3 | warm6 | mid1 | mid3 | mid6 | cool1 | cool3 | cool6 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HOME | 100 / 0.8 | 99 / 0.6 | 58 / 0.4 | 0 / 0.0 | 51 / 0.0 | 53 / 0.0 | 0 / 0.0 | 38 / 0.0 | 65 / 0.0 | 0 / 0.1 | 81 / 0.2 | 83 / 0.3 |
| CAMPUS | 99 / 10.5 | 100 / 0.9 | 49 / 0.6 | 0 / 0.0 | 60 / 0.0 | 84 / 0.0 | 0 / 0.0 | 74 / 0.0 | 65 / 0.0 | 0 / 0.0 | 92 / 0.2 | 85 / 0.3 |
| BLACK | 27 / 21.3 | 89 / 15.8 | 100 / 1.0 | 0 / 0.0 | 97 / 0.0 | 94 / 0.0 | 0 / 0.0 | 98 / 0.1 | 97 / 0.0 | 0 / 0.7 | 97 / 1.4 | 99 / 1.7 |
| warm1 | 0 / 0.1 | 0 / 0.4 | 0 / 0.4 | 99 / 0.9 | 0 / 38.9 | 0 / 72.0 | 93 / 0.9 | 0 / 18.0 | 0 / 45.8 | 89 / 0.5 | 0 / 6.3 | 0 / 5.1 |
| warm3 | 4 / 21.5 | 30 / 14.8 | 62 / 1.0 | 0 / 0.0 | 100 / 0.1 | 97 / 0.0 | 0 / 0.0 | 96 / 0.1 | 79 / 0.1 | 0 / 0.7 | 87 / 1.3 | 53 / 1.6 |
| warm6 | 3 / 24.3 | 20 / 16.5 | 79 / 1.3 | 0 / 0.0 | 100 / 0.1 | 100 / 0.0 | 0 / 0.0 | 95 / 0.1 | 80 / 0.1 | 0 / 0.7 | 72 / 1.4 | 46 / 1.7 |
| mid1 | 0 / 0.1 | 0 / 0.4 | 0 / 0.3 | 91 / 0.8 | 0 / 27.8 | 0 / 31.8 | 100 / 0.6 | 0 / 4.8 | 0 / 30.5 | 93 / 0.4 | 0 / 1.3 | 0 / 1.5 |
| mid3 | 47 / 22.3 | 96 / 15.6 | 92 / 1.0 | 0 / 0.0 | 99 / 0.1 | 98 / 0.0 | 0 / 0.0 | 100 / 0.1 | 100 / 0.1 | 0 / 0.7 | 100 / 1.4 | 94 / 1.7 |
| mid6 | 66 / 25.1 | 97 / 18.8 | 99 / 1.2 | 0 / 0.0 | 98 / 0.1 | 96 / 0.0 | 0 / 0.0 | 100 / 0.1 | 100 / 0.1 | 0 / 0.7 | 100 / 1.4 | 100 / 1.7 |
| cool1 | 0 / 0.2 | 0 / 0.4 | 0 / 0.3 | 92 / 0.6 | 0 / 8.9 | 0 / 40.9 | 96 / 0.5 | 0 / 4.4 | 0 / 13.1 | 100 / 0.2 | 0 / 1.0 | 0 / 1.1 |
| cool3 | 53 / 19.2 | 96 / 6.8 | 91 / 0.7 | 0 / 0.0 | 89 / 0.1 | 94 / 0.0 | 0 / 0.0 | 98 / 0.1 | 99 / 0.0 | 0 / 0.7 | 100 / 0.9 | 99 / 1.3 |
| cool6 | 48 / 18.8 | 96 / 7.9 | 90 / 0.6 | 0 / 0.0 | 72 / 0.0 | 93 / 0.0 | 0 / 0.0 | 97 / 0.0 | 99 / 0.0 | 0 / 0.6 | 99 / 0.9 | 99 / 0.9 |
