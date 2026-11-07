"""Value pools per device per year from the synthetic competition dataset."""
import sys
import numpy as np
import pandas as pd

D = sys.argv[1]
r = lambda p: pd.read_parquet(f"{D}/{p}.parquet")
dev = r("reference/devices")
eco = r("labels_dev/reference_economics")
ev = r("operations/collection_events")
an = r("labels_dev/anomaly_labels")
oav = r("labels_dev/operator_action_values")
cv = r("reference/contract_versions")

days = (pd.to_datetime(eco.service_date).max() - pd.to_datetime(eco.service_date).min()).days + 1
yrs = days / 365
n_dev = eco.device_id.nunique()
print(f"devices with economics: {n_dev}, span {days} d")

spend = eco.groupby("device_id").total_customer_cost_eur.sum() / yrs
coll = eco.groupby("device_id").collection_cost_eur.sum() / yrs
proc = eco.groupby("device_id").processing_cost_eur.sum() / yrs
cred = eco.groupby("device_id").material_credit_eur.sum() / yrs
print(f"\n== Customer spend per device/yr: median {spend.median():.0f} €, mean {spend.mean():.0f} €")
print(f"   collection (lift+km) mean {coll.mean():.0f} €, processing mean {proc.mean():.0f} €, credits mean {cred.mean():.0f} €")

# Over-servicing: completed lifts under 60 % fill
m = ev.merge(eco[["collection_id", "collection_cost_eur", "service_date"]], on="collection_id")
m = m[m.status == "COMPLETED"]
low = m[m.device_fill_pct_before < 60]
print(f"\n== Lifts under 60 % fill: {len(low)/len(m):.1%} of lifts; their lift cost per device/yr "
      f"{low.collection_cost_eur.sum()/n_dev/yrs:.0f} €")
# a lift at fill f could be avoided by waiting; avoidable share ~ 1 - f/85
avoid = (low.collection_cost_eur * (1 - low.device_fill_pct_before / 85)).sum() / n_dev / yrs
print(f"   avoidable lift cost (waiting to 85 %): {avoid:.0f} € per device/yr")

# Labelled value at stake by family
v = an.groupby("label_family").value_at_stake_eur.sum().sort_values(ascending=False) / n_dev / yrs
print("\n== Labelled value at stake per device/yr by family (€):")
print(v[v > 0].round(0).to_string())

# Operator actions (C2): positive values per case
pos = oav[oav.positive]
print(f"\n== Operator actions: cases {oav.case_id.nunique()}, positive best_set_value mean "
      f"{oav.groupby('case_id').best_set_value_eur.max().mean():.0f} € per contract")
print(pos.groupby("action").value_eur.agg(["count", "mean"]).round(0).to_string())

# Pricing risk for an operator bidding an all-in €/t price: kg per lift
k = m.merge(eco[["collection_id", "billing_mass_kg"]], on="collection_id")
k = k[k.billing_mass_kg > 0].merge(dev[["device_id", "material_stream", "container_volume_m3", "equipment_class"]], on="device_id")
k["date"] = pd.to_datetime(k.service_date)
k = k.sort_values("date")
site = k.groupby("device_id").agg(kg=("billing_mass_kg", "mean"), mat=("material_stream", "first"),
                                   vol=("container_volume_m3", "first"), cls=("equipment_class", "first"))
# Blind bid: peer median for same material + volume + class (leave-one-out-ish via median)
site["peer"] = site.groupby(["mat", "vol", "cls"]).kg.transform("median")
site["err_blind"] = (site.peer - site.kg) / site.kg
# Profile bid: first half of year predicts second half
half = k.date.min() + (k.date.max() - k.date.min()) / 2
a = k[k.date < half].groupby("device_id").billing_mass_kg.mean()
b = k[k.date >= half].groupby("device_id").billing_mass_kg.mean()
site["err_profile"] = (a - b) / b
s = site.dropna()
print(f"\n== kg-per-lift forecast error for a new bidder (n={len(s)} devices):")
for c in ["err_blind", "err_profile"]:
    e = s[c].abs()
    print(f"   {c}: median |err| {e.median():.1%}, p80 {e.quantile(.8):.1%}, share >20 % off {(e>.2).mean():.1%}")
# Translate into money: transport cost per tonne mis-estimated by err -> loss/overbid on the transport part
s = s.join(coll.rename("coll"))
for c in ["err_blind", "err_profile"]:
    risk = (s[c].abs() * s.coll).mean()
    print(f"   expected transport mis-pricing per device/yr ({c}): {risk:.0f} €")
