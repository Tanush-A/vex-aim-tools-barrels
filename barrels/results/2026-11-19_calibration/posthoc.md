# After the failed validation: is the ruler session like the other sessions? (post hoc)

git 05bdaa8. Written after `validation.md` was seen. It decides nothing. Train frames and ruler frames only.

## 1. No camera model: boxes whose top edge is on the same row

For each whole box of the ruler set: the hand-drawn boxes of each train set whose top row is within 4 px of it (unoccluded, untruncated boxes, as in the size check). Height and width in px; `n` = how many boxes.

| ruler frame | mm | top row | ruler box: height | width | HOME: n, median height, width | CAMPUS: n, median height, width | BLACK: n, median height, width | WOOD: n, median height, width |
|---|---|---|---|---|---|---|---|---|
| 07 | 30 | 214 | 246 | 200 | - | - | - | - |
| 08 | 50 | 181 | 175 | 143 | - | 1, 175, 148 | - | - |
| 09 | 100 | 147 | 97 | 85 | 1, 92, 88 | 3, 98, 104 | - | 18, 94, 85 |
| 10 | 150 | 132 | 67 | 61 | - | 7, 71, 67 | 4, 76, 69 | 45, 65, 59 |
| 11 | 200 | 123 | 53 | 48 | 10, 54, 50 | 9, 56, 53 | 2, 61, 64 | 36, 58, 52 |
| 12 | 300 | 113 | 35 | 34 | - | 7, 40, 37 | 4, 45, 46 | 18, 35, 34 |

Train box / ruler box at the same top row, averaged over the ruler frames with at least 3 such boxes:

| set | ruler frames used | height ratio | width ratio |
|---|---|---|---|
| HOME | 1 | 1.02 | 1.05 |
| CAMPUS | 4 | 1.07 | 1.13 |
| BLACK | 2 | 1.21 | 1.23 |
| WOOD | 4 | 1.01 | 1.01 |

## 2. With the model: the tilt each set would need

f 400. For each set, the tilt at which the median error of the bottom inferred from the top row is zero, over its far and mid boxes (drawn width under 60 px), for the two camera heights. The horizon row follows from the tilt.

| boxes | n | camera height 43.47: tilt | horizon row | camera height 40.2: tilt | horizon row |
|---|---|---|---|---|---|
| ruler set (150, 200, 300 mm) | 3 | 21.44° | 83 | 20.50° | 90 |
| HOME | 15 | 21.82° | 80 | 21.02° | 86 |
| CAMPUS | 16 | 21.64° | 81 | 20.86° | 88 |
| BLACK | 6 | 21.92° | 79 | 21.16° | 85 |
| WOOD | 72 | 21.56° | 82 | 20.68° | 89 |
| HOME and CAMPUS together | 31 | 21.68° | 81 | 20.96° | 87 |

The wood ladder is 8 scenes under 9 lamp settings with the boxes copied between settings, so its 72 boxes are 8 independent ones.

## Reading

- At the same top row the wood boxes (same table and day as the ruler set) are the size of the ruler boxes; campus and black boxes are larger. The sessions do not share one geometry to better than a few percent, or the boxes were not drawn the same way.
- Every set, the ruler set included, wants a tilt within about 0.3° of the others once the camera height is fixed: horizon rows 79 to 84 at 43.47 mm, 85 to 90 at 40.2 mm.
- The ruler fit (tilt 20.4°, height 40.2 mm) takes away the drift with distance that the old camera has (`validation.md`, by distance), but sits 0.5° from what HOME and CAMPUS want at that height, which is the constant 6 to 8 px it is off by there.
- A camera with the ruler set's height and the tilt HOME and CAMPUS want together: f 400, tilt 20.96° (rounded 20.95°), height 40.2 mm, horizon row 86.9. Its tilt is read off the train boxes, so the size check is no longer an independent test of it; PREREG.md, addendum.
