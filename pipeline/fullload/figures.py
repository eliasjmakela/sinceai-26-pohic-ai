"""`Figure`: every number the UI shows (PRODUCT.md §7.3).

The UI never displays a bare number; it displays a Figure with its evidence tag, formula and sources,
so every value on screen can open a receipt.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

Tag = Literal["observed", "estimated", "simulated", "hypothetical"]
TAGS: tuple[str, ...] = ("observed", "estimated", "simulated", "hypothetical")


@dataclass(frozen=True)
class Figure:
    value: float | int | None          # None = cannot be computed (never impute)
    unit: str                          # "EUR", "t", "kg", "%", "count", "EUR/t" ...
    tag: Tag
    formula: str                       # human-readable, e.g. "sum(amount_eur) where line_type in TRIP_LINES"
    sources: tuple[str, ...]           # "table.column" references
    sigma: float | None = None         # 1-sigma uncertainty in `unit`, if known
    row_ids: tuple[str, ...] = ()      # example row ids for the receipt (keep short)
    assumptions: tuple[str, ...] = field(default=())

    def __post_init__(self) -> None:
        if self.tag not in TAGS:
            raise ValueError(f"tag must be one of {TAGS}, got {self.tag!r}")
        if not self.sources:
            raise ValueError("a Figure needs at least one source")
        if not self.formula:
            raise ValueError("a Figure needs a formula")

    def to_dict(self) -> dict:
        d = asdict(self)
        d["sources"], d["row_ids"], d["assumptions"] = list(self.sources), list(self.row_ids), list(self.assumptions)
        return d


def eur_from_cents(cents: int) -> float:
    """Money is integer cents in the pipeline; convert only when building a Figure."""
    return round(cents / 100, 2)
