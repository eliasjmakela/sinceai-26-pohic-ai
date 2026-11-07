"""The operator fee: EUR 30 per weighed device per month, customers free (PRICING.md).

Architecture (decided 7 Nov evening): **every new compactor gets the H7 hydraulic self-lift**; billing stays on
the operator's certified weighbridge, the device weight is for planning and cross-checks. The cash-flow structure is
the team document's (`analysis/final_v2.py`, LIITE §6.3), reproduced here so the fee decision is traceable, with
the H7 cost replaced by Part 1's installed cost (`part1/installed_cost.json`, capex without the 6-year upkeep,
which is counted per year instead).

Per year y = 1..years (weighed units = new units x y; ramp = min(y / ramp years, 1)):
  operator fees   = weighed x adoption x ramp x fee x 12
  tender packages = weighed / tender interval x tender share x bidders x package price x ramp
  extra sales     = new units x sales growth x min((y - 1) / ramp years, 1) x device price x margin
  costs           = fixed cost + weighed x (platform + H7 upkeep)
  investment      = new units x H7 capex
Two sides are reported: Europress (NPV, payback, break-even fee and adoption) and the operator (the fee against its
hard gain from avoided visits and against its profit per device today).
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace

import duckdb
import yaml

from .config import PARAMS_PATH
from .figures import Figure
from .weighing import COST_PATH


BASE = "base (H7 EUR 1,000, team decision)"
RECOMMENDED_FEE = 30   # PRICING.md: EUR 20 never pays back with every new unit weighed


@dataclass(frozen=True)
class PricingParams:
    years: int
    discount_rate: float
    ramp_years: float
    new_units_per_year: int
    adoption: float
    h7_capex_eur: float
    platform_eur_per_unit_year: float
    h7_upkeep_eur_per_unit_year: float
    fixed_cost_eur_per_year: float
    package_eur: float
    bidders: float
    tender_share: float
    tender_interval_years: float
    sales_growth: float
    device_price_eur: float
    device_margin: float
    fees_eur_per_month: tuple[float, ...]
    operator_cost_per_visit_eur: tuple[float, float]
    operator_value_team_eur: float
    operator_margin_pct: tuple[float, float]


def h7_cost_split() -> dict:
    """H7 factory-fit cost from Part 1, split into capex and the yearly upkeep (6-year maintenance line / 6)."""
    c = json.loads(COST_PATH.read_text(encoding="utf-8"))
    h7 = c["candidates"]["H7"]
    maint = next(line["factory_fit"] for line in h7["lines"] if line["line"].startswith("maintenance"))
    years = c["lease_years"]
    lo, hi = h7["factory_fit_eur"]["low"] - maint[0], h7["factory_fit_eur"]["high"] - maint[1]
    return {"capex_eur": [lo, hi], "capex_mid_eur": round((lo + hi) / 2),
            "upkeep_eur_per_year": [round(maint[0] / years), round(maint[1] / years)],
            "upkeep_mid_eur_per_year": round((maint[0] + maint[1]) / 2 / years)}


def load_params() -> PricingParams:
    raw = yaml.safe_load(PARAMS_PATH.read_text(encoding="utf-8"))["pricing"]
    v = {k: raw[k]["value"] for k in raw}
    for k in ("fees_eur_per_month", "operator_cost_per_visit_eur", "operator_margin_pct"):
        v[k] = tuple(v[k])
    h7 = h7_cost_split()
    # capex: the team's planning figure (params.yaml, decided 7 Nov evening); upkeep: Part 1 midpoint
    return PricingParams(**v, h7_upkeep_eur_per_unit_year=h7["upkeep_mid_eur_per_year"])


def cash_flows(pp: PricingParams, fee: float) -> list[float]:
    out = []
    for y in range(1, pp.years + 1):
        weighed = pp.new_units_per_year * y
        ramp = min(y / pp.ramp_years, 1)
        fees = weighed * pp.adoption * ramp * fee * 12
        packages = weighed / pp.tender_interval_years * pp.tender_share * pp.bidders * pp.package_eur * ramp
        sales = (pp.new_units_per_year * pp.sales_growth * min((y - 1) / pp.ramp_years, 1)
                 * pp.device_price_eur * pp.device_margin)
        costs = pp.fixed_cost_eur_per_year + weighed * (pp.platform_eur_per_unit_year + pp.h7_upkeep_eur_per_unit_year)
        out.append(fees + packages + sales - costs - pp.new_units_per_year * pp.h7_capex_eur)
    return out


def summarise(cfs: list[float], rate: float) -> dict:
    cum, deepest, payback = 0.0, 0.0, None
    for y, c in enumerate(cfs, start=1):
        cum += c
        deepest = min(deepest, cum)
        if payback is None and cum >= 0:
            payback = y
    npv_ = sum(c / (1 + rate) ** y for y, c in enumerate(cfs, start=1))
    return {"npv_eur": round(npv_), "payback_year": payback, "deepest_eur": round(deepest), "cumulative_eur": round(cum)}


def npv(pp: PricingParams, fee: float) -> float:
    return summarise(cash_flows(pp, fee), pp.discount_rate)["npv_eur"]


def break_even_fee(pp: PricingParams) -> int | None:
    """Smallest whole-euro monthly fee with NPV >= 0."""
    return next((f for f in range(0, 151) if npv(pp, f) >= 0), None)


def break_even_adoption(pp: PricingParams, fee: float) -> float | None:
    """Smallest paying share of weighed units (whole percent) with NPV >= 0 at this fee."""
    return next((p / 100 for p in range(0, 101) if npv(replace(pp, adoption=p / 100), fee) >= 0), None)


def max_h7_capex(pp: PricingParams, fee: float) -> int | None:
    """Highest H7 capex (EUR, step 10) with NPV >= 0 at this fee: the design-to-cost target."""
    return next((c for c in range(5000, -1, -10) if npv(replace(pp, h7_capex_eur=c), fee) >= 0), None)


def scenarios(pp: PricingParams) -> dict[str, PricingParams]:
    h7 = h7_cost_split()
    lo, hi = h7["capex_eur"]
    return {
        "team document (H7 EUR 825, upkeep EUR 50)": replace(pp, h7_capex_eur=825, h7_upkeep_eur_per_unit_year=50),
        "base (H7 EUR 1,000, team decision)": pp,
        "Part 1 mid H7": replace(pp, h7_capex_eur=h7["capex_mid_eur"]),
        "cheap H7": replace(pp, h7_capex_eur=lo, h7_upkeep_eur_per_unit_year=h7["upkeep_eur_per_year"][0]),
        "dear H7": replace(pp, h7_capex_eur=hi, h7_upkeep_eur_per_unit_year=h7["upkeep_eur_per_year"][1]),
        "adoption 40 %": replace(pp, adoption=0.4),
        "no tender packages": replace(pp, package_eur=0),
        "no extra machine sales": replace(pp, sales_growth=0),
    }


def parity_cases(pp: PricingParams) -> list[dict]:
    """Inputs and outputs for the browser mirror (web/src/pricing/model.ts, `npm run parity`)."""
    variants = [{}, {"h7_capex_eur": 825, "h7_upkeep_eur_per_unit_year": 50}, {"adoption": 0.4, "package_eur": 0},
                {"sales_growth": 0, "h7_capex_eur": 1000}]
    out = []
    for v in variants:
        sp = replace(pp, **v)
        for fee in (20, 30):
            out.append({"params": asdict(sp), "fee": fee, "cash_flows": cash_flows(sp, fee),
                        "summary": summarise(cash_flows(sp, fee), sp.discount_rate)})
    return out


def customer_spend_median_eur(con: duckdb.DuckDBPyConnection) -> float:
    """Median yearly invoiced amount per device (all lines except material credits): the operator's revenue."""
    return round(con.execute("""
        SELECT median(t) FROM (
            SELECT k.device_id, sum(l.amount_eur) FILTER (WHERE l.line_type <> 'MATERIAL_CREDIT') AS t
            FROM invoice_lines l JOIN invoices i USING (invoice_id) JOIN contracts k ON k.contract_id = i.contract_id
            GROUP BY 1)""").fetchone()[0])


