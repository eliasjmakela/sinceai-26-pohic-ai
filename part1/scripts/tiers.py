"""Single source of truth for the weighing tiers (v1: T0/T1/T2; v2: H1 hopper plate, H5 weighing rails, PS platform
scale; H7 hydraulic self-lift) and the T1 error budget.

v2: H1's sigma comes from generated/self_calibration.json (fleet self-calibration after >= 10 tickets) and every
tier's BOM from part1/installed_cost.json (hardware lines, factory-fit), so run calc/installed_cost.py and
scripts/self_calibration.py first (reproduce.sh does). T1's budget gained a support-position line (RED_TEAM R9).

Writes:
  part1/sigma_tiers.json            interface for the app (shape fixed by briefs/PART1_WEIGHING.md section 4)
  part1/generated/tiers_table.md    comparison table pasted into WEIGHING_CONCEPT.md (checked by check_interface.py)
  part1/generated/error_budget.md   T1 error budget table
  part1/figures/error_budget.svg    T1 error budget chart

No dataset input. Every number here is a team estimate or a literature value; the [n] ids point to the reference
list in WEIGHING_CONCEPT.md. sigma values are 1-standard-deviation errors of one load weight.
"""
from __future__ import annotations

import json
import math

from common import GEN, INK, INK2, PART1, S1, TIER_COLOR, save_svg, style

import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------------------------------------------
# T1 error budget: 1-sigma contribution in % of a ~3 t load, (low, mid, high). Team estimates, reasoning in D1 sec 8.
ERROR_BUDGET_T1 = [
    # (component, low, mid, high, what keeps it down)
    ("Reading noise (bridge + 24-bit ADC, averaged)", 0.2, 0.3, 0.5, "average 10-30 s of samples at rest [7]"),
    ("Temperature drift (-30..+35 C)", 0.5, 1.0, 1.5, "full bridges + board temperature model [14]"),
    ("Calibration gain/offset residual", 0.5, 0.8, 1.5, "reference weights + ticket cross-check"),
    ("Off-centre load / load path", 0.5, 1.0, 2.0, "4 points, sum of bridges"),
    ("Friction / hysteresis at supports", 0.5, 0.8, 1.5, "read after settling, ram retracted"),
    ("Residue + press-cycle disturbance", 0.3, 0.5, 1.0, "auto-zero after each lift; read only at rest"),
    ("Support position after each set-down (mainly COMBI; v2)", 0.5, 2.0, 4.0, "frame strain measures bending, not reactions: ticket cross-check"),
]


def rss(values):
    return math.sqrt(sum(v * v for v in values))


T1_SIGMA = {k: round(rss([row[i] for row in ERROR_BUDGET_T1]), 1) for i, k in ((1, "low"), (2, "mid"), (3, "high"))}

# Citations for the BOM cell of the comparison table (not part of the JSON shape).
BOM_CITE = {"T0": "team estimate (software only)", "T1": "[4][5][6][7] + team estimate", "T2": "[8][9][10][11][26] + team estimate",
            "H1": "[6][9][10][22][25] + team estimate", "H5": "[8][9][10][11][23][26] + team estimate",
            "PS": "[27] + team estimate", "H7": "[39] + team estimate"}
CHOSEN = "H7"  # 7 Nov evening: H7 on every new COMBI (WEIGHING_CONCEPT §0)
COST = json.loads((PART1 / "installed_cost.json").read_text())["candidates"]
CAL = json.loads((GEN / "self_calibration.json").read_text())["levels"]
H1_SIGMA = {l: round(CAL[l]["after_10_plus"]["fleet_h2_pct"], 1) for l in ("low", "mid", "high")}
# H7: one-point lift after H2 ticket calibration at a typical 2.5 t pick-up (calc/h7_hydraulic.py, case B)
H7 = json.loads((GEN / "h7_hydraulic.json").read_text())
H7_SIGMA = {l: float(H7["sigma_rel_pct"]["B"]["2.5t"][l]) for l in ("low", "mid", "high")}
H7_FLOOR = {l: float(H7["sigma_abs_kg_floor"][l]) for l in ("low", "mid", "high")}


def bom(tid):
    h = COST[tid]["hardware_eur"]
    return {"low": int(round(h["low"], -1)), "high": int(round(h["high"], -1))}

