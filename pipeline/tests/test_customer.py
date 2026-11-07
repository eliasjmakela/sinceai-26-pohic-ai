"""AI-summarized report guard (PRODUCT.md §7.6): numbers in the report must come from the fact sheet."""
from fullload.customer import report_numbers_ok

FACTS = {"lifts": 163, "cost_today_eur": 28218, "cost_per_t_today_eur": 137.6}


def test_report_numbers_checked():
    assert report_numbers_ok("163 visits cost €28,218 (€137.6 per tonne) over 12 months.", FACTS) == []
    assert report_numbers_ok("163 visits cost €29,000.", FACTS) == ["29,000"]
    assert report_numbers_ok("Customer ORG-0036 with operator OP-A.", FACTS) == []
