# DETECTOR-MAP.md — what `detect()` does, check by check

**Now (2026-11-26, after the collapse).** This is the map of `barrels/src/barrels/detector.py` as it stands on branch `wip/collapse`. The detector has **no on/off switches**. It has 20 numbers (`DetConfig`) and ten stages, each one function. It draws exactly the boxes it drew before the collapse: 6152 boxes on 5435 masks, box for box (section 5).

- Every name in `code font` is a function or a field of that file. There are no line numbers: search for the name.
- W = the width, H = the height, "a stripe height" = the stripe's height that the geometry expects of a barrel at the row in question.
- "edge tolerance" = 15 % of the height, at least 4 px (`edge_tol`).
- A word in quotes at the end of a check, like "too_far", is the reason the detector writes in its reason log when the check says no (`detect(mask, log=[])`).
- The map before the collapse, with the 30 switches, is `archive/DETECTOR-MAP-before-collapse-2026-11-26.md`. When each rule was added and for which frame: `archive/DETECTOR-HISTORY.md`.

---

## 1. Overview

The color step (`pipeline.py`, not the detector) makes every pixel orange, blue or other. The detector takes that mask and returns the boxes.

| # | stage | function | what it does, in one line | boxes |
|---|---|---|---|---|
| 1 | Pieces | `find_pieces` | blobs of orange and blue together, cut to barrel width, bottom edge from the top row, size checks | none yet: kept for stage 4 |
| 2 | Stripes | `find_stripes` | one color with the other color right above **and** right below; pieces joined; size checks; a wide stripe cut | none: makes stripes |
| 3 | Stripe step | `boxes_from_stripes` | one box per stripe. The stripe's row gives the distance, the distance gives the full box | **adds** (most boxes) |
| 4 | Close-ups | `closeup_pieces` | a stage-1 piece that no box covers is kept only when its stripe is below the frame | adds |
| 5 | Verify, pass 1 | `drop_seen_through` | drop a box that was read from a nearer barrel's own picture | **deletes** |
| 6 | Caps | `caps_behind` | a barrel-wide top showing above a found nearer barrel is a barrel behind it | adds |
| 7 | Pairs | `post_pairs` | two thin slices at the same rows, one barrel apart, are one barrel behind a post | adds |
| 8 | Half stripes | `half_stripes` | a stripe with body on one side only is a barrel hidden from above or from below | adds; may **replace** a stage-3 box |
| 9 | Verify, pass 2 | `drop_seen_through` | the stage-5 check again, on every box | deletes |
| 10 | Verify, readings | `drop_single_reading` | a box placed from a guessed side must have a seen top, bottom or full width | deletes |

Then the boxes are sorted left to right and returned. `detect` is these ten lines and nothing else.

Three things to keep in mind:

- **Stripes come first.** The first boxes come from stripes (stage 3). A stripe already needs body color above and below it, so "stripe" means "stripe sandwiched in body".
- **Geometry is not a stage.** It is the ruler inside every check. A row gives a distance. The distance gives the expected width, height and stripe height (`BarrelAt`). A check compares what is seen with that.
- **Occlusion is not a stage either.** It is one branch inside stage 3 (a stripe narrower than 0.8 W) and three add-on stages after it (6, 7, 8).

```mermaid
flowchart TD
    M["class mask<br/>0 other, 1 orange, 2 blue"] --> S1
    S1["1 PIECES find_pieces<br/>blobs of both colors, barrel-shaped.<br/>No box yet"] --> S2
    S2["2 STRIPES find_stripes<br/>one color with the other right above and below"] --> S3
    S3["3 STRIPE STEP boxes_from_stripes<br/>whole stripes first, then partly seen ones, nearest first"] --> Q1{"stripe at least<br/>0.8 W wide?"}
    Q1 -- yes --> WH["WHOLE<br/>sides = the body joined to the stripe"]
    Q1 -- no --> PS["PARTLY SEEN (section 3, stage 3)<br/>what is seen, a reason for a hidden side,<br/>the outline, centred"]
    PS --> Q2{"placed?"}
    Q2 -- no --> ASIDE["no box.<br/>The stripe is kept for stage 7"]
    Q2 -- yes --> Q3
    WH --> Q3{"holds body color?<br/>not a duplicate?"}
    Q3 -- no --> NOBOX["no box"]
    Q3 -- yes --> B3["boxes so far"]
    B3 --> S4["4 CLOSE-UPS closeup_pieces<br/>a piece no box covers,<br/>stripe below the frame"]
    S1 -. "pieces" .-> S4
    S4 --> V1["5 VERIFY drop_seen_through<br/>not read from a nearer barrel's picture"]
    V1 --> S6["6 CAPS caps_behind<br/>a top above a found nearer barrel"]
    S6 --> S7["7 PAIRS post_pairs<br/>two thin slices, one barrel apart"]
    ASIDE -. "left-over stripes" .-> S7
    S2 -. "left-over pieces" .-> S7
    S7 --> S8["8 HALF STRIPES half_stripes<br/>body on one side only.<br/>May replace a stage 3 box"]
    S8 --> V2["9 VERIFY drop_seen_through, again<br/>10 drop_single_reading:<br/>a guessed side needs a seen edge"]
    V2 --> OUT["boxes, left to right"]
```