# ---------------------------------------------------------------------------------------------------------------
# Tier definitions. BOM ranges come from the BOM tables in D1 sec 4 (sum of line ranges, rounded to EUR 10).
TIERS = [
    {
        "id": "T0",
        "name": "Virtual weight (existing hydraulic pressure + fill)",
        "principle": "Estimate the load from the existing hydraulic back-pressure fingerprint, ram position and fill "
                     "level with a per-device density model calibrated against shared weighbridge tickets.",
        "sigma_rel_pct": {"low": 5.0, "mid": 10.0, "high": 20.0},
        "sigma_abs_kg": {"low": 100.0, "mid": 150.0, "high": 300.0},
        "bom_eur_per_device": bom("T0"),
        "install_hours": {"low": 0, "high": 1},
        "suits": ["COMBI", "DUO"],
        "weak_for": ["BIOWASTE", "WET_CARDBOARD", "MIXED_WASTE"],
        "evidence_tag": "estimate",
        "sources": ["[1]", "[3]", "[13]"],
    },
    {
        "id": "T1",
        "name": "Cheap strain gauges on frame / container rails",
        "principle": "Four strain-gauge full bridges on the load-carrying frame (COMBI) or the container rails (DUO) "
                     "read by a low-cost 24-bit bridge amplifier on the SMART modem, auto-zeroed after each lift.",
        "sigma_rel_pct": {"low": T1_SIGMA["low"], "mid": T1_SIGMA["mid"], "high": T1_SIGMA["high"]},
        "sigma_abs_kg": {"low": 20.0, "mid": 30.0, "high": 50.0},
        "bom_eur_per_device": bom("T1"),
        "install_hours": {"low": 4, "high": 8},
        "suits": ["COMBI", "DUO"],
        "weak_for": ["LOADS_UNDER_0.5T", "COMBI_SUPPORT_CHANGES"],
        "evidence_tag": "estimate",
        "sources": ["[4]", "[5]", "[6]", "[7]", "[14]"],
    },
    {
        "id": "T2",
        "name": "Shear-beam load cells under the frame",
        "principle": "Four C3 shear-beam load cells under the DUO container frame or the COMBI base frame, a summing "
                     "box and a weighing transmitter connected to the SMART modem.",
        "sigma_rel_pct": {"low": 0.3, "mid": 0.6, "high": 1.0},
        "sigma_abs_kg": {"low": 10.0, "mid": 15.0, "high": 25.0},
        "bom_eur_per_device": bom("T2"),
        "install_hours": {"low": 8, "high": 16},
        "suits": ["COMBI", "DUO"],
        "weak_for": [],
        "evidence_tag": "literature",
        "sources": ["[8]", "[9]", "[10]", "[11]", "[12]", "[13]", "[26]"],
    },
    {
        "id": "H1",
        "name": "Hopper-stage weighing plate + fleet self-calibration (hopper idea: Europress)",
        "principle": "A small load-cell plate in the charging chamber weighs each charge before and after the ram stroke; "
                     "the device sums the charges and the fleet calibrates the sum from shared weighbridge tickets.",
        "sigma_rel_pct": H1_SIGMA,
        "sigma_abs_kg": {"low": 5.0, "mid": 10.0, "high": 20.0},
        "bom_eur_per_device": bom("H1"),
        "install_hours": {"low": 10, "high": 20},
        "suits": ["COMBI", "DUO"],
        "weak_for": ["RETROFIT_UNITS", "BIOWASTE_LIQUIDS", "NEW_DEVICE_BEFORE_TICKETS"],
        "evidence_tag": "estimate",
        "sources": ["[22]", "[25]", "[28]", "[29]", "[36]"],
    },
    {
        "id": "H7",
        "name": "Hydraulic self-lift on the compactor's own power pack (team idea, to explore)",
        "principle": "A cylinder near the door end of a COMBI, driven by the compactor's own hydraulics, lifts that end ~10 mm "
                     "at rest; lift/lower pressure average x piston area gives the end reaction, and W = (R - R0) L / x_w gives the waste.",
        "sigma_rel_pct": H7_SIGMA,
        "sigma_abs_kg": H7_FLOOR,
        "bom_eur_per_device": bom("H7"),
        "install_hours": {"low": 12, "high": 24},
        "suits": ["COMBI"],
        "weak_for": ["DUO", "RETROFIT_UNITS", "RAILS_AND_PLINTHS", "SOFT_GROUND", "NEW_DEVICE_BEFORE_TICKETS", "SNOW_ON_ROOF"],
        "evidence_tag": "estimate",
        "sources": ["[39]", "[40]", "[42]", "[43]", "[48]"],
    },
    {
        "id": "H5",
        "name": "Weighing guide rails (team idea)",
        "principle": "The unit (COMBI) or container (DUO) rests only on two guide rails, each on two shear-beam load "
                     "cells with overload stops and side restraint; weight = sum of the four cells, re-tared at every exchange.",
        "sigma_rel_pct": {"low": 0.6, "mid": 1.0, "high": 2.0},
        "sigma_abs_kg": {"low": 10.0, "mid": 20.0, "high": 40.0},
        "bom_eur_per_device": bom("H5"),
        "install_hours": {"low": 12, "high": 24},
        "suits": ["COMBI", "DUO"],
        "weak_for": ["SITES_WITHOUT_RAILS", "ICE_AND_DEBRIS"],
        "evidence_tag": "estimate",
        "sources": ["[8]", "[12]", "[13]", "[20]", "[26]", "[27]"],
    },
    {
        "id": "PS",
        "name": "Platform scale under the whole unit (Europress's existing option)",
        "principle": "A steel weighing platform or weighing beams with ramps on a foundation; the whole unit or "
                     "container stands on it.",
        "sigma_rel_pct": {"low": 0.2, "mid": 0.5, "high": 1.0},
        "sigma_abs_kg": {"low": 10.0, "mid": 20.0, "high": 40.0},
        "bom_eur_per_device": bom("PS"),
        "install_hours": {"low": 16, "high": 32},
        "suits": ["COMBI", "DUO"],
        "weak_for": ["COST"],
        "evidence_tag": "estimate",
        "sources": ["[27]", "[36]"],
    },
]


