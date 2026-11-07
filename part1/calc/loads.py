"""First-principles load cases for H1 (hopper-stage weighing plate) and H5 (weighing guide rails).

    python calc/loads.py            -> prints the working, writes generated/calc_loads.md

Order-of-magnitude mechanics only (energy balance, linear springs, statics). The team has no mechanical-
engineering expertise: every result here is a sizing hint for an engineer to check, not a design.
Sources: [kit] configs/assumptions.yaml; [17] COMBI listing (infeed 1,500 x 900 mm, infeed height 1,480 mm,
compaction force 25 t); [18] COMBI empty-weight listings (4,010-4,435 kg); [Tommi] 7 Nov talk (~3 t machine,
up to ~5 t waste); [19] shear-beam deflection 0.2-0.5 mm at rated load; [20] Flintec SSB5 safe load 200 %,
ultimate 300 %; [21] steel-on-steel friction 0.4-0.8 dry. Everything else: team estimate.
"""
from __future__ import annotations

import math

from calc_common import G, kn_to_t, md_table, write

# ------------------------------------------------------------------------------------------------ H1 parameters
CHARGES = [  # (label, mass kg, extra drop m above free fall, stopping distance m)  -- team estimate except masses
    ("plastic film bag, 9 kg (kit median charge)", 9, 0.0, 0.08),
    ("cardboard charge, 18 kg (kit median)", 18, 0.0, 0.05),
    ("biowaste bag, 30 kg (kit median)", 30, 0.0, 0.03),
    ("dense item thrown hard, 25 kg (misuse)", 25, 0.0, 0.005),
]
DROP_M = (0.9, 1.1)          # infeed 1.48 m [17] minus chamber floor ~0.4-0.6 m above ground (team estimate)
THROW_V0 = 1.5               # m/s downward throw speed (team estimate)
PLATE_CELLS, PLATE_CELL_KG = 4, 500     # 4 x 500 kg C3 cells under the plate ([22] KERN CT 500) -> 2 t range
SAFE_LIMIT = 1.5             # conservative safe-load limit for small cells (150 %; SSB5 class is 200 % [20])
CELL_DEFL_MM = (0.2, 0.4)    # deflection at rated load [19]

RAM_FORCE_T = 25             # COMBI compaction force [17]
RAM_FACE_M2 = 1.5 * 0.8      # aperture width 1.5 m [17] x chamber height ~0.8 m (team estimate)
K_LATERAL = (0.3, 0.6)       # vertical/axial pressure ratio of compressed waste on the floor (team estimate)
PLATE_M2 = 1.4 * 0.8         # weighing plate in the charging zone (team estimate)

# ------------------------------------------------------------------------------------------------ H5 parameters
COMBI_MACHINE_T = (3.0, 4.5)   # Tommi ~3 t; listings 4.0-4.4 t [18]
WASTE_MAX_T = 5.0              # Tommi
DUO_CONTAINER_T = (2.0, 3.0)   # empty DUO container 20-30 m3 (team estimate)
DUO_WASTE_MAX_T = 8.0          # dataset p90 DUO mixed waste ticket 7.7 t (scripts output) rounded up
REAR_SHARE = (0.55, 0.70)      # share of weight on the press-end (heavier) pair of cells (team estimate)
RAIL_CELL_T = 5.0              # 4 x 5 t shear-beam cells (brief H5)
SAFE_RAIL = 2.0                # SSB5-class safe load limit 200 % [20]
DYN = 1.5                      # dynamic factor while the unit rolls on/off (team estimate)
SETDOWN_V = (0.05, 0.20)       # m/s vertical speed when the hook-lift sets the front down (team estimate)
K_CELL = RAIL_CELL_T * 1000 * G / 0.3e-3   # N/m per cell, 0.3 mm at rated load [19]
K_RAIL = (2.5e7, 5e7)          # N/m, rail beam flex 1-2 mm under ~5 t (team estimate)
MU_ROLL, MU_SLIDE = 0.05, (0.4, 0.8)   # rolling rollers (team estimate); dry steel skids [21]


