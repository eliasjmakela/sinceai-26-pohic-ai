"""Forecast backtest: how well can an operator predict a site's tonnage with vs without its collection history?

This is the evidence for the incumbent's information advantage (PRODUCT.md §1, §3):
  * own-history forecast  = what the incumbent (or anyone with OpenWeight data) can do
  * peer forecast         = what a newcomer without history can do: the average of similar devices
                            (same material stream and container size), excluding the device itself

Method (deliberately simple and explainable):
  monthly tonnage per device = sum of device_estimated_collected_kg of completed lifts, by local (Helsinki) month;
  history = the first 3/4 of the months, held-out = the last 1/4 (competition: Oct–Jun vs Jul–Sep);
  a device needs lifts in all but at most one month of each period;
  forecast = mean monthly tonnage over history (own) or mean of the peers' own-history means (peer);
  error    = |forecast - actual mean monthly tonnage in held-out months| / actual.
"""
from __future__ import annotations

import duckdb
import pandas as pd

from .figures import Figure

HELDOUT_SHARE = 0.25        # last quarter of the months is held out: competition pack = 9 months history, 3 held out
MIN_PEERS = 3               # fewer peers with the same material+size -> fall back to material only

SOURCES = ("collection_events.device_estimated_collected_kg", "collection_events.actual_at",
           "collection_events.status", "devices.material_stream", "devices.container_volume_m3")
ASSUMPTIONS = (
    "Synthetic data: the size of the gap depends on how different the generator makes individual devices",
    "Device-side weight estimates stand in for the operator's weighbridge history",
    "Seasonality cannot be learned from 12 months; the forecast is a plain mean",
)


def monthly_tonnage(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return con.execute("""
        SELECT c.device_id, d.material_stream, d.container_volume_m3,
               date_trunc('month', timezone('Europe/Helsinki', c.actual_at))::DATE AS month,
               sum(c.device_estimated_collected_kg) / 1000.0 AS tonnes
        FROM collection_events c JOIN devices d USING (device_id)
        WHERE c.status = 'COMPLETED' AND c.device_estimated_collected_kg IS NOT NULL
        GROUP BY ALL ORDER BY c.device_id, month""").df()


def backtest(monthly: pd.DataFrame) -> pd.DataFrame:
    """One row per eligible device: own forecast, peer forecast, actual, relative errors."""
    months = sorted(monthly["month"].unique())
    n_held = max(1, round(len(months) * HELDOUT_SHARE))
    n_hist = len(months) - n_held
    cut = months[n_hist - 1]
    hist, held = monthly[monthly.month <= cut], monthly[monthly.month > cut]

    keys = ["device_id", "material_stream", "container_volume_m3"]
    h = hist.groupby(keys).agg(own=("tonnes", "mean"), n_hist=("month", "nunique")).reset_index()
    a = held.groupby("device_id").agg(actual=("tonnes", "mean"), n_held=("month", "nunique")).reset_index()
    df = h.merge(a, on="device_id")
    df = df[(df.n_hist >= max(1, n_hist - 1)) & (df.n_held >= max(1, n_held - 1)) & (df.actual > 0)].copy()

    # Peer mean excluding self: (group sum - own) / (group count - 1); fall back to material-only groups.
    for level, cols in (("material+size", ["material_stream", "container_volume_m3"]), ("material", ["material_stream"])):
        g = df.groupby(cols)["own"]
        n = g.transform("count") - 1
        mean = (g.transform("sum") - df["own"]) / n.where(n > 0)
        col_ok = n >= MIN_PEERS
        if level == "material+size":
            df["peer"], df["peer_level"] = mean.where(col_ok), level
        else:
            fill = df["peer"].isna() & col_ok
            df.loc[fill, "peer"], df.loc[fill, "peer_level"] = mean[fill], level
    df = df[df.peer.notna()].copy()
    df["own_err"] = (df.own - df.actual).abs() / df.actual
    df["peer_err"] = (df.peer - df.actual).abs() / df.actual
    return df.sort_values("device_id").reset_index(drop=True)


def forecast_facts(con: duckdb.DuckDBPyConnection) -> dict:
    monthly = monthly_tonnage(con)
    bt = backtest(monthly)
    n_months = monthly["month"].nunique()
    n_held = max(1, round(n_months * HELDOUT_SHARE))
    n = len(bt)

    def pct(x: float) -> float:
        return round(100 * float(x), 1)

    def fig(value, formula):
        return Figure(value, "%", "estimated", formula, SOURCES, assumptions=ASSUMPTIONS).to_dict()

    by_material = (bt.groupby("material_stream")
                   .agg(devices=("device_id", "count"), own=("own_err", "median"), peer=("peer_err", "median"))
                   .reset_index().sort_values("material_stream"))
    return {
        "method": {"history_months": n_months - n_held, "heldout_months": n_held, "devices": n, "min_peers": MIN_PEERS,
                   "peer_definition": "same material stream and container size, excluding the device itself "
                                      "(material only if fewer than MIN_PEERS)"},
        "own_history_error_median_pct": fig(pct(bt.own_err.median()), "median |own-history mean - actual| / actual"),
        "own_history_error_p80_pct": fig(pct(bt.own_err.quantile(0.8)), "80th percentile of own-history relative error"),
        "peer_error_median_pct": fig(pct(bt.peer_err.median()), "median |peer mean - actual| / actual"),
        "peer_error_p80_pct": fig(pct(bt.peer_err.quantile(0.8)), "80th percentile of peer relative error"),
        "own_better_share_pct": fig(pct((bt.own_err < bt.peer_err).mean()),
                                    "share of devices where own-history error < peer error"),
        "by_material": [{"material_stream": r.material_stream, "devices": int(r.devices),
                         "own_error_median_pct": pct(r.own), "peer_error_median_pct": pct(r.peer)}
                        for r in by_material.itertuples()],
    }
