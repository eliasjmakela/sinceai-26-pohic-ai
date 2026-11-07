"""Shared data loading and the H1 charge-summing simulator (used by charge_sum.py, self_calibration.py, fusion.py).

Reference lifts: completed lifts with a shared single-load, weighed-tare weighbridge ticket (the synthetic dataset's
best mass). The number of charges in a container = compaction cycles since the previous completed lift of the same
device (telemetry_hourly). The simulated H1 device then 'weighs' each charge with the error model in
calc/h1_params.py. The masses are synthetic and the error model is a team estimate: this measures what the method
would do under stated assumptions, not what hardware does.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from europress_data.sdk import open_dataset

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "calc"))
from h1_params import CHARGE_CV, P, W_MAT  # noqa: E402

WB_SIGMA_KG = 12.0  # kit configs/assumptions.yaml weighbridge_sigma_kg

SQL_LIFTS = """
WITH all_lifts AS (
  SELECT device_id, actual_at, operator_job_ref,
         lag(actual_at) OVER (PARTITION BY device_id ORDER BY actual_at, collection_id) AS prev_at,
         driver_reported_side_waste, device_fill_pct_before
  FROM collection_events WHERE status = 'COMPLETED'
), ref AS (
  SELECT a.*, w.allocated_net_kg::DOUBLE AS ticket_kg
  FROM all_lifts a JOIN weighbridge_tickets w USING (operator_job_ref)
  WHERE w.loads_on_vehicle = 1 AND w.tare_method = 'WEIGHED' AND w.allocated_net_kg > 100
    AND a.prev_at IS NOT NULL AND NOT coalesce(a.driver_reported_side_waste, false)
)
SELECT r.device_id, d.equipment_class, d.material_stream, d.container_volume_m3::DOUBLE AS volume_m3, d.operator_id,
       r.actual_at, r.prev_at, r.ticket_kg, r.device_fill_pct_before::DOUBLE AS fill_before,
       sum(t.compaction_cycles)::BIGINT AS n_cycles,
       avg(t.press_load_index)::DOUBLE AS press_index
FROM ref r JOIN devices d USING (device_id)
JOIN telemetry_hourly t ON t.device_id = r.device_id AND t.measured_at > r.prev_at AND t.measured_at <= r.actual_at
GROUP BY ALL
HAVING sum(t.compaction_cycles) >= 5
ORDER BY r.actual_at, r.device_id
"""


def load_lifts(con) -> pd.DataFrame:
    df = con.execute(SQL_LIFTS).df()
    df["actual_at"] = pd.to_datetime(df.actual_at)
    return df.reset_index(drop=True)


def open_public(root: Path):
    return open_dataset(root)


def simulate(df: pd.DataFrame, lvl: str, seed: int) -> pd.DataFrame:
    """Return df with m_true (= ticket, the synthetic truth), m_hat (raw H1 sum) and ticket_obs (ticket + noise)."""
    rng = np.random.default_rng(seed)
    p = {k: v[lvl] for k, v in P.items()}
    devs = sorted(df.device_id.unique())
    mats = sorted(df.material_stream.unique())
    # true group-level bridging share differs from our guess W_MAT by the stated relative uncertainty
    w_true = {m: max(0.0, W_MAT[m] * (1 + p["W_MAT_REL_UNC"] * rng.normal())) for m in mats}
    dev_delta = dict(zip(devs, rng.normal(0, p["TAU_DEVICE"], len(devs))))
    dev_g0 = dict(zip(devs, rng.normal(0, p["SIGMA_G0"], len(devs))))
    out = df.copy()
    m_hat = np.empty(len(df))
    drift = {d: 0.0 for d in devs}
    last_t = {}
    for i, r in enumerate(df.itertuples(index=False)):
        d = r.device_id
        if d in last_t:  # gain random walk between lifts
            months = (r.actual_at - last_t[d]).total_seconds() / (30.4 * 86400)
            drift[d] += rng.normal(0, p["DRIFT_PER_MONTH"] * np.sqrt(max(months, 0)))
        last_t[d] = r.actual_at
        n = int(r.n_cycles)
        w = rng.lognormal(0, np.sqrt(np.log(1 + CHARGE_CV ** 2)), n)
        m_i = r.ticket_kg * w / w.sum()
        c_k = rng.normal(0, p["C_CONTAINER"])
        share = np.clip(w_true[r.material_stream] + dev_delta[d] + c_k + p["S_CHARGE"] * rng.normal(size=n), 0, 0.9)
        kept = rng.random(n) >= p["P_MISS"]
        noise = rng.normal(0, np.sqrt(2) * p["SIGMA_READ_KG"], n)
        m_hat[i] = ((1 + dev_g0[d] + drift[d]) * (1 - share) * m_i * kept + noise * kept).sum()
    out["m_true"] = df.ticket_kg.values
    out["m_hat"] = m_hat
    out["ticket_obs"] = df.ticket_kg.values + rng.normal(0, WB_SIGMA_KG, len(df))
    return out
