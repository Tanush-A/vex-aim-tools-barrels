# The hard cases: what the checks remove, by kind (question 3)

From `harness_removed.csv` (every box removed in the proof harness). 'on a barrel' = found or box off before; 'not' = wrong color, second box, on nothing; 'unscored' = no truth for that mask. Expected width W from the box's top row.

## S: solid paint only, solidity under 0.40 dropped (P) — 0 boxes removed

| group | on a barrel | not on a barrel | unscored |
|---|---|---|---|

| reason | on a barrel | not on a barrel | unscored |
|---|---|---|---|

| rule that drew it | on a barrel | not on a barrel | unscored |
|---|---|---|---|

| scene kind (amount hidden) | on a barrel | not on a barrel | unscored |
|---|---|---|---|

| expected width | on a barrel | not on a barrel | unscored |
|---|---|---|---|

| place of the frame | on a barrel | not on a barrel | unscored |
|---|---|---|---|

## L: label only, stripe over 1.25 x a stripe height with body under 0.6 dropped (P) — 25 boxes removed

| group | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| damage | 0 | 7 | 0 |
| real | 0 | 2 | 0 |
| real_dilate | 0 | 2 | 0 |
| real_erode | 0 | 2 | 0 |
| scene | 7 | 5 | 0 |

| reason | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| label | 7 | 18 | 0 |

| rule that drew it | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| body_span | 3 | 1 | 0 |
| centred | 0 | 3 | 0 |
| hidden_side | 1 | 1 | 0 |
| whole_stripe | 3 | 13 | 0 |

| scene kind (amount hidden) | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (not a scene) | 0 | 13 | 0 |
| barrel_front/same 0.25 | 0 | 2 | 0 |
| barrel_front/same 0.5 | 0 | 1 | 0 |
| barrel_front/same 0.75 | 0 | 1 | 0 |
| barrel_low/other 0.75 | 2 | 0 | 0 |
| barrel_side/other 0.5 | 1 | 1 | 0 |
| barrel_side/other 0.75 | 4 | 0 | 0 |

| expected width | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| 25-60 px | 6 | 17 | 0 |
| close, W >= 60 px | 1 | 1 | 0 |

| place of the frame | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (scene) | 7 | 5 | 0 |
| campus_study | 0 | 8 | 0 |
| home_glass | 0 | 3 | 0 |
| home_wooddesk | 0 | 1 | 0 |
| uc_palewood | 0 | 1 | 0 |

## SL: both, at P (0.40; 1.25 / 0.6) — 25 boxes removed

| group | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| damage | 0 | 7 | 0 |
| real | 0 | 2 | 0 |
| real_dilate | 0 | 2 | 0 |
| real_erode | 0 | 2 | 0 |
| scene | 7 | 5 | 0 |

| reason | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| label | 7 | 18 | 0 |

| rule that drew it | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| body_span | 3 | 1 | 0 |
| centred | 0 | 3 | 0 |
| hidden_side | 1 | 1 | 0 |
| whole_stripe | 3 | 13 | 0 |

| scene kind (amount hidden) | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (not a scene) | 0 | 13 | 0 |
| barrel_front/same 0.25 | 0 | 2 | 0 |
| barrel_front/same 0.5 | 0 | 1 | 0 |
| barrel_front/same 0.75 | 0 | 1 | 0 |
| barrel_low/other 0.75 | 2 | 0 | 0 |
| barrel_side/other 0.5 | 1 | 1 | 0 |
| barrel_side/other 0.75 | 4 | 0 | 0 |

| expected width | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| 25-60 px | 6 | 17 | 0 |
| close, W >= 60 px | 1 | 1 | 0 |

| place of the frame | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (scene) | 7 | 5 | 0 |
| campus_study | 0 | 8 | 0 |
| home_glass | 0 | 3 | 0 |
| home_wooddesk | 0 | 1 | 0 |
| uc_palewood | 0 | 1 | 0 |

## Sm: solid paint only, under 0.35 (M) — 0 boxes removed

| group | on a barrel | not on a barrel | unscored |
|---|---|---|---|

| reason | on a barrel | not on a barrel | unscored |
|---|---|---|---|

| rule that drew it | on a barrel | not on a barrel | unscored |
|---|---|---|---|

| scene kind (amount hidden) | on a barrel | not on a barrel | unscored |
|---|---|---|---|

| expected width | on a barrel | not on a barrel | unscored |
|---|---|---|---|

| place of the frame | on a barrel | not on a barrel | unscored |
|---|---|---|---|

## Lm: label only, over 1.5 x with body under 0.6 (M) — 3 boxes removed

| group | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| scene | 1 | 2 | 0 |

| reason | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| label | 1 | 2 | 0 |

| rule that drew it | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| body_span | 1 | 0 | 0 |
| centred | 0 | 1 | 0 |
| whole_stripe | 0 | 1 | 0 |

| scene kind (amount hidden) | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| barrel_front/same 0.25 | 0 | 1 | 0 |
| barrel_side/other 0.5 | 0 | 1 | 0 |
| barrel_side/other 0.75 | 1 | 0 | 0 |

| expected width | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| 25-60 px | 1 | 2 | 0 |

| place of the frame | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (scene) | 1 | 2 | 0 |

## SLm: both, at M (0.35; 1.5 / 0.6) — 3 boxes removed

| group | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| scene | 1 | 2 | 0 |

| reason | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| label | 1 | 2 | 0 |

| rule that drew it | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| body_span | 1 | 0 | 0 |
| centred | 0 | 1 | 0 |
| whole_stripe | 0 | 1 | 0 |

| scene kind (amount hidden) | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| barrel_front/same 0.25 | 0 | 1 | 0 |
| barrel_side/other 0.5 | 0 | 1 | 0 |
| barrel_side/other 0.75 | 1 | 0 | 0 |

| expected width | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| 25-60 px | 1 | 2 | 0 |

| place of the frame | on a barrel | not on a barrel | unscored |
|---|---|---|---|
| (scene) | 1 | 2 | 0 |

