"""Assemble and write the demo bundle. Deterministic: same inputs -> byte-identical JSON."""
from __future__ import annotations

import json
from pathlib import Path

from . import business, customer, fleet, value, virtual_scale, forecast, market, pick_heroes, premature, scorecard, trips, validate
from .config import BUNDLE_PATH, data_root, profile_name
from .kit import KIT_VERSION, open_dataset

SCHEMA_VERSION = 1


def build_bundle(data: str | None = None) -> dict:
    root = data_root(data)
    con = open_dataset(root)
    try:
        market_section = market.market_facts(con)
        devices = market.account_devices(con, market_section["region"])
        policies = dict(con.execute("SELECT device_id, collection_policy FROM devices").fetchall())
        hero = pick_heroes.hero_customer(market_section["default"]["rows"], devices, policies)
        return {
            "schema_version": SCHEMA_VERSION,
            "provenance": {"kit_version": KIT_VERSION, "data": profile_name(root), "synthetic": True},
            "fleet": fleet.fleet_facts(con),
            "forecast": forecast.forecast_facts(con),
            "trips": trips.trips_facts(con),
            "premature": premature.premature_facts(con),
            "scorecard": scorecard.scorecard_facts(con, root),
            "validation": validate.validation_facts(root),
            "market": market_section,
            "heroes": {"customer_id": hero},
            "hero": customer.hero_view(con, market_section, devices, hero, root),
            "value_per_device": value.value_per_device(con, root, market_section["sigma_inc"], market_section["sigma_ent"]),
            "business": business.business_facts(con),
            "virtual_scale": virtual_scale.virtual_scale_facts(con),
            # Next sections, in build order (PRODUCT.md §6): reconcile (beat 5), weighing (beat 1).
        }
    finally:
        con.close()


def dumps(bundle: dict) -> str:
    return json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_bundle(bundle: dict, path: Path = BUNDLE_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(bundle), encoding="utf-8")
    return path
