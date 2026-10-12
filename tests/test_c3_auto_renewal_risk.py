"""Test: c3 flags at-risk auto-renewals."""
from agent.agent import answer_c3_auto_renewal_risk


def test_c3_returns_risk_shape():
    r = answer_c3_auto_renewal_risk()
    assert isinstance(r, dict)
    assert isinstance(r.get("expiring_30d"), int)
    assert isinstance(r.get("at_risk"), list)


def test_c3_at_risk_entries_have_risks():
    r = answer_c3_auto_renewal_risk()
    for entry in r.get("at_risk", [])[:3]:
        assert "contract_id" in entry
        assert isinstance(entry.get("risks"), list)
        assert len(entry["risks"]) > 0
