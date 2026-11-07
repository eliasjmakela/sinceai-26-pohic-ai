# calc/temperature.py output (datasheet TCs [20], ΔT team estimate)

Zero drift = TC0 × rated output × ΔT per cell (independent cells add as √n, correlated as n); span drift = TC × load × ΔT.

| case | ΔT °C | error kg (independent–correlated) | % of load | note |
|---|---|---|---|---|
| H1 plate, one charge (reading before vs after the stroke, ~1 min apart) | 0.5 | 0.02–0.04 | 0.11–0.22 | differential reading: only the drift within one press cycle counts |
| H1 plate, if read against a daily zero instead | 10 | 0.40–0.80 | 2.22–4.46 | why the design reads before/after each stroke |
| H5 rails, COMBI: tare on return, read before pick-up | 25 | 10.11–21.50 | 0.34–0.72 | tare and read days apart, sun vs night |
| H5 rails, DUO: same | 25 | 10.11–21.50 | 0.34–0.72 |  |
| H5 rails with 10 t cells | 25 | 20.06–41.50 | 0.67–1.38 | zero TC scales with rated output |

Reading: temperature is negligible for H1 because each charge is a before/after difference ~1 min apart, and small for H5 (≈0.3–0.7 % of a 3 t load with 5 t cells) because the system re-tares at every exchange; 10 t cells double it, which is why the design keeps 5 t cells and adds overload stops (calc/loads.py). Even for H1 a same-sign drift over a warming day adds only ~0.1 % to a container total. Below the cells' compensated range (−10 °C [20]) the datasheet gives no figure: winter performance is an engineer question (ENGINEER_QUESTIONS Q7). Ice and frost act mechanically, not through the TC (RED_TEAM R1).
