"""Compute every figure the OpenWeight demo shows and write it to backend/data/.

Inputs : the challenge's public synthetic dataset.
Logic  : the challenge's baselines (B1 contract calculator, B2 rules, B5 scorecard, C2 valuation rules) plus
         OpenWeight's weight rules. No figure in the app comes from a language model.
Labels : labels_dev/ only evaluates the rules and reproduces the 21 % / 9 % method. It never feeds a customer's figure.

The pipeline (`pipeline/`, `.venv/bin/fullload build`) is the source of truth for the market figures. Its
pipeline/out/bundle.json is read here directly, so this app and the pitch show the same numbers (MASTER.md section C).
Rebuild this app's data after rebuilding the bundle.
Demo customer: the team's hero account, ORG-0036, four weighed compactors in Uusimaa.
Run: .venv/bin/python app/backend/build_data.py
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from europress_data.evaluate import score_b

# The starter kit is reached only through the pipeline's bridge (CLAUDE.md, PRODUCT.md §7.2): same kit and data
# package as `fullload build` (FULLLOAD_KIT / FULLLOAD_DATA), so the app and the pitch read the same data.
from fullload.config import data_root
from fullload.kit import baseline

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PUB = data_root(None)
OUT = HERE / "data"

compute = baseline("b1_economic_calculator").compute
_b2 = baseline("b2_rules_anomaly")
collection_features, detect_collections, detect_invoices = _b2.collection_features, _b2.detect_collections, _b2.detect_invoices
scorecard = baseline("b5_operator_scorecard").scorecard

CHALLENGER = "OP-E"  # the team's simulated winner of this account's tender
AS_OF = pd.Timestamp("2026-09-30")
CYCLE_YEARS = 3  # the challenge lead: contracts are retendered about every three years
RESPONSE_HOURS = 48  # assumption: a real service reads the agreed response time from the customer's contract
QUERY_WINDOW_DAYS = 125  # C2 rules: invoices issued in the last 90 days; invoices come out about 35 days after service
WEIGHT_TOLERANCE = 0.033  # ECONOMIC_MODEL.md section 2b, the kit's example
FULL_FILL_PCT = 80  # pickup is ordered at this fill level (volume, fill sensor; SMART orders at ~80 % today). Weight varies by material, so it is not the target
UNDERFILL_SHARE = 0.50  # a pickup counts as far from full below this share of the usual load (best F1 on validation)
TRUCK_BIAS_KG = 100  # a truck is worth checking when compactors disagree with its tickets by this much, in the median
TRUCK_MIN_PICKUPS = 20

LINE_TEXT = {
    "LIFT_FEE": "Pickup fee", "TRANSPORT": "Transport", "REMOTE_SURCHARGE": "Remote surcharge", "FUEL_SURCHARGE": "Fuel surcharge",
    "MATERIAL_CREDIT": "Material credit", "RENTAL": "Container rental", "SIDE_WASTE_FEE": "Side-waste fee",
    "EMERGENCY_SURCHARGE": "Emergency surcharge", "HAUL_PER_TONNE": "Haulage per tonne", "HAUL_FEE": "Haulage per tonne", "PROCESSING_FEE": "Treatment per tonne",
    "CANCELLATION_FEE": "Cancellation fee", "WASTED_TRIP_FEE": "Wasted-trip fee", "CONTAMINATION_PENALTY": "Contamination charge",
    "REJECTION_FEE": "Rejection fee", "MIN_CHARGE_TOPUP": "Minimum charge", "PROCESSING": "Treatment per tonne",
}
VISIT_LINES = {"LIFT_FEE", "TRANSPORT", "REMOTE_SURCHARGE", "FUEL_SURCHARGE"}
SURCHARGE_LINES = {"SIDE_WASTE_FEE", "EMERGENCY_SURCHARGE"}
BILLING_TEXT = {
    "DUPLICATE_LINE": "Same charge billed twice", "WRONG_SURCHARGE": "Surcharge differs from the contract", "OUTDATED_TARIFF": "Price differs from the contract",
    "WEIGHT_BASIS_MISMATCH": "Billed tonnage differs from the weighing record", "UNMATCHED_LINE": "Invoice line has no matching pickup",
}
MATERIAL_TEXT = {"plastic_film": "Plastic film", "cardboard": "Cardboard", "mixed_waste": "Mixed waste", "biowaste": "Biowaste", "paper": "Paper", "mixed_plastic": "Mixed plastic"}


def r(path: str) -> pd.DataFrame:
    return pd.read_parquet(PUB / f"{path}.parquet")


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, np.ndarray)):
        return [clean(v) for v in o]
    if o is None or o is pd.NaT:
        return None
    if isinstance(o, (bool, np.bool_)):
        return bool(o)
    if isinstance(o, (int, np.integer)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        return None if not np.isfinite(o) else round(float(o), 3)
    if hasattr(o, "isoformat"):
        return o.isoformat()
    return o


def op_label(name: str) -> str:
    return name.replace(" (fictional)", "")


def site_label(name: str) -> str:
    return name.split(" (")[0].capitalize()


def money(v: float) -> str:
    return f"{'−' if v < 0 else ''}€{abs(v):,.2f}"


def next_end(start) -> pd.Timestamp:
    end = pd.Timestamp(start)
    while end <= AS_OF:
        end += pd.DateOffset(years=CYCLE_YEARS)
    return end


# ---- weight rules -------------------------------------------------------------------------------------------------
def typical_full_load(f: pd.DataFrame) -> pd.Series:
    done = f[f.status.isin(["COMPLETED", "PARTIAL"]) & f.device_mass_kg_before.notna()]
    return done.groupby("device_id").device_mass_kg_before.apply(lambda s: s[s >= s.median()].median())


def weight_rule_mask(f: pd.DataFrame, full: pd.Series, share: float = UNDERFILL_SHARE) -> pd.Series:
    legit = f.original_trigger_type.isin(["MAX_INTERVAL_RULE", "CUSTOMER_REQUEST_PRE_CLOSURE", "DECOMMISSION", "MIN_FREQUENCY_REQUIRED"])
    ratio = f.device_mass_kg_before / f.device_id.map(full)
    return f.status.eq("COMPLETED") & ratio.lt(share) & ~legit & ~f.at_min_frequency.astype(bool)


def evaluate_rules(f: pd.DataFrame, full: pd.Series, base_flags: pd.DataFrame) -> dict:
    labels = PUB / "labels_dev"
    add = pd.DataFrame({"entity_type": "collection", "entity_id": f.loc[weight_rule_mask(f, full), "collection_id"], "label_family": "PREMATURE_UNJUSTIFIED"})
    base = score_b(base_flags, labels, "validation")
    union = score_b(pd.concat([base_flags, add], ignore_index=True).drop_duplicates(), labels, "validation")
    keys = ["positives", "predicted", "precision", "recall", "f1", "explained_flagged_as_anomaly"]
    fam = "PREMATURE_UNJUSTIFIED"
    return {"family": fam, "split": "validation", "underfill_share": UNDERFILL_SHARE,
            "baseline": {k: base[fam][k] for k in keys} | {"macro_f1": base["macro_f1"]},
            "combined": {k: union[fam][k] for k in keys} | {"macro_f1": union["macro_f1"]}}


def truck_checks(f: pd.DataFrame, wb: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Compare compactor weight with single-load tickets. A truck whose tickets differ from many compactors
    in the same direction points at the truck's stored tare, not at any one compactor."""
    t = wb[["operator_job_ref", "ticket_id", "allocated_net_kg", "tare_method", "vehicle_id", "loads_on_vehicle"]].rename(columns={"allocated_net_kg": "net", "vehicle_id": "truck", "loads_on_vehicle": "loads"})
    w = f[f.status.eq("COMPLETED")].drop(columns=["loads_on_vehicle", "tare_method", "vehicle_id"], errors="ignore").merge(t, on="operator_job_ref")
    w = w[w.net.gt(200) & w.device_estimated_collected_kg.notna() & w.loads.eq(1) & (w.driver_reported_side_waste != True)].copy()
    w["diff_kg"] = w.device_estimated_collected_kg - w.net
    g = w.groupby("truck").agg(pickups=("diff_kg", "size"), median_diff_kg=("diff_kg", "median"), compactors=("device_id", "nunique"),
                               stored_share=("tare_method", lambda s: (s == "STORED").mean()), operator_id=("operator_id", "first"))
    flagged = g[(g.pickups >= TRUCK_MIN_PICKUPS) & (g.median_diff_kg.abs() >= TRUCK_BIAS_KG)].sort_values("median_diff_kg")
    # check the rule against the labels
    an = r("labels_dev/anomaly_labels")
    tare = set(an[(an.label_family == "WEIGHT_DISCREPANCY") & (an.explanation_code == "WEIGHBRIDGE_TARE_ERROR")].entity_id)
    labelled = w[w.collection_id.isin(an[an.label_family == "WEIGHT_DISCREPANCY"].entity_id)]
    hit = labelled[labelled.truck.isin(flagged.index)]
    stats = {"flagged_trucks": len(flagged), "trucks_checked": int((g.pickups >= TRUCK_MIN_PICKUPS).sum()),
             "labelled_on_flagged": len(hit), "tare_share_on_flagged": float(hit.collection_id.isin(tare).mean()) if len(hit) else None,
             "tare_share_elsewhere": float(labelled[~labelled.truck.isin(flagged.index)].collection_id.isin(tare).mean())}
    return w, flagged, stats


