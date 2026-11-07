"""Market simulation invariants (PRODUCT.md §3, decisions a–c of 7 Nov)."""
from __future__ import annotations

from dataclasses import replace

import pytest

from fullload import market
from fullload.config import data_root
from fullload.kit import open_dataset


@pytest.fixture(scope="module")
def setup():
    con = open_dataset(data_root("quickstart"))
    region = market.pick_region(con)
    acc = market.accounts(con, region).to_dict("records")
    ops = sorted({a["incumbent"] for a in acc})
    s_inc, s_ent = market.forecast_sigmas(con)
    return acc, ops, s_inc, s_ent, market.load_params()


def test_before_price_is_observed_invoices(setup):
    acc, ops, s_inc, s_ent, p = setup
    res = market.simulate(acc, ops, s_inc, s_ent, p)
    for a, r in zip(acc, res["rows"]):
        assert r["price_before"] == a["trip_cents"] + a["tonne_cents"]


def test_price_bounds_and_tonnage(setup):
    acc, ops, s_inc, s_ent, p = setup
    res = market.simulate(acc, ops, s_inc, s_ent, replace(p, new_entrants=2, entrant_cost_advantage=0.1))
    assert abs(sum(r["tonnes"] for r in res["rows"]) - sum(a["kg"] for a in acc) / 1000) < 1e-9   # same waste
    for r in res["rows"]:
        assert r["price_after"] <= r["price_before"] + 1e-6        # never above today's price
        assert r["lifts_after"] <= r["lifts_before"] or r["lifts_after"] >= 1


def test_no_challengers_means_incumbent_keeps_all(setup):
    acc, _, s_inc, s_ent, p = setup
    solo = sorted({a["incumbent"] for a in acc})[:1]
    one = [a for a in acc if a["incumbent"] == solo[0]]
    res = market.simulate(one, solo, s_inc, s_ent, replace(p, new_entrants=0))
    assert res["summary"]["accounts_switched"] == 0


def test_route_fit_is_deterministic_and_bounded():
    v = market.route_fit("OP-A", "ORG-0001")
    assert v == market.route_fit("OP-A", "ORG-0001") and -1 <= v < 1
    assert market.fnv1a("a") == 0xE40C292C   # reference FNV-1a 32-bit value, also checked in the TS mirror
