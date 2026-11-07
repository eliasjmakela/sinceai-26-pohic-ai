"""H6: full installed cost per device for every candidate, retrofit and factory-fit, over a 6-year lease.

    python calc/installed_cost.py   -> generated/calc_installed_cost.md, part1/installed_cost.json

Every line is a (low, high) EUR range with its source: a reference id [n] from WEIGHING_CONCEPT.md or "team
estimate". Labour lines are hours x rate, with the rate range RATE_EUR_H. Prices exclude VAT. FX (team assumption):
1 USD = 0.85-0.95 EUR, 1 INR = 0.0095-0.011 EUR. Lines are summed low-with-low and high-with-high, so the total is a
wide envelope, not a confidence interval.

Lines (brief H6): sensors, electronics, mechanical parts, site work, labour, calibration and commissioning,
maintenance / replacement over 6 years, and development cost amortised per unit (NRE; not asked, added for honesty).
"""
from __future__ import annotations

import json

from calc_common import PART1, md_table, write

RATE_EUR_H = (55, 90)        # technician rate: [24] fitter 55 EUR/h ex VAT; high end team estimate ([37] lists 152 for expert on-site)
REFERENCE_EUR = 2000         # ~EUR 2,000 option price Tommi named [36]
COMBI_PRICE_EUR = (20000, 25000)   # basic COMBI [36]
LEASE_YEARS = 6

# NRE: development + firmware + testing, amortised over the units that get it (team estimate)
NRE_UNITS = (2000, 5000)


def nre(lo_eur, hi_eur):
    return (round(lo_eur / NRE_UNITS[1]), round(hi_eur / NRE_UNITS[0]))


def lab(h_lo, h_hi):
    return (h_lo * RATE_EUR_H[0], h_hi * RATE_EUR_H[1])