def bid_error_stats(dev: pd.DataFrame, b1: pd.DataFrame) -> dict:
    def stats(k: pd.DataFrame) -> dict:
        k = k[k.kg > 0].merge(dev[["device_id", "material_stream", "container_volume_m3", "equipment_class"]], on="device_id")
        k["date"] = pd.to_datetime(k.service_date)
        s = k.groupby("device_id").agg(kg=("kg", "mean"), mat=("material_stream", "first"), vol=("container_volume_m3", "first"), cls=("equipment_class", "first"))
        s["peer"] = s.groupby(["mat", "vol", "cls"]).kg.transform("median")
        half = k.date.min() + (k.date.max() - k.date.min()) / 2
        s["first_half"], s["second_half"] = k[k.date < half].groupby("device_id").kg.mean(), k[k.date >= half].groupby("device_id").kg.mean()
        s = s.dropna()
        blind, prof = (s.peer - s.kg) / s.kg, (s.first_half - s.second_half) / s.second_half
        return {"n_devices": len(s), "blind_median_abs": blind.abs().median(), "blind_p80_abs": blind.abs().quantile(.8),
                "profile_median_abs": prof.abs().median(), "profile_p80_abs": prof.abs().quantile(.8),
                "blind_ratio_p10": (s.kg / s.peer).quantile(.10), "blind_ratio_p90": (s.kg / s.peer).quantile(.90),
                "profile_ratio_p10": (s.second_half / s.first_half).quantile(.10), "profile_ratio_p90": (s.second_half / s.first_half).quantile(.90)}

    eco = r("labels_dev/reference_economics")
    eco = eco[eco.status == "COMPLETED"].rename(columns={"billing_mass_kg": "kg"})[["device_id", "service_date", "kg"]]
    done = b1[b1.status == "COMPLETED"].rename(columns={"mass_kg": "kg"})[["device_id", "service_date", "kg"]]
    return {"published_method": stats(eco), "full_year_customer_side": stats(done)}


