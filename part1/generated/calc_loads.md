# calc/loads.py output (team estimate; order of magnitude, untested)

## H1: impact of a thrown charge on the weighing plate

Energy E = m(g·h + v0²/2), h = 0.9–1.1 m, v0 = 1.5 m/s; peak force of a linear spring F = 2E/d + mg. Plate range 4 × 500 kg = 2 t, safe limit 150% = 3 t.

| charge | kg | stop distance mm | peak force kN | × static weight | seen as t |
|---|---|---|---|---|---|
| plastic film bag, 9 kg (kit median charge) | 9 | 80 | 2.3–2.8 | 26–31× | 0.24–0.28 |
| cardboard charge, 18 kg (kit median) | 18 | 50 | 7.3–8.8 | 42–50× | 0.75–0.89 |
| biowaste bag, 30 kg (kit median) | 30 | 30 | 20.2–24.1 | 69–82× | 2.06–2.46 |
| dense item thrown hard, 25 kg (misuse) | 25 | 5 | 99.8–119.4 | 407–487× | 10.17–12.17 |


Worst case ≈ 12.2 t against a 3 t safe limit: **overload stops are required**; a cardboard charge (0.89 t) stays inside the cell range and a biowaste bag (2.5 t) inside the safe limit.


## H1: vertical load on the plate during the compaction stroke

Ram pressure p = 25 t / 1.20 m² = 204 kPa; vertical floor pressure K·p with K = 0.3–0.6; plate 1.12 m² → **7–14 t** on the plate on every stroke, 3–7× the cell range. The stops carry this; the cells see only what the stop gap lets through. Readings are valid only with the ram retracted.


Stop gap: set at ~120 % of rated deflection, i.e. **0.24–0.48 mm** (cells deflect 0.2–0.4 mm at rated load [19]). A gap this small jams with grit or ice unless sealed (RED_TEAM R3). An elastomer layer would allow a few mm of travel but adds creep and hysteresis (team estimate).


Signal-to-range: a 9–30 kg charge is 0.4%–1.5% of the 2 t range. C3 cells have 0.017 % combined error [8][22] (≈0.3 kg on 2 t), so a charge reads to about ±1–3 % electrically; mechanics (bridging, friction) dominate (calc/error_accumulation.py).


## H5: loads on the four rail cells

| case | total t | per cell, even t | heavier pair, per cell t | × dynamic 1.5 | cell rated / safe limit |
|---|---|---|---|---|---|
| COMBI full (machine + waste) | 8.0–9.5 | 2.0–2.4 | 2.2–3.3 | 3.3–5.0 | 5 t / 10 t |
| DUO full (container + waste) | 10.0–11.0 | 2.5–2.8 | 2.8–3.8 | 4.1–5.8 | 5 t / 10 t |


Pick-up of a full COMBI: when the hook lifts the front, the rear pair carries up to ~80% of 9.5 t → **5.7 t per rear cell** with the dynamic factor: inside a 5 t cell's 200 % safe limit [20] but with little margin. Overload stops under the rear pair give that margin; 10 t cells would too but double the zero drift (calc/temperature.py), so the design keeps 5 t cells + stops (team estimate).


## H5: set-down impact of an empty COMBI (front half on the front pair of cells)

Peak force F = √(2E·k_eff) + mg, cell stiffness 1.6e+08 N/m each (0.3 mm at 5 t [19]).


| set-down speed m/s | rail stiffness N/m | energy J | peak per front cell t |
|---|---|---|---|
| 0.05 | 2.5e+07 | 3 | 1.7 |
| 0.05 | 5.0e+07 | 3 | 1.9 |
| 0.05 | rigid rail | 3 | 3.3 |
| 0.20 | 2.5e+07 | 45 | 3.5 |
| 0.20 | 5.0e+07 | 45 | 4.3 |
| 0.20 | rigid rail | 45 | 9.9 |


At the higher set-down speed on a stiff rail the peak reaches the 10 t safe limit of a 5 t cell (no margin for a faster or uneven drop): **overload stops (or 10 t cells plus a compliant pad) are required**; slow set-down on a flexible rail stays inside it.


## H5: horizontal force when the hook-lift pulls the unit on or off

Rolling rollers μ ≈ 0.05 → 0.5 t; sliding steel skids μ = 0.4–0.8 [21] → **3.8–7.6 t horizontal** on a 9.5 t unit. Shear-beam cells must not carry this: longitudinal and lateral check rods (stay rods) anchored to the base take it, as in tank weighing modules with lift-off and side restraint [23].


Signal-to-range: on a COMBI the cells carry the machine too, so a 1 t load is 18%–25% of the reading; the machine tare is removed by re-taring when the emptied unit returns.
