"""Beat 6: Europress business model (PRODUCT.md §1, §4). Network-level, per year, over the lease horizon.

Europress funds the weighing hardware; operators pay a service fee; customers pay nothing; Europress also sells more
machines. Inputs are the business team's assumptions (message of 7 Nov; scripts pending) in params.yaml `business`,
plus two numbers from our own pipeline: tonnes per device-year (fleet average) and the installed-cost ranges from
Part 1 v2 (`part1/installed_cost.json` on branch weighing-v2) as the alternative hardware cost.

  investment        = devices x (T0 share x T0 cost + H1 share x H1 cost)                    one-off, EUR
  service revenue   = devices x paying coverage x fee                                       per year, EUR
                      fee = fee per device per month x 12          (fee_mode "per_device_month")
                          = fee per tonne x tonnes per device-year  (fee_mode "per_tonne")
  extra sales margin= devices / renewal years x sales growth x device price x margin         per year, EUR
  net per year      = service revenue + extra sales margin - opex per device x devices
  payback (years)   = investment / net per year
The browser mirror is web/src/business/model.ts; `parity_cases` lets the parity check compare both.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace

import duckdb
import yaml

from .config import PARAMS_PATH
from .figures import Figure

INSTALLED_COST_SOURCE = "part1/installed_cost.json (branch weighing-v2): H1 factory-fit EUR 548-2,363, T0 EUR 10-125"
H1_FACTORY_FIT = (548, 2363)   # copied from the weighing-v2 branch until it is merged (then read from the file)
T0_FACTORY_FIT = (10, 125)


@dataclass(frozen=True)
class BizParams:
    devices_total: int
    paying_coverage: float
    fee_mode: str
    fee_eur_per_device_month: float
    fee_eur_per_t: float
    t0_share: float
    t0_cost_eur: float
    h1_share: float
    h1_cost_eur: float
    opex_eur_per_device_year: float
    sales_growth: float
    device_price_eur: float
    device_margin: float
    renewal_years: float
    horizon_years: float
    tonnes_per_device_year: float


def load_params(tonnes_per_device_year: float) -> BizParams:
    raw = yaml.safe_load(PARAMS_PATH.read_text(encoding="utf-8"))["business"]
    v = {k: raw[k]["value"] for k in raw}
    return BizParams(**v, tonnes_per_device_year=tonnes_per_device_year)


def simulate(p: BizParams) -> dict:
    fee_year = (p.fee_eur_per_device_month * 12 if p.fee_mode == "per_device_month"
                else p.fee_eur_per_t * p.tonnes_per_device_year)
    investment = p.devices_total * (p.t0_share * p.t0_cost_eur + p.h1_share * p.h1_cost_eur)
    revenue = p.devices_total * p.paying_coverage * fee_year
    extra_sales = p.devices_total / p.renewal_years * p.sales_growth * p.device_price_eur * p.device_margin
    opex = p.devices_total * p.opex_eur_per_device_year
    net = revenue + extra_sales - opex
    return {
        "fee_per_device_year": fee_year, "investment": investment, "service_revenue": revenue,
        "extra_sales_margin": extra_sales, "opex": opex, "net_per_year": net,
        "payback_years": investment / net if net > 0 else None,
        "cumulative_net_horizon": net * p.horizon_years - investment,
        "customer_pays": 0.0,
    }


def tonnes_per_device_year(con: duckdb.DuckDBPyConnection) -> float:
    kg, n = con.execute("""SELECT sum(device_estimated_collected_kg), count(DISTINCT device_id)
                           FROM collection_events WHERE status = 'COMPLETED' AND device_estimated_collected_kg IS NOT NULL""").fetchone()
    return round(kg / 1000 / n, 1)


def parity_cases(base: BizParams) -> list[dict]:
    variants = [{}, {"fee_mode": "per_tonne"}, {"h1_cost_eur": H1_FACTORY_FIT[1], "t0_cost_eur": T0_FACTORY_FIT[1]},
                {"paying_coverage": 1.0, "sales_growth": 0.0}]
    return [asdict(replace(base, **v)) for v in variants]


def business_facts(con: duckdb.DuckDBPyConnection) -> dict:
    p = load_params(tonnes_per_device_year(con))
    s = simulate(p)

    def fig(v, unit, formula, tag="hypothetical"):
        return Figure(None if v is None else round(v, 1), unit, tag, formula,
                      ("params.yaml: business (business team assumptions)", "collection_events (tonnes per device)",
                       INSTALLED_COST_SOURCE)).to_dict()

    return {
        "params": asdict(p),
        "installed_cost_ranges": {"H1_factory_fit": H1_FACTORY_FIT, "T0_factory_fit": T0_FACTORY_FIT,
                                  "source": INSTALLED_COST_SOURCE,
                                  "note": "Part 1 installed cost includes 6-year maintenance; opex is counted separately here, "
                                          "so the Part 1 figure slightly double-counts upkeep."},
        "default": s,
        "headline": {
            "investment_eur": fig(s["investment"], "EUR", "devices x (T0 share x T0 cost + H1 share x H1 cost)"),
            "service_revenue_eur": fig(s["service_revenue"], "EUR", "devices x paying coverage x fee per device-year"),
            "extra_sales_margin_eur": fig(s["extra_sales_margin"], "EUR",
                                          "devices / renewal years x sales growth x device price x margin"),
            "net_per_year_eur": fig(s["net_per_year"], "EUR", "service revenue + extra sales margin - opex"),
            "payback_years": fig(s["payback_years"], "years", "investment / net per year"),
        },
        "parity": [{"params": c, "result": simulate(BizParams(**c))} for c in parity_cases(p)],
    }


if __name__ == "__main__":
    from .config import data_root
    from .kit import open_dataset
    print(json.dumps(business_facts(open_dataset(data_root())), indent=2, default=str))
