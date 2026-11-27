# Part A, two more questions (in-sample; written after the pre-registration; not a judged run)

## 1. With the parked conditions counted too

r / rho between a reading's condition mean and the blue paint's median S.

| reading | 17 ordinary conditions | all 25 (the wood desk lamp ladder, the black table, the very dark ottoman added) | leave one place out line, 8 ordinary places: skill | 10 places: skill |
|---|---|---|---|---|
| `without_loose` | -0.96 / -0.88 | -0.78 / -0.86 | 0.89 | 0.55 |
| `above_gate20` | -0.96 / -0.89 | -0.82 / -0.88 | 0.83 | 0.64 |
| `whole_frame` | -0.95 / -0.91 | -0.81 / -0.84 | 0.70 | 0.50 |
| `tiles` | -0.94 / -0.83 | -0.88 / -0.87 | 0.76 | 0.68 |
| `max_rgb` | -0.96 / -0.85 | -0.81 / -0.84 | 0.90 | 0.63 |
| `gray_world` | -0.84 / -0.74 | -0.89 / -0.86 | 0.20 | 0.53 |

The lamp conditions side by side (ordinary and parked): the reading, how bright the scene is, and the blue paint.

| condition | class | `without_loose` | median brightness below the gate | blue paint brightness | blue paint S (median) |
|---|---|---|---|---|---|
| lampcool6_bathtile | ordinary | 0.08 | 165 | 77 | 196 |
| lampmid3_bathtile | ordinary | 0.20 | 185 | 52 | 48 |
| lampmid6_bathtile | ordinary | 0.23 | 194 | 62 | 82 |
| lampwarm6_bathtile | ordinary | 0.35 | 204 | 53 | 44 |
| lampcool6_ottoman | ordinary | 0.03 | 31 | 98 | 192 |
| lampmid3_ottoman | extreme | 0.05 | 14 | 19 | 54 |
| lampmid6_ottoman | ordinary | 0.14 | 36 | 83 | 140 |
| lampwarm6_ottoman | ordinary | 0.26 | 37 | 54 | 63 |
| lampcool3_wood | extreme | 0.04 | 128 | 64 | 67 |
| lampcool6_wood | extreme | 0.04 | 181 | 99 | 114 |
| lampmid3_wood | extreme | 0.11 | 149 | 68 | 36 |
| lampmid6_wood | extreme | 0.13 | 201 | 81 | 47 |
| lampwarm3_wood | extreme | 0.16 | 152 | 62 | 22 |
| lampwarm6_wood | extreme | 0.22 | 208 | 72 | 33 |

## 2. The light's color alone, or the color and how dim it is

Leave one place out, per frame, target = the blue paint's median S. The second input is the median brightness of the frame below the gate (readable without knowing where a barrel is).

| inputs | 8 ordinary places: skill (error against baseline, S units) | 10 places with the parked ones: skill (error against baseline) |
|---|---|---|
| `without_loose` alone | 0.89 (21 against 65) | 0.55 (52 against 78) |
| `without_loose` and the scene's brightness | 0.60 (41 against 65) | 0.54 (53 against 78) |
| the scene's brightness alone | -3.98 (145 against 65) | -0.16 (84 against 78) |
| `above_gate20` alone | 0.83 (27 against 65) | 0.64 (47 against 78) |
| `above_gate20` and the scene's brightness | 0.70 (35 against 65) | 0.61 (49 against 78) |
