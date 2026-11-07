"""Virtual scale (roadmap analysis, not in the product claim): estimating weight on older units. (synthetic data)

Model (log-linear, explainable): log(kg) = material + machine type + b1 log(fill x container volume)
                                          + b2 log(1 + compaction cycles since last lift) + b3 log(days since last lift)
Reference mass: weighbridge net of single-load, weighed-tare tickets (independent of the device's own weight sensor).
Biowaste excluded (decision of 7 Nov: little back-pressure, the hardest stream to weigh).

Experiments (devices split, fixed seeds):
  * reference share: the model is trained on a small share of devices that have a real scale (e.g. weighing rails),
    then applied to all other devices without any device-specific data ("uncalibrated");
  * per-device calibration: each device's first K shared weighbridge tickets give it a correction factor
    (median ratio), and the rest of its lifts are scored -- fleet self-calibration;
  * monthly totals: errors on single lifts partly average out over a month.
Caveat: the synthetic generator derives mass from similar quantities (fill, density), so these errors are likely
optimistic; the real accuracy must be measured on real pressure / fill data (Part 1 validation plan).
"""
from __future__ import annotations

import duckdb
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from .config import EXCLUDED_MATERIALS as EXCLUDE
from .figures import Figure

FEATURES = ("lfv", "lcyc", "ld")
REFERENCE_SHARES = (0.02, 0.05, 0.10, 0.30)
DEFAULT_SHARE = 0.10
CALIBRATION_K = (0, 1, 3, 5, 10)
SEEDS = (1, 2, 3, 4, 5)
SOURCES = ("collection_events.device_fill_pct_before", "devices.container_volume_m3", "devices.material_stream",
           "devices.equipment_class", "telemetry_daily_summary.compaction_cycles", "weighbridge_tickets.allocated_net_kg")


