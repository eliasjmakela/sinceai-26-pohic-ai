"""Assemble and write the demo bundle. Deterministic: same inputs -> byte-identical JSON."""
from __future__ import annotations

import json
from pathlib import Path

from . import fleet, forecast, trips
from .config import BUNDLE_PATH, data_root, profile_name
from .kit import KIT_VERSION, open_dataset

SCHEMA_VERSION = 1


def build_bundle(data: str | None = None) -> dict:
    root = data_root(data)
    con = open_dataset(root)
    try:
        return {
            "schema_version": SCHEMA_VERSION,
            "provenance": {"kit_version": KIT_VERSION, "data": profile_name(root), "synthetic": True},
            "fleet": fleet.fleet_facts(con),
            "forecast": forecast.forecast_facts(con),
            "trips": trips.trips_facts(con),
            # Next sections, in build order (PRODUCT.md §6): market, heroes, reconcile, business.
        }
    finally:
        con.close()


def dumps(bundle: dict) -> str:
    return json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_bundle(bundle: dict, path: Path = BUNDLE_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(bundle), encoding="utf-8")
    return path
