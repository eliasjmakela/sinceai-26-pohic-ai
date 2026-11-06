"""The only bridge to the starter kit's internals (PRODUCT.md §7.2).

Everything else in `fullload` imports kit functionality from here. Never edit the kit itself;
if a kit function does not fit, wrap it in this module.
"""
from __future__ import annotations

import functools
import importlib
import sys
from pathlib import Path
from types import ModuleType

import duckdb
import yaml

from europress_data import GENERATOR_VERSION as KIT_VERSION  # noqa: F401  (re-exported for provenance)
from europress_data.economics import price_event, summarize  # noqa: F401  (re-exported)
from europress_data.sdk import open_dataset as _open_dataset

from .config import kit_root


def open_dataset(root: Path, as_of: str | None = None) -> duckdb.DuckDBPyConnection:
    """DuckDB connection with one view per kit table (+ `telemetry_dedup`). `as_of` gives a leak-free view."""
    return _open_dataset(root, as_of=as_of)


@functools.cache
def kit_assumptions() -> dict:
    """The kit's simulation assumptions (configs/assumptions.yaml), e.g. materials.*.max_days_between."""
    return yaml.safe_load((kit_root() / "configs" / "assumptions.yaml").read_text(encoding="utf-8"))


def baseline(name: str) -> ModuleType:
    """Import a kit baseline script as a module, e.g. baseline("b1_economic_calculator").

    The baselines are scripts, not a package, and expect `src/` and `baselines/` on sys.path.
    """
    for p in (kit_root() / "src", kit_root() / "baselines"):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    return importlib.import_module(name)
