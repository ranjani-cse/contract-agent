"""Test: c6 combines blockers + risk + drift into a priority list."""
from agent.agent import answer_c6_portfolio_audit


def test_c6_returns_priority_list():
    r = answer_c6_portfolio_audit()
    assert isinstance(r, dict)
    assert isinstance(r.get("priority_list"), list)
    assert isinstance(r.get("blockers_found"), int)
    assert isinstance(r.get("renewal_at_risk"), int)
    assert isinstance(r.get("drift_reports"), int)


def test_c6_priority_sorted():
    r = answer_c6_portfolio_audit()
    items = r.get("priority_list", [])
    if len(items) > 1:
        totals = [i.get("total_issues", 0) for i in items]
        assert totals == sorted(totals, reverse=True), \
            "priority list should be sorted by total issues, high first"