def lifts(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    df = con.execute("""
        WITH t AS (SELECT operator_job_ref, allocated_net_kg, loads_on_vehicle, tare_method FROM weighbridge_tickets),
        cum AS (SELECT device_id, date, sum(coalesce(compaction_cycles, 0)) OVER (PARTITION BY device_id ORDER BY date) AS cc
                FROM telemetry_daily_summary),
        c AS (SELECT c.*, d.material_stream, d.container_volume_m3, d.equipment_class,
                     lag(actual_at) OVER (PARTITION BY device_id ORDER BY actual_at) AS prev_at
              FROM collection_events c JOIN devices d USING (device_id) WHERE c.status = 'COMPLETED')
        SELECT c.collection_id, c.device_id, c.material_stream, c.container_volume_m3, c.equipment_class,
               c.device_fill_pct_before AS fill, date_diff('hour', c.prev_at, c.actual_at) / 24.0 AS days,
               c.actual_at, t.allocated_net_kg AS ref_kg, a.cc - b.cc AS cycles
        FROM c JOIN t USING (operator_job_ref)
        JOIN cum a ON a.device_id = c.device_id AND a.date = CAST(timezone('Europe/Helsinki', c.actual_at) AS DATE)
        JOIN cum b ON b.device_id = c.device_id AND b.date = CAST(timezone('Europe/Helsinki', c.prev_at) AS DATE)
        WHERE t.loads_on_vehicle = 1 AND t.tare_method = 'WEIGHED' AND t.allocated_net_kg > 50
          AND c.device_fill_pct_before > 5 AND c.prev_at IS NOT NULL
        ORDER BY c.device_id, c.actual_at""").df()
    df = df[~df.material_stream.isin(EXCLUDE)].dropna(subset=["fill", "days", "cycles"]).reset_index(drop=True)
    df["lkg"] = np.log(df.ref_kg)
    df["lfv"] = np.log(df.fill / 100 * df.container_volume_m3)
    df["lcyc"] = np.log1p(df.cycles)
    df["ld"] = np.log(df.days.clip(lower=0.1))
    return df


def _design(df: pd.DataFrame, cols: tuple[str, ...]) -> pd.DataFrame:
    x = pd.get_dummies(df[["material_stream", "equipment_class"]]).astype(float)
    for c in cols:
        x[c] = df[c]
    return x


def experiment(df: pd.DataFrame, share: float, cols: tuple[str, ...], seed: int) -> dict:
    devs = np.array(sorted(df.device_id.unique()))
    ref = set(np.random.default_rng(seed).choice(devs, size=max(2, int(share * len(devs))), replace=False))
    train = df.device_id.isin(ref).to_numpy()
    x = _design(df, cols)
    model = LinearRegression().fit(x[train], df.lkg[train])
    ev = df[~train].assign(pred=np.exp(model.predict(x[~train])))
    ev = ev.assign(rank=ev.groupby("device_id").cumcount(), n=ev.groupby("device_id").device_id.transform("size"),
                   ratio=ev.ref_kg / ev.pred, month=ev.actual_at.dt.strftime("%Y-%m"))
    out = {}
    for k in CALIBRATION_K:
        e = ev[ev.n > k + 2]
        if e.empty:
            out[k] = {"lift_error_median_pct": None, "month_error_median_pct": None}
            continue
        f = e[e["rank"] < k].groupby("device_id").ratio.median().astype(float) if k else None
        h = e[e["rank"] >= k]
        h = h.assign(est=h.pred.to_numpy(dtype=float) * (h.device_id.map(f).to_numpy(dtype=float) if k else 1.0))
        lift_err = (h.est - h.ref_kg).abs() / h.ref_kg
        m = h.groupby(["device_id", "month"])[["est", "ref_kg"]].sum()
        out[k] = {"lift_error_median_pct": round(100 * float(lift_err.median()), 1),
                  "month_error_median_pct": round(100 * float(((m.est - m.ref_kg).abs() / m.ref_kg).median()), 1)}
    return {"reference_devices": len(ref), "evaluated_devices": int(ev.device_id.nunique()), "by_k": out}


def _mean_over_seeds(df, share, cols):
    runs = [experiment(df, share, cols, s) for s in SEEDS]
    res = {}
    for k in CALIBRATION_K:
        lift = [r["by_k"][k]["lift_error_median_pct"] for r in runs if r["by_k"][k]["lift_error_median_pct"] is not None]
        mon = [r["by_k"][k]["month_error_median_pct"] for r in runs if r["by_k"][k]["month_error_median_pct"] is not None]
        if not lift:
            res[str(k)] = {"lift_error_median_pct": None, "lift_error_range_pct": None, "month_error_median_pct": None}
            continue
        res[str(k)] = {"lift_error_median_pct": round(float(np.mean(lift)), 1),
                       "lift_error_range_pct": [min(lift), max(lift)],
                       "month_error_median_pct": round(float(np.mean(mon)), 1)}
    return {"reference_devices": runs[0]["reference_devices"], "evaluated_devices": runs[0]["evaluated_devices"],
            "by_k": res}


def virtual_scale_facts(con: duckdb.DuckDBPyConnection) -> dict:
    df = lifts(con)
    main = _mean_over_seeds(df, DEFAULT_SHARE, FEATURES)
    fill_only = _mean_over_seeds(df, DEFAULT_SHARE, ("lfv",))
    shares = {str(s): _mean_over_seeds(df, s, FEATURES)["by_k"] for s in REFERENCE_SHARES}

    def fig(v, formula):
        return Figure(v, "%", "simulated", formula, SOURCES,
                      assumptions=("Synthetic data: the generator links mass to fill and density, so errors are likely "
                                   "optimistic", "Reference = single-load weighed-tare weighbridge tickets",
                                   "Biowaste excluded", f"Mean over {len(SEEDS)} random device splits")).to_dict()

    return {
        "lifts": int(len(df)), "devices": int(df.device_id.nunique()), "reference_share": DEFAULT_SHARE,
        "headline": {
            "uncalibrated_lift_error_pct": fig(main["by_k"]["0"]["lift_error_median_pct"],
                                               "median |estimate - weighbridge| / weighbridge, devices not in the reference set"),
            "calibrated_lift_error_pct": fig(main["by_k"]["5"]["lift_error_median_pct"],
                                             "same, after each device's first 5 shared weighbridge tickets"),
            "calibrated_month_error_pct": fig(main["by_k"]["5"]["month_error_median_pct"],
                                              "monthly totals per device, after 5 tickets"),
            "fill_only_uncalibrated_lift_error_pct": fig(fill_only["by_k"]["0"]["lift_error_median_pct"],
                                                         "uncalibrated, fill x volume and material only"),
        },
        "learning_curve": main, "fill_only": fill_only, "by_reference_share": shares,
        "reading": ("A model trained on a few reference devices estimates every other device's lift weight from signals "
                    "the compactor already has; compaction cycles and time since the last lift halve the error compared "
                    "with fill alone. A handful of shared weighbridge tickets per device calibrate it further. Beyond ~5 % "
                    "reference devices, more reference scales add little."),
    }