**Which rule draws the boxes.** On the 261 real train masks (boxes drawn, not barrels found; no labels read) the detector draws 239 boxes. 201 come from a stripe (stage 3): 137 from a stripe seen whole, 27 where the body shows the width, 30 with one hidden side, 5 centred, 1 by the outline, 1 thin slice at the frame edge. 28 are close-ups (stage 4), 6 are caps, 4 are half stripes. No pair. `results/2026-11-26_collapse/rule_counts.md` has the same count for the simulated scenes and the damaged masks, and how often each check says no.

---

## 2. The path of a plain, fully visible barrel

A barrel standing free, whole in the frame, body and stripe both painted. The numbers in brackets are for a barrel 20 cm away (51 px wide, 55 px tall, stripe 13 px, stripe centre at row 150) and 40 cm away (25.5 px wide, 28 px tall, stripe 6.8 px).

Before the detector, the color step must paint the body **and** the stripe.

Stage 1 finds this barrel's piece, but cannot refuse the barrel: a barrel with a stripe gets its box in stage 3, and the piece is then dropped as "covered".

| # | test, in plain words | number | function | if it fails |
|---|---|---|---|---|
| 1 | The stripe's pixels survive the clean-up. Both colors are closed (3 × 3). A stripe pixel inside the closed body is body. | `close_px` 3 | `sandwiches` | a very thin stripe vanishes |
| 2 | **The sandwich.** Every stripe pixel has body color above it **and** below it in its own column, near enough. | 3 × the stripe height expected at that row (`band_h_max`) [39 px; 20 px] | `sandwiches`, `_reach_by_row` | no stripe at all. This is the commonest real miss: the body is not painted |
| 3 | If a highlight cut the stripe, the pieces join into one. | same rows; together at most 1.2 W; each piece stripe-shaped, or the gap bridged by body color | `_join_pieces` | each piece is judged alone |
| 4 | Big enough. | 20 px (`min_area_px`) | `find_stripes` 1 | "area" |
| 5 | Its row gives a distance. | below the horizon (row 76) | `find_stripes` 2 | "no_geometry" |
| 6 | On the table. | W at least 16 px, i.e. nearer than 637 mm (`min_width_px`) | `on_the_table` | "too_far" |
| 7 | As tall as a stripe. | 0.45 to 1.6 × the stripe height [5.9–21 px; 3.0–10.8 px], from the 10th to the 90th percentile of its rows. Too thin but seen whole: read once more as the mean of its height and the gap between the two body parts | `find_stripes` 4 | "height" |
| 8 | Not a speck sideways. | at least 0.45 × the stripe height wide [5.9 px] | `find_stripes` 5 | "width"; kept for stage 7 |
| 9 | Not wider than one barrel. | at most 1.4 W (`stripe_merge`); and at most 1.2 × W where body is seen right above and below | `_one_stripe_per_barrel` | it is cut into two barrels |
| 10 | Top and bottom. The body is walked up and down from the stripe. A seen end that agrees with the predicted row is the edge; else the predicted row is drawn. This refuses only when **both** edges are predicted **and** the body above ends against the other barrel color. | the edge tolerance [8.3 px; 4.2 px]; "against" = the 4 rows beyond the end, half of the stripe's columns | `read_edges` | "top_against_barrel" |
| 11 | Is the stripe at least 0.8 W wide? Yes: the box's sides are the body joined to the stripe. (No: the partly seen branch, also for a barrel that is not hidden.) | `stripe_full` 0.8 [41 px; 20 px]; the box at most 1.2 W (`body_width`) | `place_sides`, `_body_columns` | the partly seen branch |
| 12 | The box is not empty. | at least 2 × 2 px | `box_from_stripe` | "empty_box" |
| 13 | The box holds the body color. | in the stripe's columns, outside its rows: body pixels ≥ stripe-colored pixels, and body ≥ 10 % (`body_min`) | `holds_body` | "body_min" |
| 14 | It is not the same barrel as a surer box. | same color, IoU over 0.5; the box whose stripe holds more labeled pixels stays | `boxes_from_stripes` 4 | "duplicate" |
| 15 | It was not read from a nearer barrel's picture. Asked twice (stages 5 and 9). | at least 20 of its evidence pixels are not explained by a nearer kept barrel | `drop_seen_through` | "verify: front" |

Each test is a hard yes or no. None can make up for another. `drop_single_reading` does not ask this barrel anything: its box is not flagged "occluded".

After that the scorer asks for overlap ≥ 0.5 and the bottom edge within 10 % of the height (at least 3 px). The detector's own "agrees" in test 10 is 15 % (at least 4 px). See B8 in section 6.

---

## 3. The checks, stage by stage

Each check: **what it asks**; the number; what happens; *why it exists*.

### Stage 1 — Pieces (`find_pieces`)

In: the mask. Out: the pieces (`Piece`: a box, a color, flags, and the last row its own pixels reach). Only stage 4 uses them.

First the piece is made:

- **Which barrel-colored pixels touch?** Orange and blue together, gaps closed 3 × 3, touching diagonally counts, at least 20 px (`find_blobs`). *So a body and its stripe are one blob.*
- **How many barrels wide is the blob?** Its width ÷ the width W of one barrel at its bottom row (at its top row if it touches the frame bottom), rounded (`expected_width_px`). Two or more: cut at the narrowest column within ± 0.25 W of each equal cut (`split_blob`). *Touching barrels meet at their bulges, so there is a waist.*
- **Is the seen bottom where the top row says the base must be?** Within the edge tolerance: the seen bottom is kept. Else the predicted bottom is drawn, flag `bottom_inferred` (`predicted_bottom`, `resolve_bottom`). The box is clipped to the frame; at the frame bottom it is `truncated`. *A shaded lower face makes the blob short.* A piece whose top is at row 232 or lower always gets a box to the frame bottom: its predicted base is below the frame.

