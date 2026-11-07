"""H1 charge-summing error model on the real (synthetic) lift sequence.

    python charge_sum.py <data/<profile>/public>   -> generated/charge_sum.{md,json}, figures/charge_sum.svg

For every reference lift the container is split into as many charges as the device ran compaction cycles since
its previous lift; each charge is weighed with the H1 error model (calc/h1_params.py). Reported per material:
RMS relative error of the container total before any calibration, and after an ideal per-device correction (the
floor that self-calibration can approach), next to the closed form of calc/error_accumulation.py.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "calc"))
from error_accumulation import container_error  # noqa: E402

from common import GEN, INK, INK2, S1, S2, check_public_root, save_svg, style  # noqa: E402
from h1_sim import load_lifts, open_public, simulate  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

SEED = 1
LEVELS = ("low", "mid", "high")


def rms(x):
    return float(np.sqrt(np.mean(np.square(x))))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("public")
    a = ap.parse_args(argv)
    con = open_public(check_public_root(a.public))
    lifts = load_lifts(con)
    res = {"n_lifts": int(len(lifts)), "n_devices": int(lifts.device_id.nunique()),
           "median_charges_per_lift": float(lifts.n_cycles.median()),
           "kg_per_cycle_p10_p50_p90": [round(float(q), 1) for q in np.quantile(lifts.ticket_kg / lifts.n_cycles, [.1, .5, .9])],
           "levels": {}}
    for i, lvl in enumerate(LEVELS):
        s = simulate(lifts, lvl, SEED + i)
        s["ratio"] = s.m_hat / s.m_true
        s["oracle"] = s.ratio / s.groupby("device_id").ratio.transform("mean")
        per = {}
        for mat, g in s.groupby("material_stream"):
            per[mat] = {"n": int(len(g)), "rms_before_pct": round(100 * rms(g.ratio - 1), 2),
                        "floor_after_pct": round(100 * rms(g.oracle - 1), 2),
                        "closed_form_before_pct": round(container_error(mat, lvl)["rms_before_pct"], 2),
                        "closed_form_floor_pct": round(container_error(mat, lvl)["floor_after_pct"], 2)}
        res["levels"][lvl] = {"all": {"rms_before_pct": round(100 * rms(s.ratio - 1), 2),
                                      "floor_after_pct": round(100 * rms(s.oracle - 1), 2)}, "per_material": per}
    (GEN / "charge_sum.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")

    mid = res["levels"]["mid"]["per_material"]
    lines = ["| material | reference lifts | RMS error before calibration (sim / closed form) | floor after calibration (sim / closed form) |",
             "|---|---|---|---|"]
    for mat, v in mid.items():
        lines.append(f"| {mat} | {v['n']} | {v['rms_before_pct']:.1f} % / {v['closed_form_before_pct']:.1f} % | "
                     f"{v['floor_after_pct']:.1f} % / {v['closed_form_floor_pct']:.1f} % |")
    allr = {l: res["levels"][l]["all"] for l in LEVELS}
    lines.append(f"| **all (low / mid / high)** | {res['n_lifts']} | "
                 + " / ".join(f"{allr[l]['rms_before_pct']:.1f}" for l in LEVELS) + " % | "
                 + " / ".join(f"{allr[l]['floor_after_pct']:.1f}" for l in LEVELS) + " % |")
    (GEN / "charge_sum.md").write_text("\n".join(lines) + "\n")

    style()
    mats = list(mid)
    y = np.arange(len(mats))[::-1]
    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    ax.barh(y + 0.18, [mid[m]["rms_before_pct"] for m in mats], 0.34, color=S2, label="before calibration")
    ax.barh(y - 0.18, [mid[m]["floor_after_pct"] for m in mats], 0.34, color=S1, label="after per-device calibration (floor)")
    ax.scatter([mid[m]["closed_form_before_pct"] for m in mats], y + 0.18, marker="|", s=200, color=INK, zorder=3,
               label="closed form (calc/error_accumulation.py)")
    ax.scatter([mid[m]["closed_form_floor_pct"] for m in mats], y - 0.18, marker="|", s=200, color=INK, zorder=3)
    ax.set_yticks(y, [m.replace("_", " ") for m in mats])
    ax.set_xlabel("RMS error of the container total, %  (mid parameters, synthetic lifts)")
    ax.set_title("H1: summing tens to hundreds of weighed charges per container (team-estimate error model, untested)", loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=3, fontsize=8)
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", colors=INK2)
    save_svg(fig, "charge_sum.svg")
    print(json.dumps(res["levels"]["mid"]["all"]), res["n_lifts"], res["median_charges_per_lift"], res["kg_per_cycle_p10_p50_p90"])
    print("\n".join(lines))


if __name__ == "__main__":
    main()
