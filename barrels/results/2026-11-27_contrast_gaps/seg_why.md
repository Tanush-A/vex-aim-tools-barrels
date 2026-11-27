# Why the fixed colors miss parts of these barrels (Tanush's question)

Fixed colors: orange hue 3-13 with S >= 140, blue hue 103-119 with S >= 113, and V (brightest channel) >= 40. Per barrel the body (the wall above the stripe) and the stripe, middle 60 % of the columns, rows from the geometry of the hand box's bottom row. 'painted' = the fixed colors paint it its right color; then the share stopped first by V, by the hue range, by the saturation floor; 'contrast' = the share the contrast stage paints its right color on top.

| frame | barrel | part | should be | median H | median S | median V | painted | stopped by V | by hue | by S | contrast paints |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lampwarm6_bathtile_core_01 | 0 orange (223, 115, 270, 165) | body | orange | 8 | 221 | 210 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| lampwarm6_bathtile_core_01 | 0 orange (223, 115, 270, 165) | stripe | blue | 32 | 39 | 52 | 0.00 | 0.00 | 1.00 | 0.00 | 1.00 |
| lampwarm6_bathtile_core_01 | 1 orange (328, 106, 358, 138) | body | orange | 9 | 225 | 211 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| lampwarm6_bathtile_core_01 | 1 orange (328, 106, 358, 138) | stripe | blue | 20 | 83 | 61 | 0.00 | 0.00 | 1.00 | 0.00 | 0.80 |
| lampwarm6_bathtile_core_01 | 2 blue (374, 140, 457, 226) | body | blue | 55 | 32 | 51 | 0.00 | 0.00 | 1.00 | 0.00 | 0.99 |
| lampwarm6_bathtile_core_01 | 2 blue (374, 140, 457, 226) | stripe | orange | 8 | 220 | 174 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| lampwarm6_bathtile_core_01 | 3 blue (475, 110, 513, 147) | body | blue | 43 | 48 | 58 | 0.00 | 0.00 | 1.00 | 0.00 | 1.00 |
| lampwarm6_bathtile_core_01 | 3 blue (475, 110, 513, 147) | stripe | orange | 9 | 220 | 168 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| lampcool6_ottoman_core_01 | 0 blue (77, 133, 155, 208) | body | blue | 104 | 164 | 128 | 0.78 | 0.00 | 0.21 | 0.01 | 0.21 |
| lampcool6_ottoman_core_01 | 0 blue (77, 133, 155, 208) | stripe | orange | 17 | 208 | 134 | 0.05 | 0.00 | 0.93 | 0.02 | 0.88 |
| lampcool6_ottoman_core_01 | 1 orange (155, 166, 280, 311) | body | orange | 17 | 208 | 147 | 0.01 | 0.00 | 0.96 | 0.02 | 0.93 |
| lampcool6_ottoman_core_01 | 1 orange (155, 166, 280, 311) | stripe | blue | 105 | 197 | 94 | 0.75 | 0.04 | 0.19 | 0.02 | 0.03 |
| lampcool6_ottoman_core_01 | 2 blue (273, 113, 316, 160) | body | blue | 103 | 174 | 123 | 0.66 | 0.00 | 0.34 | 0.00 | 0.00 |
| lampcool6_ottoman_core_01 | 2 blue (273, 113, 316, 160) | stripe | orange | 16 | 200 | 129 | 0.15 | 0.00 | 0.85 | 0.00 | 0.00 |
| lampcool6_ottoman_core_01 | 3 orange (413, 126, 479, 190) | body | orange | 16 | 199 | 131 | 0.12 | 0.00 | 0.88 | 0.00 | 0.87 |
| lampcool6_ottoman_core_01 | 3 orange (413, 126, 479, 190) | stripe | blue | 103 | 152 | 63 | 0.52 | 0.39 | 0.07 | 0.03 | 0.05 |
| lampmid6_ottoman_close_01 | 0 orange (218, 232, 470, 480) | body | orange | 16 | 204 | 230 | 0.09 | 0.00 | 0.91 | 0.00 | 0.00 |
| lampmid6_ottoman_close_01 | 0 orange (218, 232, 470, 480) | stripe | blue | 16 | 197 | 204 | 0.00 | 0.00 | 0.99 | 0.01 | 0.00 |