# ---- one compactor ----------------------------------------------------------------------------------------------------
def device_view(d, ctx) -> dict:
    f, b1, b1l, wb, gr, il, inv, cv, ct, daily, full, flagged, inv_flags, sc_lookup = (ctx[k] for k in ("f", "b1", "b1l", "wb", "gr", "il", "inv", "cv", "ct", "daily", "full", "flagged", "inv_flags", "sc_lookup"))
    c = ct[ct.device_id == d.device_id].iloc[0]
    fd = f[f.device_id == d.device_id].sort_values("actual_at")
    bd = b1[b1.device_id == d.device_id]
    exp_lines = b1l[b1l.collection_id.isin(bd.collection_id)]
    invs = inv[inv.contract_id == c.contract_id]
    lines = il[il.invoice_id.isin(invs.invoice_id)]
    flags = inv_flags[inv_flags.entity_type == "invoice_line"].set_index("entity_id").label_family.to_dict()
    tix = wb[wb.operator_job_ref.isin(fd.operator_job_ref)].drop_duplicates("operator_job_ref").set_index("operator_job_ref")
    vers = cv[cv.contract_id == c.contract_id].sort_values("version_no")
    usual = float(full.get(d.device_id, np.nan))
    weighs = bool(d.has_weight_measurement)
    low_ids = {e.collection_id for e in fd.itertuples() if (d.device_id, str(e.actual_at)[:10]) in ctx["flagged_lifts"] or (d.device_id, str(e.scheduled_at)[:10]) in ctx["flagged_lifts"]}
    site = ctx["sites"].set_index("site_id").loc[d.site_id]
    rows, findings = [], []
    for e in fd.itertuples():
        b = bd[bd.collection_id == e.collection_id].iloc[0]
        ticket = tix.loc[e.operator_job_ref] if e.operator_job_ref in tix.index else None
        billed = lines[lines.operator_job_ref == e.operator_job_ref]
        ref_on_invoice = None
        if billed.empty and e.status in ("COMPLETED", "PARTIAL"):  # SCHEMA.md: about 1.2 % of job refs have typos
            same_day = lines[(lines.service_date.astype(str) == str(b.service_date)[:10]) & ~lines.operator_job_ref.isin(fd.operator_job_ref)]
            if not same_day.empty:
                billed, ref_on_invoice = same_day, same_day.operator_job_ref.iloc[0]
        ex = exp_lines[exp_lines.collection_id == e.collection_id]
        line_rows = []
        for lt in sorted(set(ex.line_type) | set(billed.line_type)):
            x, y = ex[ex.line_type == lt], billed[billed.line_type == lt]
            line_rows.append({"type": lt, "label": LINE_TEXT.get(lt, lt.replace("_", " ").capitalize()), "contract_eur": float(x.amount_eur.sum()) if len(x) else None,
                              "invoice_eur": float(y.amount_eur.sum()) if len(y) else None, "flags": [flags[i] for i in y.invoice_line_id if i in flags]})
        mass_before = None if pd.isna(e.device_mass_kg_before) else float(e.device_mass_kg_before)
        hours = None if pd.isna(e.order_placed_at) or pd.isna(e.actual_at) else (e.actual_at - e.order_placed_at).total_seconds() / 3600
        visit = float(ex[ex.line_type.isin(VISIT_LINES)].amount_eur.sum())
        surcharge = float(ex[ex.line_type.isin(SURCHARGE_LINES)].amount_eur.sum())
        rows.append({
            "id": e.collection_id, "job_ref": e.operator_job_ref, "date": str(b.service_date)[:10], "status": e.status, "trigger": e.original_trigger_type, "version": b.contract_version_id,
            "fill_pct": e.device_fill_pct_before, "mass_before_kg": mass_before, "compactor_kg": None if pd.isna(e.device_estimated_collected_kg) else float(e.device_estimated_collected_kg), "billed_kg": None if pd.isna(b.mass_kg) else float(b.mass_kg), "basis": b.mass_basis,
            "ticket_id": None if ticket is None else ticket.ticket_id, "ticket_kg": None if ticket is None else ticket.allocated_net_kg, "truck": None if ticket is None else ticket.vehicle_id, "grade": b.grade if isinstance(b.grade, str) else None,
            "cost_eur": float(sum(v for v in (b.collection_cost_eur, b.processing_cost_eur, b.penalties_eur) if pd.notna(v))), "credit_eur": 0.0 if pd.isna(b.material_credit_eur) else float(b.material_credit_eur), "penalty_eur": 0.0 if pd.isna(b.penalties_eur) else float(b.penalties_eur), "treatment_eur": 0.0 if pd.isna(b.processing_cost_eur) else float(b.processing_cost_eur),
            "visit_eur": visit, "surcharge_eur": surcharge, "hours_to_pickup": hours, "load_ratio": mass_before / usual if mass_before and np.isfinite(usual) else None, "lines": line_rows, "ref_on_invoice": ref_on_invoice,
        })
    done = [x for x in rows if x["status"] in ("COMPLETED", "PARTIAL")]
    full_lifts = [x for x in done if x["status"] == "COMPLETED"]
    site_name, material = site_label(site.site_name), MATERIAL_TEXT[d.material_stream]
    base = {"compactor": d.device_id, "site": site_name, "material": material}

    def add(**k):
        findings.append(base | k)

    for x in done:
        if x["id"] in low_ids and x["load_ratio"] is not None and x["load_ratio"] < 1:
            avoidable = x["visit_eur"] * max(0.0, 1 - x["load_ratio"])
            sensor = (x["fill_pct"] or 0) >= 80
            add(id=f"UF-{x['id']}", kind="FAR_FROM_FULL", date=x["date"], pickup=x["id"], eur=avoidable, trigger=x["trigger"], sensor_full=sensor,
                title="Fill sensor full, weight low" if sensor else "Picked up early",
                detail=f"{x['mass_before_kg']:,.0f} kg in the container, {x['load_ratio'] * 100:.0f} % of its usual {usual:,.0f} kg. Fill sensor: {x['fill_pct']:.0f} %.",
                calc=f"Pickup cost {money(x['visit_eur'])} × (1 − {min(x['load_ratio'], 1):.2f}) = {money(avoidable)}", cause="Sensor" if sensor else "Ordering", evidence="estimate")
        differing = [ln for ln in x["lines"] if abs((ln["invoice_eur"] or 0) - (ln["contract_eur"] or 0)) > 0.005 and not x["ref_on_invoice"]]
        if differing:
            over = sum((ln["invoice_eur"] or 0) - (ln["contract_eur"] or 0) for ln in differing)
            fam = next((fl for ln in differing for fl in ln["flags"]), None)
            add(id=f"BL-{x['id']}", kind="INVOICE", family=fam, lines=len(differing), date=x["date"], pickup=x["id"], eur=over, title=BILLING_TEXT.get(fam, "Invoice differs from the contract"),
                detail="; ".join(f"{ln['label']}: invoice {money(ln['invoice_eur'] or 0)}, contract {money(ln['contract_eur'] or 0)}" for ln in differing) + ("." if over >= 0 else ". In your favour."),
                calc=f"Invoice minus contract = {money(over)}", cause="Invoice", evidence="simulated")
        if x["surcharge_eur"] > 0 and x["hours_to_pickup"] and x["hours_to_pickup"] > RESPONSE_HOURS:
            add(id=f"LS-{x['id']}", kind="LATE_SURCHARGE", date=x["date"], pickup=x["id"], eur=x["surcharge_eur"], title="Overflow charge after late pickup",
                detail=f"Pickup {x['hours_to_pickup']:.0f} h after the order. Overflow charges: {money(x['surcharge_eur'])}.",
                calc=f"Surcharges on this pickup: {money(x['surcharge_eur'])}. Response time {x['hours_to_pickup']:.0f} h against {RESPONSE_HOURS} h.", cause="Response time", evidence="estimate")
        if x["ref_on_invoice"]:
            add(id=f"RF-{x['id']}", kind="REFERENCE", date=x["date"], pickup=x["id"], eur=None, title="Different job reference on invoice", detail=f"Invoice: {x['ref_on_invoice']}. Pickup: {x['job_ref']}. Matched by contract and date.", calc="Matched by contract and service date.", cause="Data entry", evidence="simulated")
        if x["grade"] in ("C", "R"):
            add(id=f"QA-{x['id']}", kind="WRONG_MATERIAL", date=x["date"], pickup=x["id"], eur=x["penalty_eur"] or None, title=f"Load graded {x['grade']}: wrong material", detail=(f"Charges added: {money(x['penalty_eur'])}." if x["penalty_eur"] else "Lower material value."), calc="Grade from the waste company's published assessment.", cause="Sorting on site", evidence="simulated")
    for x in rows:
        if x["status"] == "MISSED_BY_OPERATOR":
            add(id=f"MS-{x['id']}", kind="MISSED_VISIT", date=x["date"], pickup=x["id"], eur=None, title="Missed visit", detail="Marked as missed by the waste company. Not charged.", calc="Status in the order record.", cause="Waste company record", evidence="simulated")
    # invoice lines that match no pickup, even by contract and date: the contract expects nothing for them
    # (same rule as the pipeline's invoice_lines_vs_contract, so the app and the pitch agree)
    used = set(fd.operator_job_ref) | {x["ref_on_invoice"] for x in rows if x["ref_on_invoice"]}
    orphan = lines[~lines.operator_job_ref.isin(used) & lines.line_type.ne("RENTAL")]
    for (ref, day), g in orphan.groupby(["operator_job_ref", orphan.service_date.astype(str).str[:10]]):
        over = float(g.amount_eur.sum())
        if abs(over) < 0.005:
            continue
        add(id=f"UL-{ref}", kind="INVOICE", family="UNMATCHED_LINE", lines=len(g), date=day, pickup=None, eur=over, title=BILLING_TEXT["UNMATCHED_LINE"],
            detail="; ".join(f"{LINE_TEXT.get(t, t)}: invoice {money(a)}, contract {money(0)}" for t, a in zip(g.line_type, g.amount_eur)) + f". No pickup with job reference {ref}.",
            calc=f"Invoice minus contract = {money(over)}", cause="Invoice", evidence="simulated")

    # truck tare: per truck on this compactor, valued only where the customer pays per tonne
    haul = float(vers.iloc[-1].haul_fee_cents_per_t) / 100
    by_truck: dict[str, list] = {}
    for x in full_lifts:
        if x["truck"] in flagged.index and x["ticket_kg"] and x["compactor_kg"]:
            by_truck.setdefault(x["truck"], []).append(x)
    for truck, xs in by_truck.items():
        if len(xs) < 3:
            continue
        bias = float(flagged.loc[truck].median_diff_kg)
        eur = 0.0
        for x in xs:
            t = (x["ticket_kg"] or 0) / 1000
            if t > 0:
                per_t = haul + x["treatment_eur"] / t - x["credit_eur"] / t
                eur += -bias / 1000 * per_t
        add(id=f"TR-{d.device_id}-{truck}", kind="TRUCK_TARE", date=xs[-1]["date"], pickup=None, truck=truck, eur=eur, pickups=len(xs), bias_kg=bias, recent_eur=eur * sum(1 for x in xs if pd.Timestamp(x["date"]) >= AS_OF - pd.Timedelta(days=QUERY_WINDOW_DAYS)) / len(xs),
            title=f"Truck {truck}: tickets {'above' if bias < 0 else 'below'} compactor weights", detail=f"{abs(bias):,.0f} kg in the median across {int(flagged.loc[truck].compactors)} compactors, {len(xs)} of these pickups here. Likely cause: outdated truck tare.",
            calc=f"{len(xs)} pickups × {abs(bias):,.0f} kg × this contract's net price per tonne = {money(eur)}", cause="Truck tare", evidence="estimate")
    # compactor calibration: only when the difference survives without the flagged trucks
    clean_rows = [x for x in full_lifts if x["ticket_kg"] and x["compactor_kg"] and x["ticket_kg"] > 200 and x["truck"] not in flagged.index]
    if len(clean_rows) >= 10:
        rel = float(np.median([(x["compactor_kg"] - x["ticket_kg"]) / x["ticket_kg"] for x in clean_rows]))
        if abs(rel) > 0.05:
            add(id=f"CA-{d.device_id}", kind="CALIBRATION", date=clean_rows[-1]["date"], pickup=None, eur=None, title="Calibration check suggested", detail=f"Median difference from weighing tickets: {rel * 100:+.0f} %, across trucks.", calc=f"Median across {len(clean_rows)} pickups, tickets from trucks with no known difference.", cause="Compactor", evidence="estimate")
    # moisture: the lead's example, weight rising with no compaction and no pickup
    dd = daily[daily.device_id == d.device_id].sort_values("date").copy()
    dd["delta"] = dd.mass_kg_last_valid.diff()
    pickup_days = {x["date"] for x in done}
    wet = dd[(dd.compaction_cycles == 0) & (dd.delta >= 30) & ~dd.date.astype(str).isin(pickup_days)]
    if len(wet) >= 2:
        add(id=f"MO-{d.device_id}", kind="MOISTURE", date=str(wet.date.max()), pickup=None, eur=None, title="Weight increase without use", detail=f"+{wet.delta.sum():,.0f} kg over {len(wet)} days with no compaction.", calc="Days with a mass rise of 30 kg or more, no compaction and no pickup.", cause="Weather", evidence="estimate")
    findings.sort(key=lambda z: z["date"], reverse=True)

    months = {}
    for x in done:
        m = months.setdefault(x["date"][:7], {"month": x["date"][:7], "pickups": 0, "kg": 0.0, "cost": 0.0, "credit": 0.0})
        m["pickups"] += 1
        m["kg"] += x["billed_kg"] or 0
        m["cost"] += x["cost_eur"]
        m["credit"] += x["credit_eur"]
    rental = float(vers.iloc[-1].rental_cents_per_month) / 100
    monthly = []
    for k in sorted(months):
        m = months[k]
        m["rental"] = rental
        m["net"] = m["cost"] + rental - m["credit"]
        m["eur_per_t"] = m["net"] / (m["kg"] / 1000) if m["kg"] else None
        m["invoiced"] = float(invs[invs.billing_period == k].total_eur.sum())
        monthly.append(m)
    span = (pd.Timestamp(done[-1]["date"]) - pd.Timestamp(done[0]["date"])).days + 1 if len(done) > 1 else 365
    net = sum(m["net"] for m in monthly)
    kg_sum = sum(m["kg"] for m in monthly)
    rated = [x for x in done if x["hours_to_pickup"] is not None]
    end = next_end(c.contract_start)
    last = vers.iloc[-1]
    return {
        "id": d.device_id, "site": site_name, "municipality": site.municipality, "region_code": site.region_code, "material": material, "material_key": d.material_stream, "equipment_class": d.equipment_class, "container_m3": d.container_volume_m3,
        "weighs": weighs, "usual_full_kg": None if not np.isfinite(usual) else usual, "policy": d.collection_policy, "operator_id": c.operator_id, "operator": ctx["names"][c.operator_id], "contract_id": c.contract_id,
        "pricing_model": last.pricing_model, "contract_start": str(c.contract_start), "contract_end": str(end.date()), "months_left": round((end - AS_OF).days / 30.44, 1), "notice_days": int(c.notice_period_days), "notice_by": str((end - pd.Timedelta(days=int(c.notice_period_days))).date()),
        "versions": [{"id": v.contract_version_id, "from": str(v.effective_from), "reason": v.change_reason} for v in vers.itertuples()],
        "totals": {"span_days": span, "pickups": len(done), "kg": kg_sum, "cost": sum(m["cost"] + m["rental"] for m in monthly), "credit": sum(m["credit"] for m in monthly), "net": net, "invoiced": float(invs.total_eur.sum()), "eur_per_t": net / (kg_sum / 1000) if kg_sum else None, "annual_net": net * 365 / span,
                   "far_from_full": sum(1 for z in findings if z["kind"] == "FAR_FROM_FULL"), "far_from_full_eur": sum(z["eur"] for z in findings if z["kind"] == "FAR_FROM_FULL"), "within_response": sum(1 for x in rated if x["hours_to_pickup"] <= RESPONSE_HOURS), "rated": len(rated), "median_response_h": float(np.median([x["hours_to_pickup"] for x in rated])) if rated else None,
                   "missed": sum(1 for x in rows if x["status"] == "MISSED_BY_OPERATOR"), "tickets": sum(1 for x in done if x["ticket_id"]), "surcharge_eur": sum(x["surcharge_eur"] for x in done), "billed_above_eur": sum(z["eur"] for z in findings if z["kind"] == "INVOICE" and (z["eur"] or 0) > 0)},
        "monthly": monthly, "pickups": sorted(rows, key=lambda z: z["date"], reverse=True), "findings": findings,
    }


