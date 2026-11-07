"""Operator x region x month service figures (Task B2), from public tables only. Feeds the market simulation.

These are the records a customer (or Europress, with FullLoad) can see without the operator's books:
  jobs                    collection_events with status COMPLETED, PARTIAL, MISSED_BY_OPERATOR or WASTED_TRIP
                          (month = local month of scheduled_at)
  tonnes_per_lift         sum(device_estimated_collected_kg) / lifts with a device weight, in t (device estimate)
  on_time_share           completed/partial lifts with |actual_at - scheduled_at| <= 2 h
  missed_visit_share      MISSED_BY_OPERATOR / jobs
  ticket_share            completed/partial lifts whose weighbridge ticket was shared within 7 days of weighing
  ticket_lag_days_median  median days from weighing (arrival_at) to sharing (published_at), shared tickets
  discrepant_line_share   invoice lines (not RENTAL; month = billing_period) whose amount differs by more than one
                          cent from the contract-expected amount for that job and line type (kit B1 calculator);
                          a repeated (job, line type) is expected at 0
Column names map 1:1 to the kit's Task B2 metrics (see `KIT_METRIC`) so validate.py can score them.

Every figure is a difference or a share, not a verdict. Many have causes other than the operator: a late lift can
follow blocked access or a customer reschedule, a missed visit a site closure, an unshared ticket a data-sharing
agreement that was never set up, and an invoice difference an outdated tariff on either side or a calculator gap.
"""
from __future__ import annotations

import functools
from pathlib import Path

import duckdb
import pandas as pd

from .figures import Figure
from .kit import baseline

KEY = ["operator_id", "region_code", "month"]
ON_TIME_HOURS = 2          # same window as the kit's Task B2 definition
SHARED_WITHIN_DAYS = 7     # same window as the kit's Task B2 definition
KIT_METRIC = {"on_time_share": "on_time_rate", "missed_visit_share": "missed_visit_rate",
              "ticket_share": "weighbridge_shared_7d_rate", "ticket_lag_days_median": "median_share_lag_days",
              "discrepant_line_share": "discrepant_line_rate"}
METRICS = ("tonnes_per_lift", "on_time_share", "missed_visit_share", "ticket_share", "ticket_lag_days_median",
           "discrepant_line_share")

DEFINITIONS = {
    "jobs": "Jobs the operator was asked to do in the month: completed, partial, missed by operator, wasted trip.",
    "tonnes_per_lift": "Device-estimated tonnes per completed lift that has a device weight (estimate, not a "
                       "weighbridge figure). Low values can come from early lifts the customer ordered.",
    "on_time_share": f"Share of completed lifts done within {ON_TIME_HOURS} h of the scheduled time. Late lifts can "
                     "have causes outside the operator (blocked access, weather, customer reschedules).",
    "missed_visit_share": "Share of jobs recorded as missed by the operator. A site closure or access problem can "
                          "be recorded the same way.",
    "ticket_share": f"Share of completed lifts whose weighbridge ticket was shared with the customer within "
                    f"{SHARED_WITHIN_DAYS} days. Depends on the data-sharing agreement, not only on the operator.",
    "ticket_lag_days_median": "Median days from weighing to sharing, over shared tickets. Tickets shared after the "
                              "data extraction are not visible, so the lag is a lower bound.",
    "discrepant_line_share": "Share of invoice lines whose amount differs from the contract-expected amount by more "
                             "than one cent. A difference is not an error by itself: tariff versions, mass basis and "
                             "calculator gaps also cause differences.",
}
SOURCES = ("collection_events.status", "collection_events.scheduled_at", "collection_events.actual_at",
           "collection_events.device_estimated_collected_kg", "weighbridge_tickets.arrival_at",
           "weighbridge_tickets.published_at", "invoice_lines.amount_eur", "invoices.billing_period",
           "sites.region_code", "contract_versions (via kit B1 calculator)")


@functools.cache
def _expected_lines(root: Path) -> pd.DataFrame:
    """Contract-expected charges per job and line type from the kit's B1 calculator (integer cents)."""
    _, lines = baseline("b1_economic_calculator").compute(root)
    exp = lines.groupby(["operator_job_ref", "line_type"], as_index=False).amount_eur.sum()
    exp["exp_cents"] = (exp.amount_eur * 100).round().astype("int64")
    return exp[["operator_job_ref", "line_type", "exp_cents"]]


