"""H7 hydraulic self-lift (team idea, Plus-malli PDF [39]): statics, pressure range, friction band, error budget.

    python calc/h7_hydraulic.py   -> generated/calc_h7_hydraulic.md, generated/h7_budget.md, generated/h7_hydraulic.json

Principle: one cylinder near the door end of a COMBI, driven by the compactor's own power pack, lifts that end
~10 mm; the front of the runners is the pivot. Moments about the pivot with the unit at rest:
    R * L = M * x_m + W * x_w            (R cylinder force, M machine, W waste, x from the pivot)
    R0 * L = M * x_m                     (same, empty unit just returned)
    W = (R - R0) * L / x_w               (Plus-malli formula [39], checked in reviews/PLUS_MALLI_REVIEW.md row 1)
Force from pressure: R = p * A (single-acting, rod side vented; reading at rest; up/down average for friction).

Sources: machine mass and waste from calc/loads.py (Tommi [36], listings [18]); press-end share of the machine from
calc/loads.py REAR_SHARE (the cylinder sits at the other, door end); system pressure ~200 bar (Tommi [36], as quoted
in the Plus-malli review); everything else is a TEAM ESTIMATE (no drawings, no hardware): unit geometry, centre-of-mass
shares, seal friction, sensor class, pivot shift, tare change. Untested.
"""
from __future__ import annotations

import json
import math

from calc_common import G, GEN, md_table, write
from loads import COMBI_MACHINE_T, REAR_SHARE, WASTE_MAX_T

# ------------------------------------------------------------------------------------------------ geometry / loads
L_M = (5.0, 5.5, 6.0)                 # pivot (front of runners) to cylinder axis, m: unit 6-7 m long, cylinder 0.5-1 m from the door end [39] (team estimate)
S_MACHINE = (1 - REAR_SHARE[1], 1 - REAR_SHARE[0])   # x_m / L: share of the machine on the door end = 1 - press-end share (calc/loads.py)
S_WASTE = (0.45, 0.60, 0.75)          # x_w / L: waste centre of mass between press face and door (team estimate)
LOADS_T = (2.5, 5.0)                  # typical pick-up (synthetic mean ~2.3 t/lift, review row 6) and full (Tommi max [36])
P_SYSTEM_BAR = 200                    # compactor hydraulics "up to 200 bar" (Tommi [36], via the review)
BORES_MM = (63, 80)                   # ISO 3320 standard bores; 80 mm is the design choice (pressure margin)
DESIGN_BORE = 80
STROKE_MM, LIFT_MM, FOOT_GAP_MM = 50, 10, 30   # Plus-malli [39]: 50 mm stroke, foot 30 mm above runner bottom, 10 mm lift
LIFT_S = 15                           # slow lift and lower, 15 s each [39]
FOOT_M = 0.30                         # 300 x 300 mm ball-joint foot [39]
BEARING_MPA = [("concrete slab", 3.0), ("dense asphalt, cold", 1.0), ("asphalt, hot summer day", 0.4),
               ("compacted gravel", 0.3), ("soft ground / thawing frost", 0.1)]   # allowable bearing, order of magnitude (team estimate)

# ------------------------------------------------------------------------------------------------ error model (1 sigma, low / mid / high)
SENSOR_FS_BAR = 250
SENSOR_REPEAT_PCT_FS = (0.10, 0.15, 0.25)   # non-repeatability + hysteresis of an industrial 0-250 bar transducer, after auto-zero (team estimate)
FRICTION_KN = (0.3, 0.7, 1.5)               # seal + guide breakaway friction of an 80 mm cylinder; high = cold seals (team estimate)
FRICTION_ASYM = (0.10, 0.20, 0.30)          # share of friction NOT cancelled by averaging lift and lower (stick-slip, speed asymmetry; team estimate)
SPAN_TEMP_PCT = (0.10, 0.25, 0.50)          # sensor span drift between tare and reading after auto-zero, % of R (team estimate)
PIVOT_SHIFT_CM = (0.5, 2.0, 5.0)            # pivot moves between tare and pick-up reading (settling, frost, unit nudged; team estimate)
TARE_CHANGE_KG = (25, 50, 150)              # rain water, ice, residue on the unit between tare and reading; heavy snow flagged, not included (team estimate)
COM_UNCAL_PCT = (5, 10, 20)                 # x_w unknown, fixed design value used (team estimate; review: +-10 cm on 3 m = 3 %)
COM_CAL_PCT = (2, 3, 5)                     # x_w from a fill/ram-position model learned from tickets: container-to-container residual (team estimate, same as H1's floor)
GEOM_TWO_END_PCT = (0.3, 0.5, 1.0)          # two-end lift solves W and x_w; residual from pivot/cylinder positions (team estimate)
GAIN_UNCAL_PCT = (1, 2, 3)                  # L, x_w design tolerance and sensor gain before any ticket (team estimate)
GAIN_CAL_PCT = (0.3, 0.5, 1.0)              # after H2 ticket calibration (team estimate)
VIRTUAL_SCALE_PCT = {"uncalibrated": 8.3, "after_5_tickets": 7.6, "monthly": 5.5}   # pipeline virtual_scale headline: MEDIAN |error| (synthetic, optimistic)
MEDIAN_ABS_TO_SIGMA = 1 / 0.6745      # a normal error's median |e| is 0.6745 sigma; this budget is 1 sigma
LEVELS = ("low", "mid", "high")


