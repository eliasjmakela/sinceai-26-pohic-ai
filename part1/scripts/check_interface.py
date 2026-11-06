"""QG6 check: sigma_tiers.json has exactly the shape of briefs/PART1_WEIGHING.md section 4, chosen_tier is T1,
and the comparison table in WEIGHING_CONCEPT.md is byte-identical to the generated table (same numbers)."""
from __future__ import annotations

import json
import sys

from common import GEN, PART1

TOP = {"schema_version": int, "chosen_tier": str, "tiers": list}
TIER = {"id": str, "name": str, "principle": str, "sigma_rel_pct": dict, "sigma_abs_kg": dict,
        "bom_eur_per_device": dict, "install_hours": dict, "suits": list, "weak_for": list,
        "evidence_tag": str, "sources": list}
LMH = {"low", "mid", "high"}
LH = {"low", "high"}


def main() -> int:
    errs = []
    doc = json.loads((PART1 / "sigma_tiers.json").read_text())
    if set(doc) != set(TOP):
        errs.append(f"top-level keys {sorted(doc)}")
    for k, typ in TOP.items():
        if not isinstance(doc.get(k), typ):
            errs.append(f"{k} not {typ.__name__}")
    if doc.get("schema_version") != 1 or doc.get("chosen_tier") != "T1":
        errs.append("schema_version must be 1 and chosen_tier T1")
    ids = [t.get("id") for t in doc["tiers"]]
    if ids != ["T0", "T1", "T2"]:
        errs.append(f"tier ids {ids}")
    for t in doc["tiers"]:
        if set(t) != set(TIER):
            errs.append(f"{t.get('id')}: keys {sorted(set(t) ^ set(TIER))}")
        for k, typ in TIER.items():
            if not isinstance(t.get(k), typ):
                errs.append(f"{t.get('id')}.{k} not {typ.__name__}")
        for k in ("sigma_rel_pct", "sigma_abs_kg"):
            if set(t[k]) != LMH or not all(isinstance(v, float) for v in t[k].values()):
                errs.append(f"{t['id']}.{k} must be low/mid/high floats")
            if not t[k]["low"] <= t[k]["mid"] <= t[k]["high"]:
                errs.append(f"{t['id']}.{k} not ordered")
        for k in ("bom_eur_per_device", "install_hours"):
            if set(t[k]) != LH or not all(isinstance(v, int) for v in t[k].values()) or t[k]["low"] > t[k]["high"]:
                errs.append(f"{t['id']}.{k} must be ordered low/high ints")
        if t["evidence_tag"] not in {"estimate", "simulation_target", "literature"}:
            errs.append(f"{t['id']}.evidence_tag {t['evidence_tag']}")
        if not set(t["suits"]) <= {"COMBI", "DUO"}:
            errs.append(f"{t['id']}.suits {t['suits']}")
        if not all(s.startswith("[") and s.endswith("]") for s in t["sources"]):
            errs.append(f"{t['id']}.sources {t['sources']}")
    table = (GEN / "tiers_table.md").read_text()
    d1 = (PART1 / "WEIGHING_CONCEPT.md").read_text()
    if table.strip() not in d1:
        errs.append("WEIGHING_CONCEPT.md does not contain generated/tiers_table.md verbatim")
    print("sigma_tiers.json + D1 table:", "OK" if not errs else "FAIL")
    for e in errs:
        print("  -", e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