# Each line: (H6 line, item, retrofit (lo, hi), factory-fit (lo, hi), source)
CANDIDATES = {
    "H1": {
        "name": "Hopper-stage weighing plate (idea: Europress / Tommi)",
        "lines": [
            ("sensors", "4 × 500 kg C3 IP68 cells under the plate", (100, 880), (100, 880),
             "[22] €220 each list; low end [25] ≈€12 per cell + team estimate for volume C3"),
            ("electronics", "4-channel 24-bit ADC / weighing board on the SMART modem, junction", (25, 180), (20, 150),
             "[6] HX711 board, [10] €51.95 transmitter, [9] €130 junction box; team estimate"),
            ("mechanical", "plate 1.4 × 0.8 m wear steel, cell mounts, overload stops, side stays, perimeter seal",
             (400, 1000), (150, 400), "team estimate (retrofit: cut the chamber floor and weld a sub-frame)"),
            ("site work", "none on site; COMBI retrofit: hook-lift round trip to a workshop", (0, 400), (0, 0), "team estimate"),
            ("labour", "retrofit 10–20 h (cut, weld, fit, wire); factory 2–4 h on the line", lab(10, 20), lab(2, 4),
             "hours team estimate × rate [24]"),
            ("calibration", "test weights (4 × 25 kg) on the plate, firmware set-up", lab(1, 2), lab(0.5, 1),
             "team estimate × rate [24]"),
            ("maintenance (6 y)", "clean the seal gap at each service (0.25 h/yr), new seal, 30–40 % chance of one cell",
             (6 * 0.25 * RATE_EUR_H[0] + 20 + 0.3 * 25, 6 * 0.25 * RATE_EUR_H[1] + 60 + 0.4 * 220),
             (6 * 0.25 * RATE_EUR_H[0] + 20 + 0.3 * 25, 6 * 0.25 * RATE_EUR_H[1] + 60 + 0.4 * 220), "team estimate"),
            ("development (NRE)", "plate design per machine family, firmware gating, field test: €150–400k", nre(150e3, 400e3),
             nre(150e3, 400e3), "team estimate"),
        ],
    },
    "H5": {
        "name": "Weighing guide rails (idea: team)",
        "lines": [
            ("sensors", "4 × 5 t shear-beam C3 IP68 cells", (900, 1740), (900, 1740),
             "[26] Zemic BM8H $262.50 ≈ €225–250; [8] KERN CT 5000 €435"),
            ("electronics", "IP68 summing box + weighing transmitter to the SMART modem", (110, 460), (110, 460),
             "[9] €130 box (low: board-level summing, team estimate), [10] €51.95–[11] $350 transmitter"),
            ("mechanical", "rail modification and cell seats, overload stops, lift-off and side restraint (check rods)",
             (500, 1400), (300, 900), "team estimate; [23] a 5 t weigh module with lift-off/tip protection lists $1,225"),
            ("site work", "level and anchor two rail bases (concrete pads), cable conduit to the unit",
             (800, 2500), (300, 1000), "team estimate (factory-fit = new site where the base is being built anyway)"),
            ("labour", "retrofit 12–24 h (2 technicians); new installation 6–12 h extra", lab(12, 24), lab(6, 12),
             "hours team estimate × rate [24]"),
            ("calibration", "known load on the rails (water IBCs or hired test weights), commissioning",
             (150, 800), (150, 800), "team estimate"),
            ("maintenance (6 y)", "clean under the rails, ice and debris checks 0.5–1 h/yr; 30–60 % chance of one cell; cable repair",
             (6 * 0.5 * RATE_EUR_H[0] + 0.3 * 225 + 50, 6 * 1 * RATE_EUR_H[1] + 0.6 * 435 + 200),
             (6 * 0.5 * RATE_EUR_H[0] + 0.3 * 225 + 50, 6 * 1 * RATE_EUR_H[1] + 0.6 * 435 + 200), "team estimate"),
            ("development (NRE)", "rail design, restraint, firmware: €50–150k", nre(50e3, 150e3), nre(50e3, 150e3), "team estimate"),
        ],
    },
    "T0": {
        "name": "Virtual weight from existing pressure + fill (v1)",
        "lines": [
            ("sensors", "none (existing pressure, ram position, fill)", (0, 0), (0, 0), "[3] existing sensors"),
            ("electronics", "none, or a faster pressure log", (0, 50), (0, 50), "team estimate"),
            ("mechanical", "none", (0, 0), (0, 0), "–"),
            ("site work", "none", (0, 0), (0, 0), "–"),
            ("labour", "remote firmware update; 0–1 h on site", lab(0, 1), lab(0, 0), "team estimate × rate [24]"),
            ("calibration", "learned from shared weighbridge tickets (H2)", (0, 0), (0, 0), "scripts/self_calibration.py"),
            ("maintenance (6 y)", "none beyond software", (0, 0), (0, 0), "team estimate"),
            ("development (NRE)", "model, firmware, back end: €50–150k", nre(50e3, 150e3), nre(50e3, 150e3), "team estimate"),
        ],
    },
    "T1": {
        "name": "Strain gauges on frame / container rails (v1 choice)",
        "lines": [
            ("sensors", "16 foil gauges for 4 full bridges", (25, 280), (25, 280), "[4][5]"),
            ("electronics", "24-bit bridge board, temperature sensor, connector", (10, 60), (10, 60), "[6][7] + team estimate"),
            ("mechanical", "gauge covers, coating, cable, glands, enclosure", (60, 140), (60, 140), "team estimate (v1 §4)"),
            ("site work", "none", (0, 0), (0, 0), "–"),
            ("labour", "retrofit 4–8 h; factory 1–3 h", lab(4, 8), lab(1, 3), "v1 §5 hours × rate [24]"),
            ("calibration", "water IBC (~1 t) at two positions, 1–1.5 h", lab(1, 1.5), lab(0.5, 1), "v1 §6 × rate [24]"),
            ("maintenance (6 y)", "30–60 % chance of re-gauging one point (2–4 h + parts)",
             (0.3 * (2 * RATE_EUR_H[0] + 20), 0.6 * (4 * RATE_EUR_H[1] + 80)),
             (0.3 * (2 * RATE_EUR_H[0] + 20), 0.6 * (4 * RATE_EUR_H[1] + 80)), "team estimate"),
            ("development (NRE)", "gauge layout per family, test rig, firmware: €50–150k", nre(50e3, 150e3), nre(50e3, 150e3), "team estimate"),
        ],
    },
    "T2": {
        "name": "Load cells under the unit's own frame (v1)",
        "lines": [
            ("sensors", "4 × 5 t shear-beam C3 cells", (900, 1740), (900, 1740), "[26][8]"),
            ("electronics", "summing box + transmitter", (110, 460), (110, 460), "[9][10][11]"),
            ("mechanical", "cell mounts in the frame, frame adaptation, stops", (200, 600), (150, 400), "team estimate (v1 §4)"),
            ("site work", "none (cells travel with a COMBI)", (0, 0), (0, 0), "–"),
            ("labour", "retrofit 8–16 h; factory 3–6 h", lab(8, 16), lab(3, 6), "v1 §5 hours × rate [24]"),
            ("calibration", "known load, commissioning", (150, 500), (150, 500), "team estimate"),
            ("maintenance (6 y)", "cells travel with a COMBI: 40–80 % chance of one cell, cable", (0.4 * 225 + 50, 0.8 * 435 + 200),
             (0.4 * 225 + 50, 0.8 * 435 + 200), "team estimate"),
            ("development (NRE)", "frame redesign per family, structural review: €100–300k", nre(100e3, 300e3), nre(100e3, 300e3), "team estimate"),
        ],
    },
    "PS": {
        "name": "Platform scale under the whole unit (Europress's existing option)",
        "lines": [
            ("sensors", "4–6 heavy cells (included in the platform price)", (0, 0), (0, 0), "in the line below"),
            ("electronics", "indicator / transmitter (included)", (0, 0), (0, 0), "in the line below"),
            ("mechanical", "steel weighing platform or beams with ramps, ~15 t", (4800, 12000), (4800, 12000),
             "[27] container scale €4,800–5,620 (beams + ramps, 15 t); full deck high end team estimate"),
            ("site work", "foundation or pit, ramps, anchoring, drainage", (2000, 6000), (1500, 5000), "team estimate"),
            ("labour", "16–32 h retrofit; 12–24 h new site", lab(16, 32), lab(12, 24), "team estimate × rate [24]"),
            ("calibration", "test weights by a scale service", (400, 1500), (400, 1500), "team estimate"),
            ("maintenance (6 y)", "annual check, cleaning, one cell", (500, 1500), (500, 1500), "team estimate"),
            ("development (NRE)", "exists today", (0, 0), (0, 0), "[36]"),
        ],
    },
}
ORDER = ["T0", "T1", "H1", "H5", "T2", "PS"]
HARDWARE = ("sensors", "electronics", "mechanical")


