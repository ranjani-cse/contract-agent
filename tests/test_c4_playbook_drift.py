"""Test: c4 returns portfolio playbook drift."""
from agent.agent import answer_c4_playbook_drift


def test_c4_returns_drift_shape():
    r = answer_c4_playbook_drift()
    assert isinstance(r, dict)
    assert isinstance(r.get("contracts_scanned"), int)
    assert isinstance(r.get("drift_reports"), list)


def test_c4_drift_sorted_by_missing_clauses():
    r = answer_c4_playbook_drift()
    reports = r.get("drift_reports", [])
    if len(reports) > 1:
        counts = [x.get("missing_clauses", 0) for x in reports]
        assert counts == sorted(counts, reverse=True), \
            "drift reports should be sorted high to low"
