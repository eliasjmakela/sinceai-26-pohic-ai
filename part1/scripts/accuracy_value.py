"""What is each tier's accuracy worth?  Adapted from the starter kit's examples/weighing_accuracy_value.py
(Europress x Since AI starter kit v1.0.1) with attribution.

    python accuracy_value.py <data/<profile>/public>

Changes against the kit example:
  * data access through europress_data.sdk.open_dataset (DuckDB views), as PRODUCT.md section 7.2 requires;
  * reference loads = shared single-load tickets with a WEIGHED tare only (stored tares can be outdated);
  * the error model per tier comes from part1/sigma_tiers.json (relative sigma + absolute floor), low/mid/high;
  * adds a sigma sweep for the chart and the number of loads needed to see a 3 % systematic tonnage difference.

The reference masses are synthetic. The simulation only re-measures them with an assumed error model; it says
nothing about whether real hardware reaches that error model.
"""
from __future__ import annotations

import argparse
import json
import math

import numpy as np
from europress_data.sdk import open_dataset

from common import GEN, INK, INK2, PART1, TIER_COLOR, check_public_root, save_svg, style

import matplotlib.pyplot as plt

WB_SIGMA_KG = 12.0   # weighbridge noise in the synthetic world (configs/assumptions.yaml -> weighbridge_sigma_kg)
SEED = 1
SWEEP = [0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 4, 5, 7.5, 10, 15, 20]

SQL = """
SELECT w.allocated_net_kg::DOUBLE AS m
FROM collection_events c
JOIN weighbridge_tickets w USING (operator_job_ref)
WHERE c.status = 'COMPLETED'
  AND w.loads_on_vehicle = 1 AND w.tare_method = 'WEIGHED' AND w.allocated_net_kg > 100
  AND NOT coalesce(c.driver_reported_side_waste, false)
ORDER BY w.ticket_id
"""

SQL_RECON = """
SELECT c.device_estimated_collected_kg::DOUBLE AS dev, w.allocated_net_kg::DOUBLE AS wb
FROM collection_events c
JOIN weighbridge_tickets w USING (operator_job_ref)
WHERE c.status = 'COMPLETED'
  AND w.loads_on_vehicle = 1 AND w.tare_method = 'WEIGHED' AND w.allocated_net_kg > 100
  AND NOT coalesce(c.driver_reported_side_waste, false)
  AND c.device_estimated_collected_kg IS NOT NULL
"""


