"""Shared helpers for the first-principles calculations in part1/calc/.

Every input is a named parameter with a source tag: a reference id [n] from WEIGHING_CONCEPT.md, "kit" (starter
kit configs/assumptions.yaml), "Tommi" (7 Nov talk) or "team estimate". Scripts print their working and write a
markdown table to part1/generated/calc_<name>.md that the concept and the claims ledger quote.
"""
from __future__ import annotations

from pathlib import Path

PART1 = Path(__file__).resolve().parents[1]
GEN = PART1 / "generated"
G = 9.81  # m/s2


def md_table(header: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def write(name: str, text: str) -> Path:
    GEN.mkdir(parents=True, exist_ok=True)
    p = GEN / f"calc_{name}.md"
    p.write_text(text)
    return p


def kn_to_t(f_n: float) -> float:
    """Force in newtons -> equivalent mass in tonnes (what a load cell 'sees')."""
    return f_n / G / 1000
