"""Trips model: how many lifts would each device need if lifts were triggered by weight (container full)?

Method (simple, conserves tonnage):
  full payload  = median over the device's lifts of  collected kg x 100 / fill % before lift,
                  using lifts with fill >= MIN_FILL_FOR_PAYLOAD_PCT (needs >= MIN_PAYLOAD_LIFTS such lifts,
                  otherwise "cannot be computed" -- never imputed). Linear extrapolation ignores extra
                  compaction near full, so it underestimates the payload: conservative (more trips, not fewer).
  weight trips  = max( ceil(annual kg / (TARGET_SHARE x full payload)),
                       ceil(active days / max_days_between) )         # hygiene/fire-safety maximum interval
  The max interval per material comes from the starter kit's assumptions (materials.*.max_days_between).
Same waste, different number of trips: tonnage is identical in both regimes.
"""
from __future__ import annotations

import math

import duckdb
import pandas as pd

from .figures import Figure
from .kit import kit_assumptions

MIN_FILL_FOR_PAYLOAD_PCT = 40   # below this, fill readings are too noisy to extrapolate a full payload
MIN_PAYLOAD_LIFTS = 3
TARGET_SHARE = 0.9              # trigger at 90 % of the full payload (margin for sensor error and peaks)

SOURCES = ("collection_events.device_estimated_collected_kg", "collection_events.device_fill_pct_before",
           "collection_events.status", "collection_events.actual_at", "devices.material_stream",
           "devices.collection_policy", "configs/assumptions.yaml: materials.*.max_days_between")
ASSUMPTIONS = (f"Lift triggered at {int(TARGET_SHARE * 100)} % of the device's full payload, extrapolated from its "
               "own lifts (conservative)", "Maximum interval per material from the starter kit",
               "Devices with fewer than 3 usable lifts are excluded, not imputed",
               "Ignores closures, peaks and overflow risk days: simulation, not a saving")


def device_trips(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    df = con.execute(f"""
        SELECT c.device_id, d.material_stream, d.collection_policy,
               count(*) AS actual_lifts,
               sum(c.device_estimated_collected_kg) AS annual_kg,
               median(c.device_estimated_collected_kg * 100 / c.device_fill_pct_before)
                   FILTER (WHERE c.device_fill_pct_before >= {MIN_FILL_FOR_PAYLOAD_PCT}) AS full_payload_kg,
               count(*) FILTER (WHERE c.device_fill_pct_before >= {MIN_FILL_FOR_PAYLOAD_PCT}) AS n_payload_lifts,
               date_diff('day', min(c.actual_at), max(c.actual_at)) + 1 AS active_days
        FROM collection_events c JOIN devices d USING (device_id)
        WHERE c.status = 'COMPLETED' AND c.device_estimated_collected_kg IS NOT NULL
        GROUP BY ALL ORDER BY c.device_id""").df()
    max_days = {m: v["max_days_between"] for m, v in kit_assumptions()["materials"].items()}

    df["interval_bound"] = [math.ceil(r.active_days / max_days[r.material_stream]) for r in df.itertuples()]

    def weight_trips(r) -> int | None:
        if r.n_payload_lifts < MIN_PAYLOAD_LIFTS or pd.isna(r.full_payload_kg) or r.full_payload_kg <= 0:
            return None
        return max(math.ceil(r.annual_kg / (TARGET_SHARE * r.full_payload_kg)), r.interval_bound)

    df["weight_trips"] = pd.array([weight_trips(r) for r in df.itertuples()], dtype="Int64")
    return df


def _reduction(actual: int, weighted: int) -> float:
    return round(100 * (1 - weighted / actual), 1)


def trips_facts(con: duckdb.DuckDBPyConnection) -> dict:
    df = device_trips(con)
    ok = df[df.weight_trips.notna()]
    actual, weighted = int(ok.actual_lifts.sum()), int(ok.weight_trips.sum())
    tonnes = float(ok.annual_kg.sum()) / 1000

    def fig(value, unit, formula, tag="simulated"):
        return Figure(value, unit, tag, formula, SOURCES, assumptions=ASSUMPTIONS).to_dict()

    def breakdown(col: str) -> list[dict]:
        g = ok.groupby(col).agg(devices=("device_id", "count"), actual=("actual_lifts", "sum"),
                                weighted=("weight_trips", "sum")).reset_index().sort_values(col)
        return [{col: getattr(r, col), "devices": int(r.devices), "actual_lifts": int(r.actual),
                 "weight_triggered_lifts": int(r.weighted), "reduction_pct": _reduction(int(r.actual), int(r.weighted))}
                for r in g.itertuples()]

    return {
        "devices_modelled": int(len(ok)),
        "devices_excluded": int(len(df) - len(ok)),
        "devices_interval_bound": int((ok.weight_trips == ok.interval_bound).sum()),
        "actual_lifts": fig(actual, "count", "count of completed lifts (modelled devices)", tag="observed"),
        "weight_triggered_lifts": fig(weighted, "count",
                                      "sum over devices of max(ceil(annual kg / (0.9 x full payload)), interval bound)"),
        "lift_reduction_pct": fig(_reduction(actual, weighted), "%", "1 - weight_triggered_lifts / actual_lifts"),
        "tonnes_per_lift_actual": fig(round(tonnes / actual, 2), "t", "tonnes / actual lifts", tag="estimated"),
        "tonnes_per_lift_weighted": fig(round(tonnes / weighted, 2), "t", "tonnes / weight-triggered lifts"),
        "by_policy": breakdown("collection_policy"),
        "by_material": breakdown("material_stream"),
    }
