"""In-service cross-check: how cheap strain gauges stay honest using shared weighbridge tickets.

    python drift_watch.py <data/<profile>/public>

For every completed lift that has a shared single-load, weighed-tare ticket, the ratio
device_estimated_collected_kg / allocated_net_kg is a free calibration check. A rolling median of the last
ROLL ratios is compared with the device's own baseline (median of its first BASE pairs). If it leaves the
+/- BAND window on two consecutive pairs, the device is flagged for recalibration (a proposal for a human).

Device choice is deterministic and uses only public data (no labels):
  * "drifting" = the device with the largest change of rolling median from its first to its last BASE pairs;
  * "healthy"  = among never-flagged devices with >= 40 pairs and a median within 3 % of 1, the smallest change.
The device weights in the dataset are simulated; this shows the method, not hardware behaviour.
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from europress_data.sdk import open_dataset

from common import GEN, INK, INK2, S1, S2, check_public_root, save_svg, style

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROLL, BASE, BAND, MIN_PAIRS = 7, 10, 0.05, 30

SQL = """
SELECT c.device_id, d.equipment_class, d.material_stream, c.actual_at,
       c.device_estimated_collected_kg::DOUBLE AS dev, w.allocated_net_kg::DOUBLE AS wb
FROM collection_events c
JOIN weighbridge_tickets w USING (operator_job_ref)
JOIN devices d USING (device_id)
WHERE c.status = 'COMPLETED'
  AND w.loads_on_vehicle = 1 AND w.tare_method = 'WEIGHED' AND w.allocated_net_kg > 300
  AND NOT coalesce(c.driver_reported_side_waste, false)
  AND c.device_estimated_collected_kg IS NOT NULL
ORDER BY c.device_id, c.actual_at
"""


def watch(g: pd.DataFrame) -> pd.DataFrame:
    g = g.sort_values("actual_at").reset_index(drop=True).copy()
    g["ratio"] = g.dev / g.wb
    g["roll"] = g.ratio.rolling(ROLL, min_periods=ROLL).median()
    base = float(g.ratio.iloc[:BASE].median())
    g["base"] = base
    out = (g.roll - base).abs() > BAND * base
    g["alarm"] = out & out.shift(1, fill_value=False)
    return g


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("public")
    a = ap.parse_args(argv)
    con = open_dataset(check_public_root(a.public))
    df = con.sql(SQL).df()
    df["actual_at"] = pd.to_datetime(df.actual_at, utc=True)
    n = df.groupby("device_id").size()
    keep = n[n >= MIN_PAIRS].index
    stats = []
    for dev_id in sorted(keep):
        g = watch(df[df.device_id == dev_id])
        r = g.ratio
        stats.append({"device_id": dev_id, "pairs": len(g),
                      "change": abs(float(r.iloc[-BASE:].median()) - float(r.iloc[:BASE].median())),
                      "median": float(r.median()), "iqr": float(r.quantile(0.75) - r.quantile(0.25)),
                      "alarm_pairs": int(g.alarm.sum())})
    st = pd.DataFrame(stats)
    drifting = st.sort_values(["change", "device_id"], ascending=[False, True]).iloc[0].device_id
    healthy_pool = st[(st.pairs >= 40) & ((st["median"] - 1).abs() <= 0.03)]
    healthy = healthy_pool[healthy_pool.alarm_pairs == 0].sort_values(["change", "iqr", "device_id"]).iloc[0].device_id

    summary = {"params": {"rolling_pairs": ROLL, "baseline_pairs": BASE, "band_pct": 100 * BAND, "min_pairs": MIN_PAIRS},
               "devices_with_enough_pairs": int(len(st)),
               "devices_flagged_at_least_once": int((st.alarm_pairs > 0).sum()),
               "examples": {}}
    gs = {}
    for label, dev_id in (("drifting", drifting), ("healthy", healthy)):
        g = watch(df[df.device_id == dev_id])
        gs[label] = g
        first = g[g.alarm].actual_at.min()
        summary["examples"][label] = {
            "device_id": dev_id, "equipment_class": g.equipment_class.iloc[0], "material": g.material_stream.iloc[0],
            "pairs": int(len(g)), "baseline_ratio": round(float(g.base.iloc[0]), 3),
            "last_rolling_ratio": round(float(g.roll.iloc[-1]), 3),
            "first_alarm": None if pd.isna(first) else first.strftime("%Y-%m-%d"),
            "pairs_until_first_alarm": None if pd.isna(first) else int((g.actual_at <= first).sum()),
            "suggested_gain_correction_at_end": round(float(g.base.iloc[0] / g.roll.iloc[-1]), 3)}
    GEN.mkdir(parents=True, exist_ok=True)
    (GEN / "drift_watch.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    chart(gs, summary)


def chart(gs, summary):
    style()
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.7), sharey=True)
    for ax, (label, color) in zip(axes, (("healthy", S1), ("drifting", S2))):
        g, ex = gs[label], summary["examples"][label]
        base = ex["baseline_ratio"]
        ax.axhspan(base * (1 - BAND), base * (1 + BAND), color="#e9e8e4", linewidth=0)
        ax.axhline(base, color=INK2, linewidth=1, linestyle=(0, (4, 3)))
        ax.plot(g.actual_at, g.ratio, "o", markersize=4, color=color, alpha=0.35, markeredgewidth=0)
        ax.plot(g.actual_at, g.roll, color=color, linewidth=2)
        if ex["first_alarm"]:
            t0 = pd.Timestamp(ex["first_alarm"], tz="UTC")
            ax.axvline(t0, color=INK, linewidth=1)
            ax.text(t0, 1.40, f"  recalibration\n  proposed {ex['first_alarm']}", fontsize=8, color=INK, va="top")
        ax.set_title(f"{label.capitalize()}: {ex['device_id']} ({ex['equipment_class']}, {ex['material'].replace('_', ' ')})",
                     loc="left", fontsize=10)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
        ax.set_ylim(0.7, 1.42)
    axes[0].set_ylabel("device weight / weighbridge ticket")
    axes[0].text(gs["healthy"].actual_at.iloc[0], 0.72,
                 f"dots = single lifts, line = rolling median of {ROLL}, band = baseline ±{BAND:.0%}",
                 fontsize=8, color=INK2)
    fig.suptitle("Drift watch on shared weighed-tare tickets (synthetic data; simulated device weights)",
                 x=0.01, ha="left", fontsize=10, color=INK)
    fig.tight_layout()
    save_svg(fig, "drift_watch.svg")


if __name__ == "__main__":
    main()
