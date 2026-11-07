"""Beats 2 and 3: the hero customer's free view and the same site through an operator's eyes (PRODUCT.md §4).

Beat 2 (customer, free): a year of lifts coloured by fill at lift, today's per-trip cost vs the simulated per-kg
price from the market model, a tender proposal the customer approves, and a plain-language AI-summarized report.
Beat 3 (operator, paid): what an operator can forecast for this customer with and without FullLoad data, and the
per-kg bids that follow (from the market model's bid detail).

The AI report text is written once, frozen in `reports/<customer_id>.md`, and checked: every number in it must appear
in the fact sheet (`report_numbers_ok`). If the check fails, the bundle carries the report as `unchecked`.
"""
from __future__ import annotations

import re
from pathlib import Path

import duckdb
import pandas as pd

from .figures import Figure, eur_from_cents
from .forecast import backtest, monthly_tonnage
from .premature import flag_lifts

REPORTS = Path(__file__).resolve().parent / "reports"
LOW_FILL_PCT = 60
SOURCES = ("collection_events.*", "devices.*", "sites.site_name", "customers.customer_name",
           "invoice_lines (via market model)", "forecast backtest", "market simulation")


def _pct(x: float) -> float:
    return round(100 * x, 1)


def hero_view(con: duckdb.DuckDBPyConnection, market: dict, devices: pd.DataFrame, customer_id: str) -> dict:
    region = market["region"]
    row = next(r for r in market["default"]["rows"] if r["customer_id"] == customer_id)
    dev_ids = sorted(devices.loc[devices.customer_id == customer_id, "device_id"])
    ids = "(" + ", ".join(f"'{d}'" for d in dev_ids) + ")"
    cust = con.execute("SELECT customer_name, primary_sector FROM customers WHERE customer_id = ?", [customer_id]).fetchone()

    dinfo = con.execute(f"""
        SELECT d.device_id, d.material_stream, d.collection_policy, d.fixed_schedule_per_week, d.container_volume_m3,
               d.equipment_class, s.site_name
        FROM devices d JOIN sites s USING (site_id) WHERE d.device_id IN {ids} ORDER BY 1""").df()
    flags = flag_lifts(con)
    lifts = flags[flags.device_id.isin(dev_ids) & (flags.status == "COMPLETED")].copy()
    lifts["date"] = pd.to_datetime(lifts.actual_at).dt.tz_convert("Europe/Helsinki").dt.strftime("%Y-%m-%d")
    lifts = lifts.sort_values(["date", "device_id", "collection_id"])
    dev_rows = devices[devices.device_id.isin(dev_ids)].set_index("device_id")

    devices_out = []
    for r in dinfo.itertuples():
        lf = lifts[lifts.device_id == r.device_id]
        d = dev_rows.loc[r.device_id]
        devices_out.append({
            "device_id": r.device_id, "site": r.site_name, "material": r.material_stream, "policy": r.collection_policy,
            "schedule_per_week": None if pd.isna(r.fixed_schedule_per_week) else float(r.fixed_schedule_per_week),
            "container_m3": float(r.container_volume_m3), "equipment": r.equipment_class,
            "lifts": int(d.actual_lifts), "weight_triggered_lifts": int(d.weight_trips),
            "tonnes": round(float(d.annual_kg) / 1000, 1),
            "median_fill_at_lift_pct": None if lf.device_fill_pct_before.isna().all()
            else round(float(lf.device_fill_pct_before.median()), 1),
        })

    n_lifts = int(len(lifts))
    low = int((lifts.device_fill_pct_before < LOW_FILL_PCT).sum())
    flagged = int(lifts.flagged.sum())
    t = row["tonnes"]
    cost_today, price_kg = row["price_before"], row["price_after"]

    # Beat 3: forecasts for this customer's devices (own history vs peers), from the backtest.
    bt = backtest(monthly_tonnage(con))
    # Per device: errors on a sum of devices partly cancel, so the operator's per-site risk is shown per device.
    hb = bt[bt.device_id.isin(dev_ids)].sort_values("device_id")

    def fig(value, unit, formula, tag="observed"):
        return Figure(value, unit, tag, formula, SOURCES).to_dict()

    facts = {
        "customer_name": cust[0], "sector": cust[1], "region": region, "devices": len(dev_ids),
        "lifts": n_lifts, "low_fill_lifts": low, "low_fill_share_pct": _pct(low / n_lifts),
        "flagged_lifts": flagged, "tonnes": round(t, 1),
        "cost_today_eur": round(eur_from_cents(round(cost_today))), "cost_per_t_today_eur": round(cost_today / 100 / t, 1),
        "price_per_kg_regime_eur": round(eur_from_cents(round(price_kg))),
        "cost_per_t_after_eur": round(price_kg / 100 / t, 1),
        "saving_pct": _pct(1 - price_kg / cost_today), "saving_eur": round(eur_from_cents(round(cost_today - price_kg))),
        "lifts_after": row["lifts_after"], "lift_reduction_pct": _pct(1 - row["lifts_after"] / row["lifts_before"]),
        "incumbent": row["incumbent"], "winner": row["winner_after"],
    }
    report = load_report(customer_id, facts)

    proposal = {
        "schema": "fullload.proposal.v1 (extends smve.recommendation.v0, illustrative)",
        "synthetic": True, "customer_id": customer_id, "region": region,
        "proposal": {"action": "TENDER_PER_KG", "requires_human_approval": True, "auto_execute": False,
                     "contract_term_years": 3,
                     "terms": "per-kg price, weight-triggered lifts, billing on the operator's certified weighbridge"},
        "evidence": {
            "observed": {"lifts_last_12m": n_lifts, "share_lifts_under_60pct_fill": facts["low_fill_share_pct"],
                         "cost_today_eur": facts["cost_today_eur"], "tonnes": facts["tonnes"]},
            "simulated": {"lifts_weight_triggered": row["lifts_after"], "price_per_kg_regime_eur": facts["price_per_kg_regime_eur"]},
            "hypothetical": {"assumptions": "PRODUCT.md §3; pipeline/fullload/params.yaml"},
        },
        "rationale": f"{low} of {n_lifts} lifts emptied a container under {LOW_FILL_PCT} % full.",
        "reversal": "No commitment: the customer can keep today's contract; a tender only invites bids.",
        "not_proven": ["Savings are simulated on synthetic data, not demonstrated"],
    }

    return {
        "customer_id": customer_id, "customer_name": cust[0], "sector": cust[1], "region": region,
        "devices": devices_out,
        "lifts": [{"date": r.date, "device_id": r.device_id,
                   "fill_pct": None if pd.isna(r.device_fill_pct_before) else round(float(r.device_fill_pct_before), 1),
                   "kg": None if pd.isna(r.device_estimated_collected_kg) else round(float(r.device_estimated_collected_kg)),
                   "trigger": r.original_trigger_type, "flagged": bool(r.flagged)} for r in lifts.itertuples()],
        "figures": {
            "lifts": fig(n_lifts, "count", "completed lifts of the customer's devices in the region"),
            "low_fill_share_pct": fig(facts["low_fill_share_pct"], "%", f"lifts with fill before lift < {LOW_FILL_PCT} % / lifts"),
            "flagged_lifts": fig(flagged, "count", "lifts flagged by the FullLoad premature-lift rule", tag="estimated"),
            "cost_today_eur": fig(facts["cost_today_eur"], "EUR", "trip- and tonne-driven invoice lines, 12 months"),
            "cost_per_t_today": fig(facts["cost_per_t_today_eur"], "EUR/t", "cost today / tonnes"),
            "cost_per_t_after": fig(facts["cost_per_t_after_eur"], "EUR/t", "market model price / tonnes", tag="simulated"),
            "saving_pct": fig(facts["saving_pct"], "%", "1 - per-kg price / cost today", tag="simulated"),
        },
        "facts": facts,
        "report": report,
        "proposal": proposal,
        "operator_view": {
            "devices": [{"device_id": r.device_id, "actual_t_per_month": round(float(r.actual), 2),
                         "own_forecast_t_per_month": round(float(r.own), 2),
                         "peer_forecast_t_per_month": round(float(r.peer), 2),
                         "own_error_pct": _pct(float(r.own_err)), "peer_error_pct": _pct(float(r.peer_err))}
                        for r in hb.itertuples()],
            "own_error_median_pct": _pct(float(hb.own_err.median())) if len(hb) else None,
            "peer_error_median_pct": _pct(float(hb.peer_err.median())) if len(hb) else None,
            "sigma_inc": market["sigma_inc"], "sigma_ent": market["sigma_ent"],
            "price_today_eur": facts["cost_today_eur"],
            "bids_before_eur": {o: round(b / 100) for o, b in sorted(row["bids_before"].items())},
            "bids_after_eur": {o: round(b / 100) for o, b in sorted(row["bids_after"].items())},
            "incumbent": row["incumbent"], "winner_after": row["winner_after"],
            "price_after_eur": facts["price_per_kg_regime_eur"],
        },
    }


