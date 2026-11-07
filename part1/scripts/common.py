"""Shared helpers for the Part 1 scripts: paths, chart style, deterministic SVG output.

Every script reads data only from a `data/<profile>/public` root passed on the command line.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PART1 = Path(__file__).resolve().parents[1]
FIG = PART1 / "figures"
GEN = PART1 / "generated"

# Light-mode reference palette (dataviz skill, references/palette.md); text never uses series colours.
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e4e3df"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"   # categorical slots 1-3, fixed order
TIER_COLOR = {"T0": S2, "T1": "#9a6fc0", "T2": S3, "H1": S1, "H5": "#c9a227", "PS": "#7a7a75", "H7": "#c2185b"}  # v2: H1 takes slot 1


def check_public_root(p: str) -> Path:
    root = Path(p).resolve()
    if "private_evaluation" in root.parts or root.name != "public":
        sys.exit(f"refusing to read {root}: pass a data/<profile>/public directory")
    return root


def style():
    plt.rcParams.update({
        "svg.hashsalt": "fullload-part1",      # stable element ids -> byte-identical SVGs
        "svg.fonttype": "none",                 # keep text as text
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.edgecolor": INK2,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "axes.titlesize": 11,
        "axes.facecolor": SURFACE,
        "figure.facecolor": SURFACE,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "lines.linewidth": 2,
    })


def save_svg(fig, name: str):
    FIG.mkdir(parents=True, exist_ok=True)
    out = FIG / name
    fig.savefig(out, format="svg", metadata={"Date": None, "Creator": "OpenWeight part1 scripts"}, bbox_inches="tight")
    plt.close(fig)
    return out
