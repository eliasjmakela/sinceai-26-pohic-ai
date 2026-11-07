"""Beat 0 — "Paid per trip": fleet-level facts (PRODUCT.md §4).

Answers: how much of what customers pay is driven by trips rather than tonnes, and how full containers
are when they are emptied.
"""
from __future__ import annotations

import duckdb
import pandas as pd

from .config import EXCLUDED_MATERIALS
from .figures import Figure, eur_from_cents

# Invoice line types whose amount scales with the number of trips (definition, not a hypothesis).
# FUEL_SURCHARGE is a percentage on transport, so it scales with trips too.
TRIP_LINES = ("LIFT_FEE", "TRANSPORT", "FUEL_SURCHARGE", "EMERGENCY_SURCHARGE", "REMOTE_SURCHARGE",
              "WASTED_TRIP_FEE", "CANCELLATION_FEE")
TONNE_LINES = ("PROCESSING", "HAUL_PER_TONNE")
CREDIT_LINES = ("MATERIAL_CREDIT",)
LOW_FILL_PCT = 60
FULL_FILL_PCT = 90


def sql_in(values: tuple[str, ...]) -> str:
    """SQL list literal for constant tuples defined in this package (never for user input)."""
    return "(" + ", ".join(f"'{v}'" for v in values) + ")"


def device_charges(con: duckdb.DuckDBPyConnection, region: str | None = None,
                   exclude: tuple[str, ...] = EXCLUDED_MATERIALS) -> pd.DataFrame:
    """Trip- and tonne-driven invoice charges per device over the whole period, in integer cents.

    Invoice lines reach a device through invoices.contract_id -> contracts.device_id (one contract per device).
    """
    where = [f"d.material_stream NOT IN {sql_in(exclude)}"] if exclude else []
    params: list = []
    if region is not None:
        where.append("s.region_code = ?")
        params.append(region)
    df = con.execute(f"""
        SELECT k.device_id, d.customer_id, d.operator_id, d.material_stream, s.region_code,
               sum(round(l.amount_eur * 100)) FILTER (WHERE l.line_type IN {sql_in(TRIP_LINES)}) AS trip_cents,
               sum(round(l.amount_eur * 100)) FILTER (WHERE l.line_type IN {sql_in(TONNE_LINES)}) AS tonne_cents
        FROM invoice_lines l JOIN invoices i USING (invoice_id) JOIN contracts k ON k.contract_id = i.contract_id
        JOIN devices d ON d.device_id = k.device_id JOIN sites s ON s.site_id = d.site_id
        {"WHERE " + " AND ".join(where) if where else ""}
        GROUP BY ALL ORDER BY k.device_id""", params).df()
    df[["trip_cents", "tonne_cents"]] = df[["trip_cents", "tonne_cents"]].fillna(0).astype("int64")
    return df


def visit_cost_by_fill(con: duckdb.DuckDBPyConnection, exclude: tuple[str, ...] = EXCLUDED_MATERIALS) -> list[dict]:
    """Per-visit charges vs per-tonne cost, by how full the compactor was at the lift (screen 1).

    Invoice lines join to lifts by operator_job_ref. Per band: median per-visit charge (TRIP_LINES), median kg
    collected, and per-visit charges divided by the tonnes collected (EUR per tonne). Completed lifts with a
    device weight only; excluded materials left out.
    """
    rows = con.execute(f"""
        WITH j AS (SELECT operator_job_ref, sum(round(amount_eur * 100)) AS trip_cents
                   FROM invoice_lines WHERE line_type IN {sql_in(TRIP_LINES)} GROUP BY 1)
        SELECT CASE WHEN c.device_fill_pct_before < {LOW_FILL_PCT} THEN 0
                    WHEN c.device_fill_pct_before < {FULL_FILL_PCT} THEN 1 ELSE 2 END AS band,
               count(*), median(j.trip_cents), median(c.device_estimated_collected_kg),
               sum(j.trip_cents), sum(c.device_estimated_collected_kg)
        FROM collection_events c JOIN j USING (operator_job_ref) JOIN devices d USING (device_id)
        WHERE c.status = 'COMPLETED' AND c.device_fill_pct_before IS NOT NULL AND c.device_estimated_collected_kg > 0
          AND d.material_stream NOT IN {sql_in(exclude)}
        GROUP BY 1 ORDER BY 1""").fetchall()
    labels = (f"under {LOW_FILL_PCT} % full", f"{LOW_FILL_PCT}–{FULL_FILL_PCT} % full", f"{FULL_FILL_PCT} % full or more")
    src = ("invoice_lines.line_type", "invoice_lines.amount_eur", "invoice_lines.operator_job_ref",
           "collection_events.device_fill_pct_before", "collection_events.device_estimated_collected_kg")
    total = sum(r[1] for r in rows)
    out = []
    for band, n, med_cents, med_kg, cents, kg in rows:
        out.append({
            "band": labels[band], "lifts": int(n), "share_pct": round(100 * n / total, 1),
            "visit_eur": Figure(round(med_cents / 100), "EUR", "observed", "median per-visit charges per lift (TRIP_LINES)",
                                src).to_dict(),
            "kg": Figure(round(med_kg), "kg", "estimated", "median device-estimated kg collected per lift", src).to_dict(),
            "eur_per_t": Figure(round(cents / kg * 10, 1), "EUR/t", "estimated",
                                "sum(per-visit charges) / sum(kg collected) x 1000, this band", src,
                                assumptions=("Charges are observed invoices; tonnes are the device-side estimate",)).to_dict(),
        })
    return out