# ------------------------------------------------------------------ AI-summarized report

_NUM = re.compile(r"(?<![\w-])(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?")


def _allowed(facts: dict) -> set[str]:
    out = {"12", "60", "3", "1", "0"}   # time window, the fill threshold, contract years, trivial counts
    for v in facts.values():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            for s in {f"{v}", f"{v:,}", f"{round(v)}", f"{round(v):,}", f"{v:.1f}", f"{v:,.1f}"}:
                out.add(s)
    return out


def report_numbers_ok(text: str, facts: dict) -> list[str]:
    """Numbers in the text that are not in the fact sheet (empty list = OK)."""
    allowed = _allowed(facts)
    body = re.sub(r"ORG-\d+|OP-[A-Z]|FI-\d+|CMP-\d+", "", text)
    return [n for n in _NUM.findall(body) if n not in allowed]


def load_report(customer_id: str, facts: dict) -> dict:
    path = REPORTS / f"{customer_id}.md"
    if not path.exists():
        return {"status": "missing", "text": None, "facts": facts}
    text = path.read_text(encoding="utf-8").strip()
    bad = report_numbers_ok(text, facts)
    return {"status": "checked" if not bad else "unchecked", "unmatched_numbers": bad, "text": text, "facts": facts,
            "label": "AI-summarized (Claude) from the figures on this page; every number checked against the data"}
