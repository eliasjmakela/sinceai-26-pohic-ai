"""Market before/after simulation (PRODUCT.md §3, beat 4). Stylised, deterministic, one region, one tender round.

Unit of tender: an *account* = one customer's devices in the region (the devices the trips model can model).
Each account is tendered as one contract. Its current operator is its incumbent: it holds the account's history.
The other operators active in the region, plus `new_entrants` from outside, are the challengers.

Before (per trip, private data)  -- decision (c): the price is what the customer actually paid (observed invoices).
  Challengers could only offer per kg by forecasting the volume from peers, error σ_ent (forecast backtest), so they
  add a risk premium; we report how many accounts a challenger would win even so ("contestable today").
After (per kg, FullLoad data)
  Lifts are weight-triggered (trips model). Every operator forecasts with device data, error σ_after
  = sqrt(σ_inc² + σ_sensor²). Every operator pays the Europress fee per tonne. Bids converge; decision (b): the
  winner prices just below the second-best bid, never above today's price and never below its own bid.
  If even the best per-kg bid is above today's price, the customer keeps today's contract (no switch, no fee).

Bid (annual, cents) = cost × (1 + min_margin) × (1 + risk_z × σ)
  cost(before) = cost_share × today's tendered charges            (trip part + tonne part)
  cost(after)  = cost_share × (trip part × weight lifts / actual lifts + tonne part) + fee × tonnes
  challengers from outside the region have cost × (1 − entrant_cost_advantage);
  operators also differ per account (route fit): cost × (1 + cost_spread × u), u in [-1, 1) a fixed hash of
  (operator, account) -- deterministic, identical in Python and TypeScript (FNV-1a 32-bit);
  route density: an operator with regional tonnage share s runs cost × (1 − density_benefit × s), so the incumbent's
  real efficiency advantage survives -- only its *information* advantage disappears.
Tendered charges = trip-driven + tonne-driven invoice lines (fleet.TRIP_LINES, fleet.TONNE_LINES); rental, credits
and other lines are outside the tender and identical in both regimes.

Every number from this module is *simulated* except the observed inputs. The browser runs the same `simulate` maths
for the sliders (web/src/market/model.ts); `parity_cases` lets a test check both give identical results.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import duckdb
import pandas as pd
import yaml

from .config import PARAMS_PATH
from .figures import Figure
from .fleet import TONNE_LINES, TRIP_LINES, _in
from .forecast import backtest, monthly_tonnage
from .trips import device_trips

SOURCES = ("invoice_lines.amount_eur", "invoice_lines.line_type", "invoices.contract_id", "contracts.device_id",
           "devices.customer_id", "devices.operator_id", "sites.region_code", "collection_events (trips model)")
ASSUMPTIONS = ("One region, one tender round, closed-form bids; no routing, capacity limits or learning",
               "Operator cost = cost_share x today's price (hypothetical, params.yaml)",
               "Forecast errors from the pipeline's backtest on synthetic data",
               "Simulation, not a prediction of real prices or savings")


@dataclass(frozen=True)
class Params:
    cost_share: float
    min_margin: float
    risk_z: float
    new_entrants: int
    entrant_cost_advantage: float
    cost_spread: float
    density_benefit: float
    europress_fee_cents_per_t: int
    sigma_sensor: float


def load_params() -> Params:
    raw = yaml.safe_load(PARAMS_PATH.read_text(encoding="utf-8"))["market"]
    v = {k: raw[k]["value"] for k in raw}
    v["europress_fee_cents_per_t"] = round(v.pop("europress_fee_eur_per_t") * 100)
    v["new_entrants"] = int(v["new_entrants"])
    return Params(**v)


# ---------------------------------------------------------------- inputs (observed, precomputed)

def pick_region(con: duckdb.DuckDBPyConnection) -> str:
    """The region with the most operators, then the most devices."""
    return con.execute("""
        SELECT s.region_code FROM devices d JOIN sites s USING (site_id)
        GROUP BY 1 ORDER BY count(DISTINCT d.operator_id) DESC, count(*) DESC, 1 LIMIT 1""").fetchone()[0]


def accounts(con: duckdb.DuckDBPyConnection, region: str) -> pd.DataFrame:
    trips = device_trips(con)
    trips = trips[trips.weight_trips.notna()][["device_id", "actual_lifts", "weight_trips", "annual_kg"]]
    charges = con.execute(f"""
        SELECT ct.device_id, d.customer_id, d.operator_id, s.region_code,
               sum(round(l.amount_eur * 100)) FILTER (WHERE l.line_type IN {_in(TRIP_LINES)}) AS trip_cents,
               sum(round(l.amount_eur * 100)) FILTER (WHERE l.line_type IN {_in(TONNE_LINES)}) AS tonne_cents
        FROM invoice_lines l JOIN invoices i USING (invoice_id) JOIN contracts ct ON ct.contract_id = i.contract_id
        JOIN devices d ON d.device_id = ct.device_id JOIN sites s ON s.site_id = d.site_id
        WHERE s.region_code = ? GROUP BY ALL""", [region]).df()
    df = charges.merge(trips, on="device_id")
    df[["trip_cents", "tonne_cents"]] = df[["trip_cents", "tonne_cents"]].fillna(0).astype("int64")
    # The account's incumbent = the operator carrying most of its tonnage.
    inc = (df.groupby(["customer_id", "operator_id"]).annual_kg.sum().reset_index()
           .sort_values(["customer_id", "annual_kg", "operator_id"], ascending=[True, False, True])
           .drop_duplicates("customer_id")[["customer_id", "operator_id"]].rename(columns={"operator_id": "incumbent"}))
    acc = (df.groupby("customer_id").agg(devices=("device_id", "count"), trip_cents=("trip_cents", "sum"),
                                         tonne_cents=("tonne_cents", "sum"), actual_lifts=("actual_lifts", "sum"),
                                         weight_lifts=("weight_trips", "sum"), kg=("annual_kg", "sum"))
           .reset_index().merge(inc, on="customer_id"))
    acc = acc[(acc.trip_cents + acc.tonne_cents) > 0].copy()
    acc["weight_lifts"] = acc.weight_lifts.astype("int64")
    return acc.sort_values("customer_id").reset_index(drop=True)


def forecast_sigmas(con: duckdb.DuckDBPyConnection) -> tuple[float, float]:
    bt = backtest(monthly_tonnage(con))
    return round(float(bt.own_err.median()), 4), round(float(bt.peer_err.median()), 4)


# ---------------------------------------------------------------- the model (mirrored in TypeScript)

def fnv1a(text: str) -> int:
    h = 0x811C9DC5
    for b in text.encode("utf-8"):
        h = ((h ^ b) * 0x01000193) & 0xFFFFFFFF
    return h


def route_fit(operator: str, customer_id: str) -> float:
    """Fixed per (operator, account) number in [-1, 1)."""
    return 2 * fnv1a(f"{operator}|{customer_id}") / 2 ** 32 - 1


def simulate(accs: list[dict], operators: list[str], sigma_inc: float, sigma_ent: float, p: Params) -> dict:
    """Pure function on plain data so the TypeScript mirror can reproduce it exactly. Money in cents (floats)."""
    entrants = [f"NEW-{i + 1}" for i in range(p.new_entrants)]
    sigma_after = math.sqrt(sigma_inc ** 2 + p.sigma_sensor ** 2)
    total_kg = sum(a["kg"] for a in accs)
    density = {o: 0.0 for o in operators + entrants}
    for a in accs:
        density[a["incumbent"]] += a["kg"] / total_kg
    rows = []
    for a in accs:
        today = a["trip_cents"] + a["tonne_cents"]
        t = a["kg"] / 1000
        challengers = [o for o in operators if o != a["incumbent"]] + entrants

        def eff(o: str) -> float:
            base = 1 - p.entrant_cost_advantage if o.startswith("NEW-") else 1.0
            return base * (1 + p.cost_spread * route_fit(o, a["customer_id"])) * (1 - p.density_benefit * density[o])

        cost_before = p.cost_share * today
        rel = {o: eff(o) / eff(a["incumbent"]) for o in [a["incumbent"]] + challengers}   # cost relative to incumbent
        bids_before = {o: cost_before * rel[o] * (1 + p.min_margin) * (1 + p.risk_z * sigma_ent) for o in challengers}
        best_challenger_before = min(bids_before.values()) if bids_before else math.inf

        cost_after = (p.cost_share * (a["trip_cents"] * a["weight_lifts"] / a["actual_lifts"] + a["tonne_cents"])
                      + p.europress_fee_cents_per_t * t)
        bids_after = {o: cost_after * rel[o] * (1 + p.min_margin) * (1 + p.risk_z * sigma_after)
                      for o in [a["incumbent"]] + challengers}
        ranked = sorted(bids_after.items(), key=lambda kv: (kv[1], kv[0] != a["incumbent"], kv[0]))
        winner, win_bid = ranked[0]
        second = ranked[1][1] if len(ranked) > 1 else today
        keeps_today = win_bid > today
        best_challenger_after = min(b for o, b in bids_after.items() if o != a["incumbent"]) if challengers else math.inf
        price_after = today if keeps_today else max(win_bid, min(second, today))
        if keeps_today:
            winner = a["incumbent"]
        rows.append({
            "customer_id": a["customer_id"], "incumbent": a["incumbent"], "tonnes": t,
            "lifts_before": a["actual_lifts"],
            "price_before": today, "contestable_today": best_challenger_before < today,
            "contestable_after": best_challenger_after < today,
            "winner_after": winner, "price_after": price_after, "keeps_today": keeps_today,
            "lifts_after": a["actual_lifts"] if keeps_today else a["weight_lifts"],
            "operator_margin_before": today - cost_before,
            "operator_margin_after": (today - cost_before) if keeps_today else price_after - cost_after * rel[winner],
            "europress_fee": 0.0 if keeps_today else p.europress_fee_cents_per_t * t,
        })
    return {"rows": rows, "summary": summarise(rows, operators + entrants), "sigma_after": sigma_after}


def _hhi(shares: dict[str, float]) -> float:
    return sum((100 * s) ** 2 for s in shares.values())


def summarise(rows: list[dict], all_ops: list[str]) -> dict:
    t = sum(r["tonnes"] for r in rows)
    def share(key: str) -> dict[str, float]:
        out = {o: 0.0 for o in all_ops}
        for r in rows:
            out[r[key]] += r["tonnes"] / t
        return out
    before, after = share("incumbent"), share("winner_after")
    pb, pa = sum(r["price_before"] for r in rows), sum(r["price_after"] for r in rows)
    lb, la = sum(r["lifts_before"] for r in rows), sum(r["lifts_after"] for r in rows)
    return {
        "accounts": len(rows), "tonnes": t,
        "customer_cost_before": pb, "customer_cost_after": pa,
        "cost_per_t_before": pb / t, "cost_per_t_after": pa / t,
        "lifts_before": lb, "lifts_after": la, "t_per_lift_before": t / lb, "t_per_lift_after": t / la,
        "share_before": before, "share_after": after, "hhi_before": _hhi(before), "hhi_after": _hhi(after),
        "accounts_switched": sum(r["winner_after"] != r["incumbent"] for r in rows),
        "accounts_contestable_today": sum(r["contestable_today"] for r in rows),
        "accounts_contestable_after": sum(r["contestable_after"] for r in rows),
        "accounts_keep_today": sum(r["keeps_today"] for r in rows),
        "operator_margin_before": sum(r["operator_margin_before"] for r in rows),
        "operator_margin_after": sum(r["operator_margin_after"] for r in rows),
        "europress_fee": sum(r["europress_fee"] for r in rows),
    }


# ---------------------------------------------------------------- bundle section

def parity_cases(base: Params) -> list[dict]:
    """Fixed parameter sets; the TypeScript parity check must reproduce their summaries."""
    variants = [{}, {"new_entrants": 0}, {"entrant_cost_advantage": 0.15, "new_entrants": 2, "sigma_sensor": 0.05},
                {"risk_z": 0.5, "europress_fee_cents_per_t": 0}]
    return [{**asdict(base), **v} for v in variants]


def market_facts(con: duckdb.DuckDBPyConnection) -> dict:
    region = pick_region(con)
    acc = accounts(con, region)
    operators = sorted(acc.incumbent.unique().tolist() + [
        o for o in con.execute("""SELECT DISTINCT d.operator_id FROM devices d JOIN sites s USING (site_id)
                                  WHERE s.region_code = ? ORDER BY 1""", [region]).df().operator_id
        if o not in set(acc.incumbent)])
    sigma_inc, sigma_ent = forecast_sigmas(con)
    p = load_params()
    inputs = acc.to_dict("records")
    for r in inputs:   # plain JSON types
        for k, v in r.items():
            r[k] = v.item() if hasattr(v, "item") else v
    res = simulate(inputs, operators, sigma_inc, sigma_ent, p)
    s = res["summary"]

    def fig(value, unit, formula, tag="simulated"):
        return Figure(value, unit, tag, formula, SOURCES, assumptions=ASSUMPTIONS).to_dict()

    cases = parity_cases(p)
    return {
        "region": region, "operators": operators, "sigma_inc": sigma_inc, "sigma_ent": sigma_ent,
        "params": asdict(p), "inputs": inputs,
        "headline": {
            "cost_per_t_before": fig(round(s["cost_per_t_before"] / 100, 2), "EUR/t",
                                     "today's tendered charges / tonnes (observed)", tag="observed"),
            "cost_per_t_after": fig(round(s["cost_per_t_after"] / 100, 2), "EUR/t", "sum of after-regime prices / tonnes"),
            "lifts_before": fig(s["lifts_before"], "count", "actual completed lifts", tag="observed"),
            "lifts_after": fig(s["lifts_after"], "count", "weight-triggered lifts (trips model)"),
            "contestable_before": fig(s["accounts_contestable_today"], "count",
                                      "accounts where a challenger's per-kg bid (peer forecast, sigma_ent) beats today's price"),
            "contestable_after": fig(s["accounts_contestable_after"], "count",
                                     "accounts where a challenger's per-kg bid (FullLoad forecast) beats today's price"),
            "incumbent_margin_before_eur": fig(round(s["operator_margin_before"] / 100, 2), "EUR",
                                               "today's price - cost_share x today's price", tag="hypothetical"),
            "operator_margin_after_eur": fig(round(s["operator_margin_after"] / 100, 2), "EUR",
                                             "tender price - winner's cost"),
            "accounts_switched": fig(s["accounts_switched"], "count", "accounts whose tender winner is not the incumbent"),
            "europress_fee_eur": fig(round(s["europress_fee"] / 100, 2), "EUR", "fee per tonne x tonnes", tag="hypothetical"),
        },
        "default": {"summary": s, "rows": res["rows"]},
        "parity": [{"params": c, "summary": simulate(inputs, operators, sigma_inc, sigma_ent, Params(**c))["summary"]}
                   for c in cases],
    }