Then four checks, numbered as in `find_pieces`:

1. **Is it on the table?** W at its bottom row is at least 16 px. No: "too_far". *The hand at the horizon.*
2. **Is its top below the horizon?** (`above_horizon`) No: "above_horizon". *A barrel is 24 mm tall and the camera is 43 mm up, so the camera looks down on every lid. Nothing on the table has its top at or above the horizon. A jacket above the table edge does.*
3. **Is it barrel-wide?** 0.4 to 1.6 × W. No: "width".
4. **Is it barrel-tall?** Asked only when the box ends inside the frame and does not touch the frame top: 0.5 to 1.5 × H for its bottom row. No: "height". Once 2 has been asked, this can only refuse a piece that is too short with its top in the lowest rows of the frame (row 427 or lower; see B13).

Its color is the majority of its pixels. A tie is orange.

### Stage 2 — Stripes (`find_stripes`)

Done twice: orange as the body (blue stripes), then blue as the body. In: the mask. Out: the stripes (`Stripe`) and the **left-over pieces**.

First the sandwich (`sandwiches`, computed once per image and used again by stage 8): a pixel of the other color counts when body color is above **and** below it in its own column, within 3 stripe heights (`band_h_max`). Connected pixels are a piece. Then:

- **Join** (`_join_pieces`). Going left to right, a piece joins the nearest group to its left when they share rows (`same_rows`), together fit in one barrel (1.2 W), and either both are stripe-shaped (not taller than wide, not taller than 1.6 stripe heights) or the gap between them is **bridged**: both no taller than 1.6 stripe heights, box middles within half a stripe height, body color above and below in **every** column of the gap, gap at most half the joined span. *A highlight or a slit cuts a stripe in pieces. Two barrels cannot both have their stripe inside one barrel's width at the same rows.*

Per stripe, in this order:

1. **Big enough?** 20 px. No: "area".
2. **Does its row give a distance?** The median row of its pixels is below the horizon. No: "no_geometry".
3. **On the table?** (`on_the_table`) W at least 16 px. No: "too_far".
4. **As tall as a stripe?** 0.45 to 1.6 × the stripe height, measured from the 10th to the 90th percentile of its rows. Too thin **and** at least 0.8 W wide: read a second time as the mean of its own height and the gap between the two body parts. *Mixed pixels at the two seams make the stripe thinner and the gap taller by the same amount.* No: "height".
5. **Wide enough to look at?** At least 0.45 × the stripe height. No: "width", and the piece becomes a **left-over piece**.
6. **Wider than one barrel?** (`_one_stripe_per_barrel`) Over 1.4 W: cut into round(width ÷ W) equal parts. Or, where body is seen right above **and** below the whole region: over 1.2 × W₂, cut into at least two parts. W₂ is the larger of W and the width of a barrel as tall as that body. Each part remembers the region (`Stripe.cut_from`). *Two same-colored barrels side by side have one joined stripe. A near barrel runs wider than its row predicts, but then it is taller too.*
7. **Thin?** Narrower than one stripe height, or taller than wide: marked `Stripe.thin`. It enters stage 3 **and** a copy goes to the left-over pieces.

### Stage 3 — One box per stripe (`boxes_from_stripes`, `box_from_stripe`)

In: the stripes. Out: the boxes (`Found`), the stripes nothing could place (for stage 7), and the stripes that lost to a surer box (for stage 6).

**Order.** Stripes at least 0.8 W wide first, left to right. Then the narrower ones, lowest stripe row (nearest) first. *A partly seen stripe asks about the barrels found so far.*

Per stripe, four steps, numbered as in `boxes_from_stripes`:

