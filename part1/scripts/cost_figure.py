"""Installed cost per device (H6) vs the ~EUR 2k reference and vs accuracy after calibration.

    python cost_figure.py   -> figures/installed_cost.svg   (reads installed_cost.json and sigma_tiers.json)
"""
from __future__ import annotations

import json

from common import INK, INK2, PART1, TIER_COLOR, save_svg, style

import matplotlib.pyplot as plt


def main():
    cost = json.loads((PART1 / "installed_cost.json").read_text())
    tiers = {t["id"]: t for t in json.loads((PART1 / "sigma_tiers.json").read_text())["tiers"]}
    order = ["T0", "T1", "H1", "H7", "H5", "T2", "PS"]
    style()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(10, 3.9), gridspec_kw={"width_ratios": [1.6, 1]})
    for i, cid in enumerate(order[::-1]):
        c = cost["candidates"][cid]
        r, f = c["retrofit_eur"], c["factory_fit_eur"]
        col = TIER_COLOR[cid]
        ax.plot([f["low"], f["high"]], [i + 0.15] * 2, color=col, linewidth=7, solid_capstyle="butt")
        ax.plot([r["low"], r["high"]], [i - 0.15] * 2, color=col, linewidth=7, alpha=0.4, solid_capstyle="butt")
        ax.text(max(r["high"], f["high"]) * 1.08, i, f"factory €{f['low']:,}–{f['high']:,}\nretrofit €{r['low']:,}–{r['high']:,}",
                va="center", fontsize=7.5, color=INK2)
    ax.axvline(cost["reference_option_eur"], color=INK, linestyle=(0, (4, 3)), linewidth=1.2)
    ax.text(cost["reference_option_eur"] * 1.05, len(order) - 0.45, "~€2,000 option\n(Tommi, 7 Nov)", fontsize=8, color=INK)
    ax.set_xscale("log")
    ax.set_xlim(8, 2.4e5)
    ax.set_xticks([10, 100, 1000, 10000], ["€10", "€100", "€1k", "€10k"])
    ax.set_yticks(range(len(order)), [f"{cid}" for cid in order[::-1]])
    ax.set_xlabel("full installed cost per device, 6-year lease (dark = factory-fit, light = retrofit)")
    ax.set_title("H6 installed cost (estimate, ex VAT)", loc="left")
    ax.grid(axis="y", visible=False)
    for cid in order:
        t = tiers[cid]
        f = cost["candidates"][cid]["factory_fit_eur"]
        x = (f["low"] * f["high"]) ** 0.5 if f["low"] > 0 else max(f["high"], 10) / 2
        s = t["sigma_rel_pct"]
        bx.errorbar([max(x, 10)], [s["mid"]], yerr=[[s["mid"] - s["low"]], [s["high"] - s["mid"]]], fmt="o",
                    color=TIER_COLOR[cid], markersize=8, capsize=3)
        bx.annotate(cid, (max(x, 10), s["mid"]), textcoords="offset points", xytext=(7, 3), fontsize=9, color=INK)
    bx.set_xscale("log")
    bx.set_yscale("log")
    bx.set_xticks([10, 100, 1000, 10000], ["€10", "€100", "€1k", "€10k"])
    bx.set_yticks([0.5, 1, 2, 5, 10, 20], ["0.5", "1", "2", "5", "10", "20"])
    bx.set_xlabel("factory-fit installed cost (geometric mid)")
    bx.set_ylabel("1σ error after calibration, %")
    bx.set_title("cost vs accuracy (estimate)", loc="left")
    fig.tight_layout()
    save_svg(fig, "installed_cost.svg")


if __name__ == "__main__":
    main()
