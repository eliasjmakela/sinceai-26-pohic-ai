"""Error accumulation over one container fill for H1 (sum of hundreds of weighed charges).

    python calc/error_accumulation.py   -> generated/calc_error_accumulation.md (+ .json for the scripts)

Closed form, from the model in calc/h1_params.py. Relative error of the container total M = sum m_i:
  random part (shrinks with sqrt N):   sqrt( N*2*sr^2 + (s^2 + p(1-p)) * N * mbar^2 * (1+cv^2) ) / M
  per-container part (does not shrink): c
  per-device systematic part:           -(W_MAT + p) mean bias, spread sqrt(g0^2 + tau^2 + (u*W_MAT)^2)
Before calibration the systematic part dominates; perfect knowledge of the device gain (what H2 learns from
weighbridge tickets) leaves sqrt(random^2 + c^2): the floor that self-calibration can reach.
"""
from __future__ import annotations

import json
import math

from calc_common import GEN, md_table, write
from h1_params import CHARGE_CV, CHARGE_KG, CONTAINER_KG, LEVELS, P, W_MAT


def container_error(material: str, lvl: str) -> dict:
    m_tot, mbar = CONTAINER_KG[material], CHARGE_KG[material]
    n = m_tot / mbar
    sr, s, p = P["SIGMA_READ_KG"][lvl], P["S_CHARGE"][lvl], P["P_MISS"][lvl]
    var_kg2 = n * 2 * sr ** 2 + (s ** 2 + p * (1 - p)) * n * mbar ** 2 * (1 + CHARGE_CV ** 2)
    rnd = math.sqrt(var_kg2) / m_tot
    c = P["C_CONTAINER"][lvl]
    bias = -(W_MAT[material] + p)
    spread = math.sqrt(P["SIGMA_G0"][lvl] ** 2 + P["TAU_DEVICE"][lvl] ** 2 + (P["W_MAT_REL_UNC"][lvl] * W_MAT[material]) ** 2)
    before = math.sqrt(bias ** 2 + spread ** 2 + c ** 2 + rnd ** 2)   # RMS error over the fleet, uncalibrated
    floor = math.hypot(rnd, c)
    return {"n_charges": round(n), "random_pct": 100 * rnd, "container_pct": 100 * c, "bias_pct": 100 * bias,
            "device_spread_pct": 100 * spread, "rms_before_pct": 100 * before, "floor_after_pct": 100 * floor,
            "abs_random_kg": math.sqrt(n * 2 * sr ** 2)}


def main():
    res = {lvl: {m: container_error(m, lvl) for m in W_MAT} for lvl in LEVELS}
    rows = []
    for m in W_MAT:
        r = {lvl: res[lvl][m] for lvl in LEVELS}
        f = lambda k: " / ".join(f"{r[l][k]:.1f}" for l in LEVELS)
        rows.append([m, r["mid"]["n_charges"], f("random_pct"), f("bias_pct"), f("device_spread_pct"),
                     f("rms_before_pct"), f("floor_after_pct")])
    text = ("# calc/error_accumulation.py output (H1, team-estimate parameters in calc/h1_params.py; untested)\n\n"
            "Values are low / mid / high, in % of the container total.\n\n"
            + md_table(["material", "charges per container (mid)", "random part (√N)", "mean bias",
                        "device spread", "RMS error before calibration", "floor after calibration"], rows)
            + "\nReading: 50–170 charges per container make the random part small (≈1–4.5 %). What is left is a **bias** "
              "(the plate misses the part of each charge that hangs on the walls or the ram) that does not average out. "
              "It is about the same for every charge of one device, so a handful of weighbridge tickets can measure it "
              "(scripts/self_calibration.py). The floor is set by how much that share changes from one container to the next.\n")
    write("error_accumulation", text)
    (GEN / "calc_error_accumulation.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(text)


if __name__ == "__main__":
    main()
