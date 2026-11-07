"""Pricing, value per device, virtual scale and weighing (PRICING.md, PRODUCT.md §6)."""
from __future__ import annotations

from dataclasses import replace

import pytest

from fullload import pricing, value, virtual_scale, weighing
from fullload.config import data_root
from fullload.kit import open_dataset


@pytest.fixture(scope="module")
def con():
    return open_dataset(data_root("quickstart"))


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


def test_weighing_reads_part1_and_reproduces_the_worked_example():
    w = weighing.weighing_facts()
    ex = w["h7"]["example"]
    # WEIGHING_CONCEPT.md §19.2 worked example: 27 bar tare, 57 bar loaded, ~85 kg of waste per bar, W back = 2.5 t
    assert (ex["tare_bar"], ex["loaded_bar"], ex["kg_waste_per_bar"], ex["waste_from_reading_t"]) == (27, 57, 85, 2.5)
    strip = {c["id"]: c["factory_fit_eur"] for c in w["installed_cost"]["strip"]}
    assert strip["H7"][0] < strip["H7"][1] and set(strip) == set(weighing.COST_STRIP)
    assert w["h7"]["figures"]["sigma_one_point_pct"]["tag"] == "estimated"


def test_pricing_reproduces_team_model_and_break_evens(con):
    pp = pricing.load_params()
    team = replace(pp, h7_capex_eur=825, h7_upkeep_eur_per_unit_year=50)
    # LIITE §6.3: NPV 2.49 M EUR, deepest -2.94 M EUR, cumulative +6.41 M EUR, payback year 7 (EUR 30, H7 EUR 825)
    s = pricing.summarise(pricing.cash_flows(team, 30), pp.discount_rate)
    assert (round(s["npv_eur"], -4), round(s["deepest_eur"], -4), s["payback_year"]) == (2_490_000, -2_940_000, 7)
    fee = pricing.break_even_fee(pp)
    assert pricing.npv(pp, fee) >= 0 > pricing.npv(pp, fee - 1)
    cap = pricing.max_h7_capex(pp, 30)
    assert pricing.npv(replace(pp, h7_capex_eur=cap), 30) >= 0 > pricing.npv(replace(pp, h7_capex_eur=cap + 10), 30)
    assert pricing.customer_spend_median_eur(con) > 0