def operator_side(pp: PricingParams, visits_per_device: float, fewer_visits_pct: tuple[float, float],
                  spend_median_eur: float) -> dict:
    lo_v, hi_v = (visits_per_device * p / 100 for p in fewer_visits_pct)
    lo_c, hi_c = pp.operator_cost_per_visit_eur
    gain = (round(lo_v * lo_c), round(((lo_v + hi_v) / 2) * ((lo_c + hi_c) / 2)), round(hi_v * hi_c))
    lo_m, hi_m = pp.operator_margin_pct
    profit = (round(spend_median_eur * lo_m / 100), round(spend_median_eur * hi_m / 100))
    rows = []
    for fee in pp.fees_eur_per_month:
        year = fee * 12
        rows.append({"fee_eur_per_month": fee, "fee_eur_per_year": year,
                     "share_of_hard_gain_mid_pct": round(100 * year / gain[1]),
                     "share_of_team_value_pct": round(100 * year / pp.operator_value_team_eur),
                     "share_of_profit_today_pct": [round(100 * year / profit[1]), round(100 * year / profit[0])],
                     "net_hard_gain_eur": [gain[0] - year, gain[1] - year, gain[2] - year]})
    return {"visits_per_device": round(visits_per_device, 1), "fewer_visits_pct": list(fewer_visits_pct),
            "hard_gain_eur": list(gain), "spend_median_eur": spend_median_eur, "profit_per_device_today_eur": list(profit),
            "team_value_eur": pp.operator_value_team_eur, "by_fee": rows}