def tiers_table_md() -> str:
    lines = [
        "| Tier | Name | σ rel % (low / mid / high) | σ abs kg floor (low / mid / high) | BOM EUR per device | Install h | Weak for | Evidence | Sources |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for t in TIERS:
        s, a, b, h = t["sigma_rel_pct"], t["sigma_abs_kg"], t["bom_eur_per_device"], t["install_hours"]
        bom_s = f"€{b['low']:,}–{b['high']:,}" if b["high"] else "€0 (no new hardware)"
        lines.append(
            f"| {t['id']} | {t['name']} | {s['low']} / {s['mid']} / {s['high']} | {a['low']:.0f} / {a['mid']:.0f} / {a['high']:.0f} "
            f"| {bom_s} {BOM_CITE[t['id']]} | {h['low']}–{h['high']} | {', '.join(t['weak_for']) or '–'} "
            f"| {t['evidence_tag']} | {' '.join(t['sources'])} |")
    return "\n".join(lines) + "\n"


def budget_md() -> str:
    lines = ["| Error source (1σ, % of a ~3 t load) | low | mid | high | Mitigation |", "|---|---|---|---|---|"]
    for name, lo, mid, hi, how in ERROR_BUDGET_T1:
        lines.append(f"| {name} | {lo} | {mid} | {hi} | {how} |")
    lines.append(f"| **Combined (root-sum-square)** | **{T1_SIGMA['low']}** | **{T1_SIGMA['mid']}** | **{T1_SIGMA['high']}** | estimate |")
    return "\n".join(lines) + "\n"


def budget_chart():
    style()
    names = [r[0] for r in ERROR_BUDGET_T1] + ["Combined (RSS)"]
    mids = [r[2] for r in ERROR_BUDGET_T1] + [T1_SIGMA["mid"]]
    los = [r[1] for r in ERROR_BUDGET_T1] + [T1_SIGMA["low"]]
    his = [r[3] for r in ERROR_BUDGET_T1] + [T1_SIGMA["high"]]
    y = list(range(len(names)))[::-1]
    fig, ax = plt.subplots(figsize=(8.2, 4.0))
    for yi, lo, mid, hi, nm in zip(y, los, mids, his, names):
        last = nm.startswith("Combined")
        ax.barh(yi, mid, height=0.55, color=TIER_COLOR["T1"] if last else "#9cc2ee", edgecolor="none")
        ax.plot([lo, hi], [yi, yi], color=INK2, linewidth=1.5)
        ax.plot([lo, lo], [yi - 0.12, yi + 0.12], color=INK2, linewidth=1.5)
        ax.plot([hi, hi], [yi - 0.12, yi + 0.12], color=INK2, linewidth=1.5)
        ax.text(3.65, yi, f"{mid:.1f} %  ({lo:.1f}–{hi:.1f})", va="center", fontsize=9, color=INK,
                fontweight="bold" if last else "normal")
    target = 100 / 1.96 / 3000 * 100
    ax.axvline(target, color=INK, linestyle=(0, (4, 3)), linewidth=1.2)
    ax.text(target + 0.05, max(y) + 0.55, f"σ ≈ {target:.1f} %: dataset's simulation target\n(±100 kg on 3 t at 95 %), not a Europress specification",
            fontsize=8, color=INK2, va="bottom")
    ax.set_yticks(y, names)
    ax.set_xlim(0, 4.7)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_ylim(-0.6, max(y) + 1.4)
    ax.set_xlabel("1σ error, % of a ~3 t load  (bar = mid estimate, whisker = low–high)")
    ax.set_title("T1 strain-gauge error budget (team estimate, untested; v2 adds support position)", loc="left")
    ax.grid(axis="y", visible=False)
    return save_svg(fig, "error_budget.svg")


def main():
    GEN.mkdir(parents=True, exist_ok=True)
    doc = {"schema_version": 1, "chosen_tier": CHOSEN, "tiers": TIERS}
    (PART1 / "sigma_tiers.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    (GEN / "tiers_table.md").write_text(tiers_table_md())
    (GEN / "error_budget.md").write_text(budget_md())
    budget_chart()
    print("T1 combined sigma %:", T1_SIGMA)
    print(tiers_table_md())


if __name__ == "__main__":
    main()