# ---- main -------------------------------------------------------------------------------------------------------------
def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "compactors").mkdir(parents=True)
    team = json.loads((REPO / "pipeline/out/bundle.json").read_text())
    hero, market = team["hero"], team["market"]
    facts, sv, ov = hero["facts"], hero["service_check"], hero["operator_view"]
    print("computing baselines ...", flush=True)
    b1, b1l = compute(PUB)
    f = collection_features(PUB, b1)
    inv_flags = detect_invoices(PUB, b1, b1l)
    coll_flags = detect_collections(f)
    sc = scorecard(PUB, b1, b1l)
    sc = sc.reset_index() if sc.index.names[0] else sc
    dv, ct, cv, sites, ops = r("reference/devices"), r("reference/contracts"), r("reference/contract_versions"), r("reference/sites"), r("reference/operators")
    regions = r("reference/regions")
    wb, qa, il, inv, daily = r("operations/weighbridge_tickets"), r("operations/quality_assessments"), r("finance/invoice_lines"), r("finance/invoices"), r("telemetry/telemetry_daily_summary")
    names = {o.operator_id: op_label(o.operator_name) for o in ops.itertuples()}
    region_names = regions.set_index("region_code").region_name.to_dict()
    full = typical_full_load(f)
    print("evaluating rules ...", flush=True)
    rule_eval = evaluate_rules(f, full, pd.concat([coll_flags, inv_flags], ignore_index=True))
    w, flagged, truck_stats = truck_checks(f, wb)
    ctx = {"f": f, "b1": b1, "b1l": b1l, "wb": wb, "gr": qa.set_index("ticket_id"), "il": il, "inv": inv, "cv": cv, "ct": ct, "daily": daily, "full": full, "flagged": flagged, "inv_flags": inv_flags, "sc_lookup": sc, "sites": sites, "names": names, "dv": dv, "region_names": region_names,
           "flagged_lifts": {(l["device_id"], l["date"]) for l in hero["lifts"] if l["flagged"]}}

    hero_ids = [d["device_id"] for d in hero["devices"]]
    hero_info = {d["device_id"]: d for d in hero["devices"]}
    forecast_info = {d["device_id"]: d for d in ov["devices"]}
    print("building the account ...", flush=True)
    views, findings = {}, []
    for d in dv[dv.device_id.isin(hero_ids)].itertuples():
        v = device_view(d, ctx)
        views[v["id"]] = v
        findings.extend(v["findings"])

    # fill bands on this account's own pickups: the visit costs about the same, so a half-empty one costs far more per tonne
    done = [x for v in views.values() for x in v["pickups"] if x["status"] == "COMPLETED" and x["compactor_kg"] and x["fill_pct"] is not None]
    bands = []
    for label, lo, hi in (("Under 60 % full", 0, 60), ("60–90 % full", 60, 90), ("90 % full or more", 90, 101)):
        xs = [x for x in done if lo <= x["fill_pct"] < hi]
        kg = sum(x["compactor_kg"] for x in xs)
        visit = sum(x["visit_eur"] + x["surcharge_eur"] for x in xs)
        bands.append({"label": label, "pickups": len(xs), "eur_per_pickup": visit / len(xs) if xs else None, "eur_per_t": visit / kg * 1000 if kg else None})

    compactors = []
    for i in hero_ids:
        v, t = views[i], views[i]["totals"]
        h = hero_info[i]
        compactors.append({k: v[k] for k in ("id", "site", "municipality", "material", "equipment_class", "container_m3", "operator", "operator_id", "contract_id", "contract_end", "months_left", "notice_by", "notice_days", "pricing_model", "policy")} | {
            "pickups": h["lifts"], "tonnes": h["tonnes"], "median_fill": h["median_fill_at_lift_pct"], "weight_pickups": h["weight_triggered_lifts"], "early": t["far_from_full"], "early_eur": t["far_from_full_eur"], "kinds": sorted({z["kind"] for z in v["findings"]})})
    compactors.sort(key=lambda c: c["months_left"])

    # right now: the weight in each container, and what the next pickup would cost before the truck leaves
    live = []
    for c_ in compactors:
        v = views[c_["id"]]
        t = daily[daily.device_id == c_["id"]].sort_values("date")
        cur, inc = t.iloc[-1], t.tail(30).fill_pct_last.diff()
        rate = float(inc[inc > 0].mean())  # fill points per day while filling
        fill = float(cur.fill_pct_last)
        usual = v["usual_full_kg"]
        recent = [x for x in v["pickups"] if x["status"] == "COMPLETED" and x["billed_kg"]][:8]
        tonnes = sum(x["billed_kg"] for x in recent) / 1000
        visit = float(np.median([x["visit_eur"] for x in recent]))
        per_t = (sum(x["treatment_eur"] for x in recent) - sum(x["credit_eur"] for x in recent)) / tonnes
        mass = float(cur.mass_kg_last_valid)
        cost_now, cost_full = visit + per_t * mass / 1000, visit + per_t * usual / 1000
        live.append({"id": c_["id"], "name": f"{c_['municipality']}, {c_['material'].lower()}", "mass_kg": mass, "usual_kg": usual, "fill_pct": fill, "full_fill_pct": FULL_FILL_PCT, "share_pct": fill, "days_to_full": max(0.0, (FULL_FILL_PCT - fill) / rate), "cost_now": cost_now, "cost_full": cost_full, "eur_t_now": cost_now / (mass / 1000) if mass > 50 else None, "eur_t_full": cost_full / (usual / 1000), "read_on": str(cur.date), "fill_per_day": rate, "trend": [{"date": str(q.date), "fill": None if pd.isna(q.fill_pct_last) else float(q.fill_pct_last), "kg": None if pd.isna(q.mass_kg_last_valid) else float(q.mass_kg_last_valid)} for q in t.tail(35).itertuples()], "pickups": c_["pickups"], "weight_pickups": c_["weight_pickups"], "tonnes": c_["tonnes"], "median_fill": c_["median_fill"], "equipment_class": c_["equipment_class"], "container_m3": c_["container_m3"], "pricing_model": c_["pricing_model"], "contract_end": c_["contract_end"], "notice_by": c_["notice_by"], "credit_eur": views[c_["id"]]["totals"]["credit"], "municipality": c_["municipality"], "material": c_["material"]})

    # response on the customer's own on-call orders: the SLA the challenge lead described
    orders = [x for v in views.values() for x in v["pickups"] if x["hours_to_pickup"] is not None and x["status"] in ("COMPLETED", "PARTIAL")]
    response = {"orders": len(orders), "within": sum(1 for x in orders if x["hours_to_pickup"] <= RESPONSE_HOURS), "median_h": float(np.median([x["hours_to_pickup"] for x in orders])), "longest_h": max(x["hours_to_pickup"] for x in orders), "hours": RESPONSE_HOURS}

    # by weight, per material: credits and the share going into recycling streams, for ESG reporting
    by_material: dict[str, dict] = {}
    for c_ in compactors:
        m_ = by_material.setdefault(c_["material"], {"material": c_["material"], "tonnes": 0.0, "credit_eur": 0.0, "recyclable": c_["material"] in ("Cardboard", "Plastic film", "Mixed plastic", "Paper", "Biowaste")})
        m_["tonnes"] += c_["tonnes"]
        m_["credit_eur"] += views[c_["id"]]["totals"]["credit"]
    for c_ in compactors:
        c_["credit_eur"] = views[c_["id"]]["totals"]["credit"]
    materials = sorted(by_material.values(), key=lambda z: -z["tonnes"])
    recycled_pct = sum(z["tonnes"] for z in materials if z["recyclable"]) / sum(z["tonnes"] for z in materials) * 100
    upcoming = sorted([c_ for c_ in compactors if pd.Timestamp(c_["notice_by"]) >= AS_OF], key=lambda z: z["notice_by"])
    next_notice = {"date": upcoming[0]["notice_by"], "name": f"{upcoming[0]['municipality']}, {upcoming[0]['material'].lower()}"} if upcoming else None

    # what to raise with the company: invoices that can still be queried, late overflow charges, truck tare
    query = {"operator": names[hero_ids and views[hero_ids[0]]["operator_id"]], "invoice_eur": 0.0, "surcharge_eur": 0.0, "tare_eur": 0.0, "total_eur": 0.0, "items": []}
    for z in findings:
        if z["kind"] not in ("INVOICE", "LATE_SURCHARGE", "TRUCK_TARE"):
            continue
        amount = z.get("recent_eur", z["eur"]) if z["kind"] == "TRUCK_TARE" else z["eur"]
        if not amount or amount <= 0:
            continue
        query["total_eur"] += amount
        query[{"INVOICE": "invoice_eur", "LATE_SURCHARGE": "surcharge_eur", "TRUCK_TARE": "tare_eur"}[z["kind"]]] += amount
        query["items"].append({k: z.get(k) for k in ("id", "kind", "compactor", "site", "material", "date", "title", "detail", "pickup")} | {"eur": amount})
    query["items"].sort(key=lambda i: -i["eur"])

    # invoices against the contract. Lines on a mistyped job reference are matched by contract and date first (SCHEMA.md),
    # so they don't count as differences. The team's bundle counts them, which is why its figure is higher.
    invoice_rows = [z for z in findings if z["kind"] == "INVOICE"]
    invoice_check = {"lines_total": sv["invoice_lines"], "lines_differing": sum(z["lines"] for z in invoice_rows), "above_eur": sum(z["eur"] for z in invoice_rows if z["eur"] > 0), "below_eur": -sum(z["eur"] for z in invoice_rows if z["eur"] < 0), "mistyped_refs": sum(1 for z in findings if z["kind"] == "REFERENCE"), "team_lines": sv["invoice_lines_differing"], "team_above_eur": sv["invoice_above_contract_eur"]}
    # the app and the pitch must tell the customer the same thing about its invoices
    assert invoice_check["lines_differing"] == sv["invoice_lines_differing"] and abs(invoice_check["above_eur"] - sv["invoice_above_contract_eur"]) < 0.01, \
        f"invoice check differs from the pipeline: {invoice_check} vs {sv['invoice_lines_differing']} / {sv['invoice_above_contract_eur']}"

    # the team's market model, read back for this account
    acc = next(a for a in market["inputs"] if a["customer_id"] == "ORG-0036")
    p = market["params"]
    trip, tonne, kg_year = acc["trip_cents"] / 100, acc["tonne_cents"] / 100, acc["kg"]
    t_year = kg_year / 1000
    today = trip + tonne
    fee_t = p["europress_fee_cents_per_t"] / 100
    sigma_after = (market["sigma_inc"] ** 2 + p["sigma_sensor"] ** 2) ** 0.5
    bid_after = ov["bids_after_eur"][CHALLENGER]
    base_after = (p["cost_share"] * (trip * acc["weight_lifts"] / acc["actual_lifts"] + tonne) + fee_t * t_year) * (1 + p["min_margin"]) * (1 + p["risk_z"] * sigma_after)
    rel = bid_after / base_after
    cost_per_pickup = p["cost_share"] * trip / acc["actual_lifts"] * rel
    cost_per_t = p["cost_share"] * tonne / t_year * rel + fee_t * rel - fee_t  # so the default reproduces the team's bid exactly

    # Every offer is one the customer received outside OpenWeight and uploaded to compare. OpenWeight never relays offers.
    # Quoted prices follow the market model: each bidder offers its own floor, and the winner prices at the runner-up's
    # bid (market.py), so the lowest offer is the pitch's best case (price_after_eur), not the winner's floor.
    quoted = {o: (ov["price_after_eur"] if o == ov["winner_after"] else v) for o, v in ov["bids_after_eur"].items()}
    received = {o: str((AS_OF - pd.Timedelta(days=d)).date()) for o, d in zip(sorted(quoted), (6, 4, 3, 1, 2, 5))}
    offers = [{"id": f"model-{o}", "uploaded": received[o], "operator_id": o, "operator": names.get(o, "New entrant"), "annual_eur": float(v), "price_eur_t": v / t_year, "model_winner": o == ov["winner_after"], "kind": "Current company" if o == ov["incumbent"] else ("New to the region" if o not in names else "Another company in the region")} for o, v in quoted.items()]
    cards = {}
    for op, g in sc[sc.region_code == hero["region"]].groupby("operator_id"):
        cards[op] = {"on_time_pct": float(g.on_time_rate.mean()) * 100, "missed_pct": float(g.missed_visit_rate.mean()) * 100, "tickets_pct": float(g.weighbridge_shared_7d_rate.mean()) * 100, "billed_above_pct": float(g.billing_overcharge_pct.mean()), "response_h": float(g.median_order_to_lift_hours.mean())}

    # forecast for the account: this year's shape, band from the team's backtest
    months_kg: dict[str, float] = {}
    for v in views.values():
        for m in v["monthly"]:
            months_kg[m["month"]] = months_kg.get(m["month"], 0.0) + m["kg"]
    avg = float(np.mean(list(months_kg.values())))
    by_cal = {int(k[5:7]): val for k, val in months_kg.items()}
    forecast = []
    for per in pd.period_range(AS_OF.to_period("M") + 1, periods=12, freq="M"):
        point = (by_cal.get(per.month, avg) + by_cal.get((per.month - 2) % 12 + 1, avg) + by_cal.get(per.month % 12 + 1, avg)) / 3
        forecast.append({"month": str(per), "p50_kg": point, "low_kg": point * (1 - market["sigma_inc"]), "high_kg": point * (1 + market["sigma_inc"])})

    pack_rows = []
    for c in compactors:
        kg_rows = [x["billed_kg"] for x in views[c["id"]]["pickups"] if x["status"] == "COMPLETED" and x["billed_kg"]]
        fi = forecast_info[c["id"]]
        pack_rows.append({"material": c["material"], "site": c["municipality"], "container_m3": c["container_m3"], "equipment_class": c["equipment_class"], "pickups": c["pickups"], "weight_pickups": c["weight_pickups"], "tonnes": c["tonnes"], "p10": float(np.percentile(kg_rows, 10)), "p50": float(np.percentile(kg_rows, 50)), "p90": float(np.percentile(kg_rows, 90)), "contract_end": c["contract_end"], "own_t_month": fi["own_forecast_t_per_month"], "peer_t_month": fi["peer_forecast_t_per_month"], "actual_t_month": fi["actual_t_per_month"]})
    own_year = sum(d["own_forecast_t_per_month"] for d in ov["devices"]) * 12
    peer_year = sum(d["peer_forecast_t_per_month"] for d in ov["devices"]) * 12
    pack = {
        "id": "T-0036", "region": region_names[hero["region"]], "compactors": len(pack_rows), "tonnes": t_year, "pickups_today": acc["actual_lifts"], "pickups_by_weight": acc["weight_lifts"], "offers_due": str((AS_OF + pd.Timedelta(days=30)).date()), "term_years": CYCLE_YEARS, "response_hours": RESPONSE_HOURS,
        "rows": pack_rows, "forecast": forecast, "sigma_blind_pct": market["sigma_ent"] * 100, "sigma_data_pct": sigma_after * 100, "sigma_own_pct": market["sigma_inc"] * 100,
        "range_blind": {"estimate": peer_year, "low": peer_year * (1 - market["sigma_ent"]), "high": peer_year * (1 + market["sigma_ent"])}, "range_data": {"estimate": own_year, "low": own_year * (1 - market["sigma_inc"]), "high": own_year * (1 + market["sigma_inc"])},
        "model": {"cost_per_pickup": round(cost_per_pickup, 2), "cost_per_t": round(cost_per_t, 2), "fee_t": fee_t, "margin_pct": p["min_margin"] * 100, "risk_z": p["risk_z"]}, "price_per_pack_eur": team["pricing"]["params"].get("package_eur", 500) if isinstance(team.get("pricing", {}).get("params"), dict) else 500,
    }
    notice = {"id": pack["id"], "uploaded": str((AS_OF - pd.Timedelta(days=8)).date()), "region": pack["region"], "compactors": pack["compactors"], "offers_due": pack["offers_due"], "term_years": pack["term_years"], "response_hours": RESPONSE_HOURS, "price_per_pack_eur": pack["price_per_pack_eur"], "asks": ["A net price per tonne", "Pickups ordered by weight", f"Response within {RESPONSE_HOURS} hours of an order", "Weighing tickets shared within 7 days", "The bill stays on your certified weighbridge"], "sigma_blind_pct": pack["sigma_blind_pct"], "sigma_data_pct": pack["sigma_data_pct"], "range_blind": pack["range_blind"], "materials": sorted({c["material"] for c in compactors}), "blind_price_t": ov["bids_before_eur"][CHALLENGER] / t_year}

    me_card = {}
    allc = []
    for op, g in sc.groupby("operator_id"):
        allc.append({"operator_id": op, "on_time_pct": float(g.on_time_rate.mean()) * 100, "missed_pct": float(g.missed_visit_rate.mean()) * 100, "tickets_pct": float(g.weighbridge_shared_7d_rate.mean()) * 100, "billed_above_pct": float(g.billing_overcharge_pct.mean())})
    me_card = next(c for c in allc if c["operator_id"] == CHALLENGER)
    others = {k: float(np.mean([c[k] for c in allc if c["operator_id"] != CHALLENGER])) for k in me_card if k != "operator_id"}

    # the challenger's own compactors
    own = dv[(dv.operator_id == CHALLENGER) & dv.has_weight_measurement]
    site_ix = sites.set_index("site_id")
    fleet = []
    for x in own.itertuples():
        t = daily[daily.device_id == x.device_id].sort_values("date")
        if not len(t):
            continue
        cur, inc = t.iloc[-1], t.tail(30).fill_pct_last.diff()
        rate = float(inc[inc > 0].mean()) if (inc > 0).any() else 0.0
        cap = float(full.get(x.device_id, np.nan))
        mass = None if pd.isna(cur.mass_kg_last_valid) else float(cur.mass_kg_last_valid)
        if mass is None or pd.isna(cur.fill_pct_last) or not np.isfinite(cap) or rate <= 0:
            continue
        fill = float(cur.fill_pct_last)
        s = site_ix.loc[x.site_id]
        fleet.append({"id": x.device_id, "site": site_label(s.site_name), "region": region_names[s.region_code], "material": MATERIAL_TEXT[x.material_stream], "container_m3": x.container_volume_m3, "mass_kg": mass, "full_kg": cap, "fill_pct": fill, "days_to_full": max(0.0, (FULL_FILL_PCT - fill) / rate)})
    fleet.sort(key=lambda z: z["days_to_full"])
    unweighed = dv[(dv.operator_id == CHALLENGER) & ~dv.has_weight_measurement]
    not_weighing = {"compactors": len(unweighed), "sites": int(unweighed.site_id.nunique()), "customers": int(unweighed.customer_id.nunique())}
    my_flagged = flagged[flagged.operator_id == CHALLENGER]
    my_rows = w[w.truck.isin(my_flagged.index)].sort_values("actual_at", ascending=False)
    trucks = []
    for truck, row in my_flagged.iterrows():
        rows = my_rows[my_rows.truck == truck].head(5)
        trucks.append({"truck": truck, "pickups": int(row.pickups), "compactors": int(row.compactors), "median_diff_kg": float(row.median_diff_kg), "stored_tare_pct": float(row.stored_share) * 100,
                       "recent": [{"date": str(q.actual_at)[:10], "compactor": q.device_id, "ticket_id": q.ticket_id, "ticket_kg": q.net, "compactor_kg": q.device_estimated_collected_kg, "diff_kg": q.diff_kg} for q in rows.itertuples()]})
    mine = w[w.operator_id == CHALLENGER]
    rel_diff = (mine.diff_kg / mine.net).abs()
    mine_f = f[f.operator_id == CHALLENGER]
    mine_low = mine_f[weight_rule_mask(mine_f, full)]
    visit_cost = b1l[b1l.line_type.isin(VISIT_LINES)].groupby("collection_id").amount_eur.sum()
    mine_done = mine_f[mine_f.status.eq("COMPLETED")]
    efficiency = {"pickups": len(mine_done), "early": len(mine_low), "share_pct": float(len(mine_low) / max(1, len(mine_done)) * 100), "visit_eur": float(mine_low.collection_id.map(visit_cost).fillna(0).sum())}
    hauler = {"as_of": str(AS_OF.date()), "operator": {"id": CHALLENGER, "name": names[CHALLENGER]}, "fleet": fleet, "trucks": trucks, "weight_stats": {"pickups": len(mine), "within_pct": float((rel_diff <= WEIGHT_TOLERANCE).mean()) * 100, "within10_pct": float((rel_diff <= 0.10).mean()) * 100, "median_pct": float(rel_diff.median()) * 100}, "record": {"me": me_card, "others": others}, "efficiency": efficiency, "not_weighing": not_weighing}

    weighed_not = dv[(dv.customer_id == "ORG-0036") & (dv.operator_id == ov["incumbent"]) & ~dv.has_weight_measurement & dv.site_id.isin(sites[sites.region_code == hero["region"]].site_id)]
    customer = {
        "as_of": str(AS_OF.date()), "name": facts["customer_name"], "region": region_names[hero["region"]], "response_hours": RESPONSE_HOURS,
        "facts": facts, "service": sv, "operator": names[ov["incumbent"]], "operator_id": ov["incumbent"], "bands": bands, "compactors": compactors, "not_weighed": len(weighed_not), "query": query, "invoice_check": invoice_check, "scatter": hero["lifts"], "live": live, "response": response, "materials": materials, "recycled_pct": recycled_pct, "credits_eur": sum(z["credit_eur"] for z in materials), "next_notice": next_notice,
        "findings": sorted([z for z in findings if z["kind"] in ("FAR_FROM_FULL", "INVOICE", "LATE_SURCHARGE", "TRUCK_TARE", "MISSED_VISIT", "REFERENCE", "WRONG_MATERIAL", "CALIBRATION", "MOISTURE")], key=lambda z: z["date"], reverse=True), "early_eur": float(sum(z["eur"] for z in findings if z["kind"] == "FAR_FROM_FULL")),
        "market": {"today_eur": facts["cost_today_eur"], "tonnes": t_year, "price_after_eur": facts["price_per_kg_regime_eur"], "saving_eur": facts["saving_eur"], "saving_pct": facts["saving_pct"], "region_saving_pct": (1 - market["headline"]["cost_per_t_after"]["value"] / market["headline"]["cost_per_t_before"]["value"]) * 100, "contestable_before": market["headline"]["contestable_before"]["value"], "contestable_after": market["headline"]["contestable_after"]["value"], "accounts": market["headline"]["contestable_after"]["value"], "today_price_t": today / t_year, "sigma_blind_pct": market["sigma_ent"] * 100, "sigma_data_pct": sigma_after * 100},
        "offers": offers, "cards": cards, "challenger": {"id": CHALLENGER, "name": names[CHALLENGER]}, "offers_due": pack["offers_due"], "term_years": CYCLE_YEARS, "c2_note": None, "truck_stats": truck_stats,
    }
    # the core value in four facts, for the sign-in page; all from the pipeline's bundle (market and pricing)
    pr = team["pricing"]
    about = {"region": market["region"], "region_saving_pct": customer["market"]["region_saving_pct"],
             "sigma_blind_pct": customer["market"]["sigma_blind_pct"], "sigma_data_pct": customer["market"]["sigma_data_pct"],
             "contestable_before": customer["market"]["contestable_before"], "contestable_after": customer["market"]["contestable_after"],
             "accounts": customer["market"]["accounts"], "fee_eur_per_device_month": pr["recommended_fee_eur_per_month"]}
    for name, obj in [("customer", customer), ("hauler", hauler), ("pack", pack), ("notice", notice), ("about", about)]:
        (OUT / f"{name}.json").write_text(json.dumps(clean(obj), ensure_ascii=False))
    for k, v in views.items():
        (OUT / "compactors" / f"{k}.json").write_text(json.dumps(clean(v), ensure_ascii=False))
    print(json.dumps(clean({"rule_eval": rule_eval, "bands": bands, "query": {k: query[k] for k in ("total_eur", "invoice_eur", "surcharge_eur", "tare_eur")}, "n_q": len(query["items"]), "lines": sum(z.get("lines", 0) for z in findings if z["kind"] == "INVOICE"), "early_eur": customer["early_eur"], "market": customer["market"], "offers": offers, "cards": cards, "model": pack["model"], "ranges": [pack["range_blind"], pack["range_data"]], "rows": pack_rows, "compactors": [(c["id"], c["municipality"], c["material"], c["pricing_model"], c["contract_end"], c["months_left"], c["notice_by"], c["early"], c["kinds"]) for c in compactors], "fleet": len(fleet), "full3": sum(1 for x in fleet if x["days_to_full"] <= 3), "trucks": [(t["truck"], t["pickups"], t["median_diff_kg"]) for t in trucks], "weight": hauler["weight_stats"], "eff": efficiency, "me": me_card, "others": others, "not_weighed": customer["not_weighed"], "truck_stats": truck_stats, "kinds": pd.Series([z["kind"] for z in findings]).value_counts().to_dict(), "price_check": (cost_per_pickup, cost_per_t)}), ensure_ascii=False))


if __name__ == "__main__":
    main()
