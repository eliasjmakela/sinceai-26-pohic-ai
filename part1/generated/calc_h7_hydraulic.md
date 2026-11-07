# calc/h7_hydraulic.py output: H7 hydraulic self-lift (team estimate; order of magnitude, untested)

## H7: statics and pressure

Moments about the front pivot: R·L = M·x_m + W·x_w; tare R0·L = M·x_m → **W = (R − R0)·L / x_w**. Machine 3.0–4.5 t with 0.30–0.45 of it on the door end (1 − press-end share of calc/loads.py), waste up to 5 t at x_w/L = 0.45–0.75, L = 5.0–6.0 m (team estimate).

| case | cylinder force kN | pressure bar, 63 mm bore | pressure bar, 80 mm bore |
|---|---|---|---|
| empty unit (tare R0) | 9–20 | 28–64 | 18–40 |
| full, 5 t waste (R) | 31–57 | 99–182 | 61–113 |


Design choice: **80 mm bore**, ≤ 113 bar at the heaviest case against ~200 bar system pressure [36]; a 63 mm bore would need 182 bar, too close to the limit. A relief valve set just above the design force makes an over-heavy unit simply not lift (flagged), so the cylinder can never lift more than it was designed for.


Flow: a 10 mm lift moves 50 cm³ of oil; over 15 s that is 0.20 L/min, far below a power pack's flow, so a pressure-compensated flow-control (throttle) valve sets the slow constant speed (0.67 mm/s). Mechanical work 0.6 kJ per lift: negligible; the cost is starting the pump.


Stroke: 50 mm − 30 mm to reach the ground − 10 mm lift = **10 mm** left for unevenness, soft ground or a rail/plinth under the runners. If the stroke runs out before the pressure plateau, the firmware records 'no reading' instead of a wrong one.


### Ground under the 300 × 300 mm foot (heaviest case 57 kN)

| ground | allowable MPa (team estimate) | foot pressure MPa | verdict |
|---|---|---|---|
| concrete slab | 3 | 0.63 | ok |
| dense asphalt, cold | 1 | 0.63 | ok |
| asphalt, hot summer day | 0.4 | 0.63 | needs a 376 mm square pad |
| compacted gravel | 0.3 | 0.63 | needs a 435 mm square pad |
| soft ground / thawing frost | 0.1 | 0.63 | needs a 753 mm square pad |


## H7: seal friction band

Lifting, the pressure reads R + F_f; lowering, R − F_f. Averaging the two plateaus cancels symmetric (Coulomb) friction; stick-slip and speed asymmetry leave a residue (team estimate).


| level | friction kN | % of lightest tare force | % of heaviest full force | not cancelled | residue % of heaviest force |
|---|---|---|---|---|---|
| low | 0.3 | 3.4 | 0.5 | 10% | 0.05 |
| mid | 0.7 | 7.9 | 1.2 | 20% | 0.25 |
| high | 1.5 | 17.0 | 2.6 | 30% | 0.79 |


## H7: error budget (1σ of the waste mass from one tare + one pick-up reading)

**A. one-point lift, no tickets**, 2.5 t of waste (1σ, % of the waste mass)

| source | low | mid | high |
|---|---|---|---|
| Pressure sensor repeatability (tare + reading) | 1.21 | 1.81 | 3.02 |
| Seal friction left after up/down averaging | 0.29 | 1.35 | 4.32 |
| Sensor span vs temperature (after auto-zero) | 0.19 | 0.48 | 0.97 |
| Pivot shift between tare and reading | 0.20 | 0.81 | 2.05 |
| Tare change (rain, ice, residue; heavy snow flagged) | 1.00 | 2.00 | 6.00 |
| Centre of mass x_w (fixed design value) | 5.00 | 10.00 | 20.00 |
| Geometry / gain before tickets | 1.00 | 2.00 | 3.00 |
| **combined (RSS)** | **5.3** | **10.7** | **21.9** |

**B. one-point lift + H2 ticket calibration**, 2.5 t of waste (1σ, % of the waste mass)

| source | low | mid | high |
|---|---|---|---|
| Pressure sensor repeatability (tare + reading) | 1.21 | 1.81 | 3.02 |
| Seal friction left after up/down averaging | 0.29 | 1.35 | 4.32 |
| Sensor span vs temperature (after auto-zero) | 0.19 | 0.48 | 0.97 |
| Pivot shift between tare and reading | 0.20 | 0.81 | 2.05 |
| Tare change (rain, ice, residue; heavy snow flagged) | 1.00 | 2.00 | 6.00 |
| Centre of mass x_w (fill model, ticket-calibrated) | 2.00 | 3.00 | 5.00 |
| Geometry / gain after tickets (H2) | 0.30 | 0.50 | 1.00 |
| **combined (RSS)** | **2.6** | **4.4** | **9.7** |

**C. two-end lift + H2 ticket calibration**, 2.5 t of waste (1σ, % of the waste mass)

| source | low | mid | high |
|---|---|---|---|
| Pressure sensor repeatability (tare + reading) | 1.21 | 1.81 | 3.02 |
| Seal friction left after up/down averaging | 0.29 | 1.35 | 4.32 |
| Sensor span vs temperature (after auto-zero) | 0.19 | 0.48 | 0.97 |
| Pivot shift between tare and reading | 0.20 | 0.81 | 2.05 |
| Tare change (rain, ice, residue; heavy snow flagged) | 1.00 | 2.00 | 6.00 |
| Two-end lift: W and x_w solved, residual geometry | 0.30 | 0.50 | 1.00 |
| Geometry / gain after tickets (H2) | 0.30 | 0.50 | 1.00 |
| **combined (RSS)** | **1.7** | **3.2** | **8.4** |


### Summary

| H7 case (1σ, % of waste mass, low / mid / high) | 2.5 t (typical pick-up) | 5 t (full) |
|---|---|---|
| A. one-point, no tickets | 5.3 / 10.7 / 21.9 | 5.2 / 10.3 / 20.7 |
| B. one-point + H2 tickets | 2.6 / 4.4 / 9.7 | 2.2 / 3.5 / 6.8 |
| C. two-end lift + H2 tickets | 1.7 / 3.2 / 8.4 | 0.9 / 1.9 / 4.8 |

Fused with the virtual scale (7.6 % median error after 5 tickets, synthetic; ≈ 11.3 % as 1σ): case B at 2.5 t → 2.5 / 4.1 / 7.4 % if the two errors were independent (they are not fully: both learn from the same tickets).


Absolute floor (sensor + friction + tare change), kg of waste: 40 / 80 / 200. Pivot shift: 2.05 % at 5 cm (review row 2 estimated ~0.8 % without the machine term).
