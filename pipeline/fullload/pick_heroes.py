"""Deterministic choice of the demo's hero cases (PRODUCT.md §6 item 5). Written to the bundle as `heroes`.

Hero customer (beats 2–4): an account in the market region that
  * has at least MIN_DEVICES devices in the region and at least one FIXED_SCHEDULE device (where waste lives), and
  * has the largest simulated per-kg saving under the default market assumptions.
No labels are needed for this choice (labels_dev may be read here per PRODUCT.md, but are not).
"""
from __future__ import annotations

import pandas as pd

MIN_DEVICES = 3


def hero_customer(market_rows: list[dict], devices: pd.DataFrame, policies: dict[str, str]) -> str:
    """market_rows: market default rows; devices: market.account_devices; policies: device_id -> policy."""
    dev = devices.assign(policy=devices.device_id.map(policies))
    ok = {c for c, g in dev.groupby("customer_id")
          if len(g) >= MIN_DEVICES and (g.policy == "FIXED_SCHEDULE").any()}
    cands = [r for r in market_rows if r["customer_id"] in ok and not r["keeps_today"]]
    if not cands:
        cands = list(market_rows)
    best = min(cands, key=lambda r: (r["price_after"] / r["price_before"], r["customer_id"]))
    return best["customer_id"]
