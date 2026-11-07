"""Business model, value per device and virtual scale (PRODUCT.md §6, beat 6)."""
from __future__ import annotations

from dataclasses import replace

import pytest

from fullload import business, value, virtual_scale
from fullload.config import data_root
from fullload.kit import open_dataset


@pytest.fixture(scope="module")
def con():
    return open_dataset(data_root("quickstart"))


def test_business_reproduces_team_headline():
    p = business.load_params(tonnes_per_device_year=92.6)
    s = business.simulate(p)
    # business team's stated figures (7 Nov): EUR 1.5 M investment, 1.2 M revenue, 0.74 M opex, ~0.47 M extra sales
    assert s["investment"] == pytest.approx(1_500_000)
    assert s["service_revenue"] == pytest.approx(1_200_000)
    assert s["opex"] == pytest.approx(740_000)
    assert s["extra_sales_margin"] == pytest.approx(468_750)
    assert s["customer_pays"] == 0


def test_business_payback_grows_with_hardware_cost():
    p = business.load_params(tonnes_per_device_year=92.6)
    cheap, dear = business.simulate(p), business.simulate(replace(p, h1_cost_eur=2363))
    assert dear["payback_years"] > cheap["payback_years"]
    assert business.simulate(replace(p, fee_eur_per_device_month=0, sales_growth=0))["payback_years"] is None


def test_value_rows_are_figures_or_explained(con):
    from fullload.market import forecast_sigmas
    s_inc, s_ent = forecast_sigmas(con)
    v = value.value_per_device(con, data_root("quickstart"), s_inc, s_ent)
    for r in v["rows"]:
        assert r["ours"] is not None or r.get("note")
        if r["ours_range"]:
            assert r["ours_range"][0] <= r["ours_range"][1]


def test_virtual_scale_excludes_biowaste_and_runs(con):
    df = virtual_scale.lifts(con)
    assert "biowaste" not in set(df.material_stream)
    assert (df.ref_kg > 0).all()
