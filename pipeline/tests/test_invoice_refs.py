"""Mistyped job references on invoices (kit SCHEMA.md: ~1.2 %, fall back to contract + service_date)."""
from fullload.config import data_root
from fullload.kit import open_dataset
from fullload.scorecard import _b1, invoice_lines_vs_contract


def test_mistyped_refs_matched_by_contract_and_date():
    root = data_root("quickstart")
    il = invoice_lines_vs_contract(open_dataset(root), root)
    econ, lines = _b1(root)
    jobs = econ.set_index("operator_job_ref")
    fixed = il[il.ref_fixed]
    assert len(fixed) > 0
    assert fixed.operator_job_ref.isin(set(lines.operator_job_ref)).all()   # every remapped ref is a real job
    for r in fixed.drop_duplicates("operator_job_ref").itertuples():          # ... on the same contract and day
        j = jobs.loc[r.operator_job_ref]
        assert j.contract_id == r.contract_id and str(j.service_date)[:10] == r.service_date
    # a remapped line is compared with its job's contract terms instead of counting in full as a difference
    assert (fixed.exp_cents != 0).all()