def pricing_facts(con: duckdb.DuckDBPyConnection, visits_per_device: float, fewer_visits_pct: tuple[float, float],
                  pp: PricingParams | None = None) -> dict:
    pp = pp or load_params()
    grid = {name: {"break_even_fee": break_even_fee(sp), "break_even_adoption_at_20": break_even_adoption(sp, 20),
                   "break_even_adoption_at_30": break_even_adoption(sp, 30),
                   "by_fee": {str(f): summarise(cash_flows(sp, f), sp.discount_rate) for f in pp.fees_eur_per_month}}
            for name, sp in scenarios(pp).items()}
    base = grid[BASE]
    src = ("params.yaml: pricing", "part1/installed_cost.json", "pipeline/fullload/pricing.py")

    def fig(v, unit, formula):
        return Figure(v, unit, "hypothetical", formula, src).to_dict()

    team = grid["team document (H7 EUR 825, upkeep EUR 50)"]["by_fee"][str(RECOMMENDED_FEE)]
    return {
        "recommended_fee_eur_per_month": RECOMMENDED_FEE,
        "max_h7_capex_eur": {str(f): max_h7_capex(pp, f) for f in pp.fees_eur_per_month},
        "params": asdict(pp),
        "parity": parity_cases(pp),
        "h7_cost": h7_cost_split(),
        "scenarios": grid,
        "operator": operator_side(pp, visits_per_device, fewer_visits_pct, customer_spend_median_eur(con)),
        "headline": {
            "npv_20_eur": fig(base["by_fee"]["20"]["npv_eur"], "EUR", "10-year NPV at 8 %, EUR 20 per device per month"),
            "npv_30_eur": fig(base["by_fee"]["30"]["npv_eur"], "EUR", "10-year NPV at 8 %, EUR 30 per device per month"),
            "payback_30_year": fig(base["by_fee"]["30"]["payback_year"], "year",
                                   "first year the cumulative cash flow is >= 0, EUR 30, H7 EUR 1,000"),
            "deepest_30_eur": fig(base["by_fee"]["30"]["deepest_eur"], "EUR", "lowest cumulative cash position, EUR 30"),
            "break_even_fee": fig(base["break_even_fee"], "EUR per month", "smallest monthly fee with NPV >= 0"),
            "max_h7_capex_eur": fig(max_h7_capex(pp, RECOMMENDED_FEE), "EUR",
                                    f"highest H7 capex with NPV >= 0 at EUR {RECOMMENDED_FEE} per month (design-to-cost target)"),
            "team_npv_eur": fig(team["npv_eur"], "EUR", f"10-year NPV at EUR {RECOMMENDED_FEE}, team document's H7 EUR 825"),
            "team_payback_year": fig(team["payback_year"], "year", f"payback year at EUR {RECOMMENDED_FEE}, team document's H7 EUR 825"),
        },
    }