def impact_rows():
    rows, notes = [], []
    for label, m, _, d in CHARGES:
        hi = []
        for h in DROP_M:
            e = m * (G * h + THROW_V0 ** 2 / 2)           # energy at impact, J
            f = 2 * e / d + m * G                         # linear-spring peak force + static weight, N
            hi.append(f)
        rows.append([label, m, f"{d * 1000:.0f}", f"{min(hi) / 1000:.1f}–{max(hi) / 1000:.1f}",
                     f"{min(hi) / (m * G):.0f}–{max(hi) / (m * G):.0f}×",
                     f"{kn_to_t(min(hi)):.2f}–{kn_to_t(max(hi)):.2f}"])
        notes.append((label, max(hi)))
    return rows, notes


def main():
    out = ["# calc/loads.py output (team estimate; order of magnitude, untested)\n"]

    # ---- H1 impact
    rows, notes = impact_rows()
    cap_t = PLATE_CELLS * PLATE_CELL_KG / 1000
    out.append("## H1: impact of a thrown charge on the weighing plate\n")
    out.append(f"Energy E = m(g·h + v0²/2), h = {DROP_M[0]}–{DROP_M[1]} m, v0 = {THROW_V0} m/s; peak force of a linear "
               f"spring F = 2E/d + mg. Plate range {PLATE_CELLS} × {PLATE_CELL_KG} kg = {cap_t:.0f} t, safe limit "
               f"{SAFE_LIMIT:.0%} = {cap_t * SAFE_LIMIT:.0f} t.\n")
    out.append(md_table(["charge", "kg", "stop distance mm", "peak force kN", "× static weight", "seen as t"], rows))
    worst = max(f for _, f in notes)
    out.append(f"\nWorst case ≈ {kn_to_t(worst):.1f} t against a {cap_t * SAFE_LIMIT:.0f} t safe limit: **overload "
               f"stops are required**; a cardboard charge ({kn_to_t(notes[1][1]):.2f} t) stays inside the cell range and a biowaste bag ({kn_to_t(notes[2][1]):.1f} t) inside the safe limit.\n")

    # ---- H1 compaction
    p = RAM_FORCE_T * 1000 * G / RAM_FACE_M2
    fv = [k * p * PLATE_M2 for k in K_LATERAL]
    out.append("\n## H1: vertical load on the plate during the compaction stroke\n")
    out.append(f"Ram pressure p = {RAM_FORCE_T} t / {RAM_FACE_M2:.2f} m² = {p / 1000:.0f} kPa; vertical floor pressure "
               f"K·p with K = {K_LATERAL[0]}–{K_LATERAL[1]}; plate {PLATE_M2:.2f} m² → "
               f"**{kn_to_t(fv[0]):.0f}–{kn_to_t(fv[1]):.0f} t** on the plate on every stroke, "
               f"{kn_to_t(fv[0]) / cap_t:.0f}–{kn_to_t(fv[1]) / cap_t:.0f}× the cell range. The stops carry this; "
               "the cells see only what the stop gap lets through. Readings are valid only with the ram retracted.\n")
    gaps = [d * 1.2 for d in CELL_DEFL_MM]
    out.append(f"\nStop gap: set at ~120 % of rated deflection, i.e. **{gaps[0]:.2f}–{gaps[1]:.2f} mm** (cells deflect "
               f"{CELL_DEFL_MM[0]}–{CELL_DEFL_MM[1]} mm at rated load [19]). A gap this small jams with grit or ice "
               "unless sealed (RED_TEAM R3). An elastomer layer would allow a few mm of travel but adds creep and "
               "hysteresis (team estimate).\n")
    charge_frac = [m / (cap_t * 1000) for _, m, _, _ in CHARGES[:3]]
    out.append(f"\nSignal-to-range: a 9–30 kg charge is {min(charge_frac):.1%}–{max(charge_frac):.1%} of the 2 t range. "
               "C3 cells have 0.017 % combined error [8][22] (≈0.3 kg on 2 t), so a charge reads to about ±1–3 % "
               "electrically; mechanics (bridging, friction) dominate (calc/error_accumulation.py).\n")

    # ---- H5 statics
    out.append("\n## H5: loads on the four rail cells\n")
    rows = []
    for name, tare, waste in (("COMBI full (machine + waste)", COMBI_MACHINE_T, WASTE_MAX_T),
                              ("DUO full (container + waste)", DUO_CONTAINER_T, DUO_WASTE_MAX_T)):
        tot = (tare[0] + waste, tare[1] + waste)
        even = (tot[0] / 4, tot[1] / 4)
        rear = (tot[0] * REAR_SHARE[0] / 2, tot[1] * REAR_SHARE[1] / 2)
        dyn = (rear[0] * DYN, rear[1] * DYN)
        rows.append([name, f"{tot[0]:.1f}–{tot[1]:.1f}", f"{even[0]:.1f}–{even[1]:.1f}", f"{rear[0]:.1f}–{rear[1]:.1f}",
                     f"{dyn[0]:.1f}–{dyn[1]:.1f}", f"{RAIL_CELL_T:.0f} t / {RAIL_CELL_T * SAFE_RAIL:.0f} t"])
    out.append(md_table(["case", "total t", "per cell, even t", "heavier pair, per cell t",
                         f"× dynamic {DYN}", "cell rated / safe limit"], rows))
    # pickup: the hook lifts the front; the rear pair carries the remainder (assume up to rear share + 10 pp)
    tot_hi = COMBI_MACHINE_T[1] + WASTE_MAX_T
    pick = tot_hi * min(1.0, REAR_SHARE[1] + 0.1) / 2 * DYN
    out.append(f"\nPick-up of a full COMBI: when the hook lifts the front, the rear pair carries up to ~{min(1, REAR_SHARE[1] + 0.1):.0%} "
               f"of {tot_hi:.1f} t → **{pick:.1f} t per rear cell** with the dynamic factor: inside a 5 t cell's 200 % "
               "safe limit [20] but with little margin. Overload stops under the rear pair give that margin; 10 t cells "
               "would too but double the zero drift (calc/temperature.py), so the design keeps 5 t cells + stops (team estimate).\n")

    # ---- H5 set-down impact
    rows = []
    for v in SETDOWN_V:
        for kr in K_RAIL:
            m_half = COMBI_MACHINE_T[1] * 1000 / 2       # empty unit, front half lands on the front pair
            e = 0.5 * m_half * v ** 2
            k_pair = 2 * K_CELL
            k_eff = 1 / (1 / k_pair + 1 / kr)
            f = math.sqrt(2 * e * k_eff) + m_half * G
            rows.append([f"{v:.2f}", f"{kr:.1e}", f"{e:.0f}", f"{kn_to_t(f) / 2:.1f}"])
        f_rigid = math.sqrt(2 * 0.5 * COMBI_MACHINE_T[1] * 500 * v ** 2 * 2 * K_CELL) + COMBI_MACHINE_T[1] * 500 * G
        rows.append([f"{v:.2f}", "rigid rail", f"{0.5 * COMBI_MACHINE_T[1] * 500 * v ** 2:.0f}", f"{kn_to_t(f_rigid) / 2:.1f}"])
    out.append("\n## H5: set-down impact of an empty COMBI (front half on the front pair of cells)\n")
    out.append(f"Peak force F = √(2E·k_eff) + mg, cell stiffness {K_CELL:.1e} N/m each (0.3 mm at 5 t [19]).\n\n")
    out.append(md_table(["set-down speed m/s", "rail stiffness N/m", "energy J", "peak per front cell t"], rows))
    out.append("\nAt the higher set-down speed on a stiff rail the peak reaches the 10 t safe limit of a 5 t cell (no margin for a faster or uneven drop): "
               "**overload stops (or 10 t cells plus a compliant pad) are required**; slow set-down on a flexible "
               "rail stays inside it.\n")

    # ---- H5 horizontal
    w = tot_hi * 1000 * G
    out.append("\n## H5: horizontal force when the hook-lift pulls the unit on or off\n")
    out.append(f"Rolling rollers μ ≈ {MU_ROLL} → {kn_to_t(MU_ROLL * w):.1f} t; sliding steel skids μ = {MU_SLIDE[0]}–{MU_SLIDE[1]} [21] → "
               f"**{kn_to_t(MU_SLIDE[0] * w):.1f}–{kn_to_t(MU_SLIDE[1] * w):.1f} t horizontal** on a {tot_hi:.1f} t unit. "
               "Shear-beam cells must not carry this: longitudinal and lateral check rods (stay rods) anchored to the "
               "base take it, as in tank weighing modules with lift-off and side restraint [23].\n")
    # ---- H5 signal
    out.append(f"\nSignal-to-range: on a COMBI the cells carry the machine too, so a 1 t load is "
               f"{1 / (COMBI_MACHINE_T[0] + 1):.0%}–{1 / (COMBI_MACHINE_T[1] + 1):.0%} of the reading; the machine "
               "tare is removed by re-taring when the emptied unit returns.\n")

    text = "\n".join(out)
    write("loads", text)
    print(text)


if __name__ == "__main__":
    main()
