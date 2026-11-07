"""Beat 2: how we get the weight (PRODUCT.md §4, part1/WEIGHING_CONCEPT.md §19).

Reads the Part 1 outputs instead of copying their numbers: installed cost per concept
(`part1/installed_cost.json`) and the H7 hydraulic self-lift statics and error budget
(`part1/generated/h7_hydraulic.json`, from `part1/calc/h7_hydraulic.py`). All of it is a team estimate, untested.

The worked example recomputes the statics of §19.2 so the screen can show the working:
  door-end reaction  R = M x door-end share + W x (x_w / L)          (tonnes, moments about the front pivot)
  cylinder pressure  p = R x g / piston area
  waste              W = (R - R0) x L / x_w
"""
from __future__ import annotations

import json
import math
from functools import cache

from .config import REPO_ROOT
from .figures import Figure

PART1 = REPO_ROOT / "part1"
COST_PATH = PART1 / "installed_cost.json"
H7_PATH = PART1 / "generated" / "h7_hydraulic.json"
G = 9.81

# Mid values of WEIGHING_CONCEPT.md §19.2 (team estimates).
EXAMPLE = {"machine_t": 3.75, "door_end_share": 0.375, "waste_t": 2.5, "x_w_over_l": 0.6}

# Concepts shown on the cost strip, in display order.
COST_STRIP = ("H7", "H1", "PS")


@cache
def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def installed_cost() -> dict:
    """Factory-fit installed cost range per concept (EUR, incl. 6-year upkeep), plus the ~EUR 2k reference."""
    d = _json(COST_PATH)
    return {"reference_eur": d["reference_option_eur"],
            "concepts": {k: {"name": v["name"], "factory_fit_eur": [v["factory_fit_eur"]["low"], v["factory_fit_eur"]["high"]],
                             "retrofit_eur": [v["retrofit_eur"]["low"], v["retrofit_eur"]["high"]]}
                         for k, v in d["candidates"].items()}}


def worked_example(bore_mm: float) -> dict:
    area_m2 = math.pi * (bore_mm / 1000) ** 2 / 4
    bar = lambda tonnes: tonnes * 1000 * G / area_m2 / 1e5   # noqa: E731
    e = EXAMPLE
    r0 = e["machine_t"] * e["door_end_share"]
    r = r0 + e["waste_t"] * e["x_w_over_l"]
    kg_per_bar = 1e5 * area_m2 / G / e["x_w_over_l"]
    return {**e, "bore_mm": bore_mm, "tare_bar": round(bar(r0)), "loaded_bar": round(bar(r)),
            "waste_from_reading_t": round((r - r0) / e["x_w_over_l"], 2), "kg_waste_per_bar": round(kg_per_bar)}


def weighing_facts() -> dict:
    h7 = _json(H7_PATH)
    cost = installed_cost()
    src = ("part1/generated/h7_hydraulic.json", "part1/calc/h7_hydraulic.py", "part1/WEIGHING_CONCEPT.md §19")
    untested = ("Team estimate, untested: no prototype, no supplier quote",)

    def fig(value, unit, formula, sources=src, assumptions=untested):
        return Figure(value, unit, "estimated", formula, sources, assumptions=assumptions).to_dict()

    b, c = h7["sigma_rel_pct"]["B"]["2.5t"], h7["sigma_rel_pct"]["C"]["2.5t"]
    lo, hi = cost["concepts"]["H7"]["factory_fit_eur"]
    return {
        "h7": {
            "design_bore_mm": h7["design_bore_mm"],
            "pressure_bar": [h7["pressure_bar_design_bore"]["empty_min"], h7["pressure_bar_design_bore"]["full_max"]],
            "system_pressure_bar": 200,   # named by Europress at kickoff (WEIGHING_CONCEPT.md [36])
            "stroke_margin_mm": h7["stroke_margin_mm"],
            "example": worked_example(h7["design_bore_mm"]),
            "sigma_one_point_pct": [b["low"], b["mid"], b["high"]],
            "sigma_one_point_no_tickets_pct": h7["sigma_rel_pct"]["A"]["2.5t"]["mid"],
            "sigma_two_end_pct": [c["low"], c["mid"], c["high"]],
            "figures": {
                "sigma_one_point_pct": fig(b["mid"], "%", "error budget case B (one-point lift + shared tickets), 2.5 t, "
                                           "RSS of 7 sources, mid parameters",
                                           assumptions=(*untested, f"low / high parameters: {b['low']} / {b['high']} %")),
                "installed_eur_low": fig(lo, "EUR", "sum of factory-fit cost lines, low (incl. 6-year upkeep)",
                                         sources=("part1/installed_cost.json", "part1/calc/installed_cost.py")),
                "installed_eur_high": fig(hi, "EUR", "sum of factory-fit cost lines, high (incl. 6-year upkeep)",
                                          sources=("part1/installed_cost.json", "part1/calc/installed_cost.py")),
            },
        },
        "installed_cost": {"reference_eur": cost["reference_eur"],
                           "strip": [{"id": k, **cost["concepts"][k]} for k in COST_STRIP]},
    }