def totals(c, key):
    i = 2 if key == "retrofit" else 3
    lo = sum(l[i][0] for l in c["lines"])
    hi = sum(l[i][1] for l in c["lines"])
    return round(lo), round(hi)


def hw(c):
    return round(sum(l[3][0] for l in c["lines"] if l[0] in HARDWARE)), round(sum(l[3][1] for l in c["lines"] if l[0] in HARDWARE))


def main():
    out = ["# calc/installed_cost.py output: full installed cost per device (EUR, ex VAT, 6-year lease)\n",
           f"Labour at €{RATE_EUR_H[0]}–{RATE_EUR_H[1]}/h [24]. Reference: ~€{REFERENCE_EUR:,} weighing option on a "
           f"€{COMBI_PRICE_EUR[0]:,}–{COMBI_PRICE_EUR[1]:,} COMBI [36]. Lines summed low-with-low, high-with-high.\n"]
    summary = []
    js = {"currency": "EUR", "vat": "excluded", "lease_years": LEASE_YEARS, "labour_eur_per_h": list(RATE_EUR_H),
          "reference_option_eur": REFERENCE_EUR, "evidence_tag": "estimate", "candidates": {}}
    for cid in ORDER:
        c = CANDIDATES[cid]
        rows = [[l[0], l[1], f"€{l[2][0]:,.0f}–{l[2][1]:,.0f}", f"€{l[3][0]:,.0f}–{l[3][1]:,.0f}", l[4]] for l in c["lines"]]
        r, f = totals(c, "retrofit"), totals(c, "factory")
        rows.append(["**total**", "", f"**€{r[0]:,}–{r[1]:,}**", f"**€{f[0]:,}–{f[1]:,}**", "sum of lines"])
        out.append(f"\n## {cid}: {c['name']}\n")
        out.append(md_table(["H6 line", "what", "retrofit", "factory-fit", "source"], rows))
        h = hw(c)
        summary.append([cid, c["name"], f"€{h[0]:,}–{h[1]:,}", f"€{r[0]:,}–{r[1]:,}", f"€{f[0]:,}–{f[1]:,}",
                        "yes" if f[1] <= REFERENCE_EUR else ("partly" if f[0] <= REFERENCE_EUR else "no")])
        js["candidates"][cid] = {"name": c["name"], "hardware_eur": {"low": h[0], "high": h[1]},
                                 "retrofit_eur": {"low": r[0], "high": r[1]}, "factory_fit_eur": {"low": f[0], "high": f[1]},
                                 "lines": [{"line": l[0], "item": l[1], "retrofit": [round(l[2][0]), round(l[2][1])],
                                            "factory_fit": [round(l[3][0]), round(l[3][1])], "source": l[4]} for l in c["lines"]]}
    summ = md_table(["id", "candidate", "hardware (factory)", "installed, retrofit", "installed, factory-fit",
                     f"factory-fit within ~€{REFERENCE_EUR:,}?"], summary)
    write("installed_cost_summary", summ)
    out.insert(2, "\n## Summary\n\n" + summ)
    text = "\n".join(out)
    write("installed_cost", text)
    (PART1 / "installed_cost.json").write_text(json.dumps(js, indent=1, ensure_ascii=False) + "\n")
    print(text)


if __name__ == "__main__":
    main()