def area_m2(bore_mm):
    return math.pi * (bore_mm / 1000) ** 2 / 4


def bar(f_n, bore_mm):
    return f_n / area_m2(bore_mm) / 1e5


def statics():
    """Cylinder force and pressure, empty and full, envelope over machine mass, shares and L."""
    out = []
    empty = [M * 1000 * G * s for M in COMBI_MACHINE_T for s in S_MACHINE]
    full = [(M * S + WASTE_MAX_T * w) * 1000 * G for M in COMBI_MACHINE_T for S in S_MACHINE for w in (S_WASTE[0], S_WASTE[2])]
    for name, f in (("empty unit (tare R0)", empty), (f"full, {WASTE_MAX_T:.0f} t waste (R)", full)):
        row = [name, f"{min(f) / 1000:.0f}–{max(f) / 1000:.0f}"]
        row += [f"{bar(min(f), b):.0f}–{bar(max(f), b):.0f}" for b in BORES_MM]
        out.append(row)
    return out, min(empty), max(full)


def pivot_effect(delta_m):
    """Relative error of W when the pivot moves by delta between tare and reading (mid geometry, 2.5 t)."""
    L, sw, sm, M, W = L_M[1], S_WASTE[1], sum(S_MACHINE) / 2, sum(COMBI_MACHINE_T) / 2, LOADS_T[0]
    xm, xw = sm * L, sw * L
    r0 = M * xm / L
    r = (M * (xm - delta_m) + W * (xw - delta_m)) / (L - delta_m)
    w_hat = (r - r0) * L / xw
    return abs(w_hat - W) / W * 100


def budget(load_t, case):
    """1-sigma components in % of the waste mass W for one reading pair (tare, pick-up)."""
    a = area_m2(DESIGN_BORE)
    sw = S_WASTE[1]
    rows = []
    for i, lvl in enumerate(LEVELS):
        sig_w_n = load_t * 1000 * G * sw                     # signal: R - R0
        r_n = (sum(COMBI_MACHINE_T) / 2 * sum(S_MACHINE) / 2 + load_t * sw) * 1000 * G
        c = {}
        c["Pressure sensor repeatability (tare + reading)"] = SENSOR_REPEAT_PCT_FS[i] / 100 * SENSOR_FS_BAR * 1e5 * a * math.sqrt(2) / sig_w_n * 100
        c["Seal friction left after up/down averaging"] = FRICTION_KN[i] * 1000 * FRICTION_ASYM[i] * math.sqrt(2) / sig_w_n * 100
        c["Sensor span vs temperature (after auto-zero)"] = SPAN_TEMP_PCT[i] / 100 * r_n / sig_w_n * 100
        c["Pivot shift between tare and reading"] = pivot_effect(PIVOT_SHIFT_CM[i] / 100)
        c["Tare change (rain, ice, residue; heavy snow flagged)"] = TARE_CHANGE_KG[i] / (load_t * 1000) * 100
        if case == "A":
            c["Centre of mass x_w (fixed design value)"] = COM_UNCAL_PCT[i]
            c["Geometry / gain before tickets"] = GAIN_UNCAL_PCT[i]
        elif case == "B":
            c["Centre of mass x_w (fill model, ticket-calibrated)"] = COM_CAL_PCT[i]
            c["Geometry / gain after tickets (H2)"] = GAIN_CAL_PCT[i]
        else:
            c["Two-end lift: W and x_w solved, residual geometry"] = GEOM_TWO_END_PCT[i]
            c["Geometry / gain after tickets (H2)"] = GAIN_CAL_PCT[i]
        rows.append(c)
    return rows