def metrics(m: np.ndarray, s_pct: float, abs_kg: float, rng) -> dict:
    sig = np.maximum(abs_kg, s_pct / 100 * m)
    dev = m + rng.normal(0, 1, len(m)) * sig
    err = dev - m
    band = (m >= 2500) & (m <= 3500)
    sig_tot = np.sqrt(sig ** 2 + WB_SIGMA_KG ** 2)
    detect = (1.10 * m - dev) > 2 * sig_tot          # invoice tonnage +10 %, flag beyond 2 combined sigma
    false_alarm = (m - dev) > 2 * sig_tot
    cpt_err = np.abs(m / dev - 1)                    # relative error of EUR/t computed from the device weight
    rel = s_pct / 100
    return {
        "within_100kg_2.5_3.5t": round(float((np.abs(err[band]) <= 100).mean()), 3),
        "median_eur_per_t_error_pct": round(100 * float(np.median(cpt_err)), 2),
        "p95_eur_per_t_error_pct": round(100 * float(np.quantile(cpt_err, 0.95)), 2),
        "detects_+10pct_on_one_load": round(float(detect.mean()), 3),
        "false_alarm_rate": round(float(false_alarm.mean()), 4),
        # random error only: loads n with 2 * sigma_rel / sqrt(n) <= 3 %  (systematic gain error is NOT reduced)
        "loads_to_see_3pct_difference": max(1, math.ceil((2 * rel / 0.03) ** 2)),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("public")
    a = ap.parse_args(argv)
    root = check_public_root(a.public)
    con = open_dataset(root)
    m = con.sql(SQL).fetchnumpy()["m"]
    tiers = json.loads((PART1 / "sigma_tiers.json").read_text())["tiers"]

    rows = []
    for t in tiers:
        for lvl in ("low", "mid", "high"):
            rng = np.random.default_rng(SEED)
            r = {"tier": t["id"], "level": lvl, "sigma_rel_pct": t["sigma_rel_pct"][lvl], "sigma_abs_kg": t["sigma_abs_kg"][lvl]}
            r.update(metrics(m, t["sigma_rel_pct"][lvl], t["sigma_abs_kg"][lvl], rng))
            rows.append(r)
    sweep = []
    for s in SWEEP:
        rng = np.random.default_rng(SEED)
        sweep.append({"sigma_rel_pct": s, **metrics(m, s, 30.0, rng)})

    rec = con.sql(SQL_RECON).fetchnumpy()
    rel = np.abs(rec["dev"] - rec["wb"]) / rec["wb"]
    recon = {"pairs": int(len(rel)), "median_abs_diff_pct": round(100 * float(np.median(rel)), 2),
             "p95_abs_diff_pct": round(100 * float(np.quantile(rel, 0.95)), 2)}

    out = {"reference_loads": int(len(m)),
           "loads_2.5_3.5t": int(((m >= 2500) & (m <= 3500)).sum()),
           "seed": SEED, "tiers": rows, "sweep_abs_floor_30kg": sweep, "dataset_device_vs_ticket": recon}
    GEN.mkdir(parents=True, exist_ok=True)
    (GEN / "accuracy_value.json").write_text(json.dumps(out, indent=2) + "\n")

    cols = ["tier", "level", "sigma_rel_pct", "sigma_abs_kg", "within_100kg_2.5_3.5t", "median_eur_per_t_error_pct",
            "detects_+10pct_on_one_load", "false_alarm_rate", "loads_to_see_3pct_difference"]
    md = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    md += ["| " + " | ".join(str(r[c]) for c in cols) + " |" for r in rows]
    md.append("")
    md.append(f"Reference: {out['reference_loads']} shared single-load, weighed-tare weighbridge tickets "
              f"({out['loads_2.5_3.5t']} in the 2.5–3.5 t band), synthetic competition data, seed {SEED}.")
    md.append(f"Dataset's own simulated device vs ticket: {recon['pairs']} pairs, median |difference| "
              f"{recon['median_abs_diff_pct']} %, p95 {recon['p95_abs_diff_pct']} %.")
    (GEN / "accuracy_value.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    chart(sweep, rows, tiers)


def chart(sweep, rows, tiers):
    style()
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9), sharex=True)
    x = [r["sigma_rel_pct"] for r in sweep]
    panels = [("within_100kg_2.5_3.5t", "Share of 2.5–3.5 t loads within ±100 kg"),
              ("detects_+10pct_on_one_load", "Share of +10 % tonnage over-billing\nflagged on a single load")]
    for ax, (key, title) in zip(axes, panels):
        ax.plot(x, [r[key] for r in sweep], color=INK2, linewidth=2)
        for t in tiers:
            lo, hi = t["sigma_rel_pct"]["low"], t["sigma_rel_pct"]["high"]
            ax.axvspan(lo, hi, color=TIER_COLOR[t["id"]], alpha=0.14, linewidth=0)
            mid = next(r for r in rows if r["tier"] == t["id"] and r["level"] == "mid")
            ax.plot([mid["sigma_rel_pct"]], [mid[key]], "o", markersize=8, color=TIER_COLOR[t["id"]],
                    markeredgecolor="#fcfcfb", markeredgewidth=2, zorder=5)
            ax.annotate(f"{t['id']} {mid[key]:.0%}", (mid["sigma_rel_pct"], mid[key]), textcoords="offset points",
                        xytext=(6, 6), fontsize=9, color=INK)
        ax.set_xscale("log")
        ax.set_xticks([0.25, 0.5, 1, 2, 5, 10, 20], ["0.25", "0.5", "1", "2", "5", "10", "20"])
        ax.set_ylim(0, 1.12)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1], ["0 %", "25 %", "50 %", "75 %", "100 %"])
        ax.set_title(title, loc="left", fontsize=10)
        ax.set_xlabel("weighing error σ, % of load (log scale)")
    axes[0].axhline(0.95, color=INK, linestyle=(0, (4, 3)), linewidth=1)
    axes[0].text(2.6, 0.965, "95 %: dataset's simulation target,\nnot a Europress specification", fontsize=7.5, color=INK2, va="bottom")
    fig.suptitle("Accuracy → value: re-measuring synthetic reference loads with each tier's error model "
                 "(dot = tier mid, band = tier low–high,\ngrey line = σ sweep with a 30 kg floor)", x=0.01, ha="left", fontsize=10, color=INK)
    fig.tight_layout()
    save_svg(fig, "accuracy_value.svg")


if __name__ == "__main__":
    main()
