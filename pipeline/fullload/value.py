"""Value per device per year, recomputed from our own pipeline (beat 6). Fleet averages over the devices each lever
can be computed for. Compared, where available, with the business team's independent figures (`TEAM_FIGURES`,
their scripts are not yet in this repo).

Levers (EUR per device per year):
  avoidable_trips      customer: trip-driven charges x share of lifts that are avoidable.
                       Lower = share flagged by our premature-lift rule; upper = share removed by the trips model.
  pricing_risk         operator: the risk premium a challenger must add without the data, removed by OpenWeight:
                       cost_share x tendered charges x (1 + min_margin) x risk_z x (sigma_ent - sigma_inc). Hypothetical
                       (market parameters in params.yaml).
  expensive_tonnes     customer: cost per tonne above the median of peer devices (same material and region) x tonnes,
                       positive part. Needs a known mass, i.e. the weight.
  invoice_differences  customer: invoiced above the contract-expected amount (kit B1 calculator), positive part.
  contamination        not recomputed: material quality is assessed only by the operator; Europress cannot measure it.
  contract_visibility  not priced: on-time share, missed visits and ticket sharing per customer (service_check in
                       customer.py), the customer's view of whether the contract is kept.
"""
from __future__ import annotations

from pathlib import Path

import duckdb

from .figures import Figure
from .fleet import device_charges
from .market import load_params
from .premature import flag_lifts
from .scorecard import invoice_lines_vs_contract
from .trips import device_trips

TEAM_FIGURES = {   # business team analysis, 7 Nov (message; scripts pending) -- EUR per device per year
    "pricing_risk": 1930, "avoidable_trips": 1570, "expensive_tonnes": 1245, "contamination": 400,
    "invoice_differences": 100,
}
SOURCES = ("invoice_lines.amount_eur", "invoice_lines.line_type", "contracts.device_id", "collection_events",
           "trips model", "premature-lift rule", "kit B1 calculator", "params.yaml (market)")


def value_per_device(con: duckdb.DuckDBPyConnection, root: Path, sigma_inc: float, sigma_ent: float) -> dict:
    ch = device_charges(con).assign(trip_eur=lambda d: d.trip_cents / 100, tonne_eur=lambda d: d.tonne_cents / 100)
    tr = device_trips(con)
    tr = tr[tr.weight_trips.notna()][["device_id", "actual_lifts", "weight_trips", "annual_kg"]]
    df = ch.merge(tr, on="device_id")
    fl = flag_lifts(con)
    fl = fl[fl.status == "COMPLETED"].groupby("device_id").flagged.mean().rename("flag_share").reset_index()
    df = df.merge(fl, on="device_id", how="left").fillna({"flag_share": 0.0})
    df["model_share"] = (1 - df.weight_trips.astype(float) / df.actual_lifts).clip(lower=0)

    avoid_lo = float((df.trip_eur * df.flag_share).mean())
    avoid_hi = float((df.trip_eur * df.model_share).mean())

    p = load_params()
    tendered = df.trip_eur + df.tonne_eur
    risk = float((p.cost_share * tendered * (1 + p.min_margin) * p.risk_z * (sigma_ent - sigma_inc)).mean())

    df["t"] = df.annual_kg / 1000
    df["cpt"] = tendered / df.t.where(df.t > 0)
    med = df.groupby(["material_stream", "region_code"]).cpt.transform("median")
    expensive = float(((df.cpt - med).clip(lower=0) * df.t).fillna(0).mean())

    il = invoice_lines_vs_contract(con, root)
    over = il.assign(o=(il.cents - il.exp_cents).clip(lower=0)).groupby("device_id").o.sum() / 100
    invoice = float(over.reindex(df.device_id).fillna(0).mean())

    def fig(v, formula, tag):
        return Figure(round(v), "EUR", tag, formula, SOURCES).to_dict()

    rows = [
        {"lever": "pricing_risk", "who": "operator", "needs_weight": "yes: only the weight history removes it",
         "ours": fig(risk, "cost_share x tendered x (1+min_margin) x risk_z x (sigma_ent - sigma_inc), mean per device",
                     "hypothetical"), "ours_range": None},
        {"lever": "avoidable_trips", "who": "customer",
         "needs_weight": "fill level finds them; the weight makes per-kg pricing possible",
         "ours": fig(avoid_hi, "trip-driven charges x trips-model removed share, mean per device", "simulated"),
         "ours_range": [round(avoid_lo), round(avoid_hi)]},
        {"lever": "expensive_tonnes", "who": "customer", "needs_weight": "yes: cost per tonne needs the mass",
         "ours": fig(expensive, "(cost per tonne - peer median, same material and region)+ x tonnes, mean per device",
                     "estimated"), "ours_range": None},
        {"lever": "invoice_differences", "who": "customer", "needs_weight": "partly (tonnage lines)",
         "ours": fig(invoice, "invoiced above contract-expected (kit B1), mean per device", "observed"), "ours_range": None},
        {"lever": "contamination", "who": "customer", "needs_weight": "partly (density)", "ours": None, "ours_range": None,
         "note": "not recomputed: quality is assessed only by the operator"},
        {"lever": "contract_visibility", "who": "customer", "needs_weight": "no (service data) / yes (tonnage checks)",
         "ours": None, "ours_range": None, "note": "not priced: on-time, missed visits, ticket sharing (beat 2)"},
    ]
    for r in rows:
        r["team"] = TEAM_FIGURES.get(r["lever"])
    return {"devices": int(len(df)), "rows": rows,
            "note": ("Fleet averages on synthetic data; levers overlap partly (fewer trips also lowers cost per tonne), "
                     "so do not add them up. Team figures: business team analysis, scripts pending.")}
