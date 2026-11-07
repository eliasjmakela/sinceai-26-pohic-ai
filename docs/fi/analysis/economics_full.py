"""Full value model per device/yr from the synthetic dataset (all € are synthetic)."""
import sys
import pandas as pd

D = sys.argv[1]
r = lambda p: pd.read_parquet(f"{D}/{p}.parquet")
dev, eco, ev = r("reference/devices"), r("labels_dev/reference_economics"), r("operations/collection_events")
an, oav, cl = r("labels_dev/anomaly_labels"), r("labels_dev/operator_action_values"), r("labels_dev/reference_charge_lines")
ctr = r("reference/contracts")
yrs = 304 / 365
n = eco.device_id.nunique()
per = lambda x: x / n / yrs

e = ev.merge(eco[["collection_id", "billing_mass_kg", "collection_cost_eur", "total_customer_cost_eur"]], on="collection_id", how="left")
e = e.merge(ctr[["device_id", "pricing_model_initial"]], on="device_id")
print("== Status counts per device/yr")
print((e.status.value_counts() / n / yrs).round(2).to_string())

# Charge lines by type
c = cl.merge(eco[["collection_id", "device_id"]], on="collection_id")
print("\n== Customer spend per device/yr by line type (€)")
print(per(c.groupby("line_type").amount_eur.sum()).round(0).sort_values(ascending=False).to_string())

# Shift to all-in per-tonne: lifts needed if every lift were as full as the device's own 'full' lifts
done = e[(e.status == "COMPLETED") & (e.billing_mass_kg > 0)]
full_kg = done[done.device_fill_pct_before >= 80].groupby("device_id").billing_mass_kg.median()
g = done.groupby("device_id").agg(t=("billing_mass_kg", "sum"), lifts=("collection_id", "count"),
                                  coll=("collection_cost_eur", "sum"), model=("pricing_model_initial", "first"))
g = g.join(full_kg.rename("full_kg")).dropna()
g["eff_lifts"] = (g.t / g.full_kg).clip(upper=g.lifts)
g["cost_per_lift"] = g.coll / g.lifts
g["saving"] = (g.lifts - g.eff_lifts) * g.cost_per_lift
print(f"\n== Fewer lifts at full loads: lifts -{1 - g.eff_lifts.sum()/g.lifts.sum():.1%}, "
      f"collection cost saving {g.saving.sum()/g.coll.sum():.1%} = {per(g.saving.sum()):.0f} €/device/yr")
print((g.groupby("model").saving.sum() / g.groupby("model").size() / yrs).round(0).rename("saving €/dev/yr by contract").to_string())

# Service-level breaches
sla_fam = ["DELAYED_COLLECTION", "MISSED_COLLECTION", "WASTED_TRIP", "SIDE_WASTE", "EMERGENCY_LIFT", "OVERFLOW"]
print("\n== Anomaly label families per device/yr (count, € at stake)")
fam = an.groupby("label_family").agg(cnt=("entity_id", "count"), eur=("value_at_stake_eur", "sum"))
print((fam.assign(cnt=per(fam.cnt), eur=per(fam.eur))).round(1).sort_values("eur", ascending=False).to_string())

# Tender / renegotiation value (Task C2)
best = oav.groupby("case_id").agg(v=("best_set_value_eur", "max"), cost=("annual_contract_cost_eur", "first"))
print(f"\n== Contract cases: {len(best)}, share with positive action {(best.v>0).mean():.0%}, "
      f"mean value {best.v.mean():.0f} € on annual cost {best.cost.mean():.0f} € ({best.v.sum()/best.cost.sum():.1%})")