def rss(d):
    return math.sqrt(sum(v * v for v in d.values()))


def main():
    out = ["# calc/h7_hydraulic.py output: H7 hydraulic self-lift (team estimate; order of magnitude, untested)\n"]
    st, f_empty_min, f_full_max = statics()
    out.append("## H7: statics and pressure\n")
    out.append(f"Moments about the front pivot: R·L = M·x_m + W·x_w; tare R0·L = M·x_m → **W = (R − R0)·L / x_w**. "
               f"Machine {COMBI_MACHINE_T[0]}–{COMBI_MACHINE_T[1]} t with {S_MACHINE[0]:.2f}–{S_MACHINE[1]:.2f} of it on the "
               f"door end (1 − press-end share of calc/loads.py), waste up to {WASTE_MAX_T:.0f} t at x_w/L = "
               f"{S_WASTE[0]}–{S_WASTE[2]}, L = {L_M[0]}–{L_M[2]} m (team estimate).\n")
    out.append(md_table(["case", "cylinder force kN"] + [f"pressure bar, {b} mm bore" for b in BORES_MM], st))
    p_hi = bar(f_full_max, DESIGN_BORE)
    out.append(f"\nDesign choice: **{DESIGN_BORE} mm bore**, ≤ {p_hi:.0f} bar at the heaviest case against ~{P_SYSTEM_BAR} bar "
               f"system pressure [36]; a 63 mm bore would need {bar(f_full_max, 63):.0f} bar, too close to the limit. "
               f"A relief valve set just above the design force makes an over-heavy unit simply not lift (flagged), "
               "so the cylinder can never lift more than it was designed for.\n")
    vol_cm3 = area_m2(DESIGN_BORE) * LIFT_MM / 1000 * 1e6
    flow = vol_cm3 / 1000 / (LIFT_S / 60)
    out.append(f"\nFlow: a {LIFT_MM} mm lift moves {vol_cm3:.0f} cm³ of oil; over {LIFT_S} s that is {flow:.2f} L/min, far below "
               "a power pack's flow, so a pressure-compensated flow-control (throttle) valve sets the slow constant speed "
               f"({LIFT_MM / LIFT_S:.2f} mm/s). Mechanical work {f_full_max * LIFT_MM / 1000 / 1000:.1f} kJ per lift: negligible; the "
               "cost is starting the pump.\n")
    stroke_left = STROKE_MM - FOOT_GAP_MM - LIFT_MM
    out.append(f"\nStroke: {STROKE_MM} mm − {FOOT_GAP_MM} mm to reach the ground − {LIFT_MM} mm lift = **{stroke_left} mm** left for "
               "unevenness, soft ground or a rail/plinth under the runners. If the stroke runs out before the pressure "
               "plateau, the firmware records 'no reading' instead of a wrong one.\n")
    rows = []
    for name, cap in BEARING_MPA:
        q = f_full_max / FOOT_M ** 2 / 1e6
        rows.append([name, f"{cap:g}", f"{q:.2f}", "ok" if q <= cap else f"needs a {math.sqrt(f_full_max / (cap * 1e6)) * 1000:.0f} mm square pad"])
    out.append(f"\n### Ground under the {FOOT_M * 1000:.0f} × {FOOT_M * 1000:.0f} mm foot (heaviest case {f_full_max / 1000:.0f} kN)\n")
    out.append(md_table(["ground", "allowable MPa (team estimate)", "foot pressure MPa", "verdict"], rows))

    # friction band
    rows = []
    for lvl, ff, asym in zip(LEVELS, FRICTION_KN, FRICTION_ASYM):
        rows.append([lvl, f"{ff:g}", f"{100 * ff * 1000 / f_empty_min:.1f}", f"{100 * ff * 1000 / f_full_max:.1f}",
                     f"{asym:.0%}", f"{100 * ff * 1000 * asym / f_full_max:.2f}"])
    out.append("\n## H7: seal friction band\n")
    out.append("Lifting, the pressure reads R + F_f; lowering, R − F_f. Averaging the two plateaus cancels symmetric (Coulomb) "
               "friction; stick-slip and speed asymmetry leave a residue (team estimate).\n\n")
    out.append(md_table(["level", "friction kN", "% of lightest tare force", "% of heaviest full force",
                         "not cancelled", "residue % of heaviest force"], rows))

    # error budget
    res = {}
    btxt = []
    for case, title in (("A", "A. one-point lift, no tickets"), ("B", "B. one-point lift + H2 ticket calibration"),
                        ("C", "C. two-end lift + H2 ticket calibration")):
        res[case] = {}
        for load in LOADS_T:
            b = budget(load, case)
            res[case][f"{load:g}t"] = {lvl: round(rss(b[i]), 1) for i, lvl in enumerate(LEVELS)}
            if load == LOADS_T[0]:
                rows = [[k] + [f"{b[i][k]:.2f}" for i in range(3)] for k in b[0]]
                rows.append(["**combined (RSS)**"] + [f"**{rss(b[i]):.1f}**" for i in range(3)])
                btxt.append(f"**{title}**, {load:g} t of waste (1σ, % of the waste mass)\n\n" +
                            md_table(["source", "low", "mid", "high"], rows))
    summ = [["A. one-point, no tickets"] + [f"{res['A'][f'{l:g}t']['low']} / {res['A'][f'{l:g}t']['mid']} / {res['A'][f'{l:g}t']['high']}" for l in LOADS_T],
            ["B. one-point + H2 tickets"] + [f"{res['B'][f'{l:g}t']['low']} / {res['B'][f'{l:g}t']['mid']} / {res['B'][f'{l:g}t']['high']}" for l in LOADS_T],
            ["C. two-end lift + H2 tickets"] + [f"{res['C'][f'{l:g}t']['low']} / {res['C'][f'{l:g}t']['mid']} / {res['C'][f'{l:g}t']['high']}" for l in LOADS_T]]
    vs = VIRTUAL_SCALE_PCT["after_5_tickets"]
    vs_sigma = vs * MEDIAN_ABS_TO_SIGMA
    fused = {lvl: round(1 / math.sqrt(1 / res["B"]["2.5t"][lvl] ** 2 + 1 / vs_sigma ** 2), 1) for lvl in LEVELS}
    summ_md = (md_table(["H7 case (1σ, % of waste mass, low / mid / high)", "2.5 t (typical pick-up)", "5 t (full)"], summ) +
               f"\nFused with the virtual scale ({vs} % median error after 5 tickets, synthetic; ≈ {vs_sigma:.1f} % as 1σ): case B at 2.5 t → "
               f"{fused['low']} / {fused['mid']} / {fused['high']} % if the two errors were independent (they are not fully: "
               "both learn from the same tickets).\n")
    floor_kg = {}
    for i, lvl in enumerate(LEVELS):
        sensor_n = SENSOR_REPEAT_PCT_FS[i] / 100 * SENSOR_FS_BAR * 1e5 * area_m2(DESIGN_BORE) * math.sqrt(2)
        friction_n = FRICTION_KN[i] * 1000 * FRICTION_ASYM[i] * math.sqrt(2)
        force_kg = math.hypot(sensor_n, friction_n) / (G * S_WASTE[1])     # force error -> kg of waste at mid x_w/L
        floor_kg[lvl] = float(round(math.hypot(force_kg, TARE_CHANGE_KG[i]), -1))
    out.append("\n## H7: error budget (1σ of the waste mass from one tare + one pick-up reading)\n")
    out.append("\n".join(btxt))
    out.append("\n### Summary\n")
    out.append(summ_md)
    out.append(f"\nAbsolute floor (sensor + friction + tare change), kg of waste: {floor_kg['low']:.0f} / {floor_kg['mid']:.0f} / "
               f"{floor_kg['high']:.0f}. Pivot shift: {pivot_effect(0.05):.2f} % at 5 cm (review row 2 estimated ~0.8 % without the "
               "machine term).\n")
    text = "\n".join(out)
    write("h7_hydraulic", text)
    (GEN / "h7_budget.md").write_text(summ_md)
    js = {"evidence_tag": "estimate", "design_bore_mm": DESIGN_BORE,
          "force_kn": {"empty_min": round(f_empty_min / 1000, 1), "full_max": round(f_full_max / 1000, 1)},
          "pressure_bar_design_bore": {"empty_min": round(bar(f_empty_min, DESIGN_BORE)), "full_max": round(bar(f_full_max, DESIGN_BORE))},
          "stroke_margin_mm": stroke_left, "sigma_rel_pct": res, "sigma_abs_kg_floor": floor_kg,
          "fused_with_virtual_scale_pct_2.5t": fused, "virtual_scale_pct": VIRTUAL_SCALE_PCT}
    (GEN / "h7_hydraulic.json").write_text(json.dumps(js, indent=1) + "\n")
    print(text)


if __name__ == "__main__":
    main()
