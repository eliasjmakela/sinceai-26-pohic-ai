# calc/error_accumulation.py output (H1, team-estimate parameters in calc/h1_params.py; untested)

Values are low / mid / high, in % of the container total.

| material | charges per container (mid) | random part (√N) | mean bias | device spread | RMS error before calibration | floor after calibration |
|---|---|---|---|---|---|---|
| cardboard | 167 | 0.8 / 1.3 / 2.5 | -6.5 / -7.0 / -9.0 | 2.7 / 4.4 / 8.1 | 7.4 / 8.9 / 13.3 | 2.2 / 3.3 / 5.6 |
| plastic_film | 111 | 1.1 / 1.7 / 3.3 | -5.5 / -6.0 / -8.0 | 2.5 / 4.0 / 7.3 | 6.5 / 8.0 / 12.4 | 2.3 / 3.5 / 6.0 |
| mixed_plastic | 94 | 1.2 / 1.9 / 3.7 | -5.5 / -6.0 / -8.0 | 2.5 / 4.0 / 7.3 | 6.5 / 8.1 / 12.5 | 2.3 / 3.6 / 6.2 |
| paper | 57 | 1.4 / 2.2 / 4.2 | -3.5 / -4.0 / -6.0 | 2.2 / 3.5 / 6.2 | 4.8 / 6.5 / 10.8 | 2.4 / 3.7 / 6.5 |
| mixed_waste | 100 | 1.0 / 1.7 / 3.1 | -3.5 / -4.0 / -6.0 | 2.2 / 3.5 / 6.2 | 4.7 / 6.3 / 10.4 | 2.2 / 3.4 / 5.9 |
| biowaste | 47 | 1.5 / 2.4 / 4.5 | -1.5 / -2.0 / -4.0 | 2.1 / 3.2 / 5.5 | 3.6 / 5.4 / 9.6 | 2.5 / 3.9 / 6.8 |

Reading: 50–170 charges per container make the random part small (≈1–4.5 %). What is left is a **bias** (the plate misses the part of each charge that hangs on the walls or the ram) that does not average out. It is about the same for every charge of one device, so a handful of weighbridge tickets can measure it (scripts/self_calibration.py). The floor is set by how much that share changes from one container to the next.