def _service(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return con.execute(f"""
        WITH jobs AS (
            SELECT c.*, s.region_code, strftime(timezone('Europe/Helsinki', c.scheduled_at), '%Y-%m') AS month
            FROM collection_events c JOIN sites s USING (site_id)
            WHERE c.status IN ('COMPLETED', 'PARTIAL', 'MISSED_BY_OPERATOR', 'WASTED_TRIP')),
        tickets AS (
            SELECT operator_job_ref, min(arrival_at) AS arrival_at, min(published_at) AS published_at
            FROM weighbridge_tickets GROUP BY 1),
        j AS (
            SELECT jobs.*, epoch(t.published_at - t.arrival_at) / 86400 AS lag_days,
                   status IN ('COMPLETED', 'PARTIAL') AS lift
            FROM jobs LEFT JOIN tickets t USING (operator_job_ref))
        SELECT operator_id, region_code, month,
               count(*) AS jobs,
               sum(device_estimated_collected_kg) FILTER (WHERE lift) / 1000.0
                   / nullif(count(device_estimated_collected_kg) FILTER (WHERE lift), 0) AS tonnes_per_lift,
               avg(CASE WHEN abs(epoch(actual_at - scheduled_at)) <= {ON_TIME_HOURS} * 3600 THEN 1.0 ELSE 0.0 END)
                   FILTER (WHERE lift) AS on_time_share,
               avg(CASE WHEN status = 'MISSED_BY_OPERATOR' THEN 1.0 ELSE 0.0 END) AS missed_visit_share,
               avg(CASE WHEN lag_days <= {SHARED_WITHIN_DAYS} THEN 1.0 ELSE 0.0 END) FILTER (WHERE lift) AS ticket_share,
               median(lag_days) FILTER (WHERE lift) AS ticket_lag_days_median
        FROM j GROUP BY ALL""").df()


def _billing(con: duckdb.DuckDBPyConnection, root: Path) -> pd.DataFrame:
    il = con.execute("""
        SELECT l.invoice_id, l.line_no, l.operator_job_ref, l.line_type,
               CAST(round(l.amount_eur * 100) AS BIGINT) AS cents,
               i.operator_id, s.region_code, i.billing_period AS month
        FROM invoice_lines l JOIN invoices i USING (invoice_id)
        JOIN contracts k ON k.contract_id = i.contract_id JOIN sites s ON s.site_id = k.site_id
        WHERE l.line_type <> 'RENTAL'
        ORDER BY l.invoice_id, l.line_no""").df()
    il = il.merge(_expected_lines(root), on=["operator_job_ref", "line_type"], how="left")
    il["exp_cents"] = il.exp_cents.fillna(0).astype("int64")
    il.loc[il.duplicated(["operator_job_ref", "line_type"], keep="first"), "exp_cents"] = 0
    il["discrepant"] = (il.cents - il.exp_cents).abs() > 0
    return il.groupby(KEY, as_index=False).agg(discrepant_line_share=("discrepant", "mean"))


def scorecard(con: duckdb.DuckDBPyConnection, root: Path) -> pd.DataFrame:
    """One row per operator x region x month; NaN where a figure cannot be computed. Sorted by KEY."""
    df = _service(con).merge(_billing(con, root), on=KEY, how="outer")
    df["jobs"] = df.jobs.fillna(0).astype("int64")
    return df.sort_values(KEY, ignore_index=True)[KEY + ["jobs", *METRICS]]


def _num(v, nd: int = 4):
    return None if pd.isna(v) else round(float(v), nd)


def scorecard_facts(con: duckdb.DuckDBPyConnection, root: Path) -> dict:
    df = scorecard(con, root)
    rows = [{**{k: getattr(r, k) for k in KEY}, "jobs": int(r.jobs), **{m: _num(getattr(r, m)) for m in METRICS}}
            for r in df.itertuples()]
    lifts_t = df.tonnes_per_lift.dropna()
    return {
        "rows": rows,
        "definitions": DEFINITIONS,
        "rows_count": Figure(len(rows), "count", "observed", "count of operator x region x month rows",
                             SOURCES).to_dict(),
        "tonnes_per_lift_median": Figure(_num(lifts_t.median(), 3) if len(lifts_t) else None, "t", "estimated",
                                         "median over rows of tonnes_per_lift", SOURCES,
                                         assumptions=("Device-side estimate of collected mass",)).to_dict(),
    }
