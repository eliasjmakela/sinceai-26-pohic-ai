"""Temperature error of H1 (plate cells, differential reading) and H5 (rail cells, re-tare at each exchange).

    python calc/temperature.py      -> generated/calc_temperature.md

Load-cell temperature coefficients from the Flintec SSB5 datasheet [20]: zero TC0 = 0.04 % of rated output per
10 C, span TC = 0.02 % of reading per 10 C, compensated range -10..+40 C. Smaller C3 cells are of the same order
(team assumption). Temperature swings: team estimate for an outdoor unit in Finland.
"""
from __future__ import annotations

import math

from calc_common import md_table, write

TC0 = 0.04 / 100 / 10      # fraction of rated output per C
TCS = 0.02 / 100 / 10      # fraction of reading per C

CASES = [
    # name, n cells, rated kg per cell, dT between zero/tare and reading (C), load kg, note
    ("H1 plate, one charge (reading before vs after the stroke, ~1 min apart)", 4, 500, 0.5, 18,
     "differential reading: only the drift within one press cycle counts"),
    ("H1 plate, if read against a daily zero instead", 4, 500, 10, 18, "why the design reads before/after each stroke"),
    ("H5 rails, COMBI: tare on return, read before pick-up", 4, 5000, 25, 3000, "tare and read days apart, sun vs night"),
    ("H5 rails, DUO: same", 4, 5000, 25, 3000, ""),
    ("H5 rails with 10 t cells", 4, 10000, 25, 3000, "zero TC scales with rated output"),
]


def main():
    rows = []
    for name, n, rated, dt, load, note in CASES:
        zero_uncorr = math.sqrt(n) * TC0 * rated * dt     # independent cells
        zero_corr = n * TC0 * rated * dt                   # all cells drift the same way (worst case)
        span = TCS * load * dt
        lo = math.hypot(zero_uncorr, span)
        hi = zero_corr + span
        rows.append([name, f"{dt:g}", f"{lo:.2f}–{hi:.2f}", f"{100 * lo / load:.2f}–{100 * hi / load:.2f}", note])
    text = ("# calc/temperature.py output (datasheet TCs [20], ΔT team estimate)\n\n"
            "Zero drift = TC0 × rated output × ΔT per cell (independent cells add as √n, correlated as n); span drift = "
            "TC × load × ΔT.\n\n"
            + md_table(["case", "ΔT °C", "error kg (independent–correlated)", "% of load", "note"], rows)
            + "\nReading: temperature is negligible for H1 because each charge is a before/after difference ~1 min apart, "
              "and small for H5 (≈0.3–0.7 % of a 3 t load with 5 t cells) because the system re-tares at every exchange; 10 t cells double it, which is why the design keeps 5 t cells and adds overload stops (calc/loads.py). Even for H1 a same-sign drift over a warming day adds only ~0.1 % to a container total. Below the "
              "cells' compensated range (−10 °C [20]) the datasheet gives no figure: winter performance is an engineer "
              "question (ENGINEER_QUESTIONS Q7). Ice and frost act mechanically, not through the TC (RED_TEAM R1).\n")
    write("temperature", text)
    print(text)


if __name__ == "__main__":
    main()