def fleet_facts(con: duckdb.DuckDBPyConnection) -> dict:
    n_devices, n_weighing = con.execute(
        "SELECT count(*), count(*) FILTER (WHERE has_weight_measurement) FROM devices").fetchone()

    # Money in integer cents (amount_eur is a float column in the kit's invoice_lines).
    gross, trip, tonne = con.execute(f"""
        SELECT sum(round(amount_eur * 100)) FILTER (WHERE line_type NOT IN {sql_in(CREDIT_LINES)}),
               sum(round(amount_eur * 100)) FILTER (WHERE line_type IN {sql_in(TRIP_LINES)}),
               sum(round(amount_eur * 100)) FILTER (WHERE line_type IN {sql_in(TONNE_LINES)})
        FROM invoice_lines""").fetchone()
    gross, trip, tonne = int(gross), int(trip), int(tonne)

    lifts, low_fill, tonnes = con.execute(f"""
        SELECT count(*) FILTER (WHERE device_fill_pct_before IS NOT NULL),
               count(*) FILTER (WHERE device_fill_pct_before < {LOW_FILL_PCT}),
               sum(device_estimated_collected_kg) / 1000.0
        FROM collection_events WHERE status = 'COMPLETED'""").fetchone()

    hist = con.execute("""
        SELECT least(floor(device_fill_pct_before / 10) * 10, 90)::INT AS bin, count(*) AS n
        FROM collection_events WHERE status = 'COMPLETED' AND device_fill_pct_before IS NOT NULL
        GROUP BY 1 ORDER BY 1""").fetchall()

    by_trigger = con.execute("""
        SELECT trigger_type, count(*) AS n, round(median(device_fill_pct_before), 1) AS median_fill_pct
        FROM collection_events WHERE status = 'COMPLETED' AND device_fill_pct_before IS NOT NULL
        GROUP BY 1 ORDER BY n DESC, trigger_type""").fetchall()

    lines_src = ("invoice_lines.line_type", "invoice_lines.amount_eur")
    fill_src = ("collection_events.status", "collection_events.device_fill_pct_before")
    return {
        "devices": Figure(n_devices, "count", "observed", "count(devices)", ("devices.device_id",)).to_dict(),
        "devices_with_weighing": Figure(n_weighing, "count", "observed", "count(devices where has_weight_measurement)",
                                        ("devices.has_weight_measurement",)).to_dict(),
        "gross_charges_eur": Figure(eur_from_cents(gross), "EUR", "observed",
                                    "sum(amount_eur) over all invoice lines except MATERIAL_CREDIT", lines_src).to_dict(),
        "trip_charges_eur": Figure(eur_from_cents(trip), "EUR", "observed",
                                   f"sum(amount_eur) where line_type in {list(TRIP_LINES)}", lines_src).to_dict(),
        "trip_share_pct": Figure(round(100 * trip / gross, 1), "%", "observed", "trip_charges / gross_charges",
                                 lines_src).to_dict(),
        "tonne_charges_eur": Figure(eur_from_cents(tonne), "EUR", "observed",
                                    f"sum(amount_eur) where line_type in {list(TONNE_LINES)}", lines_src).to_dict(),
        "tonnes_per_year": Figure(round(tonnes, 1), "t", "estimated",
                                  "sum(device_estimated_collected_kg) / 1000 over completed lifts",
                                  ("collection_events.device_estimated_collected_kg",),
                                  assumptions=("Device-side estimate; lifts without a device weight are not counted",)).to_dict(),
        "low_fill_lift_share_pct": Figure(round(100 * low_fill / lifts, 1), "%", "observed",
                                          f"completed lifts with fill before lift < {LOW_FILL_PCT} % / completed lifts with a fill reading",
                                          fill_src).to_dict(),
        "fill_at_lift_histogram": [{"bin_pct": b, "lifts": n} for b, n in hist],
        "fill_by_trigger": [{"trigger_type": t, "lifts": n, "median_fill_pct": m} for t, n, m in by_trigger],
        "visit_cost_by_fill": visit_cost_by_fill(con),
    }