1. **(partly seen, not cut from a wider stripe) Is it a second piece of a found barrel's stripe?** Same body color, shares rows with that barrel's stripe, its middle column inside that barrel's box (`piece_of_found`). Yes: no box, "stripe_piece".
2. **Make its box** (`box_from_stripe`, three steps of its own):
   1. **Where are the top and the bottom?** (`read_edges`) The body is walked up and down from the stripe in the stripe's columns; the walk ends after 3 empty rows (`_body_extent`). A seen end within the edge tolerance of the predicted row is the edge. Else the predicted row is drawn and flagged `top_inferred` / `bottom_inferred`. Then two questions, because an edge is only seen against something that is not a barrel:
      - (a) **Both edges predicted, and the body above ends against the other barrel color?** (`ends_against`: that color in half of the stripe's columns, in the 4 rows beyond the end.) Yes: no box, "top_against_barrel". *A strip of a back barrel between its own stripe and a front barrel is not a barrel.*
      - (b) **A seen bottom that ends against the other barrel color, with the predicted bottom lower?** Yes: the predicted bottom is drawn. *The barrel may go on behind the one in front.*

      **A thin stripe must be a slice seen from top to bottom:** neither edge predicted. Else no box, "slice_not_full". *A reason for a hidden side says where a barrel would be, not that there is one.*
   2. **Where are the left and the right?** (`place_sides`) See the tree below. Nothing places it: no box, "side_unexplained" (thin: "outline_unknown"). A stripe that is not thin is then kept for stage 7.
   3. **Is the box at least 2 × 2?** No: "empty_box". **Does it hold the body color?** (`holds_body`) In the stripe's columns, outside its rows: body pixels ≥ stripe-colored pixels, and body ≥ 10 %. No: "body_min". *A blue barrel's body between two orange things is not an orange barrel.*
3. **Would the box sit on a found box** (`same_barrel`: same color, IoU over 0.5)? A box the outline placed never takes a found box's place. A thin stripe: no box, "duplicate". Any other: the box is made again without the outline (`use_outline=False`).
4. **Is it the same barrel as a found box** (and not another part cut from the same wide stripe)? The surer one stays: confidence = 0.5 + 0.5 × the labeled share of the stripe's box. "duplicate". The stripe of the box that goes is "lost": stage 6 still treats it as a stripe.

**The sides (`place_sides`).**

```mermaid
flowchart TD
    A["one stripe, top and bottom known"] --> W{"at least 0.8 W wide?"}
    W -- yes --> WB["WHOLE: the box is as wide as the body joined<br/>to the stripe, at most 1.2 W<br/>rule: whole_stripe"]
    W -- no --> SP["seen_span: the stripe's columns joined with<br/>the body columns above and below it.<br/>Flag: occluded"]
    SP --> T{"thin?"}
    T -- no --> W8{"span at least 0.8 W?"}
    W8 -- yes --> B1["box = the span<br/>rule: body_span"]
    W8 -- no --> R{"hidden_side: a reason on exactly one side?<br/>frame edge, nearer found barrel,<br/>or body and stripe ending apart"}
    R -- "one side" --> B2["box = W wide from the seen end<br/>of the other side<br/>rule: hidden_side"]
    R -- "none or both" --> O{"own_end_by_outline: exactly one end<br/>has a barrel's rounded corners?"}
    O -- yes --> B3["box = W wide from that end<br/>rule: outline"]
    O -- no --> C{"stripe at least 0.4 W wide?"}
    C -- yes --> B4["box = W wide, centred on the span.<br/>A guess. rule: centred"]
    C -- no --> N2["no box: side_unexplained.<br/>Kept for stage 7"]
    T -- yes --> TS{"span at least 0.8 W, body trusted,<br/>body does not cross the stripe's rows?"}
    TS -- yes --> B5["box = the span<br/>rule: thin_span"]
    TS -- no --> TF{"touches the frame on<br/>exactly one side?"}
    TF -- yes --> B6["box = W wide from the other end<br/>rule: thin_frame"]
    TF -- no --> TO{"exactly one own end<br/>by the outline?"}
    TO -- yes --> B7["box = W wide from that end<br/>rule: thin_outline"]
    TO -- no --> N3["no box: outline_unknown"]
```

- **Whole** (`_body_columns`). A column counts with 2 or more body pixels. Gaps of 2 columns are allowed. Columns under another stripe never count (thin stripes are not "another stripe"). *The stripe's outermost pixels curve away and go dark, so the stripe alone runs 15 % narrow.*
- **What is seen** (`seen_span`, `_body_span`). The stripe's columns joined with the body columns above and below it. If that is wider than 1.2 W, a same-colored neighbour is in it: the body is "not trusted" and only the stripe counts. A side is **cut** when the body's end and the stripe's end there are further apart than max(4 px, 15 % of **W**). A part cut from a wider stripe is cut on its cut side. *At a barrel's own edge the stripe and the body end together.*
- **A reason for a hidden side** (`hidden_side`). The span touches the frame edge there; or a found barrel standing nearer is there (its box holds one of the 3 pixels beside the span at the stripe's middle row, and its bottom is lower than this barrel's predicted bottom); or the side is cut.
- **The outline** (`own_end_by_outline`, `_end_costs`, `Outline`). Each end of the span is asked alone. Put the barrel's outline with its side on that end. Over the columns within 0.353 W of the end, compare the seen top line, stripe line and bottom line with the outline's. The end's cost is the largest of the three mean differences, in barrel heights. An end costing at most 0.05 (`pin_good`) is the barrel's own side. *A barrel's own side has rounded corners. A cut side has square ones.*
- **Thin stripes** (`thin_slice`) skip the reasons. They get here only as a slice seen from top to bottom (`box_from_stripe`, step 1).
- Only the exits "hidden_side", "outline" and "centred" guess a side. `drop_single_reading` asks them again at the end.

### Stage 4 — Close-ups (`closeup_pieces`)

In: the stage-1 pieces and the boxes so far. Out: more boxes (source "det1").

1. **Does a box already account for this piece?** They share more than 0.3 of the narrower one's width, **and** they share rows. A piece kept just before counts too. Yes: "covered". *A far barrel standing above a close-up in the picture must not hide it.*
2. **Is it a close-up?** Its box reaches the frame bottom (rule "closeup"). Or its top row puts the stripe's bottom edge at or below the frame bottom: top at row 241 or lower (rule "closeup_stripe"; `_closeup_stripe_rows`). *The frame cuts the stripe, so no body shows below it and the stripe finder cannot see it.*
3. **A close-up that the left or right frame side also cuts: is its body seen down to where its top row puts the stripe (or to the frame bottom)?** Within the edge tolerance (`_seen_to_stripe`). No: "closeup_side". *A printed orange fruit at the frame corner. With the side cut, the width says nothing.*
4. **Keep it?** A close-up: yes. Else only if the stripe expected at its middle row is under 4 px (`min_stripe_px`; rule "far_piece"). Else "stripeless". The "far" half takes no piece today (B1).

Nothing here asks whether the piece is a solid face (B10).

### Stages 5, 9 and 10 — Verify (`drop_seen_through`, `drop_single_reading`)

**A barrel cannot be seen through a nearer barrel** (`drop_seen_through`; stage 5 and stage 9).

```
fewer than 2 boxes → nothing to do
boxes taken nearest first (lowest bottom edge first)
for each box b:
├─ its evidence = the box of what it was read from: its stripe, its cap piece, its band,
│    its two slices together; a piece is its own (Found.evidence_box)
├─ nearer = the kept boxes whose bottom edge is strictly lower than b's
├─ each nearer barrel explains the pixels of its own layout (outline_layout): body color in its body rows,
│    stripe color in its stripe rows, either color within half a stripe height of a seam;
│    only in the rows where its body is seen
├─ own pixels = barrel-colored evidence pixels that no nearer barrel explains
└─ a nearer barrel exists and own pixels < 20 (min_area_px) → dropped: "verify: front"
```

*A nearer barrel's upper body between clutter above and its own stripe below reads as the stripe of a smaller barrel behind.* It runs before the caps so that stages 6 to 8 lean only on boxes that passed. A dropped box's stripe is cap material again.

**A guessed side needs a second reading** (`drop_single_reading`; the last stage).

```
only for a box from a stripe (source det2) flagged occluded, with top AND bottom both predicted
├─ W from the middle row of its stripe's box
├─ seen span = the stripe's columns joined with the body columns; wider than 1.2 W: only the stripe's
└─ seen span under 0.8 W → dropped: "verify: readings"
```

*A tin with an orange lid and a blue label: a piece of the label made a box from one stripe row and nothing else.* Caps, pairs, half stripes and thin stripes always have a seen edge by the way they are made.

### Stage 6 — Caps (`caps_behind`, `_cap_pieces`, `_cap_box`)

A barrel behind a found barrel shows its upper body (its "cap") above it. Its stripe has melted into the front barrel's body, so stage 3 cannot find it. The distance comes from the cap's **top row**. Done per color. Out: boxes (source "det3", flags `occluded` and `bottom_inferred`, confidence 0.5).

```
that color's pixels (closed), without the boxes of the stripes already read
a connected piece of 20 px or more:
├─ fewer than half of its pixels inside found boxes of its color → a candidate
│    else → only its parts outside those boxes are candidates        (a barrel behind one of its own color)
├─ 1. top row readable (not at the frame top), on the table?         no → dropped, no note
├─ 2. 0.4 to 1.2 W wide?                                             no → "width"
├─ 3. 0.4 of an upper body to one upper body + the edge tolerance tall?   no → "height"
├─ 4. at least 0.8 W wide → bottom = top + the height of a barrel as wide as the cap
├─ 5. narrower → exactly one side hidden (the frame edge, or a found box beside it whose bottom is lower than the cap's)?
│         neither → "narrow"        both → "both_sides"
│         one → widened to W toward that side; bottom = the one the top row predicts
├─ 6. its own color seen ending within the edge tolerance of that bottom (3 empty rows after)?  yes → that end is the bottom
├─ 7.   no, and the cap is narrow → seen ending beside the nearer found barrels, between the bottom of a barrel
│         only as wide as the cap and the estimate + the tolerance?  yes → that end is the bottom
├─ 8. at least half of the box below the cap inside found boxes whose bottom is lower than this box's?   no → "not_hidden"
└─ 9. not the same barrel as a found box or an earlier cap → box       else "duplicate"
```

*Why 4 uses the width: the bottom predicted from the top row is 4 to 7 px low at mid and far range with this camera.* "Standing nearer" means a different bottom at 5, 7 and 8 (B4).

### Stage 7 — Pairs (`post_pairs`, `_full_slice`)

In: the left-over pieces of stage 2 and the stripes stage 3 could not place. Out: boxes (source "det2", flag `occluded`, confidence 0.5).

1. **Is the piece a second piece of a found barrel's stripe?** (`piece_of_found`) Yes: left out.
2. **Is it a full slice?** The body above and below ends where its row predicts the top and the bottom (edge tolerance), and neither end lies against the other barrel color. No: left out.
3. **Is it narrow?** Under 0.4 W (`stripe_w_min`). No: left out.
4. **Two such pieces: same body color, the right one wholly right of the left one, same rows?**
5. **Are their outer body edges one barrel apart?** 0.8 to 1.2 × W. Yes, and not the same barrel as a found box: one box from outer edge to outer edge.

*A post over the middle of a barrel. Two barrels at one distance cannot have their outer edges within 1.2 W of each other.* No real train frame forms a pair.

### Stage 8 — Half stripes (`half_stripes`)

A band = a connected piece of one color, 20 px or more. The distance comes from the **seam** between band and body. Out: boxes (source "det2", flags `occluded` and `top_inferred` or `bottom_inferred`, confidence 0.5).

```
├─ 1. body right below in ≥ 0.8 of its columns and right above in ≤ 0.2 → "top hidden"
│       body right above in ≥ 0.8 and right below in ≤ 0.2              → "bottom hidden"       else → not a half stripe
├─ 2. the seam gives the distance (15 mm above the table for the stripe's top edge, 9 mm for its bottom edge);
│       on the table?                                               no → skipped
├─ 3. band not taller than 1.6 stripe heights (no floor)             no → "height"
├─ 4. band 0.8 to 1.2 W wide                                         no → "width"
├─ 5. the body's far edge where the seam predicts it, inside the frame   no → "far_edge"
├─ 6. band thinner than the body part beside it                      no → "thicker_than_body"
├─ 7. body 0.8 to 1.2 W wide                                         no → "body_width"
├─ 8. open side clear: barrel color in the 4 rows beyond the band in under half of its columns   no → "open_side"
├─ 9. far edge not against barrel color                              no → "far_edge_against_barrel"
├─ 10. not a found barrel's (under half of the band inside found boxes; no found box of its color with IoU over 0.5)   no → "found"
└─ box: sides and far edge as seen, hidden edge where the seam's distance puts it.
        A stage-3 box (flag occluded) whose stripe lies inside this band's box is a corner of it: it does not count
        as "found" in 10, and the new box REPLACES it.
```

*A book lying in front of a barrel, or something hanging over it.* A half stripe always shows its whole width. No side is guessed.

---

## 4. Every number that is left

### 4.1 `DetConfig`: 20 numbers, no switches

| name | value | what it means | where it is used |
|---|---|---|---|
| `min_area_px` | 20 | a speck | a blob (`find_blobs`), a stripe (`find_stripes` 1), a cap piece (`_cap_pieces`, `_cap_box`), a half-stripe band; and the "own pixels" limit of `drop_seen_through` |
| `close_px` | 3 | the closing: 3 × 3 | `_closed` (blobs, the sandwich, caps). Also, unrelated: how many pixels beside a seen end are searched for a nearer barrel (`hidden_side`) |
| `bottom_tol` | 0.15 | the edge tolerance, as a share | `edge_tol`: of the height at 7 sites (`resolve_bottom`, `_seen_to_stripe`, `read_edges`, `_end_costs`, `_cap_box`, `_full_slice`, `half_stripes`); of the **width** at 1 (`seen_span`: body and stripe ending apart) |
| `bottom_tol_min_px` | 4 | its floor | `edge_tol` |
| `width_min` | 0.4 | narrower × W is a sliver | a piece (`find_pieces` 3), a cap (`_cap_box` 2). Also a cap's least **height**, × an upper body (`_cap_box` 3) |
| `width_max` | 1.6 | wider × W is not one barrel | a piece (`find_pieces` 3) |
| `split_search` | 0.25 | where a blob's waist is looked for, ± × W | `split_blob` |
| `min_width_px` | 16 | a barrel narrower than this is beyond the table | `find_pieces` 1, `on_the_table` (stripes, caps, half stripes) |
| `stripe_h_min` | 0.45 | a stripe's least height, × the stripe height | `find_stripes` 4. Also a stripe piece's least **width**, × the stripe height (`find_stripes` 5) |
| `stripe_h_max` | 1.6 | a stripe's greatest height, × the stripe height | `find_stripes` 4, `half_stripes` 3, "stripe-shaped" in `_join_pieces` |
| `band_h_max` | 3.0 | "right above / right below": within this × the stripe height | `_reach_by_row` (the sandwich: stages 2 and 8) |
| `stripe_w_min` | 0.4 | × W | the least stripe for the centred guess (`centred`); the widest slice of a pair (`post_pairs`) |
| `stripe_merge` | 1.4 | a stripe region wider × W is several barrels | `_one_stripe_per_barrel` |
| `stripe_full` | 0.8 | "the whole width shows", × W | whole or partly seen (`place_sides`, the order of stage 3); the second height reading (`find_stripes` 4); the seen span (`seen_span`, `drop_single_reading`); a cap (`_cap_box` 4, 7); a pair's span; half stripes (the shares 0.8 and 0.2, and the widths) |
| `min_stripe_px` | 4.0 | a stripe thinner than this cannot be resolved | the "far" half of `closeup_pieces` 4; the assertion in `on_the_table` |
| `height_min` | 0.5 | a piece's least height, × H | `find_pieces` 4 |
| `height_max` | 1.5 | a piece's greatest height, × H | `find_pieces` 4 |
| `body_min` | 0.1 | the least share of body color in the box | `holds_body` |
| `body_width` | 1.2 | one barrel is at most this × W wide | as it is: the box (`place_sides`), the trusted body (`seen_span`, `drop_single_reading`). As `widest_barrel` (never under 1): a joined stripe, the second cut of `_one_stripe_per_barrel`, a cap, a pair, a half stripe |
| `pin_good` | 0.05 | an end is the barrel's own side when the outline's lines lie within this × H | `own_end_by_outline` |

Seven numbers do more than one job: `stripe_full`, `body_width`, `bottom_tol`, `close_px`, `min_area_px`, `width_min`, and `stripe_h_min`. None can be changed for one job without moving the others.

### 4.2 Numbers that are not in `DetConfig`

| number | what it decides | where |
|---|---|---|
| touching diagonally counts (8-connected) | what is one piece | `find_blobs`, `find_stripes`, `_cap_pieces`, `half_stripes` |
| a tie is orange | a piece's color | `find_pieces` |
| a quarter | the stripe's centre row is the median row of its colored pixels when they are at least a quarter of the part, else the box middle | `_one_stripe_per_barrel` |
| 10th to 90th percentile of the rows, + 1 | "the stripe's height" | `find_stripes`, `_join_pieces`, `half_stripes` |
| overlap at least half the shorter height | "the same rows" | `same_rows` (join, `piece_of_found`, pairs) |
| middles within ½ stripe height; gap ≤ ½ the joined span; body in every gap column | the bridge | `_join_pieces` |
| equal weights ½ and ½ | the second height reading | `find_stripes` 4 |
| 3 empty rows end the walk | where the body ends, up and down | `_body_extent`, `_seen_lines` |
| 2 body pixels make a column; 2 empty columns end the walk | where the body ends, sideways | `_body_columns`, `_body_span` |
| 0.353 W; the side curve 1 − √(1 − t) | the barrel's outline: the lid's half width, the shoulder | `LID_HALF`, `Outline` |
| the columns within 0.353 W of the end; at least 2; the worst of the three lines; each line's median taken out | the own-side test | `_end_costs` |
| more than half of the stripe's rows | "the body crosses the stripe" | `_body_crosses` |
| the 4 rows beyond the edge; half of the columns | "ends against" | `ends_against`, and the open side of `half_stripes` |
| body pixels ≥ stripe-colored pixels | the first half of the body check | `holds_body` |
| 0.5 + 0.5 × the labeled share; a fixed 0.5 for caps, pairs, half stripes | "confidence", used only to pick the surer of two stripe boxes | `box_from_stripe` |
| IoU over 0.5, same color | "the same barrel" | `is_same_barrel` |
| more than 0.3 of the narrower width, and any shared row | "covers" | `closeup_pieces` 1 |
| half of the pixels; half of the box below | a cap candidate; "hidden by a barrel" | `_cap_pieces`, `_cap_box` 8 |
| 3 empty rows after it | a cap's seen bottom | `_cap_box` 6, 7 |
| 15 mm and 9 mm | the seam heights of a half stripe | `half_stripes` |
| within half a stripe height of a seam, either color | what a nearer barrel explains | `outline_layout` |
| a strictly lower bottom edge | "nearer" | `standing_nearer`, `drop_seen_through` |
| 12.75 + 1 mm | the nearest a barrel's axis can be | `BarrelAt` |
| 2 px | the smallest box | `box_from_stripe`, `half_stripes` |

### 4.3 Where one idea still has several numbers

The collapse put each idea in one helper but did **not** make the numbers the same. That would change boxes (section 6).

| idea | the numbers today |
|---|---|
| "wider than one barrel" | 1.5 W (the blob's count rounds to 2), 1.6 W (`width_max`), 1.4 W (`stripe_merge`), 1.2 W (`body_width`) |
| "a barrel standing nearer" | a found box's bottom lower than: this barrel's **predicted** bottom (`hidden_side`); the cap piece's **seen** bottom (`_cap_box` 5, 7); the cap box's **drawn** bottom (`_cap_box` 8); the other **box's** bottom (`drop_seen_through`) |
| "beside" | 3 pixels beside the span (`hidden_side`); 1 pixel beside the cap (`_cap_box` 5) |
| "ends against" | the **other** barrel color (`read_edges`, `_full_slice`); **any** barrel color (`half_stripes` 8, 9) |
| the row that gives a stripe's barrel | the median row of the candidate's pixels (`find_stripes`); the stripe's centre row (stage 3, `Stripe.at`); the middle of a piece's box (`_join_pieces`); the middle of the stripe's box (`drop_single_reading`) |
| "the same rows" | overlap at least half the shorter (`same_rows`); middles within half a stripe height (the bridge); any overlap (`closeup_pieces` 1) |
| "one barrel at most" | `body_width` as it is at 3 sites; never under 1 at 6 (`widest_barrel`). The same today |
| "the seen edge agrees" | 15 %, at least 4 px (the detector); 10 %, at least 3 px (the scorer, `eval_det.py`) |

---

## 5. What the collapse removed, and why it is safe

Before: 1904 lines, 51 `DetConfig` fields (30 on/off switches read at 63 places, 20 numbers, 1 mode). After: 1825 lines, 20 numbers. The file is not much shorter: about 420 lines of switches and dead code went, and the docstrings that now say what each check asks came in.

| step | what went or changed | why no box can change |
|---|---|---|
| A1 | the 7 switches that were off (`dark_stripe`, `occl_body_side`, `slice_box`, `cover_unpinned`, `stripe_two`, `slice_behind`, `own_close`), the "bands" finder, and their code | every line sat behind an `if` that was false |
| A2 | the 23 switches that were on are plain code; step 1 alone (`detect_step1`, `--step1`) is gone | every `if` was true |
| A3 | `detect` is ten named stages; the partly seen branch is small functions | code moved |
| A4 | one helper per idea (`edge_tol`, `same_rows`, `same_barrel`, `ends_against`, `standing_nearer`, `widest_barrel`, `sandwiches`) | each is called with the number its site had |
| A5 | `BarrelAt`: the geometry's barrel, built once per stripe | same row in, same numbers out |
| A6 | each box carries its evidence (`Found`); the verify stages no longer search the reason log | not certain in advance; the check decided |
| A7 | the horizon fact is a check of its own (`above_horizon`) | not certain in advance; the check decided |
| A8 | three clauses that never decide are gone | argued below |
| A9 | the history is out of the comments (`archive/DETECTOR-HISTORY.md`) | comments |

**The proof.** The detector is a pure function of the mask and the camera. So 5435 masks were fixed before the first change: every train frame as the color step paints it (261), each with one pixel eroded and dilated (522), the 45 frames with hand-set thresholds, the 53 masks the occlusion scorecard is built from, 666 damaged masks and all 3888 simulated occlusion scenes. No test frame. The detector before the collapse draws 6152 boxes on them. After **every** step the detector drew the same 6152 boxes: same color, box, flags, source and confidence, in the same order. The scripts and the boxes are in `experiments/2026-11-26_collapse/` and `results/2026-11-26_collapse/`.

The reason logs are the same too, except in one step, A7. On 224 of the 5435 masks a piece with its top above the horizon is now refused as "above_horizon" where the log said "height" (473 notes) or "width" (22 notes) before. They are the same pieces, refused one check earlier.

**A7, the horizon.** Before, nothing said "a barrel's top is below the horizon". A piece with its top above the horizon has no distance from its top row. The close-up rule read "no distance" as "the stripe is below the frame" and would have boxed it. What stopped it was the height check, written for one jacket: such a piece is always more than 1.5 × too tall for its bottom row (1.63 × or more, for every pair of rows). Now `find_pieces` asks the fact itself (its check 2), and the close-up rule no longer reads "no distance" as "below the frame". One case differs in theory: a piece that touches the **frame top** skipped the height check before, so it could pass; now it is refused. The color step paints nothing above row 50, so no mask has such a piece.

**A8, the three clauses.**
- "The stripe is at least 4 px tall" next to "the barrel is at least 16 px wide" (stripes, half stripes). A barrel 16 px wide has a stripe 4.3 px tall with this camera, and both grow together. `on_the_table` keeps an assertion that says so, and a test checks it for the three camera presets.
- "Is it a full slice?" inside `thin_slice`. A thin stripe with a predicted edge is refused one step earlier (`box_from_stripe`, step 1), so the answer was always yes.
- "A thin stripe never replaces a found box" in step 4 of `boxes_from_stripes`. Its step 3 has already refused every thin stripe whose box sits on a found box.

**Tests.** 930 before, 907 after (30 removed, 7 added). With the measurement work of `barrels` merged in afterwards (975 tests there): 952. The tests of deleted off paths went with them. The others were rewritten to state what the detector does, without the switch. The table of removed tests is in `experiments/2026-11-26_collapse/ENTRY.md`.

**Old experiments** that name switches run at the git tag `pre-collapse-2026-11-26` (`experiments/README.md`).

---

## 6. What is still not clean

The collapse changed how the code reads, not what it does. Everything below **would change boxes**. Each is an experiment of its own, judged by the standard pass rule.

| # | change | what it would fix |
|---|---|---|
| B1 | delete the "too far for a stripe" half of `closeup_pieces` 4, and `min_stripe_px` with it | a rule that takes no piece. Tried for every top row and bottom row: stage 1 lets nothing through that reaches it. At other numbers it wakes up (the audit: 43 false boxes at 4.8) |
| B2 | one rule for cutting a wide stripe: trust the body's height where it is seen, use 1.4 W only where it is not | 2 real stripe regions that `stripe_merge` alone cuts are one barrel each: two false boxes |
| B3 | one number for "wider than one barrel" (today 1.2, 1.4, 1.5, 1.6) | four limits for one idea |
| B4 | one meaning of "a barrel standing nearer" (today four bottoms, and 3 pixels or 1 beside) | caps and partly seen stripes judge "nearer" differently |
| B5 | one "ends against" test (today the other color, or any barrel color) | three rules, two meanings |
| B6 | one row for a stripe (today four) | far barrels, where one row is 5 % of the size |
| B7 | `drop_single_reading` reads the span that `seen_span` measured | it measures the span again with another row and without leaving out other stripes' columns. "Under 0.8 W" can be true in one and false in the other |
| B8 | the detector and the scorer agree on the bottom edge (15 % against 10 %) | a bottom the detector calls "agrees" can be outside what the scorer accepts |
| B9 | one rule for a barrel cut at the side, without the cliff at 0.4 W. It replaces the centred guess | the guess (`centred`) is the weakest exit of the partly seen branch |
| B10 | a close-up must be a solid face | "reaches the frame bottom" is decided on a box that stage 1 may have stretched; wood grain gets a box 330 px wide |
| B11 | a cap's least height gets its own number | it borrows `width_min` |
| B12 | a join that does not depend on left and right | `_join_pieces` is greedy from the left: mirroring a mask changes boxes on 6 of 199 real frame-runs (the audit) |
| B13 | say what the height check of `find_pieces` is, or delete it | with the horizon check in place, `height_max` can refuse nothing (tried for every top row and bottom row), and `height_min` only a short piece with its top in rows 427 to 479 |
| B14 | `widest_barrel` and `body_width` become one | "never under 1" at 6 sites and not at 3. The same number today |
| B15 | the "kept" note of a stripe is written after the duplicate decision | diagnostics only: today a note can say "kept" for a box that then loses as a duplicate |

Kept on purpose, because they are today's behaviour:

- **Stage 4 reads the list it is adding to.** A piece kept as a close-up can cover a later piece.
- **A stripe that lost as a duplicate is still erased from the cap mask**, and a stripe whose box the verify step dropped is not. Both are what the code did.
- **The detector leans on the color step's row gate.** The color step paints nothing above row 50; the horizon is row 76. Rows 50 to 75 can hold paint. Stage 1 now refuses a piece that starts there. A cap that starts there is dropped because its top row gives no distance.

None of this is why barrels are missed. On real frames the misses are the color step's. The structure was why nobody could say what the detector would do.
