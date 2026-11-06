"""Demo-serving tests (PRODUCT.md §8). Run on the quickstart pack for speed."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from fullload.export import build_bundle, dumps
from fullload.figures import TAGS

PKG = Path(__file__).resolve().parents[1] / "fullload"
LABEL_READERS = {"validate.py", "pick_heroes.py"}   # the only modules allowed to read labels_dev


@pytest.fixture(scope="module")
def bundle() -> dict:
    return build_bundle("quickstart")


def _figures(node):
    if isinstance(node, dict):
        if {"value", "tag", "sources", "formula"} <= node.keys():
            yield node
        else:
            for v in node.values():
                yield from _figures(v)
    elif isinstance(node, list):
        for v in node:
            yield from _figures(v)


def test_deterministic(bundle):
    assert dumps(bundle) == dumps(build_bundle("quickstart"))


def test_every_figure_has_tag_and_sources(bundle):
    figs = list(_figures(bundle))
    assert figs, "bundle contains no figures"
    for f in figs:
        assert f["tag"] in TAGS and f["sources"] and f["formula"]


def test_fleet_shares_are_sane(bundle):
    fl = bundle["fleet"]
    assert 0 < fl["trip_share_pct"]["value"] < 100
    assert fl["trip_charges_eur"]["value"] + fl["tonne_charges_eur"]["value"] <= fl["gross_charges_eur"]["value"]


def test_labels_only_read_by_allowed_modules():
    offenders = [p.name for p in PKG.glob("*.py")
                 if p.name not in LABEL_READERS and re.search(r"labels_(dev|test)", p.read_text())]
    assert not offenders, f"only {LABEL_READERS} may read labels: {offenders}"


def test_kit_baselines_importable():
    from fullload.kit import baseline
    assert hasattr(baseline("b1_economic_calculator"), "compute")


def test_forecast_shows_history_advantage(bundle):
    f = bundle["forecast"]
    assert f["method"]["devices"] > 0
    assert f["own_history_error_median_pct"]["value"] < f["peer_error_median_pct"]["value"]


def test_trips_model_conserves_tonnage_and_respects_interval():
    from fullload.config import data_root
    from fullload.kit import open_dataset
    from fullload.trips import TARGET_SHARE, device_trips
    df = device_trips(open_dataset(data_root("quickstart")))
    ok = df[df.weight_trips.notna()]
    assert len(ok) > 0
    # enough capacity for the same waste: trips x (target share x payload) >= annual kg
    assert (ok.weight_trips * TARGET_SHARE * ok.full_payload_kg >= ok.annual_kg - 1e-6).all()
    assert (ok.weight_trips >= ok.interval_bound).all()
